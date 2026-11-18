// CL-APP-09 (owner ruling): user-defined condition sets (自訂題材) attached to
// OFFICIAL spots. A member may fork an official genre template (or build from
// scratch) into a PERSONAL condition set on any official place:
//   - duplicates allowed: the same official template may be forked into
//     multiple sets, other members' ideas may be re-created freely, and names
//     are NOT deduplicated (owner ruling: 題材可重複、命名不阻擋重名);
//   - caps (owner ruling, 追加2 ① + FINAL 收斂): every place carries up to
//     5 sets per user (paid AND free), owner unlimited, and there is NO
//     system-wide total cap for paid; the free tier is bounded by a
//     5-set TOTAL plus a 5-per-day add throttle (owner wording:
//     「Free 的總量5組，每天新增的上限也是5組」 — the daily add limit
//     applies ONLY to free; paid/owner are never throttled by it):
//       per official place  5 sets per user (paid / free / free-as-paid)
//       free total          5 sets across all places
//       daily add           5 new sets per UTC day (FREE ONLY — paid ∞)
//       owner               unlimited
//     over-cap is FAIL-CLOSED 403 with the concrete numbers + upgrade
//     guidance (the client renders the gray upgrade card);
//   - fork semantics: template_id + base_rev (the official contract's
//     revision at fork time) + base_conditions (the mappable weather subset
//     snapshotted at fork time). When the official contract's revision moves
//     past base_rev the fork is honestly marked 「官方已更新可同步」; the
//     client diff view compares the fork's values against base_conditions,
//     and thresholds beyond ±30% of the official value are WARNED (never
//     blocked — owner ruling 超出提示但不硬擋);
//   - judgment: the SAME condition engine (notify.js customHourMatches /
//     findNextCustomWindow) computed at READ time over the already-published
//     KV grid record (v1:evals:<place_id> rec.hourly) — zero extra upstream
//     weather API calls, identical anatomy to official subject rows.
//   - verdict cache (steer 2 + 追加2 ④): read-time verdicts are cached in KV
//     keyed by hash(conditions)+place_id+forecast-generation, SHARED across
//     users with identical condition sets. Worker KV allows 1000 writes/day
//     TOTAL, so writes are metered per user per UTC day in D1 (metering costs
//     zero KV writes). Over-budget requests still compute and answer normally
//     — only the KV write is skipped; the user never sees a difference.
//   - batch read (steer 2 + 追加2 ③): the card list page consumes ONE batch
//     endpoint for all of the user's custom sets — never per-card-per-set
//     calls. The payload is PAGINATED: at most MAX_BATCH_PLACES places and
//     MAX_BATCH_SETS sets per response, with a next_cursor to page through
//     (client lazy-loads visible cards first, see draft/assets/subject-sets-list.js).
// Results only — thresholds/formulas never leave this module's own domain,
// and user-facing copy is tri-lingual everywhere.
import { validateCustomConditions, parseCustomConditions, customHourMatches, hourInWindow } from "./notify.js";
import { dominantFailWord, NAME_MAX_LEN } from "./custom-places.js";

export const CAP_PLACE = 5;       // per-place cap — paid AND free (owner ∞)
export const CAP_TOTAL_FREE = 5;  // final ruling: free TOTAL across all places
export const DAILY_ADD_LIMIT = 5; // final ruling: max 5 NEW sets per UTC day (FREE tier only)
export const THIRTY_PCT = 0.3;
export const NAME_LEN_LIMIT = NAME_MAX_LEN;

// 追加2 ③/④ limits. Each is owner-tunable via worker env vars so the numbers
// can move without a redeploy cycle.
export const DEFAULT_MAX_BATCH_PLACES = 20;   // places per batch response
export const DEFAULT_MAX_BATCH_SETS = 100;    // sets per batch response (20×5)
export const DEFAULT_MAX_KV_WRITES_USER_DAY = 40; // ≈25 users saturate 1000/day
export const MAX_IDS_PER_BATCH_REQUEST = 200; // URL sanity ceiling
export const VERDICT_CACHE_TTL_S = 6 * 3_600; // grid regen changes the key anyway

