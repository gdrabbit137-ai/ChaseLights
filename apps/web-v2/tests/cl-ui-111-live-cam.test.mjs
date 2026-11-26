// CL-UI-111 (owner ruling): places with an official live camera get a 4th
// card button 「🔴 LIVE」 (thumbnail background + red-dot badge) in the
// 題材/地圖/天氣圖 tool row; places without a camera keep the three-button row.
// The click opens an IN-APP live panel that plays the official 北觀處 YouTube
// live stream via an embedded iframe — click-to-load (zero preload), the
// player carries the 「交通部觀光署北觀處」 attribution and an 「在 YouTube
// 開啟」 fallback link (new window, never an app redirect); fullscreen uses
// the native iframe button. The subject panel's 「拍攝位置」 area gets the
// same-source thumbnail entry. Data: data/v2/copy/live_cam.json
// (place_id → video_id/thumb/watch/official page), verified against the
// 北觀處 official site + YouTube oembed on 2026-11-17.
// CL-UI-119: tw-001 大屯山 joins with the 陽明山國家公園管理處 official live
// stream (YMSNP 即時影像專區, verified 2026-11-21); attribution moved to
// per-entry source_label_i18n because the two agencies differ.
// CL-UI-120: tw-002 象山／tw-179 碧山巖／tw-005 大稻埕碼頭 join with the
// 臺北市政府觀光傳播局 official channel 「Taipei Travel Live Cam 台北觀光即時
// 影像」 (@taipeitravelofficial, verified 2026-11-21); the channel rotates
// 24/7 live video_ids, so tw-005 carries the current isLive:true id.
//
// Run: node --test apps/web-v2/tests/cl-ui-111-live-cam.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { mkdtempSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const cssSource = readFileSync(join(WEB, 'assets', 'app.css'), 'utf8');
const htmlSource = readFileSync(join(WEB, 'index.html'), 'utf8');
const camData = JSON.parse(readFileSync(join(WEB, 'data', 'v2', 'copy', 'live_cam.json'), 'utf8'));

const CAM_IDS = ['tw-001', 'tw-002', 'tw-005', 'tw-008', 'tw-010', 'tw-073', 'tw-074', 'tw-161', 'tw-179'];

