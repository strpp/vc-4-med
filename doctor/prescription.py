from flask import jsonify, request, render_template, url_for
from flask_socketio import SocketIO, join_room, leave_room
from datetime import timedelta, datetime
from model.issuer import Issuer
from model.credential import Credential
from model.credential_manifest import Credential_Manifest
import json
import uuid
import didkit
import os

doctor = os.getenv('DOCTOR')
# did:key
key_issuer = Issuer(
    'key', 
    'did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX', 
    json.dumps(json.load(open("key.pem", "r")))
)
# did:ethr
public_key = '0xd661a61c964b8872db826dc854888527c235119f'
chain_id = '0x13881'
ethr_issuer = Issuer(
    'ethr',
    f'did:ethr:{chain_id}:{public_key}',
    json.dumps(json.load(open("ethkey.pem", "r")))
)

# select
issuer = ethr_issuer


REDIS_DATA_TIME_TO_LIVE = 1800

def init_app(app, red, socketio) :
    app.add_url_rule('/endpoint/<stream_id>',  view_func=endpoint, methods = ['GET', 'POST'], defaults={"red" : red, "socketio" : socketio})
    app.add_url_rule('/callback/<stream_id>',  view_func=callback, methods = ['GET', 'POST'], defaults={"red" : red})
    app.add_url_rule('/generate-credential',  view_func=generate_credential, methods = ['POST'], defaults={"red" : red, "socketio" : socketio})
    return

# API to interact with smartphone (wallet)
async def endpoint(stream_id, red, socketio):

    if request.method == 'GET':
        try:
            print(f'Stream ID: {stream_id}')
            data = json.loads(red.get(stream_id).decode())
            drug = data['drug']
            dosage = data['dosage']
            proof_of_identity = data['proofOfIdentity']
        except:
            return jsonify('Bad request: missing or invalid stream_id'), 400
        
        # make an offer  
        credential_manifest = Credential_Manifest(f'did:example:{stream_id}')
        credential_manifest.set_description(f'A prescription for n.{dosage} of {drug}')
        credential_manifest.set_doctor(doctor)

        if (proof_of_identity == 'verifiableId'):
            print(data["name"])
            credential_manifest.add_proof_of_identity(data["name"], data["surname"])

        # generate credential        
        schema = json.load(open('credentials/PrescriptionNoPersonalInfo.jsonld', 'r'))
        credential = Credential(schema)
        credential.set_id(f'did:example:{stream_id}')
        # fill vc with values stored in redis
        try:
            credential.set_value('drug', data['drug'])
            credential.set_value('quantity', data['dosage'])
        except ValueError as ve:
            print('Invalid data for credential')
            return 500
        
        red.set(stream_id, json.dumps({'vc' : credential.schema}))
        
        credential_offer = {
            "type": "CredentialOffer",
            "credentialPreview": credential.schema,
            "expires" : (datetime.now() + timedelta(days= 365)).isoformat() + "Z",
            "credential_manifest" : credential_manifest.schema
        }
        return jsonify(credential_offer)

    else :  #POST

        schema = json.loads(red.get(stream_id).decode())['vc']
        credential = Credential(schema)
        socket_id = json.loads(red.get(f'ws:{stream_id}').decode())['socket_id']

        try:
            signed_credential =  await issuer.issue_credential(credential) 
        except:
            socketio.emit('stream_id', {'stream_id' : stream_id}, to=socket_id)
            return jsonify('Server failed'), 500
        
        # Redirect client via server push
        red.set(f'ws:{stream_id}', json.dumps({'socket_id' : socket_id, 'success' : True}))
        socketio.emit('stream_id', {'stream_id' : stream_id}, to=socket_id)
        
        # Success : send event to client agent to go forward
        return jsonify(signed_credential)

def generate_credential(red, socketio):
        
        #Generate stream id
        stream_id = str(uuid.uuid4().hex)

        @socketio.on('subscribe')
        def subscribe(data):
            # Add client to private channel to get further updates
            join_room(data['socket_id'])
            # Save socket_id on server session to make /authorize able to link socket_id and stream_id
            socket_id = data['socket_id']
            print(f'socket_id : {socket_id}, stream_id : {stream_id}')
            red.set(f'ws:{stream_id}', json.dumps({'socket_id' : socket_id, 'success' : False}))

        #Get values from form
        try:
            data = {
                'proofOfIdentity' : request.form['proofOfIdentity'],
                'name' : request.form['name'],
                'surname' : request.form['surname'],
                'drug' : request.form['drug'],
                'dosage' : request.form['dosage']
            }
        except:
            print('Missing value(s) for building credential')
            return 500
        
        #Save on Redis using stream_id as key
        red.set(stream_id, json.dumps(data))

        #Generate QR Code
        url = url_for('endpoint', stream_id=stream_id, _external=True)
        return render_template('qrcode.html', url=url)

def callback(stream_id, red):
    success = json.loads(red.get(f'ws:{stream_id}').decode())['success']
    return render_template('callback.html', success=success)

