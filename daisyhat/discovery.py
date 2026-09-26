import os

from . import config_file
from . import flash
from .errors import DaisyHatError


SUPPORTED_CONFIG_VERSION = 1


def find_tests_dir(root):
    """ Returns the tests directory of a test root, or raises DaisyHatError. """
    tests_dir = os.path.join(root, "tests")
    if not os.path.isdir(tests_dir):
        raise DaisyHatError(
            "no tests directory found: '{}' (root '{}' must contain a 'tests' subdirectory)".format(
                tests_dir, root))
    return tests_dir


def discover_tests(root):
    """ Discovers the tests of a test root.

        A test is a subdirectory of <root>/tests/ that contains a
        CMakeLists.txt.

        :return: dict test_name -> test directory (sorted by name)
    """
    tests_dir = find_tests_dir(root)
    tests = dict()
    for name in sorted(os.listdir(tests_dir)):
        test_dir = os.path.join(tests_dir, name)
        if os.path.isdir(test_dir) and os.path.isfile(os.path.join(test_dir, "CMakeLists.txt")):
            tests[name] = test_dir
    if not tests:
        raise DaisyHatError(
            "no tests found in '{}' (a test is a subdirectory containing a CMakeLists.txt)".format(
                tests_dir))
    return tests


def select_tests(tests, names):
    """ Filters the discovered tests by name. None/empty selects all. """
    if not names:
        return tests
    unknown = [name for name in names if name not in tests]
    if unknown:
        raise DaisyHatError(
            "unknown test(s): {} (available: {})".format(
                ", ".join(unknown), ", ".join(tests)))
    return {name: tests[name] for name in sorted(tests) if name in names}


def firmware_images(test_dir):
    """ Returns the firmware images (*.elf) of a test, by scanning its build
        directory (.build) at the upstream default location.

        :return: dict of image name (filename without .elf) -> full path """
    build_dir = os.path.join(test_dir, ".build")
    if not os.path.isdir(build_dir):
        return {}
    return {name[:-len(".elf")]: os.path.join(build_dir, name)
            for name in sorted(os.listdir(build_dir))
            if name.endswith(".elf")}


def load_suite_config(root, config_path=None):
    """ Loads the suite config file (daisyHat.config.json) of a test root.

        The config carries an API version number; dispatch happens here so the
        config API can evolve while older versioned projects keep working.
        An absent version is treated as the oldest supported version.

        :return: the parsed config dict (also loaded into the config_file module for
                 the DaisySeed objects)
    """
    if config_path is None:
        config_path = os.path.join(root, "daisyHat.config.json")
    if not os.path.isfile(config_path):
        raise DaisyHatError(
            "daisyHat config file not found: '{}' (expected at the test root; "
            "use --config to override)".format(config_path))
    config_file.read_config_file(config_path)
    config = config_file.daisyhat_config
    version = config.get("version", SUPPORTED_CONFIG_VERSION)
    if version != SUPPORTED_CONFIG_VERSION:
        raise DaisyHatError(
            "unsupported daisyHat config file version {} in '{}' "
            "(supported: {})".format(version, config_path, SUPPORTED_CONFIG_VERSION))
    if not config.get("seeds"):
        raise DaisyHatError(
            "daisyHat config file '{}' does not define any seeds".format(config_path))
    default_seed = config.get("defaultSeed")
    if default_seed is not None and default_seed not in config["seeds"]:
        raise DaisyHatError(
            "daisyHat config file '{}': 'defaultSeed' ('{}') must be one of "
            "the configured seeds".format(config_path, default_seed))
    if default_seed is None and len(config["seeds"]) > 1:
        raise DaisyHatError(
            "daisyHat config file '{}' defines {} seeds and must therefore "
            "name a 'defaultSeed' (one of the configured seeds)".format(
                config_path, len(config["seeds"])))
    # validate the flash backend of every seed so that config problems
    # are reported before anything is run
    for seed_name in config["seeds"]:
        flash.make_flash_backend(config["seeds"][seed_name], seed_name=seed_name)
    return config
