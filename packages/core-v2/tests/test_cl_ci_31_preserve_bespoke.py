"""CL-CI-31: the fail_reason_overrides generator must not clobber bespoke copy.

Evidence (CL-DATA-20): rerunning build_fail_reason_overrides.py rewrote the
whole JSON from the script's (stale) BESPOKE tables, silently replacing
hand-tuned trilingual entries with generic template text. The fix makes the
on-disk JSON the SOURCE OF TRUTH: the generator preserves every existing
entry verbatim and only APPENDS opportunity/metric slots that are missing,
matching the on-disk serialization (indent/CRLF) so a no-op rerun is
byte-identical.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "v2" / "copy" / "fail_reason_overrides.json"
SCRIPT = ROOT / "data" / "v2" / "tools" / "build_fail_reason_overrides.py"

_spec = importlib.util.spec_from_file_location("bfro", SCRIPT)
bfro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bfro)


def _entries(d):
    return {(oid, m): json.dumps(v, sort_keys=True) for oid, mm in d.items() for m, v in mm.items()}


class MergePreserveUnit(unittest.TestCase):
    """merge_preserve: existing wins verbatim; only missing slots append."""

    def test_existing_entry_wins(self):
        existing = {"tw-001-P01": {"light_direction": {"zh-TW": "手寫", "en": "hand", "ja": "手書き"}}}
        generated = {"tw-001-P01": {"light_direction": {"zh-TW": "模板", "en": "template", "ja": "テンプレート"}}}
        merged = bfro.merge_preserve(existing, generated)
        self.assertEqual(merged["tw-001-P01"]["light_direction"]["zh-TW"], "手寫")
        self.assertEqual(merged["tw-001-P01"]["light_direction"]["ja"], "手書き")

    def test_new_metric_appends(self):
        existing = {"tw-001-P01": {"light_direction": {"zh-TW": "手寫", "en": "hand", "ja": "手書き"}}}
        generated = {"tw-001-P01": {"precipitation": {"zh-TW": "新", "en": "new", "ja": "新しい"}}}
        merged = bfro.merge_preserve(existing, generated)
        self.assertEqual(merged["tw-001-P01"]["precipitation"]["zh-TW"], "新")
        self.assertEqual(merged["tw-001-P01"]["light_direction"]["zh-TW"], "手寫")

    def test_new_opportunity_appends_and_lost_metrics_survive(self):
        existing = {"tw-001-P01": {"light_direction": {"zh-TW": "x", "en": "x", "ja": "x"}}}
        generated = {"tw-999-P99": {"visibility": {"zh-TW": "n", "en": "n", "ja": "n"}}}
        merged = bfro.merge_preserve(existing, generated)
        self.assertIn("tw-001-P01", merged)   # stale vs generator — preserved (CL-CI-31 lost-3 fix)
        self.assertIn("tw-999-P99", merged)


class GeneratorIdempotence(unittest.TestCase):
    """Integration pin: two consecutive generator runs are byte-identical,
    and the first run never alters any existing entry (append-only)."""

    def test_rerun_is_byte_identical_and_preserves_entries(self):
        before_bytes = OUT.read_bytes()
        before = json.loads(before_bytes.decode("utf-8"))
        before_entries = _entries(before)
        hashes = []
        for run in (1, 2):
            res = subprocess.run([sys.executable, str(SCRIPT), "all"],
                                 capture_output=True, text=True, timeout=600)
            self.assertEqual(res.returncode, 0, res.stderr[-2000:])
            data = OUT.read_bytes()
            hashes.append(hashlib.sha256(data).hexdigest())
            after = json.loads(data.decode("utf-8"))
            after_entries = _entries(after)
            for k, v in before_entries.items():
                self.assertIn(k, after_entries, f"entry lost on run {run}: {k}")
                self.assertEqual(v, after_entries[k], f"entry rewritten on run {run}: {k}")
            run1 = (before_bytes == data)
            if run == 1 and not run1:
                # first run may legitimately APPEND missing contract coverage;
                # entries must still all be preserved (checked above) and the
                # file must only ever GROW.
                self.assertGreater(len(after_entries), len(before_entries))
        self.assertEqual(hashes[0], hashes[1],
                         "generator is not idempotent — rerun changed the bytes")


if __name__ == "__main__":
    unittest.main()
