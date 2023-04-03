const signTypedDataV4Button = document.getElementById('a');

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
      contents: 'Hello, Bob!',
      attachedMoneyInEth: 4.2,
      from: {
        name: 'Cow',
        wallets: [
          '0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826',
          '0xDeaDbeefdEAdbeefdEadbEEFdeadbeEFdEaDbeeF',
        ],
      },
      to: [
        {
          name: 'Bob',
          wallets: [
            '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB',
            '0xB0BdaBea57B0BDABeA57b0bdABEA57b0BDabEa57',
            '0xB0B0b0b0b0b0B000000000000000000000000000',
          ],
        },
      ],
    },
    // Refers to the keys of the *types* object below.
    primaryType: 'Mail',
    types: {
      // TODO: Clarify if EIP712Domain refers to the domain the contract is hosted on
      EIP712Domain: [
        { name: 'name', type: 'string' },
        { name: 'version', type: 'string' },
        { name: 'chainId', type: 'uint256' },
        { name: 'verifyingContract', type: 'address' },
      ],
      // Not an EIP712Domain definition
      Group: [
        { name: 'name', type: 'string' },
        { name: 'members', type: 'Person[]' },
      ],
      // Refer to PrimaryType
      Mail: [
        { name: 'from', type: 'Person' },
        { name: 'to', type: 'Person[]' },
        { name: 'contents', type: 'string' },
      ],
      // Not an EIP712Domain definition
      Person: [
        { name: 'name', type: 'string' },
        { name: 'wallets', type: 'address[]' },
      ],
    },
    
    /*

        orderId: '1',
        prescriptions: [
            {id : 'pr1', quantity : 1, price : 1},
            {id : 'pr2', quantity : 2, price : 2},
        ]
      },
      primaryType: 'Order',
      types: {
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
      */
    });
    
    const { ethereum } = window;
    var from = await ethereum.request({ method: 'eth_accounts' });
    const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
    console.log(accounts[0])
  
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

        console.log(msgParams)
      }
    );
  });