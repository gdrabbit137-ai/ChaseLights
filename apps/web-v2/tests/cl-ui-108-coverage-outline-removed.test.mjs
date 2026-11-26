// CL-UI-108: 資料來源範圍虛線（coverage outline）移除（owner 實測回報）。
// 台灣周邊仍有一圈淡藍虛線——不是行政邊界（CL-UI-107 已修），是自家 canvas
// 繪製的「目前資料來源涵蓋範圍」輪廓（drawProviderBoundary，圖例曾註記
// 「虛線＝目前資料來源範圍」）。使用者不需要，預設不繪製。
// Contract:
//  (1) drawProviderBoundary 嚴格閘門：state.showCoverageOutline 為 false
//      （預設）時是 no-op，任何模型／圖層都不再畫範圍虛線。
//  (2) 圖例註記「虛線＝目前資料來源範圍」（.coverage-outline-key）自
//      updateLegend、字典（en/ja）與 CSS 一併移除。
//  (3) ⓘ 資料彈出保留一個「預設關閉」的顯示選項（data-info-coverage-toggle，
//      三語文案 wm_cov_outline），勾選即重繪——除錯 regional bbox 仍可用。
//  (4) 真瀏覽器 LIVE 斷言（lazy-boot headless Chrome）：五個模型
//      （gfs/icon/cwa/jma/himawari）逐一：預設旗標 off、畫布上無範圍虛線
//      像素、開關 A/B（ON 畫布改變 → OFF 畫布逐位元組復原）、圖例 DOM 無註記。
// Run: node --test apps/web-v2/tests/cl-ui-108-coverage-outline-removed.test.mjs
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
const MAP_CSS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.css'), 'utf8');
const WG_HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

function grab(src, start, end) {
  const a = src.indexOf(start);
  assert.ok(a !== -1, `source slice start not found: ${start}`);
  const b = src.indexOf(end, a);
  assert.ok(b !== -1, `source slice end not found: ${end}`);
  return src.slice(a, b);
}

// ---------------------------------------------------------------------------
// 1. drawProviderBoundary is strictly gated (extracted-function harness)
// ---------------------------------------------------------------------------
function buildDrawBoundary() {
  const src = grab(MAP_JS, 'function drawProviderBoundary(', 'function draw(){');
  return new Function('state', 'ctx', 'project', 'normalizeViewBbox',
    `${src}\nreturn drawProviderBoundary;`);
}
function fakeCtx() {
  const rec = { strokes: 0, dashes: null, saves: 0 };
  const ctx = {
    save() { rec.saves++; }, restore() {},
    beginPath() {}, closePath() {}, moveTo() {}, lineTo() {},
    set fillStyle(v) {}, set strokeStyle(v) {}, set lineWidth(v) {},
    setLineDash(d) { rec.dashes = d; },
    stroke() { rec.strokes++; }
  };
  return { ctx, rec };
}
const BBOX = { leftlon: 0, toplat: 1, rightlon: 1, bottomlat: 0 };

test('CL-UI-108: drawProviderBoundary is a strict no-op by default (flag off)', () => {
  const fn = buildDrawBoundary();
  const { ctx, rec } = fakeCtx();
  fn({ showCoverageOutline: false }, ctx, () => ({ x: 0, y: 0 }), () => BBOX)({ bbox: BBOX });
  assert.equal(rec.strokes, 0, 'default render must not draw the coverage outline at all');
  assert.equal(rec.saves, 0, 'not even a ctx.save()/restore() pair may run');
});

test('CL-UI-108: opt-in flag draws the dashed coverage box (debug path preserved)', () => {
  const fn = buildDrawBoundary();
  const { ctx, rec } = fakeCtx();
  fn({ showCoverageOutline: true }, ctx, () => ({ x: 1, y: 2 }), () => BBOX)({ bbox: BBOX });
  assert.equal(rec.strokes, 1, 'opt-in still draws the outline once');
  assert.deepEqual(rec.dashes, [6, 5], 'the debug outline keeps its dashed style');
  assert.equal(rec.saves, 1);
});

