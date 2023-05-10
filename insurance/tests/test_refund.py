from model.refund import Refund
import json

def test_create_refund():
  prescriptions = [{
    "prId": "did:example:3c461c2d-81c6-4075-b036-3cae383ca236",
    "quantity": 1,
    "maxQuantity": 3,
    "price": 1,
    "drug" : 'A'
  }]
  r = Refund('abcde', prescriptions, '0xA')
  assert r._id == 'abcde'

def test_compute_refund_amount():
  prescriptions = [{
    "prId": "did:example:3c461c2d-81c6-4075-b036-3cae383ca236",
    "quantity": 1,
    "maxQuantity": 3,
    "price": 1,
    "drug" : 'A'
  }]
  r = Refund('abcde', prescriptions, '0xA')
  r.compute_amount()
  assert r.refund_amount == 1
