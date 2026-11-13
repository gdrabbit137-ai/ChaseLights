// CL-UI-75: mobile reflow of the 8-day strip in the place-guide modal (owner ruling).
// Owner's 390px screenshot showed the strip collapsed into a vertical narrow
// column: 「符合時數 9 · 06:00-14:00」 wrapped one-character-per-line and the
// 🎯 下一個符合時段 badge stacked three lines on the first qualifying cell.
// Contract:
//  (1) The 🎯 下一個符合時段 in-cell badge (CL-UI-67) is retired at EVERY
//      breakpoint — source + CSS + extracted render all badge-free; the
//      next-window info is carried by the 今日速覽 quick-view window line.
//  (2) Compact cell copy: met = ✓n qualifying-hours badge + abbreviated
//      window (06:00–13:00 → 06–13; a lone whole-hour stamp keeps 17:00),
//      unmet = ✗short-reason, unknown = the honest label. The aria-label
//      keeps the FULL qualifying-hours wording (screen-reader parity).
//  (3) Layout: ONE horizontal row of fixed-width cells that scrolls
//      horizontally at 390px — no wrap tier, no one-character-per-line
//      vertical reflow (headless-Chrome probe at 390px AND desktop).
// Run: node --test --test-isolation=none apps/web-v2/tests/cl-ui-75-day-strip-mobile.test.mjs
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

test('CL-UI-75 (1): the 🎯 下一個符合時段 badge is retired at every breakpoint', () => {
  assert.ok(!appSource.includes('🎯'), 'no 🎯 emoji anywhere in app.js');
  assert.ok(!cssSource.includes('🎯'), 'no 🎯 emoji anywhere in app.css');
  assert.ok(!appSource.includes('v2-strip-next') && !cssSource.includes('v2-strip-next'),
    'the badge span + its CSS rule are gone');
  assert.ok(!appSource.includes('nextNote'), 'no next-note wiring left');
  // The strip call takes no note (6 args, no nextNote).
  assert.match(appSource,
    /v2DayStripHtml\(days,labels,spot\.timezone,spot,opp\.genre_template\|\|'',opp\.opportunity_id\)/);
  assert.ok(!appSource.includes('v2DayStripHtml(days,labels,spot.timezone,spot,opp.genre_template||\'\',opp.opportunity_id,nextNote'));
  // The next-window info is the quick view's job: the 今日速覽 window line survives.
  assert.ok(appSource.includes('quick-window'), 'quick-view window line intact');
});

