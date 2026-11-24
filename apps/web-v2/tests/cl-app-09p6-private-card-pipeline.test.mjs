// CL-APP-09 patch-6: private points ride the OFFICIAL card renderer and the
// OFFICIAL filter pipeline — one truth for chip counts, tier filters and card
// verdicts (owner实测 bug: a ✗-private card appeared under the ✓推薦 filter
// because private cards bypassed the tier pipeline entirely).
//   (1) source contract: createSpotCard(spot,metric,opts) private bridge,
//       registerSyntheticRows(days) synthetic bundle places, cardRows() merge
//       in filterAndRender, cp-data re-render event, no bare-coordinates
//       subtitle, no compact ✗+雨 homegrown row.
//   (2) headless behavior (lazy-boot raw-CDP, NO root test.before): stubbed
//       /api/v1/custom_places fixture drives — ✓ private counts INTO the
//       ✓推薦 tab, ✗ private does not; tier filter excludes ✗ private; 私人
//       view shows private only; card anatomy = official (subject row +
//       pills + 三鈕, no coordinate subtitle); chip count === filtered cards
//       (same-source assertion); 390 side-by-side screenshot.
// Run: node --test apps/web-v2/tests/cl-app-09p6-private-card-pipeline.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { mkdtempSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const htmlSource = readFileSync(join(WEB, 'index.html'), 'utf8');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const cpSource = readFileSync(join(WEB, 'assets', 'custom-places.js'), 'utf8');

