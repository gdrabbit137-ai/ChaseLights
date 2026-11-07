"""CL-UI-08 synthetic tests: sub-hour interval sampling for narrow astro windows.

Guarantees that a window falling STRICTLY between two whole-hour grid points is
still detected (the root cause of the systematic UNFAVORABLE false negatives in
CL-UI-08). The synthetic altitude curve is piecewise linear, so window
membership at every 5-minute sample is exact.
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

NOON_TPEI = (25.0330, 121.5654)  # Elephant Mountain vicinity (synthetic only)


def _epoch(h, m=0):
    return datetime(2026, 11, 1, h, m, tzinfo=timezone.utc).timestamp()


def _interp(points, t):
    """Piecewise-linear interpolation over sorted (epoch, altitude) points."""
    if t <= points[0][0]:
        return points[0][1]
    if t >= points[-1][0]:
        return points[-1][1]
    for i in range(len(points) - 1):
        t0, a0 = points[i]
        t1, a1 = points[i + 1]
        if t0 <= t <= t1:
            frac = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            return a0 + frac * (a1 - a0)
    return points[-1][1]


def _fake_alt_factory(points):
    def _fake_alt(dt_utc, lat, lon):
        return _interp(points, dt_utc.timestamp())
    return _fake_alt


class WindowProfileTests(unittest.TestCase):
    """CL-DATA-31: per-sample window profiles — a qualifying bucket's earliest
    passing sample must not lead the actual window (sunrise ±40 min labels)."""

    LAT, LON = NOON_TPEI

    def _profiles(self, points, dt_utc):
        with patch.object(ah, "_sun_altitude", _fake_alt_factory(points)):
            return ah.window_pass_profiles(dt_utc, self.LAT, self.LON)

    def test_sunrise_profile_first_pass_lags_bucket_start(self):
        # Sun crosses the horizon 65 min AFTER the bucket start: the bucket
        # qualifies (a sample sits inside sunrise±40) but its earliest passing
        # sample is minute 25, not the bucket start.
        t0 = _epoch(0)
        pts = [(t0, -6.5), (t0 + 60 * 60, -0.5), (t0 + 70 * 60, 0.5),
               (t0 + 180 * 60, 5.0)]
        profiles = self._profiles(pts, datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc))
        self.assertFalse(profiles["sunrise_time_window"][0])
        self.assertTrue(any(profiles["sunrise_time_window"]))
        first = ah.WINDOW_SAMPLE_OFFSETS[
            profiles["sunrise_time_window"].index(True)]
        self.assertEqual(first, 25)

    def test_all_metrics_profiles_agree_with_hour_observations(self):
        t0 = _epoch(12)
        pts = [(t0 - 3600, -8.0), (t0, 4.0), (t0 + 1800, -2.0),
               (t0 + 3600, -8.0), (t0 + 5400, -20.0), (t0 + 9000, -25.0)]
        dt = datetime.fromtimestamp(t0, timezone.utc)
        with patch.object(ah, "_sun_altitude", _fake_alt_factory(pts)):
            obs = ah.hour_observations(dt, self.LAT, self.LON)
            profiles = ah.window_pass_profiles(dt, self.LAT, self.LON)
        for metric, aggregate in (("astronomical_darkness", any),
                                  ("city_night_window", all),
                                  ("golden_hour_window", any),
                                  ("blue_hour_window", any),
                                  ("light_window", all),
                                  ("sunrise_time_window", any),
                                  ("sunset_window", any)):
            self.assertEqual(obs[metric], aggregate(profiles[metric]),
                             metric)

    def test_no_crossing_propagates_unknown_not_false(self):
        # Polar day: no sunrise/sunset crossing in the ±24h span — the window
        # metric stays None (UNKNOWN), never a fabricated False FAIL.
        t0 = _epoch(0)
        pts = [(t0 - 90000, 15.0), (t0, 15.0), (t0 + 90000, 15.0)]
        with patch.object(ah, "_sun_altitude", _fake_alt_factory(pts)):
            obs = ah.hour_observations(datetime.fromtimestamp(t0, timezone.utc),
                                       self.LAT, self.LON)
        self.assertIsNone(obs["sunrise_time_window"])
        self.assertIsNone(obs["sunset_window"])


class SubHourSamplingTests(unittest.TestCase):
    LAT, LON = NOON_TPEI

    def _observe(self, points, dt_utc, events=None):
        with patch.object(ah, "_sun_altitude", _fake_alt_factory(points)):
            return ah.hour_observations(dt_utc, self.LAT, self.LON,
                                        events=events)

    def _bucket(self, points, hour, events=None):
        return self._observe(
            points, datetime(2026, 11, 1, hour, 0, tzinfo=timezone.utc),
            events=events)

    def test_blue_hour_window_between_grid_points(self):
        # Blue hour (-8..-4) strictly inside hour 10:
        # alt(10:00) = -9.5 -> FAIL, alt(10:30) = -6.0 -> PASS,
        # alt(11:00) = -2.5 -> FAIL. Both grid instants miss the window.
        points = [(_epoch(9, 0), -10.0), (_epoch(10, 0), -9.5),
                  (_epoch(10, 30), -6.0), (_epoch(11, 0), -2.5),
                  (_epoch(12, 0), 5.0)]
        self.assertFalse(-8.0 <= -9.5 <= -4.0)   # grid instant 10:00
        self.assertFalse(-8.0 <= -2.5 <= -4.0)   # grid instant 11:00
        row = self._bucket(points, 10)
        self.assertTrue(row["blue_hour_window"])
        for hour in (9, 11):
            self.assertFalse(self._bucket(points, hour)["blue_hour_window"],
                             f"bucket {hour} must not be contaminated")

    def test_golden_hour_window_between_grid_points(self):
        # Golden hour (-6..+6) strictly inside hour 10; grid instants miss it.
        points = [(_epoch(9, 0), -8.0), (_epoch(10, 0), -8.0),
                  (_epoch(10, 15), -2.0), (_epoch(10, 30), 8.0),
                  (_epoch(11, 0), 20.0), (_epoch(12, 0), 30.0)]
        self.assertFalse(-6.0 <= -8.0 <= 6.0)    # grid instant 10:00
        self.assertFalse(-6.0 <= 20.0 <= 6.0)    # grid instant 11:00
        self.assertTrue(self._bucket(points, 10)["golden_hour_window"])
        self.assertFalse(self._bucket(points, 11)["golden_hour_window"])

    def test_astronomical_darkness_between_grid_points(self):
        # Darkness (<= -18) strictly inside hour 10; grid instants at -15 fail.
        points = [(_epoch(9, 0), -15.0), (_epoch(10, 0), -15.0),
                  (_epoch(10, 30), -20.0), (_epoch(11, 0), -15.0),
                  (_epoch(12, 0), -15.0)]
        self.assertFalse(-15.0 <= -18.0)         # grid instants 10:00 / 11:00
        self.assertTrue(self._bucket(points, 10)["astronomical_darkness"])
        for hour in (9, 11):
            self.assertFalse(
                self._bucket(points, hour)["astronomical_darkness"],
                f"bucket {hour} must not be contaminated")

    def test_sunrise_time_window_interval_overlap(self):
        # Sunrise crossing at 10:30 -> 80-minute window [09:50, 11:10].
        # The window overlaps buckets 09, 10, 11; bucket 12 is too far.
        events = [(_epoch(10, 30), "sunrise")]
        points = [(_epoch(9, 0), -15.0), (_epoch(12, 0), 15.0)]
        for hour in (9, 10, 11):
            self.assertTrue(
                self._bucket(points, hour, events)["sunrise_time_window"],
                f"bucket {hour} must overlap the sunrise window")
        self.assertFalse(self._bucket(points, 12, events)["sunrise_time_window"])

    def test_sunset_window_interval_overlap(self):
        # Sunset crossing at 10:30 -> 80-minute window [09:50, 11:10].
        events = [(_epoch(10, 30), "sunset")]
        points = [(_epoch(9, 0), 15.0), (_epoch(12, 0), -15.0)]
        for hour in (9, 10, 11):
            self.assertTrue(
                self._bucket(points, hour, events)["sunset_window"],
                f"bucket {hour} must overlap the sunset window")
        self.assertFalse(self._bucket(points, 12, events)["sunset_window"])

    def test_provenance_declares_sub_hour_sampling(self):
        prov = ah.ASTRO_SAMPLING_PROVENANCE
        self.assertEqual(prov["mode"], "sub_hour_interval_scan")
        self.assertEqual(prov["step_minutes"], 5)
        self.assertEqual(prov["samples_per_hour"], 12)
        self.assertEqual(prov["sample_offsets_minutes"],
                         list(range(0, 60, 5)))
        for metric in ("blue_hour_window", "sunset_window",
                       "sunrise_time_window", "golden_hour_window",
                       "astronomical_darkness"):
            self.assertIn(metric, prov["metrics"])


if __name__ == "__main__":
    unittest.main()
