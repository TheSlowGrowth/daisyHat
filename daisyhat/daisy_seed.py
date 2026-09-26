import re
import time

from . import serial_device
from . import config_file
from . import flash


class DaisySeed:
    """ Represents a Daisy Seed board and provides functions for test execution """

    def __init__(self, identifier):
        self._identifier = identifier
        seed_cfg = config_file.daisyhat_config["seeds"][identifier]
        self._flash_backend = flash.make_flash_backend(seed_cfg, seed_name=identifier)
        self._serial_device_path = seed_cfg["serialDevice"]
        self.serial_connection = None
        self.lines = []  # raw lines received since the serial connection was opened

    @property
    def identifier(self):
        return self._identifier

    @property
    def serial_device_path(self):
        return self._serial_device_path

    def upload_firmware_elf_and_start_serial(self, elf_path):
        """
        Uploads the given firmware ELF to the seed using the flash backend
        configured for the seed and opens a connection to the serial port
        that was configured for the seed
        """
        self._flash_backend.flash(elf_path)
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
