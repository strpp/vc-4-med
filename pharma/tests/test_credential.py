# python -m pytest tests/
from model.credential import Credential
from model.issuer import Issuer
from model.verifier import Verifier
import json
import pytest

def test_create_new_credential():
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)

def test_stringify():
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)

def test_set_value():
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)
    receipt.set_value("invoice", {
            "description": "12345",
            "confirmationNumber": "abcde"
    })
    assert receipt.schema['credentialSubject']['invoice']['description'] == "12345"

@pytest.mark.asyncio
async def test_issue_credential_did_key():
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)
    receipt.set_value("invoice", {
            "description": "12345",
            "confirmationNumber": "abcde"
    })
    issuer = Issuer(
        did_method='key', 
        did='did:key:z6MktaAfLYZF3khaHZuWCho1vrJkDPXx1nkHtPSXFSwk6g5i', 
        jwk=json.dumps(json.load(open("key.pem", "r")))
    )
    signed_credential = await issuer.issue_credential(receipt)
    verification_method = 'did:key:z6MktaAfLYZF3khaHZuWCho1vrJkDPXx1nkHtPSXFSwk6g5i#z6MktaAfLYZF3khaHZuWCho1vrJkDPXx1nkHtPSXFSwk6g5i'
    assert ('proof' in json.loads(signed_credential).keys()) == True
    assert (json.loads(signed_credential)['proof']['verificationMethod']) == verification_method

@pytest.mark.asyncio
async def test_issue_credential_did_ethr():
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)
    receipt.set_value("invoice", {
            "description": "12345",
            "confirmationNumber": "abcde"
    })

    issuer = Issuer(
        did_method='ethr',
        did = 'did:ethr:0x13881:0x2e3D6752536566ED51c805A86070BA596052FCb6',
        jwk=json.dumps(json.load(open("ethkey.pem", "r")))
    )
    signed_credential = await issuer.issue_credential(receipt)
    controller_verification_method = 'did:ethr:0x13881:0x2e3D6752536566ED51c805A86070BA596052FCb6#controller'
    Eip712_verification_method = 'did:ethr:0x13881:0x2e3D6752536566ED51c805A86070BA596052FCb6#Eip712Method2021'
    assert ('proof' in json.loads(signed_credential).keys()) == True
    controller = (json.loads(signed_credential)['proof']['verificationMethod']) == controller_verification_method
    Eip712 = (json.loads(signed_credential)['proof']['verificationMethod']) == Eip712_verification_method
    assert (controller or Eip712) == True

@pytest.mark.asyncio
async def test_verify_credential_did_key():
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)
    receipt.set_value("invoice", {
            "description": "12345",
            "confirmationNumber": "abcde"
    })

    issuer = Issuer(
        did_method='key', 
        did='did:key:z6MktaAfLYZF3khaHZuWCho1vrJkDPXx1nkHtPSXFSwk6g5i', 
        jwk=json.dumps(json.load(open("key.pem", "r")))
    )
    signed_credential = await issuer.issue_credential(receipt)
    
    verifier = Verifier('key', '0x13881')
    result = await verifier.verify_credential(signed_credential)
    
    assert result == True


@pytest.mark.asyncio
async def test_verify_credential_did_ethr():
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)
    receipt.set_value("invoice", {
            "description": "12345",
            "confirmationNumber": "abcde"
    })

    issuer = Issuer(
        did_method='ethr',
        did = 'did:ethr:0x13881:0x2e3D6752536566ED51c805A86070BA596052FCb6',
        jwk=json.dumps(json.load(open("ethkey.pem", "r")))
    )
    signed_credential = await issuer.issue_credential(receipt)
    
    verifier = Verifier('key', '0x13881')
    result = await verifier.verify_credential(signed_credential)
    
    assert result == True

