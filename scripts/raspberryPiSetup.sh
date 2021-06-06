#!/bin/bash

##############################################################
# update system
##############################################################

echo "########################################################"
echo "Updating system..."
echo "########################################################"

sudo apt-get update < "/dev/null"
sudo apt-get upgrade -y < "/dev/null"

##############################################################
# setup envorinment
##############################################################

echo "########################################################"
echo "Setting up environment"
echo "########################################################"

# install curl...
sudo apt-get install -y curl < "/dev/null"

# download the env var file
mkdir ~/daisyHat
cd ~/daisyHat
curl -OL https://github.com/TheSlowGrowth/daisyHat/raw/develop/scripts/setupEnvVars.sh
chmod +x setupEnvVars.sh

# prompt user for repo name, user name and github token
read -p "Enter github repo name:" REPO_NAME
read -p "Enter github user name:" USER_NAME
read -p "Enter github personal access token:" GH_TOKEN

# read device ID for the programmer chip
read -p "Plug in the JTAG programmer, then press Enter" tmp
lsusb 
read -p "Enter the bus and device numbers of the programmer, as shown above (format: [bus/device], e.g. 001/003) :" PROGRAMMER_PATH
# extract the major number with a regex
USB_DEVICE_MAJOR=$(ls -l /dev/bus/usb/${PROGRAMMER_PATH} | sed "s/^.*root root \([0-9]*\), .*$/\1/")
echo "Extracted device major number: ${USB_DEVICE_MAJOR}" 

# write these to setupEnvVars.sh
echo "# Appended from rapsberryPiSetup.sh:" >> setupEnvVars.sh
echo "DAISYHAT_REPO=${REPO_NAME}" >> setupEnvVars.sh
echo "DAISYHAT_USER=${USER_NAME}" >> setupEnvVars.sh
echo "DAISYHAT_GH_TOKEN=${GH_TOKEN}" >> setupEnvVars.sh
echo "DAISYHAT_DEVICE_MAJOR=${USB_DEVICE_MAJOR}" >> setupEnvVars.sh
# source this file now
source ./setupEnvVars.sh
# include this file with every bash session
echo "# include daisyhat environment if it exists" >> $HOME/.bash_profile
echo "if [ -f $HOME/daisyHat/setupEnvVars.sh ]; then" >> $HOME/.bash_profile
echo "    source $HOME/daisyHat/setupEnvVars.sh" >> $HOME/.bash_profile
echo "fi" >> $HOME/.bash_profile

# download the docker startup script
curl -OL https://github.com/TheSlowGrowth/daisyHat/raw/develop/scripts/startDockerContainer.sh
chmod +x startDockerContainer.sh

cd

echo "########################################################"
echo "Setting up udev rules"
echo "########################################################"

cd ~/daisyHat

# download the script that will automatically attach new usb devices to the running container
curl -OL https://github.com/TheSlowGrowth/daisyHat/raw/develop/scripts/daisyHatUsbAttach.py
chmod +x daisyHatUsbAttach.py

# download the script that will automatically attach new tty devices to the running container
curl -OL https://github.com/TheSlowGrowth/daisyHat/raw/develop/scripts/daisyHatTtyAttach.sh
chmod +x daisyHatTtyAttach.sh

# install udev rule to attach devices that match the major number to the docker container
USB_ATTACH_SCRIPT=$(pwd)/daisyHatUsbAttach.py
UDEV_RULE_FILE=/etc/udev/rules.d/99-daisyHatUsbPassthrough.rules
sudo rm -R ${UDEV_RULE_FILE}
echo "ACTION==\"add\", SUBSYSTEM==\"usb\", RUN+=\"${USB_ATTACH_SCRIPT}\"" | sudo tee ${UDEV_RULE_FILE} > /dev/null

USB_ATTACH_SCRIPT=$(pwd)/daisyHatTtyAttach.sh
UDEV_RULE_FILE=/etc/udev/rules.d/100-daisyHatTtyPassthrough.rules
sudo rm -R ${UDEV_RULE_FILE}
echo -e "ACTION==\"add\", SUBSYSTEM==\"tty\", RUN+=\"${USB_ATTACH_SCRIPT} 'added' '%E{DEVNAME}' '%M' '%m'\"\nACTION==\"remove\", SUBSYSTEM==\"tty\", RUN+=\"${USB_ATTACH_SCRIPT} 'removed' '%E{DEVNAME}' '%M' '%m'\"" | sudo tee ${UDEV_RULE_FILE} > /dev/null

sudo service udev restart

# install udev rule for stlinkv3
curl -OL https://github.com/TheSlowGrowth/daisyHat/raw/develop/docker/49-stlinkv3.rules
mkdir -p /etc/udev/rules.d/
sudo mv 49-stlinkv3.rules /etc/udev/rules.d/49-stlinkv3.rules
sudo service udev restart

cd

##############################################################
# install docker
##############################################################

echo "########################################################"
echo "Installing docker"
echo "########################################################"

# remove previous docker installations
sudo apt-get remove -y docker docker-engine docker.io containerd runc < "/dev/null"

# Install dependencies for the Docker installation: 
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release < "/dev/null"

# Get Dockers official GPG key: 
DOCKER_KEYRING_FILE=/usr/share/keyrings/docker-archive-keyring.gpg
sudo rm -f ${DOCKER_KEYRING_FILE}
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o ${DOCKER_KEYRING_FILE}

# Setup the docker repository: 
echo "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install the docker engine: 
sudo apt-get update < "/dev/null"
sudo apt-get install -y docker-ce docker-ce-cli containerd.io < "/dev/null"

echo "Adding user '${USER}' to the 'docker' group"

# Add a "docker" group and add the current user to this group
if [ $(getent group docker) ]; then
    sudo usermod -aG docker $USER
else
    sudo groupadd docker
    sudo usermod -aG docker $USER
fi

# Start the docker service automatically after booting
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

# Install flask and pip3
# TODO: Is this still needed?
sudo apt install -y python3-pip < "/dev/null"
pip3 install flask

##############################################################
# build the docker image
##############################################################

echo "########################################################"
echo "Building docker image"
echo "########################################################"

mkdir -p ~/daisyHat/docker
cd ~/daisyHat/docker 

# download Dockerfile and entrypoint
curl -OL https://github.com/TheSlowGrowth/daisyHat/raw/develop/docker/Dockerfile
curl -OL https://github.com/TheSlowGrowth/daisyHat/raw/develop/docker/entrypoint.sh
chmod +x entrypoint.sh
curl -OL https://github.com/TheSlowGrowth/daisyHat/raw/develop/docker/49-stlinkv3.rules

# build the docker image.
# We haven't logged out and back in again, so the new "docker" group permissions
# aren't applied to the current user yet (at least not in this shell session).
# To run the command with the new group permissions, we use use "sudo" which
# will create a new shell (that has the correct permissions).
sudo -u $USER docker build -t ${DAISYHAT_DOCKER_IMAGE} .

cd

echo "Done!"
