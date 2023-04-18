import os
import json
import asyncio
from time import sleep
from hexbytes import HexBytes
from web3 import Web3

# add your blockchain connection information
#ganache_url = 'http://localhost:8545'
MUMBAI_URL = os.getenv('MUMBAI_URL')
VC_4_MED_ADDRESS = os.getenv('VC_4_MED_ADDRESS')
web3 = Web3(Web3.HTTPProvider(MUMBAI_URL))

# address and abi
abi = json.load(open('static/vc4med.json', 'r'))['abi']
contract = web3.eth.contract(address=VC_4_MED_ADDRESS, abi=abi)

# filter events according to condition and return transaction hash related to it
def handle_event(events, condition):
    for i in range(0, len(events)):
        recv = events[i].args._to
        if recv == condition:
            return (events[i].transactionHash).hex()
    return False


# create a filter for the latest block and look for the "orderHasBeenPayed" event
# if event is found, return the hash. Else timeout error
TIMEOUT = 500
POLLING_INTERVAL = 2
def main(condition):
    event_filter = contract.events.Transfer.create_filter(fromBlock='latest')
    i = 0
    while(i<TIMEOUT):
        events = event_filter.get_new_entries()
        if events:
            result = handle_event(events, condition)
            if(result):
                return result
        i+=1
        sleep(POLLING_INTERVAL)
    return False

if __name__ == "__main__":
    main()