from flask import Flask, request, jsonify
from flask_cors import CORS
from model.verifier import Verifier
from model.registry import Registry
import json
import collections.abc
import blockchain_reader

app = Flask(__name__)
CORS(app)

app.config.from_pyfile('config.py')

registry = Registry(
    app.config['RPC_URL'],
    app.config['REGISTRY_ADDRESS'],
    app.config['DOCTOR_IDENTITY'],
    app.config['PHARMACY_IDENTITY']
)

verifier = Verifier(registry)

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
        result = await verifier.verify_presentation(vp, 'MedicalReceiptCredential')
        if(result == False):
            return 'Invalid invoice', 500
        
        
        prescription = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['invoice']['description']
        result = await verifier.verify_presentation(json.dumps(prescription), 'MedicalPrescriptionCredential')
        if(result == False):
            return 'Invalid Prescription Presentation', 500
        
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
            print(vc)
            result = await verifier.verify_credential(json.dumps(vc), 'MedicalPrescriptionCredential')
            if(result == False):
                return 'Invalid Prescription Credential', 500
            prId_list.append(vc["credentialSubject"]["id"])

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
