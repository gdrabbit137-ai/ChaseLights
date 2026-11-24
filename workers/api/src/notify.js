// CL-API-03: notification engine — cron matcher, dedupe, Telegram delivery.
// Data source: KV distilled evaluations (v1:evals:<place_id>), RESULTS ONLY —
// no thresholds/operators ever enter this module or the messages it sends.
//
// Time convention: distilled days carry spot-LOCAL wall clock (local_date + hour
// int). This v1 matches them on the site-wide GMT+8 convention; JP (UTC+9)
// spots may drift up to 1h inside the match window — follow-up: per-spot tz.
import { sendPush } from "./push.js";
import { sunTimesForDate } from "./solar.js";

export const MATCH_WINDOW_H = 24;

// ---------------------------------------------------------------------------
// CL-UI-99: custom-conditions mode. A rule may carry a custom_conditions JSON
// payload (nullable custom_conditions column) instead of an opportunity_id.
// The engine then judges PLACE-LEVEL hourly weather values (KV distilled
// rec.hourly rows from the W1 weather_details hourly_forecast) against the
// user parameters — same window/lead-time semantics as subject mode.
// Parameter contract (all optional; absent = no constraint):
//   cloud_low_max / cloud_mid_max / cloud_high_max : % 0..100 (>=100 = none)
//   cloud_low_min / cloud_mid_min / cloud_high_min : % 0..100 (<=0 = none) —
//     patch-5 ⑤: the 越多越好 direction (cloud-sea-style decks judged from the
//     same flat hourly % grid; the viewpoint-height nuance stays official-genre)
//   precip_max_mmh    : mm/h 0..200
//   visibility_min_km : km 0..50 (<=0 = none)
//   wind_max_ms       : m/s 0..75
//   window_start/window_end : "HH:MM" both-or-none (midnight wrap allowed)
//   lead_minutes      : int 0..4320 (fallback: min_advance_hours * 60)
// ---------------------------------------------------------------------------
const CC_NUM_LIMITS = {
  cloud_low_max: [0, 100],
  cloud_mid_max: [0, 100],
  cloud_high_max: [0, 100],
  cloud_low_min: [0, 100],
  cloud_mid_min: [0, 100],
  cloud_high_min: [0, 100],
  precip_max_mmh: [0, 200],
  visibility_min_km: [0, 50],
  wind_max_ms: [0, 75],
};
const CC_HM_RE = /^([01]\d|2[0-3]):[0-5]\d$/;

// Contract validation for POST /notify/rules. Returns {ok, cc} where cc is
// the normalized payload (or null when the input is absent/empty).
export function validateCustomConditions(input) {
  if (input == null) return { ok: true, cc: null };
  if (typeof input !== "object" || Array.isArray(input)) {
    return { ok: false, error: "customConditions must be an object" };
  }
  const out = {};
  for (const [k, [lo, hi]] of Object.entries(CC_NUM_LIMITS)) {
    const v = input[k];
    if (v === undefined || v === null) continue;
    const n = Number(v);
    if (!Number.isFinite(n) || n < lo || n > hi) {
      return { ok: false, error: `customConditions.${k} must be a number ${lo}..${hi}` };
    }
    out[k] = n;
  }
  for (const k of ["window_start", "window_end"]) {
    const v = input[k];
    if (v === undefined || v === null) continue;
    if (typeof v !== "string" || !CC_HM_RE.test(v)) {
      return { ok: false, error: `customConditions.${k} must be an HH:MM string` };
    }
    out[k] = v;
  }
  if ((out.window_start != null) !== (out.window_end != null)) {
    return { ok: false, error: "customConditions window needs both window_start and window_end" };
  }
  const lead = input.lead_minutes;
  if (lead !== undefined && lead !== null) {
    const n = Number(lead);
    if (!Number.isInteger(n) || n < 0 || n > 4320) {
      return { ok: false, error: "customConditions.lead_minutes must be an integer 0..4320" };
    }
    out.lead_minutes = n;
  }
  // patch-5 ④: months — array of ints 1..12 (multi-select). Absent/empty =
  // all year (the owner's default). Duplicates collapse; order is normalized.
  if (input.months !== undefined && input.months !== null) {
    if (!Array.isArray(input.months) || !input.months.length) {
      return { ok: false, error: "customConditions.months must be a non-empty array of 1..12 (omit for all year)" };
    }
    const ms = [...new Set(input.months.map(Number))];
    for (const m of ms) {
      if (!Number.isInteger(m) || m < 1 || m > 12) {
        return { ok: false, error: "customConditions.months entries must be integers 1..12" };
      }
    }
    out.months = ms.sort((a, b) => a - b);
  }
  // ------------------------------------------------------------------
  // CL-APP-09 patch-2 (owner steer): ANCHOR + MULTI-SEGMENT time windows.
  //   windows: array of 1..2 segments { type, start?, end?, offset_minutes? }
  //     type: fixed | before_sunrise | after_sunrise | before_sunset |
  //           after_sunset
  //     fixed       → start+end HH:MM BOTH required; offset_minutes forbidden
  //     before_*    → optional offset_minutes (shifts the anchor END bound)
  //                   and optional start (narrows the window start); end
  //                   forbidden (the anchor IS the end bound)
  //     after_*     → mirror: optional offset_minutes + optional end; start
  //                   forbidden (the anchor IS the start bound)
  //   offset_minutes: integer -720..720 (absent = 0). The engine expands the
  //   anchor with the place's REAL sun times per row's local date (solar.js),
  //   so a set saved in winter still tracks the later summer sunrise.
  // Back-compat: a cc WITHOUT windows but WITH window_start/window_end keeps
  // the legacy single fixed segment; mixing windows with the flat fields is
  // rejected (ambiguous payload, fail-closed). The legacy FLAT anchor form
  // (window_type+offset_minutes, no start/end) is still accepted as a single
  // segment; narrowing an anchor needs the windows array.
  // ------------------------------------------------------------------
  const wt = input.window_type;
  if (wt !== undefined) {
    if (!WINDOW_TYPES.includes(wt)) return { ok: false, error: `customConditions.window_type must be one of ${WINDOW_TYPES.join("|")}` };
  }
  const flatOff = input.offset_minutes;
  if (flatOff !== undefined && flatOff !== null) {
    if (!Number.isInteger(flatOff) || flatOff < -720 || flatOff > 720) {
      return { ok: false, error: "customConditions.offset_minutes must be an integer -720..720" };
    }
  }
  if (input.windows != null) {
    if (wt !== undefined || input.window_start != null || input.window_end != null || flatOff != null) {
      return { ok: false, error: "customConditions.windows excludes the flat window fields (window_type/window_start/window_end/offset_minutes)" };
    }
    if (!Array.isArray(input.windows) || !input.windows.length || input.windows.length > 2) {
      return { ok: false, error: "customConditions.windows must be an array of 1..2 segments" };
    }
    const segs = [];
    for (const s of input.windows) {
      const v = validateWindowSegment(s);
      if (!v.ok) return { ok: false, error: `customConditions.windows: ${v.error}` };
      segs.push(v.seg);
    }
    out.windows = segs;
  } else if (wt !== undefined) {
    if (wt === "fixed") return { ok: false, error: "customConditions: a flat fixed window uses window_start/window_end without window_type" };
    if (input.window_start != null || input.window_end != null) {
      return { ok: false, error: `customConditions: anchor window_type ${wt} cannot carry flat start/end bounds — use the windows array to narrow an anchor` };
    }
    out.windows = [validateWindowSegment({ type: wt, offset_minutes: flatOff != null ? flatOff : 0 }).seg];
  }
  return { ok: true, cc: Object.keys(out).length ? out : null };
}

