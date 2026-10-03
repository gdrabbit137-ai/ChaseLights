import json, tempfile, unittest
from pathlib import Path
from weathergrid_v2_tile_export import frame_to_tile, write_frame_tile

class TileExportTest(unittest.TestCase):
 def sample(self):
  return {"reference_time_utc":"2026-10-03T00:00:00Z","grid":{"rows":2,"cols":2,"latitudes":[35,34.95],"longitudes":[138,138.0625]},"frames":[{"forecast_hour":1,"valid_time_utc":"2026-10-03T01:00:00Z","values":{"cloud_cover":[1,2,3,4],"cloud_cover_low":[5,6,7,8]}}],"transport":{"layout":"data_spatial"}}
 def test_exports_one_valid_time_only(self):
  t=frame_to_tile(self.sample())
  self.assertEqual(t["valid_time_utc"],"2026-10-03T01:00:00Z")
  self.assertNotIn("frames",t); self.assertEqual(len(t["values"]["cloud_cover"]),4)
 def test_rejects_wrong_grid_length(self):
  s=self.sample();s["frames"][0]["values"]["cloud_cover"]=[1]
  with self.assertRaises(ValueError): frame_to_tile(s)
 def test_compact_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"tile.json";write_frame_tile(self.sample(),p)
   self.assertEqual(json.loads(p.read_text())["provider"],"jma")
