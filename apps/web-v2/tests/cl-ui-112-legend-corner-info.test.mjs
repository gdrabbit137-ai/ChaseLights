// CL-UI-112: 天氣圖角落資訊合併縮小（owner 裁示 — 小票）。
// Contract (mobile shell, min(w,h)≤768 only; 1280 desktop zero change):
//   (1) 右上「ⓘ 資料」獨立排退場（.weather-header display:none）——ⓘ 收進左下角
//       圖例框標題列（標題行「低雲 ⓘ」），點 ⓘ 開同一個資料彈出
//       （模型/起報/解析度 meta 列＋範圍 opt-in，CL-UI-106/108 契約照舊）。
//   (2) 圖例框縮小：字級 11px、padding 緊縮（4px 5px）、寬度 min-content。
//   (3) 地圖右上只剩縮放鈕（＋/−）——↺ 模型範圍移到地圖右下。
//   (4) 桌面 1280 零改動：header ⓘ 保留、圖例無 ⓘ、圖例字級/尺寸不變。
// Run: node --test apps/web-v2/tests/cl-ui-112-legend-corner-info.test.mjs
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
// 1. Source pins
// ---------------------------------------------------------------------------
test('CL-UI-112 source: legend title row carries the ⓘ slot, wired to the same data dialog', () => {
  // updateLegend renders 標題列「<圖層名> ⓘ」
  const legendBody = MAP_JS.slice(MAP_JS.indexOf('function updateLegend(cfg){'),
    MAP_JS.indexOf('function toggleLegendExpanded(btn){'));
  assert.match(legendBody, /<div class="legend-title"><strong>\$\{wmT\(cfg\.label\)\}<\/strong><button type="button" class="legend-info"/,
    'legend title row = layer name + ⓘ button');
  assert.ok(legendBody.includes("aria-label=\"${wmT('資料說明')}\""), 'ⓘ carries the trilingual aria label');
  // delegation lives in initDataInfoDialog and reuses the header ⓘ open path
  const dlgWire = MAP_JS.slice(MAP_JS.indexOf('function initDataInfoDialog(){'),
    MAP_JS.indexOf('function syncInspectorVisibility(){'));
  assert.ok(dlgWire.includes("ev.target.closest('.legend-info')"), 'delegated click filter on .legend-info');
  assert.ok(dlgWire.includes('open.click()'), 'reuses the header ⓘ open path (meta rows + showModal)');
  // i18n: the ⓘ label exists in en and ja phrase packs
  assert.ok(MAP_JS.includes("'資料說明':'Data info'"), 'en phrase present');
  assert.ok(MAP_JS.includes("'資料說明':'データ解説'"), 'ja phrase present');
  // stamp bump
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg46/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg46/);
});

