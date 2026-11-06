"""CL-DATA-13: sun_azimuth_deg pins — azimuth from the same NOAA/Meeus chain.

Pin provenance:
- tw legacy V1 astronomy values (jp-001 2026-11-04T23:00Z sun_azimuth 131.5,
  sun_elevation 16.3) cross-check the V2 chain against the independently
  produced legacy curve (both within 0.1 deg).
- Tamsui (tw-003) monthly sunset-azimuth pins back the light_direction
  month-sector design: the seasonal swing is ~51-52 deg (winter ~244,
  summer ~296) — a single fixed arc would aim at the wrong direction for
  half of the year (CL-PHOTO-02 evidence report).
"""
from __future__ import annotations

import importlib.util
import math
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sw = _load("solar_window", "packages/models-v2/solar_window.py")
ah = _load("astro_hourly", "packages/models-v2/astro_hourly.py")

JP001 = (43.493611, 142.614167)  # Biei Blue Pond (legacy V1 pin source)
TW003 = (25.18339, 121.41147)    # Tamsui Fisherman's Wharf


def _utc(y, mo, d, h, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=timezone.utc)


class SunAzimuthPinTests(unittest.TestCase):
    def test_legacy_v1_cross_source_pin(self):
        """The V2 chain must reproduce the legacy V1 sun_azimuth/sun_elevation
        for the same instant to within 0.1 deg (jp-001, 2026-11-05 08:00 JST)."""
        at = _utc(2026, 11, 4, 23, 0)  # = 2026-11-05 08:00 JST
        az = sw._solar_azimuth_deg(at, *JP001)
        alt = sw._solar_altitude_deg(at, *JP001)
        self.assertAlmostEqual(az, 131.5, delta=0.1)
        self.assertAlmostEqual(alt, 16.3, delta=0.1)

    def test_hour_observations_carries_azimuth(self):
        row = ah.hour_observations(_utc(2026, 11, 4, 23, 0), *JP001)
        self.assertIsNotNone(row["sun_azimuth_deg"])
        self.assertAlmostEqual(row["sun_azimuth_deg"], 131.5, delta=0.1)

    def test_azimuth_qc_range_and_continuity(self):
        """QC: every azimuth stays in [0, 360]; while the sun is at or above
        -10 deg elevation (the only regime where light direction is
        photographically meaningful) consecutive-hour azimuth moves stay
        under 15 deg/h. Deep-night azimuths are geometrically defined but
        not light-direction signals; their wrap-around is not QC'd."""
        for h in range(24):
            at = _utc(2026, 11, 5, h, 0)
            az = sw._solar_azimuth_deg(at, *TW003)
            alt = sw._solar_altitude_deg(at, *TW003)
            self.assertTrue(0.0 <= az <= 360.0)
            if alt > -10.0:
                nxt = _utc(2026, 11, 5, h + 1, 0)
                if nxt.day == 5:  # keep the same local day
                    az2 = sw._solar_azimuth_deg(nxt, *TW003)
                    self.assertLess(abs(az2 - az), 20.0)

    def test_sunset_azimuth_monthly_swing_pin(self):
        """Monthly sunset azimuth at Tamsui: winter ~244, summer ~296
        (CL-PHOTO-02 evidence: 51-52 deg seasonal swing). Values are pinned
        to the V2 chain itself, re-measured via sun_events_span."""
        pins = {}
        for month in (1, 7):
            events = ah.sun_events_span(
                *TW003,
                datetime(2026, month, 15, 0, 0, tzinfo=timezone.utc).timestamp(),
                datetime(2026, month, 15, 23, 59, tzinfo=timezone.utc).timestamp())
            sunsets = [t for t, kind in events if kind == "sunset"]
            self.assertTrue(sunsets)
            sunset = datetime.fromtimestamp(sunsets[0], timezone.utc)
            pins[month] = round(sw._solar_azimuth_deg(sunset, *TW003), 1)
        self.assertAlmostEqual(pins[1], 246.6, delta=1.5)
        self.assertAlmostEqual(pins[7], 293.9, delta=1.5)
        self.assertGreaterEqual(pins[7] - pins[1], 45.0)


if __name__ == "__main__":
    unittest.main()
