// CL-E2E-131: semantic sweep gate — what a Taiwan user actually SEES at a
// given hour of the day, not what the source strings say.
//
// Why this exists: the suite has 1,100+ assertions that all check implementation
// shape (strings, JSON structure). It still shipped 「15:00 日出」 and a modal
// that listed 「昨天」 twice to a real phone. This gate replays a user who opens
// the page at 10:00 (DAY) and again at 23:30 (NIGHT) Asia/Taipei and asserts on
// the RENDERED DOM:
//   (1) DAY  — the forecast modal's daily list: no 「昨天」, every date label
//              once, exactly 7 entries, ascending, first = today, aligned with
//              the page's own date tabs.
//   (2) DAY+NIGHT — no physically impossible sunrise/sunset window (a 日出 start
//              must be 04:30–08:30, a 日落 start 16:00–19:30).
//   (3) NIGHT — no card may print 「✓ 推薦」 together with 「本日無符合題材」.
//   (4) NIGHT — a card whose day peaked at 推薦 and has no window left says
//              「今日可拍時段已結束」 (skip honestly when the data has no such card).
//   (5) MAP  — /weather-map.html?region=tw opens on mainland Taiwan at zoom ≥ 7.
//   (6) BOTH — no engineering tokens ('chip', 'undefined', 'NaN',
//              '(未調任何參數)', 'null') in the visible text.
//
// Harness: static file server at the repo root + headless Chrome + raw CDP over
// WebSocket (cl-app-06 / cl-ui-47 precedent — the suite is CDP-based, no
// Playwright). Time control is a clock shim injected with
// Page.addScriptToEvaluateOnNewDocument BEFORE any page script runs.
//
// Run:
//   node --test --test-timeout=180000 apps/web-v2/tests/cl-e2e-131-semantic-sweep.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync, readdirSync, existsSync, mkdtempSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

// ---------------------------------------------------------------- scenarios
// The two instants the owner reported: 10:00 (a user planning the morning) and
// 23:30 (after nightfall, when the day's windows are gone).
// CL-CI-43: the anchor day is the COMMITTED bundle's own first day, not a
// hard-coded date. A literal 2026-11-26 rots the moment the six-hourly refresh
// moves the window: the sweep would then shim the clock into a day the bundle
// no longer covers and fail on an empty daily list. Read the bundle, pin the
// clock to its first day, and the gate stays valid across every refresh.
const BUNDLE = JSON.parse(readFileSync(join(WEB, 'apps/web-v2/evaluations-latest.json'), 'utf8'));
const BUNDLE_DAYS = (() => {
  const set = new Set();
  for (const place of BUNDLE.places || []) {
    for (const opp of place.opportunities || []) {
      for (const day of opp.days || []) if (day && day.local_date) set.add(day.local_date);
    }
  }
  return [...set].sort();
})();
// The anchor must be a day the TAIWAN user calls today AND that BOTH halves of
// the render pipeline actually carry:
//   · the V2 evaluation bundle (day-qualified verdicts), and
//   · the weather snapshot the card list paints from (tw_weather.json `daily`
//     rows, one 7-day window per spot).
// Those two artifacts refresh on independent schedules. The bundle's generated_at
// Taipei date can already be YESTERDAY for the card list (observed: bundle
// generated_at 2026-11-26, weather snapshot's first daily row 2026-11-27).
// Freezing the clock on that stale day makes `currentDayForSpot` miss every
// spot's `daily` rows, `filterAndRender` renders the empty state, and the sweep
// fails on "waitFor timed out: index cards" — a harness artifact, not a page
// defect (the same page paints 161 cards against a live clock).
const WEATHER = JSON.parse(readFileSync(join(WEB, 'tw_weather.json'), 'utf8'));
const WEATHER_DAYS = (() => {
  const set = new Set();
  for (const spot of WEATHER.spots || []) {
    for (const day of spot.daily || []) if (day && day.date) set.add(day.date);
  }
  return [...set].sort();
})();
const ANCHOR_DAY = (() => {
  const bundleDays = new Set(BUNDLE_DAYS);
  const weatherDays = new Set(WEATHER_DAYS);
  const dayAfter = (d, n) => new Date(Date.parse(d + 'T00:00:00Z') + n * 86400000).toISOString().slice(0, 10);
  // A candidate must have the FULL 7-day chain in the weather snapshot (the
  // modal's daily list and the page's day tabs are 7 days wide) and be present
  // in the bundle (the verdicts of cases 1/6 read it).
  const candidates = WEATHER_DAYS.filter(d => bundleDays.has(d)
    && Array.from({ length: 7 }, (_, i) => weatherDays.has(dayAfter(d, i))).every(Boolean));
  if (!candidates.length) return null;
  let taipei = null;
  const at = Date.parse(BUNDLE.generated_at || '');
  if (Number.isFinite(at)) {
    taipei = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(at));
  }
  return (taipei && candidates.find(d => d >= taipei)) || candidates[0];
})();
if (!ANCHOR_DAY) throw new Error('no day is covered by both the evaluation bundle and the weather snapshot — cannot anchor the sweep');
// Does the served HOURLY shard (weather_details/, gitignored) actually reach the
// anchor day? The modal's day accordion groups the shard's rows from the
// place-local today, so a shard whose newest row is 11/15 while the anchor is
// 11/27 legitimately renders zero groups — a data-freshness fact, not a UI
// defect. The same probe decides whether an empty accordion is a REAL regression
// (the shard does cover the anchor) or an environment limit (it does not).
const SHARD_REACHES_ANCHOR = (() => {
  const dir = join(WEB, 'weather_details', 'tw');
  if (!existsSync(dir)) return false;
  try {
    for (const f of readdirSync(dir)) {
      if (!f.endsWith('.json')) continue;
      try {
        const payload = JSON.parse(readFileSync(join(dir, f), 'utf8'));
        for (const r of (payload.spot && payload.spot.hourly_forecast) || []) {
          if (r && String(r.local_date || '') >= ANCHOR_DAY) return true;
        }
      } catch { /* a half-written shard is not evidence either way */ }
    }
  } catch { return false; }
  return false;
})();
const [ANCHOR_Y, ANCHOR_M, ANCHOR_D] = ANCHOR_DAY.split('-').map(Number);
const DAY_FIXED = Date.UTC(ANCHOR_Y, ANCHOR_M - 1, ANCHOR_D, 2, 0, 0);   // 10:00 Asia/Taipei
const NIGHT_FIXED = Date.UTC(ANCHOR_Y, ANCHOR_M - 1, ANCHOR_D, 15, 30, 0); // 23:30 Asia/Taipei
const SPOT_TZ = 'Asia/Taipei';        // region=tw → every official spot's tz
const MACHINE_OFFSET_MIN = new Date().getTimezoneOffset(); // -480 on UTC+8
// The shim proof: the page's own `new Date().getHours()` must equal the hour of
// the FIXED instant in the MACHINE's timezone (the page renders wall-clock time
// with the machine's zone). On this runner that is literally 10 / 23; on a
// runner that is not UTC+8 the same instant yields a different literal hour, so
// the assertion is made against the instant, never a hard-coded number.
const DAY_HOUR = new Date(DAY_FIXED).getHours();
const NIGHT_HOUR = new Date(NIGHT_FIXED).getHours();

