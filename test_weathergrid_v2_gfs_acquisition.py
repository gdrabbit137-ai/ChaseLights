import unittest
from weathergrid_v2_gfs_acquisition import GFS_GRIB_VARS,build_cloud_url,build_publish_manifest
class GfsAcquisitionContractTests(unittest.TestCase):
 def test_four_cloud_grib_variables(self):
  self.assertEqual(set(GFS_GRIB_VARS.values()),{"TCDC","LCDC","MCDC","HCDC"})
 def test_antimeridian_request_fails_closed(self):
  with self.assertRaises(ValueError): build_cloud_url(filename="x",directory="/gfs",bbox={"west":178,"south":0,"east":-178,"north":4})
 def test_manifest_only_claims_fully_published_cells(self):
  m=build_publish_manifest(reference_time_utc="2026-10-05T12:00:00Z",valid_time_utc="2026-10-05T15:00:00Z",cell_results=[
   {"cell_id":"a","tile_path":"a.json","published_fields":["cloud_cover","cloud_cover_low","cloud_cover_mid","cloud_cover_high"]},
   {"cell_id":"b","tile_path":"b.json","published_fields":["cloud_cover_low","cloud_cover_mid","cloud_cover_high"]}])
  self.assertEqual(m["published_cell_ids"],["a"]); self.assertFalse(m["coverage_complete"])
if __name__=="__main__": unittest.main()
