// CL-APP-06 tests: custom places (private points). Kept in a SELF-CONTAINED
// file with its own mock D1 so in-flight sibling tickets (notify.test.js /
// worker.test.js owners) cannot collide. Covers the owner-ruled contract:
//   caps three states (free trial 3 / trial expired 0 / paid 50 / owner ∞)
//   trial boundary at users.created_at + 90d (all 3 points flip
//     trial_expired the moment it passes — evaluation stops, data kept)
//   CRUD permission (another member's place 404s)
//   daily add cooldown 60 (reminder at 50, 403 at the 61st)
//   rotation attack: no distinct-key budget blocks an add; daily fetches stay
//     constant at 60 (owner close-out ruling — the 30-day budget layer is gone)
//   soft delete + revive within 30d (no new fetch, no re-charge)
//   first fetch queued LOW priority; queue processing writes KV evals
//   global brake ladder (70% → batch ×0.9; 90% → refresh stop + honest labels)
//   nomination → feedback type=report routing_key=nomination (pending dup
//     409, 7-day throttle 429)
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import {
  TRIAL_DAYS, CAPS, DAILY_ADD_LIMIT, DAILY_ADD_REMINDER_AT,
  DEDUP_WINDOW_DAYS,  roundCoord, dedupeKey, trialState, capFor,
  evaluateCustomPlace, dominantFailWord, energySaverLevel,
  processCustomFetchQueue, globalUsageState, userFetchCount,
} from "../src/custom-places.js";
import { signJWT } from "../src/auth.js";

const DAY = 24 * 3_600_000;
let MOCKNOW = null; // tests can advance the mock clock for next-day pickup
const NOW = Date.now();
const dbStamp = (ms) => new Date(ms).toISOString().slice(0, 19).replace("T", " ");

