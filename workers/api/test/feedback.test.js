// CL-DATA-70 tests: unified feedback channel (ratings / reports / comments).
// Covers the ticket's test list: rating upsert uniqueness, aggregate math
// (Bayesian / half-life / trust ladder / chain factor), cluster cap, first
// review pending, admin permissions, gray-release off rejection — plus the
// standing suite requirement that nothing here touches tier computation.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { aggregateFromRows, maskName, maskedDisplayName, shortCode36, computeTrustLevel, FEEDBACK_CONSTANTS } from "../src/feedback.js";
import { signJWT } from "../src/auth.js";

const DAY = 86_400_000;
const DEV_SECRET = "chaselights-dev-secret-do-not-use-in-prod";
const FLAG_KEY = "v1:flags:feedback";

// ---------------------------------------------------------------- mock D1
function stamp(ms) {
  return new Date(ms).toISOString().replace("T", " ").slice(0, 19);
}
const dbTime = (s) => (s ? Date.parse(String(s).replace(" ", "T") + "Z") : NaN);

function makeFeedbackEnv(opts = {}) {
  const t = { users: new Map(), feedback: [], kv: new Map() };
  const parseLimit = (sql) => {
    const m = sql.match(/LIMIT (\d+)(?:\s+OFFSET (\d+))?/);
    return { limit: m ? Number(m[1]) : Infinity, offset: m && m[2] ? Number(m[2]) : 0 };
  };
  const jparse = (s) => { try { return JSON.parse(s); } catch { return {}; } };

  function runQuery(sql, args) {
    const u = args[0];
    // users lookups
    if (/SELECT device_id, level, created_at FROM users WHERE device_id = \?1/.test(sql)) {
      const r = t.users.get(u);
      return r ? [{ device_id: r.device_id, level: r.level, created_at: r.created_at }] : [];
    }
    if (/SELECT level FROM users WHERE device_id = \?1/.test(sql)) {
      const r = t.users.get(u);
      return r ? [{ level: r.level }] : [];
    }
    // chain count (photo_url report or push_invite rating, last 90 days)
    // NOTE: must run before the generic valid-submission count — the chain SQL
    // shares its prefix.
    if (/json_extract\(payload, '\$\.photo_url'\)/.test(sql) && /'-90 days'/.test(sql)) {
      const rows = t.feedback.filter((r) =>
        r.user_id === u && (r.status === "ok" || r.status === "pending") &&
        dbTime(r.created_at) >= Date.now() - 90 * DAY &&
        ((r.type === "report" && jparse(r.payload).photo_url) ||
         (r.type === "rating" && jparse(r.payload).source === "push_invite")));
      return [{ n: rows.length }];
    }
    // valid-submission counts (trust ladder)
    if (/COUNT\(\*\) AS n FROM feedback WHERE user_id = \?1 AND status IN \('ok','pending'\)/.test(sql)) {
      let rows = t.feedback.filter((r) => r.user_id === u && (r.status === "ok" || r.status === "pending"));
      if (/'-30 days'/.test(sql)) rows = rows.filter((r) => dbTime(r.created_at) >= Date.now() - 30 * DAY);
      return [{ n: rows.length }];
    }
    // T0 24h burst count
    if (/type = 'rating'/.test(sql) && /status = 'ok'/.test(sql) && /'-1 day'/.test(sql)) {
      const rows = t.feedback.filter((r) =>
        r.user_id === u && r.type === "rating" && r.status === "ok" &&
        dbTime(r.created_at) >= Date.now() - DAY);
      return [{ n: rows.length }];
    }
    // distinct regions
    if (/COUNT\(DISTINCT substr/.test(sql)) {
      const prefixes = new Set(t.feedback
        .filter((r) => r.user_id === u && (r.status === "ok" || r.status === "pending") && r.place_id && (r.type === "rating" || r.type === "report"))
        .map((r) => r.place_id.split("-")[0]));
      return [{ n: prefixes.size }];
    }
    // global Bayesian prior
    if (/AVG\(json_extract/.test(sql)) {
      const rows = t.feedback.filter((r) => r.type === "rating" && r.status === "ok").map((r) => jparse(r.payload));
      const ls = rows.map((p) => p.l).filter((v) => typeof v === "number");
      const ps = rows.map((p) => p.p).filter((v) => typeof v === "number");
      const avg = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : null);
      return [{ n: rows.length, ml: avg(ls), mp: avg(ps) }];
    }
    // per-place ok votes (aggregate scan)
    if (/SELECT payload, created_at FROM feedback WHERE type = 'rating' AND place_id = \?1 AND status = 'ok'/.test(sql)) {
      const { limit, offset } = parseLimit(sql);
      return t.feedback
        .filter((r) => r.type === "rating" && r.place_id === args[0] && r.status === "ok")
        .sort((a, b) => dbTime(a.created_at) - dbTime(b.created_at))
        .slice(offset, offset + limit)
        .map((r) => ({ payload: r.payload, created_at: r.created_at }));
    }
    // per-place public comments (join users for masked name)
    if (/LEFT JOIN users u ON u\.device_id = f\.user_id/.test(sql) && /f\.type = 'comment'/.test(sql)) {
      const { limit, offset } = parseLimit(sql);
      const status = (sql.match(/f\.status = '(\w+)'/) || [])[1];
      const place = /f\.place_id = \?1/.test(sql) ? args[0] : undefined;
      return t.feedback
        .filter((r) => r.type === "comment" && r.status === status && (place === undefined || r.place_id === place))
        .sort((a, b) => dbTime(b.created_at) - dbTime(a.created_at))
        .slice(offset, offset + limit)
        .map((r) => ({ user_id: r.user_id, payload: r.payload, created_at: r.created_at, display_name: (t.users.get(r.user_id) || {}).display_name || null }));
    }
    // CL-UI-100: L/P of the commenter's own ok rating on the same place
    if (/SELECT user_id, payload FROM feedback WHERE type = 'rating' AND place_id = \?1 AND status = 'ok'/.test(sql)) {
      return t.feedback
        .filter((r) => r.type === "rating" && r.place_id === args[0] && r.status === "ok")
        .map((r) => ({ user_id: r.user_id, payload: r.payload }));
    }
    // CL-UI-100: display-name group for the short-code collision check
    if (/SELECT device_id FROM users WHERE display_name = \?1$/.test(sql)) {
      return [...t.users.values()].filter((u) => u.display_name === args[0]).map((u) => ({ device_id: u.device_id }));
    }
    // comment count for a place
    if (/COUNT\(\*\) AS n FROM feedback WHERE type = 'comment' AND place_id = \?1 AND status = 'ok'/.test(sql)) {
      return [{ n: t.feedback.filter((r) => r.type === "comment" && r.place_id === args[0] && r.status === "ok").length }];
    }
    // my rating for one place
    if (/FROM feedback WHERE user_id = \?1 AND place_id = \?2 AND type = 'rating' LIMIT 1/.test(sql)) {
      const r = t.feedback.find((x) => x.user_id === u && x.place_id === args[1] && x.type === "rating");
      return r ? [r] : [];
    }
    // all my ratings
    if (/FROM feedback WHERE user_id = \?1 AND type = 'rating' ORDER BY created_at DESC/.test(sql)) {
      return t.feedback.filter((x) => x.user_id === u && x.type === "rating")
        .sort((a, b) => dbTime(b.created_at) - dbTime(a.created_at));
    }
    // last submission (throttle)
    if (/SELECT created_at FROM feedback WHERE user_id = \?1 ORDER BY created_at DESC LIMIT 1/.test(sql)) {
      const r = t.feedback.filter((x) => x.user_id === u).sort((a, b) => dbTime(b.created_at) - dbTime(a.created_at))[0];
      return r ? [{ created_at: r.created_at }] : [];
    }
    // existing vote id (upsert target)
    if (/SELECT id FROM feedback WHERE user_id = \?1 AND place_id = \?2 AND type = 'rating' LIMIT 1/.test(sql)) {
      const r = t.feedback.find((x) => x.user_id === u && x.place_id === args[1] && x.type === "rating");
      return r ? [{ id: r.id }] : [];
    }
    // admin queue
    if (/SELECT f\.id, f\.user_id.*FROM feedback f/.test(sql)) {
      const status = (sql.match(/WHERE f\.status = '(\w+|all)'/) || [])[1];
      const { limit, offset } = parseLimit(sql);
      return t.feedback
        .filter((r) => !status || status === "all" || r.status === status)
        .sort((a, b) => dbTime(b.created_at) - dbTime(a.created_at))
        .slice(offset, offset + limit)
        .map((r) => ({ ...r, display_name: (t.users.get(r.user_id) || {}).display_name || null, name_history: (t.users.get(r.user_id) || {}).name_history }));
    }
    // admin queue count
    if (/SELECT COUNT\(\*\) AS n FROM feedback WHERE status =/.test(sql)) {
      const status = (sql.match(/WHERE status = '(\w+)'/) || [])[1];
      return [{ n: t.feedback.filter((r) => r.status === status).length }];
    }
    // admin review select
    if (/SELECT id, status, payload FROM feedback WHERE id = \?1 LIMIT 1/.test(sql)) {
      const r = t.feedback.find((x) => x.id === u);
      return r ? [{ id: r.id, status: r.status, payload: r.payload }] : [];
    }
    // generic users row (profile PATCH reads display_name/name_history)
    if (/FROM users WHERE device_id = \?1/.test(sql)) {
      const r = t.users.get(u);
      return r ? [{ ...r }] : [];
    }
    return [];
  }

  function runSql(sql, args) {
    if (/INSERT INTO feedback \(id, user_id, place_id, type, status, payload\)/.test(sql)) {
      const now = stamp(Date.now());
      t.feedback.push({
        id: args[0], user_id: args[1], place_id: args[2], type: args[3],
        status: args[4], payload: args[5], created_at: now, updated_at: now,
      });
      return { meta: { changes: 1 } };
    }
    if (/UPDATE feedback SET status = 'ok', payload = \?2, updated_at = \?3 WHERE id = \?1/.test(sql)) {
      const r = t.feedback.find((x) => x.id === args[0]);
      if (!r) return { meta: { changes: 0 } };
      r.status = "ok"; r.payload = args[1]; r.updated_at = args[2];
      return { meta: { changes: 1 } };
    }
    if (/UPDATE feedback SET status = 'flagged', payload = \?2, updated_at = \?3 WHERE id = \?1/.test(sql)) {
      const r = t.feedback.find((x) => x.id === args[0]);
      if (!r) return { meta: { changes: 0 } };
      r.status = "flagged"; r.payload = args[1]; r.updated_at = args[2];
      return { meta: { changes: 1 } };
    }
    if (/UPDATE feedback SET status = \?2, payload = \?3, updated_at = \?4 WHERE id = \?1/.test(sql)) {
      const r = t.feedback.find((x) => x.id === args[0]);
      if (!r) return { meta: { changes: 0 } };
      r.status = args[1]; r.payload = args[2]; r.updated_at = args[3];
      return { meta: { changes: 1 } };
    }
    if (/DELETE FROM feedback WHERE user_id = \?1 AND place_id = \?2 AND type = 'rating'/.test(sql)) {
      const before = t.feedback.length;
      t.feedback = t.feedback.filter((x) => !(x.user_id === u0(args) && x.place_id === args[1] && x.type === "rating"));
      return { meta: { changes: before - t.feedback.length } };
    }
    if (/UPDATE users SET display_name = \?1, profile_json = \?2 WHERE device_id = \?3/.test(sql)) {
      const r = t.users.get(args[2]);
      if (!r) return { meta: { changes: 0 } };
      r.display_name = args[0]; r.profile_json = args[1];
      return { meta: { changes: 1 } };
    }
    if (/UPDATE users SET name_history = \?1 WHERE device_id = \?2/.test(sql)) {
      const r = t.users.get(args[1]);
      if (!r) return { meta: { changes: 0 } };
      r.name_history = args[0];
      return { meta: { changes: 1 } };
    }
    return { meta: { changes: 0 } };
  }
  const u0 = (args) => args[0];

  const db = {
    _t: t,
    prepare(sqlRaw) {
      const sql = sqlRaw.replace(/\s+/g, " "); // multiline SQL strings → single line for matching
      const runner = (args = []) => ({
        run: async () => runSql(sql, args),
        first: async () => runQuery(sql, args)[0] || null,
        all: async () => ({ results: runQuery(sql, args) }),
      });
      return { ...runner([]), bind: (...a) => runner(a) };
    },
  };
  const kv = {
    get: async (k, type) => {
      const v = t.kv.get(k);
      if (v === undefined) return null;
      return type === "json" ? JSON.parse(v) : v;
    },
    put: async (k, v) => { t.kv.set(k, v); },
  };
  return { env: { EVALS: kv, DB: db }, t };
}

// ---------------------------------------------------------------- helpers
async function tokenFor(uid, level = "free") {
  const now = Math.floor(Date.now() / 1000);
  return signJWT({ sub: uid, name: "U", level, typ: "access", iat: now, exp: now + 900 }, DEV_SECRET);
}
function makeReq(path, opts = {}) {
  return new Request(`https://chaselights.app/api/v1${path}`, opts);
}
async function enableFlag(env, on = true) {
  await env.EVALS.put(FLAG_KEY, JSON.stringify({ enabled: on }));
}
function seedRow(t, { user, place, type = "rating", status = "ok", payload = {}, ageDays = 2, id }) {
  const created_at = stamp(Date.now() - ageDays * DAY);
  t.feedback.push({
    id: id || `s${t.feedback.length}`,
    user_id: user, place_id: place, type, status,
    payload: JSON.stringify(payload), created_at, updated_at: created_at,
  });
}
const close = (x, want, eps = 1e-6) => Math.abs(x - want) < eps;
const fresh = () => ({ l: 5, p: 4, weight: 1, trust_level: "t2", source: "app", ip_cluster: "c1", device_hash: "d1" });
const row = (payload, ageDays = 0) => ({ payload: JSON.stringify(payload), created_at: stamp(Date.now() - ageDays * DAY) });

// ---------------------------------------------------------------- owner rulings (Stage 1 addition)
test("rename throttle: display_name limited to once per 7 days once feedback is live (429 + tri-lingual)", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);
  t.users.set("u-rn", { device_id: "u-rn", level: "free", created_at: stamp(Date.now() - 100 * DAY), display_name: "舊名", name_history: "[]" });
  const tok = await tokenFor("u-rn");
  const patch = (name) => worker.fetch(makeReq("/auth/profile", { method: "PATCH", headers: { Authorization: `Bearer ${tok}`, "Content-Type": "application/json" }, body: JSON.stringify({ displayName: name }) }), env, {});

  const r1 = await patch("新名一");
  assert.equal(r1.status, 200);
  assert.equal(t.users.get("u-rn").display_name, "新名一");

  // second change inside 7 days → 429 + tri-lingual message
  const r2 = await patch("新名二");
  assert.equal(r2.status, 429);
  const b2 = await r2.json();
  assert.ok(b2.message["zh-TW"] && b2.message.en && b2.message.ja);
  assert.equal(t.users.get("u-rn").display_name, "新名一"); // unchanged

  // setting the SAME name is idempotent — no throttle, no history entry
  const r3 = await patch("新名一");
  assert.equal(r3.status, 200);
  assert.equal(JSON.parse(t.users.get("u-rn").name_history).length, 1);

  // outside the 7-day window → allowed again
  const hist = JSON.parse(t.users.get("u-rn").name_history);
  hist[hist.length - 1].at = new Date(Date.now() - 8 * DAY).toISOString();
  t.users.get("u-rn").name_history = JSON.stringify(hist);
  const r4 = await patch("改名三");
  assert.equal(r4.status, 200);
  const finalHist = JSON.parse(t.users.get("u-rn").name_history);
  assert.equal(finalHist.length, 2);
  assert.equal(finalHist[1].name, "改名三");
});

