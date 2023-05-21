from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from model.verifier import Verifier
from model.registry import Registry
from model.error import Error
from model.refund import Refund
from model.db_connector import dbConnector
from model.blockchain_payer import blockchainPayer
import json
import requests
import collections.abc
import blockchain_reader
import socket


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
bp = blockchainPayer(
    app.config['RPC_URL'],
    app.config['CHAIN_ID'],
    app.config['MY_PUBLIC_KEY'],
    app.config['MY_PRIVATE_KEY']
)

hostname = socket.gethostname()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/refund', methods=['GET'])
async def get_refund():
    dbc = dbConnector(app.config['MODE'], hostname)
    result_set = dbc.getAllRefund()
    return jsonify(result_set)

@app.route('/api/refund/<status>', methods=['GET'])
async def get_all_refund(status):
    if(status == 'false'):
        status = False
    elif(status == 'true'):
        status = True
    else:
        return 'Bad Request', 400
    
    dbc = dbConnector(app.config['MODE'], hostname)
    result_set = dbc.getAllRefundFilterEmitted(status)
    return jsonify(result_set)


@app.route('/api/refund', methods=['POST'])
async def create_refund():
    try:
        vps = request.json
    except:
        return 'Bad Request', 400

    errors = []
    refunds = []

    for vp in vps:
        # Check Receipt presentation
        result = await verifier.verify_presentation(vp, 'MedicalReceiptCredential')
        if(result == False):
            print('Invalid receipt presentation')
            e = Error(
                json.loads(vp)['verifiableCredential'][0]['id'],
                'Invalid receipt presentation'
            )
            errors.append(e.to_dict())
            continue
        
        prescription = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['invoice']['description']
        result = await verifier.verify_presentation(json.dumps(prescription), 'MedicalPrescriptionCredential')
        if(result == False):
            print('Invalid prescription presentation')
            e = Error(prescription['id'],'Invalid prescription presentation')
            errors.append(e.to_dict())
            continue
        
        # Check Prescription credential
        vc_list = []
        prId_dict = {}
        data = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['invoice']['description']['verifiableCredential']
        
        # if we have only one vc, this is not an array so we have to check and in case is not, build one
        if isinstance(data, collections.abc.Sequence):
            vc_list = data
        else:
            vc_list.append(data)

        for vc in vc_list:
            result = await verifier.verify_credential(json.dumps(vc), 'MedicalPrescriptionCredential')
            if(result == False):
                print('Invalid prescription credential')
                e = Error(vc['credentialSubject']['id'],'Invalid prescription credential')
                errors.append(e.to_dict())
                continue
            
            # we need to save the drug to know the price and the refund percentage
            prId_dict[ vc["credentialSubject"]["id"] ] = vc["credentialSubject"]["drug"]

        # read blockchain to get order related to receipt
        try: 
            tx = json.loads(vp)['verifiableCredential'][0]['credentialSubject']['invoice']['confirmationNumber']
            params = blockchain_reader.decode(tx)
            order = params['order']
        except:
            e = Error(tx, 'Error while reading blockchain')
            errors.append(e.to_dict())

        # check prId from order
        for p in order['prescriptions']:
            """
            if p['prId'] not in prId_list:
                e = Error(order['orderId'], 'Order contains a invalid prescription id ')
                errors.append(e.to_dict())
                break  # order is not valid so skip to next
            """
            p['drug'] = prId_dict[ p['prId'] ]
            
        # orderId must be unique to avoid duplicate refund
        dbc = dbConnector(app.config['MODE'], hostname)


        if( dbc.getRefund(order['orderId']) != False ):
            e = Error(order['orderId'], 'Order has already been inserted in DB')
            errors.append(e.to_dict())
        
        else:
            # Save refund instance
            refund = Refund(order['orderId'], order['prescriptions'], order['pharmacy'])
            refund.compute_amount()
            dbc.save(refund)
            refunds.append(order['orderId'])
    
    return jsonify({'errors': errors, 'refunds': refunds})


@app.route('/api/emit/refund', methods=['GET','POST'])
async def emit_refund():
    try:
        order_ids = request.json['order_ids']
    except:
        return 'Bad Request', 400
    
    errors = []
    refunds = []
    dbc = dbConnector(app.config['MODE'], hostname)



    for order_id in order_ids:
        # get refund from db
        refund = dbc.getRefundNotEmitted(order_id)
        if(refund == False):
            print('Order not found or already refunded')
            e = Error(order_id, 'Order not found or already refunded')
            errors.append(e.to_dict())
            continue
        
        # pay back amount
        txh = refund.pay_refund(bp)
        print(order_id)
        if(txh == False):
            print('Error while emitting refund n:{order_id}')
            e = Error(order_id, 'Error while emitting refund')
            errors.append(e.to_dict())
            continue

        # update refund object and save on db
        updated_refund = refund.change_to_emitted(txh)
        dbc.update(updated_refund)
        refunds.append({'id':updated_refund._id, 'txh': txh, 'amount': updated_refund.refund_amount})
    
    # notify pharma about refund success
    order_ids = list(map(lambda x: x.get('id'), refunds))
    res = requests.post('http://192.168.1.20:5001/api/credentials/true', json={'order_ids': order_ids})
    
    return jsonify({'errors': errors, 'refunds': refunds})

@app.route('/api/order/<order_id>', methods=['GET'])
async def retrieve_refund(order_id):
    dbc = dbConnector(app.config['MODE'], hostname)
    refund = dbc.getRefund(order_id)
    if(refund == False):
        return 'Order not found', 404
    
    return jsonify(refund.__dict__)
        
if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5002)