// ------------------------------------------------------------------ mock D1
function parseAssignments(sql, args) {
  // "UPDATE custom_places SET name = ?2, lat = ?3, updated_at = datetime('now') WHERE ..."
  const set = sql.split(/SET /i)[1].split(/ WHERE /i)[0];
  const updates = {};
  for (const part of set.split(",")) {
    const p = part.trim();
    if (/^updated_at = datetime\('now'\)$/i.test(p)) { updates.updated_at = dbStamp(NOW); continue; }
    if (/^deleted_at = NULL$/i.test(p)) { updates.deleted_at = null; continue; }
    if (/^elevation = NULL$/i.test(p)) { updates.elevation = null; continue; }
    if (/^timezone = NULL$/i.test(p)) { updates.timezone = null; continue; }
    const m = p.match(/^(\w+) = \?(\d+)$/);
    if (m) updates[m[1]] = args[Number(m[2]) - 1];
    const lit = p.match(/^status = '(\w+)'$/);
    if (lit) updates.status = lit[1];
    const del = p.match(/^deleted_at = datetime\('now'\)$/);
    if (del) updates.deleted_at = dbStamp(NOW);
  }
  return updates;
}
function makeMockD1() {
  const t = { users: new Map(), custom_places: [], custom_fetch_queue: new Map(), feedback: [] };
  const inPlace = (row) => {
    t.custom_places.push(row);
    return { meta: { changes: 1 } };
  };
  const db = {
    _tables: t,
    prepare(sql) {
      const runner = (args) => ({
        run: async () => runSql(t, sql, args, db),
        first: async () => runFirst(t, sql, args, db),
        all: async () => runAll(t, sql, args, db),
      });
      return { ...runner([]), bind: (...a) => runner(a) };
    },
  };
  return db;
}
function cutoffIso(days, startOfDay = false) {
  const d = startOfDay ? new Date(new Date(NOW).toISOString().slice(0, 10) + "T00:00:00Z") : new Date(NOW - days * DAY);
  return dbStamp(d.getTime());
}
function runSql(t, sql, args, db) {
  if (/INSERT INTO custom_places/.test(sql)) {
    const [id, uid, name, lat, lng, elevation, timezone, cc] = args;
    t.custom_places.push({ id, user_id: uid, name, lat, lng, elevation, timezone, custom_conditions: cc, status: "active", created_at: dbStamp(NOW), updated_at: dbStamp(NOW), deleted_at: null });
    return { meta: { changes: 1 } };
  }
  if (/INSERT INTO custom_fetch_queue/.test(sql)) {
    const [placeId, uid] = args;
    const priority = /priority\) VALUES/.test(sql) ? args[3] : 20;
    const reason = /'new'/.test(sql) ? "new" : (/reason = 'refresh'/.test(sql) ? "refresh" : args[2] || "new");
    if (t.custom_fetch_queue.has(placeId) && /DO NOTHING/.test(sql)) return { meta: { changes: 0 } };
    t.custom_fetch_queue.set(placeId, { place_id: placeId, user_id: uid, reason, priority: priority ?? 20, due_at: dbStamp(NOW), status: "pending", updated_at: dbStamp(NOW) });
    return { meta: { changes: 1 } };
  }
  if (/INSERT INTO feedback/.test(sql)) {
    t.feedback.push({ id: args[0], user_id: args[1], place_id: args[2], type: "report", status: "pending", payload: args[3], created_at: dbStamp(NOW) });
    return { meta: { changes: 1 } };
  }
  if (/UPDATE custom_places SET status = 'trial_expired'/.test(sql)) {
    let n = 0;
    for (const r of t.custom_places) if (r.user_id === args[0] && r.status === "active") { r.status = "trial_expired"; n += 1; }
    return { meta: { changes: n } };
  }
  if (/UPDATE custom_places SET status = 'archived'/.test(sql)) {
    const r = t.custom_places.find((x) => x.id === args[0]);
    if (!r) return { meta: { changes: 0 } };
    r.status = "archived"; r.deleted_at = dbStamp(NOW); r.updated_at = dbStamp(NOW);
    return { meta: { changes: 1 } };
  }
  if (/UPDATE custom_places SET/.test(sql)) {
    const upd = parseAssignments(sql, args);
    const guardActive = /WHERE id = \?1 AND status = 'active'/.test(sql);
    const r = t.custom_places.find((x) => x.id === args[0] && (!guardActive || x.status === "active"));
    if (!r) return { meta: { changes: 0 } };
    Object.assign(r, upd);
    return { meta: { changes: 1 } };
  }
  if (/UPDATE custom_fetch_queue SET status = 'done'/.test(sql)) {
    const q = t.custom_fetch_queue.get(args[0]);
    if (!q) return { meta: { changes: 0 } };
    q.status = "done"; return { meta: { changes: 1 } };
  }
  if (/UPDATE custom_fetch_queue SET due_at = \?2/.test(sql)) {
    const q = t.custom_fetch_queue.get(args[0]);
    if (!q) return { meta: { changes: 0 } };
    q.due_at = args[1]; q.updated_at = dbStamp(NOW);
    return { meta: { changes: 1 } };
  }
  if (/DELETE FROM custom_fetch_queue/.test(sql)) {
    const had = t.custom_fetch_queue.delete(args[0]);
    return { meta: { changes: had ? 1 : 0 } };
  }
  return { meta: { changes: 0 } };
}
function runFirst(t, sql, args) {
  const u = sql.match(/SELECT device_id, level, created_at FROM users/);
  if (u) { const row = t.users.get(args[0]); return Promise.resolve(row || null); }
  if (/COUNT\(\*\) AS n FROM custom_places WHERE user_id = \?1 AND created_at/.test(sql)) {
    const cutoff = /start of day/.test(sql) ? cutoffIso(0, true) : cutoffIso(1);
    return Promise.resolve({ n: t.custom_places.filter((r) => r.user_id === args[0] && r.created_at >= cutoff).length });
  }
  if (/COUNT\(\*\) AS n FROM custom_places WHERE user_id = \?1 AND status != 'archived'/.test(sql)) {
    return Promise.resolve({ n: t.custom_places.filter((r) => r.user_id === args[0] && r.status !== "archived").length });
  }
  if (/COUNT\(\*\) AS n FROM \(SELECT DISTINCT/.test(sql)) {
    const cutoff = cutoffIso(DEDUP_WINDOW_DAYS);
    const seen = new Set();
    for (const r of t.custom_places) {
      if (r.user_id !== args[0]) continue;
      const active = r.status === "active" || (r.status === "archived" && r.deleted_at && r.deleted_at >= cutoff);
      if (!active) continue;
      seen.add(`${r.lat.toFixed(3)},${r.lng.toFixed(3)}`);
    }
    return Promise.resolve({ n: seen.size });
  }
  if (/SELECT id FROM custom_places WHERE user_id = \?1 AND ROUND\(lat,3\)/.test(sql)) {
    const cutoff = cutoffIso(DEDUP_WINDOW_DAYS);
    const r = t.custom_places.find((x) => x.user_id === args[0]
      && x.lat.toFixed(3) === Number(args[1]).toFixed(3) && x.lng.toFixed(3) === Number(args[2]).toFixed(3)
      && x.status === "archived" && x.deleted_at && x.deleted_at >= cutoff);
    return Promise.resolve(r ? { id: r.id } : null);
  }
  if (/SELECT id, user_id, name/.test(sql) && /FROM custom_places WHERE id = \?1/.test(sql)) {
    const r = t.custom_places.find((x) => x.id === args[0]);
    return Promise.resolve(r || null);
  }
  if (/SELECT due_at, status FROM custom_fetch_queue WHERE place_id = \?1/.test(sql)) {
    const q = t.custom_fetch_queue.get(args[0]);
    return Promise.resolve(q && q.status === "pending" ? { due_at: q.due_at, status: q.status } : null);
  }
  if (/UPDATE custom_fetch_queue SET due_at = \?2/.test(sql)) {
    const q = t.custom_fetch_queue.get(args[0]);
    if (!q) return Promise.resolve(null);
    q.due_at = args[1];
    return Promise.resolve({ due_at: q.due_at, status: q.status });
  }
  if (/FROM feedback WHERE user_id = \?1 AND place_id = \?2/.test(sql)) {
    const cutoff = /7 days|NOMINATION/.test(sql) ? cutoffIso(7) : null;
    const c = cutoffIso(30);
    const wantPending = /status = 'pending'/.test(sql);
    const rows = t.feedback.filter((f) => f.user_id === args[0] && f.place_id === args[1]
      && (!wantPending || f.status === 'pending')
      && (cutoff ? f.created_at >= cutoff : true));
    const r = rows[rows.length - 1];
    return Promise.resolve(r ? { id: r.id, status: r.status } : null);
  }
  return Promise.resolve(null);
}
function runAll(t, sql, args) {
  if (/FROM custom_places WHERE user_id = \?1 AND status != 'archived' ORDER BY created_at DESC/.test(sql)) {
    const rows = t.custom_places.filter((r) => r.user_id === args[0] && r.status !== "archived")
      .sort((a, b) => b.created_at.localeCompare(a.created_at));
    return Promise.resolve({ results: rows });
  }
  if (/FROM custom_fetch_queue q WHERE q.status = 'pending'/.test(sql)) {
    const cutoff = dbStamp(MOCKNOW ?? NOW);
    const rows = [...t.custom_fetch_queue.values()]
      .filter((q) => q.status === "pending" && q.due_at <= cutoff)
      .sort((a, b) => a.priority - b.priority || a.due_at.localeCompare(b.due_at))
      .slice(0, args[0]);
    return Promise.resolve({ results: rows });
  }
  return Promise.resolve({ results: [] });
}

function makeEnv(opts = {}) {
  const store = new Map(Object.entries(opts.kv || {}));
  const kv = {
    get: async (k, type) => { const v = store.has(k) ? store.get(k) : null; return v !== null && type === "json" ? JSON.parse(v) : v; },
    put: async (k, v) => { store.set(k, v); },
    _store: store,
  };
  const db = opts.db || makeMockD1();
  return { env: { EVALS: kv, DB: db, AUTH_SECRET: "test-secret" }, db };
}
let reqIpCounter = 0;
function makeReq(path, opts = {}) {
  const headers = new Headers(opts.headers || {});
  // A fresh IP per request keeps the worker's per-IP write-class limiter out
  // of these contract tests (it is covered by worker.test.js).
  headers.set("CF-Connecting-IP", `10.${reqIpCounter >> 8 & 255}.${reqIpCounter & 255}.${(reqIpCounter = (reqIpCounter + 1) % 65536) & 255}`);
  return new Request(`https://chaselights.app/api/v1${path}`, { ...opts, headers });
}
async function mint(env, sub, level = "paid") {
  return signJWT({ sub, name: "T", level, typ: "access", exp: Math.floor(Date.now() / 1000) + 600 }, env.AUTH_SECRET);
}
function seedUser(db, id, level, createdDaysAgo = 400) {
  db._tables.users.set(id, { device_id: id, level, created_at: dbStamp(NOW - createdDaysAgo * DAY) });
}
const hdr = (token) => ({ "Content-Type": "application/json", Authorization: `Bearer ${token}` });

// ---------------------------------------------------------------- pure logic
test("capFor: free trial 3 / expired 0 / paid 50 / owner unlimited / freeAsPaid lifts free", () => {
  assert.equal(capFor("free", false), CAPS.freeTrial);
  assert.equal(capFor("free", true), CAPS.freeExpired);
  assert.equal(capFor("paid", true), 50);            // paid ignores the trial
  assert.equal(capFor("owner", true), Infinity);
  assert.equal(capFor("free", false, true), 50);     // gray flag: free tests at paid
});
test("trialState: 90-day boundary from users.created_at (UTC-normalized D1 stamps)", () => {
  const d1 = dbStamp(NOW - (TRIAL_DAYS - 1) * DAY);   // 89d ago → inside
  const d2 = dbStamp(NOW - TRIAL_DAYS * DAY);         // exactly 90d ago → expired
  assert.equal(trialState({ created_at: d1 }, NOW).expired, false);
  assert.equal(trialState({ created_at: d2 }, NOW).expired, true);
});
test("roundCoord/dedupeKey: 0.001° dedupe key", () => {
  assert.equal(roundCoord(24.82254), 24.823);
  assert.equal(roundCoord(-121.76751), -121.768);
  assert.equal(dedupeKey(24.82254, 121.76749), "24.823,121.767");
});
test("evaluateCustomPlace: pending/rec/no via CL-UI-99 engine; shoot via lenient general baseline", () => {
  const now = Date.parse("2026-11-15T12:00:00+08:00");
  const hourly = [];
  for (let i = 0; i < 24; i++) {
    hourly.push({ local_date: "2026-11-15", hour: `${String(i).padStart(2, "0")}:00`, values: { cloud_low: 90, precipitation: 0, visibility: 20, wind: 2 } });
  }
  assert.deepEqual(evaluateCustomPlace(null, null, now), { tier: "pending", reason: null, window: null });
  const rec = { hourly };
  const cc = { cloud_low_max: 20 };
  const e = evaluateCustomPlace(cc, rec, now);
  assert.equal(e.tier, "no");
  assert.equal(e.reason, "低雲");
  // relax the condition → rec with the matching window
  const e2 = evaluateCustomPlace({ cloud_low_max: 90 }, rec, now);
  assert.equal(e2.tier, "rec");
  assert.match(e2.window, /2026-11-15 \d\d:00/);
  // no conditions: baseline (rain/vis/wind) passes → shoot
  const e3 = evaluateCustomPlace(null, rec, now);
  assert.equal(e3.tier, "shoot");
  // baseline fails on rain → no + 雨
  const rainy = hourly.map((h) => ({ ...h, values: { ...h.values, precipitation: 9 } }));
  const e4 = evaluateCustomPlace(null, { hourly: rainy }, now);
  assert.equal(e4.tier, "no");
  assert.equal(e4.reason, "雨");
});
test("dominantFailWord: largest violation share wins; visibility floor direction", () => {
  const now = Date.parse("2026-11-15T12:00:00+08:00");
  const hourly = [];
  for (let i = 0; i < 20; i++) hourly.push({ local_date: "2026-11-15", hour: `${String(i).padStart(2, "0")}:00`, values: { cloud_low: 5, cloud_mid: 5, cloud_high: 5, precipitation: 0, visibility: 1, wind: 2 } });
  hourly.push({ local_date: "2026-11-16", hour: "09:00", values: { cloud_low: 95, cloud_mid: 5, cloud_high: 5, precipitation: 0, visibility: 20, wind: 2 } });
  assert.equal(dominantFailWord(hourly, { visibility_min_km: 3, cloud_low_max: 90 }, now), "霧");
  assert.equal(dominantFailWord(hourly, { cloud_low_max: 90 }, now), "低雲");
});
test("energySaverLevel: top-1% daily / persistent top-0.1% every-2-days / normal", () => {
  const users = {}; for (let i = 0; i < 200; i++) users[`u${i}`] = { count: 300 - i };
  assert.equal(energySaverLevel(users, "u0").level, "every-2-days");  // top 0.1%
  assert.equal(energySaverLevel(users, "u1").level, "daily");         // top 1%
  assert.equal(energySaverLevel(users, "u50").level, "normal");
  assert.equal(energySaverLevel(users, "nobody").level, "normal");
  assert.equal(energySaverLevel({ a: { count: 3 } }, "a").level, "normal"); // below min volume
});

// ---------------------------------------------------------------- contract
test("contract: 401 without session; POST validates name/lat/lng/elevation bounds", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u1", "paid");
  const anon = await worker.fetch(makeReq("/custom_places"), env, {});
  assert.equal(anon.status, 401);
  const t = await mint(env, "u1");
  const noName = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ lat: 24.8, lng: 121.7 }) }), env, {});
  assert.equal(noName.status, 400);
  const badLat = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "X", lat: 95, lng: 121 }) }), env, {});
  assert.equal(badLat.status, 400);
  const badElev = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "X", lat: 24.8, lng: 121.7, elevation: 99999 }) }), env, {});
  assert.equal(badElev.status, 400);
  const badCc = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "X", lat: 24.8, lng: 121.7, customConditions: { cloud_low_max: 999 } }) }), env, {});
  assert.equal(badCc.status, 400);
});

