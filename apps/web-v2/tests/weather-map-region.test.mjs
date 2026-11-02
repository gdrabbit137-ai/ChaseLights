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
      tw: {leftlon: 117.5, rightlon: 123.5, bottomlat: 20.5, toplat: 26.75},
      jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46},
      us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5},
      ak: {leftlon: -158, rightlon: -132, bottomlat: 55, toplat: 69.5},
      hi: {leftlon: -160.3, rightlon: -154.8, bottomlat: 18.8, toplat: 22.4}
    }
  },
  icon: {
    coverage: {
      tw: {leftlon: 117.5, rightlon: 123.5, bottomlat: 20.5, toplat: 26.75},
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
      tw: {leftlon: 118, rightlon: 124, bottomlat: 21.5, toplat: 27}
    }
  },
  cams: {
    coverage: {
      tw: {leftlon: 117.6, rightlon: 123.6, bottomlat: 20.4, toplat: 26.8},
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
  assert.deepEqual(regions.REGION_BBOXES.tw,
    {leftlon: 118, rightlon: 123, bottomlat: 21.5, toplat: 26.5});
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
  assert.equal(regions.sourceCoversRegion(
    regions.REGION_BBOXES.tw, CATALOG.jma.coverage.tw), false);
  assert.equal(regions.sourceCoversRegion(
    regions.REGION_BBOXES.tw, CATALOG.himawari.coverage.tw), true);
  assert.equal(regions.sourceCoversRegion(
    regions.REGION_BBOXES.jp, CATALOG.jma.coverage.jp), true);
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
  assert.equal(akPlaces.length, 20,
    'exactly the 20 outlying Alaska places route to the ak frame');
  assert.equal(hiPlaces.length, 0,
    'the catalog has no Hawaii places yet — hi stays an honest empty state');
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
  const tw = regions.sourcesForRegion('tw', CATALOG);
  assert.equal(tw.includes('jma'), false,
    'JMA MSM does not fully cover the Taiwan bbox and must not be listed');
  assert.deepEqual(tw, ['gfs', 'icon', 'cwa', 'himawari', 'cams', 'viirs']);

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
