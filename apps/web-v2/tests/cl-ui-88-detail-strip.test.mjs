// CL-UI-88: 詳情彈窗日方框截斷修復（owner 實測缺陷, mockup-first Stage 2c,
// spec = origin/task/DESIGN-3 data/v2/audits/design-mockups/mockup-detail.html
// @3d455f121, DESIGN-3a strip section）.
// Owner's screenshot: the Japanese-locale day cell truncated its slot string
// with an ellipsis (「✓6 / 01—0…」) and the row's right edge was cut with NO
// scroll hint. Contract:
//  (1) 時段字串永不截斷 — no ellipsis/hidden overflow on the in-cell copy at
//      ANY width; cells are content-sized (min-width content-driven, the box
//      widens to its text); the full unabbreviated segments ride the cell
//      tooltip (title=) beside the aria-label parity copy.
//  (2) 日期列橫移 — the strip is an overflow-x scroll row at EVERY width with
//      two-side 8px gradient fade hints, hidden scrollbar and drag-to-scroll
//      (initDragScroll/centerSel, copied verbatim from mockup-detail.html).
//  (3) 多題材區塊各自日期列可獨立橫移 — one strip per subject block; scrolling
//      one never moves the other (real-browser probe).
//  (4) ≤480px the detail modal goes full-screen (mockup-detail n4b).
// Run: node --test --test-isolation=none apps/web-v2/tests/cl-ui-88-detail-strip.test.mjs
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

test('CL-UI-88 (1): strip CSS — content-sized cells, no ellipsis, fade hints + drag', () => {
  // (1) 時段字串永不截斷：the in-cell copy never ellipsizes or hides overflow.
  const textRules = cssSource.match(/\.v2-strip-text\{[^}]*\}/g) || [];
  const dayRules = cssSource.match(/\.v2-strip-day\{[^}]*\}/g) || [];
  assert.ok(textRules.length >= 1 && dayRules.length >= 1, 'strip copy rules present');
  for (const rule of [...textRules, ...dayRules]) {
    assert.ok(!rule.includes('text-overflow:ellipsis'), `no ellipsis: ${rule}`);
    assert.ok(!rule.includes('overflow:hidden'), `no hidden overflow: ${rule}`);
    assert.ok(!rule.includes('max-width:100%'), `no max-width clamp: ${rule}`);
  }
  // Cell min-width is content-driven (grid min-content columns), not fixed.
  const cellRule = cssSource.match(/\.v2-strip-cell\{[^}]*\}/)[0];
  assert.match(cellRule, /width:auto;min-width:0/);
  assert.doesNotMatch(cellRule, /width:46px/);
  assert.doesNotMatch(cellRule, /flex:0 0 auto/);
  // (2) 日期列橫移：overflow-x + hidden scrollbar + drag cursor + contained
  // overscroll + two-side 8px gradient fade hints (mockup DESIGN-3a).
  const stripRule = cssSource.match(/\.v2-day-strip\{[^}]*\}/)[0];
  assert.match(stripRule, /overflow-x:auto/);
  assert.match(stripRule, /scrollbar-width:none/);
  assert.match(stripRule, /overscroll-behavior-x:contain/);
  assert.match(stripRule, /cursor:grab/);
  assert.match(stripRule, /mask-image:linear-gradient\(90deg,transparent,var\(--cl-ink\) 8px,var\(--cl-ink\) calc\(100% - 8px\),transparent\)/);
  assert.match(cssSource, /\.v2-day-strip\.dragging\{cursor:grabbing\}/);
  assert.ok(cssSource.includes('-webkit-mask-image:linear-gradient(90deg,transparent,var(--cl-ink) 8px'), 'webkit mask twin');
  // The selected-date cell carries the mockup's outline selection mark.
  assert.match(cssSource, /\.v2-strip-cell\.sel\{outline:2px solid var\(--cl-text-1\);outline-offset:-2px\}/);
  // (4) ≤480px full-screen detail modal (mockup n4b: inset 0, radius 0,
  // 44×44 close button).
  const fsStart = cssSource.indexOf('@media (max-width:480px){');
  assert.ok(fsStart >= 0, 'a (max-width:480px) tier exists');
  const fsBlock = cssSource.slice(fsStart, cssSource.indexOf('\n}', fsStart) + 1);
  assert.match(fsBlock, /\.modal\.place-guide-modal\{max-width:none;width:100%;height:100dvh;max-height:100dvh;margin:0;border-radius:0\}/);
  assert.match(fsBlock, /\.place-guide-modal \.close-btn\{width:44px;height:44px\}/);
  // Quick-view panel carries the tier semantics (green when recommended).
  assert.match(cssSource, /\.place-quick-view\.quick-ok\{background:color-mix\(in srgb, var\(--cl-green\) 10%, transparent\);border-color:color-mix\(in srgb, var\(--cl-green\) 55%, transparent\)\}/);
  // Cache-bust: the served homepage carries the new stamp.
  assert.equal((indexSource.match(/\?v=clui102/g) || []).length,2, 'feedback-ui stays at clui102 (app.js + app.css advanced to clui120) (app.js advanced to clui118, CL-UI-110)');
  assert.equal((indexSource.match(/\?v=clui148/g) || []).length,3, 'app.css + app.js + icons.js at clui148 (CL-UI-115 added the icon set)');
  assert.match(indexSource, /assets\/app\.js\?v=clui148/);
});

