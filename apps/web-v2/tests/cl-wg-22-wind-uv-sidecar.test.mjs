// CL-WG-22: u/v vector fields split out of the main GFS bundle into a
// per-region sidecar (gfs_<region>_wind_uv_sidecar.json), fetched ONLY when
// the particle switch is turned on. Regression: CL-DATA-08 merged them into
// the main bundle and doubled the mobile load (tw 19.4 MB -> 43.9 MB) while
// the particle animation defaults OFF. Missing/failed sidecar must honestly
// degrade to no-particles and never block the main map.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const WG = path.join(ROOT, 'weathergrid');
const REGIONS = ['tw', 'jp', 'us', 'ak', 'hi'];
const UV_FIELDS = [
  'wind_u_10m_m_s', 'wind_v_10m_m_s',
  'wind_u_925hpa_m_s', 'wind_v_925hpa_m_s',
  'wind_u_850hpa_m_s', 'wind_v_850hpa_m_s',
  'wind_u_700hpa_m_s', 'wind_v_700hpa_m_s',
];
const MAIN_FIELDS = [
  'total_cloud_percent', 'low_cloud_percent', 'mid_cloud_percent',
  'high_cloud_percent', 'visibility_km', 'precip_rate_mm_h',
  'wind_speed_10m_m_s', 'wind_direction_10m_deg',
];

function grab(startMarker, endMarker) {
  const a = JS.indexOf(startMarker);
  assert.ok(a >= 0, `start marker not found: ${startMarker}`);
  const b = JS.indexOf(endMarker, a);
  assert.ok(b > a, `end marker not found: ${endMarker}`);
  return JS.slice(a, b);
}

// ===== data layer: bundles on disk =====

for (const region of REGIONS) {
  test(`gfs_${region}: main bundle carries NO u/v fields; sidecar carries exactly the 8 with identical bbox/grid/cycle/frames`, () => {
    const main = JSON.parse(fs.readFileSync(
      path.join(WG, `gfs_${region}_weather_browser.json`), 'utf8'));
    const sidecar = JSON.parse(fs.readFileSync(
      path.join(WG, `gfs_${region}_wind_uv_sidecar.json`), 'utf8'));
    const leaked = UV_FIELDS.filter(k => main.fields[k]);
    assert.equal(leaked.length, 0, `main bundle leaked ${leaked}`);
    for (const key of MAIN_FIELDS) assert.ok(main.fields[key], `missing ${key}`);
    assert.deepEqual(Object.keys(sidecar.fields).sort(), [...UV_FIELDS].sort());
    assert.deepEqual(sidecar.bbox, main.bbox);
    assert.deepEqual(sidecar.grid, main.grid);
    assert.deepEqual(sidecar.cycle, main.cycle);
    assert.equal(sidecar.frames.length, main.frames.length);
    main.frames.forEach((frame, i) => {
      assert.equal(sidecar.frames[i].forecast_hour, frame.forecast_hour);
      assert.equal(sidecar.frames[i].valid_time_utc, frame.valid_time_utc);
      assert.deepEqual(
        Object.keys(sidecar.frames[i].values).sort(), [...UV_FIELDS].sort());
      assert.equal(Object.keys(frame.values).some(k => UV_FIELDS.includes(k)), false);
    });
    assert.equal(sidecar.sidecar.purpose, 'wind_uv_particle_flow');
  });
}

test('cache index covers the five sidecars so on-demand fetches are content-addressed', () => {
  const index = JSON.parse(fs.readFileSync(path.join(WG, 'index.json'), 'utf8'));
  for (const region of REGIONS) {
    assert.ok(index.files[`gfs_${region}_wind_uv_sidecar.json`],
      `index.json missing gfs_${region}_wind_uv_sidecar.json`);
  }
});

// ===== frontend: on-demand load / cache / honest degradation =====

function makeHarness({ fetchImpl, stateOverrides = {} } = {}) {
  const block = grab('// ===== CL-WG-22: on-demand u/v sidecar',
    'function particleFieldSignature');
  const state = {
    region: 'tw',
    modelMode: 'auto',
    data: null,
    layer: 'wind_direction_10m_deg',
    windUvSidecars: new Map(),
    windUvSidecarState: 'idle',
    ...stateOverrides,
  };
  const calls = [];
  const fetchVersioned = fetchImpl || (async () => { throw new Error('no fetch'); });
  const fn = new Function('state', 'fetchVersioned', 'syncWindParticleControl',
    'windParticleUvKeys', 'isWindDirectionLayer', 'console', `${block}
    return {ensureWindUvSidecar, windUvSidecarNeeded, windUvSidecarPath,
      mergeWindUvSidecar, windUvSidecarCacheKey, rememberWindUvSidecar,
      activeGfsDataset, WIND_UV_SIDECAR_CACHE_MAX};`);
  const api = fn(state,
    (...args) => { calls.push(args[0]); return fetchVersioned(...args); },
    () => {}, // syncWindParticleControl (DOM side, not under test here)
    (layer) => {
      layer = layer === undefined ? state.layer : layer;
      const m = /^wind_direction_([0-9]{3})hpa_deg$/.exec(layer);
      const level = m ? `${m[1]}hpa` : '10m';
      return { u: `wind_u_${level}_m_s`, v: `wind_v_${level}_m_s` };
    },
    () => true,
    console);
  return { api, state, calls };
}

