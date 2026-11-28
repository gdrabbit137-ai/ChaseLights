// CL-UI-119 — one glyph for the cloud BASE, distinct from the terrain elevation.
//
// Owner spec (docs/backlog/cl-ui-119-cloud-base-icon.md): the now row printed
// 「▲ 1743 m」 (cloud base) and the terrain line 「▲ 256 m」 (spot elevation) with
// the SAME mountain glyph, so one card showed two different numbers under one
// picture. For a photographer the first means 「山頭會不會沒入雲中」 and the second
// 「這個地方多高」 — two quantities that must not look alike.
//
// What this file pins, on the REAL rendered page (no source-only claims):
//   (1) the card's now-row cloud chip resolves to `cloud_base`
//   (2) the terrain elevation chip still resolves to `elevation`
//   (3) the two keys on one card ARE different values (the point of the ticket)
//   (4) the modal hourly kv row and the mobile timeline print the SAME key
//   (5) `cloud_base` is rasterised next to its four neighbours at 12 px AND
//       56 px and every pair differs — a hash of the path body alone cannot see
//       a glyph that reads as a copy on screen
//
// Harness: static server rooted at the repo + raw CDP (the CL-UI-117/118
// pattern, no playwright needed on Windows).
//
// Run: CHROMIUM_EXECUTABLE="C:/Program Files/Google/Chrome/Application/chrome.exe" \
//      node --test apps/web-v2/tests/cl-ui-119-cloud-base-icon.test.mjs
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

