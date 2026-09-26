""" daisyhat command line interface.

    daisyhat test <root> [test_name ...] [options]
    daisyhat build <root> [test_name ...] [options]
    daisyhat clean <root>
"""

import argparse
import logging
import os
import subprocess
import sys

from . import hostlog

from . import build
from . import discovery
from . import envfile
from . import hooks
from .errors import DaisyHatError


def build_parser():
    parser = argparse.ArgumentParser(
        prog="daisyhat",
        description="daisyHat: build & test orchestration for Daisy Seed firmware")

    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_test_cmd(name, help_text):
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("root",
                         help="test root directory (must contain a tests/ subdirectory)")
        sub.add_argument("test_names", nargs="*",
                         help="names of the tests to operate on (default: all discovered tests)")
        sub.add_argument("--list", action="store_true",
                         help="list discovered tests and their firmware images, exit")
        return sub

    test = add_test_cmd("test", "build and run the firmware tests found in <root>/tests/")
    test.add_argument("--no-build", action="store_true", help="skip the build step")
    test.add_argument("--config", type=str,
                      help="path to the daisyHat config file (default: <root>/daisyHat.config.json)")
    test.set_defaults(command="test", func=cmd_test)

    build_cmd = add_test_cmd("build", "build the firmware tests found in <root>/tests/")
    build_cmd.set_defaults(command="build", func=cmd_build)

    clean = subparsers.add_parser("clean", help="clean the test build directories")
    clean.add_argument("root",
                       help="test root directory (must contain a tests/ subdirectory)")
    clean.set_defaults(command="clean", func=cmd_clean)

    return parser


def _print_tests(root, tests):
    hostlog.log("Tests in '{}':".format(os.path.join(root, "tests")))
    for name, test_dir in tests.items():
        images = [os.path.basename(p) for p in discovery.firmware_images(test_dir).values()]
        hostlog.log("  {}  ({})".format(name, ", ".join(images) if images else "no firmware image yet"))


def _require_env(name):
    value = os.environ.get(name)
    if not value:
        raise DaisyHatError(
            "environment variable {} is not set; it is required for building. "
            "Set it in the environment or in a local .env file (see .env.example)".format(name))
    return value


def _daisyhat_dir():
    # the package lives in <repo>/daisyhat/
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _prepare_build_env():
    return (_require_env("LIBDAISY_DIR"),
            _require_env("TOOLCHAIN_PREFIX"),
            _daisyhat_dir())


def cmd_build(args):
    tests = discovery.discover_tests(args.root)
    if args.list:
        _print_tests(args.root, tests)
        return
    tests = discovery.select_tests(tests, args.test_names)
    libdaisy_dir, toolchain_prefix, daisyhat_dir = _prepare_build_env()
    for name, test_dir in tests.items():
        build.build_test(name, test_dir, libdaisy_dir, toolchain_prefix, daisyhat_dir)
    hostlog.log("Built {} test(s).".format(len(tests)))


def cmd_clean(args):
    tests = discovery.discover_tests(args.root)
    for name, test_dir in tests.items():
        build.clean_test(name, test_dir)
    hostlog.log("Cleaned {} test(s).".format(len(tests)))


def cmd_test(args):
    tests = discovery.discover_tests(args.root)
    if args.list:
        _print_tests(args.root, tests)
        return
    tests = discovery.select_tests(tests, args.test_names)
    discovery.load_suite_config(args.root, args.config)

    if not args.no_build:
        libdaisy_dir, toolchain_prefix, daisyhat_dir = _prepare_build_env()
        for name, test_dir in tests.items():
            build.build_test(name, test_dir, libdaisy_dir, toolchain_prefix, daisyhat_dir)

    results = dict()
    for name, test_dir in tests.items():
        hostlog.log("")
        hostlog.log("========== test '{}' ==========".format(name))
        images = discovery.firmware_images(test_dir)
        try:
            results[name] = hooks.run_test(name, test_dir, images)
        except (subprocess.CalledProcessError, OSError):
            raise DaisyHatError(
                "test '{}' failed to execute (flashing or serial error, see output above)".format(
                    name))

    hostlog.log("")
    hostlog.log("Summary:")
    all_passed = True
    for name in tests:
        passed = results[name]
        all_passed = all_passed and passed
        hostlog.log("  {}: {}".format(name, "PASSED" if passed else "FAILED"))
    sys.exit(0 if all_passed else 1)


def main(argv=None):
    # local development environment file (gitignored; see .env.example)
    envfile.load_env_file(os.path.join(os.getcwd(), ".env"))
    # optional logging for the pyocd flash backend, e.g. DAISYHAT_LOG_LEVEL=DEBUG
    log_level = os.getenv("DAISYHAT_LOG_LEVEL")
    if log_level:
        logging.basicConfig(
            level=log_level, format="%(levelname)s:%(name)s:%(message)s")
        logging.getLogger("pyocd").setLevel(log_level)
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except DaisyHatError as e:
        print("daisyhat: error: {}".format(e), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