// --------------------------------------------------------------- clock shim
// Replaces window.Date with a subclass: no-arg construction and .now() return
// the FIXED epoch; Date.parse / Date.UTC / Date.prototype stay real, so Intl
// still formats normally and string parsing keeps working.
const clockShim = (fixed) => `(() => {
  const RealDate = window.Date;
  const FIXED = ${fixed};
  class ShimDate extends RealDate {
    constructor(...args) {
      if (args.length === 0) super(FIXED);
      else super(...args);
    }
    static now() { return FIXED; }
  }
  window.Date = ShimDate;
  window.__clClockShim = { fixed: FIXED, real: RealDate };
})();`;

// Network monitor: the list paints from the legacy snapshot first and re-renders
// once the V2 evaluation bundle / subject-cards artifact resolve. "Settled" is
// therefore observed as NETWORK IDLE (no fetch in flight for a couple of
// seconds), not as a guess about copy.
const netMonitor = `(() => {
  const of = window.fetch;
  const st = { inflight: 0, total: 0, lastDoneAt: performance.now(), failed: [] };
  window.__clNet = st;
  window.fetch = function (...a) {
    st.inflight++; st.total++;
    const url = String(a[0]);
    const p = of.apply(this, a);
    const note = (why) => { st.failed.push(url + ' → ' + why); if (st.failed.length > 12) st.failed.shift(); };
    try {
      p.then((r) => { st.inflight--; st.lastDoneAt = performance.now(); if (r && r.ok === false) note(r.status); },
             (e) => { st.inflight--; st.lastDoneAt = performance.now(); note((e && e.message) || 'network error'); });
    } catch (e) { st.inflight--; }
    return p;
  };
})();`;

// ------------------------------------------------------------------ harness
let server, baseURL, chrome, ws, send, evaljs, ready;
// Per-CDP-call reply deadline (see send()): generous enough that a page whose
// own in-page poll times out still reports ITS error, tight enough that a
// wedged main thread fails the test with a real message instead of a 300s kill.
const CDP_TIMEOUT_MS = Number(process.env.CL131_CDP_TIMEOUT_MS || 90000);
const pageErrors = [];
let loadEvents = 0; // Page.loadEventFired counter — an evaluate can land on the STALE document mid-navigation
let scriptIds = [];
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

// CL-E2E-131 (5): headless Chrome on a Linux runner has no GPU. MapLibre creates
// a WebGL context during init; without SwiftShader the context creation fails,
// the map never initialises, and `#basemap-status` stays "loading" forever — the
// exact 90s stall this gate used to report. The spawn args below enable the
// software rasteriser (the same flags cl-ui-113 uses), so the style/tile network
// is no longer the suspect.

const MIME = {
  '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript',
  '.css': 'text/css', '.json': 'application/json', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.webp': 'image/webp',
  '.woff2': 'font/woff2', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
};

async function boot() {
  if (ready) return ready;
  ready = (async () => {
    server = createServer((req, res) => {
      res.on('error', () => { /* client aborted mid-write */ });
      const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
      const file = join(WEB, p === '/' ? 'index.html' : decodeURIComponent(p.slice(1)));
      try {
        const body = readFileSync(file);
        res.writeHead(200, {
          'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream',
          'content-length': body.length,
        });
        res.end(body);
      } catch { if (!res.headersSent) { res.writeHead(404); res.end('not found'); } }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    baseURL = `http://127.0.0.1:${server.address().port}/`;

    chrome = spawn(BROWSER, [
      '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--use-angle=swiftshader',
      '--no-sandbox', '--disable-dev-shm-usage',
      '--no-first-run', '--remote-debugging-port=0',
      '--window-size=1280,1000', '--hide-scrollbars',
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'cle2e131-')), 'about:blank',
    ], { stdio: ['ignore', 'ignore', 'pipe'] });

    const wsUrl = await new Promise((resolve, reject) => {
      let buf = '';
      const timer = setTimeout(() => reject(new Error('no devtools endpoint (chrome did not report one in 30s)')), 30000);
      chrome.stderr.on('data', d => {
        buf += d;
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearTimeout(timer); resolve(m[1]); }
      });
      chrome.on('error', e => { clearTimeout(timer); reject(new Error('spawn: ' + e.message)); });
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
    ws.onmessage = e => {
      const m = JSON.parse(e.data);
      if (m.method === 'Page.loadEventFired') loadEvents++;
      // CL-CI-43: keep the page's own exceptions. A blocked render (missing
      // asset, thrown init) used to surface only as "waitFor timed out: index
      // cards", which says nothing about WHY. Attach them to the failure.
      if (m.method === 'Runtime.exceptionThrown') {
        const d = m.params?.exceptionDetails || {};
        const text = d.exception?.description || d.text || 'page exception';
        pageErrors.push(String(text).split(String.fromCharCode(10))[0].slice(0, 400));
        if (pageErrors.length > 6) pageErrors.shift();
      }
      if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    };
    // CL-E2E-131: every CDP call carries its own reply deadline. Without one a
    // Runtime.evaluate whose promise never settles (a busy main thread while the
    // basemap/tiles churn) leaves the await hanging until the runner kills the
    // whole test at 300s, which tells nobody what actually stalled.
    send = (method, params = {}, { timeoutMs = CDP_TIMEOUT_MS } = {}) => new Promise((resolve, reject) => {
      const i = nextId();
      const timer = setTimeout(() => {
        if (pending.delete(i)) reject(new Error(`${method}: no CDP reply within ${timeoutMs}ms (page main thread blocked?)`));
      }, timeoutMs);
      pending.set(i, m => {
        clearTimeout(timer);
        if (m.error) reject(new Error(`${method}: ${m.error.message}`));
        else resolve(m.result);
      });
      try { ws.send(JSON.stringify({ id: i, method, params })); }
      catch (e) { clearTimeout(timer); pending.delete(i); reject(e); }
    });
    evaljs = async (expr, opts = {}) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }, opts);
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text || 'page error');
      return r.result?.value;
    };

    await send('Page.enable');
    await send('Runtime.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 1000, deviceScaleFactor: 1, mobile: false });
  })().catch(e => { ready = null; throw e; });
  return ready;
}

async function teardown() {
  await Promise.all([
    (async () => { try { ws?.close(); } catch { /* already closed */ } })(),
    (async () => { try { chrome?.kill(); } catch { /* already dead */ } })(),
    (async () => { await new Promise(r => { try { server?.close(r); } catch { r(); } }); })(),
  ]);
}
test.after(teardown);

