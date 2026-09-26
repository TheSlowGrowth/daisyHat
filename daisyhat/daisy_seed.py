import os
import re
import subprocess
import time

from . import serial_device
from . import config_file
from .errors import DaisyHatError

class DaisySeed:
    """ Represents a Daisy Seed board and provides functions for test execution """

    def __init__(self, identifier):
        self._identifier = identifier
        self._openocd_cfg = config_file.daisyhat_config["seeds"][identifier]["openOcdCfg"]
        self._serial_device_path = config_file.daisyhat_config["seeds"][identifier]["serialDevice"]
        self.serial_connection = None
        self.lines = []  # raw lines received since the serial connection was opened

    @property
    def identifier(self):
        return self._identifier

    @property
    def openocd_cfg(self):
        return self._openocd_cfg

    @property
    def serial_device_path(self):
        return self._serial_device_path

    def upload_firmware_elf_and_start_serial(self, elf_path):
        """
        Uploads the given firmware ELF to the seed using OpenOCD
        and opens a connection to the serial port that was configured for the seed
        """
        openocd_args = [
            "openocd",
            "-s", "/usr/local/share/openocd/scripts",
            "-f", self.openocd_cfg,
            "-f", "target/stm32h7x.cfg",
            "-c", f'program "{elf_path}" verify reset exit'
        ]
        print("command:")
        print(openocd_args)
        result = subprocess.run(openocd_args)
        if result.returncode != 0:
            raise DaisyHatError(f"OpenOCD failed to flash '{elf_path}' to seed '{self._identifier}' (return code {result.returncode})")
        self.open_serial()

    def open_serial(self):
        """Opens the serial connection configured for the seed (without flashing)."""
        self.serial_connection = serial_device.SerialDevice(self._identifier, self.serial_device_path)
        self.lines = []

    def start_test_execution(self):
        """ Starts the test execution by sending the `start_test` signal """
        self.serial_connection.send_signal("start_test")

    def await_test_result(self, timeout_ms=10000):
        """
        Awaits the test result by waiting for the seed to report `> testResult = SUCCESS` or `> testResult = FAILURE`
        :param timeout_ms: the timeout in ms before returning `None`
        :return: `True` if the test was successful, `False` if not and `None` on timeout
        """
        start_time_ms = time.time() * 1000
        while True:
            now = time.time() * 1000
            if timeout_ms > 0 and now - start_time_ms > timeout_ms:
                return None
            # wait for a line on the serial connection
            line = self.serial_connection.get_data_received()
            if line:
                for received_line in line.splitlines():
                    self.lines.append(received_line)
                if re.search(r"> testResult = SUCCESS", line):
                    return True
                elif re.search(r"> testResult = FAILURE", line):
                    return False