test('CL-UI-111/119 (D): live_cam.json — verified mapping, per-entry attribution, honest pending note', () => {
  assert.equal(camData.stream_format, 'youtube_live', '查證結論：串流形式＝YouTube live（非 HLS）');
  for (const id of CAM_IDS) {
    const e = camData.entries[id];
    assert.ok(e, `${id} must have a live cam entry`);
    assert.match(e.video_id, /^[A-Za-z0-9_-]{11}$/, `${id} video_id must be a YouTube id`);
    assert.match(e.thumb_url, new RegExp(`i\\.ytimg\\.com/vi/${e.video_id}/hqdefault\\.jpg`));
    assert.match(e.watch_url, new RegExp(`youtube\\.com/watch\\?v=${e.video_id}`));
    // CL-UI-119: provenance per entry — official page + verification date.
    assert.ok(e.official_page && e.official_page.startsWith('https://'), `${id} keeps an official page`);
    assert.match(e.verified_at, /^\d{4}-\d{2}-\d{2}$/, `${id} records the verification date`);
    if (id === 'tw-001') {
      assert.match(e.official_page, /ymsnp\.gov\.tw/, 'tw-001 keeps the 陽明山國家公園管理處 official page');
      assert.match(e.note, /大屯山主峰/, 'tw-001 carries the honest camera-location note');
    } else if (id === 'tw-002' || id === 'tw-179' || id === 'tw-005') {
      // CL-UI-120: Taipei City DoIT official channel is the provenance page.
      assert.match(e.official_page, /youtube\.com\/@taipeitravelofficial/,
        `${id} keeps the Taipei Travel Live Cam official channel page`);
    } else {
      assert.match(e.official_page, /northguan-nsa\.gov\.tw/, `${id} keeps the 北觀處 official page`);
    }
    // CL-UI-120: the three Taipei City DoIT entries pin their verified video ids.
    if (id === 'tw-002') assert.equal(e.video_id, 'z_fY1pj1VBw');
    if (id === 'tw-179') assert.equal(e.video_id, 'uvwfYzwY8tg');
    if (id === 'tw-005') {
      assert.equal(e.video_id, 'Ndo_8RuefH4',
        'tw-005 carries the CURRENT isLive:true 大稻埕 id (3Sf6rJgyObs ended 2026-07-10)');
      assert.match(e.note, /3Sf6rJgyObs/, 'tw-005 note honestly records the rotated id');
      assert.match(e.note, /isLiveNow:false/);
    }
    // Per-entry attribution (agencies differ): trilingual, complete display string.
    assert.ok(e.source_label_i18n, `${id} has a per-entry source_label_i18n`);
    for (const lang of ['zh-TW', 'en', 'ja']) {
      const label = e.source_label_i18n[lang];
      assert.ok(label && label.length > 0, `${id} ${lang} attribution label`);
      assert.match(label, /^(影像來源：|Live camera: |映像提供：)/, `${id} ${lang} label carries the prefix`);
    }
    assert.match(e.source_label_i18n['zh-TW'],
      id === 'tw-001' ? /陽明山國家公園管理處/
        : (id === 'tw-002' || id === 'tw-179' || id === 'tw-005') ? /臺北市政府觀光傳播局/
        : /交通部觀光署北觀處/,
      `${id} attribution names the right agency`);
    // CL-UI-120: the English attribution uses the agency's own full name.
    if (id === 'tw-002' || id === 'tw-179' || id === 'tw-005') {
      assert.match(e.source_label_i18n.en,
        /Taipei City Government Department of Information and Tourism/,
        `${id} en attribution names Taipei City Government DoIT`);
    }
  }
  assert.equal(Object.keys(camData.entries).length, CAM_IDS.length, 'no unmapped extra entries');
  // 白沙灣 has an official stream but NO catalog place_id yet — recorded, not mapped.
  assert.match(camData.pending_entries.notes, /白沙灣/);
  assert.match(camData.pending_entries.notes, /FbB8WDUXXqU/);
  assert.match(camData.pending_entries.notes, /place_id/);
  // Attribution is the owner-specified label (data layer + UI share it).
  assert.match(camData.source_label_i18n['zh-TW'], /交通部觀光署北觀處/);
});

test('CL-UI-111 (S1): i18n keys exist in all three dictionaries', () => {
  const checks = [
    ['live_link', '🔴 LIVE'],
    ['live_panel_title', '即時影像'],
    ['live_source_label', '交通部觀光署北觀處'],
    ['live_open_youtube', '在 YouTube 開啟'],
    ['close_live', '關閉即時影像'],
  ];
  for (const [k, v] of checks) {
    const re = new RegExp(`${k}:'[^']*${v.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[^']*'`);
    assert.match(appSource, re, `zh-TW ${k}`);
  }
  assert.match(appSource, /live_link:'🔴 LIVE', live_panel_title:'Live camera', live_source_label:'Live camera: North Coast & Guanyinshan National Scenic Area Administration, MOTC', live_open_youtube:'Open on YouTube', close_live:'Close live camera'/);
  assert.match(appSource, /live_link:'🔴 LIVE', live_panel_title:'ライブカメラ', live_source_label:'映像提供：交通部観光署 北海岸及観音山国家風景区管理処', live_open_youtube:'YouTubeで開く', close_live:'ライブカメラを閉じる'/);
});

