# python -m pytest tests/
from model.db_connector import dbConnector
from model.refund import Refund
import uuid

id = str(uuid.uuid4())
MODE = 'test'
MODE = 'insurance'

def test_save_refund():
    dbc = dbConnector(MODE)
    refund = Refund(id, [{'a':1, 'b':2}], '0x2FFd2e8c5065b65159392cCDf9f358e339833f1A')
    dbc.save(refund)

    dbc = dbConnector(MODE)
    refund = Refund(str(uuid.uuid4()), [{'a':1, 'b':2}], '0x2FFd2e8c5065b65159392cCDf9f358e339833f1A')
    dbc.save(refund)

    r = dbc.getRefund(id)
    assert r.emitted == False


def test_get_refund():
    dbc = dbConnector(MODE)
    r = dbc.getRefundNotEmitted(id)
    assert r._id == id

    r = dbc.getRefund(id)
    assert r._id == id


def test_update_refund():
    dbc = dbConnector(MODE)
    r = dbc.getRefundNotEmitted(id)
    r.change_to_emitted('12345')
    dbc.update(r)

    r = dbc.getRefund(id)
    assert r.emitted == True

def test_get_all_refunds():
    dbc = dbConnector(MODE)
    r = dbc.getAllRefund()

def test_get_all_refunds_emitted():
    dbc = dbConnector(MODE)
    r = dbc.getAllRefundFilterEmitted(True)
    assert len(r) > 0

    dbc = dbConnector(MODE)
    r = dbc.getAllRefundFilterEmitted(False)
    #assert len(r) == 2