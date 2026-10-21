#!/usr/bin/env python3
"""Compose committed site code + verified complete data snapshot for Jekyll."""
import argparse
import io
import json
from pathlib import Path
import tarfile
from publisher import git, overlay, read_snapshot


def compose(code, snapshot, output):
    code, snapshot, output = code.resolve(), snapshot.resolve(), output.resolve()
    if (output == code or code.is_relative_to(output) or
            (output.is_relative_to(code) and not output.is_relative_to(code / '.ci'))):
        raise ValueError('Site output must be outside source checkout')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Site output must be empty')
    manifest, payload = read_snapshot(snapshot)
    source = git(code, 'rev-parse', 'HEAD').stdout.decode().strip()
    archive = git(code, 'archive', '--format=tar', source).stdout
    output.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            target = (output / member.name).resolve()
            if (not target.is_relative_to(output) or
                    not (member.isfile() or member.isdir())):
                raise ValueError('Unsafe source archive member')
        tar.extractall(output, filter='data')
    anchors = ['index.html', 'weather-map.html', 'apps/web-v2/index.html', 'CNAME']
    previous = {p: (output / p).read_bytes() for p in anchors}
    overlay(output, payload)
    if any((output / p).read_bytes() != b for p, b in previous.items()):
        raise ValueError('Non-data site anchor changed')
    if previous['CNAME'].strip() != b'chaselights.app':
        raise ValueError('Hosting domain drift')
    receipt = {'version': 1, 'code_sha': source,
               'data_sha': git(snapshot, 'rev-parse', 'HEAD').stdout.decode().strip(),
               'data_manifest': manifest, 'deployment_performed': False}
    (output / 'data-publication-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code-root', type=Path, required=True)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    print(json.dumps(compose(a.code_root, a.snapshot, a.output)))