export const WINDOW_TYPES = ["fixed", "before_sunrise", "after_sunrise", "before_sunset", "after_sunset"];

// One {type,start,end,offset_minutes} segment. Returns {ok, seg} | {ok:false,error}.
export function validateWindowSegment(s) {
  if (!s || typeof s !== "object" || Array.isArray(s)) return { ok: false, error: "segment must be an object" };
  const type = s.type != null ? s.type : "fixed";
  if (!WINDOW_TYPES.includes(type)) return { ok: false, error: `type must be one of ${WINDOW_TYPES.join("|")}` };
  const seg = { type };
  if (type === "fixed") {
    if (s.offset_minutes != null) return { ok: false, error: "fixed segments take start/end, not offset_minutes" };
    if (s.span_minutes != null) return { ok: false, error: "fixed segments take start/end, not span_minutes" };
    if (typeof s.start !== "string" || typeof s.end !== "string" || !CC_HM_RE.test(s.start) || !CC_HM_RE.test(s.end)) {
      return { ok: false, error: "fixed segments need both start and end as HH:MM strings" };
    }
    seg.start = s.start;
    seg.end = s.end;
    return { ok: true, seg };
  }
  if (s.offset_minutes != null) {
    const n = s.offset_minutes;
    if (!Number.isInteger(n) || n < -720 || n > 720) return { ok: false, error: "offset_minutes must be an integer -720..720" };
    seg.offset_minutes = n;
  }
  // CL-APP-09 patch-5 ⑤: optional SHORT-WINDOW span for anchor segments —
  // before_* ends at the anchor bound and spans span_minutes BACK; after_*
  // starts at the anchor bound and spans span_minutes FORWARD. This is how a
  // golden-hour phrase (霞光/金色 ±30 min around the sun event) becomes ONE
  // short sun-anchored window instead of two full-day spans. Mutually
  // exclusive with the fixed-clock narrowing bound (fail-closed ambiguity).
  if (s.span_minutes != null) {
    const sp = s.span_minutes;
    if (!Number.isInteger(sp) || sp < 1 || sp > 720) return { ok: false, error: "span_minutes must be an integer 1..720" };
    if (type.startsWith("before_") && s.start != null) return { ok: false, error: "span_minutes excludes a fixed start on a before_* anchor (the span IS the start)" };
    if (!type.startsWith("before_") && s.end != null) return { ok: false, error: "span_minutes excludes a fixed end on an after_* anchor (the span IS the end)" };
    seg.span_minutes = sp;
  }
  if (type.startsWith("before_")) {
    if (s.end != null) return { ok: false, error: `${type} has no end (the sun anchor IS the end); use start to narrow the window start` };
    if (s.start != null) {
      if (typeof s.start !== "string" || !CC_HM_RE.test(s.start)) return { ok: false, error: "start must be an HH:MM string" };
      seg.start = s.start;
    }
  } else {
    if (s.start != null) return { ok: false, error: `${type} has no start (the sun anchor IS the start); use end to narrow the window end` };
    if (s.end != null) {
      if (typeof s.end !== "string" || !CC_HM_RE.test(s.end)) return { ok: false, error: "end must be an HH:MM string" };
      seg.end = s.end;
    }
  }
  return { ok: true, seg };
}

// The cc's window segments, normalized: windows array wins; legacy flat
// window_type/window_start/window_end/offset_minutes maps to one segment;
// legacy flat fixed bounds (no window_type) map to one fixed segment.
export function segmentsOf(cc) {
  if (!cc || typeof cc !== "object") return null;
  if (Array.isArray(cc.windows) && cc.windows.length) return cc.windows;
  if (cc.window_type && cc.window_type !== "fixed") {
    return [{ type: cc.window_type, start: cc.window_start, end: cc.window_end, offset_minutes: cc.offset_minutes != null ? cc.offset_minutes : 0 }];
  }
  if (cc.window_start != null || cc.window_end != null) {
    return [{ type: "fixed", start: cc.window_start, end: cc.window_end }];
  }
  return null; // no window constraint
}

// Anchor segment → concrete [start,end] HH:MM for ONE row local date, using
// the place's REAL sun times (solar.js). Returns null when the segment cannot
// resolve (no place coordinates / polar day-night): the caller must treat it
// as "no match", never as "whole day" (fail-closed, no fabricated window).
export function resolveSegmentBounds(seg, localDate, placeCtx) {
  if (!seg || typeof seg !== "object") return null;
  if (seg.type === "fixed") {
    return { start: seg.start || null, end: seg.end || null };
  }
  if (!placeCtx || !Number.isFinite(placeCtx.lat) || !Number.isFinite(placeCtx.lng)) return null;
  const sun = sunTimesForDate(localDate, placeCtx.lat, placeCtx.lng, placeCtx.utcOffsetHours);
  if (!sun) return null;
  const off = Number.isFinite(seg.offset_minutes) ? seg.offset_minutes : 0;
  const anchorMin = seg.type.endsWith("sunrise") ? sun.sunriseMin : sun.sunsetMin;
  const norm = (x) => ((Math.round(x) % 1440) + 1440) % 1440;
  const toHM = (x) => `${String(Math.floor(x / 60)).padStart(2, "0")}:${String(x % 60).padStart(2, "0")}`;
  if (seg.type.startsWith("before_")) {
    // patch-5 ⑤: span_minutes makes the SHORT window [anchor+off−span, anchor+off];
    // without it the legacy full-span start (00:00 or the fixed narrowing start) holds.
    const start = Number.isFinite(seg.span_minutes)
      ? toHM(norm(anchorMin + off - seg.span_minutes))
      : (seg.start || "00:00");
    return { start, end: toHM(norm(anchorMin + off)), anchorHM: toHM(norm(anchorMin)) };
  }
  const startHM = toHM(norm(anchorMin + off));
  const end = Number.isFinite(seg.span_minutes)
    ? toHM(norm(anchorMin + off + seg.span_minutes))
    : (seg.end || "23:59");
  return { start: startHM, end, anchorHM: toHM(norm(anchorMin)) };
}

