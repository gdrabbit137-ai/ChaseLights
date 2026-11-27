// CL-APP-06: custom places (private points) — homepage single-list UI.
// (1) Source contract: tags+stamps on index.html, honest markers in the
//     self-contained asset, gray-identity CSS, tri-lingual parity.
// (2) Headless behavior (lazy-boot raw-CDP harness, cl-ui-47 pattern —
//     NO root test.before): stubbed /api/v1/custom_places fixture drives
//     quota chip + honest count + private cards; real assertions on
//     COMPUTED visibility at 1280 and 390; screenshots for the mockup
//     comparison (data/v2/audits/design-mockups/mockup-custom-places.html).
// Run: node --test apps/web-v2/tests/cl-app-06-custom-places.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';
import { mkdtempSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const htmlSource = readFileSync(join(WEB, 'index.html'), 'utf8');
const jsSource = readFileSync(join(WEB, 'assets', 'custom-places.js'), 'utf8');
const cssSource = readFileSync(join(WEB, 'assets', 'custom-places.css'), 'utf8');

// ------------------------------------------------------------- (1) source
test('CL-APP-06 (1a): index.html carries the asset tags with their own cache-bust stamp', () => {
  // CL-INT-206 merge: clapp06g (patch-8) + clapp08a (shared-fetch tag) ->
  // clapp08b on the merged tree; CL-APP-09-p3 (popup anatomy) -> clapp09e;
  // CL-APP-09 patch-4 (popup rides the official renderers) -> clapp09g
  // (per-file cache-bust rule, monotonic)
  assert.match(htmlSource, /assets\/custom-places\.css\?v=clapp09g/);
  assert.match(htmlSource, /assets\/custom-places\.js\?v=clapp09n/); // CL-APP-09 patch-5/6 stamp advance (CL-INT-212 re-anchor)
  assert.doesNotMatch(htmlSource, /custom-places\.(css|js)\?v=clapp08b/);
  assert.match(htmlSource, /assets\/vendor\/maplibre-gl\.css\?v=clapp06f/);
  // untouched neighbors keep their stamps (per-file cache-bust rule)
  // CL-INT-190: clui101 -> clui102 re-anchored (CL-INT-187 favicon stamp bump on main during merge)
  assert.match(htmlSource, /assets\/app\.js\?v=clui142/);
});

test('CL-APP-06 (1b): the asset is self-contained and owner-ruled-honest', () => {
  // single-list gray identity — the ONLY badge, never a semantic color
  assert.match(jsSource, /cl-cp-priv-badge/);
  assert.match(jsSource, /v_all[\s\S]{0,40}v_official[\s\S]{0,40}v_private/);
  // trial expired: data kept, evaluation stopped, honest label + CTA
  assert.match(jsSource, /trial_expired/);
  assert.match(jsSource, /cl-cp-expired/);
  assert.match(jsSource, /trial_cta/);
  // per-user daily fetch budget honesty (owner layer 3)
  assert.match(jsSource, /fetchDeferred/);
  assert.match(jsSource, /明日更新|updates tomorrow|明日更新/);
  // patch-6 (owner ruling): 提名升級官方 is GONE — no nominate modal, menu
  // item or dict key may remain in the asset; backend endpoint is kept but
  // no longer exposed anywhere in the UI
  assert.doesNotMatch(jsSource, /nomModal|m_nom|nom_title|nom_btn|cl-cp-nom/);
  assert.match(jsSource, /30 天|30 days|30 日/);
  // member gating: signed-out users get the login notice, never a silent action
  assert.match(jsSource, /needLoginModal/);
  // member-auth integration via the chaselights:auth broadcast
  assert.match(jsSource, /chaselights:auth/);
  // test seam used by this harness (stubbed network)
  assert.match(jsSource, /__clcpFetch/);
  // patch-8: multi-theme — list manager, per-place cap 5, dup names NOT blocked,
  // per-group card rows in the official subject-row anatomy, theme CRUD endpoints
  assert.match(jsSource, /themeGroups/);
  assert.match(jsSource, /cl-cp-theme-row/);
  assert.match(jsSource, /\/themes/, 'theme CRUD endpoints are called by the manager');
  assert.match(jsSource, /waitThemeList/);
  assert.match(jsSource, /th_cap_note/);
  assert.match(jsSource, /th_name_required/);
  assert.match(jsSource, /cap\) \|\| 5/, 'the UI honours the worker-reported 5-group cap');
  const workerSrc8 = readFileSync(join(WEB, 'workers', 'api', 'src', 'custom-places.js'), 'utf8');
  assert.match(workerSrc8, /MAX_THEMES_PER_PLACE = 5/);
  assert.match(workerSrc8, /handleCustomPlaceThemes/);
  assert.match(workerSrc8, /loadThemeGroups/);
  assert.match(workerSrc8, /題材 1/, 'legacy single set migrates into ONE named group');
  assert.match(workerSrc8, /evaluateThemeGroups/);
  assert.match(workerSrc8, /aggregateEvaluation/);
  assert.match(readFileSync(join(WEB, 'migrations', '0012_custom_place_themes.sql'), 'utf8'), /CREATE TABLE IF NOT EXISTS custom_place_themes/);
  // 📍 current-location: browser Geolocation API + Capacitor plugin fallback,
  // one implementation, honest no-tracking note, bounded timeout
  assert.match(jsSource, /__clcpGeo/);
  assert.match(jsSource, /useMyLocation/);
  assert.match(jsSource, /navigator\.geolocation\.getCurrentPosition\(resolve, reject, opts\)/);
  assert.match(jsSource, /cap\.Plugins\.Geolocation/);
  assert.match(jsSource, /timeout: 10000/);
  assert.match(jsSource, /不會追蹤你的行蹤|never tracked|追跡しません/);
});

// ------------------------------------------------- (1d) CL-APP-08 grid dedup
test('CL-APP-08 (1d): shared-fetch tag 「與 ○○○ 共用資料」 + 獨立重新抓取 escape hatch', () => {
  // the shared tag: gray identity, rendered from the API's sharing info
  assert.match(jsSource, /shareTagText/);
  assert.match(jsSource, /share_one[\s\S]{0,60}與 \{n\} 共用資料/);
  assert.match(jsSource, /share_many[\s\S]{0,60}共用資料/);
  assert.match(jsSource, /cl-cp-share-tag/);
  // tri-lingual parity for the tag + the escape-hatch menu item (anchored to
  // each language block, not just anywhere in the file)
  for (const lang of ["'zh-TW': {", "'en': {", "'ja': {"]) {
    const rx = new RegExp(`${lang.replace(/[-']/g, (c) => '\\' + c)}[\\s\\S]{0,3200}m_refetch`);
    assert.match(jsSource, rx, `${lang} carries the 獨立重新抓取 menu item`);
    const rx2 = new RegExp(`${lang.replace(/[-']/g, (c) => '\\' + c)}[\\s\\S]{0,3200}refetch_done`);
    assert.match(jsSource, rx2, `${lang} carries the refetch toast copy`);
  }
  assert.match(jsSource, /m_refetch/);
  assert.match(jsSource, /refetchIndependent/);
  assert.match(jsSource, /\/refetch/, 'calls the POST /custom_places/:id/refetch endpoint');
  // gray identity: the tag never borrows the ✓○✗ semantic colors
  const tag = cssSource.slice(cssSource.indexOf('.cl-cp-share-tag'), cssSource.indexOf('.cl-cp-card.cl-cp-expired'));
  assert.match(tag, /var\(--cl-text-2\)/);
  assert.doesNotMatch(tag, /--cl-(green|amber|red)-text/);
});

test('CL-APP-06 (1c): gray identity CSS never borrows the ✓○✗ semantic colors', () => {
  assert.match(cssSource, /\.cl-cp-priv-badge[^}]*var\(--cl-grey-bg\)/);
  assert.match(cssSource, /\.cl-cp-priv-badge[^}]*var\(--cl-grey-text\)/);
  // the badge class must not set green/amber/red text colors
  const badge = cssSource.slice(cssSource.indexOf('.cl-cp-priv-badge'), cssSource.indexOf('.cl-cp-coord'));
  assert.doesNotMatch(badge, /--cl-(green|amber|red)-text/);
  // view filtering is class/attribute driven (never the [hidden] attribute —
  // shell display rules would override it)
  assert.match(cssSource, /body\[data-cp-view="official"\]/);
  assert.match(cssSource, /body\[data-cp-view="private"\]/);
});

