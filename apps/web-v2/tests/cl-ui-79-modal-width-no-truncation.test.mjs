// CL-UI-79: place-detail modal width + day-strip zero-truncation (owner report:
// at a 1280px viewport the modal was ~800px wide, so the 8 day cells
// (90px min each + gaps + body padding) could not fit — day labels rendered
// as overlapping 「1114」 fragments and hour windows clipped).
// Contract:
//  (1) The place-detail modal (.modal.place-guide-modal) is 1180px wide
//      (design-review-1 P1-1 designer ruling) — ≥1000px real rendered width
//      at a 1280px viewport.
//  (1b) P1-1: the modal hourly table keeps min-width 1080px inside a
//      horizontally-scrolling wrapper; the 能見度 column is a fixed 88px and
//      the 「（資料上限）」 note is a tooltip, never clipped text.
//  (2) Desktop (>=768px) strip is a max-content grid (columns min 90px, grow
//      to their text) — a cell can never be narrower than its own text, so
//      scrollWidth <= clientWidth on every cell/span (zero truncation).
//  (3) Mobile (<768px) keeps the 46px horizontal-scroll tier untouched
//      (CL-UI-75; do not regress).
//  (4) Breakpoints probed for real: 1280 / 1024 / 768 / 390.
// Run: node --test --test-isolation=none apps/web-v2/tests/cl-ui-79-modal-width-no-truncation.test.mjs
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
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const cssSource = readFileSync(join(WEB, 'assets', 'app.css'), 'utf8');
const indexSource = readFileSync(join(WEB, 'index.html'), 'utf8');
const grab = (start, end) => {
  const a = appSource.indexOf(start);
  const b = appSource.indexOf(end, a + 1);
  assert.ok(a >= 0 && b > a, `source block ${start}…${end} not found`);
  return appSource.slice(a, b);
};

test('CL-UI-79 (1): source contract — 1180px modal, max-content grid strip, mobile 46px intact', () => {
  assert.match(cssSource, /\.place-guide-modal \{ max-width: 1180px;/);
  assert.doesNotMatch(cssSource, /\.place-guide-modal \{ max-width: 1080px;/);
  // P1-1: hourly table scrolls inside its wrapper; vis column fixed 88px.
  assert.match(cssSource, /\.timeline-table-wrap\{overflow-x:auto\}/);
  assert.match(cssSource, /\.timeline-table-wrap \.terminal-table\{min-width:1080px\}/);
  assert.match(cssSource, /\.terminal-table \.td-vis\{width:88px;min-width:88px;max-width:88px\}/);
  assert.match(appSource, /function visCellHtml\(km\)/);
  assert.match(appSource, /class="key-metric td-vis">\$\{visCellHtml\(item\.visibility\)\}/);
  assert.match(appSource, /class="vis-cap" title="\$\{esc\(d\(\)\.tip_vis\)\}">≥ 24 km<\/span>/);
  const mediaEnd = cssSource.indexOf('\n}', cssSource.indexOf('@media (min-width:768px){'));
  const desk = cssSource.slice(cssSource.indexOf('@media (min-width:768px){'), mediaEnd + 1);
  assert.match(desk, /\.v2-day-strip\{display:grid;grid-auto-flow:column;grid-auto-columns:minmax\(90px,max-content\);justify-content:space-between\}/);
  assert.doesNotMatch(desk, /text-overflow:ellipsis/);
  // Mobile 46px tier untouched (CL-UI-75).
  assert.match(cssSource, /\.v2-strip-cell\{[^}]*flex:0 0 auto[^}]*width:46px[^}]*box-sizing:border-box/);
  // Hourly control never navigates away (owner follow-up ruling).
  assert.doesNotMatch(appSource, /<a class="place-hourly-link"/);
  assert.match(appSource, /id="place-hourly-btn"/);
  // Cache-bust: served HTML carries the new stamp.
  assert.match(indexSource, /assets\/app\.js\?v=clui89/);
  assert.match(indexSource, /assets\/app\.css\?v=clui89/);
});