// ------------------------------------------------------------ (1) source
test('CL-APP-09p6 (1a): app.js — the official renderer + pipeline accept private rows', () => {
  // createSpotCard grows the private bridge (badge/openers), not a fork
  assert.match(appSource, /function createSpotCard\(spot,metric,opts\)/);
  assert.match(appSource, /const cp=!!\(opts&&opts\.private\)/);
  assert.match(appSource, /cpOpenCard=\(opts&&opts\.openCard\)\|\|openWeatherModal/);
  assert.match(appSource, /cpOpenPlace=\(opts&&opts\.openPlace\)\|\|openPlaceModal/);
  // official anatomy by construction; the ONLY private additions are the
  // ◉私人 badge and the interaction targets
  assert.match(appSource, /cp\?\(\(opts&&opts\.badgeHtml\)\|\|''\):''/);
  assert.match(appSource, /card\.dataset\.placeId=cp\?'':\(spot\.spot_id\|\|''\)/);
  // synthetic bundle places: ONE verdict pipeline for card + counts + filters
  assert.match(appSource, /let v2SyntheticPlaces=\{\}/);
  assert.match(appSource, /registerSyntheticRows:function\(placeId,tree,genreNames,days\)/);
  assert.match(appSource, /v2SyntheticPlaces\[placeId\]=\{place_id:placeId,opportunities:/);
  assert.match(appSource, /return \(v2SyntheticPlaces&&v2SyntheticPlaces\[spot\.spot_id\]\)\|\|null/);
  assert.match(appSource, /createCard:function\(spot,metric,opts\)\{return createSpotCard\(spot,metric,opts\);\}/);
  // filterAndRender merges private rows BEFORE the tier tabs/filters run
  assert.match(appSource, /window\.ChaseLightsCustomPlaces\.cardRows/);
  assert.match(appSource, /if\(cpView==='official'\)cpRows=\[\];/);
  assert.match(appSource, /if\(cpView==='private'\)rowsAll\.length=0;/);
  assert.match(appSource, /rowsAll\.push\(\.\.\.cpRows\)/);
  // data-version coupling: private data changes re-run the SAME pass
  assert.match(appSource, /chaselights:cp-data/);
  // the card's private subject rows keep the custom-condition reminder bell
  assert.match(appSource, /cc:s\.cc\|\|null/);
  // CL-UI-121: the private-view filter pass must never wipe the list before the
  // data guard, and a completed render must retire the first-load splash — the
  // owner saw 「正在獲取攝影氣象數據...」 sitting on top of a rendered list.
  assert.ok(appSource.indexOf("if(!currentData)return;") < appSource.indexOf("container.innerHTML='';"),
    'the currentData guard runs before the container wipe');
  assert.match(appSource, /if\(clui121Loading&&clui121Loading\.style\.display!=='none'\)clui121Loading\.style\.display='none';/);
  // cache-bust: this ticket's stamps
  assert.match(htmlSource, /assets\/app\.js\?v=clui123/); // CL-UI-110/111 stamp advance (CL-INT-212 re-anchor)
});

test('CL-APP-09p6 (1b): custom-places.js — cards render via the bridge; patch-9 coord line rides the card, homegrown ✗ row stays retired', () => {
  assert.match(cpSource, /CLForecastRenderers\.createCard/);
  assert.match(cpSource, /cardRows/);
  assert.match(cpSource, /chaselights:cp-data/);
  // the homegrown compact card row (✗ + 雨 on its own mini anatomy) is retired
  assert.doesNotMatch(cpSource, /function cpCardRow\(/);
  // CL-CI-38 re-anchor: the patch-9 coord meta line (coords @3dp · elevation
  // · GMT±n) rides the CARD face via postMount (same anatomy the cl-app-06
  // (2b) pin requires); the popup header keeps the patch-3 cpMetaLine.
  assert.match(cpSource, /cl-cp-coord/);
  assert.equal((cpSource.match(/cpMetaLine\(/g) || []).length, 2, 'cpMetaLine survives only as the popup meta line (def + call)');
  // trial-expired / pending special states keep their honest dedicated cards
  // (no verdict exists → they ride the 全部 tab only)
  assert.match(cpSource, /function isSpecialCard/);
  assert.match(cpSource, /cpActiveTier/);
  // stamps
  assert.match(htmlSource, /assets\/custom-places\.js\?v=clapp09j/);
  assert.match(htmlSource, /assets\/custom-places\.css\?v=clapp09f/);
});

// --------------------------------------------------- (2) headless behavior
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');

let server, baseURL, chrome, ws, send, evaljs, ready;
let loadEvents = 0;
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
      '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clapp09p6-')), 'about:blank'],
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
    await send('Page.enable');
    await send('Page.addScriptToEvaluateOnNewDocument', { source: `
      // fixture: TWO private points — cpA has a ✓ subject (counts into ✓推薦),
      // cpB's single subject is ✗雨 (the owner's 「公司」card case: must never
      // appear under the ✓推薦 filter or its count).
      window.__clcpPlaces = [
        { id: 'cpa', name: '上班大樓天台', lat: 25.068, lng: 121.579, elevation: 13, timezone: 'Asia/Taipei',
          customConditions: null, status: 'active', createdAt: '', updatedAt: '', fetchDeferred: false,
          themeGroups: [ { id: 'tg-a', placeId: 'cpa', name: '城市景觀', nameI18n: { 'zh-TW': '城市景觀' },
            conditions: { cloud_low_max: 20 },
            evaluation: { tier: 'rec', reason: null, window: new Date(Date.now() + 8 * 3600e3 + 2 * 3600e3).toISOString().slice(0, 10) + ' 21:30' } } ],
          evaluation: { tier: 'rec', reason: null, window: new Date(Date.now() + 8 * 3600e3 + 2 * 3600e3).toISOString().slice(0, 10) + ' 21:30' } },
        { id: 'cpb', name: '公司', lat: 25.03, lng: 121.56, elevation: 9, timezone: 'Asia/Taipei',
          customConditions: null, status: 'active', createdAt: '', updatedAt: '', fetchDeferred: false,
          themeGroups: [ { id: 'tg-b', placeId: 'cpb', name: '城市景觀', nameI18n: { 'zh-TW': '城市景觀' },
            conditions: { cloud_low_max: 20 },
            evaluation: { tier: 'no', reason: '雨', window: null } } ],
          evaluation: { tier: 'no', reason: '雨', window: null } },
      ];
      window.__clcpFetch = function (path) {
        if (path === '/api/v1/custom_places') {
          return Promise.resolve({ ok: true, status: 200, json: function () {
            return Promise.resolve({ ok: true, userId: 'u1', level: 'paid',
              quota: { used: 2, cap: 50 }, degraded: false, degradedMessage: null,
              places: window.__clcpPlaces });
          } });
        }
        if (/\\/api\\/v1\\/custom_places\\/[^/]+\\/eval$/.test(path)) {
          return Promise.resolve({ ok: true, status: 200, json: function () {
            return Promise.resolve({ ok: false, status: 404 });
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
    (async () => { try { chrome?.kill(); } catch {} })(),
    (async () => { try { await new Promise(r => server?.close(r)); } catch {} })(),
  ]);
}

async function setViewport(width, height, mobile) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile });
}

async function loadPage() {
  const before = loadEvents;
  await send('Page.navigate', { url: baseURL });
  await new Promise((resolve, reject) => {
    const t0 = Date.now();
    const iv = setInterval(() => {
      if (loadEvents > before) { clearInterval(iv); resolve(true); }
      else if (Date.now() - t0 > 20000) { clearInterval(iv); reject(new Error('navigation never fired load')); }
    }, 100);
  });
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      if(document.querySelector('.card')){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>25000){clearInterval(iv);reject(new Error('official cards never rendered'));}
    },100);
  })`);
  // CL-INT-190: re-dispatch every tick — a broadcast lost to a navigation race
  // must not hang the harness; chaselights:auth is REPLACE-semantics/idempotent.
  await evaljs(`new Promise((resolve,reject)=>{
    const t0=Date.now();
    const iv=setInterval(()=>{
      document.dispatchEvent(new CustomEvent('chaselights:auth', { detail: { member: { id: 'u1', displayName: '晨曦旅人', level: 'paid' } } }));
      if(document.querySelectorAll('.cl-cp-card').length>=1){clearInterval(iv);resolve(true);}
      else if(Date.now()-t0>15000){clearInterval(iv);reject(new Error('private cards never rendered'));}
    },300);
  })`);
  await new Promise(r => setTimeout(r, 400));
}

