""" Minimal .env file support (stdlib only).

    load_env_file(path) parses KEY=VALUE lines and sets the variables in
    os.environ, unless the variable is already set in the environment.
    Blank lines and lines starting with '#' are ignored, 'export ' prefixes
    and surrounding quotes are stripped.
"""

import os


def load_env_file(path):
    """ Loads KEY=VALUE pairs from the .env file at `path` into os.environ.
        Variables that are already set in the environment take precedence.
        Does nothing if the file does not exist.
    """
    if not os.path.isfile(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):].lstrip()
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value
