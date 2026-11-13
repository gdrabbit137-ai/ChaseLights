// CL-UI-57: favorites account isolation + member profile editing.
//
// A. Favorites isolation (owner-reported leak): after logout the previous
//    member's favorites stayed visible, and another account on the same
//    browser inherited them. Root causes fixed:
//      - backend: mergeAnonDevice left anonymous rows behind when the member
//        already held the same place (UPDATE OR IGNORE conflict) → device-wide
//        cleanup DELETE after the merge (workers/api/src/auth.js + index.js).
//      - client: the device-local chaselights_favs_v2 cache IS the member's
//        merged list while signed in; on a signed-in -> signed-out transition
//        it is dropped (favorites-client.js) and app.js REPLACES the rendered
//        set with the broadcast cloud set instead of adopting into it.
// B. Member profile editing: PATCH /api/v1/auth/profile (session-only) edits
//    display_name (nickname) + three optional profile fields
//    (experience/region/bio, users.profile_json via migration 0006);
//    member-auth.js expands an inline editor panel from the member name,
//    trilingual, with save/cancel and a success notice.
import { test } from 'node:test';
import assert from 'node:assert';
import { readFileSync, existsSync } from 'node:fs';
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
  if (seed) for (const [k, v] of Object.entries(seed)) storage.setItem(k, v);
  sandbox.fireDOMContentLoaded = () => {
    for (const [type, fn] of domListeners) if (type === 'DOMContentLoaded') fn();
  };
  vm.createContext(sandbox);
  vm.runInContext(readFileSync(join(ROOT, 'assets', 'favorites-client.js'), 'utf8'), sandbox);
  return { client: sandbox.window.ChaseLightsFavorites, sandbox, authListeners, init: sandbox.fireDOMContentLoaded, storage };
}

// --- (1) client: signed-out transition drops the member's local cache ---------
test('CL-UI-57 (1): logout transition clears the device-local member list so it can never leak into the anonymous device list', async () => {
  // Signed in as A: the local cache holds A's merged list.
  const fetchImpl = mockFetch([]);
  const { client, authListeners, storage } = makeSandbox(fetchImpl, { seed: { chaselights_favs_v2: '["tw-datun-P01","tw-002-P02"]' } });
  assert.equal(authListeners.length, 1, 'favorites-client.js subscribes to chaselights:auth');
  const onAuth = authListeners[0][1];

  onAuth({ detail: { member: { name: 'A' } } });   // signed in
  await Promise.resolve();
  assert.ok(storage.store.get('chaselights_favs_v2'), 'signed-in state keeps the local cache');

  onAuth({ detail: { member: null } });             // logout
  await Promise.resolve();
  assert.equal(storage.store.get('chaselights_favs_v2'), null, 'signed-out transition must drop the member list');
  assert.deepEqual(client.localFavorites(), []);
  // The failed-cloud fallback therefore broadcasts an empty set, never A's list.
  assert.deepEqual(await client.syncLocal(), []);
  // The GET after logout carries the anonymous device id (server truth).
  assert.ok(fetchImpl.calls.some(c => c.url.includes('/api/v1/favorites?userId=')), 'logout re-sync queries the anonymous device list');

  // Login again: the anonymous state was empty, so nothing of A re-uploads.
  const posts = fetchImpl.calls.filter(c => c.opts.method === 'POST');
  assert.ok(!posts.some(c => JSON.parse(c.opts.body).placeId === 'tw-datun-P01'), 'account A favorites are never re-uploaded after logout');
});

