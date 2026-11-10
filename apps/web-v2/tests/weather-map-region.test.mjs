// CL-WG-04 WeatherGrid region scoping tests: bbox constants, source coverage
// gate, and region layer masking logic.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const regions = require('../../../assets/weather-map-regions.js');

// Fixture mirroring the REGION_SOURCE_CATALOG coverage in
// assets/weather-map.js (kept literal here so the UI contract is pinned).
const CATALOG = {
  gfs: {
    coverage: {
      tw: {leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40},
      jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46},
      us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5},
      ak: {leftlon: -158, rightlon: -132, bottomlat: 55, toplat: 69.5},
      hi: {leftlon: -160.3, rightlon: -154.8, bottomlat: 18.8, toplat: 22.4}
    }
  },
  icon: {
    coverage: {
      tw: {leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40},
      jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46},
      us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5},
      ak: {leftlon: -158, rightlon: -132, bottomlat: 55, toplat: 69.5},
      hi: {leftlon: -160.3, rightlon: -154.8, bottomlat: 18.8, toplat: 22.4}
    }
  },
  cwa: {
    coverage: {
      tw: {leftlon: 117.5, rightlon: 125.5, bottomlat: 20, toplat: 27}
    }
  },
  jma: {
    coverage: {
      tw: {leftlon: 120.0625, rightlon: 124.5, bottomlat: 22.45, toplat: 27},
      jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46}
    }
  },
  himawari: {
    coverage: {
      tw: {leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40}
    }
  },
  cams: {
    coverage: {
      tw: {leftlon: 104.8, rightlon: 145.2, bottomlat: 4.8, toplat: 40},
      jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46},
      us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5},
      ak: {leftlon: -158, rightlon: -132, bottomlat: 55, toplat: 69.5},
      hi: {leftlon: -160.3, rightlon: -154.8, bottomlat: 18.8, toplat: 22.4}
    }
  },
  viirs: {
    coverage: {
      tw: {leftlon: 117.5, rightlon: 123.5, bottomlat: 20.5, toplat: 26.75},
      jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46},
      us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5}
    }
  }
};

test('region bbox constants match the owner spec', () => {
  // CL-WG-13: tw display range = CWA official satellite cloud-map extent.
  assert.deepEqual(regions.REGION_BBOXES.tw,
    {leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40});
  assert.deepEqual(regions.REGION_BBOXES.jp,
    {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46});
  assert.deepEqual(regions.REGION_BBOXES.us,
    {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5});
  assert.deepEqual(regions.REGION_BBOXES.ak,
    {leftlon: -158, rightlon: -132, bottomlat: 55, toplat: 69.5},
    'Alaska independent frame (owner ruling 2026-11-03)');
  assert.deepEqual(regions.REGION_BBOXES.hi,
    {leftlon: -160.3, rightlon: -154.8, bottomlat: 18.8, toplat: 22.4},
    'Hawaii independent frame (owner spec)');
  assert.deepEqual(regions.REGION_ORDER, ['tw', 'jp', 'us', 'ak', 'hi']);
});

test('region bboxes contain every catalogued place of the region', () => {
  for (const id of regions.REGION_ORDER) {
    assert.equal(regions.regionContainsAllPlaces(id), true,
      `${id} bbox must contain all its catalogued places`);
  }
});

test('source coverage gate withholds partial sources (JMA vs Taiwan)', () => {
  // The strict gate itself still fails for a partial source...
  assert.equal(regions.sourceCoversRegion(
    regions.REGION_BBOXES.tw, CATALOG.jma.coverage.tw), false);
  // CL-WG-17: himawari was widened to the full tw frame, so it now passes the
  // strict gate (it used to be the partial-source example here).
  assert.equal(regions.sourceCoversRegion(
    regions.REGION_BBOXES.tw, CATALOG.himawari.coverage.tw), true);
  assert.equal(regions.sourceCoversRegion(
    regions.REGION_BBOXES.jp, CATALOG.jma.coverage.jp), true);
});

test('regional model options: partial sources with a published coverage entry stay listed for tw (CL-WG-13)', () => {
  // CL-WG-13: on the widened tw display range the regional high-resolution
  // models (cwa/jma/himawari) and the limited-extent observation layer
  // (viirs) stay offered as regional model options — they render honestly
  // inside their own coverage and stay blank outside.
  assert.deepEqual(regions.REGIONAL_MODEL_SOURCES,
    new Set(['cwa', 'jma', 'himawari', 'viirs']));
  const tw = regions.sourcesForRegion('tw', CATALOG);
  assert.deepEqual(tw, ['gfs', 'icon', 'cwa', 'jma', 'himawari', 'cams', 'viirs']);
  // A regional source without a published coverage entry for the region is
  // still not offered (cwa/jma/himawari have no jp/us coverage entries).
  const jp = regions.sourcesForRegion('jp', CATALOG);
  assert.deepEqual(jp, ['gfs', 'icon', 'jma', 'cams', 'viirs']);
  const us = regions.sourcesForRegion('us', CATALOG);
  assert.deepEqual(us, ['gfs', 'icon', 'cams', 'viirs']);
});

