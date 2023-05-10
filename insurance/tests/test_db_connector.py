from model.db_connector import dbConnector
from model.refund import Refund
from time import sleep


def test_save_refund():
    dbc = dbConnector()
    refund = Refund('1', [{'a':1, 'b':2}], '0x1')
    dbc.save(refund)

    r = dbc.getRefund('1')
    assert r.emitted == False


def test_get_refund():
    order_id = "1"
    dbc = dbConnector()
    r = dbc.getRefundNotEmitted(order_id)
    assert r._id == '1'


    order_id = "1"
    r = dbc.getRefund(order_id)
    assert r._id == '1'


def test_update_refund():
    dbc = dbConnector()
    r = dbc.getRefundNotEmitted('1')
    r.change_to_emitted('12345')
    dbc.update(r)

    r = dbc.getRefund('1')
    assert r.emitted == True
