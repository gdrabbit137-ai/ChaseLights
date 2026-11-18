// CL-APP-09 追加2 steer tests (kept in a SELF-CONTAINED file with its own mock
// D1 so in-flight sibling tickets cannot collide — custom-places.test.js
// precedent). Covers the owner's 追加2 rulings:
//   ① 20-set system-wide TOTAL cap REMOVED — only per-point caps remain
//     (paid 5/place, free trial 1 PER PLACE, owner unlimited). A free member
//     may hold 1 set on EVERY place (the old total-cap regression test).
//   ③ batch endpoint payload PAGINATION — ≤20 places + ≤100 sets per
//     response with next_cursor (and the ids ceiling 400).
//   ④ KV verdict-cache writes metered PER USER per UTC day — over-budget
//     requests still answer normally (transparent), only the write is skipped.
//   + shared hash cache: identical condition sets across users hit one KV
//     entry; a new forecast generation produces fresh keys.
import test from "node:test";
import assert from "node:assert/strict";
import {
  CAP_PLACE, CAP_TOTAL_FREE, DAILY_ADD_LIMIT, capPlaceFor, capTotalFor, capsPayload,
  handleSubjectSetCreate, handleSubjectSetsEval, handleSubjectSetsEvalBatch,
  evaluateSet, verdictCacheKey, DEFAULT_MAX_BATCH_PLACES, DEFAULT_MAX_BATCH_SETS,
  DEFAULT_MAX_KV_WRITES_USER_DAY, MAX_IDS_PER_BATCH_REQUEST,
} from "../src/subject-sets.js";
import { signJWT } from "../src/auth.js";

const SEC = "test-secret";

// ------------------------------------------------------------------ mock D1
function makeMockD1() {
  const t = { users: new Map(), sets: [], budget: new Map() };
  const db = {
    _tables: t,
    prepare(sql) {
      const runner = (args) => ({
        run: async () => runSql(t, sql, args),
        first: async () => runFirst(t, sql, args),
        all: async () => runAll(t, sql, args),
      });
      return { ...runner([]), bind: (...a) => runner(a) };
    },
  };
  return db;
}

function runSql(t, sql, args) {
  if (/INSERT INTO custom_subject_sets/.test(sql)) {
    const [id, uid, placeId, name, templateId, baseRev, baseCc, cc, months, now] = args;
    t.sets.push({ id, user_id: uid, place_id: placeId, name, template_id: templateId, base_rev: baseRev, base_conditions: baseCc, conditions: cc, months, created_at: now, updated_at: now });
    return { meta: { changes: 1 } };
  }
  if (/DELETE FROM custom_subject_sets/.test(sql)) {
    const before = t.sets.length;
    t.sets = t.sets.filter((r) => r.id !== args[0]);
    return { meta: { changes: before - t.sets.length } };
  }
  if (/UPDATE custom_subject_sets SET/.test(sql)) {
    const setClause = sql.split(/SET /i)[1].split(/ WHERE /i)[0];
    const upd = {};
    for (const m of setClause.matchAll(/(\w+) = \?(\d+)/g)) upd[m[1]] = args[Number(m[2]) - 1];
    const row = t.sets.find((r) => r.id === args[0]);
    if (!row) return { meta: { changes: 0 } };
    Object.assign(row, upd);
    return { meta: { changes: 1 } };
  }
  return { meta: { changes: 0 } };
}

