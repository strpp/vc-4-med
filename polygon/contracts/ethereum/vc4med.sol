// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract vc4med {
  address public owner;

  struct prescription{
    bytes32 id;
    uint quantity;
    uint price;
  }

  mapping(bytes32 => uint) alreadyRedeemedQuantity;
  mapping(string => bool) doctors;
  mapping(string => bool) pharmas;

  constructor(){
    // Set the transaction sender as the owner of the contract.
    owner = msg.sender;
    // Values for demo
    doctors['did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX']= true;
    pharmas['did:key:z6MktaAfLYZF3khaHZuWCho1vrJkDPXx1nkHtPSXFSwk6g5i']=true;
  }

  // Modifier to check that the caller is the owner of the contract.
  modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    // execute the rest of the code.
    _;
  }

  function isDoctor(string memory didkey) public view returns (bool) {
    return doctors[didkey];
  }

  function isPharma(string memory didkey) public view returns (bool) {
    return pharmas[didkey];
  }

  function addNewDoctor(string memory didkey) public onlyOwner(){
    doctors[didkey] = true;
  }

  function addNewPharma(string memory didkey) public onlyOwner(){
    pharmas[didkey] = true;
  }

  function payOrder() public payable{

  }

  function recoverSigner(bytes32 message, bytes memory sig)
   public
   pure
   returns (address)
   {
    uint8 v;
    bytes32 r;
    bytes32 s;
    (v, r, s) = splitSignature(sig);
    return ecrecover(message, v, r, s);
   }
  
  function splitSignature(bytes memory sig) public pure returns (uint8, bytes32, bytes32){
    require(sig.length == 65);
    bytes32 r;
    bytes32 s;
    uint8 v;
    assembly {
      // first 32 bytes, after the length prefix
      r := mload(add(sig, 32))
      // second 32 bytes
      s := mload(add(sig, 64))
      // final byte (first byte of the next 32 bytes)
      v := byte(0, mload(add(sig, 96)))
    }
    return (v, r, s);
   }


}
