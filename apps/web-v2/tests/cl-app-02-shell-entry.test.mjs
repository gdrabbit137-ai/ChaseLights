// CL-APP-02: shell entry — pull-to-refresh + trilingual member sign-in.
import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname, join} from "node:path";
import {createPullToRefresh, fetchCloudDigest} from "../pull-refresh.mjs";
import {AUTH_START_ENDPOINTS, AUTH_ME_ENDPOINT, parseMember, fetchMember} from "../shell-auth.mjs";

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
  assert.deepEqual(await fetchMember((url, init) => {
    calls.push([url, init]);
    return {ok: true, json: async () => ({display_name: "小美"})};
  }), {name: "小美", provider: null});
  assert.deepEqual(calls[0], ["/auth/me", {credentials: "same-origin", cache: "no-store"}]);
  assert.equal(await fetchMember(async () => ({ok: false})), null);
  assert.equal(await fetchMember(async () => { throw new Error("x"); }), null);
  assert.equal(await fetchMember(async () => ({ok: true, json: async () => { throw new Error("bad json"); }})), null);
});

test("sign-in entry points target the deployed auth endpoints", () => {
  assert.equal(AUTH_START_ENDPOINTS.line, "/api/v1/auth/line/start");
  assert.equal(AUTH_START_ENDPOINTS.google, "/api/v1/auth/google/start");
  assert.equal(AUTH_ME_ENDPOINT, "/auth/me");
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
  assert.ok(app.includes('import {fetchMember} from "./shell-auth.mjs";'));
  assert.ok(app.includes('async function refreshData()'), "refreshData defined");
  assert.ok(app.includes("state.cloudDigest=await fetchCloudDigest();"), "refresh re-fetches bundle digest");
  assert.ok(app.includes("await loadResearchIndex();"), "refresh re-fetches browse index");
  assert.ok(app.includes("await catalogState.load();"), "refresh re-fetches catalog data");
  assert.ok(app.includes("await refreshMember();"), "refresh re-checks signed-in member");
  assert.ok(app.includes('createPullToRefresh({'), "pull gesture wired");
  for (const evt of ["touchstart", "touchmove", "touchend"]) {
    assert.ok(app.includes(`document.addEventListener("${evt}"`), `${evt} listener`);
  }
  assert.ok(app.includes("async function refreshMember(){state.member=await fetchMember();renderMember();}"));
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
