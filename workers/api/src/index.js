// ChaseLights API v1 (CL-API-01 base + CL-API-02 member system).
// Results only — no thresholds/condition formulas.
const ALLOWED_ORIGIN = "https://chaselights.app";
const RATE_LIMIT = { max: 60, windowMs: 60_000 };
import {
  PROVIDERS, providerCredentials, oauthUserKey, makeTokens, getSession,
  cookieHeader, SESSION_COOKIE, REFRESH_COOKIE, authSecret, MERGE_SQL, verifyJWT,
} from "./auth.js";
import { runNotifyCron } from "./notify.js";

// CL-API-03: rule limits by member level (402 = upgrade semantics).
const NOTIFY_LIMITS = { free: 3, paid: 30 };
// CL-APP-03 (owner ruling): reminder delivery default is APP PUSH (FCM);
// telegram/web_push stay accepted for legacy rules.
const NOTIFY_CHANNELS = new Set(["push", "telegram", "web_push"]);

function corsHeaders(req) {
  const origin = req.headers.get("Origin") || "";
  return {
    "Access-Control-Allow-Origin": origin === ALLOWED_ORIGIN ? origin : "null",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Vary": "Origin",
  };
}

function json(req, status, body, extraHeaders = {}) {
  const h = new Headers({ "Content-Type": "application/json", ...corsHeaders(req) });
  for (const [k, v] of Object.entries(extraHeaders)) {
    if (Array.isArray(v)) for (const item of v) h.append(k, item); // multiple Set-Cookie
    else h.set(k, v);
  }
  return new Response(JSON.stringify(body), { status, headers: h });
}

// naive per-isolate rate limiter (enough for v1; Redis-class precision later)
const buckets = new Map();
function rateLimited(ip, now) {
  const b = buckets.get(ip) || { count: 0, start: now };
  if (now - b.start > RATE_LIMIT.windowMs) { b.count = 0; b.start = now; }
  b.count += 1;
  buckets.set(ip, b);
  return b.count > RATE_LIMIT.max;
}

async function getUser(env, userId) {
  if (!userId) return null;
  await env.DB.prepare("INSERT INTO users (device_id) VALUES (?1) ON CONFLICT(device_id) DO NOTHING")
    .bind(userId).run();
  const row = await env.DB.prepare("SELECT device_id FROM users WHERE device_id = ?1").bind(userId).first();
  return row ? row.device_id : null;
}

// CL-API-02: Authorization Bearer JWT takes precedence; legacy userId
// query/body param stays as anonymous (device) mode.
async function resolveUserId(req, env, url, body) {
  const session = await getSession(req, env);
  if (session && session.sub) return session.sub;
  const userId = url.searchParams.get("userId") || (body && body.userId);
  return getUser(env, userId);
}

async function handleFavorites(req, env, url) {
  let body = null;
  if (req.method === "POST") body = await req.json().catch(() => null);
  const uid = await resolveUserId(req, env, url, body);
  if (!uid) return json(req, req.method === "GET" ? 401 : 400, { error: "userId required (Authorization or userId)" });

  if (req.method === "GET") {
    const { results } = await env.DB.prepare(
      "SELECT place_id, created_at FROM favorites WHERE user_id = ?1 ORDER BY created_at DESC"
    ).bind(uid).all();
    return json(req, 200, { userId: uid, favorites: results });
  }

  if (req.method === "POST") {
    const placeId = body && body.placeId;
    const action = (body && body.action) || "add";
    if (!placeId) return json(req, 400, { error: "placeId required" });
    if (action === "remove") {
      await env.DB.prepare("DELETE FROM favorites WHERE user_id = ?1 AND place_id = ?2").bind(uid, placeId).run();
      return json(req, 200, { ok: true, action, placeId });
    }
    await env.DB.prepare(
      "INSERT INTO favorites (user_id, place_id) VALUES (?1, ?2) ON CONFLICT(user_id, place_id) DO NOTHING"
    ).bind(uid, placeId).run();
    return json(req, 200, { ok: true, action: "add", placeId });
  }
  return json(req, 405, { error: "method not allowed" });
}

// ---------------------------------------------------------------------------
// CL-API-02 member system
// ---------------------------------------------------------------------------

