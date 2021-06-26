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
- a **host-side python library** to upload device firmware images, collect test results and orchestrate tests that involve other hardware,
- **CMake functions** and utilities to create a CMake project that contains multiple daisyHat tests which can be built and run with one command respectively,
- a **Docker image** that can be used to deploy ephemeral github actions runners that are safe to use on public repositories,
- **setup scripts** to prepare and install this Docker image on a Raspberry Pi 4B and turn it into the heart of a automated hardware testbed for github repositories.

**WOKR IN PROGRESS**
This project is in very early stages and not production ready. Don't expect everything to be plug-and-play yet. Please help out where you can!

<!-- Example test -->
# Example test

The simplest test consists of a single firmware image that performs the entire test on a Daisy Seed.
View [more complex example code here](examples/).

firmware.cpp
```cpp
#include <daisy_seed.h>
#include <daisyHat.h>

daisy::DaisySeed seed;

int main()
{
    seed.Configure();
    seed.Init();

    daisyhat::StartTest(seed, "test1");
    int a = 1;
    int b = 1;
    EXPECT_EQ(a, b);
    daisyhat::FinishTest();
}
```
CMakeLists.txt
```
# register the test with CMake.
# This will upload the test to a Daisy Seed and collect the results over USB-Serial
daisyhat_add_test(
    NAME test1
    SOURCES 
        firmware.cpp
)
```

<!-- Getting Started -->
# Getting started

Core concepts:
- tests live in a git repository where daisyHat and libDaisy are available (e.g. as submodules)
- Depending on the test scenario, each test consists of one or multiple firmware images and additional host-side test execution scripts, if needed
- All tests are accumulated into a CMake project so that building and running is entirely handled by CMake
- GitHub actions integration is realised with an ephemeral test runner based on a docker image that can easily be deployed to a Raspberry Pi and is safe to use for public repositories

## Setting up a test project

1. Create a new repository for your tests
2. Add `libDaisy` as a submodule in the `lib/libDaisy` folder
3. Add the **daisyHat** repo as a submodule in the `lib/daisyHat` folder 
4. Add a `CMakeLists.txt` in the repository root that includes `lib/libDaisy` and `lib/daisyHat` as sub directories (with `add_subdirectory()`) (you can copy and edit [this file](examples/CMakeLists.txt))
5. For each test, create a new directory `tests/<testName>` and add to it
    1. The C++ source code for your test firmware (take a look [here](examples/test1/main.cpp))
    2. A `CMakeLists.txt` file that registers a test firmware with the `daisyhat_add_test()` function (you can copy [this file](examples/test1/CMakeLists.txt))
6. Include each of the test directories in the root `CMakeLists.txt`
7. _Future addition_: Describe the hardware configuration of your test setup in the `daisyHat.config.json` at the project root

## Running the tests locally

1. Setup your toolchain with _CMake_, _make_, _gcc-arm-none-eabi_, _openocd_ and _Python3.9_
2. Connect to each Daisy Seed board via USB
3. Connect to each Daisy Seed board via an STLinkv3 JTAG programmer
4. Configure the project: `cmake -D TOOLCHAIN_PREFIX=<path-to-gcc-arm-none-eabi> -D CMAKE_TOOLCHAIN_FILE="lib/libDaisy/cmake/toolchains/stm32h750xx.cmake" -S . -B build -G "Unix Makefiles"`
5. Build libDaisy, daisyHat and the tests: `cmake --build build`
6. Run the tests: `ctest --output-on-failure`

## Running tests automatically via github ations

1. Prepare the target github repository by generating a personal access token to be able to register new github actions runners (see [here](docs/github-actions-runner-setup-public-repos.md))
2. Install Ubuntu Server 20.04 on a Raspberry Pi 4B
3. Download and execute the setup script (see [here](docs/github-actions-runner-setup-public-repos.md)) 
4. Connect the Pi to each Daisy Seed board via USB
5. Connect the Pi to each Daisy Seed board via an STLinkv3 JTAG programmer

Detailed instructions can be found [here](docs/github-actions-runner-setup-public-repos.md). Please note that the setup is currently not fully automated and still work in progress.

<!-- Project Structure -->
# Project Structure

- `cmake/` contains cmake functions
- `docs/` contains documentation and guides
- `docker/` contains files to build the github action runner docker image
- `examples/` contains a usage example with two tests (one succeeds, one fails)
- `python/` contains the python library for the host computer / test runner
- `scripts/` contains scripts to setup and run a daisyHat test runner
- `src/` contains C++ library for the device firmware

<!-- CONTRIBUTING -->
# Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request