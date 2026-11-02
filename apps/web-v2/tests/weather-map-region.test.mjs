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
      us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5}
    }
  },
  icon: {
    coverage: {
      tw: {leftlon: 117.5, rightlon: 123.5, bottomlat: 20.5, toplat: 26.75},
      jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46},
      us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5}
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
      us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5}
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
  assert.deepEqual(regions.REGION_ORDER, ['tw', 'jp', 'us']);
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