test("caps: paid member up to 50, the 51st is 403 with grandfather-keeping copy", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u1", "paid");
  const t = await mint(env, "u1");
  for (let i = 0; i < 50; i++) {
    const res = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: `p${i}`, lat: 24 + i * 0.01, lng: 121 + i * 0.01 }) }), env, {});
    assert.equal(res.status, 200, `add #${i + 1}`);
  }
  // no other gate may fire before the 50-cap (the 30-day budget layer was removed)
  const res51 = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "p51", lat: 25.6, lng: 121.6 }) }), env, {});
  assert.equal(res51.status, 403);
  const body = await res51.json();
  assert.equal(body.reason, "paid_cap");
  assert.equal(body.cap, 50);
  assert.match(body.message["zh-TW"], /50/);
  const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb = await list.json();
  assert.equal(lb.places.length, 50);
  assert.equal(lb.quota.cap, 50);
});

test("owner: unlimited cap (quota.cap null, no 403)", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "o1", "owner");
  const t = await mint(env, "o1");
  for (let i = 0; i < 55; i++) {
    const res = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: `o${i}`, lat: 10 + i * 0.5, lng: 100 + i * 0.5 }) }), env, {});
    assert.equal(res.status, 200);
  }
  const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb = await list.json();
  assert.equal(lb.places.length, 55);
  assert.equal(lb.quota.cap, null);
});

