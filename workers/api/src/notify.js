// CL-API-03: notification engine — cron matcher, dedupe, Telegram delivery.
// Data source: KV distilled evaluations (v1:evals:<place_id>), RESULTS ONLY —
// no thresholds/operators ever enter this module or the messages it sends.
//
// Time convention: distilled days carry spot-LOCAL wall clock (local_date + hour
// int). This v1 matches them on the site-wide GMT+8 convention; JP (UTC+9)
// spots may drift up to 1h inside the match window — follow-up: per-spot tz.

export const MATCH_WINDOW_H = 24;

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
  const summary = { checkedAt: new Date(nowMs).toISOString(), bindings: null, rules_scanned: 0, matches: 0, sent: 0, skipped_dupe: 0, undelivered: 0, errors: [] };
  try {
    summary.bindings = await pollTelegramBindings(env);
  } catch (e) {
    summary.errors.push(`bindings: ${e && e.message}`);
  }

  let rules = [];
  try {
    ({ results: rules } = await env.DB.prepare(
      "SELECT r.id, r.user_id, r.place_id, r.opportunity_id, r.channel, r.min_advance_hours FROM notify_rules r WHERE r.enabled = 1"
    ).all());
  } catch (e) {
    summary.errors.push(`rules: ${e && e.message}`);
    return summary;
  }

  for (const rule of rules || []) {
    summary.rules_scanned += 1;
    let rec;
    try {
      rec = await env.EVALS.get(`v1:evals:${rule.place_id}`, "json");
    } catch { rec = null; }
    if (!rec) continue;

    const win = findNextWindow(rec.subjects, rule.opportunity_id, nowMs, rule.min_advance_hours);
    if (!win) continue;
    const key = windowKey(win);
    summary.matches += 1;

    // Atomic dedupe: same rule + same window is delivered once, ever.
    let fresh = true;
    try {
      const ins = await env.DB.prepare(
        "INSERT INTO notify_log (rule_id, window_start, user_id, place_id, opportunity_id, channel) VALUES (?1, ?2, ?3, ?4, ?5, ?6) ON CONFLICT(rule_id, window_start) DO NOTHING"
      ).bind(rule.id, key, rule.user_id, rule.place_id, rule.opportunity_id || null, rule.channel || "telegram").run();
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
      result = await sendTelegram(env, binding.chat_id, buildMessage(rec, win));
    } catch (e) {
      result = { ok: false, error: e && e.message };
    }
    await env.DB.prepare(
      "UPDATE notify_log SET delivered = ?2, detail = ?3 WHERE rule_id = ?1 AND window_start = ?4"
    ).bind(rule.id, result.ok ? 1 : 0, JSON.stringify({ status: result.status, error: result.error }), key).run();
    if (result.ok) summary.sent += 1;
    else summary.undelivered += 1;
  }
  return summary;
}
