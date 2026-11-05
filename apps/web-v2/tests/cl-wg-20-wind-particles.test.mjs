// CL-WG-23: real particle-animation tests (replaces the lost CL-DATA-08-era
// file, which was 0 bytes on main despite the CL-DATA-08 report claiming
// "8 CL-WG-20 tests"). Follows the CL-WG-22 pattern: grab the real functions
// out of weather-map.js and run them against stubs. Covers: engine
// construction + density caps (390 px half density, min/cap bounds), u/v
// single-source bilinear sampling (never re-derived from the wrapped angle),
// neutral-color strokes (no hue), lifecycle (leaving the layer / toggle off /
// hidden tab all stop the loop and clear the canvas), and the CL-WG-22
// integration point (turning particles on must call ensureWindUvSidecar
// first, with honest degradation when the sidecar fails).
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');

function grab(startMarker, endMarker) {
  const a = JS.indexOf(startMarker);
  assert.ok(a >= 0, `start marker not found: ${startMarker}`);
  const b = JS.indexOf(endMarker, a);
  assert.ok(b > a, `end marker not found: ${endMarker}`);
  return JS.slice(a, b);
}

const UVKEYS_BLOCK = grab(
  'function windParticleUvKeys(layer){',
  'function windParticleField(layer){');
const FIELD_BLOCK = grab(
  'function windParticleField(layer){',
  '// ===== CL-WG-22: on-demand u/v sidecar =====');
const SIG_BLOCK = grab(
  'function particleFieldSignature(){',
  'function ensureParticleCanvas(){');
const SIZING_BLOCK = grab(
  'function ensureParticleCanvas(){',
  'function sampleParticleUv(field,lat,lon){');
const SAMPLE_BLOCK = grab(
  'function sampleParticleUv(field,lat,lon){',
  'function spawnParticle(field,rect){');
const LOOP_BLOCK = grab(
  'function spawnParticle(field,rect){',
  'function syncWindParticleAnimation(){');
const TIMESCALE_BLOCK = grab(
  'const WIND_PARTICLE_TIME_SCALE=700;',
  'function drawCoverage(){');
const TOGGLE_BLOCK = grab(
  "const particleToggle=$('wind-particle-toggle');",
  'windToggle.addEventListener');

// ---- grid fixture: 3x3, lats descending 30/29/28, lons 100/120/140 ----
const G_ROWS = 3, G_COLS = 3;
const G_LATS = [30, 29, 28];
const G_LONS = [100, 120, 140];
const VIEW = { leftlon: 100, rightlon: 140, bottomlat: 5, toplat: 40 };

function makeUvField(u, v) {
  return {
    data: { model: 'GFS' },
    u, v, rows: G_ROWS, cols: G_COLS,
    lats: G_LATS, lons: G_LONS,
  };
}

// u[i]=i (distinct per cell), v all zero - deterministic bilinear fixture.
const FIX_U = Array.from({ length: G_ROWS * G_COLS }, (_, i) => i);
const FIX_V = new Array(G_ROWS * G_COLS).fill(0);

function makeRecordingCtx() {
  const rec = { strokes: [], segments: [], fills: [], clears: [], transforms: [], cancels: [] };
  const ctx = {
    strokeStyle: '', fillStyle: '', globalCompositeOperation: '',
    lineCap: '', lineWidth: 0,
    setTransform(...a) { rec.transforms.push(a); },
    save() {}, restore() {},
    clearRect(x, y, w, h) { rec.clears.push([x, y, w, h]); },
    fillRect(x, y, w, h) { rec.fills.push({ rect: [x, y, w, h], style: ctx.fillStyle, composite: ctx.globalCompositeOperation }); },
    beginPath() {}, moveTo(x, y) { ctx._p = [x, y]; },
    lineTo(x, y) { ctx._q = [x, y]; },
    stroke() { rec.strokes.push(ctx.strokeStyle); rec.segments.push([ctx._p, ctx._q]); },
  };
  return { ctx, rec };
}