// ---- (2) real-browser probe: 1280 / 1024 / 768 / 390 ------------------------
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

const stripHtml = (() => {
  const helperCode = grab('function compactHourSegmentsText', 'function v2ContractThreshold')
    + grab('function v2DominantFailMetric', 'function v2DayStripHtml')
    + grab('function v2DayStripHtml', '// CL-UI-64: top');
  const prelude = `
    const V2_EVAL_METRICS={'zh-TW':{cloud_cover_low:'低雲',precipitation:'降水'},en:{},ja:{}};
    const V2_FAIL_PRIORITY=['cloud_cover_low'];
    let currentLang='zh-TW';
    let v2SubjectCards={};
    const v2SubjectCardRow=()=>null;
    const v2SubjectCardShortReason=()=>('');
    const v2SubjectCardShorts=()=>[];
    const localDateString=()=>'2026-11-13';
    const selectedDayOffset=()=>0;
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({eval2_hours:'符合時數',eval2_ok:'符合',eval2_bad:'未符',eval2_unk:'資料不足'});
    const listSep=()=>'、';
    const formatHourSegments=list=>{
      const times=(list||[]).slice().sort();
      if(!times.length)return '';
      const segs=[];let st=times[0],en=times[0];
      for(let i=1;i<times.length;i++){if(times[i]>en)en=times[i];}
      return st===en?st:st+'–'+en;
    };
    const v2EffectiveHours=(day)=>((day&&day.good_hours)||[]);
    const v2BestForSpot=null;
  `;
  const fns = new Function(prelude + helperCode + ';return {v2DayStripHtml};')();
  const days = [
    {local_date: '2026-11-13', state: 'GUIDANCE_SATISFIED', good_hours: ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00'], conditions: []},
    {local_date: '2026-11-14', state: 'GUIDANCE_SATISFIED', good_hours: ['17:00'], conditions: []},
    {local_date: '2026-11-15', state: 'UNFAVORABLE', good_hours: [], conditions: [{metric: 'cloud_cover_low', day_verdict: 'FAIL'}]},
    {local_date: '2026-11-16', state: 'GUIDANCE_SATISFIED', good_hours: ['05:00', '06:00', '07:00', '08:00', '09:00', '10:00'], conditions: []},
    {local_date: '2026-11-17', state: 'NOT_EVALUABLE', good_hours: [], conditions: []},
    {local_date: '2026-11-18', state: 'UNFAVORABLE', good_hours: [], conditions: [{metric: 'precipitation', day_verdict: 'FAIL'}]},
    {local_date: '2026-11-19', state: 'GUIDANCE_SATISFIED', good_hours: ['18:00', '19:00', '20:00'], conditions: []},
    {local_date: '2026-11-20', state: 'UNFAVORABLE', good_hours: [], conditions: [{metric: 'cloud_cover_low', day_verdict: 'FAIL'}]},
  ];
  const labels = ['今天', '明天', '11/15', '11/16', '11/17', '11/18', '11/19', '11/20'];
  return fns.v2DayStripHtml(days, labels, 'Asia/Taipei', {spot_id: 'jp-003'}, 'cloud_sea', 'jp-003-P01');
})();

// The strip lives inside the REAL place-detail modal, styled by the REAL
// app.css — the modal overlay is the real fixed overlay with 15px padding.
const fixtureHtml = `<!doctype html><html lang="zh-TW"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CL-UI-79 fixture</title><link rel="stylesheet" href="/assets/app.css"></head>
<body style="margin:0"><div class="modal-overlay" style="display:flex">
<div class="modal place-guide-modal"><div class="modal-body">${stripHtml}
<button type="button" class="place-hourly-link" id="place-hourly-btn" data-spot-id="jp-003">查看逐小時預報 →</button>
</div></div></div></body></html>`;

let server, baseURL, chrome, ws, send, evaljs;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

test.before(async () => {
  server = createServer((req, res) => {
    if (req.url.startsWith('/assets/app.css')) {
      res.writeHead(200, {'content-type': 'text/css'});
      res.end(cssSource);
      return;
    }
    res.writeHead(200, {'content-type': 'text/html; charset=utf-8'});
    res.end(fixtureHtml);
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  baseURL = `http://127.0.0.1:${server.address().port}/`;
  chrome = spawn(BROWSER, [
    '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
    '--no-first-run', '--remote-debugging-port=0',
    '--window-size=1280,900',
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui79-')), 'about:blank'],
    {stdio: ['ignore', 'ignore', 'pipe']});
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

const PROBE = `(() => {
  const modal = document.querySelector('.modal.place-guide-modal');
  const strip = document.querySelector('.v2-day-strip');
  if (!modal || !strip) return {error: 'fixture incomplete'};
  const cells = [...strip.querySelectorAll('.v2-strip-cell')];
  const tops = new Set(cells.map(c => c.offsetTop));
  const widths = cells.map(c => c.offsetWidth);
  const clipped = [...strip.querySelectorAll('.v2-strip-cell, .v2-strip-day, .v2-strip-text, .v2-strip-hours')]
    .filter(el => el.scrollWidth > el.clientWidth).map(el => el.textContent);
  return {
    modalWidth: modal.offsetWidth,
    cells: cells.length,
    oneRow: tops.size === 1,
    minCell: Math.min(...widths),
    maxCell: Math.max(...widths),
    stripScrolls: strip.scrollWidth > strip.clientWidth,
    clipped,
    firstDay: document.querySelector('.v2-strip-day')?.textContent,
  };
})()`;

for (const vp of [{name: '1280px', w: 1280, h: 900, mobile: false, minModal: 1000, shot: 'clui79-1280'},
                  {name: '1024px', w: 1024, h: 800, mobile: false, minModal: 950, shot: 'clui79-1024'},
                  {name: '768px', w: 768, h: 900, mobile: false, minModal: 700, shot: 'clui79-768'},
                  {name: '390px', w: 390, h: 844, mobile: true, minModal: 0, shot: 'clui79-390'}]) {
  test(`CL-UI-79 (2): ${vp.name} — modal width + zero truncation`, async () => {
    await send('Emulation.setDeviceMetricsOverride', {width: vp.w, height: vp.h, deviceScaleFactor: 1, mobile: vp.mobile});
    await send('Page.enable');
    await send('Page.navigate', {url: baseURL});
    await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
    await new Promise(r => setTimeout(r, 300));
    const probe = await evaljs(PROBE);
    assert.equal(probe.error, undefined, 'fixture rendered');
    assert.equal(probe.cells, 8, 'all 8 day cells present');
    assert.equal(probe.clipped.length, 0, `zero text truncation (got ${JSON.stringify(probe.clipped)})`);
    assert.equal(probe.oneRow, true, 'every cell sits on ONE row');
    assert.equal(probe.firstDay, '今天', 'day label intact (no overlapping fragments)');
    if (vp.w >= 768) {
      assert.ok(probe.modalWidth >= vp.minModal, `${vp.name}: modal width ${probe.modalWidth}px >= ${vp.minModal}px`);
      assert.ok(probe.minCell >= 90, `desktop cells >=90px (min ${probe.minCell}px)`);
    } else {
      assert.equal(probe.minCell, 46, 'mobile keeps the exact 46px fixed width');
      assert.equal(probe.maxCell, 46, 'mobile keeps the exact 46px fixed width');
    }
    console.log(vp.shot + ' probe: ' + JSON.stringify(probe));
    const shot = await send('Page.captureScreenshot', {format: 'png'});
    const shotDir = process.env.CLUI79_SHOT_DIR || tmpdir();
    const file = join(shotDir, vp.shot + '.png');
    const {writeFileSync} = await import('node:fs');
    writeFileSync(file, Buffer.from(shot.data, 'base64'));
    console.log(`screenshot: ${file}`);
  });
}
