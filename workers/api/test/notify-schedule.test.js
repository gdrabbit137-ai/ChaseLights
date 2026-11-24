// CL-UX-01 Part B tests: schedules (bucket gate, cadence, forecast horizon,
// tier/target filters, silence, consolidation) + defaults endpoints.
// Own mock D1 (same stub style as notify.test.js) so sibling work on those
// files can never collide with this one.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import {
  runNotifyCron, scheduleGate, effectiveRule, isLegacySchedule, findScheduledWindow,
  validateScheduleFields, buildScheduleBatchMessage, tzClock,
} from "../src/notify.js";
import { signJWT } from "../src/auth.js";

// ---------------------------------------------------------------- mock D1
function makeMockD1() {
  const t = {
    notify_rules: [], notify_log: new Map(), telegram_bindings: new Map(),
    push_tokens: [], notify_defaults: new Map(), users: new Map(),
  };
  const db = {
    _tables: t,
    prepare(sql) {
      const runner = (args) => ({
        run: async () => runSql(t, sql, args),
        first: async () => {
          if (/COUNT\(\*\) AS n FROM notify_rules WHERE user_id = \?1/.test(sql)) {
            return { n: t.notify_rules.filter((r) => r.user_id === args[0]).length };
          }
          if (/SELECT level FROM users/.test(sql)) {
            const u = t.users.get(args[0]);
            return u ? { level: u.level } : null;
          }
          if (/SELECT chat_id, status FROM telegram_bindings/.test(sql)) {
            const b = t.telegram_bindings.get(args[0]);
            return b ? { chat_id: b.chat_id, status: b.status } : null;
          }
          if (/FROM notify_defaults WHERE user_id = \?1/.test(sql)) {
            return t.notify_defaults.get(args[0]) || null;
          }
          return null;
        },
        all: async () => {
          if (/FROM notify_rules r WHERE r\.enabled = 1/.test(sql)) {
            return { results: t.notify_rules.filter((r) => r.enabled === 1) };
          }
          if (/FROM notify_rules WHERE user_id = \?1 ORDER BY created_at DESC/.test(sql)) {
            return { results: t.notify_rules.filter((r) => r.user_id === args[0]) };
          }
          if (/FROM notify_defaults/.test(sql)) {
            return { results: [...t.notify_defaults.values()] };
          }
          if (/SELECT token FROM push_tokens WHERE user_device_id = \?1/.test(sql)) {
            return { results: t.push_tokens.filter((p) => p.user_device_id === args[0]).map((p) => ({ token: p.token })) };
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
  if (/INSERT INTO notify_rules/.test(sql)) {
    t.notify_rules.push({
      id: args[0], user_id: args[1], place_id: args[2], opportunity_id: args[3], channel: args[4],
      min_advance_hours: args[5], custom_conditions: args[6],
      schedule_mode: args[7], schedule_every_n: args[8], schedule_weekdays: args[9], send_time: args[10],
      lead_days: args[11], target_weekdays: args[12], min_tier: args[13], tz: args[14],
      last_sent_at: null, enabled: 1, created_at: new Date().toISOString(),
    });
    return { meta: { changes: 1 } };
  }
  if (/INSERT INTO notify_log/.test(sql)) {
    const key = `${args[0]}|${args[1]}`;
    if (t.notify_log.has(key)) return { meta: { changes: 0 } };
    t.notify_log.set(key, {
      rule_id: args[0], window_start: args[1], user_id: args[2], place_id: args[3],
      opportunity_id: args[4], channel: args[5], batch_id: args[6], delivered: 0, detail: null,
    });
    return { meta: { changes: 1 } };
  }
  if (/UPDATE notify_log SET delivered = \?2/.test(sql)) {
    const entry = t.notify_log.get(`${args[0]}|${args[3]}`);
    if (!entry) return { meta: { changes: 0 } };
    entry.delivered = args[1];
    entry.detail = args[2];
    return { meta: { changes: 1 } };
  }
  if (/UPDATE notify_rules SET last_sent_at/.test(sql)) {
    const r = t.notify_rules.find((x) => x.id === args[0]);
    if (!r) return { meta: { changes: 0 } };
    r.last_sent_at = args[1];
    return { meta: { changes: 1 } };
  }
  if (/UPDATE notify_rules SET enabled/.test(sql)) {
    const r = t.notify_rules.find((x) => x.id === args[0] && x.user_id === args[2]);
    if (!r) return { meta: { changes: 0 } };
    r.enabled = args[1];
    return { meta: { changes: 1 } };
  }
  if (/DELETE FROM notify_rules/.test(sql)) {
    const i = t.notify_rules.findIndex((r) => r.id === args[0] && r.user_id === args[1]);
    if (i < 0) return { meta: { changes: 0 } };
    t.notify_rules.splice(i, 1);
    return { meta: { changes: 1 } };
  }
  if (/INSERT INTO notify_defaults/.test(sql)) {
    t.notify_defaults.set(args[0], {
      user_id: args[0], schedule_mode: args[1], schedule_every_n: args[2], schedule_weekdays: args[3],
      send_time: args[4], lead_days: args[5], target_weekdays: args[6], min_tier: args[7],
      channel: args[8], tz: args[9],
    });
    return { meta: { changes: 1 } };
  }
  return { meta: { changes: 0 } };
}

function makeEnv(opts = {}) {
  const store = new Map(Object.entries(opts.kv || {}));
  const kv = {
    get: async (k, type) => { const v = store.has(k) ? store.get(k) : null; return v !== null && type === "json" ? JSON.parse(v) : v; },
    put: async (k, v) => { store.set(k, v); },
    _store: store,
  };
  const db = opts.db || makeMockD1();
  return { env: { EVALS: kv, DB: db, TG_BOT_TOKEN: "TEST:TOKEN", AUTH_SECRET: "test-secret" }, db };
}

// Runs the cron with a stubbed fetch; returns {summary, calls, sends}.
async function cronWith(env, nowMs, calls = []) {
  const orig = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    const u = String(url);
    calls.push({ url: u, init });
    if (u.includes("getUpdates")) return new Response(JSON.stringify({ ok: true, result: [] }), { status: 200 });
    if (u.includes("sendMessage")) return new Response(JSON.stringify({ ok: true, result: { message_id: 1 } }), { status: 200 });
    return new Response(JSON.stringify({ ok: true }), { status: 200 });
  };
  try {
    const summary = await runNotifyCron(env, nowMs);
    return { summary, calls, sends: calls.filter((c) => c.url.includes("sendMessage")) };
  } finally {
    globalThis.fetch = orig;
  }
}

function makeReq(path, opts = {}) {
  const headers = new Headers(opts.headers || {});
  return new Request(`https://chaselights.app/api/v1${path}`, { ...opts, headers });
}

async function mint(env, sub, level = "paid") {
  return signJWT({ sub, name: "T", level, typ: "access", exp: Math.floor(Date.now() / 1000) + 600 }, env.AUTH_SECRET);
}

// ---------------------------------------------------------------- fixtures
const HOUR = 3_600_000;
const T = (iso) => Date.parse(iso);

const ruleBase = (over = {}) => ({
  user_id: "u1", place_id: "tw-001", opportunity_id: null, channel: "telegram",
  min_advance_hours: 24, custom_conditions: null, enabled: 1,
  schedule_mode: null, schedule_every_n: null, schedule_weekdays: null, send_time: null,
  lead_days: null, target_weekdays: null, min_tier: null, tz: null, last_sent_at: null,
  ...over,
});

function gday(local_date, hours, extra = {}) {
  return { local_date, verdict: "GUIDANCE_SATISFIED", hours, ...extra };
}

function subjRec(placeId, name, days) {
  return {
    place_id: placeId,
    name_i18n: { "zh-TW": name },
    subjects: [{ opportunity_id: "cloud-sea", name_i18n: { "zh-TW": "雲海" }, days }],
  };
}

// ---------------------------------------------------------------- unit: gate
test("scheduleGate: non-round 20:15 is due from 20:15 until the local day ends", () => {
  const eff = effectiveRule(ruleBase({ schedule_mode: "weekdays", schedule_weekdays: "0,1,2,3,4,5,6", send_time: "20:15", tz: "Asia/Taipei" }), null);
  assert.equal(scheduleGate(eff, T("2026-11-10T20:00:00+08:00")).due, false);
  const g = scheduleGate(eff, T("2026-11-10T20:15:00+08:00"));
  assert.equal(g.due, true);
  assert.equal(g.bucket, "2026-11-10");
  assert.equal(scheduleGate(eff, T("2026-11-10T20:30:00+08:00")).bucket, "2026-11-10");
  assert.equal(scheduleGate(eff, T("2026-11-10T23:59:00+08:00")).due, true); // missed tick catches up
  assert.equal(scheduleGate(eff, T("2026-11-11T20:14:00+08:00")).due, false); // next day, before time
});

test("scheduleGate: weekdays + every_n_days cadence", () => {
  const wd = effectiveRule(ruleBase({ schedule_mode: "weekdays", schedule_weekdays: "4,5", send_time: "08:00", tz: "Asia/Taipei" }), null);
  assert.equal(scheduleGate(wd, T("2026-11-10T09:00:00+08:00")).due, false); // Tuesday
  assert.equal(scheduleGate(wd, T("2026-11-12T07:59:00+08:00")).due, false); // Thursday, too early
  assert.equal(scheduleGate(wd, T("2026-11-12T08:00:00+08:00")).due, true);

  const ev = effectiveRule(ruleBase({ schedule_mode: "every_n_days", schedule_every_n: 2, send_time: "07:00", tz: "Asia/Taipei" }), null);
  assert.equal(scheduleGate(ev, T("2026-11-10T07:30:00+08:00")).due, true); // first send
  const withLast = { ...ev, last_sent_at: new Date(T("2026-11-10T07:30:00+08:00")).toISOString() };
  assert.equal(scheduleGate(withLast, T("2026-11-11T07:30:00+08:00")).due, false); // 1 day < 2
  assert.equal(scheduleGate(withLast, T("2026-11-12T07:30:00+08:00")).due, true); // 2 days
});

test("validateScheduleFields: contract bounds (mode/every_n/weekdays/send_time/lead/tier/tz)", () => {
  assert.deepEqual(validateScheduleFields({}).fields, {});
  assert.equal(validateScheduleFields({ scheduleMode: "daily" }).ok, false);
  assert.equal(validateScheduleFields({ scheduleMode: "weekdays", scheduleEveryN: 0 }).ok, false);
  assert.equal(validateScheduleFields({ scheduleEveryN: 8 }).ok, false);
  assert.equal(validateScheduleFields({ scheduleWeekdays: "4,9" }).ok, false);
  assert.equal(validateScheduleFields({ scheduleWeekdays: "4,4,5" }).fields.schedule_weekdays, "4,5");
  assert.equal(validateScheduleFields({ sendTime: "20:15" }).fields.send_time, "20:15");
  assert.equal(validateScheduleFields({ sendTime: "8:00" }).ok, false);
  assert.equal(validateScheduleFields({ leadDays: 0 }).ok, false);
  assert.equal(validateScheduleFields({ leadDays: 8 }).ok, false);
  assert.equal(validateScheduleFields({ minTier: "maybe" }).ok, false);
  assert.equal(validateScheduleFields({ minTier: "shootable" }).fields.min_tier, "shootable");
  assert.equal(validateScheduleFields({ tz: "Mars/Olympus" }).ok, false);
  assert.equal(validateScheduleFields({ tz: "Asia/Taipei" }).ok, true);
  assert.equal(validateScheduleFields({ targetWeekdays: "0,6" }).fields.target_weekdays, "0,6");
});

test("legacy detection: no schedule_mode and no send_time keeps the old path", () => {
  assert.equal(isLegacySchedule(effectiveRule(ruleBase(), null)), true);
  // a stray tz/min_tier default must never silently disable a working rule
  assert.equal(isLegacySchedule(effectiveRule(ruleBase(), { tz: "Asia/Tokyo", min_tier: "shootable" })), true);
  assert.equal(isLegacySchedule(effectiveRule(ruleBase({ send_time: "08:00" }), null)), false);
  assert.equal(isLegacySchedule(effectiveRule(ruleBase(), { schedule_mode: "weekdays", send_time: "08:00", schedule_weekdays: "1" })), false);
});

test("findScheduledWindow: lead_days horizon + target_weekdays + min_tier", () => {
  const now = T("2026-11-10T09:00:00+08:00");
  const rec = subjRec("tw-001", "合歡山", [gday("2026-11-20", ["05:00"])]);
  const eff = effectiveRule(ruleBase({ schedule_mode: "weekdays", send_time: "08:00", lead_days: 2 }), null);
  assert.equal(findScheduledWindow(rec, eff, null, now), null, "beyond the lead window -> silence");

  const near = subjRec("tw-001", "合歡山", [gday("2026-11-11", ["05:00"])]);
  assert.equal(findScheduledWindow(near, eff, null, now).local_date, "2026-11-11");

  const sundayOnly = effectiveRule(ruleBase({ schedule_mode: "weekdays", send_time: "08:00", lead_days: 3, target_weekdays: "0" }), null);
  assert.equal(findScheduledWindow(near, sundayOnly, null, now), null, "11/11 is a Wednesday");
  const sunday = subjRec("tw-001", "合歡山", [gday("2026-11-15", ["05:00"])]);
  const wide = effectiveRule(ruleBase({ schedule_mode: "weekdays", send_time: "08:00", lead_days: 7, target_weekdays: "0" }), null);
  assert.equal(findScheduledWindow(sunday, wide, null, now).local_date, "2026-11-15");

  const shootOnly = subjRec("tw-001", "合歡山", [gday("2026-11-11", ["05:00"], { tier: "shootable" })]);
  const recOnly = effectiveRule(ruleBase({ schedule_mode: "weekdays", send_time: "08:00", lead_days: 2, min_tier: "recommend" }), null);
  assert.equal(findScheduledWindow(shootOnly, recOnly, null, now), null, "shootable-only is below 'recommend'");
  const shootOk = effectiveRule(ruleBase({ schedule_mode: "weekdays", send_time: "08:00", lead_days: 2, min_tier: "shootable" }), null);
  assert.ok(findScheduledWindow(shootOnly, shootOk, null, now));
});

test("buildScheduleBatchMessage: summary title first, one line per rule", () => {
  const b = buildScheduleBatchMessage([
    { placeName: "合歡山", subjectName: "雲海", local_date: "2026-11-11", hour: "05:00" },
    { placeName: "七星潭", subjectName: "星軌", local_date: "2026-11-11", hour: "21:00" },
  ]);
  assert.equal(b.title, "2 個追蹤景點達標");
  assert.equal(b.lines.length, 2);
  assert.ok(b.text.split("\n")[1] === "2 個追蹤景點達標");
  assert.ok(b.lines[0].includes("合歡山") && b.lines[0].includes("2026-11-11 05:00"));
});

// ---------------------------------------------------------------- cron: bucket
test("cron: send_time 20:15 fires once at 20:15 and once more never (bucket), not at 20:00", async () => {
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(subjRec("tw-001", "合歡山", [gday("2026-11-11", ["05:00"])])) },
  });
  db._tables.notify_rules.push(ruleBase({
    id: "r1", schedule_mode: "weekdays", schedule_weekdays: "0,1,2,3,4,5,6",
    send_time: "20:15", lead_days: 2, tz: "Asia/Taipei",
  }));
  db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });

  const calls = [];
  const early = await cronWith(env, T("2026-11-10T20:00:00+08:00"), calls);
  assert.equal(early.sends.length, 0, "20:00 tick is before 20:15");
  assert.equal(early.summary.schedule_not_due, 1);
  assert.equal(db._tables.notify_log.size, 0);

  const onTime = await cronWith(env, T("2026-11-10T20:15:00+08:00"), calls);
  assert.equal(onTime.summary.sent, 1);
  assert.equal(onTime.summary.messages_sent, 1);
  assert.equal(onTime.sends.length, 1);
  assert.equal(db._tables.notify_log.get("r1|2026-11-10").delivered, 1);
  assert.ok(db._tables.notify_rules[0].last_sent_at, "last_sent_at stamped on success");

  const later = await cronWith(env, T("2026-11-10T20:30:00+08:00"), calls);
  assert.equal(later.summary.sent, 0);
  assert.equal(later.summary.skipped_dupe, 1);
  assert.equal(calls.filter((c) => c.url.includes("sendMessage")).length, 1, "still exactly one message");
});

