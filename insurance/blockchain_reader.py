import os
import json
import asyncio
from time import sleep
from hexbytes import HexBytes
from web3 import Web3

# add your blockchain connection information
MUMBAI_URL = os.getenv('MUMBAI_URL')
web3 = Web3(Web3.HTTPProvider(MUMBAI_URL))
VC_4_MED_ADDRESS = os.getenv('VC_4_MED_ADDRESS')
POLYGON_SCAN_KEY = os.getenv('POLYGON_SCAN_KEY')
abi_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={VC_4_MED_ADDRESS}&apikey={POLYGON_SCAN_KEY}"
# address and abi
abi = json.load(open('static/vc4med.json', 'r'))['abi']
contract = web3.eth.contract(address=VC_4_MED_ADDRESS, abi=abi)

def decode(tx_hash):
    try:
        tx = web3.eth.get_transaction(tx_hash)
        func_obj, func_params = contract.decode_function_input(tx["input"])
    except Exception as e:
        print(e)
    return func_params

if __name__ == "__main__":
    decode()