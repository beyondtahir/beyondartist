#!/usr/bin/env python3
"""Copy the complete skill to a selected host; never overwrite user files."""
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
HOST_DIRS = {'codex': '.agents/skills', 'claude': '.claude/skills', 'hermes': '.hermes/skills'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', choices=sorted(HOST_DIRS), required=True)
    parser.add_argument('--destination', type=Path, help='Explicit full destination skill folder')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    source = ROOT / 'skills/beyondartist'
    target = (args.destination or Path.home() / HOST_DIRS[args.host] / 'beyondartist').expanduser().absolute()
    if not (source / 'SKILL.md').is_file():
        parser.error('Complete skills/beyondartist source not found.')
    if target.exists() or target.is_symlink():
        parser.error('Destination already exists. Inspect it before choosing another destination; no files were changed.')
    if source == target or source in target.parents:
        parser.error('Destination cannot be inside the source skill.')
    if not args.dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
    print(('Would install' if args.dry_run else 'Installed') + ' beyondartist for ' + args.host + ' at ' + str(target))
    print('Start a fresh session and verify discovery. Image tools and durable memory require separate host access.')


if __name__ == '__main__':
    main()
