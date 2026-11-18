/* CL-APP-09 (owner ruling): 自訂題材 on OFFICIAL spots. Self-contained asset
   (custom-places.js / member-auth.js precedent): own tri-lingual pack, own
   CSS file, NO app.js edits — app.js render-expression pins stay valid.

   Surfaces (owner spec §1):
   - official card gains a ⋯ menu with 「＋ 加自訂題材」 (portal menu, same
     pattern as the private-card ⋯ — fixed position, flips up near the
     viewport bottom, closes on outside tap/scroll/resize);
   - the 題材 panel (place modal) gains a 「我的自訂題材」 section listing the
     member's sets in the SAME row anatomy as official subjects: 自訂 badge,
     8-day strip via the SAME v2-day classes, next window, months window;
   - fork semantics (owner spec §4): a set forked from an official template
     carries the 自訂 badge + a diff view against the snapshotted official
     values; thresholds beyond ±30% of the official value are WARNED (never
     blocked); 「重設回官方」 resets; when the official contract's revision
     moves past the fork's base_rev the row honestly shows
     「官方已更新可同步」 with a one-click sync;
   - caps (owner FINAL ruling, 收斂 2026-11-18): 5 per place (paid AND free —
     free additionally bounded by a 5-set TOTAL + 5-per-day add, fail-closed
     403 + gray upgrade card), owner unlimited;
   - duplicates ARE allowed (same template multiple times, duplicate names). */