test('CL-UI-108: state default is showCoverageOutline:false (not drawn anywhere by default)', () => {
  assert.match(MAP_JS, /showCoverageOutline:false/,
    'the state flag must default to OFF');
  assert.match(MAP_JS, /if\(!state\.showCoverageOutline\) return;/,
    'drawProviderBoundary must hard-return before any drawing when off');
  assert.equal((MAP_JS.match(/rgba\(125,211,252,\.52\)/g) || []).length, 1,
    'the outline stroke color survives only inside the gated function');
});

// ---------------------------------------------------------------------------
// 2. The legend note 虛線＝目前資料來源範圍 is removed everywhere
// ---------------------------------------------------------------------------
test('CL-UI-108: legend note + .coverage-outline-key removed from js/css (dict entries too)', () => {
  assert.ok(!MAP_JS.includes('coverage-outline-key'), 'weather-map.js no longer emits the key element');
  assert.ok(!MAP_JS.includes('虛線＝目前資料來源範圍'),
    'the zh-TW legend string and its en/ja dictionary entries are gone');
  assert.ok(!MAP_CSS.includes('coverage-outline-key'), 'weather-map.css drops both key rules');
  assert.ok(!WG_HTML.includes('coverage-outline-key'), 'weather-map.html carries no key markup');
});

test('CL-UI-108: updateLegend keeps the surrounding keys intact (wind + coverage swatches)', () => {
  const legendBody = grab(MAP_JS, 'function updateLegend(cfg){', 'function toggleLegendExpanded(btn){');
  assert.match(legendBody, /\$\{windKey\}/);
  assert.match(legendBody, /\$\{coverageKey\}/, 'camera/subject/environment swatch key untouched');
  assert.match(legendBody, /legend-toggle/, 'the legend toggle control stays');
});

// ---------------------------------------------------------------------------
// 3. The ⓘ data dialog keeps an opt-in (default OFF) display switch
// ---------------------------------------------------------------------------
test('CL-UI-108: ⓘ dialog carries the default-off coverage toggle with trilingual copy', () => {
  assert.match(WG_HTML, /<label class="data-info-coverage-toggle">/);
  assert.match(WG_HTML, /<input id="data-info-coverage-toggle" type="checkbox">/);
  assert.match(WG_HTML, /data-i18n="wm_cov_outline"/);
  // 三語等價（WM_STATIC zh-TW/en/ja）。
  assert.match(MAP_JS, /wm_cov_outline:'顯示目前資料來源範圍（預設關閉）'/);
  assert.match(MAP_JS, /wm_cov_outline:'Show the current data-source coverage box \(off by default\)'/);
  assert.match(MAP_JS, /wm_cov_outline:'現在のデータソース範囲の枠を表示（既定はオフ）'/);
  // 接線：change → state flag → renderAll（虛線是 canvas 繪製，必須重繪生效）。
  const wiring = grab(MAP_JS, 'function initDataInfoDialog(){', 'function syncInspectorVisibility(){');
  assert.match(wiring, /\$\('data-info-coverage-toggle'\)/);
  assert.match(wiring, /coverageToggle\.checked=Boolean\(state\.showCoverageOutline\)/,
    'the checkbox reflects the OFF-by-default state');
  assert.match(wiring, /state\.showCoverageOutline=coverageToggle\.checked;/);
  assert.match(wiring, /if\(state\.data\) renderAll\(\);/,
    'toggling re-renders the data canvas immediately');
});

// ---------------------------------------------------------------------------
// 4. Cache-bust stamps bumped (bclwg43 -> bclwg50)
// ---------------------------------------------------------------------------
test('CL-UI-108: weather-map.html stamps bumped to bclwg50', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg53/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg50/);
  assert.ok(!/bclwg43/.test(WG_HTML), 'old stamp must not linger');
});

// ---------------------------------------------------------------------------
// 5. Live headless assertion — five model layers, one by one (lazy boot)
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
      '--no-first-run','--remote-debugging-port=0',
      '--window-size=390,844',
      '--user-data-dir=' + fs.mkdtempSync(path.join(require('node:os').tmpdir(), 'clui108-')), 'about:blank'],
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

// Deterministic byte signature of the weather canvas (data + overlays only —
// no randomness in any draw path with particles off, so two identical frames
// hash identically).
const CANVAS_SIG = `(() => {
  const c = document.getElementById('weather-canvas');
  if (!c || !c.width) return { ready: false };
  const ctx = c.getContext('2d');
  const d = ctx.getImageData(0, 0, c.width, c.height).data;
  let h = 2166136261, opaque = 0;
  for (let i = 0; i < d.length; i += 4) {
    if (d[i+3] > 0) opaque++;
    h ^= d[i] | (d[i+1] << 8) | (d[i+2] << 16) | (d[i+3] << 24);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return { ready: true, hash: h >>> 0, opaque };
})()`;

