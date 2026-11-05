// CL-WG-24 spot deep-link camera regression. Owner evidence: landing on
// weather-map.html?region=tw&spot=tw-004&subject=cloud_sea left the camera on
// the region fit (whole East Asia) with the spot only marked. Two coupled
// causes, both pinned here:
//   (1) the deferred spot camera (PNG-stub first paint carries no spots; the
//       full bundle applies it later) can land on state.view BEFORE the
//       MapLibre 'load' event fires, and the plain applyCameraLimits() in that
//       handler re-fit the region bbox and clobbered the spot view;
//   (2) fitBounds zoom is viewport-dependent — wide windows landed below the
//       owner spec of zoom 9–11 (CL-WG-19 §7.3), so the spot camera is
//       explicitly clamped into 9–11 after the fit.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const regions = require('../../../assets/weather-map-regions.js');
const fs = require('node:fs');
const path = require('node:path');

const ASSETS = path.join(path.dirname(require.resolve('../../../assets/weather-map-regions.js')));
const MAP_JS = fs.readFileSync(path.join(ASSETS, 'weather-map.js'), 'utf8');

function grab(start, end) {
  const a = MAP_JS.indexOf(start);
  assert.ok(a !== -1, `source slice start not found: ${start}`);
  const b = MAP_JS.indexOf(end, a);
  assert.ok(b !== -1, `source slice end not found: ${end}`);
  return MAP_JS.slice(a, b);
}

// Same faithful MapLibre camera simulation as cl-wg-10 (equirectangular,
// 256px world — every camera move constrained by active limits).
const VIEW_W = 1200, VIEW_H = 800, PAD = 28;

function makeFakeMap(initial) {
  const map = {
    _center: { lng: initial.lng, lat: initial.lat },
    _zoom: initial.zoom,
    _maxBounds: null,
    _minZoom: null,
    _maxZoom: null,
    getCenter() { return { lng: this._center.lng, lat: this._center.lat }; },
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
      const spanLon = e - w, spanLat = n - s;
      let pad = opts?.padding ?? 0;
      const zLon = Math.log2((VIEW_W - 2 * pad) * 360 / (256 * spanLon));
      const zLat = Math.log2((VIEW_H - 2 * pad) * 360 / (256 * spanLat));
      let z = this._minZoom == null ? Math.min(zLon, zLat) : Math.max(this._minZoom, Math.min(zLon, zLat));
      if (opts?.maxZoom != null) z = Math.min(z, opts.maxZoom);
      this._zoom = z;
      this._center = { lng: (w + e) / 2, lat: (s + n) / 2 };
    },
    jumpTo({ center, zoom }) {
      this._center = { lng: center.lng, lat: center.lat };
      this._zoom = this._minZoom == null ? zoom : Math.max(this._minZoom, zoom);
    },
    setMaxBounds(b) { this._maxBounds = b; },
    setMinZoom(z) {
      this._minZoom = z;
      if (z != null && this._zoom < z) this._zoom = z;
    },
    setMaxZoom(z) { this._maxZoom = z; }
  };
  return map;
}

// Evaluate the camera-related source slices against a fake map.
function setup({ initial, region = 'tw', spotApplied = false, spot = null, focus = null }) {
  const map = makeFakeMap(initial);
  const state = {
    mapReady: true, map, region,
    deepLink: { spot, focus, hasAny: Boolean(spot || focus) },
    deepLinkSpotApplied: spotApplied,
    view: null
  };
  return { map, state, api: buildSpotCameraApi(state) };
}

function buildSpotCameraApi(state) {
  const src =
    grab('function normalizeViewBbox', 'function renderViewBbox') +
    grab('function clampSpotCameraZoom', 'function applyDeepLinkEntry');
  const ctx = { WeatherMapRegions: {
    cameraBounds: b => regions.cameraBounds(b),
    cameraMinZoom: z => regions.cameraMinZoom(z),
    CAMERA_MAX_ZOOM: regions.CAMERA_MAX_ZOOM,
    REGION_BBOXES: regions.REGION_BBOXES
  } };
  new Function('window', fs.readFileSync(path.join(ASSETS, 'weather-map-deeplink.js'), 'utf8'))(ctx);
  const fn = new Function('state', 'window', 'regionBbox',
    src + '\nreturn { setViewBbox, applyCameraLimits, clampSpotCameraZoom, applyDeepLinkSpotCamera };');
  return fn(state, ctx, () => regions.REGION_BBOXES[state.region]);
}

