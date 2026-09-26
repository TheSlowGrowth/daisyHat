# libDaisy tests

This is a **test root** that uses [daisyHat](../) to test [libDaisy](https://github.com/electro-smith/libDaisy) itself.
Each test here drives one or more Daisy Seeds with libDaisy firmware built against a specific libDaisy checkout, so that changes to libDaisy can be verified on real hardware.

## The fixture: Alice & Bob

The tests in this repository are designed around a fixture of **two** Daisy Seeds, named **Alice** and **Bob**, connected to each other with jumper wires. Each test wires up (configures and uses) a subset of the wires; the first test (`spi_transfer`) only uses the SPI wires, and further tests will add more connections between the two seeds.

This readme is intended to grow into the full fixture description (complete pin-to-pin wiring table, power / programmer setup, etc.) as more wires are added.

### Seeds & programmers

| seed  | role in tests | debug programmer                    | programmer config (daisyHat)                                                                                                     |
| ----- | ------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Alice | primary / master | STLink V3                          | `pyocd` backend, selected by probe ID via `flash.board` (`pyocd list` shows the unique ID)                                      |
| Bob   | secondary / slave  | Olimex ARM-USB-Tiny-H (FTDI-based) | `openocd` backend (pyOCD does not support FTDI probes), `interfaceCfg: "interface/ftdi/olimex-arm-usb-tiny-h.cfg"`              |

Each seed is connected **both** via USB (for the on-board serial port) and via its debug programmer (for flashing).

### Config files

- `daisyHat.config.json` — the committed draft config (same settings as the local one for now).
- `daisyHat.config.local.json` — the local (machine specific) config, gitignored. Point daisyHat at it with `DAISYHAT_CONFIG_FILE_OVERRIDE=libDaisyTests/daisyHat.config.local.json` in your `.env` file.

One open question for the local config: **Bob's USB serial device path is not known yet** — it only shows up as `/dev/cu.usbmodem<serial number>` (macOS) or a `/dev/serial/by-id/...` path (Linux) once Bob has been flashed at least once. Until then the local config carries a placeholder.

### Wiring (so far)

The seeds are connected directly, with a small series resistor on each wire as protection (e.g. 100 Ω – 1 kΩ).

| function | Alice | wire to | Bob | note
| -------- | ----- | ------- | --- | ----
| SPI CS   | D7    | ----    | D7  | master CS → slave CS
| SPI SCK  | D8    | ----    | D8  | master SCK → slave SCK
| SPI MISO | D9    | ----    | D9  | master MISO → slave MISO
| SPI MOSI | D10   | ----    | D10 | master MOSI → slave MOSI

Additional wires will be documented here as they are added to the fixture.

## Tests

| test            | description                                                        |
| --------------- | ------------------------------------------------------------------ |
| `spi_transfer`  | Alice (SPI master) sends a fixed byte sequence to Bob (SPI slave) over the direct SPI connection, once per hardcoded SPI configuration (speed, clock polarity/phase). Bob asserts the received bytes against the same hardcoded sequence. Per round, the host synchronizes the devices via checkpoint holds: Alice is held before sending until Bob confirms he is configured and waiting to receive. |

> The checkpoint synchronization (`// CHECKPOINT` markers in `tests/spi_transfer/`) uses `daisyhat::Checkpoint` on the device and `DaisySeed.halt_at_checkpoint` / `CheckpointHold.release` on the host, communicating via the usual daisyHat serial signals (`cp:<name>` device→host, `rel:<name>` host→device).

## Running

From the daisyHat repository root (where the `.env` file lives):

```
.venv/bin/daisyhat test libDaisyTests            # all tests
.venv/bin/daisyhat test libDaisyTests spi_transfer
```