async function ensureOAuthUser(env, provider, providerUserId, displayName) {
  const deviceKey = oauthUserKey(provider, providerUserId);
  await env.DB.prepare(
    "INSERT INTO users (device_id, provider, provider_user_id, display_name, level) VALUES (?1, ?2, ?3, ?4, 'free') ON CONFLICT(device_id) DO NOTHING"
  ).bind(deviceKey, provider, providerUserId, displayName).run();
  const row = await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level FROM users WHERE device_id = ?1"
  ).bind(deviceKey).first();
  return row;
}

async function mergeAnonDevice(env, anonDeviceId, userKey) {
  if (!anonDeviceId || anonDeviceId === userKey) return 0;
  let moved = 0;
  for (const sql of [MERGE_SQL.favorites, MERGE_SQL.notify_rules]) {
    const r = await env.DB.prepare(sql).bind(userKey, anonDeviceId).run();
    moved += r && r.meta && typeof r.meta.changes === "number" ? r.meta.changes : 0;
  }
  // CL-UI-57: UPDATE OR IGNORE leaves a source row in place when the member
  // already holds the same place (PK conflict). Delete every remaining row
  // keyed to the anonymous device id so the merged data can never re-surface
  // under the device identity (logout / another account on the same browser).
  await env.DB.prepare(MERGE_SQL.favorites_cleanup).bind(anonDeviceId).run();
  await env.DB.prepare(MERGE_SQL.notify_rules_cleanup).bind(anonDeviceId).run();
  return moved;
}

// CL-API-05: token+cookie issuance is shared by the JSON path (mock/dev) and
// the browser callback path (302 back to the homepage — no bare JSON page).
async function issueSessionCookies(env, user, anonDeviceId) {
  const { access, refresh } = await makeTokens(env, user.device_id, user.display_name, user.level);
  const merged = await mergeAnonDevice(env, anonDeviceId, user.device_id);
  return {
    access, refresh, merged,
    setCookie: [
      cookieHeader(SESSION_COOKIE, access, 15 * 60),
      cookieHeader(REFRESH_COOKIE, refresh, 30 * 24 * 3600),
    ],
  };
}

async function issueSession(req, env, user, anonDeviceId) {
  const s = await issueSessionCookies(env, user, anonDeviceId);
  return json(req, 200, {
    ok: true,
    user: { id: user.device_id, provider: user.provider, providerUserId: user.provider_user_id, displayName: user.display_name, level: user.level },
    accessToken: s.access,
    mergedRows: s.merged,
  }, { "Set-Cookie": s.setCookie });
}

// CL-API-05: OAuth callbacks are top-level browser navigations, so every
// terminal outcome is a 302 — success lands on the homepage (with cookies
// attached), failure lands on the homepage with ?auth_error=1 which the shell
// (member-auth.js / web-v2 shell) turns into a trilingual retry notice. A
// fixed target was chosen over a return_to round-trip: the sign-in entry only
// exists on the homepage shells, and keeping the D1 state payload unchanged is
// the simplest, least-surprising option.
const HOME_URL = "https://chaselights.app/";
function homeRedirect(query) {
  return Response.redirect(`${HOME_URL}?${query}`, 302);
}
function authErrorRedirect() {
  return homeRedirect("auth_error=1");
}

