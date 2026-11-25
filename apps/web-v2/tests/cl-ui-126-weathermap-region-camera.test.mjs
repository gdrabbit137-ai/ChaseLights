// CL-UI-126 (owner report): weather-map?region=tw opened zoomed out over all of
// East Asia. A region entry now lands on that region's own opening camera —
// Taiwan 23.7N/120.96E at zoom 7.5, jp 36.2N/138.2E z6, us 39N/-98W z3.5,
// ak 64N/-152W z3.5, hi 20.7N/-156.3W z6.5 — and ONLY while the URL carries no
// explicit camera (?focus= lat,lon,zoom or ?spot=), so deep links keep owning
// the camera exactly as before.
//
// Run: node --test apps/web-v2/tests/cl-ui-126-weathermap-region-camera.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const MAP_JS = readFileSync(join(WEB, 'assets', 'weather-map.js'), 'utf8');

const grab = (start, end) => {
  const a = MAP_JS.indexOf(start);
  assert.ok(a !== -1, `slice start not found: ${start}`);
  const b = MAP_JS.indexOf(end, a);
  assert.ok(b !== -1, `slice end not found: ${end}`);
  return MAP_JS.slice(a, b);
};

const src = [
  grab('const REGION_CAMERA_DEFAULTS = {', 'function applyRegionDefaultCamera()'),
  grab('function applyRegionDefaultCamera()', 'const state = {')
].join('\n');
// eslint-disable-next-line no-new-func
const make = new Function('window', 'state', `${src}\nreturn {REGION_CAMERA_DEFAULTS,regionCameraDefault,urlHasExplicitCamera,applyRegionDefaultCamera};`);

function harness(search, region, { mapReady = true } = {}) {
  const calls = [];
  const fakeWindow = {
    location: { search },
    WeatherMapDeepLink: {
      focusBboxFromCamera(lat, lon, zoom) {
        const dLat = 180 / Math.pow(2, zoom);
        const dLon = 360 / Math.pow(2, zoom);
        return { leftlon: lon - dLon, rightlon: lon + dLon, bottomlat: lat - dLat, toplat: lat + dLat, zoom };
      }
    },
    WeatherMapRegions: { normalizeBbox: (b) => (b ? { ...b } : null) }
  };
  const state = { region, mapReady, map: { jumpTo(o) { calls.push(o); } }, view: null };
  const api = make(fakeWindow, state);
  return { api, state, calls };
}

const EXPECTED = {
  tw: { center: [23.7, 120.96], zoom: 7.5 },
  jp: { center: [36.2, 138.2], zoom: 6 },
  us: { center: [39, -98], zoom: 3.5 },
  ak: { center: [64, -152], zoom: 3.5 },
  hi: { center: [20.7, -156.3], zoom: 6.5 }
};

test('CL-UI-126 (1): every region carries its documented opening camera', () => {
  const { api } = harness('', 'tw');
  for (const [region, want] of Object.entries(EXPECTED)) {
    const cam = api.regionCameraDefault(region);
    assert.ok(cam, `${region} has a default camera`);
    assert.deepEqual(cam.center, want.center, `${region} centre`);
    assert.equal(cam.zoom, want.zoom, `${region} zoom`);
  }
  assert.equal(api.regionCameraDefault('zz'), null, 'unknown region → no camera default');
});

test('CL-UI-126 (2): region=tw centres Taiwan at zoom 7.5 instead of the whole East-Asia bbox', () => {
  const { api, calls, state } = harness('?region=tw', 'tw');
  assert.equal(api.applyRegionDefaultCamera(), true);
  assert.equal(calls.length, 1, 'the camera is repositioned once');
  assert.deepEqual(calls[0].center, [23.7, 120.96]);
  assert.equal(calls[0].zoom, 7.5);
  assert.ok(state.view, 'state.view mirrors the camera so the canvas fallback agrees');
  assert.ok(state.view.bottomlat < 23.7 && state.view.toplat > 23.7, 'the mirrored view is around Taiwan');
});

test('CL-UI-126 (3): each region applies its own camera', () => {
  for (const [region, want] of Object.entries(EXPECTED)) {
    const { api, calls } = harness(`?region=${region}`, region);
    assert.equal(api.applyRegionDefaultCamera(), true, `${region} applied`);
    assert.deepEqual(calls[0].center, want.center, `${region} centre`);
    assert.equal(calls[0].zoom, want.zoom, `${region} zoom`);
  }
});

test('CL-UI-126 (4): an explicit ?focus= camera is never overridden', () => {
  const { api, calls } = harness('?region=tw&focus=24.1,121.2,9', 'tw');
  assert.equal(api.urlHasExplicitCamera(), true);
  assert.equal(api.applyRegionDefaultCamera(), false);
  assert.equal(calls.length, 0, 'no jumpTo when the URL names a camera');
});

test('CL-UI-126 (5): a ?spot= deep link keeps its own camera', () => {
  const { api, calls } = harness('?region=tw&spot=tw-036', 'tw');
  assert.equal(api.applyRegionDefaultCamera(), false);
  assert.equal(calls.length, 0);
});

test('CL-UI-126 (6): the canvas fallback gets the same camera through state.view', () => {
  const { api, state, calls } = harness('', 'jp', { mapReady: false });
  assert.equal(api.applyRegionDefaultCamera(), true);
  assert.equal(calls.length, 0, 'no map to jump');
  assert.ok(state.view && Math.abs((state.view.bottomlat + state.view.toplat) / 2 - 36.2) < 0.001,
    'the fallback view is centred on Japan');
});

test('CL-UI-126 (7): the hook runs after the region fit in the basemap load handler', () => {
  const load = grab("map.on('load',()=>{", 'map.on(\'styledata\'');
  const fit = load.indexOf('applyCameraLimits({preserveCamera:true})');
  const apply = load.indexOf('applyRegionDefaultCamera()');
  assert.ok(fit > 0 && apply > fit, 'the default camera lands after the bbox fit');
  const fallback = grab('function showWebglFallback()', 'async function initBasemap()');
  assert.ok(fallback.indexOf('applyRegionDefaultCamera()') > 0,
    'the WebGL fallback path mirrors the same camera');
});
