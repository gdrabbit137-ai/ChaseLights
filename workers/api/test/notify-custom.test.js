// CL-UI-99 tests: custom-conditions contract + engine. Kept in a SEPARATE file
// from notify.test.js so in-flight sibling work on that file cannot collide.
// Covers: validateCustomConditions boundaries, hourInWindow (midnight wrap),
// customHourMatches (per-parameter boundaries + honest missing-data), contract
// endpoints (custom POST / mutual exclusion / GET round-trip) and cron matching
// against KV rec.hourly (dedupe + lead minutes + custom_skipped).
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import {
  validateCustomConditions, parseCustomConditions, hourInWindow,
  customHourMatches, findNextCustomWindow, runNotifyCron, buildCustomMessage,
} from "../src/notify.js";
import { signJWT } from "../src/auth.js";

const HOUR = 3_600_000;
const NOW = Date.parse("2026-11-10T12:00:00+08:00");

// ---------------------------------------------------------------- validation
test("validateCustomConditions: absent/empty ok; boundaries; bad values 400-class", () => {
  assert.deepEqual(validateCustomConditions(null), { ok: true, cc: null });
  assert.deepEqual(validateCustomConditions(undefined), { ok: true, cc: null });
  assert.deepEqual(validateCustomConditions({}), { ok: true, cc: null });

  assert.equal(validateCustomConditions({ cloud_low_max: -1 }).ok, false);
  assert.equal(validateCustomConditions({ cloud_mid_max: 101 }).ok, false);
  assert.equal(validateCustomConditions({ cloud_high_max: 100 }).ok, true);
  assert.equal(validateCustomConditions({ precip_max_mmh: 200.5 }).ok, false);
  assert.equal(validateCustomConditions({ precip_max_mmh: 0 }).ok, true);
  assert.equal(validateCustomConditions({ visibility_min_km: 50.1 }).ok, false);
  assert.equal(validateCustomConditions({ wind_max_ms: -0.5 }).ok, false);
  assert.equal(validateCustomConditions({ lead_minutes: 4321 }).ok, false);
  assert.equal(validateCustomConditions({ lead_minutes: 60.5 }).ok, false);
  assert.equal(validateCustomConditions({ lead_minutes: 0 }).ok, true);
  assert.equal(validateCustomConditions({ window_start: "05:00" }).ok, false); // one-sided window
  assert.equal(validateCustomConditions({ window_end: "07:00", window_start: "25:00" }).ok, false);
  assert.equal(validateCustomConditions({ window_start: "22:00", window_end: "05:00" }).ok, true);
  assert.equal(validateCustomConditions([1]).ok, false);
  assert.equal(validateCustomConditions("x").ok, false);

  const r = validateCustomConditions({ cloud_low_max: 20, visibility_min_km: 10, window_start: "05:00", window_end: "07:00", lead_minutes: 90 });
  assert.deepEqual(r.cc, { cloud_low_max: 20, visibility_min_km: 10, window_start: "05:00", window_end: "07:00", lead_minutes: 90 });
});

// ---------------------------------------------------------------- matching
test("hourInWindow: normal, midnight wrap, no-window whole day, malformed hour", () => {
  assert.equal(hourInWindow("05:00", "05:00", "07:00"), true);
  assert.equal(hourInWindow("07:00", "05:00", "07:00"), true);
  assert.equal(hourInWindow("07:01", "05:00", "07:00"), false);
  assert.equal(hourInWindow("23:00", "22:00", "05:00"), true); // wrap
  assert.equal(hourInWindow("03:00", "22:00", "05:00"), true); // wrap
  assert.equal(hourInWindow("12:00", "22:00", "05:00"), false); // wrap gap
  assert.equal(hourInWindow("12:00", null, null), true); // no window = any hour
  assert.equal(hourInWindow("24:00", null, null), false);
  assert.equal(hourInWindow(5, null, null), false);
});

