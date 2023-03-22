from flask import jsonify, request, render_template, session, redirect, flash, Response
from datetime import timedelta, datetime
import json
import uuid
import didkit

#Keypair generated with DIDkit
jwk = json.dumps(json.load(open("key.pem", "r")))
did = 'did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX'

REDIS_DATA_TIME_TO_LIVE = 1800

def init_app(app, red) :
    app.add_url_rule('/endpoint/<stream_id>',  view_func=endpoint, methods = ['GET', 'POST'], defaults={"red" : red})
    app.add_url_rule('/generate-credential',  view_func=generate_credential, methods = ['POST'], defaults={"red" : red})
    return

# API to interact with smartphone (wallet)
async def endpoint(stream_id, red):
    try:
        print(f'Stream ID: {stream_id}')
        data = json.loads(red.get(stream_id).decode())
    except:
        data =  {'name': 'mario', 'surname': 'rossi', 'drug': 'oki', 'dosage': '2'}
        #return jsonify('Bad request: missing or invalid stream_id'), 400

    credential = json.load(open('credentials/Prescription.jsonld', 'r'))
    credential["issuer"] = did
    credential['issuanceDate'] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    credential['expirationDate'] =  (datetime.now() + timedelta(days= 365)).isoformat() + "Z"
    
    if request.method == 'GET': 
        # make an offer  
        credential_manifest = json.load(open('credentials/prescription_credential_manifest.json', 'r'))
        credential_manifest['issuer']['id'] = did
        credential_manifest['output_descriptors'][0]['id'] = '1234'
        credential['id'] = "did:example:1234"
        credential['credentialSubject']['id'] = "did:example:1234"
        credential_offer = {
            "type": "CredentialOffer",
            "credentialPreview": credential,
            "expires" : '2024-02-20T18:15:39Z',
            "credential_manifest" : credential_manifest
        }
        return jsonify(credential_offer)

    else :  #POST
        credential = json.load(open('credentials/Prescription.jsonld', 'r'))
        credential['issuer'] = did
        # fill vc with values stored in redis
        keys = credential['credentialSubject']['claim'].keys()
        print(credential['credentialSubject']['claim'], data)
        for k in keys:
            try:
                 credential['credentialSubject']['claim'][k] = data[k]
            except:
                 pass

        # does not work => didkit.DIDKitException: Missing verification relationship
        didkit_options = {
            "proofPurpose": "assertionMethod",
            "verificationMethod": did,
        }

        signed_credential =  await didkit.issue_credential(json.dumps(credential), json.dumps({}), jwk)
        if not signed_credential :         # send event to client agent to go forward
            return jsonify('Server failed'), 500
        # Success : send event to client agent to go forward
        return jsonify(signed_credential)

def generate_credential(red):
        
        #Generate stream id
        stream_id = str(uuid.uuid1())

        form_keys = list(request.form.keys())
         
        #Load credential to check which values we have to save
        vc_to_issue = request.form['vc']
        try:
            vc = json.load(open(f'credentials/{vc_to_issue}.jsonld', 'r'))
            claim = vc['credentialSubject']['claim']
            claim_keys = claim.keys()
        except:
             return jsonify('Bad request'), 400

        #Get values from form
        data = {}
        for k in form_keys:
             if(k in claim_keys):
                  data[k] = request.form[k]
        
        #Save on Redis using stream_id as key
        red.set(stream_id, json.dumps(data))

        #Generate QR Code
        url = f'http:192.168.1.20:5000/endpoint/{stream_id}'
        return render_template('qrcode.html', url=url)