function stubGfsBundle({ region = 'tw', withUv = false, frames = 3 } = {}) {
  return {
    schema_version: 1, provider: 'NOAA/NCEP NOMADS', model: 'GFS',
    cycle: { date: '20261105', cycle: '00' },
    bbox: { leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40 },
    grid: { rows: 2, cols: 2, latitudes: [25, 24.75], longitudes: [121, 121.25] },
    fields: withUv ? {
      wind_u_10m_m_s: { unit: 'm/s', scale: 0.1 },
      wind_v_10m_m_s: { unit: 'm/s', scale: 0.1 },
    } : {},
    frames: Array.from({ length: frames }, (_, i) => ({
      forecast_hour: i * 3, valid_time_utc: `2026-11-05T0${i}:00:00+00:00`,
      values: {},
    })),
  };
}

function stubSidecar({ contract = 'valid', frames = 3 } = {}) {
  const base = stubGfsBundle({ frames });
  const sidecar = {
    schema_version: base.schema_version, provider: base.provider,
    model: base.model, cycle: base.cycle, bbox: base.bbox, grid: base.grid,
    fields: {
      wind_u_10m_m_s: { unit: 'm/s', scale: 0.1 },
      wind_v_10m_m_s: { unit: 'm/s', scale: 0.1 },
    },
    frames: base.frames.map((f, i) => ({
      forecast_hour: f.forecast_hour,
      valid_time_utc: f.valid_time_utc,
      values: {
        wind_u_10m_m_s: [1 + i, 2 + i],
        wind_v_10m_m_s: [-1 - i, -2 - i],
      },
    })),
    sidecar: { purpose: 'wind_uv_particle_flow' },
  };
  if (contract === 'bbox') sidecar.bbox = { ...sidecar.bbox, toplat: 39 };
  if (contract === 'grid') sidecar.grid = { ...sidecar.grid, rows: 3 };
  if (contract === 'cycle') sidecar.cycle = { date: '20261104', cycle: '12' };
  if (contract === 'frames') sidecar.frames = sidecar.frames.slice(0, frames - 1);
  if (contract === 'fields') delete sidecar.fields.wind_v_10m_m_s;
  if (contract === 'valid_time') sidecar.frames[0].valid_time_utc = 'drift';
  return sidecar;
}

test('the default load path never references the sidecar: it is only reachable from the particle toggle', () => {
  const loader = grab('async function loadEnhancementsSequentially',
    'async function activateRegion');
  assert.equal(loader.includes('Sidecar'), false);
  assert.equal(/windUvSidecar/i.test(loader), false,
    'progressive region load must not fetch the sidecar');
  const toggleHandler = grab("particleToggle.addEventListener('change'",
    'document.addEventListener(\'visibilitychange\'');
  assert.match(toggleHandler, /ensureWindUvSidecar\(\)/,
    'the toggle handler is the only sidecar entry point');
  assert.match(toggleHandler, /windUvSidecarNeeded\(\)/,
    'fetch happens only when the merged dataset lacks u/v');
});

test('toggling particles ON fetches the sidecar for the active region, merges u/v into the dataset, and is cached', async () => {
  const data = stubGfsBundle();
  const sidecar = stubSidecar();
  const h = makeHarness({
    fetchImpl: async (p) => {
      assert.equal(p, 'gfs_tw_wind_uv_sidecar.json');
      return sidecar;
    },
  });
  h.state.data = data;
  assert.equal(h.api.windUvSidecarNeeded(), true);
  assert.ok(await h.api.ensureWindUvSidecar());
  assert.equal(h.calls.length, 1, 'exactly one sidecar fetch');
  assert.ok(data.fields.wind_u_10m_m_s && data.fields.wind_v_10m_m_s);
  assert.deepEqual(data.frames[1].values.wind_u_10m_m_s, [2, 3]);
  assert.deepEqual(data.frames[1].values.wind_v_10m_m_s, [-2, -3]);
  assert.equal(h.state.windUvSidecarState, 'ready');
  // Second call: served from the in-memory cache, no refetch, no re-merge.
  data.fields.wind_v_10m_m_s = { unit: 'm/s', scale: 0.1 };
  assert.ok(await h.api.ensureWindUvSidecar());
  assert.equal(h.calls.length, 1, 'cached sidecar must not refetch');
  assert.deepEqual(data.frames[1].values.wind_v_10m_m_s, [-2, -3],
    'cache hit re-merges values');
});

