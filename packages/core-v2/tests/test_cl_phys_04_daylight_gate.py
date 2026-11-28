"""CL-PHYS-04: the daylight gate for daytime-only subjects + 內洞 venue hours.

Defect (live bundle 2026-11-28T08:22:45Z): tw-151-P01 內洞三層瀑布 (waterfall)
published good_hours 16:35–23:00 on 2026-11-28 and 00:00–06:00 on 11-29. Sunset
at that latitude/date is ~17:05 local, so those were pitch-black hours. The
waterfall template says "light is not gated" on purpose (soft overcast light is
fine for a waterfall) and no evaluation-layer gate asked whether the sun was UP.

Rule under test (owner ruling, CL-PHYS-04): a daytime-only genre's hour can
only be satisfied when the solar altitude at the hour bucket's START is
>= -6 deg (civil twilight or brighter); altitude < -6 deg fails the hour.
Night/dusk genres are untouched. ONE shared predicate: solar_altitude_deg ->
daylight_hour_state -> the EVALGATE-daylight-only phys gate.

Every fixture is a fixed coordinate + fixed UTC instants — no live clock and no
provider call.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)

# 內洞國家森林遊樂區 (tw-151-P01) — the verified camera geometry of the ticket.
WATERFALL_LAT, WATERFALL_LON = 24.8165785, 121.5478222
# 大雪山 (tw-140-P03) — a star_trails subject used to prove no over-reach.
NIGHT_LAT, NIGHT_LON = 24.5242406, 121.6228895
LOCAL = timezone(timedelta(hours=8))


def available(value):
    return {"value": value, "state": "AVAILABLE", "reason_code": None}


def local_instant(day, hour, base=(2026, 11, 28)):
    """UTC instant of a local (UTC+8) hour bucket start."""
    return datetime(day[0], day[1], day[2], hour, 0, tzinfo=LOCAL).astimezone(
        timezone.utc)


def daylight_artifact(start_utc, hours, values_factory):
    """Stubbed Open-Meteo artifact: PASSING weather at every hour.

    Only the weather cells the gates read are present; nothing here is
    night-time aware — that is the gate's job.
    """
    rows = []
    for index in range(hours):
        rows.append({
            "valid_at_utc": (start_utc + timedelta(hours=index))
            .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "values": values_factory(),
        })
    return {
        "adapter_version": "open-meteo-batch-0.1", "provider": "open-meteo",
        "place_coordinate": {"latitude": WATERFALL_LAT, "longitude": WATERFALL_LON},
        "grid": {"latitude": round(WATERFALL_LAT, 2),
                 "longitude": round(WATERFALL_LON, 2), "elevation_m": 230.0},
        "retrieved_at_utc": start_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": [
            {"source_url": "stub://forecast", "source_sha256": "0" * 64,
             "kind": "forecast", "fields": []},
            {"source_url": "stub://air-quality", "source_sha256": "0" * 64,
             "kind": "air_quality", "fields": []}],
        "freshness_policy": {}, "notes": {},
        "hours": rows,
    }


def clear_weather():
    """Every weather condition those subjects carry passes: no cloud, dry."""
    return {
        "temperature_2m": available(12.0),
        "dew_point_2m": available(2.0),
        "relative_humidity_2m": available(55.0),
        "cloud_cover_low": available(5.0),
        "cloud_cover_mid": available(5.0),
        "cloud_cover_high": available(5.0),
        "cloud_cover_total": available(5.0),
        "wind_speed_10m": available(2.0),
        "visibility": available(20.0),
        "precipitation": available(0.0),
        "precipitation_probability": available(0.0),
        "relative_humidity_925hpa": available(55.0),
        "relative_humidity_850hpa": available(50.0),
        "wind_speed_850hpa": available(3.0),
        "aod_550nm": available(0.1),
        "cloud_cover_mid_and_high": available(5.0),
    }


class DaylightPredicateTests(unittest.TestCase):
    """The single predicate, at its boundary and when geometry is missing."""

    def test_altitude_is_computed_from_coordinate_and_instant(self):
        # 2026-11-28 16:00 local: sun well up; 18:00 local: well past civil
        # twilight. Assert the values the gate actually judges on.
        up = eb.daylight_hour_state(local_instant((2026, 11, 28), 16),
                                    WATERFALL_LAT, WATERFALL_LON)
        dark = eb.daylight_hour_state(local_instant((2026, 11, 28), 18),
                                      WATERFALL_LAT, WATERFALL_LON)
        self.assertEqual(up["state"], "AVAILABLE")
        self.assertEqual(up["value"], "daylight")
        self.assertGreater(up["sun_altitude_deg"], 5.0)
        self.assertEqual(dark["value"], "dark")
        self.assertLess(dark["sun_altitude_deg"], -6.0)

    def test_civil_twilight_floor_is_minus_six_degrees(self):
        self.assertEqual(eb.DAYLIGHT_MIN_ALTITUDE_DEG, -6.0)
        # 17:00 local on 11-28 sits at the horizon (+0.02 deg): civil twilight
        # or brighter, so the hour is NOT closed by this gate.
        cell = eb.daylight_hour_state(local_instant((2026, 11, 28), 17),
                                      WATERFALL_LAT, WATERFALL_LON)
        self.assertGreaterEqual(cell["sun_altitude_deg"], -6.0)
        self.assertEqual(cell["value"], "daylight")

    def test_missing_coordinate_is_unknown_not_daylight(self):
        cell = eb.daylight_hour_state(local_instant((2026, 11, 28), 12),
                                      None, WATERFALL_LON)
        self.assertEqual(cell["state"], "UNKNOWN")
        self.assertEqual(cell["reason_code"], "SOLAR_ALTITUDE_UNAVAILABLE")
        self.assertIsNone(eb.solar_altitude_deg(local_instant((2026, 11, 28), 12),
                                                "24.8", 121.5))

    def test_gate_verdict_fails_below_the_floor_and_passes_above(self):
        dark = {"daylight_state": {"state": "AVAILABLE", "value": "dark",
                                   "sun_altitude_deg": -12.71}}
        light = {"daylight_state": {"state": "AVAILABLE", "value": "daylight",
                                    "sun_altitude_deg": 12.14}}
        verdict, detail = eb.phys_gate_verdict(eb.DAYLIGHT_GATE, dark,
                                               local_start_min=18 * 60)
        self.assertEqual(verdict, "FAIL")
        self.assertIn("DAYLIGHT_SUN_BELOW_HORIZON", detail)
        self.assertIn("-12.71", detail)
        verdict, detail = eb.phys_gate_verdict(eb.DAYLIGHT_GATE, light,
                                               local_start_min=16 * 60)
        self.assertEqual(verdict, "PASS")
        self.assertIn("12.14", detail)

    def test_uncomputable_altitude_is_unknown_never_a_pass(self):
        self.assertEqual(
            eb.phys_gate_verdict(eb.DAYLIGHT_GATE, {}, local_start_min=600)[0],
            "UNKNOWN")


class GenreScopeTests(unittest.TestCase):
    """The gate is injected for daytime-only genres and for nothing else."""

    DAYTIME = ("waterfall", "seasonal_plant", "mountain_view",
               "geological_landform", "misty_forest", "reflection", "overlook")
    NIGHT = ("night_sky", "star_trails", "moonlit_scene", "city_night",
             "blue_hour_city", "aurora", "sunset", "sunrise", "golden_hour",
             "alpenglow", "firefly", "blue_tears")

    def test_mandated_daytime_genres_are_gated(self):
        for genre in self.DAYTIME:
            self.assertIn(genre, eb.DAYLIGHT_ONLY_GENRES)
            gates = eb.daylight_gates_for({"genre_template": genre})
            self.assertEqual([g["metric"] for g in gates],
                             [eb.DAYLIGHT_GATE_METRIC], genre)

    def test_night_and_dusk_genres_are_never_gated(self):
        for genre in self.NIGHT:
            self.assertNotIn(genre, eb.DAYLIGHT_ONLY_GENRES)
            self.assertEqual(eb.daylight_gates_for({"genre_template": genre}),
                             [], genre)

    def test_genre_sets_are_disjoint(self):
        self.assertEqual(eb.DAYLIGHT_ONLY_GENRES
                         & eb.NIGHT_OR_LIGHT_WINDOW_GENRES, frozenset())

    def test_unknown_genre_gets_no_gate(self):
        self.assertEqual(eb.daylight_gates_for({}), [])
        self.assertEqual(
            eb.daylight_gates_for({"genre_template": "not_a_genre"}), [])


class RealPathWaterfallTests(unittest.TestCase):
    """tw-151-P01 through evaluate_batch.main() with a stubbed provider.

    The fixture's weather PASSES at every hour, so before CL-PHYS-04 the
    night hours were good hours (the reported defect).
    """

    HOURS = 72
    START = datetime(2026, 11, 27, 16, 0, tzinfo=timezone.utc)  # 11-28 00:00 local
    OID = "tw-151-P01"

    def run_main(self):
        scratch = Path(tempfile.mkdtemp(prefix="cl-phys04-"))
        artifact = daylight_artifact(self.START, self.HOURS, clear_weather)

        def fake_fetch(lat, lon, forecast_hours):
            return artifact

        def fake_trailing(lat, lon, past_hours=72):
            # 0.2 mm/h * 72 h = 14.4 mm -> river_flow_state "mid" (shootable).
            return [0.2] * past_hours, "stub://past", "0" * 64

        out = scratch / "bundle.json"
        argv = ["evaluate_batch.py", "--forecast-hours", str(self.HOURS),
                "--only-place-id", "tw-151", "--out", str(out),
                "--archive", str(scratch / "archive"),
                "--details-dir", str(scratch / "details")]
        with mock.patch.object(eb.adapter, "fetch_place", fake_fetch), \
                mock.patch.object(eb.adapter, "fetch_trailing_precipitation",
                                  fake_trailing), \
                mock.patch.object(sys, "argv", argv):
            eb.main()
        bundle = json.loads(out.read_text(encoding="utf-8"))
        return next(o for place in bundle["places"]
                    for o in place["opportunities"] if o["opportunity_id"] == self.OID)

    def day(self, opportunity, iso_date):
        return next(d for d in opportunity["days"] if d["local_date"] == iso_date)

    def altitude_table(self, iso_date, hours):
        day = datetime.fromisoformat(iso_date)
        rows = []
        for hour in hours:
            instant = datetime(day.year, day.month, day.day, hour, 0,
                               tzinfo=LOCAL).astimezone(timezone.utc)
            cell = eb.daylight_hour_state(instant, WATERFALL_LAT, WATERFALL_LON)
            rows.append(f"{hour:02d}:00 alt={cell.get('sun_altitude_deg')}deg "
                        f"({cell['value']})")
        return "; ".join(rows)

    def test_night_hours_18_to_23_are_not_good_hours_on_1128(self):
        opportunity = self.run_main()
        good = self.day(opportunity, "2026-11-28")["good_hours"]
        self.assertTrue(good, "fixture should yield daytime good hours")
        night = {"18:00", "19:00", "20:00", "21:00", "22:00", "23:00"}
        self.assertFalse(night & set(good),
                         f"night hours leaked into good_hours: {good}; "
                         + self.altitude_table("2026-11-28", range(16, 24)))
        self.assertIn("12:00", good)

    def test_early_hours_0000_to_0600_are_not_good_hours_on_1129(self):
        opportunity = self.run_main()
        good = self.day(opportunity, "2026-11-29")["good_hours"]
        early = {f"{h:02d}:00" for h in range(0, 7)}
        self.assertFalse(early & set(good),
                         f"dark hours leaked into good_hours: {good}; "
                         + self.altitude_table("2026-11-29", range(0, 7)))

    def test_venue_window_keeps_daylight_hours_and_blocks_the_close(self):
        opportunity = self.run_main()
        good = set(self.day(opportunity, "2026-11-28")["good_hours"])
        # 內洞 opens 08:00 and closes 17:00; the table is half-open [open, close),
        # so the 17:00 bucket start is already closed while 08:00–16:00 are in.
        for hour in range(8, 16):
            self.assertIn(f"{hour:02d}:00", good, sorted(good))
        # The 16:00 bucket qualifies and carries the golden-hour precise stamp.
        self.assertTrue(any(h.startswith("16:") for h in good), sorted(good))
        self.assertNotIn("17:00", good)
        self.assertFalse({f"{h:02d}:00" for h in range(17, 24)} & good)
        self.assertFalse({f"{h:02d}:00" for h in range(0, 8)} & good)

    def test_the_gate_is_injected_into_the_opportunity_conditions(self):
        opportunity = self.run_main()
        day = self.day(opportunity, "2026-11-28")
        metrics = [c["metric"] for c in day["conditions"]]
        self.assertIn(eb.DAYLIGHT_GATE_METRIC, metrics)


class RealPathNightGenreTests(unittest.TestCase):
    """star_trails at 大雪山 still has satisfied hours well after dark."""

    HOURS = 10
    START = datetime(2026, 11, 8, 13, 0, tzinfo=timezone.utc)  # 11-08 21:00 local
    OID = "tw-140-P03"

    def run_main(self):
        scratch = Path(tempfile.mkdtemp(prefix="cl-phys04-night-"))
        artifact = daylight_artifact(self.START, self.HOURS, clear_weather)
        artifact["place_coordinate"] = {"latitude": NIGHT_LAT,
                                        "longitude": NIGHT_LON}
        artifact["grid"] = {"latitude": round(NIGHT_LAT, 2),
                            "longitude": round(NIGHT_LON, 2),
                            "elevation_m": 1950.0}

        out = scratch / "bundle.json"
        argv = ["evaluate_batch.py", "--forecast-hours", str(self.HOURS),
                "--only-place-id", "tw-140", "--out", str(out),
                "--archive", str(scratch / "archive"),
                "--details-dir", str(scratch / "details")]
        with mock.patch.object(eb.adapter, "fetch_place",
                               lambda lat, lon, hours: artifact), \
                mock.patch.object(sys, "argv", argv):
            eb.main()
        bundle = json.loads(out.read_text(encoding="utf-8"))
        return next(o for place in bundle["places"]
                    for o in place["opportunities"] if o["opportunity_id"] == self.OID)

    def test_star_trails_keeps_satisfied_hours_after_dark(self):
        opportunity = self.run_main()
        good = set(opportunity["days"][0]["good_hours"])
        # 21:00 local start + 10 h on a new-moon night (illumination < 1 %):
        # the deep-night hours are legitimate star-trail windows.
        self.assertTrue(good, opportunity["days"][0]["state"])
        self.assertTrue({"22:00", "23:00", "00:00", "01:00"} & good, good)
        for day in opportunity["days"]:
            metrics = [c["metric"] for c in day["conditions"]]
            self.assertNotIn(eb.DAYLIGHT_GATE_METRIC, metrics)


class VenueHoursEntryTests(unittest.TestCase):
    """The owner-asserted 內洞 window, read from the shipped table."""

    def setUp(self):
        self.venues = eb.load_venue_hours()
        self.entry = self.venues["tw-151-P01"]

    def test_entry_shape_and_provenance(self):
        self.assertEqual(self.entry["open"], "08:00")
        self.assertEqual(self.entry["close"], "17:00")
        self.assertEqual(self.entry["source_kind"], "owner_asserted")
        self.assertEqual(self.entry["confirmed_by"], "CL-PHYS-04")
        self.assertEqual(self.entry["place_id"], "tw-151")
        # The owner supplied the hours in the ticket: no URL is invented.
        self.assertNotIn("http", self.entry["source"].lower())
        self.assertIn("CL-PHYS-04", self.entry["source"])

    def test_gate_opens_12_to_17_and_closes_from_18(self):
        gate = eb.policy_gates_for("tw-151-P01", {}, self.venues)[0]
        self.assertEqual(gate["metric"], eb.VENUE_HOURS_METRIC)
        for hour in (12, 13, 14, 15, 16):
            self.assertEqual(
                eb.phys_gate_verdict(gate, {}, local_start_min=hour * 60)[0],
                "PASS", hour)
        # [open, close): the 17:00 bucket start is the close instant.
        for hour in (17, 18, 19, 20, 21, 22, 23):
            self.assertEqual(
                eb.phys_gate_verdict(gate, {}, local_start_min=hour * 60)[0],
                "FAIL", hour)
        self.assertEqual(
            eb.phys_gate_verdict(gate, {}, local_start_min=7 * 60)[0], "FAIL")


if __name__ == "__main__":
    unittest.main()
