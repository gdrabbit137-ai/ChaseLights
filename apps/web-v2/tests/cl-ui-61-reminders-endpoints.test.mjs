// CL-UI-61 — reminders endpoint path fix + login-state integration.
// Root cause: reminders-page.js / reminders-client.js called /api/v1/notify_rules,
// but the worker's real routes (workers/api/src/index.js) are /api/v1/notify/rules
// (list/create) and /api/v1/notify/rules/<id> (PATCH/PUT/DELETE) — the old spelling
// 404'd every reminder action (manager live repro).
// Covers: 1) worker route wiring (source assertions); 2) no /notify_rules leftovers
// in any frontend asset; 3) a mock server mirroring the WORKER's real routes
// (same method set, status codes and body shapes) driving the real client + page
// IIFEs through GET/POST/PATCH/DELETE end to end; 4) the /auth/me login gate with
// its throttle window — signed-out users never reach the rules endpoint, the
// throttle reuses one /auth/me answer, and a forced refresh bypasses it.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import http from 'node:http';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const read = (p) => readFileSync(join(root, p), 'utf8');

const clientJs = read('assets/reminders-client.js');
const pageJs = read('assets/reminders-page.js');
const workerJs = read('workers/api/src/index.js');

// ---------------------------------------------------------------------------
// (1) Worker routes: the /api/v1 base plus /notify/rules + /notify/rules/<id>.
// ---------------------------------------------------------------------------
test('CL-UI-61 (1): worker serves notify rules at /notify/rules and /notify/rules/<id> under the /api/v1 base', () => {
  assert.match(workerJs, /const base = url\.origin \+ "\/api\/v1";/);
  assert.match(workerJs, /path === "\/notify\/rules"\) return handleNotifyRules/);
  assert.ok(
    workerJs.includes('const dm = path.match(/^'),
    'single-rule route matcher /notify/rules/<id> exists'
  );
  // Evaluate the worker's EXACT matcher and confirm it accepts real rule ids.
  const dmLine = workerJs.split('\n').find((l) => l.trim().startsWith('const dm = path.match('));
  assert.ok(dmLine, 'dm matcher line found');
  const re = new RegExp(dmLine.slice(dmLine.indexOf('/^') + 1, dmLine.lastIndexOf('/);')));
  assert.ok(re.test('/notify/rules/AbC-12_3'), 'matcher accepts worker-style rule ids');
  assert.ok(!re.test('/notify/rules/'), 'matcher rejects the bare list route');
  assert.ok(workerJs.includes('"DELETE") return handleNotifyRuleDelete(request, env, dm[1]);'));
  assert.ok(workerJs.includes('"PATCH" || request.method === "PUT")) return handleNotifyRuleUpdate(request, env, dm[1]);'));
});

// ---------------------------------------------------------------------------
// (2) Frontend spellings: every endpoint call uses the real route.
// ---------------------------------------------------------------------------
test('CL-UI-61 (2): reminders client + page call /api/v1/notify/rules; no /notify_rules leftovers in assets', () => {
  assert.match(clientJs, /var RULES_ENDPOINT = '\/api\/v1\/notify\/rules';/);
  assert.match(pageJs, /var RULES_ENDPOINT = '\/api\/v1\/notify\/rules';/);
  for (const f of readdirSync(join(root, 'assets')).filter((n) => n.endsWith('.js'))) {
    const src = read('assets/' + f);
    assert.doesNotMatch(src, /\/api\/v1\/notify_rules/, `${f} still calls the 404 route /api/v1/notify_rules`);
  }
  // The single-rule calls go through the endpoint + encodeURIComponent(id).
  assert.match(clientJs, /RULES_ENDPOINT \+ '\/' \+ encodeURIComponent\(ruleId\)/);
  assert.match(pageJs, /RULES_ENDPOINT \+ '\/' \+ encodeURIComponent\(id\)/);
});

