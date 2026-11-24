// CL-APP-06 (DESIGN-8): custom places — private member points at ANY global
// latitude/longitude, evaluated by the SAME machinery as official places:
//   - conditions: CL-UI-99 custom-conditions engine (notify.js) — same five
//     parameter groups, same validation, same hourly judgment;
//   - fetches: dedicated LOW-PRIORITY queue (custom_fetch_queue) so bulk adds
//     never burst Open-Meteo, with the owner-ruled quota insurance:
//     personal top-1% → daily refresh, persistent top-0.1% → every 2 days,
//     global usage at 70% of budget → all refreshes downshift 10%,
//     global usage at 90% → non-core refreshes stop (honest 「資料更新延遲」
//     labels, never a silent quality drop);
//   - caps (owner ruling 2026-11-15): free members hold a 3-point trial for
//     90 days measured from users.created_at; after expiry the cap is 0 —
//     every active point flips trial_expired (data kept, evaluation stopped,
//     hidden from the default list, gray + honest 「試用期滿」 under the
//     private filter). paid = 50, owner = unlimited.
//   - anti-abuse layers (owner ruling, updated: the rolling 30-day distinct
//     budget was REMOVED — daily cost is already capped by the per-user daily
//     fetch budget, and the 75-key budget was redundant + confusing):
//     (1) 60 creates/day hard block (friendly reminder at the 50th),
//     (2) per-user daily fetch budget 60 (excess deferred to next day),
//     (3) first fetch queued low priority. Delete stays SOFT — archived +
//     deleted_at, and re-adding the same coords within 30 days REVIVES the
//     row with its existing data, no new fetch, no new charge; the 30-day
//     distinct-key count is kept as an internal telemetry record only
//     (it never blocks an add).
// Results only — thresholds/formulas never leave this module's own domain,
// and user-facing copy is tri-lingual everywhere.
// CL-APP-08: private-place grid dedup (owner-approved conservative version)
import {
  findGroupFor, joinGroup, leaveGroup, representativeOf, fanOutGroupEval,
  getGroupRecord, regroupExistingPlaces,
} from "./place-groups.js";
import { validateCustomConditions, parseCustomConditions, findNextCustomWindow, slotTimeMs, placeCtxFromRec, validateWindowSegment } from "./notify.js";

export const TRIAL_DAYS = 90;
export const CAPS = { freeTrial: 3, freeExpired: 0, paid: 50 };
// Owner ruling (updated): the daily add cooldown is a HARD block at 60/day
// (supports a new member importing a whole batch on day one). At the 50th
// add the response carries a friendly tri-lingual reminder (never a block);
// the 61st add is rejected 403.
export const DAILY_ADD_LIMIT = 60;
export const DAILY_ADD_REMINDER_AT = 50;
export const DEDUP_WINDOW_DAYS = 30;
export const COORD_PRECISION = 3;            // 0.001° dedupe key
export const NOMINATION_THROTTLE_DAYS = 7;
export const NAME_MAX_LEN = 60;
// patch-8 (owner ruling): ONE private point may carry MULTIPLE condition
// groups (custom themes) — each with its own name (i18n) + the CL-UI-99
// conditions blob (months live inside it). Cap = 5 groups per place. The
// fetch quota does NOT scale with groups: weather is fetched ONCE per place
// and every group judges the SAME stored hourly rows, so theme CRUD never
// enqueues a fetch and never consumes the daily fetch budget.
export const MAX_THEMES_PER_PLACE = 5;
export const THEME_NAME_MAX_LEN = 40;
// Quota insurance (design-review-8 §2.2): 1 custom place ≈ 1.0 Open-Meteo
// call per refresh. The daily budget counts only CUSTOM-PLACE calls — the
// official pipeline is budgeted separately by the data layer.
export const GLOBAL_DAILY_BUDGET = 5000;
export const BRAKE_SOFT = 0.7;               // ≥70% of budget → refresh batch ×0.9
export const BRAKE_HARD = 0.9;               // ≥90% → stop non-core refreshes
// Owner-ruled layer 3: per-user daily fetch budget — at most 60 ACTUAL
// weather fetches per user per day (50 routine + 10 new-point headroom).
// Excess queue entries are DEFERRED to the next day (never rejected: the
// new point is created fine and the card honestly shows 「已建立·氣象資料
// 明日更新」); deferred entries are picked up when the counter resets.
export const USER_DAILY_FETCH_BUDGET = 60;
export const ELEV_MIN_M = -450;              // Dead Sea floor sanity bounds
export const ELEV_MAX_M = 8849;              // Everest summit

// ---------------------------------------------------------------------------
// Trial window (owner ruling): users.created_at + 90 days drives the free
// trial. D1 stores datetime('now') as "YYYY-MM-DD HH:MM:SS" (UTC, no zone) —
// normalize before Date.parse or the host timezone silently shifts the
// boundary.
// ---------------------------------------------------------------------------
function parseDbTime(s) {
  if (typeof s !== "string" || !s) return NaN;
  let t = s.trim().replace(" ", "T");
  if (!/[Zz]|[+-]\d\d:?\d\d$/.test(t)) t += "Z";
  return Date.parse(t);
}

export function trialExpiresAtMs(createdStr) {
  const created = parseDbTime(createdStr);
  if (!Number.isFinite(created)) return null;
  return created + TRIAL_DAYS * 24 * 3_600_000;
}

export function trialState(userRow, nowMs = Date.now()) {
  const expiresAt = trialExpiresAtMs(userRow && userRow.created_at);
  return { expired: expiresAt !== null && nowMs >= expiresAt, expiresAt };
}

