// CL-WG-11: GFS bbox-outside fill (Taiwan pilot) — trigger conditions,
// feather-band alpha gradient, and GFS frame-axis alignment.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const fill = require('../../../assets/weather-map-gfs-fill.js');

// Bboxes matching the GFS TW bundle (CL-WG-12 widened window) and the region registry.
const GFS_TW = {leftlon: 116, rightlon: 125, bottomlat: 20, toplat: 28};
const REGION_TW = {leftlon: 118, rightlon: 123, bottomlat: 21.5, toplat: 26.5};

function gfsDataset() {
  return {
    bbox: GFS_TW,
    grid: {rows: 26, cols: 25, longitudes: [], latitudes: []},
    fields: {low_cloud_percent: {scale: 1}, visibility_km: {scale: .1},
      wind_speed_10m_m_s: {scale: .1}, wind_direction_10m_deg: {scale: 1}},
    frames: [
      {valid_time_utc: '2026-11-04T00:00:00+00:00', values: {low_cloud_percent: [0]}},
      {valid_time_utc: '2026-11-04T03:00:00+00:00', values: {low_cloud_percent: [1]}},
      {valid_time_utc: '2026-11-04T06:00:00+00:00', values: {low_cloud_percent: [2]}}
    ]
  };
}

test('fill trigger: activates when the view extends past the region bbox', () => {
  // Camera padding shows area west of the 118°E region edge.
  const view = {leftlon: 116.7, rightlon: 123.4, bottomlat: 21.3, toplat: 26.5};
  const plan = fill.gfsFillPlan({
    regionId: 'tw', layerKey: 'low_cloud_percent',
    gfsDataset: gfsDataset(), viewBbox: view, regionBbox: REGION_TW
  });
  assert.ok(plan, 'plan must activate outside the region bbox');
  assert.equal(plan.layerKey, 'low_cloud_percent');
  assert.deepEqual(plan.main_bbox, REGION_TW,
    'the feather seam must be anchored on the region bbox');
  assert.deepEqual(plan.gfs_bbox, GFS_TW);
  assert.equal(plan.band_deg, 0.5);
});

test('fill trigger: inactive when the view is fully inside the region bbox', () => {
  const plan = fill.gfsFillPlan({
    regionId: 'tw', layerKey: 'low_cloud_percent',
    gfsDataset: gfsDataset(), viewBbox: REGION_TW, regionBbox: REGION_TW
  });
  assert.equal(plan, null);
});

test('fill trigger: inactive for layers without a same-semantics GFS field (honest blank)', () => {
  const view = {leftlon: 116.7, rightlon: 123.4, bottomlat: 21.3, toplat: 26.5};
  for (const key of ['observed_cloud_mask', 'cloud_top_height_m',
    'aerosol_optical_depth_550nm', 'pm2_5_ug_m3',
    'nighttime_lights_radiance_nw_cm2_sr',
    'relative_humidity_2m_percent', 'temperature_2m_c',
    'precip_total_mm', 'shortwave_flux_w_m2']) {
    assert.equal(fill.gfsFillFieldAvailable(key), false, `${key} must not be filled`);
    const plan = fill.gfsFillPlan({
      regionId: 'tw', layerKey: key,
      gfsDataset: gfsDataset(), viewBbox: view, regionBbox: REGION_TW
    });
    assert.equal(plan, null, `${key} fill must stay blank (semantic mismatch)`);
  }
});

test('fill trigger: pilot scope is Taiwan only', () => {
  const view = {leftlon: 116.7, rightlon: 123.4, bottomlat: 21.3, toplat: 26.5};
  const plan = fill.gfsFillPlan({
    regionId: 'jp', layerKey: 'low_cloud_percent',
    gfsDataset: gfsDataset(), viewBbox: view, regionBbox: REGION_TW
  });
  assert.equal(plan, null);
});

