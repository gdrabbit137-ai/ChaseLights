// CL-WG-10 region-switch camera regression: switching regions must fit the
// camera to the NEW region bbox, unencumbered by the previous region's
// maxBounds/minZoom. Owner evidence: after switching to 夏威夷 (hi), the view
// was almost all Pacific with the islands only at the viewport edge — the old
// region's limits clamped the fit. The hi bbox is 160.3–154.8°W / 18.8–22.4°N;
// after fit the islands must be centered and fully in frame.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const regions = require('../../../assets/weather-map-regions.js');
const fs = require('node:fs');
const path = require('node:path');

const MAP_JS = fs.readFileSync(
  path.join(path.dirname(require.resolve('../../../assets/weather-map-regions.js')),
    'weather-map.js'), 'utf8');

function grab(start, end) {
  const a = MAP_JS.indexOf(start);
  assert.ok(a !== -1, `source slice start not found: ${start}`);
  const b = MAP_JS.indexOf(end, a);
  assert.ok(b !== -1, `source slice end not found: ${end}`);
  return MAP_JS.slice(a, b);
}

// ---------------------------------------------------------------------------
// Faithful-enough MapLibre camera simulation: every camera move is constrained
// by the currently active maxBounds/minZoom, exactly the mechanism that broke
// region switches. equirectangular fit: pick the largest zoom (fractional)
// whose lon/lat span fits the viewport minus padding.
// ---------------------------------------------------------------------------
const VIEW_W = 1200, VIEW_H = 800, PAD = 28;
const clampZoom = (z, minZoom) =>
  minZoom == null ? z : Math.max(minZoom, z);

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
    fitBounds([[w, s], [e, n]], opts) {
      calls.push(['fitBounds', [w, s, e, n], opts?.padding]);
      const spanLon = e - w, spanLat = n - s;
      const zLon = Math.log2((VIEW_W - 2 * PAD) * 360 / (256 * spanLon));
      const zLat = Math.log2((VIEW_H - 2 * PAD) * 360 / (256 * spanLat));
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
    setMaxBounds(b) {
      calls.push(['setMaxBounds', b ? 'bounds' : 'null']);
      this._maxBounds = b;
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

function buildApplyCameraLimits() {
  const src = grab('function applyCameraLimits', 'function renderViewBbox');
  return new Function('state', 'window', 'regionBbox',
    `${src}\nreturn applyCameraLimits;`);
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
  const applyCameraLimits = buildApplyCameraLimits()(state, fakeWindow,
    () => regions.REGION_BBOXES[bbox]);
  applyCameraLimits(preserveCamera ? { preserveCamera: true } : {});
  return map;
}

const HI_CENTER = {
  lng: (-160.3 + -154.8) / 2,
  lat: (18.8 + 22.4) / 2
};

test('CL-WG-10: switching to hi fits the hi bbox centered, not clamped by the old region', () => {
  // Camera state after browsing Taiwan (tw limits active, camera at the fitted
  // tw view), then the user clicks the 夏威夷 card.
  const twFit = runLimits('tw', { lng: 120.5, lat: 24, zoom: 5.4 });
  const afterTw = { lng: twFit.getCenter().lng, lat: twFit.getCenter().lat, zoom: twFit.getZoom() };
  assert.ok(Math.abs(afterTw.zoom - twFit.getZoom()) < 1e-9);

  // The hi fitZoom is HIGHER than the tw fitZoom (hi is a much smaller box) —
  // the old tw minZoom floor and tw maxBounds are exactly what used to wedge
  // the camera.
  const hi = runLimits('hi', afterTw);
  assert.ok(Math.abs(hi.getCenter().lng - HI_CENTER.lng) < 1e-9,
    `hi switch must center on the hi bbox (got lng ${hi.getCenter().lng})`);
  assert.ok(Math.abs(hi.getCenter().lat - HI_CENTER.lat) < 1e-9,
    `hi switch must center on the hi bbox (got lat ${hi.getCenter().lat})`);
  // The hi floor derives from the hi fitZoom, not from the camera the switch
  // arrived with.
  const oldCalls = hi.calls.map(c => c[0]);
  const firstFit = hi.calls.findIndex(c => c[0] === 'fitBounds');
  const cleared = hi.calls.findIndex(c => c[0] === 'setMaxBounds' && c[1] === 'null');
  assert.ok(cleared !== -1, 'old region maxBounds must be cleared (setMaxBounds(null))');
  assert.ok(cleared < firstFit,
    'the previous region limits must be cleared BEFORE fitting the new region');
  // Full hi bbox (160.3–154.8W / 18.8–22.4N) is inside the final viewport:
  // the fitted camera shows the whole box, islands centered and complete.
  const worldPx = 256 * Math.pow(2, hi.getZoom());
  const pxPerDegLon = worldPx / 360;
  const pxSpan = (-154.8 - -160.3) * pxPerDegLon;
  assert.ok(pxSpan <= VIEW_W - 2 * PAD + 1e-6,
    'the hi bbox must fit fully in the viewport after the switch');
  assert.ok(Math.abs(hi.getZoom() - regions.cameraMinZoom(hi.getZoom()) - 0.05) < 1e-9,
    'the zoom floor sits just below the hi fit zoom (CL-WG-07 margin preserved)');
});

test('CL-WG-10: switching tw→jp (wider box) is not zoomed in by the old minZoom', () => {
  const twFit = runLimits('tw', { lng: 120.5, lat: 24, zoom: 5.4 });
  const afterTw = { lng: twFit.getCenter().lng, lat: twFit.getCenter().lat, zoom: twFit.getZoom() };
  const jp = runLimits('jp', afterTw);
  assert.ok(Math.abs(jp.getCenter().lng - (122 + 146) / 2) < 1e-9,
    'jp switch must center on the jp bbox, not the old region edge');
  assert.ok(Math.abs(jp.getCenter().lat - (24 + 46) / 2) < 1e-9);
});

test('CL-WG-10: resize preserves the user camera (preserveCamera)', () => {
  // Start zoomed in ABOVE the hi floor (a zoom below the floor is unreachable
  // while the floor is active in the real map). The fake map is seeded directly
  // — runLimits() always forces a fit, which would move the camera itself.
  const before = { lng: HI_CENTER.lng, lat: HI_CENTER.lat, zoom: 9.5 };
  const map = makeFakeMap(before);
  const state = { mapReady: true, map };
  const fakeWindow = {
    WeatherMapRegions: {
      cameraBounds: b => regions.cameraBounds(b),
      cameraMinZoom: z => regions.cameraMinZoom(z),
      CAMERA_MAX_ZOOM: regions.CAMERA_MAX_ZOOM
    }
  };
  const applyCameraLimits = buildApplyCameraLimits()(state, fakeWindow,
    () => regions.REGION_BBOXES.hi);
  applyCameraLimits({ preserveCamera: true });
  assert.ok(Math.abs(map.getZoom() - 9.5) < 1e-9,
    'resize must keep the zoomed-in camera');
  assert.ok(Math.abs(map.getCenter().lng - before.lng) < 1e-9);
  // zoomed-in resize still re-derives the floor from the fit zoom, not from
  // the current zoom (CL-WG-07 regression guard).
  const fitCalls = map.calls.filter(c => c[0] === 'fitBounds');
  assert.equal(fitCalls.length, 1);
});

test('CL-WG-10: source order — limits cleared before fit, fitZoom read before restore', () => {
  const fn = grab('function applyCameraLimits', 'function renderViewBbox');
  const clearIdx = fn.indexOf('map.setMaxBounds(null)');
  const fitIdx = fn.indexOf('map.fitBounds(bounds');
  const fitZoomIdx = fn.indexOf('const fitZoom=map.getZoom()');
  const jumpIdx = fn.indexOf('map.jumpTo');
  assert.ok(clearIdx !== -1 && fitIdx !== -1, 'stale-limit clearing must exist');
  assert.ok(clearIdx < fitIdx,
    'setMaxBounds(null) must precede the fitBounds call');
  assert.ok(fitZoomIdx < jumpIdx,
    'fitZoom must be read while the new region is fitted, before any camera restore');
  assert.ok(fn.includes('if(preserveCamera)'),
    'camera restore must be conditional (preserveCamera), not unconditional');
  // Region switches keep the default: fit to the new region bbox.
  const activate = grab('async function activateRegion', 'async function switchRegion');
  const setViewIdx = activate.indexOf('setViewBbox(bbox);');
  const limitsIdx = activate.indexOf('applyCameraLimits();');
  assert.ok(setViewIdx !== -1 && limitsIdx !== -1 && setViewIdx < limitsIdx,
    'activateRegion still fits the region bbox then applies limits');
  assert.ok(!activate.includes('applyCameraLimits({preserveCamera'),
    'region activation must fit the new region (no preserveCamera)');
  const resizeBlock = MAP_JS.slice(MAP_JS.indexOf("map.on('resize'"), MAP_JS.indexOf("map.on('click'"));
  assert.ok(resizeBlock.includes('applyCameraLimits({preserveCamera:true})'),
    'viewport resize preserves the user camera');
});

test('CL-WG-10: hi frame sanity for the fixed behavior (bbox + coverage)', () => {
  assert.deepEqual(regions.REGION_BBOXES.hi,
    {leftlon: -160.3, rightlon: -154.8, bottomlat: 18.8, toplat: 22.4});
  assert.deepEqual(regions.cameraBounds(regions.REGION_BBOXES.hi),
    [[-160.3, 18.8], [-154.8, 22.4]]);
  assert.equal(regions.regionContainsPoint('hi', 20.7, -156.3), true,
    'Haleakala-area point inside the hi frame');
});