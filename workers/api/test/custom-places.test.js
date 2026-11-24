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
  MAX_THEMES_PER_PLACE, validateThemeInput, validateThemeNameInput,
  evaluateThemeGroups, aggregateEvaluation,
} from "../src/custom-places.js";
// CL-APP-08: private-place grid dedup (owner-approved conservative version)
import {
  analyzeTerrain, haversineM, regroupExistingPlaces,
  SHARE_MAX_DIST_M, SHARE_MAX_ELEV_DIFF_M, SHARE_MAX_RELIEF_M, RIDGE_DETECT_M,
} from "../src/place-groups.js";
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
    if (/^group_id = NULL$/i.test(p)) { updates.group_id = null; continue; }
    if (/^custom_conditions = NULL$/i.test(p)) { updates.custom_conditions = null; continue; }
    const lit = p.match(/^(\w+) = '(\w+)'$/);
    if (lit) { updates[lit[1]] = lit[2]; continue; }
    const m = p.match(/^(\w+) = \?(\d+)$/);
    if (m) updates[m[1]] = args[Number(m[2]) - 1];
    const del = p.match(/^deleted_at = datetime\('now'\)$/);
    if (del) updates.deleted_at = dbStamp(NOW);
  }
  return updates;
}
// The place_id of a queue INSERT: the first bound arg (?1) — for the refetch
// and rep-redirect statements that is the row's own id.
function placeIdOf(sql, args) { return args[0]; }

