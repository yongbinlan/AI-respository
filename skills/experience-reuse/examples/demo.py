"""Reproducible synthetic experience lifecycle; no network or model calls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'praxis.py'


def main():
    with tempfile.TemporaryDirectory(prefix='experience-reuse-demo-') as temp:
        root = Path(temp)
        project = root / 'project-a'
        other = root / 'project-b'
        project.mkdir()
        other.mkdir()
        evidence = project / 'synthetic-evidence.txt'
        evidence.write_text('Synthetic fixture only: expected entity and body returned.', encoding='utf-8')
        sequence = 0

        def run(command, payload=None, context=None, selected_project=project):
            nonlocal sequence
            args = [sys.executable, '-X', 'utf8', str(SCRIPT), command, '--project', str(selected_project)]
            if payload is not None:
                sequence += 1
                file = root / f'input-{sequence}.json'
                file.write_text(json.dumps(payload), encoding='utf-8')
                args += ['--input', str(file)]
            if command == 'find':
                sequence += 1
                file = root / f'context-{sequence}.json'
                file.write_text(json.dumps(context or {}), encoding='utf-8')
                args += ['--query', 'detail reader', '--context-file', str(file)]
            completed = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
            if completed.returncode:
                raise RuntimeError(completed.stdout or completed.stderr)
            return json.loads(completed.stdout)

        context = {'host': 'example.test', 'tool': 'reader-a', 'version': '1'}
        recipe = {
            'pattern_key': 'demo.detail.reader', 'summary': 'Synthetic detail reader fixture',
            'when': context, 'procedure': 'Synthetic method A; never a live website recipe.',
            'success_check': 'Check the expected entity and body.',
            'invalidate_when': 'Reader version or access conditions change.',
            'evidence_refs': [str(evidence)],
        }
        entry = run('capture', recipe)
        first = run('find', context=context)
        assert first['results'][0]['recommendation'] == 'candidate_requires_evidence_review'
        print('1. Captured candidate: review evidence before use.')
        event = {'id': entry['id'], 'event_key': 'demo.task1.read1', 'task_id': 'demo.task1',
                 'adopted': True, 'conditions_checked': True, 'outcome': 'success',
                 'evidence_refs': [str(evidence)], 'note': 'Synthetic fixture succeeded.'}
        run('observe', event)
        success = run('find', context=context)
        assert success['results'][0]['recommendation'] == 'preferred_method_recheck_conditions'
        print('2. Recorded success: prefer this method after checking current conditions.')
        changed = run('find', context={**context, 'version': '2'})
        assert not changed['results'] and changed['exclusions'][0]['reason'] == 'context_mismatch'
        print('3. Changed version: old method excluded as context_mismatch.')
        failure = {**event, 'event_key': 'demo.task2.read1', 'task_id': 'demo.task2',
                   'outcome': 'failure', 'note': 'Synthetic later failure.'}
        run('observe', failure)
        stale = run('find', context=context)
        assert not stale['results'] and stale['exclusions'][0]['reason'] == 'stale'
        print('4. Recorded failure: method excluded as stale; history retained.')
        isolated = run('find', context=context, selected_project=other)
        assert not isolated['results'] and not (other / '.codex').exists()
        print('5. Another project: no inherited experience and no lookup-created store.')
    print('Demo passed. Synthetic temporary records were cleaned up.')


if __name__ == '__main__':
    main()
