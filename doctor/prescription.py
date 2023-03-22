from flask import jsonify, request, render_template, session, redirect, flash, Response
from datetime import timedelta, datetime
import json
import uuid
import didkit
from web3 import Web3

#Keypair generated with DIDkit
jwk = json.dumps(json.load(open("key.pem", "r")))
did = 'did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX'
doctor = 'Dr. Mario Rossi'

REDIS_DATA_TIME_TO_LIVE = 1800

def init_app(app, red) :
    app.add_url_rule('/endpoint/<stream_id>',  view_func=endpoint, methods = ['GET', 'POST'], defaults={"red" : red})
    app.add_url_rule('/generate-credential',  view_func=generate_credential, methods = ['POST'], defaults={"red" : red})
    return

# API to interact with smartphone (wallet)
async def endpoint(stream_id, red):

    
    if request.method == 'GET':
        
        try:
            print(f'Stream ID: {stream_id}')
            data = json.loads(red.get(stream_id).decode())
            drug = data['drug']
            dosage = data['dosage']
        except:
            return jsonify('Bad request: missing or invalid stream_id'), 400
        
        # make an offer  
        credential_manifest = json.load(open('credentials/prescription_credential_manifest.json', 'r'))
        credential_manifest['issuer']['id'] = did
        credential_manifest['output_descriptors'][0]['id'] = f'did:example:{stream_id}'
        # fill with doctor and prescription details
        credential_manifest['output_descriptors'][0]['display']['subtitle']['fallback'] = f'A prescription for n.{dosage} of {drug}'
        credential_manifest['output_descriptors'][0]['display']['properties'][0]['fallback'] = doctor

        credential = json.load(open('credentials/Prescription.jsonld', 'r'))
        credential["issuer"] = did
        credential['issuanceDate'] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        credential['expirationDate'] =  (datetime.now() + timedelta(days= 365)).isoformat() + "Z"
        credential['id'] = f'did:example:{stream_id}'
        # use keccak hash to optimize smart contract
        credential['credentialSubject']['id'] = (Web3.keccak(text=stream_id)).hex()

        # fill vc with values stored in redis
        keys = credential['credentialSubject']['prescription'].keys()
        for k in keys:
            try:
                 credential['credentialSubject']['prescription'][k] = data[k]
            except:
                 pass
        
        red.set(stream_id, json.dumps({'vc' : credential}))
        
        credential_offer = {
            "type": "CredentialOffer",
            "credentialPreview": credential,
            "expires" : '2024-02-20T18:15:39Z',
            "credential_manifest" : credential_manifest
        }
        return jsonify(credential_offer)

    else :  #POST

        credential = json.loads(red.get(stream_id).decode())['vc']

        # does not work => didkit.DIDKitException: Missing verification relationship
        didkit_options = {
            "proofPurpose": "assertionMethod",
            "verificationMethod": did,
        }

        signed_credential =  await didkit.issue_credential(json.dumps(credential), json.dumps({}), jwk)
        
        if not signed_credential :         # send event to client agent to go forward
            return jsonify('Server failed'), 500
        # Success : send event to client agent to go forward

        #TODO: insert prescription on blockchain using smart contract

        return jsonify(signed_credential)

def generate_credential(red):
        
        #Generate stream id
        stream_id = str(uuid.uuid4().hex)

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
        for k in form_keys:
             if(k in prescription_keys):
                  data[k] = request.form[k]
        
        #Save on Redis using stream_id as key
        red.set(stream_id, json.dumps(data))

        #Generate QR Code
        url = f'http://192.168.1.20:5000/endpoint/{stream_id}'
        print(url)
        return render_template('qrcode.html', url=url)
