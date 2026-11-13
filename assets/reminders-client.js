/* CL-UI-58: card "加入提醒" button + notify_rules client for the V1 shell.
   Mirrors the favorites-client.js precedent (CL-UI-55): self-contained,
   ships its own trilingual copy, never edits the heavily test-pinned
   assets/app.js beyond the single button template inside the best-subject
   summary line. Buttons are re-enhanced via a MutationObserver so card
   re-renders (day tab / language / region switches) restyle themselves.

   Backend contract (workers/api/src/index.js + notify.js, CL-API-03/58;
   CL-UI-61: the real worker route is /notify/rules under the /api/v1 base —
   the earlier /notify_rules spelling was a 404):
   - GET    /api/v1/notify/rules        -> { userId, level, rules:[{id, place_id, opportunity_id, channel, min_advance_hours, enabled, created_at}] } (JWT only)
   - POST   /api/v1/notify/rules        { placeId, opportunityId?, channel:'push', minAdvanceHours:24 } -> { ok, rule, count, limit } (402 = free-tier cap)
   - PATCH  /api/v1/notify/rules/<id>   { enabled: boolean } -> { ok, rule } (CL-UI-58 added the toggle)
   - DELETE /api/v1/notify/rules/<id>   -> { ok, deleted }
   Sessions ride HttpOnly cookies (CL-UI-53) — same-origin fetches carry them;
   notify rules have NO anonymous fallback, so 401 always means "log in first".

   CL-UI-61 login gate: boot resolves the session via /api/v1/auth/me first
   (throttled to one call per window) and only fetches rules while signed in;
   signed-out visitors get the login toast, never a sync error.

   Failure posture: a network error never blocks the card — the button keeps
   its previous state and a trilingual toast explains the retry. */
