export const LOCALES = Object.freeze(["zh-TW", "en", "ja"]);
const TYPES = new Set(["point","polygon","polyline","ridge","area","horizon_sector","foreground_area","water_surface","dynamic_sky"]);
export function rows(value) {
  if (Array.isArray(value)) return value.filter(x => x && typeof x === "object");
  if (value && typeof value === "object") return Object.values(value).filter(x => x && typeof x === "object");
  return [];
}
export function idOf(record, keys = ["id"]) {
  for (const key of keys) if (record && (typeof record[key] === "string" || typeof record[key] === "number") && String(record[key]).trim()) return String(record[key]);
  return null;
}
export function normalizeCatalog(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("Invalid V2 document");
  const data = input.data && input.data.places ? input.data : input;
  const fields = ["places","opportunities","camera_zones","subject_geometries","view_relations","condition_contracts","conditions","access_advisories","evidence","research_status","unknowns","evaluations"];
  const result = Object.fromEntries(fields.map(k => [k,rows(data[k])]));
  result.metadata = data.metadata && typeof data.metadata === "object" ? data.metadata : {};
  result.generated_at = data.generated_at || result.metadata.generated_at || null;
  if (!result.places.length) throw new Error("No V2 places");
  return result;
}
export function placeId(place) { return idOf(place,["spot_id","place_id","id"]); }
export function opportunityId(opp) { return idOf(opp,["opportunity_id","id"]); }
export function linkedPlaceId(opp) { return idOf(opp,["place_id","spot_id"]); }
// CL-UI-07: provisional/pending internal-state markers must never reach the UI.
// These are the exact marker strings the pre-fix W2 generator baked into name
// and description display strings; matching them exactly (not fuzzily) means
// honest degradation/advisory copy is never filtered by mistake. Shipped
// bundles are regenerated without them; this filter is defense in depth for
// stale cached data and for any imported JSON that still carries markers.
const PROVISIONAL_MARKERS = [
  " (provisional English title, pending review)",
  "（暫定日本語タイトル、レビュー待ち）",
  " (zh-TW source values retained pending translation).",
  "（zh-TW原文のまま、翻訳待ち）。",
];
function markerTainted(value) {
  return typeof value === "string" && PROVISIONAL_MARKERS.some((m) => value.includes(m));
}
export function displayLocalizedName(i18n, locale) {
  // Safe display for any raw name_i18n object (topic labels etc.): requested
  // locale first, then the zh-TW source value as a neutral readable fallback.
  if (!i18n || typeof i18n !== "object") return null;
  for (const l of [locale, "zh-TW"]) {
    const v = typeof i18n[l] === "string" ? i18n[l].trim() : "";
    if (v && !markerTainted(v)) return v;
  }
  return null;
}
// Name-display paths (place/opportunity/subject names) fall back to the zh-TW
// source name when the requested locale has no reviewed value; other semantic
// fields keep the no-silent-fallback rule (callers show the missing-translation
// notice instead). CL-UI-07, owner-approved.
const NAME_KEYS = new Set(["name", "canonical_name", "title"]);
export function localized(record, key, locale, properName = false) {
  if (!record || !LOCALES.includes(locale)) return null;
  const usable = (v) => {
    const s = typeof v === "string" ? v.trim() : "";
    return s && !markerTainted(s) ? s : null;
  };
  for (const value of [record[key + "_i18n"], record[key]]) {
    if (value && typeof value === "object" && !Array.isArray(value)) {
      const v = usable(value[locale]);
      if (v) return v;
      if (NAME_KEYS.has(key) && locale !== "zh-TW") {
        const zh = usable(value["zh-TW"]);
        if (zh) return zh;
      }
    }
  }
  if (locale === "zh-TW" && typeof record[key + "_zh"] === "string") {
    const v = usable(record[key + "_zh"]);
    if (v) return v;
  }
  if (properName && typeof record[key] === "string") {
    const v = usable(record[key]);
    if (v) return v;
  }
  return null;
}
export function safeUrl(value) {
  try { const u = new URL(value); return u.protocol === "https:" || u.protocol === "http:" ? u.href : null; } catch { return null; }
}
export function navigationAction(nav) {
  if (!nav || typeof nav !== "object") return null;
  const lat = Number(nav.lat), lon = Number(nav.lon);
  if (nav.lat == null || nav.lon == null || !Number.isFinite(lat) || !Number.isFinite(lon) || Math.abs(lat)>90 || Math.abs(lon)>180) return null;
  const coords = lat + "," + lon;
  if (nav.status === "verified") {
    if (!Array.isArray(nav.evidence_refs) || nav.evidence_refs.length===0 || !["entrance","trailhead","parking","station","street_access","viewpoint"].includes(nav.target_type)) return null;
    return {kind:"directions",url:"https://www.google.com/maps/dir/?api=1&destination=" + encodeURIComponent(coords)};
  }
  return null;
}
export function geometryType(record) {
  return TYPES.has(record?.geometry_type) ? record.geometry_type : null;
}
export function relationValue(value, unit) {
  return typeof value === "number" && Number.isFinite(value) && typeof unit === "string" && unit.trim() ? value + " " + unit : null;
}
export function runtimeEvaluation(record) {
  // Worker 3's reviewed EvaluationResult contract is not yet released. Fail closed.
  return null;
}
export function associated(rowsList, key, value) { return rowsList.filter(x => String(x[key] ?? "") === String(value)); }

// A presentation of existing research, never a condition evaluator. Role and
// evaluation mode are independent; even AUTO alone proves no connected result.
export function researchTopic(catalog, opportunity, locale) {
  const id = opportunityId(opportunity);
  const conditions = rows(catalog?.conditions)
    .filter(row => row.opportunity_id === id && row.domain !== 'ACCESS_SAFETY');
  return {
    id,
    name: localized(opportunity, 'name', locale),
    description: localized(opportunity, 'description', locale),
    targets: rows(catalog?.subject_geometries)
      .filter(row => row.opportunity_id === id)
      .map(row => localized(row, 'name', locale)).filter(Boolean),
    conditions: conditions.map(row => ({
      id: row.condition_id,
      description: localized(row, 'human_description', locale),
      role: ['REQUIRED', 'QUALITY', 'BLOCKER'].includes(row.role) ? row.role : null,
      mode: ['GUIDANCE', 'VERIFY', 'AUTO'].includes(row.evaluation_mode) ? row.evaluation_mode : null,
      domain: row.domain
    })),
    // Canonical imports have no authenticated result channel. Do not treat
    // a research condition, source availability or claimed AUTO flag as PASS.
    automaticEvaluationConnected: false,
    evaluation: null
  };
}
