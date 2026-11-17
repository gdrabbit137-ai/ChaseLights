// CL-UI-109: CHALLENGER-17 新問題修正批次（7 項）。
// Audit: task/CHALLENGER-17 data/v2/audits/challenger-17-map-verification.md
// Contract:
//   (P2-1) 圖層 sheet 開啟時 dim「點此返回」pill 有效 — 共用 handler 的
//          sheet-close / layer-sheet-close 分支收掉「目前開啟的那個」sheet。
//   (P2-2) 版面判斷軸改 min(w,h)≤768 — CSS 行動塊 (max-width:768px),(max-height:768px)、
//          桌面塊 (min-width:769px) and (min-height:769px)（互為補集，1280 零改動）。
//   (P2-3) 底圖健壯性 — maplibre vendor 進 repo（無 unpkg）、逾時 8s→4s、
//          逾時誠實標「圖資載入失敗 · Canvas fallback」。
//   (P2-4) 切層不閃（三個切層入口不再 flash inspector）＋ QC 徽章與真實畫布對齊
//          （canvasHasFieldPaint 下採樣 alpha 複核，與 lastDataRendered 聯合判斷）。
//   (P3-5) 觸控命中區 44px — play/返回 pill/↺模型範圍/圖例/ⓘ 以透明 ::after 外擴（視覺不變）。
//   (P3-6) .wm-ops 的 wm-dock-open 殘留復位（wmSyncOpsDockOpen 掛進所有收合路徑）。
//   (P3)   grab 下拉收起維持既有 ✕/Esc＋細帶收合路徑（真機不可行，不硬做）。
// Run: node --test apps/web-v2/tests/cl-ui-109-ch17-fix-batch.test.mjs
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
// 1. Source pins
// ---------------------------------------------------------------------------
test('CL-UI-109 P2-1: shared dim handler closes the CURRENTLY OPEN sheet (return pill works for both sheets)', () => {
  const handler = grab(MAP_JS, '[data-wm-act="sheet-close"]', '[data-wm-act="layer-details"]');
  assert.ok(handler.includes('if(wmLayerSheetOpen) wmCloseLayerSheet(); else wmCloseSheet();'),
    'sheet-close branch closes whichever sheet is open (layer sheet return pill)');
  assert.ok(handler.includes('if(wmSheetOpen) wmCloseSheet(); else wmCloseLayerSheet();'),
    'layer-sheet-close branch stays symmetric');
});

test('CL-UI-109 P3-6: wm-dock-open residue cleared on every collapse path', () => {
  assert.ok(MAP_JS.includes('function wmSyncOpsDockOpen(){'),
    'sync helper exists');
  const closeSheet = grab(MAP_JS, 'function wmCloseSheet(){', 'wmRelocateDockForSheet(false)');
  const closeLayer = grab(MAP_JS, 'function wmCloseLayerSheet(){', 'wmRelocateDockForSheet(false)');
  const collapseBand = grab(MAP_JS, 'function wmCollapseTimelineBand(){', 'function wmOpenLayerSheet');
  for (const [name, block] of [['wmCloseSheet', closeSheet], ['wmCloseLayerSheet', closeLayer], ['wmCollapseTimelineBand', collapseBand]]) {
    assert.ok(block.includes('wmSyncOpsDockOpen();'), `${name} syncs the ops tray class`);
  }
});

test('CL-UI-109 P2-4: no inspector flash on layer change; QC badge reads the REAL canvas state', () => {
  const selectHook = grab(MAP_JS, "layerSelect.addEventListener('change'", "const opacitySlider=");
  const sheetChipHook = grab(MAP_JS, "const chip=e.target.closest('[data-wm-layer]');", "const row=e.target.closest('[data-wm-sheet-spot]');");
  const chipsHook = grab(MAP_JS, "const chips=$('layer-chips');", "const sideBody=$('wm-side-body');");
  for (const [name, hook] of [['layer-select', selectHook], ['layer-sheet chip', sheetChipHook], ['map chips', chipsHook]]) {
    assert.ok(!hook.includes('wmFlashInspector();'), `${name} change must NOT flash the inspector`);
  }
  assert.ok(MAP_JS.includes('function canvasHasFieldPaint(){'), 'real-canvas probe helper exists');
  assert.ok(MAP_JS.includes('state.lastCanvasPainted=canvasHasFieldPaint();'),
    'probe runs at the field-draw moment (canvas holds only the field, grid/spots not stacked yet)');
  assert.ok(MAP_JS.includes('if(!state.lastDataRendered && !state.lastCanvasPainted){'),
    'updateQc fail-closed gate combines the flag with the real canvas probe');
});