// Pixel scan for the outline's exact paint: rgba(125,211,252,.52) composited
// over a TRANSPARENT canvas cell is (125,211,252,~133). No other draw path
// uses this color. (Only used with the toggle OFF, where nothing may paint it.)
const OUTLINE_PIXELS = `(() => {
  const c = document.getElementById('weather-canvas');
  if (!c || !c.width) return { ready: false };
  const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
  let hits = 0;
  for (let i = 0; i < d.length; i += 4) {
    if (Math.abs(d[i]-125) <= 8 && Math.abs(d[i+1]-211) <= 8 && Math.abs(d[i+2]-252) <= 8
        && d[i+3] >= 126 && d[i+3] <= 140) hits++;
  }
  return { ready: true, hits };
})()`;

// A/B diff probe: store the current frame, then report how many pixels changed
// since the previous snapshot. Compositing-independent (the outline may lie
// over opaque data cells, where its alpha blends to 255) and void of any
// color-matching assumptions.
const SNAP_DIFF = `(() => {
  const c = document.getElementById('weather-canvas');
  if (!c || !c.width) return { ready: false };
  const cur = c.getContext('2d').getImageData(0, 0, c.width, c.height);
  const ref = window.__clui108Ref;
  window.__clui108Ref = cur;
  if (!ref || ref.width !== cur.width || ref.height !== cur.height) return { ready: true, diff: -1 };
  let diff = 0;
  const a = ref.data, b = cur.data;
  for (let i = 0; i < a.length; i += 4) {
    if (a[i] !== b[i] || a[i+1] !== b[i+1] || a[i+2] !== b[i+2] || a[i+3] !== b[i+3]) diff++;
  }
  return { ready: true, diff };
})()`;

const DEBUG_PROBE = `(() => {
  const dbg = window.__weatherGridCoverageDebug;
  return { ready: !!(dbg && dbg.showCoverageOutline !== undefined), dbg };
})()`;

async function switchModel(mode) {
  await evaljs(`(() => {
    const sel = document.getElementById('model-select');
    sel.value = ${JSON.stringify(mode)};
    sel.dispatchEvent(new Event('change', {bubbles: true}));
    return sel.value;
  })()`);
}

async function setToggle(on) {
  return evaljs(`(() => {
    const t = document.getElementById('data-info-coverage-toggle');
    t.checked = ${on ? 'true' : 'false'};
    t.dispatchEvent(new Event('change', {bubbles: true}));
    return t.checked;
  })()`);
}

async function settle() {
  // Wait until a signature repeats identically across two samples (draws settled).
  let prev = null;
  for (let i = 0; i < 60; ++i) {
    const sig = await evaljs(CANVAS_SIG);
    if (sig.ready && prev && sig.hash === prev.hash && sig.opaque === prev.opaque) return sig;
    prev = sig;
    await new Promise(r => setTimeout(r, 300));
  }
  return prev;
}

