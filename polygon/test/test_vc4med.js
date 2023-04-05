const vc4med = artifacts.require("./vc4med.sol");

const Web3 = require('web3')
const EthCrypto = require('eth-crypto');
const web3 = new Web3('http://localhost:8545')

contract("Vc4Med", accounts => {
  it("Add a new doctor", async () => {
    const vc4medInstance = await vc4med.deployed();

    let tx = await vc4medInstance.isDoctor("did:key:123456789")
    assert.equal(tx, false, "Doctor already on the list");

    await vc4medInstance.addNewDoctor("did:key:123456789", { from: accounts[0] });
    tx = await vc4medInstance.isDoctor("did:key:123456789")
    assert.equal(tx, true, "Doctor has not been inserted correctly");

  });

  it("Create an order", async () => {
    const vc4medInstance = await vc4med.deployed();
    const order = {orderId:"1",totalPrice:1,prescription:[{prescriptionId:"1",quantity:1,price:1}]}
  
    let ids = []; let quantities = []; let prices = [];
    for(let i=0; i<order.prescription.length; i++){
      ids.push(order.prescription[i].prescriptionId)
      quantities.push(order.prescription[i].quantity)
      prices.push(order.prescription[i].price)
    }
    const hash = await vc4medInstance.createOrder(
      order.orderId,
      order.totalPrice,
      ids,
      quantities,
      prices
    )
  });

  it("Verify an order", async () => {
    const vc4medInstance = await vc4med.deployed();
    const order = {orderId:"1",totalPrice:1,prescription:[{prescriptionId:"1",quantity:1,price:1}]}
    const signedOrder = "0xee09d0a12972065e6afce54864ff48dc5d2f222f5e1168c1a603ae78c8e760b96d55fa29b94292aec5ff9a6ff1c69d4d3e3e8b904c6aa6498f8d562845bc656e1c"
    
    let ids = []; let quantities = []; let prices = [];
    for(let i=0; i<order.prescription.length; i++){
      ids.push(order.prescription[i].prescriptionId)
      quantities.push(order.prescription[i].quantity)
      prices.push(order.prescription[i].price)
    }
    const hash = await vc4medInstance.payOrder(
      order.orderId,
      order.totalPrice,
      ids,
      quantities,
      prices,
      signedOrder
    )
    const signer = '0xB2Bd4fF4068214274692595847BF562FFAb9b10e'
    assert.equal(hash, signer, "Wrong signer");

  });
});
