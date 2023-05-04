import json
import uuid

class Credential_Request:
    def __init__(self, schema, type, number_of_credential_to_request):
        self.schema = schema
        self.type = type
        self.schema['challenge'] = str(uuid.uuid4())

        for i in range(1, number_of_credential_to_request + 1):
            self.schema['query'][0]['credentialQuery'].append({"example": {"type": type}})
    
    def stringify(self):
        return json.dumps(self.schema)
