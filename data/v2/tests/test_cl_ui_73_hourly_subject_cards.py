"""CL-UI-73: hourly granularity of the derived subject-card layer.

Covers: per-hour general floor (hourly_general_rows — ok/no/fit/unk buckets,
fail-closed on missing or incomplete weather), the fitting-subject merge (a
curated subject fits exactly the hours inside its good_hours window), the
hour key matching the forecast modal's "HH:MM" key, and the committed
artifact's tw-142 (安平漁人碼頭) hourly spot-check.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "data/v2/tools"))

import build_subject_cards as bsc  # noqa: E402


def _words():
    return json.loads((ROOT / "data/v2/copy/fail_reason_short.json").read_bytes().decode("utf-8"))


PRIORITY = {m: i for i, m in enumerate(_words()["metric_priority"])}
WORDS = _words()["words"]

# CL-CI-36: the scheduled refresh rebuilds the artifact in place under the
# stable pointer app.js pins (V2_SUBJECT_CARDS_FILE) — resolve the filename
# from app.js, never a copied literal that goes stale every 6h.
_pointer = re.search(
    r"V2_SUBJECT_CARDS_FILE='([^']+)'",
    (ROOT / "assets/app.js").read_text(encoding="utf-8"))
assert _pointer, "app.js pins V2_SUBJECT_CARDS_FILE"
ARTIFACT = ROOT / "data/v2/evaluations" / _pointer.group(1)


def _hour(hh, vis=24.1, precip=0.0, rh=60, sun=30):
    return {"time": "2026-01-01 %s" % hh, "visibility": vis,
            "precipitation": precip, "rh": rh, "sun_elevation": sun}


class HourlyGeneralRowsTests(unittest.TestCase):
    def test_clear_daylight_hours_ok(self):
        rows = bsc.hourly_general_rows([_hour("12:00")], 5, PRIORITY)
        self.assertEqual(rows["ok"], ["12:00"])
        self.assertEqual(rows["no"], {})
        self.assertEqual(rows["unk"], [])
        self.assertEqual(rows["fit"], {})

    def test_night_hour_is_neutral_not_light_window(self):
        # CHALLENGER-14/B: a night hour is NOT a light_window failure — night
        # scenery subjects are IN their window at night; without a covering
        # curated window the hour is neutral (na), never a failure word, and
        # never a general pass either.
        rows = bsc.hourly_general_rows([_hour("02:00", sun=-20)], 5, PRIORITY)
        self.assertEqual(rows["no"], {})
        self.assertEqual(rows["na"], ["02:00"])
        self.assertNotIn("02:00", rows["ok"])

    def test_night_weather_violation_names_a_weather_word(self):
        # CHALLENGER-14/B: weather words win the no bucket — a fogged night
        # hour is ✗ 霾/能見度, never ✗ 非日照時段 (light_window stays a
        # DAY-layer vote only).
        rows = bsc.hourly_general_rows([_hour("02:00", sun=-20, vis=1.5)], 5, PRIORITY)
        self.assertEqual(rows["no"], {"02:00": "visibility"})
        self.assertEqual(rows["na"], [])

    def test_rain_hour_names_precipitation(self):
        rows = bsc.hourly_general_rows([_hour("13:00", precip=2.0)], 5, PRIORITY)
        self.assertEqual(rows["no"], {"13:00": "precipitation"})

    def test_incomplete_hour_is_unknown_fail_closed(self):
        rows = bsc.hourly_general_rows(
            [{"time": "2026-01-01 14:00", "visibility": 20}], 5, PRIORITY)
        self.assertEqual(rows["unk"], ["14:00"])
        self.assertEqual(rows["ok"], [])
        self.assertEqual(rows["no"], {})

    def test_hour_without_time_is_dropped(self):
        self.assertEqual(bsc.hourly_general_rows([{"visibility": 20}], 5, PRIORITY),
                         {"ok": [], "no": {}, "fit": {}, "unk": [], "na": []})

    def test_view_scale_applies_per_hour(self):
        rows = bsc.hourly_general_rows([_hour("10:00", vis=6)], 8, PRIORITY)
        self.assertEqual(rows["no"], {"10:00": "visibility"})
        self.assertEqual(bsc.hourly_general_rows([_hour("10:00", vis=6)], 5, PRIORITY)["ok"],
                         ["10:00"])


class HourlyMergeTests(unittest.TestCase):
    """Fitting subjects land on exactly the hours of their good_hours window."""

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

    def test_sunset_subject_fits_only_its_window_hours(self):
        weather = {"2026-01-01": [_hour("%02d:00" % h) for h in range(24)]}
        days = [("sunset", [{"local_date": "2026-01-01", "state": "GUIDANCE_SATISFIED",
                             "good_hours": ["17:00", "18:00"], "conditions": []}])]
        row = self._derive(_place(days), weather)["2026-01-01"]
        self.assertEqual(row["hours"]["fit"], {"17:00": ["sunset"], "18:00": ["sunset"]})
        # the general floor is independent of the curated windows: on a clear
        # day every hour (window or not) is ok, and a fit hour stays ok too
        self.assertIn("12:00", row["hours"]["ok"])
        self.assertIn("17:00", row["hours"]["ok"])
        self.assertEqual(row["hours"]["no"], {})
        self.assertEqual(row["hours"]["unk"], [])

    def test_fit_hour_without_a_weather_bucket_has_no_floor_verdict(self):
        weather = {"2026-01-01": [_hour("%02d:00" % h) for h in range(24)]}
        days = [("sunset", [{"local_date": "2026-01-01", "state": "GUIDANCE_SATISFIED",
                             "good_hours": ["25:00"], "conditions": []}])]
        row = self._derive(_place(days), weather)["2026-01-01"]
        # the fit bucket itself is honest eval-bundle data, but no weather row
        # means no ok/no/unk verdict is fabricated for that hour key
        self.assertEqual(row["hours"]["fit"], {"25:00": ["sunset"]})
        self.assertNotIn("25:00", row["hours"]["ok"])
        self.assertNotIn("25:00", row["hours"]["no"])
        self.assertEqual(row["hours"]["unk"], [])

    def test_sub_hour_window_stamp_folds_into_the_covering_bucket(self):
        # CHALLENGER-14/D (CHALLENGER-13 P7 closure): a precise sub-hour
        # good_hours stamp (17:35 inside the 17:00 bucket) lands on the :00
        # bucket row — the hourly grid only renders :00 rows, so the sub-hour
        # bucket would otherwise be unreachable. The precise stamp itself is
        # untouched in suitable[].window.
        weather = {"2026-01-01": [_hour("%02d:00" % h, sun=-20 if h < 17 else 30)
                                  for h in range(24)]}
        days = [("sunset", [{"local_date": "2026-01-01", "state": "GUIDANCE_SATISFIED",
                             "good_hours": ["17:35"], "conditions": []}])]
        row = self._derive(_place(days), weather)["2026-01-01"]
        self.assertEqual(row["hours"]["fit"], {"17:00": ["sunset"]})
        self.assertEqual([hh for hh in row["hours"]["fit"] if hh[3:] != "00"], [])
        self.assertEqual(row["suitable"][0]["window"], ["17:35"])

    def test_window_coverage_clears_the_no_and_na_buckets(self):
        # CHALLENGER-14/B: one hour, one bucket — a night hour a curated
        # window covers must not simultaneously carry a no-word (fit∩no was
        # 1,163 hours in the previous artifact, only shadowed by the
        # renderer's priority) nor stay in the neutral na list.
        weather = {"2026-01-01": [_hour("%02d:00" % h, sun=-20, vis=1.5)
                                  for h in range(24)]}
        days = [("night_sky", [{"local_date": "2026-01-01", "state": "GUIDANCE_SATISFIED",
                                "good_hours": ["02:00"], "conditions": []}])]
        row = self._derive(_place(days), weather)["2026-01-01"]
        self.assertIn("02:00", row["hours"]["fit"])
        self.assertNotIn("02:00", row["hours"]["no"])
        self.assertNotIn("02:00", row["hours"]["na"])

    def test_no_weather_day_has_empty_floor_buckets(self):
        days = [("sunset", [{"local_date": "2026-01-01", "state": "GUIDANCE_SATISFIED",
                             "good_hours": ["17:00"], "conditions": []}])]
        row = self._derive(_place(days), {})["2026-01-01"]
        self.assertEqual(row["hours"], {"ok": [], "no": {}, "fit": {"17:00": ["sunset"]}, "unk": [], "na": []})

    def test_day_baseline_stays_the_hour_aggregate(self):
        weather = {"2026-01-01": [_hour("%02d:00" % h, precip=1.0 if h == 9 else 0.0)
                                  for h in range(24)]}
        days = [("sunset", [{"local_date": "2026-01-01", "state": "GUIDANCE_SATISFIED",
                             "good_hours": ["17:00"], "conditions": []}])]
        row = self._derive(_place(days), weather)["2026-01-01"]
        self.assertTrue(row["general_baseline"]["ok"])
        self.assertEqual(row["hours"]["no"], {"09:00": "precipitation"})


def _place(opp_days):
    return {"place_id": "xx-000", "name_i18n": {"zh-TW": "x"},
            "opportunities": [
                {"opportunity_id": "xx-000-P01", "genre_template": g, "days": days}
                for g, days in opp_days]}


class ArtifactHourlySpotCheckTests(unittest.TestCase):
    """CL-UI-73: the committed artifact carries the hourly layer, and the
    tw-142 (安平漁人碼頭) rows round-trip against the committed weather file."""

    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(ARTIFACT.read_bytes().decode("utf-8"))
        cls.bundle = json.loads(
            (ROOT / "data/v2/evaluations" / cls.artifact["derived_from"]["source_bundle"])
            .read_bytes().decode("utf-8"))
        cls.genres = cls.artifact["dictionaries"]["genre_short_names"]
        cls.words = cls.artifact["dictionaries"]["fail_reason_short"]

    def test_schema_and_hourly_provenance(self):
        self.assertEqual(self.artifact["schema_version"], "1.3")
        self.assertIn("hourly_granularity", self.artifact["derived_from"])

    def test_every_row_carries_hour_buckets(self):
        n = 0
        for rows in self.artifact["places"].values():
            for row in rows.values():
                hours = row["hours"]
                self.assertEqual(sorted(hours), ["fit", "na", "no", "ok", "unk"])
                self.assertIsInstance(hours["ok"], list)
                self.assertIsInstance(hours["no"], dict)
                self.assertIsInstance(hours["fit"], dict)
                self.assertIsInstance(hours["unk"], list)
                self.assertIsInstance(hours["na"], list)
                n += 1
        self.assertGreater(n, 3000)

    def test_no_bucket_content_is_valid(self):
        for rows in self.artifact["places"].values():
            for row in rows.values():
                hours = row["hours"]
                for metric in hours["no"].values():
                    self.assertIn(metric, self.words, metric)
                    # CHALLENGER-14/B: light_window never names an HOUR
                    # failure — night hours are window-coverage decisions.
                    self.assertNotEqual(metric, "light_window")
                # CHALLENGER-14/B: one hour, one bucket.
                self.assertFalse(set(hours["fit"]) & set(hours["no"]))
                self.assertFalse(set(hours["fit"]) & set(hours["na"]))
                # CHALLENGER-14/D: every fit bucket is reachable from the
                # hourly table's :00 rows.
                for hh in hours["fit"]:
                    self.assertEqual(hh[3:], "00", f"sub-hour fit bucket {hh}")
                for genre_list in hours["fit"].values():
                    self.assertTrue(genre_list)
                    for g in genre_list:
                        self.assertIn(g, self.genres, g)

    def test_tw142_anping_hourly_output(self):
        place = next(p for p in self.bundle["places"] if p["place_id"] == "tw-142")
        weather = json.loads((ROOT / "weather_details/tw/tw-142.json").read_bytes().decode("utf-8"))
        by_date = {}
        for hour in weather["spot"]["hourly_forecast"]:
            by_date.setdefault(hour["local_date"], []).append(hour)
        for date, row in self.artifact["places"]["tw-142"].items():
            hours = row["hours"]
            whours = by_date.get(date) or []
            every_known_hour = all(
                all(h.get(k) is not None for k in
                    ("visibility", "precipitation", "rh", "sun_elevation"))
                for h in whours)
            if whours and every_known_hour:
                # CHALLENGER-14/B accounting: one verdict per hour — ok, or a
                # fit-only hour (a covering window removed its no/na word), or
                # no, unk, na. (A daylight window hour stays in ok AND fit.)
                fit_only = {hh for hh in hours["fit"] if hh not in set(hours["ok"])}
                self.assertEqual(len(hours["ok"]) + len(fit_only)
                                 + len(hours["no"]) + len(hours["unk"])
                                 + len(hours["na"]),
                                 len(whours), date)
            self.assertFalse(hours["unk"], f"{date} must have complete fields")
            # fit hours must be inside the curated good_hours windows
            good = set()
            for opp in place["opportunities"]:
                for day in opp["days"]:
                    if day["local_date"] == date and day["state"] == "GUIDANCE_SATISFIED":
                        good.update(day.get("good_hours") or [])
            # CHALLENGER-14/D: sub-hour stamps fold to their covering bucket.
            good = {hh[:3] + "00" if hh[3:] != "00" else hh for hh in good
                    if isinstance(hh, str) and len(hh) == 5}
            for hh in hours["fit"]:
                self.assertIn(hh, good, f"tw-142 {date} {hh} not in good_hours")
        # one concrete daylight row, anchored dynamically (CL-CI-36): the
        # refresh slides the 8-day window every run, so the spot-check date is
        # derived from the current artifact — the row must be a tw-142 day
        # whose curated window fits a city-night hour, with neutral night
        # hours (na, never no) and daylight general-pass hours.
        day_date = next(
            d for d, r in self.artifact["places"]["tw-142"].items()
            if any("city_night" in g for g in r["hours"]["fit"].values()))
        day1 = self.artifact["places"]["tw-142"][day_date]["hours"]
        fit_hh = next(hh for hh, g in day1["fit"].items() if "city_night" in g)
        self.assertIn("city_night", day1["fit"][fit_hh])
        self.assertTrue(day1["na"], f"tw-142 {day_date} has neutral night hours")
        for hh in day1["na"]:
            self.assertNotIn(hh, day1["no"])  # night hours are never a failure
        self.assertTrue(day1["ok"], f"tw-142 {day_date} has daylight general-pass hours")
        self.assertEqual(self.words["light_window"]["zh-TW"], "非日照時段")  # CL-UI-70 word layer

    def test_lf_bytes(self):
        self.assertNotIn(b"\r\n", ARTIFACT.read_bytes())


class SameRunAssertionTests(unittest.TestCase):
    """CHALLENGER-14/A: build_subject_cards refuses a cross-run bundle."""

    def setUp(self):
        self.details = Path(self.enterContext(_tmp_dir()))

    def test_matching_run_passes(self):
        (self.details / "tw-000.json").write_text(
            json.dumps({"generated_at": "2026-11-13T07:12:12Z"}), encoding="utf-8")
        self.assertIsNone(bsc.assert_same_run_as_details(
            "/x/bundle-20261113T071212Z.json", self.details))

    def test_mismatched_run_refused(self):
        (self.details / "tw-001.json").write_text(
            json.dumps({"generated_at": "2026-11-14T01:12:12Z"}), encoding="utf-8")
        with self.assertRaises(SystemExit):
            bsc.assert_same_run_as_details(
                "/x/bundle-20261113T071212Z.json", self.details)

    def test_missing_details_warn_but_proceed(self):
        empty = self.details / "empty"
        empty.mkdir()
        self.assertIsNone(bsc.assert_same_run_as_details(
            "/x/bundle-20261113T071212Z.json", empty))

    def test_stale_older_run_details_do_not_block(self):
        (self.details / "tw-002.json").write_text(
            json.dumps({"generated_at": "2026-11-12T20:23:12Z"}), encoding="utf-8")
        (self.details / "tw-003.json").write_text(
            json.dumps({"generated_at": "2026-11-13T07:12:12Z"}), encoding="utf-8")
        self.assertIsNone(bsc.assert_same_run_as_details(
            "/x/bundle-20261113T071212Z.json", self.details))


import contextlib  # noqa: E402
import tempfile  # noqa: E402


@contextlib.contextmanager
def _tmp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


if __name__ == "__main__":
    unittest.main()
