"""CL-DATA-11: cloud-sea light window (owner ruling 2026-11-05).

雲海晚上除非有月光否則看不到 — a sea of clouds is invisible at night unless
there is moonlight. The new `light_window` metric is a necessary hourly
condition for cloud_sea contracts: EVERY sampled instant of the hour bucket
must be lit — sun elevation > -6 deg (civil light) OR moon above the horizon
with moon illumination fraction >= 0.5 (reusing the existing
moon_illumination_fraction semantics). Pinned scenarios:
- a fully sunlit hour passes on the solar branch alone (no moon data needed);
- a dark night hour with a moonless sky (or sub-50% moon) FAILS — 23:00 with
  no moon can no longer qualify a cloud-sea hour;
- a dark night hour lit by a >= 50%-illuminated moon PASSES;
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


class LightWindowSolarBranchTests(unittest.TestCase):
    def test_fully_sunlit_hour_passes_without_moon_data(self):
        obs = ah.hour_observations(utc(13), LAT, LON, need_moon=False)
        self.assertIs(obs["light_window"], True)

    def test_straddle_dusk_without_moon_data_is_unknown(self):
        obs = ah.hour_observations(utc(18), LAT, LON, need_moon=False)
        self.assertIsNone(obs["light_window"])


class LightWindowMoonBranchTests(unittest.TestCase):
    """Dark buckets decided by the moon branch (mocked ephemeris)."""

    def run_dark_hour(self, moon_alt_deg, illum):
        def fake_ephem(dt_utc, lat, lon):
            return {"moon_altitude_deg": moon_alt_deg,
                    "moon_illumination_fraction": illum,
                    "moon_target_separation_deg": 90.0,
                    "moon_illuminance_proxy": illum, "galactic_core_altitude": 5.0}
        with patch.object(ah, "lunar_ephemeris_for_galactic_core", fake_ephem):
            return ah.hour_observations(utc(23), LAT, LON, need_moon=True)

    def test_moonless_night_fails(self):
        # 23:00 local, moon below horizon: cloud sea no longer qualifies.
        self.assertIs(self.run_dark_hour(-10.0, 0.9)["light_window"], False)

    def test_low_illumination_night_fails(self):
        # Moon up but < 50% illumination: not enough moonlight.
        self.assertIs(self.run_dark_hour(40.0, 0.3)["light_window"], False)

    def test_half_moon_night_passes(self):
        # Moon above horizon with illumination >= 50%: the night hour qualifies.
        self.assertIs(self.run_dark_hour(40.0, 0.5)["light_window"], True)

    def test_partially_dark_bucket_fails_even_with_moon(self):
        # A bucket that straddles civil dusk with a dark tail fails: the
        # whole-bucket rule keeps a going-dark hour from qualifying.
        def fake_ephem(dt_utc, lat, lon):
            return {"moon_altitude_deg": -20.0,
                    "moon_illumination_fraction": 0.9,
                    "moon_target_separation_deg": 90.0,
                    "moon_illuminance_proxy": 0.0, "galactic_core_altitude": 5.0}
        with patch.object(ah, "lunar_ephemeris_for_galactic_core", fake_ephem):
            obs = ah.hour_observations(utc(18), LAT, LON, need_moon=True)
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
