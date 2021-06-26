# Setting up a github actions runner for public repos using a Raspberry Pi

## The Problem

Self hosted runners are generally not safe for public repositories. When someone makes a pull request, they could inject arbitrary code into your workflow run, possibly gaining root access to the runner. 
This is not a problem for the github-provided runners, as they are only virtual machines that are disposed after each workflow run.

## The Solution

To achieve a similar level of security, we can use Docker images for our self hosted runner. 
The setup in this repository follows the steps outlined in [this article](https://dev.to/wayofthepie/ephemeral-self-hosted-github-actions-runners-1h5m).

## Prerequisites 

- Raspberry Pi 4B or similar arm64 embedded computer 
    - 32bit is not supported; both Docker and arm-gcc-none-eabi require a 64bit OS
    - x86_64 is not (yet?) supported
- Fast micro SD card with at least 32GB

## Generate a personal access token

Spinning up a new runner requires a github access token, which you'd have to get from the github website everytime a runner needs to be started. This would prevent automatically starting a fresh docker container for each workflow run.
Fortunately, github allows to generate these tokens via a web API. This API itself needs a "master token" (aka "personal access token") which we will generate now.

- Open github.com and navigate to  _Account Settings_ > _Developer Settings_ > _Personal Access Tokens_
- Click on "Generate New Token"
- Give the token a name, e.g. `actions-runner-registration` and select all Scopes in the _Repo_ category
- Generate the token and store it somewhere safe. This is the only time you'll see this token.

## Installation on the Raspberry Pi

- Install Ubuntu Server 20.04 (64bit!) on the micro SD card
- Boot into ubuntu, login and change default password to something secure (you'll be prompted to do so)
- Install updates
    - `sudo apt-get update`
    - `sudo apt-get upgrade`
- Install openssh server: `sudo apt-get install openssh-server`
- Check that the ssh server is running: `sudo systemctl status sshd`
- TODO: Add ufw firewall (?)
- You can from now on connect to your Pi over ssh without attaching a keyboard and display
- Download and execute `scripts/raspberryPiSetup.sh` to setup the Pi for running the CI agent in a docker container:
    - `curl -OL https://github.com/TheSlowGrowth/daisyHat/raw/develop/scripts/raspberryPiSetup.sh`
    - `chmod +x raspberryPiSetup.sh`
    - `./raspberryPiSetup.sh`
    - The script will download all required files; install software; setup hooks, etc.
    - You will be prompted to enter some details about the target repository
- After the setup script is done, reboot the Pi
- log in and run `~/daisyHat/startDockerContainer.sh`
    - The script starts the docker container that contains the github actions runner. 
    - Once the script is running, you should see your runner attached to the target github repository.
    - After each CI job, the runner & container will shut down and the script will restart it immediately, ready for the next CI job.

## Details about the installation process

During the installation, several thing will be setup for you. The script will ...

1. ... install system updates
2. ... download additional scripts from this github repo
3. ... request some details about the target repository, such as the user name, repo name and personal access token. These will be stored in `~/daisyHat/setupEnvVars.sh` from where they will be loaded each time you log in
4. ... find out the device major number of the STLinkV3 Programmer. This is required to setup the USB device passthrough into the Docker container. You will be promted to plug in the programmer.
5. ... install some udev rules. 
    - There's a rule that grants user access to the STLinkV3 programmer
    - Two additional rules execute scripts when new USB devices are plugged in. These script are also installed automatically. They will re-attach the new devices to a running docker container so that hot-plugging devices during the container execution is possible. This is required because the devices will constantly be unplugged and re-attached during the test execution.
6. ... install Docker and add the user to the `docker` group (allowing the user to manage docker containers without root priviliges) and the `plugdev` group (allowing it raw access to USB devices)
7. ... download `docker/Dockerfile` and `docker/entrypoint.sh` from this repo and build the final docker image that runs the github actions.
    - The Docker image contains all tools required for daisyHat tests, e.g. CMake, gcc, make, python, openocd, etc.
    - Should your tests require additional software and tools, you can simply modify the Dockerfile and rebuild the container.