test('CL-UI-112 CSS: base hides the legend ⓘ (desktop zero change); mobile block shrinks the legend box', () => {
  const mobileStart = MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){');
  const mobileBlock = MAP_CSS.slice(mobileStart);
  const beforeMobile = MAP_CSS.slice(0, mobileStart);
  // base: title row + hidden ⓘ (1280 keeps the header ⓘ as the only entry)
  assert.match(beforeMobile, /\.legend-title\{display:flex;align-items:center;justify-content:space-between;gap:6px\}/);
  assert.match(beforeMobile, /\.legend-info\{display:none\}/);
  // mobile: header row retired + ⓘ revealed
  assert.match(mobileBlock, /\.weather-header\{display:none\}/, '右上「ⓘ 資料」獨立排退場');
  assert.match(mobileBlock, /\.legend-info\{display:inline-flex/, 'ⓘ 收進圖例框標題列');
  // mobile: legend box shrinks — 11px font, tight padding, min-content width
  assert.match(mobileBlock, /\.map-wrap \.legend\{min-width:0;width:min-content;max-width:min\(64vw,240px\);padding:4px 5px;font-size:11px\}/,
    '圖例框縮小（字級 11px、padding 緊縮、寬度 min-content）');
  assert.match(mobileBlock, /\.legend strong\{font-size:11px\}/, '標題字級 11px');
  assert.match(mobileBlock, /\.legend-toggle \.legend-bar\{width:110px;display:block\}/,
    'min-content width needs an explicit bar width (percentage/flex children collapse)');
  // mobile: top-right keeps only the zoom group — reset moves to the bottom-right
  assert.match(mobileBlock, /#reset-view\{position:absolute;left:auto;right:8px;top:auto;bottom:34px/,
    '↺ 模型範圍 leaves the map top-right');
  // desktop block untouched by the relocation
  const desktopBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'));
  assert.ok(!desktopBlock.includes('#reset-view'), 'desktop reset positioning unchanged');
  assert.ok(!desktopBlock.includes('legend-info'), 'desktop legend carries no ⓘ');
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
    '--enable-unsafe-swiftshader','--use-angle=swiftshader',
    '--no-first-run','--remote-debugging-port=0',
    '--window-size=1280,900',
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui112-')), 'about:blank'],
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
  await new Promise(r => setTimeout(r, 2500));
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.map-panel') && document.querySelector('.wm-ops')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>30000){clearInterval(iv);reject(new Error('app shell never rendered'));}
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
    return {t:Math.round(b.top),b:Math.round(b.bottom),h:Math.round(b.height),l:Math.round(b.left),rr:Math.round(b.right),w:Math.round(b.width)}; };
  const cs=el=>el?getComputedStyle(el):null;
  const leg=$('#legend'), info=$('.legend-info');
  const legCS=cs(leg);
  return {
    innerW:window.innerWidth,
    header:r($('.weather-header')),
    infoBtn:r($('#data-info-open')),
    legend:r(leg), legendInfo:r(info),
    legendFont:legCS?legCS.fontSize:null,
    legendPad:legCS?legCS.padding:null,
    strongFont:leg?cs(leg.querySelector('.legend-title strong')).fontSize:null,
    zoom:r($('#weather-basemap .maplibregl-ctrl-top-right')),
    reset:r($('#reset-view')),
    title:(leg?((leg.querySelector('.legend-title strong')||{}).textContent||''):null),
  };
})()`;

// ---- (2a) 390: ⓘ row gone, ⓘ lives in the shrunk legend, top-right = zoom only ----
test('CL-UI-112 (2a) 390px: ⓘ in the legend title, legend shrunk, top-right zoom-only, header row gone', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  await send('Page.bringToFront');
  await waitDataReady();
  const p = await evaljs(SHELL_PROBE);
  assert.equal(p.header.h, 0, '右上「ⓘ 資料」獨立排退場 (header display:none)');
  assert.equal(p.infoBtn.h, 0, 'header ⓘ button retired with the row');
  assert.ok(p.legend && p.legend.h > 0, 'legend box visible (data ready)');
  assert.ok(p.legendInfo && p.legendInfo.h > 0, 'ⓘ present in the legend title row');
  assert.ok(p.legendInfo.l >= p.legend.l && p.legendInfo.rr <= p.legend.rr + 1,
    'ⓘ sits inside the legend box');
  assert.ok((p.title || '').length > 0, `legend title row carries the layer name (${p.title})`);
  assert.equal(p.legendFont, '11px', `legend font 11px (got ${p.legendFont})`);
  assert.equal(p.strongFont, '11px', `legend title font 11px (got ${p.strongFont})`);
  assert.equal(p.legendPad, '4px 5px', `padding 緊縮 (got ${p.legendPad})`);
  assert.ok(p.legend.w > 0 && p.legend.w < 132, `box narrower than the old 132px min-width (w=${p.legend.w})`);
  // 地圖右上只剩縮放鈕
  assert.ok(p.zoom && p.zoom.h > 0 && p.zoom.rr >= p.innerW - 60,
    `zoom group hugs the top-right (right=${p.zoom && p.zoom.rr}/${p.innerW})`);
  assert.ok(p.reset && p.reset.h > 0 && p.reset.t > p.zoom.b,
    `↺ reset no longer at the top-right (t=${p.reset && p.reset.t}, zoom.b=${p.zoom && p.zoom.b})`);
});

// ---- (2b) 390: real click on the legend ⓘ opens the data dialog with meta rows ----
test('CL-UI-112 (2b) 390px: clicking the legend ⓘ opens the data dialog (模型/起報/解析度 + opt-in)', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  await send('Page.bringToFront');
  await waitDataReady();
  const p = await evaljs(SHELL_PROBE);
  assert.ok(p.legendInfo && p.legendInfo.h > 0, 'legend ⓘ reachable');
  await realClickAt(Math.round((p.legendInfo.l + p.legendInfo.rr) / 2), Math.round((p.legendInfo.t + p.legendInfo.b) / 2));
  await new Promise(r => setTimeout(r, 300));
  const meta = await evaljs(`(() => {
    const d=document.querySelector('#data-info-dialog'), host=document.querySelector('#data-info-meta');
    const lines=[...host.querySelectorAll('.data-info-meta-line')].map(l=>l.textContent);
    return {open:d.open, hidden:host.hidden, lines,
      optin:!!document.querySelector('#data-info-coverage-toggle')};
  })()`);
  assert.equal(meta.open, true, 'legend ⓘ opens the data dialog');
  assert.equal(meta.hidden, false, 'meta block visible on the mobile shell');
  assert.equal(meta.lines.length, 3, 'three meta rows (模型/起報時間/解析度)');
  assert.ok(meta.optin, '範圍 opt-in switch still in the dialog');
  await evaljs(`document.querySelector('#data-info-close').click()`);
  await new Promise(r => setTimeout(r, 250));
});

// ---- (2c) 1280 regression: header ⓘ kept, no legend ⓘ, legend styling unchanged ----
test('CL-UI-112 (2c) 1280px: zero change — header ⓘ kept, legend has no ⓘ and keeps its size', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  await evaljs(`window.scrollTo(0,0); new Promise(r=>setTimeout(r,150))`);
  const p = await evaljs(SHELL_PROBE);
  assert.ok(p.header.h > 0, 'header (with the ⓘ button) kept on desktop');
  assert.ok(p.infoBtn && p.infoBtn.h > 0, 'desktop header ⓘ button kept');
  assert.ok(!p.legendInfo || p.legendInfo.h === 0, 'no ⓘ inside the desktop legend');
  assert.notEqual(p.legendFont, '11px', 'desktop legend font untouched');
  assert.notEqual(p.legendPad, '4px 5px', 'desktop legend padding untouched');
});

test('CL-UI-112 (2d): browser teardown', async () => { await teardownBrowser(); });
