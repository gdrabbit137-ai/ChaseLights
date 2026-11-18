/* CL-APP-09 (追加 3): 「我的題材」管理區 — the member's own custom condition
   sets across ALL places (official spots + private custom places), grouped by
   place, listed on the (renamed) 我的 page (reminders.html) alongside the
   untouched reminder list.

   Self-contained asset (custom-places.js / member-auth.js / subject-sets.js
   precedent): own tri-lingual pack, page-level CSS lives in reminders.html,
   NO app.js edits — app.js render-expression pins stay valid.

   Owner spec (追加 3):
   - grouped list: every 自訂題材 set, grouped by place; official places
     first (catalog order), then the member's private custom places, then any
     unknown place ids (honest raw id fallback — never dropped silently);
   - per group: ＋新增 (opens the condition form for THAT place);
   - per set: click the row (or ✎編輯) → jump straight into the edit form;
     🗑 two-step delete (confirm within 4s — no native confirm());
   - a top-level ＋新增題材 requires picking the place FIRST (searchable
     picker: official catalog + the member's private places) → condition form;
   - the card 題材 panel keeps its quick entry (its rows carry ✎編輯 already);
     this page is the management depth behind it;
   - caps are rendered from the WORKER's numbers only (fail-closed concrete
     numbers; free: 5 total + 5 new per day per owner ruling 追加 3) — the UI
     never invents a cap when the response omits one (fail-soft quota line);
   - 403 quota responses surface the server's tri-lingual message verbatim
     (concrete numbers, plus the gray upgrade card for free members). */
