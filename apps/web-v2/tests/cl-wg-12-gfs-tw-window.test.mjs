// CL-WG-13: the tw display range is the CWA official satellite cloud-map
// extent (105–145°E / 5–40°N). The GFS bundle IS the single full-frame main
// source over that range, so the fetch window equals the region bbox and the
// CL-WG-11 fill is naturally inactive in GFS main-source mode.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const regions = require('../../../assets/weather-map-regions.js');

const ROOT = path.resolve(import.meta.dirname, '../../..');

// Pinned window (gfs_raw_poc.py TAIWAN_BBOX, mirrored in the
// REGION_SOURCE_CATALOG gfs coverage for tw in assets/weather-map.js).
const NEW_WINDOW = {leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40};

test('tw GFS window is pinned to the CL-WG-13 extent', () => {
  const src = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
  const gfsBlock = src.slice(src.indexOf('const REGION_SOURCE_CATALOG'), src.indexOf('const REGION_SOURCE_CATALOG') + 4000);
  assert.match(gfsBlock,
    /tw:\s*\{leftlon:105,\s*rightlon:145,\s*bottomlat:5,\s*toplat:40\}/,
    'REGION_SOURCE_CATALOG gfs coverage tw must pin the CL-WG-13 window');
});

test('tw GFS window equals the region display bbox (single-source full frame)', () => {
  assert.deepEqual(regions.REGION_BBOXES.tw, NEW_WINDOW,
    'the fetch window must equal the region bbox — one source over the whole frame means no seam');
});

test('gfs/icon/cams tw coverage follows the display range (global free sources)', () => {
  const src = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
  const catalogBlock = src.slice(src.indexOf('const REGION_SOURCE_CATALOG'), src.indexOf('const REGION_SOURCE_PRIORITY'));
  assert.match(catalogBlock,
    /icon:[\s\S]*?tw:\s*\{leftlon:105,\s*rightlon:145,\s*bottomlat:5,\s*toplat:40\}/,
    'ICON tw coverage must follow the CL-WG-13 display range');
  assert.match(catalogBlock,
    /cams:[\s\S]*?tw:\s*\{leftlon:104\.8,\s*rightlon:145\.2,\s*bottomlat:4\.8,\s*toplat:40\}/,
    'CAMS tw coverage must follow the CL-WG-13 display range (0.4° request lattice margin)');
});

test('published gfs_tw bundle bbox covers the full display range', () => {
  const bundlePath = path.join(ROOT, 'weathergrid/gfs_tw_weather_browser.json');
  if (!fs.existsSync(bundlePath)) {
    assert.fail('weathergrid/gfs_tw_weather_browser.json missing — regenerate the bundle with the widened window before merging');
  }
  const bundle = JSON.parse(fs.readFileSync(bundlePath, 'utf8'));
  assert.ok(regions.sourceCoversRegion(regions.REGION_BBOXES.tw, bundle.bbox),
    `published bundle bbox ${JSON.stringify(bundle.bbox)} must cover the display range ${JSON.stringify(regions.REGION_BBOXES.tw)}`);
});
