import json
from web3 import Web3


class Registry():

    def __init__(self, rpc_url, registry_address, doctor, pharmacy):
        self.doctor = doctor
        self.pharmacy = pharmacy

        # load smart contract instance
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        abi = json.load(open('static/EthereumDIDRegistry.json', 'r'))['abi']
        self.contract = w3.eth.contract(address=registry_address, abi=abi)


    async def valid_delegate(self, identity, delegate_type, delegate):
        txn = self.contract.functions.validDelegate(
            identity,
            bytes.fromhex((bytes(delegate_type, 'utf-8')).hex().zfill(64)),
            delegate
        ).call()
        return txn

    async def identity_owner(self, identity):
        txn = self.contract.functions.identityOwner(identity).call()
        return txn

    async def is_doctor(self, doctor):
        is_valid = await self.valid_delegate(self.doctor, 'DID-JWT', doctor)
        if(is_valid):
            return True
    
        owner = await self.identity_owner(doctor)
        if( owner == self.doctor):
            return True

        return False
    
    async def is_pharmacy(self, pharmacy):
        is_valid = await self.valid_delegate(self.pharmacy, 'DID-JWT', pharmacy)
        if(is_valid):
            return True
    
        owner = await self.identity_owner(pharmacy)
        if( owner == self.pharmacy):
            return True

        return False