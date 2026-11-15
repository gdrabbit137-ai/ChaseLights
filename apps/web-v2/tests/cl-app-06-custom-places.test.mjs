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
  assert.match(htmlSource, /assets\/custom-places\.css\?v=clapp06b/);
  assert.match(htmlSource, /assets\/custom-places\.js\?v=clapp06b/);
  // untouched neighbors keep their stamps (per-file cache-bust rule)
  assert.match(htmlSource, /assets\/app\.js\?v=clui101/);
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
  // nomination → review queue; soft delete (30-day revive) copy
  assert.match(jsSource, /nomModal/);
  assert.match(jsSource, /30 天|30 days|30 日/);
  // member gating: signed-out users get the login notice, never a silent action
  assert.match(jsSource, /needLoginModal/);
  // member-auth integration via the chaselights:auth broadcast
  assert.match(jsSource, /chaselights:auth/);
  // test seam used by this harness (stubbed network)
  assert.match(jsSource, /__clcpFetch/);
  // 📍 current-location: browser Geolocation API + Capacitor plugin fallback,
  // one implementation, honest no-tracking note, bounded timeout
  assert.match(jsSource, /__clcpGeo/);
  assert.match(jsSource, /useMyLocation/);
  assert.match(jsSource, /navigator\.geolocation\.getCurrentPosition\(resolve, reject, opts\)/);
  assert.match(jsSource, /cap\.Plugins\.Geolocation/);
  assert.match(jsSource, /timeout: 10000/);
  assert.match(jsSource, /不會追蹤你的行蹤|never tracked|追跡しません/);
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

test('CL-APP-06 (1d): tri-lingual dictionary parity in the asset', () => {
  const keys = ['priv_badge', 'v_all', 'v_official', 'v_private', 'trial_expired', 'trial_note',
    'deferred_note', 'm_edit', 'm_cc', 'm_nom', 'm_del', 'add_title', 'ro_elev', 'ro_tz',
    'nom_title', 'del_title', 'count_fmt',
    // 📍 current-location copy must exist in ALL three dictionaries
    'geo_btn', 'geo_note', 'geo_working', 'geo_denied', 'geo_timeout', 'geo_error'];
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
  // the form still submits CONCRETE values only
  assert.match(jsSource, /payload = \{ customConditions: readCc\(\) \}/);
});

