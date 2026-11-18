// ChaseLights API v1 (CL-API-01 base + CL-API-02 member system).
// Results only — no thresholds/condition formulas.
const ALLOWED_ORIGIN = "https://chaselights.app";
// CL-API-07: class-based per-IP limits. A single 60/min bucket 429'd the
// cheap read endpoints (1×/auth/me + 6×/favorites per page load) after a few
// owner page switches, and the clients misread 429 as signed-out. Reads are
// lenient (D1/KV reads are cheap); OAuth callbacks and token endpoints stay
// strict; everything else keeps the original default.
const RATE_LIMITS = {
  read: { max: 600, windowMs: 60_000 },
  auth: { max: 20, windowMs: 60_000 },
  write: { max: 60, windowMs: 60_000 },
};
function rateClass(path, method) {
  if (
    method === "GET" &&
    /^\/(auth\/me$|auth\/config$|auth\/link\/status$|favorites$|notify\/rules$|evaluations$|catalog\/digests$|health$|feedback$|feedback\/config$|admin\/feedback$|custom_places$|conditions\/parse$)/.test(path)
  ) return "read";
  if (/^\/auth\/(line|google|apple)\/callback$|^\/auth\/mock\/start$|^\/auth\/refresh$/.test(path)) return "auth";
  return "write";
}
import {
  PROVIDERS, providerCredentials, providerConfigured, oauthUserKey, makeTokens, getSession,
  cookieHeader, SESSION_COOKIE, REFRESH_COOKIE, authSecret, MERGE_SQL, verifyJWT,
  appleClientSecret, verifyAppleIdToken, resolvePrimaryDeviceId,
} from "./auth.js";
import { runNotifyCron, validateCustomConditions, parseCustomConditions } from "./notify.js";
import {
  handleFeedback, handleFeedbackSubmit, handleFeedbackDelete,
  handleAdminFeedbackList, handleAdminFeedbackReview, feedbackEnabled,
} from "./feedback.js";
// CL-APP-06: custom places (private points) — CRUD + nomination + low-priority fetch queue.
import {
  handleCustomPlaces, handleCustomPlaceItem, handleCustomPlaceNominate,
  handleCustomPlaceEval, handleCustomPlaceThemes, handleCustomPlaceThemeItem,
  handleCustomPlacePinInfo, processCustomFetchQueue,
  handleConditionsParse, handleConditionsParseConfig,
} from "./custom-places.js";

// CL-API-03: rule limits by member level (402 = upgrade semantics).
// CL-DATA-70 owner ruling (Stage 1): grading column users.member_level
// (free/paid/owner) drives the reminder cap — free 3 / paid 20 / owner
// unlimited. Until billing is live a KV flag (same style as the feedback
// gray flag) treats every free member as paid for testing.
const NOTIFY_RULE_CAPS = { free: 3, paid: 20 };
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
// CL-API-07: one bucket per (class, ip) so a read burst can never consume the
// strict auth-write budget, and vice versa.
const buckets = new Map();
function rateLimited(ip, path, method, now) {
  const cls = rateClass(path, method);
  const lim = RATE_LIMITS[cls];
  const key = cls + ":" + ip;
  const b = buckets.get(key) || { count: 0, start: now };
  if (now - b.start > lim.windowMs) { b.count = 0; b.start = now; }
  b.count += 1;
  buckets.set(key, b);
  return b.count > lim.max;
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
  if (session && session.sub) return resolvePrimaryDeviceId(env, session.sub);
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

async function ensureOAuthUser(env, provider, providerUserId, displayName, verifiedEmail = null) {
  const deviceKey = oauthUserKey(provider, providerUserId);
  // CL-API-06: DO NOTHING left provider/display_name NULL forever on rows
  // created by the legacy insert. Backfill NULL/empty fields on conflict, but
  // never overwrite a name the user edited via /auth/profile.
  // CL-APP-07: a provider-verified email is stored on first sight (auto-link
  // key); an already-stored verified_email is never overwritten.
  await env.DB.prepare(
    `INSERT INTO users (device_id, provider, provider_user_id, display_name, level, verified_email) VALUES (?1, ?2, ?3, ?4, 'free', ?5)
     ON CONFLICT(device_id) DO UPDATE SET
       provider = excluded.provider,
       provider_user_id = excluded.provider_user_id,
       display_name = CASE WHEN users.display_name IS NULL OR users.display_name = '' THEN excluded.display_name ELSE users.display_name END,
       verified_email = CASE WHEN (users.verified_email IS NULL OR users.verified_email = '') THEN excluded.verified_email ELSE users.verified_email END`
  ).bind(deviceKey, provider, providerUserId, displayName, verifiedEmail).run();
  const row = await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level, verified_email FROM users WHERE device_id = ?1"
  ).bind(deviceKey).first();
  return row;
}