function makeCanvasStub(ctx, { width = 2600, height = 1600, clientWidth = 1300, clientHeight = 800 } = {}) {
  return {
    width, height, clientWidth, clientHeight,
    getContext: () => ctx,
    setAttribute() {},
    getBoundingClientRect: () => ({ width: clientWidth, height: clientHeight }),
    parentNode: { insertBefore() {} },
  };
}

// Full engine harness: real sizing/sampling/spawn/loop/stop/signature code
// with stubbed DOM, canvas projection, layer predicate and field provider.
function makeEngine({
  hidden = false, dirLayer = true, dpr = 1, mobile = false,
  activeData = null, decoded = {}, particleField = null,
} = {}) {
  const { ctx, rec } = makeRecordingCtx();
  const mainCanvas = makeCanvasStub(ctx);
  const rafCalls = [];
  let rafId = 0;
  const windowStub = {
    devicePixelRatio: dpr,
    matchMedia: (q) => ({ matches: mobile && q.includes('max-width:720px') }),
    requestAnimationFrame: (fn) => { rafCalls.push(fn); return ++rafId; },
    cancelAnimationFrame: (id) => rec.cancels.push(id),
  };
  const documentStub = {
    hidden,
    body: { contains: () => true },
    createElement: () => makeCanvasStub(ctx),
    addEventListener() {},
  };
  const state = {
    layer: 'wind_direction_10m_deg',
    frameIndex: 0,
    windParticles: true,
    particles: null,
    particleField,
    particleFieldKey: null,
    particleRaf: null,
    particleLastTs: null,
    particleCanvas: null,
    particleCtx: null,
  };
  const body = [
    UVKEYS_BLOCK, FIELD_BLOCK, SIG_BLOCK, SIZING_BLOCK,
    SAMPLE_BLOCK, LOOP_BLOCK, TIMESCALE_BLOCK,
    'return {windParticleUvKeys, windParticleField, windParticleAvailable,',
    'particleFieldSignature, ensureParticleCanvas, syncParticleCanvasSize,',
    'particleTargetCount, sampleParticleUv, spawnParticle, particleLoop,',
    'stopWindParticles, WIND_PARTICLE_TIME_SCALE, stateRef: state};',
  ].join('\n');
  const fn = new Function(
    'state', 'document', 'window', 'canvas', 'project',
    'isWindDirectionLayer', 'activeGfsDataset', 'decodeValue', 'renderViewBbox',
    body);
  const api = fn(
    state, documentStub, windowStub, mainCanvas,
    (lon, lat) => ({ x: (lon - 100) * 1000, y: (40 - lat) * 1000 }),
    () => dirLayer,
    () => activeData,
    (key, v) => (v == null ? null : v),
    () => VIEW);
  return { api, state, ctx, rec, rafCalls, mainCanvas, windowStub, documentStub };
}

// windParticleField standalone harness (field-construction logic only).
// CL-WG-24: the field now reads the GFS dataset (activeGfsDataset) and decodes
// the frame values itself, so the harness supplies those instead of
// activeDataset/decodedArray.
function makeFieldHarness({ gfsData }) {
  const state = { layer: 'wind_direction_10m_deg', frameIndex: 0 };
  const fn = new Function('state', 'activeGfsDataset', 'decodeValue',
    UVKEYS_BLOCK + FIELD_BLOCK +
    'return {windParticleUvKeys, windParticleField, windParticleAvailable};');
  return fn(state, () => gfsData,
    (key, v, data) => (v == null ? null : v));
}

// ===== 1. u/v key derivation =====

test('windParticleUvKeys: default layer maps to 10 m u/v; pressure layers map to their own level', () => {
  const state = { layer: 'wind_direction_10m_deg' };
  const fn = new Function('state', UVKEYS_BLOCK + 'return windParticleUvKeys;');
  const keys = fn(state);
  assert.deepEqual(keys(), { u: 'wind_u_10m_m_s', v: 'wind_v_10m_m_s' });
  assert.deepEqual(keys('wind_direction_850hpa_deg'),
    { u: 'wind_u_850hpa_m_s', v: 'wind_v_850hpa_m_s' });
  assert.deepEqual(keys('wind_direction_700hpa_deg'),
    { u: 'wind_u_700hpa_m_s', v: 'wind_v_700hpa_m_s' });
  assert.deepEqual(keys('wind_direction_925hpa_deg'),
    { u: 'wind_u_925hpa_m_s', v: 'wind_v_925hpa_m_s' });
});

