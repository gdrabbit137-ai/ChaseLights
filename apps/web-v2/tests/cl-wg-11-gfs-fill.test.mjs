// CL-WG-14 (owner ruling 2026-11-04): the CL-WG-11 GFS feathered-seam fill
// design is CANCELLED. In regional-model mode the regional product is drawn
// only inside its own coverage and the area outside it stays honestly blank
// (QC note), with no GFS fill pass, no feather seam, and no mixed-source
// label. This file is now a NEGATIVE test: the fill machinery must be gone.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

test('CL-WG-14: no GFS fill machinery remains in weather-map.js (regional-model mode draws no fill)', () => {
  assert.doesNotMatch(JS, /gfsFillPlanForView/,
    'gfsFillPlanForView must be removed');
  assert.doesNotMatch(JS, /drawGfsFillLayer/,
    'drawGfsFillLayer must be removed');
  assert.doesNotMatch(JS, /gfsFillNoteHtml/,
    'gfsFillNoteHtml (mixed-source QC note) must be removed');
  assert.doesNotMatch(JS, /gfsFillActive/,
    'state.gfsFillActive must be removed');
  assert.doesNotMatch(JS, /WeatherMapGfsFill/,
    'no reference to the removed helper may remain');
  assert.doesNotMatch(JS, /rawViewBbox/,
    'rawViewBbox existed only for the fill plan and must be removed');
});

test('CL-WG-14: the fill helper bundle is gone and the page no longer loads it', () => {
  assert.equal(fs.existsSync(path.join(ROOT, 'assets/weather-map-gfs-fill.js')), false,
    'assets/weather-map-gfs-fill.js must be deleted');
  assert.doesNotMatch(HTML, /weather-map-gfs-fill/,
    'weather-map.html must not load the fill helper');
});

test('CL-WG-14: regional-model mode keeps the honest-blank QC note without mixed-source semantics', () => {
  assert.match(JS, /function regionalModelNoteHtml\(\)/,
    'the regional-product honest-blank note must stay');
  assert.match(JS, /此為區域產品，僅在其涵蓋範圍內繪製，範圍外留白/,
    'the note text must be the CL-WG-14 regional-product wording');
  assert.doesNotMatch(JS, /混合來源/,
    'no mixed-source (blended-source) wording may remain');
  // All four updateQc output paths still append the regional-model note alone.
  const appends = JS.match(/regionalModelNoteHtml\(\)/g) || [];
  assert.equal(appends.length, 5, '1 definition + 4 updateQc append paths');
});