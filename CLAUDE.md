# ioxys-esphome

Public ESPHome package repository (core / hardware / i18n / projects). Read `CONVENTIONS.md` before
adding or changing any file; it is the single source of truth.

- Run `python scripts/check.py` before finishing any change to YAML and fix everything it reports.
- Place new files with the "Where does a new file go?" rules in `CONVENTIONS.md`; start from `templates/`.
- Never commit secrets, real IPs/MACs or personal data. Never reference `@main`.
- Visible texts go to `i18n/en.yaml` (and `de.yaml` if translated), never hard-coded in modules.
- Do not commit, tag or push without the user asking for it.