// ===== 2. field construction (single source: only u/v fields qualify) =====

test('windParticleField: built from the GFS dataset (activeGfsDataset) frame values with grid metadata; null when u/v or grid/frame missing; null on length mismatch', () => {
  const grid = { rows: G_ROWS, cols: G_COLS, latitudes: G_LATS, longitudes: G_LONS };
  const missing = makeFieldHarness({ gfsData: { grid, fields: {}, frames: [] } });
  assert.equal(missing.windParticleField(), null);
  const badLen = makeFieldHarness({
    gfsData: {
      grid,
      fields: { wind_u_10m_m_s: {}, wind_v_10m_m_s: {} },
      frames: [{ values: { wind_u_10m_m_s: FIX_U, wind_v_10m_m_s: FIX_V.slice(0, 5) } }],
    },
  });
  assert.equal(badLen.windParticleField(), null);
  const ok = makeFieldHarness({
    gfsData: {
      grid,
      fields: { wind_u_10m_m_s: {}, wind_v_10m_m_s: {} },
      frames: [{ values: { wind_u_10m_m_s: FIX_U, wind_v_10m_m_s: FIX_V } }],
    },
  });
  const field = ok.windParticleField();
  assert.ok(field, 'field should be built when u/v + grid + frame present');
  assert.deepEqual(field.u, FIX_U);
  assert.deepEqual(field.v, FIX_V);
  assert.equal(field.rows, G_ROWS);
  assert.equal(field.cols, G_COLS);
  assert.equal(ok.windParticleAvailable(), true);
});

// ===== 3. engine density caps =====

test('particleTargetCount: desktop density area/2600, 4K capped at 640, tiny rect floored at 48', () => {
  const { api } = makeEngine();
  // 1300x800 = 1_040_000 / 2600 = 400
  assert.equal(api.particleTargetCount({ width: 1300, height: 800 }), 400);
  // 3840x2160 4K = 3190 raw -> capped 640
  assert.equal(api.particleTargetCount({ width: 3840, height: 2160 }), 640);
  // 20x20 raw 0 -> floor 48
  assert.equal(api.particleTargetCount({ width: 20, height: 20 }), 48);
});

test('particleTargetCount: 390 px phones run at half the desktop density, capped at 220', () => {
  const desktop = makeEngine({ mobile: false });
  const mobile = makeEngine({ mobile: true });
  // 390x844 = 329_160 / 2600 = 126.6 -> 127 raw; mobile 63.5 -> 64
  const rect = { width: 390, height: 844 };
  const d = desktop.api.particleTargetCount(rect);
  const m = mobile.api.particleTargetCount(rect);
  assert.equal(d, 127);
  assert.equal(m, 64);
  assert.equal(m, Math.round(d / 2), 'mobile must be half desktop density');
  // Large mobile viewport hits the 220 mobile cap: 390x5000 -> 750 raw -> 375 -> 220
  assert.equal(mobile.api.particleTargetCount({ width: 390, height: 5000 }), 220);
});

// ===== 4. u/v bilinear sampling =====

test('sampleParticleUv: exact at grid nodes, bilinear at cell midpoints, null outside bbox, null on non-finite values', () => {
  const { api } = makeEngine();
  const field = makeUvField(FIX_U, FIX_V);
  const node = api.sampleParticleUv(field, 30, 100);
  assert.deepEqual(node, { u: 0, v: 0 });
  const nodeEnd = api.sampleParticleUv(field, 28, 140);
  assert.equal(nodeEnd.u, 8);
  // Cell midpoint (lat 29.5, lon 110): weights 0.5/0.5 over corners
  // u00=0,u01=1,u10=3,u11=4 -> mean 2; v all 0.
  const mid = api.sampleParticleUv(field, 29.5, 110);
  assert.equal(mid.u, 2);
  assert.equal(mid.v, 0);
  assert.equal(api.sampleParticleUv(field, 30, 140.001), null);
  assert.equal(api.sampleParticleUv(field, 27.999, 120), null);
  const hole = makeUvField([...FIX_U], [...FIX_V]);
  hole.u[0] = NaN;
  assert.equal(api.sampleParticleUv(hole, 29.9, 100.1), null);
});