test('CL-UI-88 (2): strip wiring — tooltip + .sel + per-block drag init in app.js', () => {
  // (1) the cell carries the FULL wording as a tooltip beside aria-label.
  assert.match(appSource, /title="\$\{esc\(aria\)\}" aria-label="\$\{esc\(aria\)\}"/);
  // The selected date cell gets .sel from selectedDayOffset.
  assert.match(appSource, /const sel=\(i===selectedDayOffset\(\)\)\?' sel':'';/);
  // (2) mockup DESIGN-3a drag helpers exist and are wired to EVERY block's
  // strip inside decorateV2Eval (one independent row per 題材區塊).
  assert.ok(appSource.includes('function initDragScroll(el){'), 'initDragScroll present');
  assert.ok(appSource.includes('function centerSel(el){'), 'centerSel present');
  assert.match(appSource, /const strip=el\.querySelector\('\.v2-day-strip'\);\n\s+if\(strip\)\{initDragScroll\(strip\);centerSel\(strip\);\}/);
  // The quick view panel toggles its tier class after the render (CL-UI-95:
  // quick-ok / quick-mid / quick-bad from the chip's data-tier marker).
  assert.ok(appSource.includes("section.classList.remove('quick-ok','quick-mid','quick-bad')"), 'quick panel tier class wired');
  // The strip render call site stays pinned (cl-ui-05/12/22/75 contract).
  assert.match(appSource, /v2DayStripHtml\(days,labels,spot\.timezone,spot,opp\.genre_template\|\|'',opp\.opportunity_id\)/);
});

// ---- (3) extracted-function checks -----------------------------------------
const stripFns = (() => {
  const helperCode = grab('function compactHourSegmentsText', 'function v2ContractThreshold')
    + grab('function v2MetricName', '// CL-COPY-01: handwritten')
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
    const localDateString=()=>'2026-11-15';
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
  return new Function(prelude + helperCode + ';return {v2DayStripHtml};')();
})();

const DAYS_A = [
  {local_date: '2026-11-15', state: 'GUIDANCE_SATISFIED', good_hours: ['01:00', '02:00', '03:00', '04:00', '05:00', '06:00'], conditions: []},
  {local_date: '2026-11-16', state: 'UNFAVORABLE', good_hours: [], conditions: [{metric: 'precipitation', day_verdict: 'FAIL'}]},
  {local_date: '2026-11-17', state: 'NOT_EVALUABLE', good_hours: [], conditions: []},
  {local_date: '2026-11-18', state: 'GUIDANCE_SATISFIED', good_hours: ['05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00'], conditions: []},
  {local_date: '2026-11-19', state: 'UNFAVORABLE', good_hours: [], conditions: [{metric: 'cloud_cover_low', day_verdict: 'FAIL'}]},
  {local_date: '2026-11-20', state: 'GUIDANCE_SATISFIED', good_hours: ['16:00', '17:00', '18:00'], conditions: []},
  {local_date: '2026-11-21', state: 'GUIDANCE_SATISFIED', good_hours: ['06:00', '07:00'], conditions: []},
  {local_date: '2026-11-22', state: 'NOT_EVALUABLE', good_hours: [], conditions: []},
];
const DAYS_B = [
  {local_date: '2026-11-15', state: 'UNFAVORABLE', good_hours: [], conditions: [{metric: 'cloud_cover_low', day_verdict: 'FAIL'}]},
  {local_date: '2026-11-16', state: 'GUIDANCE_SATISFIED', good_hours: ['17:00', '18:00', '19:00', '20:00'], conditions: []},
  {local_date: '2026-11-17', state: 'GUIDANCE_SATISFIED', good_hours: ['06:00', '07:00'], conditions: []},
  {local_date: '2026-11-18', state: 'NOT_EVALUABLE', good_hours: [], conditions: []},
  {local_date: '2026-11-19', state: 'GUIDANCE_SATISFIED', good_hours: ['04:00', '05:00', '06:00', '07:00', '08:00'], conditions: []},
  {local_date: '2026-11-20', state: 'UNFAVORABLE', good_hours: [], conditions: [{metric: 'precipitation', day_verdict: 'FAIL'}]},
  {local_date: '2026-11-21', state: 'NOT_EVALUABLE', good_hours: [], conditions: []},
  {local_date: '2026-11-22', state: 'GUIDANCE_SATISFIED', good_hours: ['15:00'], conditions: []},
];
const LABELS = ['今天', '明天', '11/17', '11/18', '11/19', '11/20', '11/21', '11/22'];

