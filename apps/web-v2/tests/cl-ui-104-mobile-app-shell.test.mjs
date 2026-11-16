// CL-UI-104: 手機天氣圖改 APP 式固定版面（owner 裁示：地圖固定不隨頁面捲動，
// 其餘空間放操作介面）。
// Contract (mobile shell, <=768px only):
//   (1) 100dvh app layout: the PAGE itself never scrolls (html/body 100dvh +
//       overflow hidden on THIS page only); the top map area (.map-wrap, with
//       the sheet-open preview strip state) is fixed and flex-fills; the fixed
//       operations tray (.wm-ops: 時間軸細帶 → 預報滑桿 → 控制列) and the
//       .inspector (目前圖層) sit below and scroll INTERNALLY, never the page.
//   (2) 「頁面捲動」與「地圖手勢」徹底分離: the page never scrolls (100dvh +
//       overflow hidden) and the map area's gestures are owned by MapLibre's
//       own canvas handler (CL-UI-105: .map-wrap no longer carries
//       touch-action:none — MapLibre's canvas container owns touch-action, so
//       real-device pan/zoom works while the page still cannot scroll).
//   (3) Sheets (列表/圖層/時間軸展開) rise out of the operations area and occupy
//       its height — the map area is never covered (sheet-open re-flows the
//       tray via display:contents: 地圖預覽條 / sheet / 細帶 / 滑桿 各佔各列).
//   (4) Desktop >=769px zero change: the .wm-ops wrapper is layout-neutral
//       (display:contents) and .map-panel flex+order repaints 控制列→地圖→時間軸
//       exactly as before; the dock stays floating inside .map-wrap.
// Run: node --test apps/web-v2/tests/cl-ui-104-mobile-app-shell.test.mjs
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

function grab(src, start, end) {
  const a = src.indexOf(start);
  assert.ok(a !== -1, `source slice start not found: ${start}`);
  const b = src.indexOf(end, a);
  assert.ok(b !== -1, `source slice end not found: ${end}`);
  return src.slice(a, b);
}

// ---------------------------------------------------------------------------
// 1. Markup: the fixed operations tray wraps 控制列 + 預報滑桿 (+ JS-placed 細帶)
// ---------------------------------------------------------------------------
test('CL-UI-104: weather-map.html puts the control bar and time navigator inside the .wm-ops operations tray', () => {
  const tray = grab(WG_HTML, '<div class="wm-ops">', '<!-- /.wm-ops -->');
  assert.ok(tray.includes('class="control-bar"'), '控制列 lives in the tray');
  assert.ok(tray.includes('id="time-slider"'), '預報滑桿 lives in the tray');
  assert.ok(tray.includes('id="time-play"'), '播放 control lives in the tray');
  assert.ok(tray.includes('id="region-switch"'), 'region switch lives in the tray');
  // the tray sits AFTER the two sheets (below the map area in the panel flex column)
  const panel = grab(WG_HTML, '<section class="map-panel">', '</section>\n\n    <aside class="inspector">');
  assert.ok(panel.indexOf('class="map-wrap"') < panel.indexOf('class="wm-ops"'), 'map area precedes the tray');
  assert.ok(panel.indexOf('id="wm-sheet"') < panel.indexOf('class="wm-ops"'), 'list sheet is a panel flex sibling');
});

test('CL-UI-104: cache-bust stamps bumped to bclwg45 in weather-map.html', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg45/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg45/);
  assert.ok(!/weather-map\.(js|css)\?v=bclwg41/.test(WG_HTML), 'old stamp must not linger');
});