// ---------------------------------------------------------------------------
// CL-APP-07: account linking. All member data keys on users.device_id, so an
// alias identity is re-keyed onto the PRIMARY user's device_id and every
// ownership table (favorites/notify_rules/feedback/custom_places/push_tokens)
// moves with it. Conflict policy (owner ruling): favorites = union (UPDATE OR
// IGNORE + leftover cleanup), reminders = ALL kept (notify_rules has no unique
// constraint on user content), feedback = one-rating-per-(user,place) keeps the
// PRIMARY's vote (the conflicting alias row cannot survive the UNIQUE index —
// reported honestly, never silently duplicated).
// ---------------------------------------------------------------------------
const LINK_MERGE_STEPS = [
  // [merge SQL, cleanup SQL, may-be-missing-table] — custom_places arrives with
  // CL-APP-06; until that migration exists the step is skipped, not fatal.
  { sql: "UPDATE OR IGNORE favorites SET user_id = ?1 WHERE user_id = ?2", cleanup: "DELETE FROM favorites WHERE user_id = ?1" },
  { sql: "UPDATE notify_rules SET user_id = ?1 WHERE user_id = ?2", cleanup: null }, // PK is a random id: no conflicts, all kept
  { sql: "UPDATE OR IGNORE feedback SET user_id = ?1 WHERE user_id = ?2", cleanup: "DELETE FROM feedback WHERE user_id = ?1" },
  { sql: "UPDATE OR IGNORE custom_places SET user_id = ?1 WHERE user_id = ?2", cleanup: "DELETE FROM custom_places WHERE user_id = ?1", optional: true },
  { sql: "UPDATE OR IGNORE push_tokens SET user_device_id = ?1 WHERE user_device_id = ?2", cleanup: null },
];

async function mergeAliasDataIntoPrimary(env, aliasId, primaryId) {
  let moved = 0;
  for (const step of LINK_MERGE_STEPS) {
    try {
      const r = await env.DB.prepare(step.sql).bind(primaryId, aliasId).run();
      moved += r && r.meta && typeof r.meta.changes === "number" ? r.meta.changes : 0;
      if (step.cleanup) await env.DB.prepare(step.cleanup).bind(aliasId).run();
    } catch (e) {
      if (step.optional) continue; // table not migrated yet (CL-APP-06)
      throw e;
    }
  }
  return moved;
}

export function normalizeEmail(email) {
  return typeof email === "string" ? email.trim().toLowerCase() : "";
}

async function getPrimaryRow(env, deviceKey) {
  const link = await env.DB.prepare(
    "SELECT primary_user_id FROM account_links WHERE alias_device_id = ?1"
  ).bind(deviceKey).first();
  if (!link || !link.primary_user_id || link.primary_user_id === deviceKey) return null;
  return await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level, verified_email FROM users WHERE device_id = ?1"
  ).bind(link.primary_user_id).first() || null;
}

async function linkAliasToPrimary(env, aliasRow, primaryRow, email) {
  if (!aliasRow || !primaryRow || aliasRow.device_id === primaryRow.device_id) return null;
  // Chains stay flat by construction: an alias always resolves to its primary
  // first, so reaching here means the row is still standalone.
  await env.DB.prepare(
    "INSERT INTO account_links (alias_device_id, primary_user_id, alias_provider, alias_provider_user_id, verified_email) VALUES (?1, ?2, ?3, ?4, ?5) ON CONFLICT(alias_device_id) DO NOTHING"
  ).bind(aliasRow.device_id, primaryRow.device_id, aliasRow.provider, aliasRow.provider_user_id, email || null).run();
  await mergeAliasDataIntoPrimary(env, aliasRow.device_id, primaryRow.device_id);
  return primaryRow;
}

