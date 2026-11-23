// CL-UI-105: 手機天氣圖高度重分配（owner 實測：固定版面上線後地圖太小）。
// Contract (mobile shell, <=768px only):
//   (1) 地圖區目標 ≥60% 視高（實測斷言：.map-wrap 高 / innerHeight ≥ 0.60）。
//   (2) 操作區壓扁（總高 ≤180px）：細帶＋預報滑桿合併成一行
//       （左：目前所選細帶／中：滑桿／右：播放鈕）→ 控制列縮為 44px 單行；
//       目前圖層 inspector 預設收合 — 換圖層短暫展開（2.6s flash）或
//       圖層 sheet「詳細」持續展開（sticky）。操作區各項可達。
//   (3) sheet 展開時仍從操作區浮起（不蓋地圖）— 由 CL-UI-104 (4c) 覆蓋，
//       本檔以 display:contents 釘值守住不回歸。
//   (4) 桌面 ≥769 零改動：inspector 照常顯示、prev/next 照常、無收合類別。
// Run: node --test apps/web-v2/tests/cl-ui-105-mobile-ops-compaction.test.mjs
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
// 1. Source pins: CSS compaction + JS inspector collapse + stamps
// ---------------------------------------------------------------------------
test('CL-UI-105 source: cache-bust stamps bumped to bclwg49 in weather-map.html', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg50/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg49/);
});

