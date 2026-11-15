// CL-DATA-70 (DESIGN-7 v2): unified UGC feedback channel — ratings / reports /
// comments in one table (migration 0008). Implements the owner-approved design
// (data/v2/audits/design-review-7-rating-system.md, head ddbf4bcfc) with the
// five ruling points as recommended:
//   ① L/P two axes on the place itself; no-chain members weigh P ×0.5
//   ② all comments (and reports) first-reviewed: pending → admin approve/reject
//   ③ 365-day half-life decay on ratings
//   ④ masked nickname display — never a raw account/device/email
//   ⑤ gray release behind FEEDBACK_ENABLED (KV / env flag), default OFF
// Tier computation (✓○✗ weather pipeline) is never touched by any of this.

const WEIGHTS = { t0: 0.5, t1: 1.0, t2: 1.5, t3: 2.0, tx: 3.0 };
const TRUST_LEVELS = new Set(Object.keys(WEIGHTS));
const REPORT_CATEGORIES = new Set([
  "data_wrong", "location_wrong", "condition_wrong",
  "seasonal_wrong", "place_gone", "other",
]);
const HALF_LIFE_DAYS = 365;   // ruling ③
const BAYES_K = 5;
const CLUSTER_CAP = 2;        // per-place per-cluster full-weight vote budget
const CLUSTER_PENALTY = 0.25; // 3rd+ same-cluster vote
const NO_CHAIN_P_FACTOR = 0.5;// ruling ① P-axis no-evidence penalty
const DISPLAY_MIN_EFF = 2.0;  // n_eff >= 2.0 ...
const DISPLAY_MIN_RAW = 3;    // ... and n_raw >= 3 or nothing is shown
const MAX_TEXT = 500;         // comment/report text
const MAX_FIX_SUGGEST = 300;  // report correction suggestion
const THROTTLE_MS = 90_000;   // <90s between submissions → flagged (fail-closed)
const T0_24H_VOTE_CAP = 3;    // T0 members: ≤3 aggregate-counting ratings / 24h
const VOTE_ROW_LIMIT = 500;   // per-place vote scan cap
const COMMENT_LIST_LIMIT = 20;
const AGGREGATE_LIMIT_MS = 30 * 86_400_000;

import { getSession } from "./auth.js";

function nowIso() {
  // D1 datetime('now') format "YYYY-MM-DD HH:MM:SS" (UTC)
  return new Date().toISOString().replace("T", " ").slice(0, 19);
}

function parseDbTime(s) {
  if (!s) return NaN;
  return Date.parse(String(s).replace(" ", "T") + "Z");
}

async function sha256Hex16(text) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(d).slice(0, 8)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// ip_cluster: /24 hash — the raw IP is never stored.
async function ipCluster(ip) {
  const parts = String(ip || "").split(".");
  const basis = parts.length === 4 ? `${parts[0]}.${parts[1]}.${parts[2]}` : String(ip || "unknown");
  return sha256Hex16(basis);
}

async function newId() {
  return btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(16))))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// ---------------------------------------------------------------------------