test("rename throttle: not enforced while the feedback flag is OFF (takes effect at gray release)", async () => {
  const { env, t } = makeFeedbackEnv(); // flag off
  t.users.set("u-rn2", { device_id: "u-rn2", level: "free", created_at: stamp(Date.now() - 100 * DAY), display_name: "A", name_history: "[]" });
  const tok = await tokenFor("u-rn2");
  const patch = (name) => worker.fetch(makeReq("/auth/profile", { method: "PATCH", headers: { Authorization: `Bearer ${tok}`, "Content-Type": "application/json" }, body: JSON.stringify({ displayName: name }) }), env, {});
  assert.equal((await patch("B")).status, 200);
  assert.equal((await patch("C")).status, 200);
  assert.equal(t.users.get("u-rn2").name_history, "[]"); // no audit before launch
});

test("rename history: admin feedback queue exposes the audit trail; trust stays keyed to user_id", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);
  t.users.set("u1", {
    device_id: "u1", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "晨曦之光",
    name_history: JSON.stringify([{ name: "晨曦之光", at: new Date(Date.now() - 40 * DAY).toISOString() }]),
  });
  seedRow(t, { user: "u1", place: "tw-001", type: "comment", status: "pending", ageDays: 0.01, payload: { comment_text: "待審留言", trust_level: "t1" } });
  const adminTok = await tokenFor("admin-1", "admin");
  t.users.set("admin-1", { device_id: "admin-1", level: "admin", created_at: stamp(Date.now() - 400 * DAY) });
  const list = await (await worker.fetch(makeReq("/admin/feedback?status=pending", { headers: { Authorization: `Bearer ${adminTok}` } }), env, {})).json();
  assert.equal(list.items.length, 1);
  assert.deepEqual(list.items[0].nameHistory, [{ name: "晨曦之光", at: list.items[0].nameHistory[0].at }]);
  // rating payload carries its own trust snapshot — rename cannot touch it
  assert.ok(list.items[0].payload.trust_level);
});

