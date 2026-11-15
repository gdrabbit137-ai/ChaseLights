// CL-UI-100: headless screenshots of the rating UI against the mockup
// (data/v2/audits/design-mockups/mockup-rating.html, head ddbf4bcfc).
// Raw-CDP harness (local-smoke.mjs / cl-ui-47 precedent, no playwright needed
// on Windows). NOT a test — run manually:
//   node apps/web-v2/tests/cl-ui-100-screenshots.mjs <out-dir>
// The real page renders (repo data files are served statically); the feedback
// API resolves from window.__FBX_FIXTURES injected before any script runs.
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const OUT = process.argv[2] || 'D:/tmp/clui100-shots';
mkdirSync(OUT, { recursive: true });

const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || 'C:/Program Files/Google/Chrome/Application/chrome.exe';

const MIME = { '.html': 'text/html', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };
const server = createServer((req, res) => {
  res.on('error', () => { /* aborted client — nothing to do */ });
  try {
    const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
    const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
    const body = readFileSync(file);
    if (!res.headersSent) res.writeHead(200, { 'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream' });
    res.end(body);
  } catch { if (!res.headersSent) { res.writeHead(404); res.end('not found'); } }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}/`;

const chrome = spawn(BROWSER, [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
  '--no-first-run', '--remote-debugging-port=0',
  '--window-size=1280,900', '--hide-scrollbars',
  '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui100-')), 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });

const wsUrl = await new Promise((resolve, reject) => {
  let buf = '';
  chrome.stderr.on('data', (d) => {
    buf += d;
    const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
    if (m) resolve(m[1]);
  });
  setTimeout(() => reject(new Error('no devtools endpoint')), 30000);
});
const dbgHost = wsUrl.match(/ws:\/\/([^/]+)/)[1];
let targets = [];
for (let i = 0; i < 40; ++i) {
  targets = await (await fetch(`http://${dbgHost}/json/list`)).json();
  if (targets.some((x) => x.type === 'page')) break;
  await new Promise((r) => setTimeout(r, 250));
}
const ws = new WebSocket(targets.find((x) => x.type === 'page').webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });

let msgId = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
};
function send(method, params = {}, sessionId) {
  return new Promise((resolve) => {
    const id = ++msgId;
    pending.set(id, resolve);
    ws.send(JSON.stringify({ id, method, params, sessionId }));
  });
}
async function evaljs(expr) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.result && r.result.exceptionDetails) throw new Error('eval failed: ' + JSON.stringify(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails).slice(0, 500));
  return r.result && r.result.result && r.result.result.value;
}
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'png' });
  const buf = Buffer.from(r.result.data, 'base64');
  const p = join(OUT, name + '.png');
  (await import('node:fs')).writeFileSync(p, buf);
  console.log('saved', p);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const FIXTURES = `
window.__FBX_ERRORS = [];
window.addEventListener('error', function (e) { window.__FBX_ERRORS.push(String(e.message || e)); });
window.addEventListener('unhandledrejection', function (e) { window.__FBX_ERRORS.push('rej: ' + String(e.reason && e.reason.message || e.reason)); });
window.__FBX_FIXTURES = {
  config: { enabled: true },
  respond: function (path, opts) {
    var u = new URL(path, location.origin);
    var p = u.pathname;
    var json = function (doc) { return { ok: true, status: 200, json: function () { return Promise.resolve(doc); } }; };
    if (p.indexOf('/auth/me') >= 0) return json({ user: { displayName: '晨曦之光', provider: 'line' } });
    if (u.searchParams.get('mine')) return json({ rating: null });
    if (p.indexOf('/feedback') >= 0) {
      return json({
        placeId: u.searchParams.get('place_id'),
        insufficient: false, lFinal: 4.1, pFinal: 3.9, nRaw: 34, nEff: 30.8,
        nLast30: 8, pctP4plus: 0.78, nComments: 3,
        comments: [
          { message: '雲海值得，日出後半小時最紅；機位在停車場北側', maskedName: '山風·#4F2', lp: { l: 4, p: 5 }, createdAt: '2026-11-14 03:00:00' },
          { message: '風大要帶濾鏡，海面反光比預期多', maskedName: null, lp: { l: 4, p: 4 }, createdAt: '2026-11-13 12:00:00' },
          { message: '到達成本偏高，住宿只有一間', maskedName: '山影·#77AA', lp: { l: 3, p: 3 }, createdAt: '2026-11-12 21:00:00' }
        ]
      });
    }
    return { ok: false, status: 404, json: function () { return Promise.resolve({}); } };
  }
};`;

await send('Page.enable');
await send('Runtime.enable');
await send('Page.addScriptToEvaluateOnNewDocument', { source: FIXTURES });

async function setViewport(w, h) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: h < 500 });
}


async function waitFor(expr, ms) {
  const deadline = Date.now() + (ms || 20000);
  while (Date.now() < deadline) {
    if (await evaljs('!!(' + expr + ')')) return true;
    await sleep(400);
  }
  throw new Error('waitFor timeout: ' + expr);
}

// ---------- desktop 1280 ----------
await setViewport(1280, 900);
await send('Page.navigate', { url: base });
await waitFor("document.querySelector('#spots-container .card[data-place-id]')", 30000);
await waitFor("document.querySelector('#spots-container .card span.r-chip:not([hidden])')", 15000);
await sleep(1200);
await shot('clui100-1-cards-1280');