// Gray-release flag (ruling ⑤). Env override first (operators can force), KV
// second (owner flips it post-deploy), default OFF.
// ---------------------------------------------------------------------------
export async function feedbackEnabled(env) {
  if (env.FEEDBACK_ENABLED === "1") return true;
  if (env.FEEDBACK_ENABLED === "0") return false;
  try {
    const v = await env.EVALS.get("v1:flags:feedback", "json");
    return !!(v && v.enabled === true);
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Trust ladder (design §3.1) — computed from live member records at submission
// time; the resulting level+weight snapshot travels in the row payload.
//   T0 新會員  帳齡 <30天 或 有效提交 <3            → 0.5
//   T1 活躍    帳齡 ≥30天 且 近30天 ≥3筆有效提交    → 1.0
//   T2 有出片  T1 ＋ 出片鏈路近90天 ≥1             → 1.5
//      (photo_url 回報獲核可，或 push_invite 評分)
//   T3 資深    T2 ＋ 帳齡 ≥90天 且 提交 ≥20 且 跨 ≥3 地區 → 2.0
//   Tx 策展    owner/admin 認證                     → 3.0
// 有效提交 = feedback rows not rejected/flagged (pending still counts — it is
// not yet adjudicated; fail-closed demotes on reject, never on pending).
// ---------------------------------------------------------------------------
export async function computeTrustLevel(env, userId) {
  const user = await env.DB.prepare(
    "SELECT device_id, level, created_at FROM users WHERE device_id = ?1"
  ).bind(userId).first();
  if (user && (user.level === "admin" || user.level === "curator" || user.level === "owner")) {
    return { level: "tx", weight: WEIGHTS.tx };
  }
  const countValid = (windowSql) => env.DB.prepare(
    `SELECT COUNT(*) AS n FROM feedback WHERE user_id = ?1 AND status IN ('ok','pending')${windowSql}`
  ).bind(userId).first();

  const totalRow = await countValid("");
  const last30Row = await countValid(" AND created_at >= datetime('now','-30 days')");
  const total = totalRow ? totalRow.n : 0;
  const last30 = last30Row ? last30Row.n : 0;
  const ageDays = user && user.created_at
    ? Math.max(0, (Date.now() - parseDbTime(user.created_at)) / 86_400_000)
    : 0;

  if (ageDays < 30 || total < 3) return { level: "t0", weight: WEIGHTS.t0 };
  if (last30 < 3) return { level: "t0", weight: WEIGHTS.t0 };
  // T2 chain: an accepted report carrying photo_url, or a push_invite rating
  // (拍完邀評), within 90 days.
  const chainRow = await env.DB.prepare(
    `SELECT COUNT(*) AS n FROM feedback WHERE user_id = ?1 AND status IN ('ok','pending')
     AND created_at >= datetime('now','-90 days')
     AND ((type = 'report' AND json_extract(payload, '$.photo_url') IS NOT NULL)
       OR (type = 'rating' AND json_extract(payload, '$.source') = 'push_invite'))`
  ).bind(userId).first();
  const chain = chainRow ? chainRow.n : 0;
  if (chain < 1) return { level: "t1", weight: WEIGHTS.t1 };
  const regionRow = await env.DB.prepare(
    `SELECT COUNT(DISTINCT substr(place_id, 1, instr(place_id || '-', '-') - 1)) AS n
     FROM feedback WHERE user_id = ?1 AND status IN ('ok','pending')
     AND place_id IS NOT NULL AND type IN ('rating','report')`
  ).bind(userId).first();
  const regions = regionRow ? regionRow.n : 0;
  if (ageDays < 90 || total < 20 || regions < 3) return { level: "t2", weight: WEIGHTS.t2 };
  return { level: "t3", weight: WEIGHTS.t3 };
}

// ---------------------------------------------------------------------------
// Aggregation (design §3.3) — computed live per GET from the feedback rows
// (deterministic, idempotent: the same rows always yield the same numbers).
//   per ok rating:  decay = 0.5^(age_days/365);  cluster = same-cluster votes
//   beyond the 2nd → ×0.25;  w'_L = w×decay×cluster;  w'_P = w'_L×chain
//   chain = 1.0 when source≠'app' (push_invite) or trust snapshot ≥ t2 (the
//   ladder's 出片鏈路 marker), else 0.5  (design §1.2 no-evidence P penalty)
//   Bayesian shrink toward the global prior, k=5; display gate n_eff/n_raw.
// ---------------------------------------------------------------------------
export function aggregateFromRows(rows, prior, nowMs = Date.now()) {
  const mL = Number.isFinite(prior && prior.m_l) ? prior.m_l : 3;
  const mP = Number.isFinite(prior && prior.m_p) ? prior.m_p : 3;

  // Ascending time order so the cluster budget belongs to the earliest votes.
  const sorted = [...rows].sort((a, b) => parseDbTime(a.created_at) - parseDbTime(b.created_at));
  const clusterTally = new Map();
  let sumWL = 0, sumPL = 0, sumWP = 0, sumPP = 0, nRaw = 0, nLast30 = 0, p4plus = 0;

  for (const row of sorted) {
    let pl = {};
    try { pl = JSON.parse(row.payload || "{}"); } catch { pl = {}; }
    const ageDays = Math.max(0, (nowMs - parseDbTime(row.created_at)) / 86_400_000);
    const decay = Math.pow(0.5, ageDays / HALF_LIFE_DAYS);
    const w = typeof pl.weight === "number" && pl.weight > 0 ? pl.weight : WEIGHTS.t0;
    // votes whose decayed equivalent weight dropped below 3% are discarded
    if (w * decay < 0.03) continue;

    let cluster = 1;
    if (pl.ip_cluster || pl.device_hash) {
      const ipN = clusterTally.get("ip:" + pl.ip_cluster) || 0;
      const devN = clusterTally.get("dev:" + pl.device_hash) || 0;
      if (ipN >= CLUSTER_CAP || devN >= CLUSTER_CAP) cluster = CLUSTER_PENALTY;
      clusterTally.set("ip:" + pl.ip_cluster, ipN + 1);
      clusterTally.set("dev:" + pl.device_hash, devN + 1);
    }

    const chain = (pl.source && pl.source !== "app") ||
      (pl.trust_level && (pl.trust_level === "t2" || pl.trust_level === "t3" || pl.trust_level === "tx"))
      ? 1.0 : NO_CHAIN_P_FACTOR;

    const wL = w * decay * cluster;
    const wP = wL * chain;
    if (typeof pl.l === "number") { sumWL += wL; sumPL += wL * pl.l; }
    if (typeof pl.p === "number") { sumWP += wP; sumPP += wP * pl.p; }
    nRaw += 1;
    if (nowMs - parseDbTime(row.created_at) <= AGGREGATE_LIMIT_MS) nLast30 += 1;
    if (pl.p >= 4) p4plus += 1;
  }

  const sL = sumWL > 0 ? sumPL / sumWL : null;
  const sP = sumWP > 0 ? sumPP / sumWP : null;
  const nEff = sumWL;

  const lFinal = sL === null ? null : (sL * nEff + mL * BAYES_K) / (nEff + BAYES_K);
  const pFinal = sP === null ? null : (sP * nEff + mP * BAYES_K) / (nEff + BAYES_K);

  const insufficient = !(nEff >= DISPLAY_MIN_EFF && nRaw >= DISPLAY_MIN_RAW);
  return {
    lRaw: sL, pRaw: sP,
    // design §4.2/§8: below the display gate no score exists (null), the raw
    // means stay available for the daily batch / debugging.
    lFinal: insufficient ? null : lFinal,
    pFinal: insufficient ? null : pFinal,
    nRaw, nEff, nLast30,
    pctP4plus: nRaw > 0 ? p4plus / nRaw : null,
    insufficient,
  };
}

// Global Bayesian prior m_L/m_P: KV override (rating_prior written by the daily
// batch) when present, otherwise the plain mean over all ok ratings.
async function ratingPrior(env) {
  try {
    const kv = await env.EVALS.get("v1:rating_prior", "json");
    if (kv && Number.isFinite(kv.m_l) && Number.isFinite(kv.m_p)) return kv;
  } catch { /* KV not bound in some test envs */ }
  const row = await env.DB.prepare(
    `SELECT COUNT(*) AS n, AVG(json_extract(payload, '$.l')) AS ml, AVG(json_extract(payload, '$.p')) AS mp
     FROM feedback WHERE type = 'rating' AND status = 'ok'`
  ).bind().first();
  if (row && row.n > 0 && Number.isFinite(row.ml) && Number.isFinite(row.mp)) {
    return { m_l: row.ml, m_p: row.mp };
  }
  return null;
}

// ---------------------------------------------------------------------------
// Display masking (ruling ④): first two characters + "**"; nothing when the
// member never set a display name (clients then show 「攝影者·地區」). Raw
// account / device / email never leaves the API.
// ---------------------------------------------------------------------------
export function maskName(displayName) {
  const n = String(displayName || "").trim();
  if (!n) return null;
  return n.slice(0, 2) + "**";
}

function publicRating(row) {
  let pl = {};
  try { pl = JSON.parse(row.payload || "{}"); } catch { pl = {}; }
  return {
    id: row.id,
    placeId: row.place_id,
    l: pl.l, p: pl.p,
    shotDate: pl.shot_date || null,
    commentText: pl.comment_text || null,
    status: row.status,
    trustLevel: pl.trust_level || null,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

function reportCategoryOk(v) { return REPORT_CATEGORIES.has(v); }

// ---------------------------------------------------------------------------
// GET /api/v1/feedback            → aggregate for ?place_id=... (public shape,
//                                   masked comments, cold-start gate)
// GET /api/v1/feedback?mine=1     → my rating(s) (JWT session)
// ---------------------------------------------------------------------------
export async function handleFeedback(req, env, url) {
  const mine = url.searchParams.get("mine");
  const placeId = url.searchParams.get("place_id");

  if (mine === "1" || mine === "true") {
    const session = await requireMember(req, env);
    if (!session) return jsonErr(req, 401, "JWT session required");
    if (placeId) {
      const row = await env.DB.prepare(
        `SELECT id, user_id, place_id, type, status, payload, created_at, updated_at
         FROM feedback WHERE user_id = ?1 AND place_id = ?2 AND type = 'rating' LIMIT 1`
      ).bind(session.sub, placeId).first();
      return jsonOk(req, { rating: row ? publicRating(row) : null });
    }
    const { results } = await env.DB.prepare(
      `SELECT id, user_id, place_id, type, status, payload, created_at, updated_at
       FROM feedback WHERE user_id = ?1 AND type = 'rating' ORDER BY created_at DESC`
    ).bind(session.sub).all();
    return jsonOk(req, { ratings: (results || []).map(publicRating) });
  }

  if (!placeId) return jsonErr(req, 400, "place_id required");
  const { results } = await env.DB.prepare(
    `SELECT payload, created_at FROM feedback
     WHERE type = 'rating' AND place_id = ?1 AND status = 'ok'
     ORDER BY created_at ASC LIMIT ${VOTE_ROW_LIMIT}`
  ).bind(placeId).all();

  const prior = await ratingPrior(env);
  const agg = aggregateFromRows(results || [], prior);

  const commentRows = await env.DB.prepare(
    `SELECT f.payload, f.created_at, u.display_name FROM feedback f
     LEFT JOIN users u ON u.device_id = f.user_id
     WHERE f.type = 'comment' AND f.place_id = ?1 AND f.status = 'ok'
     ORDER BY f.created_at DESC LIMIT ${COMMENT_LIST_LIMIT}`
  ).bind(placeId).all();
  const comments = (commentRows.results || []).map((r) => {
    let pl = {};
    try { pl = JSON.parse(r.payload || "{}"); } catch { pl = {}; }
    return {
      message: pl.comment_text || "",
      maskedName: maskName(r.display_name),
      trustLevel: pl.trust_level || null,
      createdAt: r.created_at,
    };
  });
  const nCommentsRow = await env.DB.prepare(
    `SELECT COUNT(*) AS n FROM feedback WHERE type = 'comment' AND place_id = ?1 AND status = 'ok'`
  ).bind(placeId).first();

  return jsonOk(req, {
    placeId,
    insufficient: agg.insufficient,
    // Cold start (design §3.2): below the gate no score is exposed at all.
    lFinal: agg.insufficient ? null : agg.lFinal,
    pFinal: agg.insufficient ? null : agg.pFinal,
    lRaw: agg.lRaw, pRaw: agg.pRaw,
    nRaw: agg.nRaw, nEff: agg.nEff,
    nLast30: agg.nLast30,
    pctP4plus: agg.pctP4plus,
    nComments: nCommentsRow ? nCommentsRow.n : 0,
    comments,
  });
}

async function requireMember(req, env) {
  const session = await getSession(req, env);
  return session && session.sub ? session : null;
}

// Admin/curator/owner member level (users.level) gates the review surface —
// the site owner's account carries level='owner' and is the primary reviewer.
async function isAdmin(env, sub) {
  const row = await env.DB.prepare(
    "SELECT level FROM users WHERE device_id = ?1"
  ).bind(sub).first();
  return !!row && ["owner", "admin", "curator"].includes(row.level);
}

function jsonReply(req, status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "https://chaselights.app" },
  });
}

function jsonOk(req, body) {
  return jsonReply(req, 200, body);
}

function jsonErr(req, status, error, extra) {
  return jsonReply(req, status, extra ? { error, ...extra } : { error });
}

// ---------------------------------------------------------------------------
// POST/PUT /api/v1/feedback
//   rating  → upsert (one vote per (user, place); edit overwrites)
//   report  → create, status='pending' (owner ticket queue, never public)
//   comment → create, status='pending' (first-review, ruling ②)
// ---------------------------------------------------------------------------
export async function handleFeedbackSubmit(req, env, url) {
  const session = await requireMember(req, env);
  if (!session) return jsonErr(req, 401, "JWT session required");
  const body = await req.json().catch(() => null);
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return jsonErr(req, 400, "body required");
  }
  const type = body.type;
  if (!["rating", "report", "comment"].includes(type)) {
    return jsonErr(req, 400, "type must be rating, report or comment");
  }
  const uid = session.sub;
  const now = nowIso();

  // 90s throttle (design §2.4): any submission inside 90s of the previous one
  // is flagged, never silently accepted (fail-closed).
  const lastRow = await env.DB.prepare(
    "SELECT created_at FROM feedback WHERE user_id = ?1 ORDER BY created_at DESC LIMIT 1"
  ).bind(uid).first();
  const throttled = lastRow && lastRow.created_at &&
    (Date.now() - parseDbTime(lastRow.created_at)) < THROTTLE_MS;

  const trust = await computeTrustLevel(env, uid);
  const deviceHash = await sha256Hex16(uid);
  const ipHash = await ipCluster(req.headers.get("CF-Connecting-IP") || "unknown");

  let payload = {
    source: "app", trust_level: trust.level, weight: trust.weight,
    ip_cluster: ipHash, device_hash: deviceHash,
  };

  if (type === "rating") {
    const placeId = body.placeId || body.place_id;
    if (!placeId || typeof placeId !== "string") return jsonErr(req, 400, "placeId required");
    const l = body.l, p = body.p;
    for (const [k, v] of [["l", l], ["p", p]]) {
      if (!Number.isInteger(v) || v < 1 || v > 5) return jsonErr(req, 400, `${k} must be an integer 1..5`);
    }
    let shotDate = body.shotDate || body.shot_date || null;
    if (shotDate) {
      if (typeof shotDate !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(shotDate)) {
        return jsonErr(req, 400, "shot_date must be YYYY-MM-DD");
      }
      if (shotDate > nowIso().slice(0, 10)) return jsonErr(req, 400, "shot_date cannot be in the future");
    }
    const commentText = clampText(body.commentText || body.comment_text, MAX_TEXT);
    payload = { ...payload, l, p, shot_date: shotDate, comment_text: commentText };

    const existing = await env.DB.prepare(
      `SELECT id FROM feedback WHERE user_id = ?1 AND place_id = ?2 AND type = 'rating' LIMIT 1`
    ).bind(uid, placeId).first();
    const existingId = existing && existing.id;

    if (throttled) {
      // 90s rule: the vote is flagged, never silently accepted — and it must
      // NOT create a second (user, place) row (unique vote index).
      const pl = { ...payload, flag_reason: "time" };
      if (existingId) {
        await env.DB.prepare(
          `UPDATE feedback SET status = 'flagged', payload = ?2, updated_at = ?3 WHERE id = ?1`
        ).bind(existingId, JSON.stringify(pl), now).run();
        return jsonReply(req, 202, { ok: true, id: existingId, status: "flagged", flagReason: "time" });
      }
      const id = await insertFeedback(env, uid, placeId, "rating", "flagged", pl);
      return jsonReply(req, 202, { ok: true, id, status: "flagged", flagReason: "time" });
    }
    // T0 burst cap (design §2.4): ≤3 aggregate-counting ratings per 24h.
    if (trust.level === "t0") {
      const row = await env.DB.prepare(
        `SELECT COUNT(*) AS n FROM feedback WHERE user_id = ?1 AND type = 'rating'
         AND status = 'ok' AND created_at >= datetime('now','-1 day')`
      ).bind(uid).first();
      if (row && row.n >= T0_24H_VOTE_CAP) {
        const pl = { ...payload, flag_reason: "burst" };
        if (existingId) {
          await env.DB.prepare(
            `UPDATE feedback SET status = 'flagged', payload = ?2, updated_at = ?3 WHERE id = ?1`
          ).bind(existingId, JSON.stringify(pl), now).run();
          return jsonReply(req, 202, { ok: true, id: existingId, status: "flagged", flagReason: "burst" });
        }
        const id = await insertFeedback(env, uid, placeId, "rating", "flagged", pl);
        return jsonReply(req, 202, { ok: true, id, status: "flagged", flagReason: "burst" });
      }
    }

    if (existingId) {
      await env.DB.prepare(
        `UPDATE feedback SET status = 'ok', payload = ?2, updated_at = ?3 WHERE id = ?1`
      ).bind(existingId, JSON.stringify(payload), now).run();
      return jsonOk(req, {
        ok: true, upserted: "updated", id: existingId,
        rating: { placeId, l, p, shotDate, commentText, status: "ok", trustLevel: trust.level, weight: trust.weight },
      });
    }
    const id = await insertFeedback(env, uid, placeId, "rating", "ok", payload);
    return jsonOk(req, {
      ok: true, upserted: "created", id,
      rating: { placeId, l, p, shotDate, commentText, status: "ok", trustLevel: trust.level, weight: trust.weight },
    });
  }

  if (type === "report") {
    const placeId = body.placeId || body.place_id;
    if (!placeId || typeof placeId !== "string") return jsonErr(req, 400, "placeId required");
    const category = body.reportCategory || body.report_category;
    if (!reportCategoryOk(category)) {
      return jsonErr(req, 400, "report_category must be one of data_wrong, location_wrong, condition_wrong, seasonal_wrong, place_gone, other");
    }
    const text = clampText(body.commentText || body.comment_text, MAX_TEXT);
    if (!text) return jsonErr(req, 400, "comment_text (說明) required for reports");
    const fix = clampText(body.fixSuggest || body.fix_suggest, MAX_FIX_SUGGEST);
    const photoUrl = clampText(body.photoUrl || body.photo_url, 2000);
    if (photoUrl && !/^https:\/\//.test(photoUrl)) return jsonErr(req, 400, "photo_url must be an https URL");
    payload = { ...payload, report_category: category, comment_text: text, fix_suggest: fix, photo_url: photoUrl || null };
    // 出片鏈路 evidence (ticket item 3): an optional photo URL the owner can
    // verify; accepted reports with a photo feed the T2 ladder rung.
    const status = throttled ? "flagged" : "pending";
    const id = await insertFeedback(env, uid, placeId, "report", status, throttled ? { ...payload, flag_reason: "time" } : payload);
    return jsonOk(req, { ok: true, id, type: "report", status });
  }

  // comment
  const placeId = body.placeId || body.place_id || null;
  const text = clampText(body.commentText || body.comment_text, MAX_TEXT);
  if (!text) return jsonErr(req, 400, "comment_text required");
  payload = { ...payload, comment_text: text };
  const status = throttled ? "flagged" : "pending";
  const id = await insertFeedback(env, uid, placeId, "comment", status, throttled ? { ...payload, flag_reason: "time" } : payload);
  return jsonOk(req, { ok: true, id, type: "comment", status });
}

function clampText(v, max) {
  if (typeof v !== "string") return null;
  const t = v.trim();
  if (!t) return null;
  return t.slice(0, max);
}

async function insertFeedback(env, uid, placeId, type, status, payload) {
  const id = await newId();
  await env.DB.prepare(
    `INSERT INTO feedback (id, user_id, place_id, type, status, payload) VALUES (?1, ?2, ?3, ?4, ?5, ?6)`
  ).bind(id, uid, placeId, type, status, JSON.stringify(payload)).run();
  return id;
}

// ---------------------------------------------------------------------------
// DELETE /api/v1/feedback?place_id=... — member deletes their own rating.
// ---------------------------------------------------------------------------
export async function handleFeedbackDelete(req, env, url) {
  const session = await requireMember(req, env);
  if (!session) return jsonErr(req, 401, "JWT session required");
  const placeId = url.searchParams.get("place_id");
  if (!placeId) return jsonErr(req, 400, "place_id required");
  const r = await env.DB.prepare(
    "DELETE FROM feedback WHERE user_id = ?1 AND place_id = ?2 AND type = 'rating'"
  ).bind(session.sub, placeId).run();
  const changed = r && r.meta && typeof r.meta.changes === "number" ? r.meta.changes : 0;
  if (!changed) return jsonErr(req, 404, "rating not found");
  return jsonOk(req, { ok: true, deleted: placeId });
}

// ---------------------------------------------------------------------------
// Admin review surface (design §2.3 minimal plan):
//   GET   /api/v1/admin/feedback?status=pending  — review queue (admin only)
//   PATCH /api/v1/admin/feedback/<id> {action}   — approve → ok / reject
// ---------------------------------------------------------------------------
export async function handleAdminFeedbackList(req, env, url) {
  const session = await requireMember(req, env);
  if (!session) return jsonErr(req, 401, "JWT session required");
  if (!(await isAdmin(env, session.sub))) return jsonErr(req, 403, "admin required");

  const status = url.searchParams.get("status") || "pending";
  if (!["pending", "ok", "flagged", "rejected", "need_info", "all"].includes(status)) {
    return jsonErr(req, 400, "unknown status filter");
  }
  const limit = Math.min(Number(url.searchParams.get("limit")) || 50, 200);
  const offset = Math.max(Number(url.searchParams.get("offset")) || 0, 0);
  const where = status === "all" ? "" : ` WHERE f.status = '${status}'`;
  const { results } = await env.DB.prepare(
    `SELECT f.id, f.user_id, f.place_id, f.type, f.status, f.payload, f.created_at, u.display_name, u.name_history
     FROM feedback f LEFT JOIN users u ON u.device_id = f.user_id${where}
     ORDER BY f.created_at DESC LIMIT ${limit} OFFSET ${offset}`
  ).bind().all();
  const countRow = await env.DB.prepare(
    `SELECT COUNT(*) AS n FROM feedback${where ? where.replace(" f.", " ").replace("f.status", "status") : ""}`
  ).bind().first();
  const items = (results || []).map((r) => {
    let pl = {};
    try { pl = JSON.parse(r.payload || "{}"); } catch { pl = {}; }
    let history = [];
    try { const h = JSON.parse(r.name_history || "[]"); if (Array.isArray(h)) history = h; } catch { history = []; }
    return {
      id: r.id, type: r.type, placeId: r.place_id, status: r.status,
      maskedName: maskName(r.display_name),
      // owner ruling (Stage 1): rename audit readable by admins in the queue
      nameHistory: history,
      trustLevel: pl.trust_level || null,
      reportCategory: pl.report_category || null,
      commentText: pl.comment_text || null,
      photoUrl: pl.photo_url || null,
      payload: pl,
      createdAt: r.created_at,
    };
  });
  return jsonOk(req, { items, count: countRow ? countRow.n : items.length });
}

export async function handleAdminFeedbackReview(req, env, id) {
  const session = await requireMember(req, env);
  if (!session) return jsonErr(req, 401, "JWT session required");
  if (!(await isAdmin(env, session.sub))) return jsonErr(req, 403, "admin required");
  const body = await req.json().catch(() => null);
  const action = body && (body.action || body.status);
  if (action !== "approve" && action !== "reject") {
    return jsonErr(req, 400, "action must be approve or reject");
  }
  const row = await env.DB.prepare(
    "SELECT id, status, payload FROM feedback WHERE id = ?1 LIMIT 1"
  ).bind(id).first();
  if (!row) return jsonErr(req, 404, "feedback not found");
  let pl = {};
  try { pl = JSON.parse(row.payload || "{}"); } catch { pl = {}; }
  pl.reviewed_by = session.sub;
  pl.reviewed_at = nowIso();
  const status = action === "approve" ? "ok" : "rejected";
  await env.DB.prepare(
    "UPDATE feedback SET status = ?2, payload = ?3, updated_at = ?4 WHERE id = ?1"
  ).bind(id, status, JSON.stringify(pl), nowIso()).run();
  return jsonOk(req, { ok: true, id, status });
}

// Exported for tests / future daily-batch reuse.
export const FEEDBACK_CONSTANTS = {
  WEIGHTS, REPORT_CATEGORIES, HALF_LIFE_DAYS, BAYES_K, CLUSTER_CAP,
  CLUSTER_PENALTY, NO_CHAIN_P_FACTOR, DISPLAY_MIN_EFF, DISPLAY_MIN_RAW,
  THROTTLE_MS, T0_24H_VOTE_CAP,
};
