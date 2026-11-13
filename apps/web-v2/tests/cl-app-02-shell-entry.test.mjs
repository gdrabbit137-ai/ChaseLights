// CL-APP-02: shell entry — pull-to-refresh + trilingual member sign-in.
import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname, join} from "node:path";
import {createPullToRefresh, fetchCloudDigest} from "../pull-refresh.mjs";
import {AUTH_START_ENDPOINTS, AUTH_ME_ENDPOINT, parseMember, fetchMember, consumeAuthError, authErrorMessage, AUTH_ERROR_I18N, resetAuthRefreshState, MEMBER_TRANSIENT} from "../shell-auth.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => readFileSync(join(root, p), "utf8");

function touch(y) { return {touches: [{clientY: y}]}; }

test("pull gesture fires refresh only for a qualifying top-of-page downward pull", () => {
  let refreshes = 0, pullState = null;
  const pull = createPullToRefresh({threshold: 80, atTop: () => true,
    onRefresh: () => { refreshes++; }, onPullChange: (v) => { pullState = v; }});
  pull.handleTouchStart(touch(300));
  pull.handleTouchMove(touch(340)); // 40px — below threshold
  pull.handleTouchMove(touch(380)); // 80px — at threshold
  assert.equal(pullState, true);
  pull.handleTouchEnd();
  assert.equal(refreshes, 1);
  assert.equal(pullState, false);
  // A second touchend from the same (already consumed) gesture must not refire.
  pull.handleTouchEnd();
  assert.equal(refreshes, 1);
});

test("pull gesture ignores pulls that do not start at the top of the page", () => {
  let refreshes = 0;
  const pull = createPullToRefresh({threshold: 40, atTop: () => false,
    onRefresh: () => { refreshes++; }});
  pull.handleTouchStart(touch(100));
  pull.handleTouchMove(touch(300));
  pull.handleTouchEnd();
  assert.equal(refreshes, 0);
});

test("pull gesture requires a positive numeric threshold", () => {
  assert.throws(() => createPullToRefresh({threshold: 0}), /threshold/);
  assert.throws(() => createPullToRefresh({threshold: -5}), /threshold/);
});

test("refresh re-fetches the published bundle digest and reports it", async () => {
  const urls = [];
  const digest = await fetchCloudDigest((url) => { urls.push(url); return {ok: true, json: async () => ({digest: "abc"})}; });
  assert.equal(digest, "abc");
  assert.deepEqual(urls, ["/api/v1/catalog/digests"]);
  // Catalog-style document shape is accepted too.
  assert.equal(await fetchCloudDigest(async () => ({ok: true, json: async () => ({catalog: {sha256: "d"}})})), "d");
  // Unreachable / non-OK / malformed: null, never a throw.
  assert.equal(await fetchCloudDigest(async () => { throw new Error("offline"); }), null);
  assert.equal(await fetchCloudDigest(async () => ({ok: false, json: async () => ({})})), null);
  assert.equal(await fetchCloudDigest(async () => ({ok: true, json: async () => ({digest: 5})})), null);
});

test("member lookup parses /auth/me documents and fails closed", async () => {
  assert.deepEqual(parseMember({display_name: " 小美 ", provider: "line"}), {name: "小美", provider: "line"});
  assert.deepEqual(parseMember({name: "Ken"}), {name: "Ken", provider: null});
  assert.deepEqual(parseMember({sub: "u123"}), {name: "u123", provider: null});
  assert.equal(parseMember({display_name: "   "}), null);
  assert.equal(parseMember({}), null);
  assert.equal(parseMember(null), null);
  assert.equal(parseMember([1]), null);
  const calls = [];
  resetAuthRefreshState(); // CL-API-07: clear the module me cache between pulls
  assert.deepEqual(await fetchMember((url, init) => {
    calls.push([url, init]);
    return {ok: true, json: async () => ({display_name: "小美"})};
  }), {name: "小美", provider: null});
  assert.deepEqual(calls[0], ["/api/v1/auth/me", {credentials: "same-origin", cache: "no-store"}]);
  resetAuthRefreshState();
  // CL-API-07: unknown non-401 failures are transient — state is kept, never "signed out".
  assert.equal(await fetchMember(async () => ({ok: false})), MEMBER_TRANSIENT);
  resetAuthRefreshState();
  assert.equal(await fetchMember(async () => { throw new Error("x"); }), MEMBER_TRANSIENT);
  resetAuthRefreshState();
  assert.equal(await fetchMember(async () => ({ok: true, json: async () => { throw new Error("bad json"); }})), null);
  resetAuthRefreshState();
});

