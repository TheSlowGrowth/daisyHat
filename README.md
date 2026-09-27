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

# Core concepts

- Tests live in a directory (the **test root**), typically a git repository, that contains a `tests/` subdirectory and a `daisyHat.config.json` file describing the hardware setup
- Each test is a subdirectory of `tests/` that contains a `CMakeLists.txt` making it a standalone CMake project
- libDaisy and daisyHat are available to the test projects via the environment variables `LIBDAISY_DIR` and `DAISYHAT_DIR` (e.g. pointing at checkouts / submodules inside the repository)
- The `daisyhat` python package builds each test with CMake and runs the firmware on the hardware
- A test can optionally provide a `daisyHatTest.py` with host-side orchestration hooks (flash firmware to specific seeds, multi-firmware tests, host-only tests)
- GitHub actions integration is realised with an ephemeral test runner based on a docker image that can easily be deployed to a Raspberry Pi and is safe to use for public repositories


The layout of a test root:

```
<test-root>/
├── daisyHat.config.json   # hardware setup (seed identifiers, ...)
└── tests/
    ├── test1/            # a test: standalone CMake project
    │   ├── CMakeLists.txt
    │   ├── daisyHatTest.py   # (optional) host-side orchestration hooks
    │   └── main.cpp
    └── test2/
        └── ...
```

<!-- Example test -->
# Example test

The simplest test consists of a single firmware image that performs the entire test on a Daisy Seed.
View [more complex example code here](examples/).

In this repository, `examples/` is a test root containing one test, `test1`.

`examples/daisyHat.config.json` describes the hardware setup. The example defines one Daisy Seed with the identifier `Alice`:

```json
{
    "version": 1,
    "seeds": {
        "Alice": {
            "flash": {
                "backend": "pyocd"
            },
            "serialDevice": "/dev/serial/by-id/usb-Electrosmith_Daisy_Seed_Built_In_346135793139-if00"
        }
    }
}
```

`examples/tests/test1/main.cpp`:
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
`examples/tests/test1/CMakeLists.txt`:
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

Run the test from the test root's parent directory (here: the repository root, where the `.env` file is). The first argument is the path to the test root folder (`examples` here — for your own projects it is typically `.` for the repository root), the second argument names the test to run (omit it to run all discovered tests):

```
daisyhat test <path-to-test-root> [test_name ...]
daisyhat test examples test1
```

Expected output (CMake and flashing output elided):

```
INFO: daisyHat config file path: examples/daisyHat.config.json
 ... configuring 'test1'
 ... building 'test1'

========== test 'test1' ==========

-----------------------------------------------------------------------
Flashing firmware images
-----------------------------------------------------------------------

 ... flashing to 'Alice': 'examples/tests/test1/.build/test1.elf'
<flashing progress output>

-----------------------------------------------------------------------
Starting test execution
-----------------------------------------------------------------------

 ... 'Alice'

-----------------------------------------------------------------------
Collecting test results
-----------------------------------------------------------------------

 ... 'Alice': Passed

Summary:
  test1: PASSED
```

A failing test prints `Failed` in the result collection and a non-zero exit code:

```
Summary:
  test2: FAILED
```

<!-- Getting Started -->
# Getting started

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

1. Setup your toolchain: _CMake_, _make_, _gcc-arm-none-eabi_ (as `TOOLCHAIN_PREFIX`) and _Python3_ with pyocd (_openocd_ is only required if your config uses the `openocd` flash backend)
2. Install the daisyHat python package: `pip install <path-to-daisyHat>`
3. Connect each Daisy Seed board via USB and via an STLink JTAG programmer
4. Build and run the tests: `daisyhat test <path-to-test-root>`
   - `daisyhat build <path-to-test-root>` builds without running
   - `daisyhat clean <path-to-test-root>` removes the test build directories
   - `daisyhat test <path-to-test-root> --list` shows the discovered tests

### Editor / LSP support

Each test project builds in its own `.build/` directory, so CMake writes one `compile_commands.json` per project. To get a single `compile_commands.json` covering all CMake targets (for clangd, C/C++ IntelliSense, etc.), build the tests first, then merge the per-project files:

```sh
python3 scripts/aggregate_compile_commands.py
```

This writes a merged `compile_commands.json` to the repository root (gitignored). Point your editor at it (the repository `.vscode/c_cpp_properties.json` already does).

## Developing daisyHat locally

How to work on the daisyHat repository itself, testing it against real hardware with the self-tests in [`selftests/`](selftests/).

1. Create a local python venv and install the package:
   ```sh
   python3 -m venv .venv
   .venv/bin/pip install -e .
   ```
2. Create a `.env` file at the repository root from [.env.example](.env.example) and fill in `LIBDAISY_DIR` and `TOOLCHAIN_PREFIX` (the CLI loads `.env` from the working directory automatically; values already set in the environment are not overridden)
3. Create a local config file `selftests/daisyHat.config.local.json` (gitignored) describing your local hardware — machine specific serial device paths and probe IDs — and point `DAISYHAT_CONFIG_FILE_OVERRIDE` in your `.env` file to it
4. Find the ID of your USB debug probe: `.venv/bin/pyocd list` shows all connected pyOCD-compatible probes with their unique IDs
5. Find the serial port path of the Daisy Seed: `ls /dev/cu.*` on macOS (it appears as `/dev/cu.usbmodem<serial number>` once the seed has been flashed at least once) or `ls /dev/serial/by-id/` on Linux (stable path derived from the USB serial number)
6. Connect the Daisy Seed via USB and via its debug probe, and run the self-tests:
   ```sh
   .venv/bin/daisyhat test selftests
   ```
   (in VS Code, the `daisyhat: test (selftests)` task does the same)
   - `.venv/bin/daisyhat build selftests` builds without running
   - `.venv/bin/daisyhat clean selftests` removes the test build directories
   - Troubleshooting flash errors: run with `DAISYHAT_LOG_LEVEL=DEBUG` (full pyOCD logging incl. tracebacks); `Pipe error`s under flash load are typically a bad USB cable, hub or port, and a stuck probe USB handle requires unplugging the probe

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