test("cron: weekdays mode fires on a listed weekday only", async () => {
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(subjRec("tw-001", "合歡山", [gday("2026-11-13", ["05:00"])])) },
  });
  db._tables.notify_rules.push(ruleBase({
    id: "r1", schedule_mode: "weekdays", schedule_weekdays: "4,5", send_time: "08:00",
    lead_days: 3, tz: "Asia/Taipei",
  }));
  db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });

  const calls = [];
  const tue = await cronWith(env, T("2026-11-10T09:00:00+08:00"), calls);
  assert.equal(tue.sends.length, 0, "Tuesday is not listed");
  assert.equal(tue.summary.schedule_not_due, 1);

  const thu = await cronWith(env, T("2026-11-12T09:00:00+08:00"), calls);
  assert.equal(thu.summary.sent, 1);
  assert.equal(thu.sends.length, 1);
  assert.ok(db._tables.notify_log.has("r1|2026-11-12"));
});

test("cron: every_n_days — first fire when last_sent_at is NULL, then cadence-gated", async () => {
  const { env, db } = makeEnv({
    kv: {
      "v1:evals:tw-001": JSON.stringify(subjRec("tw-001", "合歡山", [
        gday("2026-11-10", ["18:00"]), gday("2026-11-11", ["18:00"]), gday("2026-11-12", ["18:00"]),
      ])),
    },
  });
  db._tables.notify_rules.push(ruleBase({
    id: "r1", schedule_mode: "every_n_days", schedule_every_n: 2, send_time: "07:00",
    lead_days: 3, tz: "Asia/Taipei",
  }));
  db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });

  const calls = [];
  const first = await cronWith(env, T("2026-11-10T08:00:00+08:00"), calls);
  assert.equal(first.summary.sent, 1);
  assert.ok(db._tables.notify_log.has("r1|2026-11-10"));

  const next = await cronWith(env, T("2026-11-11T08:00:00+08:00"), calls);
  assert.equal(next.summary.sent, 0, "only 1 day since the last send");
  assert.equal(next.summary.schedule_not_due, 1);
  assert.ok(!db._tables.notify_log.has("r1|2026-11-11"));

  const third = await cronWith(env, T("2026-11-12T08:00:00+08:00"), calls);
  assert.equal(third.summary.sent, 1, "2 days later: due again");
  assert.ok(db._tables.notify_log.has("r1|2026-11-12"));
  assert.equal(calls.filter((c) => c.url.includes("sendMessage")).length, 2);
});

