# python -m pytest tests/

from model.verifier import Verifier
from model.registry import Registry
from dotenv import load_dotenv
import os
import json
import didkit
import pytest

load_dotenv()

@pytest.mark.asyncio
async def test_prescription_presentation():
    vp = 					{
					"@context":["https://www.w3.org/2018/credentials/v1"],
					"holder":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj",
					"id":"urn:uuid:5302aee1-fd87-4b30-9679-4cb0736356c6",
					"proof":
						{
						"challenge":"b9e9be0d-a713-4f66-8b03-70d4f9b956dc",
						"created":"2023-05-03T14:30:42.042Z",
						"domain":"",
						"jws":"eyJhbGciOiJFZERTQSIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..7MjMWDbjFtcKlpQ-n5tXRopHMdcr12CvM6IhmOpYr1lR1UWb8TwmWTrdMcDIDDdDRdFHCvwGr2IFgZBgNtpUBg",
						"proofPurpose":"authentication",
						"type":"Ed25519Signature2018",
						"verificationMethod":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj#z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj"
						},
					"type":["VerifiablePresentation"],
					"verifiableCredential":
						{
						"@context":["https://www.w3.org/2018/credentials/v1",{"MedicalPrescriptionCredential":{"@context":{"@protected":True,"@version":1.1,"drug":"schema:drug","id":"@id","quantity":"schema:quantity","schema":"https://schema.org/","type":"@type"},"@id":"https://example.com"}}],
						"credentialSubject":
							{
							"drug":"Ebastina",
							"id":"did:example:842016e8d4f145a2a5d130eaa7638cac",
							"quantity":"1",
							"type":"MedicalPrescriptionCredential"
							},
						"expirationDate":"2024-05-02T16:30:28.070172Z",
						"id":"did:example:6ed92a69f982411b863fdc8791c00af8",
						"issuanceDate":"2023-05-03T14:30:28Z",
						"issuer":"did:ethr:0x13881:0xd661a61c964b8872db826dc854888527c235119f",
						"proof":{"@context":["https://identity.foundation/EcdsaSecp256k1RecoverySignature2020/lds-ecdsa-secp256k1-recovery2020-0.0.jsonld","https://demo.spruceid.com/EcdsaSecp256k1RecoverySignature2020/esrs2020-extra-0.0.jsonld"],"created":"2023-05-03T14:30:29.378Z","jws":"eyJhbGciOiJFUzI1NkstUiIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..G4TFVnsSZECZXT7VqroFZdceGDRgSBn_nBf16dXdB486jZkPcEVqSU_9scJFtlRggxuTr44Io7fflVXzED3GbQA","proofPurpose":"assertionMethod","type":"EcdsaSecp256k1RecoverySignature2020","verificationMethod":"did:ethr:0x13881:0xd661a61c964b8872db826dc854888527c235119f#controller"},
						"type":["VerifiableCredential","MedicalPrescriptionCredential"]
						}
					}
    vp = json.dumps(vp)

    registry = Registry(
        os.getenv('MUMBAI_URL'),
        '0xdCa7EF03e98e0DC2B855bE647C39ABe984fcF21B',
        '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2',
        '0x2e3D6752536566ED51c805A86070BA596052FCb6'
    )
    verifier = Verifier(registry)

    result = await verifier.verify_presentation(vp, 'MedicalPrescriptionCredential')
    assert result == True
    
