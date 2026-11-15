// CL-UI-90 — reminders page mockup-first rebuild (Stage 3a).
// Spec source (逐字實作): origin/task/DESIGN-3 head 3d455f121 —
// data/v2/audits/design-mockups/mockup-reminders.html. Pure visual layer:
// notify_rules CRUD / bell semantics / favorites isolation / login gate
// contracts (CL-UI-58/61) are untouched — API paths and payload shapes below
// are asserted unchanged.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { spawn } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const read = (p) => readFileSync(join(ROOT, p), 'utf8');

const remHtml = read('reminders.html');
const pageJs = read('assets/reminders-page.js');
const clientJs = read('assets/reminders-client.js');
const bundle = JSON.parse(read('apps/web-v2/evaluations-latest.json'));

// ---- (1) page anatomy pins (mockup 逐字對應) -------------------------------
test('CL-UI-90 (1) reminders.html carries the mockup add-flow anatomy', () => {
  // title row + count
  assert.match(remHtml, /<h1>🔔 <span id="page-title">/);
  assert.match(remHtml, /id="rem-count"/);
  // three-tier flow with arrow indicators + parallel keyword search
  assert.match(remHtml, /class="rem-add-flow"/);
  assert.match(remHtml, /<select id="rem-region" aria-label="地區"><\/select>/);
  assert.match(remHtml, /<span class="rem-arrow" aria-hidden="true">→<\/span>/);
  assert.match(remHtml, /<select id="rem-place" aria-label="景點"><\/select>/);
  assert.match(remHtml, /<select id="rem-subject" aria-label="題材"><\/select>/);
  assert.match(remHtml, /<input id="rem-search" class="rem-search" type="search"/);
  assert.match(remHtml, /<ul id="rem-results" class="rem-results"><\/ul>/);
  // add preview row (hidden until a place is picked) + flow hint
  assert.match(remHtml, /id="rem-preview" hidden/);
  assert.match(remHtml, /id="rem-preview-txt"/);
  assert.match(remHtml, /id="rem-flow-hint"/);
});

test('CL-UI-90 (2) reminders.html carries the card, streak and empty-state hosts', () => {
  // card anatomy host + standard empty state (dashed frame + icon + CTA)
  assert.match(remHtml, /<div class="rem-empty" id="rem-empty" hidden>/);
  assert.match(remHtml, /class="rem-e-ic"/);
  assert.match(remHtml, /id="rem-empty-title"/);
  assert.match(remHtml, /id="rem-empty-desc"/);
  assert.match(remHtml, /id="rem-empty-add"/);
  // login panel keeps its CL-UI-61 semantics
  assert.match(remHtml, /id="rem-login-panel" hidden/);
});