test('CL-APP-06 (1c-2, patch-2): the modal is height-bounded + internally scrollable at ANY window height', () => {
  // owner bug: the popup grew taller than the window and the name field was
  // clipped, so 「建立私人點」 stayed disabled — the user was stuck.
  const modal = cssSource.slice(cssSource.indexOf('.cl-cp-modal{'), cssSource.indexOf('.cl-cp-m-head'));
  assert.match(modal, /max-height:\s*calc\(100vh\s*-\s*var\(--cl-sp-6\)\s*\*\s*2\)/,
    'desktop modal height ≤ window minus the overlay padding');
  assert.match(modal, /overflow-y:\s*auto/, 'the modal scrolls INTERNALLY (overlay no longer the only scroller)');
  // mobile sheet: exactly the window height, internal scroll
  const mq = cssSource.slice(cssSource.indexOf('@media (max-width:700px)'));
  assert.match(mq, /max-height:100vh/, '390px sheet: min=max=100vh — never taller than the window');
  // the name field is the first field and auto-focuses (focus also scrolls it into view)
  assert.match(jsSource, /#cl-cp-name[\s\S]{0,120}\.focus\(\)/, 'name field auto-focuses on open');
  // the disabled button shows the reason on itself, not just gray
  assert.match(jsSource, /reason_name/);
  assert.match(jsSource, /reason_pin/);
  assert.match(jsSource, /updateSubmitState/);
  assert.match(jsSource, /請先輸入景點名稱/);
});

test('CL-APP-06 (1d): tri-lingual dictionary parity in the asset', () => {
  const keys = ['priv_badge', 'v_all', 'v_official', 'v_private', 'trial_expired', 'trial_note',
    'deferred_note', 'm_edit', 'm_cc', 'm_del', 'add_title', 'ro_elev', 'ro_tz',
    'del_title', 'count_fmt',
    // 📍 current-location copy must exist in ALL three dictionaries
    'geo_btn', 'geo_note', 'geo_working', 'geo_denied', 'geo_timeout', 'geo_error',
    // patch-2: disabled-button reason copy must exist in ALL three dictionaries
    'reason_name', 'reason_pin',
    // patch-4: mini-map honest loading copy; patch-5: conflict + months copy
    'pin_map_loading', 'ai_conflict', 'p_months', 'p_months_hint',
    // patch-7: private-card forecast popup (quick view / 8-day strip / subjects)
    'qv_title', 'qv_quick', 'qv_days', 'qv_no_data', 'qv_no_data_note', 'qv_subjects',
    // patch-9: qv_baseline removed (dual-truth residue); qv_general + the
    // official 「條件 ×{n}」 collapse copy are tri-lingual
    'qv_subject_custom', 'qv_general', 'qv_entry', 'qv_load_fail', 'qv_gen',
    'cond_n', 'cond_required',
    // patch-8: theme list manager + per-theme form (trilingual)
    'th_title', 'th_sub', 'th_add', 'th_cap_note', 'th_empty', 'th_count',
    'th_name', 'th_name_ph', 'th_name_required', 'th_del_title',
    'th_create', 'th_save', 'th_done1', 'th_deleted', 'th_row_shoot', 'qv_month_note'];
  for (const lang of ['zh-TW', 'en', 'ja']) {
    const block = jsSource.slice(jsSource.indexOf(`'${lang}':`), jsSource.indexOf(`'${lang}':`) + 8000);
    for (const key of keys) assert.ok(new RegExp(`\\b${key}:`).test(block), `${lang} missing ${key}`);
  }
});

test('CL-APP-06 (1e): conditions form — semantic dropdowns with transparent hardcoded mapping + genre starters + advanced raw inputs', () => {
  // ① trilingual hardcoded option→value mapping (deterministic, zero cost)
  assert.match(jsSource, /越少越好[\s\S]{0,200}低雲 ≤20%/);
  assert.match(jsSource, /完全不能有霧[\s\S]{0,200}能見度 ≥10km/);
  assert.match(jsSource, /不能下雨[\s\S]{0,200}降水 <0\.2/);
  assert.match(jsSource, /'en':[\s\S]{0,300}As little as possible/);
  assert.match(jsSource, /'ja':[\s\S]{0,300}できるだけ少ない/);
  // the mapped RESULT is shown to the user (transparent), synced into the
  // concrete advanced inputs (single source of truth the form submits)
  assert.match(jsSource, /cl-cp-sem-map/);
  assert.match(jsSource, /→ '/);
  assert.match(jsSource, /inp\.value = mapped == null \? '' : String\(mapped\)/);
  // ② official genre copy starters (21 general genres)
  assert.match(jsSource, /CC_GENRE_STARTERS/);
  assert.match(jsSource, /copy_genre/);
  // ③ advanced raw numeric inputs stay (power user), collapsed by default
  assert.match(jsSource, /cl-cp-cc-advanced/);
  assert.match(jsSource, /adv_toggle/);
  // patch-8: the form submits a THEME GROUP — name + i18n + concrete conditions
  assert.match(jsSource, /payload = \{ name: name, nameI18n: i18n, conditions: readCc\(\) \}/);
});

const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs, ready;
let loadEvents = 0; // Page.loadEventFired counter (CL-INT-190: evaluate may land on the STALE page before a navigation commits)
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

const CP_PAGE_STUB = `try { localStorage.removeItem('chaselights_cp_view'); } catch (e) { /* storage blocked */ }
      
      // patch-4: pin-picker mini-map is DISABLED in this harness (deterministic
      // schematic fallback) — the real-MapLibre path is covered by test (2r)
      // which clears this flag at runtime.
      window.__clcpMapLibre = false;
      // patch-8: per-place theme groups (multi-theme) — a small in-memory
      // CRUD store the manager modal exercises end-to-end (create / rename /
      // delete / duplicate names all pass through the real client paths)
      var __cpThemes = [
        { id: 'tg1', placeId: 'cp1', name: '雲海窗', nameI18n: { 'zh-TW': '雲海窗' },
          conditions: { cloud_low_max: 15, window_start: '04:30', window_end: '07:00' },
          evaluation: { tier: 'rec', reason: null, window: '2026-11-16 05:00' } },
        { id: 'tg3', placeId: 'cp3', name: '風平窗', nameI18n: null,
          conditions: { wind_max_ms: 5 },
          evaluation: { tier: 'no', reason: '風強', window: null } },
        // patch-9: a LEGACY group — the worker's lazy migration auto-named the
        // old single blob 「題材 1」 with no nameI18n. Display must never show
        // the placeholder: this set is an EXACT night_sky starter match → 星空.
        { id: 'tg9', placeId: 'cp6', name: '題材 1', nameI18n: null,
          conditions: { cloud_low_max: 20, visibility_min_km: 10, precip_max_mmh: 0.2, window_start: '21:00', window_end: '03:00' },
          evaluation: { tier: 'rec', reason: null, window: '2026-11-16 21:00' } },
      ];
      var __cpThemeSeq = 0;
      var __cpPlaces = [
        { id: 'cp1', name: '霧社水庫西岸岔路', lat: 23.9412, lng: 121.1523, elevation: 1150, timezone: 'Asia/Taipei',
          customConditions: { cloud_low_max: 15, visibility_min_km: 12, window_start: '04:30', window_end: '07:00' },
          status: 'active', createdAt: '', updatedAt: '',
          evaluation: { tier: 'rec', reason: null, window: '2026-11-16 05:00', evaluatedAt: '2026-11-15T10:00:00Z', private: true },
          refresh: { intervalHours: 6, label: '6h', energySaver: false }, fetchDeferred: false, fetchDueAt: null },
        { id: 'cp2', name: '礁溪自家陽台展望', lat: 24.8225, lng: 121.7675, elevation: 80, timezone: 'Asia/Taipei',
          customConditions: null,
          status: 'active', createdAt: '', updatedAt: '',
          evaluation: { tier: 'shoot', reason: null, window: '2026-11-16 06:00', evaluatedAt: '2026-11-15T10:00:00Z', private: true },
          refresh: { intervalHours: 6, label: '6h', energySaver: false }, fetchDeferred: false, fetchDueAt: null },
        { id: 'cp3', name: '苫小牧西港堤防燈點', lat: 42.6389, lng: 141.3556, elevation: 3, timezone: 'Asia/Tokyo',
          customConditions: { wind_max_ms: 5 },
          status: 'active', createdAt: '', updatedAt: '',
          evaluation: { tier: 'no', reason: '風強', window: null, evaluatedAt: '2026-11-15T10:00:00Z', private: true },
          refresh: { intervalHours: 6, label: '6h', energySaver: false }, fetchDeferred: false, fetchDueAt: null },
        { id: 'cp4', name: '試用期滿的點', lat: 35.0, lng: 138.0, elevation: 100, timezone: 'Asia/Tokyo',
          customConditions: null, status: 'trial_expired', createdAt: '', updatedAt: '',
          evaluation: { tier: 'pending', reason: null, window: null, evaluatedAt: null, private: true },
          refresh: { intervalHours: 6, label: '6h', energySaver: false }, fetchDeferred: false, fetchDueAt: null },
        { id: 'cp5', name: '明日補抓的點', lat: 25.0, lng: 122.0, elevation: null, timezone: null,
          customConditions: null, status: 'active', createdAt: '', updatedAt: '',
          evaluation: { tier: 'pending', reason: null, window: null, evaluatedAt: null, private: true },
          refresh: { intervalHours: 6, label: '6h', energySaver: false }, fetchDeferred: true, fetchDueAt: '2026-11-16 00:05:00' },
        // patch-9: carries the legacy auto-named group (see __cpThemes tg9)
        { id: 'cp6', name: '合歡北峰瞭望台', lat: 24.14, lng: 121.27, elevation: 3200, timezone: 'Asia/Taipei',
          customConditions: null, status: 'active', createdAt: '', updatedAt: '',
          evaluation: { tier: 'rec', reason: null, window: '2026-11-16 21:00', evaluatedAt: '2026-11-15T10:00:00Z', private: true },
          refresh: { intervalHours: 6, label: '6h', energySaver: false }, fetchDeferred: false, fetchDueAt: null },
      ];
      var __cpThemeCap = 5;
      // CL-APP-08: shared-fetch groups (same-member grid dedup) — cp1 is the
      // group representative, cp2 rides its fetch; the card shows the
      // 「與 ○○○ 共用資料」 tag from the list payload's sharing field.
      var __cpShare = {
        cp1: { groupId: 'g:cp1', representativeId: 'cp1', isRepresentative: true, shareMode: 'auto',
          sharedWith: [{ id: 'cp2', name: '礁溪自家陽台展望' }] },
        cp2: { groupId: 'g:cp1', representativeId: 'cp1', isRepresentative: false, shareMode: 'auto',
          sharedWith: [{ id: 'cp1', name: '霧社水庫西岸岔路' }] },
      };
      window.__cpThemes = __cpThemes; // test seam: the harness inspects the store
      window.__clcpFetch = function (path, opts) {
        if (path.indexOf('/api/v1/custom_places/pin_info') === 0) {
          return Promise.resolve({ ok: true, status: 200, json: function () {
            return Promise.resolve({ ok: true, elevation: 80, timezone: 'Asia/Taipei', utcOffsetSeconds: 28800, elevationOutlier: false });
          } });
        }
        // patch-7: the private-card forecast popup reads the stored eval.
        // patch-4: the fixture's hourly grid is DATE-ANCHORED to the real
        // spot-local today (the official quick view renders the page-selected
        // date = today), with clean-air hours inside the group's 04:30–07:00
        // window and low cloud everywhere else — deterministic verdicts:
        // today's strip cell stays ✓ (fit hours exist), the next day ✗低雲,
        // day 8 honest 資料不足, and the tier chip is ✓/○ depending on how
        // much of the fit window is still remaining at run time.
        if (path === '/api/v1/custom_places/cp1/eval') {
          const pad = (n) => String(n).padStart(2, '0');
          const d0 = new Date(Date.now() + 8 * 3600e3);
          const iso = (off) => new Date(d0.getTime() + off * 86400e3).toISOString().slice(0, 10);
          const hourly = [];
          for (let day = 0; day < 2; day++) {
            for (let h = 0; h < 24; h++) {
              const clean = day === 0 && h >= 5 && h <= 7; // inside the 04:30–07:00 group window, TODAY only
              hourly.push({ local_date: iso(day), hour: pad(h) + ':00', values: {
                cloud_low: clean ? 10 : 90, cloud_mid: 20, cloud_high: 30,
                precipitation: 0, visibility: 20000, wind: 2 } });
            }
          }
          return Promise.resolve({ ok: true, status: 200, json: function () {
            return Promise.resolve({ ok: true, id: 'cp1', private: true, hourly: hourly, generatedAt: '2026-11-15T10:00:00Z', elevation: 1150, timezone: 'Asia/Taipei' });
          } });
        }
        if (path === '/api/v1/conditions/parse') {
          if (opts && opts.method === 'POST') {
            return Promise.resolve({ ok: true, status: 200, json: function () {
              return Promise.resolve({ ok: true, suggestions: { cloud: 'min', fog: 'none', rain: 'no', wind_max_ms: 5, window_start: '04:30', window_end: '07:00', lead_minutes: 45, confidence: 0.8 } });
            } });
          }
          return Promise.resolve({ ok: true, status: 200, json: function () { return Promise.resolve({ ok: true, enabled: true }); } });
        }
      if (path === '/api/v1/custom_places') {
        return Promise.resolve({ ok: true, status: 200, json: function () {
          return Promise.resolve({
            ok: true, userId: 'u1', level: 'paid',
            trial: { expired: false, expiresAt: null },
            quota: { used: 5, cap: 50 },
            degraded: false, degradedMessage: null,
            places: __cpPlaces.map(function (p) {
              var g = __cpThemes.filter(function (t) { return t.placeId === p.id; });
              return Object.assign({}, p, { themeGroups: g, themes: { used: g.length, cap: __cpThemeCap },
                sharing: __cpShare[p.id] || null });
            }),
          });
        } });
      }
      // patch-8 theme CRUD (the real client paths hit these)
      var mThemes = path.match(/^\\/api\\/v1\\/custom_places\\/([\\w-]+)\\/themes$/);
      if (mThemes && opts && opts.method === 'POST') {
        return Promise.resolve(opts.body ? JSON.parse(opts.body) : {}).then(function (payload) {
          if (__cpThemes.filter(function (t) { return t.placeId === mThemes[1]; }).length >= __cpThemeCap) {
            return Promise.resolve({ ok: true, status: 403, json: function () { return Promise.resolve({ error: 'theme group limit reached', reason: 'theme_cap', cap: __cpThemeCap, message: { 'zh-TW': '每個私人點最多 5 組題材。既有題材會保留，刪除後即可再新增。' } }); } });
          }
          var id = 'tg-new-' + (++__cpThemeSeq);
          var g = { id: id, placeId: mThemes[1], name: payload.name, nameI18n: payload.nameI18n || null,
            conditions: payload.conditions || {}, evaluation: { tier: 'shoot', reason: null, window: '2026-11-16 06:00' } };
          __cpThemes.push(g);
          return { ok: true, status: 200, json: function () { return Promise.resolve({ ok: true, id: id, theme: g, themes: { used: __cpThemes.filter(function (t) { return t.placeId === mThemes[1]; }).length, cap: __cpThemeCap } }); } };
        });
      }
      var mThemeItem = path.match(/^\\/api\\/v1\\/custom_places\\/([\\w-]+)\\/themes\\/([\\w-]+)$/);
      if (mThemeItem && opts && (opts.method === 'PATCH' || opts.method === 'DELETE')) {
        var idx = __cpThemes.findIndex(function (t) { return t.id === mThemeItem[2]; });
        if (idx < 0) return Promise.resolve({ ok: true, status: 404, json: function () { return Promise.resolve({ error: 'theme not found' }); } });
        if (opts.method === 'DELETE') __cpThemes.splice(idx, 1);
        else { return Promise.resolve(opts.body ? JSON.parse(opts.body) : {}).then(function (payload) {
          __cpThemes[idx] = Object.assign(__cpThemes[idx], payload, { id: mThemeItem[2] });
          return { ok: true, status: 200, json: function () { return Promise.resolve({ ok: true, id: mThemeItem[2] }); } };
        }); }
        return Promise.resolve({ ok: true, status: 200, json: function () { return Promise.resolve({ ok: true, deleted: mThemeItem[2] }); } });
      }
      return Promise.resolve({ ok: false, status: 404, json: function () { return Promise.resolve({ error: 'stub 404' }); } });
      };
    `;

async function bootBrowser() {
  if (ready) return ready;
  ready = (async () => {
    const MIME = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };
    server = createServer((req, res) => {
      const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
      const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
      try {
        const body = readFileSync(file);
        res.writeHead(200, { 'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream' });
        res.end(body);
      } catch { res.writeHead(404); res.end('not found'); }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    baseURL = `http://127.0.0.1:${server.address().port}/`;
    chrome = spawn(BROWSER, [
      '--headless=new', '--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage',
      '--no-first-run', '--remote-debugging-port=0',
      '--window-size=1280,900',
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clapp06-')), 'about:blank'],
      { stdio: ['ignore', 'ignore', 'pipe'] });
      const wsUrl = await new Promise((resolve, reject) => {
      let buf = '';
      let loopLast = Date.now(); const loopStart = loopLast;
      const timer = setInterval(() => {
        const now = Date.now();
        if (now - loopLast < 1500 && now - loopStart > 60000) { clearInterval(timer); reject(new Error('no devtools endpoint')); }
        loopLast = now;
      }, 250);
      chrome.stderr.on('data', d => { buf += d;
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearInterval(timer); resolve(m[1]); } });
      chrome.on('error', e => reject(new Error('spawn: ' + e.message)));
    });
    const dbgHost = wsUrl.match(/ws:\/\/([^/]+)/)[1];
    let targets = [];
    for (let i = 0; i < 40; ++i) {
      targets = await (await fetch(`http://${dbgHost}/json/list`)).json();
      if (targets.some(t => t.type === 'page')) break;
      await new Promise(r => setTimeout(r, 250));
    }
      ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
    await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
    ws.onmessage = e => { const m = JSON.parse(e.data);
      if (m.method === 'Page.loadEventFired') loadEvents++;
      if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
    send = (method, params = {}) => new Promise((resolve, reject) => {
      const i = nextId(); pending.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
      ws.send(JSON.stringify({ id: i, method, params }));
    });
      evaljs = async (expr) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
      return r.result?.result?.value ?? r.result?.value;
    };
    // The stub rides every navigation: window.__clcpFetch answers the
    // custom-places API before the widget ever asks; the widget's member
    // state is pushed via the chaselights:auth broadcast after load.
    await send('Page.enable');
    await send('Page.addScriptToEvaluateOnNewDocument', { source: CP_PAGE_STUB });
  })().catch(e => { ready = null; throw e; });
  return ready;
}

function teardownBrowser() {
  return Promise.all([
    (async () => { try { ws?.close(); } catch {} })(),
    (async () => { chrome?.kill(); })(),
    (async () => { await new Promise(r => server?.close(r)); })(),
  ]);
}

async function setViewport(width, height, mobile) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile });
}
async function loadPage() {
  const before = loadEvents;
  // CL-CI-38 root fix: the init-script registration does NOT survive past the
  // first navigation on this harness — every later document ran without the
  // stub (window.__clcpFetch undefined → real fetch → private cards never
  // rendered; the CL-APP-09b harness re-registers before each navigate for
  // the same reason). Re-send the stub before EVERY navigation.
  await send('Page.addScriptToEvaluateOnNewDocument', { source: CP_PAGE_STUB });
  await send('Page.navigate', { url: baseURL });
  await new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(loadEvents>before){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>20000){clearInterval(iv);reject(new Error('navigation never fired load'));}
    },100);
  });
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>25000){clearInterval(iv);reject(new Error('cards never rendered'));}
    },100);
  })`);
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      // CL-INT-190: re-dispatch every tick — a broadcast lost to a navigation race
      // must not hang the harness; chaselights:auth is REPLACE-semantics/idempotent.
      document.dispatchEvent(new CustomEvent('chaselights:auth', { detail: { member: { id: 'u1', displayName: '晨曦旅人', level: 'paid' } } }));
      if(document.querySelector('.cl-cp-card')){clearInterval(iv);resolve(true);}
      // CL-CI-38: late navigations in a long-lived chrome accumulate maplibre
      // instances — the post-auth private-card render can take >10s under that
      // load. The broadcast is idempotent, so a longer window is honest.
      else if(Date.now()-t0>25000){clearInterval(iv);reject(new Error('private cards never rendered'));}
    },300);
  })`);
  await new Promise(r => setTimeout(r, 400));
}

