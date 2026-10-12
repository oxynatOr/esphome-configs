#!/usr/bin/env python3
"""Consistency checks for ioxys-esphome (see CONVENTIONS.md).

Usage: python scripts/check.py [--esphome]
  --esphome  additionally run `esphome config` for every file in projects/ and examples/
             (needs esphome installed and a secrets.yaml next to the repo root)
"""
import importlib.util
import re
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIRS = ["core", "hardware", "i18n", "projects", "examples", "templates"]
HEADER_DIRS = {"core", "hardware", "i18n", "projects", "templates"}
TAG_DIRS = {"core", "hardware", "i18n", "projects"}
ALLOWED_SECRETS = {"wifi_ssid", "wifi_password", "wifi_ap_password"}
PROJECT_PREFIX = "ioxys."
DOC_IP_PREFIXES = ("192.0.2.", "198.51.100.", "203.0.113.", "0.0.0.0", "255.255.255.")

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
MAC_RE = re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")
SECRET_RE = re.compile(r"!secret\s+([^\s#]+)")
TXT_REF_RE = re.compile(r"\$\{?(txt_[a-z0-9_]+)\}?")
GITREF_RE = re.compile(r"github://([^/\s\"']+)/([^/\s\"']+)/([^\s\"'@]+)@([A-Za-z0-9._-]+)")


class Loader(yaml.SafeLoader):
    """SafeLoader that tolerates ESPHome's custom tags (!secret, !lambda, !include ...)."""


def _any_tag(loader, _suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node, deep=True)
    return loader.construct_mapping(node, deep=True)


Loader.add_multi_constructor("!", _any_tag)

errors = []


def err(path, msg):
    errors.append(f"{path.relative_to(ROOT).as_posix()}: {msg}")


def yaml_files():
    for d in CONTENT_DIRS:
        base = ROOT / d
        if base.is_dir():
            yield from sorted(base.rglob("*.yaml"))


