from datetime import datetime

class Refund:
    def __init__(self, *args):
        
        # create from scratch
        if(len(args) == 3):
            self._id = args[0]
            self.prescriptions = args[1]
            self.pharmacy = args[2]
            self.emitted = False
            self.emission_date = ''
            self.refund_amount = 0
            self.refund_txh = ''
        
        elif(len(args) == 7):
            self._id = args[0]
            self.prescriptions = args[1]
            self.pharmacy = args[2]
            self.emitted = args[3]
            self.emission_date = args[4]
            self.refund_amount = args[5]
            self.refund_txh = args[6]
        
        else:
            raise ValueError('Refund object is not valid')
        
    
    def compute_amount(self):
        amount = 0
        # just a mockup: we except Insurance to have a personal db where each drug has a price and a fixed refund percentage
        refund_percentage = 100
        for p in self.prescriptions:
            amount += p['price'] * refund_percentage * p['quantity'] / 100
        self.refund_amount = amount

    def pay_refund(self, payer):
        self.compute_amount()
        txh = payer.send_eth(self.refund_amount, self.pharmacy)
        return txh
    
    def change_to_emitted(self, txh):
        self.emitted = True
        self.emission_date = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        self.refund_txh = txh
        return self





