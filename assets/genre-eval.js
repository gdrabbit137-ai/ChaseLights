/* ChaseLights V1 — 攝影題材條件評估 (V2 evaluation bundle, GUIDANCE-only).
   CL-UI-93 (mockup-first Stage 3c): layout redo per
   data/v2/audits/design-mockups/mockup-genre-eval.html (DESIGN-3 3d455f121) —
   地區/景點/日期選擇 → 逐題材 8 日格（✓視窗/✗短詞/—點名缺項印在格內）、
   選中日同步、條件明細表（v-pass/v-fail/v-unk）。語義沿用現行資料結構
   （evaluations bundle + details），本頁不入 nav — 直達 URL（owner ruling）。 */
(function () {
  'use strict';

  const BUNDLE_URL = './apps/web-v2/evaluations-latest.json';
  const DETAILS_BASE = './apps/web-v2/evaluations-details/';

  const I18N = {
    'zh-TW': {
      title: '攝影題材條件評估', search: '搜尋景點…', loading: '正在載入評估資料…',
      load_error: '載入失敗，請稍後再試', updated: '評估產生時間',
      hours: '符合時數', today: '今天', today_v: '今日',
      cond: '條件', value: '現值', threshold: '門檻', verdict: '判定', th_metric: '指標',
      no_data: '此景點目前沒有可評估的題材。', cond_loading: '正在載入條件明細…',
      tab_ok: '✓ 符合', tab_no: '✗ 未符', tab_unk: '— 未評估', tab_all: '🌐 全部',
      unk_note: '：此題材缺輸入資料，非「不適合」。',
      unk_suffix: '未評估',
      r_tw: '🇹🇼 台灣', r_jp: '🇯🇵 日本', r_us: '🇺🇸 美國',
      v_sat: '符合', v_unsat: '未符', v_declared: '已宣告', v_no_data: '無資料',
      v_thr_prefix: '（門檻 ', v_thr_suffix: '）',
      metric_names: { cloud_cover_low: '低雲', cloud_cover_mid: '中雲', cloud_cover_high: '高雲', cloud_cover_mid_and_high: '中高雲', cloud_cover_total: '總雲量', wind_speed_10m: '風速', wind_speed_850hpa: '850hPa 風速', precipitation: '降水', aod_550nm: '氣膠光學厚度', visibility: '能見度', relative_humidity_2m: '相對濕度', relative_humidity_700hpa:'相對濕度 700hPa', relative_humidity_600hpa:'相對濕度 600hPa', wind_speed_700hpa:'700hPa 風速', wind_speed_600hpa:'600hPa 風速', temperature_delta_850_700_c:'T850−T700 溫差', temperature_delta_700_600_c:'T700−T600 溫差', relative_humidity_925hpa: '相對濕度 925hPa', relative_humidity_850hpa: '相對濕度 850hPa', lcl_height_m_agl: '抬升凝結高度', temperature_delta_850_925_c: 'T850−T925 溫差', sunrise_time_window: '日出時段', sunset_window: '日落時段', light_window: '民用光線', golden_hour_window: '黃金時段', blue_hour_window: '藍調時段', astronomical_darkness: '天文黑暗', moon_illumination_fraction: '月照亮百分比', moon_altitude: '月亮高度', moon_target_separation_deg: '月目標角距', moon_illuminance_proxy: '月光照度代理', galactic_core_altitude: '銀河核心高度', water_surface_state: '水面狀態', water_reflection_state: '水面平靜度', seasonal_state: '季節狀態', landform_present: '地形地貌存在', river_flow_state: '河川流量狀態' },
      genres: { mountain_view: '山景視野', overlook: '制高點展望', reflection: '水面倒影', cloud_sea: '雲海', sunrise: '日出', sunset: '日落夕景', golden_hour: '黃金時刻', blue_hour_city: '城市藍調', overcast_soft: '陰天柔光', city_night: '城市夜景', night_sky: '夜空星空', seasonal_plant: '季節植物', geological_landform: '地質地景', waterfall: '瀑布' },
      nav_cards: '卡片', nav_weathermap: '天氣圖', nav_more_tools: '更多工具 ▾', nav_genre_eval: '題材評估', nav_field_intake: '實拍驗證', nav_my: '我的'
    },
    en: {
      title: 'Genre Condition Assessment', search: 'Search places…', loading: 'Loading evaluations…',
      load_error: 'Load failed, please retry later', updated: 'Generated',
      hours: 'qualifying hours', today: 'Today', today_v: 'Today',
      cond: 'Condition', value: 'Value', threshold: 'Threshold', verdict: 'Verdict', th_metric: 'Metric',
      no_data: 'No assessable subjects for this place yet.', cond_loading: 'Loading condition details…',
      tab_ok: '✓ Met', tab_no: '✗ Not met', tab_unk: '— Not evaluated', tab_all: '🌐 All',
      unk_note: ': input data is missing for this subject — it is not "unsuitable".',
      unk_suffix: ' — not evaluated',
      r_tw: '🇹🇼 Taiwan', r_jp: '🇯🇵 Japan', r_us: '🇺🇸 United States',
      v_sat: 'Meets', v_unsat: 'Not met', v_declared: 'Declared', v_no_data: 'No data',
      v_thr_prefix: ' (threshold: ', v_thr_suffix: ')',
      metric_names: { cloud_cover_low: 'Low cloud', cloud_cover_mid: 'Mid cloud', cloud_cover_high: 'High cloud', cloud_cover_mid_and_high: 'Mid & high cloud', cloud_cover_total: 'Total cloud', wind_speed_10m: 'Wind', wind_speed_850hpa: 'Wind 850hPa', precipitation: 'Precipitation', aod_550nm: 'AOD 550nm', visibility: 'Visibility', relative_humidity_2m: 'Rel. humidity', relative_humidity_700hpa:'RH 700hPa', relative_humidity_600hpa:'RH 600hPa', wind_speed_700hpa:'Wind 700hPa', wind_speed_600hpa:'Wind 600hPa', temperature_delta_850_700_c:'T850−T700 delta', temperature_delta_700_600_c:'T700−T600 delta', relative_humidity_925hpa: 'RH 925hPa', relative_humidity_850hpa: 'RH 850hPa', lcl_height_m_agl: 'LCL height', temperature_delta_850_925_c: 'T850−T925 delta', sunrise_time_window: 'Sunrise window', sunset_window: 'Sunset window', light_window: 'Civil light', golden_hour_window: 'Golden hour', blue_hour_window: 'Blue hour', astronomical_darkness: 'Astronomical darkness', moon_illumination_fraction: 'Moon illumination', moon_altitude: 'Moon altitude', moon_target_separation_deg: 'Moon separation', moon_illuminance_proxy: 'Moon illuminance proxy', galactic_core_altitude: 'Galactic core altitude', water_surface_state: 'Water surface state', water_reflection_state: 'Water reflection state', seasonal_state: 'Seasonal state', landform_present: 'Landform presence', river_flow_state: 'River flow state' },
      genres: { mountain_view: 'Mountain view', overlook: 'Overlook', reflection: 'Water reflection', cloud_sea: 'Sea of clouds', sunrise: 'Sunrise', sunset: 'Sunset', golden_hour: 'Golden hour', blue_hour_city: 'City blue hour', overcast_soft: 'Overcast soft light', city_night: 'City night', night_sky: 'Night sky', seasonal_plant: 'Seasonal flora', geological_landform: 'Geological landform', waterfall: 'Waterfall' },
      nav_cards: 'Cards', nav_weathermap: 'Weather map', nav_more_tools: 'More tools ▾', nav_genre_eval: 'Genre assessment', nav_field_intake: 'Field check', nav_my: 'My Library'
    },
    ja: {
      title: '撮影題材の条件評価', search: '撮影地を検索…', loading: '評価データを読み込み中…',
      load_error: '読み込みに失敗しました', updated: '評価生成時刻',
      hours: '撮影に適した時間数', today: '今日', today_v: '今日',
      cond: '条件', value: '現在値', threshold: 'しきい値', verdict: '判定', th_metric: '指標',
      no_data: 'この撮影地には現在評価可能な題材がありません。', cond_loading: '条件の詳細を読み込み中…',
      tab_ok: '✓ 達成', tab_no: '✗ 未達成', tab_unk: '— 未評価', tab_all: '🌐 すべて',
      unk_note: '：この題材は入力データが不足しており、「不適合」ではありません。',
      unk_suffix: '未評価',
      r_tw: '🇹🇼 台湾', r_jp: '🇯🇵 日本', r_us: '🇺🇸 アメリカ',
      v_sat: '達成', v_unsat: '未達成', v_declared: '宣言済み', v_no_data: 'データなし',
      v_thr_prefix: '（しきい値 ', v_thr_suffix: '）',
      metric_names: { cloud_cover_low: '下層雲', cloud_cover_mid: '中層雲', cloud_cover_high: '上層雲', cloud_cover_mid_and_high: '中上層雲', cloud_cover_total: '全雲量', wind_speed_10m: '風速', wind_speed_850hpa: '850hPa 風速', precipitation: '降水', aod_550nm: 'エアロゾル光学的厚さ', visibility: '視程', relative_humidity_2m: '相対湿度', relative_humidity_700hpa:'相対湿度 700hPa', relative_humidity_600hpa:'相対湿度 600hPa', wind_speed_700hpa:'700hPa 風速', wind_speed_600hpa:'600hPa 風速', temperature_delta_850_700_c:'T850−T700 温度差', temperature_delta_700_600_c:'T700−T600 温度差', relative_humidity_925hpa: '相対湿度 925hPa', relative_humidity_850hpa: '相対湿度 850hPa', lcl_height_m_agl: 'LCL 高度', temperature_delta_850_925_c: 'T850−T925 温度差', sunrise_time_window: '日の出時間帯', sunset_window: '日の入り時間帯', light_window: '市民光', golden_hour_window: 'ゴールデンアワー', blue_hour_window: 'ブルーアワー', astronomical_darkness: '天文学的薄明', moon_illumination_fraction: '月照亮率', moon_altitude: '月高度', moon_target_separation_deg: '月角距離', moon_illuminance_proxy: '月光照度プロキシ', galactic_core_altitude: '銀河中心高度', water_surface_state: '水面状態', water_reflection_state: '水面の静けさ', seasonal_state: '季節状態', landform_present: '地形の存在', river_flow_state: '河川流量状態' },
      genres: { mountain_view: '山の眺望', overlook: '高所展望', reflection: '水面反射', cloud_sea: '雲海', sunrise: '日の出', sunset: '夕景', golden_hour: 'ゴールデンアワー', blue_hour_city: '都市ブルーアワー', overcast_soft: '曇天ソフトライト', city_night: '都市夜景', night_sky: '星空', seasonal_plant: '季節の植物', geological_landform: '地形・地質', waterfall: '滝' },
      nav_cards: 'カード', nav_weathermap: '天気マップ', nav_more_tools: 'その他のツール ▾', nav_genre_eval: '題材評価', nav_field_intake: '実写検証', nav_my: 'マイライブラリ'
    }
  };

  /* 題材短名（21 類）× 不符短詞 — 與 subject-cards 資料層的
     dictionaries.genre_short_names / fail_reason_short 同一詞表（本頁自帶
     三語包，和 reminders-page.js 同一做法），只用 metric id 對照，不重複造詞。 */
  const GENRE_SHORT = {
    blue_hour_city: {'zh-TW':'藍調','en':'Blue hour','ja':'ブルーアワー'},
    blue_tears: {'zh-TW':'藍眼淚','en':'Blue tears','ja':'藍眼淚'},
    city_night: {'zh-TW':'夜景','en':'City night','ja':'夜景'},
    cloud_sea: {'zh-TW':'雲海','en':'Cloud sea','ja':'雲海'},
    drift_ice: {'zh-TW':'流冰','en':'Drift ice','ja':'流氷'},
    general: {'zh-TW':'一般','en':'General','ja':'一般'},
    geological_landform: {'zh-TW':'地景','en':'Landform','ja':'地形'},
    golden_hour: {'zh-TW':'金光','en':'Golden hour','ja':'ゴールデンアワー'},
    mountain_view: {'zh-TW':'山景','en':'Mountain view','ja':'山景'},
    night_sky: {'zh-TW':'星空','en':'Night sky','ja':'星空'},
    overcast_soft: {'zh-TW':'陰柔光','en':'Soft overcast','ja':'柔光'},
    overlook: {'zh-TW':'眺望','en':'Overlook','ja':'眺望'},
    reflection: {'zh-TW':'倒影','en':'Reflection','ja':'水面反射'},
    seasonal_plant: {'zh-TW':'花季','en':'Seasonal flora','ja':'季節の花'},
    snow_ice: {'zh-TW':'冰雪','en':'Snow & ice','ja':'雪氷'},
    snow_ice_night: {'zh-TW':'夜冰雪','en':'Night snow & ice','ja':'夜の雪氷'},
    sunrise: {'zh-TW':'日出','en':'Sunrise','ja':'日の出'},
    sunset: {'zh-TW':'夕陽','en':'Sunset','ja':'夕景'},
    tidal: {'zh-TW':'潮汐','en':'Tide','ja':'潮汐'},
    volcanic_glow: {'zh-TW':'熔岩','en':'Lava glow','ja':'溶岩'},
    waterfall: {'zh-TW':'瀑布','en':'Waterfall','ja':'滝'}
  };
  const FAIL_SHORT = {
    aod_550nm: {'zh-TW':'霾','en':'haze','ja':'霞'},
    astronomical_darkness: {'zh-TW':'天不夠暗','en':'not dark enough','ja':'暗さ不足'},
    blue_hour_window: {'zh-TW':'非拍攝時段','en':'outside shooting window','ja':'撮影時間帯外'},
    city_night_window: {'zh-TW':'非拍攝時段','en':'outside shooting window','ja':'撮影時間帯外'},
    cloud_cover_low: {'zh-TW':'低雲','en':'low cloud','ja':'低い雲'},
    cloud_cover_mid: {'zh-TW':'厚雲','en':'thick cloud','ja':'厚い雲'},
    cloud_cover_mid_and_high: {'zh-TW':'厚雲','en':'thick cloud','ja':'厚い雲'},
    cloud_cover_total: {'zh-TW':'陰','en':'overcast','ja':'曇り'},
    daylight_window: {'zh-TW':'非拍攝時段','en':'outside shooting window','ja':'撮影時間帯外'},
    galactic_core_altitude: {'zh-TW':'銀河偏低','en':'galactic core too low','ja':'銀河中心が低い'},
    golden_hour_window: {'zh-TW':'非拍攝時段','en':'outside shooting window','ja':'撮影時間帯外'},
    landform_present: {'zh-TW':'地形不合','en':'landform not present','ja':'地形条件外'},
    lcl_height_m_agl: {'zh-TW':'雲底低','en':'low cloud base','ja':'雲底が低い'},
    legacy_drift_ice: {'zh-TW':'無流冰','en':'no drift ice','ja':'流氷なし'},
    legacy_long_exposure: {'zh-TW':'長曝條件','en':'long-exposure conditions off','ja':'長時間露出の条件外'},
    legacy_mountain_view: {'zh-TW':'條件不合','en':'conditions not met','ja':'条件が満たされず'},
    legacy_reflection: {'zh-TW':'條件不合','en':'conditions not met','ja':'条件が満たされず'},
    legacy_tide: {'zh-TW':'潮位不合','en':'tide not in range','ja':'潮位が適域外'},
    light_direction: {'zh-TW':'光向不合','en':'wrong light direction','ja':'光の向きが悪い'},
    light_window: {'zh-TW':'非日照時段','en':'outside daylight hours','ja':'日照時間帯外'},
    moon_altitude: {'zh-TW':'月位置','en':'moon position','ja':'月の位置'},
    moon_illuminance_proxy: {'zh-TW':'月太亮','en':'moon too bright','ja':'月明るすぎ'},
    moon_illumination_fraction: {'zh-TW':'月太亮','en':'moon too bright','ja':'月明るすぎ'},
    moon_target_separation_deg: {'zh-TW':'月位置','en':'moon position','ja':'月の位置'},
    moonrise_moonset_separation_h: {'zh-TW':'月位置','en':'moon position','ja':'月の位置'},
    nearshore_surf_state: {'zh-TW':'浪大','en':'heavy surf','ja':'うねり'},
    noctiluca_concentration: {'zh-TW':'藻量不足','en':'bioluminescence too sparse','ja':'夜光虫が少ない'},
    precipitation: {'zh-TW':'雨','en':'rain','ja':'雨'},
    relative_humidity_600hpa: {'zh-TW':'濕度不合','en':'humidity not in range','ja':'湿度が適域外'},
    relative_humidity_700hpa: {'zh-TW':'濕度不合','en':'humidity not in range','ja':'湿度が適域外'},
    relative_humidity_850hpa: {'zh-TW':'濕度不合','en':'humidity not in range','ja':'湿度が適域外'},
    relative_humidity_925hpa: {'zh-TW':'濕度不合','en':'humidity not in range','ja':'湿度が適域外'},
    river_flow_state: {'zh-TW':'溪水不佳','en':'river conditions wrong','ja':'川の状態が悪い'},
    seasonal_state: {'zh-TW':'非季節','en':'off-season','ja':'季節外れ'},
    sunrise_time_window: {'zh-TW':'非拍攝時段','en':'outside shooting window','ja':'撮影時間帯外'},
    sunset_window: {'zh-TW':'非拍攝時段','en':'outside shooting window','ja':'撮影時間帯外'},
    temperature_2m: {'zh-TW':'氣溫不合','en':'temperature out of range','ja':'気温が適域外'},
    temperature_delta_700_600_c: {'zh-TW':'大氣不合','en':'atmosphere not in range','ja':'大気条件外'},
    temperature_delta_850_700_c: {'zh-TW':'大氣不合','en':'atmosphere not in range','ja':'大気条件外'},
    temperature_delta_850_925_c: {'zh-TW':'大氣不合','en':'atmosphere not in range','ja':'大気条件外'},
    venue_open_window: {'zh-TW':'未開放','en':'closed','ja':'営業時間外'},
    visibility: {'zh-TW':'霧','en':'fog','ja':'霧'},
    volcanic_activity: {'zh-TW':'火山條件','en':'volcanic conditions off','ja':'火山の条件外'},
    water_surface_state: {'zh-TW':'水面不佳','en':'water surface not still','ja':'水面の状態が悪い'},
    wind_speed_10m: {'zh-TW':'風強','en':'strong wind','ja':'強風'},
    wind_speed_600hpa: {'zh-TW':'風強','en':'strong wind','ja':'強風'},
    wind_speed_700hpa: {'zh-TW':'風強','en':'strong wind','ja':'強風'},
    wind_speed_850hpa: {'zh-TW':'風強','en':'strong wind','ja':'強風'}
  };
  /* 未評估格點名缺項（hours-absurdity sweep）— 說出缺的輸入，不黑箱。 */
  const UNK_REASON = {
    seasonal_state: {'zh-TW':'季節曆未涵蓋','en':'No seasonal calendar','ja':'季節暦未カバー'},
    water_surface_state: {'zh-TW':'水況資料未接入','en':'Water-condition data not connected','ja':'水況データ未接続'},
    river_flow_state: {'zh-TW':'水況資料未接入','en':'Water-condition data not connected','ja':'水況データ未接続'},
    precipitation: {'zh-TW':'預報資料未涵蓋','en':'Outside forecast coverage','ja':'予報範囲外'},
    cloud_cover_total: {'zh-TW':'預報資料未涵蓋','en':'Outside forecast coverage','ja':'予報範囲外'},
    visibility: {'zh-TW':'預報資料未涵蓋','en':'Outside forecast coverage','ja':'予報範囲外'},
    wind_speed_10m: {'zh-TW':'預報資料未涵蓋','en':'Outside forecast coverage','ja':'予報範囲外'},
    aod_550nm: {'zh-TW':'預報資料未涵蓋','en':'Outside forecast coverage','ja':'予報範囲外'},
    golden_hour_window: {'zh-TW':'天文時段資料未接入','en':'Astronomy-window data not connected','ja':'天文時間帯データ未接続'},
    city_night_window: {'zh-TW':'天文時段資料未接入','en':'Astronomy-window data not connected','ja':'天文時間帯データ未接続'},
    astronomical_darkness: {'zh-TW':'天文時段資料未接入','en':'Astronomy-window data not connected','ja':'天文時間帯データ未接続'},
    light_window: {'zh-TW':'天文時段資料未接入','en':'Astronomy-window data not connected','ja':'天文時間帯データ未接続'},
    legacy_long_exposure: {'zh-TW':'長曝條件未評估','en':'long-exposure conditions not evaluated','ja':'長時間露出の条件は未評価'},
    legacy_mountain_view: {'zh-TW':'山景條件未評估','en':'mountain-view conditions not evaluated','ja':'山の眺望の条件は未評価'},
    legacy_reflection: {'zh-TW':'倒影條件未評估','en':'reflection conditions not evaluated','ja':'水面反射の条件は未評価'},
    legacy_tide: {'zh-TW':'潮位條件未評估','en':'tide conditions not evaluated','ja':'潮位の条件は未評価'},
    legacy_drift_ice: {'zh-TW':'流冰條件未評估','en':'drift-ice conditions not evaluated','ja':'流氷の条件は未評価'}
  };

  /* 不符短詞取主導失敗指標時的優先序（與卡片同一語義來源：評估束的
     day.conditions——FAIL/PARTIAL 才是攝影者的主因；UNKNOWN 不編原因）。 */
  const FAIL_PRIORITY = ['precipitation','visibility','aod_550nm','cloud_cover_low','cloud_cover_mid','cloud_cover_mid_and_high','cloud_cover_total','wind_speed_10m','lcl_height_m_agl','relative_humidity_925hpa','relative_humidity_700hpa','relative_humidity_600hpa','relative_humidity_850hpa','galactic_core_altitude','sunrise_time_window','sunset_window','golden_hour_window','blue_hour_window','city_night_window','light_window','astronomical_darkness','moon_illumination_fraction','moon_illuminance_proxy','moon_altitude','moon_target_separation_deg','wind_speed_850hpa','wind_speed_600hpa','temperature_delta_850_925_c','temperature_delta_700_600_c','water_surface_state','seasonal_state','river_flow_state','landform_present'];

  let lang = (typeof localStorage !== 'undefined' && localStorage.getItem('chaselights_lang')) || 'zh-TW';
  if (!I18N[lang]) lang = 'zh-TW';
  let bundle = null;
  let detailCache = new Map();   // place_id -> detail json
  let daySel = 0;
  let filter = 'all';
  let openRows = new Set();      // `${place_id}|${opportunity_id}`
  let searchQ = '';
  let pid = null;                // selected place_id

  const $ = (id) => document.getElementById(id);
  const t = () => I18N[lang];

  function esc(v) { return String(v ?? '').replace(/[&<>\"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;', "'": '&#39;' }[c])); }

  // CL-UI-09: English count pluralization — 1 subject / N subjects.
  // zh-TW/ja do not inflect for count (個題材/題材 are invariant).
  function subjectCountLabel(n, lang) {
    if (lang === 'en') return n === 1 ? 'subject' : 'subjects';
    if (lang === 'ja') return '題材';
    return '個題材';
  }

  function localizedName(obj) {
    if (!obj) return '';
    return obj[lang] || obj['zh-TW'] || obj['en'] || '';
  }

  function listSep() { return lang === 'en' ? ', ' : '、'; }

  function metricName(m) { return t().metric_names[m] || m; }
  function genreShort(g) { const s = GENRE_SHORT[g]; return s ? (s[lang] || s['zh-TW'] || g) : g; }
  function genreName(g) { return t().genres[g] || genreShort(g); }

  function fmtThreshold(c) {
    const th = c.threshold;
    if (th == null) return '—';
    if (c.operator === 'between' && Array.isArray(th)) return `${th[0]}–${th[1]}`;
    if (c.operator === 'lte') return `≤ ${th}`;
    if (c.operator === 'lt') return `< ${th}`;
    if (c.operator === 'gte') return `≥ ${th}`;
    if (c.operator === 'gt') return `> ${th}`;
    return String(th);
  }

  function verdictClass(v) { return v === 'PASS' ? 'v-pass' : v === 'FAIL' ? 'v-fail' : 'v-unk'; }

  // CL-UI-06: condition values are mapped to localized labels. Raw booleans
  // (legacy artifacts) and the pipeline enum 'satisfied'/'unsatisfied' both
  // resolve to human language; numeric and other values render as strings.
  function fmtValue(c) {
    const t2 = t();
    const v = c.value;
    if (v === true || v === 'satisfied') return t2.v_sat;
    if (v === false || v === 'unsatisfied') return t2.v_unsat;
    if (v === 'declared') return t2.v_declared;
    if (v == null) return t2.v_no_data;
    return String(v);
  }

  // Minor #7: photographer-friendly "value (threshold …)" cell — e.g. zh-TW
  // 「66（門檻 20–70）」 — localized per language, no raw "66 / 20–70".
  function fmtValueThreshold(c) {
    const v = fmtValue(c);
    const th = fmtThreshold(c);
    if (th === '—' || th === t().none) return v;
    return `${v}${t().v_thr_prefix}${th}${t().v_thr_suffix}`;
  }

  /* ── 日格語義（沿用現行評估束的三狀態）──────────────────────
     ✓ GUIDANCE_SATISFIED：good_hours 連續時段摺成視窗直接印在格內
     ✗ UNFAVORABLE：主導失敗指標 → fail_reason_short 短詞
     — NOT_EVALUABLE：點名缺的輸入（不得黑箱「—」） */
  /* good_hours 是評估層的合格時段「起點」（CL-DATA-68 後為分鐘級，每段一小
     時長）：相鄰段起點間距 ≤60 分即連續，整段視窗 = 首段起點 – 末段起點＋1h。 */
  function toMin(h) { const p = String(h).split(':'); return Number(p[0]) * 60 + Number(p[1]); }
  function fromMin(m) { return `${String(Math.floor(m / 60) % 24).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`; }
  function collapseHours(hours, sep) {
    if (!hours || !hours.length) return '';
    const s = sep || listSep();
    const hs = [...new Set(hours)].map(toMin).sort((a, b) => a - b);
    const ranges = [];
    let start = hs[0], prev = hs[0];
    for (let i = 1; i <= hs.length; i++) {
      const cur = hs[i];
      if (cur !== undefined && cur - prev <= 60) { prev = cur; continue; }
      ranges.push(`${fromMin(start)}–${fromMin(prev + 60)}`);
      start = prev = cur;
    }
    return ranges.join(s);
  }
  function dominantFailWord(conditions) {
    const failSet = new Set((conditions || [])
      .filter((c) => c && (c.day_verdict === 'FAIL' || c.day_verdict === 'PARTIAL'))
      .map((c) => c.metric));
    for (const m of FAIL_PRIORITY) {
      if (!failSet.has(m)) continue;
      const w = FAIL_SHORT[m];
      if (w) return w[lang] || w['zh-TW'] || '';
    }
    return '';
  }
  function unkReason(day) {
    const unk = (day.conditions || []).find((c) => c && c.day_verdict === 'UNKNOWN');
    if (!unk) return t().unk_suffix;
    const r = UNK_REASON[unk.metric];
    if (r) return r[lang] || r['zh-TW'] || t().unk_suffix;
    return `${metricName(unk.metric)}${t().unk_suffix}`;
  }
  function dayCellInfo(opp, dayIdx) {
    const day = (opp.days || [])[dayIdx];
    if (!day) return { cls: 'unk', text: `— ${t().unk_suffix}` };
    if (day.state === 'GUIDANCE_SATISFIED') {
      const win = collapseHours(day.good_hours || []);
      return { cls: 'ok', text: `✓ ${win || t().v_sat}` };
    }
    if (day.state === 'NOT_EVALUABLE') {
      return { cls: 'unk', text: `— ${unkReason(day)}` };
    }
    const word = dominantFailWord(day.conditions);
    return { cls: 'bad', text: `✗ ${word || t().v_unsat}` };
  }

  /* 條件明細代表值：門檻/現值取自 details 的逐時條件——符合日取第一個
     符合時段、未符日取該指標第一個 FAIL 時段、資料不足日取第一個 UNKNOWN
     時段；details 未涵蓋該日時誠實顯示「無資料」。 */
  function representativeCondition(detDay, metric, day) {
    if (!detDay || !detDay.hours || !detDay.hours.length) return null;
    const withMetric = detDay.hours.filter((h) => (h.conditions || []).some((c) => c.metric === metric));
    if (!withMetric.length) return null;
    const cond = (h) => (h.conditions || []).find((c) => c.metric === metric);
    let hour = null;
    if (day && day.state === 'GUIDANCE_SATISFIED') {
      hour = withMetric.find((h) => h.status === 'GUIDANCE_SATISFIED') || withMetric[0];
    } else if (day && day.state === 'NOT_EVALUABLE') {
      hour = withMetric.find((h) => cond(h).verdict === 'UNKNOWN') || withMetric[0];
    } else {
      hour = withMetric.find((h) => cond(h).verdict === 'FAIL') || withMetric[0];
    }
    return cond(hour);
  }
  function condRows(opp, dayIdx, detDay) {
    const day = (opp.days || [])[dayIdx];
    if (!day) return '';
    return (day.conditions || []).map((c) => {
      const rep = representativeCondition(detDay, c.metric, day);
      const cls = rep ? verdictClass(rep.verdict)
        : (c.day_verdict === 'PASS' ? 'v-pass' : c.day_verdict === 'FAIL' ? 'v-fail' : 'v-unk');
      const val = rep ? fmtValue(rep) : t().v_no_data;
      const th = rep ? fmtThreshold(rep) : t().v_no_data;
      const mark = cls === 'v-pass' ? '✓' : cls === 'v-fail' ? '✗' : '?';
      return `<tr><td class="mono">${esc(metricName(c.metric))}</td><td>${esc(th)}</td>` +
        `<td class="${cls} mono">${esc(val)} · ${mark}</td></tr>`;
    }).join('');
  }
  function condTable(opp, dayIdx) {
    const place = currentPlace();
    const day = (opp.days || [])[dayIdx];
    const det = place ? detailCache.get(place.place_id) : null;
    const detOpp = det ? (det.opportunities || []).find((x) => x.opportunity_id === opp.opportunity_id) : null;
    const detDay = detOpp && day ? (detOpp.days || []).find((d) => d.local_date === day.local_date) : null;
    const dateLabel = day ? day.local_date : '';
    if (!det) return `<p class="eval-muted">${esc(t().cond_loading)}</p>`;
    const rows = condRows(opp, dayIdx, detDay);
    const note = day && day.state === 'NOT_EVALUABLE'
      ? `<p class="unk-note">— ${esc(unkReason(day))}${esc(t().unk_note)}</p>` : '';
    return `<table class="cond-table">` +
      `<thead><tr><th>${esc(t().th_metric)}</th><th>${esc(t().threshold)}</th>` +
      `<th>${esc(t().today_v)} · ${esc(dateLabel)}</th></tr></thead>` +
      `<tbody>${rows}</tbody></table>${note}`;
  }

  function currentPlace() {
    if (!bundle) return null;
    return bundle.places.find((p) => p.place_id === pid) || null;
  }
  function placeDates(p) {
    const opp = (p.opportunities || [])[0];
    return opp ? (opp.days || []).map((d) => d.local_date) : [];
  }

  function fillRegion() {
    const sel = $('region-select');
    sel.innerHTML = [['tw', 'r_tw'], ['jp', 'r_jp'], ['us', 'r_us']]
      .map(([v, k]) => `<option value="${v}">${esc(t()[k])}</option>`).join('');
    const p = currentPlace();
    sel.value = p ? p.place_id.split('-')[0] : 'tw';
  }
  function fillPlaces() {
    const rg = $('region-select').value;
    const q = searchQ.trim().toLowerCase();
    const places = (bundle ? bundle.places : [])
      .filter((p) => p.place_id.startsWith(rg + '-'))
      .filter((p) => !q || (localizedName(p.name_i18n).toLowerCase().includes(q) || p.place_id.toLowerCase().includes(q)));
    if (!places.some((p) => p.place_id === pid) && places.length) pid = places[0].place_id;
    $('place-select').innerHTML = places.map((p) =>
      `<option value="${esc(p.place_id)}"${p.place_id === pid ? ' selected' : ''}>${esc(localizedName(p.name_i18n))}</option>`
    ).join('');
    $('place-select').value = pid || '';
    return places;
  }

  function renderDates() {
    const row = $('date-row');
    const p = currentPlace();
    if (!p) { row.innerHTML = ''; return; }
    const dates = placeDates(p);
    const opps = p.opportunities || [];
    row.innerHTML = dates.map((d, i) => {
      const ok = opps.filter((o) => ((o.days || [])[i] || {}).state === 'GUIDANCE_SATISFIED').length;
      return `<button class="date-pill${i === daySel ? ' sel' : ''}" data-day="${i}">` +
        `<span class="l1">${esc(d.slice(5))}${i === 0 ? ' ' + esc(t().today) : ''}</span>` +
        `<span class="l2">✓ ${ok}/${opps.length}</span></button>`;
    }).join('');
    const selEl = row.children[daySel];
    if (selEl && selEl.scrollIntoView) selEl.scrollIntoView({ inline: 'center', block: 'nearest' });
  }

  function renderOverview() {
    const p = currentPlace();
    const ov = $('overview');
    if (!p) {
      ov.innerHTML = `<p class="eval-muted">${esc(t().no_data)}</p>`;
      return;
    }
    const opps = p.opportunities || [];
    const states = opps.map((o) => ((o.days || [])[daySel] || {}).state);
    const nOk = states.filter((s) => s === 'GUIDANCE_SATISFIED').length;
    const nNo = states.filter((s) => s === 'UNFAVORABLE').length;
    const nUnk = states.filter((s) => s === 'NOT_EVALUABLE').length;
    const dates = placeDates(p);
    $('eval-meta').textContent = `${localizedName(p.name_i18n)} · ${dates[daySel] ? dates[daySel].slice(5) : ''}${daySel === 0 ? ' ' + t().today : ''} · ${opps.length} ${subjectCountLabel(opps.length, lang)}`;
    let html = `<div class="box overview-panel"><div class="sum-tabs">` +
      `<button class="tab t-rec${filter === 'ok' ? ' sel' : ''}" data-f="ok">${esc(t().tab_ok)} <span class="n">${nOk}</span></button>` +
      `<button class="tab t-no${filter === 'no' ? ' sel' : ''}" data-f="no">${esc(t().tab_no)} <span class="n">${nNo}</span></button>` +
      `<button class="tab t-unk${filter === 'unk' ? ' sel' : ''}" data-f="unk">${esc(t().tab_unk)} <span class="n">${nUnk}</span></button>` +
      `<button class="tab${filter === 'all' ? ' sel' : ''}" data-f="all">${esc(t().tab_all)} <span class="n">${opps.length}</span></button>` +
      `</div>`;
    opps.forEach((o) => {
      const info = dayCellInfo(o, daySel);
      if (filter !== 'all' && info.cls !== filter) return;
      const key = `${p.place_id}|${o.opportunity_id}`;
      const open = openRows.has(key);
      const days = (o.days || []).map((d, i) => {
        const di = dayCellInfo(o, i);
        return `<button class="mday ${di.cls}${i === daySel ? ' cur' : ''}" data-day="${i}" data-opp="${esc(o.opportunity_id)}" title="${esc(d.local_date)}">` +
          `<span class="md-d">${esc(d.local_date.slice(5))}</span><span class="md-f">${esc(di.text)}</span></button>`;
      }).join('');
      html += `<div class="g-row${info.cls === 'ok' ? ' sel' : ''}${open ? ' open' : ''}" data-g="${esc(o.opportunity_id)}">` +
        `<div class="g-head" data-head="${esc(o.opportunity_id)}">` +
        `<span class="g-name" title="${esc(genreName(o.genre_template))}">${esc(genreShort(o.genre_template))}</span>` +
        `<span class="grow"><span class="g-day">${esc(info.text)}</span></span>` +
        `<span class="mini-days">${days}</span></div>` +
        `<div class="g-body">${open ? condTable(o, daySel) : ''}</div></div>`;
    });
    ov.innerHTML = html + '</div>';
  }

  function render() {
    if (!bundle) return;
    fillRegion();
    fillPlaces();
    renderDates();
    renderOverview();
    $('eval-loading').style.display = 'none';
  }

  async function loadDetail(placeId) {
    if (detailCache.has(placeId)) return detailCache.get(placeId);
    const res = await fetch(`${DETAILS_BASE}${placeId}.json`, { cache: 'no-cache' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    detailCache.set(placeId, json);
    return json;
  }

  function rebind() {
    $('date-row').onclick = (e) => {
      const b = e.target.closest('[data-day]');
      if (!b) return;
      daySel = +b.dataset.day;
      renderDates();
      renderOverview();
    };
    $('overview').onclick = async (e) => {
      const mday = e.target.closest('.mday');
      if (mday) {
        daySel = +mday.dataset.day;
        renderDates();
        renderOverview();
        return;
      }
      const tab = e.target.closest('.sum-tabs [data-f]');
      if (tab) {
        filter = tab.dataset.f;
        renderOverview();
        return;
      }
      const head = e.target.closest('.g-head');
      if (!head) return;
      const oppId = head.dataset.head;
      const key = `${pid}|${oppId}`;
      if (openRows.has(key)) openRows.delete(key);
      else {
        openRows.add(key);
        if (!detailCache.has(pid)) {
          try { await loadDetail(pid); } catch { /* cond table falls back honestly */ }
        }
      }
      renderOverview();
    };
  }

  function bindEvents() {
    $('region-select').addEventListener('change', () => {
      pid = null;
      fillPlaces();
      openRows.clear();
      renderDates();
      renderOverview();
    });
    $('place-select').addEventListener('change', (e) => {
      pid = e.target.value;
      openRows.clear();
      renderDates();
      renderOverview();
    });
    $('eval-search').addEventListener('input', (e) => {
      searchQ = e.target.value;
      fillPlaces();
      openRows.clear();
      renderDates();
      renderOverview();
    });
    $('lang-select').addEventListener('change', (e) => {
      lang = e.target.value; localStorage.setItem('chaselights_lang', lang);
      applyStaticTexts(); render();
    });
  }

  function applyStaticTexts() {
    document.documentElement.lang = lang;
    $('page-title').textContent = t().title;
    document.title = `ChaseLights — ${t().title}`;
    $('eval-search').placeholder = t().search;
    $('eval-loading').textContent = t().loading;
    // CL-UI-28: the shared site-nav labels follow the page language.
    document.querySelectorAll('.site-nav [data-i18n]').forEach((el) => { const k = el.dataset.i18n; if (t()[k]) el.textContent = t()[k]; });
    if (bundle) {
      // CL-UI-19: the evaluation timestamp is displayed in the page-header
      // GMT+8 convention — the UTC value is converted for display only and the
      // underlying data stays untouched.
      const generated = new Date(bundle.generated_at);
      const stamp = isNaN(generated)
        ? String(bundle.generated_at).replace('T', ' ').replace('Z', ' UTC')
        : new Date(generated.getTime() + 8 * 3600 * 1000).toISOString().slice(0, 19).replace('T', ' ') + ' GMT+8';
      $('update-time').textContent = `${t().updated}: ${stamp}`;
    }
    $('lang-select').value = lang;
  }

  async function init() {
    applyStaticTexts();
    bindEvents();
    rebind();
    try {
      const res = await fetch(BUNDLE_URL, { cache: 'no-cache' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      bundle = await res.json();
    } catch (e) {
      $('eval-loading').textContent = `⚠️ ${t().load_error} (${e.message})`;
      return;
    }
    const rg = $('region-select').value;
    const first = bundle.places.find((p) => p.place_id.startsWith(rg + '-'));
    pid = first ? first.place_id : (bundle.places[0] ? bundle.places[0].place_id : null);
    applyStaticTexts();
    render();
  }

  // Test/export hook: allow Node (node --test) to import the pure helpers
  // without booting the DOM-driven UI.
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { subjectCountLabel };
  }
  if (typeof document !== 'undefined') init();

  // Test/DOM-optional exposure for the CI label-contract assertions
  // (apps/web-v2/tests/genre-eval-value-labels.test.mjs) and the CL-UI-93
  // day-cell contract (cl-ui-93-genre-eval-mockup.test.mjs).
  if (typeof window !== 'undefined') {
    window.__genreEval = {
      fmtValue, fmtValueThreshold, fmtThreshold, verdictClass,
      collapseHours, dominantFailWord, unkReason, dayCellInfo, representativeCondition,
      setLang(l) { if (I18N[l]) lang = l; }
    };
  }
})();