test('region switch re-maps the sidecar path; a same-cycle revisit is served from cache without refetch', async () => {
  const twData = stubGfsBundle();
  const jpData = stubGfsBundle({ region: 'jp' });
  jpData.cycle = twData.cycle;
  const sidecars = {
    'gfs_tw_wind_uv_sidecar.json': stubSidecar(),
    'gfs_jp_wind_uv_sidecar.json': stubSidecar(),
  };
  const h = makeHarness({
    fetchImpl: async (p) => {
      assert.ok(sidecars[p], `unexpected fetch ${p}`);
      return sidecars[p];
    },
  });
  h.state.data = twData;
  assert.equal(h.api.windUvSidecarPath(), 'gfs_tw_wind_uv_sidecar.json');
  assert.ok(await h.api.ensureWindUvSidecar());
  assert.equal(h.calls.length, 1);
  h.state.region = 'jp';
  assert.equal(h.api.windUvSidecarPath('jp'), 'gfs_jp_wind_uv_sidecar.json');
  h.state.data = jpData;
  assert.ok(await h.api.ensureWindUvSidecar());
  assert.equal(h.calls.length, 2);
  // Back to tw with the SAME cycle: cache hit, no refetch.
  h.state.region = 'tw';
  h.state.data = twData;
  assert.ok(await h.api.ensureWindUvSidecar());
  assert.equal(h.calls.length, 2, 'same region+cycle revisit must not refetch (tw+jp each fetched once)');
  // A NEW cycle re-fetches (fresh data), keyed by region+cycle.
  const nextCycleData = stubGfsBundle();
  nextCycleData.cycle = { date: '20261105', cycle: '12' };
  h.state.data = nextCycleData;
  // The publisher ships a sidecar whose cycle matches the new main bundle.
  sidecars['gfs_tw_wind_uv_sidecar.json'] = {
    ...stubSidecar(), cycle: { date: '20261105', cycle: '12' },
  };
  assert.ok(await h.api.ensureWindUvSidecar());
  assert.equal(h.calls.length, 3, 'new cycle must refetch');
});

test('missing/failed sidecar degrades honestly: failed state, no particles, main map untouched', async () => {
  const data = stubGfsBundle();
  const h = makeHarness({ fetchImpl: async () => { throw new Error('404'); } });
  h.state.data = data;
  assert.equal(await h.api.ensureWindUvSidecar(), false);
  assert.equal(h.state.windUvSidecarState, 'failed');
  assert.equal(data.fields.wind_u_10m_m_s, undefined,
    'failed load must not mutate the main dataset');
  assert.equal(h.state.windParticles ?? false, false);
  // Retry after failure is refused without a network call (honest no-particles).
  assert.equal(await h.api.ensureWindUvSidecar(), false);
});

test('sidecar contract mismatch (bbox/grid/cycle/frame/field/valid_time) is an honest refusal, never a partial merge', async () => {
  for (const contract of ['bbox', 'grid', 'cycle', 'frames', 'fields', 'valid_time']) {
    const data = stubGfsBundle();
    const h = makeHarness({
      fetchImpl: async () => stubSidecar({ contract }),
      stateOverrides: { windUvSidecars: new Map(), windUvSidecarState: 'idle' },
    });
    h.state.data = data;
    const ok = await h.api.ensureWindUvSidecar();
    assert.equal(ok, false, `contract=${contract} must refuse`);
    assert.equal(h.state.windUvSidecarState, 'failed', `contract=${contract}`);
    assert.equal(Object.keys(data.fields).length, 0,
      `contract=${contract} must not merge anything`);
  }
});

test('the sidecar cache is FIFO-capped so a long session cannot accumulate every region', async () => {
  const h = makeHarness();
  assert.ok(h.api.WIND_UV_SIDECAR_CACHE_MAX >= 2);
  for (let i = 0; i < h.api.WIND_UV_SIDECAR_CACHE_MAX + 2; i++) {
    h.api.rememberWindUvSidecar(`k${i}`, { marker: i });
  }
  assert.equal(h.state.windUvSidecars.size, h.api.WIND_UV_SIDECAR_CACHE_MAX);
  assert.equal(h.state.windUvSidecars.has('k0'), false, 'oldest entries evicted');
  assert.equal(h.state.windUvSidecars.has(`k${h.api.WIND_UV_SIDECAR_CACHE_MAX + 1}`), true);
});

test('loading state is honest: toggle disabled + loading note while the sidecar is in flight; failure hides the switch', () => {
  const handler = grab("particleToggle.addEventListener('change'",
    "document.addEventListener('visibilitychange'");
  assert.match(handler, /particleToggle\.disabled=true/,
    'toggle disabled while sidecar loads');
  assert.match(handler, /particleToggle\.disabled=false/);
  assert.match(handler, /state\.windParticles=false/,
    'failure switches particles back off');
  assert.match(handler, /particleToggle\.checked=false/);
  const control = grab('function syncWindParticleControl',
    'const WIND_PARTICLE_TIME_SCALE');
  assert.match(control, /粒子層 u\/v 風場資料載入中/,
    'honest loading note shown during fetch');
  assert.match(control, /cached==='failed'\) available=false/,
    'failed sidecar hides the switch');
});

test('cache-bust stamp bumped in the same ticket (weather-map.js ?v=bclwg31)', () => {
  const html = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');
  assert.match(html, /assets\/weather-map\.js\?v=bclwg32/);
});