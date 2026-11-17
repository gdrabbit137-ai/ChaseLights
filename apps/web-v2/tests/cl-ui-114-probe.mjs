// CL-UI-114 probe: verify the A/B flags actually take effect in the live page.
// NOT a test — run manually: node apps/web-v2/tests/cl-ui-114-probe.mjs
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const MIME = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };
const server = createServer((req, res) => {
  try {
    const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
    const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
    const body = readFileSync(file);
    if (!res.headersSent) res.writeHead(200, { 'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream' });
    res.end(body);
  } catch { if (!res.headersSent) { res.writeHead(404); res.end('nf'); } }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}/`;
const chrome = spawn(process.env.CHROMIUM_EXECUTABLE || 'C:/Program Files/Google/Chrome/Application/chrome.exe', [
  '--headless=new', '--disable-gpu', '--no-sandbox', '--remote-debugging-port=0',
  '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui114p-')), 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });
const wsUrl = await new Promise((res, rej) => {
  let b = '';
  chrome.stderr.on('data', (d) => { b += d; const m = b.match(/DevTools listening on (ws:\/\/\S+)/); if (m) res(m[1]); });
  setTimeout(() => rej(new Error('no devtools')), 30000);
});
const dbg = wsUrl.match(/ws:\/\/([^/]+)/)[1];
let targets = [];
for (let i = 0; i < 40; ++i) { targets = await (await fetch(`http://${dbg}/json/list`)).json(); if (targets.some(x => x.type === 'page')) break; await new Promise(r => setTimeout(r, 250)); }
const ws = new WebSocket(targets.find(x => x.type === 'page').webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let id = 0; const pend = new Map();
ws.onmessage = (ev) => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const evaljs = async (e) => { const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true }); if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 300)); return r.result?.result?.value; };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function waitFor(expr, ms = 45000) { const dl = Date.now() + ms; while (Date.now() < dl) { if (await evaljs('!!(' + expr + ')')) return; await sleep(400); } throw new Error('timeout ' + expr); }

await send('Page.enable'); await send('Runtime.enable');
for (const q of ['', '?wgBasemapDark=1', '?wgBasemapDim=1', '?wgBasemapWindy=1', '?wgBasemapDark=1&wgBasemapDim=1']) {
  await send('Page.navigate', { url: `${base}weather-map.html${q}` });
  await waitFor("window.__weatherGridMap && document.querySelector('#basemap-status') && /ready/.test(document.querySelector('#basemap-status').className)");
  await sleep(2500);
  const info = await evaljs(`(function(){
    var m=window.__weatherGridMap, s=m.getStyle();
    var hs = s.layers && s.layers.find(function(l){return l.type==='hillshade';});
    return JSON.stringify({
      styleUrl: (s.sources && s.sources.openmaptiles && s.sources.openmaptiles.url) || Object.keys(s.sources).join(','),
      styleName: (typeof s.name==='string'? s.name : 'n/a'),
      hasHillshade: !!hs, hillshadeSrc: hs && hs.source,
      hasTerrarium: !!(s.sources && s.sources['clui114-terrarium']),
      tintApplied: (function(){ try { var b=s.layers && s.layers.find(function(l){return l.id==='background';}); return b ? (b.paint && b.paint['background-color']) : null; } catch(e){ return 'err'; } })(),
      filter: (m.getContainer() && m.getContainer().style.filter) || '(none)',
      canvasInsideContainer: !!(m.getContainer() && m.getContainer().querySelector('canvas'))
    });
  })()`);
  console.log(`q="${q}" →`, info);
}
chrome.kill(); server.close(); process.exit(0);
