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
    logout: '/api/v1/auth/logout',
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
      ma_auth_error: '登入失敗，請重試'
    },
    'en': {
      ma_login: 'Sign in',
      ma_logout: 'Sign out',
      ma_line: 'Sign in with LINE',
      ma_google: 'Sign in with Google',
      ma_signed_in_as: 'Member',
      ma_auth_error: 'Sign in failed, please try again'
    },
    'ja': {
      ma_login: 'ログイン',
      ma_logout: 'ログアウト',
      ma_line: 'LINEでログイン',
      ma_google: 'Googleでログイン',
      ma_signed_in_as: '会員',
      ma_auth_error: 'ログインに失敗しました。もう一度お試しください'
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
    var raw = doc.display_name != null ? doc.display_name :
              (doc.name != null ? doc.name : (doc.sub != null ? doc.sub : null));
    if (typeof raw !== 'string') return null;
    var name = raw.trim();
    if (!name) return null;
    var provider = (typeof doc.provider === 'string' && doc.provider.trim()) ? doc.provider.trim() : null;
    return { name: name, provider: provider };
  }

  function fetchMember() {
    return fetch(MA_ENDPOINTS.me, { credentials: 'same-origin', cache: 'no-store' })
      .then(function (res) { return res.ok ? res.json() : null; })
      .then(function (doc) { return parseMember(doc); })
      .catch(function () { return null; });
  }

  var area, toggle, menu, nameEl, logoutBtn;

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
    broadcastAuth(member);
    var signed = Boolean(member);
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
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) {
        setOpen(false);
        area.setAttribute('data-open', 'false');
      }
    });

    logoutBtn.addEventListener('click', function () {
      logoutBtn.disabled = true;
      fetch(MA_ENDPOINTS.logout, {
        method: 'POST',
        credentials: 'same-origin',
        cache: 'no-store'
      }).then(function () {
        logoutBtn.disabled = false;
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
