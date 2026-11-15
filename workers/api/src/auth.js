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
    parseUser: (u) => ({
      providerUserId: u.sub,
      displayName: u.name || u.email || `GOOGLE-${u.sub}`,
      email: typeof u.email === "string" ? u.email : null,
      emailVerified: u.email_verified === true,
    }),
  },
  // CL-APP-07: Sign in with Apple. Identity comes from the id_token JWT (Apple
  // has no userinfo endpoint); the client_secret is an ES256 JWT signed with
  // the owner's .p8 key, so FOUR owner-provided values are required —
  // APPLE_SERVICES_ID (client_id), APPLE_TEAM_ID, APPLE_KEY_ID, APPLE_PRIVATE_KEY
  // (PEM contents). Until all four land as wrangler secrets the provider is
  // fail-closed: /auth/apple/start answers 503 and the shells hide the entry.
  apple: {
    authorizeUrl: "https://appleid.apple.com/auth/authorize",
    tokenUrl: "https://appleid.apple.com/auth/token",
    jwksUrl: "https://appleid.apple.com/auth/keys",
    issuer: "https://appleid.apple.com",
    userinfoUrl: null, // identity comes from the id_token, not a userinfo call
    scope: "name email",
    idEnv: "APPLE_SERVICES_ID",
    secretEnv: "APPLE_TEAM_ID",
    configured: (env) => Boolean(env.APPLE_SERVICES_ID && env.APPLE_TEAM_ID && env.APPLE_KEY_ID && env.APPLE_PRIVATE_KEY),
    parseToken: (tok) => ({ idToken: tok.id_token || null, accessToken: tok.access_token }),
    // Apple sends name/email only inside the id_token claims (first consent
    // carries name; email carries email_verified as boolean | "true"/"false").
    parseUser: (u) => {
      const n = (u.name && typeof u.name === "object") ? [u.name.givenName, u.name.lastName].filter(Boolean).join(" ") : null;
      const email = typeof u.email === "string" && u.email ? u.email : null;
      return {
        providerUserId: u.sub,
        displayName: n || (email ? email.split("@")[0] : `APPLE-${u.sub}`),
        email,
        emailVerified: email != null && (u.email_verified === true || u.email_verified === "true" || u.email_verified == null),
      };
    },
  },
};

export function providerConfigured(env, name) {
  const p = PROVIDERS[name];
  if (!p) return false;
  return p.configured ? p.configured(env) : Boolean(env[p.idEnv] && env[p.secretEnv]);
}

export function providerCredentials(env, name) {
  const p = PROVIDERS[name];
  if (!p) return null;
  return { id: env[p.idEnv], secret: env[p.secretEnv], provider: p };
}

export function oauthUserKey(provider, providerUserId) {
  return `p:${provider}:${providerUserId}`;
}

// CL-APP-07: sessions minted BEFORE a link was established still carry the
// alias device_id for up to 30 days — every ownership read/write resolves the
// alias to its primary first so a linked member's data never splits again.
export async function resolvePrimaryDeviceId(env, sub) {
  if (!sub || !env.DB || !/^p:/.test(sub)) return sub;
  try {
    const link = await env.DB.prepare(
      "SELECT primary_user_id FROM account_links WHERE alias_device_id = ?1"
    ).bind(sub).first();
    return (link && link.primary_user_id) || sub;
  } catch { return sub; }
}

// Anonymous device rows are re-keyed onto the OAuth identity. UPDATE OR IGNORE
// keeps PK (user_id, place_id) conflicts from exploding when both sides share
// rows. CL-UI-57: the conflicting source rows are NOT left behind by OR IGNORE,
// so mergeAnonDevice follows up with a device-wide DELETE — otherwise a stale
// anonymous row (a favorite the account already had) survives the merge and
// leaks to whichever identity the device id later resolves to (a different
// account on the same browser, or the anonymous mode after logout).
export const MERGE_SQL = {
  favorites: "UPDATE OR IGNORE favorites SET user_id = ?1 WHERE user_id = ?2",
  notify_rules: "UPDATE OR IGNORE notify_rules SET user_id = ?1 WHERE user_id = ?2",
  favorites_cleanup: "DELETE FROM favorites WHERE user_id = ?1",
  notify_rules_cleanup: "DELETE FROM notify_rules WHERE user_id = ?1",
};

