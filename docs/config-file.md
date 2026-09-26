# daisyHat configuration file format

A project level configuration file, usually named `daisyHat.config.json`, describes the hardware setup.

- `version` – the config file format version
- `defaultSeed` – the identifier of the seed that the default test flow (no
  `daisyHatTest.py`) flashes and runs the firmware on. Must be one of the
  configured seeds. Required if the config defines more than one seed; for a
  single seed it defaults to that seed.
- `seeds` – the configured Daisy Seeds, keyed by identifier:
  - `openOcdCfg` – the OpenOCD configuration to use for flashing
  - `serialDevice` – the serial device path of the seed's USB serial interface

## Example

```json
{
    "version": 1,
    "defaultSeed": "Alice",
    "seeds": {
        "Alice": {
            "openOcdCfg": "interface/stlink.cfg",
            "serialDevice": "/dev/serial/by-id/usb-Electrosmith_Daisy_Seed_Built_In_346135793139-if00"
        },
        "Bob": {
            "openOcdCfg": "interface/ftdi/olimex-arm-usb-tiny-h.cfg",
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

- For now, multiple seeds will need different programmers types. In the future, support for multiple programmers of the same type via serial numbers will be added.