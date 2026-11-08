// W4 read-only solar WINDOW pilot display (tw-036 sidecar).
// Renders the committed deterministic solar research artifact. It never
// issues a photography verdict: the WINDOW capability is a deterministic
// technical computation at an ideal unobstructed horizon from a
// representative place sample — not a tripod GPS, not a weather forecast
// and not a shooting recommendation. Bundle identity is re-verified in
// the browser and past local dates are marked honestly stale.
const PILOT_ID = 'tw-036-solar-window-v0.1';
const PLACE_ID = 'tw-036';
const DAYS = 14;

export const COPY = {
  'zh-TW': {
    pageTitle: 'ChaseLights V2 — 太陽視窗研究資料（試點）',
    heading: '七星潭太陽視窗研究資料', language: '語言', languageAria: '語言選擇',
    intro: '研究用確定性太陽視窗計算；不是攝影預報，不提供拍攝建議或分數。',
    placeLabel: '研究地點', pilotLabel: '試點識別碼', availability: '資料完整度',
    generatedAt: '計算執行時間（UTC）', generatorLabel: '產生器版本', tzdbLabel: 'tzdata 版本',
    sourceLabel: '計算來源', tableHeading: '逐日視窗（理想無遮蔽地平線）',
    dateColumn: '當地日期', sunriseColumn: '日出（當地）', sunsetColumn: '日落（當地）',
    polarColumn: '極日狀態', pastNotice: '此日期已過去：僅供回顧。',
    futureNotice: '尚未到來的日期：事件時刻不隨天氣改變，但可見性仍取決於天氣與實際地平線。',
    horizonNotice: '理想無遮蔽地平線近似（-0.833° 視高度）：實際山棱、建築與大氣折射會改變可見時刻。',
    sampleNotice: '座標為代表性地點樣本，不是實測機位座標；此結果不得用於確認任何地平線對齊。',
    unknownsHeading: '本頁未提供的內容',
    limitationsHeading: '已知限制', attributionHeading: '演算法依據',
    limitations: '理想無遮蔽地平線的區域性日出日落估算（代表性地點樣本，非實測機位座標）；未驗證實際地形地平線、大氣折射、雲況或攝影適合度，不構成拍攝建議。',
    attribution: '演算法：NOAA 太陽計算法（時間方程／赤緯）與 Jean Meeus《Astronomical Algorithms》；以 -0.833° 視高度近似。',
    notProvided: '不提供：拍攝建議、分數、導航、雲況或天氣推論。',
    footer: 'ChaseLights V2 試點研究資料。WINDOW ≠ FAVORABLE；未經校準，不得用於拍攝決策。',
    loadError: '研究資料無法通過驗證，已停止顯示：'
  },
  en: {
    pageTitle: 'ChaseLights V2 — solar window research data (pilot)',
    heading: 'Qixingtan solar window research data', language: 'Language', languageAria: 'Language selection',
    intro: 'Deterministic solar-window research computation; not a photography forecast, no advice or scores.',
    placeLabel: 'Research place', pilotLabel: 'Pilot ID', availability: 'Data completeness',
    generatedAt: 'Computed at (UTC)', generatorLabel: 'Generator version', tzdbLabel: 'tzdata release',
    sourceLabel: 'Computation source', tableHeading: 'Daily windows (ideal unobstructed horizon)',
    dateColumn: 'Local date', sunriseColumn: 'Sunrise (local)', sunsetColumn: 'Sunset (local)',
    polarColumn: 'Polar state', pastNotice: 'This date has passed: historical reference only.',
    futureNotice: 'Upcoming date: event instants do not change with weather, but visibility still depends on weather and the real horizon.',
    horizonNotice: 'Ideal unobstructed-horizon approximation (-0.833 deg apparent altitude): real terrain, buildings and refraction shift the visible event.',
    sampleNotice: 'The coordinate is a representative place sample, not a surveyed camera point; this result must not be used to confirm any horizon alignment.',
    unknownsHeading: 'What this page does not provide',
    limitationsHeading: 'Known limitations', attributionHeading: 'Algorithm basis',
    limitations: 'Regional sunrise/sunset at an ideal unobstructed horizon from a representative place sample (not a surveyed camera point); actual terrain horizon, refraction, clouds and photographic suitability are unverified. Not a shooting recommendation.',
    attribution: 'Algorithms: NOAA Solar Calculation Details (equation of time / declination) and Jean Meeus, Astronomical Algorithms; -0.833 deg apparent-altitude approximation.',
    notProvided: 'Not provided: shooting advice, scores, navigation, cloud or weather inference.',
    footer: 'ChaseLights V2 pilot research data. WINDOW is not FAVORABLE; uncalibrated; not for shooting decisions.',
    loadError: 'Research data failed verification; display stopped: '
  },
  ja: {
    pageTitle: 'ChaseLights V2 — 太陽ウィンドウ調査データ（パイロット）',
    heading: '七星潭の太陽ウィンドウ調査データ', language: '言語', languageAria: '言語の選択',
    intro: '決定論的な太陽ウィンドウ計算の調査データです。撮影予報ではなく、助言や点数は表示しません。',
    placeLabel: '調査地点', pilotLabel: 'パイロット ID', availability: 'データ完全性',
    generatedAt: '計算実行時刻（UTC）', generatorLabel: 'ジェネレーター版', tzdbLabel: 'tzdata 版',
    sourceLabel: '計算ソース', tableHeading: '日別ウィンドウ（理想の遮蔽なし水平線）',
    dateColumn: '現地日付', sunriseColumn: '日の出（現地）', sunsetColumn: '日の入り（現地）',
    polarColumn: '極昼状態', pastNotice: 'この日は過去です。過去の記録としてのみ表示します。',
    futureNotice: '今後の日付：時刻は天気で変わりませんが、見え方は天気と実際の地平線に依存します。',
    horizonNotice: '理想の遮蔽なし水平線近似（-0.833 度）：実際の山・建物・大気屈折で見え方の時刻は変わります。',
    sampleNotice: '座標は代表地点サンプルで、実測の撮影座標ではありません。この結果で地平線整合を確認することはできません。',
    unknownsHeading: 'このページが提供しないもの',
    limitationsHeading: '既知の制限', attributionHeading: 'アルゴリズム出典',
    limitations: '代表地点サンプルに基づく、遮蔽のない理想水平線での日の出・日の入り推定。実際の地形・屈折・雲・撮影適性は未確認で、撮影提案ではありません。',
    attribution: 'アルゴリズム：NOAA 太陽計算法（均時差・赤緯）および Jean Meeus『Astronomical Algorithms』。-0.833 度近似。',
    notProvided: '提供しないもの：撮影助言、点数、ナビゲーション、雲や天気の推論。',
    footer: 'ChaseLights V2 パイロット調査データ。WINDOW ≠ FAVORABLE。未校正のため撮影判断には使用できません。',
    loadError: '調査データが検証に失敗したため表示を中止しました：'
  }
};

