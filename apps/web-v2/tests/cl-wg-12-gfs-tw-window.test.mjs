// CL-WG-12: the tw GFS fetch window must cover the camera maxBounds pan
// range (region bbox expanded 25% of its span per side) so the CL-WG-11
// GFS fill layer never paints a bare basemap outside the region bbox.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const regions = require('../../../assets/weather-map-regions.js');

const ROOT = path.resolve(import.meta.dirname, '../../..');

// New pinned window (gfs_raw_poc.py TAIWAN_BBOX, mirrored in the
// REGION_SOURCE_CATALOG gfs coverage for tw in assets/weather-map.js).
const NEW_WINDOW = {leftlon: 116, rightlon: 125, bottomlat: 20, toplat: 28};

function sourceCovers(regionBbox, sourceBbox) {
  return regions.sourceCoversRegion(regionBbox, sourceBbox);
}

test('tw GFS window is pinned to the CL-WG-12 extent', () => {
  const src = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
  const gfsBlock = src.slice(src.indexOf('const REGION_SOURCE_CATALOG'), src.indexOf('const REGION_SOURCE_CATALOG') + 4000);
  assert.match(gfsBlock,
    /tw:\s*\{leftlon:116,\s*rightlon:125,\s*bottomlat:20,\s*toplat:28\}/,
    'REGION_SOURCE_CATALOG gfs coverage tw must pin the CL-WG-12 window');
});

test('tw GFS window covers the camera maxBounds pan range', () => {
  const region = regions.REGION_BBOXES.tw;
  const lonPad = (region.rightlon - region.leftlon) * 0.25;
  const latPad = (region.toplat - region.bottomlat) * 0.25;
  const maxBounds = {
    leftlon: region.leftlon - lonPad,
    rightlon: region.rightlon + lonPad,
    bottomlat: region.bottomlat - latPad,
    toplat: region.toplat + latPad,
  };
  assert.ok(sourceCovers(maxBounds, NEW_WINDOW),
    `GFS window ${JSON.stringify(NEW_WINDOW)} must cover maxBounds ${JSON.stringify(maxBounds)}`);
});

test('published gfs_tw bundle bbox covers the camera maxBounds pan range', () => {
  const bundlePath = path.join(ROOT, 'weathergrid/gfs_tw_weather_browser.json');
  if (!fs.existsSync(bundlePath)) {
    assert.fail('weathergrid/gfs_tw_weather_browser.json missing — regenerate the bundle with the widened window before merging');
  }
  const bundle = JSON.parse(fs.readFileSync(bundlePath, 'utf8'));
  const region = regions.REGION_BBOXES.tw;
  const lonPad = (region.rightlon - region.leftlon) * 0.25;
  const latPad = (region.toplat - region.bottomlat) * 0.25;
  const maxBounds = {
    leftlon: region.leftlon - lonPad,
    rightlon: region.rightlon + lonPad,
    bottomlat: region.bottomlat - latPad,
    toplat: region.toplat + latPad,
  };
  assert.ok(sourceCovers(maxBounds, bundle.bbox),
    `published bundle bbox ${JSON.stringify(bundle.bbox)} must cover maxBounds ${JSON.stringify(maxBounds)}`);
});
