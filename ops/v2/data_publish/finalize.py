#!/usr/bin/env python3
"""Verify a Jekyll artifact and retain the existing custom-domain marker."""
import argparse
import hashlib
import json
from pathlib import Path


def finalize(source, output, receipt):
    cname = (source / 'CNAME').read_bytes()
    if cname.strip() != b'chaselights.app' or not output.is_dir():
        raise ValueError('Invalid custom domain or missing Jekyll output')
    # Official Jekyll Pages action excludes CNAME; retain it explicitly, without
    # changing repository/domain settings or adding a deployment here.
    (output / 'CNAME').write_bytes(cname)
    for path in ('index.html', 'weather-map.html', 'apps/web-v2/index.html', 'CNAME'):
        if not (output / path).is_file():
            raise ValueError('Missing built public route: ' + path)
    files = receipt['data_manifest']['files']
    for path, expected in files.items():
        if hashlib.sha256((output / path).read_bytes()).hexdigest() != expected:
            raise ValueError('Built JSON differs from verified source: ' + path)
    # Also reject stale extra generated JSON that could otherwise survive build.
    from publisher import files as generated
    if set(generated(output)) != set(files):
        raise ValueError('Built JSON inventory differs from snapshot')
    return {'status': 'PASS', 'json_files': len(files), 'routes': 4,
            'deployment_performed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('source', 'output', 'receipt'):
        parser.add_argument('--' + arg, type=Path, required=True)
    a = parser.parse_args()
    print(json.dumps(finalize(a.source, a.output, json.loads(a.receipt.read_text()))))
