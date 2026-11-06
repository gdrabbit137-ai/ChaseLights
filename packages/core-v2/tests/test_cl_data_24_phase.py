"""CL-DATA-24: dusk-named subjects must not match symmetric window hours on
the dawn side. astro_hourly now emits a per-hour `phase` ("dawn"/"dusk") from
the sun's rise/set direction, and evaluate_batch honours a condition-level
`phase` constraint on ASTRO window metrics.

All inputs are synthetic TEST-ONLY fixtures, never live forecasts.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "astro_hourly", ROOT / "packages/models-v2/astro_hourly.py")
ah = importlib.util.module_from_spec(spec)
sys.modules["astro_hourly"] = ah
spec.loader.exec_module(ah)

spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)

TPEI = (25.0330, 121.5654)


class SunPhaseTests(unittest.TestCase):
    def _observe(self, points, hour, events=None):
        """Synthetic piecewise-linear altitude curve: points = [(offset_min,
        alt_deg), ...] over the bucket [hour:00, hour+1:00)."""
        from datetime import datetime, timezone

        def _fake_alt(dt_utc, lat, lon):
            t = dt_utc.timestamp()
            h0 = datetime(2026, 11, 7, hour, 0, tzinfo=timezone.utc).timestamp()
            off = (t - h0) / 60.0
            pts = sorted([(0.0, points[0][1])] + list(points) + [(60.0, points[-1][1])])
            prev = pts[0]
            for nxt in pts[1:]:
                if prev[0] <= off <= nxt[0]:
                    frac = (off - prev[0]) / (nxt[0] - prev[0]) if nxt[0] > prev[0] else 0.0
                    return prev[1] + frac * (nxt[1] - prev[1])
                prev = nxt
            return pts[-1][1]

        with patch.object(ah, "_sun_altitude", _fake_alt):
            return ah.hour_observations(
                datetime(2026, 11, 7, hour, 0, tzinfo=timezone.utc),
                *TPEI, events=events)

    def test_rising_bucket_is_dawn(self):
        # altitude rises across the bucket: dawn side (e.g. pre-sunrise twilight)
        row = self._observe([(0, -8.0), (30, -2.0), (55, 3.0)], 21)
        self.assertEqual(row["phase"], "dawn")

    def test_falling_bucket_is_dusk(self):
        # altitude falls across the bucket: dusk side (post-sunset twilight)
        row = self._observe([(0, 3.0), (30, -2.0), (55, -8.0)], 9)
        self.assertEqual(row["phase"], "dusk")

    def test_phase_is_pure_geometry_no_events_needed(self):
        # events=None must still yield a phase: the phase comes from the
        # sampled altitude trend, never from the events list.
        row = self._observe([(0, -8.0), (55, 3.0)], 21, events=[])
        self.assertIn(row["phase"], ("dawn", "dusk"))

    def test_symmetric_window_persists_in_both_phases(self):
        # blue_hour_window (-8..-4) holds on both sides; phase is the only
        # discriminator — this is the exact defect CL-DATA-24 fixes.
        row = self._observe([(0, -7.0), (30, -6.0), (55, -5.0)], 21)
        self.assertTrue(row["blue_hour_window"])
        row = self._observe([(0, -5.0), (30, -6.0), (55, -7.0)], 9)
        self.assertTrue(row["blue_hour_window"])
        self.assertEqual(row["phase"], "dusk")


class PhaseGateTests(unittest.TestCase):
    COND = {"id": "C-x", "role": "REQUIRED", "domain": "ASTRONOMY",
            "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
            "metric": "blue_hour_window", "operator": "none",
            "unknown_policy": "propagate_unknown", "claim_refs": ["x"],
            "phase": "dusk"}

    def test_wrong_phase_fails_even_when_window_satisfied(self):
        verdict, detail = eb.condition_verdict(
            self.COND, {}, {"blue_hour_window": True, "phase": "dawn"})
        self.assertEqual((verdict, detail), ("FAIL", "ASTRO_PHASE_MISMATCH"))

    def test_matching_phase_passes_on_window_membership(self):
        verdict, detail = eb.condition_verdict(
            self.COND, {}, {"blue_hour_window": True, "phase": "dusk"})
        self.assertEqual((verdict, detail), ("PASS", "ASTRO_WINDOW_MEMBERSHIP"))

    def test_wrong_phase_fails_unsatisfied_window_too(self):
        verdict, detail = eb.condition_verdict(
            self.COND, {}, {"blue_hour_window": False, "phase": "dawn"})
        self.assertEqual((verdict, detail), ("FAIL", "ASTRO_PHASE_MISMATCH"))

    def test_unavailable_phase_propagates_unknown(self):
        verdict, detail = eb.condition_verdict(
            self.COND, {}, {"blue_hour_window": True, "phase": None})
        self.assertEqual((verdict, detail), ("UNKNOWN", "ASTRO_PHASE_UNAVAILABLE"))

    def test_no_phase_constraint_keeps_plain_window_semantics(self):
        cond = dict(self.COND); cond.pop("phase")
        verdict, detail = eb.condition_verdict(
            cond, {}, {"blue_hour_window": True, "phase": "dawn"})
        self.assertEqual((verdict, detail), ("PASS", "ASTRO_WINDOW_MEMBERSHIP"))

    def test_phase_gate_does_not_touch_weather_metrics(self):
        cond = {"id": "C-w", "role": "REQUIRED", "domain": "WEATHER",
                "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
                "metric": "cloud_cover_total", "operator": "lte",
                "threshold": 70, "unknown_policy": "propagate_unknown",
                "claim_refs": ["x"], "phase": "dusk"}
        values = {"cloud_cover_total": {"state": "AVAILABLE", "value": 40}}
        verdict, detail = eb.condition_verdict(cond, values, {"phase": "dawn"})
        self.assertEqual((verdict, detail), ("PASS", "FORECAST_THRESHOLD"))


class RealGeometryPhaseTests(unittest.TestCase):
    """Real deterministic geometry (no mocks): for Taipei the bucket holding
    the sunrise event must be dawn; the bucket holding sunset must be dusk."""

    def test_taipei_sunrise_bucket_is_dawn_sunset_is_dusk(self):
        from datetime import datetime, timedelta, timezone
        start = datetime(2026, 11, 7, tzinfo=timezone.utc)
        events = ah.sun_events_span(TPEI[0], TPEI[1],
                                    start.timestamp(), start.timestamp() + 86400)
        sunrises = [t for t, kind in events if kind == "sunrise"]
        sunsets = [t for t, kind in events if kind == "sunset"]
        self.assertTrue(sunrises and sunsets)
        # Taipei UTC+8: sunrise ~21:2x UTC (05:2x local), sunset ~09:0x UTC.
        sr_dt = datetime.fromtimestamp(sunrises[0], timezone.utc)
        ss_dt = datetime.fromtimestamp(sunsets[0], timezone.utc)
        self.assertEqual(sr_dt.hour, 22)  # 06:xx local next day (early-November Taipei)
        self.assertEqual(ss_dt.hour, 9)   # 17:xx local
        dawn_row = ah.hour_observations(
            sr_dt.replace(minute=0, second=0, microsecond=0), *TPEI, events=events)
        self.assertEqual(dawn_row["phase"], "dawn")
        # the hour after sunrise (morning golden hour) stays on the dawn side
        m_golden = dawn_row  # next-hour check
        later = ah.hour_observations(
            sr_dt.replace(minute=0, second=0, microsecond=0)
            + timedelta(hours=1), *TPEI, events=events)
        self.assertEqual(later["phase"], "dawn")
        self.assertEqual(m_golden["phase"], "dawn")
        dusk_row = ah.hour_observations(
            ss_dt.replace(minute=0, second=0, microsecond=0), *TPEI, events=events)
        self.assertEqual(dusk_row["phase"], "dusk")


if __name__ == "__main__":
    unittest.main()
