""" Runner logic for firmware tests: flash firmware images to Daisy Seeds,
    start the test execution and collect the results.

    This is the library version of the former `python/runners/daisyHatTestRunner.py`
    script and must keep its behavior: flash -> start -> collect.
"""

import sys

from . import ConfigFile
from . import DaisySeed
from . import Tools


def run_firmware_test(firmware, config_file_path):
    """ Flashes firmware images to Daisy Seeds, starts the test execution on
        all of them and collects the per-seed results.

        :param firmware: iterable of (firmware_elf, seed_identifier) pairs.
                         `firmware_elf` is the path to a firmware image (*.elf)
                         and `seed_identifier` is the identifier of the Daisy
                         Seed to flash it to, as configured in the daisyHat
                         config file.
        :param config_file_path: path to the daisyHat config file
                                 (daisyHat.config.json)
        :return: True if the test on all seeds passed, False otherwise
                 (a timed-out seed counts as failed)
    """
    # read daisyHat config file (e.g. daisyHat.config.json)
    ConfigFile.readConfigFile(config_file_path)

    # create DaisySeed object and upload firmware
    seeds = list()
    Tools.printSmallHeadline("Flashing firmware images")
    for elf, seed_id in firmware:
        print(" ... flashing to '{}': '{}'".format(seed_id, elf))
        seed = DaisySeed(seed_id)
        seed.uploadFirmwareElfAndStartSerial(elf)
        seeds.append(seed)

    Tools.printSmallHeadline("Starting test execution")
    for seed in seeds:
        print(" ... '{}'".format(seed.identifier))
        seed.startTestExecution()

    # get results from all of the seeds
    Tools.printSmallHeadline("Collecting test results")
    result = True
    for seed in seeds:
        seed_result = seed.awaitTestResult()
        result_str = "Passed" if seed_result else "Failed"
        print(" ... '{}': {}".format(seed.identifier, result_str))
        result = result and seed_result
    return result


def main(argv):
    """ Entry point that keeps the old daisyHatTestRunner.py script interface:

            daisyHatTestRunner.py --firmware <elf> <seedId> [--firmware ...] --config <config>
    """
    import argparse

    parser = argparse.ArgumentParser(prog="daisyHatTestRunner")
    parser.add_argument("--firmware", action="append", type=str, nargs=2,
                        help="The firmware *.elf file to upload, followed by the seed id to upload to")
    parser.add_argument("--config", action="store", type=str,
                        help="The daisyHat config file")
    args = parser.parse_args(argv)

    result = run_firmware_test(args.firmware, args.config)
    sys.exit(0 if result else 1)