// Effective cap matrix. freeAsPaid (pre-billing gray flag) lifts free → paid
// exactly like the notify caps (CL-DATA-70) — same one source of truth.
export function capFor(level, trialExpired, freeAsPaid = false) {
  if (level === "owner") return Infinity;
  if (level === "paid" || (level === "free" && freeAsPaid)) return CAPS.paid;
  return trialExpired ? CAPS.freeExpired : CAPS.freeTrial;
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
// Honest tri-lingual copy (every rejection explains itself; never a silent
// refusal — same family as NOTIFY_RULE_LIMIT_MESSAGES).
// ---------------------------------------------------------------------------
export const MESSAGES = {
  trial_cap: {
    "zh-TW": "免費試用期內上限 3 個自訂點。既有自訂點會保留，刪除後即可再新增。",
    "en": "Free trial is capped at 3 custom places. Existing places are kept — delete one to add more.",
    "ja": "無料トライアル中の自作スポット上限は3件です。既存は保持され、削除後に追加できます。",
  },
  trial_expired: {
    "zh-TW": "免費試用期（90 天）已滿，自訂點上限為 0——既有自訂點已保留但停止評估；升級 Premium 後可恢復使用。",
    "en": "The 90-day free trial has ended and the custom-place cap is 0 — your places are kept but evaluation is stopped. Upgrade to Premium to resume.",
    "ja": "無料トライアル（90日）が終了し、自作スポットの上限は0です。既存スポットは保持されますが評価は停止中です。Premiumへアップグレードすると再開できます。",
  },
  paid_cap: {
    "zh-TW": "付費版上限 50 個自訂點。既有自訂點會保留，刪除後即可再新增。",
    "en": "Premium is capped at 50 custom places. Existing places are kept — delete one to add more.",
    "ja": "有料プランの自作スポット上限は50件です。既存は保持され、削除後に追加できます。",
  },
  daily_add: {
    "zh-TW": "單日上限 60 個，明天再繼續。",
    "en": "Daily add limit is 60 — please continue tomorrow.",
    "ja": "1日の追加上限は60件です。明日続きを行ってください。",
  },
  daily_add_reminder: {
    "zh-TW": "今日已新增 50 個景點，單日上限 60 個。",
    "en": "You have added 50 places today — the daily limit is 60.",
    "ja": "本日50件のスポットを追加しました。1日の上限は60件です。",
  },
  degraded: {
    "zh-TW": "資料更新延遲：全站自訂點用量接近額度上限，首次抓取暫緩（資料保留，不會遺失）。",
    "en": "Data refresh delayed: site-wide custom-place usage is near the quota — first fetches are postponed (data is kept, nothing is lost).",
    "ja": "データ更新が遅延しています：サイト全体の自作スポット使用量が上限に近づいています。初回取得は延期されます（データは保持されます）。",
  },
  // patch-8: per-place theme-group cap + input honesty
  theme_cap: {
    "zh-TW": "每個私人點最多 5 組題材。既有題材會保留，刪除後即可再新增。",
    "en": "A place holds at most 5 subject groups. Existing ones are kept — delete one to add more.",
    "ja": "1スポットの題材グループは最大5件です。既存は保持され、削除後に追加できます。",
  },
  theme_name_required: {
    "zh-TW": "請先輸入題材名稱。",
    "en": "Enter a subject name first.",
    "ja": "先に題材名を入力してください。",
  },
  theme_conditions_required: {
    "zh-TW": "請至少設定一組條件（未調整＝一般基準，不需要另掛一組）。",
    "en": "Set at least one condition (nothing tuned = the general baseline, which needs no extra group).",
    "ja": "条件を1つ以上設定してください（未調整＝一般基準のため、別グループは不要です）。",
  },
};

// Every rejection/explanation carries the FULL tri-lingual object — the
// client picks its language (same contract as NOTIFY_RULE_LIMIT_MESSAGES).
function pickMsg(key) {
  return MESSAGES[key] || null;
}

// ---------------------------------------------------------------------------
// Fail short-words (tri-lingual) — same vocabulary family as the data layer's
// fail_reason_short.json (visibility 霧 / precipitation 雨 / cloud_cover_low
// 低雲 / cloud_cover_mid 厚雲 / wind 風強); cloud_cover_high is a worker-local
// addition in the same style.
// ---------------------------------------------------------------------------
const FAIL_WORDS = {
  cloud_low: { "zh-TW": "低雲", "en": "low cloud", "ja": "低い雲" },
  cloud_mid: { "zh-TW": "厚雲", "en": "thick cloud", "ja": "厚い雲" },
  cloud_high: { "zh-TW": "高雲", "en": "high cloud", "ja": "高い雲" },
  precipitation: { "zh-TW": "雨", "en": "rain", "ja": "雨" },
  visibility: { "zh-TW": "霧", "en": "fog", "ja": "霧" },
  wind: { "zh-TW": "風強", "en": "strong wind", "ja": "強風" },
};

// ---------------------------------------------------------------------------
// Lenient general baseline (no custom conditions attached): a private point
// is ○可拍 whenever the hour is physically shootable at all — rain ≤ 2 mm/h,
// visibility ≥ 3 km, wind ≤ 10 m/s. Clouds stay unconstrained (the general
// baseline is about "can you shoot", not about any subject's decisive
// condition). Missing data fails the hour honestly.
// ---------------------------------------------------------------------------
export const GENERAL_BASELINE = { precip_max_mmh: 2, visibility_min_km: 3, wind_max_ms: 10 };

export function roundCoord(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return NaN;
  return Math.round(n * Math.pow(10, COORD_PRECISION)) / Math.pow(10, COORD_PRECISION);
}

export function dedupeKey(lat, lng) {
  return `${roundCoord(lat)},${roundCoord(lng)}`;
}

function json(req, status, body, extraHeaders = {}) {
  const origin = req.headers.get("Origin") || "";
  const h = new Headers({
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": origin === "https://chaselights.app" ? origin : "null",
    "Vary": "Origin",
    ...extraHeaders,
  });
  return new Response(JSON.stringify(body), { status, headers: h });
}

async function requireSession(req, env) {
  const { getSession } = await import("./auth.js");
  const session = await getSession(req, env);
  return session && session.sub ? session : null;
}

function randomId() {
  return btoa(crypto.getRandomValues(new Uint8Array(16)).reduce((s, b) => s + String.fromCharCode(b), ""))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function clampText(v, max) {
  if (typeof v !== "string") return "";
  const t = v.trim();
  return t ? [...t].slice(0, max).join("") : "";
}

// ---------------------------------------------------------------------------
// Evaluation summary (results only). A private point's tier:
//   rec    — a CL-UI-99 custom-condition window matches within 24h
//   shoot  — no conditions attached; the lenient general baseline passes
//   no     — conditions (or the baseline) fail; dominant fail short-word
//   pending — first fetch still queued (honest 「排隊中」, never fabricated)
// ---------------------------------------------------------------------------
export function evaluateCustomPlace(cc, rec, nowMs = Date.now()) {
  if (!rec || !Array.isArray(rec.hourly) || !rec.hourly.length) {
    return { tier: "pending", reason: null, window: null };
  }
  const hourly = rec.hourly;
  const placeCtx = placeCtxFromRec(rec);
  if (cc) {
    const win = findNextCustomWindow(hourly, cc, nowMs, 0, placeCtx);
    if (win) return { tier: "rec", reason: null, window: `${win.local_date} ${win.hour}` };
    // patch-5 ④: when a month window is set and NO hour in the next-24h
    // horizon falls inside it, the honest dominant reason is the month
    // window itself — never a weather word (non-applicable month is an
    // eligibility fact, not a daily weather failure).
    if (Array.isArray(cc.months) && cc.months.length &&
        !hourly.some((r) => r && typeof r.local_date === "string" &&
          cc.months.includes(Number(r.local_date.slice(5, 7))))) {
      return { tier: "no", reason: "非適用月份", window: null };
    }
    return { tier: "no", reason: dominantFailWord(hourly, cc, nowMs), window: null };
  }
  // no conditions: lenient general baseline
  const win = findNextCustomWindow(hourly, { ...GENERAL_BASELINE }, nowMs, 0, placeCtx);
  if (win) return { tier: "shoot", reason: null, window: `${win.local_date} ${win.hour}` };
  return { tier: "no", reason: dominantFailWord(hourly, GENERAL_BASELINE, nowMs), window: null };
}

// Dominant failure = the constrained metric violating the largest share of
// the next-24h hours (same spirit as the data layer's dominant-reason vote —
// window/eligibility classes are not in the pool by construction here).
export function dominantFailWord(hourly, cc, nowMs = Date.now()) {
  const latest = nowMs + 24 * 3_600_000;
  const checked = hourly.filter((r) => {
    if (!r || typeof r.local_date !== "string" || typeof r.hour !== "string") return false;
    const t = slotTimeMs(r.local_date, r.hour);
    return Number.isFinite(t) && t >= nowMs - 3_600_000 && t <= latest;
  });
  const rows = checked.length ? checked : hourly;
  const pairs = [
    ["cloud_low_max", "cloud_low"], ["cloud_mid_max", "cloud_mid"],
    ["cloud_high_max", "cloud_high"], ["precip_max_mmh", "precipitation"],
    ["visibility_min_km", "visibility"], ["wind_max_ms", "wind"],
    ["cloud_low_min", "cloud_low"], ["cloud_mid_min", "cloud_mid"], ["cloud_high_min", "cloud_high"],
  ];
  const gteParam = (p) => p === "visibility_min_km" || p.endsWith("_min");
  let best = null;
  for (const [param, metric] of pairs) {
    const limit = cc && cc[param] != null ? Number(cc[param]) : null;
    if (limit == null) continue;
    let violations = 0, counted = 0;
    for (const r of rows) {
      const v = r && r.values ? r.values[metric] : undefined;
      if (v == null || !Number.isFinite(Number(v))) continue;
      counted += 1;
      const val = Number(v);
      if (gteParam(param) ? val < limit : val > limit) violations += 1;
    }
    if (!counted) continue;
    const share = violations / counted;
    if (share > 0 && (!best || share > best.share)) best = { metric, share };
  }
  if (!best) return FAIL_WORDS.precipitation["zh-TW"];
  return FAIL_WORDS[best.metric]["zh-TW"];
}

export function failWordLocalized(metric, lang) {
  const d = FAIL_WORDS[metric] || FAIL_WORDS.precipitation;
  return d[lang] || d["zh-TW"];
}

// ---------------------------------------------------------------------------
// patch-8: MULTIPLE condition groups per private point.
//   validateThemeInput     — name (required, ≤40 chars) + optional i18n object
//                            + non-empty CL-UI-99 conditions blob (months ride
//                            inside it — the same schema notify validates);
//   evaluateThemeGroups    — ONE evaluation per group with the SAME
//                            evaluateCustomPlace machinery (same-source tiers);
//   aggregateEvaluation    — the place-level verdict: rec if ANY group matches
//                            within 24h (earliest window), else shoot if the
//                            lenient baseline passes, else no with a VOTED
//                            dominant reason (no single-group bias).
// Theme CRUD never enqueues a fetch: every group judges the same stored
// hourly rows — the fetch quota is per-PLACE, counted once.
// ---------------------------------------------------------------------------
export function validateThemeNameInput(name, nameI18nRaw) {
  const n = clampText(name, THEME_NAME_MAX_LEN);
  if (!n) return { ok: false, error: "theme name required", messageKey: "theme_name_required" };
  let nameI18n = null;
  if (nameI18nRaw != null) {
    if (typeof nameI18nRaw !== "object" || Array.isArray(nameI18nRaw)) {
      return { ok: false, error: "nameI18n must be an object" };
    }
    const out = {};
    for (const [k, v] of Object.entries(nameI18nRaw)) {
      if (!["zh-TW", "en", "ja"].includes(k)) continue; // unknown locales are dropped, never stored
      const s = clampText(v, THEME_NAME_MAX_LEN);
      if (s) out[k] = s;
    }
    nameI18n = Object.keys(out).length ? out : null;
  }
  return { ok: true, name: n, nameI18n };
}

export function validateThemeInput(body) {
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return { ok: false, error: "body required" };
  }
  const nameCheck = validateThemeNameInput(body.name, body.nameI18n != null ? body.nameI18n : body.name_i18n);
  if (!nameCheck.ok) return nameCheck;
  const ccRes = validateCustomConditions(body.conditions != null ? body.conditions : body.customConditions);
  if (!ccRes.ok) return { ok: false, error: ccRes.error };
  if (!ccRes.cc) return { ok: false, error: "conditions required", messageKey: "theme_conditions_required" };
  return { ok: true, name: nameCheck.name, nameI18n: nameCheck.nameI18n, conditions: ccRes.cc };
}

export function evaluateThemeGroups(groups, rec, nowMs = Date.now()) {
  return (groups || []).map((g) => ({
    id: g.id, name: g.name, nameI18n: g.nameI18n || null, conditions: g.conditions || null,
    evaluation: evaluateCustomPlace(g.conditions, rec, nowMs),
  }));
}

export function aggregateEvaluation(evalList) {
  const items = (evalList || []).filter(Boolean);
  if (!items.length) return { tier: "pending", reason: null, window: null };
  // every input still queued (first fetch deferred) → the honest pending state
  if (items.every((e) => e.tier === "pending")) {
    return { tier: "pending", reason: null, window: null };
  }
  const recs = items.filter((e) => e.tier === "rec" && e.window);
  if (recs.length) {
    // earliest qualifying window wins (same 「next window」 semantics as a card)
    const best = recs.reduce((a, b) => (String(b.window) < String(a.window) ? b : a));
    return { tier: "rec", reason: null, window: best.window };
  }
  if (items.some((e) => e.tier === "shoot")) {
    const shoot = items.find((e) => e.tier === "shoot");
    return { tier: "shoot", reason: null, window: shoot.window };
  }
  const reasons = items.map((e) => e.reason).filter(Boolean);
  const counts = new Map();
  for (const r of reasons) counts.set(r, (counts.get(r) || 0) + 1);
  let reason = null;
  for (const [r, n] of counts) if (!reason || n > counts.get(reason)) reason = r;
  return { tier: "no", reason, window: null };
}

// Load a place's theme groups WITH the legacy-single-set migration built in:
// a place whose custom_conditions blob is set but has NO group rows yet gets
// that blob migrated into one group (「題材 1」) — idempotent, lazy, and
// byte-compatible with the 0012 SQL backfill. Never throws (best-effort).
export async function loadThemeGroups(env, placeRow) {
  let rows = [];
  try {
    ({ results: rows } = await env.DB.prepare(
      "SELECT id, place_id, user_id, name, name_i18n, conditions FROM custom_place_themes WHERE place_id = ?1 ORDER BY created_at ASC, id ASC"
    ).bind(placeRow.id).all());
  } catch { rows = []; }
  rows = rows || [];
  if (!rows.length && placeRow.custom_conditions) {
    const id = randomId();
    try {
      await env.DB.prepare(
        "INSERT INTO custom_place_themes (id, place_id, user_id, name, conditions) VALUES (?1, ?2, ?3, ?4, ?5)"
      ).bind(id, placeRow.id, placeRow.user_id, "題材 1", placeRow.custom_conditions).run();
      rows = [{ id, place_id: placeRow.id, name: "題材 1", name_i18n: null, conditions: placeRow.custom_conditions }];
    } catch { /* migration is best-effort; the legacy blob still evaluates */ }
  }
  return rows.map((r) => ({
    id: r.id, name: r.name,
    nameI18n: parseCustomConditions(r.name_i18n),
    conditions: parseCustomConditions(r.conditions),
  }));
}

// ---------------------------------------------------------------------------
// Global quota counters (KV): v1:cp:global:<yyyymmdd> = {count}, plus a
// degraded flag consumed by clients for honest 「資料更新延遲」 labels.
// ---------------------------------------------------------------------------
function dayKey(nowMs = Date.now()) {
  return new Date(nowMs).toISOString().slice(0, 10).replace(/-/g, "");
}

export async function globalUsageState(env, nowMs = Date.now()) {
  let count = 0;
  try {
    const v = await env.EVALS.get(`v1:cp:global:${dayKey(nowMs)}`, "json");
    if (v && typeof v.count === "number") count = v.count;
  } catch { count = 0; }
  const ratio = count / GLOBAL_DAILY_BUDGET;
  return { count, budget: GLOBAL_DAILY_BUDGET, ratio, soft: ratio >= BRAKE_SOFT, hard: ratio >= BRAKE_HARD };
}

export async function bumpGlobalUsage(env, n = 1, nowMs = Date.now()) {
  const key = `v1:cp:global:${dayKey(nowMs)}`;
  let v = null;
  try { v = await env.EVALS.get(key, "json"); } catch { v = null; }
  const count = ((v && typeof v.count === "number") ? v.count : 0) + n;
  try { await env.EVALS.put(key, JSON.stringify({ count, updated_at: new Date(nowMs).toISOString() })); } catch { /* best-effort */ }
  return count;
}

// Per-user daily fetch counter (owner-ruled layer 3): KV
// v1:cp:fetch:<uid>:<yyyymmdd> = count. The counter resets at the UTC day
// boundary, which is exactly when deferred queue entries come due again.
export async function userFetchCount(env, uid, nowMs = Date.now()) {
  try {
    const v = await env.EVALS.get(`v1:cp:fetch:${uid}:${dayKey(nowMs)}`, "json");
    return (v && typeof v.count === "number") ? v.count : 0;
  } catch { return 0; }
}

export async function bumpUserFetch(env, uid, n = 1, nowMs = Date.now()) {
  const key = `v1:cp:fetch:${uid}:${dayKey(nowMs)}`;
  const used = (await userFetchCount(env, uid, nowMs)) + n;
  try { await env.EVALS.put(key, JSON.stringify({ count: used, updated_at: new Date(nowMs).toISOString() })); } catch { /* best-effort */ }
  return used;
}

// Per-user rolling-24h call counter → the percentile-lite energy saver.
// Registry key v1:cp:usage24h = { [uid]: {count, day} }; heavy users (top 1%
// of active custom users, minimum meaningful volume) refresh daily instead of
// every cycle, persistent top-0.1% every 2 days — exactly the owner-ruled
// downshift ladder, honest-labeled in the UI.
export function energySaverLevel(usageCounts, uid, minVolume = 50) {
  const entries = Object.entries(usageCounts || {})
    .map(([id, c]) => [id, typeof c === "number" ? c : (c && c.count) || 0])
    .filter(([id, c]) => c >= minVolume)
    .sort((a, b) => b[1] - a[1]);
  if (!entries.length) return { rank: null, level: "normal" };
  const rank = entries.findIndex(([id]) => id === uid);
  if (rank < 0) return { rank: null, level: "normal" };
  const top1 = Math.max(1, Math.ceil(entries.length * 0.01));
  const top01 = Math.max(1, Math.ceil(entries.length * 0.001));
  if (rank < top01 && entries.length >= 100) return { rank, level: "every-2-days" };
  if (rank < top1) return { rank, level: "daily" };
  return { rank, level: "normal" };
}

export async function refreshIntervalFor(env, uid, nowMs = Date.now()) {
  // default cadence: the queue cycles every scheduled run (cron 30 min);
  // official-style refreshes are spread by due_at offsets. The saver only
  // WIDENS personal intervals — it never narrows them.
  let registry = {};
  try { registry = (await env.EVALS.get("v1:cp:usage24h", "json")) || {}; } catch { registry = {}; }
  const { level } = energySaverLevel(registry, uid);
  if (level === "daily") return { intervalHours: 24, label: "daily", energySaver: true };
  if (level === "every-2-days") return { intervalHours: 48, label: "every-2-days", energySaver: true };
  return { intervalHours: 6, label: "6h", energySaver: false };
}

// ---------------------------------------------------------------------------
// CRUD handlers. All endpoints are JWT-member-only (custom places are a
// member feature — the mockup's 未登入 state blocks every action).
// ---------------------------------------------------------------------------
// ---------------------------------------------------------------------------
// CL-APP-08: member-facing shared-fetch info. sharedWith = the OTHER members
// of this place's group (names from the group KV record), representativeId
// tells who performs the shared fetch. Trial-expired members keep showing
// their tag; archived rows never appear in the listing anyway.
// ---------------------------------------------------------------------------
export async function sharingInfoFor(env, row, siblings = []) {
  if (!row.group_id) return null;
  const rec = await getGroupRecord(env, row.group_id);
  const siblingNames = new Map(siblings.filter((s) => s.id !== row.id && s.group_id === row.group_id).map((s) => [s.id, s.name]));
  const members = (rec && Array.isArray(rec.members) ? rec.members : [...siblingNames].map(([id, name]) => ({ id, name })));
  const sharedWith = members
    .filter((m) => m.id !== row.id)
    .map((m) => ({ id: m.id, name: siblingNames.get(m.id) || m.name }));
  return {
    groupId: row.group_id,
    representativeId: (rec && rec.representativeId) || null,
    isRepresentative: !rec || rec.representativeId === row.id,
    sharedWith,
    shareMode: row.share_mode || "auto",
  };
}

export async function handleCustomPlaces(req, env, opts = {}) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;

  const user = await env.DB.prepare(
    "SELECT device_id, level, created_at FROM users WHERE device_id = ?1"
  ).bind(uid).first();
  if (!user) return json(req, 401, { error: "session user not found" });
  const level = user.level || "free";
  const fap = level === "free" ? await freeAsPaidFlag(env) : false;

  if (req.method === "GET") {
    const trial = trialState(user);
    // Sweep: a free member past the trial window has ALL active points flip
    // to trial_expired (data kept, evaluation stopped) — materialized lazily
    // so the boundary takes effect the moment it passes.
    let effectiveLevel = level;
    if (level === "free" && !fap && trial.expired) {
      effectiveLevel = "free-expired";
      try {
        await env.DB.prepare(
          "UPDATE custom_places SET status = 'trial_expired', updated_at = datetime('now') WHERE user_id = ?1 AND status = 'active'"
        ).bind(uid).run();
      } catch { /* sweep is best-effort; the read-side state is authoritative */ }
    }
    const cap = capFor(level, trial.expired, fap);
    const { results } = await env.DB.prepare(
      "SELECT id, user_id, name, lat, lng, elevation, timezone, custom_conditions, status, group_id, share_mode, created_at, updated_at FROM custom_places WHERE user_id = ?1 AND status != 'archived' ORDER BY created_at DESC"
    ).bind(uid).all();
    const places = [];
    for (const row of results || []) {
      let cc = null;
      try { cc = parseCustomConditions(row.custom_conditions); } catch { cc = null; }
      let rec = null;
      try { rec = await env.EVALS.get(`v1:evals:custom:${row.id}`, "json"); } catch { rec = null; }
      // patch-8: per-GROUP evaluations (same-source tiers, one row per theme)
      // + the aggregate place verdict. The lenient baseline ALWAYS rides along
      // as the general row — a rec group's window only covers its own hours.
      const groups = await loadThemeGroups(env, row);
      const themeGroups = evaluateThemeGroups(groups, rec);
      const baselineEval = evaluateCustomPlace(null, rec);
      const evaluation = aggregateEvaluation([...themeGroups.map((g) => g.evaluation), baselineEval]);
      const { intervalHours, label, energySaver } = await refreshIntervalFor(env, uid);
      // Owner-ruled layer 3 honesty: a point whose first fetch is deferred to
      // the next day (per-user daily budget) reports it — never fabricated data.
      let fetchDeferred = false, fetchDueAt = null;
      try {
        const q = await env.DB.prepare(
          "SELECT due_at, status FROM custom_fetch_queue WHERE place_id = ?1 AND status = 'pending'"
        ).bind(row.id).first();
        const nowStamp = new Date().toISOString().slice(0, 19).replace("T", " ");
        if (q && q.due_at && q.due_at > nowStamp) { fetchDeferred = true; fetchDueAt = q.due_at; }
      } catch { /* honesty flag is best-effort */ }
      places.push({
        id: row.id, name: row.name, lat: row.lat, lng: row.lng,
        elevation: row.elevation, timezone: row.timezone,
        customConditions: cc, status: row.status,
        // patch-8: every group rides the list payload (each with its own
        // same-source tier) + the per-place 5-group quota honestly
        themeGroups,
        themes: { used: themeGroups.length, cap: MAX_THEMES_PER_PLACE },
        // CL-APP-08: shared-fetch info for the member-facing
        // 「與 ○○○ 共用資料」 tag (group members of the SAME user only).
        sharing: row.group_id ? await sharingInfoFor(env, row, results || []) : null,
        createdAt: row.created_at, updatedAt: row.updated_at,
        evaluation: { ...evaluation, evaluatedAt: (rec && rec.generated_at) || null, private: true },
        weather: weatherSummary(rec, row.timezone),
        refresh: { intervalHours, label, energySaver },
        fetchDeferred, fetchDueAt,
      });
    }
    const globalState = await globalUsageState(env);
    const degraded = globalState.hard;
    // CL-APP-08 quota counting: a group counts as ONE point. Ungrouped
    // places count 1 each; grouped places collapse into their group key.
    const groupKeys = new Set((results || []).map((r) => r.group_id || r.id));
    const quotaUsed = groupKeys.size;
    return json(req, 200, {
      ok: true,
      userId: uid,
      level: effectiveLevel,
      trial: { expired: trial.expired, expiresAt: trial.expiresAt ? new Date(trial.expiresAt).toISOString() : null },
      quota: { used: quotaUsed, cap: cap === Infinity ? null : cap },
      degraded,
      degradedMessage: degraded ? pickMsg("degraded") : null,
      places,
    });
  }

  if (req.method === "POST") {
    const body = await req.json().catch(() => null);
    if (!body || typeof body !== "object") return json(req, 400, { error: "body required" });
    const name = clampText(body.name, NAME_MAX_LEN);
    if (!name) return json(req, 400, { error: "name required" });
    const lat = Number(body.lat), lng = Number(body.lng);
    if (!Number.isFinite(lat) || lat < -90 || lat > 90) return json(req, 400, { error: "lat must be a number -90..90" });
    if (!Number.isFinite(lng) || lng < -180 || lng > 180) return json(req, 400, { error: "lng must be a number -180..180" });
    // Elevation is DEM-sourced, never user-authored: only a sanity-bounded
    // value may ride along (the queue processor re-verifies against the API).
    let elevation = null;
    if (body.elevation != null) {
      const e = Number(body.elevation);
      if (!Number.isFinite(e) || e < ELEV_MIN_M || e > ELEV_MAX_M) {
        return json(req, 400, { error: `elevation must be within ${ELEV_MIN_M}..${ELEV_MAX_M} m (DEM value)` });
      }
      elevation = e;
    }
    let timezone = typeof body.timezone === "string" && body.timezone.trim() ? body.timezone.trim().slice(0, 64) : null;

    const ccRes = validateCustomConditions(body.customConditions != null ? body.customConditions : body.custom_conditions);
    if (!ccRes.ok) return json(req, 400, { error: ccRes.error });

    const trial = trialState(user);
    const expired = level === "free" && !fap && trial.expired;
    const cap = capFor(level, trial.expired, fap);

    // Owner-ruled layer 1: daily add cooldown (churn brake) — hard block at
    // 60/day; the 50th add of the day rides with a friendly reminder.
    const dailyRow = await env.DB.prepare(
      "SELECT COUNT(*) AS n FROM custom_places WHERE user_id = ?1 AND created_at >= datetime('now','start of day')"
    ).bind(uid).first();
    const dailyAdds = dailyRow ? dailyRow.n : 0;
    if (dailyAdds >= DAILY_ADD_LIMIT) {
      return json(req, 403, {
        error: "daily add limit reached", reason: "daily_add", count: dailyAdds, limit: DAILY_ADD_LIMIT,
        message: pickMsg("daily_add"),
      });
    }

    // Dedupe/revive: same (user, coords@0.001°) archived within 30 days
    // comes back to life with its existing data — no new fetch, no new
    // charge.
    const keyLat = roundCoord(lat), keyLng = roundCoord(lng);
    const reviveRow = await env.DB.prepare(
      "SELECT id FROM custom_places WHERE user_id = ?1 AND ROUND(lat,3) = ?2 AND ROUND(lng,3) = ?3 AND status = 'archived' AND deleted_at >= datetime('now', ?4) ORDER BY deleted_at DESC LIMIT 1"
    ).bind(uid, keyLat, keyLng, `-${DEDUP_WINDOW_DAYS} days`).first();

    // Active count vs cap (revive occupies an active slot too).
    const activeRow = await env.DB.prepare(
      "SELECT COUNT(*) AS n FROM custom_places WHERE user_id = ?1 AND status != 'archived'"
    ).bind(uid).first();
    const activeCount = activeRow ? activeRow.n : 0;
    if (cap !== Infinity && activeCount >= cap) {
      const reason = expired ? "trial_expired" : (level === "paid" || fap ? "paid_cap" : "trial_cap");
      return json(req, 403, {
        error: "custom place limit reached", reason, memberLevel: level, count: activeCount,
        cap: cap === Infinity ? null : cap,
        message: pickMsg(reason),
      });
    }

    if (reviveRow) {
      // CL-APP-08: a revived place starts fresh as independent-auto — its
      // old group memberships were dissolved at delete; re-grouping happens
      // on the next background sweep (no new fetch is charged for it).
      await env.DB.prepare(
        "UPDATE custom_places SET status = 'active', name = ?2, deleted_at = NULL, group_id = NULL, share_mode = 'auto', updated_at = datetime('now') WHERE id = ?1"
      ).bind(reviveRow.id, name).run();
      const after = dailyAdds + 1;
      return json(req, 200, {
        ok: true, revived: true, id: reviveRow.id,
        quota: { used: activeCount + 1, cap: cap === Infinity ? null : cap },
        dailyAdds: after, dailyRemaining: Math.max(0, DAILY_ADD_LIMIT - after),
        reminder: after >= DAILY_ADD_REMINDER_AT ? pickMsg("daily_add_reminder") : null,
      });
    }

    // Owner ruling (CL-APP-06 close-out): the rolling 30-day distinct budget
    // (cap × 1.5) was REMOVED as a gate — daily cost is already capped by the
    // per-user daily fetch budget, and the extra layer confused users. The
    // distinct-key count is kept as an INTERNAL telemetry record only (it
    // never rejects an add); revive/archived semantics above are unchanged.
    let distinct30d = null;
    try {
      const distinctRow = await env.DB.prepare(
        "SELECT COUNT(*) AS n FROM (SELECT DISTINCT ROUND(lat,3) AS la, ROUND(lng,3) AS lo FROM custom_places WHERE user_id = ?1 AND (status = 'active' OR (status = 'archived' AND deleted_at >= datetime('now', ?2))))"
      ).bind(uid, `-${DEDUP_WINDOW_DAYS} days`).first();
      distinct30d = distinctRow ? distinctRow.n : null;
    } catch { /* telemetry is best-effort, never blocking */ }

    const id = randomId();
    await env.DB.prepare(
      "INSERT INTO custom_places (id, user_id, name, lat, lng, elevation, timezone, custom_conditions) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)"
    ).bind(id, uid, name, lat, lng, elevation, timezone, ccRes.cc ? JSON.stringify(ccRes.cc) : null).run();
    // CL-APP-08 grid dedup: before queueing the first fetch, try to join an
    // existing group of the SAME member (distance <1 km + elev diff <30 m +
    // 500 m relief ≤100 m + no ridge/gully crossing). A DEM-sourced
    // elevation is REQUIRED to even try — without it the point stays
    // independent (fail-closed). Joining reuses the representative's data
    // verbatim (no fetch, no quota charge); if the representative has no
    // data yet, its queued fetch fans out to the whole group.
    let grouping = null;
    if (elevation != null) {
      const found = await findGroupFor(env, { id, user_id: uid, lat, lng, elevation }, opts);
      if (found) {
        const rep = await env.DB.prepare(
          "SELECT id, name, group_id FROM custom_places WHERE id = ?1 AND status = 'active'"
        ).bind(found.representativeId).first();
        if (rep && rep.id !== id) {
          const joined = await joinGroup(env, { id, name }, rep);
          grouping = { groupId: joined.groupId, representativeId: rep.id };
          try {
            const repEval = await env.EVALS.get(`v1:evals:custom:${rep.id}`, "json");
            if (repEval && repEval.hourly && repEval.hourly.length) {
              await env.EVALS.put(`v1:evals:custom:${id}`, JSON.stringify({
                ...repEval,
                place_id: id, private: true, name,
                lat, lng, elevation, timezone,
                shared_from: rep.id, shared_group: joined.groupId,
                generated_at: new Date().toISOString(),
              }));
            }
          } catch { /* seeding is best-effort; the rep's next fetch fans out */ }
        }
      }
    }
    if (!grouping) {
      // Owner-ruled layer 3: the first fetch is LOW priority — never immediate.
      await env.DB.prepare(
        "INSERT INTO custom_fetch_queue (place_id, user_id, reason, priority) VALUES (?1, ?2, 'new', 20) ON CONFLICT(place_id) DO NOTHING"
      ).bind(id, uid).run();
    }
    const globalState = await globalUsageState(env);
    const dailyAddsAfter = dailyAdds + 1;
    return json(req, 200, {
      ok: true, id,
      place: { id, name, lat, lng, elevation, timezone, customConditions: ccRes.cc, status: "active" },
      grouping,
      quota: { used: activeCount + 1, cap: cap === Infinity ? null : cap },
      dailyAdds: dailyAddsAfter, dailyRemaining: Math.max(0, DAILY_ADD_LIMIT - dailyAddsAfter),
      reminder: dailyAddsAfter >= DAILY_ADD_REMINDER_AT ? pickMsg("daily_add_reminder") : null,
      degraded: globalState.hard,
      degradedMessage: globalState.hard ? pickMsg("degraded") : null,
      internal: { distinct30d }, // 30-day dedupe telemetry — informational only, never a gate
    });
  }

  return json(req, 405, { error: "method not allowed" });
}

