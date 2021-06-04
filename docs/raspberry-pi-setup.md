# Setting up a Rapsberry Pi CI agent for daisyHat

## Prerequisites 

- Raspberry Pi 4B
- Fast micro SD card with at least 32GB

## Installation

- Install Ubuntu Server 20.04 (64bit!) on the micro SD card
- Boot into ubuntu, login and change default password to something secure (you'll be prompted to do so)
- Install updates
    - `sudo apt-get update`
    - `sudo apt-get upgrade`
- Install openssh server: `sudo apt-get install openssh-server`
- Check that the ssh server is running: `sudo systemctl status sshd`
- TODO: Add ufw firewall
- You can from now on connect to your Pi over ssh without attaching a keyboard and display
- Download and execute docs/raspberryPiSetup.sh to setup the Pi for running the CI agent in a docker container

# Run the python flask app that spins up / shuts down the docker container
- `export GITHUB_RUNNER_TOKEN=<youtTokenHere>`
- `export FLASK_APP=daisyHatDockerOrchestrator`
- `export FLASK_ENV=development`
- `python3 -m flask run --host=0.0.0.0`
- visit `http//<yourRaspberryPiIp>:5000/start` to start the docker container
- a runner should now be coming online in github. It auto shuts down after each workflow run.
- visit `http//<yourRaspberryPiIp>:5000/stop` to force-quit any running docker containers