// Resolve the row a login actually issues the session for. Three paths:
//  (a) the identity is already linked → its primary;
//  (b) explicit 連結 intent (member-center flow, `link=1` start param): the
//      CURRENT session user becomes the primary — explicit beats email;
//  (c) auto-link: the login carried a provider-verified email matching another
//      account's verified email → linked to that (older) account.
async function resolveLoginUser(env, candidateRow, { linkToSessionDeviceId = null } = {}) {
  let row = candidateRow;
  const existingPrimary = await getPrimaryRow(env, row.device_id);
  if (existingPrimary) row = existingPrimary;

  if (linkToSessionDeviceId && linkToSessionDeviceId !== row.device_id) {
    const primary = await env.DB.prepare(
      "SELECT device_id, provider, provider_user_id, display_name, level, verified_email FROM users WHERE device_id = ?1"
    ).bind(linkToSessionDeviceId).first();
    if (primary) {
      // The session user may itself be an alias — resolve to the real primary.
      const realPrimary = (await getPrimaryRow(env, primary.device_id)) || primary;
      const linked = await linkAliasToPrimary(env, row, realPrimary, row.verified_email);
      if (linked) return linked;
    }
  } else {
    const email = normalizeEmail(row.verified_email);
    if (email) {
      const other = await env.DB.prepare(
        "SELECT device_id FROM users WHERE verified_email = ?1 AND device_id != ?2 ORDER BY created_at ASC LIMIT 1"
      ).bind(email, row.device_id).first();
      if (other && other.device_id) {
        const primary = (await getPrimaryRow(env, other.device_id)) ||
          await env.DB.prepare(
            "SELECT device_id, provider, provider_user_id, display_name, level, verified_email FROM users WHERE device_id = ?1"
          ).bind(other.device_id).first();
        const linked = await linkAliasToPrimary(env, row, primary, email);
        if (linked) return linked;
      }
    }
  }
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
  // CL-APP-07: fail-closed — Apple needs FOUR owner-supplied secrets (Services
  // ID / team ID / key ID / .p8 key); until they land the start endpoint says
  // so honestly (503) and the shells keep the entry hidden.
  if (!providerConfigured(env, provider)) {
    return json(req, 503, { error: `${provider} OAuth credentials not configured (owner application pending)` });
  }
  const base = url.origin + "/api/v1";
  const redirectUri = `${base}/auth/${provider}/callback`;
  const state = randomId();
  const merge = url.searchParams.get("merge") || null;
  // CL-APP-07: `link=1` marks the 連結其他登入方式 flow — at callback the
  // current session user becomes the link's primary (explicit link beats
  // email auto-link). Plain login buttons never carry it, so a family
  // member's QR scan can never silently merge into the signed-in account.
  const link = url.searchParams.get("link") === "1" ? true : null;
  await putAuthState(env, state, { provider, redirectUri, merge, link, exp: Date.now() + 600_000 });
  const q = new URLSearchParams({
    response_type: "code", client_id: creds.id, redirect_uri: redirectUri,
    state, scope: creds.provider.scope,
  });
  if (provider === "line") q.set("prompt", "consent");
  // Apple requires the code via form_post (name/email scope can't use query).
  if (provider === "apple") q.set("response_mode", "form_post");
  return Response.redirect(`${creds.provider.authorizeUrl}?${q}`, 302);
}

// CL-APP-07: exchange the authorization code for an identity. LINE/Google use
// the userinfo endpoint; Apple has none — the identity comes from the RS256
// id_token verified against Apple's JWKS, and the client_secret is an ES256
// JWT minted from the owner's .p8 key.
async function fetchOAuthIdentity(env, creds, provider, code, st) {
  const clientSecret = provider === "apple" ? await appleClientSecret(env) : creds.secret;
  const tokenRes = await fetch(creds.provider.tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code", code,
      redirect_uri: st.redirectUri, client_id: creds.id, client_secret: clientSecret,
    }),
  });
  if (!tokenRes.ok) return null;
  const tokens = await tokenRes.json();
  if (provider === "apple") {
    const claims = await verifyAppleIdToken(env, tokens.id_token);
    if (!claims) return null;
    const parsed = creds.provider.parseUser(claims);
    if (!parsed || !parsed.providerUserId) return null;
    return parsed;
  }
  const { accessToken } = creds.provider.parseToken(tokens);
  if (!accessToken) return null;
  const userRes = await fetch(creds.provider.userinfoUrl, { headers: { Authorization: `Bearer ${accessToken}` } });
  if (!userRes.ok) return null;
  const profile = await userRes.json();
  const parsed = creds.provider.parseUser(profile);
  if (!parsed || !parsed.providerUserId) return null;
  return parsed;
}

async function handleOAuthCallback(req, env, provider, url) {
  const creds = providerCredentials(env, provider);
  if (!creds) return authErrorRedirect();
  // Apple posts the code (response_mode=form_post); LINE/Google answer with a
  // query-string GET. Accept both shapes so one handler serves every provider.
  let code = url.searchParams.get("code");
  let state = url.searchParams.get("state");
  if (provider === "apple" && (!code || !state) && (req.method === "POST")) {
    try {
      const form = await req.formData();
      code = code || form.get("code");
      state = state || form.get("state");
    } catch { /* malformed POST body → auth_error below */ }
  }
  if (!code || !state) return authErrorRedirect();

  // single-use (CSRF): read then delete immediately — a replayed state misses.
  const st = await takeAuthState(env, state);
  if (!st) return authErrorRedirect();
  if (st.provider !== provider) return authErrorRedirect();

  const identity = await fetchOAuthIdentity(env, creds, provider, code, st);
  if (!identity) return authErrorRedirect();

  const user = await ensureOAuthUser(
    env, provider, identity.providerUserId, identity.displayName,
    identity.emailVerified ? normalizeEmail(identity.email) : null,
  );
  // CL-APP-07: resolve the link — explicit member-center intent, then email
  // auto-link, then the identity itself (see resolveLoginUser).
  const session = await getSession(req, env);
  const linkTo = st.link && session && session.sub ? session.sub : null;
  const resolved = await resolveLoginUser(env, user, { linkToSessionDeviceId: linkTo });
  // CL-API-05: success is a 302 back to the homepage with the HttpOnly session
  // cookies attached (never a bare JSON page).
  const s = await issueSessionCookies(env, resolved, st.merge);
  const res = homeRedirect("lang=zh-TW");
  const h = new Headers(res.headers);
  for (const c of s.setCookie) h.append("Set-Cookie", c);
  return new Response(null, { status: 302, headers: h });
}