const TIME_ZONE_OFFSET_MINUTES = 480; // Asia/Taipei fixed offset; verified against artifact time_zone.

export function validateArtifact(a) {
  if (!a || typeof a !== 'object') throw new Error('ARTIFACT_MISSING');
  for (const [key, expected] of [['pilot_id', PILOT_ID], ['place_id', PLACE_ID],
    ['schema_version', '0.1.0'], ['time_zone', 'Asia/Taipei']]) {
    if (a[key] !== expected) throw new Error('ARTIFACT_IDENTITY_MISMATCH: ' + key);
  }
  if (a.data_state !== 'RAW_ONLY' || a.calibration_status !== 'UNVALIDATED'
    || a.availability !== 'COMPLETE' || a.recommendation_eligible !== false
    || a.photography_verdict !== 'NOT_EVALUABLE') throw new Error('ARTIFACT_STATE_NOT_RESEARCH');
  if (!Array.isArray(a.results) || a.results.length !== DAYS
    || a.window_days.length !== DAYS) throw new Error('ARTIFACT_WINDOW_NOT_14_DAYS');
  let previous = null;
  for (const result of a.results) {
    if (result.capability !== 'WINDOW' || result.recommendation_eligible !== false
      || result.photography_verdict !== 'NOT_EVALUABLE'
      || result.time_zone !== 'Asia/Taipei') throw new Error('RESULT_STATE_NOT_WINDOW');
    if (!/^\d{4}-\d{2}-\d{2}$/.test(result.local_date)) throw new Error('RESULT_DATE_INVALID');
    if (previous && !(result.local_date > previous)) throw new Error('RESULT_DATES_NOT_ASCENDING');
    previous = result.local_date;
    for (const event of [result.sunrise, result.sunset]) {
      if (!event || typeof event !== 'object' || typeof event.status !== 'string') throw new Error('EVENT_MISSING');
      const calculated = event.status === 'CALCULATED';
      if (calculated !== (typeof event.time_utc === 'string' && typeof event.time_local === 'string')
        || (calculated && event.reason !== null)) throw new Error('EVENT_STATE_INCONSISTENT');
    }
    if (result.observer.coordinate_role !== 'representative_place_sample'
      || typeof result.observer.coordinate_source !== 'string') throw new Error('OBSERVER_PROVENANCE_INVALID');
    if (!result.limitations_i18n || !result.limitations_i18n['zh-TW']) throw new Error('LIMITATIONS_MISSING');
  }
  if (!a.generation || typeof a.generation.generated_at_utc !== 'string'
    || a.generation.tzdb_version === undefined) throw new Error('GENERATION_PROVENANCE_MISSING');
  if (!a.limitations_i18n || !a.attribution_i18n) throw new Error('BUNDLE_TEXT_MISSING');
  return a;
}

