"""CL-DATA-06R: legacy weather pipeline spans the 7-day forecast window.

The legacy homepage cards consume daily conclusions from `${region}_weather.json`.
CL-DATA-06 extended the V2 evaluation bundle to 7 days (168h) but left the
legacy path at 72h, so the far-day tabs (11/08 onward) rendered zero cards.
This file pins the fix: Open-Meteo forecast_hours=168, legacy daily across
seven local dates, and at least one card on the first far day (2026-11-08).
"""
import json
import unittest
from pathlib import Path

import analyze_weather
import opportunities

ROOT = Path(__file__).resolve().parent


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
        hours = []
        for offset in range(7):
            for hour in (18,):
                hours.append({
                    "is_past": False,
                    "local_date": f"2026-11-{5 + offset:02d}",
                    "time": f"2026-11-{5 + offset:02d} 18:00",
                    "time_utc": f"2026-11-{5 + offset:02d}T{hour:02d}:00:00Z",
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
        self.assertEqual([d["date"] for d in days],
                         [f"2026-11-{5 + i:02d}" for i in range(7)])
        # The first far day (offset 3 => 2026-11-08) carries at least one card.
        far = next(d for d in days if d["date"] == "2026-11-08")
        self.assertIn("tw-018-P02", far["opportunities"])
        self.assertEqual(far["all"]["opportunity_id"], "tw-018-P02")

    def test_regenerated_region_snapshots_have_seven_daily_entries(self):
        for region, count in (("tw", 85), ("jp", 36), ("us", 96)):
            data = json.loads((ROOT / f"{region}_weather.json").read_text(encoding="utf-8"))
            self.assertEqual(len(data["spots"]), count)
            for spot in data["spots"]:
                self.assertEqual(len(spot.get("daily") or []), 7,
                                 f"{region} {spot['spot_id']} daily != 7")

    def test_first_far_day_2026_11_08_has_at_least_one_card_per_region(self):
        for region in ("tw", "jp", "us"):
            data = json.loads((ROOT / f"{region}_weather.json").read_text(encoding="utf-8"))
            cards = [
                spot["spot_id"]
                for spot in data["spots"]
                for day in (spot.get("daily") or [])
                if day["date"] == "2026-11-08"
                and (day.get("all") or {}).get("score") is not None
            ]
            self.assertGreaterEqual(len(cards), 1,
                                    f"{region} has no 2026-11-08 card")


if __name__ == "__main__":
    unittest.main()
