"""Offline, project-scoped experience index. Never executes stored procedures."""
from __future__ import annotations

import argparse
import copy
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

STORE = Path('.codex/praxis-nexus/experiences.json')
STATUSES = {'candidate', 'validated', 'stale', 'retired', 'superseded'}
SECRET = re.compile(r'(?:bearer\s+[A-Za-z0-9_.-]{12,}|(?:api[_-]?key|access[_-]?token|cookie|password)\s*[=:]\s*[^\s\"\',;]{8,}|sk-[A-Za-z0-9_-]{20,})', re.I)


def fail(message):
    raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def keypath(path):
    return os.path.normcase(str(path.resolve()))


def safe_path(path):
    path = Path(path).expanduser().resolve()
    parts = [p.casefold() for p in path.parts]
    native_memory = any(parts[i] == '.codex' and parts[i + 1].startswith('memories') for i in range(len(parts) - 1))
    if '.agents' in parts or native_memory:
        fail('protected memory/other-agent path')
    if path.name.casefold() in {'auth.json', '.env', 'credentials.json', 'cookies.json', 'storage_state.json', 'storagestate.json'}:
        fail('credential files cannot be references')
    return path


def text_field(data, name, maximum=1600):
    value = data.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        fail(f'{name}: expected non-empty string up to {maximum} characters')
    return value.strip()


def refs(data):
    value = data.get('evidence_refs')
    if not isinstance(value, list) or not 1 <= len(value) <= 12:
        fail('evidence_refs: expected 1–12 existing file references')
    result = []
    for item in value:
        if not isinstance(item, str) or not Path(item).is_absolute():
            fail('evidence references must be absolute file paths')
        path = safe_path(item)
        if not path.is_file():
            fail(f'evidence unavailable: {path}')
        if str(path) not in result:
            result.append(str(path))
    return result


def input_json(path):
    raw = Path(path).read_bytes()
    if len(raw) > 16384:
        fail('input exceeds 16 KiB; store concise metadata and evidence references')
    data = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(data, dict):
        fail('input must be a JSON object')
    if SECRET.search(json.dumps(data, ensure_ascii=False)):
        fail('possible credential content; redact before saving')
    return data


def store_path(project):
    root = safe_path(project)
    if not root.is_dir() or root == Path(root.anchor):
        fail('project must be an existing project directory, not a drive root')
    target = root / STORE
    if not target.resolve().is_relative_to(root):
        fail('index path escapes project through a directory link')
    return root, target