test("trial boundary: free member holds 3 within 90 days; at expiry all 3 flip trial_expired and adds are 403 (cap 0)", async () => {
  const { env, db } = makeEnv();
  // member created 89 days ago — inside the trial
  seedUser(db, "f1", "free", TRIAL_DAYS - 1);
  const t = await mint(env, "f1");
  for (let i = 0; i < 3; i++) {
    const res = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: `f${i}`, lat: 24 + i * 0.1, lng: 121 + i * 0.1 }) }), env, {});
    assert.equal(res.status, 200);
  }
  const over = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "f4", lat: 25, lng: 121 }) }), env, {});
  assert.equal(over.status, 403);
  assert.equal((await over.json()).reason, "trial_cap");

  // age the account past the boundary → the SAME GET sweeps all 3 to trial_expired
  db._tables.users.get("f1").created_at = dbStamp(NOW - TRIAL_DAYS * DAY);
  const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb = await list.json();
  assert.equal(lb.level, "free-expired");
  assert.equal(lb.trial.expired, true);
  assert.equal(lb.places.length, 3, "data kept — hidden from default list, gray in private view");
  assert.ok(lb.places.every((p) => p.status === "trial_expired"));
  assert.ok(lb.places.every((p) => p.evaluation.tier === "pending"), "evaluation stopped");
  const after = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "f5", lat: 26, lng: 122 }) }), env, {});
  assert.equal(after.status, 403);
  assert.equal((await after.json()).reason, "trial_expired");
});