// open the forecast modal via a real card click on the chip (card body opens it)
const chipBox = await evaljs('(function(){var c=document.querySelector("#spots-container .card span.r-chip:not([hidden])");var r=c.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()');
await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: chipBox.x, y: chipBox.y, button: 'left', clickCount: 1 });
await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: chipBox.x, y: chipBox.y, button: 'left', clickCount: 1 });
await waitFor("document.querySelector('#modal-overlay .clfb[data-fbx-eval] .rbox')", 20000);
await sleep(1500);
const pos2 = await evaljs("(function(){var el=document.querySelector('#modal-overlay .clfb[data-fbx-eval]');if(!el)return null;el.scrollIntoView({block:'center'});var body=document.querySelector('#modal-overlay .modal-body');return {top:Math.round(el.getBoundingClientRect().top),bodyScroll:body.scrollTop};})()");
console.log('eval pos:', JSON.stringify(pos2));
await sleep(500);
await shot('clui100-2-forecast-modal-eval-1280');
// probe: how often does the eval section re-render?
await evaljs("(function(){window.__EVAL_MUTS=[];var sec=document.querySelector('#modal-overlay .clfb[data-fbx-eval]');var mo=new MutationObserver(function(){window.__EVAL_MUTS.push(Date.now());});mo.observe(sec,{childList:true,attributes:true});return 1;})()");
await sleep(2500);
console.log('eval mutations in 2.5s:', await evaljs("JSON.stringify({n:window.__EVAL_MUTS.length, t:window.__EVAL_MUTS.slice(-5), secs:document.querySelectorAll('.clfb[data-fbx-eval]').length})"));

// remove the mutation probe observer noise; keep going with real clicks
async function closeOv(id) {
  await evaljs('(function(){var b=document.querySelector("' + id + ' [data-fbx-close]");if(b)b.click();})()');
  await sleep(400);
}
async function openVia(openerSel, waitExpr, ms) {
  const box = await evaljs('(function(){var b=document.querySelector(' + JSON.stringify(openerSel) + ');if(!b)return null;b.scrollIntoView({block:"center"});var r=b.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()');
  if (!box) throw new Error('opener not found: ' + openerSel);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: box.x, y: box.y, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: box.x, y: box.y, button: 'left', clickCount: 1 });
  await waitFor(waitExpr, ms || 15000);
  await sleep(350);
}

// report modal
try {
  await openVia('#modal-overlay .clfb[data-fbx-eval] [data-fbx-open=report]', "document.querySelector('#fbx-report-overlay .type')");
} catch (e) {
  console.log('report open failed:', e.message);
  console.log('trace:', await evaljs("JSON.stringify(window.__FBX_TRACE||[])"), 'errors:', await evaljs("JSON.stringify(window.__FBX_ERRORS||[])"));
  console.log('sections:', await evaljs("JSON.stringify({secs:document.querySelectorAll('.clfb[data-fbx-eval]').length, rbox:!!document.querySelector('#modal-overlay .clfb[data-fbx-eval] .rbox'), btns:[].map.call(document.querySelectorAll('#modal-overlay .clfb[data-fbx-eval] [data-fbx-open]'),function(b){return b.getAttribute('data-fbx-open')}).join(',')})"));
  throw e;
}
await evaljs("(function(){var t=document.querySelector('#fbx-report-overlay .type');if(t)t.click();})()");
await sleep(300);
await shot('clui100-3-report-modal-1280');
await closeOv('#fbx-report-overlay');

// rate modal
await openVia('#modal-overlay .clfb[data-fbx-eval] [data-fbx-open=rate]', "document.querySelector('#fbx-rate-overlay .lev')");
await shot('clui100-4-rate-modal-1280');
await evaljs("(function(){var b=document.querySelector('#fbx-lev-L .lev[data-v=\"4\"]');if(b)b.click();var c=document.querySelector('#fbx-lev-P .lev[data-v=\"5\"]');if(c)c.click();})()");
await sleep(250);
await shot('clui100-4b-rate-modal-armed-1280');
await closeOv('#fbx-rate-overlay');

// subject panel (題材): close the forecast modal, then open via the card tool
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
await sleep(600);
await openVia('#spots-container .card [data-weather]', "document.querySelector('#place-modal-overlay .clfb[data-fbx-eval] .rbox')", 20000);
await sleep(800);
const pos5 = await evaljs("(function(){var el=document.querySelector('#place-modal-overlay .clfb[data-fbx-eval]');if(!el)return null;el.scrollIntoView({block:'center'});return Math.round(el.getBoundingClientRect().top);})()");
await sleep(500);
await shot('clui100-5-subject-panel-eval-1280');
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
await sleep(400);

// ---------- mobile 390 ----------
await setViewport(390, 844);
await send('Page.navigate', { url: base });
await waitFor("document.querySelector('#spots-container .card[data-place-id]')", 30000);
await waitFor("document.querySelector('#spots-container .card span.r-chip:not([hidden])')", 15000);
await sleep(1200);
await shot('clui100-6-cards-390');
await openVia('#spots-container .card span.r-chip:not([hidden])', "document.querySelector('#modal-overlay .clfb[data-fbx-eval] .rbox')", 20000);
await sleep(1000);
const pos7 = await evaljs("(function(){var el=document.querySelector('#modal-overlay .clfb[data-fbx-eval]');if(!el)return null;el.scrollIntoView({block:'center'});return Math.round(el.getBoundingClientRect().top);})()");
await sleep(500);
await shot('clui100-7-forecast-modal-eval-390');
await openVia('#modal-overlay .clfb[data-fbx-eval] [data-fbx-open=rate]', "document.querySelector('#fbx-rate-overlay .lev')");
await shot('clui100-8-rate-modal-390');

console.log('errors:', await evaljs("JSON.stringify(window.__FBX_ERRORS||[])"));
console.log('done');
chrome.kill();
server.close();
process.exit(0);
