#!/usr/bin/env python3
"""Build only the committed V2 Research Preview; never package Legacy or deploy."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from integration_gate import check_v2_assets
from postmerge_verify import verify_main

RUNTIME_FILES = ('index.html', 'styles.css', 'app.mjs', 'model.mjs',
                 'catalog-loader.mjs', 'v21-adapter.mjs', 'catalog.v2.json')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE)


def validate_refs(files):
    errors = check_v2_assets(files['index.html'].decode(),
                             lambda ref: ref.removeprefix('./') in files)
    for name, body in files.items():
        if not name.endswith('.mjs'):
            continue
        text = body.decode()
        refs = re.findall(r'''(?m)^\s*import\b[^\n;]*?['"]([^'"]+)['"]''', text)
        refs += re.findall(r'''\b(?:fetch|import)\s*\(\s*['"]([^'"]+)['"]''', text)
        for ref in refs:
            if not ref.startswith('./') or ref[2:] not in files:
                errors.append('Unpackaged or nonisolated dependency: ' + name + ' -> ' + ref)
    if errors:
        raise ValueError('; '.join(errors))


def build(root, output):
    root, output = root.resolve(), output.resolve()
    if (output == root or root.is_relative_to(output) or
            (output.is_relative_to(root) and not any(output.is_relative_to(root / p)
                                                   for p in ('work', '.ci')))):
        raise ValueError('Build output must not overwrite repository/application source')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Build output must be empty; never delete a previous release')
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    lock = json.loads((root / 'ops/v2/integration-sources.json').read_text())
    provenance = verify_main(root, lock)
    files = {}
    for name in RUNTIME_FILES:
        path = 'apps/web-v2/' + name
        content = git(root, 'show', head + ':' + path)
        source = root / path
        if source.is_symlink() or source.read_bytes() != content:
            raise ValueError('Dirty/symlink runtime source: ' + path)
        files[name] = content
    validate_refs(files)
    catalog = json.loads(files['catalog.v2.json'])
    if (catalog.get('research_only') is not True or catalog.get('forecast_available') is not False
            or catalog.get('selected_date_recommendation_eligible') is not False
            or catalog.get('evaluations') != []):
        raise ValueError('Only the verified Research-only catalog may be packaged')
    public = output / 'public/apps/web-v2'
    public.mkdir(parents=True)
    for name, content in files.items():
        (public / name).write_bytes(content)
    report = {'status': 'PASS', 'source_commit_sha': head, 'mode': 'RESEARCH_ONLY',
              'base_path': '/apps/web-v2/', 'public_directory': 'public',
              'deployment_allowed': False, 'live_forecast_eligible': False,
              'owner_trees': provenance['owner_trees'],
              'files': {f'apps/web-v2/{n}': hashlib.sha256(b).hexdigest()
                        for n, b in files.items()}}
    (output / 'build-manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.root, args.output)))
        return 0
    except Exception as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc), 'deployment_allowed': False}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
