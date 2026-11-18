// CL-APP-08 (owner-approved conservative version): private-place grid
// deduplication. Two ACTIVE private points of the SAME member share ONE
// Open-Meteo grid fetch when ALL of the following hold (fail-closed — every
// check must pass or the points stay independent):
//   1. distance < 1 km;
//   2. DEM elevation difference < 30 m;
//   3. terrain relief within a 500 m radius ≤ 100 m (flat-enough pocket);
//   4. the straight line between them crosses NO ridge line / gully mouth:
//      no intermediate DEM sample rises ≥ RIDGE_DETECT_M above BOTH endpoints
//      (ridge) nor dips ≥ RIDGE_DETECT_M below BOTH endpoints (gully).
// Groups are per-user ONLY (conservative: no cross-member data sharing).
// The representative (earliest created active member) performs the actual
// forecast fetch ONCE; every other group member reuses the raw grid result
// verbatim (cloud/precip/visibility/wind — the shared hourly block) while
// KEEPING its own DEM lat/lng/elevation/timezone in its eval record:
// judgment-side inputs change ZERO (CL-APP-08 rule 4).
// Costs: a group counts as ONE quota point — one user-fetch budget unit and
// one global-usage unit per representative fetch, never per member.
// Escape hatch: a member can detach a point (share_mode='independent') and
// trigger a solo refetch — that refetch costs 1 quota like any first fetch.
// The migration re-group of already-existing places runs in the background
// and queues NO fetches and bumps NO counters (rule 5).
// DEM terrain sampling rides the Open-Meteo Elevation API (batched coords),
// which is a separate free endpoint from the forecast API.

export const SHARE_MAX_DIST_M = 1000;       // rule 1
export const SHARE_MAX_ELEV_DIFF_M = 30;    // rule 2
export const SHARE_MAX_RELIEF_M = 100;      // rule 3 (500 m ring)
export const SHARE_RELIEF_RADIUS_M = 500;
export const RIDGE_DETECT_M = 30;           // rule 4 (ridge / gully mouth)

const EARTH_R_M = 6371000;
const M_PER_DEG_LAT = 111320;

export function haversineM(lat1, lng1, lat2, lng2) {
  const p1 = (lat1 * Math.PI) / 180, p2 = (lat2 * Math.PI) / 180;
  const dp = p2 - p1, dl = ((lng2 - lng1) * Math.PI) / 180;
  const a = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
  return 2 * EARTH_R_M * Math.asin(Math.min(1, Math.sqrt(a)));
}

// ---------------------------------------------------------------------------
// Pure terrain analysis (no I/O) — the testable core of every acceptance case.
//   ring[]     elevations sampled on a ring of SHARE_RELIEF_RADIUS_M around
//              the midpoint (plus the two endpoints themselves);
//   segment[]  elevations at t = 0.25 / 0.50 / 0.75 along a→b (endpoints
//              excluded — they are the bases the profile is compared to).
// ---------------------------------------------------------------------------
export function analyzeTerrain({ elevA, elevB, ring = [], segment = [] } = {}) {
  if (![elevA, elevB].every((v) => Number.isFinite(Number(v)))) return null;
  const nums = (arr) => arr.map(Number).filter((v) => Number.isFinite(v));
  const r = nums(ring);
  const relief500 = r.length >= 3 ? Math.max(...r) - Math.min(...r) : null;
  const elevDiff = Math.abs(Number(elevA) - Number(elevB));
  const hi = Math.max(Number(elevA), Number(elevB));
  const lo = Math.min(Number(elevA), Number(elevB));
  let crossRidge = false;
  for (const s of nums(segment)) {
    if (s >= hi + RIDGE_DETECT_M || s <= lo - RIDGE_DETECT_M) { crossRidge = true; break; }
  }
  const distOk = null; // distance is checked by the caller (not a DEM fact)
  const canShare = relief500 != null && relief500 <= SHARE_MAX_RELIEF_M &&
    elevDiff < SHARE_MAX_ELEV_DIFF_M && !crossRidge;
  return { relief500, elevDiff, crossRidge, distOk, canShare };
}

