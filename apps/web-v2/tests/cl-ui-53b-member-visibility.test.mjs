// CL-UI-53B: two homepage member-menu CSS bugs reproduced headless by the
// manager and fixed here:
//
//  (a) The open member menu reported menu.hidden=false, display:block and a
//      visible rect (~182x102 @ (1025,76)) but was INVISIBLE on screen: the
//      desktop .site-nav had z-index:400 without any position, so the value
//      was ignored — the dropdown (z-index 401, inside the backdrop-filter
//      stacking context) painted under the sticky .filter-shell (z-index 120,
//      opaque background) that follows it in root stacking order. Fix: the
//      bar is position:relative so z-index applies; the menu is additionally
//      shown only through a .ma-open class (positive state, not attribute
//      absence) and carries an inline style.display managed by
//      member-auth.js, so no shell display rule can ever fight the widget.
//  (b) The 登出 button carried hidden=true while signed out, but the unscoped
//      `.site-nav-more-btn { display:inline-flex; }` rule overrode the UA
//      [hidden] rule, so 登入 and 登出 rendered side by side. Fix: explicit
//      [hidden] guard rules in site-nav.css plus inline style.display:'none'
//      from member-auth.js (weight-explicit, shell-rule-proof).
//
// Contract:
//  (1) Source: site-nav.css carries the guard rules + the positioning fix;
//      member-auth.js switches visibility via inline style + .ma-open class,
//      never by relying on [hidden] vs shell display rules.
//  (2) Real headless browser (raw-CDP harness, same as cl-ui-47):
//        - signed out: computed display of 登出 is 'none';
//        - REAL input click on 登入 → menu computed display 'block',
//          .ma-open present, rect w/h > 0, rect inside the viewport, and
//          elementFromPoint() at the menu's center resolves to the menu or a
//          descendant (this is what catches a menu covered by the
//          filter-shell: rect numbers alone stay "green" while nothing is
//          visible);
//        - Escape closes it again (display back to 'none').
//  (3) Cache-bust stamps bumped to clui62 on all four shell pages.
// Run: node --test apps/web-v2/tests/cl-ui-53b-member-visibility.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync, mkdtempSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const cssSource = readFileSync(join(WEB, 'assets', 'site-nav.css'), 'utf8');
const jsSource = readFileSync(join(WEB, 'assets', 'member-auth.js'), 'utf8');
const PAGES = ['index.html', 'weather-map.html', 'genre-eval.html', 'field-intake.html'];