function makeMockD1() {
  const t = { users: new Map(), custom_places: [], custom_place_themes: [], custom_fetch_queue: new Map(), feedback: [] };
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
  if (/INSERT INTO custom_place_themes/.test(sql)) {
    // two shapes: full insert (?1..?6 with name_i18n) and the lazy-backfill
    // insert (?1..?5 without it — column order id, place_id, user_id, name, conditions)
    const withI18n = /name_i18n/.test(sql);
    t.custom_place_themes.push({
      id: args[0], place_id: args[1], user_id: args[2], name: args[3],
      name_i18n: withI18n ? args[4] : null,
      conditions: withI18n ? args[5] : args[4],
      created_at: dbStamp(NOW), updated_at: dbStamp(NOW),
    });
    return { meta: { changes: 1 } };
  }
  if (/UPDATE custom_place_themes SET/.test(sql)) {
    const upd = parseAssignments(sql, args);
    const th = t.custom_place_themes.find((x) => x.id === args[0]);
    if (!th) return { meta: { changes: 0 } };
    Object.assign(th, upd);
    return { meta: { changes: 1 } };
  }
  if (/DELETE FROM custom_place_themes/.test(sql)) {
    const before = t.custom_place_themes.length;
    t.custom_place_themes = t.custom_place_themes.filter((x) => x.id !== args[0]);
    return { meta: { changes: before - t.custom_place_themes.length } };
  }
  if (/INSERT INTO custom_places/.test(sql)) {
    const [id, uid, name, lat, lng, elevation, timezone, cc] = args;
    t.custom_places.push({ id, user_id: uid, name, lat, lng, elevation, timezone, custom_conditions: cc, status: "active", group_id: null, share_mode: "auto", created_at: dbStamp(NOW), updated_at: dbStamp(NOW), deleted_at: null });
    return { meta: { changes: 1 } };
  }
  if (/INSERT INTO custom_fetch_queue/.test(sql)) {
    // reason/priority may be literals in the SQL text (refetch / rep redirect)
    const lit = sql.match(/VALUES \(\?1, \?2, '(\w+)', (\d+)\)/);
    const priority = lit ? Number(lit[2]) : (/priority\) VALUES/.test(sql) ? args[3] : 20);
    const reason = lit ? lit[1] : (/'new'/.test(sql) ? "new" : (/reason = 'refresh'/.test(sql) ? "refresh" : args[2] || "new"));
    if (t.custom_fetch_queue.has(placeIdOf(sql, args)) && /DO NOTHING/.test(sql)) return { meta: { changes: 0 } };
    const pid = placeIdOf(sql, args);
    const existed = t.custom_fetch_queue.get(pid);
    t.custom_fetch_queue.set(pid, { place_id: pid, user_id: existed ? existed.user_id : args[1], reason, priority: priority ?? 20, due_at: dbStamp(NOW), status: "pending", updated_at: dbStamp(NOW) });
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
  if (/SELECT COUNT\(\*\) AS n FROM custom_place_themes/.test(sql)) {
    return Promise.resolve({ n: t.custom_place_themes.filter((r) => r.place_id === args[0]).length });
  }
  if (/FROM custom_place_themes WHERE id = \?1 AND place_id = \?2/.test(sql)) {
    const r = t.custom_place_themes.find((x) => x.id === args[0] && x.place_id === args[1]);
    return Promise.resolve(r || null);
  }
  const u2 = sql.match(/SELECT level, created_at FROM users/);
  if (u2) { const row = t.users.get(args[0]); return Promise.resolve(row || null); }
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
  // Generic custom_places row lookup by id (item PATCH/DELETE, refetch, rep
  // lookup, regroup re-read). Optional "AND status = 'active'" gate honored.
  if (/FROM custom_places WHERE id = \?1( AND status = 'active')?$/.test(sql.trim())) {
    const r = t.custom_places.find((x) => x.id === args[0] && (/AND status = 'active'$/.test(sql) ? x.status === "active" : true));
    return Promise.resolve(r || null);
  }
  // CL-APP-08: group-member queries (rep promote / representative fallback).
  if (/FROM custom_places WHERE group_id = \?1 AND id != \?2 AND status = 'active' AND share_mode = 'auto' ORDER BY created_at ASC LIMIT 1/.test(sql)) {
    const r = t.custom_places.find((x) => x.group_id === args[0] && x.id !== args[1] && x.status === "active" && x.share_mode === "auto")
      || t.custom_places.filter((x) => x.group_id === args[0] && x.id !== args[1] && x.status === "active" && x.share_mode === "auto")
        .sort((a, b) => a.created_at.localeCompare(b.created_at))[0];
    return Promise.resolve(r || null);
  }
  if (/FROM custom_places WHERE group_id = \?1 AND status = 'active' AND share_mode = 'auto' ORDER BY created_at ASC LIMIT 1/.test(sql)) {
    const r = t.custom_places.filter((x) => x.group_id === args[0] && x.status === "active" && x.share_mode === "auto")
      .sort((a, b) => a.created_at.localeCompare(b.created_at))[0];
    return Promise.resolve(r || null);
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
  if (/FROM custom_place_themes WHERE place_id = \?1/.test(sql)) {
    const rows = t.custom_place_themes.filter((r) => r.place_id === args[0])
      .sort((a, b) => a.created_at.localeCompare(b.created_at) || a.id.localeCompare(b.id));
    return Promise.resolve({ results: rows });
  }
  if (/FROM custom_places WHERE user_id = \?1 AND status != 'archived' ORDER BY created_at DESC/.test(sql)) {
    const rows = t.custom_places.filter((r) => r.user_id === args[0] && r.status !== "archived")
      .sort((a, b) => b.created_at.localeCompare(a.created_at));
    return Promise.resolve({ results: rows });
  }
  // CL-APP-08: same-user dedup candidates for a new/ungrouped place.
  if (/FROM custom_places WHERE user_id = \?1 AND id != \?2 AND status = 'active' AND share_mode = 'auto' AND lat BETWEEN/.test(sql)) {
    const rows = t.custom_places.filter((r) => r.user_id === args[0] && r.id !== args[1]
      && r.status === "active" && r.share_mode === "auto"
      && r.lat >= args[2] && r.lat <= args[3] && r.lng >= args[4] && r.lng <= args[5])
      .sort((a, b) => a.created_at.localeCompare(b.created_at));
    return Promise.resolve({ results: rows });
  }
  // CL-APP-08: fan-out members of a group (active, auto mode).
  if (/FROM custom_places WHERE group_id = \?1 AND id != \?2 AND status = 'active' AND share_mode = 'auto'$/.test(sql.trim())) {
    const rows = t.custom_places.filter((r) => r.group_id === args[0] && r.id !== args[1] && r.status === "active" && r.share_mode === "auto");
    return Promise.resolve({ results: rows });
  }
  // CL-APP-08: the background re-group sweep input (ungrouped active places).
  if (/FROM custom_places WHERE status = 'active' AND share_mode = 'auto' AND group_id IS NULL ORDER BY user_id, created_at ASC LIMIT/.test(sql)) {
    const rows = t.custom_places.filter((r) => r.status === "active" && r.share_mode === "auto" && r.group_id == null)
      .sort((a, b) => a.user_id.localeCompare(b.user_id) || a.created_at.localeCompare(b.created_at))
      .slice(0, args[0]);
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
    delete: async (k) => { store.delete(k); },
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
// ------------------------------------------ patch-5 ④: 適用月份 month window
import { validateCustomConditions, findNextCustomWindow } from "../src/notify.js";
test("patch-5 ④: months validation — 1..12 ints, dedupe+sort, empty rejected (omit = all year)", () => {
  assert.deepEqual(validateCustomConditions({ months: [4, 3, 4] }).cc.months, [3, 4]);
  assert.deepEqual(validateCustomConditions({}).cc, null);
  assert.equal(validateCustomConditions({ months: [] }).ok, false);
  assert.equal(validateCustomConditions({ months: [13] }).ok, false);
  assert.equal(validateCustomConditions({ months: [0] }).ok, false);
  assert.equal(validateCustomConditions({ months: [3.5] }).ok, false);
  assert.equal(validateCustomConditions({ months: "3" }).ok, false);
});
test("patch-5 ④: month window — findNextCustomWindow skips out-of-month rows; evaluateCustomPlace reports honest 非適用月份 (never a weather word)", () => {
  const now = Date.parse("2026-11-15T12:00:00+08:00");
  const hourly = [];
  for (let i = 0; i < 24; i++) hourly.push({ local_date: "2026-11-15", hour: `${String(i).padStart(2, "0")}:00`, values: { cloud_low: 10, precipitation: 0, visibility: 20, wind: 2 } });
  // month included → rec even though other params would pass anyway
  const inWin = findNextCustomWindow(hourly, { cloud_low_max: 50, months: [11] }, now, 0);
  assert.ok(inWin && /2026-11-15 \d\d:00/.test(inWin.window || `${inWin.local_date} ${inWin.hour}`));
  // month excluded → null + honest eligibility reason, NOT 低雲/雨 etc.
  assert.equal(findNextCustomWindow(hourly, { cloud_low_max: 50, months: [6] }, now, 0), null);
  const e = evaluateCustomPlace({ cloud_low_max: 50, months: [6] }, { hourly }, now);
  assert.equal(e.tier, "no");
  assert.equal(e.reason, "非適用月份");
});
// ----------------------------------- patch-7: private-card forecast popup endpoint
test("patch-7: GET /custom_places/:id/eval — owner-only stored eval; queued 404 honest; trial-expired 403", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u1", "paid");
  const t = await mint(env, "u1");
  const add = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "私點", lat: 24.8, lng: 121.7 }) }), env, {});
  assert.equal(add.status, 200);
  const id = (await add.json()).id;
  // no stored eval yet → honest 404 with fetchQueued (never fabricated rows)
  const none = await worker.fetch(makeReq(`/custom_places/${id}/eval`, { headers: hdr(t) }), env, {});
  assert.equal(none.status, 404);
  assert.equal((await none.json()).fetchQueued, true);
  // stored eval → 200 with the SAME hourly the tier engine reads
  const hourly = [{ local_date: "2026-01-01", hour: "05:00", values: { cloud_low: 10, precipitation: 0, visibility: 20000, wind: 2 } }];
  env.EVALS._store.set(`v1:evals:custom:${id}`, JSON.stringify({ place_id: id, hourly, generated_at: "2026-01-01T00:00:00Z", elevation: 80, timezone: "Asia/Taipei" }));
  const ok = await worker.fetch(makeReq(`/custom_places/${id}/eval`, { headers: hdr(t) }), env, {});
  assert.equal(ok.status, 200);
  const ob = await ok.json();
  assert.equal(ob.ok, true);
  assert.deepEqual(ob.hourly, hourly);
  assert.equal(ob.generatedAt, "2026-01-01T00:00:00Z");
  assert.equal(ob.timezone, "Asia/Taipei");
  // another member's place simply does not exist (same CRUD rule as PATCH/DELETE)
  seedUser(db, "u2", "paid");
  const t2 = await mint(env, "u2");
  const other = await worker.fetch(makeReq(`/custom_places/${id}/eval`, { headers: hdr(t2) }), env, {});
  assert.equal(other.status, 404);
  // trial expired → evaluation stopped (data kept), honest 403
  db._tables.users.set("u1", { device_id: "u1", level: "free", created_at: dbStamp(NOW - TRIAL_DAYS * DAY) });
  const t1b = await mint(env, "u1");
  const expired = await worker.fetch(makeReq(`/custom_places/${id}/eval`, { headers: hdr(t1b) }), env, {});
  assert.equal(expired.status, 403);
});

// --------------------------- patch-8: multi-theme condition groups per place
const themeDay = new Date(NOW + DAY).toISOString().slice(0, 10); // tomorrow — inside the 24h judgment horizon
const themeHourly = () => {
  const out = [];
  for (let i = 0; i < 24; i++) {
    out.push({ local_date: themeDay, hour: `${String(i).padStart(2, "0")}:00`,
      values: { cloud_low: 10, cloud_mid: 20, cloud_high: 30, precipitation: 0, visibility: 20, wind: 2 } });
  }
  return out;
};