// ---------------------------------------------------------------- cron: silence
test("cron: silence — no window inside lead_days / target_weekdays => no push, no log row", async () => {
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(subjRec("tw-001", "合歡山", [gday("2026-11-20", ["05:00"])])) },
  });
  db._tables.notify_rules.push(ruleBase({
    id: "r-far", schedule_mode: "weekdays", schedule_weekdays: "2", send_time: "08:00",
    lead_days: 2, tz: "Asia/Taipei",
  }));
  db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });
  const calls = [];
  const s = await cronWith(env, T("2026-11-10T09:00:00+08:00"), calls); // Tuesday, listed
  assert.equal(s.summary.silent_skipped, 1);
  assert.equal(s.sends.length, 0);
  assert.equal(db._tables.notify_log.size, 0);

  // target_weekdays excludes the only qualifying day (11/11 is a Wednesday)
  const g = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(subjRec("tw-001", "合歡山", [gday("2026-11-11", ["05:00"])])) },
  });
  g.db._tables.notify_rules.push(ruleBase({
    id: "r-target", schedule_mode: "weekdays", schedule_weekdays: "2", send_time: "08:00",
    lead_days: 3, target_weekdays: "0", tz: "Asia/Taipei",
  }));
  g.db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });
  const calls2 = [];
  const s2 = await cronWith(g.env, T("2026-11-10T09:00:00+08:00"), calls2);
  assert.equal(s2.summary.silent_skipped, 1);
  assert.equal(calls2.filter((c) => c.url.includes("sendMessage")).length, 0);
  assert.equal(g.db._tables.notify_log.size, 0);
});

