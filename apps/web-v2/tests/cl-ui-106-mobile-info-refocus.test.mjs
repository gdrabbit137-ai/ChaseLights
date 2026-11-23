// CL-UI-106: 手機天氣圖移除上下資訊塊（owner 裁示）。
// Contract (mobile shell, <=768px only):
//   (1) 頂部退場：WeatherGrid Preview 標題＋模型 chip（AUTO·…）＋起報資訊行；
//       內容收進右上「ⓘ 資料」彈出（data-info-dialog 內 模型/起報時間/解析度列，
//       點開才看）＋圖層 sheet 模型列（#wm-ls-model）。ⓘ 按鈕本身保留在右上。
//   (2) 底部退場：site-footer（資料來源與授權連結＋免責行）——sources.html
//       已涵蓋，地圖頁不再重複。
//   (3) 地圖區獲得高度：map ≥60% 視高仍成立（CL-UI-105 契約重測）。
//   (4) 桌面 1280 零改動：標題/banner 保留；footer 照常；ⓘ 彈出不加 meta 列。
// Run: node --test apps/web-v2/tests/cl-ui-106-mobile-info-refocus.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync, mkdtempSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const MAP_JS = readFileSync(join(WEB, 'assets', 'weather-map.js'), 'utf8');
const MAP_CSS = readFileSync(join(WEB, 'assets', 'weather-map.css'), 'utf8');
const WG_HTML = readFileSync(join(WEB, 'weather-map.html'), 'utf8');

// ---------------------------------------------------------------------------
// 1. Source pins: markup + mobile-block CSS + JS wiring
// ---------------------------------------------------------------------------
test('CL-UI-106 source: markup carries the ⓘ meta host and the layer-sheet model row', () => {
  // ⓘ dialog gains the meta host as the FIRST child of .data-info-body
  const body = WG_HTML.slice(WG_HTML.indexOf('<div class="data-info-body">'),
    WG_HTML.indexOf('<p data-i18n="wm_dialog_p1">'));
  assert.ok(body.includes('id="data-info-meta"'), 'ⓘ dialog carries the meta host');
  assert.match(body, /<div id="data-info-meta" class="data-info-meta" hidden>/,
    'meta host starts hidden (filled only when opened on the mobile shell)');
  // layer sheet gains the model row between chips grid and legend rows
  const sheetStart = WG_HTML.indexOf('id="wm-layer-sheet"');
  const sheet = WG_HTML.slice(sheetStart, WG_HTML.indexOf('</section>', sheetStart));
  assert.ok(sheet.includes('id="wm-ls-model"'), 'layer sheet carries the model row');
  const chipsAt = sheet.indexOf('id="wm-ls-chips"'), modelAt = sheet.indexOf('id="wm-ls-model"'),
    legendAt = sheet.indexOf('wm-ls-legend');
  assert.ok(chipsAt !== -1 && modelAt !== -1 && legendAt !== -1, 'sheet anatomy intact');
  assert.ok(chipsAt < modelAt && modelAt < legendAt, 'model row sits between chips and legend');
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg50/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg49/);
});

