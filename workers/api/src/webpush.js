// CL-API-03 skeleton: Web Push (VAPID). Interface only — key generation works,
// delivery intentionally NOT implemented this ticket (never silently fake-sent).

export async function generateVapidKeys() {
  const kp = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
  const priv = await crypto.subtle.exportKey("jwk", kp.privateKey);
  const pub = await crypto.subtle.exportKey("jwk", kp.publicKey);
  // RFC 8292 requires the public key as raw P-256 ("Base64URL-encoded x||y") for VAPID;
  // the JWK fields are kept so a follow-up ticket can re-derive any encoding.
  return {
    privateKeyJwk: priv,
    publicKeyJwk: pub,
    subject: "mailto:admin@chaselights.app",
    note: "store keys as worker secrets VAPID_PRIVATE_KEY / VAPID_PUBLIC_KEY",
  };
}

export async function sendWebPush(_env, _subscription, _payload) {
  throw new Error("NOT_IMPLEMENTED: VAPID web-push delivery ships in a follow-up ticket");
}