export const MESSAGES = {
  place_cap: {
    "zh-TW": "此景點已達 5 組自訂題材上限（現有 {place} 組）；刪除一組後即可再新增。",
    "en": "This place is at its 5 custom-subject cap ({place} sets); delete one to add more.",
    "ja": "このスポットの自作題材上限（5件・現在{place}件）に達しました。削除すると追加できます。",
  },
  free_cap: {
    "zh-TW": "免費會員自訂題材全站總量 5 組（現有 {total} 組）、每日新增 5 組；升級 Premium 後每個景點 5 組、無總量上限。",
    "en": "Free members hold 5 custom-subject sets in TOTAL ({total} now) and can add 5 per day; Premium unlocks 5 per place with no total cap.",
    "ja": "無料會員は自作題材の合計5件（現在{total}件）・1日5件まで追加可能です。Premiumなら1か所5件・合計上限なし。",
  },
  total_cap: {
    "zh-TW": "免費會員自訂題材全站總量 5 組（現有 {total} 組）——刪除一組或升級 Premium 後即可再新增。",
    "en": "Free members hold 5 custom-subject sets in TOTAL ({total} now) — delete one or upgrade Premium to add more.",
    "ja": "無料會員は自作題材の合計上限5件（現在{total}件）です。削除するかPremiumにアップグレードすると追加できます。",
  },
  daily_add: {
    "zh-TW": "今日已新增 5 組自訂題材（每日上限 5 組）——明日再新增即可。",
    "en": "You added 5 custom-subject sets today (daily cap 5) — add more tomorrow.",
    "ja": "本日すでに自作題材を5件追加しました（1日の上限5件）。明日以降に追加できます。",
  },
  name_long: {
    "zh-TW": "題材名稱上限 60 字。",
    "en": "Subject name is limited to 60 characters.",
    "ja": "題材名は60字以内です。",
  },
};

function pickMsg(key) { return MESSAGES[key] || null; }

function json(req, status, body) {
  const origin = req.headers.get("Origin") || "";
  const h = {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "Access-Control-Allow-Origin": origin === "https://chaselights.app" ? origin : "null",
    "Vary": "Origin",
  };
  return new Response(JSON.stringify(body), { status, headers: h });
}

async function requireSession(req, env) {
  const { getSession } = await import("./auth.js");
  const session = await getSession(req, env);
  return session && session.sub ? session : null;
}

// Owner ruling 追加2 ① + FINAL caps ruling (合流收斂 2026-11-18 + 微調: the
// daily-add throttle is FREE-ONLY — owner re-worded it as 「Free 的總量5組，
// 每天新增的上限也是5組」, so paid/owner are never day-throttled): per place
// 5 sets for EVERY member level (paid AND free), owner unlimited; the free
// trial is bounded by a TOTAL of 5 sets system-wide plus a 5-per-day add
// throttle (anti-churn, same shape as the custom-places daily brake).
// Paid has NO total cap and NO daily add cap (追加2 ① cancelled the 20-set total).
export function capPlaceFor(level, freeAsPaid) {
  if (level === "owner") return Infinity;
  return CAP_PLACE;
}
export function capTotalFor(level, freeAsPaid) {
  if (level === "owner" || level === "paid" || freeAsPaid) return Infinity;
  return CAP_TOTAL_FREE;
}
// The daily-add throttle applies ONLY to the free tier (same predicate as the
// total cap: paid / owner / free-as-paid are never throttled).
export function dailyAddCappedFor(level, freeAsPaid) {
  return capTotalFor(level, freeAsPaid) !== Infinity;
}
// JSON-safe caps payload — Infinity serializes as null and every client reads
// null as 「無上限」 (the custom-places quota convention, one source of truth).
export function capsPayload(level, freeAsPaid) {
  const place = capPlaceFor(level, freeAsPaid);
  const total = capTotalFor(level, freeAsPaid);
  return { place: place === Infinity ? null : place, total: total === Infinity ? null : total };
}
// UTC date key for the daily-add throttle (created_at is 'YYYY-MM-DD HH:MM:SS')
function utcDayKey() { return new Date().toISOString().slice(0, 10); }

