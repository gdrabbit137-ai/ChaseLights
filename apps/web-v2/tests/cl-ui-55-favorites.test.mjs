// CL-UI-55: cloud-backed favorites — POST add/remove over /api/v1/favorites,
// anonymous device-id fallback, offline fallback to chaselights_favs_v2,
// first-launch local upload/merge and login resync.
//
// Layers covered here:
//  (1) assets/favorites-client.js (V1 shell) unit behavior against a mocked
//      fetch (contract shape from workers/api/src/index.js handleFavorites).
//  (2) V1 shell wiring: favorites-client.js stamped ?v=clui67 on all four
//      shell pages; app.js routes the card star through
//      window.ChaseLightsFavorites and adopts cloud merges via the
//      chaselights:favorites event; member-auth.js broadcasts chaselights:auth.
//  (3) V2 shell wiring: app.mjs star button + favorites module import +
//      trilingual i18n keys; packaging manifests register the new module.
import { test } from 'node:test';
import assert from 'node:assert';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const WEB = join(ROOT, 'apps', 'web-v2');

function mockFetch(responses) {
  const calls = [];
  const impl = (url, opts = {}) => {
    calls.push({ url, opts });
    const spec = responses.shift() || { ok: false, status: 503, body: { error: 'unavailable' } };
    return Promise.resolve({
      ok: spec.ok !== false, status: spec.status || 200,
      json: async () => spec.body
    });
  };
  impl.calls = calls;
  return impl;
}

function makeSandbox(fetchImpl, { seed } = {}) {
  const authListeners = [];
  const domListeners = [];
  const storage = { store: new Map(), getItem(k) { return this.store.has(k) ? this.store.get(k) : null; }, setItem(k, v) { this.store.set(k, String(v)); }, removeItem(k) { this.store.delete(k); } };
  const sandbox = {
    document: {
      addEventListener: (type, fn) => { (type === 'chaselights:auth' ? authListeners : domListeners).push([type, fn]); },
      dispatchEvent: () => true,
      readyState: 'loading',
      cookie: '',
      body: { appendChild: () => {} }
    },
    localStorage: storage,
    fetch: fetchImpl,
    crypto: { randomUUID: () => 'uuid-fixed-0001' },
    setTimeout: () => 0, clearTimeout: () => {},
    CustomEvent: function (type, opts) { this.type = type; this.detail = opts && opts.detail; }
  };
  sandbox.window = sandbox;
  // The IIFE boots syncLocal on load; keep it deferred (readyState=loading)
  // so each test seeds localStorage and drives init explicitly.
  if (seed) for (const [k, v] of Object.entries(seed)) storage.setItem(k, v);
  sandbox.fireDOMContentLoaded = () => {
    for (const [type, fn] of domListeners) if (type === 'DOMContentLoaded') fn();
  };
  vm.createContext(sandbox);
  vm.runInContext(readFileSync(join(ROOT, 'assets', 'favorites-client.js'), 'utf8'), sandbox);
  return { client: sandbox.window.ChaseLightsFavorites, sandbox, authListeners, init: sandbox.fireDOMContentLoaded };
}

test('CL-UI-55 (1): toggle posts the backend contract shape (add/remove) with the device id', async () => {
  const fetchImpl = mockFetch([
    { body: { ok: true, action: 'add' } },
    { body: { userId: 'uuid-fixed-0001', favorites: [{ place_id: 'tw-001-P01' }] } },
    { body: { ok: true, action: 'remove' } }
  ]);
  const { client } = makeSandbox(fetchImpl);
  const ids = await client.toggle('tw-001-P01', true);
  const post = fetchImpl.calls.find(c => c.opts.method === 'POST');
  assert.ok(post.url.startsWith('/api/v1/favorites'), 'POST hits the favorites endpoint');
    assert.equal(post.opts.method, 'POST');
  assert.equal(post.opts.credentials, 'same-origin');
  const body = JSON.parse(post.opts.body);
  assert.equal(body.placeId, 'tw-001-P01');
  assert.equal(body.action, 'add');
  assert.equal(body.userId, 'uuid-fixed-0001');
  assert.deepEqual([...ids], ['tw-001-P01']);
  await client.toggle('tw-001-P01', false);
  const removes = fetchImpl.calls.filter(c => c.opts.method === 'POST').slice(-1);
  assert.equal(JSON.parse(removes[0].opts.body).action, 'remove');
});

test('CL-UI-55 (2): offline toggle falls back to the local list without throwing', async () => {
  const { client, sandbox, init } = makeSandbox(mockFetch([]), { seed: { chaselights_favs_v2: '["tw-001-P01"]' } });
  init();
  const ids = await client.toggle('tw-002-P02', true);
  assert.deepEqual([...ids], ['tw-001-P01']);
});

