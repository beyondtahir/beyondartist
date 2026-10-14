#!/usr/bin/env python3
"""Validate the portable repo, source index, assets, links and private-data boundary."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/beyondartist'
PUBLIC_FILES = {'README.md', 'LICENSE', 'ASSET-LICENSE.md', 'CONTRIBUTING.md', 'AGENTS.md', 'plugin.json', '.gitignore'}
PUBLIC_DIRS = {'assets', 'docs', 'examples', 'scripts', 'skills', '.github'}
EXCLUDED_PARTS = {'.git', '__pycache__', '.pytest_cache', 'dist', 'build', 'preview'}
PRIVATE_PARTS = {'profiles', 'private', 'user-data', '.beyondartist', 'memory'}
PRIVATE_PATTERNS = [
    r'/Users/[A-Za-z0-9_.-]+/', r'IMG_\d+\.(?:heic|HEIC)',
    r'\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}/Pasted text\.txt',
    r'WhatsApp Image \d{4}-',
    r'(?<![A-Za-z0-9])(?:ghp|gho|github_pat|sk-proj)_[A-Za-z0-9_-]{16,}'
]


def public_paths():
    result = []
    for path in ROOT.rglob('*'):
        if not path.is_file() and not path.is_symlink():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError('Symlinks are not release assets: ' + str(rel))
        if any(part in PRIVATE_PARTS for part in rel.parts) or path.name.startswith('.env'):
            raise ValueError('Private/runtime file in repo: ' + str(rel))
        if rel.parts[0] not in PUBLIC_DIRS and rel.as_posix() not in PUBLIC_FILES:
            raise ValueError('Unrecognized distribution file: ' + str(rel))
        if path.suffix in {'.pyc', '.heic', '.HEIC', '.pem', '.key', '.log'} or path.name == '.DS_Store':
            raise ValueError('Unexpected private/cache file: ' + str(rel))
        result.append(path)
    return sorted(result)


def check_links(paths):
    checked = 0
    for path in paths:
        if path.suffix != '.md':
            continue
        text = path.read_text()
        # Avoid treating literal documentation schemas/code as navigable links.
        text = re.sub(r'(?ms)^([~' + chr(96) + r']{3,}).*?^\1\s*$', '', text)
        urls = re.findall(r'\]\(([^)\s]+)\)', text)
        urls += re.findall(r'(?:href|src)="([^"]+)"', text)
        for url in urls:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            target = (path.parent / unquote(parts.path)).resolve()
            if ROOT not in target.parents and target != ROOT:
                raise ValueError('Link leaves distribution: ' + str(path.relative_to(ROOT)) + ' → ' + url)
            if not target.exists():
                raise ValueError('Broken local link: ' + str(path.relative_to(ROOT)) + ' → ' + url)
            checked += 1
    return checked


def validate(run_tests=True):
    paths = public_paths()
    required = ['README.md','plugin.json','docs/getting-started.md','docs/creative-system.md',
                'docs/memory.md','docs/automation.md','docs/gallery.md','docs/sources.md',
                'assets/brand/banner.png','assets/brand/beyondartist-logo.png','skills/beyondartist/SKILL.md']
    for name in required:
        if not (ROOT / name).is_file():
            raise ValueError('Missing ' + name)
    plugin = json.loads((ROOT / 'plugin.json').read_text())
    skill_text = (SKILL / 'SKILL.md').read_text()
    if plugin['name'] != 'beyondartist' or plugin['version'] != '1.0.1' or 'version: "1.0.1"' not in skill_text:
        raise ValueError('Release metadata must agree at 1.0.1.')
    description = re.search(r'^description: (.+)$', skill_text, re.M)[1]
    if len(description) > 200:
        raise ValueError('Portable skill description exceeds 200 characters.')
    for path in paths:
        if path.suffix in {'.md','.json','.yaml','.yml','.py'}:
            content = path.read_text()
            # Pattern definitions are validation code, not actual leaked source data.
            if path == Path(__file__).resolve():
                content = content[content.index('def public_paths'): ]
            for pattern in PRIVATE_PATTERNS:
                if re.search(pattern, content):
                    raise ValueError('Private marker found in ' + str(path.relative_to(ROOT)))
    catalog = json.loads((ROOT / 'assets/showcase/catalog.json').read_text())
    works = [row for row in catalog if row['role'] == 'showcase']
    brands = [row for row in catalog if row['role'] == 'identity']
    if len(works) != 16 or len(brands) != 1 or len({row['id'] for row in catalog}) != 17:
        raise ValueError('Expected 16 selected artworks and one banner.')
    expected_pngs = {row['file'] for row in catalog} | {'assets/brand/beyondartist-logo.png','assets/brand/beyondartist-icon.png'}
    actual_pngs = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'assets').rglob('*.png')}
    if actual_pngs != expected_pngs:
        raise ValueError('Image set differs from the authorized asset catalog.')
    for row in catalog:
        p = ROOT / row['file']
        data = p.read_bytes()
        if data[:8] != b'\x89PNG\r\n\x1a\n' or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Invalid or changed original image: ' + row['file'])
        width, height = struct.unpack('>II', data[16:24])
        if [width, height] != [row['width'], row['height']]:
            raise ValueError('Image dimensions changed: ' + row['file'])
    checked = check_links(paths)
    subprocess.run([sys.executable, str(SKILL / 'scripts/retrieve_library.py'), '--validate-index'], check=True)
    if run_tests:
        subprocess.run([sys.executable,'-m','unittest','discover','-s',str(SKILL / 'tests'),'-p','test_*.py'], check=True)
    return {'version':'1.0.1','files':len(paths),'showcase_artworks':16,'identity_banner':1,
            'local_links_checked':checked,'private_marker_scan':'passed',
            'shared_index':'valid','tests':'run' if run_tests else 'not-repeated'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-tests', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(validate(not args.skip_tests), indent=2))
    except (ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
