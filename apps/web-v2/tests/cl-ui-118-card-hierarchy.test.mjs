// CL-UI-118 (sub-commit A) — the homepage card is FOUR stacked layers, plus the
// action row last, and side-by-side cards line up layer-for-layer.
//
// Owner spec (docs/backlog/cl-ui-118-card-hierarchy.md): L1 identification
// (name + city/landform sub-label | ✓ badge + ★ + ONE spot-level bell), L2 the
// now row as its own full-width line ABOVE the subject block, L4 elevation and
// the astronomical numbers on their own fixed never-wrapping line with the
// action row last. L3 (headline-subject typography) is a separate follow-up —
// this file asserts nothing about its type size or tint.
//
// Every assertion here is a REAL DOM assertion in headless Chrome against the
// shipped page (assets/app.js + app.css), not a source regex: card order, the
// single bell, the tooltip carried cap text, the terrain/now separation and the
// cross-card alignment are all measured with getBoundingClientRect().
//
// Harness: static server rooted at the repo + raw CDP (no playwright on
// Windows), the CL-UI-117 pattern. The now sidecar is generated at run time so
// the wall clock never rots the fixture, and EVERY row reports the visibility
// cap (24.8 km ≥ VIS_CAP_KM 24.1) so the 「資料上限」 wording contract is
// exercised on real cards.
//
// Run: CHROMIUM_EXECUTABLE="C:/Program Files/Google/Chrome/Application/chrome.exe" \
//      node --test apps/web-v2/tests/cl-ui-118-card-hierarchy.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
import {readFileSync, mkdtempSync, existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP = join(HERE, '..', '..', '..');
const CSS = readFileSync(join(APP, 'assets', 'app.css'), 'utf8');
const APPJS = readFileSync(join(APP, 'assets', 'app.js'), 'utf8');
const FIXTURE = JSON.parse(readFileSync(join(HERE, 'fixtures', 'now-latest.clui117.json'), 'utf8'));
const FIXTURE_IDS = Object.keys(FIXTURE.places);

const BROWSER = [
  process.env.CHROMIUM_EXECUTABLE,
  process.env.CHROME_PATH,
  ...(process.platform === 'win32'
    ? ['C:/Program Files/Google/Chrome/Application/chrome.exe',
       'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe']
    : ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']),
].filter(Boolean).find(p => existsSync(p)) || null;
// CL-CI-140: with no binary, register ONE skipped case and never boot.
const NO_BROWSER = 'no browser binary available in this environment; this suite runs in the Chromium job';
const browserTest = BROWSER ? test : () => {};
if (!BROWSER) test('CL-UI-118 card hierarchy (browser)', {skip: NO_BROWSER}, () => {});

const MIME = {'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.ico':'image/x-icon','.woff2':'font/woff2','.jpg':'image/jpeg'};
const NO_STORE = {'cache-control':'no-store'};
const TPE = 'Asia/Taipei';
const CAP_VIS_KM = 24.8;   // ≥ VIS_CAP_KM (24.1) — every row exercises the cap wording
const tpeDate = () => new Intl.DateTimeFormat('en-CA', {timeZone: TPE, year:'numeric', month:'2-digit', day:'2-digit'}).format(new Date());
const tpeHour = () => String(Number(new Intl.DateTimeFormat('en-GB', {timeZone: TPE, hour:'2-digit', hour12:false}).format(new Date())) % 24).padStart(2, '0') + ':00';

// The five layers, in the order the owner reads them.
const LAYERS = ['identification', 'now', 'subject', 'terrain', 'actions'];

let server, baseURL, chrome, ws, send, evaljs, ready;
const pendingCalls = new Map();
let nextId = 0;
const sleep = ms => new Promise(r => setTimeout(r, ms));

function sidecarBody() {
  const today = tpeDate(), hour = tpeHour();
  const places = {};
  for (const id of FIXTURE_IDS) {
    places[id] = {local_date: today, hour, wmo: 3, temp_c: 21.5, vis_km: CAP_VIS_KM, is_today: true};
  }
  return JSON.stringify({artifact_version:'now-sidecar@1', generated_at:new Date().toISOString(),
    source_bundle:'evaluations-latest.json', hours:168, places});
}

// Lazy boot (never a root test.before — see CL-UI-90).
async function boot() {
  if (ready) return ready;
  ready = (async () => {
    server = createServer((req, res) => {
      res.on('error', () => {});
      const raw = req.url.split('?')[0];
      if (raw === '/apps/web-v2/now-latest.json') {
        const body = sidecarBody();
        res.writeHead(200, {...NO_STORE, 'content-type':'application/json', 'content-length':Buffer.byteLength(body)});
        res.end(body); return;
      }
      const p = raw.replace(/\/+$/, '') || '/';
      const file = join(APP, p === '/' ? 'index.html' : decodeURIComponent(p.slice(1)));
      try {
        const body = readFileSync(file);
        res.writeHead(200, {...NO_STORE, 'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
        res.end(body);
      } catch { res.writeHead(404); res.end('not found'); }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    baseURL = `http://127.0.0.1:${server.address().port}/`;

    chrome = spawn(BROWSER, [
      '--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
      '--enable-unsafe-swiftshader','--use-angle=swiftshader',
      '--no-first-run','--remote-debugging-port=0','--window-size=1440,900',
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui118-')), 'about:blank',
    ], {stdio:['ignore','ignore','pipe']});
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = '';
      const t = setTimeout(() => reject(new Error('no devtools endpoint')), 60000);
      chrome.stderr.on('data', d => {
        buf += d;
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearTimeout(t); resolve(m[1]); }
      });
      chrome.on('error', e => reject(new Error('spawn: ' + e.message)));
    });
    const dbgHost = wsUrl.match(/ws:\/\/([^/]+)/)[1];
    let targets = [];
    for (let i = 0; i < 40; ++i) {
      targets = await (await fetch(`http://${dbgHost}/json/list`)).json();
      if (targets.some(t => t.type === 'page')) break;
      await sleep(250);
    }
    ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
    await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
    ws.onmessage = e => {
      const m = JSON.parse(e.data);
      if (m.id && pendingCalls.has(m.id)) { pendingCalls.get(m.id)(m); pendingCalls.delete(m.id); }
    };
    send = (method, params = {}) => new Promise((resolve, reject) => {
      const i = ++nextId;
      pendingCalls.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
      ws.send(JSON.stringify({id:i, method, params}));
    });
    evaljs = async expr => {
      const r = await send('Runtime.evaluate', {expression:expr, returnByValue:true, awaitPromise:true});
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
      return r.result?.value;
    };
    await send('Page.enable');
    return true;
  })().catch(e => { ready = null; throw e; });
  return ready;
}

// Load the page at a given viewport and wait until ≥3 cards are rendered with
// their now rows painted (the sidecar settles asynchronously).
async function load(width, height) {
  await boot();
  await send('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor:1, mobile:width < 700});
  await send('Page.navigate', {url: baseURL + 'index.html'});
  const deadline = Date.now() + 60000;
  let cards = 0;
  while (Date.now() < deadline) {
    await sleep(500);
    cards = await evaljs(`document.querySelectorAll('#spots-container .card [data-layer="now"]').length`).catch(() => 0);
    if (cards >= 3) break;
  }
  assert.ok(cards >= 3, `expected at least three layered cards, got ${cards}`);
  // Let the post-settle repaint land (the sidecar paints twice by design).
  await sleep(1500);
  return cards;
}

// ---------------------------------------------------------------- 1. the order
browserTest('CL-UI-118 A (1): card DOM order is identification → now → subject → terrain → actions', {timeout:240000}, async () => {
  await load(1440, 900);
  const shape = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const bad = [];
    let checked = 0;
    for (const c of cards) {
      const layers = [...c.querySelectorAll('[data-layer]')].map(e => e.getAttribute('data-layer'));
      if (layers.length) checked++;
      if (JSON.stringify(layers) !== JSON.stringify(${JSON.stringify(LAYERS)})) bad.push({id:c.getAttribute('data-place-id'), layers});
    }
    return {cards: cards.length, checked, bad, exact: ${JSON.stringify(LAYERS)}};
  })()`);
  assert.ok(shape.checked > 0, 'cards carry data-layer markers');
  assert.equal(shape.checked, shape.cards, 'EVERY card carries the four layers + action row (no legacy format left)');
  assert.deepEqual(shape.bad, [], `cards must be ${JSON.stringify(LAYERS)} in that order`);
  // The now row is its own layer ABOVE the subject block — not folded into it.
  const nesting = await evaljs(`(() => {
    const c = document.querySelector('#spots-container .card');
    const now = c.querySelector('[data-layer="now"]');
    const subj = c.querySelector('[data-layer="subject"]');
    return {ownLayer: !subj.contains(now), nowFirst: !!(now.compareDocumentPosition(subj) & Node.DOCUMENT_POSITION_FOLLOWING)};
  })()`);
  assert.equal(nesting.ownLayer, true, 'the now row is not a descendant of the subject block');
  assert.equal(nesting.nowFirst, true, 'the now row precedes the subject block in document order');
  // CL-UI-118 A-fix: the access-note strip is the card's LAST block — after the
  // action row and outside .card-layers, so it cannot push a layer top around.
  const strip = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const out = [];
    for (const c of cards) {
      const s = c.querySelector('.card-access-note');
      const layers = c.querySelector('.card-layers');
      const actions = c.querySelector('[data-layer="actions"]');
      out.push({id: c.getAttribute('data-place-id'), hasStrip: !!s,
        outsideGrid: !!(s && layers && !layers.contains(s)),
        afterActions: !!(s && actions && (actions.compareDocumentPosition(s) & Node.DOCUMENT_POSITION_FOLLOWING)),
        lastChild: !!(s && c.lastElementChild === s)});
    }
    return out;
  })()`);
  assert.ok(strip.length > 0, 'cards measured for the note strip');
  for (const s of strip) {
    assert.equal(s.hasStrip, true, `${s.id}: every card carries the note strip block`);
    assert.equal(s.outsideGrid, true, `${s.id}: the strip is outside .card-layers (the aligned grid)`);
    assert.equal(s.afterActions, true, `${s.id}: the strip follows the action row`);
    assert.equal(s.lastChild, true, `${s.id}: the strip is the card's last block`);
  }
});

// ------------------------------------------------------------- 2. one bell only
browserTest('CL-UI-118 A (2): exactly ONE bell per card, and it still lists every subject reminder option', {timeout:240000}, async () => {
  await load(1440, 900);
  const bells = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    return cards.map(c => {
      const triggers = c.querySelectorAll('[data-rem-menu-trigger]');
      const menus = c.querySelectorAll('[data-rem-menu]');
      const rowBells = c.querySelectorAll('.cl-subject-row .cl-rem-btn, .cl-subject-rows .cl-rem-btn');
      const opts = [...c.querySelectorAll('[data-rem-menu] .cl-rem-btn')].map(b => ({
        place: b.getAttribute('data-rem-place'),
        compact: b.getAttribute('data-rem-compact'),
        label: (b.parentElement.querySelector('.cl-bell-opt-name') || {}).textContent || '',
      }));
      const subjects = [...c.querySelectorAll('.cl-subject-row .cl-subject-name')].map(n => n.textContent);
      return {id:c.getAttribute('data-place-id'), triggers:triggers.length, menus:menus.length,
              rowBells:rowBells.length, opts, subjects,
              open:hidden(c.querySelector('[data-rem-menu]'))};
    });
    function hidden(m) { return m ? m.hidden : null; }
  })()`);
  assert.ok(bells.length >= 3, `cards rendered (${bells.length})`);
  for (const c of bells) {
    assert.equal(c.triggers, 1, `${c.id}: exactly one spot-level bell`);
    assert.equal(c.menus, 1, `${c.id}: the bell owns one menu`);
    assert.equal(c.rowBells, 0, `${c.id}: no subject row repeats a bell`);
    assert.equal(c.open, true, `${c.id}: the menu starts closed`);
    assert.ok(c.opts.length >= 1, `${c.id}: the bell menu is never empty`);
    for (const o of c.opts) {
      assert.equal(o.place, c.id, `${c.id}: every option targets this place`);
      assert.equal(o.compact, '1', `${c.id}: options are the compact 🔔 mounts the client owns`);
    }
    // Every subject that has a row is offered, by name, in the one bell's menu.
    for (const name of c.subjects) {
      assert.ok(c.opts.some(o => o.label === name),
        `${c.id}: the menu offers 「${name}」 (has ${JSON.stringify(c.opts.map(o => o.label))})`);
    }
  }
  // A real click opens it (aria + painted box), and the menu is the compact list.
  const clicked = await evaljs(`(() => {
    const card = document.querySelector('#spots-container .card');
    card.scrollIntoView({block:'center'});
    const btn = card.querySelector('[data-rem-menu-trigger]');
    const r = btn.getBoundingClientRect();
    return {x: r.left + r.width / 2, y: r.top + r.height / 2, hit: (document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2) || {}).nodeName};
  })()`);
  await send('Input.dispatchMouseEvent', {type:'mousePressed', x:clicked.x, y:clicked.y, button:'left', clickCount:1});
  await send('Input.dispatchMouseEvent', {type:'mouseReleased', x:clicked.x, y:clicked.y, button:'left', clickCount:1});
  await sleep(150);
  const opened = await evaljs(`(() => {
    const card = document.querySelector('#spots-container .card');
    const btn = card.querySelector('[data-rem-menu-trigger]');
    const menu = card.querySelector('[data-rem-menu]');
    const r = menu.getBoundingClientRect();
    return {expanded: btn.getAttribute('aria-expanded'), hidden: menu.hidden, w: Math.round(r.width), h: Math.round(r.height),
            options: menu.querySelectorAll('.cl-rem-btn').length,
            placeOnTop: !!(document.elementFromPoint(r.left + 8, r.top + r.height / 2) || {}).closest};
  })()`);
  assert.equal(opened.expanded, 'true', 'a real click expands the bell');
  assert.equal(opened.hidden, false, 'and paints the menu');
  assert.ok(opened.w > 0 && opened.h > 0, `the menu occupies a real box (${opened.w}×${opened.h})`);
  assert.ok(opened.options >= 1, 'the open menu lists its reminder mounts');
});

browserTest('CL-UI-118 A (2a): every evaluated card really offers the opportunity-scoped reminder', {timeout:240000}, async () => {
  await load(1440, 900);
  const cards = await evaljs(`(() => [...document.querySelectorAll('#spots-container .card')].map(c => ({
    id: c.getAttribute('data-place-id'),
    badge: (c.querySelector('.card-header-actions .tier') || {}).className || '',
    mounts: [...c.querySelectorAll('[data-rem-menu] [data-rem-place]')].map(b => ({
      place: b.getAttribute('data-rem-place'), cc: b.getAttribute('data-rem-cc'),
      opp: b.getAttribute('data-rem-opp'), label: (b.parentElement.querySelector('.cl-bell-opt-name') || {}).textContent || ''})),
  })))()`);
  const evaluated = cards.filter(c => /tier-(rec|shoot|no)\b/.test(c.badge));
  assert.ok(evaluated.length >= 10, `evaluated cards rendered (${evaluated.length})`);
  const missing = evaluated.filter(c => !c.mounts.some(m => m.opp)).map(c => c.id);
  assert.deepEqual(missing, [], 'every card with a best opportunity mounts data-rem-opp in its bell menu');
  // …and the opportunity option is labelled, never a bare bell.
  const labelled = evaluated.filter(c => c.mounts.filter(m => m.opp).every(m => !m.label)).map(c => c.id);
  assert.deepEqual(labelled, [], 'the opportunity option carries a readable label');
});

// ------------------------------------------- 2b. reminder-mount parity (node)
// CL-UI-118 A-fix (reviewer condition 2): the ONE bell's menu must mount every
// payload the retired per-subject bells carried at base bfa313cea — EXECUTED,
// not pinned as a source regex (that is exactly what CL-UI-91 (5) regressed
// into). The pre-consolidation card mounted:
//   · one bell per curated subject row      → data-rem-place [+ data-rem-cc]
//   · the tier row (no-window / scPassedNote) → data-rem-place + data-rem-opp
//   · the no-subject summary bell            → data-rem-place + data-rem-opp
// so the menu is asserted a SUPERSET of that set for every context, including
// the scPassedNote branch where the ONLY opportunity mount used to be the (now
// bell-less) tier row.
const sliceSrc = (start, end) => {
  const i = APPJS.indexOf(start);
  assert.ok(i >= 0, `source marker not found: ${start}`);
  const j = APPJS.indexOf(end, i + start.length);
  assert.ok(j > i, `source end marker not found after ${start}: ${end}`);
  return APPJS.slice(i, j);
};
const ROW_SRC = sliceSrc('function clSubjectRowLine', '// CL-E2E-131 (2) (owner');
const BELL_SRC = sliceSrc('const clBellHtml=(()=>{', '})();') + '})();';
const DICT = {clui118_bell_menu:'提醒設定', clui118_bell_all:'整個景點', clui118_bell_opp:'最佳時段'};
const makeMenu = new Function('DICT', 'spot', 'scEntries', 'v2Best',
  `const d=()=>DICT;const esc=s=>String(s);${BELL_SRC};return clBellHtml;`);
const baseRows = new Function(`
  const esc=s=>String(s);
  const colonSep=()=>'：';
  const formatHourSegments=a=>(a||[]).join('–');
  const clIconSvg=()=>'';
  ${ROW_SRC}
  return {clSubjectRowLine, clTierRowLine};`)();
const mountsOf = html => [...String(html).matchAll(/<button\b[^>]*>/g)]
  .map(m => m[0]).filter(tag => /data-rem-place=/.test(tag))
  .map(tag => {
    const g = k => (new RegExp(`data-rem-${k}="([^"]*)"`).exec(tag) || ['', ''])[1];
    return {place:g('place'), cc:g('cc'), opp:g('opp')};
  });