// ---------------------------------------------------------------------------
// 2. CSS: 100dvh app shell — page never scrolls, map area fixed, tray fixed
// ---------------------------------------------------------------------------
test('CL-UI-104 CSS (mobile): 100dvh shell — body overflow hidden, flex column, map area flex-fills', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /html,body\{height:100dvh;overflow:hidden;overscroll-behavior:none\}/,
    'the page itself never scrolls on this page at this breakpoint');
  assert.match(mobileBlock, /body\{display:flex;flex-direction:column\}/);
  assert.match(mobileBlock, /\.map-panel\{flex:1 1 0;min-height:0;display:flex;flex-direction:column;overflow:hidden\}/);
  assert.match(mobileBlock, /\.map-wrap\{order:0;flex:1 1 0;min-height:120px;aspect-ratio:auto\}/,
    'the fixed map area flex-fills (touch-action owned by the MapLibre canvas, not the wrapper)');
  assert.match(mobileBlock, /\.map-wrap \.maplibregl-canvas-container,\.map-wrap #weather-canvas\{touch-action:none\}/,
    'CL-UI-105: MapLibre canvas container + overlay canvas own the gestures (pan/zoom live, page cannot scroll)');
  // CL-UI-105 re-anchor: the tray is a compact grid — merged band+slider row,
  // then a 44px single-row control strip (total ops height target ≤180px).
  assert.match(mobileBlock, /\.wm-ops\{order:1;flex:0 1 auto;min-height:0;max-height:47dvh;display:grid/);
  assert.match(mobileBlock, /grid-template-columns:auto minmax\(0,1fr\) auto;grid-auto-rows:min-content/,
    'the tray is a compact grid (merged row + control row)');
  assert.match(mobileBlock, /overflow-y:auto;overscroll-behavior:contain;touch-action:pan-y\}/,
    'the tray scrolls internally, never the page');
  assert.match(mobileBlock, /\.wm-ops \.wm-timeline-dock\{order:1;grid-row:1;grid-column:1;position:static;inset:auto;min-width:0\}/,
    'the timeline band is a flow row of the tray (not floating over the map)');
  assert.match(mobileBlock, /\.wm-ops \.time-navigator\{order:2;grid-row:1;grid-column:2\/-1;display:grid/,
    '細帶與滑桿 share the first merged row (band left / slider right)');
  assert.match(mobileBlock, /\.wm-ops \.control-bar\{order:3;grid-row:2;grid-column:1\/-1;margin-bottom:2px;display:flex;flex-direction:row/,
    '控制列 becomes a 44px single-row horizontally scrolling strip');
  assert.match(mobileBlock, /height:44px;overflow-x:auto/, '控制列 row height is 44px');
  // CL-UI-105: 目前圖層 inspector collapsed by default on mobile; shown only via
  // the layer-change flash (.wm-insp-show) or the layer-sheet 詳細 sticky.
  assert.match(mobileBlock, /\.inspector\{display:none\}/,
    '目前圖層 panel is collapsed by default on the mobile shell');
  assert.match(mobileBlock, /\.inspector\.wm-insp-show\{display:flex/,
    'the collapsed inspector has an explicit show state for flash/sticky');
  // the shell chrome must not leak outside the mobile block (1280 zero-change)
  const beforeMobile = MAP_CSS.slice(0, MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.ok(!beforeMobile.includes('100dvh'), 'no app-shell height/overflow leak outside the mobile block');
  assert.ok(!/\.wm-ops\{/.test(beforeMobile), 'no .wm-ops rule leak outside the mobile block');
});

test('CL-UI-104 CSS (mobile): sheets rise out of the operations area — tray re-flows, map never covered', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /\.map-panel\.sheet-open \.wm-ops\{display:contents\}/,
    'sheet-open promotes the tray rows into the panel flex column');
  assert.match(mobileBlock, /\.map-panel\.sheet-open \.wm-timeline-dock\{order:2\}/, '細帶 below the sheet');
  assert.match(mobileBlock, /\.map-panel\.sheet-open \.time-navigator\{order:3;padding-top:8px\}/, '滑桿 below the band');
  assert.match(mobileBlock, /#wm-sheet,#wm-layer-sheet\{order:1\}/, 'sheets take the tray place (order 1, above the map strip)');
});

test('CL-UI-104 CSS (desktop): the .wm-ops wrapper is layout-neutral and map-panel repaints the original order', () => {
  const desktopBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'));
  assert.match(desktopBlock, /\.map-panel\{display:flex;flex-direction:column\}/);
  assert.match(desktopBlock, /\.wm-ops\{display:contents\}/, 'tray wrapper vanishes from desktop layout');
  assert.match(desktopBlock, /\.map-panel \.control-bar\{order:-1\}/, '控制列 paints above the map as before');
});

// ---------------------------------------------------------------------------
// 3. JS: shell-driven dock placement; no pixel-height stage fitting
// ---------------------------------------------------------------------------
test('CL-UI-104 JS: dock placement is shell-driven (tray on mobile, map overlay on desktop)', () => {
  const place = grab(MAP_JS, 'function wmPlaceDockForShell()', 'function wmRelocateDockForSheet(');
  assert.ok(place.includes("wmIsMobileShell()"), 'placement branches on the mobile shell');
  assert.ok(place.includes("ops.insertBefore(dock,tn)"), 'mobile: dock joins the tray before the slider');
  assert.ok(place.includes("wrap.insertBefore(dock,$('wm-mini'))"), 'desktop: dock returns into the map overlay');
  const relocate = grab(MAP_JS, 'function wmRelocateDockForSheet(', 'function wmFitSheetPanel(');
  assert.ok(relocate.includes('wmPlaceDockForShell()'), 'sheet open/close keeps the shell-driven placement');
  const fit = grab(MAP_JS, 'function wmFitSheetPanel()', 'function wmOpenSheet(');
  assert.ok(fit.includes("panel.style.height=''"), 'flex shell owns the panel height — no pixel stage fit');
  assert.ok(!fit.includes('Math.round(h)'), 'the old pixel-height fit is gone');
  const init = grab(MAP_JS, 'function wmInitOverlays()', '// ── renderAll 掛鉤');
  assert.ok(init.includes('wmPlaceDockForShell();'), 'placement runs at overlay init');
  assert.ok(MAP_JS.includes("wmPlaceDockForShell();\n    wmFitSheetPanel();"), 'resize re-places the dock when the shell flips');
});

// ---------------------------------------------------------------------------
// 4. Real-browser probes (lazy boot — never a root test.before)
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
      // CL-UI-109: newer Chrome headless needs software WebGL for the MapLibre LIVE probes
      '--enable-unsafe-swiftshader','--use-angle=swiftshader',
    '--no-first-run','--remote-debugging-port=0',
    '--window-size=1280,900',
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui104-')), 'about:blank'],
    {stdio: ['ignore', 'ignore', 'pipe']});
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = '';
    // event-loop-aware wait (CL-UI-90 pattern): only unblocked wall-clock time
    // counts toward the spawn deadline under --test-isolation=none.
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
    (async () => { await new Promise(r => server?.close(r)); })()
  ]);
}

