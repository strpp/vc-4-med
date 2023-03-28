from web3 import Web3
from time import sleep

#w3 = Web3(Web3.EthereumTesterProvider())
#myContract = w3.eth.contract(address=contract_address, abi=contract_abi)


async def pay_order(prescription_id, quantity, pharmacy):
    #tx = await myContract.functions.pay(prescription_id, quantity, pharmacy)
    sleep(5)
    tx = "0xeef10fc5170f669b86c4cd0444882a96087221325f8bf2f55d6188633aa7be7c"
    return tx