// A fresh document always gets exactly the current scenario's shim: the
// registration is re-sent before EVERY navigation (the init-script
// registration does not survive a navigation on this harness — CL-CI-38).
async function installClock(fixed) {
  for (const id of scriptIds) {
    try { await send('Page.removeScriptToEvaluateOnNewDocument', { identifier: id }); } catch { /* gone with the old session */ }
  }
  scriptIds = [];
  const r = await send('Page.addScriptToEvaluateOnNewDocument', { source: clockShim(fixed) });
  if (r?.identifier) scriptIds.push(r.identifier);
  const n = await send('Page.addScriptToEvaluateOnNewDocument', { source: netMonitor });
  if (n?.identifier) scriptIds.push(n.identifier);
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// CL-E2E-131: bounded, HARNESS-side polling. An in-page `awaitPromise` poll is a
// single CDP request: if the page's main thread stalls (tile/style churn on a
// cold CI runner) the request never answers and nothing inside the page can
// recover — the whole test dies at the runner timeout with no diagnosis. This
// helper keeps the budget in Node: every probe is a short-lived evaluate with
// its own deadline, a failed/slow probe just counts as "not ready yet", and the
// dead-line surfaces an explicit error naming what never settled.
async function pollUntil(expr, { timeoutMs = 90000, intervalMs = 500, label = expr, probe = v => !!v, callTimeoutMs = 15000 } = {}) {
  const t0 = Date.now();
  let last, lastErr;
  let probes = 0, failures = 0;
  while (Date.now() - t0 < timeoutMs) {
    probes++;
    try {
      const v = await evaljs(expr, { timeoutMs: Math.max(2000, Math.min(callTimeoutMs, timeoutMs - (Date.now() - t0))) });
      last = v;
      if (probe(v)) return { value: v, probes, failures, elapsedMs: Date.now() - t0 };
    } catch (e) {
      failures++;
      lastErr = e;
      if (/no CDP reply/.test(e.message) || /Execution context was destroyed|Cannot find context/.test(e.message)) {
        // the document is mid-swap/hung — keep polling until the deadline
      }
    }
    await sleep(intervalMs);
  }
  throw new Error(`${label}: not settled within ${timeoutMs}ms `
    + `(${probes} probes, ${failures} failed; last=${JSON.stringify(last) ?? 'n/a'}`
    + (lastErr ? `; last error: ${lastErr.message}` : '')
    + (pageErrors.length ? ` | page errors: ${pageErrors.join(' ;; ')}` : '') + ')');
}

async function navigate(path, { waitFor, timeout = 45000, label = path } = {}) {
  const before = loadEvents;
  await send('Page.navigate', { url: baseURL + path });
  const t0 = Date.now();
  while (loadEvents <= before) {
    if (Date.now() - t0 > 30000) throw new Error(`navigation never fired load: ${label}`);
    await sleep(100);
  }
  if (waitFor) {
    // pageErrors is a NODE-side array: it is read here and interpolated as a
    // literal. Referencing it inside the in-page expression made the timeout
    // branch throw `ReferenceError: pageErrors is not defined`, so a page that
    // never became ready hung the awaited evaluate until the CDP deadline
    // instead of reporting "waitFor timed out".
    const pageErrNote = pageErrors.length ? ` | page errors: ${pageErrors.join(' ;; ')}` : '';
    await evaljs(`new Promise((resolve, reject) => {
      // performance.now() — NOT Date.now(): the clock shim freezes Date.now, so a
      // Date-based in-page timeout would never fire and the promise would hang.
      const t0 = performance.now();
      const iv = setInterval(() => {
        let ok = false;
        try { ok = !!(${waitFor}); } catch (e) { ok = false; }
        if (ok) { clearInterval(iv); resolve(true); }
        else if (performance.now() - t0 > ${timeout}) {
          clearInterval(iv);
          reject(new Error('waitFor timed out: ' + ${JSON.stringify(label)} + ' (' + ${JSON.stringify(waitFor)} + ')'
            + ${JSON.stringify(pageErrNote)}));
        }
      }, 200);
    })`);
  }
}

// Prove the clock shim is live in the page before any assertion leans on it.
async function assertClock(fixed, expectedHour, scenario) {
  const probe = await evaljs(`(() => {
    const d = new Date();
    return {
      isDate: d instanceof Date,
      hours: d.getHours(),
      now: Date.now(),
      intl: (() => { try { return new Intl.DateTimeFormat('en-GB', { timeZone: '${SPOT_TZ}', hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date()); } catch (e) { return 'ERR'; } })(),
      parse: Date.parse('2026-11-26T00:00:00Z'),
    };
  })()`);
  assert.equal(probe.isDate, true, `${scenario}: the shimmed Date still produces real Date instances`);
  assert.equal(probe.now, fixed, `${scenario}: Date.now() returns the fixed epoch (${fixed})`);
  assert.equal(probe.hours, expectedHour,
    `${scenario}: new Date().getHours() is the fixed instant's hour in the machine zone (${expectedHour}); ` +
    `machine offset ${MACHINE_OFFSET_MIN} min`);
  // Intl must still format normally — the shim only replaces construction/now.
  assert.match(String(probe.intl), /^\d{2}:\d{2}$/, `${scenario}: Intl.DateTimeFormat still formats the fixed instant`);
  assert.equal(probe.parse, Date.parse('2026-11-26T00:00:00Z'), `${scenario}: Date.parse stays the real implementation`);
  return probe;
}

// ------------------------------------------------------------------ helpers
async function openFirstCardModal(index = 0, { requireRows = 7 } = {}) {
  const opened = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const card = cards[${index}];
    if (!card) return { ok: false, cards: cards.length };
    card.click();
    return { ok: true, name: (card.querySelector('.spot-name') || {}).textContent || '' };
  })()`);
  assert.equal(opened.ok, true, `a card exists at index ${index} to open`);
  // The modal paints 「正在載入天氣預報…」 first; the daily list and the timeline
  // arrive with the detail payload.
  try {
    await evaljs(`new Promise((resolve, reject) => {
      const t0 = performance.now();
      const iv = setInterval(() => {
        const ov = document.getElementById('modal-overlay');
        const rows = document.querySelectorAll('#modal-summary .modal-day-row').length;
        if (ov && getComputedStyle(ov).display !== 'none' && rows >= ${requireRows}) { clearInterval(iv); resolve(true); }
        else if (performance.now() - t0 > 45000) {
          clearInterval(iv);
          reject(new Error('modal daily summary never rendered (' + rows + ' rows)'));
        }
      }, 200);
    })`);
  } catch (e) {
    // The detail payload is a per-place shard (./weather_details/<region>/<spot>.json)
    // that is NOT committed — CI hydrates it from R2. A missing tree used to fail
    // here as a bare "0 rows" after 45s with nothing pointing at the cause.
    const failed = await evaljs(`((window.__clNet && window.__clNet.failed) || [])
      .filter((u) => /weather_details|evaluations|\\.json/.test(u)).slice(-4)`).catch(() => null);
    throw new Error(e.message + (failed && failed.length ? ` | failed fetches: ${failed.join(', ')}` : ''));
  }
  await sleep(600); // let the timeline/quicks view settle
  return opened.name;
}

async function closeModal() {
  await evaljs(`(() => { const b = document.querySelector('#modal-overlay .close-btn'); if (b) b.click(); return true; })()`);
  await sleep(300);
}

// Read the modal's daily list + the page's own date-tab chains.
async function readDayList() {
  return evaljs(`(() => {
    const ov = document.getElementById('modal-overlay');
    const rows = [...document.querySelectorAll('#modal-summary .modal-overview .modal-day-row')].map(r => ({
      label: ((r.querySelector('.modal-day-label') || {}).textContent || '').trim(),
      text: (r.innerText || '').replace(/\\s+/g, ' ').trim(),
    }));
    const tabs = [...document.querySelectorAll('#modal-summary .modal-day-btn')].map(b => (b.textContent || '').trim());
    // the page's own date tabs (the day picker list) — same 7-day chain
    const pageTabs = [...document.querySelectorAll('#day-picker-panel .day-option')].map(b => ({
      key: b.getAttribute('data-day'),
      label: ((b.querySelector('.day-option-label') || {}).textContent || '').trim(),
    }));
    // expected chain derived from the spot's OWN local today (fixed instant + real Intl)
    const todayKey = new Intl.DateTimeFormat('en-CA', { timeZone: '${SPOT_TZ}', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
    const base = Date.parse(todayKey + 'T12:00:00Z');
    const chain = Array.from({ length: 7 }, (_, i) => {
      if (i === 0) return '今天';
      if (i === 1) return '明天';
      if (i === 2) return '後天';
      const iso = new Date(base + i * 86400000).toISOString().slice(0, 10);
      return iso.slice(5, 7).replace(/^0/, '') + '/' + iso.slice(8, 10);
    });
    const dates = chain.map((_, i) => new Date(base + i * 86400000).toISOString().slice(0, 10));
    return {
      rows, tabs, pageTabs, chain, dates, todayKey,
      modalText: ov ? ov.textContent : '',
      modalInnerText: ov ? ov.innerText : '',
    };
  })()`);
}

// Sunrise / sunset window labels as the USER sees them. Two surfaces are read:
//   · the forecast modal's own text, and
//   · the per-subject rows of the card that owns the open modal — the same
//     anatomy (「日出 ： 05:40–06:00」) where the owner's 「15:00 日出」 was seen.
// Both are rendered text; nothing is read from source.
async function readAstroWindows(index = 0) {
  return evaljs(`(() => {
    const out = [];
    const push = (label, start, end, src) => {
      if (!label || !/^\\d{1,2}:\\d{2}$/.test(start || '') || !/^\\d{1,2}:\\d{2}$/.test(end || '')) return;
      out.push({ label, start, end, src });
    };
    const rx = /(日出|日落)[\\s:：]{0,6}(\\d{1,2}:\\d{2})\\s*[-–~]\\s*(\\d{1,2}:\\d{2})/g;
    const ov = document.getElementById('modal-overlay');
    if (ov) {
      let m;
      const txt = ov.textContent || '';
      while ((m = rx.exec(txt))) push(m[1], m[2], m[3], 'modal');
    }
    const card = [...document.querySelectorAll('#spots-container .card')][${index}];
    if (card) {
      [...card.querySelectorAll('.cl-subject-row')].forEach(r => {
        const name = ((r.querySelector('.cl-subject-name') || {}).textContent || '').trim();
        const win = ((r.querySelector('.cl-subject-window') || {}).textContent || '').trim();
        const lm = name.match(/(日出|日落)/);
        if (!lm) return;
        const wm = win.match(/(\\d{1,2}:\\d{2})\\s*[-–~]\\s*(\\d{1,2}:\\d{2})/);
        if (wm) push(lm[1], wm[1], wm[2], 'card');
        else if (win) out.push({ label: lm[1], start: '', end: '', raw: win, src: 'card' });
      });
    }
    return out;
  })()`);
}

const minutes = (hhmm) => {
  const m = /^(\d{1,2}):(\d{2})$/.exec(String(hhmm || ''));
  return m ? Number(m[1]) * 60 + Number(m[2]) : null;
};

// A 日出 window must start in the morning, a 日落 window in the evening. The
// bounds are deliberately generous (Taiwan summer/winter spread) so this flags
// only physically impossible labels (the shipped 「15:00 日出」), not style.
function assertAstroSane(windows, scenario) {
  for (const w of windows) {
    const start = minutes(w.start);
    if (start === null) continue;
    if (w.label === '日出') {
      assert.ok(start >= 4 * 60 + 30 && start <= 8 * 60 + 30,
        `${scenario}: 日出 window starts ${w.start} — outside the physically possible 04:30–08:30 (${w.src})`);
      const end = minutes(w.end);
      assert.ok(end !== null && end > start,
        `${scenario}: 日出 window ${w.start}–${w.end} must end after it starts (${w.src})`);
    } else {
      assert.ok(start >= 16 * 60 && start <= 19 * 60 + 30,
        `${scenario}: 日落 window starts ${w.start} — outside the physically possible 16:00–19:30 (${w.src})`);
      const end = minutes(w.end);
      assert.ok(end !== null && end > start,
        `${scenario}: 日落 window ${w.start}–${w.end} must end after it starts (${w.src})`);
    }
  }
}

const ENGINEERING_TOKENS = ['chip', 'undefined', 'NaN', '(未調任何參數)', 'null'];

async function readEngineeringTokens() {
  return evaljs(`(() => {
    const txt = document.body.innerText || '';
    return {
      hits: ${JSON.stringify(ENGINEERING_TOKENS)}.filter(t => txt.includes(t)),
      sample: ${JSON.stringify(ENGINEERING_TOKENS)}.map(t => {
        const i = txt.indexOf(t);
        return i < 0 ? null : (t + ' → ' + txt.slice(Math.max(0, i - 40), i + 40).replace(/\\s+/g, ' '));
      }).filter(Boolean),
    };
  })()`);
}

// The list first paints from the legacy snapshot, then re-renders once the V2
// evaluation bundle + subject-cards artifact are applied (their fetches resolve
// after load). Assert on the SETTLED list: poll until a card's summary text
// changes from the first paint, or already carries the data-driven line.
async function waitForCardData(failMessage) {
  await evaljs(`new Promise((resolve, reject) => {
    const t0 = performance.now();
    const QUITE_MS = 3000;
    const iv = setInterval(() => {
      const net = window.__clNet || { inflight: 0, total: 999, lastDoneAt: 0 };
      const quietFor = performance.now() - net.lastDoneAt;
      const ready = net.total >= 5 && net.inflight === 0 && quietFor >= QUITE_MS;
      if (ready) { clearInterval(iv); resolve(true); }
      else if (performance.now() - t0 > 45000) {
        clearInterval(iv);
        reject(new Error(${JSON.stringify(failMessage)} + ' (net: ' + JSON.stringify({ inflight: net.inflight, total: net.total }) + ')'));
      }
    }, 250);
  })`);
  // one extra breath: the re-render that publishes the evaluation layer runs on
  // the frame after the last fetch resolves.
  await sleep(3500);
}

// =========================================================== (1) DAY 10:00
test('CL-E2E-131 (1) DAY 10:00 — the modal daily list is 7 aligned days, no 昨天, every label once', async () => {
  await boot();
  await installClock(DAY_FIXED);
  await navigate('index.html', { waitFor: `document.querySelectorAll('#spots-container .card').length > 0`, label: 'index cards' });

  const clock = await assertClock(DAY_FIXED, DAY_HOUR, 'DAY');
  if (MACHINE_OFFSET_MIN === -480) assert.equal(clock.hours, 10, 'DAY on a UTC+8 runner is literally 10:00');

  await waitForCardData('the DAY card list never received its evaluation data');
  await openFirstCardModal(0);
  const day = await readDayList();

  // (a) the owner's 「昨天」 must never be in the modal
  assert.ok(!day.modalText.includes('昨天'), 'the modal never says 昨天 (a past day must not be listed as today)');
  assert.ok(!day.modalInnerText.includes('昨天'), 'the modal never RENDERS 昨天');

  // (c) exactly 7 day entries
  assert.equal(day.rows.length, 7, `the daily summary lists exactly 7 days (got ${day.rows.length}: ${day.rows.map(r => r.label).join(',')})`);

  // (b) every date label appears exactly once
  const labels = day.rows.map(r => r.label);
  assert.equal(new Set(labels).size, labels.length,
    `every date label appears exactly once (got ${labels.join(',')})`);

  // (d) ascending by date — parse the label back to a calendar date
  const parsed = day.rows.map((r, i) => {
    const idx = day.chain.indexOf(r.label);
    return idx >= 0 ? idx : NaN;
  });
  assert.deepEqual(parsed, [0, 1, 2, 3, 4, 5, 6],
    `rows ascend by date, today first, in the page's own label chain (rows: ${labels.join(',')} / chain: ${day.chain.join(',')})`);
  for (let i = 1; i < day.dates.length; i++) {
    assert.ok(day.dates[i] > day.dates[i - 1], `date ${i} (${day.dates[i]}) is after ${i - 1} (${day.dates[i - 1]})`);
  }

  // (e) the first entry is today's local date — cross-checked two ways:
  //     the chain derived from Intl(today, Asia/Taipei) and the page's own tabs.
  assert.equal(day.rows[0].label, '今天', `the first row is today (today is ${day.todayKey} in ${SPOT_TZ})`);
  assert.equal(day.chain[0], '今天');
  assert.deepEqual(day.tabs, day.chain, `the modal date tabs carry the same chain (got ${day.tabs.join(',')})`);
  assert.deepEqual(day.pageTabs.map(t => t.label).slice(0, 7), day.chain,
    `the page's own date tabs agree with the modal's chain (page: ${day.pageTabs.map(t => t.label).join(',')})`);
  assert.deepEqual(day.pageTabs.map(t => t.key), ['today', 'tomorrow', 'after_tomorrow', 'day3', 'day4', 'day5', 'day6'],
    'the page date tabs are the 7 day keys');

  // (6) engineering tokens on the index page
  const tokens = await readEngineeringTokens();
  assert.deepEqual(tokens.hits, [], `no engineering tokens on screen (${JSON.stringify(tokens.sample)})`);
});

