// CL-UI-60: silent login-session renewal (owner report: 登入後右上角又變回「登入」).
//
// Root cause: the access JWT cookie (cl_session) expires after 15 minutes
// while the refresh JWT cookie (cl_refresh) lasts 30 days, but member-auth.js
// (V1 shell) and shell-auth.mjs (web-v2) only ever called GET /auth/me and
// treated the 401 as signed-out — the refresh cookie was never used.
//
// Contract (from the REAL worker code, workers/api/src/index.js
// handleAuthRefresh — parser/calls follow the worker, per the last lesson):
//   POST /api/v1/auth/refresh (credentials same-origin; the HttpOnly
//   cl_refresh cookie is the only source in the shell)
//     200 → { ok: true, accessToken: "…", refreshToken: "…" } AND Set-Cookie
//           rotating BOTH cl_session and cl_refresh (the browser applies
//           them, so the follow-up /auth/me succeeds without token handling)
//     401 → { error: "invalid refresh token" } (or "user not found")
//   GET  /api/v1/auth/me 200 → { user: { id, provider, providerUserId,
//           displayName, level } }; 401 → { error: "unauthorized" }
//
// Fix contract tested here:
//   (1) me 401 → refresh 200 → me 200 → member shown;
//   (2) me 401 → refresh 401 → signed out (no second me);
//   (3) me 401 → refresh 200 → me still 401 → signed out;
//   (4) throttle: a renewed session never re-double-calls refresh (one
//       refresh POST per window; concurrent 401s share one in-flight refresh);
//   (5) non-401 failures never touch /auth/refresh;
//   (6) V1 member-auth.js mirrors the same flow + cache-bust clui81.
// Run: node --test apps/web-v2/tests/cl-ui-60-auth-refresh.test.mjs
import test, { beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import {
  AUTH_ME_ENDPOINT, AUTH_REFRESH_ENDPOINT, fetchMember, parseMember, resetAuthRefreshState,
  MEMBER_TRANSIENT, isMemberTransient
} from '../shell-auth.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const memberSource = readFileSync(join(WEB, 'assets', 'member-auth.js'), 'utf8');

// ---- worker-shaped response fixtures ----------------------------------------
const ME_UNAUTHORIZED = { error: 'unauthorized' };                                  // handleAuthMe 401 body
const ME_OK = { user: { id: 'p:line:u-9', provider: 'line', providerUserId: 'u-9',  // handleAuthMe 200 body
                       displayName: '山客小美', level: 'free', profile: {} } };
const REFRESH_OK = { ok: true, accessToken: 'acc-2', refreshToken: 'ref-2' };       // handleAuthRefresh 200 body
const REFRESH_INVALID = { error: 'invalid refresh token' };                        // handleAuthRefresh 401 body

const me200 = () => ({ ok: true, status: 200, json: async () => ME_OK });
const me401 = () => ({ ok: false, status: 401, json: async () => ME_UNAUTHORIZED });
const refresh200 = () => ({ ok: true, status: 200, json: async () => REFRESH_OK });
const refresh401 = () => ({ ok: false, status: 401, json: async () => REFRESH_INVALID });

const ME_INIT = { credentials: 'same-origin', cache: 'no-store' };
const REFRESH_INIT = { method: 'POST', credentials: 'same-origin', cache: 'no-store' };

// Records every (url, init) pair and answers from a scripted queue keyed by url.
function scriptedFetch(routes) {
  const calls = [];
  return {
    calls,
    fetchImpl: async (url, init) => {
      calls.push([url, init]);
      const queue = routes[url];
      if (!queue) throw new Error(`unexpected fetch ${url}`);
      const make = queue.length > 1 ? queue.shift() : queue[0];
      return make();
    }
  };
}

beforeEach(() => { resetAuthRefreshState(); });

test('CL-UI-60 (1): me 401 → refresh 200 → me 200 shows the member display name', async () => {
  const s = scriptedFetch({
    [AUTH_ME_ENDPOINT]: [me401, me200],
    [AUTH_REFRESH_ENDPOINT]: [refresh200]
  });
  const member = await fetchMember(s.fetchImpl);
  assert.deepEqual(member, parseMember(ME_OK), 'member resolves from the retried /auth/me');
  assert.equal(member.name, '山客小美');
  assert.deepEqual(s.calls.map(c => c[0]), [AUTH_ME_ENDPOINT, AUTH_REFRESH_ENDPOINT, AUTH_ME_ENDPOINT],
    'flow is me → refresh → retried me');
  assert.deepEqual(s.calls[1][1], REFRESH_INIT, 'refresh is a same-origin POST');
  assert.deepEqual(s.calls[2][1], ME_INIT, 'the follow-up me retries with same-origin credentials');
});

test('CL-UI-60 (2): me 401 → refresh 401 stays signed out (no second me)', async () => {
  const s = scriptedFetch({
    [AUTH_ME_ENDPOINT]: [me401],
    [AUTH_REFRESH_ENDPOINT]: [refresh401]
  });
  assert.equal(await fetchMember(s.fetchImpl), null);
  assert.deepEqual(s.calls.map(c => c[0]), [AUTH_ME_ENDPOINT, AUTH_REFRESH_ENDPOINT],
    'a rejected refresh must not re-hit /auth/me');
});

test('CL-UI-60 (3): me 401 → refresh 200 → me still 401 stays signed out', async () => {
  const s = scriptedFetch({
    [AUTH_ME_ENDPOINT]: [me401, me401],
    [AUTH_REFRESH_ENDPOINT]: [refresh200]
  });
  assert.equal(await fetchMember(s.fetchImpl), null);
  assert.deepEqual(s.calls.map(c => c[0]), [AUTH_ME_ENDPOINT, AUTH_REFRESH_ENDPOINT, AUTH_ME_ENDPOINT]);
});

test('CL-UI-60 (4a): throttle — a second 401 load within the window does not re-refresh', async () => {
  const s = scriptedFetch({
    [AUTH_ME_ENDPOINT]: [me401, me401, me401],
    [AUTH_REFRESH_ENDPOINT]: [refresh200]
  });
  // First call: me 401 → refresh 200 → me still 401 → signed out, refresh state remembered.
  assert.equal(await fetchMember(s.fetchImpl), null);
  const refreshCallsAfterFirst = s.calls.filter(c => c[0] === AUTH_REFRESH_ENDPOINT).length;
  assert.equal(refreshCallsAfterFirst, 1);
  // CL-API-07: the second load is served from the 10 s result cache — zero
  // additional requests, no refresh, no re-probe.
  assert.equal(await fetchMember(s.fetchImpl), null);
  assert.equal(s.calls.filter(c => c[0] === AUTH_REFRESH_ENDPOINT).length, 1,
    'refresh POST ran exactly once across both loads');
  assert.equal(s.calls.filter(c => c[0] === AUTH_ME_ENDPOINT).length, 2,
    'the second load reuses the cached answer (no re-probe)');
});

test('CL-UI-60 (4b): concurrent 401s share one in-flight me+refresh round trip', async () => {
  // CL-API-07: concurrent fetchMember calls share a single in-flight round
  // trip — one me probe, one refresh POST, one retried me serve both loads.
  const s = scriptedFetch({
    [AUTH_ME_ENDPOINT]: [me401, me200],
    [AUTH_REFRESH_ENDPOINT]: [refresh200]
  });
  const [a, b] = await Promise.all([fetchMember(s.fetchImpl), fetchMember(s.fetchImpl)]);
  assert.deepEqual(a, b);
  assert.deepEqual(b, parseMember(ME_OK));
  assert.equal(s.calls.filter(c => c[0] === AUTH_REFRESH_ENDPOINT).length, 1,
    'a single refresh POST serves both concurrent loads');
  assert.equal(s.calls.filter(c => c[0] === AUTH_ME_ENDPOINT).length, 2,
    'a single me probe + retried me serve both concurrent loads');
});

// CL-API-07: 429/5xx/network failures are TRANSIENT — the shell keeps its
// current member state (no 登入 flip) and retries with backoff; only a 401
// with a failed refresh decides signed-out.
test('CL-UI-60 (5): non-401 failures never touch /auth/refresh', async () => {
  const s = scriptedFetch({ [AUTH_ME_ENDPOINT]: [() => ({ ok: false, status: 500, json: async () => ({}) })] });
  assert.equal(await fetchMember(s.fetchImpl), MEMBER_TRANSIENT, '5xx is transient, not signed-out');
  assert.deepEqual(s.calls.map(c => c[0]), [AUTH_ME_ENDPOINT]);
  // Network failure on me is transient too, without a refresh attempt.
  assert.equal(await fetchMember(async () => { throw new Error('offline'); }), MEMBER_TRANSIENT);
});

test('CL-API-07 (5b): me 429 is transient — signed-in state is never dropped', async () => {
  const s = scriptedFetch({ [AUTH_ME_ENDPOINT]: [() => ({ ok: false, status: 429, json: async () => ({ error: 'rate limited' }) })] });
  assert.equal(await fetchMember(s.fetchImpl), MEMBER_TRANSIENT);
  assert.deepEqual(s.calls.map(c => c[0]), [AUTH_ME_ENDPOINT], '429 never touches /auth/refresh');
  assert.ok(isMemberTransient(MEMBER_TRANSIENT));
});

test('CL-UI-60 (6): V1 member-auth.js mirrors the silent-renewal flow', () => {
  // same endpoints as the worker contract
  assert.match(memberSource, /refresh:\s*'\/api\/v1\/auth\/refresh'/);
  assert.match(memberSource, /me:\s*'\/api\/v1\/auth\/me'/);
  // refresh is a same-origin POST, then a retried me — both same-origin no-store
  assert.match(memberSource, /method:\s*'POST',\s*credentials:\s*'same-origin',\s*cache:\s*'no-store'/);
  assert.match(memberSource, /credentials:\s*'same-origin',\s*cache:\s*'no-store'/);
  // 401 earns the refresh attempt; a non-OK refresh keeps signed-out; retried me 401 too
  assert.match(memberSource, /res\.status === 401\) return maRefreshThenMe\(\)/);
  assert.match(memberSource, /function maRefreshThenMe\(\)/);
  assert.match(memberSource, /if \(!res \|\| !res\.ok\) return null;/);
  // throttle: remembered attempt timestamp blocks a re-refresh within the window
  assert.match(memberSource, /MA_REFRESH_THROTTLE_MS = 30000/);
  assert.match(memberSource, /Date\.now\(\) - maLastRefreshAt < MA_REFRESH_THROTTLE_MS/);
  // single in-flight refresh shared by concurrent 401s
  assert.match(memberSource, /if \(maRefreshInFlight\) return maRefreshInFlight;/);
});

test('CL-UI-60 (7): cache-bust — member-auth.js advanced to clui81 on every shell page', () => {
  for (const page of ['index.html', 'weather-map.html', 'genre-eval.html', 'field-intake.html', 'reminders.html']) {
    const src = readFileSync(join(WEB, page), 'utf8');
    assert.match(src, /assets\/member-auth\.js\?v=clui81/, `${page} loads member-auth.js?v=clui81`);
  }
});
