"""Tests for the deterministic W4 solar pilot artifact builder."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOL_PATH = ROOT / "packages/models-v2/tools/build_solar_pilot.py"
ARTIFACT_PATH = ROOT / "apps/web-v2/solar-window-tw036.json"
sys.path.insert(0, str(ROOT / "packages/models-v2"))

_spec = importlib.util.spec_from_file_location("build_solar_pilot", TOOL_PATH)
build_solar_pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_solar_pilot)

COMPUTED_AT = datetime(2026, 10, 23, 18, 5, 0, tzinfo=timezone.utc)


class SolarPilotToolTests(unittest.TestCase):
    def test_build_is_deterministic_given_fixed_inputs(self):
        first = build_solar_pilot.build("2026-10-24", 14, COMPUTED_AT, "2025.3")
        second = build_solar_pilot.build("2026-10-24", 14, COMPUTED_AT, "2025.3")
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_committed_artifact_is_a_valid_research_bundle(self):
        artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(artifact["pilot_id"], "tw-036-solar-window-v0.1")
        self.assertEqual(artifact["place_id"], "tw-036")
        self.assertEqual(len(artifact["results"]), 14)
        self.assertEqual(artifact["data_state"], "RAW_ONLY")
        self.assertEqual(artifact["recommendation_eligible"], False)
        self.assertEqual(artifact["photography_verdict"], "NOT_EVALUABLE")
        self.assertEqual(artifact["observer"]["coordinate_role"], "representative_place_sample")
        self.assertEqual(artifact["time_zone"], "Asia/Taipei")
        for result in artifact["results"]:
            self.assertEqual(result["capability"], "WINDOW")
            self.assertEqual(result["recommendation_eligible"], False)
            self.assertEqual(result["observer"]["coordinate_role"], "representative_place_sample")
            self.assertEqual(result["time_zone"], "Asia/Taipei")
            if result["sunrise"]["status"] == "CALCULATED":
                self.assertTrue(result["sunrise"]["time_local"].startswith(result["local_date"]))
        self.assertIn("generated_at_utc", artifact["generation"])

    def test_every_committed_result_passes_the_pinned_result_schema(self):
        from solar_window import _schema_validate, RESULT_SCHEMA
        artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        for result in artifact["results"]:
            _schema_validate(result, RESULT_SCHEMA)

    def test_invalid_timezone_or_date_fails_closed(self):
        with self.assertRaises(Exception):
            build_solar_pilot.build("2026-13-40", 1, COMPUTED_AT, None)
        artifact = build_solar_pilot.build("2026-10-24", 1, COMPUTED_AT, None)
        self.assertEqual(artifact["window_days"], ["2026-10-24"])

    def test_no_network_access_is_needed(self):
        """The builder imports only local modules; this assertion documents
        that solar windows are deterministic local computations."""
        source = TOOL_PATH.read_text(encoding="utf-8")
        self.assertNotIn("urllib", source)
        self.assertNotIn("requests", source)
        self.assertNotIn("http", source.replace("https://json-schema", ""))


if __name__ == "__main__":
    unittest.main()
