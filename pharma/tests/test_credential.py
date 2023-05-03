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

def test_change_value():
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)
    receipt.change_value("invoice", {
            "description": "12345",
            "confirmationNumber": "abcde"
    })
    assert receipt.schema['credentialSubject']['invoice']['description'] == "12345"

@pytest.mark.asyncio
async def test_issue_credential_did_key():
    schema = json.load(open('credentials/Receipt.jsonld', 'r'))
    receipt = Credential(schema)
    receipt.change_value("invoice", {
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
    receipt.change_value("invoice", {
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
    receipt.change_value("invoice", {
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
    receipt.change_value("invoice", {
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

    
            

