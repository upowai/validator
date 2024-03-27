# Upow Validator Node

Welcome to the Upow Validator Node repository. This repository contains the code and configuration necessary for running a validator node within the Upow blockchain network. Validators are essential to the Upow ecosystem, ensuring the integrity and proper functioning of inodes and minerpools by validating jobs, setting emission rates, and scoring minerpools.

## Prerequisites

Before setting up the Validator Server, ensure you have the following installed:

- Python 3.10 or higher
- MongoDB
- Redis (See the "Installing Redis" section below for installation instructions)
- Required Python libraries (listed in `requirements.txt`)

## Configuration

Before you start, ensure you have correctly set up your environment. The `config.py` file contains essential settings that you must review and configure according to your setup.

Please check envExample file to set `.env`

## Enable port for accepting connections (Ubuntu)

```bash
  sudo ufw allow 5503
```

### Inode Configuration

- `INODE_IP`: The IP address of the inode server.
- `INODE_PORT`: The port on which the inode server is running.
- `INODE_BUFFER`: Buffer size for inode communications. Default is `1024`.
- `PRIVATEKEY`: Your validator node's private key.
- `API_URL`: The URL of the API server.
- `TRACK`: The starting block height for processing.
- `CORE_URL`: The URL of the node.

### Validator Configuration

- `VALIDATOR_IP`: The IP address for the validator node.
- `VALIDATOR_PORT`: The port for the validator node.
- `CHECK_INTERVAL`: Time interval (in seconds) for checking new transactions.
- `VALIDATOR_WALLET_ADDRESS`: Your validator wallet address.
- `VALIDATOR_REWARD_WALLET_ADDRESS`: The wallet address for distributing Validator Fee. (18%)
- `FAST_API_URL`: The host address for FastAPI.
- `FAST_API_PORT`: The port for FastAPI.

## Installing Redis

To ensure Redis is installed and properly configured on your system, you can use the `install_redis.sh` script. Follow these steps for your operating system:

### macOS and Ubuntu

1. **Make the Script Executable:**

   - Open a terminal and navigate to the directory containing the `install_redis.sh` script.
   - Run the command `chmod +x install_redis.sh` to make the script executable.

2. **Run the Script:**
   - Execute the script by running `./install_redis.sh` in the terminal.
   - If necessary, the script will ask for your password to grant permission for installation steps that require superuser access.

The script will check if Redis is already installed on your system and proceed with the installation if it is not. It also ensures that Redis is set to start on boot.

## Installing Mongodb

To Install Mongodb on Ubuntu you can use the `install_mongodb.sh` script.

### Ubuntu

1. **Make the Script Executable:**

   - Open a terminal and navigate to the directory containing the `install_mongodb.sh` script.
   - Run the command `chmod +x install_mongodb.sh` to make the script executable.

2. **Run the Script:**
   - Execute the script by running `./install_mongodb.sh` in the terminal.
   - If necessary, the script will ask for your password to grant permission for installation steps that require superuser access.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/upowai/validator.git
   ```

2. **Navigate to the Project Directory:**

   ```bash
   cd validator
   ```

3. **Install Dependencies:**

   ```bash
   pip3 install -r requirements.txt
   ```

4. **Review and update the `config.py` file with your specific settings.**

5. **Configure MongoDB and Redis:**

   - Ensure MongoDB and Redis are running on your system.
   - Update the MongoDB connection URL and database details in `database/mongodb.py` if necessary.

6. **Set Up Environment Variables:**
   - Set up environment variables for configuration parameters.

## Running the Validator

To start

the validator node, navigate to the repository's root directory and execute the following command:

```bash
python3 validator.py
```

This command starts the FastAPI server and initializes the validator node, allowing it to begin processing transactions and performing its duties within the Upow network.

## API Endpoints

The validator node provides several API endpoints for interaction:

- `/get_balance/`: Retrieve the balance of a given wallet address.
- `/get_balance_validatorowner/`: Get the balance of the validator owner.
- `/deduct_balance/`: Deduct a specified amount from a wallet.
- `/validatorowner_deduct_balance/`: Deduct a specified amount from the validator owner's balance.

These endpoints are accessible via HTTP GET and POST requests to the FastAPI server running on `FAST_API_URL:FAST_API_PORT`.

## Maintaining the Node

It's crucial to regularly check the logs for any errors or unusual activity. The validator node plays a vital role in the Upow network, and its continuous, error-free operation is essential for the network's health.

## Security

Ensure your validator's private key is securely stored and not exposed to unauthorized individuals. Regularly update your software to the latest version to mitigate security vulnerabilities.
