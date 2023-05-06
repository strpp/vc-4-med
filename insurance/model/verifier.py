import didkit
import json
import collections.abc
from model.registry import Registry

class Verifier():
    def __init__(self, registry):
        self.registry = registry
    
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


    async def verify_credential(self, signed_credential, credential_type):
        # verify with didkit
        options = self.get_options_from(signed_credential)
        result = await didkit.verify_credential(signed_credential, options)
        result = json.loads(result)
        if(result['errors']):
            print(result['errors'])
            return False
        
        # check identity on blockchain
        verification_method = json.loads(options)['verificationMethod']
        return await self.verify_issuer(verification_method, credential_type)

    async def verify_presentation(self, presentation, credential_type):
        # verify with didkit
        options = self.get_options_from(presentation)
        result = await didkit.verify_presentation(presentation, options)
        result = json.loads(result)
        if(result['errors']):
            print(result['errors'])
            return False
        
        # check identity on blockchain
        verification_method = json.loads(options)['verificationMethod']
        return await self.verify_issuer(verification_method, credential_type)
    
    async def verify_issuer(self, verification_method, credential_type):
        did_method = get_did_method(verification_method)
        if(did_method=='ethr'):
            issuer = get_ethr_identity(verification_method)
            if(credential_type == 'MedicalPrescriptionCredential'):
                return await self.registry.is_doctor(issuer)
            elif(credential_type == 'MedicalPrescriptionReceipt'):
                return await self.registry.is_pharmacy(issuer)

        elif(did_method=='key'):
            issuer = verification_method
            return True #Todo
        else:
            raise ValueError(f'DID method {did_method} is not supported')
    
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


def get_did_method(verification_method):
    return verification_method.split(':')[1]

def get_ethr_identity(verification_method):
    controller = verification_method.split(':')

    # mainnet did does not have a chainId field
    if(len(controller)==3):
        return controller[2].split('#')[0]
    # other net have to specify their chainId after did:ethr
    elif(len(controller)==4):
        return controller[3].split('#')[0]
    else:
        raise ValueError('Verification method is not valid')
