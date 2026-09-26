""" Runner logic for firmware tests: flash firmware images to Daisy Seeds,
    start the test execution and collect the results (flash -> start -> collect).
"""

from . import config_file
from .daisy_seed import DaisySeed
from . import tools


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
    config_file.read_config_file(config_file_path)

    # create DaisySeed object and upload firmware
    seeds = list()
    tools.print_small_headline("Flashing firmware images")
    for elf, seed_id in firmware:
        print(" ... flashing to '{}': '{}'".format(seed_id, elf))
        seed = DaisySeed(seed_id)
        seed.upload_firmware_elf_and_start_serial(elf)
        seeds.append(seed)

    tools.print_small_headline("Starting test execution")
    for seed in seeds:
        print(" ... '{}'".format(seed.identifier))
        seed.start_test_execution()

    # get results from all of the seeds
    tools.print_small_headline("Collecting test results")
    result = True
    for seed in seeds:
        seed_result = seed.await_test_result()
        result_str = "Passed" if seed_result else "Failed"
        print(" ... '{}': {}".format(seed.identifier, result_str))
        result = result and seed_result
    return result
