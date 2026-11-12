// CL-API-03 tests: cron matcher, dedupe, limits, TG delivery (mock fetch),
// rules endpoints (JWT-only). node:test, no external deps.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { findNextWindow, windowKey, buildMessage, runNotifyCron, pollTelegramBindings, MATCH_WINDOW_H } from "../src/notify.js";
import { signJWT } from "../src/auth.js";
import { generateVapidKeys } from "../src/webpush.js";

const HOUR = 3_600_000;

// ---------------------------------------------------------------- mock D1
function makeMockD1() {
  const t = { notify_rules: [], notify_log: new Map(), telegram_bindings: new Map(), web_push_subscriptions: new Map(), users: new Map() };
  const db = {
    _tables: t,
    prepare(sql) {
      const runner = (args) => ({
        run: async () => runSql(t, sql, args),
        first: async () => {
          // SELECT COUNT(*) FROM notify_rules WHERE user_id = ?
          const cm = sql.match(/COUNT\(\*\) AS n FROM notify_rules WHERE user_id = \?1/);
          if (cm) return { n: t.notify_rules.filter((r) => r.user_id === args[0]).length };
          const lm = sql.match(/SELECT level FROM users/);
          if (lm) { const u = t.users.get(args[0]); return u ? { level: u.level } : null; }
          const bm = sql.match(/SELECT (chat_id, status|status, chat_id) FROM telegram_bindings/);
          if (bm) { const b = t.telegram_bindings.get(args[0]); return b ? { chat_id: b.chat_id, status: b.status } : null; }
          const pm = sql.match(/SELECT user_id FROM telegram_bindings WHERE token = \?1 AND status = 'pending'/);
          if (pm) { for (const [uid, b] of t.telegram_bindings) if (b.token === args[0] && b.status === "pending") return { user_id: uid }; return null; }
          return null;
        },
        all: async () => {
          const lm = sql.match(/FROM notify_rules WHERE user_id = \?1 ORDER BY created_at DESC/);
          if (lm) return { results: t.notify_rules.filter((r) => r.user_id === args[0]) };
          const em = sql.match(/FROM notify_rules r WHERE r\.enabled = 1/);
          if (em) return { results: t.notify_rules.filter((r) => r.enabled === 1) };
          return { results: [] };
        },
      });
      return { ...runner([]), bind: (...a) => runner(a) }; // D1 allows .all()/.first()/.run() without bind
    },
  };
  return db;
}