test("customHourMatches: per-parameter boundaries + lenient defaults + honest missing data", () => {
  const v = { cloud_low: 20, cloud_mid: 40, cloud_high: 60, precipitation: 0.5, visibility: 10, wind: 4 };
  const all = { cloud_low_max: 20, cloud_mid_max: 40, cloud_high_max: 60, precip_max_mmh: 0.5, visibility_min_km: 10, wind_max_ms: 4 };
  assert.equal(customHourMatches(v, all), true); // every boundary inclusive

  assert.equal(customHourMatches({ ...v, cloud_low: 20.1 }, all), false); // low cloud over
  assert.equal(customHourMatches({ ...v, cloud_mid: 40.1 }, all), false);
  assert.equal(customHourMatches({ ...v, cloud_high: 60.1 }, all), false);
  assert.equal(customHourMatches({ ...v, precipitation: 0.51 }, all), false);
  assert.equal(customHourMatches({ ...v, visibility: 9.9 }, all), false);
  assert.equal(customHourMatches({ ...v, wind: 4.01 }, all), false);

  // lenient defaults never reject even when the value is missing
  assert.equal(customHourMatches({ precipitation: 0, wind: 2 }, { cloud_low_max: 100, cloud_mid_max: 100, cloud_high_max: 100, visibility_min_km: 0 }), true);
  // a set constraint with MISSING data fails the hour honestly
  assert.equal(customHourMatches({ precipitation: 0 }, { cloud_low_max: 50 }), false);
  assert.equal(customHourMatches(null, { wind_max_ms: 5 }), false);
  // unset params never constrain
  assert.equal(customHourMatches({}, {}), true);
  assert.equal(customHourMatches({}, null), false);
});

test("findNextCustomWindow: earliest inside 24h honoring lead minutes + window", () => {
  const hourly = [
    { local_date: "2026-11-10", hour: "20:00", values: { wind: 1 } },
    { local_date: "2026-11-11", hour: "05:00", values: { wind: 1 } },
    { local_date: "2026-11-11", hour: "13:00", values: { wind: 1 } }, // +25h -> outside
  ];
  const cc = { wind_max_ms: 2 };
  // lead 4h: 20:00 (+8h) earliest
  assert.equal(findNextCustomWindow(hourly, cc, NOW, 240).hour, "20:00");
  // lead 9h: skips 20:00, takes 11/11 05:00 (+17h)
  assert.equal(findNextCustomWindow(hourly, cc, NOW, 540).hour, "05:00");
  // lead 30h: everything out
  assert.equal(findNextCustomWindow(hourly, cc, NOW, 1800), null);
  // window filter excludes 20:00
  assert.equal(findNextCustomWindow(hourly, { ...cc, window_start: "04:00", window_end: "06:00" }, NOW, 0).hour, "05:00");
  // midnight-wrap window excludes both day hours
  assert.equal(findNextCustomWindow(hourly, { ...cc, window_start: "22:00", window_end: "03:00" }, NOW, 0), null);
  // no conditions set -> matches on window alone
  assert.equal(findNextCustomWindow(hourly, {}, NOW, 0).hour, "20:00");
  assert.equal(findNextCustomWindow([], cc, NOW, 0), null);
});