// ================================================= (2) astro windows, DAY+NIGHT
test('CL-E2E-131 (2) DAY+NIGHT — no physically impossible sunrise/sunset window', async () => {
  await boot();
  let checked = 0;
  const seen = [];

  for (const [scenario, fixed, hour] of [['DAY', DAY_FIXED, DAY_HOUR], ['NIGHT', NIGHT_FIXED, NIGHT_HOUR]]) {
    await installClock(fixed);
    await navigate('index.html', { waitFor: `document.querySelectorAll('#spots-container .card').length > 0`, label: `index cards (${scenario})` });
    await assertClock(fixed, hour, scenario);
    await waitForCardData(`the ${scenario} card list never received its evaluation data`);

    // The default tier tab (✓推薦) can hide every card that carries an astro
    // subject on a given day — the gate would then report "blind" while the
    // impossible label is one tab away. Widen to the 🌐 全部 tab first: the
    // rule stays strict (every 日出/日落 label found must be physically sane),
    // but the sweep looks at the full list, not only the recommended slice.
    await evaljs(`(() => {
      const b = document.querySelector('#tier-tabs button[data-tier="all"]');
      if (b && b.getAttribute('aria-selected') !== 'true') b.click();
      return true;
    })()`);
    await sleep(800);

    // Pick the spot the sweep will inspect: the first rendered card that carries
    // an astro window label. A spot with no 日出/日落 subject has no label at all
    // — skipping it is honest (the sweep-wide rule below still fails if NOTHING
    // was checked), and NOT inventing a label for it would be worse.
    const pick = await evaljs(`(() => {
      const cards = [...document.querySelectorAll('#spots-container .card')];
      for (let i = 0; i < cards.length; i++) {
        const names = [...cards[i].querySelectorAll('.cl-subject-row .cl-subject-name')].map(e => (e.textContent || ''));
        if (names.some(n => /日出|日落/.test(n))) return { i, names };
      }
      return { i: -1, names: [] };
    })()`);
    if (pick.i < 0) {
      seen.push(`${scenario}: no rendered card carries a 日出/日落 window label — skipped`);
      continue;
    }

    // Read the card's own subject-row labels, then open that spot's forecast
    // modal and read the labels again (the modal text is part of the sweep).
    await openFirstCardModal(pick.i, { requireRows: 1 });
    const raw = await readAstroWindows(pick.i);
    await closeModal();

    const windows = raw.filter(w => w.start && w.end);
    const unparsable = raw.filter(w => !w.start || !w.end);
    assert.deepEqual(unparsable.map(w => `${w.label}: ${w.raw || w.start + '–' + w.end}`), [],
      `${scenario}: every 日出/日落 label carries a readable HH:MM–HH:MM window (a label with no window cannot be checked and must not be silently dropped)`);
    if (!windows.length) {
      seen.push(`${scenario}: the selected spot (card ${pick.i}) carries no readable astro window — skipped`);
      continue;
    }
    assertAstroSane(windows, scenario);
    checked += windows.length;
    seen.push(`${scenario}: card ${pick.i} ${windows.map(w => `${w.label} ${w.start}–${w.end} (${w.src})`).join(', ')}`);
  }

  assert.ok(checked > 0,
    `sweep saw no astro window — the gate is blind, not green. Checked: ${JSON.stringify(seen)}`);
  console.log('# CL-E2E-131 astro windows checked:', checked, '·', seen.join(' | '));
});

