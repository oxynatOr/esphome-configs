#!/usr/bin/env python3
"""Claude Code PostToolUse hook: run the repository checks after a YAML file was edited.

Reads the hook JSON from stdin. For *.yaml files inside the repository (not __ESPHOME__/ or private/)
it runs scripts/check.py; on findings it prints them to stderr and exits with 2 so Claude sees them.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = ("__ESPHOME__", "private", ".esphome")


def main():
    try:
        data = json.load(sys.stdin)
        file_path = Path(data.get("tool_input", {}).get("file_path", ""))
    except (ValueError, AttributeError):
        return 0
    if file_path.suffix not in (".yaml", ".py") or not file_path.name:
        return 0
    try:
        rel = file_path.resolve().relative_to(ROOT)
    except ValueError:
        return 0
    if rel.parts and rel.parts[0] in SKIP:
        return 0
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "check.py")], cwd=ROOT,
                         capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stdout + res.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
