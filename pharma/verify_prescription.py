from flask import request, render_template, url_for
from flask_socketio import join_room, leave_room
from datetime import timedelta, datetime
from model.issuer import Issuer
from model.verifier import Verifier
from model.credential import Credential
from model.credential_request import Credential_Request
from model.prescription import Prescription
from model.order import Order
from model.registry import Registry
import json
import uuid
import os
import contract_listener
import collections.abc

def init_app(app, red, socketio, couch) : 
        # Setup SSI model
    if(app.config['DID_METHOD']=='did:ethr'):
        issuer = Issuer(
            'ethr',
            f'did:ethr:{app.config["PHARMACY_PUBLIC_KEY"]}',
            json.dumps(json.load(open("ethkey.pem", "r")))
        )    
    elif((app.config['DID_METHOD']=='did:key')):
        issuer = Issuer(
        'key',
        app.config['DID_KEY'],
        json.dumps(json.load(open("key.pem", "r")))
    )  
    else:
        raise ValueError('did:method is not supported')

    registry = Registry(
        app.config['RPC_URL'],
        app.config['REGISTRY_ADDRESS'],
        app.config['DOCTOR_IDENTITY'],
        app.config['PHARMACY_IDENTITY']
    )
    verifier = Verifier(registry)

    db = couch['pharmacy']

    app.add_url_rule('/authorize',  view_func=authorize, methods = ['POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/verify/<stream_id>/<number_of_prescriptions>',  
                     view_func=verify, 
                     methods = ['GET','POST'], 
                     defaults={"red" : red, "socketio" : socketio, "verifier" : verifier}
    )
    app.add_url_rule('/callback/<stream_id>',  view_func=callback, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/success/<tx>',  view_func=success, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/order/<stream_id>',
                     view_func=create_order, 
                     methods = ['POST'], 
                     defaults={"red" : red, "socketio" : socketio, "pharmacy" : app.config['PHARMACY_PUBLIC_KEY']})
    app.add_url_rule('/order/sign/<order_id>',  view_func=receive_sign, methods = ['POST'], defaults={"red" : red})
    app.add_url_rule('/order/qr/<code>',  view_func=create_qr_order, methods = ['GET'])
    app.add_url_rule('/order/pay/<code>',
                     view_func=pay_order, 
                     methods = ['GET','POST'], 
                     defaults={"red" : red, "rpc_url" : app.config['RPC_URL']})
    app.add_url_rule('/order/wait/<code>',  
                     view_func=wait_order, 
                     methods = ['GET'], 
                     defaults={"red" : red, "db":db, "issuer":issuer}
    )
    app.add_url_rule('/api/credentials',  
                     view_func=get_credentials, 
                     methods = ['GET', 'POST'], 
                     defaults={"red" : red, "db": db, "issuer" : issuer})
    app.add_url_rule('/api/receipts/<status>',  
                     view_func=get_receipts, 
                     methods = ['GET'], 
                     defaults={"db": db})
    app.add_url_rule('/api/credentials/pending',  
                     view_func=update_credentials_status, 
                     methods = ['POST'], 
                     defaults={"db": db})
    app.add_url_rule('/insurance',  view_func=insurance, methods = ['GET'])

    return

def authorize(red, socketio):

    #Generate stream id
    stream_id = str(uuid.uuid4().hex)

    @socketio.on('subscribe')
    def subscribe(data):
        # Add client to private channel to get further updates
        join_room(data['socket_id'])
        # Save socket_id on server session to make /authorize able to link socket_id and stream_id
        socket_id = data['socket_id']
        print(f'socket_id : {socket_id}, stream_id : {stream_id}')
        red.set(stream_id, json.dumps({'stream_id' : stream_id, 'socket_id' : socket_id, 'verified' : False}))

    #Generate QR Code
    url = url_for('verify', stream_id=stream_id, number_of_prescriptions=request.form['pnumber'], _external = True)
    return render_template('qrcode.html', url=url)

async def verify(stream_id, number_of_prescriptions, red, socketio, verifier):

    if request.method == 'GET':
        request_schema = json.load(open('credentials/CredentialRequest.json', 'r'))
        request_credential = Credential_Request(request_schema, 'MedicalPrescriptionCredential', int(number_of_prescriptions))
        return request_credential.stringify()
    
    else: #POST
        form = request.form
        presentation = form.get('presentation')

        socket_id = json.loads(red.get(stream_id).decode())['socket_id']
        
        try:
            result = await verifier.verify_presentation(presentation, 'MedicalPrescriptionCredential')
            if(result == False):
                socketio.emit('error', {'error' : 'Presentation is not valid'}, to=socket_id)
                return 'Presentation is not valid', 500
            
        except Exception as e:
            print(e)
            socketio.emit('error', {'error' : 'Credential verification failed.'}, to=socket_id)
            return 'Credential verification failed.', 400
            
        if(verifier.are_credentials_unique(presentation) == False):
            socketio.emit('error', {'error' : 'There are duplicate credentials in the presentation'}, to=socket_id)
            return 'There are duplicate credentials in the presentation', 500

        # Redirect client via server push
        socketio.emit('stream_id', {'stream_id' : stream_id}, to=socket_id)

        # Save the tokens in the session
        try:
            red.set(stream_id, json.dumps({
                'stream_id' : stream_id, 
                'socket_id' : socket_id, 
                'vp' : json.loads(presentation)
            }))
        except Exception as e:
            print(e)
            # TODO : signal to socket error while writing to redis
            return 200
        
        # Send ok to wallet
        return 'Credential verified successfully!', 200
        
def callback(stream_id, red):
    json_prescriptions = []
    prescriptions = []
    data = json.loads(red.get(stream_id).decode())['vp']['verifiableCredential']
    # if we have multiple vcs, just save the array
    if isinstance(data, collections.abc.Sequence):
        json_prescriptions = data
    # if vc is single, create an array
    else:
        json_prescriptions.append(data)
    
    for p in json_prescriptions:
        drug = p['credentialSubject']['drug']
        max_quantity = int(p['credentialSubject']['quantity'])
        id = p['credentialSubject']['id']
        price = 1
        prescriptions.append( Prescription(id, max_quantity, price, drug).__dict__)

    red.set(f'pr:{stream_id}', json.dumps({'prescriptions' : prescriptions}))
    return render_template('prescription.html', prescriptions=prescriptions, stream_id=stream_id)

# Handle request for creating a new order from pharmacy
def create_order(stream_id, red, socketio, pharmacy):

    prescriptions = json.loads(red.get(f'pr:{stream_id}').decode())['prescriptions']
    for p in prescriptions:
            p['quantity'] = int(request.form.get(p['prId']))
    order = Order([], pharmacy)
    order.load_prescriptions_from_json(prescriptions)
    red.set(order.orderId, json.dumps({'order' : order.serialize(), 'stream_id' : stream_id, 'signed_order' : 'null'}))
    return order.serialize()

# Receive order signed by pharmacy, store it on Redis and redirect to QRCode to make user able to pay with SC
def receive_sign(order_id, red):
    code = str(uuid.uuid4())
    rs = json.loads(red.get(order_id).decode())
    stream_id = rs['stream_id']
    order = rs['order']
    signed_order = request.get_json()['signedOrder']

    red.set(code, json.dumps({'order' : order, 'stream_id' : stream_id, 'signed_order' : signed_order}))
    return code, 200

def create_qr_order(code):
    url = url_for('pay_order', code=code, _external = True)
    return render_template('qrcode-sc.html', url=url, code=code)

async def wait_order(code, red, db, issuer):
    rs = json.loads(red.get(code).decode())
    order_id = rs['order']['orderId']
    stream_id = rs['stream_id']

    # run blockchain listener
    tx = contract_listener.main(order_id)
    if not tx:
        return 'Timeout while listening blockchain', 500

    # Get data from Redis (prescription_id, quantity, socket_id)
    vp = json.loads(red.get(stream_id).decode())['vp']

    # Issue new credential (Prescription + Proof of payment)
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)
    receipt.set_value("invoice", {
            "description": vp,
            "confirmationNumber": tx
    })
    receipt.set_id(f'did:example:{order_id}')

    signed_receipt = await issuer.issue_credential(receipt)

    # Save credential on couchDB
    db.save({
        '_id' : order_id,
        'receipt' : json.loads(signed_receipt), 
        'refunded' : False, 
        'date': datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    })

    #Save on redis
    red.set(tx, json.dumps({'success' : True, 'order': order_id}))

    return tx