function runSql(t, sql, args) {
  if (/INSERT INTO notify_rules/.test(sql)) {
    t.notify_rules.push({ id: args[0], user_id: args[1], place_id: args[2], opportunity_id: args[3], channel: args[4], min_advance_hours: args[5], enabled: 1, created_at: new Date().toISOString() });
    return { meta: { changes: 1 } };
  }
  if (/DELETE FROM notify_rules/.test(sql)) {
    const i = t.notify_rules.findIndex((r) => r.id === args[0] && r.user_id === args[1]);
    if (i < 0) return { meta: { changes: 0 } };
    t.notify_rules.splice(i, 1);
    return { meta: { changes: 1 } };
  }
  if (/UPDATE notify_rules SET enabled/.test(sql)) {
    const r = t.notify_rules.find((x) => x.id === args[0] && x.user_id === args[2]);
    if (!r) return { meta: { changes: 0 } };
    r.enabled = args[1];
    return { meta: { changes: 1 } };
  }
  if (/INSERT INTO notify_log/.test(sql)) {
    const key = `${args[0]}|${args[1]}`;
    if (t.notify_log.has(key)) return { meta: { changes: 0 } };
    t.notify_log.set(key, { delivered: 0, detail: null });
    return { meta: { changes: 1 } };
  }
  if (/UPDATE notify_log SET delivered = \?2/.test(sql) && !/web_push/.test(args[1])) {
    const entry = t.notify_log.get(`${args[0]}|${args[3]}`);
    if (entry) { entry.delivered = args[1]; entry.detail = args[2]; return { meta: { changes: 1 } }; }
    return { meta: { changes: 0 } };
  }
  if (/UPDATE notify_log SET delivered = 0, detail = \?2/.test(sql)) {
    const entry = t.notify_log.get(`${args[0]}|${args[2]}`);
    if (entry) { entry.delivered = 0; entry.detail = args[1]; return { meta: { changes: 1 } }; }
    return { meta: { changes: 0 } };
  }
  if (/INSERT INTO telegram_bindings/.test(sql) || /UPDATE telegram_bindings SET chat_id/.test(sql)) {
    const uid = /UPDATE telegram_bindings SET/.test(sql) ? args[0] : args[0];
    const chat = /UPDATE telegram_bindings SET/.test(sql) ? args[1] : null;
    const prev = t.telegram_bindings.get(uid) || { status: "none", token: null, chat_id: null };
    if (/UPDATE telegram_bindings SET/.test(sql)) t.telegram_bindings.set(uid, { ...prev, chat_id: chat, status: "active" });
    else t.telegram_bindings.set(uid, { ...prev, status: "pending", token: args[1] });
    return { meta: { changes: 1 } };
  }
  if (/INSERT INTO web_push_subscriptions/.test(sql)) {
    t.web_push_subscriptions.set(args[1], { user_id: args[0], p256dh: args[2], auth: args[3] });
    return { meta: { changes: 1 } };
  }
  if (/INSERT INTO users|DELETE FROM telegram_bindings/.test(sql)) return { meta: { changes: 0 } };
  return { meta: { changes: 0 } };
}

function makeEnv(opts = {}) {
  const store = new Map(Object.entries(opts.kv || {}));
  const kv = { get: async (k, type) => { const v = store.has(k) ? store.get(k) : null; return v !== null && type === "json" ? JSON.parse(v) : v; }, put: async (k, v) => { store.set(k, v); }, _store: store };
  const db = opts.db || makeMockD1();
  return { env: { EVALS: kv, DB: db, TG_BOT_TOKEN: "TEST:TOKEN", AUTH_SECRET: "test-secret" }, db };
}

function makeReq(path, opts = {}) {
  const headers = new Headers(opts.headers || {});
  return new Request(`https://chaselights.app/api/v1${path}`, { ...opts, headers });
}

async function mint(env, sub, level = "free") {
  return signJWT({ sub, name: "T", level, typ: "access", exp: Math.floor(Date.now() / 1000) + 600 }, env.AUTH_SECRET);
}

// ---------------------------------------------------------------- matcher
function subj(oid, days) { return { opportunity_id: oid, name_i18n: { "zh-TW": oid }, days }; }
const NOW = Date.parse("2026-11-10T12:00:00+08:00");

test("findNextWindow: earliest qualifying slot inside 24h honoring min advance", () => {
  const subjects = [
    subj("cloud-sea", [
      { local_date: "2026-11-11", verdict: "GUIDANCE_SATISFIED", hours: ["05:00", "06:00"] },
      { local_date: "2026-11-10", verdict: "GUIDANCE_SATISFIED", hours: ["20:00"] },
    ]),
  ];
  // advance 4h: 11/10 20:00 is +8h from 12:00 -> inside window; 11/11 05:00 is +17h -> also; earliest wins
  const w = findNextWindow(subjects, null, NOW, 4);
  assert.equal(windowKey(w), "2026-11-10T20:00");
  // advance 9h: 20:00 slot is now below advance -> next is 11/11 05:00
  const w2 = findNextWindow(subjects, null, NOW, 9);
  assert.equal(windowKey(w2), "2026-11-11T05:00");
  // advance 30h: everything out -> null
  assert.equal(findNextWindow(subjects, null, NOW, 30), null);
});

