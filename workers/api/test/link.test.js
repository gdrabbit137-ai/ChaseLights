// CL-APP-07 tests: account linking + Sign in with Apple (mock/fake-crypto).
// In-memory D1 stub mirrors the real handlers' SQL (same technique as
// auth.test.js makeEnv, extended for account_links / link_email_verifications /
// verified_email / feedback / push_tokens). node:test, no external deps.
import test, { before } from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

const SECRET = "test-secret-000";

function makeEnv(opts = {}) {
  const users = new Map(); // device_id → row (uidOrder = created_at order)
  const favorites = new Set(); // "uid|place"
  const notifyRules = new Map(); // id → row
  const feedback = new Map(); // id → row
  const pushTokens = new Map(); // token → row
  const accountLinks = new Map(); // alias_device_id → row
  const linkVerifications = new Map(); // token → row
  const authStates = new Map();
  const uidOrder = [];

  const getUsersByEmail = (email, exceptId) =>
    uidOrder.filter((d) => users.get(d).verified_email === email && d !== exceptId);

  const db = {
    prepare(sql) {
      return {
        bind(...args) {
          const run = async () => {
            const meta = { changes: 0 };
            if (/INSERT INTO users/.test(sql)) {
              const [device_id, provider, puid, name, verifiedEmail] = args;
              if (!users.has(device_id)) {
                users.set(device_id, { device_id, provider: provider ?? null, provider_user_id: puid ?? null, display_name: name ?? null, level: "free", verified_email: verifiedEmail ?? null, created_at: `2026-01-01 00:00:${String(uidOrder.length).padStart(2, "0")}` });
                uidOrder.push(device_id);
                meta.changes = 1;
              } else {
                // ON CONFLICT DO UPDATE backfill semantics (never overwrite email)
                const row = users.get(device_id);
                row.provider = provider ?? row.provider;
                row.provider_user_id = puid ?? row.provider_user_id;
                if (row.display_name === null || row.display_name === "") row.display_name = name ?? row.display_name;
                if ((row.verified_email === null || row.verified_email === "") && verifiedEmail) row.verified_email = verifiedEmail;
                meta.changes = 1;
              }
            } else if (/UPDATE users SET verified_email/.test(sql)) {
              const [email, id] = args;
              if (getUsersByEmail(email, id).length > 0) throw new Error("UNIQUE constraint failed: users.verified_email");
              const row = users.get(id);
              if (row) { row.verified_email = email; meta.changes = 1; }
            } else if (/UPDATE OR IGNORE favorites SET user_id/.test(sql)) {
              for (const k of [...favorites]) {
                const [uid, place] = k.split("|");
                if (uid === args[1] && !favorites.has(`${args[0]}|${place}`)) {
                  favorites.delete(k); favorites.add(`${args[0]}|${place}`); meta.changes++;
                }
              }
            } else if (/UPDATE notify_rules SET user_id/.test(sql)) {
              for (const row of notifyRules.values()) {
                if (row.user_id === args[1]) { row.user_id = args[0]; meta.changes++; }
              }
            } else if (/UPDATE OR IGNORE feedback SET user_id/.test(sql)) {
              for (const row of feedback.values()) {
                if (row.user_id !== args[1]) continue;
                const conflict = row.type === "rating" && [...feedback.values()].some(
                  (r) => r.user_id === args[0] && r.place_id === row.place_id && r.type === "rating");
                if (conflict) continue; // OR IGNORE: the primary's rating wins
                row.user_id = args[0]; meta.changes++;
              }
            } else if (/UPDATE OR IGNORE custom_places/.test(sql)) {
              throw new Error("no such table: custom_places"); // CL-APP-06 not merged yet
            } else if (/UPDATE OR IGNORE push_tokens SET user_device_id/.test(sql)) {
              for (const row of pushTokens.values()) {
                if (row.user_device_id === args[1]) { row.user_device_id = args[0]; meta.changes++; }
              }
            } else if (/INSERT INTO favorites/.test(sql)) {
              const k = `${args[0]}|${args[1]}`;
              if (!favorites.has(k)) { favorites.add(k); meta.changes = 1; }
            } else if (/DELETE FROM favorites/.test(sql)) {
              if (args.length === 1) {
                for (const k of [...favorites]) if (k.split("|")[0] === args[0]) { favorites.delete(k); meta.changes++; }
              } else if (favorites.has(`${args[0]}|${args[1]}`)) { favorites.delete(`${args[0]}|${args[1]}`); meta.changes = 1; }
            } else if (/DELETE FROM feedback/.test(sql)) {
              for (const [k, row] of [...feedback]) {
                if (row.user_id === args[0]) { feedback.delete(k); meta.changes++; }
              }
            } else if (/INSERT INTO account_links/.test(sql)) {
              const [alias, primary, provider, puid, email] = args;
              if (!accountLinks.has(alias)) {
                accountLinks.set(alias, { alias_device_id: alias, primary_user_id: primary, alias_provider: provider, alias_provider_user_id: puid, verified_email: email ?? null, created_at: "2026-01-01 00:00:00" });
                meta.changes = 1;
              }
            } else if (/INSERT INTO link_email_verifications/.test(sql)) {
              const [token, userId, email] = args;
              linkVerifications.set(token, { token, user_id: userId, email, consumed: 0, created_at: new Date().toISOString().replace("T", " ").slice(0, 19) });
              meta.changes = 1;
            } else if (/DELETE FROM link_email_verifications WHERE created_at/.test(sql)) {
              const cutoff = Date.now() - 30 * 60 * 1000;
              for (const [k, v] of [...linkVerifications]) {
                if (Date.parse(v.created_at.replace(" ", "T") + "Z") < cutoff || v.consumed) { linkVerifications.delete(k); meta.changes++; }
              }
            } else if (/DELETE FROM link_email_verifications WHERE token/.test(sql)) {
              if (linkVerifications.has(args[0])) { linkVerifications.delete(args[0]); meta.changes = 1; }
            } else if (/INSERT INTO auth_states/.test(sql)) {
              authStates.set(args[0], { payload: args[1], created_at: new Date().toISOString().replace("T", " ").slice(0, 19) });
              meta.changes = 1;
            } else if (/DELETE FROM auth_states WHERE created_at/.test(sql)) {
              const cutoff = Date.now() - 15 * 60 * 1000;
              for (const [k, v] of [...authStates]) {
                if (Date.parse(v.created_at.replace(" ", "T") + "Z") < cutoff) authStates.delete(k);
              }
            } else if (/DELETE FROM auth_states WHERE state/.test(sql)) {
              if (authStates.has(args[0])) { authStates.delete(args[0]); meta.changes = 1; }
            }
            return { meta };
          };
          const first = async () => {
            if (/FROM link_email_verifications/.test(sql)) {
              const row = linkVerifications.get(args[0]);
              return row ? { ...row } : null;
            }
            if (/FROM auth_states/.test(sql)) {
              const row = authStates.get(args[0]);
              return row ? { payload: row.payload } : null;
            }
            if (/FROM account_links/.test(sql)) {
              const row = accountLinks.get(args[0]);
              return row ? { primary_user_id: row.primary_user_id } : null;
            }
            if (/FROM users WHERE verified_email/.test(sql)) {
              const matches = getUsersByEmail(args[0], args[1]);
              return matches.length ? { device_id: matches[0] } : null;
            }
            if (/FROM users/.test(sql)) {
              const row = users.get(args[0]);
              return row ? { ...row } : null;
            }
            return null;
          };
          const all = async () => {
            if (/FROM account_links WHERE primary_user_id/.test(sql)) {
              return { results: [...accountLinks.values()].filter((r) => r.primary_user_id === args[0]).map((r) => ({ alias_provider: r.alias_provider, verified_email: r.verified_email, created_at: r.created_at })) };
            }
            if (/FROM favorites/.test(sql)) {
              return { results: [...favorites].filter((k) => k.split("|")[0] === args[0]).map((k) => ({ place_id: k.split("|")[1] })) };
            }
            if (/FROM notify_rules/.test(sql)) {
              return { results: [...notifyRules.values()].filter((r) => r.user_id === args[0]).map((r) => ({ id: r.id, place_id: r.place_id, opportunity_id: r.opportunity_id, channel: r.channel, min_advance_hours: r.min_advance_hours, custom_conditions: null, enabled: 1, created_at: r.created_at })) };
            }
            return { results: [] };
          };
          return { run, first, all };
        },
      };
    },
  };

  const env = { DB: db, AUTH_SECRET: SECRET, AUTH_MOCK: "1" };
  if (opts.env) Object.assign(env, opts.env);
  return { env, users, favorites, notifyRules, feedback, pushTokens, accountLinks, linkVerifications };
}

