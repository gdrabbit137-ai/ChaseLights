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
  var ME_ENDPOINT = '/api/v1/auth/me';
  var CATALOG_URL = './apps/web-v2/evaluations-latest.json';
  var REGIONS = [
    { id: 'tw', flag: '🇹🇼' },
    { id: 'jp', flag: '🇯🇵' },
    { id: 'us', flag: '🇺🇸' },
    { id: 'ak', flag: '🇺🇸' },
    { id: 'hi', flag: '🇺🇸' }
  ];

  var I18N = {
    'zh-TW': {
      page_title: '提醒清單', nav_cards: '卡片', nav_weathermap: '天氣圖', nav_reminders: '提醒',
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
      rem_flow_hint: '選地區 → 景點 → 題材，或直接搜尋景點名；符合時段前會透過 APP 推播通知。'
    },
    'en': {
      page_title: 'Reminders', nav_cards: 'Cards', nav_weathermap: 'Weather map', nav_reminders: 'Reminders',
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
      rem_flow_hint: 'Pick region → place → subject, or search directly; we notify via app push when conditions qualify.'
    },
    'ja': {
      page_title: 'リマインダー', nav_cards: 'カード', nav_weathermap: '天気マップ', nav_reminders: 'リマインダー',
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
      rem_flow_hint: '地域 → スポット → 題材を選ぶか、直接検索。条件が揃うとアプリのプッシュ通知でお知らせします。'
    }
  };

  var state = { lang: 'zh-TW', catalog: [], rules: [], signedIn: null };

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
    for (var i = 0; i < REGIONS.length; i++) if (REGIONS[i].id === regionId) return REGIONS[i].flag + ' ' + regionId.toUpperCase();
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
  // Card status line: paused → grey 暫停中; amber streak (>=3 unfit days, no
  // next window) → 該複核提醒 cue; else mono green next trigger; honest
  // 「近期無符合時段」 fallback instead of a fabricated time.
  function nextStatusHtml(rule) {
    var on = !!rule.enabled;
    var place = findPlace(state.catalog, rule.place_id);
    if (!on) return '<span class="rem-next rem-next-off">' + esc(t('rem_paused_next')) + '</span>';
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
      return r.json().then(function (b) { state.rules = (b && b.rules) || []; });
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
  function createRule(placeId, oppId) {
    return fetch(RULES_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ placeId: placeId, opportunityId: oppId || undefined, channel: 'push', minAdvanceHours: 24 })
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
    if (rule.opportunity_id) {
      var subj = findSubject(place, rule.opportunity_id);
      subjName = subj ? nameOf(subj.name_i18n, state.lang) : rule.opportunity_id;
    }
    return { placeName: placeName, subjName: subjName };
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
      return '<div class="rem-card' + (on ? '' : ' rem-off') + '" data-rule-id="' + esc(rule.id) + '">' +
        '<div class="rem-main">' +
        '<div class="rem-line1"><span class="rem-place">' + esc(names.placeName) + '</span>' +
        '<span class="rem-subject-chip">' + esc(names.subjName) + '</span></div>' +
        '<div class="rem-line2"><span class="rem-region">' + esc(region) + ' · ' + esc(t('rem_col_channel')) + ' · ' +
        esc(t('rem_col_advance').replace('{n}', String(rule.min_advance_hours != null ? rule.min_advance_hours : 24))) + '</span>' +
        nextStatusHtml(rule) +
        '</div></div>' +
        '<div class="rem-acts">' +
        '<button type="button" class="rem-switch' + (on ? ' rem-on' : '') + '" data-rem-toggle role="switch"' +
        ' aria-checked="' + (on ? 'true' : 'false') + '" aria-label="' + esc(on ? t('rem_enabled') : t('rem_disabled')) + '"></button>' +
        '<button type="button" class="rem-edit-btn" data-rem-edit>' + esc(t('rem_edit')) + '</button>' +
        '<button type="button" class="rem-del" data-rem-delete>' + esc(t('rem_delete')) + '</button>' +
        '</div></div>';
    }).join('');
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
    var options = [{ value: '', label: t('rem_any_subject') }].concat(
      opps.map(function (o) { return { value: o.opportunity_id, label: nameOf(o.name_i18n, state.lang) || o.opportunity_id }; }));
    fillSelect(subjSel, options, options.some(function (o) { return o.value === prev; }) ? prev : '');
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
    document.getElementById('rem-region').addEventListener('change', function () { renderPlaceOptions(); renderPreview(); });
    document.getElementById('rem-place').addEventListener('change', function () { renderSubjectOptions(); renderPreview(); });
    document.getElementById('rem-subject').addEventListener('change', renderPreview);
    document.getElementById('rem-search').addEventListener('input', renderSearchResults);
    document.getElementById('rem-empty-add').addEventListener('click', function () {
      var region = document.getElementById('rem-region');
      if (region) region.focus();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    document.getElementById('rem-add-submit').addEventListener('click', function () {
      var placeId = document.getElementById('rem-place').value;
      var oppId = document.getElementById('rem-subject').value;
      addRule(placeId, oppId);
    });
    document.getElementById('rem-list').addEventListener('click', function (e) {
      var row = e.target.closest ? e.target.closest('.rem-card') : null;
      if (!row) return;
      var ruleId = row.getAttribute('data-rule-id');
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
        if (rule.opportunity_id) document.getElementById('rem-subject').value = rule.opportunity_id;
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

  function addRule(placeId, oppId) {
    createRule(placeId, oppId).then(function (res) {
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
      renderAll();
      if (!signed) return null;
      return reload();
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
    nextStatusHtml: nextStatusHtml
  };
})();
