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
        self.assertIn("tw-014", by_spot)
        self.assertIn("tw-078", by_spot)
        self.assertIn("tw-081", by_spot)

        jianggong_group = by_spot["tw-078"]
        self.assertEqual(jianggong_group["catalog_opportunity_count"], 1)
        self.assertEqual(jianggong_group["coverage_entry_count"], 1)
        self.assertTrue(jianggong_group["all_topics_complete"])

        tieb堡_group = by_spot["tw-081"]
        self.assertEqual(tieb堡_group["catalog_opportunity_count"], 1)
        self.assertEqual(tieb堡_group["coverage_entry_count"], 1)
        self.assertTrue(tieb堡_group["all_topics_complete"])

        qingshui = by_spot["tw-034"]
        self.assertEqual(qingshui["catalog_opportunity_count"], 3)
        self.assertEqual(qingshui["coverage_entry_count"], 3)
        self.assertTrue(qingshui["all_topics_complete"])

        yundong = by_spot["tw-014"]
        self.assertEqual(yundong["catalog_opportunity_count"], 2)
        self.assertEqual(yundong["coverage_entry_count"], 2)
        self.assertTrue(yundong["all_topics_complete"])

        qix = by_spot["tw-036"]
        self.assertEqual(qix["catalog_opportunity_count"], 4)
        self.assertEqual(qix["coverage_entry_count"], 4)
        self.assertTrue(qix["all_topics_complete"])

        by_opp = {
            op["opportunity_id"]: op
            for spot in payload["spots"]
            for op in spot["opportunities"]
        }
        jianggong = by_opp["tw-078-P01"]
        self.assertTrue(jianggong["complete"])
        self.assertEqual(jianggong["status"], "provisional")
        self.assertEqual(
            jianggong["subject_geometries"][0]["geometry"]["type"],
            "corridor",
        )

        tieb堡 = by_opp["tw-081-P01"]
        self.assertTrue(tieb堡["complete"])
        self.assertEqual(tieb堡["status"], "provisional")
        self.assertEqual(
            tieb堡["subject_geometries"][0]["geometry"]["type"],
            "sector",
        )

        qingshui_p01 = by_opp["tw-034-P01"]
        self.assertTrue(qingshui_p01["complete"])
        self.assertEqual(len(qingshui_p01["subject_geometries"]), 2)
        self.assertTrue(qingshui_p01["environment_geometries"])

        qingshui_p02 = by_opp["tw-034-P02"]
        self.assertTrue(qingshui_p02["complete"])
        self.assertEqual(len(qingshui_p02["subject_geometries"]), 2)

        p01 = by_opp["tw-036-P01"]
        self.assertTrue(p01["complete"])
        self.assertEqual(p01["status"], "provisional")
        self.assertTrue(p01["subject_geometries"])
        self.assertTrue(p01["environment_geometries"])

        p02 = by_opp["tw-036-P02"]
        self.assertTrue(p02["complete"])
        self.assertEqual(p02["status"], "provisional")
        self.assertFalse(p02["subject_geometries"])
        self.assertTrue(p02["environment_geometries"])

        p03 = by_opp["tw-036-P03"]
        self.assertTrue(p03["complete"])
        self.assertEqual(p03["status"], "provisional")
        self.assertEqual(len(p03["camera_zones"]), 1)
        self.assertEqual(p03["camera_zones"][0]["browser_exposure"], "generalized")
        self.assertAlmostEqual(p03["camera_zones"][0]["lat"], 24.031426)
        self.assertTrue(p03["subject_geometries"])

        liyu_group = by_spot["tw-082"]
        self.assertEqual(liyu_group["catalog_opportunity_count"], 10)
        self.assertEqual(liyu_group["coverage_entry_count"], 10)
        self.assertTrue(liyu_group["all_topics_complete"])

        liyu = by_opp["tw-082-P01"]
        self.assertTrue(liyu["complete"])
        self.assertEqual(liyu["status"], "provisional")
        self.assertFalse(liyu["errors"])
        self.assertGreaterEqual(len(liyu["subject_geometries"]), 2)

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