test('ak/hi route outlying US places out of the US Mainland frame', () => {
  const catalog = require('../../../apps/web-v2/catalog.v2.json');
  const akPlaces = [];
  const hiPlaces = [];
  const seen = new Set();
  for (const opp of catalog.opportunities || []) {
    for (const target of opp.navigation_targets || []) {
      if (target.lat == null || target.lon == null) continue;
      if (seen.has(opp.place_id)) continue;
      seen.add(opp.place_id);
      const routed = regions.regionForPoint(target.lat, target.lon);
      if (routed === 'ak') akPlaces.push(opp.place_id);
      if (routed === 'hi') hiPlaces.push(opp.place_id);
    }
  }
  assert.equal(akPlaces.length, 27,
    'exactly the 27 outlying Alaska places route to the ak frame (CL-DATA-43 +5, CL-DATA-53 +2: Keystone Canyon/Harding Icefield)');
  assert.equal(hiPlaces.length, 10,
    'exactly the 10 Hawaii places route to the hi frame (CL-DATA-43 7 + CL-DATA-63v2 3: us-161..163)');
  assert.ok(akPlaces.includes('us-041') && akPlaces.includes('us-069'),
    'Alaska places are catalog us-* ids routed to ak');

  // Anchorage / Hawaii points must never be claimed by the us box.
  assert.notEqual(regions.regionForPoint(61.2042, -150.01871), 'us');
  assert.notEqual(regions.regionForPoint(21.3, -157.8), 'us');
  assert.equal(regions.regionForPoint(45.0, -100.0), 'us',
    'a CONUS point still routes to the us frame');
  assert.equal(regions.regionForPoint(0.0, 0.0), null);

  // Every catalogued place routes into exactly one of the registered frames.
  for (const id of regions.REGION_ORDER) {
    assert.equal(regions.regionContainsAllPlaces(id), true,
      `${id} bbox must contain all its catalogued places`);
  }
});

test('ak/hi source lists follow the coverage rule and stay fail-closed on VIIRS', () => {
  const ak = regions.sourcesForRegion('ak', CATALOG);
  assert.deepEqual(ak, ['gfs', 'icon', 'cams'],
    'global free sources cover Alaska; regional models do not');
  const hi = regions.sourcesForRegion('hi', CATALOG);
  assert.deepEqual(hi, ['gfs', 'icon', 'cams'],
    'global free sources cover Hawaii; regional models do not');
  // NASA Black Marble is fail-closed: not offered for new regions.
  for (const id of ['ak', 'hi']) {
    assert.equal(regions.sourcesForRegion(id, CATALOG).includes('viirs'), false);
  }
});

test('per-region source lists follow the coverage rule', () => {
  // CL-WG-13: on the widened tw display range, regional high-resolution
  // models stay listed as model options (honest blank outside coverage);
  // JMA MSM is now one of them (its native transport boundary is disclosed
  // in the data-info panel).
  const tw = regions.sourcesForRegion('tw', CATALOG);
  assert.deepEqual(tw, ['gfs', 'icon', 'cwa', 'jma', 'himawari', 'cams', 'viirs']);

  const jp = regions.sourcesForRegion('jp', CATALOG);
  assert.deepEqual(jp, ['gfs', 'icon', 'jma', 'cams', 'viirs']);

  const us = regions.sourcesForRegion('us', CATALOG);
  assert.deepEqual(us, ['gfs', 'icon', 'cams', 'viirs'],
    'regional models (CWA/JMA/Himawari) are not offered for the US mainland');
});

test('region layer mask never offers layers no enabled source carries', () => {
  const iconOnly = [{id: 'icon', layers: ['low_cloud_percent', 'mid_cloud_percent', 'high_cloud_percent']}];
  const fieldsBySource = {icon: {low_cloud_percent: {}, mid_cloud_percent: {}, high_cloud_percent: {}}};
  assert.deepEqual(
    regions.maskLayersForRegion(
      ['low_cloud_percent', 'total_cloud_percent', 'visibility_km', 'wind_speed_10m_m_s'],
      iconOnly, fieldsBySource),
    ['low_cloud_percent']);

  // A source that declares a layer its bundle does not carry is masked out.
  const phantom = [{id: 'icon', layers: ['low_cloud_percent', 'total_cloud_percent']}];
  assert.deepEqual(
    regions.maskLayersForRegion(['low_cloud_percent', 'total_cloud_percent'], phantom, fieldsBySource),
    ['low_cloud_percent']);
});

