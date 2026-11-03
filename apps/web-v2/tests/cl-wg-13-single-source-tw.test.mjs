// CL-WG-13: tw single-source full-frame rendering (方案 A). GFS is the main
// source over the whole widened display range, so gfsFillPlanForView must
// return null (no fill, no feather, no mixed-source label) whenever GFS is
// the main source; the fill only returns in regional-model mode, anchored on
// that model's own bundle bbox, and the QC panel labels the honest blank
// outside a regional model's coverage.
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

function gfsFillPlanForViewSource() {
  const start = JS.indexOf('function gfsFillPlanForView');
  const end = JS.indexOf('function', start + 10);
  return JS.slice(start, end);
}

test('tw display range is pinned to the CWA official cloud-map extent', () => {
  assert.deepEqual(regions.REGION_BBOXES.tw,
    {leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40});
  assert.match(REGIONS_JS, /105–145°E \/ 5–40°N/,
    'the region registry header documents the CWA cloud-map extent');
});

test('gfsFillPlanForView is disabled when GFS is the main source (single source, no seam)', () => {
  const src = gfsFillPlanForViewSource();
  assert.match(src, /const mainData=modelDataset\(\)/,
    'the plan must resolve the active main source dataset');
  assert.match(src, /if\(mainData===state\.data\) return null/,
    'GFS main source → no fill plan (one source over the whole frame has no seam)');
  assert.match(src, /mainBbox:mainData\?\.bbox\|\|null/,
    'regional-model mode anchors the fill on the model bundle bbox');
});

test('QC panel labels: mixed-source note only via active fill state; regional-model blank note added', () => {
  assert.match(JS, /function regionalModelNoteHtml\(\)/,
    'regional-model honest-blank QC note must exist');
  assert.match(JS, /mainData===state\.data \|\| !mainData\?\.bbox\) return ''/,
    'the regional-model note must never show in GFS single-source mode');
  assert.match(JS, /範圍外誠實留白（不代表晴朗）/);
  // Every QC output path appends both notes (they are mutually exclusive).
  const qcHostAppends = JS.match(/regionalModelNoteHtml\(\)\+gfsFillNoteHtml\(\)/g) || [];
  assert.equal(qcHostAppends.length, 4,
    'all four updateQc output paths append the regional-model note before the fill note');
});

test('single-source mode keeps the region clipped render and camera confined to the widened bbox', () => {
  // renderViewBbox clips to the (now huge) region bbox — unchanged logic,
  // re-asserted so the widened bbox is the only thing that moved.
  assert.match(JS, /CL-WG-04 render clip: never draw cells outside the active region bbox/);
  // applyCameraLimits still derives maxBounds from the FITTED viewport.
  assert.match(JS, /fitted\.getEast\(\)-fitted\.getWest\(\)\)\*0\.25/);
});