test("findNextWindow: opportunity filter, verdict filter, >24h exclusion", () => {
  const subjects = [
    subj("aurora", [{ local_date: "2026-11-11", verdict: "GUIDANCE_SATISFIED", hours: ["03:00"] }]), // 15h ahead
    subj("sunset", [{ local_date: "2026-11-11", verdict: "UNFAVORABLE", hours: ["17:00"] }, { local_date: "2026-11-10", verdict: "GUIDANCE_SATISFIED", hours: ["19:00"] }]),
  ];
  const w = findNextWindow(subjects, "sunset", NOW, 0);
  assert.equal(w.opportunity_id, "sunset");
  assert.equal(windowKey(w), "2026-11-10T19:00");
  // >24h slot (11/11 13:00 = +25h) is never matched
  const far = subj("far", [{ local_date: "2026-11-11", verdict: "GUIDANCE_SATISFIED", hours: ["13:00"] }]);
  assert.equal(findNextWindow([far], null, NOW, 0), null);
  assert.equal(findNextWindow(subjects, "nope", NOW, 0), null);
});

test("buildMessage: plain-language zh-TW line, no thresholds", () => {
  const rec = { place_id: "tw-001", name_i18n: { "zh-TW": "合歡山" }, subjects: [subj("cloud-sea", [])] };
  const msg = buildMessage(rec, { local_date: "2026-11-11", hour: "05:00", opportunity_id: "cloud-sea" });
  assert.ok(msg.includes("合歡山"));
  assert.ok(msg.includes("cloud-sea"));
  assert.ok(msg.includes("2026-11-11 05:00（GMT+8）"));
  for (const bad of ["threshold", "operator", "conditions"]) assert.ok(!msg.toLowerCase().includes(bad));
});

// ---------------------------------------------------------------- cron + dedupe + TG
function evalRec(placeId, hoursByDay, hourOverrides) {
  return {
    place_id: placeId,
    name_i18n: { "zh-TW": "七星潭" },
    subjects: [subj("star-trail", Object.entries(hoursByDay).map(([local_date, hours]) => ({ local_date, verdict: "GUIDANCE_SATISFIED", hours })))],
    ...(hourOverrides || {}),
  };
}

test("cron: match -> TG delivered once; second run same window deduped (no TG call)", async () => {
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(evalRec("tw-001", { "2026-11-10": ["22:00"] })) },
  });
  // rule + active binding
  db._tables.notify_rules.push({ id: "r1", user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "telegram", min_advance_hours: 0, enabled: 1 });
  db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "5048265539" });

  const calls = [];
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    calls.push(String(url));
    return new Response(JSON.stringify({ ok: true, result: { message_id: 7 } }), { status: 200 });
  };
  try {
    const s1 = await runNotifyCron(env, NOW);
    assert.equal(s1.matches, 1);
    assert.equal(s1.sent, 1);
    assert.ok(calls.some((c) => c.includes("api.telegram.org/botTEST:TOKEN/sendMessage")));
    const sentBody = s1; // second run must not re-send
    const s2 = await runNotifyCron(env, NOW);
    assert.equal(s2.skipped_dupe, 1);
    assert.equal(s2.sent, 0);
    const tgCalls2 = calls.filter((c) => c.includes("sendMessage")).length;
    // third run far later, same window -> still deduped
    await runNotifyCron(env, NOW + 2 * HOUR);
    assert.equal(calls.filter((c) => c.includes("sendMessage")).length, tgCalls2);
    const logEntry = db._tables.notify_log.get("r1|2026-11-10T22:00");
    assert.equal(logEntry.delivered, 1);
    assert.ok(sentBody);
  } finally {
    globalThis.fetch = origFetch;
  }
});

test("cron: TG failure recorded undelivered, no retry spam within window", async () => {
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(evalRec("tw-001", { "2026-11-10": ["22:00"] })) },
  });
  db._tables.notify_rules.push({ id: "r1", user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "telegram", min_advance_hours: 0, enabled: 1 });
  db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "5048265539" });
  const origFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response(JSON.stringify({ ok: false, description: "Forbidden: bot was blocked" }), { status: 403 });
  try {
    const s = await runNotifyCron(env, NOW);
    assert.equal(s.undelivered, 1);
    const logEntry = db._tables.notify_log.get("r1|2026-11-10T22:00");
    assert.equal(logEntry.delivered, 0);
    assert.ok(logEntry.detail.includes("Forbidden"));
  } finally {
    globalThis.fetch = origFetch;
  }
});