test('region labels are trilingual', () => {
  for (const id of regions.REGION_ORDER) {
    for (const lang of ['zh-TW', 'en', 'ja']) {
      assert.ok(regions.REGION_LABELS[id][lang], `${id} missing ${lang} label`);
    }
  }
});

// CL-WG-06 視野收斂: the map camera is confined to the active region bbox.
test('camera bounds sit exactly on the region bbox edges', () => {
  assert.deepEqual(regions.cameraBounds(regions.REGION_BBOXES.tw),
    [[105, 5], [145, 40]]);
  assert.deepEqual(regions.cameraBounds(regions.REGION_BBOXES.us),
    [[-125, 25], [-70.5, 49.5]]);
  assert.equal(regions.cameraBounds(null), null);
  assert.equal(regions.cameraBounds({leftlon: 5, rightlon: 5, bottomlat: 0, toplat: 1}), null,
    'degenerate bbox is rejected');
});

test('camera minZoom is a fixed floor just below the bbox-fit zoom (CL-WG-07)', () => {
  const floor = regions.cameraMinZoom(6.4);
  assert.ok(Math.abs(floor - 6.35) < 1e-9, 'fitZoom minus a small margin');
  assert.equal(regions.cameraMinZoom(0.03), 0, 'never negative');
  assert.equal(regions.cameraMinZoom(Number.NaN), null);
  assert.equal(regions.cameraMinZoom(undefined), null);
});

test('camera minZoom ignores the current zoom so zooming in never raises the floor (CL-WG-07)', () => {
  const fit = 6.4;
  const floor = regions.cameraMinZoom(fit);
  for (const currentZoom of [fit, 8, 9, 11, 13]) {
    assert.equal(regions.cameraMinZoom(fit, currentZoom), floor,
      `zoomed in to ${currentZoom}, minus must still return to the fit view`);
  }
  // 模擬 owner 情境：放大後連按 −，每一步都允許繼續縮小，最終回到 fit。
  let zoom = 11;
  while (zoom > floor + 1e-9) {
    zoom = Math.max(floor, zoom - 1);
  }
  assert.ok(Math.abs(zoom - floor) < 1e-9, 'repeated minus presses reach the full-region fit zoom');
});

test('camera max zoom keeps spot-level detail', () => {
  assert.equal(regions.CAMERA_MAX_ZOOM, 13);
});

test('weather-map.js confines the camera per region (CL-WG-06)', () => {
  const js = require('node:fs').readFileSync(
    require('node:path').join(require('node:url').fileURLToPath(new URL('../../../assets/weather-map.js', import.meta.url))), 'utf8');
  assert.ok(js.includes('function applyCameraLimits({preserveCamera=false}={})'),
    'applyCameraLimits must be defined');
  assert.ok(js.includes('map.setMaxBounds(['), 'maxBounds must clamp panning');
  assert.ok(js.includes('map.setMinZoom(minZoom)'), 'minZoom must clamp zooming out');
  assert.ok(js.includes('window.WeatherMapRegions.CAMERA_MAX_ZOOM'),
    'maxZoom must come from the regions registry');
  // Region activation fits the region bbox (not the wider source bundle bbox)
  // and then applies the camera limits.
  assert.ok(js.includes('setViewBbox(bbox);\n    applyCameraLimits();'),
    'activateRegion must fit the region bbox then apply camera limits');
  assert.ok(!js.includes('setViewBbox(state.data.bbox || bbox)'),
    'the wider source bundle bbox must no longer drive the initial view');
  // The camera limits are re-applied on basemap load and viewport resize.
  const loadBlock = js.slice(js.indexOf("map.on('load'"), js.indexOf("map.on('move'"));
  assert.ok(loadBlock.includes('applyCameraLimits()'),
    'basemap load must apply camera limits');
  const resizeBlock = js.slice(js.indexOf("map.on('resize'"), js.indexOf("map.on('click'"));
  assert.ok(resizeBlock.includes('applyCameraLimits({preserveCamera:true})'),
    'viewport resize must re-apply camera limits (CL-WG-10: preserveCamera so the user view survives resize)');
  // Reset returns to the region bbox.
  assert.ok(js.includes('setViewBbox(regionBbox(),{animate:true,maxZoom:8})'),
    'reset-view must target the region bbox');
});