const TW_004 = { lat: 25.08923, lon: 121.84752 };

test('CL-WG-24: spot deep-link camera centers on the spot and settles at zoom 9-11', () => {
  const { map, state, api } = setup({
    initial: { lng: 120.5, lat: 24, zoom: 5.4 },
    spotApplied: true, spot: 'tw-004'
  });
  const ok = api.applyDeepLinkSpotCamera(TW_004);
  assert.ok(ok, 'spot camera must apply');
  const c = map.getCenter(), z = map.getZoom();
  assert.ok(Math.abs(c.lng - TW_004.lon) < 0.01, `center lon must be the spot (got ${c.lng})`);
  assert.ok(Math.abs(c.lat - TW_004.lat) < 0.01, `center lat must be the spot (got ${c.lat})`);
  assert.ok(z >= 9 && z <= 11, `zoom must settle in 9-11 (got ${z})`);
  // state.view mirrors the spot view for the canvas fallback.
  assert.ok(state.view && Math.abs((state.view.leftlon + state.view.rightlon) / 2 - TW_004.lon) < 0.01);
});

test('CL-WG-24: low fit zoom is clamped up to 9 on wide viewports', () => {
  const { map, state } = setup({ initial: { lng: 120.5, lat: 24, zoom: 5.4 }, spotApplied: true, spot: 'tw-004' });
  state.deepLinkSpotApplied = true;
  // Simulate a fit that landed below 9 (small spot bbox on a tall viewport).
  map._zoom = 7.9;
  const ok = api_clamp(state);
  assert.ok(ok, 'clamp applies on the live map path');
  assert.ok(Math.abs(map.getZoom() - 9) < 1e-6, `zoom raised to 9 (got ${map.getZoom()})`);
  // Focus wins: explicit focus zoom is never re-clamped by the spot clamp.
  state.deepLink.focus = { lat: 23.8, lon: 121, zoom: 10.5 };
  map._zoom = 10.5;
  assert.ok(!api_clamp(state), 'focus camera is left alone');
  assert.ok(Math.abs(map.getZoom() - 10.5) < 1e-9);
});

function api_clamp(state) {
  const src = grab('function clampSpotCameraZoom', 'function applyDeepLinkSpotCamera');
  const ctx = { WeatherMapRegions: { REGION_BBOXES: regions.REGION_BBOXES } };
  new Function('window', fs.readFileSync(path.join(ASSETS, 'weather-map-deeplink.js'), 'utf8'))(ctx);
  const fn = new Function('state', 'window', src + '\nreturn clampSpotCameraZoom;');
  return fn(state, ctx)(state);
}

test('CL-WG-24: clamp is a no-op before the spot part is applied / map not ready', () => {
  const notApplied = setup({ initial: { lng: 134, lat: 35.75, zoom: 3.8 } });
  notApplied.map._zoom = 3.8;
  assert.ok(!api_clamp(notApplied.state));
  assert.ok(Math.abs(notApplied.map.getZoom() - 3.8) < 1e-9, 'region fit untouched');

  const mapNotReady = setup({ initial: { lng: 121.8, lat: 25.09, zoom: 7.9 }, spotApplied: true, spot: 'tw-004' });
  mapNotReady.state.mapReady = false;
  assert.ok(!api_clamp(mapNotReady.state));
  assert.ok(Math.abs(mapNotReady.map.getZoom() - 7.9) < 1e-9);
});

