// Shell auth entry (CL-APP-02): trilingual sign-in entry points and the
// signed-in member lookup.
//
// JWTs ride HttpOnly cookies, so same-origin fetches to /api/v1/auth/me carry
// the session automatically inside the WebView — no token handling lives here.
// The start endpoints are plain top-level navigations (302 to the OAuth
// provider), so they are rendered as anchors, never fetched.
// CL-UI-54: the bare /auth/* path 404'd — the API mounts under /api/v1.
export const AUTH_START_ENDPOINTS = Object.freeze({
  line: "/api/v1/auth/line/start",
  google: "/api/v1/auth/google/start"
});
export const AUTH_ME_ENDPOINT = "/api/v1/auth/me";
// CL-UI-60: silent session renewal. The access JWT cookie (cl_session) expires
// after 15 minutes while the refresh JWT cookie (cl_refresh) lasts 30 days
// (workers/api/src/index.js handleAuthRefresh), so a 401 on /auth/me must try
// POST /auth/refresh once before declaring the visitor signed out. The worker
// answers 200 { ok, accessToken, refreshToken } and rotates BOTH cookies via
// Set-Cookie, so the follow-up /auth/me succeeds inside the WebView without
// any token handling here; 401 answers { error: "invalid refresh token" }.
export const AUTH_REFRESH_ENDPOINT = "/api/v1/auth/refresh";

// CL-API-05: OAuth callbacks redirect back to the homepage instead of
// rendering bare JSON. A failed callback carries ?auth_error=1; the shell
// consumes it and shows a trilingual retry notice.
export const AUTH_ERROR_PARAM = "auth_error";
export const AUTH_ERROR_I18N = Object.freeze({
  "zh-TW": "登入失敗，請重試",
  "en": "Sign in failed, please try again",
  "ja": "ログインに失敗しました。もう一度お試しください"
});

// Returns true exactly when `search` (URLSearchParams or location.search
// string) carries the auth_error=1 flag, and — given a URLSearchParams —
// strips the flag from it so callers can clean the address bar.
export function consumeAuthError(search) {
  const q = typeof search === "string" ? new URLSearchParams(search) : search;
  if (!(q && typeof q.get === "function")) return false;
  if (q.get(AUTH_ERROR_PARAM) !== "1") return false;
  if (typeof q.delete === "function") q.delete(AUTH_ERROR_PARAM);
  return true;
}

export function authErrorMessage(locale) {
  return AUTH_ERROR_I18N[locale] || AUTH_ERROR_I18N["zh-TW"];
}

// Accepts the /auth/me document; returns a member only when a usable display
// name is present. Anything else (401, empty object, blank name) is "not
// signed in" — the entry must show the sign-in buttons, never a fake member.
export function parseMember(doc) {
  if (!doc || typeof doc !== "object" || Array.isArray(doc)) return null;
  // CL-UI-56: /api/v1/auth/me actually answers { user: { displayName, provider, … } }
  // (nested + camelCase, see workers/api/src/index.js handleAuthMe), so the
  // nested shape wins; legacy top-level display_name/name/sub stay supported.
  const u = doc.user != null && typeof doc.user === "object" ? doc.user : null;
  const raw = (u && u.displayName != null) ? u.displayName
            : doc.display_name ?? doc.name ?? doc.sub ?? null;
  if (typeof raw !== "string") return null;
  const name = raw.trim();
  if (!name) return null;
  const rawProvider = (u && typeof u.provider === "string" && u.provider.trim()) ? u.provider
                    : (typeof doc.provider === "string" && doc.provider.trim() ? doc.provider : null);
  const provider = rawProvider ? rawProvider.trim() : null;
  return { name, provider };
}

// CL-UI-60: simple throttle so a renewed session does not re-double-call
// /auth/me + /auth/refresh on every load: at most one refresh attempt per
// window, and concurrent 401s share a single in-flight refresh. State lives
// per module instance (one page load), like the throttle in member-auth.js.
const REFRESH_THROTTLE_MS = 30_000;
let lastRefreshAt = 0;
let refreshInFlight = null;

// Test hook: reset throttle + in-flight state between cases.
export function resetAuthRefreshState() {
  lastRefreshAt = 0;
  refreshInFlight = null;
  resetAuthMeState();
}

// CL-API-07: a 429/5xx/network failure on /auth/me must NEVER be read as
// "signed out" — the old `res.ok ? … : null` path flipped a signed-in member
// back to the 登入 buttons whenever the IP rate limiter answered 429 after a
// few page loads. Callers receiving MEMBER_TRANSIENT keep their current
// member state and retry later (exponential backoff in the shell); only a
// 401 — after a failed silent refresh — decides signed-out.
export const MEMBER_TRANSIENT = Object.freeze({ transient: true });
export function isMemberTransient(v) {
  return v === MEMBER_TRANSIENT;
}

// CL-API-07: module-level single-flight + short result cache so the repeated
// /auth/me pulls across member/favorites/shell modules on one page load share
// at most ONE real request per cache window.
const ME_CACHE_MS = 10_000;
let meInFlight = null, meCacheMember = null, meCacheAt = 0;

export function resetAuthMeState() {
  meInFlight = null;
  meCacheMember = null;
  meCacheAt = 0;
}

export async function fetchMember(fetchImpl = (...args) => fetch(...args), url = AUTH_ME_ENDPOINT) {
  if (meInFlight) return meInFlight;
  if (meCacheAt && Date.now() - meCacheAt < ME_CACHE_MS) return meCacheMember;
  meInFlight = (async () => {
    let result;
    let response = null;
    try {
      response = await fetchImpl(url, { credentials: "same-origin", cache: "no-store" });
    } catch {
      result = MEMBER_TRANSIENT;
    }
    if (response) {
      if (response.status === 429 || response.status >= 500) {
        result = MEMBER_TRANSIENT; // transient: keep current state, retry later
      } else if (response.status === 401) {
        const doc = await refreshThenMe(fetchImpl, url);
        result = doc ? parseMember(doc) : null; // 401 + failed refresh = signed out
      } else if (!response.ok) {
        result = MEMBER_TRANSIENT;
      } else {
        let doc;
        try { doc = await response.json(); } catch { doc = null; }
        result = parseMember(doc);
      }
    }
    meCacheMember = result;
    meCacheAt = Date.now();
    return result;
  })();
  try {
    return await meInFlight;
  } finally {
    meInFlight = null;
  }
}

async function refreshThenMe(fetchImpl, url) {
  if (refreshInFlight) return refreshInFlight;
  if (Date.now() - lastRefreshAt < REFRESH_THROTTLE_MS) return null;
  lastRefreshAt = Date.now();
  refreshInFlight = (async () => {
    try {
      // The refresh JWT rides the HttpOnly cl_refresh cookie (same-origin);
      // the POST body stays empty — handleAuthRefresh also accepts a
      // { refreshToken } body but cookies are the only source in the shell.
      const refreshRes = await fetchImpl(AUTH_REFRESH_ENDPOINT, {
        method: "POST",
        credentials: "same-origin",
        cache: "no-store"
      });
      if (!refreshRes.ok) return null;
      const meRes = await fetchImpl(url, { credentials: "same-origin", cache: "no-store" });
      if (!meRes.ok) return null;
      return await meRes.json();
    } catch {
      return null;
    } finally {
      refreshInFlight = null;
    }
  })();
  return refreshInFlight;
}


