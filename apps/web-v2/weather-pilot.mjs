// W4 read-only hourly weather-information pilot display (tw-036 sidecar).
// Renders the admitted RAW_ONLY research artifact; never a photography
// forecast: no scores, no directions, no availability verdicts. The artifact
// identity is re-verified in the browser and the retrieval age is recomputed
// at display time per the W1 freshness contract.
const PILOT_ID = 'tw-036-open-meteo-hourly-v0.1';
const PLACE_ID = 'tw-036';
const BINDING_SHA256 = '9fb4cc6f89daae3ce851a30f2880847705b4afa6097b7c4c54d19d357b202921';
const FIELD_ORDER = ['temperature_2m', 'dew_point_2m', 'relative_humidity_2m',
  'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high',
  'wind_speed_10m', 'visibility', 'precipitation', 'precipitation_probability'];

export const COPY = {
  'zh-TW': {
    pageTitle: 'ChaseLights V2 — 逐時天氣研究資料（試點）',
    heading: '七星潭逐時天氣研究資料', language: '語言', languageAria: '語言選擇',
    intro: '研究用原始網格預報資料；不是攝影預報，不提供拍攝建議或分數。',
    placeLabel: '研究地點', pilotLabel: '試點識別碼', bindingLabel: 'W2 綁定 SHA256',
    dataState: '資料狀態', availability: '資料完整度', tzdbLabel: '執行時 tzdb 版本',
    retrievalHeading: '取得時間與時效', retrievedAt: '資料取得時間（UTC）',
    ageNow: '距取得時間', staleNotice: '已超過研究時效上限（6 小時）：以下資料僅供回顧，請勿視為目前天氣。',
    currentNotice: '仍在研究時效內（自取得時間起 6 小時內）。',
    freshnessBasis: '時效以「資料取得時間」計算；模式發行時間由供應商未提供，一律不明示為新鮮。',
    unknownsHeading: '供應商未提供的欄位（一律標記未知）',
    unknownReason: '原因：預報回應未提供（NOT_SUPPLIED_BY_FORECAST_RESPONSE）',
    gridHeading: '請求點與回應格點', requestPoint: '請求座標（代表性地點樣本）',
    gridPoint: '回應格點座標（供應商選取）', elevation: '格點高程',
    tableHeading: '逐時資料（72 小時；10 欄位）', hourColumn: '當地時間（Asia/Taipei）',
    precedingNote: '降水與降水機率屬「前一個小時」累積值（區間起點不含、終點含）。',
    limitationsHeading: '已知限制', attributionHeading: '資料來源與授權',
    providerLabel: '提供者', licenceLabel: '授權', modificationsLabel: '轉換說明',
    unavailable: '未提供', footer: 'ChaseLights V2 試點研究資料。RAW_ONLY；未經校準，不得用於拍攝決策。',
    loadError: '研究資料無法通過驗證，已停止顯示：'
  },
  en: {
    pageTitle: 'ChaseLights V2 — hourly weather research data (pilot)',
    heading: 'Qixingtan hourly weather research data', language: 'Language', languageAria: 'Language selection',
    intro: 'Research-only raw grid forecast data; not a photography forecast, no advice or scores.',
    placeLabel: 'Research place', pilotLabel: 'Pilot ID', bindingLabel: 'W2 binding SHA256',
    dataState: 'Data state', availability: 'Data completeness', tzdbLabel: 'tzdb release at execution',
    retrievalHeading: 'Retrieval time and freshness', retrievedAt: 'Retrieved at (UTC)',
    ageNow: 'Age since retrieval', staleNotice: 'Older than the research freshness bound (6 hours): this is a historical record, not current weather.',
    currentNotice: 'Within the research freshness bound (6 hours since retrieval).',
    freshnessBasis: 'Freshness counts from retrieval time; the model issue time is not supplied by the provider and is never presented as fresh.',
    unknownsHeading: 'Fields the provider does not supply (always labelled unknown)',
    unknownReason: 'Reason: not supplied by the forecast response (NOT_SUPPLIED_BY_FORECAST_RESPONSE)',
    gridHeading: 'Request point and response grid', requestPoint: 'Request coordinate (representative place sample)',
    gridPoint: 'Response grid coordinate (provider-selected)', elevation: 'Grid elevation',
    tableHeading: 'Hourly table (72 hours; 10 fields)', hourColumn: 'Local time (Asia/Taipei)',
    precedingNote: 'Precipitation and probability are preceding-hour accumulations (open start, closed end).',
    limitationsHeading: 'Known limitations', attributionHeading: 'Source and licence',
    providerLabel: 'Provider', licenceLabel: 'Licence', modificationsLabel: 'Transformation notice',
    unavailable: 'Not provided', footer: 'ChaseLights V2 pilot research data. RAW_ONLY; uncalibrated; not for shooting decisions.',
    loadError: 'Research data failed verification; display stopped: '
  },
  ja: {
    pageTitle: 'ChaseLights V2 — 時間別天気調査データ（パイロット）',
    heading: '七星潭の時間別天気調査データ', language: '言語', languageAria: '言語の選択',
    intro: '調査用の生グリッド予報データです。撮影予報ではなく、助言や点数は表示しません。',
    placeLabel: '調査地点', pilotLabel: 'パイロット ID', bindingLabel: 'W2 バインディング SHA256',
    dataState: 'データ状態', availability: 'データ完全性', tzdbLabel: '実行時の tzdb 版',
    retrievalHeading: '取得時刻と鮮度', retrievedAt: 'データ取得時刻（UTC）',
    ageNow: '取得からの経過', staleNotice: '調査用の鮮度上限（6 時間）を超えています。過去の記録であり、現在の天気として扱わないでください。',
    currentNotice: '調査用の鮮度内です（取得から 6 時間以内）。',
    freshnessBasis: '鮮度はデータ取得時刻から計算します。モデルの発行時刻は提供されないため、新鮮と表示することはありません。',
    unknownsHeading: '提供元が供給しない項目（常に不明と表示）',
    unknownReason: '理由：予報レスポンスに未提供（NOT_SUPPLIED_BY_FORECAST_RESPONSE）',
    gridHeading: '要求座標と応答グリッド', requestPoint: '要求座標（代表地点サンプル）',
    gridPoint: '応答グリッド座標（提供元選択）', elevation: 'グリッド標高',
    tableHeading: '時間別表（72 時間・10 項目）', hourColumn: '現地時刻（Asia/Taipei）',
    precedingNote: '降水・降水確率は「前の 1 時間」の累積値です（始点を含まない・終点を含む）。',
    limitationsHeading: '既知の制限', attributionHeading: '出典とライセンス',
    providerLabel: '提供元', licenceLabel: 'ライセンス', modificationsLabel: '変換の説明',
    unavailable: '未提供', footer: 'ChaseLights V2 パイロット調査データ。RAW_ONLY・未校正・撮影判断には使用できません。',
    loadError: '調査データが検証に失敗したため表示を中止しました：'
  }
};