// Does ONE hour row pass the cc's window segments (ANY segment passes)? This
// is the multi-segment replacement for the raw hourInWindow gate: fixed
// segments behave exactly as before; anchor segments expand per the row's
// local date with real sun times. Unresolvable anchor segments never match
// (fail-closed: a window we cannot resolve must not silently become all-day).
export function hourPassesWindows(row, cc, placeCtx = null) {
  const segs = segmentsOf(cc);
  if (!segs) return true; // no window constraint at all
  if (!row || typeof row.local_date !== "string" || typeof row.hour !== "string") return false;
  for (const seg of segs) {
    const b = resolveSegmentBounds(seg, row.local_date, placeCtx);
    if (!b) continue; // unresolvable (missing coords / polar) — never matches
    if (hourInWindow(row.hour, b.start, b.end)) return true;
  }
  return false;
}

// Safe parse for stored rows: JSON string, object passthrough, else null.
export function parseCustomConditions(v) {
  if (v == null) return null;
  if (typeof v === "object") {
    return Array.isArray(v) ? null : v;
  }
  if (typeof v !== "string" || !v.trim()) return null;
  try {
    const o = JSON.parse(v);
    return o && typeof o === "object" && !Array.isArray(o) ? o : null;
  } catch {
    return null;
  }
}

// Inclusive HH:MM window membership; start > end wraps midnight.
export function hourInWindow(hour, start, end) {
  if (typeof hour !== "string" || !CC_HM_RE.test(hour)) return false;
  if (typeof start !== "string" || typeof end !== "string") return true; // no window = whole day
  if (!CC_HM_RE.test(start) || !CC_HM_RE.test(end)) return true;
  return start <= end ? hour >= start && hour <= end : hour >= start || hour <= end;
}

// One hour row {local_date, hour, values:{...}} vs the parameter blob.
// A set constraint whose value is MISSING fails the hour honestly (no
// fabricated match from absent data); an unset/lenient constraint never
// rejects (cloud >=100% and visibility <=0 km are treated as unconstrained).
export function customHourMatches(values, cc) {
  if (!cc) return false;
  const v = values && typeof values === "object" ? values : {};
  const num = (x) => (typeof x === "number" && Number.isFinite(x) ? x : null);
  const rows = [
    ["cloud_low_max", "cloud_low", "lte"],
    ["cloud_mid_max", "cloud_mid", "lte"],
    ["cloud_high_max", "cloud_high", "lte"],
    ["cloud_low_min", "cloud_low", "gte"],
    ["cloud_mid_min", "cloud_mid", "gte"],
    ["cloud_high_min", "cloud_high", "gte"],
    ["precip_max_mmh", "precipitation", "lte"],
    ["visibility_min_km", "visibility", "gte"],
    ["wind_max_ms", "wind", "lte"],
  ];
  for (const [k, metric, op] of rows) {
    const limit = num(cc[k]);
    if (limit == null) continue;
    if (op === "lte" && metric.startsWith("cloud") && limit >= 100) continue; // lenient default
    if (op === "gte" && metric.startsWith("cloud") && limit <= 0) continue; // patch-5 ⑤ lenient default
    if (op === "gte" && metric === "visibility" && limit <= 0) continue; // lenient default
    const val = num(v[metric]);
    if (val == null) return false; // constraint set but data missing -> no match
    if (op === "lte" ? val > limit : val < limit) return false;
  }
  return true;
}

// Earliest qualifying hour in [now + leadMinutes, now + MATCH_WINDOW_H].
// placeCtx ({lat,lng,utcOffsetHours}) lets ANCHOR window segments expand with
// real sun times; anchor rows are honest no-matches when it is missing.
export function findNextCustomWindow(hourly, cc, nowMs, leadMinutes, placeCtx = null) {
  if (!cc || !Array.isArray(hourly)) return null;
  const earliest = nowMs + (leadMinutes || 0) * 60_000;
  const latest = nowMs + MATCH_WINDOW_H * 3_600_000;
  // patch-5 ④: month window — rows outside the selected months are skipped
  // (empty months = all year); both the cron and evaluateCustomPlace use this
  // one hook, so 通知 and tier always honour the same month window.
  const months = Array.isArray(cc.months) && cc.months.length ? new Set(cc.months) : null;
  let best = null;
  for (const row of hourly) {
    if (!row || typeof row.local_date !== "string" || typeof row.hour !== "string") continue;
    if (months && !months.has(Number(row.local_date.slice(5, 7)))) continue;
    if (!hourPassesWindows(row, cc, placeCtx)) continue;
    if (!customHourMatches(row.values, cc)) continue;
    const t = slotTimeMs(row.local_date, row.hour);
    if (t >= earliest && t <= latest && (!best || t < best.t)) {
      best = { t, local_date: row.local_date, hour: row.hour, opportunity_id: null };
    }
  }
  return best;
}

// Judgment context from an eval KV record: lat/lng (+ tz offset) drive the
// anchor-window expansion. Custom-place records carry lat/lng/timezone; the
// official distilled records gain lat/lng/utc_offset_hours (kv_distill).
export function placeCtxFromRec(rec) {
  if (!rec || typeof rec !== "object") return null;
  const lat = Number(rec.lat), lng = Number(rec.lng);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  let utcOffsetHours = 8;
  if (Number.isFinite(rec.utc_offset_hours)) utcOffsetHours = Number(rec.utc_offset_hours);
  else if (typeof rec.timezone === "string" && rec.timezone) {
    try {
      const parts = new Intl.DateTimeFormat("en-US", { timeZone: rec.timezone, timeZoneName: "shortOffset" })
        .formatToParts(new Date());
      const name = (parts.find((p) => p.type === "timeZoneName") || {}).value || "";
      const m = /GMT([+-])(\d{1,2})(?::(\d{2}))?/.exec(name);
      if (m) utcOffsetHours = (m[1] === "-" ? -1 : 1) * (Number(m[2]) + Number(m[3] || 0) / 60);
    } catch { /* unknown tz keeps the +8 baseline */ }
  }
  return { lat, lng, utcOffsetHours };
}

export function slotTimeMs(localDate, hour) {
  // KV distilled hours are "HH:MM" strings (spot-local, GMT+8 convention);
  // ints (legacy) are accepted as whole hours.
  const hm = typeof hour === "string" && hour.includes(":") ? hour.split(":") : [String(hour).padStart(2, "0"), "00"];
  return Date.parse(`${localDate}T${hm[0].padStart(2, "0")}:${hm[1]}:00+08:00`);
}

export function windowKey(win) {
  return `${win.local_date}T${win.hour}`; // win.hour is "HH:MM"
}

