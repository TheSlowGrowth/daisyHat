"""Per-test orchestration hooks.

A test directory may contain a `daisyHatTest.py` defining a `Test` class:

    class Test:
        def setup(self, ctx): ...     # optional: flash firmware, set up fixtures
        def run(self, ctx): ...      # required: return True if the test passed
        def teardown(self, ctx): ... # optional: always runs, even on failure

The CLI drives the class and hands it a `TestContext`. If the hook file is
absent, `DefaultTest` is used: flash every image to every configured seed,
start the test execution on all of them and collect the results.
"""
import importlib.util
import traceback
from pathlib import Path

from . import config_file
from .daisy_seed import DaisySeed
from .tools import print_small_headline, print_warning
from .errors import DaisyHatError


class TestContext:
    """Everything a test needs to know and do, provided by the CLI."""

    def __init__(self, test_name, test_dir, images, config):
        self.test_name = test_name
        self.test_dir = Path(test_dir)
        self.build_dir = self.test_dir / ".build"
        self.images = images  # CMake target name -> .elf path (from the build)
        self.config = config  # raw parsed suite config dict
        self.seed_ids = tuple(config["seeds"].keys())
        self.default_seed_id = config.get("defaultSeed") or next(iter(config["seeds"]))
        self._seeds = []

    def flash(self, image, seed_id):
        """Flash the .elf image to the given seed and open its serial connection.

        :return: the connected DaisySeed
        """
        seed = DaisySeed(seed_id)
        seed.upload_firmware_elf_and_start_serial(image)
        self._seeds.append(seed)
        return seed

    def connect(self, seed_id):
        """Open the serial connection to the given seed without flashing.

        :return: the connected DaisySeed
        """
        seed = DaisySeed(seed_id)
        seed.open_serial()
        self._seeds.append(seed)
        return seed

    def close(self):
        """Close all serial connections opened through this context."""
        for seed in self._seeds:
            try:
                seed.serial_connection.close()
            except Exception as e:
                print_warning("failed to close serial connection for '{}': {}".format(
                    seed.identifier, e))
        self._seeds = []


class DefaultTest:
    """Default flow: flash the image to the default seed, start, await the result."""

    def setup(self, ctx):
        if not ctx.images:
            raise DaisyHatError(
                "no firmware image (*.elf) found for test '{}' in '{}' "
                "(build the test first, or add a daisyHatTest.py with a "
                "custom test runner)".format(ctx.test_name, ctx.build_dir))
        if len(ctx.images) > 1:
            raise DaisyHatError(
                "test '{}' has multiple firmware images ({}); "
                "image-to-seed mapping requires a daisyHatTest.py".format(
                    ctx.test_name, ", ".join(ctx.images)))
        print_small_headline("Flashing firmware images")
        image = next(iter(ctx.images.values()))
        print(" ... flashing to '{}': '{}'".format(ctx.default_seed_id, image))
        self._seeds = [(ctx.default_seed_id, ctx.flash(image, ctx.default_seed_id))]

    def run(self, ctx):
        print_small_headline("Starting test execution")
        for seed_id, seed in self._seeds:
            print(" ... '{}'".format(seed_id))
            seed.start_test_execution()
        print_small_headline("Collecting test results")
        results = []
        for seed_id, seed in self._seeds:
            result = seed.await_test_result()
            print(" ... '{}': {}".format(seed_id, "Passed" if result else "Failed"))
            results.append(result)
        return all(results)


def load_test_hook(test_dir):
    """Return the Test class from <test_dir>/daisyHatTest.py, or None if absent."""
    path = Path(test_dir) / "daisyHatTest.py"
    if not path.exists():
        return None
    module_name = "daisyhat_hook_" + Path(test_dir).name
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    test_class = getattr(module, "Test", None)
    if not isinstance(test_class, type):
        raise DaisyHatError(
            "test hook '{}' must define a 'Test' class".format(path))
    return test_class


def run_test(test_name, test_dir, images):
    """Run a single test (hook-based or default flow). Returns True if passed.

    The suite config must already be loaded via config_file.read_config_file.
    """
    test_class = load_test_hook(test_dir) or DefaultTest
    test = test_class()
    ctx = TestContext(test_name, test_dir, images, config_file.daisyhat_config)
    try:
        if hasattr(test, "setup"):
            test.setup(ctx)  # config errors (missing images, ...) propagate
        try:
            return bool(test.run(ctx))
        except Exception:
            print_warning("test '{}' raised an exception:".format(test_name))
            traceback.print_exc()
            return False
        finally:
            if hasattr(test, "teardown"):
                try:
                    test.teardown(ctx)
                except Exception:
                    print_warning("teardown of test '{}' failed:".format(test_name))
                    traceback.print_exc()
    finally:
        ctx.close()
