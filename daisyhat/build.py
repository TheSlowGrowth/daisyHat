import os
import shutil
import subprocess

from .errors import DaisyHatError


def build_test(test_name, test_dir, libdaisy_dir, toolchain_prefix, daisyhat_dir,
               parallel=None):
    """ Configures and builds one test project (a standalone CMake project)
        into <test_dir>/.build.

        CMake's cache is the staleness check: configure + build are no-ops
        when nothing changed.

        :return: the build directory
    """
    build_dir = os.path.join(test_dir, ".build")
    configure = [
        "cmake",
        "-S", test_dir,
        "-B", build_dir,
        "-DCMAKE_TOOLCHAIN_FILE=" + os.path.join(libdaisy_dir, "cmake", "toolchains", "stm32h750xx.cmake"),
        "-DCMAKE_SYSTEM_NAME=Generic",
        "-DCMAKE_C_COMPILER=" + os.path.join(toolchain_prefix, "bin", "arm-none-eabi-gcc"),
        "-DCMAKE_CXX_COMPILER=" + os.path.join(toolchain_prefix, "bin", "arm-none-eabi-g++"),
        "-DCMAKE_EXE_LINKER_FLAGS=--specs=nano.specs --specs=nosys.specs",
        "-DLIBDAISY_DIR=" + libdaisy_dir,
        "-DDAISYHAT_DIR=" + daisyhat_dir,
    ]
    print(" ... configuring '{}'".format(test_name))
    try:
        subprocess.run(configure, check=True)
    except subprocess.CalledProcessError:
        raise DaisyHatError(
            "cmake configure failed for test '{}' (see output above)".format(test_name))

    parallel = parallel or os.cpu_count() or 1
    build = ["cmake", "--build", build_dir, "-j", str(parallel)]
    print(" ... building '{}'".format(test_name))
    try:
        subprocess.run(build, check=True)
    except subprocess.CalledProcessError:
        raise DaisyHatError(
            "cmake build failed for test '{}' (see output above)".format(test_name))
    return build_dir


def clean_test(test_name, test_dir):
    """ Removes the build directory (.build) of a test. """
    build_dir = os.path.join(test_dir, ".build")
    if os.path.isdir(build_dir):
        print(" ... cleaning '{}'".format(test_name))
        shutil.rmtree(build_dir)