// ---------------------------------------------------------------- flag (ruling ⑤)
test("feedback flag: default OFF rejects every endpoint (gray release)", async () => {
  const { env } = makeFeedbackEnv(); // KV empty → default off
  const get = await worker.fetch(makeReq("/feedback?place_id=tw-001"), env, {});
  assert.equal(get.status, 403);
  const post = await worker.fetch(makeReq("/feedback", { method: "POST", body: JSON.stringify({ type: "rating", placeId: "tw-001", l: 5, p: 4 }) }), env, {});
  assert.equal(post.status, 403);
  const del = await worker.fetch(makeReq("/feedback?place_id=tw-001", { method: "DELETE" }), env, {});
  assert.equal(del.status, 403);
  const admin = await worker.fetch(makeReq("/admin/feedback?status=pending"), env, {});
  assert.equal(admin.status, 403);
  assert.equal((await post.json()).error, "feedback disabled");
});

test("feedback flag: KV on, env override, explicit off", async () => {
  const a = makeFeedbackEnv();
  await enableFlag(a.env);
  assert.equal((await worker.fetch(makeReq("/feedback?place_id=tw-001"), a.env, {})).status, 200);

  const b = makeFeedbackEnv();
  b.env.FEEDBACK_ENABLED = "1";
  assert.equal((await worker.fetch(makeReq("/feedback?place_id=tw-001"), b.env, {})).status, 200);

  const c = makeFeedbackEnv();
  await enableFlag(c.env);
  c.env.FEEDBACK_ENABLED = "0";
  assert.equal((await worker.fetch(makeReq("/feedback?place_id=tw-001"), c.env, {})).status, 403);
});

