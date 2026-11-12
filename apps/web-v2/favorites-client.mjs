// CL-UI-55: cloud favorites client for the V2 shell (apps/web-v2).
// Same backend contract as the V1 shell's assets/favorites-client.js
// (workers/api/src/index.js): GET /api/v1/favorites[?userId=<device-id>]
// and POST { placeId, action:"add"|"remove", userId? }. The session cookie
// (Authorization/Bearer) takes precedence server-side; the legacy userId
// param is the anonymous device mode. Anonymous identity is a client-persisted
// device id; the server re-keys anonymous favorites onto the member account
// at login, so the client just re-pulls the cloud list on auth changes.
//
// Failure posture: cloud calls never block the UI. The local
// chaselights_favs_v2 list is the offline fallback (same key as the V1 shell,
// so both shells share one device-local list); failures surface as a
// trilingual notice while the local list stands.
const FAVORITES_ENDPOINT = "/api/v1/favorites";
const DEVICE_ID_KEY = "chaselights_device_id";
const LOCAL_FAVS_KEY = "chaselights_favs_v2";

export const FAVORITES_FALLBACK_I18N = Object.freeze({
  "zh-TW": "收藏暫時無法同步，已保存在此裝置。",
  "en": "Favorites could not be synced; saved on this device.",
  "ja": "お気に入りを同期できませんでした。この端末に保存しました。"
});

export function favoritesFallbackMessage(locale) {
  return FAVORITES_FALLBACK_I18N[locale] || FAVORITES_FALLBACK_I18N["zh-TW"];
}

function storageGet(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}
function storageSet(key, value) {
  try { localStorage.setItem(key, value); return true; } catch { return false; }
}

export function deviceId() {
  let id = storageGet(DEVICE_ID_KEY);
  if (!id) {
    id = (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function")
      ? globalThis.crypto.randomUUID()
      : "dev-" + Date.now() + "-" + Math.random().toString(36).slice(2);
    storageSet(DEVICE_ID_KEY, id);
  }
  try { document.cookie = "chaselights_device=" + encodeURIComponent(id) + ";max-age=31536000;path=/;SameSite=Lax"; } catch { /* cookie blocked */ }
  return id;
}

export function localFavorites() {
  let raw = null;
  try { raw = JSON.parse(storageGet(LOCAL_FAVS_KEY) || "[]"); } catch { raw = null; }
  if (!Array.isArray(raw)) return [];
  return raw.filter((x) => typeof x === "string" && x);
}

export function persistLocalFavorites(ids) {
  return storageSet(LOCAL_FAVS_KEY, JSON.stringify([...ids]));
}

export function createFavoritesClient({ fetchImpl = (...args) => fetch(...args), onNotice = () => {} } = {}) {
  let cached = null;

  async function fetchCloud() {
    const res = await fetchImpl(
      FAVORITES_ENDPOINT + "?userId=" + encodeURIComponent(deviceId()),
      { credentials: "same-origin", cache: "no-store" }
    );
    if (!res.ok) throw new Error("favorites HTTP " + res.status);
    const doc = await res.json();
    if (!doc || !Array.isArray(doc.favorites)) return [];
    cached = doc.favorites
      .map((row) => (row && typeof row.place_id === "string" ? row.place_id : null))
      .filter((x) => x);
    return cached;
  }

  async function push(placeId, action) {
    const res = await fetchImpl(FAVORITES_ENDPOINT, {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ placeId, action, userId: deviceId() })
    });
    if (!res.ok) throw new Error("favorites HTTP " + res.status);
    return true;
  }

  // Toggle a place favorite. Cloud success returns the merged cloud id set;
  // any failure falls back to the local list (already updated by the caller)
  // and raises the trilingual offline notice.
  async function toggle(placeId, adding) {
    try {
      await push(placeId, adding ? "add" : "remove");
      return await fetchCloud();
    } catch {
      onNotice(favoritesFallbackMessage());
      const local = localFavorites();
      return Array.isArray(cached) ? cached : local;
    }
  }

  // First-launch bootstrap and login resync: upload every local favorite the
  // cloud list lacks (POST add is idempotent), then return the merged set.
  async function syncLocal() {
    const cloud = await fetchCloud().catch(() => null);
    if (!cloud) return localFavorites(); // offline: local list stands, no data loss
    const missing = localFavorites().filter((id) => !cloud.includes(id));
    for (const id of missing) {
      try { await push(id, "add"); } catch { /* per-item best-effort */ }
    }
    return await fetchCloud();
  }

  return { toggle, syncLocal, fetchCloud };
}