function runFirst(t, sql, args) {
  if (/SELECT level FROM users/.test(sql)) return Promise.resolve(t.users.get(args[0]) || null);
  if (/COUNT\(\*\) AS n FROM custom_subject_sets WHERE user_id = \?1 AND created_at >=/.test(sql)) {
    return Promise.resolve({ n: t.sets.filter((r) => r.user_id === args[0] && r.created_at >= args[1]).length });
  }
  if (/COUNT\(\*\) AS n FROM custom_subject_sets WHERE user_id = \?1 AND place_id/.test(sql)) {
    return Promise.resolve({ n: t.sets.filter((r) => r.user_id === args[0] && r.place_id === args[1]).length });
  }
  if (/COUNT\(\*\) AS n FROM custom_subject_sets WHERE user_id = \?1/.test(sql)) {
    return Promise.resolve({ n: t.sets.filter((r) => r.user_id === args[0]).length });
  }
  // ss_kv_budget atomic upsert (追加2 ④): charge n writes; no row = over budget
  if (/INSERT INTO ss_kv_budget/.test(sql)) {
    const [uid, day, n, cap] = args;
    const k = `${uid}|${day}`;
    const cur = t.budget.get(k) || 0;
    if (cur + n > cap) return Promise.resolve(null);
    t.budget.set(k, cur + n);
    return Promise.resolve({ writes: cur + n });
  }
  if (/SELECT id, user_id, place_id, name, template_id/.test(sql) && /WHERE id = \?1$/.test(sql.trim())) {
    return Promise.resolve(t.sets.find((r) => r.id === args[0]) || null);
  }
  if (/SELECT id FROM custom_subject_sets WHERE id = \?1 AND user_id = \?2/.test(sql)) {
    return Promise.resolve(t.sets.find((r) => r.id === args[0] && r.user_id === args[1]) || null);
  }
  if (/SELECT id, user_id, place_id, name, template_id/.test(sql) && /WHERE user_id = \?1 AND place_id = \?2 ORDER BY/.test(sql)) {
    const rows = t.sets.filter((r) => r.user_id === args[0] && r.place_id === args[1])
      .sort((a, b) => b.created_at.localeCompare(a.created_at));
    return Promise.resolve(rows[0] || null);
  }
  return Promise.resolve(null);
}

function runAll(t, sql, args) {
  if (/WHERE user_id = \?1 AND place_id = \?2 ORDER BY created_at DESC/.test(sql)) {
    const rows = t.sets.filter((r) => r.user_id === args[0] && r.place_id === args[1])
      .sort((a, b) => b.created_at.localeCompare(a.created_at));
    return Promise.resolve({ results: rows });
  }
  if (/WHERE user_id = \?1 ORDER BY created_at DESC/.test(sql)) {
    const rows = t.sets.filter((r) => r.user_id === args[0])
      .sort((a, b) => b.created_at.localeCompare(a.created_at));
    return Promise.resolve({ results: rows });
  }
  return Promise.resolve({ results: [] });
}

function makeEnv(opts = {}) {
  const store = new Map(Object.entries(opts.kv || {}));
  const kv = {
    get: async (k, type) => {
      const v = store.has(k) ? store.get(k) : null;
      return v !== null && type === "json" ? JSON.parse(v) : v;
    },
    put: async (k, v) => { store.set(k, v); },
    _store: store,
  };
  const db = makeMockD1();
  return { env: { EVALS: kv, DB: db, AUTH_SECRET: SEC, ...opts.envVars }, db, kvStore: store };
}

let ipSeq = 0;
function makeReq(pathWithQuery, opts = {}) {
  const headers = new Headers(opts.headers || {});
  headers.set("CF-Connecting-IP", `10.9.${(ipSeq = (ipSeq + 1) % 256)}.${ipSeq}`);
  return new Request(`https://chaselights.app/api/v1${pathWithQuery}`, { ...opts, headers });
}
async function mint(env, sub) {
  const now = Math.floor(Date.now() / 1000);
  return signJWT({ sub, name: "T", level: "paid", typ: "access", exp: now + 600 }, env.AUTH_SECRET);
}
function seedUser(db, id, level) {
  db._tables.users.set(id, { device_id: id, level });
}
const hdr = (token) => ({ "Content-Type": "application/json", Authorization: `Bearer ${token}` });
function url(path) { return new URL(`https://chaselights.app/api/v1${path}`); }
function seedGrid(env, placeId, gen = "2026-11-18T00:30:00Z") {
  env.EVALS._store.set(`v1:evals:${placeId}`, JSON.stringify({
    generated_at: gen,
    hourly: [
      { local_date: "2026-11-20", hour: "06:00", values: { cloud_low: 10, cloud_mid: 30, cloud_high: 50, precipitation: 0, visibility: 20, wind: 3 } },
      { local_date: "2026-11-20", hour: "07:00", values: { cloud_low: 10, cloud_mid: 30, cloud_high: 50, precipitation: 0, visibility: 20, wind: 3 } },
      { local_date: "2026-11-21", hour: "06:00", values: { cloud_low: 10, cloud_mid: 30, cloud_high: 50, precipitation: 0, visibility: 20, wind: 3 } },
    ],
  }));
}
const CC_OK = { cloud_low_max: 20 };
async function createSet(env, token, body) {
  return handleSubjectSetCreate(makeReq("/subject_sets", { method: "POST", headers: hdr(token), body: JSON.stringify(body) }), env);
}
async function evalBatch(env, token, ids, cursor) {
  const q = `/subject_sets/eval_batch?ids=${ids.join(",")}${cursor != null ? `&cursor=${cursor}` : ""}`;
  return handleSubjectSetsEvalBatch(makeReq(q, { headers: hdr(token) }), env, url(q));
}