test("daily add cooldown: reminder rides the 50th add; the 61st is 403 單日上限 60 個", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "o2", "owner");
  const t = await mint(env, "o2");
  let reminderAt50 = null;
  for (let i = 0; i < 60; i++) {
    const res = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: `d${i}`, lat: -40 + i * 0.5, lng: 20 + i * 0.5 }) }), env, {});
    assert.equal(res.status, 200, `daily add #${i + 1}`);
    const body = await res.json();
    assert.equal(body.dailyAdds, i + 1);
    assert.equal(body.dailyRemaining, 60 - (i + 1));
    if (i + 1 === DAILY_ADD_REMINDER_AT) reminderAt50 = body;
  }
  assert.equal(reminderAt50.reminder["zh-TW"], "今日已新增 50 個景點，單日上限 60 個。");
  assert.equal(reminderAt50.dailyRemaining, 10);
  const res61 = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "d61", lat: -10, lng: 51 }) }), env, {});
  assert.equal(res61.status, 403);
  const b61 = await res61.json();
  assert.equal(b61.reason, "daily_add");
  assert.equal(b61.limit, DAILY_ADD_LIMIT);
  assert.equal(b61.message["zh-TW"], "單日上限 60 個，明天再繼續。");
});

test("rotation attack (owner ruling: the 30-day distinct budget layer is REMOVED): churn never blocks an add; daily fetches stay constant at 60", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "rot1", "paid"); // cap 50
  const t = await mint(env, "rot1");
  const t2 = db._tables;
  const restore = await stubFetch(async () => omGood());
  try {
    // churn: 60 DISTINCT coords, deleting every other place to stay under the
    // 50-active cap — every add succeeds (no distinct-key rejection exists)
    let distinct30d = null;
    for (let i = 0; i < 60; i++) {
      const res = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: `r${i}`, lat: -60 + i * 0.3, lng: 60 + i * 0.3 }) }), env, {});
      assert.equal(res.status, 200, `rotation add #${i + 1} must never be blocked by a distinct-key budget`);
      const b = await res.json();
      assert.notEqual(b.reason, "budget");
      if (b.internal && typeof b.internal.distinct30d === "number") distinct30d = b.internal.distinct30d;
      if (i % 2 === 1) {
        const del = await worker.fetch(makeReq(`/custom_places/${b.id}`, { method: "DELETE", headers: hdr(t) }), env, {});
        assert.equal(del.status, 200);
      }
    }
    assert.equal(distinct30d, 59, "30-day distinct telemetry is recorded internally (pre-insert count, never a gate)");
    // the owner-ruled cost ceiling is the DAILY FETCH BUDGET: exactly 60
    // actual fetches per day regardless of rotation churn — excess defers.
    // 30 adds still queue (deleted ones dropped their entries); +35 seeded.
    for (let i = 0; i < 35; i++) {
      const pid = `rotx-${i}`;
      t2.custom_places.push({ id: pid, user_id: "rot1", name: `x${i}`, lat: -20 + i * 0.1, lng: 70 + i * 0.1, elevation: null, timezone: null, custom_conditions: null, status: "active", created_at: dbStamp(NOW), updated_at: dbStamp(NOW), deleted_at: null });
      t2.custom_fetch_queue.set(pid, { place_id: pid, user_id: "rot1", reason: "new", priority: 20, due_at: dbStamp(NOW), status: "pending", updated_at: dbStamp(NOW) });
    }
    const s = await processCustomFetchQueue(env, NOW, { batch: 100 });
    assert.equal(s.processed, 60, "daily fetches stay constant at 60 under rotation attack");
    assert.equal(s.deferred, 5, "the 5 excess entries defer, not fail");
    assert.equal(await userFetchCount(env, "rot1", NOW), 60);
    for (const id of s.deferredPlaces) {
      assert.ok(db._tables.custom_fetch_queue.get(id).due_at > dbStamp(NOW), "deferred entry moves to the next day");
    }
  } finally { restore(); }
});

test("soft delete + revive: same coords@0.001° within 30d revives with existing id, no new fetch, no re-charge", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u3", "paid");
  const t = await mint(env, "u3");
  const c = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "A", lat: 24.82254, lng: 121.76749 }) }), env, {});
  const { id } = await c.json();
  assert.equal(db._tables.custom_fetch_queue.get(id).reason, "new", "first fetch queued low priority");
  const del = await worker.fetch(makeReq(`/custom_places/${id}`, { method: "DELETE", headers: hdr(t) }), env, {});
  assert.equal(del.status, 200);
  assert.match((await del.json()).note["zh-TW"], /30 天/);
  assert.equal(db._tables.custom_places[0].status, "archived");
  assert.ok(db._tables.custom_places[0].deleted_at, "deleted_at stamped");
  assert.equal(db._tables.custom_fetch_queue.has(id), false, "pending fetch for an archived place is dropped");
  const gone = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  assert.equal((await gone.json()).places.length, 0, "archived rows are hidden from the list");

  const re = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "A2", lat: 24.8226, lng: 121.7674 }) }), env, {});
  assert.equal(re.status, 200);
  const rb = await re.json();
  assert.equal(rb.revived, true);
  assert.equal(rb.id, id, "same dedupe key revives the SAME row");
  assert.equal(db._tables.custom_places[0].name, "A2");
  assert.equal(db._tables.custom_places[0].status, "active");
  assert.equal(db._tables.custom_fetch_queue.get(id), undefined, "revive does NOT re-queue a fetch");
  // 31+ days old archived row does NOT revive — a new row is created
  db._tables.custom_places[0].deleted_at = cutoffIso(DEDUP_WINDOW_DAYS + 1);
  const fresh = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "B", lat: 24.8226, lng: 121.7674 }) }), env, {});
  assert.equal(fresh.status, 200);
  const fb = await fresh.json();
  assert.notEqual(fb.id, id);
  assert.equal(fb.revived, undefined);
  assert.equal(db._tables.custom_fetch_queue.get(fb.id).reason, "new");
});

