// CL-APP-09b: the ＋加自訂題材 editor was unusable on iPhone (owner repro:
// 詳情 → 我的自訂題材 → ＋ → only keyboard + name field visible; the condition
// form body / 適用月份 / 送出鈕 were unreachable). Three real defects found:
//   (1) keyboard clip — the ≤700px sheet's min/max-height:100vh measures the
//       LAYOUT viewport; iOS shrinks only the VISUAL viewport, the ~842px
//       editor fits inside 100vh so the sheet never scrolls internally and
//       everything under the keyboard was stranded. Fix: subject-sets.js fits
//       the OPEN sheet to visualViewport (resize+scroll) and hands the sheet
//       back to CSS when the keyboard closes.
//   (2) dead menu — homepage cards carry data-place-id (never data-spot-id)
//       and decorateCards never stamps the button, so the ⋯ menu's
//       ＋加自訂題材 item resolved pid='' and did NOTHING.
//   (3) buried sheet — opened from the place-modal panel the editor (z 90)
//       rendered BEHIND the place modal (z 1000); this asset's sheet now
//       paints at z 1100 and its toast follows.
// Also: create/patch/reset/sync/delete now force the panel list to re-render
// (signature guard skipped it — the new set stayed invisible until reopen).
// Contract: real CDP clicks + elementFromPoint at 390 under a simulated
// keyboard band (visualViewport.height 420), the FULL create flow 0→1, and
// the desktop 1280 sheet must stay untouched by the fit.
// Run: node --test apps/web-v2/tests/cl-app-09b-keyboard-fit.test.mjs
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
const jsSrc = readFileSync(join(WEB, 'assets', 'subject-sets.js'), 'utf8');
const cssSrc = readFileSync(join(WEB, 'assets', 'subject-sets.css'), 'utf8');
const htmlSrc = readFileSync(join(WEB, 'index.html'), 'utf8');

// ------------------------------------------------------------------ (1) source
test('CL-APP-09b (1a): the sheet fits the visual viewport while open and hands back to CSS when it closes', () => {
  assert.match(jsSrc, /function fitOverlay\(/);
  assert.match(jsSrc, /attachViewportFit\(\);\s*\n\s*fitOverlay\(\);/, 'openOverlay must fit immediately');
  assert.match(jsSrc, /vv\.addEventListener\('resize', els\._vvFit\)/);
  assert.match(jsSrc, /vv\.addEventListener\('scroll', els\._vvFit\)/);
  // fit writes the band (top+height) AND overrides the mobile sheet's 100vh
  // min/max-height (min-height would otherwise always win over max-height)
  assert.match(jsSrc, /els\.overlay\.style\.top = off \+ 'px'/);
  assert.match(jsSrc, /els\.overlay\.style\.height = h \+ 'px'/);
  assert.match(jsSrc, /modal\.style\.minHeight = h \+ 'px'/);
  assert.match(jsSrc, /modal\.style\.maxHeight = h \+ 'px'/);
  // keyboard closed (h >= full, offset 0) → CSS rules take over again
  assert.match(jsSrc, /if \(h >= full && off === 0\)/);
  // closing detaches the listeners and clears the inline fit
  assert.match(jsSrc, /function detachViewportFit\(\)/);
  assert.match(jsSrc, /detachViewportFit\(\);\s*\n\s*\}\s*\n\s*function wireClose/);
});

test('CL-APP-09b (1b): the sheet is marker-scoped and floats above the place modal (z 1000)', () => {
  assert.match(jsSrc, /'cl-cp-overlay cl-ss-overlay'/, 'marker class scopes the fit to THIS asset only');
  assert.match(cssSrc, /\.cl-ss-overlay\{z-index:1100\}/);
  // toast must paint above the place modal too (403-cap / success notices)
  assert.match(jsSrc, /els\.toast\.style\.zIndex = '1100'/);
});

test('CL-APP-09b (1c): the card ⋯ menu resolves the place id from data-place-id cards', () => {
  assert.match(jsSrc, /btn\.closest\('\[data-spot-id\]'\) \|\| btn\.closest\('\[data-place-id\]'\)/);
  assert.match(jsSrc, /host\.dataset\.spotId \|\| host\.dataset\.placeId/);
});

