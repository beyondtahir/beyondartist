#!/usr/bin/env python3
"""Search BeyondArtist Design Memory: cached local Markdown, Python 3.9+ stdlib.

No network, embedding API, model training, visual search or external packages.
Rebuild only after reviewing canonical source changes. Queries fail on stale data.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
INDEX_REL = 'references/library/design-memory-index.json'
SCHEMA = 3
CORPORA = ('foundation', 'pinterest', 'thumbnails', 'style-panels', 'seeds', 'guides', 'provenance')
THUMBNAIL_THRESHOLDS = {'likes': 50, 'reactions': 50, 'saves': 100}
STOPWORDS = set(('a an and are as at be by for from has have how in is it its of on or '
                 'our that the their then these this to use using was we what which '
                 'with you your make want design designs please').split())
ALIASES = {'colours': 'color', 'colour': 'color', 'colors': 'color', 'palettes': 'palette',
           'layouts': 'layout', 'fonts': 'font', 'carousels': 'carousel',
           'hierachy': 'hierarchy', 'hairachy': 'hierarchy', 'textography': 'typography',
           'textgraphy': 'typography', 'earrings': 'earring', 'moodboards': 'moodboard',
           'portraits': 'portrait', 'hooks': 'hook', 'tools': 'tool', 'services': 'service',
           'expressions': 'expression', 'characters': 'character', 'thumbnails': 'thumbnail'}
# Curated foundation routes retained from the original detailed study index.
FACETS = {
    'palette': {3, 4, *range(10, 16), *range(22, 28), *range(63, 83), *range(87, 96)},
    'hierarchy': {1, 2, 7, 8, 16, 28, 30, 31, 38, 43, 44, 48, 49, 50, 53, 54, 58, 59, 61, 84},
    'design-thinking': {*range(31, 38), 45, 46, 47},
    'structure': {2, *range(5, 10), 28, 29, 30, 34, 35, 36, 37, 44, *range(48, 63)},
    'typography': {1, 8, 30, *range(38, 45), 49, 50, 54, 58, 84},
    'style': {1, 10, *range(16, 23), 31, 38, 45, 46, 47, 48, 78, *range(83, 88)},
    'carousel': {1, 2, *range(5, 10), 28, 29, 30},
}
CATEGORY_TERMS = {
    'palette': 'palette color hue saturation burgundy mustard contrast',
    'hierarchy': 'hierarchy focal emphasis priority attention prominence first secondary tertiary',
    'design-thinking': 'brief audience purpose research meaning concept strategy problem',
    'structure': 'structure composition layout grid grouping rhythm spacing sequence',
    'typography': 'typography typographic lettering type font headline serif sans kerning leading',
    'style': 'style texture material illustration photographic collage art',
    'carousel': 'carousel slide swipe sequence',
    'thumbnail': 'thumbnail youtube packaging',
    'hook': 'hook headline punchline curiosity promise',
    'copy': 'copy wording phrase quote language text',
    'motivation': 'motivation motivational encouragement aspiration confidence',
    'service-tool': 'service tool product software workflow benefit feature',
    'character': 'character portrait face expression animal silhouette',
    'lighting': 'lighting light shadow highlights studio',
    'humor': 'humor humorous funny sarcasm sarcastic meme joke',
    'quality-control': 'review quality critique inspect accuracy validation',
}
LIMITS = [
    'Retrieval returns saved written knowledge, not live research or visual similarity.',
    'Sources remain distinct: operational guidance, full screenshot studies, preview observations, and provenance.',
    'The 95 foundation screenshots include repeated captures; 700 Pinterest records cover 694 distinct pin URLs.',
    'Thumbnail studies are admitted separately after visual review and an observed count of at least 50 likes or heart React reactions, or 100 saves. Reactions and saves retain their source labels.',
    'The requested collection requires at least 100 admitted distinct completed-thumbnail or portfolio references; candidate counts alone do not meet that requirement. Saved engagement evidence is dated, not a current count or proof of YouTube performance.',
    'Style panels inherit their board context; source fonts, rights, exact colors and performance remain unverified unless explicitly documented.',
    'Relevance scores are lexical matches, never design quality, audience results or a virality prediction.',
    'Original image checksums are preserved; this text-only tool does not recheck original image bytes.',
]


def digest(value):
    return hashlib.sha256(value.encode('utf-8') if isinstance(value, str) else value).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def tokens(value):
    words = re.findall(r'#?[\w]+', unicodedata.normalize('NFKC', value).casefold())
    return [ALIASES.get(w, w) for w in words if w not in STOPWORDS]


def canonical_id(value):
    value = value.upper()
    return 'FND-' + value[4:] if re.fullmatch(r'ZIP-\d{3}', value) else value


def source_paths(root):
    """Discover knowledge files, including future guide sections and SYS records."""
    refs = root / 'references'
    excluded = {'library-index.md', 'retrieval.md'}  # navigation, not another knowledge copy
    return sorted(p for p in refs.rglob('*.md') if p.name not in excluded)


def source_snapshots(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes()) for p in source_paths(root)}


def sections(text, pattern=r'^## (.+)$'):
    found = list(re.finditer(pattern, text, re.MULTILINE))
    context = text[:found[0].start()].strip() if found else text.strip()
    for i, match in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(text)
        yield match, text[match.start():end].strip() + '\n', context


def inferred_categories(title, body, explicit=()):
    words = set(tokens(title + ' ' + body))
    categories = set(explicit)
    for category, terms in CATEGORY_TERMS.items():
        if words.intersection(tokens(terms)):
            categories.add(category)
    return sorted(categories)


def urls(body):
    return sorted(set(re.findall(r'https?://[^\s<>\)\]`]+', body)))


def make_record(root, path, text, offset, source_id, title, body, context, corpus,
                source_type, categories=None, provenance=None):
    rel = path.relative_to(root).as_posix()
    tags = re.findall(r'^(?:\*\*)?Tags[^\n]*', body, re.MULTILINE)
    cats = categories if categories is not None else inferred_categories(title, body)
    start = text[:offset].count('\n') + 1
    record = {
        'id': source_id, 'aliases': ['ZIP-' + source_id[4:]] if source_id.startswith('FND-') else [],
        'title': title, 'corpus': corpus, 'source_type': source_type, 'categories': cats,
        'tags': tags, 'file': rel, 'line_start': start,
        'line_end': start + len(body.splitlines()) - 1,
        'citation': rel + ':' + str(start),
        'section_sha256': digest(body), 'context_sha256': digest(context),
        'source': provenance or {'urls': urls(body)},
        'printed_hex_codes': sorted(set(re.findall(r'#[0-9a-fA-F]{6}\b', body)), key=str.casefold),
        'content_markdown': body, 'document_context_markdown': context,
    }
    # Context is searchable at low weight, with its own match evidence; it is not a new study.
    counts = Counter(tokens(body))
    record['term_frequencies'] = dict(sorted(counts.items()))
    record['token_count'] = sum(counts.values())
    record['context_terms'] = sorted(set(tokens(context)))
    record['title_terms'] = sorted(set(tokens(title)))
    record['facet_terms'] = sorted(set(tokens(' '.join(cats) + ' ' + ' '.join(tags))))
    return record


def thumbnail_provenance(body, sid):
    """Validate recorded evidence, not its truth or current live Pinterest state.

    Each THUMB section contains one fenced JSON evidence object. Only exact
    integers and explicit integer lower bounds are admitted; ambiguous rounded
    displays remain in the working candidate ledger. The user's Pinterest-like
    criterion includes the observed heart control labelled React, stored as
    reactions rather than relabelled likes or saves.
    """
    def fail(message):
        raise ValueError(sid + ': ' + message)

    def required_text(mapping, key):
        value = mapping.get(key)
        if not isinstance(value, str) or not value.strip():
            fail('Missing evidence field: ' + key)
        return value

    blocks = re.findall(r'^```json\s*\n([\s\S]*?)^```\s*$', body, re.MULTILINE)
    if len(blocks) != 1:
        fail('Expected exactly one fenced JSON evidence object.')
    try:
        source = json.loads(blocks[0])
    except json.JSONDecodeError as error:
        fail('Invalid JSON evidence: ' + str(error))
    if not isinstance(source, dict):
        fail('Evidence must be a JSON object.')
    pin_id = required_text(source, 'pin_id')
    pin_url = required_text(source, 'canonical_pin_url')
    if not re.fullmatch(r'\d+', pin_id) or pin_url != 'https://www.pinterest.com/pin/' + pin_id + '/':
        fail('Canonical Pinterest URL must match the numeric pin_id string.')
    timestamp = required_text(source, 'observed_at')
    try:
        observed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except ValueError:
        fail('observed_at must be an ISO-8601 timestamp with timezone.')
    if observed.utcoffset() is None:
        fail('observed_at must include a timezone.')

    visual = source.get('visual_review')
    if not isinstance(visual, dict) or visual.get('status') != 'inspected':
        fail('Actual visual inspection is required.')
    if visual.get('depth') not in ('pin-detail', 'search-preview'):
        fail('visual_review.depth must state pin-detail or search-preview.')
    required_text(visual, 'evidence_ref')
    metrics = source.get('metrics')
    if not isinstance(metrics, list) or not metrics:
        fail('At least one observed engagement metric is required.')
    qualifying = []
    for metric in metrics:
        if not isinstance(metric, dict):
            fail('Each metric must be an evidence object.')
        kind = metric.get('kind')
        if kind not in ('likes', 'saves', 'reactions'):
            fail('Metric must be likes, saves, or heart React reactions.')
        label = required_text(metric, 'raw_label')
        if kind == 'reactions':
            if not re.search(r'\breact\b', label, re.IGNORECASE) or metric.get('icon') != 'heart':
                fail('Reactions qualify only with the observed React label and heart icon.')
        elif not re.search(r'\b' + ('likes?' if kind == 'likes' else 'saves?') + r'\b', label, re.IGNORECASE):
            fail('Metric kind disagrees with its observed label.')
        display = required_text(metric, 'raw_display').strip()
        match = re.fullmatch(r'(0|[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+)(\+?)', display)
        if not match:
            fail('Unknown, abbreviated or ambiguous engagement count; keep candidate unadmitted.')
        value = metric.get('value')
        if type(value) is not int or value != int(match[1].replace(',', '')):
            fail('Metric value must equal the observed integer count.')
        precision = 'explicit-lower-bound' if match[2] else 'exact'
        if metric.get('precision') != precision:
            fail('Metric precision disagrees with its displayed count.')
        required_text(metric, 'evidence_ref')
        if value >= THUMBNAIL_THRESHOLDS[kind]:
            qualifying.append(kind)
    if not qualifying:
        fail('No observed count reaches 50 likes/heart React reactions or 100 saves.')

    dedupe = source.get('dedupe')
    if not isinstance(dedupe, dict) or dedupe.get('assessment') != 'distinct' or dedupe.get('duplicate_of') is not None:
        fail('Only reviewed distinct artwork may be admitted.')
    required_text(dedupe, 'artwork_group_id')
    existing = dedupe.get('existing_memory_matches', [])
    if not isinstance(existing, list) or any(not isinstance(i, str) for i in existing):
        fail('existing_memory_matches must be a list of canonical IDs.')
    printed = source.get('printed_hex_codes', [])
    if not isinstance(printed, list) or any(not isinstance(c, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', c) for c in printed):
        fail('printed_hex_codes must contain only explicitly printed six-digit source labels.')
    source['urls'] = [pin_url]
    source['qualification'] = {'thresholds': dict(THUMBNAIL_THRESHOLDS), 'qualifying_metric_kinds': sorted(set(qualifying)),
                               'heart_react_counts_as_user_likes': 'reactions' in qualifying}
    return source


def read_records(root):
    lib = root / 'references/library'
    manifest_path = lib / 'foundation-manifest.md'
    manifest = manifest_path.read_text(encoding='utf-8')
    member_rows = re.findall(r'^\| (FND-\d{3}) \| `([^`]+)` \| `([a-f0-9]{64})` \|$', manifest, re.MULTILINE)
    expected = {'FND-%03d' % n for n in range(1, 96)}
    members = {i: {'archive_member': name, 'image_sha256': sha} for i, name, sha in member_rows}
    if len(member_rows) != 95 or set(members) != expected:
        raise ValueError('Foundation manifest must contain exactly FND-001 through FND-095 once.')
    archive_match = re.search(r'Original source:.*SHA-256: `([a-f0-9]{64})`', manifest)
    if not archive_match:
        raise ValueError('Original archive checksum missing in foundation manifest.')
    archive_hash = archive_match.group(1)
    records = []
    for path in source_paths(root):
        text = path.read_text(encoding='utf-8')
        filename = path.name
        if filename == 'foundation-manifest.md':
            continue  # Every row is attached to its study; do not double-index 95 entries.
        if filename in ('foundation-001-048.md', 'foundation-049-095.md'):
            for m, body, context in sections(text, r'^## (FND-\d{3}) — (.+)$'):
                sid, title = m.group(1, 2)
                source = re.search(r'^Source(?: file)?: `([^`]+)`', body, re.MULTILINE)
                if sid not in members or not source or source.group(1) != members[sid]['archive_member']:
                    raise ValueError('Study provenance disagrees with manifest: ' + sid)
                cats = sorted(k for k, ids in FACETS.items() if int(sid[4:]) in ids)
                records.append(make_record(root, path, text, m.start(), sid, title, body, context,
                    'foundation', 'screenshot-study', cats,
                    {'archive': 'Design.zip', 'archive_sha256': archive_hash, **members[sid]}))
        elif re.fullmatch(r'pinterest-0[1-7]\.md', filename):
            number = int(filename[11:12])
            pin_sections = list(sections(text, r'^#{2,3} (PIN-\d-\d{3}) — (.+)$'))
            if pin_sections:
                for m, body, context in pin_sections:
                    records.append(make_record(root, path, text, m.start(), m[1], m[2], body, context,
                        'pinterest', 'visual-preview-study'))
            else:
                rows = list(re.finditer(r'^\| \[(PIN-\d-\d{3})\]\((https://www\.pinterest\.com/pin/\d+/)\) \| (.+)$', text, re.MULTILINE))
                if not rows:
                    raise ValueError('No Pinterest records parsed in ' + filename)
                context = text[:rows[0].start()].strip()
                for m in rows:
                    # Preserve exact source row; the table header travels with the context.
                    body = m[0] + '\n'
                    title = m[3].split('|')[0].strip()
                    records.append(make_record(root, path, text, m.start(), m[1], title, body, context,
                        'pinterest', 'visual-preview-study', provenance={'urls': [m[2]]}))
            found_ids = {r['id'] for r in records if r['file'] == path.relative_to(root).as_posix()}
            if found_ids != {'PIN-%d-%03d' % (number, n) for n in range(1, 101)}:
                raise ValueError('Pinterest set must contain its 100 exact IDs: ' + filename)
        elif filename == 'thumbnail-studies.md':
            studies = list(sections(text, r'^## (THUMB-\d{3,}) — (.+)$'))
            if len(studies) != len(re.findall(r'^#{1,6} THUMB-\S+', text, re.MULTILINE)):
                raise ValueError('Malformed THUMB heading in ' + filename)
            for m, body, context in studies:
                source = thumbnail_provenance(body, m[1])
                record = make_record(root, path, text, m.start(), m[1], m[2], body, context,
                    'thumbnails', 'qualified-thumbnail-study',
                    inferred_categories(m[2], body, ('thumbnail',)), source)
                # Estimated or sampled palette codes are not printed source labels.
                record['printed_hex_codes'] = sorted(set(source.get('printed_hex_codes', [])), key=str.casefold)
                records.append(record)
        elif filename == 'additional-design-tips.md':
            register = {i: {'filename': name, 'visible_label': label.strip(), 'carousel_number': num.strip()}
                        for i, name, label, num in re.findall(r'^\| (TIP-\d{2}) \| `([^`]+)` \| ([^|]+) \| ([^|]+) \|$', text, re.MULTILINE)}
            intro = text[:text.index('## TIP-01')].strip()
            for m, board, _ in sections(text, r'^## (TIP-\d{2}) — (.+)$'):
                # Last board ends at its next generic H2; shared advice is kept in context.
                if '\n## Practical use' in board:
                    board, shared = board.split('\n## Practical use', 1)
                    shared = '## Practical use' + shared
                else:
                    shared_match = re.search(r'^## Practical use[\s\S]*', text, re.MULTILINE)
                    shared = shared_match[0] if shared_match else ''
                rows = list(re.finditer(r'^\| (TIP-\d{2}-[A-Z]{2})([^|]*) \| (.+)$', board, re.MULTILINE))
                if len(rows) != 6 or m[1] not in register:
                    raise ValueError('Style board requires six panels and source register: ' + m[1])
                board_context = intro + '\n\n' + board[:rows[0].start()].strip() + '\n\n' + shared.strip()
                for row in rows:
                    body = row[0] + '\n'
                    # Exact offset is found in original text, not normalized board whitespace.
                    offset = text.index(row[0], m.start())
                    title = m[2] + ' — ' + row[1] + row[2].strip()
                    cats = inferred_categories(m[2], board[:rows[0].start()] + body)
                    records.append(make_record(root, path, text, offset, row[1], title, body, board_context,
                        'style-panels', 'style-board-panel-study', cats,
                        {'board_id': m[1], 'source_collection': 'supplied-style-boards', **register[m[1]]}))
        elif filename == 'pinterest-seeds.md':
            for m, body, context in sections(text, r'^## Seed (\d) — (.+)$'):
                records.append(make_record(root, path, text, m.start(), 'SEED-%02d' % int(m[1]), m[2],
                    body, context, 'seeds', 'larger-view-seed-study'))
        else:
            corpus = 'provenance' if filename == 'research-ledger.md' else 'guides'
            kind = 'research-provenance' if corpus == 'provenance' else 'operational-guidance'
            guide_sections = list(sections(text))
            if not guide_sections:
                records.append(make_record(root, path, text, 0, 'GUIDE-' + path.stem.upper() + '-01',
                    text.splitlines()[0].lstrip('# '), text, '', corpus, kind))
            for n, (m, body, context) in enumerate(guide_sections, 1):
                exact = re.match(r'(SYS-\d{3})\s+[—–-]\s+(.+)', m[1])
                sid = exact[1] if exact else 'GUIDE-' + path.stem.upper() + '-%02d' % n
                title = exact[2] if exact else m[1]
                records.append(make_record(root, path, text, m.start(), sid, title, body, context, corpus, kind))
    ids = [r['id'] for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate canonical record ID found.')
    thumbnail_records = [r for r in records if r['corpus'] == 'thumbnails']
    for field in ('pin_id', 'artwork_group_id'):
        values = [r['source']['pin_id'] if field == 'pin_id' else r['source']['dedupe'][field]
                  for r in thumbnail_records]
        if len(values) != len(set(values)):
            raise ValueError('Duplicate thumbnail ' + field + ' found.')
    for record in thumbnail_records:
        matches = record['source']['dedupe'].get('existing_memory_matches', [])
        if any(sid not in ids or sid == record['id'] for sid in matches):
            raise ValueError('Unknown/self thumbnail existing_memory_matches: ' + record['id'])
    if {i for i in ids if i.startswith('FND-')} != expected:
        raise ValueError('Foundation study coverage must be exactly 95 IDs.')
    counts = Counter(r['corpus'] for r in records)
    if counts['pinterest'] != 700 or counts['style-panels'] != 54 or counts['seeds'] != 7:
        raise ValueError('Incomplete canonical visual corpus: ' + str(dict(counts)))
    return sorted(records, key=lambda r: r['id']), archive_hash


def build_index(root):
    records, archive_hash = read_records(root)
    document_frequency = Counter(term for r in records
                                 for term in set(r['term_frequencies']) | set(r['context_terms']))
    index = {
        'schema_version': SCHEMA, 'name': 'BeyondArtist Design Memory',
        'retrieval': 'Cached BM25 lexical ranking with title and metadata boosts',
        'record_count': len(records), 'counts_by_corpus': dict(sorted(Counter(r['corpus'] for r in records).items())),
        'categories': sorted(set(c for r in records for c in r['categories'])),
        'category_policy': 'Foundation facets are curated; other facets are lexical routing aids, not asserted visual facts.',
        'sources': source_snapshots(root), 'retriever_sha256': digest(Path(__file__).read_bytes()),
        'archive_sha256': archive_hash, 'limits': LIMITS,
        'average_document_length': sum(r['token_count'] for r in records) / len(records),
        'document_frequency': dict(sorted(document_frequency.items())), 'records': records,
    }
    index['payload_sha256'] = digest(canonical(index))
    return index


def load_index(root):
    index = json.loads((root / INDEX_REL).read_text(encoding='utf-8'))
    expected_digest = index.pop('payload_sha256', None)
    if digest(canonical(index)) != expected_digest:
        raise ValueError('Design Memory index checksum mismatch. Review it and rebuild.')
    index['payload_sha256'] = expected_digest
    if index.get('schema_version') != SCHEMA or index.get('retriever_sha256') != digest(Path(__file__).read_bytes()):
        raise ValueError('Retriever/index version changed. Review sources, then run --rebuild-index.')
    current = source_snapshots(root)
    if current != index['sources']:
        changed = sorted(k for k in set(current) | set(index['sources']) if current.get(k) != index['sources'].get(k))
        raise ValueError('Design Memory is stale or has missing/new sources: ' + ', '.join(changed) +
                         '. Review changes, then run --rebuild-index.')
    return index


def rank(index, query, corpus=(), categories=(), requested_ids=()):
    terms = list(dict.fromkeys(tokens(query)))
    ranked = []
    count = index['record_count']
    for record in index['records']:
        if corpus and record['corpus'] not in corpus:
            continue
        if categories and not set(categories).intersection(record['categories']):
            continue
        if requested_ids and record['id'] not in requested_ids:
            continue
        score, matches = 0.0, []
        for term in terms:
            frequency = record['term_frequencies'].get(term, 0)
            primary_match = frequency or term in record['title_terms'] or term in record['facet_terms']
            if not primary_match and term not in record['context_terms']:
                continue
            matches.append(term)
            df = index['document_frequency'].get(term, 0)
            idf = math.log(1 + (count - df + 0.5) / (df + 0.5))
            denominator = frequency + 1.5 * (0.25 + 0.75 * record['token_count'] / index['average_document_length'])
            score += idf * frequency * 2.5 / denominator
            score += 2 * idf if term in record['title_terms'] else 0
            score += 0.65 * idf if term in record['facet_terms'] else 0
            score += 0.15 * idf if not primary_match and term in record['context_terms'] else 0
        if terms and not matches:
            continue
        ranked.append((score, record, matches))
    return sorted(ranked, key=lambda row: (-row[0], row[1]['id'])), terms


def excerpt(body, terms):
    candidates = []
    for position, raw in enumerate(body.splitlines()):
        line = raw.strip()
        if not line or line.startswith(('#', 'Source', '**Authority')):
            continue
        overlap = len(set(tokens(line)).intersection(terms))
        if not terms or overlap:
            candidates.append((-overlap, position, line))
    return '\n'.join(row[2] for row in sorted(sorted(candidates)[:3], key=lambda row: row[1]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', default='')
    parser.add_argument('--corpus', action='append', choices=CORPORA, help='Repeat for OR filtering.')
    parser.add_argument('--category', action='append', help='Exact category; repeat for OR filtering.')
    parser.add_argument('--id', action='append', type=canonical_id, help='Exact record ID. Legacy ZIP-* resolves to FND-*.')
    parser.add_argument('--limit', type=int, default=5)
    parser.add_argument('--full', action='store_true', help='Return exact full source section and context.')
    parser.add_argument('--list-facets', action='store_true', help='Show corpus counts and available categories.')
    parser.add_argument('--validate-index', action='store_true', help='Reparse sources and compare entire derived index.')
    parser.add_argument('--rebuild-index', action='store_true', help='Rebuild only after reviewing source changes.')
    args = parser.parse_args(argv)
    if args.limit < 1:
        parser.error('--limit must be a positive integer.')
    if (args.rebuild_index or args.validate_index or args.list_facets) and (args.query or args.id or args.corpus or args.category or args.full):
        parser.error('Maintenance/facet flags cannot be combined with retrieval arguments.')
    if sum((args.rebuild_index, args.validate_index, args.list_facets)) > 1:
        parser.error('Use one maintenance/facet flag at a time.')
    try:
        if args.rebuild_index:
            index = build_index(ROOT)
            target = ROOT / INDEX_REL
            temporary = target.with_suffix('.json.tmp')
            temporary.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            temporary.replace(target)
        else:
            index = load_index(ROOT)
        if args.validate_index and index != build_index(ROOT):
            raise ValueError('Design Memory cached records differ from parsed canonical sources.')
        if args.rebuild_index or args.validate_index or args.list_facets:
            output = {'name': index['name'], 'status': 'rebuilt' if args.rebuild_index else 'valid',
                      'records': index['record_count'], 'counts_by_corpus': index['counts_by_corpus'],
                      'categories': index['categories'], 'archive_sha256': index['archive_sha256'],
                      'note': 'Text/source integrity checked; original image bytes are not reopened.'}
        else:
            unknown_categories = set(args.category or ()) - set(index['categories'])
            unknown_ids = set(args.id or ()) - {r['id'] for r in index['records']}
            if unknown_categories or unknown_ids:
                raise ValueError('Unknown categories/IDs: ' + ', '.join(sorted(unknown_categories | unknown_ids)))
            ranked, terms = rank(index, args.query, args.corpus or (), args.category or (), args.id or ())
            if args.id and not args.query:
                order = {sid: n for n, sid in enumerate(dict.fromkeys(args.id))}
                ranked.sort(key=lambda row: order[row[1]['id']])
            results = []
            for score, record, matches in (ranked if args.id else ranked[:args.limit]):
                hidden = {'term_frequencies', 'token_count', 'title_terms', 'facet_terms', 'context_terms', 'content_markdown', 'document_context_markdown'}
                result = {k: v for k, v in record.items() if k not in hidden}
                body_excerpt = excerpt(record['content_markdown'], terms)
                result.update(score=round(score, 6) if terms else None, matched_terms=matches,
                              context_matched_terms=[term for term in terms if term in record['context_terms']],
                              excerpt=body_excerpt or excerpt(record['document_context_markdown'], terms),
                              excerpt_source='section' if body_excerpt else 'context')
                if args.full:
                    result.update(content_markdown=record['content_markdown'], document_context_markdown=record['document_context_markdown'])
                results.append(result)
            output = {'name': index['name'], 'method': index['retrieval'], 'query': args.query,
                      'corpora': args.corpus or [], 'categories': args.category or [],
                      'matching_records': len(ranked), 'returned_records': len(results),
                      'archive_sha256': index['archive_sha256'], 'limits': index['limits'], 'results': results}
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