const tierCount = key => `Number((document.querySelector('.tier-tab[data-tier="${key}"] .tier-tab-count')||{textContent:'-1'}).textContent)`;

test('CL-APP-09p6 (2a): ✓ private counts INTO ✓推薦; ✗ private never does (same pass, same data version)', async () => {
  await bootBrowser();
  await setViewport(1280, 900, false);
  await loadPage();
  const probe = await evaljs(`(() => {
    const recBefore = Number(document.querySelector('.tier-tab[data-tier="recommend"] .tier-tab-count').textContent);
    // logout view: officials only
    document.dispatchEvent(new CustomEvent('chaselights:auth', { detail: {} }));
    return new Promise(res => setTimeout(() => {
      const recOfficial = Number(document.querySelector('.tier-tab[data-tier="recommend"] .tier-tab-count').textContent);
      res({ recBefore, recOfficial, diff: recBefore - recOfficial });
    }, 600));
  })()`);
  assert.equal(probe.diff, 1, '✓推薦 count grows by EXACTLY the one ✓ private point (cpa), not the ✗ one (cpb)');
  // back to signed-in
  await evaljs(`document.dispatchEvent(new CustomEvent('chaselights:auth', { detail: { member: { id: 'u1', displayName: '晨曦旅人', level: 'paid' } } })), new Promise(r => setTimeout(r, 600))`);
});

