// CL-API-02 tests: OAuth flow (mock provider), JWT sign/verify, session,
// anonymous merge. node:test, no external deps.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { signJWT, verifyJWT, authSecret } from "../src/auth.js";

// --- richer in-memory D1 stub ------------------------------------------------
export function makeEnv(opts = {}) {
  const tables = { users: new Map(), favorites: new Set(), notify_rules: new Set(), auth_states: new Map() };
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
              if (args.length === 1) {
                // CL-UI-57 merge cleanup: delete every row keyed to one user id
                for (const k of [...tables.favorites]) if (k.split("|")[0] === args[0]) { tables.favorites.delete(k); meta.changes++; }
              } else {
                const k = keyFor(null, [args[0], args[1]]);
                if (tables.favorites.has(k)) { tables.favorites.delete(k); meta.changes = 1; }
              }
            } else if (/DELETE FROM notify_rules/.test(sql)) {
              if (args.length === 1) {
                for (const k of [...tables.notify_rules]) if (k.split("|")[0] === args[0]) { tables.notify_rules.delete(k); meta.changes++; }
              }
            } else if (/UPDATE users SET/.test(sql)) {
              // CL-UI-57 profile update: [display_name, profile_json, device_id]
              const row = tables.users.get(args[2]);
              if (row) {
                if (args[0] !== undefined) row.display_name = args[0];
                row.profile_json = args[1] ?? null;
                meta.changes = 1;
              }
            } else if (/INSERT INTO auth_states/.test(sql)) {
              const [state, payload] = args;
              if (!tables.auth_states.has(state)) { tables.auth_states.set(state, { state, payload, created_at: new Date().toISOString().replace("T", " ").slice(0, 19) }); meta.changes = 1; }
            } else if (/DELETE FROM auth_states WHERE created_at/.test(sql)) {
              const cutoff = Date.now() - 15 * 60 * 1000;
              for (const [k, v] of [...tables.auth_states]) {
                if (Date.parse(v.created_at.replace(" ", "T") + "Z") < cutoff) { tables.auth_states.delete(k); meta.changes++; }
              }
            } else if (/DELETE FROM auth_states WHERE state/.test(sql)) {
              if (tables.auth_states.has(args[0])) { tables.auth_states.delete(args[0]); meta.changes = 1; }
            }
            return { meta, run: () => {} };
          },
          first: async () => {
            if (/FROM auth_states/.test(sql)) {
              const row = tables.auth_states.get(args[0]);
              return row ? { payload: row.payload } : null;
            }
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
  const { env, tables, store } = makeEnv();
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
    // CL-API-02C: state lives in D1, KV (EVALS) is untouched
    assert.ok(![...store.keys()].some(k => k.startsWith("auth:state:")), "KV must not carry auth state");
    assert.ok(tables.auth_states.has(state));

    // CL-API-05: success is a 302 back to the homepage with HttpOnly cookies,
    // never a bare JSON page.
    const cb = await worker.fetch(req(`/auth/line/callback?code=xyz&state=${state}`), env, {});
    assert.equal(cb.status, 302);
    const cbLoc = new URL(cb.headers.get("Location"));
    assert.equal(cbLoc.origin + cbLoc.pathname, "https://chaselights.app/");
    assert.ok(!cbLoc.searchParams.has("auth_error"));
    const cbCookies = cb.headers.getSetCookie();
    assert.ok(cbCookies.some(c => c.startsWith("cl_session=") && c.includes("HttpOnly")));
    assert.ok(cbCookies.some(c => c.startsWith("cl_refresh=") && c.includes("HttpOnly")));
    assert.ok(tables.users.has("p:line:U123"));
    assert.ok(!tables.auth_states.has(state), "single-use state row must be deleted at read");

    // CL-API-05: every failure path is a 302 to the homepage with ?auth_error=1
    // state is single-use: replay rejected
    const replay = await worker.fetch(req(`/auth/line/callback?code=xyz&state=${state}`), env, {});
    assert.equal(replay.status, 302);
    assert.ok(new URL(replay.headers.get("Location")).searchParams.get("auth_error") === "1");
    // forged state rejected
    const forged = await worker.fetch(req("/auth/line/callback?code=xyz&state=forged"), env, {});
    assert.equal(forged.status, 302);
    assert.ok(new URL(forged.headers.get("Location")).searchParams.get("auth_error") === "1");
    assert.ok(calls.some(u => u.includes("api.line.me/oauth2/v2.1/token")));
  } finally { globalThis.fetch = realFetch; }
});

