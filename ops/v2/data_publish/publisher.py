#!/usr/bin/env python3
"""Bounded JSON publisher. No model, secret management, merge or main bypass."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import time

MANIFEST = 'publication-manifest.json'
POLICY = Path(__file__).with_name('policy.json')
PAIR = lambda stem: {f'weathergrid/{stem}_{suffix}.json' for suffix in ('browser', 'qc')}
GRID = (PAIR('gfs_tw_weather') | PAIR('icon_tw_cloud') | PAIR('cwa_wrf3_tw_weather') |
        {'weathergrid/weathergrid_coverage_browser.json'})
SCOPES = {
    'weather': {'tw_weather.json', 'jp_weather.json', 'us_weather.json', 'usa_weather.json',
                'tw_weather_details.json', 'jp_weather_details.json', 'us_weather_details.json'} |
               {f'{r}_weather_{loc}.json' for r in ('tw', 'jp', 'us', 'usa')
                for loc in ('zh-TW', 'en', 'ja')},
    'grid': GRID,
    'jma': PAIR('jma_msm_tw_cloud'),
    'himawari': PAIR('himawari9_tw_cloud'),
    'cams': PAIR('cams_global_tw_aod'),
    'viirs': PAIR('viirs_nightlights_tw'),
    'calibration': {'weathergrid/calibration/cwa_low_cloud_history.json',
                    'weathergrid/calibration/cwa_low_cloud_latest.json'},
    'v2-cwa': {'weathergrid/v2/index.json'},
    'v2-jma': {'weathergrid/v2/index.json'},
    'experiment': GRID | PAIR('jma_msm_tw_cloud'),
}
WORKFLOWS = {
    'update_weather.yml': 'weather', 'update_weathergrid.yml': 'grid',
    'update_jma_msm_weathergrid.yml': 'jma', 'update_himawari9_weathergrid.yml': 'himawari',
    'weathergrid_v2_cwa_publish.yml': 'v2-cwa', 'weathergrid_v2_jma_publish.yml': 'v2-jma',
    'b169_viirs_live_ingest.yml': 'viirs', 'b166_cams_aod_weathergrid.yml': 'cams',
    'cwa_low_cloud_calibration.yml': 'calibration', 'b117_gfs_multilayer_poc.yml': 'experiment',
}


def git(root, *args, check=True, data=None):
    p = subprocess.run(['git', '-C', str(root), *args], input=data, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    if check and p.returncode:
        raise ValueError(f'git {args[0]} failed: {p.stderr.decode(errors="replace")[-1500:]}')
    return p


def safe_path(path):
    p = PurePosixPath(path)
    return (not p.is_absolute() and p.as_posix() == path and
            all(re.fullmatch(r'[A-Za-z0-9_.-]+', part) and part not in ('.', '..')
                for part in p.parts) and path.endswith('.json'))


def allowed(path, producer=None):
    if not safe_path(path):
        return False
    producers = [producer] if producer else SCOPES
    for name in producers:
        if path in SCOPES[name]:
            return True
        if name == 'weather' and re.fullmatch(r'weather_details/(tw|jp|us)/[A-Za-z0-9_-]+\.json', path):
            return True
        provider = {'v2-cwa': 'cwa', 'v2-jma': 'jma'}.get(name)
        if provider and path.startswith(f'weathergrid/v2/{provider}/current/'):
            return True
    return False


def digest(body):
    return hashlib.sha256(body).hexdigest()


def valid_json(body):
    json.loads(body, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def files(root):
    """Only allowlisted regular JSON; no symlinked parents or executable modes."""
    out = {}
    for path in root.rglob('*.json'):
        rel = path.relative_to(root).as_posix()
        if not allowed(rel):
            continue
        if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
            raise ValueError('Symlink payload: ' + rel)
        if path.stat().st_mode & 0o111:
            raise ValueError('Executable JSON: ' + rel)
        body = path.read_bytes()
        valid_json(body)
        out[rel] = body
    return out


def read_snapshot(root):
    manifest = json.loads((root / MANIFEST).read_text())
    entries = manifest.get('files')
    if manifest.get('version') != 1 or not isinstance(entries, dict) or not entries:
        raise ValueError('Invalid/empty snapshot manifest')
    actual = {}
    for path in root.rglob('*'):
        if '.git' in path.relative_to(root).parts:
            continue
        if path.is_symlink():
            raise ValueError('Symlink snapshot path')
        if path.is_dir():
            continue
        rel = path.relative_to(root).as_posix()
        if rel == MANIFEST:
            if path.is_symlink():
                raise ValueError('Symlink manifest')
            continue
        if not allowed(rel) or path.is_symlink() or path.stat().st_mode & 0o111:
            raise ValueError('Non-data snapshot path: ' + rel)
        body = path.read_bytes()
        valid_json(body)
        actual[rel] = body
    if {p: digest(b) for p, b in actual.items()} != entries:
        raise ValueError('Snapshot hash/file inventory mismatch')
    if not re.fullmatch('[0-9a-f]{40}', manifest.get('source_main_sha', '')):
        raise ValueError('Missing source main provenance')
    return manifest, actual


def overlay(root, payload):
    # A complete inventory represents deletions too. Remove only managed data,
    # never code, registries, W2 canonical data or unrelated public resources.
    for path in files(root):
        if path not in payload:
            (root / path).unlink()
    for path, body in payload.items():
        if not allowed(path):
            raise ValueError('Disallowed overlay path: ' + path)
        target = root / path
        if any(p.is_symlink() for p in [target, *target.parents]):
            raise ValueError('Symlink destination')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)


def write_snapshot(root, payload, source, producer, previous=None, run_id=None, rollback=None, provenance=None):
    if not payload:
        raise ValueError("Refuse empty data snapshot")
    # Called only on a fresh data-only checkout, never the source checkout.
    for p in files(root):
        if p not in payload:
            (root / p).unlink()
    for p, body in payload.items():
        if not allowed(p):
            raise ValueError('Non-data write')
        valid_json(body)
        target = root / p
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    records = dict(provenance or {})
    records[producer] = {'source_main_sha': source, 'run_id': run_id}
    manifest = {'version': 1, 'source_main_sha': source, 'producer': producer,
                'producer_receipts': records,
                'run_id': run_id, 'previous_data_sha': previous,
                'rollback_of_data_sha': rollback,
                'published_at_utc': datetime.now(timezone.utc).isoformat(),
                'files': {p: digest(b) for p, b in sorted(payload.items())}}
    (root / MANIFEST).write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def policy():
    p = json.loads(POLICY.read_text())
    if (p.get('version') != 1 or p.get('mode') not in ('legacy-main', 'data-branch') or
            p.get('data_branch') != 'weather-data' or type(p.get('pages_enabled')) is not bool):
        raise ValueError('Unknown publication policy; no fallback')
    if p['mode'] == 'data-branch' and p['pages_enabled'] is not True:
        raise ValueError('Data mode requires coordinated Pages activation')
    return p


def require_main(producer=None):
    if (os.environ.get('GITHUB_REF') != 'refs/heads/main' or
            os.environ.get('GITHUB_EVENT_NAME') not in ('schedule', 'push', 'workflow_dispatch', 'workflow_run')):
        raise ValueError('Publisher requires a trusted main event')
    if producer:
        workflow = os.environ.get('GITHUB_WORKFLOW_REF', '')
        expected = f'/.github/workflows/{next(k for k,v in WORKFLOWS.items() if v == producer)}@refs/heads/main'
        if not workflow.endswith(expected):
            raise ValueError('Producer/workflow identity mismatch')


def baseline_path(root):
    return Path(git(root, 'rev-parse', '--absolute-git-dir').stdout.decode().strip()) / 'data-publication-baseline.json'


def checkout_data(root, remote, branch, destination, required=True):
    # Validate destination at the mutation boundary, not only at CLI parsing.
    if branch != 'weather-data' and not re.fullmatch(r'data-publish-smoke/528-[0-9]+', branch):
        raise ValueError('Ref outside dedicated data namespace')
    git(destination, 'init', '-q')
    git(destination, 'remote', 'add', 'origin', remote)
    # Reuse checkout's ephemeral GITHUB_TOKEN extraheader, without printing it.
    header = git(root, 'config', '--get', 'http.https://github.com/.extraheader', check=False).stdout
    if header:
        git(destination, 'config', 'http.https://github.com/.extraheader', header.decode().strip())
    exists = git(destination, 'ls-remote', '--exit-code', 'origin', 'refs/heads/' + branch, check=False)
    if exists.returncode == 2 and not required:
        git(destination, 'checkout', '--orphan', 'snapshot')
        return None
    if exists.returncode:
        raise ValueError('Cannot resolve data ref (never fall back to main)')
    git(destination, 'fetch', '-q', '--depth=1', 'origin', 'refs/heads/' + branch)
    git(destination, 'checkout', '-q', '--detach', 'FETCH_HEAD')
    return git(destination, 'rev-parse', 'HEAD').stdout.decode().strip()


def remote_url(root):
    return git(root, 'remote', 'get-url', 'origin').stdout.decode().strip()


def prepare(root):
    p = policy()
    if p['mode'] == 'legacy-main':
        return {'mode': p['mode'], 'changed': False}
    require_main()
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        sha = checkout_data(root, remote_url(root), p['data_branch'], dest)
        manifest, payload = read_snapshot(dest)
        overlay(root, payload)
        baseline_path(root).write_text(json.dumps({'sha': sha, 'manifest': manifest}))
    return {'mode': p['mode'], 'data_sha': sha}


def apply_delta(latest, baseline, delta):
    for path, body in delta.items():
        if (digest(latest[path]) if path in latest else None) != baseline.get(path):
            raise ValueError('Concurrent same-path update; rerun producer: ' + path)
        if body is None:
            latest.pop(path, None)
        else:
            latest[path] = body
    return latest


def commit_push(dest, branch, message):
    if branch != 'weather-data' and not re.fullmatch(r'data-publish-smoke/528-[0-9]+', branch):
        raise ValueError('Forbidden data ref')
    git(dest, 'config', 'user.name', 'github-actions[bot]')
    git(dest, 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    git(dest, 'add', '-A')
    git(dest, 'commit', '-qm', message)
    # Normal fast-forward push provides server-side compare-and-swap. NO force.
    git(dest, 'push', 'origin', 'HEAD:refs/heads/' + branch)
    return git(dest, 'rev-parse', 'HEAD').stdout.decode().strip()


def publish(root, producer):
    p = policy()
    require_main(producer)
    source = git(root, 'rev-parse', 'HEAD').stdout.decode().strip()
    if p['mode'] == 'legacy-main':
        staged = git(root, 'diff', '--cached', '--name-only', '-z').stdout.decode().split('\0')
        paths = [x for x in staged if x]
        if any(not allowed(x, producer) for x in paths):
            raise ValueError('Staged file outside producer scope')
        for row in git(root, 'ls-files', '--stage', '-z').stdout.decode().split('\0'):
            if row and row.split('\t')[-1] in paths and not row.startswith('100644 '):
                raise ValueError('Invalid staged data mode')
        for path in paths:
            blob = git(root, 'show', ':' + path, check=False)
            if blob.returncode == 0:
                valid_json(blob.stdout)
        if not paths:
            return {'mode': p['mode'], 'changed': False}
        git(root, 'config', 'user.name', 'github-actions[bot]')
        git(root, 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com')
        messages = {'weather': 'Auto-update ChaseLights weather data [skip ci]',
                    'grid': 'Auto-update live WeatherGrid preview [skip ci]',
                    'jma': 'Auto-update JMA MSM WeatherGrid',
                    'himawari': 'Auto-update Himawari-9 WeatherGrid',
                    'cams': 'Auto-update CAMS AOD WeatherGrid [skip ci]',
                    'viirs': 'Auto-update VIIRS nighttime-light snapshot [skip ci]',
                    'v2-cwa': 'Auto-update WeatherGrid V2 CWA derived tiles',
                    'v2-jma': 'Auto-update WeatherGrid V2 JMA native tiles',
                    'calibration': 'Auto-update CWA low-cloud calibration history',
                    'experiment': 'Update WeatherGrid preview snapshot [skip ci]'}
        git(root, 'commit', '-qm', messages[producer])
        # Retain existing main refreshes during review. Protection failures stop;
        # this path never uses an App, bypass credential, admin flag or force.
        for attempt in range(5):
            pull = git(root, 'pull', '--rebase', 'origin', 'main', check=False)
            if pull.returncode:
                raise ValueError('Main rebase conflict; no data published')
            if git(root, 'push', 'origin', 'HEAD:refs/heads/main', check=False).returncode == 0:
                return {'mode': p['mode'], 'changed': True}
            if attempt < 4:
                time.sleep(5)
        raise ValueError('Main publication rejected after five bounded attempts')
    saved = json.loads(baseline_path(root).read_text())
    basefiles = saved['manifest']['files']
    current = files(root)
    names = {x for x in basefiles if allowed(x, producer)} | {x for x in current if allowed(x, producer)}
    delta = {x: current.get(x) for x in names
             if (digest(current[x]) if x in current else None) != basefiles.get(x)}
    if not delta:
        return {'mode': p['mode'], 'changed': False}
    return update_snapshot(root, p['data_branch'], basefiles, delta, source, producer)


def update_snapshot(root, branch, basefiles, delta, source, producer):
    if any(not allowed(path, producer) for path in delta):
        raise ValueError('Delta outside producer scope')
    # Each attempt re-reads latest: unrelated producers are preserved. A changed
    # same path fails closed rather than silently overwriting a newer snapshot.
    for attempt in range(5):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            previous = checkout_data(root, remote_url(root), branch, dest)
            old_manifest, latest = read_snapshot(dest)
            payload = apply_delta(latest, basefiles, delta)
            write_snapshot(dest, payload, source, producer, previous, os.environ.get('GITHUB_RUN_ID'),
                           provenance=old_manifest.get('producer_receipts'))
            try:
                sha = commit_push(dest, branch, 'Refresh ' + producer + ' data')
            except ValueError as exc:
                if 'git push failed' not in str(exc) or attempt == 4:
                    raise
                continue
            return {'mode': 'data-branch', 'changed': True, 'data_sha': sha}


def bootstrap(root):
    require_main()
    p = policy()
    if p['mode'] != 'legacy-main':
        raise ValueError('Bootstrap is permitted before cutover only')
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        if checkout_data(root, remote_url(root), p['data_branch'], dest, required=False):
            raise ValueError('Bootstrap refuses to overwrite existing data history')
        source = git(root, 'rev-parse', 'HEAD').stdout.decode().strip()
        write_snapshot(dest, files(root), source, 'bootstrap', run_id=os.environ.get('GITHUB_RUN_ID'))
        return {'data_sha': commit_push(dest, p['data_branch'], 'Bootstrap generated data only')}


def synchronize(root):
    require_main()
    p = policy()
    if p['mode'] != 'legacy-main':
        raise ValueError('Final seed synchronization requires legacy mode and drained writers')
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        previous = checkout_data(root, remote_url(root), p['data_branch'], dest)
        read_snapshot(dest)
        source = git(root, 'rev-parse', 'HEAD').stdout.decode().strip()
        write_snapshot(dest, files(root), source, 'final-legacy-seed', previous,
                       os.environ.get('GITHUB_RUN_ID'))
        return {'data_sha': commit_push(dest, p['data_branch'], 'Synchronize final legacy main data')}


def rollback(root, snapshot):
    require_main()
    p = policy()
    if p['mode'] != 'data-branch' or not re.fullmatch('[0-9a-f]{40}', snapshot):
        raise ValueError('Rollback requires activated data mode and immutable SHA')
    return restore_snapshot(root, p['data_branch'], snapshot)


def restore_snapshot(root, branch, snapshot):
    if not re.fullmatch('[0-9a-f]{40}', snapshot):
        raise ValueError('Immutable snapshot SHA required')
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        previous = checkout_data(root, remote_url(root), branch, dest)
        git(dest, 'fetch', '-q', '--unshallow', 'origin', 'refs/heads/' + branch)
        git(dest, 'merge-base', '--is-ancestor', snapshot, previous)
        archive = dest / '.git' / 'restore'
        archive.mkdir()
        # Materialize only validated Git blobs; never extract arbitrary archives.
        for line in git(dest, 'ls-tree', '-rz', snapshot).stdout.decode().split('\0'):
            if not line:
                continue
            mode_type_sha, path = line.split('\t')
            mode, kind, sha = mode_type_sha.split()
            if mode != '100644' or kind != 'blob' or (path != MANIFEST and not allowed(path)):
                raise ValueError('Unsafe rollback tree')
            target = archive / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(dest, 'cat-file', 'blob', sha).stdout)
        manifest, payload = read_snapshot(archive)
        write_snapshot(dest, payload, manifest['source_main_sha'], 'rollback', previous,
                       os.environ.get('GITHUB_RUN_ID'), snapshot,
                       provenance=manifest.get('producer_receipts'))
        return {'data_sha': commit_push(dest, branch, 'Restore data snapshot ' + snapshot)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'publish', 'bootstrap', 'synchronize', 'rollback', 'verify'])
    parser.add_argument('--producer', choices=SCOPES)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--snapshot')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == 'prepare': result = prepare(root)
        elif args.command == 'publish':
            if not args.producer: raise ValueError('Producer required')
            result = publish(root, args.producer)
        elif args.command == 'bootstrap': result = bootstrap(root)
        elif args.command == 'synchronize': result = synchronize(root)
        elif args.command == 'rollback': result = rollback(root, args.snapshot or '')
        else:
            manifest, payload = read_snapshot(root)
            result = {'files': len(payload), 'source_main_sha': manifest['source_main_sha']}
        print(json.dumps({'status': 'PASS', **result}))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
