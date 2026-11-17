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
      priv_badge: '私人', v_all: '全部', v_official: '官方', v_private: '私人',
      add_btn: '新增私人景點', quota_lbl: '私人點', quota_owner: '無限',
      count_fmt: '共 {n} 個官方景點＋你的 {m} 個私人點',
      count_fmt_zero: '共 {n} 個官方景點（尚未建立私人點）',
      tier_rec: '✓ 條件窗', tier_shoot: '○ 可拍', tier_no: '✗', tier_pending: '⏳ 排隊中',
      trial_expired: '試用期滿', trial_note: '評估已停止（資料保留）', trial_cta: '升級 Premium 恢復使用',
      deferred_note: '已建立·氣象資料明日更新',
      m_edit: '✎ 編輯', m_cc: '🎞 掛題材·條件', m_del: '🗑 刪除',
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
      qv_subject_custom: '自訂條件', qv_baseline: '一般基準', qv_entry: '🎞 題材',
      qv_load_fail: '預報資料暫時無法載入——可能仍在排隊抓取（明日更新）。',
      qv_gen: '符合 {n}/{t} 小時',
      cc_prev: '摘要預覽：', cc_prev_none: '（未調任何參數＝一般基準）', cc_submit: '套用到此點',
      cc_done1: '✓ 條件已套用', cc_none: '（僅一般基準）',
      del_title: '刪除此私人點？', del_warn: '資料保留 30 天：30 日內在同一座標重新新增會直接復活（不重抓）。',
      del_confirm: '🗑 刪除私人點', del_cancel: '取消',
      nl1: '登入後才能使用私人點', nl2: '新增／編輯私人景點是會員功能；私人點只出現在你的帳號。',
      login_cta: '登入以繼續', close: '關閉',
      sem_cloud: '雲量', sem_fog: '霧', sem_rain: '雨',
      ai_hint: '用一句話描述你要的拍攝條件', ai_ph: '例如：清晨要能看到雲海，不要下雨，最好六點前', ai_btn: '解析', ai_working: '解析中…', ai_done: '✓ AI 建議（信賴度 {c}%）——請確認後再送出', ai_conflict: '⚠ 條件矛盾：{m}——請擇一，AI 未套用任何值。', ai_fail: '解析失敗，請手動設定。',
      geo_btn: '📍 使用我的目前位置', geo_note: '為何需要位置：僅用於填入此新景點的座標，不會追蹤你的行蹤。', geo_working: '取得位置中…',
      geo_denied: '無法取得位置：定位權限被拒絕。請改用點圖落釘或直接鍵入經緯度。', geo_timeout: '取得位置逾時。請改用點圖落釘或直接鍵入經緯度。', geo_error: '無法取得位置。請改用點圖落釘或直接鍵入經緯度。',
      copy_genre: '複製官方題材改（起點）', copy_genre_none: '不複製', copy_genre_hint: '選一個官方題材當起點，再微調單一參數',
      adv_toggle: '進階：原始數值輸入',
      lat_lng: 'lat/lng', elev_m: 'm',
    },
    'en': {
      priv_badge: 'Private', v_all: 'All', v_official: 'Official', v_private: 'Private',
      add_btn: 'Add custom place', quota_lbl: 'Custom places', quota_owner: 'Unlimited',
      count_fmt: '{n} official places + your {m} custom places',
      count_fmt_zero: '{n} official places (no custom places yet)',
      tier_rec: '✓ Window', tier_shoot: '○ Shootable', tier_no: '✗', tier_pending: '⏳ Queued',
      trial_expired: 'Trial ended', trial_note: 'Evaluation stopped (data kept)', trial_cta: 'Upgrade to Premium to resume',
      deferred_note: 'Created · weather data updates tomorrow',
      m_edit: '✎ Edit', m_cc: '🎞 Subject & conditions', m_del: '🗑 Delete',
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
      qv_subject_custom: 'Custom conditions', qv_baseline: 'General baseline', qv_entry: '🎞 Subjects',
      qv_load_fail: 'Forecast data is temporarily unavailable — the fetch may still be queued (updates tomorrow).',
      qv_gen: '{n}/{t} hours met',
      cc_prev: 'Summary: ', cc_prev_none: '(nothing tuned = general baseline)', cc_submit: 'Apply to this place',
      cc_done1: '✓ Conditions applied', cc_none: '(general baseline only)',
      del_title: 'Delete this custom place?', del_warn: 'Data is kept 30 days: re-adding the same coordinates within 30 days revives it (no new fetch).',
      del_confirm: '🗑 Delete place', del_cancel: 'Cancel',
      nl1: 'Log in to use custom places', nl2: 'Adding / editing is member-only; places appear only on your account.',
      login_cta: 'Log in to continue', close: 'Close',
      sem_cloud: 'Cloud', sem_fog: 'Fog', sem_rain: 'Rain',
      ai_hint: 'Describe the conditions you want in one sentence', ai_ph: 'e.g. I want a cloud sea at dawn, no rain, ideally before 06:00', ai_btn: 'Parse', ai_working: 'Parsing…', ai_done: '✓ AI suggestion (confidence {c}%) — review, then submit', ai_conflict: '⚠ Conflicting conditions: {m} — pick one; the AI applied nothing.', ai_fail: 'Parsing failed — please set the conditions manually.',
      geo_btn: '📍 Use my current location', geo_note: 'Why we need it: only to fill in this place’s coordinates — your movements are never tracked.', geo_working: 'Getting your location…',
      geo_denied: 'Could not get your location: permission denied. Please pin on the map or type lat/lng manually.', geo_timeout: 'Getting your location timed out. Please pin on the map or type lat/lng manually.', geo_error: 'Could not get your location. Please pin on the map or type lat/lng manually.',
      copy_genre: 'Copy an official genre template (starter)', copy_genre_none: 'No copy', copy_genre_hint: 'Pick an official genre as the starting point, then tweak a single parameter',
      adv_toggle: 'Advanced: raw numeric inputs',
      lat_lng: 'lat/lng', elev_m: 'm',
    },
    'ja': {
      priv_badge: '自作', v_all: 'すべて', v_official: '公式', v_private: '自作',
      add_btn: '自作スポットを追加', quota_lbl: '自作スポット', quota_owner: '無制限',
      count_fmt: '公式 {n} スポット＋あなたの自作 {m} スポット',
      count_fmt_zero: '公式 {n} スポット（自作スポットはまだありません）',
      tier_rec: '✓ 条件窓', tier_shoot: '○ 撮影可', tier_no: '✗', tier_pending: '⏳ 待機中',
      trial_expired: 'トライアル期限切れ', trial_note: '評価停止中（データは保持）', trial_cta: 'Premiumへアップグレードで再開',
      deferred_note: '作成済み・気象データは明日更新',
      m_edit: '✎ 編集', m_cc: '🎞 題材・条件', m_del: '🗑 削除',
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
      qv_subject_custom: 'カスタム条件', qv_baseline: '一般基準', qv_entry: '🎞 題材',
      qv_load_fail: '予報データを取得できません——取得待ちの可能性があります（明日更新）。',
      qv_gen: '{n}/{t} 時間適合',
      cc_prev: 'サマリー：', cc_prev_none: '（未調整＝一般基準）', cc_submit: 'このスポットに適用',
      cc_done1: '✓ 条件を適用しました', cc_none: '（一般基準のみ）',
      del_title: 'この自作スポットを削除？', del_warn: 'データは 30 日保持：30 日以内に同じ座標を再追加すると復活します（再取得なし）。',
      del_confirm: '🗑 削除する', del_cancel: 'キャンセル',
      nl1: '自作スポットにはログインが必要', nl2: '追加／編集は会員機能；自作スポットは自分のアカウントにのみ表示されます。',
      login_cta: 'ログインして続行', close: '閉じる',
      sem_cloud: '雲量', sem_fog: '霧', sem_rain: '雨',
      ai_hint: '撮りたい条件を一文で説明', ai_ph: '例：明け方に雲海が見たい。雨は嫌。できれば6時まで', ai_btn: '解析', ai_working: '解析中…', ai_done: '✓ AI提案（信頼度 {c}%）— 確認してから送信してください', ai_conflict: '⚠ 条件が矛盾しています：{m} — どちらかを選択してください（AIは未適用）。', ai_fail: '解析に失敗しました。手動で設定してください。',
      geo_btn: '📍 現在地を使う', geo_note: '位置情報の使い道：このスポットの座標を入力するためだけ。現在地は追跡しません。', geo_working: '現在地を取得中…',
      geo_denied: '位置を取得できませんでした：権限が拒否されました。地図クリックまたは手動入力をご利用ください。', geo_timeout: '位置の取得がタイムアウトしました。地図クリックまたは手動入力をご利用ください。', geo_error: '位置を取得できませんでした。地図クリックまたは手動入力をご利用ください。',
      copy_genre: '公式題材をコピーして改造（出発点）', copy_genre_none: 'コピーしない', copy_genre_hint: '公式題材を出発点に選び、1つのパラメータだけ調整します',
      adv_toggle: '高度：生の数値入力',
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
  function openOverlay(html) { ensureHosts(); var m = els.overlay.querySelector('.cl-cp-modal'); m.innerHTML = html; els.overlay.classList.add('open'); els.overlay.scrollTop = 0; m.scrollTop = 0; document.body.classList.add('cl-cp-lock'); }
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
    var c = document.getElementById('spots-container');
    return c ? c.querySelectorAll('.card:not(.cl-cp-card)').length : 0;
  }
  function privatePlaces() { return (state.data && state.data.places) || []; }

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
    var keep = {};
    places.forEach(function (p) { keep[p.id] = true; });
    // remove stale cards
    container.querySelectorAll('.cl-cp-card').forEach(function (card) {
      if (!keep[card.getAttribute('data-cp-id')]) card.remove();
    });
    var existing = {};
    container.querySelectorAll('.cl-cp-card').forEach(function (card) { existing[card.getAttribute('data-cp-id')] = true; });
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
    appendPrivateCards(places);
  }
  function syncPrivateCards(places) {
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

  function tierBadge(p) {
    var ev = p.evaluation || {};
    var map = { rec: ['cl-cp-tier-rec', t().tier_rec], shoot: ['cl-cp-tier-shoot', t().tier_shoot], no: ['cl-cp-tier-no', t().tier_no], pending: ['cl-cp-tier-pending', t().tier_pending] };
    var m = map[ev.tier] || map.pending;
    return '<span class="cl-cp-tier ' + m[0] + '">' + esc(m[1]) + '</span>';
  }
  function ccSummary(cc, lang) {
    if (!cc) return '';
    var parts = [];
    var L = T[lang] || T['zh-TW'];
    if (cc.cloud_low_max != null && cc.cloud_low_max < 100) parts.push((lang === 'en' ? 'low≤' : lang === 'ja' ? '低雲≤' : '低雲≤') + cc.cloud_low_max + '%');
    if (cc.cloud_mid_max != null && cc.cloud_mid_max < 100) parts.push('中雲≤' + cc.cloud_mid_max + '%');
    if (cc.cloud_high_max != null && cc.cloud_high_max < 100) parts.push('高雲≤' + cc.cloud_high_max + '%');
    if (cc.precip_max_mmh != null) parts.push((lang === 'en' ? 'precip≤' : '降水≤') + cc.precip_max_mmh);
    if (cc.visibility_min_km != null) parts.push((lang === 'en' ? 'vis≥' : '能見度≥') + cc.visibility_min_km);
    if (cc.wind_max_ms != null) parts.push('風≤' + cc.wind_max_ms);
    if (cc.window_start && cc.window_end) parts.push(cc.window_start + '–' + cc.window_end);
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
  function buildPrivateCard(p) {
    var card = document.createElement('div');
    card.className = 'card cl-cp-card';
    card.setAttribute('data-cp-id', p.id);
    card.tabIndex = 0;
    updatePrivateCard(p, card);
    return card;
  }
  function updatePrivateCard(p, card) {
    card = card || document.querySelector('#spots-container .cl-cp-card[data-cp-id="' + CSS.escape(p.id) + '"]');
    if (!card) return;
    var sig = JSON.stringify(p);
    if (card._cpSig === sig) return; // identical data → no innerHTML rewrite (the
    card._cpSig = sig;               // container MutationObserver watches these cards)
    var ev = p.evaluation || {};
    var expired = p.status === 'trial_expired';
    card.classList.toggle('cl-cp-expired', expired);
    var lang = currentLang();
    var head =
      '<div class="spot-title-group">' +
        '<div class="card-head-line" style="display:flex;align-items:center;gap:8px;min-width:0">' +
          '<span class="cl-cp-card-name" style="font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">' + esc(p.name) + '</span>' +
          tierBadge(p) +
          '<span class="cl-cp-priv-badge">◉ ' + esc(expired ? t().trial_expired : t().priv_badge) + '</span>' +
        '</div>' +
        '<div class="cl-cp-coord">' + esc(p.lat) + ', ' + esc(p.lng) + (p.elevation != null ? ' · ' + esc(p.elevation) + ' m' : '') + (p.timezone ? ' · ' + esc(p.timezone) : '') + '</div>' +
      '</div>' +
      // patch-3: the menu markup moved OUT of the card — one shared menu is
      // portaled to document.body (ensureMenu) and position:fixed under the
      // ⋯ trigger, so the card's content-visibility/paint containment and the
      // container overflow can never clip the dropdown again.
      '<button type="button" class="cl-cp-more" aria-label="⋯" aria-haspopup="menu" aria-expanded="false">⋯</button>';
    var body = '';
    if (expired) {
      body = '<div class="cl-cp-expired-note">🔒 ' + esc(t().trial_note) + '</div>' +
        '<button type="button" class="cl-cp-expired-cta" data-cp-act="upgrade">⬆ ' + esc(t().trial_cta) + '</button>';
    } else if (ev.tier === 'pending' && p.fetchDeferred) {
      body = '<div class="cl-cp-deferred-note">⏳ ' + esc(t().deferred_note) + '</div>';
    } else if (ev.tier === 'rec' || ev.tier === 'shoot') {
      body = '<div class="cl-subject-row" style="display:flex;align-items:center;gap:8px;height:26px;font-size:13px">' +
        '<span class="cl-cp-window" style="flex:1">' + esc(ev.window || '') + '</span></div>';
    } else if (ev.tier === 'no') {
      body = '<div style="font-size:13px;color:var(--cl-red-text)">' + esc(t().tier_no) + ' <span style="font-weight:600">' + esc(ev.reason || '') + '</span></div>';
    } else {
      body = '<div class="cl-cp-deferred-note">⏳ ' + esc(t().tier_pending) + '</div>';
    }
    var ccLine = ccSummary(p.customConditions, lang)
      ? '<div class="cl-cp-cc-line"><span class="cl-cp-cc-chip">🎚</span><span class="cl-cp-cc-txt">' + esc(ccSummary(p.customConditions, lang)) + '</span></div>' : '';
    card.innerHTML = '<div style="display:flex;align-items:flex-start;gap:8px;min-width:0">' + head + '</div>' + body + ccLine;
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
      if (e.target.closest('[data-cp-act="upgrade"]')) { e.stopPropagation(); toast(t().trial_cta); }
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
  var CP_GENERAL_BASELINE = { precip_max_mmh: 2, visibility_min_km: 3, wind_max_ms: 10 };
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
      ['precip_max_mmh', 'precipitation'], ['visibility_min_km', 'visibility'], ['wind_max_ms', 'wind'],
    ];
    for (var i = 0; i < rows.length; i++) {
      var limit = Number(cc[rows[i][0]]);
      if (!isFinite(limit)) continue;
      if (rows[i][1].indexOf('cloud') === 0 && limit >= 100) continue; // lenient default
      if (rows[i][1] === 'visibility' && limit <= 0) continue;        // lenient default
      var val = v[rows[i][1]];
      val = (typeof val === 'number' && isFinite(val)) ? val : null;
      if (val == null) return false; // constraint set but data missing → no match
      if (rows[i][0] === 'visibility_min_km' ? val < limit : val > limit) return false;
    }
    return true;
  }
  function forecastModal(p) {
    var ev = p.evaluation || {};
    var html =
      '<div class="cl-cp-m-head"><div><div class="name">📍 ' + esc(p.name) + '</div>' +
      '<div class="sub">' + esc(p.lat) + ', ' + esc(p.lng) +
      (p.elevation != null ? ' · ' + esc(p.elevation) + ' m' : '') +
      (p.timezone ? ' · ' + esc(p.timezone) : '') + '</div></div>' +
      '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      '<div class="cl-cp-qv-quick"><span class="k">' + esc(t().qv_quick) + '</span>' + tierBadge(p) +
      (ev.window ? ' <span class="cl-cp-window">' + esc(ev.window) + '</span>' : '') +
      (ev.reason ? ' <span class="cl-cp-qv-reason">' + esc(ev.reason) + '</span>' : '') + '</div>' +
      '<div class="cl-cp-qv-sec">' + esc(t().qv_days) + '</div>' +
      '<div class="cl-cp-qv-strip" id="cl-cp-qv-days"><div class="cl-cp-qv-loading">…</div></div>' +
      '<div class="cl-cp-qv-sec">' + esc(t().qv_subjects) + '</div>' +
      '<div id="cl-cp-qv-subjects"><div class="cl-cp-qv-loading">…</div></div>' +
      '<div class="cl-cp-qv-actions"><button type="button" class="cl-cp-btn" id="cl-cp-qv-subject-entry">' +
      esc(t().qv_entry) + '</button></div>';
    openOverlay(html);
    wireClose(); // patch-7: the ✕ closes the popup like every other modal
    var entry = els.overlay.querySelector('#cl-cp-qv-subject-entry');
    if (entry) entry.addEventListener('click', function () { ccModal(p); });
    api(API + '/' + p.id + '/eval')
      .then(function (res) { return res.json().then(function (body) { return { status: res.status, body: body }; }); })
      .then(function (r) {
      if (!els.overlay.classList.contains('open')) return; // closed meanwhile
      var daysEl = els.overlay.querySelector('#cl-cp-qv-days'), subjEl = els.overlay.querySelector('#cl-cp-qv-subjects');
      if (!daysEl) return;
      if (r.status === 200 && r.body && r.body.ok && Array.isArray(r.body.hourly) && r.body.hourly.length) {
        renderForecast(p, r.body.hourly, daysEl, subjEl);
      } else {
        daysEl.innerHTML = '<div class="cl-cp-qv-none">' + esc(t().qv_load_fail) + '</div>';
        if (subjEl) subjEl.innerHTML = '<div class="cl-cp-qv-none">' + esc(t().qv_load_fail) + '</div>';
      }
    });
  }
  function qvDayGrid(hourly) {
    // 8 calendar days starting at the feed's first local_date (honest today);
    // days with no rows render as ─ with the title explaining why.
    var days = [], seen = {}, first = null;
    hourly.forEach(function (row) {
      if (!row || typeof row.local_date !== 'string') return;
      if (!first) first = row.local_date;
      seen[row.local_date] = true;
    });
    if (!first) return [];
    var base = first.split('-').map(Number);
    var d = new Date(Date.UTC(base[0], base[1] - 1, base[2]));
    for (var i = 0; i < 8; i++) {
      var iso = d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0');
      days.push({ date: iso, rows: seen[iso] ? hourly.filter(function (r) { return r.local_date === iso; }) : null });
      d.setUTCDate(d.getUTCDate() + 1);
    }
    return days;
  }
  function qvDayCell(day, cc) {
    var label = day.date.slice(5).replace('-', '/'); // M/D — place-local dates only
    if (!day.rows || !day.rows.length) return '<div class="cl-cp-qv-cell none" title="' + esc(t().qv_no_data_note) + '"><span class="d">' + esc(label) + '</span><span class="v">' + esc(t().qv_no_data) + '</span></div>';
    var met = 0, total = 0;
    day.rows.forEach(function (row) {
      if (!row || typeof row.hour !== 'string') return;
      if (!cpHourInWindow(row.hour, cc && cc.window_start, cc && cc.window_end)) return;
      total += 1;
      if (cpHourMatches(row.values, cc)) met += 1;
    });
    var v = total === 0 ? t().qv_no_data : (met > 0 ? '✓' : '✗');
    var cls = total === 0 ? 'none' : (met > 0 ? 'ok' : 'bad');
    var title = total === 0 ? t().qv_no_data_note : t().qv_gen.replace('{n}', met).replace('{t}', total);
    return '<div class="cl-cp-qv-cell ' + cls + '" title="' + esc(title) + '"><span class="d">' + esc(label) + '</span><span class="v">' + esc(v) + '</span></div>';
  }
  function renderForecast(p, hourly, daysEl, subjEl) {
    var cc = p.customConditions || null;
    var days = qvDayGrid(hourly);
    daysEl.innerHTML = days.map(function (day) { return qvDayCell(day, cc); }).join('');
    var subjects = [];
    if (cc) subjects.push({ name: t().qv_subject_custom, cond: cc });
    subjects.push({ name: t().qv_baseline, cond: CP_GENERAL_BASELINE });
    subjEl.innerHTML = subjects.map(function (s) {
      return '<div class="cl-cp-qv-row"><span class="cl-cp-qv-row-name">' + esc(s.name) + '</span>' +
        '<div class="cl-cp-qv-strip cl-cp-qv-row-strip">' + days.map(function (day) { return qvDayCell(day, s.cond); }).join('') + '</div></div>';
    }).join('');
  }
  // ───── patch-3: the ⋯ menu — one fixed-position menu portaled to body ─────
  var MENU_LABELS = { edit: 'm_edit', cc: 'm_cc', del: 'm_del' };
  function ensureMenu() {
    if (els.menu) return els.menu;
    var m = document.createElement('div');
    m.id = 'cl-cp-menu';
    m.className = 'cl-cp-menu';
    m.setAttribute('role', 'menu');
    m.innerHTML =
      '<button type="button" role="menuitem" data-cp-act="edit"><span class="cm-ic">✎</span><span class="cm-txt"></span></button>' +
      '<button type="button" role="menuitem" data-cp-act="cc"><span class="cm-ic">🎞</span><span class="cm-txt"></span></button>' +
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
      else if (act === 'del') delModal(place);
    });
    document.body.appendChild(m);
    els.menu = m;
    return m;
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
  function positionMenu(m, more) {
    m.style.visibility = 'hidden';
    m.classList.add('open');
    var r = more.getBoundingClientRect();
    var mw = m.offsetWidth, mh = m.offsetHeight;
    var gap = 6, margin = 8;
    var top = r.bottom + gap;
    if (top + mh > window.innerHeight - margin && r.top - gap - mh >= margin) top = r.top - gap - mh; // 靠近螢幕下緣 → 向上展開
    top = Math.max(margin, Math.min(top, Math.max(margin, window.innerHeight - margin - mh)));
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
  function watchContainer() {
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
        'zh-TW': [['min', '越少越好', '低雲 ≤20%'], ['half', '半晴半雲', '低雲 ≤50%'], ['any', '多雲也行', '不限']],
        'en': [['min', 'As little as possible', 'low cloud ≤20%'], ['half', 'Half sun, half cloud', 'low cloud ≤50%'], ['any', 'Cloudy is fine', 'no limit']],
        'ja': [['min', 'できるだけ少ない', '低雲 ≤20%'], ['half', '半分晴れ半分雲', '低雲 ≤50%'], ['any', '曇りでも可', '制限なし']],
      },
      values: { min: 20, half: 50, any: 100 },
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
    cloud_sea: { cloud: 'min', fog: 'any', rain: 'no', window: ['04:30', '07:00'] },
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
            if (s.window_start) { els.overlay.querySelector('#cl-cp-cc-start').value = s.window_start; els.overlay.querySelector('#cl-cp-cc-end').value = s.window_end || ''; }
            if (s.lead_minutes != null) { var l = els.overlay.querySelector('#cl-cp-cc-lead'); if (l) l.value = String(s.lead_minutes); }
            els.overlay.querySelector('#cl-cp-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
            var conf = Math.round((s.confidence || 0) * 100);
            note.textContent = t().ai_done.replace('{c}', conf);
          } else {
            var msg = r.body && r.body.message && (r.body.message[currentLang()] || r.body.message['zh-TW']);
            note.textContent = msg || t().ai_fail;
          }
        })
        .catch(function () { note.textContent = t().ai_fail; });
    });
  }

  // conditions modal — CL-UI-99 five parameter groups (same schema as
  // notify_rules.custom_conditions; the worker re-validates)
  function ccModal(place) {
    var cc = place.customConditions || {};
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
      '<div class="cl-cp-m-head"><div><div class="name">🎞 ' + esc(t().cc_title) + '</div>' +
      '<div class="sub">' + esc(t().cc_sub) + ' · ' + esc(place.name) + '</div></div>' +
      '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      (aiEnabled ? aiParseBlock() : '') +
      '<div class="cl-cp-cc-params">' +
      semSel('cloud', t().sem_cloud) +
      semSel('fog', t().sem_fog) +
      semSel('rain', t().sem_rain) +
      '<div class="cl-cp-ccp wide"><label>' + esc(t().p_window) + '</label><div style="display:flex;gap:6px;align-items:center">' +
      '<input id="cl-cp-cc-start" value="' + esc(v('window_start')) + '" placeholder="04:30" style="flex:1"><span style="color:var(--cl-text-3)">–</span>' +
      '<input id="cl-cp-cc-end" value="' + esc(v('window_end')) + '" placeholder="07:00" style="flex:1"></div>' +
      '<div class="hint">HH:MM</div></div>' +
      '<div class="cl-cp-ccp wide" id="cl-cp-cc-months-wrap"><label>' + esc(t().p_months) + '</label>' +
      '<div class="cl-cp-cc-months" id="cl-cp-cc-months">' + monthsHtml(cc.months) + '</div>' +
      '<div class="hint">' + esc(t().p_months_hint) + '</div></div>' +
      '</div>' +
      '<div class="cl-cp-fld" style="margin-bottom:8px"><label>' + esc(t().copy_genre) + '</label>' +
      '<select id="cl-cp-cc-genre" class="inp"><option value="">— ' + esc(t().copy_genre_none) + ' —</option>' + genreOpts + '</select>' +
      '<div class="hint">' + esc(t().copy_genre_hint) + '</div></div>' +
      '<details class="cl-cp-cc-advanced" id="cl-cp-cc-adv"><summary>' + esc(t().adv_toggle) + '</summary>' +
      '<div class="cl-cp-cc-params" style="margin-top:8px">' +
      ccp('cl-cp-cc-low', t().p_low, v('cloud_low_max')) +
      ccp('cl-cp-cc-mid', t().p_mid, v('cloud_mid_max')) +
      ccp('cl-cp-cc-high', t().p_high, v('cloud_high_max')) +
      ccp('cl-cp-cc-precip', t().p_precip, v('precip_max_mmh')) +
      ccp('cl-cp-cc-vis', t().p_vis, v('visibility_min_km')) +
      ccp('cl-cp-cc-wind', t().p_wind, v('wind_max_ms')) +
      ccp('cl-cp-cc-lead', t().p_lead, v('lead_minutes')) +
      '</div></details>' +
      '<div class="cl-cp-cc-preview"><span style="color:var(--cl-text-3)">' + esc(t().cc_prev) + '</span><span class="k" id="cl-cp-cc-prev">' + esc(ccSummary(cc, lang) || t().cc_prev_none) + '</span></div>' +
      '<button type="button" class="cl-cp-submit ready" id="cl-cp-cc-submit" style="cursor:pointer">' + esc(t().cc_submit) + '</button>');
    wireClose();
    if (aiEnabled) wireAiParse();
    var sync = function () {
      // semantic → concrete: write the mapped value into the advanced input
      // (the advanced inputs stay the single source of truth) and refresh
      // the transparent mapping labels + preview.
      ['cloud', 'fog', 'rain'].forEach(function (axis) {
        var sel = els.overlay.querySelector('#cl-cp-sem-' + axis);
        if (!sel) return;
        var val = sel.value;
        els.overlay.querySelector('#cl-cp-sem-map-' + axis).textContent = '→ ' + semanticMappedLabel(axis, val);
        var target = { cloud: '#cl-cp-cc-low', fog: '#cl-cp-cc-vis', rain: '#cl-cp-cc-precip' }[axis];
        var inp = els.overlay.querySelector(target);
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
      els.overlay.querySelector('#cl-cp-cc-start').value = starter.window[0];
      els.overlay.querySelector('#cl-cp-cc-end').value = starter.window[1];
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
    els.overlay.querySelector('#cl-cp-cc-submit').addEventListener('click', function () {
      var payload = { customConditions: readCc() };
      api(API + '/' + place.id, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
        .then(function (res) { return res.json().then(function (body) { return { status: res.status, body: body }; }); })
        .then(function (r) {
          if (r.status !== 200) { toast((r.body && r.body.error) || ('HTTP ' + r.status)); return; }
          openOverlay('<div class="cl-cp-m-head"><div><div class="name">' + esc(place.name) + '</div></div>' +
            '<button type="button" class="close" data-cp-close aria-label="' + esc(t().close) + '">✕</button></div>' +
            '<div class="cl-cp-done"><div class="d1">' + esc(t().cc_done1) + '</div>' +
            '<div class="d2">' + esc(ccSummary(readCc(), currentLang()) || t().cc_none) + '</div>' +
            '<button type="button" id="cl-cp-done-btn">' + esc(t().close) + '</button></div>');
          wireClose();
          var dn = els.overlay.querySelector('#cl-cp-done-btn'); if (dn) dn.addEventListener('click', closeOverlay);
          refresh();
        });
    });
  }
  function currentSemantic(axis, cc) {
    var m = CC_SEMANTIC[axis]; if (!m) return 'any';
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
    ['cl-cp-cc-low:cloud_low_max', 'cl-cp-cc-mid:cloud_mid_max', 'cl-cp-cc-high:cloud_high_max', 'cl-cp-cc-precip:precip_max_mmh', 'cl-cp-cc-vis:visibility_min_km', 'cl-cp-cc-wind:wind_max_ms'].forEach(function (pair) {
      var parts = pair.split(':'); var n = num(parts[0]); if (n != null) out[parts[1]] = n;
    });
    var ws = els.overlay.querySelector('#cl-cp-cc-start').value.trim(), we = els.overlay.querySelector('#cl-cp-cc-end').value.trim();
    if (ws && we && /^\d\d:\d\d$/.test(ws) && /^\d\d:\d\d$/.test(we)) { out.window_start = ws; out.window_end = we; }
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