// --- (2) app.js: broadcast set replaces the rendered favorites ----------------
test('CL-UI-57 (2): app.js replaces the rendered favorites with the broadcast cloud set (logout can clear the screen)', () => {
  const app = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
  assert.match(app, /addEventListener\('chaselights:favorites'/);
  assert.match(app, /favorites=cloud;/, 'the broadcast cloud set REPLACES the in-memory list');
  assert.ok(!/for\(const id of ids\)if\(typeof id==='string'&&id&&!favorites\.includes\(id\)\)\{favorites\.push/.test(app), 'adoption-only semantics must be gone (a logout broadcast could never empty the list)');
  const client = readFileSync(join(ROOT, 'assets', 'favorites-client.js'), 'utf8');
  assert.match(client, /removeItem\(LOCAL_FAVS_KEY\)/, 'client drops the device-local member list on the signed-out transition');
  assert.match(client, /wasAuthed && !authed/);
});

// --- (3) backend: merge cleanup + profile endpoint -----------------------------
test('CL-UI-57 (3): backend merge cleans anonymous residue and exposes PATCH /auth/profile over users.profile_json', () => {
  const src = readFileSync(join(ROOT, 'workers', 'api', 'src', 'auth.js'), 'utf8');
  assert.match(src, /favorites_cleanup: "DELETE FROM favorites WHERE user_id = \?1"/, 'merge must delete anonymous residue (UPDATE OR IGNORE leaves conflicts)');
  assert.match(src, /notify_rules_cleanup: "DELETE FROM notify_rules WHERE user_id = \?1"/);
  const index = readFileSync(join(ROOT, 'workers', 'api', 'src', 'index.js'), 'utf8');
  assert.match(index, /MERGE_SQL\.favorites_cleanup\)\.bind\(anonDeviceId\)/, 'mergeAnonDevice runs the device-wide cleanup');
  assert.match(index, /path === "\/auth\/profile" && request\.method === "PATCH"/);
  assert.match(index, /PROFILE_FIELDS = \["experience", "region", "bio"\]/, 'the three optional profile fields');
  assert.match(index, /profile_json/, 'profile fields persist in users.profile_json');
  assert.match(index, /profile: \(\(\) => \{/, '/auth/me answers the profile object');
  assert.match(index, /requireSession|getSession\(req, env\)/, 'session-guarded endpoints');
  const migration = '0006_users_profile.sql';
  assert.ok(existsSync(join(ROOT, 'migrations', migration)), 'migration 0006 adds users.profile_json');
  const mig = readFileSync(join(ROOT, 'migrations', migration), 'utf8');
  assert.match(mig, /ALTER TABLE users ADD COLUMN profile_json TEXT/);
});

// --- (4) member-auth.js: trilingual profile editor panel -----------------------
test('CL-UI-57 (4): member-auth.js expands a trilingual profile editor (nickname + optional fields, save/cancel, success notice)', () => {
  const auth = readFileSync(join(ROOT, 'assets', 'member-auth.js'), 'utf8');
  assert.match(auth, /profile: '\/api\/v1\/auth\/profile'/);
  assert.match(auth, /data-ma-profile-panel/, 'the editor panel is built in the DOM');
  assert.match(auth, /ma-profile-save/);
  assert.match(auth, /ma-profile-cancel/);
  assert.match(auth, /ma_profile_saved/, 'a success notice is shown after saving');
  assert.match(auth, /displayName: name/, 'the PATCH body edits the nickname (display_name)');
  assert.match(auth, /experience: profInputs\.experience\.value\.trim\(\)/, 'the optional profile fields ride the PATCH body');
  const locales = auth.match(/ma_profile_save: '[^']*'/g) || [];
  assert.equal(locales.length, 3, 'the profile copy exists in all three dictionaries');
  const packs = ['zh-TW', 'en', 'ja'].map(l => {
    const m = auth.match(new RegExp("'" + l + "':\\s*\\{[\\s\\S]*?ma_profile_error: '([^']*)'"));
    return [l, m && m[1]];
  });
  for (const [l, err] of packs) assert.ok(err && err.length, `${l} carries ma_profile_error`);
  for (const key of ['ma_edit_profile', 'ma_nickname', 'ma_experience', 'ma_region', 'ma_bio']) {
    const hits = auth.split(new RegExp("\\b" + key + ":")).length - 1;
    assert.equal(hits, 3, `${key} exists exactly three times (zh-TW/en/ja)`);
  }
});

// --- (5) parseMember passes the profile object through (extracted-function) ----
test('CL-UI-57 (5): parseMember carries the nested profile object; empty shape falls back to null', () => {
  const src = readFileSync(join(ROOT, 'assets', 'member-auth.js'), 'utf8');
  const start = src.indexOf('function parseMember(doc) {');
  const end = src.indexOf('\n  }\n', start);
  const fn = new Function('return (' + src.slice(start, end + 4).replace('function parseMember(doc) {', 'function(doc) {') + ')')();
  const ok = fn({ user: { displayName: 'Mei', provider: 'line', profile: { experience: '十年' } } });
  assert.equal(ok.name, 'Mei');
  assert.deepEqual(ok.profile, { experience: '十年' });
  assert.equal(fn({ user: { displayName: 'Mei' } }).profile, undefined, 'missing profile stays absent');
  assert.equal(fn({ user: { displayName: 'Mei', profile: 'junk' } }).profile, undefined, 'non-object profile stays absent');
});

// --- (6) cache-bust stamps ------------------------------------------------------
test('CL-UI-57 (6): the edited V1 assets are cache-busted on their pages', () => {
  const index = readFileSync(join(ROOT, 'index.html'), 'utf8');
  assert.match(index, /assets\/app\.js\?v=clui78/);
  // CL-UI-60: member-auth.js advanced to clui68 (silent refresh session renewal).
  assert.match(index, /assets\/member-auth\.js\?v=clui68/);
  assert.match(index, /assets\/favorites-client\.js\?v=clui67/);
  for (const page of ['weather-map.html', 'genre-eval.html', 'field-intake.html']) {
    const html = readFileSync(join(ROOT, page), 'utf8');
    assert.match(html, /assets\/member-auth\.js\?v=clui68/, `${page} loads member-auth.js?v=clui68`);
  }
});

// --- (7) V2 shell: same isolation semantics ------------------------------------
test('CL-UI-57 (7): V2 shell clears the local cache on signed-out transition and replaces the favorite set', () => {
  const fav = readFileSync(join(WEB, 'favorites-client.mjs'), 'utf8');
  assert.match(fav, /export function clearLocalFavorites\(\)/);
  const app = readFileSync(join(WEB, 'app.mjs'), 'utf8');
  assert.match(app, /clearLocalFavorites/);
  assert.match(app, /favoriteIds=new Set\(ids\);/, 'V2 favorites replace the local set on cloud sync');
  assert.match(app, /if\(prev&&!state\.member\)clearLocalFavorites\(\);/);
});