// Local/dev mock provider: same session-issue + link-resolution path as the
// real OAuth callback, gated behind an env flag so it can never serve in
// production. `email=` simulates a provider-verified email, `link=1` the
// member-center link flow (needs the session cookie of the primary account).
async function handleMockStart(req, env, url) {
  if (env.AUTH_MOCK !== "1") return json(req, 404, { error: "not found" });
  const provider = url.searchParams.get("provider") || "line";
  if (!PROVIDERS[provider]) return json(req, 400, { error: "unknown provider" });
  const uid = url.searchParams.get("user") || "mock-user-1";
  const name = url.searchParams.get("name") || `Mock ${provider} User`;
  const email = normalizeEmail(url.searchParams.get("email") || "");
  const merge = url.searchParams.get("merge") || null;
  const user = await ensureOAuthUser(env, provider, uid, name, email || null);
  const session = await getSession(req, env);
  const linkTo = url.searchParams.get("link") === "1" && session && session.sub ? session.sub : null;
  const resolved = await resolveLoginUser(env, user, { linkToSessionDeviceId: linkTo });
  return issueSession(req, env, resolved, merge);
}

async function handleAuthMe(req, env) {
  const session = await getSession(req, env);
  if (!session) return json(req, 401, { error: "unauthorized" });
  let row = await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level, profile_json, verified_email FROM users WHERE device_id = ?1"
  ).bind(session.sub).first();
  if (!row) {
    // Self-heal: a validly-signed session whose users row is missing (e.g. token
    // minted outside the login flow, or row lost) re-materializes from claims.
    const provider = /^p:(line|google|apple):/.test(session.sub) ? session.sub.split(":")[1] : "jwt";
    const puid = /^p:(line|google|apple):/.test(session.sub) ? session.sub.split(":").slice(2).join(":") : session.sub;
    await env.DB.prepare(
      "INSERT INTO users (device_id, provider, provider_user_id, display_name, level) VALUES (?1, ?2, ?3, ?4, ?5) ON CONFLICT(device_id) DO NOTHING"
    ).bind(session.sub, provider, puid, session.name || "User", session.level || "free").run();
    row = await env.DB.prepare(
      "SELECT device_id, provider, provider_user_id, display_name, level, verified_email FROM users WHERE device_id = ?1"
    ).bind(session.sub).first();
    if (!row) return json(req, 401, { error: "session user not found" });
  }
  // CL-APP-07: an alias identity's data lives under its PRIMARY device_id —
  // /auth/me answers for the primary so the session the member actually uses
  // never points at a dormant alias row.
  const primary = await getPrimaryRow(env, row.device_id);
  if (primary) row = primary;
  return json(req, 200, {
    user: {
      id: row.device_id, provider: row.provider, providerUserId: row.provider_user_id,
      displayName: row.display_name, level: row.level,
      // CL-APP-07: the verified email (linking key); null until provided by a
      // verified-email provider or the member-center email flow.
      verifiedEmail: row.verified_email || null,
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
  // CL-APP-07: refresh re-keys onto the primary when the account was linked
  // after the original login — the new session must not keep the alias id.
  const refreshSub = await resolvePrimaryDeviceId(env, payload.sub);
  const row = await env.DB.prepare("SELECT device_id, display_name, level FROM users WHERE device_id = ?1").bind(refreshSub).first();
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

  // CL-APP-07: edits land on the PRIMARY row (an alias session edits the
  // account the member actually sees).
  const profileUserId = await resolvePrimaryDeviceId(env, session.sub);
  const row = await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level, profile_json, name_history, verified_email FROM users WHERE device_id = ?1"
  ).bind(profileUserId).first();
  if (!row) return json(req, 401, { error: "session user not found" });

  let displayName = row.display_name;
  let renameEntry = null;
  let nameHistory = [];
  try { const h = JSON.parse(row.name_history || "[]"); if (Array.isArray(h)) nameHistory = h; } catch { nameHistory = []; }
  if (body.displayName !== undefined) {
    if (typeof body.displayName !== "string") return json(req, 400, { error: "displayName must be a string" });
    const trimmed = body.displayName.trim();
    if (!trimmed || trimmed.length > 100) return json(req, 400, { error: "displayName must be 1-100 characters" });
    if (trimmed !== (row.display_name || "")) {
      // CL-DATA-70 owner ruling: once the feedback channel is live, display_name
      // may change at most once per 7 days (429 + tri-lingual reason); every
      // accepted rename is recorded in users.name_history for audit. Rating
      // trust stays keyed to user_id — renames never touch it.
      if (await feedbackEnabled(env)) {
        const last = nameHistory[nameHistory.length - 1];
        if (last && last.at && (Date.now() - Date.parse(last.at)) < 7 * 24 * 3600_000) {
          return json(req, 429, {
            error: "display_name can only be changed once every 7 days",
            message: {
              "zh-TW": "暱稱每 7 天只能修改一次，請稍後再試",
              "en": "Display name can only be changed once every 7 days — please try again later",
              "ja": "表示名は7日に1回のみ変更できます。しばらくしてからお試しください",
            },
          });
        }
        // empty→name is an initial setup, not a rename — recorded, never throttled
        if (row.display_name) renameEntry = { name: trimmed, at: new Date().toISOString() };
        else renameEntry = { name: trimmed, at: new Date().toISOString(), initial: true };
      }
    }
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
  ).bind(displayName, profileJson, profileUserId).run();

  // CL-DATA-70: append the rename audit entry (kept small — last 50).
  if (renameEntry) {
    const nextHistory = [...nameHistory, renameEntry].slice(-50);
    await env.DB.prepare("UPDATE users SET name_history = ?1 WHERE device_id = ?2")
      .bind(JSON.stringify(nextHistory), profileUserId).run();
  }

  return json(req, 200, {
    ok: true,
    user: { id: row.device_id, provider: row.provider, providerUserId: row.provider_user_id, displayName, level: row.level, profile: publicProfile },
  });
}

// ---------------------------------------------------------------------------
// CL-API-03 notification engine — rules, Telegram binding, web-push skeleton
// ---------------------------------------------------------------------------

// Rules endpoints are JWT-only (no legacy anonymous fallback); CL-UI-99
// custom-conditions validation lives in notify.js next to the engine.
async function requireSession(req, env) {
  const session = await getSession(req, env);
  if (!session || !session.sub) return null;
  // CL-APP-07: pre-link sessions still carry the alias id — ownership reads
  // and writes resolve to the primary before touching data.
  return { ...session, sub: await resolvePrimaryDeviceId(env, session.sub) };
}

async function userLevel(env, sub, fallback) {
  const row = await env.DB.prepare("SELECT level FROM users WHERE device_id = ?1").bind(sub).first();
  return (row && row.level) || fallback || "free";
}

// CL-DATA-70: effective member grade from the EXISTING users.level column
// (value domain extended: free/paid/owner — owner = unlimited, set by the
// manager directly in D1).
function effectiveMemberLevel(level, freeAsPaid) {
  if (level === "owner") return "owner";
  if (level === "paid" || (level === "free" && freeAsPaid)) return "paid";
  return "free";
}

// Pre-billing grace flag: everyone tests at the paid cap until money flows.
async function memberFreeAsPaid(env) {
  if (env.MEMBER_FREE_AS_PAID === "1") return true;
  if (env.MEMBER_FREE_AS_PAID === "0") return false;
  try {
    const v = await env.EVALS.get("v1:flags:member", "json");
    return !!(v && v.freeAsPaid === true);
  } catch { return false; }
}

const NOTIFY_RULE_LIMIT_MESSAGES = {
  free: {
    "zh-TW": "免費版上限 3 條提醒。既有提醒會保留，刪除至上限內即可再新增。",
    "en": "Free plan is capped at 3 reminders. Existing reminders are kept — delete down below the cap to add more.",
    "ja": "無料プランのリマインダー上限は3件です。既存のリマインダーは保持され、上限以下にすると追加できます。",
  },
  paid: {
    "zh-TW": "付費版上限 20 條提醒。既有提醒會保留，刪除至上限內即可再新增。",
    "en": "Paid plan is capped at 20 reminders. Existing reminders are kept — delete down below the cap to add more.",
    "ja": "有料プランのリマインダー上限は20件です。既存のリマインダーは保持され、上限以下にすると追加できます。",
  },
};

async function handleNotifyRules(req, env) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const level = await userLevel(env, uid, session.level);

  if (req.method === "GET") {
    const { results } = await env.DB.prepare(
      "SELECT id, place_id, opportunity_id, channel, min_advance_hours, custom_conditions, enabled, created_at FROM notify_rules WHERE user_id = ?1 ORDER BY created_at DESC"
    ).bind(uid).all();
    // CL-UI-99: custom_conditions round-trips as a parsed object (null = subject mode).
    const rules = (results || []).map((r) => {
      const cc = parseCustomConditions(r.custom_conditions);
      return cc ? { ...r, custom_conditions: cc } : r;
    });
    return json(req, 200, { userId: uid, level, rules });
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

    // CL-UI-99: optional custom-conditions payload — custom mode. Mutually
    // exclusive with the subject mode (opportunityId): exactly one of the two.
    const ccRes = validateCustomConditions(body ? (body.customConditions != null ? body.customConditions : body.custom_conditions) : null);
    if (!ccRes.ok) return json(req, 400, { error: ccRes.error });
    if (ccRes.cc && opportunityId) {
      return json(req, 400, { error: "customConditions and opportunityId are mutually exclusive (subject mode or custom mode)" });
    }

    const freeAsPaid = level !== "owner" && level !== "paid" ? await memberFreeAsPaid(env) : false;
    const effLevel = effectiveMemberLevel(level, freeAsPaid);
    const limit = effLevel === "owner" ? Infinity : NOTIFY_RULE_CAPS[effLevel];
    const row = await env.DB.prepare("SELECT COUNT(*) AS n FROM notify_rules WHERE user_id = ?1").bind(uid).first();
    const count = row ? row.n : 0;
    if (count >= limit) {
      // CL-DATA-70 owner ruling: 403 (not 402) + tri-lingual reason. Rules that
      // predate the cap are grandfathered (never auto-deleted) — the member
      // can only add again once the count is below the cap. Owner is exempt.
      return json(req, 403, {
        error: "notify rule limit reached",
        memberLevel: effLevel,
        count,
        cap: effLevel === "owner" ? null : limit,
        message: NOTIFY_RULE_LIMIT_MESSAGES[effLevel],
      });
    }

    const id = btoa(crypto.getRandomValues(new Uint8Array(12)).reduce((s, b) => s + String.fromCharCode(b), ""))
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    const ccJson = ccRes.cc ? JSON.stringify(ccRes.cc) : null;
    await env.DB.prepare(
      "INSERT INTO notify_rules (id, user_id, place_id, opportunity_id, channel, min_advance_hours, custom_conditions) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)"
    ).bind(id, uid, placeId, opportunityId, channel, advance, ccJson).run();
    const rule = { id, placeId, opportunityId, channel, minAdvanceHours: advance };
    if (ccRes.cc) rule.customConditions = ccRes.cc;
    return json(req, 200, { ok: true, rule, count: count + 1, limit });
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
  if (session && session.sub) uid = await resolvePrimaryDeviceId(env, session.sub);
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

// ---------------------------------------------------------------------------
// CL-APP-07: provider config + account linking.
// ---------------------------------------------------------------------------

// GET /auth/config — public, read-class. The shells read this BEFORE mounting
// provider entries: a provider the owner has not provisioned stays hidden
// (fail-closed), never a button that answers 503 in the user's face.
async function handleAuthConfig(req, env) {
  return json(req, 200, {
    providers: {
      line: providerConfigured(env, "line"),
      google: providerConfigured(env, "google"),
      apple: providerConfigured(env, "apple"),
    },
  });
}

// GET /auth/link/status — session-only. Powers the member dropdown 連結 panel.
async function handleLinkStatus(req, env) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const row = await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level, verified_email FROM users WHERE device_id = ?1"
  ).bind(session.sub).first();
  if (!row) return json(req, 401, { error: "session user not found" });
  const { results } = await env.DB.prepare(
    "SELECT alias_provider, verified_email, created_at FROM account_links WHERE primary_user_id = ?1 ORDER BY created_at ASC"
  ).bind(session.sub).all();
  return json(req, 200, {
    user: { id: row.device_id, provider: row.provider, providerUserId: row.provider_user_id, displayName: row.display_name, level: row.level },
    verifiedEmail: row.verified_email || null,
    // Provider ids stay server-side (privacy): the UI shows provider + email.
    links: (results || []).map((r) => ({ provider: r.alias_provider, email: r.verified_email || null, createdAt: r.created_at })),
  });
}

