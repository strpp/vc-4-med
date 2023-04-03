const Web3 = require('web3')
const web3 = new Web3('http://localhost:8545')

const signTypedDataV4Button = document.getElementById('signedTypedDataV4Button');

signTypedDataV4Button.addEventListener('click', async function (event) {
    event.preventDefault();
  
    const msgParams = JSON.stringify({
      domain: {
        // Defining the chain aka Rinkeby testnet or Ethereum Main Net
        chainId: 1337,
        // Give a user friendly name to the specific contract you are signing for.
        name: 'vc4med',
        // If name isn't enough add verifying contract to make sure you are establishing contracts with the proper entity
        verifyingContract: '0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC',
        // Just let's you know the latest version. Definitely make sure the field name is correct.
        version: '1',
      },
  
      // Defining the message signing data content.
      message: {
        /*
         - Anything you want. Just a JSON Blob that encodes the data you want to send
         - No required fields
         - This is DApp Specific
         - Be as explicit as possible when building out the message schema.
        */
        orderId: '1',
        prescriptions: [
            {id : 'pr1', quantity : 1, price : 1},
            {id : 'pr2', quantity : 2, price : 2},
        ]
      },
      // Refers to the keys of the *types* object below.
      primaryType: 'Order',
      types: {
        // TODO: Clarify if EIP712Domain refers to the domain the contract is hosted on
        EIP712Domain: [
          { name: 'name', type: 'string' },
          { name: 'version', type: 'string' },
          { name: 'chainId', type: 'uint256' },
          { name: 'verifyingContract', type: 'address' },
        ],
        // Refer to PrimaryType
        Order: [
          { name: 'orderId', type: 'uint256' },
          { name: 'prescriptions', type: 'Prescription []' },
        ],
        // Not an EIP712Domain definition
        Prescription: [
          { name: 'id', type: 'string' },
          { name: 'quantity', type: 'uint256'},
          { name: 'price', type: 'uint256'},
        ],
      },
    });
  
    var from = await web3.eth.getAccounts();
  
    var params = [from[0], msgParams];
    var method = 'eth_signTypedData_v4';
  
    web3.currentProvider.sendAsync(
      {
        method,
        params,
        from: from[0],
      },
      function (err, result) {
        if (err) return console.dir(err);
        if (result.error) {
          alert(result.error.message);
        }
        if (result.error) return console.error('ERROR', result);
        console.log('TYPED SIGNED:' + JSON.stringify(result.result));
  
        const recovered = sigUtil.recoverTypedSignature_v4({
          data: JSON.parse(msgParams),
          sig: result.result,
        });
  
        if (
          ethUtil.toChecksumAddress(recovered) === ethUtil.toChecksumAddress(from)
        ) {
          alert('Successfully recovered signer as ' + from);
        } else {
          alert(
            'Failed to verify signer when comparing ' + result + ' to ' + from
          );
        }
      }
    );
  });