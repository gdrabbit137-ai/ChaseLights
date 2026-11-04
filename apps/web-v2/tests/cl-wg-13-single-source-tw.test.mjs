// CL-WG-13: tw single-source full-frame rendering (方案 A). GFS is the main
// source over the whole widened display range. CL-WG-14 (owner ruling
// 2026-11-04) cancels the CL-WG-11 feathered-seam fill entirely: there is no
// fill plan, no seam, and no mixed-source label in any mode — a regional
// product renders only inside its own coverage, honestly blank outside it.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const regions = require('../../../assets/weather-map-regions.js');

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const REGIONS_JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map-regions.js'), 'utf8');

test('tw display range is pinned to the CWA official cloud-map extent', () => {
  assert.deepEqual(regions.REGION_BBOXES.tw,
    {leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40});
  assert.match(REGIONS_JS, /105–145°E \/ 5–40°N/,
    'the region registry header documents the CWA cloud-map extent');
});

test('CL-WG-14: no GFS fill machinery exists in any mode (fill design cancelled)', () => {
  assert.doesNotMatch(JS, /gfsFillPlanForView/,
    'gfsFillPlanForView must be removed');
  assert.doesNotMatch(JS, /drawGfsFillLayer/,
    'drawGfsFillLayer must be removed');
  assert.doesNotMatch(JS, /WeatherMapGfsFill/,
    'no reference to the removed fill helper may remain');
});

test('QC panel labels: regional-product honest-blank note on every updateQc path, no mixed-source note', () => {
  assert.match(JS, /function regionalModelNoteHtml\(\)/,
    'regional-product honest-blank QC note must exist');
  assert.match(JS, /mainData===state\.data \|\| !mainData\?\.bbox\) return ''/,
    'the regional-product note must never show in GFS single-source mode');
  assert.match(JS, /此為區域產品，僅在其涵蓋範圍內繪製，範圍外留白/,
    'CL-WG-14 regional-product wording');
  assert.doesNotMatch(JS, /gfsFillNoteHtml|混合來源/,
    'the mixed-source fill note must be gone');
  const qcHostAppends = JS.match(/regionalModelNoteHtml\(\)/g) || [];
  assert.equal(qcHostAppends.length, 6,
    'definition + all five updateQc output paths append the regional-product note (CL-WG-18 added the data-not-rendered honesty path)');
});

test('single-source mode keeps the region clipped render and camera confined to the widened bbox', () => {
  // renderViewBbox clips to the (now huge) region bbox — unchanged logic,
  // re-asserted so the widened bbox is the only thing that moved.
  assert.match(JS, /CL-WG-04 render clip: never draw cells outside the active region bbox/);
  // applyCameraLimits still derives maxBounds from the FITTED viewport.
  assert.match(JS, /fitted\.getEast\(\)-fitted\.getWest\(\)\)\*0\.25/);
});