// ------------------------------------------------------------------ ① caps
test("caps: paid 5/place no total / free 5/place + 5 TOTAL + 5 daily adds / owner unlimited", () => {
  assert.equal(capPlaceFor("free", false), CAP_PLACE);
  assert.equal(capPlaceFor("free", true), CAP_PLACE);
  assert.equal(capPlaceFor("paid", false), CAP_PLACE);
  assert.equal(capPlaceFor("owner", false), Infinity);
  assert.equal(capTotalFor("free", false), CAP_TOTAL_FREE);
  assert.equal(capTotalFor("free", true), Infinity); // free-as-paid trial flag lifts the total
  assert.equal(capTotalFor("paid", false), Infinity);
  assert.equal(capTotalFor("owner", false), Infinity);
  assert.equal(CAP_PLACE, 5);
  assert.equal(CAP_TOTAL_FREE, 5);
  assert.equal(DAILY_ADD_LIMIT, 5);
  // caps payload is JSON-safe: Infinity → null (owner reads 「無上限」)
  assert.deepEqual(capsPayload("owner", false), { place: null, total: null });
  assert.deepEqual(capsPayload("paid", false), { place: 5, total: null });
  assert.deepEqual(capsPayload("free", false), { place: 5, total: 5 });
});

test("create: paid 5 per place — 6th (older rows seeded so the daily throttle is unused) 403 place_cap", async () => {
  const { env } = makeEnv();
  seedUser(env.DB, "u1", "paid");
  const token = await mint(env, "u1");
  // seed the 5 rows on PREVIOUS UTC days so the daily-add throttle stays at 0
  // and the PER-PLACE cap is what fires (the paid tier has no total cap)
  const old = new Date(Date.now() - 26 * 3600 * 1000).toISOString().replace("T", " ").slice(0, 19);
  for (let i = 0; i < 5; i++) {
    await env.DB.prepare(
      "INSERT INTO custom_subject_sets (id, user_id, place_id, name, template_id, base_rev, base_conditions, conditions, months, created_at, updated_at) VALUES (?1, ?2, ?3, ?4, NULL, NULL, '{}', '{}', '[]', ?5, ?5)"
    ).bind(`seed-${i}`, "u1", "tw-014", `s${i}`, old).run();
  }
  const six = await createSet(env, token, { place_id: "tw-014", name: "s6", conditions: CC_OK });
  assert.equal(six.status, 403);
  const b = await six.json();
  assert.equal(b.error, "per-place cap reached");
  assert.equal(b.message._t, "place_cap");
  assert.equal(b.counts.place, 5);
  assert.deepEqual(b.caps, { place: 5, total: null }); // paid has NO total cap
});

test("create: paid daily add throttle 5 — the 6th same-UTC-day creation is 403 daily_add (anti-churn, owner exempt)", async () => {
  const { env } = makeEnv();
  seedUser(env.DB, "u5", "paid");
  const token = await mint(env, "u5");
  for (let i = 0; i < 5; i++) {
    const r = await createSet(env, token, { place_id: `tw-02${i}`, name: `d${i}`, conditions: CC_OK });
    assert.equal(r.status, 200);
  }
  const sixth = await createSet(env, token, { place_id: "tw-030", name: "d6", conditions: CC_OK });
  assert.equal(sixth.status, 403);
  const b = await sixth.json();
  assert.equal(b.message._t, "daily_add");
});

