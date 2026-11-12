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
  const raw = doc.display_name ?? doc.name ?? doc.sub ?? null;
  if (typeof raw !== "string") return null;
  const name = raw.trim();
  if (!name) return null;
  const provider = typeof doc.provider === "string" && doc.provider.trim() ? doc.provider.trim() : null;
  return { name, provider };
}

export async function fetchMember(fetchImpl = (...args) => fetch(...args), url = AUTH_ME_ENDPOINT) {
  let response;
  try {
    response = await fetchImpl(url, { credentials: "same-origin", cache: "no-store" });
  } catch {
    return null;
  }
  if (!response.ok) return null;
  let doc;
  try { doc = await response.json(); } catch { return null; }
  return parseMember(doc);
}