test('CL-UI-53B (1a): site-nav.css guards [hidden] against the shell display rules', () => {
  assert.match(cssSource,
    /\.site-nav-item\[hidden\],\s*\n\.site-nav-more-btn\[hidden\],\s*\n\.site-nav-menu\[hidden\]\s*\{\s*\n\s*display:\s*none;/,
    'explicit [hidden] guard so a hidden 登出 can never compute to flex');
  assert.match(cssSource,
    /\.site-nav-menu\[data-member-menu\]\s*\{\s*\n\s*display:\s*none;/,
    'member menu is closed by default through a display rule, not attribute absence');
  assert.match(cssSource,
    /\.site-nav-menu\[data-member-menu\]\.ma-open\s*\{\s*\n\s*display:\s*block;/,
    'open state is a positive .ma-open class with explicit weight');
});

test('CL-UI-53B (1b): the desktop bar is positioned so z-index applies (dropdown above filter-shell)', () => {
  const navBlock = cssSource.slice(cssSource.indexOf('.site-nav {'), cssSource.indexOf('.site-nav-inner'));
  assert.match(navBlock, /position:\s*relative;/,
    '.site-nav z-index was ignored without a position — dropdown painted under .filter-shell');
  assert.match(navBlock, /z-index:\s*400;/, 'bar keeps z-index 400 (> .filter-shell 120)');
});

test('CL-UI-53B (1c): member-auth.js switches visibility via inline style + .ma-open, not [hidden] alone', () => {
  assert.match(jsSource, /el\.style\.display = show \? '' : 'none';/,
    'inline display wins over any shell class rule');
  assert.match(jsSource, /menu\.classList\.toggle\('ma-open', show\);/,
    'menu open state is the .ma-open class');
  assert.match(jsSource, /el\.classList\.toggle\('ma-open', Boolean\(show\)\);/,
    'every member element mirrors state on .ma-open');
  assert.match(jsSource, /function isOpen\(\)/, 'single open-state read helper');
});

for (const page of PAGES) {
  test(`CL-UI-53B (3): ${page} carries the cache-bust stamps (site-nav clui62, member-auth clui68)`, () => {
    const html = readFileSync(join(WEB, page), 'utf8');
    assert.match(html, /site-nav\.css\?v=clui62/, 'site-nav.css stamp bumped');
    // CL-UI-60: member-auth.js advanced to clui68 (silent refresh session renewal).
    assert.match(html, /member-auth\.js\?v=clui68/, 'member-auth.js stamp bumped (CL-UI-60)');
  });
}

// ---- (2) real headless browser checks ---------------------------------------
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

test.before(async () => {
  const MIME = { '.html': 'text/html', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml' };
  server = createServer((req, res) => {
    const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
    const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
    try {
      const body = readFileSync(file);
      res.writeHead(200, { 'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream' });
      res.end(body);
    } catch { res.writeHead(404); res.end('not found'); }
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  baseURL = `http://127.0.0.1:${server.address().port}/`;
  chrome = spawn(BROWSER, [
    '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
    '--no-first-run', '--remote-debugging-port=0',
    '--window-size=1280,900',
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui53b-')), 'about:blank'],
    { stdio: ['ignore', 'ignore', 'pipe'] });
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = '';
    const t = setTimeout(() => reject(new Error('no devtools endpoint')), 20000);
    chrome.stderr.on('data', d => { buf += d;
      const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
      if (m) { clearTimeout(t); resolve(m[1]); } });
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
    ws.send(JSON.stringify({ id: i, method, params }));
  });
  evaljs = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
    return r.result?.result?.value ?? r.result?.value;
  };
});

test.after(async () => {
  try { ws?.close(); } catch {}
  chrome?.kill();
  await new Promise(r => server?.close(r));
});

async function realClick(x, y) {
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 });
  }
  await new Promise(r => setTimeout(r, 300));
}

test('CL-UI-53B (2): headless — signed-out 登出 computes display:none; real click on 登入 shows a truly visible menu', { timeout: 60000 }, async t => {
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.enable');
  await send('Page.navigate', { url: baseURL });
  // masthead member widgets are static markup — wait for member-auth.js init
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      const area=document.querySelector('[data-member-area]');
      if(area&&area.querySelector('[data-member-toggle]').style.display===''){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>15000){clearInterval(iv);reject(new Error('member area never initialized'));}
    },100);
  })`);
  await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);

  // (2b) signed out: 登出 must be truly invisible (computed display none)
  const closedProbe = await evaljs(`(() => {
    const area = document.querySelector('[data-member-area]');
    const logout = area.querySelector('[data-member-logout]');
    const toggle = area.querySelector('[data-member-toggle]');
    const menu = area.querySelector('[data-member-menu]');
    return {
      logoutDisplay: getComputedStyle(logout).display,
      logoutHidden: logout.hidden,
      toggleDisplay: getComputedStyle(toggle).display,
      menuDisplay: getComputedStyle(menu).display,
      menuClassOpen: menu.classList.contains('ma-open')
    };
  })()`);
  assert.equal(closedProbe.logoutDisplay, 'none', 'signed-out 登出 must compute display:none');
  assert.equal(closedProbe.logoutHidden, true);
  assert.ok(['inline-flex', 'flex'].includes(closedProbe.toggleDisplay),
    `signed-out 登入 stays visible, got ${closedProbe.toggleDisplay}`);
  assert.equal(closedProbe.menuDisplay, 'none', 'closed member menu must not render');
  assert.equal(closedProbe.menuClassOpen, false);

  // real input click on the 登入 button center (trusted event through hit-testing)
  const togglePos = await evaljs(`(() => {
    const r = document.querySelector('[data-member-area] [data-member-toggle]').getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  })()`);
  await realClick(togglePos.x, togglePos.y);

  const openProbe = await evaljs(`(() => {
    const menu = document.querySelector('[data-member-area] [data-member-menu]');
    const r = menu.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const hit = document.elementFromPoint(cx, cy);
    return {
      display: getComputedStyle(menu).display,
      classOpen: menu.classList.contains('ma-open'),
      hidden: menu.hidden,
      rect: { w: r.width, h: r.height, left: r.left, top: r.top },
      hitTag: hit ? hit.tagName : null,
      hitInside: hit ? menu.contains(hit) : false
    };
  })()`);
  assert.equal(openProbe.display, 'block', 'opened menu must compute display:block');
  assert.equal(openProbe.classOpen, true, 'opened menu carries .ma-open');
  assert.equal(openProbe.hidden, false);
  assert.ok(openProbe.rect.w > 0 && openProbe.rect.h > 0, `menu rect must have size, got ${JSON.stringify(openProbe.rect)}`);
  assert.ok(openProbe.rect.top >= 0 && openProbe.rect.left >= 0 && openProbe.rect.top < 900,
    `menu must sit inside the viewport, got ${JSON.stringify(openProbe.rect)}`);
  assert.ok(openProbe.hitInside,
    `elementFromPoint at menu center must hit the menu or a descendant — got ${openProbe.hitTag} ` +
    '(if false, something opaque covers the menu: the CL-UI-53B stacking bug)');

  // Escape closes it again
  await evaljs(`document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))`);
  await new Promise(r => setTimeout(r, 150));
  const afterEscape = await evaljs(`getComputedStyle(document.querySelector('[data-member-area] [data-member-menu]')).display`);
  assert.equal(afterEscape, 'none', 'Escape must close the menu');
});
