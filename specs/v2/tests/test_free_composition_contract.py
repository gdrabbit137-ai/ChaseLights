"""Synthetic free-composition regression; structural validity is not live approval."""
import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from validate_contract import validate_record

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema/opportunity-v2.1.schema.json").read_text(encoding="utf-8"))
BASE = json.loads((ROOT / "tests/fixtures/valid_aurora_draft.json").read_text(encoding="utf-8"))

def synthetic_free_composition():
    record = copy.deepcopy(BASE)
    record["opportunity_id"] = "test-only:free-composition-research-only"
    record["camera_contexts"] = [{
        "id": "test-only:camera-area", "kind": "area",
        "geometry": {"kind": "area", "status": "unknown", "geojson": None},
        "verification_status": "unknown", "evidence_refs": [],
    }]
    record["observation_relations"] = []
    record["condition_contract"]["conditions"] = [{
        "id": "test-only:regional-weather-guidance", "role": "QUALITY",
        "domain": "WEATHER", "evaluation_mode": "GUIDANCE",
        "capability": "CONDITIONS", "metric": "test-only:regional-weather-input",
        "threshold": None, "model_binding": None,
        "unknown_policy": "propagate_unknown", "claim_refs": [],
        "validation_status": "provisional",
    }]
    return record

class FreeCompositionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Draft202012Validator.check_schema(SCHEMA)
        cls.validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

    def test_area_without_fixed_camera_gps_or_relation_is_structurally_valid(self):
        record = synthetic_free_composition()
        self.assertEqual(validate_record(record, SCHEMA), [])
        self.assertIsNone(record["camera_contexts"][0]["geometry"]["geojson"])
        self.assertEqual(record["observation_relations"], [])

    def test_route_and_mobile_platform_do_not_require_invented_track(self):
        for kind, geometry_kind in (("route", "polyline"), ("mobile_platform", "none")):
            with self.subTest(kind=kind):
                record = synthetic_free_composition()
                record["camera_contexts"][0]["kind"] = kind
                record["camera_contexts"][0]["geometry"] = {
                    "kind": geometry_kind, "status": "unknown", "geojson": None,
                }
                self.assertEqual(validate_record(record, SCHEMA), [])

    def test_unknown_geometry_does_not_invalidate_independent_weather_contract(self):
        record = synthetic_free_composition()
        record["condition_contract"]["conditions"].append({
            "id": "test-only:alignment-unknown", "role": "REQUIRED",
            "domain": "GEOMETRY_COMPOSITION", "evaluation_mode": "VERIFY",
            "capability": "CONDITIONS", "metric": "test-only:alignment",
            "threshold": None, "model_binding": None,
            "unknown_policy": "propagate_unknown", "claim_refs": [],
            "validation_status": "unvalidated",
        })
        self.assertEqual(validate_record(record, SCHEMA), [])
        self.assertEqual(record["condition_contract"]["conditions"][0]["domain"], "WEATHER")
        self.assertEqual(record["condition_contract"]["conditions"][1]["domain"], "GEOMETRY_COMPOSITION")

    def test_negative_verified_navigation_without_arrival_proof_is_rejected(self):
        record = synthetic_free_composition()
        record["navigation_targets"] = [{
            "id": "test-only:unverified-arrival", "status": "verified",
            "target_type": "street_access", "evidence_refs": [],
        }]
        errors = validate_record(record, SCHEMA)
        self.assertTrue(errors)
        self.assertTrue(any("lat" in e and "required" in e for e in errors), errors)
        self.assertTrue(any("lon" in e and "required" in e for e in errors), errors)

    def test_negative_unknown_required_condition_cannot_ignore_unknown(self):
        record = synthetic_free_composition()
        record["condition_contract"]["conditions"][0]["role"] = "REQUIRED"
        record["condition_contract"]["conditions"][0]["unknown_policy"] = "ignore"
        errors = validate_record(record, SCHEMA)
        self.assertTrue(errors)
        self.assertTrue(any("propagate_unknown" in e for e in errors), errors)

    def test_negative_geometry_envelope_still_required_not_precise_gps(self):
        record = synthetic_free_composition()
        del record["camera_contexts"][0]["geometry"]
        errors = validate_record(record, SCHEMA)
        self.assertTrue(errors)
        self.assertTrue(any("geometry" in e and "required" in e for e in errors), errors)

if __name__ == "__main__":
    unittest.main()