async function capture(pathOut) {
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  const { writeFileSync } = await import('node:fs');
  writeFileSync(pathOut, Buffer.from(shot.data, 'base64'));
  return pathOut;
}

test('CL-APP-06 (2a): honest count + quota chip + view-tab count identity (全部＝官方＋私人)', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(() => {
    const count = document.querySelector('.cl-cp-count');
    const chip = document.querySelector('.cl-cp-quota-chip');
    const official = document.querySelectorAll('#spots-container .card:not(.cl-cp-card)').length;
    const priv = document.querySelectorAll('#spots-container .cl-cp-card').length;
    const tabs = [...document.querySelectorAll('.cl-cp-view-tab')].map(b => ({
      key: b.getAttribute('data-cp-view'), n: Number(b.querySelector('.n').textContent), sel: b.classList.contains('sel') }));
    return { count: count && count.textContent, chip: chip && chip.textContent, official, priv, tabs,
      chipVisible: chip ? getComputedStyle(chip).display !== 'none' : false };
  })()`);
  assert.ok(probe.chipVisible, 'quota chip visible for a member');
  assert.match(probe.chip, /5\/50/, 'quota chip shows used/cap honestly');
  assert.match(probe.chip, /Premium/);
  assert.match(probe.count, /官方/, 'count line is the honest 共 N 官方＋M 私人點 identity');
  const allTab = probe.tabs.find(x => x.key === 'all'), offTab = probe.tabs.find(x => x.key === 'official'), privTab = probe.tabs.find(x => x.key === 'private');
  assert.equal(allTab.n, offTab.n + privTab.n, '全部 count = 官方 + 私人 (never mis-added)');
  assert.equal(allTab.sel, true);
  assert.ok(privTab.n >= 5);
});

test('CL-APP-06 (2b): private card anatomy — gray badge + PER-GROUP subject rows (official anatomy) + ⋯ menu opens', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  // CL-CI-38: private cards ride the official tier-tab pipeline (patch-6) —
  // non-✓推薦 points render only under their own tab / 全部. Switch first.
  await evaljs(`(async () => {
    const all = document.querySelector('#tier-tabs .tier-tab[data-tier="all"]');
    if (all) { all.click(); await new Promise(r => setTimeout(r, 600)); }
  })()`);
  const probe = await evaljs(`(() => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    if (!card) return { error: 'no cp1 card' };
    const badge = card.querySelector('.cl-cp-priv-badge');
    const cs = badge ? getComputedStyle(badge) : null;
    // patch-8: the temporary 「✓ 條件窗」 chip is GONE in rec state — per-group
    // subject rows carry the tier badges from the same source
    const rows = [...card.querySelectorAll('.cl-subject-row')].map(r => ({
      tier: r.querySelector('.cl-cp-tier') && r.querySelector('.cl-cp-tier').textContent,
      tierCls: r.querySelector('.cl-cp-tier') && r.querySelector('.cl-cp-tier').className,
      name: r.querySelector('.cl-cp-row-name') && r.querySelector('.cl-cp-row-name').textContent,
      window: r.querySelector('.cl-cp-window') && r.querySelector('.cl-cp-window').textContent,
    }));
    const c3 = document.querySelector('.cl-cp-card[data-cp-id="cp3"]');
    const c2 = document.querySelector('.cl-cp-card[data-cp-id="cp2"]');
    const c6 = document.querySelector('.cl-cp-card[data-cp-id="cp6"]');
    const more = card.querySelector('.cl-cp-more');
    more.click();
    const menu = document.getElementById('cl-cp-menu');
    const acts = [...menu.querySelectorAll('[data-cp-act]')].map(b => b.getAttribute('data-cp-act'));
    return {
      badgeText: badge && badge.textContent,
      color: cs && cs.color, bg: cs && cs.backgroundColor,
      headTierGone: !card.querySelector('.spot-title-group .cl-cp-tier'),
      rows, noCcLine: !card.querySelector('.cl-cp-cc-line'),
      cp3Rows: c3 ? [...c3.querySelectorAll('.cl-subject-row')].map(r => ({
        tier: r.querySelector('.cl-cp-tier') && r.querySelector('.cl-cp-tier').textContent,
        name: r.querySelector('.cl-cp-row-name') && r.querySelector('.cl-cp-row-name').textContent,
        reason: r.textContent.includes('風強'),
      })) : [],
      cp2None: c2 ? c2.textContent.includes('尚未設定題材') : false,
      cp2Baseline: c2 ? [...c2.querySelectorAll('.cl-subject-row')].map(r => ({
        tier: r.querySelector('.cl-cp-tier') && r.querySelector('.cl-cp-tier').textContent,
        name: r.querySelector('.cl-cp-row-name') && r.querySelector('.cl-cp-row-name').textContent,
        window: r.querySelector('.cl-cp-window') && r.querySelector('.cl-cp-window').textContent,
      })) : [],
      // patch-9: the legacy 「題材 1」 group renders the USER's genre name
      cp6Rows: c6 ? [...c6.querySelectorAll('.cl-subject-row')].map(r => ({
        tier: r.querySelector('.cl-cp-tier') && r.querySelector('.cl-cp-tier').textContent,
        name: r.querySelector('.cl-cp-row-name') && r.querySelector('.cl-cp-row-name').textContent,
      })) : [],
      cp6Coord: c6 ? (c6.querySelector('.cl-cp-coord') || {}).textContent : null,
      acts, menuOpen: getComputedStyle(menu).display,
      menuParentIsBody: menu.parentNode === document.body,
      menuPos: getComputedStyle(menu).position,
    };
  })()`);
  assert.match(probe.badgeText, /私人/);
  // gray identity: the badge color must be the neutral --cl-grey family
  // (#98A4B3 = 152,164,179), NEVER the green/amber/red semantic tokens
  assert.equal(probe.color, 'rgb(152, 164, 179)', `badge color must be --cl-grey-text, got ${probe.color}`);
  assert.equal(probe.headTierGone, true, 'patch-8: the generic 「✓ 條件窗」chip is replaced by per-group tier rows');
  assert.equal(probe.noCcLine, true, 'the single 🎚 summary line is replaced by the per-group rows');
  assert.equal(probe.rows.length, 1, 'cp1 carries ONE theme group');
  assert.equal(probe.rows[0].tier, '✓', 'per-group tier badge ✓ (same source as the worker tier)');
  assert.match(probe.rows[0].tierCls, /cl-cp-tier-rec/);
  assert.match(probe.rows[0].name, /雲海窗/, 'official subject-row anatomy: the group name rides the row');
  assert.match(probe.rows[0].window, /2026-11-16 05:00/, 'the group next window rides the row');
  assert.equal(probe.cp3Rows.length, 1);
  assert.equal(probe.cp3Rows[0].tier, '✗', 'a failing group shows ✗ with its short reason');
  assert.match(probe.cp3Rows[0].name, /風平窗/);
  assert.equal(probe.cp3Rows[0].reason, true);
  // CL-APP-12 (owner ruling 2026-11-24): a place with NO theme groups has no
  // subject to judge — the card shows 「尚未設定題材」 instead of a fabricated
  // baseline ○/✗ row.
  assert.equal(probe.cp2Baseline.length, 0, 'no groups → NO subject row is invented');
  assert.equal(probe.cp2None, true, 'the zero-subject card names the state (尚未設定題材)');
  // patch-9: the legacy auto-named group shows the user's GENRE (exact
  // night_sky starter match → 星空), never the 「題材 1」 migration placeholder
  assert.equal(probe.cp6Rows.length, 1);
  assert.equal(probe.cp6Rows[0].tier, '✓');
  assert.match(probe.cp6Rows[0].name, /^星空$/, 'legacy 「題材 1」 renders as the matched genre short name');
  assert.doesNotMatch(probe.cp6Rows[0].name, /題材 1/);
  // patch-9: the card sub-line uses the same official meta anatomy
  assert.match(probe.cp6Coord, /24\.140, 121\.270/);
  assert.match(probe.cp6Coord, /3200 m/);
  assert.match(probe.cp6Coord, /GMT\+8/);
  assert.doesNotMatch(probe.cp6Coord, /Asia\/Taipei/);
  assert.deepEqual(probe.acts.sort(), ['cc', 'del', 'edit', 'refetch'], 'menu is 編輯／掛題材·條件／🔄 獨立重新抓取／刪除 (nom removed patch-8, refetch added CL-APP-08)');
  assert.equal(probe.menuOpen, 'block', '⋯ menu opens');
  // CL-APP-08: cp2 (grouped with cp1) shows the shared-data tag, computed-visible
  const probe2 = await evaljs(`(() => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp2"]');
    if (!card) return { error: 'no cp2 card' };
    const tag = card.querySelector('.cl-cp-share-tag');
    if (!tag) return { error: 'no share tag' };
    const r = tag.getBoundingClientRect();
    const cs = getComputedStyle(tag);
    return {
      text: tag.textContent,
      visible: r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden',
      color: cs.color,
    };
  })()`);
  assert.match(probe2.text, /與 霧社水庫西岸岔路 共用資料/);
  assert.equal(probe2.visible, true, 'the share tag is COMPUTED-visible on the card');
  assert.equal(probe2.color, 'rgb(168, 179, 194)', 'share tag stays gray-identity (--cl-text-2), never a semantic color');
  // patch-3: the menu is portaled OUT of the card to document.body (fixed)
  assert.equal(probe.menuParentIsBody, true, '⋯ menu lives on document.body — outside the card boundary');
  assert.equal(probe.menuPos, 'fixed', '⋯ menu is position:fixed — card overflow can never clip it');
});

test('CL-APP-06 (2c): trial-expired card is gray + honest 試用期滿 + upgrade CTA; deferred card honest note', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  // CL-CI-38: patch-6 renders special-state cards (no verdict) ONLY under the
  // 全部 tier tab — same rule as official noeval spots. Switch to 全部 first.
  await evaljs(`(async () => {
    const all = document.querySelector('#tier-tabs .tier-tab[data-tier="all"]');
    if (all) { all.click(); await new Promise(r => setTimeout(r, 600)); }
  })()`);
  const probe = await evaljs(`(() => {
    const ex = document.querySelector('.cl-cp-card[data-cp-id="cp4"]');
    const df = document.querySelector('.cl-cp-card[data-cp-id="cp5"]');
    const cs = ex && getComputedStyle(ex);
    return {
      expired: !!ex, opacity: cs && cs.opacity,
      label: ex && [...ex.querySelectorAll('*')].map(x => x.textContent).join(' ').includes('試用期滿'),
      cta: ex && !!ex.querySelector('[data-cp-act="upgrade"]'),
      tierPending: ex && !!ex.querySelector('.cl-cp-tier-pending'),
      deferred: df && df.textContent.includes('明日更新'),
    };
  })()`);
  assert.equal(probe.expired, true);
  assert.equal(probe.label, true, 'honest 「試用期滿」 label');
  assert.equal(probe.cta, true, 'upgrade CTA present');
  assert.equal(probe.tierPending, true, 'evaluation stopped — no fabricated tier');
  assert.ok(Number(probe.opacity) < 1, 'expired card renders grayed out');
  assert.equal(probe.deferred, true, 'layer-3 deferred card honestly reports 明日更新');
});

test('CL-APP-06 (2d): view switch filters with real computed visibility (private ⇄ official)', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    const out = {};
    document.querySelector('.cl-cp-view-tab[data-cp-view="private"]').click();
    await new Promise(r => setTimeout(r, 300));
    const privCard = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    const firstOfficial = document.querySelector('#spots-container .card:not(.cl-cp-card)');
    out.privateView = {
      priv: privCard && getComputedStyle(privCard).display,
      official: firstOfficial ? getComputedStyle(firstOfficial).display : 'absent',
    };
    document.querySelector('.cl-cp-view-tab[data-cp-view="official"]').click();
    await new Promise(r => setTimeout(r, 300));
    // CL-CI-38: the patch-6 bridge REMOVES private cards in official view
    // (app.js rebuilds the container from the filtered rows) — absent reads
    // as hidden, same intent as the pre-bridge display:none CSS.
    const privInOfficial = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    out.officialView = {
      priv: privInOfficial ? getComputedStyle(privInOfficial).display : 'absent',
      official: document.querySelector('#spots-container .card:not(.cl-cp-card)') ? getComputedStyle(document.querySelector('#spots-container .card:not(.cl-cp-card)')).display : 'absent',
    };
    document.querySelector('.cl-cp-view-tab[data-cp-view="all"]').click();
    await new Promise(r => setTimeout(r, 300));
    return out;
  })()`);
  assert.notEqual(probe.privateView.priv, 'none', 'private tab shows private cards');
  // CL-CI-38: the patch-6 filter pipeline rebuilds the container per view —
  // officials in the private view are REMOVED, which reads as hidden.
  assert.ok(probe.privateView.official === 'none' || probe.privateView.official === 'absent', 'private tab hides official cards (hidden or removed)');
  // CL-CI-38: the patch-6 bridge removes private cards in official view —
  // 'absent' is the honest hidden state (same intent as the pre-bridge
  // display:none CSS pin).
  assert.ok(probe.officialView.priv === 'none' || probe.officialView.priv === 'absent', 'official tab hides private cards (hidden or removed)');
  assert.notEqual(probe.officialView.official, 'none', 'official tab shows official cards');
});

