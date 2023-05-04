
class Prescription:
    def __init__(self, id, maxQuantity, price, drug):
       
        if(price < 0):
            raise ValueError('Price is negative')
        
        self.prId = id
        self.drug = drug
        self.maxQuantity = maxQuantity
        self.price = price
        self.quantity = 0

    def set_price(self, price):
        self.price = price
    
    def set_quantity(self, quantity):
        if(quantity < 1):
            raise ValueError('Quantity is less than 1')
        
        if(quantity > self.maxQuantity):
            raise ValueError('Quantity is greater than the maxQuantity allowed by prescription')
        self.quantity = quantity
    
    def serialize(self):
        jsonPrescription = {
            'prId' : self.prId,
            'maxQuantity' : self.maxQuantity,
            'quantity' : self.quantity,
            'price' : self.price
        }
        return jsonPrescription