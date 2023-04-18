// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract vc4med {

  /* EIP 712 */
  struct EIP712Domain {
    string  name;
    string  version;
    uint256 chainId;
    address verifyingContract;
  }

  struct Prescription {
    string prId;
    uint256 quantity;
    uint256 maxQuantity;
    uint256 price;
  }

  struct Order {
    Prescription[] prescriptions;
    string orderId;
    uint256 totalPrice;
    address pharmacy;
  }

  bytes32 constant EIP712DOMAIN_TYPEHASH = keccak256(
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
  );

  bytes32 constant PRESCRIPTION_TYPEHASH = keccak256(
    "Prescription(string prId,uint256 quantity,uint256 maxQuantity,uint256 price)"
  );

  bytes32 constant ORDER_TYPEHASH = keccak256(
    "Order(Prescription[] prescriptions,string orderId,uint256 totalPrice,address pharmacy)Prescription(string prId,uint256 quantity,uint256 maxQuantity,uint256 price)"
  );

  bytes32 DOMAIN_SEPARATOR;

  /* GLOBAL VARS */
  mapping(string => uint) alreadyRedeemedQuantity;
  mapping(string => bool) orders;
  mapping(string => bool) doctorsKey;
  mapping(string => bool) pharmasKey;
  mapping(address=> bool) pharmasAddr;

  address public owner;

  event orderHasBeenPayed(string orderId, uint256 value, address to);

  constructor(){
    // Set the transaction sender as the owner of the contract.
    owner = msg.sender;

    // Values for demo
    doctorsKey['did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX']= true;
    pharmasKey['did:key:z6MktaAfLYZF3khaHZuWCho1vrJkDPXx1nkHtPSXFSwk6g5i']=true;
    pharmasAddr[0x2e3D6752536566ED51c805A86070BA596052FCb6]=true;

    //EIP 712
    DOMAIN_SEPARATOR = hash(EIP712Domain({
      name: "vc4med",
      version: '1',
      chainId: 1337,
      // verifyingContract: this
      verifyingContract: 0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC
    }));
  }

  // Modifier to check that the caller is the owner of the contract.
  modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    // execute the rest of the code.
    _;
  }

  /* CRUD operations */
  function isDoctor(string memory didkey) public view returns (bool) {
    return doctorsKey[didkey];
  }

  function isPharma(string memory didkey) public view returns (bool) {
    return pharmasKey[didkey];
  }

  function isPharma(address a) public view returns (bool) {
    return pharmasAddr[a];
  }

  function addNewDoctor(string memory didkey) public onlyOwner(){
    doctorsKey[didkey] = true;
  }

  function addNewPharma(string memory didkey, address a) public onlyOwner(){
    pharmasKey[didkey] = true;
    pharmasAddr[a] = true;
  }

  function getOrder(string memory orderId) public view returns (bool){
    return orders[orderId];
  }

  function getAlreadyRedeemedQuantity(string memory prId) public view returns (uint256){
    return alreadyRedeemedQuantity[prId];
  }

  function isPrescriptionValid(string memory prId, uint256 toRedeem, uint256 maxQuantity) public view returns (bool){
    if (alreadyRedeemedQuantity[prId] + toRedeem > maxQuantity) return false; //quantity exceeded
    return true;
  }

  /* Hash functions for EIP 712 */
  function hash(EIP712Domain memory eip712Domain) internal pure returns (bytes32) {
    return keccak256(abi.encode(
      EIP712DOMAIN_TYPEHASH,
      keccak256(bytes(eip712Domain.name)),
      keccak256(bytes(eip712Domain.version)),
      eip712Domain.chainId,
      eip712Domain.verifyingContract
    ));
  }

  function hash(Prescription memory prescription) internal pure returns (bytes32) {
    return keccak256(abi.encode(
      PRESCRIPTION_TYPEHASH,
      keccak256(bytes(prescription.prId)),
      prescription.quantity,
      prescription.maxQuantity,
      prescription.price
    ));
  }

  function hash(Prescription[] memory ps) internal pure returns (bytes32) {
    bytes32[] memory keccakItems = new bytes32[](ps.length);
      for(uint i=0; i<keccakItems.length;i++){
        keccakItems[i] = hash(ps[i]);
      }
    return keccak256(abi.encodePacked(keccakItems));
  }

  function hash(Order memory order) internal pure returns (bytes32) {
    return keccak256(abi.encode(
      ORDER_TYPEHASH,
      hash(order.prescriptions),
      keccak256(bytes(order.orderId)),
      order.totalPrice,
      order.pharmacy
    ));
  }

  function verify(Order memory order, uint8 v, bytes32 r, bytes32 s) internal view returns (address) {
    // Note: we need to use `encodePacked` here instead of `encode`.
    bytes32 digest = keccak256(abi.encodePacked(
      "\x19\x01",
      DOMAIN_SEPARATOR,
      hash(order)
    ));
    return ecrecover(digest, v, r, s);
  }
    
  // Order: JSON file with all the info to complete the payment
  // Sig : hash signed by the pharmacy to check the order has not been tampered
  function payOrder(Order memory order, bytes memory sig) public payable {
    require(sig.length == 65, "invalid signature length");
    require(msg.value >= order.totalPrice * 1e18, 'Amount of ETH is not enough to pay the order');
    require(!(orders[order.orderId]), 'Order has already been delivered');
    require(isPharma(order.pharmacy), 'Signer is not a valid Pharmacy');

    for(uint i=0; i<order.prescriptions.length; i++){
      require(isPrescriptionValid(
        order.prescriptions[i].prId,
        order.prescriptions[i].quantity,
        order.prescriptions[i].maxQuantity),
       'Max quantity exceeded'
      );    
    alreadyRedeemedQuantity[order.prescriptions[i].prId] += order.prescriptions[i].quantity;
    }

   uint8 v; bytes32 r; bytes32 s;
   assembly {
    /*
    First 32 bytes stores the length of the signature
    add(sig, 32) = pointer of sig + 32
    effectively, skips first 32 bytes of signature
    mload(p) loads next 32 bytes starting at the memory address p into memory
    */
    // first 32 bytes, after the length prefix
    r := mload(add(sig, 32))
    // second 32 bytes
    s := mload(add(sig, 64))
    // final byte (first byte of the next 32 bytes)
    v := byte(0, mload(add(sig, 96)))
    }

    address signer = verify(order, v, r, s);
    require(signer == order.pharmacy, 'Signer and Pharmacy does not correspond');
    (bool sent, ) = (payable (order.pharmacy)).call{value: order.totalPrice * 1e18}("");
    require(sent, "Failed to pay");

    orders[order.orderId] = true;

    emit orderHasBeenPayed(order.orderId, msg.value, order.pharmacy);

  }
}