(function () {
  'use strict';

  var RULES_ENDPOINT = '/api/v1/notify/rules';
  var ME_ENDPOINT = '/api/v1/auth/me';

  var I18N = {
    'zh-TW': {
      rem_add: '🔔 加入提醒',
      rem_added: '🔔 已設定提醒 · 點擊移除',
      rem_add_aria: '為這個題材加入拍攝提醒',
      rem_added_aria: '已設定提醒，點擊移除',
      rem_login: '請先登入後再設定提醒',
      rem_saved: '已加入提醒，條件符合時將透過 APP 推播通知。',
      rem_removed: '已移除提醒。',
      rem_err: '提醒暫時無法同步，請稍後再試。',
      rem_limit: '提醒數量已達方案上限，請先移除部分提醒。'
    },
    'en': {
      rem_add: '🔔 Add reminder',
      rem_added: '🔔 Reminder set · tap to remove',
      rem_add_aria: 'Add a shooting reminder for this subject',
      rem_added_aria: 'Reminder set, tap to remove',
      rem_login: 'Please sign in before setting reminders',
      rem_saved: 'Reminder added — you will be notified via app push when conditions qualify.',
      rem_removed: 'Reminder removed.',
      rem_err: 'Reminders could not be synced right now; please try again later.',
      rem_limit: 'Reminder limit reached for your plan — remove some reminders first.'
    },
    'ja': {
      rem_add: '🔔 リマインダー追加',
      rem_added: '🔔 リマインダー設定済み · タップで削除',
      rem_add_aria: 'この題材の撮影リマインダーを追加',
      rem_added_aria: 'リマインダー設定済み、タップで削除',
      rem_login: 'リマインダーを使うには先にログインしてください',
      rem_saved: 'リマインダーを追加しました。条件が揃うとアプリのプッシュ通知でお知らせします。',
      rem_removed: 'リマインダーを削除しました。',
      rem_err: 'リマインダーを同期できませんでした。しばらくしてから再試行してください。',
      rem_limit: 'リマインダー数がプランの上限に達しました。先に一部を削除してください。'
    }
  };

  function lang() {
    var sel = document.getElementById('lang-select');
    var v = (sel && typeof sel.value === 'string' && sel.value) ||
            (function () { try { return localStorage.getItem('chaselights_lang'); } catch (e) { return null; } }()) || 'zh-TW';
    return I18N[v] ? v : 'zh-TW';
  }
  function t(key) { var p = I18N[lang()]; return (p && p[key]) || I18N['zh-TW'][key] || ''; }

  // ---- toast (favorites-client.js precedent) ----
  var notice = null, noticeTimer = null;
  function showNotice(key) {
    try {
      if (!notice) {
        notice = document.createElement('p');
        notice.className = 'rem-notice';
        notice.setAttribute('role', 'status');
        notice.style.cssText = 'position:fixed;bottom:12px;left:12px;right:12px;margin:0 auto;max-width:420px;padding:8px 12px;border:1px solid #475569;background:#111827;color:#e2e8f0;font-size:13px;border-radius:8px;z-index:10001;text-align:center';
        document.body.appendChild(notice);
      }
      notice.textContent = t(key);
      notice.hidden = false;
      if (noticeTimer) clearTimeout(noticeTimer);
      noticeTimer = setTimeout(function () { if (notice) notice.hidden = true; }, 6000);
    } catch (e) { /* no body yet — notices are best-effort */ }
  }

  // ---- state ----
  // rulesByKey: "placeId|oppId" -> rule object (oppId '' = any-subject rule).
  var state = { rules: {}, loaded: false, signedIn: null, busy: {} };

  function ruleKey(placeId, oppId) { return String(placeId || '') + '|' + String(oppId || ''); }

  // The rule governing a card button: an exact place+subject rule wins, else
  // the place-level any-subject rule (opportunity_id-less) covers the button.
  function ruleFor(map, placeId, oppId) {
    return map[ruleKey(placeId, oppId)] || map[ruleKey(placeId, '')] || null;
  }

  function reindex(rules) {
    var map = {};
    (rules || []).forEach(function (r) {
      // A rule with no opportunity_id covers any subject at the place.
      var k = ruleKey(r.place_id, r.opportunity_id || '');
      map[k] = r;
      if (r.opportunity_id) { var any = ruleKey(r.place_id, ''); if (!map[any]) map[any] = r; }
    });
    return map;
  }

  function fetchRules() {
    return fetch(RULES_ENDPOINT, { headers: { Accept: 'application/json' } }).then(function (r) {
      if (r.status === 401) { state.signedIn = false; state.rules = {}; state.loaded = true; return null; }
      if (!r.ok) throw new Error('HTTP ' + r.status);
      state.signedIn = true;
      return r.json();
    }).then(function (body) {
      if (body) { state.rules = reindex(body.rules); state.loaded = true; }
      return state.rules;
    });
  }

  // CL-UI-61: the session check is throttled — one /auth/me call per window
  // (boot, card clicks, tab returns reuse the same in-flight/cached answer
  // instead of hammering the endpoint). force=true bypasses the window
  // (e.g. the chaselights:auth event after a login in another surface).
  var ME_THROTTLE_MS = 30000;
  var mePromise = null, meAt = 0;
  function checkSignedIn(force) {
    var now = Date.now();
    if (!force && mePromise && now - meAt < ME_THROTTLE_MS) return mePromise;
    meAt = now;
    mePromise = fetch(ME_ENDPOINT, { headers: { Accept: 'application/json' } }).then(function (r) {
      state.signedIn = r.ok;
      return state.signedIn;
    }).catch(function () {
      return state.signedIn === true;
    });
    return mePromise;
  }

  function createRule(placeId, oppId) {
    return fetch(RULES_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ placeId: placeId, opportunityId: oppId || undefined, channel: 'push', minAdvanceHours: 24 })
    }).then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); });
  }

  function deleteRule(ruleId) {
    return fetch(RULES_ENDPOINT + '/' + encodeURIComponent(ruleId), { method: 'DELETE' })
      .then(function (r) { return r.json().then(function (b) { return { status: r.status, body: b }; }); });
  }

  // CL-UI-61 login gate: rules are fetched only after /auth/me says signed-in.
  // Signed-out visitors never hit the rules endpoint (their buttons keep the
  // plain label; the click guard shows the login toast).
  function refresh(force) {
    return checkSignedIn(force).then(function (signed) {
      if (!signed) { state.rules = {}; state.loaded = true; enhance(); return state.rules; }
      return fetchRules().then(enhance).catch(function () { enhance(); });
    });
  }

  // ---- DOM ----
  function placeOf(btn) { return btn.getAttribute('data-rem-place') || ''; }
  function oppOf(btn) { return btn.getAttribute('data-rem-opp') || ''; }

  function applyToButton(btn) {
    var rule = state.rules[ruleKey(placeOf(btn), oppOf(btn))] || state.rules[ruleKey(placeOf(btn), '')];
    var added = !!rule;
    // CL-UI-69 compact mode: per-subject-row bells render the icon only
    // (owner ruling — 🔔 toggle, ★ stays favorites-only; the app.css
    // .cl-rem-compact rules make hollow=off, filled/highlight=on).
    var compact = btn.getAttribute('data-rem-compact') === '1';
    btn.classList.toggle('cl-rem-on', added);
    btn.textContent = compact ? '🔔' : (added ? t('rem_added') : t('rem_add'));
    btn.setAttribute('aria-label', added ? t('rem_added_aria') : t('rem_add_aria'));
    btn.setAttribute('aria-pressed', added ? 'true' : 'false');
    if (state.busy[ruleKey(placeOf(btn), oppOf(btn))]) btn.setAttribute('data-rem-busy', '1');
    else btn.removeAttribute('data-rem-busy');
  }

  function enhance() {
    var btns = document.querySelectorAll('.cl-rem-btn');
    for (var i = 0; i < btns.length; i++) applyToButton(btns[i]);
  }

  function onCardClick(placeId, oppId, btn) {
    var key = ruleKey(placeId, oppId);
    if (state.busy[key]) return;
    if (state.signedIn === false) { showNotice('rem_login'); return; }
    var rule = ruleFor(state.rules, placeOf(btn), oppOf(btn));
    state.busy[key] = true;
    if (btn) btn.setAttribute('data-rem-busy', '1');
    var work = rule ? deleteRule(rule.id) : createRule(placeId, oppId);
    work.then(function (res) {
      if (res && res.status === 401) { state.signedIn = false; showNotice('rem_login'); return; }
      if (res && res.status === 402) { showNotice('rem_limit'); return; }
      if (!res || !res.body || res.body.ok !== true) { showNotice('rem_err'); return; }
      showNotice(rule ? 'rem_removed' : 'rem_saved');
      return refresh();
    }).catch(function () {
      showNotice('rem_err');
    }).then(function () {
      delete state.busy[key];
      enhance();
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target && e.target.closest ? e.target.closest('.cl-rem-btn') : null;
    if (!btn) return;
    e.preventDefault();
    // Signed-in state may be stale (login/logout in another tab) — the API is
    // the authority; an optimistic stale state still resolves via 401/refresh.
    if (state.signedIn === null) {
      checkSignedIn().then(function () { onCardClick(placeOf(btn), oppOf(btn), btn); });
    } else {
      onCardClick(placeOf(btn), oppOf(btn), btn);
    }
  });

  // Re-enhance buttons after every card re-render (day tabs / language / region).
  var enhanceTimer = null;
  if (typeof MutationObserver === 'function') {
    new MutationObserver(function () {
      if (enhanceTimer) clearTimeout(enhanceTimer);
      enhanceTimer = setTimeout(enhance, 50);
    }).observe(document.documentElement, { childList: true, subtree: true });
  }
  // The auth event fires after a login/logout in another surface — the cached
  // signed-in answer is stale, so force a fresh /auth/me.
  document.addEventListener('chaselights:auth', function () { refresh(true); });
  window.addEventListener('pageshow', function () { refresh(); });

  function boot() {
    refresh();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  // Exposed for reminders-page.js and tests.
  window.ChaseLightsReminders = {
    enhance: enhance,
    refresh: refresh,
    state: state,
    ruleKey: ruleKey,
    ruleFor: ruleFor,
    reindex: reindex,
    t: t,
    lang: lang,
    _internals: { fetchRules: fetchRules, checkSignedIn: checkSignedIn, createRule: createRule, deleteRule: deleteRule, onCardClick: onCardClick }
  };
})();
