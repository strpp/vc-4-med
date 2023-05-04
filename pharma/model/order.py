import uuid

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
        
