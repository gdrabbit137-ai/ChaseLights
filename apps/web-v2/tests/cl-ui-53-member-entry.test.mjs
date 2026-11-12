// CL-UI-53: homepage member sign-in entry (V1 shell masthead).
//
// Contract tested here (source-level, mirroring sibling cl-ui-52 test):
//  (1) index.html carries a member area in the site-nav masthead with the
//      two OAuth start anchors (LINE + Google), a hidden 登入 toggle, a
//      hidden 登出 button and a hidden menu — all closed by `hidden`;
//  (2) member-auth.js reuses the existing site-nav shell classes (no new
//      stylesheet) and owns endpoints exactly like apps/web-v2/shell-auth.mjs
//      (/auth/me GET, /auth/logout POST, both 302 start endpoints);
//  (3) all copy exists in three languages (zh-TW/en/ja);
//  (4) parseMember semantics match web-v2: no usable display name → not
//      signed in (never a fake member);
//  (5) signed-in state shows the member display name + 登出; signed-out
//      shows 登入 with the LINE/Google menu;
//  (6) cache-bust: assets/member-auth.js?v=clui61 in index.html (monotonic).
// Run: node --test apps/web-v2/tests/cl-ui-53-member-entry.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const htmlSource = readFileSync(join(WEB, 'index.html'), 'utf8');
const jsSource = readFileSync(join(WEB, 'assets', 'member-auth.js'), 'utf8');

const LANGS = ['zh-TW', 'en', 'ja'];
const I18N_KEYS = ['ma_login', 'ma_logout', 'ma_line', 'ma_google', 'ma_signed_in_as', 'ma_auth_error'];

test('CL-UI-53 (1): member area lives in the site-nav masthead with both OAuth anchors', () => {
  const navAt = htmlSource.indexOf('<nav class="site-nav"');
  const areaAt = htmlSource.indexOf('data-member-area');
  const shellAt = htmlSource.indexOf('filter-shell');
  assert.ok(navAt > 0 && areaAt > navAt && areaAt < htmlSource.indexOf('filter-shell'),
    'member entry must sit inside the masthead site-nav, before the filter shell');
  assert.match(htmlSource, /data-ma-line href="\/api\/v1\/auth\/line\/start"/);
  assert.match(htmlSource, /data-ma-google href="\/api\/v1\/auth\/google\/start"/);
  // menu + 登入 toggle + 登出 button all closed/hidden in static markup
  assert.match(htmlSource, /data-member-menu hidden/);
  assert.match(htmlSource, /data-member-toggle[^>]*hidden/);
  assert.match(htmlSource, /data-member-logout[^>]*hidden/);
  assert.match(htmlSource, /data-member-name hidden/);
});

test('CL-UI-53 (2): member-auth.js owns the exact auth endpoints and reuses site-nav classes', () => {
  // CL-UI-54: the API mounts under /api/v1 — bare /auth/* 404'd live.
  assert.match(jsSource, /me:\s*'\/api\/v1\/auth\/me'/);
  assert.match(jsSource, /logout:\s*'\/api\/v1\/auth\/logout'/);
  assert.match(jsSource, /line:\s*'\/api\/v1\/auth\/line\/start'/);
  assert.match(jsSource, /google:\s*'\/api\/v1\/auth\/google\/start'/);
  // start endpoints are 302 navigations → set as anchors, never fetched
  assert.match(jsSource, /setAttribute\('href', MA_ENDPOINTS\.line\)/);
  assert.match(jsSource, /setAttribute\('href', MA_ENDPOINTS\.google\)/);
  // session rides HttpOnly cookies: same-origin + no-store, logout is POST
  assert.match(jsSource, /credentials:\s*'same-origin'/);
  assert.match(jsSource, /cache:\s*'no-store'/);
  assert.match(jsSource, /method:\s*'POST'/);
  // no new stylesheet — styling comes from the existing site-nav shell classes
  const html = htmlSource;
  assert.ok(!/member-auth\.css/.test(html), 'no member-auth.css may be added');
  assert.match(jsSource, /data-member-area/, 'widget binds to the masthead member area');
});

