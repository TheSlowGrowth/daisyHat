import argparse
import sys
import os

# import the pyDaisyHat package from the local filesytem
pathToPyDaisyHatPackage = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(pathToPyDaisyHatPackage)

import pyDaisyHat

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--firmware", action="append", type=str, nargs=2,
                        help="The firmware *.elf file to upload, followed by the seed id to upload to")
    parser.add_argument("--config", action="store", type=str,
                        help="The daisyHat config file")
    args = parser.parse_args()

    # read daisyHat config file (e.g. daisyHat.config.json)
    pyDaisyHat.readConfigFile(args.config)

    # create DaisySeed object and upload firmware
    seeds = list()
    pyDaisyHat.Tools.printSmallHeadline(f"Flashing firmware images")
    for [elf, seedId] in args.firmware:
        print(f" ... flashing to '{seedId}': '{elf}'")
        seed = pyDaisyHat.DaisySeed(seedId)
        seed.uploadFirmwareElfAndStartSerial(elf)
        seeds.append(seed)
    
    pyDaisyHat.Tools.printSmallHeadline(f"Starting test execution")
    for seed in seeds:
        print(f" ... '{seed.identifier}'")
        seed.startTestExecution()

    # get results from all of the seeds
    pyDaisyHat.Tools.printSmallHeadline(f"Collecting test results")
    result = True
    for seed in seeds:
        seedResult = seed.awaitTestResult() 
        resultStr = "Passed" if seedResult else "Failed"
        print(f" ... '{seed.identifier}': {resultStr}")
        result = result and seedResult
    sys.exit(0 if result == True else 1)
