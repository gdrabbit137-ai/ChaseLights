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
//   (2) with the sidecar 404ing, the shipped lazy shard path still runs and
//       cards get their now rows from the shards;
//   (3) a place absent from the artifact keeps the day chip and triggers no
//       shard download (absence is the generator's honest signal);
//   (4) an artifact whose `generated_at` predates the bundle by more than a day
//       is ignored in favour of the shard path.
//
// Harness: headless Chrome over CDP against a static server rooted at the repo.
// The shards are served as SMALL synthetic files (today's 24 local rows at the
// place's own hours): the committed shards are stale by design (they end days
// before "today"), so a real file would prove only the day-chip fallback, and
// 2.3 MB per card is pointless IO for a request-count assertion.
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

const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

const MIME = {'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.ico':'image/x-icon','.woff2':'font/woff2','.jpg':'image/jpeg'};
// Every response is no-store: the assertions count SERVER-SIDE requests, and a
// heuristically cached JSON (no validators on this server) would silently drop
// one from the log on the second page load.
const NO_STORE = {'cache-control':'no-store'};
const TPE = 'Asia/Taipei';
const tpeDate = () => new Intl.DateTimeFormat('en-CA', {timeZone: TPE, year:'numeric', month:'2-digit', day:'2-digit'}).format(new Date());
const tpeHour = () => Number(new Intl.DateTimeFormat('en-GB', {timeZone: TPE, hour:'2-digit', hour12:false}).format(new Date())) % 24;

// ------------------------------------------------ static page + request log
let scenario = 'ok';            // 'ok' | '404' | 'stale'
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

function sidecarBody() {
  const copy = JSON.parse(JSON.stringify(FIXTURE));
  copy.generated_at = BUNDLE.generated_at;           // published with THIS bundle
  const today = tpeDate();
  for (const p of Object.values(copy.places)) p.local_date = today;
  if (scenario === 'stale') copy.generated_at = new Date(Date.parse(BUNDLE.generated_at) - 5 * 86400000).toISOString();
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
        if (scenario === '404') { res.writeHead(404, NO_STORE); res.end('not found'); return; }
        const body = sidecarBody();
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

// Fresh page load per scenario; returns the DOM snapshot the assertions use.
async function load(sidecarScenario) {
  scenario = sidecarScenario;
  requests.length = 0;
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
  const wantState = sidecarScenario === 'ok' ? 'ready' : 'unusable';
  const settleDeadline = Date.now() + 45000;
  let last = null, stable = 0;
  while (Date.now() < settleDeadline) {
    const probe = await evaljs(`(() => ({
      state: (window.__clui117 && window.__clui117.state && window.__clui117.state()) || '',
      now: document.querySelectorAll('#spots-container .card .now-wx').length,
    }))()`).catch(() => ({state: '', now: -1}));
    if (probe.state === wantState && probe.now > 0 && probe.now === last) {
      if (++stable >= 3) break;
    } else {
      stable = 0;
    }
    last = probe.now;
    await sleep(250);
  }

  const snapshot = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    return {
      cards: cards.length,
      ids: cards.map(c => c.getAttribute('data-place-id')),
      nowIds: cards.filter(c => c.querySelector('.now-wx')).map(c => c.getAttribute('data-place-id')),
      nowHours: cards.filter(c => c.querySelector('.now-wx')).map(c => c.querySelector('.now-wx').getAttribute('data-now-hour')),
      dayChipOnly: cards.filter(c => !c.querySelector('.now-wx') && c.querySelector('.day-wx')).map(c => c.getAttribute('data-place-id')),
      state: window.__clui117 && window.__clui117.state(),
    };
  })()`);
  snapshot.sidecar = requests.filter(u => /now-latest\.json/.test(u));
  snapshot.shards = requests.filter(u => /weather_details\//.test(u));
  // Reported, not asserted: the exact traffic of this page load (the numbers the
  // ticket quotes come from here — sidecar path vs fallback path).
  console.log('CL-UI-117 [' + sidecarScenario + '] cards=' + snapshot.cards
    + ' sidecarRequests=' + snapshot.sidecar.length + ' shardRequests=' + snapshot.shards.length
    + ' nowRows=' + snapshot.nowIds.length + ' state=' + snapshot.state);
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
  const s = await load('404');
  assert.equal(s.state, 'unusable', 'a 404 marks the artifact unusable');
  assert.equal(s.sidecar.length, 1, 'the artifact is still attempted exactly once');
  assert.ok(s.shards.length > 0, `the shipped shard path runs (got ${s.shards.length} shard requests)`);
  assert.ok(s.nowIds.length > 0,
    `cards still get a now row from the shards (got ${s.nowIds.length} of ${s.cards} cards)`);
  // The fallback stays lazy: only cards near the viewport were fetched, never all 124.
  assert.ok(s.shards.length < s.cards, `lazy (IntersectionObserver) fetching, not a bulk download (${s.shards.length} < ${s.cards})`);
});

test('CL-UI-117: a sidecar lagging the bundle by more than a day is ignored', {timeout: 300000}, async t => {
  await boot();
  const s = await load('stale');
  assert.equal(s.state, 'unusable', 'the stale artifact must not paint a now row');
  assert.ok(s.shards.length > 0, `the shard path takes over (got ${s.shards.length} shard requests)`);
  assert.ok(s.nowIds.length > 0, `cards still get rows from the shards (got ${s.nowIds.length})`);
});

test('CL-UI-117: cache stamps bump clui140 → clui141 on all five root pages', () => {
  assert.match(INDEX, /assets\/app\.js\?v=clui141/, 'index.html loads app.js with the new stamp');
  assert.match(INDEX, /assets\/icons\.js\?v=clui141/, 'index.html loads icons.js with the new stamp');
  assert.match(INDEX, /assets\/app\.css\?v=clui141/, 'index.html loads app.css with the new stamp');
  for (const page of ['404.html', 'genre-eval.html', 'reminders.html', 'sources.html']) {
    const src = readFileSync(join(APP, page), 'utf8');
    assert.match(src, /assets\/app\.css\?v=clui141/, `${page} loads app.css with the new stamp`);
    assert.ok(!/clui140/.test(src), `${page} carries no stale clui140 stamp`);
  }
});

test.after(async () => {
  try { ws?.close(); } catch {}
  try { chrome?.kill(); } catch {}
  try { await new Promise(r => server?.close(r)); } catch {}
});
