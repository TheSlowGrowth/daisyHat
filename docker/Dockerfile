FROM ubuntu:21.04

ENV RUNNER_VERSION=2.278.0
ENV RUNNER_PLATFORM=arm64
ENV GCC_ARM_NONE_EABI_DOWNLOAD=https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2020q2/gcc-arm-none-eabi-9-2020-q2-update-aarch64-linux.tar.bz2
ENV GCC_ARM_NONE_EABI_FILE=gcc-arm-none-eabi-9-2020-q2-update-aarch64-linux.tar.bz2
ENV GCC_ARM_NONE_EABI_PATH=/home/actions/dev/gcc-arm-none-eabi-9-2020-q2-update

RUN useradd -m actions \
    && apt-get update \
    && apt-get install -y \
    wget curl jq

# must be installed non interactively, otherwise it fails later
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
# add kitware repository (+ signing keys) for a more recent version of cmake 
RUN apt-get install -y apt-transport-https ca-certificates gnupg software-properties-common \
    && wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null \
    && apt-add-repository 'deb https://apt.kitware.com/ubuntu/ focal main' \
    && apt-get update
# install build tools
RUN apt-get install -y make cmake python3 openocd git python3-pip
# install python modules
RUN pip3 install pyserial
#install gcc-arm-none-eabi locally
RUN cd /home/actions && mkdir dev && cd dev && wget ${GCC_ARM_NONE_EABI_DOWNLOAD} && tar xf ./${GCC_ARM_NONE_EABI_FILE}

# install the github actions runner
RUN cd /home/actions && mkdir actions-runner && cd actions-runner \
    && wget https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_PLATFORM}-${RUNNER_VERSION}.tar.gz \
    && tar xzf ./actions-runner-linux-${RUNNER_PLATFORM}-${RUNNER_VERSION}.tar.gz
WORKDIR /home/actions/actions-runner
RUN chown -R actions ~actions && /home/actions/actions-runner/bin/installdependencies.sh

# install udev and setup udev rules for ST-Link V3
RUN apt-get update && apt-get install -y udev usbutils
RUN mkdir -p /etc/udev/rules.d/
COPY 49-stlinkv3.rules /etc/udev/rules.d/49-stlinkv3.rules
RUN service udev restart

# install tini
RUN apt-get update && apt-get install tini

USER actions

COPY entrypoint.sh .
# use tini to be able to stop the container gracefully
ENTRYPOINT ["tini", "-v", "--", "./entrypoint.sh"]
