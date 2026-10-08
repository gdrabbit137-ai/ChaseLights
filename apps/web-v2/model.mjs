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
  const fields = ["places","opportunities","camera_zones","subject_geometries","view_relations","condition_contracts","conditions","evidence","research_status","unknowns","evaluations"];
  const result = Object.fromEntries(fields.map(k => [k,rows(data[k])]));
  result.metadata = data.metadata && typeof data.metadata === "object" ? data.metadata : {};
  result.generated_at = data.generated_at || result.metadata.generated_at || null;
  if (!result.places.length) throw new Error("No V2 places");
  return result;
}
export function placeId(place) { return idOf(place,["spot_id","place_id","id"]); }
export function opportunityId(opp) { return idOf(opp,["opportunity_id","id"]); }
export function linkedPlaceId(opp) { return idOf(opp,["place_id","spot_id"]); }
export function localized(record, key, locale, properName = false) {
  if (!record || !LOCALES.includes(locale)) return null;
  for (const value of [record[key + "_i18n"],record[key]]) {
    if (value && typeof value === "object" && !Array.isArray(value) && typeof value[locale] === "string" && value[locale].trim()) return value[locale].trim();
  }
  if (locale === "zh-TW" && typeof record[key + "_zh"] === "string" && record[key + "_zh"].trim()) return record[key + "_zh"].trim();
  if (properName && typeof record[key] === "string" && record[key].trim()) return record[key].trim();
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
  if (nav.status === "verified") return {kind:"directions",url:"https://www.google.com/maps/dir/?api=1&destination=" + encodeURIComponent(coords)};
  if (nav.status === "provisional_camera_anchor") return {kind:"map",url:"https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(coords)};
  return null;
}
export function geometryType(record) {
  return TYPES.has(record?.geometry_type) ? record.geometry_type : null;
}
export function relationValue(value, unit) {
  return typeof value === "number" && Number.isFinite(value) && typeof unit === "string" && unit.trim() ? value + " " + unit : null;
}
export function runtimeEvaluation(record) {
  // Never infer live readiness from a score or a historical observation alone.
  if (!record || record.kind !== "runtime" || record.contract_status !== "ready" || !record.source || !record.generated_at) return null;
  return record;
}
export function associated(rowsList, key, value) { return rowsList.filter(x => String(x[key] ?? "") === String(value)); }
