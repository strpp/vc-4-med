import asyncio
import didkit
import json

jwk = didkit.generate_ed25519_key()
did = didkit.key_to_did("key", jwk)

async def main():
    
    print('Generating KEYPAIR ED25519...')

    #Create pem file
    f = open("key.pem", "w")
    f.write(jwk)
    f.close()

    #Add did:key to env file
    f = open(".env", 'a')
    f.write(f'DID_KEY = {did}')
    print(f'{did}')

asyncio.run(main())