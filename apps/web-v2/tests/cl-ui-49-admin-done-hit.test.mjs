// CL-UI-49: the admin-picker sheet's Done button (#admin-filter [data-admin-done])
// was swallowed by the fixed mobile .site-nav bar (site-nav z-index:400) — the
// open sheet's backdrop/menu sat at z-index 210/220, BELOW the nav, so a native
// click at the Done button's center hit a .site-nav-item instead
// (ElementClickInterceptedException in the B149 mobile admin production smoke).
// Contract:
//  (1) Source: in the ≤640px media query the OPEN picker's backdrop must be
//      z-index > 400 and the menu > 401 (above .site-nav / .site-nav-menu).
//  (2) Real-hit regression (headless Chrome, 390px viewport, picker OPEN):
//        - elementFromPoint() at the Done button's center must resolve to the
//          button or a descendant (this catches layer-swallowing);
//        - a REAL input click (CDP Input.dispatchMouseEvent — trusted event
//          that goes through hit-testing, unlike el.click()) at that point must
//          close the picker (remove admin-picker-open).
// Pattern follows cl-ui-47-real-hit-targets.test.mjs.
// Run: node --test apps/web-v2/tests/cl-ui-49-admin-done-hit.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync} from 'node:fs';
import {mkdtempSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const cssSource = readFileSync(join(WEB, 'assets', 'app.css'), 'utf8');

test('CL-UI-49 (1): open admin-picker sheet renders above the fixed .site-nav', () => {
  const start = cssSource.indexOf('body.admin-picker-open');
  const sheet = cssSource.slice(start, cssSource.indexOf('@keyframes admin-sheet-in', start));
  const backdrop = sheet.match(/\.admin-picker-backdrop\s*\{[^}]*z-index:\s*(\d+)/);
  const menu = sheet.match(/\.admin-filter-menu\s*\{[^}]*z-index:\s*(\d+)/);
  assert.ok(backdrop, 'mobile backdrop rule must carry a z-index');
  assert.ok(menu, 'mobile menu rule must carry a z-index');
  assert.ok(Number(backdrop[1]) > 400, `backdrop z-index must exceed .site-nav (400), got ${backdrop[1]}`);
  assert.ok(Number(menu[1]) > 401, `menu z-index must exceed .site-nav-menu (401), got ${menu[1]}`);
});

// ---- (2) real-hit headless check --------------------------------------------
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

test.before(async () => {
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
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui49-')), 'about:blank'],
    {stdio: ['ignore','ignore','pipe']});
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = '';
    const t = setTimeout(() => reject(new Error('no devtools endpoint')), 20000);
    chrome.stderr.on('data', d => { buf += d;
      const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
      if (m) { clearTimeout(t); resolve(m[1]); } });
    chrome.on('error', e => reject(new Error('spawn: ' + e.message)));
  });
  const targets = await (await fetch(`http://${wsUrl.match(/ws:\/\/([^/]+)/)[1]}/json/list`)).json();
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
});

test.after(async () => {
  try { ws?.close(); } catch {}
  chrome?.kill();
  await new Promise(r => server?.close(r));
});

async function realClick(cx, cy) {
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', {type, x: cx, y: cy, button: 'left', clickCount: 1});
  }
  await new Promise(r => setTimeout(r, 400));
}

test('CL-UI-49 (2): at 390px with the picker OPEN, the Done button center hits the button and a real click closes the picker', async (t) => {
  await send('Emulation.setDeviceMetricsOverride', {width: 390, height: 844, deviceScaleFactor: 1, mobile: true});
  await send('Page.enable');
  await send('Page.navigate', {url: baseURL});
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>20000){clearInterval(iv);reject(new Error('cards never rendered'));}
    },100);
  })`);
  await new Promise(r => setTimeout(r, 500));
  // Open the admin picker the way a user does (real click on the summary).
  const openProbe = await evaljs(`(() => {
    const d = document.querySelector('.admin-filter');
    if (!d) return {error: 'no .admin-filter host'};
    const r = d.querySelector('summary').getBoundingClientRect();
    return {cx: r.left + r.width / 2, cy: r.top + r.height / 2};
  })()`);
  assert.ok(!openProbe.error, 'admin-filter must be present on the homepage');
  await realClick(openProbe.cx, openProbe.cy);
  const state = await evaljs(`(() => {
    const d = document.querySelector('.admin-filter');
    const open = !!(d && d.open && document.body.classList.contains('admin-picker-open'));
    if (!open) return {open};
    const btn = document.querySelector('#admin-filter [data-admin-done]');
    if (!btn) return {open, error: 'no Done button'};
    const r = btn.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const el = document.elementFromPoint(cx, cy);
    return {open, cx, cy,
      hit: el ? {tag: el.tagName, cls: String(el.className), inside: btn.contains(el)} : null,
      siteNavHit: el ? !!el.closest('.site-nav') : null};
  })()`);
  assert.equal(state.open, true, 'admin picker must be open at 390px');
  assert.ok(state.hit, 'elementFromPoint must hit something at the Done center');
  assert.ok(state.hit.inside, `Done button center must hit the button or a descendant, hit ${state.hit.tag}.${state.hit.cls}`);
  assert.equal(state.siteNavHit, false, 'the fixed .site-nav must not intercept the hit');
  // Real trusted click at the same point must close the picker.
  await realClick(state.cx, state.cy);
  const after = await evaljs(`({open: document.body.classList.contains('admin-picker-open')})`);
  assert.equal(after.open, false, 'real input click on the Done button must close the picker');
});
