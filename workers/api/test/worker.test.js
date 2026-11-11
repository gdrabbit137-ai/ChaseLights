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

test("catalog digests: 503 fail-closed when absent, 200 with APP-01-tolerant shape when synced", async () => {
  const { env } = makeEnv();
  const miss = await worker.fetch(makeReq("/catalog/digests"), env, {});
  assert.equal(miss.status, 503);

  const DIGEST = "39a773885c8d14036e9e8fdcfe38f3419e07ba2a2f1eec3812d22c14d19148ca";
  env.EVALS.put("v1:catalog:digest", JSON.stringify({
    digest: DIGEST, catalog: { sha256: DIGEST }, generated_at: "2026-11-10T18:30:00Z",
  }));
  const hit = await worker.fetch(makeReq("/catalog/digests"), env, {});
  assert.equal(hit.status, 200);
  const body = await hit.json();
  assert.equal(body.digest, DIGEST);
  assert.equal(body.catalog.sha256, DIGEST);
  assert.ok(body.generated_at);
});

// APP-01 version-checker compatibility: the checker must accept either of the
// two tolerant shapes ({digest} alone, or {catalog:{sha256}}+generated_at) as
// served by GET /api/v1/catalog/digests.
test("APP-01 checker simulation accepts both digest response shapes", async () => {
  const DIGEST = "39a773885c8d14036e9e8fdcfe38f3419e07ba2a2f1eec3812d22c14d19148ca";
  const checker = (body) => {
    if (typeof body.digest === "string" && /^[a-f0-9]{64}$/.test(body.digest)) return body.digest;
    if (body.catalog && typeof body.catalog.sha256 === "string") return body.catalog.sha256;
    throw new Error("no digest in response");
  };
  const { env } = makeEnv();
  env.EVALS.put("v1:catalog:digest", JSON.stringify({ digest: DIGEST, generated_at: "2026-11-10T18:30:00Z" }));
  const res = await worker.fetch(makeReq("/catalog/digests"), env, {});
  assert.equal(checker(await res.json()), DIGEST);
  const res2 = await worker.fetch(makeReq("/catalog/digests"), env, {});
  assert.equal(checker({ catalog: { sha256: DIGEST }, generated_at: "2026-11-10T18:30:00Z" }), DIGEST);
  assert.throws(() => checker({ foo: 1 }));
});

test("unknown path 404; rate limit 429 after burst", async () => {
  const { env } = makeEnv();
  const nf = await worker.fetch(makeReq("/nope"), env, {});
  assert.equal(nf.status, 404);
  let last;
  for (let i = 0; i < 70; i++) last = await worker.fetch(makeReq("/health", { headers: { "CF-Connecting-IP": "1.2.3.4" } }), env, {});
  assert.equal(last.status, 429);
});
