"""CL-DATA-06R: legacy weather pipeline spans the 7-day forecast window.

The legacy homepage cards consume daily conclusions from `${region}_weather.json`.
CL-DATA-06 extended the V2 evaluation bundle to 7 days (168h) but left the
legacy path at 72h, so the far-day tabs rendered zero cards.
This file pins the fix: Open-Meteo forecast_hours=168, legacy daily across
seven LOCAL dates, and at least one card on the first far day.

CL-PHYS-02 stage 1 removed the two stale pins (the hardcoded `tw: 85` spot
counts and the literal 2026-11-08 date): the catalog has since grown and the
window is relative to today, so both now derive from the data. What they
protected is unchanged — exactly seven daily entries per spot, seven
CONSECUTIVE local days covering today, and a far-day card in every region.
"""
import json
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import analyze_weather
import opportunities

ROOT = Path(__file__).resolve().parent
FAR_DAY_OFFSET = 3  # the first day past the old 72h horizon


def local_today():
    """Today in the app's reference zone (Asia/Taipei, UTC+8)."""
    return datetime.now(timezone.utc).astimezone(
        timezone(timedelta(hours=8))).date()


def region_snapshot(region):
    return json.loads((ROOT / f"{region}_weather.json").read_text(encoding="utf-8"))


class LegacyForecastHorizonTests(unittest.TestCase):
    def test_fetch_request_pulls_168_hours(self):
        src = Path("fetch_data.py").read_text(encoding="utf-8")
        self.assertIn("FORECAST_HOURS = 168", src)
        self.assertNotIn('"forecast_hours=72"', src)

    def test_get_weather_dev_cli_pulls_168_hours(self):
        src = Path("get_weather.py").read_text(encoding="utf-8")
        self.assertIn('"forecast_hours": 168', src)

    def test_legacy_daily_window_is_seven_days(self):
        self.assertEqual(analyze_weather.LEGACY_DAILY_DAYS, 7)

    def test_day_summaries_span_seven_future_dates(self):
        # CL-PHYS-02: the window starts at TODAY (local), not a frozen date.
        start = local_today()
        dates = [(start + timedelta(days=offset)).isoformat()
                 for offset in range(7)]
        hours = []
        for offset, local_date in enumerate(dates):
            hours.append({
                "is_past": False,
                "local_date": local_date,
                "time": f"{local_date} 18:00",
                "time_utc": f"{local_date}T10:00:00Z",
                "access_open": True,
                "opportunity_scores": {
                    "tw-018-P02": {"score": 88, "status_key": "OPPORTUNITY_MATCH",
                                   "indicator_key": "OPPORTUNITY_MATCH", "factors": [],
                                   "runtime_policy": "preview_module_available",
                                   "condition_state": "dedicated_conditions_match",
                                   "score_confidence": "high",
                                   "recommendation_state": "recommended",
                                   "recommendation_eligible": True,
                                   "base_theme_score": 91},
                },
            })
        opportunity = next(
            o for o in opportunities.get_opportunities("tw", "tw-018")
            if o["opportunity_id"] == "tw-018-P02"
        )
        days = analyze_weather._build_day_summaries(hours, ["reflection"], [opportunity])
        self.assertEqual(len(days), 7)
        self.assertEqual([d["date"] for d in days], dates)
        far_date = dates[FAR_DAY_OFFSET]
        far = next(d for d in days if d["date"] == far_date)
        self.assertIn("tw-018-P02", far["opportunities"])
        self.assertEqual(far["all"]["opportunity_id"], "tw-018-P02")

    def test_regenerated_region_snapshots_have_seven_daily_entries(self):
        # CL-PHYS-02: the spot count is derived, not pinned — the catalog
        # grows (219 tw / 94 jp / 160 us at the time of writing). The
        # protected invariant is "every spot in every region carries exactly
        # seven daily entries over seven CONSECUTIVE local days covering
        # today", never a frozen catalog size.
        today = local_today()
        for region in ("tw", "jp", "us"):
            with self.subTest(region=region):
                data = region_snapshot(region)
                spots = data["spots"]
                self.assertGreater(len(spots), 0, f"{region} has no spots")
                self.assertEqual(data.get("total_spots"), len(spots))
                for spot in spots:
                    daily = spot.get("daily") or []
                    self.assertEqual(len(daily), 7,
                                     f"{region} {spot['spot_id']} daily != 7")
                    dates = [date.fromisoformat(day["date"]) for day in daily]
                    self.assertEqual(
                        dates,
                        [dates[0] + timedelta(days=offset) for offset in range(7)],
                        f"{region} {spot['spot_id']} daily is not 7 consecutive days")
                    # The window is relative to the run date: it must start at
                    # or before today and carry the following days. (A western
                    # region's LOCAL date can lag UTC by one day, so the exact
                    # start date is asserted per region below.)
                    self.assertLessEqual(dates[0], today,
                                         f"{region} window starts after today")
                    self.assertIn(today, dates,
                                  f"{region} window does not cover today")

    def test_first_far_day_has_at_least_one_card_per_region(self):
        # CL-PHYS-02: the far day is the 4th local day of the snapshot window
        # (the first day the old 72h path could not reach), never a literal
        # calendar date.
        for region in ("tw", "jp", "us"):
            with self.subTest(region=region):
                data = region_snapshot(region)
                window = sorted({day["date"]
                                 for spot in data["spots"]
                                 for day in (spot.get("daily") or [])})
                self.assertGreaterEqual(len(window), 7, f"{region} window < 7 days")
                self.assertEqual(
                    [date.fromisoformat(d) for d in window],
                    [date.fromisoformat(window[0]) + timedelta(days=offset)
                     for offset in range(len(window))],
                    f"{region} window is not consecutive")
                far_date = window[FAR_DAY_OFFSET]
                cards = [
                    spot["spot_id"]
                    for spot in data["spots"]
                    for day in (spot.get("daily") or [])
                    if day["date"] == far_date
                    and (day.get("all") or {}).get("score") is not None
                ]
                self.assertGreaterEqual(len(cards), 1,
                                        f"{region} has no {far_date} card")


if __name__ == "__main__":
    unittest.main()
