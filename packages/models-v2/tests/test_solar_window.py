"""Independent W3 solar WINDOW benchmarks (not camera GPS or favorable scores).

Reference almanacs, retrieved 2026-10-13:
https://www.timeanddate.com/sun/taiwan/taipei?month=10&year=2026
https://www.timeanddate.com/sun/usa/seattle?month=10&year=2026
https://www.timeanddate.com/sun/usa/fairbanks?month=10&year=2026
https://www.timeanddate.com/sun/japan/tokyo?month=6&year=2026
https://www.timeanddate.com/sun/usa/seattle?month=3&year=2026
Published values are rounded to minute; ±5 minute numeric tolerance does
not imply any actual mountain horizon or atmospheric accuracy.
"""
from datetime import date, datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

MODEL = Path(__file__).resolve().parents[1] / "solar_window.py"
spec = spec_from_file_location("chase_solar_window", MODEL)
solar = module_from_spec(spec)
spec.loader.exec_module(solar)
NOW = datetime(2026, 10, 13, tzinfo=timezone.utc)


def request(day="2026-10-13", tz="Asia/Taipei", lat=25.033, lon=121.565):
    return {
        "schema_version": "0.1.0", "request_id": "M6a-numeric-almanac",
        "local_date": day, "time_zone": tz,
        "observer": {
            "coordinate_role": "representative_place_sample", "lat": lat, "lon": lon,
            "coordinate_source": "Named-city numerical reference, not a camera/arrival GPS",
            "uncertainty_m": None, "altitude_m": None},
        "model": {"model_id": solar.MODEL_ID,
                  "algorithm_version": solar.ALGORITHM_VERSION,
                  "horizon_assumption": "ideal_unobstructed",
                  "sun_altitude_crossing_deg": -0.833},
    }


def local_time(result, event):
    return datetime.fromisoformat(result[event]["time_local"]).strftime("%H:%M")


def delta_minutes(actual, expected):
    h, m = map(int, actual.split(":"))
    eh, em = map(int, expected.split(":"))
    return abs((h * 60 + m) - (eh * 60 + em))