test('CL-UI-111 (S2): loader rides the single gated render; fail-soft to 3 buttons', () => {
  assert.match(appSource, /function ensureLiveCams\(\)\{\s*\n\s*if\(!liveCamsPromise\)\{\s*\n\s*liveCamsPromise=fetch\('\.\/data\/v2\/copy\/live_cam\.json',\{cache:'no-cache'\}\)/,
    'mapping loads from data/v2/copy/live_cam.json (same home as fail_reason_overrides.json)');
  assert.match(appSource,
    /return Promise\.all\(\[ensureFailOverrides\(\),ensureSubjectCards\(\),ensureLiveCams\(\)\]\)\.then\(\(\)=>j\);/,
    'live cams load inside the SAME gated bundle promise — cards paint once with the correct button count');
  assert.match(appSource, /\.catch\(\(\)=>\{liveCams=null;return null;\}\);/,
    'load failure never blocks rendering — spots keep the three-button row');
  // The 4th button only ever ADDS to the row: '' when the place has no camera.
  assert.match(appSource, /function liveCamBtnHtml\(spot\)\{\s*\n\s*const cam=liveCamFor\(spot\.spot_id\);\s*\n\s*if\(!cam\)return '';/);
});

test('CL-UI-111 (S3): 4th card button — thumbnail bg + red dot, mounted after 天氣圖', () => {
  assert.match(appSource,
    /\$\{toolButtonInner\(d\(\)\.radar_link\)\}<\/a>\$\{liveCamBtnHtml\(spot\)\}<\/div><\/div>`;/,
    'LIVE mounts as the 4th button in the 題材/地圖/天氣圖 row');
  assert.match(appSource, /class="tool-link tool-live" data-live-btn data-live-place="\$\{esc\(spot\.spot_id\)\}"/);
  assert.match(appSource, /<img src="\$\{esc\(cam\.thumb_url\)\}" alt="" loading="lazy" decoding="async">/,
    'thumbnail is a lazy <img> — no preloaded background fetch');
  assert.match(appSource, /<span class="tool-live-dot" aria-hidden="true"><\/span>/,
    'red-dot live badge');
  // Click wiring opens the live panel (never navigates, never opens YouTube).
  assert.match(appSource, /const clLiveBtn=card\.querySelector\('\[data-live-btn\]'\);\s*\n\s*if\(clLiveBtn\)clLiveBtn\.onclick=e=>\{e\.preventDefault\(\);e\.stopPropagation\(\);openLiveModal\(spot\);\};/);
});

test('CL-UI-111 (S4): in-app panel — zero-preload iframe, attribution, fallback link', () => {
  // Zero preload: the iframe is created ONLY inside openLiveModal (click-time);
  // no static iframe exists in index.html.
  assert.doesNotMatch(htmlSource, /<iframe/i, 'index.html must not ship any iframe');
  assert.match(appSource, /function openLiveModal\(spot\)\{\s*\n\s*const cam=liveCamFor\(spot\.spot_id\);\s*\n\s*if\(!cam\)return;/);
  assert.match(appSource, /document\.getElementById\('live-frame-host'\)\.innerHTML=`<iframe class="live-frame" src="https:\/\/www\.youtube\.com\/embed\/\$\{encodeURIComponent\(cam\.video_id\)\}\?autoplay=1&mute=1&rel=0"/,
    'official YouTube embed, in-app (never a YouTube-app redirect)');
  // INT-204 owner ruling: click LIVE plays immediately (autoplay) with sound
  // OFF until the user unmutes (mute=1 keeps browser autoplay policy happy).
  assert.match(appSource, /src="https:\/\/www\.youtube\.com\/embed\/\$\{encodeURIComponent\(cam\.video_id\)\}\?autoplay=1&mute=1&rel=0"/,
    'live modal iframe src carries autoplay=1 and mute=1');
  assert.match(appSource, /allowfullscreen loading="lazy" referrerpolicy="strict-origin-when-cross-origin"/,
    'fullscreen rides the native iframe button');
  // CL-UI-119: per-entry attribution — the entry's own trilingual label wins,
  // the dictionary label stays the fallback for entries without one.
  assert.match(appSource, /const perEntrySource=\(cam\.source_label_i18n&&\(\(cam\.source_label_i18n\[currentLang\]\)\|\|cam\.source_label_i18n\['zh-TW'\]\)\)\|\|null;/,
    'per-entry source label resolved currentLang → zh-TW');
  assert.match(appSource, /document\.getElementById\('live-source-label'\)\.textContent=perEntrySource\|\|d\(\)\.live_source_label;/,
    '署名 lives under the player (per-entry label, dict fallback)');
  assert.match(appSource, /yt\.href=cam\.watch_url\|\|`https:\/\/www\.youtube\.com\/watch\?v=\$\{encodeURIComponent\(cam\.video_id\)\}`;\s*\n\s*yt\.textContent=d\(\)\.live_open_youtube;/,
    '在 YouTube 開啟 fallback link');
  // Closing the panel unloads the stream.
  assert.match(appSource, /function closeLiveModal\(e\)\{[\s\S]*?overlay\.style\.display='none';\s*\n\s*document\.getElementById\('live-frame-host'\)\.innerHTML='';/);
  // Shell in index.html + scroll lock includes the new overlay.
  assert.match(htmlSource, /id="live-modal-overlay"/);
  assert.match(htmlSource, /id="live-frame-host"/);
  assert.match(htmlSource, /id="live-open-yt" href="#" target="_blank" rel="noopener noreferrer"/);
  assert.match(appSource, /document\.getElementById\('live-modal-overlay'\)\]\.some\(el=>el\?\.style\.display==='flex'\)/);
});

test('CL-UI-111 (S5): subject panel 「拍攝位置」 thumbnail entry — same data source', () => {
  assert.match(appSource, /const clLiveEntry=viewpoints\.length\?liveCamThumbEntryHtml\(spot\):'';/,
    'entry belongs to the 拍攝位置 area');
  assert.match(appSource, /\$\{\(metaRows\.length\|\|clLiveEntry\)\?`<div class="opportunity-meta">\$\{metaRows\.join\(''\)\}\$\{clLiveEntry\}<\/div>`:''\}/);
  assert.match(appSource, /class="live-thumb-entry" data-live-btn data-live-place="\$\{esc\(spot\.spot_id\)\}"/);
  assert.match(appSource, /body\.querySelectorAll\('\[data-live-btn\]'\)\.forEach\(el=>\{\s*\n\s*el\.addEventListener\('click',e=>\{e\.preventDefault\(\);e\.stopPropagation\(\);openLiveModal\(spot\);\}\);\s*\n\s*\}\);/,
    'panel entries open the SAME live panel');
});

test('CL-UI-111 (S6): css — dot uses the contract red token, lazy-player shell', () => {
  assert.match(cssSource, /\.tool-live-dot \{[\s\S]*?background:var\(--cl-red\);/);
  assert.match(cssSource, /\.tool-live-thumb \{\s*\n\s*position:absolute;\s*\n\s*inset:0;\s*\n\s*z-index:-1;/,
    'thumbnail paints as the button background');
  assert.match(cssSource, /\.live-frame-host \{[\s\S]*?aspect-ratio: 16 \/ 9;/);
  assert.match(cssSource, /\.live-thumb-entry-img img \{[\s\S]*?width: 100%;\s*\n\s*height: 100%;\s*\n\s*object-fit: cover;/);
});

test('CL-UI-111 (S7): cache-bust stamp bumped to clui118', () => {
  assert.match(htmlSource, /assets\/app\.js\?v=clui132/);
  assert.doesNotMatch(htmlSource, /clui110/);
});

// ---- (F) extracted-function checks ------------------------------------------
const GRAB = appSource.slice(
  appSource.indexOf('let liveCams=null, liveCamsPromise=null;'),
  appSource.indexOf('    // CL-UI-63: subject-card lookup uses the committed derived artifact')
);
function buildFns(withCam) {
  const prelude = withCam
    ? `let liveCams={'tw-074':{video_id:'ZjuY4qKaj40',thumb_url:'https://i.ytimg.com/vi/ZjuY4qKaj40/hqdefault.jpg',watch_url:'https://www.youtube.com/watch?v=ZjuY4qKaj40',official_page:'x'},'tw-008':{video_id:'gNWeZsaqD98',thumb_url:'https://i.ytimg.com/vi/gNWeZsaqD98/hqdefault.jpg',watch_url:'https://www.youtube.com/watch?v=gNWeZsaqD98',official_page:'x'}};`
    : 'let liveCams=null;';
  const src = `${prelude}
    const esc=s=>String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({
      live_link:'🔴 LIVE',
      live_panel_title:'即時影像'
    });
    function toolButtonAttrs(label,extraTitle){const title=extraTitle?\`\${extraTitle} · \${label}\`:label;return \` title="\${esc(title)}" aria-label="\${esc(label)}"\`;}
    function toolButtonInner(label){const icoMatch=label.match(/^(\\S+)\\s*(.*)$/);const ico=icoMatch?icoMatch[1]:label;const txt=icoMatch?icoMatch[2]:'';return \`<span class="tool-ico" aria-hidden="true">\${ico}</span><span class="tool-txt">\${esc(txt)}</span>\`;}
    ${GRAB.replace('let liveCams=null, liveCamsPromise=null;', '')}
    return {liveCamFor,liveCamBtnHtml,liveCamThumbEntryHtml};`;
  return new Function(src)();
}

test('CL-UI-111 (F1): no mapping → the helper returns "" (three-button row intact)', () => {
  const fns = buildFns(false);
  assert.equal(fns.liveCamFor('tw-074'), null);
  assert.equal(fns.liveCamBtnHtml({ spot_id: 'tw-074' }), '');
  assert.equal(fns.liveCamThumbEntryHtml({ spot_id: 'tw-074' }), '');
});

test('CL-UI-111 (F2): with mapping → 4th button anatomy (thumb lazy img + dot + label)', () => {
  const fns = buildFns(true);
  assert.equal(fns.liveCamFor('tw-074').video_id, 'ZjuY4qKaj40');
  const btn = fns.liveCamBtnHtml({ spot_id: 'tw-074' });
  assert.match(btn, /^<a href="#" class="tool-link tool-live" data-live-btn data-live-place="tw-074"/);
  assert.match(btn, /title="🔴 LIVE" aria-label="🔴 LIVE"/);
  assert.match(btn, /<img src="https:\/\/i\.ytimg\.com\/vi\/ZjuY4qKaj40\/hqdefault\.jpg" alt="" loading="lazy" decoding="async">/);
  assert.match(btn, /<span class="tool-live-dot" aria-hidden="true"><\/span>/);
  assert.match(btn, /<span class="tool-ico" aria-hidden="true">🔴<\/span><span class="tool-txt">LIVE<\/span>/);
  // XSS hardening: a hostile spot_id must be escaped, never emitted raw.
  assert.doesNotMatch(fns.liveCamBtnHtml({ spot_id: '"><script>' }), /<script>/);
  const entry = fns.liveCamThumbEntryHtml({ spot_id: 'tw-008' });
  assert.match(entry, /^<button type="button" class="live-thumb-entry" data-live-btn data-live-place="tw-008"/);
  assert.match(entry, /loading="lazy"/);
  assert.match(entry, /<span class="tool-live-dot"/);
});

// ---- (H) headless raw-CDP checks (real render, real click, hermetic network) --
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs, ready, loadCount = 0;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();

// Lazy per-file init (CL-UI-90 harness rule): never a root test.before().
async function bootBrowser() {
  if (ready) return ready;
  ready = (async () => {
    const MIME = { '.html': 'text/html', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml' };
    server = createServer((req, res) => {
      const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
      const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
      try { const body = readFileSync(file);
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
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui111-')), 'about:blank'],
      { stdio: ['ignore', 'ignore', 'pipe'] });
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = '';
      let loopLast = Date.now(); const loopStart = loopLast;
      const t = setInterval(() => {
        const now = Date.now();
        if (now - loopLast < 1500 && now - loopStart > 60000) { clearInterval(t); reject(new Error('no devtools endpoint')); }
        loopLast = now;
      }, 250);
      chrome.stderr.on('data', d => { buf += d;
        const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearInterval(t); resolve(m[1]); } });
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
      if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
      // CL-UI-111: raw-CDP navigation race guard — a Runtime.evaluate can land
      // on the STALE previous document before Page.navigate commits; every
      // loadPage() awaits a NEW load event before polling for .card.
      if (m.method === 'Page.loadEventFired') loadCount++; };
    send = (method, params = {}) => new Promise((resolve, reject) => {
      const i = nextId(); pending.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
      ws.send(JSON.stringify({ id: i, method, params }));
    });
    evaljs = async (expr) => {
      const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
      return r.result?.result?.value ?? r.result?.value;
    };
    // Hermetic: block every YouTube request so the iframe src can be asserted
    // without a network load.
    await send('Network.enable');
    await send('Network.setBlockedURLs', { urls: ['*://www.youtube.com/*', '*://i.ytimg.com/*', '*://googlevideo.com/*'] });
  })().catch(e => { ready = null; throw e; });
  return ready;
}

function teardownBrowser() {
  return Promise.all([
    (async () => { try { ws?.close(); } catch {} })(),
    (async () => { try { chrome?.kill(); } catch {} })(),
    (async () => { await new Promise(r => server?.close(r)); })()
  ]).then(() => { ready = null; });
}

// Global teardown for the single shared headless session (one boot, one kill).
test.after(() => teardownBrowser());

async function loadPage(width = 1280, height = 900, mobile = false) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile });
  await send('Page.enable');
  const prevLoads = loadCount;
  await send('Page.navigate', { url: baseURL });
  // Stale-document guard: wait until a NEW load event confirms the navigation.
  await evaljs(`null`); // settle pending evaluate traffic before the wait
  await new Promise((resolve, reject) => {
    const t0 = Date.now();
    const iv = setInterval(() => {
      if (loadCount > prevLoads) { clearInterval(iv); resolve(); }
      else if (Date.now() - t0 > 20000) { clearInterval(iv); reject(new Error('navigation never committed')); }
    }, 50);
  });
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>20000){clearInterval(iv);reject(new Error('cards never rendered'));}
    },100);
  })`);
  await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50)})`);
  // Show every tier so the five cam places are all in the DOM regardless of
  // today's verdicts.
  await evaljs(`(() => {
    const tabs=[...document.querySelectorAll('#tier-tabs button')];
    const all=tabs.find(b=>b.textContent.includes('全部'));
    if(all){all.click();return 'clicked';}
    return 'no-tabs';
  })()`);
  // CL-CI-42: the tier-tab click re-renders the grid (filterAndRender clears
  // innerHTML first). A fixed 400 ms sleep could land inside that window and
  // the probe then read 0 cards. Wait until the card count is non-zero AND
  // stable across two samples instead.
  await evaljs(`new Promise((resolve)=>{let last=-1,same=0;const t0=Date.now();
    const iv=setInterval(()=>{const n=document.querySelectorAll('.card').length;
      if(n>0&&n===last)same++;else same=0;last=n;
      if(same>=2||Date.now()-t0>20000){clearInterval(iv);resolve(n);}},120);})`);
}