test('sampleParticleUv reads u and v independently - u-only field returns v=0 and vice versa (never re-derived from the wrapped direction angle)', () => {
  const { api } = makeEngine();
  const uOnly = makeUvField(FIX_U.map(() => 10), FIX_V);
  const vOnly = makeUvField(new Array(G_ROWS * G_COLS).fill(0), FIX_V.map(() => 7));
  for (const [lat, lon] of [[29.3, 115], [28.2, 132], [29.9, 101]]) {
    const s1 = api.sampleParticleUv(uOnly, lat, lon);
    assert.equal(s1.v, 0, `v must stay 0 in u-only field at ${lat},${lon}`);
    const s2 = api.sampleParticleUv(vOnly, lat, lon);
    assert.equal(s2.u, 0, `u must stay 0 in v-only field at ${lat},${lon}`);
  }
});

// ===== 5. u/v drives advection =====

function runFrame({ u, v, preSpawn = false } = {}) {
  const { api, state, rec } = makeEngine({
    particleField: makeUvField(FIX_U.map(() => u), FIX_V.map(() => v)),
  });
  if (preSpawn) state.particles = Array.from({ length: 10 }, () =>
    api.spawnParticle(state.particleField, { width: 1300, height: 800 }));
  api.particleLoop(1000);
  return { api, state, rec };
}

test('particleLoop: eastward u moves particle heads east (x increases), northward v moves them north (y decreases)', () => {
  const east = runFrame({ u: 10, v: 0, preSpawn: true });
  assert.ok(east.rec.segments.length > 0, 'u=10 must produce stroke segments');
  for (const [[x0], [x1]] of east.rec.segments) assert.ok(x1 > x0, 'u=10 (eastward) must increase x');
  const north = runFrame({ u: 0, v: 10, preSpawn: true });
  assert.ok(north.rec.segments.length > 0, 'v=10 must produce stroke segments');
  for (const [[, y0], [, y1]] of north.rec.segments) assert.ok(y1 < y0, 'v=10 (northward) must decrease y');
});

test('particleLoop: zero wind draws nothing (no phantom motion)', () => {
  const still = runFrame({ u: 0, v: 0, preSpawn: true });
  assert.equal(still.rec.segments.length, 0);
});

// ===== 6. neutral colors =====

