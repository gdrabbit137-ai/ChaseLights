import unittest
from weathergrid_v2_cache_index import cells_for_region
from weathergrid_v2_capacity import estimate_cell,estimate_region,recommend_storage

class CapacityTest(unittest.TestCase):
 def test_native_resolution_changes_cost(self):
  b={"west":120,"south":22.4,"east":122,"north":24.4}
  self.assertGreater(estimate_cell("jma",b)["values"],estimate_cell("gfs",b)["values"])
 def test_region_budget_is_reported(self):
  r=estimate_region("jma",cells_for_region("jp"))
  self.assertGreater(r["cell_count"],20);self.assertGreater(r["estimated_refresh_mib"],0)
 def test_generated_cells_are_not_committed_by_default(self):
  x=recommend_storage([estimate_region("gfs",cells_for_region("us_west"))])
  self.assertFalse(x["publish_generated_cells_to_git"])
if __name__=="__main__":unittest.main()