// ---------------------------------------------------------------- cron + contract
function makeMockD1() {
  const t = { notify_rules: [], notify_log: new Map(), telegram_bindings: new Map(), users: new Map() };
  const db = {
    _tables: t,
    prepare(sql) {
      const runner = (args) => ({
        run: async () => runSql(t, sql, args),
        first: async () => {
          const cm = sql.match(/COUNT\(\*\) AS n FROM notify_rules WHERE user_id = \?1/);
          if (cm) return { n: t.notify_rules.filter((r) => r.user_id === args[0]).length };
          const lm = sql.match(/SELECT level FROM users/);
          if (lm) { const u = t.users.get(args[0]); return u ? { level: u.level } : null; }
          const bm = sql.match(/SELECT (chat_id, status|status, chat_id) FROM telegram_bindings/);
          if (bm) { const b = t.telegram_bindings.get(args[0]); return b ? { chat_id: b.chat_id, status: b.status } : null; }
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
      return { ...runner([]), bind: (...a) => runner(a) };
    },
  };
  return db;
}

function runSql(t, sql, args) {
  if (/INSERT INTO notify_rules/.test(sql)) {
    t.notify_rules.push({ id: args[0], user_id: args[1], place_id: args[2], opportunity_id: args[3], channel: args[4], min_advance_hours: args[5], custom_conditions: args[6], enabled: 1, created_at: new Date().toISOString() });
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
  if (/INSERT INTO users/.test(sql)) return { meta: { changes: 0 } };
  return { meta: { changes: 0 } };
}

function makeEnv(opts = {}) {
  const store = new Map(Object.entries(opts.kv || {}));
  const kv = { get: async (k, type) => { const v = store.has(k) ? store.get(k) : null; return v !== null && type === "json" ? JSON.parse(v) : v; }, put: async (k, v) => { store.set(k, v); }, _store: store };
  const db = opts.db || makeMockD1();
  return { env: { EVALS: kv, DB: db, TG_BOT_TOKEN: "TEST:TOKEN", AUTH_SECRET: "test-secret", FCM_SERVICE_ACCOUNT_JSON: JSON.stringify({ project_id: "t" }) }, db };
}

function makeReq(path, opts = {}) {
  const headers = new Headers(opts.headers || {});
  return new Request(`https://chaselights.app/api/v1${path}`, { ...opts, headers });
}

async function mint(env, sub, level = "paid") {
  return signJWT({ sub, name: "T", level, typ: "access", exp: Math.floor(Date.now() / 1000) + 600 }, env.AUTH_SECRET);
}

function hourlyRec(placeId, rows) {
  return { place_id: placeId, name_i18n: { "zh-TW": "合歡山" }, subjects: [], hourly: rows };
}

test("contract: POST custom rule round-trips; mutual exclusion; GET returns parsed cc", async () => {
  const { env, db } = makeEnv({});
  const t = await mint(env, "u1");
  const hdr = { "Content-Type": "application/json", Authorization: `Bearer ${t}` };

  const cc = { cloud_low_max: 20, visibility_min_km: 10, window_start: "05:00", window_end: "07:00", lead_minutes: 90 };
  const created = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-001", customConditions: cc }) }), env, {});
  assert.equal(created.status, 200);
  const { rule } = await created.json();
  assert.equal(rule.opportunityId, null);
  assert.deepEqual(rule.customConditions, cc);

  const bad = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-001", customConditions: { cloud_low_max: 200 } }) }), env, {});
  assert.equal(bad.status, 400);
  const both = await worker.fetch(makeReq("/notify/rules", { method: "POST", headers: hdr, body: JSON.stringify({ placeId: "tw-001", opportunityId: "cloud-sea", customConditions: cc }) }), env, {});
  assert.equal(both.status, 400);
  assert.match((await both.json()).error, /mutually exclusive/);

  const list = await worker.fetch(makeReq("/notify/rules", { headers: hdr }), env, {});
  const body = await list.json();
  assert.equal(body.rules.length, 1);
  assert.deepEqual(body.rules[0].custom_conditions, cc);

  // stored row keeps the JSON string for the cron engine
  assert.equal(typeof db._tables.notify_rules[0].custom_conditions, "string");
  const parsed = parseCustomConditions(db._tables.notify_rules[0].custom_conditions);
  assert.deepEqual(parsed, cc);
  assert.equal(parseCustomConditions("not-json"), null);
  assert.equal(parseCustomConditions(undefined), null);
});

test("cron custom mode: matches KV hourly vs conditions, dedupes, custom message, no thresholds", async () => {
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(hourlyRec("tw-001", [
      { local_date: "2026-11-10", hour: "20:00", values: { cloud_low: 90, visibility: 2, wind: 1 } },
      { local_date: "2026-11-11", hour: "05:00", values: { cloud_low: 10, visibility: 15, wind: 1 } },
    ])) },
  });
  db._tables.notify_rules.push({
    id: "r1", user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "telegram",
    min_advance_hours: 0, enabled: 1, custom_conditions: JSON.stringify({ cloud_low_max: 20, visibility_min_km: 10 }),
  });
  db._tables.notify_rules.push({
    id: "r2", user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "telegram",
    min_advance_hours: 0, enabled: 1, custom_conditions: JSON.stringify({ cloud_low_max: 20, visibility_min_km: 10, window_start: "04:00", window_end: "06:00" }),
  });
  db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });

  const calls = [];
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    calls.push({ url: String(url), init });
    return new Response(JSON.stringify({ ok: true, result: { message_id: 7 } }), { status: 200 });
  };
  try {
    const s = await runNotifyCron(env, NOW);
    assert.equal(s.matches, 2);
    assert.equal(s.sent, 2);
    assert.equal(db._tables.notify_log.get("r1|2026-11-11T05:00").delivered, 1);
    const tgBody = JSON.parse(calls.find((c) => c.url.includes("sendMessage")).init.body);
    assert.ok(tgBody.text.includes("自訂條件"));
    assert.ok(tgBody.text.includes("2026-11-11 05:00（GMT+8）"));
    for (const bad of ["threshold", "operator", "conditions"]) assert.ok(!tgBody.text.toLowerCase().includes(bad));
    // second run deduped
    const s2 = await runNotifyCron(env, NOW);
    assert.equal(s2.skipped_dupe, 2);
    assert.equal(s2.sent, 0);
  } finally {
    globalThis.fetch = origFetch;
  }
});