const mountKey = m => `${m.place}|${m.cc}|${m.opp}`;

test('CL-UI-118 A (2b): the bell menu mounts every payload the retired per-subject bells carried', () => {
  const SPOT = {spot_id:'tw-074'};
  const CC = {subject:'夜景'};
  const E1 = {name:'夜景', window:['22:00','23:00'], cc:CC};
  const E2 = {name:'日出', window:['05:00','06:00']};
  const contexts = [
    {name:'curated rows + a best opportunity', entries:[E1, E2], best:{oppId:'tw-074-P01'},
     base:[baseRows.clSubjectRowLine(E1, 'tw-074', false), baseRows.clSubjectRowLine(E2, 'tw-074', false)]},
    {name:'scPassedNote (the tier row replaced the subject rows)', entries:[E1], best:{oppId:'tw-074-P01'},
     base:[baseRows.clTierRowLine('○ 可拍 · 窗已過', '明天 04:00', 'tw-074', 'tw-074-P01')]},
    {name:'no subject row, evaluated', entries:[], best:{oppId:'tw-074-P01'},
     base:['<button type="button" class="cl-rem-btn" data-rem-place="tw-074" data-rem-opp="tw-074-P01">🔔</button>']},
    {name:'no subject row, not evaluated', entries:[], best:null, base:[]},
  ];
  for (const ctx of contexts) {
    const menu = mountsOf(makeMenu(DICT, SPOT, ctx.entries, ctx.best));
    assert.ok(menu.length >= 1, `${ctx.name}: the bell menu is never empty`);
    const have = new Set(menu.map(mountKey));
    for (const html of ctx.base) {
      for (const m of mountsOf(html)) {
        assert.ok(have.has(mountKey(m)),
          `${ctx.name}: the menu must mount ${mountKey(m)} — a retired per-subject bell carried it`);
      }
    }
    for (const m of menu) assert.equal(m.place, SPOT.spot_id, `${ctx.name}: every mount targets this place`);
  }
  // The latent gap the reviewer found: with scPassedNote the tier row is the ONE
  // opportunity carrier and it no longer has a bell — so an opportunity-scoped
  // reminder could not be created on those cards at all.
  const silentTierRow = baseRows.clTierRowLine('○ 可拍 · 窗已過', '明天 04:00', 'tw-074', 'tw-074-P01', {bell:false});
  assert.equal(mountsOf(silentTierRow).length, 0, 'the card tier row carries no bell any more');
  const passedMenu = mountsOf(makeMenu(DICT, SPOT, [E1], {oppId:'tw-074-P01'}));
  assert.ok(passedMenu.some(m => m.opp === 'tw-074-P01'),
    'so the ONE bell MUST carry the opportunity mount on a scPassedNote card (gap closed)');
  assert.ok(passedMenu.some(m => m.cc && !m.opp), 'and it still offers the curated subject choice');
  // The spot-wide fallback stays for a card with neither subject nor opportunity.
  const bare = mountsOf(makeMenu(DICT, SPOT, [], null));
  assert.deepEqual(bare, [{place:'tw-074', cc:'', opp:''}], 'a bare card keeps the spot-wide reminder');
});