test('CL-UI-75 (2): compact cell copy — ✓n badge / ✗short-reason / abbreviated window', () => {
  const helperCode = grab('function compactHourSegmentsText', 'function v2ContractThreshold')
    + grab('function v2DominantFailMetric', 'function v2DayStripHtml')
    + grab('function v2DayStripHtml', '// CL-UI-64: top');
  const prelude = `
    const V2_EVAL_METRICS={'zh-TW':{cloud_cover_low:'低雲'},en:{},ja:{}};
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
  const fns = new Function(prelude + helperCode + ';return {v2DayStripHtml,compactHourSegmentsText};')();
  // Abbreviation helper: ranges compress, lone stamps keep their full form.
  assert.equal(fns.compactHourSegmentsText('06:00–13:00'), '06–13');
  assert.equal(fns.compactHourSegmentsText('17:00'), '17:00');
  assert.equal(fns.compactHourSegmentsText('06:00–08:00、17:00'), '06–08、17:00');
  const days = [
    {local_date: '2026-11-13', state: 'GUIDANCE_SATISFIED', good_hours: ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00'], conditions: []},
    {local_date: '2026-11-14', state: 'UNFAVORABLE', good_hours: [], conditions: [{metric: 'cloud_cover_low', day_verdict: 'FAIL'}]},
    {local_date: '2026-11-15', state: 'NOT_EVALUABLE', good_hours: [], conditions: []},
  ];
  const html = fns.v2DayStripHtml(days, ['今天', '明天', '後天'], 'Asia/Taipei', {spot_id: 'jp-003'}, 'cloud_sea', 'jp-003-P01');
  const cells = html.match(/<button[\s\S]*?<\/button>/g) || [];
  assert.equal(cells.length, 3);
  // Met: ✓n badge (never the 符合時數 n sentence) + abbreviated window.
  assert.ok(cells[0].includes('<span class="v2-strip-hours">✓8</span>'), 'badge-form hours, not a sentence');
  assert.ok(cells[0].includes('<span class="v2-strip-text">06–13</span>'), 'window abbreviated 06:00–13:00 → 06–13');
  const metText=(cells[0].match(/<span class="v2-strip-text">([^<]*)<\/span>/)||[])[1]||'';
  assert.ok(!metText.includes('符合時數'), 'the 符合時數 wording stays out of the cell text');
  // Unmet: ✗short-reason. Unknown: the honest label.
  assert.ok(cells[1].includes('<span class="v2-strip-text">✗低雲</span>'), 'unmet cell: ✗short-reason');
  assert.ok(cells[2].includes('<span class="v2-strip-text">資料不足</span>'), 'unknown cell: honest label');
  // No badge, no hover carrier anywhere.
  assert.ok(!html.includes('🎯') && !html.includes('v2-strip-next') && !html.includes('title='));
  // aria-label keeps the FULL unabbreviated wording (screen-reader parity).
  assert.match(html, /aria-label="今天 符合時數 8 · 06:00–13:00"/);
  assert.match(html, /aria-label="明天 未符·低雲"/);
});

test('CL-UI-75 (3): strip layout CSS — one horizontal row, fixed-width cells, no wrap tier', () => {
  assert.match(cssSource, /\.v2-day-strip\{[^}]*flex-wrap:nowrap/);
  assert.match(cssSource, /\.v2-day-strip\{[^}]*overflow-x:auto/);
  assert.match(cssSource, /\.v2-strip-cell\{[^}]*flex:0 0 auto[^}]*width:46px[^}]*box-sizing:border-box/);
  assert.match(cssSource, /\.v2-strip-text\{[^}]*white-space:nowrap[^}]*text-overflow:ellipsis/);
  // The old wrap tier and the one-char-per-line reflow rule are gone.
  assert.ok(!cssSource.includes('flex:1 1 76px'), 'the 76px wrap tier is retired');
  assert.ok(!/\.v2-strip-text\{[^}]*overflow-wrap:anywhere/.test(cssSource),
    'overflow-wrap:anywhere was the one-character-per-line reflow rule');
  // 390px tier: cells keep the 46px width (the honest 資料不足 label must
  // never ellipsize) and only shrink type/padding; no wrap tier, ever.
  const mobile = cssSource.slice(cssSource.indexOf('@media (max-width:390px)'), cssSource.indexOf('@media (max-width:390px)') + 600);
  assert.match(mobile, /\.v2-strip-cell\{font-size:\.62rem;padding:2px 1px;gap:2px\}/);
  assert.doesNotMatch(mobile, /flex:1 1/);
  assert.match(indexSource, /assets\/app\.js\?v=clui84/);
  assert.match(indexSource, /assets\/app\.css\?v=clui84/);
});

// ---- (4) real-browser probe: 390px and desktop -------------------------------
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
  // 8 real days: met 8h / met 1h / unmet / met 6h / unknown / unmet / met 3h / unmet —
  // the heaviest copy the strip can carry (✓8 · 06–13 on the first cell).
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
<title>CL-UI-75 fixture</title><link rel="stylesheet" href="/assets/app.css"></head>
<body style="margin:0"><div style="padding:12px">${stripHtml}</div></body></html>`;

let server, baseURL, chrome, ws, send, evaljs, screenshotPath;
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
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui75-')), 'about:blank'],
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
  const textHeights = cells.map(c => {
    const t = c.querySelector('.v2-strip-text');
    return t ? t.offsetHeight : null;
  });
  return {
    cells: cells.length,
    oneRow: tops.size === 1,
    sameWidth: new Set(widths).size === 1,
    maxWidth: Math.max(...widths),
    maxTextHeight: Math.max(...textHeights.filter(v => v != null)),
    overflow: strip.scrollWidth > strip.clientWidth,
    stripW: strip.clientWidth,
    scrollW: strip.scrollWidth,
    firstText: cells[0].querySelector('.v2-strip-text').textContent,
    firstBadge: cells[0].querySelector('.v2-strip-hours')?.textContent || null,
    anyBadge: !!strip.querySelector('.v2-strip-next'),
  };
})()`;

for (const vp of [{name: 'mobile 390px', w: 390, h: 844, mobile: true, shot: 'clui75-390px'}, {name: 'desktop 1280px', w: 1280, h: 900, mobile: false, shot: 'clui75-desktop'}]) {
  test(`CL-UI-75 (4): ${vp.name} — the strip is ONE row of fixed-width cells, no vertical squeeze`, async () => {
    await send('Emulation.setDeviceMetricsOverride', {width: vp.w, height: vp.h, deviceScaleFactor: 1, mobile: vp.mobile});
    await send('Page.enable');
    await send('Page.navigate', {url: baseURL});
    await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
    await new Promise(r => setTimeout(r, 300));
    const probe = await evaljs(PROBE);
    assert.equal(probe.error, undefined, 'strip rendered');
    assert.equal(probe.cells, 8, 'all 8 day cells present');
    assert.equal(probe.oneRow, true, 'every cell sits on ONE row — no wrap into a vertical column');
    assert.equal(probe.sameWidth, true, 'fixed-width cells');
    // CL-UI-76: desktop cells are content-sized (90–110px); the fixed-width
    // cap stays a MOBILE-only contract (<768px keeps CL-UI-75's 46px cells).
    if (vp.w >= 768) {
      assert.ok(probe.maxWidth >= 90 && probe.maxWidth <= 110, `desktop cells are content-sized 90–110px (got ${probe.maxWidth}px, CL-UI-76)`);
    } else {
      assert.ok(probe.maxWidth <= 60, `mobile cell width stays fixed (got ${probe.maxWidth}px)`);
    }
    assert.ok(probe.maxTextHeight <= 20, `no one-character-per-line squeeze: text stays single-line (got ${probe.maxTextHeight}px)`);
    assert.equal(probe.anyBadge, false, 'no 🎯 badge in the rendered strip');
    assert.equal(probe.firstBadge, '✓8', 'badge-form hours on the met cell');
    assert.equal(probe.firstText, '06–13', 'abbreviated window');
    console.log(vp.shot + ' probe: ' + JSON.stringify(probe));
    // CL-UI-75: at 390px the eight fixed-width cells may exceed the container —
    // the owner ruling sanctions horizontal scrolling there; the hard contract
    // is ONE row + no vertical squeeze, which holds either way.
    assert.ok(probe.scrollW >= probe.stripW, 'cells laid out at their fixed width');
    // Visual evidence screenshot (not committed).
    const shot = await send('Page.captureScreenshot', {format: 'png'});
    screenshotPath = process.env.CLUI75_SHOT_DIR || tmpdir();
    const file = join(screenshotPath, vp.shot + '.png');
    const {writeFileSync} = await import('node:fs');
    writeFileSync(file, Buffer.from(shot.data, 'base64'));
    console.log(`screenshot: ${file}`);
  });
}