// DEM sampling geometry for the pair a→b: the 500 m ring (8 compass points
// around the segment midpoint + both endpoints) and 3 intermediate segment
// samples. All coordinates land in ONE batched Elevation-API call.
export function demSamplePoints(latA, lngA, latB, lngB) {
  const midLat = (latA + latB) / 2, midLng = (lngA + lngB) / 2;
  const dLat = SHARE_RELIEF_RADIUS_M / M_PER_DEG_LAT;
  const dLng = SHARE_RELIEF_RADIUS_M / (M_PER_DEG_LAT * Math.max(0.2, Math.cos((midLat * Math.PI) / 180)));
  const ring = [
    [midLat + dLat, midLng], [midLat + dLat * 0.707, midLng + dLng * 0.707],
    [midLat, midLng + dLng], [midLat - dLat * 0.707, midLng + dLng * 0.707],
    [midLat - dLat, midLng], [midLat - dLat * 0.707, midLng - dLng * 0.707],
    [midLat, midLng - dLng], [midLat + dLat * 0.707, midLng - dLng * 0.707],
    [latA, lngA], [latB, lngB],
  ];
  const segment = [0.25, 0.5, 0.75].map((t) => [latA + (latB - latA) * t, lngA + (lngB - lngA) * t]);
  return { ring, segment };
}

// Open-Meteo Elevation API — up to 100 coords per call. `opts.fetchElev`
// replaces the network in tests (synthetic DEM); the real shape is
// { elevation: [h0, h1, ...] } aligned with the request order.
export async function fetchDemElevations(points, env, opts = {}) {
  if (!points.length) return [];
  if (typeof opts.fetchElev === "function") return opts.fetchElev(points);
  const lat = points.map((p) => p[0].toFixed(5)).join(",");
  const lng = points.map((p) => p[1].toFixed(5)).join(",");
  const api = env.OPEN_METEO_ELEVATION_BASE || "https://api.open-meteo.com/v1/elevation";
  const res = await fetch(`${api}?latitude=${lat}&longitude=${lng}`);
  if (!res.ok) throw new Error(`DEM HTTP ${res.status}`);
  const body = await res.json();
  return Array.isArray(body.elevation) ? body.elevation.map(Number) : [];
}

// Full terrain verdict for one candidate pair (one DEM call).
export async function terrainBetween(a, b, env, opts = {}) {
  const { ring, segment } = demSamplePoints(a.lat, a.lng, b.lat, b.lng);
  const vals = await fetchDemElevations(ring.concat(segment), env, opts);
  if (!vals.length) return null;
  const ringElevs = vals.slice(0, ring.length);
  const segElevs = vals.slice(ring.length);
  const out = analyzeTerrain({
    elevA: a.elevation != null ? a.elevation : ringElevs[ring.length - 2],
    elevB: b.elevation != null ? b.elevation : ringElevs[ring.length - 1],
    ring: ringElevs,
    segment: segElevs,
  });
  if (out) out.distanceM = haversineM(a.lat, a.lng, b.lat, b.lng);
  return out;
}

// Distance gate kept OUTSIDE analyzeTerrain on purpose: the caller may want
// the terrain numbers even when the pair is too far apart.
export function pairCanShare(a, b, terrain) {
  if (!terrain || !terrain.canShare) return false;
  const d = terrain.distanceM != null ? terrain.distanceM : haversineM(a.lat, a.lng, b.lat, b.lng);
  return d < SHARE_MAX_DIST_M;
}

export function newGroupId(placeId) {
  return `g:${placeId}`;
}

// Candidate rows must share the user (privacy) and sit inside a coarse bbox
// around the point (~0.02° ≈ 2.2 km — generous, the precise gate is 1 km).
export function candidateWhere(place) {
  return {
    sql: "SELECT id, name, lat, lng, elevation, status, created_at, share_mode FROM custom_places WHERE user_id = ?1 AND id != ?2 AND status = 'active' AND share_mode = 'auto' AND lat BETWEEN ?3 AND ?4 AND lng BETWEEN ?5 AND ?6 ORDER BY created_at ASC",
    binds: [
      place.user_id, place.id,
      place.lat - 0.02, place.lat + 0.02,
      place.lng - 0.02, place.lng + 0.02,
    ],
  };
}

// ---------------------------------------------------------------------------
// Group records (KV v1:cp:group:<gid>): the single source of truth for
// membership + representative. DB rows carry group_id/share_mode for fast
// queries; the KV record carries names for the member-facing shared tag.
// ---------------------------------------------------------------------------
export async function getGroupRecord(env, gid) {
  try { return await env.EVALS.get(`v1:cp:group:${gid}`, "json"); } catch { return null; }
}

export async function putGroupRecord(env, gid, rec) {
  try { await env.EVALS.put(`v1:cp:group:${gid}`, JSON.stringify(rec)); } catch { /* best-effort */ }
}

export async function deleteGroupRecord(env, gid) {
  try { await env.EVALS.delete(`v1:cp:group:${gid}`); } catch { /* best-effort */ }
}