async function setViewport(width, height, mobile) {
  await send('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor: 1, mobile});
}

async function loadPage() {
  await send('Page.enable');
  await send('Page.navigate', {url: baseURL});
  // CL-APP-06 race guard: only trust the DOM after a NEW load event for THIS navigation.
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

async function waitMapReady(timeoutMs = 60000) {
  return evaljs(`new Promise(resolve=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(window.__weatherGridMap){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>${timeoutMs}){clearInterval(iv);resolve(false);}
    },250);
  })`);
}

const LAYOUT_PROBE = `(() => {
  const $=s=>document.querySelector(s);
  const cs=el=>getComputedStyle(el);
  const r=el=>{ if(!el) return null; const b=el.getBoundingClientRect();
    return {t:Math.round(b.top),b:Math.round(b.bottom),h:Math.round(b.height),l:Math.round(b.left),r:Math.round(b.right)}; };
  const wrap=$('.map-wrap'), ops=$('.wm-ops'), panel=$('.map-panel'), ins=$('.inspector'),
        slider=$('#time-slider'), cb=$('.control-bar'), dock=$('#wm-timeline-dock');
  if(!wrap||!ops||!panel||!ins||!slider||!cb) return {error:'missing shell element'};
  return {
    innerH:window.innerHeight,
    docScrollH:document.documentElement.scrollHeight,
    bodyOverflowY:cs(document.body).overflowY,
    scrollY:window.scrollY,
    map:r(wrap), mapTouchAction:wrap?cs(wrap.querySelector('.maplibregl-canvas-container')||wrap).touchAction:cs(wrap).touchAction,
    ops:r(ops), opsOverflowY:cs(ops).overflowY,
    opsScrollable:ops.scrollHeight>ops.clientHeight,
    panel:r(panel), insp:r(ins),
    slider:r(slider), cb:r(cb),
    dockHost:dock ? (dock.closest('.wm-ops')?'ops':(dock.closest('.map-wrap')?'wrap':'other')) : 'none',
    footer:r($('.site-footer')),
    header:r($('.weather-header')),
    navPos:cs($('.site-nav')).position,
    sheetBtn:r($('#side-toggle')),
    layerPill:r($('#layer-sheet-btn')),
  };
})()`;

const SHEET_PROBE = `(() => {
  const $=s=>document.querySelector(s);
  const r=el=>{ if(!el) return null; const b=el.getBoundingClientRect();
    return {t:Math.round(b.top),b:Math.round(b.bottom),h:Math.round(b.height)}; };
  const wrap=$('.map-wrap'), sheet=$('#wm-sheet'), lsheet=$('#wm-layer-sheet'),
        dim=$('#wm-map-dim'), panel=$('.map-panel'), dock=$('#wm-timeline-dock');
  const vis=el=>!!el && el.getBoundingClientRect().height>0;
  return {
    sheetOpen:panel.classList.contains('sheet-open'),
    listVisible:vis(sheet), layerVisible:vis(lsheet),
    dimShown:!dim.hidden,
    mapH:r(wrap).h, list:r(sheet), layer:r(lsheet),
    sheetBelowStrip: vis(sheet) ? r(sheet).t >= r(wrap).b - 2 : null,
    layerBelowStrip: vis(lsheet) ? r(lsheet).t >= r(wrap).b - 2 : null,
    opsDisplay:getComputedStyle($('.wm-ops')).display,
    dockStillVisible: vis(dock),
    listBtnVisible: vis($('#side-toggle')),
    pillVisible: vis($('#layer-sheet-btn')),
  };
})()`;

const BAND_PROBE = `(() => {
  const $=s=>document.querySelector(s);
  const r=el=>{ if(!el) return null; const b=el.getBoundingClientRect();
    return {t:Math.round(b.top),b:Math.round(b.bottom),h:Math.round(b.height)}; };
  const dock=$('#wm-timeline-dock'), dayRow=$('#wm-day-row'), wrap=$('.map-wrap'), ops=$('.wm-ops');
  return {
    expanded:dock.classList.contains('expanded'),
    dayVisible:dayRow.getBoundingClientRect().height>0,
    dayTop:r(dayRow).t, mapBottom:r(wrap).b,
    dayBelowMap: r(dayRow).t >= r(wrap).b - 2,
    dockInOps:!!dock.closest('.wm-ops'),
    barTop:r($('#wm-tl-bar')).t,
  };
})()`;

async function realClickAt(cx, cy) {
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', {type, x: cx, y: cy, button: 'left', clickCount: 1});
  }
}

async function realTouchDrag(x0, y0, dx, dy, steps = 6) {
  await send('Input.dispatchTouchEvent', {type: 'touchStart', touchPoints: [{x: x0, y: y0}]});
  for (let i = 1; i <= steps; ++i) {
    await send('Input.dispatchTouchEvent', {type: 'touchMove',
      touchPoints: [{x: x0 + dx * i / steps, y: y0 + dy * i / steps}]});
  }
  await send('Input.dispatchTouchEvent', {type: 'touchEnd', touchPoints: []});
}

const centerExpr = `(window.__weatherGridMap
  ? [window.__weatherGridMap.getCenter().lng, window.__weatherGridMap.getCenter().lat]
  : null)`;

// ---- (4a) mobile 390: the page never scrolls; the shell is fixed ------------
for (const vp of [{name: 'mobile 390px', w: 390, h: 844, mobile: true, tag: '390'}]) {
  test(`CL-UI-104 (4a) ${vp.name}: page never scrolls; map area fixed on top; ops tray + inspector fixed below`, async () => {
    await bootBrowser();
    await setViewport(vp.w, vp.h, vp.mobile);
    await loadPage();
    const p = await evaljs(LAYOUT_PROBE);
    assert.equal(p.error, undefined, 'shell elements present');
    assert.equal(p.bodyOverflowY, 'hidden', 'body overflow hidden — the page itself cannot scroll');
    assert.ok(p.docScrollH <= p.innerH + 1, `document never overflows the viewport (scrollH ${p.docScrollH} vs ${p.innerH})`);
    assert.equal(p.scrollY, 0, 'page stays at scroll 0');
    // CL-UI-105: gestures are owned by the MapLibre canvas container — wait for
    // the basemap to boot so the computed touch-action is meaningful here.
    const mapTouch = await evaljs(`new Promise(resolve=>{
      const t0=Date.now();
      const iv=setInterval(()=>{
        const cc=document.querySelector('.map-wrap .maplibregl-canvas-container');
        if(cc){clearInterval(iv);resolve(getComputedStyle(cc).touchAction);}
        else if(Date.now()-t0>20000){clearInterval(iv);resolve('no-canvas');}
      },200);
    })`);
    assert.equal(mapTouch, 'none', 'map gestures are owned by the MapLibre canvas container (touch-action:none — pan/zoom live, page cannot scroll)');
    assert.ok(p.map.h >= 0.28 * p.innerH, `map area keeps a substantial fixed slice (${p.map.h}px)`);
    assert.ok(p.map.b <= p.ops.t + 1, 'map area sits fully above the operations tray');
    // CL-UI-105: the inspector is collapsed by default on mobile — the tray
    // runs down to the page bottom (CL-UI-106: no footer block below it) and
    // 目前圖層 reserves no viewport height.
    assert.equal(p.insp.h, 0, 'inspector collapsed by default (no reserved slice)');
    assert.equal(p.footer.h, 0, 'CL-UI-106: site-footer retired on the mobile shell (sources.html covers it)');
    assert.ok(p.ops.b <= p.innerH + 1, 'tray sits above the bottom edge (no footer block below)');
    assert.ok(p.ops.h <= 180, `operations tray stays within the 180px budget (${p.ops.h}px)`);
    assert.equal(p.dockHost, 'ops', 'timeline band lives in the operations tray (not floating over the map)');
    assert.ok(p.slider.t >= p.map.b - 2 && p.slider.b <= p.innerH, '預報滑桿 is reachable in the fixed tray');
    // attempts to scroll the page must be no-ops (both directions)
    const still = await evaljs(`window.scrollTo(0,600); new Promise(r=>setTimeout(()=>r(window.scrollY),150))`);
    assert.equal(still, 0, 'window.scrollTo cannot move the page');
    // tray reachability: the control strip scrolls INTERNALLY, controls reachable
    // CL-UI-105 (owner): 地區選擇 is the single-row dropdown now; the five big
    // cards are retired on mobile and the dropdown leads the control row.
    const reach = await evaljs(`(() => {
      const ops=document.querySelector('.wm-ops');
      ops.scrollTop=ops.scrollHeight;
      const sel=document.querySelector('#region-select');
      const cards=document.querySelector('.region-switch');
      const rc=sel.getBoundingClientRect();
      return {scrolled:ops.scrollTop, regionIn:rc.top>=0 && rc.bottom<=window.innerHeight,
        regionW:Math.round(rc.width), cardsHidden:getComputedStyle(cards).display==='none',
        cardCount:cards.querySelectorAll('.region-card').length};
    })()`);
    assert.ok(reach.regionIn, '地區下拉 reachable in the fixed tray');
    assert.ok(reach.regionW >= 100, `地區下拉 is a usable single-row dropdown (${reach.regionW}px)`);
    assert.equal(reach.cardsHidden, true, '五大卡 retired on mobile (dropdown replaces them)');
    assert.equal(reach.cardCount, 5, 'card row still rendered for desktop (hidden, not removed)');
    await evaljs(`document.querySelector('.wm-ops').scrollTop=0`);
  });
}

// ---- (4b) mobile 390: map gestures vs page scroll separation ----------------
test('CL-UI-104 (4b) 390px: a real touch drag on the map pans the map and never scrolls the page', async (t) => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  await send('Page.bringToFront');
  const dataReady = await waitDataReady();
  assert.ok(dataReady, 'local weathergrid data loads (preview ready)');
  const mapReady = await waitMapReady();
  assert.ok(mapReady, 'MapLibre basemap ready (__weatherGridMap present)');
  const p = await evaljs(LAYOUT_PROBE);
  const cx = (p.map.l + p.map.r) / 2, cy = (p.map.t + p.map.b) / 2;
  const before = await evaljs(centerExpr);
  assert.ok(before, 'MapLibre basemap ready (__weatherGridMap present)');
  await realTouchDrag(cx, cy, -90, -60);
  await new Promise(r => setTimeout(r, 500));
  const after = await evaljs(centerExpr);
  const moved = Math.abs(after[0] - before[0]) + Math.abs(after[1] - before[1]);
  assert.ok(moved > 0.01, `map pan gesture moves the camera (Δ=${moved.toFixed(4)}°)`);
  const p2 = await evaljs(LAYOUT_PROBE);
  assert.equal(p2.scrollY, 0, 'the same drag never scrolls the page');
  assert.equal(p2.bodyOverflowY, 'hidden');
});