// ---------------------------------------------------- 3. the cap wording on L2
browserTest('CL-UI-118 A (3): L2 reads 「≥ 24 km」 — 「資料上限」 lives in the tooltip only', {timeout:240000}, async () => {
  await load(1440, 900);
  const cap = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const rows = cards.map(c => c.querySelector('[data-layer="now"]')).filter(Boolean);
    const withNow = rows.filter(r => r.querySelector('.now-wx'));
    const withCap = rows.filter(r => r.querySelector('.now-wx .vis-cap'));
    const first = withCap[0];
    const span = first ? first.querySelector('.now-wx .vis-cap') : null;
    return {
      rows: rows.length, withNow: withNow.length, withCap: withCap.length,
      visible: span ? span.textContent : null,
      title: span ? span.getAttribute('title') : null,
      aria: span ? span.getAttribute('aria-label') : null,
      nowText: first ? first.textContent : '',
      rowHasCapWords: withNow.some(r => r.textContent.includes('資料上限')),
      cappedRowText: first ? first.textContent : '',
    };
  })()`);
  assert.ok(cap.rows > 0, 'the now layer rendered');
  assert.ok(cap.withNow >= 3, `cards with a painted now row (${cap.withNow})`);
  assert.equal(cap.withCap, cap.withNow, 'every now row reports the served cap visibility (sidecar vis 24.8 km)');
  assert.equal(cap.visible, '≥ 24 km', 'the visible value is the short form');
  assert.equal(cap.rowHasCapWords, false, '「資料上限」 never appears in the visible now row text');
  assert.doesNotMatch(cap.cappedRowText, /資料上限/, 'the rendered row carries no parenthetical');
  assert.match(String(cap.title), /資料上限/, 'the tooltip carries the words');
  assert.match(String(cap.aria), /≥ 24 km（資料上限）/, 'and so does the screen-reader label');
});

// ------------------------------------------------- 4. terrain is a separate line
browserTest('CL-UI-118 A (4): elevation + astronomy never share an element with the now row', {timeout:240000}, async () => {
  await load(1440, 900);
  const sep = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const out = [];
    for (const c of cards) {
      const now = c.querySelector('[data-layer="now"]');
      const terrain = c.querySelector('[data-layer="terrain"]');
      if (!now || !terrain) continue;
      const elev = [...terrain.querySelectorAll('.metric-chip')].find(x => / m$/.test((x.textContent || '').trim()));
      const astro = terrain.querySelector('.card-meta-astro');
      if (!elev) continue;
      out.push({
        id: c.getAttribute('data-place-id'),
        elevInNow: now.contains(elev),
        astroInNow: astro ? now.contains(astro) : false,
        // A common ancestor that IS the now row would mean one line again.
        sharedAncestorIsNow: (() => {
          let a = elev.parentElement;
          while (a && !a.contains(now)) a = a.parentElement;
          return !!(a && a.hasAttribute('data-layer') && a.getAttribute('data-layer') === 'now');
        })(),
        elevTop: Math.round(elev.getBoundingClientRect().top),
        nowTop: Math.round(now.getBoundingClientRect().top),
        terrainTop: Math.round(terrain.getBoundingClientRect().top),
        lineWhiteSpace: getComputedStyle(terrain.querySelector('.card-terrain-line')).whiteSpace,
        lineBox: (() => {
          const line = terrain.querySelector('.card-terrain-line');
          if (!line) return null;
          const lb = line.getBoundingClientRect();
          const outside = [...line.children].filter(k => {
            const r = k.getBoundingClientRect();
            return r.top < lb.top - 1 || r.bottom > lb.bottom + 1;
          }).length;
          return {h: Math.round(lb.height), outside, scrollH: line.scrollHeight, clientH: line.clientHeight};
        })(),
        layerH: Math.round(terrain.getBoundingClientRect().height),
      });
    }
    return out;
  })()`);
  assert.ok(sep.length >= 3, `cards with a terrain line (${sep.length})`);
  for (const c of sep) {
    assert.equal(c.elevInNow, false, `${c.id}: elevation is not inside the now layer`);
    assert.equal(c.astroInNow, false, `${c.id}: astronomy is not inside the now layer`);
    assert.equal(c.sharedAncestorIsNow, false, `${c.id}: no shared ancestor is the now row`);
    assert.ok(c.terrainTop > c.nowTop, `${c.id}: the terrain line sits below the now row`);
    assert.equal(c.lineWhiteSpace, 'nowrap', `${c.id}: the terrain line never wraps`);
    assert.ok(c.lineBox, `${c.id}: the terrain line exists`);
    assert.equal(c.lineBox.outside, 0, `${c.id}: every item stays inside the one 22px line (no second row)`);
    assert.ok(c.lineBox.h <= 23, `${c.id}: the line keeps its fixed 22px height (${c.lineBox.h})`);
    assert.ok(c.lineBox.scrollH <= c.lineBox.clientH + 1, `${c.id}: the line does not overflow vertically`);
  }
  // The layer geometry is pinned in CSS as a single internal grid (not margins).
  assert.match(CSS, /\.card-layers\s*\{[^}]*display:grid/);
  assert.match(CSS, /grid-template-rows:\s*\n?\s*var\(--cl-card-r-id\)\s*\n?\s*var\(--cl-card-r-now\)\s*\n?\s*minmax\(var\(--cl-card-r-subject\),1fr\)\s*\n?\s*minmax\(var\(--cl-card-r-terrain\),auto\)/,
    'the four rows are one grid: two fixed heights + the flexible subject band + the terrain row that can only grow for its own terrain line');
});