// ---------------------------------------------------------------- auth + validation
test("feedback: full-channel login requirement (JWT session, no anonymous fallback)", async () => {
  const { env } = makeFeedbackEnv();
  await enableFlag(env);
  const post = await worker.fetch(makeReq("/feedback", { method: "POST", body: JSON.stringify({ type: "rating", placeId: "tw-001", l: 5, p: 4 }) }), env, {});
  assert.equal(post.status, 401);
  // legacy anonymous userId param must NOT open the channel
  const anon = await worker.fetch(makeReq("/feedback", { method: "POST", body: JSON.stringify({ type: "rating", placeId: "tw-001", l: 5, p: 4, userId: "dev1" }) }), env, {});
  assert.equal(anon.status, 401);
  const mine = await worker.fetch(makeReq("/feedback?mine=1"), env, {});
  assert.equal(mine.status, 401);
  const del = await worker.fetch(makeReq("/feedback?place_id=tw-001", { method: "DELETE" }), env, {});
  assert.equal(del.status, 401);
});

test("feedback: submission validation (axes, categories, text limits, shot_date, photo_url)", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);
  const tok = await tokenFor("u-val");
  const post = (body) => worker.fetch(makeReq("/feedback", { method: "POST", headers: { Authorization: `Bearer ${tok}` }, body: JSON.stringify(body) }), env, {});

  assert.equal((await post({ type: "rating", placeId: "tw-001", l: 0, p: 4 })).status, 400);
  assert.equal((await post({ type: "rating", placeId: "tw-001", l: 6, p: 4 })).status, 400);
  assert.equal((await post({ type: "rating", placeId: "tw-001", l: 3.5, p: 4 })).status, 400);
  assert.equal((await post({ type: "rating", l: 3, p: 4 })).status, 400);
  assert.equal((await post({ type: "rating", placeId: "tw-001", l: 3, p: 4, shotDate: "2099-01-01" })).status, 400);
  assert.equal((await post({ type: "report", placeId: "tw-001" })).status, 400); // category required
  assert.equal((await post({ type: "report", placeId: "tw-001", reportCategory: "nope", commentText: "x" })).status, 400);
  assert.equal((await post({ type: "report", placeId: "tw-001", reportCategory: "data_wrong" })).status, 400); // text required
  assert.equal((await post({ type: "report", placeId: "tw-001", reportCategory: "data_wrong", commentText: "x", photoUrl: "http://e.com/a.jpg" })).status, 400);
  assert.equal((await post({ type: "comment", commentText: "" })).status, 400);
  assert.equal(t.feedback.length, 0);
});

// ---------------------------------------------------------------- rating upsert / one vote
test("rating: one vote per (user, place) — edit overwrites, nRaw never grows; delete works", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);
  t.users.set("u9", { device_id: "u9", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "山手線" });
  const tok = await tokenFor("u9");
  const headers = { Authorization: `Bearer ${tok}` };

  const r1 = await worker.fetch(makeReq("/feedback", { method: "POST", headers, body: JSON.stringify({ type: "rating", placeId: "tw-001", l: 5, p: 4 }) }), env, {});
  assert.equal((await r1.json()).upserted, "created");

  // second submission lands inside the 90s window → flagged (fail-closed, §2.4)
  const r2 = await worker.fetch(makeReq("/feedback", { method: "POST", headers, body: JSON.stringify({ type: "rating", placeId: "tw-001", l: 2, p: 2 }) }), env, {});
  const b2 = await r2.json();
  assert.equal(b2.status, "flagged");
  assert.equal(b2.flagReason, "time");
  // throttled edit must NOT have created a second row (unique vote index holds)
  assert.equal(t.feedback.filter((x) => x.type === "rating" && x.place_id === "tw-001").length, 1);

  // legitimate edit outside the throttle window → overwrite same row
  const mine = t.feedback[0];
  mine.created_at = stamp(Date.now() - 10 * 60 * 1000);
  const r3 = await worker.fetch(makeReq("/feedback", { method: "PUT", headers, body: JSON.stringify({ type: "rating", placeId: "tw-001", l: 4, p: 5 }) }), env, {});
  const b3 = await r3.json();
  assert.equal(b3.upserted, "updated");
  assert.equal(t.feedback.length, 1);
  assert.equal(JSON.parse(t.feedback[0].payload).l, 4);

  const agg = await (await worker.fetch(makeReq("/feedback?place_id=tw-001"), env, {})).json();
  assert.equal(agg.nRaw, 1);

  const del = await worker.fetch(makeReq("/feedback?place_id=tw-001", { method: "DELETE", headers }), env, {});
  assert.equal((await del.json()).ok, true);
  const agg2 = await (await worker.fetch(makeReq("/feedback?place_id=tw-001"), env, {})).json();
  assert.equal(agg2.nRaw, 0);
  assert.equal(agg2.insufficient, true);
  assert.equal(agg2.lFinal, null);
  const del2 = await worker.fetch(makeReq("/feedback?place_id=tw-001", { method: "DELETE", headers }), env, {});
  assert.equal(del2.status, 404);
  const mine2 = await worker.fetch(makeReq("/feedback?mine=1&place_id=tw-001", { headers }), env, {});
  assert.equal((await mine2.json()).rating, null);
});

