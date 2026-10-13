"""W1 M6b NWS gridpoint schema-only fail-closed tests; not a live network verification."""
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = Path(__file__).resolve().parents[1] / "schema/weather-source-record-v0.1.schema.json"


def record():
    return {
        "schema_version": "0.1.0", "record_id": "Seattle-skyCover-one-interval",
        "source_kind": "FORECAST", "provider": "NOAA_NWS",
        "source_url": "https://api.weather.gov/gridpoints/SEW/100,100",
        "mapping_url": "https://api.weather.gov/points/47.6,-122.33",
        "source_sha256": "a" * 64, "source_update_time_utc": "2026-10-13T12:00:00Z",
        "retrieved_at_utc": "2026-10-13T12:05:00Z",
        "provider_issued_at_utc": None, "provider_run_id": None,
        "grid": {
            "office": "SEW", "grid_x": 100, "grid_y": 100,
            "sample_lat": 47.6, "sample_lon": -122.33,
            "coordinate_role": "representative_place_sample",
            "coordinate_source": "Seattle area research reference, NOT tripod GPS",
            "coordinate_uncertainty_m": None, "native_resolution_m": None
        },
        "field": "skyCover", "uom": "wmoUnit:percent", "raw_value": 50,
        "valid_from_utc": "2026-10-13T14:00:00Z",
        "valid_until_utc": "2026-10-13T16:00:00Z",
        "retrieval_mode": "TEST_FIXTURE", "data_state": "RAW_ONLY",
        "calibration_status": "UNVALIDATED", "recommendation_eligible": False,
        "photography_verdict": "NOT_EVALUABLE", "limitations_i18n": {
            "zh-TW": "美國網格資料；非合法攝影機位、即時拍照預測。",
            "en": "US forecast grid, not a surveyed camera point or photography prediction.",
            "ja": "米国の格子予報であり、撮影位置や撮影適性の保証ではない。"
        }
    }


class WeatherSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        cls.validator = Draft202012Validator(schema, format_checker=FormatChecker())

    def fail(self, payload):
        self.assertTrue(list(self.validator.iter_errors(payload)), payload)

    def test_valid_raw_record_with_frozen_no_score_and_locale_contract(self):
        self.assertFalse(list(self.validator.iter_errors(record())))

    def test_fabricated_forecast_issued_time_model_run_and_favorable_rejected(self):
        for name, value in [
            ("provider_issued_at_utc", "2026-10-13T12:00:00Z"),
            ("provider_run_id", "GFS-06Z"),
            ("recommendation_eligible", True),
            ("photography_verdict", "FAVORABLE"),
            ("data_state", "APPROVED"),
            ("calibration_status", "VALIDATED")
        ]:
            with self.subTest(name=name):
                x = record(); x[name] = value; self.fail(x)

    def test_missing_or_invented_camera_grid_location_rejected(self):
        for key, value in [
            ("coordinate_role", "verified_camera_reference"),
            ("native_resolution_m", 2500),
            ("sample_lat", 95),
            ("coordinate_source", ""),
            ("grid_x", -1)
        ]:
            with self.subTest(key=key):
                x = record(); x["grid"][key] = value; self.fail(x)
        x = record(); x["grid"]["camera_gps"] = [47.6, -122.3]; self.fail(x)

    def test_source_url_hash_and_locale_fail_closed(self):
        for k, bad in [
            ("source_url", "https://api.weather.gov.evil.com/gridpoints/SEW/100,100"),
            ("source_url", "http://api.weather.gov/gridpoints/SEW/100,100"),
            ("mapping_url", "https://api.weather.gov/alerts"),
            ("source_sha256", "not-a-sha256")
        ]:
            with self.subTest(key=k):
                x = record(); x[k] = bad; self.fail(x)
        x = record(); del x["limitations_i18n"]["ja"]; self.fail(x)
        x = record(); x["unexpected_score"] = 10; self.fail(x)

    def test_invalid_time_unit_raw_source_or_boolean_rejected(self):
        for k, bad in [
            ("valid_from_utc", "2026-10-13T14:00:00"),
            ("source_update_time_utc", "yesterday"),
            ("raw_value", "0"),
            ("uom", ""),
            ("source_kind", "OBSERVATION"),
            ("provider", "GFS")
        ]:
            with self.subTest(key=k):
                x = record(); x[k] = bad; self.fail(x)
        # The W3 parser also checks UTC chronological order, field-specific unit
        # consistency and nonfinite floats, beyond Draft2020-12 structural checks.


if __name__ == "__main__":
    unittest.main()