// ==================================== (3) NIGHT 23:30 — contradictory card copy
test('CL-E2E-131 (3) NIGHT 23:30 — no 「✓ 推薦」 badge next to 「本日無符合題材」', async () => {
  await boot();
  await installClock(NIGHT_FIXED);
  await navigate('index.html', { waitFor: `document.querySelectorAll('#spots-container .card').length > 0`, label: 'index cards (NIGHT)' });
  await assertClock(NIGHT_FIXED, NIGHT_HOUR, 'NIGHT');

  // The list a user lands on at 23:30 — settled, not mid-render. (The tier tab
  // stays on its default ✓推薦 view: that is the surface the owner reported.)
  await waitForCardData('the NIGHT card list never received its evaluation data');

  const cards = await evaljs(`(() => {
    const nowMin = new Date().getHours() * 60 + new Date().getMinutes();
    const winEndMinutes = (txt) => {
      const r = /(\d{1,2}):(\d{2})\s*[-–~]\s*(\d{1,2}):(\d{2})/.exec(txt);
      if (r) return Number(r[3]) * 60 + Number(r[4]);
      const s = /(\d{1,2}):(\d{2})/.exec(txt);
      return s ? Number(s[1]) * 60 + Number(s[2]) : null;
    };
    return [...document.querySelectorAll('#spots-container .card')].map((c, i) => {
      // textContent, not innerText: the card list is content-visibility:auto, so
      // off-screen cards report an EMPTY innerText even though they are rendered
      // into the DOM the user scrolls through. textContent is the same rendered
      // markup without that paint-containment blind spot.
      const windows = [...c.querySelectorAll('.cl-subject-row .cl-subject-window')]
        .map(e => (e.textContent || '').trim()).filter(Boolean);
      const ends = windows.map(winEndMinutes).filter(v => v !== null);
      return {
        i,
        nowMin,
        name: ((c.querySelector('.spot-name') || {}).textContent || '').trim(),
        tier: ((c.querySelector('.card-header-actions .tier') || {}).textContent || '').trim(),
        summary: ((c.querySelector('.shooting-summary') || {}).textContent || '').replace(/\s+/g, ' ').trim(),
        text: (c.textContent || '').replace(/\s+/g, ' '),
        windows,
        windowLeft: ends.some(end => end >= nowMin),
      };
    });
  })()`);
  if (process.env.CL131_DBG) {
    console.log('DBG-NIGHT', JSON.stringify(await evaljs(`(() => ({
      hour: new Date().getHours() + ':' + new Date().getMinutes(),
      fixed: window.__clClockShim && window.__clClockShim.fixed,
      net: window.__clNet,
      n: document.querySelectorAll('#spots-container .card').length,
      dayOver: document.querySelectorAll('#spots-container .card').length && [...document.querySelectorAll('#spots-container .card')].filter(c => (c.textContent||'').includes('今日可拍時段已結束')).length,
      none: [...document.querySelectorAll('#spots-container .card')].filter(c => (c.textContent||'').includes('本日無符合題材')).length,
      first3: [...document.querySelectorAll('#spots-container .card')].slice(0,3).map(c => ((c.querySelector('.shooting-summary')||{}).textContent||'').replace(/\s+/g,' ').slice(0,120)),
      trigger: (document.getElementById('day-picker-trigger')||{}).textContent,
    }))()`), null, 1));
  }
  assert.ok(cards.length >= 5, `the night list shows cards (got ${cards.length})`);

  // (3) never both halves of the self-contradiction on one card
  const contradictory = cards.filter(c => /✓\s*推薦/.test(c.tier) && c.text.includes('本日無符合題材'));
  assert.deepEqual(contradictory.map(c => c.name), [],
    `no card shows 「✓ 推薦」 together with 「本日無符合題材」 (${contradictory.map(c => c.name + ': ' + c.summary).join(' | ')})`);

  // the tokens rule on the night page too
  const tokens = await readEngineeringTokens();
  assert.deepEqual(tokens.hits, [], `no engineering tokens on screen at night (${JSON.stringify(tokens.sample)})`);
});

