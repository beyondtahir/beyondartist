"""Meaningful retrieval/integrity regression checks; never mutate installed sources."""
import importlib.util
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('design_memory', ROOT / 'scripts/retrieve_library.py')
memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory)


class DesignMemoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = memory.build_index(ROOT)
        cls.by_id = {r['id']: r for r in cls.index['records']}

    def top(self, query, corpus='guides', category=None, limit=3):
        ranked, _ = memory.rank(self.index, query, [corpus], [category] if category else [])
        return [record['id'] for _, record, _ in ranked[:limit]]

    def test_all_visual_records_preserved(self):
        counts = self.index['counts_by_corpus']
        self.assertEqual((counts['foundation'], counts['pinterest'], counts['style-panels'], counts['seeds']),
                         (95, 700, 54, 7))
        self.assertEqual(len(self.by_id), self.index['record_count'])
        for number in range(1, 96):
            record = self.by_id['FND-%03d' % number]
            self.assertEqual(record['aliases'], ['ZIP-%03d' % number])
            self.assertEqual(len(record['source']['image_sha256']), 64)
            self.assertEqual(record['source']['archive_sha256'], self.index['archive_sha256'])

    def test_every_cached_section_is_verbatim_source_lines(self):
        for record in self.index['records']:
            with self.subTest(record=record['id']):
                lines = (ROOT / record['file']).read_text(encoding='utf-8').splitlines()
                source = '\n'.join(lines[record['line_start'] - 1:record['line_end']]).strip() + '\n'
                self.assertEqual(source, record['content_markdown'])
                self.assertEqual(memory.digest(source), record['section_sha256'])
                self.assertTrue(record['citation'].endswith(':' + str(record['line_start'])))

    def test_legacy_exact_lookup_and_filters(self):
        sid = memory.canonical_id('zip-068')
        self.assertEqual(sid, 'FND-068')
        rows, _ = memory.rank(self.index, '', ['foundation'], ['palette'], [sid])
        self.assertEqual([r['id'] for _, r, _ in rows], ['FND-068'])
        self.assertIn('#F7B538', rows[0][1]['printed_hex_codes'])
        self.assertEqual(memory.rank(self.index, '', ['pinterest'], [], [sid])[0], [])

    def test_foundation_palette_relevance(self):
        self.assertIn('FND-068', self.top('xanthous burgundy', 'foundation', 'palette'))
        self.assertIn('FND-059', self.top('negative space', 'foundation', 'structure'))

    def test_carousel_hook_and_flow_relevance(self):
        self.assertIn('SYS-005', self.top('carousel hook narrative payoff', category='carousel'))

    def test_phrase_and_motivation_relevance(self):
        self.assertIn('SYS-002', self.top('phrase quote idea'))
        self.assertIn('SYS-003', self.top('motivation specific believable'))

    def test_service_tool_relevance(self):
        self.assertEqual(self.top('tool service relatable consequence')[0], 'SYS-004')

    def test_typography_priority_relevance(self):
        self.assertIn('SYS-009', self.top('typography major decision', category='typography'))

    def test_artist_hierarchy_relevance(self):
        self.assertEqual(self.top('viewer intended path attention')[0], 'SYS-012')
        self.assertIn('SYS-013', self.top('artistic priority order'))

    def test_adaptive_questionnaire_relevance(self):
        self.assertIn('SYS-024', self.top('starting questionnaire rough prompt platform purpose'))

    def test_vidiq_packaging_and_visible_copy_relevance(self):
        self.assertIn('SYS-025', self.top('vidiq category thumbnail title visible text scoring'))

    def test_shared_learning_and_private_brief_boundary_relevance(self):
        self.assertIn('SYS-026', self.top('private test prompts excluded shared training'))

    def test_art_form_and_reference_craft_relevance(self):
        self.assertEqual(self.top('statue must look carved instead of face photo')[0], 'SYS-022')
        self.assertEqual(self.top('learn emotional brushwork and retain rich reference detail')[0], 'SYS-021')

    def test_pinterest_content_and_provenance(self):
        self.assertIn('PIN-2-005', self.top('rope swipe', 'pinterest', limit=5))
        record = self.by_id['PIN-7-024']
        self.assertEqual(record['source_type'], 'visual-preview-study')
        self.assertTrue(record['source']['urls'][0].startswith('https://www.pinterest.com/pin/'))
        self.assertIn('preview', record['document_context_markdown'].lower())

    def test_style_panels_keep_geometry_and_board_context(self):
        record = self.by_id['TIP-09-TR']
        self.assertIn('middle left', record['content_markdown'])
        self.assertIn('Panel geometry', record['document_context_markdown'])
        self.assertIn('Context, limits and recipe', record['document_context_markdown'])
        self.assertEqual(record['source']['board_id'], 'TIP-09')
        self.assertTrue(all(i.startswith('TIP-03-') for i in self.top('expressive typography', 'style-panels')))

    def test_board_context_lessons_are_searchable(self):
        rows, _ = memory.rank(self.index, 'integer scaling', ['style-panels'])
        self.assertTrue(rows)
        self.assertTrue(all(r['id'].startswith('TIP-02-') for _, r, _ in rows[:3]))
        self.assertIn('integer', rows[0][1]['context_terms'])

    def test_document_evidence_context_is_searchable(self):
        rows, _ = memory.rank(self.index, 'mis-crops', ['pinterest'], requested_ids=['PIN-6-001'])
        self.assertTrue(rows)
        self.assertIn('mis-crops', rows[0][1]['document_context_markdown'])
        self.assertNotIn('mis-crops', rows[0][1]['content_markdown'])

    def test_no_matching_terms_returns_empty(self):
        self.assertEqual(memory.rank(self.index, 'qxzvnonexistenttoken')[0], [])

    def test_deterministic_rebuild(self):
        self.assertEqual(self.index, memory.build_index(ROOT))

    def temporary_root(self):
        context = tempfile.TemporaryDirectory()
        self.addCleanup(context.cleanup)
        root = Path(context.name)
        shutil.copytree(ROOT / 'references', root / 'references')
        index = memory.build_index(root)
        (root / memory.INDEX_REL).write_text(json.dumps(index, ensure_ascii=False), encoding='utf-8')
        return root

    def test_changed_source_fails_until_reviewed_rebuild(self):
        root = self.temporary_root()
        path = root / 'references/creative-system.md'
        path.write_text(path.read_text() + '\nReviewed addition.\n')
        with self.assertRaisesRegex(ValueError, 'stale'):
            memory.load_index(root)

    def test_missing_source_fails(self):
        root = self.temporary_root()
        (root / 'references/library/pinterest-07.md').unlink()
        with self.assertRaisesRegex(ValueError, 'missing'):
            memory.load_index(root)

    def test_new_sys_record_is_detected_and_included_on_rebuild(self):
        root = self.temporary_root()
        path = root / 'references/creative-system.md'
        path.write_text(path.read_text() + '\n## SYS-999 — Accessibility proof\n\nTags: typography, hierarchy\n\nRead essential copy at delivery scale.\n')
        with self.assertRaisesRegex(ValueError, 'stale'):
            memory.load_index(root)
        rebuilt = memory.build_index(root)
        found = [r for r in rebuilt['records'] if r['id'] == 'SYS-999']
        self.assertEqual(len(found), 1)
        self.assertIn('Read essential copy', found[0]['content_markdown'])

    def test_new_guide_file_is_not_silently_ignored(self):
        root = self.temporary_root()
        (root / 'references/new-reviewed-guide.md').write_text('# New lesson\n\nA newly reviewed lesson.\n')
        with self.assertRaisesRegex(ValueError, 'new sources'):
            memory.load_index(root)
        found = [r for r in memory.build_index(root)['records'] if r['id'] == 'GUIDE-NEW-REVIEWED-GUIDE-01']
        self.assertEqual(len(found), 1)

    def test_tampered_cached_content_fails(self):
        root = self.temporary_root()
        path = root / memory.INDEX_REL
        index = json.loads(path.read_text())
        index['records'][0]['content_markdown'] = 'Invented replacement'
        path.write_text(json.dumps(index))
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            memory.load_index(root)

    def thumbnail_fixture(self, sid='THUMB-001', pin_id='1', metric_kind='reactions', count=189):
        """Synthetic evidence exists only in a temporary test root, never installed."""
        evidence = {
            'pin_id': pin_id,
            'canonical_pin_url': 'https://www.pinterest.com/pin/' + pin_id + '/',
            'observed_at': '2026-10-14T09:00:00+05:00',
            'metrics': [{'kind': metric_kind, 'raw_label': 'React' if metric_kind == 'reactions' else metric_kind,
                         'raw_display': str(count), 'value': count, 'precision': 'exact',
                         'evidence_ref': 'fixture-only/metric.png'}],
            'visual_review': {'status': 'inspected', 'depth': 'pin-detail',
                              'evidence_ref': 'fixture-only/visual.png'},
            'dedupe': {'artwork_group_id': 'fixture-' + pin_id, 'assessment': 'distinct',
                       'duplicate_of': None, 'existing_memory_matches': []},
        }
        if metric_kind == 'reactions':
            evidence['metrics'][0]['icon'] = 'heart'
        return sid, evidence

    def thumbnail_section(self, sid, evidence):
        return ('## ' + sid + ' — Giant-key escape metaphor\n\n'
                'Tags: thumbnail, hook, typography, negative space\n\n```json\n' +
                json.dumps(evidence, ensure_ascii=False, indent=2) + '\n```\n\n'
                '**Observed hook:** A tiny figure pushes a giant key through a doorway.\n\n'
                '**Composition:** Empty upper field, diagonal motion, a clear focal object.\n\n'
                '**Typography:** One short bold line with high contrast.\n\n'
                '**Color:** An estimated blue #123456 is not a printed source label.\n\n'
                '**Original transfer:** Connect a different everyday object to a new useful outcome.\n\n'
                '**Limits:** Synthetic temporary test evidence, not a real studied Pinterest pin.\n')

    def write_thumbnails(self, root, fixtures):
        path = root / 'references/library/thumbnail-studies.md'
        path.write_text('# Thumbnail studies\n\nOnly admitted studies; 200 candidates is not 200 admissions.\n\n' +
                        '\n'.join(self.thumbnail_section(*fixture) for fixture in fixtures), encoding='utf-8')
        return path

    def test_thumbnail_exact_retrieval_preserves_evidence_and_source(self):
        root = self.temporary_root()
        fixture = self.thumbnail_fixture()
        path = self.write_thumbnails(root, [fixture])
        index = memory.build_index(root)
        rows, _ = memory.rank(index, '', ['thumbnails'], [], ['THUMB-001'])
        self.assertEqual(len(rows), 1)
        record = rows[0][1]
        self.assertEqual(record['corpus'], 'thumbnails')
        self.assertEqual(record['source_type'], 'qualified-thumbnail-study')
        self.assertIn('thumbnail', record['categories'])
        self.assertEqual(record['source']['metrics'], fixture[1]['metrics'])
        self.assertEqual(record['source']['visual_review'], fixture[1]['visual_review'])
        self.assertEqual(record['source']['qualification']['qualifying_metric_kinds'], ['reactions'])
        self.assertEqual(record['source']['qualification']['thresholds'], {'likes': 50, 'reactions': 50, 'saves': 100})
        self.assertTrue(record['source']['qualification']['heart_react_counts_as_user_likes'])
        self.assertEqual(record['printed_hex_codes'], [])
        lines = path.read_text().splitlines()
        self.assertEqual(record['content_markdown'], '\n'.join(lines[record['line_start'] - 1:record['line_end']]).strip() + '\n')
        self.assertEqual(record['section_sha256'], memory.digest(record['content_markdown']))
        self.assertEqual(index['counts_by_corpus']['pinterest'], 700)
        self.assertEqual(index['counts_by_corpus']['thumbnails'], 1)
        self.assertEqual(memory.rank(index, '', ['pinterest'], [], ['THUMB-001'])[0], [])
        self.assertEqual(memory.rank(index, 'giant key escape', ['thumbnails'])[0][0][1]['id'], 'THUMB-001')

    def test_thumbnail_threshold_boundaries_and_metric_labels(self):
        for kind in ('likes', 'saves', 'reactions'):
            threshold = 100 if kind == 'saves' else 50
            for count in (49, 50, 51, 99, 100, 101):
                with self.subTest(kind=kind, count=count):
                    sid, source = self.thumbnail_fixture(metric_kind=kind, count=count)
                    body = self.thumbnail_section(sid, source)
                    if count < threshold:
                        with self.assertRaisesRegex(ValueError, '50 likes/heart React reactions or 100 saves'):
                            memory.thumbnail_provenance(body, sid)
                    else:
                        accepted = memory.thumbnail_provenance(body, sid)
                        self.assertEqual(accepted['metrics'][0]['kind'], kind)
                        self.assertEqual(accepted['metrics'][0]['raw_label'], source['metrics'][0]['raw_label'])
        sid, source = self.thumbnail_fixture(metric_kind='saves', count=100)
        source['metrics'][0].update(raw_display='100+', precision='explicit-lower-bound')
        self.assertEqual(memory.thumbnail_provenance(self.thumbnail_section(sid, source), sid)['metrics'][0]['value'], 100)
        source['metrics'][0].update(raw_display='1,200', value=1200, precision='exact')
        self.assertEqual(memory.thumbnail_provenance(self.thumbnail_section(sid, source), sid)['metrics'][0]['value'], 1200)
        sid, source = self.thumbnail_fixture(metric_kind='reactions', count=50)
        source['metrics'][0].update(raw_display='50+', precision='explicit-lower-bound')
        self.assertEqual(memory.thumbnail_provenance(self.thumbnail_section(sid, source), sid)['metrics'][0]['value'], 50)

    def test_thumbnail_mixed_metrics_qualify_independently_without_relabeling(self):
        sid, source = self.thumbnail_fixture(metric_kind='reactions', count=50)
        _, saves = self.thumbnail_fixture(metric_kind='saves', count=99)
        source['metrics'].extend(saves['metrics'])
        accepted = memory.thumbnail_provenance(self.thumbnail_section(sid, source), sid)
        self.assertEqual(accepted['qualification']['qualifying_metric_kinds'], ['reactions'])
        self.assertEqual(accepted['metrics'], source['metrics'])
        source['metrics'][0].update(raw_display='49', value=49)
        source['metrics'][1].update(raw_display='100', value=100)
        accepted = memory.thumbnail_provenance(self.thumbnail_section(sid, source), sid)
        self.assertEqual(accepted['qualification']['qualifying_metric_kinds'], ['saves'])
        self.assertFalse(accepted['qualification']['heart_react_counts_as_user_likes'])

    def test_thumbnail_unknown_inconsistent_or_uninspected_evidence_rejected(self):
        _, original = self.thumbnail_fixture()
        mutations = [
            lambda s: s['metrics'][0].update(raw_display='1.2K', value=1200, precision='abbreviated'),
            lambda s: s['metrics'][0].update(raw_display='0.1K', value=100, precision='abbreviated'),
            lambda s: s['metrics'][0].update(raw_display='unknown', value=None),
            lambda s: s['metrics'][0].update(value=190),
            lambda s: s['metrics'][0].update(value=True, raw_display='1'),
            lambda s: s['metrics'][0].update(evidence_ref=''),
            lambda s: s['metrics'][0].update(kind='followers'),
            lambda s: s['metrics'][0].update(kind='comments'),
            lambda s: s['metrics'][0].update(kind='saves', raw_label='React'),
            lambda s: s['metrics'][0].update(raw_label='All reactions'),
            lambda s: s['metrics'][0].update(icon='unknown'),
            lambda s: s['visual_review'].update(status='uninspected'),
            lambda s: s['visual_review'].update(depth='metadata-only'),
            lambda s: s['visual_review'].update(evidence_ref=''),
            lambda s: s.update(observed_at='2026-10-14'),
            lambda s: s.update(canonical_pin_url='https://www.pinterest.com/pin/2/'),
            lambda s: s['dedupe'].update(duplicate_of='THUMB-999'),
            lambda s: s['dedupe'].update(assessment='unknown'),
        ]
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index):
                source = copy.deepcopy(original)
                mutation(source)
                with self.assertRaises(ValueError):
                    memory.thumbnail_provenance(self.thumbnail_section('THUMB-001', source), 'THUMB-001')
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            memory.thumbnail_provenance('## THUMB-001 — No evidence\n', 'THUMB-001')

    def test_thumbnail_duplicate_pin_artwork_and_record_ids_rejected(self):
        root = self.temporary_root()
        first = self.thumbnail_fixture()
        cases = [
            ([first, self.thumbnail_fixture(sid='THUMB-002')], 'Duplicate thumbnail pin_id'),
            ([first, self.thumbnail_fixture(pin_id='2')], 'Duplicate canonical record ID'),
        ]
        second = self.thumbnail_fixture(sid='THUMB-002', pin_id='2')
        second[1]['dedupe']['artwork_group_id'] = first[1]['dedupe']['artwork_group_id']
        cases.append(([first, second], 'Duplicate thumbnail artwork_group_id'))
        for fixtures, message in cases:
            with self.subTest(message=message):
                self.write_thumbnails(root, fixtures)
                with self.assertRaisesRegex(ValueError, message):
                    memory.build_index(root)

    def test_thumbnail_partial_admission_and_known_legacy_links(self):
        root = self.temporary_root()
        self.write_thumbnails(root, [])
        self.assertEqual(memory.build_index(root)['counts_by_corpus'].get('thumbnails', 0), 0)
        first = self.thumbnail_fixture()
        first[1]['dedupe']['existing_memory_matches'] = ['PIN-2-005']
        second = self.thumbnail_fixture(sid='THUMB-003', pin_id='3', metric_kind='saves', count=200)
        self.write_thumbnails(root, [first, second])
        index = memory.build_index(root)
        self.assertEqual(index['counts_by_corpus']['thumbnails'], 2)
        # Sparse stable IDs are allowed: neither 200 admissions nor contiguous IDs is invented.
        records = {r['id']: r for r in index['records']}
        self.assertEqual(records['THUMB-001']['source']['dedupe']['existing_memory_matches'], ['PIN-2-005'])
        first[1]['dedupe']['existing_memory_matches'] = ['THUMB-999']
        self.write_thumbnails(root, [first])
        with self.assertRaisesRegex(ValueError, 'existing_memory_matches'):
            memory.build_index(root)

    def test_new_thumbnail_source_requires_reviewed_rebuild(self):
        root = self.temporary_root()
        self.write_thumbnails(root, [self.thumbnail_fixture()])
        with self.assertRaisesRegex(ValueError, 'new sources'):
            memory.load_index(root)
        index = memory.build_index(root)
        (root / memory.INDEX_REL).write_text(json.dumps(index), encoding='utf-8')
        self.assertEqual(memory.load_index(root)['counts_by_corpus']['thumbnails'], 1)

    def test_thumbnail_malformed_heading_is_not_silently_ignored(self):
        root = self.temporary_root()
        path = self.write_thumbnails(root, [self.thumbnail_fixture()])
        path.write_text(path.read_text().replace('## THUMB-001 —', '### THUMB-001 —'))
        with self.assertRaisesRegex(ValueError, 'Malformed THUMB'):
            memory.build_index(root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
