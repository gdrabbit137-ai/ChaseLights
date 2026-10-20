#!/usr/bin/env python3
"""Fail on new unreviewed Actions writers; inventory includes indirect writes."""
import json
from pathlib import Path
import re
from publisher import WORKFLOWS


def inventory(root):
    rows = []
    expected = set(WORKFLOWS) | {'field_snapshot_capture_request.yml'}
    for path in sorted((root / '.github/workflows').glob('*.yml')):
        text = path.read_text()
        direct = bool(re.search(r'\bgit\s+push\b', text))
        routed = 'publisher.py publish --producer ' in text
        other_write = bool(re.search(r'gh\s+pr\s+(create|merge)|gh\s+api[^\n]*(?:-X|--method)\s+(?:POST|PUT|PATCH|DELETE)|create-pull-request|/git/refs|/contents/', text))
        if other_write:
            raise ValueError('Unreviewed alternate write mechanism: ' + path.name)
        if (direct or routed) and path.name not in expected:
            raise ValueError('Unreviewed workflow writer: ' + path.name)
        if path.name in WORKFLOWS:
            if direct or 'publisher.py prepare' not in text or not routed:
                raise ValueError('Incomplete migration: ' + path.name)
            producer = WORKFLOWS[path.name]
            if f'publisher.py publish --producer {producer}' not in text:
                raise ValueError('Wrong workflow scope')
            rows.append({'workflow': path.name, 'producer': producer,
                         'route': 'main-owned policy; legacy-main until reviewed cutover'})
        if path.name == 'field_snapshot_capture_request.yml':
            if '"snapshot-capture/**"' not in text or 'HEAD:${{ github.ref_name }}' not in text:
                raise ValueError('Field snapshot branch boundary drift')
            rows.append({'workflow': path.name, 'route': 'snapshot-capture/** only; not main'})
    if {x['workflow'] for x in rows} != expected:
        raise ValueError('Missing inventory writer')
    return rows


if __name__ == '__main__':
    print(json.dumps(inventory(Path('.')), indent=2))