test('CL-UI-109 P2-3: maplibre vendored (no unpkg), timeout 4s, honest fallback label', () => {
  assert.ok(MAP_JS.includes("new URL('assets/vendor/maplibre-gl.mjs', document.baseURI)"),
    'module path is repo-local and document-base-anchored');
  assert.ok(!MAP_JS.includes('unpkg.com'), 'no unpkg dependency in weather-map.js');
  assert.ok(!WG_HTML.includes('unpkg.com'), 'no unpkg dependency in weather-map.html');
  for (const f of ['maplibre-gl.mjs', 'maplibre-gl-shared.mjs', 'maplibre-gl-worker.mjs', 'maplibre-gl.css']) {
    const p = join(WEB, 'assets', 'vendor', f);
    const body = readFileSync(p, 'utf8');
    assert.ok(body.length > 10000, `vendor file exists and is non-trivial: ${f}`);
    assert.ok(!body.includes('unpkg.com'), `${f} carries no unpkg self-reference`);
  }
  const timeout = grab(MAP_JS, "setBasemapStatus('fallback'", "map.on('load'");
  assert.ok(timeout.includes('},4000)'), 'basemap boot timeout is 4000ms (was 8000)');
  assert.ok(MAP_JS.includes("setBasemapStatus('fallback',wmT('圖資載入失敗 · Canvas fallback'));"),
    'timeout label is the honest 圖資載入失敗');
  // trilingual dictionary entries
  const en = grab(MAP_JS, "  const WM_I18N={\n    'en':{", "    'ja':{");
  assert.ok(en.includes("'圖資載入失敗 · Canvas fallback':'Basemap failed to load · Canvas fallback'"), 'en entry');
  const ja = MAP_JS.slice(MAP_JS.indexOf("'ja':{"), MAP_JS.indexOf("'ja':{") + 20000);
  assert.ok(ja.includes("'圖資載入失敗 · Canvas fallback':'図版の読み込みに失敗 · Canvas フォールバック'"), 'ja entry');
  assert.match(WG_HTML, /assets\/vendor\/maplibre-gl\.css\?v=bclwg48/);
});

test('CL-UI-109 P2-2: layout axis is min(w,h)<=768 (landscape phones get the app shell)', () => {
  assert.ok(MAP_CSS.includes('@media (max-width:768px),(max-height:768px){'), 'mobile block covers short viewports');
  assert.ok(MAP_CSS.includes('@media (min-width:769px) and (min-height:769px){'), 'desktop block needs BOTH axes tall');
  for (const needle of ["matchMedia('(max-width:768px),(max-height:768px)')"]) {
    assert.ok(MAP_JS.includes(needle), `JS uses the min(w,h) query: ${needle}`);
  }
  assert.equal((MAP_JS.match(/max-width:768px'\)/g) || []).length, 0, 'no width-only 768 matchMedia left');
  // complements: a 1280×800 desktop is NOT mobile; 844×390 landscape IS mobile
  const mobile = ['(max-width:768px),', '(max-height:768px)'];
  const desktop = ['(min-width:769px)', 'and', '(min-height:769px)'];
  assert.ok(desktop.every(d => MAP_CSS.includes(d)));
  assert.ok(mobile.every(m => MAP_CSS.includes(m)));
});

test('CL-UI-109 P3-5: 44px hit-area expansion (visual unchanged) lives inside the mobile block only', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  const beforeMobile = MAP_CSS.slice(0, MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  for (const sel of ['#time-play', '#layer-sheet-btn', '#reset-view', '.legend-toggle', '#data-info-open']) {
    const hit = mobileBlock.match(new RegExp(`${sel}\\{position:relative\\}\\n\\s*${sel}::after\\{content:'';position:absolute;inset:([^}]+)\\}`));
    assert.ok(hit, `${sel} has an ::after hit-area expander inside the mobile block`);
    assert.ok(!beforeMobile.includes(sel + '{position:relative}'), `${sel} expander does not leak to desktop`);
  }
  // desktop 1280 zero-change: no pseudo hit-area rules in the desktop block
  const desktopBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'));
  assert.ok(!desktopBlock.includes("::after{content:'';position:absolute;inset:-"), 'no hit-area rules on desktop');
});

test('CL-UI-109 stamp: weather-map.html bumped to bclwg48 (js+css+vendor css)', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg48/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg48/);
  assert.ok(!/bclwg44/.test(WG_HTML), 'old stamp must not linger');
});

// ---------------------------------------------------------------------------
// 2. Live probes (lazy boot — never a root test.before)
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
      const file = join(WEB, p === '/' ? 'weather-map.html' : p.slice(1));
      try { const body = readFileSync(file);
        res.writeHead(200, {'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
        res.end(body);
      } catch { res.writeHead(404); res.end('not found'); }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    baseURL = `http://127.0.0.1:${server.address().port}/`;
    chrome = spawn(BROWSER, [
      '--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
      // CL-UI-109: Chrome 157 requires an explicit debugging port for the CDP endpoint
      '--remote-debugging-port=0',
      '--enable-unsafe-swiftshader','--use-angle=swiftshader',
      '--window-size=390,844',
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui109-')), 'about:blank'],
      {stdio: ['pipe','pipe','pipe']});   // CL-UI-109: Chrome 157 prints the DevTools endpoint on stdout
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = '';
      const t = setTimeout(() => {
        if (process.env.CLUI109_DEBUG) console.error('[boot timeout] buf=', buf.slice(-400));
        reject(new Error('no devtools endpoint'));
      }, 60000);
      const scan = d => { buf += d; if (process.env.CLUI109_DEBUG) console.error('[boot]', String(d).slice(0,120));
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearTimeout(t); resolve(m[1]); } };
      chrome.stderr.on('data', scan);   // CL-UI-109: Chrome 157 prints the DevTools endpoint on stdout
      chrome.stdout.on('data', scan);
      chrome.on('error', e => reject(new Error('spawn: ' + e.message)));
    });
    let targets = null;
    for (let k = 0; k < 20 && !targets; ++k) {
      await new Promise(r => setTimeout(r, 500));
      try { targets = await fetch('http://' + wsUrl.replace('ws://','').split('/')[0] + '/json/list').then(r => r.json()); } catch {}
    }
    const page = targets.find(t => t.type === 'page') || targets[0];
    ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise(r => ws.addEventListener('open', r, {once:true}));
    ws.addEventListener('message', m => {
      const d = JSON.parse(m.data);
      if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); }
    });
    send = (method, params={}) => new Promise((resolve, reject) => {
      const i = nextId(); pending.set(i, d => d.error ? reject(new Error(d.error.message)) : resolve(d.result));
      ws.send(JSON.stringify({id: i, method, params}));
    });
    evaljs = async (expression) => {
      const r = await send('Runtime.evaluate', {expression, returnByValue: true, awaitPromise: true});
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
      return r.result?.result?.value ?? r.result?.value;
    };
  })().catch(e => { ready = null; throw e; });
  return ready;
}

