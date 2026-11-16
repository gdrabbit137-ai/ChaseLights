// CL-UI-105: 初始相機回台灣 + ?spot= 只帶回合法值 + 歸屬小字（owner 裁決）。
// Contract (mobile 390 first, desktop-safe by construction):
//   (1) 初始相機：無 ?spot=/?focus= 時，相機中心必須落在台灣（tw）地區 bbox
//       105–145E / 5–40N 內（初始 fitBounds=既有預設 bounds；MapLibre 預設
//       center [0,0] 會落在幾內亞/肯亞一帶——絕不可發生）。
//   (2) 重載重置：使用者拖歪相機後重新載入 → 回地區預設 bounds（相機狀態
//       不落 URL 也不落 localStorage；唯一例外是 URL 帶 spot）。
//   (3) ?spot= 跨頁帶回只帶回合法值：形狀合法但不存在的 id → 相機維持地區
//       預設 bounds，且 spot 參數從 URL 撤下（fail-closed）；合法 id → 景點
//       相機照常套用（CL-WG-19 語意不變）。
//   (4) OpenFreeMap/OpenMapTiles 歸屬縮到地圖下緣小字（右下角、≤22px 高、
//       不遮主要陸塊）；資料來源 ready 徽章不在天氣圖旁。
// Run: node --test apps/web-v2/tests/cl-ui-105-camera-deeplink.test.mjs
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

function grab(src, start, end) {
  const a = src.indexOf(start);
  assert.ok(a !== -1, `source slice start not found: ${start}`);
  const b = src.indexOf(end, a);
  assert.ok(b !== -1, `source slice end not found: ${end}`);
  return src.slice(a, b);
}

// ---------------------------------------------------------------------------
// 1. Source pins
// ---------------------------------------------------------------------------
test('CL-UI-105 camera JS: initial basemap constructor center carries bbox fallbacks (never [0,0])', () => {
  const init = grab(MAP_JS, 'async function initBasemap()', 'state.map=map;');
  assert.ok(init.includes('normalizeViewBbox(state.data.bbox)'), 'primary center source = dataset bbox');
  assert.match(init, /normalizeViewBbox\(state\.data\.bbox\)\s*\|\|\s*normalizeViewBbox\(state\.view\)/,
    'state.view is the first fallback');
  assert.match(init, /normalizeViewBbox\(state\.view\)\s*\|\|\s*normalizeViewBbox\(regionBbox\(\)\)/,
    'region bbox is the last fallback — the constructor center can never go NaN→[0,0]');
  assert.ok(MAP_JS.includes('setViewBbox(state.view || state.data.bbox)'), 'fitBounds re-anchors the camera right after construction');
});

