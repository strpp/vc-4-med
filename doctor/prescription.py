from flask import jsonify, request, render_template, url_for
from flask_socketio import SocketIO, join_room, leave_room
from datetime import timedelta, datetime
import json
import uuid
import didkit
import os
import web3

doctor = os.getenv('DOCTOR')
# did:key
jwk = json.dumps(json.load(open("key.pem", "r")))
did = 'did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX'
# did:ethr
eth_jwk = json.dumps(json.load(open("ethkey.pem", "r")))
public_key = '0xd661a61c964b8872db826dc854888527c235119f'
chain_id = '0x13881'
ethr_did = f'did:ethr:{chain_id}:{public_key}'
verification_method = f'did:ethr:{chain_id}:{public_key}#controller'


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
        credential_manifest = json.load(open('credentials/prescription_credential_manifest.json', 'r'))

        # NOTE -> did:key credential_manifest['issuer']['id'] = did
        credential_manifest['issuer']['id'] = ethr_did
        
        credential_manifest['output_descriptors'][0]['id'] = f'did:example:{stream_id}'
        # fill with doctor and prescription details
        credential_manifest['output_descriptors'][0]['display']['subtitle']['fallback'] = f'A prescription for n.{dosage} of {drug}'
        credential_manifest['output_descriptors'][0]['display']['properties'][0]['fallback'] = doctor
        if (proof_of_identity == 'verifiableId'):
            credential_manifest['presentation_definition']['id'] = str(uuid.uuid4())
            filter_type = {
                "path": ["$.type"],
                "filter": {
                    "type": "string",
                    "pattern": "VerifiableId"
                }
            }
            # NOTE: i don't know why on Altme Name=FamilyName and Surname=firstName
            filter_first_name =  {
                "path": [
                    "$.credentialSubject.firstName"
                ],
                "filter": {
                    "type": "string",
                    "pattern": data["surname"].upper()
                }
            }
            filter_family_name =  {
                "path": [
                    "$.credentialSubject.familyName"
                ],
                "filter": {
                    "type": "string",
                    "pattern": data["name"].upper()
                }
            }

            credential_manifest['presentation_definition']['input_descriptors'][0]['constraints']['fields'] = [
                 filter_type, filter_first_name, filter_family_name
            ]
        
        elif(proof_of_identity == 'none'):
            credential_manifest['presentation_definition'] = {}
        
        credential = json.load(open('credentials/PrescriptionNoPersonalInfo.jsonld', 'r'))

        # NOTE -> did:key credential["issuer"] = did = did
        credential["issuer"] = ethr_did
        
        credential['issuanceDate'] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        credential['expirationDate'] =  (datetime.now() + timedelta(days= 365)).isoformat() + "Z"
        credential['id'] = f'did:example:{stream_id}'
        credential['credentialSubject']['id'] = f'did:example:{uuid.uuid4().hex}'

        # fill vc with values stored in redis
        credential['credentialSubject']['drug'] = data['drug']
        credential['credentialSubject']['quantity'] = data['dosage']
        
        red.set(stream_id, json.dumps({'vc' : credential}))
        
        credential_offer = {
            "type": "CredentialOffer",
            "credentialPreview": credential,
            "expires" : (datetime.now() + timedelta(days= 365)).isoformat() + "Z",
            "credential_manifest" : credential_manifest
        }
        return jsonify(credential_offer)

    else :  #POST

        credential = json.loads(red.get(stream_id).decode())['vc']
        socket_id = json.loads(red.get(f'ws:{stream_id}').decode())['socket_id']

        # did:key
        #signed_credential =  await didkit.issue_credential(json.dumps(credential), json.dumps({}), jwk)
        
        # did:ethr
        options = {
            "proofPurpose" : "assertionMethod",
            "verificationMethod" : verification_method,
        }
        print(credential)
        signed_credential =  await didkit.issue_credential(
            json.dumps(credential),
            options.__str__().replace("'", '"'),
            eth_jwk
        )        

        if not signed_credential :         # send event to client agent to go forward
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

        form_keys = list(request.form.keys())
        #Load credential to check which values we have to save
        vc_to_issue = request.form['vc']
        try:
            vc = json.load(open(f'credentials/{vc_to_issue}.jsonld', 'r'))
            prescription = vc['credentialSubject']['prescription']
            prescription_keys = prescription.keys()
        except:
             return jsonify('Bad request'), 400

        #Get values from form
        data = {}
        data['proofOfIdentity'] = request.form['proofOfIdentity']
        for k in form_keys:
             if(k in prescription_keys):
                  data[k] = request.form[k]
        
        #Save on Redis using stream_id as key
        red.set(stream_id, json.dumps(data))

        #Generate QR Code
        url = url_for('endpoint', stream_id=stream_id, _external=True)
        return render_template('qrcode.html', url=url)

def callback(stream_id, red):
    success = json.loads(red.get(f'ws:{stream_id}').decode())['success']
    return render_template('callback.html', success=success)

