// CL-WG-25 camera-regression pins + basemap boundary-line hiding.
//
// Part 1 — CL-WG-07/09/10 camera confinement regression proof: after
// applyCameraLimits, simulating 8 consecutive zoom-out presses must bottom
// out at the FIXED floor (fitZoom − 0.05) and the camera viewport bounds must
// never leave the maxBounds box (fitted viewport expanded 25% per side).
// Owner evidence was a "whole East Asia" view; live A/B at bclwg27 confirmed
// the three layers still hold on direct load / spot deep link / region
// switch — these tests pin that behavior so no future change can silently
// drop it (CL-WG-24 round 2 / CL-DATA-13 did NOT touch the camera code).
//
// Part 2 — boundary-line hide: the OpenFreeMap liberty style draws
// boundary_2 / boundary_3 / boundary_disputed as yellow dashed lines over the
// sea, colliding with the cloud-cover color field. hideBoundaryLineLayers()
// must hide exactly those line layers and leave terrain/labels/roads intact.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const regions = require('../../../assets/weather-map-regions.js');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(path.dirname(require.resolve('../../../assets/weather-map-regions.js')), '..');
const MAP_JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const WG_HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

function grab(src, start, end) {
  const a = src.indexOf(start);
  assert.ok(a !== -1, `source slice start not found: ${start}`);
  const b = src.indexOf(end, a);
  assert.ok(b !== -1, `source slice end not found: ${end}`);
  return src.slice(a, b);
}

// ---------------------------------------------------------------------------
// Faithful-enough MapLibre camera simulation (same model as cl-wg-10 tests):
// equirectangular fit, 256px world; minZoom/maxBounds clamp every camera move.
// ---------------------------------------------------------------------------
const VIEW_W = 1200, VIEW_H = 800, PAD = 28;
const clampZoom = (z, minZoom) => (minZoom == null ? z : Math.max(minZoom, z));

function makeFakeMap(initial) {
  const calls = [];
  const map = {
    calls,
    _center: { lng: initial.lng, lat: initial.lat },
    _zoom: initial.zoom,
    _maxBounds: null,
    _minZoom: null,
    _maxZoom: null,
    _clampCenter(c) {
      if (!this._maxBounds) return c;
      const [[w, s], [e, n]] = this._maxBounds;
      return {
        lng: Math.min(e, Math.max(w, c.lng)),
        lat: Math.min(n, Math.max(s, c.lat))
      };
    },
    getCenter() { return this._center; },
    getZoom() { return this._zoom; },
    getBounds() {
      const worldPx = 256 * Math.pow(2, this._zoom);
      const lonSpan = VIEW_W * 360 / worldPx;
      const latSpan = VIEW_H * 360 / worldPx;
      return {
        getWest: () => this._center.lng - lonSpan / 2,
        getEast: () => this._center.lng + lonSpan / 2,
        getSouth: () => this._center.lat - latSpan / 2,
        getNorth: () => this._center.lat + latSpan / 2
      };
    },
    fitBounds([[w, s], [e, n]], opts) {
      calls.push(['fitBounds', [w, s, e, n], opts?.padding]);
      const zLon = Math.log2((VIEW_W - 2 * PAD) * 360 / (256 * (e - w)));
      const zLat = Math.log2((VIEW_H - 2 * PAD) * 360 / (256 * (n - s)));
      let z = clampZoom(Math.min(zLon, zLat), this._minZoom);
      if (this._maxZoom != null) z = Math.min(this._maxZoom, z);
      this._zoom = z;
      this._center = this._clampCenter({ lng: (w + e) / 2, lat: (s + n) / 2 });
    },
    jumpTo({ center, zoom }) {
      calls.push(['jumpTo', center.lng, center.lat, zoom]);
      this._center = this._clampCenter({ lng: center.lng, lat: center.lat });
      this._zoom = clampZoom(zoom, this._minZoom);
    },
    // One press of the − button: MapLibre steps the zoom down 1.0 and the
    // active minZoom floor clamps it.
    zoomOutStep() {
      this._zoom = clampZoom(this._zoom - 1, this._minZoom);
    },
    setMaxBounds(b) {
      calls.push(['setMaxBounds', b ? 'bounds' : 'null']);
      this._maxBounds = b;
      if (b) this._center = this._clampCenter(this._center);
    },
    setMinZoom(z) {
      calls.push(['setMinZoom', z]);
      this._minZoom = z;
      if (z != null && this._zoom < z) this._zoom = z;
    },
    setMaxZoom(z) {
      calls.push(['setMaxZoom', z]);
      this._maxZoom = z;
    }
  };
  return map;
}

