"""M6a W1 solar WINDOW schema regressions — NOT a numeric ephemeris test."""
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"


def load(name):
    model = json.loads((SCHEMA / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(model)
    return Draft202012Validator(model, format_checker=FormatChecker())


REQUEST = "solar-window-request-v0.1.schema.json"
RESULT = "solar-window-result-v0.1.schema.json"


def request():
    return {
        "schema_version": "0.1.0",
        "request_id": "M6a-tw-082-20261013",
        "local_date": "2026-10-13",
        "time_zone": "Asia/Taipei",
        "observer": {
            "coordinate_role": "representative_place_sample",
            "lat": 23.93, "lon": 121.51,
            "coordinate_source": "Official tourism place-area research; not a tripod/arrival coordinate",
            "uncertainty_m": None, "altitude_m": None,
        },
        "model": {
            "model_id": "m6a-solar-window-prototype",
            "algorithm_version": "proposal-only-0.1",
            "horizon_assumption": "ideal_unobstructed",
            "sun_altitude_crossing_deg": -0.833,
        },
    }


def result():
    r = request()
    r.update({
        "capability": "WINDOW", "computed_at_utc": "2026-10-12T18:00:00Z",
        "polar_state": "NORMAL",
        "sunrise": {"status": "CALCULATED", "time_utc": "2026-10-12T22:00:00Z",
                    "time_local": "2026-10-13T06:00:00+08:00", "reason": None},
        "sunset": {"status": "UNKNOWN", "time_utc": None, "time_local": None,
                   "reason": "NO_VALIDATED_MODEL"},
        "recommendation_eligible": False, "photography_verdict": "NOT_EVALUABLE",
        "limitations_i18n": {
            "zh-TW": "區域日出時間估算，不代表實際地平線、雲量或攝影適合度。",
            "en": "Regional sunrise estimate, not verified horizon, cloud conditions or photographic suitability.",
            "ja": "地域の日の出時刻の推定であり、実際の地平線・雲や撮影適性の保証ではない。",
        }
    })
    return r


class SolarWindowContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_schema = load(REQUEST)
        cls.result_schema = load(RESULT)

    def test_valid_representative_request_without_triangulated_camera_gps(self):
        self.assertEqual([], list(self.request_schema.iter_errors(request())))
        r = request()
        r["observer"].update({"coordinate_role": "unknown", "lat": None,
                               "lon": None, "coordinate_source": None})
        self.assertEqual([], list(self.request_schema.iter_errors(r)))
        r["observer"]["lat"] = 23.93
        self.assertTrue(list(self.request_schema.iter_errors(r)))

    def test_missing_source_invalid_latlon_invalid_date_and_extra_fields_fail(self):
        for change in (
            {"observer": {**request()["observer"], "coordinate_source": ""}},
            {"observer": {**request()["observer"], "lat": 92}},
            {"observer": {**request()["observer"], "lon": 182}},
            {"local_date": "2026-02-30"},
            {"model": {**request()["model"], "sun_altitude_crossing_deg": 1}},
            {"invented_camera_azimuth_deg": 80},
        ):
            with self.subTest(change=change):
                r = request()
                r.update(change)
                self.assertTrue(list(self.request_schema.iter_errors(r)), change)

    def test_result_no_favorable_and_explicit_unknown_event(self):
        self.assertEqual([], list(self.result_schema.iter_errors(result())))
        for change in (
            {"recommendation_eligible": True},
            {"photography_verdict": "FAVORABLE"},
            {"capability": "PROBABILITY"},
            {"sunset": {"status": "CALCULATED", "time_utc": None,
                        "time_local": None, "reason": None}},
            {"sunset": {"status": "UNKNOWN", "time_utc": "2026-10-13T08:00:00Z",
                        "time_local": None, "reason": "TEST"}},
        ):
            with self.subTest(change=change):
                r = result()
                r.update(change)
                self.assertTrue(list(self.result_schema.iter_errors(r)), change)

    def test_polar_non_event_is_explicit_and_translations_mandatory(self):
        r = result()
        r["polar_state"] = "POLAR_DAY"
        r["sunrise"] = {"status": "NO_EVENT", "time_utc": None, "time_local": None,
                        "reason": "POLAR_DAY"}
        r["sunset"] = {"status": "NO_EVENT", "time_utc": None, "time_local": None,
                       "reason": "POLAR_DAY"}
        self.assertEqual([], list(self.result_schema.iter_errors(r)))
        r["limitations_i18n"].pop("ja")
        self.assertTrue(list(self.result_schema.iter_errors(r)))


if __name__ == "__main__":
    unittest.main()