export async function handleCustomPlaceItem(req, env, placeId) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const row = await env.DB.prepare(
    "SELECT id, user_id, name, lat, lng, elevation, timezone, custom_conditions, status, group_id, share_mode, created_at FROM custom_places WHERE id = ?1"
  ).bind(placeId).first();
  // CRUD permission: another member's place simply does not exist for you.
  if (!row || row.user_id !== uid) return json(req, 404, { error: "place not found" });

  if (req.method === "PATCH") {
    const body = await req.json().catch(() => null);
    if (!body || typeof body !== "object") return json(req, 400, { error: "body required" });
    const updates = [];
    const binds = [placeId];
    let reFetch = false;
    if (body.name !== undefined) {
      const name = clampText(body.name, NAME_MAX_LEN);
      if (!name) return json(req, 400, { error: "name required" });
      updates.push(`name = ?${binds.length + 1}`); binds.push(name);
    }
    if (body.lat !== undefined || body.lng !== undefined) {
      const lat = Number(body.lat !== undefined ? body.lat : row.lat);
      const lng = Number(body.lng !== undefined ? body.lng : row.lng);
      if (!Number.isFinite(lat) || lat < -90 || lat > 90) return json(req, 400, { error: "lat must be a number -90..90" });
      if (!Number.isFinite(lng) || lng < -180 || lng > 180) return json(req, 400, { error: "lng must be a number -180..180" });
      updates.push(`lat = ?${binds.length + 1}`); binds.push(lat);
      updates.push(`lng = ?${binds.length + 1}`); binds.push(lng);
      reFetch = true;
      updates.push(`elevation = NULL, timezone = NULL`);
      // CL-APP-08: moving a point invalidates the terrain relation with its
      // old group — the place detaches (fails closed to independent) and its
      // next refetch re-evaluates grouping honestly. Escape-hatch semantics:
      // share_mode='independent' survives until the member opts back in.
      if (row.group_id) {
        try { await leaveGroup(env, { id: placeId, group_id: row.group_id }); } catch { /* detach is best-effort */ }
      }
    }
    if (body.customConditions !== undefined || body.custom_conditions !== undefined) {
      const ccRes = validateCustomConditions(body.customConditions != null ? body.customConditions : body.custom_conditions);
      if (!ccRes.ok) return json(req, 400, { error: ccRes.error });
      updates.push(`custom_conditions = ?${binds.length + 1}`);
      binds.push(ccRes.cc ? JSON.stringify(ccRes.cc) : null);
      reFetch = true;
    }
    if (!updates.length) return json(req, 400, { error: "nothing to update (name / lat+lng / customConditions)" });
    updates.push("updated_at = datetime('now')");
    await env.DB.prepare(`UPDATE custom_places SET ${updates.join(", ")} WHERE id = ?1`).bind(...binds).run();
    if (reFetch && row.status === "active") {
      await env.DB.prepare(
        "INSERT INTO custom_fetch_queue (place_id, user_id, reason, priority) VALUES (?1, ?2, 'refresh', 20) ON CONFLICT(place_id) DO UPDATE SET reason = 'refresh', status = 'pending', updated_at = datetime('now')"
      ).bind(placeId, uid).run();
    }
    return json(req, 200, { ok: true, id: placeId });
  }

  if (req.method === "DELETE") {
    // Owner-ruled soft delete: archived + deleted_at. Re-adding the same
    // coords within 30 days revives the row (existing data, no new fetch).
    // CL-APP-08: an archived point also leaves its fetch group (the group
    // promotes the next-oldest active member or dissolves).
    if (row.group_id) {
      try { await leaveGroup(env, { id: placeId, group_id: row.group_id }); } catch { /* detach is best-effort */ }
    }
    await env.DB.prepare(
      "UPDATE custom_places SET status = 'archived', deleted_at = datetime('now'), updated_at = datetime('now') WHERE id = ?1"
    ).bind(placeId).run();
    await env.DB.prepare("DELETE FROM custom_fetch_queue WHERE place_id = ?1").bind(placeId).run();
    return json(req, 200, {
      ok: true, deleted: placeId,
      note: {
        "zh-TW": "已刪除（資料保留 30 天）：30 日內在同一座標重新新增會直接復活，不重抓。",
        "en": "Deleted (data kept 30 days): re-adding the same coordinates within 30 days revives it without a new fetch.",
        "ja": "削除しました（データは30日保持）：30日以内に同じ座標を再追加すると再取得なしで復活します。",
      },
    });
  }

  return json(req, 405, { error: "method not allowed" });
}

