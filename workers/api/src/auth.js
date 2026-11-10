// CL-API-02: auth helpers — HS256 JWT (Web Crypto), OAuth providers, session cookies.
// Short-lived signed access JWT + refresh JWT; HttpOnly cookies + Authorization header.

const ACCESS_TTL_S = 15 * 60;          // 15 min
const REFRESH_TTL_S = 30 * 24 * 3600;  // 30 days
export const SESSION_COOKIE = "cl_session";
export const REFRESH_COOKIE = "cl_refresh";

const enc = new TextEncoder();

function b64url(bytes) {
  let s = "";
  for (const b of new Uint8Array(bytes)) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64urlJson(obj) { return b64url(enc.encode(JSON.stringify(obj))); }

function hmacKey(secret) {
  return crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
}

export async function signJWT(payload, secret) {
  const head = b64urlJson({ alg: "HS256", typ: "JWT" });
  const body = b64urlJson(payload);
  const data = `${head}.${body}`;
  const sig = await crypto.subtle.sign("HMAC", await hmacKey(secret), enc.encode(data));
  return `${data}.${b64url(sig)}`;
}

export async function verifyJWT(token, secret) {
  if (typeof token !== "string") return null;
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  const [head, body, sigB64] = parts;
  const key = await hmacKey(secret);
  const sigBytes = Uint8Array.from(atob(sigB64.replace(/-/g, "+").replace(/_/g, "/")), c => c.charCodeAt(0));
  const ok = await crypto.subtle.verify("HMAC", key, sigBytes, enc.encode(`${head}.${body}`));
  if (!ok) return null;
  try {
    const payload = JSON.parse(atob(body.replace(/-/g, "+").replace(/_/g, "/")));
    if (typeof payload.exp === "number" && Math.floor(Date.now() / 1000) > payload.exp) return null;
    return payload;
  } catch { return null; }
}

export function authSecret(env) {
  return env.AUTH_SECRET || "chaselights-dev-secret-do-not-use-in-prod";
}

export async function makeTokens(env, sub, name, level) {
  const now = Math.floor(Date.now() / 1000);
  const base = { sub, name, level, iat: now };
  const access = await signJWT({ ...base, typ: "access", exp: now + ACCESS_TTL_S }, authSecret(env));
  const refresh = await signJWT({ ...base, typ: "refresh", exp: now + REFRESH_TTL_S }, authSecret(env));
  return { access, refresh };
}

export function cookieHeader(name, value, maxAgeS) {
  const attrs = [`${name}=${value}`, "HttpOnly", "Secure", "SameSite=Lax", "Path=/", `Max-Age=${maxAgeS}`];
  return attrs.join("; ");
}

export async function getSession(request, env) {
  const authz = request.headers.get("Authorization");
  if (authz && /^Bearer\s+/i.test(authz)) {
    return verifyJWT(authz.replace(/^Bearer\s+/i, ""), authSecret(env));
  }
  const cookies = request.headers.get("Cookie") || "";
  const m = cookies.match(new RegExp(`(?:^|;\\s*)${SESSION_COOKIE}=([^;]+)`));
  if (!m) return null;
  const payload = await verifyJWT(m[1], authSecret(env));
  return payload && payload.typ === "access" ? payload : null;
}

// ---------------------------------------------------------------------------
// OAuth providers (client id/secret are owner-supplied via wrangler secrets;
// flow is fully built + mock-testable until credentials land).
// ---------------------------------------------------------------------------
export const PROVIDERS = {
  line: {
    authorizeUrl: "https://access.line.me/oauth2/v2.1/authorize",
    tokenUrl: "https://api.line.me/oauth2/v2.1/token",
    userinfoUrl: "https://api.line.me/oauth2/v2.1/userinfo",
    scope: "openid profile",
    idEnv: "LINE_LOGIN_CLIENT_ID",
    secretEnv: "LINE_LOGIN_CLIENT_SECRET",
    parseToken: (tok) => ({ accessToken: tok.access_token }),
    parseUser: (u) => ({ providerUserId: u.sub, displayName: u.name || `LINE-${u.sub}` }),
  },
  google: {
    authorizeUrl: "https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl: "https://oauth2.googleapis.com/token",
    userinfoUrl: "https://openidconnect.googleapis.com/v1/userinfo",
    scope: "openid email profile",
    idEnv: "GOOGLE_CLIENT_ID",
    secretEnv: "GOOGLE_CLIENT_SECRET",
    parseToken: (tok) => ({ accessToken: tok.access_token }),
    parseUser: (u) => ({ providerUserId: u.sub, displayName: u.name || u.email || `GOOGLE-${u.sub}` }),
  },
};

export function providerCredentials(env, name) {
  const p = PROVIDERS[name];
  if (!p) return null;
  return { id: env[p.idEnv], secret: env[p.secretEnv], provider: p };
}

export function oauthUserKey(provider, providerUserId) {
  return `p:${provider}:${providerUserId}`;
}

// Anonymous device rows are re-keyed onto the OAuth identity. UPDATE OR IGNORE
// keeps PK (user_id, place_id) conflicts from exploding when both sides share rows.
export const MERGE_SQL = {
  favorites: "UPDATE OR IGNORE favorites SET user_id = ?1 WHERE user_id = ?2",
  notify_rules: "UPDATE OR IGNORE notify_rules SET user_id = ?1 WHERE user_id = ?2",
};
