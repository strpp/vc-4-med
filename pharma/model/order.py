import uuid
from model.prescription import Prescription

class Order:
    def __init__(self, prescriptions, pharmacy_address):
        self.prescriptions = prescriptions
        self.orderId = uuid.uuid4().hex
        self.totalPrice = self.compute_total_price()
        self.pharmacy = pharmacy_address

    
    def compute_total_price(self):
        total_price = 0
        for p in self.prescriptions:
            total_price += (p.quantity * p.price)
        return total_price
    
    def serialize(self):
        jsonPrescription = []
        for p in self.prescriptions:
            jsonPrescription.append(p.serialize())
        jsonOrder = {
            'prescriptions' : jsonPrescription,
            'orderId' : self.orderId,
            'totalPrice' : self.totalPrice,
            'pharmacy' : self.pharmacy
        }
        return jsonOrder
    
    def load_prescriptions_from_json(self, prescriptions):
        self.prescriptions = []
        for p in prescriptions:
            o = Prescription(p['prId'], p['maxQuantity'], p['price'], p['drug'])
            try:
                o.set_quantity(p['quantity'])
            except:
                pass
            self.prescriptions.append(o)
        self.totalPrice = self.compute_total_price()
        