function randomId() {
  return btoa(crypto.getRandomValues(new Uint8Array(16)).reduce((s, b) => s + String.fromCharCode(b), ""))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// ---------------------------------------------------------------------------
// CL-API-02C: OAuth state storage on D1 (was KV auth:state:* — KV free-tier
// daily put() cap was exhausted by manual re-seeds and 500ed /auth/*/start).
// KV stays evaluation-data only. Cleanup is opportunistic: every read also
// deletes rows older than 15 minutes (state TTL is 10 minutes).
// ---------------------------------------------------------------------------
async function putAuthState(env, state, obj) {
  await env.DB.prepare("INSERT INTO auth_states (state, payload) VALUES (?1, ?2)")
    .bind(state, JSON.stringify(obj)).run();
}

async function takeAuthState(env, state) {
  const cleanup = env.DB.prepare("DELETE FROM auth_states WHERE created_at < datetime('now', '-15 minutes')").bind().run();
  const row = await env.DB.prepare("SELECT payload FROM auth_states WHERE state = ?1").bind(state).first();
  await env.DB.prepare("DELETE FROM auth_states WHERE state = ?1").bind(state).run(); // single-use
  await cleanup;
  if (!row || !row.payload) return null;
  let st = null;
  try { st = JSON.parse(row.payload); } catch { return null; }
  if (typeof st.exp === "number" && Date.now() > st.exp) return null;
  return st;
}

async function handleOAuthStart(req, env, provider, url) {
  const creds = providerCredentials(env, provider);
  if (!creds) return json(req, 404, { error: "unknown provider" });
  if (!creds.id || !creds.secret) {
    // Skeleton mode: no owner credentials yet — mock path is the only way in.
    return json(req, 503, { error: `${provider} OAuth credentials not configured (owner application pending)` });
  }
  const base = url.origin + "/api/v1";
  const redirectUri = `${base}/auth/${provider}/callback`;
  const state = randomId();
  const merge = url.searchParams.get("merge") || null;
  await putAuthState(env, state, { provider, redirectUri, merge, exp: Date.now() + 600_000 });
  const q = new URLSearchParams({
    response_type: "code", client_id: creds.id, redirect_uri: redirectUri,
    state, scope: creds.provider.scope,
  });
  if (provider === "line") q.set("prompt", "consent");
  return Response.redirect(`${creds.provider.authorizeUrl}?${q}`, 302);
}

async function handleOAuthCallback(req, env, provider, url) {
  const creds = providerCredentials(env, provider);
  if (!creds) return authErrorRedirect();
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  if (!code || !state) return authErrorRedirect();

  // single-use (CSRF): read then delete immediately — a replayed state misses.
  const st = await takeAuthState(env, state);
  if (!st) return authErrorRedirect();
  if (st.provider !== provider) return authErrorRedirect();

  const tokenRes = await fetch(creds.provider.tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code", code,
      redirect_uri: st.redirectUri, client_id: creds.id, client_secret: creds.secret,
    }),
  });
  if (!tokenRes.ok) return authErrorRedirect();
  const tokens = await tokenRes.json();
  const { accessToken } = creds.provider.parseToken(tokens);

  const userRes = await fetch(creds.provider.userinfoUrl, { headers: { Authorization: `Bearer ${accessToken}` } });
  if (!userRes.ok) return authErrorRedirect();
  const profile = await userRes.json();
  const { providerUserId, displayName } = creds.provider.parseUser(profile);

  const user = await ensureOAuthUser(env, provider, providerUserId, displayName);
  // CL-API-05: success is a 302 back to the homepage with the HttpOnly session
  // cookies attached (never a bare JSON page).
  const s = await issueSessionCookies(env, user, st.merge);
  const res = homeRedirect("lang=zh-TW");
  const h = new Headers(res.headers);
  for (const c of s.setCookie) h.append("Set-Cookie", c);
  return new Response(null, { status: 302, headers: h });
}

// Local/dev mock provider: same session-issue path as real OAuth callback,
// gated behind an env flag so it can never serve in production.
async function handleMockStart(req, env, url) {
  if (env.AUTH_MOCK !== "1") return json(req, 404, { error: "not found" });
  const provider = url.searchParams.get("provider") || "line";
  if (!PROVIDERS[provider]) return json(req, 400, { error: "unknown provider" });
  const uid = url.searchParams.get("user") || "mock-user-1";
  const name = url.searchParams.get("name") || `Mock ${provider} User`;
  const merge = url.searchParams.get("merge") || null;
  const user = await ensureOAuthUser(env, provider, uid, name);
  return issueSession(req, env, user, merge);
}

