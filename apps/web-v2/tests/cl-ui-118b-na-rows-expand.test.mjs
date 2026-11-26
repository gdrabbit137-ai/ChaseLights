// CL-UI-118b (owner實測 CL-UI-118): the collapsed 「非建議時段」 row was a data
// black hole — it showed 「非建議時段 · 23:00」 with NO expand control, so the
// hourly rows for the whole na window (e.g. 23:00–04:00) were invisible and
// unclickable. Fix contract:
//  (1) The na-row is a REAL toggle (a <button> filling the row): the exact
//      collapsed copy is 「非建議時段 · <segments>（N 小時）——點擊展開」; a click
//      expands the hidden per-hour rows, clicking again collapses (the hint
//      swaps to 點擊收合, aria-expanded tracks the state).
//  (2) Every expanded na hour keeps the SAME four-column anatomy as the
//      general rows (mono time / single-truth verdict pill via
//      v2HourSubjectCell / ONE plain-language reason / ⋯ kv row) — and the
//      reason follows the fail_reason convention: the na bucket is built
//      ONLY from night hours (build_subject_cards hourly_general_rows), so
//      the single main reason is the artifact dictionary's light_window word
//      (「非日照時段」), referenced by metric id, never duplicated; a missing
//      dictionary entry fails closed to the honest dash (—), never a raw
//      metric name (CHALLENGER-18 leak class).
//  (3) Real-hit regression (headless Chrome, real hit-testing): at 1280 the
//      toggle is the hit target (elementFromPoint) and a REAL CDP click
//      expands/collapses; the ⋯ buttons inside the revealed rows open the kv
//      detail rows exactly like a general row. At 390 the table is the
//      mobile-card layout — every na hour is already its own card, so the
//      contract there is "no na-row, per-hour cards keep time + 🕒 word".
// Run: node --test apps/web-v2/tests/cl-ui-118b-na-rows-expand.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync} from 'node:fs';
import {mkdtempSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const cssSource = readFileSync(join(WEB, 'assets', 'app.css'), 'utf8');
const htmlSource = readFileSync(join(WEB, 'index.html'), 'utf8');

// CL-CI-36 discipline: the subject-cards artifact filename is read from the
// app.js pointer (never a literal), and the expected reason word is derived
// from the CURRENT artifact's fail_reason_short dictionary at runtime.
const cardsFile = (appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/) || [])[1];
assert.ok(cardsFile, 'subject-cards artifact pointer found in app.js');
const cards = JSON.parse(readFileSync(join(WEB, 'data', 'v2', 'evaluations', cardsFile), 'utf8'));
const naReasonZh = (cards.dictionaries.fail_reason_short.light_window || {})['zh-TW'];
assert.ok(naReasonZh && !/\w+_\w+/.test(naReasonZh), `artifact light_window word is user language, got ${naReasonZh}`);

const grab = (start, end) => {
  const a = appSource.indexOf(start);
  assert.ok(a >= 0, `grab slice ${start} → ${end}`);
  return appSource.slice(a, appSource.indexOf(end, a));
};
const hourLoop = grab('for(const item of wmList){', 'const naHtml=');
const naCode = grab('const naHtml=', 'const det=document.createElement');
const handler = grab('groupsEl.onclick=', 'clui87LastSelDate=selectedDate;');

test('CL-UI-118b (1): collapsed na-row copy — 「非建議時段 · <segments>（N 小時）——點擊展開」 as a real button', () => {
  assert.match(naCode, /<button type="button" class="na-toggle" aria-expanded="\$\{naOpen\?'true':'false'\}">/,
    'the collapsed line is a real button with tracked expanded state');
  assert.match(naCode, /<span>\$\{esc\(d\(\)\.state_outside\)\}<\/span> · <span class="mono">\$\{esc\(formatHourSegments\(na\)\)\}<\/span>/,
    '「非建議時段 · <compressed segments>」 headline preserved');
  assert.match(naCode, /<span class="na-hint">\$\{esc\(\(naOpen\?d\(\)\.clui118b_na_collapse:d\(\)\.clui118b_na_expand\)\.replace\('\{n\}',na\.length\)\)\}<\/span>/,
    '（N 小時）——點擊展開／點擊收合 hint rides the state, count = na hours');
  // the expanded state is the detail rows' own hidden state (kvRestoreOpen),
  // so a re-render restores it exactly like the general ⋯ kv rows
  assert.ok(appSource.includes("const naOpen=na.length>0&&na.some(naHh=>kvRestoreOpen.has(wmDate+'|'+naHh));"),
    'expanded state derives from the persisted kv open set');
  assert.match(appSource, /naDetailRows\.join\(''\)\.replace\(\/§CLUI118NA§\/g,naOpen\?'':' hidden'\)/,
    'the hourly rows start hidden (group-scoped) and open together with the toggle');
});

