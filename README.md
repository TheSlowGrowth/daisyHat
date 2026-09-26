<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/TheSlowGrowth/daisyHat">
    <img width=15% src="docs/images/banner.png" alt="Logo">
  </a>

  <h3 align="center">daisyHat</h3>

  <p align="center">
    A framework for automated testing on <a href="https://github.com/electro-smith/libDaisy">Electro Smith Daisy</a> (or similar) hardware
    <br />
    <a href="https://github.com/TheSlowGrowth/daisyHat/tree/develop/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/TheSlowGrowth/daisyHat/tree/develop/examples">View Example Code</a>
    ·
    <a href="https://github.com/TheSlowGrowth/daisyHat/issues">Report Bugs</a>
    ·
    <a href="https://github.com/TheSlowGrowth/daisyHat/issues">Request Features</a>
    <br />
    <br />
    <!-- Shields and links -->
    <a href="https://github.com/TheSlowGrowth/daisyHat/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/TheSlowGrowth/daisyHat.svg" alt="Contributors">
    </a>
    <a href="https://github.com/TheSlowGrowth/daisyHat/network/members">
    <img src="https://img.shields.io/github/forks/TheSlowGrowth/daisyHat.svg" alt="Forks">
    </a>
    <a href="https://github.com/TheSlowGrowth/daisyHat/stargazers">
    <img src="https://img.shields.io/github/stars/TheSlowGrowth/daisyHat.svg" alt="Stars">
    </a>
    <a href="https://github.com/TheSlowGrowth/daisyHat/issues">
    <img src="https://img.shields.io/github/issues/TheSlowGrowth/daisyHat.svg" alt="Issues">
    </a>
    <a href="https://github.com/TheSlowGrowth/daisyHat/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/TheSlowGrowth/daisyHat.svg" alt="License">
    </a>

  </p>
</p>

<!-- ABOUT THE PROJECT -->
# About The Project

**daisyHat** aims to provide a framework for writing and executing automated tests for embedded hardware, with premium support for the <a href="https://github.com/electro-smith/libDaisy">Electro Smith Daisy platform</a>. Tests can be run locally or in github actions and cover a wide range of test scenarios from simple one-device tests to complex hardware setups including custom measurement equipment and test fixtures.

**daisyHat** provides ...
- a **device-side C++ library** that comes with assertion macros, flow control and other tooling to write tests on the hardware,
- a **host-side python package** (`daisyhat`) with a CLI to build the test firmware, upload firmware images to the hardware, collect test results and orchestrate the test run,
- a **Docker image** that can be used to deploy ephemeral github actions runners that are safe to use on public repositories,
- **setup scripts** to prepare and install this Docker image on a Raspberry Pi 4B and turn it into the heart of a automated hardware testbed for github repositories.

**WORK IN PROGRESS**
This project is in very early stages and not production ready. Don't expect everything to be plug-and-play yet. Please help out where you can!

<!-- Example test -->
# Example test

The simplest test consists of a single firmware image that performs the entire test on a Daisy Seed.
View [more complex example code here](examples/).

main.cpp
```cpp
#include <daisy_seed.h>
#include <daisyHat.h>

daisy::DaisySeed seed;

int main()
{
    seed.Configure();
    seed.Init();

    daisyhat::Init(seed, "test1");
    int a = 1;
    int b = 1;
    EXPECT_EQ(a, b);
    daisyhat::FinishTest();
}
```
CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.20)
project (test1)

# register the firmware with the libDaisy CMake firmware target
set(FIRMWARE_NAME test1)
set(FIRMWARE_SOURCES main.cpp)
include(${LIBDAISY_DIR}/cmake/DaisyDefaultBuild.cmake)

# link the daisyHat test library
add_subdirectory(${DAISYHAT_DIR} daisyhat)
target_link_libraries(${FIRMWARE_NAME} PRIVATE daisyHat)
```

<!-- Getting Started -->
# Getting started

Core concepts:
- Tests live in a directory (the **test root**), typically a git repository, that contains a `tests/` subdirectory and a `daisyHat.config.json` file describing the hardware setup
- Each test is a subdirectory of `tests/` that contains a `CMakeLists.txt` making it a standalone CMake project
- libDaisy and daisyHat are available to the test projects via the environment variables `LIBDAISY_DIR` and `DAISYHAT_DIR` (e.g. pointing at checkouts / submodules inside the repository)
- The `daisyhat` python package builds each test with CMake and runs the firmware on the hardware
- GitHub actions integration is realised with an ephemeral test runner based on a docker image that can easily be deployed to a Raspberry Pi and is safe to use for public repositories

## Setting up a test project

1. Create a new repository for your tests
2. Add `libDaisy` as a submodule (e.g. in `lib/libDaisy`)
3. Add the **daisyHat** repo as a submodule (e.g. in `lib/daisyHat`)
4. Add a `daisyHat.config.json` at the repository root that describes your hardware setup (you can copy and edit [this file](examples/daisyHat.config.json))
5. For each test, create a new directory `tests/<testName>` and add to it
    1. The C++ source code for your test firmware (take a look [here](examples/tests/test1/main.cpp))
    2. A `CMakeLists.txt` file (you can copy and edit [this file](examples/tests/test1/CMakeLists.txt))
6. Create a `.env` file at the repository root with the paths your tests need to build (see [.env.example](.env.example))

## Running the tests locally

1. Setup your toolchain: _CMake_, _make_, _gcc-arm-none-eabi_ (as `TOOLCHAIN_PREFIX`), _openocd_ and _Python3_
2. Install the daisyHat python package: `pip install <path-to-daisyHat>`
3. Connect each Daisy Seed board via USB and via an STLink JTAG programmer
4. Build and run the tests: `daisyhat test <path-to-test-root>`
   - `daisyhat build <path-to-test-root>` builds without running
   - `daisyhat clean <path-to-test-root>` removes the test build directories
   - `daisyhat test <path-to-test-root> --list` shows the discovered tests
5. _Future addition_: Host-side orchestration hooks per test (`daisyHatTest.py`)

## Running tests automatically via github actions

1. Prepare the target github repository by generating a personal access token to be able to register new github actions runners (see [here](docs/github-actions-runner-setup-public-repos.md))
2. Install Ubuntu Server 20.04 on a Raspberry Pi 4B
3. Download and execute the setup script (see [here](docs/github-actions-runner-setup-public-repos.md))
4. Connect the Pi to each Daisy Seed board via USB
5. Connect the Pi to each Daisy Seed board via an STLinkv3 JTAG programmer

Detailed instructions can be found [here](docs/github-actions-runner-setup-public-repos.md). Please note that the setup is currently not fully automated and still work in progress.

<!-- Project Structure -->
# Project Structure

- `daisyhat/` contains the python package (CLI, build & test orchestration, host-side runner)
- `src/` contains the C++ library for the device firmware
- `docker/` contains files to build the github action runner docker image
- `examples/` contains a usage example (a test root with two tests; one succeeds, one fails)
- `scripts/` contains scripts to setup and run a daisyHat test runner
- `docs/` contains documentation and guides

<!-- CONTRIBUTING -->
# Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