// ---------------------------------------------------------------------------
// patch-7 (owner ruling): private-place card click parity with official cards.
// Clicking a private card opens a forecast popup; THIS endpoint feeds it with
// the SAME stored eval (v1:evals:custom:<id>) the tier engine reads —
// owner-only, read-only, zero new fetch quota (the popup renders data that
// already exists). A place still queued (first fetch deferred) or one whose
// evaluation stopped (trial expired) answers honestly; the popup shows the
// reason verbatim instead of fabricating rows.
// ---------------------------------------------------------------------------
export async function handleCustomPlaceEval(req, env, placeId) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  // Trial-expiry is materialized lazily by the list sweep; the popup must
  // honour the same boundary the moment it passes (evaluation stopped,
  // data kept) instead of relying on a list visit that may never come.
  const user = await env.DB.prepare(
    "SELECT device_id, level, created_at FROM users WHERE device_id = ?1"
  ).bind(uid).first();
  if (!user) return json(req, 401, { error: "session user not found" });
  const level = user.level || "free";
  const row = await env.DB.prepare(
    "SELECT id, user_id, name, lat, lng, elevation, timezone, custom_conditions, status, created_at FROM custom_places WHERE id = ?1"
  ).bind(placeId).first();
  // another member's place simply does not exist for you (same CRUD rule)
  if (!row || row.user_id !== uid) return json(req, 404, { error: "place not found" });
  if (row.status === "trial_expired" ||
      (level === "free" && !(await freeAsPaidFlag(env)) && trialState(user).expired)) {
    return json(req, 403, { error: "evaluation stopped (trial expired); your data is kept" });
  }
  let rec = null;
  try { rec = await env.EVALS.get(`v1:evals:custom:${placeId}`, "json"); } catch { rec = null; }
  if (!rec || !Array.isArray(rec.hourly) || !rec.hourly.length) {
    return json(req, 404, { error: "no evaluation yet", fetchQueued: true });
  }
  return json(req, 200, {
    ok: true, id: placeId, private: true,
    hourly: rec.hourly, generatedAt: rec.generated_at || null,
    elevation: rec.elevation ?? null, timezone: rec.timezone ?? null,
  });
}

