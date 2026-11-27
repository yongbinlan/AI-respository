"""Read a SKILL.md through an explicit task-provided catalog, without guessing."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import sys


def resolve_catalog(roots, reference):
    catalog = {}
    for value in roots:
        alias, separator, location = value.partition('=')
        if not separator or not alias or '/' in alias or '\\' in alias or alias in catalog:
            raise ValueError('each --root needs one unique alias=absolute-path mapping')
        path = Path(location).expanduser()
        if not path.is_absolute():
            raise ValueError('catalog roots must be absolute; no guessed cwd expansion')
        path = path.resolve()
        if '.agents' in [x.casefold() for x in path.parts]:
            raise ValueError('other-agent skill roots are not allowed')
        catalog[alias] = path
    parts = PurePosixPath(reference.replace('\\', '/')).parts
    if len(parts) < 3 or parts[0] not in catalog:
        raise ValueError('unknown alias or incomplete catalog reference; no fallback attempted')
    if '..' in parts or any(':' in p for p in parts) or parts[-1] != 'SKILL.md':
        raise ValueError('reference must remain within its root and end with SKILL.md')
    root = catalog[parts[0]]
    target = root.joinpath(*parts[1:]).resolve()
    if not target.is_relative_to(root) or '.agents' in [x.casefold() for x in target.parts]:
        raise ValueError('reference escapes the catalog root')
    if not target.is_file():
        raise FileNotFoundError('catalog target does not exist; no fallback attempted: ' + str(target))
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', action='append', required=True)
    parser.add_argument('--reference', required=True)
    args = parser.parse_args(argv)
    try:
        target = resolve_catalog(args.root, args.reference)
        content = target.read_text(encoding='utf-8-sig')
        print(json.dumps({'ok': True, 'activation': 'experience-reuse.catalog-first',
                          'reference': args.reference, 'resolved_path': str(target),
                          'fallback_attempted': False, 'content': content}, ensure_ascii=False))
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps({'ok': False, 'activation': 'experience-reuse.catalog-first',
                          'error': str(error), 'fallback_attempted': False}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
