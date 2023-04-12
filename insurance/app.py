from flask import Flask, request, jsonify
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv
import didkit
import json

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
            prescription = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['receipt']['vp']
            verification_method = prescription['proof']['verificationMethod']
            didkit_options = {"proofPurpose": "assertionMethod", "verificationMethod": verification_method}
            await didkit.verify_presentation(json.dumps(prescription), json.dumps(didkit_options))
        except:
            print('Failed prescription presentation check')
            return 'Internal Server Error', 500
        
        # Check Prescription credential
        vc_list = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['receipt']['vp']['verifiableCredential']
        for vc in vc_list:
            try:
                verification_method = vc['proof']['verificationMethod']
                didkit_options = {"proofPurpose": "assertionMethod", "verificationMethod": verification_method}
                await didkit.verify_credential(json.dumps(vc), json.dumps(didkit_options))
                print(f'{vc["credentialSubject"]["id"]} is ok')
            except:
                print('Failed prescription credential check')
                return 'Internal Server Error', 500
        
        # Check TXH on blockchain (TODO)
        try:
            tx = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['receipt']['proofOfPayment']
            print(tx)
        except:
            print('Failed proofOfPayment check')
            return 'Internal Server Error', 500

        # Initiate refund process

    # Return results
    response = jsonify({'message': 'success'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5002)
