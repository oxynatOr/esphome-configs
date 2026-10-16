# Conventions

Single source of truth for this repository. `scripts/check.py` enforces everything that can be checked
mechanically; whatever it cannot catch is checked in review.

## Where does a new file go?
1. Works on any device, only with different values (ids, pins, reference values)? -> `hardware/<function>/`,
   parametrised via `substitutions:`.
2. Contains GPIOs or IC variants of one specific model? -> `hardware/<family>/<model>/<revision>.yaml`.
3. A complete, adoptable device? -> `projects/<family>/<revision>.yaml` with `dashboard_import`. Thin: only `packages:`.
4. Infrastructure shared by all devices (api, ota, wifi, time, i2c)? -> `core/`.
5. Visible texts? -> `i18n/en.yaml` (all keys) and optionally `i18n/de.yaml` (overrides).
6. Real calibration values, personal entity ids or credentials of one device -> never here, keep them in the private repo.

Function folders in `hardware/`: `boards`, `sensors`, `diagnostics`, `power-monitoring`, `controllers`, `batteries`,
`meters`, `plugs` (`common`, `addons`, `<model>/<revision>`; the Power Strip lives here too), `lights` (`effects`, `<model>/<revision>`), `ui-elements`.
Use `python scripts/gen-catalog.py` output (`docs/CATALOG.md`) to see what already exists before adding a new file.

## Variants
| Axis | Example | Location |
|---|---|---|
| Chip | ESP32, ESP8266, RP2040 | `hardware/boards/<chip>.yaml` |
| Hardware revision | v2, v3 | `hardware/<family>/<model>/vN.yaml` (includes its board) |
| Software version | 1.0, 1.1 | git tags only, never folders |

## Naming
- Files and directories: `kebab-case`. `.yaml` extension only.
- `id:` values and substitution names: `snake_case`, substitutions prefixed with their module (`wifi_static_ip`).
- User-visible texts: substitutions `txt_<module>_<name>`, defined in `i18n/`.
- `esphome.project.name`: `ioxys.<kebab-name>-<revision>`, one per adoptable file.
- Contract ids that a device family shares (plugs): `relay`, `bvoltage`, `bcurrent`, `bpower`, `benergy`, `ntc_temp`,
  `temp_analog_reading`, `rgb_lights`, `fault_lock`. Lights: the light is `bulb`, the time is `homeassistant_time` (core/time-homeassistant.yaml), the sun
  is `ha_sun` (lights/effects/daylight-sun.yaml). Modules rely on them; do not rename.

## File layout
- Every file starts with the header block (within the first 15 lines):
  `# Purpose:`, `# Requires:`, `# Chip:`, `# Substitutions:` (list them with defaults, or `none`).
- 2 spaces indentation, comments in English, lists indented under their key.
- Defaults for substitutions are documentation values, never real ones.

## Multi-instance modules and sub-devices
- A module that is included several times (batteries, fans, BME680 sensors) creates its **own sub-device** and sets
  `device_id` on every entity. Device and entity ids contain the instance variable:
  ```yaml
  esphome:
    devices:
      - id: battery_${pytes_battery_num}
        name: "${pytes_battery_prefix} ${pytes_battery_num}"
  ```
- Entity names inside such a module are short (`Voltage`, `Cell 3 Voltage`); the sub-device carries the context.
- Single-instance hardware (BL0942, NTC, relay, diagnostics) attaches to the main device, no `device_id`.
- Instances are included with `vars:` (local `!include` with `file:` + `vars:`; remote packages use the long
  form with `files: - path: ... vars:`). The `github://` shorthand cannot take vars.
- A device that several modules share (CT clamps) is created once by the device config; modules take its id as a substitution.

## Hooks into other components
- `!extend` only reaches top-level entities with an id. To hook into a sub-sensor (for example `current` of the BL0942)
  use a `platform: copy` sensor with `internal: true` and put `on_value` / `on_value_range` there.
- An `ota:` entry that other packages extend has `id: ota_esphome`; they use `- id: !extend ota_esphome`.

## Secrets and personal data
- Only `!secret wifi_ssid`, `wifi_password` and `wifi_ap_password` are allowed.
- No real IPs (use 192.0.2.x, 198.51.100.x, 203.0.113.x), MACs, keys, names or passwords.

## Remote references
- Between files inside this repo always `github://OWNER/esphome-configs/<path>@<tag>`, never `@main`.
- All refs in one release use the same tag; `scripts/bump-tag.py` changes them together.
- Adoptable files must have `dashboard_import.package_import_url` pointing to themselves.
- Remote packages cannot ship local files (images, C++ headers, partition tables). Such things stay in the private repo
  or become an external component.

## Languages
- `en.yaml` has every key, other languages only override. Keys unknown to `en.yaml` are errors.
- Included as packages (`i18n_base` first, language after); never via `!include` of a single block.
- Effect names that code compares as strings (`"Live Current"`) stay literal.

## Validation
- `python scripts/check.py` - conventions (fast, run it after every change).
- `python scripts/check.py --esphome` - additionally `esphome config` for every file in `projects/` and `examples/`
  (needs `esphome` and a `secrets.yaml` copied from `secrets.example.yaml`).
- A compile (`esphome compile`) is the only test of C++ lambdas; do it for one project per release.
  On Windows run it from PowerShell (the ESP-IDF installer refuses Git Bash/MSys), clear `IDF_PATH` / `IDF_TOOLS_PATH`
  if they point to a missing install, and keep `PLATFORMIO_CORE_DIR` short (the RP2040 toolchain clone fails on long paths).
- New module = new example in `examples/` (two instances for multi-instance modules).

## Releases
- SemVer tags `vX.Y.Z`. Breaking change = major. Never delete or move a tag.
- Write the changes under `## [Unreleased]` in `CHANGELOG.md`.
- `python scripts/bump-tag.py X.Y.Z --owner <github-user> --apply --git`, review, then push the branch and the tag.
