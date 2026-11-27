// CL-UI-117 — the card's now-hour row is served by the precomputed sidecar.
//
// CL-UI-115 made each card lazily fetch `weather_details/<region>/<place>.json`
// (~2.3 MB, concurrency 4) to render the current-hour row. CL-DATA-115 publishes
// ONE compact artifact (`apps/web-v2/now-latest.json`, ~50 KB, built by
// data/v2/tools/build_now_sidecar.py) carrying the same pick for every place.
// This file proves, over a real page load with a request-logging server, that:
//   (1) with the sidecar served, the page issues exactly ONE `now-latest.json`
//       request and ZERO `weather_details/` requests, and every card whose place
//       is in the artifact paints a `.now-wx` row;
//   (2) a re-render AFTER the artifact settled repaints every card (the
//       settle-time paint is one-shot — cards built in a later pass, or still
//       detached at that instant, used to stay empty for the page lifetime);
//   (3) a place absent from the artifact keeps the day chip and triggers no
//       shard download (absence is the generator's honest signal);
//   (4) with the sidecar 404ing, the shipped lazy shard path still runs;
//   (5) an artifact older than the wall-clock freshness bound (26 h) is ignored
//       in favour of the shards — asserted on the DOM, not on source text — and
//       one just INSIDE the bound is still used (both sides of the bound);
//   (6) a TRANSIENT failure (503) does not poison the promise for the page
//       lifetime: a later attempt succeeds and the cards switch to sidecar rows;
//   (7) date rollover: a yesterday-stamped artifact is re-fetched, and one
//       stamped today but carrying yesterday's rows falls back to the shards;
//       a re-fetch that is STILL yesterday-stamped leaves no card without a row.
//   (8) the full-set repaint is coalesced (one pass per tick) and costs a small
//       fraction of the CL-UI-45 date-switch budget over the real 124-card list.
//
// NOTE — WRONG DEVICE CLOCK (intended degradation): both freshness gates (the
// 26 h artifact bound and the 1 h/6 h hour tiers) read the DEVICE clock, so a
// device whose clock is off by more than the bound gets NO now row and keeps the
// honest day chip. That is deliberate — the artifact is stamped by the publisher
// and an untrusted clock cannot produce a present tense — so there is no test
// here asserting a row for a skewed clock. Do not "fix" that blank row.
//
// Harness: headless Chrome over CDP against a static server rooted at the repo.
// The shards are served as SMALL synthetic files (today's 24 local rows at the
// place's own hours): the committed shards are stale by design (they end days
// before "today"), so a real file would prove only the day-chip fallback, and
// 2.3 MB per card is pointless IO for a request-count assertion.
//
// The sidecar rows are re-stamped per request (local date = today, hour = the
// place's current hour, a distinctive 41.5 °C) so the suite is independent of
// the time of day and the assertions can tell a SIDECAR row from a SHARD row in
// the DOM by its temperature alone.
//
// Run: CHROMIUM_EXECUTABLE="C:/Program Files/Google/Chrome/Application/chrome.exe" \
//      node --test apps/web-v2/tests/cl-ui-117-now-sidecar.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
import {readFileSync, mkdtempSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP = join(HERE, '..', '..', '..');
const INDEX = readFileSync(join(APP, 'index.html'), 'utf8');
const BUNDLE = JSON.parse(readFileSync(join(APP, 'apps', 'web-v2', 'evaluations-latest.json'), 'utf8'));
const FIXTURE = JSON.parse(readFileSync(join(HERE, 'fixtures', 'now-latest.clui117.json'), 'utf8'));
// The client's freshness bound (assets/app.js CLUI117_MAX_AGE_MS), mirrored as a
// literal so a change to the product constant shows up as a red test instead of
// silently re-basing the fixture ages.
const MAX_AGE_MS = 26 * 60 * 60 * 1000;

const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

const MIME = {'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.ico':'image/x-icon','.woff2':'font/woff2','.jpg':'image/jpeg'};
// Every response is no-store: the assertions count SERVER-SIDE requests, and a
// heuristically cached JSON (no validators on this server) would silently drop
// one from the log on the second page load.
const NO_STORE = {'cache-control':'no-store'};
const TPE = 'Asia/Taipei';
const SIDECAR_TEMP = '41.5';    // marks a row that came from the artifact
const tpeDate = () => new Intl.DateTimeFormat('en-CA', {timeZone: TPE, year:'numeric', month:'2-digit', day:'2-digit'}).format(new Date());
const tpeHour = () => Number(new Intl.DateTimeFormat('en-GB', {timeZone: TPE, hour:'2-digit', hour12:false}).format(new Date())) % 24;
const tpeDateOffset = days => new Intl.DateTimeFormat('en-CA', {timeZone: TPE, year:'numeric', month:'2-digit', day:'2-digit'}).format(new Date(Date.now() + days * 86400000));
// Epoch of a place-local (Asia/Taipei, fixed UTC+8) date+time — builds stamps
// that sit deterministically on a given side of place-local midnight.
const tpeStamp = (date, hhmm) => {
  const [y, m, d] = date.split('-').map(Number);
  const [H, M] = hhmm.split(':').map(Number);
  return new Date(Date.UTC(y, m - 1, d, H - 8, M)).toISOString();
};

// ------------------------------------------------ static page + request log
let scenario = 'ok';            // ok | 404 | stale | fresh-edge | flaky | rollover | rolloverstuck | datedmiss
let sidecarHits = 0;            // now-latest.json requests in THIS page load
const requests = [];            // every URL the page asked for, query string included
let server, baseURL, chrome, ws, send, evaljs, ready;
const pendingCalls = new Map();
let nextId = 0;
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Minimal shard with today's 24 local rows — the shape assets/app.js reads
// (payload.spot.hourly_forecast[] with time/local_date/weather_code/temp/visibility).
function shardBody(placeId) {
  const today = tpeDate();
  const rows = [];
  for (let h = 0; h < 24; ++h) {
    const hh = String(h).padStart(2, '0');
    rows.push({time:`${today} ${hh}:00`, local_date:today, weather_code:3, temp:19 + (h % 5), visibility:14});
  }
  return JSON.stringify({spot:{spot_id:placeId, timezone:TPE, hourly_forecast:rows}});
}

// `hit` is 1-based within the page load.
function sidecarBody(hit) {
  const copy = JSON.parse(JSON.stringify(FIXTURE));
  const today = tpeDate();
  const hour = String(tpeHour()).padStart(2, '0') + ':00';
  for (const p of Object.values(copy.places)) {
    p.local_date = today;
    p.hour = hour;
    p.temp_c = Number(SIDECAR_TEMP);
  }
  copy.generated_at = new Date().toISOString();
  if (scenario === 'stale') copy.generated_at = new Date(Date.now() - (MAX_AGE_MS + 3600000)).toISOString();      // 27 h
  if (scenario === 'fresh-edge') copy.generated_at = new Date(Date.now() - (MAX_AGE_MS - 3600000)).toISOString();  // 25 h
  if (scenario === 'rollover' && hit === 1) {
    // Published on the PREVIOUS local day: every row it carries is yesterday's.
    // The re-fetch (hit 2) is a fresh, today's artifact.
    const yesterday = tpeDateOffset(-1);
    for (const p of Object.values(copy.places)) p.local_date = yesterday;
    copy.generated_at = tpeStamp(yesterday, '23:00');
  }
  if (scenario === 'rolloverstuck') {
    // Published yesterday AND the re-fetch is still yesterday's (the pipeline has
    // not republished): the client cannot get a row from the artifact at all, so
    // the card must fall through to the shard / day chip — never an empty slot.
    const yesterday = tpeDateOffset(-1);
    for (const p of Object.values(copy.places)) p.local_date = yesterday;
    copy.generated_at = tpeStamp(yesterday, '23:00');
  }
  if (scenario === 'datedmiss') {
    // Stamped TODAY but carrying yesterday's rows: the generator itself had no
    // today row, so a re-fetch cannot help — the shards are the honest source.
    const yesterday = tpeDateOffset(-1);
    for (const p of Object.values(copy.places)) p.local_date = yesterday;
    copy.generated_at = tpeStamp(today, '00:05');
  }
  return JSON.stringify(copy);
}

async function boot() {
  if (ready) return ready;
  ready = (async () => {
    server = createServer((req, res) => {
      res.on('error', () => {});
      requests.push(req.url);
      const raw = req.url.split('?')[0];
      if (raw === '/apps/web-v2/now-latest.json') {
        sidecarHits += 1;
        if (scenario === '404') { res.writeHead(404, NO_STORE); res.end('not found'); return; }
        if (scenario === 'flaky' && sidecarHits === 1) { res.writeHead(503, NO_STORE); res.end('busy'); return; }
        const body = sidecarBody(sidecarHits);
        res.writeHead(200, {...NO_STORE, 'content-type':'application/json', 'content-length':Buffer.byteLength(body)});
        res.end(body); return;
      }
      const shard = /^\/weather_details\/[^/]+\/([^/]+)\.json$/.exec(raw);
      if (shard) {
        const body = shardBody(decodeURIComponent(shard[1]));
        res.writeHead(200, {...NO_STORE, 'content-type':'application/json', 'content-length':Buffer.byteLength(body)});
        res.end(body); return;
      }
      const p = raw.replace(/\/+$/, '') || '/';
      const file = join(APP, p === '/' ? 'index.html' : decodeURIComponent(p.slice(1)));
      try {
        const body = readFileSync(file);
        res.writeHead(200, {...NO_STORE, 'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
        res.end(body);
      } catch { res.writeHead(404); res.end('not found'); }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    baseURL = `http://127.0.0.1:${server.address().port}/`;

    chrome = spawn(BROWSER, [
      '--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
      '--enable-unsafe-swiftshader','--use-angle=swiftshader',
      '--no-first-run','--remote-debugging-port=0','--window-size=1280,900',
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui117-')), 'about:blank',
    ], {stdio:['ignore','ignore','pipe']});
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = '';
      const t = setTimeout(() => reject(new Error('no devtools endpoint')), 60000);
      chrome.stderr.on('data', d => {
        buf += d;
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearTimeout(t); resolve(m[1]); }
      });
      chrome.on('error', e => reject(new Error('spawn: ' + e.message)));
    });
    const dbgHost = wsUrl.match(/ws:\/\/([^/]+)/)[1];
    let targets = [];
    for (let i = 0; i < 40; ++i) {
      targets = await (await fetch(`http://${dbgHost}/json/list`)).json();
      if (targets.some(t => t.type === 'page')) break;
      await sleep(250);
    }
    ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
    await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
    ws.onmessage = e => {
      const m = JSON.parse(e.data);
      if (m.id && pendingCalls.has(m.id)) { pendingCalls.get(m.id)(m); pendingCalls.delete(m.id); }
    };
    send = (method, params = {}) => new Promise((resolve, reject) => {
      const i = ++nextId;
      pendingCalls.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
      ws.send(JSON.stringify({id:i, method, params}));
    });
    evaljs = async expr => {
      const r = await send('Runtime.evaluate', {expression:expr, returnByValue:true, awaitPromise:true});
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
      return r.result?.value;
    };
    await send('Page.enable');
  })().catch(e => { ready = null; throw e; });
  return ready;
}

const PROBE = `(() => ({
  state: (window.__clui117 && window.__clui117.state && window.__clui117.state()) || '',
  now: document.querySelectorAll('#spots-container .card .now-wx').length,
}))()`;

// Fresh page load per scenario; returns the DOM snapshot the assertions use.
// `want` is the terminal sidecar state; `extra` is an extra page-side condition
// that must also hold before the page counts as settled.
async function load(sidecarScenario, {want = 'ready', extra = null} = {}) {
  scenario = sidecarScenario;
  requests.length = 0;
  sidecarHits = 0;
  await send('Page.navigate', {url: baseURL + 'index.html'});
  let cards = 0;
  for (let i = 0; i < 60 && cards === 0; ++i) {
    await sleep(1000);
    cards = await evaljs(`document.querySelectorAll('#spots-container .card').length`).catch(() => 0);
  }
  assert.ok(cards > 0, `${sidecarScenario}: cards must render`);
  // Deterministic settle. Fixed sleeps made this suite flaky: under load the
  // sidecar paint (ok) or the lazy shard paint (404/stale) can land later than
  // 4-8 s, so a snapshot taken on a timer reads a half-painted page.
  // Poll the probe until the scenario reaches its terminal state AND the number
  // of painted now rows has stopped moving for three consecutive samples.
  const settleDeadline = Date.now() + 45000;
  let last = null, stable = 0;
  while (Date.now() < settleDeadline) {
    const probe = await evaljs(`(() => {
      const p = ${PROBE};
      p.extra = ${extra ? `(${extra})` : 'true'};
      return p;
    })()`).catch(() => ({state: '', now: -1, extra: false}));
    if (probe.state === want && probe.now > 0 && probe.now === last && probe.extra) {
      if (++stable >= 3) break;
    } else {
      stable = 0;
    }
    last = probe.now;
    await sleep(250);
  }

  const snapshot = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const host = document.querySelector('#spots-container') || {textContent:''};
    return {
      cards: cards.length,
      epoch: window.__clV2Epoch || 0,
      ids: cards.map(c => c.getAttribute('data-place-id')),
      nowIds: cards.filter(c => c.querySelector('.now-wx')).map(c => c.getAttribute('data-place-id')),
      nowHours: cards.filter(c => c.querySelector('.now-wx')).map(c => c.querySelector('.now-wx').getAttribute('data-now-hour')),
      dayChipOnly: cards.filter(c => !c.querySelector('.now-wx') && c.querySelector('.day-wx')).map(c => c.getAttribute('data-place-id')),
      sidecarTemp: host.textContent.includes('${SIDECAR_TEMP}'),
      state: window.__clui117 && window.__clui117.state(),
      generatedAt: (window.__clui117 && window.__clui117.generatedAt && window.__clui117.generatedAt()) || null,
      attempts: (window.__clui117 && window.__clui117.attempts && window.__clui117.attempts()) || 0,
    };
  })()`);
  snapshot.sidecar = requests.filter(u => /now-latest\.json/.test(u));
  snapshot.shards = requests.filter(u => /weather_details\//.test(u));
  // Reported, not asserted: the exact traffic of this page load (the numbers the
  // ticket quotes come from here — sidecar path vs fallback path).
  console.log('CL-UI-117 [' + sidecarScenario + '] cards=' + snapshot.cards
    + ' sidecarRequests=' + snapshot.sidecar.length + ' shardRequests=' + snapshot.shards.length
    + ' nowRows=' + snapshot.nowIds.length + ' state=' + snapshot.state
    + ' sidecarTemp=' + snapshot.sidecarTemp);
  return snapshot;
}

// ------------------------------------------------------------------ fixtures
const FIXTURE_IDS = Object.keys(FIXTURE.places);

test('CL-UI-117: the sidecar is fetched ONCE per page load and feeds every card', {timeout: 240000}, async t => {
  await boot();
  const s = await load('ok');
  assert.equal(s.state, 'ready', 'a served, fresh artifact is used');
  assert.equal(s.sidecar.length, 1, `exactly one now-latest.json request per page load (got ${s.sidecar.length})`);
  // Cache-buster derived from the loaded bundle's generated_at.
  assert.ok(s.sidecar[0].includes('?v=' + encodeURIComponent(BUNDLE.generated_at)),
    `the request carries the bundle stamp as cache-buster (got ${s.sidecar[0]})`);
  assert.equal(s.shards.length, 0, `no weather_details/ request in the sidecar path (got ${s.shards.join(', ')})`);
  const expected = s.ids.filter(id => FIXTURE_IDS.includes(id));
  assert.ok(expected.length > 0, 'the rendered list must contain places the artifact covers (non-vacuous)');
  const painted = s.nowIds.filter(id => FIXTURE_IDS.includes(id));
  assert.deepEqual(painted.sort(), expected.slice().sort(),
    'every card whose place is in the artifact renders a now row');
  assert.ok(s.nowHours.every(h => /^\d{2}:\d{2}$/.test(String(h))),
    `each now row labels a served hour (got ${JSON.stringify(s.nowHours.slice(0, 4))})`);
  // The rows really came from the artifact, not from a shard: the artifact's
  // distinctive temperature is on screen.
  assert.equal(s.sidecarTemp, true, 'the painted rows carry the artifact\'s values');
});

test('CL-UI-117: a re-render after the artifact settled repaints EVERY card', {timeout: 240000}, async t => {
  // Reviewer finding: the settle-time paint was one-shot, so a card built in a
  // render pass that ran AFTER the artifact landed kept an empty row for the
  // life of the page (15 of 18 painted, tw-010 / tw-025 / tw-111 stayed blank).
  // Force a real list pass (a sort change wipes and rebuilds the container) and
  // prove the NEWLY BUILT cards are painted too.
  await boot();
  const before = await load('ok');
  assert.equal(before.state, 'ready');
  const epochBefore = before.epoch;
  const requestsBefore = requests.length;
  const expectedIds = before.ids.filter(id => FIXTURE_IDS.includes(id)).sort();
  await evaljs(`(() => { setSortMode('hours_desc'); })()`);
  const deadline = Date.now() + 30000;
  let after = null;
  while (Date.now() < deadline) {
    after = await evaljs(`(() => {
      const cards = [...document.querySelectorAll('#spots-container .card')];
      return {
        epoch: window.__clV2Epoch || 0,
        cards: cards.length,
        nowIds: cards.filter(c => c.querySelector('.now-wx')).map(c => c.getAttribute('data-place-id')),
      };
    })()`);
    const paintedNow = after.nowIds.filter(id => FIXTURE_IDS.includes(id)).sort();
    if (after.epoch > epochBefore && after.cards > 0 && paintedNow.join() === expectedIds.join()) break;
    await sleep(250);
  }
  assert.ok(after.epoch > epochBefore, `a real render pass ran (epoch ${epochBefore} → ${after.epoch})`);
  const painted = after.nowIds.filter(id => FIXTURE_IDS.includes(id)).sort();
  assert.deepEqual(painted, expectedIds, 'the rebuilt cards all carry a now row');
  assert.equal(requests.slice(requestsBefore).filter(u => /now-latest\.json/.test(u)).length, 0,
    'the re-render does not re-fetch the artifact (it is already ready)');
});

test('CL-UI-117: a place absent from the sidecar keeps the day chip and downloads no shard', {timeout: 240000}, async t => {
  await boot();
  const s = await load('ok');
  assert.equal(s.state, 'ready', 'artifact used, so absence is meaningful');
  const absent = s.ids.filter(id => !FIXTURE_IDS.includes(id));
  assert.ok(absent.length > 0, 'the page renders places the artifact omits (non-vacuous)');
  assert.equal(s.nowIds.filter(id => absent.includes(id)).length, 0,
    'no now row is invented for an omitted place');
  assert.equal(s.shards.length, 0,
    `an omitted place must not trigger a 2.3 MB shard fetch (got ${s.shards.length})`);
  assert.ok(s.dayChipOnly.length > 0, 'omitted places keep an honest day chip');
});

test('CL-UI-117: a 404ing sidecar falls back to the lazily fetched shards', {timeout: 300000}, async t => {
  await boot();
  const s = await load('404', {want: 'unusable'});
  assert.equal(s.state, 'unusable', 'a 404 marks the artifact unusable');
  // The promise is dropped on failure (a retry is allowed), so the artifact may
  // be attempted more than once — but never unboundedly.
  assert.ok(s.sidecar.length >= 1 && s.sidecar.length <= 3,
    `the artifact is attempted a bounded number of times (got ${s.sidecar.length})`);
  assert.ok(s.shards.length > 0, `the shipped shard path runs (got ${s.shards.length} shard requests)`);
  assert.ok(s.nowIds.length > 0,
    `cards still get a now row from the shards (got ${s.nowIds.length} of ${s.cards} cards)`);
  assert.equal(s.sidecarTemp, false, 'no row is painted from the failing artifact');
  // The fallback stays lazy: only cards near the viewport were fetched, never all 124.
  assert.ok(s.shards.length < s.cards, `lazy (IntersectionObserver) fetching, not a bulk download (${s.shards.length} < ${s.cards})`);
});

test('CL-UI-117: an artifact past the 26 h wall-clock bound is unusable (DOM-level)', {timeout: 300000}, async t => {
  await boot();
  const s = await load('stale', {want: 'unusable'});
  assert.equal(s.state, 'unusable', 'an artifact past the freshness bound must not paint a now row');
  assert.equal(s.generatedAt, null, 'the stale artifact is not kept as the row source');
  assert.equal(s.sidecarTemp, false, 'no card shows the stale artifact\'s values (DOM, not source text)');
  assert.ok(s.shards.length > 0, `the shard path takes over (got ${s.shards.length} shard requests)`);
  assert.ok(s.nowIds.length > 0, `cards still get rows from the shards (got ${s.nowIds.length})`);
  // Same upper bound as case 3: the fallback is lazy, never a bulk download.
  assert.ok(s.shards.length < s.cards, `lazy fallback, not a bulk download (${s.shards.length} < ${s.cards})`);
});

test('CL-UI-117: an artifact just INSIDE the 26 h bound is still used (both sides proven)', {timeout: 300000}, async t => {
  await boot();
  const s = await load('fresh-edge');
  assert.equal(s.state, 'ready', '25 h old is within the bound');
  assert.equal(s.shards.length, 0, 'no shard backup for a usable artifact');
  assert.equal(s.sidecarTemp, true, 'the artifact\'s own values are on screen');
  const expected = s.ids.filter(id => FIXTURE_IDS.includes(id));
  assert.deepEqual(s.nowIds.filter(id => FIXTURE_IDS.includes(id)).sort(), expected.slice().sort(),
    'every covered card paints from the artifact');
});

test('CL-UI-117: a TRANSIENT sidecar failure is retried — the shard path is not permanent', {timeout: 300000}, async t => {
  await boot();
  // First attempt 503, second succeeds. The reviewer's bug: the promise was never
  // nulled, so one transient 5xx locked the page into the shard path forever.
  const s = await load('flaky', {want: 'ready', extra: '(window.__clui117.attempts() >= 2)'});
  assert.equal(s.state, 'ready', 'the retry recovers the artifact path');
  assert.ok(s.sidecar.length >= 2, `the artifact is re-attempted after the failure (got ${s.sidecar.length})`);
  assert.equal(s.sidecarTemp, true, 'the recovered artifact supplies the painted rows');
  const expected = s.ids.filter(id => FIXTURE_IDS.includes(id));
  assert.deepEqual(s.nowIds.filter(id => FIXTURE_IDS.includes(id)).sort(), expected.slice().sort(),
    'every covered card is repainted from the recovered artifact');
  // The fallback engaged while the artifact was failing, but stayed lazy.
  assert.ok(s.shards.length <= s.cards, `shard usage stays bounded (${s.shards.length} ≤ ${s.cards})`);
});

test('CL-UI-117: date rollover — a yesterday-stamped artifact is re-fetched', {timeout: 300000}, async t => {
  await boot();
  // The first response carries yesterday's stamp and yesterday's rows; the
  // client must notice the rollover, re-fetch, and use the fresh second answer.
  const s = await load('rollover', {want: 'ready', extra: 'document.querySelectorAll("#spots-container .card .now-wx").length > 0'});
  assert.equal(s.state, 'ready', 'the refreshed artifact is usable');
  assert.ok(s.sidecar.length >= 2, `the artifact is re-fetched across local midnight (got ${s.sidecar.length})`);
  assert.equal(s.sidecarTemp, true, 'the fresh artifact supplies the rows (yesterday\'s did not)');
  const expected = s.ids.filter(id => FIXTURE_IDS.includes(id));
  assert.deepEqual(s.nowIds.filter(id => FIXTURE_IDS.includes(id)).sort(), expected.slice().sort(),
    'every covered card gets a row again after midnight');
});

test('CL-UI-117: date rollover — a today-stamped artifact with yesterday\'s rows falls back to shards', {timeout: 300000}, async t => {
  await boot();
  // Re-fetching cannot help (the generator itself published no today row), so the
  // honest answer is the lazy shard — never a silently empty row.
  const s = await load('datedmiss', {want: 'ready'});
  assert.equal(s.state, 'ready', 'the artifact itself is valid');
  assert.equal(s.sidecarTemp, false, 'its yesterday rows are not painted as now');
  assert.ok(s.shards.length > 0, `the shard path supplies today's rows (got ${s.shards.length})`);
  assert.ok(s.nowIds.length > 0, `cards still get a now row (got ${s.nowIds.length})`);
  assert.ok(s.shards.length < s.cards, `and it stays lazy (${s.shards.length} < ${s.cards})`);
});