const req = (path, opts = {}) => new Request(`https://chaselights.app/api/v1${path}`, opts);
const sessionCookies = (res) => {
  const out = [];
  res.headers.forEach((v, k) => { if (k === "set-cookie") out.push(v); });
  return out;
};
const bearer = (token) => ({ Authorization: `Bearer ${token}` });

async function mockLogin(env, { provider, user, email, name, cookie, link }) {
  const q = new URLSearchParams({ provider, user, name });
  if (email) q.set("email", email);
  if (link) q.set("link", "1");
  return worker.fetch(req(`/auth/mock/start?${q}`, { headers: cookie ? { Cookie: cookie } : {} }), env);
}

// Seed a standalone users row WITHOUT logging in (so no link resolution runs
// yet) — data can then be attached to it before the linking event.
function seedUser(users, id, provider, puid, name) {
  users.set(id, { device_id: id, provider, provider_user_id: puid, display_name: name, level: "free", verified_email: null, created_at: "2026-01-01 00:00:59" });
}

// ---------------------------------------------------------------------------
// Sign in with Apple — fail-closed contract + mocked full callback flow
// ---------------------------------------------------------------------------
const APPLE_ENV = {
  APPLE_SERVICES_ID: "com.chaselights.signin",
  APPLE_TEAM_ID: "TEAM123456",
  APPLE_KEY_ID: "KEYID999",
  APPLE_PRIVATE_KEY: null, // filled by the EC key fixture below
};

