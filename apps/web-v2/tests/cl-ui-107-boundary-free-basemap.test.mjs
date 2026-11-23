// CL-UI-107: 行政邊界虛線「全面」移除（防回歸）。
// Owner 實測：台灣周邊中國沿海/省份虛線在 OpenFreeMap 圖磚上又出現——
// CL-WG-25 只修了 line 型別 + /^boundary|boundary|disputed/ id 命名，屬
// 白名單式比對，圖磚樣式只要換 id 命名或用非 line 型別就漏網。
// Contract:
//  (1) hideBoundaryLineLayers 比對必須涵蓋 id 與 source-layer 的
//      boundary/disputed/admin（不限圖層型別），且對已 visibility:none 的
//      圖層冪等跳過（styledata 重入不得迴圈）。
//  (2) 套用時機：basemap 'load' 之後「以及」任何 'styledata' 之後。
//  (3) 真瀏覽器斷言（lazy-boot headless Chrome + 線上 OpenFreeMap 樣式）：
//      五個雲量圖資來源（gfs/icon/cwa/jma/himawari）逐一驅動 model-select，
//      每次斷言 map.getStyle() 內不含任何「可見」的 boundary 類圖層，且樣式
//      確實帶有 boundary 類圖層（避免斷言因樣式缺席而空轉）。
//  (4) 頂部「若此網頁未如預期顯示…減少隱私保護措施」提示條為 iPhone Safari
//      ITP 瀏覽器內建提示（站外元素）：站內不得有任何同類提示文案。
// Run: node --test apps/web-v2/tests/cl-ui-107-boundary-free-basemap.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';

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
// 1. Matcher breadth + idempotency (extracted-function harness, offline)
// ---------------------------------------------------------------------------
function buildHideFn() {
  const src = grab(MAP_JS, 'function hideBoundaryLineLayers', 'function renderViewBbox');
  return new Function(`${src}\nreturn hideBoundaryLineLayers;`)();
}
function buildBoundaryFake(layers) {
  const hidden = [];
  return {
    hidden,
    getStyle: () => ({ layers }),
    setLayoutProperty: (id, prop, val) => hidden.push([id, prop, val])
  };
}

test('CL-UI-107: every boundary/admin/disputed-class layer is hidden — id match, any type', () => {
  const layers = [
    { id: 'boundary_3', type: 'line', 'source-layer': 'boundary' },
    { id: 'boundary_2', type: 'line', 'source-layer': 'boundary' },
    { id: 'boundary_disputed', type: 'line', 'source-layer': 'boundary' },
    // 漏網形狀：非 line 型別 + 非慣用 id 命名（CL-WG-25 白名單會放過的）
    { id: 'admin_borders_fill', type: 'fill' },
    { id: 'admin1_fringe', type: 'symbol' },
    { id: ' disputed_zone_dash', type: 'background' }
  ];
  const fake = buildBoundaryFake(layers);
  const n = buildHideFn()(fake);
  assert.equal(n, 6, 'all six boundary-class layers hidden regardless of type');
  assert.deepEqual(fake.hidden.map(h => h[0]), [
    'boundary_3', 'boundary_2', 'boundary_disputed',
    'admin_borders_fill', 'admin1_fringe', ' disputed_zone_dash'
  ]);
});

test('CL-UI-107: source-layer match catches layers whose id does not say boundary', () => {
  const layers = [
    { id: 'country_fringe_dash', type: 'line', 'source-layer': 'boundary' },
    { id: 'province_overlay', type: 'fill', 'source-layer': 'admin_areas' },
    { id: 'road_minor', type: 'line', 'source-layer': 'transportation' },
    { id: 'place_city', type: 'symbol', 'source-layer': 'place' },
    { id: 'water', type: 'fill', 'source-layer': 'water' },
    { id: 'contour_lines', type: 'line' }
  ];
  const fake = buildBoundaryFake(layers);
  const n = buildHideFn()(fake);
  assert.deepEqual(fake.hidden.map(h => h[0]),
    ['country_fringe_dash', 'province_overlay'],
    'only boundary/admin source-layers; roads/labels/water/terrain untouched');
});