test('CL-APP-09p6 (2b): tier filter and the chip count share ONE source — ✗ private is filtered out of ✓推薦', async () => {
  await loadPage();
  const probe = await evaljs(`(() => {
    const cards = [...document.querySelectorAll('#spots-container .cl-cp-card')];
    const names = cards.map(c => c.querySelector('.cl-cp-card-name,.spot-name')?.textContent || '');
    const rec = Number(document.querySelector('.tier-tab[data-tier="recommend"] .tier-tab-count').textContent);
    // same-source assertion: the number of private cards that PASSED the
    // recommend tier filter equals the count the tab advertises minus officials
    const officials = document.querySelectorAll('#spots-container .card:not(.cl-cp-card)').length;
    return { names, rec, officials, privateVisible: cards.length };
  })()`);
  // default tab is ✓推薦: only cpa (✓) shows; cpb (✗雨) is gone
  assert.ok(probe.names.some(n => /上班大樓天台/.test(n)), '✓ private card renders under ✓推薦');
  assert.ok(!probe.names.some(n => /公司/.test(n)), '✗雨 private card NEVER renders under ✓推薦 (owner bug fixed)');
  assert.equal(probe.rec, probe.officials + probe.privateVisible, 'chip count and filtered cards agree (one source)');
});

test('CL-APP-09p6 (2c): 私人 view shows private cards only, filtered by the SAME tier; ✗ private appears under ✗不宜', async () => {
  await loadPage();
  await evaljs(`(function(){var b=document.querySelector('.cl-cp-view-tab[data-cp-view="private"]');b.click();})()`);
  await new Promise(r => setTimeout(r, 600));
  const probe = await evaljs(`(() => {
    const visible=[...document.querySelectorAll('#spots-container .card')].filter(c=>c.offsetParent!==null||getComputedStyle(c).display!=='none');
    const names=visible.map(c=>c.querySelector('.cl-cp-card-name,.spot-name')?.textContent||'');
    return { names, officials: visible.filter(c=>!c.classList.contains('cl-cp-card')).length };
  })()`);
  assert.equal(probe.officials, 0, '私人 view renders no official cards');
  assert.equal(await evaljs(`document.getElementById('loading').style.display`), 'none',
    'CL-UI-121: the first-load splash is retired after the private render pass');
  assert.ok(probe.names.some(n => /上班大樓天台|公司/.test(n)), 'private cards render in the 私人 view');
  // switch tier to ✗不宜 → only cpb (公司) remains
  await evaljs(`(function(){var b=document.querySelector('.tier-tab[data-tier="not_recommended"]');b.click();})()`);
  await new Promise(r => setTimeout(r, 600));
  const probe2 = await evaljs(`(() => {
    const visible=[...document.querySelectorAll('#spots-container .card')].filter(c=>c.offsetParent!==null||getComputedStyle(c).display!=='none');
    const names=visible.map(c=>c.querySelector('.cl-cp-card-name,.spot-name')?.textContent||'');
    return { names };
  })()`);
  assert.ok(probe2.names.some(n => /公司/.test(n)), '✗ private card shows under ✗不宜');
  assert.ok(!probe2.names.some(n => /上班大樓天台/.test(n)), '✓ private card not under ✗不宜');
  await evaljs(`(function(){var b=document.querySelector('.cl-cp-view-tab[data-cp-view="all"]');b.click();})()`);
});

