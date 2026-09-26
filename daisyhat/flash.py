"""
Flash backends for Daisy Seed firmware images.

The flash backend of a seed is configured in the "flash" object of the suite
config file (daisyHat.config.json):

    "flash": { "backend": "pyocd",   "board": "<probe unique ID, optional>" }
    "flash": { "backend": "openocd", "interfaceCfg": "interface/stlink.cfg" }

Backends:

- pyocd (default): in-process pyOCD, no system dependencies. Supported probes:
  ST-Link (v2/v3), DAPLink (CMSIS-DAP), J-Link, PicoProbe. Note that probes
  based on FTDI chips (e.g. the Olimex ARM-USB-Tiny-H) are not supported by
  pyOCD - use the openocd backend for those.

- openocd: spawns an OpenOCD process. Requires openocd on PATH.

Diagnostics: set DAISYHAT_LOG_LEVEL (e.g. 'DEBUG') to enable logging of the
pyocd backend. Without it, pyOCD's error records (which carry tracebacks) are
only reported as bare lines by Python's last-resort logging handler.
"""

import subprocess
import time

from .errors import DaisyHatError


class FlashBackend:
    """Abstract flash backend for Daisy Seed firmware images."""

    def flash(self, elf_path):
        raise NotImplementedError()


class PyOcdFlashBackend(FlashBackend):
    """Flashes a firmware ELF via pyOCD (in-process, no external process)."""

    #: the pyOCD target for the Daisy Seed (STM32H750)
    DAISY_TARGET = "stm32h750xx"

    #: number of attempts before giving up (probe USB connections can be flaky)
    MAX_ATTEMPTS = 3

    def __init__(self, board_match=None):
        self._board_match = board_match

    def flash(self, elf_path):
        try:
            from pyocd.core.helpers import ConnectHelper
            from pyocd.core.session import Session
            from pyocd.flash.file_programmer import FileProgrammer
        except ImportError as e:
            raise DaisyHatError(
                "pyocd is not installed: '{}' (pip install pyocd)".format(e)) from e

        last_error = None
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            probe = ConnectHelper.choose_probe(
                blocking=False, return_first=True, unique_id=self._board_match)
            if probe is None:
                raise DaisyHatError(
                    "no debug probe found matching '{}' (use 'pyocd list' to show "
                    "connected probes and set 'board' in the seed config accordingly)"
                    .format(self._board_match or "any"))
            session = Session(probe, options={"target_override": self.DAISY_TARGET,
                                              "debug.traceback": True})
            try:
                with session:
                    FileProgrammer(session).program(elf_path)
                    session.target.reset()
                return
            except Exception as e:
                last_error = e
                # a stuck USB handle (left behind by a failed disconnect) cannot
                # be recovered from inside the process - further attempts are
                # guaranteed to fail with 'Access denied' until the probe is
                # physically replugged
                if "Access denied" in str(e):
                    raise DaisyHatError(
                        "pyocd failed to flash '{}': {} - the probe's USB handle "
                        "appears stuck (typically left behind by a failed "
                        "disconnect); replug the probe's USB cable and try again"
                        .format(elf_path, e)) from e
                if attempt < self.MAX_ATTEMPTS:
                    print("flash attempt {} failed ({}), retrying...".format(
                        attempt, e))
                    time.sleep(1)
        raise DaisyHatError(
            "pyocd failed to flash '{}' (probe: {}): {}".format(
                elf_path, probe.unique_id, last_error)) from last_error


class OpenOcdFlashBackend(FlashBackend):
    """Flashes a firmware ELF via an OpenOCD process (requires openocd on PATH)."""

    def __init__(self, interface_cfg):
        self._interface_cfg = interface_cfg

    def flash(self, elf_path):
        openocd_args = [
            "openocd",
            "-s", "/usr/local/share/openocd/scripts",
            "-f", self._interface_cfg,
            "-f", "target/stm32h7x.cfg",
            "-c", 'program "{}" verify reset exit'.format(elf_path),
        ]
        print("command:")
        print(openocd_args)
        result = subprocess.run(openocd_args)
        if result.returncode != 0:
            raise DaisyHatError(
                "OpenOCD failed to flash '{}' (return code {})".format(
                    elf_path, result.returncode))


def make_flash_backend(seed_cfg, seed_name=None):
    """ Creates the flash backend configured for a seed.

        Validates the "flash" object of the seed config and raises DaisyHatError
        on any problem.

        :param seed_cfg: the seed config dict (the value under "seeds" in the suite config)
        :param seed_name: optional seed name, only used for error messages
    """
    name = "'{}'".format(seed_name) if seed_name is not None else "seed"
    # a missing 'flash' object defaults to the pyocd backend
    flash_cfg = seed_cfg.get("flash", {"backend": "pyocd"})
    if not isinstance(flash_cfg, dict):
        raise DaisyHatError(
            "seed {} has an invalid 'flash' object (expected: "
            '{{\"backend\": \"pyocd\", ...}} or {{\"backend\": \"openocd\", ...}})'
            .format(name))
    backend = flash_cfg.get("backend")
    if backend == "pyocd":
        board_match = flash_cfg.get("board")
        if board_match is not None and not isinstance(board_match, str):
            raise DaisyHatError(
                "seed {}: 'flash.board' must be a string (probe unique ID or name)"
                .format(name))
        return PyOcdFlashBackend(board_match)
    elif backend == "openocd":
        interface_cfg = flash_cfg.get("interfaceCfg")
        if not isinstance(interface_cfg, str) or not interface_cfg:
            raise DaisyHatError(
                "seed {}: 'flash.interfaceCfg' is required for the openocd backend "
                "(e.g. 'interface/stlink.cfg')".format(name))
        return OpenOcdFlashBackend(interface_cfg)
    else:
        raise DaisyHatError(
            "seed {}: 'flash.backend' must be 'pyocd' or 'openocd' (got: {})".format(
                name, backend))