async function handleAuthMe(req, env) {
  const session = await getSession(req, env);
  if (!session) return json(req, 401, { error: "unauthorized" });
  let row = await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level, profile_json FROM users WHERE device_id = ?1"
  ).bind(session.sub).first();
  if (!row) {
    // Self-heal: a validly-signed session whose users row is missing (e.g. token
    // minted outside the login flow, or row lost) re-materializes from claims.
    const provider = /^p:(line|google):/.test(session.sub) ? session.sub.split(":")[1] : "jwt";
    const puid = /^p:(line|google):/.test(session.sub) ? session.sub.split(":").slice(2).join(":") : session.sub;
    await env.DB.prepare(
      "INSERT INTO users (device_id, provider, provider_user_id, display_name, level) VALUES (?1, ?2, ?3, ?4, ?5) ON CONFLICT(device_id) DO NOTHING"
    ).bind(session.sub, provider, puid, session.name || "User", session.level || "free").run();
    row = await env.DB.prepare(
      "SELECT device_id, provider, provider_user_id, display_name, level FROM users WHERE device_id = ?1"
    ).bind(session.sub).first();
    if (!row) return json(req, 401, { error: "session user not found" });
  }
  return json(req, 200, {
    user: {
      id: row.device_id, provider: row.provider, providerUserId: row.provider_user_id,
      displayName: row.display_name, level: row.level,
      // CL-UI-57: member-editable profile fields (migration 0006 profile_json);
      // cleared (null) keys are omitted so clients only see live values.
      profile: (() => {
        try {
          const p = JSON.parse(row.profile_json || "{}");
          if (!p || typeof p !== "object" || Array.isArray(p)) return {};
          const out = {};
          for (const key of PROFILE_FIELDS) if (p[key]) out[key] = p[key];
          return out;
        } catch { return {}; }
      })(),
    },
  });
}

async function handleAuthLogout(req, env) {
  return json(req, 200, { ok: true }, {
    "Set-Cookie": [cookieHeader(SESSION_COOKIE, "", 0), cookieHeader(REFRESH_COOKIE, "", 0)],
  });
}

async function handleAuthRefresh(req, env) {
  let token = null;
  const m = (req.headers.get("Cookie") || "").match(new RegExp(`(?:^|;\\s*)${REFRESH_COOKIE}=([^;]+)`));
  if (m) token = m[1];
  const body = await req.json().catch(() => null);
  if (!token && body && body.refreshToken) token = body.refreshToken;
  const payload = token ? await verifyJWT(token, authSecret(env)) : null;
  if (!payload || payload.typ !== "refresh") return json(req, 401, { error: "invalid refresh token" });
  const row = await env.DB.prepare("SELECT device_id, display_name, level FROM users WHERE device_id = ?1").bind(payload.sub).first();
  if (!row) return json(req, 401, { error: "user not found" });
  const { access, refresh } = await makeTokens(env, row.device_id, row.display_name, row.level);
  return json(req, 200, { ok: true, accessToken: access, refreshToken: refresh }, {
    "Set-Cookie": [cookieHeader(SESSION_COOKIE, access, 15 * 60), cookieHeader(REFRESH_COOKIE, refresh, 30 * 24 * 3600)],
  });
}

// ---------------------------------------------------------------------------
// CL-UI-57: member profile editing (PATCH /auth/profile, session-only).
// display_name is the member's editable nickname; the optional free-form
// profile fields (experience / region / bio, all non-required) live in
// users.profile_json (migration 0006).
// ---------------------------------------------------------------------------
const PROFILE_FIELDS = ["experience", "region", "bio"];
const PROFILE_MAX_LEN = 200;

function sanitizeProfile(raw) {
  const out = {};
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return out;
  for (const key of PROFILE_FIELDS) {
    const v = raw[key];
    if (typeof v !== "string") continue;
    const trimmed = v.trim();
    if (trimmed) out[key] = trimmed.slice(0, PROFILE_MAX_LEN);
  }
  return out;
}