test("CRUD permission: another member's place 404s on PATCH/DELETE/nominate", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "a", "paid"); seedUser(db, "b", "paid");
  const ta = await mint(env, "a");
  const tb = await mint(env, "b");
  const c = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(ta), body: JSON.stringify({ name: "A", lat: 24, lng: 121 }) }), env, {});
  const { id } = await c.json();
  const patch = await worker.fetch(makeReq(`/custom_places/${id}`, { method: "PATCH", headers: hdr(tb), body: JSON.stringify({ name: "hack" }) }), env, {});
  assert.equal(patch.status, 404);
  const del = await worker.fetch(makeReq(`/custom_places/${id}`, { method: "DELETE", headers: hdr(tb) }), env, {});
  assert.equal(del.status, 404);
  const nom = await worker.fetch(makeReq(`/custom_places/${id}`, { method: "POST", headers: hdr(tb) }), env, {});
  assert.equal(nom.status, 404);
  const patchOk = await worker.fetch(makeReq(`/custom_places/${id}`, { method: "PATCH", headers: hdr(ta), body: JSON.stringify({ name: "A2", customConditions: { cloud_low_max: 20 } }) }), env, {});
  assert.equal(patchOk.status, 200);
  assert.equal(db._tables.custom_places[0].name, "A2");
  assert.equal(db._tables.custom_fetch_queue.get(id).reason, "refresh", "condition change re-queues a refresh");
});

test("nomination: feedback type=report routing_key=nomination pending; dup 409; 7-day throttle 429", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u4", "paid");
  const t = await mint(env, "u4");
  const c = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "礁溪自家陽台", lat: 24.8225, lng: 121.7675, elevation: 80 }) }), env, {});
  const { id } = await c.json();
  const nom = await worker.fetch(makeReq(`/custom_places/${id}`, { method: "POST", headers: hdr(t) }), env, {});
  assert.equal(nom.status, 200);
  const nb = await nom.json();
  assert.equal(nb.routingKey, "nomination");
  assert.equal(nb.status, "pending");
  const frow = db._tables.feedback[0];
  assert.equal(frow.type, "report");
  assert.equal(frow.status, "pending");
  assert.equal(frow.place_id, `custom:${id}`);
  const payload = JSON.parse(frow.payload);
  assert.equal(payload.routing_key, "nomination");
  assert.equal(payload.name, "礁溪自家陽台");
  const dup = await worker.fetch(makeReq(`/custom_places/${id}`, { method: "POST", headers: hdr(t) }), env, {});
  assert.equal(dup.status, 409);
  // resolve the pending ticket admin-side, then an immediate re-nominate hits the 7-day throttle
  db._tables.feedback[0].status = "ok";
  const again = await worker.fetch(makeReq(`/custom_places/${id}`, { method: "POST", headers: hdr(t) }), env, {});
  assert.equal(again.status, 429);
  assert.match((await again.json()).message["zh-TW"], /7 天/);
});

// ---------------------------------------------------------------- queue/brake
async function stubFetch(fn) {
  const real = globalThis.fetch;
  globalThis.fetch = fn;
  return () => { globalThis.fetch = real; };
}
test("queue: low-priority first fetch; processing writes private=true KV eval rows (in→out batch)", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u5", "paid");
  const t = await mint(env, "u5");
  const c = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "Q", lat: 24.8, lng: 121.7 }) }), env, {});
  const { id } = await c.json();
  let list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  let lb = await list.json();
  assert.equal(lb.places[0].evaluation.tier, "pending", "honest 排隊中 before the first fetch lands");
  assert.equal(lb.places[0].evaluation.private, true);

  const omPayload = {
    elevation: 80, timezone: "Asia/Taipei",
    hourly: { time: Array.from({ length: 24 }, (_, i) => `${new Date(NOW + DAY).toISOString().slice(0, 10)}T${String(i).padStart(2, "0")}:00`),
      cloud_cover_low: Array(24).fill(10), cloud_cover_mid: Array(24).fill(20), cloud_cover_high: Array(24).fill(30),
      precipitation: Array(24).fill(0), visibility: Array(24).fill(20), wind_speed_10m: Array(24).fill(2) },
  };
  let omCalls = 0;
  const restore = await stubFetch(async () => { omCalls += 1; return { ok: true, json: async () => omPayload }; });
  try {
    const summary = await processCustomFetchQueue(env);
    assert.equal(summary.processed, 1);
    assert.equal(omCalls, 1);
  } finally { restore(); }
  const rec = JSON.parse(env.EVALS._store.get(`v1:evals:custom:${id}`));
  assert.equal(rec.private, true, "subject-cards private marking");
  assert.equal(rec.hourly.length, 24);
  assert.equal(rec.hourly[0].values.cloud_low, 10);
  assert.equal(db._tables.custom_places[0].timezone, "Asia/Taipei", "DEM/tz backfilled from the fetch");
  list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  lb = await list.json();
  assert.equal(lb.places[0].evaluation.tier, "shoot", "general baseline passes → ○可拍");
  assert.equal(lb.places[0].evaluation.evaluatedAt, rec.generated_at);
  assert.equal(db._tables.custom_fetch_queue.get(id).status, "done");
  const usage = await globalUsageState(env);
  assert.equal(usage.count, 1, "call counter incremented");
});