test('CL-UI-88 (3): extracted v2DayStripHtml — compact slot + full tooltip + .sel', () => {
  const html = stripFns.v2DayStripHtml(DAYS_A, LABELS, 'Asia/Taipei', {spot_id: 'tw-179'}, 'star', 'tw-179-P01');
  const cells = html.match(/<button[\s\S]*?<\/button>/g) || [];
  assert.equal(cells.length, 8);
  // 時段字串永不截斷：compact 「01–05」 (no minute colon) in the cell text…
  // CL-UI-125 (owner ruling): the met cell carries ONE ✓ and no hour line —
  // the compact slot survives in the tooltip instead.
  assert.ok(cells[0].includes('<span class="v2-strip-mark" aria-hidden="true">✓</span>'), 'met cell carries the single check mark');
  assert.ok(!cells[0].includes('v2-strip-text'), 'no hour line under the mark');
  // …and the FULL unabbreviated segments ride the tooltip with the aria copy.
  assert.ok(cells[0].includes('title="今天 符合時數 6 · 01:00–06:00"'), 'full segments in tooltip');
  assert.ok(cells[0].includes('aria-label="今天 符合時數 6 · 01:00–06:00"'), 'aria parity');
  // The selected date (offset 0) carries .sel so centerSel can center it.
  assert.match(cells[0], /class="v2-strip-cell v2-ok sel"/);
  assert.ok(!cells[1].includes('sel"') && !cells[1].includes(' sel '), 'non-selected cells carry no .sel');
  // 橫移列：the strip element is the scroll container.
  assert.ok(html.startsWith('<div class="v2-day-strip" role="group">'));
});

// ---- (4) real-browser probe: two subject blocks, independent scrolling ------
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

