/* CL-UI-58: reminders page (reminders.html) — list / toggle / delete / quick-add
   for notify_rules. Follows the genre-eval.js page pattern: self-contained
   trilingual dict, own lang select, loads the shared reminders-client.js for
   the API contract and toasts.

   Catalog source (既有 browse/目錄資料): apps/web-v2/evaluations-latest.json —
   places[{place_id, name_i18n, opportunities[{opportunity_id, name_i18n}]}].
   The region is derived from the place_id prefix (tw/jp/us/ak/hi), the same
   regions the homepage VALID_REGIONS uses. No data-layer files are touched.

   Backend contract (CL-API-03 + CL-UI-58 PATCH):
   - GET    /api/v1/notify_rules      -> { rules:[{id, place_id, opportunity_id, channel, min_advance_hours, enabled}] } (JWT only; 401 = not signed in)
   - POST   /api/v1/notify_rules      { placeId, opportunityId, channel:'telegram', minAdvanceHours:24 }
   - PATCH  /api/v1/notify_rules/<id> { enabled: boolean }
   - DELETE /api/v1/notify_rules/<id>
*/
(function () {
  'use strict';

  var RULES_ENDPOINT = '/api/v1/notify_rules';
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
      page_title: '我的拍攝提醒', nav_cards: '卡片', nav_weathermap: '天氣圖', nav_reminders: '提醒',
      rem_list_title: '我的提醒',
      rem_add_title: '快速增加提醒',
      rem_add_btn: '🔔 加入提醒',
      rem_added_btn: '已加入 ✓',
      rem_search_placeholder: '搜尋景點名稱或題材名稱…',
      rem_region_label: '地區', rem_place_label: '景點', rem_subject_label: '題材',
      rem_col_channel: 'Telegram', rem_col_advance: '提前 {n} 小時',
      rem_enabled: '啟用', rem_disabled: '停用',
      rem_delete: '刪除',
      rem_login_prompt: '登入後即可管理你的拍攝提醒（條件符合時透過 Telegram 通知）。',
      rem_login_line: '使用 LINE 登入', rem_login_google: '使用 Google 登入',
      rem_empty: '目前沒有提醒。用下方「快速增加提醒」新增第一筆。',
      rem_loading: '正在載入提醒…',
      rem_saved: '已加入提醒，條件符合時將透過 Telegram 通知。',
      rem_removed: '已移除提醒。',
      rem_err: '提醒暫時無法同步，請稍後再試。',
      rem_limit: '提醒數量已達方案上限，請先移除部分提醒。',
      rem_any_subject: '該景點全部題材',
      rem_no_match: '沒有符合的景點或題材。'
    },
    'en': {
      page_title: 'My shooting reminders', nav_cards: 'Cards', nav_weathermap: 'Weather map', nav_reminders: 'Reminders',
      rem_list_title: 'My reminders',
      rem_add_title: 'Quick add reminder',
      rem_add_btn: '🔔 Add reminder',
      rem_added_btn: 'Added ✓',
      rem_search_placeholder: 'Search place or subject names…',
      rem_region_label: 'Region', rem_place_label: 'Place', rem_subject_label: 'Subject',
      rem_col_channel: 'Telegram', rem_col_advance: '{n} h in advance',
      rem_enabled: 'Enabled', rem_disabled: 'Paused',
      rem_delete: 'Delete',
      rem_login_prompt: 'Sign in to manage your shooting reminders (notified via Telegram when conditions qualify).',
      rem_login_line: 'Sign in with LINE', rem_login_google: 'Sign in with Google',
      rem_empty: 'No reminders yet. Use “Quick add reminder” below to create your first one.',
      rem_loading: 'Loading reminders…',
      rem_saved: 'Reminder added — you will be notified via Telegram when conditions qualify.',
      rem_removed: 'Reminder removed.',
      rem_err: 'Reminders could not be synced right now; please try again later.',
      rem_limit: 'Reminder limit reached for your plan — remove some reminders first.',
      rem_any_subject: 'All subjects at this place',
      rem_no_match: 'No matching places or subjects.'
    },
    'ja': {
      page_title: '撮影リマインダー', nav_cards: 'カード', nav_weathermap: '天気マップ', nav_reminders: 'リマインダー',
      rem_list_title: 'リマインダー一覧',
      rem_add_title: 'リマインダーをクイック追加',
      rem_add_btn: '🔔 リマインダー追加',
      rem_added_btn: '追加済み ✓',
      rem_search_placeholder: 'スポット名や題材名を検索…',
      rem_region_label: '地域', rem_place_label: 'スポット', rem_subject_label: '題材',
      rem_col_channel: 'Telegram', rem_col_advance: '{n} 時間前に通知',
      rem_enabled: '有効', rem_disabled: '停止',
      rem_delete: '削除',
      rem_login_prompt: 'ログインすると撮影リマインダーを管理できます（条件が揃うと Telegram で通知）。',
      rem_login_line: 'LINE でログイン', rem_login_google: 'Google でログイン',
      rem_empty: 'リマインダーはまだありません。下の「クイック追加」で最初の1件を作成してください。',
      rem_loading: 'リマインダーを読み込み中…',
      rem_saved: 'リマインダーを追加しました。条件が揃うと Telegram で通知します。',
      rem_removed: 'リマインダーを削除しました。',
      rem_err: 'リマインダーを同期できませんでした。しばらくしてから再試行してください。',
      rem_limit: 'リマインダー数がプランの上限に達しました。先に一部を削除してください。',
      rem_any_subject: 'このスポットの全題材',
      rem_no_match: '該当するスポットや題材がありません。'
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
      body: JSON.stringify({ placeId: placeId, opportunityId: oppId || undefined, channel: 'telegram', minAdvanceHours: 24 })
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
    if (!state.signedIn) { panel.hidden = true; return; }
    panel.hidden = false;
    document.getElementById('rem-list-title').textContent = t('rem_list_title') + '（' + state.rules.length + '）';
    if (!state.rules.length) { list.innerHTML = '<p class="rem-state">' + esc(t('rem_empty')) + '</p>'; return; }
    list.innerHTML = state.rules.map(function (rule) {
      var names = ruleLabel(rule);
      var on = !!rule.enabled;
      return '<div class="rem-row" data-rule-id="' + esc(rule.id) + '">' +
        '<div class="rem-names"><b>' + esc(names.placeName) + '</b>' +
        '<span class="rem-sub">' + esc(names.subjName) + '</span></div>' +
        '<span class="rem-meta">' + esc(t('rem_col_channel')) + ' · ' + esc(t('rem_col_advance').replace('{n}', String(rule.min_advance_hours != null ? rule.min_advance_hours : 24))) + '</span>' +
        '<label class="rem-switch"><input type="checkbox" data-rem-toggle aria-label="' + esc(t('rem_enabled')) + '"' + (on ? ' checked' : '') + '> ' + esc(on ? t('rem_enabled') : t('rem_disabled')) + '</label>' +
        '<button type="button" class="rem-del" data-rem-delete>' + esc(t('rem_delete')) + '</button>' +
        '</div>';
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

    var regionSel = document.getElementById('rem-region');
    var prevRegion = regionSel.value || 'tw';
    fillSelect(regionSel, REGIONS.map(function (r) { return { value: r.id, label: regionName(r.id, state.lang) }; }), prevRegion);
    renderPlaceOptions();
    renderSubjectOptions();
    renderSearchResults();
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
    var matches = [];
    filterCatalog(state.catalog, kw, state.lang).forEach(function (m) {
      var opps = m.opportunities.length ? m.opportunities : (m.place.opportunities || []);
      if (kw && !m.opportunities.length && !(nameOf(m.place.name_i18n, state.lang) || '').toLocaleLowerCase().includes(String(kw).trim().toLocaleLowerCase())) return;
      opps.forEach(function (o) {
        matches.push({ place: m.place, opp: o });
      });
    });
    if (!matches.length) { ul.innerHTML = '<li class="rem-rr-sub">' + esc(t('rem_no_match')) + '</li>'; return; }
    var existing = {};
    state.rules.forEach(function (r) { existing[r.place_id + '|' + (r.opportunity_id || '')] = true; });
    ul.innerHTML = matches.slice(0, 40).map(function (m) {
      var key = m.place.place_id + '|' + (m.opp ? m.opp.opportunity_id : '');
      var added = !!existing[key];
      return '<li><span><b>' + esc(nameOf(m.place.name_i18n, state.lang) || m.place.place_id) + '</b>' +
        '<span class="rem-rr-sub"> · ' + esc(m.opp ? (nameOf(m.opp.name_i18n, state.lang) || m.opp.opportunity_id) : t('rem_any_subject')) + '</span></span>' +
        '<button type="button" data-rem-quick-add data-place="' + esc(m.place.place_id) + '" data-opp="' + esc(m.opp ? m.opp.opportunity_id : '') + '"' + (added ? ' disabled' : '') + '>' +
        esc(added ? t('rem_added_btn') : t('rem_add_btn')) + '</button></li>';
    }).join('');
  }

  function renderAll() {
    document.getElementById('page-title').textContent = t('page_title');
    document.documentElement.lang = state.lang;
    document.title = 'ChaseLights — ' + t('page_title');
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
    document.getElementById('rem-region').addEventListener('change', renderPlaceOptions);
    document.getElementById('rem-place').addEventListener('change', renderSubjectOptions);
    document.getElementById('rem-search').addEventListener('input', renderSearchResults);
    document.getElementById('rem-add-submit').addEventListener('click', function () {
      var placeId = document.getElementById('rem-place').value;
      var oppId = document.getElementById('rem-subject').value;
      addRule(placeId, oppId);
    });
    document.getElementById('rem-list').addEventListener('click', function (e) {
      var row = e.target.closest ? e.target.closest('.rem-row') : null;
      if (!row) return;
      var ruleId = row.getAttribute('data-rule-id');
      if (e.target.matches && e.target.matches('[data-rem-delete]')) {
        deleteRule(ruleId).then(function (res) {
          if (!res || !res.body || res.body.ok !== true) { showNotice('rem_err'); return; }
          showNotice('rem_removed');
          return reload();
        }).catch(function () { showNotice('rem_err'); });
      }
    });
    document.getElementById('rem-list').addEventListener('change', function (e) {
      var row = e.target.closest ? e.target.closest('.rem-row') : null;
      if (!row || !e.target.matches || !e.target.matches('[data-rem-toggle]')) return;
      var ruleId = row.getAttribute('data-rule-id');
      var on = !!e.target.checked;
      patchRule(ruleId, on).then(function (res) {
        if (!res || res.status === 401 || !res.body || res.body.ok !== true) {
          e.target.checked = !on;
          if (res && res.status === 401) { state.signedIn = false; renderAll(); }
          else showNotice('rem_err');
          return;
        }
        state.rules = state.rules.map(function (r) { return r.id === ruleId ? Object.assign({}, r, { enabled: on ? 1 : 0 }) : r; });
        renderList();
        if (window.ChaseLightsReminders) window.ChaseLightsReminders.refresh();
      }).catch(function () { e.target.checked = !on; showNotice('rem_err'); });
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

  function checkSignedIn() {
    return fetch(ME_ENDPOINT, { headers: { Accept: 'application/json' } }).then(function (r) {
      state.signedIn = r.ok;
      return r.ok;
    }).catch(function () { return false; });
  }

  function boot() {
    state.lang = lang();
    bindEvents();
    renderAll();
    Promise.all([
      fetch(CATALOG_URL, { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (b) { state.catalog = (b && b.places) || []; }),
      checkSignedIn()
    ]).then(reload).catch(function () { showNotice('rem_err'); });
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
    renderSearchResults: renderSearchResults
  };
})();
