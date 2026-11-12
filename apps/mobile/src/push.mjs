// CL-APP-03: APP push base — @capacitor/push-notifications integration.
//
// Startup flow: request permission -> create the reminders notification
// channel -> listen for the FCM registration token -> POST it to
// POST /api/v1/push_tokens (platform: android/fcm, token, anonymous/会员
// device_id binding, Bearer header when a session token is available).
//
// Graceful degradation: when the APK was built WITHOUT google-services.json
// (owner's Firebase project pending) the FCM plugin is absent or registration
// fails — the module logs a console notice and stays disabled. The app and
// every other feature keep working; push simply never registers.

export const PUSH_CHANNEL_ID = "chaselights_reminders";
export const PUSH_API_PATH = "/api/v1/push_tokens";

const DEVICE_ID_KEY = "chaselights:device-id";

// Anonymous, per-install device id (survives restarts via localStorage).
export function deviceUniqueId(storage) {
  let id = null;
  try { id = storage.getItem(DEVICE_ID_KEY); } catch { id = null; }
  if (id) return id;
  id = "app-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
  try { storage.setItem(DEVICE_ID_KEY, id); } catch { /* storage unavailable */ }
  return id;
}

// POST /api/v1/push_tokens — resolves { ok, status } and NEVER throws
// (a network hiccup at registration time must not break app boot).
export async function registerPushToken({ apiBase, fetchImpl, token, deviceId, platform = "android/fcm", accessToken = null, log = console }) {
  try {
    const headers = { "Content-Type": "application/json" };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    const res = await fetchImpl(`${apiBase}${PUSH_API_PATH}`, {
      method: "POST",
      headers,
      body: JSON.stringify({ platform, token, deviceId }),
    });
    if (!res.ok) {
      log.warn(`[push] token registration failed: HTTP ${res.status}`);
      return { ok: false, status: res.status };
    }
    return { ok: true, status: res.status };
  } catch (e) {
    log.warn(`[push] token registration failed: ${e && e.message}`);
    return { ok: false, status: 0 };
  }
}

// Resolve the real plugin inside the Capacitor WebView. Returns null when the
// shell runs in a plain browser or the APK was built without the plugin wired
// to google-services.json.
export function defaultPushPlugin() {
  try {
    const cap = (typeof window !== "undefined" && window.Capacitor) || null;
    return (cap && cap.Plugins && cap.Plugins.PushNotifications) || null;
  } catch { return null; }
}

// createPushRegistrar({ plugin, ... }) — plugin is the Capacitor
// PushNotifications plugin object (or null/undefined when the APK shipped
// without google-services.json so FCM was never wired up).
export function createPushRegistrar({
  plugin = null,
  apiBase = "https://chaselights.app",
  fetchImpl = (typeof fetch !== "undefined" ? fetch : null),
  storage = (typeof localStorage !== "undefined" ? localStorage : null),
  accessTokenProvider = () => null,
  log = console,
} = {}) {
  async function start() {
    if (!plugin) {
      log.info("[push] disabled: PushNotifications plugin unavailable (google-services.json missing at build time — APK built without FCM push)");
      return { enabled: false, reason: "plugin-unavailable" };
    }
    if (!fetchImpl || !storage) {
      log.info("[push] disabled: fetch/storage unavailable in this runtime");
      return { enabled: false, reason: "runtime-unavailable" };
    }

    // Permission (Android 13+ POST_NOTIFICATIONS): ask once at startup.
    let granted = false;
    try {
      const cur = await plugin.checkPermissions();
      granted = (cur && cur.display === "granted") || false;
      if (!granted) {
        const req = await plugin.requestPermissions();
        granted = (req && req.display === "granted") || false;
      }
    } catch (e) {
      log.info(`[push] disabled: permission check failed (${e && e.message})`);
      return { enabled: false, reason: "permission-error" };
    }
    if (!granted) {
      log.info("[push] disabled: notification permission denied by user");
      return { enabled: false, reason: "permission-denied" };
    }

    // Android notification channel for reminders (native-side icon/channel).
    try {
      await plugin.createChannel({
        id: PUSH_CHANNEL_ID,
        name: "ChaseLights 攝影提醒",
        description: "天氣符合拍攝條件提醒",
        importance: 4, // IMPORTANCE_HIGH
        visibility: 1, // PUBLIC
      });
    } catch (e) {
      log.warn(`[push] channel creation failed (continuing): ${e && e.message}`);
    }

    let registered = false;
    plugin.addListener("registration", (res) => {
      const token = res && res.value;
      if (!token) return;
      registered = true;
      registerPushToken({
        apiBase, fetchImpl, token,
        deviceId: deviceUniqueId(storage),
        accessToken: accessTokenProvider() || null,
        log,
      });
    });
    plugin.addListener("registrationError", (err) => {
      log.info(`[push] disabled: FCM registration error (${(err && err.error) || "unknown"} — google-services.json missing at build time?)`);
    });

    try {
      await plugin.register();
    } catch (e) {
      log.info(`[push] disabled: FCM register() failed (${e && e.message})`);
      return { enabled: false, reason: "register-failed" };
    }
    return { enabled: true, registered: () => registered };
  }
  return { start };
}
