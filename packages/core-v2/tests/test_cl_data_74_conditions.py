"""CL-DATA-74 five-genre engine tests (offline).

- alpenglow_window: the -0.8..-6 deg civil-band summit-light window rides the
  same sub-hour sampling family as the light_window engine; a bucket inside
  the band sits within the sunset +-40 min window (evening side).
- snow_cover_state: the derived three-level ground enum (snowing /
  snow_covered / none) collapses the ticket OR semantics (snowfall > 0 OR
  snow_depth > 0); both snow fields missing -> fail-closed UNKNOWN.
- clear_streak_hours: the continuous-clear probe (CHALLENGER-15 continuity
  semantics) for star_trails — streak ending at the current hour, gaps never
  counted, missing cells break the streak honestly.
- firefly: season window (calendar bridge), moon <= 30% with the batch-A
  below-horizon pass, humidity/temp/no-rain gates.
- moonlit_scene: full-moon vs new-moon day contrast, the 5-30 deg moon
  elevation band, and the honest moon-down veto (the below-horizon auto-pass
  of the illumination gate must never make a moonless hour moonlit).
"""
from __future__ import annotations

import importlib.util
import json
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


def available(value):
    return {"value": value, "state": "AVAILABLE"}


def hour_row(**cells):
    return {"values": {k: available(v) for k, v in cells.items()}}


class AlpenglowWindowTests(unittest.TestCase):
    HEHUAN = (24.1426, 121.2712)
    EVENING = datetime(2026, 11, 16, 10, 0, tzinfo=timezone.utc)  # ~18:00 TW

    def test_band_constants(self):
        self.assertEqual(astro_hourly.ALPENGLOW_LOW_DEG, -6.0)
        self.assertEqual(astro_hourly.ALPENGLOW_HIGH_DEG, -0.8)

    def test_some_evening_bucket_is_in_band(self):
        hours = [datetime(2026, 11, 16, 8 + i, 0, tzinfo=timezone.utc)
                 for i in range(6)]
        rows = [astro_hourly.hour_observations(h, *self.HEHUAN, need_moon=False)
                for h in hours]
        hits = [r["alpenglow_window"] for r in rows]
        self.assertIn(True, hits, "one of the dusk buckets must catch the band")
        self.assertIn(False, hits)
        # any bucket inside the band also sits inside the sunset +-40 min
        # window (the band is below -0.8 deg, which is ~4 min after sunset at
        # this latitude, and above -6 deg, ~30 min after sunset)
        for r in rows:
            if r["alpenglow_window"]:
                self.assertTrue(r["sunset_window"], r)
                self.assertEqual(r["phase"], "dusk", r)

    def test_registered_in_provenance(self):
        self.assertIn("alpenglow_window", astro_hourly.ASTRO_SAMPLING_PROVENANCE["metrics"])

    def test_astro_threshold_membership(self):
        astro = {"alpenglow_window": True}
        cond = {"metric": "alpenglow_window", "operator": "none", "threshold": None}
        self.assertEqual(eb.condition_verdict(cond, {}, astro)[0], "PASS")
        self.assertEqual(
            eb.condition_verdict(cond, {}, {"alpenglow_window": False})[0], "FAIL")
        self.assertEqual(
            eb.condition_verdict(cond, {}, {"alpenglow_window": None})[0], "UNKNOWN")