// Join `place` into `rep`'s group (creating it if `rep` is ungrouped). The
// representative never changes on join — earliest-created place stays the
// fetcher so its existing data keeps serving the group.
export async function joinGroup(env, place, rep, opts = {}) {
  let gid = rep.group_id || null;
  if (!gid) {
    gid = newGroupId(rep.id);
    await env.DB.prepare(
      "UPDATE custom_places SET group_id = ?2, updated_at = datetime('now') WHERE id = ?1"
    ).bind(rep.id, gid).run();
  }
  await env.DB.prepare(
    "UPDATE custom_places SET group_id = ?2, share_mode = 'auto', updated_at = datetime('now') WHERE id = ?1"
  ).bind(place.id, gid).run();
  const rec = (await getGroupRecord(env, gid)) || {
    group_id: gid, representativeId: rep.id, formed_at: new Date().toISOString(), members: [],
  };
  rec.representativeId = rep.id;
  const names = new Map((rec.members || []).map((m) => [m.id, m.name]));
  names.set(rep.id, rep.name); names.set(place.id, place.name);
  rec.members = [...names].map(([id, name]) => ({ id, name }));
  await putGroupRecord(env, gid, rec);
  if (opts.nowMs) rec._nowMs = opts.nowMs;
  return { groupId: gid, record: rec };
}

// Detach a point: remove from the KV record; if it WAS the representative,
// promote the earliest remaining active auto member (the group keeps serving
// from the oldest member's data). An emptied group record is deleted.
export async function leaveGroup(env, placeRow) {
  const gid = placeRow.group_id;
  if (!gid) return { left: false };
  const rec = await getGroupRecord(env, gid);
  if (rec) {
    rec.members = (rec.members || []).filter((m) => m.id !== placeRow.id);
    if (rec.representativeId === placeRow.id) {
      const next = await env.DB.prepare(
        "SELECT id, name FROM custom_places WHERE group_id = ?1 AND id != ?2 AND status = 'active' AND share_mode = 'auto' ORDER BY created_at ASC LIMIT 1"
      ).bind(gid, placeRow.id).first();
      if (next) {
        rec.representativeId = next.id;
        if (!rec.members.some((m) => m.id === next.id)) rec.members.push({ id: next.id, name: next.name });
        await putGroupRecord(env, gid, rec);
      } else {
        await deleteGroupRecord(env, gid);
      }
    } else {
      await putGroupRecord(env, gid, rec);
    }
  }
  await env.DB.prepare(
    "UPDATE custom_places SET group_id = NULL, share_mode = 'independent', updated_at = datetime('now') WHERE id = ?1"
  ).bind(placeRow.id).run();
  return { left: true, groupId: gid, record: rec };
}

// Representative of the group a row belongs to. KV record first; if the KV
// record is missing (best-effort storage), fall back to the earliest active
// auto member — a group NEVER loses its fetcher because of a KV hiccup.
export async function representativeOf(env, row) {
  if (!row.group_id || row.share_mode !== "auto") return row;
  const rec = await getGroupRecord(env, row.group_id);
  if (rec && rec.representativeId) {
    if (rec.representativeId === row.id) return row;
    const rep = await env.DB.prepare(
      "SELECT id, user_id, name, lat, lng, elevation, status, custom_conditions FROM custom_places WHERE id = ?1"
    ).bind(rec.representativeId).first();
    if (rep && rep.status === "active") return rep;
  }
  const fb = await env.DB.prepare(
    "SELECT id, user_id, name, lat, lng, elevation, status, custom_conditions FROM custom_places WHERE group_id = ?1 AND status = 'active' AND share_mode = 'auto' ORDER BY created_at ASC LIMIT 1"
  ).bind(row.group_id).first();
  return fb || row;
}

// After the representative's fetch succeeds, every active group member gets
// its OWN eval record — same raw hourly grid verbatim, but the member's own
// lat/lng/elevation/timezone (CL-APP-08 rule 4: judgment inputs untouched).
export async function fanOutGroupEval(env, repRow, evalBody, nowMs = Date.now()) {
  if (!repRow.group_id) return 0;
  let n = 0;
  let members = [];
  try {
    const { results } = await env.DB.prepare(
      "SELECT id, name, lat, lng, elevation, timezone, status FROM custom_places WHERE group_id = ?1 AND id != ?2 AND status = 'active' AND share_mode = 'auto'"
    ).bind(repRow.group_id, repRow.id).all();
    members = results || [];
  } catch { return 0; }
  for (const m of members) {
    try {
      await env.EVALS.put(`v1:evals:custom:${m.id}`, JSON.stringify({
        ...evalBody,
        place_id: m.id, private: true, name: m.name,
        lat: m.lat, lng: m.lng, elevation: m.elevation, timezone: m.timezone,
        shared_from: repRow.id, shared_group: repRow.group_id,
        generated_at: new Date(nowMs).toISOString(),
      }));
      n += 1;
    } catch { /* per-member fan-out is best-effort */ }
  }
  return n;
}