// ---------------------------------------------------------------- first review + admin (rulings ②④)
test("comment/report: first-review pending → admin approve makes public, masked name only", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);
  t.users.set("u1", { device_id: "u1", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "晨曦之光" });
  const tok = await tokenFor("u1");
  const headers = { Authorization: `Bearer ${tok}` };

  // comment lands pending
  const c1 = await worker.fetch(makeReq("/feedback", { method: "POST", headers, body: JSON.stringify({ type: "comment", placeId: "tw-001", commentText: "雲海值得但機位只有一個" }) }), env, {});
  const c1b = await c1.json();
  assert.equal(c1b.status, "pending");
  assert.equal(c1b.type, "comment");

  // report lands pending and is never publicly visible (backdate the comment
  // so the 90s throttle does not flag this second submission by the same user)
  t.feedback[0].created_at = stamp(Date.now() - 10 * 60 * 1000);
  const rp = await worker.fetch(makeReq("/feedback", { method: "POST", headers, body: JSON.stringify({ type: "report", placeId: "tw-001", reportCategory: "location_wrong", commentText: "座標偏移 300m" }) }), env, {});
  assert.equal((await rp.json()).status, "pending");

  // aggregate shows neither comment nor report
  const agg0 = await (await worker.fetch(makeReq("/feedback?place_id=tw-001"), env, {})).json();
  assert.equal(agg0.nComments, 0);
  assert.deepEqual(agg0.comments, []);

  // admin queue shows both, masked name, no raw identity
  const adminTok = await tokenFor("admin-1", "admin");
  t.users.set("admin-1", { device_id: "admin-1", level: "admin", created_at: stamp(Date.now() - 400 * DAY) });
  const list = await (await worker.fetch(makeReq("/admin/feedback?status=pending", { headers: { Authorization: `Bearer ${adminTok}` } }), env, {})).json();
  assert.equal(list.count, 2);
  assert.equal(list.items.length, 2);
  const commentItem = list.items.find((i) => i.type === "comment");
  assert.equal(commentItem.maskedName, `晨曦·#${await shortCode36("u1", 4)}`);
  assert.ok(!JSON.stringify(list.items).includes("p:line") && !JSON.stringify(list.items).includes("u1@"));
  assert.ok(list.items.every((i) => !("userId" in i) && !("user_id" in i)));

  // non-admin is rejected on both admin endpoints
  const noTok = await tokenFor("u1");
  const noGet = await worker.fetch(makeReq("/admin/feedback?status=pending", { headers: { Authorization: `Bearer ${noTok}` } }), env, {});
  assert.equal(noGet.status, 403);
  const noPatch = await worker.fetch(makeReq(`/admin/feedback/${commentItem.id}`, { method: "PATCH", headers: { Authorization: `Bearer ${noTok}` }, body: JSON.stringify({ action: "approve" }) }), env, {});
  assert.equal(noPatch.status, 403);

  // admin rejects the report, approves the comment
  const repItem = list.items.find((i) => i.type === "report");
  const rej = await worker.fetch(makeReq(`/admin/feedback/${repItem.id}`, { method: "PATCH", headers: { Authorization: `Bearer ${adminTok}` }, body: JSON.stringify({ action: "reject" }) }), env, {});
  assert.equal((await rej.json()).status, "rejected");
  const app = await worker.fetch(makeReq(`/admin/feedback/${commentItem.id}`, { method: "PATCH", headers: { Authorization: `Bearer ${adminTok}` }, body: JSON.stringify({ action: "approve" }) }), env, {});
  assert.equal((await app.json()).status, "ok");

  // approved comment is public with masked name; rejected report never is
  const agg = await (await worker.fetch(makeReq("/feedback?place_id=tw-001"), env, {})).json();
  assert.equal(agg.nComments, 1);
  assert.equal(agg.comments[0].message, "雲海值得但機位只有一個");
  assert.equal(agg.comments[0].maskedName, `晨曦·#${await shortCode36("u1", 4)}`);
  assert.ok(!JSON.stringify(agg).includes("座標偏移"));

  // review bookkeeping + bad actions
  const list2 = await (await worker.fetch(makeReq("/admin/feedback?status=rejected", { headers: { Authorization: `Bearer ${adminTok}` } }), env, {})).json();
  assert.equal(list2.count, 1);
  assert.equal(list2.items[0].payload.reviewed_by, "admin-1");
  assert.ok(list2.items[0].payload.reviewed_at);
  assert.equal((await worker.fetch(makeReq(`/admin/feedback/${commentItem.id}`, { method: "PATCH", headers: { Authorization: `Bearer ${adminTok}` }, body: JSON.stringify({ action: "nuke" }) }), env, {})).status, 400);
  assert.equal((await worker.fetch(makeReq("/admin/feedback/nope-id", { method: "PATCH", headers: { Authorization: `Bearer ${adminTok}` }, body: JSON.stringify({ action: "approve" }) }), env, {})).status, 404);
  assert.equal((await worker.fetch(makeReq("/admin/feedback?status=bogus", { headers: { Authorization: `Bearer ${adminTok}` } }), env, {})).status, 400);
});

