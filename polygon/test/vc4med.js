const vc4med = artifacts.require("./vc4med.sol");

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
         price: 14
      },{
        prId: "did:example:797a54d456bd4f6894358853ec2fb5f0",
        quantity: 1,
        maxQuantity: 4,
        price: 38
     }],
      orderId: "38de0ac738614f729d57c7904bda5735",
      totalPrice: 52
    }
    const sig = '0x09a711da4d5d6c0d23a1fa979a4120321567a39f6b2c3d501c30a37d969df4882c3ae3041abe4269d32e1e78aea576c8fe4a470fb2accc7be36bcae15f3c5d8b1c'
    const hash = await c.payOrder(order,sig,{from: accounts[3], value: order["totalPrice"]*1e18});
    //console.log(hash.tx)
  });


});
