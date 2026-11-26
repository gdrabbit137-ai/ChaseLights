// CL-UI-45 — rendering consistency, the date-switch freeze, the counts.
//
// Contract this file guards (owner 語意鐵律: 上下兩處不得出現不同等級判定):
//  (1) ONE normalized verdict source. The card window, the 7-day summary and
//      the hourly rows all read the evaluation bundle's day row (good_hours,
//      remaining-hours filtered). The derived subject-cards hour buckets may
//      only NAME a subject inside that set — an hour outside it renders a
//      neutral 「本日建議時段外」 (v2DayQualifiedSet + the gate in
//      v2HourSubjectCell / v2BandHtml / the modal's wmGateOf).
//      tw-188-P02 2026-11-29 used to paint a green ✓ at 16:00 while the card's
//      window was 16:30–17:00.
//  (2) The modal/card show the cloud base as a height ABOVE SEA LEVEL
//      (cloud_base_asl); the 60 m AGL floor is gone from fetch_data.py and no
//      surface renders cloud_base_agl.
//  (3) The date switch is cheap (cached Intl + per-pass memo) and a card click
//      may never open a DIFFERENT place's forecast: the click is bound to the
//      card's place_id and ignored during a transition.
//  (4) Every count on the page comes from one render publish; a region switch
//      clears the list and paints a skeleton.
//  (5) No engineering jargon (AOD / seasonal-calendar / bare unit-less 現況
//      numbers) reaches a photographer.
//  (6) A 日出/日落 subject row always carries a readable HH:MM–HH:MM window, or
//      the row is not rendered at all.
// Run: node --test apps/web-v2/tests/cl-ui-45-render-consistency.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync, mkdtempSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const cssSource = readFileSync(join(WEB, 'assets', 'app.css'), 'utf8');
const cpSource = readFileSync(join(WEB, 'assets', 'custom-places.js'), 'utf8');
const fetchSource = readFileSync(join(WEB, 'fetch_data.py'), 'utf8');
const indexSource = readFileSync(join(WEB, 'index.html'), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  const j = appSource.indexOf(end, i);
  assert.ok(j > i, 'source slice end not found: ' + end);
  return appSource.slice(i, j);
};

