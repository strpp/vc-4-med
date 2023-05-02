import json
import didkit
import pytest
from datetime import timedelta, datetime


@pytest.mark.asyncio
async def test_pass_issuing():
    eth_jwk = json.dumps(json.load(open("ethkey.pem", "r")))
    did = 'did:ethr:0xd661a61c964b8872db826dc854888527c235119f'
    credential = {
        "@context":["https://www.w3.org/2018/credentials/v1",{"Pass":{"@context":{"@protected":True,"@version":1.1,"duration":"schema:duration","id":"@id","image":{"@id":"schema:image","@type":"@id"},"issuedBy":{"@context":{"@protected":True,"@version":1.1,"address":"schema:address","issuerId":"schema:identifier","logo":{"@id":"schema:logo","@type":"@id"},"name":"schema:name","schema":"https://schema.org/"},"@id":"schema:issuedBy"},"schema":"https://schema.org/","type":"@type"},"@id":"https://github.com/TalaoDAO/context/blob/main/README.me#pass"}}],
        "id":"urn:uuid:d9085432-8540-4691-86ff-3c1fae5cfc46",
        "type":["VerifiableCredential","Pass"],
        "credentialSubject":
        {
            "id":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj",
            "issuedBy":{"address":"","issuerId":"qcmthtpdmc","name":"New company"},
            "type":"Pass",
            "duration":"365"
        },
        "issuer":"did:ethr:0xd661a61c964b8872db826dc854888527c235119f",
        "issuanceDate":"2023-04-27T09:06:22Z",
        "expirationDate":"2024-04-26T09:06:22Z"
        }
    options = {
        "proofPurpose" : "assertionMethod",
        "verificationMethod" : await didkit.key_to_verification_method('ethr', eth_jwk),
        "type": "EcdsaSecp256k1RecoverySignature2020"
    }
    c = await didkit.issue_credential(
        json.dumps(credential),
        options.__str__().replace("'", '"'),
        eth_jwk
    )
    v = await didkit.verify_credential(c, '{}')
    print(v)

@pytest.mark.asyncio
async def test_prescription_issuing():
    eth_jwk = json.dumps(json.load(open("ethkey.pem", "r")))
    did = 'did:ethr:0xd661a61c964b8872db826dc854888527c235119f'
    
    credential = json.load(open('/home/pi/vc-4-med/doctor/credentials/PrescriptionNoPersonalInfo.jsonld', 'r'))
    
    credential['issuer'] = did
    credential['id'] = "did:example:c68652180e6c4ef9814974c9e7c93677"
    credential['credentialSubject']['id'] = "did:example:c68652180e6c4ef9814974c9e7c93677"
    credential['credentialSubject']['drug'] = 'A'
    credential['credentialSubject']['quantity'] = '1'
    credential['issuanceDate'] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    credential['expirationDate'] =  (datetime.now() + timedelta(days= 365)).isoformat() + "Z"
    
    options = {
        "proofPurpose" : "assertionMethod",
        "verificationMethod" : await didkit.key_to_verification_method('ethr', eth_jwk),
    }
    c = await didkit.issue_credential(
        json.dumps(credential),
        options.__str__().replace("'", '"'),
        eth_jwk
    )
    v = await didkit.verify_credential(c, '{}')
    print(v)

@pytest.mark.asyncio
async def test_verifying():
    signed_credential = {
        "@context":["https://www.w3.org/2018/credentials/v1",{"Pass":{"@context":{"@protected":True,"@version":1.1,"duration":"schema:duration","id":"@id","image":{"@id":"schema:image","@type":"@id"},"issuedBy":{"@context":{"@protected":True,"@version":1.1,"address":"schema:address","issuerId":"schema:identifier","logo":{"@id":"schema:logo","@type":"@id"},"name":"schema:name","schema":"https://schema.org/"},"@id":"schema:issuedBy"},"schema":"https://schema.org/","type":"@type"},"@id":"https://github.com/TalaoDAO/context/blob/main/README.me#pass"}}],
        "id":"urn:uuid:d9085432-8540-4691-86ff-3c1fae5cfc46",
        "type":["VerifiableCredential","Pass"],
        "credentialSubject":
        {
            "id":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj",
            "issuedBy":{"address":"","issuerId":"qcmthtpdmc","name":"New company"},
            "type":"Pass","duration":"365"
        },
        "issuer":"did:ethr:0xd661a61c964b8872db826dc854888527c235119f",
        "issuanceDate":"2023-04-27T09:06:22Z",
        "proof":
        {
            "@context":["https://identity.foundation/EcdsaSecp256k1RecoverySignature2020/lds-ecdsa-secp256k1-recovery2020-0.0.jsonld","https://demo.spruceid.com/EcdsaSecp256k1RecoverySignature2020/esrs2020-extra-0.0.jsonld"],
            "type":"EcdsaSecp256k1RecoverySignature2020",
            "proofPurpose":"assertionMethod",
            "verificationMethod":"did:ethr:0xd661a61c964b8872db826dc854888527c235119f#controller",
            "created":"2023-04-27T09:06:22.496Z",
            "jws":"eyJhbGciOiJFUzI1NkstUiIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..G4TFVnsSZECZXT7VqroFZdceGDRgSBn_nBf16dXdB49VQJu7fpG-FxBq8X39Ur9f454o8GX7gY-8pOMghuVHPAE"},
        "expirationDate":"2024-04-26T09:06:22Z"
        }
    options = {
            "proofPurpose": "assertionMethod",
            "verificationMethod":"did:ethr:0xd661a61c964b8872db826dc854888527c235119f#controller",
        }
    v = await didkit.verify_credential(json.dumps(signed_credential), json.dumps(options))
    print(v)

@pytest.mark.asyncio
async def test_mumbai():
    jwk = json.dumps(json.load(open("ethkey.pem", "r")))
    public_key = '0xd661a61c964b8872db826dc854888527c235119f'
    chain_id = '0x13881'
    did = f'did:ethr:{chain_id}:{public_key}'
    verification_method = f'did:ethr:{chain_id}:{public_key}#controller'
    
    credential = json.load(open('/home/pi/vc-4-med/doctor/credentials/PrescriptionNoPersonalInfo.jsonld', 'r'))
    
    credential['issuer'] = did
    credential['id'] = "did:example:c68652180e6c4ef9814974c9e7c93677"
    credential['credentialSubject']['id'] = "did:example:c68652180e6c4ef9814974c9e7c93677"
    credential['credentialSubject']['drug'] = 'A'
    credential['credentialSubject']['quantity'] = '1'
    credential['issuanceDate'] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    credential['expirationDate'] =  (datetime.now() + timedelta(days= 365)).isoformat() + "Z"
    
    options = {
        "proofPurpose" : "assertionMethod",
        "verificationMethod" : verification_method,
    }
    c = await didkit.issue_credential(
        json.dumps(credential),
        options.__str__().replace("'", '"'),
        jwk
    )
    v = await didkit.verify_credential(c, '{}')
    print(v)