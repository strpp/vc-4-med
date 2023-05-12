import json
import uuid
from datetime import timedelta, datetime


class Credential:
    
    def __init__(self, schema):
        self.schema = schema
        self.schema['issuanceDate'] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        self.schema['expirationDate'] = (datetime.now() + timedelta(days= 365)).isoformat() + "Z"
        did = f'did:example:{str(uuid.uuid4())}'
        self.schema['id'] = did
        self.schema['credentialSubject']['id'] = did
    
    def stringify(self):
        return json.dumps(self.schema)
    
    def set_id(self, id):
        self.schema['id'] = id
        self.schema['credentialSubject']['id'] = id

    def set_value(self, key, value):
        if(key not in self.schema['credentialSubject'].keys()):
            raise ValueError('Object is missing required value')
        
        self.schema['credentialSubject'][key] = value
