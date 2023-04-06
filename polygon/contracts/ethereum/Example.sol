// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract Example {
    
    struct EIP712Domain {
        string  name;
        string  version;
        uint256 chainId;
        address verifyingContract;
    }

    struct Prescription {
        string name;
        uint256 quantity;
        uint256 price;
    }

    struct Order {
        Prescription[] p;
        string orderId;
        uint256 totalPrice;
    }

    bytes32 constant EIP712DOMAIN_TYPEHASH = keccak256(
        "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
    );

    bytes32 constant PRESCRIPTION_TYPEHASH = keccak256(
        "Prescription(string name,uint256 quantity,uint256 price)"
    );

    bytes32 constant ORDER_TYPEHASH = keccak256(
        "Order(Prescription[] p,string orderId,uint256 totalPrice)Prescription(string name,uint256 quantity,uint256 price)"
    );

    bytes32 DOMAIN_SEPARATOR;

    constructor (){
        DOMAIN_SEPARATOR = hash(EIP712Domain({
            name: "vc4med",
            version: '1',
            chainId: 1337,
            // verifyingContract: this
            verifyingContract: 0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC
        }));
    }

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
            keccak256(bytes(prescription.name)),
            prescription.quantity,
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
            hash(order.p),
            keccak256(bytes(order.orderId)),
            order.totalPrice
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
    
    function test(Order memory order, bytes memory sig) public view returns (address) {
        require(sig.length == 65, "invalid signature length");
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
        //assert(DOMAIN_SEPARATOR == 0xf2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f);
        //assert(hash(order) == 0xc52c0ee5d84264471806290a3f2c4cecfc5490626bf912d01f240d7a274b371e);
        return (verify(order, v, r, s));
    }
}