test('CL-UI-117: a re-fetch that is STILL yesterday-stamped never leaves an empty weather slot', {timeout: 300000}, async t => {
  await boot();
  // Reviewer condition 1. The card that triggers the forced refresh used to
  // `return` without engaging the shard path; when the refetched artifact was
  // still yesterday-stamped that card ended with NO row at all (and the comment
  // claiming "either way the row is not silently lost" was false). The branch now
  // re-queues its settle handler, so the card falls through to the shard path.
  const s = await load('rolloverstuck', {
    want: 'ready',
    // Covered cards that sit near the viewport must end with a now row from the
    // shard (the shipped CL-UI-115 loader is viewport-driven: an off-screen card
    // legitimately has not fetched yet).
    extra: `(() => {
      const ids = ${JSON.stringify(FIXTURE_IDS)};
      return [...document.querySelectorAll('#spots-container .card')].filter(c => {
        const r = c.getBoundingClientRect();
        return r.bottom > -300 && r.top < innerHeight + 300 && ids.includes(c.getAttribute('data-place-id'));
      }).every(c => !!c.querySelector('.now-wx'));
    })()`,
  });
  assert.equal(s.state, 'ready', 'the artifact is fresh enough to be used');
  assert.ok(s.sidecar.length >= 2, `the rollover triggers exactly one re-fetch (got ${s.sidecar.length})`);
  assert.equal(s.sidecarTemp, false, "yesterday's rows are never painted as now");
  assert.ok(s.shards.length > 0, `the fall-through engages the shard path (got ${s.shards.length} shard requests)`);
  assert.ok(s.nowIds.length > 0, `cards still get rows from the shards (got ${s.nowIds.length})`);
  // The bug was a card with NO row at all. Proof, scoped to the cards the shard
  // path actually reached (the shipped CL-UI-115 loader is viewport-driven, so an
  // off-screen card is not expected to have fetched yet): every covered card near
  // the viewport must end with a now row, and no visible card may be an empty
  // weather slot (no now row AND no labelled day chip).
  const visible = await evaljs(`(() => {
    const ids = ${JSON.stringify(FIXTURE_IDS)};
    const out = {covered:[], painted:[], empty:[]};
    for (const c of document.querySelectorAll('#spots-container .card')) {
      const id = c.getAttribute('data-place-id');
      if (!ids.includes(id)) continue;
      const r = c.getBoundingClientRect();
      if (r.bottom < -300 || r.top > innerHeight + 300) continue;
      const now = !!c.querySelector('.now-wx');
      const day = !!c.querySelector('.day-wx');
      if (!now && !day) out.empty.push(id);
      out.covered.push(id);
      if (now) out.painted.push(id);
    }
    return out;
  })()`);
  assert.ok(visible.covered.length > 0, 'non-vacuous: covered cards sit near the viewport');
  assert.deepEqual(visible.painted.sort(), visible.covered.slice().sort(),
    'every covered card the shard path reached ends with a now row — the triggering card is not lost');
  assert.deepEqual(visible.empty, [],
    'no visible card is left with an empty weather slot after a stuck rollover');
  const covered = s.ids.filter(id => FIXTURE_IDS.includes(id));
  assert.ok(covered.length > 0, 'non-vacuous: the list contains places the artifact covers');
});

