# Changelog

All notable changes are listed here. Versions follow SemVer, tags look like `v1.2.3`.
`scripts/bump-tag.py` moves the `[Unreleased]` entries under the new version.

## [Unreleased]

### Added
- Devices moved here from the example configs of free-shelly-ota: Shelly Power Strip 4 Gen4 (`projects/power-strip/v4.yaml`, hardware in `hardware/plugs/power-strip/`),
  Shelly Multicolor Bulb E27 Gen3 (`projects/multicolor-bulb/v3.yaml`, hardware in `hardware/lights/multicolor-bulb/`, KP18068 driver and `rgbw_ct_table` light from
  `oxynatOr/esphome-kp18058`, pinned commit) and Shelly Duo Bulb E27 Gen3 (`projects/duo-bulb/v3.yaml`, hardware in `hardware/lights/duo-bulb/`). Each has an optional
  `ota-stock-layout.yaml` for the install over OTA from the stock firmware (needs the stock CSV from `ota.py partition-csv`).
- New function folder `hardware/lights/`: the light effects as packages (`effects/`: daylight by time and by sun, night by time and by sun, scenes, sunrise alarm),
  and for the Multicolor Bulb over-temperature protection and a dim range. `examples/multicolor-bulb-full.yaml` includes all of them.
- Texts for these devices in `i18n/en.yaml` (`txt_strip_*`, `txt_light_*`, effect names included). No German overrides yet.
- Documents `docs/power-strip-v4.md`, `docs/multicolor-bulb-v3.md` and `docs/duo-bulb-v3.md` (pins, status, what is untested).

### Fixed
- `hardware/plugs/plug-m/ota-stock-layout.yaml`: together with the project it failed with "ID ota_esphome redefined" (a second `platform: esphome` entry does not merge
  with the one of `core/ota.yaml`). It extends that entry now (`- id: !extend ota_esphome`) and only adds `allow_partition_access: true`, as the stock layouts of the
  Power Strip and the bulbs do.

## [0.1.0] - 2026-10-12

### Added
- Core packages: api, ota, safe mode, logger, preferences, SNTP and Home Assistant time, WiFi (DHCP, static), I2C, UART.
- Diagnostics: uptime and version, WiFi, ESP32 (heap, chip temperature), Pico, debug (with and without PSRAM).
- Sensors: BME280, BME680 (multi-instance, own sub-device), BME680/BME688 with BSEC2, DS18B20 on a 1-Wire hub, NTC.
- Power monitoring: BL0942 (with runtime calibration), HLW8012/BL0937, CSE7766, PZEM-004T, energy counters.
- Controllers: PID fan/heater (own sub-device) with PWM outputs for ESP32 and RP2040, and an autotune package.
- Batteries: Pytes E-Box (generated, own sub-device per battery).
- Devices: Shelly Plug M Gen3 and Plug S Gen3 (protection, status LED, add-ons), Shelly PM Mini Gen3,
  NOUS A1T, Gosund SP1, Meross-style CSE7766 plug.
- UI: colour palettes.
- Languages: English reference and German overrides.
- Tooling: `scripts/check.py`, `scripts/bump-tag.py`, `scripts/gen-catalog.py` and templates.
