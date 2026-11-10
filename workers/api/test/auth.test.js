// CL-API-02 tests: OAuth flow (mock provider), JWT sign/verify, session,
// anonymous merge. node:test, no external deps.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { signJWT, verifyJWT, authSecret } from "../src/auth.js";

// --- richer in-memory D1 stub ------------------------------------------------
export function makeEnv(opts = {}) {
  const tables = { users: new Map(), favorites: new Set(), notify_rules: new Set() };
  const store = new Map();
  const keyFor = (t, pk) => pk.join("|");
  const db = {
    prepare(sql) {
      return {
        bind: (...args) => ({
          run: async () => {
            const meta = { changes: 0 };
            if (/INSERT INTO users/.test(sql)) {
              const [device_id, provider, puid, name] = args;
              if (!tables.users.has(device_id)) {
                tables.users.set(device_id, { device_id, provider: provider ?? null, provider_user_id: puid ?? null, display_name: name ?? null, level: "free" });
                meta.changes = 1;
              }
            } else if (/INSERT OR IGNORE INTO favorites/.test(sql) || /INSERT INTO favorites/.test(sql)) {
              const k = keyFor(null, [args[0], args[1]]);
              if (!tables.favorites.has(k)) { tables.favorites.add(k); meta.changes = 1; }
            } else if (/UPDATE OR IGNORE favorites SET user_id/.test(sql)) {
              for (const k of [...tables.favorites]) {
                const [uid] = k.split("|");
                if (uid === args[1] && !tables.favorites.has(`${args[0]}|${k.split("|")[1]}`)) {
                  tables.favorites.delete(k); tables.favorites.add(`${args[0]}|${k.split("|")[1]}`); meta.changes++;
                }
              }
            } else if (/UPDATE OR IGNORE notify_rules SET user_id/.test(sql)) {
              for (const k of [...tables.notify_rules]) {
                const [uid, place] = k.split("|");
                if (uid === args[1] && !tables.notify_rules.has(`${args[0]}|${place}`)) {
                  tables.notify_rules.delete(k); tables.notify_rules.add(`${args[0]}|${place}`); meta.changes++;
                }
              }
            } else if (/DELETE FROM favorites/.test(sql)) {
              const k = keyFor(null, [args[0], args[1]]);
              if (tables.favorites.has(k)) { tables.favorites.delete(k); meta.changes = 1; }
            }
            return { meta, run: () => {} };
          },
          first: async () => {
            if (/FROM users/.test(sql)) {
              const row = tables.users.get(args[0]);
              return row ? { ...row } : null;
            }
            return null;
          },
          all: async () => {
            if (/FROM favorites/.test(sql)) {
              const results = [...tables.favorites].filter(k => k.split("|")[0] === args[0]).map(k => ({ place_id: k.split("|")[1] }));
              return { results };
            }
            return { results: [] };
          },
        }),
      };
    },
  };
  const env = {
    DB: db,
    EVALS: {
      get: async (k) => store.get(k) ?? null,
      put: async (k, v) => store.set(k, v),
      delete: async (k) => store.delete(k),
    },
    AUTH_SECRET: opts.AUTH_SECRET || "test-secret-000",
  };
  if (opts.AUTH_MOCK) env.AUTH_MOCK = "1";
  return { env, tables, store };
}

const req = (path, opts = {}) => new Request(`https://chaselights.app/api/v1${path}`, opts);

// --- JWT unit tests -----------------------------------------------------------
test("JWT sign/verify roundtrip; tamper and expiry rejected", async () => {
  const s = "test-secret-000";
  const now = Math.floor(Date.now() / 1000);
  const tok = await signJWT({ sub: "u1", typ: "access", exp: now + 60, iat: now }, s);
  const payload = await verifyJWT(tok, s);
  assert.equal(payload.sub, "u1");
  assert.equal(payload.typ, "access");

  const tampered = tok.slice(0, -2) + (tok.endsWith("aa") ? "bb" : "aa");
  assert.equal(await verifyJWT(tampered, s), null);
  assert.equal(await verifyJWT(tok, "wrong-secret"), null);
  const expired = await signJWT({ sub: "u1", typ: "access", exp: now - 10, iat: now - 100 }, s);
  assert.equal(await verifyJWT(expired, s), null);
});