test("global brake ladder: ≥70% batch ×0.9; ≥90% refreshes stop + degraded honest labels", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u6", "owner");
  const t = await mint(env, "o6" in db._tables.users ? "o6" : "u6");
  // two places: one 'new', one 'refresh'
  const ids = [];
  for (let i = 0; i < 2; i++) {
    const res = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: `g${i}`, lat: 24 + i, lng: 121 + i }) }), env, {});
    ids.push((await res.json()).id);
  }
  db._tables.custom_fetch_queue.set(ids[1], { place_id: ids[1], user_id: "u6", reason: "refresh", priority: 20, due_at: dbStamp(NOW), status: "pending", updated_at: dbStamp(NOW) });
  const omPayload = { elevation: 5, timezone: "Asia/Taipei", hourly: { time: [`${new Date(NOW + DAY).toISOString().slice(0, 10)}T05:00`], cloud_cover_low: [10], cloud_cover_mid: [10], cloud_cover_high: [10], precipitation: [0], visibility: [20], wind_speed_10m: [2] } };
  const restore = await stubFetch(async () => ({ ok: true, json: async () => omPayload }));
  try {
    // 90% of budget → refresh stops, first fetch trickles (batch 3)
    env.EVALS._store.set(`v1:cp:global:${new Date(NOW).toISOString().slice(0, 10).replace(/-/g, "")}`, JSON.stringify({ count: Math.ceil(0.92 * 5000) }));
    const hard = await processCustomFetchQueue(env);
    assert.equal(hard.skipped_brake, 1, "refresh entry skipped by the hard brake");
    assert.equal(hard.processed, 1, "new-place first fetch still trickles");
    const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
    const lb = await list.json();
    assert.equal(lb.degraded, true);
    assert.match(lb.degradedMessage["zh-TW"], /資料更新延遲/);
    // 70% → batch ×0.9 (20 → 18), nothing skipped
    env.EVALS._store.set(`v1:cp:global:${new Date(NOW).toISOString().slice(0, 10).replace(/-/g, "")}`, JSON.stringify({ count: Math.ceil(0.71 * 5000) }));
    const soft = await processCustomFetchQueue(env, NOW, { batch: 20 });
    assert.equal(soft.processed, 1, "remaining refresh entry runs under the soft brake");
    assert.equal(soft.globalUsage.soft, true);
  } finally { restore(); }
});

// ------------------------------------------------- layer 3: daily fetch budget
const omGood = () => { const day = new Date(NOW + DAY).toISOString().slice(0, 10);
  return { ok: true, json: async () => ({
  elevation: 5, timezone: "Asia/Taipei",
  hourly: { time: [`${day}T05:00`, `${day}T06:00`, `${day}T07:00`], cloud_cover_low: [10, 10, 10], cloud_cover_mid: [10, 10, 10], cloud_cover_high: [10, 10, 10], precipitation: [0, 0, 0], visibility: [20, 20, 20], wind_speed_10m: [2, 2, 2] } }) }; };

test("layer 3 per-user daily fetch budget: 60/day hard — excess DEFERS to next day, points stay created", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "ch1", "owner");
  const tok = await mint(env, "ch1");
  const t = db._tables;
  const restore = await stubFetch(async () => omGood());
  try {
    // churn attack: 60 adds (the daily add cap) + 5 more pending queue
    // entries seeded directly — queue backlog beyond the add cap still defers
    const ids = [];
    for (let i = 0; i < 60; i++) {
      const res = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(tok), body: JSON.stringify({ name: `c${i}`, lat: -60 + i * 0.3, lng: 60 + i * 0.3 }) }), env, {});
      assert.equal(res.status, 200, "adds are never rejected by the fetch budget");
      ids.push((await res.json()).id);
    }
    for (let i = 0; i < 5; i++) {
      const pid = `seeded-${i}`;
      t.custom_places.push({ id: pid, user_id: "ch1", name: `s${i}`, lat: -60 + 60 * 0.3 + i, lng: 78 + i, elevation: null, timezone: null, custom_conditions: null, status: "active", created_at: dbStamp(NOW), updated_at: dbStamp(NOW), deleted_at: null });
      t.custom_fetch_queue.set(pid, { place_id: pid, user_id: "ch1", reason: "new", priority: 20, due_at: dbStamp(NOW), status: "pending", updated_at: dbStamp(NOW) });
      ids.push(pid);
    }
    const s1 = await processCustomFetchQueue(env, NOW, { batch: 100 });
    assert.equal(s1.processed, 60, "exactly 60 actual fetches (50 routine + 10 headroom)");
    assert.equal(s1.deferred, 5, "the 5 excess entries defer, not fail");
    assert.equal(s1.deferredPlaces.every((id) => db._tables.custom_fetch_queue.get(id).status === "pending"), true);
    for (const id of s1.deferredPlaces) {
      const due = db._tables.custom_fetch_queue.get(id).due_at;
      assert.ok(due > dbStamp(NOW), "deferred entry moves to the next day");
    }
    // cards stay honest: deferred points show tier pending + fetchDeferred
    const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(tok) }), env, {});
    const lb = await list.json();
    const deferredList = lb.places.filter((p) => p.fetchDeferred);
    assert.equal(deferredList.length, 5);
    assert.ok(deferredList.every((p) => p.evaluation.tier === "pending"), "no fabricated data on a deferred card");
    // next day: the counter reset lets the SAME entries through
    const tomorrow = NOW + DAY;
    MOCKNOW = tomorrow;
    const s2 = await processCustomFetchQueue(env, tomorrow, { batch: 100 });
    assert.equal(s2.processed, 5, "deferred entries are picked up once the daily counter resets");
    assert.equal(s2.deferred || 0, 0);
  } finally { restore(); }
});

