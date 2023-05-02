import os
import json
from web3 import Web3
from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount

load_dotenv()
MUMBAI_URL = os.getenv('MUMBAI_URL')
REGISTRY_ADDRESS = '0xdCa7EF03e98e0DC2B855bE647C39ABe984fcF21B'
w3 = Web3(Web3.HTTPProvider(MUMBAI_URL))
private_key = os.getenv('DOCTOR_PRIVATE_KEY')
account: LocalAccount = Account.from_key(private_key)

# address and abi
abi = json.load(open('static/EthereumDIDRegistry.json', 'r'))['abi']
registry = w3.eth.contract(address=REGISTRY_ADDRESS, abi=abi)

async def add_delegate(identity, delegate_type, delegate, validity):
    nonce = w3.eth.get_transaction_count(account.address) 

    txn = registry.functions.addDelegate(
        identity,
        bytes.fromhex((bytes(delegate_type, 'utf-8')).hex().zfill(64)),
        delegate,
        validity
        ).build_transaction({
            'chainId': 80001,
            'gas':  16000000,
            'maxFeePerGas': w3.to_wei('2', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('1', 'gwei'),
            'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return signed_txn

async def valid_delegate(identity, delegate_type, delegate):
    txn = registry.functions.validDelegate(
        identity,
        bytes.fromhex((bytes(delegate_type, 'utf-8')).hex().zfill(64)),
        delegate
    ).call()
    return txn

async def identity_owner(identity):
    txn = registry.functions.identityOwner(identity).call()
    return txn

async def is_doctor(doctor):
    is_valid = await valid_delegate('0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2', 'DID-JWT', doctor)
    if(is_valid):
        return True
    
    owner = await identity_owner(doctor)
    if( owner == '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2'):
        return True

    return False