// ==================================== (4) NIGHT 23:30 — post-nightfall copy
test('CL-E2E-131 (4) NIGHT 23:30 — a 推薦 card with no window left says 「今日可拍時段已結束」', async (t) => {
  await boot();
  await installClock(NIGHT_FIXED);
  await navigate('index.html', { waitFor: `document.querySelectorAll('#spots-container .card').length > 0`, label: 'index cards (NIGHT, copy)' });
  await assertClock(NIGHT_FIXED, NIGHT_HOUR, 'NIGHT');
  await waitForCardData('the NIGHT card list never received its evaluation data');

  const cards = await evaljs(`(() => {
    const nowMin = new Date().getHours() * 60 + new Date().getMinutes();
    const winEndMinutes = (txt) => {
      const r = /(\d{1,2}):(\d{2})\s*[-–~]\s*(\d{1,2}):(\d{2})/.exec(txt);
      if (r) return Number(r[3]) * 60 + Number(r[4]);
      const s = /(\d{1,2}):(\d{2})/.exec(txt);
      return s ? Number(s[1]) * 60 + Number(s[2]) : null;
    };
    return [...document.querySelectorAll('#spots-container .card')].map((c, i) => {
      const windows = [...c.querySelectorAll('.cl-subject-row .cl-subject-window')]
        .map(e => (e.textContent || '').trim()).filter(Boolean);
      const ends = windows.map(winEndMinutes).filter(v => v !== null);
      return {
        i,
        name: ((c.querySelector('.spot-name') || {}).textContent || '').trim(),
        tier: ((c.querySelector('.card-header-actions .tier') || {}).textContent || '').trim(),
        summary: ((c.querySelector('.shooting-summary') || {}).textContent || '').replace(/\s+/g, ' ').trim(),
        windows,
        windowLeft: ends.some(end => end >= nowMin),
      };
    });
  })()`);

  // "No window left" is derived from the card's OWN rendered window labels: every
  // 日出/瀑布/… window on it ended before the fixed 23:30 local now.
  const peaked = cards.filter(c => /✓\s*推薦/.test(c.tier));
  const noWindowLeft = peaked.filter(c => c.windows.length > 0 && !c.windowLeft);
  if (!noWindowLeft.length) {
    const reason = `no card in the current data peaked at ✓推薦 with zero remaining window ` +
      `(${peaked.length} ✓推薦 cards, all still advertising a window) — copy check skipped, not forced`;
    console.log('# CL-E2E-131 (4) skipped:', reason);
    t.diagnostic(reason);
    return;
  }
  const missingCopy = noWindowLeft.filter(c => !c.summary.includes('今日可拍時段已結束'));
  assert.deepEqual(missingCopy.map(c => c.name + ' → ' + c.summary), [],
    'every card whose day peaked at 推薦 and has no window left says 「今日可拍時段已結束」');
});

// ================================================== (5) weather map camera
// CL-E2E-131: this case used exactly ONE in-page `awaitPromise` poll for the map
// instance and another for the camera. On a cold CI runner the basemap style /
// tile fetch can stall the page's main thread, and a single long-lived CDP
// request then never answers: nothing inside the page can time out a request the
// page never gets to run, so the case hung until the runner killed it at 300s
// with no message. The budget now lives in Node (MAP_BUDGET_MS), every wait is a
// bounded harness-side poll, and the semantic assertions are untouched.
const MAP_BUDGET_MS = Number(process.env.CL131_MAP_BUDGET_MS || 90000);

async function disposeMapPage() {
  try {
    await evaljs(`(() => {
      try {
        const m = window.__weatherGridMap;
        if (m) {
          try { if (m.stop) m.stop(); } catch (e) { /* not moving */ }
          try { m.remove(); } catch (e) { /* already torn down */ }
        }
        window.__weatherGridMap = null;
      } catch (e) { /* page is gone */ }
      return true;
    })()`, { timeoutMs: 5000 });
    return 'released';
  } catch (e) {
    return 'map page not reachable (' + e.message + ')';
  }
}

