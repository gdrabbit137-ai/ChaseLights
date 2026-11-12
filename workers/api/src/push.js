// CL-APP-03: FCM HTTP v1 delivery for APP push (owner ruling: reminders are
// APP push, not Telegram). Service-account credentials come from the worker
// secret FCM_SERVICE_ACCOUNT_JSON (the JSON key file itself NEVER enters the
// repo). Fail-closed: when the secret is missing or malformed, sendPush
// returns { ok:false, skipped:'no-credentials' } and the caller just records
// an undelivered notify_log row — the cron never throws because of push.
//
// Auth: self-signed RS256 JWT -> OAuth2 token exchange (cached per isolate).

let cached = { access_token: null, exp: 0, project_id: null };

// test hook: clear the per-isolate OAuth token cache
export function _resetFcmTokenCache() { cached = { access_token: null, exp: 0, project_id: null }; }

function base64url(bytes) {
  return btoa(String.fromCharCode(...new Uint8Array(bytes)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function parseServiceAccount(raw) {
  let sa = null;
  try { sa = JSON.parse(raw); } catch { return null; }
  if (!sa || typeof sa !== "object") return null;
  if (!sa.client_email || !sa.private_key || !sa.project_id) return null;
  return sa;
}

export async function getFcmAccessToken(env, nowMs = Date.now()) {
  if (cached.access_token && nowMs < cached.exp - 60_000) {
    return { ok: true, access_token: cached.access_token, project_id: cached.project_id };
  }
  const raw = env && env.FCM_SERVICE_ACCOUNT_JSON;
  if (!raw) return { ok: false, skipped: "no-credentials", error: "FCM_SERVICE_ACCOUNT_JSON not set — push disabled (fail-closed)" };
  const sa = parseServiceAccount(raw);
  if (!sa) return { ok: false, skipped: "no-credentials", error: "FCM_SERVICE_ACCOUNT_JSON is not a valid service account JSON" };

  const enc = new TextEncoder();
  const header = base64url(enc.encode(JSON.stringify({ alg: "RS256", typ: "JWT" })));
  const now = Math.floor(nowMs / 1000);
  const claims = base64url(enc.encode(JSON.stringify({
    iss: sa.client_email, scope: "https://www.googleapis.com/auth/firebase.messaging",
    aud: "https://oauth2.googleapis.com/token", iat: now, exp: now + 3600,
  })));
  const pem = sa.private_key.replace(/-----BEGIN PRIVATE KEY-----/, "")
    .replace(/-----END PRIVATE KEY-----/, "").replace(/\s+/g, "");
  const der = Uint8Array.from(atob(pem), (c) => c.charCodeAt(0));
  let key;
  try {
    key = await crypto.subtle.importKey(
      "pkcs8", der.buffer, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]
    );
  } catch (e) {
    return { ok: false, skipped: "bad-credentials", error: `service account private_key unreadable: ${e && e.message}` };
  }
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, enc.encode(`${header}.${claims}`));
  const assertion = `${header}.${claims}.${base64url(sig)}`;

  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer", assertion,
    }),
  });
  const body = await res.json().catch(() => null);
  if (!res.ok || !body || !body.access_token) {
    return { ok: false, skipped: "auth-failed", error: (body && body.error_description) || `token endpoint HTTP ${res.status}` };
  }
  cached = { access_token: body.access_token, exp: nowMs + (body.expires_in || 3600) * 1000, project_id: sa.project_id };
  return { ok: true, access_token: body.access_token, project_id: sa.project_id };
}

// Send one notification to one FCM registration token. title/body are plain
// strings; message copy is produced by notify.buildMessage (results only).
export async function sendPush(env, token, { title, body }) {
  const auth = await getFcmAccessToken(env);
  if (!auth.ok) return auth; // fail-closed skip shape
  const res = await fetch(`https://fcm.googleapis.com/v1/projects/${auth.project_id}/messages:send`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${auth.access_token}` },
    body: JSON.stringify({
      message: {
        token,
        notification: { title, body },
        android: { notification: { channel_id: "chaselights_reminders" } },
      },
    }),
  });
  const resBody = await res.json().catch(() => null);
  if (!res.ok) {
    return { ok: false, error: (resBody && resBody.error && resBody.error.message) || `FCM HTTP ${res.status}` };
  }
  return { ok: true, name: resBody && resBody.name };
}