// POST /auth/link/start { email } — the member-center email-verification flow
// for providers without an email scope (LINE). A single-use token (30 min) is
// queued and delivered through the owner-configured webhook; WITHOUT a
// configured delivery channel the flow fails closed (503): handing the verify
// URL to the requester instead would let any signed-in member claim an email
// they don't own and take over the matching account via auto-link.
// Token TTL: 30 minutes (enforced in the SQL WHERE clauses below).
const LINK_MESSAGES = {
  sent: {
    "zh-TW": "驗證信已寄出，請在 30 分鐘內點擊信中連結完成連結。",
    "en": "A verification email was sent — open the link within 30 minutes to finish linking.",
    "ja": "確認メールを送信しました。30分以内にリンクを開いて連携を完了してください。",
  },
  notConfigured: {
    "zh-TW": "會員中心連結信尚未開放（待站方設定寄信服務）。",
    "en": "Email linking is not open yet (the mail service is pending owner setup).",
    "ja": "メール連携はまだ利用できません（送信設定は準備中です）。",
  },
  deliveryFailed: {
    "zh-TW": "驗證信寄送失敗，請稍後再試。",
    "en": "The verification email could not be sent — please try again later.",
    "ja": "確認メールの送信に失敗しました。しばらくしてからお試しください。",
  },
};
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