test('CL-UI-107: idempotent — layers already visibility:none are skipped (styledata re-entry safe)', () => {
  const layers = [
    { id: 'boundary_2', type: 'line', 'source-layer': 'boundary', layout: { visibility: 'none' } },
    { id: 'boundary_3', type: 'line', 'source-layer': 'boundary' }
  ];
  const fake = buildBoundaryFake(layers);
  const n = buildHideFn()(fake);
  assert.equal(n, 1, 'only the still-visible boundary layer is mutated');
  assert.deepEqual(fake.hidden.map(h => h[0]), ['boundary_3']);
});

test('CL-UI-107: fail-open on unknown style shape — no throw, nothing hidden', () => {
  const fn = buildHideFn();
  assert.doesNotThrow(() => fn(buildBoundaryFake(null)));
  assert.doesNotThrow(() => fn(buildBoundaryFake(undefined)));
  const bad = { getStyle: () => { throw new Error('no style'); }, setLayoutProperty() {} };
  assert.doesNotThrow(() => fn(bad));
  assert.equal(fn({ getStyle: () => ({ layers: [] }), setLayoutProperty() {} }), 0);
});

// ---------------------------------------------------------------------------
// 2. Wiring: applied on 'load' AND re-applied on every 'styledata'
// ---------------------------------------------------------------------------
test('CL-UI-107: hide runs on load AND on styledata (late style mutations covered)', () => {
  const loadBlock = grab(MAP_JS, "map.on('load'", "map.on('move'");
  assert.ok(loadBlock.includes('hideBoundaryLineLayers(map)'),
    'load handler must apply the boundary hide');
  assert.ok(loadBlock.includes("map.on('styledata'"),
    'styledata handler must exist right after the load handler');
  const styleBlock = grab(MAP_JS, "map.on('styledata'", "map.on('move'");
  assert.ok(styleBlock.includes('hideBoundaryLineLayers(map)'),
    'styledata handler re-applies the boundary hide');
});

test('CL-UI-107: weather-map.html stamps bumped to bclwg49 in weather-map.html', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg50/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg49/);
  assert.ok(!/weather-map\.js\?v=bclwg42/.test(WG_HTML), 'old js stamp must not linger');
});

// ---------------------------------------------------------------------------
// 3. In-page ITP-banner lookalike is banned (item 3 of the ticket: the
//    「若此網頁未如預期顯示…」bar is iPhone Safari's own ITP banner, not ours)
// ---------------------------------------------------------------------------
test('CL-UI-107: no in-page privacy-protection banner copy in the weather-map page assets', () => {
  const CSS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.css'), 'utf8');
  for (const [name, src] of [['weather-map.html', WG_HTML], ['weather-map.js', MAP_JS], ['weather-map.css', CSS]]) {
    assert.ok(!/未如預期|隱私保護|Privacy Report|prevent cross-site tracking/i.test(src),
      `${name} must not render a lookalike of the Safari ITP banner`);
  }
});

// ---------------------------------------------------------------------------
// 4. Live headless assertion — five model layers, one by one (lazy boot)
// ---------------------------------------------------------------------------
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs, ready;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

