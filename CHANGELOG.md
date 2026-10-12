# Changelog

All notable changes are listed here. Versions follow SemVer, tags look like `v1.2.3`.
`scripts/bump-tag.py` moves the `[Unreleased]` entries under the new version.

## [Unreleased]

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
- Tooling: `scripts/check.py`, `scripts/bump-tag.py`, `scripts/gen-catalog.py`, templates, Claude skill, hook and reviewer agent.
