const vc4med = artifacts.require("./Example.sol");

const Web3 = require('web3')
const EthCrypto = require('eth-crypto');
const web3 = new Web3('http://localhost:8545')

contract("Example of Message Signatures", accounts => {


  it("Sign a message", async () => {
    const c = await vc4med.deployed();
    const sig = '0x459143d4c5ffa5aea5962a5e1978a7326437004c145380a8b71f85a6d523597155e410c4a9010fcc4c080d678ccf005f22b4f0c6eae29600ca4a860c9667f5721c'
    const hash = await c.test(sig);
    assert.equal(hash, '0xB2Bd4fF4068214274692595847BF562FFAb9b10e', "Signer is wrong")    
  });



});
