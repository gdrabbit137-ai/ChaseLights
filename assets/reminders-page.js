/* CL-UI-58: reminders page (reminders.html) — list / toggle / delete / quick-add
   for notify_rules. Follows the genre-eval.js page pattern: self-contained
   trilingual dict, own lang select, loads the shared reminders-client.js for
   the API contract and toasts.

   Catalog source (既有 browse/目錄資料): apps/web-v2/evaluations-latest.json —
   places[{place_id, name_i18n, opportunities[{opportunity_id, name_i18n}]}].
   The region is derived from the place_id prefix (tw/jp/us/ak/hi), the same
   regions the homepage VALID_REGIONS uses. No data-layer files are touched.

   Backend contract (CL-API-03 + CL-UI-58 PATCH; CL-UI-61: the real worker
   route is /notify/rules under the /api/v1 base — /notify_rules was a 404):
   - GET    /api/v1/notify/rules      -> { rules:[{id, place_id, opportunity_id, channel, min_advance_hours, enabled}] } (JWT only; 401 = not signed in)
   - POST   /api/v1/notify/rules      { placeId, opportunityId, channel:'push', minAdvanceHours:24 }
   - PATCH  /api/v1/notify/rules/<id> { enabled: boolean }
   - DELETE /api/v1/notify/rules/<id>
*/
(function () {
  'use strict';

  var RULES_ENDPOINT = '/api/v1/notify/rules';
  var DEFAULTS_ENDPOINT = '/api/v1/notify/defaults';
  var ME_ENDPOINT = '/api/v1/auth/me';
  var CATALOG_URL = './apps/web-v2/evaluations-latest.json';
  var REGIONS = [
    { id: 'tw', flag: '🇹🇼', name: { 'zh-TW': '台灣', en: 'Taiwan', ja: '台湾' } },
    { id: 'jp', flag: '🇯🇵', name: { 'zh-TW': '日本', en: 'Japan', ja: '日本' } },
    { id: 'us', flag: '🇺🇸', name: { 'zh-TW': '美國', en: 'US', ja: 'アメリカ' } },
    { id: 'ak', flag: '🇺🇸', name: { 'zh-TW': '阿拉斯加', en: 'Alaska', ja: 'アラスカ' } },
    { id: 'hi', flag: '🇺🇸', name: { 'zh-TW': '夏威夷', en: 'Hawaii', ja: 'ハワイ' } }
  ];

  var I18N = {
    'zh-TW': {
      page_title: '我的', nav_cards: '卡片', nav_weathermap: '天氣圖', nav_my: '我的', my_rem_tab: '我的提醒', my_subj_tab: '我的題材',
      rem_list_title: '我的提醒',
      rem_add_title: '＋ 新增提醒',
      rem_add_btn: '加入提醒',
      rem_added_btn: '已加入 ✓',
      rem_search_placeholder: '搜尋景點名稱或題材名稱…',
      rem_region_label: '地區', rem_place_label: '景點', rem_subject_label: '題材',
      rem_col_channel: 'App 推播', rem_col_advance: '提前 {n} 小時',
      rem_enabled: '啟用', rem_disabled: '停用',
      rem_delete: '刪除',
      rem_login_prompt: '登入後即可管理你的拍攝提醒（條件符合時透過 APP 推播通知）。',
      rem_login_line: '使用 LINE 登入', rem_login_google: '使用 Google 登入',
      rem_empty: '還沒有提醒。選地區 → 景點 → 題材建立第一個拍攝提醒。',
      rem_loading: '正在載入提醒…',
      rem_saved: '已加入提醒，條件符合時將透過 APP 推播通知。',
      rem_removed: '已移除提醒。',
      rem_err: '提醒暫時無法同步，請稍後再試。',
      rem_limit: '提醒數量已達方案上限，請先移除部分提醒。',
      rem_any_subject: '該景點全部題材',
      rem_no_match: '沒有符合的景點或題材。',
      rem_next_label: '下次觸發', rem_paused_next: '暫停中',
      rem_streak: '連續 {n} 日未符',
      rem_next_estimate: '依目前評估推估', rem_no_window: '近期無符合時段',
      rem_preview_first: '首次觸發', rem_preview_unknown: '待評估',
      rem_found: '找到 {n} 個景點',
      rem_empty_t: '還沒有提醒', rem_empty_d: '選地區 → 景點 → 題材建立第一個拍攝提醒，條件符合時會透過 APP 推播通知你。',
      rem_empty_a: '建立提醒', rem_edit: '編輯',
      rem_active_count: '{total} 個提醒 · {active} 個啟用中',
      rem_flow_hint: '選地區 → 景點 → 題材，或直接搜尋景點名；符合時段前會透過 APP 推播通知。',
      rem_custom_opt: '自訂條件…',
      rem_cc_chip: '自訂條件',
      rem_custom_next: '符合自訂條件時推播',
      rem_custom_preview: '條件符合時推播',
      rem_cc_panel_title: '自訂條件（全部符合才推播；預設值寬鬆，可只調整你在意的項目）',
      rem_cc_low: '低雲門檻（%）', rem_cc_mid: '中雲門檻（%）', rem_cc_high: '高雲門檻（%）',
      rem_cc_precip: '降水上限（mm/h）', rem_cc_vis: '能見度下限（km）',
      rem_cc_wind: '風速上限（m/s）', rem_cc_window: '時間窗', rem_cc_lead: '提前量（分鐘）',
      rem_cc_hint_low: '低空雲量低於此值才推播；100 代表不限',
      rem_cc_hint_mid: '中空雲量影響中景清晰度',
      rem_cc_hint_high: '高空雲量影響星空與長曝',
      rem_cc_hint_precip: '每小時雨量不超過此值，避免淋雨拍攝',
      rem_cc_hint_vis: '能見度至少要有這麼遠，避免起霧看不清',
      rem_cc_hint_wind: '風速不超過此值，腳架與長曝較穩',
      rem_cc_hint_window: '只在這個時段推播，起訖可跨午夜',
      rem_cc_hint_lead: '條件成立前這麼多分鐘通知你出發',
      rem_col_advance_min: '提前 {n} 分',
      rem_cc_invalid: '自訂條件數值超出範圍，請再檢查。',
      // CL-UX-01 Part B: 預設提醒規則＋單點覆寫（新鍵，既有鍵不動）
      rem_def_title: '預設提醒規則',
      rem_def_intro: '新提醒沿用這裡的設定；下方每一張提醒卡都可以個別覆寫。',
      rem_def_freq: '發送頻率',
      rem_def_mode_every: '每隔 N 天',
      rem_def_mode_weekdays: '指定每星期幾',
      rem_def_days: '星期',
      rem_def_send_time: '發送時間',
      rem_def_lead: '預報展望天數',
      rem_def_lead_opt: '{n} 天',
      rem_def_modify: '修改預設',
      rem_def_target: '目標出景日',
      rem_def_target_any: '不限星期',
      rem_def_target_only: '只篩選',
      rem_def_tier: '達標門檻',
      rem_def_tier_recommend: '僅✓推薦',
      rem_def_tier_shootable: '包含○可拍',
      rem_def_save: '儲存',
      rem_def_saved: '已儲存預設提醒規則。',
      rem_def_err: '預設規則暫時無法儲存，請稍後再試。',
      rem_def_loading: '正在載入預設規則…',
      rem_def_inherited: '（預設）',
      rem_def_every_n: '每 {n} 天',
      rem_def_weekly: '每週{d}',
      rem_def_lookahead: '看未來 {n} 天',
      rem_def_target_days: '只看週{d}',
      rem_def_no_days: '未選星期',
      rem_edit_rule: '修改此點規則',
      rem_def_save_rule: '儲存此點規則',
      rem_def_reset: '恢復預設',
      rem_def_rule_saved: '已更新此點規則。',
      rem_def_rule_reset: '已恢復沿用預設規則。'
    },
    'en': {
      page_title: 'My Library', nav_cards: 'Cards', nav_weathermap: 'Weather map', nav_my: 'My Library', my_rem_tab: 'My reminders', my_subj_tab: 'My subjects',
      rem_list_title: 'My reminders',
      rem_add_title: '＋ New reminder',
      rem_add_btn: 'Add reminder',
      rem_added_btn: 'Added ✓',
      rem_search_placeholder: 'Search place or subject names…',
      rem_region_label: 'Region', rem_place_label: 'Place', rem_subject_label: 'Subject',
      rem_col_channel: 'App push', rem_col_advance: '{n} h in advance',
      rem_enabled: 'Enabled', rem_disabled: 'Paused',
      rem_delete: 'Delete',
      rem_login_prompt: 'Sign in to manage your shooting reminders (notified via app push when conditions qualify).',
      rem_login_line: 'Sign in with LINE', rem_login_google: 'Sign in with Google',
      rem_empty: 'No reminders yet. Pick region → place → subject to create your first reminder.',
      rem_loading: 'Loading reminders…',
      rem_saved: 'Reminder added — you will be notified via app push when conditions qualify.',
      rem_removed: 'Reminder removed.',
      rem_err: 'Reminders could not be synced right now; please try again later.',
      rem_limit: 'Reminder limit reached for your plan — remove some reminders first.',
      rem_any_subject: 'All subjects at this place',
      rem_no_match: 'No matching places or subjects.',
      rem_next_label: 'Next trigger', rem_paused_next: 'Paused',
      rem_streak: '{n} days unfit in a row',
      rem_next_estimate: 'estimated from the current evaluation', rem_no_window: 'No fitting window soon',
      rem_preview_first: 'First trigger', rem_preview_unknown: 'Pending evaluation',
      rem_found: 'Found {n} places',
      rem_empty_t: 'No reminders yet', rem_empty_d: 'Pick region → place → subject to create your first reminder — we notify via app push when conditions qualify.',
      rem_empty_a: 'Create reminder', rem_edit: 'Edit',
      rem_active_count: '{total} reminders · {active} active',
      rem_flow_hint: 'Pick region → place → subject, or search directly; we notify via app push when conditions qualify.',
      rem_custom_opt: 'Custom conditions…',
      rem_cc_chip: 'Custom conditions',
      rem_custom_next: 'Notifies when your custom conditions are met',
      rem_custom_preview: 'Notifies when conditions are met',
      rem_cc_panel_title: 'Custom conditions (all must hold to notify; defaults are lenient — tune only what you care about)',
      rem_cc_low: 'Low cloud cap (%)', rem_cc_mid: 'Mid cloud cap (%)', rem_cc_high: 'High cloud cap (%)',
      rem_cc_precip: 'Precipitation cap (mm/h)', rem_cc_vis: 'Visibility floor (km)',
      rem_cc_wind: 'Wind cap (m/s)', rem_cc_window: 'Time window', rem_cc_lead: 'Lead time (minutes)',
      rem_cc_hint_low: 'Notify only below this low-cloud value; 100 = no limit',
      rem_cc_hint_mid: 'Mid-level cloud affects midground clarity',
      rem_cc_hint_high: 'High cloud affects stars and long exposures',
      rem_cc_hint_precip: 'Hourly rain stays under this value',
      rem_cc_hint_vis: 'Visibility must reach at least this far (fog guard)',
      rem_cc_hint_wind: 'Wind stays under this value — steadier tripod shots',
      rem_cc_hint_window: 'Only notifies inside this window; it may cross midnight',
      rem_cc_hint_lead: 'You are notified this many minutes before conditions are met',
      rem_col_advance_min: '{n} min in advance',
      rem_cc_invalid: 'Some custom-condition values are out of range — please check.',
      // CL-UX-01 Part B: default reminder rule + per-rule override
      rem_def_title: 'Default reminder rule',
      rem_def_intro: 'New reminders inherit these settings; any card below can override them.',
      rem_def_freq: 'Frequency',
      rem_def_mode_every: 'Every N days',
      rem_def_mode_weekdays: 'On chosen weekdays',
      rem_def_days: 'Weekdays',
      rem_def_send_time: 'Send time',
      rem_def_lead: 'Forecast look-ahead',
      rem_def_lead_opt: '{n}d',
      rem_def_modify: 'Modify default',
      rem_def_target: 'Target shooting day',
      rem_def_target_any: 'Any weekday',
      rem_def_target_only: 'Filter only',
      rem_def_tier: 'Qualifying tier',
      rem_def_tier_recommend: '✓ Recommended only',
      rem_def_tier_shootable: 'Include ○ Shootable',
      rem_def_save: 'Save',
      rem_def_saved: 'Default reminder rule saved.',
      rem_def_err: 'The default rule could not be saved; please try again later.',
      rem_def_loading: 'Loading the default rule…',
      rem_def_inherited: '(default)',
      rem_def_every_n: 'Every {n} days',
      rem_def_weekly: 'Every {d}',
      rem_def_lookahead: 'Looking {n} days ahead',
      rem_def_target_days: 'Only {d}',
      rem_def_no_days: 'No weekday chosen',
      rem_edit_rule: 'Edit this rule',
      rem_def_save_rule: 'Save this rule',
      rem_def_reset: 'Reset to default',
      rem_def_rule_saved: 'This rule was updated.',
      rem_def_rule_reset: 'This rule follows the default again.'
    },
    'ja': {
      page_title: 'マイライブラリ', nav_cards: 'カード', nav_weathermap: '天気マップ', nav_my: 'マイライブラリ', my_rem_tab: 'マイリマインダー', my_subj_tab: 'マイ題材',
      rem_list_title: 'リマインダー一覧',
      rem_add_title: '＋ リマインド追加',
      rem_add_btn: 'リマインドに追加',
      rem_added_btn: '追加済み ✓',
      rem_search_placeholder: 'スポット名や題材名を検索…',
      rem_region_label: '地域', rem_place_label: 'スポット', rem_subject_label: '題材',
      rem_col_channel: 'アプリ通知', rem_col_advance: '{n} 時間前に通知',
      rem_enabled: '有効', rem_disabled: '停止',
      rem_delete: '削除',
      rem_login_prompt: 'ログインすると撮影リマインダーを管理できます（条件が揃うとアプリのプッシュ通知でお知らせします）。',
      rem_login_line: 'LINE でログイン', rem_login_google: 'Google でログイン',
      rem_empty: 'リマインダーはまだありません。地域 → スポット → 題材を選んで最初の1件を作成してください。',
      rem_loading: 'リマインダーを読み込み中…',
      rem_saved: 'リマインダーを追加しました。条件が揃うとアプリのプッシュ通知でお知らせします。',
      rem_removed: 'リマインダーを削除しました。',
      rem_err: 'リマインダーを同期できませんでした。しばらくしてから再試行してください。',
      rem_limit: 'リマインダー数がプランの上限に達しました。先に一部を削除してください。',
      rem_any_subject: 'このスポットの全題材',
      rem_no_match: '該当するスポットや題材がありません。',
      rem_next_label: '次回発火', rem_paused_next: '停止中',
      rem_streak: '{n} 日連続で不適合',
      rem_next_estimate: '現在の評価からの推定', rem_no_window: '近くに適合する時間帯なし',
      rem_preview_first: '初回発火', rem_preview_unknown: '評価待ち',
      rem_found: '{n} 件見つかりました',
      rem_empty_t: 'リマインドはまだありません', rem_empty_d: '地域 → スポット → 題材を選んで最初のリマインドを作成。条件が揃うとアプリのプッシュ通知でお知らせします。',
      rem_empty_a: 'リマインド作成', rem_edit: '編集',
      rem_active_count: 'リマインド {total} 件・有効 {active} 件',
      rem_flow_hint: '地域 → スポット → 題材を選ぶか、直接検索。条件が揃うとアプリのプッシュ通知でお知らせします。',
      rem_custom_opt: 'カスタム条件…',
      rem_cc_chip: 'カスタム条件',
      rem_custom_next: 'カスタム条件成立時に通知',
      rem_custom_preview: '条件成立時に通知',
      rem_cc_panel_title: 'カスタム条件（すべて成立時のみ通知。初期値は緩め — 気になる項目だけ調整してください）',
      rem_cc_low: '低雲しきい値（%）', rem_cc_mid: '中雲しきい値（%）', rem_cc_high: '高雲しきい値（%）',
      rem_cc_precip: '降水上限（mm/h）', rem_cc_vis: '視程下限（km）',
      rem_cc_wind: '風速上限（m/s）', rem_cc_window: '時間帯', rem_cc_lead: '通知の余裕（分）',
      rem_cc_hint_low: '低雲がこの値未満のときだけ通知。100 は無制限',
      rem_cc_hint_mid: '中雲は中景の明瞭さに影響します',
      rem_cc_hint_high: '高雲は星空や長時間露光に影響します',
      rem_cc_hint_precip: '1時間の雨量がこの値を超えない場合に通知',
      rem_cc_hint_vis: '視程がこの距離以上必要（霧対策）',
      rem_cc_hint_wind: '風速がこの値以下 — 三脚撮影が安定します',
      rem_cc_hint_window: 'この時間帯内のみ通知。開始終了は日跨み可',
      rem_cc_hint_lead: '条件成立のこの分数前に通知します',
      rem_col_advance_min: '{n} 分前に通知',
      rem_cc_invalid: 'カスタム条件の値が範囲外です。確認してください。',
      // CL-UX-01 Part B: 既定リマインダールール＋個別上書き
      rem_def_title: '既定のリマインダールール',
      rem_def_intro: '新しいリマインダーはこの設定を引き継ぎます。下の各カードで個別に上書きできます。',
      rem_def_freq: '通知の頻度',
      rem_def_mode_every: 'N 日ごと',
      rem_def_mode_weekdays: '曜日を指定',
      rem_def_days: '曜日',
      rem_def_send_time: '通知時刻',
      rem_def_lead: '予報の見通し日数',
      rem_def_lead_opt: '{n}日',
      rem_def_modify: '既定を変更',
      rem_def_target: '狙う撮影日',
      rem_def_target_any: '曜日の指定なし',
      rem_def_target_only: '絞り込む',
      rem_def_tier: '成立ライン',
      rem_def_tier_recommend: '✓おすすめのみ',
      rem_def_tier_shootable: '○撮影可も含む',
      rem_def_save: '保存',
      rem_def_saved: '既定のリマインダールールを保存しました。',
      rem_def_err: '既定ルールを保存できませんでした。しばらくしてから再試行してください。',
      rem_def_loading: '既定ルールを読み込み中…',
      rem_def_inherited: '（既定）',
      rem_def_every_n: '{n} 日ごと',
      rem_def_weekly: '毎週{d}',
      rem_def_lookahead: '今後 {n} 日先まで',
      rem_def_target_days: '{d}のみ',
      rem_def_no_days: '曜日未選択',
      rem_edit_rule: 'このルールを変更',
      rem_def_save_rule: 'このルールを保存',
      rem_def_reset: '既定に戻す',
      rem_def_rule_saved: 'このルールを更新しました。',
      rem_def_rule_reset: '既定ルールを引き継ぐ設定に戻しました。'
    }
  };

  var state = { lang: 'zh-TW', catalog: [], rules: [], signedIn: null, defaults: null };

  function lang() {
    var sel = document.getElementById('lang-select');
    var v = (sel && typeof sel.value === 'string' && sel.value) ||
            (function () { try { return localStorage.getItem('chaselights_lang'); } catch (e) { return null; } }()) || 'zh-TW';
    return I18N[v] ? v : 'zh-TW';
  }
  function t(key) { var p = I18N[state.lang]; return (p && p[key]) || I18N['zh-TW'][key] || ''; }

  // Pure helpers (unit-tested via source extraction).
  function regionOfPlace(placeId) { return String(placeId || '').split('-')[0]; }
  function regionName(regionId, lg) {
    for (var i = 0; i < REGIONS.length; i++) if (REGIONS[i].id === regionId) return REGIONS[i].flag + ' ' + nameOf(REGIONS[i].name, lg);
    return regionId;
  }
  function nameOf(i18n, lg) {
    if (!i18n) return '';
    return i18n[lg] || i18n['zh-TW'] || i18n.en || '';
  }
  // Keyword filter over place + subject names (search-in-page contract).
  function filterCatalog(catalog, keyword, lg) {
    var kw = String(keyword || '').trim().toLocaleLowerCase();
    var out = [];
    (catalog || []).forEach(function (p) {
      var placeName = nameOf(p.name_i18n, lg);
      var opps = (p.opportunities || []).filter(function (o) {
        if (!kw) return true;
        return (placeName + ' ' + nameOf(o.name_i18n, lg) + ' ' + (o.opportunity_id || '')).toLocaleLowerCase().indexOf(kw) >= 0;
      });
      if (!kw || opps.length || placeName.toLocaleLowerCase().indexOf(kw) >= 0) {
        out.push({ place: p, opportunities: opps });
      }
    });
    return out;
  }
  function findPlace(catalog, placeId) {
    for (var i = 0; i < (catalog || []).length; i++) if (catalog[i].place_id === placeId) return catalog[i];
    return null;
  }
  function findSubject(place, oppId) {
    if (!place) return null;
    var opps = place.opportunities || [];
    for (var i = 0; i < opps.length; i++) if (opps[i].opportunity_id === oppId) return opps[i];
    return null;
  }

  // ---- CL-UI-99: custom-conditions mode (subject mode stays untouched) ----
  // The third picker layer offers 自訂條件… which opens a five-parameter form;
  // defaults are lenient so only the parameters the user actually tunes bite.
  var CC_CUSTOM_ID = '__custom__';
  var CC_DEFAULTS = {
    cloud_low_max: 100, cloud_mid_max: 100, cloud_high_max: 100,
    precip_max_mmh: 5, visibility_min_km: 0, wind_max_ms: 20,
    window_start: '00:00', window_end: '23:59', lead_minutes: 60
  };
  var CC_INPUT_IDS = {
    cloud_low_max: 'rem-cc-low', cloud_mid_max: 'rem-cc-mid', cloud_high_max: 'rem-cc-high',
    precip_max_mmh: 'rem-cc-precip', visibility_min_km: 'rem-cc-vis', wind_max_ms: 'rem-cc-wind',
    lead_minutes: 'rem-cc-lead'
  };
  var CC_RANGES = {
    cloud_low_max: [0, 100], cloud_mid_max: [0, 100], cloud_high_max: [0, 100],
    precip_max_mmh: [0, 200], visibility_min_km: [0, 50], wind_max_ms: [0, 75]
  };
  var CC_HM_RE = /^([01]\d|2[0-3]):[0-5]\d$/;
  // Summary prefixes per language; thresholds/units are language-neutral.
  var CC_SUMMARY_WORDS = {
    'zh-TW': { low: '低雲', mid: '中雲', high: '高雲', precip: '雨', vis: '能見度', wind: '風' },
    'en': { low: 'low cloud', mid: 'mid cloud', high: 'high cloud', precip: 'rain', vis: 'vis', wind: 'wind' },
    'ja': { low: '低雲', mid: '中雲', high: '高雲', precip: '雨', vis: '視界', wind: '風' }
  };
  // Sanitized payload from the form; null = some value out of range.
  function collectCustomConditions() {
    var out = {};
    for (var k in CC_INPUT_IDS) {
      var el = document.getElementById(CC_INPUT_IDS[k]);
      if (!el) return null;
      var raw = String(el.value == null ? '' : el.value).trim();
      if (!raw) return null; // every field is prefilled — an empty one is a mistake
      var n = Number(raw);
      if (k === 'lead_minutes') {
        if (!Number.isInteger(n) || n < 0 || n > 4320) return null;
        out[k] = n;
      } else {
        var range = CC_RANGES[k];
        if (!Number.isFinite(n) || n < range[0] || n > range[1]) return null;
        out[k] = n;
      }
    }
    var s = document.getElementById('rem-cc-start');
    var e = document.getElementById('rem-cc-end');
    if (!s || !e) return null;
    if (!CC_HM_RE.test(s.value) || !CC_HM_RE.test(e.value)) return null;
    out.window_start = s.value;
    out.window_end = e.value;
    return out;
  }
  // Pure card-summary builder (unit-tested). Summary shows what the user
  // TUNED away from the lenient defaults (owner example: 「低雲≤20%・能見度≥10km・
  // 05:00–07:00」); unconstrained bounds (cloud 100, precip 200, vis 0, wind 75,
  // full-day window) and default values are suppressed. Custom-engine semantics
  // (worker customHourMatches) treat cloud 100 / vis 0 / bounds as no-constraint.
  function customSummary(cc, lg) {
    var words = CC_SUMMARY_WORDS[lg] || CC_SUMMARY_WORDS['zh-TW'];
    var parts = [];
    function num(v) { var n = Number(v); return (v != null && Number.isFinite(n)) ? n : null; }
    var low = num(cc && cc.cloud_low_max), mid = num(cc && cc.cloud_mid_max), high = num(cc && cc.cloud_high_max);
    var precip = num(cc && cc.precip_max_mmh), vis = num(cc && cc.visibility_min_km), wind = num(cc && cc.wind_max_ms);
    if (low != null && low < 100) parts.push(words.low + '≤' + trimNum(low) + '%');
    if (mid != null && mid < 100) parts.push(words.mid + '≤' + trimNum(mid) + '%');
    if (high != null && high < 100) parts.push(words.high + '≤' + trimNum(high) + '%');
    if (precip != null && precip < 200 && precip !== CC_DEFAULTS.precip_max_mmh) parts.push(words.precip + '≤' + trimNum(precip) + 'mm/h');
    if (vis != null && vis > 0) parts.push(words.vis + '≥' + trimNum(vis) + 'km');
    if (wind != null && wind < 75 && wind !== CC_DEFAULTS.wind_max_ms) parts.push(words.wind + '≤' + trimNum(wind) + 'm/s');
    var ws = cc && typeof cc.window_start === 'string' ? cc.window_start : null;
    var we = cc && typeof cc.window_end === 'string' ? cc.window_end : null;
    if (ws && we && CC_HM_RE.test(ws) && CC_HM_RE.test(we) && !(ws === CC_DEFAULTS.window_start && we === CC_DEFAULTS.window_end)) {
      parts.push(ws + '–' + we);
    }
    return parts.join('・');
  }
  function trimNum(n) { return String(Math.round(n * 100) / 100); }

  // ---- CL-UX-01 Part B: default schedule + per-rule override ----
  // One control group (the data-f contract in reminders.html and in the card
  // panels built by scheduleControlsHtml) is read back by readSchedule and
  // written by writeSchedule, so the defaults panel and every rule's inline
  // panel share exactly one implementation.
  //
  // Contract: schedule_weekdays / target_weekdays are CSV of 0..6 (0=Sunday),
  // send_time is 'HH:MM' in the USER's timezone, so every write carries
  // tz = Intl.DateTimeFormat().resolvedOptions().timeZone. null on a rule
  // means "inherit the user default" (and null in a defaults PUT means
  // "unset" — the backend falls back to its built-in schedule).
  var SCHEDULE_FIELDS = ['schedule_mode', 'schedule_every_n', 'schedule_weekdays',
    'send_time', 'lead_days', 'target_weekdays', 'min_tier'];
  var WD_NAMES = {
    'zh-TW': ['日', '一', '二', '三', '四', '五', '六'],
    'en': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    'ja': ['日', '月', '火', '水', '木', '金', '土']
  };

  function browserTz() {
    try {
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      return tz || 'UTC';
    } catch (e) { return 'UTC'; }
  }
  function tIn(key, lg) { var p = I18N[lg] || I18N['zh-TW']; return p[key] || I18N['zh-TW'][key] || ''; }
  // CL-UX-01 Part B: the API's canonical values are 'every_n_days' | 'weekdays'
  // (workers/api/src/notify.js validateSchedule REJECTS anything else with 400).
  // Reads tolerate the short aliases; writes always emit the canonical spelling.
  function modeOf(v) {
    var s = String(v == null ? '' : v).toLowerCase();
    if (s === 'weekdays' || s === 'weekly' || s === 'days') return 'weekdays';
    if (s === 'every_n_days' || s === 'every_n' || s === 'every') return 'every_n_days';
    return 'every_n_days';
  }
  function csvDays(v) {
    var out = [];
    String(v == null ? '' : v).split(',').forEach(function (part) {
      var n = parseInt(String(part).trim(), 10);
      if (n >= 0 && n <= 6 && out.indexOf(n) < 0) out.push(n);
    });
    out.sort(function (a, b) { return a - b; });
    return out;
  }
  // Display order runs Monday → Sunday (owner wording: 「只看週六日」 reads
  // 六 then 日), while the payload CSV stays numeric-sorted 0..6. compact=true
  // drops the 、 separator — the owner's target-day wording 「只看週六日」.
  var WD_DISPLAY_ORDER = [1, 2, 3, 4, 5, 6, 0];
  function dayNames(days, lg, compact) {
    var names = WD_NAMES[lg] || WD_NAMES['zh-TW'];
    var ordered = (days || []).slice().sort(function (a, b) {
      return WD_DISPLAY_ORDER.indexOf(a) - WD_DISPLAY_ORDER.indexOf(b);
    });
    var sep = lg === 'en' ? ', ' : (compact ? '' : '、');
    return ordered.map(function (d) { return names[d]; }).join(sep);
  }
  function clampInt(v, lo, hi, fallback) {
    var n = parseInt(v, 10);
    if (!Number.isFinite(n) || n < lo || n > hi) return fallback;
    return n;
  }
  function blankDefaults() {
    return { schedule_mode: 'every_n_days', schedule_every_n: 3, schedule_weekdays: '', send_time: '20:00',
      lead_days: 3, target_weekdays: '', min_tier: 'recommend', channel: 'push', tz: browserTz() };
  }
  // Server payload -> the shape the controls expect (null = unset -> built-in).
  function mergeDefaults(d) {
    var out = blankDefaults();
    if (d && typeof d === 'object') {
      for (var i = 0; i < SCHEDULE_FIELDS.length; i++) {
        var k = SCHEDULE_FIELDS[i];
        if (d[k] !== null && d[k] !== undefined && String(d[k]).trim() !== '') out[k] = d[k];
      }
      if (d.channel) out.channel = d.channel;
      if (d.tz) out.tz = d.tz;
    }
    out.schedule_mode = modeOf(out.schedule_mode);
    out.schedule_every_n = clampInt(out.schedule_every_n, 1, 7, 3);
    out.lead_days = clampInt(out.lead_days, 1, 7, 3);
    out.send_time = CC_HM_RE.test(String(out.send_time)) ? String(out.send_time) : '20:00';
    out.schedule_weekdays = csvDays(out.schedule_weekdays).join(',');
    out.target_weekdays = csvDays(out.target_weekdays).join(',');
    out.min_tier = String(out.min_tier) === 'shootable' ? 'shootable' : 'recommend';
    return out;
  }
  function defOf() { return state.defaults || blankDefaults(); }

  function scNode(root, field) { return root ? root.querySelector('[data-f="' + field + '"]') : null; }
  function scNodes(root, field) { return root ? root.querySelectorAll('[data-f="' + field + '"]') : []; }
  function scRadio(root, field) {
    var el = root ? root.querySelector('[data-f="' + field + '"]:checked') : null;
    return el ? el.getAttribute('data-v') : '';
  }
  // CL-UX-02: look-ahead is a row of quick capsules (1/3/5/7) backed by a
  // hidden input so a non-preset value (2/4/6) still survives a round-trip.
  function readLead(root) {
    var els = scNodes(root, 'lead');
    for (var i = 0; i < els.length; i++) {
      if (els[i].type === 'radio' && els[i].checked) return els[i].value;
    }
    for (var j = 0; j < els.length; j++) {
      if (els[j].type !== 'radio') return els[j].value;
    }
    return null;
  }
  function writeLead(root, n) {
    var v = String(clampInt(n, 1, 7, 3));
    var els = scNodes(root, 'lead');
    for (var i = 0; i < els.length; i++) {
      if (els[i].type === 'radio') els[i].checked = els[i].value === v;
      else els[i].value = v;
    }
  }
  function applyLeadLabels(root) {
    if (!root) return;
    var els = root.querySelectorAll('[data-lead-t]');
    for (var i = 0; i < els.length; i++) {
      var n = els[i].getAttribute('data-lead-t');
      els[i].textContent = tIn('rem_def_lead_opt', state.lang).replace('{n}', n);
    }
  }
  function checkedDays(root, field) {
    var els = scNodes(root, field), out = [];
    for (var i = 0; i < els.length; i++) {
      if (!els[i].checked) continue;
      var n = parseInt(els[i].value, 10);
      if (n >= 0 && n <= 6 && out.indexOf(n) < 0) out.push(n);
    }
    out.sort(function (a, b) { return a - b; });
    return out;
  }
  // Sanitized write payload. Nulls mark the axis that this mode does not use
  // (backend: null clears the override / falls back to the user default).
  function readSchedule(root) {
    var mode = modeOf(scRadio(root, 'mode') || 'every_n');
    var everyEl = scNode(root, 'every_n');
    var timeEl = scNode(root, 'time');
    var targetOnly = scRadio(root, 'target_mode') === 'only';
    var wd = checkedDays(root, 'wd');
    var twd = targetOnly ? checkedDays(root, 'twd') : [];
    return {
      schedule_mode: mode,
      schedule_every_n: mode === 'weekdays' ? null : clampInt(everyEl && everyEl.value, 1, 7, 3),
      schedule_weekdays: mode === 'weekdays' ? wd.join(',') : null,
      send_time: CC_HM_RE.test(String(timeEl && timeEl.value)) ? timeEl.value : '20:00',
      lead_days: clampInt(readLead(root), 1, 7, 3),
      target_weekdays: twd.length ? twd.join(',') : null,
      min_tier: scRadio(root, 'min_tier') === 'shootable' ? 'shootable' : 'recommend',
      tz: browserTz()
    };
  }
  function setRadio(root, field, val) {
    var els = scNodes(root, field);
    for (var i = 0; i < els.length; i++) els[i].checked = els[i].getAttribute('data-v') === val;
  }
  function setDays(root, field, csv) {
    var days = csvDays(csv), els = scNodes(root, field);
    for (var i = 0; i < els.length; i++) els[i].checked = days.indexOf(parseInt(els[i].value, 10)) >= 0;
  }
  function writeSchedule(root, sch) {
    if (!root) return;
    var s = sch || blankDefaults();
    setRadio(root, 'mode', modeOf(s.schedule_mode));
    var everyEl = scNode(root, 'every_n');
    if (everyEl) everyEl.value = String(clampInt(s.schedule_every_n, 1, 7, 3));
    setDays(root, 'wd', s.schedule_weekdays);
    var timeEl = scNode(root, 'time');
    if (timeEl) timeEl.value = CC_HM_RE.test(String(s.send_time)) ? s.send_time : '20:00';
    writeLead(root, s.lead_days);
    var twd = csvDays(s.target_weekdays);
    setRadio(root, 'target_mode', twd.length ? 'only' : 'any');
    setDays(root, 'twd', twd.join(','));
    setRadio(root, 'min_tier', String(s.min_tier) === 'shootable' ? 'shootable' : 'recommend');
    syncModes(root);
  }
  // The two frequency modes and the two target modes are mutually exclusive —
  // only the live group stays operable (the other keeps its values).
  function syncModes(root) {
    if (!root) return;
    var weekdays = modeOf(scRadio(root, 'mode') || 'every_n') === 'weekdays';
    var everyEl = scNode(root, 'every_n');
    if (everyEl) everyEl.disabled = weekdays;
    var wds = scNodes(root, 'wd');
    for (var i = 0; i < wds.length; i++) wds[i].disabled = !weekdays;
    // CL-UX-02: the capsule row only expands for the mode that uses it —
    // 指定每星期幾 for sending, 只篩選 for the target day.
    var wdGroup = root.querySelector('[data-wd-group="wd"]');
    if (wdGroup) wdGroup.hidden = !weekdays;
    var only = scRadio(root, 'target_mode') === 'only';
    var twds = scNodes(root, 'twd');
    for (var j = 0; j < twds.length; j++) twds[j].disabled = !only;
    var twdGroup = root.querySelector('[data-wd-group="twd"]');
    if (twdGroup) twdGroup.hidden = !only;
  }
  function applyWeekdayLabels(root) {
    if (!root) return;
    var names = WD_NAMES[state.lang] || WD_NAMES['zh-TW'];
    ['wd', 'twd'].forEach(function (field) {
      var els = scNodes(root, field);
      for (var i = 0; i < els.length; i++) {
        var lbl = els[i].parentNode ? els[i].parentNode.querySelector('.rem-wd-t') : null;
        if (lbl) lbl.textContent = names[parseInt(els[i].value, 10)] || '';
      }
    });
  }

  // Plain-language summary fragments (owner example:
  // 「每週四、五 20:00 · 看未來 3 天 · 只看週六日 · 僅✓推薦」).
  function scheduleParts(sch, lg) {
    var s = sch || {};
    var parts = [];
    var time = CC_HM_RE.test(String(s.send_time)) ? s.send_time : '20:00';
    if (modeOf(s.schedule_mode) === 'weekdays') {
      var wd = csvDays(s.schedule_weekdays);
      parts.push({
        text: wd.length
          ? tIn('rem_def_weekly', lg).replace('{d}', dayNames(wd, lg)) + ' ' + time
          : tIn('rem_def_no_days', lg) + ' ' + time,
        fields: ['schedule_mode', 'schedule_weekdays', 'send_time']
      });
    } else {
      parts.push({
        text: tIn('rem_def_every_n', lg).replace('{n}', String(clampInt(s.schedule_every_n, 1, 7, 3))) + ' ' + time,
        fields: ['schedule_mode', 'schedule_every_n', 'send_time']
      });
    }
    parts.push({ text: tIn('rem_def_lookahead', lg).replace('{n}', String(clampInt(s.lead_days, 1, 7, 3))), fields: ['lead_days'] });
    var twd = csvDays(s.target_weekdays);
    if (twd.length) parts.push({ text: tIn('rem_def_target_days', lg).replace('{d}', dayNames(twd, lg, true)), fields: ['target_weekdays'] });
    parts.push({ text: tIn(String(s.min_tier) === 'shootable' ? 'rem_def_tier_shootable' : 'rem_def_tier_recommend', lg), fields: ['min_tier'] });
    return parts;
  }
  // inherited = { field: true } for rule fields that fall back to the default.
  // A partially-inheriting rule marks just the inherited fragments 「（預設）」;
  // a rule that overrides nothing carries the suffix once at the end.
  function scheduleSummary(sch, lg, inherited) {
    var parts = scheduleParts(sch, lg);
    var inh = inherited || {};
    function owned(p) { return p.fields.every(function (f) { return !!inh[f]; }); }
    var allInherited = parts.length > 0 && parts.every(owned);
    var suffix = tIn('rem_def_inherited', lg);
    var texts = parts.map(function (p) { return (owned(p) && !allInherited) ? p.text + suffix : p.text; });
    return texts.join(' · ') + (allInherited ? ' ' + suffix : '');
  }
  // Effective schedule of a rule = its own field, else the user default.
  function effectiveSchedule(rule, def) {
    var base = def || blankDefaults();
    var out = {}, inh = {};
    for (var i = 0; i < SCHEDULE_FIELDS.length; i++) {
      var f = SCHEDULE_FIELDS[i];
      var raw = rule ? rule[f] : null;
      var has = raw !== null && raw !== undefined && String(raw).trim() !== '';
      inh[f] = !has;
      out[f] = has ? raw : base[f];
    }
    return { schedule: mergeDefaults(out), inherited: inh };
  }

  // ---- next-trigger / unfit-streak derivation (CL-UI-90 mockup anatomy) ----
  // Pure client-side derivation from the SAME evaluations bundle the page
  // already loads for the picker — no new API, no data-layer change.
  // Next trigger = first future "good hour" of the rule's opportunity minus
  // min_advance_hours (spot-local, displayed as M/D HH:MM). A rule without an
  // explicit subject (opportunity_id empty) scans every opportunity at the
  // place and takes the earliest fit.
  function oppDays(place, oppId) {
    if (oppId) { var o = findSubject(place, oppId); return o ? (o.days || []) : []; }
    var out = [];
    ((place && place.opportunities) || []).forEach(function (o) { (o.days || []).forEach(function (d) { out.push(d); }); });
    return out;
  }
  function localNow(place, nowMs) {
    var off = 0;
    if (place && place.timezone_display && typeof place.timezone_display.utc_offset_hours === 'number') {
      off = place.timezone_display.utc_offset_hours * 3600000;
    }
    return new Date((nowMs == null ? Date.now() : nowMs) + off);
  }
  function findNextTrigger(place, oppId, advanceHours, nowMs) {
    var days = oppDays(place, oppId);
    if (!days.length) return null;
    var now = localNow(place, nowMs);
    var nowKey = now.toISOString().slice(0, 10) + 'T' + now.toISOString().slice(11, 16);
    var best = null; // {date, hour, atMs} earliest future good hour
    days.forEach(function (d) {
      (d.good_hours || []).forEach(function (h) {
        var key = d.local_date + 'T' + h;
        if (key <= nowKey) return;
        var atMs = Date.parse(d.local_date + 'T' + h + ':00Z');
        if (best === null || atMs < best.atMs) best = { local_date: d.local_date, hour: h, atMs: atMs };
      });
    });
    if (best === null) return null;
    var adv = (advanceHours == null ? 24 : advanceHours) * 3600000;
    var trig = new Date(best.atMs - adv);
    return {
      date: best.local_date, hour: best.hour,
      label: pad2(trig.getUTCMonth() + 1) + '/' + pad2(trig.getUTCDate()) + ' ' + pad2(trig.getUTCHours()) + ':' + pad2(trig.getUTCMinutes())
    };
  }
  function pad2(n) { return (n < 10 ? '0' : '') + n; }
  // Consecutive unfit days counted from the start of the bundle window
  // (earliest first), stopping at today — the amber 「該複核提醒」 cue.
  function unfitStreak(place, oppId, nowMs) {
    var days = oppDays(place, oppId);
    if (!days.length) return 0;
    var today = localNow(place, nowMs).toISOString().slice(0, 10);
    var streak = 0;
    for (var i = 0; i < days.length; i++) {
      var d = days[i];
      if (d.local_date > today) break;
      if ((d.good_hours || []).length === 0) streak++;
      else break;
    }
    return streak;
  }
  // CL-UI-99: a rule's parsed custom_conditions (object or JSON string), null in subject mode.
  function ccOf(rule) {
    var cc = rule && rule.custom_conditions;
    if (cc && typeof cc === 'object' && !(cc instanceof Array)) return cc;
    if (typeof cc === 'string' && cc.trim()) {
      try {
        var o = JSON.parse(cc);
        return (o && typeof o === 'object' && !(o instanceof Array)) ? o : null;
      } catch (e) { return null; }
    }
    return null;
  }

  // Card status line: paused → grey 暫停中; amber streak (>=3 unfit days, no
  // next window) → 該複核提醒 cue; else mono green next trigger; honest
  // 「近期無符合時段」 fallback instead of a fabricated time. Custom-mode
  // rules have no subject verdict layer — honest 「符合自訂條件時推播」.
  function nextStatusHtml(rule) {
    var on = !!rule.enabled;
    if (!on) return '<span class="rem-next rem-next-off">' + esc(t('rem_paused_next')) + '</span>';
    if (ccOf(rule)) {
      return '<span class="rem-next rem-next-off">' + esc(t('rem_custom_next')) + '</span>';
    }
    var place = findPlace(state.catalog, rule.place_id);
    var streak = unfitStreak(place, rule.opportunity_id);
    var next = findNextTrigger(place, rule.opportunity_id, rule.min_advance_hours);
    if (!next && streak >= 3) {
      return '<span class="rem-next rem-next-warn">' + esc(t('rem_streak').replace('{n}', String(streak))) + '</span>';
    }
    if (next) {
      return '<span class="rem-next" title="' + esc(t('rem_next_estimate')) + '">' +
        esc(t('rem_next_label')) + ' ' + esc(next.label) + '</span>';
    }
    return '<span class="rem-next">' + esc(t('rem_no_window')) + '</span>';
  }

  // ---- toast ----
  var notice = null, noticeTimer = null;
  function showNotice(key) {
    var el = document.getElementById('rem-state');
    var text = t(key);
    try {
      if (!notice) {
        notice = document.createElement('p');
        notice.className = 'rem-notice';
        notice.setAttribute('role', 'status');
        document.body.appendChild(notice);
      }
      notice.textContent = text;
      notice.hidden = false;
      if (noticeTimer) clearTimeout(noticeTimer);
      noticeTimer = setTimeout(function () { if (notice) notice.hidden = true; }, 6000);
    } catch (e) { /* best-effort */ }
    if (el) el.textContent = text;
  }

  // ---- data ----
  function fetchRules() {
    return fetch(RULES_ENDPOINT, { headers: { Accept: 'application/json' } }).then(function (r) {
      if (r.status === 401) { state.signedIn = false; state.rules = []; return; }
      if (!r.ok) throw new Error('HTTP ' + r.status);
      state.signedIn = true;
      return r.json().then(function (b) {
        state.rules = (b && b.rules) || [];
        // The rules payload also carries the user defaults — keep the panel in
        // sync without a second round-trip (CL-UX-01 Part B).
        if (b && b.defaults) state.defaults = mergeDefaults(b.defaults);
      });
    });
  }
  function patchRule(id, enabled) {
    return fetch(RULES_ENDPOINT + '/' + encodeURIComponent(id), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ enabled: enabled })
    }).then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); });
  }
  function deleteRule(id) {
    return fetch(RULES_ENDPOINT + '/' + encodeURIComponent(id), { method: 'DELETE' })
      .then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); });
  }
  function createRule(placeId, oppId, customConditions) {
    var payload = { placeId: placeId, channel: 'push', minAdvanceHours: 24 };
    if (customConditions) payload.customConditions = customConditions;
    else payload.opportunityId = oppId || undefined;
    return fetch(RULES_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload)
    }).then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); });
  }

  // CL-UX-01 Part B: the user's default schedule (GET) and its single write
  // path (PUT). Both carry tz from the browser — send_time is user-local.
  function fetchDefaults() {
    return fetch(DEFAULTS_ENDPOINT, { headers: { Accept: 'application/json' } }).then(function (r) {
      if (r.status === 401) throw new Error('HTTP 401');
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (b) {
      state.defaults = mergeDefaults(b && b.defaults);
      return state.defaults;
    });
  }
  function saveDefaults() {
    var panel = document.getElementById('rem-def-panel');
    var payload = readSchedule(panel);
    payload.channel = 'push';
    return fetch(DEFAULTS_ENDPOINT, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload)
    }).then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); });
  }
  function patchRuleSchedule(id, payload) {
    return fetch(RULES_ENDPOINT + '/' + encodeURIComponent(id), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload)
    }).then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); });
  }

  // ---- rendering ----
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function ruleLabel(rule) {
    var place = findPlace(state.catalog, rule.place_id);
    var placeName = place ? nameOf(place.name_i18n, state.lang) : rule.place_id;
    var subjName = t('rem_any_subject');
    if (ccOf(rule)) subjName = t('rem_cc_chip');
    else if (rule.opportunity_id) {
      var subj = findSubject(place, rule.opportunity_id);
      subjName = subj ? nameOf(subj.name_i18n, state.lang) : rule.opportunity_id;
    }
    return { placeName: placeName, subjName: subjName };
  }

  // ---- CL-UX-01 Part B: defaults panel + per-rule override panel ----
  function setText(id, key) {
    var el = document.getElementById(id);
    if (el) el.textContent = t(key);
  }
  var ovrSeq = 0;
  function wdBoxesHtml(field) {
    var labels = WD_NAMES[state.lang] || WD_NAMES['zh-TW'];
    var out = '';
    for (var d = 0; d <= 6; d++) {
      out += '<label class="rem-def-wd"><input type="checkbox" data-f="' + field + '" value="' + d + '">' +
        '<span class="rem-wd-t">' + esc(labels[d]) + '</span></label>';
    }
    return out;
  }
  // CL-UX-02: quick look-ahead capsules shared by the defaults panel and the
  // per-card override panel (same data-f="lead" contract as the weekday axes).
  function leadCapsulesHtml(ns) {
    var out = '';
    [1, 3, 5, 7].forEach(function (n) {
      out += '<label class="rem-def-lead"><input type="radio" name="' + ns + '-lead" data-f="lead" value="' + n + '">' +
        '<span data-lead-t="' + n + '"></span></label>';
    });
    return out;
  }
  function numOptionsHtml() {
    var out = '';
    for (var n = 1; n <= 7; n++) out += '<option value="' + n + '">' + n + '</option>';
    return out;
  }
  // The same control group as the defaults panel; labels are [data-l] keys
  // filled by localizeLabels so a panel follows the language switcher.
  function scheduleControlsHtml() {
    var ns = 'rem-ovr-' + (++ovrSeq);
    return '<div class="rem-def-grid">' +
      '<div class="rem-def-field">' +
        '<span class="rem-def-name" data-l="rem_def_freq"></span>' +
        '<label class="rem-def-opt"><input type="radio" name="' + ns + '-mode" data-f="mode" data-v="every_n" value="every_n">' +
          '<span data-l="rem_def_mode_every"></span><select data-f="every_n">' + numOptionsHtml() + '</select></label>' +
        '<label class="rem-def-opt"><input type="radio" name="' + ns + '-mode" data-f="mode" data-v="weekdays" value="weekdays">' +
          '<span data-l="rem_def_mode_weekdays"></span></label>' +
        '<div class="rem-def-wds" data-wd-group="wd" hidden>' + wdBoxesHtml('wd') + '</div>' +
      '</div>' +
      '<label class="rem-def-field"><span class="rem-def-name" data-l="rem_def_send_time"></span>' +
        '<input type="time" step="60" data-f="time"></label>' +
      '<div class="rem-def-field"><span class="rem-def-name" data-l="rem_def_lead"></span>' +
        '<div class="rem-def-leads" role="radiogroup">' + leadCapsulesHtml(ns) + '</div>' +
        '<input type="hidden" data-f="lead"></div>' +
      '<div class="rem-def-field">' +
        '<span class="rem-def-name" data-l="rem_def_target"></span>' +
        '<label class="rem-def-opt"><input type="radio" name="' + ns + '-target" data-f="target_mode" data-v="any" value="any">' +
          '<span data-l="rem_def_target_any"></span></label>' +
        '<label class="rem-def-opt"><input type="radio" name="' + ns + '-target" data-f="target_mode" data-v="only" value="only">' +
          '<span data-l="rem_def_target_only"></span></label>' +
        '<div class="rem-def-wds" data-wd-group="twd" hidden>' + wdBoxesHtml('twd') + '</div>' +
      '</div>' +
      '<div class="rem-def-field">' +
        '<span class="rem-def-name" data-l="rem_def_tier"></span>' +
        '<label class="rem-def-opt"><input type="radio" name="' + ns + '-tier" data-f="min_tier" data-v="recommend" value="recommend">' +
          '<span data-l="rem_def_tier_recommend"></span></label>' +
        '<label class="rem-def-opt"><input type="radio" name="' + ns + '-tier" data-f="min_tier" data-v="shootable" value="shootable">' +
          '<span data-l="rem_def_tier_shootable"></span></label>' +
      '</div></div>';
  }
  function localizeLabels(root) {
    if (!root) return;
    var els = root.querySelectorAll('[data-l]');
    for (var i = 0; i < els.length; i++) {
      var k = els[i].getAttribute('data-l');
      if (t(k)) els[i].textContent = t(k);
    }
  }
  function updateDefaultsSummary() {
    var panel = document.getElementById('rem-def-panel');
    var out = document.getElementById('rem-def-summary');
    if (!panel || !out || !state.defaults) return;
    out.textContent = scheduleSummary(readSchedule(panel), state.lang, {});
  }
  function updateOvrSummary(pnl) {
    if (!pnl) return;
    var out = pnl.querySelector('[data-ovr-summary]');
    if (out) out.textContent = scheduleSummary(readSchedule(pnl), state.lang, {});
  }
  function renderDefaults() {
    var panel = document.getElementById('rem-def-panel');
    if (!panel) return;
    // Non-DOM test stubs expose a plain object here — labels are the only
    // thing they can take, so stop before touching the control tree.
    if (typeof panel.querySelector !== 'function' || typeof panel.querySelectorAll !== 'function') return;
    setText('rem-def-title', 'rem_def_title');
    setText('rem-def-intro', 'rem_def_intro');
    setText('rem-def-l-freq', 'rem_def_freq');
    setText('rem-def-l-every', 'rem_def_mode_every');
    setText('rem-def-l-weekdays', 'rem_def_mode_weekdays');
    setText('rem-def-l-time', 'rem_def_send_time');
    setText('rem-def-l-lead', 'rem_def_lead');
    setText('rem-def-l-target', 'rem_def_target');
    setText('rem-def-l-target-any', 'rem_def_target_any');
    setText('rem-def-l-target-only', 'rem_def_target_only');
    setText('rem-def-l-tier', 'rem_def_tier');
    setText('rem-def-l-recommend', 'rem_def_tier_recommend');
    setText('rem-def-l-shootable', 'rem_def_tier_shootable');
    setText('rem-def-save', 'rem_def_save');
    setText('rem-def-toggle', 'rem_def_modify');
    applyWeekdayLabels(panel);
    applyLeadLabels(panel);
    var out = document.getElementById('rem-def-summary');
    if (!state.defaults) {
      if (out) out.textContent = t('rem_def_loading');
      return;
    }
    // Write only when the server payload object changes — a language switch
    // re-renders labels without stomping the user's in-progress edits.
    if (panel._src !== state.defaults) { writeSchedule(panel, state.defaults); panel._src = state.defaults; }
    syncModes(panel);
    updateDefaultsSummary();
  }
  function focusRuleId() {
    try { return new URLSearchParams(window.location.search).get('focus'); } catch (e) { return null; }
  }
  // ./reminders.html?focus=<rule id> — the card bell's 「修改此點規則」 deep
  // link: scroll to that card and open its override panel.
  var focusedOnce = false;
  function applyFocusParam() {
    var id = focusRuleId();
    if (!id || focusedOnce) return;
    var cards = document.querySelectorAll('#rem-list .rem-card');
    for (var i = 0; i < cards.length; i++) {
      if (cards[i].getAttribute('data-rule-id') !== id) continue;
      var pnl = cards[i].querySelector('[data-rem-ovr]');
      if (pnl) { pnl.hidden = false; syncModes(pnl); updateOvrSummary(pnl); }
      focusedOnce = true;
      try { cards[i].scrollIntoView({ behavior: 'smooth', block: 'center' }); }
      catch (e) { cards[i].scrollIntoView(); }
      return;
    }
  }
  // 儲存此點規則: PATCH concrete values for every field (+ tz).
  function saveRuleSchedule(ruleId, pnl) {
    if (!pnl) return;
    var payload = readSchedule(pnl);
    patchRuleSchedule(ruleId, payload).then(function (res) {
      if (res && res.status === 401) { state.signedIn = false; renderAll(); return; }
      if (!res || !res.body || res.body.ok !== true) { showNotice('rem_err'); return; }
      var next = (res.body && res.body.rule) ? res.body.rule : payload;
      state.rules = state.rules.map(function (r) { return r.id === ruleId ? Object.assign({}, r, next) : r; });
      showNotice('rem_def_rule_saved');
      renderList();
      if (window.ChaseLightsReminders) window.ChaseLightsReminders.refresh();
    }).catch(function () { showNotice('rem_err'); });
  }
  // 恢復預設: explicit nulls clear every override so the rule inherits the
  // user default again (backend contract: null = inherit).
  function resetRuleSchedule(ruleId) {
    var cleared = {
      schedule_mode: null, schedule_every_n: null, schedule_weekdays: null,
      send_time: null, lead_days: null, target_weekdays: null, min_tier: null,
      tz: browserTz()
    };
    patchRuleSchedule(ruleId, cleared).then(function (res) {
      if (res && res.status === 401) { state.signedIn = false; renderAll(); return; }
      if (!res || !res.body || res.body.ok !== true) { showNotice('rem_err'); return; }
      state.rules = state.rules.map(function (r) { return r.id === ruleId ? Object.assign({}, r, cleared) : r; });
      showNotice('rem_def_rule_reset');
      renderList();
      if (window.ChaseLightsReminders) window.ChaseLightsReminders.refresh();
    }).catch(function () { showNotice('rem_err'); });
  }

  function renderList() {
    var list = document.getElementById('rem-list');
    var panel = document.getElementById('rem-list-panel');
    var empty = document.getElementById('rem-empty');
    if (!state.signedIn) { panel.hidden = true; return; }
    panel.hidden = false;
    document.getElementById('rem-list-title').textContent = t('rem_list_title');
    var active = state.rules.filter(function (r) { return !!r.enabled; }).length;
    document.getElementById('rem-count').textContent = state.rules.length
      ? t('rem_active_count').replace('{total}', String(state.rules.length)).replace('{active}', String(active))
      : '';
    empty.hidden = !!state.rules.length;
    document.getElementById('rem-empty-title').textContent = t('rem_empty_t');
    document.getElementById('rem-empty-desc').textContent = t('rem_empty_d');
    document.getElementById('rem-empty-add').textContent = t('rem_empty_a');
    if (!state.rules.length) { list.innerHTML = ''; return; }
    list.innerHTML = state.rules.map(function (rule) {
      var names = ruleLabel(rule);
      var on = !!rule.enabled;
      var region = regionName(regionOfPlace(rule.place_id), state.lang);
      var cc = ccOf(rule);
      // CL-UI-99: custom-mode cards carry a one-line condition summary.
      // CL-UX-02: the legacy 「提前 N 小時」 fragment is gone — the schedule
      // summary line below is the single trigger narrative on the card.
      var summary = cc ? customSummary(cc, state.lang) : '';
      // CL-UX-01 Part B: effective schedule line (rule value, else default)
      // with 「（預設）」 on whatever the rule inherits.
      var eff = effectiveSchedule(rule, defOf());
      var schSummary = scheduleSummary(eff.schedule, state.lang, eff.inherited);
      return '<div class="rem-card' + (on ? '' : ' rem-off') + '" data-rule-id="' + esc(rule.id) + '">' +
        '<div class="rem-main">' +
        '<div class="rem-line1"><span class="rem-place">' + esc(names.placeName) + '</span>' +
        '<span class="rem-subject-chip">' + esc(names.subjName) + '</span></div>' +
        '<div class="rem-line2"><span class="rem-region">' + esc(region) + '</span>' +
        nextStatusHtml(rule) +
        '</div>' +
        '<div class="rem-line3"><span class="rem-sched-summary" data-rem-sched-summary>' + esc(schSummary) + '</span></div>' +
        (summary ? '<div class="rem-line3"><span class="rem-cc-summary">' + esc(summary) + '</span></div>' : '') +
        '</div>' +
        '<div class="rem-acts">' +
        '<button type="button" class="rem-switch' + (on ? ' rem-on' : '') + '" data-rem-toggle role="switch"' +
        ' aria-checked="' + (on ? 'true' : 'false') + '" aria-label="' + esc(on ? t('rem_enabled') : t('rem_disabled')) + '"></button>' +
        '<button type="button" class="rem-edit-btn" data-rem-sched>' + esc(t('rem_edit_rule')) + '</button>' +
        '<button type="button" class="rem-edit-btn" data-rem-edit>' + esc(t('rem_edit')) + '</button>' +
        '<button type="button" class="rem-del" data-rem-delete>' + esc(t('rem_delete')) + '</button>' +
        '</div>' +
        '<div class="rem-ovr" data-rem-ovr hidden>' +
        '<p class="rem-cc-title">' + esc(t('rem_edit_rule')) + '</p>' +
        scheduleControlsHtml() +
        '<p class="rem-def-summary" data-ovr-summary></p>' +
        '<div class="rem-ovr-acts">' +
        '<button type="button" class="rem-add-btn" data-rem-sched-save>' + esc(t('rem_def_save_rule')) + '</button>' +
        '<button type="button" class="rem-edit-btn" data-rem-sched-reset>' + esc(t('rem_def_reset')) + '</button>' +
        '</div></div>' +
        '</div>';
    }).join('');
    // Prefill each override panel with the rule's EFFECTIVE values. A stub
    // list element (tests) cannot be queried — skip the post-pass there.
    if (typeof list.querySelectorAll !== 'function' || typeof list.querySelector !== 'function') return;
    var cards = list.querySelectorAll('.rem-card');
    for (var ci = 0; ci < cards.length; ci++) {
      var pnl = cards[ci].querySelector('[data-rem-ovr]');
      if (!pnl) continue;
      var rid = cards[ci].getAttribute('data-rule-id');
      var target = null;
      for (var ri = 0; ri < state.rules.length; ri++) if (state.rules[ri].id === rid) target = state.rules[ri];
      localizeLabels(pnl);
      applyWeekdayLabels(pnl);
      applyLeadLabels(pnl);
      writeSchedule(pnl, effectiveSchedule(target, defOf()).schedule);
      updateOvrSummary(pnl);
    }
    applyFocusParam();
  }

  function renderLoginPanel() {
    var panel = document.getElementById('rem-login-panel');
    var body = document.getElementById('rem-login-body');
    if (state.signedIn !== false) { panel.hidden = true; return; }
    panel.hidden = false;
    body.innerHTML = '<p>' + esc(t('rem_login_prompt')) + '</p>' +
      '<a href="/api/v1/auth/line/start">' + esc(t('rem_login_line')) + '</a>' +
      '<a href="/api/v1/auth/google/start">' + esc(t('rem_login_google')) + '</a>';
  }

  function fillSelect(sel, options, value) {
    sel.innerHTML = options.map(function (o) {
      return '<option value="' + esc(o.value) + '"' + (o.value === value ? ' selected' : '') + '>' + esc(o.label) + '</option>';
    }).join('');
  }

  function renderQuickAdd() {
    var panel = document.getElementById('rem-add-panel');
    if (!state.signedIn) { panel.hidden = true; return; }
    panel.hidden = false;
    document.getElementById('rem-add-title').textContent = t('rem_add_title');
    document.getElementById('rem-search').placeholder = t('rem_search_placeholder');
    document.getElementById('rem-add-submit').textContent = t('rem_add_btn');
    document.getElementById('rem-flow-hint').textContent = t('rem_flow_hint');

    var regionSel = document.getElementById('rem-region');
    var prevRegion = regionSel.value || 'tw';
    fillSelect(regionSel, REGIONS.map(function (r) { return { value: r.id, label: regionName(r.id, state.lang) }; }), prevRegion);
    renderPlaceOptions();
    renderSubjectOptions();
    renderSearchResults();
    renderPreview();
  }

  // Add preview (mockup .preview): appears once a place is picked; the primary
  // button stays disabled until then (no guessing the user's intent).
  function renderPreview() {
    var pv = document.getElementById('rem-preview');
    var btn = document.getElementById('rem-add-submit');
    if (!state.signedIn) { pv.hidden = true; return; }
    var placeId = document.getElementById('rem-place').value;
    var place = findPlace(state.catalog, placeId);
    var oppId = document.getElementById('rem-subject').value;
    if (oppId === CC_CUSTOM_ID) {
      if (!place) { pv.hidden = true; btn.disabled = true; return; }
      pv.hidden = false;
      btn.disabled = false;
      var placeNameC = nameOf(place.name_i18n, state.lang) || place.place_id;
      document.getElementById('rem-preview-txt').textContent =
        placeNameC + ' · ' + t('rem_cc_chip') + ' · ' + t('rem_custom_preview');
      return;
    }
    var subjName = oppId
      ? (function () { var s = findSubject(place, oppId); return s ? nameOf(s.name_i18n, state.lang) : oppId; })()
      : t('rem_any_subject');
    if (!place) { pv.hidden = true; btn.disabled = true; return; }
    pv.hidden = false;
    btn.disabled = false;
    var placeName = nameOf(place.name_i18n, state.lang) || place.place_id;
    var next = findNextTrigger(place, oppId || null, 24);
    var when = next ? t('rem_preview_first') + ' ' + next.label : t('rem_preview_unknown');
    document.getElementById('rem-preview-txt').textContent = placeName + ' · ' + subjName + ' · ' + when;
  }

  function placesForRegion(regionId) {
    return state.catalog.filter(function (p) { return regionOfPlace(p.place_id) === regionId; });
  }

  function renderPlaceOptions() {
    var regionId = document.getElementById('rem-region').value;
    var placeSel = document.getElementById('rem-place');
    var prev = placeSel.value;
    var places = placesForRegion(regionId);
    fillSelect(placeSel, places.map(function (p) { return { value: p.place_id, label: nameOf(p.name_i18n, state.lang) || p.place_id }; }),
      places.some(function (p) { return p.place_id === prev; }) ? prev : (places[0] && places[0].place_id));
    renderSubjectOptions();
  }

  function renderSubjectOptions() {
    var placeId = document.getElementById('rem-place').value;
    var place = findPlace(state.catalog, placeId);
    var subjSel = document.getElementById('rem-subject');
    var prev = subjSel.value;
    var opps = (place && place.opportunities) || [];
    // CL-UI-99: third layer gains the 自訂條件… entry (custom-conditions mode).
    var options = [{ value: '', label: t('rem_any_subject') }].concat(
      opps.map(function (o) { return { value: o.opportunity_id, label: nameOf(o.name_i18n, state.lang) || o.opportunity_id }; })
    ).concat([{ value: CC_CUSTOM_ID, label: t('rem_custom_opt') }]);
    fillSelect(subjSel, options, options.some(function (o) { return o.value === prev; }) ? prev : '');
    renderCustomPanel();
  }

  // CL-UI-99: show/hide the custom-conditions form; label + hint texts follow
  // the language, values follow CC_DEFAULTS unless the rule-edit prefill set them.
  function renderCustomPanel() {
    var panel = document.getElementById('rem-custom-panel');
    if (!panel) return;
    var custom = document.getElementById('rem-subject').value === CC_CUSTOM_ID;
    panel.hidden = !custom;
    if (!custom) return;
    document.getElementById('rem-cc-title').textContent = t('rem_cc_panel_title');
    var labelIds = {
      'rem-cc-low': 'rem_cc_low', 'rem-cc-mid': 'rem_cc_mid', 'rem-cc-high': 'rem_cc_high',
      'rem-cc-precip': 'rem_cc_precip', 'rem-cc-vis': 'rem_cc_vis', 'rem-cc-wind': 'rem_cc_wind',
      'rem-cc-lead': 'rem_cc_lead'
    };
    for (var id in labelIds) {
      var labelEl = document.querySelector('label[for="' + id + '"] .rem-cc-name');
      if (labelEl) labelEl.textContent = t(labelIds[id]);
    }
    var hintIds = {
      'rem-cc-hint-low': 'rem_cc_hint_low', 'rem-cc-hint-mid': 'rem_cc_hint_mid',
      'rem-cc-hint-high': 'rem_cc_hint_high', 'rem-cc-hint-precip': 'rem_cc_hint_precip',
      'rem-cc-hint-vis': 'rem_cc_hint_vis', 'rem-cc-hint-wind': 'rem_cc_hint_wind',
      'rem-cc-hint-window': 'rem_cc_hint_window', 'rem-cc-hint-lead': 'rem_cc_hint_lead'
    };
    for (var hid in hintIds) {
      var hintEl = document.getElementById(hid);
      if (hintEl) hintEl.textContent = t(hintIds[hid]);
    }
    document.getElementById('rem-cc-window-label').textContent = t('rem_cc_window');
    // Defaults are written once (a user mid-edit is never reset by a re-render).
    if (!panel.dataset.filled) {
      for (var k in CC_INPUT_IDS) {
        var input = document.getElementById(CC_INPUT_IDS[k]);
        if (input) input.value = CC_DEFAULTS[k];
      }
      document.getElementById('rem-cc-start').value = CC_DEFAULTS.window_start;
      document.getElementById('rem-cc-end').value = CC_DEFAULTS.window_end;
      panel.dataset.filled = '1';
    }
  }

  function renderSearchResults() {
    var kw = document.getElementById('rem-search').value;
    var ul = document.getElementById('rem-results');
    // Mockup contract: the hit list only appears once a keyword is typed —
    // no 460-row dump on an empty input (the pure filterCatalog helper keeps
    // its empty-keyword = full-catalog semantics for tests).
    if (!String(kw || '').trim()) { ul.innerHTML = ''; return; }
    var matches = [];
    filterCatalog(state.catalog, kw, state.lang).forEach(function (m) {
      var opps = m.opportunities.length ? m.opportunities : (m.place.opportunities || []);
      if (kw && !m.opportunities.length && !(nameOf(m.place.name_i18n, state.lang) || '').toLocaleLowerCase().includes(String(kw).trim().toLocaleLowerCase())) return;
      opps.forEach(function (o) {
        matches.push({ place: m.place, opp: o });
      });
    });
    if (!matches.length) { ul.innerHTML = '<li class="rem-rr-note">' + esc(t('rem_no_match')) + '</li>'; return; }
    var existing = {};
    state.rules.forEach(function (r) { existing[r.place_id + '|' + (r.opportunity_id || '')] = true; });
    var hits = {};
    matches.forEach(function (m) { hits[m.place.place_id] = true; });
    var hitCount = Object.keys(hits).length;
    var head = '<li class="rem-rr-note"><span class="rem-rr-hint">' +
      esc(t('rem_found').replace('{n}', String(hitCount))) + '</span></li>';
    ul.innerHTML = head + matches.slice(0, 40).map(function (m) {
      var key = m.place.place_id + '|' + (m.opp ? m.opp.opportunity_id : '');
      var added = !!existing[key];
      return '<li><span class="rem-rr-main"><span class="rem-rr-name">' + esc(nameOf(m.place.name_i18n, state.lang) || m.place.place_id) + '</span>' +
        '<span class="rem-rr-sub">' + esc(m.opp ? (nameOf(m.opp.name_i18n, state.lang) || m.opp.opportunity_id) : t('rem_any_subject')) + '</span></span>' +
        '<button type="button" data-rem-quick-add data-place="' + esc(m.place.place_id) + '" data-opp="' + esc(m.opp ? m.opp.opportunity_id : '') + '"' + (added ? ' disabled' : '') + '>' +
        esc(added ? t('rem_added_btn') : t('rem_add_btn')) + '</button></li>';
    }).join('');
  }

  function renderAll() {
    document.getElementById('page-title').textContent = t('page_title');
    document.documentElement.lang = state.lang;
    document.title = 'ChaseLights — ' + t('page_title');
    if (!state.signedIn) document.getElementById('rem-count').textContent = '';
    // nav_* keys are mirrored in this page's dict (shared shell markup).
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var k = el.getAttribute('data-i18n');
      if (t(k)) el.textContent = t(k);
    });
    var state0 = document.getElementById('rem-state');
    if (state0 && !notice) state0.textContent = state.signedIn === null ? t('rem_loading') : '';
    renderLoginPanel();
    renderDefaults();
    renderList();
    renderQuickAdd();
  }

  // ---- events ----
  function bindEvents() {
    document.getElementById('lang-select').addEventListener('change', function () {
      state.lang = lang();
      try { localStorage.setItem('chaselights_lang', state.lang); } catch (e) { /* private mode */ }
      renderAll();
    });
    // CL-UX-01 Part B: defaults panel — live summary + mode exclusivity + save.
    var defPanel = document.getElementById('rem-def-panel');
    if (defPanel) {
      defPanel.addEventListener('change', function () { syncModes(defPanel); updateDefaultsSummary(); });
      defPanel.addEventListener('input', function () { updateDefaultsSummary(); });
    }
    // CL-UX-02: defaults collapse to a summary row; 修改預設 expands the panel.
    var defToggle = document.getElementById('rem-def-toggle');
    if (defToggle) defToggle.addEventListener('click', function () {
      var body = document.getElementById('rem-def-body');
      if (!body) return;
      var opening = !!body.hidden;
      body.hidden = !opening;
      defToggle.setAttribute('aria-expanded', opening ? 'true' : 'false');
      if (opening) { syncModes(defPanel); updateDefaultsSummary(); }
    });
    var defSave = document.getElementById('rem-def-save');
    if (defSave) defSave.addEventListener('click', function () {
      if (state.signedIn === false) { showNotice('rem_login_prompt'); return; }
      saveDefaults().then(function (res) {
        if (res && res.status === 401) { state.signedIn = false; renderAll(); return; }
        if (!res || !res.body || res.body.ok !== true) { showNotice('rem_def_err'); return; }
        state.defaults = mergeDefaults((res.body && res.body.defaults) || readSchedule(defPanel));
        showNotice('rem_def_saved');
        renderDefaults();
        // Every inherited card line now shows the new default values.
        renderList();
        if (window.ChaseLightsReminders) window.ChaseLightsReminders.refresh();
      }).catch(function () { showNotice('rem_def_err'); });
    });
    // A rule's override panel keeps its own one-line summary live.
    var remListEl = document.getElementById('rem-list');
    function ovrChanged(e) {
      var pnl = e.target && e.target.closest ? e.target.closest('[data-rem-ovr]') : null;
      if (!pnl) return;
      syncModes(pnl);
      updateOvrSummary(pnl);
    }
    remListEl.addEventListener('change', ovrChanged);
    remListEl.addEventListener('input', ovrChanged);
    document.getElementById('rem-region').addEventListener('change', function () { renderPlaceOptions(); renderPreview(); });
    document.getElementById('rem-place').addEventListener('change', function () { renderSubjectOptions(); renderPreview(); });
    document.getElementById('rem-subject').addEventListener('change', function () {
      // CL-UI-99: the custom entry toggles the parameter form live.
      renderCustomPanel();
      renderPreview();
    });
    document.getElementById('rem-search').addEventListener('input', renderSearchResults);
    document.getElementById('rem-empty-add').addEventListener('click', function () {
      var region = document.getElementById('rem-region');
      if (region) region.focus();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    document.getElementById('rem-add-submit').addEventListener('click', function () {
      var placeId = document.getElementById('rem-place').value;
      var subjVal = document.getElementById('rem-subject').value;
      if (subjVal === CC_CUSTOM_ID) {
        var cc = collectCustomConditions();
        if (!cc) { showNotice('rem_cc_invalid'); return; }
        addRule(placeId, null, cc);
        return;
      }
      addRule(placeId, subjVal);
    });
    document.getElementById('rem-list').addEventListener('click', function (e) {
      var row = e.target.closest ? e.target.closest('.rem-card') : null;
      if (!row) return;
      var ruleId = row.getAttribute('data-rule-id');
      // CL-UX-01 Part B: per-rule schedule override panel
      if (e.target.matches && e.target.matches('[data-rem-sched]')) {
        var ovr = row.querySelector('[data-rem-ovr]');
        if (ovr) {
          ovr.hidden = !ovr.hidden;
          if (!ovr.hidden) { syncModes(ovr); updateOvrSummary(ovr); }
        }
        return;
      }
      if (e.target.matches && e.target.matches('[data-rem-sched-save]')) {
        saveRuleSchedule(ruleId, row.querySelector('[data-rem-ovr]'));
        return;
      }
      if (e.target.matches && e.target.matches('[data-rem-sched-reset]')) {
        resetRuleSchedule(ruleId);
        return;
      }
      if (e.target.matches && e.target.matches('[data-rem-delete]')) {
        deleteRule(ruleId).then(function (res) {
          if (!res || !res.body || res.body.ok !== true) { showNotice('rem_err'); return; }
          showNotice('rem_removed');
          return reload();
        }).catch(function () { showNotice('rem_err'); });
        return;
      }
      if (e.target.matches && e.target.matches('[data-rem-edit]')) {
        // Mockup semantics: 編輯 = load the rule into the add panel for
        // re-picking; no extra API surface (CL-UI-58 contract untouched).
        var rule = state.rules.filter(function (r) { return r.id === ruleId; })[0];
        if (!rule) return;
        var regionSel = document.getElementById('rem-region');
        regionSel.value = regionOfPlace(rule.place_id);
        renderPlaceOptions();
        document.getElementById('rem-place').value = rule.place_id;
        renderSubjectOptions();
        var editCc = ccOf(rule);
        if (editCc) {
          // CL-UI-99: editing a custom rule reopens the form with its stored
          // parameters (marked filled so a re-render never resets them).
          var ccPanel = document.getElementById('rem-custom-panel');
          document.getElementById('rem-subject').value = CC_CUSTOM_ID;
          for (var k in CC_INPUT_IDS) {
            var input = document.getElementById(CC_INPUT_IDS[k]);
            if (input && editCc[k] != null) input.value = editCc[k];
          }
          if (typeof editCc.window_start === 'string') document.getElementById('rem-cc-start').value = editCc.window_start;
          if (typeof editCc.window_end === 'string') document.getElementById('rem-cc-end').value = editCc.window_end;
          if (ccPanel) ccPanel.dataset.filled = '1';
          renderCustomPanel();
        } else if (rule.opportunity_id) {
          document.getElementById('rem-subject').value = rule.opportunity_id;
        }
        renderPreview();
        document.getElementById('rem-add-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
      if (e.target.matches && e.target.matches('[data-rem-toggle]')) {
        var btn = e.target;
        var on = !btn.classList.contains('rem-on');
        patchRule(ruleId, on).then(function (res) {
          if (!res || res.status === 401 || !res.body || res.body.ok !== true) {
            if (res && res.status === 401) { state.signedIn = false; renderAll(); }
            else showNotice('rem_err');
            return;
          }
          state.rules = state.rules.map(function (r) { return r.id === ruleId ? Object.assign({}, r, { enabled: on ? 1 : 0 }) : r; });
          renderList();
          if (window.ChaseLightsReminders) window.ChaseLightsReminders.refresh();
        }).catch(function () { showNotice('rem_err'); });
      }
    });
    document.getElementById('rem-results').addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('[data-rem-quick-add]') : null;
      if (!btn || btn.disabled) return;
      addRule(btn.getAttribute('data-place'), btn.getAttribute('data-opp'));
    });
  }

  function addRule(placeId, oppId, customConditions) {
    createRule(placeId, oppId, customConditions).then(function (res) {
      if (res && res.status === 401) { state.signedIn = false; renderAll(); return; }
      if (res && res.status === 402) { showNotice('rem_limit'); return; }
      if (!res || !res.body || res.body.ok !== true) { showNotice('rem_err'); return; }
      showNotice('rem_saved');
      return reload();
    }).catch(function () { showNotice('rem_err'); });
  }

  function reload() {
    return fetchRules().then(renderAll).catch(function () { showNotice('rem_err'); });
  }

  // CL-UI-61: the session check is throttled — one /auth/me call per window
  // (boot, reloads and post-401 retries reuse the same cached answer instead
  // of hammering the endpoint). force=true bypasses the window.
  var ME_THROTTLE_MS = 30000;
  var mePromise = null, meAt = 0;
  function checkSignedIn(force) {
    var now = Date.now();
    if (!force && mePromise && now - meAt < ME_THROTTLE_MS) return mePromise;
    meAt = now;
    mePromise = fetch(ME_ENDPOINT, { headers: { Accept: 'application/json' } }).then(function (r) {
      state.signedIn = r.ok;
      return r.ok;
    }).catch(function () { return false; });
    return mePromise;
  }

  function loadCatalog() {
    // Catalog failure must not block the signed-in rules load (CL-UI-61):
    // it only degrades the quick-add picker names, not the login gate.
    // CL-UI-90: once the bundle lands, re-render the picker + preview —
    // boot renders the panel before the fetch resolves, so without this
    // re-render the preview row can stay hidden until the next interaction.
    return fetch(CATALOG_URL, { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (b) {
        state.catalog = (b && b.places) || [];
        if (state.signedIn) { renderQuickAdd(); }
      })
      .catch(function () { state.catalog = []; });
  }

  function boot() {
    state.lang = lang();
    bindEvents();
    renderAll();
    loadCatalog();
    // CL-UI-61 login gate: resolve the session first (throttled /auth/me),
    // then fetch rules ONLY while signed in. Signed-out visitors get the
    // 「請先登入」 panel with the login buttons — never the sync-error wording.
    checkSignedIn().then(function (signed) {
      if (!signed) {
        // Signed-out visitors still see a usable panel (built-in defaults).
        state.defaults = state.defaults || blankDefaults();
        renderAll();
        return null;
      }
      // Defaults first: every card summary shows rule value or the default.
      return fetchDefaults().catch(function () { state.defaults = state.defaults || blankDefaults(); })
        .then(function () { renderAll(); return reload(); });
    }).catch(function () {
      // Only a signed-in rules failure reaches here as a sync error; the
      // signed-out branch renders the login panel instead (CL-UI-61).
      if (state.signedIn === true) showNotice('rem_err');
      else renderAll();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  // Exposed for tests.
  window.ChaseLightsRemindersPage = {
    state: state,
    t: t,
    lang: lang,
    regionOfPlace: regionOfPlace,
    filterCatalog: filterCatalog,
    findPlace: findPlace,
    findSubject: findSubject,
    nameOf: nameOf,
    renderList: renderList,
    renderSearchResults: renderSearchResults,
    renderPreview: renderPreview,
    findNextTrigger: findNextTrigger,
    unfitStreak: unfitStreak,
    nextStatusHtml: nextStatusHtml,
    ccOf: ccOf,
    customSummary: customSummary,
    collectCustomConditions: collectCustomConditions,
    renderCustomPanel: renderCustomPanel,
    renderSubjectOptions: renderSubjectOptions,
    CC_CUSTOM_ID: CC_CUSTOM_ID,
    CC_DEFAULTS: CC_DEFAULTS,
    // CL-UX-01 Part B: default schedule + per-rule override
    fetchDefaults: fetchDefaults,
    saveDefaults: saveDefaults,
    patchRuleSchedule: patchRuleSchedule,
    readSchedule: readSchedule,
    writeSchedule: writeSchedule,
    syncModes: syncModes,
    mergeDefaults: mergeDefaults,
    blankDefaults: blankDefaults,
    effectiveSchedule: effectiveSchedule,
    scheduleSummary: scheduleSummary,
    scheduleParts: scheduleParts,
    browserTz: browserTz,
    renderDefaults: renderDefaults,
    applyFocusParam: applyFocusParam,
    saveRuleSchedule: saveRuleSchedule,
    resetRuleSchedule: resetRuleSchedule,
    WD_NAMES: WD_NAMES
  };
})();
