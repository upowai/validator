import logging
import requests
from requests.exceptions import HTTPError
from upow_transactions.helpers import sha256
from utils.utils import Utils

wallet_utils: Utils = Utils()


def string_to_bytes(string: str) -> bytes:
    if string is None:
        return None
    try:
        return bytes.fromhex(string)
    except ValueError:
        return string.encode("utf-8")


async def push_tx(tx, wallet_utils: Utils):
    try:
        r = requests.get(
            f"{wallet_utils.NODE_URL}/push_tx", {"tx_hex": tx.hex()}, timeout=10
        )
        r.raise_for_status()
        res = r.json()
        if res["ok"]:
            transaction_hash = sha256(tx.hex())
            logging.info(f"Transaction pushed. Transaction hash: {transaction_hash}")
            return transaction_hash
        else:
            logging.error("\nTransaction has not been pushed")
            return None
    except HTTPError as http_err:

        if http_err.response.status_code == 414:
            logging.error("URI Too Long for url: The request URL is too long.")
            return None
        else:
            logging.error(f"HTTP error occurred: {http_err}")
    except Exception as e:
        logging.error(f"Error during request to node: {e}")
        return None


async def send_transaction(private_key_hex, recipients, amounts, message=None):
    private_key = int(private_key_hex, 16)
    recipients_list = recipients.split(",")
    amounts_list = amounts.split(",")
    message_bytes = string_to_bytes(message) if message else None
    if (
        len(recipients_list) > 1
        and len(amounts_list) > 1
        and len(recipients_list) == len(amounts_list)
    ):
        tx = await wallet_utils.create_transaction_to_send_multiple_wallet(
            private_key, recipients_list, amounts_list, message_bytes
        )
    else:
        receiver = recipients_list[0]
        amount = amounts_list[0]
        tx = await wallet_utils.create_transaction(
            private_key, receiver, amount, message_bytes
        )
    return await push_tx(tx, wallet_utils)  # Ensure this returns the hash
