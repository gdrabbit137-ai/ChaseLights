// W4 display contract for the archived, single-place RAW_ONLY pilot.
// This module never requests a provider or derives a photography result.
export const HOURLY_FIELDS = Object.freeze([
  ['temperature_2m', '°C'], ['dew_point_2m', '°C'],
  ['relative_humidity_2m', '%'], ['cloud_cover_low', '%'],
  ['cloud_cover_mid', '%'], ['cloud_cover_high', '%'],
  ['wind_speed_10m', 'm/s'], ['visibility', 'm'],
  ['precipitation', 'mm'], ['precipitation_probability', '%']
]);
export const ARCHIVE_SHA256 = 'e1ed353e7fcbe5a542d54da1c50e8f2b990fdade834b6fa54be0a53e1191b9ab';
export const ORIGINAL_RESPONSE_SHA256 = 'e441ea1bad2d42cfd89169bb030d7aec518d798c56aafe61e037f8a0e9406b1f';
const REQUIRED_REQUEST_FIELDS = HOURLY_FIELDS.map(([key]) => key).join(',');
const pilot = 'tw-036-open-meteo-hourly-v0.1';

export function inspectHourlyArtifact(artifact, now = Date.now()) {
  if (!artifact || artifact.schema_version !== '0.1.0' || artifact.artifact_kind !== 'HOURLY_WEATHER_INFO' ||
      artifact.pilot_id !== pilot || artifact.place_id !== 'tw-036' || artifact.time_zone !== 'Asia/Taipei' ||
      artifact.data_state !== 'RAW_ONLY' || artifact.calibration_status !== 'UNVALIDATED' ||
      artifact.recommendation_eligible !== false || artifact.photography_verdict !== 'NOT_EVALUABLE' ||
      !['COMPLETE', 'PARTIAL', 'STALE'].includes(artifact.availability) ||
      artifact.request?.hourly !== REQUIRED_REQUEST_FIELDS || artifact.request?.coordinate_role !== 'representative_place_weather_sample' ||
      artifact.source?.provider !== 'OPEN_METEO' || artifact.source?.source_sha256 !== ORIGINAL_RESPONSE_SHA256 ||
      artifact.source?.retrieval_mode !== 'HTTPS_TLS' || artifact.source?.source_update_time_utc !== null ||
      artifact.source?.provider_issued_at_utc !== null || artifact.source?.source_freshness !== 'UNKNOWN' ||
      artifact.retrieval_age_policy?.max_age_seconds !== 21600 || !Array.isArray(artifact.hours) ||
      artifact.hours.length < 1 || artifact.hours.length > 72 ||
      !['zh-TW', 'en', 'ja'].every(locale => artifact.attribution?.modifications_i18n?.[locale] && artifact.limitations_i18n?.[locale])) {
    throw new Error('Invalid archived hourly contract');
  }
  const retrieved = Date.parse(artifact.source.retrieved_at_utc);
  if (!Number.isFinite(retrieved) || !Number.isFinite(now) || now < retrieved ||
      Date.parse(artifact.source.normalized_at_utc) < retrieved) throw new Error('Invalid retrieval clock');
  let prior = null;
  let partial = artifact.hours.length !== 72;
  for (const hour of artifact.hours) {
    const instant = Date.parse(hour.valid_at_utc);
    if (!Number.isFinite(instant) || (prior !== null && instant - prior !== 3600000)) throw new Error('Invalid hourly axis');
    if (Date.parse(hour.preceding_hour?.start_utc) !== instant - 3600000 ||
        Date.parse(hour.preceding_hour?.end_utc) !== instant) throw new Error('Invalid preceding hour');
    prior = instant;
    for (const [key, unit] of HOURLY_FIELDS) {
      const cell = hour.values?.[key];
      if (!cell || cell.unit !== unit || !['AVAILABLE', 'UNAVAILABLE'].includes(cell.state)) throw new Error('Invalid hourly cell');
      if (cell.state === 'AVAILABLE') {
        if (typeof cell.value !== 'number' || !Number.isFinite(cell.value) || cell.source_unit !== unit || cell.reason_code !== null ||
            (unit === '%' && (cell.value < 0 || cell.value > 100)) ||
            (key !== 'temperature_2m' && key !== 'dew_point_2m' && unit !== '%' && cell.value < 0)) throw new Error('Invalid available value');
      } else {
        if (cell.value !== null || !['MISSING_FIELD', 'NULL_VALUE', 'INVALID_VALUE', 'UNIT_MISMATCH'].includes(cell.reason_code))
          throw new Error('Invalid unavailable value');
        partial = true;
      }
    }
  }
  if (artifact.availability === 'COMPLETE' && partial) throw new Error('False complete availability');
  // The bundled one-shot is historical regardless of the browser clock or its original COMPLETE state.
  return {state: 'STALE', evaluation: 'NOT_EVALUABLE', partial, hours: artifact.hours,
    retrievedAt: artifact.source.retrieved_at_utc, source: artifact.source,
    attribution: artifact.attribution, limitations: artifact.limitations_i18n};
}

export function displayHourlyCell(cell, locale) {
  if (cell?.state !== 'AVAILABLE' || typeof cell.value !== 'number' || !Number.isFinite(cell.value)) return null;
  return `${new Intl.NumberFormat(locale, {maximumFractionDigits: 2}).format(cell.value)} ${cell.unit}`;
}

export function taipeiTime(instant, locale, options = {}) {
  return new Intl.DateTimeFormat(locale, {timeZone: 'Asia/Taipei', ...options}).format(new Date(instant));
}
