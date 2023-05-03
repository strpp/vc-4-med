import didkit
import json
import ecdsa
import jwcrypto.jwk as jwk
import os
from dotenv import load_dotenv

def generate_did_key():
    
    jwk = didkit.generate_ed25519_key()
    did = didkit.key_to_did("key", jwk)
    
    print('Generating KEYPAIR ED25519...')

    #Create pem file
    f = open("key.pem", "w")
    f.write(jwk)
    f.close()

    #Add did:key to env file
    f = open(".env", 'a')
    f.write(f'DID_KEY = {did}')
    print(f'{did}')

def generate_pem_from_ethereum_account():

    load_dotenv()
    key_hex = os.getenv('PHARMACY_PRIVATE_KEY')

    if(key_hex):
        key_bytes = bytes.fromhex(key_hex)
        key = ecdsa.SigningKey.from_string(key_bytes, curve=ecdsa.SECP256k1)
        pem = key.to_pem()

        jwk_key = jwk.JWK.from_pem(pem, password=None)
        jwk_key_dict = jwk_key.export(as_dict=True)
    
        #Create pem file
        f = open("ethkey.pem", "w")
        f.write(json.dumps(jwk_key_dict))
        f.close()

    else:
        print('key is not valid')
