import couchdb
from model.refund import Refund

class dbConnector:
    def __init__(self):
        couch = couchdb.Server('http://localhost:5984')
        self.db = couch['insurance']

    def save(self, refund):
        try:
            self.db.save(refund.__dict__)
            return refund._id
        except:
            return False 

    def update(self, refund):
        refund = refund.__dict__
        doc = self.db.get(refund['_id'])
        keys = list(refund.keys())
        for key in keys:
            doc[key] = refund[key]
        self.db.save(doc)

    def getRefundNotEmitted(self, order_id):
        order = self.db.get(order_id)
        
        if(order.get('emitted') == True):
            return False

        r = Refund(
            order.get('_id'),
            order.get('prescriptions'),
            order.get('pharmacy'),
            order.get('emitted'),
            order.get('emission_date'),
            order.get('refund_amount'),
            order.get('refund_txh')
        )
        return r #order_id is unique so we expect exactly one result
        
    def getRefund(self, order_id):
        order = self.db.get(order_id)
        
        r = Refund(
            order.get('_id'),
            order.get('prescriptions'),
            order.get('pharmacy'),
            order.get('emitted'),
            order.get('emission_date'),
            order.get('refund_amount'),
            order.get('refund_txh')
        )

        return r #order_id is unique so we expect exactly one result
