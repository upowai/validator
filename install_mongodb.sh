#!/bin/bash

# Install necessary packages
sudo apt install software-properties-common gnupg apt-transport-https ca-certificates -y

# Add the MongoDB GPG key
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Add the MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update your package list
sudo apt update

# Install MongoDB
sudo apt install mongodb-org -y

# Start and enable MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Check MongoDB service status
sudo systemctl status mongod

# Display MongoDB version
mongod --version
