# daisyHat configuration file format

A project level configuration file, usually named `daisyHat.config.json`, describes the hardware setup.

- `version` – the config file format version
- `defaultSeed` – the identifier of the seed that the default test flow (no
  `daisyHatTest.py`) flashes and runs the firmware on. Must be one of the
  configured seeds. Required if the config defines more than one seed; for a
  single seed it defaults to that seed.
- `seeds` – the configured Daisy Seeds, keyed by identifier:
  - `flash` – the flashing setup of the seed (optional; a missing object
    defaults to the `pyocd` backend):
    - `backend` – `pyocd` (default) or `openocd`
    - `board` – (pyocd only, optional) the unique ID or name of the debug probe
      to use (show connected probes with `pyocd list`). Only needed if more
      than one pyOCD-compatible probe is connected.
    - `interfaceCfg` – (openocd only, required) the OpenOCD interface
      configuration, e.g. `interface/stlink.cfg`
  - `serialDevice` – the serial device path of the seed's USB serial interface

### Flash backends

- `pyocd` (default): in-process pyOCD, no system dependencies (pyOCD is a
  package dependency of daisyHat). Supported probes: ST-Link (v2/v3), DAPLink
  (CMSIS-DAP), J-Link, PicoProbe. Note that probes based on FTDI chips
  (e.g. the Olimex ARM-USB-Tiny-H) are not supported by pyOCD — use the
  `openocd` backend for those.
- `openocd`: spawns an `openocd` process, which requires `openocd` on `PATH`.
  Any probe OpenOCD supports works (e.g. FTDI-based probes).

## Example

```json
{
    "version": 1,
    "defaultSeed": "Alice",
    "seeds": {
        "Alice": {
            "flash": {
                "backend": "pyocd"
            },
            "serialDevice": "/dev/serial/by-id/usb-Electrosmith_Daisy_Seed_Built_In_346135793139-if00"
        },
        "Bob": {
            "flash": {
                "backend": "openocd",
                "interfaceCfg": "interface/ftdi/olimex-arm-usb-tiny-h.cfg"
            },
            "serialDevice": "/dev/serial/by-id/usb-Electrosmith_Daisy_Seed_Built_In_652347574563-if00"
        }
    }
}
```

## Specifying the config file path

By default, the config file is expected to be named `<testRoot>/daisyHat.config.json`.
You can specify a different path with the `--config` option of the `daisyhat` CLI:

```
daisyhat test <testRoot> --config myCustomFile.json
```

### Local development config

Machine specific settings (local serial device paths, local programmer
interfaces) belong in a local config file, e.g.
`<testRoot>/daisyHat.config.local.json` (gitignored), while the committed
config keeps the CI/runner setup. Point the CLI to it with the
`DAISYHAT_CONFIG_FILE_OVERRIDE` environment variable — typically via the
`.env` file in the directory the CLI is started from (loaded automatically):

```
DAISYHAT_CONFIG_FILE_OVERRIDE=selftests/daisyHat.config.local.json
```

The path is resolved relative to the directory the CLI was started in.

The host-side python library accepts overriding the configuration file path by setting the `DAISYHAT_CONFIG_FILE_OVERRIDE` environment variable.
You can use this while running the tests locally, where the device paths will likely be different from the CI encironment.

## Caveats

- With the `pyocd` backend, multiple probes of the same type can be used in a
  single config — select the probe per seed via `flash.board` (the probe
  unique ID, see `pyocd list`).