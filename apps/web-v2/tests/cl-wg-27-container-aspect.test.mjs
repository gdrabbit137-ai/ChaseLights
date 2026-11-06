// CL-WG-27 — weather-map container aspect-ratio hugs the region bbox's
// Web Mercator visual proportion.
//
// CL-WG-25 diagnosis: the fixed 1.46:1 .map-wrap container letterboxed the
// tw bbox (105–145E / 5–40N, Mercator aspect ≈ 1.033) and exposed ~22° of
// surplus ocean horizontally. Fix: the container aspect follows the active
// region via a CSS variable set from a pure per-region table.
//
// Pins here:
//   1. The Mercator aspect values (independently recomputed from
//      WeatherMapRegions.REGION_BBOXES) and their stability as a table.
//   2. The runtime wiring: weather-map.js sets --wg-map-aspect on .map-wrap
//      from WeatherMapRegions.regionMercatorAspect, and weather-map.css
//      consumes the variable on BOTH the desktop rule and the mobile
//      (≤600px) rule — no fixed 1.46/1 or 1.12/1 ratio may survive.
//   3. Camera-fit consequence: with the container aspect matched to the
//      bbox's Mercator proportion, the fitted viewport shows the full bbox
//      with essentially NO horizontal letterbox surplus (the CL-WG-25
//      ~22° surplus must be gone).
//   4. Cache-bust stamps bumped in the same ticket (bclwg31).
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const regions = require('../../../assets/weather-map-regions.js');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(path.dirname(require.resolve('../../../assets/weather-map-regions.js')), '..');
const MAP_JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const MAP_CSS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.css'), 'utf8');
const WG_HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

// --- independent recomputation (deliberately NOT via the module) ----------
function mercatorAspect({ leftlon, rightlon, bottomlat, toplat }) {
  const dLon = (rightlon - leftlon) * Math.PI / 180;
  const y = (lat) => Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360));
  return dLon / (y(toplat) - y(bottomlat));
}

const PINNED = {
  tw: 1.0335,
  jp: 0.8826,
  us: 1.7410,
  ak: 0.8162,
  hi: 1.4298
};

test('CL-WG-27: region Mercator aspects recomputed independently match the module table', () => {
  for (const [id, bbox] of Object.entries(regions.REGION_BBOXES)) {
    const expect = mercatorAspect(bbox);
    const got = regions.regionMercatorAspect(id);
    assert.ok(Number.isFinite(got) && got > 0, `${id} aspect must be finite positive`);
    assert.ok(Math.abs(got - expect) < 1e-9, `${id} module value ${got} != recomputed ${expect}`);
    assert.ok(Math.abs(got - PINNED[id]) < 5e-4,
      `${id} Mercator aspect drifted: got ${got}, pinned ${PINNED[id]}`);
  }
  // tw is the primary region: near-square, NOT 1.46 — the CL-WG-25 letterbox
  // cause must stay out of the table.
  assert.ok(Math.abs(regions.regionMercatorAspect('tw') - 1.46) > 0.3);
});

test('CL-WG-27: weather-map.js wires --wg-map-aspect from the region aspect on activateRegion', () => {
  assert.match(MAP_JS, /function applyRegionAspect\(/);
  assert.match(MAP_JS, /regionMercatorAspect\(regionId\)/);
  assert.match(MAP_JS, /--wg-map-aspect/);
  // every entry path lands: the only region-activation funnel is activateRegion
  assert.match(MAP_JS, /state\.region = regionId;\s*\n\s*applyRegionAspect\(regionId\);/);
});

test('CL-WG-27: weather-map.css consumes the variable on desktop AND mobile, no fixed ratios left', () => {
  const wrapRules = [...MAP_CSS.matchAll(/\.map-wrap\{[^}]*\}/g)].map(m => m[0]);
  assert.ok(wrapRules.length >= 2, 'desktop + mobile .map-wrap rules expected');
  for (const rule of wrapRules) {
    assert.match(rule, /aspect-ratio:var\(--wg-map-aspect/);
  }
  assert.doesNotMatch(MAP_CSS, /aspect-ratio:1\.46\/1/);
  assert.doesNotMatch(MAP_CSS, /aspect-ratio:1\.12\/1/);
});

test('CL-WG-27: aspect-matched container fit shows the full tw bbox with no horizontal letterbox surplus', () => {
  // Equirectangular-approximation fit simulation over Mercator-projected
  // pixels (same model family as cl-wg-10/cl-wg-25 tests): world is 256px *
  // 2^zoom; lon maps linearly, lat via Mercator y. fitBounds picks the zoom
  // where the bbox first fits inside (view - 2*padding) in BOTH dimensions.
  const PAD = 28;
  const W = 1200, H = 1200 / PINNED.tw; // container aspect matched to tw
  const bbox = regions.REGION_BBOXES.tw;
  const mercY = (lat) => Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360));

  const fitZoom = () => {
    // fitBounds lands where the bbox's larger pixel extent first FILLS the
    // padded viewport (growing zoom from 0 until it no longer fits).
    const target = W - 2 * PAD;
    let z = 0;
    let last = z;
    for (; z < 14; z += 0.005) {
      const world = 256 * 2 ** z;
      const pxW = ((bbox.rightlon - bbox.leftlon) / 360) * world;
      const pxH = (mercY(bbox.toplat) - mercY(bbox.bottomlat)) / (2 * Math.PI) * world;
      if (Math.max(pxW, pxH) > target) return last;
      last = z;
    }
    return last;
  };
  const z = fitZoom();
  const world = 256 * 2 ** z;
  const viewLonSpan = (W / world) * 360;
  const surplusDeg = viewLonSpan - (bbox.rightlon - bbox.leftlon);
  // Old fixed 1.46:1 container showed ~22° of surplus ocean; the matched
  // container must show essentially none (padding-only residual).
  // Residual surplus = fitBounds padding only (2*28px / 1200px * 40deg is
  // about 1.9deg, plus zoom quantization); the old fixed 1.46:1 container
  // showed ~22deg.
  assert.ok(surplusDeg < 2.5, `horizontal surplus ${surplusDeg.toFixed(2)}deg must be < 2.5deg`);
  // And the fitted view must still fully contain the bbox.
  assert.ok(surplusDeg >= 0);
});

test('CL-WG-27: weather-map.html stamps bumped to bclwg31 in the same ticket', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg31/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg31/);
  assert.match(WG_HTML, /assets\/weather-map-regions\.js\?v=bclwg30/);
  assert.ok(!/weather-map\.js\?v=bclwg28/.test(WG_HTML), 'old js stamp must be replaced');
  assert.ok(!/weather-map-regions\.js\?v=bclwg13/.test(WG_HTML), 'old regions stamp must be replaced');
});