// ---- (4c) mobile 390: CL-UI-105 (owner) 景點列表入口 removed from the shell ----
test('CL-UI-104 (4c) 390px: 景點列表 entry is removed from the ops shell (spot pins keep the mini card)', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  await send('Page.bringToFront');
  await waitDataReady();
  const p = await evaljs(LAYOUT_PROBE);
  // the entry pill is gone (display:none), the layer pill stays
  assert.ok(p.sheetBtn.h === 0, `景點列表 pill hidden (${p.sheetBtn.h}px)`);
  assert.ok(p.layerPill.h > 0, '攝影圖層 pill stays reachable');
  // the list sheet is therefore unreachable on the mobile shell: no sheet-open
  // shell state and no dim on a fresh load
  const s = await evaljs(SHEET_PROBE);
  assert.equal(s.sheetOpen, false, 'no sheet-open shell state without an entry');
  assert.equal(s.dimShown, false, 'no dim on a fresh load');
  // the sheet DOM stays (desktop markup untouched); only the entry is removed
  const markup = await evaljs(`(() => ({sheet:!!document.querySelector('#wm-sheet'),
    mini:!!document.querySelector('#wm-mini')}))()`);
  assert.equal(markup.sheet, true, '#wm-sheet markup retained (entry-only removal)');
});

