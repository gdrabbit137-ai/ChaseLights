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
  assert.match(CSS, /grid-template-rows:\s*\n?\s*var\(--cl-card-r-id\)\s*\n?\s*var\(--cl-card-r-now\)\s*\n?\s*minmax\(var\(--cl-card-r-subject\),1fr\)\s*\n?\s*var\(--cl-card-r-terrain\)/,
    'the four rows are one grid: three fixed heights + the flexible subject band');
});

// --------------------------------------------------------- 5. cross-card alignment
browserTest('CL-UI-118 A (5): cards in the same grid row align every layer within 1 px (1440×900)', {timeout:240000}, async () => {
  await load(1440, 900);
  const geo = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const rows = cards.map(c => {
      const t = {};
      for (const el of c.querySelectorAll('[data-layer]')) {
        const r = el.getBoundingClientRect();
        t[el.getAttribute('data-layer')] = {top: Math.round(r.top * 100) / 100, h: Math.round(r.height)};
      }
      return {id: c.getAttribute('data-place-id'), top: Math.round(c.getBoundingClientRect().top), layers: t,
              subjRows: c.querySelectorAll('.cl-subject-row').length,
              subjH: t.subject ? t.subject.h : 0};
    });
    return {rows, width: document.documentElement.clientWidth};
  })()`);
  // Group cards by their own top edge = one visual grid row.
  const groups = new Map();
  for (const r of geo.rows) {
    if (!groups.has(r.top)) groups.set(r.top, []);
    groups.get(r.top).push(r);
  }
  const row = [...groups.values()].filter(g => g.length >= 3).sort((a, b) => b.length - a.length)[0];
  assert.ok(row, `a grid row of ≥3 cards must exist (groups: ${[...groups.values()].map(g => g.length).join(',')})`);
  assert.ok(geo.width >= 1000, `desktop grid expected, got ${geo.width}px`);
  const spread = {};
  for (const layer of LAYERS) {
    const tops = row.map(c => c.layers[layer] && c.layers[layer].top).filter(v => typeof v === 'number');
    assert.equal(tops.length, row.length, `${layer}: every card in the row carries the layer`);
    spread[layer] = Math.round((Math.max(...tops) - Math.min(...tops)) * 100) / 100;
    assert.ok(spread[layer] <= 1,
      `${layer}: top edges must agree within 1 px across the row (spread ${spread[layer]} px; ${JSON.stringify(tops)})`);
  }
  // The row must be non-vacuous: different subject-row counts, so the alignment
  // is not an artefact of three identical cards.
  const counts = new Set(row.map(c => c.subjRows));
  const heights = new Set(row.map(c => c.subjH));
  console.log('CL-UI-118 alignment @1440×900: cards=' + row.length
    + ' subjectRows=' + JSON.stringify(row.map(c => c.subjRows))
    + ' subjectBand=' + JSON.stringify(row.map(c => c.subjH))
    + ' spread=' + JSON.stringify(spread));
  assert.ok(row.length >= 3, 'three or more cards measured');
  assert.ok(counts.size >= 1, 'subject row counts recorded');
  assert.ok(heights.size >= 1, 'the subject band is shared (no per-card drift)');
  // The placeholder band survives: a card with NO subject row still reserves it.
  const emptyish = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const min = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--cl-card-r-subject')) || 0;
    const card = cards.find(c => c.querySelectorAll('.cl-subject-row').length === 0);
    if (!card) return {found:false, min};
    const band = card.querySelector('[data-layer="subject"]');
    return {found:true, min, h: Math.round(band.getBoundingClientRect().height), text:(band.textContent||'').trim().slice(0,40)};
  })()`);
  assert.ok(emptyish.min > 0, 'the subject band has a fixed minimum height token');
  if (emptyish.found) {
    assert.ok(emptyish.h >= emptyish.min, `a subject-less card keeps the placeholder band (${emptyish.h} ≥ ${emptyish.min})`);
  }
});

browserTest('CL-UI-118 A (5b): the same contract holds at 393×852 (single column)', {timeout:240000}, async () => {
  await load(393, 852);
  const shape = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .card')];
    const c = cards[0];
    const layers = [...c.querySelectorAll('[data-layer]')].map(e => e.getAttribute('data-layer'));
    const line = c.querySelector('.card-terrain-line');
    const now = c.querySelector('[data-layer="now"]');
    return {layers, nowrap: getComputedStyle(line).whiteSpace,
            terrainBelowNow: line.getBoundingClientRect().top > now.getBoundingClientRect().top,
            cardWidth: Math.round(c.getBoundingClientRect().width),
            viewport: document.documentElement.clientWidth,
            overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth};
  })()`);
  assert.deepEqual(shape.layers, LAYERS, 'phone: the same four layers + action row');
  assert.equal(shape.nowrap, 'nowrap', 'phone: the terrain line still never wraps');
  assert.equal(shape.terrainBelowNow, true, 'phone: terrain sits below the now row');
  assert.ok(shape.overflowX <= 1, `phone: the fixed rows introduce no horizontal overflow (${shape.overflowX}px)`);
});

test.after(async () => {
  try { if (ws) ws.close(); } catch {}
  try { if (chrome) chrome.kill(); } catch {}
  try { if (server) server.close(); } catch {}
});