test("cron: min_tier='recommend' excludes a shootable-only window (shootable accepts it)", async () => {
  const kv = { "v1:evals:tw-001": JSON.stringify(subjRec("tw-001", "合歡山", [gday("2026-11-11", ["05:00"], { tier: "shootable" })])) };

  const strict = makeEnv({ kv });
  strict.db._tables.notify_rules.push(ruleBase({
    id: "r-rec", schedule_mode: "weekdays", schedule_weekdays: "2,3", send_time: "08:00",
    lead_days: 2, min_tier: "recommend", tz: "Asia/Taipei",
  }));
  strict.db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });
  const s1 = await cronWith(strict.env, T("2026-11-10T09:00:00+08:00"), []);
  assert.equal(s1.summary.silent_skipped, 1);
  assert.equal(strict.db._tables.notify_log.size, 0);

  const loose = makeEnv({ kv });
  loose.db._tables.notify_rules.push(ruleBase({
    id: "r-shoot", schedule_mode: "weekdays", schedule_weekdays: "2,3", send_time: "08:00",
    lead_days: 2, min_tier: "shootable", tz: "Asia/Taipei",
  }));
  loose.db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });
  const s2 = await cronWith(loose.env, T("2026-11-10T09:00:00+08:00"), []);
  assert.equal(s2.summary.sent, 1);
  assert.ok(loose.db._tables.notify_log.has("r-shoot|2026-11-10"));
});

