import json
from model.credential_request import Credential_Request

def test_create_new_request():
    schema = json.load(open('credentials/CredentialRequest.json', 'r'))
    number_credential_to_request = 4
    c = Credential_Request(schema, 'MedicalPrescription', number_credential_to_request)

    s = c.stringify()
    s = json.loads(s)
    assert len(s['query'][0]['credentialQuery']) == number_credential_to_request