test('CL-UI-122 (2f): a ✗-only private point still renders in the 私人 view (owner: 「私人 1」 but no card)', async () => {
  await loadPage();
  // keep ONLY the ✗ private point (公司): the active ✓推薦 tier holds no
  // private place at all, so the private view must fall back to 全部 and the
  // deferred group must render EXPANDED — otherwise the owner sees a count
  // with an empty list.
  await evaljs(`(function(){ window.__clcpPlacesAll = window.__clcpPlaces.slice(); window.__clcpPlaces = window.__clcpPlaces.filter(p=>p.id==='cpb'); if(window.ChaseLightsCustomPlaces) window.ChaseLightsCustomPlaces.refresh(); })()`);
  await new Promise(r => setTimeout(r, 800));
  await evaljs(`(function(){var b=document.querySelector('.cl-cp-view-tab[data-cp-view="private"]');b.click();})()`);
  await new Promise(r => setTimeout(r, 800));
  const probe = await evaljs(`(() => {
    const c=document.getElementById('spots-container');
    const visible=[...c.querySelectorAll('.card')].filter(x=>x.offsetParent!==null||getComputedStyle(x).display!=='none');
    const open=[...c.querySelectorAll('details')].map(d=>d.open);
    const details=c.querySelectorAll('details').length;
    return { view: document.body.getAttribute('data-cp-view'),
      activeTier: (document.querySelector('.tier-tab.active')||{}).getAttribute('data-tier'),
      visible: visible.length, names: visible.map(x=>x.querySelector('.cl-cp-card-name,.spot-name')?.textContent||''),
      open, details, empty: !!c.querySelector('.empty-state') };
  })()`);
  assert.equal(probe.view, 'private');
  assert.equal(probe.activeTier, 'all', 'CL-UI-122: the 私人 view falls back to the 全部 tier when the active tier has no private point');
  assert.ok(probe.visible >= 1, 'the ✗ private card is rendered and visible in the 私人 view');
  assert.ok(probe.names.some(n => /公司/.test(n)), 'the ✗ private card is the one rendered');
  assert.ok(!probe.empty, 'no empty-state placeholder for a private view that has a private point');
  // CL-UI-122: the 私人 view's CSS hides every direct child that is not a
  // .cl-cp-card, so the private rows must render FLAT (no <details> wrapper).
  assert.equal(probe.details, 0, 'CL-UI-122: private rows render flat in the 私人 view (no hidden <details> wrapper)');
  assert.ok(probe.visible >= 1, 'CL-UI-122: the private card is actually visible in the 私人 view');
  // restore the fixture for the tests that follow (same browser page)
  await evaljs(`(function(){ window.__clcpPlaces = window.__clcpPlacesAll; window.__clcpPlacesAll = null; if(window.ChaseLightsCustomPlaces) window.ChaseLightsCustomPlaces.refresh(); var b=document.querySelector('.cl-cp-view-tab[data-cp-view="all"]'); if(b) b.click(); })()`);
  await new Promise(r => setTimeout(r, 500));
});

