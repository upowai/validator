from database.database import r, test_redis_connection
import json
import logging
from tabulate import tabulate
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_and_process_delegates():
    try:
        if not test_redis_connection():
            logging.error("Redis connection is not established.")
            return None

        delegates_list = r.hgetall("delegates_list")
        validator_owner_details = r.hgetall("validator_owner")
    except Exception as e:
        logging.error(f"Error fetching data from Redis: {e}")
        return

    total_balance = 0.0
    table_data = []

    for wallet_address, balance in delegates_list.items():
        try:
            wallet_address = (
                wallet_address.decode("utf-8")
                if isinstance(wallet_address, bytes)
                else wallet_address
            )
            balance = balance.decode("utf-8") if isinstance(balance, bytes) else balance

            total_balance += float(balance)
            table_data.append([wallet_address, balance])
        except ValueError as e:
            logging.error(
                f"Error processing balance for wallet address {wallet_address}: {e}"
            )

    validator_owner_balance = 0.0
    if validator_owner_details:
        try:
            validator_owner = {
                k.decode("utf-8") if isinstance(k, bytes) else k: (
                    v.decode("utf-8") if isinstance(v, bytes) else v
                )
                for k, v in validator_owner_details.items()
            }
            validator_owner_balance = float(validator_owner.get("amount", 0))
            total_balance += validator_owner_balance
            table_data.append(
                [
                    "Validator Owner (" + validator_owner["wallet_address"] + ")",
                    validator_owner_balance,
                ]
            )
        except Exception as e:
            logging.error(f"Error processing validator owner details: {e}")

    print(tabulate(table_data, headers=["Wallet Address", "Balance"], tablefmt="grid"))
    logging.info(
        f"Total balance of all users (excluding validator owner): {total_balance - validator_owner_balance}"
    )
    logging.info(f"Validator owner balance: {validator_owner_balance}")
    logging.info(f"Combined total balance: {total_balance}")


if __name__ == "__main__":
    fetch_and_process_delegates()
