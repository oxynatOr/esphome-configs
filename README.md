# ioxys-esphome

Reusable ESPHome packages and adoptable device configs. [Deutsch](README.de.md)

## Layout
| Folder | Content |
|---|---|
| `core/` | api, ota, wifi |
| `hardware/` | building blocks by function (boards, sensors, power monitoring, lighting ...) |
| `i18n/` | user-visible texts (`en` complete, `de` overrides) |
| `projects/` | complete devices, adoptable through the ESPHome dashboard |
| `templates/` | starting points for new files |

## Adopt a device
1. Flash a device with a config from `projects/` (or use its web installer when available).
2. Open the ESPHome dashboard, the device appears as *discovered*, click *Adopt*.
3. Your `secrets.yaml` needs `wifi_ssid` and `wifi_password` (see `secrets.example.yaml`).

## Language
Add the language package after the base one, remove the line for English:
```yaml
packages:
  i18n_base: github://OWNER/ioxys-esphome/i18n/en.yaml@<tag>
  i18n_lang: github://OWNER/ioxys-esphome/i18n/de.yaml@<tag>
```
Entity ids in Home Assistant are derived from the name, so a device adopted in another language gets other ids.

## Contributing
See [CONVENTIONS.md](CONVENTIONS.md) and run `python scripts/check.py`.
