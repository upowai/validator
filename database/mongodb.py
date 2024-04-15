from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import utils.config as config

def test_db_connection():
    try:
        client = MongoClient(
            config.MONGO_DB, serverSelectionTimeoutMS=5000
        )

        client.admin.command("ping")
        print("MongoDB connection established successfully.")
        return True
    except ConnectionFailure:
        print("Failed to connect to MongoDB.")
        return False


def get_db_connection():
    client = MongoClient(config.MONGO_DB)
    return client.validator


# Initialize the connection
db = get_db_connection()
validatorProcessedTransaction = db.validatorProcessedTransaction
validatorTransactionsCollection = db.validatorTransactionsCollection
validatorTransactionsPushed = db.validatorTransactionsPushed
validatorBalanceUpdateData = db.validatorBalanceUpdateData
errorTransaction = db.errorTransaction
catchTransaction = db.catchTransaction
pushHistory = db.pushHistory