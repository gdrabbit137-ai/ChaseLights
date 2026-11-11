// CL-UI-47: mobile card clicks were dead because CL-UI-46's date-picker
// overlay (and the admin area-filter menu) floated over the page in their
// CLOSED state — author `display` rules in the ≤640px media query overrode
// the UA `[hidden]` / closed-`<details>` hiding, so the invisible overlay
// swallowed every real hit (JS .click() bypasses hit-testing, which is why
// headless element.click() tests kept passing).
// Contract:
//  (1) Source: the overlay's mobile display rule is scoped to :not([hidden]),
//      an explicit [hidden] guard exists, and the admin menu/backdrop/handle
//      are display:none !important whenever .admin-filter is not [open].
//  (2) Real-hit regression (headless Chrome, real hit-testing, 390px AND
//      desktop viewports):
//        - closed overlays/menus must compute to display:none;
//        - elementFromPoint() at a card's center must resolve to the card or
//          one of its descendants (this is what catches layer-swallowing);
//        - a REAL input click (CDP Input.dispatchMouseEvent — trusted event
//          that goes through hit-testing, unlike el.click()) at the card's
//          center must open the place modal.
// Run: node --test apps/web-v2/tests/cl-ui-47-real-hit-targets.test.mjs
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
const htmlSource = readFileSync(join(WEB, 'index.html'), 'utf8');

test('CL-UI-47 (1a): day-picker overlay display rules are state-scoped', () => {
  const sheet = cssSource.slice(cssSource.indexOf('@media (max-width: 640px)'), cssSource.indexOf('.sub-btn.active'));
  assert.match(sheet, /\.day-picker-overlay:not\(\[hidden\]\)\s*\{\s*display:\s*block;/,
    'mobile block rule must not apply to a hidden overlay');
  assert.match(sheet, /\.day-picker-overlay\[hidden\]\s*\{\s*display:\s*none;/,
    'explicit guard so the author rule can never defeat [hidden]');
  // No mobile display value other than none may survive for the overlay
  // without a state scope (the desktop @media block hides it, which is fine).
  assert.doesNotMatch(sheet, /\.day-picker-overlay\s*\{\s*display:\s*(?:(?!none)[^}])*;/,
    'unscoped .day-picker-overlay{display:<not-none>} is the bug — keep it scoped');
});

test('CL-UI-47 (1b): admin filter menu/backdrop are guarded against a closed details', () => {
  assert.match(cssSource,
    /\.admin-filter:not\(\[open\]\)\s+\.admin-filter-menu,\s*\n\.admin-filter:not\(\[open\]\)\s+\.admin-picker-backdrop,\s*\n\.admin-filter:not\(\[open\]\)\s+\.admin-mobile-handle\s*\{\s*\n\s*display:\s*none\s*!important;/,
    'closed admin filter must force-hide menu, backdrop and handle');
});

test('CL-UI-47 (1c): cache-bust stamp for app.css is bumped in index.html', () => {
  const m = htmlSource.match(/app\.css\?v=clui(\d+)/);
  assert.ok(m, 'index.html must carry an app.css cache-bust stamp');
  assert.ok(Number(m[1]) >= 52, `stamp must be monotonic ≥ clui52, got clui${m[1]}`);
});

// ---- (2) real-hit headless checks -------------------------------------------
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
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui47-')), 'about:blank'],
    {stdio: ['ignore','ignore','pipe']});
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = '';
    const t = setTimeout(() => reject(new Error('no devtools endpoint')), 20000);
    chrome.stderr.on('data', d => { buf += d;
      const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
      if (m) { clearTimeout(t); resolve(m[1]); } });
    chrome.on('error', e => reject(new Error('spawn: ' + e.message)));
  });
  // Chrome (headless=new) can report an empty /json/list immediately after the
  // DevTools-listening line — poll until the initial page target exists.
  let targets = [];
  for (let i = 0; i < 20 && !targets.length; i++) {
    targets = await (await fetch(`http://${wsUrl.match(/ws:\/\/([^/]+)/)[1]}/json/list`)).json();
    if (!targets.length) await new Promise(r => setTimeout(r, 250));
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
});

test.after(async () => {
  try { ws?.close(); } catch {}
  chrome?.kill();
  await new Promise(r => server?.close(r));
});

async function setViewport(width, height, mobile) {
  await send('Emulation.setDeviceMetricsOverride',
    {width, height, deviceScaleFactor: 1, mobile});
}

async function loadPage() {
  await send('Page.enable');
  await send('Page.navigate', {url: baseURL});
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>20000){clearInterval(iv);reject(new Error('cards never rendered'));}
    },100);
  })`);
  await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
  await new Promise(r => setTimeout(r, 500));
}

// Returns {display, hit:{tag, cls, inside}} for the closed-state card center.
async function cardCenterProbe() {
  return evaljs(`(() => {
    const card = document.querySelector('.card');
    if (!card) return {error: 'no card'};
    const r = card.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const el = document.elementFromPoint(cx, cy);
    const ov = document.getElementById('day-picker-overlay');
    return {
      cx, cy,
      display: ov ? getComputedStyle(ov).display : 'absent',
      overlayHidden: ov ? ov.hidden : null,
      hit: el ? {tag: el.tagName, cls: el.className, inside: card.contains(el)} : null,
      adminMenuDisplay: (() => {
        const d = document.querySelector('.admin-filter');
        const menu = document.querySelector('.admin-filter-menu');
        if (!menu) return 'absent';
        if (d && !d.open) return getComputedStyle(menu).display;
        return 'open';
      })(),
      modalOpen: document.getElementById('place-modal-overlay').style.display === 'flex'
    };
  })()`);
}

async function realClick(cx, cy) {
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', {type, x: cx, y: cy, button: 'left', clickCount: 1});
  }
  await new Promise(r => setTimeout(r, 400));
}

for (const vp of [{name: 'mobile 390px', w: 390, h: 844, mobile: true}, {name: 'desktop 1280px', w: 1280, h: 900, mobile: false}]) {
  test(`CL-UI-47 (2): ${vp.name} — closed overlay is display:none and a REAL hit reaches the card`, async (t) => {
    await setViewport(vp.w, vp.h, vp.mobile);
    await loadPage();
    const probe = await cardCenterProbe();
    assert.equal(probe.display, 'none', 'closed day-picker overlay must not render');
    assert.equal(probe.overlayHidden, true, 'overlay element carries [hidden]');
    assert.ok(['none', 'absent'].includes(probe.adminMenuDisplay), 'closed admin-filter-menu must not render'); // CL-INT-103: CL-UI-49 merged admin picker renders conditionally (absent) or display:none — both honest
    assert.ok(probe.hit, 'elementFromPoint must hit something');
    assert.ok(probe.hit.inside, `card center must hit the card or a descendant, hit ${probe.hit.tag}.${probe.hit.cls}`);
    assert.equal(probe.modalOpen, false);
    await realClick(probe.cx, probe.cy);
    const after = await evaljs(`({modalOpen: document.getElementById('place-modal-overlay').style.display === 'flex'})`);
    assert.equal(after.modalOpen, true, 'real input click at the card center must open the modal');
    await realClick(10, 10); // outside-click close
  });
}
