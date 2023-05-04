from model.prescription import Prescription
from model.order import Order
import json

def test_create_new_order():
    number = 5
    prescriptions = []
    for i in range(0, number):
        prescriptions.append(
            Prescription('12345', 3, 3, 1)
        )
    order = Order(prescriptions, '0xABCD')
    assert order.totalPrice == 15

def prescription_to_json():
    p = Prescription('12345', 3, 3, 1)
    json.dumps(p.serialize())

def test_order_to_json():
    number = 5
    prescriptions = []
    for i in range(0, number):
        prescriptions.append(
            Prescription('12345', 3, 3, 1)
        )
    order = Order(prescriptions, '0xABCD')
    json.dumps(order.serialize())