const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs, ready;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

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
    await send('Page.addScriptToEvaluateOnNewDocument', { source: `
      window.__clcpFetch = function (path, opts) {
        if (path.indexOf('/api/v1/custom_places/pin_info') === 0) {
          return Promise.resolve({ ok: true, status: 200, json: function () {
            return Promise.resolve({ ok: true, elevation: 80, timezone: 'Asia/Taipei', utcOffsetSeconds: 28800, elevationOutlier: false });
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
              quota: { used: 3, cap: 50 },
              degraded: false, degradedMessage: null,
              places: [
                { id: 'cp1', name: '霧社水庫西岸岔路', lat: 23.9412, lng: 121.1523, elevation: 1150, timezone: 'Asia/Taipei',
                  customConditions: { cloud_low_max: 15, visibility_min_km: 12, window_start: '04:30', window_end: '07:00' },
                  status: 'active', createdAt: '', updatedAt: '',
                  evaluation: { tier: 'rec', reason: null, window: '2026-11-16 05:00', evaluatedAt: '2026-11-15T10:00:00Z', private: true },
                  refresh: { intervalHours: 6, label: '6h', energySaver: false }, fetchDeferred: false, fetchDueAt: null },
                { id: 'cp2', name: '礁溪自家陽台展望', lat: 24.8225, lng: 121.7675, elevation: 80, timezone: 'Asia/Taipei',
                  customConditions: null, status: 'active', createdAt: '', updatedAt: '',
                  evaluation: { tier: 'shoot', reason: null, window: '2026-11-16 06:00', evaluatedAt: '2026-11-15T10:00:00Z', private: true },
                  refresh: { intervalHours: 6, label: '6h', energySaver: false }, fetchDeferred: false, fetchDueAt: null },
                { id: 'cp3', name: '苫小牧西港堤防燈點', lat: 42.6389, lng: 141.3556, elevation: 3, timezone: 'Asia/Tokyo',
                  customConditions: { wind_max_ms: 5 }, status: 'active', createdAt: '', updatedAt: '',
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
              ],
            });
          } });
        }
        return Promise.resolve({ ok: false, status: 404, json: function () { return Promise.resolve({ error: 'stub 404' }); } });
      };
    ` });
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
  await send('Page.navigate', { url: baseURL });
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>25000){clearInterval(iv);reject(new Error('cards never rendered'));}
    },100);
  })`);
  await evaljs(`document.dispatchEvent(new CustomEvent('chaselights:auth', { detail: { member: { id: 'u1', displayName: '晨曦旅人', level: 'paid' } } }))`);
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.cl-cp-card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>10000){clearInterval(iv);reject(new Error('private cards never rendered'));}
    },100);
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
  assert.match(probe.chip, /3\/50/, 'quota chip shows used/cap honestly');
  assert.match(probe.chip, /Premium/);
  assert.match(probe.count, /官方/, 'count line is the honest 共 N 官方＋M 私人點 identity');
  const allTab = probe.tabs.find(x => x.key === 'all'), offTab = probe.tabs.find(x => x.key === 'official'), privTab = probe.tabs.find(x => x.key === 'private');
  assert.equal(allTab.n, offTab.n + privTab.n, '全部 count = 官方 + 私人 (never mis-added)');
  assert.equal(allTab.sel, true);
  assert.ok(privTab.n >= 5);
});

test('CL-APP-06 (2b): private card anatomy — gray badge computed style + tier + ⋯ menu opens', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(() => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    if (!card) return { error: 'no cp1 card' };
    const badge = card.querySelector('.cl-cp-priv-badge');
    const cs = badge ? getComputedStyle(badge) : null;
    const more = card.querySelector('.cl-cp-more');
    const r = more.getBoundingClientRect();
    more.click();
    const menu = card.querySelector('.cl-cp-menu');
    const acts = [...menu.querySelectorAll('[data-cp-act]')].map(b => b.getAttribute('data-cp-act'));
    const menuOpen = getComputedStyle(menu).display;
    return {
      badgeText: badge && badge.textContent,
      color: cs && cs.color, bg: cs && cs.backgroundColor,
      tier: card.querySelector('.cl-cp-tier') && card.querySelector('.cl-cp-tier').textContent,
      window: card.querySelector('.cl-cp-window') && card.querySelector('.cl-cp-window').textContent,
      cc: card.querySelector('.cl-cp-cc-txt') && card.querySelector('.cl-cp-cc-txt').textContent,
      acts, menuOpen,
    };
  })()`);
  assert.match(probe.badgeText, /私人/);
  // gray identity: the badge color must be the neutral --cl-grey family
  // (#98A4B3 = 152,164,179), NEVER the green/amber/red semantic tokens
  assert.equal(probe.color, 'rgb(152, 164, 179)', `badge color must be --cl-grey-text, got ${probe.color}`);
  assert.match(probe.tier, /✓/, 'rec private card carries the ✓ tier');
  assert.match(probe.window, /05:00/, 'rec window rides the card');
  assert.match(probe.cc, /低雲≤15/, 'CL-UI-99 condition summary (only tuned params)');
  assert.deepEqual(probe.acts.sort(), ['cc', 'del', 'edit', 'nom']);
  assert.equal(probe.menuOpen, 'block', '⋯ menu opens');
});