async function handleLinkStart(req, env, url) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const body = await req.json().catch(() => null);
  const email = normalizeEmail(body && body.email);
  if (!EMAIL_RE.test(email) || email.length > 200) {
    return json(req, 400, { error: "valid email required" });
  }
  if (!env.LINK_EMAIL_WEBHOOK) {
    return json(req, 503, { error: "email delivery not configured", message: LINK_MESSAGES.notConfigured });
  }
  // Opportunistic cleanup: consumed/expired rows never linger.
  await env.DB.prepare(
    "DELETE FROM link_email_verifications WHERE created_at < datetime('now', '-30 minutes') OR consumed = 1"
  ).bind().run();
  const token = randomId();
  await env.DB.prepare(
    "INSERT INTO link_email_verifications (token, user_id, email) VALUES (?1, ?2, ?3)"
  ).bind(token, session.sub, email).run();
  const verifyUrl = `${url.origin}/api/v1/auth/link/verify?token=${encodeURIComponent(token)}`;
  let delivered = false;
  try {
    const res = await fetch(env.LINK_EMAIL_WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ to: email, verifyUrl, token, ttlMinutes: 30 }),
    });
    delivered = res && res.ok;
  } catch { delivered = false; }
  if (!delivered) return json(req, 503, { error: "email delivery failed", message: LINK_MESSAGES.deliveryFailed });
  return json(req, 200, { ok: true, delivery: "webhook", email, message: LINK_MESSAGES.sent });
}

