/* CL-APP-09 追加2 steer ② — card-list custom-subject verdict LAZY LOADER.
   Self-contained asset (custom-places.js / member-auth.js precedent): own
   tri-lingual pack, zero dependency on app.js internals.

   Contract (追加2 rulings):
   - the card list page consumes the ONE batch endpoint
     GET /api/v1/subject_sets/eval_batch?ids=<≤200 place ids>&cursor=<n>
     — never per-card-per-set calls (steer 2);
   - VISIBLE RANGE FIRST: cards are observed with an IntersectionObserver;
     ids of cards near/inside the viewport are fetched first (one page =
     ≤20 places, payload-paginated by the 追加2 ③ server caps);
   - pages continue while the user scrolls (next_cursor), each page is a
     single-flight request; 429/5xx/disconnect are TRANSIENT (house rule):
     keep the official card intact, exponential backoff, retry the page;
   - rendering: verdict lines land in a dedicated slot on each card
     ([data-custom-sets], appended under .shooting-summary when absent);
     「自訂」 badge is GRAY (identity, never ✓○✗ semantic colors), the
     verdict glyph itself reuses the shared tier semantics (✓推薦/○可拍/✗短原因);
   - the loader NEVER blocks the page: official content renders regardless;
     with no custom sets the slot stays empty and nothing is fetched.

   Integration (the only two hooks needed):
     CLSubjectSetsList.init(function getPlaceIds(){ return [...ids of cards currently in the DOM, viewport-near first]; });
     CLSubjectSetsList.reset();  // after re-render / filter / date change
*/
(function () {
  'use strict';
  var API = '/api/v1/subject_sets/eval_batch';
  var MAX_IDS_PER_REQUEST = 200; // server rejects more (追加2 ③)
  var LANGS = ['zh-TW', 'en', 'ja'];
  var T = {
    'zh-TW': { badge: '自訂', none_hour: '今日無符合時段', fail: '✗', ok: '✓' },
    'en': { badge: 'Custom', none_hour: 'No qualifying hours today', fail: '✗', ok: '✓' },
    'ja': { badge: '自作', none_hour: '本日適合する時間帯なし', fail: '✗', ok: '✓' },
  };
  function lang() {
    try {
      var k = null;
      if (typeof window.CLMemberAuth !== 'undefined' && window.CLMemberAuth.lang) k = window.CLMemberAuth.lang;
      if (!k) k = localStorage.getItem('chaselights_lang') || (navigator.language || 'zh-TW');
      if (LANGS.indexOf(k) < 0) k = k && k.indexOf('ja') === 0 ? 'ja' : (k && k.indexOf('zh') === 0 ? 'zh-TW' : 'en');
      return k;
    } catch (e) { return 'zh-TW'; }
  }

  var S = {
    ids: [],            // ordered place ids (viewport-near first)
    els: {},            // placeId -> card element
    fetched: {},        // placeId -> true once covered by a page
    verdicts: {},       // placeId -> [{id,name,tier,window,failReason,days}]
    nextCursor: 0,
    pendingPage: null,  // ids for the page currently being fetched (dedupe/retry)
    inflight: false,
    backoffMs: 1000,
    exhausted: false,   // no more pages
    observer: null,
    getIds: null,
  };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  // ---- page fetch ------------------------------------------------------
  function loadNextPage() {
    if (S.inflight || S.exhausted) return Promise.resolve();
    // up to 20 places per page that are still unfetched, in priority order
    var page = [];
    for (var i = 0; i < S.ids.length && page.length < 20; i++) {
      var id = S.ids[i];
      if (!S.fetched[id]) page.push(id);
    }
    if (!page.length) return Promise.resolve();
    S.inflight = true;
    S.pendingPage = page;
    var q = API + '?ids=' + encodeURIComponent(page.join(','));
    if (S.nextCursor) q += '&cursor=' + S.nextCursor;
    return fetch(q, { credentials: 'same-origin' })
      .then(function (r) {
        if (r.status === 429 || r.status >= 500) throw new Error('transient ' + r.status); // backoff + retry (house rule)
        if (!r.ok) throw new Error('batch eval ' + r.status);
        return r.json();
      })
      .then(function (b) {
        S.backoffMs = 1000;
        if (!b || !b.ok) throw new Error('batch eval payload');
        (b.results || []).forEach(function (row) {
          S.fetched[row.place_id] = true;
          S.verdicts[row.place_id] = row.sets || [];
          render(row.place_id);
        });
        // server returns next_cursor for the VALIDATED id list — resume there
        if (b.page && b.page.next_cursor != null) {
          S.nextCursor = b.page.next_cursor;
        } else if (b.page && b.page.next_cursor === null) {
          // page done: everything still unfetched after this point waits for
          // the next visible-range scheduling pass (ids may have been added)
          S.nextCursor = 0;
          var anyLeft = S.ids.some(function (id) { return !S.fetched[id]; });
          S.exhausted = !anyLeft;
        }
        S.inflight = false;
        if (!S.exhausted) maybeFetchForVisible();
      })
      .catch(function (e) {
        S.inflight = false;
        // transient: retry the SAME page later with exponential backoff;
        // official card content is untouched (never blocks the page)
        if (S.backoffMs < 16000) {
          setTimeout(function () { loadNextPage(); }, S.backoffMs);
          S.backoffMs *= 2;
        }
      });
  }

  function maybeFetchForVisible() {
    if (S.inflight || S.exhausted) return;
    var need = S.ids.some(function (id, i) {
      return i < 20 && !S.fetched[id] && S.els[id] && isVisible(S.els[id]);
    });
    if (need) loadNextPage();
  }

  function isVisible(el) {
    if (!el || !el.isConnected) return false;
    var r = el.getBoundingClientRect();
    return r.bottom > -200 && r.top < (window.innerHeight || 800) + 200;
  }

  // ---- rendering -------------------------------------------------------
  function shortSetLine(v, d) {
    var head = esc(v.name || (d ? d.badge : ''));
    var glyph, cls, tail;
    if (v.tier === 'rec') {
      glyph = '✓'; cls = 'cl-ss-ok';
      tail = v.window && v.window.hours && v.window.hours.length
        ? esc(v.window.hours[0]) + (v.window.hours.length > 1 ? '+' : '') : '';
    } else if (v.tier === 'pending') {
      glyph = '…'; cls = 'cl-ss-pending'; tail = '';
    } else {
      glyph = '✗'; cls = 'cl-ss-no';
      tail = v.failReason ? esc(v.failReason) : '';
    }
    return '<span class="cl-ss-line ' + cls + '"><span class="cl-ss-badge">' + esc(d.badge) + '</span>' +
      '<span class="cl-ss-name">' + head + '</span>' +
      '<span class="cl-ss-verdict">' + glyph + (tail ? ' ' + tail : '') + '</span></span>';
  }

  function render(placeId) {
    var el = S.els[placeId];
    var sets = S.verdicts[placeId];
    if (!el || !el.isConnected) return;
    var d = T[lang()] || T['zh-TW'];
    var slot = el.querySelector('[data-custom-sets]');
    if (!slot) {
      var anchor = el.querySelector('.shooting-summary') || el.querySelector('.card-header');
      if (!anchor) return;
      slot = document.createElement('div');
      slot.setAttribute('data-custom-sets', '');
      slot.className = 'cl-ss-slot';
      anchor.parentNode.insertBefore(slot, anchor.nextSibling);
    }
    if (!sets || !sets.length) { slot.innerHTML = ''; return; }
    slot.innerHTML = sets.slice(0, 5).map(function (v) { return shortSetLine(v, d); }).join('');
    slot.classList.add('cl-ss-loaded');
  }

  // ---- registration ----------------------------------------------------
  function register(placeId, el) {
    if (!placeId || !el) return;
    if (S.els[placeId] !== el) S.els[placeId] = el;
  }

  function refresh(getIds) {
    if (typeof getIds === 'function') S.getIds = getIds;
    var ids = [];
    try { ids = (S.getIds ? S.getIds() : []) || []; } catch (e) { ids = []; }
    // visible-range-first ordering: connected + visible cards first, then the rest
    var vis = [], rest = [];
    ids.slice(0, MAX_IDS_PER_REQUEST).forEach(function (id) {
      // self-registration: the caller only supplies ids — the loader finds the
      // card element itself (app.js cards carry data-place-id)
      var el = S.els[id];
      if (!el || !el.isConnected) {
        try { el = document.querySelector('.card[data-place-id="' + id + '"]') || null; } catch (e) { el = null; }
        if (el) S.els[id] = el;
      }
      if (el && el.isConnected) (isVisible(el) ? vis : rest).push(id);
      else rest.push(id);
    });
    S.ids = vis.concat(rest.filter(function (id) { return vis.indexOf(id) < 0; }));
    S.exhausted = false;
    maybeFetchForVisible();
  }

  function reset() {
    S.ids = []; S.els = {}; S.fetched = {}; S.verdicts = {};
    S.nextCursor = 0; S.pendingPage = null; S.inflight = false;
    S.backoffMs = 1000; S.exhausted = false;
  }

  window.CLSubjectSetsList = {
    init: function (getIds) {
      refresh(getIds);
      if (!S.observer) {
        S.observer = new IntersectionObserver(function () { maybeFetchForVisible(); }, { rootMargin: '200px 0px' });
        window.addEventListener('scroll', function () { maybeFetchForVisible(); }, { passive: true });
      }
    },
    register: register,
    refresh: refresh,
    reset: reset,
  };
})();
