/* CL-UI-53: homepage member sign-in entry (V1 shell masthead).
   Mirrors apps/web-v2/shell-auth.mjs semantics (CL-APP-02): the start
   endpoints are plain top-level navigations (302 to the OAuth provider), so
   they render as anchors, never fetched; JWTs ride HttpOnly cookies, so
   same-origin fetches to /auth/me carry the session automatically — no token
   handling lives here. Logout is a same-origin POST to /auth/logout.
   Self-contained on purpose, following the guest-comment.js precedent
   (GC_ENDPOINT): the main assets/app.js is heavily test-pinned, so this
   widget ships its own trilingual copy and never edits it.
   Styling reuses the existing site-nav shell classes (.site-nav-more /
   .site-nav-more-btn / .site-nav-menu) — no new stylesheet. */
(function () {
  'use strict';

  var MA_ENDPOINTS = {
    me: '/auth/me',
    logout: '/auth/logout',
    line: '/api/v1/auth/line/start',
    google: '/api/v1/auth/google/start'
  };

  var MA_I18N = {
    'zh-TW': {
      ma_login: '登入',
      ma_logout: '登出',
      ma_line: '使用 LINE 登入',
      ma_google: '使用 Google 登入',
      ma_signed_in_as: '會員'
    },
    'en': {
      ma_login: 'Sign in',
      ma_logout: 'Sign out',
      ma_line: 'Sign in with LINE',
      ma_google: 'Sign in with Google',
      ma_signed_in_as: 'Member'
    },
    'ja': {
      ma_login: 'ログイン',
      ma_logout: 'ログアウト',
      ma_line: 'LINEでログイン',
      ma_google: 'Googleでログイン',
      ma_signed_in_as: '会員'
    }
  };

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

  function render(member) {
    if (!area) return;
    var signed = Boolean(member);
    toggle.hidden = signed;
    menu.hidden = signed || area.getAttribute('data-open') !== 'true';
    toggle.setAttribute('aria-expanded', menu.hidden ? 'false' : 'true');
    logoutBtn.hidden = !signed;
    nameEl.hidden = !signed;
    if (signed) {
      nameEl.textContent = t('ma_signed_in_as') + '： ' + member.name;
    } else {
      nameEl.textContent = '';
      toggle.textContent = t('ma_login');
    }
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

    // Start endpoints are 302 navigations — plain anchors, never fetched.
    var lineLink = area.querySelector('[data-ma-line]');
    var googleLink = area.querySelector('[data-ma-google]');
    if (lineLink) lineLink.setAttribute('href', MA_ENDPOINTS.line);
    if (googleLink) googleLink.setAttribute('href', MA_ENDPOINTS.google);

    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      if (nameEl.hidden === false) return; // signed in: toggle is hidden anyway
      var open = menu.hidden;
      menu.hidden = !open;
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!area.contains(e.target) && !menu.hidden) {
        menu.hidden = true;
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) {
        menu.hidden = true;
        toggle.setAttribute('aria-expanded', 'false');
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
