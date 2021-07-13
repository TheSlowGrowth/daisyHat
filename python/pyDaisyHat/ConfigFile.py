import json
import os
from . import Tools

daisyHatConfig = dict()

def readConfigFile(configFilePath):
    global daisyHatConfig

    configFilePathOverride = os.getenv('DAISYHAT_CONFIG_FILE_OVERRIDE')
    if configFilePathOverride:
        configFilePath = os.path.abspath(configFilePathOverride)
    Tools.printInfo("daisyHat config file path: " + configFilePath + (" [Manual Override]" if configFilePathOverride else ""))

    with open(configFilePath) as jsonFile:
        daisyHatConfig = json.load(jsonFile)
        jsonFile.close()

    if not daisyHatConfig:
        raise ValueError("Cannot read daisyHat configuration file from path " + str(configFilePath))