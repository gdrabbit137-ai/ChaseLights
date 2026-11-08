// CL-WG-19 WeatherGrid deep-link tests: URL parameter parsing, subject→layer
// relevance mapping, fail-closed invalid-parameter behavior, spot focus
// camera geometry, and the weather-map.js integration wiring (localStorage
// region memory + replaceState URL sync). Pure logic lives in
// assets/weather-map-deeplink.js; integration assertions are source-greps on
// assets/weather-map.js / weather-map.html per the WeatherGrid verification
// convention (static grep, not shell bundle loading).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const dl = require('../../../assets/weather-map-deeplink.js');
const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const mapSource = readFileSync(join(WEB, 'assets', 'weather-map.js'), 'utf8');
const regionsSource = readFileSync(join(WEB, 'assets', 'weather-map-regions.js'), 'utf8');
const htmlSource = readFileSync(join(WEB, 'weather-map.html'), 'utf8');
const indexSource = readFileSync(join(WEB, 'index.html'), 'utf8');

const REGIONS = ['tw', 'jp', 'us', 'ak', 'hi'];
const BBOXES = {
  tw: {leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40},
  jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46},
  us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5},
  ak: {leftlon: -158, rightlon: -132, bottomlat: 55, toplat: 69.5},
  hi: {leftlon: -160.3, rightlon: -154.8, bottomlat: 18.8, toplat: 22.4}
};
const LAYERS = ['total_cloud_percent', 'low_cloud_percent', 'visibility_km',
  'aerosol_optical_depth_550nm', 'shortwave_flux_w_m2',
  'nighttime_lights_radiance_nw_cm2_sr'];

const params = s => new URLSearchParams(s);

// ---------- 1. region param ----------

test('CL-WG-19 (1): ?region=tw..hi parses to the initial region', () => {
  for (const id of REGIONS) {
    const p = dl.parseDeepLinkParams(params(`?region=${id}`), {validRegions: REGIONS});
    assert.equal(p.region, id);
    assert.ok(p.hasAny);
  }
});

test('CL-WG-19 (2): unknown region fails closed to null (no throw, default path)', () => {
  const p = dl.parseDeepLinkParams(params('?region=eu&spot=tw-036'), {validRegions: REGIONS});
  assert.equal(p.region, null);
  assert.equal(p.spot, 'tw-036');
});

test('CL-WG-19 (3): region resolution order URL > localStorage > tw', () => {
  assert.equal(dl.resolveInitialRegion({urlRegion: 'jp', storedRegion: 'us'}), 'jp');
  assert.equal(dl.resolveInitialRegion({urlRegion: null, storedRegion: 'us'}), 'us');
  assert.equal(dl.resolveInitialRegion({urlRegion: null, storedRegion: null}), 'tw');
  // Corrupted stored value fails closed.
  assert.equal(dl.resolveInitialRegion({urlRegion: null, storedRegion: 'xx'}), 'tw');
  assert.equal(dl.resolveInitialRegion({}), 'tw');
});

// ---------- 2. spot / layer params ----------

test('CL-WG-19 (4): spot id accepts catalog format and rejects malformed ids', () => {
  assert.equal(dl.parseDeepLinkParams(params('?spot=tw-036'), {}).spot, 'tw-036');
  assert.equal(dl.parseDeepLinkParams(params('?spot=TW-036'), {}).spot, 'tw-036');
  assert.equal(dl.parseDeepLinkParams(params('?spot=../../etc'), {}).spot, null);
  assert.equal(dl.parseDeepLinkParams(params('?spot=tw-'), {}).spot, null);
  assert.equal(dl.parseDeepLinkParams(params('?spot=036'), {}).spot, null);
});

test('CL-WG-19 (5): layer param passes a valid key and fails closed on an unknown key', () => {
  const p = dl.parseDeepLinkParams(params('?layer=visibility_km'), {validLayers: LAYERS});
  assert.equal(p.layer, 'visibility_km');
  const bad = dl.parseDeepLinkParams(params('?layer=not_a_layer'), {validLayers: LAYERS});
  assert.equal(bad.layer, null);
  assert.equal(dl.parseDeepLinkParams(params('?layer='), {}).layer, null);
});

