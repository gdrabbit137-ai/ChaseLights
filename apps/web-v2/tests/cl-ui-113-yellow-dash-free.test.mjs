// CL-UI-113: yellow-dash-free map at the owner-report viewpoint (regression).
// Root cause of the recurring yellow-dash reports (CL-WG-25 -> CL-UI-107 ->
// CL-UI-113) was NOT a MapLibre style layer: it was the app's own canvas
// 50% cloud threshold contour (rgba(254,240,138) dashed), proven by headless
// A/B (hiding boundary_2/3 + boundary_disputed + park + park_outline left the
// dashes untouched; disabling the contour removed them). The contour is now
// removed; this test keeps the owner viewpoint honest:
//  (1) five model layers (gfs/icon/cwa/jma/himawari), low-cloud active,
//      camera at the Fujian-coast strait view (119.9E, 25.4N, zoom 7) where
//      the owner saw the dashed shapes;
//  (2) assert the weather overlay canvas has ZERO contour-yellow pixels in
//      the open-sea region (the RGB band only matches the old contour stroke
//      blended over sea; cloud fills are blue-dominant, whites keep B high);
//  (3) non-vacuous guard: the canvas region must actually be painted;
//  (4) keep the CL-UI-107 contract: no visible boundary-class style layers.
// Run: node --test apps/web-v2/tests/cl-ui-113-yellow-dash-free.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';

const require = createRequire(import.meta.url);
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.join(path.dirname(require.resolve('../../../assets/weather-map-regions.js')), '..');

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
      const file = path.join(ROOT, p === '/' ? 'weather-map.html' : p.slice(1));
      try { const body = fs.readFileSync(file);
        res.writeHead(200, {'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
        res.end(body);
      } catch { res.writeHead(404); res.end('not found'); }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    baseURL = `http://127.0.0.1:${server.address().port}/`;
    chrome = spawn(BROWSER, [
      '--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
      '--enable-unsafe-swiftshader','--use-angle=swiftshader',
      '--no-first-run','--remote-debugging-port=0',
      '--window-size=1280,900',
      '--user-data-dir=' + fs.mkdtempSync(path.join(require('node:os').tmpdir(), 'clui118-')), 'about:blank'],
      {stdio: ['ignore','ignore','pipe']});
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = '';
      const t = setTimeout(() => reject(new Error('no devtools endpoint')), 60000);
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
    (async () => { try { chrome?.kill(); } catch {} })(),
    (async () => { try { await new Promise(r => server?.close(r)); } catch {} })()
  ]);
}

const FIVE_MODES = ['gfs', 'icon', 'cwa', 'jma', 'himawari'];

// Sea-region scan of #weather-canvas. The old contour stroke was
// rgba(254,240,138) at .68 alpha — over the blue sea it lands in a
// yellow-cream band (R about G, both far above B). Cloud fills are
// blue-dominant and the pale overcast tail keeps B >= G, so nothing else in
// the overlay matches this band.
const SCAN = `(() => {
  const cv = document.getElementById('weather-canvas');
  if (!cv) return { error: 'no canvas' };
  const g = cv.getContext('2d');
  const x0 = Math.round(cv.width * 0.42), x1 = cv.width - 4;
  const y0 = Math.round(cv.height * 0.18), y1 = cv.height - 4;
  const img = g.getImageData(x0, y0, x1 - x0, y1 - y0).data;
  let contourYellow = 0, painted = 0, total = 0;
  for (let i = 0; i < img.length; i += 4) {
    const r = img[i], gg = img[i + 1], b = img[i + 2], a = img[i + 3];
    if (a < 8) continue;
    total++;
    if (b < 210 && r > 200 && gg > 195 && (r - b) > 35 && (gg - b) > 25 && Math.abs(r - gg) < 30) contourYellow++;
    if (b > 120 && b >= r) painted++;
  }
  return { contourYellow, painted, total, w: x1 - x0, h: y1 - y0 };
})()`;

const BOUNDARY_PROBE = `(() => {
  const map = window.__weatherGridMap;
  if (!map || !map.getStyle) return { ready: false };
  const layers = (map.getStyle() || {}).layers || [];
  const boundaryClass = layers.filter(l =>
    /boundary|disputed|admin/i.test(String(l.id || ''))
    || String(l['source-layer'] || '') === 'boundary'
    || /boundary|admin/i.test(String(l['source-layer'] || '')));
  const visible = boundaryClass.filter(l => ((l.layout || {}).visibility) !== 'none');
  return { ready: true, boundaryCount: boundaryClass.length, visibleIds: visible.map(l => l.id) };
})()`;

test('CL-UI-113 LIVE: five model layers, owner viewpoint, zero contour-yellow dashes', { timeout: 300000 }, async t => {
  await bootBrowser();
  t.after(() => teardownBrowser());
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', {width: 1280, height: 900, deviceScaleFactor: 1, mobile: false});
  await send('Page.navigate', {url: baseURL + '?spot='});
  let probe = { ready: false };
  for (let i = 0; i < 150 && !probe.ready; ++i) {
    await new Promise(r => setTimeout(r, 1000));
    probe = await evaljs(`(() => { const m = window.__weatherGridMap;
      return { ready: !!(m && m.isStyleLoaded && m.isStyleLoaded()) }; })()`).catch(() => ({ready:false}));
  }
  assert.ok(probe.ready, 'MapLibre basemap must boot within the wait window');
  await evaljs(`(() => { window.__weatherGridMap.jumpTo({center:[119.9,25.4],zoom:7}); return 1; })()`);
  await new Promise(r => setTimeout(r, 4000));

  for (const mode of FIVE_MODES) {
    await evaljs(`(() => {
      const sel = document.getElementById('model-select');
      sel.value = ${JSON.stringify(mode)};
      sel.dispatchEvent(new Event('change', {bubbles: true}));
      return sel.value;
    })()`);
    await new Promise(r => setTimeout(r, 2500));
    const bp = await evaljs(BOUNDARY_PROBE);
    assert.ok(bp.ready, `${mode}: basemap still live after switch`);
    assert.deepEqual(bp.visibleIds, [], `${mode}: no visible boundary-class layers (CL-UI-107 contract)`);
    const scan = await evaljs(SCAN);
    assert.ok(!scan.error, `${mode}: weather canvas readable`);
    assert.ok(scan.painted > 200, `${mode}: overlay canvas region is painted (non-vacuous scan)`);
    assert.equal(scan.contourYellow, 0,
      `${mode}: no contour-yellow dashed pixels in the open-sea region (got ${scan.contourYellow})`);
  }
});