test("patch-8: theme CRUD — create rides GET with per-group tiers; PATCH renames + re-sets conditions; DELETE removes; duplicate names NOT blocked; NO fetch, NO quota", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "m8", "paid");
  const t = await mint(env, "m8");
  const c = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "私點", lat: 24.8, lng: 121.7 }) }), env, {});
  const id = (await c.json()).id;
  env.EVALS._store.set(`v1:evals:custom:${id}`, JSON.stringify({ place_id: id, hourly: themeHourly(), generated_at: "2026-11-15T00:00:00Z" }));

  // create ×2 with the SAME name — duplicate names are deliberately NOT blocked
  const p1 = { name: "雲海窗", nameI18n: { "zh-TW": "雲海窗", en: "Cloud sea" }, conditions: { cloud_low_max: 20, window_start: "04:30", window_end: "07:00" } };
  const r1 = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify(p1) }), env, {});
  assert.equal(r1.status, 200);
  const b1 = await r1.json();
  assert.equal(b1.themes.used, 1);
  const r2 = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "雲海窗", conditions: { cloud_low_max: 50 } }) }), env, {});
  assert.equal(r2.status, 200, "duplicate name is NOT blocked (owner ruling)");
  const b2 = await r2.json();
  assert.notEqual(b2.id, b1.id);
  assert.equal(b2.themes.used, 2);

  // GET: both groups ride the list payload with same-source per-group tiers
  const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb = await list.json();
  const place = lb.places.find((p) => p.id === id);
  assert.equal(place.themeGroups.length, 2);
  assert.equal(place.themes.used, 2);
  assert.equal(place.themes.cap, MAX_THEMES_PER_PLACE);
  const gFirst = place.themeGroups.find((g) => g.id === b1.id);
  assert.equal(gFirst.name, "雲海窗");
  assert.deepEqual(gFirst.nameI18n, { "zh-TW": "雲海窗", en: "Cloud sea" });
  assert.equal(gFirst.evaluation.tier, "rec", "per-group tier from the SAME evaluateCustomPlace machinery");
  assert.match(gFirst.evaluation.window, new RegExp(`${themeDay} 0\\d:00`));
  assert.equal(place.themeGroups[0].evaluation.tier, "rec");
  assert.equal(place.evaluation.tier, "rec", "aggregate: any rec → rec");

  // PATCH: rename + re-set conditions; then the tier follows the new blob
  const tid1 = b1.id;
  const up = await worker.fetch(makeReq(`/custom_places/${id}/themes/${tid1}`, { method: "PATCH", headers: hdr(t), body: JSON.stringify({ name: "星空窗", conditions: { cloud_low_max: 10 } }) }), env, {});
  assert.equal(up.status, 200);
  const list2 = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb2 = await list2.json();
  const g1 = lb2.places.find((p) => p.id === id).themeGroups.find((g) => g.id === tid1);
  assert.equal(g1.name, "星空窗");
  assert.equal(g1.evaluation.tier, "rec", "10% low cloud ≤ the 20%-clean hour → still rec");

  // DELETE removes the group
  const del = await worker.fetch(makeReq(`/custom_places/${id}/themes/${tid1}`, { method: "DELETE", headers: hdr(t) }), env, {});
  assert.equal(del.status, 200);
  const list3 = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb3 = await list3.json();
  assert.equal(lb3.places.find((p) => p.id === id).themeGroups.length, 1);

  // NO fetch, NO quota: theme CRUD never touches the queue or the daily budget
  // (the ONE 'new' entry was created with the place itself — it never grows)
  assert.equal(db._tables.custom_fetch_queue.size, 1, "only the place's own first-fetch entry exists");
  assert.equal(await userFetchCount(env, "m8"), 0, "the daily fetch budget is NOT consumed");
  const usage = await globalUsageState(env);
  assert.equal(usage.count, 0, "the global fetch counter is NOT consumed");

  // another member's place/theme simply does not exist
  seedUser(db, "m9", "paid");
  const t9 = await mint(env, "m9");
  const other = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t9), body: JSON.stringify({ name: "X", conditions: { cloud_low_max: 20 } }) }), env, {});
  assert.equal(other.status, 404);
  const other2 = await worker.fetch(makeReq(`/custom_places/${id}/themes/${tid1}`, { method: "DELETE", headers: hdr(t9) }), env, {});
  assert.equal(other2.status, 404);
});

test("patch-8: cap 5 groups per place → the 6th is 403 theme_cap; validation honest (name required, non-empty conditions)", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "m8c", "paid");
  const t = await mint(env, "m8c");
  const c = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "私點", lat: 24.8, lng: 121.7 }) }), env, {});
  const id = (await c.json()).id;
  for (let i = 0; i < MAX_THEMES_PER_PLACE; i++) {
    const r = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify({ name: `g${i}`, conditions: { cloud_low_max: 20 } }) }), env, {});
    assert.equal(r.status, 200, `theme #${i + 1}`);
  }
  const over = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "g6", conditions: { cloud_low_max: 20 } }) }), env, {});
  assert.equal(over.status, 403);
  const ob = await over.json();
  assert.equal(ob.reason, "theme_cap");
  assert.equal(ob.cap, 5);
  assert.match(ob.message["zh-TW"], /最多 5 組/);
  // honest validation
  const noName = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify({ conditions: { cloud_low_max: 20 } }) }), env, {});
  assert.equal(noName.status, 400);
  assert.match((await noName.json()).message["zh-TW"], /題材名稱/);
  const noCc = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "X" }) }), env, {});
  assert.equal(noCc.status, 400);
  assert.match((await noCc.json()).message["zh-TW"], /至少設定一組條件/);
  const badCc = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "X", conditions: { cloud_low_max: 999 } }) }), env, {});
  assert.equal(badCc.status, 400);
  // DELETE one → the cap frees up again
  const tid = db._tables.custom_place_themes[0].id;
  await worker.fetch(makeReq(`/custom_places/${id}/themes/${tid}`, { method: "DELETE", headers: hdr(t) }), env, {});
  const again = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "g6", conditions: { cloud_low_max: 20 } }) }), env, {});
  assert.equal(again.status, 200, "after a delete the 6th add passes");
});