// ---------------------------------------------------------------------------
// patch-8: per-place condition-group CRUD (multi-theme). Routes:
//   POST   /custom_places/:id/themes          — create a group (cap 5, dup
//                                               names NOT blocked, NO fetch)
//   PATCH  /custom_places/:id/themes/:tid     — rename / re-set conditions
//   DELETE /custom_places/:id/themes/:tid     — remove the group (hard delete
//                                               of a group — the PLACE keeps
//                                               its own soft-delete revive
//                                               semantics; groups are user
//                                               objects, not weather data)
// All 404 for another member's place (same CRUD permission rule) and none of
// them touches the fetch queue or any quota counter — the weather is fetched
// ONCE per place and every group judges the same stored hourly rows.
// ---------------------------------------------------------------------------
export async function handleCustomPlaceThemes(req, env, placeId) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const row = await env.DB.prepare(
    "SELECT id, user_id, status FROM custom_places WHERE id = ?1"
  ).bind(placeId).first();
  if (!row || row.user_id !== uid) return json(req, 404, { error: "place not found" });
  if (req.method !== "POST") return json(req, 405, { error: "method not allowed" });

  const body = await req.json().catch(() => null);
  const check = validateThemeInput(body);
  if (!check.ok) {
    return json(req, 400, { error: check.error, message: check.messageKey ? pickMsg(check.messageKey) : null });
  }
  const countRow = await env.DB.prepare(
    "SELECT COUNT(*) AS n FROM custom_place_themes WHERE place_id = ?1"
  ).bind(placeId).first();
  const used = countRow ? countRow.n : 0;
  if (used >= MAX_THEMES_PER_PLACE) {
    return json(req, 403, {
      error: "theme group limit reached", reason: "theme_cap",
      cap: MAX_THEMES_PER_PLACE, message: pickMsg("theme_cap"),
    });
  }
  const id = randomId();
  await env.DB.prepare(
    "INSERT INTO custom_place_themes (id, place_id, user_id, name, name_i18n, conditions) VALUES (?1, ?2, ?3, ?4, ?5, ?6)"
  ).bind(id, placeId, uid, check.name, check.nameI18n ? JSON.stringify(check.nameI18n) : null, JSON.stringify(check.conditions)).run();
  return json(req, 200, {
    ok: true, id, placeId,
    theme: { id, name: check.name, nameI18n: check.nameI18n, conditions: check.conditions },
    themes: { used: used + 1, cap: MAX_THEMES_PER_PLACE },
  });
}

export async function handleCustomPlaceThemeItem(req, env, placeId, themeId) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const row = await env.DB.prepare(
    "SELECT id, user_id, status FROM custom_places WHERE id = ?1"
  ).bind(placeId).first();
  if (!row || row.user_id !== uid) return json(req, 404, { error: "place not found" });
  const theme = await env.DB.prepare(
    "SELECT id, place_id, user_id, name, name_i18n, conditions FROM custom_place_themes WHERE id = ?1 AND place_id = ?2"
  ).bind(themeId, placeId).first();
  if (!theme || theme.user_id !== uid) return json(req, 404, { error: "theme not found" });

  if (req.method === "PATCH") {
    const body = await req.json().catch(() => null);
    if (!body || typeof body !== "object") return json(req, 400, { error: "body required" });
    const updates = [];
    const binds = [themeId];
    if (body.name !== undefined || body.nameI18n !== undefined || body.name_i18n !== undefined) {
      // rename: name required (the display anchor); i18n replaces wholesale
      const merged = {
        name: body.name !== undefined ? body.name : theme.name,
        nameI18n: body.nameI18n !== undefined ? body.nameI18n
          : body.name_i18n !== undefined ? body.name_i18n
          : theme.name_i18n ? parseCustomConditions(theme.name_i18n) : undefined,
      };
      const check = validateThemeNameInput(merged.name, merged.nameI18n);
      if (!check.ok) {
        return json(req, 400, { error: check.error, message: check.messageKey ? pickMsg(check.messageKey) : null });
      }
      updates.push(`name = ?${binds.length + 1}`); binds.push(check.name);
      updates.push(`name_i18n = ?${binds.length + 1}`); binds.push(check.nameI18n ? JSON.stringify(check.nameI18n) : null);
    }
    if (body.conditions !== undefined || body.customConditions !== undefined) {
      const ccRes = validateCustomConditions(body.conditions != null ? body.conditions : body.customConditions);
      if (!ccRes.ok) return json(req, 400, { error: ccRes.error });
      if (!ccRes.cc) return json(req, 400, { error: "conditions required", message: pickMsg("theme_conditions_required") });
      updates.push(`conditions = ?${binds.length + 1}`); binds.push(JSON.stringify(ccRes.cc));
    }
    if (!updates.length) return json(req, 400, { error: "nothing to update (name / conditions)" });
    updates.push("updated_at = datetime('now')");
    await env.DB.prepare(`UPDATE custom_place_themes SET ${updates.join(", ")} WHERE id = ?1`).bind(...binds).run();
    return json(req, 200, { ok: true, id: themeId, placeId });
  }

  if (req.method === "DELETE") {
    await env.DB.prepare("DELETE FROM custom_place_themes WHERE id = ?1").bind(themeId).run();
    // CL-APP-10: deleting the LAST group must clear the legacy single-blob
    // column, otherwise loadThemeGroups() lazily "migrates" that blob back into
    // a group on the very next GET — the owner deleted a subject and a 山景
    // group reappeared. The blob is only a pre-groups storage format; once the
    // user has managed groups and removed them all, the place honestly has no
    // subject at all.
    const left = await env.DB.prepare(
      "SELECT COUNT(*) AS n FROM custom_place_themes WHERE place_id = ?1"
    ).bind(placeId).first();
    const remaining = left && typeof left.n === "number" ? left.n : 0;
    if (remaining === 0) {
      await env.DB.prepare(
        "UPDATE custom_places SET custom_conditions = NULL, updated_at = datetime('now') WHERE id = ?1"
      ).bind(placeId).run();
    }
    return json(req, 200, {
      ok: true, deleted: themeId, placeId,
      themes: { used: remaining, cap: MAX_THEMES_PER_PLACE },
    });
  }

  return json(req, 405, { error: "method not allowed" });
}

