import os
from dotenv import load_dotenv

dotenv_path = ".env"
load_dotenv(dotenv_path)


class Env:
    def __init__(self):
        for key, value in os.environ.items():
            setattr(self, key, value)


env = Env()

validator_private_key = os.getenv("PRIVATEKEY")
if validator_private_key is None:
    print(
        "Validator PRIVATEKEY not found. Please check readme.md to set the PRIVATEKEY in the .env variable."
    )
    exit(0)

validator_wallet_address = os.getenv("VALIDATORWALLETADDRESS")
if validator_wallet_address is None:
    print(
        "Validator VALIDATORWALLETADDRESS not found. Please check readme.md to set the VALIDATORWALLETADDRESS in the .env variable."
    )
    exit(1)

validator_reward_address = os.getenv("VALIDATORREWARDWALLETADDRESS")
if validator_reward_address is None:
    print(
        "Validator VALIDATORREWARDWALLETADDRESS not found. Please check readme.md to set the VALIDATORREWARDWALLETADDRESS in the .env variable."
    )
    exit(2)

validator_ip = os.getenv("VALIDATORIP")
if validator_ip is None:
    print(
        "Validator VALIDATORIP not found. Please check readme.md to set the VALIDATORIP in the .env variable."
    )
    exit(3)

# Inode Configuration settings

INODE_IP = "152.53.3.235"
INODE_PORT = 65432
INODE_BUFFER = 1024
PRIVATEKEY = env.PRIVATEKEY
API_URL = "https://api.upow.ai"
TRACK = 15616
CORE_URL = "https://api.upow.ai"

# Validator Configuration settings
VALIDATOR_IP = env.VALIDATORIP
VALIDATOR_PORT = 5503
CHECK_INTERVAL = 60
VALIDATOR_WALLET_ADDRESS = env.VALIDATORWALLETADDRESS
VALIDATOR_REWARD_WALLET_ADDRESS = env.VALIDATORREWARDWALLETADDRESS
FAST_API_URL = "0.0.0.0"
FAST_API_PORT = 8002