async function handleAuthProfile(req, env) {
  const session = await getSession(req, env);
  if (!session || !session.sub) return json(req, 401, { error: "unauthorized" });
  const body = await req.json().catch(() => null);
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return json(req, 400, { error: "body required" });
  }

  const row = await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level, profile_json FROM users WHERE device_id = ?1"
  ).bind(session.sub).first();
  if (!row) return json(req, 401, { error: "session user not found" });

  let displayName = row.display_name;
  if (body.displayName !== undefined) {
    if (typeof body.displayName !== "string") return json(req, 400, { error: "displayName must be a string" });
    const trimmed = body.displayName.trim();
    if (!trimmed || trimmed.length > 100) return json(req, 400, { error: "displayName must be 1-100 characters" });
    displayName = trimmed;
  }

  // profile_json merges over the stored object; omitted keys keep their value,
  // an empty string clears the field.
  let profile = {};
  try { const prev = JSON.parse(row.profile_json || "{}"); if (prev && typeof prev === "object") profile = prev; } catch { profile = {}; }
  const next = sanitizeProfile(body.profile);
  for (const key of PROFILE_FIELDS) {
    if (body.profile && typeof body.profile === "object" && !Array.isArray(body.profile) && body.profile[key] !== undefined) {
      profile[key] = next[key] || null;
    }
  }
  const profileJson = JSON.stringify(profile);

  // Response omits cleared (null) keys so the client sees only live fields.
  const publicProfile = {};
  for (const key of PROFILE_FIELDS) if (profile[key]) publicProfile[key] = profile[key];

  await env.DB.prepare(
    "UPDATE users SET display_name = ?1, profile_json = ?2 WHERE device_id = ?3"
  ).bind(displayName, profileJson, session.sub).run();

  return json(req, 200, {
    ok: true,
    user: { id: row.device_id, provider: row.provider, providerUserId: row.provider_user_id, displayName, level: row.level, profile: publicProfile },
  });
}

// ---------------------------------------------------------------------------
// CL-API-03 notification engine — rules, Telegram binding, web-push skeleton
// ---------------------------------------------------------------------------

// Rules endpoints are JWT-only (no legacy anonymous fallback).
async function requireSession(req, env) {
  const session = await getSession(req, env);
  if (!session || !session.sub) return null;
  return session;
}

async function userLevel(env, sub, fallback) {
  const row = await env.DB.prepare("SELECT level FROM users WHERE device_id = ?1").bind(sub).first();
  return (row && row.level) || fallback || "free";
}

async function handleNotifyRules(req, env) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const level = await userLevel(env, uid, session.level);

  if (req.method === "GET") {
    const { results } = await env.DB.prepare(
      "SELECT id, place_id, opportunity_id, channel, min_advance_hours, enabled, created_at FROM notify_rules WHERE user_id = ?1 ORDER BY created_at DESC"
    ).bind(uid).all();
    return json(req, 200, { userId: uid, level, rules: results || [] });
  }

  if (req.method === "POST") {
    const body = await req.json().catch(() => null);
    const placeId = (body && (body.placeId || body.place_id)) || null;
    if (!placeId) return json(req, 400, { error: "placeId required" });
    const opportunityId = (body && (body.opportunityId || body.opportunity_id)) || null;
    const channel = (body && body.channel) || "push";
    if (!NOTIFY_CHANNELS.has(channel)) return json(req, 400, { error: "channel must be push, telegram or web_push" });
    let advance = body && body.minAdvanceHours != null ? Number(body.minAdvanceHours) : 24;
    if (!Number.isFinite(advance) || advance < 0 || advance > 72) return json(req, 400, { error: "minAdvanceHours must be 0..72" });
    advance = Math.round(advance);

    const limit = NOTIFY_LIMITS[level] || NOTIFY_LIMITS.free;
    const row = await env.DB.prepare("SELECT COUNT(*) AS n FROM notify_rules WHERE user_id = ?1").bind(uid).first();
    const count = row ? row.n : 0;
    if (count >= limit) {
      return json(req, 402, { error: "notify rule limit reached — upgrade to paid for more", level, limit, count });
    }

    const id = btoa(crypto.getRandomValues(new Uint8Array(12)).reduce((s, b) => s + String.fromCharCode(b), ""))
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    await env.DB.prepare(
      "INSERT INTO notify_rules (id, user_id, place_id, opportunity_id, channel, min_advance_hours) VALUES (?1, ?2, ?3, ?4, ?5, ?6)"
    ).bind(id, uid, placeId, opportunityId, channel, advance).run();
    return json(req, 200, { ok: true, rule: { id, placeId, opportunityId, channel, minAdvanceHours: advance }, count: count + 1, limit });
  }
  return json(req, 405, { error: "method not allowed" });
}

async function handleNotifyRuleDelete(req, env, ruleId) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const r = await env.DB.prepare("DELETE FROM notify_rules WHERE id = ?1 AND user_id = ?2").bind(ruleId, session.sub).run();
  const changed = r && r.meta && typeof r.meta.changes === "number" ? r.meta.changes : 0;
  if (!changed) return json(req, 404, { error: "rule not found" });
  return json(req, 200, { ok: true, deleted: ruleId });
}