test("CL-APP-10: deleting the LAST theme group does NOT resurrect the legacy blob as a 山景 group", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "m10", "paid");
  const t = await mint(env, "m10");
  // created WITH a legacy blob → the lazy backfill turns it into one group
  const c = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "私點", lat: 24.8, lng: 121.7, customConditions: { cloud_low_max: 20, window_start: "05:00", window_end: "07:00" } }) }), env, {});
  const id = (await c.json()).id;
  env.EVALS._store.set(`v1:evals:custom:${id}`, JSON.stringify({ place_id: id, hourly: themeHourly(), generated_at: "2026-11-15T00:00:00Z" }));
  const list1 = await (await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {})).json();
  const p1 = list1.places.find((p) => p.id === id);
  assert.equal(p1.themeGroups.length, 1, "the legacy blob became one group");
  const gid = p1.themeGroups[0].id;

  // delete that only group
  const del = await worker.fetch(makeReq(`/custom_places/${id}/themes/${gid}`, { method: "DELETE", headers: hdr(t) }), env, {});
  assert.equal(del.status, 200);
  const delBody = await del.json();
  assert.equal(delBody.themes.used, 0, "the response reports zero groups left");

  // the next GET must NOT re-create a group from the stale blob
  const list2 = await (await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {})).json();
  const p2 = list2.places.find((p) => p.id === id);
  assert.equal(p2.themeGroups.length, 0, "no group resurrected after deleting the last one");
  assert.equal(p2.customConditions, null, "the legacy blob was cleared with the last group");
  assert.equal(p2.themes.used, 0);
  // the place-level verdict keeps the lenient baseline (○可拍) — the DATA
  // semantics are unchanged; the CLIENT renders a zero-theme place as its own
  // 「尚未設定題材」 card instead of a verdict row.
  assert.equal(p2.evaluation.tier, "shoot", "no subjects → the general baseline still answers");
  assert.equal(db._tables.custom_place_themes.length, 0, "no theme row was written back");

  // deleting a NON-last group must keep the blob untouched (nothing to clear)
  const mk = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "雲海窗", conditions: { cloud_low_max: 20 } }) }), env, {});
  assert.equal(mk.status, 200);
  const mk2 = await worker.fetch(makeReq(`/custom_places/${id}/themes`, { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "星空窗", conditions: { cloud_low_max: 10 } }) }), env, {});
  const g2 = (await mk2.json()).id;
  await worker.fetch(makeReq(`/custom_places/${id}/themes/${g2}`, { method: "DELETE", headers: hdr(t) }), env, {});
  const list3 = await (await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {})).json();
  assert.equal(list3.places.find((p) => p.id === id).themeGroups.length, 1, "the remaining group survives");
});

test("patch-8: legacy single set migrates to ONE group (lazy backfill); aggregate = voted reason when nothing rec/shoots", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "m8l", "paid");
  const t = await mint(env, "m8l");
  const c = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "私點", lat: 24.8, lng: 121.7, customConditions: { cloud_low_max: 20, months: [11] } }) }), env, {});
  assert.equal(c.status, 200);
  const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb = await list.json();
  const place = lb.places[0];
  // migration: the single blob became ONE named group with the same conditions
  assert.equal(place.themeGroups.length, 1);
  assert.equal(place.themeGroups[0].name, "題材 1");
  assert.deepEqual(place.themeGroups[0].conditions, { cloud_low_max: 20, months: [11] });
  assert.equal(db._tables.custom_place_themes.length, 1, "the lazy backfill wrote the row (idempotent)");
  assert.ok(place.customConditions && typeof place.customConditions === "object", "legacy blob still readable");
  // idempotent: a second GET does NOT duplicate the group
  const list2 = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  assert.equal((await list2.json()).places[0].themeGroups.length, 1);

  // aggregate: nothing rec/shoots → voted dominant reason (no single-group bias)
  const now = NOW;
  const rec = { hourly: themeHourly() };
  const ev = evaluateThemeGroups([
    { id: "a", name: "A", conditions: { cloud_low_max: 5 } },
    { id: "b", name: "B", conditions: { cloud_low_max: 5 } },
    { id: "c", name: "C", conditions: { visibility_min_km: 25 } },
  ], rec, now);
  assert.equal(ev[0].evaluation.tier, "no");
  assert.equal(ev[0].evaluation.reason, "低雲");
  const agg = aggregateEvaluation([...ev.map((g) => g.evaluation), evaluateCustomPlace(null, rec, now)]);
  assert.equal(agg.tier, "shoot", "the lenient baseline still passes themeHourly — the place verdict is ○可拍 even when the tuned groups fail");
  // pure vote (no baseline row): 2×低雲 outvote 1×霧
  const aggVote = aggregateEvaluation(ev.map((g) => g.evaluation));
  assert.equal(aggVote.tier, "no");
  assert.equal(aggVote.reason, "低雲", "2×低雲 outvote 1×霧");
  // rec windows: the EARLIEST qualifying window wins
  const recs = [
    { tier: "rec", reason: null, window: "2026-11-16 07:00" },
    { tier: "rec", reason: null, window: "2026-11-16 05:00" },
  ];
  assert.equal(aggregateEvaluation(recs).window, "2026-11-16 05:00");
  // shoot when no rec but the baseline passes
  assert.equal(aggregateEvaluation([{ tier: "no", reason: "低雲" }, { tier: "shoot", reason: null, window: "2026-11-16 06:00" }]).tier, "shoot");
  // validator shape
  assert.equal(validateThemeInput(null).ok, false);
  assert.equal(validateThemeInput({ name: "  ", conditions: { cloud_low_max: 20 } }).ok, false);
  assert.deepEqual(validateThemeNameInput("名字", { fr: "drop me", "zh-TW": "保留" }).nameI18n, { "zh-TW": "保留" });
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
// CL-APP-09 patch-2: the LLM contract is OpenRouter chat/completions — the
// response rides choices[0].message.content (the old generativelanguage
// candidates shape is GONE: the provider mismatch was the live outage).
const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";
function llmResponse(obj, opts = {}) {
  return async (url, init) => {
    llmCalls.push({ url: String(url), init });
    if (opts.status) return { ok: false, status: opts.status, text: async () => opts.body || "upstream boom" };
    return { ok: true, json: async () => ({ choices: [{ message: { content: JSON.stringify(obj) } }] }) };
  };
}
let llmCalls = [];

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