test('CL-UI-111 (H1): cards with a camera get the 4th LIVE button; without keep 3', async () => {
  await bootBrowser();
  {
    await loadPage();
    const probe = await evaljs(`(() => {
      const cards=[...document.querySelectorAll('.card')];
      const out={total:cards.length,live:[],plain:null,names:{}};
      for(const c of cards){
        const name=(c.querySelector('.spot-name')||{}).textContent||'';
        const row=c.querySelector('.card-footer-tools div:last-child');
        const kids=row?[...row.children]:[];
        const live=c.querySelector('[data-live-btn]');
        const info={name,kids:kids.length,
          liveId:live?live.getAttribute('data-live-place'):null,
          hasLiveAnchor:!!(live&&live.classList.contains('tool-live')&&live.tagName==='A'),
          dot:!!c.querySelector('.tool-live-dot'),
          lazyImg:live&&live.querySelector('img')?live.querySelector('img').getAttribute('loading'):null};
        if(live){out.live.push(info);out.names[name]=info;}
        else if(!out.plain&&kids.length===3)out.plain=info;
      }
      return out;
    })()`);
    assert.ok(probe.total > 10, `cards rendered (${probe.total})`);
    assert.ok(probe.live.length >= 1, 'at least one cam place rendered a LIVE button');
    for (const l of probe.live) {
      assert.equal(l.kids, 4, `${l.name}: 4-button row (題材/地圖/天氣圖/LIVE)`);
      assert.ok(CAM_IDS.includes(l.liveId), `${l.name}: data-live-place=${l.liveId} must be a mapped place`);
      assert.equal(l.hasLiveAnchor, true);
      assert.equal(l.dot, true, `${l.name}: red-dot badge present`);
      assert.equal(l.lazyImg, 'lazy', `${l.name}: thumbnail img is loading=lazy`);
    }
    assert.ok(probe.plain, 'at least one three-button card exists');
    assert.equal(probe.plain.kids, 3, `${probe.plain.name}: no-camera card keeps 3 buttons`);
    // The whole catalog has exactly five mapped places — no other card claims LIVE.
    const liveIds = probe.live.map(l => l.liveId);
    for (const id of liveIds) assert.ok(CAM_IDS.includes(id));
    // No iframe anywhere before a click (zero preload).
    const iframes = await evaljs(`document.querySelectorAll('iframe').length`);
    assert.equal(iframes, 0, 'no iframe exists before the panel is opened');
  }
});

