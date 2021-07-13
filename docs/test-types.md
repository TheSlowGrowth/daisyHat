# Types of daisyHat tests

## Single/Multi Seed tests

- The test runs entirely one or more Daisy Seeds. There is no upper limit on the number of Seeds that are part of the test.
- The results are collected from the Seeds. The test succeeds only of all of the Seeds report success.
- This form of test is easy to setup with the CMake function `daisyhat_add_test()`

### Examples
tests/mySingleSeedTest/CMakeLists.txt
```
daisyhat_add_test(
    NAME MyTestName
    SEED SeedIdToExecuteOn
    SOURCES 
        main.cpp
        util.cpp
)
```

tests/myMultiSeedTest/CMakeLists.txt
```
daisyhat_add_test(
    NAME MyTestName
    SEED SeedIdForFirstFirmwareImage
    SOURCES 
        firmwareImage1/main.cpp
        firmwareImage1/util.cpp
    SEED SeedIdForSecondFirmwareImage
    SOURCES 
        firmwareImage2/main.cpp
        firmwareImage2/util.cpp
)
```

## Tests with a custom test runner

- The test is orchestrated by a custom command/script on the test runner. It may involve one or more Daisy Seeds as needed.
- Since the script has to be provided, this form of test is very flexible and can involve external measurement equipment or test fixtures.
- The scripts return value determines if the tests failed or succeeded.
- Seed firmwares are registered with the CMake function `daisyhat_add_firmware()`
- The test itself is registered with the CMake function `daisyhat_add_custom_test()`
- The path to the project-wide `daisyHat.config.json` is passed to the custom script via the command line arguments `--config <pathToConfigFile>`

### Example
tests/myCustomTest/CMakeLists.txt
```
daisyhat_add_firmware(
    NAME MyFirmwareBinaryName
    SOURCES 
        main.cpp
        util.cpp
)
daisyhat_add_custom_test(
    NAME MyTestName
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/myTestRunner.py --elf $<TARGET_FILE:MyFirmwareBinaryName>
)
```
tests/myCustomTest/myTestRunner.py
```python
import argparse
import pyDaisyHat

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # We pass this argument from CMake
    parser.add_argument("--elf", action="store", type=str,
                        help="The firmware image to flash")
    # This argument is implicitly added by daisyhat_add_custom_test()
    parser.add_argument("--config", action="store", type=str,
                        help="The daisyHat config file")
    args = parser.parse_args()

    # read daisyHat config file from the provided path (e.g. daisyHat.config.json)
    # or use the override (as provided with environment variable DAISYHAT_CONFIG_FILE_OVERRIDE)
    pyDaisyHat.readConfigFile(args.config)
    # create DaisySeed object to interact with the seed "Alice" (as configured in the config file)
    seed = pyDaisyHat.DaisySeed("Alice")
    # flash the firmware image
    seed.uploadFirmwareElfAndStartSerial(args.elf)

    # you could setup a test fixture here

    # start the test execution on the seed
    seed.startTestExecution()
    # wait for the test to complete
    result = seed.awaitTestResult() 

    # return the result to the test environment
    sys.exit(0 if result == True else 1)
```