// ---------------------------------------------------------------------------
// ±30% fork-tolerance audit (owner ruling: 超出提示但不硬擋). Compares each
// mappable cc field against the official snapshot's mapped value; a set
// threshold beyond ±30% of the official value is reported as a WARNING (the
// write still succeeds). Metrics without a mapped official counterpart are
// never warned (the fork starts from scratch for them).
// ---------------------------------------------------------------------------
export function thirtyPercentWarnings(cc, baseCc) {
  const out = [];
  if (!cc || !baseCc) return out;
  for (const key of ["cloud_low_max", "cloud_mid_max", "cloud_high_max", "precip_max_mmh", "visibility_min_km", "wind_max_ms"]) {
    const mine = cc[key], base = baseCc[key];
    if (typeof mine !== "number" || typeof base !== "number" || base === 0) continue;
    if (Math.abs(mine - base) > THIRTY_PCT * Math.abs(base)) {
      out.push({ metric: key, official: base, value: mine });
    }
  }
  return out;
}

async function countsFor(env, uid, placeId) {
  const one = await env.DB.prepare(
    "SELECT COUNT(*) AS n FROM custom_subject_sets WHERE user_id = ?1 AND place_id = ?2"
  ).bind(uid, placeId).first();
  const all = await env.DB.prepare(
    "SELECT COUNT(*) AS n FROM custom_subject_sets WHERE user_id = ?1"
  ).bind(uid).first();
  return { place: (one && one.n) || 0, total: (all && all.n) || 0 };
}

function setRowToApi(row) {
  return {
    id: row.id, placeId: row.place_id, name: row.name,
    templateId: row.template_id || null, baseRev: row.base_rev || null,
    baseConditions: parseCustomConditions(row.base_conditions) || {},
    conditions: parseCustomConditions(row.conditions) || {},
    months: parseCustomConditions(row.months) || [],
    createdAt: row.created_at || null, updatedAt: row.updated_at || null,
  };
}

// ---------------------------------------------------------------------------
// GET /subject_sets?place_id=X — the caller's sets for a place + honest quota
// numbers (concrete counts drive the UI's cap line and gray upgrade card).
// counts.total is INFORMATIONAL only (追加2 ① removed the total cap).
// ---------------------------------------------------------------------------
export async function handleSubjectSetsList(req, env, url) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const placeId = url.searchParams.get("place_id") || "";
  const user = await env.DB.prepare(
    "SELECT level FROM users WHERE device_id = ?1"
  ).bind(uid).first();
  if (!user) return json(req, 401, { error: "session user not found" });
  const level = user.level || "free";
  const freeAsPaid = await freeAsPaidFlag(env);
  let rows;
  if (placeId) {
    rows = await env.DB.prepare(
      "SELECT id, user_id, place_id, name, template_id, base_rev, base_conditions, conditions, months, created_at, updated_at FROM custom_subject_sets WHERE user_id = ?1 AND place_id = ?2 ORDER BY created_at DESC"
    ).bind(uid, placeId).all();
  } else {
    rows = await env.DB.prepare(
      "SELECT id, user_id, place_id, name, template_id, base_rev, base_conditions, conditions, months, created_at, updated_at FROM custom_subject_sets WHERE user_id = ?1 ORDER BY created_at DESC"
    ).bind(uid).all();
  }
  const counts = await countsFor(env, uid, placeId);
  // free quota surface for the 我的題材 library: total budget + today's add usage
  const capTotal = capTotalFor(level, freeAsPaid);
  if (capTotal !== Infinity) {
    const dayStart = utcDayKey() + " 00:00:00";
    const today = await env.DB.prepare(
      "SELECT COUNT(*) AS n FROM custom_subject_sets WHERE user_id = ?1 AND created_at >= ?2"
    ).bind(uid, dayStart).first();
    counts.daily_used = (today && today.n) || 0;
  }
  const caps = capsPayload(level, freeAsPaid);
  if (capTotal !== Infinity) {
    caps.free_total = capTotal;
    caps.daily_add = DAILY_ADD_LIMIT;
  }
  return json(req, 200, {
    ok: true, level,
    sets: (rows.results || []).map(setRowToApi),
    counts, caps,
  });
}

async function freeAsPaidFlag(env) {
  if (env.MEMBER_FREE_AS_PAID === "1") return true;
  if (env.MEMBER_FREE_AS_PAID === "0") return false;
  try {
    const v = await env.EVALS.get("v1:flags:member", "json");
    return !!(v && v.freeAsPaid === true);
  } catch { return false; }
}

