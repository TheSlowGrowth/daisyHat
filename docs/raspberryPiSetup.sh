#!/bin/sh

# remove previous docker installations
sudo apt-get remove -y docker docker-engine docker.io containerd runc

# Install the latest updates for your system: 
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies for the Docker installation: 
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Get Dockers official GPG key: 
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Setup the docker repository: 
echo "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install the docker engine: 
sudo apt-get update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io

# Add a "docker" group and add the current user to this group
sudo groupadd docker
sudo usermod -aG docker $USER
# apply the changes 
newgrp docker

# Start the docker service automatically after booting
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

# Install flask and pip3
sudo apt install -y python3-pip
pip3 install flask

# build the docker image
docker build -t actions-image .