(function () {
  'use strict';
  var API = '/api/v1/subject_sets';
  var CONTRACTS_URL = './apps/web-v2/opportunity-contracts.json';
  var LANGS = ['zh-TW', 'en', 'ja'];

  var T = {
    'zh-TW': {
      sec_title: '我的自訂題材', add_btn: '＋ 加自訂題材',
      badge: '自訂', stale_badge: '官方已更新可同步',
      quota_fmt: '此景點 {p}/{pc} 組', quota_owner: '此景點 {p} 組（無上限）',
      quota_free: '此景點 {p}/{pc} 組 · 全站 {t}/{tc} 組 · 每日新增 {d} 組',
      free_cap_note: '免費會員自訂題材全站總量 5 組、每日新增 5 組；升級 Premium 後每個景點 5 組、無總量上限。',
      login_note: '登入後可在此建立自訂題材', login_cta: '登入以繼續',
      months_all: '全年', months_fmt: '適用月份：{m}', next_win: '下一窗：',
      no_win: '今日無下一窗', fail_no_data: '評估資料尚未涵蓋', fail_month: '非適用月份', fail_wp: '時段待座標同步',
      day_ok: '符合', day_bad: '未符', hours_lbl: '符合時數',
      diff_title: '與官方模板差異', diff_none: '（自建條件，非官方模板 fork）',
      diff_official: '官方', diff_mine: '此組', diff_warn: '超出官方門檻 ±30%（僅提示，不阻擋）',
      reset_btn: '重設回官方', sync_btn: '同步官方更新', edit_btn: '✎ 編輯', del_btn: '🗑 刪除',
      ed_title: '加自訂題材', ed_title_edit: '編輯自訂題材', ed_name: '題材名稱', ed_name_ph: '例如：晨光斜射反高潮位',
      ed_fork: 'fork 官方模板（出發點）', ed_fork_none: '— 不 fork，自建 —',
      sem_cloud: '雲量', sem_fog: '霧', sem_rain: '雨',
      p_low: '低雲門檻（%）', p_mid: '中雲門檻（%）', p_high: '高雲門檻（%）', p_precip: '降水上限（mm/h）',
      p_vis: '能見度下限（km）', p_wind: '風速上限（m/s）', p_window: '時間窗', p_months: '適用月份',
      p_months_hint: '不選＝全年適用；選取後只有該月份會判定',
      wt_fixed: '固定時段', wt_bs: '日出前（每日動態）', wt_as: '日出後（每日動態）', wt_bd: '日落前（每日動態）', wt_ads: '日落後（每日動態）',
      win_off: '錨點偏移（分鐘，可負）', win_add2: '＋ 加第二段', win_rm: '移除此段', win_hint: '錨點型以當日實際日出／日落動態展開，冬天夏天不同',
      win_before: '{t} 前', win_from: '{t} 起',
      cc_prev: '摘要預覽：', cc_prev_none: '（未調任何參數）', ed_submit: '建立此題材組', ed_submit_edit: '儲存變更',
      warn_pct: '⚠ {m}：官方 {o} → 此組 {v}，超出 ±30%（已照存，不阻擋）',
      done1: '✓ 自訂題材已建立', done1_edit: '✓ 已更新',
      del_title: '刪除此自訂題材？', del_confirm: '🗑 刪除', del_cancel: '取消',
      cap_place: '此景點已達 5 組上限（現有 {p} 組）——刪除一組後即可再新增。',
      cap_free: '免費會員自訂題材全站總量 5 組（現有 {t} 組）——刪除一組或升級 Premium 後即可再新增。',
      cap_daily: '今日已新增 5 組（每日上限 5 組）——明日再新增即可。',
      reset_note: '✓ 已重設回官方門檻', sync_note: '✓ 已同步官方更新', close: '關閉',
    },
    en: {
      sec_title: 'My custom subjects', add_btn: '＋ Custom subject',
      badge: 'Custom', stale_badge: 'Official template updated — sync available',
      quota_fmt: 'Here {p}/{pc}', quota_owner: 'Here {p} (unlimited)',
      quota_free: 'Here {p}/{pc} · {t}/{tc} total · {d} new per day',
      free_cap_note: 'Free members hold 5 custom-subject sets in TOTAL and can add 5 per day; Premium unlocks 5 per place with no total cap.',
      login_note: 'Sign in to create custom subjects here', login_cta: 'Sign in to continue',
      months_all: 'All year', months_fmt: 'Months: {m}', next_win: 'Next window:',
      no_win: 'No next window today', fail_no_data: 'Evaluation data not yet covering', fail_month: 'Outside applicable months', fail_wp: 'Window pending place sync',
      day_ok: 'Meets', day_bad: 'Misses', hours_lbl: 'Qualifying hours',
      diff_title: 'Diff vs official template', diff_none: '(built from scratch — not a template fork)',
      diff_official: 'Official', diff_mine: 'This set', diff_warn: 'Beyond ±30% of the official threshold (advisory only)',
      reset_btn: 'Reset to official', sync_btn: 'Sync official update', edit_btn: '✎ Edit', del_btn: '🗑 Delete',
      ed_title: 'Add custom subject', ed_title_edit: 'Edit custom subject', ed_name: 'Subject name', ed_name_ph: 'e.g. first-light on the reef',
      ed_fork: 'Fork an official template (starting point)', ed_fork_none: '— no fork, build fresh —',
      sem_cloud: 'Cloud', sem_fog: 'Fog', sem_rain: 'Rain',
      p_low: 'Low-cloud cap (%)', p_mid: 'Mid-cloud cap (%)', p_high: 'High-cloud cap (%)', p_precip: 'Precip cap (mm/h)',
      p_vis: 'Visibility min (km)', p_wind: 'Wind cap (m/s)', p_window: 'Time window', p_months: 'Applicable months',
      p_months_hint: 'None = all year; when set, only those months are judged',
      wt_fixed: 'Fixed span', wt_bs: 'Before sunrise (daily dynamic)', wt_as: 'After sunrise (daily dynamic)', wt_bd: 'Before sunset (daily dynamic)', wt_ads: 'After sunset (daily dynamic)',
      win_off: 'Anchor offset (minutes, may be negative)', win_add2: '＋ Add a second span', win_rm: 'Remove this span', win_hint: 'Anchor spans expand with each day\u2019s REAL sunrise/sunset — winter and summer differ',
      win_before: 'before {t}', win_from: 'from {t}',
      cc_prev: 'Summary:', cc_prev_none: '(no parameters set)', ed_submit: 'Create this set', ed_submit_edit: 'Save changes',
      warn_pct: '⚠ {m}: official {o} → set {v}, beyond ±30% (saved anyway)',
      done1: '✓ Custom subject created', done1_edit: '✓ Updated',
      del_title: 'Delete this custom subject?', del_confirm: '🗑 Delete', del_cancel: 'Cancel',
      cap_place: 'This place is at its 5-set cap ({p}) — delete one to add more.',
      cap_free: 'Free members hold 5 sets in TOTAL ({t} now) — delete one or upgrade Premium to add more.',
      cap_daily: 'You added 5 sets today (daily cap 5) — add more tomorrow.',
      reset_note: '✓ Reset to official thresholds', sync_note: '✓ Official update synced', close: 'Close',
    },
    ja: {
      sec_title: '自作題材', add_btn: '＋ 自作題材を追加',
      badge: '自作', stale_badge: '公式テンプレ更新あり・同期可能',
      quota_fmt: 'ここ {p}/{pc} 件', quota_owner: 'ここ {p} 件（無制限）',
      quota_free: 'ここ {p}/{pc} 件 · 合計 {t}/{tc} 件 · 1日{d}件まで追加',
      free_cap_note: '無料會員は自作題材の合計5件・1日5件まで追加可能；Premiumなら1か所5件・合計上限なし。',
      login_note: 'ログインすると自作題材を作成できます', login_cta: 'ログインして続行',
      months_all: '通年', months_fmt: '適用月：{m}', next_win: '次は：',
      no_win: '本日これ以上なし', fail_no_data: '判定データはまだありません', fail_month: '適用月外', fail_wp: '時間帯は座標同期待ち',
      day_ok: '適合', day_bad: '未達成', hours_lbl: '適合時間数',
      diff_title: '公式テンプレとの差分', diff_none: '（自作条件・フォークなし）',
      diff_official: '公式', diff_mine: 'この組', diff_warn: '公式しきい値の±30%外（保存は可能）',
      reset_btn: '公式へリセット', sync_btn: '公式更新を同期', edit_btn: '✎ 編集', del_btn: '🗑 削除',
      ed_title: '自作題材を追加', ed_title_edit: '自作題材を編集', ed_name: '題材名', ed_name_ph: '例：朝焼けの反射',
      ed_fork: '公式テンプレをフォーク（出発点）', ed_fork_none: '— フォークしない —',
      sem_cloud: '雲量', sem_fog: '霧', sem_rain: '雨',
      p_low: '下層雲しきい値（%）', p_mid: '中層雲しきい値（%）', p_high: '上層雲しきい値（%）', p_precip: '降水上限（mm/h）',
      p_vis: '視程下限（km）', p_wind: '風速上限（m/s）', p_window: '時間帯', p_months: '適用月',
      p_months_hint: '未選択＝通年；選択するとその月のみ判定',
      wt_fixed: '固定時間帯', wt_bs: '日の出前（毎日動的）', wt_as: '日の出後（毎日動的）', wt_bd: '日の入前（毎日動的）', wt_ads: '日の入後（毎日動的）',
      win_off: 'アンカーオフセット（分・負可）', win_add2: '＋ 2つ目を追加', win_rm: 'この枠を削除', win_hint: 'アンカーは当日の実際の日の出入りから毎日展開（季節で変わる）',
      win_before: '{t} まで', win_from: '{t} から',
      cc_prev: 'サマリー：', cc_prev_none: '（未設定）', ed_submit: 'この題材を作成', ed_submit_edit: '変更を保存',
      warn_pct: '⚠ {m}：公式 {o} → この組 {v}、±30%外（保存可）',
      done1: '✓ 自作題材を作成しました', done1_edit: '✓ 保存しました',
      del_title: 'この自作題材を削除？', del_confirm: '🗑 削除', del_cancel: 'キャンセル',
      cap_place: 'このスポットは上限5件に達しました（{p}件）——削除後に追加できます。',
      cap_free: '無料會員は自作題材の合計上限5件（現在{t}件）です。削除するかPremiumにアップグレードすると追加できます。',
      cap_daily: '本日すでに5件追加しました（1日の上限5件）——明日以降に追加できます。',
      reset_note: '✓ 公式しきい値へリセットしました', sync_note: '✓ 公式更新を同期しました', close: '閉じる',
    },
  };

  var state = { member: null, contracts: null, contractsPromise: null, panelSig: '', evalCache: {}, dirty: false };
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
  function api(path, opts) {
    opts = opts || {};
    opts.credentials = 'same-origin';
    opts.cache = 'no-store';
    if (typeof window.__clssFetch === 'function') return Promise.resolve(window.__clssFetch(path, opts));
    return fetch(path, opts);
  }
  function toast(msg) {
    if (!els.toast) {
      els.toast = document.createElement('div'); els.toast.className = 'cl-cp-toast'; els.toast.setAttribute('role', 'status');
      els.toast.style.zIndex = '1100'; /* CL-APP-09b: must paint above the place modal (z 1000) */
      document.body.appendChild(els.toast);
    }
    els.toast.textContent = typeof msg === 'string' ? msg : (msg && msg[currentLang()]) || '';
    els.toast.classList.add('show');
    clearTimeout(toast._tm);
    toast._tm = setTimeout(function () { els.toast.classList.remove('show'); }, 6000);
  }
  function memberMsg(m) {
    if (!m) return '';
    if (typeof m === 'string') return m;
    return m[currentLang()] || m['zh-TW'] || '';
  }

  // ───────────────────────── official contracts (fork base) ─────────────
  function loadContracts() {
    if (state.contracts) return Promise.resolve(state.contracts);
    if (state.contractsPromise) return state.contractsPromise;
    state.contractsPromise = fetch(CONTRACTS_URL, { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { state.contracts = j && j.opportunities ? j : null; state.contractsPromise = null; return state.contracts; })
      .catch(function () { state.contractsPromise = null; return null; });
    return state.contractsPromise;
  }
  function contractFor(oppId) { return state.contracts && state.contracts.opportunities ? state.contracts.opportunities[oppId] : null; }
  function contractsForPlace(placeId) {
    if (!state.contracts || !state.contracts.opportunities) return [];
    return Object.keys(state.contracts.opportunities)
      .map(function (k) { return state.contracts.opportunities[k]; })
      .filter(function (c) { return c.place_id === placeId; });
  }
  function contractName(c) {
    var n = c && c.name_i18n;
    if (!n) return c && c.opportunity_id || '';
    return n[currentLang()] || n['zh-TW'] || c.opportunity_id;
  }

  // Mappable weather axes: only constraints whose DIRECTION matches the cc
  // schema (clouds/precip/wind caps, visibility floor) are copied into a
  // fork; inverted (gte-cloud) or computed-window conditions stay unmapped
  // and remain visible in the diff view as honest gaps.
  function mapOfficialToCc(contract) {
    var cc = {};
    (contract && contract.conditions || []).forEach(function (cond) {
      var th = cond.threshold;
      if (typeof th !== 'number' || th == null) return;
      if (cond.metric === 'cloud_cover_low' && (cond.operator === 'lte' || cond.operator === 'lt')) cc.cloud_low_max = th;
      else if (cond.metric === 'cloud_cover_mid' && (cond.operator === 'lte' || cond.operator === 'lt')) cc.cloud_mid_max = th;
      else if (cond.metric === 'cloud_cover_mid_and_high' && (cond.operator === 'lte' || cond.operator === 'lt')) { cc.cloud_mid_max = th; cc.cloud_high_max = th; }
      else if (cond.metric === 'cloud_cover_total' && (cond.operator === 'lte' || cond.operator === 'lt')) { cc.cloud_low_max = th; cc.cloud_mid_max = th; cc.cloud_high_max = th; }
      else if (cond.metric === 'precipitation' && (cond.operator === 'lte' || cond.operator === 'lt')) cc.precip_max_mmh = th;
      else if (cond.metric === 'visibility' && cond.operator === 'gte') cc.visibility_min_km = th;
      else if (cond.metric === 'wind_speed_10m' && (cond.operator === 'lte' || cond.operator === 'lt')) cc.wind_max_ms = th;
    });
    return cc;
  }
  var CC_LABELS = {
    cloud_low_max: 'cloud_low', cloud_mid_max: 'cloud_mid', cloud_high_max: 'cloud_high',
    precip_max_mmh: 'precip_max_mmh', visibility_min_km: 'visibility_min_km', wind_max_ms: 'wind_max_ms',
  };
  function diffRows(cc, baseCc) {
    var rows = [];
    if (!baseCc || !Object.keys(baseCc).length) return rows;
    Object.keys(CC_LABELS).forEach(function (k) {
      var mine = cc[k], base = baseCc[k];
      if (typeof base !== 'number') return;
      var pct = (typeof mine === 'number' && base !== 0) ? Math.round(Math.abs(mine - base) / Math.abs(base) * 100) : null;
      rows.push({ metric: k, official: base, mine: (typeof mine === 'number' ? mine : '—'), pct: pct, warn: pct !== null && pct > 30 });
    });
    return rows;
  }

  // ───────────────────────── shared ⋯ menu (official cards) ─────────────
  function menu() {
    if (els.menu) return els.menu;
    var m = document.createElement('div');
    m.className = 'cl-cp-menu cl-ss-menu';
    m.setAttribute('role', 'menu');
    document.body.appendChild(m);
    m.addEventListener('click', function (e) {
      var it = e.target.closest('[data-ss-menu-item]');
      if (!it) return;
      e.stopPropagation();
      closeMenu();
      var pid = m._placeId;
      if (it.dataset.ssMenuItem === 'add' && pid) startAdd(pid);
    });
    els.menu = m;
    return m;
  }
  function closeMenu() {
    if (els.menu) { els.menu.classList.remove('open'); els.menu.style.visibility = ''; }
    document.querySelectorAll('.cl-ss-more[aria-expanded="true"]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
  }
  function positionMenu(m, trigger) {
    var r = trigger.getBoundingClientRect();
    m.style.visibility = 'hidden';
    m.classList.add('open');
    var mw = m.offsetWidth, mh = m.offsetHeight, margin = 8, gap = 6;
    var top = r.bottom + gap, left = Math.min(r.left, window.innerWidth - mw - margin);
    if (top + mh > window.innerHeight - margin && r.top - gap - mh >= margin) top = r.top - gap - mh;
    top = Math.max(margin, Math.min(top, Math.max(margin, window.innerHeight - margin - mh)));
    left = Math.max(margin, Math.min(left, Math.max(margin, window.innerWidth - margin - mw)));
    m.style.top = top + 'px'; m.style.left = left + 'px';
    m.style.visibility = '';
  }
  function openCardMenu(trigger, placeId) {
    var m = menu();
    m._placeId = placeId;
    m.innerHTML = '<button type="button" role="menuitem" data-ss-menu-item="add">' + esc(t().add_btn) + '</button>';
    positionMenu(m, trigger);
    trigger.setAttribute('aria-expanded', 'true');
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.cl-ss-more');
    if (btn) {
      e.stopPropagation();
      // CL-APP-09b: the homepage cards carry data-place-id (NOT data-spot-id)
      // and decorateCards never stamps the button, so the old lookup always
      // resolved pid='' and the ＋加自訂題材 item was a silent no-op. Read
      // whichever id attribute the card ancestor actually carries.
      var host = btn.closest('[data-spot-id]') || btn.closest('[data-place-id]');
      var pid = host ? (host.dataset.spotId || host.dataset.placeId || '') : (btn.dataset.placeId || '');
      if (els.menu && els.menu.classList.contains('open') && btn.getAttribute('aria-expanded') === 'true') closeMenu();
      else openCardMenu(btn, pid);
      return;
    }
    if (!e.target.closest('.cl-ss-menu')) closeMenu();
  }, true);
  document.addEventListener('scroll', function () { if (els.menu && els.menu.classList.contains('open')) closeMenu(); }, true);
  window.addEventListener('resize', function () { if (els.menu && els.menu.classList.contains('open')) closeMenu(); });

  // ───────────────────────── overlay machinery ─────────────────────────
  function ensureOverlay() {
    if (els.overlay) return;
    els.overlay = document.createElement('div');
    // CL-APP-09b marker: only THIS asset's sheet gets the keyboard-aware fit
    // (custom-places.js owns the same shared classes — leave its sheet alone).
    els.overlay.className = 'cl-cp-overlay cl-ss-overlay';
    els.overlay.innerHTML = '<div class="cl-cp-modal"></div>';
    els.overlay.addEventListener('click', function (e) { if (e.target === els.overlay) closeOverlay(); });
    document.body.appendChild(els.overlay);
  }
  // CL-APP-09b (owner iPhone repro): the iOS keyboard shrinks the VISUAL
  // viewport while 100vh (the ≤700px sheet's min/max-height) keeps measuring
  // the LAYOUT viewport. The editor (~842px tall at 390) fits inside 100vh,
  // so the sheet never scrolls internally — with the keyboard up everything
  // below the visible band (條件表單 / 適用月份 / 送出鈕) was unreachable and
  // the user was stuck on the name field. Fit the OPEN sheet to the visual
  // viewport on every resize/scroll: the band becomes exactly the visible
  // region, the content overflows it, and internal scrolling reaches the
  // submit button. No visualViewport (old engines) → the CSS sheet stands.
  function fitOverlay() {
    if (!els.overlay || !els.overlay.classList.contains('open')) return;
    var vv = window.visualViewport;
    if (!vv || typeof vv.height !== 'number') return;
    var modal = els.overlay.querySelector('.cl-cp-modal');
    var full = Math.round(window.innerHeight);
    var h = Math.round(vv.height);
    var off = Math.max(0, Math.round(vv.offsetTop || 0));
    if (h >= full && off === 0) {
      // keyboard closed (and desktop): hand the sheet back to the CSS rules
      els.overlay.style.top = '';
      els.overlay.style.height = '';
      if (modal) { modal.style.minHeight = ''; modal.style.maxHeight = ''; }
      return;
    }
    els.overlay.style.top = off + 'px';
    els.overlay.style.height = h + 'px';
    if (modal) { modal.style.minHeight = h + 'px'; modal.style.maxHeight = h + 'px'; }
    var ae = document.activeElement;
    if (ae && els.overlay.contains(ae)) {
      try { ae.scrollIntoView({ block: 'nearest' }); } catch (e) { /* old engine */ }
    }
  }
  function attachViewportFit() {
    var vv = window.visualViewport;
    if (!vv || els._vvFit) return;
    els._vvFit = function () { fitOverlay(); };
    try {
      vv.addEventListener('resize', els._vvFit);
      vv.addEventListener('scroll', els._vvFit);
    } catch (e) { els._vvFit = null; }
  }
  function detachViewportFit() {
    var vv = window.visualViewport;
    if (vv && els._vvFit) {
      try {
        vv.removeEventListener('resize', els._vvFit);
        vv.removeEventListener('scroll', els._vvFit);
      } catch (e) { /* already gone */ }
    }
    els._vvFit = null;
    if (els.overlay) {
      els.overlay.style.top = '';
      els.overlay.style.height = '';
      var modal = els.overlay.querySelector('.cl-cp-modal');
      if (modal) { modal.style.minHeight = ''; modal.style.maxHeight = ''; }
    }
  }
  function openOverlay(html) {
    ensureOverlay();
    els.overlay.querySelector('.cl-cp-modal').innerHTML = html;
    els.overlay.classList.add('open');
    document.body.classList.add('cl-cp-lock');
    attachViewportFit();
    fitOverlay();
    var first = els.overlay.querySelector('input, select, button.cl-cp-submit');
    if (first) { try { first.focus({ preventScroll: true }); } catch (e) { try { first.focus(); } catch (e2) { } } }
  }
  function closeOverlay() {
    if (!els.overlay) return;
    els.overlay.classList.remove('open');
    document.body.classList.remove('cl-cp-lock');
    detachViewportFit();
  }
  function wireClose() {
    els.overlay.querySelectorAll('[data-ss-close]').forEach(function (b) {
      b.addEventListener('click', closeOverlay);
    });
  }

  // ───────────────────────── cc editor (fork aware) ─────────────────────
  // Five parameter groups = CL-UI-99 schema; semantic dropdowns map to the
  // same concrete numbers the worker re-validates (cloud/fog/rain + window +
  // months multi-select + advanced numeric inputs).
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
  function monthsHtml(selected) {
    var sel = Array.isArray(selected) ? selected : [];
    var out = '';
    for (var m = 1; m <= 12; m++) {
      out += '<label class="cl-cp-mo"><input type="checkbox" id="cl-ss-m' + m + '" value="' + m + '"' +
        (sel.indexOf(m) >= 0 ? ' checked' : '') + '>' + m + '月</label>';
    }
    return out;
  }
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
  // ─── CL-APP-09 patch-2: ANCHOR + MULTI-SEGMENT time windows ───
  // Segments: fixed (start–end) | before_sunrise/after_sunrise/before_sunset/
  // after_sunset (offset_minutes). ≤2 segments; ANY segment passes an hour.
  // The ENGINE (worker solar.js) expands anchors with the place's REAL sun
  // times per day — 冬天/夏至 give different windows by design.
  var WTYPES = ['fixed', 'before_sunrise', 'after_sunrise', 'before_sunset', 'after_sunset'];
  function wtLabel(type) {
    return { fixed: t().wt_fixed, before_sunrise: t().wt_bs, after_sunrise: t().wt_as, before_sunset: t().wt_bd, after_sunset: t().wt_ads }[type] || '';
  }
  function windowSegsOf(cc) {
    if (cc && Array.isArray(cc.windows) && cc.windows.length) return cc.windows;
    if (cc && cc.window_start && cc.window_end) return [{ type: 'fixed', start: cc.window_start, end: cc.window_end }];
    return [{ type: 'fixed', start: '', end: '' }];
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
  // Editor: segments state lives in-memory so type switches can re-render the
  // fields without losing the other segment's values.
  function renderWinArea() {
    var host = els.overlay.querySelector('#cl-ss-win-area');
    if (!host) return;
    host.innerHTML = winAreaHtml();
    wireWinArea();
  }
  function winAreaHtml() {
    var out = '';
    for (var i = 0; i < winState.length; i++) out += winSegHtml(i, winState[i]);
    out += (winState.length < 2 ? '<button type="button" class="cl-ss-act" id="cl-ss-win-add">' + esc(t().win_add2) + '</button>' : '') +
      '<div class="hint">' + esc(t().win_hint) + '</div>';
    return out;
  }
  function winSegHtml(i, seg) {
    var idp = 'cl-ss-ws' + i;
    var typeSel = '<select id="' + idp + '-type" class="inp" style="flex:0 0 auto">' +
      WTYPES.map(function (w) { return '<option value="' + w + '"' + (w === seg.type ? ' selected' : '') + '>' + esc(wtLabel(w)) + '</option>'; }).join('') +
      '</select>';
    var fields;
    if (seg.type === 'fixed') {
      fields = '<input id="' + idp + '-start" value="' + esc(seg.start || '') + '" placeholder="04:30" style="flex:1">' +
        '<span style="color:var(--cl-text-3)">–</span>' +
        '<input id="' + idp + '-end" value="' + esc(seg.end || '') + '" placeholder="07:00" style="flex:1">';
    } else {
      var res = (winResolved && winResolved[i] && winResolved[i].start) ? ' · ' + relLabel(winResolvedDay) + ' ' +
        (seg.type.indexOf('before_') === 0
          ? t().win_before.replace('{t}', winResolved[i].end)
          : t().win_from.replace('{t}', winResolved[i].start)) : '';
      fields = '<input id="' + idp + '-off" inputmode="numeric" value="' + esc(seg.offset_minutes != null ? String(seg.offset_minutes) : '') + '" placeholder="0" style="flex:0 0 90px">' +
        '<span class="hint" style="flex:1">' + esc(t().win_off) + esc(res) + '</span>';
    }
    return '<div class="cl-ss-winseg" data-ss-ws="' + i + '" style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">' + typeSel + fields +
      (i === 1 ? '<button type="button" class="cl-ss-act cl-ss-act-del" id="cl-ss-win-rm" aria-label="' + esc(t().win_rm) + '">✕</button>' : '') +
      '</div>';
  }
  function readWinState() {
    // pull current input values into winState (survives partial re-renders)
    var segs = [];
    for (var i = 0; i < 2; i++) {
      var typeEl = els.overlay.querySelector('#cl-ss-ws' + i + '-type');
      if (!typeEl) { if (winState[i]) segs.push(winState[i]); continue; }
      var type = typeEl.value;
      if (type === 'fixed') {
        var s = (els.overlay.querySelector('#cl-ss-ws' + i + '-start') || {}).value || '';
        var e = (els.overlay.querySelector('#cl-ss-ws' + i + '-end') || {}).value || '';
        segs.push({ type: 'fixed', start: s.trim(), end: e.trim() });
      } else {
        var offEl = els.overlay.querySelector('#cl-ss-ws' + i + '-off');
        var off = offEl && offEl.value.trim() !== '' ? parseInt(offEl.value, 10) : 0;
        segs.push({ type: type, offset_minutes: isFinite(off) ? off : 0 });
      }
    }
    return segs;
  }
  function wireWinArea() {
    var addBtn = els.overlay.querySelector('#cl-ss-win-add');
    if (addBtn) addBtn.addEventListener('click', function () {
      winState = readWinState();
      if (winState.length < 2) winState.push({ type: 'fixed', start: '', end: '' });
      renderWinArea();
      winRefreshPrev();
    });
    var rmBtn = els.overlay.querySelector('#cl-ss-win-rm');
    if (rmBtn) rmBtn.addEventListener('click', function () {
      winState = readWinState().slice(0, 1);
      renderWinArea();
      winRefreshPrev();
    });
    [0, 1].forEach(function (i) {
      var typeEl = els.overlay.querySelector('#cl-ss-ws' + i + '-type');
      if (!typeEl) return;
      typeEl.addEventListener('change', function () {
        winState = readWinState();
        winState[i] = typeEl.value === 'fixed' ? { type: 'fixed', start: '', end: '' } : { type: typeEl.value, offset_minutes: 0 };
        renderWinArea();
        winRefreshPrev();
      });
      ['start', 'end', 'off'].forEach(function (f) {
        var el = els.overlay.querySelector('#cl-ss-ws' + i + '-' + f);
        if (el) el.addEventListener('change', winRefreshPrev);
      });
    });
  }
  var winState = [{ type: 'fixed', start: '', end: '' }];
  var winResolved = null, winResolvedDay = null;
  // the win editor lives at MODULE scope but the preview refresh is editor-local;
  // the editor registers its refreshPrev here (patch-2 fix: a bare refreshPrev
  // reference in wireWinArea threw at attach and killed every later wiring)
  var winPrevHook = null;
  function winRefreshPrev() { if (winPrevHook) winPrevHook(); }

  function currentSemantic(axis, cc) {
    var m = CC_SEMANTIC[axis]; if (!m) return 'any';
    var val = cc && cc[m.key];
    if (val == null) return 'any';
    var entries = Object.keys(m.values);
    for (var i = 0; i < entries.length; i++) if (entries[i] !== 'any' && m.values[entries[i]] === val) return entries[i];
    return 'any';
  }
  function ccSummary(cc, lang) {
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
  function readCc() {
    var num = function (id) { var v = els.overlay.querySelector('#' + id).value.trim(); if (!v) return null; var n = Number(v); return isFinite(n) ? n : null; };
    var out = {};
    ['cl-ss-cc-low:cloud_low_max', 'cl-ss-cc-mid:cloud_mid_max', 'cl-ss-cc-high:cloud_high_max', 'cl-ss-cc-precip:precip_max_mmh', 'cl-ss-cc-vis:visibility_min_km', 'cl-ss-cc-wind:wind_max_ms'].forEach(function (pair) {
      var parts = pair.split(':'); var n = num(parts[0]); if (n != null) out[parts[1]] = n;
    });
    // window segments → cc schema. A single filled fixed segment keeps the
    // legacy flat fields (backward-compatible reads everywhere); anything
    // anchor-shaped or a second segment rides the windows array (≤2, ANY
    // segment passes an hour; the worker re-validates).
    var segs = readWinState().filter(function (s) {
      return s.type === 'fixed' ? (s.start && s.end) : true;
    });
    if (segs.length === 1 && segs[0].type === 'fixed' && /^\d\d:\d\d$/.test(segs[0].start) && /^\d\d:\d\d$/.test(segs[0].end)) {
      out.window_start = segs[0].start; out.window_end = segs[0].end;
    } else if (segs.length) {
      out.windows = segs.map(function (s) {
        return s.type === 'fixed' ? { type: 'fixed', start: s.start, end: s.end } : { type: s.type, offset_minutes: s.offset_minutes || 0 };
      });
    }
    var monthsWrap = els.overlay.querySelector('#cl-ss-cc-months');
    if (monthsWrap) {
      var months = [].slice.call(monthsWrap.querySelectorAll('input[type="checkbox"]:checked'))
        .map(function (b) { return Number(b.value); }).filter(function (n) { return n >= 1 && n <= 12; });
      if (months.length) out.months = months.sort(function (a, b) { return a - b; });
    }
    return out;
  }
  function fmtNum(v) {
    if (typeof v !== 'number') return '—';
    return (Math.round(v * 100) / 100).toString();
  }

  // The editor. mode: {placeId, set?} — set present = edit mode.
  function editorModal(mode) {
    var set = mode.set || {};
    var cc = Object.assign({}, set.conditions || {});
    var baseCc = Object.assign({}, set.baseConditions || {});
    var templateId = set.templateId || '';
    var lang = currentLang();
    // segment state for the window area (anchor + multi-segment editor)
    winState = windowSegsOf(cc).slice(0, 2);
    winResolved = (mode.ev && Array.isArray(mode.ev.windowResolved)) ? mode.ev.windowResolved : null;
    winResolvedDay = (winResolved && mode.ev && mode.ev.window) ? mode.ev.window.local_date : null;
    loadContracts().then(function () {
      var opts = contractsForPlace(mode.placeId).map(function (c) {
        return '<option value="' + esc(c.opportunity_id) + '"' + (c.opportunity_id === templateId ? ' selected' : '') + '>' + esc(contractName(c)) + '</option>';
      }).join('');
      var semSel = function (axis, label) {
        var m = CC_SEMANTIC[axis];
        var o = m.options[lang] || m.options['zh-TW'];
        var cur = currentSemantic(axis, cc);
        return '<div class="cl-cp-ccp wide"><label>' + esc(label) + '</label>' +
          '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">' +
          '<select id="cl-ss-sem-' + axis + '" class="cl-cp-sem-select">' +
          o.map(function (x) { return '<option value="' + x[0] + '"' + (x[0] === cur ? ' selected' : '') + '>' + esc(x[1]) + '</option>'; }).join('') +
          '</select><span class="cl-cp-sem-map" id="cl-ss-sem-map-' + axis + '">→ ' + esc(semanticMappedLabel(axis, cur)) + '</span></div></div>';
      };
      function v(k) { return cc[k] == null ? '' : String(cc[k]); }
      openOverlay(
        '<div class="cl-cp-m-head"><div><div class="name">' + esc(mode.set ? t().ed_title_edit : t().ed_title) + '</div>' +
        '<div class="sub">' + esc(ccSummary(cc, lang) || t().cc_prev_none) + '</div></div>' +
        '<button type="button" class="close" data-ss-close aria-label="' + esc(t().close) + '">✕</button></div>' +
        '<div class="cl-cp-fld"><label>' + esc(t().ed_name) + '</label>' +
        '<input id="cl-ss-name" class="inp" maxlength="60" value="' + esc(set.name || '') + '" placeholder="' + esc(t().ed_name_ph) + '"></div>' +
        '<div class="cl-cp-fld"><label>' + esc(t().ed_fork) + '</label>' +
        '<select id="cl-ss-fork" class="inp"><option value="">' + esc(t().ed_fork_none) + '</option>' + opts + '</select></div>' +
        '<div class="cl-cp-cc-params">' +
        semSel('cloud', t().sem_cloud) +
        semSel('fog', t().sem_fog) +
        semSel('rain', t().sem_rain) +
        '<div class="cl-cp-ccp wide"><label>' + esc(t().p_window) + '</label>' +
        '<div id="cl-ss-win-area"></div>' +
        '</div>' +
        '<div class="cl-cp-ccp wide"><label>' + esc(t().p_months) + '</label>' +
        '<div class="cl-cp-cc-months" id="cl-ss-cc-months">' + monthsHtml(set.months) + '</div>' +
        '<div class="hint">' + esc(t().p_months_hint) + '</div></div>' +
        '</div>' +
        '<details class="cl-cp-cc-advanced"><summary>⋯</summary>' +
        '<div class="cl-cp-cc-params" style="margin-top:8px">' +
        '<div class="cl-cp-ccp"><label>' + esc(t().p_low) + '</label><input id="cl-ss-cc-low" inputmode="decimal" value="' + esc(v('cloud_low_max')) + '"></div>' +
        '<div class="cl-cp-ccp"><label>' + esc(t().p_mid) + '</label><input id="cl-ss-cc-mid" inputmode="decimal" value="' + esc(v('cloud_mid_max')) + '"></div>' +
        '<div class="cl-cp-ccp"><label>' + esc(t().p_high) + '</label><input id="cl-ss-cc-high" inputmode="decimal" value="' + esc(v('cloud_high_max')) + '"></div>' +
        '<div class="cl-cp-ccp"><label>' + esc(t().p_precip) + '</label><input id="cl-ss-cc-precip" inputmode="decimal" value="' + esc(v('precip_max_mmh')) + '"></div>' +
        '<div class="cl-cp-ccp"><label>' + esc(t().p_vis) + '</label><input id="cl-ss-cc-vis" inputmode="decimal" value="' + esc(v('visibility_min_km')) + '"></div>' +
        '<div class="cl-cp-ccp"><label>' + esc(t().p_wind) + '</label><input id="cl-ss-cc-wind" inputmode="decimal" value="' + esc(v('wind_max_ms')) + '"></div>' +
        '</div></details>' +
        '<div class="cl-cp-cc-preview"><span style="color:var(--cl-text-3)">' + esc(t().cc_prev) + '</span><span class="k" id="cl-ss-cc-prev">' + esc(ccSummary(cc, lang) || t().cc_prev_none) + '</span></div>' +
        '<div class="cl-ss-warn" id="cl-ss-warn" role="status" aria-live="polite"></div>' +
        '<button type="button" class="cl-cp-submit ready" id="cl-ss-submit" style="cursor:pointer">' + esc(mode.set ? t().ed_submit_edit : t().ed_submit) + '</button>');
      wireClose();
      winPrevHook = refreshPrev; // patch-2: the win editor's preview hook
      renderWinArea();
      var nameInput = els.overlay.querySelector('#cl-ss-name');
      if (nameInput) nameInput.focus({ preventScroll: true });
      var forkSel = els.overlay.querySelector('#cl-ss-fork');
      function syncSemantic() {
        ['cloud', 'fog', 'rain'].forEach(function (axis) {
          var sel = els.overlay.querySelector('#cl-ss-sem-' + axis);
          if (!sel) return;
          var val = sel.value;
          els.overlay.querySelector('#cl-ss-sem-map-' + axis).textContent = '→ ' + semanticMappedLabel(axis, val);
          var target = { cloud: '#cl-ss-cc-low', fog: '#cl-ss-cc-vis', rain: '#cl-ss-cc-precip' }[axis];
          var inp = els.overlay.querySelector(target);
          if (!inp) return;
          var mapped = semanticValue(axis, val);
          inp.value = mapped == null ? '' : String(mapped);
        });
        refreshPrev();
      }
      function refreshPrev() {
        els.overlay.querySelector('#cl-ss-cc-prev').textContent = ccSummary(readCc(), currentLang()) || t().cc_prev_none;
        refreshWarn();
      }
      function refreshWarn() {
        var warnHost = els.overlay.querySelector('#cl-ss-warn');
        if (!warnHost) return;
        var base = liveBaseCc();
        var rows = diffRows(readCc(), base);
        var out = rows.filter(function (r) { return r.warn; }).map(function (r) {
          return t().warn_pct.replace('{m}', r.metric).replace('{o}', fmtNum(r.official)).replace('{v}', fmtNum(r.mine));
        });
        warnHost.innerHTML = out.map(function (s) { return '<div class="cl-ss-warn-line">' + esc(s) + '</div>'; }).join('');
        warnHost.style.display = out.length ? '' : 'none';
      }
      function liveBaseCc() {
        var sel = els.overlay.querySelector('#cl-ss-fork');
        var c = sel && sel.value ? contractFor(sel.value) : (templateId ? contractFor(templateId) : null);
        return c ? mapOfficialToCc(c) : baseCc;
      }
      ['cloud', 'fog', 'rain'].forEach(function (axis) {
        var sel = els.overlay.querySelector('#cl-ss-sem-' + axis);
        if (sel) sel.addEventListener('change', syncSemantic);
      });
      els.overlay.querySelectorAll('.cl-cp-cc-advanced input').forEach(function (inp) {
        inp.addEventListener('change', refreshPrev);
      });
      var monthsWrap = els.overlay.querySelector('#cl-ss-cc-months');
      if (monthsWrap) monthsWrap.querySelectorAll('input[type="checkbox"]').forEach(function (b) {
        b.addEventListener('change', refreshPrev);
      });
      if (forkSel) forkSel.addEventListener('change', function () {
        var c = forkSel.value ? contractFor(forkSel.value) : null;
        if (!c) return;
        var mapped = mapOfficialToCc(c);
        var fill = { cloud_low_max: '#cl-ss-cc-low', cloud_mid_max: '#cl-ss-cc-mid', cloud_high_max: '#cl-ss-cc-high', precip_max_mmh: '#cl-ss-cc-precip', visibility_min_km: '#cl-ss-cc-vis', wind_max_ms: '#cl-ss-cc-wind' };
        Object.keys(fill).forEach(function (k) {
          var inp = els.overlay.querySelector(fill[k]);
          if (inp) inp.value = mapped[k] != null ? String(mapped[k]) : '';
        });
        refreshPrev();
      });
      els.overlay.querySelector('#cl-ss-submit').addEventListener('click', function () {
        var name = (els.overlay.querySelector('#cl-ss-name').value || '').trim();
        if (!name) { toast(t().ed_name_ph); return; }
        var ccOut = readCc();
        var months = ccOut.months || []; delete ccOut.months;
        var forkVal = els.overlay.querySelector('#cl-ss-fork').value;
        var forkC = forkVal ? contractFor(forkVal) : null;
        var baseCcOut = forkC ? mapOfficialToCc(forkC) : (set.templateId ? baseCc : {});
        var body = {
          place_id: mode.placeId, name: name,
          template_id: forkVal || set.templateId || null,
          base_rev: forkC ? (forkC.revision || null) : (set.baseRev != null ? set.baseRev : null),
          base_conditions: baseCcOut,
          conditions: ccOut, months: months,
        };
        var p = mode.set
          ? api(API + '/' + mode.set.id, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
          : api(API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        p.then(function (res) { return res.json().then(function (b) { return { status: res.status, body: b }; }); })
          .then(function (r) {
            if (r.status === 403) {
              closeOverlay();
              var capMsg = memberMsg(r.body && r.body.message);
              if (capMsg && r.body && r.body.counts) {
                capMsg = capMsg.replace('{place}', String(r.body.counts.place)).replace('{total}', String(r.body.counts.total));
              }
              toast(capMsg || (r.body && r.body.error) || '403');
              renderPanels(); return;
            }
            if (r.status !== 200 && r.status !== 201) { toast((r.body && r.body.error) || ('HTTP ' + r.status)); return; }
            var warns = (r.body && r.body.warnings) || [];
            var warnTxt = warns.map(function (w) {
              return t().warn_pct.replace('{m}', w.metric).replace('{o}', fmtNum(w.official)).replace('{v}', fmtNum(w.value));
            });
            toast((mode.set ? t().done1_edit : t().done1) + (warnTxt.length ? '\n' + warnTxt.join('\n') : ''));
            state.dirty = true; /* CL-APP-09b: the list must refresh NOW */
            closeOverlay();
            renderPanels();
          })
          .catch(function () { toast('network'); });
      });
    });
  }

  function startAdd(placeId) {
    ensureSignedIn().then(function (ok) {
      if (!ok) return;
      loadContracts().then(function () { editorModal({ placeId: placeId }); });
    });
  }

  // ───────────────────────── session ─────────────────────────
  var sessionPromise = null;
  function fetchMe() {
    return api('/api/v1/auth/me').then(function (r) {
      if (r.status === 401) {
        // silent refresh (member-auth pattern): one retry after POST refresh
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
    renderPanels();
  });
  window.addEventListener('pageshow', function () { renderPanels(); });

  // ───────────────────────── panel decoration ─────────────────────────
  // The 題材 panel (place modal) is rebuilt by app.js on every open; a
  // MutationObserver appends the 自訂題材 section idempotently (signature
  // keyed, no DOM write when unchanged — same incremental-sync pattern as
  // the private cards).
  function panelHost() {
    var overlay = document.getElementById('place-modal-overlay');
    if (!overlay || overlay.style.display !== 'flex') return null;
    var placeId = overlay.dataset.placeId || '';
    var body = document.getElementById('place-modal-body');
    if (!placeId || !body || !body.querySelector('.opportunity-card')) return null;
    return { overlay: overlay, body: body, placeId: placeId };
  }
  function relLabel(localDate) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(localDate || ''));
    if (!m) return String(localDate || '');
    try {
      var d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
      var now = new Date(); var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      var diff = Math.round((d - today) / 86400000);
      var zh = currentLang() === 'zh-TW', ja = currentLang() === 'ja';
      if (diff === 0) return zh ? '今天' : ja ? '今日' : 'Today';
      if (diff === 1) return zh ? '明天' : ja ? '明日' : 'Tomorrow';
      if (diff === 2) return zh ? '後天' : ja ? '明後日' : 'Day after';
    } catch (e) { /* fall through */ }
    return String(localDate || '').slice(5).replace('-', '/');
  }
  function mergeHours(hours) {
    // consecutive HH:MM stamps compress to segments (official strip anatomy)
    var sorted = hours.slice().sort();
    var segs = [], cur = null;
    var toMin = function (s) { var p = s.split(':'); return Number(p[0]) * 60 + Number(p[1]); };
    var fmt = function (mm) { var h = Math.floor(mm / 60), m2 = mm % 60; return (h < 10 ? '0' : '') + h + ':' + (m2 < 10 ? '0' : '') + m2; };
    sorted.forEach(function (s) {
      if (!/^\d\d:\d\d$/.test(s)) return;
      var mm = toMin(s);
      if (cur && mm - cur.end === 30) cur.end = mm;
      else { if (cur) segs.push(cur); cur = { start: mm, end: mm }; }
    });
    if (cur) segs.push(cur);
    return segs.map(function (s) { return s.start === s.end ? fmt(s.start) : fmt(s.start) + '–' + fmt(s.end); }).join(' ');
  }
  function dayHtml(day) {
    var ok = day.state === 'GUIDANCE_SATISFIED';
    var cls = ok ? 'v2-ok' : 'v2-bad';
    var label = relLabel(day.local_date);
    var hoursN = day.hours.length;
    var seg = hoursN ? mergeHours(day.hours) : '';
    return '<div class="v2-day ' + cls + '"><span class="v2-day-label">' + esc(label) + '</span>' +
      '<span class="v2-badge ' + cls + '">' + esc(ok ? t().day_ok : t().day_bad) + '</span>' +
      '<span class="v2-hours">' + esc(t().hours_lbl) + ' ' + hoursN + (seg ? ' · ' + esc(seg) : '') + '</span></div>';
  }
  // Resolved-bound line for anchor window sets. Returns null when the verdict
  // carries no resolvable anchor data (then the hour merge stays as before).
  function dynamicWindowLine(ev) {
    var wr = ev && Array.isArray(ev.windowResolved) ? ev.windowResolved : null;
    if (!wr || !wr.length) return null;
    var spans = [];
    var label = '';
    var hasAnchor = false;
    var lang = currentLang(), zh = lang === 'zh-TW', ja = lang === 'ja';
    for (var i = 0; i < wr.length; i++) {
      var s = wr[i];
      if (!s || !s.start || !s.end) continue; // unresolved segment — honest skip
      var span;
      if (!s.type || s.type === 'fixed') {
        span = s.start === s.end ? s.start : s.start + '–' + s.end;
      } else {
        hasAnchor = true;
        label = label || wtLabel(s.type);
        if (s.type.indexOf('before_') === 0 && s.start === '00:00') {
          span = zh ? s.end + ' 前' : ja ? s.end + ' まで' : 'before ' + s.end;
        } else if (s.type.indexOf('after_') === 0 && s.end === '23:59') {
          span = zh ? s.start + ' 起' : ja ? s.start + ' から' : 'from ' + s.start;
        } else {
          span = s.start === s.end ? s.start : s.start + '–' + s.end;
        }
      }
      spans.push(span);
    }
    if (!spans.length || !hasAnchor) return null;
    return { label: label, spans: spans.join('＋') };
  }
  function setRowHtml(set, ev) {
    var stale = set.templateId && set.baseRev != null && (function () {
      var c = contractFor(set.templateId);
      return !!c && typeof c.revision === 'number' && c.revision > set.baseRev;
    })();
    var days = ev && Array.isArray(ev.days) ? ev.days : [];
    var strip = days.map(dayHtml).join('');
    var tier = ev ? ev.tier : null;
    var windowLine = '';
    if (ev && ev.window && ev.window.hours && ev.window.hours.length) {
      // CL-APP-09 patch-2: anchor segments carry the RESOLVED real sun bounds
      // (windowResolved from the engine) — 「下一窗 今天 日出前（每日動態）·05:10 前」;
      // two-segment sets read 「下一窗 今天 05:00–06:00＋17:30–18:40（每日動態）」.
      var dyn = dynamicWindowLine(ev);
      if (dyn) {
        windowLine = t().next_win + relLabel(ev.window.local_date) + ' ' +
          (dyn.label ? dyn.label + '（每日動態）·' + dyn.spans : dyn.spans + '（每日動態）');
      } else {
        windowLine = t().next_win + relLabel(ev.window.local_date) + ' ' + mergeHours(ev.window.hours);
      }
    } else if (ev && ev.tier === 'no') {
      windowLine = ev.failReason === '非適用月份' ? t().fail_month
        : ev.failReason === '時段待座標同步' ? t().fail_wp
        : t().no_win;
    } else if (!ev) {
      windowLine = t().fail_no_data;
    }
    var monthsLine = (set.months && set.months.length)
      ? t().months_fmt.replace('{m}', set.months.map(function (m) { return m + '月'; }).join('、'))
      : t().months_all;
    var rows = diffRows(set.conditions || {}, set.baseConditions || {});
    var diffHtml = set.templateId
      ? '<details class="cl-ss-diff"><summary>' + esc(t().diff_title) + '</summary><div class="cl-ss-diff-body">' +
        rows.map(function (r) {
          return '<div class="cl-ss-diff-row' + (r.warn ? ' cl-ss-diff-warn' : '') + '">' +
            '<span class="cl-ss-diff-metric">' + esc(r.metric) + '</span>' +
            '<span>' + esc(t().diff_official) + ' ' + esc(fmtNum(r.official)) + '</span>' +
            '<span>' + esc(t().diff_mine) + ' ' + esc(fmtNum(r.mine)) + (r.pct != null ? '（' + (r.mine >= r.official ? '+' : '−') + r.pct + '%）' : '') + '</span>' +
            (r.warn ? '<span class="cl-ss-diff-flag">' + esc(t().diff_warn) + '</span>' : '') +
            '</div>';
        }).join('') + '</div></details>'
      : '<div class="cl-ss-diff-none">' + esc(t().diff_none) + '</div>';
    var actions = '<div class="cl-ss-actions">' +
      '<button type="button" class="cl-ss-act" data-ss-act="edit" data-ss-id="' + esc(set.id) + '">' + esc(t().edit_btn) + '</button>' +
      (set.templateId ? '<button type="button" class="cl-ss-act" data-ss-act="reset" data-ss-id="' + esc(set.id) + '">' + esc(t().reset_btn) + '</button>' : '') +
      (stale ? '<button type="button" class="cl-ss-act cl-ss-act-sync" data-ss-act="sync" data-ss-id="' + esc(set.id) + '">' + esc(t().sync_btn) + '</button>' : '') +
      '<button type="button" class="cl-ss-act cl-ss-act-del" data-ss-act="del" data-ss-id="' + esc(set.id) + '">' + esc(t().del_btn) + '</button>' +
      '</div>';
    return '<div class="cl-ss-row" data-ss-set="' + esc(set.id) + '">' +
      '<div class="opportunity-head"><div class="opportunity-title">' + esc(set.name) +
      ' <span class="cl-ss-badge">' + esc(t().badge) + '</span>' +
      (stale ? ' <span class="cl-ss-badge cl-ss-badge-stale">' + esc(t().stale_badge) + '</span>' : '') +
      '</div></div>' +
      (tier === 'pending' ? '<div class="cl-ss-nonote">' + esc(t().fail_no_data) + '</div>' : '') +
      (strip ? '<div class="cl-ss-strip">' + strip + '</div>' : '') +
      '<div class="cl-ss-meta"><span>' + esc(monthsLine) + '</span>' +
      (windowLine ? '<span>' + esc(windowLine) + '</span>' : '') + '</div>' +
      diffHtml + actions + '</div>';
  }
  function renderPanels() {
    var host = panelHost();
    if (!host) return;
    var sig = host.placeId + '|' + currentLang() + '|' + (state.member ? state.member.displayName || '1' : 'out');
    var section = host.body.querySelector('.cl-ss-section');
    // CL-APP-09b: a create/update/reset/delete must show up IMMEDIATELY — the
    // signature guard (same panel still open) would otherwise skip the
    // re-render and the new set stayed invisible until the panel was reopened.
    if (section && !state.dirty && section.dataset.ssSig === sig && section._ssSig2 === host.body.childElementCount) {
      // same panel still open; refresh verdicts only if data changed
      return;
    }
    state.dirty = false;
    if (!section) {
      section = document.createElement('div');
      section.className = 'cl-ss-section';
      var hourlyBtn = host.body.querySelector('#place-hourly-btn');
      if (hourlyBtn && hourlyBtn.parentNode) hourlyBtn.parentNode.insertBefore(section, hourlyBtn);
      else host.body.appendChild(section);
    }
    section.dataset.ssSig = sig;
    section._ssSig2 = host.body.childElementCount;
    section.innerHTML = '<div class="cl-ss-head"><span class="cl-ss-head-title">' + esc(t().sec_title) + '</span>' +
      '<span class="cl-ss-quota" id="cl-ss-quota"></span>' +
      '<button type="button" class="cl-ss-add" id="cl-ss-add">' + esc(t().add_btn) + '</button></div>' +
      '<div class="cl-ss-rows" id="cl-ss-rows"><div class="cl-ss-loading">…</div></div>';
    var addBtn = section.querySelector('#cl-ss-add');
    if (addBtn) addBtn.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); startAdd(host.placeId); });
    ensureSignedIn().then(function (signed) {
      if (!signed) {
        var rows = section.querySelector('#cl-ss-rows');
        if (rows) rows.innerHTML = '<div class="cl-ss-login"><div>' + esc(t().login_note) + '</div></div>';
        return;
      }
      Promise.all([
        api(API + '?place_id=' + encodeURIComponent(host.placeId)).then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); }),
        api(API + '/eval?place_id=' + encodeURIComponent(host.placeId)).then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); }),
      ]).then(function (rs) {
        var list = rs[0], evalRes = rs[1];
        var rows = section.querySelector('#cl-ss-rows');
        if (!rows) return;
        if (list.status === 401) {
          rows.innerHTML = '<div class="cl-ss-login"><div>' + esc(t().login_note) + '</div></div>';
          return;
        }
        if (list.status !== 200) {
          rows.innerHTML = '<div class="cl-ss-login">' + esc((list.body && list.body.error) || 'HTTP ' + list.status) + '</div>';
          return;
        }
        var data = list.body || {};
        var caps = data.caps || { place: 5 };
        var level = data.level || (state.member && state.member.level) || 'free';
        var quota = section.querySelector('#cl-ss-quota');
        if (quota) {
          var ownerCap = caps.place === Infinity || caps.place === null;
          var dayCap = caps.total != null ? 5 : null; // free daily-add cap rides the total cap (final ruling)
          quota.textContent = ownerCap
            ? t().quota_owner.replace('{p}', String(data.counts.place))
            : (level === 'free' && caps.total != null
              ? t().quota_free.replace('{p}', String(data.counts.place)).replace('{pc}', String(caps.place))
                .replace('{t}', String(data.counts.total)).replace('{tc}', String(caps.total)).replace('{d}', String(dayCap))
              : t().quota_fmt.replace('{p}', String(data.counts.place)).replace('{pc}', String(caps.place)));
        }
        var evById = {};
        if (evalRes.status === 200 && evalRes.body && Array.isArray(evalRes.body.sets)) {
          evalRes.body.sets.forEach(function (s) { evById[s.id] = s; });
        }
        state.lastEvalById = evById; // the edit flow reuses the verdict for the anchor hint
        var sets = data.sets || [];
        if (!sets.length) {
          rows.innerHTML = '<div class="cl-ss-empty">' + esc(t().cc_prev_none) + '</div>';
        } else {
          rows.innerHTML = sets.map(function (s) { return setRowHtml(s, evById[s.id]); }).join('');
          wireRowActions(rows, host.placeId);
        }
        // free at cap → gray upgrade card (owner spec §3, gray style)
        if (level === 'free' && caps.total != null && data.counts.total >= caps.total) {
          var card = document.createElement('div');
          card.className = 'cl-ss-upgrade';
          card.textContent = t().free_cap_note;
          rows.appendChild(card);
        }
      }).catch(function () {
        var rows = section.querySelector('#cl-ss-rows');
        if (rows) rows.innerHTML = '<div class="cl-ss-login">' + esc(t().fail_no_data) + '</div>';
      });
    });
  }
  function wireRowActions(rows, placeId) {
    rows.querySelectorAll('[data-ss-act]').forEach(function (b) {
      b.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        var id = b.dataset.ssId, act = b.dataset.ssAct;
        if (act === 'edit') {
          loadContracts().then(function () {
            api(API + '?place_id=' + encodeURIComponent(placeId)).then(function (r) { return r.json(); }).then(function (data) {
              var set = (data.sets || []).find(function (s) { return s.id === id; });
              if (set) editorModal({ placeId: placeId, set: set, ev: (state.lastEvalById || {})[id] || null });
            });
          });
        } else if (act === 'reset') {
          api(API + '?place_id=' + encodeURIComponent(placeId)).then(function (r) { return r.json(); }).then(function (data) {
            var set = (data.sets || []).find(function (s) { return s.id === id; });
            if (!set) return;
            return api(API + '/' + id, {
              method: 'PATCH', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ reset_to_official: true }),
            }).then(function (r) { return r.json().then(function (bd) { return { status: r.status, body: bd }; }); })
              .then(function (r) {
                if (r.status === 200) { state.dirty = true; toast(t().reset_note); renderPanels(); }
                else toast((r.body && r.body.error) || 'HTTP ' + r.status);
              });
          });
        } else if (act === 'sync') {
          loadContracts().then(function () {
            api(API + '?place_id=' + encodeURIComponent(placeId)).then(function (r) { return r.json(); }).then(function (data) {
              var set = (data.sets || []).find(function (s) { return s.id === id; });
              if (!set) return;
              var c = contractFor(set.templateId);
              if (!c) { toast(t().fail_no_data); return; }
              return api(API + '/' + id, {
                method: 'PATCH', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ base_conditions: mapOfficialToCc(c), base_rev: c.revision || null }),
              }).then(function (r) { return r.json().then(function (bd) { return { status: r.status, body: bd }; }); })
                .then(function (r) {
                  if (r.status === 200) { state.dirty = true; toast(t().sync_note); renderPanels(); }
                  else toast((r.body && r.body.error) || 'HTTP ' + r.status);
                });
            });
          });
        } else if (act === 'del') {
          api(API + '/' + id, { method: 'DELETE' })
            .then(function (r) { return r.json().then(function (bd) { return { status: r.status, body: bd }; }); })
            .then(function (r) {
              if (r.status === 200) { state.dirty = true; renderPanels(); }
              else toast((r.body && r.body.error) || 'HTTP ' + r.status);
            }).catch(function () { toast('network'); });
        }
      });
    });
  }

  // MutationObserver: both the card grid (⋯ button per official card) and
  // the place modal body (panel section). Idempotent — signature-guarded.
  function decorateCards() {
    var grid = document.getElementById('spots-container');
    if (!grid) return;
    grid.querySelectorAll('.card:not(.cl-cp-card)').forEach(function (card) {
      if (card.querySelector('.cl-ss-more')) return;
      var actions = card.querySelector('.card-header-actions');
      var spotId = card.dataset.placeId || card.dataset.spotId || '';
      if (!actions || !spotId) return;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'cl-ss-more';
      btn.setAttribute('aria-label', '⋯');
      btn.setAttribute('aria-haspopup', 'menu');
      btn.setAttribute('aria-expanded', 'false');
      btn.textContent = '⋯';
      actions.appendChild(btn);
    });
  }
  var mo = null;
  function boot() {
    if (mo || typeof MutationObserver === 'undefined') return;
    mo = new MutationObserver(function () {
      decorateCards();
      renderPanels();
    });
    mo.observe(document.body, { childList: true, subtree: true });
    decorateCards();
    renderPanels();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  // test / integration surface
  window.ChaseLightsSubjectSets = {
    renderPanels: renderPanels,
    state: function () {
      var s = {};
      for (var k in state) s[k] = state[k];
      return JSON.parse(JSON.stringify(s, function (key, val) { return val === undefined ? null : val; }));
    },
    startAdd: startAdd,
  };
})();