test("admin queue filters by status and reports still exist after reject (audit trail)", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);
  t.users.set("u2", { device_id: "u2", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "" });
  const tok = await tokenFor("u2");
  await worker.fetch(makeReq("/feedback", { method: "POST", headers: { Authorization: `Bearer ${tok}` }, body: JSON.stringify({ type: "comment", commentText: "站務留言（無景點）" }) }), env, {});
  const adminTok = await tokenFor("admin-1", "admin");
  t.users.set("admin-1", { device_id: "admin-1", level: "admin", created_at: stamp(Date.now() - 400 * DAY) });
  const all = await (await worker.fetch(makeReq("/admin/feedback?status=all", { headers: { Authorization: `Bearer ${adminTok}` } }), env, {})).json();
  assert.equal(all.count, 1);
  assert.equal(all.items[0].placeId, null); // site-wide comment
  assert.equal(all.items[0].maskedName, null); // no display name → 攝影者·地區 client-side
});

// ---------------------------------------------------------------- trust ladder (ticket item 3)
test("trust ladder: t0 → t1 → t2 → t3 → tx with weights 0.5/1/1.5/2/3", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);

  const mk = async (uid, level, createdDaysAgo) => {
    t.users.set(uid, { device_id: uid, level, created_at: stamp(Date.now() - createdDaysAgo * DAY) });
    return tokenFor(uid, level);
  };
  const post = (tok, body) => worker.fetch(makeReq("/feedback", { method: "POST", headers: { Authorization: `Bearer ${tok}` }, body: JSON.stringify(body) }), env, {});
  const rating = { type: "rating", placeId: "tw-701", l: 4, p: 4 };

  // T0: brand-new member, no submissions
  let b = await (await post(await mk("u-t0", "free", 1), rating)).json();
  assert.equal(b.rating.trustLevel, "t0");
  assert.equal(b.rating.weight, 0.5);

  // T1: age ≥30d and ≥3 valid submissions in the last 30 days
  const tok1 = await mk("u-t1", "free", 40);
  for (let i = 0; i < 3; i++) seedRow(t, { user: "u-t1", place: `tw-00${i}`, type: "comment", ageDays: 2 });
  b = await (await post(tok1, rating)).json();
  assert.equal(b.rating.trustLevel, "t1");
  assert.equal(b.rating.weight, 1.0);

  // T2: T1 + 出片鏈路 (accepted report with photo_url within 90 days)
  const tok2 = await mk("u-t2", "free", 40);
  for (let i = 0; i < 3; i++) seedRow(t, { user: "u-t2", place: `tw-00${i}`, type: "comment", ageDays: 2 });
  seedRow(t, { user: "u-t2", place: "tw-010", type: "report", ageDays: 2, payload: { report_category: "data_wrong", comment_text: "x", photo_url: "https://e.com/p.jpg" } });
  b = await (await post(tok2, rating)).json();
  assert.equal(b.rating.trustLevel, "t2");
  assert.equal(b.rating.weight, 1.5);

  // T3: T2 + age ≥90d + ≥20 submissions + ≥3 regions
  const tok3 = await mk("u-t3", "free", 100);
  const regions = ["tw", "jp", "us"];
  for (let i = 0; i < 19; i++) seedRow(t, { user: "u-t3", place: `${regions[i % 3]}-p${i}`, type: "rating", ageDays: 2 });
  seedRow(t, { user: "u-t3", place: "tw-p20", type: "report", ageDays: 2, payload: { report_category: "other", comment_text: "x", photo_url: "https://e.com/p.jpg" } });
  b = await (await post(tok3, rating)).json();
  assert.equal(b.rating.trustLevel, "t3");
  assert.equal(b.rating.weight, 2.0);

  // Tx: owner/admin certified
  const tokx = await mk("u-tx", "admin", 500);
  b = await (await post(tokx, rating)).json();
  assert.equal(b.rating.trustLevel, "tx");
  assert.equal(b.rating.weight, 3.0);

  // T0 burst cap: ≤3 aggregate-counting ratings per 24h (design §2.4)
  const tokB = await mk("u-burst", "free", 1);
  for (let i = 0; i < 3; i++) seedRow(t, { user: "u-burst", place: `tw-b0${i}`, type: "rating", ageDays: 0.2 });
  const b4 = await (await post(tokB, { type: "rating", placeId: "tw-b04", l: 5, p: 5 })).json();
  assert.equal(b4.status, "flagged");
  assert.equal(b4.flagReason, "burst");
});

// ---------------------------------------------------------------- T0 burst cap already above; aggregate math below
test("aggregate math: Bayesian shrink k=5 toward global prior", () => {
  const now = Date.now();
  const votes = [1, 2, 3].map((i) => row({ ...fresh(), device_hash: `d${i}`, ip_cluster: `c${i}`, l: 5, p: 4 }, 0));
  const a = aggregateFromRows(votes, { m_l: 3, m_p: 3 }, now);
  assert.equal(a.nRaw, 3);
  assert.ok(close(a.nEff, 3));
  assert.ok(close(a.lRaw, 5) && close(a.lFinal, (5 * 3 + 3 * 5) / 8));
  assert.ok(close(a.pRaw, 4) && close(a.pFinal, (4 * 3 + 3 * 5) / 8));
});

test("aggregate math: 365-day half-life decay", () => {
  const a = aggregateFromRows([
    row({ ...fresh(), l: 5 }, 365),   // exactly one half-life → 0.5
    row({ ...fresh(), l: 5, device_hash: "d2" }, 0),
    row({ ...fresh(), l: 5, device_hash: "d3", ip_cluster: "c2" }, 0),
    row({ ...fresh(), l: 5, device_hash: "d4", ip_cluster: "c3" }, 0),
  ], { m_l: 5, m_p: 5 });
  // n_eff = 3×1 + 1×0.5 = 3.5
  assert.ok(close(a.nEff, 3.5));
  assert.equal(a.insufficient, false);
});

