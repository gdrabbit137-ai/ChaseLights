#!/usr/bin/env python3
"""Compute a real, fixed-SHA W5 merge tree without changing refs or deploying."""
import argparse
import json
from pathlib import Path
import re
import subprocess

OWNER_PATHS = ('specs/v2', 'data/v2', 'packages/core-v2', 'packages/models-v2', 'apps/web-v2')


def git(repo, *args, check=True):
    result = subprocess.run(['git', '-C', str(repo), *args], text=True,
                            capture_output=True, check=False)
    if check and result.returncode:
        raise ValueError('git ' + ' '.join(args) + ': ' + result.stderr.strip())
    return result


def fixed_commit(repo, sha):
    if not isinstance(sha, str) or not re.fullmatch('[0-9a-f]{40}', sha):
        raise ValueError('Full immutable commit SHA required; branches are not accepted')
    if git(repo, 'rev-parse', sha + '^{commit}').stdout.strip() != sha:
        raise ValueError('Commit object unavailable: ' + sha)
    return sha


def w5_path(path):
    return path.startswith(('ops/v2/', '.github/workflows/'))


def rehearse(repo, base, candidate):
    base, candidate = fixed_commit(repo, base), fixed_commit(repo, candidate)
    common = git(repo, 'merge-base', base, candidate).stdout.strip()
    proposed = git(repo, 'diff', '--name-only', common, candidate).stdout.splitlines()
    if not proposed or any(not w5_path(p) for p in proposed):
        raise ValueError('W5 rehearsal requires a nonempty W5-only proposal: ' + repr(proposed))
    merged = git(repo, 'merge-tree', '--write-tree', base, candidate, check=False)
    if merged.returncode:
        raise ValueError('Merge conflict or missing object; no conflict is bypassed:\n' +
                         merged.stdout + merged.stderr)
    tree = merged.stdout.splitlines()[0]
    changed = git(repo, 'diff', '--name-only', base, tree).stdout.splitlines()
    if any(not w5_path(p) for p in changed):
        raise ValueError('Merged tree changes non-W5 paths: ' + repr(changed))
    lock = json.loads(git(repo, 'show', candidate + ':ops/v2/integration-sources.json').stdout)
    source_trees = {}
    for owner, paths in (('w1', OWNER_PATHS[:1]), ('w2', OWNER_PATHS[1:2]),
                         ('w3', OWNER_PATHS[2:4]), ('w4', OWNER_PATHS[4:])):
        pin = fixed_commit(repo, lock['sources'][owner]['sha'])
        if all(git(repo, 'merge-base', '--is-ancestor', pin, tip, check=False).returncode
               for tip in (base, candidate)):
            raise ValueError('Owner pin is not integrated into either parent: ' + owner)
        for path in paths:
            actual = git(repo, 'rev-parse', tree + ':' + path).stdout.strip()
            expected = git(repo, 'rev-parse', pin + ':' + path).stdout.strip()
            if actual != expected:
                raise ValueError('Owner subtree differs from immutable pin: ' + path)
            source_trees[path] = actual
    return {'status': 'PASS', 'base_sha': base, 'candidate_sha': candidate,
            'merge_base_sha': common, 'merged_tree_sha': tree,
            'changed_paths': changed, 'owner_trees': source_trees,
            'already_integrated_owner_pins': True, 'refs_changed': False,
            'deployment_allowed': False, 'approval': 'NOT_GRANTED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--base-sha', required=True)
    parser.add_argument('--candidate-sha', required=True)
    parser.add_argument('--log-dir', type=Path, required=True)
    args = parser.parse_args()
    args.log_dir.mkdir(parents=True, exist_ok=True)
    try:
        report = rehearse(args.repo, args.base_sha, args.candidate_sha)
    except Exception as exc:
        report = {'status': 'FAIL', 'base_sha': args.base_sha,
                  'candidate_sha': args.candidate_sha, 'error': str(exc),
                  'refs_changed': False, 'deployment_allowed': False}
    (args.log_dir / 'merge-simulation.json').write_text(json.dumps(report, indent=2) + '\n')
    (args.log_dir / 'merge-simulation.log').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return int(report['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
