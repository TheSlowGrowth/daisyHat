import os
import re
import subprocess
import time

from . import SerialDevice
from . import Tools
from . import ConfigFile

class DaisySeed:
    """ Represents a Daisy Seed board and provides functions    
        for flashing and communicating with it
    """

    def __init__(self, identifier):
        """ Construct a new 'DaisySeed' object. It will read all configuration data from the
            projects daisyHat.config.json, according the the identifier.

            :param identifier: The identifier string that uniquely represents this Daisy Seed
        """
        self._identifier = identifier
        self._openOcdCfg = "interface/stlink.cfg"
        self._serialDevicePath = "<invalid>"

        self.serialConnection = None
        """ The SerialDevice that talks to the Daisy Seed """

        # read config json
        if not ConfigFile.daisyHatConfig:
            raise Exception("daisyHat config file was not loaded")
        if "seeds" not in ConfigFile.daisyHatConfig:
            raise Exception("daisyHat config file doesn't contain \"seeds\" entry")
        seeds = ConfigFile.daisyHatConfig["seeds"]
        if not identifier in seeds:
            raise Exception("daisyHat config file doesn't contain a Daisy Seed with identifier '{}'".format(str(identifier)))
        seedConfig = seeds[identifier]

        if "serialDevice" in seedConfig:
            sanitizedDevicePath = re.sub(r'[^A-Za-z0-9_\-\\\/]', '', seedConfig["serialDevice"])
            if sanitizedDevicePath != seedConfig["serialDevice"]:
                Tools.printWarning("Serial device path '{}' was sanitized to '{}'".format(seedConfig["serialDevice"], sanitizedDevicePath))
            self._serialDevicePath = sanitizedDevicePath
        
        if "openOcdCfg" in seedConfig:
            self._openOcdCfg = seedConfig["openOcdCfg"]

    @property     
    def identifier(self):
        """ The identifier string that uniquely represents this Daisy Seed """
        return self._identifier

    @property     
    def openOcdCfg(self):
        """ The openocd device configuration file used for programming this Daisy Seed """
        return self._openOcdCfg

    @property     
    def serialDevicePath(self):
        """ The serial device path used for communicating with this Daisy Seed """
        return self._serialDevicePath

    def uploadFirmwareElfAndStartSerial(self, firmwareElfFilePath):
        """ Uploads a firmware image *.elf to this Daisy Seed. The test execution will
            be halted until startTestExecution has been called.
        """
        command = ["openocd"]
        command = command + ["-s", "/usr/local/share/openocd/scripts",
                             "-f", self._openOcdCfg,
                             "-f", "target/stm32h7x.cfg",
                             "-c", "program \"" + firmwareElfFilePath + "\" verify reset exit"]
        print("command:")
        print(command)

        try:
            result = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    timeout=20,
                                    check=True)
            print(result.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print(e.output.decode("utf-8"))
            raise e

        # start serial device
        self.serialConnection = SerialDevice.SerialDevice(self._identifier, self._serialDevicePath)

    def startTestExecution(self):
        """ Starts the execution of the test firmware on the DaisySeed by sending the 
            "start_test" signal. The serial port must have been opened prior to calling 
            this function.
        """
        self.serialConnection.sendSignal("start_test")
    
    def awaitTestResult(self, timeoutInMs = 10000):
        """ Waits until the test execution completed and returns the result: True/False.
            Returns None if the timeout was exceeded.
            :param timeoutInMs: a timeout in ms before an Exception is thrown; 
                                or 0 if signal should be awaited forever
        """
        startTimeMs = time.time() * 1000
        while True:
            now = time.time() * 1000
            if timeoutInMs > 0 and now - startTimeMs > timeoutInMs:
                return None
            for line in iter(self.serialConnection.getEntireDataReceived().splitlines()):
                if line.startswith("> testResult = "):
                    if line.startswith("> testResult = SUCCESS"):
                        return True
                    else:
                        return False
            time.sleep(0.5)
    
    