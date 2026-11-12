// CL-APP-03 tests: push token CRUD endpoints + FCM HTTP v1 cron delivery
// (mocked fetch; no external deps).
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { runNotifyCron } from "../src/notify.js";
import { getFcmAccessToken, _resetFcmTokenCache } from "../src/push.js";
import { signJWT } from "../src/auth.js";

const HOUR = 3_600_000;
const NOW = Date.parse("2026-11-10T12:00:00+08:00");

// ---------------------------------------------------------------- mock D1
function makeMockD1() {
  const t = {
    notify_rules: [], notify_log: new Map(), telegram_bindings: new Map(),
    web_push_subscriptions: new Map(), users: new Map(), push_tokens: new Map(),
  };
  const db = {
    _tables: t,
    prepare(sql) {
      const runner = (args) => ({
        run: async () => runSql(t, sql, args),
        first: async () => {
          if (/SELECT device_id FROM users/.test(sql)) return { device_id: args[0] };
          if (/SELECT COUNT\(\*\) AS n FROM notify_rules/.test(sql)) {
            return { n: t.notify_rules.filter((r) => r.user_id === args[0]).length };
          }
          const bm = sql.match(/SELECT (chat_id, status|status, chat_id) FROM telegram_bindings/);
          if (bm) { const b = t.telegram_bindings.get(args[0]); return b ? { chat_id: b.chat_id, status: b.status } : null; }
          return null;
        },
        all: async () => {
          if (/FROM push_tokens WHERE user_device_id = \?1/.test(sql)) {
            return { results: [...t.push_tokens.values()].filter((x) => x.user_device_id === args[0]).map((x) => ({ token: x.token })) };
          }
          if (/FROM notify_rules r WHERE r\.enabled = 1/.test(sql)) {
            return { results: t.notify_rules.filter((r) => r.enabled === 1) };
          }
          return { results: [] };
        },
      });
      return { ...runner([]), bind: (...a) => runner(a) };
    },
  };
  return db;
}

function runSql(t, sql, args) {
  if (/INSERT INTO push_tokens/.test(sql)) {
    t.push_tokens.set(args[2], { user_device_id: args[0], platform: args[1], token: args[2], updated_at: "now" });
    return { meta: { changes: 1 } };
  }
  if (/DELETE FROM push_tokens/.test(sql)) {
    const had = t.push_tokens.has(args[0]);
    t.push_tokens.delete(args[0]);
    return { meta: { changes: had ? 1 : 0 } };
  }
  if (/INSERT INTO notify_rules/.test(sql)) {
    t.notify_rules.push({ id: args[0], user_id: args[1], place_id: args[2], opportunity_id: args[3], channel: args[4], min_advance_hours: args[5], enabled: 1 });
    return { meta: { changes: 1 } };
  }
  if (/DELETE FROM notify_rules/.test(sql)) {
    const i = t.notify_rules.findIndex((r) => r.id === args[0] && r.user_id === args[1]);
    if (i < 0) return { meta: { changes: 0 } };
    t.notify_rules.splice(i, 1);
    return { meta: { changes: 1 } };
  }
  if (/INSERT INTO notify_log/.test(sql)) {
    const key = `${args[0]}|${args[1]}`;
    if (t.notify_log.has(key)) return { meta: { changes: 0 } };
    t.notify_log.set(key, { delivered: 0, detail: null });
    return { meta: { changes: 1 } };
  }
  if (/UPDATE notify_log SET delivered = \?2/.test(sql)) {
    const entry = t.notify_log.get(`${args[0]}|${args[3]}`);
    if (entry) { entry.delivered = args[1]; entry.detail = args[2]; return { meta: { changes: 1 } }; }
    return { meta: { changes: 0 } };
  }
  if (/UPDATE notify_log SET delivered = 0, detail = \?2/.test(sql)) {
    const entry = t.notify_log.get(`${args[0]}|${args[2]}`);
    if (entry) { entry.delivered = 0; entry.detail = args[1]; return { meta: { changes: 1 } }; }
    return { meta: { changes: 0 } };
  }
  if (/INSERT INTO users|DELETE FROM telegram_bindings/.test(sql)) return { meta: { changes: 0 } };
  return { meta: { changes: 0 } };
}

function makeEnv(opts = {}) {
  const store = new Map(Object.entries(opts.kv || {}));
  const kv = { get: async (k, type) => { const v = store.has(k) ? store.get(k) : null; return v !== null && type === "json" ? JSON.parse(v) : v; }, put: async (k, v) => { store.set(k, v); }, _store: store };
  const db = opts.db || makeMockD1();
  return { env: { EVALS: kv, DB: db, TG_BOT_TOKEN: "TEST:TOKEN", AUTH_SECRET: "test-secret", ...opts.env }, db };
}

