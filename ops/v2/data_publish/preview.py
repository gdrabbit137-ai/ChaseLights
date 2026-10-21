#!/usr/bin/env python3
"""Offline full-size site composition from committed generated JSON."""
import json
from pathlib import Path
import tempfile
from compose import compose
from publisher import files, git, write_snapshot

root = Path('.').resolve()
work = Path('/tmp/chaselights-528-preview')
if work.exists():
    raise ValueError('Refuse to replace existing preview')
work.mkdir()
data = work / 'data'; data.mkdir()
source = git(root, 'rev-parse', 'HEAD').stdout.decode().strip()
payload = files(root)
write_snapshot(data, payload, source, 'offline-preview')
git(data, 'init', '-q')
git(data, 'config', 'user.name', 'Offline preview')
git(data, 'config', 'user.email', 'preview@example.invalid')
git(data, 'add', '.')
git(data, 'commit', '-qm', 'Local-only source-data snapshot')
receipt = compose(root, data, root / '.ci/publication-site-source')
out = root / '.ci/publication'; out.mkdir(parents=True, exist_ok=True)
(out / 'full-size-assembly.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'files': len(payload), 'bytes': sum(map(len, payload.values())), 'source_sha': source}))
