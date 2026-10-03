import maplibregl from 'https://unpkg.com/maplibre-gl@6.11.2/dist/maplibre-gl.mjs';

const API = {
  jma: {
    url: 'https://api.open-meteo.com/v1/jma',
    label: 'JMA Best Match · MSM/GSM',
    detail: 'JMA endpoint; Auto 僅在 MSM 原生區域內優先使用',
  },
  gfs: {
    url: 'https://api.open-meteo.com/v1/gfs',
    label: 'NCEP Best Match · GFS/HRRR',
    detail: 'NCEP endpoint; 全球 fallback',
  },
};

const MSM_DOMAIN = { w: 120.0, s: 22.4, e: 150.0, n: 47.6 };
const FIELDS = {
  cloud_cover_low: { label: '低雲', unit: '%' },
  cloud_cover_mid: { label: '中雲', unit: '%' },
  cloud_cover_high: { label: '高雲', unit: '%' },
  visibility: { label: '能見度', unit: 'km' },
  precipitation: { label: '降水', unit: 'mm' },
  wind_speed_10m: { label: '10m 風速', unit: 'm/s' },
};
const HOURLY = Object.keys(FIELDS).join(',');
const $ = (id) => document.getElementById(id);
const canvas = $('overlay');
const ctx = canvas.getContext('2d');
const state = {
  samples: [],
  coverage: null,
  provider: null,
  cache: new Map(),
  timer: null,
  aborter: null,
  requestSerial: 0,
  sampleDx: 0,
  sampleDy: 0,
  validTime: null,
};

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://tiles.openfreemap.org/styles/liberty',
  center: [121.0, 23.7],
  zoom: 6,
  renderWorldCopies: false,
});
map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
function view() {
  const b = map.getBounds();
  return {
    w: clamp(b.getWest(), -180, 180),
    s: clamp(b.getSouth(), -80, 80),
    e: clamp(b.getEast(), -180, 180),
    n: clamp(b.getNorth(), -80, 80),
  };
}
function expand(b, factor = 0.45) {
  const dx = Math.max(0.3, (b.e - b.w) * factor);
  const dy = Math.max(0.25, (b.n - b.s) * factor);
  return {
    w: clamp(b.w - dx, -180, 180),
    s: clamp(b.s - dy, -80, 80),
    e: clamp(b.e + dx, -180, 180),
    n: clamp(b.n + dy, -80, 80),
  };
}
function contains(a, b) {
  return !!(a && b && a.w <= b.w && a.e >= b.e && a.s <= b.s && a.n >= b.n);
}
function fmt(b) {
  return b ? [b.w, b.s, b.e, b.n].map((v) => Number(v).toFixed(2)).join(', ') : '—';
}
function bboxKey(provider, b) {
  return provider + ':' + [b.w, b.s, b.e, b.n].map((v) => Number(v).toFixed(1)).join(':');
}
function autoProvider(b) {
  return contains(MSM_DOMAIN, b) ? 'jma' : 'gfs';
}
function selectedProvider(b) {
  const selected = $('provider').value;
  if (selected === 'auto') return autoProvider(b);
  if (selected === 'jma' && !contains(MSM_DOMAIN, b)) return null;
  return selected;
}
function gridShape() {
  const z = map.getZoom();
  if (z >= 7.5) return { cols: 8, rows: 7 };
  if (z >= 5.0) return { cols: 7, rows: 6 };
  return { cols: 6, rows: 5 };
}
function sampleGrid(b) {
  const shape = gridShape();
  const dx = (b.e - b.w) / Math.max(1, shape.cols - 1);
  const dy = (b.n - b.s) / Math.max(1, shape.rows - 1);
  const points = [];
  for (let r = 0; r < shape.rows; r += 1) {
    const lat = b.s + dy * r;
    for (let c = 0; c < shape.cols; c += 1) {
      points.push({ lat, lon: b.w + dx * c });
    }
  }
  return { points, dx, dy };
}
function cacheFind(provider, v) {
  const now = Date.now();
  for (const [key, item] of state.cache) {
    if (item.provider !== provider || now - item.fetchedAt > 15 * 60 * 1000) continue;
    if (contains(item.coverage, v)) {
      state.cache.delete(key);
      state.cache.set(key, item);
      return item;
    }
  }
  return null;
}
function cachePut(key, item) {
  state.cache.set(key, item);
  while (state.cache.size > 12) state.cache.delete(state.cache.keys().next().value);
}
function colorFor(field, value) {
  if (value == null || Number.isNaN(Number(value))) return 'rgba(0,0,0,0)';
  const v = Number(value);
  if (field.startsWith('cloud_cover_')) {
    const a = 0.12 + clamp(v / 100, 0, 1) * 0.7;
    return 'rgba(220,235,255,' + a.toFixed(3) + ')';
  }
  if (field === 'visibility') {
    const t = clamp(v / 40, 0, 1);
    return 'rgba(' + Math.round(235 - 110 * t) + ',' + Math.round(150 + 80 * t) + ',150,0.62)';
  }
  if (field === 'precipitation') {
    const a = 0.18 + clamp(v / 8, 0, 1) * 0.72;
    return 'rgba(60,145,255,' + a.toFixed(3) + ')';
  }
  const a = 0.2 + clamp(v / 15, 0, 1) * 0.65;
  return 'rgba(185,105,235,' + a.toFixed(3) + ')';
}
function displayValue(field, raw) {
  if (raw == null) return null;
  if (field === 'visibility') return Number(raw) / 1000;
  return Number(raw);
}
function draw() {
  const rect = canvas.getBoundingClientRect();
  ctx.clearRect(0, 0, rect.width, rect.height);
  if (!state.samples.length) return;
  const field = $('layer').value;
  const dx = Math.max(0.02, state.sampleDx);
  const dy = Math.max(0.02, state.sampleDy);
  for (const sample of state.samples) {
    const value = displayValue(field, sample.values[field]);
    if (value == null) continue;
    const nw = map.project([sample.lon - dx / 2, sample.lat + dy / 2]);
    const se = map.project([sample.lon + dx / 2, sample.lat - dy / 2]);
    const x = Math.min(nw.x, se.x);
    const y = Math.min(nw.y, se.y);
    const w = Math.max(7, Math.abs(se.x - nw.x) + 1);
    const h = Math.max(7, Math.abs(se.y - nw.y) + 1);
    ctx.fillStyle = colorFor(field, value);
    ctx.fillRect(x, y, w, h);
  }
  $('legend').textContent = FIELDS[field].label + ' · ' + FIELDS[field].unit + ' · sampled viewport prototype';
}
function resize() {
  const r = canvas.getBoundingClientRect();
  const d = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.round(r.width * d));
  canvas.height = Math.max(1, Math.round(r.height * d));
  ctx.setTransform(d, 0, 0, d, 0, 0);
  draw();
}
function buildUrl(provider, grid) {
  const cfg = API[provider];
  const latitudes = grid.points.map((p) => p.lat.toFixed(4)).join(',');
  const longitudes = grid.points.map((p) => p.lon.toFixed(4)).join(',');
  const params = new URLSearchParams({
    latitude: latitudes,
    longitude: longitudes,
    hourly: HOURLY,
    forecast_hours: '1',
    timezone: 'GMT',
    wind_speed_unit: 'ms',
    cell_selection: 'nearest',
    elevation: 'nan',
  });
  return cfg.url + '?' + params.toString();
}
function normalizeResponse(payload, requested) {
  const rows = Array.isArray(payload) ? payload : [payload];
  if (rows.length !== requested.length) throw new Error('location count mismatch');
  return rows.map((row, i) => {
    const hourly = row.hourly || {};
    const values = {};
    for (const field of Object.keys(FIELDS)) {
      const series = hourly[field] || [];
      values[field] = series.length ? series[0] : null;
    }
    return { lat: requested[i].lat, lon: requested[i].lon, values, time: (hourly.time || [])[0] || null };
  });
}
function applyDataset(item, cacheStatus) {
  state.samples = item.samples;
  state.coverage = item.coverage;
  state.provider = item.provider;
  state.sampleDx = item.dx;
  state.sampleDy = item.dy;
  state.validTime = item.validTime;
  $('coverage').textContent = 'loaded coverage: ' + fmt(item.coverage);
  $('cache').textContent = 'request cache: ' + state.cache.size + ' · ' + cacheStatus;
  $('source').textContent = API[item.provider].label + ' · ' + API[item.provider].detail;
  $('time').textContent = 'valid time: ' + (item.validTime || '—');
  $('status').textContent = '資料已就緒 · ' + item.samples.length + ' samples';
  draw();
}
async function fetchCoverage(provider, coverage, currentView) {
  const serial = ++state.requestSerial;
  if (state.aborter) state.aborter.abort();
  state.aborter = new AbortController();
  const grid = sampleGrid(coverage);
  const url = buildUrl(provider, grid);
  $('status').textContent = '補抓 ' + API[provider].label + ' · ' + grid.points.length + ' samples…';
  const response = await fetch(url, { signal: state.aborter.signal, cache: 'no-store' });
  if (!response.ok) throw new Error('HTTP ' + response.status);
  const payload = await response.json();
  if (serial !== state.requestSerial) return;
  const samples = normalizeResponse(payload, grid.points);
  const item = {
    provider,
    coverage,
    samples,
    dx: grid.dx,
    dy: grid.dy,
    validTime: samples.find((s) => s.time)?.time || null,
    fetchedAt: Date.now(),
  };
  cachePut(bboxKey(provider, coverage), item);
  applyDataset(item, contains(coverage, currentView) ? 'network-fill' : 'prefetch');
}
async function updateForViewport(force = false) {
  const v = view();
  const prefetch = expand(v);
  $('viewport').textContent = 'viewport: ' + fmt(v);
  $('prefetch').textContent = 'prefetch ring: ' + fmt(prefetch);
  const provider = selectedProvider(prefetch);
  if (!provider) {
    $('status').textContent = 'JMA MSM prototype 僅限約 120–150°E / 22.4–47.6°N；請切回 Auto 或 GFS';
    return;
  }
  $('resolved-provider').textContent = 'resolved: ' + API[provider].label;
  if (!force) {
    const hit = cacheFind(provider, v);
    if (hit) {
      applyDataset(hit, 'viewport-hit');
      return;
    }
  }
  await fetchCoverage(provider, prefetch, v);
}
function schedule(force = false) {
  clearTimeout(state.timer);
  state.timer = setTimeout(() => {
    updateForViewport(force).catch((error) => {
      if (error.name === 'AbortError') return;
      $('status').textContent = '資料補抓失敗 · ' + error.message;
    });
  }, force ? 0 : 320);
}
function gotoPreset(name) {
  const presets = {
    tw: { center: [121.0, 23.7], zoom: 6.0 },
    jp: { center: [138.0, 36.0], zoom: 5.0 },
    us: { center: [-119.5, 38.5], zoom: 4.2 },
  };
  const p = presets[name];
  map.jumpTo({ center: p.center, zoom: p.zoom });
  schedule(true);
}

map.on('load', () => { resize(); schedule(true); });
map.on('move', draw);
map.on('moveend', () => schedule(false));
map.on('resize', resize);
$('provider').addEventListener('change', () => schedule(true));
$('layer').addEventListener('change', draw);
$('refresh').addEventListener('click', () => schedule(true));
document.querySelectorAll('[data-preset]').forEach((button) => {
  button.addEventListener('click', () => gotoPreset(button.dataset.preset));
});
window.addEventListener('resize', resize);