test('CL-APP-06 (2e): add modal — pin map + lat/lng + READ-ONLY auto elevation/timezone', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    document.querySelector('.cl-cp-add-btn').click();
    await new Promise(r => setTimeout(r, 200));
    const ov = document.querySelector('.cl-cp-overlay');
    const open = ov.classList.contains('open');
    const pick = ov.querySelector('.cl-cp-pinpick');
    const r = pick.getBoundingClientRect();
    // drop a pin at the schematic center-right (Taiwan-ish)
    const ev = new MouseEvent('click', { clientX: r.left + r.width * 0.84, clientY: r.top + r.height * 0.6, bubbles: true });
    pick.dispatchEvent(ev);
    await new Promise(res => setTimeout(res, 400));
    const lat = ov.querySelector('#cl-cp-lat').value, lng = ov.querySelector('#cl-cp-lng').value;
    const elev = ov.querySelector('#cl-cp-elev') && ov.querySelector('#cl-cp-elev').textContent;
    const tz = ov.querySelector('#cl-cp-tz') && ov.querySelector('#cl-cp-tz').textContent;
    const submitBtn = ov.querySelector('#cl-cp-submit');
    const out = { open, lat, lng, elev, tz,
      readyBefore: submitBtn.classList.contains('ready'), btnBefore: submitBtn.textContent };
    // patch-2: the name is required — typing it flips the button ready with its real label
    const nm = ov.querySelector('#cl-cp-name');
    nm.value = '測試私人點';
    nm.dispatchEvent(new Event('input'));
    await new Promise(r => setTimeout(r, 100));
    out.readyAfter = submitBtn.classList.contains('ready');
    out.btnAfter = submitBtn.textContent;
    return out;
  })()`);
  assert.equal(probe.open, true);
  assert.ok(probe.lat, 'click-to-drop fills lat');
  assert.ok(probe.lng, 'click-to-drop fills lng');
  assert.equal(probe.elev, '80 m', 'DEM elevation auto-filled (read-only value)');
  assert.match(probe.tz, /Asia\/Taipei/, 'timezone auto-filled (IANA)');
  assert.equal(probe.readyBefore, false, 'no name yet — button not ready');
  assert.match(probe.btnBefore, /請先輸入景點名稱/, 'patch-2: the disabled button shows the reason on itself, not just gray');
  assert.equal(probe.readyAfter, true, 'typing the name makes the button ready');
  assert.match(probe.btnAfter, /建立私人點/, 'ready button carries its real label again');
});

test('CL-APP-06 (2f): headless screenshots at 1280/390 for the mockup comparison', async () => {
  await bootBrowser();
  const shots = [];
  await setViewport(1280, 900, false);
  await loadPage();
  shots.push(await capture(join(WEB, 'apps', 'web-v2', 'tests', 'logs', 'cl-app-06-1280.png')));
  await setViewport(390, 844, true);
  await new Promise(r => setTimeout(r, 400));
  shots.push(await capture(join(WEB, 'apps', 'web-v2', 'tests', 'logs', 'cl-app-06-390.png')));
  assert.equal(shots.length, 2);
});
test('CL-APP-06 (2h, patch-8): 「掛題材·條件」 = LIST manager — groups with tiers; add form carries the name field, semantic selects, transparent mapping, genre starter, advanced inputs', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    card.querySelector('.cl-cp-more').click();
    document.querySelector('#cl-cp-menu [data-cp-act="cc"]').click();
    await new Promise(r => setTimeout(r, 250));
    const ov = document.querySelector('.cl-cp-overlay');
    const out = {};
    // the LIST manager: 1 group with its tier + honest count
    out.listOpen = ov.classList.contains('open');
    out.listTitle = ov.querySelector('.cl-cp-m-head .name').textContent;
    out.count = ov.querySelector('.cl-cp-th-count').textContent;
    out.groupRow = ov.querySelector('.cl-cp-theme-row') && {
      name: ov.querySelector('.cl-cp-theme-row .cl-cp-theme-info .n').textContent,
      tier: ov.querySelector('.cl-cp-theme-row .cl-cp-tier').textContent,
    };
    // the EDIT form: name field FIRST, prefilled from the stored group
    const editBtn = ov.querySelector('.cl-cp-theme-row [data-cp-th-act="edit"]');
    editBtn.click();
    await new Promise(r => setTimeout(r, 200));
    out.formTitle = ov.querySelector('.cl-cp-m-head .name').textContent;
    out.nameFieldFirst = ov.querySelector('.cl-cp-modal').querySelector('input') === ov.querySelector('#cl-cp-theme-name');
    out.namePrefill = ov.querySelector('#cl-cp-theme-name').value;
    const sel = ov.querySelector('#cl-cp-sem-cloud');
    const map0 = ov.querySelector('#cl-cp-sem-map-cloud').textContent;
    const low0 = ov.querySelector('#cl-cp-cc-low').value;
    sel.value = 'half';
    sel.dispatchEvent(new Event('change'));
    await new Promise(r => setTimeout(r, 100));
    const map1 = ov.querySelector('#cl-cp-sem-map-cloud').textContent;
    const low1 = ov.querySelector('#cl-cp-cc-low').value;
    const prev = ov.querySelector('#cl-cp-cc-prev').textContent;
    const genreOptions = ov.querySelectorAll('#cl-cp-cc-genre option').length;
    const gs = ov.querySelector('#cl-cp-cc-genre');
    gs.value = 'cloud_sea';
    gs.dispatchEvent(new Event('change'));
    await new Promise(r => setTimeout(r, 100));
    const starterCloud = ov.querySelector('#cl-cp-sem-cloud').value;
    // CL-APP-09 patch-2: the window editor is now segment-based (#cl-cp-ws0-*)
    const starterWin = [ov.querySelector('#cl-cp-ws0-start').value, ov.querySelector('#cl-cp-ws0-end').value];
    const advanced = ov.querySelector('.cl-cp-cc-advanced');
    Object.assign(out, { map0, low0, map1, low1, prev, genreOptions, starterCloud, starterWin, advancedOpenDefault: advanced.open });
    // disabled-reason pattern: clearing the name → the button prints it
    out.btnBefore = (function () { const nm = ov.querySelector('#cl-cp-theme-name'); nm.value = ''; nm.dispatchEvent(new Event('input')); return ov.querySelector('#cl-cp-cc-submit').textContent; })();
    const nm = ov.querySelector('#cl-cp-theme-name');
    nm.value = '星光窗';
    nm.dispatchEvent(new Event('input'));
    out.btnAfter = ov.querySelector('#cl-cp-cc-submit').textContent;
    return out;
  })()`);
  assert.equal(probe.listOpen, true);
  assert.match(probe.listTitle, /掛題材/);
  assert.match(probe.count, /1\/5/, 'honest group count against the 5 cap');
  assert.match(probe.groupRow.name, /雲海窗/);
  assert.equal(probe.groupRow.tier, '✓', 'the list row carries the same-source per-group tier');
  assert.match(probe.formTitle, /✎/, 'the edit form opens from the list row');
  assert.equal(probe.nameFieldFirst, true, 'the group name is the FIRST field');
  assert.match(probe.namePrefill, /雲海窗/, 'the stored group name prefills');
  assert.match(probe.map0, /低雲 ≤20%/, 'transparent mapped value shown (15% rounds to the 越少越好 tier)');
  assert.equal(probe.low0, '15', 'advanced input keeps the actual stored concrete value');
  assert.match(probe.map1, /低雲 ≤50%/);
  assert.equal(probe.low1, '50', 'changing the semantic select writes the mapped concrete value');
  assert.match(probe.prev, /低雲≤50/, 'preview updates from the mapped value');
  assert.ok(probe.genreOptions >= 22, '21 genre starters + the empty option');
  // CL-CI-38: patch-5 fixed the 雲海 starter direction — low cloud 越多越好
  // (cloud_low_min), so the semantic select prefills 'more', not 'min'.
  assert.equal(probe.starterCloud, 'more', '雲海 starter applies');
  assert.deepEqual(probe.starterWin, ['04:30', '07:00']);
  assert.equal(probe.advancedOpenDefault, false, 'advanced raw inputs collapsed by default');
  assert.match(probe.btnBefore, /請先輸入題材名稱/, 'the disabled button shows the reason on itself');
  assert.match(probe.btnAfter, /儲存題材/, 'typing the name readies the button');
});
test('CL-APP-06 (2i): ✨ one-sentence AI parse fills the semantic selects (AI only translates — concrete values still submitted)', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  // CL-CI-38: private cards ride the official tier-tab pipeline (patch-6) —
  // non-✓推薦 points render only under their own tab / 全部. Switch first.
  await evaljs(`(async () => {
    const all = document.querySelector('#tier-tabs .tier-tab[data-tier="all"]');
    if (all) { all.click(); await new Promise(r => setTimeout(r, 600)); }
  })()`);
  const probe = await evaljs(`(async () => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp2"]');
    card.querySelector('.cl-cp-more').click();
    document.querySelector('#cl-cp-menu [data-cp-act="cc"]').click();
    await new Promise(r => setTimeout(r, 250));
    const ov = document.querySelector('.cl-cp-overlay');
    // cp2 has NO groups — the list shows the honest empty state, then the add form
    if (!ov.querySelector('.cl-cp-th-empty')) return { error: 'empty-state note absent' };
    ov.querySelector('#cl-cp-th-add').click();
    await new Promise(r => setTimeout(r, 250));
    const ai = ov.querySelector('#cl-cp-ai');
    if (!ai) return { error: 'AI entry absent although the stub reports enabled' };
    ov.querySelector('#cl-cp-ai-text').value = 'I want a cloud sea at dawn, no rain, 04:30-07:00, wind under 5';
    ov.querySelector('#cl-cp-ai-go').click();
    await new Promise(r => setTimeout(r, 300));
    const note = ov.querySelector('#cl-cp-ai-note').textContent;
    return {
      cloud: ov.querySelector('#cl-cp-sem-cloud').value,
      fog: ov.querySelector('#cl-cp-sem-fog').value,
      rain: ov.querySelector('#cl-cp-sem-rain').value,
      mapCloud: ov.querySelector('#cl-cp-sem-map-cloud').textContent,
      win: [ov.querySelector('#cl-cp-ws0-start').value, ov.querySelector('#cl-cp-ws0-end').value],
      wind: ov.querySelector('#cl-cp-cc-wind').value,
      note,
    };
  })()`);
  assert.equal(probe.cloud, 'min');
  assert.equal(probe.fog, 'none');
  assert.equal(probe.rain, 'no');
  assert.match(probe.mapCloud, /低雲 ≤20%/, 'the mapped concrete value stays transparent after the AI fills the selects');
  assert.deepEqual(probe.win, ['04:30', '07:00']);
  assert.equal(probe.wind, '5');
  assert.match(probe.note, /80%/);
});
test('CL-APP-06 (2j): 📍 current location — success fills lat/lng + drops the map mark + submit-ready', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    document.querySelector('.cl-cp-add-btn').click();
    await new Promise(r => setTimeout(r, 200));
    const ov = document.querySelector('.cl-cp-overlay');
    const btn = ov.querySelector('#cl-cp-geo-btn');
    const note = ov.querySelector('.cl-cp-geo-note');
    const btnCs = getComputedStyle(btn);
    // mock geolocation: honest browser-API-shaped success (Web and the
    // Capacitor plugin both resolve { coords: { latitude, longitude } })
    window.__clcpGeo = (opts) => {
      window.__clcpGeoOpts = opts;
      return Promise.resolve({ coords: { latitude: 24.82252, longitude: 121.76748 } });
    };
    btn.click();
    await new Promise(r => setTimeout(r, 300));
    const nm = ov.querySelector('#cl-cp-name');
    nm.value = '測試私人點';
    nm.dispatchEvent(new Event('input'));
    await new Promise(r => setTimeout(r, 100));
    const lat = ov.querySelector('#cl-cp-lat').value, lng = ov.querySelector('#cl-cp-lng').value;
    const mark = !!ov.querySelector('.cl-cp-pinmark');
    const submitReady = ov.querySelector('#cl-cp-submit').classList.contains('ready');
    const status = ov.querySelector('#cl-cp-geo-status').textContent;
    const opts = window.__clcpGeoOpts;
    return { btnLabel: btn.textContent.trim(), btnVisible: btnCs.display !== 'none',
      noteVisible: getComputedStyle(note).display !== 'none', noteText: note.textContent,
      lat, lng, mark, submitReady, status, hadTimeout: !!opts && opts.timeout > 0,
      latLngEditable: !ov.querySelector('#cl-cp-lat').disabled };
  })()`);
  assert.match(probe.btnLabel, /使用我的目前位置/);
  assert.equal(probe.btnVisible, true);
  assert.equal(probe.noteVisible, true, 'permission-explanation note renders');
  assert.match(probe.noteText, /不會追蹤/, 'honest why-we-need-it note');
  assert.equal(probe.lat, '24.8225', 'coords fill the lat input');
  assert.equal(probe.lng, '121.7675', 'coords fill the lng input');
  assert.equal(probe.mark, true, 'map preview marks the coordinate');
  assert.equal(probe.submitReady, true);
  assert.equal(probe.status, '', 'no error text on success');
  assert.equal(probe.hadTimeout, true, 'request is bounded by a timeout');
  assert.equal(probe.latLngEditable, true, 'manual input stays available');
});

test('CL-APP-06 (2k): 📍 denied → honest message, falls back to manual pin/lat-lng', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    document.querySelector('.cl-cp-add-btn').click();
    await new Promise(r => setTimeout(r, 200));
    const ov = document.querySelector('.cl-cp-overlay');
    window.__clcpGeo = () => Promise.reject({ code: 1, message: 'permission denied' });
    const btn = ov.querySelector('#cl-cp-geo-btn');
    btn.click();
    await new Promise(r => setTimeout(r, 300));
    const status = ov.querySelector('#cl-cp-geo-status').textContent;
    const lat = ov.querySelector('#cl-cp-lat').value, lng = ov.querySelector('#cl-cp-lng').value;
    // manual path still works end-to-end: type lat/lng → pin + submit-ready
    ov.querySelector('#cl-cp-lat').value = '24.8225';
    ov.querySelector('#cl-cp-lng').value = '121.7675';
    ov.querySelector('#cl-cp-lng').dispatchEvent(new Event('change'));
    await new Promise(r => setTimeout(r, 150));
    const nm = ov.querySelector('#cl-cp-name');
    nm.value = '測試私人點';
    nm.dispatchEvent(new Event('input'));
    await new Promise(r => setTimeout(r, 100));
    return { status, lat, lng, mark: !!ov.querySelector('.cl-cp-pinmark'),
      submitReady: ov.querySelector('#cl-cp-submit').classList.contains('ready'),
      btnReEnabled: !ov.querySelector('#cl-cp-geo-btn').disabled };
  })()`);
  assert.match(probe.status, /定位權限被拒絕/, 'honest permission-denied message');
  assert.equal(probe.lat, '', 'no fabricated coordinates on denial');
  assert.equal(probe.lng, '');
  assert.equal(probe.btnReEnabled, true);
  assert.equal(probe.mark, true, 'manual lat/lng entry still drops the pin');
  assert.equal(probe.submitReady, true, 'manual entry reaches submit-ready');
});