export const FIELD_LABELS = {
  'zh-TW': { temperature_2m: '氣溫 2m', dew_point_2m: '露點 2m', relative_humidity_2m: '相對濕度', cloud_cover_low: '低雲量', cloud_cover_mid: '中雲量', cloud_cover_high: '高雲量', wind_speed_10m: '風速 10m', visibility: '能見度', precipitation: '降水量（前一小時）', precipitation_probability: '降水機率（前一小時）' },
  en: { temperature_2m: 'Temperature 2m', dew_point_2m: 'Dew point 2m', relative_humidity_2m: 'Relative humidity', cloud_cover_low: 'Low cloud', cloud_cover_mid: 'Mid cloud', cloud_cover_high: 'High cloud', wind_speed_10m: 'Wind speed 10m', visibility: 'Visibility', precipitation: 'Precipitation (preceding hour)', precipitation_probability: 'Precipitation probability (preceding hour)' },
  ja: { temperature_2m: '気温 2m', dew_point_2m: '露点 2m', relative_humidity_2m: '相対湿度', cloud_cover_low: '下層雲量', cloud_cover_mid: '中層雲量', cloud_cover_high: '上層雲量', wind_speed_10m: '風速 10m', visibility: '視程', precipitation: '降水量（前の 1 時間）', precipitation_probability: '降水確率（前の 1 時間）' }
};

const UTC_ISO = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
const HOUR_MS = 3600000;