// ---------------------------------------------------------------- consolidation
test("cron: three due rules for one user => ONE message, three lines, one shared batch_id", async () => {
  const { env, db } = makeEnv({
    kv: {
      "v1:evals:tw-001": JSON.stringify(subjRec("tw-001", "合歡山", [gday("2026-11-11", ["05:00"])])),
      "v1:evals:tw-002": JSON.stringify(subjRec("tw-002", "七星潭", [gday("2026-11-11", ["21:00"])])),
      "v1:evals:tw-003": JSON.stringify(subjRec("tw-003", "阿里山", [gday("2026-11-11", ["06:00"])])),
    },
  });
  for (const [id, place] of [["r1", "tw-001"], ["r2", "tw-002"], ["r3", "tw-003"]]) {
    db._tables.notify_rules.push(ruleBase({
      id, place_id: place, schedule_mode: "weekdays", schedule_weekdays: "0,1,2,3,4,5,6",
      send_time: "08:00", lead_days: 2, tz: "Asia/Taipei",
    }));
  }
  db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });

  const calls = [];
  const s = await cronWith(env, T("2026-11-10T09:00:00+08:00"), calls);
  const sends = calls.filter((c) => c.url.includes("sendMessage"));
  assert.equal(sends.length, 1, "exactly ONE message per (user, channel, tick)");
  assert.equal(s.summary.messages_sent, 1);
  assert.equal(s.summary.sent, 3);
  assert.equal(s.summary.rules_matched, 3);

  const text = JSON.parse(sends[0].init.body).text;
  const lines = text.split("\n");
  assert.equal(lines[1], "3 個追蹤景點達標");
  const ruleLines = lines.filter((l) => l.includes("｜"));
  assert.equal(ruleLines.length, 3, "one line per due rule");
  assert.ok(ruleLines.some((l) => l.includes("合歡山") && l.includes("2026-11-11 05:00")));

  assert.equal(db._tables.notify_log.size, 3);
  const batches = new Set([...db._tables.notify_log.values()].map((r) => r.batch_id));
  assert.equal(batches.size, 1, "all three ledger rows share the batch_id");
  assert.ok([...batches][0]);
  for (const r of db._tables.notify_log.values()) assert.equal(r.delivered, 1);
});