test('CL-UI-111 (H2): LIVE click opens the in-app panel — embed iframe + attribution + fallback link; close unloads', async () => {
  await bootBrowser();
  {
    await loadPage();
    const before = await evaljs(`document.querySelectorAll('iframe').length`);
    assert.equal(before, 0);
    const openRes = await evaljs(`(() => {
      const live=[...document.querySelectorAll('.card [data-live-btn]')]
        .find(b=>b.getAttribute('data-live-place')==='tw-074');
      if(!live)return {error:'no tw-074 live button'};
      live.click();
      const ov=document.getElementById('live-modal-overlay');
      const frame=document.querySelector('#live-frame-host iframe.live-frame');
      const yt=document.getElementById('live-open-yt');
      return {
        visible: ov && ov.style.display==='flex',
        title: document.getElementById('live-modal-title').textContent,
        src: frame?frame.getAttribute('src'):null,
        fullscreen: frame?frame.hasAttribute('allowfullscreen'):null,
        label: document.getElementById('live-source-label').textContent,
        ytHref: yt?yt.getAttribute('href'):null,
        ytTarget: yt?yt.getAttribute('target'):null,
        ytText: yt?yt.textContent:null
      };
    })()`);
    assert.equal(openRes.visible, true, 'panel opens in-app');
    assert.match(openRes.title, /即時影像/);
    assert.match(openRes.title, /野柳/);
    assert.match(openRes.src, /www\.youtube\.com\/embed\/ZjuY4qKaj40/, 'official YouTube embed iframe (lazy, click-time)');
    assert.equal(openRes.fullscreen, true);
    assert.equal(openRes.label, '影像來源：交通部觀光署北觀處');
    assert.equal(openRes.ytHref, 'https://www.youtube.com/watch?v=ZjuY4qKaj40');
    assert.equal(openRes.ytTarget, '_blank', 'fallback link opens a new window');
    assert.equal(openRes.ytText, '在 YouTube 開啟');
    // Screenshot evidence (blocked network → black player is expected).
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    const { writeFileSync } = await import('node:fs');
    writeFileSync(join(WEB, 'apps', 'web-v2', 'audits', 'design-mockups', 'clui111-live-panel-desktop.png'), Buffer.from(shot.data, 'base64'));
    // Close → overlay hidden AND the iframe is dropped (stream unloads).
    const closed = await evaljs(`(() => {
      closeLiveModal();
      const ov=document.getElementById('live-modal-overlay');
      return {display:ov.style.display, hostHTML:document.getElementById('live-frame-host').innerHTML,
        iframes:document.querySelectorAll('iframe').length};
    })()`);
    assert.equal(closed.display, 'none');
    assert.equal(closed.hostHTML, '');
    assert.equal(closed.iframes, 0, 'no iframe survives the panel close');
  }
});

