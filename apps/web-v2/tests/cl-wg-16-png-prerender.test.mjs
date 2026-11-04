// CL-WG-16: pre-rendered PNG frame path tests.
// Covers: shared palette pins, manifest parsing, PNG path-selection logic
// (incl. palette_version fallback), timeline frame switching between PNG
// frames, manifest-derived stub dataset, generator PNG bytes (decode +
// pixel pin against the shared palette), and the weather-map.js layerConfig
// single-source assertion.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import zlib from 'node:zlib';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { rgbForTest } from './cl-wg-16-rgb-helper.mjs';

const require_ = createRequire(import.meta.url);
const REPO = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')), '../../..');
const palette = require_(path.join(REPO, 'assets/weather-map-palette.js'));

// ---------- shared palette pins (single render source) ----------
test('palette module exports PALETTE_VERSION and pinned cloud bands', () => {
  assert.equal(palette.PALETTE_VERSION, 'wg16-p1');
  assert.deepEqual(palette.CLOUD_PERCENT_BREAKS, [0, 20, 40, 50, 70, 85, 100]);
  assert.equal(palette.CLOUD_MAX_OVERLAY_ALPHA, .78);
});

test('pinned colors: cloud band colors are the exact live palette strings', () => {
  const cloud = palette.LAYER_RENDER_CONFIG.low_cloud_percent;
  assert.equal(palette.cloudColorFor(0), 'hsl(190 78% 68%)');
  assert.equal(palette.cloudColorFor(19.9), 'hsl(190 78% 68%)');
  assert.equal(palette.cloudColorFor(30), 'hsl(199 82% 56%)');
  assert.equal(palette.cloudColorFor(45), 'hsl(216 82% 50%)');
  assert.equal(palette.cloudColorFor(55), 'hsl(238 78% 50%)');
  assert.equal(palette.cloudColorFor(80), 'hsl(263 72% 60%)');
  assert.equal(palette.cloudColorFor(99), 'hsl(285 48% 82%)');
  assert.equal(palette.cloudColorFor(100), 'hsl(285 48% 82%)');
  assert.ok(cloud.domain);
});

test('pinned opacities: cloud hinge at 50% and visibility falloff', () => {
  const cloud = palette.LAYER_RENDER_CONFIG.low_cloud_percent;
  const vis = palette.LAYER_RENDER_CONFIG.visibility_km;
  assert.equal(palette.cellOpacityFor(0, cloud), .02);
  assert.equal(palette.cellOpacityFor(20, cloud), .12);
  assert.equal(palette.cellOpacityFor(50, cloud), .55);
  assert.equal(palette.cellOpacityFor(100, cloud), 1);
  assert.equal(palette.cellOpacityFor(null, cloud), .08);
  // visibility: t=0 -> .08+.92 = 1 ; t=1 -> .08
  assert.equal(Math.round(palette.cellOpacityFor(0, vis) * 255), 255);
  assert.equal(Math.round(palette.cellOpacityFor(10, vis) * 255), 190);
  assert.equal(Math.round(palette.cellOpacityFor(30, vis) * 255), 20);
});

test('pinned RGB: hsl strings convert to the canonical 8-bit colors', () => {
  // rgbForTest reimplements the CSS hsl() conversion independently of the
  // generator code (see cl-wg-16-rgb-helper.mjs); these constants were also
  // cross-pinned in test_weathergrid_png_prerender.py.
  assert.deepEqual(rgbForTest('hsl(199 82% 56%)'), [51, 177, 235]);
  assert.deepEqual(rgbForTest('hsl(5 72% 46%)'), [202, 47, 33]);
  assert.deepEqual(rgbForTest('hsl(150 72% 46%)'), [33, 202, 117]);
});

