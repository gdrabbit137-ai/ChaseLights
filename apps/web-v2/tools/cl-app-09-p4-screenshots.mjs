// CL-APP-09 patch-4 step ③: BLOCK-BY-BLOCK side-by-side verification — the
// OFFICIAL card forecast popup vs the PRIVATE point forecast popup, 1280/390,
// saved into apps/web-v2/tests/logs/cl-app-09-p4/. Run ad hoc (not part of
// the test-count floor):
//   node apps/web-v2/tests/cl-app-09-p4-screenshots.mjs
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { mkdtempSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const OUT = join(HERE, 'logs', 'cl-app-09-p4');
mkdirSync(OUT, { recursive: true });

const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

const MIME = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };
const server = createServer((req, res) => {
  const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
  const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
  try {
    const body = readFileSync(file);
    res.writeHead(200, { 'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream' });
    res.end(body);
  } catch { res.writeHead(404); res.end('not found'); }
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const baseURL = `http://127.0.0.1:${server.address().port}/`;

const chrome = spawn(BROWSER, [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
  '--no-first-run', '--remote-debugging-port=0', '--window-size=1280,900',
  '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clapp09p4-')), 'about:blank'],
  { stdio: ['ignore', 'ignore', 'pipe'] });
const wsUrl = await new Promise((resolve, reject) => {
  let buf = '';
  const timer = setTimeout(() => { reject(new Error('no devtools endpoint')); }, 60000);
  chrome.stderr.on('data', d => { buf += d;
    const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
    if (m) { clearTimeout(timer); resolve(m[1]); } });
});
const dbgHost = wsUrl.match(/ws:\/\/([^/]+)/)[1];
let targets = [];
for (let i = 0; i < 40; ++i) {
  targets = await (await fetch(`http://${dbgHost}/json/list`)).json();
  if (targets.some(t => t.type === 'page')) break;
  await new Promise(r => setTimeout(r, 250));
}
const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let loadEvents = 0;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();
ws.onmessage = m => { const msg = JSON.parse(m.data);
  if (msg.method === 'Page.loadEventFired') loadEvents++;
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); } };
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const i = nextId(); pending.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
  ws.send(JSON.stringify({ id: i, method, params })); });
const evaljs = async (expr) => {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
  return r.result?.result?.value ?? r.result?.value; };
const shot = async (pathOut) => {
  const s = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(pathOut, Buffer.from(s.data, 'base64'));
  return pathOut; };
const setViewport = (width, height, mobile) =>
  send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile });
const loadPage = async () => {
  const before = loadEvents;
  await send('Page.navigate', { url: baseURL });
  await new Promise((resolve, reject) => {
    const t0 = Date.now();
    const iv = setInterval(() => {
      if (loadEvents > before) { clearInterval(iv); resolve(true); }
      else if (Date.now() - t0 > 20000) { clearInterval(iv); reject(new Error('navigation never fired load')); }
    }, 100); });
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>30000){clearInterval(iv);reject(new Error('cards never rendered'));}
    },100);})`);
};

// The private-point stub rides every navigation (same fixture family as the
// cl-app-06 popup test — date-anchored hourly grid, one theme group).
await send('Page.enable');
await send('Page.addScriptToEvaluateOnNewDocument', { source: `
  window.__clcpMapLibre = false;
  window.__cpThemes = [
    { id: 'tg1', placeId: 'cp1', name: '雲海窗', nameI18n: { 'zh-TW': '雲海窗' },
      conditions: { cloud_low_max: 15, window_start: '04:30', window_end: '07:00' },
      evaluation: { tier: 'rec', reason: null, window: '2026-11-16 05:00' } },
  ];
  window.__clcpFetch = function (path) {
    if (path === '/api/v1/custom_places') {
      return Promise.resolve({ ok: true, status: 200, json: function () {
        return Promise.resolve({ ok: true, userId: 'u1', level: 'paid',
          trial: { expired: false, expiresAt: null }, quota: { used: 1, cap: 50 },
          degraded: false, degradedMessage: null,
          places: [{ id: 'cp1', name: '霧社水庫西岸岔路', lat: 23.9412, lng: 121.1523, elevation: 1150,
            timezone: 'Asia/Taipei',
            customConditions: { cloud_low_max: 15, visibility_min_km: 12, window_start: '04:30', window_end: '07:00' },
            status: 'active', createdAt: '', updatedAt: '',
            evaluation: { tier: 'rec', reason: null, window: '2026-11-16 05:00', evaluatedAt: '2026-11-15T10:00:00Z', private: true },
            themeGroups: window.__cpThemes, themes: { used: 1, cap: 5 }, sharing: null,
            refresh: { intervalHours: 6, label: '6h', energySaver: false }, fetchDeferred: false, fetchDueAt: null }] });
      } });
    }
    if (path === '/api/v1/custom_places/cp1/eval') {
      const pad = (n) => String(n).padStart(2, '0');
      const d0 = new Date(Date.now() + 8 * 3600e3);
      const iso = (off) => new Date(d0.getTime() + off * 86400e3).toISOString().slice(0, 10);
      const hourly = [];
      for (let day = 0; day < 2; day++) for (let h = 0; h < 24; h++) {
        const clean = day === 0 && h >= 5 && h <= 7;
        hourly.push({ local_date: iso(day), hour: pad(h) + ':00', values: {
          cloud_low: clean ? 10 : 90, cloud_mid: 20, cloud_high: 30,
          precipitation: 0, visibility: 20000, wind: 2 } });
      }
      return Promise.resolve({ ok: true, status: 200, json: function () {
        return Promise.resolve({ ok: true, id: 'cp1', private: true, hourly: hourly, generatedAt: '2026-11-15T10:00:00Z', elevation: 1150, timezone: 'Asia/Taipei' });
      } });
    }
    return Promise.resolve({ ok: false, status: 404, json: function () { return Promise.resolve({ error: 'stub 404' }); } });
  };
