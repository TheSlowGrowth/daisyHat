#!/bin/bash

DAISYHAT_DOCKER_IMAGE="actions-image" # name of the daisyhat docker image
DAISYHAT_CONTAINER_NAME="daisyhat-container" # desired name of the docker container
DAISYHAT_RUNNER_NAME="daisyhat-runner" # desired name of the github actions runner

# Uncomment these or add new lines below:
# DAISYHAT_DEVICE_MAJOR=189 # major device number of devices to passthrough to the container
# DAISYHAT_REPO="daisyhat_Examples" # the github repo to connect to
# DAISYHAT_USER="TheSlowGrowth" # the github username
# DAISYHAT_GH_TOKEN="" # the github access token that allows to add/remove runners