class SnowCoverStateTests(unittest.TestCase):
    COND = {"metric": "snow_cover_state", "operator": "none", "threshold": None}

    def test_or_semantics_collapsed(self):
        # snowfall > 0 (snowing) OR snow_depth > 0 (snow_covered) — one is
        # enough; never both required.
        self.assertEqual(
            eb.snow_cover_levels([hour_row(snowfall=0.4, snow_depth=0.0)])[0]["value"],
            "snowing")
        self.assertEqual(
            eb.snow_cover_levels([hour_row(snowfall=0.0, snow_depth=0.35)])[0]["value"],
            "snow_covered")
        self.assertEqual(
            eb.snow_cover_levels([hour_row(snowfall=0.0, snow_depth=0.0)])[0]["value"],
            "none")
        self.assertEqual(
            eb.snow_cover_levels([hour_row(snowfall=1.2, snow_depth=0.8)])[0]["value"],
            "snowing")

    def test_depth_only_row_never_claims_snowing(self):
        # a depth-only row cannot speak for snowfall — a 0 depth with no
        # snowfall cell is "none", not a fabricated "snowing".
        self.assertEqual(
            eb.snow_cover_levels([hour_row(snow_depth=0.0)])[0]["value"], "none")

    def test_both_fields_missing_fail_closed(self):
        cells = eb.snow_cover_levels([{"values": {"snowfall": {"state": "UNAVAILABLE"},
                                                  "snow_depth": {"state": "UNAVAILABLE"}}}])
        self.assertEqual(cells[0]["state"], "UNKNOWN")
        self.assertEqual(
            eb.condition_verdict(dict(self.COND), {}, {})[1],
            "SNOW_COVER_STATE_DERIVATION_UNAVAILABLE")

    def test_verdicts(self):
        self.assertEqual(
            eb.condition_verdict(dict(self.COND),
                                 {"snow_cover_state": available("snowing")}, {})[0], "PASS")
        self.assertEqual(
            eb.condition_verdict(dict(self.COND),
                                 {"snow_cover_state": available("snow_covered")}, {})[0],
            "PASS")
        verdict, detail = eb.condition_verdict(
            dict(self.COND), {"snow_cover_state": available("none")}, {})
        self.assertEqual((verdict, detail), ("FAIL", "SNOW_COVER_STATE(none)"))

    def test_display_value(self):
        cond = {"metric": "snow_cover_state", "operator": "none"}
        self.assertEqual(eb.condition_value(cond, {"snow_cover_state": available("snowing")}, {}),
                         "snowing")
        self.assertIsNone(eb.condition_value(cond, {}, {}))


class ClearStreakTests(unittest.TestCase):
    COND = {"metric": "clear_streak_hours", "operator": "gte", "threshold": 2.0}

    def test_streak_counts_consecutive_clear_hours(self):
        rows = [hour_row(cloud_cover_total=15), hour_row(cloud_cover_total=20),
                hour_row(cloud_cover_total=45), hour_row(cloud_cover_total=10)]
        values = [c["value"] for c in eb.clear_streak_levels(rows)]
        self.assertEqual(values, [1.0, 2.0, 0.0, 1.0])

    def test_missing_cell_breaks_streak(self):
        rows = [hour_row(cloud_cover_total=15),
                {"values": {"cloud_cover_total": {"state": "UNAVAILABLE"}}},
                hour_row(cloud_cover_total=10)]
        cells = eb.clear_streak_levels(rows)
        self.assertEqual([c["value"] for c in cells], [1.0, None, 1.0])
        self.assertEqual(cells[1]["state"], "UNKNOWN")

    def test_verdict_two_hour_window(self):
        self.assertEqual(
            eb.condition_verdict(dict(self.COND),
                                 {"clear_streak_hours": available(2.0)}, {})[0], "PASS")
        self.assertEqual(
            eb.condition_verdict(dict(self.COND),
                                 {"clear_streak_hours": available(1.0)}, {})[0], "FAIL")
        # a missing streak cell propagates UNKNOWN (fail-closed), never a FAIL
        verdict, detail = eb.condition_verdict(dict(self.COND), {}, {})
        self.assertEqual((verdict, detail), ("UNKNOWN", "CELL_NOT_AVAILABLE"))