test('CL-UI-53 (3): all copy keys exist in all three dictionaries', () => {
  for (const key of I18N_KEYS) {
    const vals = [...jsSource.matchAll(new RegExp(`${key}:\\s*'([^']*)'`, 'g'))].map(m => m[1]);
    assert.equal(vals.length, LANGS.length, `${key} must exist ${LANGS.length} times`);
    vals.forEach(v => assert.ok(v.length >= 2, `${key} carries a meaningful label`));
  }
  for (const lang of LANGS) {
    assert.match(jsSource, new RegExp(`'${lang}':\\s*\\{`), `${lang} dictionary present`);
  }
});

// Extracted-function test (new Function) for parseMember — same slice
// technique as the legacy app.js shell tests.
function loadParseMember() {
  const start = jsSource.indexOf('function parseMember(');
  const end = jsSource.indexOf('function fetchMember(');
  assert.ok(start > 0 && end > start, 'parseMember block found');
  const fn = new Function(jsSource.slice(start, end) + '\nreturn parseMember;');
  return fn();
}

test('CL-UI-53 (4): parseMember semantics match web-v2 shell-auth (never a fake member)', () => {
  const parseMember = loadParseMember();
  assert.equal(parseMember(null), null);
  assert.equal(parseMember(undefined), null);
  assert.equal(parseMember('x'), null);
  assert.equal(parseMember([]), null);
  assert.equal(parseMember({}), null);
  assert.equal(parseMember({ display_name: '  ' }), null);
  assert.equal(parseMember({ display_name: 42 }), null);
  const m = parseMember({ display_name: ' 山客 ', provider: 'line' });
  assert.deepEqual(m, { name: '山客', provider: 'line' });
  assert.deepEqual(parseMember({ name: 'Alice' }), { name: 'Alice', provider: null });
  assert.deepEqual(parseMember({ sub: 'u-123' }), { name: 'u-123', provider: null });
});

test('CL-UI-53 (5): signed-out shows 登入 + menu; signed-in shows display name + 登出', () => {
  // CL-UI-53B: render() drives visibility via setShown — inline style.display
  // (weight-explicit, shell-rule-proof) plus the [hidden] attribute and the
  // .ma-open class; menu open state goes through setOpen().
  assert.match(jsSource, /setShown\(toggle, !signed\);/);
  assert.match(jsSource, /setShown\(logoutBtn, signed\);/);
  assert.match(jsSource, /setShown\(nameEl, signed\);/);
  assert.match(jsSource, /setOpen\(menuOpen\);/);
  assert.match(jsSource, /ma_signed_in_as'\) \+ '： ' \+ member\.name/);
  // logout re-fetches the session afterwards
  assert.match(jsSource, /logoutBtn\.disabled = true;/);
  assert.match(jsSource, /fetchMember\(\)\.then\(render\)/);
});

test('CL-UI-54: cache-bust stamp ?v=clui64 on member-auth.js on all four shell pages', () => {
  for (const page of ['index.html', 'weather-map.html', 'genre-eval.html', 'field-intake.html']) {
    const src = readFileSync(join(WEB, page), 'utf8');
    assert.match(src, /assets\/member-auth\.js\?v=clui64/, `${page} loads member-auth.js?v=clui64`);
    assert.match(src, /data-member-area/, `${page} carries the masthead member area`);
  }
  const stamps = [...htmlSource.matchAll(/\?v=(clui\d+)/g)].map(m => Number(m[1].slice(4)));
  assert.ok(Math.min(...stamps) >= 41, 'all stamps clui41+');
  assert.ok(Math.max(...stamps) === 64, 'new generation is the highest');
});

// CL-API-05: failed OAuth callbacks land on the homepage as ?auth_error=1 —
// member-auth.js consumes the flag, shows the trilingual retry notice and
// cleans the address bar.
test('CL-UI-53 (7): auth_error query flag consumed with trilingual retry notice', () => {
  assert.match(jsSource, /auth_error/);
  assert.match(jsSource, /function showAuthErrorNotice\(\)/);
  assert.match(jsSource, /showAuthErrorNotice\(\);/);
  assert.match(jsSource, /history\.replaceState/);
  const vals = [...jsSource.matchAll(/ma_auth_error:\s*'([^']*)'/g)].map(m => m[1]);
  assert.equal(vals.length, 3);
  assert.equal(vals[0], '登入失敗，請重試');
  assert.ok(vals.every(v => v.length >= 6));
});
