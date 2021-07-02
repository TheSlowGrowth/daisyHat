#!/bin/bash

export DAISYHAT_DOCKER_IMAGE="actions-image" # name of the daisyhat docker image
export DAISYHAT_CONTAINER_NAME="daisyhat-container" # desired name of the docker container
export DAISYHAT_RUNNER_NAME="daisyhat-runner" # desired name of the github actions runner

# Uncomment these or add new lines below:
# export DAISYHAT_DEVICE_MAJOR=189 # major device number of devices to passthrough to the container
# export DAISYHAT_REPO="daisyhat_Examples" # the github repo to connect to
# export DAISYHAT_USER="TheSlowGrowth" # the github username
# export DAISYHAT_GH_TOKEN="" # the github access token that allows to add/remove runners

