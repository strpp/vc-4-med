# import the following dependencies
import json
from web3 import Web3
import asyncio

# add your blockchain connection information
ganache_url = 'http://192.168.1.2:8545'
web3 = Web3(Web3.HTTPProvider(ganache_url))

# uniswap address and abi
vc4med_address = '0xFFfc5E7dbf136E36E6548891051925aD8327E198'
vc4med_abi = json.loads(
    """
    [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "string",
          "name": "orderId",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "address",
          "name": "to",
          "type": "address"
        }
      ],
      "name": "orderHasBeenPayed",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "didkey",
          "type": "string"
        }
      ],
      "name": "isDoctor",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "didkey",
          "type": "string"
        }
      ],
      "name": "isPharma",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "a",
          "type": "address"
        }
      ],
      "name": "isPharma",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": true
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "didkey",
          "type": "string"
        }
      ],
      "name": "addNewDoctor",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "didkey",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "a",
          "type": "address"
        }
      ],
      "name": "addNewPharma",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "components": [
            {
              "components": [
                {
                  "internalType": "string",
                  "name": "prId",
                  "type": "string"
                },
                {
                  "internalType": "uint256",
                  "name": "quantity",
                  "type": "uint256"
                },
                {
                  "internalType": "uint256",
                  "name": "price",
                  "type": "uint256"
                }
              ],
              "internalType": "struct vc4med.Prescription[]",
              "name": "p",
              "type": "tuple[]"
            },
            {
              "internalType": "string",
              "name": "orderId",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "totalPrice",
              "type": "uint256"
            }
          ],
          "internalType": "struct vc4med.Order",
          "name": "order",
          "type": "tuple"
        },
        {
          "internalType": "bytes",
          "name": "sig",
          "type": "bytes"
        }
      ],
      "name": "payOrder",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function",
      "payable": true
    }
  ]
"""
)
contract = web3.eth.contract(address=vc4med_address, abi=vc4med_abi)


# define function to handle events and print to the console
def handle_event(event):
    print(Web3.toJSON(event))
    # and whatever


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval, order_id):
    while True:
        for orderHasBeenPayed in event_filter.get_new_entries():
            handle_event(orderHasBeenPayed, order_id)
        await asyncio.sleep(poll_interval)


# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main(order_id):
    event_filter = contract.events.orderHasBeenPayed.createFilter(fromBlock='latest')
    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, 2, order_id)))
                # log_loop(block_filter, 2),
                # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()