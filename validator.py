import socket
import threading
import json
import asyncio
import websockets
from websockets.exceptions import WebSocketException
import utils.config as config
import logging
import time
from datetime import datetime
import sys
from pydantic import BaseModel
from datetime import datetime, timedelta, date
from fastapi import FastAPI, HTTPException, Query, Request, Depends
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from database.database import r
from database.mongodb import test_db_connection
from database.database import test_redis_connection
from api.api_client import test_api_connection
from dotenv import load_dotenv
import os

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


dotenv_path = ".env"
load_dotenv(dotenv_path)

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

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_fastapi():
    uvicorn.run(app, host=config.FAST_API_URL, port=config.FAST_API_PORT)


from transactions.transactionBatch import (
    process_all_transactions,
    add_transaction_to_batch,
)

from transactions.fetchBlock import (
    process_transactions,
    get_balance_from_wallet,
    get_balance_validatorowner,
    deduct_balance_from_wallet,
    deduct_balance_from_validatorowner,
    get_delegates_TransactionsPushed,
)


logging.basicConfig(level=logging.INFO)


class MessageType:
    VALIDATEMODEL = "validateModel"
    UPDATEINFO = "updateInfo"
    SETCONFIG = "setConfig"
    UPDATEMODEL = "updateModel"


class DeductBalanceRequest(BaseModel):
    wallet_address: str
    amount_to_deduct: float


class DeductBalanceValidator(BaseModel):
    amount_to_deduct: float


@app.get("/get_balance/")
@limiter.limit("10/minute")
async def get_balance(wallet_address: str, request: Request):
    if not wallet_address:
        raise HTTPException(status_code=400, detail="Wallet address must be provided")

    balance = get_balance_from_wallet(wallet_address)
    if isinstance(balance, str) and balance.startswith("Error"):

        raise HTTPException(
            status_code=404 if "not found" in balance else 400, detail=balance
        )
    return {"balance": balance}


@app.get("/get_balance_validatorowner/")
@limiter.limit("10/minute")
async def poolowner_get_balance(request: Request):

    balance = get_balance_validatorowner()
    if isinstance(balance, str) and balance.startswith("Error"):

        raise HTTPException(
            status_code=404 if "not found" in balance else 400, detail=balance
        )

    return {"balance": balance}


@app.post("/deduct_balance/")
@limiter.limit("10/minute")
async def deduct_balance(
    request: Request,
    deduct_request: DeductBalanceRequest,
):
    result, response = deduct_balance_from_wallet(
        deduct_request.wallet_address, deduct_request.amount_to_deduct
    )
    if result is None:
        raise HTTPException(status_code=400, detail=response)
    else:
        add_transaction_to_batch(
            deduct_request.wallet_address, response, "Delegate_deduct_balance"
        )
        return {"message": f"Amount deducted successfully: {response}"}


@app.post("/validatorowner_deduct_balance/")
@limiter.limit("10/minute")
async def poolowner_deduct_balance(
    request: Request,
    deduct_request: DeductBalanceValidator,
):
    result, response, wallet_address = deduct_balance_from_validatorowner(
        deduct_request.amount_to_deduct
    )
    if result is None:
        raise HTTPException(status_code=400, detail=response)
    else:
        add_transaction_to_batch(
            wallet_address, response, "validator_owner_deduct_balance"
        )
        return {"message": f"Amount deducted successfully: {response}"}


@app.get("/latestwithdraws/")
@limiter.limit("10/minute")
async def latest_withdraws(wallet_address: str, request: Request):
    if not wallet_address:
        raise HTTPException(status_code=400, detail="Wallet address must be provided")

    result = get_delegates_TransactionsPushed(wallet_address)

    if not result.get("success", False):
        message = result.get("message", "An unexpected error occurred")
        status_code = 404 if "No details found" in message else 500
        raise HTTPException(status_code=status_code, detail=message)
    return result.get("data", {})


def send_data_to_inode(
    job_id, miner_pool_wallet, validator_wallet, job_details, message_type
):
    try:
        if message_type == MessageType.VALIDATEMODEL:
            data = {
                "type": message_type,
                "content": {
                    "job_id": job_id,
                    "miner_pool_wallet": miner_pool_wallet,
                    "validator_wallet": validator_wallet,
                    "job_details": job_details,
                },
            }
        else:
            raise ValueError("Invalid message type")

        serialized_data = json.dumps(data)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client.connect((config.INODE_IP, config.INODE_PORT))
            client.send(serialized_data.encode("utf-8"))
            response = client.recv(config.INODE_BUFFER).decode("utf-8")
        finally:
            client.close()

        return response

    except json.JSONDecodeError as e:

        print(f"Error serializing data: {e}")
        return None
    except socket.error as e:

        print(f"Socket error: {e}")
        return None
    except ValueError as e:

        print(e)
        return None
    except Exception as e:

        print(f"An unexpected error occurred: {e}")
        return None