test('fill trigger: inactive when the GFS bundle lacks the layer field or frames', () => {
  const view = {leftlon: 116.7, rightlon: 123.4, bottomlat: 21.3, toplat: 26.5};
  const noField = gfsDataset();
  delete noField.fields.low_cloud_percent;
  assert.equal(fill.gfsFillPlan({
    regionId: 'tw', layerKey: 'low_cloud_percent',
    gfsDataset: noField, viewBbox: view, regionBbox: REGION_TW
  }), null);
  const noFrames = gfsDataset();
  noFrames.frames = [];
  assert.equal(fill.gfsFillPlan({
    regionId: 'tw', layerKey: 'low_cloud_percent',
    gfsDataset: noFrames, viewBbox: view, regionBbox: REGION_TW
  }), null);
});

test('fill trigger: inactive when the GFS bundle does not extend past the region bbox', () => {
  const view = {leftlon: 116.7, rightlon: 123.4, bottomlat: 21.3, toplat: 26.5};
  const narrow = gfsDataset();
  narrow.bbox = {...REGION_TW};
  assert.equal(fill.gfsFillPlan({
    regionId: 'tw', layerKey: 'low_cloud_percent',
    gfsDataset: narrow, viewBbox: view, regionBbox: REGION_TW
  }), null);
});

test('feather band: alpha is 0 inside the region bbox and ramps 0→1 across 0.5° outside', () => {
  // Inside the region bbox: zero (main-source territory, never overwritten).
  assert.equal(fill.gfsFillFeatherAlpha({lon: 120.5, lat: 24}, REGION_TW), 0);
  // Exactly on the west edge: still 0.
  assert.equal(fill.gfsFillFeatherAlpha({lon: 118, lat: 24}, REGION_TW), 0);
  // Monotonic gradient across the band, reaching 1 at 0.5° out.
  const alphas = [];
  for (let d = 0; d <= 0.5; d += 0.1) {
    alphas.push(fill.gfsFillFeatherAlpha({lon: 118 - d, lat: 24}, REGION_TW));
  }
  for (let i = 1; i < alphas.length; i++) {
    assert.ok(alphas[i] > alphas[i - 1], `alpha must increase across the band at d=${i * 0.1}`);
  }
  assert.ok(Math.abs(alphas[0]) < 1e-9);
  assert.ok(Math.abs(alphas[alphas.length - 1] - 1) < 1e-9,
    'alpha reaches 1 at the band outer edge');
  // Farther out stays saturated at 1.
  assert.equal(fill.gfsFillFeatherAlpha({lon: 117.0, lat: 24}, REGION_TW), 1);
  // Works on every side of the bbox (east, south, north).
  assert.ok(fill.gfsFillFeatherAlpha({lon: 123.25, lat: 24}, REGION_TW) > 0);
  assert.ok(fill.gfsFillFeatherAlpha({lon: 120.5, lat: 21.25}, REGION_TW) > 0);
  assert.ok(fill.gfsFillFeatherAlpha({lon: 120.5, lat: 26.75}, REGION_TW) > 0);
});

test('feather band: 0.5° band matches the ticket spec constant', () => {
  assert.equal(fill.GFS_FILL_BAND_DEG, 0.5);
});

test('frame alignment: GFS frame is the nearest valid time to the main source frame', () => {
  const gfs = gfsDataset();
  // Main frame at 03:10 → nearest GFS frame is 03:00 (offset -10 min).
  let hit = fill.nearestGfsFrame(gfs, '2026-11-04T03:10:00+00:00');
  assert.equal(hit.frame.valid_time_utc, '2026-11-04T03:00:00+00:00');
  assert.equal(hit.offset_minutes, -10);
  // 05:40 → nearest is 06:00 (+20), not 03:00 (-160).
  hit = fill.nearestGfsFrame(gfs, '2026-11-04T05:40:00+00:00');
  assert.equal(hit.frame.valid_time_utc, '2026-11-04T06:00:00+00:00');
  assert.equal(hit.offset_minutes, 20);
  // Missing target time → null (no fabricated alignment).
  assert.equal(fill.nearestGfsFrame(gfs, null), null);
  assert.equal(fill.nearestGfsFrame({frames: []}, '2026-11-04T03:00:00+00:00'), null);
});