// ---------- weather-map.js layerConfig single-source assertion ----------
test('weather-map.js layerConfig spreads the shared LAYER_RENDER_CONFIG', () => {
  const src = fs.readFileSync(path.join(REPO, 'assets/weather-map.js'), 'utf8');
  const keys = Object.keys(palette.LAYER_RENDER_CONFIG);
  for(const key of keys){
    assert.ok(
      src.includes(`layerConfig['${key}']={label:'`),
      `layerConfig label entry missing for ${key}`
    );
    assert.ok(
      src.includes(`...window.WeatherMapPalette.LAYER_RENDER_CONFIG['${key}']`),
      `layerConfig spread missing for ${key}`
    );
  }
  // The old inline palette/domain copies must be gone from weather-map.js.
  assert.ok(!/layerConfig = \{\n\s+total_cloud_percent:\{label:'/.test(src));
});

// ---------- PNG path-selection logic (grabbed from weather-map.js) ----------
function grabSlice(startMarker, endMarker){
  const src = fs.readFileSync(path.join(REPO, 'assets/weather-map.js'), 'utf8');
  const s = src.indexOf(startMarker);
  assert.ok(s >= 0, `marker not found: ${startMarker}`);
  const e = src.indexOf(endMarker, s);
  assert.ok(e > s, `end marker not found: ${endMarker}`);
  return src.slice(s, e);
}

const baseManifest = {
  schema_version: 1,
  palette_version: palette.PALETTE_VERSION,
  region: 'tw',
  sources: {
    gfs: {
      bbox: {leftlon: 105, rightlon: 145, toplat: 40, bottomlat: 5},
      grid: {rows: 4, cols: 5, latitudes: [5, 10, 20, 40], longitudes: [105, 115, 125, 135, 145]},
      layers: {
        total_cloud_percent: {covered: true, scale: 1, frames: [
          {forecast_hour: 0, valid_time_utc: '2026-11-03T12:00:00+00:00', file: 'gfs/total_cloud_percent/f000.png'},
          {forecast_hour: 3, valid_time_utc: '2026-11-03T15:00:00+00:00', file: 'gfs/total_cloud_percent/f003.png'}
        ]},
        visibility_km: {covered: true, scale: 1, frames: [
          {forecast_hour: 0, valid_time_utc: '2026-11-03T12:00:00+00:00', file: 'gfs/visibility_km/f000.png'}
        ]},
        wind_speed_10m_m_s: {covered: false}
      }
    },
    icon: { layers: { low_cloud_percent: {covered: false} } }
  }
};

// Deterministic harness: exposes the real pngSourceIdFor/pngFrameDecision
// functions with datasets registered in a stubbed state.
function harnessWithDatasets(datasets){
  const assignments = Object.entries(datasets)
    .map(([field, ds]) => `state.${field} = __datasets[${JSON.stringify(field)}];`).join('\n');
  const body = grabSlice('function pngManifestUsable(manifest){', 'function pngImageEntry(file){');
  return new Function('__datasets', `
    const PNG_PALETTE_VERSION = ${JSON.stringify(palette.PALETTE_VERSION)};
    const state = { region: 'tw' };
    ${assignments}
    function regionManifest(){
      return [
        {id:'gfs', field:'data'},
        {id:'icon', field:'iconData'},
        {id:'jma', field:'jmaData'}
      ].filter(e => state[e.field]);
    }
    ${body}
    return { pngSourceIdFor, pngFrameDecision, pngManifestUsable };
  `)(datasets);
}

const gfsDataset = {};
const iconDataset = {};
const harness = harnessWithDatasets({ data: gfsDataset, iconData: iconDataset });

test('pngFrameDecision: covered source/layer/frame selects the PNG file', () => {
  const frame = {valid_time_utc: '2026-11-03T12:00:00+00:00'};
  const d = harness.pngFrameDecision(gfsDataset, 'total_cloud_percent', frame, baseManifest);
  assert.equal(d.ok, true);
  assert.equal(d.sourceId, 'gfs');
  assert.equal(d.frame.file, 'gfs/total_cloud_percent/f000.png');
  assert.equal(d.frame.forecast_hour, 0);
});

test('pngFrameDecision: timeline frame switch selects the matching frame file', () => {
  const d3 = harness.pngFrameDecision(gfsDataset, 'total_cloud_percent',
    {valid_time_utc: '2026-11-03T15:00:00+00:00'}, baseManifest);
  assert.equal(d3.ok, true);
  assert.equal(d3.frame.file, 'gfs/total_cloud_percent/f003.png');
  assert.equal(d3.frame.forecast_hour, 3);
});

test('pngFrameDecision: palette_version mismatch forces JSON fallback', () => {
  const stale = {...baseManifest, palette_version: 'wg15-old'};
  const d = harness.pngFrameDecision(gfsDataset, 'total_cloud_percent',
    {valid_time_utc: '2026-11-03T12:00:00+00:00'}, stale);
  assert.equal(d.ok, false);
  assert.equal(d.reason, 'manifest_unavailable_or_version');
});

test('pngFrameDecision: missing manifest / null frame fall back', () => {
  const d = harness.pngFrameDecision(gfsDataset, 'total_cloud_percent',
    {valid_time_utc: '2026-11-03T12:00:00+00:00'}, null);
  assert.equal(d.ok, false);
  assert.equal(d.reason, 'manifest_unavailable_or_version');
  const d2 = harness.pngFrameDecision(gfsDataset, 'total_cloud_percent', null, baseManifest);
  assert.equal(d2.ok, false);
  assert.equal(d2.reason, 'no_frame');
});

test('pngFrameDecision: uncovered layer and uncovered frame fall back', () => {
  const d = harness.pngFrameDecision(gfsDataset, 'wind_speed_10m_m_s',
    {valid_time_utc: '2026-11-03T12:00:00+00:00'}, baseManifest);
  assert.equal(d.ok, false);
  assert.equal(d.reason, 'layer_not_covered');
  const d2 = harness.pngFrameDecision(gfsDataset, 'total_cloud_percent',
    {valid_time_utc: '2026-11-03T18:00:00+00:00'}, baseManifest);
  assert.equal(d2.ok, false);
  assert.equal(d2.reason, 'frame_not_covered');
});

test('pngFrameDecision: auto-mode dataset of another source maps to its own entry', () => {
  const d = harness.pngFrameDecision(iconDataset, 'total_cloud_percent',
    {valid_time_utc: '2026-11-03T12:00:00+00:00'}, baseManifest);
  assert.equal(d.ok, false);
  assert.equal(d.reason, 'layer_not_covered'); // icon source present, layer not covered
});

// ---------- manifest-derived stub dataset ----------
test('stubDatasetFromManifest: covered layers only, frame list from manifest', () => {
  const body = grabSlice('function stubDatasetFromManifest', 'const PACKED_NULL_SENTINEL');
  const fn = new Function(`
    ${body}
    return stubDatasetFromManifest;
  `)();
  const stub = fn(baseManifest, 'gfs');
  assert.ok(stub);
  assert.equal(stub.png_prerendered, true);
  assert.deepEqual(Object.keys(stub.fields).sort(), ['total_cloud_percent', 'visibility_km']);
  assert.equal(stub.frames.length, 2);
  assert.equal(stub.frames[1].valid_time_utc, '2026-11-03T15:00:00+00:00');
  assert.deepEqual(stub.frames[0].values, {});
  assert.equal(stub.bbox.leftlon, 105);
  assert.equal(stub.grid.rows, 4);
});

test('stubDatasetFromManifest: null when source has no covered layers', () => {
  const body = grabSlice('function stubDatasetFromManifest', 'const PACKED_NULL_SENTINEL');
  const fn = new Function(`${body} return stubDatasetFromManifest;`)();
  assert.equal(fn(baseManifest, 'icon'), null);
  assert.equal(fn(baseManifest, 'nope'), null);
});

// ---------- manifest parsing ----------
test('loadPngManifest: rejects non-schema / malformed manifests', async () => {
  const body = grabSlice('async function loadPngManifest', 'function pngManifestUsable');
  const holder = {};
  const fn = new Function('holder', `
    const window = { location: { search: '' } };
    const fetch = (...a) => holder.fetchImpl(...a);
    ${body}
    return loadPngManifest;
  `)(holder);
  holder.fetchImpl = async () => ({ok: true, json: async () => ({foo: 1})});
  assert.equal(await fn('tw'), null);
  holder.fetchImpl = async () => ({ok: false});
  assert.equal(await fn('tw'), null);
  holder.fetchImpl = async () => { throw new Error('network'); };
  assert.equal(await fn('tw'), null);
  holder.fetchImpl = async () => ({ok: true, json: async () => ({schema_version: 1, sources: {}})});
  assert.deepEqual(await fn('tw'), {schema_version: 1, sources: {}});
});

// ---------- generator: real PNG bytes ----------
function decodePng(buf){
  assert.deepEqual([...buf.slice(0, 8)], [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  let off = 8;
  let width, height, idat = [];
  while(off < buf.length){
    const len = buf.readUInt32BE(off);
    const type = buf.toString('ascii', off + 4, off + 8);
    const data = buf.slice(off + 8, off + 8 + len);
    if(type === 'IHDR'){
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      assert.equal(data[8], 8);   // bit depth
      assert.equal(data[9], 6);   // RGBA
    }else if(type === 'IDAT'){
      idat.push(data);
    }
    off += 12 + len;
  }
  const raw = zlib.inflateSync(Buffer.concat(idat));
  const rgba = Buffer.alloc(width * height * 4);
  for(let y = 0; y < height; y++){
    assert.equal(raw[y * (width * 4 + 1)], 0); // filter none
    raw.copy(rgba, y * width * 4, y * (width * 4 + 1) + 1, (y + 1) * (width * 4 + 1));
  }
  return {width, height, rgba};
}

test('generator: pixels equal the shared palette for pinned values, rows flipped north-up', {timeout: 30000}, () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'wg16-'));
  // 2x2 grid, latitudes ascending (row 0 = south). Values chosen so each cell
  // pins a different palette branch; one null cell stays transparent.
  const bundle = {
    schema_version: 1, model: 'TEST', bbox: {leftlon: 105, rightlon: 106, bottomlat: 5, toplat: 6},
    grid: {rows: 2, cols: 2, latitudes: [5, 6], longitudes: [105, 106]},
    fields: {
      total_cloud_percent: {scale: 1},
      visibility_km: {scale: 1}
    },
    frames: [{
      forecast_hour: 0,
      valid_time_utc: '2026-11-03T12:00:00+00:00',
      values: {
        total_cloud_percent: [30, null, 55, 100],
        visibility_km: [0, 10, 20, 30]
      }
    }]
  };
  const bundlePath = path.join(dir, 'test_bundle.json');
  fs.writeFileSync(bundlePath, JSON.stringify(bundle));
  execFileSync(process.execPath, [
    path.join(REPO, 'scripts/weathergrid_png_prerender.mjs'),
    '--out', path.join(dir, 'png'),
    `region=tw,source=test,bundle=${bundlePath}`
  ], {cwd: REPO});
  const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'png/tw/manifest.json'), 'utf8'));
  assert.equal(manifest.palette_version, palette.PALETTE_VERSION);
  assert.equal(manifest.schema_version, 1);
  assert.equal(manifest.region, 'tw');
  const cloudLayer = manifest.sources.test.layers.total_cloud_percent;
  assert.equal(cloudLayer.covered, true);
  assert.equal(cloudLayer.frames.length, 1);
  assert.equal(cloudLayer.frames[0].file, 'test/total_cloud_percent/f000.png');

  const cloudPng = decodePng(fs.readFileSync(path.join(dir, 'png/tw', cloudLayer.frames[0].file)));
  assert.equal(cloudPng.width, 2);
  assert.equal(cloudPng.height, 2);
  // pixel (0,0) = top-left = north-west = grid row 1 (lat 6), col 0 (105) = value 55
  const px = (img, x, y) => {
    const o = (y * img.width + x) * 4;
    return [img.rgba[o], img.rgba[o + 1], img.rgba[o + 2], img.rgba[o + 3]];
  };
  // value 55 -> hsl(238 78% 50%) -> rgb(28,35,227); alpha = stops(55)=.5925 -> 151
    assert.deepEqual(px(cloudPng, 0, 0), [28, 35, 227, 151]);
  // value 100 (row1 col1) -> hsl(285 48% 82%) rgb(220,187,231), alpha 255
  assert.deepEqual(px(cloudPng, 1, 0), [220, 187, 231, 255]);
  // value 30 (south-west) -> hsl(199 82% 56%) rgb(51,177,235), alpha 56
  assert.deepEqual(px(cloudPng, 0, 1), [51, 177, 235, 56]);
  // null cell -> fully transparent
  assert.deepEqual(px(cloudPng, 1, 1), [0, 0, 0, 0]);

  const visLayer = manifest.sources.test.layers.visibility_km;
  const visPng = decodePng(fs.readFileSync(path.join(dir, 'png/tw', visLayer.frames[0].file)));
  const vpx = (x, y) => {
    const o = (y * visPng.width + x) * 4;
    return [visPng.rgba[o], visPng.rgba[o + 1], visPng.rgba[o + 2], visPng.rgba[o + 3]];
  };
  // visibility 0 (south-west) -> hsl(5 72% 46%) rgb(202,47,33), alpha 255
  assert.deepEqual(vpx(0, 1), [202, 47, 33, 255]);
  // visibility 30 (north-east) -> t=1 -> hue 150 -> rgb(33,202,117), alpha 20
  assert.deepEqual(vpx(1, 0), [33, 202, 117, 20]);
});

