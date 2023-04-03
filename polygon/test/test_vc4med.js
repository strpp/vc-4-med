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

it("Sign an order", async () => {
  const vc4medInstance = await vc4med.deployed();
  
  //const signerIdentity = EthCrypto.createIdentity();
  const message = EthCrypto.hash.keccak256([
  {type: "string",value: "Hello World!"}
  ]);
  //const sig = EthCrypto.sign(signerIdentity.privateKey, message);
  const sig = EthCrypto.sign('0x4d2fe803638d640d79c082c79755fbd8fb82b29350d5a287bf043868a8964d18', message);

  console.log(`message: ${message}`);
  console.log(`signature: ${sig}`);
  //console.log(`signer public key: ${signerIdentity.address}`);

  const pharma = await vc4medInstance.recoverSigner(message, sig);
  assert.equal(pharma, accounts[0], "Doctor has not been inserted correctly");
  });

});