test('CL-UI-90 (3) page renderer emits the mockup card markup + status classes', () => {
  assert.match(pageJs, /class="rem-card'\s*\+/);
  assert.match(pageJs, /class="rem-line1"/);
  assert.match(pageJs, /class="rem-subject-chip"/);
  assert.match(pageJs, /class="rem-line2"/);
  assert.match(pageJs, /class="rem-next rem-next-off"/); // paused → grey
  assert.match(pageJs, /class="rem-next rem-next-warn"/); // streak → amber
  assert.match(pageJs, /data-rem-toggle role="switch"/);
  assert.match(pageJs, /data-rem-edit/);
  assert.match(pageJs, /data-rem-delete/);
  assert.match(remHtml, /\.rem-next\{margin-left:auto;font-family:var\(--cl-mono\)/);
  assert.match(remHtml, /\.rem-next\.rem-next-warn\{color:var\(--cl-amber-text\)\}/);
});

test('CL-UI-90 (4) visual layer only — API contract untouched', () => {
  // endpoints identical to CL-UI-58/61 (page + client)
  assert.match(pageJs, /var RULES_ENDPOINT = '\/api\/v1\/notify\/rules';/);
  assert.match(pageJs, /var ME_ENDPOINT = '\/api\/v1\/auth\/me';/);
  assert.match(pageJs, /channel: 'push', minAdvanceHours: 24/);
  assert.match(pageJs, /method: 'PATCH'/);
  assert.match(pageJs, /method: 'DELETE'/);
  // no new API surface: no fetch() outside the four known endpoints
  const urls = [...pageJs.matchAll(/['"](\/api\/[^'"]+)['"]/g)].map(m => m[1]);
  assert.deepEqual([...new Set(urls)].sort(),
    ['/api/v1/auth/google/start', '/api/v1/auth/line/start', '/api/v1/auth/me', '/api/v1/notify/rules']);
  assert.doesNotMatch(clientJs, /CL-UI-90/); // client byte-untouched by this ticket
});

test('CL-UI-90 (5) next-trigger/streak derivation — pure helpers, no fabrication', () => {
  // dates are computed from the real clock so the fixture never goes stale
  const d = (offsetDays) => new Date(Date.now() + offsetDays * 86400000).toISOString().slice(0, 10);
  const place = {
    place_id: 'tw-001', timezone_display: { utc_offset_hours: 8 },
    opportunities: [{
      opportunity_id: 'tw-001-P01',
      days: [
        { local_date: d(-3), good_hours: [] },
        { local_date: d(-2), good_hours: [] },
        { local_date: d(-1), good_hours: [] },
        // d(2): always strictly future even in the UTC+8 spot frame
        // (local now ∈ [d(0) 08:00, d(1) 08:00)), so the fixture cannot race
        { local_date: d(2), good_hours: ['05:00', '06:00'] },
      ]
    }]
  };
  const h = loadHelpers();
  // trigger = first future good hour − advance hours (spot-local UTC framing)
  const now = Date.now();
  const next = h.findNextTrigger(place, 'tw-001-P01', 24, now);
  assert.ok(next, 'a future good hour exists');
  assert.equal(next.date, d(2));
  assert.equal(next.hour, '05:00');
  assert.match(next.label, /^\d{2}\/\d{2} \d{2}:\d{2}$/);
  const want = new Date(Date.parse(d(2) + 'T05:00:00Z') - 24 * 3600000);
  const p2 = (n) => (n < 10 ? '0' : '') + n;
  assert.equal(next.label, `${p2(want.getUTCMonth() + 1)}/${p2(want.getUTCDate())} ${p2(want.getUTCHours())}:${p2(want.getUTCMinutes())}`);
  // past hours are never picked
  const past = h.findNextTrigger(place, 'tw-001-P01', 24, Date.parse(d(3) + 'T00:00:00Z'));
  assert.equal(past, null);
  // streak counts consecutive unfit days up to today
  assert.equal(h.unfitStreak(place, 'tw-001-P01', now), 3);
  assert.equal(h.unfitStreak({ ...place, opportunities: [{ opportunity_id: 'tw-001-P01', days: [] }] }, 'tw-001-P01', now), 0);
  // status HTML: paused grey, streak amber (>=3 unfit days, no next window),
  // next green, honest fallback
  const state = h.state;
  state.catalog = [place];
  assert.match(h.nextStatusHtml({ enabled: 0, place_id: 'tw-001', opportunity_id: 'tw-001-P01', min_advance_hours: 24 }), /rem-next-off/);
  const unfitOnly = { ...place, opportunities: [{ opportunity_id: 'tw-001-P01',
    days: [d(-3), d(-2), d(-1)].map(x => ({ local_date: x, good_hours: [] })) }] };
  state.catalog = [unfitOnly];
  assert.match(h.nextStatusHtml({ enabled: 1, place_id: 'tw-001', opportunity_id: 'tw-001-P01', min_advance_hours: 24 }), /rem-next-warn/);
  const fitPlace = { ...place, opportunities: [{ opportunity_id: 'tw-001-P01', days: [{ local_date: d(2), good_hours: ['06:00'] }] }] };
  state.catalog = [fitPlace];
  const green = h.nextStatusHtml({ enabled: 1, place_id: 'tw-001', opportunity_id: 'tw-001-P01', min_advance_hours: 24 });
  assert.match(green, /class="rem-next"/);
  assert.match(green, /下次觸發/);
  const noData = { ...place, opportunities: [{ opportunity_id: 'tw-001-P01', days: [{ local_date: d(-5), good_hours: [] }] }] };
  state.catalog = [noData];
  assert.match(h.nextStatusHtml({ enabled: 1, place_id: 'tw-001', opportunity_id: 'tw-001-P01', min_advance_hours: 24 }), /近期無符合時段/);
});

// vm-load the page IIFE and expose only the pure helpers (DOM stubs).
function loadHelpers() {
  const elements = new Map();
  function el(id) {
    if (!elements.has(id)) elements.set(id, { id, hidden: false, innerHTML: '', textContent: '', value: '', checked: false,
      addEventListener() {}, setAttribute() {}, getAttribute: () => null, placeholder: '', disabled: false, scrollIntoView() {} });
    return elements.get(id);
  }
  const document = {
    readyState: 'complete', getElementById: el,
    querySelector: () => null, querySelectorAll: () => [],
    documentElement: {}, addEventListener() {}, body: { appendChild() {} },
    createElement: () => ({ style: {}, setAttribute() {}, classList: {} })
  };
  const sandbox = { document, localStorage: { getItem: () => null, setItem() {} },
    fetch: () => Promise.resolve({ ok: false, status: 401, json: () => Promise.resolve({}) }),
    Promise, setTimeout, clearTimeout, MutationObserver: undefined, scrollTo() {} };
  sandbox.window = sandbox;
  new Function('window', 'document', 'localStorage', 'fetch', 'Promise', 'setTimeout', 'clearTimeout', 'MutationObserver',
    pageJs)(sandbox.window, document, sandbox.localStorage, sandbox.fetch, Promise, setTimeout, clearTimeout, undefined);
  const pg = sandbox.window.ChaseLightsRemindersPage;
  pg.state.lang = 'zh-TW';
  return pg;
}

test('CL-UI-90 (6) trilingual copy for every new key (no internal wording)', () => {
  const keys = ['rem_next_label:', 'rem_paused_next:', 'rem_streak:', 'rem_no_window:',
    'rem_preview_first:', 'rem_preview_unknown:', 'rem_found:', 'rem_empty_t:',
    'rem_empty_d:', 'rem_empty_a:', 'rem_edit:', 'rem_active_count:', 'rem_flow_hint:'];
  for (const langTag of ["'zh-TW'", "'en'", "'ja'"]) {
    const block = pageJs.slice(pageJs.indexOf(langTag), pageJs.indexOf(langTag) + 2600);
    for (const key of keys) assert.ok(block.includes(key), `page ${langTag} ${key}`);
  }
  const copyText = pageJs.slice(pageJs.indexOf('var I18N'), pageJs.indexOf('function lang()'));
  assert.doesNotMatch(copyText, /provisional|draft|internal/i);
});

test('CL-UI-90 (7) token discipline — zero hardcoded colors in the page styles', () => {
  const style = remHtml.slice(remHtml.indexOf('<style>'), remHtml.indexOf('</style>')).replace(/\/\*[\s\S]*?\*\//g, '');
  assert.equal((style.match(/#[0-9A-Fa-f]{3,8}\b/g) || []).length, 0, 'hex colors in page styles');
  assert.equal((style.match(/rgba?\(/g) || []).length, 0, 'rgba() in page styles');
  // tokens used verbatim from the live app.css :root layer
  for (const tok of ['--cl-bg-1', '--cl-border', '--cl-border-strong', '--cl-text-1', '--cl-text-3',
    '--cl-green-text', '--cl-amber-text', '--cl-grey-text', '--cl-red-border', '--cl-red-text', '--cl-red-bg',
    '--cl-r-md', '--cl-r-sm', '--cl-r-xs', '--cl-sp-2', '--cl-sp-3', '--cl-sp-4', '--cl-sp-5', '--cl-sp-6',
    '--cl-fs-12', '--cl-fs-13', '--cl-fs-14', '--cl-fs-20', '--cl-control-h', '--cl-chip-h', '--cl-btn-h',
    '--cl-mono']) {
    assert.ok(style.includes(`var(${tok})`), `page styles use ${tok}`);
  }
  // cache-bust bump is scoped to the reminders page
  assert.match(remHtml, /assets\/reminders-page\.js\?v=clui90/);
  assert.doesNotMatch(remHtml, /reminders-page\.js\?v=clui75/);
  assert.match(remHtml, /assets\/site-nav\.css\?v=clui62/);
  assert.match(remHtml, /assets\/app\.css\?v=clui97/);
});

// ---- (8) headless 1280/390 screenshots vs mockup (raw CDP, no playwright) --
const BROWSER = process.env.CHROMIUM_EXECUTABLE || 'C:/Program Files/Google/Chrome/Application/chrome.exe';

test('CL-UI-90 (8) headless 1280/390 — cards render the mockup anatomy live', { timeout: 120000 }, async () => {
  let http, path;
  try { http = await import('node:http'); path = await import('node:path'); } catch (e) { throw e; }
  // stub API routes; static-serve the real page + real assets + real bundle
  const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.ico': 'image/x-icon' };
  const rulePlace = bundle.places.find(p => p.place_id === 'tw-001');
  const ruleOpp = rulePlace.opportunities[0].opportunity_id;
  const server = http.createServer((req, res) => {
    const url = req.url.split('?')[0];
    const send = (code, body, type) => { res.writeHead(code, { 'content-type': type }); res.end(body); };
    if (url === '/api/v1/auth/me') return send(200, JSON.stringify({ ok: true }), 'application/json');
    if (url === '/api/v1/notify/rules') return send(200, JSON.stringify({
      rules: [
        { id: 'r1', place_id: 'tw-001', opportunity_id: ruleOpp, channel: 'push', min_advance_hours: 24, enabled: 1 },
        { id: 'r2', place_id: 'tw-001', opportunity_id: ruleOpp, channel: 'push', min_advance_hours: 24, enabled: 0 }
      ]
    }), 'application/json');
    let file = url === '/' ? 'reminders.html' : url.replace(/^\//, '');
    try {
      const body = readFileSync(join(ROOT, file));
      return send(200, body, MIME[path.extname(file)] || 'application/octet-stream');
    } catch (e) { return send(404, 'not found', 'text/plain'); }
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const baseURL = `http://127.0.0.1:${server.address().port}/`;
  const chrome = spawn(BROWSER, [
    '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
    '--no-first-run', '--remote-debugging-port=0', '--window-size=1280,900',
    '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui90-')), 'about:blank'],
    { stdio: ['ignore', 'ignore', 'pipe'] });
  let ws = null, send = null, evaljs = null;
  const pending = new Map(); let nextId = 1;
  try {
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = ''; // event-loop-aware wait: with --test-isolation=none these hooks run while later
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
      const i = nextId++; pending.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
      ws.send(JSON.stringify({ id: i, method, params }));
    });
    evaljs = async (expr) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
      return r.result?.result?.value ?? r.result?.value;
    };
    await send('Page.enable');
    const PROBE = `(() => {
      const cards = [...document.querySelectorAll('.rem-card')];
      const first = cards[0];
      if (!first) return { error: 'no cards' };
      const next = first.querySelector('.rem-next');
      const cs = next ? getComputedStyle(next) : null;
      return {
        cards: cards.length,
        chips: [...first.querySelectorAll('.rem-subject-chip')].map(x => x.textContent),
        place: first.querySelector('.rem-place')?.textContent || null,
        nextClass: next?.className || null,
        nextMono: cs ? cs.fontFamily.includes('mono') || cs.fontFamily.includes('Consolas') || cs.fontFamily.includes('SF Mono') : false,
        switchOn: !!first.querySelector('.rem-switch.rem-on'),
        offCard: !!document.querySelector('.rem-card.rem-off'),
        previewShown: !document.getElementById('rem-preview').hidden,
        count: document.getElementById('rem-count').textContent,
        actsBtns: [...first.querySelectorAll('.rem-acts button')].map(b => b.className),
        regionFlow: !!document.querySelector('.rem-add-flow .rem-arrow'),
      };
    })()`;
    for (const vp of [{ name: 'desktop 1280px', w: 1280, h: 900, mobile: false, shot: 'clui90-desktop' },
                      { name: 'mobile 390px', w: 390, h: 844, mobile: true, shot: 'clui90-390px' }]) {
      await send('Emulation.setDeviceMetricsOverride', { width: vp.w, height: vp.h, deviceScaleFactor: 1, mobile: vp.mobile });
      await send('Page.navigate', { url: baseURL });
      await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
      // under full-suite load the catalog fetch can trail the load event —
      // poll for the settled render instead of a fixed sleep
      await evaljs(`new Promise(r=>{const t0=Date.now();const t=setInterval(()=>{
        if(!document.getElementById('rem-preview').hidden||Date.now()-t0>8000){clearInterval(t);r(1)}},100)})`);
      const probe = await evaljs(PROBE);
      assert.equal(probe.error, undefined, 'cards rendered');
      assert.equal(probe.cards, 2, 'two seeded rules render as two cards');
      assert.ok(probe.place, 'place name on line 1');
      assert.ok(probe.chips.length >= 1, 'subject chip on line 1');
      assert.equal(probe.nextMono, true, 'next-trigger renders in the mono face');
      assert.match(probe.nextClass, /rem-next/);
      assert.equal(probe.switchOn, true, 'enabled rule shows the on-switch');
      assert.equal(probe.offCard, true, 'paused rule dims via rem-off');
      assert.equal(probe.previewShown, true, 'add preview row visible with a picked place');
      assert.ok(probe.count.length > 0, 'count line filled');
      assert.equal(probe.regionFlow, true, 'three-tier flow arrows present');
      assert.ok(probe.actsBtns.some(c => c.includes('rem-switch')), 'switch in action column');
      assert.ok(probe.actsBtns.some(c => c.includes('rem-edit-btn')), 'edit in action column');
      assert.ok(probe.actsBtns.some(c => c.includes('rem-del')), 'delete in action column');
      const shot = await send('Page.captureScreenshot', { format: 'png' });
      const fs = await import('node:fs');
      const out = join(here, '..', 'audits', 'design-mockups', vp.shot + '.png');
      fs.mkdirSync(path.dirname(out), { recursive: true });
      fs.writeFileSync(out, Buffer.from(shot.data, 'base64'));
      console.log(vp.shot + ' probe: ' + JSON.stringify(probe) + ' → ' + out);
    }
  } finally {
    try { ws?.close(); } catch {}
    chrome.kill();
    await new Promise(r => server.close(r));
  }
});
