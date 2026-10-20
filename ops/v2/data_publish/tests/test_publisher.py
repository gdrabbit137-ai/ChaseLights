import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import publisher as p
from compose import compose
from inventory import inventory
from finalize import finalize

REPO = Path(__file__).resolve().parents[4]
SOURCE = '1' * 40


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.code = self.root / 'code'
        self.code.mkdir()
        self.remote = self.root / 'remote.git'
        p.git(self.root, 'init', '--bare', str(self.remote))
        p.git(self.code, 'init', '-q', '-b', 'main')
        p.git(self.code, 'config', 'user.name', 'Test')
        p.git(self.code, 'config', 'user.email', 'test@example.invalid')
        for path, body in {'index.html': 'V1', 'weather-map.html': 'MAP',
                           'apps/web-v2/index.html': 'V2', 'CNAME': 'chaselights.app\n',
                           'tw_weather.json': '{"fixture_only": 1}'}.items():
            target = self.code / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body)
        p.git(self.code, 'add', '.')
        p.git(self.code, 'commit', '-qm', 'test-only source')
        p.git(self.code, 'remote', 'add', 'origin', 'file://' + str(self.remote))
        p.git(self.code, 'push', '-q', 'origin', 'main')
        self.main = self.ref('main')
        self.policy = {'version': 1, 'mode': 'legacy-main', 'data_branch': 'weather-data',
                       'pages_enabled': False}
        self.addCleanup(patch.stopall)
        patch.object(p, 'policy', side_effect=lambda: self.policy).start()
        patch.object(p.time, 'sleep').start()
        patch.dict(os.environ, {'GITHUB_REF': 'refs/heads/main', 'GITHUB_EVENT_NAME': 'workflow_dispatch',
                                'GITHUB_WORKFLOW_REF': 'o/r/.github/workflows/update_weather.yml@refs/heads/main'}).start()

    def ref(self, branch):
        return p.git(self.remote, 'rev-parse', 'refs/heads/' + branch).stdout.decode().strip()

    def boot(self):
        sha = p.bootstrap(self.code)['data_sha']
        self.policy.update(mode='data-branch', pages_enabled=True)
        return sha

    def test_bootstrap_is_data_only_and_never_changes_main(self):
        sha = self.boot()
        paths = p.git(self.remote, 'ls-tree', '-r', '--name-only', sha).stdout.decode().splitlines()
        self.assertEqual(set(paths), {'tw_weather.json', p.MANIFEST})
        self.assertEqual(self.main, self.ref('main'))

    def test_end_to_end_update_then_ancestor_rollback(self):
        first = self.boot()
        p.prepare(self.code)
        (self.code / 'tw_weather.json').write_text('{"fixture_only": 2}')
        second = p.publish(self.code, 'weather')['data_sha']
        self.assertNotEqual(first, second)
        restored = p.rollback(self.code, first)['data_sha']
        self.assertNotEqual(restored, first)
        self.assertEqual(json.loads(p.git(self.remote, 'show', restored + ':tw_weather.json').stdout), {'fixture_only': 1})
        p.git(self.remote, 'merge-base', '--is-ancestor', second, restored)
        self.assertEqual(self.main, self.ref('main'))

    def test_deletion_of_data_absent_from_code_head_is_retained(self):
        self.boot()
        p.prepare(self.code)
        (self.code / 'us_weather.json').write_text('{"fixture_only": true}')
        p.publish(self.code, 'weather')
        p.prepare(self.code)
        (self.code / 'us_weather.json').unlink()
        sha = p.publish(self.code, 'weather')['data_sha']
        self.assertNotEqual(p.git(self.remote, 'show', sha + ':us_weather.json', check=False).returncode, 0)

    def test_unrelated_producer_update_survives_stale_baseline(self):
        self.boot()
        p.prepare(self.code)
        base = json.loads(p.baseline_path(self.code).read_text())['manifest']['files']
        grid = 'weathergrid/gfs_tw_weather_browser.json'
        p.update_snapshot(self.code, 'weather-data', base, {grid: b'{"fixture_only": 3}'}, self.main, 'grid')
        (self.code / 'tw_weather.json').write_text('{"fixture_only": 2}')
        sha = p.publish(self.code, 'weather')['data_sha']
        self.assertEqual(json.loads(p.git(self.remote, 'show', sha + ':' + grid).stdout), {'fixture_only': 3})
        m = json.loads(p.git(self.remote, 'show', sha + ':' + p.MANIFEST).stdout)
        self.assertIn('grid', m['producer_receipts'])
        self.assertIn('weather', m['producer_receipts'])

    def test_same_path_race_fails_without_overwriting_newer_data(self):
        self.boot()
        p.prepare(self.code)
        base = json.loads(p.baseline_path(self.code).read_text())['manifest']['files']
        latest = p.update_snapshot(self.code, 'weather-data', base, {'tw_weather.json': b'{"fixture_only": 3}'}, self.main, 'weather')['data_sha']
        (self.code / 'tw_weather.json').write_text('{"fixture_only": 2}')
        with self.assertRaisesRegex(ValueError, 'Concurrent same-path'):
            p.publish(self.code, 'weather')
        self.assertEqual(latest, self.ref('weather-data'))

    def test_wrong_workflow_identity_cannot_publish(self):
        self.boot()
        with patch.dict(os.environ, {'GITHUB_WORKFLOW_REF': 'o/r/.github/workflows/update_weathergrid.yml@refs/heads/main'}):
            with self.assertRaisesRegex(ValueError, 'identity'):
                p.publish(self.code, 'weather')

    def test_pr_and_nonmain_events_cannot_publish(self):
        for values in ({'GITHUB_EVENT_NAME': 'pull_request'}, {'GITHUB_REF': 'refs/heads/topic'}):
            with patch.dict(os.environ, values):
                with self.assertRaisesRegex(ValueError, 'trusted main'):
                    p.publish(self.code, 'weather')

    def test_missing_data_branch_never_falls_back_to_main(self):
        self.policy.update(mode='data-branch', pages_enabled=True)
        with self.assertRaisesRegex(ValueError, 'never fall back'):
            p.prepare(self.code)
        self.assertEqual(self.main, self.ref('main'))

    def test_final_seed_synchronizes_latest_legacy_without_rewinding_refs(self):
        first = p.bootstrap(self.code)['data_sha']
        (self.code / 'tw_weather.json').write_text('{"fixture_only": "latest legacy"}')
        p.git(self.code, 'add', 'tw_weather.json')
        p.publish(self.code, 'weather')
        current_main = self.ref('main')
        second = p.synchronize(self.code)['data_sha']
        self.assertNotEqual(first, second)
        p.git(self.remote, 'merge-base', '--is-ancestor', first, second)
        self.assertEqual(current_main, self.ref('main'))
        self.policy.update(mode='data-branch', pages_enabled=True)
        with self.assertRaisesRegex(ValueError, 'legacy mode'):
            p.synchronize(self.code)

    def test_bootstrap_refuses_existing_history(self):
        first = p.bootstrap(self.code)['data_sha']
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            p.bootstrap(self.code)
        self.assertEqual(first, self.ref('weather-data'))

    def test_main_and_arbitrary_refs_rejected_at_mutation_boundary(self):
        for branch in ('main', 'codex/task', 'refs/heads/weather-data'):
            with self.assertRaisesRegex(ValueError, 'Forbidden data ref'):
                p.commit_push(self.code, branch, 'forbidden')
        with self.assertRaisesRegex(ValueError, 'outside dedicated'):
            p.checkout_data(self.code, 'file://' + str(self.remote), 'main', self.root / 'unused')

    def test_cross_producer_and_code_deltas_rejected(self):
        self.boot()
        for path in ('index.html', 'weathergrid/jma_msm_tw_cloud_browser.json', '../tw_weather.json'):
            with self.assertRaisesRegex(ValueError, 'outside producer'):
                p.update_snapshot(self.code, 'weather-data', {}, {path: b'{}'}, SOURCE, 'weather')

    def test_stale_observation_deletion_survives_site_assembly(self):
        first = self.boot()
        p.prepare(self.code)
        (self.code / 'tw_weather.json').unlink()
        # Keep another fixture so a completely empty snapshot remains rejected.
        (self.code / 'us_weather.json').write_text('{"fixture_only": true}')
        sha = p.publish(self.code, 'weather')['data_sha']
        dest = self.root / 'data'; dest.mkdir()
        p.checkout_data(self.code, 'file://' + str(self.remote), 'weather-data', dest)
        site = self.root / 'site'
        compose(self.code, dest, site)
        self.assertFalse((site / 'tw_weather.json').exists())
        for path in ('index.html', 'weather-map.html', 'apps/web-v2/index.html', 'CNAME'):
            self.assertEqual((site / path).read_bytes(), (self.code / path).read_bytes())
        self.assertEqual(json.loads((site / 'data-publication-receipt.json').read_text())['data_sha'], sha)

    def test_dirty_site_code_is_not_packaged(self):
        self.boot()
        (self.code / 'index.html').write_text('uncommitted code')
        dest = self.root / 'data'; dest.mkdir()
        p.checkout_data(self.code, 'file://' + str(self.remote), 'weather-data', dest)
        site = self.root / 'site'
        compose(self.code, dest, site)
        self.assertEqual((site / 'index.html').read_text(), 'V1')

    def test_rollback_rejects_source_main_and_nonsha(self):
        self.boot()
        for value in (self.main, 'main'):
            with self.assertRaises(ValueError):
                p.rollback(self.code, value)

    def test_legacy_main_cannot_publish_code_or_wrong_mode(self):
        (self.code / 'index.html').write_text('forbidden')
        p.git(self.code, 'add', 'index.html')
        with self.assertRaisesRegex(ValueError, 'outside producer'):
            p.publish(self.code, 'weather')
        p.git(self.code, 'reset', '--hard', 'HEAD')
        p.git(self.code, 'update-index', '--chmod=+x', 'tw_weather.json')
        with self.assertRaisesRegex(ValueError, 'data mode'):
            p.publish(self.code, 'weather')

    def test_legacy_refresh_still_works_without_protection_bypass(self):
        (self.code / 'tw_weather.json').write_text('{"fixture_only": 2}')
        p.git(self.code, 'add', 'tw_weather.json')
        result = p.publish(self.code, 'weather')
        self.assertTrue(result['changed'])
        self.assertNotEqual(self.main, self.ref('main'))

    def test_main_protection_rejection_fails_closed_locally(self):
        # This is a real local Git receive-hook rejection, NOT evidence that
        # current GitHub main (observed unprotected) already rejects a token.
        hook = self.remote / 'hooks/pre-receive'
        hook.write_text('#!/bin/sh\nwhile read old new ref; do\n[ "$ref" != refs/heads/main ] || exit 1\ndone\n')
        hook.chmod(0o755)
        (self.code / 'tw_weather.json').write_text('{"fixture_only": 2}')
        p.git(self.code, 'add', 'tw_weather.json')
        with self.assertRaisesRegex(ValueError, 'rejected'):
            p.publish(self.code, 'weather')
        self.assertEqual(self.main, self.ref('main'))
        self.boot()  # data-only bootstrap still works under the main deny rule

    def test_json_hash_mode_and_symlink_tampering_rejected(self):
        for mutation in ('hash', 'extra-code', 'mode', 'symlink', 'directory-symlink'):
            dest = self.root / mutation; dest.mkdir()
            p.write_snapshot(dest, {'tw_weather.json': b'{}'}, SOURCE, 'bootstrap')
            if mutation == 'hash': (dest / 'tw_weather.json').write_text('{"changed": true}')
            elif mutation == 'extra-code': (dest / 'evil.js').write_text('throw 1')
            elif mutation == 'mode': (dest / 'tw_weather.json').chmod(0o755)
            elif mutation == 'symlink':
                (dest / 'tw_weather.json').unlink(); (dest / 'tw_weather.json').symlink_to(self.code / 'tw_weather.json')
            else: (dest / 'linked').symlink_to(self.code, target_is_directory=True)
            with self.assertRaises(ValueError, msg=mutation): p.read_snapshot(dest)

    def test_invalid_and_nonfinite_json_rejected(self):
        self.boot()
        p.prepare(self.code)
        for body in ('{', '{"invalid": NaN}'):
            (self.code / 'tw_weather.json').write_text(body)
            with self.assertRaises(ValueError): p.publish(self.code, 'weather')

    def test_allowlist_boundaries(self):
        for path in ('../tw_weather.json', '/tw_weather.json', 'weathergrid/v2/../index.json',
                     'weathergrid/v2/cwa/current/code.py', 'data/v2/opportunity.json',
                     'weathergrid/unreviewed.json', '.github/workflows/test.json'):
            self.assertFalse(p.allowed(path), path)

    def test_jekyll_finalizer_retains_domain_and_rejects_changed_json(self):
        out = self.root / 'built'; out.mkdir()
        for path in ('index.html', 'weather-map.html', 'apps/web-v2/index.html', 'tw_weather.json'):
            target = out / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((self.code / path).read_bytes())
        receipt = {'data_manifest': {'files': {'tw_weather.json': p.digest((out / 'tw_weather.json').read_bytes())}}}
        self.assertEqual(finalize(self.code, out, receipt)['json_files'], 1)
        self.assertEqual((out / 'CNAME').read_bytes(), (self.code / 'CNAME').read_bytes())
        (out / 'tw_weather.json').write_text('{"fixture_only": "modified"}')
        with self.assertRaisesRegex(ValueError, 'differs'):
            finalize(self.code, out, receipt)

    def test_exhaustive_current_workflow_inventory(self):
        self.assertEqual(len(inventory(REPO)), 11)


if __name__ == '__main__':
    unittest.main()