// ---------------------------------------------------------------------------
// Mock server mirroring the worker's REAL routes (method set, statuses, bodies
// follow workers/api/src/index.js handleNotifyRules / handleNotifyRuleUpdate /
// handleNotifyRuleDelete / handleAuthMe).
// ---------------------------------------------------------------------------
function startMockServer(opts) {
  const state = { authed: !!(opts && opts.authed), rules: [], nextId: 1, limit: (opts && opts.limit) || 3, meHits: 0 };
  const log = [];
  const server = http.createServer((req, res) => {
    let raw = '';
    req.on('data', (c) => { raw += c; });
    req.on('end', () => {
      const path = new URL(req.url, 'http://x').pathname;
      const method = req.method;
      log.push(method + ' ' + path);
      const json = (status, body) => {
        res.writeHead(status, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(body));
      };
      const parse = () => { try { return JSON.parse(raw || '{}'); } catch { return {}; } };
      if (path === '/api/v1/auth/me' && method === 'GET') {
        state.meHits += 1;
        return state.authed ? json(200, { user: { displayName: 'Tester' } }) : json(401, { error: 'JWT session required' });
      }
      if (path === '/api/v1/notify/rules') {
        if (!state.authed) return json(401, { error: 'JWT session required' });
        if (method === 'GET') return json(200, { userId: 'u1', level: 'free', rules: state.rules });
        if (method === 'POST') {
          const body = parse();
          if (!body.placeId) return json(400, { error: 'placeId required' });
          if (state.rules.length >= state.limit) return json(402, { error: 'notify rule limit reached — upgrade to paid for more', level: 'free', limit: state.limit, count: state.rules.length });
          const rule = { id: 'r' + (state.nextId++), place_id: body.placeId, opportunity_id: body.opportunityId || null, channel: body.channel || 'push', min_advance_hours: body.minAdvanceHours != null ? body.minAdvanceHours : 24, enabled: 1, created_at: '2026-11-13T00:00:00Z' };
          state.rules.push(rule);
          return json(200, { ok: true, rule: { id: rule.id, placeId: rule.place_id, opportunityId: rule.opportunity_id, channel: rule.channel, minAdvanceHours: rule.min_advance_hours }, count: state.rules.length, limit: state.limit });
        }
        return json(405, { error: 'method not allowed' });
      }
      const dm = path.match(/^\/api\/v1\/notify\/rules\/([\w-]+)$/);
      if (dm) {
        if (!state.authed) return json(401, { error: 'JWT session required' });
        const rule = state.rules.find((r) => r.id === dm[1]);
        if (method === 'PATCH' || method === 'PUT') {
          const body = parse();
          if (typeof body.enabled !== 'boolean') return json(400, { error: 'enabled boolean required' });
          if (!rule) return json(404, { error: 'rule not found' });
          rule.enabled = body.enabled ? 1 : 0;
          return json(200, { ok: true, rule: { id: rule.id, enabled: body.enabled } });
        }
        if (method === 'DELETE') {
          if (!rule) return json(404, { error: 'rule not found' });
          state.rules = state.rules.filter((r) => r.id !== dm[1]);
          return json(200, { ok: true, deleted: dm[1] });
        }
        return json(405, { error: 'method not allowed' });
      }
      // The catalog the quick-add picker reads (same route the page requests).
      if (path === '/apps/web-v2/evaluations-latest.json' && method === 'GET') {
        return json(200, { places: [{ place_id: 'tw-001', name_i18n: { 'zh-TW': '測試景點', en: 'Test Place', ja: 'テストスポット' }, opportunities: [{ opportunity_id: 'tw-001-P01', name_i18n: { 'zh-TW': '雲海', en: 'Cloud sea', ja: '雲海' } }] }] });
      }
      return json(404, { error: 'not found' });
    });
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve({ server, state, log })));
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function waitFor(cond, ms = 5000) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    if (cond()) return true;
    await sleep(25);
  }
  return false;
}