def test_are_credentials_unique():
    verifier = Verifier('key', '0x13881')
    presentation = '{"@context":["https://www.w3.org/2018/credentials/v1"],"id":"urn:uuid:6ca730db-0a5e-4e2e-87bd-3879b54e7011","type":["VerifiablePresentation"],"verifiableCredential":[{"@context":["https://www.w3.org/2018/credentials/v1","https://schema.org/"],"id":"did:example:c68652180e6c4ef9814974c9e7c93677","type":["VerifiableCredential","MedicalPrescriptionCredential"],"credentialSubject":{"id":"did:example:d1c44e337d0a4fa2b66eb79c129927ce","prescription":{"@type":"MedicalPrescription","dosage":"4","drug":"Actigrip","name":"Tommaso","surname":"Baldo"}},"issuer":"did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX","issuanceDate":"2023-04-24T16:52:58Z","proof":{"type":"Ed25519Signature2018","proofPurpose":"assertionMethod","verificationMethod":"did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX#z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX","created":"2023-04-24T16:53:04.632Z","jws":"eyJhbGciOiJFZERTQSIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..Rjphe_KEDxzG01Zj4D0S_wGAuami4ACifuC0ZaBYF6gQ61y2RK0A7IHpG9KCE2Qj3W_QqKnG3FRcDVlxP_hfBQ"},"expirationDate":"2024-04-23T18:52:58.504163Z"},{"@context":["https://www.w3.org/2018/credentials/v1","https://schema.org/"],"id":"did:example:793b2f1ebaa343299b5955d9dbeb786b","type":["VerifiableCredential","MedicalPrescriptionCredential"],"credentialSubject":{"id":"did:example:746f895bdb2946358aef7970b6929cd0","prescription":{"@type":"MedicalPrescription","dosage":"1","drug":"Paracetamol","name":"Tommaso","surname":"Baldo"}},"issuer":"did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX","issuanceDate":"2023-04-24T16:51:18Z","proof":{"type":"Ed25519Signature2018","proofPurpose":"assertionMethod","verificationMethod":"did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX#z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX","created":"2023-04-24T16:51:25.893Z","jws":"eyJhbGciOiJFZERTQSIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..fhkB80zs9Oq8-IkTmg9wGA-fs3wsPtefqYLWJPn2EiFMNv1kuttw3QI5b2lkrg0iaoqrt7-6ZBRCyDiTpi_WBQ"},"expirationDate":"2024-04-23T18:51:18.183166Z"}],"proof":{"type":"Ed25519Signature2018","proofPurpose":"authentication","challenge":"546d975f-49ee-478d-a35d-6564d6792954","verificationMethod":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj#z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj","created":"2023-05-03T13:35:57.429Z","domain":"","jws":"eyJhbGciOiJFZERTQSIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..FQwSjzbtDBKNgCAtT3sYM2XqPzQ4gLMFkrKNIjXr_b0r0JPELphnwFh_CMwd8xe-gFWKEOWblZpC-eecVUm3DA"},"holder":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj"}'
    result = verifier.are_credentials_unique(presentation)
    assert result == True

    presentation = '{"@context":["https://www.w3.org/2018/credentials/v1"],"id":"urn:uuid:6ca730db-0a5e-4e2e-87bd-3879b54e7011","type":["VerifiablePresentation"],"verifiableCredential":[{"@context":["https://www.w3.org/2018/credentials/v1","https://schema.org/"],"id":"did:example:c68652180e6c4ef9814974c9e7c93677","type":["VerifiableCredential","MedicalPrescriptionCredential"],"credentialSubject":{"id":"a","prescription":{"@type":"MedicalPrescription","dosage":"4","drug":"Actigrip","name":"Tommaso","surname":"Baldo"}},"issuer":"did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX","issuanceDate":"2023-04-24T16:52:58Z","proof":{"type":"Ed25519Signature2018","proofPurpose":"assertionMethod","verificationMethod":"did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX#z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX","created":"2023-04-24T16:53:04.632Z","jws":"eyJhbGciOiJFZERTQSIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..Rjphe_KEDxzG01Zj4D0S_wGAuami4ACifuC0ZaBYF6gQ61y2RK0A7IHpG9KCE2Qj3W_QqKnG3FRcDVlxP_hfBQ"},"expirationDate":"2024-04-23T18:52:58.504163Z"},{"@context":["https://www.w3.org/2018/credentials/v1","https://schema.org/"],"id":"did:example:793b2f1ebaa343299b5955d9dbeb786b","type":["VerifiableCredential","MedicalPrescriptionCredential"],"credentialSubject":{"id":"a","prescription":{"@type":"MedicalPrescription","dosage":"1","drug":"Paracetamol","name":"Tommaso","surname":"Baldo"}},"issuer":"did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX","issuanceDate":"2023-04-24T16:51:18Z","proof":{"type":"Ed25519Signature2018","proofPurpose":"assertionMethod","verificationMethod":"did:key:z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX#z6MkeWr8PVVshiC14dGLUQNrE1Y2AcvfemHHQ1xKivsVB6JX","created":"2023-04-24T16:51:25.893Z","jws":"eyJhbGciOiJFZERTQSIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..fhkB80zs9Oq8-IkTmg9wGA-fs3wsPtefqYLWJPn2EiFMNv1kuttw3QI5b2lkrg0iaoqrt7-6ZBRCyDiTpi_WBQ"},"expirationDate":"2024-04-23T18:51:18.183166Z"}],"proof":{"type":"Ed25519Signature2018","proofPurpose":"authentication","challenge":"546d975f-49ee-478d-a35d-6564d6792954","verificationMethod":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj#z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj","created":"2023-05-03T13:35:57.429Z","domain":"","jws":"eyJhbGciOiJFZERTQSIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..FQwSjzbtDBKNgCAtT3sYM2XqPzQ4gLMFkrKNIjXr_b0r0JPELphnwFh_CMwd8xe-gFWKEOWblZpC-eecVUm3DA"},"holder":"did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj"}'
    result = verifier.are_credentials_unique(presentation)
    assert result == False

