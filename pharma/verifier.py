from flask import jsonify, request, render_template, session, redirect, flash, Response
from flask_socketio import SocketIO, join_room, leave_room
from datetime import timedelta, datetime
import didkit
import json
import uuid
import os
import contract_api
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
    url = f'http://192.168.1.20:5001/verify/{stream_id}'
    print(url)
    return render_template('qrcode.html', url=url)

async def verify(stream_id, red, socketio):

    if request.method == 'GET':
        presentation_request = {
            "type": "VerifiablePresentationRequest",
            "query": [
                    {
                    "type": "QueryByExample",
                    "credentialQuery": [
                        {
                        "required": True,
                        "example": {
                            "type": "MedicalPrescriptionCredential",
                            "trustedIssuer": [
                                {
                                    "required": True,
                                    "issuer": "did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX"
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ],
            "challenge": str(uuid.uuid4),
            "domain": "www.example.com"
        }
        return jsonify(presentation_request)
    
    else: #POST
        form = request.form
        presentation = json.loads(form.get('presentation'))
        verification_method = presentation['proof']['verificationMethod']
        
        try:
            didkit_options = {"proofPurpose": "assertionMethod","verificationMethod": verification_method}
            await didkit.verify_presentation(json.dumps(presentation), json.dumps(didkit_options))

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
    credentialSubject = json.loads(red.get(stream_id).decode())['vp']['verifiableCredential']['credentialSubject']
    prescription = credentialSubject['prescription']
    return render_template('prescription.html', drug=prescription['drug'], dosage=prescription['dosage'], stream_id=stream_id)

def order(stream_id, red, socketio):
    prescription_id = json.loads(red.get(stream_id).decode())['vp']['verifiableCredential']['credentialSubject']['id']
    
    # create JSON order to be signed
    order_id = "abcd"
    order = {
        "p" : 
        [{
            "prId" : prescription_id, 
            "quantity" : request.form.get('quantity'),
            "maxQuantity" : json.loads(red.get(stream_id).decode())['vp']['verifiableCredential']['credentialSubject']['prescription']['dosage'],
            "price" : 1
        }],
        "orderId" : order_id,
        "totalPrice" : 1
    }

    @socketio.on('subscribe')
    def subscribe(data):
        # Add client to private channel to get further updates
        join_room(data['socket_id'])
        # Save socket_id on server session to make /authorize able to link socket_id and stream_id
        socket_id = data['socket_id']
        print(f'socket_id : {socket_id} listening for prescription_id : {prescription_id}')
        red.set(prescription_id, json.dumps({'prescription_id' : prescription_id, 'socket_id' : socket_id}))

    red.set(order_id, json.dumps(order))
    return order

# Receive order signed by pharmacy, store it on Redis and redirect to QRCode to make user able to pay with SC
def receive_sign(order_id, red):
    code = str(uuid.uuid4())
    order = json.loads(red.get(order_id).decode())
    signed_order = request.get_json()['signedOrder']
    red.set(code, json.dumps({'order' : order, 'signed_order' : signed_order}))
    return code, 200

def create_qr_order(code):
    url=f'http://192.168.1.20:5001/order/pay/{code}'
    return render_template('qrcode-sc.html', url=url)

def pay_order(code, red):
    order = json.loads(red.get(code).decode())
    return render_template('pay.html',order=json.dumps(order))
    


#TODO: change this function to handle the payment success and store the receipt
async def contract(stream_id, red, db, socketio):
    tx='1234'
    # Get data from Redis (prescription_id, quantity, socket_id)
    vp = json.loads(red.get(stream_id).decode())['vp']
    prescription_id = vp['verifiableCredential']['credentialSubject']['id']
    quantity = request.args.get('quantity')
    
    # Issue new credential (Prescription + Proof of payment)
    receipt = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt["issuer"] = DID_KEY
    receipt['issuanceDate'] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    receipt['expirationDate'] =  (datetime.now() + timedelta(days= 365)).isoformat() + "Z"
    receipt['id'] = f'did:example:{prescription_id}'
    receipt['credentialSubject']['receipt']['vp'] = vp
    receipt['credentialSubject']['receipt']['proofOfPayment'] = tx

    try:
        signed_receipt =  await didkit.issue_credential(json.dumps(receipt), json.dumps({}), jwk)
        print(signed_receipt)
    except:
        return 500

    # Save credential on couchDB
    db.save(json.loads(signed_receipt))

    # Push notification to pharmacy client listening
    socket_id = json.loads(red.get(prescription_id).decode())['socket_id']
    socketio.emit('txReceived', {'tx' : tx, "success" : True}, to=socket_id)
    
    return "Payment successfully executed"

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