def pay_order(code, red, rpc_url):
    order = json.loads(red.get(code).decode())
    return render_template('pay.html',order=json.dumps(order), mumbai_url=rpc_url)

def success(tx, red):
    try:
        txh = json.loads(red.get(tx).decode())
    except AttributeError as e:
        return 'Not Found', 404

    if(txh['success'] == True):
        return render_template('success.html', tx=tx)
    else:
        return 'Not Found TX', 404
    
def get_receipts(db, status):

    if(status == 'false'):
        status = False
    elif(status == 'true'):
        status = True

    # Mango query
    query = {
        "selector": {
            "refunded": {"$eq": status}
        }
    }

    rs = []
    for doc in db.find(query):
        rs.append({
            '_id' : doc.get('_id'),
            'date' : doc.get('date'),
            'refunded' : doc.get('refunded')
        })
    return rs
    

async def get_credentials(red, db, issuer):

    # Mango query
    query = {
        "selector": {
            "refunded": {"$eq": False}
        }
    }

    # Run query
    result_set = []
    for doc in db.find(query):

        # get receipt
        vc = doc['receipt']

        #Generate VPs 
        vp = {
                "@context": ["https://www.w3.org/2018/credentials/v1","https://www.w3.org/2018/credentials/examples/v1"],
                "type": ["VerifiablePresentation"],
                "verifiableCredential": [vc],
            }
        try:
            vp = await issuer.issue_presentation(vp)
        except Exception as e:
            print(e)
            return 'Internal server error', 500

        result_set.append(vp)
    
    return result_set

def update_credentials_status(db):
    try:
        order_ids = request.json['order_ids']
    except:
        return 'Bad Request', 400
    
    for order_id in order_ids:
        doc = db.get(order_id)
        doc['refunded'] = 'pending'
        db.save(doc)
    
    return 'Success', 200

def insurance():
    return render_template('insurance.html')





