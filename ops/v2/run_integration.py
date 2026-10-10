"""Assemble pinned owner code in scratch space; never alter W1-W4 or Legacy."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

TASK = Path(__file__).resolve().parents[2]
EXTENSIONS = (
    'specs/v2/schema/evaluation-result-v0.1.schema.json',
    'specs/v2/tests/test_evaluation_result_security.py',
    'specs/v2/tests/fixtures/evaluation/valid_evaluation_unknown.json',
    'specs/v2/tests/fixtures/evaluation/invalid_evaluation_unknown_as_favorable.json',
    'specs/v2/tests/fixtures/evaluation/invalid_evaluation_forged_favorable_no_provider.json',
)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args]).decode().strip()


def blob(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def verified_copy(source, destination, path):
    """Copy only checked-in bytes; missing/modified inputs are blockers."""
    expected = git(source, 'rev-parse', 'HEAD:' + path)
    original = source / path
    if original.is_symlink() or not original.is_file():
        raise ValueError('Missing/non-regular source: ' + str(original))
    data = original.read_bytes()
    if blob(data) != expected:
        raise ValueError('Modified source: ' + str(original))
    target = destination / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return expected


def copy_directory(source, destination, prefix):
    paths = git(source, 'ls-tree', '-r', '--name-only', 'HEAD', '--', prefix).splitlines()
    if not paths:
        raise ValueError('No source files under ' + prefix)
    for path in paths:
        if '/tests/logs/' not in path:
            verified_copy(source, destination, path)


def parse_node(output):
    counts = {}
    for key, label in [('tests', 'tests'), ('pass', 'pass'), ('fail', 'fail'), ('skip', 'skipped')]:
        matches = re.findall(r'^# ' + label + r' (\d+)\s*$', output, re.M)
        if len(matches) != 1:
            raise ValueError('Missing/ambiguous Node test count: ' + label)
        counts[key] = int(matches[0])
    return counts


def run_group(name, command, root, logs, env, expected=None, python=False, node=False):
    result_path = logs / (name + '.json')
    if python:
        command = [sys.executable, str(TASK / 'ops/v2/run_unittest.py'),
                   *command, str(result_path)]
    print('RUN', name, flush=True)
    log_path = logs / (name + '.log')
    timed_out = False
    with log_path.open('w') as handle:
        handle.write('$ ' + ' '.join(command) + '\n')
        handle.flush()
        try:
            proc = subprocess.run(command, cwd=root, env=env, stdout=handle,
                                  stderr=subprocess.STDOUT, timeout=180)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            handle.write('\nENVIRONMENT ERROR: required suite timed out after 180 seconds\n')
            exit_code = 124
            timed_out = True
    output = log_path.read_text()
    counts = {}
    error = None
    try:
        if python:
            counts = json.loads(result_path.read_text())
        elif node:
            counts = parse_node(output)
            result_path.write_text(json.dumps(counts, indent=2) + '\n')
        if expected is not None and counts.get('tests') != expected:
            raise ValueError(f'Expected {expected} tests; got {counts.get("tests")}')
        if counts.get('skip', 0) or counts.get('expected_failure', 0):
            raise ValueError('SKIP/expected failure cannot satisfy integration')
        if (python or node) and (not counts.get('tests') or counts.get('fail', 0) or
                                counts.get('error', 0) or counts.get('unexpected_success', 0) or
                                counts.get('pass') != counts.get('tests')):
            raise ValueError('Zero tests or unsuccessful test cases')
    except (ValueError, OSError) as exc:
        error = str(exc)
    outcome = {'name': name, 'exit_code': exit_code, 'counts': counts,
               'status': 'PASS' if exit_code == 0 and error is None else 'FAIL',
               'timed_out': timed_out,
               'gate_error': error, 'log': name + '.log'}
    print(json.dumps(outcome), flush=True)
    return outcome


def check_real_sources(root):
    """Cross-owner provenance must agree with independently checked-out W2."""
    web = root / 'apps/web-v2/tests/fixtures/worker2'
    manifest = json.loads((web / 'manifest.json').read_text())
    for item in manifest['files']:
        source = root / item['source_path']
        fixture = web / item['fixture']
        if source.read_bytes() != fixture.read_bytes():
            raise ValueError('W4 fixture differs from actual W2: ' + item['fixture'])
        if blob(source.read_bytes()) != item['blob_sha']:
            raise ValueError('W2 blob mismatch: ' + item['source_path'])
    source = root / 'data/v2/opportunities/tw-026-P01.json'
    if source.read_bytes() != (root / 'packages/core-v2/tests/fixtures/tw-026-P01.w2-fe52720.json').read_bytes():
        raise ValueError('W3 regression fixture differs from actual W2')
    preview = json.loads((root / 'data/v2/previews/tw-026-P01.research-only.v21.json').read_text())
    if preview.get('forecast_available') is not False or preview.get('evaluations'):
        raise ValueError('W2 research-only preview carries live evaluations')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources-root', type=Path, required=True)
    parser.add_argument('--work-root', type=Path, required=True)
    parser.add_argument('--logs-dir', type=Path, required=True)
    args = parser.parse_args()
    root, logs = args.work_root.resolve(), args.logs_dir.resolve()
    logs.mkdir(parents=True, exist_ok=True)
    lock = json.loads((TASK / 'ops/v2/integration-sources.json').read_text())
    report = {'research_only': True, 'live_recommendation': False,
              'task_head': git(TASK, 'rev-parse', 'HEAD'), 'sources': {}, 'groups': []}
    try:
        if root.exists():
            raise ValueError('Scratch work root must be absent: ' + str(root))
        if root == TASK or root.is_relative_to(TASK / 'ops'):
            raise ValueError('Unsafe work root')
        sources = {k: (args.sources_root / k).resolve() for k in ['main', 'w1', 'w2', 'w3', 'w4']}
        for key, source in sources.items():
            sha = git(source, 'rev-parse', 'HEAD')
            if key != 'main' and sha != lock['sources'][key]['sha']:
                raise ValueError('Unpinned source: ' + key + ' at ' + sha)
            report['sources'][key] = sha
        for path, expected in lock['reviewed_blobs'].items():
            if git(sources['main'], 'rev-parse', 'HEAD:' + path) != expected:
                raise ValueError('Latest-main spec changed; review and repin: ' + path)
            if blob((TASK / path).read_bytes()) != expected:
                raise ValueError('Task spec differs from reviewed main: ' + path)
        root.mkdir(parents=True)
        copy_directory(sources['main'], root, 'specs/v2')
        for path in ['AGENTS.md', 'RESEARCH_EVIDENCE_SPEC_R4_2.md', 'NAVIGATION_SPEC_R4_2.md', 'index.html', 'CNAME']:
            verified_copy(sources['main'], root, path)
        for path in EXTENSIONS:
            verified_copy(sources['w1'], root, path)
        for key, prefix in [('w2', 'data/v2'), ('w3', 'packages/core-v2'), ('w4', 'apps/web-v2')]:
            copy_directory(sources[key], root, prefix)
        shutil.copytree(TASK / 'ops/v2', root / 'ops/v2', ignore=shutil.ignore_patterns('__pycache__', 'logs'))
        manifest = json.loads((root / 'apps/web-v2/tests/fixtures/worker2/manifest.json').read_text())
        if manifest['commit_sha'] != lock['sources']['w2']['sha']:
            raise ValueError('W4 manifest does not pin current selected W2')
        check_real_sources(root)
        (logs / 'provenance.log').write_text(json.dumps(report, indent=2) + '\nPASS: copied bytes match Git blobs; W3/W4 fixtures match independently checked-out W2.\n')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                   WORKER2_DATA_DIR=str(root / 'data/v2/opportunities'))
        groups = [
            ('w1-schema', ['specs/v2/tests', 'test_schema_smoke.py'], 15, True, False),
            ('w1-evaluation-schema', ['specs/v2/tests', 'test_evaluation_result_security.py'], 2, True, False),
            ('w5-contract', ['ops/v2/tests', 'test_integration_gate.py'], 7, True, False),
            ('w5-watchdog', ['ops/v2/tests', 'test_worker_watchdog.py'], 3, True, False),
            ('w5-runner', ['ops/v2/tests', 'test_ci_runner.py'], 6, True, False),
            ('w3-evaluator', ['packages/core-v2/tests', 'test_*.py'], 20, True, False),
            ('w2-crosswalk-schema', ['data/v2/tests', 'test_*.py'], 5, True, False),
            ('w2-real-records', [sys.executable, 'specs/v2/tests/validate_contract.py',
                *[str(p.relative_to(root)) for p in sorted((root / 'data/v2/opportunities').glob('*.json'))]], None, False, False),
            ('schema-valid-fixture', [sys.executable, 'specs/v2/tests/validate_contract.py'], None, False, False),
            ('w3-compile', [sys.executable, '-m', 'py_compile', 'packages/core-v2/evaluator.py',
                           'packages/core-v2/adapters/source_observation.py'], None, False, False),
            ('w4-node', ['node', '--test', '--test-isolation=none', '--test-timeout=120000', '--test-reporter=tap',
                *[str(p.relative_to(root)) for p in sorted((root / 'apps/web-v2/tests').glob('*.test.mjs'))]], 22, False, True),
            ('local-isolation', [sys.executable, 'ops/v2/integration_gate.py', '--root', str(root)], None, False, False),
            ('browser-smoke', ['node', '--test', '--test-isolation=none', '--test-timeout=120000', '--test-reporter=tap', 'apps/web-v2/tests/browser-smoke.mjs'], 6, False, True),
        ]
        for name, command, expected, python, node in groups:
            report['groups'].append(run_group(name, command, root, logs, env, expected, python, node))
        baseline = ['w1-schema', 'w5-contract', 'w3-evaluator', 'w4-node']
        report['historical_64'] = {k: sum(g['counts'].get(k, 0) for g in report['groups'] if g['name'] in baseline)
                                   for k in ['tests', 'pass', 'fail', 'error', 'skip']}
        report['status'] = 'PASS' if all(g['status'] == 'PASS' for g in report['groups']) else 'FAIL'
    except Exception as exc:
        report['status'] = 'FAIL'
        report['environment_or_source_error'] = f'{type(exc).__name__}: {exc}'
        (logs / 'assembly.log').write_text(report['environment_or_source_error'] + '\n')
        print(report['environment_or_source_error'], file=sys.stderr)
    (logs / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    summary = '# V2 integration: ' + report['status'] + '\n\nResearch-only; no live recommendation.\n\n'
    summary += '| Group | Status | PASS | FAIL | ERROR | SKIP |\n|---|---|---:|---:|---:|---:|\n'
    for g in report['groups']:
        c = g['counts']
        summary += f"| {g['name']} | {g['status']} | {c.get('pass', '—')} | {c.get('fail', '—')} | {c.get('error', 0)} | {c.get('skip', 0)} |\n"
    summary += '\nSource SHAs:\n\n' + '\n'.join(f'- {k}: `{v}`' for k, v in report['sources'].items()) + '\n'
    if report.get('environment_or_source_error'):
        summary += '\nBLOCKED: ' + report['environment_or_source_error'] + '\n'
    (logs / 'summary.md').write_text(summary)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as handle:
            handle.write(summary)
    return int(report['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
