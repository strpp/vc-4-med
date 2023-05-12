from model.blockchain_payer import blockchainPayer
from dotenv import load_dotenv
import os

load_dotenv()

# NOTE : this test costs gas
"""
def test_pay_refund():
    bp = blockchainPayer(
        os.getenv('MUMBAI_URL'),
        80001,
        os.getenv('INSURANCE_PUBLIC_KEY'),
        os.getenv('INSURANCE_PRIVATE_KEY')
    )

    tx = bp.send_eth(0.1, '0x2e3D6752536566ED51c805A86070BA596052FCb6')
    assert tx != False

    tx = bp.send_eth(10, '0x2e3D6752536566ED51c805A86070BA596052FCb6')
    assert tx == False
"""

