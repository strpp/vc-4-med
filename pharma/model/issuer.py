import didkit
import json

class Issuer:
    def __init__(self, did_method, did, jwk):
        self.did_method = did_method
        self.did = did
        self.jwk = jwk
    
    async def issue_credential(self, credential):
        credential.schema['issuer'] = self.did
        options = {}
        if (self.did_method == 'ethr'):
            options = {"proofPurpose": "assertionMethod", "verificationMethod": f'{self.did}#controller'}
        signed_credential = await didkit.issue_credential(credential.stringify(), json.dumps(options), self.jwk)
        return signed_credential
    
    async def issue_presentation(self, presentation):
        options = {"verificationMethod": f'{self.did}#controller', 'proofPurpose' : 'authentication'}
        signed_presentation = await didkit.issue_presentation(json.dumps(presentation), json.dumps(options), self.jwk)
        return signed_presentation