// CL-UI-114: A/B 深色底圖截圖（三案並列：現行亮色 / 方案A dark+hillshade / 方案B CSS暗化）。
// Raw-CDP harness（cl-ui-100 precedent）。NOT a test — run manually:
//   node apps/web-v2/tests/cl-ui-114-screenshots.mjs <out-dir>
// 每案 × 390/1280 × 台灣全幅＋山區放大（zoom 10，合歡山一帶）各一張。
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const OUT = process.argv[2] || 'D:/tmp/clui114-shots';
mkdirSync(OUT, { recursive: true });

const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || 'C:/Program Files/Google/Chrome/Application/chrome.exe';

const MIME = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };
const server = createServer((req, res) => {
  res.on('error', () => {});
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
  '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui114-')), 'about:blank',
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
function send(method, params = {}) {
  return new Promise((resolve) => {
    const id = ++msgId;
    pending.set(id, resolve);
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evaljs(expr) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.result && r.result.exceptionDetails) throw new Error('eval failed: ' + JSON.stringify(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails).slice(0, 500));
  return r.result && r.result.result && r.result.result.value;
}
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(join(OUT, name + '.png'), Buffer.from(r.result.data, 'base64'));
  console.log('saved', name);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function waitFor(expr, ms) {
  const deadline = Date.now() + (ms || 30000);
  while (Date.now() < deadline) {
    if (await evaljs('!!(' + expr + ')')) return true;
    await sleep(400);
  }
  throw new Error('waitFor timeout: ' + expr);
}
async function setViewport(w, h) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: h < 500 });
}

// 合歡山一帶（中央山脈北段，山區地形最明顯的對比點）
const MTN = { center: [121.27, 24.14], zoom: 10 };

const VARIANTS = [
  { tag: 'current', url: 'weather-map.html' },
  { tag: 'a-dark-hillshade', url: 'weather-map.html?wgBasemapDark=1' },
  { tag: 'b-dim-filter', url: 'weather-map.html?wgBasemapDim=1' },
];
const VIEWPORTS = [{ w: 1280, h: 900, tag: '1280' }, { w: 390, h: 844, tag: '390' }];

await send('Page.enable');
await send('Runtime.enable');

for (const vp of VIEWPORTS) {
  await setViewport(vp.w, vp.h);
  for (const v of VARIANTS) {
    await send('Page.navigate', { url: `${base}${v.url}` });
    // 等 MapLibre 起來 + basemap ready + 雲層 canvas 畫好
    await waitFor("window.__weatherGridMap && document.querySelector('#basemap-status') && /ready|fallback/.test(document.querySelector('#basemap-status').className)", 45000);
    await sleep(6000); // 底圖圖磚 + DEM/雲層繪製
    await shot(`clui114-${v.tag}-tw-full-${vp.tag}`);
    await evaljs(`(function(){var m=window.__weatherGridMap;if(m)m.jumpTo({center:[${MTN.center}],zoom:${MTN.zoom}});return 1;})()`);
    await sleep(6000); // zoom10 圖磚 + hillshade 重繪
    await shot(`clui114-${v.tag}-mountain-z10-${vp.tag}`);
    const status = await evaljs("document.querySelector('#basemap-status').className + ' | ' + document.querySelector('#basemap-status').textContent");
    const zoomNow = await evaljs("(function(){var m=window.__weatherGridMap;return m?m.getZoom().toFixed(2):'n/a';})()");
    console.log(`  [${v.tag} @${vp.tag}] status=${status} zoomAfterJump=${zoomNow}`);
  }
}
console.log('DONE →', OUT);
chrome.kill();
server.close();
process.exit(0);
