"""Offline tests for V2 watchdog: not a proof of worker execution."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from worker_watchdog import classify, identify, snapshot, render

NOW = datetime(2026, 10, 9, 21, tzinfo=timezone.utc)

class Stub:
    def pages(self, path):
        if path == "branches":
            return [
                {"name": "v2/worker1-test", "commit": {"sha": "a"}},
                {"name": "v2/worker2-test", "commit": {"sha": "b"}},
                {"name": "irrelevant", "commit": {"sha": "z"}}]
        if path == "pulls?state=open":
            return [{"number": 430, "html_url": "https://github.com/a/b/pull/430",
                     "draft": True, "head": {"ref": "v2/worker1-test", "sha": "a"}}]
        raise AssertionError(path)
    def get(self, path):
        if path.endswith("check-runs"):
            return {"check_runs": []}
        dates = {"a": "2026-10-09T20:55:00Z", "b": "2026-10-09T12:00:00Z"}
        return {"commit": {"committer": {"date": dates[path.split("/")[-1]]}}}

class Tests(unittest.TestCase):
    def test_worker_mapping(self):
        self.assertEqual(identify("w3/v2-m3"), "W3")
        self.assertEqual(identify("worker4/v2-web"), "W4")
        self.assertIsNone(identify("weathergrid_v2"))
    def test_age_is_advisory(self):
        self.assertEqual(classify(None, NOW), "UNKNOWN")
        self.assertEqual(classify("2026-10-09T20:00:00Z", NOW), "RECENT_COMMIT")
        self.assertEqual(classify("2026-10-09T16:00:00Z", NOW), "REVIEW_NO_RECENT_COMMIT")
    def test_real_github_signal_not_automation_success(self):
        data = snapshot(Stub(), NOW)
        self.assertEqual(data["workers"]["W2"]["signal"], "REVIEW_NO_RECENT_COMMIT")
        self.assertEqual(data["workers"]["W3"]["signal"], "UNKNOWN")
        self.assertEqual(data["workers"]["W1"]["automation_run"], "UNOBSERVABLE_FROM_GITHUB")
        self.assertEqual(data["open_worker_prs"][0]["action"], "CHECKS_MISSING")
        self.assertIn("Advisory only", render(data))

if __name__ == "__main__":
    unittest.main()