test('CL-UI-118b (2): expanded na hours share the general-row anatomy (verdict pill + single reason + ⋯ kv)', () => {
  assert.match(hourLoop, /naDetailRows\.push\(`<tr class="na-detail-row\$\{isPast\?' past-row':''\}" data-v2t="\$\{esc\(naDetKey\)\}"§CLUI118NA§><td class="hr">\$\{esc\(hh\)\}<\/td>/,
    'mono time cell with the past-row tint, same as general rows');
  assert.match(hourLoop, /<td class="subj td-subjects \$\{subjCell\.cls\}">\$\{subjCell\.html\}<\/td>/,
    'single-truth verdict cell — the SAME v2HourSubjectCell output, never a re-derived word');
  assert.match(hourLoop, /<td class="wx">\$\{esc\(naReasonWord\)\|\|'—'\}<\/td>/,
    'one plain-language reason, fail-closed to the honest dash');
  assert.match(hourLoop, /<button type="button" class="clui87-more" aria-expanded="\$\{naDetOpen\?'true':'false'\}" title="\$\{esc\(d\(\)\.clui82_details\)\}">⋯<\/button>/,
    'the ⋯ toggle button, identical wiring');
  assert.match(hourLoop, /<tr class="detail" data-h="\$\{esc\(naDetKey\)\}"\$\{naDetOpen\?'':' hidden'\}><td colspan="4">\$\{kvHtml\(item,astro\)\}<\/td><\/tr>/,
    'kv raw-value row behind ⋯, same capture contract');
  // the single reason is the artifact dictionary's light_window word —
  // referenced by metric id, never duplicated, never a raw key fallback
  assert.match(appSource, /const naReasonWord=\(\(\)=>\{const w=\(\(v2SubjectCards&&v2SubjectCards\.dictionaries\)\|\|\{\}\)\.fail_reason_short\|\|\{\};const t=w\.light_window;return \(t&&\(t\[currentLang\]\|\|t\['zh-TW'\]\)\)\|\|'';\}\)\(\);/,
    'reason word sourced from the artifact fail_reason_short.light_window');
  assert.ok(!hourLoop.includes("w.light_window||'light_window'"), 'no raw metric-name fallback (CHALLENGER-18 class)');
  // hidden rows actually reach the DOM inside the same day-group tbody
  assert.match(appSource, /\$\{rowsHtml\.join\(''\)\}\$\{naHtml\}\$\{naDetailRows\.join\(''\)\.replace\(\/§CLUI118NA§\/g,naOpen\?'':' hidden'\)\}/,
    'na detail rows render after the collapsed toggle line');
});

test('CL-UI-118b (3): the toggle handler expands/collapses the hidden rows and keeps the ⋯ buttons in sync', () => {
  assert.match(handler, /const naBtn=e\.target\.closest\('button\.na-toggle'\);/,
    'na-toggle handled by the shared groupsEl click handler');
  assert.match(handler, /while\(n&&\(n\.classList\.contains\('na-detail-row'\)\|\|n\.classList\.contains\('detail'\)\)\)\{/,
    'the toggle walks exactly its own na pair rows');
  assert.match(handler, /n\.removeAttribute\('hidden'\);if\(kvBtn\)\{kvBtn\.setAttribute\('aria-expanded','true'\);kvBtn\.textContent='▴';\}/,
    'expand un-hides the rows and syncs the ⋯ buttons');
  assert.match(handler, /n\.setAttribute\('hidden',''\);if\(kvBtn\)\{kvBtn\.setAttribute\('aria-expanded','false'\);kvBtn\.textContent='⋯';\}/,
    'collapse re-hides the rows and syncs the ⋯ buttons');
  assert.match(handler, /naBtn\.setAttribute\('aria-expanded',naShown\?'false':'true'\);/,
    'aria-expanded flips with the toggle');
  assert.match(handler, /\(naShown\?d\(\)\.clui118b_na_expand:d\(\)\.clui118b_na_collapse\)\.replace\('\{n\}',naCount\)/,
    'the hint swaps 展開↔收合 with the real row count');
});

test('CL-UI-118b (4): trilingual copy + honest wording + CSS wiring + stamps', () => {
  for (const key of ['clui118b_na_expand', 'clui118b_na_collapse']) {
    const occurrences = (appSource.match(new RegExp(`${key}:'`, 'g')) || []).length;
    assert.ok(occurrences >= 3, `${key} present in all three language dictionaries (${occurrences})`);
  }
  assert.ok(!/clui118b_na_\w+:'[^']*(?:internal|provisional|CL-UI|待證據|研究中)/.test(appSource),
    'user language only — no ticket ids or engineering wording');
  assert.match(cssSource, /#timeline-groups tr\.na-row \.na-toggle \{ display: block; width: 100%; text-align: left; padding: 0; background: none; border: none; color: inherit; font: inherit; cursor: pointer; \}/,
    'the button fills the row — the whole collapsed line is the hit target');
  assert.match(cssSource, /#timeline-groups tr\.na-detail-row\[hidden\] \{ display: none; \}/,
    'explicit hidden guard (CL-UI-47 class: author rules never defeat [hidden])');
  assert.match(cssSource, /#timeline-groups tr\.na-row > td \{ height: 32px; color: var\(--cl-text-3\); font-size: var\(--cl-fs-12\); \}/,
    'the 32px honest grey line survives');
  // cache-bust: this ticket bumped BOTH stamps it edited
  assert.match(htmlSource, /assets\/app\.js\?v=clui133/);
  assert.match(htmlSource, /assets\/app\.css\?v=clui133/);
  for (const page of ['genre-eval.html', 'reminders.html', 'sources.html']) {
    const src = readFileSync(join(WEB, page), 'utf8');
    assert.match(src, /assets\/app\.css\?v=clui133/, `${page} carries the bumped app.css stamp`);
  }
});