// ---------------------------------------------------------------------------
// One-shot candidate search for a (new or ungrouped) place: nearest candidate
// of the SAME user that passes every gate. `opts` carries the DEM seam.
// Returns { groupId, representativeId } | null. Never throws to the caller —
// grouping is an optimization, an error simply means "stay independent".
// ---------------------------------------------------------------------------
export async function findGroupFor(env, place, opts = {}) {
  try {
    const where = candidateWhere(place);
    const { results } = await env.DB.prepare(where.sql).bind(...where.binds).all();
    for (const cand of results || []) {
      const d = haversineM(place.lat, place.lng, cand.lat, cand.lng);
      if (d >= SHARE_MAX_DIST_M) continue; // ordered by distance below anyway
      if (place.elevation != null && cand.elevation != null &&
          Math.abs(place.elevation - cand.elevation) >= SHARE_MAX_ELEV_DIFF_M) continue;
      const terrain = await terrainBetween(place, cand, env, opts);
      if (pairCanShare(place, cand, terrain)) return { groupId: null, representativeId: cand.id, terrain };
    }
    return null;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Background migration (rule 5): re-group EXISTING active places once.
// KV guard v1:cp:regroup:done. Queues NO fetch, bumps NO counter — the
// representative's normal refresh cadence keeps serving the whole group.
// Batched: at most opts.maxPairs candidate pairs per invocation (DEM calls),
// the guard only lands when the sweep finishes; partial sweeps resume.
// ---------------------------------------------------------------------------
export const REGROUP_GUARD_KEY = "v1:cp:regroup:done";

export async function regroupExistingPlaces(env, opts = {}) {
  const summary = { scanned: 0, grouped: 0, pairs: 0, remaining: false, skipped: false };
  if (!opts.force) {
    let done = null;
    try { done = await env.EVALS.get(REGROUP_GUARD_KEY, "json"); } catch { done = null; }
    if (done && done.regrouped) { summary.skipped = true; return summary; }
  }
  const maxPairs = typeof opts.maxPairs === "number" ? opts.maxPairs : 120;
  // Ungrouped active auto-mode places.
  let rows = [];
  try {
    ({ results: rows } = await env.DB.prepare(
      "SELECT id, user_id, name, lat, lng, elevation, status, created_at FROM custom_places WHERE status = 'active' AND share_mode = 'auto' AND group_id IS NULL ORDER BY user_id, created_at ASC LIMIT ?1"
    ).bind(opts.maxRows || 300).all());
  } catch (e) {
    summary.error = e && e.message;
    return summary;
  }
  summary.scanned = rows.length;
  // Candidate pairs: same user, coarse bbox — ordered oldest first so the
  // earliest place becomes the representative.
  const pairs = [];
  for (let i = 0; i < rows.length; i++) {
    for (let j = i + 1; j < rows.length; j++) {
      const a = rows[i], b = rows[j];
      if (a.user_id !== b.user_id) continue;
      if (Math.abs(a.lat - b.lat) > 0.02 || Math.abs(a.lng - b.lng) > 0.02) continue;
      pairs.push([a, b]);
    }
  }
  for (const [a, b] of pairs) {
    if (summary.pairs >= maxPairs) { summary.remaining = true; break; }
    // both rows may have joined a group already via an earlier pair
    const ra = await env.DB.prepare("SELECT id, group_id, share_mode, status, name FROM custom_places WHERE id = ?1").bind(a.id).first();
    const rb = await env.DB.prepare("SELECT id, group_id, share_mode, status, name FROM custom_places WHERE id = ?1").bind(b.id).first();
    if (!ra || !rb || ra.status !== "active" || rb.status !== "active") continue;
    if (ra.group_id && ra.group_id === rb.group_id) continue;
    if (ra.share_mode !== "auto" || rb.share_mode !== "auto") continue;
    const terrain = await terrainBetween(a, b, env, opts);
    summary.pairs += 1;
    if (!pairCanShare(a, b, terrain)) continue;
    const rep = ra.created_at <= b.created_at ? ra : rb;
    const joiner = rep.id === ra.id ? rb : ra;
    await joinGroup(env, { id: joiner.id, name: joiner.name }, { id: rep.id, name: rep.name, group_id: rep.group_id });
    summary.grouped += 1;
  }
  if (!summary.remaining && !summary.error) {
    try { await env.EVALS.put(REGROUP_GUARD_KEY, JSON.stringify({ regrouped: true, at: new Date().toISOString(), ...summary })); } catch { /* best-effort */ }
  }
  return summary;
}
