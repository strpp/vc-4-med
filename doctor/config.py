import os
from dotenv import load_dotenv

load_dotenv()

# General Config
SECRET_KEY = os.getenv("MY_SECRET_KEY")

# Doctor
DOCTOR = os.getenv('DOCTOR')
DOCTOR_PRIVATE_KEY = os.getenv('DOCTOR_PRIVATE_KEY')
DOCTOR_PUBLIC_KEY = os.getenv('DOCTOR_PUBLIC_KEY')
DID_METHOD = 'did:ethr'

# Blockchain
RPC_URL = os.getenv('MUMBAI_URL')

# did:ethr registry
DOCTOR_IDENTITY = '0x5D00c7A06f6fE6aC36B0347C8E5536c799E492b2'
REGISTRY_ADDRESS = '0xdCa7EF03e98e0DC2B855bE647C39ABe984fcF21B'

