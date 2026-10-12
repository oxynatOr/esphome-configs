#!/usr/bin/env python3
"""Prepare a release: set the same tag on every github:// reference, set the project versions, update the changelog.

Usage:
  python scripts/bump-tag.py 1.0.0                  dry run, shows what would change
  python scripts/bump-tag.py 1.0.0 --apply          write the changes
  python scripts/bump-tag.py 1.0.0 --owner myname   also replace OWNER in the references and READMEs
  python scripts/bump-tag.py 1.0.0 --apply --git    additionally commit and create the annotated tag v1.0.0

Nothing is ever pushed; the command to do so is printed at the end.
"""
import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YAML_DIRS = ("core", "hardware", "i18n", "projects", "examples")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
GITREF = re.compile(r"(github://[^/\s\"']+/[^/\s\"']+/[^\s\"'@]+)@[A-Za-z0-9._-]+")
PROJECT_VERSION = re.compile(r'(project:\n\s+name: "[^"]+"\n\s+version: )"[^"]*"')


def files():
    for d in YAML_DIRS:
        yield from sorted((ROOT / d).rglob("*.yaml"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version", help="X.Y.Z without the leading v")
    ap.add_argument("--owner", help="GitHub user or organisation that replaces OWNER")
    ap.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    ap.add_argument("--git", action="store_true", help="commit and tag (needs --apply)")
    args = ap.parse_args()

    if not SEMVER.match(args.version):
        sys.exit("version must look like 1.2.3")
    if args.git and not args.apply:
        sys.exit("--git needs --apply")
    tag = f"v{args.version}"

    if args.git:
        if subprocess.run(["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"], cwd=ROOT,
                          capture_output=True).returncode == 0:
            sys.exit(f"tag {tag} already exists - tags are never moved or deleted")

    changed = []
    for path in files():
        text = path.read_text(encoding="utf-8")
        new = GITREF.sub(rf"\1@{tag}", text)
        if args.owner:
            new = new.replace("github://OWNER/", f"github://{args.owner}/")
        if path.parts[-3:-1] != () and "projects" in path.relative_to(ROOT).parts[:1]:
            new = PROJECT_VERSION.sub(rf'\1"{args.version}"', new)
        if new != text:
            changed.append(path)
            if args.apply:
                path.write_text(new, encoding="utf-8", newline="\n")

    if args.owner:
        for readme in ROOT.glob("README*.md"):
            text = readme.read_text(encoding="utf-8")
            new = text.replace("github://OWNER/", f"github://{args.owner}/")
            if new != text:
                changed.append(readme)
                if args.apply:
                    readme.write_text(new, encoding="utf-8", newline="\n")

    log = ROOT / "CHANGELOG.md"
    if log.exists():
        text = log.read_text(encoding="utf-8")
        if f"## [{args.version}]" in text:
            print(f"CHANGELOG already has {args.version}")
        elif "## [Unreleased]" in text:
            entry = f"## [Unreleased]\n\n## [{args.version}] - {datetime.date.today().isoformat()}"
            changed.append(log)
            if args.apply:
                log.write_text(text.replace("## [Unreleased]", entry, 1), encoding="utf-8", newline="\n")
        else:
            print("CHANGELOG.md has no '## [Unreleased]' heading - not touched")

    print(f"{'changed' if args.apply else 'would change'}: {len(changed)} file(s) -> {tag}")
    for path in changed[:15]:
        print("  " + path.relative_to(ROOT).as_posix())
    if len(changed) > 15:
        print(f"  ... and {len(changed) - 15} more")
    if not args.apply:
        print("dry run - add --apply to write")
        return

    check = subprocess.run([sys.executable, str(ROOT / "scripts" / "check.py")], cwd=ROOT)
    if check.returncode != 0:
        sys.exit("check.py failed after the bump - fix the findings before tagging")

    if args.git:
        subprocess.run(["git", "add", "-A", "core", "hardware", "i18n", "projects", "examples", "README.md",
                        "README.de.md", "CHANGELOG.md"], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", f"Release {tag}"], cwd=ROOT, check=True)
        subprocess.run(["git", "tag", "-a", tag, "-m", f"Release {tag}"], cwd=ROOT, check=True)
        print(f"committed and tagged {tag}")
        print(f"publish with:  git push origin main && git push origin {tag}")
    else:
        print("review the diff, then commit and tag yourself or rerun with --git")


if __name__ == "__main__":
    main()
