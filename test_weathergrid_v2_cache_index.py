import unittest
from weathergrid_v2_cache_index import build_index, cells_for_region

class CacheIndexTest(unittest.TestCase):
    def test_regions_cover_beyond_current_taiwan_bundle(self):
        i=build_index()
        self.assertIn("tw",i["regions"])
        self.assertIn("jp",i["regions"])
        self.assertIn("us_west",i["regions"])
        self.assertGreater(len(i["regions"]["jp"]["cells"]),20)

    def test_provider_paths_follow_native_domains(self):
        index=build_index()
        jp=index["regions"]["jp"]["cells"]
        us=index["regions"]["us_west"]["cells"]
        self.assertTrue(all("gfs" in c["providers"] for c in jp+us))
        self.assertTrue(any("jma" in c["providers"] for c in jp))
        self.assertTrue(all("jma" not in c["providers"] for c in us))

    def test_cell_bounds_do_not_exceed_region(self):
        index=build_index()
        for r in ("tw","jp","us_west"):
            b=index["regions"][r]["bbox"]
            for c in cells_for_region(r):
                x=c["bbox"]
                self.assertGreaterEqual(x["west"],b["west"])
                self.assertLessEqual(x["east"],b["east"])
                self.assertGreaterEqual(x["south"],b["south"])
                self.assertLessEqual(x["north"],b["north"])

if __name__=="__main__":
    unittest.main(verbosity=2)