test('CL-APP-06 (2l): 📍 timeout → honest message, manual input survives', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  const probe = await evaljs(`(async () => {
    document.querySelector('.cl-cp-add-btn').click();
    await new Promise(r => setTimeout(r, 200));
    const ov = document.querySelector('.cl-cp-overlay');
    window.__clcpGeo = () => Promise.reject({ code: 3, message: 'timeout' });
    ov.querySelector('#cl-cp-geo-btn').click();
    await new Promise(r => setTimeout(r, 300));
    const status = ov.querySelector('#cl-cp-geo-status').textContent;
    const btn = ov.querySelector('#cl-cp-geo-btn');
    return { status, mark: !!ov.querySelector('.cl-cp-pinmark'),
      btnVisible: getComputedStyle(btn).display !== 'none',
      btnReEnabled: !btn.disabled,
      statusVisible: getComputedStyle(ov.querySelector('#cl-cp-geo-status')).display !== 'none' };
  })()`);
  assert.match(probe.status, /逾時/, 'honest timeout message');
  assert.equal(probe.mark, false, 'no pin fabricated on timeout');
  assert.equal(probe.btnVisible, true, 'geo button stays visible on mobile');
  assert.equal(probe.btnReEnabled, true);
  assert.equal(probe.statusVisible, true, 'status text is computed-visible');
});


test('CL-APP-06 (2m, patch-2): short window (1280×768) — modal fully visible, name field visible + auto-focused, reason on the button', async () => {
  await bootBrowser();
  await setViewport(1280, 768, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    document.querySelector('.cl-cp-add-btn').click();
    await new Promise(r => setTimeout(r, 200));
    const ov = document.querySelector('.cl-cp-overlay');
    const modal = ov.querySelector('.cl-cp-modal');
    const mr = modal.getBoundingClientRect();
    const name = ov.querySelector('#cl-cp-name');
    const nr = name.getBoundingClientRect();
    const btn = ov.querySelector('#cl-cp-submit');
    const out = {
      winH: window.innerHeight, modalTop: mr.top, modalBottom: mr.bottom,
      nameVisible: getComputedStyle(name).display !== 'none' && nr.height > 0 && nr.top >= 0 && nr.bottom <= window.innerHeight,
      focused: document.activeElement === name,
      btnText: btn.textContent, ready: btn.classList.contains('ready'),
      modalScrollable: modal.scrollHeight > modal.clientHeight,
    };
    // internal scroll: the button must be reachable at the BOTTOM of the modal
    modal.scrollTop = modal.scrollHeight;
    await new Promise(r => setTimeout(r, 100));
    const br = btn.getBoundingClientRect();
    const hit = document.elementFromPoint(br.left + br.width / 2, br.top + br.height / 2);
    out.btnReachable = br.top >= 0 && br.bottom <= window.innerHeight + 1 && (hit === btn || (hit && btn.contains(hit)));
    return out;
  })()`);
  assert.ok(probe.modalTop >= -1 && probe.modalBottom <= probe.winH + 1,
    `modal fully inside the ${probe.winH}px window (top=${probe.modalTop}, bottom=${probe.modalBottom})`);
  assert.equal(probe.nameVisible, true, 'name field computed-visible inside the window');
  assert.equal(probe.focused, true, 'the first field (name) auto-focuses on open');
  assert.equal(probe.ready, false);
  assert.match(probe.btnText, /請先輸入景點名稱/, 'the disabled button shows its reason, not just gray');
  assert.ok(probe.btnReachable, 'the submit button is reachable (clickable) inside the internally scrolled modal');
});

test('CL-APP-06 (2n, patch-2): 390×768 small window — same fix on the mobile sheet', async () => {
  await bootBrowser();
  await setViewport(390, 768, true);
  await loadPage();
  const probe = await evaljs(`(async () => {
    document.querySelector('.cl-cp-add-btn').click();
    await new Promise(r => setTimeout(r, 200));
    const ov = document.querySelector('.cl-cp-overlay');
    const modal = ov.querySelector('.cl-cp-modal');
    const mr = modal.getBoundingClientRect();
    const name = ov.querySelector('#cl-cp-name');
    const nr = name.getBoundingClientRect();
    const btn = ov.querySelector('#cl-cp-submit');
    const out = {
      winH: window.innerHeight, winW: window.innerWidth,
      modalTop: mr.top, modalBottom: mr.bottom, modalW: mr.width,
      nameVisible: getComputedStyle(name).display !== 'none' && nr.height > 0 && nr.top >= 0 && nr.bottom <= window.innerHeight,
      focused: document.activeElement === name,
      btnText: btn.textContent,
    };
    modal.scrollTop = modal.scrollHeight;
    await new Promise(r => setTimeout(r, 100));
    const br = btn.getBoundingClientRect();
    const hit = document.elementFromPoint(br.left + br.width / 2, br.top + br.height / 2);
    out.btnReachable = br.left >= 0 && br.top >= 0 && br.bottom <= window.innerHeight + 1 && (hit === btn || (hit && btn.contains(hit)));
    // typing the name swaps the button reason to the missing-pin one…
    const nm = ov.querySelector('#cl-cp-name');
    nm.value = '測試私人點';
    nm.dispatchEvent(new Event('input'));
    await new Promise(r => setTimeout(r, 100));
    out.btnNameOnly = btn.textContent;
    // …and dropping the pin (manual lat/lng) makes it ready with the real label
    ov.querySelector('#cl-cp-lat').value = '24.8225';
    ov.querySelector('#cl-cp-lng').value = '121.7675';
    ov.querySelector('#cl-cp-lng').dispatchEvent(new Event('change'));
    await new Promise(r => setTimeout(r, 400));
    out.readyAfter = btn.classList.contains('ready');
    out.btnAfter = btn.textContent;
    return out;
  })()`);
  assert.ok(probe.modalW <= probe.winW + 1, 'the sheet fits the 390px window');
  assert.ok(probe.modalTop >= -1 && probe.modalBottom <= probe.winH + 1,
    `sheet fully inside the ${probe.winW}×${probe.winH} window (top=${probe.modalTop}, bottom=${probe.modalBottom})`);
  assert.equal(probe.nameVisible, true, 'name field visible on the 390px sheet');
  assert.equal(probe.focused, true, 'name field auto-focuses on mobile too');
  assert.match(probe.btnText, /請先輸入景點名稱/, 'disabled reason visible on mobile');
  assert.ok(probe.btnReachable, 'submit button reachable on the 390px sheet');
  assert.match(probe.btnNameOnly, /請先落釘或輸入經緯度/, 'after the name, the button explains the NEXT missing step');
  assert.equal(probe.readyAfter, true);
  assert.match(probe.btnAfter, /建立私人點/);
});

test('CL-APP-06 (2r, patch-5): 1280×768 EDIT modal after a scrolled tall modal — top fields not clipped, body locked, no horizontal overflow, menu = 3 items (patch-6)', async () => {
  await bootBrowser();
  await setViewport(1280, 768, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    const out = {};
    // step 1 — repro precondition: open the TALL theme form, scroll to
    // its bottom (patch-5 architecture: the tall overflow lives INSIDE the
    // modal; the overlay only scrolls when the modal itself exceeds the
    // viewport — scroll whichever scroller actually overflows), close it
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    card.querySelector('.cl-cp-more').click();
    document.querySelector('#cl-cp-menu [data-cp-act="cc"]').click();
    await new Promise(r => setTimeout(r, 250));
    const ov = document.querySelector('.cl-cp-overlay');
    ov.querySelector('.cl-cp-theme-row [data-cp-th-act="edit"]').click();
    await new Promise(r => setTimeout(r, 250));
    const tallModal = ov.querySelector('.cl-cp-modal');
    tallModal.scrollTop = tallModal.scrollHeight;
    ov.scrollTop = ov.scrollHeight;
    await new Promise(r => setTimeout(r, 50));
    out.overlayScrollPersisted = (tallModal.scrollTop > 0) || (ov.scrollTop > 0);
    out.bodyLockedWhileOpen = document.body.classList.contains('cl-cp-lock');
    ov.querySelector('[data-cp-close]').click();
    await new Promise(r => setTimeout(r, 100));
    out.bodyUnlockedAfterClose = !document.body.classList.contains('cl-cp-lock');
    // step 2 — owner's exact case: open the EDIT modal right after
    card.querySelector('.cl-cp-more').click();
    document.querySelector('#cl-cp-menu [data-cp-act="edit"]').click();
    await new Promise(r => setTimeout(r, 250));
    const modal = ov.querySelector('.cl-cp-modal');
    const mr = modal.getBoundingClientRect();
    out.bodyLocked = document.body.classList.contains('cl-cp-lock');
    out.modalTop = mr.top; out.modalBottom = mr.bottom;
    out.hScroll = modal.scrollWidth > modal.clientWidth;
    out.hOffenders = [...modal.querySelectorAll('*')].filter(el => el.scrollWidth > el.clientWidth + 1).slice(0, 10).map(el => el.tagName + '.' + el.className + ' sw=' + el.scrollWidth + ' cw=' + el.clientWidth + ' kids=' + [...el.children].map(k => k.tagName + '.' + k.className + ':' + Math.round(k.getBoundingClientRect().width) + 'w/sw' + k.scrollWidth).join('|'));
    const vis = (el) => { const r = el.getBoundingClientRect(); return r.top >= 0 && r.bottom <= window.innerHeight + 1 && r.height > 0; };
    const name = ov.querySelector('#cl-cp-name'), pin = ov.querySelector('#cl-cp-pinpick'), btn = ov.querySelector('#cl-cp-submit');
    out.nameVisible = vis(name);
    out.pinVisible = vis(pin);
    out.submitVisible = vis(btn);
    if (!out.submitVisible) { // reachable via the modal's INTERNAL scroll
      modal.scrollTop = modal.scrollHeight;
      await new Promise(r => setTimeout(r, 100));
      out.submitVisible = vis(btn);
      out.submitViaInnerScroll = true; }
    out.menuActs = [...document.querySelectorAll('#cl-cp-menu [data-cp-act]')].map(b => b.getAttribute('data-cp-act'));
    return out;
  })()`);
  assert.equal(probe.bodyLockedWhileOpen, true, 'body scroll is locked while a modal is open');
  assert.equal(probe.bodyUnlockedAfterClose, true, 'body scroll unlocks on close');
  assert.equal(probe.bodyLocked, true);
  assert.ok(probe.overlayScrollPersisted, 'repro precondition: the tall modal left the overlay scrolled');
  assert.ok(probe.modalTop >= -1 && probe.modalBottom <= 769,
    `edit modal inside the 1280×768 window (top=${probe.modalTop}, bottom=${probe.modalBottom})`);
  assert.equal(probe.hScroll, false, 'no horizontal overflow inside the modal (offenders: ' + JSON.stringify(probe.hOffenders) + ')');
  assert.ok(probe.nameVisible, 'name field visible at the top of the edit modal');
  assert.ok(probe.pinVisible, 'pin-picker area visible');
  assert.ok(probe.submitVisible, 'submit/update button visible (viewport or inner scroll)');
  assert.deepEqual(probe.menuActs.sort(), ['cc', 'del', 'edit', 'refetch'], 'menu = 編輯／掛題材·條件／🔄 獨立重新抓取／刪除 (CL-APP-08 + patch-8)');
});