test('CL-WG-24: spot camera stays inside region limits (no clamp-back to the region fit)', () => {
  const { map, state, api } = setup({
    initial: { lng: 120.5, lat: 24, zoom: 5.4 },
    spotApplied: true, spot: 'tw-004'
  });
  api.applyDeepLinkSpotCamera(TW_004);
  // Camera after the full chain (spot fit + zoom clamp + limits with
  // preserveCamera) must still be the spot view at photography zoom.
  const c = map.getCenter(), z = map.getZoom();
  assert.ok(Math.abs(c.lng - TW_004.lon) < 0.01 && Math.abs(c.lat - TW_004.lat) < 0.01);
  assert.ok(z >= 9 && z <= 11, `spot zoom preserved after applyCameraLimits (got ${z})`);
  // And the region confinement (CL-WG-06/07/10) still holds: maxBounds/minZoom
  // are re-derived from the region fit, not the spot view.
  const b = regions.REGION_BBOXES.tw;
  const view = [map.getBounds().getWest(), map.getBounds().getSouth(),
                map.getBounds().getEast(), map.getBounds().getNorth()];
  assert.ok(view[0] >= b.leftlon - 0.01 && view[2] <= b.rightlon + 0.01 &&
            view[1] >= b.bottomlat - 0.01 && view[3] <= b.toplat + 0.01,
    'spot viewport must sit inside the region bbox');
});

test('CL-WG-24: basemap load handler keeps state.view camera (clobber regression pin)', () => {
  // The deferred spot application can precede the MapLibre load event; the
  // handler must fit state.view AND preserve that camera when deriving limits.
  const a = MAP_JS.indexOf("map.on('load'");
  assert.ok(a !== -1, "map.on('load') handler present");
  const block = MAP_JS.slice(a, MAP_JS.indexOf("map.on('move'", a));
  assert.ok(block.includes('setViewBbox(state.view'), 'load handler fits state.view');
  assert.ok(block.includes('clampSpotCameraZoom()'), 'load handler applies the spot zoom clamp');
  assert.ok(block.includes('applyCameraLimits({preserveCamera:true})'),
    'load handler preserves the just-fitted camera (region fit clobber regression)');
});

test('CL-WG-24: region-only deep link keeps the region fit camera', () => {
  const { map } = setup({ initial: { lng: 134, lat: 35.75, zoom: 3.8 } });
  // Region entry path: setViewBbox(region bbox) + plain applyCameraLimits().
  const b = regions.REGION_BBOXES.jp;
  const state = { mapReady: true, map, region: 'jp', view: null, deepLink: null, deepLinkSpotApplied: false };
  const api = buildSpotCameraApi(state);
  api.setViewBbox(b);
  api.applyCameraLimits();
  const view = [map.getBounds().getWest(), map.getBounds().getSouth(),
                map.getBounds().getEast(), map.getBounds().getNorth()];
  assert.ok(view[0] <= b.leftlon && view[2] >= b.rightlon &&
            view[1] <= b.bottomlat && view[3] >= b.toplat,
    `region-only landing must fit the whole region bbox (view ${JSON.stringify(view)})`);
});

test('CL-WG-24: spotFocusBbox adapts to region scale and clamps to the region bbox', () => {
  const ctx = { WeatherMapDeepLink: null };
  new Function('window', fs.readFileSync(path.join(ASSETS, 'weather-map-deeplink.js'), 'utf8'))(ctx);
  const dl = ctx.WeatherMapDeepLink;
  const tw = dl.spotFocusBbox(TW_004.lat, TW_004.lon, 'tw', regions.REGION_BBOXES);
  assert.ok(Math.abs((tw.leftlon + tw.rightlon) / 2 - TW_004.lon) < 1e-9);
  assert.ok(Math.abs((tw.bottomlat + tw.toplat) / 2 - TW_004.lat) < 1e-9);
  const us = dl.spotFocusBbox(39, -105, 'us', regions.REGION_BBOXES);
  assert.ok((us.rightlon - us.leftlon) > (tw.rightlon - tw.leftlon),
    'a larger region frames a wider spot view (adaptive scale)');
  // Edge spot: view is shifted, never shrunk below the minimum.
  const hi = dl.spotFocusBbox(21.3, -157.86, 'hi', regions.REGION_BBOXES);
  assert.ok(hi.leftlon >= regions.REGION_BBOXES.hi.rightlon * -1 - 1e9);
  assert.ok((hi.toplat - hi.bottomlat) > 0 && (hi.rightlon - hi.leftlon) > 0);
});
