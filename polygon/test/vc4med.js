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
      p: [{
         prId: "Cow",
         quantity: 1,
         price: 1
      },{
        prId: "Abc",
        quantity: 2,
        price: 1
     }],
      orderId: "Hello, Bob!",
      totalPrice: 1
    }
    const sig = '0x0ab5b96ae2b121d12ea862b0ac5afa80c1c7db9584f8e795e2c3cc6a0c248eb74334e04c346271b2830552b974412cda35411dae900c6a457fa4289227a8cac61c'
    const hash = await c.payOrder(order,sig,{from: accounts[3], value: order["totalPrice"]*1e18});
    //console.log(hash.tx)
  });


});
