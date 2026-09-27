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
| I2C SCL  | D11   | ----    | D13 | Alice I2C1 SCL → Bob I2C4 SCL (Alice enables internal pull-ups)
| I2C SDA  | D12   | ----    | D14 | Alice I2C1 SDA → Bob I2C4 SDA (Alice enables internal pull-ups)

The two I2C wires (Alice D11/D12 ↔ Bob D13/D14) are **shared with UART**: the same two lines double as a direct UART connection between the seeds, so no extra wires are needed for the UART test.

| function | Alice             | wire to | Bob             |
| -------- | ----------------- | ------- | --------------- |
| UART TX  | D12 (UART4 TX)    | ----    | D14 (USART1 RX) |
| UART RX  | D11 (UART4 RX)    | ----    | D13 (USART1 TX) |

Additional wires will be documented here as they are added to the fixture.

## Tests

| test            | description                                                        |
| --------------- | ------------------------------------------------------------------ |
| `spi_transfer`  | Alice (SPI master) sends a fixed byte sequence to Bob (SPI slave) over the direct SPI connection, once per hardcoded SPI configuration (speed, clock polarity/phase). Bob asserts the received bytes against the same hardcoded sequence. Per round, the host synchronizes the devices via checkpoint holds: Alice is held before sending until Bob confirms he is configured and waiting to receive. |
| `i2c_transfer`  | Alice (I2C1 master, D11 SCL / D12 SDA, internal pull-ups enabled) and Bob (I2C4 slave, D13 SCL / D14 SDA) exchange fixed byte sequences at each hardcoded speed (100 kHz, 400 kHz). Per direction the host synchronizes the devices via checkpoint holds; Bob's I2C4 has no DMA support (yet), so Bob is always on the blocking APIs while Alice's master side alternates between blocking and DMA. |
| `uart_transfer` | Alice (UART4, D12 TX / D11 RX) and Bob (USART1, D13 TX / D14 RX) exchange fixed byte sequences at each hardcoded baud rate (115200, 921600), over the same two wires the I2C test uses. Both sides alternate between the blocking and DMA APIs. UART has no flow control, so per step the host releases the *receiver* before the *sender* (its peripheral must be armed and polling before bits start clocking, or the bytes are lost). |

> The checkpoint synchronization (`// CHECKPOINT` markers in `tests/spi_transfer/` and `tests/i2c_transfer/`) uses `daisyhat::Checkpoint` on the device and `DaisySeed.halt_at_checkpoint` / `CheckpointHold.release` on the host, communicating via the usual daisyHat serial signals (`cp:<name>` device→host, `rel:<name>` host→device).

## Running

From the daisyHat repository root (where the `.env` file lives):

```
.venv/bin/daisyhat test libDaisyTests            # all tests
.venv/bin/daisyhat test libDaisyTests spi_transfer
```
