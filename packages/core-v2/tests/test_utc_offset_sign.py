"""CL-UI-24: western-hemisphere UTC offsets must be NEGATIVE.

Regression guard for the Round 9 audit finding: TZ_DISPLAY stored absolute
magnitudes (LA +8 instead of −8), which shifted every western-hemisphere local
clock by +16h and let daytime hours pass as "night" for city-night subjects.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)


class TZSignTests(unittest.TestCase):
    def test_western_zones_negative(self):
        cases = {
            "America/Los_Angeles": (-8, (34.05, -118.24)),
            "America/Denver": (-7, (39.74, -104.99)),
            "America/New_York": (-5, (40.71, -74.01)),
            "America/Anchorage": (-9, (61.22, -149.90)),
            # CL-DATA-43: Hawaii places (us-112..118) previously fell through
            # to the iana=null / offset=0 fallback and rendered good_hours in
            # UTC (Makapuʻu us-117 sunrise showed 17:00 instead of ~07:00).
            "Pacific/Honolulu": (-10, (21.31, -157.65)),
        }
        for zone, (expected, coord) in cases.items():
            got_zone, offset = eb.static_timezone(*coord)
            self.assertEqual(got_zone, zone)
            self.assertEqual(offset, expected, f"{zone} offset must be {expected}")

    def test_eastern_zones_positive(self):
        self.assertEqual(eb.static_timezone(25.03, 121.56),
                         ("Asia/Taipei", 8))
        self.assertEqual(eb.static_timezone(35.68, 139.69),
                         ("Asia/Tokyo", 9))

    def test_local_stamp_is_local_minus_utc(self):
        """local = UTC + offset: LA 02:00 UTC is 18:00 previous local day."""
        zone, offset = eb.static_timezone(34.05, -118.24)
        at = datetime(2026, 11, 5, 2, 0, tzinfo=timezone.utc)
        local = at + timedelta(hours=offset)
        self.assertEqual(offset, -8)
        self.assertEqual(local.hour, 18)
        self.assertEqual(local.day, 4)

    def test_la_night_window_is_real_night(self):
        """LA city_night window hours must fall in 18:00–06:00 local."""
        latest = ROOT / "apps/web-v2/evaluations-latest.json"
        if not latest.exists():
            self.skipTest("evaluations-latest.json not present")
        data = latest.read_bytes()
        if b"America/Los_Angeles\": 8" in data or b'"utc_offset_hours": 8' in data:
            pass  # offsets checked via place scan below
        import json
        bundle = json.loads(data)
        for place in bundle["places"]:
            tzd = place["timezone_display"]
            if tzd["iana"] == "America/Los_Angeles":
                self.assertEqual(tzd["utc_offset_hours"], -8)
                for opp in place["opportunities"]:
                    if opp.get("genre_template") != "city_night":
                        continue
                    for day in opp.get("days", []):
                        for h in day.get("hours", []):
                            if h["status"] != "GUIDANCE_SATISFIED":
                                continue
                            hh, mm = h["local"].split(":")
                            self.assertTrue(
                                int(hh) >= 18 or int(hh) < 6,
                                f"city_night satisfied hour {h['local']} local "
                                f"is daytime for LA")


if __name__ == "__main__":
    unittest.main()