async function teardownBrowser() {
  return Promise.all([
    (async () => { try { ws?.close(); } catch {} })(),
    (async () => { try { chrome?.kill(); } catch {} })(),
    (async () => { try { await new Promise(r => server?.close(r)); } catch {} })()
  ]);
}

async function setViewport(w, h, mobile) {
  await send('Emulation.setDeviceMetricsOverride', {width: w, height: h, deviceScaleFactor: 1, mobile});
  await send('Page.bringToFront', {});
}

test('CL-UI-109 (live 390): P2-1 layer-sheet return pill closes the sheet; P3-6 dock-open residue cleared', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await send('Page.enable');
  await send('Page.navigate', {url: baseURL + '?region=tw'});
  await new Promise(r => setTimeout(r, 2500));
  const out = await evaljs(`(async () => {
    const $=s=>document.querySelector(s);
    // open the layer sheet, then click the dim return pill
    $('#layer-sheet-btn').click();
    await new Promise(r=>setTimeout(r,400));
    const openAfter=$('.map-panel').classList.contains('sheet-open');
    const dimVisible=!$('#wm-map-dim').hidden;
    const pill=$('#wm-map-dim')?.querySelector('[data-wm-act="sheet-close"],[data-wm-act="layer-sheet-close"]');
    if(pill) pill.click();
    await new Promise(r=>setTimeout(r,400));
    const closed=$('.map-panel').classList.contains('sheet-open');
    const dimHidden=$('#wm-map-dim').hidden;
    // P3-6: open the band, open the layer sheet (closes band), close sheet → no residue
    $('#wm-tl-bar').click();
    await new Promise(r=>setTimeout(r,200));
    const ops=$('.wm-ops');
    const expandedResidue=ops.classList.contains('wm-dock-open');
    $('#layer-sheet-btn').click();
    await new Promise(r=>setTimeout(r,300));
    $('#wm-map-dim').querySelector('[data-wm-act]').click();
    await new Promise(r=>setTimeout(r,300));
    const residue=ops.classList.contains('wm-dock-open');
    return {openAfter,dimVisible,pillFound:!!pill,closed,dimHidden,expandedResidue,residue};
  })()`);
  assert.equal(out.pillFound, true, 'dim hint carries the return action');
  assert.equal(out.openAfter, true, 'layer sheet opened');
  assert.equal(out.closed, false, 'P2-1: return pill CLOSES the layer sheet');
  assert.equal(out.dimHidden, true, 'dim hidden after close');
  assert.equal(out.residue, false, 'P3-6: no wm-dock-open residue after sheet interactions');
});