test("create: free TOTAL cap 5 — a 6th set (older rows seeded, daily adds unused) 403 total_cap", async () => {
  const { env } = makeEnv();
  seedUser(env.DB, "u2", "free");
  const token = await mint(env, "u2");
  // 5 rows created on PREVIOUS UTC days — the daily throttle must NOT mask
  // the total cap (both are 5-shaped; the total is the tier limit)
  const old = new Date(Date.now() - 26 * 3600 * 1000).toISOString().replace("T", " ").slice(0, 19);
  for (let i = 0; i < 5; i++) {
    await env.DB.prepare(
      "INSERT INTO custom_subject_sets (id, user_id, place_id, name, template_id, base_rev, base_conditions, conditions, months, created_at, updated_at) VALUES (?1, ?2, ?3, ?4, NULL, NULL, '{}', '{}', '[]', ?5, ?5)"
    ).bind(`old-${i}`, "u2", `tw-01${i}`, `t${i}`, old).run();
  }
  const sixth = await createSet(env, token, { place_id: "jp-001", name: "t6", conditions: CC_OK });
  assert.equal(sixth.status, 403);
  const b = await sixth.json();
  assert.equal(b.message._t, "total_cap");
  assert.match(b.message["zh-TW"], /全站總量 5 組/);
  assert.equal(b.counts.total, 5);
  assert.deepEqual(b.caps, { place: 5, total: 5 });
});

test("create: free gets 5 PER PLACE (paid parity) — 5 same-place sets pass, 6th same-day honest 403", async () => {
  const { env } = makeEnv();
  seedUser(env.DB, "u4", "free");
  const token = await mint(env, "u4");
  for (let i = 0; i < 5; i++) {
    const r = await createSet(env, token, { place_id: "tw-014", name: `p${i}`, conditions: CC_OK });
    assert.equal(r.status, 200, `free set ${i} on ONE place must pass (5 per place)`);
  }
  const sixth = await createSet(env, token, { place_id: "tw-014", name: "p6", conditions: CC_OK });
  assert.equal(sixth.status, 403);
  const b = await sixth.json();
  // same UTC day as the five above → the daily throttle answers FIRST
  assert.equal(b.message._t, "daily_add");
});

test("create: free daily add throttle 5 — the 6th same-UTC-day creation is 403 daily_add", async () => {
  const { env } = makeEnv();
  seedUser(env.DB, "u3", "free");
  const token = await mint(env, "u3");
  for (let i = 0; i < 5; i++) {
    const r = await createSet(env, token, { place_id: `jp-00${i}`, name: `d${i}`, conditions: CC_OK });
    assert.equal(r.status, 200);
  }
  const sixth = await createSet(env, token, { place_id: "jp-010", name: "d6", conditions: CC_OK });
  assert.equal(sixth.status, 403);
  const b = await sixth.json();
  assert.equal(b.message._t, "daily_add");
  assert.match(b.message["zh-TW"], /每日上限 5 組/);
});

test("create: owner unlimited per place (no cap at all)", async () => {
  const { env } = makeEnv();
  seedUser(env.DB, "own", "owner");
  const token = await mint(env, "own");
  for (let i = 0; i < 7; i++) {
    const r = await createSet(env, token, { place_id: "tw-014", name: `o${i}`, conditions: CC_OK });
    assert.equal(r.status, 200);
  }
});