test('CL-UI-106 CSS (mobile): title block + model chip + cycle line + footer retired (CL-UI-112: ⓘ row retired too, ⓘ lives in the legend)', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /\.weather-header \.header-title-line\{display:none\}/,
    'WeatherGrid Preview title block retired on the mobile shell');
  assert.match(mobileBlock, /\.weather-header \.source-pill,\.weather-header \.source-mobile-summary\{display:none\}/,
    'model chip + cycle line retired on the mobile shell');
  assert.match(mobileBlock, /\.weather-header\{display:none\}/,
    'CL-UI-112: the whole header row (ⓘ 資料 alone, aligned right) retired');
  assert.match(mobileBlock, /\.legend-info\{display:inline-flex/,
    'CL-UI-112: ⓘ moved into the legend title row');
  assert.match(mobileBlock, /#reset-view\{position:absolute;left:auto;right:8px/,
    'CL-UI-112: ↺ 模型範圍 leaves the map top-right (zoom-only there)');
  assert.match(mobileBlock, /body \.site-footer\{display:none\}/,
    'site-footer (sources link + disclaimer) retired on the mobile shell');
  assert.match(mobileBlock, /\.data-info-meta\{/, 'ⓘ dialog meta block styling present');
  assert.match(mobileBlock, /\.wm-ls-model\{flex:none/, 'layer sheet model row styling present');
  // no leak outside the mobile block (1280 zero-change)
  const beforeMobile = MAP_CSS.slice(0, MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.ok(!/\.header-title-line\{display:none/.test(beforeMobile), 'no title-block retirement leak');
  assert.ok(!/site-footer\{display:none/.test(beforeMobile), 'no footer retirement leak');
  assert.ok(!/\.data-info-meta\{/.test(beforeMobile), 'no meta styling leak');
  assert.ok(!/\.wm-ls-model\{/.test(beforeMobile), 'no model-row styling leak');
  assert.ok(!/\.legend-info\{display:inline-flex/.test(beforeMobile), 'no legend-ⓘ reveal leak (desktop keeps .legend-info{display:none})');
  const desktopBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'));
  assert.ok(!desktopBlock.includes('site-footer'), 'desktop footer untouched');
  assert.ok(!desktopBlock.includes('legend-info'), 'desktop legend carries no ⓘ');
});

test('CL-UI-106 JS: ⓘ dialog fills 模型/起報時間/解析度 (mobile only) and the layer sheet fills the model row', () => {
  // helper present and wired into both surfaces
  assert.ok(MAP_JS.includes('let wmDataInfoMeta=null;'), 'meta stash');
  const render = MAP_JS.slice(MAP_JS.indexOf('function wmRenderDataInfoMeta(){'),
    MAP_JS.indexOf('function initDataInfoDialog(){'));
  assert.ok(render.includes("wmT('模型')") && render.includes("wmT('起報時間')") && render.includes("wmT('解析度')"),
    'meta rows are the three i18n-labelled facts');
  assert.ok(render.includes('!wmIsMobileShell()'), 'meta is mobile-shell-only (1280 zero change)');
  const open = MAP_JS.slice(MAP_JS.indexOf('open.addEventListener(\'click\''),
    MAP_JS.indexOf('close.addEventListener(\'click\''));
  assert.ok(open.includes('wmRenderDataInfoMeta();'), 'opening the ⓘ dialog (re)renders the meta rows');
  // CL-UI-112: the legend title ⓘ opens the SAME dialog (delegated on #legend)
  const dlgWire = MAP_JS.slice(MAP_JS.indexOf('function initDataInfoDialog(){'),
    MAP_JS.indexOf('function syncInspectorVisibility(){'));
  assert.ok(dlgWire.includes("ev.target.closest('.legend-info')"), 'legend ⓘ delegation wired into initDataInfoDialog');
  assert.ok(dlgWire.includes("open.click()"), 'legend ⓘ reuses the header ⓘ open path');
  // stash site: updateSourceMeta feeds the latest facts
  const stash = MAP_JS.slice(MAP_JS.indexOf('CL-UI-106: stash the'),
    MAP_JS.indexOf('const attributionHost='));
  assert.ok(stash.includes('wmDataInfoMeta={model:status.textContent,cycle:wmInfoCycle,resolution};'),
    'model/cycle/resolution stashed from the live source meta');
  // layer sheet model row
  const sheetOpen = MAP_JS.slice(MAP_JS.indexOf('function wmOpenLayerSheet(){'),
    MAP_JS.indexOf('function wmCloseLayerSheet(){'));
  assert.ok(sheetOpen.includes("const modelRow=$('wm-ls-model');"), 'layer sheet fills the model row');
  assert.ok(sheetOpen.includes("($('source-state').textContent||'—')"), 'model row reads the live model chip text');
  // i18n: the new labels exist in en and ja phrase packs (zh-TW = source literal;
  // en/ja values are distinct literals so presence in the file is unambiguous)
  assert.ok(MAP_JS.includes("'模型':'Model'") && MAP_JS.includes("'起報時間':'Init time'") && MAP_JS.includes("'解析度':'Resolution'"),
    'en phrases present');
  assert.ok(MAP_JS.includes("'模型':'モデル'") && MAP_JS.includes("'起報時間':'起報時刻'") && MAP_JS.includes("'解析度':'解像度'"),
    'ja phrases present');
});

// ---------------------------------------------------------------------------
// 2. Real-browser probes (lazy boot — never a root test.before)
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
  const MIME = {'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css',
    '.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.woff':'font/woff','.woff2':'font/woff2'};
  server = createServer((req, res) => {
    const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
    const file = join(WEB, p === '/' ? 'weather-map.html' : p.slice(1));
    try { const body = readFileSync(file);
      res.writeHead(200, {'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
      res.end(body);
    } catch { res.writeHead(404); res.end('not found'); }
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  baseURL = `http://127.0.0.1:${server.address().port}/weather-map.html`;
  chrome = spawn(BROWSER, [
    '--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
    '--no-first-run','--remote-debugging-port=0',
    '--window-size=1280,900',
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui106-')), 'about:blank'],
    {stdio: ['ignore', 'ignore', 'pipe']});
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = '';
    let loopLast = Date.now(); const loopStart = loopLast;
    const t = setInterval(() => {
      const now = Date.now();
      if (now - loopLast < 1500 && now - loopStart > 60000) {
        clearInterval(t); reject(new Error('no devtools endpoint'));
      }
      loopLast = now;
    }, 250);
    chrome.stderr.on('data', d => { buf += d;
      const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
      if (m) { clearInterval(t); resolve(m[1]); } });
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

async function teardownBrowser() {
  ready = null;
  await Promise.all([
    (async () => { try { ws?.close(); } catch {} })(),
    (async () => { try { chrome?.kill(); } catch {} })(),
    (async () => { try { await new Promise(r => server?.close(r)); } catch {} })()
  ]);
}

async function setViewport(width, height, mobile) {
  await send('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor: 1, mobile});
}

async function loadPage() {
  await send('Page.enable');
  await send('Page.navigate', {url: baseURL});
  await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.map-panel') && document.querySelector('.wm-ops')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>20000){clearInterval(iv);reject(new Error('app shell never rendered'));}
    },100);
  })`);
  await new Promise(r => setTimeout(r, 600));
}

async function waitDataReady(timeoutMs = 45000) {
  return evaljs(`new Promise(resolve=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(window.__weatherGridPreviewReady===true){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>${timeoutMs}){clearInterval(iv);resolve(false);}
    },200);
  })`);
}

async function realClickAt(cx, cy) {
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', {type, x: cx, y: cy, button: 'left', clickCount: 1});
  }
}

const SHELL_PROBE = `(() => {
  const $=s=>document.querySelector(s);
  const r=el=>{ if(!el) return null; const b=el.getBoundingClientRect();
    return {t:Math.round(b.top),b:Math.round(b.bottom),h:Math.round(b.height),l:Math.round(b.left),rr:Math.round(b.right)}; };
  const wrap=$('.map-wrap');
  return {
    innerH:window.innerHeight, innerW:window.innerWidth,
    title:r($('.weather-header .header-title-line')),
    subtitle:r($('.weather-header .subtitle')),
    pill:r($('#source-state')),
    summary:r($('#source-mobile-summary')),
    infoBtn:r($('#data-info-open')),
    legendInfo:r($('.legend-info')),
    legend:r($('#legend')),
    reset:r($('#reset-view')),
    zoom:r($('#weather-basemap .maplibregl-ctrl-top-right')),
    footer:r($('.site-footer')),
    mapPct:wrap?+(wrap.getBoundingClientRect().height/window.innerHeight).toFixed(4):null,
    modelRowText:($('#wm-ls-model')||{}).textContent||null,
    // CL-CI-39: the shell renders an explicit fallback when WebGL is missing
    webglState:wrap?wrap.dataset.webgl||null:null,
    fallback:r($('.wm-webgl-fallback')),
  };
})()`;

// ---- (2a) 390: no top info block, no footer, ⓘ row retired (CL-UI-112: ⓘ lives in the legend), map ≥60% ----
test('CL-UI-106 (2a) 390px: title/chip/cycle/footer retired; ⓘ row gone (ⓘ in the legend title); map ≥60% viewport', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  await send('Page.bringToFront');
  await waitDataReady();
  const p = await evaljs(SHELL_PROBE);
  assert.equal(p.title.h, 0, `WeatherGrid Preview title block retired (${p.title && p.title.h}px)`);
  assert.equal(p.subtitle.h, 0, 'subtitle retired with the title block');
  assert.equal(p.pill.h, 0, `model chip (AUTO·…) retired (${p.pill && p.pill.h}px)`);
  assert.equal(p.summary.h, 0, `cycle/info line retired (${p.summary && p.summary.h}px)`);
  assert.equal(p.footer.h, 0, '資料來源/免責 footer rows retired');
  // CL-UI-112: the standalone top-right ⓘ 資料 row is retired with the header
  assert.equal(p.infoBtn.h, 0, 'ⓘ 資料 standalone top-right row retired (header display:none)');
  // …and the ⓘ lives inside the bottom-left legend title row instead
  assert.ok(p.legendInfo && p.legendInfo.h > 0, 'legend title ⓘ present and reachable');
  assert.ok(p.legendInfo.l >= p.legend.l && p.legendInfo.rr <= p.legend.rr + 1,
    'legend ⓘ sits inside the legend box');
  // CL-CI-39: headless CI has no WebGL context, so MapLibre never mounts and the
  // zoom control group cannot exist. The contract then is the explicit fallback:
  // the map area keeps its reserved height and the panel says why.
  if (p.webglState === 'unsupported') {
    assert.ok(p.fallback && p.fallback.h > 0,
      'no-WebGL: the explicit fallback panel renders inside the map area');
    assert.equal(p.reset.h, 0, 'no-WebGL: the reset pill is hidden (nothing to reset)');
    assert.ok(p.mapPct >= 0.6, `no-WebGL: the map area still reserves >=60% viewport (${p.mapPct})`);
  } else {
    // CL-UI-112: the map top-right carries ONLY the zoom (+/−) group — the ↺
    // reset pill moved to the bottom-right
    assert.ok(p.zoom && p.zoom.h > 0 && p.zoom.rr >= p.innerW - 60,
      `zoom group hugs the top-right (right=${p.zoom && p.zoom.rr}/${p.innerW})`);
    assert.ok(p.reset && p.reset.h > 0 && p.reset.t > p.zoom.b,
      `reset pill is below the zoom group (t=${p.reset && p.reset.t})`);
  }
  // 地圖區獲得高度 — CL-UI-105 contract still holds (re-measured)
  assert.ok(p.mapPct >= 0.60, `地圖區 ≥60% 視高 (實測 ${(p.mapPct * 100).toFixed(1)}%)`);
});

// ---- (2b) 390: ⓘ dialog carries 模型/起報時間/解析度; layer sheet model row ----
test('CL-UI-106 (2b) 390px: ⓘ dialog shows model/init/resolution; layer sheet carries the model row', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  await send('Page.bringToFront');
  await waitDataReady();
  const p = await evaljs(SHELL_PROBE);
  // open the ⓘ dialog with a real click on the legend title ⓘ (CL-UI-112)
  assert.ok(p.legendInfo && p.legendInfo.h > 0, 'legend title ⓘ reachable before the click');
  await realClickAt(Math.round((p.legendInfo.l + p.legendInfo.rr) / 2), Math.round((p.legendInfo.t + p.legendInfo.b) / 2));
  await new Promise(r => setTimeout(r, 300));
  const meta = await evaljs(`(() => {
    const d=document.querySelector('#data-info-dialog'), host=document.querySelector('#data-info-meta');
    const lines=[...host.querySelectorAll('.data-info-meta-line')].map(l=>l.textContent);
    return {open:d.open, hidden:host.hidden, lines};
  })()`);
  assert.equal(meta.open, true, 'ⓘ dialog opens');
  assert.equal(meta.hidden, false, 'meta block visible on the mobile shell');
  assert.equal(meta.lines.length, 3, 'exactly the three meta rows (模型/起報時間/解析度)');
  const sourceState = await evaljs(`document.querySelector('#source-state').textContent`);
  assert.ok(meta.lines[0].startsWith('模型') && meta.lines[0].includes(sourceState),
    `模型 row shows the live model (${meta.lines[0]})`);
  assert.ok(meta.lines[1].startsWith('起報時間') && meta.lines[1].length > 4,
    `起報時間 row populated (${meta.lines[1]})`);
  assert.ok(meta.lines[2].startsWith('解析度') && meta.lines[2].length > 4,
    `解析度 row populated (${meta.lines[2]})`);
  // close the dialog (✕), then open the layer sheet and check the model row
  await evaljs(`document.querySelector('#data-info-close').click()`);
  await new Promise(r => setTimeout(r, 250));
  const pill = await evaljs(`(() => { const b=document.querySelector('#layer-sheet-btn');
    const r=b.getBoundingClientRect(); return [Math.round(r.left+r.width/2), Math.round(r.top+r.height/2)]; })()`);
  await realClickAt(pill[0], pill[1]);
  await new Promise(r => setTimeout(r, 400));
  const sheet = await evaljs(SHELL_PROBE);
  assert.ok(sheet.modelRowText && sheet.modelRowText.startsWith('模型'),
    `layer sheet model row labelled (${sheet.modelRowText})`);
  assert.ok(sheet.modelRowText.includes(sourceState),
    'layer sheet model row shows the live model text');
});

// ---- (2c) 1280 regression: zero change — title/footer kept, no meta block ----
test('CL-UI-106 (2c) 1280px: zero change — title/banner + footer kept; ⓘ dialog gains no meta rows', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  // desktop loads can land focus-scrolled (pre-existing); the header probe and
  // the ⓘ click need the top of the page, not the mid-load scroll position.
  await evaljs(`window.scrollTo(0,0); new Promise(r=>setTimeout(r,150))`);
  const p = await evaljs(SHELL_PROBE);
  assert.ok(p.title.h > 0, 'WeatherGrid Preview title kept on desktop');
  assert.ok(p.footer.h > 0, 'site-footer kept on desktop');
  // open ⓘ on desktop: the meta host stays hidden (zero change)
  await realClickAt(Math.round((p.infoBtn.l + p.infoBtn.rr) / 2), Math.round((p.infoBtn.t + p.infoBtn.b) / 2));
  await new Promise(r => setTimeout(r, 300));
  const meta = await evaljs(`(() => { const d=document.querySelector('#data-info-dialog'), host=document.querySelector('#data-info-meta');
    return {open:d.open, hidden:host.hidden, lines:host.querySelectorAll('.data-info-meta-line').length}; })()`);
  assert.equal(meta.open, true, 'ⓘ dialog opens on desktop');
  assert.equal(meta.hidden, true, 'meta host stays hidden on desktop (no content change)');
  assert.equal(meta.lines, 0, 'no meta rows rendered on desktop');
});

test('CL-UI-106 (2d): browser teardown', async () => { await teardownBrowser(); });


// CL-CI-40: release the browser, the CDP socket and the static server even when a
// test aborts or fails. Without a file-level hook the old "teardown" TEST only ran
// if every earlier test completed, so one hang left a Chrome process behind and the
// runner eventually reported the remaining cases as `cancelled` (OOM).
test.after(async () => {
  try { await teardownBrowser(); } catch (_) { /* already gone */ }
});
