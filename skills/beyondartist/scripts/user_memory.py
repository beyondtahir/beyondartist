#!/usr/bin/env python3
"""Private per-user and per-project retrieval. Python 3.9+; standard library only."""
import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import uuid

SCHEMA = 1
KINDS = {'identity', 'preference', 'brand', 'brief', 'decision', 'reference',
         'feedback', 'artifact', 'research', 'outcome'}
STATUSES = {'recorded', 'draft', 'approved', 'rejected', 'superseded'}
PROVENANCE = {'user-statement', 'user-upload', 'user-approval', 'observation',
              'agent-decision', 'agent-review', 'measured', 'import'}
SKILL_ROOT = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', value):
        raise ValueError('IDs must be 1–64 lowercase ASCII letters, digits, underscores or hyphens.')
    if value.upper() in {'CON', 'PRN', 'AUX', 'NUL', *['COM%d' % i for i in range(1, 10)],
                         *['LPT%d' % i for i in range(1, 10)]}:
        raise ValueError('Reserved filesystem ID.')
    return value


def root_path(value=None):
    root = Path(value or os.environ.get('BEYONDARTIST_MEMORY_HOME') or
                (Path.home() / '.beyondartist' / 'memory')).expanduser().resolve()
    if root == SKILL_ROOT or SKILL_ROOT in root.parents:
        raise ValueError('Personal memory must live outside the installable skill folder.')
    return root


