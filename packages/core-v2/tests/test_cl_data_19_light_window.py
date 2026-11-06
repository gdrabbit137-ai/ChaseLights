"""CL-DATA-19: mid-latitude all-day subjects gain a civil light_window.

得月樓 (tw-062-P01, 建築外觀, overcast_soft, Kinmen 24.4N) exposed the
systemic defect the spot-check found: mid-latitude all-day genres passed the
weather gates at night (00:00-05:00 qualified although there is no light to
shoot in). The fix adds the same civil light_window (sun elevation > -6 deg,
CL-DATA-11 same-source semantics, night hours never qualify) to 126
mid-latitude all-day contracts. Pinned scenarios:
- a night hour at the 得月樓 coordinates FAILS the light window;
- a midday hour PASSES it;
- the window semantics are independent of the moon (no moon metric consulted).
Offline tests, no network.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

spec = importlib.util.spec_from_file_location(
    "astro_hourly", ROOT / "packages/models-v2/astro_hourly.py")
ah = importlib.util.module_from_spec(spec)
sys.modules["astro_hourly"] = ah
spec.loader.exec_module(ah)

# 得月樓, Jincheng, Kinmen.
LAT, LON = 24.40583, 118.30056


def utc(hours_local_gmt8):
    h = hours_local_gmt8 - 8
    d = 7
    while h < 0:
        h += 24
        d -= 1
    return datetime(2026, 11, d, h, 0,
                    tzinfo=timezone.utc)


class Data19MidLatitudeLightWindowTests(unittest.TestCase):
    def test_night_hour_fails_at_deyue_lou(self):
        # 03:00 local: no civil light, the building facade is unshootable.
        obs = ah.hour_observations(utc(3), LAT, LON, need_moon=False)
        self.assertIs(obs["light_window"], False)

    def test_midday_hour_passes(self):
        obs = ah.hour_observations(utc(13), LAT, LON, need_moon=False)
        self.assertIs(obs["light_window"], True)

    def test_straddle_dusk_hour_fails(self):
        # A bucket straddling civil dusk has dark-tail samples: whole-bucket
        # rule excludes it, same as CL-DATA-11 cloud_sea semantics.
        obs = ah.hour_observations(utc(18), LAT, LON, need_moon=False)
        self.assertIs(obs["light_window"], False)


if __name__ == "__main__":
    unittest.main()
