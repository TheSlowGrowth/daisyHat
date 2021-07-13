# daisyHat configuration file format

A project level configuration file, usually named `daisyHat.config.json`, describes the hardware setup.

## Example

```json
{
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

By default, the config file is expected to be named `${projectRoot}/daisyHat.config.json`. 
You can specify a different path by setting the `DAISYHAT_CONFIG_FILE` CMake variable.

```
set(DAISYHAT_CONFIG_FILE myCustomFile.json)
```

The host-side python library accepts overriding the configuration file path by setting the `DAISYHAT_CONFIG_FILE_OVERRIDE` environment variable.
You can use this while running the tests locally, where the device paths will likely be different from the CI encironment.

## Caveats

- For now, multiple seeds will need different programmers types. In the future, support for multiple programmers of the same type via serial numbers will be added.