// Earliest qualifying slot in [now + minAdvanceHours, now + 24h].
// opportunityId null/empty = any subject at the place.
export function findNextWindow(subjects, opportunityId, nowMs, minAdvanceHours) {
  const earliest = nowMs + (minAdvanceHours || 0) * 3_600_000;
  const latest = nowMs + MATCH_WINDOW_H * 3_600_000;
  let best = null;
  for (const s of subjects || []) {
    if (opportunityId && s.opportunity_id !== opportunityId) continue;
    for (const d of s.days || []) {
      if (d.verdict !== "GUIDANCE_SATISFIED") continue;
      for (const h of d.hours || []) {
        const t = slotTimeMs(d.local_date, h);
        if (t >= earliest && t <= latest && (!best || t < best.t)) {
          best = { t, local_date: d.local_date, hour: h, opportunity_id: s.opportunity_id };
        }
      }
    }
  }
  return best;
}

export function subjectDisplayName(subject) {
  const n = (subject && subject.name_i18n) || {};
  return n["zh-TW"] || n["zh-TW "] || n.en || subject?.opportunity_id || "題材";
}

export function placeDisplayName(rec) {
  const n = (rec && rec.name_i18n) || {};
  return n["zh-TW"] || n.en || rec?.place_id || "";
}

export function buildMessage(rec, win) {
  let subj = null;
  for (const s of rec?.subjects || []) if (s.opportunity_id === win.opportunity_id) subj = s;
  const place = placeDisplayName(rec);
  const name = subj ? subjectDisplayName(subj) : win.opportunity_id || "";
  const when = `${win.local_date} ${win.hour}（GMT+8）起天氣符合拍攝條件，預計 24 小時內。`;
  return `📸 ChaseLights 攝影通知\n${place}｜${name}\n${when}`;
}

// CL-UI-99: custom-mode message — no thresholds/operators ever echoed; the
// summary the user sees on the card already carries their own parameters.
export function buildCustomMessage(rec, win) {
  const place = placeDisplayName(rec);
  const when = `${win.local_date} ${win.hour}（GMT+8）起天氣符合您的自訂條件，預計 24 小時內。`;
  return `📸 ChaseLights 攝影通知\n${place}｜自訂條件\n${when}`;
}

// ---------------------------------------------------------------------------
// CL-UX-01 Part B: member schedules. A rule MAY carry a schedule (send_time in
// the member's tz, cadence, forecast lead window, target weekdays, tier gate).
// Any NULL rule column inherits notify_defaults; when a schedule field is NULL
// on BOTH, the rule keeps the pre-CL-UX-01 behaviour byte for byte (legacy).
// Due rule (cron every 30 min, send_time may be non-round):
//   local clock in tz -> [weekdays] today's weekday must be listed
//                     -> [every_n_days] dayDiff(last send local date, today) >= n
//                     -> now >= send_time  (later ticks of the SAME local day
//                        still fire, so a missed tick is caught up)
//   bucket key = local date of the cadence day, written as notify_log
//   .window_start so a second 30-min tick cannot double-send.
// ---------------------------------------------------------------------------
const HM_RE = /^([01]\d|2[0-3]):[0-5]\d$/;
const WEEKDAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const DEFAULT_TZ = "Asia/Taipei";

// Columns that participate in the schedule/inheritance resolution.
export const SCHEDULE_FIELDS = [
  "schedule_mode", "schedule_every_n", "schedule_weekdays", "send_time",
  "lead_days", "target_weekdays", "min_tier", "tz",
];

// Plausible IANA identifier: shape check + the runtime must accept it.
export function isPlausibleTz(tz) {
  if (typeof tz !== "string") return false;
  const s = tz.trim();
  if (!s || s.length > 64) return false;
  if (!/^[A-Za-z][A-Za-z0-9_+\-]*(\/[A-Za-z0-9_+\-]+){0,2}$/.test(s)) return false;
  try { new Intl.DateTimeFormat("en-US", { timeZone: s }); return true; } catch { return false; }
}

// '4,5' -> [4,5] sorted/unique; malformed or empty -> null.
export function parseWeekdayCsv(v) {
  if (typeof v !== "string") return null;
  const out = [];
  for (const part of v.split(",")) {
    const s = part.trim();
    if (!s) continue;
    const n = Number(s);
    if (!Number.isInteger(n) || n < 0 || n > 6) return null;
    if (!out.includes(n)) out.push(n);
  }
  return out.length ? out.sort((a, b) => a - b) : null;
}

export function normalizeWeekdayCsv(v) {
  if (v == null || v === "") return { ok: true, csv: null };
  if (typeof v !== "string") return { ok: false, error: "weekdays must be a CSV string of 0..6 (0=Sunday)" };
  const list = parseWeekdayCsv(v);
  if (!list) return { ok: false, error: "weekdays must be a CSV of 0..6 (0=Sunday), e.g. '4,5'" };
  return { ok: true, csv: list.join(",") };
}

// Contract validation shared by POST /notify/rules and PUT /notify/defaults.
// Returns {ok, fields} where fields only carries the keys the caller supplied
// (absent key = NULL on the row = inherit). camelCase and snake_case accepted.
export function validateScheduleFields(input) {
  const src = input && typeof input === "object" && !Array.isArray(input) ? input : {};
  const pick = (camel, snake) => (src[camel] !== undefined ? src[camel] : src[snake]);
  const out = {};

  const mode = pick("scheduleMode", "schedule_mode");
  if (mode !== undefined && mode !== null && mode !== "") {
    if (mode !== "every_n_days" && mode !== "weekdays") {
      return { ok: false, error: "scheduleMode must be 'every_n_days', 'weekdays' or null" };
    }
    out.schedule_mode = mode;
  }

  const everyN = pick("scheduleEveryN", "schedule_every_n");
  if (everyN !== undefined && everyN !== null && everyN !== "") {
    const n = Number(everyN);
    if (!Number.isInteger(n) || n < 1 || n > 7) return { ok: false, error: "scheduleEveryN must be an integer 1..7" };
    out.schedule_every_n = n;
  }

  const weekdays = pick("scheduleWeekdays", "schedule_weekdays");
  if (weekdays !== undefined) {
    const r = normalizeWeekdayCsv(weekdays);
    if (!r.ok) return { ok: false, error: `scheduleWeekdays: ${r.error}` };
    out.schedule_weekdays = r.csv;
  }

  const sendTime = pick("sendTime", "send_time");
  if (sendTime !== undefined && sendTime !== null && sendTime !== "") {
    if (typeof sendTime !== "string" || !HM_RE.test(sendTime)) return { ok: false, error: "sendTime must be an 'HH:MM' string" };
    out.send_time = sendTime;
  }

  const leadDays = pick("leadDays", "lead_days");
  if (leadDays !== undefined && leadDays !== null && leadDays !== "") {
    const n = Number(leadDays);
    if (!Number.isInteger(n) || n < 1 || n > 7) return { ok: false, error: "leadDays must be an integer 1..7" };
    out.lead_days = n;
  }

  const target = pick("targetWeekdays", "target_weekdays");
  if (target !== undefined) {
    const r = normalizeWeekdayCsv(target);
    if (!r.ok) return { ok: false, error: `targetWeekdays: ${r.error}` };
    out.target_weekdays = r.csv;
  }

  const minTier = pick("minTier", "min_tier");
  if (minTier !== undefined && minTier !== null && minTier !== "") {
    if (minTier !== "recommend" && minTier !== "shootable") {
      return { ok: false, error: "minTier must be 'recommend', 'shootable' or null" };
    }
    out.min_tier = minTier;
  }

  const tz = pick("tz", "timezone");
  if (tz !== undefined && tz !== null && tz !== "") {
    if (!isPlausibleTz(tz)) return { ok: false, error: "tz must be a plausible IANA timezone, e.g. Asia/Taipei" };
    out.tz = String(tz).trim();
  }

  return { ok: true, fields: out };
}

