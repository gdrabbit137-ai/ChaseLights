/* CL-UI-53: homepage member sign-in entry (V1 shell masthead).
   Mirrors apps/web-v2/shell-auth.mjs semantics (CL-APP-02): the start
   endpoints are plain top-level navigations (302 to the OAuth provider), so
   they render as anchors, never fetched; JWTs ride HttpOnly cookies, so
   same-origin fetches to /api/v1/auth/me carry the session automatically —
   no token handling lives here. Logout is a same-origin POST to
   /api/v1/auth/logout (CL-UI-54: the bare /auth/* paths 404'd — the API
   mounts everything under /api/v1).
   Self-contained on purpose, following the guest-comment.js precedent
   (GC_ENDPOINT): the main assets/app.js is heavily test-pinned, so this
   widget ships its own trilingual copy and never edits it.
   Styling reuses the existing site-nav shell classes (.site-nav-more /
   .site-nav-more-btn / .site-nav-menu) — no new stylesheet. */
(function () {
  'use strict';

  var MA_ENDPOINTS = {
    me: '/api/v1/auth/me',
    refresh: '/api/v1/auth/refresh',
    logout: '/api/v1/auth/logout',
    profile: '/api/v1/auth/profile',
    line: '/api/v1/auth/line/start',
    google: '/api/v1/auth/google/start'
  };

  var MA_I18N = {
    'zh-TW': {
      ma_login: '登入',
      ma_logout: '登出',
      ma_line: '使用 LINE 登入',
      ma_google: '使用 Google 登入',
      ma_signed_in_as: '會員',
      ma_auth_error: '登入失敗，請重試',
      ma_edit_profile: '編輯會員資料',
      ma_nickname: '暱稱',
      ma_experience: '拍攝資歷（選填）',
      ma_region: '常用地區（選填）',
      ma_bio: '自介（選填）',
      ma_profile_save: '儲存',
      ma_profile_cancel: '取消',
      ma_profile_saved: '已儲存會員資料。',
      ma_profile_error: '儲存失敗，請重試'
    },
    'en': {
      ma_login: 'Sign in',
      ma_logout: 'Sign out',
      ma_line: 'Sign in with LINE',
      ma_google: 'Sign in with Google',
      ma_signed_in_as: 'Member',
      ma_auth_error: 'Sign in failed, please try again',
      ma_edit_profile: 'Edit member profile',
      ma_nickname: 'Nickname',
      ma_experience: 'Photography experience (optional)',
      ma_region: 'Usual shooting region (optional)',
      ma_bio: 'Bio (optional)',
      ma_profile_save: 'Save',
      ma_profile_cancel: 'Cancel',
      ma_profile_saved: 'Member profile saved.',
      ma_profile_error: 'Could not save, please try again'
    },
    'ja': {
      ma_login: 'ログイン',
      ma_logout: 'ログアウト',
      ma_line: 'LINEでログイン',
      ma_google: 'Googleでログイン',
      ma_signed_in_as: '会員',
      ma_auth_error: 'ログインに失敗しました。もう一度お試しください',
      ma_edit_profile: 'メンバー情報を編集',
      ma_nickname: 'ニックネーム',
      ma_experience: '撮影歴（任意）',
      ma_region: 'よく撮影する地域（任意）',
      ma_bio: '自己紹介（任意）',
      ma_profile_save: '保存',
      ma_profile_cancel: 'キャンセル',
      ma_profile_saved: 'プロフィールを保存しました。',
      ma_profile_error: '保存に失敗しました。もう一度お試しください'
    }
  };

  // CL-API-05: OAuth callbacks land back on the homepage; the failure variant
  // carries ?auth_error=1. Show a trilingual retry notice and clean the URL —
  // no bare JSON page is ever rendered by the callback.
  function showAuthErrorNotice() {
    var q = new URLSearchParams(window.location.search);
    if (q.get('auth_error') !== '1') return;
    try {
      q.delete('auth_error');
      var rest = q.toString();
      window.history.replaceState(null, '', window.location.pathname + (rest ? '?' + rest : '') + window.location.hash);
    } catch (e) { /* replaceState unavailable — notice still shows */ }
    var note = document.createElement('p');
    note.className = 'ma-auth-error';
    note.setAttribute('role', 'status');
    note.style.cssText = 'margin:6px 12px 0;padding:6px 10px;border:1px solid #b36;background:#2a1420;color:#ffb3c8;font-size:13px;border-radius:6px';
    note.textContent = t('ma_auth_error');
    if (area && area.parentNode) area.parentNode.insertBefore(note, area);
    else document.body.appendChild(note);
    window.setTimeout(function () { if (note.parentNode) note.parentNode.removeChild(note); }, 8000);
  }

  function maLang() {
    var sel = document.getElementById('lang-select');
    var v = (sel && typeof sel.value === 'string' && sel.value) ||
            localStorage.getItem('chaselights_lang') || 'zh-TW';
    return MA_I18N[v] ? v : 'zh-TW';
  }

  function t(key) {
    var pack = MA_I18N[maLang()];
    return (pack && pack[key]) || MA_I18N['zh-TW'][key] || '';
  }

  function applyCopy() {
    var nodes = document.querySelectorAll('[data-ma-i18n]');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var v = t(el.getAttribute('data-ma-i18n'));
      if (v) el.textContent = v;
    }
  }

  // Same semantics as apps/web-v2/shell-auth.mjs parseMember: anything
  // without a usable display name (401, empty object, blank name) is
  // "not signed in" — the entry must show the sign-in buttons, never a
  // fake member.
  function parseMember(doc) {
    if (!doc || typeof doc !== 'object' || Array.isArray(doc)) return null;
    // CL-UI-56: /api/v1/auth/me actually answers { user: { displayName, provider, … } }
    // (nested + camelCase, see workers/api/src/index.js handleAuthMe), so the
    // nested shape wins; legacy top-level display_name/name/sub stay supported.
    var u = (doc.user != null && typeof doc.user === 'object') ? doc.user : null;
    var raw = (u && u.displayName != null) ? u.displayName :
              (doc.display_name != null ? doc.display_name :
              (doc.name != null ? doc.name : (doc.sub != null ? doc.sub : null)));
    if (typeof raw !== 'string') return null;
    var name = raw.trim();
    if (!name) return null;
    var rawProvider = (u && typeof u.provider === 'string' && u.provider.trim()) ? u.provider :
                      (typeof doc.provider === 'string' && doc.provider.trim() ? doc.provider : null);
    var provider = rawProvider ? rawProvider.trim() : null;
    // CL-UI-57: /auth/me carries the member-editable profile object
    // (experience/region/bio — migration 0006 profile_json). Unknown or
    // non-object shapes stay null; the editor treats that as "empty".
    var prof = (u && u.profile != null && typeof u.profile === 'object' && !Array.isArray(u.profile)) ? u.profile :
               (doc.profile != null && typeof doc.profile === 'object' && !Array.isArray(doc.profile) ? doc.profile : null);
    // CL-UI-57: profile is attached only when present — legacy callers see the
    // original { name, provider } shape unchanged.
    return prof ? { name: name, provider: provider, profile: prof } : { name: name, provider: provider };
  }

  // CL-UI-60: silent session renewal (mirrors apps/web-v2/shell-auth.mjs).
  // The access JWT cookie (cl_session) expires after 15 minutes while the
  // refresh JWT cookie (cl_refresh) lasts 30 days (workers/api/src/index.js
  // handleAuthRefresh), so a 401 on /auth/me must try POST /auth/refresh once
  // before declaring the visitor signed out — the owner-visible bug was the
  // masthead flipping back to 「登入」 after every 15-minute expiry. The
  // worker answers 200 { ok, accessToken, refreshToken } and rotates BOTH
  // cookies via Set-Cookie, so the follow-up /auth/me succeeds without any
  // token handling here; 401 answers { error: "invalid refresh token" }.
  // Throttle: at most one refresh attempt per window (remembered in closure
  // state, so a renewed session never double-calls me+refresh on every
  // load/lang switch), and concurrent 401s share a single in-flight refresh.
  var MA_REFRESH_THROTTLE_MS = 30000;
  var maLastRefreshAt = 0, maRefreshInFlight = null;

  function maFetch(url, opts) {
    return fetch(url, opts).catch(function () { return null; });
  }

  function maMeOnce() {
    return maFetch(MA_ENDPOINTS.me, { credentials: 'same-origin', cache: 'no-store' })
      .then(function (res) {
        // CL-API-07: 429/5xx and network failure are transient — keep the
        // current state (only 401 after a failed refresh means signed out).
        if (!res || res.status === 429 || res.status >= 500) return MA_TRANSIENT;
        if (res.status === 401) return maRefreshThenMe();
        return res.ok ? res.json().catch(function () { return null; }) : MA_TRANSIENT;
      });
  }

  function maRefreshThenMe() {
    if (maRefreshInFlight) return maRefreshInFlight;
    if (Date.now() - maLastRefreshAt < MA_REFRESH_THROTTLE_MS) return Promise.resolve(null);
    maLastRefreshAt = Date.now();
    // The refresh JWT rides the HttpOnly cl_refresh cookie (same-origin);
    // the POST body stays empty — handleAuthRefresh also accepts a
    // { refreshToken } body but cookies are the only source in the shell.
    maRefreshInFlight = maFetch(MA_ENDPOINTS.refresh, {
      method: 'POST', credentials: 'same-origin', cache: 'no-store'
    }).then(function (res) {
      if (!res || !res.ok) return null;
      return maFetch(MA_ENDPOINTS.me, { credentials: 'same-origin', cache: 'no-store' })
        .then(function (meRes) {
          return (meRes && meRes.ok) ? meRes.json().catch(function () { return null; }) : null;
        });
    }).then(function (doc) {
      maRefreshInFlight = null;
      return doc;
    }).catch(function () {
      maRefreshInFlight = null;
      return null;
    });
    return maRefreshInFlight;
  }

  // CL-API-07: 429/5xx/network failure on /auth/me is NEVER "signed out" —
  // it returns the transient marker so render() keeps the current state and
  // schedules a backoff retry; only 401 (after a failed refresh) clears it.
  var MA_TRANSIENT = { transient: true };

  // CL-API-07: single-flight + short result cache — repeated member pulls on
  // one page load (boot, lang switch) share at most one real /auth/me per
  // cache window. Forced callers (logout, profile save) bypass via reset.
  var MA_ME_CACHE_MS = 10000;
  var maMeInFlight = null, maMeCacheMember = null, maMeCacheAt = 0;
  function maMeReset() {
    maMeInFlight = null; maMeCacheMember = null; maMeCacheAt = 0;
  }

  // CL-API-07: exponential backoff retry (1s → 2s → 4s, max 3) after a
  // transient failure — never re-render from the marker itself.
  var maRetryAttempt = 0, maRetryTimer = null;
  function maScheduleRetry() {
    if (maRetryAttempt >= 3) return;
    var delay = 1000 * Math.pow(2, maRetryAttempt++);
    if (maRetryTimer) clearTimeout(maRetryTimer);
    maRetryTimer = setTimeout(function () { fetchMember().then(render); }, delay);
  }

  function fetchMember() {
    if (maMeInFlight) return maMeInFlight;
    if (maMeCacheAt && Date.now() - maMeCacheAt < MA_ME_CACHE_MS) {
      return Promise.resolve(maMeCacheMember);
    }
    maMeInFlight = maMeOnce().then(function (doc) {
      var member = (doc === MA_TRANSIENT) ? MA_TRANSIENT : parseMember(doc);
      maMeCacheMember = member;
      maMeCacheAt = Date.now();
      return member;
    });
    return maMeInFlight.finally
      ? maMeInFlight.finally(function () { maMeInFlight = null; })
      : maMeInFlight.then(function (m) { maMeInFlight = null; return m; });
  }

  var area, toggle, menu, nameEl, logoutBtn, panel, profInputs = null, curMember = null;

  // CL-UI-57: save/error status notice — same fixed-bottom pattern as
  // favorites-client.js, trilingual copy from MA_I18N.
  var noticeEl = null, noticeTimer = null;
  function showNotice(key) {
    try {
      if (!noticeEl) {
        noticeEl = document.createElement('p');
        noticeEl.className = 'ma-profile-notice';
        noticeEl.setAttribute('role', 'status');
        noticeEl.style.cssText = 'position:fixed;bottom:12px;left:12px;right:12px;margin:0 auto;max-width:420px;padding:8px 12px;border:1px solid #475569;background:#111827;color:#e2e8f0;font-size:13px;border-radius:8px;z-index:10001;text-align:center';
        document.body.appendChild(noticeEl);
      }
      noticeEl.textContent = t(key);
      noticeEl.hidden = false;
      if (noticeTimer) clearTimeout(noticeTimer);
      noticeTimer = setTimeout(function () { if (noticeEl) noticeEl.hidden = true; }, 6000);
    } catch (e) { /* no body yet — notices are best-effort */ }
  }

  // CL-UI-57: the member profile editor. Clicking the member name while signed
  // in expands an inline panel (nickname = display_name, plus three optional
  // fields stored in users.profile_json via PATCH /api/v1/auth/profile).
  // All inline styles + a custom class: no shell display rule can un-hide it
  // (CL-UI-53B lesson), and no new stylesheet is needed.
  var PROFILE_PANEL_CSS = 'display:none;position:absolute;top:calc(100% + 6px);right:0;min-width:230px;margin:0;padding:10px 12px;border:1px solid #334155;background:#1e293b;border-radius:10px;box-shadow:0 10px 24px rgba(0,0,0,.5);z-index:401;box-sizing:border-box';
  var PROFILE_INPUT_CSS = 'display:block;width:100%;box-sizing:border-box;padding:4px 6px;font-size:13px;border:1px solid #334155;border-radius:6px;background:#0b1220;color:#e2e8f0';
  var PROFILE_LABEL_CSS = 'display:block;font-size:12px;color:#94a3b8;margin:8px 0 2px';
  var PROFILE_BTN_CSS = 'padding:6px 12px;font-size:13px;border-radius:8px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;cursor:pointer';

  function profileField(labelKey) {
    var label = document.createElement('label');
    label.style.cssText = PROFILE_LABEL_CSS;
    var span = document.createElement('span');
    span.setAttribute('data-ma-i18n', labelKey);
    label.appendChild(span);
    var input = document.createElement('input');
    input.type = 'text';
    input.style.cssText = PROFILE_INPUT_CSS;
    label.appendChild(input);
    panel.appendChild(label);
    return input;
  }

  function buildPanel() {
    if (panel) return;
    panel = document.createElement('div');
    panel.className = 'ma-profile-panel';
    panel.setAttribute('data-ma-profile-panel', '');
    panel.style.cssText = PROFILE_PANEL_CSS;
    profInputs = {
      name: profileField('ma_nickname'),
      experience: profileField('ma_experience'),
      region: profileField('ma_region'),
      bio: profileField('ma_bio')
    };
    var row = document.createElement('div');
    row.style.cssText = 'display:flex;gap:8px;margin-top:10px';
    var save = document.createElement('button');
    save.type = 'button';
    save.className = 'ma-profile-save';
    save.setAttribute('data-ma-i18n', 'ma_profile_save');
    save.style.cssText = PROFILE_BTN_CSS;
    var cancel = document.createElement('button');
    cancel.type = 'button';
    cancel.className = 'ma-profile-cancel';
    cancel.setAttribute('data-ma-i18n', 'ma_profile_cancel');
    cancel.style.cssText = PROFILE_BTN_CSS;
    row.appendChild(save);
    row.appendChild(cancel);
    panel.appendChild(row);
    area.appendChild(panel);
    save.addEventListener('click', function () { saveProfile(); });
    cancel.addEventListener('click', function () { setPanelOpen(false); });
    applyCopy();
  }

  function setPanelOpen(open) {
    if (open) buildPanel();
    if (!panel) return;
    panel.hidden = !open;
    panel.style.display = open ? 'block' : 'none';
    if (open) fillPanel();
  }

  function isPanelOpen() {
    return Boolean(panel) && panel.style.display !== 'none' && !panel.hidden;
  }

  function fillPanel() {
    if (!profInputs || !curMember) return;
    profInputs.name.value = curMember.name || '';
    var prof = curMember.profile || {};
    profInputs.experience.value = typeof prof.experience === 'string' ? prof.experience : '';
    profInputs.region.value = typeof prof.region === 'string' ? prof.region : '';
    profInputs.bio.value = typeof prof.bio === 'string' ? prof.bio : '';
  }

  function saveProfile() {
    if (!profInputs || !curMember) return;
    var name = profInputs.name.value.trim();
    if (!name || name.length > 100) { showNotice('ma_profile_error'); return; }
    var saveBtn = panel.querySelector('.ma-profile-save');
    if (saveBtn) saveBtn.disabled = true;
    fetch(MA_ENDPOINTS.profile, {
      method: 'PATCH',
      credentials: 'same-origin',
      cache: 'no-store',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        displayName: name,
        profile: {
          experience: profInputs.experience.value.trim(),
          region: profInputs.region.value.trim(),
          bio: profInputs.bio.value.trim()
        }
      })
    }).then(function (res) {
      if (saveBtn) saveBtn.disabled = false;
      if (!res.ok) throw new Error('HTTP ' + res.status);
      showNotice('ma_profile_saved');
      setPanelOpen(false);
      maMeReset(); // forced fresh pull after the profile changed
      return fetchMember().then(render);
    }).catch(function () {
      if (saveBtn) saveBtn.disabled = false;
      showNotice('ma_profile_error');
    });
  }

  // CL-UI-53B: visibility must not depend on the [hidden] attribute alone —
  // shell display rules (.site-nav-more-btn { display:inline-flex } …)
  // override the UA [hidden] rule, which is how the 登出 button stayed
  // visible while signed out. Every element gets an explicit inline
  // style.display (wins over any class rule), the [hidden] attribute for
  // semantics/AT, and the menu additionally a .ma-open class so "open" is
  // a positive, weight-explicit state instead of an attribute absence.
  function setShown(el, show) {
    if (!el) return;
    el.hidden = !show;
    el.style.display = show ? '' : 'none';
    el.classList.toggle('ma-open', Boolean(show));
  }

  function setOpen(open) {
    var show = Boolean(open);
    menu.hidden = !show;
    menu.classList.toggle('ma-open', show);
    menu.style.display = show ? '' : 'none';
    toggle.setAttribute('aria-expanded', show ? 'true' : 'false');
  }

  function isOpen() {
    return !menu.hidden && menu.classList.contains('ma-open');
  }

  // CL-UI-55: the favorites module subscribes to this auth state (login =>
  // cloud favorites re-sync after the server merges the anonymous device list).
  function broadcastAuth(member) {
    try {
      document.dispatchEvent(new CustomEvent('chaselights:auth', { detail: { member: member || null } }));
    } catch (e) { /* old browsers — favorites still boot-time sync */ }
  }

  function render(member) {
    if (!area) return;
    // CL-API-07: a transient /auth/me failure never re-renders — the current
    // member state stands and a backoff retry re-checks later.
    if (member === MA_TRANSIENT) { maScheduleRetry(); return; }
    maRetryAttempt = 0;
    curMember = member;
    broadcastAuth(member);
    var signed = Boolean(member);
    if (!signed && isPanelOpen()) setPanelOpen(false);
    var menuOpen = !signed && area.getAttribute('data-open') === 'true';
    setShown(toggle, !signed);
    setShown(logoutBtn, signed);
    setShown(nameEl, signed);
    if (signed) {
      nameEl.textContent = t('ma_signed_in_as') + '： ' + member.name;
    } else {
      nameEl.textContent = '';
      toggle.textContent = t('ma_login');
    }
    setOpen(menuOpen);
    applyCopy();
  }

  function init() {
    area = document.querySelector('[data-member-area]');
    if (!area) return;
    toggle = area.querySelector('[data-member-toggle]');
    menu = area.querySelector('[data-member-menu]');
    nameEl = area.querySelector('[data-member-name]');
    logoutBtn = area.querySelector('[data-member-logout]');
    if (!toggle || !menu || !nameEl || !logoutBtn) return;

    showAuthErrorNotice();

    // Start endpoints are 302 navigations — plain anchors, never fetched.
    var lineLink = area.querySelector('[data-ma-line]');
    var googleLink = area.querySelector('[data-ma-google]');
    if (lineLink) lineLink.setAttribute('href', MA_ENDPOINTS.line);
    if (googleLink) googleLink.setAttribute('href', MA_ENDPOINTS.google);

    // CL-UI-57: clicking the member name (signed in) expands the profile editor.
    nameEl.style.cursor = 'pointer';
    nameEl.setAttribute('role', 'button');
    nameEl.setAttribute('tabindex', '0');
    nameEl.addEventListener('click', function () {
      if (curMember) setPanelOpen(!isPanelOpen());
    });
    nameEl.addEventListener('keydown', function (e) {
      if (curMember && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        setPanelOpen(!isPanelOpen());
      }
    });

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      if (nameEl.style.display !== 'none' || nameEl.hidden === false) return; // signed in: toggle is hidden anyway
      setOpen(!isOpen());
      area.setAttribute('data-open', isOpen() ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!area.contains(e.target) && isOpen()) {
        setOpen(false);
        area.setAttribute('data-open', 'false');
      }
      if (!area.contains(e.target) && isPanelOpen()) setPanelOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) {
        setOpen(false);
        area.setAttribute('data-open', 'false');
      }
      if (e.key === 'Escape' && isPanelOpen()) setPanelOpen(false);
    });

    logoutBtn.addEventListener('click', function () {
      logoutBtn.disabled = true;
      fetch(MA_ENDPOINTS.logout, {
        method: 'POST',
        credentials: 'same-origin',
        cache: 'no-store'
      }).then(function () {
        logoutBtn.disabled = false;
        maMeReset(); // forced fresh pull after the session changed
        return fetchMember();
      }).then(function (member) {
        area.setAttribute('data-open', 'false');
        render(member);
      }).catch(function () {
        logoutBtn.disabled = false;
      });
    });

    var langSel = document.getElementById('lang-select');
    if (langSel) langSel.addEventListener('change', function () {
      localStorage.setItem('chaselights_lang', langSel.value);
      applyCopy();
      fetchMember().then(render);
    });

    render(null);
    fetchMember().then(render);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
