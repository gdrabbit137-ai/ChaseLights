// CL-WG-26: contour zoom gate.
// The 50% cloud contour (rgba(254,240,138) dash) degenerates into dense
// dotted noise at low zoom levels when the low-cloud field hovers near 50%
// over open sea (CL-WG-25 diagnosis). Gate: the contour is drawn only when
// the camera zoom is >= 6 AND one grid cell measures >= 10px on screen.
// Below the gate the legend keeps the 50% key with a trilingual zoom hint,
// and zoom changes flip the legend key in real time (draw() runs on 'move').
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const CSS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.css'), 'utf8');
const HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

function grab(src, startMarker, endMarker) {
  const a = src.indexOf(startMarker);
  assert.ok(a >= 0, `start marker not found: ${startMarker}`);
  const b = src.indexOf(endMarker, a);
  assert.ok(b > a, `end marker not found: ${endMarker}`);
  return src.slice(a, b);
}

test('gate constants and decision rule: zoom>=6 AND cellPx>=10', () => {
  assert.match(JS, /const CONTOUR_MIN_ZOOM=6;/);
  assert.match(JS, /const CONTOUR_MIN_CELL_PX=10;/);
  const src = grab(JS, 'const CONTOUR_MIN_ZOOM=6;', 'function contourCrossing(');
  const fn = new Function(`${src}\n  return cloudContourGateAllowed;`)();
  // Low zoom / small cells: gate closed.
  assert.equal(fn(5, 11.4), false, 'zoom<6 hides the contour even if cells are big');
  assert.equal(fn(6, 4.5), false, 'cellPx<10 hides the contour even if zoom>=6');
  assert.equal(fn(5.9, 2), false);
  // Gate open only when both criteria hold.
  assert.equal(fn(6, 10), true);
  assert.equal(fn(8, 11.4), true);
  // Canvas fallback (no live camera): previous always-draw behavior.
  assert.equal(fn(null, null), true, 'missing camera keeps pre-gate behavior');
  assert.equal(fn(NaN, 12), true);
});

test('contour drawing in draw() is gated by the live camera probe', () => {
  assert.match(JS, /function cloudContourGateState\(data\)/);
  assert.match(JS, /function shouldDrawCloudContour\(data\)/);
  assert.match(JS, /state\.map\.project\(\[center\.lng-stepLon\/2,center\.lat-stepLat\/2\]\)/,
    'cellPx comes from the real MapLibre projection at the map center');
  assert.match(JS, /const gate=cloudContourGateState\(data\);\s*try\{ window\.__weatherGridContourGate=\{\.\.\.gate,layer:state\.layer\}; \}catch\(_\)\{\}\s*if\(gate\.allowed\)\{\s*drawCloudThresholdContour\(data,vals,50,visibleView\);/,
    'draw() skips drawCloudThresholdContour below the gate');
});

test('legend: trilingual 50% key with zoom hint below the gate', () => {
  assert.match(JS, /CLOUD_THRESHOLD_LABELS=\{\s*'zh-TW':'50% 雲量分界',\s*'en':'50% cloud boundary',\s*'ja':'50% 雲量境界'\s*\}/);
  assert.match(JS, /CLOUD_THRESHOLD_ZOOM_HINTS=\{\s*'zh-TW':'請放大檢視',\s*'en':'Zoom in to view the contour',\s*'ja':'拡大してご覧ください'\s*\}/);
  // No simplified han in the ja copy.
  const jaHint = JS.match(/'ja':'拡大してご覧ください'/);
  assert.ok(jaHint, 'ja hint present');
  assert.match(JS, /const thresholdKey=isCloud\?cloudThresholdKeyHtml\(activeDataset\(state\.layer\)\)\.html:'';/,
    'updateLegend renders the gated trilingual key (CL-INT-80: inside the CL-WG-28 legend-expanded panel)');
  assert.match(JS, /data-zoom-gated="\$\{gated\}"/);
  assert.match(CSS, /\.cloud-threshold-hint\{color:#cbd5e1/);
});

test('zoom changes flip the legend key in real time (draw() wiring)', () => {
  const drawBody = grab(JS, 'function draw(){', 'function windVectorStep(){');
  assert.match(drawBody, /refreshCloudThresholdKey\(\);/,
    'draw() (fired by map.on("move") on every camera change) refreshes the legend key');
  const refreshBody = grab(JS, 'function refreshCloudThresholdKey(){', 'function updateLegend(cfg){');
  assert.match(refreshBody, /host\.dataset\.zoomGated===String\(next\.gated\)/,
    'the DOM is only touched when the gate state flips');
  assert.match(refreshBody, /host\.replaceWith\(wrap\.firstElementChild\);/);
  assert.match(JS, /map\.on\('move',\(\)=>\{[\s\S]*?draw\(\);/,
    'map zoom/move events re-run draw(), which re-evaluates the gate');
  assert.match(JS, /window\.__weatherGridContourGate=/,
    'live gate hook for headless verification (same spirit as __weatherGridCamera)');
});

test('cache-bust stamps bumped in the same ticket (?v=bclwg30)', () => {
  assert.match(HTML, /assets\/weather-map\.js\?v=bclwg30/);
  assert.match(HTML, /assets\/weather-map\.css\?v=bclwg30/);
  assert.doesNotMatch(HTML, /weather-map\.js\?v=bclwg28/);
});
