#!/usr/bin/env python3
"""Real GITHUB_TOKEN Git smoke, restricted to one run-owned disposable ref."""
import json
import os
from pathlib import Path
import re
import tempfile
from publisher import (MANIFEST, checkout_data, commit_push, digest, git,
                       read_snapshot, remote_url, restore_snapshot, update_snapshot,
                       write_snapshot)


def run(root, evidence):
    if (os.environ.get('GITHUB_EVENT_NAME') != 'push' or
            os.environ.get('GITHUB_REF') != 'refs/heads/codex/w5-safe-data-publication-528'):
        raise ValueError('Smoke requires the explicit Issue 528 test branch push')
    suffix = os.environ.get('GITHUB_RUN_ID', '') + os.environ.get('GITHUB_RUN_ATTEMPT', '')
    if not suffix.isdigit():
        raise ValueError('GitHub numeric run identity required')
    branch = 'data-publish-smoke/528-' + suffix
    assert re.fullmatch(r'data-publish-smoke/528-[0-9]+', branch)
    source = git(root, 'rev-parse', 'HEAD').stdout.decode().strip()
    protected_refs = ['refs/heads/main', 'refs/heads/weather-data']
    before = git(root, 'ls-remote', 'origin', *protected_refs).stdout.decode()
    evidence.mkdir(parents=True, exist_ok=True)
    result = {'version': 1, 'fixture_only': True, 'source_sha': source, 'test_ref': branch,
              'protected_refs_before': before, 'openai_calls': 0, 'weather_requests': 0,
              'deployment_performed': False}
    created = False
    try:
        with tempfile.TemporaryDirectory() as tmp:
            seed = Path(tmp)
            if checkout_data(root, remote_url(root), branch, seed, required=False):
                raise ValueError('Ref already exists; refuse overwrite')
            write_snapshot(seed, {'tw_weather.json': b'{"fixture_only": 1}'}, source, 'bootstrap')
            first = commit_push(seed, branch, 'Issue 528 fixture seed')
            created = True
            base = {'tw_weather.json': digest(b'{"fixture_only": 1}')}
            updated = update_snapshot(root, branch, base, {'tw_weather.json': b'{"fixture_only": 2}'}, source, 'weather')['data_sha']
            try:
                update_snapshot(root, branch, base, {'tw_weather.json': b'{"fixture_only": 3}'}, source, 'weather')
            except ValueError as exc:
                if 'Concurrent same-path' not in str(exc): raise
                result['same_path_conflict_rejected'] = True
            else:
                raise ValueError('Stale same-path overwrite was accepted')
            try:
                update_snapshot(root, branch, base, {'index.html': b'forbidden'}, source, 'weather')
            except ValueError:
                result['code_payload_rejected'] = True
            else:
                raise ValueError('Code payload accepted')
            restored = restore_snapshot(root, branch, first)['data_sha']
        with tempfile.TemporaryDirectory() as tmp:
            final = Path(tmp)
            checkout_data(root, remote_url(root), branch, final)
            manifest, payload = read_snapshot(final)
            if payload != {'tw_weather.json': b'{"fixture_only": 1}'}:
                raise ValueError('Rollback data mismatch')
            git(final, 'fetch', '-q', '--unshallow', 'origin', 'refs/heads/' + branch)
            git(final, 'merge-base', '--is-ancestor', updated, restored)
            git(final, 'branch', 'smoke-evidence', restored)
            git(final, 'bundle', 'create', str((evidence / 'smoke.bundle').resolve()), 'smoke-evidence')
            (evidence / MANIFEST).write_text(json.dumps(manifest, indent=2) + '\n')
        result.update(seed_sha=first, updated_sha=updated, restored_sha=restored,
                      rollback_bytes_verified=True, rollback_is_new_descendant=True)
    finally:
        if created:
            git(root, 'push', 'origin', ':refs/heads/' + branch)
            result['test_ref_deleted'] = True
        after = git(root, 'ls-remote', 'origin', *protected_refs).stdout.decode()
        result['protected_refs_after'] = after
        result['production_refs_unchanged_during_smoke'] = before == after
        (evidence / 'github-smoke.json').write_text(json.dumps(result, indent=2) + '\n')
    if before != after:
        raise ValueError('Production ref moved during smoke; inspect concurrent scheduled runs')
    return result


if __name__ == '__main__':
    print(json.dumps(run(Path('.').resolve(), Path('.ci/publication').resolve()), indent=2))
