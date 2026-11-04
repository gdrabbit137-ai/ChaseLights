// CL-WG-15: faint flow-arrow overlay on every wind-direction color field
// (10 m + 925/850/700 hPa). Arrows point toward the motion ("吹往"), share the
// wind-speed layer's arrow conventions (windVectorStep sampling, screen-space
// occupancy buckets, meteorological-from flip), and are dimmer/thinner/sparser
// so the direction color field stays the primary reading.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const require_ = createRequire(import.meta.url);
const paletteModule = () => require_(path.join(ROOT, 'assets/weather-map-palette.js'));

function dirSpeedKeyStub(layer = 'wind_direction_10m_deg') {
  const m = /^wind_direction_([0-9]{3})hpa_deg$/.exec(layer);
  return m ? `wind_speed_${m[1]}hpa_m_s` : 'wind_speed_10m_m_s';
}

function grab(startMarker, endMarker) {
  const a = JS.indexOf(startMarker);
  assert.ok(a >= 0, `start marker not found: ${startMarker}`);
  const b = JS.indexOf(endMarker, a);
  assert.ok(b > a, `end marker not found: ${endMarker}`);
  return JS.slice(a, b);
}

test('all four wind-direction layers are covered by the direction-layer predicate', () => {
  assert.match(JS, /function isWindDirectionLayer\(layer=state\.layer\)\{/);
  const body = grab('function isWindDirectionLayer', 'function windDirectionSpeedKey');
  assert.match(body, /\/\^wind_direction_\(10m\|\[0-9\]\{3\}hpa\)_deg\$\//);
  // The predicate must match every layerConfig direction entry's key shape.
  const cfgKeys = [...JS.matchAll(/layerConfig\['(wind_direction_(?:10m|[0-9]{3}hpa)_deg)'\]=\{label/g)].map(m => m[1]);
  assert.equal(cfgKeys.length, 4, 'layerConfig declares exactly four wind-direction layers');
  assert.equal(cfgKeys.filter(k => k.endsWith('hpa_deg')).length, 3,
    '925/850/700 hPa pressure-level direction layers all exist');
});

test('each direction layer resolves its own pressure-level speed field, with a 10 m fallback', () => {
  const src = grab('function windDirectionSpeedKey', 'function syncWindVectorDefault');
  const fn = new Function(`${src}
    return windDirectionSpeedKey;`)();
  assert.equal(fn('wind_direction_10m_deg'), 'wind_speed_10m_m_s');
  assert.equal(fn('wind_direction_925hpa_deg'), 'wind_speed_925hpa_m_s');
  assert.equal(fn('wind_direction_850hpa_deg'), 'wind_speed_850hpa_m_s');
  assert.equal(fn('wind_direction_700hpa_deg'), 'wind_speed_700hpa_m_s');
  assert.equal(fn('wind_speed_10m_m_s'), 'wind_speed_10m_m_s', 'non-direction layers fall back safely');
});

test('the arrow overlay is drawn on direction layers and shares the speed-layer conventions', () => {
  assert.match(JS, /function drawDirectionFlowArrows\(\)\{/, 'dedicated faint-arrow overlay exists');
  assert.match(JS, /if\(isWindDirectionLayer\(\)\) drawDirectionFlowArrows\(\);/,
    'drawWindVectors always draws the overlay on direction layers');
  assert.match(JS, /const toward=\(\(direction\+180\)%360\)\*Math\.PI\/180;/,
    'arrows point toward the motion, matching the speed-layer vector math');
  assert.match(JS, /strokeWindArrow\(sx,sy,ex,ey,/, 'reuses the shared strokeWindArrow renderer');
  assert.match(JS, /const step=windVectorStep\(\);/,
    'overlay sampling reuses the zoom-aware windVectorStep grid');
  assert.match(JS, /occupiedArrowCells\.has\(bucketKey\)/,
    'screen-space occupancy buckets prevent arrow pileup');
});

test('overlay arrows are fainter, thinner and sparser than the wind-speed layer vectors', () => {
  assert.match(JS, /const minVectorSpacingPx=compactUi\?30:34;/, 'speed-layer spacing unchanged');
  assert.match(JS, /const minArrowSpacingPx=compactUi\?36:40;/,
    'overlay spacing is sparser than the speed layer on both UIs');
  assert.match(JS, /'rgba\(2,6,23,\.45\)'/, 'overlay under-stroke is dimmer than the speed layer (.72)');
  assert.match(JS, /'rgba\(241,245,249,\.68\)'/, 'overlay highlight is dimmer than the speed layer (.94)');
  assert.match(JS, /compactUi\?2\.4:3\)/, 'overlay stroke is thinner than the speed layer (3.5/4.5)');
});

test('direction-only data still draws arrows (no speed magnitude required)', () => {
  const src = grab('function drawDirectionFlowArrows', 'function drawGrid');
  assert.match(src, /const usableSpeeds=\(speeds && speeds\.length===rows\*cols\) \? speeds : null;/,
    'speed arrays from a different grid are rejected');
  assert.match(src, /if\(usableSpeeds && \(!Number\.isFinite\(speed\) \|\| speed<0\.5\)\) continue;/,
    'speed is only a gate when the same-grid speed field exists');
  assert.match(src, /const speedScale=\(Number\.isFinite\(speed\)\?speed:10\)\/20;/,
    'without speed the arrow falls back to a fixed length from the angle alone');
});

test('legend keeps the color wheel and gains the arrow key on direction layers; panel explains the overlay', () => {
  assert.match(JS, /const windKey=\(state\.windVectors \|\| isWindLayer\(\) \|\| isWindDirectionLayer\(\)\)/,
    'arrow key shows on every wind-direction layer');
  assert.match(JS, /箭頭指示氣流吹往方向（疊加於風向色場之上）/,
    '「目前圖層」detail panel carries the arrow-direction note');
  assert.match(JS, /箭頭＝風去向/, 'existing legend wording preserved');
  // QC/legend color wheel untouched: direction palette + compass labels stay.
  assert.match(JS, /layerConfig\['wind_direction_10m_deg'\]=\{label:'10 m 風向',\.\.\.window\.WeatherMapPalette\.LAYER_RENDER_CONFIG\['wind_direction_10m_deg'\]\}/);
  // The palette/domain fields live in the shared render config (CL-WG-16).
  assert.equal(paletteModule().LAYER_RENDER_CONFIG.wind_direction_10m_deg.domain[1], 360);
});

test('extracted overlay loop: sampling, occupancy, mobile density and arrow direction', () => {
  const src = grab('function drawDirectionFlowArrows', 'function drawGrid');
  const strokes = [];
  const harness = {
    compact: false,
    grid: {
      rows: 4, cols: 4,
      latitudes: [26, 25.5, 25, 24.5],
      longitudes: [120, 120.9, 121.8, 122.7]
    },
    directions: Array(16).fill(90)
  };
  const stubs = {
    state: { layer: 'wind_direction_10m_deg', lastWindVectorCount: 0 },
    ctx: {
      save(){}, restore(){}, lineCap:'', lineJoin:''
    },
    activeDataset(){ return { fields: { wind_direction_10m_deg: {} }, grid: harness.grid }; },
    decodedArray(){ return harness.directions.slice(); },
    renderViewBbox(){ return { leftlon: 119, rightlon: 123, bottomlat: 24, toplat: 26.5 }; },
    windVectorStep(){ return 1; },
    project(lon, lat){ return { x: (lon - 120) * 100, y: (26 - lat) * 100 }; },
    strokeWindArrow(sx, sy, ex, ey, stroke, width){ strokes.push({ sx, sy, ex, ey, stroke, width }); },
    windDirectionSpeedKey: dirSpeedKeyStub,
    window: { matchMedia(){ return { matches: harness.compact }; } },
    Number, Math
  };
  const keys = Object.keys(stubs);
  const fn = new Function(...keys, `${src}\nreturn { run: drawDirectionFlowArrows };`)(
    ...keys.map(k => stubs[k]));
  fn.run();
  // step=1, lon spacing 0.9° -> 90 px apart, all inside 40 px buckets: 16 arrows.
  assert.equal(strokes.length, 32, 'desktop, sparse grid: every sampled cell draws (2 strokes per arrow)');
  assert.equal(stubs.state.lastWindVectorCount, 16, 'overlay counts drawn arrows');
  // direction 90° = wind FROM east -> arrow points WEST (toward=270°): ex < sx.
  const first = strokes[0];
  assert.ok(first.ex < first.sx, 'arrow points toward the motion (west for a from-east wind)');
  // Under-stroke is the faint dark color, highlight the dim light one.
  assert.equal(first.stroke, 'rgba(2,6,23,.45)');
  assert.equal(strokes[1].stroke, 'rgba(241,245,249,.68)');
  assert.equal(first.width, 3, 'desktop under-stroke width');
  assert.equal(strokes[1].width, 1.4, 'desktop highlight width');

  // Mobile: denser buckets (36 px), thinner strokes.
  harness.compact = true;
  strokes.length = 0;
  stubs.state.lastWindVectorCount = 0;
  fn.run();
  assert.equal(strokes.length, 32, 'mobile still draws one arrow per sample (grid too sparse to collide)');
  assert.equal(strokes[0].width, 2.4, 'mobile under-stroke is thinner');
  assert.equal(strokes[1].width, 1.1, 'mobile highlight is thinner');

  // Occupancy: dense grid (lon 0.15° = 15 px apart, lat 0.15° = 15 px apart)
  // collapses to one arrow per occupied bucket: cols 0-2 share a bucket, col 3
  // opens a new one; both rows share bucketY -> 2 buckets x 1 row-pair = 2... no:
  // row bucketY(15px)=0 for both rows, so 2 arrows total per row-bucket pair.
  harness.compact = false;
  strokes.length = 0;
  stubs.state.lastWindVectorCount = 0;
  harness.grid = {
    rows: 2, cols: 4,
    latitudes: [26, 25.85],
    longitudes: [120, 120.15, 120.3, 120.45]
  };
  harness.directions = Array(8).fill(90);
  fn.run();
  assert.equal(stubs.state.lastWindVectorCount, 2,
    '15 px spacing < 40 px bucket: cols 0-2 share a bucket, col 3 opens a new one; rows share a bucketY');
});

test('direction-only fallback path draws arrows without any speed field', () => {
  const src = grab('function drawDirectionFlowArrows', 'function drawGrid');
  const strokes = [];
  const stubs = {
    state: { layer: 'wind_direction_925hpa_deg', lastWindVectorCount: 0 },
    ctx: { save(){}, restore(){}, lineCap:'', lineJoin:'' },
    activeDataset(){ return { fields: { wind_direction_925hpa_deg: {} }, grid: {
      rows: 1, cols: 1, latitudes: [30], longitudes: [140]
    } }; },
    decodedArray(){ return [0]; },
    renderViewBbox(){ return { leftlon: 139, rightlon: 141, bottomlat: 29, toplat: 31 }; },
    windVectorStep(){ return 1; },
    project(lon, lat){ return { x: 50, y: 50 }; },
    strokeWindArrow(sx, sy, ex, ey, stroke, width){ strokes.push({ sx, sy, ex, ey }); },
    windDirectionSpeedKey: dirSpeedKeyStub,
    window: { matchMedia(){ return { matches: false }; } },
    Number, Math
  };
  const keys = Object.keys(stubs);
  const fn = new Function(...keys, `${src}\nreturn drawDirectionFlowArrows;`)(
    ...keys.map(k => stubs[k]));
  fn();
  assert.equal(strokes.length, 2, 'angle-only layer still renders the overlay arrow');
  assert.ok(strokes[0].ey > strokes[0].sy, 'wind from north (0°) -> arrow points SOUTH (+y)');
});