test('generator: packed i16gz bundles decode with scale applied', {timeout: 30000}, () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'wg16-'));
  const ints = Int16Array.from([50, -32768, 100, 25]); // cloud values, sentinel = null
  const gz = zlib.gzipSync(Buffer.from(ints.buffer));
  const bundle = {
    schema_version: 1, model: 'TESTP', bundle_encoding: 'i16gz-v1',
    bbox: {leftlon: 105, rightlon: 106, bottomlat: 5, toplat: 6},
    grid: {rows: 2, cols: 2, latitudes: [5, 6], longitudes: [105, 106]},
    fields: {total_cloud_percent: {scale: 1}},
    frames: [{
      forecast_hour: 6, valid_time_utc: '2026-11-03T18:00:00+00:00',
      values: {total_cloud_percent: {enc: 'i16gz', data: gz.toString('base64')}}
    }]
  };
  const bundlePath = path.join(dir, 'packed_bundle.json');
  fs.writeFileSync(bundlePath, JSON.stringify(bundle));
  execFileSync(process.execPath, [
    path.join(REPO, 'scripts/weathergrid_png_prerender.mjs'),
    '--out', path.join(dir, 'png'),
    `region=tw,source=packed,bundle=${bundlePath}`
  ], {cwd: REPO});
  const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'png/tw/manifest.json'), 'utf8'));
  const png = decodePng(fs.readFileSync(path.join(dir, 'png/tw', manifest.sources.packed.layers.total_cloud_percent.frames[0].file)));
  const px = (x, y) => {
    const o = (y * png.width + x) * 4;
    return [png.rgba[o], png.rgba[o + 1], png.rgba[o + 2], png.rgba[o + 3]];
  };
  // north row: [100, 25] -> 100 = last band hsl(285 48% 82%); 25 alpha stops(25)=.17 -> 43
  assert.deepEqual(px(0, 0), [220, 187, 231, 255]);
  assert.deepEqual(px(1, 0), [51, 177, 235, 43]);
  // south row: [50, null] -> 50 = hsl(238 78% 50%) alpha 140; null transparent
  assert.deepEqual(px(0, 1), [28, 35, 227, 140]);
  assert.deepEqual(px(1, 1), [0, 0, 0, 0]);
});