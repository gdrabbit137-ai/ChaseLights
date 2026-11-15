"""CL-DATA-73: misty_forest template + fog_state inversion tests (offline).

Covers the owner verification cases (霧日 ✓ / 晴天 10 km ✗「無霧」/ 晨窗外 →
時段語義), the fog_state ANY-branch derivation, soft-light / morning-window
geometry, the seasonal-window gate, the mounted contracts, and the copy-layer
sync (fail words / genre short name / overrides).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)

sys.path.insert(0, str(ROOT / "packages/models-v2"))
import astro_hourly  # noqa: E402

sys.path.insert(0, str(ROOT / "data/v2/tools"))
import apply_template as at  # noqa: E402

MOUNTED = [
    "tw-024-P07", "tw-032-P04", "tw-053-P03", "tw-088-P03", "tw-089-P02",
    "tw-091-P03", "tw-104-P02", "tw-120-P03", "tw-140-P04", "tw-151-P03",
    "tw-173-P03", "tw-177-P02",
]

TEMPLATE = json.loads((ROOT / "data/v2/templates/misty_forest.json")
                      .read_text(encoding="utf-8"))
VOCAB = json.loads((ROOT / "data/v2/templates/metric-vocabulary.json")
                   .read_text(encoding="utf-8"))
GENRE_SHORT = json.loads((ROOT / "data/v2/copy/genre_short_names.json")
                         .read_text(encoding="utf-8"))
FAIL_SHORT = json.loads((ROOT / "data/v2/copy/fail_reason_short.json")
                        .read_text(encoding="utf-8"))


def cell(value):
    return {"value": value, "state": "AVAILABLE"}


def fog_condition():
    return {"metric": "fog_state", "operator": "none", "role": "REQUIRED"}


def with_fog_cell(values):
    """Mimic the batch runner: derive the fog_state cell onto the hour row."""
    row = {"values": dict(values)}
    row["values"]["fog_state"] = eb.fog_states([row])[0]
    return row["values"]


def hour_values(vis=None, rh=None, temp=None, dew=None, wind=None, precip=None):
    values = {}
    if vis is not None:
        values["visibility"] = cell(vis)
    if rh is not None:
        values["relative_humidity_2m"] = cell(rh)
    if temp is not None:
        values["temperature_2m"] = cell(temp)
    if dew is not None:
        values["dew_point_2m"] = cell(dew)
    if wind is not None:
        values["wind_speed_10m"] = cell(wind)
    if precip is not None:
        values["precipitation"] = cell(precip)
    return values


def cell_row(values):
    return {"values": values}


class TemplateRegistryTests(unittest.TestCase):
    def test_template_is_defined_and_validates(self):
        statuses = {t["template_id"]: t["status"] for t in at.validate_registry()}
        self.assertEqual(statuses["misty_forest"], "defined")

    def test_title_trilingual_owner_spec(self):
        self.assertEqual(TEMPLATE["title_i18n"]["zh-TW"], "迷霧森林")
        self.assertEqual(TEMPLATE["title_i18n"]["en"], "Misty Forest")
        self.assertEqual(TEMPLATE["title_i18n"]["ja"], "霧の森")

    def test_conditions_match_the_owner_spec(self):
        conds = {c["metric"]: c for c in TEMPLATE["conditions"]}
        self.assertEqual(set(conds), {
            "fog_state", "soft_light_window", "morning_window",
            "precipitation", "wind_speed_10m", "seasonal_state"})
        # decisive condition: REQUIRED MAIN, operator none (derived cell)
        fog = conds["fog_state"]
        self.assertEqual((fog["role"], fog["condition_tier"], fog["operator"],
                          fog["threshold_source"]),
                         ("REQUIRED", "MAIN", "none", "computed"))
        # rain and wind REQUIRED with the owner thresholds
        self.assertEqual(conds["precipitation"]["operator"], "lt")
        self.assertEqual(conds["precipitation"]["threshold"], 0.2)
        self.assertEqual(conds["wind_speed_10m"]["operator"], "lte")
        self.assertEqual(conds["wind_speed_10m"]["threshold"], 3.0)
        self.assertEqual(conds["wind_speed_10m"]["role"], "REQUIRED")
        # soft light REQUIRED, morning window advisory (PRIORITY)
        self.assertEqual((conds["soft_light_window"]["role"],
                          conds["soft_light_window"]["condition_tier"]),
                         ("REQUIRED", "MAIN"))
        self.assertEqual((conds["morning_window"]["role"],
                          conds["morning_window"]["condition_tier"]),
                         ("QUALITY", "MODIFIER"))
        # seasonal gate rides the calendar engine
        self.assertEqual((conds["seasonal_state"]["metric"],
                          conds["seasonal_state"]["operator"],
                          conds["seasonal_state"]["threshold"],
                          conds["seasonal_state"]["domain"]),
                         ("seasonal_state", "eq", "window_open", "SEASON_TIME"))

    def test_all_template_metrics_in_vocabulary(self):
        for c in TEMPLATE["conditions"]:
            self.assertIn(c["metric"], VOCAB["metrics"], c["template_ref"])


class FogStateDerivationTests(unittest.TestCase):
    def _state(self, **kw):
        levels = eb.fog_states([cell_row(hour_values(**kw))])
        return levels[0]

    def test_fog_day_vis_in_band_passes_owner_case_1(self):
        # owner case 1: 霧日（能見度 <500 m 時段）✓ — fog happening branch
        lvl = self._state(vis=0.3)
        self.assertEqual(lvl, {"state": "AVAILABLE", "value": "fog"})
        verdict, detail = eb.condition_verdict(fog_condition(),
                                               with_fog_cell(hour_values(vis=0.3)), {})
        self.assertEqual((verdict, detail), ("PASS", "FOG_STATE(fog)"))

    def test_forming_branch_passes_owner_any_semantics(self):
        # branch 2 of the owner ANY: vis outside the band but RH>=95 + spread<1
        lvl = self._state(vis=0.8, rh=96.0, temp=12.0, dew=11.6)
        self.assertEqual(lvl["value"], "forming")
        verdict, detail = eb.condition_verdict(
            fog_condition(),
            with_fog_cell(hour_values(vis=0.8, rh=96.0, temp=12.0, dew=11.6)), {})
        self.assertEqual((verdict, detail), ("PASS", "FOG_STATE(forming)"))

    def test_clear_day_10km_is_explicit_no_fog_owner_case_2(self):
        # owner case 2: 晴天日能見度 10 km → ✗「無霧」
        lvl = self._state(vis=10.0)
        self.assertEqual(lvl["value"], "no_fog")
        verdict, detail = eb.condition_verdict(fog_condition(),
                                               with_fog_cell(hour_values(vis=10.0)), {})
        self.assertEqual((verdict, detail), ("FAIL", "FOG_STATE(no_fog)"))
        # REQUIRED fail -> hour UNFAVORABLE, and the fail word is 無霧
        status, _, _ = eb.hour_status({"C1": "REQUIRED"},
                                      {"C1": verdict})
        self.assertEqual(status, "UNFAVORABLE")
        self.assertEqual(FAIL_SHORT["words"]["fog_state"]["zh-TW"], "無霧")

    def test_below_one_km_without_branches_is_not_forming(self):
        lvl = self._state(vis=0.8, rh=80.0, temp=12.0, dew=8.0)
        self.assertEqual(lvl["value"], "not_forming")
        verdict, _ = eb.condition_verdict(
            fog_condition(),
            with_fog_cell(hour_values(vis=0.8, rh=80.0, temp=12.0, dew=8.0)), {})
        self.assertEqual(verdict, "FAIL")

    def test_missing_visibility_fails_closed_unknown(self):
        lvl = self._state(rh=98.0, temp=10.0, dew=9.8)
        self.assertEqual(lvl, {"state": "UNKNOWN", "value": None})
        verdict, detail = eb.condition_verdict(fog_condition(), {}, {})
        self.assertEqual((verdict, detail),
                         ("UNKNOWN", "FOG_STATE_DERIVATION_UNAVAILABLE"))
        status, _, _ = eb.hour_status({"C1": "REQUIRED"}, {"C1": verdict})
        self.assertEqual(status, "NOT_EVALUABLE")

    def test_malformed_operator_degrades_to_unknown(self):
        verdict, detail = eb.condition_verdict(
            {"metric": "fog_state", "operator": "lt", "threshold": 1},
            with_fog_cell(hour_values(vis=0.3)), {})
        self.assertEqual((verdict, detail),
                         ("UNKNOWN", "UNSUPPORTED_FOG_STATE_OPERATOR"))

    def test_band_edges(self):
        self.assertEqual(self._state(vis=0.05)["value"], "fog")
        self.assertEqual(self._state(vis=0.5)["value"], "fog")
        self.assertEqual(self._state(vis=0.049)["value"], "not_forming")
        self.assertEqual(self._state(vis=1.0)["value"], "not_forming")
        self.assertEqual(self._state(vis=1.001)["value"], "no_fog")


class LightWindowTests(unittest.TestCase):
    LAT, LON = 23.632, 120.792

    def _hour(self, y, mo, d, h):
        return datetime(y, mo, d, h, 0, tzinfo=timezone.utc) - timedelta(hours=8)

    def test_night_never_qualifies_soft_light(self):
        # 12:00 local midday AND 23:00 local night both fail soft light
        mid = self._hour(2026, 1, 15, 12)
        night = self._hour(2026, 1, 15, 15)  # 23:00 local
        self.assertIs(astro_hourly.hour_observations(mid, self.LAT, self.LON)["soft_light_window"], False)
        self.assertIs(astro_hourly.hour_observations(night, self.LAT, self.LON)["soft_light_window"], False)
        # owner rule: 夜間不成立（看不見樹）— REQUIRED soft-light fail gates the hour
        verdict, _ = eb.condition_verdict({"metric": "soft_light_window",
                                           "operator": "none"}, {}, {})
        self.assertEqual(verdict, "UNKNOWN")
        astro_obs = astro_hourly.hour_observations(night, self.LAT, self.LON)
        verdict_night, _ = eb.condition_verdict(
            {"metric": "soft_light_window", "operator": "none"}, {},
            astro_obs)
        self.assertEqual(verdict_night, "FAIL")

    def test_dawn_slant_hour_qualifies_soft_light(self):
        # 2026-01-15 07:00 local bucket: whole bucket in civil light, slant
        # samples <= 10 deg present (empirically pinned via window_pass_profiles)
        dt = self._hour(2026, 1, 15, 7)
        obs = astro_hourly.hour_observations(dt, self.LAT, self.LON)
        self.assertIs(obs["soft_light_window"], True)
        # and the Nov deep-fog-season bucket 06:00 local qualifies too
        dt_nov = self._hour(2026, 11, 16, 6)
        obs_nov = astro_hourly.hour_observations(dt_nov, self.LAT, self.LON)
        self.assertIs(obs_nov["soft_light_window"], True)

    def test_morning_window_1_to_3h_after_sunrise(self):
        # 2026-11-16: sunrise ~05:55 local (= UTC 2026-11-15 21:55). The
        # 06:00 local bucket holds no sample a full 1 h past sunrise (band
        # opens ~06:55 local); local 07/08/09 buckets qualify; local 10:00
        # (UTC 02:00 on the 16th) does not.
        def morning(utc_y, utc_mo, utc_d, utc_h):
            return astro_hourly.hour_observations(
                datetime(utc_y, utc_mo, utc_d, utc_h, 0, tzinfo=timezone.utc),
                self.LAT, self.LON)["morning_window"]
        self.assertIs(morning(2026, 11, 15, 22), False)  # 06:00 local
        self.assertIs(morning(2026, 11, 15, 23), True)   # 07:00 local
        self.assertIs(morning(2026, 11, 16, 0), True)    # 08:00 local
        self.assertIs(morning(2026, 11, 16, 1), True)    # 09:00 local
        self.assertIs(morning(2026, 11, 16, 2), False)   # 10:00 local

    def test_morning_window_is_quality_never_a_lone_veto(self):
        # owner case 3: 晨窗外 → 時段語義 (advisory; hour still decided by fog)
        status, _, _ = eb.hour_status(
            {"F1": "REQUIRED", "M1": "QUALITY"},
            {"F1": "PASS", "M1": "FAIL"})
        self.assertEqual(status, "GUIDANCE_SATISFIED")
        # the time-slot semantics live in the QUALITY row + fail word
        self.assertEqual(FAIL_SHORT["words"]["morning_window"]["zh-TW"],
                         "非晨窗時段")
        self.assertIn("morning_window", FAIL_SHORT["metric_priority"])


class SeasonalGateTests(unittest.TestCase):
    ENTRY = {
        "plant_id": "misty_forest",
        "typical_window": {"start": "12-01", "end": "04-30"},
    }

    def _verdict(self, date):
        import datetime as _dt
        return eb.seasonal_window_verdict([self.ENTRY], _dt.date.fromisoformat(date))

    def test_inside_window_passes(self):
        verdict, detail = self._verdict("2026-01-15")
        self.assertEqual(verdict, "PASS")
        self.assertIn("typical", detail)
        self.assertIn("misty_forest", detail)

    def test_outside_window_fails(self):
        verdict, _ = self._verdict("2026-07-15")
        self.assertEqual(verdict, "FAIL")

    def test_no_entry_resolves_fail_not_fabricated_open(self):
        # with no calendar entry the window cannot be shown open; the
        # DATA-72 engine degrades to window_closed (FAIL), never a fake PASS
        import datetime as _dt
        verdict, detail = eb.seasonal_window_verdict(
            [], _dt.date.fromisoformat("2026-01-15"))
        self.assertEqual(verdict, "FAIL")
        self.assertIn("SEASONAL_WINDOW_CLOSED", detail)

    def test_calendar_entry_covers_all_mounted_spots(self):
        cal = json.loads((ROOT / "data/v2/seasonal-calendar.json")
                         .read_text(encoding="utf-8"))
        entry = next(e for e in cal["entries"] if e["plant_id"] == "misty_forest")
        self.assertEqual(set(entry["spots"]), set(MOUNTED))
        self.assertEqual(entry["typical_window"],
                         {"start": "12-01", "end": "04-30"})
        self.assertTrue(entry["sources"])


class MountedContractTests(unittest.TestCase):
    def test_all_12_mounted_contracts_exist_and_validate(self):
        from jsonschema import Draft202012Validator
        schema = json.loads((ROOT / "specs/v2/schema/opportunity-v2.1.schema.json")
                            .read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        for oid in MOUNTED:
            with self.subTest(oid=oid):
                doc = json.loads((ROOT / f"data/v2/opportunities/{oid}.json")
                                 .read_text(encoding="utf-8"))
                self.assertEqual(doc["condition_contract"]["genre_template"],
                                 "misty_forest")
                metrics = [c["metric"]
                           for c in doc["condition_contract"]["conditions"]]
                self.assertEqual(metrics, [
                    "fog_state", "soft_light_window", "morning_window",
                    "precipitation", "wind_speed_10m", "seasonal_state"])
                self.assertFalse(list(validator.iter_errors(doc)))

    def test_mounted_places_are_the_ticket_candidates(self):
        place_ids = {oid.rsplit("-P", 1)[0] for oid in MOUNTED}
        self.assertEqual(place_ids, {
            "tw-024", "tw-032", "tw-053", "tw-088", "tw-089", "tw-091",
            "tw-104", "tw-120", "tw-140", "tw-151", "tw-173", "tw-177"})


class CopyLayerTests(unittest.TestCase):
    def test_genre_short_name_leq6_trilingual(self):
        entry = GENRE_SHORT["genres"]["misty_forest"]
        self.assertEqual(entry["zh-TW"], "迷霧森林")
        self.assertLessEqual(len(entry["zh-TW"]), 6)
        self.assertEqual(entry["en"], "Misty Forest")
        self.assertEqual(entry["ja"], "霧の森")

    def test_fail_words_registered(self):
        words = FAIL_SHORT["words"]
        self.assertEqual(words["fog_state"]["zh-TW"], "無霧")
        self.assertEqual(words["soft_light_window"]["zh-TW"], "非柔光時段")
        self.assertEqual(words["morning_window"]["zh-TW"], "非晨窗時段")
        for m in ("fog_state", "soft_light_window", "morning_window"):
            self.assertIn(m, FAIL_SHORT["metric_priority"])
            self.assertNotIn(m, ("", None))
        self.assertEqual(len(set(FAIL_SHORT["metric_priority"])),
                         len(FAIL_SHORT["metric_priority"]))

    def test_overrides_carry_misty_forest_copy(self):
        ovr = json.loads((ROOT / "data/v2/copy/fail_reason_overrides.json")
                         .read_text(encoding="utf-8"))
        per = ovr.get("tw-053-P03") or {}
        for m in ("fog_state", "precipitation", "wind_speed_10m",
                  "soft_light_window", "morning_window", "seasonal_state"):
            entry = per.get(m)
            self.assertIsNotNone(entry, m)
            for lang in ("zh-TW", "en", "ja"):
                self.assertTrue(entry.get(lang), f"{m}/{lang}")
        self.assertIn("無霧", per["fog_state"]["zh-TW"])


class EvaluatorCompositionTests(unittest.TestCase):
    """The whole hour composition on the real mounted contract."""

    def test_foggy_morning_hour_is_guidance_satisfied(self):
        oid = "tw-053-P03"
        doc = json.loads((ROOT / f"data/v2/opportunities/{oid}.json")
                         .read_text(encoding="utf-8"))
        conds = doc["condition_contract"]["conditions"]
        roles = {c["id"]: c["role"] for c in conds}
        values = with_fog_cell(hour_values(vis=0.3, wind=1.0, precip=0.0))
        verdicts = {}
        for c in conds:
            if c["metric"] in ("fog_state", "precipitation", "wind_speed_10m"):
                v, _ = eb.condition_verdict(c, values, {})
                verdicts[c["id"]] = v
            else:
                verdicts[c["id"]] = "PASS"  # astro/seasonal assumed fine here
        status, _, _ = eb.hour_status(roles, verdicts)
        self.assertEqual(status, "GUIDANCE_SATISFIED")

    def test_clear_day_hour_is_unfavorable_via_fog_required(self):
        oid = "tw-053-P03"
        doc = json.loads((ROOT / f"data/v2/opportunities/{oid}.json")
                         .read_text(encoding="utf-8"))
        conds = doc["condition_contract"]["conditions"]
        roles = {c["id"]: c["role"] for c in conds}
        values = with_fog_cell(hour_values(vis=10.0, wind=1.0, precip=0.0))
        verdicts = {}
        for c in conds:
            if c["metric"] in ("fog_state", "precipitation", "wind_speed_10m"):
                v, _ = eb.condition_verdict(c, values, {})
                verdicts[c["id"]] = v
            else:
                verdicts[c["id"]] = "PASS"
        status, fails, _ = eb.hour_status(roles, verdicts)
        self.assertEqual(status, "UNFAVORABLE")
        fog_id = next(c["id"] for c in conds if c["metric"] == "fog_state")
        self.assertIn(fog_id, fails)


if __name__ == "__main__":
    unittest.main()