const fixtureHtml = (() => {
  const a = stripFns.v2DayStripHtml(DAYS_A, LABELS, 'Asia/Taipei', {spot_id: 'tw-179'}, 'star', 'tw-179-P01');
  const b = stripFns.v2DayStripHtml(DAYS_B, LABELS, 'Asia/Taipei', {spot_id: 'tw-179'}, 'moon', 'tw-179-P02');
  return `<!doctype html><html lang="zh-TW"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CL-UI-88 fixture</title><link rel="stylesheet" href="/assets/app.css"></head>
<body style="margin:0"><div style="padding:12px;display:flex;flex-direction:column;gap:12px;max-width:420px">
<div data-block="P01">${a}</div><div data-block="P02">${b}</div></div></body></html>`;
})();

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
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui88-')), 'about:blank'],
    {stdio: ['ignore', 'ignore', 'pipe']});
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = '';
    // event-loop-aware wait: with --test-isolation=none these hooks run while later
    // test modules still import (heavy synchronous JSON parsing blocks the loop);
    // only unblocked wall-clock time counts toward the spawn deadline.
    let loopLast = Date.now(); const loopStart = loopLast;
    const t = setInterval(() => {
      const now = Date.now();
      if (now - loopLast < 1500 && now - loopStart > 20000) {
        clearInterval(t); reject(new Error('no devtools endpoint'));
      }
      loopLast = now;
    }, 250);
    chrome.stderr.on('data', d => { buf += d;
      const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
      if (m) { clearInterval(t); resolve(m[1]); } });
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
  const strips = [...document.querySelectorAll('.v2-day-strip')];
  const trunc = [], cellOverflow = [], rows = [];
  strips.forEach((s, si) => {
    [...s.querySelectorAll('.v2-strip-text,.v2-strip-day')].forEach(t => {
      if (t.scrollWidth > t.clientWidth) trunc.push(si + ':' + t.textContent);
    });
    [...s.querySelectorAll('.v2-strip-cell')].forEach(c => {
      if (c.scrollWidth > c.clientWidth + 1) cellOverflow.push(si + ':' + c.dataset.idx);
    });
    const tops = new Set([...s.querySelectorAll('.v2-strip-cell')].map(c => c.offsetTop));
    rows.push(tops.size);
    s._sw = s.scrollWidth; s._cw = s.clientWidth;
    s._mask = getComputedStyle(s).maskImage || getComputedStyle(s).webkitMaskImage || 'none';
  });
  // 多題材區塊各自日期列可獨立橫移：slide strip A, strip B must not move.
  const a = strips[0], b = strips[1];
  const before = b.scrollLeft;
  a.scrollLeft = 80;
  const afterA = a.scrollLeft, afterB = b.scrollLeft;
  b.scrollLeft = 40;
  const bSlide = b.scrollLeft, aHeld = a.scrollLeft;
  a.scrollLeft = 0; b.scrollLeft = 0;
  return {
    strips: strips.length,
    cellsPerStrip: strips.map(s => s.querySelectorAll('.v2-strip-cell').length),
    oneRow: rows.every(r => r === 1),
    truncated: trunc,
    cellOverflow,
    scrollable: [{sw: a._sw, cw: a._cw}, {sw: b._sw, cw: b._cw}],
    masks: strips.map(s => s._mask),
    indep: {before, afterA, afterB, bSlide, aHeld},
    hasSel: strips.some(s => s.querySelector('.v2-strip-cell.sel')),
  };
})()`;

for (const vp of [{name: 'desktop 1280px', w: 1280, h: 900, mobile: false, shot: 'clui88-desktop-1280'},
                  {name: 'mobile 390px', w: 390, h: 844, mobile: true, shot: 'clui88-mobile-390'}]) {
  test(`CL-UI-88 (4): ${vp.name} — no truncation, fade hints, independent slide`, async () => {
    await send('Emulation.setDeviceMetricsOverride', {width: vp.w, height: vp.h, deviceScaleFactor: 1, mobile: vp.mobile});
    await send('Page.enable');
    await send('Page.navigate', {url: baseURL});
    await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
    await new Promise(r => setTimeout(r, 300));
    const probe = await evaljs(PROBE);
    assert.equal(probe.strips, 2, 'two subject blocks, two independent strips');
    assert.deepEqual(probe.cellsPerStrip, [8, 8], 'all day cells present');
    assert.equal(probe.oneRow, true, 'every cell sits on ONE row');
    assert.deepEqual(probe.truncated, [], `no in-cell copy is truncated (got ${JSON.stringify(probe.truncated)})`);
    assert.deepEqual(probe.cellOverflow, [], `no cell overflows its own box — scrollWidth === clientWidth (got ${JSON.stringify(probe.cellOverflow)})`);
    assert.ok(probe.hasSel, 'the selected date cell carries .sel');
    for (const m of probe.masks) {
      const mask = String(m);
      assert.ok(mask.includes('linear-gradient(90deg') && mask.includes('calc(100% - 8px)') && mask.includes(' 8px'),
        `two-side fade hint on every strip: ${mask}`);
    }
    if (vp.w < 768) {
      // CL-UI-125: with the hour line gone the eight cells may FIT at 390px —
      // sliding is then unnecessary (the fade hint stays for when it does not).
      assert.ok(probe.scrollable[0].sw >= probe.scrollable[0].cw, 'the date row never clips: it fits or slides');
      const slides = probe.scrollable[0].sw > probe.scrollable[0].cw;
      if (!slides) {
        // CL-UI-125: eight ✓-only cells fit a 390px row, so there is nothing to
        // slide — independence is vacuous, not violated.
        assert.equal(probe.indep.afterA, 0, 'a fitting strip needs no horizontal offset');
      } else {
        assert.ok(probe.indep.afterA > 0 && probe.indep.afterA <= 80, `strip A slid to its own offset (${probe.indep.afterA})`);
        assert.equal(probe.indep.afterB, probe.indep.before, 'strip B never moved with A');
        assert.ok(probe.indep.bSlide > 0, 'strip B slides on its own');
        assert.equal(probe.indep.aHeld, probe.indep.afterA, 'strip A holds its position while B slides');
      }
    }
    console.log(vp.shot + ' probe: ' + JSON.stringify(probe));
    // Visual evidence screenshot (not committed).
    const shot = await send('Page.captureScreenshot', {format: 'png'});
    const shotDir = process.env.CLUI88_SHOT_DIR || tmpdir();
    const file = join(shotDir, vp.shot + '.png');
    const {writeFileSync} = await import('node:fs');
    writeFileSync(file, Buffer.from(shot.data, 'base64'));
    console.log(`screenshot: ${file}`);
  });
}