test("conditions/parse: rides OpenRouter chat/completions with the Bearer key + KV/env/default model; upstream failure carries a CONCRETE detail (fail-closed, never silent)", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u11", "paid");
  const t = await mint(env, "u11");
  env.LLM_API_KEY = "TEST-KEY";
  llmCalls = [];
  const restore = await stubFetch(llmResponse(GOOD_SUGGESTION));
  try {
    const res = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "x" }) }), env, {});
    assert.equal(res.status, 200);
    assert.equal(llmCalls.length, 1);
    assert.equal(llmCalls[0].url, OPENROUTER_URL, "the provider contract is OpenRouter (the generativelanguage mismatch was the live outage)");
    const sent = JSON.parse(llmCalls[0].init.body);
    assert.equal(sent.model, "google/gemini-2.5-flash", "default model when KV/env hold nothing");
    assert.equal(llmCalls[0].init.headers.Authorization, "Bearer TEST-KEY");
    assert.ok(sent.messages.some((m) => m.role === "system" && /before_sunrise/.test(m.content)), "the prompt teaches the anchor window schema");
  } finally { restore(); }
  // KV model swap (zero-code ruling): KV wins over the default
  env.EVALS._store.set("v1:cparse:model", "google/gemini-3-flash");
  llmCalls = [];
  const restore2 = await stubFetch(llmResponse(GOOD_SUGGESTION));
  try {
    await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "x" }) }), env, {});
    assert.equal(JSON.parse(llmCalls[0].init.body).model, "google/gemini-3-flash");
  } finally { restore2(); env.EVALS._store.delete("v1:cparse:model"); }
  // upstream auth failure: 502 with a CONCRETE detail (status + snippet), key never included
  llmCalls = [];
  const restore3 = await stubFetch(llmResponse(GOOD_SUGGESTION, { status: 401, body: '{"error":"Invalid API key"}' }));
  try {
    const res = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "x" }) }), env, {});
    assert.equal(res.status, 502);
    const b = await res.json();
    assert.match(b.detail, /LLM HTTP 401/);
    assert.match(b.detail, /Invalid API key/, "the upstream snippet makes diagnosis possible without wrangler tail");
    assert.ok(!/TEST-KEY/.test(JSON.stringify(b)), "the credential never leaks into the response");
  } finally { restore3(); }
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
  // patch-2: the windows ARRAY form (anchor + multi-segment) validates through
  // the SAME segment contract the condition schema enforces
  const WINDOWS_OK = { cloud: "any", fog: "any", rain: "no", windows: [
    { type: "before_sunrise", offset_minutes: -30 },
    { type: "fixed", start: "17:00", end: "18:40" },
  ], confidence: 0.7 };
  const wv = validateParseSuggestions(WINDOWS_OK);
  assert.equal(wv.ok, true);
  assert.deepEqual(wv.suggestions.windows, WINDOWS_OK.windows);
  assert.equal(validateParseSuggestions({ ...WINDOWS_OK, windows: [...WINDOWS_OK.windows, { type: "after_sunset" }] }).ok, false, ">2 segments violate");
  assert.equal(validateParseSuggestions({ ...WINDOWS_OK, windows: [{ type: "before_sunrise", end: "06:00" }] }).ok, false, "anchor + forbidden bound violates");
  assert.equal(validateParseSuggestions({ ...WINDOWS_OK, window_start: "05:00", window_end: "06:00" }).ok, false, "windows + flat fields together violate");
  assert.equal(validateParseSuggestions({ ...WINDOWS_OK, conflict: "請擇一" }).ok, false, "conflict excludes concrete windows");
  // patch-5 ③: conflict — non-overlapping windows come back as conflict text
  // with NO concrete window; conflict + window together is a schema violation.
  const CONFLICT = { ...GOOD_SUGGESTION, window_start: null, window_end: null, conflict: "兩個時間窗不重疊，請擇一" };
  const c = validateParseSuggestions(CONFLICT);
  assert.equal(c.ok, true);
  assert.equal(c.suggestions.conflict, "兩個時間窗不重疊，請擇一");
  assert.equal(c.suggestions.window_start, undefined);
  assert.equal(validateParseSuggestions({ ...CONFLICT, window_start: "04:30", window_end: "07:00" }).ok, false, "conflict excludes a concrete window");
  assert.equal(validateParseSuggestions({ ...GOOD_SUGGESTION, conflict: "x".repeat(201) }).ok, false);
  assert.equal(validateParseSuggestions({ ...GOOD_SUGGESTION, conflict: "   " }).ok, false);
  assert.equal(validateParseSuggestions({ ...GOOD_SUGGESTION, conflict: 5 }).ok, false);
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

// CL-APP-09 patch-5: AI-parse SEMANTIC GUARD (owner field-tested 「金色雲海」:
// the old prompt let the model answer 低雲≤20% + 日出前/日落後 whole-period two
// windows — the cloud direction was INVERTED (a cloud sea needs the low deck
// THICK) and the windows were far too wide). The guard lives in the prompt;
// these three mock-LLM cases assert the shapes the guarded prompt must
// produce, and that the handler propagates them honestly.
const CLOUD_SEA_ADVICE_ZH = "自訂條件引擎無法表達雲海（雲海需低雲層厚且低於拍攝點），請改掛官方『雲海』題材";
test("conditions/parse patch-5: semantic guard — 金色雲海/雲海 → honest official-genre advice (NO inverted cloud), 霞光 → ONE ±30min sun-anchored span", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "u12", "paid");
  const t = await mint(env, "u12");
  env.LLM_API_KEY = "TEST-KEY";
  // the prompt itself must TEACH the guard (the enforcement layer for a live LLM)
  {
    llmCalls = [];
    const restore = await stubFetch(llmResponse(GOOD_SUGGESTION));
    try {
      await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "x" }) }), env, {});
      const prompt = JSON.parse(llmCalls[0].init.body).messages.find((m) => m.role === "system").content;
      assert.match(prompt, /CLOUD-SEA GUARD/, "the prompt carries the cloud-sea guard");
      assert.match(prompt, /雲海/, "the guard names the cloud-sea phrase class");
      assert.match(prompt, /GOLDEN-LIGHT RULE/, "the prompt carries the golden-light rule");
      assert.match(prompt, /span_minutes/, "the prompt teaches the short-window span");
    } finally { restore(); }
  }
  // ① 金色雲海: cloud stays 'any' (never 低雲≤20%), NO windows, honest advice in conflict
  {
    llmCalls = [];
    const restore = await stubFetch(llmResponse({ cloud: "any", fog: "any", rain: "no", wind_max_ms: null, windows: [], lead_minutes: null, conflict: CLOUD_SEA_ADVICE_ZH, confidence: 0.6 }));
    try {
      const res = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "金色雲海" }) }), env, {});
      assert.equal(res.status, 200);
      const s = (await res.json()).suggestions;
      assert.equal(s.cloud, "any", "the cloud direction is NEVER inverted into a maximum");
      assert.notEqual(s.cloud, "min");
      assert.equal(s.windows, undefined, "no windows ride along with the advice");
      assert.match(s.conflict, /雲海/, "the honest advice names the official genre");
      assert.match(s.conflict, /官方/);
    } finally { restore(); }
  }
  // ② 霞光: ONE sun-anchored segment, ±30 min of the anchor — never two spans
  {
    llmCalls = [];
    const GOLDEN = { cloud: "half", fog: "thin", rain: "no", windows: [{ type: "before_sunset", offset_minutes: 30, span_minutes: 60 }], confidence: 0.8 };
    const restore = await stubFetch(llmResponse(GOLDEN));
    try {
      const res = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "今天傍晚想要霞光" }) }), env, {});
      assert.equal(res.status, 200);
      const s = (await res.json()).suggestions;
      assert.equal(s.windows.length, 1, "exactly ONE segment (the two-span disease is dead)");
      assert.equal(s.windows[0].type, "before_sunset");
      assert.equal(Math.abs(s.windows[0].offset_minutes), 30, "the anchor bound sits ±30 min of the sun event");
      assert.equal(s.windows[0].span_minutes, 60, "a short ±30 window around the anchor, never a full day");
    } finally { restore(); }
  }
  // ③ 雲海: same honest advice channel, tri-lingually (owner language zh-TW here)
  {
    llmCalls = [];
    const restore = await stubFetch(llmResponse({ cloud: "any", fog: "any", rain: "any", windows: [], conflict: CLOUD_SEA_ADVICE_ZH, confidence: 0.55 }));
    try {
      const res = await worker.fetch(makeReq("/conditions/parse", { method: "POST", headers: hdr(t), body: JSON.stringify({ text: "清晨雲海" }) }), env, {});
      assert.equal(res.status, 200);
      const s = (await res.json()).suggestions;
      assert.match(s.conflict, /請改掛官方/, "honest advice, never a hard-forced condition set");
      assert.equal(s.cloud, "any");
    } finally { restore(); }
  }
  // the span contract itself: valid ±30 golden shape passes; malformed spans fail-closed
  const ok = validateParseSuggestions({ cloud: "any", fog: "any", rain: "any", windows: [{ type: "after_sunrise", offset_minutes: -30, span_minutes: 60 }], confidence: 0.7 });
  assert.equal(ok.ok, true, "morning golden shape validates");
  assert.equal(validateParseSuggestions({ cloud: "any", fog: "any", rain: "any", windows: [{ type: "before_sunset", offset_minutes: 30, span_minutes: 60, start: "16:00" }], confidence: 0.7 }).ok, false, "span + fixed narrowing start violate");
  assert.equal(validateParseSuggestions({ cloud: "any", fog: "any", rain: "any", windows: [{ type: "after_sunrise", offset_minutes: -30, span_minutes: 7200 }], confidence: 0.7 }).ok, false, "span beyond 720 violates");
  assert.equal(validateParseSuggestions({ cloud: "any", fog: "any", rain: "any", windows: [{ type: "fixed", start: "04:00", end: "06:00", span_minutes: 60 }], confidence: 0.7 }).ok, false, "span on a fixed segment violates");
});

