import json
from time import sleep
from web3 import Web3

class BlockchainReader():

    def __init__(self, rpc_url, contract_address):
        # add your blockchain connection information
        self.rpc_url = rpc_url
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))

        # address and abi
        abi = json.load(open('static/vc4med.json', 'r'))['abi']
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)

    def read_blocks(self, filter):
        for block in filter.get_new_entries():
            # get the block number
            block_number = block['number']

            # if the block number is greater than the latest block number, analyze the block
            if block_number > self.latest_block_number:
                # update the latest block number
                self.latest_block_number = block_number

            # retrieve the block
            block = self.web3.eth.get_block(block_number, full_transactions=True)

            # loop over the transactions in the block and check if they interacted with the contract
            for tx in block.transactions:
                # get the transaction receipt
                receipt = self.web3.eth.get_transaction_receipt(tx.hash)

                # check if the transaction interacted with the contract
                if receipt.contract_address == self.contract_address:
                    # fail
                    if(receipt.status == 0):
                        print('transaction failed')
                        for log in receipt.logs:
                            try:
                                decoded_log = self.web3.eth.abi.decode_log(log.topics, log.data, log.topics[0])
                                if decoded_log['event'] == 'Error':
                                    print(decoded_log['args']['reason'])
                            except:
                                pass
                    return False

    # create a filter for the latest block and look for the "orderHasBeenPayed" event
    # if event is found, return the hash. Else timeout error
    def read(self, condition, timeout, polling_delta):

        try:
            event_filter = self.contract.events.orderHasBeenPayed.create_filter(fromBlock='latest')
            block_filter = self.web3.eth.filter('latest')
        except:
            print('Error while creating filter')
            return False
    
        i = 0
        while(i<timeout):
            try:
                # look for events to check if transaction is ok
                read_events(event_filter, condition)

                # NOTE: I think we could avoid reading events, because when we check the transaction status we already know if
                # it was successfully completed or not. So we could just read transactions, and if true find the event in the block to
                # have a confirm.

                # read blocks to check if transaction is failed
                self.read_blocks(block_filter)

            except:
                print('Error while reading blockchain')
                break

            sleep(polling_delta)
            i+=1

        print('Timeout reached')
        return False
    
    # get events using the filter and return true if the condition is met
def read_events(filter, condition):
    events = filter.get_new_entries()
    if events:
        result = handle_event(events, condition)
        if(result):
            return result

# filter events according to condition and return transaction hash related to it
def handle_event(events, condition):
    for i in range(0, len(events)):
        orderId = events[i].args.orderId
        if orderId == condition:
            return (events[i].transactionHash).hex()
    return False