test("layer 3: a normal 50-point member is unaffected (50 ≤ 60)", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "n50", "paid");
  const t = await mint(env, "n50");
  const restore = await stubFetch(async () => omGood());
  try {
    for (let i = 0; i < 50; i++) {
      const res = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: `n${i}`, lat: 30 + i * 0.1, lng: 130 + i * 0.1 }) }), env, {});
      assert.equal(res.status, 200);
    }
    const s = await processCustomFetchQueue(env, NOW, { batch: 100 });
    assert.equal(s.processed, 50);
    assert.equal(s.deferred || 0, 0);
    assert.equal(await userFetchCount(env, "n50", NOW), 50);
  } finally { restore(); }
});

// -------------------------------------------------- ✨ AI one-sentence parse
import { validateParseSuggestions, PARSE_DAILY_LIMIT } from "../src/custom-places.js";

const GOOD_SUGGESTION = { cloud: "min", fog: "none", rain: "no", wind_max_ms: 5, window_start: "04:30", window_end: "07:00", lead_minutes: 45, confidence: 0.8 };
function llmResponse(obj) {
  return async () => ({ ok: true, json: async () => ({ candidates: [{ content: { parts: [{ text: JSON.stringify(obj) }] } }] }) });
}

test("conditions/parse: config disabled without the key (fail-closed); POST 503s honestly", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u9", "paid");
  const t = await mint(env, "u9");
  const cfg = await worker.fetch(makeReq("/conditions/parse", { headers: hdr(t) }), env, {});
  assert.equal(cfg.status, 200);
  assert.equal((await cfg.json()).enabled, false);
  const post = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "清晨雲海不要雨" }) }), env, {});
  assert.equal(post.status, 503);
  assert.match((await post.json()).message["zh-TW"], /尚未啟用|金鑰/);
});

test("conditions/parse: trilingual inputs → strict schema suggestions; violations rejected; limit 10/day", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u10", "paid");
  const t = await mint(env, "u10");
  env.LLM_API_KEY = "TEST-KEY";
  const restore = await stubFetch(llmResponse(GOOD_SUGGESTION));
  try {
    // zh-TW / en / ja inputs share the same strict-JSON contract
    for (const text of ["清晨要看到雲海，不要下雨，04:30–07:00", "dawn cloud sea, no rain, window 04:30-07:00", "明け方の雲海、雨は嫌、4時半〜7時"]) {
      const res = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text }) }), env, {});
      assert.equal(res.status, 200);
      const body = await res.json();
      assert.equal(body.ok, true);
      assert.deepEqual(body.suggestions, GOOD_SUGGESTION);
    }
  } finally { restore(); }
  // schema violations are rejected 422 honestly (never applied)
  const bad = await stubFetch(llmResponse({ cloud: "monsters", confidence: 0.5 }));
  try {
    const res = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "x" }) }), env, {});
    assert.equal(res.status, 422);
    assert.match((await res.json()).message["zh-TW"], /解析失敗/);
  } finally { bad(); }
  // out-of-range numbers also violate
  assert.equal(validateParseSuggestions({ ...GOOD_SUGGESTION, wind_max_ms: 999 }).ok, false);
  assert.equal(validateParseSuggestions({ ...GOOD_SUGGESTION, window_start: "25:00" }).ok, false);
  assert.equal(validateParseSuggestions({ ...GOOD_SUGGESTION, confidence: 1.5 }).ok, false);
  assert.equal(validateParseSuggestions({ ...GOOD_SUGGESTION, lead_minutes: -1 }).ok, false);
  assert.equal(validateParseSuggestions({ ...GOOD_SUGGESTION, lead_minutes: null }).ok, true);
  // per-user 10/day budget: 3 used so far → 7 more pass, the 11th 403s
  const restore2 = await stubFetch(llmResponse(GOOD_SUGGESTION));
  try {
    for (let i = 0; i < 7; i++) {
      const res = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "x" }) }), env, {});
      assert.equal(res.status, 200, `parse #${i + 4}`);
    }
    const over = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "x" }) }), env, {});
    assert.equal(over.status, 403);
    const body = await over.json();
    assert.equal(body.limit, PARSE_DAILY_LIMIT);
    assert.match(body.message["zh-TW"], /每日 10 次/);
  } finally { restore2(); }
});
