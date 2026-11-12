// CL-UI-59: selecting a spot on the weather map must NOT reposition the map
// camera. Owner requirement: tapping another spot swaps the data panel +
// marker highlight, but the view (zoom + center) stays exactly where the user
// put it. The camera may move for a spot only on (a) deep-link initial load
// (applyDeepLinkSpotCamera — untouched) and (b) the explicit 「定位景點」
// control (#locate-spot → locateSpot()).
//
// Mechanism tested here:
//   1. selectSpot() no longer calls fitCoverageBbox/zoomToSpot and no longer
//      resets state.view to the timeline bbox (functional mock test: spies
//      must record zero calls for both select and clear).
//   2. locateSpot() is the explicit re-center path (functional mock test).
//   3. #locate-spot exists in weather-map.html, starts disabled, is wired in
//      initControls, and gets its disabled state from updateLocateSpotButton.
//   4. i18n keys wm_locate_aria/wm_locate_text exist in all three dictionaries.
//   5. Cache-bust: weather-map.js bumped to bclwg35 in weather-map.html.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(path.dirname(require.resolve('../../../assets/weather-map-regions.js')), '..');
const MAP_JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const WG_HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

function grab(src, start, end) {
  const a = src.indexOf(start);
  assert.ok(a !== -1, `source slice start not found: ${start}`);
  const b = src.indexOf(end, a);
  assert.ok(b !== -1, `source slice end not found: ${end}`);
  return src.slice(a, b);
}

// ---------------------------------------------------------------------------
// 1. selectSpot must not move the camera (mock-map spy test)
// ---------------------------------------------------------------------------
function buildFn(slice, names, tail = '') {
  if (!slice.endsWith('\n')) slice += '\n';
  return new Function(...names, slice + tail);
}

function spySpots() {
  const calls = [];
  const spy = (name) => (...args) => { calls.push([name, ...args]); };
  return { calls, spy };
}

test('CL-UI-59: selectSpot only updates data panel — no camera reposition, no view reset', () => {
  const slice = grab(MAP_JS, 'function selectSpot(', 'function locateSpot(');
  const factory = buildFn(slice,
    ['state', 'refreshOpportunityOptions', 'updateLocateSpotButton', 'renderAll',
     'fitCoverageBbox', 'zoomToSpot', 'selectedCoverageGroup', 'unionViewport', 'selectedSpot'],
    '; return selectSpot;');
  const { calls, spy } = spySpots();
  const state = { spotId: '', opportunityId: 'prev', view: { leftlon: 1 } };
  const selectSpot = factory(
    state,
    spy('refreshOpportunityOptions'),
    spy('updateLocateSpotButton'),
    spy('renderAll'),
    spy('fitCoverageBbox'),
    spy('zoomToSpot'),
    spy('selectedCoverageGroup'),
    spy('unionViewport'),
    spy('selectedSpot')
  );

  // Select a spot: camera helpers must stay silent.
  selectSpot('tw-001-P01');
  assert.equal(state.spotId, 'tw-001-P01');
  assert.equal(state.opportunityId, '');
  const moved = calls.filter(([name]) =>
    name === 'fitCoverageBbox' || name === 'zoomToSpot');
  assert.deepEqual(moved, [],
    'selectSpot must not call fitCoverageBbox/zoomToSpot (CL-UI-59 owner requirement)');
  assert.ok(calls.some(([name]) => name === 'renderAll'), 'data panel must still re-render');

  // Clear the selection: previously reset state.view to the timeline bbox —
  // also a camera move; must now leave state.view untouched.
  const viewBefore = { ...state.view };
  selectSpot('');
  assert.equal(state.spotId, '');
  assert.deepEqual(state.view, viewBefore, 'clearing the spot must not reset state.view');
});

test('CL-UI-59: selectSpot source contains no camera calls', () => {
  const slice = grab(MAP_JS, 'function selectSpot(', 'function locateSpot(');
  assert.ok(!/fitCoverageBbox|zoomToSpot|setViewBbox|state\.view\s*=/.test(slice),
    'selectSpot body must not reposition the camera');
});