test('CL-UI-105 camera JS: an illegal ?spot= id is dropped from the URL (fail-closed)', () => {
  // bundle-arrival retry path (PNG-stub first paint carries no spots)
  const bundlePath = grab(MAP_JS, 'applyDeepLinkSpotEntry();\n          // CL-UI-105', ' Enhancement bundles');
  assert.ok(bundlePath.includes('dlAfterBundle.spot=null'), 'bundle retry drops an unresolved spot param');
  assert.ok(bundlePath.includes("filter(k=>k!=='spot')"), 'spot key removed from urlKeys');
  assert.ok(bundlePath.includes('syncDeepLinkUrl(state.region,{keepEntryKeys:true})'), 'URL synced after the drop');
  // direct-load path (spots already on disk when the entry applies)
  const entry = grab(MAP_JS, 'function applyDeepLinkEntry()', 'function applyDeepLinkSpotEntry()');
  assert.match(entry, /if\(dl\.spot && \(state\.data\?\.spots\|\|\[\]\)\.length\)\{[\s\S]*?dl\.spot=null/,
    'entry path drops the spot param only when spots are on disk (stub keeps it for the retry)');
});

test('CL-UI-105 CSS: attribution shrinks to bottom-edge small text; ready source badge off the map', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px){'));
  assert.match(mobileBlock, /#weather-basemap \.maplibregl-ctrl-attrib\{font-size:\.52rem/,
    'attribution is bottom-edge small text (MapLibre 6 starts compact controls EXPANDED)');
  assert.match(mobileBlock, /#weather-basemap \.maplibregl-ctrl-attrib \.maplibregl-ctrl-attrib-inner\{\s*\n\s*display:block !important;font-size:\.52rem\}/,
    'the attribution text always renders small');
  assert.match(mobileBlock, /#weather-basemap \.maplibregl-ctrl-attrib \.maplibregl-ctrl-attrib-button\{display:none !important\}/,
    'the ⓘ expander is retired (small text is always visible)');
  assert.match(mobileBlock, /\.map-wrap \.basemap-status\.ready\{display:none\}/,
    'the ready source badge (MapLibre · OpenFreeMap) leaves the map area');
  const beforeMobile = MAP_CSS.slice(0, MAP_CSS.indexOf('@media (max-width:768px){'));
  assert.ok(!beforeMobile.includes('maplibregl-ctrl-attrib{font-size'),
    'no attribution small-text rule leak outside the mobile block (the ≤720 duplicates retired)');
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
    '.json':'application/json','.png':'image/png','.svg':'image/svg+xml'};
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
    '--window-size=390,844',
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui105cam-')), 'about:blank'],
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

async function loadPage(query = '') {
  await send('Page.enable');
  await send('Page.navigate', {url: baseURL + query});
  await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
  await send('Page.bringToFront');
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.map-panel') && document.querySelector('.wm-ops')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>20000){clearInterval(iv);reject(new Error('app shell never rendered'));}
    },100);
  })`);
}

async function waitCameraSettled(timeoutMs = 60000) {
  return evaljs(`new Promise(resolve=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(window.__weatherGridMap && window.__weatherGridCamera){
        clearInterval(iv);
        // a beat so the load-handler re-fit (preserveCamera path) settles
        setTimeout(()=>resolve(true), 800);
      }
      else if(Date.now()-t0>${timeoutMs}){clearInterval(iv);resolve(false);}
    },250);
  })`);
}

async function realTouchDrag(x0, y0, dx, dy, steps = 6) {
  await send('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [{x: x0, y: y0}]});
  for (let i = 1; i <= steps; ++i) {
    await send('Input.dispatchTouchEvent', {type: 'touchMove',
      touchPoints: [{x: x0 + dx * i / steps, y: y0 + dy * i / steps}]});
  }
  await send('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []});
}

// tw region bbox = 105–145E / 5–40N (weathergrid 規範值)
const CAM_PROBE = `(() => {
  const map=window.__weatherGridMap;
  if(!map) return {ready:false};
  const c=map.getCenter();
  const attr=document.querySelector('.map-wrap .maplibregl-ctrl-attrib');
  const wrap=document.querySelector('.map-wrap').getBoundingClientRect();
  const ar=attr?attr.getBoundingClientRect():null;
  const badge=document.querySelector('.map-wrap .basemap-status');
  return {ready:true, lng:+c.lng.toFixed(3), lat:+c.lat.toFixed(3), zoom:+map.getZoom().toFixed(3),
    inTW: c.lng>=105 && c.lng<=145 && c.lat>=5 && c.lat<=40,
    attr: ar ? {h:Math.round(ar.height), bottomGap:Math.round(wrap.bottom-ar.bottom),
      rightGap:Math.round(wrap.right-ar.right), smallFont:getComputedStyle(attr).fontSize} : null,
    badgeDisp: badge ? getComputedStyle(badge).display : null};
})()`;

const TW_BBOX = {left: 105, right: 145, bottom: 5, top: 40};
const assertCenterInTW = (cam, label) => {
  assert.equal(cam.ready, true, 'MapLibre camera probe ready');
  assert.ok(cam.inTW,
    `${label}: camera center (${cam.lng}, ${cam.lat}) inside the tw bbox 105–145E/5–40N`);
};

test('CL-UI-105 (1a) 390px: initial camera (no params) centers on the tw default bounds — never [0,0]/Africa', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  const ok = await waitCameraSettled();
  assert.ok(ok, 'camera settles');
  const cam = await evaljs(CAM_PROBE);
  assertCenterInTW(cam, 'initial camera');
  assert.ok(cam.zoom >= 1.5, `initial camera zoom keeps the region meaningful (zoom ${cam.zoom})`);
});

test('CL-UI-105 (1b) 390px: after a real fling drag, a fresh reload resets the camera to the tw default', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  await waitCameraSettled();
  // fling the camera far away (no ?spot= in the URL → nothing may persist it)
  const wrap = await evaljs(`(() => { const r=document.querySelector('.map-wrap').getBoundingClientRect();
    return [Math.round(r.left+r.width/2), Math.round(r.top+r.height/2)]; })()`);
  await realTouchDrag(wrap[0], wrap[1], -140, -100);
  await new Promise(r => setTimeout(r, 600));
  const drifted = await evaljs(CAM_PROBE);
  assert.ok(drifted.ready, 'drag moved the map (map pans live)');
  // reload → default tw bounds again (相機狀態不落 URL/localStorage)
  await loadPage();
  const ok = await waitCameraSettled();
  assert.ok(ok, 'camera settles after reload');
  const cam = await evaljs(CAM_PROBE);
  assertCenterInTW(cam, 'reloaded camera');
});

test('CL-UI-105 (1c) 390px: an illegal ?spot= id never moves the camera and is dropped from the URL', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage('?region=tw&spot=xx-999');
  const ok = await waitCameraSettled();
  assert.ok(ok, 'camera settles');
  const cam = await evaljs(CAM_PROBE);
  assertCenterInTW(cam, 'illegal-spot camera');
  // PNG-stub path: the retry runs after the background bundle lands — give it room
  await new Promise(r => setTimeout(r, 2500));
  const url = await evaljs('location.search');
  assert.ok(!/[?&]spot=/.test(url), `spot param dropped from the URL (got ${url})`);
});

test('CL-UI-105 (1d) 390px: a legal ?spot= still brings the spot camera back (CL-WG-19 unchanged)', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  // 知本澆水冰瀑 tw-036 exists in the bundle; the spot view must apply and stay in tw
  await loadPage('?region=tw&spot=tw-036');
  const ok = await waitCameraSettled();
  assert.ok(ok, 'camera settles');
  const dl = await evaljs(`new Promise(resolve=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(window.__weatherGridDeepLink && window.__weatherGridDeepLink.spotId){clearInterval(iv);resolve(window.__weatherGridDeepLink);}
      else if(Date.now()-t0>30000){clearInterval(iv);resolve(null);}
    },250);
  })`);
  assert.ok(dl, 'deep-link entry state published');
  assert.equal(dl.spotId, 'tw-036', 'legal spot id applied');
  const cam = await evaljs(CAM_PROBE);
  assertCenterInTW(cam, 'legal-spot camera');
  const url = await evaljs('location.search');
  assert.ok(/[?&]spot=tw-036/.test(url), 'legal spot param stays in the URL');
});

test('CL-UI-105 (2a) 390px: OpenFreeMap/OpenMapTiles attribution is bottom-edge small text, not a center white box', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  const ok = await waitCameraSettled();
  assert.ok(ok, 'camera settles');
  const cam = await evaljs(CAM_PROBE);
  assert.ok(cam.attr, 'attribution control present');
  assert.ok(cam.attr.h <= 16, `attribution strip is small text (${cam.attr.h}px ≤ 16px)`);
  assert.ok(cam.attr.bottomGap <= 6, `attribution hugs the bottom edge (gap ${cam.attr.bottomGap}px)`);
  assert.ok(cam.attr.rightGap <= 6, `attribution hugs the right edge (gap ${cam.attr.rightGap}px)`);
  assert.ok(parseFloat(cam.attr.smallFont) <= 8.5, `attribution font is small (${cam.attr.smallFont})`);
  assert.equal(cam.badgeDisp, 'none', 'ready source badge (MapLibre · OpenFreeMap) is off the map');
});

test('CL-UI-105 (2e): browser teardown', async () => { await teardownBrowser(); });
