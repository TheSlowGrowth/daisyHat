# daisyHat
Automated hardware testing for Electro-Smith Daisy

daisyHat provides a bring-your-own-test platform to run automated tests on the Electro-Smith Daisy Seed development board.

1. Each test consists of a small firmware that performs the test and prints the results to a host computer via the USB-serial connection and a python script that collects the results on the host computer.
2. daisyHat comes with a C++-library which provides basic testing macros like `EXPECT_EQ(a, b)` and handles the synchronization with the host computer.
3. daisyHat comes with a python module for the host computer which uploads the compiled firmware and runs the test
4. CMake orchestrates the building and running of the tests

## Project structure

- `cmake/` contains cmake functions
- `docs/` contains documentation and guides
- `docker/` contains files to build the github action runner docker image
- `examples/` contains a usage example with two tests (one succeeds, one fails)
- `python/` contains the python library for the host computer / test runner
- `scripts/` contains scripts for setup and run a daisyHat test runner
- `src/` contains C++ library for the device firmware

## Getting started (running tests locally)

1. Setup your toolchain with _CMake_, _make_, _gcc-arm-none-eabi_, _openocd_ and _Python3.9_
2. Create a new repository for your tests
3. Add `libDaisy` as a submodule in the `lib/libDaisy` folder (CMake-support in `libDaisy` is required - this is currently only available on a pull request feature branch)
4. Add this repository as a submodule in the `lib/daisyHat` folder 
5. Add a `CMakeLists.txt` that includes `lib/libDaisy` and `lib/daisyHat` as sub directories (with `add_subdirectory()`) (you can copy [this file](examples/CMakeLists.txt))
6. For each test, create a new directory `tests/<testName>` and add to it
    1. The C++ source code for your test firmware (take a look [here](examples/test1/main.cpp))
    2. A `CMakeLists.txt` file that registers a test firmware with the `daisyhat_add_test()` function (you can copy [this file](examples/test1/CMakeLists.txt))
7. Configure the project: `cmake -D TOOLCHAIN_PREFIX=<path-to-gcc-arm-none-eabi> -D CMAKE_TOOLCHAIN_FILE="lib/libDaisy/cmake/toolchains/stm32h750xx.cmake" -S . -B build -G "Unix Makefiles"`
8. Build libDaisy, daisyHat and the tests: `cmake --build build`
9. Connect the Daisy Seed via USB
10. Connect your JTAG programmer
11. Run the tests: `ctest --output-on-failure`

## Getting started (running tests in github CI)
[See `docs/github-actions-runner-setup-public-repos.md`]

## Work in Progress

This is just a proof-of-concept. 
If you try this out, you'll have to edit `python/daisyHat/defaultTestRunner.py` to configure your JTAG programmer and the serial port of your Daisy Seed.