// CL-APP-08 escape hatch (owner ruling): 「獨立重新抓取」. One click detaches
// the point from its fetch group (share_mode → 'independent', group_id →
// NULL) and queues a SOLO refetch that costs 1 quota (1 user-budget unit +
// 1 global-usage unit when it actually runs — the queue processor bumps
// them, exactly like a first fetch). The detached point never auto-rejoins:
// only the background re-group sweep may group an 'auto'-mode place.
// ---------------------------------------------------------------------------
export const REFETCH_MESSAGES = {
  detached: {
    "zh-TW": "已脫離共組，獨立重新抓取排隊中（計 1 點配額）。",
    "en": "Detached from the shared group — solo refetch queued (counts as 1 quota point).",
    "ja": "共有グループを解除し、単独再取得を待ち列に入れました（1ポイント消費）。",
  },
  queued: {
    "zh-TW": "獨立重新抓取排隊中（計 1 點配額）。",
    "en": "Solo refetch queued (counts as 1 quota point).",
    "ja": "単独再取得を待ち列に入れました（1ポイント消費）。",
  },
};

export async function handleCustomPlaceRefetch(req, env, placeId) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const row = await env.DB.prepare(
    "SELECT id, user_id, name, status, group_id, share_mode FROM custom_places WHERE id = ?1"
  ).bind(placeId).first();
  if (!row || row.user_id !== uid) return json(req, 404, { error: "place not found" });
  if (row.status !== "active") {
    return json(req, 403, {
      error: row.status === "trial_expired" ? "trial expired — refetch unavailable" : "archived place cannot refetch",
      message: {
        "zh-TW": row.status === "trial_expired" ? "試用期滿的自訂點無法重新抓取；升級後即可。" : "已刪除的自訂點無法重新抓取。",
        "en": row.status === "trial_expired" ? "A trial-expired place cannot refetch; upgrade to resume." : "A deleted place cannot refetch.",
        "ja": row.status === "trial_expired" ? "トライアル期限切れのスポットは再取得できません。アップグレード後に可能です。" : "削除済みスポットは再取得できません。",
      },
    });
  }
  let detached = false;
  if (row.group_id) {
    const r = await leaveGroup(env, { id: row.id, group_id: row.group_id });
    detached = !!(r && r.left);
  }
  // Solo refetch: HIGH-ish priority within the low-priority queue (10 < 20)
  // so an explicit member action is not stuck behind bulk adds.
  await env.DB.prepare(
    "INSERT INTO custom_fetch_queue (place_id, user_id, reason, priority) VALUES (?1, ?2, 'refresh', 10) ON CONFLICT(place_id) DO UPDATE SET reason = 'refresh', status = 'pending', priority = 10, updated_at = datetime('now')"
  ).bind(placeId, uid).run();
  const activeRow = await env.DB.prepare(
    "SELECT COUNT(*) AS n FROM custom_places WHERE user_id = ?1 AND status != 'archived'"
  ).bind(uid).first();
  const user = await env.DB.prepare("SELECT level, created_at FROM users WHERE device_id = ?1").bind(uid).first();
  const level = (user && user.level) || "free";
  const trial = trialState(user);
  const fap = level === "free" ? await freeAsPaidFlag(env) : false;
  const cap = capFor(level, trial.expired, fap);
  return json(req, 200, {
    ok: true,
    id: placeId,
    detached,
    shareMode: "independent",
    message: detached ? REFETCH_MESSAGES.detached : REFETCH_MESSAGES.queued,
    quota: { used: activeRow ? activeRow.n : null, cap: cap === Infinity ? null : cap },
  });
}

// ---------------------------------------------------------------------------
// Nomination (⬆ 提名升級官方): one click → the EXISTING feedback review
// queue, type='report' with payload.routing_key='nomination' so admin
// triage can filter nomination tickets. Fail-closed: duplicates and
// 7-day repeats are rejected honestly; the place stays private meanwhile.
// ---------------------------------------------------------------------------
export async function handleCustomPlaceNominate(req, env, placeId) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const uid = session.sub;
  const row = await env.DB.prepare(
    "SELECT id, user_id, name, lat, lng, elevation, status FROM custom_places WHERE id = ?1"
  ).bind(placeId).first();
  if (!row || row.user_id !== uid) return json(req, 404, { error: "place not found" });
  if (row.status !== "active") {
    return json(req, 403, {
      error: row.status === "trial_expired" ? "trial expired — nomination unavailable" : "archived place cannot be nominated",
      message: {
        "zh-TW": row.status === "trial_expired" ? "試用期滿的自訂點無法提名；升級後即可提名。" : "已刪除的自訂點無法提名。",
        "en": row.status === "trial_expired" ? "A trial-expired place cannot be nominated; upgrade to nominate." : "A deleted place cannot be nominated.",
        "ja": row.status === "trial_expired" ? "トライアル期限切れのスポットは推薦できません。アップグレード後に推薦できます。" : "削除済みスポットは推薦できません。",
      },
    });
  }
  const feedbackId = `custom:${row.id}`;
  const dup = await env.DB.prepare(
    "SELECT id, status FROM feedback WHERE user_id = ?1 AND place_id = ?2 AND type = 'report' AND status = 'pending' ORDER BY created_at DESC LIMIT 1"
  ).bind(uid, feedbackId).first();
  if (dup) return json(req, 409, { error: "already nominated (pending review)", id: dup.id });
  const recent = await env.DB.prepare(
    "SELECT id FROM feedback WHERE user_id = ?1 AND place_id = ?2 AND type = 'report' AND created_at >= datetime('now', ?3) ORDER BY created_at DESC LIMIT 1"
  ).bind(uid, feedbackId, `-${NOMINATION_THROTTLE_DAYS} days`).first();
  if (recent) {
    return json(req, 429, {
      error: "nomination throttled (once per 7 days)",
      message: {
        "zh-TW": "同一景點 7 天內只能提名一次，請稍後再試。",
        "en": "A place can only be nominated once every 7 days — please try again later.",
        "ja": "同じスポットは7日に1回のみ推薦できます。しばらくしてからお試しください。",
      },
    });
  }
  const id = randomId();
  const payload = {
    routing_key: "nomination", report_category: "other", source: "custom-place-nomination",
    name: row.name, lat: row.lat, lng: row.lng, elevation: row.elevation,
    comment_text: `提名升級官方：${row.name}（${row.lat}, ${row.lng}${row.elevation != null ? ` · ${row.elevation} m` : ""}）`,
  };
  await env.DB.prepare(
    "INSERT INTO feedback (id, user_id, place_id, type, status, payload) VALUES (?1, ?2, ?3, 'report', 'pending', ?4)"
  ).bind(id, uid, feedbackId, JSON.stringify(payload)).run();
  return json(req, 200, { ok: true, nominationId: id, routingKey: "nomination", status: "pending" });
}

// ---------------------------------------------------------------------------
// ✨ AI one-sentence parse (owner ruling 2026-11-15, in THIS ticket): a free
// description in ANY language → the LLM returns a STRICT-JSON suggestion
// (semantic cloud/fog/rain tiers + wind/window/lead + confidence) which fills
// the conditions form's semantic dropdowns. The AI ONLY TRANSLATES — it never
// judges: the form still submits concrete values through readCc()/the
// semantic mapping. Fail-closed: no LLM_API_KEY → the endpoint 503s and the
// UI hides the entry; every schema violation is rejected honestly; per-user
// 10 parses/day keeps the cost bounded.
// ---------------------------------------------------------------------------
export const PARSE_DAILY_LIMIT = 10;
const PARSE_NUM_LIMITS = { wind_max_ms: [0, 75], lead_minutes: [0, 4320] };
const PARSE_ENUMS = {
  cloud: ['min', 'half', 'any'],
  fog: ['none', 'thin', 'any'],
  rain: ['no', 'drizzle', 'any'],
};
const PARSE_MESSAGES = {
  disabled: {
    "zh-TW": "AI 描述解析尚未啟用（金鑰未設定）——請手動設定條件。",
    "en": "AI description parsing is not enabled (key not configured) — please set conditions manually.",
    "ja": "AI説明解析は未有効（キー未設定）— 手動で条件を設定してください。",
  },
  limit: {
    "zh-TW": "今日的 AI 解析次數已用完（每日 10 次），明天再試。",
    "en": "You have used today's 10 AI parses — please try again tomorrow.",
    "ja": "本日のAI解析回数（10回）を使い切りました。明日再度お試しください。",
  },
  fail: {
    "zh-TW": "解析失敗，請手動設定。",
    "en": "Parsing failed — please set the conditions manually.",
    "ja": "解析に失敗しました。手動で設定してください。",
  },
};

export function validateParseSuggestions(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return { ok: false };
  const out = {};
  for (const [k, allowed] of Object.entries(PARSE_ENUMS)) {
    if (!allowed.includes(body[k])) return { ok: false };
    out[k] = body[k];
  }
  for (const [k, [lo, hi]] of Object.entries(PARSE_NUM_LIMITS)) {
    if (body[k] == null) continue; // optional
    const n = Number(body[k]);
    if (!Number.isFinite(n) || n < lo || n > hi) return { ok: false };
    out[k] = n;
  }
  if (Number.isFinite(Number(body.wind_max_ms)) && body.wind_max_ms != null) out.wind_max_ms = Number(body.wind_max_ms);
  // patch-2 (owner steer): the LLM may return the multi-segment windows array
  // (fixed + sun-anchored segments, ≤2) or the legacy flat window_start/end.
  // Both never appear together; conflict excludes any concrete window.
  if (body.windows != null && (body.window_start != null || body.window_end != null)) return { ok: false };
  if (body.windows != null) {
    if (!Array.isArray(body.windows) || body.windows.length > 2) return { ok: false };
    const segs = [];
    for (const s of body.windows) {
      const v = validateWindowSegment(s);
      if (!v.ok) return { ok: false };
      segs.push(v.seg);
    }
    // patch-5 semantic guard: an EMPTY windows array is "no concrete window"
    // (the cloud-sea advice shape is conflict + empty windows) — only a
    // NON-empty array counts as a concrete window and excludes conflict.
    if (segs.length) out.windows = segs;
  } else {
    const hm = /^([01]\d|2[0-3]):[0-5]\d$/;
    if (body.window_start != null || body.window_end != null) {
      if (typeof body.window_start !== "string" || typeof body.window_end !== "string") return { ok: false };
      if (!hm.test(body.window_start) || !hm.test(body.window_end)) return { ok: false };
      out.window_start = body.window_start; out.window_end = body.window_end;
    }
  }
  // patch-5 ③: conflict — when the text demands incompatible conditions
  // (e.g. non-overlapping time windows), the LLM sets window keys null and
  // returns a SHORT user-language conflict message instead. The UI applies
  // nothing and asks the user to pick one (解析結果必經確認).
  if (body.conflict != null) {
    if (typeof body.conflict !== "string" || !body.conflict.trim() || body.conflict.length > 200) {
      return { ok: false };
    }
    if (out.window_start != null || out.windows != null) return { ok: false }; // conflict excludes a concrete window
    out.conflict = body.conflict.trim();
  }
  const conf = Number(body.confidence);
  if (!Number.isFinite(conf) || conf < 0 || conf > 1) return { ok: false };
  out.confidence = conf;
  return { ok: true, suggestions: out };
}

