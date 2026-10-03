import unittest
from pathlib import Path

class BrowserTileLoaderContract(unittest.TestCase):
 def test_loader_has_index_and_native_decode_contract(self):
  s=Path("assets/weather-map-v2-tile-loader.js").read_text()
  self.assertIn("weathergrid/v2/index.json",s)
  self.assertIn("schema_version !== 2",s)
  self.assertIn("payload_partition !== 'valid_time'",s)
  self.assertIn("tileToSamples",s)
  self.assertIn("grid length mismatch",s)
  self.assertIn("cellsForViewport",s)
  self.assertIn("loadViewportTiles",s)
  self.assertIn("Promise.allSettled",s)
  self.assertIn("cell.providers?.[provider]",s)
 def test_v2_page_prefers_native_jma_tiles(self):
  s=Path("assets/weather-map-v2.js").read_text()
  self.assertIn("tryNativeJma",s)
  self.assertIn("native-tile",s)
  self.assertIn("JMA MSM native tiles",s)

if __name__=="__main__": unittest.main()
