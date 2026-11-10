// ChaseLights API v1 (CL-API-01 base + CL-API-02 member system).
// Results only — no thresholds/condition formulas.
const ALLOWED_ORIGIN = "https://chaselights.app";
const RATE_LIMIT = { max: 60, windowMs: 60_000 };
import {
  PROVIDERS, providerCredentials, oauthUserKey, makeTokens, getSession,
  cookieHeader, SESSION_COOKIE, REFRESH_COOKIE, authSecret, MERGE_SQL, verifyJWT,
} from "./auth.js";

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
  return moved;
}

async function issueSession(req, env, user, anonDeviceId) {
  const { access, refresh } = await makeTokens(env, user.device_id, user.display_name, user.level);
  const merged = await mergeAnonDevice(env, anonDeviceId, user.device_id);
  return json(req, 200, {
    ok: true,
    user: { id: user.device_id, provider: user.provider, providerUserId: user.provider_user_id, displayName: user.display_name, level: user.level },
    accessToken: access,
    mergedRows: merged,
  }, {
    "Set-Cookie": [
      cookieHeader(SESSION_COOKIE, access, 15 * 60),
      cookieHeader(REFRESH_COOKIE, refresh, 30 * 24 * 3600),
    ],
  });
}

function randomId() {
  return btoa(crypto.getRandomValues(new Uint8Array(16)).reduce((s, b) => s + String.fromCharCode(b), ""))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
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
  await env.EVALS.put(`auth:state:${state}`, JSON.stringify({ provider, redirectUri, merge, exp: Date.now() + 600_000 }), { expirationTtl: 600 });
  const q = new URLSearchParams({
    response_type: "code", client_id: creds.id, redirect_uri: redirectUri,
    state, scope: creds.provider.scope,
  });
  if (provider === "line") q.set("prompt", "consent");
  return Response.redirect(`${creds.provider.authorizeUrl}?${q}`, 302);
}

async function handleOAuthCallback(req, env, provider, url) {
  const creds = providerCredentials(env, provider);
  if (!creds) return json(req, 404, { error: "unknown provider" });
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  if (!code || !state) return json(req, 400, { error: "code and state required" });

  const stateJson = await env.EVALS.get(`auth:state:${state}`);
  await env.EVALS.delete(`auth:state:${state}`); // single-use (CSRF)
  if (!stateJson) return json(req, 400, { error: "invalid or expired state" });
  const st = JSON.parse(stateJson);
  if (st.provider !== provider) return json(req, 400, { error: "state provider mismatch" });

  const tokenRes = await fetch(creds.provider.tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code", code,
      redirect_uri: st.redirectUri, client_id: creds.id, client_secret: creds.secret,
    }),
  });
  if (!tokenRes.ok) return json(req, 502, { error: "provider token exchange failed", status: tokenRes.status });
  const tokens = await tokenRes.json();
  const { accessToken } = creds.provider.parseToken(tokens);

  const userRes = await fetch(creds.provider.userinfoUrl, { headers: { Authorization: `Bearer ${accessToken}` } });
  if (!userRes.ok) return json(req, 502, { error: "provider userinfo failed", status: userRes.status });
  const profile = await userRes.json();
  const { providerUserId, displayName } = creds.provider.parseUser(profile);

  const user = await ensureOAuthUser(env, provider, providerUserId, displayName);
  return issueSession(req, env, user, st.merge);
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
  const row = await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level FROM users WHERE device_id = ?1"
  ).bind(session.sub).first();
  if (!row) return json(req, 401, { error: "session user not found" });
  return json(req, 200, {
    user: { id: row.device_id, provider: row.provider, providerUserId: row.provider_user_id, displayName: row.display_name, level: row.level },
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
    if (path === "/auth/logout" && request.method === "POST") return handleAuthLogout(request, env);
    if (path === "/auth/refresh" && request.method === "POST") return handleAuthRefresh(request, env);

    return json(request, 404, { error: "not found" });
  },
};
