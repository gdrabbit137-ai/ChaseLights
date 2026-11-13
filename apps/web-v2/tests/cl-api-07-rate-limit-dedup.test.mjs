// CL-API-07: rate-limit misjudged-logout fix (owner tail: a few owner page
// loads fired 1×/auth/me + 6×/favorites each, the IP limiter answered 429,
// and every client read `!res.ok` as signed-out — the 登入 button reappeared).
//
// Layers covered here:
//  (1) V2 shell: one page load shares at most ONE real /auth/me and ONE
//      real favorites GET across all modules (module-level single-flight +
//      result cache);
//  (2) 429/5xx semantics: MEMBER_TRANSIENT — callers keep their current
//      member/favorites state and retry with exponential backoff; only a
//      401 (with a failed refresh) decides signed-out;
//  (3) V1 member-auth.js sandbox: a 429 on /auth/me never flips a signed-in
//      masthead back to 登入 and schedules a backoff retry;
//  (4) V1 favorites-client.js sandbox: 429 on /favorites keeps the local
//      list, and repeated syncs within the window re-fetch nothing;
//  (5) worker source: lenient read class (me/favorites/notify rules/…),
//      strict auth class (callbacks/refresh), default write class.
// Run: node --test apps/web-v2/tests/cl-api-07-rate-limit-dedup.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';
import { fetchMember, resetAuthRefreshState, MEMBER_TRANSIENT } from '../shell-auth.mjs';
import { createFavoritesClient, persistLocalFavorites } from '../favorites-client.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const WEB = join(ROOT, 'apps', 'web-v2');
const V1 = ROOT;

// ---------------------------------------------------------------- (1) V2 ----
test('CL-API-07 (1): one page load issues at most 1 me + 1 favorites GET (V2)', async () => {
  const calls = [];
  const impl = (url, opts = {}) => {
    calls.push({ url, method: opts.method || 'GET' });
    if (url === '/api/v1/auth/me') {
      return Promise.resolve({ ok: true, status: 200, json: async () => ({ user: { displayName: '山客', provider: 'line' } }) });
    }
    if (url.startsWith('/api/v1/favorites')) {
      return Promise.resolve({ ok: true, status: 200, json: async () => ({ favorites: [] }) });
    }
    throw new Error('unexpected fetch ' + url);
  };
  persistLocalFavorites([]);
  const client = createFavoritesClient({ fetchImpl: impl });
  // Boot storm: member pull + favorites boot sync + auth-event resync — the
  // exact duplicates the tail logged (1×me + 6×favorites per page).
  await Promise.all([fetchMember(impl), fetchMember(impl), client.syncLocal(), client.syncLocal()]);
  const meGets = calls.filter(c => c.url === '/api/v1/auth/me' && c.method === 'GET').length;
  const favGets = calls.filter(c => c.url.startsWith('/api/v1/favorites') && c.method === 'GET').length;
  assert.ok(meGets <= 1, `me GETs = ${meGets}, must be ≤ 1 per page load`);
  assert.ok(favGets <= 1, `favorites GETs = ${favGets}, must be ≤ 1 per page load`);
});

test('CL-API-07 (2): me 429 → MEMBER_TRANSIENT, member state kept; 401 still signs out', async () => {
  const { fetchMember, resetAuthRefreshState, MEMBER_TRANSIENT } = await import('../shell-auth.mjs');
  resetAuthRefreshState();
  const res429 = await fetchMember(async () => ({ ok: false, status: 429, json: async () => ({ error: 'rate limited' }) }));
  assert.equal(res429, MEMBER_TRANSIENT, '429 is transient — callers keep the signed-in state');
  resetAuthRefreshState();
  const res401 = await fetchMember(async () => ({ ok: false, status: 401, json: async () => ({ error: 'unauthorized' }) }));
  assert.equal(res401, null, '401 (refresh also fails) is the only signed-out signal');
  resetAuthRefreshState();
});

