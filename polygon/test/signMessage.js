const vc4med = artifacts.require("./Example.sol");

const Web3 = require('web3')
const EthCrypto = require('eth-crypto');
const web3 = new Web3('http://localhost:8545')

contract("Example of Message Signatures", accounts => {


  it("Verify a metamask signed message", async () => {
    const c = await vc4med.deployed();
    const order = {
      p: [{
         name: "Cow",
         quantity: 1,
         price: 1
      },{
        name: "Abc",
        quantity: 2,
        price: 1
     }],
      orderId: "Hello, Bob!",
      totalPrice: 1
  }
    const sig = '0xcc302d3d35fda279b96665c3afd99c721c1bef30f6c6d713670e59a9267f9079016513c43ea8512685184898a6086b91b72e1442c0d6bee50761bfe7960826111c'
    const hash = await c.test(order,sig);
    assert.equal(hash, '0xB2Bd4fF4068214274692595847BF562FFAb9b10e', "Signer is wrong")    
  });



});
