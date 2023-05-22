import { showPopupBox } from "./popupBox.js";

window.onload = function() {
    const order = JSON.parse(rawOrder.
        replace(/&#34;/g,'"')
        .replace('"{','{').replace('}"','}')
        .replace('""','"').replace('""','"')).order

    const orderId = document.getElementById('orderId')
    let content = document.createTextNode(`Order: ${order.orderId}`)
    orderId.appendChild(content)

    const prescriptions = document.getElementById('prescriptions')
    for(let i=0; i< order.prescriptions.length; i++ ){
        const li = document.createElement("p")
        li.appendChild(document.createTextNode(order.prescriptions[i].prId))
        prescriptions.appendChild(li)
    }

    const totalPrice = document.getElementById('totalPrice')
    content = document.createTextNode(`Total Price: ${order.totalPrice}`)
    totalPrice.appendChild(content)

  };

const payButton = document.getElementById('payButton');
payButton.addEventListener('click', async () => { pay() });
async function pay(){
    // ask for order and signed order
    const order = JSON.parse(rawOrder.
                    replace(/&#34;/g,'"')
                    .replace('"{','{').replace('}"','}')
                    .replace('""','"').replace('""','"'))
    // Load web 3 instance and contract
    const web3 = new Web3(Web3.givenProvider ||  mumbaiUrl);
    const { ethereum } = window;
    var account = await ethereum.request({ method: 'eth_requestAccounts' });
    const ABI_CONTRACT =  await fetch('/static/vc4med.json').then((response) => response.json()).then((json) => json['abi']);
    const vc4med = new web3.eth.Contract(ABI_CONTRACT, '0xCD3D21d1e7f8303d2450a2954444E04a2AFB20AE')

    // pay
    try {
        web3.eth.handleRevert = true   
        const tx = await vc4med.methods.payOrder(
            order['order'], 
            order['signed_order'],
            )
        .send({from:account[0], value: order['order']['totalPrice']*1e18})
        setTimeout( () => window.location.href = `/success/${tx.transactionHash}`, 30000); // TODO: just a silly fix

    } catch (error) {
        console.log(error.reason)
        showPopupBox('alert', `Transaction failed: ${error.reason}`)
    }
}