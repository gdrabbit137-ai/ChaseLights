/* CL-APP-06 (DESIGN-8): custom places — private member points on the homepage
   single list. Self-contained asset (member-auth.js / favorites-client.js
   precedent): own tri-lingual pack, own CSS file, no app.js edits —
   app.js stays untouched so its render-expression pins stay valid.

   Design contract (design-review-8 §1 + owner rulings):
   - single list: private points ride the SAME card grid and tier semantics —
     the ONLY differences are the gray 「私人」 badge, the ⋯ menu
     (✎編輯／🎞掛題材·條件／🗑刪除 — patch-6 removed 提名升級官方) and the 全部｜官方｜私人
     view switch next to the region/tier filters;
   - gray identity: badge/pin NEVER borrow ✓○✗ semantic colors;
   - honest counts: 「共 N 官方＋你的 M 私人點」, 全部 = 官方 + 私人;
   - trial expired (owner ruling): free trial 90 days → cap 0 — expired points
     are hidden from the default list and shown GRAY under 私人 with an
     honest 「試用期滿」 + upgrade CTA; data is kept, evaluation stopped;
   - fetch deferred (owner layer-3): a queued point honestly shows
     「已建立·氣象資料明日更新」 — no fabricated weather data;
   - add flow = button modal (map pin + lat/lng, DEM elevation + timezone are
     READ-ONLY, auto-resolved — the user never types either);
   - conditions = CL-UI-99 five parameter groups, same schema/validation;
   - delete = red confirm dialog; soft delete (revivable within 30 days);
   - soft delete keeps data 30 days (same-coordinate revive). */
