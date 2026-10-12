---
name: new-module
description: Create a new building block, device revision or adoptable project in this ESPHome repository in the right folder, with header block, prefixed substitutions, i18n keys, a validation example and a changelog entry. Use whenever a new YAML file should be added to core/, hardware/ or projects/.
---

# New module

Follow `CONVENTIONS.md`; it is the single source of truth. This skill is the checklist for adding a file.

## 1. Decide where it goes
Use the "Where does a new file go?" rules in `CONVENTIONS.md`. In short:
- generic block, only values differ -> `hardware/<function>/<name>.yaml`
- model specific (pins, IC variant) -> `hardware/<family>/<model>/<revision>.yaml`
- complete adoptable device -> `projects/<family>/<revision>.yaml` (thin: only packages)
- shared infrastructure -> `core/`
- texts -> `i18n/en.yaml`

If something similar exists (`Glob hardware/**`, `docs/CATALOG.md`), extend or reuse it instead of copying.

## 2. Start from a template
- `templates/module.yaml` for blocks, `templates/project.yaml` for adoptable projects.
- Fill the header block: `# Purpose:`, `# Requires:`, `# Chip:`, `# Substitutions:` (all with defaults).

## 3. Write it
- Substitution names: `snake_case` with the module prefix (`ds18b20_resolution`), always with a default that works.
- Visible names: `${txt_<module>_<name>}`, never literal strings; add the key to `i18n/en.yaml`
  (and the German text to `i18n/de.yaml` if known). Effect names that code compares by string stay literal.
- IDs: `snake_case`. Keep the contract ids of the family (plugs: `relay`, `bvoltage`, `bcurrent`, `bpower`, `ntc_temp`, `rgb_lights`).
- Hooks into sub-sensors of another component (for example the BL0942) use a `platform: copy` sensor, not `!extend`.
- Multi-instance modules (batteries, fans, several sensors) create their own sub-device:
  `esphome: devices: [{id: <name>_${..._id}, name: "..."}]` and `device_id: <name>_${..._id}` on each entity.
  Single-instance hardware does not use sub-devices.
- Pins and chip specifics are substitutions or live in the revision file, never in generic blocks.
- No real IPs, MACs, keys or personal entity ids; only `!secret wifi_ssid`, `wifi_password`, `wifi_ap_password`.
- References between repository files: `github://OWNER/ioxys-esphome/<path>@v0.0.0`, never `@main`.

## 4. Prove it
- Add a small config to `examples/` (or a project) that includes the module; multi-instance modules get two instances.
- `python scripts/gen-catalog.py` to refresh `docs/CATALOG.md`.
- `python scripts/check.py --esphome` (needs `esphome` and a `secrets.yaml` copied from `secrets.example.yaml`) must pass.
- Add a line under `## [Unreleased]` in `CHANGELOG.md`.

Do not commit or tag unless asked.