// --- auth/me with Authorization header ----------------------------------------
test("GET /auth/me: 401 anonymous, 200 with valid Bearer JWT", async () => {
  const { env } = makeEnv();
  const anon = await worker.fetch(req("/auth/me"), env, {});
  assert.equal(anon.status, 401);

  const tables = { users: new Map([["p:line:u-777", { device_id: "p:line:u-777", provider: "line", provider_user_id: "u-777", display_name: "Lin", level: "free" }]]) };
  env.DB = {
    prepare(sql) { return { bind: (...a) => ({ run: async () => ({}), first: async () => tables.users.get(a[0]) ?? null, all: async () => ({ results: [] }) }) }; },
  };
  const tok = await signJWT({ sub: "p:line:u-777", typ: "access", exp: Math.floor(Date.now() / 1000) + 60 }, authSecret(env));
  const ok = await worker.fetch(req("/auth/me", { headers: { Authorization: `Bearer ${tok}` } }), env, {});
  assert.equal(ok.status, 200);
  const body = await ok.json();
  assert.equal(body.user.provider, "line");
  assert.equal(body.user.level, "free");
});

// --- mock provider OAuth flow ---------------------------------------------------
test("mock provider: disabled in prod-like env, session flow works with AUTH_MOCK=1 (cookies + Bearer)", async () => {
  const off = makeEnv();
  const r404 = await worker.fetch(req("/auth/mock/start?provider=line&user=m1"), off.env, {});
  assert.equal(r404.status, 404);

  const { env, tables } = makeEnv({ AUTH_MOCK: "1" });
  const start = await worker.fetch(req("/auth/mock/start?provider=line&user=m1&name=Mocker&merge=dev-anon-1"), env, {});
  assert.equal(start.status, 200);
  const body = await start.json();
  assert.equal(body.user.id, "p:line:m1");
  assert.ok(body.accessToken);
  const cookies = start.headers.getSetCookie();
  assert.ok(cookies.some(c => c.startsWith("cl_session=") && c.includes("HttpOnly")));
  assert.ok(cookies.some(c => c.startsWith("cl_refresh=") && c.includes("HttpOnly")));
  assert.ok(tables.users.has("p:line:m1"));

  const me = await worker.fetch(req("/auth/me", { headers: { Cookie: `cl_session=${body.accessToken}` } }), env, {});
  assert.equal(me.status, 200);
  assert.equal((await me.json()).user.displayName, "Mocker");

  const meBearer = await worker.fetch(req("/auth/me", { headers: { Authorization: `Bearer ${body.accessToken}` } }), env, {});
  assert.equal(meBearer.status, 200);
});

// --- full OAuth callback with mocked provider endpoints (LINE) ------------------
test("OAuth flow: start redirects with state; callback exchanges code via mocked LINE endpoints; state single-use", async () => {
  const { env, tables } = makeEnv();
  env.LINE_LOGIN_CLIENT_ID = "line-client-id";
  env.LINE_LOGIN_CLIENT_SECRET = "line-client-secret";
  const calls = [];
  const realFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    calls.push(String(url));
    if (String(url).includes("/oauth2/v2.1/token")) {
      return new Response(JSON.stringify({ access_token: "fake-at", token_type: "Bearer" }), { status: 200 });
    }
    if (String(url).includes("/oauth2/v2.1/userinfo")) {
      return new Response(JSON.stringify({ sub: "U123", name: "LINE User" }), { status: 200 });
    }
    return realFetch(url, init);
  };
  try {
    const start = await worker.fetch(req("/auth/line/start?merge=dev-anon-2"), env, {});
    assert.equal(start.status, 302);
    const loc = start.headers.get("Location");
    assert.ok(loc.startsWith("https://access.line.me/oauth2/v2.1/authorize"));
    const state = new URL(loc).searchParams.get("state");
    assert.ok(state);
    assert.ok(new URL(loc).searchParams.get("redirect_uri").includes("/api/v1/auth/line/callback"));

    const cb = await worker.fetch(req(`/auth/line/callback?code=xyz&state=${state}`), env, {});
    assert.equal(cb.status, 200);
    const body = await cb.json();
    assert.equal(body.user.id, "p:line:U123");
    assert.equal(body.user.displayName, "LINE User");
    assert.ok(tables.users.has("p:line:U123"));

    // state is single-use: replay rejected
    const replay = await worker.fetch(req(`/auth/line/callback?code=xyz&state=${state}`), env, {});
    assert.equal(replay.status, 400);
    // forged state rejected
    const forged = await worker.fetch(req("/auth/line/callback?code=xyz&state=forged"), env, {});
    assert.equal(forged.status, 400);
    assert.ok(calls.some(u => u.includes("api.line.me/oauth2/v2.1/token")));
  } finally { globalThis.fetch = realFetch; }
});