// ---------- 3. focus param + spot camera ----------

test('CL-WG-19 (6): focus=lat,lon,zoom parses and clamps zoom to the camera cap', () => {
  const p = dl.parseDeepLinkParams(params('?focus=24.13,121.27,10.5'), {maxZoom: 13});
  assert.deepEqual(p.focus, {lat: 24.13, lon: 121.27, zoom: 10.5});
  const capped = dl.parseDeepLinkParams(params('?focus=24,121,99'), {maxZoom: 13});
  assert.equal(capped.focus.zoom, 13);
  assert.equal(capped.focus.lat, 24);
});

test('CL-WG-19 (7): malformed focus fails closed (no partial camera)', () => {
  for (const raw of ['?focus=24,121', '?focus=a,b,c', '?focus=999,121,10',
    '?focus=24,121,0.2', '?focus=', '?focus=24,,10']) {
    const p = dl.parseDeepLinkParams(params(raw), {});
    assert.equal(p.focus, null, raw);
  }
});

test('CL-WG-19 (8): focusCamera validates and clamps to CAMERA_MAX_ZOOM', () => {
  const cam = dl.focusCamera({lat: 24.13, lon: 121.27, zoom: 10}, 13);
  assert.deepEqual(cam, {center: [121.27, 24.13], zoom: 10});
  assert.equal(dl.focusCamera({lat: 24, lon: 121, zoom: 50}, 13).zoom, 13);
  assert.equal(dl.focusCamera({lat: 24, lon: 121, zoom: 0.5}, 13).zoom, 1);
  assert.equal(dl.focusCamera({lat: NaN, lon: 121, zoom: 10}, 13), null);
  assert.equal(dl.focusCamera(null, 13), null);
});

test('CL-WG-19 (9): spot focus bbox is spot-centered and adaptive to region scale', () => {
  const tw = dl.spotFocusBbox(24.13, 121.27, 'tw', BBOXES);
  const midLon = (tw.leftlon + tw.rightlon) / 2;
  const midLat = (tw.bottomlat + tw.toplat) / 2;
  assert.ok(Math.abs(midLon - 121.27) < 1e-9);
  assert.ok(Math.abs(midLat - 24.13) < 1e-9);
  // us (span 54.5°) gets a wider view than hi (span 5.5°).
  const us = dl.spotFocusBbox(40, -100, 'us', BBOXES);
  const hi = dl.spotFocusBbox(20.7, -157.3, 'hi', BBOXES);
  assert.ok((us.rightlon - us.leftlon) > (hi.rightlon - hi.leftlon));
  // The view stays inside the region bbox and near the 9–11 zoom band
  // (a ~1.6° span on a typical desktop viewport fits ≈ zoom 9–11).
  assert.ok(tw.leftlon >= BBOXES.tw.leftlon && tw.rightlon <= BBOXES.tw.rightlon);
  assert.ok(tw.bottomlat >= BBOXES.tw.bottomlat && tw.toplat <= BBOXES.tw.toplat);
  const lonSpan = tw.rightlon - tw.leftlon;
  assert.ok(lonSpan >= 1.2 && lonSpan <= 2.4, `tw spot span ${lonSpan}`);
});

test('CL-WG-19 (10): spot camera near a region edge clamps inside the bbox', () => {
  // Taiwan east coast: an unshifted box would cross the 145°E edge.
  const b = dl.spotFocusBbox(25.0, 144.6, 'tw', BBOXES);
  assert.ok(b.rightlon <= BBOXES.tw.rightlon + 1e-9);
  assert.ok(b.leftlon >= BBOXES.tw.leftlon - 1e-9);
  assert.ok(Math.abs((b.bottomlat + b.toplat) / 2 - 25.0) < 1e-9);
  assert.equal(dl.spotFocusBbox(24, 121, 'xx', BBOXES), null);
  assert.equal(dl.spotFocusBbox(NaN, 121, 'tw', BBOXES), null);
});

