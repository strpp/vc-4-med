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
    try{
        const tx = await vc4med.methods.payOrder(
            order['order'], 
            order['signed_order'],
            )
            .send({from:account[0], value: order['order']['totalPrice']*1e18});
        //alert(`Payment successfully executed with TX /${tx.transactionHash}`)
        window.location.href = `/success/${tx.transactionHash}`;
    }catch(e){
        const errorJson = e.message.substring(e.message.indexOf('{'), e.message.lastIndexOf("'"))
        const tx = JSON.parse(errorJson)['value']['data']['data']
        const txNumber = Object.keys(tx)[0];
        const error = tx[txNumber]['reason']
        alert(`ERROR: ${error}`)
    }
}