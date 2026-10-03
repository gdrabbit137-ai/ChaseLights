import subprocess
import unittest
from pathlib import Path


class BrowserTileLoaderContract(unittest.TestCase):
    def test_loader_has_index_and_native_decode_contract(self):
        s = Path("assets/weather-map-v2-tile-loader.js").read_text()
        self.assertIn("weathergrid/v2/index.json", s)
        self.assertIn("schema_version !== 2", s)
        self.assertIn("payload_partition !== 'valid_time'", s)
        self.assertIn("tileToSamples", s)
        self.assertIn("grid length mismatch", s)
        self.assertIn("cellsForViewport", s)
        self.assertIn("loadViewportTiles", s)
        self.assertIn("Promise.allSettled", s)
        self.assertIn("cell.providers?.[provider]", s)
        self.assertIn("published_cell_ids", s)
        self.assertIn("loadedCoverage", s)
        self.assertIn("coverageContainsViewport", s)
        self.assertIn("const coverage = loadedCoverage(loaded, provider)", s)
        self.assertIn("const coversViewport = coverageContainsViewport(loaded, provider, viewport)", s)
        self.assertIn("complete: cells.length > 0", s)
        self.assertIn("&& loaded.length === cells.length", s)
        self.assertIn("&& failed.length === 0", s)
        self.assertIn("&& coversViewport", s)

    def test_viewport_coverage_guard_detects_manifest_holes(self):
        script = r"""
import fs from 'node:fs';
const source = fs.readFileSync('assets/weather-map-v2-tile-loader.js', 'utf8');
const url = 'data:text/javascript;base64,' + Buffer.from(source).toString('base64');
const { coverageContainsViewport } = await import(url);
const item = (id, west, south, east, north) => ({
  cell: {
    id,
    bbox: { west, south, east, north },
    providers: { jma: { coverage_bbox: { west, south, east, north } } },
  },
});
const viewport = { w: 0, s: 0, e: 2, n: 1 };
if (!coverageContainsViewport([
  item('left', 0, 0, 1, 1),
  item('right', 1, 0, 2, 1),
], 'jma', viewport)) process.exit(11);
if (coverageContainsViewport([
  item('left-gap', 0, 0, 0.9, 1),
  item('right-gap', 1.1, 0, 2, 1),
], 'jma', viewport)) process.exit(12);
if (coverageContainsViewport([
  item('bottom', 0, 0, 2, 0.45),
  item('top', 0, 0.55, 2, 1),
], 'jma', viewport)) process.exit(13);
if (coverageContainsViewport([], 'jma', viewport)) process.exit(14);
"""
        subprocess.run(
            ["node", "--input-type=module", "-e", script],
            check=True,
        )

    def test_loader_uses_manifest_time_and_canonical_token(self):
        s = Path("assets/weather-map-v2-tile-loader.js").read_text()
        self.assertIn("nearestValidTime", s)
        self.assertIn("providerSupportsField", s)
        self.assertIn("validTimeToken", s)
        self.assertIn("utcTimeMs", s)
        self.assertIn("toISOString().slice(0, 16)", s)
        utc_body = s.split("function utcTimeMs(value) {", 1)[1].split(
            "}\n\nexport function nearestValidTime", 1
        )[0]
        self.assertIn(r"/(?:Z|[+-]\d\d:\d\d)$/", utc_body)
        self.assertNotIn(r"[+-]\\d", utc_body)

    def test_loader_dedupes_shared_tile_boundaries(self):
        s = Path("assets/weather-map-v2-tile-loader.js").read_text()
        self.assertIn("dedupeSamples", s)
        self.assertIn("toFixed(6)", s)

    def test_v2_page_prefers_native_jma_tiles_safely(self):
        s = Path("assets/weather-map-v2.js").read_text()
        self.assertIn("tryNativeJma", s)
        self.assertIn("providerSupportsField", s)
        self.assertIn("nearestValidTime", s)
        self.assertIn("regionForView(currentView)", s)
        self.assertIn("native-tile", s)
        self.assertIn("JMA MSM native tiles", s)
        self.assertIn("coverage:result.coverage || coverage", s)
        self.assertIn("if(!result.loaded.length || !result.complete) return false", s)
        self.assertIn("cachePut(bboxKey('jma',field,coverage),item)", s)
        self.assertIn("applyDataset(item,'native-tile')", s)
        self.assertNotIn("native-tile-partial", s)
        self.assertIn("coverageComplete:true", s)
        self.assertIn("資料不完整", s)
        self.assertIn("addEventListener('change', () => schedule(true))", s)


if __name__ == "__main__":
    unittest.main()