(function () {
  'use strict';
  var API = '/api/v1/subject_sets';
  var CUSTOM_API = '/api/v1/custom_places';
  var CATALOG_URL = './apps/web-v2/evaluations-latest.json';
  var LANGS = ['zh-TW', 'en', 'ja'];

  var T = {
    'zh-TW': {
      sec_title: '我的題材', sec_desc: '你在各景點的自訂拍攝題材（官方景點與私人景點）。',
      add_btn: '＋ 新增題材', group_add: '＋ 新增', badge: '自訂', private_badge: '私人',
      edit_btn: '✎ 編輯', del_btn: '🗑 刪除', del_confirm: '確認刪除',
      empty_t: '還沒有自訂題材', empty_d: '在景點卡片的題材面板按「＋ 加自訂題材」，或從這裡先選景點再建立。',
      login_note: '登入後可管理你的自訂題材',
      quota_fmt: '共 {t} 組（免費上限 {ft} 組）· 今日已新增 {d}/{da} 組',
      quota_paid: '共 {t} 組', quota_owner: '共 {t} 組 · 無上限',
      pick_title: '選擇景點', pick_ph: '搜尋景點名稱…', pick_none: '沒有符合的景點',
      pick_official: '官方景點', pick_private: '私人景點',
      ed_title: '建立自訂題材', ed_title_edit: '編輯自訂題材',
      ed_name: '題材名稱', ed_name_ph: '例如：晨光斜射反高潮位',
      sem_cloud: '雲量', sem_fog: '霧', sem_rain: '雨',
      p_low: '低雲門檻（%）', p_mid: '中雲門檻（%）', p_high: '高雲門檻（%）',
      p_precip: '降水上限（mm/h）', p_vis: '能見度下限（km）', p_wind: '風速上限（m/s）',
      p_window: '時間窗', p_months: '適用月份', p_months_hint: '不選＝全年適用；選取後只有該月份會判定',
      wt_fixed: '固定時段', wt_bs: '日出前（每日動態）', wt_as: '日出後（每日動態）', wt_bd: '日落前（每日動態）', wt_ads: '日落後（每日動態）',
      win_off: '錨點偏移（分鐘，可負）', win_add2: '＋ 加第二段', win_rm: '移除此段', win_hint: '錨點型以當日實際日出／日落動態展開，冬天夏天不同',
      cc_prev: '摘要預覽：', cc_prev_none: '（未調任何參數）',
      ed_submit: '建立此題材組', ed_submit_edit: '儲存變更',
      done_saved: '✓ 已儲存', done_deleted: '✓ 已刪除', err_net: '連線失敗，請稍後再試',
      del_title: '刪除這組自訂題材？', close: '關閉',
      months_all: '全年', months_fmt: '適用月份：{m}',
      unknown_place: '未知名稱景點',
    },
    'en': {
      sec_title: 'My subjects', sec_desc: 'Your custom shooting subjects across official and private places.',
      add_btn: '＋ New subject', group_add: '＋ New', badge: 'Custom', private_badge: 'Private',
      edit_btn: '✎ Edit', del_btn: '🗑 Delete', del_confirm: 'Confirm delete',
      empty_t: 'No custom subjects yet', empty_d: 'Use the ＋ Custom subject button in a card\u2019s subject panel, or pick a place here first.',
      login_note: 'Sign in to manage your custom subjects',
      quota_fmt: '{t} sets (free cap {ft}) · {d}/{da} created today',
      quota_paid: '{t} sets', quota_owner: '{t} sets · unlimited',
      pick_title: 'Pick a place', pick_ph: 'Search place names…', pick_none: 'No matching place',
      pick_official: 'Official places', pick_private: 'Private places',
      ed_title: 'Create custom subject', ed_title_edit: 'Edit custom subject',
      ed_name: 'Subject name', ed_name_ph: 'e.g. first light on the reef',
      sem_cloud: 'Cloud', sem_fog: 'Fog', sem_rain: 'Rain',
      p_low: 'Low-cloud cap (%)', p_mid: 'Mid-cloud cap (%)', p_high: 'High-cloud cap (%)',
      p_precip: 'Precip cap (mm/h)', p_vis: 'Visibility min (km)', p_wind: 'Wind cap (m/s)',
      p_window: 'Time window', p_months: 'Applicable months', p_months_hint: 'None = all year; when set, only those months are judged',
      wt_fixed: 'Fixed span', wt_bs: 'Before sunrise (daily dynamic)', wt_as: 'After sunrise (daily dynamic)', wt_bd: 'Before sunset (daily dynamic)', wt_ads: 'After sunset (daily dynamic)',
      win_off: 'Anchor offset (minutes, may be negative)', win_add2: '＋ Add a second span', win_rm: 'Remove this span', win_hint: 'Anchor spans expand with each day\u2019s REAL sunrise/sunset — winter and summer differ',
      cc_prev: 'Summary:', cc_prev_none: '(no parameters set)',
      ed_submit: 'Create this set', ed_submit_edit: 'Save changes',
      done_saved: '✓ Saved', done_deleted: '✓ Deleted', err_net: 'Network error — try again later',
      del_title: 'Delete this custom subject?', close: 'Close',
      months_all: 'All year', months_fmt: 'Months: {m}',
      unknown_place: 'Unnamed place',
    },
    'ja': {
      sec_title: '自作題材', sec_desc: '公式・プライベート両方のスポットに作成した自作題材。',
      add_btn: '＋ 題材を追加', group_add: '＋ 追加', badge: '自作', private_badge: 'プライベート',
      edit_btn: '✎ 編集', del_btn: '🗑 削除', del_confirm: '削除を確認',
      empty_t: '自作題材はまだありません', empty_d: 'カードの題材パネル「＋ 自作題材を追加」から、またはここでスポットを選んで作成できます。',
      login_note: 'ログインすると自作題材を管理できます',
      quota_fmt: '合計 {t} 件（無料上限 {ft} 件）· 本日 {d}/{da} 件作成',
      quota_paid: '合計 {t} 件', quota_owner: '合計 {t} 件 · 無制限',
      pick_title: 'スポットを選択', pick_ph: 'スポット名を検索…', pick_none: '該当するスポットがありません',
      pick_official: '公式スポット', pick_private: 'プライベート',
      ed_title: '自作題材を作成', ed_title_edit: '自作題材を編集',
      ed_name: '題材名', ed_name_ph: '例：朝焼けの反射',
      sem_cloud: '雲量', sem_fog: '霧', sem_rain: '雨',
      p_low: '下層雲しきい値（%）', p_mid: '中層雲しきい値（%）', p_high: '上層雲しきい値（%）',
      p_precip: '降水上限（mm/h）', p_vis: '視程下限（km）', p_wind: '風速上限（m/s）',
      p_window: '時間帯', p_months: '適用月', p_months_hint: '未選択＝通年；選択するとその月のみ判定',
      wt_fixed: '固定時間帯', wt_bs: '日の出前（毎日動的）', wt_as: '日の出後（毎日動的）', wt_bd: '日の入前（毎日動的）', wt_ads: '日の入後（毎日動的）',
      win_off: 'アンカーオフセット（分・負可）', win_add2: '＋ 2つ目を追加', win_rm: 'この枠を削除', win_hint: 'アンカーは当日の実際の日の出入りから毎日展開（季節で変わる）',
      cc_prev: 'サマリー：', cc_prev_none: '（未設定）',
      ed_submit: 'この題材を作成', ed_submit_edit: '変更を保存',
      done_saved: '✓ 保存しました', done_deleted: '✓ 削除しました', err_net: '通信エラー — 後でお試しください',
      del_title: 'この自作題材を削除？', close: '閉じる',
      months_all: '通年', months_fmt: '適用月：{m}',
      unknown_place: '名称未設定のスポット',
    },
  };

  var state = { member: null, sets: [], caps: null, counts: null, catalog: [], customPlaces: [], delArm: null };

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
  function api(path, opts) {
    opts = opts || {};
    opts.credentials = 'same-origin';
    opts.cache = 'no-store';
    if (typeof window.__clssLibFetch === 'function') return Promise.resolve(window.__clssLibFetch(path, opts));
    return fetch(path, opts);
  }
  function memberMsg(m) {
    if (!m) return '';
    if (typeof m === 'string') return m;
    return m[currentLang()] || m['zh-TW'] || '';
  }
  function fmt(tpl, map) {
    return String(tpl || '').replace(/\{(\w+)\}/g, function (_, k) { return map[k] != null ? String(map[k]) : ''; });
  }

  // ───────────────────────── pure helpers (unit-tested) ─────────────────
  function summaryOf(cc, lang) {
    if (!cc || typeof cc !== 'object') return '';
    var zh = lang === 'zh-TW', ja = lang === 'ja';
    var parts = [];
    if (cc.cloud_low_max != null) parts.push((zh ? '低雲≤' : ja ? '下層雲≤' : 'low-cloud≤') + cc.cloud_low_max + '%');
    if (cc.cloud_mid_max != null) parts.push((zh ? '中雲≤' : ja ? '中層雲≤' : 'mid-cloud≤') + cc.cloud_mid_max + '%');
    if (cc.cloud_high_max != null) parts.push((zh ? '高雲≤' : ja ? '上層雲≤' : 'high-cloud≤') + cc.cloud_high_max + '%');
    if (cc.precip_max_mmh != null) parts.push((zh ? '雨≤' : ja ? '雨≤' : 'rain≤') + cc.precip_max_mmh + 'mm/h');
    if (cc.visibility_min_km != null) parts.push((zh ? '能見度≥' : ja ? '視程≥' : 'vis≥') + cc.visibility_min_km + 'km');
    if (cc.wind_max_ms != null) parts.push((zh ? '風≤' : ja ? '風≤' : 'wind≤') + cc.wind_max_ms + 'm/s');
    if (Array.isArray(cc.windows) && cc.windows.length) {
      parts.push(cc.windows.map(function (s) { return winSegSummary(s, lang); }).join('＋'));
    } else if (cc.window_start && cc.window_end) {
      parts.push(cc.window_start + '–' + cc.window_end);
    }
    if (Array.isArray(cc.months) && cc.months.length) parts.push((zh ? '月份' : ja ? '月' : 'months') + ':' + cc.months.join(','));
    return parts.join(' · ');
  }
  function monthsLine(months) {
    var lang = currentLang();
    return (months && months.length)
      ? fmt(t().months_fmt, { m: months.map(function (m) { return m + (lang === 'en' ? '' : '月'); }).join(lang === 'en' ? ', ' : '、') })
      : t().months_all;
  }
  // Group sets by place. Order: official catalog places first (catalog order),
  // then the member's private places (API order), then unknown ids in first-seen
  // order. Unknown ids fall back to the raw id — never dropped silently.
  function groupSets(sets, catalog, customPlaces) {
    var byPlace = new Map();
    (sets || []).forEach(function (s) {
      var pid = s.placeId || s.place_id || '';
      if (!byPlace.has(pid)) byPlace.set(pid, []);
      byPlace.get(pid).push(s);
    });
    var order = [];
    (catalog || []).forEach(function (p) { if (byPlace.has(p.place_id)) order.push(p.place_id); });
    (customPlaces || []).forEach(function (p) {
      var pid = p.id || p.place_id;
      if (byPlace.has(pid) && order.indexOf(pid) < 0) order.push(pid);
    });
    byPlace.forEach(function (_, pid) { if (order.indexOf(pid) < 0) order.push(pid); });
    return order.map(function (pid) {
      var name = placeName(pid, catalog, customPlaces);
      var isPrivate = !catalog.some(function (p) { return p.place_id === pid; });
      return { placeId: pid, name: name, isPrivate: isPrivate, sets: byPlace.get(pid) };
    });
  }
  function placeName(placeId, catalog, customPlaces) {
    for (var i = 0; i < (catalog || []).length; i++) {
      if (catalog[i].place_id === placeId) {
        var n = catalog[i].name_i18n;
        var lg = currentLang();
        return (n && (n[lg] || n['zh-TW'] || n.en)) || placeId;
      }
    }
    for (var j = 0; j < (customPlaces || []).length; j++) {
      if ((customPlaces[j].id || customPlaces[j].place_id) === placeId) return customPlaces[j].name || placeId;
    }
    return placeId || t().unknown_place;
  }
  function pickerEntries(catalog, customPlaces, keyword, lg) {
    var kw = String(keyword || '').trim().toLocaleLowerCase();
    var official = [], priv = [];
    (catalog || []).forEach(function (p) {
      var nm = placeName(p.place_id, catalog, customPlaces);
      if (kw && (nm + ' ' + p.place_id).toLocaleLowerCase().indexOf(kw) < 0) return;
      official.push({ placeId: p.place_id, name: nm, isPrivate: false });
    });
    (customPlaces || []).forEach(function (p) {
      var pid = p.id || p.place_id;
      var nm = p.name || pid;
      if (kw && (nm + ' ' + pid).toLocaleLowerCase().indexOf(kw) < 0) return;
      priv.push({ placeId: pid, name: nm, isPrivate: true });
    });
    return { official: official, private: priv };
  }
  function quotaLine(counts, caps, level) {
    if (!counts) return '';
    var total = counts.total;
    if (level === 'owner') return fmt(t().quota_owner, { t: total });
    if (caps && typeof caps.free_total === 'number') {
      return fmt(t().quota_fmt, { t: total, ft: caps.free_total, d: counts.daily_used || 0, da: caps.daily_add });
    }
    return fmt(t().quota_paid, { t: total });
  }

  // ───────────────────────── session (silent refresh) ─────────────────
  var sessionPromise = null;
  function fetchMe() {
    return api('/api/v1/auth/me').then(function (r) {
      if (r.status === 401) {
        return api('/api/v1/auth/refresh', { method: 'POST' }).then(function (rr) {
          if (rr.status !== 200) return { user: null };
          return api('/api/v1/auth/me').then(function (r2) { return r2.ok ? r2.json() : { user: null }; });
        }).catch(function () { return { user: null }; });
      }
      return r.ok ? r.json() : { user: null };
    }).catch(function () { return { user: null }; });
  }
  function ensureSignedIn() {
    if (!sessionPromise) sessionPromise = fetchMe();
    return sessionPromise.then(function (j) {
      state.member = (j && j.user) || null;
      return !!state.member;
    });
  }
  document.addEventListener('chaselights:auth', function () {
    sessionPromise = null;
    state.member = null;
    render();
  });

  // ───────────────────────── toast + overlay ─────────────────────────
  function toast(msg) {
    var el = document.getElementById('sslib-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'sslib-toast';
      el.className = 'sslib-toast';
      el.setAttribute('role', 'status');
      document.body.appendChild(el);
    }
    el.textContent = typeof msg === 'string' ? msg : memberMsg(msg);
    el.classList.add('show');
    clearTimeout(toast._tm);
    toast._tm = setTimeout(function () { el.classList.remove('show'); }, 6000);
  }
  function ensureOverlay() {
    var ov = document.getElementById('sslib-overlay');
    if (!ov) {
      ov = document.createElement('div');
      ov.id = 'sslib-overlay';
      ov.className = 'sslib-overlay';
      ov.innerHTML = '<div class="sslib-modal" role="dialog" aria-modal="true"></div>';
      ov.addEventListener('click', function (e) { if (e.target === ov) closeOverlay(); });
      document.body.appendChild(ov);
    }
    return ov;
  }
  function openOverlay(html) {
    var ov = ensureOverlay();
    ov.querySelector('.sslib-modal').innerHTML = html;
    ov.classList.add('open');
    document.body.classList.add('sslib-lock');
    var first = ov.querySelector('input, select, button.sslib-submit');
    if (first) { try { first.focus({ preventScroll: true }); } catch (e) { try { first.focus(); } catch (e2) {} } }
  }
  function closeOverlay() {
    var ov = document.getElementById('sslib-overlay');
    if (!ov) return;
    ov.classList.remove('open');
    document.body.classList.remove('sslib-lock');
  }

  // ───────────────────────── data ─────────────────────────
  function loadCatalog() {
    return fetch(CATALOG_URL, { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (b) { state.catalog = (b && b.places) || []; })
      .catch(function () { state.catalog = []; });
  }
  function loadCustomPlaces() {
    return api(CUSTOM_API)
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (b) { state.customPlaces = (b && b.places) || []; })
      .catch(function () { state.customPlaces = []; });
  }
  function loadSets() {
    return api(API)
      .then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); });
  }

  // ───────────────────────── render ─────────────────────────
  function render() {
    var host = document.getElementById('ss-lib-root');
    if (!host) return;
    ensureSignedIn().then(function (signed) {
      if (!signed) {
        host.innerHTML = '<div class="sslib-login">' + esc(t().login_note) + '</div>';
        return null;
      }
      host.innerHTML = '<div class="sslib-head"><div><div class="sslib-title">' + esc(t().sec_title) + '</div>' +
        '<div class="sslib-desc">' + esc(t().sec_desc) + '</div></div>' +
        '<span class="sslib-quota" id="sslib-quota"></span>' +
        '<button type="button" class="sslib-add" id="sslib-add">' + esc(t().add_btn) + '</button></div>' +
        '<div id="sslib-groups"><div class="sslib-loading">…</div></div>';
      var addBtn = host.querySelector('#sslib-add');
      if (addBtn) addBtn.addEventListener('click', function (e) { e.preventDefault(); openPicker(); });
      return Promise.all([loadCatalog(), loadCustomPlaces(), loadSets()]).then(function (rs) {
        var listRes = rs[2];
        var groupsHost = host.querySelector('#sslib-groups');
        var quotaEl = host.querySelector('#sslib-quota');
        if (listRes.status === 401) {
          if (groupsHost) groupsHost.innerHTML = '<div class="sslib-login">' + esc(t().login_note) + '</div>';
          return;
        }
        if (listRes.status !== 200) {
          if (groupsHost) groupsHost.innerHTML = '<div class="sslib-login">' + esc((listRes.body && listRes.body.error) || ('HTTP ' + listRes.status)) + '</div>';
          return;
        }
        var data = listRes.body || {};
        state.sets = data.sets || [];
        state.caps = data.caps || null;
        state.counts = data.counts || null;
        if (quotaEl) quotaEl.textContent = quotaLine(state.counts, state.caps, data.level || (state.member && state.member.level) || 'free');
        if (!groupsHost) return;
        if (!state.sets.length) {
          groupsHost.innerHTML = '<div class="sslib-empty"><div class="t">' + esc(t().empty_t) + '</div><div class="d">' + esc(t().empty_d) + '</div></div>';
          return;
        }
        var groups = groupSets(state.sets, state.catalog, state.customPlaces);
        groupsHost.innerHTML = groups.map(function (g) { return groupHtml(g); }).join('');
        wireGroups(groupsHost);
      }).catch(function () {
        var groupsHost = host.querySelector('#sslib-groups');
        if (groupsHost) groupsHost.innerHTML = '<div class="sslib-login">' + esc(t().err_net) + '</div>';
      });
    });
  }
  function groupHtml(g) {
    return '<div class="sslib-group" data-sslib-place="' + esc(g.placeId) + '">' +
      '<div class="sslib-group-head">' +
      '<span class="sslib-place-name">' + esc(g.name) + '</span>' +
      (g.isPrivate ? '<span class="sslib-badge sslib-badge-priv">' + esc(t().private_badge) + '</span>' : '') +
      '<span class="sslib-count">' + g.sets.length + '</span>' +
      '<button type="button" class="sslib-act sslib-group-add" data-sslib-add-place="' + esc(g.placeId) + '">' + esc(t().group_add) + '</button>' +
      '</div>' +
      g.sets.map(function (s) { return setRowHtml(s); }).join('') +
      '</div>';
  }
  function setRowHtml(s) {
    var cc = s.conditions || {};
    return '<div class="sslib-row" data-sslib-set="' + esc(s.id) + '" tabindex="0" role="button" aria-label="' + esc(t().edit_btn) + ' ' + esc(s.name) + '">' +
      '<span class="sslib-row-name">' + esc(s.name) + '</span>' +
      '<span class="sslib-badge">' + esc(t().badge) + '</span>' +
      '<span class="sslib-row-sum">' + esc(summaryOf(cc, currentLang()) || monthsLine(s.months)) + '</span>' +
      '<span class="sslib-row-actions">' +
      '<button type="button" class="sslib-act" data-sslib-act="edit" data-sslib-id="' + esc(s.id) + '">' + esc(t().edit_btn) + '</button>' +
      '<button type="button" class="sslib-act sslib-act-del" data-sslib-act="del" data-sslib-id="' + esc(s.id) + '">' + esc(t().del_btn) + '</button>' +
      '</span></div>';
  }
  function findSet(id) {
    for (var i = 0; i < state.sets.length; i++) if (state.sets[i].id === id) return state.sets[i];
    return null;
  }
  function wireGroups(groupsHost) {
    groupsHost.querySelectorAll('.sslib-row').forEach(function (row) {
      row.addEventListener('click', function (e) {
        if (e.target.closest('button')) return;
        var id = row.getAttribute('data-sslib-set');
        var set = findSet(id);
        if (set) openEditor(set.placeId, set);
      });
      row.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          var set = findSet(row.getAttribute('data-sslib-set'));
          if (set) openEditor(set.placeId, set);
        }
      });
    });
    groupsHost.querySelectorAll('[data-sslib-act]').forEach(function (b) {
      b.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        var id = b.getAttribute('data-sslib-id');
        if (b.getAttribute('data-sslib-act') === 'edit') {
          var set = findSet(id);
          if (set) openEditor(set.placeId, set);
        } else if (b.getAttribute('data-sslib-act') === 'del') {
          deleteArmed(b, id);
        }
      });
    });
    groupsHost.querySelectorAll('[data-sslib-add-place]').forEach(function (b) {
      b.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        openEditor(b.getAttribute('data-sslib-add-place'), null);
      });
    });
  }
  function deleteArmed(btn, id) {
    if (btn.getAttribute('data-sslib-armed') === '1') {
      api(API + '/' + id, { method: 'DELETE' })
        .then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); })
        .then(function (r) {
          if (r.status === 200) { toast(t().done_deleted); render(); }
          else { toast(memberMsg(r.body && r.body.message) || (r.body && r.body.error) || ('HTTP ' + r.status)); }
        })
        .catch(function () { toast(t().err_net); });
      return;
    }
    btn.setAttribute('data-sslib-armed', '1');
    btn.setAttribute('aria-label', t().del_title);
    btn.textContent = t().del_confirm;
    btn.classList.add('sslib-armed');
    clearTimeout(btn._disarm);
    btn._disarm = setTimeout(function () {
      btn.removeAttribute('data-sslib-armed');
      btn.classList.remove('sslib-armed');
      btn.textContent = t().del_btn;
    }, 4000);
  }

  // ───────────────────────── place picker (新增：先選景點) ─────────────
  function openPicker() {
    return loadCatalog().then(function () {
      return loadCustomPlaces();
    }).then(function () {
      var entries = pickerEntries(state.catalog, state.customPlaces, '', currentLang());
      openOverlay(
        '<div class="sslib-m-head"><div class="name">' + esc(t().pick_title) + '</div>' +
        '<button type="button" class="sslib-close" data-sslib-close aria-label="' + esc(t().close) + '">✕</button></div>' +
        '<input id="sslib-pick-search" class="sslib-search" type="search" autocomplete="off" placeholder="' + esc(t().pick_ph) + '">' +
        '<div class="sslib-pick-sec">' + esc(t().pick_official) + '</div>' +
        '<div id="sslib-pick-official" class="sslib-pick-list"></div>' +
        '<div class="sslib-pick-sec">' + esc(t().pick_private) + '</div>' +
        '<div id="sslib-pick-private" class="sslib-pick-list"></div>'
      );
      var ov = document.getElementById('sslib-overlay');
      ov.querySelectorAll('[data-sslib-close]').forEach(function (b) { b.addEventListener('click', closeOverlay); });
      function paint(entriesNow) {
        var mk = function (list) {
          return list.length
            ? list.map(function (e) {
                return '<button type="button" class="sslib-pick-item" data-sslib-place="' + esc(e.placeId) + '">' + esc(e.name) +
                  (e.isPrivate ? ' <span class="sslib-badge sslib-badge-priv">' + esc(t().private_badge) + '</span>' : '') + '</button>';
              }).join('')
            : '<div class="sslib-pick-none">' + esc(t().pick_none) + '</div>';
        };
        var a = ov.querySelector('#sslib-pick-official'), b = ov.querySelector('#sslib-pick-private');
        if (a) a.innerHTML = mk(entriesNow.official);
        if (b) b.innerHTML = mk(entriesNow.private);
      }
      paint(entries);
      var search = ov.querySelector('#sslib-pick-search');
      if (search) search.addEventListener('input', function () {
        paint(pickerEntries(state.catalog, state.customPlaces, search.value, currentLang()));
      });
      ov.addEventListener('click', function (e) {
        var item = e.target.closest('[data-sslib-place]');
        if (!item) return;
        closeOverlay();
        openEditor(item.getAttribute('data-sslib-place'), null);
      });
    });
  }

  // ───────────────────────── condition form (先選景點 → 表單) ──────────
  var CC_SEMANTIC = {
    cloud: {
      key: 'cloud_low_max',
      options: {
        'zh-TW': [['any', '不在乎', null], ['clear', '晴（低雲 ≤15%）', 15], ['partly', '少雲（低雲 ≤40%）', 40], ['cloudy', '多雲也可（低雲 ≤70%）', 70]],
        'en': [['any', "Don't care", null], ['clear', 'Clear (low ≤15%)', 15], ['partly', 'Partly cloudy (low ≤40%)', 40], ['cloudy', 'Cloudy OK (low ≤70%)', 70]],
        'ja': [['any', 'こだわらない', null], ['clear', '晴れ（下層雲 ≤15%）', 15], ['partly', '雲少なめ（下層雲 ≤40%）', 40], ['cloudy', '曇り可（下層雲 ≤70%）', 70]],
      },
      values: { any: null, clear: 15, partly: 40, cloudy: 70 },
    },
    fog: {
      key: 'visibility_min_km',
      options: {
        'zh-TW': [['any', '不限', null], ['thin', '薄霧可（能見度 ≥1 km）', 1], ['clear', '要通透（能見度 ≥8 km）', 8], ['ultra', '極通透（能見度 ≥20 km）', 20]],
        'en': [['any', 'Any', null], ['thin', 'Mist OK (vis ≥1 km)', 1], ['clear', 'Needs clarity (vis ≥8 km)', 8], ['ultra', 'Ultra clear (vis ≥20 km)', 20]],
        'ja': [['any', '指定なし', null], ['thin', '薄霧可（視程 ≥1 km）', 1], ['clear', '透明感必須（視程 ≥8 km）', 8], ['ultra', '超透明（視程 ≥20 km）', 20]],
      },
      values: { any: null, thin: 1, clear: 8, ultra: 20 },
    },
    rain: {
      key: 'precip_max_mmh',
      options: {
        'zh-TW': [['any', '不限', null], ['no', '不可下雨（0 mm/h）', 0], ['drizzle', '微雨可（≤0.5 mm/h）', 0.5], ['light', '小雨可（≤2 mm/h）', 2]],
        'en': [['any', 'Any', null], ['no', 'No rain (0 mm/h)', 0], ['drizzle', 'Drizzle OK (≤0.5 mm/h)', 0.5], ['light', 'Light rain OK (≤2 mm/h)', 2]],
        'ja': [['any', '指定なし', null], ['no', '雨は不可（0 mm/h）', 0], ['drizzle', '霧雨可（≤0.5 mm/h）', 0.5], ['light', '小雨可（≤2 mm/h）', 2]],
      },
      values: { any: null, no: 0, drizzle: 0.5, light: 2 },
    },
  };
  function semanticValue(axis, val) {
    var m = CC_SEMANTIC[axis];
    if (!m || val == null) return null;
    return val === 'any' ? null : m.values[val];
  }
  function semanticMappedLabel(axis, val) {
    var m = CC_SEMANTIC[axis]; if (!m) return '';
    var opts = m.options[currentLang()] || m.options['zh-TW'];
    for (var i = 0; i < opts.length; i++) if (opts[i][0] === val) return opts[i][2];
    return '';
  }
  function currentSemantic(axis, cc) {
    var m = CC_SEMANTIC[axis]; if (!m) return 'any';
    var val = cc && cc[m.key];
    if (val == null) return 'any';
    var entries = Object.keys(m.values);
    for (var i = 0; i < entries.length; i++) if (entries[i] !== 'any' && m.values[entries[i]] === val) return entries[i];
    return 'any';
  }
  // ─── CL-APP-09 patch-2: anchor + multi-segment windows (library editor) ───
  var WTYPES = ['fixed', 'before_sunrise', 'after_sunrise', 'before_sunset', 'after_sunset'];
  function wtLabel(type) {
    return { fixed: t().wt_fixed, before_sunrise: t().wt_bs, after_sunrise: t().wt_as, before_sunset: t().wt_bd, after_sunset: t().wt_ads }[type] || '';
  }
  function winSegSummary(seg, lang) {
    if (!seg || !seg.type || seg.type === 'fixed') {
      return (seg && seg.start ? seg.start : '?') + '–' + (seg && seg.end ? seg.end : '?');
    }
    var lbl = wtLabel(seg.type).replace(/（.*?）/, '').replace(/ \(daily dynamic\)/, '');
    var off = (seg.offset_minutes != null && seg.offset_minutes !== 0)
      ? ((seg.offset_minutes > 0 ? '+' : '−') + Math.abs(seg.offset_minutes) + (lang === 'zh-TW' ? '分' : lang === 'ja' ? '分' : 'min'))
      : '';
    return lbl + off;
  }
  var libWinState = [{ type: 'fixed', start: '', end: '' }];
  // same hook pattern as subject-sets.js: libWireWinArea sits at module scope,
  // the editor's refreshPrev is local — register it per open (patch-2 fix)
  var libWinPrevHook = null;
  function libWinRefreshPrev() { if (libWinPrevHook) libWinPrevHook(); }
  function libWindowSegsOf(cc) {
    if (cc && Array.isArray(cc.windows) && cc.windows.length) return cc.windows;
    if (cc && cc.window_start && cc.window_end) return [{ type: 'fixed', start: cc.window_start, end: cc.window_end }];
    return [{ type: 'fixed', start: '', end: '' }];
  }
  function libRenderWinArea() {
    var host = document.querySelector('#sslib-win-area');
    if (!host) return;
    host.innerHTML = libWinAreaHtml();
    libWireWinArea();
  }
  function libWinAreaHtml() {
    var out = '';
    for (var i = 0; i < libWinState.length; i++) out += libWinSegHtml(i, libWinState[i]);
    out += (libWinState.length < 2 ? '<button type="button" class="sslib-act" id="sslib-win-add">' + esc(t().win_add2) + '</button>' : '') +
      '<div class="hint">' + esc(t().win_hint) + '</div>';
    return out;
  }
  function libWinSegHtml(i, seg) {
    var idp = 'sslib-ws' + i;
    var typeSel = '<select id="' + idp + '-type" class="sslib-sel">' +
      WTYPES.map(function (w) { return '<option value="' + w + '"' + (w === seg.type ? ' selected' : '') + '>' + esc(wtLabel(w)) + '</option>'; }).join('') +
      '</select>';
    var fields;
    if (seg.type === 'fixed') {
      fields = '<input id="' + idp + '-start" type="time" value="' + esc(seg.start || '') + '"><span class="sslib-dash" aria-hidden="true">–</span>' +
        '<input id="' + idp + '-end" type="time" value="' + esc(seg.end || '') + '">';
    } else {
      fields = '<input id="' + idp + '-off" inputmode="numeric" value="' + esc(seg.offset_minutes != null ? String(seg.offset_minutes) : '') + '" placeholder="0" style="max-width:90px">' +
        '<span class="hint" style="flex:1">' + esc(t().win_off) + '</span>';
    }
    return '<div class="sslib-winseg" data-sslib-ws="' + i + '" style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">' + typeSel + fields +
      (i === 1 ? '<button type="button" class="sslib-act sslib-del" id="sslib-win-rm" aria-label="' + esc(t().win_rm) + '">✕</button>' : '') +
      '</div>';
  }
  function libReadWinState() {
    var ov = document.getElementById('sslib-overlay');
    var segs = [];
    for (var i = 0; i < 2; i++) {
      var typeEl = ov.querySelector('#sslib-ws' + i + '-type');
      if (!typeEl) { if (libWinState[i]) segs.push(libWinState[i]); continue; }
      if (typeEl.value === 'fixed') {
        var s = (ov.querySelector('#sslib-ws' + i + '-start') || {}).value || '';
        var e = (ov.querySelector('#sslib-ws' + i + '-end') || {}).value || '';
        segs.push({ type: 'fixed', start: String(s).trim(), end: String(e).trim() });
      } else {
        var offEl = ov.querySelector('#sslib-ws' + i + '-off');
        var off = offEl && offEl.value.trim() !== '' ? parseInt(offEl.value, 10) : 0;
        segs.push({ type: typeEl.value, offset_minutes: isFinite(off) ? off : 0 });
      }
    }
    return segs;
  }
  function libWireWinArea() {
    var ov = document.getElementById('sslib-overlay');
    var addBtn = ov.querySelector('#sslib-win-add');
    if (addBtn) addBtn.addEventListener('click', function () {
      libWinState = libReadWinState();
      if (libWinState.length < 2) libWinState.push({ type: 'fixed', start: '', end: '' });
      libRenderWinArea();
      libWinRefreshPrev();
    });
    var rmBtn = ov.querySelector('#sslib-win-rm');
    if (rmBtn) rmBtn.addEventListener('click', function () {
      libWinState = libReadWinState().slice(0, 1);
      libRenderWinArea();
      libWinRefreshPrev();
    });
    [0, 1].forEach(function (i) {
      var typeEl = ov.querySelector('#sslib-ws' + i + '-type');
      if (!typeEl) return;
      typeEl.addEventListener('change', function () {
        libWinState = libReadWinState();
        libWinState[i] = typeEl.value === 'fixed' ? { type: 'fixed', start: '', end: '' } : { type: typeEl.value, offset_minutes: 0 };
        libRenderWinArea();
        libWinRefreshPrev();
      });
      ['start', 'end', 'off'].forEach(function (f) {
        var el = ov.querySelector('#sslib-ws' + i + '-' + f);
        if (el) el.addEventListener('change', libWinRefreshPrev);
      });
    });
  }
  function monthsHtml(selected) {
    var sel = Array.isArray(selected) ? selected : [];
    var out = '';
    var lg = currentLang();
    for (var m = 1; m <= 12; m++) {
      out += '<label class="sslib-mo"><input type="checkbox" id="sslib-m' + m + '" value="' + m + '"' +
        (sel.indexOf(m) >= 0 ? ' checked' : '') + '>' + m + (lg === 'en' ? '' : '月') + '</label>';
    }
    return out;
  }
  function readCc() {
    var ov = document.getElementById('sslib-overlay');
    var num = function (id) { var el = ov.querySelector('#' + id); if (!el) return null; var v = el.value.trim(); if (!v) return null; var n = Number(v); return isFinite(n) ? n : null; };
    var out = {};
    ['sslib-cc-low:cloud_low_max', 'sslib-cc-mid:cloud_mid_max', 'sslib-cc-high:cloud_high_max', 'sslib-cc-precip:precip_max_mmh', 'sslib-cc-vis:visibility_min_km', 'sslib-cc-wind:wind_max_ms'].forEach(function (pair) {
      var parts = pair.split(':'); var n = num(parts[0]); if (n != null) out[parts[1]] = n;
    });
    var wsSeg = libReadWinState().filter(function (s) { return s.type === 'fixed' ? (s.start && s.end) : true; });
    if (wsSeg.length === 1 && wsSeg[0].type === 'fixed' && /^\d\d:\d\d$/.test(wsSeg[0].start) && /^\d\d:\d\d$/.test(wsSeg[0].end)) {
      out.window_start = wsSeg[0].start; out.window_end = wsSeg[0].end;
    } else if (wsSeg.length) {
      out.windows = wsSeg.map(function (s) {
        return s.type === 'fixed' ? { type: 'fixed', start: s.start, end: s.end } : { type: s.type, offset_minutes: s.offset_minutes || 0 };
      });
    }
    var monthsWrap = ov.querySelector('#sslib-cc-months');
    if (monthsWrap) {
      var months = [].slice.call(monthsWrap.querySelectorAll('input[type="checkbox"]:checked'))
        .map(function (b) { return Number(b.value); }).filter(function (n) { return n >= 1 && n <= 12; });
      if (months.length) out.months = months.sort(function (a, b) { return a - b; });
    }
    return out;
  }
  function openEditor(placeId, set) {
    var lg = currentLang();
    var cc = Object.assign({}, (set && set.conditions) || {});
    libWinState = libWindowSegsOf(cc).slice(0, 2);
    var semSel = function (axis, label) {
      var m = CC_SEMANTIC[axis];
      var o = m.options[lg] || m.options['zh-TW'];
      var cur = currentSemantic(axis, cc);
      return '<div class="sslib-fld wide"><label>' + esc(label) + '</label>' +
        '<div class="sslib-sem-wrap"><select id="sslib-sem-' + axis + '" class="sslib-sel">' +
        o.map(function (x) { return '<option value="' + x[0] + '"' + (x[0] === cur ? ' selected' : '') + '>' + esc(x[1]) + '</option>'; }).join('') +
        '</select><span class="sslib-sem-map" id="sslib-sem-map-' + axis + '">→ ' + esc(semanticMappedLabel(axis, cur)) + '</span></div></div>';
    };
    function v(k) { return cc[k] == null ? '' : String(cc[k]); }
    var isEdit = !!set;
    openOverlay(
      '<div class="sslib-m-head"><div><div class="name">' + esc(isEdit ? t().ed_title_edit : t().ed_title) + '</div>' +
      '<div class="sub">' + esc(summaryOf(cc, lg) || t().cc_prev_none) + '</div></div>' +
      '<button type="button" class="sslib-close" data-sslib-close aria-label="' + esc(t().close) + '">✕</button></div>' +
      '<div class="sslib-fld"><label>' + esc(t().ed_name) + '</label>' +
      '<input id="sslib-name" class="sslib-inp" maxlength="60" value="' + esc((set && set.name) || '') + '" placeholder="' + esc(t().ed_name_ph) + '"></div>' +
      '<div class="sslib-params">' +
      semSel('cloud', t().sem_cloud) +
      semSel('fog', t().sem_fog) +
      semSel('rain', t().sem_rain) +
      '<div class="sslib-fld wide"><label>' + esc(t().p_window) + '</label><div id="sslib-win-area"></div></div>' +
      '<div class="sslib-fld wide"><label>' + esc(t().p_months) + '</label>' +
      '<div class="sslib-months" id="sslib-cc-months">' + monthsHtml((set && set.months) || []) + '</div>' +
      '<div class="hint">' + esc(t().p_months_hint) + '</div></div>' +
      '</div>' +
      '<details class="sslib-advanced"><summary>⋯</summary>' +
      '<div class="sslib-params" style="margin-top:8px">' +
      '<div class="sslib-fld"><label>' + esc(t().p_low) + '</label><input id="sslib-cc-low" inputmode="decimal" value="' + esc(v('cloud_low_max')) + '"></div>' +
      '<div class="sslib-fld"><label>' + esc(t().p_mid) + '</label><input id="sslib-cc-mid" inputmode="decimal" value="' + esc(v('cloud_mid_max')) + '"></div>' +
      '<div class="sslib-fld"><label>' + esc(t().p_high) + '</label><input id="sslib-cc-high" inputmode="decimal" value="' + esc(v('cloud_high_max')) + '"></div>' +
      '<div class="sslib-fld"><label>' + esc(t().p_precip) + '</label><input id="sslib-cc-precip" inputmode="decimal" value="' + esc(v('precip_max_mmh')) + '"></div>' +
      '<div class="sslib-fld"><label>' + esc(t().p_vis) + '</label><input id="sslib-cc-vis" inputmode="decimal" value="' + esc(v('visibility_min_km')) + '"></div>' +
      '<div class="sslib-fld"><label>' + esc(t().p_wind) + '</label><input id="sslib-cc-wind" inputmode="decimal" value="' + esc(v('wind_max_ms')) + '"></div>' +
      '</div></details>' +
      '<div class="sslib-preview"><span class="lbl">' + esc(t().cc_prev) + '</span><span class="k" id="sslib-cc-prev">' + esc(summaryOf(cc, lg) || t().cc_prev_none) + '</span></div>' +
      '<button type="button" class="sslib-submit" id="sslib-submit">' + esc(isEdit ? t().ed_submit_edit : t().ed_submit) + '</button>'
    );
    var ov = document.getElementById('sslib-overlay');
    ov.querySelectorAll('[data-sslib-close]').forEach(function (b) { b.addEventListener('click', closeOverlay); });
    libWinPrevHook = refreshPrev; // patch-2: the win editor's preview hook
    libRenderWinArea();
    var nameInput = ov.querySelector('#sslib-name');
    if (nameInput) nameInput.focus({ preventScroll: true });
    function refreshPrev() {
      var el = ov.querySelector('#sslib-cc-prev');
      if (el) el.textContent = summaryOf(readCc(), currentLang()) || t().cc_prev_none;
    }
    ['cloud', 'fog', 'rain'].forEach(function (axis) {
      var sel = ov.querySelector('#sslib-sem-' + axis);
      if (!sel) return;
      sel.addEventListener('change', function () {
        var val = sel.value;
        var map = ov.querySelector('#sslib-sem-map-' + axis);
        if (map) map.textContent = '→ ' + semanticMappedLabel(axis, val);
        var target = { cloud: '#sslib-cc-low', fog: '#sslib-cc-vis', rain: '#sslib-cc-precip' }[axis];
        var inp = ov.querySelector(target);
        if (inp) {
          var mapped = semanticValue(axis, val);
          inp.value = mapped == null ? '' : String(mapped);
        }
        refreshPrev();
      });
    });
    ov.querySelectorAll('.sslib-advanced input').forEach(function (inp) { inp.addEventListener('change', refreshPrev); });
    var monthsWrap = ov.querySelector('#sslib-cc-months');
    if (monthsWrap) monthsWrap.querySelectorAll('input[type="checkbox"]').forEach(function (b) { b.addEventListener('change', refreshPrev); });
    ov.querySelector('#sslib-submit').addEventListener('click', function () {
      var name = ((ov.querySelector('#sslib-name') || {}).value || '').trim();
      if (!name) { toast(t().ed_name_ph); return; }
      var ccOut = readCc();
      var months = ccOut.months || []; delete ccOut.months;
      var body = { place_id: placeId, name: name, conditions: ccOut, months: months };
      if (isEdit) {
        body.template_id = set.templateId || null;
        body.base_rev = set.baseRev != null ? set.baseRev : null;
        body.base_conditions = set.baseConditions || {};
      }
      var p = isEdit
        ? api(API + '/' + set.id, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
        : api(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      p.then(function (res) { return res.json().then(function (b) { return { status: res.status, body: b }; }); })
        .then(function (r) {
          if (r.status === 403) { closeOverlay(); toast(memberMsg(r.body && r.body.message) || (r.body && r.body.error) || '403'); render(); return; }
          if (r.status !== 200 && r.status !== 201) { toast((r.body && r.body.error) || ('HTTP ' + r.status)); return; }
          toast(t().done_saved);
          closeOverlay();
          render();
        })
        .catch(function () { toast(t().err_net); });
    });
  }

  // ───────────────────────── 我的 page tabs (追加 3 ③) ─────────────────
  // Two sections on the renamed 我的 page: 我的提醒 (the original reminder
  // panels, wrapper-level hidden only — their inner logic untouched) and
  // 我的題材 (this asset's section). Default = 我的提醒; ?/#subjects deep
  // link (card panel 管理全部) opens the library directly.
  function showTab(name) {
    var secRem = document.getElementById('sec-reminders');
    var secSub = document.getElementById('sec-subjects');
    var tabRem = document.getElementById('tab-reminders');
    var tabSub = document.getElementById('tab-subjects');
    if (!secRem || !secSub) return;
    var subjects = name === 'subjects';
    secRem.hidden = subjects;
    secSub.hidden = !subjects;
    if (tabRem) { tabRem.setAttribute('aria-selected', subjects ? 'false' : 'true'); tabRem.classList.toggle('on', !subjects); }
    if (tabSub) { tabSub.setAttribute('aria-selected', subjects ? 'true' : 'false'); tabSub.classList.toggle('on', subjects); }
    if (subjects) render();
    try {
      var u = new URL(location.href);
      if (subjects) { u.hash = 'subjects'; history.replaceState(null, '', u); }
      else if (location.hash === '#subjects') { u.hash = ''; history.replaceState(null, '', u); }
    } catch (e) { /* history blocked */ }
  }
  function initMyTabs() {
    document.querySelectorAll('[data-my-tab]').forEach(function (b) {
      b.addEventListener('click', function (e) {
        e.preventDefault();
        showTab(b.getAttribute('data-my-tab'));
      });
    });
    var wantSubjects = /(^|&|#)subjects/.test(location.search + '&' + location.hash) || location.hash === '#subjects';
    showTab(wantSubjects ? 'subjects' : 'reminders');
  }

  // ───────────────────────── boot ─────────────────────────
  function boot() {
    initMyTabs();
    render();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  window.addEventListener('pageshow', function () { render(); });

  // Test / integration surface.
  window.ChaseLightsSubjectSetsLibrary = {
    render: render,
    showTab: showTab,
    openEditor: openEditor,
    openPicker: openPicker,
    state: function () {
      return JSON.parse(JSON.stringify(state, function (key, val) { return val === undefined ? null : val; }));
    },
    // pure helpers (unit tests)
    groupSets: groupSets,
    placeName: placeName,
    pickerEntries: pickerEntries,
    quotaLine: quotaLine,
    summaryOf: summaryOf,
    monthsLine: monthsLine,
    memberMsg: memberMsg,
  };
})();