// CL-UI-56: parseMember must accept the REAL /api/v1/auth/me response shape —
// { user: { id, provider, providerUserId, displayName, level } } (nested +
// camelCase, per workers/api/src/index.js handleAuthMe). 401/empty stay signed-out.
test("CL-UI-56: parseMember parses the real nested /auth/me shape (nested camelCase wins)", () => {
  // exact handleAuthMe response shape, CJK display name, provider from user object
  assert.deepEqual(
    parseMember({user: {id: "p:line:u-9", provider: "line", providerUserId: "u-9", displayName: "山客小美", level: "free"}}),
    {name: "山客小美", provider: "line"});
  // displayName wins over legacy top-level fields
  assert.deepEqual(
    parseMember({user: {displayName: "NESTED"}, display_name: "legacy"}),
    {name: "NESTED", provider: null});
  // legacy top-level shapes still parse
  assert.deepEqual(parseMember({display_name: "舊形狀", provider: "google"}), {name: "舊形狀", provider: "google"});
  // 401-like / empty bodies must never yield a member
  assert.equal(parseMember({}), null);
  assert.equal(parseMember({error: "unauthorized"}), null);
  assert.equal(parseMember({user: null}), null);
  assert.equal(parseMember({user: {}}), null);
  assert.equal(parseMember({user: {displayName: "  "}}), null);
  assert.equal(parseMember({user: {displayName: 42}}), null);
});

// CL-UI-56: fetchMember treats a 401 as signed-out and parses the nested shape on 200.
test("CL-UI-56: fetchMember returns null on 401 and parses nested shape on 200", async () => {
  resetAuthRefreshState();
  const ok401 = {ok: false, status: 401, json: async () => ({error: "unauthorized"})};
  assert.equal(await fetchMember(async () => ok401), null);
  resetAuthRefreshState();
  const ok200 = {ok: true, status: 200, json: async () => ({user: {id: "x", provider: "line", providerUserId: "y", displayName: "測試員", level: "free"}})};
  assert.deepEqual(await fetchMember(async () => ok200), {name: "測試員", provider: "line"});
  resetAuthRefreshState();
});

test("sign-in entry points target the deployed auth endpoints", () => {
  assert.equal(AUTH_START_ENDPOINTS.line, "/api/v1/auth/line/start");
  assert.equal(AUTH_START_ENDPOINTS.google, "/api/v1/auth/google/start");
  assert.equal(AUTH_ME_ENDPOINT, "/api/v1/auth/me");
  const html = read("index.html");
  assert.ok(html.includes(`<a id="login-line" class="login-link" href="${AUTH_START_ENDPOINTS.line}" hidden>`));
  assert.ok(html.includes(`<a id="login-google" class="login-link" href="${AUTH_START_ENDPOINTS.google}" hidden>`));
});

test("index.html carries the member area and pull indicator markup", () => {
  const html = read("index.html");
  for (const id of ["member-area", "login-line", "login-google", "member-name", "login-toggle", "pull-indicator"]) {
    assert.ok(html.includes(`id="${id}"`), `markup for #${id}`);
  }
  // Anchors are top-level navigations (never fetched with XHR in markup).
  assert.ok(!html.includes("fetch("));
});

test("app.mjs wires refresh to digest + data re-fetch and guarded member rendering", () => {
  const app = read("app.mjs");
  assert.ok(app.includes('import {createPullToRefresh,fetchCloudDigest} from "./pull-refresh.mjs";'));
  assert.ok(app.includes('import {fetchMember,MEMBER_TRANSIENT,consumeAuthError,authErrorMessage} from "./shell-auth.mjs";'));
  assert.ok(app.includes('async function refreshData()'), "refreshData defined");
  assert.ok(app.includes("state.cloudDigest=await fetchCloudDigest();"), "refresh re-fetches bundle digest");
  assert.ok(app.includes("await loadResearchIndex();"), "refresh re-fetches browse index");
  assert.ok(app.includes("await catalogState.load();"), "refresh re-fetches catalog data");
  assert.ok(app.includes("await refreshMember();"), "refresh re-checks signed-in member");
  assert.ok(app.includes('createPullToRefresh({'), "pull gesture wired");
  for (const evt of ["touchstart", "touchmove", "touchend"]) {
    assert.ok(app.includes(`document.addEventListener("${evt}"`), `${evt} listener`);
  }
  assert.ok(app.includes("async function refreshMember(){") && app.includes("if(prev&&!state.member)clearLocalFavorites();"), "refreshMember keeps guarded member rendering and drops the member cache on sign-out");;
  // Single-flight guard: a second pull during refresh must not stack loads.
  assert.ok(app.includes("if(refreshing)return;"));
});