// CL-UI-58: the reminders page needs an enabled toggle; PATCH (and PUT for
// client convenience) flips it. Scope is deliberately narrow — no other field
// is editable; everything else still goes through DELETE + POST recreate.
async function handleNotifyRuleUpdate(req, env, ruleId) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const body = await req.json().catch(() => null);
  const enabled = body && body.enabled;
  if (typeof enabled !== "boolean") return json(req, 400, { error: "enabled boolean required" });
  const r = await env.DB.prepare("UPDATE notify_rules SET enabled = ?2 WHERE id = ?1 AND user_id = ?3")
    .bind(ruleId, enabled ? 1 : 0, session.sub).run();
  const changed = r && r.meta && typeof r.meta.changes === "number" ? r.meta.changes : 0;
  if (!changed) return json(req, 404, { error: "rule not found" });
  return json(req, 200, { ok: true, rule: { id: ruleId, enabled } });
}

async function handleTelegramStart(req, env) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const token = btoa(crypto.getRandomValues(new Uint8Array(12)).reduce((s, b) => s + String.fromCharCode(b), ""))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  await env.DB.prepare(
    "INSERT INTO telegram_bindings (user_id, status, token) VALUES (?1, 'pending', ?2) ON CONFLICT(user_id) DO UPDATE SET status = 'pending', token = ?2"
  ).bind(session.sub, token).run();
  const bot = env.TG_BOT_USERNAME || "chaselights_cm_bot";
  return json(req, 200, {
    ok: true,
    bot: `@${bot}`,
    link: `https://t.me/${bot}?start=${token}`,
    note: "open the link and press Start in Telegram; binding completes on the next engine poll (up to 30 min, or the next scheduled run)",
  });
}

async function handleTelegramStatus(req, env) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const row = await env.DB.prepare("SELECT status, chat_id FROM telegram_bindings WHERE user_id = ?1").bind(session.sub).first();
  return json(req, 200, { status: (row && row.status) || "none", chatId: (row && row.chat_id) || null });
}

// ---------------------------------------------------------------------------
// CL-APP-03: FCM device push tokens (APP push base).
// POST   /push_tokens  — register/refresh a device token. Auth: Bearer JWT
//   session (member) OR anonymous body deviceId (device-id mode, same scheme
//   as favorites). DELETE unregisters by token.
// ---------------------------------------------------------------------------
async function handlePushTokenRegister(req, env) {
  const body = await req.json().catch(() => null);
  if (!body || typeof body !== "object") return json(req, 400, { error: "body required" });
  const token = typeof body.token === "string" ? body.token.trim() : "";
  if (!token || token.length > 4096) return json(req, 400, { error: "token required" });
  const platform = typeof body.platform === "string" && body.platform.trim() ? body.platform.trim().slice(0, 64) : "android/fcm";

  let uid = null;
  const session = await getSession(req, env);
  if (session && session.sub) uid = session.sub;
  else {
    const deviceId = typeof body.deviceId === "string" ? body.deviceId.trim() : "";
    if (!deviceId || deviceId.length > 200) return json(req, 400, { error: "Authorization session or deviceId required" });
    uid = await getUser(env, deviceId);
    if (!uid) return json(req, 400, { error: "deviceId required" });
  }

  await env.DB.prepare(
    "INSERT INTO push_tokens (user_device_id, platform, token, updated_at) VALUES (?1, ?2, ?3, datetime('now')) " +
    "ON CONFLICT(token) DO UPDATE SET user_device_id = ?1, platform = ?2, updated_at = datetime('now')"
  ).bind(uid, platform, token).run();
  return json(req, 200, { ok: true, platform, deviceId: uid });
}

async function handlePushTokenDelete(req, env) {
  const body = await req.json().catch(() => null);
  const token = body && typeof body.token === "string" ? body.token.trim() : "";
  if (!token) return json(req, 400, { error: "token required" });
  const r = await env.DB.prepare("DELETE FROM push_tokens WHERE token = ?1").bind(token).run();
  const changed = r && r.meta && typeof r.meta.changes === "number" ? r.meta.changes : 0;
  if (!changed) return json(req, 404, { error: "token not found" });
  return json(req, 200, { ok: true });
}