test('CL-E2E-131 (5) MAP — /weather-map.html?region=tw opens on mainland Taiwan at zoom ≥ 7', async () => {
  const t0 = Date.now();
  const budgetLeft = () => Math.max(3000, MAP_BUDGET_MS - (Date.now() - t0));
  try {
    await boot();
    await installClock(DAY_FIXED);
    // No in-page waitFor here: the map instance is created inside MapLibre's
    // 'load' handler, so the wait must survive a slow style/tile fetch — which
    // is precisely the wait that used to hang. Poll it from the harness.
    await navigate('weather-map.html?region=tw', { label: 'weather map' });
    const inst = await pollUntil(`(() => {
      const m = window.__weatherGridMap;
      const s = document.getElementById('basemap-status');
      return {hasMap: !!(m && typeof m.getZoom === 'function'), status: s ? String(s.className) : 'absent'};
    })()`, {
      timeoutMs: budgetLeft(),
      label: 'weather map never became interactive (MapLibre "load" never fired — basemap style/tiles stalled)',
      probe: v => !!(v && v.hasMap),
    });
    if (inst.failures) console.log(`# CL-E2E-131 (5): ${inst.failures}/${inst.probes} probes had no CDP reply (slow main thread), recovered`);

    // The region opening camera is applied on the basemap 'load' event
    // (applyRegionDefaultCamera), which can land after the map object exists —
    // so wait for the camera to SETTLE (status ready, not moving, two identical
    // readings), not merely for the instance. The assertions below still read a
    // fresh camera and fail if it is not on Taiwan.
    let settleKey = '';
    await pollUntil(`(() => {
      const m = window.__weatherGridMap;
      if (!m || typeof m.getZoom !== 'function') return null;
      const c = m.getCenter();
      const s = document.getElementById('basemap-status');
      return {
        zoom: Math.round(m.getZoom() * 1000) / 1000,
        lat: Math.round(c.lat * 10000) / 10000,
        lng: Math.round(c.lng * 10000) / 10000,
        moving: !!(m.isMoving && m.isMoving()),
        status: s ? String(s.className) : 'absent',
      };
    })()`, {
      timeoutMs: budgetLeft(),
      label: 'map camera never settled after load (basemap-status never reached "ready")',
      probe: (v) => {
        if (!v || v.moving || !/ready/.test(v.status)) { settleKey = ''; return false; }
        const key = v.zoom + '|' + v.lat + '|' + v.lng;
        if (key !== settleKey) { settleKey = key; return false; }
        return true;
      },
    });
    await sleep(800);
    const cam = await evaljs(`(() => {
      const m = window.__weatherGridMap;
      const c = m.getCenter();
      return { zoom: m.getZoom(), lat: c.lat, lng: c.lng };
    })()`);
    assert.ok(cam.zoom >= 7, `the map is zoomed into Taiwan, not the whole of East Asia (zoom=${cam.zoom})`);
    assert.ok(cam.lat >= 21.5 && cam.lat <= 25.5, `center latitude is mainland Taiwan (lat=${cam.lat})`);
    assert.ok(cam.lng >= 119.0 && cam.lng <= 122.5, `center longitude is mainland Taiwan (lng=${cam.lng})`);

    const tokens = await readEngineeringTokens();
    assert.deepEqual(tokens.hits, [], `no engineering tokens on screen on the map page (${JSON.stringify(tokens.sample)})`);

    // The map must have a live style with real basemap layers — a blank/absent
    // style would mean the instance exists but never rendered.
    const styleProof = await evaljs(`(() => {
      const m = window.__weatherGridMap;
      const s2 = (m && m.getStyle && m.getStyle()) || null;
      return { layers: (s2 && Array.isArray(s2.layers)) ? s2.layers.length : 0 };
    })()`);
    assert.ok(styleProof.layers > 0, `the map rendered a live basemap style (layers=${styleProof.layers})`);
    console.log(`# CL-E2E-131 (5): live basemap layers=${styleProof.layers}`);
  } finally {

    // always hand the map's tiles/timers back before the next case navigates
    console.log(`# CL-E2E-131 (5) map cleanup: ${await disposeMapPage()} (${Date.now() - t0}ms)`);
  }
});