// ---------------------------------------------------------------- legacy
test("cron: legacy rule (all schedule columns NULL) behaves exactly as before", async () => {
  const { env, db } = makeEnv({
    kv: { "v1:evals:tw-001": JSON.stringify(subjRec("tw-001", "七星潭", [gday("2026-11-10", ["20:00"])])) },
  });
  db._tables.notify_rules.push(ruleBase({ id: "r-legacy", min_advance_hours: 0, last_sent_at: null }));
  db._tables.telegram_bindings.set("u1", { status: "active", chat_id: "123" });

  const calls = [];
  const s1 = await cronWith(env, T("2026-11-10T12:00:00+08:00"), calls);
  assert.equal(s1.summary.sent, 1);
  assert.equal(s1.summary.silent_skipped, 0);
  assert.equal(s1.summary.messages_sent, 1);
  // legacy dedupe key is the qualifying WINDOW, not a date bucket
  assert.ok(db._tables.notify_log.has("r-legacy|2026-11-10T20:00"));
  assert.equal(db._tables.notify_log.get("r-legacy|2026-11-10T20:00").delivered, 1);

  const s2 = await cronWith(env, T("2026-11-10T12:30:00+08:00"), calls);
  assert.equal(s2.summary.skipped_dupe, 1);
  assert.equal(calls.filter((c) => c.url.includes("sendMessage")).length, 1);
});