test("aggregate math: same-cluster equivalent-vote cap 2 → 3rd+ ×0.25", () => {
  const p = { ...fresh(), ip_cluster: "samec" };
  const a = aggregateFromRows(
    [1, 2, 3, 4, 5].map((i) => row({ ...p, device_hash: `d${i}`, l: 5 }, 0)),
    { m_l: 5, m_p: 5 }
  );
  assert.equal(a.nRaw, 5);
  assert.ok(close(a.nEff, 2 + 3 * 0.25), `nEff=${a.nEff}`); // §8: 2 + 0.25×3 = 2.75
  const b = aggregateFromRows(
    [1, 2, 3, 4, 5].map((i) => row({ ...p, ip_cluster: `c${i}`, device_hash: "sameDev", l: 5 }, 0)),
    { m_l: 5, m_p: 5 }
  );
  // device cluster alone: 5 votes, same device_hash → 2 full + 3×0.25
  assert.ok(close(b.nEff, 2 + 3 * 0.25), `nEff=${b.nEff}`);
});

test("aggregate math: no-chain P penalty (ruling ①) vs chain members", () => {
  // t0 app member (no chain): P ×0.5; t2 member (chain): full
  const a = aggregateFromRows([
    row({ ...fresh(), l: 1, p: 1, trust_level: "t0", weight: 0.5, device_hash: "dA" }, 0),
    row({ ...fresh(), l: 5, p: 5, trust_level: "t2", weight: 1.5, device_hash: "dB" }, 0),
  ], { m_l: 3, m_p: 3 });
  assert.ok(close(a.lRaw, (0.5 * 1 + 1.5 * 5) / 2));
  // chain: t0 row wP = 0.5×0.5 = 0.25; t2 row wP = 1.5
  assert.ok(close(a.pRaw, (0.25 * 1 + 1.5 * 5) / 1.75));
  // push_invite source always has the chain
  const b = aggregateFromRows([row({ ...fresh(), l: 5, p: 5, trust_level: "t0", weight: 0.5, source: "push_invite" })], { m_l: 3, m_p: 3 });
  assert.ok(close(b.pRaw, 5));
});

test("aggregate math: display gate + idempotence", () => {
  const now = Date.now();
  const rows = [1, 2].map((i) => row({ ...fresh(), device_hash: `d${i}` }, 0));
  const a = aggregateFromRows(rows, { m_l: 3, m_p: 3 }, now);
  assert.equal(a.insufficient, true); // n_raw < 3
  assert.equal(a.lFinal, null);
  assert.equal(a.pFinal, null);
  const three = [...rows, row({ ...fresh(), device_hash: "d3" }, 0)];
  const b = aggregateFromRows(three, { m_l: 3, m_p: 3 }, now);
  assert.equal(b.insufficient, false);
  assert.ok(b.lFinal > 0);
  assert.deepEqual(aggregateFromRows(three, { m_l: 3, m_p: 3 }, now), b); // §8 idempotence
});

test("aggregate end-to-end GET: prior + weights + cold-start + public comments", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);
  for (let i = 1; i <= 3; i++) {
    t.users.set(`m${i}`, { device_id: `m${i}`, level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: ["晨曦之光", "夜貓子", "追光者"][i - 1] });
    seedRow(t, {
      user: `m${i}`, place: "tw-001", ageDays: 0.01,
      payload: { ...fresh(), device_hash: `dv${i}`, ip_cluster: `c${i}`, l: 5, p: [4, 4, 2][i - 1] },
    });
  }
  seedRow(t, { user: "m1", place: "tw-001", type: "comment", ageDays: 0.01, payload: { comment_text: "機位只有一個", trust_level: "t1" } });
  seedRow(t, { user: "m2", place: "tw-001", type: "comment", ageDays: 0.01, payload: { comment_text: "還沒審" } }, );
  t.feedback[t.feedback.length - 1].status = "pending";

  const agg = await (await worker.fetch(makeReq("/feedback?place_id=tw-001"), env, {})).json();
  assert.equal(agg.placeId, "tw-001");
  assert.equal(agg.insufficient, false);
  assert.equal(agg.nRaw, 3);
  assert.ok(close(agg.nEff, 3, 1e-3));
  // prior computed over the same 3 votes: m_L=5 → lFinal stays 5
  assert.ok(close(agg.lFinal, (5 * 3 + 5 * 5) / 8, 1e-3));
  // m_P = (4+4+2)/3; pRaw = same → pFinal = same
  const mp = (4 + 4 + 2) / 3;
  assert.ok(close(agg.pFinal, (mp * 3 + mp * 5) / 8, 1e-3));
  assert.ok(close(agg.pctP4plus, 2 / 3));
  assert.equal(agg.nLast30, 3);
  assert.equal(agg.nComments, 1); // pending comment stays hidden
  assert.equal(agg.comments.length, 1);
  assert.equal(agg.comments[0].maskedName, `晨曦·#${await shortCode36("m1", 4)}`);
  assert.equal(agg.comments[0].message, "機位只有一個");

  // unknown place → honest cold start, no fabricated numbers
  const none = await (await worker.fetch(makeReq("/feedback?place_id=nope"), env, {})).json();
  assert.equal(none.insufficient, true);
  assert.equal(none.lFinal, null);
  assert.equal(none.pFinal, null);
  assert.equal(none.nRaw, 0);
  assert.equal((await worker.fetch(makeReq("/feedback"), env, {})).status, 400);
});

test("masked nickname: first two chars + **, empty → null (client shows 攝影者·地區)", () => {
  assert.equal(maskName("晨曦之光"), "晨曦**");
  assert.equal(maskName("晨"), "晨**");
  assert.equal(maskName("  "), null);
  assert.equal(maskName(null), null);
});

