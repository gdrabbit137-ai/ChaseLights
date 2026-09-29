import json
import unittest
from pathlib import Path

from weathergrid_coverage import (
    bbox_contains_bbox,
    bbox_contains_point,
    geometry_points,
    plan_opportunity_coverage,
    plan_place_coverage,
    audit_coverage_registry,
)


def _opportunity(
    oid,
    *,
    camera_lat=24.0,
    camera_lon=121.0,
    subject=None,
    environment=None,
    status="verified",
):
    return {
        "opportunity_id": oid,
        "viewpoints": [
            {
                "viewpoint_id": f"{oid}-VP01",
                "lat": camera_lat,
                "lon": camera_lon,
                "geometry_type": "point",
            }
        ],
        "weather_coverage": {
            "schema_version": 1,
            "status": status,
            "camera_zone_refs": [f"{oid}-VP01"],
            "camera_zone_browser_exposure": {
                f"{oid}-VP01": "generalized"
            },
            "subject_geometries": [] if subject is None else [
                {
                    "subject_id": f"{oid}-SUB01",
                    "role": "primary_subject",
                    "geometry": subject,
                    "browser_exposure": "public",
                }
            ],
            "environment_geometries": [] if environment is None else [
                {
                    "environment_id": f"{oid}-ENV01",
                    "role": "environment",
                    "geometry": environment,
                    "browser_exposure": "public",
                }
            ],
            "display_padding_km": 5,
            "coverage_confidence": "high",
        },
    }