// ---------------------------------------------------------------- (3) V1 ----
function makeElement(tag) {
  const el = {
    tagName: tag, children: [], hidden: false, disabled: false, textContent: '',
    style: {}, attributes: {}, listeners: {},
    classList: {
      _set: new Set(),
      toggle(c, force) { const on = force === undefined ? !this._set.has(c) : force; on ? this._set.add(c) : this._set.delete(c); return on; },
      add(c) { this._set.add(c); }, remove(c) { this._set.delete(c); },
      contains(c) { return this._set.has(c); }
    },
    setAttribute(k, v) { el.attributes[k] = String(v); },
    getAttribute(k) { return el.attributes[k] != null ? el.attributes[k] : null; },
    appendChild(c) { el.children.push(c); c.parentNode = el; return c; },
    insertBefore(c) { el.children.push(c); c.parentNode = el; return c; },
    removeChild(c) { el.children = el.children.filter(x => x !== c); },
    addEventListener(t, fn) { (el.listeners[t] = el.listeners[t] || []).push(fn); },
    removeEventListener() {},
    contains(n) { let x = n; while (x) { if (x === el) return true; x = x.parentNode; } return false; },
    querySelector(sel) {
      for (const c of el.children) if (sel.includes(c.attributes['data-slot'] || c.slotMatch || '')) return c;
      return null;
    },
    querySelectorAll() { return []; },
    getBoundingClientRect() { return { top: 0, left: 0, right: 10, bottom: 10, width: 10, height: 10 }; }
  };
  return el;
}

function runMemberAuth(fetchLog, routes) {
  const source = readFileSync(join(V1, 'assets', 'member-auth.js'), 'utf8');
  const area = makeElement('div');
  area.attributes['data-member-area'] = '';
  const slot = (name) => { const el = makeElement('span'); el.slotMatch = name; el.attributes['data-member-' + name] = ''; area.children.push(el); return el; };
  const toggle = slot('toggle'), menu = slot('menu'), nameEl = slot('name'), logoutBtn = slot('logout');
  const langSel = makeElement('select');
  langSel.id = 'lang-select';
  const timers = [];
  const sandbox = {
    document: {
      readyState: 'loading', cookie: '',
      getElementById(id) { return id === 'lang-select' ? langSel : null; },
      querySelector(sel) { return sel === '[data-member-area]' ? area : (sel === '#lang-select' ? langSel : null); },
      querySelectorAll() { return []; },
      createElement: makeElement,
      addEventListener(t, fn) { if (t === 'DOMContentLoaded') sandbox.domReady = fn; },
      dispatchEvent() { return true; },
      body: { appendChild: (c) => c }
    },
    window: { location: { search: '', pathname: '/', hash: '' }, history: { replaceState() {} } },
    fetch(url, opts) {
      fetchLog.push({ url, method: (opts && opts.method) || 'GET' });
      const make = routes[url];
      if (!make) throw new Error('unexpected fetch ' + url);
      return Promise.resolve(make());
    },
    setTimeout(fn, ms) { timers.push([fn, ms]); return timers.length; },
    clearTimeout() {}, localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
    URLSearchParams, CustomEvent: function (t, o) { this.type = t; this.detail = o && o.detail; },
    Promise, Date, Math, JSON, Error
  };
  sandbox.window.document = sandbox.document;
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox);
  return {
    fireReady() { return sandbox.domReady(); },
    timers,
    memberArea: area, toggle, menu, nameEl, logoutBtn,
    renderCalls: () => nameEl.textContent
  };
}

test('CL-API-07 (3): V1 masthead — me 429 never flips signed-in → 登入; backoff retry scheduled', async () => {
  const ME_OK = { ok: true, status: 200, json: async () => ({ user: { displayName: '山客小美', provider: 'line' } }) };
  const me429 = () => ({ ok: false, status: 429, json: async () => ({ error: 'rate limited' }) });
  const log = [];
  let meCalls = 0;
  const routes = {
    '/api/v1/auth/me': () => ++meCalls === 1 ? ME_OK : me429()
  };
  const box = runMemberAuth(log, routes);
  box.fireReady();
  await new Promise(r => setImmediate(r));
  assert.equal(box.toggle.hidden, true, 'boot: signed in — the 登入 toggle is hidden');
  assert.ok(box.nameEl.textContent.includes('山客小美'), 'signed-in name rendered');
  // A transient 429 on the next pull (forced fresh via logout's maMeReset)
  // must keep the member rendered — the 登入 button must NOT reappear.
  routes['/api/v1/auth/logout'] = () => ({ ok: true, status: 200, json: async () => ({ ok: true }) });
  const before = box.nameEl.textContent;
  box.logoutBtn.listeners.click[0]();
  await new Promise(r => setImmediate(r));
  await new Promise(r => setImmediate(r));
  assert.equal(box.toggle.hidden, true, '429 did NOT flip the signed-in masthead to 登入');
  assert.equal(box.nameEl.textContent, before, 'member state kept through the 429');
  assert.ok(box.timers.length >= 1, 'an exponential backoff retry was scheduled');
  assert.ok(box.timers.some(([fn, ms]) => ms === 1000 || ms === 2000 || ms === 4000), 'backoff delays are 1s→2s→4s');
});