test('the initial basemap camera fits the region bbox at first load (CL-WG-09)', () => {
  const js = require('node:fs').readFileSync(
    require('node:path').join(require('node:url').fileURLToPath(new URL('../../../assets/weather-map.js', import.meta.url))), 'utf8');
  // The Map constructor's fixed zoom is only a transient state: right after
  // state.map=map, the initial camera must be fitted to the region bbox
  // (zoomed fully out, whole data range in frame) and then camera-limited.
  const start = js.indexOf('state.map=map;');
  assert.ok(start !== -1, 'initBasemap must assign state.map');
  const block = js.slice(start, js.indexOf("map.on('load'", start));
  const setView = block.indexOf('setViewBbox(state.view || state.data.bbox);');
  const applyLimits = block.indexOf('applyCameraLimits();');
  assert.ok(setView !== -1,
    'the initial camera must fit the region bbox immediately after map creation (CL-WG-09)');
  assert.ok(applyLimits !== -1,
    'the initial camera fit must be followed by applyCameraLimits (CL-WG-09)');
  assert.ok(setView < applyLimits,
    'camera limits must be applied after the initial fit (CL-WG-09)');
  // No residual hash/URL camera state: this page never enables MapLibre's
  // hash plugin and never reads location.hash for camera state.
  assert.ok(!js.includes('.Hash'), 'MapLibre hash plugin must stay disabled (CL-WG-09)');
  assert.ok(!js.includes('location.hash'), 'no location.hash camera state (CL-WG-09)');
});

test('reset-view re-applies the camera limits after returning to the region bbox', () => {
  const js = require('node:fs').readFileSync(
    require('node:path').join(require('node:url').fileURLToPath(new URL('../../../assets/weather-map.js', import.meta.url))), 'utf8');
  const start = js.indexOf("$('reset-view').addEventListener('click'");
  assert.ok(start !== -1, 'reset-view handler must exist');
  const block = js.slice(start, js.indexOf('\n    });', start));
  const setView = block.indexOf('setViewBbox(regionBbox(),{animate:true,maxZoom:8})');
  const applyLimits = block.indexOf('applyCameraLimits()');
  assert.ok(setView !== -1, 'reset-view must fit the region bbox');
  assert.ok(applyLimits !== -1,
    'reset-view must re-apply applyCameraLimits so the camera is re-confined to the region bbox');
  assert.ok(setView < applyLimits,
    'camera limits must be applied after the reset view is set');
});

test('the single WeatherGrid page has no V2 experiment entry left', () => {
  const fs = require('node:fs');
  const root = require('node:path').resolve(
    require('node:url').fileURLToPath(new URL('../../..', import.meta.url)));
  assert.ok(fs.existsSync(require('node:path').join(root, 'weather-map.html')), 'weather-map.html stays');
  assert.ok(!fs.existsSync(require('node:path').join(root, 'weather-map-v2.html')),
    'weather-map-v2.html was removed (CL-WG-06)');
  assert.ok(!fs.existsSync(require('node:path').join(root, 'assets', 'weather-map-v2.js')),
    'the V2 page controller was removed with its page');
  const index = fs.readFileSync(require('node:path').join(root, 'index.html'), 'utf8');
  assert.ok(!index.includes('weather-map-v2'), 'index.html must not link the V2 page');
});

// CL-WG-08: the layer dropdown shows clean single layer names; photography-use
// annotations live in the「目前圖層」detail panel (PHOTOGRAPHY_LAYER_NOTES).
test('layer dropdown labels are clean and use notes live in the detail panel (CL-WG-08)', () => {
  const js = require('node:fs').readFileSync(
    require('node:path').join(require('node:url').fileURLToPath(new URL('../../../assets/weather-map.js', import.meta.url))), 'utf8');
  const labelFnStart = js.indexOf('function photographyLayerLabel(key)');
  const labelFnEnd = js.indexOf('return labels[key]', labelFnStart);
  const labelBlock = js.slice(labelFnStart, labelFnEnd);
  assert.ok(labelBlock.includes("'🌫️ 山霧'"), 'low-cloud dropdown label must be 山霧');
  assert.ok(labelBlock.includes("'🌤️ 高雲'"), 'high-cloud dropdown label must be 高雲');
  assert.ok(labelBlock.includes("'☀️ 短波'"), 'shortwave dropdown label must be 短波');
  assert.ok(!labelBlock.includes('霞光'), 'dropdown labels must not carry use annotations');
  assert.ok(js.includes('const PHOTOGRAPHY_LAYER_NOTES={'), 'panel notes table must exist');
  assert.ok(js.includes('PHOTOGRAPHY_LAYER_NOTES[state.layer]'),
    'the detail panel must render the layer use note');
  assert.ok(js.includes('霞光拍攝的參考'), 'the high-cloud use note (霞光參考) must live in the panel');
});
