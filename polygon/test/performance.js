const vc4med = artifacts.require("./vc4med.sol");
const Web3 = require('web3');
const web3 = new Web3('http://localhost:8545');

contract("Performance", (accounts) => {

  let contract;

  before(async ()=>{
    contract = await vc4med.deployed();
  });
  
  it("Add 100 doctor", async()=>{
    let gas = 0;
    let doctor;
    for(let i=0; i<100; i++){
        doctor = `did:key:${(Math.random() + 1).toString(36).substring(48)}`;
        let tx = await contract.addNewDoctor(doctor);
        gas += tx.receipt.gasUsed;
    }
    console.log(gas);
    let result = await contract.isDoctor(doctor)
    assert.equal(result, true, "Error: Is not a doctor");
  });

  it("Add 100 pharma", async()=>{
    let gas = 0;
    for(let i=0; i<100; i++){
        let pharmaKey = `did:key:${(Math.random() + 1).toString(36).substring(48)}`;
        let pharmaAddr = accounts[i]
        let tx = await contract.addNewPharma(pharmaKey, pharmaAddr);
        gas += tx.receipt.gasUsed;
    }
    console.log(gas);
    let result = await contract.isPharma(accounts[2])
    assert.equal(result, true, "Error: Is not a pharma");
  });

  it("Pay order", async()=>{
    let gas = 0;
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
    for(let i=0; i<1; i++){
        const tx = await contract.payOrder(order,sig,{from: accounts[3], value: order["totalPrice"]*1e18});
        gas += tx.receipt.gasUsed;
    }
    console.log(gas);
  });  
     
});