class FireflyConditionTests(unittest.TestCase):
    def test_moon_gate_with_below_horizon_pass(self):
        cond = {"metric": "moon_illumination_fraction", "operator": "lte", "threshold": 0.3}
        self.assertEqual(eb.condition_verdict(cond, {}, {"moon_illumination_fraction": 0.2,
                                                         "moon_altitude": 30.0})[0], "PASS")
        self.assertEqual(eb.condition_verdict(cond, {}, {"moon_illumination_fraction": 0.9,
                                                         "moon_altitude": 20.0})[0], "FAIL")
        # moon below the horizon: the gate cannot veto (CL-DATA-72 batch A)
        self.assertEqual(
            eb.condition_verdict(cond, {}, {"moon_illumination_fraction": 0.9,
                                            "moon_altitude": -20.0}),
            ("PASS", "MOON_BELOW_HORIZON_PASS"))

    def test_weather_gates(self):
        humidity = {"metric": "relative_humidity_2m", "operator": "gte", "threshold": 85.0}
        temp = {"metric": "temperature_2m", "operator": "gte", "threshold": 15.0}
        rain = {"metric": "precipitation", "operator": "lt", "threshold": 0.2}
        self.assertEqual(eb.condition_verdict(humidity, {"relative_humidity_2m": available(88)}, {})[0], "PASS")
        self.assertEqual(eb.condition_verdict(humidity, {"relative_humidity_2m": available(70)}, {})[0], "FAIL")
        self.assertEqual(eb.condition_verdict(temp, {"temperature_2m": available(16)}, {})[0], "PASS")
        self.assertEqual(eb.condition_verdict(temp, {"temperature_2m": available(12)}, {})[0], "FAIL")
        self.assertEqual(eb.condition_verdict(rain, {"precipitation": available(0.0)}, {})[0], "PASS")
        self.assertEqual(eb.condition_verdict(rain, {"precipitation": available(0.5)}, {})[0], "FAIL")

    def test_season_window_open_and_closed(self):
        # the firefly TW window rides the seasonal-calendar bridge: open in
        # May, closed in July, UNKNOWN without any calendar entry.
        cond = {"metric": "seasonal_state", "operator": "eq", "threshold": "window_open",
                "seasonal_entries": [{"plant_id": "firefly_season",
                                      "typical_window": {"start": "04-01", "end": "06-15"},
                                      "current_season": None}]}
        from datetime import date
        self.assertEqual(eb.condition_verdict(cond, {}, {}, local_date=date(2026, 5, 15))[0],
                         "PASS")
        self.assertEqual(eb.condition_verdict(cond, {}, {}, local_date=date(2026, 7, 1))[0],
                         "FAIL")
        bare = {k: v for k, v in cond.items() if k != "seasonal_entries"}
        verdict, detail = eb.condition_verdict(bare, {}, {}, local_date=date(2026, 5, 15))
        self.assertEqual((verdict, detail), ("UNKNOWN", "NO_SEASONAL_CALENDAR_ENTRY"))


class MoonlitConditionTests(unittest.TestCase):
    ILLUM = {"metric": "moon_illumination_fraction", "operator": "gte", "threshold": 0.85}
    ELEV = {"metric": "moon_altitude", "operator": "between", "threshold": [5, 30]}

    def test_full_moon_vs_new_moon(self):
        self.assertEqual(eb.condition_verdict(dict(self.ILLUM), {},
                                              {"moon_illumination_fraction": 0.98,
                                               "moon_altitude": 20.0})[0], "PASS")
        self.assertEqual(eb.condition_verdict(dict(self.ILLUM), {},
                                              {"moon_illumination_fraction": 0.10,
                                               "moon_altitude": 20.0})[0], "FAIL")

    def test_elevation_band(self):
        for alt, expected in ((5.0, "PASS"), (30.0, "PASS"), (20.0, "PASS"),
                              (3.0, "FAIL"), (35.0, "FAIL")):
            self.assertEqual(eb.condition_verdict(dict(self.ELEV), {},
                                                  {"moon_altitude": alt})[0], expected)

    def test_moon_down_hour_is_never_moonlit(self):
        # The batch-A below-horizon auto-pass stands the illumination gate
        # down on a moonless hour; the elevation band must still veto the
        # hour, so a moonless night can never read as moonlit.
        roles = {"m1": "REQUIRED", "m2": "REQUIRED"}
        states = {
            "m1": eb.condition_verdict(dict(self.ILLUM), {},
                                       {"moon_illumination_fraction": 0.9,
                                        "moon_altitude": -12.0})[0],
            "m2": eb.condition_verdict(dict(self.ELEV), {},
                                       {"moon_altitude": -12.0})[0],
        }
        self.assertEqual(states["m1"], "PASS")   # moon down -> no interference
        self.assertEqual(states["m2"], "FAIL")   # but no moon in the sky either
        self.assertEqual(eb.hour_status(roles, states)[0], "UNFAVORABLE")


