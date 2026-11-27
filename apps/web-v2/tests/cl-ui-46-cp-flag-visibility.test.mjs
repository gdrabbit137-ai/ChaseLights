// CL-UI-46 condition 3: DOM-level proof that the 不限來源/官方/私人 source-filter
// row is hidden/shown by the member's REAL private-place count.
//
// The 2a source pins in cl-ui-46-card-count-dedupe.test.mjs only read app.js
// text — they pass even when the flag counts the wrong population (cardRows()
// drops trial-expired / pending / theme-less places) or when a stale '1'
// survives a cp-data event with no summary bundle. This file drives a real
// headless Chrome and asserts the COMPUTED display of .cl-cp-view-bar for:
//   (a) a member with zero private places            → none
//   (b) a member with one normal private place       → flex
//   (c) a member whose ONLY place is special/pending → flex   (condition 1)
//   (d) sign-out (cp-data with state.data null)      → none   (condition 2)
//   (e) the chaselights:auth sign-out path           → none   (condition 2)
// Run: CHROMIUM_EXECUTABLE=<chrome> node --test apps/web-v2/tests/cl-ui-46-cp-flag-visibility.test.mjs
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
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs, ready;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

// CL-UI-90 rule: no top-level test.before() (it poisons the shared root suite
// under --test-isolation=none). Boot lazily on the first test that needs it.
async function bootBrowser() {
  if (ready) return ready;
  ready = (async () => {
    const MIME = {'.html': 'text/html', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml'};
    server = createServer((req, res) => {
      const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
      // The summary/evaluation bundle is BLOCKED on purpose: this test needs the
      // exact state condition 2 is about — the page is up, the member's data has
      // arrived, but `currentData` is still null (bundle loading / failed), so a
      // cp-data handler gated on `if(currentData)` would never re-read the flag.
      if (/evaluations-latest\.json|evaluations-details\/|\/data\/v2\/evaluations\//.test(p)) {
        res.writeHead(404); res.end('blocked for CL-UI-46 test'); return;
      }
      const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
      try {
        const body = readFileSync(file);
        res.writeHead(200, {'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
        res.end(body);
      } catch { res.writeHead(404); res.end('not found'); }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    baseURL = `http://127.0.0.1:${server.address().port}/`;
    chrome = spawn(BROWSER, [
      '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
      '--no-first-run', '--remote-debugging-port=0', '--window-size=1440,900',
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui46cp-')), 'about:blank'],
      {stdio: ['ignore', 'ignore', 'pipe']});
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = ''; let loopLast = Date.now(); const loopStart = loopLast;
      const t = setInterval(() => {
        const now = Date.now();
        if (now - loopLast < 1500 && now - loopStart > 60000) { clearInterval(t); reject(new Error('no devtools endpoint')); }
        loopLast = now;
      }, 250);
      chrome.stderr.on('data', d => {
        buf += d;
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearInterval(t); resolve(m[1]); }
      });
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
    ws.onmessage = e => {
      const m = JSON.parse(e.data);
      if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    };
    send = (method, params = {}) => new Promise((resolve, reject) => {
      const i = nextId();
      pending.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
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

// Boots index.html once; the page needs no evaluation bundle for this test —
// the source-filter bar is created by custom-places.js at boot.
async function loadPage() {
  await send('Page.enable');
  await send('Page.navigate', {url: baseURL});
  await evaljs(`new Promise((resolve,reject)=>{const t0=Date.now();const iv=setInterval(()=>{
    if(document.querySelector('.cl-cp-view-bar')){clearInterval(iv);resolve(1);}
    else if(Date.now()-t0>30000){clearInterval(iv);reject(new Error('source-filter bar never mounted'));}},100);})`);
  // precondition: no summary bundle → currentData stays null for the whole test
  const cards = await evaljs(`document.querySelectorAll('#spots-container .card').length`);
  assert.equal(cards, 0, 'the evaluation bundle is blocked, so no card rendered (currentData is null)');
  // install the state stub seam ONCE (the real module's state() is replaced)
  await evaljs(`(()=>{
    const api=window.ChaseLightsCustomPlaces;
    if(!api) throw new Error('ChaseLightsCustomPlaces missing');
    window.__origState=api.state;
    window.__setPlaces=function(places,member){
      api.state=function(){return {member:member||null, data: places===null?null:{places:places}};};
      document.dispatchEvent(new CustomEvent('chaselights:cp-data'));
      const bar=document.querySelector('.cl-cp-view-bar');
      return {flag:document.body.getAttribute('data-cp-has-private'),
              display:bar?getComputedStyle(bar).display:'absent',
              height:bar?Math.round(bar.getBoundingClientRect().height):null};
      // NOTE: the bar's 「私人 N」 label is painted by custom-places.js's own
      // render() from its INTERNAL state, which this seam does not replace —
      // so the label is deliberately not asserted here. The seam replaces the
      // module's public state() accessor, i.e. exactly the source the flag (and
      // the label) must both derive from; case (c) is the regression guard.
    };
    return 1;})()`);
}

const NORMAL = {id:'cp-normal', name:'測試私人點', lat:25.1, lon:121.5, status:'ready', theme_groups:[{name:'海景'}]};
// The condition-1 population: a place that owns NO renderable card. cardRows()
// skips it (isSpecialCard), so a cardRows()-based flag would read 0 while the
// bar's own 「私人 N」 label reads 1.
const SPECIAL = {id:'cp-special', name:'待審核私人點', lat:25.2, lon:121.6, status:'trial_expired', theme_groups:[]};

test('CL-UI-46 (3): the source-filter row follows the member\'s private-place count (DOM)', async () => {
  await bootBrowser();
  await loadPage();

  // (a) zero private places → the row has no filtering meaning → hidden
  const a = await evaljs(`window.__setPlaces([], {id:'m1'})`);
  assert.equal(a.flag, '0');
  assert.equal(a.display, 'none', '(a) no private places: .cl-cp-view-bar computes to display:none');
  assert.equal(a.height, 0, '(a) the hidden row occupies no vertical space');

  // (b) one NORMAL private place → behaves exactly as before the ticket
  const b = await evaljs(`window.__setPlaces([${JSON.stringify(NORMAL)}], {id:'m1'})`);
  assert.equal(b.flag, '1');
  assert.equal(b.display, 'flex', '(b) one private place: the row comes back');
  assert.ok(b.height > 0, '(b) the row occupies real height');

  // (c) CONDITION 1: the only private place is special (trial_expired / no
  // themes). The bar's own label says 「私人 1」 — so the row must be VISIBLE.
  const c = await evaljs(`window.__setPlaces([${JSON.stringify(SPECIAL)}], {id:'m1'})`);
  assert.equal(c.flag, '1', '(c) a special/pending place still counts — cardRows() must not drive the flag');
  assert.equal(c.display, 'flex', '(c) the row is visible for a member whose only place is pending/trial-expired');

  // (d) CONDITION 2: sign-out arrives as a cp-data event with state.data null —
  // no summary bundle is loaded here at all, which is exactly the case that
  // used to leave a stale '1'.
  const d = await evaljs(`window.__setPlaces(null, null)`);
  assert.equal(d.flag, '0');
  assert.equal(d.display, 'none', '(d) sign-out (cp-data, no data) clears the flag: row hidden');

  // (e) CONDITION 2: the explicit chaselights:auth sign-out path clears it too,
  // without waiting for custom-places.js to finish a 401 refresh.
  const e = await evaljs(`(()=>{
    window.__setPlaces([${JSON.stringify(NORMAL)}], {id:'m1'});
    const before=getComputedStyle(document.querySelector('.cl-cp-view-bar')).display;
    // The real sign-out makes the module's state empty AND fires the auth event;
    // the seam is updated first so it mirrors that reality (a stub that kept
    // claiming a place would simply re-raise the flag on the cp-data the module
    // dispatches from its own synchronous sign-out render).
    window.ChaseLightsCustomPlaces.state=function(){return {member:null,data:null};};
    document.dispatchEvent(new CustomEvent('chaselights:auth',{detail:{member:null}}));
    const bar=document.querySelector('.cl-cp-view-bar');
    return {before, flag:document.body.getAttribute('data-cp-has-private'), display:getComputedStyle(bar).display};})()`);
  assert.equal(e.before, 'flex');
  assert.equal(e.flag, '0');
  assert.equal(e.display, 'none', '(e) chaselights:auth sign-out clears the flag immediately');
});

test('CL-UI-46 teardown', async () => {
  await teardownBrowser();
});