(function () {
  'use strict';
  var API = '/api/v1/custom_places';
  var VIEW_KEY = 'chaselights_cp_view';
  var LANGS = ['zh-TW', 'en', 'ja'];
  // patch-4 (CL-APP-06): real basemap in the pin picker — the same vendored
  // maplibre-gl 6.11.2 module weather-map.js already ships (assets/vendor/,
  // no unpkg CDN). Relative chunk imports resolve inside assets/vendor/.
  var MAPLIBRE_MODULE = new URL('assets/vendor/maplibre-gl.mjs', document.baseURI).href;

  var T = {
    'zh-TW': {
      priv_badge: '私人', v_all: '不限來源', v_official: '官方', v_private: '私人',
      wx_no_subject: '尚未設定題材', wx_no_subject_note: '這個點還沒掛題材，所以不給拍攝判定。以下是當地天氣。',
      wx_vis: '能見度', wx_temp: '氣溫', wx_wx: '天氣',
      wmo_clear: '晴', wmo_mostly_clear: '晴時多雲', wmo_partly: '多雲', wmo_overcast: '陰',
      wmo_fog: '霧', wmo_drizzle: '毛毛雨', wmo_rain: '雨', wmo_snow: '雪', wmo_showers: '陣雨',
      wmo_snow_showers: '陣雪', wmo_thunder: '雷雨',
      add_btn: '新增私人景點', quota_lbl: '私人點', quota_owner: '無限',
      count_fmt: '共 {n} 個官方景點＋你的 {m} 個私人點',
      count_fmt_zero: '共 {n} 個官方景點（尚未建立私人點）',
      tier_rec: '✓ 推薦', tier_shoot: '○ 可拍', tier_no: '✗ 不宜', tier_pending: '⏳ 排隊中',
      trial_expired: '試用期滿', trial_note: '評估已停止（資料保留）', trial_cta: '升級 Premium 恢復使用',
      deferred_note: '已建立·氣象資料明日更新',
      m_edit: '✎ 編輯', m_cc: '🎞 掛題材·條件', m_del: '🗑 刪除',
      m_refetch: '🔄 獨立重新抓取',
      share_one: '與 {n} 共用資料', share_many: '與 {n} 等 {c} 處共用資料',
      refetch_done: '已脫離共組，獨立重新抓取排隊中（計 1 點配額）。',
      add_title: '新增私人景點', add_edit_title: '編輯私人景點', add_sub: '名稱 → 地圖釘點 → 自動海拔／時區',
      qd_name: '名稱', qd_name_ph: '例如：礁溪自家陽台展望', qd_pin: '地圖釘點（點圖落釘，或直接鍵入經緯度）',
      qd_pin_hint: '全球任意經緯度皆可（海洋／極區亦可）；拖曳地圖釘或點圖落釘，與 lat/lng 雙向同步',
      pin_map_loading: '底圖載入中…（載入失敗會退回格線模式）',
      ro_elev: '海拔（DEM 自動）', ro_tz: '時區自動', ro_pending: '落釘後自動帶入',
      ro_elev_outlier: '海拔異常（超出 −450～8,849 m）——請確認座標',
      create: '建立私人點', update: '更新私人點',
      reason_name: '請先輸入景點名稱', reason_pin: '請先落釘或輸入經緯度',
      done1: '✓ 私人點已建立', done1_edit: '✓ 已更新', done_deferred: '已建立·氣象資料明日更新（每日抓取額度誠實排隊）',
      cc_title: '掛題材·自訂條件', cc_sub: '自訂條件',
      p_low: '低雲門檻（%）', p_mid: '中雲門檻（%）', p_high: '高雲門檻（%）', p_precip: '降水上限（mm/h）',
      p_vis: '能見度下限（km）', p_wind: '風速上限（m/s）', p_window: '時間窗', p_lead: '提前量（分鐘）',
      p_months: '適用月份', p_months_hint: '不選＝全年適用；選取後只有該月份會判定（cron 同步月份窗）',
      // patch-7: private-card forecast popup (same card-click interaction as official cards)
      qv_title: '預報速覽', qv_quick: '現在去會怎樣', qv_days: '8 日概況', qv_no_data: '─',
      qv_no_data_note: '此日尚無資料（資料僅涵蓋未來約 2 日）', qv_subjects: '逐題材判定',
      qv_subject_custom: '自訂條件', qv_general: '可拍', qv_general_base: '一般基準', qv_entry: '🎞 題材',
      qv_load_fail: '預報資料暫時無法載入——可能仍在排隊抓取（明日更新）。',
      qv_gen: '符合 {n}/{t} 小時',
      qv_win_passed: '窗已過·今日仍可拍',
      cond_n: '條件 ×{n}', cond_required: '成立條件',
      cc_prev: '摘要預覽：', cc_prev_none: '（未調任何參數＝一般基準）', cc_submit: '套用到此點',
      cc_done1: '✓ 條件已套用', cc_none: '（僅一般基準）',
      // patch-8: theme list manager (multiple condition groups per place)
      th_title: '掛題材·條件', th_sub: '題材列表', th_add: '＋ 新增題材', th_cap_note: '已達上限 5 組（刪除一組後可再新增）',
      th_empty: '尚未掛任何題材——此點以一般基準判定。', th_count: '{n}/{c} 組',
      th_name: '題材名稱', th_name_ph: '例如：清晨雲海窗', th_name_required: '請先輸入題材名稱',
      th_del_title: '刪除此題材組？',
      th_create: '新增題材', th_save: '儲存題材', th_done1: '✓ 題材已儲存', th_deleted: '✓ 題材已刪除',
      th_row_shoot: '○ 可拍',
      qv_month_note: '非適用月份',
      del_title: '刪除此私人點？', del_warn: '資料保留 30 天：30 日內在同一座標重新新增會直接復活（不重抓）。',
      del_confirm: '🗑 刪除私人點', del_cancel: '取消',
      nl1: '登入後才能使用私人點', nl2: '新增／編輯私人景點是會員功能；私人點只出現在你的帳號。',
      login_cta: '登入以繼續', close: '關閉',
      sem_cloud: '雲量', sem_fog: '霧', sem_rain: '雨',
      ai_hint: '用一句話描述你要的拍攝條件（AI 只翻譯成條件，不判斷好壞）', ai_ph: '例如：清晨六點前要有雲海，不要下雨，風要小，能見度要好', ai_btn: '解析', ai_working: '解析中…', ai_done: '✓ AI 建議（信賴度 {c}%）——請確認後再送出', ai_conflict: '⚠ AI 未套用任何值：{m}', ai_fail: '解析失敗，請手動設定。',
      geo_btn: '📍 使用我的目前位置', geo_note: '為何需要位置：僅用於填入此新景點的座標，不會追蹤你的行蹤。', geo_working: '取得位置中…',
      wt_fixed: '固定時段', wt_bs: '日出前（每日動態）', wt_as: '日出後（每日動態）', wt_bd: '日落前（每日動態）', wt_ads: '日落後（每日動態）',
      win_off: '錨點偏移（分鐘，可負）', win_add2: '＋ 加第二段', win_rm: '移除此段', win_hint: '錨點型以當日實際日出／日落動態展開，冬天夏天不同',
      geo_denied: '無法取得位置：定位權限被拒絕。請改用點圖落釘或直接鍵入經緯度。', geo_timeout: '取得位置逾時。請改用點圖落釘或直接鍵入經緯度。', geo_error: '無法取得位置。請改用點圖落釘或直接鍵入經緯度。',
      copy_genre: '複製官方題材改（起點）', copy_genre_none: '不複製', copy_genre_hint: '選一個官方題材當起點，再微調單一參數',
      adv_toggle: '進階：原始數值輸入', p_lowmin: '低雲下限 ≥%（越多越好）', win_span: '窗長（分鐘，留空＝整段動態）',
      lat_lng: 'lat/lng', elev_m: 'm',
    },
    'en': {
      priv_badge: 'Private', v_all: 'All sources', v_official: 'Official', v_private: 'Private',
      wx_no_subject: 'No subject set', wx_no_subject_note: 'No subject is attached to this place, so there is no shooting verdict. Local weather below.',
      wx_vis: 'Visibility', wx_temp: 'Temp', wx_wx: 'Weather',
      wmo_clear: 'Clear', wmo_mostly_clear: 'Mostly clear', wmo_partly: 'Partly cloudy', wmo_overcast: 'Overcast',
      wmo_fog: 'Fog', wmo_drizzle: 'Drizzle', wmo_rain: 'Rain', wmo_snow: 'Snow', wmo_showers: 'Showers',
      wmo_snow_showers: 'Snow showers', wmo_thunder: 'Thunderstorm',
      add_btn: 'Add custom place', quota_lbl: 'Custom places', quota_owner: 'Unlimited',
      count_fmt: '{n} official places + your {m} custom places',
      count_fmt_zero: '{n} official places (no custom places yet)',
      tier_rec: '✓ Recommended', tier_shoot: '○ Shootable', tier_no: '✗ Not recommended', tier_pending: '⏳ Queued',
      trial_expired: 'Trial ended', trial_note: 'Evaluation stopped (data kept)', trial_cta: 'Upgrade to Premium to resume',
      deferred_note: 'Created · weather data updates tomorrow',
      m_edit: '✎ Edit', m_cc: '🎞 Subject & conditions', m_del: '🗑 Delete',
      m_refetch: '🔄 Refetch independently',
      share_one: 'Shares data with {n}', share_many: 'Shares data with {n} +{c} more',
      refetch_done: 'Detached from the shared group — solo refetch queued (counts as 1 quota point).',
      add_title: 'Add a custom place', add_edit_title: 'Edit custom place', add_sub: 'Name → pin on map → auto elevation/timezone',
      qd_name: 'Name', qd_name_ph: 'e.g. My rooftop terrace, Jiaoxi', qd_pin: 'Pin on map (click to drop, or type lat/lng)',
      qd_pin_hint: 'Any lat/lng worldwide (oceans/poles included); drag the pin or click the map — two-way sync with lat/lng',
      pin_map_loading: 'Loading basemap… (falls back to the grid mode if it fails)',
      ro_elev: 'Elevation (auto DEM)', ro_tz: 'Timezone (auto)', ro_pending: 'auto-filled after pinning',
      ro_elev_outlier: 'Elevation outlier (outside −450…8,849 m) — check the coordinates',
      create: 'Create place', update: 'Save changes',
      reason_name: 'Enter a place name first', reason_pin: 'Pin on the map or enter lat/lng first',
      done1: '✓ Place created', done1_edit: '✓ Saved', done_deferred: 'Created · weather data updates tomorrow (honest daily-fetch queue)',
      cc_title: 'Subject & custom conditions', cc_sub: 'Custom conditions',
      p_low: 'Low-cloud threshold (%)', p_mid: 'Mid-cloud threshold (%)', p_high: 'High-cloud threshold (%)', p_precip: 'Precip cap (mm/h)',
      p_vis: 'Visibility floor (km)', p_wind: 'Wind cap (m/s)', p_window: 'Time window', p_lead: 'Lead time (min)',
      p_months: 'Applicable months', p_months_hint: 'None selected = all year; when set, only those months are evaluated (the cron honours the month window)',
      qv_title: 'Forecast quick view', qv_quick: 'If I go now', qv_days: '8-day outlook', qv_no_data: '─',
      qv_no_data_note: 'No data for this day yet (data covers about the next 2 days)', qv_subjects: 'Per-subject verdicts',
      qv_subject_custom: 'Custom conditions', qv_general: 'Shootable', qv_general_base: 'General baseline', qv_entry: '🎞 Subjects',
      qv_load_fail: 'Forecast data is temporarily unavailable — the fetch may still be queued (updates tomorrow).',
      qv_gen: '{n}/{t} hours met',
      qv_win_passed: 'windows passed · still shootable today',
      cond_n: 'Conditions ×{n}', cond_required: 'Required conditions',
      cc_prev: 'Summary: ', cc_prev_none: '(nothing tuned = general baseline)', cc_submit: 'Apply to this place',
      cc_done1: '✓ Conditions applied', cc_none: '(general baseline only)',
      // patch-8: theme list manager (multiple condition groups per place)
      th_title: 'Subject & conditions', th_sub: 'Subject groups', th_add: '＋ Add a group', th_cap_note: 'Cap of 5 groups reached (delete one to add more)',
      th_empty: 'No subject group attached yet — this place is judged by the general baseline.', th_count: '{n}/{c} groups',
      th_name: 'Group name', th_name_ph: 'e.g. Dawn cloud-sea window', th_name_required: 'Enter a group name first',
      th_del_title: 'Delete this group?',
      th_create: 'Add group', th_save: 'Save group', th_done1: '✓ Group saved', th_deleted: '✓ Group deleted',
      th_row_shoot: '○ Shootable',
      qv_month_note: 'Not an applicable month',
      del_title: 'Delete this custom place?', del_warn: 'Data is kept 30 days: re-adding the same coordinates within 30 days revives it (no new fetch).',
      del_confirm: '🗑 Delete place', del_cancel: 'Cancel',
      nl1: 'Log in to use custom places', nl2: 'Adding / editing is member-only; places appear only on your account.',
      login_cta: 'Log in to continue', close: 'Close',
      sem_cloud: 'Cloud', sem_fog: 'Fog', sem_rain: 'Rain',
      ai_hint: 'Describe the shot you want in one sentence (the AI only translates it into conditions — it never judges)', ai_ph: 'e.g. cloud sea before 06:00, no rain, light wind, good visibility', ai_btn: 'Parse', ai_working: 'Parsing…', ai_done: '✓ AI suggestion (confidence {c}%) — review, then submit', ai_conflict: '⚠ The AI applied nothing: {m}', ai_fail: 'Parsing failed — please set the conditions manually.',
      geo_btn: '📍 Use my current location', geo_note: 'Why we need it: only to fill in this place’s coordinates — your movements are never tracked.', geo_working: 'Getting your location…',
      wt_fixed: 'Fixed span', wt_bs: 'Before sunrise (daily dynamic)', wt_as: 'After sunrise (daily dynamic)', wt_bd: 'Before sunset (daily dynamic)', wt_ads: 'After sunset (daily dynamic)',
      win_off: 'Anchor offset (minutes, may be negative)', win_add2: '＋ Add a second span', win_rm: 'Remove this span', win_hint: 'Anchor spans expand with each day\u2019s REAL sunrise/sunset — winter and summer differ',
      geo_denied: 'Could not get your location: permission denied. Please pin on the map or type lat/lng manually.', geo_timeout: 'Getting your location timed out. Please pin on the map or type lat/lng manually.', geo_error: 'Could not get your location. Please pin on the map or type lat/lng manually.',
      copy_genre: 'Copy an official genre template (starter)', copy_genre_none: 'No copy', copy_genre_hint: 'Pick an official genre as the starting point, then tweak a single parameter',
      adv_toggle: 'Advanced: raw numeric inputs', p_lowmin: 'Low-cloud floor ≥% (the more the better)', win_span: 'Span (minutes; empty = full dynamic span)',
      lat_lng: 'lat/lng', elev_m: 'm',
    },
    'ja': {
      priv_badge: '自作', v_all: 'すべて', v_official: '公式', v_private: '自作',
      wx_no_subject: '題材が未設定', wx_no_subject_note: 'このスポットには題材がないため、撮影判定は行いません。以下は現地の天気です。',
      wx_vis: '視程', wx_temp: '気温', wx_wx: '天気',
      wmo_clear: '晴れ', wmo_mostly_clear: '晴れ時々曇り', wmo_partly: '曇り', wmo_overcast: '本曇り',
      wmo_fog: '霧', wmo_drizzle: '霧雨', wmo_rain: '雨', wmo_snow: '雪', wmo_showers: 'にわか雨',
      wmo_snow_showers: 'にわか雪', wmo_thunder: '雷雨',
      add_btn: '自作スポットを追加', quota_lbl: '自作スポット', quota_owner: '無制限',
      count_fmt: '公式 {n} スポット＋あなたの自作 {m} スポット',
      count_fmt_zero: '公式 {n} スポット（自作スポットはまだありません）',
      tier_rec: '✓ 推薦', tier_shoot: '○ 撮影可', tier_no: '✗ 非推奨', tier_pending: '⏳ 待機中',
      trial_expired: 'トライアル期限切れ', trial_note: '評価停止中（データは保持）', trial_cta: 'Premiumへアップグレードで再開',
      deferred_note: '作成済み・気象データは明日更新',
      m_edit: '✎ 編集', m_cc: '🎞 題材・条件', m_del: '🗑 削除',
      m_refetch: '🔄 個別に再取得',
      share_one: '{n} とデータ共有', share_many: '{n} ほか{c}件とデータ共有',
      refetch_done: '共有グループを解除し、単独再取得を待ち列に入れました（1ポイント消費）。',
      add_title: '自作スポットを追加', add_edit_title: '自作スポットを編集', add_sub: '名称 → ピン配置 → 標高／タイムゾーン自動',
      qd_name: '名称', qd_name_ph: '例：自宅ベランダの展望（礁渓）', qd_pin: '地図でピン配置（クリック、または緯度経度を直接入力）',
      qd_pin_hint: '全球任意の緯度経度（海洋・極域も可）；ピンをドラッグまたは地図クリック、緯度経度と双方向同期',
      pin_map_loading: 'ベースマップ読み込み中…（失敗時はグリッドに切替）',
      ro_elev: '標高（DEM 自動）', ro_tz: 'タイムゾーン（自動）', ro_pending: 'ピン配置後に自動入力',
      ro_elev_outlier: '標高が異常（−450〜8,849 m 外）— 座標を確認してください',
      create: '作成', update: '変更を保存',
      reason_name: '先に名称を入力してください', reason_pin: 'ピン配置か緯度経度の入力が必要です',
      done1: '✓ 作成しました', done1_edit: '✓ 保存しました', done_deferred: '作成済み・気象データは明日更新（毎日取得枠の正直な待機）',
      cc_title: '題材・カスタム条件', cc_sub: 'カスタム条件',
      p_low: '低雲しきい値（%）', p_mid: '中雲しきい値（%）', p_high: '高雲しきい値（%）', p_precip: '降水上限（mm/h）',
      p_vis: '視程下限（km）', p_wind: '風速上限（m/s）', p_window: '時間帯', p_lead: '通知の余裕（分）',
      p_months: '適用月', p_months_hint: '未選択＝通年；選択するとその月のみ判定（cron も月窓を尊重）',
      qv_title: '予報クイックビュー', qv_quick: '今すぐ行くと', qv_days: '8日間の概況', qv_no_data: '─',
      qv_no_data_note: 'この日はまだデータなし（データは今後約2日分）', qv_subjects: '題材別判定',
      qv_subject_custom: 'カスタム条件', qv_general: '撮影可', qv_general_base: '一般基準', qv_entry: '🎞 題材',
      qv_load_fail: '予報データを取得できません——取得待ちの可能性があります（明日更新）。',
      qv_gen: '{n}/{t} 時間適合',
      qv_win_passed: '撮影窓は終了・本日は撮影可',
      cond_n: '条件 ×{n}', cond_required: '成立条件',
      cc_prev: 'サマリー：', cc_prev_none: '（未調整＝一般基準）', cc_submit: 'このスポットに適用',
      cc_done1: '✓ 条件を適用しました', cc_none: '（一般基準のみ）',
      // patch-8: theme list manager (multiple condition groups per place)
      th_title: '題材・条件', th_sub: '題材グループ', th_add: '＋ 題材を追加', th_cap_note: '上限5件に達しました（削除後に追加できます）',
      th_empty: '題材グループはまだありません——一般基準で判定します。', th_count: '{n}/{c} 件',
      th_name: '題材名', th_name_ph: '例：明け方の雲海窓', th_name_required: '先に題材名を入力してください',
      th_del_title: 'この題材グループを削除？',
      th_create: '題材を追加', th_save: '保存', th_done1: '✓ 保存しました', th_deleted: '✓ 削除しました',
      th_row_shoot: '○ 撮影可',
      qv_month_note: '適用月外',
      del_title: 'この自作スポットを削除？', del_warn: 'データは 30 日保持：30 日以内に同じ座標を再追加すると復活します（再取得なし）。',
      del_confirm: '🗑 削除する', del_cancel: 'キャンセル',
      nl1: '自作スポットにはログインが必要', nl2: '追加／編集は会員機能；自作スポットは自分のアカウントにのみ表示されます。',
      login_cta: 'ログインして続行', close: '閉じる',
      sem_cloud: '雲量', sem_fog: '霧', sem_rain: '雨',
      ai_hint: '撮りたい条件を一文で説明（AIは条件への翻訳のみ・良し悪しは判断しない）', ai_ph: '例：6時までに雲海。雨は嫌。風は弱め。視程は良い', ai_btn: '解析', ai_working: '解析中…', ai_done: '✓ AI提案（信頼度 {c}%）— 確認してから送信してください', ai_conflict: '⚠ AIは未適用：{m}', ai_fail: '解析に失敗しました。手動で設定してください。',
      geo_btn: '📍 現在地を使う', geo_note: '位置情報の使い道：このスポットの座標を入力するためだけ。現在地は追跡しません。', geo_working: '現在地を取得中…',
      wt_fixed: '固定時間帯', wt_bs: '日の出前（毎日動的）', wt_as: '日の出後（毎日動的）', wt_bd: '日の入前（毎日動的）', wt_ads: '日の入後（毎日動的）',
      win_off: 'アンカーオフセット（分・負可）', win_add2: '＋ 2つ目を追加', win_rm: 'この枠を削除', win_hint: 'アンカーは当日の実際の日の出入りから毎日展開（季節で変わる）',
      geo_denied: '位置を取得できませんでした：権限が拒否されました。地図クリックまたは手動入力をご利用ください。', geo_timeout: '位置の取得がタイムアウトしました。地図クリックまたは手動入力をご利用ください。', geo_error: '位置を取得できませんでした。地図クリックまたは手動入力をご利用ください。',
      copy_genre: '公式題材をコピーして改造（出発点）', copy_genre_none: 'コピーしない', copy_genre_hint: '公式題材を出発点に選び、1つのパラメータだけ調整します',
      adv_toggle: '高度：生の数値入力', p_lowmin: '低雲下限 ≥%（多いほうが良い）', win_span: '枠の長さ（分・空欄＝全体）',
      lat_lng: 'lat/lng', elev_m: 'm',
    },
  };

  var state = { member: null, data: null, view: 'all', loading: false, overlay: null, pin: null, editing: null, menuPlace: null, menuTrigger: null,
    pinMapToken: 0, miniMap: null, miniMapReady: false, miniMapMarker: null, pinSource: null };
  var els = {};

  function t() { return T[currentLang()] || T['zh-TW']; }
  function currentLang() {
    try {
      var sel = document.getElementById('lang-select');
      if (sel && LANGS.indexOf(sel.value) >= 0) return sel.value;
      var v = localStorage.getItem('chaselights_lang');
      if (v && LANGS.indexOf(v) >= 0) return v;
    } catch (e) { /* storage blocked */ }
    return 'zh-TW';
  }
  function esc(v) { return String(v == null ? '' : v).replace(/[&<>"']/g, function (ch) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]); }); }
  // fetch with a test seam: window.__clcpFetch(path, opts) replaces the real
  // network in the headless harness (credentials/same-origin semantics kept).
  function api(path, opts) {
    opts = opts || {};
    opts.credentials = 'same-origin';
    opts.cache = 'no-store';
    if (typeof window.__clcpFetch === 'function') return Promise.resolve(window.__clcpFetch(path, opts));
    return fetch(path, opts);
  }
  function toast(msg) {
    if (!els.toast) { els.toast = document.createElement('div'); els.toast.className = 'cl-cp-toast'; els.toast.setAttribute('role', 'status'); document.body.appendChild(els.toast); }
    els.toast.textContent = typeof msg === 'string' ? msg : (msg && msg[currentLang()]) || '';
    els.toast.classList.add('show');
    clearTimeout(toast._tm);
    toast._tm = setTimeout(function () { els.toast.classList.remove('show'); }, 6000);
  }

  // ───────────────────────────── bootstrap ─────────────────────────────
  function ensureHosts() {
    // quota chip + ＋ button + honest count live in the discovery row
    var row = document.querySelector('.discovery-row');
    if (row && !els.quota) {
      els.quota = document.createElement('span'); els.quota.className = 'cl-cp-quota-chip'; els.quota.hidden = true;
      els.addBtn = document.createElement('button'); els.addBtn.type = 'button'; els.addBtn.className = 'cl-cp-add-btn';
      els.addBtn.innerHTML = '<b>＋</b> <span class="cl-cp-add-label"></span>';
      els.addBtn.addEventListener('click', startAdd);
      els.count = document.createElement('span'); els.count.className = 'cl-cp-count'; els.count.hidden = true;
      row.appendChild(els.quota); row.appendChild(els.addBtn); row.appendChild(els.count);
    }
    // view tabs AFTER the tier tab bar (never inside #tier-tabs — app.js
    // wipes that host on every render)
    var tierTabs = document.getElementById('tier-tabs');
    if (tierTabs && tierTabs.parentNode && !els.viewBar) {
      els.viewBar = document.createElement('div'); els.viewBar.className = 'cl-cp-view-bar';
      els.viewBar.setAttribute('role', 'tablist');
      tierTabs.parentNode.insertBefore(els.viewBar, tierTabs.nextSibling);
    }
    if (!els.overlay) {
      els.overlay = document.createElement('div'); els.overlay.className = 'cl-cp-overlay';
      els.overlay.innerHTML = '<div class="cl-cp-modal"></div>';
      els.overlay.addEventListener('click', function (e) { if (e.target === els.overlay) closeOverlay(); });
      document.body.appendChild(els.overlay);
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeOverlay(); });
    }
  }

  // patch-5: each modal opens at the TOP — the overlay is its own scroller and
  // a previous tall modal's scrollTop otherwise persists, clipping the short
  // edit modal's first fields above the viewport. Body scroll is locked while
  // a modal is open (the page must not scroll behind the overlay).
  function openOverlay(html, extraCls) { ensureHosts(); var m = els.overlay.querySelector('.cl-cp-modal'); m.classList.remove('cl-cp-qv-modal'); if (extraCls) m.classList.add(extraCls); m.innerHTML = html; els.overlay.classList.add('open'); els.overlay.scrollTop = 0; m.scrollTop = 0; document.body.classList.add('cl-cp-lock'); }
  function closeOverlay() {
    if (!els.overlay) return;
    els.overlay.classList.remove('open');
    document.body.classList.remove('cl-cp-lock');
    teardownMiniMap(); // patch-4: the GL context must not leak across modals
  }

  // ───────────────────────────── data ─────────────────────────────
  function refresh() {
    if (!state.member) { state.data = null; state.aiEnabled = undefined; render(); return; }
    if (state.loading) return;
    state.loading = true;
    aiParseConfigCheck();
    api(API).then(function (res) {
      if (res.status === 401) { state.data = null; render(); return; }
      if (!res.ok) { state.loading = false; scheduleRetry(); return; } // 429/5xx transient — keep state
      return res.json().then(function (body) { state.data = body; state.loading = false; render(); });
    }).catch(function () { state.loading = false; scheduleRetry(); });
  }
  var retryAttempt = 0, retryTimer = 0;
  function scheduleRetry() { // CL-API-07: 429/5xx are transient; backoff 1s→2s→4s, max 3
    if (retryAttempt >= 3) return;
    var delay = 1000 * Math.pow(2, retryAttempt++);
    clearTimeout(retryTimer);
    retryTimer = setTimeout(function () { retryAttempt === 3 ? null : refresh(); }, delay);
  }

  // ───────────────────────────── render ─────────────────────────────
  function officialCardCount() {
    // CL-UI-45 (counts): the 來源 (source) tabs counted DOM cards, so after a
    // region switch they kept the PREVIOUS region's number (the owner read the
    // TW total 126 on the Japan tab, whose real catalog is 94). Prefer app.js's
    // single render publish — same rows, same pass as the list and the tier
    // tabs — and fall back to the DOM only when no publish exists (standalone
    // harness / script-only page).
    var stats = (typeof window !== 'undefined') ? window.CLListStats : null;
    var sel = document.getElementById('country-select');
    var wantRegion = sel && sel.value ? sel.value : null;
    if (stats && typeof stats.official === 'number' && (!wantRegion || stats.region === wantRegion)) {
      // Same region as the selector: the publish is the truth — including the
      // loading publish (a region switch in flight shows 0, never the previous
      // country's cards).
      return stats.loading ? 0 : stats.official;
    }
    var c = document.getElementById('spots-container');
    return c ? c.querySelectorAll('.card:not(.cl-cp-card)').length : 0;
  }
  function privatePlaces() { return (state.data && state.data.places) || []; }
  // ───── patch-6: private points ride the OFFICIAL card renderer + filter
  // pipeline (owner ruling). The official app.js owns the card anatomy and
  // the tier tabs/chip counts/filters; this module only CONVERTS the stored
  // custom-set evaluations into the official pipeline's INPUTS:
  //   cpCardInfo(p)   → synthetic subject-cards rows (tree) + synthetic
  //                     evaluation days, registered via registerSyntheticRows
  //                     (so v2PlaceForSpot → v2BestForSpot → v2SubjectCardRow
  //                     → clui66SpotTier decide the verdict ONCE — the SAME
  //                     truth the card badge, the tier-tab counts and the
  //                     filters consume; never a second judgment source),
  //   cardRows()      → {spot, metric} rows for filterAndRender (registered
  //                     lazily from the CURRENT state.data, so chip counts
  //                     and cards can never come from different data
  //                     versions),
  //   createCard      → the official createSpotCard via the CLForecastRenderers
  //                     bridge (identical anatomy; ◉私人 badge + forecast-popup
  //                     targets are the ONLY private differences).
  // Special states (trial-expired / pending) keep their honest dedicated cards
  // and appear only under the 全部 tier tab (no verdict exists — same rule as
  // official noeval spots).
  function bridgeActive() {
    return !!(window.CLForecastRenderers && window.CLForecastRenderers.createCard &&
              window.CLForecastRenderers.localDate);
  }
  function isSpecialCard(p) {
    return p.status === 'trial_expired' || (p.evaluation || {}).tier === 'pending' || cpHasNoThemes(p);
  }
  function cpActiveTier() {
    var el = document.querySelector('#tier-tabs .tier-tab.active');
    return (el && el.getAttribute('data-tier')) || 'recommend';
  }
  // CL-UI-122: the 私人 view keeps the official tier tab — when that tab has no
  // private place at all (e.g. the only private point is ✗不宜 while ✓推薦 is
  // active) the list rendered empty and the owner saw 「私人 1」 with no card.
  // Fall back to the 全部 tier so the private points are always reachable.
  function cpTierHasPrivate(tierKey) {
    if (tierKey === 'all') return true;
    var map = { recommend: 'rec', shootable: 'shoot', not_recommended: 'no' };
    var want = map[tierKey];
    if (!want) return false;
    return privatePlaces().some(function (p) { return ((p.evaluation || {}).tier) === want; });
  }
  function cpEnsurePrivateTier() {
    if (state.view !== 'private' || !state.data) return;
    var act = cpActiveTier();
    if (act === 'all' || cpTierHasPrivate(act)) return;
    var allTab = document.querySelector('#tier-tabs .tier-tab[data-tier="all"]');
    if (allTab && !allTab.classList.contains('active')) allTab.click();
  }
  function cpStamps(winStr) {
    var out = [], rx = /(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})/g, m, s = String(winStr || '');
    while ((m = rx.exec(s))) out.push({ date: m[1], hhmm: m[2] });
    return out;
  }
  function cpSynthMetric() {
    return { theme: 'custom', temp: null, cloud_base_agl: null, sun_azimuth: null, sun_elevation: null,
      moon_illumination: null, opportunity_id: '', opportunity_name: '', indicator_key: '',
      no_viable_opportunity: false, research_pending: false };
  }
  function cpCardInfo(p) {
    var br = window.CLForecastRenderers;
    if (!br || !br.localDate) return null;
    var ev = p.evaluation || {};
    if (ev.tier === 'pending') return null;
    var tz = p.timezone || 'Asia/Taipei';
    var today = br.localDate(tz, 0);
    var groups = cpPopupGroups(p);
    var tree = {}, anyShoot = null, noReasons = [], noEntries = [], shootEntries = [];
    groups.forEach(function (g) {
      var ge = g.eval || {};
      if (ge.tier === 'rec') {
        var st = cpStamps(ge.window)[0];
        if (!st) return; // honest: window not yet resolvable → no synthetic row
        var node = tree[st.date] = tree[st.date] || { tier: 'recommend', good_hours: [], suitable: [] };
        node.good_hours.push(st.hhmm);
        // CL-CI-38: the card per-group row carries the WORKER's stored group
        // verdict (patch-8 owner-ruled anatomy) — badge + name + full window
        // stamp, rendered by the official clSubjectRowLine via cpTierCls.
        node.suitable.push({ subject_short: { 'zh-TW': themeDisplayName(g) }, window: [st.hhmm], cc: g.cond || null,
          stamp: ge.window, cpTierCls: 'cl-cp-tier-rec', cpMark: '✓', cpRowName: true });
      } else if (ge.tier === 'shoot') {
        if (!anyShoot) anyShoot = ge;
        var st2 = cpStamps(ge.window)[0];
        if (st2) shootEntries.push({ subject_short: { 'zh-TW': themeDisplayName(g) }, window: [st2.hhmm], cc: g.cond || null,
          stamp: ge.window, cpTierCls: 'cl-cp-tier-shoot', cpMark: '○', cpTail: t().th_row_shoot, cpRowName: true });
      }
      else if (ge.tier === 'no' && ge.reason) {
        noReasons.push(ge.reason);
        noEntries.push({ subject_short: { 'zh-TW': themeDisplayName(g) }, window: [],
          cpTierCls: 'cl-cp-tier-no', cpMark: '✗', cpTail: ge.reason, cpRowName: true });
      }
    });
    var keys = Object.keys(tree).sort();
    var days;
    if (keys.length) {
      // curated ✓ windows win (same aggregate rule as the worker's
      // aggregateEvaluation: any ✓ subject counts the place into ✓推薦)
      days = keys.map(function (d) {
        tree[d].good_hours.sort();
        return { local_date: d, state: 'GUIDANCE_SATISFIED', good_hours: tree[d].good_hours.slice(),
          hour_counts: { GUIDANCE_SATISFIED: tree[d].good_hours.length } };
      });
    } else if (anyShoot) {
      // ○可拍 — the general floor passes with no curated window (CL-UI-71
      // fallback anatomy renders the official 「○ 可拍」 row)
      var sh = cpStamps(anyShoot.window)[0];
      var hours = sh ? [sh.hhmm] : [];
      tree[today] = { tier: 'shootable', good_hours: hours, suitable: shootEntries.slice() };
      tree[today].suitable.push({ subject_short: { 'zh-TW': t().qv_general }, window: hours.slice(),
        stamp: anyShoot.window || null, cpTierCls: 'cl-cp-tier-shoot', cpMark: '○', cpRowName: true });
      days = [{ local_date: today, state: hours.length ? 'GUIDANCE_SATISFIED' : 'UNFAVORABLE',
        good_hours: hours, hour_counts: { GUIDANCE_SATISFIED: hours.length } }];
    } else {
      // ✗不宜 — the short reason (dominant fail word) rides the row as
      // tier_reason; the official card anatomy renders 「✗ 不宜 · 雨」
      var reason = noReasons[0] || ev.reason || '';
      tree[today] = { tier: 'not_recommended', tier_reason: reason ? { 'zh-TW': reason } : null, good_hours: [], suitable: noEntries };
      days = [{ local_date: today, state: 'UNFAVORABLE', good_hours: [], hour_counts: {} }];
    }
    br.registerSyntheticRows(p.id, tree, {}, days);
    var spot = {
      spot_id: p.id,
      name_i18n: { 'zh-TW': p.name, 'en': p.name, 'ja': p.name }, name_local: p.name,
      category: '__private__', admin_areas: [],
      lat: Number(p.lat), lon: Number(p.lng),
      elevation: p.elevation != null ? Number(p.elevation) : null,
      timezone: tz, scenes: [],
      opportunities: [{ opportunity_id: 'cp:' + p.id, genre_template: 'custom', days: days, live: {} }],
      navigation_target: { status: 'verified', lat: Number(p.lat), lon: Number(p.lng) },
    };
    return { spot: spot, metric: cpSynthMetric() };
  }
  // the interaction targets + badge the official renderer needs for private
  // cards (card body/題材 both open the private forecast popup — its quick
  // view + strip + subject rows are the private place modal)
  function cpCardOpts(p) {
    return {
      private: true,
      badgeHtml: '<span class="cl-cp-priv-badge">◉ ' + esc(t().priv_badge) + '</span>',
      openCard: function () { forecastModal(p); },
      openPlace: function () { forecastModal(p); },
      // patch-6: the ⋯ menu trigger rides the official card-header-actions
      // row — appended AFTER the official anatomy mounts (postMount hook),
      // same portaled-menu wiring as the special-state cards (patch-3).
      postMount: function (card) {
        var act = card.querySelector('.card-header-actions');
        if (act && !card.querySelector('.cl-cp-more')) {
          var more = document.createElement('button');
          more.type = 'button';
          more.className = 'cl-cp-more';
          more.setAttribute('aria-label', '⋯');
          more.setAttribute('aria-haspopup', 'menu');
          more.setAttribute('aria-expanded', 'false');
          more.textContent = '⋯';
          act.appendChild(more);
          more.addEventListener('click', function (e) {
            e.stopPropagation();
            var m = ensureMenu();
            var wasOpen = m.classList.contains('open') && state.menuPlace && state.menuPlace.id === p.id;
            closeMenu();
            if (!wasOpen) openMenuFor(p, more);
          });
        }
        // CL-CI-38: the patch-3 coord line (lat/lng · elevation · GMT±n) rides
        // the bridge card too — the official anatomy has no coord row, and a
        // private point's coordinates are the card's navigation info.
        if (!card.querySelector('.cl-cp-coord')) {
          var metaEl = card.querySelector('.card-secondary-meta');
          if (metaEl) {
            var coord = document.createElement('div');
            coord.className = 'cl-cp-coord';
            var cpTz = p.timezone || 'Asia/Taipei';
            var gmt = 'GMT';
            try {
              var parts = new Intl.DateTimeFormat('en-US', { timeZone: cpTz, timeZoneName: 'shortOffset' }).formatToParts(new Date());
              var tp = parts.filter(function (x) { return x.type === 'timeZoneName'; })[0];
              if (tp && tp.value) gmt = tp.value;
            } catch (e3) { /* honest GMT without offset */ }
            coord.textContent = Number(p.lat).toFixed(3) + ', ' + Number(p.lng).toFixed(3) +
              (p.elevation != null ? ' · ' + Number(p.elevation) + ' m' : '') +
              (p.timezone ? ' · ' + gmt : '');
            metaEl.appendChild(coord);
          }
        }
        // CL-APP-08: shared-fetch tag — the official anatomy carries it too
        // (gray identity, after the meta rows / before the footer tools).
        var share = shareTagText(p.sharing, currentLang());
        if (share && !card.querySelector('.cl-cp-share-tag')) {
          var meta = card.querySelector('.card-secondary-meta') || card.querySelector('.shooting-summary');
          if (meta) {
            var tag = document.createElement('div');
            tag.className = 'cl-cp-share-tag';
            tag.innerHTML = '<span class="st-ic">🔗</span><span class="st-txt"></span>';
            tag.querySelector('.st-txt').textContent = share;
            meta.insertAdjacentElement('afterend', tag);
          }
        }
      },
    };
  }
  // the rows app.js merges into rowsAll — one filter pipeline for both lists
  function cardRows() {
    var out = [];
    if (!state.member || !state.data) return out;
    privatePlaces().forEach(function (p) {
      if (isSpecialCard(p)) return;
      var info = cpCardInfo(p);
      if (!info) return;
      out.push({ spot: info.spot, metric: info.metric, cp: true, cpOpts: cpCardOpts(p) });
    });
    return out;
  }

  function render() {
    ensureHosts();
    var places = privatePlaces();
    var lang = currentLang();
    if (els.addBtn) els.addBtn.querySelector('.cl-cp-add-label').textContent = t().add_btn;
    try { document.body.setAttribute('data-cp-view', state.view); } catch (e) { /* no body yet */ }
    // quota chip
    if (state.data) {
      els.quota.hidden = false;
      var q = state.data.quota || {};
      var capTxt = (q.cap === null || q.cap === undefined) ? t().quota_owner : (q.used + '/' + q.cap);
      var tierTxt = state.data.level === 'owner' ? 'Owner' : state.data.level === 'paid' ? 'Premium'
        : (state.data.level === 'free-expired' ? t().trial_expired : 'Free');
      els.quota.innerHTML = '📍 <span>' + esc(t().quota_lbl) + '</span> <b>' + esc(capTxt) + '</b> · <span>' + esc(tierTxt) + '</span>';
      if (state.data.degraded && state.data.degradedMessage) toast(state.data.degradedMessage);
    } else { els.quota.hidden = true; }
    // count line — identity: 全部 = 官方 + 私人 (never mis-added)
    var n = officialCardCount(), m = places.length;
    if (state.member) {
      els.count.hidden = false;
      els.count.innerHTML = m ? esc(t().count_fmt.replace('{n}', n).replace('{m}', m)) : esc(t().count_fmt_zero.replace('{n}', n));
    } else { els.count.hidden = true; }
    // view tabs
    if (els.viewBar) {
      var counts = { all: n + m, official: n, private: m };
      var mk = function (key, label, cls) {
        return '<button type="button" class="cl-cp-view-tab ' + cls + (state.view === key ? ' sel' : '') + '" data-cp-view="' + key + '" role="tab" aria-selected="' + (state.view === key) + '"><span>' + esc(label) + '</span> <span class="n">' + esc(counts[key]) + '</span></button>';
      };
      els.viewBar.innerHTML = mk('all', t().v_all, '') + mk('official', t().v_official, '') + mk('private', t().v_private, 't-priv ');
      if (!els.viewBar._wired) {
        els.viewBar._wired = true;
        els.viewBar.addEventListener('click', function (e) {
          var b = e.target.closest('.cl-cp-view-tab'); if (!b) return;
          state.view = b.getAttribute('data-cp-view');
          try { localStorage.setItem(VIEW_KEY, state.view); } catch (err) { /* storage blocked */ }
          render();
        });
      }
    }
    renderPrivateCards(places);
    // CL-UI-122: a private view whose active tier holds no private point must
    // not render an empty list — fall back to the 全部 tier.
    cpEnsurePrivateTier();
    // patch-6: every data/view/language change re-runs the OFFICIAL filter
    // pass — the tier-tab counts, the tier/subject filters and the private
    // cards re-derive from THIS state.data in one pass (same data version).
    try { document.dispatchEvent(new CustomEvent('chaselights:cp-data')); } catch (e) { console.warn('P6DISPATCH-ERR', e && e.message, e && e.stack); }
  }
  function restoreSavedView() {
    try {
      var saved = localStorage.getItem(VIEW_KEY);
      if (saved && ['all', 'official', 'private'].indexOf(saved) >= 0) state.view = saved;
    } catch (e) { /* storage blocked */ }
  }

  function appendPrivateCards(places) {
    var container = document.getElementById('spots-container');
    if (!container) return;
    // patch-6: app.js renders the NORMAL private cards (official renderer, no
    // special marker) — this module's own append/sync only manages the
    // special-state cards (data-cp-special) in bridge mode.
    var scope = bridgeActive() ? '.cl-cp-card[data-cp-special]' : '.cl-cp-card';
    var keep = {};
    places.forEach(function (p) { keep[p.id] = true; });
    // remove stale cards
    container.querySelectorAll(scope).forEach(function (card) {
      if (!keep[card.getAttribute('data-cp-id')]) card.remove();
    });
    var existing = {};
    container.querySelectorAll(scope).forEach(function (card) { existing[card.getAttribute('data-cp-id')] = true; });
    places.forEach(function (p) {
      if (existing[p.id]) { updatePrivateCard(p); return; }
      container.appendChild(buildPrivateCard(p));
    });
  }
  function renderPrivateCards(places) {
    if (!places.length || state.view === 'official') {
      document.querySelectorAll('#spots-container .cl-cp-card').forEach(function (card) { card.remove(); });
      return;
    }
    if (bridgeActive()) {
      // patch-6: the official renderer renders the NORMAL cards (cardRows →
      // app.js filterAndRender); this module only appends the special-state
      // cards, and only under the 全部 tier tab — no verdict exists there,
      // the same rule official noeval spots follow.
      var specials = places.filter(isSpecialCard);
      if (cpActiveTier() !== 'all') specials = [];
      appendPrivateCards(specials);
      return;
    }
    appendPrivateCards(places);
  }
  function syncPrivateCards(places) {
    if (bridgeActive()) {
      // same special-only rule as renderPrivateCards; the observer re-runs
      // this after every official rebuild so the set stays exact.
      var specials = places.filter(isSpecialCard);
      if (cpActiveTier() !== 'all') specials = [];
      if (!specials.length) {
        if (containerHasSpecialCards()) { removeSpecialCards(); }
        return;
      }
      appendPrivateCards(specials);
      return;
    }
    // observer-safe incremental sync: same set + same signatures → no DOM write
    var container = document.getElementById('spots-container');
    if (!container) return;
    if (!places.length) {
      if (container.querySelector('.cl-cp-card')) { document.querySelectorAll('#spots-container .cl-cp-card').forEach(function (card) { card.remove(); }); }
      return;
    }
    var cards = container.querySelectorAll('.cl-cp-card');
    var same = cards.length === places.length;
    if (same) {
      for (var i = 0; i < places.length; i++) {
        var c = container.querySelector('.cl-cp-card[data-cp-id="' + CSS.escape(places[i].id) + '"]');
        if (!c || c._cpSig !== JSON.stringify(places[i])) { same = false; break; }
      }
    }
    if (same) return;
    appendPrivateCards(places);
  }

  // special-state card set helpers (bridge mode keeps ONLY these in the DOM)
  var CP_SPECIAL_SEL = '.cl-cp-card[data-cp-special]';
  function containerHasSpecialCards() {
    return !!document.querySelector(CP_SPECIAL_SEL);
  }
  function removeSpecialCards() {
    document.querySelectorAll(CP_SPECIAL_SEL).forEach(function (card) { card.remove(); });
  }

  function tierBadge(p) {
    var ev = p.evaluation || {};
    var map = { rec: ['cl-cp-tier-rec', t().tier_rec], shoot: ['cl-cp-tier-shoot', t().tier_shoot], no: ['cl-cp-tier-no', t().tier_no], pending: ['cl-cp-tier-pending', t().tier_pending] };
    var m = map[ev.tier] || map.pending;
    return '<span class="cl-cp-tier ' + m[0] + '">' + esc(m[1]) + '</span>';
  }
  // patch-8: group display name — the i18n object wins in the current language,
  // falling back to the zh-TW anchor `name` (unreviewed copies never invent words)
  function themeName(g) {
    var i18n = g && g.nameI18n;
    if (i18n && typeof i18n === 'object') {
      var v = i18n[currentLang()] || i18n['zh-TW'] || i18n['en'];
      if (v) return v;
    }
    return (g && g.name) || '';
  }
  // ── patch-9 (owner ruling): the legacy migration named the old single blob
  // 「題材 1」 — a system placeholder that must never reach the UI. A group
  // with NO user-facing name (nameI18n absent) carrying that placeholder falls
  // back to the USER's genre: exact-match the set against the official genre
  // starters (the picker such sets were created from) and use that genre's
  // tri-lingual short name (e.g. 星光窗的夜空 starter → 「星空」); a set that
  // was tweaked beyond the starter reads 「自訂條件」. A user who literally
  // renamed a group to 「題材 1」 (nameI18n present) keeps their name.
  function cpLegacyPlaceholder(g) {
    if (!g) return false;
    var i18n = g.nameI18n;
    if (i18n && typeof i18n === 'object' && Object.keys(i18n).length) return false;
    return String(g.name || '') === '題材 1';
  }
  function themeDisplayName(g) {
    if (cpLegacyPlaceholder(g)) {
      var key = cpStarterKeyFor(g && g.conditions);
      var names = key ? genreShortNames() : null;
      return (names && names[key]) || t().qv_subject_custom;
    }
    return themeName(g);
  }
  // canonical form: lenient defaults never constrain (same rules as
  // cpHourMatches / ccSummary); months sort-joined for stable compare
  function cpCcCanonical(cc) {
    var out = {};
    if (!cc) return out;
    if (cc.cloud_low_max != null && cc.cloud_low_max < 100) out.cloud_low_max = Number(cc.cloud_low_max);
    if (cc.cloud_mid_max != null && cc.cloud_mid_max < 100) out.cloud_mid_max = Number(cc.cloud_mid_max);
    if (cc.cloud_high_max != null && cc.cloud_high_max < 100) out.cloud_high_max = Number(cc.cloud_high_max);
    // patch-5 ⑤: the _min counterpart keys (>0 = actually constraining)
    if (cc.cloud_low_min != null && cc.cloud_low_min > 0) out.cloud_low_min = Number(cc.cloud_low_min);
    if (cc.cloud_mid_min != null && cc.cloud_mid_min > 0) out.cloud_mid_min = Number(cc.cloud_mid_min);
    if (cc.cloud_high_min != null && cc.cloud_high_min > 0) out.cloud_high_min = Number(cc.cloud_high_min);
    if (cc.precip_max_mmh != null && cc.precip_max_mmh < 200) out.precip_max_mmh = Number(cc.precip_max_mmh);
    if (cc.visibility_min_km != null && cc.visibility_min_km > 0) out.visibility_min_km = Number(cc.visibility_min_km);
    if (cc.wind_max_ms != null) out.wind_max_ms = Number(cc.wind_max_ms);
    if (cc.window_start && cc.window_end) { out.window_start = cc.window_start; out.window_end = cc.window_end; }
    if (Array.isArray(cc.months) && cc.months.length) out.months = cc.months.slice().sort(function (a, b) { return a - b; }).join(',');
    if (cc.lead_minutes != null) out.lead_minutes = Number(cc.lead_minutes);
    return out;
  }
  function cpCcSame(a, b) {
    var ca = cpCcCanonical(a), cb = cpCcCanonical(b);
    var ka = Object.keys(ca);
    if (ka.length !== Object.keys(cb).length) return false;
    for (var i = 0; i < ka.length; i++) if (ca[ka[i]] !== cb[ka[i]]) return false;
    return true;
  }
  function cpStarterKeyFor(cc) {
    if (!cc) return null;
    for (var k in CC_GENRE_STARTERS) {
      var s = CC_GENRE_STARTERS[k];
      // patch-5 ⑤: the 'more' starter direction maps to cloud_low_min (the
      // _min counterpart), everything else stays a cloud_low_max seed.
      if (cpCcSame(cc, Object.assign(
        { visibility_min_km: CC_SEMANTIC.fog.values[s.fog], precip_max_mmh: CC_SEMANTIC.rain.values[s.rain] },
        s.cloud === 'more'
          ? { cloud_low_min: CC_SEMANTIC.cloud.values.more }
          : { cloud_low_max: CC_SEMANTIC.cloud.values[s.cloud] },
        {
          window_start: s.window ? s.window[0] : null,
          window_end: s.window ? s.window[1] : null,
          months: Array.isArray(s.months) ? s.months.slice() : null,
        }
      ))) return k;
    }
    return null;
  }
  // patch-6: cpCardRow (the homegrown compact card-row anatomy) is RETIRED —
  // private verdicts render through the OFFICIAL createSpotCard pipeline.
  // CL-APP-08: 「與 ○○○ 共用資料」 label text — one other member name, or
  // the first name + the rest counted. Empty when ungrouped (no tag).
  function shareTagText(sharing, lang) {
    if (!sharing || !sharing.sharedWith || !sharing.sharedWith.length) return '';
    var names = sharing.sharedWith.map(function (m) { return m.name; }).filter(Boolean);
    if (!names.length) return '';
    var L = T[lang] || T['zh-TW'];
    if (names.length === 1) return L.share_one.replace('{n}', names[0]);
    return L.share_many.replace('{n}', names[0]).replace('{c}', names.length - 1);
  }
  function ccSummary(cc, lang) {
    if (!cc) return '';
    var parts = [];
    var L = T[lang] || T['zh-TW'];
    if (cc.cloud_low_max != null && cc.cloud_low_max < 100) parts.push((lang === 'en' ? 'low≤' : lang === 'ja' ? '低雲≤' : '低雲≤') + cc.cloud_low_max + '%');
    if (cc.cloud_mid_max != null && cc.cloud_mid_max < 100) parts.push('中雲≤' + cc.cloud_mid_max + '%');
    if (cc.cloud_high_max != null && cc.cloud_high_max < 100) parts.push('高雲≤' + cc.cloud_high_max + '%');
    // patch-5 ⑤: the 越多越好 direction reads as a floor
    if (cc.cloud_low_min != null && cc.cloud_low_min > 0) parts.push((lang === 'en' ? 'low≥' : '低雲≥') + cc.cloud_low_min + '%');
    if (cc.cloud_mid_min != null && cc.cloud_mid_min > 0) parts.push((lang === 'en' ? 'mid≥' : '中雲≥') + cc.cloud_mid_min + '%');
    if (cc.cloud_high_min != null && cc.cloud_high_min > 0) parts.push((lang === 'en' ? 'high≥' : '高雲≥') + cc.cloud_high_min + '%');
    if (cc.precip_max_mmh != null) parts.push((lang === 'en' ? 'precip≤' : '降水≤') + cc.precip_max_mmh);
    if (cc.visibility_min_km != null) parts.push((lang === 'en' ? 'vis≥' : '能見度≥') + cc.visibility_min_km);
    if (cc.wind_max_ms != null) parts.push('風≤' + cc.wind_max_ms);
    if (Array.isArray(cc.windows) && cc.windows.length) {
      parts.push(cc.windows.map(function (s) { return cpWinSegSummary(s, lang); }).join('＋'));
    } else if (cc.window_start && cc.window_end) {
      parts.push(cc.window_start + '–' + cc.window_end);
    }
    if (Array.isArray(cc.months) && cc.months.length) parts.push((lang === 'en' ? 'months ' : '月 ') + fmtMonths(cc.months));
    return parts.join('・');
  }
  // 1,2,3 / 12,1,2 → compact "1–3" ranges (list stays honest, no invented words)
  function fmtMonths(ms) {
    var parts = [], s = ms[0], prev = ms[0];
    for (var i = 1; i <= ms.length; i++) {
      if (i < ms.length && ms[i] === prev + 1) { prev = ms[i]; continue; }
      parts.push(s === prev ? String(s) : s + '–' + prev);
      s = prev = ms[i];
    }
    return parts.join(',');
  }
  // CL-APP-09 patch-2: anchor + multi-segment window editor (private-place
  // theme form). Same schema/semantics as the subject-sets editors.
  function cpWtLabel(type) {
    return { fixed: t().wt_fixed, before_sunrise: t().wt_bs, after_sunrise: t().wt_as, before_sunset: t().wt_bd, after_sunset: t().wt_ads }[type] || '';
  }
  function cpWinSegSummary(seg, lang) {
    if (!seg || !seg.type || seg.type === 'fixed') {
      return (seg && seg.start ? seg.start : '?') + '–' + (seg && seg.end ? seg.end : '?');
    }
    var lbl = cpWtLabel(seg.type).replace(/（.*?）/, '').replace(/ \(daily dynamic\)/, '');
    var off = (seg.offset_minutes != null && seg.offset_minutes !== 0)
      ? ((seg.offset_minutes > 0 ? '+' : '−') + Math.abs(seg.offset_minutes) + (lang === 'zh-TW' ? '分' : lang === 'ja' ? '分' : 'min'))
      : '';
    // patch-5 ⑤: a short-window span is part of the honest label
    var span = (seg.span_minutes != null && seg.span_minutes > 0)
      ? '·' + seg.span_minutes + (lang === 'zh-TW' ? '分窗' : lang === 'ja' ? '分窓' : 'min window')
      : '';
    return lbl + off + span;
  }
  var cpWTYPES = ['fixed', 'before_sunrise', 'after_sunrise', 'before_sunset', 'after_sunset'];
  var cpWinState = [{ type: 'fixed', start: '', end: '' }];
  function cpWindowSegsOf(cc) {
    if (cc && Array.isArray(cc.windows) && cc.windows.length) return cc.windows;
    if (cc && cc.window_start && cc.window_end) return [{ type: 'fixed', start: cc.window_start, end: cc.window_end }];
    return [{ type: 'fixed', start: '', end: '' }];
  }
  function cpRenderWinArea() {
    var host = els.overlay ? els.overlay.querySelector('#cl-cp-win-area') : null;
    if (!host) return;
    host.innerHTML = cpWinAreaHtml();
    cpWireWinArea();
  }
  function cpWinAreaHtml() {
    var out = '';
    for (var i = 0; i < cpWinState.length; i++) out += cpWinSegHtml(i, cpWinState[i]);
    out += (cpWinState.length < 2 ? '<button type="button" class="cl-ss-act" id="cl-cp-win-add">' + esc(t().win_add2) + '</button>' : '') +
      '<div class="hint">' + esc(t().win_hint) + '</div>';
    return out;
  }
  function cpWinSegHtml(i, seg) {
    var idp = 'cl-cp-ws' + i;
    var typeSel = '<select id="' + idp + '-type" class="inp" style="flex:0 0 auto">' +
      cpWTYPES.map(function (w) { return '<option value="' + w + '"' + (w === seg.type ? ' selected' : '') + '>' + esc(cpWtLabel(w)) + '</option>'; }).join('') +
      '</select>';
    var fields;
    if (seg.type === 'fixed') {
      fields = '<input id="' + idp + '-start" value="' + esc(seg.start || '') + '" placeholder="04:30" style="flex:1">' +
        '<span style="color:var(--cl-text-3)">–</span>' +
        '<input id="' + idp + '-end" value="' + esc(seg.end || '') + '" placeholder="07:00" style="flex:1">';
    } else {
      fields = '<input id="' + idp + '-off" inputmode="numeric" value="' + esc(seg.offset_minutes != null ? String(seg.offset_minutes) : '') + '" placeholder="0" style="flex:0 0 70px">' +
        '<span class="hint" style="flex:0 0 auto">' + esc(t().win_off) + '</span>' +
        '<input id="' + idp + '-span" inputmode="numeric" value="' + esc(seg.span_minutes != null ? String(seg.span_minutes) : '') + '" placeholder="— " style="flex:0 0 70px" aria-label="' + esc(t().win_span) + '">' +
        '<span class="hint" style="flex:0 0 auto">' + esc(t().win_span) + '</span>';
    }
    return '<div class="cl-cp-winseg" data-cp-ws="' + i + '" style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">' + typeSel + fields +
      (i === 1 ? '<button type="button" class="cl-ss-act cl-ss-act-del" id="cl-cp-win-rm" aria-label="' + esc(t().win_rm) + '">✕</button>' : '') +
      '</div>';
  }
  function cpReadWinState() {
    var segs = [];
    for (var i = 0; i < 2; i++) {
      var typeEl = els.overlay.querySelector('#cl-cp-ws' + i + '-type');
      if (!typeEl) { if (cpWinState[i]) segs.push(cpWinState[i]); continue; }
      if (typeEl.value === 'fixed') {
        var s = (els.overlay.querySelector('#cl-cp-ws' + i + '-start') || {}).value || '';
        var e = (els.overlay.querySelector('#cl-cp-ws' + i + '-end') || {}).value || '';
        segs.push({ type: 'fixed', start: String(s).trim(), end: String(e).trim() });
      } else {
        var idp = 'cl-cp-ws' + i;
        var offEl = els.overlay.querySelector('#' + idp + '-off');
        var off = offEl && offEl.value.trim() !== '' ? parseInt(offEl.value, 10) : 0;
        var s = { type: typeEl.value, offset_minutes: isFinite(off) ? off : 0 };
        // patch-5 ⑤: span survives round-trip when the stored segment carried one
        var spanEl = els.overlay.querySelector('#' + idp + '-span');
        var span = spanEl && spanEl.value.trim() !== '' ? parseInt(spanEl.value, 10) : NaN;
        if (isFinite(span) && span > 0) s.span_minutes = span;
        else if (cpWinState[i] && cpWinState[i].span_minutes != null && spanEl && spanEl.value.trim() === '') s.span_minutes = cpWinState[i].span_minutes;
        segs.push(s);
      }
    }
    return segs;
  }
  function cpWireWinArea() {
    var addBtn = els.overlay.querySelector('#cl-cp-win-add');
    if (addBtn) addBtn.addEventListener('click', function () {
      cpWinState = cpReadWinState();
      if (cpWinState.length < 2) cpWinState.push({ type: 'fixed', start: '', end: '' });
      cpRenderWinArea();
      els.overlay.querySelector('#cl-cp-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
    });
    var rmBtn = els.overlay.querySelector('#cl-cp-win-rm');
    if (rmBtn) rmBtn.addEventListener('click', function () {
      cpWinState = cpReadWinState().slice(0, 1);
      cpRenderWinArea();
      els.overlay.querySelector('#cl-cp-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
    });
    [0, 1].forEach(function (i) {
      var typeEl = els.overlay.querySelector('#cl-cp-ws' + i + '-type');
      if (!typeEl) return;
      typeEl.addEventListener('change', function () {
        cpWinState = cpReadWinState();
        cpWinState[i] = typeEl.value === 'fixed' ? { type: 'fixed', start: '', end: '' } : { type: typeEl.value, offset_minutes: 0 };
        cpRenderWinArea();
        els.overlay.querySelector('#cl-cp-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
      });
      ['start', 'end', 'off', 'span'].forEach(function (f) {
        var el = els.overlay.querySelector('#cl-cp-ws' + i + '-' + f);
        if (el) el.addEventListener('change', function () {
          els.overlay.querySelector('#cl-cp-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
        });
      });
    });
  }
  function buildPrivateCard(p) {
    // patch-6: normal states render through the OFFICIAL createSpotCard (the
    // CLForecastRenderers bridge) — identical anatomy to official cards; the
    // ◉私人 badge, the ⋯ menu trigger and the forecast-popup targets are the
    // only private differences. Special states (trial-expired / pending) keep
    // the dedicated honest card below.
    if (bridgeActive() && !isSpecialCard(p)) {
      var info = cpCardInfo(p);
      if (info) {
        var brCard = window.CLForecastRenderers.createCard(info.spot, info.metric, cpCardOpts(p));
        if (brCard) {
          brCard.classList.add('cl-cp-card');
          brCard.setAttribute('data-cp-id', p.id);
          brCard._cpSig = JSON.stringify(p);
          // ⋯ menu (patch-3 anatomy unchanged): one shared menu portaled to
          // body, position:fixed under the trigger — the trigger rides the
          // official card-header-actions row.
          var act = brCard.querySelector('.card-header-actions');
          if (act) {
            var more = document.createElement('button');
            more.type = 'button';
            more.className = 'cl-cp-more';
            more.setAttribute('aria-label', '⋯');
            more.setAttribute('aria-haspopup', 'menu');
            more.setAttribute('aria-expanded', 'false');
            more.textContent = '⋯';
            act.appendChild(more);
            more.addEventListener('click', function (e) {
              e.stopPropagation();
              var m = ensureMenu();
              var wasOpen = m.classList.contains('open') && state.menuPlace && state.menuPlace.id === p.id;
              closeMenu();
              if (!wasOpen) openMenuFor(p, more);
            });
          }
          // CL-APP-12: every place carries weather + temperature, subject or not
          var wxHtml0 = cpWeatherLineHtml(p.weather);
          if (wxHtml0) {
            var metaBox = brCard.querySelector('.card-secondary-meta');
            if (metaBox) metaBox.insertAdjacentHTML('beforeend', wxHtml0);
            else brCard.insertAdjacentHTML('beforeend', wxHtml0);
          }
          return brCard;
        }
      }
    }
    var card = document.createElement('div');
    card.className = 'card cl-cp-card';
    card.setAttribute('data-cp-id', p.id);
    card.setAttribute('data-cp-special', '1');
    card.tabIndex = 0;
    updatePrivateCard(p, card);
    return card;
  }
  function updatePrivateCard(p, card) {
    card = card || document.querySelector('#spots-container .cl-cp-card[data-cp-id="' + CSS.escape(p.id) + '"]');
    if (!card) return;
    // patch-6: bridge cards cannot innerHTML-rewrite (they are official-anatomy
    // DOM) — replace the node when the data signature changes.
    if (bridgeActive() && !isSpecialCard(p)) {
      if (card._cpSig === JSON.stringify(p)) return;
      var fresh = buildPrivateCard(p);
      if (fresh && card.parentNode) card.parentNode.replaceChild(fresh, card);
      return;
    }
    var sig = JSON.stringify(p);
    if (card._cpSig === sig) return; // identical data → no innerHTML rewrite (the
    card._cpSig = sig;               // container MutationObserver watches these cards)
    var ev = p.evaluation || {};
    var expired = p.status === 'trial_expired';
    card.classList.toggle('cl-cp-expired', expired);
    var lang = currentLang();
    var headBadge = (expired || ev.tier === 'pending') ? tierBadge(p) : '';
    var head =
      '<div class="spot-title-group">' +
        '<div class="card-head-line" style="display:flex;align-items:center;gap:8px;min-width:0">' +
          '<span class="cl-cp-card-name" style="font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + esc(p.name) + '</span>' +
          headBadge +
          '<span class="cl-cp-priv-badge">◉ ' + esc(expired ? t().trial_expired : t().priv_badge) + '</span>' +
        '</div>' +
      '</div>' +
      // patch-3: the menu markup moved OUT of the card — one shared menu is
      // portaled to document.body (ensureMenu) and position:fixed under the
      // ⋯ trigger, so the card's content-visibility/paint containment and the
      // container overflow can never clip the dropdown again.
      '<button type="button" class="cl-cp-more" aria-label="⋯" aria-haspopup="menu" aria-expanded="false">⋯</button>';
    // patch-6: the homegrown per-group row builder (cpCardRow, the compact
    // ✗+短因 mini anatomy) is RETIRED — verdicts render ONLY through the
    // official renderer. This legacy path now serves the special states and
    // the cache-skew fallback (old app.js without the bridge) with the honest
    // pending note.
    var body;
    // CL-UX-01 keeper: the honest data states WIN over the zero-subject face — a
    // place still queued for its first fetch must keep saying 「明早更新」, not
    // 「尚未設定題材」 (it has no subjects yet BECAUSE it has no data).
    if (!expired && ev.tier === 'pending') {
      body = p.fetchDeferred
        ? '<div class="cl-cp-deferred-note">⏳ ' + esc(t().deferred_note) + '</div>'
        : '<div class="cl-cp-deferred-note">⏳ ' + esc(t().tier_pending) + '</div>';
    } else if (!expired && cpHasNoThemes(p)) {
      // owner ruling: no subject → 「尚未設定題材」 + weather facts, never a verdict
      body = '<div class="cl-cp-none-note">🎞 ' + esc(t().wx_no_subject) + '</div>' +
        cpWeatherLineHtml(p.weather) +
        '<button type="button" class="cl-cp-none-cta" data-cp-act="add-theme">' + esc(t().th_add) + '</button>';
    } else if (expired) {
      body = '<div class="cl-cp-expired-note">🔒 ' + esc(t().trial_note) + '</div>' +
        '<button type="button" class="cl-cp-expired-cta" data-cp-act="upgrade">⬆ ' + esc(t().trial_cta) + '</button>';
    } else if (ev.tier === 'pending' && p.fetchDeferred) {
      body = '<div class="cl-cp-deferred-note">⏳ ' + esc(t().deferred_note) + '</div>';
    } else {
      body = '<div class="cl-cp-deferred-note">⏳ ' + esc(t().tier_pending) + '</div>';
    }
    // CL-APP-08: shared-fetch tag (gray identity — never a semantic color)
    var shareLine = shareTagText(p.sharing, lang)
      ? '<div class="cl-cp-share-tag"><span class="st-ic">🔗</span><span class="st-txt">' + esc(shareTagText(p.sharing, lang)) + '</span></div>' : '';
        card.innerHTML = '<div style="display:flex;align-items:flex-start;gap:8px;min-width:0">' + head + '</div>' + body + shareLine;
    // ⋯ menu (patch-3): one shared menu portaled to document.body, anchored
    // position:fixed under the trigger — the card boundary can never clip it.
    var more = card.querySelector('.cl-cp-more');
    more.addEventListener('click', function (e) {
      e.stopPropagation();
      var m = ensureMenu();
      var wasOpen = m.classList.contains('open') && state.menuPlace && state.menuPlace.id === p.id;
      closeMenu();
      if (!wasOpen) openMenuFor(p, more);
    });
    // the expired-card CTA (data-cp-act="upgrade") is card body content —
    // the portaled menu can no longer handle it by bubbling, so wire it here.
    card.addEventListener('click', function (e) {
      if (e.target.closest('[data-cp-act="upgrade"]')) { e.stopPropagation(); toast(t().trial_cta); return; }
      // CL-APP-12: the zero-subject card's ＋新增題材 CTA
      if (e.target.closest('[data-cp-act="add-theme"]')) { e.stopPropagation(); ccModal(p); }
    });
    // patch-7 (owner ruling): private cards get the SAME card-click surface as
    // official cards — clicking the card body (not ⋯, not a button/link)
    // opens the forecast popup (quick view / 8-day strip / per-subject rows).
    card.addEventListener('click', function (e) {
      if (e.target.closest('button, a, input, select')) return;
      forecastModal(p);
    });
    card.addEventListener('keydown', function (e) {
      if (e.target.closest('button, a, input, select')) return;
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); forecastModal(p); }
    });
  }
  // ───── patch-7: private-card forecast popup (official-card click parity) ─────
  // The popup renders ONLY data the worker already fetched (stored eval):
  // quick view (tier/window/reason) + an 8-day strip (honest ─ for days the
  // ~48h feed doesn't cover) + per-subject rows (the user's custom conditions
  // and the general baseline), plus a 「題材」 entry that opens the conditions
  // panel. The hour matcher mirrors the worker's customHourMatches/hourInWindow
  // EXACTLY (same lenient defaults, missing-value fails honestly) so the
  // popup can never disagree with the card tier.
  // (patch-9: the separate general-baseline row and its constant were removed
  // with the dual-truth ruling — the per-subject rows are the single truth.)
  function cpHourInWindow(hour, start, end) {
    if (typeof hour !== 'string' || !/^([01]\d|2[0-3]):[0-5]\d$/.test(hour)) return false;
    if (typeof start !== 'string' || typeof end !== 'string') return true; // no window = whole day
    if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(start) || !/^([01]\d|2[0-3]):[0-5]\d$/.test(end)) return true;
    return start <= end ? (hour >= start && hour <= end) : (hour >= start || hour <= end);
  }
  function cpHourMatches(values, cc) {
    if (!cc) return false;
    var v = values && typeof values === 'object' ? values : {};
    var rows = [
      ['cloud_low_max', 'cloud_low'], ['cloud_mid_max', 'cloud_mid'], ['cloud_high_max', 'cloud_high'],
      ['cloud_low_min', 'cloud_low'], ['cloud_mid_min', 'cloud_mid'], ['cloud_high_min', 'cloud_high'],
      ['precip_max_mmh', 'precipitation'], ['visibility_min_km', 'visibility'], ['wind_max_ms', 'wind'],
    ];
    for (var i = 0; i < rows.length; i++) {
      var limit = Number(cc[rows[i][0]]);
      if (!isFinite(limit)) continue;
      var isFloor = rows[i][0].indexOf('_min') > 0 || rows[i][0] === 'visibility_min_km';
      if (!isFloor && rows[i][1].indexOf('cloud') === 0 && limit >= 100) continue; // lenient default
      if (isFloor && limit <= 0) continue;                                          // lenient default
      var val = v[rows[i][1]];
      val = (typeof val === 'number' && isFinite(val)) ? val : null;
      if (val == null) return false; // constraint set but data missing → no match
      if (isFloor ? val < limit : val > limit) return false;
    }
    return true;
  }
  // ── patch-9 (owner ruling): the raw 「25.0682, 121.5794 · 13 m · Asia/Taipei」
  // header line leaked the full-precision coordinates and the raw IANA zone.
  // ONE meta-line anatomy everywhere (card sub-line + popup header), same
  // convention as the official modal: coordinates at 3 decimals (location
  // identity, not surveying precision), elevation in metres, the zone as the
  // GMT±n abbreviation (tzAbbrLabel convention — never a bare IANA string).
  function cpTzLabel(tz) {
    if (!tz) return '';
    if (/^GMT[+-]/.test(String(tz))) return String(tz); // already the convention
    try {
      var parts = new Intl.DateTimeFormat('en-US', { timeZone: String(tz), timeZoneName: 'shortOffset' }).formatToParts(new Date());
      for (var i = 0; i < parts.length; i++) {
        if (parts[i].type === 'timeZoneName' && /^GMT/.test(parts[i].value)) return parts[i].value;
      }
    } catch (e) { /* unknown zone → honest omit */ }
    return '';
  }
  // ───── CL-APP-12 (owner ruling 2026-11-24): weather on EVERY card ─────
  // A place with no subject gets 「尚未設定題材」 + visibility / WMO weather /
  // today's temperature range instead of a verdict it cannot support; a place
  // WITH subjects shows the same weather line underneath its verdict.
  function cpHasNoThemes(p) {
    var gs = (p && Array.isArray(p.themeGroups)) ? p.themeGroups : [];
    return !gs.length && !(p && p.customConditions);
  }
  function cpWmoWord(code) {
    var L = t();
    if (code == null || !Number.isFinite(Number(code))) return '';
    var c = Number(code);
    if (c === 0) return L.wmo_clear;
    if (c === 1) return L.wmo_mostly_clear;
    if (c === 2) return L.wmo_partly;
    if (c === 3) return L.wmo_overcast;
    if (c === 45 || c === 48) return L.wmo_fog;
    if (c >= 51 && c <= 57) return L.wmo_drizzle;
    if (c >= 61 && c <= 67) return L.wmo_rain;
    if (c >= 71 && c <= 77) return L.wmo_snow;
    if (c >= 80 && c <= 82) return L.wmo_showers;
    if (c === 85 || c === 86) return L.wmo_snow_showers;
    if (c >= 95) return L.wmo_thunder;
    return '';
  }
  // same shape the worker's weatherSummary emits; the popup recomputes from the
  // stored hourly grid when the payload carries temperature (older records
  // predate the fetch fields and simply stay silent about temp).
  function cpWeatherFromPayload(payload, tz) {
    var rows = (payload && Array.isArray(payload.hourly)) ? payload.hourly : [];
    if (!rows.length) return null;
    var today = rows[0].local_date;
    try {
      today = new Intl.DateTimeFormat('en-CA', { timeZone: tz || 'UTC', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
    } catch (e) { /* keep the row's own date */ }
    var day = rows.filter(function (r) { return r && r.local_date === today; });
    if (!day.length) day = rows.filter(function (r) { return r && r.local_date === rows[0].local_date; });
    var pick = function (k) {
      return day.map(function (r) { return (r.values || {})[k]; })
        .filter(function (v) { return v != null && isFinite(Number(v)); }).map(Number);
    };
    var temps = pick('temp'), vis = pick('visibility'), codes = pick('weather_code');
    if (!temps.length && !vis.length && !codes.length) return null;
    var code = null;
    if (codes.length) {
      var freq = {}, best = null;
      codes.forEach(function (c) { freq[c] = (freq[c] || 0) + 1; });
      Object.keys(freq).forEach(function (c) {
        var n = freq[c];
        if (!best || n > best.n || (n === best.n && Number(c) > Number(best.c))) best = { c: Number(c), n: n };
      });
      code = best ? best.c : null;
    }
    return {
      date: (day[0] && day[0].local_date) || null,
      temp_min: temps.length ? Math.min.apply(null, temps) : null,
      temp_max: temps.length ? Math.max.apply(null, temps) : null,
      visibility_min_m: vis.length ? Math.min.apply(null, vis) : null,
      visibility_max_m: vis.length ? Math.max.apply(null, vis) : null,
      weather_code: code,
    };
  }
  function cpWeatherLineHtml(w) {
    if (!w) return '';
    var parts = [];
    var wx = cpWmoWord(w.weather_code);
    if (wx) parts.push('☁ ' + esc(wx));
    if (w.visibility_min_m != null && w.visibility_max_m != null) {
      var v1 = Math.round(w.visibility_min_m / 1000), v2 = Math.round(w.visibility_max_m / 1000);
      parts.push('👁 ' + esc(t().wx_vis) + ' ' + (v1 === v2 ? String(v1) : v1 + '–' + v2) + ' km');
    }
    if (w.temp_min != null && w.temp_max != null) {
      parts.push('🌡 ' + esc(t().wx_temp) + ' ' + Math.round(w.temp_min) + '–' + Math.round(w.temp_max) + '°C');
    }
    if (!parts.length) return '';
    return '<div class="cl-cp-wx">' + parts.map(function (x) { return '<span class="cl-cp-wx-i">' + x + '</span>'; }).join('') + '</div>';
  }
  function cpMetaLine(p) {
    var lat = Number(p.lat), lng = Number(p.lng);
    var parts = [];
    if (isFinite(lat) && isFinite(lng)) parts.push(lat.toFixed(3) + ', ' + lng.toFixed(3));
    if (p.elevation != null) parts.push(p.elevation + ' m');
    var tz = cpTzLabel(p.timezone);
    if (tz) parts.push(tz);
    return parts.join(' · ');
  }
  // ── patch-4 (CL-APP-09): the popup's condition fold rides the OFFICIAL
  // builder (v2CondFoldHtml via the app.js bridge). Private sets carry
  // REQUIRED-type weather constraints only, so the fold shows the 成立條件
  // group and omits the 加分/扣分 groups exactly like the official fold omits
  // empty ones; the time window / applicable months ride extra label rows —
  // they are not weather metrics and never masquerade as internal metric ids.
  var CP_COND_LABELS = {
    'zh-TW': { cloud_low: '低雲', cloud_mid: '中雲', cloud_high: '高雲', precip: '降水', vis: '能見度', wind: '風速', window: '時窗', months: '適用月份' },
    'en': { cloud_low: 'Low cloud', cloud_mid: 'Mid cloud', cloud_high: 'High cloud', precip: 'Precip', vis: 'Visibility', wind: 'Wind', window: 'Time window', months: 'Applicable months' },
    'ja': { cloud_low: '低雲', cloud_mid: '中雲', cloud_high: '高雲', precip: '降水', vis: '視程', wind: '風速', window: '時間帯', months: '適用月' },
  };
  // the user's constraints in the OFFICIAL contract condition shape (real
  // metric ids only — v2MetricName resolves them from the shared registry)
  function cpFoldMetricConditions(cc) {
    var out = [];
    function add(metric, op, th, unit) { out.push({ metric: metric, operator: op, threshold: th, unit: unit, role: 'REQUIRED' }); }
    if (!cc) return out;
    if (cc.cloud_low_max != null && cc.cloud_low_max < 100) add('cloud_cover_low', 'lte', cc.cloud_low_max, '%');
    if (cc.cloud_mid_max != null && cc.cloud_mid_max < 100) add('cloud_cover_mid', 'lte', cc.cloud_mid_max, '%');
    if (cc.cloud_high_max != null && cc.cloud_high_max < 100) add('cloud_cover_mid_and_high', 'lte', cc.cloud_high_max, '%');
    // patch-5 ⑤: the floor direction (cloud-sea-style 越多越好)
    if (cc.cloud_low_min != null && cc.cloud_low_min > 0) add('cloud_cover_low', 'gte', cc.cloud_low_min, '%');
    if (cc.cloud_mid_min != null && cc.cloud_mid_min > 0) add('cloud_cover_mid', 'gte', cc.cloud_mid_min, '%');
    if (cc.cloud_high_min != null && cc.cloud_high_min > 0) add('cloud_cover_high', 'gte', cc.cloud_high_min, '%');
    if (cc.precip_max_mmh != null) add('precipitation', 'lte', cc.precip_max_mmh, 'mm/h');
    if (cc.visibility_min_km != null && cc.visibility_min_km > 0) add('visibility', 'gte', cc.visibility_min_km, 'km');
    if (cc.wind_max_ms != null) add('wind_speed_10m', 'lte', cc.wind_max_ms, 'm/s');
    return out;
  }
  function cpFoldExtraRows(cc, lang) {
    if (!cc) return '';
    var L = CP_COND_LABELS[lang] || CP_COND_LABELS['zh-TW'];
    var rows = '';
    var win = null;
    if (Array.isArray(cc.windows) && cc.windows.length) win = cc.windows.map(function (s) { return cpWinSegSummary(s, lang); }).join('＋');
    else if (cc.window_start && cc.window_end) win = cc.window_start + '–' + cc.window_end;
    if (win) rows += '<div class="v2-cond"><b>' + esc(L.window) + '</b> <span class="v2-th">' + esc(win) + '</span></div>';
    if (Array.isArray(cc.months) && cc.months.length) rows += '<div class="v2-cond"><b>' + esc(L.months) + '</b> <span class="v2-th">' + esc(fmtMonths(cc.months)) + '</span></div>';
    return rows;
  }
  // ───── patch-4 (CL-APP-09): the popup REUSES the official forecast popup ─────
  // renderer through the app.js bridge (window.CLForecastRenderers). The
  // popup no longer grows its own anatomy: the private place's stored eval is
  // CONVERTED into the official renderer INPUTS (synthetic subject-cards rows
  // with the SAME structure the card tier consumes + synthetic evaluation
  // days), so every block is the same HTML the official surfaces render:
  //   速覽「現在去會怎樣」+ 24h mini band  → mountQuickView (official)
  //   8 日方框 + 今天題材判定              → v2DayStripHtml/v2DaySubHtml
  //   逐題材行＝短名＋下一個窗時刻＋🔔      → clSubjectRowLine (ONE anatomy,
  //                                          never a per-day 8-cell mini strip)
  //   條件摺疊（必須/加分/扣分）            → v2CondFoldHtml (official)
  // Honest fallbacks: no hourly grid → no 24h band + honest 資料不足 days;
  // no researched guide content for a private point → the 攝影指南 section
  // stays ABSENT (never fabricated); anchor windows that cannot resolve
  // never match (fail-closed mirror of the worker).
  // ── patch-4 matcher mirrors (workers/api/src/notify.js + custom-places.js):
  // the synthetic rows are judged by the SAME rules the worker used for the
  // card tier — one hour truth, no second verdict source.
  var CP_GENERAL_BASELINE = { precip_max_mmh: 2, visibility_min_km: 3, wind_max_ms: 10 }; // mirror of GENERAL_BASELINE
  var CP_FAIL_METRIC = { cloud_low_max: 'cloud_cover_low', cloud_mid_max: 'cloud_cover_mid', cloud_high_max: 'cloud_cover_mid_and_high', cloud_low_min: 'cloud_cover_low', cloud_mid_min: 'cloud_cover_mid', cloud_high_min: 'cloud_cover_high', precip_max_mmh: 'precipitation', visibility_min_km: 'visibility', wind_max_ms: 'wind_speed_10m' };
  var CP_FAIL_PRIORITY = ['precip_max_mmh', 'visibility_min_km', 'cloud_low_max', 'cloud_mid_max', 'cloud_high_max', 'cloud_low_min', 'cloud_mid_min', 'cloud_high_min', 'wind_max_ms'];
  var CP_METRIC_OF = { cloud_low_max: 'cloud_low', cloud_mid_max: 'cloud_mid', cloud_high_max: 'cloud_high', cloud_low_min: 'cloud_low', cloud_mid_min: 'cloud_mid', cloud_high_min: 'cloud_high', precip_max_mmh: 'precipitation', visibility_min_km: 'visibility', wind_max_ms: 'wind' };
  function cpConstraintActive(k, cc) {
    if (!cc || cc[k] == null) return false;
    var n = Number(cc[k]);
    if (!isFinite(n)) return false;
    if (k.indexOf('_min') > 0) return n > 0;   // patch-5 ⑤ floors: >0 = constraining
    if (k.indexOf('cloud') === 0 && n >= 100) return false; // lenient default
    if (k === 'visibility_min_km' && n <= 0) return false;   // lenient default
    return true;
  }
  // first failing constraint (official fail-priority order) → its metric id,
  // so the SHORT word comes from the bundle's fail_reason_short dictionary
  // through the bridge — never a duplicated word table here.
  function cpFirstFailMetric(values, groups) {
    var v = values && typeof values === 'object' ? values : {};
    for (var i = 0; i < CP_FAIL_PRIORITY.length; i++) {
      var k = CP_FAIL_PRIORITY[i];
      for (var j = 0; j < groups.length; j++) {
        var cc = groups[j].cond;
        if (!cpConstraintActive(k, cc)) continue;
        var raw = v[CP_METRIC_OF[k]];
        var val = (typeof raw === 'number' && isFinite(raw)) ? raw : null;
        var isFloor = k.indexOf('_min') > 0 || k === 'visibility_min_km';
        if (val == null || (isFloor ? val < Number(cc[k]) : val > Number(cc[k]))) return CP_FAIL_METRIC[k];
      }
    }
    return null;
  }
  /* BEGIN SOLAR MIRROR (workers/api/src/solar.js — keep in sync; the test
     imports the worker module and compares both on sample dates) */
  var CP_S_RAD = Math.PI / 180, CP_S_DEG = 180 / Math.PI;
  function cpJulianDay0UT(y, m, d) { if (m <= 2) { y -= 1; m += 12; } var a = Math.floor(y / 100); var b = 2 - a + Math.floor(a / 4); return Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + d + b - 1524.5; }
  function cpSolarGeom(jd) {
    var T = (jd - 2451545.0) / 36525;
    var L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360;
    var M = 357.52911 + T * (35999.05029 - 0.0001537 * T);
    var e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T);
    var Mr = M * CP_S_RAD;
    var C = (Math.sin(Mr) * (1.914602 - T * (0.004817 + 0.000014 * T)) + Math.sin(2 * Mr) * (0.019993 - 0.000101 * T) + Math.sin(3 * Mr) * 0.000289);
    var trueLong = L0 + C;
    var omega = 125.04 - 1934.136 * T;
    var lambda = trueLong - 0.00569 - 0.00478 * Math.sin(omega * CP_S_RAD);
    var eps0 = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60;
    var eps = eps0 + 0.00256 * Math.cos(omega * CP_S_RAD);
    var decl = Math.asin(Math.sin(eps * CP_S_RAD) * Math.sin(lambda * CP_S_RAD)) * CP_S_DEG;
    var yv = Math.tan(eps * CP_S_RAD / 2) * Math.tan(eps * CP_S_RAD / 2);
    var L0r = L0 * CP_S_RAD;
    var eqtime = 4 * CP_S_DEG * (yv * Math.sin(2 * L0r) - 2 * e * Math.sin(Mr) + 4 * e * yv * Math.sin(Mr) * Math.cos(2 * L0r) - 0.5 * yv * yv * Math.sin(4 * L0r) - 1.25 * e * e * Math.sin(2 * Mr));
    return { decl: decl, eqtime: eqtime };
  }
  function cpSunTimesForDate(localDate, lat, lng, utcOffsetHours) {
    var md = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(localDate || ''));
    if (!md) return null;
    var phi = Number(lat), lngv = Number(lng);
    if (lat == null || lng == null || !isFinite(phi) || !isFinite(lngv) || Math.abs(phi) > 90 || Math.abs(lngv) > 180) return null;
    var y = Number(md[1]), m = Number(md[2]), d = Number(md[3]);
    var offMin = (isFinite(utcOffsetHours) ? utcOffsetHours : 8) * 60;
    var jdNoon = cpJulianDay0UT(y, m, d) + (12 * 60 - offMin) / 1440;
    var g = cpSolarGeom(jdNoon);
    var cosH = (Math.cos(90.833 * CP_S_RAD) - Math.sin(phi * CP_S_RAD) * Math.sin(g.decl * CP_S_RAD)) / (Math.cos(phi * CP_S_RAD) * Math.cos(g.decl * CP_S_RAD));
    if (cosH > 1 || cosH < -1) return null; // polar: sun never crosses the horizon
    var H = Math.acos(cosH) * CP_S_DEG;
    var solarNoonUT = 720 - 4 * lngv - g.eqtime;
    var riseUT = solarNoonUT - 4 * H, setUT = solarNoonUT + 4 * H;
    var norm = function (x) { return ((x % 1440) + 1440) % 1440; };
    return { sunriseMin: Math.round(norm(riseUT + offMin)), sunsetMin: Math.round(norm(setUT + offMin)) };
  }
  /* END SOLAR MIRROR */
  // mirror of notify.js resolveSegmentBounds: a sun-anchored segment expands
  // with the place's REAL sun times per row date; unresolvable → null → the
  // hour never matches (fail-closed, never "whole day").
  function cpResolveSegment(seg, localDate, placeCtx) {
    if (!seg || typeof seg !== 'object') return null;
    if (seg.type === 'fixed') return { start: seg.start || null, end: seg.end || null };
    if (!placeCtx || !isFinite(placeCtx.lat) || !isFinite(placeCtx.lng)) return null;
    var sun = cpSunTimesForDate(localDate, placeCtx.lat, placeCtx.lng, placeCtx.utcOffsetHours);
    if (!sun) return null;
    var off = isFinite(seg.offset_minutes) ? seg.offset_minutes : 0;
    var anchorMin = /sunrise$/.test(String(seg.type)) ? sun.sunriseMin : sun.sunsetMin;
    var norm = function (x) { return ((Math.round(x) % 1440) + 1440) % 1440; };
    var toHM = function (x) { return String(Math.floor(x / 60)).padStart(2, '0') + ':' + String(x % 60).padStart(2, '0'); };
    if (/^before_/.test(String(seg.type))) return { start: seg.start || '00:00', end: toHM(norm(anchorMin + off)), anchorHM: toHM(norm(anchorMin)) };
    return { start: toHM(norm(anchorMin + off)), end: seg.end || '23:59', anchorHM: toHM(norm(anchorMin)) };
  }
  // mirror of notify.js segmentsOf + hourPassesWindows
  function cpSegmentsOf(cc) {
    if (!cc || typeof cc !== 'object') return null;
    if (Array.isArray(cc.windows) && cc.windows.length) return cc.windows;
    if (cc.window_type && cc.window_type !== 'fixed') {
      return [{ type: cc.window_type, start: cc.window_start, end: cc.window_end, offset_minutes: cc.offset_minutes != null ? cc.offset_minutes : 0 }];
    }
    if (cc.window_start != null || cc.window_end != null) return [{ type: 'fixed', start: cc.window_start, end: cc.window_end }];
    return null;
  }
  function cpHourPassesWindows(hour, localDate, cc, placeCtx) {
    var segs = cpSegmentsOf(cc);
    if (!segs) return true; // no window constraint
    if (typeof hour !== 'string' || typeof localDate !== 'string' || !/^([01]\d|2[0-3]):[0-5]\d$/.test(hour)) return false;
    for (var i = 0; i < segs.length; i++) {
      var b = cpResolveSegment(segs[i], localDate, placeCtx);
      if (!b) continue; // unresolvable — never matches
      if (cpHourInWindow(hour, b.start, b.end)) return true;
    }
    return false;
  }
  // mirror of placeCtxFromRec: GMT±n from the IANA zone (Intl), +8 baseline
  function cpTzOffsetHours(tz) {
    if (!tz) return 8;
    try {
      var parts = new Intl.DateTimeFormat('en-US', { timeZone: String(tz), timeZoneName: 'shortOffset' }).formatToParts(new Date());
      for (var i = 0; i < parts.length; i++) {
        if (parts[i].type === 'timeZoneName') {
          var m = /GMT([+-])(\d{1,2})(?::(\d{2}))?/.exec(parts[i].value);
          if (m) return (m[1] === '-' ? -1 : 1) * (Number(m[2]) + Number(m[3] || 0) / 60);
        }
      }
    } catch (e) { /* unknown zone keeps the +8 baseline */ }
    return 8;
  }
  function cpPopupDates(hourly, count) {
    var first = null;
    hourly.forEach(function (r) { if (!first && r && typeof r.local_date === 'string') first = r.local_date; });
    if (!first) return [];
    var base = first.split('-').map(Number);
    var dt = new Date(Date.UTC(base[0], base[1] - 1, base[2]));
    var out = [];
    for (var i = 0; i < count; i++) {
      out.push(dt.getUTCFullYear() + '-' + String(dt.getUTCMonth() + 1).padStart(2, '0') + '-' + String(dt.getUTCDate()).padStart(2, '0'));
      dt.setUTCDate(dt.getUTCDate() + 1);
    }
    return out;
  }
  // the popup's subject list: the user's theme groups, or the legacy single
  // blob, or — for a place with no conditions at all — the implicit general
  // floor group (the SAME judgment the worker's place tier used).
  function cpPopupGroups(p) {
    var groups = [];
    var gs = Array.isArray(p.themeGroups) ? p.themeGroups : [];
    gs.forEach(function (g) {
      groups.push({ key: 'cp:' + (g.id || g.name), name: themeDisplayName(g), cond: g.conditions || null, eval: g.evaluation || null });
    });
    if (!groups.length && p.customConditions) {
      groups.push({ key: 'cp:legacy', name: t().qv_subject_custom, cond: p.customConditions, eval: p.evaluation || null });
    }
    if (!groups.length) {
      groups.push({ key: 'cp:baseline', name: t().qv_general_base, cond: CP_GENERAL_BASELINE, eval: p.evaluation || null, baseline: true });
    }
    return groups;
  }
  // THE adapter: stored eval + the user's conditions → official renderer
  // inputs (synthetic subject-cards rows keyed by local_date + synthetic
  // evaluation day entries + an official-shaped spot with an official-shaped
  // hourly forecast). Time-aware tier: TODAY counts only remaining hours.
  function cpSyntheticRows(p, payload, br) {
    var hourly = (payload && payload.hourly) || [];
    var tz = (payload && payload.timezone) || p.timezone || 'UTC';
    var ctx = { lat: Number(p.lat), lng: Number(p.lng), utcOffsetHours: cpTzOffsetHours(tz) };
    var groups = cpPopupGroups(p);
    var dates = cpPopupDates(hourly, 8);
    var words = br ? br.failWords() : {};
    var genreNames = {};
    groups.forEach(function (g) { genreNames[g.key] = { 'zh-TW': g.name }; });
    var byDate = {};
    hourly.forEach(function (r) {
      if (!r || typeof r.local_date !== 'string' || typeof r.hour !== 'string') return;
      (byDate[r.local_date] = byDate[r.local_date] || []).push(r);
    });
    var tree = {}, days = [];
    dates.forEach(function (date) {
      var rowsD = byDate[date] || [];
      if (!rowsD.length) {
        // honest ─: the ~48h feed does not cover this day
        days.push({ local_date: date, state: 'NOT_EVALUABLE', good_hours: [], conditions: [], hour_counts: {} });
        return;
      }
      var fitByHour = {}, okHours = [], noByHour = {};
      groups.forEach(function (g) { g._hours = []; });
      rowsD.forEach(function (r) {
        var hh = r.hour;
        var matched = false;
        groups.forEach(function (g) {
          if (!g.cond) return;
          // patch-8 ⑤: a whole day outside the group's 適用月份 is honest ─
          if (Array.isArray(g.cond.months) && g.cond.months.length && g.cond.months.indexOf(Number(date.slice(5, 7))) < 0) return;
          if (!cpHourPassesWindows(r.hour, date, g.cond, ctx)) return;
          if (!cpHourMatches(r.values, g.cond)) return;
          matched = true;
          (fitByHour[hh] = fitByHour[hh] || []).push(g.key);
          g._hours.push(hh);
        });
        if (!matched) {
          // the failing word is honest REGARDLESS of the baseline: the hour
          // failed the user's curated group even when the general floor still
          // passes (subject-layer ✗低雲 next to place-layer ○可拍 is the
          // official two-layer semantics, not a contradiction)
          var fm = cpFirstFailMetric(r.values, groups);
          if (fm) noByHour[hh] = fm;
          if (cpHourMatches(r.values, CP_GENERAL_BASELINE)) okHours.push(hh);
        }
      });
      var nowMin = br ? br.nowMinutes(tz) : null;
      var today = br ? br.localDate(tz, 0) : null;
      var isToday = date === today;
      var eff = function (list) {
        if (!isToday || nowMin == null) return list;
        return list.filter(function (tm) { var m = /^([01]\d|2[0-3]):([0-5]\d)$/.exec(tm); return m && (Number(m[1]) * 60 + Number(m[2])) >= nowMin; });
      };
      var allFit = Object.keys(fitByHour).sort();
      var eAllFit = eff(allFit), eOk = eff(okHours.slice().sort());
      var tier, tierReason = null, domReason = null;
      if (eAllFit.length) {
        tier = 'recommend';
      } else if (eOk.length) {
        tier = 'shootable';
        // CL-DATA-68 time-aware note (official wording): today whose curated
        // windows have ALL passed still reads ○ 可拍 — with the note.
        if (isToday && allFit.length) tierReason = { 'zh-TW': t().qv_win_passed };
      } else {
        tier = 'not_recommended';
        var ids = Object.keys(noByHour).map(function (h) { return noByHour[h]; });
        var dom = null;
        for (var i = 0; i < CP_FAIL_PRIORITY.length && !dom; i++) {
          var mid = CP_FAIL_METRIC[CP_FAIL_PRIORITY[i]];
          if (ids.indexOf(mid) >= 0) dom = mid;
        }
        if (dom && words[dom]) domReason = { 'zh-TW': words[dom]['zh-TW'] || '' };
        else if (p.evaluation && p.evaluation.reason) domReason = { 'zh-TW': p.evaluation.reason };
      }
      var suitable = [];
      groups.forEach(function (g) {
        if (g.baseline || !g._hours.length) return;
        suitable.push({ subject_short: { 'zh-TW': g.name }, window: g._hours.slice().sort() });
      });
      if (!suitable.length && eOk.length) {
        // CL-UI-71 fallback anatomy: the general floor as the synthetic entry
        suitable.push({ subject_short: { 'zh-TW': t().qv_general }, window: okHours.slice().sort() });
      }
      var gbFail = cpFirstFailMetric(null, [{ cond: CP_GENERAL_BASELINE }]);
      var gbWord = (gbFail && words[gbFail]) ? (words[gbFail]['zh-TW'] || '') : '';
      var failCond = null;
      (function () {
        for (var i = 0; i < CP_FAIL_PRIORITY.length && !failCond; i++) {
          var mid = CP_FAIL_METRIC[CP_FAIL_PRIORITY[i]];
          var found = false;
          for (var h in noByHour) if (noByHour[h] === mid) { found = true; break; }
          if (found) failCond = { metric: mid, day_verdict: 'FAIL' };
        }
      })();
      tree[date] = {
        tier: tier, tier_reason: tierReason, dominant_reason: domReason,
        suitable: suitable,
        general_baseline: { ok: eOk.length > 0, reason_short: gbWord ? { 'zh-TW': gbWord } : null },
        hours: { fit: fitByHour, ok: okHours.slice().sort(), na: [], no: noByHour, unk: [] },
        status: allFit.length ? 'ok' : 'failed',
      };
      days.push({
        local_date: date,
        state: allFit.length ? 'GUIDANCE_SATISFIED' : 'UNFAVORABLE',
        good_hours: allFit,
        conditions: failCond ? [failCond] : [],
        hour_counts: { GUIDANCE_SATISFIED: allFit.length },
      });
    });
    var spot = {
      spot_id: p.id, name: p.name, timezone: tz,
      elevation: p.elevation != null ? p.elevation : (payload && payload.elevation),
      lat: p.lat, lng: p.lng,
      hourly_forecast: hourly.map(function (r) {
        return {
          time: r.local_date + 'T' + r.hour, local_date: r.local_date,
          c_low: r.values && r.values.cloud_low, c_mid: r.values && r.values.cloud_mid, c_high: r.values && r.values.cloud_high,
          visibility: r.values && r.values.visibility, wind: r.values && r.values.wind,
        };
      }),
    };
    return { tz: tz, tree: tree, days: days, spot: spot, genreNames: genreNames, groups: groups };
  }
  // 逐題材行 — ONE official anatomy per subject (短名 + next window + 🔔);
  // rows render from the WORKER's stored per-group evaluation (the card's
  // single truth), refined when the eval payload confirms the same verdicts.
  function renderPopupSubjects(p) {
    var br = window.CLForecastRenderers;
    if (!br) return;
    var host = els.overlay.querySelector('#cl-cp-qv-subjects');
    if (!host) return;
    var tz = p.timezone || 'UTC';
    var groups = cpPopupGroups(p);
    var rows = groups.map(function (g) {
      var ge = g.eval || {};
      var stamp = ge.window ? br.nextStamp(ge.window, tz) : '';
      var nm = g.name;
      if (ge.tier === 'no' && ge.reason) nm = nm + ' · ' + ge.reason;
      else if (ge.tier === 'pending') nm = nm + ' · ' + t().tier_pending;
      return br.subjectRow({ name: nm, stamp: stamp, cc: g.cond }, p.id, false);
    }).join('');
    var folds = groups.map(function (g) {
      var conds = cpFoldMetricConditions(g.cond);
      var extra = cpFoldExtraRows(g.cond, currentLang());
      if (!conds.length && !extra) return '';
      return br.condFold(conds, extra);
    }).join('');
    host.innerHTML = '<div class="cl-subject-rows">' + rows + '</div>' + folds;
  }
  function cpPaintPopup(p, payload) {
    var br = window.CLForecastRenderers;
    if (!br) return;
    br.ensureCards().then(function () {
      if (!els.overlay.classList.contains('open')) return; // closed meanwhile
      var data = cpSyntheticRows(p, payload, br);
      br.registerSyntheticRows(p.id, data.tree, data.genreNames);
      // 速覽「現在去會怎樣」 — the OFFICIAL mountQuickView pipeline (same
      // v2QuickViewHtml → shared v2BandHtml + plain-weather as official cards)
      var host = els.overlay.querySelector('#cl-cp-qv-host');
      if (host) br.quickView(host, data.spot);
      // 8 日方框 + 今天題材判定 — the OFFICIAL strip/day-sub builders
      var stripHost = els.overlay.querySelector('#cl-cp-qv-days');
      if (stripHost) {
        var opp = { opportunity_id: null, genre_template: 'custom', days: data.days, live: null };
        // CL-UI-126: the popup's strip reads the SAME 7-day normaliser as the
        // official modal (today..today+6; past rows dropped, duplicate
        // local_date collapsed) — never a positional slice of the eval days.
        var aligned = br.modalDays(data.days, br.localDate(data.tz, 0));
        var labs = br.dayLabels(data.tz, aligned.length);
        var sd = [], sl = [];
        aligned.forEach(function (d, i) { if (!d) return; sd.push(d); sl.push(labs[i]); });
        stripHost.innerHTML = br.stripHtml(sd, sl, data.tz, data.spot, 'custom', null) +
          br.daySub(data.spot, opp);
        br.wireStrip(stripHost.querySelector('.v2-day-strip'));
      }
    });
  }
  // CL-APP-12 (owner ruling): a place with no subject has no verdict to show —
  // the popup degrades to 「尚未設定題材」 + the local weather facts, and offers
  // the same ＋新增題材 entry instead of a fabricated ✗/○ row.
  function cpPaintNoSubjectPopup(p) {
    var host = els.overlay.querySelector('#cl-cp-qv-host');
    var daysEl = els.overlay.querySelector('#cl-cp-qv-days');
    var subjEl = els.overlay.querySelector('#cl-cp-qv-subjects');
    var paint = function (w) {
      if (host) host.innerHTML = '<div class="cl-cp-none-face"><div class="cl-cp-none-title">🎞 ' + esc(t().wx_no_subject) + '</div>' +
        '<div class="cl-cp-none-sub">' + esc(t().wx_no_subject_note) + '</div>' + cpWeatherLineHtml(w) + '</div>';
      if (daysEl) daysEl.innerHTML = '';
      if (subjEl) subjEl.innerHTML = '<button type="button" class="cl-cp-btn" id="cl-cp-none-add">' + esc(t().th_add) + '</button>';
      var add = els.overlay.querySelector('#cl-cp-none-add');
      if (add) add.addEventListener('click', function () { closeOverlay(); ccModal(p); });
    };
    paint(p.weather || null);
    // fresher numbers when the stored grid already carries them
    api(API + '/' + p.id + '/eval')
      .then(function (res) { return res.json(); })
      .then(function (body) {
        if (!els.overlay.classList.contains('open')) return;
        if (body && body.ok && Array.isArray(body.hourly) && body.hourly.length) {
          paint(cpWeatherFromPayload(body, body.timezone || p.timezone) || p.weather || null);
        }
      })
      .catch(function () { /* keep the list-payload numbers */ });
  }
  function forecastModal(p) {
    var html =
      '<div class="cl-cp-m-head"><div><div class="name">📍 ' + esc(p.name) + '</div>' +
      // patch-9: official meta-line anatomy (coords @3dp · elevation · GMT±n)
      '<div class="sub">' + esc(cpMetaLine(p)) + '</div></div>' +
      '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      // patch-4: the quick view rides the OFFICIAL place-quick-view anatomy
      // (mountQuickView fills it; no band without hourly data — honest omit)
      '<section class="place-quick-view modal-quick-view" aria-label="' + esc(t().qv_quick) + '"><div class="quick-view-body" id="cl-cp-qv-host"><span class="quick-none">…</span></div></section>' +
      '<div class="cl-cp-qv-sec">' + esc(t().qv_days) + '</div>' +
      '<div id="cl-cp-qv-days"><div class="cl-cp-qv-loading">…</div></div>' +
      '<div class="cl-cp-qv-sec">' + esc(t().qv_subjects) + '</div>' +
      '<div id="cl-cp-qv-subjects"><div class="cl-cp-qv-loading">…</div></div>' +
      '<div class="cl-cp-qv-actions"><button type="button" class="cl-cp-btn" id="cl-cp-qv-subject-entry">' +
      esc(t().qv_entry) + '</button></div>';
    openOverlay(html, 'cl-cp-qv-modal'); // patch-9: the popup follows its content (no full-height stretch)
    wireClose(); // patch-7: the ✕ closes the popup like every other modal
    if (cpHasNoThemes(p)) { cpPaintNoSubjectPopup(p); return; }
    var entry = els.overlay.querySelector('#cl-cp-qv-subject-entry');
    if (entry) entry.addEventListener('click', function () { ccModal(p); });
    // 逐題材行 render FIRST from the worker's stored per-group evaluation
    // (the card's single truth) — the eval payload then confirms/refines.
    renderPopupSubjects(p);
    api(API + '/' + p.id + '/eval')
      .then(function (res) { return res.json().then(function (body) { return { status: res.status, body: body }; }); })
      .then(function (r) {
      if (!els.overlay.classList.contains('open')) return; // closed meanwhile
      var daysEl = els.overlay.querySelector('#cl-cp-qv-days'), subjEl = els.overlay.querySelector('#cl-cp-qv-subjects');
      if (!daysEl) return;
      if (r.status === 200 && r.body && r.body.ok && Array.isArray(r.body.hourly) && r.body.hourly.length) {
        cpPaintPopup(p, r.body);
      } else {
        // honest: eval still queued / trial stopped — the subject rows keep
        // the worker's verdict; the strip names the missing data instead of
        // rendering invented days.
        daysEl.innerHTML = '<div class="cl-cp-qv-none">' + esc(t().qv_load_fail) + '</div>';
      }
    });
  }
  // ───── patch-3: the ⋯ menu — one fixed-position menu portaled to body ─────
  var MENU_LABELS = { edit: 'm_edit', cc: 'm_cc', refetch: 'm_refetch', del: 'm_del' };
  function ensureMenu() {
    if (els.menu) return els.menu;
    var m = document.createElement('div');
    m.id = 'cl-cp-menu';
    m.className = 'cl-cp-menu';
    m.setAttribute('role', 'menu');
    m.innerHTML =
      '<button type="button" role="menuitem" data-cp-act="edit"><span class="cm-ic">✎</span><span class="cm-txt"></span></button>' +
      '<button type="button" role="menuitem" data-cp-act="cc"><span class="cm-ic">🎞</span><span class="cm-txt"></span></button>' +
      '<button type="button" role="menuitem" data-cp-act="refetch"><span class="cm-ic">🔄</span><span class="cm-txt"></span></button>' +
      '<span class="cm-sep"></span>' +
      '<button type="button" role="menuitem" data-cp-act="del" class="danger"><span class="cm-ic">🗑</span><span class="cm-txt"></span></button>';
    m.addEventListener('click', function (e) {
      var b = e.target.closest('[data-cp-act]');
      if (!b) return;
      e.stopPropagation();
      var place = state.menuPlace;
      closeMenu();
      if (!state.member) { needLoginModal(); return; }
      if (!place) return;
      var act = b.getAttribute('data-cp-act');
      if (act === 'edit') addModal(place);
      else if (act === 'cc') ccModal(place);
      else if (act === 'refetch') refetchIndependent(place);
      else if (act === 'del') delModal(place);
    });
    document.body.appendChild(m);
    els.menu = m;
    return m;
  }
  // CL-APP-08 escape hatch: 「獨立重新抓取」 — detach from the shared fetch
  // group and queue a SOLO refetch (costs 1 quota). The server returns the
  // tri-lingual honest message; the client toasts it and refreshes.
  function refetchIndependent(place) {
    api(API + '/' + encodeURIComponent(place.id) + '/refetch', { method: 'POST' }).then(function (res) {
      res.json().then(function (body) {
        toast((body && body.message && (body.message[currentLang()] || body.message['zh-TW'])) || t().refetch_done);
        refresh();
      });
    }).catch(function () { toast(t().refetch_done); refresh(); });
  }
  function openMenuFor(place, more) {
    var m = ensureMenu();
    // labels re-render on every open (language may have changed since)
    m.querySelectorAll('[data-cp-act]').forEach(function (b) {
      var key = MENU_LABELS[b.getAttribute('data-cp-act')];
      var span = b.querySelector('.cm-txt');
      if (span) span.textContent = t()[key].replace(/^\S+\s*/, '');
    });
    state.menuPlace = place;
    state.menuTrigger = more;
    more.setAttribute('aria-expanded', 'true');
    positionMenu(m, more);
  }
  // position:fixed under the trigger, right-aligned to it; near the viewport
  // bottom (or in a short window) it flips UP so no item is ever clipped;
  // clamped inside the viewport on both axes. Measured while visibility:hidden.
  // CL-APP-08: the taller five-item menu must also clear the FIXED BOTTOM
  // site-nav (≤640px layout) — the effective viewport bottom shrinks by the
  // nav band when it overlays the page.
  function positionMenu(m, more) {
    var navBand = 0;
    try {
      var nav = document.querySelector('.site-nav');
      if (nav) {
        var ns = getComputedStyle(nav);
        var nr = nav.getBoundingClientRect();
        if (ns.position === 'fixed' && nr.bottom > 0 && nr.top < window.innerHeight) navBand = window.innerHeight - nr.top;
      }
    } catch (e) { navBand = 0; }
    var bottomLimit = window.innerHeight - navBand;
    m.style.visibility = 'hidden';
    m.classList.add('open');
    var r = more.getBoundingClientRect();
    var mw = m.offsetWidth, mh = m.offsetHeight;
    var gap = 6, margin = 8;
    var top = r.bottom + gap;
    if (top + mh > bottomLimit - margin && r.top - gap - mh >= margin) top = r.top - gap - mh; // 靠近螢幕下緣 → 向上展開
    top = Math.max(margin, Math.min(top, Math.max(margin, bottomLimit - margin - mh)));
    var left = r.right - mw;
    left = Math.max(margin, Math.min(left, Math.max(margin, window.innerWidth - margin - mw)));
    m.style.top = top + 'px';
    m.style.left = left + 'px';
    m.style.visibility = '';
  }
  function closeMenu() {
    if (state.menuTrigger) { state.menuTrigger.setAttribute('aria-expanded', 'false'); state.menuTrigger = null; }
    state.menuPlace = null;
    if (els.menu) { els.menu.classList.remove('open'); els.menu.style.visibility = ''; }
  }
  // scroll events do NOT bubble — capture phase catches the page scroller AND
  // every inner scroller; resize likewise dismisses (the anchor has moved).
  document.addEventListener('scroll', function () { if (els.menu && els.menu.classList.contains('open')) closeMenu(); }, true);
  window.addEventListener('resize', function () { if (els.menu && els.menu.classList.contains('open')) closeMenu(); });

  document.addEventListener('click', function (e) {
    if (!e.target.closest || !e.target.closest('.cl-cp-menu, .cl-cp-more')) closeMenu();
  });

  // honest counters must follow app.js re-renders (language switches, filter
  // changes) without touching app.js itself
  var mo = null;
  // CL-UI-45: ONE counter painter, driven by app.js's render publish
  // (chaselights:list-rendered) as well as by DOM mutations — so a region
  // switch repaints the 來源 numbers from the NEW region's rows instead of
  // leaving the previous country's card count on screen.
  function syncCountLine() {
    if (!state.data) return;
    if (els.count && !els.count.hidden) {
      var n = officialCardCount(), m = privatePlaces().length;
      els.count.innerHTML = m ? esc(t().count_fmt.replace('{n}', n).replace('{m}', m)) : esc(t().count_fmt_zero.replace('{n}', n));
    }
    if (els.viewBar) {
      var nNow = officialCardCount(), mNow = privatePlaces().length;
      els.viewBar.querySelectorAll('.cl-cp-view-tab').forEach(function (b) {
        var key = b.getAttribute('data-cp-view');
        var cnt = key === 'official' ? nNow : key === 'private' ? mNow : nNow + mNow;
        var slot = b.querySelector('.n'); if (slot) slot.textContent = cnt;
      });
    }
  }
  function watchContainer() {
    if (!watchContainer._wired) {
      watchContainer._wired = true;
      try { document.addEventListener('chaselights:list-rendered', function () { syncCountLine(); }); } catch (e) { /* no document */ }
    }
    if (mo || typeof MutationObserver === 'undefined') return;
    mo = new MutationObserver(function (muts) {
      if (!state.data) return;
      // Only react to REAL structural changes (a card appended/removed); the
      // observer itself observes the private cards' innerHTML, so the
      // signature-guarded updatePrivateCard keeps this from ever looping.
      var relevant = muts.some(function (m) {
        return [...m.removedNodes].some(function (n) { return n.nodeType === 1; }) ||
          [...m.addedNodes].some(function (n) { return n.nodeType === 1 && !(n.classList && n.classList.contains('cl-cp-card')); });
      });
      syncPrivateCards(privatePlaces());
      if (!relevant) return;
      syncCountLine();
    });
    var c = document.getElementById('spots-container');
    if (c) mo.observe(c, { childList: true, subtree: true });
  }

  // ───────────────────────────── modals ─────────────────────────────
  function needLoginModal() {
    openOverlay('<div class="cl-cp-m-head"><div><div class="name">' + esc(t().nl1) + '</div>' +
      '<div class="sub">' + esc(t().nl2) + '</div></div>' +
      '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      '<div style="padding:16px;border:1px dashed var(--cl-border-strong);border-radius:12px;text-align:center">' +
      '<div style="font-size:20px">🔒</div><div style="font-size:12px;color:var(--cl-text-3);margin-top:4px">' + esc(t().nl2) + '</div>' +
      '<div style="display:flex;gap:8px;justify-content:center;margin-top:12px">' +
      '<a href="/api/v1/auth/line/start" style="height:40px;padding:0 18px;border-radius:8px;font-size:13px;font-weight:600;border:1px solid var(--cl-border-strong);background:var(--cl-bg-2);color:var(--cl-text-1);display:inline-flex;align-items:center">LINE</a>' +
      '<a href="/api/v1/auth/google/start" style="height:40px;padding:0 18px;border-radius:8px;font-size:13px;font-weight:600;border:1px solid var(--cl-border-strong);background:var(--cl-bg-2);color:var(--cl-text-1);display:inline-flex;align-items:center">Google</a>' +
      '</div></div>');
    wireClose();
  }
  function wireClose() {
    var c = els.overlay.querySelector('[data-cp-close]');
    if (c) c.addEventListener('click', closeOverlay);
  }
  function startAdd() {
    if (!state.member) { needLoginModal(); return; }
    addModal(null);
  }

  // pin map: schematic graticule; click-to-drop syncs both ways with the
  // lat/lng inputs; DEM elevation + timezone are READ-ONLY auto values.
  function addModal(place) {
    state.editing = place || null;
    state.pin = place ? { lat: String(place.lat), lng: String(place.lng) } : null;
    var isEdit = !!place;
    openOverlay(
      '<div class="cl-cp-m-head"><div><div class="name">' + esc(isEdit ? t().add_edit_title : t().add_title) + '</div>' +
      '<div class="sub">' + esc(t().add_sub) + '</div></div>' +
      '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      '<div class="cl-cp-fld"><label>' + esc(t().qd_name) + '</label>' +
      '<input class="inp" id="cl-cp-name" maxlength="60" placeholder="' + esc(t().qd_name_ph) + '" value="' + esc(place ? place.name : '') + '"></div>' +
      '<div class="cl-cp-fld"><label>' + esc(t().qd_pin) + '</label>' +
      '<div class="cl-cp-pinpick" id="cl-cp-pinpick"></div>' +
      '<div class="hint">' + esc(t().qd_pin_hint) + '</div>' +
      '<div class="cl-cp-f-row" style="margin-top:8px">' +
      '<div class="cl-cp-fld" style="margin-bottom:0"><label>lat</label><input class="inp" id="cl-cp-lat" inputmode="decimal" placeholder="24.8225" style="font-family:var(--cl-mono)" value="' + esc(place ? place.lat : '') + '"></div>' +
      '<div class="cl-cp-fld" style="margin-bottom:0"><label>lng</label><input class="inp" id="cl-cp-lng" inputmode="decimal" placeholder="121.7675" style="font-family:var(--cl-mono)" value="' + esc(place ? place.lng : '') + '"></div>' +
      '</div>' +
      '<div class="cl-cp-geo-row"><button type="button" class="cl-cp-geo-btn" id="cl-cp-geo-btn">' + esc(t().geo_btn) + '</button>' +
      '<span class="cl-cp-geo-note">' + esc(t().geo_note) + '</span></div>' +
      '<div class="cl-cp-geo-status" id="cl-cp-geo-status" role="status" aria-live="polite"></div>' +
      '<div class="cl-cp-ro" id="cl-cp-ro"></div></div>' +
      '<button type="button" class="cl-cp-submit" id="cl-cp-submit">' + esc(isEdit ? t().update : t().create) + '</button>');
    wireClose();
    // patch-2: the name field is the FIRST field and auto-focuses (owner bug:
    // on a short window the field was clipped and the user could not see why
    // 「建立私人點」 stayed disabled). focus() also scrolls it into view.
    var nm = els.overlay.querySelector('#cl-cp-name');
    if (nm) {
      nm.focus();
      // disabled reason lives ON the button (not just grayed-out): recompute
      // on every keystroke, pin change and geo fill
      nm.addEventListener('input', updateSubmitState);
    }
    setupPinPicker(els.overlay.querySelector('#cl-cp-pinpick'));
    ['#cl-cp-lat', '#cl-cp-lng'].forEach(function (sel) {
      els.overlay.querySelector(sel).addEventListener('change', function () {
        state.pin = { lat: els.overlay.querySelector('#cl-cp-lat').value.trim(), lng: els.overlay.querySelector('#cl-cp-lng').value.trim() };
        refreshPin();
      });
      els.overlay.querySelector(sel).addEventListener('input', updateSubmitState);
    });
    els.overlay.querySelector('#cl-cp-submit').addEventListener('click', submitAdd);
    var gb = els.overlay.querySelector('#cl-cp-geo-btn');
    if (gb) gb.addEventListener('click', useMyLocation);
    refreshPin();
  }

  // ── patch-4: real mini-map in the pin picker ────────────────────────────
  // Owner bug (patch-4): the picker was a bare schematic graticule. It now
  // renders a REAL MapLibre basemap (vendored module, same as weather-map).
  // ROOT-CAUSE GUARD: MapLibre initialized inside a hidden/zero-size container
  // lays out tiles and markers broken (the reported 空 grid + misplaced pin).
  // So init is DEFERRED until the modal is visibly open and the container has
  // a non-zero box (rAF poll), then the map is created; a late resize() runs
  // on 'load' as a second brace. Any failure (module/tiles/network, 4s cap)
  // falls back HONESTLY to the old schematic graticule — pin drop always
  // stays possible (click-to-drop + manual lat/lng both survive offline).
  function setupPinPicker(pk) {
    pk.innerHTML = '<span class="cl-cp-pin-hint">' + esc(t().pin_map_loading) + '</span>';
    var token = ++state.pinMapToken;
    var el = pk;
    if (window.__clcpMapLibre === false) { wireSchematicPinDrop(el); refreshPin(); return; } // test seam: force schematic
    // CL-CI-39: no WebGL -> never construct the mini-map (MapLibre throws and
    // leaves a zero-size canvas). Fall back to the schematic pin picker that the
    // 4s timeout path already uses, and expose the state for the acceptance test.
    if (!clcpWebglAvailable()) {
      try { window.__clCpMiniMapFallback = true; } catch (_) {}
      wireSchematicPinDrop(el);
      el.setAttribute('data-minimap', 'unsupported');
      refreshPin();
      return;
    }
    var pollStart = Date.now();
    (function waitBox() {
      if (token !== state.pinMapToken) return; // modal closed/replaced
      var r = el.getBoundingClientRect();
      var open = els.overlay.classList.contains('open');
      if (open && r.width > 8 && r.height > 8) { initMiniMap(el, token); return; }
      if (Date.now() - pollStart > 1500) { wireSchematicPinDrop(el); refreshPin(); return; }
      requestAnimationFrame(waitBox);
    })();
  }
  function clcpWebglAvailable() {
    try {
      var c = document.createElement('canvas');
      return !!(c.getContext('webgl2') || c.getContext('webgl') || c.getContext('experimental-webgl'));
    } catch (_) { return false; }
  }
  function initMiniMap(el, token) {
    import(MAPLIBRE_MODULE).then(function (maplibregl) {
      if (token !== state.pinMapToken || !els.overlay.classList.contains('open')) return;
      var pin = state.pin && isFinite(Number(state.pin.lat)) && isFinite(Number(state.pin.lng))
        ? [Number(state.pin.lng), Number(state.pin.lat)] : null;
      var map = new maplibregl.Map({
        container: el,
        style: 'https://tiles.openfreemap.org/styles/liberty',
        center: pin || [121.0, 23.8],
        zoom: pin ? 11 : 5.6,
        bearing: 0, pitch: 0,
        dragRotate: false, touchPitch: false,
        attributionControl: { compact: true }
      });
      state.miniMap = map;
      state.miniMapReady = false;
      state.miniMapMarker = null;
      try { window.__clCpMiniMap = map; } catch (_) {}
      var failT = setTimeout(function () {
        if (token !== state.pinMapToken || state.miniMapReady) return;
        teardownMiniMap(); wireSchematicPinDrop(el); refreshPin();
      }, 4000);
      map.on('load', function () {
        if (token !== state.pinMapToken) return;
        clearTimeout(failT);
        state.miniMapReady = true;
        map.resize(); // container may have settled after init — re-measure
        refreshPin(); // drop the marker at the current pin (or the honest hint)
      });
      // click-to-drop: clicking anywhere sets the pin there (same contract
      // as the schematic picker, now in real coordinates)
      map.on('click', function (e) {
        applyPin(e.lngLat.lat, e.lngLat.lng, 'map');
      });
      map.on('error', function () { /* individual tile errors are non-fatal */ });
    }).catch(function () {
      if (token !== state.pinMapToken) return;
      wireSchematicPinDrop(el); refreshPin();
    });
  }
  // schematic fallback (pre-patch-4 behaviour): graticule CSS on the container,
  // click → linear lat/lng mapping over the full-world frame
  function wireSchematicPinDrop(pk) {
    teardownMiniMap();
    pk.classList.add('schematic');
    pk.innerHTML = '';
    if (pk._clcpSchematic) return;
    pk._clcpSchematic = true;
    pk.addEventListener('click', function (e) {
      var r = pk.getBoundingClientRect();
      var lat = (84 - (e.clientY - r.top) / r.height * 168);
      var lng = (-180 + (e.clientX - r.left) / r.width * 360);
      applyPin(lat, lng, 'schematic');
    });
  }
  function teardownMiniMap() {
    if (state.miniMap) {
      try { state.miniMap.remove(); } catch (_) {}
      state.miniMap = null; state.miniMapReady = false; state.miniMapMarker = null;
    }
    try { delete window.__clCpMiniMap; } catch (_) { window.__clCpMiniMap = undefined; }
  }
  // single pin-mutation entry point — map click, marker drag, geo fill,
  // schematic click and manual typing all funnel through here
  function applyPin(lat, lng, source) {
    lat = Number(lat); lng = Number(lng);
    if (!isFinite(lat) || !isFinite(lng)) return;
    state.pin = { lat: lat.toFixed(4), lng: lng.toFixed(4) };
    state.pinSource = source || 'input';
    var latEl = els.overlay.querySelector('#cl-cp-lat'), lngEl = els.overlay.querySelector('#cl-cp-lng');
    if (latEl) latEl.value = state.pin.lat;
    if (lngEl) lngEl.value = state.pin.lng;
    updateSubmitState();
    if (source === 'map' || source === 'schematic') lookupPinInfo();
    refreshPin();
  }
  // 📍 current location — one implementation (web-v2, this file). The browser
  // Geolocation API works in the APP WebView over https; inside the Capacitor
  // native shell the @capacitor/geolocation plugin (registered in apps/mobile)
  // takes precedence when present — never a second copy in the mobile shell.
  function geoGetPosition(opts) {
    if (typeof window.__clcpGeo === 'function') return window.__clcpGeo(opts); // test seam
    var cap = window.Capacitor;
    if (cap && cap.isNativePlatform && cap.isNativePlatform() && cap.Plugins && cap.Plugins.Geolocation) {
      return cap.Plugins.Geolocation.getCurrentPosition(opts);
    }
    if (!navigator.geolocation) return Promise.reject({ code: 0, message: 'geolocation unavailable' });
    return new Promise(function (resolve, reject) {
      navigator.geolocation.getCurrentPosition(resolve, reject, opts);
    });
  }
  function useMyLocation() {
    var btn = els.overlay.querySelector('#cl-cp-geo-btn');
    if (!btn || btn.disabled) return;
    var status = els.overlay.querySelector('#cl-cp-geo-status');
    btn.disabled = true;
    if (status) status.textContent = t().geo_working;
    geoGetPosition({ enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }).then(function (pos) {
      if (!els.overlay.classList.contains('open')) return;
      var c = pos && pos.coords;
      var lat = c && Number(c.latitude), lng = c && Number(c.longitude);
      if (!isFinite(lat) || !isFinite(lng)) throw { code: 0 };
      applyPin(lat, lng, 'geo'); // fills the map mark + auto DEM/timezone + submit-ready
      if (status) status.textContent = '';
      var b2 = els.overlay.querySelector('#cl-cp-geo-btn'); if (b2) b2.disabled = false;
    }).catch(function (err) {
      if (!els.overlay.classList.contains('open')) return;
      var st = els.overlay.querySelector('#cl-cp-geo-status');
      var msg = err && err.code === 1 ? t().geo_denied : err && err.code === 3 ? t().geo_timeout : t().geo_error;
      if (st) st.textContent = msg; // honest failure — manual pin/lat-lng stays
      var b2 = els.overlay.querySelector('#cl-cp-geo-btn'); if (b2) b2.disabled = false;
    });
  }
  // patch-2: the disabled submit button SHOWS the reason (「請先輸入景點名稱」/
  // 「請先落釘或輸入經緯度」) instead of just graying out — the owner could not
  // see a hidden name field, so a gray button with no explanation read as a
  // dead end. ready = name AND finite lat/lng.
  function updateSubmitState() {
    var su = els.overlay.querySelector('#cl-cp-submit');
    if (!su) return;
    var nameEl = els.overlay.querySelector('#cl-cp-name');
    var name = nameEl ? nameEl.value.trim() : '';
    var latEl = els.overlay.querySelector('#cl-cp-lat'), lngEl = els.overlay.querySelector('#cl-cp-lng');
    var lat = latEl ? parseFloat(latEl.value) : NaN, lng = lngEl ? parseFloat(lngEl.value) : NaN;
    var ok = !!name && isFinite(lat) && isFinite(lng);
    su.classList.toggle('ready', ok);
    su.style.cursor = ok ? 'pointer' : 'not-allowed';
    su.textContent = ok ? (state.editing ? t().update : t().create) : (!name ? t().reason_name : t().reason_pin);
  }
  function pinXY() {
    if (!state.pin) return null;
    var lat = Number(state.pin.lat), lng = Number(state.pin.lng);
    if (!isFinite(lat) || !isFinite(lng)) return null;
    return { left: ((lng + 180) / 360 * 100), top: ((84 - lat) / 168 * 100) };
  }
  function refreshPin() {
    var pk = els.overlay.querySelector('#cl-cp-pinpick');
    var ro = els.overlay.querySelector('#cl-cp-ro');
    var xy = pinXY();
    if (xy) {
      // patch-4: with a live mini-map the pin is a draggable MapLibre marker
      // (two-way: marker dragend and map click both re-sync lat/lng); the
      // schematic overlay span is only for the fallback graticule mode.
      if (state.miniMap && state.miniMapReady) {
        syncMiniMapMarker(Number(state.pin.lng), Number(state.pin.lat));
        // manual/geo pin: bring the map to it (marker drags keep the camera)
        if (state.pinSource !== 'map') state.miniMap.jumpTo({ center: [Number(state.pin.lng), Number(state.pin.lat)] });
      } else if (pk && pk.classList.contains('schematic')) {
        pk.innerHTML = '<span class="cl-cp-pinmark" style="left:' + xy.left.toFixed(1) + '%;top:' + Math.max(2, Math.min(98, xy.top)).toFixed(1) + '%"></span>';
      }
      ro.innerHTML = '<span class="pill">🏔 <span>' + esc(t().ro_elev) + '</span> <b id="cl-cp-elev">…</b></span>' +
        '<span class="pill">🕐 <span>' + esc(t().ro_tz) + '</span> <b id="cl-cp-tz">…</b></span>';
      lookupPinInfo();
      updateSubmitState();
    } else {
      if (pk && state.miniMap && state.miniMapReady) removeMiniMapMarker();
      else if (pk) pk.innerHTML = '<span class="cl-cp-pin-hint">' + esc(t().ro_pending) + '</span>';
      ro.innerHTML = '<span class="pill" style="color:var(--cl-text-3)">🏔 🕐 ' + esc(t().ro_pending) + '</span>';
      updateSubmitState();
    }
  }
  function syncMiniMapMarker(lng, lat) {
    var map = state.miniMap;
    if (!map || !state.miniMapReady) return;
    if (!state.miniMapMarker) {
      var maplibregl = map.constructor && window.__clCpMiniMapLibre;
      if (!maplibregl) { // marker created lazily via stored module ref
        import(MAPLIBRE_MODULE).then(function (m) {
          window.__clCpMiniMapLibre = m;
          if (state.miniMap === map) { state.miniMapMarker = makeMiniMarker(m, map); syncMiniMapMarker(lng, lat); }
        });
        return;
      }
      state.miniMapMarker = makeMiniMarker(maplibregl, map);
    }
    state.miniMapMarker.setLngLat([lng, lat]);
    state.miniMapMarker.addTo(map);
    try { window.__clCpMiniMapMarker = state.miniMapMarker; } catch (_) {} // test seam
  }
  function makeMiniMarker(maplibregl, map) {
    var marker = new maplibregl.Marker({ draggable: true });
    // 拖曳地圖釘同步欄位（owner 驗收項）：dragend → fields + DEM/tz relookup
    marker.on('dragend', function () {
      var ll = marker.getLngLat();
      if (els.overlay.classList.contains('open')) applyPin(ll.lat, ll.lng, 'map');
    });
    return marker;
  }
  function removeMiniMapMarker() {
    if (state.miniMapMarker) {
      try { state.miniMapMarker.remove(); } catch (_) {}
      state.miniMapMarker = null;
    }
  }
  function lookupPinInfo() {
    if (!state.pin) return;
    api(API + '/pin_info?lat=' + encodeURIComponent(state.pin.lat) + '&lng=' + encodeURIComponent(state.pin.lng))
      .then(function (res) { return res.json(); })
      .then(function (body) {
        if (!els.overlay.classList.contains('open')) return;
        var elevEl = els.overlay.querySelector('#cl-cp-elev'), tzEl = els.overlay.querySelector('#cl-cp-tz');
        if (!elevEl) return;
        if (body && body.ok) {
          elevEl.textContent = body.elevation != null ? body.elevation + ' m' : '—';
          tzEl.textContent = body.timezone ? body.timezone + ' · UTC' + (body.utcOffsetSeconds >= 0 ? '+' : '') + (body.utcOffsetSeconds / 3600) : '—';
          if (body.elevationOutlier) { elevEl.textContent += ' ⚠'; toast(t().ro_elev_outlier); }
          state.pinInfo = body;
        } else { elevEl.textContent = '—'; tzEl.textContent = '—'; }
      }).catch(function () { /* honest dashes stay */ });
  }
  function submitAdd() {
    var name = els.overlay.querySelector('#cl-cp-name').value.trim();
    var lat = parseFloat(els.overlay.querySelector('#cl-cp-lat').value), lng = parseFloat(els.overlay.querySelector('#cl-cp-lng').value);
    if (!name || !isFinite(lat) || !isFinite(lng)) return;
    var payload = { name: name, lat: lat, lng: lng };
    if (state.pinInfo && state.pinInfo.elevation != null && !state.pinInfo.elevationOutlier) payload.elevation = state.pinInfo.elevation;
    if (state.pinInfo && state.pinInfo.timezone) payload.timezone = state.pinInfo.timezone;
    var url = state.editing ? API + '/' + state.editing.id : API;
    api(url, { method: state.editing ? 'PATCH' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (res) { return res.json().then(function (body) { return { status: res.status, body: body }; }); })
      .then(function (r) {
        if (r.status === 403 || r.status === 429) { toast(r.body && r.body.message || r.body && r.body.error || '403'); return; }
        if (r.status !== 200) { toast((r.body && r.body.error) || ('HTTP ' + r.status)); return; }
        var b = r.body || {};
        if (b.reminder) toast(b.reminder);
        var done =
          '<div class="cl-cp-m-head"><div><div class="name">' + esc(name) + '</div></div>' +
          '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
          '<div class="cl-cp-done"><div class="d1">' + esc(state.editing ? t().done1_edit : t().done1) + '</div>' +
          '<div class="d2">' + esc(lat) + ' · ' + esc(lng) + (payload.elevation != null ? ' · ' + esc(payload.elevation) + ' m' : '') + '</div>' +
          '<div class="d3">' + esc(b.degraded ? (b.degradedMessage && b.degradedMessage[currentLang()] || '') : (state.editing ? '' : t().done_deferred)) + '</div>' +
          '<button type="button" id="cl-cp-done-btn">' + esc(t().close) + '</button></div>';
        openOverlay(done);
        wireClose();
        var dn = els.overlay.querySelector('#cl-cp-done-btn'); if (dn) dn.addEventListener('click', closeOverlay);
        refresh();
      });
  }

  // ───────────────────────── conditions form (owner ruling 2026-11-15) ─────
  // Three paths into the SAME five-parameter schema — the form always
  // submits CONCRETE values (the CL-UI-99 engine never sees semantics):
  //   ① main path: semantic dropdowns (cloud / fog / rain) whose trilingual
  //      option → value mapping is HARDCODED (deterministic, zero cost) and
  //      shown NEXT TO the select (transparent: 「→ 低雲 ≤20%」);
  //   ② copy an official genre template as the starting point, then tweak;
  //   ③ <details> advanced: the original raw numeric inputs (power user).
  var CC_SEMANTIC = {
    cloud: {
      key: 'cloud_low_max',
      options: {
        'zh-TW': [['min', '越少越好', '低雲 ≤20%'], ['half', '半晴半雲', '低雲 ≤50%'], ['any', '不限', '不帶雲量條件'], ['more', '越多越好', '低雲 ≥70%']],
        'en': [['min', 'As little as possible', 'low cloud ≤20%'], ['half', 'Half sun, half cloud', 'low cloud ≤50%'], ['any', "Don't care", 'no cloud condition'], ['more', 'The more the better', 'low cloud ≥70%']],
        'ja': [['min', 'できるだけ少ない', '低雲 ≤20%'], ['half', '半分晴れ半分雲', '低雲 ≤50%'], ['any', 'こだわらない', '雲の条件なし'], ['more', '多いほうが良い', '低雲 ≥70%']],
      },
      // patch-5 ⑤: 'more' maps to cloud_low_min (the _min counterpart of the
      // _max keys — the same direction the worker schema/engine gained), so a
      // cloud-sea-style preference can be configured manually without the
      // engine pretending to know cloud-base height.
      values: { min: 20, half: 50, any: 100, more: 70 },
    },
    fog: {
      key: 'visibility_min_km',
      options: {
        'zh-TW': [['none', '完全不能有霧', '能見度 ≥10km'], ['thin', '薄霧可以', '能見度 ≥5km'], ['any', '不在乎', '不限']],
        'en': [['none', 'No fog at all', 'visibility ≥10km'], ['thin', 'Thin mist is fine', 'visibility ≥5km'], ['any', 'Do not care', 'no limit']],
        'ja': [['none', '霧は完全に不可', '視程 ≥10km'], ['thin', '薄霧は可', '視程 ≥5km'], ['any', 'こだわらない', '制限なし']],
      },
      values: { none: 10, thin: 5, any: 0 },
    },
    rain: {
      key: 'precip_max_mmh',
      options: {
        'zh-TW': [['no', '不能下雨', '降水 <0.2mm/h'], ['drizzle', '毛毛雨可以', '降水 <0.5mm/h'], ['any', '不在乎', '不限']],
        'en': [['no', 'No rain', 'precip <0.2mm/h'], ['drizzle', 'Drizzle is fine', 'precip <0.5mm/h'], ['any', 'Do not care', 'no limit']],
        'ja': [['no', '雨は不可', '降水 <0.2mm/h'], ['drizzle', '小雨なら可', '降水 <0.5mm/h'], ['any', 'こだわらない', '制限なし']],
      },
      values: { no: 0.2, drizzle: 0.5, any: 200 },
    },
  };
  // ② genre copy-starters: per official genre, the semantic starting point
  // (cloud/fog/rain + window) — the user then tweaks ONE thing. Deterministic
  // hardcoded starters; the SUBMITTED values are still the concrete ones.
  var CC_GENRE_STARTERS = {
    mountain_view: { cloud: 'any', fog: 'thin', rain: 'no', window: ['05:30', '19:00'] },
    overlook: { cloud: 'half', fog: 'none', rain: 'no', window: ['06:00', '18:00'] },
    sunrise: { cloud: 'half', fog: 'thin', rain: 'no', window: ['04:30', '06:30'] },
    sunset: { cloud: 'half', fog: 'thin', rain: 'no', window: ['16:30', '18:30'] },
    golden: { cloud: 'half', fog: 'thin', rain: 'no', window: ['05:00', '07:00'] },
    city_night: { cloud: 'any', fog: 'thin', rain: 'no', window: ['19:00', '23:00'] },
    night_sky: { cloud: 'min', fog: 'none', rain: 'no', window: ['21:00', '03:00'] },
    cloud_sea: { cloud: 'more', fog: 'any', rain: 'no', window: ['04:30', '07:00'] },
    overcast_soft: { cloud: 'any', fog: 'thin', rain: 'drizzle', window: ['06:00', '17:00'] },
    blue_hour: { cloud: 'half', fog: 'thin', rain: 'no', window: ['04:40', '05:40'] },
    sky_glow: { cloud: 'half', fog: 'thin', rain: 'no', window: ['17:30', '19:00'] },
    fog_mist: { cloud: 'any', fog: 'any', rain: 'no', window: ['05:00', '08:00'] },
    reflection: { cloud: 'half', fog: 'thin', rain: 'no', window: ['06:00', '09:00'] },
    sunbeam: { cloud: 'half', fog: 'thin', rain: 'no', window: ['06:00', '16:00'] },
    milky_way: { cloud: 'min', fog: 'none', rain: 'no', window: ['22:00', '02:00'] },
    long_exposure: { cloud: 'any', fog: 'any', rain: 'drizzle', window: ['18:00', '21:00'] },
    city_view: { cloud: 'any', fog: 'thin', rain: 'no', window: ['17:00', '21:00'] },
    coast: { cloud: 'any', fog: 'thin', rain: 'drizzle', window: ['05:00', '18:00'] },
    forest: { cloud: 'any', fog: 'thin', rain: 'drizzle', window: ['06:00', '16:00'] },
    geology: { cloud: 'half', fog: 'thin', rain: 'no', window: ['06:00', '18:00'] },
    lake: { cloud: 'half', fog: 'thin', rain: 'no', window: ['05:30', '18:00'] },
    // patch-5 ④: seasonal starters prefill the 適用月份 multi-select (months
    // left out = all year). Same schema as the worker's custom_conditions blob.
    snow_scene: { cloud: 'any', fog: 'thin', rain: 'drizzle', window: ['06:00', '17:00'], months: [12, 1, 2] },
    snow_ice: { cloud: 'any', fog: 'thin', rain: 'drizzle', window: ['08:00', '16:00'], months: [12, 1, 2] },
    seasonal_plant: { cloud: 'any', fog: 'thin', rain: 'no', window: ['06:00', '18:00'], months: [3, 4] },
    firefly: { cloud: 'any', fog: 'thin', rain: 'drizzle', window: ['19:00', '22:00'], months: [4, 5] },
    drift_ice: { cloud: 'any', fog: 'thin', rain: 'no', window: ['08:00', '16:00'], months: [1, 2] },
  };
  function semanticValue(axis, val) {
    var m = CC_SEMANTIC[axis];
    if (!m || val == null) return null;
    if (axis === 'cloud') return val === 'any' ? null : m.values[val]; // any → unconstrained
    if (axis === 'fog') return val === 'any' ? null : m.values[val];
    if (axis === 'rain') return val === 'any' ? null : m.values[val];
    return m.values[val];
  }
  function semanticMappedLabel(axis, val) {
    var m = CC_SEMANTIC[axis]; if (!m) return '';
    var opts = m.options[currentLang()] || m.options['zh-TW'];
    for (var i = 0; i < opts.length; i++) if (opts[i][0] === val) return opts[i][2];
    return '';
  }

  // ✨ AI one-sentence description (owner ruling: the semantic dropdowns stay,
  // the AI is the REQUIRED companion — free-text in any language → strict-JSON
  // suggestion → fills the semantic selects; the user then tweaks; the form
  // submits CONCRETE values only). Entry hidden + honest when the worker
  // reports the LLM key missing (fail-closed).
  function aiParseConfigCheck() {
    if (state.aiEnabled !== undefined) return Promise.resolve(state.aiEnabled);
    return api('/api/v1/conditions/parse').then(function (res) { return res.json(); })
      .then(function (b) { state.aiEnabled = !!(b && b.enabled); return state.aiEnabled; })
      .catch(function () { state.aiEnabled = false; return false; });
  }
  function aiParseBlock() {
    return '<div class="cl-cp-ai" id="cl-cp-ai">' +
      '<label for="cl-cp-ai-text">✨ ' + esc(t().ai_hint) + '</label>' +
      '<div style="display:flex;gap:6px">' +
      '<input id="cl-cp-ai-text" class="inp" style="flex:1" placeholder="' + esc(t().ai_ph) + '" maxlength="500">' +
      '<button type="button" class="cl-cp-ai-btn" id="cl-cp-ai-go">' + esc(t().ai_btn) + '</button></div>' +
      '<div class="cl-cp-ai-note" id="cl-cp-ai-note" role="status" aria-live="polite"></div></div>';
  }
  function wireAiParse() {
    var go = els.overlay.querySelector('#cl-cp-ai-go');
    if (!go) return;
    go.addEventListener('click', function () {
      var input = els.overlay.querySelector('#cl-cp-ai-text');
      var note = els.overlay.querySelector('#cl-cp-ai-note');
      var text = input && input.value.trim();
      if (!text) return;
      note.textContent = t().ai_working;
      api('/api/v1/conditions/parse', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: text }) })
        .then(function (res) { return res.json().then(function (b) { return { status: res.status, body: b }; }); })
        .then(function (r) {
          if (r.status === 200 && r.body && r.body.ok) {
            var s = r.body.suggestions || {};
            // patch-5 ③: conflicting conditions — the AI applied NOTHING and
            // the honest conflict message asks the user to pick one. The form
            // keeps whatever the user had set before (never half-filled).
            if (s.conflict) {
              note.textContent = t().ai_conflict.replace('{m}', s.conflict);
              return;
            }
            var fill = { cloud: '#cl-cp-sem-cloud', fog: '#cl-cp-sem-fog', rain: '#cl-cp-sem-rain' };
            Object.keys(fill).forEach(function (axis) {
              var sel = els.overlay.querySelector(fill[axis]);
              if (sel && s[axis]) { sel.value = s[axis]; sel.dispatchEvent(new Event('change')); }
            });
            if (s.wind_max_ms != null) { var w = els.overlay.querySelector('#cl-cp-cc-wind'); if (w) w.value = String(s.wind_max_ms); }
            // patch-2: the AI may return the windows array (anchor/multi) — fill
            // the segment editor; a legacy flat window fills segment 0 fixed.
            if (Array.isArray(s.windows) && s.windows.length) {
              cpWinState = s.windows.slice(0, 2).map(function (seg) {
                var st = seg.type === 'fixed' ? { type: 'fixed', start: seg.start || '', end: seg.end || '' } : { type: seg.type, offset_minutes: seg.offset_minutes || 0 };
                if (seg.type !== 'fixed' && seg.span_minutes != null && seg.span_minutes > 0) st.span_minutes = seg.span_minutes;
                return st;
              });
              cpRenderWinArea();
            } else if (s.window_start) {
              cpWinState = [{ type: 'fixed', start: s.window_start, end: s.window_end || '' }];
              cpRenderWinArea();
            }
            if (s.lead_minutes != null) { var l = els.overlay.querySelector('#cl-cp-cc-lead'); if (l) l.value = String(s.lead_minutes); }
            els.overlay.querySelector('#cl-cp-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
            var conf = Math.round((s.confidence || 0) * 100);
            note.textContent = t().ai_done.replace('{c}', conf);
          } else {
            var msg = r.body && r.body.message && (r.body.message[currentLang()] || r.body.message['zh-TW']);
            // fail-closed CONCRETE reason (patch-2): the tri-lingual message
            // stays stable, but the upstream detail (status/snippet) surfaces
            // so a broken key/model is visible instead of a silent 解析失敗.
            var detail = r.body && r.body.detail;
            note.textContent = msg || (detail ? '⚠ ' + detail : t().ai_fail);
          }
        })
        .catch(function () { note.textContent = t().ai_fail; });
    });
  }

  // ─── patch-8: 「掛題材·條件」 = theme LIST manager (multi-group per place) ───
  // Up to 5 condition groups per place (worker cap); each group = name_i18n +
  // the CL-UI-99 blob (months inside). Duplicate names are NOT blocked (owner
  // ruling). CRUD never refetches — the weather is fetched once per place and
  // every group judges the SAME stored hourly rows.
  function ccModal(place) {
    var groups = Array.isArray(place.themeGroups) ? place.themeGroups : [];
    var used = groups.length;
    var cap = (place.themes && place.themes.cap) || 5;
    var lang = currentLang();
    var rows = groups.map(function (g) {
      var ge = g.evaluation || {};
      var bcls = ge.tier === 'rec' ? 'cl-cp-tier-rec' : ge.tier === 'shoot' ? 'cl-cp-tier-shoot' : ge.tier === 'no' ? 'cl-cp-tier-no' : 'cl-cp-tier-pending';
      var bg = ge.tier === 'rec' ? '✓' : ge.tier === 'shoot' ? '○' : ge.tier === 'no' ? '✗' : '⏳';
      var tail = ge.tier === 'no' && ge.reason ? ' · ' + ge.reason : (ge.tier === 'rec' && ge.window ? ' · ' + ge.window : '');
      return '<div class="cl-cp-theme-row" data-theme-id="' + esc(g.id) + '">' +
        '<span class="cl-cp-tier ' + bcls + '">' + bg + '</span>' +
        '<div class="cl-cp-theme-info"><div class="n">' + esc(themeDisplayName(g)) + '</div>' +
        '<div class="s">' + esc((ccSummary(g.conditions, lang) || '—') + tail) + '</div></div>' +
        '<div class="cl-cp-theme-acts">' +
        '<button type="button" data-cp-th-act="edit" aria-label="✎ 編輯">✎</button>' +
        '<button type="button" data-cp-th-act="del" class="danger" aria-label="🗑 刪除">🗑</button>' +
        '</div></div>';
    }).join('');
    var addArea = used >= cap
      ? '<div class="cl-cp-th-cap">' + esc(t().th_cap_note) + '</div>'
      : '<button type="button" class="cl-cp-btn" id="cl-cp-th-add">' + esc(t().th_add) + '</button>';
    openOverlay(
      '<div class="cl-cp-m-head"><div><div class="name">🎞 ' + esc(t().th_title) + '</div>' +
      '<div class="sub">' + esc(t().th_sub) + ' · ' + esc(place.name) + '</div></div>' +
      '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      '<div class="cl-cp-th-count">' + esc(t().th_count.replace('{n}', used).replace('{c}', cap)) + '</div>' +
      (rows || '<div class="cl-cp-th-empty">' + esc(t().th_empty) + '</div>') +
      addArea, 'cl-cp-list-modal');
    wireClose();
    var add = els.overlay.querySelector('#cl-cp-th-add');
    if (add) add.addEventListener('click', function () { themeFormModal(place, null); });
    els.overlay.querySelectorAll('.cl-cp-theme-row').forEach(function (row) {
      var gid = row.getAttribute('data-theme-id');
      var g = groups.find(function (x) { return x.id === gid; });
      if (!g) return;
      var e = row.querySelector('[data-cp-th-act="edit"]');
      if (e) e.addEventListener('click', function () { themeFormModal(place, g); });
      var d = row.querySelector('[data-cp-th-act="del"]');
      if (d) d.addEventListener('click', function () { delThemeModal(place, g); });
    });
  }
  // after a theme CRUD succeeds the list reopens from the REFRESHED data —
  // poll until the group set differs from the snapshot (never a stale modal)
  function waitThemeList(place, beforeIds) {
    var t0 = Date.now();
    (window.__dbg3 = window.__dbg3 || []).push('wait start before=' + beforeIds);
    (function poll() {
      var p = privatePlaces().find(function (x) { return x.id === place.id; });
      var ids = p ? (p.themeGroups || []).map(function (g) { return g.id; }).join(',') : null;
      (window.__dbg3 = window.__dbg3 || []).push('poll p=' + (p ? p.id : 'null') + ' ids=' + ids + ' before=' + beforeIds + ' data=' + (!!state.data));
    if (p && ids !== beforeIds) { (window.__dbg3 = window.__dbg3 || []).push('REOPEN'); ccModal(p); return; }
      if (Date.now() - t0 > 5000) return; // honest stop — the next render refreshes the list
      setTimeout(poll, 120);
    })();
  }
  function delThemeModal(place, theme) {
    openOverlay(
      '<div class="cl-cp-m-head"><div><div class="name">' + esc(t().th_del_title) + '</div></div>' +
      '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      '<div class="cl-cp-delbox"><div class="d1">🗑 ' + esc(themeName(theme)) + '</div>' +
      '<div class="cl-cp-delacts"><button type="button" class="cancel" id="cl-cp-th-del-cancel">' + esc(t().del_cancel) + '</button>' +
      '<button type="button" class="confirm" id="cl-cp-th-del-confirm">🗑 ' + esc(t().m_del.replace(/^\S+\s*/, '')) + '</button></div></div>');
    wireClose();
    els.overlay.querySelector('#cl-cp-th-del-cancel').addEventListener('click', closeOverlay);
    els.overlay.querySelector('#cl-cp-th-del-confirm').addEventListener('click', function () {
      var beforeIds = (place.themeGroups || []).map(function (g) { return g.id; }).join(',');
      api(API + '/' + place.id + '/themes/' + theme.id, { method: 'DELETE' })
        .then(function (res) { return res.json().then(function (body) { return { status: res.status, body: body }; }); })
        .then(function (r) {
          if (r.status !== 200) { toast((r.body && r.body.error) || ('HTTP ' + r.status)); return; }
          toast(t().th_deleted);
          refresh();
          closeOverlay();
          waitThemeList(place, beforeIds);
        });
    });
  }
  // per-theme form — CL-UI-99 five parameter groups (same schema as
  // notify_rules.custom_conditions; the worker re-validates) + the group name
  // (name_i18n: the current language writes its own entry, other locales are
  // preserved on rename; the zh-TW anchor `name` carries the fallback)
  function themeFormModal(place, theme) {
    var cc = (theme && theme.conditions) || {};
    cpWinState = cpWindowSegsOf(cc).slice(0, 2);
    function v(k) { return cc[k] == null ? '' : String(cc[k]); }
    var lang = currentLang();
    var genreNames = genreShortNames();
    var genreOpts = Object.keys(CC_GENRE_STARTERS).map(function (k) {
      var n = genreNames[k] || k;
      return '<option value="' + k + '">' + esc(n) + '</option>';
    }).join('');
    var aiEnabled = state.aiEnabled === true;
    var semSel = function (axis, label) {
      var m = CC_SEMANTIC[axis];
      var opts = m.options[lang] || m.options['zh-TW'];
      var cur = currentSemantic(axis, cc);
      return '<div class="cl-cp-ccp wide"><label>' + esc(label) + '</label>' +
        '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">' +
        '<select id="cl-cp-sem-' + axis + '" class="cl-cp-sem-select">' +
        opts.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === cur ? ' selected' : '') + '>' + esc(o[1]) + '</option>'; }).join('') +
        '</select><span class="cl-cp-sem-map" id="cl-cp-sem-map-' + axis + '">→ ' + esc(semanticMappedLabel(axis, cur)) + '</span></div></div>';
    };
    openOverlay(
      '<div class="cl-cp-m-head"><div><div class="name">' + (theme ? '✎ ' : '＋ ') + esc(t().th_title) + '</div>' +
      '<div class="sub">' + esc(t().th_name) + ' · ' + esc(place.name) + '</div></div>' +
      '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      '<div class="cl-cp-fld"><label>' + esc(t().th_name) + '</label>' +
      '<input class="inp" id="cl-cp-theme-name" maxlength="40" placeholder="' + esc(t().th_name_ph) + '" value="' + esc(theme ? themeName(theme) : '') + '"></div>' +
      (aiEnabled ? aiParseBlock() : '') +
      // CL-APP-09 patch-2 item ④ (owner): 複製官方題材 sits right BELOW the AI
      // parse block and ABOVE the manual condition options — it is a starter
      // picker, not a parameter group.
      '<div class="cl-cp-fld" style="margin-bottom:8px"><label>' + esc(t().copy_genre) + '</label>' +
      '<select id="cl-cp-cc-genre" class="inp"><option value="">— ' + esc(t().copy_genre_none) + ' —</option>' + genreOpts + '</select>' +
      '<div class="hint">' + esc(t().copy_genre_hint) + '</div></div>' +
      '<div class="cl-cp-cc-params">' +
      semSel('cloud', t().sem_cloud) +
      semSel('fog', t().sem_fog) +
      semSel('rain', t().sem_rain) +
      '<div class="cl-cp-ccp wide"><label>' + esc(t().p_window) + '</label>' +
      '<div id="cl-cp-win-area"></div>' +
      '</div>' +
      '<div class="cl-cp-ccp wide" id="cl-cp-cc-months-wrap"><label>' + esc(t().p_months) + '</label>' +
      '<div class="cl-cp-cc-months" id="cl-cp-cc-months">' + monthsHtml(cc.months) + '</div>' +
      '<div class="hint">' + esc(t().p_months_hint) + '</div></div>' +
      '</div>' +
      '<details class="cl-cp-cc-advanced" id="cl-cp-cc-adv"><summary>' + esc(t().adv_toggle) + '</summary>' +
      '<div class="cl-cp-cc-params" style="margin-top:8px">' +
      ccp('cl-cp-cc-low', t().p_low, v('cloud_low_max')) +
      ccp('cl-cp-cc-lowmin', t().p_lowmin, v('cloud_low_min')) +
      ccp('cl-cp-cc-mid', t().p_mid, v('cloud_mid_max')) +
      ccp('cl-cp-cc-high', t().p_high, v('cloud_high_max')) +
      ccp('cl-cp-cc-precip', t().p_precip, v('precip_max_mmh')) +
      ccp('cl-cp-cc-vis', t().p_vis, v('visibility_min_km')) +
      ccp('cl-cp-cc-wind', t().p_wind, v('wind_max_ms')) +
      ccp('cl-cp-cc-lead', t().p_lead, v('lead_minutes')) +
      '</div></details>' +
      '<div class="cl-cp-cc-preview"><span style="color:var(--cl-text-3)">' + esc(t().cc_prev) + '</span><span class="k" id="cl-cp-cc-prev">' + esc(ccSummary(cc, lang) || t().cc_prev_none) + '</span></div>' +
      '<button type="button" class="cl-cp-submit" id="cl-cp-cc-submit">' + esc(t().th_create) + '</button>');
    wireClose();
    if (aiEnabled) wireAiParse();
    cpRenderWinArea();
    var sync = function () {
      // semantic → concrete: write the mapped value into the advanced input
      // (the advanced inputs stay the single source of truth) and refresh
      // the transparent mapping labels + preview.
      ['cloud', 'fog', 'rain'].forEach(function (axis) {
        var sel = els.overlay.querySelector('#cl-cp-sem-' + axis);
        if (!sel) return;
        var val = sel.value;
        els.overlay.querySelector('#cl-cp-sem-map-' + axis).textContent = '→ ' + semanticMappedLabel(axis, val);
        // patch-5 ⑤: 'more' routes to the _min floor input; every other cloud
        // value clears the floor (the two directions never both constrain)
        var lowmin = els.overlay.querySelector('#cl-cp-cc-lowmin');
        var target = { cloud: '#cl-cp-cc-low', fog: '#cl-cp-cc-vis', rain: '#cl-cp-cc-precip' }[axis];
        var inp = els.overlay.querySelector(target);
        if (axis === 'cloud' && lowmin) {
          if (val === 'more') { lowmin.value = String(CC_SEMANTIC.cloud.values.more); if (inp) inp.value = ''; return; }
          lowmin.value = '';
        }
        if (!inp) return;
        var mapped = semanticValue(axis, val);
        inp.value = mapped == null ? '' : String(mapped);
      });
      els.overlay.querySelector('#cl-cp-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
    };
    ['cloud', 'fog', 'rain'].forEach(function (axis) {
      var sel = els.overlay.querySelector('#cl-cp-sem-' + axis);
      if (sel) sel.addEventListener('change', sync);
    });
    els.overlay.querySelectorAll('.cl-cp-cc-advanced input').forEach(function (inp) {
      inp.addEventListener('change', function () {
        els.overlay.querySelector('#cl-cp-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
      });
    });
    // patch-5 ④: 適用月份 chips update the preview too
    var monthsWrap = els.overlay.querySelector('#cl-cp-cc-months');
    if (monthsWrap) monthsWrap.querySelectorAll('input[type="checkbox"]').forEach(function (b) {
      b.addEventListener('change', function () {
        els.overlay.querySelector('#cl-cp-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
      });
    });
    var genreSel = els.overlay.querySelector('#cl-cp-cc-genre');
    if (genreSel) genreSel.addEventListener('change', function () {
      var starter = CC_GENRE_STARTERS[genreSel.value];
      if (!starter) return;
      ['cloud', 'fog', 'rain'].forEach(function (axis) {
        var sel = els.overlay.querySelector('#cl-cp-sem-' + axis);
        if (sel && starter[axis]) sel.value = starter[axis];
      });
      // patch-2: the starter's window fills SEGMENT 0 (keep it a fixed span)
      cpWinState = [{ type: 'fixed', start: starter.window[0], end: starter.window[1] }];
      cpRenderWinArea();
      // patch-5 ④: seasonal starters prefill the 適用月份 chips (snow/櫻花類)
      var monthsWrap = els.overlay.querySelector('#cl-cp-cc-months');
      if (monthsWrap) {
        var want = Array.isArray(starter.months) ? starter.months : [];
        monthsWrap.querySelectorAll('input[type="checkbox"]').forEach(function (b) {
          b.checked = want.indexOf(Number(b.value)) >= 0;
        });
      }
      sync();
    });
    // disabled-reason pattern (patch-2 family): the submit button PRINTS what
    // is missing — a group needs a name before it can be saved
    var nameInput = els.overlay.querySelector('#cl-cp-theme-name');
    var submitBtn = els.overlay.querySelector('#cl-cp-cc-submit');
    var syncSubmit = function () {
      var ok = !!(nameInput && nameInput.value.trim());
      submitBtn.classList.toggle('ready', ok);
      submitBtn.style.cursor = ok ? 'pointer' : 'not-allowed';
      submitBtn.textContent = ok ? (theme ? t().th_save : t().th_create) : t().th_name_required;
    };
    if (nameInput) nameInput.addEventListener('input', syncSubmit);
    syncSubmit();
    submitBtn.addEventListener('click', function () {
      var name = nameInput ? nameInput.value.trim() : '';
      if (!name) return; // honest reason already printed on the button
      var i18n = Object.assign({}, (theme && theme.nameI18n) || {});
      i18n[currentLang()] = name;
      var payload = { name: name, nameI18n: i18n, conditions: readCc() };
      var beforeIds = (place.themeGroups || []).map(function (g) { return g.id; }).join(',');
      var url = theme ? API + '/' + place.id + '/themes/' + theme.id : API + '/' + place.id + '/themes';
      api(url, { method: theme ? 'PATCH' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
        .then(function (res) { return res.json().then(function (body) { return { status: res.status, body: body }; }); })
        .then(function (r) {
          if (r.status !== 200) {
            // honest server copy (cap / validation) verbatim — never a silent refusal
            var msg = r.body && r.body.message && (r.body.message[currentLang()] || r.body.message['zh-TW']);
            toast(msg || (r.body && r.body.error) || ('HTTP ' + r.status));
            return;
          }
          toast(t().th_done1);
          (window.__dbg3 = window.__dbg3 || []).push('submit-ok');
          refresh();
          closeOverlay();
          waitThemeList(place, beforeIds);
        });
    });
  }
  function currentSemantic(axis, cc) {
    var m = CC_SEMANTIC[axis]; if (!m) return 'any';
    // patch-5 ⑤: the 越多越好 floor direction is recognized from cloud_low_min
    if (axis === 'cloud' && cc && cc.cloud_low_min != null && Number(cc.cloud_low_min) >= m.values.more) return 'more';
    var val = cc && cc[m.key];
    var best = 'any';
    var entries = Object.keys(m.values);
    for (var i = 0; i < entries.length; i++) {
      if (m.values[entries[i]] === val) return entries[i];
    }
    // fall back to the strictest option that is at least as strict
    if (val != null) {
      var ranked = entries.filter(function (k) { return k !== 'any'; })
        .sort(function (a, b) { return axis === 'fog' ? m.values[a] - m.values[b] : m.values[a] - m.values[b]; });
      best = ranked[0];
      return best;
    }
    return 'any';
  }
  function genreShortNames() {
    // trilingual genre short names (21 general genres) — hardcoded copy of
    // the subject-cards dictionary so the starter picker needs no fetch
    return {
      'zh-TW': { mountain_view: '山景', overlook: '眺望', sunrise: '日出', sunset: '夕陽', golden: '金光', city_night: '夜景', night_sky: '星空', cloud_sea: '雲海', overcast_soft: '陰柔光', blue_hour: '藍調', sky_glow: '彩霞', fog_mist: '霧景', reflection: '倒影', sunbeam: '光束', milky_way: '銀河', long_exposure: '長曝', city_view: '城市景觀', coast: '海岸', forest: '森林', geology: '地質', lake: '湖景', snow_scene: '雪景', snow_ice: '冰雪', seasonal_plant: '櫻花', firefly: '螢火蟲', drift_ice: '流冰' },
      'en': { mountain_view: 'Mountain view', overlook: 'Overlook', sunrise: 'Sunrise', sunset: 'Sunset', golden: 'Golden hour', city_night: 'City night', night_sky: 'Night sky', cloud_sea: 'Cloud sea', overcast_soft: 'Soft overcast', blue_hour: 'Blue hour', sky_glow: 'Sky glow', fog_mist: 'Fog', reflection: 'Reflection', sunbeam: 'Sunbeam', milky_way: 'Milky Way', long_exposure: 'Long exposure', city_view: 'City view', coast: 'Coast', forest: 'Forest', geology: 'Geology', lake: 'Lake', snow_scene: 'Snow scene', snow_ice: 'Ice & snow', seasonal_plant: 'Cherry blossom', firefly: 'Fireflies', drift_ice: 'Drift ice' },
      'ja': { mountain_view: '山景', overlook: '眺望', sunrise: '日の出', sunset: '夕景', golden: 'ゴールデン', city_night: '夜景', night_sky: '星空', cloud_sea: '雲海', overcast_soft: '柔光', blue_hour: 'ブルーアワー', sky_glow: '彩霞', fog_mist: '霧', reflection: '反射', sunbeam: '光束', milky_way: '天の川', long_exposure: '長曝', city_view: '都市景観', coast: '海岸', forest: '森', geology: '地質', lake: '湖', snow_scene: '雪景色', snow_ice: '氷雪', seasonal_plant: '桜', firefly: '蛍', drift_ice: '流氷' },
    }[currentLang()] || {};
  }
  function ccp(id, label, val) {
    return '<div class="cl-cp-ccp"><label>' + esc(label) + '</label><input id="' + id + '" inputmode="decimal" value="' + esc(val) + '"></div>';
  }
  // patch-5 ④: 適用月份 12-chip multi-select. Default (none checked) = all
  // year; seasonal genre starters prefill their months. Value 1..12.
  function monthsHtml(selected) {
    var sel = Array.isArray(selected) ? selected : [];
    var out = '';
    for (var m = 1; m <= 12; m++) {
      out += '<label class="cl-cp-mo"><input type="checkbox" id="cl-cp-cc-m' + m + '" value="' + m + '"' +
        (sel.indexOf(m) >= 0 ? ' checked' : '') + '>' + m + '月</label>';
    }
    return out;
  }
  function readCc() {
    var num = function (id) { var v = els.overlay.querySelector('#' + id).value.trim(); if (!v) return null; var n = Number(v); return isFinite(n) ? n : null; };
    var out = {};
    ['cl-cp-cc-low:cloud_low_max', 'cl-cp-cc-lowmin:cloud_low_min', 'cl-cp-cc-mid:cloud_mid_max', 'cl-cp-cc-high:cloud_high_max', 'cl-cp-cc-precip:precip_max_mmh', 'cl-cp-cc-vis:visibility_min_km', 'cl-cp-cc-wind:wind_max_ms'].forEach(function (pair) {
      var parts = pair.split(':'); var n = num(parts[0]); if (n != null) out[parts[1]] = n;
    });
    // window segments → cc schema (same rule as the subject-sets editors)
    var segs = cpReadWinState().filter(function (s) { return s.type === 'fixed' ? (s.start && s.end) : true; });
    if (segs.length === 1 && segs[0].type === 'fixed' && /^\d\d:\d\d$/.test(segs[0].start) && /^\d\d:\d\d$/.test(segs[0].end)) {
      out.window_start = segs[0].start; out.window_end = segs[0].end;
    } else if (segs.length) {
      out.windows = segs.map(function (s) {
        if (s.type === 'fixed') return { type: 'fixed', start: s.start, end: s.end };
        // patch-5 ⑤: the short-window span rides through to the worker schema
        var w = { type: s.type, offset_minutes: s.offset_minutes || 0 };
        if (s.span_minutes != null && s.span_minutes > 0) w.span_minutes = s.span_minutes;
        return w;
      });
    }
    var monthsWrap = els.overlay.querySelector('#cl-cp-cc-months');
    if (monthsWrap) {
      var months = [].slice.call(monthsWrap.querySelectorAll('input[type="checkbox"]:checked'))
        .map(function (b) { return Number(b.value); }).filter(function (n) { return n >= 1 && n <= 12; });
      if (months.length) out.months = months.sort(function (a, b) { return a - b; });
    }
    var lead = num('cl-cp-cc-lead'); if (lead != null && Number.isInteger(lead)) out.lead_minutes = lead;
    return out;
  }


  function delModal(place) {
    openOverlay(
      '<div class="cl-cp-m-head"><div><div class="name">' + esc(t().del_title) + '</div></div>' +
      '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      '<div class="cl-cp-delbox"><div class="d1">🗑 ' + esc(place.name) + '</div>' +
      '<div class="d3">' + esc(t().del_warn) + '</div>' +
      '<div class="cl-cp-delacts"><button type="button" class="cancel" id="cl-cp-del-cancel">' + esc(t().del_cancel) + '</button>' +
      '<button type="button" class="confirm" id="cl-cp-del-confirm">' + esc(t().del_confirm) + '</button></div></div>');
    wireClose();
    els.overlay.querySelector('#cl-cp-del-cancel').addEventListener('click', closeOverlay);
    els.overlay.querySelector('#cl-cp-del-confirm').addEventListener('click', function () {
      api(API + '/' + place.id, { method: 'DELETE' })
        .then(function (res) { return res.json().then(function (body) { return { status: res.status, body: body }; }); })
        .then(function (r) {
          closeOverlay();
          if (r.status === 200 && r.body && r.body.note) toast(r.body.note);
          refresh();
        });
    });
  }

  // language switches re-render the widget copy in place (app.js re-renders
  // the grid; the MutationObserver re-appends private cards afterwards)
  function wireLang() {
    var sel = document.getElementById('lang-select');
    if (sel && !sel._clcpWired) {
      sel._clcpWired = true;
      sel.addEventListener('change', function () { setTimeout(render, 50); });
    }
  }

  // ───────────────────────────── boot ─────────────────────────────
  function boot() {
    ensureHosts();
    wireLang();
    restoreSavedView();
    watchContainer();
    render();
    if (state.member) refresh();
  }
  document.addEventListener('chaselights:auth', function (e) {
    var member = (e && e.detail && e.detail.member) ? e.detail.member : null;
    state.member = member;
    refresh();
  });
  window.addEventListener('pageshow', function () { boot(); });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  window.ChaseLightsCustomPlaces = {
    refresh: refresh,
    // patch-6: the {spot, metric, cpOpts} rows app.js's filterAndRender
    // merges into rowsAll — one filter pipeline (tier tabs/chip counts/
    // filters) for official AND private places.
    cardRows: cardRows,
    state: function () {
      // patch-4: the GL map/marker are DOM objects — copy only data fields
      var s = {};
      for (var k in state) {
        if (k === 'miniMap' || k === 'miniMapMarker' || k === 'overlay') continue;
        s[k] = state[k];
      }
      return JSON.parse(JSON.stringify(s));
    },
    setView: function (v) { if (['all', 'official', 'private'].indexOf(v) >= 0) { state.view = v; render(); } },
  };
})();
