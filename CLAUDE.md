# esphome-configs

Public ESPHome package repository (core / hardware / i18n / projects). Read `CONVENTIONS.md` before
adding or changing any file; it is the single source of truth.

- Run `python scripts/check.py` before finishing any change to YAML or scripts and fix everything it reports.
  A PostToolUse hook (`.claude/settings.json`) runs it after every edit of a `.yaml` or `.py` file.
- Adding a file: use the `new-module` skill; start from `templates/`; look at `docs/CATALOG.md` first.
- Before a release or after larger edits: ask the `config-reviewer` agent.
- Never commit secrets, real IPs/MACs or personal data. Never reference `@main`.
- Visible texts go to `i18n/en.yaml` (and `de.yaml` if translated), never hard-coded in modules.
- `__ESPHOME__/` (raw import of the old configs) and `private/` are git-ignored; never copy secrets out of them.
- Do not commit, tag or push without the user asking for it. Releases: `scripts/bump-tag.py`.
- Full validation: `python scripts/check.py --esphome` (esphome and a `secrets.yaml` are needed).