test('CL-APP-06 (1f, patch-3): ⋯ menu renders OUT of the card — portal + fixed + flip-up + 44px + scroll-close', () => {
  // owner bug: the dropdown's 3rd item 「掛題材·條件」 was clipped in half —
  // the menu was position:absolute INSIDE the card, whose content-visibility
  // (paint containment) and the container overflow clipped it.
  const menuCss = cssSource.slice(cssSource.indexOf('.cl-cp-menu{'));
  assert.match(menuCss, /position:fixed/, 'menu is position:fixed — out of every clipping ancestor');
  assert.match(menuCss, /max-height:\s*calc\(100vh\s*-\s*16px\)/, 'never taller than the viewport');
  assert.match(menuCss, /overflow-y:\s*auto/, 'extreme short windows scroll internally instead of clipping');
  assert.match(menuCss, /\.cl-cp-menu button\{[^}]*min-height:44px/, 'menu items are ≥44px touch targets');
  // the 22px ⋯ glyph keeps its look but carries a centered 44px hit area
  assert.match(cssSource, /\.cl-cp-more::after\{[^}]*width:44px;height:44px/, '⋯ trigger touch target expanded to 44px');
  // portal: one shared menu appended to document.body, NOT card markup
  assert.match(jsSource, /document\.body\.appendChild\(m\)/);
  assert.match(jsSource, /id = 'cl-cp-menu'/);
  assert.doesNotMatch(jsSource, /<span class="cl-cp-menu">/, 'the card markup no longer embeds the menu');
  // flip-up when near the viewport bottom
  assert.match(jsSource, /向上展開/, 'flip-up branch documented');
  // CL-APP-08 re-anchor: the flip-up condition now compares against
  // bottomLimit (innerHeight minus the fixed bottom site-nav band)
  assert.match(jsSource, /top \+ mh > bottomLimit - margin && r\.top - gap - mh >= margin/,
    'opens upward when the menu would overflow the viewport bottom AND there is room above');
  // scroll events do not bubble → capture-phase listener closes on ANY scroller
  assert.match(jsSource, /addEventListener\('scroll',[\s\S]{0,120}, true\)/, 'scroll closes the open menu (capture)');
  assert.match(jsSource, /window\.addEventListener\('resize'/, 'resize closes the open menu');
  // outside click still closes
  assert.match(jsSource, /\.cl-cp-menu, \.cl-cp-more/);
});

test('CL-APP-06 (2o, patch-3): 390 viewport, card near the page footer — menu escapes the card, every item visible, 「掛題材·條件」 real-clickable', async () => {
  await bootBrowser();
  await setViewport(390, 844, true);
  await loadPage();
  // CL-CI-38: private cards ride the official tier-tab pipeline (patch-6) —
  // non-✓推薦 points render only under their own tab / 全部. Switch first.
  await evaljs(`(async () => {
    const all = document.querySelector('#tier-tabs .tier-tab[data-tier="all"]');
    if (all) { all.click(); await new Promise(r => setTimeout(r, 600)); }
  })()`);
  const probe = await evaljs(`(async () => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp2"]');
    const frame = () => new Promise(r => requestAnimationFrame(() => r()));
    card.scrollIntoView({ block: 'end' }); // card bottom pinned to the viewport bottom — the owner's footer case
    await frame(); await frame();
    // CL-CI-41 (G): scrollIntoView is unreliable on the CI runner (measured a
    // trigger at top 0 after a block:'end' scroll, i.e. the page never moved), so
    // correct against the window and re-measure before opening the menu — the
    // flip-up contract only means something when the trigger really is at the
    // bottom. Up to 3 corrections; the last window position is what gets asserted.
    for (let i = 0; i < 3; i++) {
      const tb = card.querySelector('.cl-cp-more').getBoundingClientRect();
      const dy = (window.innerHeight - 24) - tb.bottom;
      if (Math.abs(dy) <= 2) break;
      window.scrollBy(0, dy);
      await frame(); await frame();
    }
    await new Promise(r => setTimeout(r, 300));
    const more = card.querySelector('.cl-cp-more');
    more.click();
    await new Promise(r => setTimeout(r, 100));
    const menu = document.getElementById('cl-cp-menu');
    const mr = menu.getBoundingClientRect();
    const moreR = more.getBoundingClientRect();
    const items = [...menu.querySelectorAll('[data-cp-act]')].map(b => {
      const ir = b.getBoundingClientRect();
      const hit = document.elementFromPoint(ir.left + ir.width / 2, ir.top + ir.height / 2);
      return { act: b.getAttribute('data-cp-act'), text: b.textContent.trim(), h: ir.height,
        top: ir.top, bottom: ir.bottom, left: ir.left, right: ir.right,
        clickable: hit === b || (hit && b.contains(hit)) };
    });
    return { inBody: menu.parentNode === document.body, pos: getComputedStyle(menu).position,
      open: menu.classList.contains('open'),
      triggerTop: moreR.top, triggerBottom: moreR.bottom,
      menuTop: mr.top, menuBottom: mr.bottom, menuRight: mr.right, menuLeft: mr.left,
      winH: window.innerHeight, winW: window.innerWidth, items };
  })()`);
  assert.equal(probe.inBody, true, 'menu is portaled to document.body — outside the card');
  assert.equal(probe.pos, 'fixed');
  assert.equal(probe.open, true);
  // CL-CI-42: the footer case only exists when the page can actually scroll the
  // trigger down to the bottom edge. When it cannot (short page / last card in a
  // 390px window), the honest contract is the other half of the same rule: the
  // menu opens BELOW the trigger and stays fully inside the viewport. Asserting
  // flip-up unconditionally made the test depend on scrollIntoView, which the
  // CL-CI-41 (G) note above already records as unreliable.
  const roomBelow = probe.winH - probe.triggerBottom;
  const menuH = probe.menuBottom - probe.menuTop;
  if (roomBelow < menuH + 12) {
    assert.ok(probe.menuBottom <= probe.triggerTop + 1,
      `menu flipped up (bottom ${probe.menuBottom} ≤ trigger top ${probe.triggerTop}, room below ${roomBelow})`);
  } else {
    assert.ok(probe.menuTop >= probe.triggerBottom - 1,
      `menu opens below the trigger when there is room (top ${probe.menuTop} ≥ trigger bottom ${probe.triggerBottom}, room ${roomBelow})`);
  }
  assert.ok(probe.menuTop >= 0, 'flipped menu still starts inside the viewport');
  assert.ok(probe.menuRight <= probe.winW + 1 && probe.menuLeft >= 0, 'menu fits the 390px width');
  // CL-INT-206 merge: four items — 編輯／掛題材·條件／🔄 獨立重新抓取／刪除
  assert.equal(probe.items.length, 4, 'menu is 編輯／掛題材·條件／獨立重新抓取／刪除');
  if (process.env.CLDBG) console.log("DBG-2o", JSON.stringify({ winH: probe.winH, menuTop: probe.menuTop, menuBottom: probe.menuBottom, triggerTop: probe.triggerTop, items: probe.items }));
  if (process.env.CLDBG) console.log("DBG-2o-hit", await evaljs(`(() => { const del = document.querySelector('#cl-cp-menu [data-cp-act="del"]'); const r = del.getBoundingClientRect(); const el = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); return JSON.stringify({ tag: el.tagName, cls: el.className && el.className.toString().slice(0,80), id: el.id, txt: (el.textContent||'').slice(0,40) }); })()`));
  for (const it of probe.items) {
    assert.ok(it.h >= 43, `${it.act} touch target ≥44px (got ${it.h})`);
    assert.ok(it.top >= 0 && it.bottom <= probe.winH + 1 && it.left >= 0 && it.right <= probe.winW + 1,
      `${it.act} fully inside the viewport — never clipped`);
    assert.equal(it.clickable, true, `${it.act} is the top hit target at its own center`);
  }
  const cc = probe.items.find(x => x.act === 'cc');
  assert.match(cc.text, /掛題材/, 'the owner-clipped 「掛題材·條件」 item is present and labeled');
  // REAL input click (not el.click()) on the formerly clipped item opens its modal
  const c = await evaljs(`(() => { const b = document.querySelector('#cl-cp-menu [data-cp-act="cc"]');
    const r = b.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: c.x, y: c.y, button: 'left', clickCount: 1, buttons: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: c.x, y: c.y, button: 'left', clickCount: 1, buttons: 1 });
  await new Promise(r => setTimeout(r, 250));
  const after = await evaljs(`(() => {
    const ov = document.querySelector('.cl-cp-overlay');
    return { open: ov.classList.contains('open'),
      title: ov.querySelector('.cl-cp-m-head .name') && ov.querySelector('.cl-cp-m-head .name').textContent,
      menuClosed: !document.getElementById('cl-cp-menu').classList.contains('open') };
  })()`);
  assert.equal(after.open, true, 'a REAL CDP click on the formerly clipped item opens the 掛題材 modal');
  assert.match(after.title, /掛題材|題材/);
  assert.equal(after.menuClosed, true, 'the menu closes after an action');
});

test('CL-APP-06 (2q, patch-3): the open menu closes on scroll (any scroller) and on outside click, then reopens', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    card.querySelector('.cl-cp-more').click();
    await new Promise(r => setTimeout(r, 100));
    const menu = document.getElementById('cl-cp-menu');
    const open1 = menu.classList.contains('open');
    window.scrollTo(0, 60); // a REAL page scroll — capture-phase listener must close it
    await new Promise(r => setTimeout(r, 150));
    const afterScroll = menu.classList.contains('open');
    card.querySelector('.cl-cp-more').click(); // reopen at the new anchor
    await new Promise(r => setTimeout(r, 100));
    const open2 = menu.classList.contains('open');
    const topAfter = menu.getBoundingClientRect().top; // re-anchored, not stale
    document.body.click(); // outside click closes
    await new Promise(r => setTimeout(r, 100));
    const afterOutside = menu.classList.contains('open');
    return { open1, afterScroll, open2, topAfter, afterOutside };
  })()`);
  assert.equal(probe.open1, true);
  assert.equal(probe.afterScroll, false, 'scroll closes the open menu');
  assert.equal(probe.open2, true, 'the ⋯ trigger reopens the menu');
  assert.ok(probe.topAfter > 0, 'the reopened menu is re-anchored under the trigger (fixed position)');
  assert.equal(probe.afterOutside, false, 'outside click closes the menu');
});

test('CL-APP-06 (1g, patch-4/5): mini-map deferred-init contract + ticket-language-free conditions copy + months plumbing', () => {
  // patch-4 root cause: init inside a hidden/zero-size container breaks the
  // tile/marker layout — init MUST wait for a visible, sized container.
  assert.match(jsSource, /getBoundingClientRect\(\)[\s\S]{0,120}width > 8 && r\.height > 8/,
    'init waits for a non-zero box (never initializes into a hidden container)');
  assert.match(jsSource, /requestAnimationFrame\(waitBox\)/);
  assert.match(jsSource, /map\.resize\(\)/, 'second brace: resize after load');
  assert.match(jsSource, /assets\/vendor\/maplibre-gl\.mjs/, 'the VENDORED module — no CDN');
  assert.match(jsSource, /draggable: true/);
  assert.match(jsSource, /marker\.on\('dragend'/, 'dragging the pin syncs the lat/lng fields');
  assert.match(jsSource, /teardownMiniMap\(\); \/\/ patch-4: the GL context must not leak across modals/,
    'closing the modal removes the GL context');
  assert.match(jsSource, /wireSchematicPinDrop/, 'honest schematic fallback on module/tile failure');
  // patch-5 ①: ticket/engineering language is OUT of every user-visible string.
  // patch-4: the scan covers the tri-lingual T pack region only (declared at
  // `var T = {` and closed before the popup helpers) — the popup helper
  // dictionaries carry NO user-visible copy beyond fixed labels, and source
  // comments with ticket ids are not user-visible strings.
  (function () {
    const tStart = jsSource.indexOf('var T = {');
    const tEnd = jsSource.indexOf('\n  };', tStart);
    assert.ok(tStart >= 0 && tEnd > tStart, 'the T pack block is locatable');
    const pack = jsSource.slice(tStart, tEnd);
    for (const lang of ['zh-TW', 'en', 'ja']) {
      const m = pack.match(new RegExp(`'${lang}':\\s*\\{[\\s\\S]*?\\n    \\}`));
      assert.ok(m, `the ${lang} pack block is locatable`);
      assert.doesNotMatch(m[0], /CL-[A-Z]+-?\d*/, `dictionary ${lang} must not carry ticket numbers`);
    }
  })();
  // patch-5 ③: conflict path — the AI applies nothing, the user picks
  assert.match(jsSource, /if \(s\.conflict\)[\s\S]{0,200}ai_conflict\.replace\('\{m\}', s\.conflict\)/);
  // CL-CI-38 re-anchor: patch-5 shortened the conflict copy — the honest '未套用任何值' + the worker's conflict detail carry 請擇一.\n  assert.match(jsSource, /ai_conflict: '⚠ AI 未套用任何值：\{m\}'/);
  // patch-5 ②: the example copy is conflict-free (single time window)
  // CL-APP-09 patch-2: the example speaks in the photographer's voice (cloud-sea at dawn IS the deck window)
  assert.match(jsSource, /ai_ph: '例如：清晨六點前要有雲海，不要下雨，風要小，能見度要好'/);
  // patch-5 ④: months multi-select, default all-year, seasonal starters prefill
  assert.match(jsSource, /p_months: '適用月份'/);
  assert.match(jsSource, /id="cl-cp-cc-months"/);
  assert.match(jsSource, /out\.months = months\.sort/, 'readCc emits the sorted months array');
  assert.match(jsSource, /snow_scene: \{[\s\S]{0,120}months: \[12, 1, 2\]/, '雪景 starter prefills its season months');
  assert.match(jsSource, /seasonal_plant: \{[\s\S]{0,120}months: \[3, 4\]/, '櫻花 starter prefills its season months');
  assert.match(cssSource, /\.cl-cp-cc-months\{display:flex;flex-wrap:wrap/);
});

test('CL-APP-06 (2r, patch-4): real mini-map — DEFERRED init after the modal is visible, marker = lat/lng, drag syncs the fields', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  // CL-CI-38: private cards ride the official tier-tab pipeline (patch-6) —
  // non-✓推薦 points render only under their own tab / 全部. Switch first.
  await evaljs(`(async () => {
    const all = document.querySelector('#tier-tabs .tier-tab[data-tier="all"]');
    if (all) { all.click(); await new Promise(r => setTimeout(r, 600)); }
  })()`);
  const probe = await evaljs(`(async () => {
    // re-enable the REAL maplibre path for this test only
    delete window.__clcpMapLibre;
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp2"]');
    card.querySelector('.cl-cp-more').click();
    document.querySelector('#cl-cp-menu [data-cp-act="edit"]').click();
    // wait for the map instance (created only after the container has a box) —
    // or for the explicit no-WebGL fallback (CL-CI-39: headless CI has no GL
    // context, so MapLibre must not be constructed at all).
    const t0 = Date.now();
    while (!window.__clCpMiniMap && !window.__clCpMiniMapFallback && Date.now() - t0 < 10000)
      await new Promise(r => setTimeout(r, 100));
    if (window.__clCpMiniMapFallback) {
      const el = document.querySelector('#cl-cp-pinpick');
      const b = el.getBoundingClientRect();
      return { fallback: true, boxW: b.width, boxH: b.height,
               marked: el.getAttribute('data-minimap'),
               text: (document.querySelector('.cl-cp-overlay') || document).textContent };
    }
    const map = window.__clCpMiniMap;
    if (!map) return { error: 'mini-map never initialized' };
    // CL-CI-38 re-anchor: read the box from the map's OWN container —
    // getElementById('cl-cp-pinpick') can resolve a re-rendered sibling after
    // the patch-6 pipeline rebuilds the modal, while the map (and its guard)
    // live on the element the deferred init actually measured.
    const boxAtInit = map.getContainer().getBoundingClientRect();
    await new Promise(res => { if (map.loaded()) res(); else map.once('load', res); });
    const t1 = Date.now();
    while (!map.loaded() && Date.now() - t1 < 15000) await new Promise(r => setTimeout(r, 200));
    const marker = window.__clCpMiniMapMarker;
    const ll = marker && marker.getLngLat();
    const out = {
      boxW: boxAtInit.width, boxH: boxAtInit.height,
      styleLoaded: map.isStyleLoaded(), allTilesLoaded: map.loaded(),
      markerLat: ll && ll.lat, markerLng: ll && ll.lng,
      draggable: true,
    };
    // drag the marker (simulated dragend at a new coordinate) → fields sync
    marker.setLngLat([121.55, 24.65]);
    marker.fire('dragend');
    await new Promise(r => setTimeout(r, 300));
    const ov = document.querySelector('.cl-cp-overlay');
    out.latAfterDrag = ov.querySelector('#cl-cp-lat').value;
    out.lngAfterDrag = ov.querySelector('#cl-cp-lng').value;
    // manual lat/lng entry moves the marker back
    ov.querySelector('#cl-cp-lat').value = '24.8225';
    ov.querySelector('#cl-cp-lng').value = '121.7675';
    ov.querySelector('#cl-cp-lng').dispatchEvent(new Event('change'));
    await new Promise(r => setTimeout(r, 400));
    const ll2 = marker.getLngLat();
    out.markerAfterInput = [Number(ll2.lat.toFixed(4)), Number(ll2.lng.toFixed(4))];
    // closing the modal tears the GL context down
    ov.querySelector('[data-cp-close]').click();
    await new Promise(r => setTimeout(r, 150));
    out.mapRemoved = !window.__clCpMiniMap;
    return out;
  })()`);
  if (probe.fallback) {
    // CL-CI-39: without WebGL the product renders the schematic pin picker
    // instead of a zero-size MapLibre canvas. Assert that contract explicitly
    // (never skip): the picker is laid out, marked unsupported, and the modal
    // stays usable.
    assert.equal(probe.marked, 'unsupported', 'no-WebGL: the pin picker is marked unsupported');
    assert.ok(probe.boxW > 8 && probe.boxH > 8, 'no-WebGL: the schematic pin picker is laid out');
    assert.match(probe.text, /緯度|lat/i, 'no-WebGL: the lat/lng fields stay usable');
    return;
  }
  assert.ok(probe.boxW > 8 && probe.boxH > 8, 'the container HAS a size at init (root-cause guard)');
  assert.equal(probe.styleLoaded, true, 'the vendored maplibre style loads');
  assert.equal(probe.allTilesLoaded, true, 'basemap tiles finished loading');
  assert.ok(Math.abs(probe.markerLat - 24.8225) < 0.01 && Math.abs(probe.markerLng - 121.7675) < 0.01,
    'the edit modal marker sits at the place lat/lng (got ' + probe.markerLat + ',' + probe.markerLng + ')');
  assert.equal(probe.latAfterDrag, '24.6500', 'dragging the pin syncs the lat field');
  assert.equal(probe.lngAfterDrag, '121.5500', 'dragging the pin syncs the lng field');
  assert.deepEqual(probe.markerAfterInput, [24.8225, 121.7675], 'manual input moves the marker (two-way)');
  assert.equal(probe.mapRemoved, true, 'GL context removed on close');
});

test('CL-APP-06 (2s, patch-5): conditions modal — no ticket language, conflict AI branch, 適用月份 chips + seasonal starter prefill', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    card.querySelector('.cl-cp-more').click();
    document.querySelector('#cl-cp-menu [data-cp-act="cc"]').click();
    await new Promise(r => setTimeout(r, 250));
    const ov = document.querySelector('.cl-cp-overlay');
    ov.querySelector('.cl-cp-theme-row [data-cp-th-act="edit"]').click();
    await new Promise(r => setTimeout(r, 250));
    const out = {};
    // ① ticket/engineering language is gone from the visible modal text
    out.text = ov.textContent;
    out.ticketFree = !/CL-[A-Z]+-\\d+/.test(out.text);
    // ④ months chips: 12 checkboxes, none preselected (all-year default)
    const mo = [...ov.querySelectorAll('#cl-cp-cc-months input')];
    out.monthCount = mo.length;
    out.monthsDefault = mo.filter(b => b.checked).length;
    mo.find(b => b.value === '1').checked = true;
    mo.find(b => b.value === '2').checked = true;
    mo.find(b => b.value === '12').checked = true;
    mo.find(b => b.value === '12').dispatchEvent(new Event('change'));
    out.previewMonths = ov.querySelector('#cl-cp-cc-prev').textContent;
    // ④ seasonal starter prefills months + preview
    const gs = ov.querySelector('#cl-cp-cc-genre');
    gs.value = 'seasonal_plant';
    gs.dispatchEvent(new Event('change'));
    await new Promise(r => setTimeout(r, 100));
    out.sakuraMonths = [...ov.querySelectorAll('#cl-cp-cc-months input:checked')].map(b => Number(b.value));
    out.previewAfterStarter = ov.querySelector('#cl-cp-cc-prev').textContent;
    // ③ AI conflict: stub a conflicting parse → honest note, NOTHING applied
    const realFetch = window.__clcpFetch;
    window.__clcpFetch = (path, opts) => {
      if (path === '/api/v1/conditions/parse' && opts && opts.method === 'POST') {
        return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ ok: true, suggestions: { cloud: 'min', fog: 'none', rain: 'no', wind_max_ms: null, window_start: null, window_end: null, lead_minutes: null, conflict: '兩個時間窗不重疊，請擇一', confidence: 0.9 } }) });
      }
      return realFetch(path, opts);
    };
    const prevBefore = ov.querySelector('#cl-cp-cc-prev').textContent;
    ov.querySelector('#cl-cp-ai-text').value = '凌晨兩點也要雲海，而且只要清晨五點';
    ov.querySelector('#cl-cp-ai-go').click();
    await new Promise(r => setTimeout(r, 400));
    out.conflictNote = ov.querySelector('#cl-cp-ai-note').textContent;
    out.cloudAfterConflict = ov.querySelector('#cl-cp-sem-cloud').value;
    out.winStartAfterConflict = ov.querySelector('#cl-cp-ws0-start').value;
    out.previewUnchanged = ov.querySelector('#cl-cp-cc-prev').textContent === prevBefore;
    window.__clcpFetch = realFetch;
    return out;
  })()`);
  assert.equal(probe.ticketFree, true, 'no CL-* ticket numbers anywhere in the modal text');
  assert.equal(probe.monthCount, 12, '12 month chips');
  assert.equal(probe.monthsDefault, 0, 'default = all year (none checked)');
  assert.match(probe.previewMonths, /1–2,12/, 'preview prints the compacted month window');
  assert.deepEqual(probe.sakuraMonths, [3, 4], '櫻花 starter prefills its seasonal months');
  assert.match(probe.previewAfterStarter, /月 3–4/);
  // CL-CI-38 re-anchor: patch-5 copy — '⚠ AI 未套用任何值：{conflict}'
  assert.match(probe.conflictNote, /未套用任何值/, 'honest conflict message');
  assert.match(probe.conflictNote, /請擇一/);
  assert.equal(probe.cloudAfterConflict, 'any', 'the conflict did NOT change the cloud select (unchanged from the 櫻花 starter = any)');
  assert.equal(probe.winStartAfterConflict, '06:00', 'the conflict did NOT touch the time window (the 櫻花 starter\'s 06:00 survives)');
  assert.equal(probe.previewUnchanged, true, 'the preview is untouched by a conflicting parse');
});

test('CL-APP-06 (1h, patch-7→patch-4): private-card click → forecast popup rides the OFFICIAL renderer (source contract)', () => {
  // card body click opens the popup; buttons/links (⋯, upgrade CTA) never do
  assert.match(jsSource, /e\.target\.closest\('button, a, input, select'\)\) return;\s*\n\s*forecastModal\(p\);/);
  assert.match(jsSource, /e\.key === 'Enter' \|\| e\.key === ' '.*forecastModal\(p\)/s, 'keyboard parity: Enter/Space open the popup');
  // the popup renders ONLY stored data — the eval endpoint, never a new fetch
  assert.match(jsSource, /API \+ '\/' \+ p\.id \+ '\/eval'/);
  // patch-4 ROOT FIX: the popup does NOT grow its own anatomy — every block
  // is the OFFICIAL renderer through the app.js bridge (window.CLForecastRenderers)
  assert.match(jsSource, /window\.CLForecastRenderers/);
  assert.match(jsSource, /br\.quickView\(host, data\.spot\)/, '速覽 rides the official mountQuickView pipeline');
  assert.match(jsSource, /br\.stripHtml\(sd, sl/, '8 日方框 rides the official v2DayStripHtml (days normalised by modalDays)');
  assert.match(jsSource, /br\.modalDays\(data\.days, br\.localDate\(data\.tz, 0\)\)/,
    'CL-UI-126: the popup strip uses the modal 7-day normaliser, not a raw slice');
  assert.match(jsSource, /br\.daySub\(data\.spot, opp\)/, '今天題材判定 rides the official v2DaySubHtml');
  assert.match(jsSource, /br\.subjectRow\(\{ name: nm, stamp: stamp, cc: g\.cond \}/, '逐題材行 rides the official cl-subject-row builder');
  assert.match(jsSource, /br\.condFold\(conds, extra\)/, '條件摺疊 rides the official v2CondFoldHtml');
  assert.match(jsSource, /br\.registerSyntheticRows\(p\.id, data\.tree/, 'private verdicts feed the SAME subject-cards row pipeline');
  assert.match(jsSource, /br\.ensureCards\(\)/, 'synthetic rows register AFTER the derived artifact loads');
  // the retired private mini-strip anatomy is swept from the asset
  assert.doesNotMatch(jsSource, /cl-cp-qv-strip|qvDayCell|qvDayGrid|renderForecast|cl-cp-qv-row|cl-cp-qv-cond|cl-cp-qv-quick/,
    'the popup never renders its own 8-cell mini strip / own rows / own fold / own quick line');
  // the hour matcher mirrors the worker exactly (lenient defaults + missing-value honesty)
  assert.match(jsSource, /limit >= 100\) continue;/);
  assert.match(jsSource, /limit <= 0\) continue;/);
  assert.match(jsSource, /if \(val == null\) return false;/);
  // anchor windows expand client-side with the SAME solar math (mirror, kept in sync by test)
  assert.match(jsSource, /BEGIN SOLAR MIRROR \(workers\/api\/src\/solar\.js/);
  assert.match(jsSource, /END SOLAR MIRROR/);
  assert.match(jsSource, /if \(!b\) continue; \/\/ unresolvable/, 'unresolvable anchor windows never match (fail-closed, never whole-day)');
  // honest fallbacks: honest 資料不足 days + no fabricated sections
  assert.match(jsSource, /qv_load_fail/);
  assert.doesNotMatch(jsSource, /guide_details|research-details/, 'a private point has NO researched guide — the section stays absent');
  // patch-9: official meta-line anatomy — coords at 3 decimals, GMT±n zone
  assert.match(jsSource, /function cpMetaLine\(p\)/);
  assert.match(jsSource, /toFixed\(3\)/);
  assert.match(jsSource, /function cpTzLabel\(tz\)/);
  assert.match(jsSource, /shortOffset/);
  assert.doesNotMatch(jsSource, /esc\(p\.lat\)/, 'raw full-precision coords never render');
  // patch-9: the popup (and only the popup) opts out of the 100vh sheet stretch
  assert.match(jsSource, /openOverlay\(html, 'cl-cp-qv-modal'\)/);
  assert.match(cssSource, /\.cl-cp-overlay \.cl-cp-modal\.cl-cp-qv-modal\{min-height:auto\}/);
  // 題材 panel entry: the user's custom conditions open the conditions panel
  assert.match(jsSource, /entry\.addEventListener\('click', function \(\) \{ ccModal\(p\); \}\)/);
  // 🔔 is REAL for private points: the bell carries the rule's own conditions
  // (custom-mode rule) and the worker cron reaches the private eval KV
  assert.match(jsSource, /cc: g\.cond/, 'subject-row bells pass the group conditions (the data-rem-cc attribute lives in the shared app.js builder)');
  const remSrc = readFileSync(join(WEB, 'assets', 'reminders-client.js'), 'utf8');
  assert.match(remSrc, /data-rem-cc/);
  assert.match(remSrc, /customConditions: cc/, 'the client posts a CUSTOM-mode rule (mutually exclusive with opportunityId)');
  assert.match(remSrc, /opportunityId: oppId \|\| undefined/);
  const notifySrc = readFileSync(join(WEB, 'workers', 'api', 'src', 'notify.js'), 'utf8');
  assert.match(notifySrc, /v1:evals:custom:\$\{rule\.place_id\}/, 'the cron falls back to the private eval KV — the bell is never a dead rule');
  // worker endpoint wiring on the popup side
  const workerSrc = readFileSync(join(WEB, 'workers', 'api', 'src', 'custom-places.js'), 'utf8');
  assert.match(workerSrc, /export async function handleCustomPlaceEval/);
  assert.match(workerSrc, /v1:evals:custom:\$\{placeId\}/);
  const idxSrc = readFileSync(join(WEB, 'workers', 'api', 'src', 'index.js'), 'utf8');
  assert.match(idxSrc, /custom_places\\\/\(\[\\w-\]\+\)\\\/eval/);
  // the shared official builders exist in app.js (one implementation, two hosts)
  const appSrc = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
  assert.match(appSrc, /function v2CondFoldHtml\(conditions,extraHtml\)/);
  assert.match(appSrc, /function clSubjectRowLine\(entry,spotId,hidden\)/);
  assert.match(appSrc, /window\.CLForecastRenderers=\{/);
});

test('CL-APP-06 (2t, patch-4): clicking a private card opens the forecast popup — OFFICIAL anatomy (quick view + 7-day strip + subject rows + condition fold); ⋯ still opens the menu', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    const out = {};
    // CL-CI-43: the selected day used to be an IMPLICIT assumption — after
    // ~22:00 the page's own day picker rolls to 明天, so this test measured
    // tomorrow's band/strip while asserting today's shape and red-ed every
    // night (runs 45063562817, 45708924071). Pin the selection explicitly to
    // 今天 and keep every assertion below unchanged in strength.
    const dayTrigger = document.querySelector('#day-picker-trigger');
    if (dayTrigger) {
      dayTrigger.click();
      await new Promise(r => setTimeout(r, 120));
      const todayOpt = document.querySelector('#day-picker-panel .day-option[data-day="today"]');
      if (todayOpt) {
        todayOpt.click();
        await new Promise(r => setTimeout(r, 350));
      }
    }
    const dayTriggerAfter = document.querySelector('#day-picker-trigger');
    out.selectedDay = dayTriggerAfter ? dayTriggerAfter.dataset.day : null;
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    // ⋯ must NOT open the popup (menu parity from patch-3 is preserved)
    card.querySelector('.cl-cp-more').click();
    await new Promise(r => setTimeout(r, 100));
    out.menuOpensNotPopup = document.querySelector('#cl-cp-menu').classList.contains('open') && !document.querySelector('.cl-cp-overlay').classList.contains('open');
    document.body.click(); // close menu
    await new Promise(r => setTimeout(r, 50));
    // card-body click → forecast popup
    card.querySelector('.spot-name').click();  // CL-CI-38: the bridge card's name span is the OFFICIAL .spot-name
    await new Promise(r => setTimeout(r, 250));
    const ov = document.querySelector('.cl-cp-overlay');
    out.popupOpens = ov.classList.contains('open');
    out.name = ov.querySelector('.cl-cp-m-head .name').textContent;
    // wait for the eval fetch + the derived artifact to land (loading gone)
    const t0 = Date.now();
    while (ov.querySelector('#cl-cp-qv-days .cl-cp-qv-loading') && Date.now() - t0 < 8000) await new Promise(r => setTimeout(r, 100));
    // ── 速覽 rides the OFFICIAL place-quick-view anatomy (mountQuickView)
    const qv = ov.querySelector('#cl-cp-qv-host');
    out.qvSection = !!ov.querySelector('.place-quick-view.modal-quick-view');
    out.qvTitle = qv.querySelector('.q-t') && qv.querySelector('.q-t').textContent;
    out.qvChip = qv.querySelector('.q-chip') && qv.querySelector('.q-chip').textContent;
    out.qvChipTier = qv.querySelector('.q-chip') && qv.querySelector('.q-chip').getAttribute('data-tier');
    out.bandCells = qv.querySelectorAll('.quick-band .band i').length;
    out.qvNext = qv.querySelector('.q-next') && qv.querySelector('.q-next').textContent;
    out.qvWx = qv.querySelector('.q-wx') && qv.querySelector('.q-wx').textContent;
    // ── 8 日方框 rides the OFFICIAL v2-strip-cell anatomy (one strip, never
    //    a per-subject 8-cell mini strip)
    const cells = [...ov.querySelectorAll('#cl-cp-qv-days .v2-strip-cell')];
    out.cellCount = cells.length;
    out.cellCls = [...new Set(cells.map(c => c.className.replace(/ sel| dragging/g, '')))];
    out.day1 = cells[0] && (cells[0].className + ' | ' + cells[0].textContent);
    out.day2 = cells[1] && (cells[1].className + ' | ' + cells[1].textContent);
    out.day7 = cells[6] && (cells[6].className + ' | ' + cells[6].textContent);
    // 今天題材判定 rides the official v2-day-sub anatomy
    out.daySub = ov.querySelector('#cl-cp-qv-days .v2-day-sub') && ov.querySelector('#cl-cp-qv-days .v2-day-sub').textContent;
    // ── 逐題材行 rides the OFFICIAL cl-subject-row anatomy (短名 + stamp + 🔔)
    const rows = [...ov.querySelectorAll('#cl-cp-qv-subjects .cl-subject-row')].map(r => ({
      name: r.querySelector('.cl-subject-name').textContent,
      window: r.querySelector('.cl-subject-window').textContent,
      bell: !!r.querySelector('.cl-rem-btn.cl-rem-compact'),
      bellPlace: r.querySelector('.cl-rem-btn') && r.querySelector('.cl-rem-btn').getAttribute('data-rem-place'),
      bellCc: r.querySelector('.cl-rem-btn') && r.querySelector('.cl-rem-btn').getAttribute('data-rem-cc'),
    }));
    out.subjectRows = rows;
    // ── 條件摺疊 rides the OFFICIAL v2-cond-details anatomy (必須 group)
    const cond = ov.querySelector('#cl-cp-qv-subjects .v2-cond-details');
    out.condSummary = cond ? cond.querySelector('summary').textContent : null;
    if (cond) {
      cond.setAttribute('open', '');
      out.condGroup = [...cond.querySelectorAll('.v2-cond-group .research-label')].map(l => l.textContent);
      out.condRows = [...cond.querySelectorAll('.v2-cond')].map(r => r.textContent);
    }
    // no fabricated sections: a private point has NO guide block
    out.noGuide = !ov.querySelector('#cl-cp-qv-subjects .research-details, #cl-cp-qv-subjects .cl-cp-guide');
    out.qvModalCls = ov.querySelector('.cl-cp-modal').className;
    // 題材 panel entry opens the conditions panel (user's custom conditions there)
    ov.querySelector('#cl-cp-qv-subject-entry').click();
    await new Promise(r => setTimeout(r, 250));
    out.subjectPanelTitle = ov.querySelector('.cl-cp-m-head .name') && ov.querySelector('.cl-cp-m-head .name').textContent;
    // ✕ closes
    ov.querySelector('[data-cp-close]').click();
    await new Promise(r => setTimeout(r, 100));
    out.closed = !ov.classList.contains('open');
    // keyboard parity: Enter on the card opens the popup again
    card.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    await new Promise(r => setTimeout(r, 150));
    out.keyboardOpens = ov.classList.contains('open');
    ov.querySelector('[data-cp-close]').click();
    return out;
  })()`);
  assert.equal(probe.menuOpensNotPopup, true, '⋯ opens the menu, not the popup');
  assert.equal(probe.popupOpens, true, 'card click opens the forecast popup');
  assert.match(probe.name, /霧社水庫西岸岔路/);
  // ── official quick-view anatomy: title + tier chip + 24h band + next/wx
  assert.equal(probe.qvSection, true, 'the quick view rides the OFFICIAL place-quick-view section');
  assert.match(probe.qvTitle, /現在去會怎樣/);
  assert.match(probe.qvChip, /(✓|○)/, `the chip is the official time-aware tier (✓推薦 or ○可拍·窗已過); got ${JSON.stringify(probe.qvChip)} tier=${JSON.stringify(probe.qvChipTier)}`);
  assert.ok(['ok', 'mid'].includes(probe.qvChipTier), 'chip tier is a valid official level for a clean-air place');
  assert.equal(probe.bandCells, 24, 'the 24h mini band renders the selected day via the SHARED v2BandHtml');
  // ── official 7-day strip anatomy: one strip, honest cells
  assert.equal(probe.selectedDay, 'today', 'the page day selection is pinned to 今天 explicitly (CL-CI-43)');
  assert.equal(probe.cellCount, 7,
    `the strip is always 7 days (DAY_KEYS: today..day6); got ${probe.cellCount}`);
  assert.match(probe.day1, /v2-ok/, 'day 1: fit hours exist inside the group window → ✓ cell');
  assert.match(probe.day2, /v2-bad/, 'day 2: the group fails on low cloud → ✗ cell');
  assert.match(probe.day2, /低雲/, 'the ✗ word comes from the bundle fail dictionary (single truth)');
  assert.match(probe.day7, /v2-unk/, 'day 7: honest 資料不足 — the ~48h feed does not cover it');
  assert.match(probe.daySub || '', /今天題材判定/, '今天題材判定 rides the official v2-day-sub row');
  // ── official subject-row anatomy: 短名 + next window stamp + 🔔
  assert.equal(probe.subjectRows.length, 1, 'ONE row per theme group');
  assert.match(probe.subjectRows[0].name, /雲海窗/);
  assert.match(probe.subjectRows[0].window, /11\/16 05:00/, 'the window slot carries the official next-window stamp format');
  assert.equal(probe.subjectRows[0].bell, true, 'the row-end 🔔 is the reminder bell (official anatomy)');
  assert.equal(probe.subjectRows[0].bellPlace, 'cp1');
  assert.ok(probe.subjectRows[0].bellCc, 'the bell carries the group conditions (custom-mode rule — never a dead rule)');
  // ── official condition fold anatomy: 必須 group + threshold rows + 時窗 label row
  assert.match(probe.condSummary, /條件 ×1/, 'one metric constraint (低雲 ≤15%); the window is a label row, not a fake metric');
  assert.equal(probe.condGroup.length, 1, 'the REQUIRED group only — private sets carry no booster/penalty roles');
  assert.match(probe.condGroup[0], /成立條件/, 'the REQUIRED group label (official semantics)');
  assert.equal(probe.condRows.length, 2);
  assert.match(probe.condRows[0], /低雲/);
  assert.match(probe.condRows[0], /≤\s*15\s*%/);
  assert.match(probe.condRows[1], /時窗/);
  assert.match(probe.condRows[1], /04:30–07:00/);
  assert.equal(probe.noGuide, true, 'no fabricated 攝影指南 for a private point (honest absence)');
  assert.match(probe.qvModalCls, /cl-cp-qv-modal/, 'the popup carries the content-height class');
  assert.match(probe.subjectPanelTitle, /掛題材|題材/, '題材 entry opens the theme list manager');
  assert.equal(probe.closed, true, '✕ closes the popup');
  assert.equal(probe.keyboardOpens, true, 'Enter on the card opens the popup');
});