// Local calendar date in Asia/Taipei for a UTC instant, e.g. '2026-10-24'.
function localDateInTaipei(nowMs) {
  return new Date(nowMs + TIME_ZONE_OFFSET_MINUTES * 60000).toISOString().slice(0, 10);
}

function localTimeOfDay(isoLocal) {
  return typeof isoLocal === 'string' ? isoLocal.slice(11, 19) : null;
}

function esc(text) {
  return String(text).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
}

function tableHtml(copy, artifact, todayLocal) {
  const head = '<tr><th scope="col">' + esc(copy.dateColumn) + '</th><th scope="col">'
    + esc(copy.sunriseColumn) + '</th><th scope="col">' + esc(copy.sunsetColumn)
    + '</th><th scope="col">' + esc(copy.polarColumn) + '</th></tr>';
  const body = artifact.results.map(result => {
    const sunrise = result.sunrise.status === 'CALCULATED' ? localTimeOfDay(result.sunrise.time_local) : result.sunrise.status;
    const sunset = result.sunset.status === 'CALCULATED' ? localTimeOfDay(result.sunset.time_local) : result.sunset.status;
    const past = result.local_date < todayLocal;
    const dateCell = esc(result.local_date) + (past ? ' <span class="pilot-past">(' + esc(copy.pastNotice) + ')</span>' : '');
    return '<tr' + (past ? ' class="pilot-past-row"' : '') + '><th scope="row">' + dateCell
      + '</th><td>' + esc(sunrise) + '</td><td>' + esc(sunset)
      + '</td><td>' + esc(result.polar_state) + '</td></tr>';
  }).join('');
  return '<table><thead>' + head + '</thead><tbody>' + body + '</tbody></table>';
}

export function render(doc, artifact, locale, nowMs) {
  const copy = COPY[locale] || COPY['zh-TW'];
  const todayLocal = localDateInTaipei(nowMs);
  const generation = artifact.generation;
  return '<h1>' + esc(copy.heading) + '</h1>'
    + '<p class="pilot-intro">' + esc(copy.intro) + '</p>'
    + '<p>' + esc(copy.placeLabel) + ': ' + esc(artifact.place_id) + ' · '
    + esc(copy.pilotLabel) + ': ' + esc(artifact.pilot_id) + ' · '
    + esc(copy.availability) + ': ' + esc(artifact.availability) + '</p>'
    + '<p>' + esc(copy.generatedAt) + ': ' + esc(generation.generated_at_utc) + '<br>'
    + esc(copy.generatorLabel) + ': ' + esc(generation.generator_version) + ' · '
    + esc(copy.tzdbLabel) + ': ' + esc(String(generation.tzdb_version)) + '<br>'
    + esc(copy.sourceLabel) + ': ' + esc(generation.source) + '</p>'
    + '<h2>' + esc(copy.tableHeading) + '</h2>'
    + tableHtml(copy, artifact, todayLocal)
    + '<p>' + esc(copy.horizonNotice) + '<br>' + esc(copy.sampleNotice) + '<br>'
    + esc(copy.futureNotice) + '</p>'
    + '<h2>' + esc(copy.unknownsHeading) + '</h2>'
    + '<p>' + esc(copy.notProvided) + '</p>'
    + '<h2>' + esc(copy.limitationsHeading) + '</h2>'
    + '<p>' + esc(artifact.limitations_i18n[locale] || artifact.limitations_i18n['en']) + '</p>'
    + '<h2>' + esc(copy.attributionHeading) + '</h2>'
    + '<p>' + esc(artifact.attribution_i18n[locale] || artifact.attribution_i18n['en']) + '</p>'
    + '<p class="pilot-footer">' + esc(copy.footer) + '</p>';
}

export async function mountPilot(doc, locale, nowMs, fetchImpl) {
  const response = await (fetchImpl || ((ref) => fetch(ref)))('./solar-window-tw036.json');
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