def walk_ids(path, obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "id" and isinstance(v, str) and "${" not in v and not SNAKE.match(v):
                err(path, f"id '{v}' is not snake_case")
            walk_ids(path, v)
    elif isinstance(obj, list):
        for item in obj:
            walk_ids(path, item)


def subs_of(data):
    subs = data.get("substitutions") if isinstance(data, dict) else None
    return subs if isinstance(subs, dict) else {}


def main():
    run_esphome = "--esphome" in sys.argv
    parsed = {}
    refs = {}

    for path in yaml_files():
        rel = path.relative_to(ROOT)
        top = rel.parts[0]
        text = path.read_text(encoding="utf-8")

        # naming
        for part in rel.parts[:-1]:
            if not KEBAB.match(part):
                err(path, f"directory '{part}' is not kebab-case")
        if not KEBAB.match(path.stem):
            err(path, "file name is not kebab-case")

        # parse
        try:
            data = yaml.load(text, Loader=Loader)
        except yaml.YAMLError as e:
            err(path, f"YAML error: {str(e).splitlines()[0]}")
            continue
        parsed[path] = data

        # header block
        if top in HEADER_DIRS:
            head = "\n".join(text.splitlines()[:15])
            for key in ("# Purpose:", "# Substitutions:"):
                if key not in head:
                    err(path, f"header block is missing '{key}' in the first 15 lines")

        # substitutions naming
        for key in () if top == "templates" else subs_of(data):
            if not SNAKE.match(str(key)):
                err(path, f"substitution '{key}' is not snake_case")
            if top == "i18n" and not str(key).startswith("txt_"):
                err(path, f"i18n key '{key}' must start with 'txt_'")

        walk_ids(path, data)

        # secrets, IPs, MACs
        for name in SECRET_RE.findall(text):
            if name not in ALLOWED_SECRETS:
                err(path, f"!secret '{name}' is not in the allowed list {sorted(ALLOWED_SECRETS)}")
        for ip in IP_RE.findall(text):
            if not ip.startswith(DOC_IP_PREFIXES):
                err(path, f"IP address '{ip}' (use documentation ranges 192.0.2.x etc.)")
        for mac in MAC_RE.findall(text):
            err(path, f"MAC address '{mac}' must not be committed")

        # remote refs
        if top in TAG_DIRS:
            for _owner, _repo, _file, ref in GITREF_RE.findall(text):
                refs.setdefault(ref, []).append(path)

        # projects
        if top == "projects":
            check_project(path, rel, data)

    # tag consistency
    for bad in ("main", "master"):
        for p in refs.get(bad, []):
            err(p, f"reference @{bad} is not allowed, use a release tag")
    if len(refs) > 1:
        err(ROOT / "README.md", f"mixed @refs in one release: {sorted(refs)}")

    check_i18n(parsed)
    check_catalog()

    if run_esphome:
        run_esphome_config()

    if errors:
        print(f"{len(errors)} problem(s) found:")
        for e in errors:
            print("  - " + e)
        return 1
    print(f"OK ({len(parsed)} YAML files checked)")
    return 0


def check_project(path, rel, data):
    if not isinstance(data, dict):
        err(path, "project is not a mapping")
        return
    project = (data.get("esphome") or {}).get("project") or {}
    name = str(project.get("name", ""))
    if not name.startswith(PROJECT_PREFIX):
        err(path, f"esphome.project.name must start with '{PROJECT_PREFIX}'")
    if not project.get("version"):
        err(path, "esphome.project.version is missing")
    url = str((data.get("dashboard_import") or {}).get("package_import_url", ""))
    m = GITREF_RE.search(url)
    if not m:
        err(path, "dashboard_import.package_import_url is missing or malformed")
    elif m.group(3) != rel.as_posix():
        err(path, f"package_import_url points to '{m.group(3)}', expected '{rel.as_posix()}'")


def check_i18n(parsed):
    en_path = ROOT / "i18n" / "en.yaml"
    if en_path not in parsed:
        return
    en_keys = set(subs_of(parsed[en_path]))
    for path, data in parsed.items():
        if path.parent == en_path.parent and path != en_path:
            for key in subs_of(data):
                if key not in en_keys:
                    err(path, f"key '{key}' does not exist in en.yaml")
    for path in parsed:
        if path.parent == en_path.parent:
            continue
        for ref in set(TXT_REF_RE.findall(path.read_text(encoding="utf-8"))):
            if ref not in en_keys:
                err(path, f"uses ${{{ref}}} which is not defined in en.yaml")


def check_catalog():
    """docs/CATALOG.md must match the header blocks (python scripts/gen-catalog.py)"""
    spec = importlib.util.spec_from_file_location("gen_catalog", ROOT / "scripts" / "gen-catalog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target = ROOT / "docs" / "CATALOG.md"
    if not target.exists() or target.read_text(encoding="utf-8") != module.build():
        errors.append("docs/CATALOG.md: stale - run python scripts/gen-catalog.py")


def run_esphome_config():
    exe = shutil.which("esphome")
    if not exe:
        errors.append("--esphome given but esphome is not installed")
        return
    if not (ROOT / "secrets.yaml").exists():
        errors.append("--esphome needs secrets.yaml (copy secrets.example.yaml)")
        return
    # remote refs (github://owner/repo/<path>@tag) are replaced by local includes in a temp copy
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        ref_line = re.compile(r"^(\s*(?!package_import_url)[A-Za-z0-9_-]+:\s*)github://[^/\s]+/[^/\s]+/(\S+?)@\S+\s*$", re.M)
        for d in ("core", "hardware", "i18n", "projects", "examples"):
            for src in (ROOT / d).rglob("*.yaml"):
                dst = tmp / src.relative_to(ROOT)
                dst.parent.mkdir(parents=True, exist_ok=True)
                text = src.read_text(encoding="utf-8")
                text = ref_line.sub(lambda m: f"{m.group(1)}!include {(tmp / m.group(2)).as_posix()}", text)
                dst.write_text(text, encoding="utf-8", newline="\n")
        targets = sorted((tmp / "projects").rglob("*.yaml")) + sorted((tmp / "examples").rglob("*.yaml"))
        for path in targets:
            shutil.copy(ROOT / "secrets.yaml", path.parent / "secrets.yaml")  # !secret is resolved next to the main config
            res = subprocess.run([exe, "config", str(path)], capture_output=True, text=True, cwd=tmp)
            if res.returncode != 0:
                lines = (res.stdout + res.stderr).strip().splitlines()
                at = next((i for i, l in enumerate(lines) if l.startswith("Failed config")), None)
                tail = [l for l in lines[at + 1:at + 14] if l.strip()][:6] if at is not None else lines[-8:]
                err(ROOT / path.relative_to(tmp), "esphome config failed:\n      " + "\n      ".join(tail))


if __name__ == "__main__":
    sys.exit(main())