test('CL-WG-19 (11): focusBboxFromCamera approximates the MapLibre viewport span', () => {
  const b = dl.focusBboxFromCamera(24.13, 121.27, 10);
  const span = b.rightlon - b.leftlon;
  assert.ok(span > 0.2 && span < 0.6, `zoom-10 span ${span}`);
  assert.equal(dl.focusBboxFromCamera(24, 121, 0), null);
});

// ---------- 4. subject → layer relevance mapping ----------

test('CL-WG-19 (12): subject genres map to the spec layers', () => {
  assert.deepEqual(dl.subjectLayerCandidates('cloud_sea'), ['low_cloud_percent']);
  assert.deepEqual(dl.subjectLayerCandidates('overcast_soft'), ['low_cloud_percent', 'total_cloud_percent']);
  assert.deepEqual(dl.subjectLayerCandidates('haze'), ['aerosol_optical_depth_550nm']);
  assert.deepEqual(dl.subjectLayerCandidates('city_night'), ['nighttime_lights_radiance_nw_cm2_sr']);
  assert.deepEqual(dl.subjectLayerCandidates('night_sky'), ['nighttime_lights_radiance_nw_cm2_sr']);
  assert.deepEqual(dl.subjectLayerCandidates('sunrise'), ['total_cloud_percent', 'shortwave_flux_w_m2']);
  assert.deepEqual(dl.subjectLayerCandidates('sunset'), ['total_cloud_percent', 'shortwave_flux_w_m2']);
  assert.deepEqual(dl.subjectLayerCandidates('golden_hour'), ['total_cloud_percent', 'shortwave_flux_w_m2']);
  assert.deepEqual(dl.subjectLayerCandidates('mountain_view'), ['visibility_km']);
  assert.deepEqual(dl.subjectLayerCandidates('overlook'), ['visibility_km']);
});

test('CL-WG-19 (13): unmappable genres fail closed to null (default layer)', () => {
  assert.equal(dl.subjectLayerCandidates('seasonal_plant'), null);
  assert.equal(dl.subjectLayerCandidates('blue_hour_city'), null);
  assert.equal(dl.subjectLayerCandidates(''), null);
  assert.equal(dl.subjectLayerCandidates(null), null);
  assert.equal(dl.subjectLayerCandidates(undefined), null);
});

test('CL-WG-19 (14): subtype genre strings map via substring matching', () => {
  assert.deepEqual(dl.subjectLayerCandidates('fog_mist_valley'), ['low_cloud_percent']);
  assert.deepEqual(dl.subjectLayerCandidates('night_sky_milkyway'), ['nighttime_lights_radiance_nw_cm2_sr']);
  assert.deepEqual(dl.subjectLayerCandidates('haze_smog'), ['aerosol_optical_depth_550nm']);
});

test('CL-WG-19 (15): resolveSubjectLayer picks the first region-offered candidate', () => {
  assert.equal(dl.resolveSubjectLayer('haze', ['aerosol_optical_depth_550nm']), 'aerosol_optical_depth_550nm');
  // Candidate layer unavailable in the region → null → default layer.
  assert.equal(dl.resolveSubjectLayer('haze', ['low_cloud_percent']), null);
  assert.equal(dl.resolveSubjectLayer('sunset', ['total_cloud_percent']), 'total_cloud_percent');
  assert.equal(dl.resolveSubjectLayer('sunset', ['shortwave_flux_w_m2']), 'shortwave_flux_w_m2');
  assert.equal(dl.resolveSubjectLayer('unmapped', ['total_cloud_percent']), null);
});

// ---------- 5. integration wiring (source assertions) ----------

