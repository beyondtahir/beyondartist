#!/usr/bin/env python3
"""Build skill-only and full repository ZIPs from validated allowlisted files."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from validate_repo import ROOT, SKILL, public_paths, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    validate(run_tests=False)
    destination = args.output.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    files = public_paths()
    packages = [
        ('beyondartist-skill-v1.0.1.zip', [(p, Path('beyondartist') / p.relative_to(SKILL)) for p in files if SKILL in p.parents]),
        ('beyondartist-repo-v1.0.1.zip', [(p, Path('beyondartist') / p.relative_to(ROOT)) for p in files]),
    ]
    summaries = []
    for name, members in packages:
        target = destination / name
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            for source, relative in members:
                archive.write(source, relative.as_posix())
        with zipfile.ZipFile(target) as archive:
            if archive.testzip() is not None or len(archive.namelist()) != len(members):
                raise ValueError('Archive integrity failed.')
            for source, relative in members:
                if archive.read(relative.as_posix()) != source.read_bytes():
                    raise ValueError('Archive/source parity failed.')
        summaries.append({'file':name,'bytes':target.stat().st_size,'files':len(members),
                          'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    checksums = '\n'.join(row['sha256'] + '  ' + row['file'] for row in summaries) + '\n'
    (destination / 'SHA256SUMS.txt').write_text(checksums)
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
