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
        self.assertIn("published_regions", s)
        self.assertIn("!publishedRegions.includes(region)", s)
        self.assertIn("!Array.isArray(published) || !published.length", s)
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

    def test_native_cell_selection_requires_published_run_contract(self):
        script = r"""
import fs from 'node:fs';
const source = fs.readFileSync('assets/weather-map-v2-tile-loader.js', 'utf8');
const url = 'data:text/javascript;base64,' + Buffer.from(source).toString('base64');
const { cellsForViewport } = await import(url);
const viewport = { w: 120, s: 23, e: 122, n: 25 };
const cell = (id) => ({
  id,
  bbox: { west: 120, south: 23, east: 122, north: 25 },
  providers: {
    jma: {
      url_template: 'weathergrid/v2/jma/current/{valid_time}/' + id + '.json',
      coverage_bbox: { west: 120, south: 23, east: 122, north: 25 },
    },
  },
});
const base = { regions: { tw: { cells: [cell('tw_a'), cell('tw_b')] } } };

if (cellsForViewport(base, 'tw', viewport, 'jma').length !== 0) process.exit(21);

const noRegions = structuredClone(base);
noRegions.provider_runs = { jma: { published_cell_ids: ['tw_a'] } };
if (cellsForViewport(noRegions, 'tw', viewport, 'jma').length !== 0) process.exit(22);

const wrongRegion = structuredClone(base);
wrongRegion.provider_runs = {
  jma: { published_regions: ['jp'], published_cell_ids: ['tw_a'] },
};
if (cellsForViewport(wrongRegion, 'tw', viewport, 'jma').length !== 0) process.exit(23);

const noCells = structuredClone(base);
noCells.provider_runs = {
  jma: { published_regions: ['tw'], published_cell_ids: [] },
};
if (cellsForViewport(noCells, 'tw', viewport, 'jma').length !== 0) process.exit(24);

const published = structuredClone(base);
published.provider_runs = {
  jma: { published_regions: ['tw'], published_cell_ids: ['tw_a'] },
};
const selected = cellsForViewport(published, 'tw', viewport, 'jma');
if (selected.length !== 1 || selected[0].id !== 'tw_a') process.exit(25);
"""
        subprocess.run(
            ["node", "--input-type=module", "-e", script],
            check=True,
        )

    def test_adaptive_fallback_sampling_is_denser_and_bounded(self):
        script = r"""
import fs from 'node:fs';
const source = fs.readFileSync('assets/weather-map-v2-sampling.js', 'utf8');
const url = 'data:text/javascript;base64,' + Buffer.from(source).toString('base64');
const { adaptiveGridShape, sampleGrid, chunkPoints } = await import(url);

const desktop = adaptiveGridShape({width: 1365, height: 800, zoom: 6});
if (desktop.cols * desktop.rows <= 42) process.exit(31);
if (desktop.cols * desktop.rows > 800) process.exit(32);

const wide = sampleGrid(
  {w: 109.8, s: 17.0, e: 132.2, n: 30.2},
  {width: 1365, height: 800, zoom: 6, minLonStepDeg: 0.0625, minLatStepDeg: 0.05},
);
if (wide.points.length <= 200) process.exit(33);
if (wide.points.length > 800) process.exit(34);
if (!(wide.dx < 1.0 && wide.dy < 1.0)) process.exit(35);

const tightGfs = sampleGrid(
  {w: 121.0, s: 23.0, e: 121.8, n: 23.8},
  {width: 1365, height: 800, zoom: 10, minLonStepDeg: 0.25, minLatStepDeg: 0.25},
);
if (tightGfs.points.length > 25) process.exit(36);

const chunks = chunkPoints(Array.from({length: 205}, (_, i) => ({i})), 80);
if (chunks.length !== 3 || chunks[0].length !== 80 || chunks[2].length !== 45) process.exit(37);
if (chunks.some((chunk) => chunk.length > 100)) process.exit(38);
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