// ---------------------------------------------------------------------------
// 2. locateSpot is the explicit manual re-center path
// ---------------------------------------------------------------------------
test('CL-UI-59: locateSpot re-centers via fitCoverageBbox/zoomToSpot on demand', () => {
  const slice = grab(MAP_JS, 'function locateSpot(', 'function refreshOpportunityOptions(');
  const { calls, spy } = spySpots();
  const buildLocateSpot = buildFn(slice,
    ['state', 'selectedCoverageGroup', 'unionViewport', 'fitCoverageBbox', 'zoomToSpot', 'selectedSpot'],
    '; return locateSpot;');

  // No spot selected: no-op.
  const locateSpotNoSpot = buildLocateSpot({ spotId: '' }, spy('selectedCoverageGroup'), spy('unionViewport'),
    spy('fitCoverageBbox'), spy('zoomToSpot'), spy('selectedSpot'));
  locateSpotNoSpot();
  assert.deepEqual(calls, []);

  // Spot with coverage union → fitCoverageBbox path.
  const union = { west: 120, east: 122, south: 23, north: 25 };
  const locateSpot = buildLocateSpot(
    { spotId: 'tw-001-P01' },
    () => ({ opportunities: [1, 2] }),
    (ops) => (ops.length ? union : null),
    spy('fitCoverageBbox'),
    spy('zoomToSpot'),
    spy('selectedSpot')
  );
  locateSpot();
  assert.deepEqual(calls.filter(([n]) => n === 'fitCoverageBbox'), [['fitCoverageBbox', union]]);
  assert.ok(!calls.some(([n]) => n === 'zoomToSpot'));

  // Spot without coverage → zoomToSpot fallback.
  calls.length = 0;
  const spot = { spot_id: 'tw-002-P01', lat: 24.1, lon: 121.5 };
  const locateSpotBare = buildLocateSpot(
    { spotId: 'tw-002-P01' },
    () => null,
    () => null,
    spy('fitCoverageBbox'),
    spy('zoomToSpot'),
    () => spot
  );
  locateSpotBare();
  assert.deepEqual(calls.filter(([n]) => n === 'zoomToSpot'), [['zoomToSpot', spot]]);
});

// ---------------------------------------------------------------------------
// 3. Button markup, wiring, and disabled state
// ---------------------------------------------------------------------------
test('CL-UI-59: #locate-spot button exists, starts disabled, and is wired', () => {
  assert.match(WG_HTML, /<button id="locate-spot" class="map-reset-button" type="button" disabled/);
  assert.match(WG_HTML, /data-i18n="wm_locate_text"/);
  assert.match(WG_HTML, /data-i18n-aria="wm_locate_aria"/);
  // Click handler wired to locateSpot().
  assert.match(MAP_JS, /\$\('locate-spot'\)\.addEventListener\('click'/);
  assert.match(MAP_JS, /locateSpot\(\);\s*renderAll\(\);/);
  // Disabled state follows the selection.
  assert.match(MAP_JS, /function updateLocateSpotButton\(\)/);
  assert.match(MAP_JS, /btn\.disabled = !state\.spotId/);
  assert.match(MAP_JS, /updateLocateSpotButton\(\);\s*\n\s*\}\s*\n\s*\/\/ CL-UI-59/);
});

// ---------------------------------------------------------------------------
// 4. Trilingual i18n
// ---------------------------------------------------------------------------
test('CL-UI-59: wm_locate_aria / wm_locate_text exist in zh-TW, en, ja', () => {
  for (const key of ['wm_locate_aria', 'wm_locate_text']) {
    const n = MAP_JS.split(new RegExp(key + ":'")).length - 1;
    assert.ok(n >= 3, `${key} must be defined in all three dictionaries (found ${n})`);
  }
});

// ---------------------------------------------------------------------------
// 5. Cache-bust
// ---------------------------------------------------------------------------
test('CL-UI-59: weather-map.js stamp bumped to bclwg35 in the same ticket', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg35/);
  assert.ok(!/assets\/weather-map\.js\?v=bclwg34/.test(WG_HTML), 'old js stamp must not linger');
  assert.match(MAP_JS, /CL-UI-59/);
});