def send_update_info(ip, port, wallet_address, message_type):
    try:
        current_time = datetime.utcnow().isoformat()

        if message_type == MessageType.SETCONFIG:
            data = {
                "type": MessageType.SETCONFIG,
                "content": {
                    "ip": ip,
                    "port": port,
                    "ping": current_time,
                    "wallet_address": wallet_address,
                },
            }
        else:
            raise ValueError("Invalid message type")

        serialized_data = json.dumps(data)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((config.INODE_IP, config.INODE_PORT))
            client.send(serialized_data.encode("utf-8"))
            response = client.recv(config.INODE_BUFFER).decode("utf-8")

            return response

    except json.JSONDecodeError as e:
        print(f"Error serializing data: {e}")
    except socket.error as e:
        print(f"Socket error: {e}")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


async def handle_client(websocket, path):
    try:
        async for message in websocket:
            try:
                parsed_message = json.loads(message)
                message_type = parsed_message.get("type")

                if message_type == "validateModel":
                    job_id = parsed_message.get("job_id")
                    miner_pool_wallet = parsed_message.get("miner_pool_wallet")
                    # print("miner_pool_wallet", miner_pool_wallet)
                    validator_wallet = config.VALIDATOR_WALLET_ADDRESS
                    job_details = parsed_message.get("job_details")

                    message_to_send = json.dumps(
                        {
                            "job_id": job_id,
                            "validator_wallet": validator_wallet,
                            "type": MessageType.UPDATEMODEL,
                        }
                    )
                    response = send_data_to_inode(
                        job_id,
                        miner_pool_wallet,
                        validator_wallet,
                        job_details,
                        message_type,
                    )

                    await websocket.send(message_to_send)
                    logging.info(f"Response: {response}")

            except json.JSONDecodeError:
                await websocket.send("Invalid message format")
            except Exception as e:
                logging.error(f"Error processing message: {e}")
                await websocket.send("Error processing message")

    except WebSocketException as e:
        logging.warning(f"WebSocket error: {e}")
    except asyncio.CancelledError:
        logging.info("Client connection handling cancelled.")
    except Exception as e:
        logging.error(f"handle_client Unexpected error: {e}")
    finally:
        logging.info("Client disconnected or connection handling stopped.")


async def periodic_update():
    while True:
        send_update_info(
            config.VALIDATOR_IP,
            config.VALIDATOR_PORT,
            config.VALIDATOR_WALLET_ADDRESS,
            MessageType.SETCONFIG,
        )
        # print("Validator ping")
        await asyncio.sleep(60)


async def main():
    update_task = asyncio.create_task(periodic_update())
    stop = asyncio.Future()
    balance_thread = threading.Thread(target=update_balance_periodically, daemon=True)
    fastapi_thread = threading.Thread(daemon=True, target=run_fastapi)
    periodic_task = threading.Thread(target=periodic_process_transactions, daemon=True)
    fastapi_thread.start()
    balance_thread.start()
    periodic_task.start()
    server = await websockets.serve(
        handle_client, config.VALIDATOR_IP, config.VALIDATOR_PORT
    )
    await stop
    server.close()
    await server.wait_closed()
    logging.info("Server shut down successfully.")
    update_task.cancel()
    try:
        await update_task
    except asyncio.CancelledError:
        logging.info("Periodic update task cancelled.")


def update_balance_periodically():
    try:
        while True:
            process_all_transactions()
            time.sleep(60)
    except Exception as e:
        logging.error(f"Error in update_balance_periodically: {e}")


def periodic_process_transactions():
    try:
        while True:
            process_transactions()
            time.sleep(config.CHECK_INTERVAL)
    except Exception as e:
        logging.error(f"Error in periodic_process_transactions: {e}")


if __name__ == "__main__":
    if not test_db_connection():
        logging.error("Failed to establish MongoDB connection. Exiting...")
        sys.exit(1)
    if not test_redis_connection():
        logging.error("Failed to establish Redis connection. Exiting...")
        sys.exit(2)
    if not test_api_connection(config.API_URL):
        logging.error("Failed to establish API connection. Exiting...")
        sys.exit(3)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down Validator due to KeyboardInterrupt.")