const PARSE_SYSTEM_PROMPT =
  'You translate a photographer\'s free-text weather description into shooting-condition suggestions. ' +
  'Output STRICT JSON only, with exactly these keys: ' +
  'cloud ("min"|"half"|"any" — how much low cloud the photographer tolerates), ' +
  'fog ("none"|"thin"|"any"), rain ("no"|"drizzle"|"any"), ' +
  'wind_max_ms (number|null, m/s), ' +
  'windows (array of 0..2 time-window SEGMENTS; empty array when the text names no time window), ' +
  'lead_minutes (integer|null), conflict (string|null), confidence (0..1). ' +
  'Each window segment is an object {type, start, end, offset_minutes, span_minutes} with type one of: ' +
  '"fixed" (BOTH start and end required, "HH:MM" strings, offset_minutes and span_minutes must be null) — ' +
  'a concrete local clock span; ' +
  '"before_sunrise" | "after_sunrise" | "before_sunset" | "after_sunset" (SUN-ANCHORED: ' +
  'offset_minutes = integer minutes relative to the anchor event, null = 0; start/end must be null). ' +
  'span_minutes (optional, integer 1..720) makes a SHORT window hugging the anchor: for a before_* ' +
  'segment the window ends at the anchor bound and spans that many minutes BACK; for an after_* ' +
  'segment it starts at the anchor bound and spans FORWARD. ' +
  'ANCHOR RULE (critical): phrases like 日出前/日出後/日落前/日落後, before/after sunrise or sunset, ' +
  '夜深到天亮前 must become SUN-ANCHORED segments — NEVER convert them into fixed clock times, ' +
  'because real sunrise/sunset shift with the seasons and the app expands them per day. ' +
  'offset_minutes sign: before_sunrise -30 means "end 30 minutes before sunrise"; ' +
  'after_sunrise 30 means "start 30 minutes after sunrise". ' +
  'TWO time spans in the text (清晨與傍晚 / twice a day / dawn AND dusk / blue hour morning and evening) ' +
  'become TWO segments in ONE windows array — never merge them into one wide window. ' +
  'GOLDEN-LIGHT RULE (owner ruling, patch-5): a golden/glow phrase — 金色/黃金/霞光/曙光/golden hour/第一道金光 — ' +
  'means the sun-event moment itself: emit exactly ONE short sun-anchored segment within ±30 minutes of the ' +
  'anchor — morning golden = {type:"after_sunrise", offset_minutes:-30, span_minutes:60} (window ' +
  'sunrise−30…sunrise+30); evening golden = {type:"before_sunset", offset_minutes:30, span_minutes:60} ' +
  '(window sunset−30…sunset+30). NEVER answer a golden phrase with two whole-period segments ' +
  '(e.g. before_sunrise + after_sunset) and never with a full-day span — pick the ONE anchor the text ' +
  'names (morning words → sunrise, evening words → sunset); when the text names neither, prefer the ' +
  'sunset anchor for 霞光/晚霞-like words and the sunrise anchor for 曙光/朝霞-like words. ' +
  'CLOUD-SEA GUARD (owner ruling, patch-5): 雲海/海霧/sea of clouds/雲の海-type phrases describe a cloud ' +
  'DECK SITTING BELOW THE VIEWPOINT — this engine cannot express that (its cloud values are flat ' +
  'percentages at one grid point, no cloud-base-height formula). Do NOT encode it as a maximum-cloud ' +
  'condition (never cloud "min"/≤20%) and do NOT invent an inverted trick either: keep cloud "any" ' +
  '(keep any GENUINELY stated constraints like rain/wind/visibility), leave windows empty unless the ' +
  'text itself names a concrete time span, and put a SHORT (<200 chars) message in conflict — written ' +
  'in the USER\'S OWN language — honestly advising them to attach the official 雲海 (cloud sea) genre ' +
  'instead, e.g. zh-TW 「自訂條件引擎無法表達雲海（雲海需低雲層厚且低於拍攝點），請改掛官方『雲海』題材」, ' +
  'en "Custom conditions cannot express a cloud sea (the deck must sit below the viewpoint) — please ' +
  'attach the official Cloud-sea genre instead.", ja 「自訂條件では雲海を表現できません（低雲が撮影点より下に厚く必要）公式の『雲海』題材をご利用ください」. ' +
  'MULTIPLE overlapping constraints on ONE span are INTERSECTED into that one segment. ' +
  'If the requested conditions CONTRADICT each other and have no valid overlap, ' +
  'set windows to [] and put a SHORT (<200 chars) message in conflict — ' +
  'written in the USER\'S OWN language — telling them the conditions conflict and to pick one. ' +
  'Otherwise conflict must be null. ' +
  'Interpret the text in ANY language. Never invent keys. Numbers must respect the stated units.';

export async function conditionsParseConfig(env) {
  return { enabled: Boolean(env.LLM_API_KEY) };
}

export async function handleConditionsParseConfig(req, env) {
  const cfg = await conditionsParseConfig(env);
  return json(req, 200, { ok: true, enabled: cfg.enabled });
}

// Provider ruling (owner): the parse LLM rides OpenRouter (LLM_API_KEY is an
// OpenRouter key; google/gemini-2.5-flash was picked for multilingual + strict
// JSON). The model name is KV-swappable (v1:cparse:model) for zero-code swaps,
// with env.LLM_MODEL as the deploy-time override and the constant as fallback.
// 2026-11-18 root cause of 「解析功能無法用」: the handler called Google's
// generativelanguage endpoint with the OpenRouter key — every live call 401'd
// into the generic 502. OpenRouter's chat/completions is the actual contract.
const PARSE_MODEL_KV_KEY = 'v1:cparse:model';
const PARSE_DEFAULT_MODEL = 'google/gemini-2.5-flash';
const PARSE_UPSTREAM = 'https://openrouter.ai/api/v1/chat/completions';

export async function conditionsParseModel(env) {
  let m = null;
  try { m = await env.EVALS.get(PARSE_MODEL_KV_KEY); } catch { /* KV hiccups must not kill the feature */ }
  if (typeof m === 'string' && m.trim()) return m.trim();
  if (typeof env.LLM_MODEL === 'string' && env.LLM_MODEL.trim()) return env.LLM_MODEL.trim();
  return PARSE_DEFAULT_MODEL;
}

