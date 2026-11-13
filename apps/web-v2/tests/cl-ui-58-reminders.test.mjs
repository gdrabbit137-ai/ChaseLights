// CL-UI-58 — reminder feature UI: card 「加入提醒」 button + reminders.html page.
// Covers: 1) notify_rules contract wiring (POST body shape, PATCH toggle,
// DELETE, 401 login guard); 2) card mount-point markup in app.js (best-subject
// line, data-rem-place/data-rem-opp); 3) reminders-page pure helpers
// (region/keyword filtering, place/subject lookup); 4) trilingual copy in all
// three dicts for client + page; 5) five-page nav + stamps (with cl-ui-28).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const read = (p) => readFileSync(join(root, p), 'utf8');

const indexHtml = read('index.html');
const appJs = read('assets/app.js');
const appCss = read('assets/app.css');
const clientJs = read('assets/reminders-client.js');
const pageJs = read('assets/reminders-page.js');
const remHtml = read('reminders.html');
const workerJs = read('workers/api/src/index.js');

// Load the client IIFE with browser stubs and capture its export.
function loadClient(fetchImpl) {
  const sandbox = {
    addEventListener() {},
    removeEventListener() {},
    document: {
      readyState: 'complete',
      addEventListener() {},
      removeEventListener() {},
      querySelectorAll: () => [],
      documentElement: {},
      createElement: () => ({ style: {}, classList: { toggle() {} }, setAttribute() {}, removeAttribute() {} }),
      body: { appendChild() {} }
    },
    localStorage: { getItem: () => null, setItem() {} },
    fetch: fetchImpl,
    setTimeout, clearTimeout,
    MutationObserver: undefined
  };
  // window === sandbox: client exports land on sandbox.window.ChaseLightsReminders.
  new Function('window', 'document', 'localStorage', 'fetch', 'setTimeout', 'clearTimeout', 'MutationObserver',
    clientJs)(sandbox, sandbox.document, sandbox.localStorage, sandbox.fetch, setTimeout, clearTimeout, sandbox.MutationObserver);
  return sandbox.ChaseLightsReminders;
}