// ------------------------------------------------------------------ cache ④
test("verdict cache: identical condition sets across users share ONE KV entry; new forecast generation makes a fresh key", async () => {
  const { env, kvStore } = makeEnv();
  seedGrid(env, "tw-014");
  seedUser(env.DB, "ua", "paid");
  seedUser(env.DB, "ub", "paid");
  const ta = await mint(env, "ua");
  const tb = await mint(env, "ub");
  await createSet(env, ta, { place_id: "tw-014", name: "A", conditions: CC_OK });
  await createSet(env, tb, { place_id: "tw-014", name: "B", conditions: CC_OK });
  const ra = await handleSubjectSetsEval(makeReq("/subject_sets/eval?place_id=tw-014", { headers: hdr(ta) }), env, url("/subject_sets/eval?place_id=tw-014"));
  assert.equal(ra.status, 200);
  const ja = await ra.json();
  assert.equal(ja.sets[0].tier, "rec");
  assert.deepEqual(ja.sets[0].window.hours, ["06:00", "07:00"]);
  const rb = await handleSubjectSetsEval(makeReq("/subject_sets/eval?place_id=tw-014", { headers: hdr(tb) }), env, url("/subject_sets/eval?place_id=tw-014"));
  const jb = await rb.json();
  assert.deepEqual(jb.sets[0].tier, "rec");
  // one shared cache entry (not two)
  const ssc = [...kvStore.keys()].filter((k) => k.startsWith("v1:ssc:tw-014:"));
  assert.equal(ssc.length, 1);
  // a new forecast generation invalidates by KEY, never serves stale
  seedGrid(env, "tw-014", "2026-11-18T12:00:00Z");
  await handleSubjectSetsEval(makeReq("/subject_sets/eval?place_id=tw-014", { headers: hdr(ta) }), env, url("/subject_sets/eval?place_id=tw-014"));
  const ssc2 = [...kvStore.keys()].filter((k) => k.startsWith("v1:ssc:tw-014:"));
  assert.equal(ssc2.length, 2);
});

test("evaluateSet: no grid = pending; no matching hour = tier no with honest reason", () => {
  const row = { id: "s1", name: "n", conditions: JSON.stringify(CC_OK), months: "[]" };
  const p = evaluateSet(row, []);
  assert.equal(p.tier, "pending");
  const rowBad = { id: "s2", name: "n", conditions: JSON.stringify({ wind_max_ms: 1 }), months: "[]" };
  const v = evaluateSet(rowBad, [
    { local_date: "2026-11-20", hour: "06:00", values: { cloud_low: 10, cloud_mid: 30, cloud_high: 50, precipitation: 0, visibility: 20, wind: 3 } },
  ]);
  assert.equal(v.tier, "no");
  assert.ok(v.failReason);
});

test("KV write throttle (追加2 ④): over-budget user still gets FULL results (transparent) — writes silently stop", async () => {
  const { env, kvStore, db } = makeEnv({ envVars: { SS_KV_WRITES_USER_DAY: 2 } });
  seedGrid(env, "tw-014");
  seedUser(env.DB, "uo", "owner"); // owner: no per-place cap → 3 distinct sets
  const token = await mint(env, "uo");
  const ccs = [{ cloud_low_max: 20 }, { cloud_low_max: 40 }, { cloud_low_max: 60 }];
  for (let i = 0; i < 3; i++) {
    const r = await createSet(env, token, { place_id: "tw-014", name: `c${i}`, conditions: ccs[i] });
    assert.equal(r.status, 200);
  }
  const resp = await handleSubjectSetsEval(makeReq("/subject_sets/eval?place_id=tw-014", { headers: hdr(token) }), env, url("/subject_sets/eval?place_id=tw-014"));
  assert.equal(resp.status, 200); // transparent: the user sees nothing
  const body = await resp.json();
  assert.equal(body.sets.length, 3);
  const ssc = [...kvStore.keys()].filter((k) => k.startsWith("v1:ssc:tw-014:"));
  assert.equal(ssc.length, 2, "only 2 of 3 cache writes land under the per-user daily budget");
  const day = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  assert.equal(db._tables.budget.get(`uo|${day}`), 2);
});

test("KV write budget defaults to 40/user/day (≈25 users saturate the 1000/day KV plan)", () => {
  assert.equal(DEFAULT_MAX_KV_WRITES_USER_DAY, 40);
  assert.equal(25 * DEFAULT_MAX_KV_WRITES_USER_DAY, 1000);
});