test('CL-UI-119 (H2b): tw-001 大屯山 — 陽明山國家公園管理處 per-entry attribution renders', async () => {
  await bootBrowser();
  {
    await loadPage();
    const openRes = await evaljs(`(() => {
      const live=[...document.querySelectorAll('.card [data-live-btn]')]
        .find(b=>b.getAttribute('data-live-place')==='tw-001');
      if(!live)return {error:'no tw-001 live button'};
      live.click();
      const ov=document.getElementById('live-modal-overlay');
      const frame=document.querySelector('#live-frame-host iframe.live-frame');
      return {
        visible: ov && ov.style.display==='flex',
        src: frame?frame.getAttribute('src'):null,
        label: document.getElementById('live-source-label').textContent
      };
    })()`);
    assert.equal(openRes.visible, true, 'tw-001 panel opens in-app');
    assert.match(openRes.src, /www\.youtube\.com\/embed\/6ghffcNt3Nw/, 'YMSNP official YouTube embed');
    assert.equal(openRes.label, '影像來源：陽明山國家公園管理處',
      'per-entry attribution shows the 陽明山 agency, not 北觀處');
    await evaljs(`closeLiveModal();`);
  }
});

test('CL-UI-120 (H2c): tw-002 象山 — 臺北市政府觀光傳播局 per-entry attribution renders', async () => {
  await bootBrowser();
  {
    await loadPage();
    const openRes = await evaljs(`(() => {
      const live=[...document.querySelectorAll('.card [data-live-btn]')]
        .find(b=>b.getAttribute('data-live-place')==='tw-002');
      if(!live)return {error:'no tw-002 live button'};
      live.click();
      const ov=document.getElementById('live-modal-overlay');
      const frame=document.querySelector('#live-frame-host iframe.live-frame');
      return {
        visible: ov && ov.style.display==='flex',
        src: frame?frame.getAttribute('src'):null,
        label: document.getElementById('live-source-label').textContent
      };
    })()`);
    assert.equal(openRes.visible, true, 'tw-002 panel opens in-app');
    assert.match(openRes.src, /www\.youtube\.com\/embed\/z_fY1pj1VBw/, 'Taipei City DoIT official YouTube embed');
    assert.equal(openRes.label, '影像來源：臺北市政府觀光傳播局',
      'per-entry attribution shows the Taipei City DoIT agency, not 北觀處');
    await evaljs(`closeLiveModal();`);
  }
});

