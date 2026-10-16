# Shelly Power Strip 4 Gen4

Packages for the **Shelly Power Strip 4 Gen4** (ESP32-C6, four relays, four buttons, two ADE7953 meters on SPI, a ring of 12 WS2812 LEDs, three per outlet).
Moved here from the example configs of [free-shelly-ota](https://github.com/oxynatOr/free-shelly-ota), which installs ESPHome on the strip over the network.

> **Status:** the owner's own config runs on a real strip: ESPHome boots with the package of free-shelly-ota and joins Wi-Fi and Home Assistant (UART log).
> This version was rebuilt from it in the layout of this repository, passes `python scripts/check.py --esphome` and **compiles** together with
> `ota-stock-layout.yaml` (ESPHome 2026.10.0-dev, ESP32-C6, 980 KB of the 3 MB app slot). It was not flashed in this form. Outlets, buttons, LEDs and
> metering were **not** checked by whoever converted it.

## Files

| File | Purpose |
|---|---|
| `projects/power-strip/v4.yaml` | Adoptable device: ties the packages below together |
| `hardware/plugs/power-strip/v4.yaml` | Hardware: board, SPI, two ADE7953, relays, buttons, LED ring |
| `hardware/plugs/power-strip/ota-stock-layout.yaml` | Optional: Shelly's partition table, so the firmware can be installed over OTA from the stock firmware |

## Pins

| Function | Pin | Status |
|---|---|---|
| SPI MISO / MOSI / SCLK | GPIO12 / GPIO11 / GPIO13 | matches the stock firmware's boot log (`SPI2 init`) |
| ADE7953 chip select (outlets 1+2 / 3+4) | GPIO15 / GPIO10 | matches the stock boot log (`CS0/1/2: 15/10/-1`) |
| ADE7953 IRQ (chip 0 / chip 1) | GPIO6 / GPIO7 | in use on the owner's device |
| Relays 1 to 4 | GPIO4 / GPIO2 / GPIO3 / GPIO1 | in use on the owner's device |
| Buttons 1 to 4 | GPIO20 / GPIO22 / GPIO23 / GPIO21 | in use on the owner's device (pull-up, inverted) |
| LED ring (WS2812, 12 LEDs, 3 per outlet) | GPIO18 | in use on the owner's device |

## Install over OTA from the stock firmware

1. Save Shelly's partition table next to your YAML: `python ota.py partition-csv PowerStrip -o PowerStrip-stock.csv` (in a clone of free-shelly-ota).
2. Add `hardware/plugs/power-strip/ota-stock-layout.yaml` to your config as a package (it sets the table, `CONFIG_PARTITION_TABLE_OFFSET: "0x10000"` and
   `allow_partition_access: true`). A default ESPHome build uses `0x8000`; `ota.py build` refuses it.
3. Compile, then `ota.py build PowerStrip app.ota.bin --esphome-factory app.factory.bin --esphome-yaml <your yaml>` and `ota.py send`. The device page
   [PowerStrip](https://github.com/oxynatOr/free-shelly-ota/blob/main/docs/devices/PowerStrip.md) has the commands and the log lines to look for.

On a strip running stock **1.7.99** a direct `send` did not work (the app landed in slot 1 and the old app started again). It worked after one official update
to 2.0.1. The log line `Will write to slot 0` is the one you want. After a successful install the UART log shows ESPHome's second stage bootloader,
`ota data partition invalid and no factory, will try all partitions` (expected) and `Loaded app from partition at offset 0x20000`.

## What differs from the owner's own config

The owner's config adds a few things that depend on the network and are left out of the shared packages. Add them to your adopted config if you want them:

- Wi-Fi options: hidden network, `fast_connect`, `power_save_mode: NONE`, `output_power: 20db`, `min_auth_mode: WPA2`, a static address.
- `web_server` on port 80, OTA encryption (`Encryption: required` in the owner's boot log), a fixed API key.
- Safe mode values: the shared package uses 5 min, 10 attempts, 1 min, which are the owner's values as well.
- The Wi-Fi diagnostics come from `hardware/diagnostics/wifi.yaml` (the owner's include files were replaced by the shared ones).
