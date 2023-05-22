import json
from time import sleep
from web3 import Web3
from web3.middleware import geth_poa_middleware

class BlockchainReader():

    def __init__(self, rpc_url, contract_address):
        # add your blockchain connection information
        self.rpc_url = rpc_url
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0) # needed in PoA chain like Mumbai

        # address and abi
        abi = json.load(open('static/vc4med.json', 'r'))['abi']
        self.contract_address = contract_address
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
        self.latest_block = self.web3.eth.block_number

    def get_tx_error(self, tx_hash):
        tx = self.web3.eth.get_transaction(tx_hash)
        try:
            tx = {
                'blockHash': tx['blockHash'].hex(),
                'blockNumber': tx['blockNumber'],
                'hash': tx['hash'].hex(),
                'accessList': tx['accessList'],
                'chainId': tx['chainId'],
                'from': tx['from'],
                'gas': tx['gas'],
                'gasPrice': tx['gasPrice'],
                'input': tx['input'],
                'nonce': tx['nonce'],
                'r': tx['r'].hex(),
                's': tx['s'].hex(),
                'to': tx['to'],
                'transactionIndex': tx['transactionIndex'],
                'type': tx['type'],
                'v': tx['v'],
                'value': tx['value']
            }   

            result = self.web3.eth.call(tx, tx['blockNumber'])

        except Exception as e:
            return e

    def read_blocks(self, order_id):
        try:
            current_block = self.web3.eth.block_number
            print(current_block)
        except Exception as e:
            print('Error while reading block')
            print(e)
            return False

        print(self.latest_block, current_block)
        if current_block > self.latest_block:
            block_range = range(self.latest_block, current_block+1)  # Get the range of new blocks
            print(block_range)

        for block_number in block_range:
            print(block_number)
            try:
                block = self.web3.eth.get_block(block_number)
                transactions = block['transactions']
            except Exception as e:
                print(f'error while reading block #{block_number}')
                print(e)
            
            self.latest_block = current_block  # Update the latest_block to the current_block       

            for tx_hash in transactions:
                transaction = self.web3.eth.get_transaction(tx_hash)
                try:
                    if transaction['to'] == self.contract_address:
                        print(tx_hash.hex())
                        return self.handle_transaction(transaction, order_id)
                except Exception as e:
                    pass

    def handle_transaction(self, transaction, order_id):
        # Decode the transaction input using the contract's ABI
        decoded_input = self.contract.decode_function_input(transaction['input'])

        # Extract the function name and parameters
        function_name = decoded_input[0]
        parameters = decoded_input[1:]
        print(parameters[0])
        current_order_id = parameters[0]['order']['orderId']

        print("New transaction:")
        print("  Transaction Hash:", transaction['hash'].hex())
        print("  From:", transaction['from'])
        print("  To:", transaction['to'])
        print("  Function Name:", function_name)
        print("  Parameters:", parameters)
        print("  OrderId:", current_order_id)

        print(current_order_id, order_id)
        if(current_order_id != order_id):
            return

        receipt = self.web3.eth.get_transaction_receipt(transaction['hash'].hex())
        print(receipt)

        if(receipt["status"]==1):
            return True, transaction['hash'].hex()
        else:
            error = self.get_tx_error(transaction['hash'].hex())
            print(error)
            return False, error


    # create a filter for the latest block and look for the "orderHasBeenPayed" event
    # if event is found, return the hash. Else timeout error
    def read(self, order_id, timeout, polling_delta):

        i = 0
        while(i<timeout):
            try:
                result = self.read_blocks(order_id)
                if(result != None):
                    return result[0], result[1]

            except Exception as e:
                print(e)
                print('Error while reading blockchain')
                break
            

            sleep(polling_delta)
            print(i)
            i+=1

        print('Timeout reached')
        return False, 'Timeout'
    
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