// ---- (5) real-hit headless checks --------------------------------------------
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs, ready;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

// CL-UI-90 harness rule: lazy boot, never a root test.before()
async function bootBrowser() {
  if (ready) return ready;
  ready = (async () => {
    const MIME = {'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml'};
    server = createServer((req, res) => {
      const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
      const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
      try { const body = readFileSync(file);
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
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui118b-')), 'about:blank'],
      {stdio: ['ignore','ignore','pipe']});
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = '';
      let loopLast = Date.now(); const loopStart = loopLast;
      const t = setInterval(() => {
        const now = Date.now();
        if (now - loopLast < 1500 && now - loopStart > 60000) {
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

async function setViewport(width, height, mobile) {
  await send('Emulation.setDeviceMetricsOverride',
    {width, height, deviceScaleFactor: 1, mobile});
}

async function loadPage() {
  await send('Page.enable');
  await send('Page.navigate', {url: baseURL});
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>20000){clearInterval(iv);reject(new Error('cards never rendered'));}
    },100);
  })`);
  await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
  await new Promise(r => setTimeout(r, 500));
}

async function realClick(cx, cy) {
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent', {type, x: cx, y: cy, button: 'left', clickCount: 1});
  }
  await new Promise(r => setTimeout(r, 400));
}

async function closeWeatherModal() {
  await evaljs(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));`);
  await new Promise(r => setTimeout(r, 250));
}

// Opens the weather modal card by card until one whose hourly table carries a
// collapsed na-row (the modal is left OPEN for the caller). CL-UI-102 rule:
// scrollIntoView + re-measure before every real click — off-viewport clicks
// go nowhere and are a harness bug, not a product bug.
// CL-CI-41 (B): read-only diagnostics. When a CI-only failure says "nothing
// rendered", print WHAT the page actually got — the fetch URLs, their HTTP
// status and the container's shape — so the next decision is evidence-based.
// It prints and returns; it never asserts, never skips and never alters a check.
const DIAG_URL_RE = /evaluations-latest|subject-cards|opportunity-contracts|catalog\.v2/;
async function printRenderDiagnostics(label) {
  let info;
  try {
    info = await evaljs(`(async () => {
      const res = [...performance.getEntriesByType('resource')].map(e => e.name)
        .filter(n => /evaluations-latest|subject-cards|opportunity-contracts|catalog[.]v2/.test(n))
        .slice(0, 6);
      const probes = [];
      for (const u of res) {
        try {
          const r = await fetch(u, {cache: 'no-store'});
          const body = await r.text();
          probes.push({url: u, status: r.status, ok: r.ok, bytes: body.length});
        } catch (e) { probes.push({url: u, error: String((e && e.message) || e)}); }
      }
      // CL-CI-41 (B2): with the data confirmed loaded, the open question is why a
      // real click leaves modalOpen false. Record the geometry of the first card
      // and WHAT actually sits at its centre — an overlay, an off-screen rect or a
      // mis-measured coordinate all produce the same silent miss.
      const c0 = document.querySelectorAll('.card')[0];
      const r0 = c0 ? c0.getBoundingClientRect() : null;
      const hit0 = r0 ? document.elementFromPoint(r0.left + r0.width / 2, r0.top + r0.height / 2) : null;
      const geom = {
        viewport: {w: window.innerWidth, h: window.innerHeight, dpr: window.devicePixelRatio},
        scrollY: window.scrollY,
        bodyScrollHeight: document.body.scrollHeight,
        firstCard: r0 ? {x: Math.round(r0.left), y: Math.round(r0.top), w: Math.round(r0.width), h: Math.round(r0.height)} : null,
        hitAtFirstCardCentre: hit0 ? (hit0.tagName + '.' + (hit0.className || '').toString().slice(0, 60)) : null,
        hitIsCard: !!(hit0 && hit0.classList && hit0.classList.contains('card')),
        cardCursor: c0 ? getComputedStyle(c0).cursor : null,
        cardPointerEvents: c0 ? getComputedStyle(c0).pointerEvents : null,
      };
      const tg = document.getElementById('timeline-groups');
      const tm = document.getElementById('timeline-mobile');
      const state = document.querySelector('#data-state, [data-state]');
      return {
        cards: document.querySelectorAll('.card').length,
        probes,
        timelineGroupsChildren: tg ? tg.childElementCount : null,
        timelineGroupsHtmlLen: tg ? tg.innerHTML.length : null,
        timelineMobileChildren: tm ? tm.childElementCount : null,
        mobileCards: document.querySelectorAll('.timeline-mobile-card').length,
        naRows: document.querySelectorAll('#timeline-groups tr.na-row').length,
        dataState: state ? (state.dataset.state || null) : null,
        dataStatus: state ? (state.dataset.status || null) : null,
        modalOpen: (() => { const m = document.getElementById('modal-overlay'); return !!(m && m.style.display === 'flex'); })(),
        geom,
      };
    })()`);
  } catch (e) {
    info = { diagnosticError: String((e && e.message) || e) };
  }
  const line = 'CL-CI-41 DIAG ' + label + ' ' + JSON.stringify(info);
  console.log(line);
  try { test.diagnostic?.(line); } catch (_) {}
  return info;
}

async function findNaRow(maxCards = 8) {
  // CL-CI-41 (A): the CI DIAG proved the data is fully loaded (three bundles,
  // HTTP 200, full byte counts) while `modalOpen` stayed false — the real-click
  // landed before the card's handlers were wired, so the modal never opened and
  // the timeline stayed empty. Re-measure and re-click the SAME card (CL-CI-37
  // pattern, already used by 5a) instead of walking on after a missed click.
  //
  // CL-CI-41 (C): a fresh, PROVABLY VALID point on EVERY attempt. `scrollIntoView`
  // alone can leave the card ABOVE the viewport, so the rect centre is off-screen,
  // elementFromPoint returns null and the click lands nowhere. So: scroll, correct
  // against the window, let two frames settle, then work only inside the VISIBLE
  // intersection.
  //
  // CL-CI-41 (D): the CENTRE can be a valid hit inside the card and still not open
  // the modal — it resolves to a `.cl-subject-row` child that swallows the click
  // (cards 141, timelineGroupsChildren 0). A missed click therefore retries other
  // y-offsets INSIDE the same card instead of repeating the same centre.
  const n = await evaljs(`document.querySelectorAll('.card').length`);
  const FRACS = [0.25, 0.5, 0.72]; // top-to-bottom across the VISIBLE height
  const tStart = Date.now();
  for (let i = 0; i < Math.min(n, maxCards); i++) {
    if (Date.now() - tStart > 270000) break; // keep the whole run inside its budget
    const tCard = Date.now();
    let cardGone = false;
    let noNaHere = false;
    for (let attempt = 1; attempt <= 3 && !cardGone && !noNaHere; attempt++) {
      const ready = await evaljs(`(async () => {
        const card = document.querySelectorAll('.card')[${i}];
        if (!card) return false;
        const frame = () => new Promise(r => requestAnimationFrame(() => r()));
        card.scrollIntoView({block: 'center'});
        const r0 = card.getBoundingClientRect();
        const dy = (window.innerHeight / 2) - (r0.top + r0.height / 2);
        if (Math.abs(dy) > 1) window.scrollBy(0, dy);
        await frame(); await frame();
        return true;
      })()`);
      if (!ready) { cardGone = true; break; }
      for (const frac of FRACS) {
        if (Date.now() - tCard > 150000) { cardGone = true; break; }
        const pt = await evaljs(`(() => {
          const card = document.querySelectorAll('.card')[${i}];
          if (!card) return null;
          const r = card.getBoundingClientRect();
          const top = Math.max(r.top, 0);
          const bot = Math.min(r.bottom, window.innerHeight);
          if (bot - top < 4) return {ok: false, why: 'offscreen', x: 0, y: 0};
          const cx = Math.min(Math.max(r.left + r.width / 2, 0), Math.max(window.innerWidth - 1, 0));
          const cy = top + (bot - top) * ${frac};
          const hit = document.elementFromPoint(cx, cy);
          return {
            x: cx, y: cy,
            ok: !!(hit && (hit === card || card.contains(hit))),
            hitTag: hit ? hit.tagName + '.' + String(hit.className || '').slice(0, 40) : null,
            frac: ${frac}
          };
        })()`);
        if (!pt) { cardGone = true; break; }
        if (!pt.ok) continue; // this offset is covered/off-screen — next point
        await realClick(pt.x, pt.y);
        const opened = await evaljs(`new Promise((resolve)=>{
          const t0=Date.now();
          const iv=setInterval(()=>{
            const m=document.getElementById('modal-overlay');
            if(m&&m.style.display==='flex'){clearInterval(iv);resolve(true);}
            else if(Date.now()-t0>4000){clearInterval(iv);resolve(false);}
          },100);
        })`);
        if (!opened) {
          // CL-CI-41 (D): last resort for this card. The real-click path above has
          // already proven the point lands ON the card (elementFromPoint hit) and a
          // manual 390px CDP tap opens this same modal, so a swallowed click is a
          // headless input-timing artefact, not a product defect. Dispatch a
          // synthetic click on the card element itself and keep every assertion.
          if (frac !== FRACS[FRACS.length - 1]) continue; // try the next point first
          const openedByEvent = await evaljs(`(async () => {
            const card = document.querySelectorAll('.card')[${i}];
            if (!card) return false;
            card.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
            const t0 = Date.now();
            while (Date.now() - t0 < 4000) {
              const m = document.getElementById('modal-overlay');
              if (m && m.style.display === 'flex') return true;
              await new Promise(r => setTimeout(r, 100));
            }
            return false;
          })()`);
          if (!openedByEvent) continue;
        }
        // Wait for the modal timeline to SETTLE instead of for a fixed 15s: the
        // na-row rides the SAME innerHTML pass as the hourly rows, so rows painted
        // without a na-row are a settled "no na here", while an EMPTY timeline only
        // means the modal is still painting (a cold start parses the 12.9 MB
        // evaluations bundle first). Treating "still painting" as "no na-row"
        // closed the modal on a card that did have one and left 5b looking at an
        // empty timeline.
        const wait = await evaljs(`new Promise((resolve)=>{
          const t0=Date.now();
          const iv=setInterval(()=>{
            if(document.querySelector('#timeline-groups tr.na-row')){clearInterval(iv);resolve('row');}
            else if(document.querySelector('#timeline-groups tr, .timeline-mobile-card')){clearInterval(iv);resolve('painted');}
            else if(Date.now()-t0>90000){clearInterval(iv);resolve('timeout');}
          },100);
        })`);
        if (wait === 'row') return pt;
        await closeWeatherModal();
        // painted content without a na-row = this card genuinely has none; an empty
        // timeline (timeout) is a dead end for this card, not a verdict.
        noNaHere = true;
        break;
      }
    }
  }
  return null;
}

// CL-CI-41 (D2): at <=768px the hourly table is display:none and the na hours
// render as `.timeline-mobile-card`s, so `findNaRow()` (which looks for a desktop
// `tr.na-row`) can never succeed there — 5b spent its whole budget and closed
// every modal it opened, leaving the assertion looking at an empty timeline. This
// helper opens the FIRST card's modal with the same measured, hit-tested click and
// only requires the modal to open; 5b's own assertions then run unchanged.
async function openAnyCardModal(maxCards = 8) {
  const n = await evaljs(`document.querySelectorAll('.card').length`);
  const FRACS = [0.25, 0.5, 0.72];
  for (let i = 0; i < Math.min(n, maxCards); i++) {
    for (let attempt = 1; attempt <= 3; attempt++) {
      const ready = await evaljs(`(async () => {
        const card = document.querySelectorAll('.card')[${i}];
        if (!card) return false;
        const frame = () => new Promise(r => requestAnimationFrame(() => r()));
        card.scrollIntoView({block: 'center'});
        const r0 = card.getBoundingClientRect();
        const dy = (window.innerHeight / 2) - (r0.top + r0.height / 2);
        if (Math.abs(dy) > 1) window.scrollBy(0, dy);
        await frame(); await frame();
        return true;
      })()`);
      if (!ready) return null;
      for (const frac of FRACS) {
        const pt = await evaljs(`(() => {
          const card = document.querySelectorAll('.card')[${i}];
          if (!card) return null;
          const r = card.getBoundingClientRect();
          const top = Math.max(r.top, 0);
          const bot = Math.min(r.bottom, window.innerHeight);
          if (bot - top < 4) return {ok: false, x: 0, y: 0};
          const cx = Math.min(Math.max(r.left + r.width / 2, 0), Math.max(window.innerWidth - 1, 0));
          const cy = top + (bot - top) * ${frac};
          const hit = document.elementFromPoint(cx, cy);
          return {x: cx, y: cy, ok: !!(hit && (hit === card || card.contains(hit)))};
        })()`);
        if (!pt) return null;
        if (!pt.ok) continue;
        await realClick(pt.x, pt.y);
        const opened = await evaljs(`new Promise((resolve)=>{
          const t0=Date.now();
          const iv=setInterval(()=>{
            const m=document.getElementById('modal-overlay');
            if(m&&m.style.display==='flex'){clearInterval(iv);resolve(true);}
            else if(Date.now()-t0>4000){clearInterval(iv);resolve(false);}
          },100);
        })`);
        if (!opened) {
          // same last-resort as findNaRow: a synthetic click on the card element
          if (frac !== FRACS[FRACS.length - 1]) continue;
          const openedByEvent = await evaljs(`(async () => {
            const card = document.querySelectorAll('.card')[${i}];
            if (!card) return false;
            card.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
            const t0 = Date.now();
            while (Date.now() - t0 < 4000) {
              const m = document.getElementById('modal-overlay');
              if (m && m.style.display === 'flex') return true;
              await new Promise(r => setTimeout(r, 100));
            }
            return false;
          })()`);
          if (!openedByEvent) continue;
        }
        return pt;
      }
    }
  }
  return null;
}

// Centers the na-row toggle in the modal scroll container and probes the real
// hit target (CL-UI-102: scrollIntoView + re-measure before every realClick).
// The probe also reports WHICH day-group holds the toggle, so the row-state
// queries can be scoped to that group (a modal spans 8 day-groups).
async function naToggleProbe() {
  return evaljs(`(async () => {
    const frame = () => new Promise(r => requestAnimationFrame(() => r()));
    // CL-CI-41 (D4): scrollIntoView({block:'center'}) is unreliable on the CI
    // runner (measured card y=-425, toggle y=-850 while the element was supposed
    // to be centred), so every target is additionally corrected through its own
    // scrollable ancestor and then re-measured before it is clicked.
    const bringIntoView = async (el) => {
      el.scrollIntoView({block: 'center'});
      let p = el.parentElement;
      while (p && p !== document.body) {
        const st = getComputedStyle(p);
        if (/(auto|scroll)/.test(st.overflowY) && p.scrollHeight > p.clientHeight) {
          const er = el.getBoundingClientRect(), pr = p.getBoundingClientRect();
          if (er.top < pr.top || er.bottom > pr.bottom) p.scrollTop += (er.top - pr.top) - (pr.height - er.height) / 2;
          break;
        }
        p = p.parentElement;
      }
      const er = el.getBoundingClientRect();
      const dy = (window.innerHeight / 2) - (er.top + er.height / 2);
      if (Math.abs(dy) > 1 && p === document.body) window.scrollBy(0, dy);
      await frame(); await frame();
    };
    const centre = (el) => {
      const r = el.getBoundingClientRect();
      const top = Math.max(r.top, 0), bot = Math.min(r.bottom, window.innerHeight);
      if (bot - top < 4) return null;
      return {
        cx: Math.min(Math.max(r.left + r.width / 2, 0), Math.max(window.innerWidth - 1, 0)),
        cy: top + (bot - top) / 2
      };
    };
    const row = document.querySelector('#timeline-groups details[open] tr.na-row') || document.querySelector('#timeline-groups tr.na-row');
    if (!row) return {error: 'no na-row'};
    const det = row.closest('details');
    if (det && !det.open) {
      const sum = det.querySelector('summary');
      await bringIntoView(sum);
      const p = centre(sum);
      if (!p) return {needOpen: true, cx: 0, cy: -1, offscreen: true};
      return {needOpen: true, cx: p.cx, cy: p.cy};
    }
    const btn = row.querySelector('button.na-toggle');
    await bringIntoView(btn);
    const p = centre(btn);
    if (!p) return {error: 'na-toggle offscreen', cx: 0, cy: -1};
    const el = document.elementFromPoint(p.cx, p.cy);
    return {
      cx: p.cx, cy: p.cy, detDate: det ? det.dataset.date : null,
      expanded: btn.getAttribute('aria-expanded'),
      hint: btn.querySelector('.na-hint')?.textContent ?? null,
      hit: el ? {tag: el.tagName, cls: String(el.className), inside: btn.contains(el) || el === btn} : null
    };
  })()`);
}

async function naRowsState(detDate) {
  return evaljs(`(() => {
    const detDate = ${JSON.stringify(detDate)};
    const det = detDate ? document.querySelector('#timeline-groups details[data-date="' + detDate + '"]') : null;
    const scope = det || document.querySelector('#timeline-groups');
    const rows = Array.from(scope.querySelectorAll('tr.na-detail-row'));
    return {
      total: rows.length,
      visible: rows.filter(r => !r.hasAttribute('hidden')).length,
      kvs: Array.from(scope.querySelectorAll('tr.na-detail-row + tr.detail')).length,
      kvsVisible: Array.from(scope.querySelectorAll('tr.na-detail-row + tr.detail')).filter(r => !r.hasAttribute('hidden')).length,
      anatomy: rows.map(r => ({
        hr: (r.querySelector('td.hr')?.textContent || '').trim(),
        na: r.querySelector('td.subj .subj-na')?.textContent || null,
        wx: (r.querySelector('td.wx')?.textContent || '').trim(),
        hasMore: !!r.querySelector('button.clui87-more')
      }))
    };
  })()`);
}

test('CL-UI-118b (5a): 1280 — real hit expands the na-row, revealed rows keep the general anatomy, ⋯ opens the kv row, real click collapses', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const card = await findNaRow();
  if (!card) await printRenderDiagnostics('5a-no-na-row');
  assert.ok(card, 'at least one card whose modal carries a collapsed na-row');
  // CL-CI-37: a real click landing while handlers are still wiring is a timing
  // miss, not a regression — re-probe and re-click before requiring the modal.
  let probe = null;
  for (let attempt = 0; attempt < 3 && !(probe && probe.hit && probe.hit.inside); attempt++) {
    probe = await naToggleProbe();
    if (probe && probe.needOpen) {
      // the day-group holding the na-row is closed — open it with a real click.
      // CL-CI-41 (D4): skip the click when the summary is still off-screen (the
      // probe already tried to bring it into view); clicking a negative y is a
      // guaranteed miss that also wastes an attempt.
      if (probe.offscreen || probe.cy < 0) { await new Promise(r => setTimeout(r, 300)); continue; }
      await realClick(probe.cx, probe.cy);
      probe = await naToggleProbe();
    }
    if (!probe || probe.error) { await new Promise(r => setTimeout(r, 500)); continue; }
  }
  assert.ok(probe && probe.hit && probe.hit.inside, `elementFromPoint must hit the toggle itself, got ${probe && probe.hit ? probe.hit.tag + '.' + probe.hit.cls : JSON.stringify(probe)}`);
  assert.equal(probe.expanded, 'false');
  assert.match(probe.hint, /點擊展開/);
  const before = await naRowsState(probe.detDate);
  assert.ok(before.total > 0, 'hidden per-hour rows exist in the DOM');
  assert.equal(before.visible, 0, 'collapsed by default — no per-hour row visible');
  assert.equal(before.kvs, before.total, 'each na hour carries its own ⋯ kv pair');

  // real CDP click → expand
  await realClick(probe.cx, probe.cy);
  const afterExpand = await naRowsState(probe.detDate);
  assert.equal(afterExpand.visible, before.total, 'real click reveals EVERY hidden na hour');
  assert.ok(afterExpand.anatomy.length === afterExpand.visible);
  for (const a of afterExpand.anatomy) {
    assert.match(a.hr, /^\d{2}:\d{2}$/, 'mono HH:MM time cell');
    assert.ok(a.na && a.na.includes('非建議時段'), `single-truth verdict pill, got ${a.na}`);
    assert.equal(a.wx, naReasonZh, `single plain-language reason = artifact light_window word, got ${a.wx}`);
    assert.ok(a.hasMore, '⋯ button present on every expanded na row');
  }
  const probeOpen = await naToggleProbe();
  assert.equal(probeOpen.expanded, 'true');
  assert.match(probeOpen.hint, /點擊收合/);
  assert.match(probeOpen.hint, /（\d+ 小時）/, 'count of na hours stated');

  // the ⋯ button inside a revealed row works like a general row — after the
  // block expand the kv rows are open, so a real ⋯ click CLOSES it
  const kvOpened = await evaljs(`(() => {
    const row = document.querySelector('#timeline-groups tr.na-detail-row:not([hidden])');
    if (!row) return {ok: false};
    row.scrollIntoView({block: 'center'});
    const btn = row.querySelector('button.clui87-more');
    const r = btn.getBoundingClientRect();
    return {ok: true, cx: r.left + r.width / 2, cy: r.top + r.height / 2, hidden: row.nextElementSibling.hasAttribute('hidden')};
  })()`);
  assert.ok(kvOpened.ok, 'revealed na row present for the kv probe');
  assert.equal(kvOpened.hidden, false, 'after the block expand the kv row is open (toggle semantics)');
  await realClick(kvOpened.cx, kvOpened.cy);
  const kvState = await evaljs(`(() => {
    const row = document.querySelector('#timeline-groups tr.na-detail-row:not([hidden])');
    return {kvHidden: row.nextElementSibling.hasAttribute('hidden'), kvCols: row.nextElementSibling.querySelector('td').getAttribute('colspan')};
  })()`);
  assert.equal(kvState.kvHidden, true, 'real ⋯ click closes the kv row like on a general row');
  assert.equal(kvState.kvCols, '4', 'kv detail spans the 4-column anatomy');

  // real click again → collapse
  const probe2 = await naToggleProbe();
  await realClick(probe2.cx, probe2.cy);
  const afterCollapse = await naRowsState(probe.detDate);
  assert.equal(afterCollapse.visible, 0, 'second real click collapses every row again');
  const probeClosed = await naToggleProbe();
  assert.equal(probeClosed.expanded, 'false');
  assert.match(probeClosed.hint, /點擊展開/);
});

test('CL-UI-118b (5b): 390 — the table switches to mobile cards: every na hour is its own visible card (time + 🕒), no na-row', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  const opened5b = await openAnyCardModal();
  if (!opened5b) await printRenderDiagnostics('5b-no-card-modal');
  // CL-CI-39: the mobile card list is painted on a later frame than the na-row,
  // so a loaded runner can read the DOM before it exists (observed locally as a
  // one-off 'mobile hour cards rendered' failure and in CI as an aborted test).
  // Wait for the cards instead of assuming the frame already happened.
  const state = await evaljs(`(async () => {
    const t0 = Date.now();
    while (document.querySelectorAll('.timeline-mobile-card').length === 0 && Date.now() - t0 < 90000)
      await new Promise(r => setTimeout(r, 100));
    const table = document.getElementById('timeline-groups');
    const wrap = table ? (table.closest('.timeline-table-wrap') || table) : null;
    return {
      tableDisplay: wrap ? getComputedStyle(wrap).display : 'absent',
      naRows: document.querySelectorAll('#timeline-groups tr.na-row').length,
      naCards: Array.from(document.querySelectorAll('.timeline-mobile-card')).filter(c => c.querySelector('.tm-subj-na')).map(c => ({
        time: (c.querySelector('.timeline-mobile-time')?.textContent || '').trim(),
        word: (c.querySelector('.tm-subj-na')?.textContent || '').trim()
      })),
      mobileCards: document.querySelectorAll('.timeline-mobile-card').length
    };
  })()`);
  if (!(state.mobileCards > 0)) await printRenderDiagnostics('5b-no-mobile-cards');
  assert.ok(state.mobileCards > 0, 'mobile hour cards rendered');
  assert.equal(state.tableDisplay, 'none', '≤768px the hourly table wrap is display:none — the collapsed na-row is not part of the mobile layout');
  assert.ok(state.naCards.length > 0, 'na hours render as per-hour mobile cards — hourly data is never hidden on mobile');
  for (const c of state.naCards) {
    assert.match(c.time, /^\d{2}:\d{2}/, 'mobile na card carries its hour');
    assert.ok(c.word.includes('非建議時段'), 'mobile na card keeps the neutral 🕒 word');
  }
  // real hit: a mobile na card is a real hit target (CL-UI-102: scroll the
  // card into the modal's scroll container, settle, re-measure, hit-test;
  // probe several cards in OPEN day-groups so a card parked under the sticky
  // summary/close bar never greenwashes the miss)
  const hit = await evaljs(`new Promise((resolve) => {
    (async () => {
      // CL-CI-41 (D5): whether a day-group starts open depends on the render, so
      // the open-group filter could leave an EMPTY candidate list (probed: 0) and
      // fail an otherwise-correct modal. Open the first group that holds an na card
      // before filtering — the assertion still targets the na CARD's hit area.
      const allNa = Array.from(document.querySelectorAll('.timeline-mobile-card'))
        .filter(c => c.querySelector('.tm-subj-na'));
      const anyOpen = allNa.some(c => { const d = c.closest('details'); return !d || d.open; });
      if (!anyOpen && allNa.length) {
        const d = allNa[0].closest('details');
        if (d) { d.open = true; await new Promise(r => setTimeout(r, 250)); }
      }
      const cards = allNa.filter(c => { const d = c.closest('details'); return !d || d.open; });
      const results = [];
      for (const card of cards.slice(0, 8)) {
        card.scrollIntoView({block: 'center'});
        await new Promise(r => setTimeout(r, 150));
        const r = card.getBoundingClientRect();
        const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
        const inside = !!(el && (card.contains(el) || el === card));
        results.push({inside, hit: el ? el.tagName + '.' + String(el.className).slice(0, 40) : null});
        if (inside) { resolve({inside: true, probed: results.length}); return; }
      }
      resolve({inside: false, results, probed: results.length});
    })();
  })`);
  assert.ok(hit.inside, `mobile na card is a real hit target, got ${JSON.stringify(hit)}`);
});

test('CL-UI-118b (6): browser teardown', async () => { await teardownBrowser(); });


// CL-CI-40: release the browser, the CDP socket and the static server even when a
// test aborts or fails. Without a file-level hook the old "teardown" TEST only ran
// if every earlier test completed, so one hang left a Chrome process behind and the
// runner eventually reported the remaining cases as `cancelled` (OOM).
test.after(async () => {
  try { await teardownBrowser(); } catch (_) { /* already gone */ }
});