test("cron: rule without active binding is logged undelivered; web_push rule stays skeleton", async () => {
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(evalRec("tw-001", { "2026-11-10": ["22:00"] })) },
  });
  db._tables.notify_rules.push({ id: "r1", user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "telegram", min_advance_hours: 0, enabled: 1 });
  db._tables.notify_rules.push({ id: "r2", user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "web_push", min_advance_hours: 0, enabled: 1 });
  const s = await runNotifyCron(env, NOW);
  assert.equal(s.undelivered, 2);
  assert.equal(db._tables.notify_log.get("r1|2026-11-10T22:00").detail.includes("binding not active"), true);
  assert.equal(db._tables.notify_log.get("r2|2026-11-10T22:00").detail.includes("VAPID"), true);
});

test("telegram binding poll: /start <token> activates pending binding, offset advanced", async () => {
  const { env, db } = makeEnv({});
  db._tables.telegram_bindings.set("u1", { status: "pending", token: "tok-1" });
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    assert.ok(String(url).includes("getUpdates?offset=0"));
    return new Response(JSON.stringify({ ok: true, result: [{ update_id: 101, message: { text: "/start tok-1", chat: { id: 5048265539 } } }] }), { status: 200 });
  };
  try {
    const r = await pollTelegramBindings(env);
    assert.equal(r.bound, 1);
    assert.equal(db._tables.telegram_bindings.get("u1").status, "active");
    assert.equal(db._tables.telegram_bindings.get("u1").chat_id, "5048265539");
    assert.equal(await env.EVALS.get("v1:tg:offset"), "102"); // max update_id + 1
  } finally {
    globalThis.fetch = origFetch;
  }
});

// ---------------------------------------------------------------- endpoints
test("rules: JWT required; free tier capped at 3 with 402; paid beyond 3 ok", async () => {
  const { env, db } = makeEnv({});
  const anon = await worker.fetch(makeReq("/notify/rules", { method: "POST", body: JSON.stringify({ placeId: "tw-001" }) }), env, {});
  assert.equal(anon.status, 401);

  const free = await mint(env, "u-free", "free");
  const paid = await mint(env, "u-paid", "paid");
  const hdr = (t) => ({ "Content-Type": "application/json", Authorization: `Bearer ${t}` });

  for (let i = 1; i <= 3; i++) {
    const r = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr(free), body: JSON.stringify({ placeId: `tw-00${i}`, channel: "telegram", minAdvanceHours: 24 }) }), env, {});
    assert.equal(r.status, 200, `free rule ${i}`);
  }
  const over = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr(free), body: JSON.stringify({ placeId: "tw-099" }) }), env, {});
  assert.equal(over.status, 402);
  const overBody = await over.json();
  assert.equal(overBody.limit, 3);
  assert.equal(overBody.level, "free");

  for (let i = 1; i <= 4; i++) {
    const r = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr(paid), body: JSON.stringify({ placeId: `tw-00${i}` }) }), env, {});
    assert.equal(r.status, 200, `paid rule ${i}`);
  }
  assert.equal(db._tables.notify_rules.length, 7);
});