def load(root, target):
    if not target.exists():
        return {'schema_version': 1, 'project_root': str(root), 'entries': [], 'events': []}
    data = json.loads(target.read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        fail('unsupported or corrupt store; original left untouched')
    if keypath(Path(data.get('project_root', ''))) != keypath(root):
        fail('store belongs to another project; do not copy or inherit it silently')
    if not isinstance(data.get('entries'), list) or not isinstance(data.get('events'), list):
        fail('corrupt entries/events; original left untouched')
    ids, patterns = set(), set()
    for entry in data['entries']:
        if not isinstance(entry, dict):
            fail('corrupt experience entry')
        if entry.get('status') not in STATUSES or not isinstance(entry.get('when'), dict):
            fail('corrupt experience status/context')
        if not entry.get('id') or not entry.get('pattern_key') or entry['id'] in ids or entry['pattern_key'] in patterns:
            fail('corrupt or duplicate experience identities')
        if not isinstance(entry.get('evidence_refs'), list) or not entry['evidence_refs']:
            fail('corrupt experience evidence')
        ids.add(entry['id'])
        patterns.add(entry['pattern_key'])
    event_keys = set()
    for event in data['events']:
        if not isinstance(event, dict) or event.get('event_key') in event_keys or event.get('id') not in ids:
            fail('corrupt or duplicate observation')
        if not event.get('event_key'):
            fail('observation has no event identity')
        event_keys.add(event['event_key'])
    return data


@contextmanager
def locked(target):
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = target.with_suffix('.lock')
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        fail(f'index locked; do not remove unknown lock: {lock}')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(json.dumps({'pid': os.getpid(), 'created_at': now()}))
        yield
    finally:
        lock.unlink()


def atomic_bytes(path, raw):
    if path.is_symlink():
        fail(f'refusing to replace a linked file: {path}')
    fd, temp = tempfile.mkstemp(prefix='.praxis-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def save(target, data):
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if target.exists():
        atomic_bytes(target.with_suffix('.json.bak'), target.read_bytes())
    atomic_bytes(target, raw)


def get_entry(data, identifier):
    entry = next((e for e in data['entries'] if e['id'] == identifier), None)
    if entry is None:
        fail('unknown experience ID')
    return entry


def snapshot(entry):
    prior = {k: copy.deepcopy(v) for k, v in entry.items() if k != 'history'}
    entry.setdefault('history', []).append(prior)


def capture(data, payload):
    pattern = text_field(payload, 'pattern_key', 180)
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]*', pattern):
        fail('pattern_key must use lowercase ASCII letters, digits, dot, underscore or hyphen')
    when = payload.get('when')
    if not isinstance(when, dict) or not when or len(when) > 12:
        fail('when: expected 1–12 explicit context key/value pairs')
    if any(not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip() for k, v in when.items()):
        fail('when keys and values must be non-empty strings')
    record = {
        'pattern_key': pattern,
        'summary': text_field(payload, 'summary', 400),
        'when': when,
        'success_check': text_field(payload, 'success_check'),
        'invalidate_when': text_field(payload, 'invalidate_when'),
        'evidence_refs': refs(payload),
    }
    if payload.get('authority_ref'):
        if payload.get('procedure'):
            fail('authority_ref mode stores a pointer, not a duplicate procedure')
        path = safe_path(payload['authority_ref'])
        if not Path(payload['authority_ref']).is_absolute() or not path.is_file():
            fail('authority_ref must point to an existing absolute file')
        record['authority_ref'] = str(path)
    else:
        record['procedure'] = text_field(payload, 'procedure', 3000)
    existing = next((e for e in data['entries'] if e['pattern_key'] == pattern), None)
    if existing:
        if all(existing.get(k) == v for k, v in record.items()) and all(k in record for k in ('procedure', 'authority_ref') if k in existing):
            return {'changed': False, 'id': existing['id'], 'status': existing['status']}
        snapshot(existing)
        for k in ('procedure', 'authority_ref', 'replacement_id', 'verification_refs', 'last_verified_at'):
            existing.pop(k, None)
        existing.update(record, status='candidate', revision=existing['revision'] + 1, updated_at=now())
        result = existing
    else:
        result = dict(record, id='PN-' + hashlib.sha256(pattern.encode()).hexdigest()[:12], status='candidate', revision=1, created_at=now(), updated_at=now(), history=[])
        data['entries'].append(result)
    return {'changed': True, 'id': result['id'], 'status': result['status'], 'revision': result['revision']}


def observe(data, payload, revalidate):
    entry = get_entry(data, text_field(payload, 'id', 80))
    for name in ('adopted', 'conditions_checked'):
        if not isinstance(payload.get(name), bool):
            fail(f'{name} must be a boolean')
    outcome = payload.get('outcome')
    if outcome not in {'success', 'failure', 'inconclusive'}:
        fail('invalid observation outcome')
    record = {
        'id': entry['id'], 'event_key': text_field(payload, 'event_key', 220),
        'task_id': text_field(payload, 'task_id', 220), 'adopted': payload['adopted'],
        'conditions_checked': payload['conditions_checked'], 'outcome': outcome,
        'evidence_refs': refs(payload), 'note': text_field(payload, 'note'),
        'entry_revision': entry['revision'],
    }
    prior = next((e for e in data['events'] if e['event_key'] == record['event_key']), None)
    if prior:
        if all(prior.get(k) == v for k, v in record.items()):
            return {'changed': False, 'status': entry['status'], 'event_key': record['event_key']}
        fail('event_key conflict; existing observation was not overwritten')
    if outcome == 'success' and payload['adopted']:
        if not payload['conditions_checked']:
            fail('success cannot validate a method without conditions_checked')
        if entry['status'] in {'retired', 'superseded'}:
            fail('retired/superseded method cannot be revived by an observation')
        if entry['status'] == 'stale' and not revalidate:
            fail('stale method needs explicit --revalidate after real verification')
        snapshot(entry)
        entry['status'] = 'validated'
        entry['last_verified_at'] = now()
        entry['verification_refs'] = record['evidence_refs']
    elif outcome == 'failure' and payload['adopted'] and entry['status'] not in {'retired', 'superseded'}:
        snapshot(entry)
        entry['status'] = 'stale'
    entry['updated_at'] = now()
    data['events'].append(dict(record, observed_at=now()))
    return {'changed': True, 'status': entry['status'], 'event_key': record['event_key']}


def mark(data, payload):
    entry = get_entry(data, text_field(payload, 'id', 80))
    status = payload.get('status')
    if status not in {'stale', 'retired', 'superseded'}:
        fail('mark supports stale, retired or superseded only')
    reason = text_field(payload, 'reason')
    evidence = refs(payload)
    replacement_id = None
    if status == 'superseded':
        replacement = get_entry(data, text_field(payload, 'replacement_id', 80))
        if replacement is entry or replacement['status'] in {'retired', 'superseded'}:
            fail('replacement must be a different current entry in this project')
        replacement_id = replacement['id']
    snapshot(entry)
    entry.update(status=status, status_reason=reason, status_evidence_refs=evidence, updated_at=now())
    entry.pop('replacement_id', None)
    if replacement_id:
        entry['replacement_id'] = replacement_id
    return {'changed': True, 'id': entry['id'], 'status': status}


def tokens(text):
    return set(re.findall(r'[a-z0-9._-]+|[\u4e00-\u9fff]', text.casefold()))


def find(data, query, context, limit):
    results, exclusions = [], []
    query_tokens = tokens(query)
    for entry in data['entries']:
        searchable = ' '.join([entry['pattern_key'], entry['summary'], *entry['when'].values()])
        overlap = len(query_tokens & tokens(searchable))
        matched = [k for k, v in entry['when'].items() if context.get(k) == v]
        if not overlap and not matched:
            continue
        conflicts = [k for k, v in entry['when'].items() if k in context and context[k] != v]
        missing = [k for k in entry['when'] if k not in context]
        reason = None
        if entry['status'] in {'stale', 'retired', 'superseded'}:
            reason = entry['status']
        elif conflicts:
            reason = 'context_mismatch'
        paths = entry['evidence_refs'] + entry.get('verification_refs', [])
        if entry.get('authority_ref'):
            paths += [entry['authority_ref']]
        absent = [p for p in paths if not safe_path(p).is_file()]
        if not reason and absent:
            reason = 'evidence_unavailable'
        if reason:
            exclusions.append({'id': entry['id'], 'reason': reason, 'context_conflicts': conflicts, 'unavailable_refs': absent})
            continue
        result = {k: v for k, v in entry.items() if k not in {'history'}}
        result.update(score=overlap + 4 * len(matched), missing_context=missing, requires_source_and_condition_check=True)
        result['recommendation'] = 'fill_context_before_use' if missing else ('preferred_method_recheck_conditions' if entry['status'] == 'validated' else 'candidate_requires_evidence_review')
        results.append(result)
    results.sort(key=lambda e: (-e['score'], e['id']))
    return {'results': results[:limit], 'matched_count': len(results), 'truncated': len(results) > limit, 'exclusions': exclusions, 'scope': data['project_root'], 'semantic_verification': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('status', 'find', 'capture', 'observe', 'mark'):
        p = sub.add_parser(command)
        p.add_argument('--project', required=True)
        if command in {'capture', 'observe', 'mark'}:
            p.add_argument('--input', required=True)
        if command == 'observe':
            p.add_argument('--revalidate', action='store_true')
        if command == 'find':
            p.add_argument('--query', required=True)
            p.add_argument('--context-file')
            p.add_argument('--limit', type=int, choices=range(1, 4), default=3)
    args = parser.parse_args(argv)
    try:
        root, target = store_path(args.project)
        if args.command in {'capture', 'observe', 'mark'}:
            payload = input_json(args.input)
            with locked(target):
                data = load(root, target)
                if args.command == 'capture':
                    result = capture(data, payload)
                elif args.command == 'observe':
                    result = observe(data, payload, args.revalidate)
                else:
                    result = mark(data, payload)
                if result['changed']:
                    save(target, data)
            result['store'] = str(target)
        else:
            data = load(root, target)
            if args.command == 'status':
                result = {'store_exists': target.exists(), 'store': str(target), 'entries': len(data['entries']), 'observations': len(data['events']), 'statuses': {s: sum(e['status'] == s for e in data['entries']) for s in sorted(STATUSES)}}
            else:
                context = input_json(args.context_file) if args.context_file else {}
                if any(not isinstance(v, str) for v in context.values()):
                    fail('context values must be observed strings')
                result = find(data, args.query, context, args.limit)
        print(json.dumps(dict(ok=True, **result), ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print(json.dumps({'ok': False, 'error': str(error), 'command': args.command}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