test('CL-APP-09p6 (2d): the private card carries the OFFICIAL anatomy — patch-9 coord line + per-group tier rows', async () => {
  await loadPage();
  // the ✗ card only exists under the 全部 tier tab (that is the fix working)
  await evaljs(`(function(){document.querySelector('.tier-tab[data-tier="all"]').click();})()`);
  await new Promise(r => setTimeout(r, 600));
  const probe = await evaljs(`(() => {
    const find=n=>[...document.querySelectorAll('#spots-container .cl-cp-card')].find(c=>(c.textContent||'').includes(n));
    const a=find('上班大樓天台'), b=find('公司');
    const grab=card=>card?{
      head:!!card.querySelector('.card-header'),
      badge:!!card.querySelector('.cl-cp-priv-badge'),
      tier:(card.querySelector('.tier')?.textContent||'').trim(),
      row:!!card.querySelector('.cl-subject-row'),
      rowText:(card.querySelector('.cl-subject-row')?.textContent||'').trim(),
      rowBell:!!card.querySelector('.cl-subject-row .cl-rem-btn'),
      pills:[...card.querySelectorAll('.card-metric-chips .metric-chip')].map(x=>x.textContent.trim()),
      tools:[...card.querySelectorAll('.card-footer-tools .tool-link')].map(x=>(x.textContent||'').trim()),
      coord:!!card.querySelector('.cl-cp-coord')||/25\\.0\\d\\d,\\s*121/.test(card.textContent),
      noCompactTierRow:!card.querySelector('.cl-cp-tier'),
    }:{};
    return { a:grab(a), b:grab(b) };
  })()`);
  assert.ok(probe.a.head && probe.a.badge, 'official card head + ◉私人 badge');
  assert.match(probe.a.tier, /✓/, 'tier badge reads the SAME synthetic row truth');
  assert.ok(probe.a.row && probe.a.rowBell, 'official subject-row anatomy (短名 + window + 🔔)');
  assert.ok(probe.a.rowText.includes('城市景觀'), 'subject short name rides the row');
  assert.ok(probe.a.pills.some(p => /13 m/.test(p)), 'elevation pill like official cards');
  assert.equal(probe.a.tools.length, 3, 'three tool buttons (題材/地圖/天氣圖)');
  // CL-CI-38 re-anchor: the patch-9 coord meta line (coords @3dp · elevation
  // · GMT±n) rides the card face — same anatomy the cl-app-06 (2b) pin
  // requires for private cards.
  assert.ok(probe.a.coord, 'patch-9 coord meta line rides the card face');
  // CL-CI-38 re-anchor: the per-group tier row badge (.cl-cp-tier inside the
  // official subject row) is the patch-8 owner-ruled anatomy — the RETIRED
  // thing was the standalone header chip (.spot-title-group .cl-cp-tier).
  const tierInRow = await evaljs(`(() => {
    const find=n=>[...document.querySelectorAll('#spots-container .cl-cp-card')].find(c=>(c.textContent||'').includes(n));
    const a=find('上班大樓天台');
    if (!a) return { err: 'no card' };
    const row = a.querySelector('.cl-subject-row');
    return { inRow: !!(row && row.querySelector('.cl-cp-tier')),
      inHead: !!a.querySelector('.spot-title-group .cl-cp-tier') };
  })()`);
  assert.equal(tierInRow.inRow, true, 'per-group tier badge rides the subject ROW (patch-8)');
  assert.equal(tierInRow.inHead, false, 'no standalone header chip (the retired compact row stays retired)');
  assert.match(probe.b.tier, /✗/, '✗ private card badge = official ✗');
  assert.ok(/雨/.test(probe.b.rowText || (probe.b.rowText || '')), '✗ verdict + short reason live in the official verdict row');
  assert.ok(probe.b.coord, 'patch-9 coord meta line rides the ✗ card face too');
});

test('CL-APP-09p6 (2e): 390 side-by-side screenshot — official vs private card anatomy parity', async () => {
  await loadPage();
  await setViewport(390, 844, true);
  await new Promise(r => setTimeout(r, 300));
  const out = await evaljs(`(() => {
    const priv=document.querySelector('#spots-container .cl-cp-card');
    const off=document.querySelector('#spots-container .card:not(.cl-cp-card)');
    if(off&&priv){off.scrollIntoView({block:'start'});window.scrollBy(0,-40);priv.scrollIntoView({block:'start'});}
    return { off:!!off, priv:!!priv, y:window.scrollY };
  })()`);
  assert.ok(out.off && out.priv, 'an official card and the private card both exist on the page');
  await new Promise(r => setTimeout(r, 300));
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  const dir = 'D:/ChaseLightsWorkspace/screenshots';
  try { mkdirSync(dir, { recursive: true }); } catch {}
  const path = dir + '/clapp09p6-official-vs-private-390.png';
  writeFileSync(path, Buffer.from(shot.data, 'base64'));
  const probe = await evaljs(`(() => {
    const priv=document.querySelector('#spots-container .cl-cp-card');
    const off=document.querySelector('#spots-container .card:not(.cl-cp-card)');
    const sig=card=>card?{header:!!card.querySelector('.card-header'),rows:card.querySelectorAll('.cl-subject-row').length,tools:card.querySelectorAll('.card-footer-tools .tool-link').length}:{};
    return { off:sig(off), priv:sig(priv) };
  })()`);
  assert.equal(probe.priv.header, probe.off.header, 'both cards share the official header anatomy');
  assert.ok(probe.priv.tools >= 2, 'private card carries the official tool-button row');
});

test.after(() => teardownBrowser());
