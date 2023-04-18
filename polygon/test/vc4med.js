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
         price: 22
      }],
      orderId: "62097173a4b04ce8824a8b8781a353ed",
      totalPrice: 22,
      pharmacy:"0x2e3D6752536566ED51c805A86070BA596052FCb6",
    }
    const sig = '0x48862b4944d0d276b252b1557754ebf21917972d8c396c7758818d2f8e44d2e8719fa1c88663d25656de844c7096a54b12bce76f4d0e621056fe2d4409478d8c1b'
    const hash = await c.payOrder(order,sig,{from: accounts[3], value: order["totalPrice"]*1e18});
    //console.log(hash.tx)
  });


});
