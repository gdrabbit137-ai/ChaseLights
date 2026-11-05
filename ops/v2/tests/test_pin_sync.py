"""CL-CI-05 regressions: owner tree pins auto-follow the tree, deletions gated."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sync_integration_sources import current_trees, sync
from validate_release_config import validate_pin_sync
import yaml


class PinSyncTests(unittest.TestCase):
    def fixture(self):
        root = Path(tempfile.mkdtemp())

        def git(*args):
            return subprocess.check_output(["git", "-C", str(root), *args],
                                           text=True, stderr=subprocess.DEVNULL).strip()
        git("init", "-q")
        git("config", "user.name", "pin sync test")
        git("config", "user.email", "test@example.invalid")
        for path in ("specs/v2", "data/v2", "packages/core-v2",
                     "packages/models-v2", "apps/web-v2"):
            (root / path).mkdir(parents=True)
            (root / path / "a.txt").write_text("original\n")
        (root / "apps/web-v2" / "b.txt").write_text("original\n")
        git("add", ".")
        git("commit", "-qm", "synthetic base")
        lock = {"sources": {}}
        for owner, info in current_trees(root).items():
            lock["sources"][owner] = dict(info)
        (root / "ops").mkdir()
        (root / "ops/v2").mkdir(parents=True)
        (root / "ops/v2/integration-sources.json").write_text(json.dumps(lock))
        return root, git, lock

    def test_pin_auto_follows_owner_tree_change(self):
        root, git, lock = self.fixture()
        (root / "specs/v2/new_contract.md").write_text("new w1 content\n")
        git("add", ".")
        git("commit", "-qm", "w1 tree change without manual re-pin")
        old_tree = lock["sources"]["w1"]["tree_sha"]
        changes = sync(root)
        lock = json.loads((root / "ops/v2/integration-sources.json").read_text())
        self.assertEqual(lock["sources"]["w1"]["tree_sha"],
                         git("rev-parse", "HEAD:specs/v2"))
        self.assertEqual(lock["sources"]["w1"]["previous_tree_sha"], old_tree)
        self.assertEqual(changes["w1"]["previous_tree_sha"], old_tree)
        # W2 untouched
        self.assertEqual(lock["sources"]["w2"]["tree_sha"],
                         git("rev-parse", "HEAD:data/v2"))

    def test_file_count_drop_is_refused_without_explicit_acceptance(self):
        root, git, lock = self.fixture()
        (root / "apps/web-v2/b.txt").unlink()
        git("add", "-A")
        git("commit", "-qm", "w4 file deleted")
        baseline = lock["sources"]["w4"]["file_count"]
        with self.assertRaisesRegex(ValueError, "accept-decrease"):
            sync(root)
        # After explicit acceptance the pins follow and record the decision.
        sync(root, accept_decrease=True)
        lock = json.loads((root / "ops/v2/integration-sources.json").read_text())
        self.assertEqual(lock["sources"]["w4"]["file_count"], baseline - 1)
        self.assertEqual(lock["sources"]["w4"]["accepted_file_count_decrease"]
                         ["previous_file_count"], baseline)

    def test_growth_and_check_mode(self):
        root, git, lock = self.fixture()
        (root / "data/v2/extra.json").write_text("{}\n")
        git("add", ".")
        git("commit", "-qm", "w2 addition")
        # --check must report stale before sync and in-sync after.
        stale = subprocess.run([sys.executable,
                                str(Path(__file__).resolve().parents[1] /
                                    "sync_integration_sources.py"),
                                "--root", str(root), "--check"], capture_output=True, text=True)
        self.assertEqual(stale.returncode, 1)
        self.assertIn("STALE", stale.stdout)
        before = json.loads(lock["sources"]["w2"]["file_count"] and
                            (root / "ops/v2/integration-sources.json").read_text())
        self.assertEqual(before["sources"]["w2"]["file_count"], 1)
        sync(root)
        clean = subprocess.run([sys.executable,
                                str(Path(__file__).resolve().parents[1] /
                                    "sync_integration_sources.py"),
                                "--root", str(root), "--check"], capture_output=True, text=True)
        self.assertEqual(clean.returncode, 0)
        self.assertIn("IN_SYNC", clean.stdout)
        after = json.loads((root / "ops/v2/integration-sources.json").read_text())
        self.assertEqual(after["sources"]["w2"]["file_count"], 2)

    def test_w3_multi_subtree_pins_auto_follow(self):
        """CL-CI-10: a w3 tree change syncs both owned subtrees (core-v2 +
        models-v2) and the sync cannot lower the combined file_count."""
        root, git, lock = self.fixture()
        (root / "packages/models-v2/new_model.py").write_text("new w3 content\n")
        git("add", ".")
        git("commit", "-qm", "w3 models-v2 tree change without manual re-pin")
        sync(root)
        lock = json.loads((root / "ops/v2/integration-sources.json").read_text())
        self.assertEqual(lock["sources"]["w3"]["tree_sha"],
                         git("rev-parse", "HEAD:packages/core-v2"))
        self.assertEqual(lock["sources"]["w3"]["models_tree_sha"],
                         git("rev-parse", "HEAD:packages/models-v2"))
        self.assertEqual(lock["sources"]["w3"]["previous_models_tree_sha"],
                         git("rev-parse", "HEAD~1:packages/models-v2"))
        baseline = lock["sources"]["w3"]["file_count"]
        (root / "packages/core-v2/a.txt").unlink()
        git("add", "-A")
        git("commit", "-qm", "w3 file deleted")
        with self.assertRaisesRegex(ValueError, "accept-decrease"):
            sync(root)
        sync(root, accept_decrease=True)
        lock = json.loads((root / "ops/v2/integration-sources.json").read_text())
        self.assertEqual(lock["sources"]["w3"]["file_count"], baseline - 1)
        self.assertEqual(lock["sources"]["w3"]["accepted_file_count_decrease"]
                         ["previous_file_count"], baseline)

    def test_real_pin_sync_workflow_pushes_only_the_lock(self):
        root = Path(__file__).resolve().parents[3]
        flow = yaml.load((root / '.github/workflows/v2-pin-sync.yml').read_text(),
                         Loader=yaml.BaseLoader)
        result = validate_pin_sync(flow)
        self.assertFalse(result['deployment_allowed'])
        unsafe = yaml.load(flow and (
            root / '.github/workflows/v2-integration.yml').read_text(),
            Loader=yaml.BaseLoader)
        with self.assertRaises(ValueError):
            # The read-only integration workflow must not satisfy the pin-sync
            # contract (it pushes nothing and lacks the sync-before-push gate).
            unsafe and validate_pin_sync({'on': {'push': {'branches': ['other']}},
                                          'jobs': unsafe['jobs']})


if __name__ == "__main__":
    unittest.main()
