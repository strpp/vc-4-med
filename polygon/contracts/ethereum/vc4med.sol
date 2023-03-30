// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract vc4med {
  address public owner;
  mapping(string => bool) doctors;
  mapping(string => bool) pharmas;

  constructor(){
    // Set the transaction sender as the owner of the contract.
    owner = msg.sender;
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
}
