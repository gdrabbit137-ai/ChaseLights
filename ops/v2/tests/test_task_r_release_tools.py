"""W5 infrastructure tests; synthetic Git fixtures are not research/provider evidence."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_static import build, validate_refs, RUNTIME_FILES
from release_readiness import assess, CHECKS
from simulate_merges import rehearse, fixed_commit
from validate_release_config import validate

SHA = '1' * 40
BASE = '2' * 40


def snapshot():
    rows = []
    for identifier, (_, domain) in CHECKS.items():
        rows.append({'id': identifier, 'status': 'PASS', 'candidate_sha': SHA,
                     'domain': domain, 'reason': 'Synthetic infrastructure regression',
                     'evidence': ['Synthetic test record, never real acceptance'],
                     'github': {'head_sha': SHA, 'tested_checkout_sha': '3' * 40,
                                'tested_parents': [BASE, SHA], 'conclusion': 'success',
                                'url': 'https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/1',
                                'counts': {'tests': 169, 'pass': 169, 'fail': 0, 'error': 0, 'skip': 0}}})
    return {'candidate_sha': SHA, 'reviewed_main_sha': BASE, 'checks': rows}


class ReleaseToolsTests(unittest.TestCase):
    def test_missing_evidence_is_unverified_and_never_permission(self):
        result = assess({'candidate_sha': SHA, 'reviewed_main_sha': BASE}, SHA)
        self.assertEqual(result['status'], 'UNVERIFIED')
        self.assertFalse(result['deployment_allowed'])

    def test_green_ci_cannot_override_known_blocker(self):
        data = snapshot(); data['checks'][8]['status'] = 'BLOCKED'
        self.assertEqual(assess(data, SHA)['status'], 'NOT READY')

    def test_wrong_candidate_sha_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'different candidate'):
            assess(snapshot(), BASE)

    def test_duplicate_and_skip_cannot_be_accepted(self):
        data = snapshot(); data['checks'].append(copy.deepcopy(data['checks'][0]))
        with self.assertRaises(ValueError): assess(data, SHA)
        data = snapshot(); data['checks'][0]['status'] = 'SKIP'
        with self.assertRaises(ValueError): assess(data, SHA)

    def test_ci_requires_actual_head_and_merge_parent_linkage(self):
        for key, value in [('head_sha', BASE), ('tested_parents', [])]:
            data = snapshot()
            row = next(x for x in data['checks'] if x['id'] == 'E.actual_commit_ci')
            row['github'][key] = value
            self.assertEqual(assess(data, SHA)['status'], 'UNVERIFIED')
        data = snapshot(); data['checks'][0]['domain'] = 'public'
        self.assertEqual(assess(data, SHA)['status'], 'UNVERIFIED')

    def test_failed_skipped_or_missing_counts_fail_closed(self):
        for counts in [{'tests': 169, 'pass': 168, 'fail': 1, 'error': 0, 'skip': 0},
                       {'tests': 169, 'pass': 168, 'fail': 0, 'error': 0, 'skip': 1}, {}]:
            data = snapshot()
            next(x for x in data['checks'] if x['id'] == 'E.no_failed_or_skipped_tests')['github']['counts'] = counts
            self.assertEqual(assess(data, SHA)['status'], 'NOT READY')

    def test_full_advisory_checklist_still_requires_review_and_approval(self):
        result = assess(snapshot(), SHA)
        self.assertEqual(result['status'], 'READY FOR APPROVAL')
        self.assertEqual(result['approval'], 'NOT_GRANTED')
        self.assertFalse(result['deployment_allowed'])
        self.assertEqual(result['evidence_authenticity'], 'EXTERNAL_REVIEW_REQUIRED')

    def test_unpackaged_external_and_parent_dependencies_are_rejected(self):
        for script in [b"import x from '../legacy.mjs'", b"import 'https://evil.invalid/x.mjs'", b"fetch('./missing.json')"]:
            with self.assertRaises(ValueError):
                validate_refs({'index.html': b'<title>V2</title>', 'app.mjs': script})

    def test_unsafe_plan_or_ci_failure_bypass_is_rejected(self):
        plan = json.loads((Path(__file__).resolve().parents[1] / 'deployment_plan.json').read_text())
        flow = {'permissions': {'contents': 'read'}, 'on': {'pull_request': {}, 'push': {}, 'workflow_dispatch': {}},
                'jobs': {'test': {'steps': [{'run': 'python check.py'}]}}}
        self.assertEqual(validate(plan, flow)['status'], 'PASS')
        for step in [{'run': 'python check.py || true'}, {'uses': 'actions/deploy-pages@v4'}, {'continue-on-error': 'true'}]:
            unsafe = copy.deepcopy(flow); unsafe['jobs']['test']['steps'] = [step]
            with self.assertRaises(ValueError): validate(plan, unsafe)
        unsafe = copy.deepcopy(plan); unsafe['deployment_enabled_by_this_plan'] = True
        with self.assertRaises(ValueError): validate(unsafe, flow)
        flow['permissions']['contents'] = 'write'
        with self.assertRaises(ValueError): validate(plan, flow)

    def fixture_repo(self, directory):
        root = Path(directory)
        def git(*args):
            return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL).decode().strip()
        git('init', '-q'); git('config', 'user.name', 'W5 test'); git('config', 'user.email', 'test@example.invalid')
        for path in ['specs/v2', 'data/v2', 'packages/core-v2', 'packages/models-v2', 'apps/web-v2', 'ops/v2']:
            (root / path).mkdir(parents=True); (root / path / 'test.txt').write_text('Synthetic infra fixture\n')
        git('add', '.'); git('commit', '-qm', 'synthetic owner source'); pin = git('rev-parse', 'HEAD')
        lock = {'sources': {w: {'sha': pin} for w in ['w1', 'w2', 'w3', 'w4']}}
        (root / 'ops/v2/integration-sources.json').write_text(json.dumps(lock))
        git('add', '.'); git('commit', '-qm', 'synthetic main'); base = git('rev-parse', 'HEAD')
        (root / 'ops/v2/test.txt').write_text('candidate\n'); git('add', '.'); git('commit', '-qm', 'synthetic candidate')
        return root, git, base, git('rev-parse', 'HEAD')

    def test_already_integrated_owner_pins_rehearse_without_ref_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, git, base, candidate = self.fixture_repo(tmp)
            before = git('show-ref')
            result = rehearse(root, base, candidate)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(before, git('show-ref'))
            with self.assertRaises(ValueError): fixed_commit(root, 'HEAD')

    def test_merge_conflict_and_nonowner_changes_fail_without_ref_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, git, base, candidate = self.fixture_repo(tmp)
            git('checkout', '--detach', base)
            (root / 'ops/v2/test.txt').write_text('incompatible main edit\n')
            git('add', '.'); git('commit', '-qm', 'conflict'); main = git('rev-parse', 'HEAD')
            before = git('show-ref')
            with self.assertRaisesRegex(ValueError, 'Merge conflict'): rehearse(root, main, candidate)
            self.assertEqual(before, git('show-ref'))
            git('checkout', '--detach', base)
            (root / 'index.html').write_text('forbidden Legacy change\n')
            git('add', '.'); git('commit', '-qm', 'nonowner')
            with self.assertRaisesRegex(ValueError, 'W5-only'): rehearse(root, base, git('rev-parse', 'HEAD'))

    def test_build_rejects_dirty_sources_and_source_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, git, _, _ = self.fixture_repo(tmp)
            files = {n: b'// synthetic build regression\n' for n in RUNTIME_FILES}
            files['index.html'] = b'<title>V2</title><script type="module" src="./app.mjs"></script>'
            files['catalog.v2.json'] = json.dumps({'research_only': True, 'forecast_available': False,
                                                  'selected_date_recommendation_eligible': False, 'evaluations': []}).encode()
            for name, body in files.items(): (root / 'apps/web-v2' / name).write_bytes(body)
            git('add', '.'); git('commit', '-qm', 'synthetic build files')
            with patch('build_static.verify_main', return_value={'owner_trees': {}}):
                output = root / 'work/build'
                result = build(root, output)
                self.assertFalse(result['deployment_allowed'])
                self.assertEqual(set(result['files']), {'apps/web-v2/' + n for n in RUNTIME_FILES})
                self.assertFalse((output / 'public/index.html').exists())
                with self.assertRaises(ValueError): build(root, output)
                with self.assertRaises(ValueError): build(root, root / 'data/v2/release')
                (root / 'apps/web-v2/app.mjs').write_text('dirty\n')
                with self.assertRaisesRegex(ValueError, 'Dirty'): build(root, root / 'work/dirty-build')


if __name__ == '__main__': unittest.main()