// ---------------------------------------------------------------- endpoints
test("defaults endpoints: GET empty -> PUT persists -> rules list carries defaults", async () => {
  const { env, db } = makeEnv({});
  const tok = await mint(env, "u1");
  const hdr = { "Content-Type": "application/json", Authorization: "Bearer " + tok };

  const anon = await worker.fetch(makeReq("/notify/defaults"), env, {});
  assert.equal(anon.status, 401);

  const empty = await worker.fetch(makeReq("/notify/defaults", { headers: hdr }), env, {});
  assert.equal(empty.status, 200);
  assert.equal((await empty.json()).defaults, null);

  const bad = await worker.fetch(makeReq("/notify/defaults", {
    method: "PUT", headers: hdr, body: JSON.stringify({ scheduleMode: "monthly" }),
  }), env, {});
  assert.equal(bad.status, 400);

  const put = await worker.fetch(makeReq("/notify/defaults", {
    method: "PUT", headers: hdr,
    body: JSON.stringify({ scheduleMode: "weekdays", scheduleWeekdays: "4,5", sendTime: "20:15", leadDays: 3, minTier: "recommend", channel: "push", tz: "Asia/Taipei" }),
  }), env, {});
  assert.equal(put.status, 200);
  const putBody = await put.json();
  assert.equal(putBody.defaults.send_time, "20:15");
  assert.equal(putBody.defaults.schedule_weekdays, "4,5");
  assert.equal(db._tables.notify_defaults.get("u1").tz, "Asia/Taipei");

  const created = await worker.fetch(makeReq("/notify/rules", {
    method: "POST", headers: hdr,
    body: JSON.stringify({ placeId: "tw-001", scheduleMode: "every_n_days", scheduleEveryN: 2, sendTime: "07:30" }),
  }), env, {});
  assert.equal(created.status, 200);
  const createdBody = await created.json();
  assert.equal(createdBody.rule.schedule.scheduleMode, "every_n_days");
  assert.equal(db._tables.notify_rules[0].send_time, "07:30");
  assert.equal(db._tables.notify_rules[0].lead_days, null, "absent field stays NULL = inherit");

  const list = await (await worker.fetch(makeReq("/notify/rules", { headers: hdr }), env, {})).json();
  assert.equal(list.defaults.send_time, "20:15");
  assert.equal(list.rules.length, 1);
  assert.equal(list.rules[0].schedule_mode, "every_n_days");
});

