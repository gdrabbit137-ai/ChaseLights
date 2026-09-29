import json
import unittest
from pathlib import Path

from build_weathergrid_coverage_browser import build_coverage_browser_payload


class WeatherGridCoverageBrowserTest(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parent
        self.catalog = json.loads(
            (root / "runtime_catalog_v004_r4_2.json").read_text(encoding="utf-8")
        )
        self.registry = json.loads(
            (root / "weathergrid_coverage_registry_r4_2.json").read_text(encoding="utf-8")
        )

    def test_real_registry_builds_compact_browser_payload(self):
        payload = build_coverage_browser_payload(self.catalog, self.registry)
        by_spot = {spot["spot_id"]: spot for spot in payload["spots"]}

        self.assertIn("tw-034", by_spot)
        self.assertIn("tw-036", by_spot)
        self.assertIn("tw-019", by_spot)
        self.assertIn("tw-082", by_spot)

        qix = by_spot["tw-036"]
        self.assertEqual(qix["coverage_entry_count"], 2)
        self.assertGreater(qix["catalog_opportunity_count"], qix["coverage_entry_count"])
        self.assertFalse(qix["all_topics_complete"])

        by_opp = {
            op["opportunity_id"]: op
            for spot in payload["spots"]
            for op in spot["opportunities"]
        }
        p03 = by_opp["tw-036-P03"]
        self.assertTrue(p03["complete"])
        self.assertEqual(p03["status"], "provisional")
        self.assertEqual(len(p03["camera_zones"]), 1)
        self.assertEqual(p03["camera_zones"][0]["browser_exposure"], "generalized")
        self.assertAlmostEqual(p03["camera_zones"][0]["lat"], 24.031426)
        self.assertTrue(p03["subject_geometries"])

        liyu = by_opp["tw-082-P01"]
        self.assertFalse(liyu["complete"])
        self.assertEqual(liyu["status"], "needs_research")
        self.assertTrue(liyu["errors"])

    def test_camera_export_fails_closed_without_explicit_exposure(self):
        registry = {
            "schema_version": 1,
            "registry_version": "test",
            "entries": [
                {
                    "opportunity_id": "tw-036-P03",
                    "spot_id": "tw-036",
                    "weather_coverage": {
                        "schema_version": 1,
                        "status": "provisional",
                        "camera_zone_refs": ["tw-036-VP01"],
                        "subject_geometries": [
                            {
                                "subject_id": "test-subject",
                                "role": "primary_subject",
                                "geometry": {
                                    "type": "point",
                                    "lat": 24.2,
                                    "lon": 121.7,
                                },
                                "browser_exposure": "public",
                            }
                        ],
                        "environment_geometries": [],
                        "display_padding_km": 1,
                        "coverage_confidence": "medium",
                    },
                }
            ],
        }
        payload = build_coverage_browser_payload(self.catalog, registry)
        camera = payload["spots"][0]["opportunities"][0]["camera_zones"][0]

        self.assertEqual(camera["browser_exposure"], "internal_only")
        self.assertNotIn("lat", camera)
        self.assertNotIn("lon", camera)


if __name__ == "__main__":
    unittest.main()
