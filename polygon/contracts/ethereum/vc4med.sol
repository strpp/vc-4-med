// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract vc4med {

  struct EIP712Domain {
    string  name;
    string  version;
    uint256 chainId;
    address verifyingContract;
  }

  struct Prescription{
    string prescriptionId;
    uint quantity;
    uint price;
  }

  struct Order{
    string orderId;
    uint totalPrice;
    Prescription [] prescriptions;
  }

  address public owner;

  bytes32 constant EIP712DOMAIN_TYPEHASH = keccak256(
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
  );

  bytes32 constant PRESCRIPTION_TYPEHASH = keccak256(
   "Prescription(string prescriptionId,uint256 quantity,uint256 price)"
  );

  bytes32 constant ORDER_TYPEHASH = keccak256(
    "Order(string orderId,uint256 totalPrice,Prescription[] prescriptions)Prescription(string prescriptionId,uint256 quantity,uint256 price)"
  );

  bytes32 DOMAIN_SEPARATOR;

  mapping(bytes32 => uint) alreadyRedeemedQuantity;
  mapping(string => bool) doctors;
  mapping(string => bool) pharmas;

  constructor(){
    // Set the transaction sender as the owner of the contract.
    owner = msg.sender;
    // Values for demo
    doctors['did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX']= true;
    pharmas['did:key:z6MktaAfLYZF3khaHZuWCho1vrJkDPXx1nkHtPSXFSwk6g5i']=true;
    //EIP 712
    DOMAIN_SEPARATOR = hash(EIP712Domain({
      name: "vc4med",
      version: '1',
      chainId: 1337,
      // verifyingContract: this
      verifyingContract: 0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC
    }));
  }

  event Print(string toPrint);

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

  function hash(EIP712Domain memory eip712Domain) public pure returns (bytes32) {
    return keccak256(abi.encode(
      EIP712DOMAIN_TYPEHASH,
      keccak256(bytes(eip712Domain.name)),
      keccak256(bytes(eip712Domain.version)),
      eip712Domain.chainId,
      eip712Domain.verifyingContract
      ));
  }

  function hash(Order memory order) public pure returns (bytes32) {
    return keccak256(abi.encode(
      ORDER_TYPEHASH,
      keccak256(bytes(order.orderId)),
      order.totalPrice,
      hash(order.prescriptions)
    ));
  }

  function hash(Prescription memory p) public pure returns (bytes32) {
    return keccak256(abi.encode(
      PRESCRIPTION_TYPEHASH,
      keccak256(bytes(p.prescriptionId)),
      p.quantity,
      p.price
    ));
  }

  function hash(Prescription [] memory ps) public pure returns(bytes32){
    bytes32 [] memory keccakValues = new bytes32[](ps.length);
    for(uint i =0; i<ps.length; i++){
      keccakValues[i] = hash(ps[i]);
    }
    return keccak256(abi.encode(keccakValues));
  }

  function verifyOrder(Order memory order, bytes memory sig) public view returns (address) {
    bytes32 r; bytes32 s; uint8 v;
    assembly {
      r := mload(add(sig, 32))
      s := mload(add(sig, 64))
      v := and(mload(add(sig, 65)), 255)
    }
    if (v < 27) v += 27;
    
    bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, hash(order)));
    return ecrecover(digest, v, r, s);
  }

  function createOrder(string memory orderId, uint totalPrice, string[] memory ids, uint[] memory quantities, uint[] memory prices) 
    public pure returns(Order memory){
  
    Prescription [] memory prs = new Prescription[](ids.length);
    for(uint i=0; i<prs.length; i++){
      prs[i] = Prescription(ids[i], quantities[i], prices[i]);
    }
    
    return Order(orderId, totalPrice, prs);
  }

  function payOrder(string memory orderId, uint totalPrice, string[] memory ids, uint[] memory quantities, uint[] memory prices, bytes memory sig)
    public view returns(address){
    
    Order memory o = createOrder(orderId, totalPrice, ids, quantities, prices);
    return verifyOrder(o, sig);
    }



}