test('CL-UI-111 (H3): subject panel 「拍攝位置」 entry opens the same live panel; mobile 390 row keeps 44px targets', async () => {
  await bootBrowser();
  {
    await loadPage();
    // Open the subject panel for a cam place (tw-074) via the 題材 button.
    const panel = await evaljs(`(() => {
      const card=[...document.querySelectorAll('.card')]
        .find(c=>((c.querySelector('.spot-name')||{}).textContent||'').includes('野柳'));
      if(!card)return {error:'no 野柳 card'};
      const btn=card.querySelector('[data-weather]');
      if(!btn)return {error:'no 題材 button'};
      btn.click();
      const ov=document.getElementById('place-modal-overlay');
      return {open:ov&&ov.style.display==='flex'};
    })()`);
    assert.equal(panel.open, true);
    const entry = await evaljs(`new Promise((resolve,reject)=>{
      const t0=Date.now();
      const iv=setInterval(()=>{
        const body=document.getElementById('place-modal-body');
        const e=body&&body.querySelector('.opportunity-meta .live-thumb-entry');
        if(e){clearInterval(iv);resolve({found:true});}
        else if(Date.now()-t0>15000){clearInterval(iv);resolve({found:false,metas:body?body.querySelectorAll('.opportunity-meta').length:-1});}
      },100);
    })`);
    assert.equal(entry.found, true, 'live thumbnail entry sits in the 拍攝位置 meta area');
    const opened = await evaljs(`(() => {
      const e=document.querySelector('#place-modal-body .opportunity-meta .live-thumb-entry');
      e.click();
      const ov=document.getElementById('live-modal-overlay');
      const frame=document.querySelector('#live-frame-host iframe.live-frame');
      return {visible:ov&&ov.style.display==='flex',
        src:frame?frame.getAttribute('src'):null};
    })()`);
    assert.equal(opened.visible, true, 'panel entry opens the SAME live panel');
    assert.match(opened.src, /www\.youtube\.com\/embed\/ZjuY4qKaj40/);
    await evaljs(`closeLiveModal();closePlaceModal();`);
    // Mobile: the LIVE button keeps the 44px icon-only touch target of the row.
    await loadPage(390, 844, true);
    const mobile = await evaljs(`new Promise((resolve,reject)=>{
      const t0=Date.now();
      const iv=setInterval(()=>{
        const live=document.querySelector('.card [data-live-btn]');
        if(live){clearInterval(iv);
          live.closest('.card').scrollIntoView({block:'center'});
          const r=live.getBoundingClientRect();
          resolve({w:Math.round(r.width),h:Math.round(r.height),name:(live.closest('.card').querySelector('.spot-name')||{}).textContent});
        } else if(Date.now()-t0>20000){clearInterval(iv);resolve({error:'no live button at 390'});}
      },100);
    })`);
    assert.ok(mobile.w >= 44 && mobile.h >= 44, `390px LIVE button stays a 44px touch target (${mobile.w}x${mobile.h})`);
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    const { writeFileSync } = await import('node:fs');
    writeFileSync(join(WEB, 'apps', 'web-v2', 'audits', 'design-mockups', 'clui111-live-cards-390.png'), Buffer.from(shot.data, 'base64'));
  }
});
