import os
from dotenv import load_dotenv

dotenv_path = ".env"
load_dotenv(dotenv_path)


class Env:
    def __init__(self):
        for key, value in os.environ.items():
            setattr(self, key, value)


env = Env()

# Inode Configuration settings

INODE_IP = "127.0.0.1"
INODE_PORT = 65432
INODE_BUFFER = 1024
PRIVATEKEY = env.PRIVATEKEY
API_URL = "http://127.0.0.1:3006"
TRACK = 500
CORE_URL = "http://127.0.0.1:3006"

# Validator Configuration settings
VALIDATOR_IP = "127.0.0.1"
VALIDATOR_PORT = 5503
CHECK_INTERVAL = 60
VALIDATOR_WALLET_ADDRESS = "DZ3hFKMTXnTHWtG8pRquCDfGBnSShfDwTKKzkoibvb3NA"
VALIDATOR_REWARD_WALLET_ADDRESS = "Djxhpx8ogGwpfe1tHxuBLVuxXZEhrS7spstDuXUugJ32i"
FAST_API_URL = "0.0.0.0"
FAST_API_PORT = 8002