test('CL-UI-55 (3): syncLocal uploads missing local favorites and returns the merged cloud set', async () => {
  const fetchImpl = mockFetch([
    { body: { favorites: [] } },                    // initial GET
    { body: { ok: true } },                          // POST add tw-001
    { body: { ok: true } },                          // POST add jp-001
    { body: { favorites: [{ place_id: 'tw-001-P01' }, { place_id: 'jp-001-P01' }] } }  // merged final GET
  ]);
  const { client } = makeSandbox(fetchImpl, { seed: { chaselights_favs_v2: '["tw-001-P01","jp-001-P01"]' } });
  const merged = await client.syncLocal();
  assert.deepEqual([...merged], ['tw-001-P01', 'jp-001-P01']);
  const posts = fetchImpl.calls.filter(c => c.opts.method === 'POST');
  assert.deepEqual(posts.map(c => JSON.parse(c.opts.body).placeId), ['tw-001-P01', 'jp-001-P01']);
  assert.ok(fetchImpl.calls[0].url.includes('userId=uuid-fixed-0001'), 'GET carries the anonymous device id');
});

test('CL-UI-55 (4): offline syncLocal keeps the local list and the client subscribes to chaselights:auth', async () => {
  const { client, authListeners } = makeSandbox(mockFetch([]), { seed: { chaselights_favs_v2: '["tw-001-P01"]' } });
  assert.deepEqual([...await client.syncLocal()], ['tw-001-P01']);
  assert.equal(authListeners.length, 1, 'favorites-client.js subscribes to the member-auth broadcast');
});

test('CL-UI-55 (5): V1 shell — favorites-client.js is stamped ?v=clui67 on all four shell pages', () => {
  for (const page of ['index.html', 'weather-map.html', 'genre-eval.html', 'field-intake.html']) {
    const html = readFileSync(join(ROOT, page), 'utf8');
    assert.match(html, /assets\/favorites-client\.js\?v=clui67/, `${page} loads favorites-client.js?v=clui67`);
  }
});

test('CL-UI-55 (6): app.js routes the card star through ChaseLightsFavorites and adopts cloud merges', () => {
  const app = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
  assert.match(app, /window\.ChaseLightsFavorites\)window\.ChaseLightsFavorites\.toggle\(id,!removing\)/, 'card star toggle delegates to the cloud client');
  assert.match(app, /addEventListener\('chaselights:favorites'/, 'app.js listens for cloud favorites merges');
  const client = readFileSync(join(ROOT, 'assets', 'favorites-client.js'), 'utf8');
  assert.match(client, /\/api\/v1\/favorites/, 'V1 client hits the cloud endpoint');
  assert.match(client, /credentials: 'same-origin'/, 'member session cookie rides along');
  const auth = readFileSync(join(ROOT, 'assets', 'member-auth.js'), 'utf8');
  assert.match(auth, /chaselights:auth/, 'member-auth.js broadcasts the auth state');
});

test('CL-UI-55 (7): V2 shell — app.mjs renders the cloud-backed star and imports the favorites module', () => {
  const app = readFileSync(join(WEB, 'app.mjs'), 'utf8');
  assert.match(app, /from "\.\/favorites-client\.mjs"/);
  assert.match(app, /node\("button","fav-star"\)/);
  assert.match(app, /favoritesClient\.toggle\(placeKey,adding\)/);
  assert.match(app, /refreshFavorites\(\)/, 'V2 boot + pull-to-refresh re-sync favorites');
  const favLines = app.split('\n').filter(l => l.includes('favStarAdd:'));
  assert.equal(favLines.length, 3, 'exactly three locale lines carry the favorites keys (zh-TW/en/ja)');
  for (const line of favLines) {
    assert.ok(line.includes('favStarRemove:') && line.includes('favNotice:'), 'each locale carries all favorites keys');
  }
  const css = readFileSync(join(WEB, 'styles.css'), 'utf8');
  assert.match(css, /\.fav-star/, 'star styling ships in styles.css');
});

test('CL-UI-55 (8): the favorites module is registered in both packaging manifests', () => {
  const build = readFileSync(join(ROOT, 'ops', 'v2', 'build_static.py'), 'utf8');
  assert.match(build, /'favorites-client\.mjs'/, 'RUNTIME_FILES carries favorites-client.mjs');
  const plan = JSON.parse(readFileSync(join(ROOT, 'ops', 'v2', 'deployment_plan.json'), 'utf8'));
  const files = plan.files || plan;
  const list = Array.isArray(files) ? files : Object.values(files).flat();
  assert.ok(list.includes('favorites-client.mjs'), 'deployment_plan.json carries favorites-client.mjs');
});