// ------------------------------------------------------------------ ③ batch pagination
test("batch eval: ≤20 places per response, cursor pages through, ids ceiling 400", async () => {
  const { env } = makeEnv();
  seedUser(env.DB, "u3", "paid");
  const token = await mint(env, "u3");
  const ids = Array.from({ length: 25 }, (_, i) => `tw-${String(100 + i)}`);
  for (const p of ids) await createSet(env, token, { place_id: p, name: "s", conditions: CC_OK });
  const r1 = await evalBatch(env, token, ids);
  assert.equal(r1.status, 200);
  const b1 = await r1.json();
  assert.equal(b1.results.length, DEFAULT_MAX_BATCH_PLACES);
  assert.equal(b1.page.cursor, 0);
  assert.equal(b1.page.next_cursor, DEFAULT_MAX_BATCH_PLACES);
  assert.equal(b1.page.total_ids, 25);
  const r2 = await evalBatch(env, token, ids, b1.page.next_cursor);
  const b2 = await r2.json();
  assert.equal(b2.results.length, 25 - DEFAULT_MAX_BATCH_PLACES);
  assert.equal(b2.page.next_cursor, null);
  // URL sanity ceiling
  const tooMany = Array.from({ length: MAX_IDS_PER_BATCH_REQUEST + 1 }, (_, i) => `tw-${String(300 + i)}`);
  const r3 = await evalBatch(env, token, tooMany);
  assert.equal(r3.status, 400);
});

test("batch eval: set-budget pagination stops BEFORE a place that no longer fits; single oversized place truncates honestly", async () => {
  const { env } = makeEnv({ envVars: { SS_BATCH_MAX_SETS: 2 } });
  seedUser(env.DB, "u4", "paid");
  seedUser(env.DB, "uo2", "owner");
  const token = await mint(env, "u4");
  await createSet(env, token, { place_id: "tw-a", name: "a1", conditions: CC_OK });
  await createSet(env, token, { place_id: "tw-a", name: "a2", conditions: { cloud_low_max: 40 } });
  await createSet(env, token, { place_id: "tw-b", name: "b1", conditions: CC_OK });
  const r1 = await evalBatch(env, token, ["tw-a", "tw-b"]);
  const b1 = await r1.json();
  assert.equal(b1.results.length, 1, "tw-b does not fit the 2-set page budget");
  assert.equal(b1.results[0].place_id, "tw-a");
  assert.equal(b1.page.next_cursor, 1);
  const r2 = await evalBatch(env, token, ["tw-a", "tw-b"], b1.page.next_cursor);
  const b2 = await r2.json();
  assert.equal(b2.results.length, 1);
  assert.equal(b2.results[0].place_id, "tw-b");
  // single place bigger than the whole page: truncated flag, no cursor loop
  const otoken = await mint(env, "uo2");
  for (let i = 0; i < 3; i++) {
    await createSet(env, otoken, { place_id: "tw-c", name: `c${i}`, conditions: { cloud_low_max: 10 + i * 10 } });
  }
  const r3 = await evalBatch(env, otoken, ["tw-c"]);
  const b3 = await r3.json();
  assert.equal(b3.results[0].truncated, true);
  assert.equal(b3.results[0].sets.length, 2);
  assert.equal(b3.page.next_cursor, null);
});

test("batch eval: places without sets answer with empty sets; defaults are the 追加2 numbers", async () => {
  const { env } = makeEnv();
  seedUser(env.DB, "u5", "paid");
  const token = await mint(env, "u5");
  const r = await evalBatch(env, token, ["tw-x", "tw-y"]);
  const b = await r.json();
  assert.deepEqual(b.results.map((x) => x.sets), [[], []]);
  assert.equal(DEFAULT_MAX_BATCH_PLACES, 20);
  assert.equal(DEFAULT_MAX_BATCH_SETS, 100);
});

test("verdictCacheKey folds the forecast generation in (stale verdicts impossible by construction)", () => {
  const k1 = verdictCacheKey("tw-014", "2026-11-18T00:30:00Z", "ab");
  const k2 = verdictCacheKey("tw-014", "2026-11-18T12:00:00Z", "ab");
  assert.notEqual(k1, k2);
  assert.match(k1, /^v1:ssc:tw-014:/);
});
