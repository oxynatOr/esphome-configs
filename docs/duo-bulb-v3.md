# Shelly Duo Bulb E27 Gen3

Packages for the **Shelly Duo Bulb E27 Gen3** (S3BL-D010009AEU, ESP32-C3, 8 MB flash, warm and cold white LEDs on two PWM pins).
Moved here from the example configs of [free-shelly-ota](https://github.com/oxynatOr/free-shelly-ota), which installs ESPHome over the network.

> **Status:** the owner flashed ESPHome over UART and it runs. The OTA route from the stock firmware (profile `DuoBulbG3`) was not run on this bulb yet.
> This version passes `python scripts/check.py --esphome`; the light itself was not measured.

## Files

| File | Purpose |
|---|---|
| `projects/duo-bulb/v3.yaml` | Adoptable device: ties the packages below together |
| `hardware/lights/duo-bulb/v3.yaml` | Hardware: board, two LEDC outputs, `cwww` light |
| `hardware/lights/duo-bulb/ota-stock-layout.yaml` | Optional: Shelly's partition table, so the firmware can be installed over OTA from the stock firmware |

## Pins and values

| Function | Value | Source |
|---|---|---|
| Warm white | GPIO4 (LEDC channel 0), not inverted | stock 2.0.1 firmware, static analysis |
| Cold white | GPIO5 (LEDC channel 1), not inverted | stock 2.0.1 firmware, static analysis |
| PWM | 1 kHz, 11 bit | stock firmware (LEDC timer arguments) |
| Colour temperature range | 2700 K to 6500 K | stock firmware |

None of it was measured on the bulb. If full brightness is dark, add `inverted: true` to the pins.

## Install over OTA from the stock firmware

1. `python ota.py partition-csv DuoBulbG3 -o DuoBulbG3-stock.csv` (in a clone of free-shelly-ota), next to your YAML.
2. Add `hardware/lights/duo-bulb/ota-stock-layout.yaml` to your config as a package.
3. Compile, then `ota.py build DuoBulbG3 app.ota.bin --esphome-factory app.factory.bin --esphome-yaml <your yaml>` and `ota.py send`; the
   [device page](https://github.com/oxynatOr/free-shelly-ota/blob/main/docs/devices/DuoBulbG3.md) has the commands and the log lines.