// ===========================================================================
// CL-APP-08: private-place grid dedup (owner-approved conservative version).
// Share ONE Open-Meteo grid fetch when: distance <1 km AND DEM elev diff
// <30 m AND 500 m-ring relief ≤100 m AND no ridge/gully crossing. A group
// counts as ONE quota point; judgment inputs stay per-place; escape hatch =
// manual 「獨立重新抓取」 (detach + solo refetch = 1 quota); background
// migration re-groups existing places with NO fetch and NO charge.
// ===========================================================================

// Synthetic DEMs (injectable via the fetch seam — no real network in tests).
// Flat pocket: everything at 80 m.
const flatElev = async (points) => points.map(() => 80);
// Knife ridge: a wall at lat 24.802 within ±100 m of lng 121.700 only — the
// 500 m ring stays flat (its off-corridor points miss the wall), but the
// segment midpoint lands ON the wall. Represents a ridge line between the
// two points that a shared grid fetch would paper over.
const ridgeElev = async (points) => points.map(([lat, lng]) =>
  (Math.abs(lat - 24.802) < 0.0003 && Math.abs(lng - 121.7) < 0.001 ? 200 : 80));
// The same wall as a GULLY (dips instead of rises) — 谷口 also forbids sharing.
// Centered on the 谷口 test pair (24.81/24.814 × 121.71).
const gullyElev = async (points) => points.map(([lat, lng]) =>
  (Math.abs(lat - 24.812) < 0.0003 && Math.abs(lng - 121.71) < 0.001 ? 0 : 80));

test("CL-APP-08 pure terrain: same-group pocket passes; ridge/gully/relief/elev-diff all fail-closed", () => {
  assert.ok(haversineM(24.8, 121.7, 24.804, 121.7) < SHARE_MAX_DIST_M, "pair distance < 1 km");
  // flat pocket: ring ~80 m everywhere (both endpoints included), segment flat, elev diff 10
  const flat = analyzeTerrain({ elevA: 80, elevB: 90, ring: [80, 80, 81, 80, 80, 79, 80, 80, 80, 90], segment: [85, 85, 85] });
  assert.equal(flat.relief500, 11);
  assert.ok(flat.relief500 <= SHARE_MAX_RELIEF_M);
  assert.ok(flat.elevDiff < SHARE_MAX_ELEV_DIFF_M);
  assert.equal(flat.crossRidge, false);
  assert.equal(flat.canShare, true);
  // 跨稜線: an intermediate sample rises ≥ RIDGE_DETECT_M above BOTH endpoints
  const ridge = analyzeTerrain({ elevA: 80, elevB: 82, ring: [80, 80, 81, 80, 82, 80, 80, 80, 80, 82], segment: [82, 200, 82] });
  assert.equal(ridge.crossRidge, true);
  assert.equal(ridge.canShare, false);
  // 谷口: an intermediate sample dips ≥ RIDGE_DETECT_M below BOTH endpoints
  const gully = analyzeTerrain({ elevA: 80, elevB: 82, ring: [80, 80, 81, 80, 82, 80, 80, 80, 80, 82], segment: [82, 0, 82] });
  assert.equal(gully.crossRidge, true);
  assert.equal(gully.canShare, false);
  // relief over the 100 m cap kills the share even without a ridge
  const rough = analyzeTerrain({ elevA: 80, elevB: 80, ring: [80, 80, 200, 80, 80, 80, 80, 80, 80, 80], segment: [80, 80, 80] });
  assert.ok(rough.relief500 > SHARE_MAX_RELIEF_M);
  assert.equal(rough.canShare, false);
  // 海拔差 31 m: over the 30 m gate even on a flat pocket
  const diff31 = analyzeTerrain({ elevA: 80, elevB: 111, ring: [80, 80, 81, 80, 81, 80, 80, 80, 80, 111], segment: [95, 95, 95] });
  assert.ok(diff31.elevDiff >= SHARE_MAX_ELEV_DIFF_M);
  assert.equal(diff31.canShare, false);
  // degenerate input (no DEM numbers) → null, never a silent share
  assert.equal(analyzeTerrain({}), null);
});