// ---------------------------------------------------------------------------
// POST /subject_sets — create (duplicates of official templates / other
// members' sets are ALLOWED; duplicate names are allowed). The per-place quota
// check is the owner-ruled fail-closed 403 with concrete numbers; there is no
// total-cap check anymore (追加2 ①).
// Body: { place_id, name, template_id?, base_rev?, base_conditions?,
//         conditions?, months? } — months rides inside conditions too, but the
// panel's multi-select writes it as a top-level field; both are accepted.
// ---------------------------------------------------------------------------
export async function handleSubjectSetCreate(req, env) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const user = await env.DB.prepare(
    "SELECT level FROM users WHERE device_id = ?1"
  ).bind(uid).first();
  if (!user) return json(req, 401, { error: "session user not found" });
  const level = user.level || "free";
  let body = null;
  try { body = await req.json(); } catch { body = null; }
  if (!body || typeof body !== "object") return json(req, 400, { error: "JSON body required" });
  const placeId = typeof body.place_id === "string" ? body.place_id : (typeof body.placeId === "string" ? body.placeId : "");
  if (!placeId || !/^[\w-]+$/.test(placeId)) return json(req, 400, { error: "place_id required" });
  const name = typeof body.name === "string" ? body.name.trim() : "";
  if (!name) return json(req, 400, { error: "name required" });
  if (name.length > NAME_LEN_LIMIT) {
    return json(req, 400, { error: "name too long", message: pickMsg("name_long") });
  }
  const freeAsPaid = await freeAsPaidFlag(env);
  const capPlace = capPlaceFor(level, freeAsPaid);
  const caps = capsPayload(level, freeAsPaid);
  const counts = await countsFor(env, uid, placeId);
  if (level !== "owner") {
    // FINAL ruling (微調): daily add throttle is FREE-ONLY — paid/owner are
    // never day-throttled (owner: 「Free 的總量5組，每天新增的上限也是5組」).
    // counts today's CREATED rows (created_at 'YYYY-MM-DD HH:MM:SS' UTC).
    if (dailyAddCappedFor(level, freeAsPaid)) {
      const dayStart = utcDayKey() + " 00:00:00";
      const today = await env.DB.prepare(
        "SELECT COUNT(*) AS n FROM custom_subject_sets WHERE user_id = ?1 AND created_at >= ?2"
      ).bind(uid, dayStart).first();
      const dailyAdds = (today && today.n) || 0;
      if (dailyAdds >= DAILY_ADD_LIMIT) {
        return json(req, 403, {
          error: "daily add limit reached",
          reason: "daily_add",
          message: Object.assign({}, pickMsg("daily_add"), { _t: "daily_add" }),
          counts, caps,
        });
      }
    }
    // free trial: TOTAL cap across all places (paid/owner unlimited)
    const capTotal = capTotalFor(level, freeAsPaid);
    if (capTotal !== Infinity && counts.total >= capTotal) {
      return json(req, 403, {
        error: "free total cap reached",
        reason: "total_cap",
        message: Object.assign({}, pickMsg("total_cap"), { _t: "total_cap" }),
        counts, caps,
      });
    }
  }
  if (counts.place >= capPlace) {
    return json(req, 403, {
      error: "per-place cap reached",
      reason: "place_cap",
      message: Object.assign({}, pickMsg("place_cap"), { _t: "place_cap" }),
      counts, caps,
    });
  }
  const ccRes = validateCustomConditions(body.conditions != null ? body.conditions : body.customConditions);
  if (!ccRes.ok) return json(req, 400, { error: ccRes.error });
  let cc = ccRes.cc || {};
  // top-level months multi-select (panel sends it explicitly)
  const mRes = validateCustomConditions(body.months != null ? { months: body.months } : null);
  if (!mRes.ok) return json(req, 400, { error: mRes.error });
  const months = (mRes.cc && mRes.cc.months) || (cc && cc.months) || [];
  if (cc && cc.months) delete cc.months;
  const templateId = typeof body.template_id === "string" && body.template_id ? body.template_id : null;
  const baseRev = Number.isInteger(body.base_rev) ? body.base_rev : (Number(body.base_rev) || null);
  const baseCc = parseCustomConditions(body.base_conditions != null ? body.base_conditions : body.baseConditions) || {};
  const warnings = thirtyPercentWarnings(cc, Object.keys(baseCc).length ? baseCc : null);
  const id = randomId();
  const now = new Date().toISOString().replace("T", " ").slice(0, 19);
  await env.DB.prepare(
    "INSERT INTO custom_subject_sets (id, user_id, place_id, name, template_id, base_rev, base_conditions, conditions, months, created_at, updated_at) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?10)"
  ).bind(id, uid, placeId, name, templateId, baseRev, JSON.stringify(baseCc), JSON.stringify(cc), JSON.stringify(months), now).run();
  const after = await countsFor(env, uid, placeId);
  return json(req, 200, {
    ok: true, id,
    set: { id, placeId, name, templateId, baseRev, baseConditions: baseCc, conditions: cc, months, createdAt: now, updatedAt: now },
    counts: after, caps, warnings,
  });
}

