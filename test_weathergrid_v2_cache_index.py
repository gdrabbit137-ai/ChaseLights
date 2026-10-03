import unittest
from weathergrid_v2_cache_index import build_index,cells_for_region

class CacheIndexTest(unittest.TestCase):
 def test_regions_cover_beyond_current_taiwan_bundle(self):
  i=build_index()
  self.assertIn("tw",i["regions"]);self.assertIn("jp",i["regions"]);self.assertIn("us_west",i["regions"])
  self.assertGreater(len(i["regions"]["jp"]["cells"]),20)
 def test_cells_have_lazy_load_paths(self):
  c=cells_for_region("tw")[0]
  p=build_index()["regions"]["tw"]["cells"][0]["providers"]
  self.assertTrue(p["jma"].endswith(".json"));self.assertTrue(p["gfs"].endswith(".json"))
 def test_cell_bounds_do_not_exceed_region(self):
  for r in ("tw","jp","us_west"):
   b=build_index()["regions"][r]["bbox"]
   for c in cells_for_region(r):
    x=c["bbox"];self.assertGreaterEqual(x["west"],b["west"]);self.assertLessEqual(x["east"],b["east"])
if __name__=="__main__":unittest.main()