// Rule column wins; NULL falls back to the member's defaults row.
export function effectiveRule(rule, defaults) {
  const r = rule || {};
  const d = defaults || null;
  const out = { ...r };
  for (const f of SCHEDULE_FIELDS) {
    out[f] = r[f] != null ? r[f] : (d && d[f] != null ? d[f] : null);
  }
  out.channel = r.channel || (d && d.channel) || "push";
  return out;
}

// Legacy = no cadence clock at all (both the rule and the defaults are NULL for
// schedule_mode + send_time): the pre-CL-UX-01 engine path applies unchanged.
// A lead_days/min_tier/tz value WITHOUT a schedule_mode cannot gate anything,
// so it must not silently disable a working rule.
export function isLegacySchedule(eff) {
  return !eff || (eff.schedule_mode == null && eff.send_time == null);
}

// Local wall clock for an instant in a tz: {date:'YYYY-MM-DD', minutes, weekday, hhmm}.
export function tzClock(nowMs, tz) {
  let fmt;
  try {
    fmt = new Intl.DateTimeFormat("en-CA", {
      timeZone: tz || DEFAULT_TZ,
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hour12: false, weekday: "short",
    });
  } catch { return null; }
  const parts = {};
  for (const p of fmt.formatToParts(new Date(nowMs))) parts[p.type] = p.value;
  if (!parts.year || !parts.month || !parts.day) return null;
  const hh = String(Number(parts.hour) % 24).padStart(2, "0");
  const weekday = WEEKDAY_NAMES.indexOf(parts.weekday);
  if (weekday < 0) return null;
  return {
    date: `${parts.year}-${parts.month}-${parts.day}`,
    minutes: Number(parts.hour) % 24 * 60 + Number(parts.minute),
    weekday,
    hhmm: `${hh}:${parts.minute}`,
  };
}

export function localDateIn(nowMs, tz) {
  const c = tzClock(nowMs, tz);
  return c ? c.date : null;
}

function dateToUTCms(date) {
  const [y, m, d] = String(date).split("-").map(Number);
  return Date.UTC(y, (m || 1) - 1, d || 1);
}

// Whole local days from `fromDate` to `toDate` (both 'YYYY-MM-DD').
export function dayDiff(fromDate, toDate) {
  return Math.round((dateToUTCms(toDate) - dateToUTCms(fromDate)) / 86_400_000);
}

export function addDays(date, n) {
  return new Date(dateToUTCms(date) + n * 86_400_000).toISOString().slice(0, 10);
}

export function weekdayOfDate(date) {
  return new Date(dateToUTCms(date)).getUTCDay();
}

// The schedule gate. Pure: reads only the effective rule + the instant.
// Returns {due, bucket, reason, localDate, weekday}. `bucket` is the ledger key
// (local date of the cadence day) and is ALSO the notify_log.window_start.
export function scheduleGate(eff, nowMs) {
  const e = eff || {};
  const tz = e.tz || DEFAULT_TZ;
  const mode = e.schedule_mode;
  if (!mode) return { due: false, reason: "no_schedule_mode", bucket: null };
  // Non-round send times are fine (20:15); absent send_time falls back to the
  // conventional morning reminder instead of leaving the rule dead.
  const sendTime = e.send_time && HM_RE.test(String(e.send_time)) ? String(e.send_time) : "08:00";
  const clock = tzClock(nowMs, tz);
  if (!clock) return { due: false, reason: "bad_tz", bucket: null };
  const [sh, sm] = sendTime.split(":").map(Number);

  if (mode === "weekdays") {
    const days = parseWeekdayCsv(e.schedule_weekdays);
    if (!days || !days.length) return { due: false, reason: "no_schedule_weekdays", bucket: null };
    if (!days.includes(clock.weekday)) return { due: false, reason: "not_a_listed_weekday", bucket: null };
  } else if (mode === "every_n_days") {
    const nRaw = Number(e.schedule_every_n);
    const n = Number.isInteger(nRaw) ? Math.min(7, Math.max(1, nRaw)) : 1;
    if (e.last_sent_at) {
      const raw = String(e.last_sent_at);
      const iso = raw.includes("T") ? raw : `${raw.replace(" ", "T")}Z`;
      const t = Date.parse(iso);
      const lastLocal = Number.isFinite(t) ? localDateIn(t, tz) : null;
      if (lastLocal) {
        const diff = dayDiff(lastLocal, clock.date);
        if (diff < n) return { due: false, reason: `cadence_wait(${diff}<${n})`, bucket: null };
      }
    }
  } else {
    return { due: false, reason: "bad_schedule_mode", bucket: null };
  }

  if (clock.minutes < sh * 60 + sm) return { due: false, reason: "before_send_time", bucket: null };
  return { due: true, bucket: clock.date, localDate: clock.date, weekday: clock.weekday, localHHMM: clock.hhmm, reason: "due" };
}

const TIER_RANK = { recommend: 2, rec: 2, shootable: 1, shoot: 1 };

export function normalizeTier(v) {
  if (typeof v !== "string") return null;
  const k = v.trim().toLowerCase();
  if (k === "recommend" || k === "rec") return "recommend";
  if (k === "shootable" || k === "shoot") return "shootable";
  return null;
}

// Distilled KV days carry verdict + hours; a day MAY also carry an explicit
// tier. Without one the GUIDANCE_SATISFIED verdict IS the engine's recommend
// class (so min_tier='recommend' never silently swallows every real window).
function tierRankOfDay(day) {
  const t = normalizeTier(day && (day.tier || day.eval_tier));
  return t ? TIER_RANK[t] : TIER_RANK.recommend;
}

