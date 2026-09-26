""" daisyhat command line interface.

Final shape (see docs/python-orchestration-migration.md):

    daisyhat test <root> [test_name ...] [options]
    daisyhat build <root> [test_name ...] [options]
    daisyhat clean <root>
"""

import argparse
import os
import sys

from . import envfile


def _not_implemented(args):
    print("ERROR: '{}' is not implemented yet.".format(args.command), file=sys.stderr)
    sys.exit(2)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="daisyhat",
        description="daisyHat: build & test orchestration for Daisy Seed firmware")

    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_test_cmd(name, help_text):
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("root", help="root directory (must contain a tests/ subdirectory)")
        sub.add_argument("test_names", nargs="*",
                         help="names of the tests to run (default: all discovered tests)")
        sub.add_argument("--list", action="store_true",
                         help="list discovered tests and their firmware images, exit")
        return sub

    test = add_test_cmd("test", "build and run the firmware tests found in <root>/tests/")
    test.add_argument("--no-build", action="store_true", help="skip the build step")
    test.set_defaults(command="test", func=_not_implemented)

    build = add_test_cmd("build", "build the firmware tests found in <root>/tests/")
    build.set_defaults(command="build", func=_not_implemented)

    clean = subparsers.add_parser("clean", help="clean the test build directories")
    clean.add_argument("root", help="root directory (must contain a tests/ subdirectory)")
    clean.set_defaults(command="clean", func=_not_implemented)

    return parser


def main(argv=None):
    # load local development environment (.env is gitignored; see .env.example)
    envfile.load_env_file(os.path.join(os.getcwd(), ".env"))
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