def test_serialize_credential():    
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)
    receipt.set_value("invoice", {
            "description": "12345",
            "confirmationNumber": "abcde"
    })
    json.dumps(receipt.schema)

@pytest.mark.asyncio
async def test_issue_presentation():
    pr = {
'@context': ['https://www.w3.org/2018/credentials/v1', 'https://www.w3.org/2018/credentials/examples/v1'], 
'type': ['VerifiablePresentation'], 
'verifiableCredential': 
	[
		{
		'@context': ['https://www.w3.org/2018/credentials/v1', {'MedicalPrescriptionReceipt': {'@context': {'@protected': True, '@version': 1.1, 'id': '@id', 'invoice': {'@context': {'@protected': True, '@version': 1.1, 'confirmationNumber': 'schema:confirmationNumber', 'description': 'schema:description', 'schema': 'https://schema.org/'}, '@id': 'schema:invoice'}, 'schema': 'https://schema.org/', 'type': '@type'}, '@id': 'https://example.com'}}], 
		'id': 'did:example:8a52a672278e41159d9f47f5b6015044', 
		'type': ['VerifiableCredential', 'MedicalPrescriptionReceipt'], 
		'credentialSubject': 
			{
			'id': 'did:example:8a52a672278e41159d9f47f5b6015044', 
			'type': 'MedicalPrescriptionReceipt', 
			'invoice': 
				{
				'confirmationNumber': '12345', 
				'description': 
					{
					'@context': ['https://www.w3.org/2018/credentials/v1'], 
					'holder': 'did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj', 
					'id': 'urn:uuid:660ef85b-3699-440c-806f-f5d377a5c165', 
					'proof': 
						{
						'challenge': 'c1a47c47-e38f-4dde-92ea-cb21224f1931', 
						'created': '2023-05-03T14:25:23.566Z', 
						'domain': '', 
						'jws': 'eyJhbGciOiJFZERTQSIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..ZlfqtyylEKI3JawsXaps2f9J53yfVyUb8aXkT04mI7XWcXIx4Q0eJkLmW0icWekuxRVEbJ3uma-EZeA0lI8EBw', 
						'proofPurpose': 'authentication', 
						'type': 'Ed25519Signature2018', 
						'verificationMethod': 'did:key:z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj#z6MkrJJ2cuw8TN75X7Ps51WddZ6qVuRKJ1muSQiRuz7cBoPj'}, 
					'type': ['VerifiablePresentation'], 
					'verifiableCredential': 
						{
						'@context': ['https://www.w3.org/2018/credentials/v1', {'MedicalPrescriptionCredential': {'@context': {'@protected': True, '@version': 1.1, 'drug': 'schema:drug', 'id': '@id', 'quantity': 'schema:quantity', 'schema': 'https://schema.org/', 'type': '@type'}, '@id': 'https://example.com'}}], 
						'credentialSubject': 
							{
							'drug': 'Tachipirina', 
							'id': 'did:example:cd67a8de809a41e99f4af5ae6818194e', 
							'quantity': '1', 
							'type': 'MedicalPrescriptionCredential'
							}, 
						'expirationDate': '2024-05-02T15:52:11.859711Z', 
						'id': 'did:example:e2459653b10f48c3a698032a2c4a1c9b', 
						'issuanceDate': '2023-05-03T13:52:11Z', 
						'issuer': 'did:ethr:0x13881:0xd661a61c964b8872db826dc854888527c235119f', 
						'proof': 
							{
							'@context': ['https://identity.foundation/EcdsaSecp256k1RecoverySignature2020/lds-ecdsa-secp256k1-recovery2020-0.0.jsonld', 'https://demo.spruceid.com/EcdsaSecp256k1RecoverySignature2020/esrs2020-extra-0.0.jsonld'], 
							'created': '2023-05-03T13:52:13.218Z', 
							'jws': 'eyJhbGciOiJFUzI1NkstUiIsImNyaXQiOlsiYjY0Il0sImI2NCI6ZmFsc2V9..G4TFVnsSZECZXT7VqroFZdceGDRgSBn_nBf16dXdB49KcSAnkTjrzZJ4FauHWzfUTiNYS5MJn2WgRN7y9RBEvAA', 
							'proofPurpose': 'assertionMethod', 
							'type': 'EcdsaSecp256k1RecoverySignature2020', 
							'verificationMethod': 'did:ethr:0x13881:0xd661a61c964b8872db826dc854888527c235119f#controller'}, 
							'type': ['VerifiableCredential', 'MedicalPrescriptionCredential']
						}
					}
				}
			}, 
			'issuer': 'did:ethr:0x2e3D6752536566ED51c805A86070BA596052FCb6', 
			'issuanceDate': '2023-05-03T14:25:29Z', 
			'proof': 
				{
				'@context': ['https://identity.foundation/EcdsaSecp256k1RecoverySignature2020/lds-ecdsa-secp256k1-recovery2020-0.0.jsonld', 'https://demo.spruceid.com/EcdsaSecp256k1RecoverySignature2020/esrs2020-extra-0.0.jsonld'], 
				'type': 'EcdsaSecp256k1RecoverySignature2020', 
				'proofPurpose': 'assertionMethod', 
				'verificationMethod': 'did:ethr:0x2e3D6752536566ED51c805A86070BA596052FCb6#controller', 
				'created': '2023-05-03T14:25:29.443Z', 
				'jws': 'eyJhbGciOiJFUzI1NkstUiIsImtpZCI6IkZaOV9vMTE0VEdxRVRDeVBtdFJZYVVjY1FjY0c5OW9xMzlJN3dUN2RmeEkiLCJjcml0IjpbImI2NCJdLCJiNjQiOmZhbHNlfQ..G4TFVnsSZECZXT7VqroFZdceGDRgSBn_nBf16dXdB4961OTO6wW5QC17tjStna6pbSrp5dMrLJTQfs__nUGWcwA'
				}, 
			'expirationDate': '2024-05-02T16:25:29.441875Z'
		}
	]
}
    issuer = Issuer(
        did_method='ethr',
        did = 'did:ethr:0x13881:0x2e3D6752536566ED51c805A86070BA596052FCb6',
        jwk=json.dumps(json.load(open("ethkey.pem", "r")))
    )
    await issuer.issue_presentation(pr)
            

