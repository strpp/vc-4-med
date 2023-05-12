var prescriptions = JSON.parse(prescriptions.replace(/&#39;/g,'"'))
//  Create form
const form = document.createElement("form");
form.setAttribute("id", "orderForm")

for(let i=0; i<prescriptions.length;i++){
  let id = prescriptions[i].prId
  let maxQuantity =  prescriptions[i].maxQuantity
  let drug = prescriptions[i].drug
  let label = document.createElement("label");
  label.setAttribute("for", id);
  label.innerHTML = `<strong>${drug}</strong> (Max quantity: ${maxQuantity})`
  let input = document.createElement("input")
  input.setAttribute("type", "number")
  input.setAttribute("min", "1")
  input.setAttribute("value", "1")
  input.setAttribute("max", maxQuantity)
  input.setAttribute("id", id)
  form.appendChild(label)
  form.appendChild(document.createElement('br'))
  form.appendChild(input)
  form.appendChild(document.createElement('br'))
  form.appendChild(document.createElement('br'))
}

const submit = document.createElement('input')
submit.className = "button"
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
      console.log(event.target.responseText)
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

  const { ethereum } = window;
  var from = await ethereum.request({ method: 'eth_requestAccounts' });

  
  let msgParams = await fetch('/static/eip712.json').then((response) => response.json()).then((json) => json);
  msgParams['message']['prescriptions'] = order['prescriptions']
  msgParams['message']['orderId'] = orderId
  msgParams['message']['totalPrice'] = order['totalPrice']
  msgParams['message']['pharmacy'] = from[0]

  var params = [from[0], JSON.stringify(msgParams)];
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
      //alert(signedOrder)
      sendSignedOrder.send(JSON.stringify({"signedOrder" : signedOrder}));
    
      sendSignedOrder.addEventListener("load", async (event)=>{
        if(event.target.status == 200) window.location.href = `/order/qr/${event.target.responseText}`;
      });
    }
  );


  return signedOrder
}