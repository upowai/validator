import time
import requests
from database.database import r, test_redis_connection
import logging

logging.basic_config(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

API_URL = "http://0.0.0.0:8002"  # Change this to your actual API URL
DEDUCT_ENDPOINT = "/deduct_balance/"


def fetch_and_process_delegates():
    try:
        if not test_redis_connection():
            logging.error("Redis connection is not established.")
            return []

        delegates_list = r.hgetall("delegates_list")
    except Exception as e:
        logging.error(f"Error fetching data from Redis: {e}")
        return []

    eligible_delegates = []

    for wallet_address, balance in delegates_list.items():
        try:
            wallet_address = (
                wallet_address.decode("utf-8")
                if isinstance(wallet_address, bytes)
                else wallet_address
            )
            balance = balance.decode("utf-8") if isinstance(balance, bytes) else balance

            if float(balance) > 1.0:
                eligible_delegates.append((wallet_address, float(balance)))
        except ValueError as e:
            logging.error(
                f"Error processing balance for wallet address {wallet_address}: {e}"
            )

    return eligible_delegates


def deduct_balance(wallet_address, amount):
    payload = {"wallet_address": wallet_address, "amount_to_deduct": amount}
    response = requests.post(API_URL + DEDUCT_ENDPOINT, json=payload)
    return response.json()


def main():
    while True:
        eligible_delegates = fetch_and_process_delegates()

        if not eligible_delegates:
            logging.info("No delegates found with a balance greater than 1.")
        else:
            for wallet_address, balance in eligible_delegates:
                amount_to_deduct = balance - 1  # Deducting amount to bring balance to 1
                result = deduct_balance(wallet_address, amount_to_deduct)
                logging.info(
                    f"Deducted {amount_to_deduct} from {wallet_address}: {result}"
                )
                time.sleep(30)  # 30 seconds delay between each API call

        time.sleep(60)  # 60 seconds delay before next fetch


if __name__ == "__main__":
    main()