test("cron custom mode: lead minutes honored; no hourly data skips honestly; legacy rules untouched", async () => {
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(hourlyRec("tw-001", [
      { local_date: "2026-11-10", hour: "20:00", values: { wind: 1 } },
      { local_date: "2026-11-11", hour: "05:00", values: { wind: 1 } },
    ])) },
  });
  // lead 9h -> 20:00 (+8h) too early, takes 05:00 next day
  db._tables.notify_rules.push({
    id: "r-lead", user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "telegram",
    min_advance_hours: 0, enabled: 1, custom_conditions: JSON.stringify({ wind_max_ms: 2, lead_minutes: 540 }),
  });
  // rule with custom_conditions but KV record without hourly -> custom_skipped
  db._tables.notify_rules.push({
    id: "r-nohourly", user_id: "u2", place_id: "tw-002", opportunity_id: null, channel: "telegram",
    min_advance_hours: 0, enabled: 1, custom_conditions: JSON.stringify({ wind_max_ms: 2 }),
  });
  // legacy subject rule on the same place keeps working (mode independence)
  db._tables.notify_rules.push({
    id: "r-legacy", user_id: "u3", place_id: "tw-001", opportunity_id: "star", channel: "telegram",
    min_advance_hours: 0, enabled: 1, custom_conditions: null,
  });
  const legacyRec = hourlyRec("tw-001", [
    { local_date: "2026-11-10", hour: "20:00", values: { wind: 1 } },
    { local_date: "2026-11-11", hour: "05:00", values: { wind: 1 } },
  ]);
  legacyRec.subjects = [{ opportunity_id: "star", name_i18n: { "zh-TW": "星軌" }, days: [{ local_date: "2026-11-10", verdict: "GUIDANCE_SATISFIED", hours: ["20:00"] }] }];
  await env.EVALS.put("v1:evals:tw-001", JSON.stringify(legacyRec));
  await env.EVALS.put("v1:evals:tw-002", JSON.stringify({ place_id: "tw-002", name_i18n: {}, subjects: [] }));

  const s = await runNotifyCron(env, NOW);
  assert.equal(s.custom_skipped, 1);
  assert.equal(s.matches, 2);
  assert.ok(db._tables.notify_log.has("r-lead|2026-11-11T05:00"));
  assert.ok(db._tables.notify_log.has("r-legacy|2026-11-10T20:00"));
  assert.ok(!db._tables.notify_log.has("r-nohourly|2026-11-10T20:00"));
});

test("buildCustomMessage: place + custom-mode wording, no thresholds echoed", () => {
  const msg = buildCustomMessage({ place_id: "tw-001", name_i18n: { "zh-TW": "合歡山" } }, { local_date: "2026-11-11", hour: "05:00" });
  assert.ok(msg.includes("合歡山"));
  assert.ok(msg.includes("自訂條件"));
  assert.ok(msg.includes("2026-11-11 05:00（GMT+8）"));
  for (const bad of ["threshold", "operator", "conditions"]) assert.ok(!msg.toLowerCase().includes(bad));
});
