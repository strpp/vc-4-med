from flask import jsonify, request, render_template, url_for
from flask_socketio import SocketIO, join_room, leave_room
from datetime import timedelta, datetime
from model.issuer import Issuer
from model.verifier import Verifier
from model.credential import Credential
import didkit
import json
import uuid
import os
import contract_listener as contract_listener
import collections.abc
from web3 import Web3

MUMBAI_URL = os.getenv('MUMBAI_URL')
PHARMACY_ADDRESS = os.getenv('PHARMACY_ADDRESS')

# did:key
key_issuer = Issuer(
    'key',
    os.getenv('DID_KEY'),
    json.dumps(json.load(open("key.pem", "r")))
)

# did:ethr
ethr_issuer = Issuer(
    'ethr',
    f'did:ethr:{PHARMACY_ADDRESS}',
    json.dumps(json.load(open("ethkey.pem", "r")))
)

# verifier
ethr_verifier = Verifier(
    'ethr',
    '0x13881'
) 

# select verifier
verifier = ethr_verifier
issuer = ethr_issuer

def init_app(app, red, socketio, couch) : 
    db = couch['vc']
    app.add_url_rule('/authorize',  view_func=authorize, methods = ['POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/verify/<stream_id>/<number_of_prescriptions>',  view_func=verify, methods = ['GET','POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/callback/<stream_id>',  view_func=callback, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/success/<tx>',  view_func=success, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/order/<stream_id>',  view_func=order, methods = ['POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/order/sign/<order_id>',  view_func=receive_sign, methods = ['POST'], defaults={"red" : red})
    app.add_url_rule('/order/qr/<code>',  view_func=create_qr_order, methods = ['GET'])
    app.add_url_rule('/order/pay/<code>',  view_func=pay_order, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/order/wait/<code>',  view_func=wait_order, methods = ['GET'], defaults={"red" : red, "db":db})
    app.add_url_rule('/api/credentials',  view_func=get_credentials, methods = ['GET', 'POST'], defaults={"red" : red, "db": db})
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

async def verify(stream_id, number_of_prescriptions, red, socketio):

    if request.method == 'GET':
        presentation_request = json.load(open('credentials/vp_request.json', 'r'))
        for i in range(1, int(number_of_prescriptions)+1):
            presentation_request['query'][0]['credentialQuery'].append({"example": {"type": "MedicalPrescriptionCredential"}})
        presentation_request['challenge'] = str(uuid.uuid4())
        return jsonify(presentation_request)
    
    else: #POST
        form = request.form
        presentation = form.get('presentation')
        
        try:
            result = await verifier.verify_presentation(presentation)
            if(result == False):
                return 'Presentation is not valid', 500
            
        except Exception as e:
            print(e)
            return 'Credential verification failed.', 400
            
        if(verifier.are_credentials_unique(presentation) == False):
            return 'There are duplicate credentials in the presentation', 500

        # Redirect client via server push
        socket_id = json.loads(red.get(stream_id).decode())['socket_id']
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
    vcs = []
    result = json.loads(red.get(stream_id).decode())['vp']['verifiableCredential']
    # if we have multiple vcs, just save the array
    if isinstance(result, collections.abc.Sequence):
        vcs = result
    # if vc is single, create an array
    else:
        vcs.append(result)

    return render_template('prescription.html', vcs={'vcs': vcs}, stream_id=stream_id)

# Handle request for creating a new order from pharmacy
def order(stream_id, red, socketio):

    prescriptions = json.loads(red.get(stream_id).decode())['vp']['verifiableCredential']
    prs = []
    total_price = 0

    if isinstance(prescriptions, collections.abc.Sequence):
        # get prescriptions
        for p in prescriptions:
            quantity = int(request.form.get(p['credentialSubject']['drug']))
            if quantity > 0 :
                price = 1 # TODO: just a mockup
                prescription = {
                    "prId" : p['credentialSubject']['id'],
                    "quantity" : quantity,
                    "maxQuantity" : p['credentialSubject']['quantity'],
                    "price" : price
                }
                prs.append(prescription)
                total_price+=(price*quantity)
    else: #just one prescription
        quantity = int(request.form.get(prescriptions['credentialSubject']['drug']))
        if ( quantity > 0):
            price = 1 # TODO: just a mockup
            prs.append(
                {
                    "prId" : prescriptions['credentialSubject']['id'],
                    "quantity" : quantity,
                    "maxQuantity" : prescriptions['credentialSubject']['quantity'],
                    "price" : price
                }
            )
            total_price=(price*quantity)
    
    # create JSON order to be signed
    order_id = uuid.uuid4().hex
    order = {
        "prescriptions" : prs,
        "orderId" : order_id,
        "totalPrice" : total_price,
        "pharmacy" : PHARMACY_ADDRESS
    }
    red.set(order_id, json.dumps({'order' : order, 'stream_id' : stream_id, 'signed_order' : 'null'}))
    return order

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

async def wait_order(code, red, db):
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
    receipt.change_value("invoice", {
            "description": vp,
            "confirmationNumber": tx
    })
    receipt.set_id(f'did:example:{order_id}')

    signed_receipt = await issuer.issue_credential(receipt)

    # Save credential on couchDB
    db.save(json.loads(signed_receipt))    
    return tx

def pay_order(code, red):
    order = json.loads(red.get(code).decode())
    return render_template('pay.html',order=json.dumps(order), mumbai_url=MUMBAI_URL)

def success(tx, red):
    return f'Payment successfully executed with TxHash:{tx}'

async def get_credentials(red, db):
    issuanceDate = "2024-03-27T20:52:06Z" #TODO

    # Mango query
    query = {
        "selector": {
            "issuanceDate": {"$lte": issuanceDate}
        }
    }

    # Run query
    result_set = []
    for vc in db.find(query):
        #Delete CouchDB keys
        vc.pop('_id', None)
        vc.pop('_rev', None)

        #Generate VPs 
        vp = {
                "@context": ["https://www.w3.org/2018/credentials/v1","https://www.w3.org/2018/credentials/examples/v1"],
                "type": ["VerifiablePresentation"],
                "verifiableCredential": [vc],
            }
        try:
            vp = await issuer.issue_presentation(vp)
        except:
            return 'Internal server error', 500

        result_set.append(vp)
    
    return result_set

def insurance():
    return render_template('insurance.html')