// --- refresh + logout ------------------------------------------------------------
test("refresh issues new access token; logout clears cookies", async () => {
  const { env } = makeEnv({ AUTH_MOCK: "1" });
  const login = await worker.fetch(req("/auth/mock/start?provider=google&user=g1&name=G User"), env, {});
  const loginBody = await login.json();
  const refresh = await worker.fetch(req("/auth/refresh", { method: "POST", body: JSON.stringify({ refreshToken: loginBody.refreshToken ?? "" }) }), env, {});
  // refreshToken not echoed by mock start? — it is not; use refresh cookie instead
  const cookies = login.headers.get("Set-Cookie") || "";
  const rt = /cl_refresh=([^;]+)/.exec(cookies)?.[1];
  const refresh2 = await worker.fetch(req("/auth/refresh", { method: "POST", body: JSON.stringify({ refreshToken: rt }) }), env, {});
  assert.equal(refresh2.status, 200);
  const at = (await refresh2.json()).accessToken;
  const me = await worker.fetch(req("/auth/me", { headers: { Authorization: `Bearer ${at}` } }), env, {});
  assert.equal(me.status, 200);

  const bad = await worker.fetch(req("/auth/refresh", { method: "POST", body: JSON.stringify({ refreshToken: "garbage" }) }), env, {});
  assert.equal(bad.status, 401);

  const out = await worker.fetch(req("/auth/logout", { method: "POST" }), env, {});
  assert.equal(out.status, 200);
  assert.ok((out.headers.get("Set-Cookie") || "").includes("Max-Age=0"));
});

// --- anonymous merge case ----------------------------------------------------------
test("anonymous device data merges into OAuth identity at login", async () => {
  const { env, tables } = makeEnv({ AUTH_MOCK: "1" });
  // anonymous device browses first
  await env.DB.prepare("INSERT INTO favorites").bind("dev-anon-9", "tw-001").run();
  await env.DB.prepare("INSERT INTO favorites").bind("dev-anon-9", "tw-002").run();
  await env.DB.prepare("UPDATE OR IGNORE notify_rules SET user_id").bind("x", "y").run(); // no-op warmup
  tables.notify_rules.add("dev-anon-9|tw-001");

  const login = await worker.fetch(req("/auth/mock/start?provider=line&user=merger&merge=dev-anon-9"), env, {});
  const body = await login.json();
  assert.equal(body.mergedRows, 3); // 2 favorites + 1 notify_rule

  const favs = [...tables.favorites].map(k => k.split("|"));
  assert.ok(favs.some(([u, p]) => u === "p:line:merger" && p === "tw-001"));
  assert.ok(favs.some(([u, p]) => u === "p:line:merger" && p === "tw-002"));
  assert.ok([...tables.notify_rules].some(k => k.startsWith("p:line:merger|")));
  assert.ok(![...tables.favorites].some(([u]) => u === "dev-anon-9"));

  // Bearer JWT now scopes favorites to the merged identity
  const me = await worker.fetch(req("/auth/me", { headers: { Authorization: `Bearer ${body.accessToken}` } }), env, {});
  assert.equal(me.status, 200);
  const res = await worker.fetch(req("/favorites", { headers: { Authorization: `Bearer ${body.accessToken}` } }), env, {});
  const favBody = await res.json();
  assert.equal(favBody.userId, "p:line:merger");
  assert.deepEqual(favBody.favorites.map(f => f.place_id).sort(), ["tw-001", "tw-002"]);
});

// --- favorites auth-aware resolution ------------------------------------------------
test("favorites: Bearer JWT takes precedence over legacy userId param; legacy anonymous still works", async () => {
  const { env } = makeEnv({ AUTH_MOCK: "1" });
  const login = await worker.fetch(req("/auth/mock/start?provider=line&user=pri&name=Pri"), env, {});
  const tok = (await login.json()).accessToken;

  const asBearer = await worker.fetch(req("/favorites?userId=someone-else", { headers: { Authorization: `Bearer ${tok}` } }), env, {});
  const bj = await asBearer.json();
  assert.equal(bj.userId, "p:line:pri");

  const anon = await worker.fetch(req("/favorites", { method: "POST", body: JSON.stringify({ userId: "dev-x", placeId: "tw-001" }) }), env, {});
  assert.equal((await anon.json()).ok, true);
});

test("self-heal: /auth/me re-materializes users row for valid JWT with no row", async () => {
  const { env } = makeEnv();
  const tok = await signJWT({ sub: "p:line:ghost", name: "Ghost", level: "free", typ: "access", exp: Math.floor(Date.now() / 1000) + 60 }, "test-secret-000");
  const me = await worker.fetch(req("/auth/me", { headers: { Authorization: `Bearer ${tok}` } }), env, {});
  assert.equal(me.status, 200);
  const body = await me.json();
  assert.equal(body.user.provider, "line");
  assert.equal(body.user.providerUserId, "ghost");
});