// ------------------------------------- 4b. the access note is fully readable
// CL-UI-118 A-fix (reviewer condition 1, second pass): at 393 px the note was
// folded into the nowrap terrain line and ellipsis-clipped (tw-074: 466 px of
// text inside a 192 px box); the first fix moved it onto its own line INSIDE the
// terrain layer, and that line's `minmax(…,auto)` growth pulled the whole layer
// upward (a 34 px terrain-top spread on every row holding a note). It is now a
// FOOTNOTE STRIP after the action row, outside the layer grid entirely, and it
// still wraps to its full length at both widths.
async function measureNotes() {
  return evaljs(`(() => {
    const out = [];
    // CL-UI-118 A-fix (reviewer condition 1): the strip assertion compares the
    // RENDERED strip against the RESOLVED --cl-card-r-note of the CURRENT
    // viewport band — not against the note's own height (min-height + auto-grow
    // made \`stripH >= note.h\` unfalsifiable: it measured 123.22 >= 123.22).
    const reserve = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--cl-card-r-note')) || 0;
    for (const c of document.querySelectorAll('#spots-container .card')) {
      const note = c.querySelector('.access-note');
      if (!note) continue;
      const strip = c.querySelector('.card-access-note');
      const actions = c.querySelector('[data-layer="actions"]');
      const terrain = c.querySelector('[data-layer="terrain"]');
      const line = terrain && terrain.querySelector('.card-terrain-line');
      const r = note.getBoundingClientRect();
      const cs = getComputedStyle(note);
      out.push({
        id: c.getAttribute('data-place-id'),
        chars: (note.textContent || '').trim().length,
        w: Math.round(r.width), h: Math.round(r.height),
        scrollW: note.scrollWidth, clientW: note.clientWidth,
        scrollH: note.scrollHeight, clientH: note.clientHeight,
        whiteSpace: cs.whiteSpace, overflowWrap: cs.overflowWrap, textOverflow: cs.textOverflow,
        lineClamp: cs.webkitLineClamp, lh: parseFloat(cs.lineHeight) || 0,
        // Outside EVERY aligned layer — the strip is a sibling of .card-layers.
        inAnyLayer: [...c.querySelectorAll('[data-layer]')].some(el => el.contains(note)),
        insideLayerGrid: !!(c.querySelector('.card-layers') || {contains: () => false}).contains(note),
        afterActions: actions ? r.top >= actions.getBoundingClientRect().bottom - 1 : null,
        stripH: strip ? Math.round(strip.getBoundingClientRect().height) : null,
        stripMinH: strip ? parseFloat(getComputedStyle(strip).minHeight) || 0 : null,
        cardW: Math.round(c.getBoundingClientRect().width),
        reserve,
        lineH: line ? Math.round(line.getBoundingClientRect().height) : null,
        lineScrollH: line ? line.scrollHeight : null, lineClientH: line ? line.clientHeight : null,
      });
    }
    return out;
  })()`);
}
function assertNotesReadable(notes, where) {
  assert.ok(notes.length >= 1, `${where}: at least one card carries an access note (${notes.length})`);
  for (const n of notes) {
    assert.equal(n.inAnyLayer, false, `${where} ${n.id}: the note lives outside every aligned layer (identification/now/subject/terrain/actions)`);
    assert.equal(n.insideLayerGrid, false, `${where} ${n.id}: and outside the layer grid itself — it cannot move a layer top`);
    assert.equal(n.afterActions, true, `${where} ${n.id}: the note sits after the action row it follows in the DOM`);
    assert.equal(n.whiteSpace, 'normal', `${where} ${n.id}: the note wraps (white-space ${n.whiteSpace})`);
    assert.equal(n.textOverflow, 'clip', `${where} ${n.id}: the note is never ellipsised (${n.textOverflow})`);
    assert.equal(n.lineClamp, 'none', `${where} ${n.id}: the note is never line-clamped (${n.lineClamp})`);
    assert.ok(n.scrollW <= n.clientW + 1,
      `${where} ${n.id}: the full ${n.chars}-char note fits its ${n.clientW}px box (needs ${n.scrollW}px)`);
    assert.ok(n.scrollH <= n.clientH + 1 || n.scrollW <= n.clientW + 1, `${where} ${n.id}: no vertical clipping`);
    assert.ok(n.h >= 20, `${where} ${n.id}: the note keeps a readable line box (${n.h}px)`);
    // CL-UI-118 A-fix (reviewer condition 1): where a strip is reserved, the
    // rendered strip must BE the resolved --cl-card-r-note of this viewport band
    // (within 1 px) — not the note's own height. The old `stripH >= n.h` was
    // vacuous: min-height + auto-grow made it compare 123.22 against 123.22, so a
    // note long enough to grow its strip (and pull that card's terrain/actions up
    // out of the row) always passed. Comparing upwards against the token makes
    // exactly that failure fatal.
    if (n.reserve > 0) {
      assert.equal(n.stripMinH, n.reserve,
        `${where} ${n.id}: the strip's min-height is the resolved --cl-card-r-note (${n.stripMinH} vs ${n.reserve})`);
      assert.ok(n.stripH <= n.reserve + 1,
        `${where} ${n.id}: the note strip never outgrows its ${n.reserve}px reserve (strip ${n.stripH}px, note ${n.h}px) — an overlong note must bump the token, not the layout`);
      assert.ok(n.stripH >= n.reserve - 1,
        `${where} ${n.id}: the ${n.reserve}px reserve is actually applied (strip ${n.stripH}px)`);
      assert.ok(n.h <= n.reserve + 1,
        `${where} ${n.id}: the ${n.h}px note fits the ${n.reserve}px reserve`);
      assert.ok(n.reserve - n.h >= 6,
        `${where} ${n.id}: ≥6px headroom in the band (note ${n.h}px, reserve ${n.reserve}px)`);
    } else {
      // Single column (≤768 px): no reserve is claimed, so the strip is exactly
      // the note's own painted box — it must neither clip nor pad the note.
      assert.ok(n.stripH <= n.h + 1,
        `${where} ${n.id}: with no reserve the strip is the note's own ${n.h}px box (strip ${n.stripH}px)`);
      assert.ok(n.stripH >= n.h - 1,
        `${where} ${n.id}: the single-column strip is not shorter than its note (${n.stripH} vs ${n.h})`);
    }
  }
  // The terrain line itself is still the fixed, single-line elevation + astronomy row.
  for (const n of notes) {
    assert.equal(n.lineH <= 23, true, `${where} ${n.id}: the terrain line keeps its fixed 22px height (${n.lineH})`);
    assert.ok(n.lineScrollH <= n.lineClientH + 1, `${where} ${n.id}: the terrain line does not overflow`);
  }
}
browserTest('CL-UI-118 A (4b): the access note is fully readable at 393 px and at 1440 px', {timeout:240000}, async () => {
  await load(393, 852);
  const phone = await measureNotes();
  assertNotesReadable(phone, '393×852');
  // The original defect: this text was ellipsis-clipped inside a 192 px box on a
  // 393 px phone. Now the longest note must WRAP (≥2 painted lines) and still fit
  // its box — the two measured facts the fix is accountable for.
  const longest = phone.slice().sort((a, b) => b.chars - a.chars)[0];
  assert.ok(longest.clientW < 340, `393×852: a phone-width note box (${longest.clientW}px)`);
  assert.ok(longest.lh > 0 && longest.h >= longest.lh * 1.5,
    `393×852: the longest ${longest.chars}-char note paints on ${Math.round(longest.h / longest.lh)} lines instead of being clipped`);
  assert.ok(longest.scrollW <= longest.clientW + 1,
    `393×852: and it still fits its ${longest.clientW}px box (needs ${longest.scrollW}px)`);
  console.log('CL-UI-118 access notes @393: ' + JSON.stringify(phone.map(n => ({id:n.id, chars:n.chars, box:n.clientW, needs:n.scrollW, h:n.h}))));
  await load(1440, 900);
  const desk = await measureNotes();
  assertNotesReadable(desk, '1440×900');
  console.log('CL-UI-118 access notes @1440: ' + JSON.stringify(desk.map(n => ({id:n.id, chars:n.chars, box:n.clientW, needs:n.scrollW, h:n.h}))));
});

