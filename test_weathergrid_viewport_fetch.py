import unittest
from weathergrid_native_viewport import adapter_bbox, build_native_request
from weathergrid_viewport_fetch import plan_viewport_fetch

class ViewportFetchTest(unittest.TestCase):
    def test_jma_expands_snaps_and_maps_adapter_bbox(self):
        p=plan_viewport_fetch("jma",{"west":121,"south":23,"east":122,"north":24},.5)
        self.assertEqual(p["status"],"ready")
        self.assertLessEqual(p["fetch_bbox"]["west"],120.5)
        self.assertGreaterEqual(p["fetch_bbox"]["east"],122.5)
        self.assertTrue(p["cache_key"])
        self.assertTrue(p["coverage_complete"])
        b=adapter_bbox(p)
        self.assertEqual(b["leftlon"],p["fetch_bbox"]["west"])
        self.assertEqual(b["toplat"],p["fetch_bbox"]["north"])

    def test_jma_clips_native_domain(self):
        p=plan_viewport_fetch("jma",{"west":119.5,"south":22.0,"east":121,"north":23},.2)
        self.assertEqual(p["fetch_bbox"]["west"],120.0)
        self.assertEqual(p["fetch_bbox"]["south"],22.4)
        self.assertFalse(p["coverage_complete"])

    def test_jma_outside_domain_is_explicit(self):
        p=plan_viewport_fetch("jma",{"west":100,"south":10,"east":101,"north":11})
        self.assertEqual(p["status"],"outside_provider_domain")
        self.assertIsNone(p["fetch_bbox"])

    def test_native_requests_identify_real_adapters(self):
        b={"west":121,"south":23,"east":122,"north":24}
        j=build_native_request("jma",b)
        g=build_native_request("gfs",b)
        self.assertEqual(j["transport"]["model"],"JMA MSM")
        self.assertIn("jma_msm_aws_om",j["transport"]["adapter"])
        self.assertEqual(g["transport"]["model"],"GFS")
        self.assertIn("gfs_multilayer_poc",g["transport"]["adapter"])

    def test_cache_key_is_stable(self):
        b={"west":121,"south":23,"east":122,"north":24}
        self.assertEqual(plan_viewport_fetch("gfs",b)["cache_key"],plan_viewport_fetch("gfs",b)["cache_key"])

if __name__=="__main__": unittest.main(verbosity=2)