` });

async function capturePopups(tag, width, height, mobile) {
  await setViewport(width, height, mobile);
  await loadPage();
  // member state so the private list renders
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      document.dispatchEvent(new CustomEvent('chaselights:auth', { detail: { member: { id: 'u1', displayName: '晨曦旅人', level: 'paid' } } }));
      if(document.querySelector('.cl-cp-card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>10000){clearInterval(iv);reject(new Error('private cards never rendered'));}
    },300);})`);
  await new Promise(r => setTimeout(r, 400));
  // OFFICIAL popup: click the first official card
  await evaljs(`(async () => {
    const card=document.querySelector('#spots-container .card:not(.cl-cp-card)');
    card.click();
    await new Promise(r=>setTimeout(r,1800)); // modal + quick view + band settle
    return true; })()`);
  const official = await shot(join(OUT, `official-${tag}.png`));
  await evaljs(`document.getElementById('modal-overlay').click()`);
  await new Promise(r => setTimeout(r, 300));
  // PRIVATE popup: click the private card cp1
  await evaljs(`(async () => {
    const card=document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    card.querySelector('.cl-cp-card-name').click();
    const t0=Date.now();
    while(document.querySelector('#cl-cp-qv-days .cl-cp-qv-loading') && Date.now()-t0<8000) await new Promise(r=>setTimeout(r,100));
    await new Promise(r=>setTimeout(r,1200)); // quick view + strip settle
    return true; })()`);
  const priv = await shot(join(OUT, `private-${tag}.png`));
  // side-by-side composite: load both into one page and screenshot it
  const b64 = (p) => readFileSync(p).toString('base64');
  const page = `data:text/html;charset=utf-8,<body style="margin:0;background:%23222;display:flex;gap:8px;align-items:flex-start">
    <figure style="margin:0"><figcaption style="color:%23fff;font:14px sans-serif;padding:4px">OFFICIAL ${tag} ${width}x${height}</figcaption>
      <img src="data:image/png;base64,${b64(official)}" style="display:block"></figure>
    <figure style="margin:0"><figcaption style="color:%23fff;font:14px sans-serif;padding:4px">PRIVATE ${tag} ${width}x${height}</figcaption>
      <img src="data:image/png;base64,${b64(priv)}" style="display:block"></figure></body>`;
  await send('Emulation.setDeviceMetricsOverride', { width: width * 2 + 24, height: height + 40, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: page });
  await new Promise(r => setTimeout(r, 800));
  const both = await shot(join(OUT, `side-by-side-${tag}.png`));
  await setViewport(width, height, mobile);
  return both;
}

const files = [];
files.push(await capturePopups('1280', 1280, 900, false));
files.push(await capturePopups('390', 390, 844, true));
console.log('WROTE', files.join('\nWROTE '));
ws.close();
chrome.kill();
await new Promise(r => server.close(r));
