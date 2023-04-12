var vcs = JSON.parse(vcs.replace(/&#39;/g,'"')).vcs

//  Create form
const form = document.createElement("form");
form.setAttribute("id", "orderForm")

for(let i=0; i<vcs.length;i++){
  let drug = vcs[i].credentialSubject.prescription.drug
  let dosage =  vcs[i].credentialSubject.prescription.dosage
  let label = document.createElement("label");
  label.setAttribute("for", drug);
  label.innerHTML = `<strong>${drug}</strong> (Max quantity: ${dosage})`
  let input = document.createElement("input")
  input.setAttribute("type", "number")
  input.setAttribute("min", "1")
  input.setAttribute("value", "1")
  input.setAttribute("max",dosage)
  input.setAttribute("id", drug)
  form.appendChild(label)
  form.appendChild(document.createElement('br'))
  form.appendChild(input)
  form.appendChild(document.createElement('br'))
  form.appendChild(document.createElement('br'))
}

const submit = document.createElement('input')
submit.setAttribute('type', 'submit')
submit.setAttribute('value', 'Create order')
form.appendChild(submit)
document.getElementById('order').appendChild(form)

window.addEventListener("load", () => {
  function sendData() {
    const XHR = new XMLHttpRequest();

    // Fill the FormData object
    const form = document.getElementsByTagName('input')
    var data = new FormData();
    for (const f of form) {
      data.append(f.id, f.value)
    }
    data.append("stream_id", streamId)

    // Define what happens on successful data submission
    XHR.addEventListener("load", async (event) => {
      const order = JSON.parse(event.target.responseText)
      const orderId = order['orderId']
      await signOrder(order);
    });

    // Define what happens in case of error
    XHR.addEventListener("error", (event) => {
      alert('Oops! Something went wrong.');
    });

    // Set up our request
    XHR.open("POST", `http://192.168.1.20:5001/order/${data.get("stream_id")}`);

    // The data sent is what the user provided in the form
    XHR.send(data);

  }

  // Add 'submit' event handler
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendData();
  });
});

async function signOrder(order){

  let signedOrder;
  const orderId = order['orderId']

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
      prescriptions : order['prescriptions'],
      orderId: order['orderId'],
      totalPrice: order['totalPrice']
    
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
        { name: 'prescriptions', type: 'Prescription[]' },
        { name: 'orderId', type: 'string' },
        { name: 'totalPrice', type: 'uint256' },
      ],
      // Not an EIP712Domain definition
      Prescription: [
        { name: 'prId', type: 'string' },
        { name: 'quantity', type: 'uint256' },
        { name: 'maxQuantity', type: 'uint256' },
        { name: 'price', type: 'uint256' },
      ],
    },
  });

  const { ethereum } = window;
  var from = await ethereum.request({ method: 'eth_requestAccounts' });

  var params = [from[0], msgParams];
  var method = 'eth_signTypedData_v4';

  ethereum.sendAsync(
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
      signedOrder = JSON.stringify(result.result)
      console.log('TYPED SIGNED:' + signedOrder);

      const sendSignedOrder = new XMLHttpRequest()

      sendSignedOrder.open("POST", `http://192.168.1.20:5001/order/sign/${orderId}`);
      sendSignedOrder.setRequestHeader("Content-Type", "application/json");
      sendSignedOrder.send(JSON.stringify({"signedOrder" : signedOrder}));
    
      sendSignedOrder.addEventListener("load", async (event)=>{
        if(event.target.status == 200) window.location.href = `http://192.168.1.20:5001/order/qr/${event.target.responseText}`;
      });
    }
  );


  return signedOrder
}