// CL-WG-18: Round 1 inspection fixes.
// 1) Timeline opens anchored to the frame nearest "now" (spot local wall
//    clock), not the model base time days in the past; manual rewind wins.
// 2) QC panel is honest when the data layer did not actually render
//    (basemap timeout + Canvas fallback with nothing drawn): no "✓ 資料正常".
// 3) Guard: layer/region label dictionaries stay 正體中文 (no simplified han).
// 4) 390px: basemap-status badge and region-card-sub wrap instead of
//    mid-word ellipsis.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const CSS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.css'), 'utf8');
const HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');
const REGIONS = fs.readFileSync(path.join(ROOT, 'assets/weather-map-regions.js'), 'utf8');

function grab(src, startMarker, endMarker) {
  const a = src.indexOf(startMarker);
  assert.ok(a >= 0, `start marker not found: ${startMarker}`);
  const b = src.indexOf(endMarker, a);
  assert.ok(b > a, `end marker not found: ${endMarker}`);
  return src.slice(a, b);
}

test('timeline defaults to the frame nearest now, and manual navigation wins', () => {
  // refreshModelControls carries the now-anchor.
  const refreshBody = grab(JS, 'function refreshModelControls(){', 'function switchModel(');
  assert.match(refreshBody, /if\(!state\.frameAnchorTouched && timeline\?\.frames\?\.length>1\)\{/,
    'anchor applies only while the user has not touched the timeline');
  assert.match(refreshBody, /nearestFrameIndex\(timeline,new Date\(\)\.toISOString\(\)\)/,
    'anchor targets absolute UTC now (= the spot local current hour)');
  // Manual navigation takes ownership.
  const setFrameBody = grab(JS, 'function setFrameIndex(', 'function toggleTimelinePlayback(');
  assert.match(setFrameBody, /state\.frameAnchorTouched=true;/,
    'slider drag / prev / next set frameAnchorTouched');
  const playbackBody = grab(JS, 'function toggleTimelinePlayback(){', 'function initDataInfoDialog(');
  assert.match(playbackBody, /state\.frameAnchorTouched=true;/,
    'playback is manual navigation too');
  // Region activation resets the anchor for the fresh bundle.
  const activateBody = grab(JS, 'async function activateRegion(', 'async function switchRegion(');
  assert.match(activateBody, /state\.frameAnchorTouched = false;/,
    'switching region re-anchors the timeline to now');
});

test('nearestFrameIndex picks the frame closest to now, not the base frame', () => {
  const src = grab(JS, 'function nearestFrameIndex(', 'function regionFieldsBySource(');
  const fn = new Function(`${src}\n  return nearestFrameIndex;`)();
  const now = Date.now();
  const frames = [
    { valid_time_utc: new Date(now - 36 * 3600e3).toISOString() },
    { valid_time_utc: new Date(now - 3 * 3600e3).toISOString() },
    { valid_time_utc: new Date(now + 45 * 60e3).toISOString() },
    { valid_time_utc: new Date(now + 30 * 3600e3).toISOString() },
  ];
  assert.equal(fn({ frames }, new Date().toISOString()), 2,
    'the frame nearest the current hour is selected');
  assert.equal(fn({ frames }, new Date(now - 36 * 3600e3).toISOString()), 0,
    'explicit old timestamps still resolve to the nearest frame (manual rewind preserved)');
  assert.equal(fn({ frames: [] }, new Date().toISOString()), 0);
  assert.equal(fn(null, null), 0);
});

test('QC panel never claims 資料正常 when the data layer did not render', () => {
  // draw() records whether the field actually painted.
  const drawBody = grab(JS, 'function draw(){', 'function windVectorStep(');
  assert.match(drawBody, /state\.lastDataRendered=fieldDrawn>0;/,
    'draw() publishes the actual render outcome');
  assert.match(drawBody, /fieldDrawn=drawNearestCells\(/);
  assert.match(drawBody, /fieldDrawn=drawCircularDirectionSubcells\(/);
  assert.match(drawBody, /fieldDrawn=1;\s*$/m, 'PNG path counts as rendered');
  assert.match(drawBody, /fieldDrawn=drawBilinearSubcells\(/);
  // Cell painters return how many cells they drew.
  assert.match(grab(JS, 'function drawNearestCells(', 'function drawBilinearSubcells('),
    /return drawn;/);
  assert.match(grab(JS, 'function drawBilinearSubcells(', 'function contourCrossing('),
    /return drawn;/);
  assert.match(grab(JS, 'function drawCircularDirectionSubcells(', 'function drawProviderBoundary('),
    /return drawn;/);
  // updateQc shows the honest degraded status instead of ✓.
  const qcBody = grab(JS, 'function updateQc(){', 'function renderAll(){');
  assert.match(qcBody, /if\(!state\.lastDataRendered\)\{/,
    'QC checks the actual render state before any ✓ claim');
  assert.match(qcBody, /setQcSummary\('warn','資料層未顯示'\)/);
  assert.match(qcBody, /底圖逾時，資料層未顯示/,
    'basemap-timeout fallback wording is honest about the data layer');
  assert.ok(!/✓ 資料正常/.test(qcBody.split('!state.lastDataRendered')[1]?.split('if(isObservationMode())')[0] || ''),
    'the honesty branch itself contains no ✓ claim');
});

test('label dictionaries stay 正體中文 — no simplified han in dropdown labels', () => {
  // CL-WG-18 finding: reviewer saw simplified 云霧 in the layer dropdown after
  // a region switch. The repo tree contains no simplified labels; the
  // dropdown display value is built from the same dictionaries as the options
  // (refreshModelControls -> photographyLayerLabel/layerConfig). These
  // sentinels fail if a simplified label ever enters the dictionary again.
  const simplified = /[云雾风时温湿层观测卫顶络书数据线性标准总]/u;
  const hanOnly = (src, name) => {
    for(const m of src.matchAll(/label:\s*'([^']*)'/g)) {
      assert.ok(!simplified.test(m[1]), `${name} label '${m[1]}' contains simplified han`);
    }
    for(const m of src.matchAll(/\{label:'([^']*)'/g)) {
      assert.ok(!simplified.test(m[1]), `${name} layerConfig label '${m[1]}' contains simplified han`);
    }
  };
  hanOnly(JS, 'weather-map.js');
  hanOnly(REGIONS, 'weather-map-regions.js');
  // The dropdown is always rendered through the label dictionaries.
  assert.match(grab(JS, 'function photographyLayerLabel(', 'function refreshModelControls('),
    /return wmT\(labels\[key\] \|\| layerConfig\[key\]\?\.label \|\| key\);/,
    'dropdown labels resolve through a single dictionary chain');
  assert.match(grab(JS, 'function refreshModelControls(){', 'function switchModel('),
    /photographyLayerLabel\(key\)/,
    'option text is always the dictionary label (no ad-hoc display value)');
});

test('390px: basemap badge and region-card-sub wrap instead of mid-word ellipsis', () => {
  const mobile = CSS.slice(CSS.indexOf('@media(max-width:720px)'), CSS.indexOf('@media(max-width:380px)'));
  const status = grab(mobile, '.basemap-status{', '}');
  assert.match(status, /white-space:normal/, 'basemap badge escapes one-line truncation');
  assert.ok(!/text-overflow:ellipsis/.test(status));
  const sub = grab(mobile, '.region-card-sub{', '}');
  assert.match(sub, /white-space:normal/, 'region subtitle wraps on phones');
  assert.ok(!/text-overflow:ellipsis/.test(sub));
});

test('cache-bust pins for weather-map.js/.css move together with content changes', () => {
  const pins = [...HTML.matchAll(/(weather-map\.(?:js|css))\?v=(bclwg\d+)/g)].map(m => [m[1], m[2]]);
  assert.equal(pins.length, 2, 'both weather-map asset pins exist');
  const versions = pins.map(([, v]) => v);
  assert.equal(versions[0], versions[1], 'js and css pins are bumped together');
  assert.ok(Number(versions[0].replace('bclwg', '')) >= 19,
    `pins advanced past the CL-WG-18 content change (got ${versions[0]})`);
});