test('CL-UI-104 (4c2) 390px: layer sheet + timeline band expand stay below the map area', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  await send('Page.bringToFront');
  await waitDataReady();
  const p = await evaljs(LAYOUT_PROBE);
  await realClickAt(Math.round((p.layerPill.l + p.layerPill.r) / 2), Math.round((p.layerPill.t + p.layerPill.b) / 2));
  await new Promise(r => setTimeout(r, 400));
  let s = await evaljs(SHEET_PROBE);
  assert.equal(s.sheetOpen, true, 'layer sheet opens in the shared shell');
  assert.equal(s.layerVisible, true, 'layer sheet visible');
  assert.ok(s.layerBelowStrip, 'layer sheet never covers the map area');
  const closeBtn = await evaljs(`(() => { const b=document.querySelector('#wm-layer-sheet .x');
    const r=b.getBoundingClientRect(); return [Math.round(r.left+r.width/2), Math.round(r.top+r.height/2)]; })()`);
  await realClickAt(closeBtn[0], closeBtn[1]);
  await new Promise(r => setTimeout(r, 300));
  // 時間軸展開: band grows inside the fixed tray, rows stay below the map
  const barCenter = await evaljs(`(() => { const b=document.querySelector('#wm-tl-bar');
    const r=b.getBoundingClientRect(); return [Math.round(r.left+r.width/2), Math.round(r.top+r.height/2)]; })()`);
  await realClickAt(barCenter[0], barCenter[1]);
  await new Promise(r => setTimeout(r, 400));
  const band = await evaljs(BAND_PROBE);
  assert.equal(band.expanded, true, 'band expands in place');
  assert.equal(band.dayVisible, true, 'day/hour rows render');
  assert.equal(band.dayBelowMap, true, 'expanded band rows never cover the map area');
  assert.equal(band.dockInOps, true, 'band stays in the operations tray');
});