test('CL-UI-108 LIVE: five model layers draw no data-source coverage outline by default',
  { timeout: 300000 }, async t => {
  await bootBrowser();
  t.after(() => teardownBrowser());
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', {width: 390, height: 844, deviceScaleFactor: 1, mobile: true});
  await send('Page.navigate', {url: baseURL + '?spot='});
  let probe = { ready: false };
  for (let i = 0; i < 60 && !probe.ready; ++i) {
    await new Promise(r => setTimeout(r, 1000));
    probe = await evaljs(DEBUG_PROBE);
  }
  assert.ok(probe.ready, 'WeatherGrid data + debug hook must boot within the wait window');
  assert.equal(probe.dbg.showCoverageOutline, false, 'default state flag is OFF');

  for (const mode of FIVE_MODES) {
    await switchModel(mode);
    // Wait for the model's bundle to be present so the outline gate is
    // exercised with a real provider bbox (not a no-data early return).
    let ok = false;
    for (let i = 0; i < 40 && !ok; ++i) {
      const dbg = (await evaljs(DEBUG_PROBE)).dbg;
      ok = mode === 'himawari' ? !!dbg.himawariAvailable
        : mode === 'gfs' ? !!dbg.datasets.gfs
        : !!(dbg.datasets || {})[mode];
      if (!ok) await new Promise(r => setTimeout(r, 1000));
    }
    assert.ok(ok, `${mode}: model bundle present within the wait window`);
    await settle();

    // (a) debug flag stays OFF by default for every model.
    const dbg = (await evaljs(DEBUG_PROBE)).dbg;
    assert.equal(dbg.showCoverageOutline, false, `${mode}: coverage outline flag default OFF`);
    // (b) no outline-colored pixels on the canvas.
    const px = await evaljs(OUTLINE_PIXELS);
    assert.equal(px.hits, 0, `${mode}: zero data-source-coverage outline pixels`);
    // (c) legend DOM carries no 虛線 note.
    // CL-CI-39: headless CI has no WebGL, so MapLibre cannot mount and the 2D
    // overlay's outline A/B probe has nothing to redraw against. Assert the
    // documented degraded state explicitly instead of a blind skip.
    const webglState = await evaljs(`(() => {
      const w = document.querySelector('.map-wrap');
      return w ? (w.dataset.webgl || null) : null;
    })()`);
    if (webglState === 'unsupported') {
      const degraded = await evaljs(`(() => {
        const strip = document.querySelector('.wm-webgl-fallback');
        const cv = document.getElementById('weather-canvas');
        const r = cv && cv.getBoundingClientRect();
        return { strip: !!strip, stripText: strip && strip.textContent,
                 canvasW: r && r.width, canvasH: r && r.height };
      })()`);
      assert.equal(degraded.strip, true, 'no-WebGL: the basemap gap is explained to the user');
      assert.match(degraded.stripText || '', /WebGL/, 'no-WebGL: the notice names the cause');
      assert.ok(degraded.canvasW > 0 && degraded.canvasH > 0,
        'no-WebGL: the 2D weather overlay still owns its box');
      t.diagnostic('no-WebGL: outline A/B probe not applicable (basemap absent)');
      return;
    }
    const legend = await evaljs(`(() => {
      const l = document.getElementById('legend');
      return { outlineKey: !!l.querySelector('.coverage-outline-key'),
               text: l.textContent || '', visible: !l.hidden };
    })()`);
    assert.equal(legend.outlineKey, false, `${mode}: no .coverage-outline-key in the legend`);
    if (legend.visible) {
      assert.ok(!/虛線＝目前資料來源範圍/.test(legend.text),
        `${mode}: legend text must not carry the removed note`);
    }
    // (d) A/B: the opt-in switch still works — ON changes the canvas pixels,
    //     OFF restores them byte-for-byte (removal is a deterministic no-op).
    //     The diff probe is compositing-independent (the outline may lie over
    //     opaque data cells, so exact-alpha pixel matching is not reliable).
    const offSig = await evaljs(CANVAS_SIG);
    assert.equal((await evaljs(SNAP_DIFF)).diff, -1, `${mode}: OFF frame stored as the A/B reference`);
    await setToggle(true);
    const onSig = await settle();
    assert.notEqual(onSig.hash, offSig.hash, `${mode}: opt-in toggle actually redraws with the outline`);
    assert.equal((await evaljs(SNAP_DIFF)).diff > 0, true,
      `${mode}: outline pixels appear when the user opts in`);
    await setToggle(false);
    const backSig = await settle();
    assert.equal(backSig.hash, offSig.hash, `${mode}: OFF restores the canvas byte-for-byte`);
    assert.equal((await evaljs(SNAP_DIFF)).diff > 0, true,
      `${mode}: dropping back OFF changes the frame again (outline gone)`);
    assert.equal((await evaljs(OUTLINE_PIXELS)).hits, 0, `${mode}: outline pixels gone again`);
    await evaljs(`window.__clui108Ref = null;`);
  }
});


// CL-CI-40: release the browser, the CDP socket and the static server even when a
// test aborts or fails. Without a file-level hook the old "teardown" TEST only ran
// if every earlier test completed, so one hang left a Chrome process behind and the
// runner eventually reported the remaining cases as `cancelled` (OOM).
test.after(async () => {
  try { await teardownBrowser(); } catch (_) { /* already gone */ }
});
