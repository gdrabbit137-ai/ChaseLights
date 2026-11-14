"""CL-DATA-68: minute-level solar window boundaries (civil twilight module).

Covers: civil dawn/dusk ordering against sunrise/sunset on the SAME
NOAA/Meeus chain solar_window is validated against; the minute-level vs
hour-bucket difference case (a boundary hour that reads dark at the grid
instant but contains civil-light minutes); midnight-spanning night windows;
polar honesty (no crossing -> no fabricated boundary); the once-per-place-
day cache; and the offset sign (negative-offset Hawaii days stay inside the
local day). Offline, no network.
"""
from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "models-v2"))

import civil_twilight as ct  # noqa: E402
from solar_window import _solar_altitude_deg  # noqa: E402


def _h(m):
    if m is None:
        return None
    return "%02d:%02d" % (m // 60, m % 60)


class CivilTwilightTests(unittest.TestCase):
    def test_taipei_order_and_civil_span(self):
        s = ct.solar_day_windows(25.033, 121.565, "2026-11-14", 8)
        ev = s["events"]
        self.assertTrue(ev["civil_dawn"] < ev["sunrise"] < ev["sunset"]
                        < ev["civil_dusk"])
        self.assertGreater(ev["civil_dusk"] - ev["civil_dawn"],
                           ev["sunset"] - ev["sunrise"])
        self.assertTrue(0 <= ev["civil_dawn"] < 1440)
        self.assertTrue(0 <= ev["civil_dusk"] < 1440)

    def test_minute_boundary_hour_the_grid_instant_calls_dark(self):
        # THE CL-DATA-68 case: Taipei 2026-11-14 civil dawn 05:45. The 05:00
        # hour bucket reads DARK at the grid instant (sun still below -6 at
        # 05:00) yet contains civil-light minutes 05:45-06:00 — the
        # minute-level civil-light interval catches it, the old hour-bucket
        # instant test did not.
        s = ct.solar_day_windows(25.033, 121.565, "2026-11-14", 8)
        dawn = s["events"]["civil_dawn"]
        self.assertIsNotNone(dawn)
        grid_alt = _solar_altitude_deg(
            datetime(2026, 11, 13, 21, 0, tzinfo=timezone.utc), 25.033, 121.565)
        self.assertLessEqual(grid_alt, -6.0, "grid instant 05:00 must be dark")
        self.assertTrue(ct.hour_hits_interval(
            300, 60, s["intervals"]["light_window"]))
        self.assertEqual(dawn, 5 * 60 + 45)

    def test_night_windows_span_midnight(self):
        s = ct.solar_day_windows(25.033, 121.565, "2026-11-14", 8)
        night = s["intervals"]["city_night_window"]
        # the -6 crossing shared by light/city-night tiles the day: the
        # night stretch that started yesterday ends at civil dawn.
        self.assertTrue(any(e == s["events"]["civil_dawn"] and start < 0
                            for start, e in night))
        self.assertTrue(any(start == s["events"]["civil_dusk"] and e > 1440
                            for start, e in night))

    def test_light_and_city_night_share_crossings(self):
        s = ct.solar_day_windows(25.033, 121.565, "2026-11-14", 8)
        light_bounds = {b for iv in s["intervals"]["light_window"]
                        for b in iv}
        night_bounds = {b for iv in s["intervals"]["city_night_window"]
                        for b in iv}
        shared = light_bounds & night_bounds
        self.assertTrue(shared, "light/night intervals share the -6 crossing")

    def test_polar_day_honest_no_boundary(self):
        s = ct.solar_day_windows(69.65, 18.96, "2026-06-21", 2)
        self.assertEqual(s["events"]["civil_dawn"], None)
        self.assertEqual(s["events"]["civil_dusk"], None)

    def test_place_day_cache_is_shared(self):
        a = ct.solar_day_windows(25.033, 121.565, "2026-11-14", 8)
        b = ct.solar_day_windows(25.033, 121.565, "2026-11-14", 8)
        self.assertIs(a, b, "one computation per place-day")

    def test_negative_offset_stays_in_the_local_day(self):
        s = ct.solar_day_windows(21.3, -157.86, "2026-11-14", -10)
        ev = s["events"]
        for key in ("civil_dawn", "civil_dusk", "sunrise", "sunset"):
            self.assertTrue(0 <= ev[key] < 1440, key)
        self.assertTrue(ev["civil_dawn"] < ev["sunrise"] < ev["sunset"]
                        < ev["civil_dusk"])

    def test_narrow_windows_around_their_events(self):
        s = ct.solar_day_windows(25.033, 121.565, "2026-11-14", 8)
        sr = s["events"]["sunrise"]
        win = next(iv for iv in s["intervals"]["sunrise_time_window"]
                   if iv[0] <= sr <= iv[1])
        self.assertLessEqual(win[1] - win[0], 80)
        golden = [iv for iv in s["intervals"]["golden_hour_window"]
                  if iv[1] > 0 and iv[0] < 1440]
        self.assertGreaterEqual(len(golden), 2,
                                "dawn and dusk golden-hour sides")

    def test_helpers_expose_day_start_and_local_minutes(self):
        day_start = ct.local_day_start_epoch("2026-11-14", 8)
        self.assertAlmostEqual(
            ct.epoch_local_minutes(day_start, day_start), 0.0)
        self.assertAlmostEqual(
            ct.epoch_local_minutes(day_start, day_start + 3600.0), 60.0)


if __name__ == "__main__":
    unittest.main()
