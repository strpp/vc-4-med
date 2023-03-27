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
jwk = json.dumps(json.load(open("key.pem", "r")))

def init_app(app, red, socketio, couch) : 
    db = couch['vc']
    app.add_url_rule('/authorize',  view_func=authorize, methods = ['GET', 'POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/verify/<stream_id>',  view_func=verify, methods = ['GET','POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/callback/<stream_id>',  view_func=callback, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/success/<tx>',  view_func=success, methods = ['GET','POST'], defaults={"red" : red})
    app.add_url_rule('/order/<stream_id>',  view_func=order, methods = ['POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/contract/<stream_id>',  view_func=contract, methods = ['GET', 'POST'], defaults={"red" : red, "db": db, "socketio" : socketio})
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
    # url to make client interact with smart contract and pay
    form = request.form
    # add quantity to redis
    quantity_to_order = request.form.get('quantity')

    prescription_id = json.loads(red.get(stream_id).decode())['vp']['verifiableCredential']['credentialSubject']['id']

    @socketio.on('subscribe')
    def subscribe(data):
        # Add client to private channel to get further updates
        join_room(data['socket_id'])
        # Save socket_id on server session to make /authorize able to link socket_id and stream_id
        socket_id = data['socket_id']
        print(f'socket_id : {socket_id} listening for prescription_id : {prescription_id}')
        red.set(prescription_id, json.dumps({'prescription_id' : prescription_id, 'socket_id' : socket_id}))

    url = f'http://192.168.1.20:5001/contract/{stream_id}?quantity={quantity_to_order}'
    return render_template('qrcode-sc.html', url=url)

async def contract(stream_id, red, db, socketio):

    # Get data from Redis (prescription_id, quantity, socket_id)
    vp = json.loads(red.get(stream_id).decode())['vp']
    prescription_id = vp['verifiableCredential']['credentialSubject']['id']
    quantity = request.args.get('quantity')

    # Call SC to perform operations
    try:
        tx = await contract_api.pay_order(prescription_id, quantity, os.getenv('PHARMACY_ADDRESS'))
    except:
        return 500
    
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