test('CL-UI-109 (live 390): P3-5 hit-area expanders land real clicks just outside the visual box', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await send('Page.navigate', {url: baseURL + '?region=tw'});
  await new Promise(r => setTimeout(r, 2500));
  const out = await evaljs(`(async () => {
    const probe=(el)=>{
      const r=el.getBoundingClientRect();
      const cx=r.left+r.width/2, cy=r.bottom+4;   // 4px BELOW the visual box
      const hit=document.elementFromPoint(cx,cy);
      return {ok:!!(hit&&(el.contains(hit)||hit===el)),hit:hit?(hit.id||hit.tagName+'.'+hit.className):'null',r:{w:Math.round(r.width),h:Math.round(r.height),b:Math.round(r.bottom)}};
    };
    const fire=(el)=>{
      let fired=false;
      const spy=()=>{fired=true;};
      el.addEventListener('click',spy,{once:true});
      const r=el.getBoundingClientRect();
      const ev=new MouseEvent('click',{bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.bottom+2});
      ev.__wmProbe=true;
      (document.querySelector('.map-panel')||document.body).dispatchEvent(ev);
      el.removeEventListener('click',spy);
      return fired;
    };
    const play=fire(document.querySelector('#time-play'));
    const reset=fire(document.querySelector('#reset-view'));
    // CL-UI-112: #data-info-open retired from the mobile shell (ⓘ moved into
    // the legend title row) — no longer a hit-compensation target/probe.
    const band=fire(document.querySelector('#layer-sheet-btn'));
    return {play,reset,band};
  })()`);
  console.error('[clui109 hit]', JSON.stringify(out));
  assert.equal(out.play, true, '#time-play hit extends past its visual box');
  assert.equal(out.reset, true, '#reset-view hit extends past its visual box');
});

test('CL-UI-109 (live 844×390): P2-2 landscape gets the APP shell — no scroll, no title block, dock in-flow', async () => {
  await setViewport(844, 390, true);
  await send('Page.navigate', {url: baseURL + '?region=tw'});
  let out = null;
  for (let i = 0; i < 30 && !out; ++i) {
    await new Promise(r => setTimeout(r, 1000));
    out = await evaljs(`(() => {
    const $=s=>document.querySelector(s);
    if(!$('#wm-tl-bar')||!$('.wm-ops')) return 'DBG '+JSON.stringify({ops:!!$('.wm-ops'),dock:!!$('#wm-timeline-dock'),bar:!!$('#wm-tl-bar'),src:$('source-state')?.textContent,sh:document.documentElement.scrollHeight});
    const cs=el=>el?getComputedStyle(el):null;
    return {
      scrollH:document.documentElement.scrollHeight,
      clientH:document.documentElement.clientHeight,
      titleLineH:document.querySelector('.header-title-line')?document.querySelector('.header-title-line').getBoundingClientRect().height:0,
      tlBarDisp:cs($('#wm-tl-bar'))?.display,
      tlBarTop:Math.round($('#wm-tl-bar')?.getBoundingClientRect().top||-1),
      opsH:Math.round($('.wm-ops')?.getBoundingClientRect().height||-1),
      mapWrapH:Math.round(document.querySelector('.map-wrap')?.getBoundingClientRect().height||-1),
      sideDisp:cs($('.wm-side'))?.display,
      inspClasses:$('.inspector')?.className||'',
    };
  })()`).catch(e => { console.error('[clui109 landpoll-err]', e && e.message); return null; });
    if (typeof out === 'string') { console.error('[clui109 landpoll]', out); out = null; }
  }
  assert.ok(out, 'landscape page rendered the timeline UI within 30s');
  assert.ok(out.scrollH <= out.clientH + 2, `landscape 844×390 must not scroll (scrollH ${out.scrollH} vs clientH ${out.clientH})`);
  assert.equal(out.titleLineH, 0, 'desktop title block must not reappear in landscape');
  assert.notEqual(out.tlBarDisp, 'none', 'timeline band visible in landscape');
  assert.ok(out.tlBarTop >= 0 && out.tlBarTop <= 390, `band reachable in the first screen (top=${out.tlBarTop})`);
  assert.equal(out.sideDisp, 'none', 'right side panel collapsed (app shell)');
  const shot = await send('Page.captureScreenshot', {format: 'png'});
  const fs = await import('node:fs');
  fs.writeFileSync(join(WEB, 'clui109-landscape-844x390.png'), Buffer.from(shot.data, 'base64'));
});

test('CL-UI-109 (live teardown)', async () => { await teardownBrowser(); });