// ---------------------------------------------------------------- CL-UX-01 (15/16)
// 進階玩家路徑：彈性排程 ＋ custom_conditions 自訂條件（owner 2026-11-24 要求補的
// 組合測試）。主人自己釘的 hourly 門檻要跟排程門檻、出景日篩選、整併一起成立。
test("CL-UX-01 (15): a scheduled custom-conditions rule consolidates with a subject rule", async () => {
  const NOW_MS = Date.parse("2026-11-26T20:05:00+08:00"); // Thursday, 20:05 local
  const { env, db } = makeEnv({
    kv: {
      "v1:evals:tw-cx": JSON.stringify({
        place_id: "tw-cx", name_i18n: { "zh-TW": "自訂點" }, timezone: "Asia/Taipei",
        hourly: [{ local_date: "2026-11-28", hour: "05:00", // Saturday
          values: { cloud_low: 10, cloud_mid: 10, cloud_high: 10, precipitation: 0, visibility: 20, wind: 2 } }],
      }),
      "v1:evals:tw-sub": JSON.stringify({
        place_id: "tw-sub", name_i18n: { "zh-TW": "合歡山" },
        subjects: [{ opportunity_id: "cloud-sea", name_i18n: { "zh-TW": "雲海" },
          days: [{ local_date: "2026-11-28", verdict: "GUIDANCE_SATISFIED", hours: ["05:00"] }] }],
      }),
    },
  });
  const t = db._tables;
  t.telegram_bindings.set("u1", { chat_id: "123", status: "active" });
  const sched = {
    user_id: "u1", channel: "telegram", min_advance_hours: 0, enabled: 1,
    schedule_mode: "weekdays", schedule_weekdays: "4", send_time: "20:00",
    lead_days: 3, target_weekdays: "6", min_tier: "recommend", tz: "Asia/Taipei",
  };
  t.notify_rules.push({ id: "r-cx", place_id: "tw-cx", opportunity_id: null,
    custom_conditions: JSON.stringify({ cloud_low_max: 30 }), ...sched });
  t.notify_rules.push({ id: "r-sub", place_id: "tw-sub", opportunity_id: "cloud-sea",
    custom_conditions: null, ...sched });

  const { summary, sends } = await cronWith(env, NOW_MS);

  assert.equal(sends.length, 1, "one consolidated message, not one per rule");
  const body = String(sends[0].init.body);
  assert.ok(body.includes("自訂點"), "the custom-conditions place rides the summary");
  assert.ok(body.includes("合歡山"), "the subject place rides the same summary");
  const rows = [...t.notify_log.values()];
  assert.equal(rows.length, 2, "one ledger row per rule");
  assert.equal(new Set(rows.map((r) => r.batch_id)).size, 1, "both rows share one batch_id");
  assert.ok(summary.messages_sent >= 1);
});

test("CL-UX-01 (16): a custom-conditions rule that never matches stays silent", async () => {
  const NOW_MS = Date.parse("2026-11-26T20:05:00+08:00");
  const { env, db } = makeEnv({
    kv: {
      "v1:evals:tw-cx": JSON.stringify({
        place_id: "tw-cx", name_i18n: { "zh-TW": "自訂點" }, timezone: "Asia/Taipei",
        hourly: [{ local_date: "2026-11-28", hour: "05:00",
          values: { cloud_low: 100, cloud_mid: 100, cloud_high: 100, precipitation: 5, visibility: 2, wind: 12 } }],
      }),
    },
  });
  const t = db._tables;
  t.telegram_bindings.set("u1", { chat_id: "123", status: "active" });
  t.notify_rules.push({ id: "r-cx", user_id: "u1", place_id: "tw-cx", opportunity_id: null,
    channel: "telegram", min_advance_hours: 0, enabled: 1,
    custom_conditions: JSON.stringify({ cloud_low_max: 10, precipitation_max: 0 }),
    schedule_mode: "weekdays", schedule_weekdays: "4", send_time: "20:00",
    lead_days: 3, target_weekdays: null, min_tier: "recommend", tz: "Asia/Taipei" });

  const { summary, sends } = await cronWith(env, NOW_MS);

  assert.equal(sends.length, 0, "no empty notification is ever sent");
  assert.equal(t.notify_log.size, 0, "silence leaves no ledger row (nothing to dedupe)");
  assert.ok(summary.silent_skipped >= 1, "the reason is counted, not swallowed");
});
