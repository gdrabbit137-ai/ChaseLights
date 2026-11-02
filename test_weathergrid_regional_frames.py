import pathlib
import unittest

from gfs_raw_poc import REGIONAL_BBOXES, TAIWAN_BBOX, active_region_places
from weathergrid_fetch_plan import build_gfs_fetch_plan
from weathergrid_coverage import CoverageError, bbox_contains_bbox

ROOT = pathlib.Path(__file__).resolve().parent


class RegionalBboxesTest(unittest.TestCase):
    """CL-WG-05 regional frames: bboxes mirror the JS region registry."""

    def test_regional_bboxes_match_owner_spec(self):
        self.assertEqual(REGIONAL_BBOXES["tw"], TAIWAN_BBOX)
        self.assertEqual(REGIONAL_BBOXES["jp"], {
            "leftlon": 122.0, "rightlon": 146.0, "toplat": 46.0, "bottomlat": 24.0,
        })
        self.assertEqual(REGIONAL_BBOXES["us"], {
            "leftlon": -125.0, "rightlon": -70.5, "toplat": 49.5, "bottomlat": 25.0,
        })
        self.assertEqual(REGIONAL_BBOXES["ak"], {
            "leftlon": -158.0, "rightlon": -132.0, "toplat": 69.5, "bottomlat": 55.0,
        })
        self.assertEqual(REGIONAL_BBOXES["hi"], {
            "leftlon": -160.3, "rightlon": -154.8, "toplat": 22.4, "bottomlat": 18.8,
        })

    def test_ak_bbox_contains_every_catalogued_alaska_place(self):
        ak = REGIONAL_BBOXES["ak"]
        places = active_region_places("ak")
        self.assertGreater(len(places), 0)
        for place in places:
            self.assertTrue(
                ak["leftlon"] <= place["lon"] <= ak["rightlon"]
                and ak["bottomlat"] <= place["lat"] <= ak["toplat"],
                place,
            )

    def test_us_places_exclude_alaska_and_hawaii(self):
        us = REGIONAL_BBOXES["us"]
        places = active_region_places("us")
        self.assertGreater(len(places), 0)
        ids = {p["spot_id"] for p in places}
        for place in places:
            self.assertTrue(
                us["leftlon"] <= place["lon"] <= us["rightlon"]
                and us["bottomlat"] <= place["lat"] <= us["toplat"],
                place,
            )
        # The 20 Alaska places are routed to the ak frame, never to us.
        self.assertNotIn("us-041", ids)
        self.assertNotIn("us-056", ids)
        self.assertNotIn("us-059", ids)

    def test_hawaii_has_no_catalogued_places_yet(self):
        # Honest empty state: no fabricated Hawaii places.
        self.assertEqual(active_region_places("hi"), [])


class RegionalFetchPlanTest(unittest.TestCase):
    def test_regional_plans_use_curated_bbox(self):
        for region in ("jp", "us", "ak", "hi"):
            plan = build_gfs_fetch_plan(scope_type="region", region=region)
            self.assertTrue(plan["coverage_complete"], region)
            segment = plan["segments"][0]
            owner = REGIONAL_BBOXES[region]
            # The snapped fetch rectangle must fully cover the owner bbox
            # (snapped outward to the 0.25° provider grid).
            self.assertLessEqual(segment["leftlon"], owner["leftlon"], region)
            self.assertGreaterEqual(segment["rightlon"], owner["rightlon"], region)
            self.assertLessEqual(segment["bottomlat"], owner["bottomlat"], region)
            self.assertGreaterEqual(segment["toplat"], owner["toplat"], region)
            # Idempotent for owner boxes already on the provider grid.
            for key in ("leftlon", "rightlon", "toplat", "bottomlat"):
                self.assertAlmostEqual(
                    segment[key] % 0.25, 0.0, places=6, msg=f"{region}:{key}"
                )

    def test_unknown_region_still_fails_closed(self):
        with self.assertRaises(CoverageError):
            build_gfs_fetch_plan(scope_type="region", region="eu")


if __name__ == "__main__":
    unittest.main()
