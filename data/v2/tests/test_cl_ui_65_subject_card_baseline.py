"""CL-UI-65: dominant-reason gap fix + general-v0.1 baseline full catalog.

Covers: NOT_EVALUABLE is not an evaluated failure (mixed rows keep the
evaluated verdict; all-NOT_EVALUABLE rows fall back to the general baseline
reason); the PARTIAL-condition fallback gives an UNFAVORABLE day a reason;
general baseline computation from hourly weather (visibility/precip/humidity/
daylight, view scale 8/5/3, UNKNOWN fail-closed); the tw-005 (大稻埕碼頭)
regression row; no general contract is mounted into opportunities/.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVAL_DIR = ROOT / "data/v2/evaluations"

import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "data/v2/tools"))

import build_subject_cards as bsc  # noqa: E402


def _words():
    return json.loads((ROOT / "data/v2/copy/fail_reason_short.json").read_bytes().decode("utf-8"))


PRIORITY = {m: i for i, m in enumerate(_words()["metric_priority"])}
WORDS = _words()["words"]


def _hour(vis=24.1, precip=0.0, rh=60, sun=30):
    return {"visibility": vis, "precipitation": precip, "rh": rh, "sun_elevation": sun}


class GeneralBaselineTests(unittest.TestCase):
    def test_clear_day_is_ok(self):
        self.assertEqual(bsc.general_day_baseline([_hour()] * 24, 8, PRIORITY, WORDS),
                         {"ok": True, "reason_short": None})

    def test_rain_day_votes_precipitation(self):
        base = bsc.general_day_baseline([_hour(precip=3.0)] * 10, 8, PRIORITY, WORDS)
        self.assertFalse(base["ok"])
        self.assertEqual(base["reason_short"], WORDS["precipitation"])

    def test_fog_day_votes_visibility(self):
        base = bsc.general_day_baseline([_hour(vis=1.0)] * 10, 8, PRIORITY, WORDS)
        self.assertEqual(base["reason_short"], WORDS["visibility"])

    def test_humidity_violation(self):
        base = bsc.general_day_baseline([_hour(rh=98)] * 10, 8, PRIORITY, WORDS)
        self.assertEqual(base["reason_short"], WORDS["relative_humidity_925hpa"])

    def test_night_only_day_is_never_ok(self):
        base = bsc.general_day_baseline([_hour(sun=-20)] * 24, 8, PRIORITY, WORDS)
        self.assertFalse(base["ok"])
        self.assertEqual(base["reason_short"], WORDS["light_window"])

    def test_one_good_hour_makes_the_day_ok(self):
        hours = [_hour(sun=-20)] * 20 + [_hour()]
        self.assertTrue(bsc.general_day_baseline(hours, 8, PRIORITY, WORDS)["ok"])

    def test_view_scale_thresholds(self):
        self.assertEqual(bsc.general_day_baseline([_hour(vis=7.9)] * 24, 8, PRIORITY, WORDS)["ok"], False)
        self.assertEqual(bsc.general_day_baseline([_hour(vis=8.0)] * 24, 8, PRIORITY, WORDS)["ok"], True)
        self.assertEqual(bsc.general_day_baseline([_hour(vis=4.0)] * 24, 5, PRIORITY, WORDS)["ok"], False)
        self.assertEqual(bsc.general_day_baseline([_hour(vis=4.0)] * 24, 3, PRIORITY, WORDS)["ok"], True)

    def test_unknown_hours_fail_closed_without_fabricating_reason(self):
        base = bsc.general_day_baseline([{}], 5, PRIORITY, WORDS)
        self.assertFalse(base["ok"])
        self.assertIsNone(base["reason_short"])

    def test_view_scale_from_genre_mix(self):
        self.assertEqual(bsc.general_view_scale(["overlook"]), 8)
        self.assertEqual(bsc.general_view_scale(["night_sky"]), 8)
        self.assertEqual(bsc.general_view_scale(["waterfall"]), 3)
        self.assertEqual(bsc.general_view_scale(["tidal"]), 3)
        self.assertEqual(bsc.general_view_scale(["sunset"]), 5)
        self.assertEqual(bsc.general_view_scale([]), 5)
        # vista beats near when both are present (mount-tool precedence)
        self.assertEqual(bsc.general_view_scale(["waterfall", "overlook"]), 8)


class TierTests(unittest.TestCase):
    """CL-UI-65 owner ruling: three-tier display semantics in the derived rows."""

    @classmethod
    def setUpClass(cls):
        cls.genres, cls.fails = bsc.load_copy()

    def _derive(self, place, weather):
        real_load = bsc.load_place_hourly_weather
        bsc.load_place_hourly_weather = lambda pid: weather
        try:
            out, _ = bsc.derive_place_days(
                {"places": [place], "_source_path": "x", "_source_sha256": "0"},
                self.genres, self.fails)
        finally:
            bsc.load_place_hourly_weather = real_load
        return out["places"]["xx-000"]

    def test_curated_pass_is_recommend_even_when_general_disagrees(self):
        weather = {"2026-01-01": [_hour(precip=5.0)] * 24}
        days = [("sunset", [{"local_date": "2026-01-01", "state": "GUIDANCE_SATISFIED",
                             "good_hours": ["17:00"], "conditions": []}])]
        row = self._derive(_place(days), weather)["2026-01-01"]
        self.assertEqual(row["tier"], "recommend")
        self.assertEqual(row["status"], "clear")

    def test_curated_all_fail_general_ok_is_shootable(self):
        weather = {"2026-01-01": [_hour()] * 24}
        days = [("sunset", [{"local_date": "2026-01-01", "state": "UNFAVORABLE",
                             "good_hours": [],
                             "conditions": [{"metric": "golden_hour_window", "tier": "MAIN",
                                             "role": "REQUIRED", "day_verdict": "PARTIAL",
                                             "pass_hours": 2}]}])]
        row = self._derive(_place(days), weather)["2026-01-01"]
        self.assertEqual(row["tier"], "shootable")
        self.assertEqual(row["status"], "failed")

    def test_general_fail_is_not_recommended_with_reason(self):
        weather = {"2026-01-01": [_hour(precip=5.0)] * 24}
        days = [("sunset", [{"local_date": "2026-01-01", "state": "UNFAVORABLE",
                             "good_hours": [], "conditions": []}])]
        row = self._derive(_place(days), weather)["2026-01-01"]
        self.assertEqual(row["tier"], "not_recommended")
        self.assertEqual(row["general_baseline"]["reason_short"], WORDS["precipitation"])

    def test_no_weather_is_honest_null_tier(self):
        days = [("sunset", [{"local_date": "2026-01-01", "state": "UNFAVORABLE",
                             "good_hours": [], "conditions": []}])]
        row = self._derive(_place(days), {})["2026-01-01"]
        self.assertIsNone(row["tier"])
        self.assertFalse(row["general_baseline"]["ok"])

    def test_not_evaluable_with_general_ok_is_shootable(self):
        weather = {"2026-01-01": [_hour()] * 24}
        days = [("noctiluca", [{"local_date": "2026-01-01", "state": "NOT_EVALUABLE",
                                "good_hours": [], "conditions": []}])]
        row = self._derive(_place(days), weather)["2026-01-01"]
        self.assertEqual(row["tier"], "shootable")
        self.assertEqual(row["status"], "not_evaluable")


def _place(opp_days):
    """opp_days: list of (genre, [day dicts]) → a minimal bundle place."""
    return {"place_id": "xx-000", "name_i18n": {"zh-TW": "x"},
            "opportunities": [
                {"opportunity_id": "xx-000-P01", "genre_template": g, "days": days}
                for g, days in opp_days]}


class NotEvaluableSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.genres, cls.fails = bsc.load_copy()

    def _derive(self, place):
        out, _ = bsc.derive_place_days({"places": [place], "_source_path": "x",
                                        "_source_sha256": "0"}, self.genres, self.fails)
        return out["places"]["xx-000"]

    def test_mixed_not_evaluable_keeps_evaluated_verdict(self):
        # one NOT_EVALUABLE subject + one UNFAVORABLE subject with a FAIL condition
        days = [("sunset", [{"local_date": "2026-01-01", "state": "NOT_EVALUABLE",
                             "good_hours": [], "conditions": []}]),
                ("sunset", [{"local_date": "2026-01-01", "state": "UNFAVORABLE",
                             "good_hours": [],
                             "conditions": [{"metric": "precipitation", "tier": "MAIN",
                                             "role": "REQUIRED", "day_verdict": "FAIL",
                                             "pass_hours": 0}]}])]
        rows = self._derive(_place(days))
        row = rows["2026-01-01"]
        self.assertEqual(row["status"], "failed")
        self.assertEqual(row["dominant_source"], "curated_votes")
        self.assertEqual(row["dominant_metric"], "precipitation")

    def test_all_not_evaluable_falls_back_to_general_reason(self):
        # weather: raining all day → general baseline not ok, reason 雨
        real_load = bsc.load_place_hourly_weather
        bsc.load_place_hourly_weather = lambda pid: {
            "2026-01-01": [_hour(precip=5.0)] * 24}
        try:
            days = [("noctiluca", [{"local_date": "2026-01-01", "state": "NOT_EVALUABLE",
                                    "good_hours": [], "conditions": []}])]
            row = self._derive(_place(days))["2026-01-01"]
        finally:
            bsc.load_place_hourly_weather = real_load
        self.assertEqual(row["status"], "not_evaluable")
        self.assertEqual(row["dominant_source"], "general_baseline")
        self.assertEqual(row["dominant_reason"], WORDS["precipitation"])
        self.assertFalse(row["general_baseline"]["ok"])

    def test_all_not_evaluable_general_ok_keeps_honest_null(self):
        real_load = bsc.load_place_hourly_weather
        bsc.load_place_hourly_weather = lambda pid: {
            "2026-01-01": [_hour()] * 24}
        try:
            days = [("noctiluca", [{"local_date": "2026-01-01", "state": "NOT_EVALUABLE",
                                    "good_hours": [], "conditions": []}])]
            row = self._derive(_place(days))["2026-01-01"]
        finally:
            bsc.load_place_hourly_weather = real_load
        self.assertEqual(row["status"], "not_evaluable")
        self.assertIsNone(row["dominant_reason"])
        self.assertTrue(row["general_baseline"]["ok"])

    def test_unfavorable_partial_only_day_gets_a_reason(self):
        """CL-UI-65 regression: tw-005-style day — UNFAVORABLE, only PARTIAL conds.

        CL-UI-70: golden_hour_window PARTIAL pass_hours=2 means the window
        DID occur — it abstains from the vote, and the weather condition
        (cloud_cover_total PARTIAL 8) is the honest day reason instead.
        """
        days = [("golden_hour", [{"local_date": "2026-01-01", "state": "UNFAVORABLE",
                                  "good_hours": [],
                                  "conditions": [
                                      {"metric": "golden_hour_window", "tier": "MAIN",
                                       "role": "REQUIRED", "day_verdict": "PARTIAL",
                                       "pass_hours": 2},
                                      {"metric": "cloud_cover_total", "tier": "MAIN",
                                       "role": "REQUIRED", "day_verdict": "PARTIAL",
                                       "pass_hours": 8},
                                      {"metric": "aod_550nm", "tier": "MAIN",
                                       "role": "REQUIRED", "day_verdict": "PASS",
                                       "pass_hours": 20}]}])]
        row = self._derive(_place(days))["2026-01-01"]
        self.assertEqual(row["status"], "failed")
        self.assertEqual(row["dominant_source"], "curated_votes")
        self.assertEqual(row["dominant_metric"], "cloud_cover_total")
        self.assertIsNotNone(row["dominant_reason"])


class ClUi70WindowVoteTests(unittest.TestCase):
    """CL-UI-70 (CHALLENGER-13): window metrics abstain when the window
    occurred; qualification metrics never vote at place-day level."""

    @classmethod
    def setUpClass(cls):
        cls.genres, cls.fails = bsc.load_copy()

    def _derive(self, place, weather=None):
        real_load = bsc.load_place_hourly_weather
        if weather is not None:
            bsc.load_place_hourly_weather = lambda pid: weather
        try:
            out, _ = bsc.derive_place_days(
                {"places": [place], "_source_path": "x", "_source_sha256": "0"},
                self.genres, self.fails)
        finally:
            bsc.load_place_hourly_weather = real_load
        return out["places"]["xx-000"]

    def test_window_occurred_votes_weather_not_window(self):
        """CHALLENGER-13 tw-001-P03 shape: blue hour window PASSED at 17:00
        (pass_hours=1) but the day failed on cloud — the reason must be the
        cloud word, never 「時段不對」."""
        days = [("blue_hour_city", [{"local_date": "2026-01-01", "state": "UNFAVORABLE",
                                     "good_hours": [],
                                     "conditions": [
                                         {"metric": "blue_hour_window", "tier": "MAIN",
                                          "role": "REQUIRED", "day_verdict": "PARTIAL",
                                          "pass_hours": 1},
                                         {"metric": "cloud_cover_total", "tier": "MAIN",
                                          "role": "REQUIRED", "day_verdict": "PARTIAL",
                                          "pass_hours": 3},
                                         {"metric": "precipitation", "tier": "MAIN",
                                          "role": "REQUIRED", "day_verdict": "PARTIAL",
                                          "pass_hours": 17}]}])]
        row = self._derive(_place(days))["2026-01-01"]
        self.assertEqual(row["dominant_metric"], "cloud_cover_total")
        self.assertEqual(row["dominant_source"], "curated_votes")
        self.assertEqual(row["dominant_reason"], WORDS["cloud_cover_total"])

    def test_window_absent_with_clear_weather_is_the_neutral_word(self):
        """Window never happened (pass_hours=0) and no weather violation:
        the window is the honest reason — with the neutral word."""
        days = [("city_night_view", [{"local_date": "2026-01-01", "state": "UNFAVORABLE",
                                      "good_hours": [],
                                      "conditions": [
                                          {"metric": "city_night_window", "tier": "MAIN",
                                           "role": "REQUIRED", "day_verdict": "PARTIAL",
                                           "pass_hours": 0},
                                          {"metric": "aod_550nm", "tier": "MAIN",
                                           "role": "REQUIRED", "day_verdict": "PASS",
                                           "pass_hours": 24}]}])]
        row = self._derive(_place(days))["2026-01-01"]
        self.assertEqual(row["dominant_metric"], "city_night_window")
        self.assertEqual(row["dominant_reason"], WORDS["city_night_window"])
        self.assertEqual(row["dominant_reason"]["zh-TW"], "非拍攝時段")

    def test_window_absent_but_weather_troubled_defers_to_weather(self):
        days = [("city_night_view", [{"local_date": "2026-01-01", "state": "UNFAVORABLE",
                                      "good_hours": [],
                                      "conditions": [
                                          {"metric": "city_night_window", "tier": "MAIN",
                                           "role": "REQUIRED", "day_verdict": "PARTIAL",
                                           "pass_hours": 0},
                                          {"metric": "precipitation", "tier": "MAIN",
                                           "role": "REQUIRED", "day_verdict": "PARTIAL",
                                           "pass_hours": 20}]}])]
        row = self._derive(_place(days))["2026-01-01"]
        self.assertEqual(row["dominant_metric"], "precipitation")

    def test_qualification_metrics_never_vote_at_day_level(self):
        """CHALLENGER-13 P3: 非季節 next to recommended chips was a
        contradiction — a qualification FAIL/UNKNOWN leaves the day vote
        pool; the row degrades to the general-baseline fallback (or null)."""
        days = [("sunset", [{"local_date": "2026-01-01", "state": "UNFAVORABLE",
                             "good_hours": [],
                             "conditions": [
                                 {"metric": "seasonal_state", "tier": "MAIN",
                                  "role": "REQUIRED", "day_verdict": "FAIL",
                                  "pass_hours": 0},
                                 {"metric": "sunset_window", "tier": "MAIN",
                                  "role": "REQUIRED", "day_verdict": "PARTIAL",
                                  "pass_hours": 2},
                                 {"metric": "aod_550nm", "tier": "MAIN",
                                  "role": "REQUIRED", "day_verdict": "PASS",
                                  "pass_hours": 24}]}])]
        row = self._derive(_place(days))["2026-01-01"]
        self.assertNotIn(row["dominant_metric"], ("seasonal_state",))
        self.assertIsNone(row["dominant_reason"])
        self.assertIsNone(row["dominant_source"])


class ArtifactRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(
            (ROOT / "data/v2/evaluations/subject-cards-20261112T202312Z.json")
            .read_bytes().decode("utf-8"))

    def test_dadaocheng_has_a_reason_on_its_bare_failed_day(self):
        rows = self.artifact["places"]["tw-005"]
        self.assertTrue(any(
            r["status"] == "failed" and r["dominant_reason"] and r["dominant_source"] == "curated_votes"
            for r in rows.values()), "tw-005 failed days must carry a curated reason")

    def test_every_row_has_general_baseline(self):
        n = 0
        for rows in self.artifact["places"].values():
            for row in rows.values():
                self.assertIn("general_baseline", row)
                self.assertIsInstance(row["general_baseline"]["ok"], bool)
                n += 1
        self.assertGreater(n, 3000)

    def test_no_general_contract_mounted(self):
        """general baseline is derived, never a formal P99-style contract flood."""
        opp_dir = ROOT / "data/v2/opportunities"
        mounted = [p.name for p in opp_dir.glob("*-P99.json")]
        # only the CL-DATA-65 zero-curated mounts (a handful), not 460 contracts
        self.assertLess(len(mounted), 30)


class ClUi70FullCatalogVoteTests(unittest.TestCase):
    """CL-UI-70 (CHALLENGER-13 P1/P2/P3): full-catalog invariant — a
    window-class dominant metric may only name a genuinely ABSENT window
    (its condition pass_hours == 0), and qualification-class metrics never
    become the place-day dominant reason."""

    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(
            (ROOT / "data/v2/evaluations/subject-cards-20261112T202312Z.json")
            .read_bytes().decode("utf-8"))

    def test_no_window_dominant_row_where_the_window_occurred(self):
        bundle = json.loads((EVAL_DIR / self.artifact["derived_from"]["source_bundle"])
                            .read_bytes().decode("utf-8"))
        checked = 0
        for place in bundle["places"]:
            rows = self.artifact["places"].get(place["place_id"], {})
            # a place-day row aggregates votes from EVERY opportunity that
            # date — collect all that date's conditions before the lookup
            conds_by_date = {}
            for opp in place["opportunities"]:
                for day in opp["days"]:
                    conds_by_date.setdefault(day["local_date"], []).extend(
                        day["conditions"])
            for date, row in rows.items():
                if row.get("dominant_metric") not in bsc.WINDOW_METRICS:
                    continue
                checked += 1
                cond = next((c for c in conds_by_date.get(date, [])
                             if c["metric"] == row["dominant_metric"]), None)
                self.assertIsNotNone(cond)
                self.assertEqual((cond or {}).get("pass_hours", 0), 0,
                                 "%s %s: window occurred but dominates (%s)"
                                 % (place["place_id"], date,
                                    row["dominant_metric"]))
        self.assertLess(checked, 100)

    def test_no_qualification_metric_ever_dominates(self):
        for pid, rows in self.artifact["places"].items():
            for date, row in rows.items():
                self.assertNotIn(row.get("dominant_metric"), bsc.QUALIFICATION_METRICS,
                                 "%s %s" % (pid, date))


if __name__ == "__main__":
    unittest.main()