// ---------------------------------------------------------------------------
// PATCH /subject_sets/<id> — name / months / conditions / fork refresh
// (template sync updates base_rev + base_conditions). ±30% warnings ride the
// success response (never a block).
// ---------------------------------------------------------------------------
export async function handleSubjectSetItem(req, env, setId) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  if (req.method === "DELETE") {
    const row = await env.DB.prepare(
      "SELECT id FROM custom_subject_sets WHERE id = ?1 AND user_id = ?2"
    ).bind(setId, uid).first();
    if (!row) return json(req, 404, { error: "set not found" });
    await env.DB.prepare("DELETE FROM custom_subject_sets WHERE id = ?1").bind(setId).run();
    return json(req, 200, { ok: true, deleted: setId });
  }
  if (req.method !== "PATCH") return json(req, 405, { error: "method not allowed" });
  const row = await env.DB.prepare(
    "SELECT id, user_id, place_id, name, template_id, base_rev, base_conditions, conditions, months, created_at, updated_at FROM custom_subject_sets WHERE id = ?1"
  ).bind(setId).first();
  // another member's set simply does not exist for you (same CRUD rule)
  if (!row || row.user_id !== uid) return json(req, 404, { error: "set not found" });
  let body = null;
  try { body = await req.json(); } catch { body = null; }
  if (!body || typeof body !== "object") return json(req, 400, { error: "JSON body required" });
  const updates = [], binds = [];
  let warnings = [];
  let baseCc = parseCustomConditions(row.base_conditions) || {};
  let cc = parseCustomConditions(row.conditions) || {};
  let months = parseCustomConditions(row.months) || [];
  if (body.name !== undefined) {
    const name = String(body.name || "").trim();
    if (!name) return json(req, 400, { error: "name required" });
    if (name.length > NAME_LEN_LIMIT) return json(req, 400, { error: "name too long", message: pickMsg("name_long") });
    updates.push("name = ?2"); binds.push(name);
  }
  if (body.conditions !== undefined || body.customConditions !== undefined) {
    const ccRes = validateCustomConditions(body.conditions != null ? body.conditions : body.customConditions);
    if (!ccRes.ok) return json(req, 400, { error: ccRes.error });
    cc = ccRes.cc || {};
  }
  if (body.months !== undefined) {
    const mRes = validateCustomConditions(body.months != null ? { months: body.months } : null);
    if (!mRes.ok) return json(req, 400, { error: mRes.error });
    months = (mRes.cc && mRes.cc.months) || [];
  }
  // fork refresh (官方同步): template refreshes the snapshot + revision so the
  // 「官方已更新可同步」 marker clears; 重設回官方 keeps base and rewrites
  // conditions to the snapshot (both land here as explicit fields).
  if (body.base_conditions !== undefined || body.baseConditions !== undefined || body.base_rev !== undefined) {
    baseCc = parseCustomConditions(body.base_conditions != null ? body.base_conditions : body.baseConditions) || baseCc;
    const baseRev = Number.isInteger(body.base_rev) ? body.base_rev : (body.base_rev != null ? (Number(body.base_rev) || null) : null);
    updates.push("base_rev = ?3"); binds.push(baseRev);
    if (cc && Object.keys(cc).length) warnings = thirtyPercentWarnings(cc, Object.keys(baseCc).length ? baseCc : null);
  }
  if (body.reset_to_official === true) {
    cc = Object.assign({}, baseCc);
  }
  if (cc && cc.months) delete cc.months;
  if (body.conditions !== undefined || body.customConditions !== undefined || body.reset_to_official === true) {
    if (Object.keys(baseCc).length) warnings = thirtyPercentWarnings(cc, baseCc);
    updates.push("conditions = ?4"); binds.push(JSON.stringify(cc));
  }
  updates.push("months = ?5"); binds.push(JSON.stringify(months));
  if (!updates.some(u => u.startsWith("name") || u.startsWith("base_rev") || u.startsWith("conditions"))) {
    // months-only change still lands via the unconditional months push below
  }
  const now = new Date().toISOString().replace("T", " ").slice(0, 19);
  updates.push("updated_at = ?6"); binds.push(now);
  const sql = `UPDATE custom_subject_sets SET ${updates.join(", ")} WHERE id = ?1`;
  await env.DB.prepare(sql).bind(...binds).run();
  const fresh = await env.DB.prepare(
    "SELECT id, user_id, place_id, name, template_id, base_rev, base_conditions, conditions, months, created_at, updated_at FROM custom_subject_sets WHERE id = ?1"
  ).bind(setId).first();
  return json(req, 200, { ok: true, set: setRowToApi(fresh), warnings });
}

