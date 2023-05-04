
class Prescription:
    def __init__(self, id, quantity, maxQuantity, price):

        if(quantity < 1):
            raise ValueError('Quantity is less than 1')
        
        if(quantity > maxQuantity):
            raise ValueError('Quantity is greater than the maxQuantity allowed by prescription')
        
        if(price < 0):
            raise ValueError('Price is negative')
        
        self.prId = id
        self.quantity = quantity
        self.maxQuantity = maxQuantity
        self.price = price

    def set_price(self, price):
        self.price = price
    
    def serialize(self):
        return self.__dict__