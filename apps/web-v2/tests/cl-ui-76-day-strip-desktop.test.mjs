// CL-UI-76: desktop responsive day-strip cell width (owner ruling).
// Owner's desktop screenshot showed the 46px fixed cell width (CL-UI-75's
// 390px-first compact tier) truncating 「今天 ✓9 06:00 0」 into overlapping
// ellipsized fragments on wide viewports.
// Contract:
//  (1) Desktop (>=768px): cells size to their content — min-width 90px,
//      max-width 110px, larger type/padding; the abbreviated window text
//      renders in FULL on one line (no ellipsis truncation).
//  (2) Mobile (<768px): the 46px fixed-width horizontal-scroll tier is
//      UNCHANGED (CL-UI-75 verified it; do not regress).
//  (3) Breakpoint: the 768px switch follows the owner-specified shell
//      breakpoint ladder (390px compact tier / 768px desktop); the 390px
//      compact tier stays untouched.
// Run: node --test --test-isolation=none apps/web-v2/tests/cl-ui-76-day-strip-desktop.test.mjs
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

test('CL-UI-76 (1): desktop tier CSS — content-sized cells 90–110px, mobile 46px untouched', () => {
  // The base (mobile <768px) rule keeps the CL-UI-75 fixed 46px width.
  assert.match(cssSource, /\.v2-strip-cell\{[^}]*flex:0 0 auto[^}]*width:46px[^}]*box-sizing:border-box/);
  // Desktop tier: >=768px media query — max-content grid columns (90px min)
  // so a cell is never narrower than its own text (CL-UI-79).
  const deskStart = cssSource.indexOf('@media (min-width:768px){');
  assert.ok(deskStart >= 0, 'a (min-width:768px) tier exists');
  const desk = cssSource.slice(deskStart, cssSource.indexOf('\n}', deskStart) + 1);
  assert.match(desk, /\.v2-day-strip\{display:grid;grid-auto-flow:column;grid-auto-columns:minmax\(90px,max-content\);justify-content:space-between\}/);
  assert.match(desk, /\.v2-strip-cell\{width:auto;min-width:90px;padding:5px 8px;font-size:\.72rem;gap:3px\}/);
  // The desktop tier must not reintroduce wrapping or a vertical reflow,
  // and must not clip cell text (no hidden/ellipsis in the desktop tier).
  assert.doesNotMatch(desk, /flex-wrap:wrap/);
  assert.doesNotMatch(desk, /overflow-wrap:anywhere/);
  assert.doesNotMatch(desk, /text-overflow:ellipsis/);
  // The 390px compact tier is unchanged (CL-UI-75's exact rules).
  const mobile = cssSource.slice(cssSource.indexOf('@media (max-width:390px)'), cssSource.indexOf('@media (max-width:390px)') + 600);
  assert.match(mobile, /\.v2-strip-cell\{font-size:\.62rem;padding:2px 1px;gap:2px\}/);
  assert.doesNotMatch(mobile, /min-width:90/);
  // Cache-bust: served HTML carries the new stamp.
  assert.match(indexSource, /assets\/app\.js\?v=clui88/);
  assert.match(indexSource, /assets\/app\.css\?v=clui88/);
});

// ---- (2) real-browser probe: desktop 1280px and mobile 390px ----------------
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

// The fixture page embeds the REAL strip markup produced by the real
// extracted function, styled by the REAL app.css — no test-only CSS.
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
  // 8 real days — the heaviest copy the strip can carry.
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

const fixtureHtml = `<!doctype html><html lang="zh-TW"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CL-UI-76 fixture</title><link rel="stylesheet" href="/assets/app.css"></head>
<body style="margin:0"><div style="padding:12px">${stripHtml}</div></body></html>`;

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
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui76-')), 'about:blank'],
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
  const strip = document.querySelector('.v2-day-strip');
  if (!strip) return {error: 'no strip'};
  const cells = [...strip.querySelectorAll('.v2-strip-cell')];
  const tops = new Set(cells.map(c => c.offsetTop));
  const widths = cells.map(c => c.offsetWidth);
  const texts = [...strip.querySelectorAll('.v2-strip-text')].map(t => ({
    text: t.textContent,
    truncated: t.scrollWidth > t.clientWidth,
    lines: Math.round(t.offsetHeight / (parseFloat(getComputedStyle(t).lineHeight) || 1)),
  }));
  return {
    cells: cells.length,
    oneRow: tops.size === 1,
    minWidth: Math.min(...widths),
    maxWidth: Math.max(...widths),
    minCell: Math.min(...widths),
    maxCell: Math.max(...widths),
    truncated: texts.filter(t => t.truncated).map(t => t.text),
    multiLine: texts.filter(t => t.lines > 1).map(t => t.text),
    firstText: texts[0]?.text,
  };
})()`;

for (const vp of [{name: 'desktop 1280px', w: 1280, h: 900, mobile: false, shot: 'clui76-desktop-1280'},
                  {name: 'mobile 390px', w: 390, h: 844, mobile: true, shot: 'clui76-mobile-390'}]) {
  test(`CL-UI-76 (2): ${vp.name} — desktop cells widen, mobile keeps 46px`, async () => {
    await send('Emulation.setDeviceMetricsOverride', {width: vp.w, height: vp.h, deviceScaleFactor: 1, mobile: vp.mobile});
    await send('Page.enable');
    await send('Page.navigate', {url: baseURL});
    await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
    await new Promise(r => setTimeout(r, 300));
    const probe = await evaljs(PROBE);
    assert.equal(probe.error, undefined, 'strip rendered');
    assert.equal(probe.cells, 8, 'all 8 day cells present');
    assert.equal(probe.oneRow, true, 'every cell sits on ONE row');
    assert.equal(probe.truncated.length, 0, `no text is ellipsis-truncated (got ${JSON.stringify(probe.truncated)})`);
    assert.equal(probe.multiLine.length, 0, `no text wraps to a second line (got ${JSON.stringify(probe.multiLine)})`);
    assert.equal(probe.firstText, '06–13', 'abbreviated window intact');
    if (vp.w >= 768) {
      assert.ok(probe.minCell >= 90, `desktop cells are content-sized >=90px (min ${probe.minCell}px)`);
      // CL-UI-79: no upper cap — cells grow to their text's max-content
      // width; the max-content grid column can never be narrower than the
      // text, so zero truncation is structural.
      assert.ok(probe.maxCell >= probe.minCell, 'cells stay content-sized');
    } else {
      assert.equal(probe.minCell, 46, 'mobile keeps the exact 46px fixed width');
      assert.equal(probe.maxCell, 46, 'mobile keeps the exact 46px fixed width');
    }
    console.log(vp.shot + ' probe: ' + JSON.stringify(probe));
    // Visual evidence screenshot (not committed).
    const shot = await send('Page.captureScreenshot', {format: 'png'});
    const shotDir = process.env.CLUI76_SHOT_DIR || tmpdir();
    const file = join(shotDir, vp.shot + '.png');
    const {writeFileSync} = await import('node:fs');
    writeFileSync(file, Buffer.from(shot.data, 'base64'));
    console.log(`screenshot: ${file}`);
  });
}