// ---------------------------------------------------------------------------
// READ-TIME judgment (owner spec §5 + steers): the user's sets are evaluated
// against the ALREADY-published KV grid record (v1:evals:<place_id>.hourly —
// the same distilled rows the official pipeline and notify cron read). Zero
// new upstream weather calls. Verdicts are memoized in KV by
// hash(conditions)+place_id+forecast-generation so users with identical
// condition sets share cache entries (追加2 ④: writes metered per user/day).
// Response per set mirrors the official subject anatomy:
//   { id, name, months, tier: rec|no|pending, window, failReason,
//     days: [{local_date, state: GUIDANCE_SATISFIED, hours}] }
// ---------------------------------------------------------------------------

// Stable short hash of a condition blob (canonical JSON, sorted keys).
export function verdictCacheHash(cc, months) {
  const canon = (v) => {
    if (Array.isArray(v)) return v.map(canon);
    if (v && typeof v === "object") {
      return Object.keys(v).sort().reduce((o, k) => (o[k] = canon(v[k]), o), {});
    }
    return v;
  };
  const s = JSON.stringify({ c: canon(cc || {}), m: (months || []).slice().sort((a, b) => a - b) });
  return crypto.subtle.digest("SHA-256", new TextEncoder().encode(s)).then((buf) =>
    [...new Uint8Array(buf)].slice(0, 8).map((b) => b.toString(16).padStart(2, "0")).join("")
  );
}

// Cache key folds the FORECAST GENERATION in: a new published grid
// (generated_at) produces fresh keys automatically, so stale verdicts can
// never be served and no janitor job is needed.
export function verdictCacheKey(placeId, generatedAt, hash) {
  const gen = String(generatedAt || "none").replace(/[^0-9TZ]/g, "").slice(0, 16) || "none";
  return `v1:ssc:${placeId}:${gen}:${hash}`;
}

// 追加2 ④: per-user daily KV-write budget, metered in D1 so the metering
// itself costs ZERO KV writes. Charge atomically:
//   INSERT ... ON CONFLICT DO UPDATE SET writes = writes + n
//   WHERE writes + n <= cap RETURNING writes
// A returned row means budget was charged; no row means over budget for the
// UTC day (writes resume next day). Transparent: callers just skip the write.
export async function chargeKvWrites(env, uid, n) {
  const cap = Number(env.SS_KV_WRITES_USER_DAY) || DEFAULT_MAX_KV_WRITES_USER_DAY;
  const day = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  try {
    const row = await env.DB.prepare(
      "INSERT INTO ss_kv_budget (user_id, day, writes) VALUES (?1, ?2, ?3) ON CONFLICT(user_id, day) DO UPDATE SET writes = writes + ?3 WHERE writes + ?3 <= ?4 RETURNING writes"
    ).bind(uid, day, n, cap).first();
    return !!row; // row present = budget charged, writes allowed
  } catch {
    return false; // metering failure must NEVER block a read (fail-open for reads)
  }
}

