from web3 import Web3

class blockchainPayer:

    # add your blockchain connection information
    def __init__(self, rpc, chain_id, public_key, private_key):
       self. web3 = Web3(Web3.HTTPProvider(rpc))
       self.chain_id = chain_id
       self.public_key = public_key
       self.private_key = private_key

    
    def send_eth(self, amount, to):
        #get the nonce.  Prevents one from sending the transaction twice
        nonce = self.web3.eth.get_transaction_count(self.public_key, 'pending')

        #build a transaction in a dictionary
        tx = {
            'nonce': nonce,
            'to': to,
            'value': self.web3.to_wei(amount, 'ether'),
            'gas': 2000000,
            'gasPrice': self.web3.to_wei('50', 'gwei'),
            'chainId' : self.chain_id
        }

        #sign the transaction
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)

        #send transaction
        try:
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        except Exception as e:
            print(e)
            return False

        #get transaction hash
        return ( self.web3.to_hex(tx_hash) )