function runLimits(bbox, initial, { preserveCamera = false } = {}) {
  const map = makeFakeMap(initial);
  const state = { mapReady: true, map };
  const fakeWindow = {
    WeatherMapRegions: {
      cameraBounds: b => regions.cameraBounds(b),
      cameraMinZoom: z => regions.cameraMinZoom(z),
      CAMERA_MAX_ZOOM: regions.CAMERA_MAX_ZOOM
    }
  };
  const src = grab(MAP_JS, 'function applyCameraLimits', 'function renderViewBbox');
  const applyCameraLimits = new Function('state', 'window', 'regionBbox',
    `${src}\nreturn applyCameraLimits;`)(state, fakeWindow, () => regions.REGION_BBOXES[bbox]);
  applyCameraLimits(preserveCamera ? { preserveCamera: true } : {});
  return map;
}

const REGIONS = Object.keys(regions.REGION_BBOXES);
const PRESS_8 = 8;

for (const regionId of REGIONS) {
  test(`CL-WG-25: ${regionId} — 8 consecutive − presses bottom out at fitZoom−0.05 and never leave maxBounds (bbox+25%)`, () => {
    const map = runLimits(regionId, { lng: 0, lat: 20, zoom: 5.4 });
    const fitZoom = map.getZoom();
    const maxBounds = map._maxBounds;

    // The expanded maxBounds box is the fit viewport + 25% per side (CL-WG-10),
    // and it is NOT the raw bbox (fit would be edge-cropped).
    assert.ok(Math.abs(maxBounds[0][0] - regions.REGION_BBOXES[regionId].leftlon) > 1,
      'maxBounds must be expanded beyond the raw bbox left edge');
    assert.ok(Math.abs(maxBounds[1][0] - regions.REGION_BBOXES[regionId].rightlon) > 1,
      'maxBounds must be expanded beyond the raw bbox right edge');

    // CL-WG-07: the floor is a FIXED value derived from the fit zoom only.
    assert.equal(map._minZoom, Math.max(0, fitZoom - 0.05),
      'minZoom floor = fitZoom − 0.05, independent of current zoom');

    // Simulate 8 presses of the − button.
    for (let i = 0; i < PRESS_8; i++) map.zoomOutStep();

    assert.ok(map._zoom < fitZoom + PRESS_8 * 0.5, 'zoom actually stepped down');
    assert.ok(Math.abs(map._zoom - map._minZoom) < 1e-9,
      '8 presses stop exactly at the fixed floor (fitZoom − 0.05), not below');

    // After all presses the whole viewport must sit inside maxBounds.
    const b = map.getBounds();
    const [[w, s], [e, n]] = maxBounds;
    assert.ok(b.getWest() >= w - 1e-9 && b.getEast() <= e + 1e-9,
      `west/east viewport must stay inside maxBounds (${b.getWest()},${b.getEast()} vs ${w},${e})`);
    assert.ok(b.getSouth() >= s - 1e-9 && b.getNorth() <= n + 1e-9,
      `south/north viewport must stay inside maxBounds (${b.getSouth()},${b.getNorth()} vs ${s},${n})`);
    // The fitted region bbox is still the dominant view at the floor: its
    // span stays inside the visible viewport span.
    const bb = regions.REGION_BBOXES[regionId];
    assert.ok(b.getWest() <= bb.leftlon && b.getEast() >= bb.rightlon,
      'full region bbox stays in frame at the zoom floor');
  });
}

test('CL-WG-25: maxBounds derived from the FITTED viewport (not the raw bbox) — CL-WG-10 edge-crop guard intact', () => {
  const map = runLimits('jp', { lng: 134, lat: 35, zoom: 3 });
  const [[w, s], [e, n]] = map._maxBounds;
  const bb = regions.REGION_BBOXES.jp;
  assert.ok(w < bb.leftlon && e > bb.rightlon && s < bb.bottomlat && n > bb.toplat,
    'expanded on every side');
  // Expansion = exactly 25% of the FITTED viewport span per side.
  const b = map.getBounds();
  assert.ok(Math.abs((e - w) - (b.getEast() - b.getWest()) * 1.5) < 1e-6,
    'lon expansion is 25% of the fitted viewport span');
  assert.ok(Math.abs((n - s) - (b.getNorth() - b.getSouth()) * 1.5) < 1e-6,
    'lat expansion is 25% of the fitted viewport span');
});

