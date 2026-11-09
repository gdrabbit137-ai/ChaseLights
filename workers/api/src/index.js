// ChaseLights API v1 (CL-API-01). Results only — no thresholds/condition formulas.
const ALLOWED_ORIGIN = "https://chaselights.app";
const RATE_LIMIT = { max: 60, windowMs: 60_000 };

function corsHeaders(req) {
  const origin = req.headers.get("Origin") || "";
  return {
    "Access-Control-Allow-Origin": origin === ALLOWED_ORIGIN ? origin : "null",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function json(req, status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders(req) },
  });
}

// naive per-isolate rate limiter (enough for v1; Redis-class precision later)
const buckets = new Map();
function rateLimited(ip, now) {
  const b = buckets.get(ip) || { count: 0, start: now };
  if (now - b.start > RATE_LIMIT.windowMs) { b.count = 0; b.start = now; }
  b.count += 1;
  buckets.set(ip, b);
  return b.count > RATE_LIMIT.max;
}

async function getUser(env, userId) {
  if (!userId) return null;
  await env.DB.prepare("INSERT INTO users (device_id) VALUES (?1) ON CONFLICT(device_id) DO NOTHING")
    .bind(userId).run();
  const row = await env.DB.prepare("SELECT device_id FROM users WHERE device_id = ?1").bind(userId).first();
  return row ? row.device_id : null;
}

async function handleFavorites(req, env, url) {
  let body = null;
  if (req.method === "POST") body = await req.json().catch(() => null);
  const userId = url.searchParams.get("userId") || (body && body.userId);
  if (!userId) return json(req, 400, { error: "userId required" });
  const uid = await getUser(env, userId);

  if (req.method === "GET") {
    const { results } = await env.DB.prepare(
      "SELECT place_id, created_at FROM favorites WHERE user_id = ?1 ORDER BY created_at DESC"
    ).bind(uid).all();
    return json(req, 200, { userId, favorites: results });
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

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/^\/api\/v1/, "");

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(request) });

    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    if (rateLimited(ip, Date.now())) return json(request, 429, { error: "rate limited" });

    if (path === "/health") {
      return json(request, 200, { ok: true, service: "chaselights-api", version: "v1", time: new Date().toISOString() });
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

    return json(request, 404, { error: "not found" });
  },
};