// --------------------------------------------------------- 5. cross-card alignment
// CL-UI-118 A-fix (reviewer condition 1, second pass): the sampled row MUST be a
// row that actually carries an access note — that is where the regression lived,
// and the old test sampled the first row of the list, which has none, so it
// passed on a clean row while note rows were 34 px out. A list with no note at
// all now fails loudly instead of silently sampling a clean row.
browserTest('CL-UI-118 A (5): a row that CARRIES an access note aligns every layer within 1 px (1440×900)', {timeout:240000}, async () => {
  await load(1440, 900);
  const geo = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const rows = cards.map(c => {
      const t = {};
      for (const el of c.querySelectorAll('[data-layer]')) {
        const r = el.getBoundingClientRect();
        t[el.getAttribute('data-layer')] = {top: Math.round(r.top * 100) / 100, h: Math.round(r.height)};
      }
      const strip = c.querySelector('.card-access-note');
      return {id: c.getAttribute('data-place-id'), top: Math.round(c.getBoundingClientRect().top), layers: t,
              subjRows: c.querySelectorAll('.cl-subject-row').length,
              subjText: ((c.querySelector('[data-layer="subject"]') || {}).textContent || '').replace(/\\s+/g, ' ').trim(),
              subjH: t.subject ? t.subject.h : 0,
              note: (() => { const n = c.querySelector('.access-note'); return n ? (n.textContent || '').trim().length : 0; })(),
              stripH: strip ? Math.round(strip.getBoundingClientRect().height) : null};
    });
    return {rows, width: document.documentElement.clientWidth};
  })()`);
  // Group cards by their own top edge = one visual grid row.
  const groups = new Map();
  for (const r of geo.rows) {
    if (!groups.has(r.top)) groups.set(r.top, []);
    groups.get(r.top).push(r);
  }
  const allRows = [...groups.values()];
  assert.ok(geo.width >= 1000, `desktop grid expected, got ${geo.width}px`);
  const ids = g => g.map(c => c.id).join(', ');
  const spreadOf = g => {
    const out = {};
    for (const layer of LAYERS) {
      const tops = g.map(c => c.layers[layer] && c.layers[layer].top).filter(v => typeof v === 'number');
      assert.equal(tops.length, g.length, `${layer}: every card in the row carries the layer [${ids(g)}]`);
      out[layer] = Math.round((Math.max(...tops) - Math.min(...tops)) * 100) / 100;
    }
    return out;
  };
  // CL-UI-118 A-fix (reviewer condition 2): EVERY note-bearing row is swept, not
  // just the first one. A long note in an unsampled row misaligned terrain +
  // actions by 77 px and nothing caught it — the old test sampled one note row
  // and a clean row. Offenders are collected with their place ids so a failure
  // names the row that broke, not just "some row".
  const noteRows = allRows.filter(g => g.some(c => c.note > 0));
  const noteCardIds = geo.rows.filter(c => c.note > 0).map(c => c.id);
  assert.ok(noteRows.length >= 1,
    `the artifact must contain grid rows with an access-note card — the alignment regression only shows up there ` +
    `(rows with notes: ${noteRows.length}; note cards: ${noteCardIds.join(',') || 'none'})`);
  assert.ok(noteRows.some(g => g.length >= 3),
    `at least one note-bearing row is a FULL grid row (row sizes: ${JSON.stringify(noteRows.map(g => g.length))}; ids: ${noteRows.map(ids).join(' | ')})`);
  const offenders = [];
  for (const g of noteRows) {
    if (g.length < 2) continue; // a one-card row has no neighbour to misalign against
    const spread = spreadOf(g);
    for (const layer of LAYERS) {
      if (spread[layer] > 1) offenders.push(`${layer} spread ${spread[layer]}px in the note row holding [${ids(g)}]`);
    }
    // …and the MECHANISM that keeps that row aligned: one shared subject band and
    // one shared strip height across the row.
    const bands = new Set(g.map(c => c.subjH));
    if (bands.size !== 1) offenders.push(`subject band ${JSON.stringify([...bands])} not shared in the note row holding [${ids(g)}]`);
    const strips = new Set(g.map(c => c.stripH));
    if (strips.size !== 1) offenders.push(`note strip ${JSON.stringify([...strips])} not shared in the note row holding [${ids(g)}]`);
  }
  assert.deepEqual(offenders, [],
    `every note-bearing grid row must keep the 1px layer contract; offenders: ${offenders.join(' | ')}`);
  console.log('CL-UI-118 alignment sweep @1440×900: ' + noteRows.length + ' note row(s) '
    + JSON.stringify(noteRows.map(g => ({ids: g.map(c => c.id), rows: g.map(c => c.subjRows), spread: g.length > 1 ? spreadOf(g) : null}))));
  // The primary (fullest) note row carries the non-vacuity claims below.
  const row = noteRows.filter(g => g.length >= 3).sort((a, b) => b.length - a.length)[0];
  const spread = spreadOf(row);
  for (const layer of LAYERS) {
    assert.ok(spread[layer] <= 1,
      `${layer}: top edges must agree within 1 px across a NOTE row (spread ${spread[layer]} px; ${JSON.stringify(row.map(c => c.layers[layer] && c.layers[layer].top))})`);
  }
  // The row must be non-vacuous: the cards show DIFFERENT subject content, and
  // their bands are nevertheless ONE shared height (the alignment claim). Both
  // halves are required — either alone is the tautology this ticket replaced.
  const content = new Set(row.map(c => c.subjText));
  const heights = new Set(row.map(c => c.subjH));
  // The note strip is the same height on every card of the row — that is the
  // mechanism that keeps the layers aligned, so it is asserted, not assumed.
  const strips = new Set(row.map(c => c.stripH));
  console.log('CL-UI-118 alignment @1440×900 NOTE row: cards=' + row.length
    + ' notes=' + JSON.stringify(row.map(c => c.note))
    + ' subjectRows=' + JSON.stringify(row.map(c => c.subjRows))
    + ' subjectBand=' + JSON.stringify(row.map(c => c.subjH))
    + ' strips=' + JSON.stringify(row.map(c => c.stripH))
    + ' spread=' + JSON.stringify(spread));
  assert.ok(row.length >= 3, 'three or more cards measured');
  assert.ok(content.size > 1, `the measured row shows different subject content per card (${content.size} distinct)`);
  assert.equal(heights.size, 1,
    `the subject band is ONE shared height across the row (got ${JSON.stringify([...heights])})`);
  assert.equal(strips.size, 1,
    `the note strip is ONE shared height across the row (got ${JSON.stringify([...strips])})`);
  // Differing row COUNTS must exist somewhere in the list — otherwise the shared
  // band would only be an artefact of identical cards.
  const mixed = allRows.filter(g => new Set(g.map(c => c.subjRows)).size > 1);
  assert.ok(mixed.length >= 1,
    `the list mixes different subject-row counts within one grid row (counts: ${JSON.stringify(allRows.map(g => g.map(c => c.subjRows)))})`);
  // …and a clean row (no note anywhere in it) still aligns, and so does a row
  // that mixes 1/2/1 subject rows: the note strip must not have bought the note
  // row's alignment with a different row's.
  const cleanRow = allRows.filter(g => g.length >= 3 && g.every(c => c.note === 0))[0];
  assert.ok(cleanRow, 'a note-free grid row exists to compare against');
  const cleanSpread = spreadOf(cleanRow);
  for (const layer of LAYERS) {
    assert.ok(cleanSpread[layer] <= 1, `${layer}: a CLEAN row keeps the 1 px contract (spread ${cleanSpread[layer]} px)`);
  }
  // Prefer the 1/2/1 shape by name; fall back to any full row with two distinct
  // counts only if the bundle carries no such row (and say so in the log).
  const is121 = g => g.some(c => c.subjRows === 1) && g.some(c => c.subjRows === 2);
  const mixedRow = mixed.filter(g => g.length >= 3 && is121(g))[0] || mixed.filter(g => g.length >= 3)[0];
  assert.ok(mixedRow, `a full grid row mixing subject-row counts exists (counts: ${JSON.stringify(allRows.map(g => g.map(c => c.subjRows)))})`);
  const mixedSpread = spreadOf(mixedRow);
  for (const layer of LAYERS) {
    assert.ok(mixedSpread[layer] <= 1, `${layer}: a row MIXING subject-row counts keeps the 1 px contract (spread ${mixedSpread[layer]} px)`);
  }
  console.log('CL-UI-118 alignment @1440×900 CLEAN row: subjectRows=' + JSON.stringify(cleanRow.map(c => c.subjRows)) + ' spread=' + JSON.stringify(cleanSpread));
  console.log('CL-UI-118 alignment @1440×900 MIXED row: subjectRows=' + JSON.stringify(mixedRow.map(c => c.subjRows)) + ' spread=' + JSON.stringify(mixedSpread));
  console.log('CL-UI-118 mixed rows: ' + JSON.stringify(mixed.slice(0, 3).map(g => g.map(c => c.subjRows))));
  // The placeholder band is asserted on a SYNTHESISED card model below (5c):
  // today's bundle happens to have 0 cards without subject rows, so finding one
  // in the artifact is not guaranteed and a conditional skip would be a hole.
});

// ---------------------------------------------- 6. the reserve vs the band edges
// CL-UI-118 A-fix (reviewer condition 3): the reserve must be sized from the
// longest note the band actually paints, with real headroom AT the boundary
// widths — the old 46px base left 1.6 px at a 1280 shell while the comment
// claimed 66 px for that same width, and the 66 px band claimed to cover 1024
// where the card is only 307 px wide.
const RESERVE_PROBES = [
  {w: 1440, band: '≥1280'},
  {w: 1280, band: '≥1280 (first px of the band)'},
  {w: 1279, band: '769–1279 (last px of the band)'},
  {w: 1024, band: '769–1279'},
  {w: 770,  band: '769–1279 (narrowest multi-column card)'},
  {w: 769,  band: '769–1279 (last px of the band)'},
  {w: 768,  band: '≤768 (single column)'},
];
browserTest('CL-UI-118 A (6): the note reserve covers the longest note with ≥6 px headroom at every band edge', {timeout:300000}, async () => {
  const measured = [];
  for (const {w, band} of RESERVE_PROBES) {
    await load(w, 900);
    const m = await evaljs(`(() => {
      const reserve = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--cl-card-r-note')) || 0;
      const notes = [];
      for (const c of document.querySelectorAll('#spots-container .card')) {
        const n = c.querySelector('.access-note'); if (!n) continue;
        const s = c.querySelector('.card-access-note');
        notes.push({id:c.dataset.placeId, chars:(n.textContent||'').trim().length,
          h: Math.round(n.getBoundingClientRect().height*100)/100,
          stripH: Math.round(s.getBoundingClientRect().height*100)/100,
          cardW: Math.round(c.getBoundingClientRect().width)});
      }
      return {reserve, cw: document.documentElement.clientWidth, notes};
    })()`);
    assert.ok(m.notes.length >= 1, `${band} @${w}: the bundle still paints its access note (${m.notes.length})`);
    const longest = m.notes.slice().sort((a, b) => b.h - a.h)[0];
    measured.push({w, band, reserve: m.reserve, longest: longest.h, chars: longest.chars, cardW: longest.cardW});
    if (m.reserve > 0) {
      assert.ok(m.reserve - longest.h >= 6,
        `${band} @${w}: reserve ${m.reserve}px must clear the longest ${longest.chars}-char note (${longest.h}px on a ${longest.cardW}px card) by ≥6px — got ${Math.round((m.reserve - longest.h) * 100) / 100}px`);
      for (const n of m.notes) {
        assert.ok(n.stripH <= m.reserve + 1,
          `${band} @${w} ${n.id}: the strip stays at its ${m.reserve}px reserve (got ${n.stripH}px for a ${n.h}px note)`);
      }
    } else {
      // ≤768 px: one column, no reserve — the strip is the note's own box.
      for (const n of m.notes) {
        assert.ok(n.stripH <= n.h + 1,
          `${band} @${w} ${n.id}: single-column strip is the note's own box (strip ${n.stripH}px, note ${n.h}px)`);
      }
    }
  }
  console.log('CL-UI-118 reserve bands: ' + JSON.stringify(measured));
  // A LARGER reserve is not automatically better: the token must track the note
  // it protects, so a band may not over-reserve by more than one line either.
  for (const m of measured.filter(x => x.reserve > 0)) {
    assert.ok(m.reserve - m.longest <= 30,
      `${m.band} @${m.w}: the reserve tracks the measured note (${m.longest}px) instead of reserving dead space (${m.reserve}px)`);
  }
});