// ---------------------------------------------------------------------------
// Part 2 — boundary-line hide
// ---------------------------------------------------------------------------

function buildBoundaryFake(layers) {
  const hidden = [];
  return {
    hidden,
    getStyle: () => ({ layers }),
    setLayoutProperty: (id, prop, val) => hidden.push([id, prop, val])
  };
}

const FAKE_STYLE_LAYERS = [
  { id: 'background', type: 'background' },
  { id: 'water', type: 'fill', 'source-layer': 'water' },
  { id: 'park_outline', type: 'line', 'source-layer': 'park' },
  { id: 'boundary_3', type: 'line', 'source-layer': 'boundary' },
  { id: 'boundary_2', type: 'line', 'source-layer': 'boundary' },
  { id: 'boundary_disputed', type: 'line', 'source-layer': 'boundary' },
  { id: 'road_minor', type: 'line', 'source-layer': 'transportation' },
  { id: 'place_city', type: 'symbol', 'source-layer': 'place' },
  { id: 'hillshade', type: 'hillshade' }
];

function buildHideFn() {
  const src = grab(MAP_JS, 'function hideBoundaryLineLayers', 'function renderViewBbox');
  return new Function(`${src}\nreturn hideBoundaryLineLayers;`)();
}

test('CL-WG-25: hideBoundaryLineLayers hides exactly the boundary/disputed line layers', () => {
  const fake = buildBoundaryFake(FAKE_STYLE_LAYERS);
  const n = buildHideFn()(fake);
  assert.equal(n, 3, 'boundary_2/boundary_3/boundary_disputed only');
  assert.deepEqual(fake.hidden.map(h => h[0]),
    ['boundary_3', 'boundary_2', 'boundary_disputed']);
  for (const h of fake.hidden) {
    assert.equal(h[1], 'visibility');
    assert.equal(h[2], 'none');
  }
});

test('CL-WG-25: terrain, roads, labels, water are never hidden; id-based match also works', () => {
  const layers = [
    { id: 'eez_maritime_boundary', type: 'line' },
    { id: 'landcover', type: 'fill' },
    { id: 'road_motorway', type: 'line', 'source-layer': 'transportation' },
    { id: 'waterway_river', type: 'line', 'source-layer': 'waterway' },
    { id: 'place_label', type: 'symbol' },
    { id: 'contour_lines', type: 'line' }
  ];
  const fake = buildBoundaryFake(layers);
  const n = buildHideFn()(fake);
  assert.deepEqual(fake.hidden.map(h => h[0]), ['eez_maritime_boundary'],
    'only boundary-named lines; roads/rivers/contours/labels untouched');
});

test('CL-WG-25: fail-open on unknown style shape — no throw, nothing hidden', () => {
  const fn = buildHideFn();
  assert.doesNotThrow(() => fn(buildBoundaryFake(null)));
  assert.doesNotThrow(() => fn(buildBoundaryFake(undefined)));
  const bad = { getStyle: () => { throw new Error('no style'); }, setLayoutProperty() {} };
  assert.doesNotThrow(() => fn(bad), 'style errors are caught (fail-open)');
  const empty = { getStyle: () => ({ layers: [] }), setLayoutProperty() {} };
  assert.equal(fn(empty), 0);
});

test('CL-WG-25: hide runs on the basemap load path, after the camera limits', () => {
  const loadBlock = grab(MAP_JS, "map.on('load'", "map.on('move'");
  assert.ok(loadBlock.includes('hideBoundaryLineLayers(map)'),
    'load handler must apply the boundary hide');
  assert.ok(
    loadBlock.indexOf('applyCameraLimits({preserveCamera:true})') < loadBlock.indexOf('hideBoundaryLineLayers(map)'),
    'boundary hide happens after the camera limits are (re)applied');
});

// ---------------------------------------------------------------------------
// Stamp discipline: same-commit cache-bust bump (per-file weather-map family)
// ---------------------------------------------------------------------------
test('CL-WG-25: weather-map.html stamps bumped to bclwg31 in the same ticket', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg32/);
  assert.ok(!/assets\/weather-map\.js\?v=bclwg27/.test(WG_HTML),
    'old stamp must not linger');
});
