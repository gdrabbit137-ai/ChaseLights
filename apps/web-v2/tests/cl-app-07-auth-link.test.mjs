// CL-APP-07: Sign in with Apple + account linking — both shells' contract.
// Source-level assertions (same technique as cl-ui-53 / cl-app-02) plus unit
// tests for the new shell-auth.mjs helpers. Run:
//   node --test apps/web-v2/tests/cl-app-07-auth-link.test.mjs
import {test} from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname, join} from "node:path";
import {
  AUTH_CONFIG_ENDPOINT, AUTH_LINK_STATUS_ENDPOINT, AUTH_LINK_START_ENDPOINT,
  consumeLinkResult, linkResultMessage, LINK_RESULT_I18N,
  parseAuthConfig, parseLinkStatus,
} from "../shell-auth.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, "..");
const REPO = join(HERE, "..", "..", "..");
const read = (p) => readFileSync(join(WEB, p), "utf8");
const v2html = read("index.html");
const v2app = read("app.mjs");
const shellAuth = read("shell-auth.mjs");
const memberAuth = readFileSync(join(REPO, "assets", "member-auth.js"), "utf8");
const legacyIndex = readFileSync(join(REPO, "index.html"), "utf8");

test("CL-APP-07: shell-auth exposes the config/link endpoints + link_result helpers", () => {
  assert.equal(AUTH_CONFIG_ENDPOINT, "/api/v1/auth/config");
  assert.equal(AUTH_LINK_STATUS_ENDPOINT, "/api/v1/auth/link/status");
  assert.equal(AUTH_LINK_START_ENDPOINT, "/api/v1/auth/link/start");
  assert.equal(linkResultMessage("zh-TW", "ok"), LINK_RESULT_I18N.ok["zh-TW"]);
  assert.equal(linkResultMessage("ja", "error"), LINK_RESULT_I18N.error.ja);
  // unknown result → error copy; unknown locale → zh-TW copy
  assert.equal(linkResultMessage("zh-TW", "weird"), LINK_RESULT_I18N.error["zh-TW"]);
  assert.equal(linkResultMessage("ko", "ok"), LINK_RESULT_I18N.ok["zh-TW"]);
});

test("CL-APP-07: consumeLinkResult mirrors consumeAuthError semantics", () => {
  const q = new URLSearchParams("link_result=ok&lang=zh-TW");
  assert.equal(consumeLinkResult(q), "ok");
  assert.equal(q.toString(), "lang=zh-TW", "the param is stripped for URL cleanup");
  assert.equal(consumeLinkResult("link_result=error"), "error");
  assert.equal(consumeLinkResult("link_result=hack"), null);
  assert.equal(consumeLinkResult(""), null);
  assert.equal(consumeLinkResult(null), null);
});

test("CL-APP-07: parseAuthConfig fails closed on malformed documents", () => {
  assert.deepEqual(parseAuthConfig(null), {line: false, google: false, apple: false});
  assert.deepEqual(parseAuthConfig({}), {line: false, google: false, apple: false});
  assert.deepEqual(parseAuthConfig({providers: {apple: "1"}}), {line: false, google: false, apple: false});
  assert.deepEqual(parseAuthConfig({providers: {line: true, google: false, apple: true}}),
    {line: true, google: false, apple: true});
});

test("CL-APP-07: parseLinkStatus never invents a link state", () => {
  assert.equal(parseLinkStatus(null), null);
  assert.equal(parseLinkStatus({}), null);
  assert.equal(parseLinkStatus({user: {}}), null);
  const doc = parseLinkStatus({
    user: {id: "p:google:g-1", provider: "google"},
    verifiedEmail: "MEI@example.com",
    links: [{provider: "line", email: null}, "garbage"],
  });
  assert.deepEqual(doc, {
    user: {id: "p:google:g-1", provider: "google"},
    verifiedEmail: "MEI@example.com",
    links: [{provider: "line", email: null}],
  });
});

test("CL-APP-07: V2 shell carries the Apple login anchor + 連結 UI markup (fail-closed hidden)", () => {
  assert.match(v2html, /id="login-apple" class="login-link" href="\/api\/v1\/auth\/apple\/start" hidden/);
  assert.match(v2html, /id="link-toggle" class="login-link" type="button" hidden/);
  assert.match(v2html, /id="member-links" hidden/);
});

test("CL-APP-07: V2 app.mjs gates provider entries on /auth/config and drives the link panel", () => {
  assert.match(v2app, /loadProviderConfig/);
  assert.match(v2app, /AUTH_CONFIG_ENDPOINT/);
  assert.match(v2app, /\$\("login-apple"\)\.hidden=!open\|\|!providerConfig\.apple/);
  assert.match(v2app, /fillMemberLinks/);
  assert.match(v2app, /AUTH_LINK_STATUS_ENDPOINT/);
  assert.match(v2app, /AUTH_LINK_START_ENDPOINT/);
  assert.match(v2app, /link=1/);
  assert.match(v2app, /consumeLinkResult/);
});

test("CL-APP-07: V2 link copy exists in all three dictionaries", () => {
  for (const key of ["memberLoginApple", "memberLinkToggle", "memberLinkNone", "memberLinkLine",
    "memberLinkGoogle", "memberLinkApple", "memberLinkEmailLabel", "memberLinkEmailBtn",
    "memberLinkEmailSent", "memberLinkEmailPending", "memberLinkError"]) {
    const vals = [...v2app.matchAll(new RegExp(`${key}:"([^"]*)"`, "g"))].map(m => m[1]);
    assert.equal(vals.length, 3, `${key} must exist 3 times (zh-TW/en/ja)`);
    vals.forEach(v => assert.ok(v.length >= 2));
  }
});

test("CL-APP-07: legacy shell carries the Apple anchor (hidden) + the link panel logic", () => {
  assert.match(legacyIndex, /data-ma-apple href="\/api\/v1\/auth\/apple\/start"[^>]*hidden/);
  assert.match(memberAuth, /apple:\s*'\/api\/v1\/auth\/apple\/start'/);
  assert.match(memberAuth, /config:\s*'\/api\/v1\/auth\/config'/);
  assert.match(memberAuth, /linkStatus:\s*'\/api\/v1\/auth\/link\/status'/);
  assert.match(memberAuth, /linkStart:\s*'\/api\/v1\/auth\/link\/start'/);
  assert.match(memberAuth, /fillLinkSection/);
  assert.match(memberAuth, /submitLinkEmail/);
  assert.match(memberAuth, /showLinkResultNotice/);
  // fail-closed: the apple anchor is only un-hidden when config says configured
  assert.match(memberAuth, /maAppleConfigured = doc\.providers\.apple === true/);
});

test("CL-APP-07: legacy link copy exists in all three dictionaries", () => {
  for (const key of ["ma_apple", "ma_link_other", "ma_link_line", "ma_link_google",
    "ma_link_apple", "ma_link_email_label", "ma_link_email_sent", "ma_link_error"]) {
    const vals = [...memberAuth.matchAll(new RegExp(`${key}:\\s*'([^']*)'`, "g"))].map(m => m[1]);
    assert.equal(vals.length, 3, `${key} must exist 3 times (zh-TW/en/ja)`);
    vals.forEach(v => assert.ok(v.length >= 2));
  }
});