export function validateArtifact(a) {
  if (!a || typeof a !== 'object') throw new Error('ARTIFACT_MISSING');
  for (const [key, expected] of [['pilot_id', PILOT_ID], ['place_id', PLACE_ID],
    ['pilot_binding_sha256', BINDING_SHA256]]) {
    if (a[key] !== expected) throw new Error('ARTIFACT_IDENTITY_MISMATCH: ' + key);
  }
  if (a.data_state !== 'RAW_ONLY' || a.calibration_status !== 'UNVALIDATED'
    || a.recommendation_eligible !== false || a.photography_verdict !== 'NOT_EVALUABLE'
    || a.availability !== 'COMPLETE') throw new Error('ARTIFACT_STATE_NOT_RESEARCH_RAW');
  if (a.time_zone !== 'Asia/Taipei') throw new Error('ARTIFACT_ZONE_MISMATCH');
  if (!Array.isArray(a.hours) || a.hours.length !== 72) throw new Error('ARTIFACT_HORIZON_NOT_72');
  let previous = 0;
  for (let index = 0; index < a.hours.length; index++) {
    const row = a.hours[index];
    if (typeof row.valid_at_utc !== 'string' || !UTC_ISO.test(row.valid_at_utc)) throw new Error('ARTIFACT_TIME_AXIS_INVALID');
    const stamp = Date.parse(row.valid_at_utc);
    if (!Number.isFinite(stamp) || stamp % HOUR_MS !== 0) throw new Error('ARTIFACT_TIME_AXIS_INVALID');
    if (index && stamp !== previous + HOUR_MS) throw new Error('ARTIFACT_TIME_AXIS_NOT_CONTIGUOUS');
    previous = stamp;
    const values = row.values;
    if (!values || typeof values !== 'object') throw new Error('ARTIFACT_VALUES_MISSING');
    for (const field of FIELD_ORDER) {
      const cell = values[field];
      if (!cell || typeof cell !== 'object' || cell.state !== 'AVAILABLE'
        || !Number.isFinite(cell.value) || typeof cell.source_unit !== 'string'
        || cell.reason_code !== null) throw new Error('ARTIFACT_CELL_INVALID: ' + field);
    }
    if (Object.keys(values).length !== FIELD_ORDER.length) throw new Error('ARTIFACT_FIELD_COUNT_MISMATCH');
  }
  if (!a.attribution || !a.limitations_i18n) throw new Error('ARTIFACT_ATTRIBUTION_MISSING');
  return a;
}

export function retrievalAgeSeconds(nowMs, artifact) {
  return (nowMs - Date.parse(artifact.source.retrieved_at_utc)) / 1000;
}

export function staleness(ageSeconds, maxAgeSeconds = 21600) {
  return ageSeconds > maxAgeSeconds ? 'STALE' : 'CURRENT';
}

export function formatHourAsiaTaipei(isoUtc) {
  const date = new Date(Date.parse(isoUtc) + 8 * HOUR_MS);
  return date.toISOString().slice(0, 16).replace('T', ' ');
}

function esc(text) {
  return String(text).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
}

function unknownRows(copy, artifact) {
  const keys = ['source_update_time_utc', 'provider_issued_at_utc', 'provider_run_id',
    'resolved_model_ids', 'native_resolution_m', 'native_time_resolution_seconds'];
  const reason = artifact.source.source_metadata_reason || 'NOT_SUPPLIED_BY_FORECAST_RESPONSE';
  return keys.map(key => {
    const value = artifact.source[key];
    const known = value !== null && value !== undefined;
    return '<tr><th scope="row">' + esc(key) + '</th><td>'
      + esc(known ? String(value) : copy.unavailable) + '</td><td>'
      + esc(known ? '' : copy.unknownReason.replace('NOT_SUPPLIED_BY_FORECAST_RESPONSE', reason))
      + '</td></tr>';
  }).join('');
}

function tableHtml(copy, labels, artifact) {
  const head = '<tr><th scope="col">' + esc(copy.hourColumn) + '</th>'
    + FIELD_ORDER.map(f => '<th scope="col">' + esc(labels[f]) + '</th>').join('') + '</tr>';
  const body = artifact.hours.map(row => {
    const cells = FIELD_ORDER.map(field => {
      const cell = row.values[field];
      const shown = cell.state === 'AVAILABLE' ? cell.value + ' ' + cell.unit : copy.unavailable;
      return '<td>' + esc(shown) + '</td>';
    }).join('');
    return '<tr><th scope="row">' + esc(formatHourAsiaTaipei(row.valid_at_utc)) + '</th>' + cells + '</tr>';
  }).join('');
  return '<table><thead>' + head + '</thead><tbody>' + body + '</tbody></table>';
}

