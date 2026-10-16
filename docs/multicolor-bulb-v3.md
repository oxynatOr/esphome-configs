# Shelly Multicolor Bulb E27 Gen3 (RGBCCT)

Packages for the **Shelly Multicolor Bulb E27 Gen3** (ESP32-C3, 8 MB flash, KP18068 LED driver, RGB and one warm white LED).
Moved here from the example configs of [free-shelly-ota](https://github.com/oxynatOr/free-shelly-ota), which installs ESPHome over the network.

> **Status:** ESPHome runs on a real bulb. The owner tested the light on 2026-10-11 (channel order below confirmed) and flashed and ran the colour temperature
> light on 2026-10-16. Not measured: colour accuracy against the stock firmware, the lowest dimming steps, the driver currents, the power consumption.
> All optional packages are **untested** on the bulb. `python scripts/check.py --esphome` passes, also for `examples/multicolor-bulb-full.yaml` with every package, and that
> example **compiles** together with `ota-stock-layout.yaml` (ESPHome 2026.10.0-dev, 947 KB of the 2.5 MB app slot). It was not flashed in this form.

## Files

| File | Purpose |
|---|---|
| `projects/multicolor-bulb/v3.yaml` | Adoptable device: light, Home Assistant time, Wi-Fi diagnostics |
| `hardware/lights/multicolor-bulb/v3.yaml` | Hardware: board, KP18068 driver, outputs, RGB + colour temperature light |
| `hardware/lights/multicolor-bulb/ota-stock-layout.yaml` | Optional: Shelly's partition table, for the install over OTA from the stock firmware |
| `hardware/lights/multicolor-bulb/overtemp.yaml`, `dim-range.yaml` | Optional: over-temperature protection, dim range (only with gamma 2.8) |
| `hardware/lights/effects/*.yaml` | Optional effects: daylight (time, sun), night (time, sun), scenes, sunrise alarm |
| `examples/multicolor-bulb-full.yaml` | The project with every optional package |

The driver and the light platform are **not** part of ESPHome. They live in [oxynatOr/esphome-kp18058](https://github.com/oxynatOr/esphome-kp18058)
(components `kp18058` and `rgbw_ct_table`); the hardware file pins the commit of its main branch of 2026-10-16. The bulb first ran an earlier local build
of the component, so the pinned code itself has not been run on it. Its README covers the bus protocol, `ignore_ack` and troubleshooting.

## What is known

| What | Value | Source |
|---|---|---|
| Chip | ESP32-C3, 8 MB flash, partition table at `0x10000` | boot log, official package |
| LED driver bus | **SDA = GPIO4, SCL = GPIO5**, 100 kHz in the stock firmware | stock boot log `I2C0: init ok (SDA: 4, SCL: 5, freq: 100000)` |
| LED driver | **KP18068** (5-channel LED driver) | marking `KP18068ESP` read on the board by the owner |
| Channel order | **OUT1 = blue, OUT2 = red, OUT3 = green, OUT4 = warm white**, OUT5 lights nothing on its own | firmware code, tested on the bulb (owner, 2026-10-11) |
| Current codes | RGB code 5 (= 9 mA), white code 11 (= 27.5 mA), analog dimming, 4 kHz | stock firmware constants, unverified on the bulb |

OUT4 and OUT5 always get the same value, so the bulb is RGB plus one white LED. The module drives both from one template output. The stock firmware
makes the other colour temperatures by mixing red, green and blue into the warm white.

## Light

Read from the stock 2.0.1 firmware. Two exclusive modes, like the Color and White tabs of its web UI:

- **RGB:** level of each colour = colour / 255 * brightness, linear (no gamma), times a fixed white balance: red 0.856, green 0.701, blue 0.749. White is off.
- **Colour temperature 2700-6500 K:** a 9-point table of 10-bit levels, interpolated, times brightness (the gains are not applied here):

| K | 2700 | 3000 | 3500 | 4000 | 4500 | 5000 | 5700 | 6000 | 6500 |
|---|---|---|---|---|---|---|---|---|---|
| white (OUT4 = OUT5) | 1023 | 635 | 483 | 451 | 494 | 490 | 441 | 426 | 425 |
| blue (OUT1) | 0 | 86 | 112 | 182 | 220 | 240 | 267 | 325 | 366 |
| red (OUT2) | 0 | 325 | 314 | 361 | 100 | 17 | 0 | 0 | 0 |
| green (OUT3) | 0 | 314 | 373 | 511 | 600 | 650 | 662 | 659 | 659 |

`gamma_correct` is 1.0 (the stock firmware is linear; the ESPHome default 2.8 makes the lowest steps much darker) and the default fade is 3 s. Not verified: whether
the colours look like the stock firmware (compare the stock web UI and this config at 2700, 4000 and 6500 K). Two details are not copied: the stock firmware
sends a lower RGB current code (`0x03` instead of `0x0A`) at exactly 2700 K, and it starts a transition with a timer of 20 ms steps. The boot state is not copied either: the
stock firmware turns the lamp ON at power-up, ESPHome's default is OFF (set `restore_mode` on the light if you want it).

## Optional packages

All untested on the bulb; each file has its settings in its header. They need the light `bulb` from the hardware file and, for most, the Home Assistant time
(`core/time-homeassistant.yaml`, included by the project).

| File | What it adds |
|---|---|
| `effects/daylight.yaml` | Effect "Daylight": warm, then cool, then warm again between two clock times |
| `effects/daylight-sun.yaml` | Effect "Daylight (sun)": follows the real sun, **set your coordinates first** |
| `effects/scenes.yaml` | Effects Relax, Reading, Focus, Energize, Sunset, Night light, Candle |
| `effects/wakeup.yaml` | Sunrise alarm: switch "Wake alarm", buttons "Sunrise start" and "Sunrise stop" |
| `effects/night.yaml` | Effect "Night (time)": 2700 K at 5 % between two clock times |
| `effects/night-sun.yaml` | Effect "Night (sun)": the same while the sun is below -4 degrees (needs `daylight-sun.yaml`) |
| `multicolor-bulb/overtemp.yaml` | Chip temperature, dims above 75 degC, light off at 90 degC (the chip, not the LEDs) |
| `multicolor-bulb/dim-range.yaml` | Floor and ceiling for the outputs, only needed with gamma 2.8 |


## Install over OTA from the stock firmware

1. `python ota.py partition-csv RGBCCTBulbG3 -o RGBCCTBulbG3-stock.csv` (in a clone of free-shelly-ota), next to your YAML.
2. Add `hardware/lights/multicolor-bulb/ota-stock-layout.yaml` to your config as a package.
3. Compile, then `ota.py build RGBCCTBulbG3 app.ota.bin --esphome-factory app.factory.bin --esphome-yaml <your yaml>` and `ota.py send`; it checks that the installer writes to
   slot 0 and tells you when to run `ota.py restore` first. The [device page](https://github.com/oxynatOr/free-shelly-ota/blob/main/docs/devices/RGBCCTBulbG3.md) has the
   commands and the log lines. Keep UART or USB access as your way back.

The Duo Bulb has a different lamp module (two PWM pins, no I2C): see [duo-bulb-v3.md](duo-bulb-v3.md).