@pytest.mark.asyncio
async def test_invoice_presentation():
    vp = {
    "@context":["https://www.w3.org/2018/credentials/v1","https://www.w3.org/2018/credentials/examples/v1"],
    "type":["VerifiablePresentation"],
    "verifiableCredential":
    [
        {
            "@context":["https://www.w3.org/2018/credentials/v1",{"MedicalPrescriptionReceipt":{"@context":{"@protected":True,"@version":1.1,"id":"@id","invoice":{"@context":{"@protected":True,"@version":1.1,"confirmationNumber":"schema:confirmationNumber","description":"schema:description","schema":"https://schema.org/"},"@id":"schema:invoice"},"schema":"https://schema.org/","type":"@type"},"@id":"https://example.com"}}],
            "id":"did:example:8a52a672278e41159d9f47f5b6015044",
            "type":["VerifiableCredential","MedicalPrescriptionReceipt"],
            "credentialSubject":
            {
                "id":"did:example:8a52a672278e41159d9f47f5b6015044",
                "invoice":
                {
                    "confirmationNumber":"12345",
                    "description":
                        {
                            "@context":["https://www.w3.org/2018/credentials/v1"],
                            "holder":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj",
                            "id":"urn:uuid:660ef85b-3699-440c-806f-f5d377a5c165",
                            "proof":{"challenge":"c1a47c47-e38f-4dde-92ea-cb21224f1931",
                                "created":"2023-05-03T14:25:23.566Z","domain":"","jws":"eyJhbGciOiJFZERTQSIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..ZlfqtyylEKI3JawsXaps2f9J53yfVyUb8aXkT04mI7XWcXIx4Q0eJkLmW0icWekuxRVEbJ3uma-EZeA0lI8EBw","proofPurpose":"authentication","type":"Ed25519Signature2018","verificationMethod":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj#z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj"},"type":["VerifiablePresentation"],"verifiableCredential":{"@context":["https://www.w3.org/2018/credentials/v1",{"MedicalPrescriptionCredential":{"@context":{"@protected":True,"@version":1.1,"drug":"schema:drug","id":"@id","quantity":"schema:quantity","schema":"https://schema.org/","type":"@type"},"@id":"https://example.com"}}],"credentialSubject":{"drug":"Tachipirina","id":"did:example:cd67a8de809a41e99f4af5ae6818194e","quantity":"1","type":"MedicalPrescriptionCredential"},"expirationDate":"2024-05-02T15:52:11.859711Z","id":"did:example:e2459653b10f48c3a698032a2c4a1c9b","issuanceDate":"2023-05-03T13:52:11Z","issuer":"did:ethr:0x13881:0xd661a61c964b8872db826dc854888527c235119f","proof":{"@context":["https://identity.foundation/EcdsaSecp256k1RecoverySignature2020/lds-ecdsa-secp256k1-recovery2020-0.0.jsonld","https://demo.spruceid.com/EcdsaSecp256k1RecoverySignature2020/esrs2020-extra-0.0.jsonld"],"created":"2023-05-03T13:52:13.218Z","jws":"eyJhbGciOiJFUzI1NkstUiIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..G4TFVnsSZECZXT7VqroFZdceGDRgSBn_nBf16dXdB49KcSAnkTjrzZJ4FauHWzfUTiNYS5MJn2WgRN7y9RBEvAA","proofPurpose":"assertionMethod","type":"EcdsaSecp256k1RecoverySignature2020","verificationMethod":"did:ethr:0x13881:0xd661a61c964b8872db826dc854888527c235119f#controller"},"type":["VerifiableCredential","MedicalPrescriptionCredential"]}}
                },
                "type":"MedicalPrescriptionReceipt"
            },
            "issuer":"did:ethr:0x2e3D6752536566ED51c805A86070BA596052FCb6",
            "issuanceDate":"2023-05-03T14:25:29Z",
            "proof":
            {
                "@context":["https://identity.foundation/EcdsaSecp256k1RecoverySignature2020/lds-ecdsa-secp256k1-recovery2020-0.0.jsonld","https://demo.spruceid.com/EcdsaSecp256k1RecoverySignature2020/esrs2020-extra-0.0.jsonld"],
                "type":"EcdsaSecp256k1RecoverySignature2020",
                "proofPurpose":"assertionMethod",
                "verificationMethod":"did:ethr:0x2e3D6752536566ED51c805A86070BA596052FCb6#controller",
                "created":"2023-05-03T14:25:29.443Z",
                "jws":"eyJhbGciOiJFUzI1NkstUiIsImtpZCI6IkZaOV9vMTE0VEdxRVRDeVBtdFJZYVVjY1FjY0c5OW9xMzlJN3dUN2RmeEkiLCJjcml0IjpbImI2NCJdLCJiNjQiOmZhbHNlfQ..G4TFVnsSZECZXT7VqroFZdceGDRgSBn_nBf16dXdB4961OTO6wW5QC17tjStna6pbSrp5dMrLJTQfs__nUGWcwA"
            },
            "expirationDate":"2024-05-02T16:25:29.441875Z"
        }
    ],
    "proof":
    {
        "@context":["https://identity.foundation/EcdsaSecp256k1RecoverySignature2020/lds-ecdsa-secp256k1-recovery2020-0.0.jsonld","https://demo.spruceid.com/EcdsaSecp256k1RecoverySignature2020/esrs2020-extra-0.0.jsonld"],
        "type":"EcdsaSecp256k1RecoverySignature2020",
        "proofPurpose":"authentication",
        "verificationMethod":"did:ethr:0x13881:0x2e3D6752536566ED51c805A86070BA596052FCb6#controller",
        "created":"2023-05-04T15:26:34.745Z",
        "jws":"eyJhbGciOiJFUzI1NkstUiIsImtpZCI6IkZaOV9vMTE0VEdxRVRDeVBtdFJZYVVjY1FjY0c5OW9xMzlJN3dUN2RmeEkiLCJjcml0IjpbImI2NCJdLCJiNjQiOmZhbHNlfQ..G4TFVnsSZECZXT7VqroFZdceGDRgSBn_nBf16dXdB49eWLJRHZRpDelevphesa5gR3Flo5SkwhnsVwCT8Rd79AE"
    }
}

    vp = json.dumps(vp)
    registry = Registry(
        os.getenv('MUMBAI_URL'),
        '0xdCa7EF03e98e0DC2B855bE647C39ABe984fcF21B',
        '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2',
        '0x2e3D6752536566ED51c805A86070BA596052FCb6'
    )
    verifier = Verifier(registry)

    result = await verifier.verify_presentation(vp, 'MedicalPrescriptionReceipt')
    assert result == True

@pytest.mark.asyncio
async def test_pharmacy_id():

    registry = Registry(
        os.getenv('MUMBAI_URL'),
        '0xdCa7EF03e98e0DC2B855bE647C39ABe984fcF21B',
        '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2',
        '0x2e3D6752536566ED51c805A86070BA596052FCb6'
    )
    result = await registry.is_pharmacy('0x2e3D6752536566ED51c805A86070BA596052FCb6')
    assert result == True