import json
import unittest
from pathlib import Path

from weathergrid_coverage import (
    bbox_contains_bbox,
    bbox_contains_point,
    camera_zone_points,
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

        self.assertEqual(audit["counts"]["entries"], 36)
        self.assertEqual(audit["counts"]["missing_opportunity"], 0)
        self.assertEqual(audit["counts"]["provisional"], 36)
        self.assertEqual(audit["counts"]["needs_research"], 0)
        self.assertEqual(audit["counts"]["complete"], 36)
        self.assertEqual(audit["counts"]["incomplete"], 0)

        by_id = {row["opportunity_id"]: row for row in audit["results"]}
        self.assertTrue(by_id["tw-034-P01"]["complete"])
        self.assertTrue(by_id["tw-034-P02"]["complete"])
        self.assertTrue(by_id["tw-034-P03"]["complete"])
        self.assertEqual(by_id["tw-034-P01"]["status"], "provisional")
        self.assertEqual(by_id["tw-034-P02"]["subject_geometry_count"], 2)

        self.assertTrue(by_id["tw-036-P01"]["complete"])
        self.assertTrue(by_id["tw-036-P02"]["complete"])
        for oid in [f"tw-036-P{i:02d}" for i in range(1, 5)]:
            self.assertTrue(by_id[oid]["complete"], (oid, by_id[oid]))
            self.assertEqual(by_id[oid]["status"], "provisional")
        self.assertGreaterEqual(by_id["tw-036-P01"]["subject_geometry_count"], 1)
        self.assertGreaterEqual(by_id["tw-036-P02"]["environment_geometry_count"], 1)
        self.assertEqual(by_id["tw-036-P01"]["status"], "provisional")
        self.assertEqual(by_id["tw-036-P02"]["status"], "provisional")
        self.assertTrue(by_id["tw-078-P01"]["complete"])
        self.assertTrue(by_id["tw-081-P01"]["complete"])
        self.assertEqual(by_id["tw-078-P01"]["status"], "provisional")
        self.assertEqual(by_id["tw-081-P01"]["status"], "provisional")
        self.assertEqual(by_id["tw-078-P01"]["subject_geometry_count"], 1)
        self.assertEqual(by_id["tw-081-P01"]["subject_geometry_count"], 1)

        self.assertTrue(by_id["tw-075-P01"]["complete"])
        self.assertEqual(by_id["tw-075-P01"]["status"], "provisional")
        self.assertEqual(by_id["tw-075-P01"]["subject_geometry_count"], 1)
        self.assertEqual(by_id["tw-075-P01"]["environment_geometry_count"], 1)

        self.assertTrue(by_id["tw-073-P01"]["complete"])
        self.assertEqual(by_id["tw-073-P01"]["status"], "provisional")
        self.assertEqual(by_id["tw-073-P01"]["subject_geometry_count"], 1)
        self.assertEqual(by_id["tw-073-P01"]["environment_geometry_count"], 1)

        self.assertTrue(by_id["tw-037-P01"]["complete"])
        self.assertEqual(by_id["tw-037-P01"]["status"], "provisional")
        self.assertEqual(by_id["tw-037-P01"]["subject_geometry_count"], 1)
        self.assertEqual(by_id["tw-037-P01"]["environment_geometry_count"], 1)

        self.assertTrue(by_id["tw-019-P04"]["complete"])
        self.assertTrue(by_id["tw-014-P01"]["complete"])
        self.assertEqual(by_id["tw-014-P01"]["status"], "provisional")
        self.assertEqual(by_id["tw-014-P01"]["subject_geometry_count"], 1)

        for oid in [f"tw-082-P{i:02d}" for i in range(1, 11)]:
            self.assertTrue(by_id[oid]["complete"], (oid, by_id[oid]))
            self.assertEqual(by_id[oid]["status"], "provisional")

        liyu = by_id["tw-082-P01"]["coverage_bbox"]
        self.assertLess(liyu["west"], 121.49)
        self.assertGreater(liyu["east"], 121.53)
        self.assertLess(liyu["south"], 23.90)
        self.assertGreater(liyu["north"], 23.95)

        for oid in [
            "tw-004-P03", "tw-008-P03", "tw-014-P02", "tw-020-P02",
            "tw-022-P02", "tw-023-P02", "tw-024-P02", "tw-035-P06",
            "tw-040-P04", "tw-043-P03", "tw-047-P01", "tw-049-P03",
        ]:
            self.assertTrue(by_id[oid]["complete"], (oid, by_id[oid]))
            self.assertEqual(by_id[oid]["status"], "provisional")
            self.assertEqual(by_id[oid]["environment_geometry_count"], 1)

        # tw-032-P02 has an existing spatial profile but its Camera Zone
        # coordinate is still pending in the catalog, so B124 must not invent
        # a coordinate just to mark the coverage complete.
        self.assertNotIn("tw-032-P02", by_id)

        # The northward Qixingtan coverage must materially extend beyond the
        # camera coordinate instead of collapsing to a Place-center viewport.
        qix = by_id["tw-036-P03"]["coverage_bbox"]
        self.assertLessEqual(qix["west"], 121.62717)
        self.assertGreater(qix["north"], 24.15)

        sunrise = by_id["tw-036-P01"]["coverage_bbox"]
        self.assertGreater(sunrise["east"], 121.75)
        self.assertLess(sunrise["south"], 24.0)
        self.assertGreater(sunrise["north"], 24.06)

        stars = by_id["tw-036-P02"]["coverage_bbox"]
        self.assertLess(stars["west"], 121.45)
        self.assertGreater(stars["east"], 121.80)
        self.assertLess(stars["south"], 23.86)
        self.assertGreater(stars["north"], 24.20)

        qingshui_sunrise = by_id["tw-034-P01"]["coverage_bbox"]
        self.assertLessEqual(qingshui_sunrise["west"], 121.661332)
        self.assertGreater(qingshui_sunrise["east"], 121.80)
        self.assertGreater(qingshui_sunrise["north"], 24.22)

        qingshui_view = by_id["tw-034-P02"]["coverage_bbox"]
        self.assertGreater(qingshui_view["east"], 121.70)
        self.assertGreater(qingshui_view["north"], 24.22)

        jianggong = by_id["tw-078-P01"]["coverage_bbox"]
        self.assertTrue(bbox_contains_point(jianggong, 24.426386, 118.304369))
        self.assertTrue(bbox_contains_point(jianggong, 24.42746, 118.30005))

        tieb堡 = by_id["tw-081-P01"]["coverage_bbox"]
        self.assertTrue(bbox_contains_point(tieb堡, 26.141922, 119.921072))
        self.assertLess(tieb堡["west"], 119.9200)
        self.assertGreater(tieb堡["east"], 119.9220)

        waiao = by_id["tw-075-P01"]["coverage_bbox"]
        self.assertTrue(bbox_contains_point(waiao, 24.842373, 121.95015))
        # The catalog Camera Zone is a ~900 m long beach area. B130 must
        # conservatively cover its curated extent rather than only the anchor.
        catalog_waiao = next(
            spot for spot in catalog["spots"] if spot["spot_id"] == "tw-075"
        )
        vp = catalog_waiao["opportunities"][0]["viewpoints"][0]
        camera_points, mode = camera_zone_points(vp)
        self.assertEqual(mode, "conservative_extent")
        for lat, lon in camera_points:
            self.assertTrue(
                bbox_contains_point(waiao, lat, lon),
                (lat, lon, waiao),
            )

        laomei = by_id["tw-073-P01"]["coverage_bbox"]
        # Official Tourism Administration attraction coordinate lies inside the
        # local green-reef foreground envelope.
        self.assertTrue(bbox_contains_point(laomei, 25.292439, 121.54471))
        catalog_laomei = next(
            spot for spot in catalog["spots"] if spot["spot_id"] == "tw-073"
        )
        laomei_vp = catalog_laomei["opportunities"][0]["viewpoints"][0]
        laomei_camera_points, laomei_mode = camera_zone_points(laomei_vp)
        self.assertEqual(laomei_mode, "conservative_extent")
        for lat, lon in laomei_camera_points:
            self.assertTrue(
                bbox_contains_point(laomei, lat, lon),
                (lat, lon, laomei),
            )
        # B131's spring dawn sector extends well beyond the 250 m local
        # foreground while staying directional rather than region-wide.
        self.assertGreater(laomei["east"], 121.65)
        self.assertLess(laomei["west"], 121.55)

        duoliang = by_id["tw-037-P01"]["coverage_bbox"]
        # Official Tourism Administration coordinate must be retained inside
        # the station/train subject envelope.
        self.assertTrue(bbox_contains_point(duoliang, 22.507487, 120.95888))
        # The broad Pacific background sector must extend meaningfully east of
        # the station without becoming region-wide.
        self.assertGreater(duoliang["east"], 121.05)
        self.assertLess(duoliang["west"], 120.96)

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