test('CL-WG-19 (16): weather-map.js wires the deep-link module and entry state', () => {
  assert.match(mapSource, /readDeepLinkParams\(\)/);
  assert.match(mapSource, /resolveInitialRegion\(/);
  assert.match(mapSource, /applyDeepLinkEntry\(\)/);
  assert.match(mapSource, /WeatherMapDeepLink\.parseDeepLinkParams/);
});

test('CL-WG-19 (17): localStorage region memory + replaceState URL sync', () => {
  assert.match(mapSource, /weathergrid\.region|REGION_MEMORY_KEY/);
  assert.match(mapSource, /persistRegion\(/);
  assert.match(mapSource, /history\.replaceState/);
  // No pushState: URL sync must never pollute browsing history.
  assert.doesNotMatch(mapSource, /history\.pushState/);
  // The URL region param is authoritative on entry.
  assert.match(mapSource, /urlRegion:\s*state\.deepLink\.region/);
  assert.match(mapSource, /storedRegion:\s*readStoredRegion\(\)/);
});

test('CL-WG-19 (18): priority layer param > subject mapping > region default', () => {
  const block = mapSource.slice(mapSource.indexOf('function applyDeepLinkEntry'),
    mapSource.indexOf('async function load('));
  assert.ok(block.includes('dl.layer && layers.includes(dl.layer)'));
  assert.ok(block.includes('resolveSubjectLayer(dl.subject, layers)'));
  assert.ok(block.indexOf('dl.layer && layers.includes') < block.indexOf('resolveSubjectLayer'));
  // Camera priority: focus param > spot-centered camera.
  assert.ok(block.indexOf('applyDeepLinkFocusCamera') < block.indexOf('applyDeepLinkSpotCamera'));
});

test('CL-WG-19 (19): region switch persists memory + syncs URL; user switches drop stale deep-link keys', () => {
  const block = mapSource.slice(mapSource.indexOf('async function switchRegion'),
    mapSource.indexOf('function renderRegionCards'));
  assert.match(block, /persistRegion\(regionId\)/);
  assert.match(block, /syncDeepLinkUrl\(regionId\)/);
  // syncDeepLinkUrl without keepEntryKeys keeps only the region key.
  const sync = mapSource.slice(mapSource.indexOf('function syncDeepLinkUrl'),
    mapSource.indexOf('function applyDeepLinkFocusCamera'));
  assert.match(sync, /keepEntryKeys/);
  assert.match(sync, /searchParams\.delete\(key\)/);
});

test('CL-WG-19 (20): entry application runs only on the initial load path', () => {
  const block = mapSource.slice(mapSource.indexOf('refreshSpotOptions();'),
    mapSource.indexOf("if(state.source === 'live' && baselineLoaded)"));
  assert.match(block, /if\(initial\)\{[\s\S]*applyDeepLinkEntry\(\)/);
});

test('CL-WG-19 (21): weather-map.html loads the deeplink module with a cache-bust stamp', () => {
  assert.match(htmlSource, /assets\/weather-map-deeplink\.js\?v=bclwg\d+/);
  assert.match(htmlSource, /assets\/weather-map\.js\?v=bclwg34/);
  // Per-file stamp consistency: every reference of each stamped asset uses
  // one stamp (same contract as test_weathergrid_ui_polish.py).
  const stamps = a => [...htmlSource.matchAll(new RegExp(`assets/${a}\\?v=(bclwg\\d+)`, 'g'))].map(m => m[1]);
  for (const asset of ['weather-map-deeplink.js', 'weather-map.js']) {
    const found = stamps(asset);
    assert.ok(found.length >= 1, `${asset} stamped`);
    assert.equal(new Set(found).size, 1, `${asset} consistent stamps`);
  }
});

test('CL-WG-19 (22): index.html homepage stamp bumped to clui41', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui51/);
  assert.match(indexSource, /assets\/app\.css\?v=clui53/);
  assert.doesNotMatch(indexSource, /clui29/);
});

test('CL-WG-19 (23): fail-closed parse never throws on garbage input', () => {
  const fake = {get: () => { throw new Error('boom'); }};
  const p = dl.parseDeepLinkParams(fake, {});
  assert.equal(p.hasAny, false);
  assert.equal(dl.parseDeepLinkParams(null, {}).region, null);
  assert.equal(dl.parseDeepLinkParams(undefined, {}).spot, null);
});