export async function evaluatePlaceSets(env, uid, placeId, rows) {
  let rec = null;
  try { rec = await env.EVALS.get(`v1:evals:${placeId}`, "json"); } catch { rec = null; }
  const hourly = rec && Array.isArray(rec.hourly) ? rec.hourly : [];
  const generatedAt = rec ? (rec.generated_at || null) : null;
  const verdicts = [];
  const misses = [];
  for (const row of rows) {
    const cc = parseCustomConditions(row.conditions) || {};
    const months = parseCustomConditions(row.months) || [];
    let key = null;
    if (hourly.length) {
      const hash = await verdictCacheHash(cc, months);
      key = verdictCacheKey(placeId, generatedAt, hash);
      let cached = null;
      try { cached = await env.EVALS.get(key, "json"); } catch { cached = null; }
      if (cached && typeof cached === "object") {
        verdicts.push(Object.assign({ id: row.id, name: row.name }, cached));
        continue;
      }
    }
    const verdict = evaluateSet(row, hourly);
    verdicts.push(verdict);
    if (key) misses.push({ key, verdict: { tier: verdict.tier, window: verdict.window, failReason: verdict.failReason, days: verdict.days } });
  }
  // incremental charge, one D1 upsert per write (metering costs ZERO KV
  // writes): once the day's budget is exhausted the remaining writes are
  // skipped QUIETLY — results above are already computed and returned, the
  // user sees no difference (追加2 ④: transparent to the user).
  for (const m of misses) {
    if (!(await chargeKvWrites(env, uid, 1))) break;
    try { await env.EVALS.put(m.key, JSON.stringify(m.verdict), { expirationTtl: VERDICT_CACHE_TTL_S }); } catch { /* cache write is best-effort */ }
  }
  return { generatedAt, verdicts };
}

// ---------------------------------------------------------------------------
// GET /subject_sets/eval?place_id=X — per-place read (subject panel / create
// flow).
// ---------------------------------------------------------------------------
export async function handleSubjectSetsEval(req, env, url) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const placeId = url.searchParams.get("place_id") || "";
  if (!placeId || !/^[\w-]+$/.test(placeId)) return json(req, 400, { error: "place_id required" });
  const rows = await env.DB.prepare(
    "SELECT id, user_id, place_id, name, template_id, base_rev, base_conditions, conditions, months, created_at, updated_at FROM custom_subject_sets WHERE user_id = ?1 AND place_id = ?2 ORDER BY created_at DESC"
  ).bind(uid, placeId).all();
  const sets = rows.results || [];
  if (!sets.length) return json(req, 200, { ok: true, place_id: placeId, sets: [], generatedAt: null });
  const { generatedAt, verdicts } = await evaluatePlaceSets(env, uid, placeId, sets);
  return json(req, 200, {
    ok: true, place_id: placeId, generatedAt,
    sets: verdicts,
  });
}

