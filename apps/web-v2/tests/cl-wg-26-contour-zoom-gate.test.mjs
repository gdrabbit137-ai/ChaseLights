// CL-UI-113 (supersedes CL-WG-26): the 50% cloud threshold contour is REMOVED.
// Root cause (owner, third report in the series CL-WG-25 -> CL-UI-107 ->
// CL-UI-113): the yellow dashed rgba(254,240,138) canvas contour over open
// sea kept being read as basemap noise / an admin boundary. Headless A/B
// proved no style layer draws it (boundary_2/3, boundary_disputed, park,
// park_outline all hidden -> dashes persist; contour disabled -> dashes gone)
// and the zoom gate only suppressed the <6 zoom degenerate case.
// Contract now:
//  (1) No contour code may return: no drawCloudThresholdContour /
//      contourCrossing / cloudContourGate* / CONTOUR_MIN_* / the yellow
//      stroke color / the __weatherGridContourGate hook anywhere.
//  (2) The legend 50% key and its CSS are retired.
//  (3) The cell painters' source adjacency (used by cl-wg-18 grabs) stays
//      intact: drawBilinearSubcells is immediately followed by
//      drawCircularDirectionSubcells.
//  (4) Live assertion (five model layers x the owner-report viewpoint):
//      apps/web-v2/tests/cl-ui-113-yellow-dash-free.test.mjs.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const CSS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.css'), 'utf8');
const HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');
const PALETTE = fs.readFileSync(path.join(ROOT, 'assets/weather-map-palette.js'), 'utf8');

function grab(src, startMarker, endMarker) {
  const a = src.indexOf(startMarker);
  assert.ok(a >= 0, `start marker not found: ${startMarker}`);
  const b = src.indexOf(endMarker, a);
  assert.ok(b > a, `end marker not found: ${endMarker}`);
  return src.slice(a, b);
}

test('CL-UI-113: no contour drawing code remains in weather-map.js', () => {
  for (const banned of [
    'drawCloudThresholdContour',
    'contourCrossing',
    'cloudContourGateAllowed',
    'cloudContourGateState',
    'shouldDrawCloudContour',
    'CONTOUR_MIN_ZOOM',
    'CONTOUR_MIN_CELL_PX',
    'window.__weatherGridContourGate',
    'rgba(254,240,138',
    'setLineDash([2,3])',
    'refreshCloudThresholdKey',
    'cloudThresholdKeyHtml',
    'CLOUD_THRESHOLD_LABELS',
    'CLOUD_THRESHOLD_ZOOM_HINTS'
  ]) {
    assert.ok(!JS.includes(banned), `contour remnant must be gone: ${banned}`);
  }
});

test('CL-UI-113: the 50% legend key and its CSS are retired', () => {
  assert.ok(!JS.includes('50% 雲量分界'), 'zh key gone');
  assert.ok(!JS.includes('50% cloud boundary'), 'en key gone');
  assert.ok(!JS.includes('50% 雲量境界'), 'ja key gone');
  assert.ok(!JS.includes('請放大檢視'), 'zh hint gone');
  assert.ok(!CSS.includes('cloud-threshold-key'), 'css key rules gone');
  assert.ok(!CSS.includes('cloud-threshold-swatch'), 'css swatch rules gone');
  // The CL-WG-28 midline marker on the gradient bar is NOT part of the
  // contour feature and must survive.
  assert.match(JS, /<span class="cloud-midline" aria-hidden="true"><\/span>/);
});

test('CL-UI-113: cell-painter source adjacency intact (cl-wg-18 grab markers)', () => {
  const src = grab(JS, 'function drawBilinearSubcells(', 'function drawCircularDirectionSubcells(');
  assert.match(src, /return drawn;/);
  const direction = grab(JS, 'function drawCircularDirectionSubcells(', 'function drawProviderBoundary(');
  assert.match(direction, /return drawn;/);
  // The draw() flow keeps its honest render-state probes (CL-UI-109 P2-4).
  const drawBody = grab(JS, 'function draw(){', 'function windVectorStep(){');
  assert.match(drawBody, /state\.lastCanvasPainted=canvasHasFieldPaint\(\);/);
});

test('CL-UI-113: cache-bust stamps bumped (?v=bclwg47)', () => {
  assert.match(HTML, /assets\/weather-map\.js\?v=bclwg47/);
  assert.match(HTML, /assets\/weather-map\.css\?v=bclwg47/);
  assert.doesNotMatch(HTML, /weather-map\.js\?v=bclwg45/);
});

test('CL-UI-113: palette module carries the cloudLow contrast ladder', () => {
  // New saturated light-end bands + dedicated denser opacity ladder/cap.
  assert.match(PALETTE, /LOW_CLOUD_OPACITY_STOPS/);
  assert.match(PALETTE, /LOW_CLOUD_MAX_OVERLAY_ALPHA=\.\d+/);
  assert.match(PALETTE, /hsl\(204 40% 74%\)/, '50-70 band saturated');
  assert.match(PALETTE, /hsl\(204 28% 89%\)/, '85-100 band saturated');
  assert.match(PALETTE, /PALETTE_VERSION = 'wg22-clui113'/);
});
