// Shell auth entry (CL-APP-02): trilingual sign-in entry points and the
// signed-in member lookup.
//
// JWTs ride HttpOnly cookies, so same-origin fetches to /auth/me carry the
// session automatically inside the WebView — no token handling lives here.
// The start endpoints are plain top-level navigations (302 to the OAuth
// provider), so they are rendered as anchors, never fetched.
export const AUTH_START_ENDPOINTS = Object.freeze({
  line: "/api/v1/auth/line/start",
  google: "/api/v1/auth/google/start"
});
export const AUTH_ME_ENDPOINT = "/auth/me";

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
