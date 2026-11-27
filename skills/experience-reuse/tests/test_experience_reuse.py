"""Outcome-level CLI checks with isolated synthetic projects, no model calls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'praxis.py'


class ExperienceReuseBehavior(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='praxis-test-')
        self.base = Path(self.temp.name)
        self.project = self.base / 'project-a'
        self.other = self.base / 'project-b'
        self.project.mkdir()
        self.other.mkdir()
        self.evidence = self.project / 'observed-result.txt'
        self.evidence.write_text('Synthetic fixture: the expected entity and body were returned.', encoding='utf-8')
        self.counter = 0
        self.recipe = {
            'pattern_key': 'fixture.example.detail.read',
            'summary': 'Synthetic example detail retrieval',
            'when': {'host': 'example.test', 'tool': 'reader-a', 'version': '1'},
            'procedure': 'Synthetic fixture method A',
            'success_check': 'Verify expected entity and actual body',
            'invalidate_when': 'Recheck when reader version or page type changes',
            'evidence_refs': [str(self.evidence)],
        }

    def tearDown(self):
        self.temp.cleanup()

    @property
    def store(self):
        return self.project / '.codex/praxis-nexus/experiences.json'

    def invoke(self, command, payload=None, project=None, query='detail', context=None, extra=(), ok=True):
        args = [sys.executable, '-X', 'utf8', str(SCRIPT), command, '--project', str(project or self.project)]
        if payload is not None:
            self.counter += 1
            file = self.base / f'input-{self.counter}.json'
            file.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
            args += ['--input', str(file)]
        if command == 'find':
            args += ['--query', query]
            if context is not None:
                self.counter += 1
                file = self.base / f'context-{self.counter}.json'
                file.write_text(json.dumps(context), encoding='utf-8')
                args += ['--context-file', str(file)]
        result = subprocess.run(args + list(extra), capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0 if ok else 2, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['ok'], ok)
        return data

    def capture(self):
        return self.invoke('capture', self.recipe)['id']

    def event(self, identifier, outcome='success', key='task-1.action-1', adopted=True, checked=True):
        return {'id': identifier, 'event_key': key, 'task_id': 'task-1', 'adopted': adopted,
                'conditions_checked': checked, 'outcome': outcome,
                'evidence_refs': [str(self.evidence)], 'note': 'Synthetic fixture observation'}

    def test_read_only_empty_lookup_creates_nothing(self):
        self.assertEqual(self.invoke('find')['results'], [])
        self.assertFalse(self.invoke('status')['store_exists'])
        self.assertFalse((self.project / '.codex').exists())

    def test_capture_is_candidate_until_observed_success(self):
        identifier = self.capture()
        candidate = self.invoke('find', context=self.recipe['when'])['results'][0]
        self.assertEqual(candidate['recommendation'], 'candidate_requires_evidence_review')
        self.invoke('observe', self.event(identifier))
        result = self.invoke('find', context=self.recipe['when'])['results'][0]
        self.assertEqual(result['status'], 'validated')
        self.assertEqual(result['recommendation'], 'preferred_method_recheck_conditions')
        self.assertTrue(result['requires_source_and_condition_check'])

    def test_identical_capture_and_observation_are_idempotent(self):
        identifier = self.capture()
        before = self.store.read_bytes()
        self.assertFalse(self.invoke('capture', self.recipe)['changed'])
        self.assertEqual(self.store.read_bytes(), before)
        event = self.event(identifier)
        self.invoke('observe', event)
        before = self.store.read_bytes()
        self.assertFalse(self.invoke('observe', event)['changed'])
        self.assertEqual(self.store.read_bytes(), before)
        self.assertEqual(self.invoke('status')['observations'], 1)

    def test_event_identity_conflict_does_not_overwrite(self):
        identifier = self.capture()
        self.invoke('observe', self.event(identifier))
        before = self.store.read_bytes()
        self.invoke('observe', self.event(identifier, outcome='failure'), ok=False)
        self.assertEqual(self.store.read_bytes(), before)

    def test_context_missing_and_version_mismatch_are_distinct(self):
        self.capture()
        result = self.invoke('find', context={'host': 'example.test'})['results'][0]
        self.assertEqual(set(result['missing_context']), {'tool', 'version'})
        self.assertEqual(result['recommendation'], 'fill_context_before_use')
        result = self.invoke('find', context={**self.recipe['when'], 'version': '2'})
        self.assertEqual(result['results'], [])
        self.assertEqual(result['exclusions'][0]['reason'], 'context_mismatch')

    def test_no_cross_project_recall(self):
        self.capture()
        self.assertEqual(self.invoke('find', project=self.other, context=self.recipe['when'])['results'], [])
        self.assertFalse((self.other / '.codex').exists())

    def test_copied_store_is_rejected(self):
        self.capture()
        other_store = self.other / '.codex/praxis-nexus/experiences.json'
        other_store.parent.mkdir(parents=True)
        shutil.copyfile(self.store, other_store)
        self.assertIn('another project', self.invoke('status', project=self.other, ok=False)['error'])

    def test_failure_excludes_method_until_explicit_revalidation(self):
        identifier = self.capture()
        self.invoke('observe', self.event(identifier))
        self.invoke('observe', self.event(identifier, outcome='failure', key='task-1.action-2'))
        result = self.invoke('find', context=self.recipe['when'])
        self.assertEqual(result['results'], [])
        self.assertEqual(result['exclusions'][0]['reason'], 'stale')
        event = self.event(identifier, key='task-2.action-1')
        self.invoke('observe', event, ok=False)
        self.assertEqual(self.invoke('observe', event, extra=['--revalidate'])['status'], 'validated')

    def test_changed_method_preserves_version_and_resets_validation(self):
        identifier = self.capture()
        self.invoke('observe', self.event(identifier))
        self.recipe['procedure'] = 'Changed synthetic method'
        result = self.invoke('capture', self.recipe)
        self.assertEqual(result['id'], identifier)
        self.assertEqual(result['revision'], 2)
        entry = self.invoke('find', context=self.recipe['when'])['results'][0]
        self.assertEqual(entry['status'], 'candidate')
        self.assertNotIn('verification_refs', entry)
        store = json.loads(self.store.read_text(encoding='utf-8'))
        self.assertTrue(any(h['procedure'] == 'Synthetic fixture method A' for h in store['entries'][0]['history']))
        self.assertTrue(self.store.with_suffix('.json.bak').is_file())

    def test_existing_authority_is_referenced_not_duplicated(self):
        self.recipe.pop('procedure')
        self.recipe['authority_ref'] = str(self.evidence)
        self.capture()
        result = self.invoke('find', context=self.recipe['when'])['results'][0]
        self.assertEqual(result['authority_ref'], str(self.evidence.resolve()))
        self.assertNotIn('procedure', result)
        self.recipe['procedure'] = 'Would duplicate authority'
        self.invoke('capture', self.recipe, ok=False)

    def test_missing_evidence_is_not_reported_as_plain_no_match(self):
        self.capture()
        self.evidence.unlink()
        result = self.invoke('find', context=self.recipe['when'])
        self.assertEqual(result['results'], [])
        self.assertEqual(result['exclusions'][0]['reason'], 'evidence_unavailable')

    def test_unknown_lock_and_corrupt_data_are_preserved(self):
        self.capture()
        lock = self.store.with_suffix('.lock')
        lock.write_text('unknown owner', encoding='utf-8')
        before = self.store.read_bytes()
        self.invoke('capture', self.recipe, ok=False)
        self.assertEqual(lock.read_text(encoding='utf-8'), 'unknown owner')
        self.assertEqual(self.store.read_bytes(), before)
        lock.unlink()  # This test owns this synthetic lock.
        self.store.write_text('{broken', encoding='utf-8')
        self.invoke('capture', self.recipe, ok=False)
        self.assertEqual(self.store.read_text(encoding='utf-8'), '{broken')

    def test_protected_memory_other_agent_paths_and_credentials_are_rejected(self):
        for parts in [('.agents', 'skills'), ('.codex', 'memories_v2')]:
            path = self.base.joinpath(*parts)
            path.mkdir(parents=True)
            self.invoke('status', project=path, ok=False)
        self.recipe['procedure'] = 'Authorization: Bearer fixtureSecretToken123456789'
        self.invoke('capture', self.recipe, ok=False)
        self.assertFalse(self.store.exists())

    def test_unadopted_result_does_not_validate_method(self):
        identifier = self.capture()
        result = self.invoke('observe', self.event(identifier, adopted=False))
        self.assertEqual(result['status'], 'candidate')
        self.invoke('observe', self.event(identifier, key='task-1.action-2', checked=False), ok=False)

    def test_supersession_preserves_original_and_does_not_revive(self):
        first = self.capture()
        self.recipe['pattern_key'] = 'fixture.example.detail.replacement'
        second = self.capture()
        self.invoke('mark', {'id': first, 'status': 'superseded', 'replacement_id': second,
                            'reason': 'Synthetic replacement', 'evidence_refs': [str(self.evidence)]})
        result = self.invoke('find', context=self.recipe['when'])
        self.assertEqual([x['id'] for x in result['results']], [second])
        self.invoke('observe', self.event(first), ok=False)
        self.assertEqual(self.invoke('status')['entries'], 2)

    def test_query_limit_is_bounded_and_reports_truncation(self):
        for i in range(5):
            self.recipe['pattern_key'] = f'fixture.detail.{i}'
            self.capture()
        result = self.invoke('find', context=self.recipe['when'])
        self.assertEqual(len(result['results']), 3)
        self.assertEqual(result['matched_count'], 5)
        self.assertTrue(result['truncated'])

    def test_directory_link_cannot_redirect_store_outside_project(self):
        outside = self.base / 'outside'
        outside.mkdir()
        try:
            os.symlink(outside, self.project / '.codex', target_is_directory=True)
        except OSError as error:
            self.skipTest(f'symlink unavailable: {error}')
        self.invoke('capture', self.recipe, ok=False)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ExperienceReuseBehavior)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {'test_count': result.testsRun, 'failures': len(result.failures),
              'errors': len(result.errors), 'skipped': [reason for _, reason in result.skipped],
              'passed': result.wasSuccessful(), 'scope': 'isolated synthetic CLI behavior; not model invocation or token savings'}
    if os.environ.get('EXPERIENCE_REUSE_TEST_REPORT'):
        report_path = Path(os.environ['EXPERIENCE_REUSE_TEST_REPORT']).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sys.exit(0 if result.wasSuccessful() else 1)
