/* CL-UI-55: cloud favorites client for the V1 shell.
   Mirrors the member-auth.js / guest-comment.js precedent: self-contained,
   ships its own trilingual copy, never edits the heavily test-pinned
   assets/app.js beyond the two-line hook that routes card-star toggles and
   cloud merges through this module (window.ChaseLightsFavorites).

   Backend contract (workers/api/src/index.js, CL-API-02/05):
   - GET  /api/v1/favorites[?userId=<device-id>] -> { userId, favorites:[{place_id,created_at}] }
   - POST /api/v1/favorites { placeId, action:"add"|"remove", userId? } -> { ok }
   - Authorization Bearer/session cookie takes precedence; the legacy userId
     param stays as the anonymous mode. Anonymous identity is a client-persisted
     device id (localStorage + a first-party cookie for continuity).
   - Anonymous favorites are re-keyed onto the member account server-side at
     login (mergeAnonDevice), so the client only re-pulls the cloud list when
     the auth state changes.

   Failure posture: the cloud call never blocks the card star — the local
   chaselights_favs_v2 list is already updated by app.js, so a network failure
   simply falls back to that local list and shows a trilingual notice.
*/
(function () {
  'use strict';

  var FAV_ENDPOINT = '/api/v1/favorites';
  var DEVICE_KEY = 'chaselights_device_id';
  var DEVICE_COOKIE = 'chaselights_device';
  var LOCAL_FAVS_KEY = 'chaselights_favs_v2';

  var I18N = {
    'zh-TW': { fav_offline: '收藏暫時無法同步，已保存在此裝置。', fav_saved: '已同步到我的最愛。' },
    'en': { fav_offline: 'Favorites could not be synced; saved on this device.', fav_saved: 'Synced to your favorites.' },
    'ja': { fav_offline: 'お気に入りを同期できませんでした。この端末に保存しました。', fav_saved: 'お気に入りに同期しました。' }
  };

  function lang() {
    var sel = document.getElementById('lang-select');
    var v = (sel && typeof sel.value === 'string' && sel.value) ||
            (function () { try { return localStorage.getItem('chaselights_lang'); } catch (e) { return null; } }()) || 'zh-TW';
    return I18N[v] ? v : 'zh-TW';
  }
  function t(key) { var p = I18N[lang()]; return (p && p[key]) || I18N['zh-TW'][key] || ''; }

  var notice = null, noticeTimer = null;
  function showNotice(key) {
    try {
      if (!notice) {
        notice = document.createElement('p');
        notice.className = 'fav-notice';
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

  function localFavorites() {
    try {
      var v = JSON.parse(localStorage.getItem(LOCAL_FAVS_KEY) || '[]');
      return Array.isArray(v) ? v.filter(function (x) { return typeof x === 'string' && x; }) : [];
    } catch (e) { return []; }
  }

  function deviceId() {
    var id = null;
    try { id = localStorage.getItem(DEVICE_KEY); } catch (e) { /* storage blocked */ }
    if (!id) {
      try { id = crypto.randomUUID ? crypto.randomUUID() : 'dev-' + Date.now() + '-' + Math.random().toString(36).slice(2); }
      catch (e) { id = 'dev-' + Date.now(); }
      try { localStorage.setItem(DEVICE_KEY, id); } catch (e) { /* keep session-only id */ }
    }
    try { document.cookie = DEVICE_COOKIE + '=' + encodeURIComponent(id) + ';max-age=31536000;path=/;SameSite=Lax'; } catch (e) { /* cookie blocked */ }
    return id;
  }

  function broadcast(ids, member) {
    try { document.dispatchEvent(new CustomEvent('chaselights:favorites', { detail: { ids: ids, member: member === undefined ? null : member } })); } catch (e) { /* old browsers */ }
  }

  function fetchCloud() {
    return fetch(FAV_ENDPOINT + '?userId=' + encodeURIComponent(deviceId()), {
      credentials: 'same-origin', cache: 'no-store'
    }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    }).then(function (doc) {
      if (!doc || !Array.isArray(doc.favorites)) return [];
      return doc.favorites.map(function (row) { return row && typeof row.place_id === 'string' ? row.place_id : null; })
        .filter(function (x) { return x; });
    });
  }

  function push(placeId, action) {
    return fetch(FAV_ENDPOINT, {
      method: 'POST',
      credentials: 'same-origin',
      cache: 'no-store',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ placeId: placeId, action: action, userId: deviceId() })
    }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return true;
    });
  }

  // Called by app.js after the local list is already updated. Cloud success
  // refreshes the merged set; any failure falls back to the local list with
  // a trilingual notice.
  function toggle(placeId, adding) {
    return push(placeId, adding ? 'add' : 'remove').then(function () {
      return fetchCloud();
    }).then(function (ids) { broadcast(ids); return ids; })
      .catch(function () { showNotice('fav_offline'); return localFavorites(); });
  }

  // First-launch bootstrap + login resync: upload every local favorite that
  // the cloud list lacks (POST add is idempotent), then broadcast the merged
  // cloud set so the 我的最愛 filter renders from it.
  function syncLocal() {
    return fetchCloud().then(function (cloud) {
      var local = localFavorites();
      var missing = local.filter(function (id) { return cloud.indexOf(id) === -1; });
      var done = Promise.resolve();
      missing.forEach(function (id) {
        done = done.then(function () { return push(id, 'add').catch(function () { /* per-item best-effort */ }); });
      });
      return done.then(function () { return fetchCloud(); }).then(function (ids) {
        if (missing.length) showNotice('fav_saved');
        broadcast(ids);
        return ids;
      });
    }).catch(function () {
      // Offline: keep the local list as-is, no silent data loss.
      broadcast(localFavorites());
      return localFavorites();
    });
  }

  // Auth-state subscription (member-auth.js dispatches chaselights:auth):
  // after a login the server has merged the anonymous favorites into the
  // member account, so re-pull the cloud list; after logout fall back to the
  // anonymous device list.
  document.addEventListener('chaselights:auth', function (e) { onAuth(e); });

  // CL-UI-57: while signed in, the device-local chaselights_favs_v2 cache is
  // the MEMBER's merged list. On a signed-in -> signed-out transition it must
  // be dropped, never re-synced or re-displayed: the cloud copy already lives
  // on the account, and keeping it here would (a) leak the previous account's
  // favorites into the anonymous device list on the next upload and (b) render
  // them as "my favorites" after logout. The server's anonymous device list is
  // the only source of truth for signed-out state.
  var wasAuthed = false;
  function onAuth(e) {
    var member = (e && e.detail && e.detail.member) ? e.detail.member : null;
    var authed = Boolean(member);
    if (wasAuthed && !authed) {
      try { localStorage.removeItem(LOCAL_FAVS_KEY); } catch (err) { /* storage blocked */ }
    }
    wasAuthed = authed;
    syncLocal();
  }

  window.ChaseLightsFavorites = {
    toggle: toggle,
    syncLocal: syncLocal,
    fetchCloud: fetchCloud,
    deviceId: deviceId,
    localFavorites: localFavorites
  };

  function init() { syncLocal(); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