// Earliest window inside the rule's forecast horizon:
//   place-local dates in [place today, place today + lead_days]
//   ∩ target_weekdays (when set) ∩ min_tier ∩ (window start >= now)
// Returns {t, local_date, hour, opportunity_id, subject} or null.
export function findScheduledWindow(rec, eff, cc, nowMs) {
  const e = eff || {};
  if (!rec) return null;
  const ruleTz = e.tz || DEFAULT_TZ;
  const placeTz = isPlausibleTz(rec.timezone) ? rec.timezone : ruleTz;
  const placeToday = localDateIn(nowMs, placeTz) || localDateIn(nowMs, ruleTz);
  if (!placeToday) return null;
  const leadRaw = Number(e.lead_days);
  const lead = Number.isInteger(leadRaw) ? Math.min(7, Math.max(1, leadRaw)) : 1;
  const endDate = addDays(placeToday, lead);
  const minRank = e.min_tier === "recommend" ? 2 : e.min_tier === "shootable" ? 1 : 0;
  const targetDays = parseWeekdayCsv(e.target_weekdays);
  const months = cc && Array.isArray(cc.months) && cc.months.length ? new Set(cc.months.map(Number)) : null;
  let best = null;

  const consider = (local_date, hour, opportunity_id, rank, subject) => {
    if (typeof local_date !== "string" || typeof hour !== "string") return;
    if (local_date < placeToday || local_date > endDate) return;
    if (targetDays && !targetDays.includes(weekdayOfDate(local_date))) return;
    if (rank < minRank) return;
    const t = slotTimeMs(local_date, hour);
    if (!Number.isFinite(t) || t < nowMs) return;
    if (!best || t < best.t) best = { t, local_date, hour, opportunity_id: opportunity_id || null, subject: subject || null };
  };

  if (cc) {
    const hourly = Array.isArray(rec.hourly) ? rec.hourly : [];
    const ctx = placeCtxFromRec(rec);
    for (const row of hourly) {
      if (!row || typeof row.local_date !== "string" || typeof row.hour !== "string") continue;
      if (months && !months.has(Number(row.local_date.slice(5, 7)))) continue;
      if (!hourPassesWindows(row, cc, ctx)) continue;
      if (!customHourMatches(row.values, cc)) continue;
      // custom hours carry no tier of their own: they pass every tier gate.
      consider(row.local_date, row.hour, null, 2, null);
    }
    return best;
  }

  for (const s of rec.subjects || []) {
    if (e.opportunity_id && s.opportunity_id !== e.opportunity_id) continue;
    for (const d of s.days || []) {
      if (d.verdict !== "GUIDANCE_SATISFIED") continue;
      const rank = tierRankOfDay(d);
      for (const h of d.hours || []) consider(d.local_date, h, s.opportunity_id, rank, s);
    }
  }
  return best;
}

// One consolidated message per (user, channel, tick): summary title first, then
// one line per due rule (place + subject/theme + qualifying window).
export function buildScheduleBatchMessage(entries) {
  const n = (entries || []).length;
  const title = `${n} 個追蹤景點達標`;
  const lines = (entries || []).map((e) => `${e.placeName || "景點"}｜${e.subjectName || "題材"}｜${e.local_date} ${e.hour}`);
  return { title, lines, text: `📸 ChaseLights 攝影通知\n${title}\n${lines.join("\n")}` };
}

function nextBatchId(nowMs) {
  try {
    if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") return `b_${globalThis.crypto.randomUUID()}`;
  } catch { /* fall through */ }
  return `b_${nowMs}_${Math.random().toString(36).slice(2, 10)}`;
}

