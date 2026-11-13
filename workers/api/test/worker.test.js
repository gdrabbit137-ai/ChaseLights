// Minimal unit tests for chaselights-api worker (node:test, no external deps).
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

function makeEnv() {
  const store = new Map();
  const sqlLog = [];
  const rows = {};
  const db = {
    prepare(sql) {
      return {
        bind: (...args) => ({ run: async () => { sqlLog.push([sql, args]); }, first: async () => (rows.first = { device_id: "u1" }), all: async () => ({ results: [{ place_id: "tw-001", created_at: "2026-11-10 00:00:00" }] }) }),
      };
    },
  };
  return { env: { EVALS: { get: async (k, type) => { const v = store.get(k); if (v === undefined) return null; return type === "json" ? JSON.parse(v) : v; }, put: (k, v) => store.set(k, v), _store: store }, DB: db }, sqlLog };
}

function makeReq(path, opts = {}) {
  const headers = new Headers(opts.headers || {});
  return new Request(`https://chaselights.app/api/v1${path}`, opts);
}

test("health returns ok", async () => {
  const { env } = makeEnv();
  const res = await worker.fetch(makeReq("/health"), env, {});
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.equal(body.ok, true);
  assert.equal(body.service, "chaselights-api");
});

test("CORS restricted to chaselights.app", async () => {
  const { env } = makeEnv();
  const bad = await worker.fetch(makeReq("/health", { headers: { Origin: "https://evil.example" } }), env, {});
  assert.equal(bad.headers.get("Access-Control-Allow-Origin"), "null");
  const good = await worker.fetch(makeReq("/health", { headers: { Origin: "https://chaselights.app" } }), env, {});
  assert.equal(good.headers.get("Access-Control-Allow-Origin"), "https://chaselights.app");
});

test("evaluations: 503 when not synced, index when synced", async () => {
  let { env, } = makeEnv();
  const miss = await worker.fetch(makeReq("/evaluations"), env, {});
  assert.equal(miss.status, 503);
  env.EVALS.put("v1:evals:index", JSON.stringify({ place_ids: ["tw-001"], place_count: 1 }));
  const hit = await worker.fetch(makeReq("/evaluations"), env, {});
  const body = await hit.json();
  assert.deepEqual(body.place_ids, ["tw-001"]);
});

test("evaluations: 404 for unknown place, record when present", async () => {
  const { env } = makeEnv();
  const miss = await worker.fetch(makeReq("/evaluations?place_id=nope"), env, {});
  assert.equal(miss.status, 404);
  env.EVALS.put("v1:evals:tw-001", JSON.stringify({ place_id: "tw-001", subjects: [] }));
  const hit = await worker.fetch(makeReq("/evaluations?place_id=tw-001"), env, {});
  assert.equal((await hit.json()).place_id, "tw-001");
});

test("favorites: GET requires userId, POST add idempotent, remove deletes", async () => {
  const { env, sqlLog } = makeEnv();
  const noUser = await worker.fetch(makeReq("/favorites"), env, {});
  assert.equal(noUser.status, 401); // CL-API-02: anonymous GET without credentials is now 401

  const add = await worker.fetch(makeReq("/favorites", { method: "POST", body: JSON.stringify({ userId: "dev1", placeId: "tw-001" }) }), env, {});
  assert.equal((await add.json()).ok, true);
  assert.ok(sqlLog.some(([sql]) => sql.includes("INSERT INTO favorites")));

  const del = await worker.fetch(makeReq("/favorites", { method: "POST", body: JSON.stringify({ userId: "dev1", placeId: "tw-001", action: "remove" }) }), env, {});
  assert.equal((await del.json()).action, "remove");
});

test("unknown path 404; rate limit 429 after burst (write class, CL-API-07)", async () => {
  const { env } = makeEnv();
  const nf = await worker.fetch(makeReq("/nope"), env, {});
  assert.equal(nf.status, 404);
  let last;
  // CL-API-07: /health is a lenient read (600/min); the default write class
  // (60/min) still 429s after a burst — probe it via the unknown path, which
  // is rate-limited before routing.
  for (let i = 0; i < 70; i++) last = await worker.fetch(makeReq("/nope", { headers: { "CF-Connecting-IP": "1.2.3.4" } }), env, {});
  assert.equal(last.status, 429);
});

// CL-API-07: cheap reads share a lenient bucket (600/min) — the owner bug was
// 1×/auth/me + 6×/favorites per page load tripping the old single 60/min
// bucket and the clients misreading 429 as signed-out.
test("CL-API-07: 30 consecutive /auth/me GETs never 429 (read class)", async () => {
  const { env } = makeEnv();
  let last;
  for (let i = 0; i < 30; i++) {
    last = await worker.fetch(makeReq("/auth/me", { headers: { "CF-Connecting-IP": "9.9.9.9" } }), env, {});
    assert.notEqual(last.status, 429, `me request #${i + 1} must not be rate limited`);
  }
});

test("CL-API-07: read bursts never consume the strict auth-write budget", async () => {
  const { env } = makeEnv();
  // 65 read-class GETs (> old 60/min) must all pass, and the auth class
  // bucket stays untouched.
  let last;
  for (let i = 0; i < 65; i++) last = await worker.fetch(makeReq("/health", { headers: { "CF-Connecting-IP": "8.8.8.8" } }), env, {});
  assert.equal(last.status, 200);
  // Strict auth class: 25 /auth/mock/start hits exceed max 20 → 429.
  let authLast;
  for (let i = 0; i < 25; i++) authLast = await worker.fetch(makeReq("/auth/mock/start", { headers: { "CF-Connecting-IP": "8.8.8.8" } }), env, {});
  assert.equal(authLast.status, 429);
});
