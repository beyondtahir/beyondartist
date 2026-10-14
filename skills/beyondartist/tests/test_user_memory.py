"""Persistence/scope/asset regression tests. All user data is synthetic and temporary."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('user_memory', ROOT / 'scripts/user_memory.py')
memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory)


class UserMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'persistent'
        memory.init(self.root, 'alice', 'Alice', 'launch', 'Launch')
        memory.init(self.root, 'alice', project='portrait')
        memory.init(self.root, 'bob', 'Bob', 'launch', 'Bob launch')

    def record(self, rid='brand', kind='brand', text='Use indigo for the academy.', status='recorded', tags=None):
        return {'id': rid, 'title': 'Academy indigo palette', 'kind': kind,
                'text': text, 'tags': tags or ['brand-colors', 'indigo'], 'status': status,
                'provenance': {'kind': 'user-statement', 'reference': 'Synthetic test brief'}}

    def cli(self, *args, input_text=None, check=True):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/user_memory.py'), '--root', str(self.root), *args],
                                input=input_text, text=True, capture_output=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        return result

    def test_resume_from_an_independent_process(self):
        record = self.record()
        self.cli('put', '--person', 'alice', '--input', '-', input_text=json.dumps(record))
        result = self.cli('context', '--person', 'alice', '--project', 'launch', '--query', 'indigo')
        self.assertEqual(result['records'][0]['text'], record['text'])
        self.assertEqual(result['person']['name'], 'Alice')

    def test_people_never_share_profile_records(self):
        memory.put(self.root, 'alice', self.record(text='Alice indigo'))
        memory.put(self.root, 'bob', self.record(text='Bob amber'))
        self.assertEqual(memory.retrieve(self.root, 'alice')['records'][0]['text'], 'Alice indigo')
        self.assertEqual(memory.retrieve(self.root, 'bob')['records'][0]['text'], 'Bob amber')

    def test_same_user_keeps_project_scope_and_personal_context(self):
        memory.put(self.root, 'alice', self.record('brand'))
        memory.put(self.root, 'alice', self.record('cover', 'brief'), 'launch')
        memory.put(self.root, 'alice', self.record('face', 'brief'), 'portrait')
        result = memory.retrieve(self.root, 'alice', 'launch')
        self.assertEqual({r['id'] for r in result['records']}, {'brand', 'cover'})
        self.assertEqual({r['id'] for r in memory.retrieve(self.root, 'alice')['records']}, {'brand'})

    def test_same_record_id_is_independent_in_each_project(self):
        memory.put(self.root, 'alice', self.record('brief', text='Launch brief'), 'launch')
        memory.put(self.root, 'alice', self.record('brief', text='Portrait brief'), 'portrait')
        memory.put(self.root, 'alice', self.record('brief', text='Personal note'))
        launch = memory.retrieve(self.root, 'alice', 'launch', exact_ids=['brief'])['records']
        self.assertEqual({r['text'] for r in launch}, {'Launch brief', 'Personal note'})
        self.assertEqual([r['text'] for r in memory.retrieve(self.root, 'alice', 'portrait')['records']
                          if r['scope'] == 'project'], ['Portrait brief'])

    def test_tags_kind_and_unicode_copy_retrieve_actual_record(self):
        payload = self.record('urdu', 'brief', text='کلائنٹ کا آخری تغیر', tags=['urdu-rtl', 'designer-meme'])
        memory.put(self.root, 'alice', payload, 'launch')
        found = memory.retrieve(self.root, 'alice', 'launch', query='کلائنٹ', tags=['urdu-rtl'], kinds=['brief'])
        self.assertEqual(found['records'][0]['id'], 'urdu')
        self.assertEqual(memory.retrieve(self.root, 'alice', 'launch', tags=['urdu-rtl', 'absent'])['records'], [])

    def test_copy_survives_removal_of_original_and_profile_transfer(self):
        source = Path(self.temp.name) / 'user-reference.txt'
        source.write_text('Synthetic reference bytes', encoding='utf-8')
        found = memory.put(self.root, 'alice', self.record('identity', 'identity'), asset=source)
        source.unlink()
        self.assertEqual(Path(found['asset']['absolute_path']).read_text(), 'Synthetic reference bytes')
        import shutil
        moved = Path(self.temp.name) / 'transferred'
        shutil.copytree(self.root, moved)
        resumed = memory.retrieve(moved, 'alice')['records'][0]
        self.assertTrue(Path(resumed['asset']['absolute_path']).is_file())
        self.assertTrue(str(moved) in resumed['asset']['absolute_path'])

    def test_missing_and_changed_assets_are_reported(self):
        source = Path(self.temp.name) / 'reference.txt'
        source.write_text('Original synthetic bytes')
        found = memory.put(self.root, 'alice', self.record('identity', 'identity'), asset=source)
        copied = Path(found['asset']['absolute_path'])
        copied.write_text('Damaged copy')
        self.assertEqual(memory.validate(self.root, 'alice')['asset_problems'][0]['availability'], 'checksum-mismatch')
        copied.unlink()
        self.assertEqual(memory.retrieve(self.root, 'alice')['records'][0]['asset']['availability'], 'missing')

    def test_revisions_keep_old_value_and_same_asset(self):
        source = Path(self.temp.name) / 'reference.txt'
        source.write_text('Synthetic reference')
        memory.put(self.root, 'alice', self.record('identity', 'identity', 'Old description'), asset=source)
        updated = memory.put(self.root, 'alice', self.record('identity', 'identity', 'User corrected description'))
        self.assertEqual(updated['revision'], 2)
        db = memory.load(memory.profile_dir(self.root, 'alice'), 'alice')
        self.assertEqual(db['records']['personal/identity']['history'][0]['text'], 'Old description')
        self.assertTrue(Path(updated['asset']['absolute_path']).exists())

    def test_generated_artifact_is_draft_until_user_approval(self):
        payload = self.record('final', 'artifact')
        payload.pop('status')
        self.assertEqual(memory.put(self.root, 'alice', payload, 'launch')['status'], 'draft')
        payload['status'] = 'approved'
        with self.assertRaisesRegex(ValueError, 'user-approval'):
            memory.put(self.root, 'alice', payload, 'launch')
        payload['approval'] = {'kind': 'user-approval', 'reference': 'Synthetic user explicitly approved this candidate'}
        self.assertEqual(memory.put(self.root, 'alice', payload, 'launch')['status'], 'approved')

    def test_rejections_are_excluded_but_available_for_feedback(self):
        memory.put(self.root, 'alice', self.record('bad', 'artifact', status='rejected'), 'launch')
        memory.put(self.root, 'alice', self.record('old', 'decision', status='superseded'), 'launch')
        self.assertEqual(memory.retrieve(self.root, 'alice', 'launch')['records'], [])
        self.assertEqual(memory.retrieve(self.root, 'alice', 'launch', statuses=['rejected'])['records'][0]['id'], 'bad')
        self.assertEqual(memory.retrieve(self.root, 'alice', 'launch', exact_ids=['old'])['records'][0]['status'], 'superseded')

    def test_no_match_does_not_return_unrelated_identity(self):
        memory.put(self.root, 'alice', self.record())
        self.assertEqual(memory.retrieve(self.root, 'alice', query='nonexistentqxz')['records'], [])
        missing = memory.retrieve(self.root, 'alice', exact_ids=['unseen'])
        self.assertEqual(missing['missing_requested_ids'], ['unseen'])

    def test_stale_or_tampered_cache_rebuilds_without_losing_canonical_records(self):
        memory.put(self.root, 'alice', self.record())
        path = memory.profile_dir(self.root, 'alice') / 'index.json'
        cached = memory.read_json(path)
        cached['terms']['personal/brand'] = {'wrong': 1000}
        memory.atomic_json(path, cached)
        self.assertEqual(memory.retrieve(self.root, 'alice', query='indigo')['records'][0]['id'], 'brand')
        path.unlink()
        self.assertEqual(memory.retrieve(self.root, 'alice', query='indigo')['records'][0]['id'], 'brand')
        self.assertTrue(memory.validate(self.root, 'alice')['index_valid'])

    def test_invalid_canonical_memory_is_not_erased(self):
        path = memory.profile_dir(self.root, 'alice') / 'memory.json'
        path.write_text('Corrupted JSON')
        with self.assertRaises(json.JSONDecodeError):
            memory.init(self.root, 'alice')
        self.assertEqual(path.read_text(), 'Corrupted JSON')

    def test_path_escape_unknown_project_and_skill_folder_are_rejected(self):
        for person in ('../bob', '/absolute', 'CON'):
            with self.subTest(person=person), self.assertRaises(ValueError):
                memory.profile_dir(self.root, person)
        with self.assertRaisesRegex(ValueError, 'outside'):
            memory.root_path(str(ROOT / 'private'))
        with self.assertRaisesRegex(ValueError, 'Initialize'):
            memory.put(self.root, 'alice', self.record(), 'unknown')
        with self.assertRaisesRegex(ValueError, 'Unknown project'):
            memory.retrieve(self.root, 'alice', 'unknown')

    def test_separate_installers_and_default_root_override(self):
        other = Path(self.temp.name) / 'another-installers-memory'
        memory.init(other, 'alice')
        memory.put(self.root, 'alice', self.record())
        self.assertEqual(memory.retrieve(other, 'alice')['records'], [])
        with patch.dict(os.environ, {'BEYONDARTIST_MEMORY_HOME': str(other)}):
            self.assertEqual(memory.root_path(), other.resolve())

    def test_parallel_writers_preserve_both_records(self):
        processes = []
        for index in range(6):
            process = subprocess.Popen([sys.executable, str(ROOT / 'scripts/user_memory.py'), '--root', str(self.root),
                                        'put', '--person', 'alice', '--project', 'launch', '--input', '-'],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            process.stdin.write(json.dumps(self.record('item-%d' % index)))
            process.stdin.close()
            process.stdin = None
            processes.append(process)
        for process in processes:
            _, errors = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, errors)
        self.assertEqual(len(memory.retrieve(self.root, 'alice', 'launch', limit=20)['records']), 6)
        self.assertTrue(memory.validate(self.root, 'alice')['index_valid'])

    def test_offline_retrieval_uses_no_network(self):
        memory.put(self.root, 'alice', self.record())
        with patch('socket.socket', side_effect=AssertionError('No network allowed in this fixture')):
            self.assertEqual(memory.retrieve(self.root, 'alice', query='indigo')['records'][0]['id'], 'brand')

    def test_cli_invalid_input_fails_without_adding_a_record(self):
        result = self.cli('put', '--person', 'alice', '--input', '-', input_text='{}', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(memory.retrieve(self.root, 'alice')['records'], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