// ---------------------------------------------------------------------------
// GET /subject_sets/eval_batch?ids=a,b,c…&cursor=0 — the card list page's ONE
// read for all of the user's custom sets (steer 2; never per-card-per-set).
// 追加2 ③: the payload is PAGINATED — at most MAX_BATCH_PLACES places and
// MAX_BATCH_SETS sets per response; next_cursor carries the resume point so
// the client can lazy-load the remaining (off-screen) cards.
//   - ids: comma-separated place_ids, ≤ MAX_IDS_PER_BATCH_REQUEST per request
//   - cursor: offset into the VALIDATED id list (default 0)
// A single place whose sets exceed the whole page budget is truncated
// (truncated: true) rather than looping forever.
// ---------------------------------------------------------------------------
export async function handleSubjectSetsEvalBatch(req, env, url) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const rawIds = (url.searchParams.get("ids") || "").split(",").map((s) => s.trim()).filter(Boolean);
  const ids = [...new Set(rawIds)].filter((p) => /^[\w-]+$/.test(p));
  if (!ids.length) return json(req, 400, { error: "ids required" });
  if (ids.length > MAX_IDS_PER_BATCH_REQUEST) {
    return json(req, 400, { error: `too many place ids (max ${MAX_IDS_PER_BATCH_REQUEST} per request)` });
  }
  let cursor = Number(url.searchParams.get("cursor")) || 0;
  if (!Number.isInteger(cursor) || cursor < 0 || cursor >= ids.length) cursor = 0;
  const maxPlaces = Math.max(1, Number(env.SS_BATCH_MAX_PLACES) || DEFAULT_MAX_BATCH_PLACES);
  const maxSets = Math.max(1, Number(env.SS_BATCH_MAX_SETS) || DEFAULT_MAX_BATCH_SETS);
  const results = [];
  let setBudget = maxSets;
  let nextCursor = null;
  const end = Math.min(cursor + maxPlaces, ids.length);
  for (let i = cursor; i < end; i++) {
    const placeId = ids[i];
    const rows = await env.DB.prepare(
      "SELECT id, user_id, place_id, name, template_id, base_rev, base_conditions, conditions, months, created_at, updated_at FROM custom_subject_sets WHERE user_id = ?1 AND place_id = ?2 ORDER BY created_at DESC"
    ).bind(uid, placeId).all();
    const sets = rows.results || [];
    if (!sets.length) {
      results.push({ place_id: placeId, generatedAt: null, sets: [] });
    } else if (sets.length > setBudget) {
      if (results.length === 0 && setBudget === maxSets) {
        // one place alone exceeds the whole page budget: truncate honestly
        // instead of an infinite cursor loop
        const { generatedAt, verdicts } = await evaluatePlaceSets(env, uid, placeId, sets.slice(0, setBudget));
        results.push({ place_id: placeId, generatedAt, sets: verdicts, truncated: true });
      } else {
        // stop BEFORE this place; the next call resumes at it
        nextCursor = i;
        break;
      }
    } else {
      const { generatedAt, verdicts } = await evaluatePlaceSets(env, uid, placeId, sets);
      setBudget -= verdicts.length;
      results.push({ place_id: placeId, generatedAt, sets: verdicts });
    }
    if (i === end - 1 && i + 1 < ids.length) nextCursor = i + 1;
  }
  return json(req, 200, {
    ok: true,
    page: { cursor, places: results.length, next_cursor: nextCursor, total_ids: ids.length },
    results,
  });
}

export function evaluateSet(row, hourly) {
  const cc = parseCustomConditions(row.conditions) || {};
  const months = parseCustomConditions(row.months) || [];
  if (months.length) cc.months = months;
  if (!hourly.length) {
    return { id: row.id, name: row.name, months, tier: "pending", window: null, failReason: null, days: [] };
  }
  // per-day rollup in the SAME anatomy as official subject rows: hours that
  // match the engine (month window + parameter blob) form the day's hours.
  const byDay = new Map();
  for (const r of hourly) {
    if (!r || typeof r.local_date !== "string" || typeof r.hour !== "string") continue;
    if (months.length && !months.includes(Number(r.local_date.slice(5, 7)))) continue;
    // the SAME engine semantics as findNextCustomWindow: the set's own time
    // window (HH:MM, midnight wrap allowed) gates the hour too
    if (!hourInWindow(r.hour, cc.window_start, cc.window_end)) continue;
    if (!customHourMatches(r.values, cc)) continue;
    if (!byDay.has(r.local_date)) byDay.set(r.local_date, []);
    byDay.get(r.local_date).push(r.hour);
  }
  const days = [...byDay.keys()].sort().map((d) => {
    const hours = byDay.get(d).sort();
    return { local_date: d, state: "GUIDANCE_SATISFIED", hours };
  });
  // honest fail reason: a set month window with zero in-window hours in the
  // data horizon is an eligibility fact, never a weather word (patch-5 ④ rule).
  let failReason = null;
  if (!days.length) {
    const anyMonthHour = months.length
      ? hourly.some((r) => r && typeof r.local_date === "string" && months.includes(Number(r.local_date.slice(5, 7))))
      : true;
    failReason = months.length && !anyMonthHour ? "非適用月份" : dominantFailWord(hourly, cc);
  }
  const nextDay = days.find((d) => d.hours.length);
  const window = nextDay ? { local_date: nextDay.local_date, hours: nextDay.hours } : null;
  const tier = days.length ? "rec" : "no";
  return { id: row.id, name: row.name, months, tier, window, failReason, days };
}

// Same id shape as custom_places (base36, unguessable per user row).
function randomId() {
  return btoa(crypto.getRandomValues(new Uint8Array(16)).reduce((s, b) => s + String.fromCharCode(b), ""))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