async function demFetchStub(dem) {
  // route DEM (elevation API) calls to the synthetic surface; forecast calls
  // to a generic Open-Meteo payload (only used when a fetch actually runs).
  const day = new Date(NOW + DAY).toISOString().slice(0, 10);
  const omPayload = {
    elevation: 80, timezone: "Asia/Taipei",
    hourly: { time: [`${day}T05:00`], cloud_cover_low: [10], cloud_cover_mid: [10], cloud_cover_high: [10],
      precipitation: [0], visibility: [20], wind_speed_10m: [2] },
  };
  const real = globalThis.fetch;
  let omCalls = 0;
  globalThis.fetch = async (url) => {
    if (/elevation/.test(String(url))) {
      const u = new URL(url);
      const lats = u.searchParams.get("latitude").split(",").map(Number);
      const lngs = u.searchParams.get("longitude").split(",").map(Number);
      return { ok: true, json: async () => ({ elevation: await dem(lats.map((la, i) => [la, lngs[i]])) }) };
    }
    omCalls += 1;
    return { ok: true, json: async () => omPayload };
  };
  return () => { globalThis.fetch = real; return omCalls; };
}

test("CL-APP-08 same-group: new point <1 km joins the member's group — ONE fetch, ONE quota point, own DEM inputs", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "g8", "paid");
  const t = await mint(env, "g8");
  const restore = await demFetchStub(flatElev);
  let aId, bId;
  try {
    const ra = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "A 點", lat: 24.8, lng: 121.7, elevation: 80 }) }), env, {});
    aId = (await ra.json()).id;
    assert.ok(db._tables.custom_fetch_queue.has(aId), "first ungrouped point queues a fetch");
    const rb = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "B 點", lat: 24.804, lng: 121.7, elevation: 80 }) }), env, {});
    const rbBody = await rb.json();
    bId = rbBody.id;
    assert.ok(rbBody.grouping, "flat pocket <1 km → grouped");
    assert.equal(rbBody.grouping.representativeId, aId, "earliest place is the representative");
    assert.equal(db._tables.custom_fetch_queue.has(bId), false, "grouped point reuses the rep's data — NO new fetch");
    assert.equal(db._tables.custom_places.find((x) => x.id === bId).group_id, `g:${aId}`);
  } finally { restore(); }

  // quota counting: 2 places, 1 group → quota.used = 1 (同組只算 1 點)
  const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb = await list.json();
  assert.equal(lb.places.length, 2);
  assert.equal(lb.quota.used, 1, "a group counts as ONE quota point");
  const bPlace = lb.places.find((p) => p.id === bId);
  assert.ok(bPlace.sharing);
  assert.match(bPlace.sharing.sharedWith[0].name, /A 點/);
  assert.equal(bPlace.sharing.isRepresentative, false);
  const aPlace = lb.places.find((p) => p.id === aId);
  assert.equal(aPlace.sharing.isRepresentative, true);

  // the representative's single fetch fans out to the whole group; the
  // judgment side keeps B's OWN lat/lng/elevation (rule 4)
  let omCalls = 0;
  const restore2 = await demFetchStub(async () => { omCalls += 1; return 80; });
  try {
    const s = await processCustomFetchQueue(env, NOW, { batch: 10 });
    assert.equal(s.processed, 1, "only the representative fetches");
    assert.equal(s.fanned_out, 1, "one fan-out member");
    assert.equal(omCalls, 0, "no DEM calls during queue processing");
  } finally { restore2(); }
  const recB = JSON.parse(env.EVALS._store.get(`v1:evals:custom:${bId}`));
  const recA = JSON.parse(env.EVALS._store.get(`v1:evals:custom:${aId}`));
  assert.deepEqual(recB.hourly, recA.hourly, "shared raw grid verbatim");
  assert.deepEqual([recB.lat, recB.lng, recB.elevation], [24.804, 121.7, 80], "B keeps its OWN DEM lat/lng/elevation");
  assert.equal(recB.shared_from, aId);
  assert.equal(await userFetchCount(env, "g8", NOW), 1, "ONE user-budget unit for the whole group");
  assert.equal((await globalUsageState(env)).count, 1, "ONE global-usage unit for the whole group");
});

test("CL-APP-08 cross-ridge + 谷口 + 海拔差31m: each pair stays independent — own fetch, own quota", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "g8x", "paid");
  const t = await mint(env, "g8x");
  const restore = await demFetchStub(ridgeElev);
  let c1, c2;
  try {
    const r1 = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "稜線北", lat: 24.8, lng: 121.7, elevation: 80 }) }), env, {});
    c1 = (await r1.json()).id;
    const r2 = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "稜線南", lat: 24.804, lng: 121.7, elevation: 80 }) }), env, {});
    c2 = (await r2.json()).id;
  } finally { restore(); }
  assert.equal(db._tables.custom_places.find((x) => x.id === c2).group_id, null, "跨稜線強制不共用");
  assert.ok(db._tables.custom_fetch_queue.has(c2), "independent point queues its own fetch");

  // 谷口 variant
  const restore3 = await demFetchStub(gullyElev);
  let v2;
  try {
    const r1 = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "谷口上", lat: 24.81, lng: 121.71, elevation: 80 }) }), env, {});
    const r2 = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "谷口下", lat: 24.814, lng: 121.71, elevation: 80 }) }), env, {});
    v2 = (await r2.json()).id;
  } finally { restore3(); }
  assert.equal(db._tables.custom_places.find((x) => x.id === v2).group_id, null, "谷口強制不共用");

  // 海拔差 31 m on a flat pocket — over the 30 m gate
  const restore4 = await demFetchStub(flatElev);
  let e2;
  try {
    await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "低點", lat: 24.82, lng: 121.72, elevation: 80 }) }), env, {});
    const r2 = await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "高點", lat: 24.824, lng: 121.72, elevation: 111 }) }), env, {});
    e2 = (await r2.json()).id;
  } finally { restore4(); }
  assert.equal(db._tables.custom_places.find((x) => x.id === e2).group_id, null, "海拔差 31 m ≥ 30 m → 不共用");

  // quota: six independent points (three rejected pairs) = six quota points
  const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  assert.equal((await list.json()).quota.used, 6, "no group → each point counts 1");
});

