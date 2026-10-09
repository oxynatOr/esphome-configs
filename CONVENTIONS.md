# Conventions

Single source of truth for this repository. `scripts/check.py` enforces everything that can be checked
mechanically; whatever it cannot catch is reviewed by the `config-reviewer` agent.

## Where does a new file go?
1. Works on any device, only with different values (ids, pins, reference values)? -> `hardware/<function>/`,
   parametrised via `substitutions:`.
2. Contains GPIOs or IC variants of one specific model? -> `hardware/<family>/<model>/<revision>.yaml`.
3. A complete, adoptable device? -> `projects/<family>/<revision>.yaml` with `dashboard_import`.
4. Infrastructure shared by all devices (api, ota, wifi)? -> `core/`.
5. Visible texts? -> `i18n/en.yaml` (all keys) and optionally `i18n/de.yaml` (overrides).
6. Real calibration values or personal data of one device -> never here, keep them in the private repo.

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
- `esphome.project.name`: `ioxys.<kebab-name>`, one per adoptable file.

## File layout
- Every file starts with the header block (within the first 15 lines):
  `# Purpose:`, `# Requires:`, `# Chip:`, `# Substitutions:` (list them with defaults, or `none`).
- 2 spaces indentation, comments in English.
- Defaults for substitutions are documentation values, never real ones.

## Secrets and personal data
- Only `!secret wifi_ssid` and `!secret wifi_password` are allowed.
- No real IPs (use 192.0.2.x, 198.51.100.x, 203.0.113.x), MACs, keys, names or passwords.

## Remote references
- Between files inside this repo always `github://OWNER/ioxys-esphome/<path>@<tag>`, never `@main`.
- All refs in one release use the same tag; `scripts/bump-tag` changes them together.
- Adoptable files must have `dashboard_import.package_import_url` pointing to themselves.

## Languages
- `en.yaml` has every key, other languages only override. Keys unknown to `en.yaml` are errors.
- Included as packages (`i18n_base` first, language after); never via `!include`.

## Releases
- SemVer tags `vX.Y.Z`. Breaking change = major. Never delete or move a tag.
- Update `CHANGELOG.md`, run `python scripts/check.py --esphome`, then tag.