test('particleLoop strokes are strictly neutral light/dark rgba - no hue anywhere; trail fade is destination-out black alpha', () => {
  const { api, state, rec, ctx } = makeEngine({
    particleField: makeUvField(FIX_U.map(() => 10), FIX_V),
  });
  state.particles = Array.from({ length: 10 }, () =>
    api.spawnParticle(state.particleField, { width: 1300, height: 800 }));
  api.particleLoop(1000);
  assert.ok(rec.strokes.length > 0);
  const NEUTRAL = new Set(['rgba(2,6,23,.38)', 'rgba(248,250,252,.85)']);
  for (const s of rec.strokes) {
    assert.ok(NEUTRAL.has(s), `strokeStyle must be one of the neutral pair, got ${s}`);
    assert.equal(/hsl|hue|#[0-9a-f]{3,6}/i.test(s), false, 'no hue/color-code in strokes');
  }
  assert.ok(rec.strokes.includes('rgba(248,250,252,.85)'), 'light head stroke present');
  assert.ok(rec.strokes.includes('rgba(2,6,23,.38)'), 'dark shadow stroke present');
  const fade = rec.fills[0];
  assert.ok(fade, 'trail fade fillRect must run each frame');
  assert.equal(fade.composite, 'destination-out');
  assert.equal(fade.style, 'rgba(0,0,0,0.085)');
  assert.equal(ctx.globalCompositeOperation, 'source-over', 'composite restored after fade');
});

// ===== 7. lifecycle =====

test('particleLoop first frame spawns exactly particleTargetCount particles inside the visible bbox', () => {
  const { api, state } = makeEngine({
    particleField: makeUvField(FIX_U.map(() => 10), FIX_V),
  });
  api.particleLoop(1000);
  assert.ok(state.particles, 'particles spawned');
  assert.equal(state.particles.length, api.particleTargetCount({ width: 1300, height: 800 }));
  for (const p of state.particles) {
    assert.ok(p.lat >= 28 && p.lat <= 30, `lat ${p.lat} within field/visible lat range`);
    assert.ok(p.lon >= 100 && p.lon <= 140, `lon ${p.lon} within field/visible lon range`);
    assert.ok(Number.isFinite(p.life) && p.life >= 60);
  }
});

test('particleLoop self-stops when the tab is hidden: no reschedule, raf cleared, canvas cleared full-size under identity transform', () => {
  const { api, state, rec, ctx, mainCanvas, rafCalls } = makeEngine({ hidden: true });
  state.particleCanvas = mainCanvas;
  state.particleCtx = ctx;
  state.particleRaf = null; // raf already fired; loop must not reschedule
  api.particleLoop(1000);
  assert.equal(state.particleRaf, null);
  assert.equal(rafCalls.length, 0, 'hidden tab must not schedule a new frame');
  assert.equal(state.particleLastTs, null);
  assert.deepEqual(rec.transforms[0], [1, 0, 0, 1, 0, 0], 'clear runs under identity transform');
  assert.deepEqual(rec.clears[0], [0, 0, 2600, 1600], 'full canvas cleared');
});

test('stopWindParticles cancels a pending raf and clears the full canvas', () => {
  const { api, state, rec, ctx, mainCanvas } = makeEngine({});
  state.particleCanvas = mainCanvas;
  state.particleCtx = ctx;
  state.particleRaf = 42; // pending frame scheduled by a previous tick
  api.stopWindParticles();
  assert.deepEqual(rec.cancels, [42]);
  assert.equal(state.particleRaf, null);
  assert.equal(state.particleLastTs, null);
  assert.deepEqual(rec.transforms[0], [1, 0, 0, 1, 0, 0]);
  assert.deepEqual(rec.clears[0], [0, 0, 2600, 1600]);
});

test('particleLoop self-stops when the layer is no longer a wind-direction layer', () => {
  const { api, state, rec, ctx, mainCanvas, rafCalls } = makeEngine({ dirLayer: false });
  state.particleCanvas = mainCanvas;
  state.particleCtx = ctx;
  api.particleLoop(1000);
  assert.equal(state.particleRaf, null);
  assert.equal(rafCalls.length, 0);
  assert.deepEqual(rec.clears[0], [0, 0, 2600, 1600]);
});

test('particleLoop self-stops when the u/v field disappears (no field -> stop, nothing scheduled)', () => {
  const { api, state, rafCalls } = makeEngine({ activeData: null });
  state.particleField = null; // windParticleField() must also fail
  state.particleRaf = 9;
  api.particleLoop(1000);
  assert.equal(state.particleRaf, null);
  assert.equal(rafCalls.length, 0);
});

test('particleFieldSignature binds layer + model + frame so a frame/layer change invalidates the particle swarm', () => {
  const { api, state } = makeEngine({
    particleField: makeUvField(FIX_U, FIX_V),
  });
  assert.equal(api.particleFieldSignature(), 'wind_direction_10m_deg:GFS:0');
  state.frameIndex = 2;
  assert.equal(api.particleFieldSignature(), 'wind_direction_10m_deg:GFS:2');
  state.particleField = null;
  assert.equal(api.particleFieldSignature(), null);
});

// ===== 8. integration: toggle -> ensureWindUvSidecar first (CL-WG-22) =====

function makeToggleHarness({ needed, ensure, hidden = false } = {}) {
  const calls = { ensure: 0, sync: 0, stop: 0, syncAnim: 0 };
  const toggle = {
    checked: true, disabled: false, handlers: {},
    addEventListener(type, fn) { this.handlers[type] = fn; },
  };
  const documentStub = {
    hidden, listeners: {},
    addEventListener(type, fn) { this.listeners[type] = fn; },
  };
  const fn = new Function(
    'state', 'document', '$', 'stopWindParticles', 'syncWindParticleAnimation',
    'windUvSidecarNeeded', 'ensureWindUvSidecar', 'syncWindParticleControl',
    TOGGLE_BLOCK + ';return particleToggle;');
  const state = { windParticles: false, particleField: null, windUvSidecarState: 'idle' };
  const api = fn(
    state, documentStub, () => toggle,
    () => { calls.stop++; }, () => { calls.syncAnim++; },
    () => needed,
    async () => { calls.ensure++; return ensure; },
    () => { calls.sync++; });
  return { api, state, toggle, calls, documentStub };
}

test('toggle ON with u/v missing fetches the sidecar FIRST: ensureWindUvSidecar called once, toggle re-enabled after fetch, success keeps particles on', async () => {
  const h = makeToggleHarness({ needed: true, ensure: true });
  assert.equal(typeof h.api.handlers.change, 'function', 'change handler registered');
  await h.api.handlers.change();
  assert.equal(h.calls.ensure, 1, 'ensureWindUvSidecar must be called when u/v missing');
  assert.equal(h.state.windParticles, true, 'success keeps the particle layer on');
  assert.equal(h.toggle.checked, true);
  assert.equal(h.toggle.disabled, false, 'toggle re-enabled after fetch');
  assert.equal(h.calls.sync, 1, 'control re-synced after load');
});

test('toggle ON with failed sidecar degrades honestly: particles switched off, toggle unchecked, no phantom state', async () => {
  const h = makeToggleHarness({ needed: true, ensure: false });
  await h.api.handlers.change();
  assert.equal(h.calls.ensure, 1);
  assert.equal(h.state.windParticles, false, 'failed sidecar must switch particles off');
  assert.equal(h.toggle.checked, false, 'toggle reflects the honest off state');
  assert.equal(h.state.particleField, null);
});

test('toggle while sidecar is loading is a no-op (double-fetch guard)', async () => {
  const h = makeToggleHarness({ needed: true, ensure: true });
  h.state.windUvSidecarState = 'loading';
  await h.api.handlers.change();
  assert.equal(h.calls.ensure, 0, 'no second fetch while loading');
  assert.equal(h.state.windParticles, false);
});

test('visibilitychange: hidden tab stops the particle loop, visible tab re-syncs the animation', () => {
  const h = makeToggleHarness({ needed: false, ensure: true, hidden: false });
  assert.equal(typeof h.documentStub.listeners.visibilitychange, 'function',
    'visibilitychange listener registered');
  h.documentStub.hidden = true;
  h.documentStub.listeners.visibilitychange();
  assert.equal(h.calls.stop, 1, 'hidden -> stopWindParticles');
  h.documentStub.hidden = false;
  h.documentStub.listeners.visibilitychange();
  assert.equal(h.calls.syncAnim, 1, 'visible -> syncWindParticleAnimation');
});

// ===== 9. static: the engine is wired into the page =====

test('weather-map.js wires the particle engine: dedicated canvas, raf loop, cancel and the ensureWindUvSidecar-first toggle are all referenced', () => {
  assert.ok(JS.includes("'weather-particle-canvas'"), 'dedicated transparent canvas id');
  assert.ok(JS.includes('window.requestAnimationFrame(particleLoop)'));
  assert.ok(JS.includes('cancelAnimationFrame(state.particleRaf)'));
  assert.ok(JS.includes('ensureWindUvSidecar()'), 'toggle path calls ensureWindUvSidecar');
  assert.ok(JS.includes('windUvSidecarNeeded()'));
});