async function handleWebPushSubscribe(req, env) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const body = await req.json().catch(() => null);
  const endpoint = body && body.endpoint;
  const keys = (body && body.keys) || {};
  if (!endpoint || !keys.p256dh || !keys.auth) return json(req, 400, { error: "endpoint and keys.p256dh/keys.auth required" });
  await env.DB.prepare(
    "INSERT INTO web_push_subscriptions (user_id, endpoint, p256dh, auth) VALUES (?1, ?2, ?3, ?4) ON CONFLICT(endpoint) DO UPDATE SET user_id = ?1, p256dh = ?3, auth = ?4"
  ).bind(session.sub, endpoint, keys.p256dh, keys.auth).run();
  return json(req, 200, { ok: true, delivery: "skeleton — VAPID delivery ships in a follow-up ticket" });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/^\/api\/v1/, "");

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(request) });

    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    if (rateLimited(ip, Date.now())) return json(request, 429, { error: "rate limited" });

    if (path === "/health") {
      return json(request, 200, { ok: true, service: "chaselights-api", version: "v2-auth", time: new Date().toISOString() });
    }

    if (path === "/evaluations" && request.method === "GET") {
      const placeId = url.searchParams.get("place_id");
      if (placeId) {
        const rec = await env.EVALS.get(`v1:evals:${placeId}`, "json");
        if (!rec) return json(request, 404, { error: "place not evaluated", placeId });
        return json(request, 200, rec);
      }
      const index = await env.EVALS.get("v1:evals:index", "json");
      if (!index) return json(request, 503, { error: "evaluations not synced yet" });
      return json(request, 200, index);
    }

    if (path === "/favorites") return handleFavorites(request, env, url);

    // --- notify engine (CL-API-03, JWT-only) ---
    if (path === "/notify/rules") return handleNotifyRules(request, env);
    {
      const dm = path.match(/^\/notify\/rules\/([\w-]+)$/);
      if (dm && request.method === "DELETE") return handleNotifyRuleDelete(request, env, dm[1]);
      if (dm && (request.method === "PATCH" || request.method === "PUT")) return handleNotifyRuleUpdate(request, env, dm[1]);
    }
    if (path === "/notify/telegram/start" && request.method === "POST") return handleTelegramStart(request, env);
    if (path === "/notify/telegram/status" && request.method === "GET") return handleTelegramStatus(request, env);
    if (path === "/notify/web_push/subscribe" && request.method === "POST") return handleWebPushSubscribe(request, env);
    if (path === "/push_tokens" && request.method === "POST") return handlePushTokenRegister(request, env);
    if (path === "/push_tokens" && request.method === "DELETE") return handlePushTokenDelete(request, env);

    // --- auth (CL-API-02) ---
    let m;
    if ((m = path.match(/^\/auth\/(line|google)\/start$/))) {
      if (request.method !== "GET") return json(request, 405, { error: "method not allowed" });
      return handleOAuthStart(request, env, m[1], url);
    }
    if ((m = path.match(/^\/auth\/(line|google)\/callback$/))) {
      if (request.method !== "GET") return json(request, 405, { error: "method not allowed" });
      return handleOAuthCallback(request, env, m[1], url);
    }
    if (path === "/auth/mock/start") return handleMockStart(request, env, url);
    if (path === "/auth/me" && request.method === "GET") return handleAuthMe(request, env);
    if (path === "/auth/profile" && request.method === "PATCH") return handleAuthProfile(request, env);
    if (path === "/auth/logout" && request.method === "POST") return handleAuthLogout(request, env);
    if (path === "/auth/refresh" && request.method === "POST") return handleAuthRefresh(request, env);

    return json(request, 404, { error: "not found" });
  },

  // CL-API-03: every 30 min (wrangler.toml [triggers]) — bind Telegram chats,
  // match enabled rules against the next-24h distilled windows, deliver once
  // per rule+window (notify_log PK dedupe).
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runNotifyCron(env).then((s) => console.log("[notify-cron]", JSON.stringify(s))).catch((e) => console.error("[notify-cron]", e && e.message)));
  },
};