class WeatherGridCoverageTest(unittest.TestCase):
    def test_opportunity_bbox_contains_camera_subject_viewport_and_fetch_halo(self):
        op = _opportunity(
            "tw-test-P01",
            camera_lat=24.0,
            camera_lon=121.0,
            subject={
                "type": "bbox",
                "west": 121.25,
                "south": 24.10,
                "east": 121.45,
                "north": 24.30,
            },
        )
        plan = plan_opportunity_coverage(op, provider_grid_spacing_deg=0.25)

        self.assertTrue(plan.complete, plan.to_dict())
        self.assertTrue(bbox_contains_point(plan.coverage_bbox, 24.0, 121.0))
        self.assertTrue(bbox_contains_point(plan.coverage_bbox, 24.30, 121.45))
        self.assertTrue(bbox_contains_bbox(plan.viewport_bbox, plan.coverage_bbox))
        self.assertTrue(bbox_contains_bbox(plan.fetch_bbox, plan.viewport_bbox))

        # GFS 0.25 degree halo is larger than display padding alone.
        self.assertLessEqual(plan.fetch_bbox["south"], plan.viewport_bbox["south"])
        self.assertGreaterEqual(plan.fetch_bbox["north"], plan.viewport_bbox["north"])

    def test_missing_subject_or_environment_is_explicitly_incomplete(self):
        op = _opportunity("tw-test-P02", subject=None, environment=None)
        plan = plan_opportunity_coverage(op)

        self.assertFalse(plan.complete)
        self.assertTrue(
            any("subject or environment geometry" in e for e in plan.errors),
            plan.errors,
        )

    def test_missing_camera_reference_does_not_fallback_to_place_center(self):
        op = _opportunity(
            "tw-test-P03",
            subject={"type": "point", "lat": 24.2, "lon": 121.3},
        )
        op["weather_coverage"]["camera_zone_refs"] = ["does-not-exist"]
        plan = plan_opportunity_coverage(op)

        self.assertFalse(plan.complete)
        self.assertTrue(any("camera_zone_ref not found" in e for e in plan.errors))
        # Subject geometry may still yield a bbox, but the plan remains incomplete.
        self.assertIsNotNone(plan.coverage_bbox)

    def test_antimeridian_subject_uses_short_wrapped_bbox(self):
        op = _opportunity(
            "us-test-P01",
            camera_lat=51.8,
            camera_lon=179.7,
            subject={
                "type": "bbox",
                "west": 179.5,
                "south": 51.5,
                "east": -179.6,
                "north": 52.0,
            },
        )
        plan = plan_opportunity_coverage(op)

        self.assertTrue(plan.complete, plan.to_dict())
        self.assertTrue(plan.coverage_bbox["wraps_antimeridian"])
        self.assertTrue(bbox_contains_point(plan.coverage_bbox, 51.8, 179.7))
        self.assertTrue(bbox_contains_point(plan.coverage_bbox, 51.7, -179.8))

    def test_sector_uses_referenced_camera_origin_and_reaches_subject_direction(self):
        op = _opportunity(
            "tw-test-P04",
            camera_lat=24.0,
            camera_lon=121.0,
            subject={
                "type": "sector",
                "origin_viewpoint_id": "tw-test-P04-VP01",
                "azimuth_start_deg": 80,
                "azimuth_end_deg": 100,
                "min_range_km": 0,
                "max_range_km": 40,
            },
        )
        plan = plan_opportunity_coverage(op)

        self.assertTrue(plan.complete, plan.to_dict())
        self.assertLessEqual(plan.coverage_bbox["west"], 121.0)
        self.assertGreater(plan.coverage_bbox["east"], 121.3)

    def test_corridor_expands_beyond_centerline(self):
        points = geometry_points({
            "type": "corridor",
            "coordinates": [[121.0, 24.0], [121.2, 24.1]],
            "half_width_km": 5,
        })
        lats = [x[0] for x in points]
        lons = [x[1] for x in points]

        self.assertLess(min(lats), 24.0)
        self.assertGreater(max(lats), 24.1)
        self.assertLess(min(lons), 121.0)
        self.assertGreater(max(lons), 121.2)

    def test_place_union_contains_all_topic_coverage(self):
        a = _opportunity(
            "tw-test-P05",
            camera_lat=24.0,
            camera_lon=121.0,
            subject={"type": "point", "lat": 24.1, "lon": 121.2},
        )
        b = _opportunity(
            "tw-test-P06",
            camera_lat=24.0,
            camera_lon=121.0,
            subject={"type": "point", "lat": 24.3, "lon": 121.5},
        )
        result = plan_place_coverage([a, b])

        self.assertTrue(result["complete"], result)
        self.assertEqual(result["opportunity_count"], 2)
        self.assertTrue(bbox_contains_point(result["coverage_bbox"], 24.1, 121.2))
        self.assertTrue(bbox_contains_point(result["coverage_bbox"], 24.3, 121.5))

    def test_b121_registry_resolves_against_runtime_catalog(self):
        root = Path(__file__).resolve().parent
        catalog = json.loads(
            (root / "runtime_catalog_v004_r4_2.json").read_text(encoding="utf-8")
        )
        registry = json.loads(
            (root / "weathergrid_coverage_registry_r4_2.json").read_text(encoding="utf-8")
        )
        audit = audit_coverage_registry(catalog, registry)

        self.assertEqual(audit["counts"]["entries"], 7)
        self.assertEqual(audit["counts"]["missing_opportunity"], 0)
        self.assertEqual(audit["counts"]["provisional"], 4)
        self.assertEqual(audit["counts"]["needs_research"], 3)
        self.assertEqual(audit["counts"]["complete"], 4)
        self.assertEqual(audit["counts"]["incomplete"], 3)

        by_id = {row["opportunity_id"]: row for row in audit["results"]}
        self.assertTrue(by_id["tw-036-P03"]["complete"])
        self.assertTrue(by_id["tw-036-P04"]["complete"])
        self.assertTrue(by_id["tw-019-P04"]["complete"])
        self.assertFalse(by_id["tw-082-P01"]["complete"])
        self.assertTrue(
            any("subject or environment geometry" in e for e in by_id["tw-082-P01"]["errors"])
        )

        # The northward Qixingtan coverage must materially extend beyond the
        # camera coordinate instead of collapsing to a Place-center viewport.
        qix = by_id["tw-036-P03"]["coverage_bbox"]
        self.assertLessEqual(qix["west"], 121.62717)
        self.assertGreater(qix["north"], 24.15)

    def test_needs_research_stays_incomplete_even_with_geometry(self):
        op = _opportunity(
            "tw-test-P07",
            subject={"type": "point", "lat": 24.1, "lon": 121.2},
            status="needs_research",
        )
        plan = plan_opportunity_coverage(op)
        self.assertFalse(plan.complete)
        self.assertEqual(plan.status, "needs_research")


if __name__ == "__main__":
    unittest.main()
