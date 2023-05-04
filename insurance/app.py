from flask import Flask, request, jsonify
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv
import didkit
import json
import collections.abc
import blockchain_reader

app = Flask(__name__)
CORS(app)
app.secret_key = 'mysecretkey' # set the secret key for sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


@app.route('/')
def index():
    return "Insurance API"

@app.route('/api/refund', methods=['POST'])
async def refund():
    try:
        vps = request.json
    except:
        return 'Bad Request', 400

    for vp in vps:
        # Check Receipt presentation
        try:
            verification_method = json.loads(vp)['proof']['verificationMethod']
            didkit_options = {"proofPurpose": "assertionMethod", "verificationMethod": verification_method}
            await didkit.verify_presentation(vp, json.dumps(didkit_options))
        except:
            print('Failed receipt check')
            return 'Internal Server Error', 500
        # Check Prescription presentation
        try:
            prescription = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['invoice']['description']
            verification_method = prescription['proof']['verificationMethod']
            didkit_options = {"proofPurpose": "assertionMethod", "verificationMethod": verification_method}
            await didkit.verify_presentation(json.dumps(prescription), json.dumps(didkit_options))
        except Exception as e: 
            print('Failed prescription presentation check')
            print(e)
            return 'Internal Server Error', 500
        
        # Check Prescription credential
        vc_list = []
        prId_list = []
        data = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['invoice']['description']['verifiableCredential']
        
        # if we have only one vc, this is not an array so we have to check and in case is not, build one
        if isinstance(data, collections.abc.Sequence):
            vc_list = data
        else:
            vc_list.append(data)

        for vc in vc_list:
            try:
                verification_method = vc['proof']['verificationMethod']
                didkit_options = {"proofPurpose": "assertionMethod", "verificationMethod": verification_method}
                verification = await didkit.verify_credential(json.dumps(vc), json.dumps(didkit_options))
                print(verification)
                prId_list.append(vc["credentialSubject"]["id"])
                print(f'{vc["credentialSubject"]["id"]} is ok')
            except:
                print('Failed prescription credential check')
                return 'Internal Server Error', 500

        # read blockchain to get order related to receipt
        try: 
            tx = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['invoice']['confirmationNumber']
            params = blockchain_reader.decode(tx)
            order = params['order']
        except:
            print('Error while reading the blockchain')
            return 'Blockchain Reader Error', 500

        # extract prId from order
        for p in order['prescriptions']:
            if p['prId'] not in prId_list:
                print('Order contains a drug without a valid verifiable credential')
                return 'Order is not valid', 500
        
        # Initiate refund process

    # Return results
    response = jsonify({'message': 'success'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5002)
