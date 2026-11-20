"""CL-DATA-78 Phase 1 — spec-quality-engine.md §2 ETL standard keys + astro metrics.

- snow_depth: raw cell renamed to snow_depth_cm (Open-Meteo m * 100);
  METRIC_FIELDS registers the cm name only (no silent m/cm threshold mix).
- Spec-standard metric-name aliases (visibility_km / cloud_cover_mid_high /
  aerosol_optical_depth) resolve to the same raw cells as the legacy names.
- astro standard-key aliases (moon_altitude_deg / moon_illumination /
  galactic_core_altitude_deg) ride the same computed values as the legacy keys.
- moon_azimuth_deg + moon_target_separation_deg view-azimuth branch:
  the spec's 月亮-目標夾角 uses the observation-relations view azimuth vs the
  moon azimuth (azimuth-plane cyclic difference), fail-closed — a missing view
  azimuth keeps the legacy galactic-core-target value, a missing moon azimuth
  propagates UNKNOWN, never a fabricated angle. Winter/summer and
  northern/southern-hemisphere galactic-core cases included.
All offline: no network calls.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)

sys.path.insert(0, str(ROOT / "packages/models-v2"))
import astro_hourly  # noqa: E402


def cell(value):
    return {"value": value, "state": "AVAILABLE"}


class StandardKeyAliasTests(unittest.TestCase):
    """Spec §2 standard metric names resolve to the same raw cells."""

    def test_metric_field_aliases(self):
        self.assertEqual(eb.METRIC_FIELDS["visibility_km"], "visibility")
        self.assertEqual(eb.METRIC_FIELDS["cloud_cover_mid_high"],
                         "cloud_cover_mid_and_high")
        self.assertEqual(eb.METRIC_FIELDS["aerosol_optical_depth"], "aod_550nm")
        self.assertEqual(eb.METRIC_FIELDS["snow_depth_cm"], "snow_depth_cm")
        # legacy names keep resolving — no serving contract changes in Phase 1
        self.assertEqual(eb.METRIC_FIELDS["visibility"], "visibility")
        self.assertEqual(eb.METRIC_FIELDS["cloud_cover_mid_and_high"],
                         "cloud_cover_mid_and_high")
        self.assertEqual(eb.METRIC_FIELDS["aod_550nm"], "aod_550nm")
        # the metre-valued snow_depth metric is NOT aliased (a future
        # m-calibrated threshold must never silently read the cm cell)
        self.assertNotIn("snow_depth", eb.METRIC_FIELDS)

    def test_alias_metric_verdicts(self):
        values = {"visibility": cell(20.0), "cloud_cover_mid_and_high": cell(45.0),
                  "aod_550nm": cell(0.4), "snow_depth_cm": cell(15.0)}
        for metric, op, thr, expect in (
                ("visibility_km", "gte", 15, "PASS"),
                ("visibility_km", "gte", 24, "FAIL"),
                ("cloud_cover_mid_high", "lte", 50, "PASS"),
                ("aerosol_optical_depth", "lte", 0.6, "PASS"),
                ("snow_depth_cm", "gt", 0, "PASS")):
            cond = {"metric": metric, "operator": op, "threshold": thr}
            self.assertEqual(eb.condition_verdict(cond, values, {})[0], expect,
                             f"{metric} {op} {thr}")
        self.assertEqual(
            eb.condition_verdict({"metric": "snow_depth", "operator": "gt",
                                  "threshold": 0}, values, {}),
            ("UNKNOWN", "METRIC_NOT_MAPPED"))

    def test_adapter_emits_cm_cell(self):
        values = eb.snow_cover_levels(
            [{"values": {"snowfall": cell(0.0), "snow_depth_cm": cell(35.0)}}])
        self.assertEqual(values[0]["value"], "snow_covered")

    def test_vocabulary_has_standard_keys(self):
        import json
        vocab = json.loads((ROOT / "data/v2/templates/metric-vocabulary.json")
                           .read_text(encoding="utf-8"))["metrics"]
        for key in ("snow_depth_cm", "visibility_km", "cloud_cover_mid_high",
                    "aerosol_optical_depth", "moon_azimuth_deg",
                    "moon_altitude_deg", "moon_illumination",
                    "galactic_core_altitude_deg"):
            self.assertIn(key, vocab, key)
        self.assertNotIn("snow_depth", vocab)


class AstroStandardKeyTests(unittest.TestCase):
    """Spec §2 astro keys + galactic-core winter/summer + hemisphere cases."""

    TAIPEI = (25.0330, 121.5654)
    SYDNEY = (-33.8688, 151.2093)

    def test_astro_aliases_and_moon_azimuth(self):
        # 2026-11-20 16:00 UTC: Taipei local midnight — moon above/below
        # horizon either way, the alias keys must carry the same values.
        row = astro_hourly.hour_observations(
            datetime(2026, 11, 20, 16, 0, tzinfo=timezone.utc),
            *self.TAIPEI, need_moon=True)
        for legacy, std in (("moon_altitude", "moon_altitude_deg"),
                            ("moon_illumination_fraction", "moon_illumination"),
                            ("galactic_core_altitude", "galactic_core_altitude_deg")):
            self.assertEqual(row[legacy], row[std], std)
        self.assertIsInstance(row["moon_azimuth_deg"], (int, float))
        self.assertTrue(0.0 <= row["moon_azimuth_deg"] <= 360.0)

    def test_galactic_core_winter_summer_taipei(self):
        # Taipei (25N): core (Dec -29 deg) max altitude ~36 deg at summer
        # transit; at winter local midnight the core sits BELOW the horizon.
        summer = astro_hourly.hour_observations(
            datetime(2026, 6, 20, 16, 0, tzinfo=timezone.utc),
            *self.TAIPEI, need_moon=True)
        winter = astro_hourly.hour_observations(
            datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
            *self.TAIPEI, need_moon=True)
        self.assertGreater(summer["galactic_core_altitude_deg"], 20.0)
        self.assertLess(summer["galactic_core_altitude_deg"], 45.0)
        self.assertLess(winter["galactic_core_altitude_deg"], 0.0)

    def test_galactic_core_southern_hemisphere_high(self):
        # Sydney (33.9S): the core culminates near the zenith — far higher
        # than any Taiwan view (max altitude = 90 - |lat - dec| ~ 85 deg).
        row = astro_hourly.hour_observations(
            datetime(2026, 6, 20, 16, 0, tzinfo=timezone.utc),
            *self.SYDNEY, need_moon=True)
        self.assertGreater(row["galactic_core_altitude_deg"], 60.0)
        sydney_alt = row["galactic_core_altitude_deg"]
        taipei_alt = astro_hourly.hour_observations(
            datetime(2026, 6, 20, 16, 0, tzinfo=timezone.utc),
            *self.TAIPEI, need_moon=True)["galactic_core_altitude_deg"]
        self.assertGreater(sydney_alt - taipei_alt, 20.0)


class MoonTargetSeparationViewAzimuthTests(unittest.TestCase):
    """view-azimuth branch: fail-closed, cyclic, below-horizon pass."""

    COND_GTE45 = {"metric": "moon_target_separation_deg", "operator": "gte",
                  "threshold": 45, "id": "C-x"}

    def _verdict(self, condition, astro_row):
        return eb.condition_verdict(condition, {}, astro_row)

    def test_view_azimuth_branch_computes_cyclic_separation(self):
        cond = dict(self.COND_GTE45, view_azimuth_deg=90.0)
        # moon at az 200 -> separation 110 -> >= 45 passes
        astro = {"moon_azimuth_deg": 200.0, "moon_altitude": 30.0}
        status, detail = self._verdict(cond, astro)
        self.assertEqual(status, "PASS")
        self.assertIn("sep=110", detail)
        # moon at az 120 -> separation 30 -> fails
        self.assertEqual(self._verdict(cond, {"moon_azimuth_deg": 120.0,
                                              "moon_altitude": 30.0})[0], "FAIL")
        # wrap-around: view 350, moon 10 -> separation 20
        cond2 = dict(self.COND_GTE45, view_azimuth_deg=350.0)
        self.assertEqual(self._verdict(cond2, {"moon_azimuth_deg": 10.0,
                                               "moon_altitude": 30.0})[0], "FAIL")

    def test_view_azimuth_branch_fail_closed_on_unknown_moon_azimuth(self):
        cond = dict(self.COND_GTE45, view_azimuth_deg=90.0)
        self.assertEqual(
            self._verdict(cond, {"moon_azimuth_deg": None, "moon_altitude": 30.0}),
            ("UNKNOWN", "MOON_AZIMUTH_UNKNOWN"))
        self.assertEqual(
            self._verdict(cond, {}), ("UNKNOWN", "MOON_AZIMUTH_UNKNOWN"))

    def test_view_azimuth_branch_below_horizon_pass(self):
        cond = dict(self.COND_GTE45, view_azimuth_deg=90.0)
        self.assertEqual(
            self._verdict(cond, {"moon_azimuth_deg": 95.0, "moon_altitude": -12.0}),
            ("PASS", "MOON_BELOW_HORIZON_PASS"))

    def test_no_view_azimuth_keeps_legacy_core_separation(self):
        # sentinel (moon below horizon, legacy 999) still degrades to
        # NOT_EVALUABLE, never a fabricated 999-degree PASS.
        cond = dict(self.COND_GTE45)  # no view_azimuth_deg
        self.assertEqual(
            self._verdict(cond, {"moon_target_separation_deg": 999.0}),
            ("UNKNOWN", "MOON_BELOW_HORIZON_SENTINEL_NOT_EVALUABLE"))
        # a real core separation is compared as before
        self.assertEqual(
            self._verdict(cond, {"moon_target_separation_deg": 60.0}),
            ("PASS", "ASTRO_THRESHOLD"))
        self.assertEqual(
            self._verdict(cond, {"moon_target_separation_deg": 10.0}),
            ("FAIL", "ASTRO_THRESHOLD"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