test('CL-APP-09-p3: at 390 the forecast popup height follows its content (never a full blank sheet)', async () => {
  await bootBrowser();
  await setViewport(390, 844, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    card.querySelector('.spot-name').click();  // CL-CI-38: the bridge card's name span is the OFFICIAL .spot-name
    await new Promise(r => setTimeout(r, 250));
    const ov = document.querySelector('.cl-cp-overlay');
    const m = ov.querySelector('.cl-cp-modal');
    const t0 = Date.now();
    while (m.querySelector('#cl-cp-qv-days .cl-cp-qv-loading') && Date.now() - t0 < 5000) await new Promise(r => setTimeout(r, 100));
    await new Promise(r => setTimeout(r, 150));
    const mr = m.getBoundingClientRect();
    const cs = getComputedStyle(m);
    // the editor sheet (no cl-cp-qv-modal class) must keep the 100vh keyboard fit
    return { h: Math.round(mr.height), vh: window.innerHeight, cls: m.className, minH: cs.minHeight };
  })()`);
  assert.match(probe.cls, /cl-cp-qv-modal/);
  assert.ok(probe.h <= probe.vh - 40,
    `popup height ${probe.h}px must follow the content (viewport ${probe.vh}px — no full-height stretch)`);
  assert.ok(probe.h > 200, 'the popup still renders its full anatomy');
});

test('CL-APP-06 (2u, patch-8): theme manager CRUD — create (dup names NOT blocked) rides the real POST path; delete reopens the refreshed list', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  // CL-CI-38: private cards ride the official tier-tab pipeline (patch-6) —
  // non-✓推薦 points render only under their own tab / 全部. Switch first.
  await evaljs(`(async () => {
    const all = document.querySelector('#tier-tabs .tier-tab[data-tier="all"]');
    if (all) { all.click(); await new Promise(r => setTimeout(r, 600)); }
  })()`);
  const probe = await evaljs(`(async () => {
    const out = {};
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp2"]'); // no groups yet
    card.querySelector('.cl-cp-more').click();
    document.querySelector('#cl-cp-menu [data-cp-act="cc"]').click();
    await new Promise(r => setTimeout(r, 250));
    const ov = document.querySelector('.cl-cp-overlay');
    out.emptyNote = !!ov.querySelector('.cl-cp-th-empty');
    // create group #1 through the real form → real POST /themes
    ov.querySelector('#cl-cp-th-add').click();
    await new Promise(r => setTimeout(r, 200));
    let nm = ov.querySelector('#cl-cp-theme-name');
    nm.value = '星光窗';
    nm.dispatchEvent(new Event('input'));
    ov.querySelector('#cl-cp-cc-precip').value = '0.2';
    ov.querySelector('#cl-cp-cc-precip').dispatchEvent(new Event('change'));
    ov.querySelector('#cl-cp-cc-submit').click();
    // waitThemeList polls until the refreshed list reopens
    const t0 = Date.now();
    while (!ov.querySelector('.cl-cp-theme-row') && Date.now() - t0 < 6000) await new Promise(r => setTimeout(r, 150));
    out.listAfterCreate = {
      title: ov.querySelector('.cl-cp-m-head .name').textContent,
      count: ov.querySelector('.cl-cp-th-count').textContent,
      rows: [...ov.querySelectorAll('.cl-cp-theme-row .cl-cp-theme-info .n')].map(n => n.textContent),
    };
    // create #2 with the SAME name — duplicate names are NOT blocked
    ov.querySelector('#cl-cp-th-add').click();
    await new Promise(r => setTimeout(r, 200));
    nm = ov.querySelector('#cl-cp-theme-name');
    nm.value = '星光窗';
    nm.dispatchEvent(new Event('input'));
    ov.querySelector('#cl-cp-cc-wind').value = '5';
    ov.querySelector('#cl-cp-cc-wind').dispatchEvent(new Event('change'));
    ov.querySelector('#cl-cp-cc-submit').click();
    const t1 = Date.now();
    while (ov.querySelectorAll('.cl-cp-theme-row').length < 2 && Date.now() - t1 < 6000) await new Promise(r => setTimeout(r, 150));
    out.dupRows = [...ov.querySelectorAll('.cl-cp-theme-row .cl-cp-theme-info .n')].map(n => n.textContent);
    // delete the FIRST group → honest toast + refreshed list back to 1
    window.__cpThemes_snapshot = JSON.parse(JSON.stringify(window.__cpThemes));
    ov.querySelector('.cl-cp-theme-row [data-cp-th-act="del"]').click();
    await new Promise(r => setTimeout(r, 200));
    ov.querySelector('#cl-cp-th-del-confirm').click();
    const t2 = Date.now();
    // the confirm modal has NO theme rows — wait until the LIST modal reopens
    // (th-count present) AND the surviving row count is ≤1, not just rows ≤1
    while ((ov.querySelectorAll('.cl-cp-theme-row').length > 1 || !ov.querySelector('.cl-cp-th-count')) && Date.now() - t2 < 6000) await new Promise(r => setTimeout(r, 150));
    out.afterDelete = {
      toast: document.querySelector('.cl-cp-toast').textContent,
      rows: [...ov.querySelectorAll('.cl-cp-theme-row .cl-cp-theme-info .n')].map(n => n.textContent),
      count: ov.querySelector('.cl-cp-th-count').textContent,
    };
    return out;
  })()`);
  assert.equal(probe.emptyNote, true, 'the empty list explains itself (general baseline)');
  assert.match(probe.listAfterCreate.count, /1\/5/, 'honest count after the create');
  assert.deepEqual(probe.listAfterCreate.rows, ['星光窗']);
  assert.equal(probe.dupRows.length, 2, 'duplicate name is NOT blocked — both groups saved');
  assert.ok(probe.dupRows.every(n => n === '星光窗'));
  assert.match(probe.afterDelete.toast, /已刪除/, 'honest deletion toast');
  assert.deepEqual(probe.afterDelete.rows, ['星光窗'], 'exactly one group survives the delete');
  assert.match(probe.afterDelete.count, /1\/5/);
});

test('CL-APP-06 (2g): browser teardown', async () => { await teardownBrowser(); });


// CL-CI-40: release the browser, the CDP socket and the static server even when a
// test aborts or fails. Without a file-level hook the old "teardown" TEST only ran
// if every earlier test completed, so one hang left a Chrome process behind and the
// runner eventually reported the remaining cases as `cancelled` (OOM).
test.after(async () => {
  try { await teardownBrowser(); } catch (_) { /* already gone */ }
});