test("rules: validation (bad channel, bad advance), GET list, DELETE own/not-found", async () => {
  const { env } = makeEnv({});
  const t = await mint(env, "u1", "paid");
  const hdr = { "Content-Type": "application/json", Authorization: `Bearer ${t}` };

  const badCh = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-001", channel: "sms" }) }), env, {});
  assert.equal(badCh.status, 400);
  const badAdv = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-001", minAdvanceHours: 999 }) }), env, {});
  assert.equal(badAdv.status, 400);
  const noPlace = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: "{}" }), env, {});
  assert.equal(noPlace.status, 400);

  const created = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-001", opportunityId: "cloud-sea" }) }), env, {});
  const { rule } = await created.json();
  // CL-APP-03: default reminder channel is now APP push.
  assert.equal(rule.channel, "push");
  assert.equal(rule.minAdvanceHours, 24);

  const list = await worker.fetch(makeReq("/notify/rules", { headers: hdr }), env, {});
  const listBody = await list.json();
  assert.equal(listBody.rules.length, 1);
  assert.equal(listBody.rules[0].place_id, "tw-001");

  const wrongUser = await worker.fetch(makeReq(`/notify/rules/${rule.id}`, { method: "DELETE", headers: { Authorization: `Bearer ${await mint(env, "u2", "paid")}` } }), env, {});
  assert.equal(wrongUser.status, 404);
  const del = await worker.fetch(makeReq(`/notify/rules/${rule.id}`, { method: "DELETE", headers: hdr }), env, {});
  assert.equal((await del.json()).ok, true);

  const tgStart = await worker.fetch(makeReq("/notify/telegram/start", { method: "POST", headers: hdr }), env, {});
  const tgBody = await tgStart.json();
  assert.ok(tgBody.link.startsWith("https://t.me/chaselights_cm_bot?start="));
  const status = await worker.fetch(makeReq("/notify/telegram/status", { headers: hdr }), env, {});
  assert.equal((await status.json()).status, "pending");

  const wp = await worker.fetch(makeReq("/notify/web_push/subscribe", { method: "POST", headers: hdr, body: JSON.stringify({ endpoint: "https://push.example/abc", keys: { p256dh: "k", auth: "a" } }) }), env, {});
  assert.equal((await wp.json()).ok, true);
});

test("CL-UI-58: PATCH toggles rule enabled (own rule only; 401 anon; 400 non-bool; 404 unknown)", async () => {
  const { env } = makeEnv({});
  const t = await mint(env, "u1", "paid");
  const hdr = { "Content-Type": "application/json", Authorization: `Bearer ${t}` };

  const anon = await worker.fetch(makeReq("/notify/rules/r1", { method: "PATCH", headers: {}, body: JSON.stringify({ enabled: false }) }), env, {});
  assert.equal(anon.status, 401);

  const created = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-001", opportunityId: "cloud-sea" }) }), env, {});
  const { rule } = await created.json();

  const bad = await worker.fetch(makeReq(`/notify/rules/${rule.id}`, { method: "PATCH", headers: hdr, body: JSON.stringify({ enabled: "yes" }) }), env, {});
  assert.equal(bad.status, 400);

  const missing = await worker.fetch(makeReq("/notify/rules/does-not-exist", { method: "PATCH", headers: hdr, body: JSON.stringify({ enabled: false }) }), env, {});
  assert.equal(missing.status, 404);

  const off = await worker.fetch(makeReq(`/notify/rules/${rule.id}`, { method: "PATCH", headers: hdr, body: JSON.stringify({ enabled: false }) }), env, {});
  assert.equal(off.status, 200);
  const offBody = await off.json();
  assert.equal(offBody.ok, true);
  assert.equal(offBody.rule.enabled, false);

  // Disabled rules are skipped by the cron engine.
  const scan = await worker.fetch(makeReq("/notify/rules", { headers: hdr }), env, {});
  const listBody = await scan.json();
  assert.equal(listBody.rules[0].enabled, 0);

  const on = await worker.fetch(makeReq(`/notify/rules/${rule.id}`, { method: "PATCH", headers: hdr, body: JSON.stringify({ enabled: true }) }), env, {});
  assert.equal((await on.json()).rule.enabled, true);
});

test("scheduled handler exists and webpush skeleton generates P-256 keys", async () => {
  assert.equal(typeof worker.scheduled, "function");
  const keys = await generateVapidKeys();
  assert.ok(keys.privateKeyJwk);
  assert.equal(keys.publicKeyJwk.crv, "P-256");
  assert.ok(MATCH_WINDOW_H === 24);
});