async function bootBrowser() {
  if (ready) return ready;
  ready = (async () => {
    const MIME = {'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml'};
    server = createServer((req, res) => {
      const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
      const file = path.join(ROOT, p === '/' ? 'weather-map.html' : p.slice(1));
      try { const body = fs.readFileSync(file);
        res.writeHead(200, {'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
        res.end(body);
      } catch { res.writeHead(404); res.end('not found'); }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    baseURL = `http://127.0.0.1:${server.address().port}/`;
    chrome = spawn(BROWSER, [
      '--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
      // CL-UI-109: newer Chrome headless needs software WebGL for the MapLibre LIVE probes
      '--enable-unsafe-swiftshader','--use-angle=swiftshader',
      '--no-first-run','--remote-debugging-port=0',
      '--window-size=390,844',
      '--user-data-dir=' + fs.mkdtempSync(path.join(require('node:os').tmpdir(), 'clui107-')), 'about:blank'],
      {stdio: ['ignore','ignore','pipe']});
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = '';
      const t = setTimeout(() => reject(new Error('no devtools endpoint')), 60000);
      chrome.stderr.on('data', d => { buf += d;
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearTimeout(t); resolve(m[1]); } });
      chrome.on('error', e => reject(new Error('spawn: ' + e.message)));
    });
    const dbgHost = wsUrl.match(/ws:\/\/([^/]+)/)[1];
    let targets = [];
    for (let i = 0; i < 40; ++i) {
      targets = await (await fetch(`http://${dbgHost}/json/list`)).json();
      if (targets.some(t => t.type === 'page')) break;
      await new Promise(r => setTimeout(r, 250));
    }
    ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
    await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
    ws.onmessage = e => { const m = JSON.parse(e.data);
      if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
    send = (method, params = {}) => new Promise((resolve, reject) => {
      const i = nextId(); pending.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
      ws.send(JSON.stringify({id: i, method, params}));
    });
    evaljs = async (expr) => {
      const r = await send('Runtime.evaluate', {expression: expr, returnByValue: true, awaitPromise: true});
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
      return r.result?.result?.value ?? r.result?.value;
    };
  })().catch(e => { ready = null; throw e; });
  return ready;
}

function teardownBrowser() {
  return Promise.all([
    (async () => { try { ws?.close(); } catch {} })(),
    (async () => { try { chrome?.kill(); } catch {} })(),
    (async () => { try { await new Promise(r => server?.close(r)); } catch {} })()
  ]);
}

const FIVE_MODES = ['gfs', 'icon', 'cwa', 'jma', 'himawari'];
const BOUNDARY_PROBE = `(() => {
  const map = window.__weatherGridMap;
  if (!map || !map.getStyle) return { ready: false };
  const layers = (map.getStyle() || {}).layers || [];
  const boundaryClass = layers.filter(l =>
    /boundary|disputed|admin/i.test(String(l.id || ''))
    || String(l['source-layer'] || '') === 'boundary'
    || /boundary|admin/i.test(String(l['source-layer'] || '')));
  const visible = boundaryClass.filter(l => ((l.layout || {}).visibility) !== 'none');
  return { ready: true, boundaryCount: boundaryClass.length, visibleIds: visible.map(l => l.id) };
})()`;

test('CL-UI-107 LIVE: five model layers each render a boundary-free basemap', { timeout: 240000 }, async t => {
  await bootBrowser();
  t.after(() => teardownBrowser());
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', {width: 390, height: 844, deviceScaleFactor: 1, mobile: true});
  await send('Page.navigate', {url: baseURL + '?spot='});
  // wait for the MapLibre basemap to be live (network-dependent)
  let probe = { ready: false };
  for (let i = 0; i < 60 && !probe.ready; ++i) {
    await new Promise(r => setTimeout(r, 1000));
    probe = await evaljs(BOUNDARY_PROBE);
  }
  assert.ok(probe.ready, 'MapLibre basemap must boot within the wait window');
  assert.ok(probe.boundaryCount > 0,
    'the live OpenFreeMap style must actually carry boundary-class layers, or this test is vacuous');
  assert.deepEqual(probe.visibleIds, [], `default mode must show no boundary layers (got ${probe.visibleIds})`);

  for (const mode of FIVE_MODES) {
    await evaljs(`(() => {
      const sel = document.getElementById('model-select');
      sel.value = ${JSON.stringify(mode)};
      sel.dispatchEvent(new Event('change', {bubbles: true}));
      return sel.value;
    })()`);
    await new Promise(r => setTimeout(r, 1500));
    const p = await evaljs(BOUNDARY_PROBE);
    assert.ok(p.ready, `${mode}: basemap still live after switch`);
    assert.ok(p.boundaryCount > 0, `${mode}: style still carries boundary-class layers (non-vacuous)`);
    assert.deepEqual(p.visibleIds, [], `${mode}: no visible boundary-class layers`);
  }
});


// CL-CI-40: release the browser, the CDP socket and the static server even when a
// test aborts or fails. Without a file-level hook the old "teardown" TEST only ran
// if every earlier test completed, so one hang left a Chrome process behind and the
// runner eventually reported the remaining cases as `cancelled` (OOM).
test.after(async () => {
  try { await teardownBrowser(); } catch (_) { /* already gone */ }
});