before(async () => {
  const pair = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
  const pkcs8 = new Uint8Array(await crypto.subtle.exportKey("pkcs8", pair.privateKey));
  const b64 = Buffer.from(pkcs8).toString("base64").replace(/(.{64})/g, "$1\n");
  APPLE_ENV.APPLE_PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----\n${b64}\n-----END PRIVATE KEY-----\n`;
});

let rsaPair = null;
before(async () => {
  rsaPair = await crypto.subtle.generateKey(
    { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true, ["sign", "verify"]);
});

const b64u = (buf) => Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
async function appleIdToken(claims) {
  const head = b64u(JSON.stringify({ alg: "RS256", kid: "test-key" }));
  const body = b64u(JSON.stringify(claims));
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", rsaPair.privateKey, new TextEncoder().encode(`${head}.${body}`));
  return `${head}.${body}.${b64u(new Uint8Array(sig))}`;
}
const jwkDoc = async () => {
  const jwk = await crypto.subtle.exportKey("jwk", rsaPair.publicKey);
  return { keys: [{ ...jwk, kid: "test-key", alg: "RS256" }] };
};

test("CL-APP-07: Apple entry fails closed until the owner's four secrets land; /auth/config reports it", async () => {
  const { env } = makeEnv();
  const res = await worker.fetch(req("/auth/apple/start"), env);
  assert.equal(res.status, 503);
  assert.match((await res.json()).error, /not configured/);
  const cfg = await worker.fetch(req("/auth/config"), env);
  assert.deepEqual((await cfg.json()).providers, { line: false, google: false, apple: false });
});

test("CL-APP-07: configured Apple start 302s to Apple with Services ID + response_mode=form_post", async () => {
  const { env } = makeEnv({ env: APPLE_ENV });
  const res = await worker.fetch(req("/auth/apple/start"), env);
  assert.equal(res.status, 302);
  const loc = res.headers.get("location");
  assert.ok(loc.startsWith("https://appleid.apple.com/auth/authorize?"));
  const q = new URLSearchParams(new URL(loc).search);
  assert.equal(q.get("client_id"), "com.chaselights.signin");
  assert.equal(q.get("response_mode"), "form_post");
  assert.equal(q.get("scope"), "name email");
  assert.ok(q.get("state"));
});

test("CL-APP-07: Apple callback (POST form) mints a session — id_token verified via JWKS, ES256 client_secret, email stored", async () => {
  const { env, users } = makeEnv({ env: APPLE_ENV });
  const start = await worker.fetch(req("/auth/apple/start"), env);
  const state = new URLSearchParams(new URL(start.headers.get("location")).search).get("state");
  const idToken = await appleIdToken({
    iss: "https://appleid.apple.com", aud: APPLE_ENV.APPLE_SERVICES_ID,
    sub: "apple-uid-1", email: "Mei@Example.com", email_verified: true,
    iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + 600,
  });
  const tokenRequests = [];
  const realFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    const u = String(url);
    if (u === "https://appleid.apple.com/auth/token") {
      tokenRequests.push(String(init.body));
      return { ok: true, json: async () => ({ id_token: idToken, access_token: "at" }) };
    }
    if (u === "https://appleid.apple.com/auth/keys") return { ok: true, json: jwkDoc };
    return realFetch(url, init);
  };
  try {
    const form = new URLSearchParams({ code: "auth-code-1", state });
    const cb = await worker.fetch(req("/auth/apple/callback", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    }), env);
    assert.equal(cb.status, 302);
    assert.equal(new URL(cb.headers.get("location")).pathname, "/");
    const cookies = sessionCookies(cb);
    assert.ok(cookies.some((c) => c.startsWith("cl_session=")), "HttpOnly session cookies ride the 302");
    // The token exchange used a minted ES256 client_secret JWT.
    assert.equal(tokenRequests.length, 1);
    const cs = new URLSearchParams(tokenRequests[0]).get("client_secret");
    const csHead = JSON.parse(Buffer.from(cs.split(".")[0], "base64url").toString());
    assert.equal(csHead.alg, "ES256");
    assert.equal(csHead.kid, "KEYID999");
    // /auth/me with the callback cookies answers for the Apple identity.
    const me = await worker.fetch(req("/auth/me", { headers: { Cookie: cookies.join("; ") } }), env);
    const doc = await me.json();
    assert.equal(doc.user.provider, "apple");
    assert.equal(doc.user.verifiedEmail, "mei@example.com");
    assert.ok(users.has("p:apple:apple-uid-1"));
  } finally {
    globalThis.fetch = realFetch;
  }
});

test("CL-APP-07: Apple callback with a tampered id_token never mints a session (302 auth_error)", async () => {
  const { env } = makeEnv({ env: APPLE_ENV });
  const start = await worker.fetch(req("/auth/apple/start"), env);
  const state = new URLSearchParams(new URL(start.headers.get("location")).search).get("state");
  const goodToken = await appleIdToken({ iss: "https://appleid.apple.com", aud: APPLE_ENV.APPLE_SERVICES_ID, sub: "evil", email: "e@x.com", email_verified: true, exp: Math.floor(Date.now() / 1000) + 600 });
  const [h, b] = goodToken.split(".");
  const badToken = `${h}.${b}.${b}`; // signature swapped for garbage
  const realFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    const u = String(url);
    if (u === "https://appleid.apple.com/auth/token") return { ok: true, json: async () => ({ id_token: badToken }) };
    if (u === "https://appleid.apple.com/auth/keys") return { ok: true, json: jwkDoc };
    return realFetch(url);
  };
  try {
    const form = new URLSearchParams({ code: "c", state });
    const cb = await worker.fetch(req("/auth/apple/callback", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: form.toString() }), env);
    assert.equal(cb.status, 302);
    assert.equal(new URL(cb.headers.get("location")).searchParams.get("auth_error"), "1");
    assert.ok(!sessionCookies(cb).some((c) => c.startsWith("cl_session=")), "no session without a verified identity");
  } finally { globalThis.fetch = realFetch; }
});

// ---------------------------------------------------------------------------
// Verified-email auto-link + data merge (mock provider)
// ---------------------------------------------------------------------------
test("CL-APP-07: same verified email auto-links — favorites union, reminders all kept, alias session answers as primary", async () => {
  const { env, users, favorites, notifyRules } = makeEnv();
  const g = await mockLogin(env, { provider: "google", user: "g-1", email: "mei@example.com", name: "小美" });
  const gDoc = await g.json();
  const googleId = gDoc.user.id;
  favorites.add(`${googleId}|place-a`);
  favorites.add(`${googleId}|place-shared`);
  notifyRules.set("rule-g", { id: "rule-g", user_id: googleId, place_id: "place-a", opportunity_id: null, channel: "push", min_advance_hours: 24, enabled: 1, created_at: "2026-01-01 00:00:00" });

  // Standalone Apple identity (row exists, no email yet) with its own data.
  seedUser(users, "p:apple:apple-1", "apple", "apple-1", "蘋果客");
  favorites.add("p:apple:apple-1|place-b");
  favorites.add("p:apple:apple-1|place-shared");
  notifyRules.set("rule-a", { id: "rule-a", user_id: "p:apple:apple-1", place_id: "place-b", opportunity_id: null, channel: "push", min_advance_hours: 24, enabled: 1, created_at: "2026-01-01 00:00:10" });

  // Logged-out Apple login with the same verified email → auto-link.
  const apple = await mockLogin(env, { provider: "apple", user: "apple-1", email: "Mei@Example.com", name: "蘋果客" });
  const appleDoc = await apple.json();
  assert.equal(appleDoc.user.id, googleId, "session issued for the PRIMARY identity");

  // Union: every favorite from both sides survives; shared place exactly once.
  const fav = await worker.fetch(req(`/favorites?userId=${encodeURIComponent(googleId)}`), env);
  const places = (await fav.json()).favorites.map((f) => f.place_id).sort();
  assert.deepEqual(places, ["place-a", "place-b", "place-shared"]);
  // Reminders: ALL kept.
  const rules = await worker.fetch(req("/notify/rules", { headers: bearer(gDoc.accessToken) }), env);
  assert.equal((await rules.json()).rules.length, 2);
  // The Apple session answers as the primary account.
  const me = await worker.fetch(req("/auth/me", { headers: bearer(appleDoc.accessToken) }), env);
  const meDoc = await me.json();
  assert.equal(meDoc.user.id, googleId);
  assert.equal(meDoc.user.verifiedEmail, "mei@example.com");
});

test("CL-APP-07: feedback merges to the primary; the one-rating-per-place conflict keeps the PRIMARY's vote", async () => {
  const { env, users, feedback } = makeEnv();
  const g = await mockLogin(env, { provider: "google", user: "g-2", email: "vote@example.com", name: "投票客" });
  const googleId = (await g.json()).user.id;
  seedUser(users, "p:apple:apple-2", "apple", "apple-2", "蘋果客二");
  // Votes recorded BEFORE the link: google rated place-a + place-x; apple
  // rated place-a (conflict) and place-y (no conflict).
  feedback.set("fb-g1", { id: "fb-g1", user_id: googleId, place_id: "place-a", type: "rating", status: "ok" });
  feedback.set("fb-g2", { id: "fb-g2", user_id: googleId, place_id: "place-x", type: "rating", status: "ok" });
  feedback.set("fb-a1", { id: "fb-a1", user_id: "p:apple:apple-2", place_id: "place-a", type: "rating", status: "ok" });
  feedback.set("fb-a2", { id: "fb-a2", user_id: "p:apple:apple-2", place_id: "place-y", type: "rating", status: "ok" });

  const apple = await mockLogin(env, { provider: "apple", user: "apple-2", email: "vote@example.com", name: "蘋果客二" });
  assert.equal((await apple.json()).user.id, googleId);
  const ids = [...feedback.values()].map((r) => r.user_id);
  assert.ok(ids.length > 0 && ids.every((id) => id === googleId), `all surviving feedback keyed to the primary (got ${[...feedback.keys()].join(",")})`);
  assert.ok(feedback.has("fb-a2"), "the non-conflicting alias vote moved over");
  assert.equal([...feedback.values()].filter((r) => r.place_id === "place-a").length, 1, "conflicting place-a rating: the primary's vote survives, never duplicated");
  assert.ok(!feedback.has("fb-a1"), "the conflicting alias rating did not survive the UNIQUE seat");
});

// ---------------------------------------------------------------------------
// No-email providers (LINE): member-center email verification flow
// ---------------------------------------------------------------------------
test("CL-APP-07: link email flow fails closed without a delivery channel; with the webhook it merges on verify", async () => {
  const { env, favorites, linkVerifications } = makeEnv();
  const g = await mockLogin(env, { provider: "google", user: "g-3", email: "owner@example.com", name: "站長" });
  const gDoc = await g.json();
  const googleId = gDoc.user.id;
  const line = await mockLogin(env, { provider: "line", user: "l-1", name: "LINE客" });
  const lDoc = await line.json();
  const lineId = lDoc.user.id;
  assert.notEqual(lineId, googleId);
  favorites.add(`${lineId}|place-line`); // LINE member's data from before linking

  // 1) without a mailer: honest 503, and no token/URL handed to the requester.
  const noMailer = await worker.fetch(req("/auth/link/start", {
    method: "POST", headers: { "Content-Type": "application/json", ...bearer(lDoc.accessToken) },
    body: JSON.stringify({ email: "owner@example.com" }),
  }), env);
  assert.equal(noMailer.status, 503);
  const noMailerDoc = await noMailer.json();
  assert.ok(noMailerDoc.message && noMailerDoc.message["zh-TW"]);

  // 2) with the webhook: the token is delivered to the mailbox only.
  const realFetch = globalThis.fetch;
  let mailed = null;
  globalThis.fetch = async (url, init) => {
    if (String(url) === "https://mail.example/send") { mailed = JSON.parse(init.body); return { ok: true, json: async () => ({}) }; }
    return realFetch(url, init);
  };
  try {
    env.LINK_EMAIL_WEBHOOK = "https://mail.example/send";
    const start = await worker.fetch(req("/auth/link/start", {
      method: "POST", headers: { "Content-Type": "application/json", ...bearer(lDoc.accessToken) },
      body: JSON.stringify({ email: "Owner@Example.com" }),
    }), env);
    assert.equal(start.status, 200);
    const startDoc = await start.json();
    assert.equal(startDoc.delivery, "webhook");
    assert.ok(mailed && mailed.to === "owner@example.com");
    assert.ok(!("verifyUrl" in startDoc) && !("token" in startDoc), "the verify URL never rides the API response");
    // 3) verify click (token-only credential) → merges into the matching account.
    const verify = await worker.fetch(req(`/auth/link/verify?token=${mailed.token}`), env);
    assert.equal(verify.status, 302);
    assert.equal(new URL(verify.headers.get("location")).searchParams.get("link_result"), "ok");
    assert.ok(![...linkVerifications.values()].some((r) => r.token === mailed.token), "token single-use (consumed)");
    const replay = await worker.fetch(req(`/auth/link/verify?token=${mailed.token}`), env);
    assert.equal(new URL(replay.headers.get("location")).searchParams.get("link_result"), "error", "replay fails closed");
    // 4) the LINE alias now resolves to the primary; the pre-link favorite moved.
    const status = await worker.fetch(req("/auth/link/status", { headers: bearer(lDoc.accessToken) }), env);
    const statusDoc = await status.json();
    assert.equal(statusDoc.user.id, googleId);
    assert.ok(statusDoc.links.some((l) => l.provider === "line"));
    assert.equal(statusDoc.verifiedEmail, "owner@example.com");
    const fav = await worker.fetch(req("/favorites", { headers: bearer(lDoc.accessToken) }), env);
    assert.deepEqual((await fav.json()).favorites.map((f) => f.place_id), ["place-line"]);
    void googleId;
  } finally { globalThis.fetch = realFetch; delete env.LINK_EMAIL_WEBHOOK; }
});

test("CL-APP-07: email verify with no matching account sets the linking key; the next same-email login auto-links", async () => {
  const { env, users } = makeEnv();
  const line = await mockLogin(env, { provider: "line", user: "l-2", name: "LINE客二" });
  const lDoc = await line.json();
  const realFetch = globalThis.fetch;
  let mailed = null;
  globalThis.fetch = async (url, init) => {
    if (String(url) === "https://mail.example/send") { mailed = JSON.parse(init.body); return { ok: true, json: async () => ({}) }; }
    return realFetch(url, init);
  };
  try {
    env.LINK_EMAIL_WEBHOOK = "https://mail.example/send";
    await worker.fetch(req("/auth/link/start", { method: "POST", headers: { "Content-Type": "application/json", ...bearer(lDoc.accessToken) }, body: JSON.stringify({ email: "fresh@example.com" }) }), env);
    const verify = await worker.fetch(req(`/auth/link/verify?token=${mailed.token}`), env);
    assert.equal(new URL(verify.headers.get("location")).searchParams.get("link_result"), "ok");
    assert.equal(users.get(lDoc.user.id).verified_email, "fresh@example.com");
    const apple = await mockLogin(env, { provider: "apple", user: "apple-9", email: "fresh@example.com", name: "蘋果客九" });
    assert.equal((await apple.json()).user.id, lDoc.user.id, "a later same-email provider login joins the email-verified account");
  } finally { globalThis.fetch = realFetch; delete env.LINK_EMAIL_WEBHOOK; }
});

// ---------------------------------------------------------------------------
// Explicit 連結 flow (member center, ?link=1) — works without any email
// ---------------------------------------------------------------------------
test("CL-APP-07: explicit link intent re-keys the second identity onto the signed-in account (no email needed)", async () => {
  const { env, favorites } = makeEnv();
  const g = await mockLogin(env, { provider: "google", user: "g-4", name: "主帳號" });
  const gDoc = await g.json();
  const googleId = gDoc.user.id;
  favorites.add("p:line:l-4b|place-line-old"); // data of the to-be-linked identity

  // From the member center: signed in as google, 連結 a (new) LINE identity.
  const linked = await mockLogin(env, { provider: "line", user: "l-4b", name: "新LINE", cookie: `cl_session=${gDoc.accessToken}`, link: true });
  const linkedDoc = await linked.json();
  assert.equal(linkedDoc.user.id, googleId, "session re-issued for the primary");
  assert.ok(favorites.has(`${googleId}|place-line-old`), "the linked alias's data merged into the primary");
  const status = await worker.fetch(req("/auth/link/status", { headers: bearer(gDoc.accessToken) }), env);
  const statusDoc = await status.json();
  assert.ok(statusDoc.links.some((l) => l.provider === "line"), "link status lists the linked provider");
  assert.equal(statusDoc.verifiedEmail, null, "no email was involved");
});

test("CL-APP-07: a plain (non-link) second-provider login NEVER merges into the signed-in account", async () => {
  const { env } = makeEnv();
  const g = await mockLogin(env, { provider: "google", user: "g-5", name: "主帳號五" });
  const gCookie = `cl_session=${(await g.json()).accessToken}`;
  // A family member scans the LINE QR while the google session is live — no
  // link param, so the identities must stay separate.
  const line = await mockLogin(env, { provider: "line", user: "l-5", name: "家人", cookie: gCookie });
  const lineDoc = await line.json();
  assert.match(lineDoc.user.id, /^p:line:/, "stays its own identity");
});
