# Types of daisyHat tests

A test is a subdirectory of `tests/` (inside a test root) that contains a
`CMakeLists.txt` making it a standalone CMake project. An optional
`daisyHatTest.py` file next to it will provide host-side orchestration hooks
(setup/teardown/run, image-to-seed mapping, host-only tests); this is not
implemented yet, see [Tests with a custom test runner](#tests-with-a-custom-test-runner).

## Single/Multi Seed tests

- The test runs entirely on one or more Daisy Seeds. There is no upper limit
  on the number of Seeds that are part of the test.
- The results are collected from the Seeds. The test succeeds only if all of
  the Seeds report success.
- Default flow: the test's CMake project registers exactly one firmware image.
  `daisyhat test` builds the CMake project, flashes the firmware image to every
  seed configured in the `daisyHat.config.json` at the test root, starts the
  test execution on all of them and collects the results.

### Example

tests/mySeedTest/main.cpp
```cpp
#include <daisy_seed.h>
#include <daisyHat.h>

daisy::DaisySeed seed;

int main()
{
    seed.Configure();
    seed.Init();

    daisyhat::Init(seed, "mySeedTest");
    int a = 1;
    int b = 1;
    EXPECT_EQ(a, b);
    daisyhat::FinishTest();
}
```
tests/mySeedTest/CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.20)
project (mySeedTest)

# register the firmware with the libDaisy CMake firmware target
set(FIRMWARE_NAME mySeedTest)
set(FIRMWARE_SOURCES main.cpp)
include(${LIBDAISY_DIR}/cmake/DaisyDefaultBuild.cmake)

# link the daisyHat test library
add_subdirectory(${DAISYHAT_DIR} daisyhat)
target_link_libraries(${FIRMWARE_NAME} PRIVATE daisyHat)
```

## Tests with a custom test runner

- The test is orchestrated by a custom command/script on the test runner. It
  may involve one or more Daisy Seeds as needed.
- Since the script has to be provided, this form of test is very flexible and
  can involve external measurement equipment or test fixtures.
- The script's return value determines if the test failed or succeeded.

This form is realised by the upcoming `daisyHatTest.py` per-test hooks.
Until then, you can orchestrate the test manually from a host-side script
using the `daisyhat` python library directly (this is essentially what the
`daisyhat test` CLI does for the default flow):

```python
import sys
import daisyhat

# read the suite config file at the test root (creates DaisySeed objects from it)
daisyhat.read_config_file("daisyHat.config.json")

# create a DaisySeed object to interact with the seed "Alice" (as configured in the config file)
seed = daisyhat.DaisySeed("Alice")
# flash the firmware image and open the serial connection
seed.upload_firmware_elf_and_start_serial(".build/mySeedTest.elf")
# you could setup a test fixture here
# start the test execution on the seed
seed.start_test_execution()
# wait for the test to complete
result = seed.await_test_result()

# return the result to the test environment
sys.exit(0 if result else 1)
```
