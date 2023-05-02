import os
import json
import ecdsa
import jwcrypto.jwk as jwk
from dotenv import load_dotenv

load_dotenv()
key_hex = os.getenv('DOCTOR_PRIVATE_KEY')

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

