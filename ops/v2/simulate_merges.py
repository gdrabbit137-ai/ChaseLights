#!/usr/bin/env python3
"""Compute a real, fixed-SHA W5 merge tree without changing refs or deploying."""
import argparse
import json
from pathlib import Path
import re
import subprocess

OWNER_PATHS = ('specs/v2', 'data/v2', 'packages/core-v2', 'packages/models-v2', 'apps/web-v2')


def git(repo, *args, check=True):
    result = subprocess.run(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false',
                             '-C', str(repo), *args], text=True,
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


def owner_transitions(repo, base, candidate, lock):
    """Permit only separately committed, exact W4 source integration, never edits.

    Pure W5 proposals retain the original gate. Task V imports an isolated W4
    owner commit; the base must still match its declared predecessor (or the
    new source if it was independently merged in the meantime).
    """
    if 'beta_owner_integrations' in lock:
        expected_paths = {'w1': ['specs/v2'], 'w2': ['data/v2'],
                          'w4': ['apps/web-v2']}
        rows = lock['beta_owner_integrations']
        if not isinstance(rows, list) or {r.get('owner') for r in rows} != set(expected_paths):
            raise ValueError('Beta requires exactly W1, W2 and W4 owner transitions')
        transitions = []
        for row in rows:
            owner = row['owner']
            paths = expected_paths[owner]
            if row.get('paths') != paths or not row.get('source_shas'):
                raise ValueError('Invalid Beta owner path/source declaration')
            for sha in row['source_shas']:
                source = fixed_commit(repo, sha)
                if source == candidate or git(repo, 'merge-base', '--is-ancestor', source, candidate, check=False).returncode:
                    raise ValueError('Independent owner source is not integrated: ' + source)
                common = git(repo, 'merge-base', base, source).stdout.strip()
                changes = git(repo, 'diff', '--name-only', common, source).stdout.splitlines()
                if not changes or any(not any(p.startswith(prefix + '/') for prefix in paths) for p in changes):
                    raise ValueError('Owner source contains nonowner changes: ' + source)
            path = paths[0]
            accepted = lock['sources'][owner]['tree_sha']
            if (git(repo, 'rev-parse', candidate + ':' + path).stdout.strip() != accepted or
                    git(repo, 'rev-parse', base + ':' + path).stdout.strip() != row['previous_tree_sha']):
                raise ValueError('Beta owner tree differs from accepted source/base: ' + owner)
            transitions.append({'owner': owner, 'paths': paths, 'source_shas': row['source_shas'],
                                'source_tree_sha': accepted, 'previous_tree_sha': row['previous_tree_sha']})
        return transitions
    rows = lock.get('owner_integrations', [])
    if not isinstance(rows, list):
        raise ValueError('Owner integration declarations must be a list')
    transitions = []
    seen = set()
    for row in rows:
        if (not isinstance(row, dict) or row.get('owner') != 'w4' or
                row.get('paths') != ['apps/web-v2'] or row['owner'] in seen):
            raise ValueError('Only one explicitly pinned W4 transition is supported')
        seen.add(row['owner'])
        source = fixed_commit(repo, row.get('source_sha'))
        previous = fixed_commit(repo, row.get('previous_sha'))
        if source == candidate or source != lock['sources']['w4']['sha']:
            raise ValueError('W4 source must be an independent pinned owner commit')
        if git(repo, 'merge-base', '--is-ancestor', previous, source, check=False).returncode:
            raise ValueError('Previous W4 source is not an ancestor of the owner source')
        common = git(repo, 'merge-base', base, source).stdout.strip()
        owner_changes = git(repo, 'diff', '--name-only', common, source).stdout.splitlines()
        if any(not p.startswith('apps/web-v2/') for p in owner_changes):
            raise ValueError('W4 source contains nonowner changes: ' + repr(owner_changes))
        prior_tree = git(repo, 'rev-parse', previous + ':apps/web-v2').stdout.strip()
        source_tree = git(repo, 'rev-parse', source + ':apps/web-v2').stdout.strip()
        if source_tree != lock['sources']['w4']['tree_sha']:
            raise ValueError('W4 transition source tree pin mismatch')
        base_tree = git(repo, 'rev-parse', base + ':apps/web-v2').stdout.strip()
        if base_tree not in (prior_tree, source_tree):
            raise ValueError('Base W4 tree is neither the predecessor nor accepted source')
        transitions.append({**row, 'previous_tree_sha': prior_tree, 'source_tree_sha': source_tree})
    return transitions


def rehearse(repo, base, candidate):
    base, candidate = fixed_commit(repo, base), fixed_commit(repo, candidate)
    lock = json.loads(git(repo, 'show', candidate + ':ops/v2/integration-sources.json').stdout)
    transitions = owner_transitions(repo, base, candidate, lock)
    def permitted(path):
        return w5_path(path) or any(path.startswith(p + '/')
                                  for row in transitions for p in row['paths'])
    common = git(repo, 'merge-base', base, candidate).stdout.strip()
    proposed = git(repo, 'diff', '--name-only', common, candidate).stdout.splitlines()
    if not proposed or any(not permitted(p) for p in proposed):
        raise ValueError('W5 rehearsal requires a nonempty W5-only proposal: ' + repr(proposed))
    merged = git(repo, 'merge-tree', '--write-tree', base, candidate, check=False)
    if merged.returncode:
        raise ValueError('Merge conflict or missing object; no conflict is bypassed:\n' +
                         merged.stdout + merged.stderr)
    tree = merged.stdout.splitlines()[0]
    changed = git(repo, 'diff', '--name-only', base, tree).stdout.splitlines()
    if any(not permitted(p) for p in changed):
        raise ValueError('Merged tree changes non-W5 paths: ' + repr(changed))
    source_trees = {}
    for owner, paths in (('w1', OWNER_PATHS[:1]), ('w2', OWNER_PATHS[1:2]),
                         ('w3', OWNER_PATHS[2:4]), ('w4', OWNER_PATHS[4:])):
        pin = fixed_commit(repo, lock['sources'][owner]['sha'])
        if all(git(repo, 'merge-base', '--is-ancestor', pin, tip, check=False).returncode
               for tip in (base, candidate)):
            raise ValueError('Owner pin is not integrated into either parent: ' + owner)
        for path in paths:
            actual = git(repo, 'rev-parse', tree + ':' + path).stdout.strip()
            expected = lock['sources'][owner].get('tree_sha') if len(paths) == 1 else None
            expected = expected or git(repo, 'rev-parse', pin + ':' + path).stdout.strip()
            if actual != expected:
                raise ValueError('Owner subtree differs from immutable pin: ' + path)
            source_trees[path] = actual
    return {'status': 'PASS', 'base_sha': base, 'candidate_sha': candidate,
            'merge_base_sha': common, 'merged_tree_sha': tree,
            'changed_paths': changed, 'owner_trees': source_trees,
            'verified_owner_transitions': transitions,
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