test('CL-API-07 (3b): V1 masthead — signed-in member survives a burst of 429s', async () => {
  const log = [];
  const routes = {
    '/api/v1/auth/me': () => log.push(1) && ({ ok: true, status: 200, json: async () => ({ user: { displayName: '山客', provider: 'line' } }) })
  };
  const box = runMemberAuth(log, routes);
  box.fireReady();
  await new Promise(r => setImmediate(r));
  const signedName = box.nameEl.textContent;
  // Retry timers fire against 429s — state must never flip.
  const fns = box.timers.map(([fn]) => fn);
  for (const fn of fns) { try { fn(); } catch { /* best-effort */ } }
  await new Promise(r => setImmediate(r));
  assert.ok(box.nameEl.textContent.includes('山客'), 'member state kept through retries');
});

// ---------------------------------------------------------------- (4) V1 ----
function makeFavoritesSandbox(fetchLog, routes) {
  const source = readFileSync(join(V1, 'assets', 'favorites-client.js'), 'utf8');
  const storage = new Map();
  const timers = [];
  const sandbox = {
    document: {
      readyState: 'loading', cookie: '',
      addEventListener(t, fn) { if (t === 'chaselights:auth') sandbox.authListeners.push(fn); else if (t === 'DOMContentLoaded') sandbox.domReady = fn; },
      dispatchEvent() { return true; },
      createElement() { return makeElement('p'); },
      body: { appendChild() {} }
    },
    window: {},
    localStorage: { getItem: k => storage.has(k) ? storage.get(k) : null, setItem: (k, v) => storage.set(k, v), removeItem: k => storage.delete(k) },
    fetch(url, opts = {}) {
      fetchLog.push({ url, method: opts.method || 'GET' });
      const make = routes[url];
      if (!make) throw new Error('unexpected fetch ' + url);
      return Promise.resolve(make());
    },
    crypto: { randomUUID: () => 'uuid-fixed-clapi07' },
    setTimeout(fn, ms) { timers.push([fn, ms]); return timers.length; },
    clearTimeout() {},
    CustomEvent: function (t, o) { this.type = t; this.detail = o && o.detail; }
  };
  sandbox.authListeners = [];
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox);
  return { sandbox, timers, fireReady() { return sandbox.domReady(); } };
}

test('CL-API-07 (4): V1 favorites — 429 keeps the local list; repeat syncs issue ≤1 GET', async () => {
  const log = [];
  const routes = {
    '/api/v1/favorites?userId=uuid-fixed-clapi07': () => ({ ok: false, status: 429, json: async () => ({ error: 'rate limited' }) })
  };
  const box = makeFavoritesSandbox(log, routes);
  box.sandbox.localStorage.setItem('chaselights_favs_v2', JSON.stringify(['tw-001']));
  box.fireReady();
  await new Promise(r => setImmediate(r));
  const gets = log.filter(c => c.method === 'GET').length;
  assert.equal(gets, 1, `boot GETs = ${gets}, must be 1`);
  assert.ok(box.timers.length >= 1, '429 schedules a backoff retry');
  // A second sync within the window re-issues nothing (single-flight/cache).
  await new Promise(r => setImmediate(r));
  assert.equal(log.filter(c => c.method === 'GET').length, 1, 'no additional GETs within the window');
});

// ---------------------------------------------------------------- (5) wk ----
test('CL-API-07 (5): worker limiter — lenient reads, strict auth, default writes', () => {
  const src = readFileSync(join(V1, 'workers', 'api', 'src', 'index.js'), 'utf8');
  // read class: cheap D1/KV reads get a lenient budget
  assert.match(src, /RATE_LIMITS = \{[\s\S]*read: \{ max: \d{3,}/, 'read class is lenient (≥100/min)');
  // auth class stays strict: callbacks + token endpoints
  assert.match(src, /auth: \{ max: (\d{1,2})\b/);
  const authMax = Number(src.match(/auth: \{ max: (\d+)/)[1]);
  const readMax = Number(src.match(/read: \{ max: (\d+)/)[1]);
  assert.ok(authMax < readMax, 'auth/token budget stays strictly below the read budget');
  assert.match(src, /auth\\\/\(line\|google\)\\\/callback/, 'OAuth callbacks in the strict class');
  assert.match(src, /auth\\\/refresh/, 'token refresh in the strict class');
  // the limiter classifies per path+method before routing
  assert.match(src, /rateLimited\(ip, path, request\.method/);
});