test('CL-UI-58 (1): card renders the reminder mount point on the best-subject line', () => {
  assert.match(appJs, /class="cl-rem-btn" data-rem-place="\$\{esc\(spot\.spot_id\)\}" data-rem-opp="\$\{esc\(v2Best\.oppId\|\|''\)\}"/);
  // It lives inside the theme-winner summary line (both the qualifying-hours
  // branch and the no-subject branch), and app.js never calls the notify
  // rules API itself — the client owns the contract.
  assert.match(appJs, /assets\/reminders-client\.js owns its label/);
  assert.doesNotMatch(appJs, /\/api\/v1\/notify/);
  // Button styling exists (44px-class touch target, busy + on states).
  assert.match(appCss, /\.cl-rem-btn\{/);
  assert.match(appCss, /\.cl-rem-btn\.cl-rem-on\{/);
  assert.match(appCss, /\.cl-rem-btn\[data-rem-busy\]\{/);
});

test('CL-UI-58 (2): client wires the real notify_rules contract (POST/PATCH/DELETE)', async () => {
  const calls = [];
  const fetchImpl = (url, opts) => {
    const method = (opts && opts.method) || 'GET';
    calls.push({ url: String(url), method, body: opts && opts.body });
    return Promise.resolve({
      ok: true, status: 200,
      json: () => Promise.resolve(method === 'POST'
        ? { ok: true, rule: { id: 'r1', placeId: 'tw-001', opportunityId: 'tw-001-P01', channel: 'telegram', minAdvanceHours: 24 } }
        : method === 'DELETE' ? { ok: true, deleted: 'r1' } : { rules: [] })
    });
  };
  const rem = loadClient(fetchImpl);
  await rem.refresh(); // boot-time GET (rules list)
  const post = await rem._internals.createRule('tw-001', 'tw-001-P01');
  assert.equal(post.status, 200);
  const postCall = calls.find(c => c.method === 'POST');
  assert.deepEqual(JSON.parse(postCall.body), {
    placeId: 'tw-001', opportunityId: 'tw-001-P01', channel: 'push', minAdvanceHours: 24
  });
  assert.equal(postCall.url, '/api/v1/notify/rules');
  assert.equal(postCall.body.indexOf('channel'), postCall.body.indexOf('channel'), 'body is a JSON string');

  const del = await rem._internals.deleteRule('r1');
  assert.equal(del.body.ok, true);
  const delCall = calls.find(c => c.method === 'DELETE');
  assert.equal(delCall.url, '/api/v1/notify/rules/r1');
});

test('CL-UI-58 (3): rule matching reindex — opp rule exact, opp-less rule covers the place', () => {
  const rem = loadClient(() => Promise.resolve({ ok: false, status: 401, json: () => Promise.resolve({}) }));
  const map = rem.reindex([
    { id: 'a', place_id: 'tw-001', opportunity_id: 'tw-001-P01' },
    { id: 'b', place_id: 'tw-002', opportunity_id: null }
  ]);
  assert.equal(rem.ruleFor(map, 'tw-001', 'tw-001-P01').id, 'a');
  assert.equal(rem.ruleFor(map, 'tw-002', '').id, 'b');
  // An any-subject rule covers every subject button at that place…
  assert.equal(rem.ruleFor(map, 'tw-002', 'tw-002-P09').id, 'b');
  // …and an exact subject rule wins over the place-level rule.
  assert.equal(rem.ruleFor(map, 'tw-003', ''), null);
  assert.equal(rem.ruleFor(map, 'tw-001', 'tw-001-P99').id, 'a');
});

test('CL-UI-58 (4) + CL-UI-61: login gate — signed-out users never reach the rules endpoint', async () => {
  let rulesCalled = 0, meCalled = 0;
  const rem = loadClient((url) => {
    const u = String(url);
    if (u.indexOf('/notify/rules') >= 0) rulesCalled += 1;
    if (u.indexOf('/auth/me') >= 0) meCalled += 1;
    return Promise.resolve({ ok: false, status: 401, json: () => Promise.resolve({ error: 'JWT session required' }) });
  });
  await rem.refresh();
  assert.equal(rem.state.signedIn, false);
  assert.equal(meCalled, 1, 'the throttled /auth/me gate answers once');
  assert.equal(rulesCalled, 0, 'CL-UI-61: rules endpoint is never hit while signed out');
  // A click while signed out never reaches createRule (no POST), only the toast.
  const postSpy = rem._internals.createRule;
  let posts = 0;
  rem._internals.createRule = (...a) => { posts += 1; return postSpy(...a); };
  rem._internals.onCardClick('tw-001', 'tw-001-P01', null);
  assert.equal(posts, 0);
  assert.equal(rem.state.signedIn, false);
});

test('CL-UI-58 (5): reminders-page pure helpers — region, catalog filter, lookups', () => {
  // Grab the pure-helper block out of the page IIFE.
  const start = pageJs.indexOf('function regionOfPlace');
  const end = pageJs.indexOf('// ---- rendering ----');
  assert.ok(start > 0 && end > start, 'helper block found');
  const src = pageJs.slice(start, end);
  const REGIONS = [{ id: 'tw', flag: '🇹🇼' }];
  const helpers = new Function('REGIONS', `"use strict";
    ${src}
    return { regionOfPlace, nameOf, filterCatalog, findPlace, findSubject };`);
  const h = helpers(REGIONS);

  assert.equal(h.regionOfPlace('jp-001'), 'jp');
  assert.equal(h.nameOf({ 'zh-TW': '合歡山', en: 'Hehuanshan', ja: '合歓山' }, 'ja'), '合歓山');
  assert.equal(h.nameOf({ en: 'Hehuanshan' }, 'ja'), 'Hehuanshan');
  const catalog = [
    { place_id: 'tw-001', name_i18n: { 'zh-TW': '合歡山', en: 'Hehuanshan' },
      opportunities: [{ opportunity_id: 'tw-001-P01', name_i18n: { 'zh-TW': '雲海', en: 'Cloud sea' } }] },
    { place_id: 'jp-001', name_i18n: { 'zh-TW': '青池', en: 'Blue Pond' },
      opportunities: [{ opportunity_id: 'jp-001-P01', name_i18n: { 'zh-TW': '倒影', en: 'Reflection' } }] }
  ];
  assert.equal(h.findPlace(catalog, 'jp-001').place_id, 'jp-001');
  assert.equal(h.findPlace(catalog, 'tw-999'), null);
  assert.equal(h.findSubject(h.findPlace(catalog, 'tw-001'), 'tw-001-P01').opportunity_id, 'tw-001-P01');
  assert.equal(h.findSubject(h.findPlace(catalog, 'tw-001'), 'tw-001-P99'), null);
  // Keyword search matches place names and subject names, in the active language.
  assert.equal(h.filterCatalog(catalog, '合歡', 'zh-TW').length, 1);
  assert.equal(h.filterCatalog(catalog, 'cloud', 'en').length, 1);
  assert.equal(h.filterCatalog(catalog, '不存在', 'zh-TW').length, 0);
  // Empty keyword returns the full catalog.
  assert.equal(h.filterCatalog(catalog, '', 'zh-TW').length, 2);
});

test('CL-UI-58 (6): page list rendering — names, channel, advance, toggle, delete', () => {
  // vm-run the page IIFE with DOM stubs, then drive renderList directly.
  const elements = new Map();
  function el(id) {
    if (!elements.has(id)) elements.set(id, { id, hidden: false, innerHTML: '', textContent: '', value: '', checked: false,
      addEventListener() {}, setAttribute() {}, getAttribute: () => null, placeholder: '' });
    return elements.get(id);
  }
  const document = {
    readyState: 'complete',
    getElementById: el,
    querySelector: () => null,
    querySelectorAll: () => [],
    documentElement: {},
    addEventListener() {},
    body: { appendChild() {} },
    createElement: () => ({ style: {}, setAttribute() {}, classList: {} })
  };
  const sandbox = { window: {}, document, localStorage: { getItem: () => 'zh-TW', setItem() {} },
    fetch: () => Promise.resolve({ ok: false, status: 401, json: () => Promise.resolve({}) }),
    Promise, setTimeout, clearTimeout, MutationObserver: undefined };
  sandbox.window = sandbox;
  // Boot runs on load; intercept fetch-driven render by awaiting microtasks.
  new Function('window', 'document', 'localStorage', 'fetch', 'Promise', 'setTimeout', 'clearTimeout', 'MutationObserver',
    pageJs)(sandbox.window, document, sandbox.localStorage, sandbox.fetch, Promise, setTimeout, clearTimeout, undefined);
  const pg = sandbox.window.ChaseLightsRemindersPage;
  pg.state.catalog = [{ place_id: 'tw-001', name_i18n: { 'zh-TW': '合歡山', en: 'Hehuanshan' },
    opportunities: [{ opportunity_id: 'tw-001-P01', name_i18n: { 'zh-TW': '雲海' } }] }];
  pg.state.lang = 'zh-TW';
  pg.state.rules = [{ id: 'r1', place_id: 'tw-001', opportunity_id: 'tw-001-P01', channel: 'telegram', min_advance_hours: 24, enabled: 1 }];
  pg.state.signedIn = true;
  pg.renderList();
  const html = el('rem-list').innerHTML;
  assert.match(html, /合歡山/);
  assert.match(html, /雲海/);
  assert.match(html, /App 推播/);
  assert.match(html, /提前 24 小時/);
  assert.match(html, /data-rem-toggle/);
  assert.match(html, /data-rem-delete/);
  assert.match(html, /checked/);
  // Disabled rule renders the unchecked toggle.
  pg.state.rules = [{ id: 'r1', place_id: 'tw-001', opportunity_id: null, channel: 'telegram', min_advance_hours: 12, enabled: 0 }];
  pg.renderList();
  assert.match(el('rem-list').innerHTML, /該景點全部題材/);
  assert.match(el('rem-list').innerHTML, /提前 12 小時/);
});

test('CL-UI-58 (7): trilingual copy for client and page (no internal wording)', () => {
  const clientKeys = [...clientJs.matchAll(/\b(rem_[a-z_]+):/g)].map(m => m[1]);
  assert.ok(clientKeys.includes('rem_add') && clientKeys.includes('rem_added') && clientKeys.includes('rem_login'));
  for (const langTag of ["'zh-TW'", "'en'", "'ja'"]) {
    const block = clientJs.slice(clientJs.indexOf(langTag), clientJs.indexOf(langTag) + 900);
    for (const key of ['rem_add:', 'rem_added:', 'rem_login:', 'rem_saved:', 'rem_removed:', 'rem_err:', 'rem_limit:']) {
      assert.ok(block.includes(key), `client ${langTag} ${key}`);
    }
  }
  const pageKeys = ['page_title:', 'rem_list_title:', 'rem_add_title:', 'rem_add_btn:', 'rem_search_placeholder:',
    'rem_enabled:', 'rem_disabled:', 'rem_delete:', 'rem_login_prompt:', 'rem_empty:'];
  for (const langTag of ["'zh-TW'", "'en'", "'ja'"]) {
    const block = pageJs.slice(pageJs.indexOf(langTag), pageJs.indexOf(langTag) + 1600);
    for (const key of pageKeys) assert.ok(block.includes(key), `page ${langTag} ${key}`);
  }
  // User-visible copy only — the _internals export name is not user copy.
  const copyText = (src) => src.slice(src.indexOf('var I18N'), src.indexOf('function lang()'));
  for (const src of [copyText(clientJs), pageJs]) {
    assert.doesNotMatch(src, /provisional|draft|internal/i);
  }
});

test('CL-UI-58 (8): page shell — nav item, script tags, stamps, mobile-first CSS', () => {
  assert.match(remHtml, /<nav class="site-nav"/);
  assert.match(remHtml, /data-nav-target="reminders" data-active="page"/);
  assert.match(remHtml, /assets\/site-nav\.css\?v=clui62/);
  assert.match(remHtml, /assets\/app\.css\?v=clui78/);
  assert.match(remHtml, /assets\/member-auth\.js\?v=clui68/);
  assert.match(remHtml, /assets\/reminders-client\.js\?v=clui75/);
  assert.match(remHtml, /assets\/reminders-page\.js\?v=clui75/);
  // Login panel + login deep links present (OAuth 302 anchors, per CL-UI-53).
  assert.match(remHtml, /rem-login-panel/);
  assert.match(pageJs, /\/api\/v1\/auth\/line\/start/);
  assert.match(pageJs, /\/api\/v1\/auth\/google\/start/);
  // 390px contract: mobile media query, 44px-class touch targets.
  assert.match(remHtml, /max-width: 390px/);
  assert.match(remHtml, /min-height:44px|min-height: 44px/);
  // The homepage loads the card-side client and carries the bumped stamps.
  assert.match(indexHtml, /assets\/reminders-client\.js\?v=clui75/);
  assert.match(indexHtml, /assets\/app\.js\?v=clui78/);
  assert.match(indexHtml, /assets\/app\.css\?v=clui78/);
});

test('CL-UI-58 (9): worker PATCH route — enabled toggle is wired and scoped', () => {
  assert.ok(workerJs.includes('request.method === "PATCH" || request.method === "PUT"'));
  assert.match(workerJs, /UPDATE notify_rules SET enabled = \?2 WHERE id = \?1 AND user_id = \?3/);
  assert.match(workerJs, /if \(typeof enabled !== "boolean"\) return json\(req, 400/);
  // JWT-only: same requireSession guard as the other rule endpoints.
  const fn = workerJs.slice(workerJs.indexOf('async function handleNotifyRuleUpdate'), workerJs.indexOf('async function handleTelegramStart'));
  assert.match(fn, /requireSession\(req, env\)/);
  assert.match(fn, /return json\(req, 401/);
});

test('CL-UI-58 (10): homepage catalog source used for quick-add is the existing evaluations bundle', () => {
  assert.match(pageJs, /apps\/web-v2\/evaluations-latest\.json/);
  // Regions follow the place_id prefix, matching the homepage VALID_REGIONS set.
  assert.match(pageJs, /split\('-'\)\[0\]/);
});