// Relative URLs → the mock server base (only /api/… and ./apps/… are proxied).
function makeFetch(base) {
  return (url, opts) => {
    const u = String(url);
    if (u.indexOf('/api/') === 0 || u.indexOf('./apps/') === 0) {
      const path = u.replace(/^\.\/apps\//, '/apps/');
      return fetch(base + path, opts);
    }
    return Promise.resolve({ ok: false, status: 400, json: () => Promise.resolve({}) });
  };
}

// Load the client IIFE exactly like cl-ui-58 does (window === sandbox).
function loadClientInto(sandbox, fetchImpl) {
  new Function('window', 'document', 'localStorage', 'fetch', 'setTimeout', 'clearTimeout', 'MutationObserver',
    clientJs)(sandbox, sandbox.document, sandbox.localStorage, fetchImpl, setTimeout, clearTimeout, sandbox.MutationObserver);
  return sandbox.ChaseLightsReminders;
}

// The page IIFE needs the id-stub document (cl-ui-58 (6) pattern) with
// addEventListener capture so the test can drive the real event wiring.
function makePageSandbox(fetchImpl) {
  const elements = new Map();
  const el = (id) => {
    if (!elements.has(id)) {
      const handlers = {};
      elements.set(id, {
        id, hidden: false, innerHTML: '', textContent: '', value: '', checked: false, placeholder: '', disabled: false,
        addEventListener(type, fn) { (handlers[type] = handlers[type] || []).push(fn); },
        setAttribute() {}, getAttribute: () => null, _handlers: handlers
      });
    }
    return elements.get(id);
  };
  const document = {
    readyState: 'complete',
    getElementById: el,
    querySelector: () => null,
    querySelectorAll: () => [],
    documentElement: { lang: '' },
    addEventListener() {},
    body: { appendChild() {} },
    createElement: () => ({ style: {}, setAttribute() {}, classList: {} })
  };
  const sandbox = {
    addEventListener() {}, removeEventListener() {},
    document, localStorage: { getItem: () => 'zh-TW', setItem() {} },
    fetch: fetchImpl, Promise, setTimeout, clearTimeout, MutationObserver: undefined
  };
  sandbox.window = sandbox;
  return { sandbox, el };
}

async function withServer(opts, fn) {
  const { server, state, log } = await startMockServer(opts);
  try {
    const base = 'http://127.0.0.1:' + server.address().port;
    return await fn({ base, state, log });
  } finally {
    await new Promise((r) => server.close(r));
  }
}

// ---------------------------------------------------------------------------
// (3) Full flow against the worker-real routes through the real client IIFE.
// ---------------------------------------------------------------------------
test('CL-UI-61 (3): client end-to-end on the real routes — GET list, POST create, DELETE, 402 cap, 404 unknown', async () => {
  await withServer({ authed: true }, async ({ base, log }) => {
    const rem = loadClientInto(makePageSandbox(makeFetch(base)).sandbox, makeFetch(base));
    await rem.refresh();
    assert.equal(rem.state.signedIn, true);
    assert.ok(log.includes('GET /api/v1/notify/rules'), 'boot fetched the real list route');

    const post = await rem._internals.createRule('tw-001', 'tw-001-P01');
    assert.equal(post.status, 200);
    assert.equal(post.body.ok, true);
    assert.ok(log.includes('POST /api/v1/notify/rules'), 'create hit the real POST route');

    const del = await rem._internals.deleteRule(post.body.rule.id);
    assert.equal(del.status, 200);
    assert.equal(del.body.ok, true);
    assert.ok(log.includes('DELETE /api/v1/notify/rules/' + post.body.rule.id), 'delete hit the real per-rule route');
  });

  await withServer({ authed: true, limit: 1 }, async ({ base }) => {
    const rem = loadClientInto(makePageSandbox(makeFetch(base)).sandbox, makeFetch(base));
    const first = await rem._internals.createRule('tw-001', 'tw-001-P01');
    assert.equal(first.status, 200);
    const second = await rem._internals.createRule('tw-002', '');
    assert.equal(second.status, 402, 'free-tier cap mirrors the worker 402');
  });

  await withServer({ authed: true }, async ({ base }) => {
    const rem = loadClientInto(makePageSandbox(makeFetch(base)).sandbox, makeFetch(base));
    const missing = await rem._internals.deleteRule('nope123');
    assert.equal(missing.status, 404, 'unknown rule id mirrors the worker 404');
  });
});

// ---------------------------------------------------------------------------
// (4) Page end-to-end: boot gate → quick-add POST → toggle PATCH → delete,
// all against the worker-real routes with the real event wiring.
// ---------------------------------------------------------------------------
test('CL-UI-61 (4): page end-to-end on the real routes — signed-in boot, quick-add POST, toggle PATCH, row DELETE', async () => {
  await withServer({ authed: true }, async ({ base, log, state }) => {
    const { sandbox, el } = makePageSandbox(makeFetch(base));
    loadClientInto(sandbox, makeFetch(base));
    new Function('window', 'document', 'localStorage', 'fetch', 'Promise', 'setTimeout', 'clearTimeout', 'MutationObserver',
      pageJs)(sandbox.window, sandbox.document, sandbox.localStorage, makeFetch(base), Promise, setTimeout, clearTimeout, undefined);
    const pg = sandbox.window.ChaseLightsRemindersPage;
    // Boot: me ×2 (client + page, separate modules) then the rules list ×2.
    assert.ok(await waitFor(() => log.filter((l) => l === 'GET /api/v1/notify/rules').length >= 2), 'both modules fetched the rules list');
    assert.equal(pg.state.signedIn, true);

    // Quick-add submit → POST /api/v1/notify/rules.
    el('rem-place').value = 'tw-001';
    el('rem-subject').value = 'tw-001-P01';
    el('rem-add-submit')._handlers.click[0]();
    assert.ok(await waitFor(() => log.includes('POST /api/v1/notify/rules')), 'quick-add POSTed the real route');
    assert.ok(await waitFor(() => pg.state.rules.length === 1));
    assert.equal(pg.state.rules[0].place_id, 'tw-001');

    // Toggle off → PATCH /api/v1/notify/rules/<id>.
    const row = { getAttribute: (k) => (k === 'data-rule-id' ? pg.state.rules[0].id : null) };
    el('rem-list')._handlers.change[0]({ target: { matches: (s) => s === '[data-rem-toggle]', checked: false, closest: () => row } });
    assert.ok(await waitFor(() => log.some((l) => l.startsWith('PATCH /api/v1/notify/rules/'))), 'toggle PATCHed the real per-rule route');
    assert.ok(await waitFor(() => pg.state.rules[0] && pg.state.rules[0].enabled === 0));

    // Row delete → DELETE /api/v1/notify/rules/<id>.
    el('rem-list')._handlers.click[0]({ target: { matches: (s) => s === '[data-rem-delete]', closest: () => row } });
    assert.ok(await waitFor(() => log.some((l) => l.startsWith('DELETE /api/v1/notify/rules/'))), 'delete hit the real per-rule route');
    assert.ok(await waitFor(() => pg.state.rules.length === 0));
    assert.equal(state.rules.length, 0);
  });
});

// ---------------------------------------------------------------------------
// (5) Login gate + throttle: /auth/me decides; signed-out never hits rules.
// ---------------------------------------------------------------------------
test('CL-UI-61 (5): signed-out gate — me 401 → no rules call; throttle reuses the answer; force refreshes', async () => {
  await withServer({ authed: false }, async ({ base, log, state }) => {
    const { sandbox } = makePageSandbox(makeFetch(base));
    const rem = loadClientInto(sandbox, makeFetch(base));
    await rem.refresh();
    assert.equal(rem.state.signedIn, false);
    assert.ok(!log.includes('GET /api/v1/notify/rules'), 'rules endpoint never hit while signed out');
    assert.equal(state.meHits, 1);

    await rem.refresh(); // throttled — the cached me answer is reused
    assert.equal(state.meHits, 1, 'throttle window reuses one /auth/me call');
    assert.ok(!log.includes('GET /api/v1/notify/rules'));

    await rem.refresh(true); // forced (chaselights:auth event path)
    assert.equal(state.meHits, 2, 'force bypasses the throttle window');
    assert.ok(!log.includes('GET /api/v1/notify/rules'));
  });
});

test('CL-UI-61 (6): signed-in throttle — repeated refreshes share one /auth/me call', async () => {
  await withServer({ authed: true }, async ({ base, log, state }) => {
    const { sandbox } = makePageSandbox(makeFetch(base));
    const rem = loadClientInto(sandbox, makeFetch(base));
    await rem.refresh();
    await rem.refresh();
    await rem.refresh();
    assert.equal(state.meHits, 1, 'three refreshes = one me call inside the window');
    assert.ok(log.filter((l) => l === 'GET /api/v1/notify/rules').length >= 1);
  });
});