// GET /auth/link/verify?token=… — the email-link click. Token-only credential
// (the click may happen in another browser, without the member session).
// Existing account with the same verified email → alias merges into it;
// otherwise the verified email becomes this account's linking key (a later
// Apple/Google login with the same email auto-links). Terminal state is a
// 302 to the homepage with ?link_result=ok|error (shell shows a tri-lingual
// notice and re-pulls /auth/me).
async function handleLinkVerify(req, env, url) {
  const token = url.searchParams.get("token");
  if (!token) return homeRedirect("link_result=error");
  await env.DB.prepare(
    "DELETE FROM link_email_verifications WHERE created_at < datetime('now', '-30 minutes')"
  ).bind().run();
  const row = await env.DB.prepare(
    "SELECT token, user_id, email, consumed FROM link_email_verifications WHERE token = ?1"
  ).bind(token).first();
  // single-use: consume first, fail-closed on replay.
  await env.DB.prepare("DELETE FROM link_email_verifications WHERE token = ?1").bind(token).run();
  if (!row || row.consumed) return homeRedirect("link_result=error");
  const email = normalizeEmail(row.email);
  const aliasRow = await env.DB.prepare(
    "SELECT device_id, provider, provider_user_id, display_name, level, verified_email FROM users WHERE device_id = ?1"
  ).bind(row.user_id).first();
  if (!aliasRow || !email) return homeRedirect("link_result=error");

  let result = "ok";
  const other = await env.DB.prepare(
    "SELECT device_id FROM users WHERE verified_email = ?1 AND device_id != ?2 ORDER BY created_at ASC LIMIT 1"
  ).bind(email, aliasRow.device_id).first();
  if (other && other.device_id) {
    const primary = (await getPrimaryRow(env, other.device_id)) ||
      await env.DB.prepare(
        "SELECT device_id, provider, provider_user_id, display_name, level, verified_email FROM users WHERE device_id = ?1"
      ).bind(other.device_id).first();
    const linked = await linkAliasToPrimary(env, aliasRow, primary, email);
    if (!linked) result = "error";
  } else if ((aliasRow.verified_email || "") !== email) {
    try {
      await env.DB.prepare("UPDATE users SET verified_email = ?1 WHERE device_id = ?2")
        .bind(email, aliasRow.device_id).run();
    } catch { result = "error"; } // unique index → email claimed meanwhile
  }
  return homeRedirect(result === "ok" ? "link_result=ok" : "link_result=error");
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/^\/api\/v1/, "");

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(request) });

    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    if (rateLimited(ip, path, request.method, Date.now())) return json(request, 429, { error: "rate limited" });

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

    // --- custom places (CL-APP-06, member-only private points) ---
    if (path === "/conditions/parse" && request.method === "GET") {
      return handleConditionsParseConfig(request, env);
    }
    if (path === "/conditions/parse" && request.method === "POST") {
      return handleConditionsParse(request, env);
    }
    if (path === "/custom_places/pin_info" && request.method === "GET") {
      return handleCustomPlacePinInfo(request, env, url);
    }
    if (path === "/custom_places") return handleCustomPlaces(request, env);
    {
      const cpm = path.match(/^\/custom_places\/([\w-]+)$/);
      if (cpm && request.method === "PATCH") return handleCustomPlaceItem(request, env, cpm[1]);
      if (cpm && request.method === "DELETE") return handleCustomPlaceItem(request, env, cpm[1]);
      if (cpm && request.method === "POST") return handleCustomPlaceNominate(request, env, cpm[1]);
    }
    {
      // patch-7: private-card forecast popup reads the stored eval (read-only)
      const cpe = path.match(/^\/custom_places\/([\w-]+)\/eval$/);
      if (cpe && request.method === "GET") return handleCustomPlaceEval(request, env, cpe[1]);
    }
    {
      // patch-8: per-place condition-group CRUD (multi-theme) — no fetch, no quota
      const cpt = path.match(/^\/custom_places\/([\w-]+)\/themes$/);
      if (cpt && request.method === "POST") return handleCustomPlaceThemes(request, env, cpt[1]);
      const cpti = path.match(/^\/custom_places\/([\w-]+)\/themes\/([\w-]+)$/);
      if (cpti && request.method === "PATCH") return handleCustomPlaceThemeItem(request, env, cpti[1], cpti[2]);
      if (cpti && request.method === "DELETE") return handleCustomPlaceThemeItem(request, env, cpti[1], cpti[2]);
    }

    // --- feedback channel (CL-DATA-70, gray-released) ---
    // CL-UI-100: the gray-release probe the shell reads before mounting any
    // rating UI — 200 with the flag value always (clients treat any non-200,
    // e.g. a 404 from a pre-config deployment, as "disabled").
    if (path === "/feedback/config" && request.method === "GET") {
      return json(request, 200, { enabled: await feedbackEnabled(env) });
    }
    if (path === "/feedback" && (request.method === "GET")) {
      if (!(await feedbackEnabled(env))) return json(request, 403, { error: "feedback disabled" });
      return handleFeedback(request, env, url);
    }
    if (path === "/feedback" && (request.method === "POST" || request.method === "PUT")) {
      if (!(await feedbackEnabled(env))) return json(request, 403, { error: "feedback disabled" });
      return handleFeedbackSubmit(request, env, url);
    }
    if (path === "/feedback" && request.method === "DELETE") {
      if (!(await feedbackEnabled(env))) return json(request, 403, { error: "feedback disabled" });
      return handleFeedbackDelete(request, env, url);
    }
    if (path === "/admin/feedback" && request.method === "GET") {
      if (!(await feedbackEnabled(env))) return json(request, 403, { error: "feedback disabled" });
      return handleAdminFeedbackList(request, env, url);
    }
    {
      const am = path.match(/^\/admin\/feedback\/([\w-]+)$/);
      if (am && request.method === "PATCH") {
        if (!(await feedbackEnabled(env))) return json(request, 403, { error: "feedback disabled" });
        return handleAdminFeedbackReview(request, env, am[1]);
      }
    }

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
    if ((m = path.match(/^\/auth\/(line|google|apple)\/start$/))) {
      if (request.method !== "GET") return json(request, 405, { error: "method not allowed" });
      return handleOAuthStart(request, env, m[1], url);
    }
    if ((m = path.match(/^\/auth\/(line|google|apple)\/callback$/))) {
      if (request.method !== "GET" && !(m[1] === "apple" && request.method === "POST")) {
        return json(request, 405, { error: "method not allowed" });
      }
      return handleOAuthCallback(request, env, m[1], url);
    }
    if (path === "/auth/mock/start") return handleMockStart(request, env, url);
    if (path === "/auth/config" && request.method === "GET") return handleAuthConfig(request, env);
    if (path === "/auth/link/status" && request.method === "GET") return handleLinkStatus(request, env);
    if (path === "/auth/link/start" && request.method === "POST") return handleLinkStart(request, env, url);
    if (path === "/auth/link/verify" && request.method === "GET") return handleLinkVerify(request, env, url);
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
    // CL-APP-06: custom places ride the SAME cron but a DEDICATED low-priority
    // queue (batch-capped; global 70% brake downshifts 10%, 90% hard-stops
    // non-core refreshes — never the notify engine, which is the paid core).
    ctx.waitUntil(processCustomFetchQueue(env).then((s) => console.log("[custom-places-queue]", JSON.stringify(s))).catch((e) => console.error("[custom-places-queue]", e && e.message)));
  },
};