// --- CL-API-02C: D1 state expiry (payload exp) + opportunistic old-row cleanup --
test("expired auth state rejected and stale rows cleaned on read", async () => {
  const { env, tables } = makeEnv();
  env.LINE_LOGIN_CLIENT_ID = "line-client-id";
  env.LINE_LOGIN_CLIENT_SECRET = "line-client-secret";
  const realFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    if (String(url).includes("/oauth2/v2.1/token")) return new Response(JSON.stringify({ access_token: "fake-at" }), { status: 200 });
    if (String(url).includes("/oauth2/v2.1/userinfo") || String(url).includes("/oauth2/v2.1/verify")) return new Response(JSON.stringify({ sub: "U999", name: "Late" }), { status: 200 });
    return realFetch(url);
  };
  try {
    const start = await worker.fetch(req("/auth/line/start"), env, {});
    assert.equal(start.status, 302);
    const state = new URL(start.headers.get("Location")).searchParams.get("state");

    // (a) payload exp in the past → 302 ?auth_error=1
    const row = tables.auth_states.get(state);
    const st = JSON.parse(row.payload);
    st.exp = Date.now() - 1000;
    tables.auth_states.set(state, { ...row, payload: JSON.stringify(st) });
    const exp = await worker.fetch(req(`/auth/line/callback?code=xyz&state=${state}`), env, {});
    assert.equal(exp.status, 302);
    assert.ok(new URL(exp.headers.get("Location")).searchParams.get("auth_error") === "1");
    assert.ok(!tables.auth_states.has(state), "expired row still deleted on read");

    // (b) stale created_at rows are swept by the opportunistic cleanup
    const stale = "stale-state-row";
    tables.auth_states.set(stale, {
      state: stale, payload: JSON.stringify({ provider: "line", redirectUri: "https://x", merge: null, exp: Date.now() + 600_000 }),
      created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString().replace("T", " ").slice(0, 19),
    });
    const start2 = await worker.fetch(req("/auth/line/start"), env, {});
    assert.equal(start2.status, 302);
    const state2 = new URL(start2.headers.get("Location")).searchParams.get("state");
    const cb2 = await worker.fetch(req(`/auth/line/callback?code=xyz&state=${state2}`), env, {});
    assert.equal(cb2.status, 302);
    assert.ok(!tables.auth_states.has(stale), "read-time cleanup removed rows older than 15 minutes");
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

// --- CL-UI-57: favorites isolation across logout and account switch ----------
test("CL-UI-57 favorites isolation: merge leaves no anonymous residue; logout shows the empty device list; account B never sees A's favorites", async () => {
  const { env, tables } = makeEnv({ AUTH_MOCK: "1" });
  const A = "p:line:acct-a", B = "p:line:acct-b", DEV = "dev-device-57";

  // Account A already faved 大屯山-equivalent (tw-001) directly on the account.
  await env.DB.prepare("INSERT INTO favorites").bind(A, "tw-001").run();
  // The anonymous device also faved tw-001 (the merge conflict case) + tw-002.
  await env.DB.prepare("INSERT INTO favorites").bind(DEV, "tw-001").run();
  await env.DB.prepare("INSERT INTO favorites").bind(DEV, "tw-002").run();

  // Login as A with the device merge.
  const loginA = await worker.fetch(req(`/auth/mock/start?provider=line&user=acct-a&merge=${DEV}`), env, {});
  const tokA = (await loginA.json()).accessToken;
  assert.ok([...tables.favorites].some(k => k.split("|")[0] === A && k.split("|")[1] === "tw-002"));

  // CL-UI-57 core: NO residue stays under the anonymous device id, not even
  // the conflicting tw-001 row that UPDATE OR IGNORE skipped.
  assert.ok(![...tables.favorites].some(k => k.split("|")[0] === DEV), "anonymous device rows must be fully cleaned after merge");

  // After logout (no cookie/Bearer), the device id resolves to the anonymous
  // list — which is now empty, never A's favorites.
  const anonAfterLogout = await worker.fetch(req(`/favorites?userId=${DEV}`), env, {});
  assert.deepEqual((await anonAfterLogout.json()).favorites, []);

  // Account B on the same browser sees only its own favorites.
  const loginB = await worker.fetch(req(`/auth/mock/start?provider=line&user=acct-b&merge=${DEV}`), env, {});
  const tokB = (await loginB.json()).accessToken;
  const favsB = await worker.fetch(req("/favorites", { headers: { Authorization: `Bearer ${tokB}` } }), env, {});
  const listB = (await favsB.json()).favorites.map(f => f.place_id);
  assert.ok(!listB.includes("tw-001") && !listB.includes("tw-002"), "account B must not inherit account A's favorites");

  // A still sees its own merged list.
  const favsA = await worker.fetch(req("/favorites", { headers: { Authorization: `Bearer ${tokA}` } }), env, {});
  assert.deepEqual((await favsA.json()).favorites.map(f => f.place_id).sort(), ["tw-001", "tw-002"]);
});

// --- CL-UI-57: member profile editing (PATCH /auth/profile) -------------------
test("CL-UI-57 profile: PATCH updates display_name + optional profile fields; /auth/me returns them; anonymous is 401", async () => {
  const { env } = makeEnv({ AUTH_MOCK: "1" });
  const anon = await worker.fetch(req("/auth/profile", { method: "PATCH", body: JSON.stringify({ displayName: "X" }) }), env, {});
  assert.equal(anon.status, 401);

  const login = await worker.fetch(req("/auth/mock/start?provider=line&user=profer&name=Profer"), env, {});
  const tok = (await login.json()).accessToken;
  const auth = { Authorization: `Bearer ${tok}` };

  const patch = await worker.fetch(req("/auth/profile", {
    method: "PATCH", headers: { ...auth, "Content-Type": "application/json" },
    body: JSON.stringify({ displayName: "山行者", profile: { experience: "十年", region: "大台北", bio: "  ", junk: "ignored" } }),
  }), env, {});
  assert.equal(patch.status, 200);
  const saved = (await patch.json()).user;
  assert.equal(saved.displayName, "山行者");
  assert.deepEqual(saved.profile, { experience: "十年", region: "大台北" }, "empty strings are cleared, unknown keys dropped");

  const me = await worker.fetch(req("/auth/me", { headers: auth }), env, {});
  const meBody = (await me.json()).user;
  assert.equal(meBody.displayName, "山行者");
  assert.deepEqual(meBody.profile, { experience: "十年", region: "大台北" });

  // Partial update merges: only bio this time; existing keys keep their value.
  const patch2 = await worker.fetch(req("/auth/profile", {
    method: "PATCH", headers: { ...auth, "Content-Type": "application/json" },
    body: JSON.stringify({ profile: { bio: "晨拍控" } }),
  }), env, {});
  assert.deepEqual((await patch2.json()).user.profile, { experience: "十年", region: "大台北", bio: "晨拍控" });

  // Validation: blank displayName and over-length are rejected.
  const bad = await worker.fetch(req("/auth/profile", { method: "PATCH", headers: { ...auth, "Content-Type": "application/json" }, body: JSON.stringify({ displayName: "   " }) }), env, {});
  assert.equal(bad.status, 400);
  const long = await worker.fetch(req("/auth/profile", { method: "PATCH", headers: { ...auth, "Content-Type": "application/json" }, body: JSON.stringify({ displayName: "x".repeat(101) }) }), env, {});
  assert.equal(long.status, 400);
  const longBio = await worker.fetch(req("/auth/profile", { method: "PATCH", headers: { ...auth, "Content-Type": "application/json" }, body: JSON.stringify({ profile: { bio: "y".repeat(201) } }) }), env, {});
  assert.equal(longBio.status, 200);
  const meAfter = (await (await worker.fetch(req("/auth/me", { headers: auth }), env, {})).json()).user;
  assert.equal(meAfter.profile.bio.length, 200, "profile fields are capped at 200 chars");
});
