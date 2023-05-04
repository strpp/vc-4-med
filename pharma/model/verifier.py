import didkit
import json
import collections.abc

class Verifier():
    def __init__(self, did_method, chain_id):
        self.did_method = did_method
        self.chain_id = chain_id
    
    def get_options_from(self, json_file):
        json_file = json.loads(json_file)
        if('proof' not in json_file.keys()):
            raise ValueError('Presentation or Credential is not signed')
        
        if('verificationMethod' not in json_file['proof'].keys()):
            raise ValueError('Missing parameters in Proof')
        
        verification_method = json_file['proof']['verificationMethod']
        proof_of_purpose = json_file['proof']['proofPurpose']
        options = {"proofPurpose": proof_of_purpose, "verificationMethod": verification_method}
        return json.dumps(options)


    async def verify_credential(self, signed_credential):
        # verify with didkit
        options = self.get_options_from(signed_credential)
        result = await didkit.verify_credential(signed_credential, options)
        result = json.loads(result)
        if(result['errors']):
            print(result['errors'])
            return False

        # check validity on blockchain


        # check identity

        return True

    async def verify_presentation(self, presentation):
        # verify with didkit
        options = self.get_options_from(presentation)
        result = await didkit.verify_presentation(presentation, options)
        result = json.loads(result)
        if(result['errors']):
            print(result['errors'])
            return False
        # check validity on blockchain


        # check identity

        return True
    
    def are_credentials_unique(self, presentation):
        # Check VCs are unique
        presentation = json.loads(presentation)
        if isinstance(presentation['verifiableCredential'], collections.abc.Sequence): #if there is only one vc, this is not an array
            ids = []
            for vc in presentation['verifiableCredential']:
                if (vc['credentialSubject']['id']) not in ids:
                    ids.append(vc['credentialSubject']['id'])
                else:
                    return False
        
        return True

        