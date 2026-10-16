"""W3 negative regressions for malformed NOAA /points geometry.

Deterministic TEST_FIXTURE inputs; these tests never claim live NOAA evidence.
"""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import unittest

ADAPTER = Path(__file__).resolve().parents[1] / "adapters/nws_gridpoint.py"
spec = spec_from_file_location("nws_gridpoint_geometry_regression", ADAPTER)
nws = module_from_spec(spec)
spec.loader.exec_module(nws)

POINTS_URL = "https://api.weather.gov/points/47.6,-122.33"
GRID_URL = "https://api.weather.gov/gridpoints/SEW/100,100"


class MalformedPointsGeometry(unittest.TestCase):
    def test_non_object_geometry_fails_closed_without_exception(self):
        for geometry in ("Point", ["Point"], 1, True, None, {}, []):
            with self.subTest(geometry=repr(geometry)):
                points = {
                    "geometry": geometry,
                    "properties": {
                        "gridId": "SEW", "gridX": 100, "gridY": 100,
                        "forecastGridData": GRID_URL,
                    },
                }
                grid = {"properties": {
                    "updateTime": "2026-10-13T12:00:00Z",
                    "skyCover": {"uom": "wmoUnit:percent", "values": [
                        {"validTime": "2026-10-13T14:00:00Z/PT3H", "value": 46}
                    ]},
                }}
                raw = json.dumps(grid, sort_keys=True).encode("utf-8")
                result = nws.normalize_fixture(
                    points, grid, raw,
                    points_url=POINTS_URL, grid_url=GRID_URL,
                    field="skyCover", valid_at="2026-10-13T15:00:00Z",
                    retrieved_at="2026-10-13T13:00:00Z",
                    coordinate_source="Seattle representative location, not Camera GPS",
                    freshness_policy={
                        "approved": True,
                        "source": "W3 deterministic test-only freshness policy",
                        "max_age_seconds": 7200,
                    },
                )
                self.assertEqual("UNKNOWN", result["source_state"])
                self.assertIsNone(result["record"])
                self.assertEqual("NOT_EVALUABLE", result["photography_verdict"])
                self.assertFalse(result["live_recommendation"])
                self.assertIn("POINTS_COORDINATE_MISMATCH", result["reasons"])


if __name__ == "__main__":
    unittest.main()