// ============================================ (6) card ↔ modal weather贯通
// CL-CI-44: the card face and the forecast modal must tell ONE story per day.
// The owner's screenshot showed 「今天無建議符合題材 · ○ 可拍」 in the modal's
// top 7-day summary while the accordion below it said 「✓ 推薦 · ✓4 雲海」 for
// the same date. Both surfaces now read the committed subject-cards row, and
// both render the SAME day-weather block (WMO code + temperature range +
// visibility), so this gate asserts equality instead of eyeballing it.
test('CL-E2E-131 (6) DAY 10:00 — card and modal agree on every day: tier, WMO, temperature, visibility', async (t) => {
  await boot();
  await installClock(DAY_FIXED);
  await navigate('index.html', { waitFor: `document.querySelectorAll('#spots-container .card').length > 0`, label: 'index cards' });
  await waitForCardData('the DAY card list never received its evaluation data');

  // (a) the card face carries a complete weather chip — icon, temperature and
  //     visibility — and never leaks a placeholder.
  // CL-UI-115 §2: the card row reads NOW (the current hour) when the place's
  // hourly shard covers the place-local TODAY, and otherwise keeps the day
  // block. A stale shard — its newest row 11/15 while the clock reads 11/27, the
  // normal state of a committed weather_details copy — earns NO now row: the
  // card keeps the day chip instead of a fabricated present tense. So the gate
  // validates both shapes where they exist and outlaws the fake one.
  await pollUntil(`document.querySelectorAll('#spots-container .card .card-metric-chips .day-wx').length > 0`,
    { timeoutMs: 60000, label: 'no card rendered its weather chip within 60s' });
  // The page-side probe is a TEMPLATE string: every backslash the page must see
  // is written twice here (`\\s` → `\s`). Reviewer condition 4 — the normalizer
  // must be `/\s+/g` ON THE PAGE, not `/\\s+/g` (a literal backslash followed by
  // `s`), which would silently never collapse whitespace. Comparing the evaluated
  // VALUE below proves the escaping instead of eyeballing backslash counts.
  const CARD_WX_PROBE = `(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const withWx = cards.map(c => {
      const chip = c.querySelector('.card-metric-chips .day-wx');
      if (!chip) return null;
      return {
        text: chip.innerText.replace(/\\s+/g, ' ').trim(),
        html: chip.outerHTML,
        icons: [...chip.querySelectorAll('svg[data-cl-icon]')].map(s => s.getAttribute('data-cl-icon')),
        nowHour: chip.getAttribute('data-now-hour') || '',
        isNow: chip.classList.contains('now-wx'),
      };
    }).filter(Boolean);
    return { total: cards.length, withWx: withWx.length, nowCount: withWx.filter(c => c.isNow).length, sample: withWx.slice(0, 6) };
  })()`;
  // The string handed to the page must carry the real `\s` class …
  assert.ok(CARD_WX_PROBE.includes('replace(/\\s+/g'),
    'the page-side normalizer is /\\s+/g (a four-backslash form would arrive as /\\\\s+/g and never collapse)');
  // … and must not carry the escaped-by-accident form.
  assert.ok(!CARD_WX_PROBE.includes('replace(/' + String.fromCharCode(92, 92) + 's+/g'),
    'the probe does not double-escape the whitespace class');
  const cardWx = await evaljs(CARD_WX_PROBE);
  assert.ok(cardWx.withWx > 0, `at least one card face renders the weather chip (got ${cardWx.withWx}/${cardWx.total})`);

  // Strict visibility (was `/(≥\s*)?\d/` — any digit satisfied it): the eye
  // icon ELEMENT must be followed by the numeric km value in the SAME markup, and
  // the visible text must carry that number with its unit.
  const VIS_ICON_THEN_VALUE = /data-cl-icon="visibility"[\s\S]*?<\/svg>\s*(≥\s*)?\d+(\.\d+)?\s*km/;
  const nowChips = cardWx.sample.filter(c => c.isNow);
  const dayChips = cardWx.sample.filter(c => !c.isNow);
  assert.equal(nowChips.length + dayChips.length, cardWx.sample.length, 'every sampled chip is exactly one shape');

  // A now row is the §2 feature; without a gate a regression that paints ZERO of
  // them passes this sweep (every check below is a for-loop over an empty set).
  // What an empty set MEANS depends on the data: when the served hourly shard
  // genuinely covers the anchor day, at least one card must carry a now row;
  // when it does not, the day chip is the honest render and forcing a now row
  // would red a stale-shard local run for the wrong reason.
  if (SHARD_REACHES_ANCHOR) {
    assert.ok(cardWx.nowCount > 0,
      `at least one card face renders a NOW row at the fixed ${DAY_HOUR}:00 — the served hourly shard carries rows on/after ${ANCHOR_DAY}, so zero now-wx chips is a regression (${cardWx.withWx} weather chips, ${cardWx.nowCount} now)`);
  } else {
    console.log(`# CL-E2E-131 (6) now-row gate skipped: no served hourly shard row on/after ${ANCHOR_DAY} — every card keeping the day chip is the honest render, not a regression`);
  }

  for (const chip of nowChips) {
    const txt = chip.text;
    assert.ok(chip.nowHour, `now chip labels its hour via data-now-hour: ${txt}`);
    // Reviewer condition 3: a now row is only ever a row of the place-local
    // TODAY, so its label is a bare hour. A `11/15 02:00` suffix on a `now-wx`
    // chip is the fake-present-tense regression this gate exists to catch.
    assert.doesNotMatch(chip.nowHour, /\d{1,2}\/\d{1,2}/, `a now chip never labels another date: ${chip.nowHour}`);
    assert.match(chip.nowHour, /^\d{2}:\d{2}$/, `now chip labels a served hour of today: ${chip.nowHour}`);
    assert.match(txt, /-?\d+(\.\d+)?°C/, `now_hour chip carries the current-hour temperature: ${txt}`);
    assert.match(txt, /\d{2}:\d{2}/, `now_hour chip labels its hour: ${txt}`);
    assert.doesNotMatch(txt, /-?\d+–-?\d+°C/, `the now chip shows ONE hour, never a fabricated day range: ${txt}`);
    assert.match(chip.html, VIS_ICON_THEN_VALUE, `the visibility ICON is followed by its numeric km value: ${chip.html}`);
    assert.ok(!/undefined|NaN|null/.test(txt), `now chip has no placeholder value: ${txt}`);
  }

  for (const chip of dayChips) {
    const txt = chip.text;
    assert.equal(chip.nowHour, '', 'a day chip carries no now-hour label');
    assert.match(txt, /-?\d+–-?\d+°C/, `day chip carries the full-day temperature range: ${txt}`);
    assert.match(chip.html, VIS_ICON_THEN_VALUE, `the visibility ICON is followed by its numeric km value: ${chip.html}`);
    assert.ok(!/undefined|NaN|null/.test(txt), `day chip has no placeholder value: ${txt}`);
  }
  // Both shapes share the same glyph set: the WMO SVG and the eye icon.
  for (const chip of cardWx.sample) {
    assert.ok(chip.icons.filter(k => /^\d+$/.test(k)).length > 0, `card weather chip carries an SVG WMO icon: ${chip.text}`);
    assert.ok(chip.icons.includes('visibility'), `card weather chip carries the visibility icon: ${chip.text}`);
  }
  await openFirstCardModal(0);

  // (b) top 7-day summary vs the accordion below it — same tier word per date.
  const surfaces = await evaljs(`(() => {
    const top = [...document.querySelectorAll('#modal-summary .modal-overview .modal-day-row')].map(r => ({
      label: ((r.querySelector('.modal-day-label') || {}).textContent || '').trim(),
      tier: ((r.querySelector('.dg-chip') || {}).textContent || '').trim(),
      wx: ((r.querySelector('.modal-day-wx') || {}).textContent || '').trim(),
      wxIcon: !!(r.querySelector('.modal-day-wx svg[data-cl-icon]')),
      text: (r.innerText || '').replace(/\s+/g, ' ').trim(),
    }));
    const acc = [...document.querySelectorAll('#timeline-groups details.day-group')].map(d => ({
      date: d.dataset.date || '',
      tier: ((d.querySelector('summary .dg-chip') || {}).textContent || '').trim(),
      wx: ((d.querySelector('summary .dg-wx') || {}).textContent || '').trim(),
      wxIcon: !!(d.querySelector('summary .dg-wx svg[data-cl-icon]')),
      text: ((d.querySelector('summary') || {}).innerText || '').replace(/\s+/g, ' ').trim(),
    }));
    const base = new Date(new Intl.DateTimeFormat('en-CA', { timeZone: '${SPOT_TZ}', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date()) + 'T12:00:00Z');
    const dates = Array.from({ length: 7 }, (_, i) => new Date(base.getTime() + i * 86400000).toISOString().slice(0, 10));
    return { top, acc, dates };
  })()`);

  assert.equal(surfaces.top.length, 7, `the top summary still lists 7 days (got ${surfaces.top.length})`);
  if (surfaces.acc.length < 1) {
    // The accordion is built from the HOURLY shard, grouped from the place-local
    // today. If the served shard has no row on/after the anchor day, zero groups
    // is the honest render (the state reviewer condition 3 describes) and the
    // parity it guards is unmeasurable here — skip with the reason. If the shard
    // DOES reach the anchor, an empty accordion is a real defect and must fail.
    assert.equal(SHARD_REACHES_ANCHOR, false,
      `the accordion renders at least one day group — the served hourly shard DOES carry rows on/after ${ANCHOR_DAY}, so an empty accordion is a defect, not missing data`);
    t.skip(`no hourly shard row on/after the anchor day ${ANCHOR_DAY} (weather_details is a committed copy whose newest row predates it) — the day accordion is legitimately empty, so card↔accordion parity cannot be measured here`);
    return;
  }

  let compared = 0;
  surfaces.top.forEach((row, i) => {
    const day = surfaces.acc.find(a => a.date === surfaces.dates[i]);
    if (!day) return;
    compared++;
    assert.equal(row.tier, day.tier,
      `day ${i} (${row.label}) carries ONE tier on both surfaces — top 「${row.tier}」 vs accordion 「${day.tier}」`);
    assert.equal(row.wx, day.wx,
      `day ${i} (${row.label}) carries ONE weather chip on both surfaces — top 「${row.wx}」 vs accordion 「${day.wx}」`);
    assert.ok(row.wx, `day ${i} (${row.label}) renders a WMO + temperature chip in the top summary`);
    // CL-UI-115 §1: the WMO glyph is now an inline SVG (emoji only as fallback).
    assert.ok(row.wxIcon, `day ${i} (${row.label}) WMO SVG icon present: ${row.wx}`);
    assert.ok(day.wxIcon, `day ${i} (${row.label}) accordion WMO SVG icon present: ${day.wx}`);
    assert.match(row.wx, /-?\d+–-?\d+°C/, `day ${i} (${row.label}) temperature range present: ${row.wx}`);
  });
  assert.ok(compared >= 5, `at least 5 days were compared across both surfaces (got ${compared})`);

  // (c) the hourly rows carry the WMO icon + that hour's temperature next to
  //     the plain-language weather (owner: 「☁️ 18°C · 陰 · 低雲 · 能見度良好」).
  const hourly = await evaljs(`(() => {
    const rows = [...document.querySelectorAll('#timeline-groups details.day-group[open] tbody tr')];
    const wx = rows.map(r => ({ text: ((r.querySelector('.wx') || {}).textContent || '').trim(), icon: !!(r.querySelector('.wx svg[data-cl-icon]')) })).filter(x => x.text);
    return { count: wx.length, sample: wx.slice(0, 6) };
  })()`);
  assert.ok(hourly.count > 0, 'the open day group renders hourly weather rows');
  for (const cell of hourly.sample) {
    const txt = cell.text;
    // CL-UI-115 §1: the WMO glyph is an inline SVG, not an emoji codepoint.
    assert.ok(cell.icon, `hourly plain weather carries a WMO SVG icon: ${txt}`);
    assert.match(txt, /-?\d+(\.\d+)?°C/, `hourly plain weather carries the hour temperature: ${txt}`);
    assert.ok(!/undefined|NaN|null/.test(txt), `hourly plain weather has no placeholder value: ${txt}`);
  }
});