test("i18n sign-in/refresh keys exist in all three locales", () => {
  const app = read("app.mjs");
  const keys = ["refreshing", "memberLogin", "memberLoginLine", "memberLoginGoogle", "memberLabel"];
  // The three base `copy` dictionaries are single source lines ending in "},"/"".
  const lineRe = /^"zh-TW":\{.*\},?$|^en:\{.*\},?$|^ja:\{.*\},?$/;
  const dictLines = app.split("\n").filter(l => lineRe.test(l)).slice(0, 3);
  assert.equal(dictLines.length, 3);
  const dictObjs = dictLines.map(l => new Function(`return ({${l}})`)());
  const dicts = dictObjs.map(o => Object.values(o)[0]);
  const keySets = dicts.map(d => Object.keys(d).sort().join("|"));
  assert.equal(keySets[1], keySets[0], "en key set matches zh-TW");
  assert.equal(keySets[2], keySets[0], "ja key set matches zh-TW");
  for (const key of keys) {
    for (const dict of dicts) assert.ok(key in dict && dict[key].length > 0, `key ${key}`);
  }
});

test("styles.css visibility rules are :not([hidden])-guarded", () => {
  const css = read("styles.css");
  for (const sel of [".login-link:not([hidden])", "#login-toggle:not([hidden])", ".member-name:not([hidden])", "#pull-indicator:not([hidden])"]) {
    assert.ok(css.includes(sel), `guarded selector ${sel}`);
  }
  // No unscoped display rule on the new elements (would swallow [hidden]).
  assert.ok(!/#pull-indicator\{[^}]*display/.test(css));
});

// --- CL-API-05: failed OAuth callback lands as ?auth_error=1 -----------------
test("consumeAuthError detects auth_error=1 and strips it from the query", () => {
  const q = new URLSearchParams("?auth_error=1&keep=2");
  assert.equal(consumeAuthError(q), true);
  assert.equal(q.has("auth_error"), false);
  assert.equal(q.get("keep"), "2");
  // URLSearchParams.get returns the FIRST occurrence → "0" does not count.
  assert.equal(consumeAuthError(new URLSearchParams("?auth_error=0")), false);
  assert.equal(consumeAuthError(new URLSearchParams("?other=1")), false);
  assert.equal(consumeAuthError(new URLSearchParams("")), false);
  assert.equal(consumeAuthError(null), false);
  assert.equal(consumeAuthError(undefined), false);
});

test("authErrorMessage is trilingual and falls back to zh-TW", () => {
  assert.equal(authErrorMessage("zh-TW"), "登入失敗，請重試");
  assert.equal(authErrorMessage("en"), "Sign in failed, please try again");
  assert.equal(authErrorMessage("ja"), "ログインに失敗しました。もう一度お試しください");
  assert.equal(authErrorMessage("fr"), "登入失敗，請重試");
  assert.deepEqual(Object.keys(AUTH_ERROR_I18N).sort(), ["en", "ja", "zh-TW"]);
});

test("auth-error notice markup + app.mjs wiring (CL-API-05)", () => {
  const html = read("index.html");
  assert.ok(html.includes('id="auth-error"'), "notice element present");
  assert.ok(html.includes('<p id="auth-error" role="status" aria-live="polite" hidden>'), "hidden + aria-live");
  const app = read("app.mjs");
  assert.ok(app.includes("consumeAuthError(q)"), "flag consumed at startup");
  assert.ok(app.includes("authErrorMessage(state.locale)"), "locale-aware copy");
  assert.ok(app.includes('history.replaceState'), "address bar cleaned");
  assert.ok(app.includes('el.hidden=false;'), "notice unhidden");
});
