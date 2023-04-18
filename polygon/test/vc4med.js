const vc4med = artifacts.require("./vc4med.sol");
const Web3 = require('web3');
const web3 = new Web3(Web3.givenProvider || "ws://localhost:8545");

contract("Vc4Med", accounts => {
  it("Add a new doctor", async () => {
    const vc4medInstance = await vc4med.deployed();

    let tx = await vc4medInstance.isDoctor("did:key:123456789")
    assert.equal(tx, false, "Doctor already on the list");

    await vc4medInstance.addNewDoctor("did:key:123456789", { from: accounts[0] });
    tx = await vc4medInstance.isDoctor("did:key:123456789")
    assert.equal(tx, true, "Doctor has not been inserted correctly");

  });

  it("Pay an order", async () => {
    const c = await vc4med.deployed();
    const order = {
      prescriptions: [{
         prId: "did:example:5c6562f2aecf4179beb7833e4cde6396",
         quantity: 1,
         maxQuantity: 2,
         price: 22
      }],
      orderId: "62097173a4b04ce8824a8b8781a353ed",
      totalPrice: 22,
      pharmacy:"0x2e3D6752536566ED51c805A86070BA596052FCb6",
    }
    const sig = '0x48862b4944d0d276b252b1557754ebf21917972d8c396c7758818d2f8e44d2e8719fa1c88663d25656de844c7096a54b12bce76f4d0e621056fe2d4409478d8c1b'
    await c.payOrder(order,sig,{from: accounts[3], value: order["totalPrice"]*1e18});

    let result = await c.getOrder(order['orderId'])
    assert.equal(result, true, "Order not delivered correctly");
    
    const secondOrder = {
      prescriptions : [
        {prId: "did:example:797a54d456bd4f6894358853ec2fb5f0", quantity:1, maxQuantity:4, price:9},
        {prId: "did:example:0ac02b59abe94b2485735818e4569c4e", quantity:1, maxQuantity:2, price:19},
        {prId: "did:example:0e9fe0b47d95454a823f174e42595087", quantity:1, maxQuantity: 1,  price: 21},
      ],
      orderId: "b210aa7583ce4b91a2dfb42752e0d522",
      totalPrice: 49,
      pharmacy:"0x2e3D6752536566ED51c805A86070BA596052FCb6"
    }
    const secondSig = "0xddb52058192c7b0958c8bde5aa817ec3e292d1c7c89983b772b385bca725350f0ce13f8c86a6d14826e592d5c1ba5222f15b566b09770ff38020feaaabe439c31c"
    await c.payOrder(secondOrder,secondSig,{from: accounts[8], value: secondOrder["totalPrice"]*1e18});

    result = await c.getOrder(secondOrder['orderId'])
    assert.equal(result, true, "Order not delivered correctly");
});

});