function makeReq(path, opts = {}) {
  const headers = new Headers(opts.headers || {});
  return new Request(`https://chaselights.app/api/v1${path}`, { ...opts, headers });
}

async function mint(env, sub, level = "free") {
  return signJWT({ sub, name: "T", level, typ: "access", exp: Math.floor(Date.now() / 1000) + 600 }, env.AUTH_SECRET);
}

// ------------------------------------------------- push token CRUD (CL-APP-03)
test("push_tokens: anonymous device-id registration upserts by token PK", async () => {
  const { env, db } = makeEnv({});
  const res = await worker.fetch(makeReq("/push_tokens", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ platform: "android/fcm", token: "tok-A", deviceId: "anon-1" }),
  }), env, {});
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.equal(body.ok, true);
  assert.equal(db._tables.push_tokens.get("tok-A").user_device_id, "anon-1");

  // same token re-registered from the same device -> single row, updated in place
  const res2 = await worker.fetch(makeReq("/push_tokens", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ platform: "android/fcm", token: "tok-A", deviceId: "anon-1" }),
  }), env, {});
  assert.equal(res2.status, 200);
  assert.equal(db._tables.push_tokens.size, 1);
});

test("push_tokens: JWT session binds the token to the member id", async () => {
  const { env, db } = makeEnv({});
  const t = await mint(env, "p:line:u1");
  const res = await worker.fetch(makeReq("/push_tokens", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${t}` },
    body: JSON.stringify({ platform: "android/fcm", token: "tok-B" }),
  }), env, {});
  assert.equal(res.status, 200);
  assert.equal(db._tables.push_tokens.get("tok-B").user_device_id, "p:line:u1");
  const out = await res.json();
  assert.equal(out.deviceId, "p:line:u1");
});

test("push_tokens: validation — no auth and no deviceId -> 400; empty token -> 400", async () => {
  const { env } = makeEnv({});
  const noAuth = await worker.fetch(makeReq("/push_tokens", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ platform: "android/fcm", token: "tok-C" }),
  }), env, {});
  assert.equal(noAuth.status, 400);
  const noToken = await worker.fetch(makeReq("/push_tokens", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ deviceId: "anon-1" }),
  }), env, {});
  assert.equal(noToken.status, 400);
});

test("push_tokens: DELETE unregisters by token (200) / unknown (404) / missing (400)", async () => {
  const { env, db } = makeEnv({});
  db._tables.push_tokens.set("tok-D", { user_device_id: "anon-1", platform: "android/fcm", token: "tok-D" });
  const missing = await worker.fetch(makeReq("/push_tokens", {
    method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token: "tok-D" }),
  }), env, {});
  assert.equal(missing.status, 200);
  const body = await missing.json();
  assert.equal(body.ok, true);
  const unknown = await worker.fetch(makeReq("/push_tokens", {
    method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token: "nope" }),
  }), env, {});
  assert.equal(unknown.status, 404);
  const empty = await worker.fetch(makeReq("/push_tokens", {
    method: "DELETE", headers: { "Content-Type": "application/json" }, body: "{}",
  }), env, {});
  assert.equal(empty.status, 400);
});

// ------------------------------------------------- FCM HTTP v1 (CL-APP-03)
async function makeServiceAccountJson() {
  const kp = await crypto.subtle.generateKey(
    { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true, ["sign", "verify"]
  );
  const pkcs8 = await crypto.subtle.exportKey("pkcs8", kp.privateKey);
  const b64 = btoa(String.fromCharCode(...new Uint8Array(pkcs8)));
  const pem = `-----BEGIN PRIVATE KEY-----\n${b64.replace(/(.{64})/g, "$1\n").trim()}\n-----END PRIVATE KEY-----`;
  return JSON.stringify({ project_id: "chaselights-test", client_email: "push@chaselights-test.iam.gserviceaccount.com", private_key: pem });
}

test("getFcmAccessToken: no secret -> fail-closed skip (no throw)", async () => {
  _resetFcmTokenCache();
  const { env } = makeEnv({});
  const r = await getFcmAccessToken(env);
  assert.equal(r.ok, false);
  assert.equal(r.skipped, "no-credentials");
});

test("cron: push rule with service-account secret sends via FCM HTTP v1 (mocked)", async () => {
  _resetFcmTokenCache();
  const sa = await makeServiceAccountJson();
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify({
      place_id: "tw-001", name_i18n: { "zh-TW": "七星潭" },
      subjects: [{ opportunity_id: "star-trail", name_i18n: { "zh-TW": "star-trail" }, days: [{ local_date: "2026-11-10", verdict: "GUIDANCE_SATISFIED", hours: ["22:00"] }] }],
    }) },
    env: { FCM_SERVICE_ACCOUNT_JSON: sa },
  });
  db._tables.notify_rules.push({ id: "r1", user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "push", min_advance_hours: 0, enabled: 1 });
  db._tables.push_tokens.set("tok-E", { user_device_id: "u1", platform: "android/fcm", token: "tok-E" });

  const calls = [];
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    calls.push({ url: String(url), init });
    if (String(url).includes("oauth2.googleapis.com/token")) {
      return new Response(JSON.stringify({ access_token: "ya29.mock", expires_in: 3600 }), { status: 200 });
    }
    return new Response(JSON.stringify({ name: "projects/chaselights-test/messages/1" }), { status: 200 });
  };
  try {
    const s = await runNotifyCron(env, NOW);
    assert.equal(s.sent, 1);
    const fcm = calls.find((c) => c.url.includes("fcm.googleapis.com/v1/projects/chaselights-test/messages:send"));
    assert.ok(fcm, "FCM v1 call expected");
    assert.equal(fcm.init.headers.Authorization, "Bearer ya29.mock");
    const payload = JSON.parse(fcm.init.body);
    assert.equal(payload.message.token, "tok-E");
    assert.ok(payload.message.notification.title.includes("ChaseLights"));
    assert.ok(payload.message.android.notification.channel_id, "chaselights_reminders");
    const logEntry = db._tables.notify_log.get("r1|2026-11-10T22:00");
    assert.equal(logEntry.delivered, 1);
  } finally {
    globalThis.fetch = origFetch;
  }
});

test("cron: push rule without FCM secret is fail-closed skipped (cron survives)", async () => {
  _resetFcmTokenCache();
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify({
      place_id: "tw-001", name_i18n: { "zh-TW": "七星潭" },
      subjects: [{ opportunity_id: "star-trail", name_i18n: { "zh-TW": "star-trail" }, days: [{ local_date: "2026-11-10", verdict: "GUIDANCE_SATISFIED", hours: ["22:00"] }] }],
    }) },
  });
  db._tables.notify_rules.push({ id: "r1", user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "push", min_advance_hours: 0, enabled: 1 });
  db._tables.push_tokens.set("tok-F", { user_device_id: "u1", platform: "android/fcm", token: "tok-F" });

  const calls = [];
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (url) => { calls.push(String(url)); return new Response("{}", { status: 200 }); };
  try {
    const s = await runNotifyCron(env, NOW);
    assert.equal(s.sent, 0);
    assert.equal(s.undelivered, 1);
    assert.ok(!calls.some((c) => c.includes("fcm.googleapis.com")), "no FCM call without credentials");
    const logEntry = db._tables.notify_log.get("r1|2026-11-10T22:00");
    assert.equal(logEntry.delivered, 0);
    assert.ok(logEntry.detail.includes("fail-closed"));
  } finally {
    globalThis.fetch = origFetch;
  }
});

test("cron: push rule with secret but no registered token is undelivered", async () => {
  _resetFcmTokenCache();
  const sa = await makeServiceAccountJson();
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify({
      place_id: "tw-001", name_i18n: { "zh-TW": "七星潭" },
      subjects: [{ opportunity_id: "star-trail", name_i18n: { "zh-TW": "star-trail" }, days: [{ local_date: "2026-11-10", verdict: "GUIDANCE_SATISFIED", hours: ["22:00"] }] }],
    }) },
    env: { FCM_SERVICE_ACCOUNT_JSON: sa },
  });
  db._tables.notify_rules.push({ id: "r1", user_id: "u2", place_id: "tw-001", opportunity_id: null, channel: "push", min_advance_hours: 0, enabled: 1 });
  const s = await runNotifyCron(env, NOW);
  assert.equal(s.sent, 0);
  assert.equal(s.undelivered, 1);
  assert.ok(db._tables.notify_log.get("r1|2026-11-10T22:00").detail.includes("no registered device token"));
});

test("rules: channel accepts push (default) and legacy telegram", async () => {
  const { env, db } = makeEnv({});
  const t = await mint(env, "u1", "paid");
  const hdr = { "Content-Type": "application/json", Authorization: `Bearer ${t}` };
  const a = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-001" }) }), env, {});
  assert.equal((await a.json()).rule.channel, "push");
  const b = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-002", channel: "telegram" }) }), env, {});
  assert.equal((await b.json()).rule.channel, "telegram");
  const c = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-003", channel: "sms" }) }), env, {});
  assert.equal(c.status, 400);
});