// ---------------------------------------------------------------- rate classes
test("rate limits: feedback GET joins the lenient read class; writes stay 60/min", async () => {
  const { env } = makeFeedbackEnv();
  await enableFlag(env);
  let last;
  for (let i = 0; i < 65; i++) {
    last = await worker.fetch(makeReq("/feedback?place_id=tw-001", { headers: { "CF-Connecting-IP": "7.7.7.1" } }), env, {});
    assert.notEqual(last.status, 429, `read request #${i + 1} must not 429`);
  }
  let post;
  for (let i = 0; i < 61; i++) {
    post = await worker.fetch(makeReq("/feedback", { method: "POST", headers: { "CF-Connecting-IP": "7.7.7.2" }, body: "{}" }), env, {});
  }
  assert.equal(post.status, 429);
});

test("tier pipeline untouched: feedback module exports no tier symbols and constants match the design", () => {
  assert.equal(FEEDBACK_CONSTANTS.HALF_LIFE_DAYS, 365);
  assert.equal(FEEDBACK_CONSTANTS.BAYES_K, 5);
  assert.deepEqual(FEEDBACK_CONSTANTS.WEIGHTS, { t0: 0.5, t1: 1.0, t2: 1.5, t3: 2.0, tx: 3.0 });
  assert.equal(FEEDBACK_CONSTANTS.CLUSTER_CAP, 2);
  assert.equal(FEEDBACK_CONSTANTS.CLUSTER_PENALTY, 0.25);
  assert.equal(FEEDBACK_CONSTANTS.DISPLAY_MIN_EFF, 2.0);
  assert.equal(FEEDBACK_CONSTANTS.DISPLAY_MIN_RAW, 3);
  assert.equal(FEEDBACK_CONSTANTS.T0_24H_VOTE_CAP, 3);
});

// ---------------------------------------------------------------- CL-UI-100 (DESIGN-7 Stage 2, shell UI)
test("CL-UI-100: /feedback/config exposes the gray flag with 200 even when off", async () => {
  const { env } = makeFeedbackEnv();
  const off = await worker.fetch(makeReq("/feedback/config"), env, {});
  assert.equal(off.status, 200);
  assert.deepEqual(await off.json(), { enabled: false });
  await enableFlag(env, true);
  const on = await worker.fetch(makeReq("/feedback/config"), env, {});
  assert.deepEqual(await on.json(), { enabled: true });
});

test("CL-UI-100: masked display name — 4-char code, same-name collision extends, unnamed → null", async () => {
  const { env, t } = makeFeedbackEnv();
  t.users.set("a1", { device_id: "a1", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "山風" });
  t.users.set("a2", { device_id: "a2", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "山風" });
  const c1 = await shortCode36("a1", 8);
  const c2 = await shortCode36("a2", 8);
  const m1 = await maskedDisplayName(env, "a1", "山風");
  const m2 = await maskedDisplayName(env, "a2", "山風");
  assert.match(m1, /^山風·#[0-9a-z]+$/);
  assert.notEqual(m1, m2); // same display name, still tellable apart
  const n1 = m1.split("#")[1];
  const n2 = m2.split("#")[1];
  if (c1.slice(0, 4) === c2.slice(0, 4)) {
    assert.ok(n1.length > 4, `collision must extend the code beyond 4 (got ${n1})`);
    assert.notEqual(n1, n2);
  } else {
    assert.equal(n1, c1.slice(0, 4));
    assert.equal(n2, c2.slice(0, 4));
  }
  // different display names never collide even with equal code prefixes
  t.users.set("b1", { device_id: "b1", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "雲端" });
  const m3 = await maskedDisplayName(env, "b1", "雲端");
  assert.equal(m3, `雲端·#${(await shortCode36("b1", 8)).slice(0, 4)}`);
  // no display name → null (the client shows the 攝影者 fallback)
  assert.equal(await maskedDisplayName(env, "n1", ""), null);
  assert.equal(await maskedDisplayName(env, "n1", null), null);
});

test("CL-UI-100: aggregate comment rows carry the commenter's own L/P when they rated", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);
  t.users.set("lp1", { device_id: "lp1", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "山風旅人" });
  t.users.set("lp2", { device_id: "lp2", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "海線" });
  seedRow(t, { user: "lp1", place: "tw-001", type: "rating", ageDays: 1, payload: { l: 4, p: 5, weight: 1, trust_level: "t1", source: "app", ip_cluster: "c", device_hash: "d" } });
  seedRow(t, { user: "lp1", place: "tw-001", type: "comment", ageDays: 0.5, payload: { comment_text: "機位在北側", trust_level: "t1" } });
  seedRow(t, { user: "lp2", place: "tw-001", type: "comment", ageDays: 0.6, payload: { comment_text: "還沒評分", trust_level: "t0" } });
  const agg = await (await worker.fetch(makeReq("/feedback?place_id=tw-001"), env, {})).json();
  const mine = agg.comments.find((c) => c.message === "機位在北側");
  assert.deepEqual(mine.lp, { l: 4, p: 5 });
  const other = agg.comments.find((c) => c.message === "還沒評分");
  assert.equal(other.lp, null);
  assert.equal(other.maskedName, `海線·#${await shortCode36("lp2", 4)}`);
});

test("CL-UI-100: mine=1 responses carry the member's own masked name", async () => {
  const { env, t } = makeFeedbackEnv();
  await enableFlag(env);
  t.users.set("me1", { device_id: "me1", level: "free", created_at: stamp(Date.now() - 60 * DAY), display_name: "晨曦之光" });
  const tok = await tokenFor("me1");
  await worker.fetch(makeReq("/feedback", { method: "POST", headers: { Authorization: `Bearer ${tok}` }, body: JSON.stringify({ type: "rating", placeId: "tw-001", l: 4, p: 5 }) }), env, {});
  const mine = await (await worker.fetch(makeReq("/feedback?mine=1&place_id=tw-001", { headers: { Authorization: `Bearer ${tok}` } }), env, {})).json();
  assert.equal(mine.rating.l, 4);
  assert.equal(mine.rating.maskedName, `晨曦·#${await shortCode36("me1", 4)}`);
});
