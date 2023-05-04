import json
import uuid

class Credential_Manifest:
    def __init__(self, id):
        self.schema = json.load(open('credentials/prescription_credential_manifest.json', 'r'))
        self.schema['output_descriptors'][0]['id'] = id

    def set_issuer(self, did):
        self.schema['issuer']['id'] = did
    
    def set_doctor(self, doctor):
        self.schema['output_descriptors'][0]['display']['properties'][0]['fallback'] = doctor
    
    def set_description(self, description):
        self.schema['output_descriptors'][0]['display']['subtitle']['fallback'] = description

    def add_proof_of_identity(self, name, surname):

        self.schema['presentation_definition'] = {
            'id' : str(uuid.uuid4()), 
            'input_descriptors' : [
                {
                "id":"input1",
                "constraints":{"fields":[]}
                }
            ]
        }
        
        filter_type = {
            "path": ["$.type"],
            "filter": {
                "type": "string",
                "pattern": "VerifiableId"
            }
        }
        
        # NOTE: i don't know why on Altme Name=FamilyName and Surname=firstName
        filter_first_name =  {
            "path": [
                "$.credentialSubject.firstName"
            ],
            "filter": {
            "type": "string",
            "pattern": surname.upper()
                }
        }
        filter_family_name =  {
            "path": [
                "$.credentialSubject.familyName"
            ],
            "filter": {
                "type": "string",
                "pattern": name.upper()
            }
        }

        self.schema['presentation_definition']['input_descriptors'][0]['constraints']['fields'] = [
            filter_type, filter_first_name, filter_family_name
        ]