def profile_dir(root, person):
    path = root / 'profiles' / identifier(person)
    for candidate in (root / 'profiles', path):
        if candidate.is_symlink():
            raise ValueError('Profile paths cannot be symlinks.')
    return path


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(prefix='.memory-', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(directory, timeout=8):
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = directory / '.write-lock'
    deadline = time.monotonic() + timeout
    while True:
        try:
            lock.mkdir(mode=0o700)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ValueError('Memory is busy. Retry after the active writer finishes; '
                                 'a crash-left lock needs operator inspection, not automatic deletion.')
            time.sleep(0.05)
    try:
        yield
    finally:
        lock.rmdir()


def nonempty(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + ' must be nonempty text.')
    return value


def validate_record(record):
    identifier(record['id'])
    nonempty(record['title'], 'title')
    if record['kind'] not in KINDS or record['status'] not in STATUSES:
        raise ValueError('Unknown record kind or status.')
    if record['scope'] not in {'personal', 'project'}:
        raise ValueError('Unknown memory scope.')
    if record['scope'] == 'project':
        identifier(record['project_id'])
    elif record.get('project_id') is not None:
        raise ValueError('Personal record cannot have a project ID.')
    if not isinstance(record['tags'], list) or not all(isinstance(t, str) and t.strip() for t in record['tags']):
        raise ValueError('tags must be a list of nonempty strings.')
    if not isinstance(record['text'], str) or not isinstance(record['data'], dict):
        raise ValueError('text must be text and data must be a JSON object.')
    provenance = record['provenance']
    if not isinstance(provenance, dict) or provenance.get('kind') not in PROVENANCE:
        raise ValueError('provenance.kind must identify the source type.')
    nonempty(provenance.get('reference'), 'provenance.reference')
    if record['status'] == 'approved':
        approval = record.get('approval') or provenance
        if not isinstance(approval, dict) or approval.get('kind') != 'user-approval':
            raise ValueError('Approved records require explicit user-approval provenance.')
        nonempty(approval.get('reference'), 'approval.reference')
    asset = record.get('asset')
    if asset:
        rel = Path(asset['path'])
        if rel.is_absolute() or '..' in rel.parts or len(rel.parts) != 2 or rel.parts[0] != 'assets':
            raise ValueError('Asset path must be a profile-relative assets/file path.')
        if not re.fullmatch(r'[a-f0-9]{64}', asset['sha256']):
            raise ValueError('Asset checksum must be SHA-256.')


def validate_database(db, person):
    if db.get('schema_version') != SCHEMA or db.get('person', {}).get('id') != person:
        raise ValueError('Wrong memory schema or profile identity.')
    for pid, project in db['projects'].items():
        identifier(pid)
        if project['id'] != pid:
            raise ValueError('Project identity mismatch.')
    for rid, record in db['records'].items():
        if record_key(record.get('project_id'), record['id']) != rid:
            raise ValueError('Record identity mismatch.')
        validate_record(record)
        if record['scope'] == 'project' and record['project_id'] not in db['projects']:
            raise ValueError('Record references an unknown project.')


def record_key(project, rid):
    return 'project/' + project + '/' + rid if project else 'personal/' + rid


def load(directory, person):
    path = directory / 'memory.json'
    if not path.exists():
        raise ValueError('Profile not initialized. Run init for this person first.')
    db = read_json(path)
    validate_database(db, person)
    return db


def digest_db(db):
    return hashlib.sha256(json.dumps(db, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def terms(text):
    return re.findall(r'[^\W_]+', text.casefold(), flags=re.UNICODE)


def build_index(db):
    rows = {}
    for rid, record in db['records'].items():
        weights = Counter(terms(record['text'] + ' ' + json.dumps(record['data'], ensure_ascii=False)))
        for word in terms(record['title']):
            weights[word] += 3
        for word in terms(' '.join(record['tags'])):
            weights[word] += 5
        rows[rid] = dict(weights)
    return {'schema_version': SCHEMA, 'source_sha256': digest_db(db), 'terms': rows,
            'terms_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()}


def save(directory, db):
    db['updated_at'] = now()
    validate_database(db, db['person']['id'])
    atomic_json(directory / 'memory.json', db)
    atomic_json(directory / 'index.json', build_index(db))


def init(root, person, name=None, project=None, project_name=None):
    directory = profile_dir(root, person)
    with locked(directory):
        if (directory / 'memory.json').exists():
            db = load(directory, person)
        else:
            db = {'schema_version': SCHEMA, 'person': {'id': person, 'name': name or person},
                  'created_at': now(), 'updated_at': now(), 'projects': {}, 'records': {}}
        if name:
            db['person']['name'] = name
        if project:
            identifier(project)
            db['projects'].setdefault(project, {'id': project, 'name': project_name or project,
                                               'created_at': now(), 'updated_at': now()})
            if project_name:
                db['projects'][project]['name'] = project_name
        save(directory, db)
    return {'root': str(root), 'person': person, 'project': project, 'memory_file': str(directory / 'memory.json')}


def put(root, person, payload, project=None, asset=None):
    directory = profile_dir(root, person)
    if not isinstance(payload, dict):
        raise ValueError('Record input must be a JSON object.')
    permitted = {'id', 'title', 'kind', 'tags', 'status', 'text', 'data', 'provenance', 'approval'}
    if set(payload) - permitted:
        raise ValueError('Unsupported record fields: ' + ', '.join(sorted(set(payload) - permitted)))
    with locked(directory):
        db = load(directory, person)
        if project and identifier(project) not in db['projects']:
            raise ValueError('Initialize the project in this profile first.')
        rid = identifier(payload.get('id') or ('record-' + uuid.uuid4().hex[:16]))
        key = record_key(project, rid)
        old = db['records'].get(key)
        kind = payload.get('kind', 'reference')
        record = {'id': rid, 'scope': 'project' if project else 'personal', 'project_id': project,
                  'title': payload.get('title'), 'kind': kind,
                  'status': payload.get('status', 'draft' if kind == 'artifact' else 'recorded'),
                  'tags': sorted(set(payload.get('tags', []))), 'text': payload.get('text', ''),
                  'data': payload.get('data', {}), 'provenance': payload.get('provenance'),
                  'created_at': old['created_at'] if old else now(), 'updated_at': now(),
                  'revision': old['revision'] + 1 if old else 1,
                  'history': (old.get('history', []) + [{k: v for k, v in old.items() if k != 'history'}]) if old else []}
        if payload.get('approval'):
            record['approval'] = payload['approval']
        if old and old.get('asset'):
            record['asset'] = old['asset']
        validate_record(record)
        if asset:
            source = Path(asset).expanduser().resolve()
            if not source.is_file():
                raise ValueError('Supplied asset file is missing.')
            assets = directory / 'assets'
            if assets.is_symlink():
                raise ValueError('Asset directory cannot be a symlink.')
            assets.mkdir(mode=0o700, exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix='.copy-', dir=str(assets))
            os.close(fd)
            try:
                shutil.copyfile(source, temporary)
                checksum = hashlib.sha256(Path(temporary).read_bytes()).hexdigest()
                suffix = source.suffix.lower() if re.fullmatch(r'\.[a-zA-Z0-9]{1,10}', source.suffix) else '.bin'
                destination = assets / (checksum + suffix)
                if destination.is_symlink():
                    raise ValueError('Asset destination cannot be a symlink.')
                if destination.exists():
                    if hashlib.sha256(destination.read_bytes()).hexdigest() != checksum:
                        raise ValueError('Existing copied asset is damaged; inspect before replacing.')
                else:
                    os.replace(temporary, destination)
                record['asset'] = {'path': destination.relative_to(directory).as_posix(),
                                   'sha256': checksum, 'original_name': source.name,
                                   'bytes': destination.stat().st_size}
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        validate_record(record)
        db['records'][key] = record
        if project:
            db['projects'][project]['updated_at'] = record['updated_at']
        save(directory, db)
    return render_record(directory, record)


def render_record(directory, record, verify=False):
    result = dict(record)
    result.pop('history', None)
    if record.get('asset'):
        path = directory / record['asset']['path']
        exists = path.is_file() and not path.is_symlink()
        state = 'available' if exists else 'missing'
        if verify and exists and hashlib.sha256(path.read_bytes()).hexdigest() != record['asset']['sha256']:
            state = 'checksum-mismatch'
        result['asset'] = dict(record['asset'], absolute_path=str(path), availability=state)
    return result


def retrieve(root, person, project=None, query='', tags=(), kinds=(), statuses=(), limit=8, exact_ids=()):
    directory = profile_dir(root, person)
    # Serialize reads against writes so canonical JSON and cache refer to one snapshot.
    with locked(directory):
        db = load(directory, person)
        if project and identifier(project) not in db['projects']:
            raise ValueError('Unknown project in this profile.')
        cached = directory / 'index.json'
        try:
            index = read_json(cached)
        except (FileNotFoundError, json.JSONDecodeError):
            index = None
        cache_valid = (isinstance(index, dict) and index.get('schema_version') == SCHEMA
                       and index.get('source_sha256') == digest_db(db)
                       and isinstance(index.get('terms'), dict)
                       and set(index['terms']) == set(db['records'])
                       and index.get('terms_sha256') == hashlib.sha256(
                           json.dumps(index['terms'], sort_keys=True).encode()).hexdigest())
        if not cache_valid:
            index = build_index(db)
            atomic_json(cached, index)
        query_terms = set(terms(query))
        rows = []
        for rid, record in db['records'].items():
            if record['scope'] == 'project' and (not project or record['project_id'] != project):
                continue
            if exact_ids and record['id'] not in exact_ids:
                continue
            if not exact_ids and record['status'] not in (set(statuses) if statuses else {'recorded', 'draft', 'approved'}):
                continue
            if tags and not set(tags).issubset(record['tags']):
                continue
            if kinds and record['kind'] not in kinds:
                continue
            score = sum(index['terms'][rid].get(word, 0) for word in query_terms)
            if query_terms and not score:
                continue
            rows.append((score, record))
        rows.sort(key=lambda pair: (pair[0], pair[1]['status'] == 'approved', pair[1]['updated_at'], pair[1]['id']), reverse=True)
        selected = rows if exact_ids else rows[:limit]
        return {'person': db['person'], 'project': db['projects'].get(project),
                'project_catalog': sorted(db['projects'].values(),
                                          key=lambda p: p.get('updated_at', p['created_at']), reverse=True),
                'query': query, 'retrieval': 'local lexical tags/title/text; no network',
                'records': [dict(render_record(directory, row), relevance=score) for score, row in selected],
                'missing_requested_ids': sorted(set(exact_ids) - {row['id'] for _, row in selected})}


def validate(root, person):
    directory = profile_dir(root, person)
    with locked(directory):
        db = load(directory, person)
        index_ok = (directory / 'index.json').exists() and read_json(directory / 'index.json') == build_index(db)
        assets = [render_record(directory, r, verify=True) for r in db['records'].values() if r.get('asset')]
        problems = [{'id': r['id'], 'availability': r['asset']['availability']} for r in assets
                    if r['asset']['availability'] != 'available']
        return {'person': person, 'schema_valid': True, 'index_valid': index_ok,
                'projects': len(db['projects']), 'records': len(db['records']), 'asset_problems': problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', help='Persistent writable root; default BEYONDARTIST_MEMORY_HOME or ~/.beyondartist/memory')
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('init', 'put', 'search', 'context', 'validate', 'profiles'):
        p = commands.add_parser(command)
        if command != 'profiles':
            p.add_argument('--person', required=True)
        if command in ('init', 'put', 'search', 'context'):
            p.add_argument('--project')
        if command == 'init':
            p.add_argument('--name')
            p.add_argument('--project-name')
        if command == 'put':
            p.add_argument('--input', required=True, help='JSON record file; use - for stdin')
            p.add_argument('--asset', help='User-supplied/created local asset to copy into this profile')
        if command in ('search', 'context'):
            p.add_argument('--query', default='')
            p.add_argument('--tag', action='append', default=[])
            p.add_argument('--kind', choices=sorted(KINDS), action='append', default=[])
            p.add_argument('--status', choices=sorted(STATUSES), action='append', default=[])
            p.add_argument('--id', action='append', default=[])
            p.add_argument('--limit', type=int, default=8)
    args = parser.parse_args()
    try:
        root = root_path(args.root)
        if args.command == 'init':
            result = init(root, identifier(args.person), args.name, args.project, args.project_name)
        elif args.command == 'put':
            payload = json.load(sys.stdin) if args.input == '-' else read_json(Path(args.input))
            result = put(root, identifier(args.person), payload, args.project, args.asset)
        elif args.command in ('search', 'context'):
            if args.limit < 1:
                raise ValueError('limit must be positive.')
            result = retrieve(root, identifier(args.person), args.project, args.query,
                              args.tag, args.kind, args.status, args.limit, args.id)
        elif args.command == 'validate':
            result = validate(root, identifier(args.person))
        else:
            result = {'root': str(root), 'profiles': []}
            if (root / 'profiles').exists():
                for directory in sorted((root / 'profiles').iterdir()):
                    if directory.is_dir() and not directory.is_symlink() and (directory / 'memory.json').exists():
                        db = load(directory, identifier(directory.name))
                        result['profiles'].append(db['person'])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == 'validate' and (not result['index_valid'] or result['asset_problems']):
            return 1
        return 0
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