test('CL-UI-105 CSS: 細帶＋滑桿合併一行；控制列 44px 單行；inspector 預設收合（僅 ≤768）', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  // merged first row: band in column 1, the forecast slider row spans the rest
  assert.match(mobileBlock, /\.wm-ops \.wm-timeline-dock\{order:1;grid-row:1;grid-column:1;/,
    '細帶 occupies the left column of the merged row');
  assert.match(mobileBlock, /\.wm-ops \.time-navigator\{order:2;grid-row:1;grid-column:2\/-1;display:grid;\n\s+grid-template-columns:minmax\(0,1fr\) auto;/,
    '滑桿列 sits in the same grid row as the band, slider+play inside');
  assert.match(mobileBlock, /\.wm-ops \.time-navigator>#time-prev,\.wm-ops \.time-navigator>#time-next,\n\s+\.wm-ops \.time-label,\.wm-ops \.time-navigator \.timeline\{display:none\}/,
    'merged row keeps only 目前所選(細帶)／滑桿／播放 — 標籤刻度與左右步進鈕不佔位');
  // 44px single-row control strip with inline captions
  assert.match(mobileBlock, /\.wm-ops \.control-bar\{order:3;grid-row:2;grid-column:1\/-1;margin-bottom:2px;display:flex;flex-direction:row;\n\s+align-items:center;gap:8px;height:44px;overflow-x:auto;/,
    '控制列 is a 44px single horizontally scrolling row');
  assert.match(mobileBlock, /\.wm-ops \.control-bar>label\{flex:0 0 auto;display:flex;flex-direction:row;align-items:center;/,
    'control captions move inline beside their control');
  assert.match(mobileBlock, /\.wm-ops \.control-bar \#locate-spot\{width:auto;height:38px;margin-top:0\}/,
    '定位景點 stays an in-row control (no full-width hack)');
  // inspector collapsed by default; explicit show state for flash/sticky
  assert.match(mobileBlock, /\.inspector\{display:none\}/);
  assert.match(mobileBlock, /\.inspector\.wm-insp-show\{display:flex;flex:0 1 auto;min-height:0;max-height:26dvh;/);
  // expanded band re-flows the tray grid (JS-synced .wm-dock-open)
  assert.match(mobileBlock, /\.wm-ops\.wm-dock-open \.time-navigator\{grid-row:2;grid-column:1\/-1\}/);
  assert.match(mobileBlock, /\.wm-ops\.wm-dock-open \.control-bar\{grid-row:3\}/);
  // no leak outside the mobile block (1280 zero-change)
  const beforeMobile = MAP_CSS.slice(0, MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.ok(!beforeMobile.includes('wm-insp-show'), 'no inspector collapse leak outside the mobile block');
  assert.ok(!beforeMobile.includes('wm-dock-open'), 'no dock-open re-flow leak outside the mobile block');
  const desktopBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'));
  assert.ok(!desktopBlock.includes('.inspector{display:none'), 'desktop inspector untouched');
});

test('CL-UI-105 JS: inspector 收合 — 換圖層短暫展開（flash）、詳細持續展開（sticky）、桌面清除', () => {
  const helpers = grab(MAP_JS, 'let wmInspFlashTimer=null;', 'function wmFlashInspector(){');
  assert.ok(helpers.includes("insp.classList.toggle('wm-insp-show'"), 'flash toggles .wm-insp-show');
  assert.ok(helpers.includes("insp.classList.toggle('wm-insp-sticky'"), 'sticky toggles .wm-insp-sticky');
  assert.ok(helpers.includes("if(!wmIsMobileShell())"), 'desktop clears the mobile collapse classes');
  assert.match(helpers, /wmInspFlashTimer=setTimeout\(\(\)=>\{[\s\S]*?2600\)/, 'flash auto-hides after 2.6s');
  const flash = grab(MAP_JS, 'function wmFlashInspector(){', '  // DESIGN-10: when the sheet opens');
  assert.ok(flash.includes('if(wmSheetOpen||wmLayerSheetOpen) return;'), 'sheet open → no flash reflow');
  assert.ok(flash.includes("contains('wm-insp-sticky')"), 'sticky state survives layer-change flashes');
  // CL-UI-109 (P2-4): 換圖層不再 flash inspector — 過渡期間版面狀態一致
  // （三個切層入口都不得再呼叫 wmFlashInspector）。
  const selectHook = grab(MAP_JS, "layerSelect.addEventListener('change'", "const opacitySlider=");
  assert.ok(!selectHook.includes('wmFlashInspector();'), 'layer select change → NO flash (CL-UI-109)');
  const sheetChipHook = grab(MAP_JS, 'const chip=e.target.closest(\'[data-wm-layer]\');', 'const row=e.target.closest(\'[data-wm-sheet-spot]\');');
  assert.ok(!sheetChipHook.includes('wmFlashInspector();'), 'layer-sheet chip pick → NO flash (CL-UI-109)');
  assert.ok(!grab(MAP_JS, 'const chips=$(\'layer-chips\');', 'const sideBody=$(\'wm-side-body\');').includes('wmFlashInspector();'),
    'map chips pick → NO flash (CL-UI-109)');
  // 詳細 opens the collapsed inspector persistently
  const details = grab(MAP_JS, '[data-wm-act="layer-details"]', 'const detailsToggle=');
  assert.ok(details.includes('wmInspectorVisible(true,true);'), '詳細 → sticky inspector');
  // band expand syncs the tray re-flow class
  const tlSync = grab(MAP_JS, "tlBar.addEventListener('click'", 'if(wmDockExpanded){');
  assert.ok(tlSync.includes("opsTray.classList.toggle('wm-dock-open'"), 'band expand re-flows the tray grid');
  assert.ok(tlSync.includes('wmIsMobileShell()'), 'dock-open class is mobile-only');
  // desktop resize clears the collapse classes (1280 zero-change)
  assert.ok(MAP_JS.includes('if(!wmIsMobileShell()) wmInspectorVisible(false,false);'),
    'resize to desktop clears the mobile collapse classes');
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
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui105-')), 'about:blank'],
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

const OPS_PROBE = `(() => {
  const $=s=>document.querySelector(s);
  const r=el=>{ if(!el) return null; const b=el.getBoundingClientRect();
    return {t:Math.round(b.top),b:Math.round(b.bottom),l:Math.round(b.left),r:Math.round(b.right),
      h:Math.round(b.height),w:Math.round(b.width)}; };
  const wrap=$('.map-wrap'),ops=$('.wm-ops'),ins=$('.inspector'),dock=$('#wm-timeline-dock'),
        band=$('#wm-tl-bar'),slider=$('#time-slider'),play=$('#time-play'),cb=$('.control-bar'),
        tn=$('.time-navigator');
  // 控制列各項可達：水平捲到最右後，定位鈕完整落在視窗內（死區清除）
  let cbReachable=null;
  if(cb){ cb.scrollLeft=cb.scrollWidth;
    const l=$('#locate-spot'); const rr=l?l.getBoundingClientRect():null;
    cbReachable=!!rr&&rr.right<=window.innerWidth+1&&rr.left>=-1;
    cb.scrollLeft=0; }
  return {
    innerH:window.innerHeight,
    mapH:wrap?Math.round(wrap.getBoundingClientRect().height):null,
    mapPct:wrap?+(wrap.getBoundingClientRect().height/window.innerHeight).toFixed(4):null,
    opsH:ops?Math.round(ops.getBoundingClientRect().height):null,
    inspDisp:ins?getComputedStyle(ins).display:null,
    dockHost:dock?(dock.closest('.wm-ops')?'ops':'wrap'):'none',
    band:r(band), tn:r(tn), slider:r(slider), play:r(play),
    prevDisp:getComputedStyle($('#time-prev')).display,
    nextDisp:getComputedStyle($('#time-next')).display,
    bandLeftOfSlider: band&&slider ? r(band).r <= r(slider).l + 2 : null,
    sliderLeftOfPlay: slider&&play ? r(slider).r <= r(play).l + 2 : null,
    sameRow: band&&tn&&play ? (r(band).b <= r(tn).b + 2 && r(play).t >= r(tn).t && r(play).b <= r(tn).b + 2) : null,
    cbH:cb?Math.round(cb.getBoundingClientRect().height):null,
    cbTop:cb?Math.round(cb.getBoundingClientRect().top):null,
    cbBelowSliderRow: cb&&tn ? r(cb).t >= r(tn).b - 2 : null,
    cbReachable,
    inspClasses: ins ? ins.className : null,
  };
})()`;

// ---- (2a) 390: map ≥60% 視高、操作區 ≤180px、合併行幾何、控制列 44px 可達 ----
test('CL-UI-105 (2a) 390px: map ≥60% viewport; ops ≤180px; merged row + 44px control row reachable', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  const p = await evaljs(OPS_PROBE);
  assert.ok(p.mapPct >= 0.60, `地圖區 ≥60% 視高 (實測 ${(p.mapPct * 100).toFixed(1)}%, ${p.mapH}px / ${p.innerH}px)`);
  assert.ok(p.opsH <= 180, `操作區總高 ≤180px (實測 ${p.opsH}px)`);
  assert.equal(p.inspDisp, 'none', '目前圖層 inspector 預設收合');
  assert.equal(p.dockHost, 'ops', '細帶 lives in the tray');
  // merged row: band left / slider middle / play right, one row
  assert.ok(p.bandLeftOfSlider, '細帶在左（目前所選時刻）');
  assert.ok(p.sliderLeftOfPlay, '滑桿在中、播放鈕在右');
  assert.ok(p.sameRow, '細帶／滑桿／播放 same visual row');
  assert.equal(p.prevDisp, 'none', '左右步進鈕不佔位（滑桿即步進）');
  assert.equal(p.nextDisp, 'none', '左右步進鈕不佔位（滑桿即步進）');
  assert.ok(p.slider.l >= p.tn.l && p.play.r <= p.tn.r, '滑桿與播放鈕都在滑桿列內');
  // 44px single-row control strip, below the merged row, all controls reachable
  assert.ok(p.cbH >= 42 && p.cbH <= 48, `控制列單行 44px (實測 ${p.cbH}px)`);
  assert.ok(p.cbBelowSliderRow, '控制列在合併行下方');
  assert.equal(p.cbReachable, true, '控制列各項水平捲動可達（定位鈕完整在視窗內）');
});

// ---- (2b) 390: 換圖層短暫展開 → 自動收回；詳細 → 持續展開；細帶展開重排 ----
test('CL-UI-105/109 (2b) 390px: layer change does NOT flash the collapsed inspector (CL-UI-109); 詳細 keeps it; band expand re-flows', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  // CL-UI-109 (P2-4): layer change must NOT flash the inspector — the layout
  // state stays consistent during the transition (inspector stays collapsed).
  const flash = await evaljs(`(async () => {
    const sel=document.querySelector('#layer-select');
    const opts=[...sel.options].map(o=>o.value);
    const other=opts.find(v=>v!==sel.value&&v!=='auto');
    if(!other) return {skip:'single layer option'};
    sel.value=other;
    sel.dispatchEvent(new Event('change',{bubbles:true}));
    await new Promise(r=>setTimeout(r,300));
    const ins=document.querySelector('.inspector');
    return {shown:ins.classList.contains('wm-insp-show'),
      disp:getComputedStyle(ins).display,sticky:ins.classList.contains('wm-insp-sticky')};
  })()`);
  if (!flash.skip) {
    assert.equal(flash.shown, false, '換圖層 → inspector 不再短暫展開（CL-UI-109）');
    assert.equal(flash.sticky, false, '切層不帶 sticky');
  }
  // sticky: 圖層 sheet 的「詳細」＝持續展開（使用者明確要求）
  const sticky = await evaljs(`(async () => {
    document.querySelector('#layer-sheet-btn').click();
    await new Promise(r=>setTimeout(r,250));
    document.querySelector('[data-wm-act="layer-details"]').click();
    await new Promise(r=>setTimeout(r,300));
    const ins=document.querySelector('.inspector');
    const lp=document.querySelector('#layer-panel');
    const first={shown:ins.classList.contains('wm-insp-show'),sticky:ins.classList.contains('wm-insp-sticky'),
      disp:getComputedStyle(ins).display,lpVisible:lp.getBoundingClientRect().height>0};
    await new Promise(r=>setTimeout(r,3100));
    return {...first,stillShown:ins.classList.contains('wm-insp-show'),after:getComputedStyle(ins).display};
  })()`);
  assert.equal(sticky.shown, true, '詳細 → inspector 展開');
  assert.equal(sticky.sticky, true, '詳細 → sticky（持續展開）');
  assert.equal(sticky.disp, 'flex', 'sticky 期間 inspector 可見');
  assert.equal(sticky.lpVisible, true, '目前圖層 panel 內容可讀');
  assert.equal(sticky.stillShown, true, 'sticky 不被 2.6s timer 收回');
  assert.equal(sticky.after, 'flex', 'sticky 持續可見');
  // band expand: tray re-flows (full-width band row, slider row below)
  const dock = await evaljs(`(async () => {
    const bar=document.querySelector('#wm-tl-bar');
    bar.click();
    await new Promise(r=>setTimeout(r,250));
    const ops=document.querySelector('.wm-ops'),dk=document.querySelector('#wm-timeline-dock');
    const ro=ops.getBoundingClientRect();
    const out={open:ops.classList.contains('wm-dock-open'),
      dockFull:dk.getBoundingClientRect().width>ro.width-2,
      navRow2:getComputedStyle(document.querySelector('.time-navigator')).gridRowStart};
    bar.click();
    await new Promise(r=>setTimeout(r,200));
    out.reclosed=!ops.classList.contains('wm-dock-open');
    out.opsH=Math.round(ops.getBoundingClientRect().height);
    return out;
  })()`);
  assert.equal(dock.open, true, '細帶展開 → 操作區重排 class');
  assert.equal(dock.dockFull, true, '展開細帶列跨全寬');
  assert.equal(dock.navRow2, '2', '滑桿退到第二列');
  assert.equal(dock.reclosed, true, '收合後 class 同步移除');
  assert.ok(dock.opsH <= 180, `收合後操作區回到 ≤180px (實測 ${dock.opsH}px)`);
});

// ---- (2c) 1280 regression: desktop zero change --------------------------------
test('CL-UI-105 (2c) 1280px: desktop zero change — inspector shown, prev/next kept, no collapse classes', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const d = await evaljs(`(() => {
    const $=s=>document.querySelector(s);
    const cs=el=>getComputedStyle(el);
    return {
      inspDisp:cs($('.inspector')).display,
      inspClasses:$('.inspector').className,
      prevDisp:cs($('#time-prev')).display,
      nextDisp:cs($('#time-next')).display,
      timeLabelDisp:cs($('.time-label')).display,
      tlBarDisp:cs($('#wm-tl-bar')).display,
      opsDisp:cs($('.wm-ops')).display,
      cbLabelDir:cs($('.control-bar label')).flexDirection,
      dockHost:$('#wm-timeline-dock')?( $('#wm-timeline-dock').closest('.map-wrap')?'wrap':'ops'):'none',
    };
  })()`);
  assert.equal(d.inspDisp, 'flex', 'desktop inspector 照常顯示');
  assert.ok(!d.inspClasses.includes('wm-insp-show') && !d.inspClasses.includes('wm-insp-sticky'),
    'desktop carries no collapse classes');
  assert.notEqual(d.prevDisp, 'none', 'desktop prev/next 照常');
  assert.notEqual(d.nextDisp, 'none', 'desktop prev/next 照常');
  assert.notEqual(d.timeLabelDisp, 'none', 'desktop 時刻標籤照常');
  assert.equal(d.tlBarDisp, 'none', 'desktop 無收合細帶');
  assert.equal(d.opsDisp, 'contents', 'desktop .wm-ops 仍為 layout-neutral');
  assert.equal(d.cbLabelDir, 'column', 'desktop 控制列仍為 caption 疊式（零改動）');
  assert.equal(d.dockHost, 'wrap', 'desktop 細帶仍浮在地圖上');
  // desktop layer change must NOT toggle the mobile collapse classes
  const after = await evaljs(`(async () => {
    const sel=document.querySelector('#layer-select');
    const opts=[...sel.options].map(o=>o.value);
    const other=opts.find(v=>v!==sel.value&&v!=='auto');
    if(other){ sel.value=other; sel.dispatchEvent(new Event('change',{bubbles:true})); }
    await new Promise(r=>setTimeout(r,300));
    const ins=document.querySelector('.inspector');
    return {classes:ins.className,disp:getComputedStyle(ins).display};
  })()`);
  assert.ok(!after.classes.includes('wm-insp-show'), 'desktop layer change doesn\'t flash the inspector');
  assert.equal(after.disp, 'flex', 'desktop inspector stays put');
});

test('CL-UI-105 (2d): browser teardown', async () => { await teardownBrowser(); });


// CL-CI-40: release the browser, the CDP socket and the static server even when a
// test aborts or fails. Without a file-level hook the old "teardown" TEST only ran
// if every earlier test completed, so one hang left a Chrome process behind and the
// runner eventually reported the remaining cases as `cancelled` (OOM).
test.after(async () => {
  try { await teardownBrowser(); } catch (_) { /* already gone */ }
});
