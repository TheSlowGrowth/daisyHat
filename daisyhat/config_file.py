import json
import os
from . import tools

daisyhat_config = dict()

def read_config_file(config_file_path):
    global daisyhat_config

    config_file_path_override = os.getenv('DAISYHAT_CONFIG_FILE_OVERRIDE')
    if config_file_path_override:
        config_file_path = os.path.abspath(config_file_path_override)
    tools.print_info("daisyHat config file path: " + config_file_path + (" [Manual Override]" if config_file_path_override else ""))

    with open(config_file_path) as json_file:
        daisyhat_config = json.load(json_file)
        json_file.close()

    if not daisyhat_config:
        raise ValueError("Cannot read daisyHat configuration file from path " + str(config_file_path))