// ---------------------------------------------------------------------------
// CL-APP-07: Sign in with Apple helpers.
// client_secret = ES256 JWT signed with the owner's .p8 (PKCS#8 P-256) key;
// identity = RS256 id_token verified against Apple's published JWKS.
// ---------------------------------------------------------------------------
const APPLE_SECRET_TTL_S = 6 * 3600; // client_secret lives ≤ 6 months; rotate per exchange

function pemToPkcs8Bytes(pem) {
  const b64 = String(pem).replace(/-----(BEGIN|END) PRIVATE KEY-----/g, "").replace(/\s+/g, "");
  return Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
}

export async function appleClientSecret(env, now = Math.floor(Date.now() / 1000)) {
  if (!env.APPLE_SERVICES_ID || !env.APPLE_TEAM_ID || !env.APPLE_KEY_ID || !env.APPLE_PRIVATE_KEY) {
    throw new Error("apple oauth not configured");
  }
  const data = `${b64urlJson({ alg: "ES256", kid: env.APPLE_KEY_ID })}.${b64urlJson({
    iss: env.APPLE_TEAM_ID,
    iat: now,
    exp: now + APPLE_SECRET_TTL_S,
    aud: "https://appleid.apple.com",
    sub: env.APPLE_SERVICES_ID,
  })}`;
  const key = await crypto.subtle.importKey(
    "pkcs8", pemToPkcs8Bytes(env.APPLE_PRIVATE_KEY),
    { name: "ECDSA", namedCurve: "P-256" }, false, ["sign"],
  );
  const sig = await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, key, enc.encode(data));
  return `${data}.${b64url(sig)}`;
}

// base64url decode → bytes (JWT segments are unpadded).
function b64urlToBytes(s) {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4);
  return Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
}

// Verify an Apple id_token (RS256) against Apple's JWKS and return its claims.
// Returns null for anything that fails signature/kid/issuer/audience/expiry —
// the caller turns that into the honest auth_error redirect, never a session.
export async function verifyAppleIdToken(env, idToken, opts = {}) {
  if (typeof idToken !== "string" || idToken.split(".").length !== 3) return null;
  const [head, body, sigB64] = idToken.split(".");
  let header, claims;
  try {
    header = JSON.parse(new TextDecoder().decode(b64urlToBytes(head)));
    claims = JSON.parse(new TextDecoder().decode(b64urlToBytes(body)));
  } catch { return null; }
  if (!header || header.alg !== "RS256" || !header.kid) return null;
  const jwksUrl = (PROVIDERS.apple.jwksUrl);
  let keys = null;
  try {
    const res = await fetch(jwksUrl, { cache: "no-store" });
    if (!res.ok) return null;
    const doc = await res.json();
    keys = Array.isArray(doc.keys) ? doc.keys : null;
  } catch { return null; }
  if (!keys) return null;
  const jwk = keys.find((k) => k.kid === header.kid && (!k.alg || k.alg === "RS256"));
  if (!jwk) return null;
  let key;
  try {
    key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  } catch { return null; }
  const ok = await crypto.subtle.verify(
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, key,
    b64urlToBytes(sigB64), enc.encode(`${head}.${body}`),
  );
  if (!ok) return null;
  const now = Math.floor((opts.now || Date.now()) / 1000);
  if (typeof claims.exp === "number" && now > claims.exp) return null;
  if (claims.iss !== PROVIDERS.apple.issuer) return null;
  if (env.APPLE_SERVICES_ID && claims.aud !== env.APPLE_SERVICES_ID) return null;
  if (!claims.sub) return null;
  return claims;
}