test("CL-APP-08 escape hatch: 獨立重新抓取 detaches the point and refetches solo for 1 quota", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "g8e", "paid");
  const t = await mint(env, "g8e");
  const restore = await demFetchStub(flatElev);
  let aId, bId;
  try {
    aId = (await (await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "主點", lat: 24.8, lng: 121.7, elevation: 80 }) }), env, {})).json()).id;
    bId = (await (await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "副點", lat: 24.804, lng: 121.7, elevation: 80 }) }), env, {})).json()).id;
    assert.ok(db._tables.custom_places.find((x) => x.id === bId).group_id, "grouped before the escape hatch");
    const rf = await worker.fetch(makeReq(`/custom_places/${bId}/refetch`, { method: "POST", headers: hdr(t) }), env, {});
    assert.equal(rf.status, 200);
    const rb = await rf.json();
    assert.equal(rb.detached, true);
    assert.equal(rb.shareMode, "independent");
    assert.match(rb.message["zh-TW"], /計 1 點配額/);
    const brow = db._tables.custom_places.find((x) => x.id === bId);
    assert.equal(brow.group_id, null, "detached from the group");
    assert.equal(brow.share_mode, "independent", "never auto-rejoins");
    const q = db._tables.custom_fetch_queue.get(bId);
    assert.equal(q.reason, "refresh");
    assert.equal(q.priority, 10, "explicit member action rides ahead of bulk adds");
    assert.ok(db._tables.custom_fetch_queue.get(aId).status === "pending", "rep keeps its own queued fetch");
  } finally { restore(); }

  // both points fetch SOLO now — 2 forecast fetches, 2 quota units
  const restore2 = await demFetchStub(flatElev);
  let summary;
  try {
    summary = await processCustomFetchQueue(env, NOW, { batch: 10 });
  } finally {
    const forecastCalls = restore2(); // demFetchStub returns the forecast-call count
    assert.equal(forecastCalls, 2, "two solo forecast fetches");
  }
  assert.equal(summary.processed, 2, "detached point fetches on its own");
  assert.equal(await userFetchCount(env, "g8e", NOW), 2, "escape hatch costs 1 quota (2 total for 2 solo points)");
  const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb = await list.json();
  assert.equal(lb.quota.used, 2, "no group → 2 quota points");
  assert.equal(lb.places.find((p) => p.id === bId).sharing, null, "independent point carries no shared tag");

  // anonymous / cross-user refetch is not a thing
  const anon = await worker.fetch(makeReq(`/custom_places/${bId}/refetch`, { method: "POST" }), env, {});
  assert.equal(anon.status, 401);
});

test("CL-APP-08 rep deletion promotes the next-oldest member; the group keeps serving", async () => {
  const { env, db } = makeEnv();
  seedUser(db, "g8p", "paid");
  const t = await mint(env, "g8p");
  const restore = await demFetchStub(flatElev);
  let aId, bId;
  try {
    aId = (await (await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "先建", lat: 24.8, lng: 121.7, elevation: 80 }) }), env, {})).json()).id;
    bId = (await (await worker.fetch(makeReq("/custom_places", { method: "POST", headers: hdr(t), body: JSON.stringify({ name: "後建", lat: 24.804, lng: 121.7, elevation: 80 }) }), env, {})).json()).id;
  } finally { restore(); }
  await worker.fetch(makeReq(`/custom_places/${aId}`, { method: "DELETE", headers: hdr(t) }), env, {});
  const rec = JSON.parse(env.EVALS._store.get(`v1:cp:group:g:${aId}`));
  assert.equal(rec.representativeId, bId, "earliest remaining active member promoted");
  const list = await worker.fetch(makeReq("/custom_places", { headers: hdr(t) }), env, {});
  const lb = await list.json();
  const bPlace = lb.places.find((p) => p.id === bId);
  assert.equal(bPlace.sharing.representativeId, bId);
  assert.equal(bPlace.sharing.sharedWith.length, 0, "no other member left to tag");
  assert.equal(lb.quota.used, 1, "the surviving group still counts 1");
});

test("CL-APP-08 migration: existing places re-group in the background — no fetch, no quota charge, once-only", async () => {
  const { env, db } = makeEnv();
  const day = dbStamp(NOW - 5 * DAY);
  // u-m: A(rep candidate, older) + B flat pocket <1 km, same elevation.
  // u-o: another member with the SAME coords — privacy: never cross-user.
  // u-i: an escape-hatch (independent) member — excluded from the sweep.
  db._tables.custom_places.push(
    { id: "mA", user_id: "u-m", name: "A", lat: 24.8, lng: 121.7, elevation: 80, timezone: null, custom_conditions: null, status: "active", group_id: null, share_mode: "auto", created_at: day, updated_at: day, deleted_at: null },
    { id: "mB", user_id: "u-m", name: "B", lat: 24.804, lng: 121.7, elevation: 80, timezone: null, custom_conditions: null, status: "active", group_id: null, share_mode: "auto", created_at: dbStamp(NOW - 4 * DAY), updated_at: day, deleted_at: null },
    { id: "mO", user_id: "u-o", name: "O", lat: 24.8, lng: 121.7, elevation: 80, timezone: null, custom_conditions: null, status: "active", group_id: null, share_mode: "auto", created_at: day, updated_at: day, deleted_at: null },
    { id: "mI", user_id: "u-i", name: "I", lat: 24.9, lng: 121.9, elevation: 80, timezone: null, custom_conditions: null, status: "active", group_id: null, share_mode: "independent", created_at: day, updated_at: day, deleted_at: null },
  );
  let demCalls = 0;
  const s = await regroupExistingPlaces(env, {
    fetchElev: async (pts) => { demCalls += 1; return flatElev(pts); },
  });
  assert.equal(s.grouped, 1, "one flat pocket grouped");
  assert.ok(demCalls >= 1, "DEM check ran (not a coords-only grouping)");
  const aRow = db._tables.custom_places.find((x) => x.id === "mA");
  const bRow = db._tables.custom_places.find((x) => x.id === "mB");
  const oRow = db._tables.custom_places.find((x) => x.id === "mO");
  const iRow = db._tables.custom_places.find((x) => x.id === "mI");
  assert.equal(aRow.group_id, `g:mA`, "earliest place carries the group key");
  assert.equal(bRow.group_id, `g:mA`);
  assert.equal(oRow.group_id, null, "跨會員不共用 (per-user privacy)");
  assert.equal(iRow.group_id, null, "escape-hatch point never regroups");
  const rec = JSON.parse(env.EVALS._store.get("v1:cp:group:g:mA"));
  assert.equal(rec.representativeId, "mA");
  assert.equal(db._tables.custom_fetch_queue.size, 0, "migration queues NO fetch");
  assert.equal(await userFetchCount(env, "u-m"), 0, "migration charges NO quota");
  assert.equal((await globalUsageState(env)).count, 0, "migration charges NO global usage");
  assert.ok(env.EVALS._store.get("v1:cp:regroup:done"), "once-only guard written");

  const again = await regroupExistingPlaces(env, { fetchElev: flatElev });
  assert.equal(again.skipped, true, "second run is a no-op (rule 5: re-group ONCE)");
});