test('CL-UI-117: the repaint hook is COALESCED — N schedules in one tick ⇒ one paint pass', {timeout: 240000}, async t => {
  await boot();
  const s = await load('ok');
  // Flush any paint already queued by the settle path, then count.
  const r = await evaljs(`(async () => {
    const raf = () => new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
    await raf();
    const before = window.__clui117.paintPasses();
    for (let i = 0; i < 124; ++i) window.__clui117.schedulePaint();
    await raf();
    return {before, after: window.__clui117.paintPasses()};
  })()`);
  assert.equal(r.after - r.before, 1,
    `124 renders inside one tick must produce ONE paint pass (got ${r.after - r.before})`);
  // Coalescing must not LOSE the paint: the rows the pass paints are still there,
  // and no card that had a row lost it.
  const after = await evaljs(`[...document.querySelectorAll('#spots-container .card')].filter(c => c.querySelector('.now-wx')).length`);
  assert.equal(after, s.nowIds.length, 'the coalesced pass leaves the same rows painted as before it');
  assert.ok(s.cards >= 100, `the measurement runs over the real list (${s.cards} cards)`);
});

test('CL-UI-117: a full 124-card repaint pass stays well inside the CL-UI-45 budget', {timeout: 240000}, async t => {
  await boot();
  const s = await load('ok');
  // CL-UI-45 (3a) budgets a whole date switch at < 600 ms and 11 switches at
  // < 4000 ms. The now-row repaint is ONE pass inside such a switch, so it must
  // cost a small fraction of 600 ms. Measured on the real list at 1280.
  const timing = await evaljs(`(() => {
    const runs = [];
    let painted = 0;
    for (let i = 0; i < 7; ++i) {
      const t0 = performance.now();
      painted = window.__clui117.repaint();
      runs.push(performance.now() - t0);
    }
    runs.sort((a, b) => a - b);
    return {cards: document.querySelectorAll('#spots-container .card').length, painted,
      median: Math.round(runs[3] * 10) / 10, max: Math.round(runs[6] * 10) / 10};
  })()`);
  console.log('CL-UI-117 repaint: cards=' + timing.cards + ' painted=' + timing.painted
    + ' median=' + timing.median + 'ms max=' + timing.max + 'ms (CL-UI-45 switch budget 600ms)');
  assert.ok(timing.cards >= 100, `measured on the real list (${timing.cards} cards)`);
  assert.equal(timing.painted, s.nowIds.length,
    'one pass repaints every card that carries a now row (nothing is skipped)');
  assert.ok(timing.median < 150,
    `a ${timing.cards}-card repaint must be well inside the 600 ms switch budget (median ${timing.median}ms)`);
  assert.ok(timing.max < 300, `no single repaint may approach the budget (max ${timing.max}ms)`);
});

test('CL-UI-117: the freshness bound and the cache-bust stamps are pinned', () => {
  assert.equal(MAX_AGE_MS, 26 * 60 * 60 * 1000, 'the fixture ages assume the 26 h bound');
  assert.match(INDEX, /assets\/app\.js\?v=clui144/, 'index.html loads app.js with the new stamp');
  assert.match(INDEX, /assets\/icons\.js\?v=clui144/, 'index.html loads icons.js with the new stamp');
  assert.match(INDEX, /assets\/app\.css\?v=clui144/, 'index.html loads app.css with the new stamp');
  for (const page of ['404.html', 'genre-eval.html', 'reminders.html', 'sources.html']) {
    const src = readFileSync(join(APP, page), 'utf8');
    assert.match(src, /assets\/app\.css\?v=clui144/, `${page} loads app.css with the new stamp`);
    assert.ok(!/clui141/.test(src), `${page} carries no stale clui141 stamp`);
  }
});

test.after(async () => {
  try { ws?.close(); } catch {}
  try { chrome?.kill(); } catch {}
  try { await new Promise(r => server?.close(r)); } catch {}
});
