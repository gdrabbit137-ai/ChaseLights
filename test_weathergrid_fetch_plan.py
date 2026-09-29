import json
import unittest
from pathlib import Path

from gfs_raw_poc import TAIWAN_BBOX
from weathergrid_fetch_plan import (
    build_gfs_fetch_plan,
    snap_nomads_bbox_outward,
    split_coverage_bbox_for_nomads,
)
from weathergrid_coverage import CoverageError, bbox_contains_bbox


ROOT = Path(__file__).resolve().parent


def _load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class WeatherGridFetchPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = _load("runtime_catalog_v004_r4_2.json")
        cls.registry = _load("weathergrid_coverage_registry_r4_2.json")

    def test_region_scope_preserves_current_taiwan_request(self):
        plan = build_gfs_fetch_plan(scope_type="region", region="tw")
        self.assertTrue(plan["coverage_complete"])
        self.assertTrue(plan["safe_to_publish_preview"])
        self.assertEqual(plan["segments"], [TAIWAN_BBOX])

    def test_complete_opportunity_uses_subject_aware_fetch_bbox(self):
        plan = build_gfs_fetch_plan(
            scope_type="opportunity",
            scope_id="tw-036-P03",
            catalog=self.catalog,
            registry=self.registry,
        )
        self.assertTrue(plan["coverage_complete"], plan)
        self.assertTrue(plan["safe_to_scope"])
        self.assertEqual(plan["effective_scope"]["type"], "opportunity")
        self.assertEqual(plan["spot_ids"], ["tw-036"])
        self.assertEqual(len(plan["segments"]), 1)

        segment = plan["segments"][0]
        snapped = {
            "west": segment["leftlon"],
            "south": segment["bottomlat"],
            "east": segment["rightlon"],
            "north": segment["toplat"],
            "wraps_antimeridian": False,
        }
        self.assertTrue(bbox_contains_bbox(snapped, plan["fetch_bbox"]))
        self.assertLess(
            segment["rightlon"] - segment["leftlon"],
            TAIWAN_BBOX["rightlon"] - TAIWAN_BBOX["leftlon"],
        )
        self.assertLess(
            segment["toplat"] - segment["bottomlat"],
            TAIWAN_BBOX["toplat"] - TAIWAN_BBOX["bottomlat"],
        )

    def test_incomplete_opportunity_falls_back_to_region(self):
        plan = build_gfs_fetch_plan(
            scope_type="opportunity",
            scope_id="tw-035-P01",
            catalog=self.catalog,
            registry=self.registry,
        )
        self.assertFalse(plan["coverage_complete"])
        self.assertFalse(plan["safe_to_scope"])
        self.assertFalse(plan["safe_to_publish_preview"])
        self.assertEqual(plan["effective_scope"], {"type": "region", "id": "tw"})
        self.assertEqual(plan["segments"], [TAIWAN_BBOX])
        self.assertIn("no subject-aware coverage registry entry", plan["fallback_reason"])

    def test_incomplete_opportunity_strict_mode_fails(self):
        with self.assertRaises(CoverageError):
            build_gfs_fetch_plan(
                scope_type="opportunity",
                scope_id="tw-035-P01",
                strict=True,
                catalog=self.catalog,
                registry=self.registry,
            )

    def test_place_scope_requires_every_active_topic(self):
        # Liushishishan currently has only part of its large Opportunity set
        # migrated. Place-level fetch must therefore still fall back region-wide.
        plan = build_gfs_fetch_plan(
            scope_type="place",
            scope_id="tw-035",
            catalog=self.catalog,
            registry=self.registry,
        )
        self.assertFalse(plan["coverage_complete"], plan)
        self.assertEqual(plan["effective_scope"], {"type": "region", "id": "tw"})
        diagnostic = plan["coverage_diagnostics"]
        self.assertEqual(diagnostic["catalog_opportunity_count"], 10)
        self.assertIn("tw-035-P01", diagnostic["missing_registry_entries"])
        self.assertIn("tw-035-P02", diagnostic["missing_registry_entries"])

    def test_secondary_local_places_can_use_scoped_fetch(self):
        for spot_id in ("tw-037", "tw-066", "tw-073", "tw-075", "tw-078", "tw-081"):
            with self.subTest(spot_id=spot_id):
                plan = build_gfs_fetch_plan(
                    scope_type="place",
                    scope_id=spot_id,
                    catalog=self.catalog,
                    registry=self.registry,
                )
                self.assertTrue(plan["coverage_complete"], plan)
                self.assertTrue(plan["safe_to_scope"], plan)
                self.assertEqual(plan["effective_scope"], {"type": "place", "id": spot_id})
                self.assertEqual(plan["spot_ids"], [spot_id])
                self.assertEqual(plan["coverage_diagnostics"]["catalog_opportunity_count"], 1)
                self.assertEqual(plan["coverage_diagnostics"]["migrated_count"], 1)
                self.assertEqual(plan["coverage_diagnostics"]["missing_registry_entries"], [])
                self.assertEqual(plan["coverage_diagnostics"]["incomplete_opportunities"], [])
                self.assertEqual(len(plan["segments"]), 1)
                segment = plan["segments"][0]
                self.assertLess(
                    segment["rightlon"] - segment["leftlon"],
                    TAIWAN_BBOX["rightlon"] - TAIWAN_BBOX["leftlon"],
                )
                self.assertLess(
                    segment["toplat"] - segment["bottomlat"],
                    TAIWAN_BBOX["toplat"] - TAIWAN_BBOX["bottomlat"],
                )

                if spot_id == "tw-037":
                    self.assertLessEqual(segment["leftlon"], 120.95888)
                    self.assertGreaterEqual(segment["rightlon"], 120.95888)
                    self.assertLessEqual(segment["bottomlat"], 22.507487)
                    self.assertGreaterEqual(segment["toplat"], 22.507487)

                if spot_id == "tw-073":
                    self.assertLessEqual(segment["leftlon"], 121.54471)
                    self.assertGreaterEqual(segment["rightlon"], 121.54471)
                    self.assertLessEqual(segment["bottomlat"], 25.292439)
                    self.assertGreaterEqual(segment["toplat"], 25.292439)

    def test_qingshui_all_topic_place_can_use_scoped_fetch(self):
        plan = build_gfs_fetch_plan(
            scope_type="place",
            scope_id="tw-034",
            catalog=self.catalog,
            registry=self.registry,
        )
        self.assertTrue(plan["coverage_complete"], plan)
        self.assertTrue(plan["safe_to_scope"], plan)
        self.assertEqual(plan["effective_scope"], {"type": "place", "id": "tw-034"})
        self.assertEqual(plan["spot_ids"], ["tw-034"])
        self.assertEqual(plan["coverage_diagnostics"]["catalog_opportunity_count"], 3)
        self.assertEqual(plan["coverage_diagnostics"]["migrated_count"], 3)
        self.assertEqual(plan["coverage_diagnostics"]["missing_registry_entries"], [])
        self.assertEqual(plan["coverage_diagnostics"]["incomplete_opportunities"], [])
        self.assertEqual(len(plan["segments"]), 1)
        segment = plan["segments"][0]
        self.assertLess(
            segment["rightlon"] - segment["leftlon"],
            TAIWAN_BBOX["rightlon"] - TAIWAN_BBOX["leftlon"],
        )
        self.assertLess(
            segment["toplat"] - segment["bottomlat"],
            TAIWAN_BBOX["toplat"] - TAIWAN_BBOX["bottomlat"],
        )

    def test_qixingtan_all_topic_place_can_use_scoped_fetch(self):
        plan = build_gfs_fetch_plan(
            scope_type="place",
            scope_id="tw-036",
            catalog=self.catalog,
            registry=self.registry,
        )
        self.assertTrue(plan["coverage_complete"], plan)
        self.assertTrue(plan["safe_to_scope"], plan)
        self.assertEqual(plan["effective_scope"], {"type": "place", "id": "tw-036"})
        self.assertEqual(plan["spot_ids"], ["tw-036"])
        self.assertEqual(plan["coverage_diagnostics"]["catalog_opportunity_count"], 4)
        self.assertEqual(plan["coverage_diagnostics"]["migrated_count"], 4)
        self.assertEqual(plan["coverage_diagnostics"]["missing_registry_entries"], [])
        self.assertEqual(plan["coverage_diagnostics"]["incomplete_opportunities"], [])
        self.assertEqual(len(plan["segments"]), 1)
        segment = plan["segments"][0]
        self.assertLess(
            segment["rightlon"] - segment["leftlon"],
            TAIWAN_BBOX["rightlon"] - TAIWAN_BBOX["leftlon"],
        )
        self.assertLess(
            segment["toplat"] - segment["bottomlat"],
            TAIWAN_BBOX["toplat"] - TAIWAN_BBOX["bottomlat"],
        )

    def test_first_all_topic_place_can_use_scoped_fetch(self):
        plan = build_gfs_fetch_plan(
            scope_type="place",
            scope_id="tw-014",
            catalog=self.catalog,
            registry=self.registry,
        )
        self.assertTrue(plan["coverage_complete"], plan)
        self.assertTrue(plan["safe_to_scope"], plan)
        self.assertEqual(plan["effective_scope"], {"type": "place", "id": "tw-014"})
        self.assertEqual(plan["spot_ids"], ["tw-014"])
        self.assertEqual(
            plan["coverage_diagnostics"]["catalog_opportunity_count"],
            2,
        )
        self.assertEqual(
            plan["coverage_diagnostics"]["migrated_count"],
            2,
        )
        self.assertEqual(
            plan["coverage_diagnostics"]["missing_registry_entries"],
            [],
        )
        self.assertEqual(len(plan["segments"]), 1)
        segment = plan["segments"][0]
        self.assertLess(
            segment["rightlon"] - segment["leftlon"],
            TAIWAN_BBOX["rightlon"] - TAIWAN_BBOX["leftlon"],
        )
        self.assertLess(
            segment["toplat"] - segment["bottomlat"],
            TAIWAN_BBOX["toplat"] - TAIWAN_BBOX["bottomlat"],
        )

    def test_liyu_all_topic_place_can_use_scoped_fetch(self):
        plan = build_gfs_fetch_plan(
            scope_type="place",
            scope_id="tw-082",
            catalog=self.catalog,
            registry=self.registry,
        )
        self.assertTrue(plan["coverage_complete"], plan)
        self.assertTrue(plan["safe_to_scope"], plan)
        self.assertEqual(plan["effective_scope"], {"type": "place", "id": "tw-082"})
        self.assertEqual(plan["spot_ids"], ["tw-082"])
        self.assertEqual(
            plan["coverage_diagnostics"]["catalog_opportunity_count"],
            10,
        )
        self.assertEqual(
            plan["coverage_diagnostics"]["migrated_count"],
            10,
        )
        self.assertEqual(
            plan["coverage_diagnostics"]["missing_registry_entries"],
            [],
        )
        self.assertEqual(
            plan["coverage_diagnostics"]["incomplete_opportunities"],
            [],
        )
        self.assertEqual(len(plan["segments"]), 1)
        segment = plan["segments"][0]
        self.assertLess(
            segment["rightlon"] - segment["leftlon"],
            TAIWAN_BBOX["rightlon"] - TAIWAN_BBOX["leftlon"],
        )
        self.assertLess(
            segment["toplat"] - segment["bottomlat"],
            TAIWAN_BBOX["toplat"] - TAIWAN_BBOX["bottomlat"],
        )

    def test_provider_grid_snap_only_expands(self):
        snapped = snap_nomads_bbox_outward({
            "leftlon": 121.13,
            "rightlon": 121.61,
            "bottomlat": 23.97,
            "toplat": 24.22,
        })
        self.assertEqual(snapped["leftlon"], 121.0)
        self.assertEqual(snapped["rightlon"], 121.75)
        self.assertEqual(snapped["bottomlat"], 23.75)
        self.assertEqual(snapped["toplat"], 24.25)

    def test_antimeridian_fetch_is_split_into_two_segments(self):
        segments = split_coverage_bbox_for_nomads({
            "west": 179.6,
            "south": 51.5,
            "east": -179.5,
            "north": 52.1,
            "wraps_antimeridian": True,
        })
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]["rightlon"], 180.0)
        self.assertEqual(segments[1]["leftlon"], -180.0)
        self.assertTrue(all(x["leftlon"] < x["rightlon"] for x in segments))

    def test_unknown_scope_id_fails_instead_of_guessing(self):
        with self.assertRaises(CoverageError):
            build_gfs_fetch_plan(
                scope_type="opportunity",
                scope_id="tw-does-not-exist",
                catalog=self.catalog,
                registry=self.registry,
            )


if __name__ == "__main__":
    unittest.main()