// ---- (4d) desktop 1280 regression ------------------------------------------
for (const vp of [{name: 'desktop 1280px', w: 1280, h: 900, mobile: false}]) {
  test(`CL-UI-104 (4d) ${vp.name}: zero change — 控制列→地圖→時間軸 order, dock floats over the map, page scrolls normally`, async () => {
    await bootBrowser();
    await setViewport(vp.w, vp.h, vp.mobile);
    await loadPage();
    const p = await evaljs(LAYOUT_PROBE);
    assert.equal(p.error, undefined);
    assert.notEqual(p.bodyOverflowY, 'hidden', 'desktop body is NOT overflow hidden');
    assert.equal(p.opsOverflowY, 'visible', '.wm-ops is layout-neutral on desktop');
    assert.equal(p.dockHost, 'wrap', 'desktop dock stays inside .map-wrap (floating overlay)');
    assert.ok(p.cb.b <= p.map.t + 1, '控制列 paints ABOVE the map exactly as before');
    assert.ok(p.map.b <= p.slider.t + 1, '時間軸滑桿 paints BELOW the map exactly as before');
    const sheets = await evaljs(`(() => {
      const cs=getComputedStyle;
      return {sheet:cs(document.querySelector('#wm-sheet')).display,
              dim:cs(document.querySelector('#wm-map-dim')).display,
              tlBar:cs(document.querySelector('#wm-tl-bar')).display};
    })()`);
    assert.equal(sheets.sheet, 'none', 'no sheet chrome on desktop');
    assert.equal(sheets.dim, 'none', 'no dim on desktop');
    assert.equal(sheets.tlBar, 'none', 'no collapsed band on desktop');
    // dock floats over the map bottom inside .map-wrap
    const dock = await evaljs(`(() => { const d=document.querySelector('#wm-timeline-dock');
      if(!d||d.hidden) return {hidden:true};
      const w=document.querySelector('.map-wrap').getBoundingClientRect(), r=d.getBoundingClientRect();
      return {hidden:false, top:Math.round(r.top), bottom:Math.round(r.bottom),
              mapTop:Math.round(w.top), mapBottom:Math.round(w.bottom)}; })()`);
    if (!dock.hidden) {
      assert.ok(dock.top >= dock.mapTop && dock.bottom <= dock.mapBottom + 2, 'dock overlay stays inside the map area');
    }
  });
}

test('CL-UI-104 (4e): browser teardown', async () => { await teardownBrowser(); });
