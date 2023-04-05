const signTypedDataV4Button = document.getElementById('sign');

signTypedDataV4Button.addEventListener('click', async function (event) {
    event.preventDefault();
  
    const msgParams = JSON.stringify({
      domain: {

        // Give a user friendly name to the specific contract you are signing for.
        name: 'vc4med',
        // Just let's you know the latest version. Definitely make sure the field name is correct.
        version: '1',
        // Defining the chain aka Rinkeby testnet or Ethereum Main Net
        chainId: 1337,
        // If name isn't enough add verifying contract to make sure you are establishing contracts with the proper entity
        verifyingContract: '0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC',
      },

          // Defining the message signing data content.
    message: {
      /*
       - Anything you want. Just a JSON Blob that encodes the data you want to send
       - No required fields
       - This is DApp Specific
       - Be as explicit as possible when building out the message schema.
      */
      orderId : '1',
      totalPrice: 1,
      prescription: [{prescriptionId:'1', quantity:1, price:1}]
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
        { name: 'orderId', type: 'string' },
        { name: 'totalPrice', type: 'uint256' },
        { name: 'prescriptions', type: 'Prescription[]'}
      ],
      // Not an EIP712Domain definition
      Prescription: [
        { name: 'prescriptionId', type: 'string' },
        { name: 'quantity', type: 'uint256' },
        { name: 'price', type: 'uint256' },
      ],
    }
  });
    
    const { ethereum } = window;
    var from = await ethereum.request({ method: 'eth_accounts' });
    const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
  
    var params = [accounts[0], msgParams];
    var method = 'eth_signTypedData_v4';
  
    ethereum.sendAsync(
      {
        method,
        params,
        from: accounts[0],
      },
      function (err, result) {
        if (err) return console.dir(err);
        if (result.error) {
          alert(result.error.message);
        }
        if (result.error) return console.error('ERROR', result);
        console.log('TYPED SIGNED:' + JSON.stringify(result.result));
      }
    );
  });