// ---------------------------------------------------------------- (1) verdict
test('CL-UI-45 (1a): one normalized day-hour source, and the winner is stated', () => {
  const helper = grab('function v2DayQualifiedSet', '// CL-UI-13:');
  assert.match(helper, /function v2DayQualifiedSet\(opp,localDate,tz\)\{/,
    'the single normalized set is exposed as one pure helper');
  assert.match(helper, /return new Set\(v2EffectiveHours\(day,tz\)\);/,
    'the bundle day row (good_hours, remaining-hours filtered) is the source');
  // The resolution rule must be documented where the rule lives: which layer
  // wins, and why, so a future edit cannot re-split the surfaces.
  assert.match(appSource, /語意鐵律/);
  assert.match(appSource, /the bundle day row WINS/);
  assert.match(appSource, /RESOLUTION \(one rule, all three surfaces\)/);
});

test('CL-UI-45 (1b): the hourly cell can never paint a positive verdict outside the day', () => {
  const cell = grab('function v2HourSubjectCell', '// CL-UI-26:');
  assert.match(cell, /function v2HourSubjectCell\(spot,item,qualified\)/,
    'the winning hour set is an argument — no surface may derive its own');
  assert.match(cell, /const gated=!!\(qualified&&qualified\.size!==undefined&&!qualified\.has\(hh\)&&!naList\.includes\(hh\)&&!saysFail\);/,
    'the gate covers every hour the artifact would call positive, while the 時段外/✗ buckets keep their own words');
  assert.match(cell, /if\(gated\)return \{cls:'subj-gated-row'/,
    'a gated hour returns the neutral cell BEFORE any ✓ chip / ○ pill');
  const gatedAt = cell.indexOf('if(gated)return');
  const fitAt = cell.indexOf("const fit=(hours.fit&&hours.fit[hh])||[];");
  assert.ok(gatedAt > 0 && fitAt > gatedAt, 'the gate runs before the subject chips are read');
});

test('CL-UI-45 (1c): every hourly surface feeds that gate (table, group count, band)', () => {
  const modal = grab('function renderWeatherModal', 'function closeModal');
  assert.match(modal, /const wmGateOf=date=>\{/,
    'one per-date gate resolver for the modal');
  assert.match(modal, /const g=v2DayQualifiedSet\(v2WmOpp,date,summarySpot\?\.timezone\);/);
  assert.match(modal, /v2HourSubjectCell\(spot,item,gate\)/, 'the day-group ✓/○ counts use the gate');
  assert.match(modal, /v2HourSubjectCell\(spot,item,wmGateOf\(wmDate\)\)/, 'the hourly rows use the gate');
  const band = grab('function v2BandHtml', '// CL-UI-95');
  assert.match(band, /v2HourSubjectCell\(spot,item,bestSet\)/, 'the 24h band uses the same gate');
});

test('CL-UI-45 (1d): the gate changes the real verdict — tw-188-P02 2026-11-29 16:00', () => {
  // Real shapes from the shipped artifacts: good_hours ['16:30','17:00'] while
  // the subject-cards layer marks 06:00–16:00 suitable for the landform
  // subject. Before CL-UI-45 every one of those hours painted a green ✓ chip
  // outside the card's window.
  const cell = grab('function v2HourSubjectCell', '// CL-UI-26:');
  const lookup = grab('function v2SubjectCardRow', '// CL-UI-63: dedup short subject names');
  const prelude = `
    let currentLang='zh-TW';
    const i18nDict={'zh-TW':{eval2_unk:'資料不足',v2_hour_general_ok:'可拍',state_outside:'非建議時段',clui45_day_gated:'本日建議時段外'}};
    const d=()=>i18nDict[currentLang];
    const esc=s=>String(s);
    const listSep=()=>'、';
    const v2SubjectCards={
      places:{'tw-188':{'2026-11-29':{hours:{fit:{'06:00':['geological_landform'],'15:00':['geological_landform'],'16:00':['geological_landform','sunset'],'16:30':['sunset'],'17:00':['sunset']}}}}},
      dictionaries:{genre_short_names:{geological_landform:{'zh-TW':'地景'},sunset:{'zh-TW':'夕陽'}},fail_reason_short:{}}
    };
  `;
  const api = new Function(prelude + lookup + cell + 'return {v2HourSubjectCell,v2SubjectCardRow};')();
  const spot = {spot_id: 'tw-188'};
  const at = hh => ({time: '2026-11-29 ' + hh, local_date: '2026-11-29'});
  const gate = new Set(['16:30', '17:00']);
  assert.equal(api.v2HourSubjectCell(spot, at('16:00')).kind, 'fit', 'ungated the artifact still says "suitable"');
  const gated = api.v2HourSubjectCell(spot, at('16:00'), gate);
  assert.equal(gated.kind, 'gated', 'inside the day gate the 16:00 chip is withdrawn');
  assert.match(gated.html, /本日建議時段外/);
  assert.ok(!/subj-chip/.test(gated.html), 'no green ✓ chip outside the card window');
  const inside = api.v2HourSubjectCell(spot, at('16:30'), gate);
  assert.equal(inside.kind, 'fit', 'an hour inside the window keeps its subject chip');
  assert.match(inside.html, /夕陽/);
  const dayWithoutRow = api.v2HourSubjectCell({spot_id: 'tw-999'}, at('16:00'), null);
  assert.equal(dayWithoutRow.cls, 'subj-unknown', 'no artifact row → honest dash (fail-closed)');
  assert.match(dayWithoutRow.html, /—/);
});

// ------------------------------------------------------------- (2) cloud base
test('CL-UI-45 (2): the cloud base is the true ASL base; no surface renders AGL', () => {
  assert.ok(!/cloud_base_agl\?\?'—'/.test(appSource), 'the modal/mobile cells no longer print the AGL value');
  assert.match(grab('function renderWeatherModal', 'function closeModal'),
    /\$\{item\.cloud_base_asl\?\?'—'\} m/, 'hourly cells show the above-sea-level base');
  assert.match(appSource, /const clBase=metric\.cloud_base_asl!=null/,
    'the card chip prefers the ASL base (same datum as the ⛰ elevation pill)');
  assert.match(appSource, /th_cloud_base:'雲底高度（海拔）'/);
  assert.match(appSource, /th_cloud_base:'Cloud base \(ASL\)'/);
  assert.doesNotMatch(fetchSource, /cloud_base_agl = max\(60,/,
    'the 60 m AGL floor is gone from the generator');
  assert.match(fetchSource, /cloud_base_agl = max\(0,/);
});

// --------------------------------------------- (3) freeze + wrong-spot clicks
test('CL-UI-45 (3a): the per-call Intl.DateTimeFormat construction is cached', () => {
  const lds = grab('function localDateString', 'function selectedDateForSpot');
  assert.match(lds, /localDateString\._fmts/, 'formatter cache on the function (harness-safe)');
  assert.match(lds, /localDateString\._today=/, 'spot-local today cached per second bucket');
  assert.ok(!/new Intl\.DateTimeFormat\('en-CA',[^)]*\)\.formatToParts/.test(lds),
    'no formatter is constructed on the hot path any more');
  const lnow = grab('function localNowMinutes', '// CL-CI-44:');
  assert.match(lnow, /localNowMinutes\._fmts/);
});

test('CL-UI-45 (3b): a repeated per-place verdict lookup is memoized per render pass', () => {
  const best = grab('function v2BestForSpot', 'function v2PlaceForSpot');
  assert.match(best, /const epoch=\(typeof window!=='undefined'&&window\.__clV2Epoch\)\|\|0;/);
  assert.match(best, /const memo=v2BestForSpot\._m\|\|\(v2BestForSpot\._m=new WeakMap\(\)\);/);
  assert.match(best, /if\(hit&&hit\.epoch===epoch&&hit\.dayIndex===dayIndex&&hit\.tz===tz\)return hit\.best;/);
  assert.match(appSource, /window\.__clV2Epoch=\(window\.__clV2Epoch\|\|0\)\+1;/,
    'every render pass invalidates the memo');
});

test('CL-UI-45 (3c): card clicks are bound to place_id and locked during a transition', () => {
  const guards = grab('const CLUI45_TRANSITION_LOCK_MS', 'function clui45SkeletonHtml');
  assert.match(guards, /const CLUI45_TRANSITION_LOCK_MS=350;/);
  assert.match(guards, /if\(clui45TransitionLocked\(\)\)\{[\s\S]*?stopImmediatePropagation\(\)/,
    'a click that lands during the transition is DROPPED, never redirected to another spot');
  assert.match(guards, /pressed\.placeId!==card\.dataset\.placeId/,
    'a press/release split across a repaint is resolved against the pressed card');
  assert.match(appSource, /clui45InstallCardGuards\(\);/, 'installed at boot');
  assert.match(appSource, /function switchDay\(k\)\{closeDayPicker\(\);clui45LockTransitions\(\);/,
    'a date switch opens the lock window');
  assert.match(appSource, /if\(clui45RegionChanged\)clui45BeginRegionSwitch\(\);/);
});

// ----------------------------------------------------------------- (4) counts
test('CL-UI-45 (4a): one count publish feeds the source tabs, tiers and the day pill', () => {
  const pub = grab('function clui45PublishListStats', '// CL-UI-45 (defect 4)');
  assert.match(pub, /listed:list\.length,/);
  assert.match(pub, /official,/);
  assert.match(pub, /private:priv,/);
  assert.match(pub, /document\.dispatchEvent\(new CustomEvent\('chaselights:list-rendered'\)\)/);
  assert.match(appSource, /clui45PublishListStats\(tierRows,clui66TierCounts\(tierRows\)\);/,
    'published once per render pass, over the SAME filtered rows the list renders');
  // the day pill states the list length from that same publish
  assert.match(appSource, /const clListN=\(window\.CLListStats&&window\.CLListStats\.day===currentDayFilter/);
  assert.match(appSource, /d\(\)\.clui45_listed\.replace\('\{n\}',clListN\)/);
  // the 來源 tabs read the publish instead of counting DOM cards of the old region
  assert.match(cpSource, /window\.CLListStats/);
  assert.match(cpSource, /return stats\.loading \? 0 : stats\.official;/);
  assert.match(cpSource, /document\.addEventListener\('chaselights:list-rendered', function \(\) \{ syncCountLine\(\); \}\)/);
});

test('CL-UI-45 (4b): a region switch clears the list and paints a skeleton', () => {
  const begin = grab('function clui45BeginRegionSwitch', 'function updateFilterResultSummary');
  assert.match(begin, /container\.innerHTML=clui45SkeletonHtml\(6\);/);
  assert.match(begin, /currentData=null;currentSpots=\[\];/, 'the previous region\'s rows are dropped at once');
  assert.match(begin, /tabs\.innerHTML=''/, 'no stale tier counts survive the switch');
  assert.match(begin, /listed:0,[\s\S]*?loading:true/, 'the count publish says "loading", never the old number');
  assert.match(appSource, /container\.innerHTML=clui45SkeletonActive\?clui45SkeletonHtml\(6\):'';/,
    'loadData keeps the skeleton instead of wiping to a blank container');
  assert.match(cssSource, /\.card-skeleton \.sk-line \{[^}]*animation:clui45sk/);
  assert.match(cssSource, /@media \(prefers-reduced-motion: reduce\) \{ \.card-skeleton \.sk-line \{ animation:none; \} \}/);
});

// ----------------------------------------------------------------- (5) jargon
test('CL-UI-45 (5): no tracking jargon or bare unit-less numbers', () => {
  assert.ok(!appSource.includes("aod_550nm:'AOD 550nm'"), 'AOD 550nm is gone from the metric names');
  assert.ok(!appSource.includes('氣膠光學厚度'), 'AOD is named in plain language (zh)');
  assert.match(appSource, /aod_550nm:'空氣霧霾'/);
  assert.match(appSource, /aod_550nm:'Air haze'/);
  assert.match(appSource, /aod_550nm:'かすみ・霞'/);
  const live = grab('function v2CondLive', 'function v2CondDaySummary');
  // keep the CL-UI-36 contract (unit when the contract carries one)…
  assert.match(live, /cond\.unit\?' '\+cond\.unit:''/);
  // …and never print a naked number when it does not.
  assert.match(live, /const unitTxt=/);
  assert.match(live, /if\(!unitTxt\)return t\.v2_cond_now\+' '\+\(cond\.verdict==='PASS'\?t\.eval2_ok/);
  assert.match(appSource, /seasonal\[ _-\]calendar/, 'seasonal-calendar is scrubbed from rationale text');
  assert.ok(!appSource.includes("'CAMS AOD"), 'the provenance layer name is not an acronym wall');
});

// ------------------------------------------------------- (6) astro row windows
test('CL-UI-45 (6): a 日出/日落 row carries a range or is not rendered', () => {
  assert.match(appSource, /clui45NormalizeAstroEntries\(scEntries,scRow\);/,
    'the card normalizes astro rows before the render slices');
  const normalize = grab('const CLUI45_ASTRO_NAME_RE', 'function createSpotCard');
  assert.match(normalize, /const CLUI45_ASTRO_NAME_RE=\(\/\(日出\|日落\|sunrise\|sunset\|日の出\|日の入り\)\/i\)|const CLUI45_ASTRO_NAME_RE=/);
  assert.match(normalize, /e\.stamp=start\+'–'\+end;e\.window=\[\];continue;/,
    'a single qualifying hour is widened into ONE readable range segment');
  assert.match(normalize, /list\.splice\(i,1\);/, 'with no usable astronomy the row is dropped');
  // behaviour: one-hour sunrise widens from that day's civil dawn; without
  // astronomy the row disappears (never a bare 「日出 07:00」).
  const body = grab('function clui45NormalizeAstroEntries', 'function createSpotCard');
  const fn = new Function('const CLUI45_ASTRO_NAME_RE=/(日出|日落|sunrise|sunset|日の出|日の入り)/i;' + body + ';return clui45NormalizeAstroEntries;')();
  const widened = fn([{name: '日出', window: ['07:00'], stamp: null}], {civil_light: {dawn: '05:52', dusk: '17:40'}});
  assert.equal(widened.length, 1);
  assert.equal(widened[0].window.length, 0);
  assert.match(String(widened[0].stamp), /^\d{1,2}:\d{2}–\d{1,2}:\d{2}$/, 'stamp is a readable range');
  assert.ok(widened[0].stamp.startsWith('05:52–'), widened[0].stamp);
  const kept = fn([{name: '日出', window: ['05:55', '06:00', '07:00']}], {civil_light: {dawn: '05:52', dusk: '17:40'}});
  assert.equal(kept.length, 1);
  assert.equal(kept[0].stamp, undefined, 'a real multi-hour window keeps its own segment text');
  const dropped = fn([{name: '日出', window: ['07:00']}], null);
  assert.equal(dropped.length, 0, 'no window and no astronomy → no row at all');
  const sunset = fn([{name: '日落', window: ['17:00']}], {civil_light: {dawn: '05:52', dusk: '17:36'}});
  assert.equal(sunset.length, 1);
  assert.equal(sunset[0].stamp, '17:00–17:36');
});

// ------------------------------------------------------------ (7) cache stamps
test('CL-UI-45 (7): every touched asset is re-stamped on every page that serves it', () => {
  for (const page of ['index.html', 'genre-eval.html', 'sources.html', '404.html', 'reminders.html']) {
    const src = readFileSync(join(WEB, page), 'utf8');
    if (/app\.css\?v=/.test(src)) assert.match(src, /app\.css\?v=clui132/, `${page}: app.css stamp`);
  }
  assert.match(indexSource, /app\.js\?v=clui132/);
  assert.match(indexSource, /custom-places\.js\?v=clapp09n/);
});

// --------------------------------------------------------------- browser race
const BROWSER = process.env.CHROMIUM_EXECUTABLE || process.env.CHROME_PATH
  || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : '/usr/bin/chromium');
const FLAGS = (process.env.CL_CHROME_FLAGS || '--enable-unsafe-swiftshader --use-angle=swiftshader').split(' ').filter(Boolean);

let ready = null;
const nextId = (() => { let id = 0; return () => ++id; })();
const pending = new Map();
let ws = null, chrome = null, server = null, send = null, evaljs = null;
const sleep = ms => new Promise(r => setTimeout(r, ms));

// CL-UI-90: lazy boot — never a top-level test.before() (it poisons the full
// suite under --test-isolation=none).
function boot() {
  if (ready) return ready;
  ready = (async () => {
    const MIME = {'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml'};
    server = createServer((req, res) => {
      const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
      const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
      try { const body = readFileSync(file);
        res.writeHead(200, {'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
        res.end(body);
      } catch { res.writeHead(404); res.end('not found'); }
    });
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    const base = `http://127.0.0.1:${server.address().port}/`;
    chrome = spawn(BROWSER, ['--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
      '--no-first-run','--remote-debugging-port=0','--window-size=1280,1000',
      ...FLAGS, '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui45-')), 'about:blank'],
      {stdio:['ignore','ignore','pipe']});
    const wsUrl = await new Promise((resolve, reject) => {
      let buf = ''; const t = setTimeout(() => reject(new Error('no devtools endpoint')), 60000);
      chrome.stderr.on('data', d => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
        if (m) { clearTimeout(t); resolve(m[1]); } });
      chrome.on('error', reject);
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
    ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
    send = (method, params = {}) => new Promise((resolve, reject) => {
      const i = nextId(); pending.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
      ws.send(JSON.stringify({id: i, method, params}));
    });
    evaljs = async (expr) => {
      const r = await send('Runtime.evaluate', {expression: expr, returnByValue: true, awaitPromise: true});
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
      return r.result?.value;
    };
    await send('Page.enable'); await send('Runtime.enable');
    await send('Emulation.setDeviceMetricsOverride', {width: 1280, height: 1000, deviceScaleFactor: 1, mobile: false});
    return base;
  })().catch(e => { ready = null; throw e; });
  return ready;
}

test('CL-UI-45 (3d): rapid date switch + a click during the transition never opens another spot', async () => {
  const base = await boot();
  await send('Page.navigate', {url: base + '?region=tw&date=today&tier=all'});
  await evaljs(`new Promise((res,rej)=>{const t0=Date.now();const iv=setInterval(()=>{
    if(document.querySelectorAll('#spots-container .card').length>10){clearInterval(iv);res(1);}
    else if(Date.now()-t0>30000){clearInterval(iv);rej(new Error('cards never rendered'));}},100);})`);
  await sleep(800);

  // (a) the freeze is gone: 11 switches must stay well under a second each
  const timing = await evaljs(`(async () => {
    const seq=['tomorrow','after_tomorrow','day3','day4','day5','day6','today','tomorrow','day3','today','tomorrow'];
    const per=[]; const wall0=performance.now();
    for (const k of seq) {
      const t0=performance.now(); switchDay(k); per.push(Math.round(performance.now()-t0));
      await new Promise(r=>setTimeout(r,20));
    }
    switchDay('today');
    return {per, wall: Math.round(performance.now()-wall0)};
  })()`);
  assert.ok(Math.max(...timing.per) < 600,
    `one date switch must cost far less than the old ~1.9s (got ${JSON.stringify(timing.per)})`);
  assert.ok(timing.wall < 4000,
    `11 switches must not take ~22s of main-thread work (got ${timing.wall}ms)`);

  // (b) the race: switch the date, then deliver a real click at a card centre.
  //     The invariant that matters for a photographer: whatever modal opens must
  //     belong to the card that was under the pointer WHEN THE CLICK LANDED (or
  //     nothing opens at all — a click that raced the transition is dropped,
  //     never redirected to a different mountain). The page records the click
  //     target itself, so the oracle cannot be fooled by a repaint.
  const realClickAt = async (x, y) => {
    await send('Input.dispatchMouseEvent', {type: 'mousePressed', x, y, button: 'left', clickCount: 1});
    await send('Input.dispatchMouseEvent', {type: 'mouseReleased', x, y, button: 'left', clickCount: 1});
  };
  await evaljs(`(()=>{ if(!window.__cl45ClickTarget){ window.__cl45ClickTarget=null;
    document.getElementById('spots-container').addEventListener('click',function(e){
      const c=e.target.closest&&e.target.closest('.card');
      window.__cl45ClickTarget=c?(c.dataset.placeId||''):null;
    },true); } return 1; })()`);
  let wrong = 0, attempts = 0, opened = 0;
  for (let i = 0; i < 10; ++i) {
    await evaljs(`(()=>{switchDay('today');return 1;})()`);
    await sleep(500);
    const probe = await evaljs(`(()=>{const c=[...document.querySelectorAll('#spots-container .card')].find(x=>x.getBoundingClientRect().top>150);
      if(!c)return null;const r=c.getBoundingClientRect();
      return {x:Math.round(r.left+r.width/2), y:Math.round(r.top+Math.min(60,r.height/2)), id:c.dataset.placeId};})()`);
    if (!probe) continue;
    attempts++;
    await evaljs(`window.__cl45ClickTarget=null`);
    await send('Runtime.evaluate', {expression: `switchDay('day3')`});
    await realClickAt(probe.x, probe.y);
    await sleep(450);
    const got = await evaljs(`(()=>{const ov=document.getElementById('modal-overlay');
      const open=ov&&ov.style.display==='flex'; const id=ov?ov.dataset.placeId:'';
      const clicked=window.__cl45ClickTarget;
      if(open)closeModal(); return {open, id, clicked};})()`);
    if (got.open) opened++;
    if (got.open && got.id !== got.clicked) wrong++;
  }
  assert.ok(attempts >= 8, `race probe must run (attempts=${attempts})`);
  assert.equal(wrong, 0, `a click during the date transition opened ${wrong}/${attempts} modals for a spot that was NOT the click target`);

  // (b2) the exact user gesture that produced the wrong mountain: press the
  //      mouse on card A, the list repaints under the pointer, then release on
  //      whatever card is now there. Nothing may open (the press and the
  //      release disagree), and certainly not a third spot.
  let splitOpened = 0, splitWrong = 0;
  for (let i = 0; i < 4; ++i) {
    await evaljs(`(()=>{switchDay('today');return 1;})()`);
    await sleep(500);
    const p2 = await evaljs(`(()=>{const c=[...document.querySelectorAll('#spots-container .card')].find(x=>x.getBoundingClientRect().top>150);
      if(!c)return null;const r=c.getBoundingClientRect();
      return {x:Math.round(r.left+r.width/2), y:Math.round(r.top+Math.min(60,r.height/2)), id:c.dataset.placeId};})()`);
    if (!p2) continue;
    await evaljs(`window.__cl45ClickTarget=null`);
    await send('Input.dispatchMouseEvent', {type: 'mousePressed', x: p2.x, y: p2.y, button: 'left', clickCount: 1});
    await send('Runtime.evaluate', {expression: `switchDay('day4')`});
    await send('Input.dispatchMouseEvent', {type: 'mouseReleased', x: p2.x, y: p2.y, button: 'left', clickCount: 1});
    await sleep(450);
    const g2 = await evaljs(`(()=>{const ov=document.getElementById('modal-overlay');
      const open=ov&&ov.style.display==='flex'; const id=ov?ov.dataset.placeId:'';
      const clicked=window.__cl45ClickTarget;
      if(open)closeModal(); return {open, id, clicked};})()`);
    if (g2.open) splitOpened++;
    if (g2.open && g2.id !== p2.id && g2.id !== g2.clicked) splitWrong++;
  }
  assert.equal(splitWrong, 0, 'a press/release split across the repaint never opened an unrelated spot');
  assert.equal(splitOpened, 0, 'a press that raced the repaint opens nothing at all (the click is dropped)');

  // (c) positive control: without a transition, a real click opens exactly the
  //     card that was pressed — the lock must not make cards inert.
  await evaljs(`(()=>{switchDay('today');return 1;})()`);
  await sleep(900);
  const target = await evaljs(`(()=>{const c=[...document.querySelectorAll('#spots-container .card')].find(x=>x.getBoundingClientRect().top>150);
    if(!c)return null;const r=c.getBoundingClientRect();
    return {x:Math.round(r.left+r.width/2), y:Math.round(r.top+Math.min(60,r.height/2)), id:c.dataset.placeId};})()`);
  assert.ok(target && target.id, 'an idle card must be clickable');
  await realClickAt(target.x, target.y);
  await sleep(600);
  const after = await evaljs(`(()=>{const ov=document.getElementById('modal-overlay');
    const open=ov&&ov.style.display==='flex'; const id=ov?ov.dataset.placeId:'';
    if(open)closeModal(); return {open, id};})()`);
  assert.ok(after.open, 'an idle click still opens the forecast modal');
  assert.equal(after.id, target.id, 'the modal belongs to the pressed card');
});

test('CL-UI-45 (5b): a region switch clears the list, shows the skeleton and repaints the counts', async () => {
  const base = await boot();
  await send('Page.navigate', {url: base + '?region=tw&date=today&tier=all'});
  await evaljs(`new Promise((res,rej)=>{const t0=Date.now();const iv=setInterval(()=>{
    if(document.querySelectorAll('#spots-container .card:not(.card-skeleton)').length>10){clearInterval(iv);res(1);}
    else if(Date.now()-t0>30000){clearInterval(iv);rej(new Error('cards never rendered'));}},100);})`);
  await sleep(600);
  const before = await evaljs(`(()=>({cards:document.querySelectorAll('#spots-container .card:not(.card-skeleton)').length,
    tabs:document.getElementById('tier-tabs').textContent.replace(/\\s+/g,' ').trim()}))()`);
  assert.ok(before.cards > 10, 'TW list rendered');
  // switch region and read the list in the same task: no old-region card may
  // survive the switch, and the skeleton must be what is on screen.
  const during = await evaljs(`(()=>{
    const sel=document.getElementById('country-select'); sel.value='jp'; switchRegion('jp');
    return {cards:document.querySelectorAll('#spots-container .card:not(.card-skeleton)').length,
      skeletons:document.querySelectorAll('#spots-container .card-skeleton').length,
      tabs:document.getElementById('tier-tabs').textContent.trim(),
      stats:(window.CLListStats||{})};})()`);
  assert.equal(during.cards, 0, 'the previous region\'s cards are gone immediately');
  assert.ok(during.skeletons >= 4, 'a skeleton states that data is on its way');
  assert.equal(during.tabs, '', 'no stale tier counts during the switch');
  assert.equal(during.stats.region, 'jp');
  assert.equal(during.stats.loading, true, 'the count publish says loading, never the old total');
  await evaljs(`new Promise((res,rej)=>{const t0=Date.now();const iv=setInterval(()=>{
    if(document.querySelectorAll('#spots-container .card:not(.card-skeleton)').length>10){clearInterval(iv);res(1);}
    else if(Date.now()-t0>30000){clearInterval(iv);rej(new Error('jp cards never rendered'));}},100);})`);
  await sleep(400);
  const after = await evaljs(`(()=>{const st=window.CLListStats||{};
    return {cards:document.querySelectorAll('#spots-container .card:not(.card-skeleton)').length,
      skeletons:document.querySelectorAll('#spots-container .card-skeleton').length,
      stats:st, tierText:document.getElementById('tier-tabs').textContent.replace(/\\s+/g,' ').trim(),
      resultLine:(document.getElementById('filter-result-summary')||{}).textContent};})()`);
  assert.equal(after.skeletons, 0, 'the skeleton is replaced by the real list');
  assert.equal(after.stats.region, 'jp');
  assert.equal(after.stats.listed, after.cards, 'the published count IS the rendered list length');
  assert.match(String(after.tierText), new RegExp(String(after.cards)), 'tier tabs agree with the list');
  assert.match(String(after.resultLine), new RegExp(String(after.cards)), 'the result line agrees with the list');
});

test('CL-UI-45 teardown', async () => {
  try { ws?.close(); } catch {}
  try { chrome?.kill(); } catch {}
  if (server) await new Promise(r => server.close(r));
});