test('CL-APP-09b (1d): create/reset/sync/delete force an immediate panel list refresh', () => {
  assert.match(jsSrc, /if \(section && !state\.dirty && section\.dataset\.ssSig === sig/);
  // every mutation success path marks the panel dirty before re-rendering
  assert.match(jsSrc, /state\.dirty = true; \/\* CL-APP-09b: the list must refresh NOW \*\//);
  const dirtyCount = (jsSrc.match(/state\.dirty = true/g) || []).length;
  assert.ok(dirtyCount >= 4, 'create + reset + sync + delete must all mark dirty, got ' + dirtyCount);
});

test('CL-APP-09b (1e): cache-bust stamp - css keeps clapp09c, js re-stamped clapp09d (anchor-window patch), list-loader unchanged', () => {
  assert.match(htmlSrc, /assets\/subject-sets\.css\?v=clapp09c/);
  assert.match(htmlSrc, /<script src="\.\/assets\/subject-sets\.js\?v=clapp09d"><\/script>/);
  assert.doesNotMatch(htmlSrc, /assets\/subject-sets\.(js|css)\?v=clapp09b/);
});

// ------------------------------------------------- (2) real-hit headless checks
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs, ready;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

async function bootBrowser() {
  if (ready) return ready;
  ready = (async () => {
  const MIME = {'.html':'text/html','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml'};
  server = createServer((req, res) => {
    const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
    const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
    try { const body = readFileSync(file);
      res.writeHead(200, {'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
      res.end(body);
    } catch { res.writeHead(404); res.end('not found'); }
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  baseURL = `http://127.0.0.1:${server.address().port}/`;
  chrome = spawn(BROWSER, [
    '--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
    '--no-first-run','--remote-debugging-port=0',
    '--window-size=1280,900',
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clapp09b-')), 'about:blank'],
    {stdio: ['ignore','ignore','pipe']});
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
    const i = nextId(); pending.set(i, m => m.error ? reject(new Error(method + ': ' + m.error.message)) : resolve(m.result));
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
    (async () => { chrome?.kill(); })(),
    (async () => { await new Promise(r => server?.close(r)); })()
  ]);
}

// signed-in API stub + a keyboard-simulable visualViewport, injected BEFORE
// any page script (headless Chrome has no real keyboard to shrink the viewport)
const PAGE_STUB = `(function(){
  if (window.__clssFetch) return;
  var sets = [];
  window.__clssSets = sets;
  function R(status, body){ return { status: status, ok: status < 400, json: function(){ return Promise.resolve(body); } }; }
  window.__clssFetch = function(path, opts){
    opts = opts || {};
    if (path === '/api/v1/auth/me') return Promise.resolve(R(200, { user: { id:'t1', displayName:'測試員', level:'paid' } }));
    if (path.indexOf('/api/v1/subject_sets/eval?') === 0) return Promise.resolve(R(200, { sets: [] }));
    if (path.indexOf('/api/v1/subject_sets?') === 0) {
      var pid = decodeURIComponent(path.split('place_id=')[1] || '');
      var mine = sets.filter(function(s){return s.place_id===pid;});
      return Promise.resolve(R(200, { sets: mine, caps:{place:5,total:null}, counts:{place:mine.length,total:sets.length}, level:'paid' }));
    }
    if (path === '/api/v1/subject_sets' && opts.method === 'POST') {
      var b = JSON.parse(opts.body);
      var s = { id:'s'+(sets.length+1), place_id:b.place_id, name:b.name, template_id:b.template_id||null,
        base_conditions:b.base_conditions||{}, conditions:b.conditions||{}, months:b.months||[], base_rev:b.base_rev||null };
      sets.push(s);
      return Promise.resolve(R(201, s));
    }
    return Promise.resolve(R(404, { error:'stub-404 '+path }));
  };
  var vvListeners = {resize: [], scroll: []};
  var vv = { height: window.innerHeight, offsetTop: 0,
    addEventListener: function(t,f){ (vvListeners[t]=vvListeners[t]||[]).push(f); },
    removeEventListener: function(t,f){ var a=vvListeners[t]||[]; var i=a.indexOf(f); if(i>=0)a.splice(i,1); } };
  try { Object.defineProperty(window, 'visualViewport', { configurable: true, get: function(){ return vv; } }); } catch(e){}
  window.__vvKeyboard = function(h, off){ vv.height = h; vv.offsetTop = off||0;
    (vvListeners.resize||[]).concat(vvListeners.scroll||[]).forEach(function(f){ try { f(); } catch(e){} }); };
})();`;

async function setViewport(width, height, mobile) {
  await send('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor: mobile ? 3 : 1, mobile});
}

async function loadPage(width, height, mobile) {
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor: mobile ? 3 : 1, mobile});
  await send('Page.addScriptToEvaluateOnNewDocument', {source: PAGE_STUB});
  await send('Page.navigate', {url: baseURL});
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.card')&&document.querySelector('.cl-ss-more')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>30000){clearInterval(iv);reject(new Error('cards never rendered'));}
    },100);
  })`);
  await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
  await new Promise(r => setTimeout(r, 800));
}

async function realClick(cx, cy) {
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', {type, x: cx, y: cy, button: 'left', clickCount: 1});
  }
  await new Promise(r => setTimeout(r, 350));
}

// scroll a control into the visible band, hit-verify its center, return coords
async function probeControl(selector) {
  return evaljs(`(() => {
    const modal = document.querySelector('.cl-ss-overlay .cl-cp-modal');
    const el = modal.querySelector('${selector}');
    if (!el) return {err: 'missing ${selector}'};
    el.scrollIntoView({block: 'center'});
    const rr = el.getBoundingClientRect();
    const cx = rr.x + rr.width/2, cy = rr.y + rr.height/2;
    const hit = document.elementFromPoint(cx, cy);
    return {cx: Math.round(cx), cy: Math.round(cy),
      hitOk: el === hit || el.contains(hit) || (hit && hit.contains(el)),
      inBand: cy > 0 && cy <= window.visualViewport.height};
  })()`);
}

async function openEditorFromPanel() {
  // owner path: card 題材 button → place modal → 我的自訂題材 ＋
  // hit-verify + retry (cl-ui-47 pattern: early clicks land while handlers wire)
  for (let attempt = 1; attempt <= 3; attempt++) {
    const btn = await evaljs(`(() => {
      const card = document.querySelector('.card[data-place-id="tw-193"]') || document.querySelector('.card');
      const b = Array.from(card.querySelectorAll('button.tool-link, a.tool-link')).find(x => (x.textContent||'').indexOf('題材') >= 0);
      if (!b) throw new Error('題材 button not found');
      // the mobile site-nav is FIXED at the bottom — bring the button out from under it
      b.scrollIntoView({block: 'center'});
      const rr = b.getBoundingClientRect();
      const cx = rr.x + rr.width/2, cy = rr.y + rr.height/2;
      const hit = document.elementFromPoint(cx, cy);
      return {cx: Math.round(cx), cy: Math.round(cy), hitOk: b === hit || b.contains(hit),
        hitDesc: hit ? (hit.tagName + '|' + (hit.className||'') + '|' + (hit.id||'')) : 'null',
        vh: window.innerHeight, btnTop: Math.round(rr.top), btnBottom: Math.round(rr.bottom)};
    })()`);
    console.log('DIAG09b attempt', attempt, JSON.stringify(btn));
    // CL-CI-38: the patch-6 tier-tab pipeline rebuilds the card container when
    // lazy data lands — a click that lands while the DOM is swapped is a no-op
    // and the next probe can find the fresh button still under a closing
    // overlay. Re-probe after a beat instead of asserting the first read;
    // the hit assertion only fires when EVERY attempt was covered.
    let probe = btn;
    if (!probe.hitOk) {
      await new Promise(r => setTimeout(r, 700));
      probe = await evaljs(`(() => {
        const card = document.querySelector('.card[data-place-id="tw-193"]') || document.querySelector('.card');
        const b = Array.from(card.querySelectorAll('button.tool-link, a.tool-link')).find(x => (x.textContent||'').indexOf('題材') >= 0);
        if (!b) return {hitOk:false, cx:0, cy:0};
        b.scrollIntoView({block: 'center'});
        const rr = b.getBoundingClientRect();
        const cx = rr.x + rr.width/2, cy = rr.y + rr.height/2;
        const hit = document.elementFromPoint(cx, cy);
        return {cx: Math.round(cx), cy: Math.round(cy), hitOk: b === hit || b.contains(hit),
          hitDesc: hit ? (hit.tagName + '|' + (hit.className||'') + '|' + (hit.id||'')) : 'null'};
      })()`);
      console.log('DIAG09b reprobe', attempt, JSON.stringify(probe));
    }
    if (attempt === 3) assert.equal(probe.hitOk, true, '題材 button must be hit-reachable (final attempt)');
    await realClick(probe.cx, probe.cy);
    const ready = await evaljs(`new Promise((resolve)=>{
      const t0=Date.now();
      const iv=setInterval(()=>{
        if(document.getElementById('cl-ss-add')){clearInterval(iv);resolve(true);}
        else if(Date.now()-t0>12000){clearInterval(iv);resolve(false);}
      },100);
    })`);
    if (ready) break;
    if (attempt === 3) {
      const diag = await evaljs(`(() => {
        const pm = document.getElementById('place-modal-overlay');
        return JSON.stringify({pm: pm ? pm.style.display : 'absent', pid: pm ? pm.dataset.placeId : '',
          cards: document.querySelectorAll('.card').length});
      })()`);
      throw new Error('我的自訂題材 section never rendered — ' + diag);
    }
    // close whatever opened and retry
    await evaljs(`(() => {
      const pm = document.getElementById('place-modal-overlay');
      if (pm) { const c = pm.querySelector('[data-close], .modal-close, .close'); if (c) c.click(); pm.style.display = ''; }
    })()`);
    await new Promise(r => setTimeout(r, 500));
  }
  const add = await evaljs(`(() => {
    const b = document.getElementById('cl-ss-add');
    const rr = b.getBoundingClientRect();
    return {cx: Math.round(rr.x+rr.width/2), cy: Math.round(rr.y+rr.height/2)};
  })()`);
  await realClick(add.cx, add.cy);
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      const ov=document.querySelector('.cl-ss-overlay');
      if(ov&&ov.classList.contains('open')&&ov.querySelector('#cl-ss-name')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>15000){clearInterval(iv);reject(new Error('editor never opened'));}
    },100);
  })`);
}

test('CL-APP-09b (2): 390 keyboard band — full create flow (點＋→名稱→條件→月份→送出) succeeds and the list shows 0→1', async () => {
  await bootBrowser();
  await loadPage(390, 844, true);
  await openEditorFromPanel();

  // the sheet must paint ABOVE the place modal (z 1000) and the name field
  // must be hit-reachable right after opening
  const head = await evaljs(`(() => {
    const ov = document.querySelector('.cl-ss-overlay');
    const name = ov.querySelector('#cl-ss-name');
    const rr = name.getBoundingClientRect();
    return {z: getComputedStyle(ov).zIndex,
      nameHit: document.elementFromPoint(rr.x+rr.width/2, rr.y+rr.height/2) === name};
  })()`);
  assert.equal(head.z, '1100', 'editor sheet must float above the place modal');
  assert.equal(head.nameHit, true, 'name field must be hit-reachable');

  // keyboard pops (name auto-focused) → visual viewport shrinks to 420
  await evaljs(`window.__vvKeyboard(420, 0)`);
  await new Promise(r => setTimeout(r, 200));
  const band = await evaljs(`(() => {
    const ov = document.querySelector('.cl-ss-overlay');
    const modal = ov.querySelector('.cl-cp-modal');
    const mr = modal.getBoundingClientRect();
    return {ovTop: ov.style.top, ovH: ov.style.height, minH: modal.style.minHeight, maxH: modal.style.maxHeight,
      top: Math.round(mr.top), bottom: Math.round(mr.bottom),
      scrollable: modal.scrollHeight > modal.clientHeight,
      vvH: window.visualViewport.height};
  })()`);
  assert.equal(band.ovTop, '0px');
  assert.equal(band.ovH, '420px', 'the sheet must fit the keyboard band');
  assert.equal(band.minH, '420px', 'min-height must be overridden or 100vh always wins');
  assert.equal(band.maxH, '420px');
  assert.equal(band.top, 0);
  assert.equal(band.bottom, 420, 'modal bottom must sit at the visible band edge');
  assert.equal(band.scrollable, true, 'content must overflow the band so internal scrolling can reach the submit');

  // name via REAL input path (click + insertText)
  const nameField = await probeControl('#cl-ss-name');
  assert.equal(nameField.hitOk, true, 'name field must be hit-reachable in the band');
  await realClick(nameField.cx, nameField.cy);
  await send('Input.insertText', {text: '晨光反高潮位測試'});
  // conditions: semantic selects (real click + real change event)
  for (const [sel, val] of [['#cl-ss-sem-cloud', 'clear'], ['#cl-ss-sem-fog', 'clear'], ['#cl-ss-sem-rain', 'no']]) {
    const p = await probeControl(sel);
    assert.equal(p.hitOk, true, sel + ' must be hit-reachable in the band');
    await realClick(p.cx, p.cy);
    await evaljs(`(() => { const s = document.querySelector('.cl-ss-overlay ${sel}');
      s.value = '${val}'; s.dispatchEvent(new Event('change', {bubbles: true})); })()`);
  }
  const cond = await evaljs(`(() => {
    const g = id => { const e = document.querySelector('.cl-ss-overlay ' + id); return e ? e.value : null; };
    return {low: g('#cl-ss-cc-low'), vis: g('#cl-ss-cc-vis'), precip: g('#cl-ss-cc-precip')};
  })()`);
  assert.deepEqual(cond, {low: '15', vis: '8', precip: '0'}, 'semantic picks must map to the concrete thresholds');
  // months: REAL checkbox clicks
  for (const m of [3, 4]) {
    const p = await probeControl('#cl-ss-m' + m);
    assert.equal(p.hitOk, true, 'month chip ' + m + ' must be hit-reachable in the band');
    await realClick(p.cx, p.cy);
  }
  const months = await evaljs(`JSON.stringify([].map.call(document.querySelectorAll('.cl-ss-overlay #cl-ss-cc-months input:checked'), b => b.value))`);
  assert.deepEqual(JSON.parse(months), ['3', '4']);
  // submit: hit-verified REAL click inside the band
  const sub = await evaljs(`(() => {
    const modal = document.querySelector('.cl-ss-overlay .cl-cp-modal');
    const el = modal.querySelector('#cl-ss-submit');
    el.scrollIntoView({block: 'center'});
    const rr = el.getBoundingClientRect();
    const cx = rr.x + rr.width/2, cy = rr.y + rr.height/2;
    return {cx: Math.round(cx), cy: Math.round(cy), hitOk: document.elementFromPoint(cx, cy) === el,
      inBand: cy <= window.visualViewport.height};
  })()`);
  assert.equal(sub.hitOk, true, 'submit must be hit-reachable');
  assert.equal(sub.inBand, true, 'submit must sit inside the visible band after scrolling');
  await realClick(sub.cx, sub.cy);
  await new Promise(r => setTimeout(r, 800));
  const after = await evaljs(`(() => {
    const toast = document.querySelector('body > .cl-cp-toast');
    const rows = document.querySelectorAll('#cl-ss-rows .cl-ss-row');
    return {posted: (window.__clssSets||[]).map(s => ({name: s.name, months: s.months, cc: s.conditions})),
      toast: toast ? toast.textContent.slice(0, 20) : null,
      closed: !document.querySelector('.cl-ss-overlay.open'),
      rows: rows.length,
      firstRow: rows[0] ? rows[0].textContent.replace(/\\s+/g,' ').slice(0, 40) : null};
  })()`);
  assert.deepEqual(after.posted, [{name: '晨光反高潮位測試', months: [3, 4],
    cc: {cloud_low_max: 15, precip_max_mmh: 0, visibility_min_km: 8}}], 'POST payload must carry name + months + mapped thresholds');
  assert.match(after.toast, /✓ 自訂題材已建立/);
  assert.equal(after.closed, true, 'editor must close after success');
  assert.equal(after.rows, 1, 'the list must show the new set IMMEDIATELY (0→1), not after a panel reopen');
  assert.match(after.firstRow, /晨光反高潮位測試/);

  // keyboard closes → the sheet hands back to the CSS rules
  await evaljs(`window.__vvKeyboard(844, 0)`);
  await new Promise(r => setTimeout(r, 200));
  const restore = await evaljs(`(() => {
    const ov = document.querySelector('.cl-ss-overlay');
    const modal = ov.querySelector('.cl-cp-modal');
    return {ovH: ov.style.height || '(none)', minH: modal.style.minHeight || '(none)', maxH: modal.style.maxHeight || '(none)'};
  })()`);
  assert.deepEqual(restore, {ovH: '(none)', minH: '(none)', maxH: '(none)'}, 'keyboard close must clear the inline fit');
});

test('CL-APP-09b (3): 390 keyboard band — the card ⋯ menu ＋加自訂題材 is a WORKING entry (data-place-id cards)', async () => {
  await bootBrowser();
  // fresh page state — the previous test may leave modals open
  await loadPage(390, 844, true);
  const more = await evaljs(`(() => {
    const b = document.querySelector('.cl-ss-more');
    const card = b && b.closest('[data-place-id]');
    const rr = b.getBoundingClientRect();
    return {cx: Math.round(rr.x+rr.width/2), cy: Math.round(rr.y+rr.height/2),
      pid: card ? String(card.dataset.placeId) : null};
  })()`);
  await realClick(more.cx, more.cy);
  const item = await evaljs(`(() => {
    const m = document.querySelector('.cl-ss-menu.open');
    if (!m) return {err: 'menu did not open'};
    const it = m.querySelector('[data-ss-menu-item="add"]');
    const rr = it.getBoundingClientRect();
    return {cx: Math.round(rr.x+rr.width/2), cy: Math.round(rr.y+rr.height/2), pid: String(m._placeId)};
  })()`);
  // derive the expectation from the DOM (data drifts daily — never hardcode a place id)
  assert.ok(more.pid, 'the ⋯ button must sit inside a data-place-id card');
  assert.equal(item.pid, more.pid, 'the menu must resolve the place id from a data-place-id card');
  await realClick(item.cx, item.cy);
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      const ov=document.querySelector('.cl-ss-overlay');
      if(ov&&ov.classList.contains('open')&&ov.querySelector('#cl-ss-name')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>15000){clearInterval(iv);reject(new Error('editor never opened from the ⋯ menu'));}
    },100);
  })`);
});

test('CL-APP-09b (4): desktop 1280 — no keyboard, the sheet keeps its CSS geometry and every control is hit-reachable', async () => {
  await bootBrowser();
  await loadPage(1280, 900, false);
  await openEditorFromPanel();
  const probe = await evaljs(`(() => {
    const ov = document.querySelector('.cl-ss-overlay');
    const modal = ov.querySelector('.cl-cp-modal');
    const mr = modal.getBoundingClientRect();
    const sub = modal.querySelector('#cl-ss-submit'); const sr = sub.getBoundingClientRect();
    const name = modal.querySelector('#cl-ss-name'); const nr = name.getBoundingClientRect();
    return {inlineTop: ov.style.top || '(none)', inlineH: ov.style.height || '(none)',
      minH: modal.style.minHeight || '(none)', maxH: modal.style.maxHeight || '(none)',
      bottom: Math.round(mr.bottom),
      nameHit: document.elementFromPoint(nr.x+nr.width/2, nr.y+nr.height/2) === name,
      submitVisible: sr.bottom <= 900 && sr.top >= 0,
      submitHit: document.elementFromPoint(sr.x+sr.width/2, sr.y+sr.height/2) === sub};
  })()`);
  assert.deepEqual([probe.inlineTop, probe.inlineH, probe.minH, probe.maxH],
    ['(none)', '(none)', '(none)', '(none)'], 'no keyboard → no inline fit on desktop');
  assert.equal(probe.nameHit, true);
  assert.equal(probe.submitVisible, true, 'desktop must keep the fully-visible sheet (no regression)');
  assert.equal(probe.submitHit, true);
  await evaljs(`(() => { const c = document.querySelector('.cl-ss-overlay [data-ss-close]'); if (c) c.click(); })()`);
});

test('CL-APP-09b (5): browser teardown', async () => { await teardownBrowser(); });