class StarTrailsConditionTests(unittest.TestCase):
    MOON = {"metric": "moon_illumination_fraction", "operator": "lte", "threshold": 0.15}
    STREAK = {"metric": "clear_streak_hours", "operator": "gte", "threshold": 2.0}

    def test_new_moon_vs_full_moon(self):
        self.assertEqual(eb.condition_verdict(dict(self.MOON), {},
                                              {"moon_illumination_fraction": 0.05,
                                               "moon_altitude": 20.0})[0], "PASS")
        self.assertEqual(eb.condition_verdict(dict(self.MOON), {},
                                              {"moon_illumination_fraction": 0.95,
                                               "moon_altitude": 20.0})[0], "FAIL")
        # moon below the horizon: the gate passes outright (batch A)
        self.assertEqual(
            eb.condition_verdict(dict(self.MOON), {},
                                 {"moon_illumination_fraction": 0.95,
                                  "moon_altitude": -30.0}),
            ("PASS", "MOON_BELOW_HORIZON_PASS"))

    def test_streak_gate(self):
        self.assertEqual(eb.condition_verdict(dict(self.STREAK),
                                              {"clear_streak_hours": available(3.0)}, {})[0],
                         "PASS")
        self.assertEqual(eb.condition_verdict(dict(self.STREAK),
                                              {"clear_streak_hours": available(1.0)}, {})[0],
                         "FAIL")


class TemplateRegistryTests(unittest.TestCase):
    def test_five_new_templates_validate_and_are_defined(self):
        sys.path.insert(0, str(ROOT / "data/v2/tools"))
        import apply_template as at
        templates = {t["template_id"]: t for t in at.validate_registry()}
        for tid in ("alpenglow", "snow_scene", "firefly", "star_trails",
                    "moonlit_scene"):
            self.assertEqual(templates[tid]["status"], "defined", tid)
            self.assertTrue(templates[tid]["conditions"], tid)

    def test_new_metrics_in_vocabulary(self):
        import json
        vocab = json.loads((ROOT / "data/v2/templates/metric-vocabulary.json")
                           .read_text(encoding="utf-8"))
        for metric in ("alpenglow_window", "snowfall", "snow_depth",
                       "snow_cover_state", "clear_streak_hours",
                       "temperature_2m", "relative_humidity_2m"):
            self.assertIn(metric, vocab["metrics"], metric)

    def test_binding_strings_lint(self):
        sys.path.insert(0, str(ROOT / "data/v2/tools"))
        import apply_template as at
        for tid in ("alpenglow", "snow_scene", "firefly", "star_trails",
                    "moonlit_scene"):
            t = json.loads((ROOT / f"data/v2/templates/{tid}.json")
                           .read_text(encoding="utf-8"))
            for c in t["conditions"]:
                mb = c.get("binding")
                if mb is None:
                    # status=defined templates need a binding only when the
                    # metric has a real fetch binding (computed/observation
                    # kinds ride the derivation layer instead)
                    continue
                # template registry stores the structured object; lint the
                # serialized form exactly like apply_template.binding_lint
                segments = []
                for key, value in mb.items():
                    if key == "field":
                        continue
                    segments.append(f"{key}:{value}")
                # fields may be compound; keep the order dataset|field|role
                seg = (f"dataset:{mb['dataset']}|field:{mb['field']}"
                       f"|role:{mb['role']}")
                at.lint_binding_string(seg)


if __name__ == "__main__":
    unittest.main()