class SolarWindowModel(unittest.TestCase):
    def solar(self, *args, **kwargs):
        result = solar.compute_solar_window(request(*args, **kwargs), computed_at=NOW)
        self.assertFalse(result["recommendation_eligible"])
        self.assertEqual("NOT_EVALUABLE", result["photography_verdict"])
        self.assertEqual("WINDOW", result["capability"])
        self.assertEqual(set(result["limitations_i18n"]), {"zh-TW", "en", "ja"})
        return result

    def test_taipei_october_almanac(self):
        result = self.solar()
        self.assertLessEqual(delta_minutes(local_time(result, "sunrise"), "05:50"), 5)
        self.assertLessEqual(delta_minutes(local_time(result, "sunset"), "17:28"), 5)

    def test_seattle_october_almanac(self):
        result = self.solar("2026-10-13", "America/Los_Angeles", 47.6062, -122.3321)
        self.assertLessEqual(delta_minutes(local_time(result, "sunrise"), "07:25"), 5)
        self.assertLessEqual(delta_minutes(local_time(result, "sunset"), "18:24"), 5)

    def test_fairbanks_october_almanac(self):
        result = self.solar("2026-10-13", "America/Anchorage", 64.8378, -147.7164)
        self.assertLessEqual(delta_minutes(local_time(result, "sunrise"), "08:38"), 5)
        self.assertLessEqual(delta_minutes(local_time(result, "sunset"), "18:34"), 5)

    def test_tokyo_solstice_almanac(self):
        result = self.solar("2026-06-21", "Asia/Tokyo", 35.68, 139.76)
        self.assertLessEqual(delta_minutes(local_time(result, "sunrise"), "04:25"), 5)
        self.assertLessEqual(delta_minutes(local_time(result, "sunset"), "19:00"), 5)

    def test_iana_dst_spring_and_fall(self):
        spring = self.solar("2026-03-08", "America/Los_Angeles", 47.6062, -122.3321)
        fall = self.solar("2026-11-01", "America/Los_Angeles", 47.6062, -122.3321)
        self.assertEqual("-07:00", spring["sunrise"]["time_local"][-6:])
        self.assertEqual("-08:00", fall["sunrise"]["time_local"][-6:])
        self.assertLessEqual(delta_minutes(local_time(spring, "sunrise"), "07:35"), 5)
        self.assertLessEqual(delta_minutes(local_time(spring, "sunset"), "19:04"), 5)
        for result in (spring, fall):
            for event in ("sunrise", "sunset"):
                utc = datetime.fromisoformat(result[event]["time_utc"].replace("Z", "+00:00"))
                local = datetime.fromisoformat(result[event]["time_local"])
                self.assertEqual(utc, local)
                self.assertEqual(date.fromisoformat(result["local_date"]), local.date())

    def test_polar_day_night_are_no_event_not_fabricated(self):
        summer = self.solar("2026-06-21", "Arctic/Longyearbyen", 78.22, 15.65)
        winter = self.solar("2026-12-21", "America/Anchorage", 71.29, -156.79)
        for result, state in ((summer, "POLAR_DAY"), (winter, "POLAR_NIGHT")):
            self.assertEqual(state, result["polar_state"])
            for event in ("sunrise", "sunset"):
                self.assertEqual("NO_EVENT", result[event]["status"])
                self.assertEqual(state, result[event]["reason"])
                self.assertIsNone(result[event]["time_local"])
                self.assertIsNone(result[event]["time_utc"])

    def test_international_date_line_has_different_utc_civil_date(self):
        result = self.solar("2026-06-21", "Pacific/Kiritimati", 1.87, -157.4)
        self.assertEqual("2026-06-21", result["sunrise"]["time_local"][:10])
        self.assertEqual("2026-06-20", result["sunrise"]["time_utc"][:10])
        self.assertTrue(result["sunrise"]["time_local"].endswith("+14:00"))

    def test_unknown_camera_does_not_invent_location(self):
        item = request()
        item["observer"].update({"coordinate_role": "unknown", "lat": None,
                                "lon": None, "coordinate_source": None})
        result = solar.compute_solar_window(item, computed_at=NOW)
        self.assertIsNone(result["observer"]["lat"])
        self.assertFalse(result["recommendation_eligible"])
        for event in ("sunrise", "sunset"):
            self.assertEqual("UNKNOWN", result[event]["status"])
            self.assertEqual("UNKNOWN_LOCATION", result[event]["reason"])
            self.assertIsNone(result[event]["time_utc"])

    def test_invalid_tz_date_coordinates_source_and_model_fail_closed(self):
        bad = []
        q = request(); q["time_zone"] = "America/NotARealCity"; bad.append(q)
        q = request(); q["local_date"] = "2026-02-30"; bad.append(q)
        q = request(); q["observer"]["lat"] = 100; bad.append(q)
        q = request(); q["observer"]["coordinate_source"] = ""; bad.append(q)
        q = request(); q["model"]["algorithm_version"] = "fabricated-model"; bad.append(q)
        q = request(); q["model"]["sun_altitude_crossing_deg"] = -6; bad.append(q)
        q = request(); q["unexpected_camera_gps"] = [25.0, 121.0]; bad.append(q)
        for item in bad:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    solar.compute_solar_window(item, computed_at=NOW)

    def test_computation_time_does_not_change_events_or_accept_access_gate(self):
        item = request()
        a = solar.compute_solar_window(item, computed_at=NOW)
        b = solar.compute_solar_window(item, computed_at=NOW.replace(hour=12))
        self.assertEqual(a["sunrise"], b["sunrise"])
        self.assertEqual(a["sunset"], b["sunset"])
        self.assertNotEqual(a["computed_at_utc"], b["computed_at_utc"])
        item["access_status"] = "CLOSED"
        with self.assertRaises(ValueError):
            solar.compute_solar_window(item, computed_at=NOW)
        self.assertEqual("NOT_EVALUABLE", a["photography_verdict"])


if __name__ == "__main__":
    unittest.main()
