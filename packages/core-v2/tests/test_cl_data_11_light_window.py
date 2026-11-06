"""CL-DATA-11: cloud-sea light window (owner ruling + clarification 2026-11-05).

雲海只在民用光線下可拍 - the earlier "unless there is moonlight" reading was
an owner rhetorical question, NOT a ruling; the moonlight exception is
withdrawn. The `light_window` metric is a necessary hourly condition for
cloud_sea contracts with a single semantics: EVERY sampled instant of the hour
bucket must have sun elevation > -6 deg (civil light). Night hours never
qualify REGARDLESS of the moon - no moon metric is consulted. Pinned
scenarios:
- a fully sunlit hour passes (pure solar geometry, no moon data);
- a dark night hour FAILS even with a high, well-illuminated moon - 23:00
  can never qualify a cloud-sea hour;
- a mid-morning hour fails the golden-hour window (sunset subject red line).
Offline tests, no network.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]

spec = importlib.util.spec_from_file_location(
    "astro_hourly", ROOT / "packages/models-v2/astro_hourly.py")
ah = importlib.util.module_from_spec(spec)
sys.modules["astro_hourly"] = ah
spec.loader.exec_module(ah)

# 大屯山 (Datunshan), northern Taiwan.
LAT, LON = 25.17614, 121.52244


def utc(hours_local_gmt8):
    return datetime(2026, 11, 5, hours_local_gmt8 - 8, 0,
                    tzinfo=timezone.utc)


class LightWindowCivilLightTests(unittest.TestCase):
    def test_fully_sunlit_hour_passes(self):
        obs = ah.hour_observations(utc(13), LAT, LON, need_moon=False)
        self.assertIs(obs["light_window"], True)

    def test_straddle_dusk_hour_fails(self):
        # A bucket straddling civil dusk has dark-tail samples: it can never
        # qualify, the whole-bucket rule excludes the going-dark hour.
        obs = ah.hour_observations(utc(18), LAT, LON, need_moon=True)
        self.assertIs(obs["light_window"], False)

    def test_night_hour_fails_regardless_of_moon(self):
        # 23:00 local with a high, well-illuminated moon: still no cloud sea.
        def bright_moon(dt_utc, lat, lon):
            return {"moon_altitude_deg": 55.0,
                    "moon_illumination_fraction": 1.0,
                    "moon_target_separation_deg": 90.0,
                    "moon_illuminance_proxy": 1.0,
                    "galactic_core_altitude": 5.0}
        with patch.object(ah, "lunar_ephemeris_for_galactic_core", bright_moon):
            obs = ah.hour_observations(utc(23), LAT, LON, need_moon=True)
        self.assertIs(obs["light_window"], False)


class SunsetSubjectWindowTests(unittest.TestCase):
    def test_mid_morning_fails_golden_hour_window(self):
        # 南雅奇岩「夕照雲霞」: the corrected contract makes golden_hour_window a
        # REQUIRED condition, so a 10:00 hour (sun high) can never qualify.
        obs = ah.hour_observations(utc(10), LAT, LON, need_moon=False)
        self.assertIs(obs["golden_hour_window"], False)
        self.assertIs(obs["sunset_window"], False)


if __name__ == "__main__":
    unittest.main()