const BROWSER = [
  process.env.CHROMIUM_EXECUTABLE,
  process.env.CHROME_PATH,
  ...(process.platform === 'win32'
    ? ['C:/Program Files/Google/Chrome/Application/chrome.exe',
       'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe']
    : ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']),
].filter(Boolean).find(p => existsSync(p)) || null;
const NO_BROWSER = 'no browser binary available in this environment; this suite runs in the Chromium job';
const browserTest = BROWSER ? test : () => {};
if (!BROWSER) test('CL-UI-119 cloud-base icon (browser)', {skip: NO_BROWSER}, () => {});

// The forecast modal reads its per-place shard from `weather_details/…` (moved
// to R2 in CL-PAGES-06, so it is not in the repo). The harness serves a
// synthetic shard carrying the summary's own `updated_at` — that version match
// is what app.js requires before it paints the hourly table (loadDetails).
const REGION_FILE = join(APP, 'tw_weather.json');
const REGION = JSON.parse(readFileSync(REGION_FILE, 'utf8'));
const TPE = 'Asia/Taipei';
// Every hour carries theme_scores for the whole label vocabulary: the modal's
// hourly day-groups only render an hour that has a score block for its theme.
const THEMES = ['all', 'mountain_view', 'alpine_lake', 'sunrise', 'sunset', 'blue_hour', 'sky_glow', 'cloud_sea', 'fog_mist', 'reflection', 'sunbeam', 'milky_way', 'long_exposure', 'city_night', 'city_view', 'coast', 'forest', 'geology', 'lake', 'landscape', 'waterfall', 'snow_scene', 'aurora'];
const THEME_SCORES = Object.fromEntries(THEMES.map(t => [t, {score: 70, status_key: 'OPPORTUNITY_SIMPLE_MATCH'}]));
const localDate = offset => new Intl.DateTimeFormat('en-CA', {timeZone: TPE, year:'numeric', month:'2-digit', day:'2-digit'})
  .format(new Date(Date.now() + offset * 86400000));
// The shard is the served summary spot (name/elevation/timezone/…) with a
// synthetic 3-day hourly forecast, so the modal's own readers all resolve.
function shardBody(placeId) {
  const spot = (REGION.spots || []).find(s => s && s.spot_id === placeId) || {spot_id: placeId, timezone: TPE};
  const rows = [];
  for (const off of [0, 1, 2]) {
    const day = localDate(off);
    for (let h = 0; h < 24; ++h) {
      rows.push({
        time: `${day} ${String(h).padStart(2, '0')}:00`, local_date: day,
        weather_code: 3, temp: 16 + (h % 6), visibility: 14, rh: 78, wind: 2.4,
        c_low: 20, c_mid: 40, c_high: 60,
        cloud_base_asl: 1743, cloud_base_agl: 512,
        sun_azimuth: 111, sun_elevation: 12,
        theme_scores: THEME_SCORES,
      });
    }
  }
  return JSON.stringify({schema_version: REGION.schema_version || 10, updated_at: REGION.updated_at, spot: {...spot, hourly_forecast: rows}});
}

const MIME = {'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.ico':'image/x-icon','.woff2':'font/woff2','.jpg':'image/jpeg','.webp':'image/webp'};
const NO_STORE = {'cache-control':'no-store'};

let server, baseURL, chrome, ws, send, evaljs, ready;
const pendingCalls = new Map();
let nextId = 0;
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function boot() {
  if (ready) return ready;
  ready = (async () => {
    server = createServer((req, res) => {
      res.on('error', () => {});
      const raw = req.url.split('?')[0];
      const shard = /^\/weather_details\/[^/]+\/([^/]+)\.json$/.exec(raw);
      if (shard) {
        const body = shardBody(decodeURIComponent(shard[1]));
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
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui119-')), 'about:blank',
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

async function load(width, height) {
  await boot();
  await send('Emulation.setDeviceMetricsOverride', {width, height, deviceScaleFactor:1, mobile:width < 700});
  await send('Page.navigate', {url: baseURL + 'index.html'});
  const deadline = Date.now() + 60000;
  let cards = 0;
  while (Date.now() < deadline) {
    await sleep(500);
    cards = await evaljs(`document.querySelectorAll('#spots-container .card').length`).catch(() => 0);
    if (cards >= 3) break;
  }
  assert.ok(cards >= 3, `expected at least three cards, got ${cards}`);
  await sleep(1200);
  return cards;
}

async function clickAt(x, y) {
  await send('Input.dispatchMouseEvent', {type:'mousePressed', x, y, button:'left', clickCount:1});
  await send('Input.dispatchMouseEvent', {type:'mouseReleased', x, y, button:'left', clickCount:1});
  await sleep(500);
}

// ----------------------------------------------- 1. the two chips on one card
browserTest('CL-UI-119 (1): the now-row cloud chip is `cloud_base`, the terrain chip stays `elevation`', {timeout:240000}, async () => {
  await load(1440, 900);
  const chips = await evaljs(`(() => {
    const out = [];
    for (const card of document.querySelectorAll('#spots-container .card')) {
      const now = card.querySelector('[data-layer="now"]');
      const terrain = card.querySelector('[data-layer="terrain"]');
      if (!now || !terrain) continue;
      const keyOf = chip => { const s = chip && chip.querySelector('svg[data-cl-icon]'); return s ? s.getAttribute('data-cl-icon') : null; };
      const nowChips = [...now.querySelectorAll('.metric-chip')];
      const terChips = [...terrain.querySelectorAll('.metric-chip')];
      const cloud = nowChips.find(c => /\\d+\\s*m\\b/.test(c.textContent || ''));
      const elev = terChips.find(c => /^\\s*(\\S+\\s*)?\\d+\\s*m\\s*$/.test((c.textContent || '').trim()));
      if (!cloud || !elev) continue;
      out.push({
        id: card.getAttribute('data-place-id'),
        cloudKey: keyOf(cloud), elevKey: keyOf(elev),
        cloudText: (cloud.textContent || '').replace(/\\s+/g, ' ').trim(),
        elevText: (elev.textContent || '').replace(/\\s+/g, ' ').trim(),
        cloudInNow: now.contains(cloud), elevInTerrain: terrain.contains(elev),
        cloudSvgBox: (() => { const s = cloud.querySelector('svg[data-cl-icon]'); if (!s) return null; const r = s.getBoundingClientRect(); return {w: Math.round(r.width), h: Math.round(r.height)}; })(),
      });
    }
    return out;
  })()`);
  assert.ok(chips.length >= 3, `cards carrying both a cloud-base and an elevation chip (${chips.length})`);
  for (const c of chips) {
    assert.equal(c.cloudInNow, true, `${c.id}: the cloud-base chip sits in the now row`);
    assert.equal(c.elevInTerrain, true, `${c.id}: the elevation chip sits in the terrain line`);
    assert.equal(c.cloudKey, 'cloud_base', `${c.id}: the cloud chip draws cloud_base (got ${c.cloudKey})`);
    assert.equal(c.elevKey, 'elevation', `${c.id}: the elevation chip keeps the mountain glyph (got ${c.elevKey})`);
    // THE POINT OF THE TICKET: two different values, two different pictures.
    assert.notEqual(c.cloudKey, c.elevKey, `${c.id}: cloud base and spot elevation must not share a glyph`);
    assert.match(c.cloudText, /\d+\s*m/, `${c.id}: the cloud base text is unchanged (${c.cloudText})`);
    assert.ok(c.cloudSvgBox && c.cloudSvgBox.w > 0 && c.cloudSvgBox.h > 0, `${c.id}: the cloud-base glyph is painted (${JSON.stringify(c.cloudSvgBox)})`);
  }
  console.log('CL-UI-119 (1): ' + JSON.stringify(chips.slice(0, 3)));
});

// ------------------------------- 2. one glyph per quantity across every surface
browserTest('CL-UI-119 (2): the modal hourly row and the mobile timeline print the same key', {timeout:240000}, async () => {
  await load(1440, 900);
  // The weather panel opens from the card body (spot title) — CL-UI-118 B (3).
  const target = await evaljs(`(() => {
    const card = document.querySelector('#spots-container .card');
    const el = card.querySelector('.spot-name');
    el.scrollIntoView({block:'center'});
    const r = el.getBoundingClientRect();
    return {x: r.left + r.width / 2, y: r.top + r.height / 2};
  })()`);
  await clickAt(target.x, target.y);
  // The hourly table settles asynchronously (summary fetch + shard merge).
  const deadline = Date.now() + 60000;
  let kvKeys = [];
  while (Date.now() < deadline) {
    kvKeys = await evaljs(`(() => {
      const rows = [...document.querySelectorAll('#timeline-groups tr.detail .kv')];
      const keys = [];
      for (const kv of rows) {
        // the cloud-base cell is the one whose label carries a glyph
        for (const cell of kv.querySelectorAll(':scope > span')) {
          const svg = cell.querySelector('svg[data-cl-icon]');
          if (svg) keys.push({key: svg.getAttribute('data-cl-icon'), cap: cell.textContent.replace(/\\s+/g, ' ').trim()});
        }
      }
      return keys;
    })()`).catch(() => []);
    if (kvKeys.length) break;
    await sleep(700);
  }
  assert.ok(kvKeys.length >= 1, 'the modal hourly kv rows rendered with their glyph (none found)');
  for (const k of kvKeys) assert.equal(k.key, 'cloud_base', `the modal hourly cloud-base label draws cloud_base (got ${k.key} for 「${k.cap}」)`);

  const mobileKeys = await evaljs(`(() => [...document.querySelectorAll('#timeline-mobile .timeline-mobile-metric svg[data-cl-icon]')].map(s => s.getAttribute('data-cl-icon')))()`);
  assert.ok(mobileKeys.length >= 1, 'the mobile timeline metric rows rendered with their glyph');
  for (const k of mobileKeys) assert.equal(k, 'cloud_base', `the mobile timeline cloud-base metric draws cloud_base (got ${k})`);
  // Same quantity, same glyph — across the two shells.
  assert.equal(new Set([...kvKeys.map(k => k.key), ...mobileKeys]).size, 1, 'every cloud-base surface resolves to ONE key');
});

// ------------------------- 3. really different pictures at 12 px and 56 px
browserTest('CL-UI-119 (3): cloud_base is visually distinct from its four neighbours at 12 px and 56 px', {timeout:240000}, async () => {
  await load(1440, 900);
  const hashes = await evaljs(`(async () => {
    const ic = k => (window.clIcon ? window.clIcon(k) : '');
    const keys = ['cloud_base', 'cloud', 'fog', 'elevation', 'weather_overview'];
    const draw = (svgText, px) => new Promise((resolve, reject) => {
      const img = new Image();
      const svg = svgText.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ');
      img.onload = () => {
        const c = document.createElement('canvas');
        c.width = px; c.height = px;
        const ctx = c.getContext('2d');
        ctx.clearRect(0, 0, px, px);
        ctx.drawImage(img, 0, 0, px, px);
        const d = ctx.getImageData(0, 0, px, px).data;
        // Coverage + a coarse ink signature: the covered-pixel COUNT alone can
        // collide between two different silhouettes, so hash the binary mask.
        let sig = '', cover = 0;
        for (let i = 3; i < d.length; i += 4) { const on = d[i] > 40 ? '1' : '0'; sig += on; if (on === '1') cover++; }
        resolve({cover, sig});
      };
      img.onerror = () => reject(new Error('svg rasterise failed'));
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    });
    const out = {};
    for (const px of [12, 56]) {
      out[px] = {};
      for (const k of keys) {
        const r = await draw(ic(k), px);
        out[px][k] = {cover: r.cover, sig: r.sig};
      }
    }
    return out;
  })()`);
  for (const px of ['12', '56']) {
    const set = hashes[px];
    const keys = Object.keys(set);
    assert.equal(keys.length, 5, `${px}px: all five glyphs rasterised`);
    for (const k of keys) assert.ok(set[k].cover > 0, `${px}px: ${k} paints ink (${set[k].cover} px)`);
    const seen = new Map();
    for (const k of keys) {
      assert.equal(seen.has(set[k].sig), false,
        `${px}px: ${k} is pixel-identical to ${seen.get(set[k].sig)} — it needs its own silhouette`);
      seen.set(set[k].sig, k);
    }
    assert.equal(seen.size, keys.length, `${px}px: five distinct silhouettes (${seen.size}/${keys.length})`);
  }
  console.log('CL-UI-119 (3): ' + JSON.stringify(Object.fromEntries(Object.entries(hashes).map(([px, m]) => [px, Object.fromEntries(Object.entries(m).map(([k, v]) => [k, v.cover]))]))));
});

test.after(async () => {
  try { if (ws) ws.close(); } catch {}
  try { if (chrome) chrome.kill(); } catch {}
  try { if (server) server.close(); } catch {}
});
