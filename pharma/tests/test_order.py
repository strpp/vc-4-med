from model.prescription import Prescription
from model.order import Order
import json

def test_create_new_order():
    number = 5
    prescriptions = []
    for i in range(0, number):
        p = Prescription('12345', 3, 1, 'abcd')
        p.set_quantity(3)
        prescriptions.append(p)
    order = Order(prescriptions, '0xABCD')
    assert order.totalPrice == 15

def test_create_order_from_json():
    prs =[{'prId': 'did:example:d6e17cab-1ee6-4c28-ac21-0c95b9a9d8b9', 'drug': 'Paracetamol', 'maxQuantity': 3, 'price': 1, 'quantity': 1}, {'prId': 'did:example:182981f5-f87e-4637-9244-8e1c534cc078', 'drug': 'Ebastina', 'maxQuantity': 4, 'price': 1, 'quantity': 1}]
    o = Order([], '0xABCD')
    o.load_prescriptions_from_json(prs)

def prescription_to_json():
    p = Prescription('12345', 3, 3, 1)
    json.dumps(p.serialize())

def test_order_to_json():
    number = 5
    prescriptions = []
    for i in range(0, number):
        p = Prescription('12345', 3, 1, 'abcd')
        p.set_quantity(3)
        prescriptions.append(p)
    order = Order(prescriptions, '0xABCD')
    json.dumps(order.serialize())