test('CL-APP-06 (2c): trial-expired card is gray + honest 試用期滿 + upgrade CTA; deferred card honest note', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
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
    out.officialView = {
      priv: getComputedStyle(document.querySelector('.cl-cp-card[data-cp-id="cp1"]')).display,
      official: document.querySelector('#spots-container .card:not(.cl-cp-card)') ? getComputedStyle(document.querySelector('#spots-container .card:not(.cl-cp-card)')).display : 'absent',
    };
    document.querySelector('.cl-cp-view-tab[data-cp-view="all"]').click();
    await new Promise(r => setTimeout(r, 300));
    return out;
  })()`);
  assert.notEqual(probe.privateView.priv, 'none', 'private tab shows private cards');
  assert.equal(probe.privateView.official, 'none', 'private tab hides official cards');
  assert.equal(probe.officialView.priv, 'none', 'official tab hides private cards');
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
    const submitReady = ov.querySelector('#cl-cp-submit').classList.contains('ready');
    return { open, lat, lng, elev, tz, submitReady };
  })()`);
  assert.equal(probe.open, true);
  assert.ok(probe.lat, 'click-to-drop fills lat');
  assert.ok(probe.lng, 'click-to-drop fills lng');
  assert.equal(probe.elev, '80 m', 'DEM elevation auto-filled (read-only value)');
  assert.match(probe.tz, /Asia\/Taipei/, 'timezone auto-filled (IANA)');
  assert.equal(probe.submitReady, true);
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
test('CL-APP-06 (2h): conditions modal — semantic selects, transparent mapping, genre starter, advanced inputs', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp1"]');
    card.querySelector('.cl-cp-more').click();
    card.querySelector('[data-cp-act="cc"]').click();
    await new Promise(r => setTimeout(r, 200));
    const ov = document.querySelector('.cl-cp-overlay');
    const sel = ov.querySelector('#cl-cp-sem-cloud');
    const map0 = ov.querySelector('#cl-cp-sem-map-cloud').textContent;
    const low0 = ov.querySelector('#cl-cp-cc-low').value;
    // change cloud → mapped label + concrete advanced input update
    sel.value = 'half';
    sel.dispatchEvent(new Event('change'));
    await new Promise(r => setTimeout(r, 100));
    const map1 = ov.querySelector('#cl-cp-sem-map-cloud').textContent;
    const low1 = ov.querySelector('#cl-cp-cc-low').value;
    const prev = ov.querySelector('#cl-cp-cc-prev').textContent;
    const genreOptions = ov.querySelectorAll('#cl-cp-cc-genre option').length;
    // genre starter prefills semantics + window
    const gs = ov.querySelector('#cl-cp-cc-genre');
    gs.value = 'cloud_sea';
    gs.dispatchEvent(new Event('change'));
    await new Promise(r => setTimeout(r, 100));
    const starterCloud = ov.querySelector('#cl-cp-sem-cloud').value;
    const starterWin = [ov.querySelector('#cl-cp-cc-start').value, ov.querySelector('#cl-cp-cc-end').value];
    const advanced = ov.querySelector('.cl-cp-cc-advanced');
    return { open: ov.classList.contains('open'), semCount: ov.querySelectorAll('.cl-cp-sem-select').length,
      map0, low0, map1, low1, prev, genreOptions, starterCloud, starterWin, advancedOpenDefault: advanced.open };
  })()`);
  assert.equal(probe.open, true);
  assert.equal(probe.semCount, 3, 'three semantic dropdowns (cloud/fog/rain)');
  assert.match(probe.map0, /低雲 ≤20%/, 'transparent mapped value shown (15% rounds to the 越少越好 tier)');
  assert.equal(probe.low0, '15', 'advanced input keeps the actual stored concrete value');
  assert.match(probe.map1, /低雲 ≤50%/);
  assert.equal(probe.low1, '50', 'changing the semantic select writes the mapped concrete value');
  assert.match(probe.prev, /低雲≤50/, 'preview updates from the mapped value');
  assert.ok(probe.genreOptions >= 22, '21 genre starters + the empty option');
  assert.equal(probe.starterCloud, 'min', '雲海 starter applies');
  assert.deepEqual(probe.starterWin, ['04:30', '07:00']);
  assert.equal(probe.advancedOpenDefault, false, 'advanced raw inputs collapsed by default');
});
test('CL-APP-06 (2i): ✨ one-sentence AI parse fills the semantic selects (AI only translates — concrete values still submitted)', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(async () => {
    const card = document.querySelector('.cl-cp-card[data-cp-id="cp2"]');
    card.querySelector('.cl-cp-more').click();
    card.querySelector('[data-cp-act="cc"]').click();
    await new Promise(r => setTimeout(r, 250));
    const ov = document.querySelector('.cl-cp-overlay');
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
      win: [ov.querySelector('#cl-cp-cc-start').value, ov.querySelector('#cl-cp-cc-end').value],
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

test('CL-APP-06 (2g): browser teardown', async () => { await teardownBrowser(); });