export async function sendTelegram(env, chatId, text) {
  if (!env.TG_BOT_TOKEN) return { ok: false, error: "TG_BOT_TOKEN not set" };
  const res = await fetch(`https://api.telegram.org/bot${env.TG_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }, // CJK-safe JSON body (form-encoding fails)
    body: JSON.stringify({ chat_id: chatId, text }),
  });
  const body = await res.json().catch(() => null);
  return { ok: !!(res.ok && body && body.ok === true), status: res.status, error: (body && body.description) || (res.ok ? null : `HTTP ${res.status}`) };
}

// Poll bot updates and complete pending /start <token> deep-link bindings.
// Uses getUpdates with a KV-stored offset (no webhook registration needed;
// the comment worker never consumes getUpdates, so no contention).
export async function pollTelegramBindings(env) {
  if (!env.TG_BOT_TOKEN) return { checked: false, bound: 0 };
  const offset = parseInt((await env.EVALS.get("v1:tg:offset")) || "0", 10);
  const res = await fetch(`https://api.telegram.org/bot${env.TG_BOT_TOKEN}/getUpdates?offset=${offset}&timeout=0`);
  const body = await res.json().catch(() => null);
  if (!body || body.ok !== true || !Array.isArray(body.result)) {
    return { checked: false, bound: 0, error: (body && body.description) || `HTTP ${res.status}` };
  }
  let bound = 0;
  let maxId = offset - 1;
  for (const u of body.result) {
    if (typeof u.update_id === "number" && u.update_id > maxId) maxId = u.update_id;
    const text = u.message && u.message.text;
    const chat = u.message && u.message.chat && u.message.chat.id;
    const m = typeof text === "string" ? text.match(/^\/start\s+(\S+)/) : null;
    if (!m || !chat) continue;
    const row = await env.DB.prepare(
      "SELECT user_id FROM telegram_bindings WHERE token = ?1 AND status = 'pending'"
    ).bind(m[1]).first();
    if (!row) continue;
    await env.DB.prepare(
      "UPDATE telegram_bindings SET chat_id = ?2, status = 'active', bound_at = datetime('now') WHERE user_id = ?1"
    ).bind(row.user_id, String(chat)).run();
    bound += 1;
  }
  if (maxId >= offset) await env.EVALS.put("v1:tg:offset", String(maxId + 1));
  return { checked: true, bound };
}

// Cron body: bindings -> enabled rules -> match next-24h windows -> dedupe (notify_log PK)
// -> deliver via the rule's channel. Returns a plain summary for logs/tests.
export async function runNotifyCron(env, nowMs = Date.now()) {
  const summary = {
    checkedAt: new Date(nowMs).toISOString(), bindings: null, rules_scanned: 0, matches: 0,
    sent: 0, skipped_dupe: 0, custom_skipped: 0, undelivered: 0, errors: [],
    // CL-UX-01 Part B counters (additive — nothing above is renamed)
    silent_skipped: 0, schedule_not_due: 0, rules_matched: 0, messages_sent: 0,
  };
  try {
    summary.bindings = await pollTelegramBindings(env);
  } catch (e) {
    summary.errors.push(`bindings: ${e && e.message}`);
  }

  let rules = [];
  try {
    ({ results: rules } = await env.DB.prepare(
      "SELECT r.id, r.user_id, r.place_id, r.opportunity_id, r.channel, r.min_advance_hours, r.custom_conditions, " +
      "r.schedule_mode, r.schedule_every_n, r.schedule_weekdays, r.send_time, r.lead_days, r.target_weekdays, " +
      "r.min_tier, r.tz, r.last_sent_at FROM notify_rules r WHERE r.enabled = 1"
    ).all());
  } catch (e) {
    summary.errors.push(`rules: ${e && e.message}`);
    return summary;
  }

  // Member schedule defaults (rule column NULL = inherit). A missing table /
  // read error simply means "no defaults" — never a reason to stop the cron.
  const defaultsByUser = new Map();
  try {
    const { results: defs } = await env.DB.prepare(
      "SELECT user_id, schedule_mode, schedule_every_n, schedule_weekdays, send_time, lead_days, target_weekdays, min_tier, channel, tz FROM notify_defaults"
    ).all();
    for (const d of defs || []) if (d && d.user_id) defaultsByUser.set(d.user_id, d);
  } catch (e) {
    summary.errors.push(`defaults: ${e && e.message}`);
  }

  // Due scheduled rules collected for the consolidated per-(user, channel) send.
  const scheduleGroups = new Map();

  for (const rule of rules || []) {
    summary.rules_scanned += 1;
    let rec;
    try {
      rec = await env.EVALS.get(`v1:evals:${rule.place_id}`, "json");
    } catch { rec = null; }
    // CL-APP-09 patch-4: private-place reminders — a rule saved from a
    // private-point subject-row bell judges the SAME stored eval grid the
    // popup renders (v1:evals:custom:<id>); without this fallback the bell
    // would create a rule the cron can never fire (a dead control).
    if (!rec) {
      try { rec = await env.EVALS.get(`v1:evals:custom:${rule.place_id}`, "json"); } catch { rec = null; }
    }
    if (!rec) continue;

    // CL-UI-99: a rule carrying a custom_conditions payload runs in CUSTOM
    // mode (place-level hourly judgment); otherwise legacy subject mode.
    // The two modes are mutually exclusive — custom wins if both ever appear.
    const cc = parseCustomConditions(rule.custom_conditions);
    const eff = effectiveRule(rule, defaultsByUser.get(rule.user_id) || null);

    // ---------------------------------------------------------------- CL-UX-01
    // Scheduled rule: bucket gate -> forecast horizon/tier/target filter ->
    // ledger row per rule (shared batch_id) -> ONE message per user+channel.
    if (!isLegacySchedule(eff)) {
      const gate = scheduleGate(eff, nowMs);
      if (!gate.due) { summary.schedule_not_due += 1; continue; }
      if (cc && (!Array.isArray(rec.hourly) || !rec.hourly.length)) {
        summary.custom_skipped += 1; // hourly data not synced yet — honest skip
        continue;
      }
      const win = findScheduledWindow(rec, eff, cc, nowMs);
      if (!win) { summary.silent_skipped += 1; continue; } // SILENT: no log, no send
      summary.rules_matched += 1;
      summary.matches += 1;

      const channel = eff.channel || "push";
      const gkey = `${rule.user_id}|${channel}`;
      let group = scheduleGroups.get(gkey);
      if (!group) {
        group = { userId: rule.user_id, channel, batchId: nextBatchId(nowMs), entries: [] };
        scheduleGroups.set(gkey, group);
      }

      // Atomic dedupe per (rule, local-date bucket): a second 30-min tick on the
      // same cadence day cannot double-send, while a missed tick still fires.
      let fresh = true;
      try {
        const ins = await env.DB.prepare(
          "INSERT INTO notify_log (rule_id, window_start, user_id, place_id, opportunity_id, channel, batch_id) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7) ON CONFLICT(rule_id, window_start) DO NOTHING"
        ).bind(rule.id, gate.bucket, rule.user_id, rule.place_id, win.opportunity_id || rule.opportunity_id || null, channel, group.batchId).run();
        fresh = !!(ins.meta && ins.meta.changes > 0);
      } catch (e) {
        summary.errors.push(`log: ${e && e.message}`);
        continue;
      }
      if (!fresh) { summary.skipped_dupe += 1; continue; }

      group.entries.push({
        rule,
        bucket: gate.bucket,
        local_date: win.local_date,
        hour: win.hour,
        placeName: placeDisplayName(rec),
        subjectName: cc ? "自訂條件" : (win.subject ? subjectDisplayName(win.subject) : (win.opportunity_id || "題材")),
      });
      continue;
    }

    let win;
    if (cc) {
      if (!Array.isArray(rec.hourly) || !rec.hourly.length) {
        summary.custom_skipped += 1; // hourly data not synced yet — honest skip
        continue;
      }
      const leadMin = Number.isFinite(cc.lead_minutes) ? cc.lead_minutes : (rule.min_advance_hours || 0) * 60;
      win = findNextCustomWindow(rec.hourly, cc, nowMs, leadMin, placeCtxFromRec(rec));
    } else {
      win = findNextWindow(rec.subjects, rule.opportunity_id, nowMs, rule.min_advance_hours);
    }
    if (!win) continue;
    const key = windowKey(win);
    summary.matches += 1;

    // Atomic dedupe: same rule + same window is delivered once, ever.
    let fresh = true;
    try {
      const ins = await env.DB.prepare(
        "INSERT INTO notify_log (rule_id, window_start, user_id, place_id, opportunity_id, channel) VALUES (?1, ?2, ?3, ?4, ?5, ?6) ON CONFLICT(rule_id, window_start) DO NOTHING"
      ).bind(rule.id, key, rule.user_id, rule.place_id, rule.opportunity_id || null, rule.channel || "push").run();
      fresh = !!(ins.meta && ins.meta.changes > 0);
    } catch (e) {
      summary.errors.push(`log: ${e && e.message}`);
      continue;
    }
    if (!fresh) { summary.skipped_dupe += 1; continue; }

    if (rule.channel === "web_push") {
      // Skeleton: subscription rows accepted, VAPID delivery is a follow-up ticket.
      await env.DB.prepare(
        "UPDATE notify_log SET delivered = 0, detail = ?2 WHERE rule_id = ?1 AND window_start = ?3"
      ).bind(rule.id, "web_push delivery not implemented (VAPID skeleton)", key).run();
      summary.undelivered += 1;
      continue;
    }

    if (rule.channel === "push") {
      // CL-APP-03: APP push via FCM HTTP v1. Fail-closed on missing service
      // account secret — record undelivered, log to console, never throw.
      const msg = cc ? buildCustomMessage(rec, win) : buildMessage(rec, win);
      const title = msg.split("\n")[0];
      const bodyText = msg.split("\n").slice(1).join("\n");
      const sa = env.FCM_SERVICE_ACCOUNT_JSON;
      if (!sa) {
        console.warn("[notify-cron] push skipped: FCM_SERVICE_ACCOUNT_JSON not set (fail-closed) — rule", rule.id);
        await env.DB.prepare(
          "UPDATE notify_log SET delivered = 0, detail = ?2 WHERE rule_id = ?1 AND window_start = ?3"
        ).bind(rule.id, "push skipped: FCM service account not configured (fail-closed)", key).run();
        summary.undelivered += 1;
        continue;
      }
      let tokens = [];
      try {
        ({ results: tokens } = await env.DB.prepare(
          "SELECT token FROM push_tokens WHERE user_device_id = ?1"
        ).bind(rule.user_id).all());
      } catch (e) {
        summary.errors.push(`push tokens: ${e && e.message}`);
      }
      tokens = tokens || [];
      if (!tokens.length) {
        await env.DB.prepare(
          "UPDATE notify_log SET delivered = 0, detail = ?2 WHERE rule_id = ?1 AND window_start = ?3"
        ).bind(rule.id, "push skipped: no registered device token for user", key).run();
        summary.undelivered += 1;
        continue;
      }
      let anyOk = false;
      let lastError = null;
      for (const t of tokens) {
        try {
          const r = await sendPush(env, t.token, { title, body: bodyText });
          if (r.ok) anyOk = true; else lastError = r.error || "unknown";
        } catch (e) {
          lastError = e && e.message;
        }
      }
      await env.DB.prepare(
        "UPDATE notify_log SET delivered = ?2, detail = ?3 WHERE rule_id = ?1 AND window_start = ?4"
      ).bind(rule.id, anyOk ? 1 : 0, JSON.stringify({ status: anyOk ? "pushed" : "failed", error: lastError }), key).run();
      if (anyOk) { summary.sent += 1; summary.messages_sent += 1; }
      else summary.undelivered += 1;
      continue;
    }

    let binding = null;
    try {
      binding = await env.DB.prepare("SELECT chat_id, status FROM telegram_bindings WHERE user_id = ?1").bind(rule.user_id).first();
    } catch (e) {
      summary.errors.push(`binding: ${e && e.message}`);
    }
    if (!binding || binding.status !== "active" || !binding.chat_id) {
      await env.DB.prepare(
        "UPDATE notify_log SET delivered = 0, detail = ?2 WHERE rule_id = ?1 AND window_start = ?3"
      ).bind(rule.id, "telegram binding not active", key).run();
      summary.undelivered += 1;
      continue;
    }

    let result;
    try {
      result = await sendTelegram(env, binding.chat_id, cc ? buildCustomMessage(rec, win) : buildMessage(rec, win));
    } catch (e) {
      result = { ok: false, error: e && e.message };
    }
    await env.DB.prepare(
      "UPDATE notify_log SET delivered = ?2, detail = ?3 WHERE rule_id = ?1 AND window_start = ?4"
    ).bind(rule.id, result.ok ? 1 : 0, JSON.stringify({ status: result.status, error: result.error }), key).run();
    if (result.ok) { summary.sent += 1; summary.messages_sent += 1; }
    else summary.undelivered += 1;
  }

  // -------------------------------------------------------------------------
  // CL-UX-01: one consolidated message per (user, channel) tick. Each rule keeps
  // its own notify_log row (per-rule dedupe survives) and they all share the
  // group's batch_id; exactly one push / telegram call per group.
  // -------------------------------------------------------------------------
  for (const group of scheduleGroups.values()) {
    if (!group.entries.length) continue;
    const { title, lines, text } = buildScheduleBatchMessage(group.entries);
    const batch = { batch_id: group.batchId };

    const mark = async (delivered, detail) => {
      for (const e of group.entries) {
        try {
          await env.DB.prepare(
            "UPDATE notify_log SET delivered = ?2, detail = ?3 WHERE rule_id = ?1 AND window_start = ?4"
          ).bind(e.rule.id, delivered, detail, e.bucket).run();
        } catch (err) { summary.errors.push(`log update: ${err && err.message}`); }
      }
    };
    const stampLastSent = async () => {
      const iso = new Date(nowMs).toISOString();
      for (const e of group.entries) {
        try {
          await env.DB.prepare("UPDATE notify_rules SET last_sent_at = ?2 WHERE id = ?1").bind(e.rule.id, iso).run();
        } catch (err) { summary.errors.push(`last_sent_at: ${err && err.message}`); }
      }
    };

    if (group.channel === "web_push") {
      // Skeleton: subscription rows accepted, VAPID delivery is a follow-up ticket.
      await mark(0, "web_push delivery not implemented (VAPID skeleton)");
      summary.undelivered += group.entries.length;
      continue;
    }

    if (group.channel === "push") {
      const sa = env.FCM_SERVICE_ACCOUNT_JSON;
      if (!sa) {
        console.warn("[notify-cron] push skipped: FCM_SERVICE_ACCOUNT_JSON not set (fail-closed) — user", group.userId);
        await mark(0, "push skipped: FCM service account not configured (fail-closed)");
        summary.undelivered += group.entries.length;
        continue;
      }
      let tokens = [];
      try {
        ({ results: tokens } = await env.DB.prepare(
          "SELECT token FROM push_tokens WHERE user_device_id = ?1"
        ).bind(group.userId).all());
      } catch (e) {
        summary.errors.push(`push tokens: ${e && e.message}`);
      }
      tokens = tokens || [];
      if (!tokens.length) {
        await mark(0, "push skipped: no registered device token for user");
        summary.undelivered += group.entries.length;
        continue;
      }
      let anyOk = false;
      let lastError = null;
      for (const t of tokens) {
        try {
          const r = await sendPush(env, t.token, { title, body: lines.join("\n") });
          if (r.ok) anyOk = true; else lastError = r.error || "unknown";
        } catch (e) {
          lastError = e && e.message;
        }
      }
      await mark(anyOk ? 1 : 0, JSON.stringify({ status: anyOk ? "pushed" : "failed", error: lastError, ...batch }));
      if (anyOk) {
        summary.sent += group.entries.length;
        summary.messages_sent += 1;
        await stampLastSent();
      } else {
        summary.undelivered += group.entries.length;
      }
      continue;
    }

    let binding = null;
    try {
      binding = await env.DB.prepare("SELECT chat_id, status FROM telegram_bindings WHERE user_id = ?1").bind(group.userId).first();
    } catch (e) {
      summary.errors.push(`binding: ${e && e.message}`);
    }
    if (!binding || binding.status !== "active" || !binding.chat_id) {
      await mark(0, "telegram binding not active");
      summary.undelivered += group.entries.length;
      continue;
    }

    let result;
    try {
      result = await sendTelegram(env, binding.chat_id, text);
    } catch (e) {
      result = { ok: false, error: e && e.message };
    }
    await mark(result.ok ? 1 : 0, JSON.stringify({ status: result.status, error: result.error, ...batch }));
    if (result.ok) {
      summary.sent += group.entries.length;
      summary.messages_sent += 1;
      await stampLastSent();
    } else {
      summary.undelivered += group.entries.length;
    }
  }
  return summary;
}