export async function handleConditionsParse(req, env) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: 'JWT session required' });
  if (!env.LLM_API_KEY) return json(req, 503, { ok: false, error: 'ai parse disabled', message: PARSE_MESSAGES.disabled });
  const body = await req.json().catch(() => null);
  const text = body && typeof body.text === 'string' ? body.text.trim().slice(0, 500) : '';
  if (!text) return json(req, 400, { ok: false, error: 'text required' });

  // per-user daily parse budget (owner cost control)
  const day = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const key = `v1:cparse:${session.sub}:${day}`;
  let used = 0;
  try {
    const v = await env.EVALS.get(key, 'json');
    if (v && typeof v.count === 'number') used = v.count;
  } catch { used = 0; }
  if (used >= PARSE_DAILY_LIMIT) {
    return json(req, 403, { ok: false, error: 'daily parse limit reached', limit: PARSE_DAILY_LIMIT, message: PARSE_MESSAGES.limit });
  }

  const model = await conditionsParseModel(env);
  let parsed = null;
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15_000);
    const res = await fetch(PARSE_UPSTREAM, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${env.LLM_API_KEY}`,
        'HTTP-Referer': 'https://chaselights.app',
        'X-Title': 'ChaseLights',
      },
      signal: controller.signal,
      body: JSON.stringify({
        model,
        messages: [
          { role: 'system', content: PARSE_SYSTEM_PROMPT },
          { role: 'user', content: text },
        ],
        temperature: 0,
        response_format: { type: 'json_object' },
      }),
    });
    clearTimeout(timer);
    if (!res.ok) {
      const snippet = (await res.text().catch(() => '')).replace(/\s+/g, ' ').slice(0, 200);
      throw new Error(`LLM HTTP ${res.status}: ${snippet}`);
    }
    const data = await res.json();
    const content = data && data.choices && data.choices[0] && data.choices[0].message &&
      data.choices[0].message.content;
    parsed = typeof content === 'string' ? JSON.parse(content) : null;
  } catch (e) {
    // fail-closed with a CONCRETE reason: the tri-lingual user message stays
    // stable, but detail (status/upstream snippet, key never included) rides
    // both the response and the console log so debugging needs no guessing.
    const detail = e && e.name === 'AbortError' ? 'LLM timeout (15s)' : String(e && e.message || e).slice(0, 200);
    try { console.error('[conditions/parse] upstream failed:', detail); } catch { /* log is best-effort */ }
    return json(req, 502, { ok: false, error: 'parse failed', detail, message: PARSE_MESSAGES.fail });
  }
  const check = validateParseSuggestions(parsed);
  if (!check.ok) {
    try { console.error('[conditions/parse] schema violation:', JSON.stringify(parsed).slice(0, 200)); } catch { /* best-effort */ }
    return json(req, 422, { ok: false, error: 'schema violation', detail: 'model output violated the strict suggestion schema', message: PARSE_MESSAGES.fail });
  }
  try { await env.EVALS.put(key, JSON.stringify({ count: used + 1 })); } catch { /* best-effort */ }
  return json(req, 200, { ok: true, suggestions: check.suggestions });
}

// ---------------------------------------------------------------------------
// pin_info: ONE Open-Meteo call resolves BOTH read-only facts the add modal
// shows — DEM elevation and the IANA timezone (timezone=auto). The user
// never types either (anti-drift ruling), and the values double as the
// sanity check for outliers (§7).
// ---------------------------------------------------------------------------
export async function handleCustomPlacePinInfo(req, env, url) {
  const session = await requireSession(req, env);
  if (!session) return json(req, 401, { error: "JWT session required" });
  const lat = Number(url.searchParams.get("lat"));
  const lng = Number(url.searchParams.get("lng"));
  if (!Number.isFinite(lat) || lat < -90 || lat > 90 || !Number.isFinite(lng) || lng < -180 || lng > 180) {
    return json(req, 400, { error: "lat must be -90..90 and lng -180..180" });
  }
  try {
    const api = env.OPEN_METEO_API_BASE || "https://api.open-meteo.com/v1/forecast";
    const res = await fetch(`${api}?latitude=${lat}&longitude=${lng}&timezone=auto`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const body = await res.json();
    const elevation = Number(body.elevation);
    return json(req, 200, {
      ok: true,
      elevation: Number.isFinite(elevation) ? elevation : null,
      timezone: typeof body.timezone === "string" ? body.timezone : null,
      utcOffsetSeconds: typeof body.utc_offset_seconds === "number" ? body.utc_offset_seconds : null,
      elevationOutlier: Number.isFinite(elevation) && (elevation < ELEV_MIN_M || elevation > ELEV_MAX_M),
    });
  } catch (e) {
    return json(req, 502, { error: `DEM/timezone lookup failed: ${e && e.message}` });
  }
}

// ---------------------------------------------------------------------------
// Cron: process the low-priority custom fetch queue. Batch stays small —
// custom places ride BEHIND the official pipeline. Brake ladder:
//   <70% budget  → normal batch
//   ≥70%         → batch ×0.9 (global 10% downshift, all members equally)
//   ≥90%         → stop non-core refreshes entirely (first fetches of brand
//                  new points still trickle at a minimal batch so a member
//                  never sees a dead point; honest degraded labels everywhere)
// ---------------------------------------------------------------------------
export const QUEUE_BATCH = 20;
const OM_HOURLY = "cloud_cover_low,cloud_cover_mid,cloud_cover_high,precipitation,visibility,wind_speed_10m,temperature_2m,weather_code";

// Owner ruling (2026-11-24): every card shows weather + temperature, and a
// place with no subject shows 「尚未設定題材」 plus visibility / WMO weather /
// today's temperature range — never a verdict it cannot support. Pure function
// so the list handler and the popup read the SAME numbers.
export function weatherSummary(rec, tz, nowMs = Date.now()) {
  const rows = (rec && Array.isArray(rec.hourly)) ? rec.hourly : [];
  if (!rows.length) return null;
  // "today" in the place's own timezone (falls back to the record's first day)
  let today = null;
  try {
    today = new Intl.DateTimeFormat("en-CA", { timeZone: tz || "UTC", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(nowMs));
  } catch { today = null; }
  let day = today ? rows.filter((r) => r && r.local_date === today) : [];
  if (!day.length) day = rows.filter((r) => r && r.local_date === rows[0].local_date);
  const nums = (pick) => day.map((r) => (r.values ? pick(r.values) : null)).filter((v) => v != null && Number.isFinite(Number(v))).map(Number);
  const temps = nums((v) => v.temp);
  const vis = nums((v) => v.visibility);
  const codes = day.filter((r) => r && r.values && r.values.weather_code != null).map((r) => Number(r.values.weather_code));
  // WMO dominant code — the day's most frequent code; ties go to the more
  // severe one (higher code = wetter/rougher), never a fabricated "clear".
  let code = null;
  if (codes.length) {
    const freq = new Map();
    codes.forEach((c) => freq.set(c, (freq.get(c) || 0) + 1));
    let best = null;
    freq.forEach((n, c) => { if (!best || n > best.n || (n === best.n && c > best.c)) best = { c, n }; });
    code = best.c;
  }
  return {
    date: (day[0] && day[0].local_date) || null,
    temp_min: temps.length ? Math.min(...temps) : null,
    temp_max: temps.length ? Math.max(...temps) : null,
    visibility_min_m: vis.length ? Math.min(...vis) : null,
    visibility_max_m: vis.length ? Math.max(...vis) : null,
    weather_code: code,
  };
}

export async function processCustomFetchQueue(env, nowMs = Date.now(), opts = {}) {
  const summary = { processed: 0, failed: 0, skipped_brake: 0, skipped_inactive: 0, done: [] };
  const globalState = await globalUsageState(env, nowMs);
  summary.globalUsage = globalState;
  let batch = typeof opts.batch === "number" ? opts.batch : QUEUE_BATCH;
  if (globalState.soft && !globalState.hard) batch = Math.max(1, Math.ceil(batch * 0.9)); // global 10% downshift
  if (globalState.hard && !opts.ignoreBrake) batch = 3;                                   // hard stop: only first-fetch trickle

  let due = [];
  try {
    ({ results: due } = await env.DB.prepare(
      "SELECT q.place_id, q.reason FROM custom_fetch_queue q WHERE q.status = 'pending' AND q.due_at <= datetime('now') ORDER BY q.priority ASC, q.due_at ASC LIMIT ?1"
    ).bind(batch).all());
  } catch (e) {
    summary.error = e && e.message;
    return summary;
  }
  if (!due || !due.length) return summary;

  let registry = {};
  try { registry = (await env.EVALS.get("v1:cp:usage24h", "json")) || {}; } catch { registry = {}; }

  for (const q of due) {
    const row = await env.DB.prepare(
      "SELECT id, user_id, name, lat, lng, status, custom_conditions, group_id, share_mode FROM custom_places WHERE id = ?1"
    ).bind(q.place_id).first();
    if (!row) { await env.DB.prepare("UPDATE custom_fetch_queue SET status = 'done', updated_at = datetime('now') WHERE place_id = ?1").bind(q.place_id).run(); continue; }
    if (row.status !== "active") { summary.skipped_inactive += 1; await env.DB.prepare("UPDATE custom_fetch_queue SET status = 'done', updated_at = datetime('now') WHERE place_id = ?1").bind(q.place_id).run(); continue; }
    // CL-APP-08 grid dedup: a grouped place NEVER fetches on its own — its
    // entry is marked done and the group's REPRESENTATIVE gets (or keeps) a
    // pending queue entry; the rep's single fetch fans out to every member.
    // No quota is charged for the redirect (the rep's fetch charges once).
    if (row.group_id && row.share_mode === "auto") {
      const rep = await representativeOf(env, row);
      if (rep && rep.id !== row.id) {
        await env.DB.prepare(
          "INSERT INTO custom_fetch_queue (place_id, user_id, reason, priority) VALUES (?1, ?2, 'refresh', 20) ON CONFLICT(place_id) DO UPDATE SET status = 'pending', updated_at = datetime('now')"
        ).bind(rep.id, rep.user_id).run();
        summary.skipped_shared = (summary.skipped_shared || 0) + 1;
        await env.DB.prepare("UPDATE custom_fetch_queue SET status = 'done', updated_at = datetime('now') WHERE place_id = ?1").bind(row.id).run();
        continue;
      }
    }
    if (globalState.hard && q.reason === "refresh" && !opts.ignoreBrake) { summary.skipped_brake += 1; continue; }

    // Owner-ruled layer 3: per-user daily fetch budget. Over-budget entries
    // are DEFERRED to the next day — the point itself stays created (the add
    // already succeeded) and the card honestly reports the delayed update.
    const usedToday = await userFetchCount(env, row.user_id, nowMs);
    if (usedToday >= USER_DAILY_FETCH_BUDGET && !opts.ignoreUserBudget) {
      const next = new Date(nowMs);
      next.setUTCHours(24, 5, 0, 0); // next UTC day, just past midnight
      await env.DB.prepare(
        "UPDATE custom_fetch_queue SET due_at = ?2, updated_at = datetime('now') WHERE place_id = ?1"
      ).bind(q.place_id, next.toISOString().slice(0, 19).replace("T", " ")).run();
      summary.deferred = (summary.deferred || 0) + 1;
      summary.deferredPlaces = summary.deferredPlaces || [];
      summary.deferredPlaces.push(q.place_id);
      continue;
    }

    try {
      const api = env.OPEN_METEO_API_BASE || "https://api.open-meteo.com/v1/forecast";
      const res = await fetch(`${api}?latitude=${row.lat}&longitude=${row.lng}&hourly=${OM_HOURLY}&timezone=auto&forecast_days=2`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const body = await res.json();
      const h = body.hourly || {};
      const times = h.time || [];
      const hourly = times.map((t, i) => {
        const [date, hm] = String(t).split("T");
        const num = (x) => (x != null && Number.isFinite(Number(x)) ? Number(x) : null);
        return {
          local_date: date,
          hour: `${String(hm || "").slice(0, 5)}`,
          values: {
            cloud_low: num((h.cloud_cover_low || [])[i]),
            cloud_mid: num((h.cloud_cover_mid || [])[i]),
            cloud_high: num((h.cloud_cover_high || [])[i]),
            precipitation: num((h.precipitation || [])[i]),
            visibility: num((h.visibility || [])[i]),
            wind: num((h.wind_speed_10m || [])[i]),
            temp: num((h.temperature_2m || [])[i]),
            weather_code: num((h.weather_code || [])[i]),
          },
        };
      });
      const elevation = Number.isFinite(Number(body.elevation)) ? Number(body.elevation) : null;
      const timezone = typeof body.timezone === "string" ? body.timezone : null;
      await env.DB.prepare(
        "UPDATE custom_places SET elevation = ?2, timezone = ?3, updated_at = datetime('now') WHERE id = ?1 AND status = 'active'"
      ).bind(row.id, elevation, timezone).run();
      const evalBody = {
        place_id: row.id, private: true, name: row.name,
        lat: row.lat, lng: row.lng, elevation, timezone,
        hourly, generated_at: new Date(nowMs).toISOString(),
      };
      await env.EVALS.put(`v1:evals:custom:${row.id}`, JSON.stringify(evalBody));
      // CL-APP-08: one fetch serves the WHOLE group — every active member
      // gets its own eval record with the member's own lat/lng/elevation
      // (judgment inputs untouched) and the identical raw hourly grid.
      const fanned = await fanOutGroupEval(env, { ...row, group_id: row.group_id }, evalBody, nowMs);
      if (fanned) summary.fanned_out = (summary.fanned_out || 0) + fanned;
      await bumpGlobalUsage(env, 1, nowMs);
      await bumpUserFetch(env, row.user_id, 1, nowMs);
      const c = registry[row.user_id];
      registry[row.user_id] = { count: ((c && c.count) || 0) + 1, day: dayKey(nowMs) };
      summary.processed += 1;
      summary.done.push(row.id);
    } catch (e) {
      summary.failed += 1;
      summary.errors = summary.errors || [];
      summary.errors.push(`${row.id}: ${e && e.message}`);
    }
    await env.DB.prepare("UPDATE custom_fetch_queue SET status = 'done', updated_at = datetime('now') WHERE place_id = ?1").bind(q.place_id).run();
  }
  try { await env.EVALS.put("v1:cp:usage24h", JSON.stringify(registry)); } catch { /* best-effort */ }
  return summary;
}