export function render(doc, artifact, locale, nowMs) {
  const copy = COPY[locale] || COPY['zh-TW'];
  const labels = FIELD_LABELS[locale] || FIELD_LABELS['zh-TW'];
  const age = Math.max(0, Math.floor(retrievalAgeSeconds(nowMs, artifact)));
  const stale = staleness(age) === 'STALE';
  const ageText = Math.floor(age / 3600) + ' h ' + Math.floor((age % 3600) / 60) + ' min';
  const request = artifact.request;
  const source = artifact.source;
  return '<h1>' + esc(copy.heading) + '</h1>'
    + '<p class="pilot-intro">' + esc(copy.intro) + '</p>'
    + '<p>' + esc(copy.placeLabel) + ': ' + esc(artifact.place_id) + ' · '
    + esc(copy.pilotLabel) + ': ' + esc(artifact.pilot_id) + ' · '
    + esc(copy.bindingLabel) + ': <code>' + esc(artifact.pilot_binding_sha256.slice(0, 16)) + '…</code> · '
    + esc(copy.tzdbLabel) + ': ' + esc(artifact.tzdb_version) + '</p>'
    + '<h2>' + esc(copy.retrievalHeading) + '</h2>'
    + '<p>' + esc(copy.retrievedAt) + ': ' + esc(artifact.source.retrieved_at_utc) + '<br>'
    + esc(copy.ageNow) + ': ' + esc(ageText) + '<br>'
    + '<strong>' + esc(stale ? copy.staleNotice : copy.currentNotice) + '</strong><br>'
    + esc(copy.freshnessBasis) + '</p>'
    + '<h2>' + esc(copy.unknownsHeading) + '</h2>'
    + '<table><tbody>' + unknownRows(copy, artifact) + '</tbody></table>'
    + '<p>' + esc(copy.unknownReason) + '</p>'
    + '<h2>' + esc(copy.gridHeading) + '</h2>'
    + '<p>' + esc(copy.requestPoint) + ': ' + esc(request.latitude + ', ' + request.longitude)
    + ' (' + esc(request.coordinate_role) + ')<br>'
    + esc(copy.gridPoint) + ': ' + esc(source.response_grid_latitude + ', ' + source.response_grid_longitude)
    + '<br>' + esc(copy.elevation) + ': ' + esc(String(source.response_elevation_m)) + ' m</p>'
    + '<h2>' + esc(copy.tableHeading) + '</h2>'
    + '<p>' + esc(copy.precedingNote) + '</p>'
    + tableHtml(copy, labels, artifact)
    + '<h2>' + esc(copy.limitationsHeading) + '</h2>'
    + '<p>' + esc(artifact.limitations_i18n[locale] || artifact.limitations_i18n['en']) + '</p>'
    + '<h2>' + esc(copy.attributionHeading) + '</h2>'
    + '<p>' + esc(copy.providerLabel) + ': <a href="' + esc(artifact.attribution.provider_url) + '" rel="noopener">'
    + esc(artifact.attribution.provider_url) + '</a><br>'
    + esc(copy.licenceLabel) + ': <a href="' + esc(artifact.attribution.licence_url) + '" rel="noopener">'
    + esc(artifact.attribution.licence_url) + '</a><br>'
    + esc(copy.modificationsLabel) + ': '
    + esc(artifact.attribution.modifications_i18n[locale] || artifact.attribution.modifications_i18n['en']) + '</p>'
    + '<p class="pilot-footer">' + esc(copy.footer) + '</p>';
}

export async function mountPilot(doc, locale, nowMs, fetchImpl) {
  const response = await (fetchImpl || ((ref) => fetch(ref)))('./weather-pilot-tw036.json');
  if (!response.ok) throw new Error('HTTP_' + response.status);
  const artifact = validateArtifact(await response.json());
  doc.title = (COPY[locale] || COPY['zh-TW']).pageTitle;
  doc.getElementById('pilot-root').innerHTML = render(doc, artifact, locale, nowMs);
  return artifact;
}

export const LOCALES = Object.keys(COPY);

if (typeof document !== 'undefined' && document.getElementById('pilot-root')) {
  const select = document.getElementById('pilot-language');
  const run = () => mountPilot(document, select ? select.value : 'zh-TW', Date.now()).catch(error => {
    document.getElementById('pilot-root').textContent =
      (COPY[select ? select.value : 'zh-TW'].loadError) + error.message;
  });
  if (select) select.addEventListener('change', run);
  run();
}
