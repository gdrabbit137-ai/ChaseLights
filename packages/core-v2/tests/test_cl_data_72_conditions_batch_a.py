"""CL-DATA-72 batch A (CHALLENGER-15 audit head 8f738fb47): the four fatal
condition fixes, offline.

- CL-COND-A8  seasonal_state bridged to data/v2/seasonal-calendar.json
              (current_season first, typical fallback, wrap-aware; no entry =
              honest UNKNOWN).
- CL-COND-A5  sunset T3 (cloud_cover_mid_and_high 20-70%) REQUIRED -> QUALITY
              in the template and all 98 sunset contracts — 167 fully-clear
              days must never again be vetoed by a bonus band.
- CL-COND-A3+A4  night_sky moon set: moon below the horizon passes the
              illumination gate outright; M2/M3/M5 are an ALTERNATION (not a
              flat AND); the moon_target_separation_deg 999 sentinel is
              fail-closed NOT_EVALUABLE, never a permanent PASS.
- CL-COND-A7  reflection water surface: derived three-level
              water_reflection_state (mirror / shootable / unfit) replaces the
              no-source death on 46 contracts; tide-decided shoreline
              subjects (tw-015/jp-078/tw-026/jp-051) keep water_surface_state
              and degrade to NOT_EVALUABLE honestly with a tide-table guide.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)

TIDAL_SPOTS = ("tw-015-P02", "jp-078-P01", "tw-026-P03", "jp-051-P01")


def available(value):
    return {"value": value, "state": "AVAILABLE"}


def hour_row(wind, precip, temp):
    return {"values": {
        "wind_speed_10m": available(wind),
        "precipitation": available(precip),
        "temperature_2m": available(temp),
    }}


class SeasonalBridgeTests(unittest.TestCase):
    """CL-COND-A8: seasonal_state is a computed calendar verdict."""

    def test_calendar_loads_and_binds_spots(self):
        cal = eb.load_seasonal_calendar()
        self.assertIn("tw-085-P03", cal)          # silvergrass (芒草)
        self.assertIn("jp-028-P02", cal)          # red_maple current season
        self.assertIn("tw-116-P01", cal)          # daylily_taimali
        entry = cal["tw-085-P03"][0]
        self.assertEqual(entry["plant_id"], "silvergrass")

    def test_current_season_takes_precedence_over_typical(self):
        # jp-028-P02 red_maple: typical 10-20~11-10 (closed on 11-15), sourced
        # current_season 2026-11-05~11-16 -> still OPEN. The live window wins.
        cal = eb.load_seasonal_calendar()
        verdict, detail = eb.seasonal_window_verdict(cal["jp-028-P02"],
                                                     date(2026, 11, 15))
        self.assertEqual(verdict, "PASS")
        self.assertIn("current_season", detail)
        self.assertEqual(eb.seasonal_window_verdict(cal["jp-028-P02"],
                                                    date(2026, 11, 20))[0],
                         "FAIL")

    def test_typical_window_fallback_and_wrap(self):
        cal = eb.load_seasonal_calendar()
        # silvergrass typical 10-01~12-15, no live window in January.
        self.assertEqual(
            eb.seasonal_window_verdict(cal["tw-085-P03"], date(2026, 12, 1))[0],
            "PASS")
        self.assertEqual(
            eb.seasonal_window_verdict(cal["tw-085-P03"], date(2026, 1, 10))[0],
            "FAIL")
        # bald_cypress 12-05~01-15 wraps across New Year (both sides open).
        self.assertEqual(
            eb.seasonal_window_verdict(cal["tw-083-P02"], date(2026, 12, 20))[0],
            "PASS")
        self.assertEqual(
            eb.seasonal_window_verdict(cal["tw-083-P02"], date(2027, 1, 10))[0],
            "PASS")
        self.assertEqual(
            eb.seasonal_window_verdict(cal["tw-083-P02"], date(2026, 12, 1))[0],
            "FAIL")

    def test_daylily_seasonal_window_open_and_closed(self):
        # tw-116-P01 (太麻里金針花, audit's 247-day all-NOT_EVALUABLE example):
        # typical 08-01~09-30 — open in September, closed in October.
        cal = eb.load_seasonal_calendar()
        self.assertEqual(
            eb.seasonal_window_verdict(cal["tw-116-P01"], date(2026, 9, 1))[0],
            "PASS")
        self.assertEqual(
            eb.seasonal_window_verdict(cal["tw-116-P01"], date(2026, 10, 1))[0],
            "FAIL")

    def test_condition_verdict_uses_bound_entries(self):
        cal = eb.load_seasonal_calendar()
        cond = {"metric": "seasonal_state", "operator": "eq",
                "threshold": "window_open",
                "seasonal_entries": cal["tw-116-P01"]}
        self.assertEqual(eb.condition_verdict(cond, {}, {}, month=9,
                                              local_date=date(2026, 9, 1))[0],
                         "PASS")
        self.assertEqual(eb.condition_verdict(cond, {}, {}, month=10,
                                              local_date=date(2026, 10, 1))[0],
                         "FAIL")

    def test_no_calendar_entry_stays_unknown(self):
        cond = {"metric": "seasonal_state", "operator": "eq",
                "threshold": "window_open", "seasonal_entries": []}
        verdict, detail = eb.condition_verdict(cond, {}, {},
                                               local_date=date(2026, 11, 15))
        self.assertEqual((verdict, detail),
                         ("UNKNOWN", "NO_SEASONAL_CALENDAR_ENTRY"))

    def test_unsourced_current_season_is_ignored(self):
        # fail-closed: a current_season without source_url + retrieved_at is
        # never trusted as a live window (calendar _meta rule).
        entries = [{"plant_id": "x", "typical_window": None,
                    "current_season": {"start": "2026-01-01",
                                       "end": "2026-12-31"}}]
        self.assertEqual(
            eb.seasonal_window_verdict(entries, date(2026, 6, 1))[0], "FAIL")

    def test_seasonal_fail_now_gates_as_unfavorable(self):
        # A window-closed day is an honest UNFAVORABLE, not a whole-genre
        # NOT_EVALUABLE: REQUIRED seasonal FAIL -> hour UNFAVORABLE.
        roles = {"s": "REQUIRED", "ok": "REQUIRED"}
        states = {"s": "FAIL", "ok": "PASS"}
        self.assertEqual(eb.hour_status(roles, states)[0], "UNFAVORABLE")


class SunsetT3QualityTests(unittest.TestCase):
    """CL-COND-A5: the 20-70% bonus band never vetoes."""

    def test_template_t3_is_quality(self):
        template = json.loads((ROOT / "data/v2/templates/sunset.json")
                              .read_text(encoding="utf-8"))
        t3 = [c for c in template["conditions"]
              if c["template_ref"] == "T3" and c["metric"] == "cloud_cover_mid_and_high"]
        self.assertEqual(len(t3), 1)
        self.assertEqual(t3[0]["role"], "QUALITY")
        self.assertEqual(t3[0]["condition_tier"], "MODIFIER")

    def test_all_sunset_contracts_are_quality(self):
        count = 0
        for path in (ROOT / "data/v2/opportunities").glob("*.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            contract = doc.get("condition_contract") or {}
            if contract.get("genre_template") != "sunset":
                continue
            for cond in contract.get("conditions", []):
                if cond["metric"] == "cloud_cover_mid_and_high":
                    count += 1
                    self.assertEqual(cond["role"], "QUALITY",
                                     path.name)
        self.assertEqual(count, 98)

    def test_quality_fail_never_gates(self):
        roles = {"cloud": "QUALITY", "win": "REQUIRED"}
        states = {"cloud": "FAIL", "win": "PASS"}
        status, _fails, _unknowns = eb.hour_status(roles, states)
        self.assertEqual(status, "GUIDANCE_SATISFIED")


class MoonAlternationTests(unittest.TestCase):
    """CL-COND-A3+A4: moon gates honour the horizon."""

    DOWN = {"moon_altitude": -20.0, "moon_illumination_fraction": 0.81,
            "moon_target_separation_deg": 999.0, "moon_illuminance_proxy": 0.0}
    UP_FAR = {"moon_altitude": 5.0, "moon_illumination_fraction": 0.20,
              "moon_target_separation_deg": 86.7, "moon_illuminance_proxy": 0.02}
    UP_CLOSE = {"moon_altitude": 30.0, "moon_illumination_fraction": 0.20,
                "moon_target_separation_deg": 12.0, "moon_illuminance_proxy": 0.10}

    B2 = {"metric": "moon_illumination_fraction", "operator": "lte",
          "threshold": 0.5}
    M2 = {"metric": "moon_altitude", "operator": "lt", "threshold": 0}
    M3 = {"metric": "moon_target_separation_deg", "operator": "gte",
          "threshold": 40}
    M5 = {"metric": "moon_illuminance_proxy", "operator": "lte",
          "threshold": 0.15}

    def test_b2_passes_when_moon_below_horizon(self):
        # A3: jp-021-P02 2026-11-19 02:00-05:00 — moon -18..-50 deg, proxy 0,
        # yet vetoed by 0.52-0.81 illumination. Below the horizon the gate
        # cannot veto.
        verdict, detail = eb.condition_verdict(dict(self.B2), {}, self.DOWN)
        self.assertEqual((verdict, detail), ("PASS", "MOON_BELOW_HORIZON_PASS"))

    def test_b2_still_gates_when_moon_is_up(self):
        verdict, _ = eb.condition_verdict(dict(self.B2), {}, self.UP_FAR)
        self.assertEqual(verdict, "PASS")  # 0.20 <= 0.5
        bright = dict(self.UP_FAR, moon_illumination_fraction=0.7)
        self.assertEqual(eb.condition_verdict(dict(self.B2), {}, bright)[0],
                         "FAIL")

    def test_sentinel_999_is_fail_closed(self):
        # C3 / batch-A item 3: the moon-down separation sentinel is never a
        # permanent PASS — when actually judged it degrades to UNKNOWN.
        verdict, detail = eb.condition_verdict(dict(self.M3), {}, self.DOWN)
        self.assertEqual((verdict, detail), (
            "UNKNOWN", "MOON_BELOW_HORIZON_SENTINEL_NOT_EVALUABLE"))

    def test_alternation_resolves_moon_up_far_case(self):
        # A4: moon up at 5 deg, separation 86.7 deg — the old flat AND vetoed
        # this hour even though the M3 fallback passed.
        conds = [dict(self.M2, id="m2"), dict(self.M3, id="m3"),
                 dict(self.M5, id="m5")]
        alternation = eb.moon_alternation(conds)
        self.assertIsNotNone(alternation)
        states = {c["id"]: eb.condition_verdict(c, {}, self.UP_FAR)[0]
                  for c in conds}
        self.assertEqual(states, {"m2": "FAIL", "m3": "PASS", "m5": "PASS"})
        eb.apply_moon_alternation(states, alternation)
        self.assertEqual(states, {"m2": "PASS", "m3": "PASS", "m5": "PASS"})

    def test_alternation_gates_moon_up_close_case(self):
        conds = [dict(self.M2, id="m2"), dict(self.M3, id="m3"),
                 dict(self.M5, id="m5")]
        alternation = eb.moon_alternation(conds)
        states = {c["id"]: eb.condition_verdict(c, {}, self.UP_CLOSE)[0]
                  for c in conds}
        eb.apply_moon_alternation(states, alternation)
        # M3 FAIL (12 deg from the core) still gates the hour.
        roles = {c["id"]: "REQUIRED" for c in conds}
        self.assertEqual(eb.hour_status(roles, states)[0], "UNFAVORABLE")

    def test_alternation_moon_down_stands_dependents_down(self):
        conds = [dict(self.M2, id="m2"), dict(self.M3, id="m3"),
                 dict(self.M5, id="m5")]
        alternation = eb.moon_alternation(conds)
        states = {c["id"]: eb.condition_verdict(c, {}, self.DOWN)[0]
                  for c in conds}
        # raw pass: m3 sentinel UNKNOWN; the alternation (moon down = the
        # constraint set is satisfied) stands it down before the role gate.
        self.assertEqual(states["m3"], "UNKNOWN")
        eb.apply_moon_alternation(states, alternation)
        self.assertEqual(states, {"m2": "PASS", "m3": "PASS", "m5": "PASS"})
        roles = {c["id"]: "REQUIRED" for c in conds}
        self.assertEqual(eb.hour_status(roles, states)[0],
                         "GUIDANCE_SATISFIED")

    def test_anchor_unknown_propagates(self):
        conds = [dict(self.M2, id="m2"), dict(self.M3, id="m3")]
        alternation = eb.moon_alternation(conds)
        states = {"m2": "UNKNOWN", "m3": "PASS"}
        eb.apply_moon_alternation(states, alternation)
        self.assertEqual(states, {"m2": "UNKNOWN", "m3": "UNKNOWN"})

    def test_night_sky_and_blue_tears_contracts_have_anchors(self):
        for path in (ROOT / "data/v2/opportunities").glob("*.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            contract = doc.get("condition_contract") or {}
            if contract.get("genre_template") not in ("night_sky", "blue_tears"):
                continue
            metrics = {c["metric"] for c in contract.get("conditions", [])}
            if "moon_target_separation_deg" in metrics:
                self.assertIn("moon_altitude", metrics, path.name)


class WaterReflectionTests(unittest.TestCase):
    """CL-COND-A7: derived three-level water surface state."""

    WRS = {"metric": "water_reflection_state", "operator": "none",
           "threshold": None}

    def test_three_state_switching_on_wind(self):
        # The owner verification case: one lake, wind swings -> the three
        # levels switch (mirror / shootable / unfit).
        hours = [hour_row(3.5, 0.0, 20.0),      # unfit (wind)
                 hour_row(2.0, 0.0, 20.0),      # shootable (wind 1.5<w<=3)
                 hour_row(1.0, 0.0, 20.0),      # mirror (2h calm+dry history)
                 hour_row(1.0, 0.0, 20.0),      # mirror
                 hour_row(1.0, 0.0, 20.0),      # mirror
                 hour_row(1.0, 0.0, -2.0),      # unfit (icing, 可能結冰)
                 hour_row(2.5, 0.1, 20.0),      # shootable (near-no-rain)
                 hour_row(2.5, 0.5, 20.0)]      # unfit (raining)
        levels = [cell["value"] for cell in eb.water_reflection_levels(hours)]
        self.assertEqual(levels, ["unfit", "shootable", "mirror", "mirror",
                                  "mirror", "unfit", "shootable", "unfit"])

    def test_missing_cells_fail_closed(self):
        hours = [{"values": {"wind_speed_10m": available(1.0),
                             "precipitation": {"state": "UNAVAILABLE"}}}]
        cells = eb.water_reflection_levels(hours)
        self.assertEqual(cells[0]["state"], "UNKNOWN")
        verdict, detail = eb.condition_verdict(dict(self.WRS), {}, {})
        self.assertEqual((verdict, detail), (
            "UNKNOWN", "REFLECTION_STATE_DERIVATION_UNAVAILABLE"))

    def test_condition_verdict_neq_unfit(self):
        self.assertEqual(
            eb.condition_verdict(dict(self.WRS),
                                 {"water_reflection_state": available("mirror")}, {})[0],
            "PASS")
        self.assertEqual(
            eb.condition_verdict(dict(self.WRS),
                                 {"water_reflection_state": available("shootable")}, {})[0],
            "PASS")
        self.assertEqual(
            eb.condition_verdict(dict(self.WRS),
                                 {"water_reflection_state": available("unfit")}, {})[0],
            "FAIL")

    def test_46_contracts_use_derived_metric_and_4_tidal_kept(self):
        derived = 0
        for path in (ROOT / "data/v2/opportunities").glob("*.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            oid = doc["opportunity_id"]
            contract = doc.get("condition_contract") or {}
            if contract.get("genre_template") != "reflection":
                continue
            conds = [c for c in contract.get("conditions", [])
                     if c["metric"] in ("water_surface_state",
                                        "water_reflection_state")]
            self.assertEqual(len(conds), 1, path.name)
            cond = conds[0]
            if oid in TIDAL_SPOTS:
                # tide-decided subjects: no-source metric kept REQUIRED with
                # the tide-table shooting guide.
                self.assertEqual(cond["metric"], "water_surface_state", oid)
                self.assertEqual(cond["role"], "REQUIRED", oid)
                self.assertIn("潮汐表",
                              (cond.get("notes_i18n") or {}).get("zh-TW", ""), oid)
                verdict, detail = eb.condition_verdict(dict(cond), {}, {})
                self.assertEqual((verdict, detail), (
                    "UNKNOWN", "NO_LIVE_OBSERVATION_SOURCE"))
            else:
                self.assertEqual(cond["metric"], "water_reflection_state", oid)
                self.assertEqual((cond["operator"], cond["threshold"]),
                                 ("none", None), oid)
                derived += 1
        self.assertEqual(derived, 46)

    def test_reflection_template_uses_derived_metric(self):
        template = json.loads((ROOT / "data/v2/templates/reflection.json")
                              .read_text(encoding="utf-8"))
        t2 = [c for c in template["conditions"]
              if c["template_ref"] == "T2"]
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2[0]["metric"], "water_reflection_state")
        self.assertEqual((t2[0]["operator"], t2[0]["threshold"]),
                         ("none", None))

    def test_vocabulary_covers_water_reflection_state(self):
        vocab = json.loads((ROOT / "data/v2/templates/metric-vocabulary.json")
                           .read_text(encoding="utf-8"))
        self.assertIn("water_reflection_state", vocab["metrics"])

    def test_seasonal_state_leaves_no_source_set(self):
        self.assertNotIn("seasonal_state", eb.NO_SOURCE_METRICS)
        self.assertIn("water_surface_state", eb.NO_SOURCE_METRICS)


class FlowerSeasonIntegrationTests(unittest.TestCase):
    """The CHALLENGER-15 A8 驗證 case: a flower-season subject gets satisfied
    days again — a window-open hour with all-weather PASS is GUIDANCE_SATISFIED
    (before the fix the same hour was NOT_EVALUABLE on the calendar UNKNOWN)."""

    def test_window_open_hour_is_satisfiable(self):
        cal = eb.load_seasonal_calendar()
        cond = {"id": "season", "metric": "seasonal_state", "operator": "eq",
                "threshold": "window_open", "role": "REQUIRED",
                "seasonal_entries": cal["tw-085-P03"]}
        weather = {"id": "rain", "metric": "precipitation", "operator": "lt",
                   "threshold": 0.2, "role": "REQUIRED"}
        # 2026-11-16 inside silvergrass current_season 2026-11-14~12-13.
        states = {
            "season": eb.condition_verdict(cond, {}, {},
                                           local_date=date(2026, 11, 16))[0],
            "rain": eb.condition_verdict(weather,
                                         {"precipitation": available(0.0)}, {})[0],
        }
        roles = {k: "REQUIRED" for k in states}
        status, _fails, _unknowns = eb.hour_status(roles, states)
        self.assertEqual(status, "GUIDANCE_SATISFIED")

    def test_display_value_round_trip(self):
        cal = eb.load_seasonal_calendar()
        cond = {"metric": "seasonal_state", "operator": "eq",
                "threshold": "window_open",
                "seasonal_entries": cal["tw-085-P03"]}
        self.assertEqual(
            eb.condition_value(cond, {}, {}, local_date=date(2026, 11, 16)),
            "window_open")
        self.assertEqual(
            eb.condition_value(cond, {}, {}, local_date=date(2026, 1, 10)),
            "window_closed")


if __name__ == "__main__":
    unittest.main()
