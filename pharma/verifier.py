from flask import jsonify, request, render_template, url_for
from flask_socketio import SocketIO, join_room, leave_room
from datetime import timedelta, datetime
import didkit
import json
import uuid
import os
import random
import contract_listener as contract_listener
from web3 import Web3

DID_KEY = os.getenv('DID_KEY')
VERIFICATION_METHOD = 'did:key:z6MktaAfLYZF3khaHZuWCho1vrJkDPXx1nkHtPSXFSwk6g5i#z6MktaAfLYZF3khaHZuWCho1vrJkDPXx1nkHtPSXFSwk6g5i'
jwk = json.dumps(json.load(open("key.pem", "r")))

def init_app(app, red, socketio, couch) : 
    db = couch['vc']
    app.add_url_rule('/authorize',  view_func=authorize, methods = ['GET', 'POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/verify/<stream_id>',  view_func=verify, methods = ['GET','POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/callback/<stream_id>',  view_func=callback, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/success/<tx>',  view_func=success, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/order/<stream_id>',  view_func=order, methods = ['POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/order/sign/<order_id>',  view_func=receive_sign, methods = ['POST'], defaults={"red" : red})
    app.add_url_rule('/order/qr/<code>',  view_func=create_qr_order, methods = ['GET'])
    app.add_url_rule('/order/pay/<code>',  view_func=pay_order, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/order/wait/<code>',  view_func=wait_order, methods = ['GET'], defaults={"red" : red, "db":db})
    app.add_url_rule('/api/credentials',  view_func=get_credentials, methods = ['GET', 'POST'], defaults={"red" : red, "db": db})
    app.add_url_rule('/insurance',  view_func=insurance, methods = ['GET'])
    app.add_url_rule('/info',  view_func=verifier_info, methods = ['GET'])

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
    url = url_for('verify', stream_id=stream_id, _external = True)
    print(url)
    return render_template('qrcode.html', url=url)

async def verify(stream_id, red, socketio):

    # TODO
    number_prescription = 2

    if request.method == 'GET':
        presentation_request = json.load(open('credentials/vp_request.json', 'r'))
        for i in range(1,number_prescription+1):
            presentation_request['query'][0]['credentialQuery'].append({"example": {"type": "MedicalPrescriptionCredential"}})
        presentation_request['challenge'] = str(uuid.uuid4())
        return jsonify(presentation_request)
    
    else: #POST
        form = request.form
        presentation = json.loads(form.get('presentation'))
        verification_method = presentation['proof']['verificationMethod']
        
        try:
            didkit_options = {"proofPurpose": "assertionMethod","verificationMethod": verification_method}
            await didkit.verify_presentation(json.dumps(presentation), json.dumps(didkit_options))

            # Check VCs are unique
            ids = []
            for vc in presentation['verifiableCredential']:
                if (vc['credentialSubject']['id']) not in ids:
                    ids.append(vc['credentialSubject']['id'])
                else:
                    #TODO emit error with socketio
                    return 'Error: VCs are not unique', 500

            # Redirect client via server push
            socket_id = json.loads(red.get(stream_id).decode())['socket_id']
            socketio.emit('stream_id', {'stream_id' : stream_id}, to=socket_id)

            # Save the tokens in the session
            red.set(stream_id, json.dumps({'stream_id' : stream_id, 'socket_id' : socket_id, 'verified' : True, 'vp' : presentation}))

            # Send ok to wallet
            return 'Credential verified successfully!', 200
        
        except Exception as e:
            print(e)
            return 'Credential verification failed.', 400


def callback(stream_id, red):
    vcs = json.loads(red.get(stream_id).decode())['vp']['verifiableCredential']
    return render_template('prescription.html', vcs={'vcs': vcs}, stream_id=stream_id)

# Handle request for creating a new order from pharmacy
def order(stream_id, red, socketio):
    print(request.form)

    prescriptions = json.loads(red.get(stream_id).decode())['vp']['verifiableCredential']

    prs = []
    total_price = 0

    # get prescriptions
    for p in prescriptions:
        price = random.randint(1, 50) # TODO: just a mockup
        prescription = {
            "prId" : p['credentialSubject']['id'],
            "quantity" : request.form.get(p['credentialSubject']['prescription']['drug']),
            "maxQuantity" : p['credentialSubject']['prescription']['dosage'],
            "price" : price
        }
        prs.append(prescription)
        total_price+=price
    
    # create JSON order to be signed
    order_id = uuid.uuid4().hex
    order = {
        "p" : prs,
        "orderId" : order_id,
        "totalPrice" : total_price
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
    # NOTE: commented til we deploy on mumbai tx = contract_listener.main(order_id)
    tx = '0x1234abcd'
    if not tx:
        return 'Timeout while listening blockchain', 500

    # Get data from Redis (prescription_id, quantity, socket_id)
    vp = json.loads(red.get(stream_id).decode())['vp']
    #prescription_id = vp['verifiableCredential']['credentialSubject']['id']
    
    # Issue new credential (Prescription + Proof of payment)
    receipt = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt["issuer"] = DID_KEY
    receipt['issuanceDate'] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    receipt['expirationDate'] =  (datetime.now() + timedelta(days= 365)).isoformat() + "Z"
    receipt['id'] = f'did:example:{order_id}'
    receipt['credentialSubject']['receipt']['vp'] = vp
    receipt['credentialSubject']['receipt']['proofOfPayment'] = tx

    try:
        signed_receipt =  await didkit.issue_credential(json.dumps(receipt), json.dumps({}), jwk)
    except:
        return 'Error while signing the order receipt', 500

    # Save credential on couchDB
    db.save(json.loads(signed_receipt))    
    return tx

def pay_order(code, red):
    order = json.loads(red.get(code).decode())
    return render_template('pay.html',order=json.dumps(order))

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
            vp = await didkit.issue_presentation(
                json.dumps(vp),
                # TODO 
                json.dumps({'verificationMethod': VERIFICATION_METHOD}), 
                jwk
            )
        except:
            return 'Internal server error', 500

        result_set.append(vp)
    
    return result_set

def insurance():
    return render_template('insurance.html')

def verifier_info():
    info = {'DID_KEY' : DID_KEY, 'VERIFICATION_METHOD' : VERIFICATION_METHOD}
    return jsonify(info)