test('CL-UI-118 A (6a): the reserve token, its media bands and the documented bands agree', () => {
  const bare = CSS.replace(/\/\*[\s\S]*?\*\//g, '');
  const decls = [...bare.matchAll(/--cl-card-r-note:\s*(\d+)px/g)].map(m => Number(m[1]));
  assert.deepEqual(decls, [52, 72, 0],
    `three declarations only — base (≥1280), 769–1279, ≤768 (got ${JSON.stringify(decls)})`);
  assert.match(bare, /@media \(min-width: 769px\) and \(max-width: 1279px\) \{\s*:root \{ --cl-card-r-note: 72px; \}/,
    'the narrow multi-column band is 769–1279 px and reserves 72px');
  assert.match(bare, /@media \(max-width: 768px\) \{\s*:root \{ --cl-card-r-note: 0px; \}/,
    'the single-column band starts at 768 px and reserves nothing');
  // The comment that documents the reserve names the SAME boundaries and values.
  assert.match(CSS, /769–1279 px[\s\S]{0,120}72px/, 'the comment documents 72px for 769–1279');
  assert.match(CSS, /≥1280 px[\s\S]{0,120}52px/, 'and 52px for ≥1280 (it used to claim 66px there)');
});

// ------------------------------- 5c. a synthesised 資料不足 card model (no data)
// Reviewer condition 3: the 資料不足 branch must be exercised for real. The
// artifact has ZERO cards without subject rows, so the test SYNTHESISES a card
// model through the page's own seams (CLForecastRenderers.registerSyntheticRows +
// createCard) — it never mutates data/v2. Three cards are built in ONE grid row:
// 1 subject row / 3 subject rows / 0 subject rows (an honest 資料不足 day), then
// measured: identical band geometry, differing row counts, and the empty card's
// band reserved AND reading 資料不足.
browserTest('CL-UI-118 A (5c): a synthesised 資料不足 card keeps its band and its row-based alignment', {timeout:240000}, async () => {
  await load(1440, 900);
  const built = await evaljs(`(() => {
    const R = window.CLForecastRenderers;
    if (!R || !R.createCard || !R.registerSyntheticRows) return {error:'renderer seams missing'};
    const today = R.localDate('Asia/Taipei', 0);
    const nowMin = R.nowMinutes('Asia/Taipei');
    const hh = (m) => String(m).padStart(2, '0') + ':00';
    // Qualifying hours must still be REMAINING today (a card advertises only
    // future hours), so they are derived from the run-time clock.
    const start = Math.min(23, Math.floor((nowMin || 0) / 60) + 1);
    const good = [hh(start), hh(Math.min(23, start + 1))];
    const subj = (n) => ({name:{'zh-TW':n,en:n,ja:n}, subject_short:{'zh-TW':n,en:n,ja:n}, window:good.slice()});
    const make = (id, names, state) => {
      const tree = {};
      if (state !== 'NOT_EVALUABLE') tree[today] = {tier:'recommend', suitable: names.map(subj)};
      R.registerSyntheticRows(id, tree, {}, [{local_date:today, state,
        good_hours: state === 'NOT_EVALUABLE' ? [] : good, hour_counts:{}}]);
      const spot = {spot_id:id, name:'fixture ' + id, timezone:'Asia/Taipei', scenes:[],
                    opportunities:[{opportunity_id:'cp:' + id}]};
      return R.createCard(spot, {opportunity_id:'cp:' + id, theme:'mountain_view'});
    };
    const host = document.createElement('div');
    host.id = 'clui118-synthetic-row';
    host.style.cssText = 'display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;width:1200px;margin:40px 0';
    document.body.appendChild(host);
    const cards = [
      make('cluifixture-one', ['夜景'], 'GUIDANCE_SATISFIED'),
      make('cluifixture-three', ['夜景', '日出', '雲海'], 'GUIDANCE_SATISFIED'),
      make('cluifixture-none', [], 'NOT_EVALUABLE'),
    ];
    // The card element itself is what createCard returns — append it.
    for (const c of cards) host.appendChild(c);
    const min = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--cl-card-r-subject')) || 0;
    const out = cards.map(c => {
      const band = c.querySelector('[data-layer="subject"]');
      const layers = {};
      for (const el of c.querySelectorAll('[data-layer]')) layers[el.getAttribute('data-layer')] = Math.round(el.getBoundingClientRect().top);
      return {rows:c.querySelectorAll('.cl-subject-row').length,
              bandH:Math.round(band.getBoundingClientRect().height),
              bandTop:Math.round(band.getBoundingClientRect().top),
              text:(band.textContent || '').replace(/\\s+/g, ' ').trim(),
              badge:(c.querySelector('.card-header-actions .tier') || {}).textContent || '',
              layers};
    });
    const cleanup = () => host.remove();
    window.__clui118SyntheticCleanup = cleanup;
    return {min, cards:out};
  })()`);
  assert.ok(!built.error, `the page's card seams are reachable (${built.error || ''})`);
  assert.ok(built.min > 0, 'the subject band has a fixed minimum height token');
  const [one, three, none] = built.cards;
  assert.equal(none.rows, 0, 'the synthesised card really has no subject row');
  assert.equal(one.rows, 1, 'the first fixture keeps its one subject row');
  assert.equal(three.rows, 3, 'the second fixture keeps its three subject rows');
  assert.match(none.text, /資料不足/, `the empty band reads the honest 資料不足 line (got 「${none.text}」)`);
  assert.match(none.badge, /資料不足/, 'and its tier badge says the same thing');
  assert.ok(none.bandH >= built.min, `its band is RESERVED, not collapsed (${none.bandH} ≥ ${built.min})`);
  // One row of the grid → every layer top edge agrees, despite 1 / 3 / 0 rows.
  for (const layer of LAYERS) {
    const tops = built.cards.map(c => c.layers[layer]);
    assert.ok(tops.every(t => t === tops[0]),
      `${layer}: the synthesised row aligns every layer (${JSON.stringify(tops)})`);
  }
  // …and the band height is shared even though the content differs by 1/3/0 rows.
  assert.equal(new Set(built.cards.map(c => c.bandH)).size, 1,
    `one shared band height across 1 / 3 / 0 subject rows (${JSON.stringify(built.cards.map(c => c.bandH))})`);
  console.log('CL-UI-118 synthetic 資料不足 row: ' + JSON.stringify(built.cards.map(c => ({rows:c.rows, band:c.bandH, text:c.text.slice(0, 24)}))));
  await evaljs('(() => { if (window.__clui118SyntheticCleanup) window.__clui118SyntheticCleanup(); return true; })()');
});

browserTest('CL-UI-118 A (5b): the same contract holds at 393×852 (single column)', {timeout:240000}, async () => {
  await load(393, 852);
  const shape = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const c = cards[0];
    const layers = [...c.querySelectorAll('[data-layer]')].map(e => e.getAttribute('data-layer'));
    const line = c.querySelector('.card-terrain-line');
    const now = c.querySelector('[data-layer="now"]');
    const strips = cards.map(x => { const s = x.querySelector('.card-access-note');
      return {id: x.getAttribute('data-place-id'), has: !!s, outside: !!(s && !x.querySelector('.card-layers').contains(s))}; });
    return {layers, nowrap: getComputedStyle(line).whiteSpace,
            terrainBelowNow: line.getBoundingClientRect().top > now.getBoundingClientRect().top,
            cardWidth: Math.round(c.getBoundingClientRect().width),
            viewport: document.documentElement.clientWidth,
            strips,
            overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth};
  })()`);
  assert.deepEqual(shape.layers, LAYERS, 'phone: the same four layers + action row');
  assert.equal(shape.nowrap, 'nowrap', 'phone: the terrain line still never wraps');
  assert.equal(shape.terrainBelowNow, true, 'phone: terrain sits below the now row');
  assert.ok(shape.overflowX <= 1, `phone: the fixed rows introduce no horizontal overflow (${shape.overflowX}px)`);
  // CL-UI-118 A-fix: the note strip is not a phone-only corner case — it is the
  // card's last block at 393 px too, and it is never clamped there.
  for (const s of shape.strips) {
    assert.equal(s.has, true, `phone ${s.id}: the note strip block exists`);
    assert.equal(s.outside, true, `phone ${s.id}: the strip stays outside the layer grid`);
  }
});

// ============================ L3 (sub-commit B): the headline subject line
// The headline subject + window line is the card's visual protagonist: one type
// step LARGER than the now row (16px vs the 12px now chip), a faint tint and a
// 3px LEFT bar in the card's own state colour (green ✓推薦 / amber ○可拍 /
// grey ✗不宜·no verdict). It must sit between the now row and the action row,
// change no copy/i18n key/verdict, and leave the band's shared height untouched.
// Switch the tier tab with a REAL click (synthetic dispatch cannot be trusted
// for the tier bar — CL-UI-47 pitfall) and let the list repaint.
async function switchTier(tier) {
  const pt = await evaljs(`(() => { const b = document.querySelector('#tier-tabs [data-tier="${tier}"]'); if (!b) return null; b.scrollIntoView({block:'center'}); const r = b.getBoundingClientRect(); return {x: r.left + r.width / 2, y: r.top + r.height / 2}; })()`);
  if (!pt) return false;
  await send('Input.dispatchMouseEvent', {type:'mousePressed', x:pt.x, y:pt.y, button:'left', clickCount:1});
  await send('Input.dispatchMouseEvent', {type:'mouseReleased', x:pt.x, y:pt.y, button:'left', clickCount:1});
  await sleep(1400);
  return true;
}
const MEASURE_HEADLINE = `(() => {
    const probe = (() => {
      const el = document.createElement('span');
      document.body.appendChild(el);
      return (v) => { el.style.color = ''; el.style.color = v; return getComputedStyle(el).color; };
    })();
    const bgProbe = (() => {
      const el = document.createElement('span');
      document.body.appendChild(el);
      return (v) => { el.style.backgroundColor = 'transparent'; el.style.backgroundColor = v; return getComputedStyle(el).backgroundColor; };
    })();
    const root = getComputedStyle(document.documentElement);
    const tok = k => root.getPropertyValue(k).trim();
    const colour = {ok:probe(tok('--cl-green')), chance:probe(tok('--cl-amber')), no:probe(tok('--cl-grey'))};
    const tint = {ok:bgProbe(tok('--cl-green-bg')), chance:bgProbe(tok('--cl-amber-bg')), no:bgProbe(tok('--cl-grey-bg'))};
    const out = [];
    for (const c of document.querySelectorAll('#spots-container .card, #spot-region-grid .card, .deferred-grid .card')) {
      const now = c.querySelector('[data-layer="now"] .metric-chip');
      const head = c.querySelector('[data-layer="subject"] [data-headline]');
      if (!now || !head) continue;
      const hs = getComputedStyle(head), ns = getComputedStyle(now);
      const band = c.querySelector('[data-layer="subject"]');
      out.push({
        id: c.getAttribute('data-place-id'),
        cardTop: Math.round(c.getBoundingClientRect().top),
        state: head.getAttribute('data-state'),
        headFont: parseFloat(hs.fontSize), nowFont: parseFloat(ns.fontSize),
        headH: Math.round(head.getBoundingClientRect().height),
        shadow: hs.boxShadow, bg: hs.backgroundColor, bgToken: tint[head.getAttribute('data-state')],
        stateColour: colour[head.getAttribute('data-state')],
        headClass: head.className,
        nowTop: Math.round(c.querySelector('[data-layer="now"]').getBoundingClientRect().top),
        headTop: Math.round(head.getBoundingClientRect().top),
        actionsTop: Math.round(c.querySelector('[data-layer="actions"]').getBoundingClientRect().top),
        bandTop: Math.round(band.getBoundingClientRect().top),
        bandH: Math.round(band.getBoundingClientRect().height),
        text: (head.textContent || '').replace(/\\s+/g, ' ').trim(),
      });
    }
    return out;
  })()`;

function assertHeadline(cards, where) {
  assert.ok(cards.length >= 3, `${where}: cards with a headline line (${cards.length})`);
  for (const c of cards) {
    assert.ok(c.headFont > c.nowFont,
      `${where} ${c.id}: the headline subject is strictly larger than the now row (${c.headFont}px vs ${c.nowFont}px)`);
    assert.ok(c.headFont - c.nowFont >= 2, `${where} ${c.id}: and the step is visible (${(c.headFont - c.nowFont).toFixed(1)}px)`);
    assert.ok(['ok', 'chance', 'no'].includes(c.state), `${where} ${c.id}: the headline carries a state (${c.state})`);
    // The left bar is an INSET shadow in the STATE token colour…
    assert.match(c.shadow, /3px 0px 0px( 0px)? inset$/, `${where} ${c.id}: a 3px inset left bar (${c.shadow})`);
    assert.ok(c.shadow.includes(c.stateColour),
      `${where} ${c.id}: the bar uses the ${c.state} token colour (${c.stateColour}; got ${c.shadow})`);
    // …and the tint is the matching state background token.
    assert.ok(c.bg && c.bg !== 'rgba(0, 0, 0, 0)', `${where} ${c.id}: the headline carries a faint tint (${c.bg})`);
    assert.equal(c.bg, c.bgToken, `${where} ${c.id}: the tint is the ${c.state} background token`);
    // It sits between the now row and the action row.
    assert.ok(c.headTop > c.nowTop, `${where} ${c.id}: the headline sits below the now row`);
    assert.ok(c.headTop < c.actionsTop, `${where} ${c.id}: and above the action row`);
    // The row keeps its own 26px line box — the styling cannot stretch the band.
    assert.ok(c.headH <= 27, `${where} ${c.id}: the headline keeps its 26px row height (${c.headH})`);
    // The class is the ONLY markup change: the row's own class list survives.
    assert.ok(c.headClass.split(/\s+/).includes('cl-subject-row') || c.headClass.split(/\s+/).includes('theme-winner'),
      `${where} ${c.id}: the headline keeps its original row class (${c.headClass})`);
  }
  // The band's TOP edge is still shared across a grid row — L3 moves no layer.
  // (Band HEIGHT is content-driven — a card carrying a long access note trades
  //  flexible-band space for its own extra terrain line — so the "the styling
  //  adds no height" claim is proven on the SAME card, class on vs class off,
  //  in case B (1b).)
  const rows = new Map();
  for (const c of cards) { if (!rows.has(c.cardTop)) rows.set(c.cardTop, []); rows.get(c.cardTop).push(c); }
  for (const [top, g] of rows) {
    if (g.length < 2) continue;
    assert.equal(new Set(g.map(c => c.bandTop)).size, 1, `${where} row ${top}: one band top (${JSON.stringify(g.map(c => c.bandTop))})`);
  }
}
browserTest('CL-UI-118 B (1): the headline subject line is larger than the now row, tinted and barred by state', {timeout:240000}, async () => {
  await load(1440, 900);
  const rec = await evaljs(MEASURE_HEADLINE);
  assertHeadline(rec, '1440/rec');
  const states = new Set(rec.map(c => c.state));
  // The other two states live on the 全部 tab — switch to it for real so the
  // amber ○可拍 and grey ✗不宜 bars are exercised against live cards, not just
  // pinned in CSS. (Tier keys are recommend / shootable / not_recommended / all;
  // 全部 re-groups the list into region grids, hence the broadened selector.)
  if (await switchTier('all')) {
    const set = await evaljs(MEASURE_HEADLINE);
    assert.ok(set.length >= 10, `the 全部 tab renders cards (${set.length})`);
    assertHeadline(set, '1440/all');
    for (const c of set) states.add(c.state);
    console.log('CL-UI-118 L3 全部: ' + JSON.stringify([...new Set(set.map(c => c.state))]));
  }
  assert.ok(states.size >= 2, `more than one state is exercised (${[...states].join(',')})`);
  console.log('CL-UI-118 L3 @1440: ' + JSON.stringify(rec.slice(0, 4).map(c => ({id:c.id, state:c.state, font:c.headFont + '/' + c.nowFont, band:c.bandH, text:c.text.slice(0, 18)}))));
  console.log('CL-UI-118 L3 states: ' + JSON.stringify([...states]));
  // B (1b): the tint + bar are PAINT ONLY — toggling the class on the same card
  // must leave the band (and the whole card) exactly as tall as before.
  const toggled = await evaljs(`(() => {
    const out = [];
    for (const c of [...document.querySelectorAll('#spots-container .card, #spot-region-grid .card')].slice(0, 40)) {
      const band = c.querySelector('[data-layer="subject"]');
      const head = band && band.querySelector('[data-headline]');
      if (!head) continue;
      const withCls = Math.round(band.getBoundingClientRect().height);
      const cardWith = Math.round(c.getBoundingClientRect().height);
      head.classList.remove('cl-headline');
      const without = Math.round(band.getBoundingClientRect().height);
      const cardWithout = Math.round(c.getBoundingClientRect().height);
      head.classList.add('cl-headline');
      out.push({id:c.getAttribute('data-place-id'), withCls, without, cardWith, cardWithout});
    }
    return out;
  })()`);
  assert.ok(toggled.length >= 10, `cards measured with and without the headline class (${toggled.length})`);
  for (const t of toggled) {
    assert.equal(t.withCls, t.without,
      `${t.id}: the tint + left bar add NO height to the subject band (${t.without}px without the class, ${t.withCls}px with)`);
    assert.equal(t.cardWith, t.cardWithout, `${t.id}: and no height to the card (${t.cardWithout} → ${t.cardWith})`);
  }
  console.log('CL-UI-118 L3 toggle: ' + JSON.stringify(toggled.slice(0, 4)));
  await switchTier('recommend');
});
// The styling introduces NO copy: it is classes only — no new i18n key, no
// verdict word and no text node added to the headline line.
test('CL-UI-118 B (2): L3 is typography + paint only — no copy, no i18n key, no verdict change', () => {
  const i = APPJS.indexOf('// CL-UI-118 L3: the headline subject');
  assert.ok(i >= 0, 'the L3 headline wiring exists');
  const j = APPJS.indexOf('// CL-UI-118 L1: the ONE spot-level bell opens its reminder menu.', i);
  assert.ok(j > i, 'the L3 block is delimited');
  const block = APPJS.slice(i, j);
  assert.match(block, /classList\.add\('cl-headline'\)/, 'the focus is a class on the existing line');
  assert.match(block, /setAttribute\('data-state',\(\{rec:'ok',shoot:'chance'\}\)\[clBadgeTier\]\|\|'no'\)/,
    'the state colour comes from the SAME clBadgeTier the badge reads (never a second verdict)');
  assert.equal(/d\(\)\./.test(block), false, 'L3 adds no dictionary key');
  assert.equal(/textContent\s*=/.test(block), false, 'L3 rewrites no text');
  assert.equal(/innerHTML/.test(block), false, 'L3 rewrites no markup');
  // The three state colours are the existing semantic tokens, never a new hex.
  const css = CSS.slice(CSS.indexOf('CL-UI-118 L3: the headline subject'), CSS.length);
  assert.match(css, /\.cl-headline\{[\s\S]*?font-size:var\(--cl-fs-16\)/, 'the headline step is a type token');
  assert.match(css, /\[data-state="ok"\]\{background:var\(--cl-green-bg\);box-shadow:inset 3px 0 0 var\(--cl-green\)\}/);
  assert.match(css, /\[data-state="chance"\]\{background:var\(--cl-amber-bg\);box-shadow:inset 3px 0 0 var\(--cl-amber\)\}/);
  assert.match(css, /\[data-state="no"\]\{background:var\(--cl-grey-bg\);box-shadow:inset 3px 0 0 var\(--cl-grey\)\}/);
  assert.equal(/#[0-9a-fA-F]{3,6}/.test(css), false, 'no hex is introduced outside :root (CL-UI-85)');
});

// Real CDP input, re-measured at click time (CL-UI-102 rule: an off-viewport or
// stale coordinate is a harness bug, so the caller always passes a fresh point).
async function clickAt(x, y) {
  for (const type of ['mousePressed', 'mouseReleased'])
    await send('Input.dispatchMouseEvent', {type, x, y, button:'left', clickCount:1});
  await sleep(400);
}
async function pressKey(key, code, vk) {
  const base = {key, code, windowsVirtualKeyCode: vk, nativeVirtualKeyCode: vk};
  const down = {...base};
  if (key === 'Enter') { down.text = '\r'; down.unmodifiedText = '\r'; }
  else if (key === ' ') { down.text = ' '; down.unmodifiedText = ' '; }
  await send('Input.dispatchKeyEvent', {type:'rawKeyDown', ...down});
  await send('Input.dispatchKeyEvent', {type:'keyUp', ...base});
  await sleep(400);
}
// Both panels report display AND a painted box, so "the panel is up" can never be
// satisfied by a display flag over a zero-width element.
const PANEL_STATE = `(() => {
  const vis = el => !!el && el.style.display === 'flex' && el.getBoundingClientRect().width > 0;
  const w = document.getElementById('modal-overlay'), p = document.getElementById('place-modal-overlay');
  return {weather: vis(w), weatherPanel: w && w.dataset.panel, place: vis(p), placePanel: p && p.dataset.panel};
})()`;

browserTest('CL-UI-118 B (3): the headline row opens the SUBJECT-WINDOW panel, the card body opens the WEATHER panel', {timeout:240000}, async () => {
  await load(1440, 900);
  const before = await evaljs(PANEL_STATE);
  assert.equal(before.weather, false, 'no panel is open before the click');
  assert.equal(before.place, false, 'and no subject panel either');
  // Owner ruling: the headline subject row is the SUBJECT-WINDOW trigger (the same
  // panel the bottom 題材 tool button opens); every other card area stays the card's
  // weather modal. A dead click is forbidden — both halves are asserted below.
  const probe = sel => evaljs(`(async () => {
    const frame = () => new Promise(r => requestAnimationFrame(() => r()));
    const card = document.querySelector('#spots-container .card');
    card.scrollIntoView({block:'center'});
    const r0 = card.getBoundingClientRect();
    const dy = (window.innerHeight/2) - (r0.top + r0.height/2);
    if (Math.abs(dy) > 1) window.scrollBy(0, dy);
    await frame(); await frame();
    const el = card.querySelector(${JSON.stringify(sel)});
    if (!el) return {error: 'missing ' + ${JSON.stringify(sel)}};
    const r = el.getBoundingClientRect();
    const x = r.left + r.width/2, y = r.top + r.height/2;
    const hit = document.elementFromPoint(x, y);
    // Nothing between the hit and the target may be pointer-events:none — that is
    // how a "hit target" silently becomes an interception.
    const blocked = [];
    let e = hit;
    while (e && e !== el) { if (getComputedStyle(e).pointerEvents === 'none') blocked.push(e.tagName + '.' + String(e.className||'')); e = e.parentElement; }
    return {x, y, painted: r.width > 0 && r.height > 0,
      hit: hit ? hit.tagName + '.' + String(hit.className||'').slice(0, 44) : null,
      hitInside: !!(hit && (hit === el || el.contains(hit))), blocked,
      pointerEvents: getComputedStyle(el).pointerEvents,
      tabindex: el.getAttribute('tabindex'), role: el.getAttribute('role')};
  })()`);

  // (a) the headline row → subject-window
  const head = await probe('.cl-subject-row.cl-headline');
  assert.ok(!head.error, String(head.error));
  assert.equal(head.painted, true, 'the headline row has a painted box');
  assert.equal(head.hitInside, true, `the headline row is the hit target at its own centre (hit ${head.hit})`);
  assert.deepEqual(head.blocked, [], 'no ancestor intercepts the headline click with pointer-events:none');
  assert.notEqual(head.pointerEvents, 'none', 'the headline itself accepts pointer events');
  assert.equal(head.tabindex, '0', 'the headline is keyboard reachable');
  assert.equal(head.role, 'button', 'and announces itself as a trigger');
  await clickAt(head.x, head.y);
  const afterHead = await evaljs(PANEL_STATE);
  assert.equal(afterHead.place, true, 'a real click on the headline OPENS the subject-window panel (#place-modal-overlay)');
  assert.equal(afterHead.placePanel, 'subject-window', 'and it is the subject-window panel');
  assert.equal(afterHead.weather, false, 'the weather panel does not open from the headline');
  // Keyboard + focus contract on the SAME row: Escape closes, focus returns here,
  // then Enter and Space each re-open the subject window.
  await pressKey('Escape', 'Escape', 27);
  const closed = await evaljs(`(() => { const p = document.getElementById('place-modal-overlay'), a = document.activeElement;
    return {place: p.style.display, focusHeadline: !!(a && a.hasAttribute && a.hasAttribute('data-headline'))}; })()`);
  assert.equal(closed.place, 'none', 'Escape closes the subject-window panel');
  assert.equal(closed.focusHeadline, true, 'and focus returns to the headline row it was opened from');
  for (const [key, code, vk, name] of [['Enter','Enter',13,'Enter'], [' ','Space',32,'Space']]) {
    const focused = await evaljs(`(() => { const h = document.querySelector('#spots-container .card .cl-subject-row.cl-headline'); h.focus(); return document.activeElement === h; })()`);
    assert.equal(focused, true, `the headline can take focus before ${name}`);
    await pressKey(key, code, vk);
    const st = await evaljs(PANEL_STATE);
    assert.equal(st.place, true, `${name} on the focused headline opens the subject-window panel`);
    assert.equal(st.placePanel, 'subject-window', `${name} opens the subject-window panel, not another one`);
    assert.equal(st.weather, false, `${name} never opens the weather panel`);
    await pressKey('Escape', 'Escape', 27);
    const back = await evaljs(`document.activeElement && document.activeElement.hasAttribute && document.activeElement.hasAttribute('data-headline')`);
    assert.equal(back, true, `focus returns to the headline after closing the ${name}-opened panel`);
  }

  // (b) the card BODY (spot title, identification layer) → weather panel
  const name = await probe('.spot-name');
  assert.ok(!name.error, String(name.error));
  assert.equal(name.hitInside, true, `the spot title is the hit target at its centre (hit ${name.hit})`);
  assert.deepEqual(name.blocked, [], 'no ancestor intercepts the card-body click');
  await clickAt(name.x, name.y);
  const afterName = await evaljs(PANEL_STATE);
  assert.equal(afterName.weather, true, 'a real click on the spot title OPENS the weather panel (#modal-overlay)');
  assert.equal(afterName.weatherPanel, 'weather', 'and it is the weather panel');
  assert.equal(afterName.place, false, 'the subject-window panel does not open from the card body');
  console.log('CL-UI-118 B (3): headline→' + JSON.stringify(afterHead) + ' body→' + JSON.stringify(afterName));
});

test.after(async () => {
  try { if (ws) ws.close(); } catch {}
  try { if (chrome) chrome.kill(); } catch {}
  try { if (server) server.close(); } catch {}
});
