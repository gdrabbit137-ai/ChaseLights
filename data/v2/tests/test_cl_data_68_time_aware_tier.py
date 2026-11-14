"""CL-DATA-68: time-aware tier (single truth) + minute-level civil windows.

Covers (owner-approved plan): the derived layer's single tier field judged
over the REMAINING period after the evaluation instant — (1) a curated
subject window with qualifying minutes ahead → recommend, (2) every window
passed/never matched but the remaining-period general baseline passes →
shootable with 「窗已過·今日仍可拍」, (3) the remaining baseline also fails →
not_recommended with the short remaining reason, (4) cross-day rows keep
the full-day rules, plus the minute-level civil-light boundary case (an
hour the grid instant calls dark but which contains civil-light minutes)
and the single-truth tab-consistency invariants over the committed
artifact. Offline, no network.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(0, str(ROOT / "data/v2/tools"))
sys.path.insert(0, str(ROOT / "packages/models-v2"))

import build_subject_cards as bsc  # noqa: E402
import civil_twilight as ct  # noqa: E402


def _words():
    return json.loads((ROOT / "data/v2/copy/fail_reason_short.json")
                      .read_bytes().decode("utf-8"))


PRIORITY = {m: i for i, m in enumerate(_words()["metric_priority"])}
WORDS = _words()["words"]


def _hour(hour, vis=24.1, precip=0.0, rh=60, sun=30, **extra):
    row = {"time": "2026-11-14 %02d:00" % hour if isinstance(hour, int)
           else hour,
           "local_date": "2026-11-14",
           "visibility": vis, "precipitation": precip, "rh": rh,
           "sun_elevation": sun}
    row.update(extra)
    return row


def _place(genre="sunset", days=None, lat=25.033, lon=121.565, offset=8):
    return {
        "place_id": "tw-000",
        "coordinate": [lat, lon],
        "timezone_display": {"iana": "Asia/Taipei", "utc_offset_hours": offset},
        "opportunities": [{
            "opportunity_id": "tw-000-P01",
            "genre_template": genre,
            "days": days or [],
        }],
    }


def _sunset_day(good_hours=("17:00",)):
    return {"local_date": "2026-11-14", "state": "GUIDANCE_SATISFIED",
            "good_hours": list(good_hours),
            "conditions": [{"id": "C1", "metric": "golden_hour_window",
                            "tier": "MAIN", "role": "REQUIRED",
                            "day_verdict": "PASS", "pass_hours": 1}]}


def _derive(place, weather, generated_at=None):
    bundle = {"places": [place], "_source_path": "x", "_source_sha256": "0"}
    if generated_at:
        bundle["generated_at"] = generated_at
    real_load = bsc.load_place_hourly_weather
    bsc.load_place_hourly_weather = lambda pid: weather
    try:
        out, _ = bsc.derive_place_days(bundle, bsc.load_copy()[0],
                                       _words())
    finally:
        bsc.load_place_hourly_weather = real_load
    return out["places"]["tw-000"]


class TimeAwareTierTests(unittest.TestCase):
    def test_window_still_ahead_is_recommend(self):
        # eval 2026-11-14T08:00:00Z = 16:00 local; the golden-hour dusk
        # window ends ~17:30 (minute-level) — qualifying minutes remain.
        weather = {"2026-11-14": [_hour(h) for h in range(24)]}
        row = _derive(_place(days=[_sunset_day()]), weather,
                      "2026-11-14T08:00:00Z")["2026-11-14"]
        self.assertEqual(row["tier"], "recommend")
        self.assertEqual(row["tier_basis"], "remaining")

    def test_window_passed_clean_remaining_is_shootable_with_note(self):
        # eval 17:58 local: the golden window (ends 17:30) has passed, the
        # remaining evening hours stay clean → shootable + the owner note.
        weather = {"2026-11-14": [_hour(h) for h in range(24)]}
        row = _derive(_place(days=[_sunset_day()]), weather,
                      "2026-11-14T09:58:41Z")["2026-11-14"]
        self.assertEqual(row["tier"], "shootable")
        self.assertEqual(row["tier_reason"]["zh-TW"], "窗已過·今日仍可拍")
        self.assertTrue(row["remaining_baseline"]["ok"])

    def test_window_passed_rainy_remaining_is_not_recommended(self):
        # Same passed window, but the remaining hours rain — the remaining
        # baseline fails and the short reason names the weather.
        weather = {"2026-11-14": [
            _hour(h, precip=5.0) if h >= 17 else _hour(h)
            for h in range(24)]}
        row = _derive(_place(days=[_sunset_day()]), weather,
                      "2026-11-14T09:58:41Z")["2026-11-14"]
        self.assertEqual(row["tier"], "not_recommended")
        self.assertEqual(row["tier_reason"], WORDS["precipitation"])
        self.assertFalse(row["remaining_baseline"]["ok"])

    def test_window_passed_unknown_remaining_stays_honest_null(self):
        weather = {"2026-11-14": [
            _hour(h, vis=None) if h >= 17 else _hour(h) for h in range(24)]}
        row = _derive(_place(days=[_sunset_day()]), weather,
                      "2026-11-14T09:58:41Z")["2026-11-14"]
        self.assertIsNone(row["tier"])
        self.assertFalse(row["remaining_baseline"]["ok"])

    def test_cross_day_keeps_the_full_day_rules(self):
        # Rule 4: a tomorrow day is judged all-remaining — the same sunset
        # subject that already passed today stays recommend for tomorrow.
        weather = {"2026-11-14": [_hour(h) for h in range(24)]}
        place = _place(days=[{"local_date": "2026-11-15",
                              "state": "GUIDANCE_SATISFIED",
                              "good_hours": ["17:00"],
                              "conditions": _sunset_day()["conditions"]}])
        row = _derive(place, weather, "2026-11-14T09:58:41Z")["2026-11-15"]
        self.assertEqual(row["tier"], "recommend")
        self.assertEqual(row["tier_basis"], "full_day")
        self.assertIsNone(row["remaining_baseline"])
        self.assertIsNone(row["tier_reason"])

    def test_no_evaluated_at_keeps_the_full_day_rules(self):
        weather = {"2026-11-14": [_hour(h) for h in range(24)]}
        row = _derive(_place(days=[_sunset_day()]), weather,
                      generated_at=None)["2026-11-14"]
        self.assertEqual(row["tier"], "recommend")
        self.assertEqual(row["tier_basis"], "full_day")

    def test_minute_level_civil_light_boundary_hour(self):
        # THE minute-level vs hour-bucket case: Taipei 2026-11-14 civil dawn
        # 05:45 — the 05:00 bucket reads dark at the grid instant
        # (sun -7) but contains 15 civil-light minutes. The old hourly
        # sun_elevation test violated light_window for it; the interval
        # intersection passes it.
        weather = {"2026-11-14": [
            _hour(h, sun=-7 if h in (0, 1, 2, 3, 4, 5, 19, 20, 21, 22, 23)
                  else 30) for h in range(24)]}
        row = _derive(_place(days=[_sunset_day()]), weather,
                      "2026-11-14T08:00:00Z")["2026-11-14"]
        self.assertIn("05:00", row["hours"]["ok"])
        self.assertNotIn("05:00", row["hours"]["na"])
        self.assertEqual(row["civil_light"]["dawn"], "05:45")
        self.assertEqual(row["civil_light"]["dusk"], "17:30")

    def test_subject_window_left_uses_the_minute_interval(self):
        solar = ct.solar_day_windows(25.033, 121.565, "2026-11-14", 8)
        entry = {"window": ["17:00"],
                 "window_metrics": ["golden_hour_window"]}
        golden_dusk_end = max(e for s, e in solar["intervals"]
                              ["golden_hour_window"] if e <= 1440)
        self.assertEqual(golden_dusk_end, 17 * 60 + 30)
        self.assertTrue(bsc.subject_window_left(entry, solar, 16 * 60))
        self.assertFalse(bsc.subject_window_left(entry, solar, 17 * 60 + 31))
        # no geometry: the bucket end is the honest fallback
        self.assertFalse(bsc.subject_window_left(entry, None, 18 * 60))
        self.assertTrue(bsc.subject_window_left(entry, None, 17 * 60 + 30))

    def test_top_level_schema_and_freshness_stamp(self):
        weather = {"2026-11-14": [_hour(h) for h in range(24)]}
        bundle = {"places": [_place(days=[_sunset_day()])],
                  "_source_path": "x", "_source_sha256": "0",
                  "generated_at": "2026-11-14T08:00:00Z"}
        real_load = bsc.load_place_hourly_weather
        bsc.load_place_hourly_weather = lambda pid: weather
        try:
            out, _ = bsc.derive_place_days(bundle, bsc.load_copy()[0],
                                           _words())
        finally:
            bsc.load_place_hourly_weather = real_load
        self.assertEqual(out["schema_version"], "1.4")
        self.assertEqual(out["tier_evaluated_at"], "2026-11-14T08:00:00Z")
        semantics = out["derived_from"]["tier_semantics"]
        self.assertEqual(semantics["rule_version"], "1.0")
        self.assertEqual(semantics["evaluated_at"], out["tier_evaluated_at"])
        self.assertIn("civil_twilight", semantics["civil_light"]["source"])
        # the legacy columns survive unchanged (compat contract, rule 5)
        row = out["places"]["tw-000"]["2026-11-14"]
        for key in ("status", "suitable", "hours", "dominant_metric",
                    "dominant_reason", "dominant_source", "general_baseline",
                    "tier"):
            self.assertIn(key, row)


class SingleTruthConsistencyTests(unittest.TestCase):
    """The committed artifact's tier is the ONE source the tier tabs and the
    cards consume (分頁計數加總=總數、卡片 tier=分頁 tier)."""

    @classmethod
    def setUpClass(cls):
        pointer = re.search(r"V2_SUBJECT_CARDS_FILE='([^']+)'",
                            (ROOT / "assets/app.js").read_text(encoding="utf-8"))
        assert pointer, "app.js pins V2_SUBJECT_CARDS_FILE"
        path = ROOT / "data/v2/evaluations" / pointer.group(1)
        cls.artifact = json.loads(path.read_bytes().decode("utf-8"))

    def test_tier_enum_and_single_field(self):
        n = 0
        counts = {"recommend": 0, "shootable": 0, "not_recommended": 0,
                  "null": 0}
        for days in self.artifact["places"].values():
            for row in days.values():
                n += 1
                if row["tier"] is None:
                    counts["null"] += 1
                else:
                    self.assertIn(row["tier"],
                                  ("recommend", "shootable",
                                   "not_recommended"))
                    counts[row["tier"]] += 1
                self.assertIn(row.get("tier_basis"),
                              ("remaining", "full_day"))
        self.assertGreater(n, 3000)
        # 分頁計數加總=總數: the three tabs plus the honest-null rows cover
        # every place-day exactly once.
        self.assertEqual(counts["recommend"] + counts["shootable"]
                         + counts["not_recommended"] + counts["null"], n)
        self.assertGreater(counts["recommend"], 0)
        self.assertGreater(counts["shootable"], 0)
        self.assertGreater(counts["not_recommended"], 0)

    def test_time_aware_rows_carry_the_remaining_columns(self):
        seen_remaining = 0
        for days in self.artifact["places"].values():
            for row in days.values():
                if row.get("tier_basis") == "remaining":
                    seen_remaining += 1
                    self.assertIn("remaining_baseline", row)
                    self.assertIn("tier_reason", row)
                    self.assertEqual(self.artifact["tier_evaluated_at"],
                                     self.artifact["derived_from"]
                                     ["tier_semantics"]["evaluated_at"])
                if row.get("tier_basis") == "remaining" and \
                        row["tier"] == "shootable":
                    self.assertTrue(row["remaining_baseline"]["ok"])
                    self.assertEqual(row["tier_reason"]["zh-TW"],
                                     "窗已過·今日仍可拍")
                elif row.get("tier_basis") == "remaining" and \
                        row["tier"] == "not_recommended":
                    self.assertFalse(row["remaining_baseline"]["ok"])
        self.assertGreater(seen_remaining, 100,
                           "today rows exist across the catalog")

    def test_civil_light_minute_stamps_present(self):
        stamped = 0
        for days in self.artifact["places"].values():
            for row in days.values():
                stamp = row.get("civil_light")
                if stamp is not None:
                    stamped += 1
                    for key in ("dawn", "dusk"):
                        self.assertRegex(stamp[key], r"^\d{2}:\d{2}$")
                    self.assertLess(stamp["dawn"], stamp["dusk"])
        self.assertGreater(stamped, 3000)

    def test_per_day_tab_counts_sum_to_the_day_rows(self):
        # the UI renders one tier-tab count set per selected local date;
        # each date's rows must be fully partitioned by the three tiers
        # plus honest-null (the 資料不足/noeval class).
        for pid, days in self.artifact["places"].items():
            for date, row in days.items():
                self.assertIn(row["tier"],
                              ("recommend", "shootable", "not_recommended",
                               None),
                               "%s %s" % (pid, date))


if __name__ == "__main__":
    unittest.main()
