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
import {readFileSync, mkdtempSync, existsSync} from 'node:fs';
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

test('CL-UI-45 (1c): every hourly surface feeds that gate (table, group count, band, quick view)', () => {
  const modal = grab('function renderWeatherModal', 'function closeModal');
  assert.match(modal, /const wmGateOf=date=>\{/,
    'one per-date gate resolver for the modal');
  assert.match(modal, /const g=v2DayQualifiedSet\(v2WmOpp,date,summarySpot\?\.timezone\);/);
  assert.match(modal, /v2HourSubjectCell\(spot,item,gate\)/, 'the day-group ✓/○ counts use the gate');
  assert.match(modal, /v2HourSubjectCell\(spot,item,wmGateOf\(wmDate\)\)/, 'the hourly rows use the gate');
  const band = grab('function v2BandHtml', '// CL-UI-95');
  assert.match(band, /v2HourSubjectCell\(spot,item,bestSet\)/, 'the 24h band uses the same gate');
  // The 現在去會怎樣 quick view is rendered OUTSIDE that pass: it must resolve
  // the same gate instead of passing `null`.
  const quick = grab('function v2QuickViewHtml', '// CL-UI-95 (DESIGN-5): subject-level verdict');
  assert.match(quick, /const qGate=typeof v2GateForSpot==='function'\?v2GateForSpot\(spot,selDate,tz\):null;/,
    'the quick view resolves the day gate through the shared resolver');
  assert.match(quick, /v2BandHtml\(\(spot\.hourly_forecast\|\|\[\]\)\.filter\(it=>it&&it\.local_date===selDate\),spot,qGate\)/,
    'the quick-view 24h band is drawn with that gate, never with null');
  assert.ok(!/v2BandHtml\([^)]*\),spot,null\)/.test(quick), 'no band on the page is drawn ungated');
  // The 3-day rows count 符合時數 from the same set.
  const row = grab('function modalDayRow(', '// CL-UI-29');
  assert.match(row, /const gate=\(typeof v2GateForSpot==='function'\)\?v2GateForSpot\(spot,dateKey,spot&&spot\.timezone\):null;/,
    'the 3-day row resolves the same gate');
  assert.match(row, /return gate\?gate\.size:0;/,
    '符合時數 is the gated hour count — never Object.keys(hours.fit).length');
  assert.ok(!row.includes('Object.keys(scRow.hours.fit).length'),
    'the ungated fit-key count is gone from the modal');
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
    // CL-UI-115 §1: the subject chip now carries the icon set's glyph; the
    // extracted slice has no icons.js, so it gets the same markup shape.
    const clIconSvg=k=>'<svg class="cl-icon" data-cl-icon="'+k+'" aria-hidden="true"></svg>';
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
  // CL-UI-115 §1: the chip's subject glyph (SVG) sits next to the text label.
  assert.match(inside.html, /<span class="subj-chip"><svg class="cl-icon" data-cl-icon="sunset"[^>]*><\/svg> 夕陽<\/span>/,
    'the sunset chip renders its SVG glyph and keeps the text label');
  const ungated = api.v2HourSubjectCell(spot, at('16:00'));
  assert.match(ungated.html, /data-cl-icon="geological_landform"[^>]*><\/svg> 地景/,
    'the landform chip renders its own glyph too');
  const dayWithoutRow = api.v2HourSubjectCell({spot_id: 'tw-999'}, at('16:00'), null);
  assert.equal(dayWithoutRow.cls, 'subj-unknown', 'no artifact row → honest dash (fail-closed)');
  assert.match(dayWithoutRow.html, /—/);
});

test('CL-UI-45 (1e): the quick-view band and 符合時數 agree with good_hours (real artifact row)', () => {
  // The owner-reported shape: the subject-cards layer marks a whole afternoon
  // `fit` while the bundle day row qualifies only a two-hour window (tw-188
  // 2026-11-29: 12 fit keys vs good_hours 16:30/17:00). BOTH reader surfaces
  // must resolve to that day row. The exemplar is DERIVED from the shipped
  // artifacts (CL-CI-36: no hardcoded place/date/filename), preferring the
  // owner case and otherwise the widest gap present in the current refresh.
  const pointer = (appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/) || [])[1];
  assert.ok(pointer, 'app.js names the subject-cards artifact');
  const sc = JSON.parse(readFileSync(join(WEB, 'data', 'v2', 'evaluations', pointer), 'utf8'));
  const evFile = (appSource.match(/V2_EVAL_FILE='([^']+)'/) || [])[1] || 'evaluations-latest.json';
  const ev = JSON.parse(readFileSync(join(WEB, 'apps', 'web-v2', evFile), 'utf8'));
  let best = null;
  for (const [pid, days] of Object.entries(sc.places || {})) {
    const place = ev.places.find(p => p.place_id === pid);
    if (!place) continue;
    for (const [dt, row] of Object.entries(days || {})) {
      const fit = Object.keys((row && row.hours && row.hours.fit) || {});
      if (!fit.length) continue;
      const opp = (place.opportunities || []).find(o => (o.days || []).some(x => x.local_date === dt));
      if (!opp) continue;
      const day = opp.days.find(x => x.local_date === dt);
      const gate = new Set(day.good_hours || []);
      const outside = fit.filter(hh => !gate.has(hh)).length;
      if (!outside) continue;
      const ownerCase = pid === 'tw-188' && dt === '2026-11-29';
      if (!best || ownerCase || outside > best.outside) best = {pid, dt, row, place, opp, day, fit, gate, outside};
      if (ownerCase) break;
    }
    if (best && best.pid === 'tw-188') break;
  }
  assert.ok(best, 'the artifacts carry a place-day whose fit keys exceed the day row');
  const {pid, dt, row, place, opp, fit, gate} = best;
  assert.ok(best.outside > 0, `${pid} ${dt}: ${fit.length} fit keys vs ${gate.size} qualifying hours`);

  const prelude = `
    let currentLang='zh-TW';
    const i18nDict={'zh-TW':{eval2_unk:'資料不足',v2_hour_general_ok:'可拍',state_outside:'非建議時段',
      clui45_day_gated:'本日建議時段外',eval2_hours:'符合時數',v2_tier_recommend:'✓ 推薦'}};
    const d=()=>i18nDict[currentLang];
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
    const listSep=()=>'、';
    const v2SubjectCards={places:{${JSON.stringify(pid)}:{${JSON.stringify(dt)}:${JSON.stringify(row)}}},
      dictionaries:{genre_short_names:{geological_landform:{'zh-TW':'地景'},sunset:{'zh-TW':'夕陽'}},fail_reason_short:{}}};
    const v2SubjectCardRow=(id,date)=>((v2SubjectCards.places[id]||{})[date])||null;
    const v2SubjectCardShorts=(r,lang)=>((r&&r.suitable)||[]).map(s=>s.subject_short&&(s.subject_short[lang]||s.subject_short['zh-TW'])).filter(Boolean);
    const clIconSvg=k=>'<svg class="cl-icon" data-cl-icon="'+k+'" aria-hidden="true"></svg>';
    const v2SubjectCardShortHtml=(r,lang,n)=>((r&&r.suitable)||[]).map(s=>s.subject_short&&(s.subject_short[lang]||s.subject_short['zh-TW'])).filter(Boolean).slice(0,n||99).map(l=>'<span class="cl-summary-subject">'+l+'</span>').join('、');
    const v2PlaceForSpot=()=>(${JSON.stringify(place)});
    const v2DayRel=()=>'future';
    const v2IsToday=()=>false;
    const localNowMinutes=()=>0;
    const v2RemainingHoursList=(l)=>l||[];
    const dayWeatherFor=()=>null;
    const wmoIcon=()=>'';
    const formatTempRange=()=>'';
    const modalDayTierLabel=t=>t==='recommend'?'✓推薦':t==='shootable'?'○可拍':t==='not_recommended'?'✗不宜':'';
    const modalDayTierChip=t=>{const l=modalDayTierLabel(t);return l?'<span class="dg-chip">'+l+'</span>':'';};
  `;
  const cell = grab('function v2HourSubjectCell', '// CL-UI-26:');
  const gateSet = grab('function v2DayQualifiedSet', '// CL-UI-13:');
  const bandSrc = grab('function v2BandHtml', '// CL-UI-95');
  const dayRow = grab('function modalDayRow(', '// CL-UI-29');
  const api = new Function(prelude + "function v2EffectiveHours(day,tz){return v2DayRel(day.local_date)==='past'?[]:(day.good_hours||[]);}" +
    gateSet + cell + bandSrc + dayRow +
    'return {v2DayQualifiedSet,v2GateForSpot,v2SetActiveModalOpp,v2BandHtml,modalDayRow,v2HourSubjectCell};')();
  api.v2SetActiveModalOpp(opp.opportunity_id);
  const spot = {spot_id: pid, timezone: 'Asia/Taipei'};
  const resolved = api.v2GateForSpot(spot, dt, 'Asia/Taipei');
  assert.deepEqual([...resolved].sort(), [...gate].sort(),
    'the shared resolver returns the bundle day row, not the artifact buckets');

  // 24h band: a green (rec) cell may exist only inside good_hours, and the
  // hours the artifact over-marks must come out neutral.
  const hours = [];
  for (let h = 0; h < 24; ++h) {
    hours.push({time: dt + ' ' + String(h).padStart(2, '0') + ':00', local_date: dt});
  }
  const band = api.v2BandHtml(hours, spot, resolved);
  const recHours = [...band.matchAll(/<i class="rec[^"]*" title="([^"]+)"/g)].map(m => m[1]);
  for (const hh of recHours) {
    assert.ok(gate.has(hh), `band painted a green fit cell at ${hh}, outside good_hours`);
  }
  const wholeFit = fit.filter(hh => /:00$/.test(hh));
  const outside = wholeFit.filter(hh => !gate.has(hh));
  assert.ok(outside.length > 0, 'the derived exemplar has whole-hour fit cells outside the day row');
  for (const hh of outside) {
    assert.ok(!recHours.includes(hh), `the old bug: ${hh} is green although the day does not qualify it`);
  }
  const ungated = api.v2BandHtml(hours, spot, null);
  assert.ok(outside.some(hh => new RegExp(`<i class="rec[^"]*" title="${hh}"`).test(ungated)),
    'fixture sanity: ungated the artifact WOULD paint those hours green');

  // 符合時數 = the gated set size, never the raw fit-key count.
  const rowHtml = api.modalDayRow('今天', {hours: fit.length, date: dt}, row, spot, dt);
  assert.match(rowHtml, new RegExp(`符合時數 ${gate.size}`), 'the 3-day row counts the gated hours: ' + rowHtml);
  assert.ok(!new RegExp(`符合時數 ${fit.length}`).test(rowHtml) || fit.length === gate.size,
    'the ungated fit-key count can never be printed again');
  assert.ok(gate.size < fit.length, 'the exemplar genuinely disagrees: gated count < fit keys');
});

// ------------------------------------------------------------- (2) cloud base
test('CL-UI-45 (2): the cloud base is ASL-only; the legacy 60 m floor is 資料下限', () => {
  // No surface may fall back to the AGL value under the 海拔 label.
  assert.ok(!/cloud_base_asl!=null\?[^;]*cloud_base_agl/.test(appSource),
    'the card chip no longer falls back from ASL to AGL');
  assert.match(appSource, /clui45CloudBaseText\(metric\.cloud_base_asl,metric\.cloud_base_agl,clElevForCb\)/,
    'the card chip goes through the one formatter');
  const cb = grab('const CLUI45_CB_FLOOR_M', 'function createSpotCard');
  assert.match(cb, /if\(asl===null\|\|asl===undefined\|\|asl===''\)return '';/, 'no ASL → no value (never the AGL number)');
  assert.match(cb, /if\(clui45CloudBaseIsFloor\(asl,agl,elev\)\)return d\(\)\.clui45_cb_floor;/,
    'a legacy floored row renders 「資料下限」');
  const fn = new Function("const d=()=>({clui45_cb_floor:'資料下限'});" + cb + ';return {clui45CloudBaseText,clui45CloudBaseIsFloor};')();
  assert.equal(fn.clui45CloudBaseText(3620, 60, 3560), '資料下限', 'AGL 60 m = elevation+60 ASL → not a reading');
  assert.equal(fn.clui45CloudBaseText(3620, null, 3560), '資料下限', 'the ASL-only spelling of the same floor');
  assert.equal(fn.clui45CloudBaseText(null, 60, 3560), '', 'AGL alone is never printed as ASL');
  assert.equal(fn.clui45CloudBaseText(1332, 250, 1082), '1332 m', 'a real base keeps its number');
  assert.equal(fn.clui45CloudBaseText(416, 387, 29), '416 m');
  assert.equal(fn.clui45CloudBaseText(null, null, 1000), '');
  // A SERVED shard row (the files that predate the floor fix) renders as 資料下限.
  const shardPath = join(WEB, 'weather_details', 'tw', 'tw-043.json');
  if (existsSync(shardPath)) {
    const shard = JSON.parse(readFileSync(shardPath, 'utf8'));
    const elev = shard.spot.elevation != null ? shard.spot.elevation : shard.spot.api_elevation;
    // The shard is a bonus cross-check, not the contract: the formatter's
    // behaviour is asserted above with synthetic values. Demand nothing about
    // which rows a served shard happens to contain — the floor disappears once
    // the shards are regenerated, and that must not red the gate.
    const floored = (shard.spot.hourly_forecast || []).find(h => h.cloud_base_agl === 60);
    if (floored) {
      assert.equal(fn.clui45CloudBaseText(floored.cloud_base_asl, floored.cloud_base_agl, elev), '資料下限',
        'a served 60 m row is labelled 資料下限, never shown as a measured ASL base');
    } else {
      console.log('# CL-UI-45 (2): served shard carries no legacy 60 m row (floor already gone)');
    }
  }
  assert.match(appSource, /th_cloud_base:'雲底高度（海拔）'/);
  assert.match(appSource, /th_cloud_base:'Cloud base \(ASL\)'/);
  assert.match(appSource, /clui45_cb_floor:'資料下限'/);
  assert.match(appSource, /clui45_cb_floor:'data floor'/);
  assert.match(appSource, /clui45_cb_floor:'データ下限'/);
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

test('CL-UI-45 (3c): a click that races a repaint opens the PRESSED place, never another', () => {
  const guards = grab('const CLUI45_TRANSITION_LOCK_MS', 'function clui45SkeletonHtml');
  assert.match(guards, /const CLUI45_TRANSITION_LOCK_MS=350;/);
  // press-time intent is captured in the capture phase, before any repaint
  assert.match(guards, /container\.addEventListener\('pointerdown',e=>\{[\s\S]*?clui45LastPress=card\?\{placeId:clui45CardKey\(card\)/,
    'the pressed card (and its stable place id) is recorded at press time');
  assert.match(guards, /const timing=clui45TransitionLocked\(\);/);
  assert.match(guards, /if\(diverged\|\|timing\)\{/,
    'the pressed-vs-live mismatch AND the transition window both take the honour-the-press path');
  assert.match(guards, /if\(pressedId&&timing\)\{[\s\S]*?clui45AnnounceListMoving\(\);/,
    'a release that lands on empty space after a repaint is answered too');
  // pointerup resolves the gesture whose click the browser never delivers: only
  // the IDENTICAL node is an ordinary click (a new node for the same place is
  // still the lost gesture), and press-time coordinates guard against drags.
  assert.match(guards, /clui45LastPress=card\?\{placeId:clui45CardKey\(card\),el:card,/,
    'the pressed NODE is kept, not only its place id');
  assert.match(guards, /if\(card&&pressed\.el&&card===pressed\.el\)return;/,
    'the same node under the pointer is left to the ordinary click path');
  assert.match(guards, /Math\.abs\(e\.clientX-pressed\.x\)>10\|\|Math\.abs\(e\.clientY-pressed\.y\)>10/, 'a drag is never treated as a tap');
  assert.match(guards, /if\(clui45OpenPressed\(pressedId\)\)return;/,
    'the pressed place is opened when it is still in the new list');
  assert.match(guards, /function clui45OpenPressed\(placeId\)\{[\s\S]*?live\.__clui45Open\(\)/,
    'the modal is opened through the card\'s own opener (no synthetic click loop)');
  assert.match(appSource, /card\.__clui45Open=\(\)=>cpOpenCard\(spot,metric\);/, 'every card stores its opener at render time');
  assert.match(guards, /clui45AnnounceListMoving\(\);/, 'a pressed place the repaint dropped is announced, never swallowed');
  assert.match(appSource, /clui45_list_moving:'列表更新中，請再點一次'/, 'the notice is real user copy (zh)'); 
  assert.match(appSource, /clui45_list_moving:'The list is updating — tap again'/);
  assert.match(appSource, /clui45_list_moving:'一覧を更新中です。もう一度タップしてください'/);
  assert.match(cssSource, /\.clui45-transition-note\s*\{/, 'the notice has a surface (CSS)');
  // the old swallow-and-return path must be gone: a locked click can never just vanish
  assert.ok(!/if\(clui45TransitionLocked\(\)\)\{\s*\/\/[^\n]*\n(?:\s*\/\/[^\n]*\n)*\s*e\.preventDefault\(\);e\.stopImmediatePropagation\(\);\s*return;/.test(guards),
    'the 0/10 dead-tap branch is gone');
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
  assert.match(appSource, /clui45PublishListStats\(tierRows,clui66TierCounts\(tierRows\),clui66TierCounts\(rowsAll\)\);/,
    'published once per render pass, over the SAME filtered rows the list renders (plus the unfiltered ✓推薦 total)');
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
    if (/app\.css\?v=/.test(src)) assert.match(src, /app\.css\?v=clui147/, `${page}: app.css stamp`);
  }
  assert.match(indexSource, /app\.js\?v=clui147/);
  assert.match(indexSource, /custom-places\.js\?v=clapp09n/);
});

// --------------------------------------------------------------- browser race
const BROWSER = [
  process.env.CHROMIUM_EXECUTABLE,
  process.env.CHROME_PATH,
  ...(process.platform === 'win32'
    ? ['C:/Program Files/Google/Chrome/Application/chrome.exe',
       'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe']
    : ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']),
].filter(Boolean).find(p => existsSync(p)) || null;
// CL-CI-140: resolve ONCE at module load and skip-fast when nothing exists. The
// hard-coded Windows path threw ENOENT on the Chromium-less ubuntu job and the
// devtools waiter then sat on its 60 s timeout per case. The static (1)–(7)
// assertions are pure source/artifact checks and keep running everywhere; only
// the three browser-driven cases are gated here, and where a browser exists
// browserTest IS test — no assertion is relaxed.
const NO_BROWSER = 'no browser binary available in this environment; this suite runs in the Chromium job';
const browserTest = BROWSER ? test : () => {};
if (!BROWSER) test('CL-UI-45 browser race cases', {skip: NO_BROWSER}, () => {});
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

browserTest('CL-UI-45 (3d): rapid date switch + a click during the transition never opens another spot', async () => {
  const base = await boot();
  await send('Page.navigate', {url: base + '?region=tw&date=today&tier=all'});
  await evaljs(`new Promise((res,rej)=>{const t0=Date.now();const iv=setInterval(()=>{
    if(document.querySelectorAll('#spots-container .card').length>10){clearInterval(iv);res(1);}
    else if(Date.now()-t0>60000){clearInterval(iv);rej(new Error('cards never rendered'));}},100);})`);
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
  //     The invariant that matters for a photographer: a tap is never swallowed
  //     and never redirected. Whatever opens must belong to the card that was
  //     PRESSED (the page records the press target in the capture phase, and the
  //     click target too, so a repaint cannot fool the oracle); when the pressed
  //     place is gone from the new list the transition notice must say so.
  const realClickAt = async (x, y) => {
    await send('Input.dispatchMouseEvent', {type: 'mousePressed', x, y, button: 'left', clickCount: 1});
    await send('Input.dispatchMouseEvent', {type: 'mouseReleased', x, y, button: 'left', clickCount: 1});
  };
  await evaljs(`(()=>{ const c=document.getElementById('spots-container');
    if(!window.__cl45PressTarget){ window.__cl45PressTarget=null;
      c.addEventListener('pointerdown',function(e){
        const el=e.target.closest&&e.target.closest('.card');
        window.__cl45PressTarget=el?(el.dataset.placeId||''):null;
      },true); }
    if(!window.__cl45ClickTarget){ window.__cl45ClickTarget=null;
      c.addEventListener('click',function(e){
        const el=e.target.closest&&e.target.closest('.card');
        window.__cl45ClickTarget=el?(el.dataset.placeId||''):null;
      },true); }
    return 1; })()`);
  let wrong = 0, attempts = 0, opened = 0, honoured = 0, silent = 0;
  for (let i = 0; i < 10; ++i) {
    await evaljs(`(()=>{switchDay('today');return 1;})()`);
    await sleep(500);
    const probe = await evaljs(`(()=>{const c=[...document.querySelectorAll('#spots-container .card')].find(x=>x.getBoundingClientRect().top>150);
      if(!c)return null;const r=c.getBoundingClientRect();
      return {x:Math.round(r.left+r.width/2), y:Math.round(r.top+Math.min(60,r.height/2)), id:c.dataset.placeId};})()`);
    if (!probe) continue;
    attempts++;
    await evaljs(`window.__cl45ClickTarget=null;window.__cl45PressTarget=null`);
    await send('Runtime.evaluate', {expression: `switchDay('day3')`});
    await realClickAt(probe.x, probe.y);
    await sleep(450);
    const got = await evaljs(`(()=>{const ov=document.getElementById('modal-overlay');
      const open=ov&&ov.style.display==='flex'; const id=ov?ov.dataset.placeId:'';
      const clicked=window.__cl45ClickTarget; const pressed=window.__cl45PressTarget;
      const note=document.getElementById('clui45-transition-note');
      const noteShown=!!(note&&note.classList.contains('show'));
      if(open)closeModal(); return {open, id, clicked, pressed, noteShown};})()`);
    if (got.open) opened++;
    if (got.open && got.id !== got.pressed) wrong++;
    if (got.open && got.id === got.pressed) honoured++;
    if (!got.open && !got.noteShown) silent++;
  }
  assert.ok(attempts >= 8, `race probe must run (attempts=${attempts})`);
  assert.equal(wrong, 0, `a click during the date transition opened ${wrong}/${attempts} modals for a place that was NOT the pressed card`);
  assert.ok(opened > 0, `clicks that can be honoured must open the pressed place (opened ${opened}/${attempts})`);
  assert.equal(silent, 0, `every tap must get an answer — ${silent}/${attempts} were swallowed with no modal and no notice`);

  // (b2) the exact user gesture that produced the wrong mountain: press the
  //      mouse on card A, the list repaints under the pointer, then release on
  //      whatever card is now there. The PRESSED place is the intent: if it is
  //      still in the new list it opens; if the repaint dropped it, the notice
  //      says the list is moving. Never an unrelated spot, never a dead tap.
  let splitOpened = 0, splitWrong = 0, splitSilent = 0, splits = 0;
  for (let i = 0; i < 4; ++i) {
    await evaljs(`(()=>{switchDay('today');return 1;})()`);
    await sleep(500);
    const p2 = await evaljs(`(()=>{const c=[...document.querySelectorAll('#spots-container .card')].find(x=>x.getBoundingClientRect().top>150);
      if(!c)return null;const r=c.getBoundingClientRect();
      return {x:Math.round(r.left+r.width/2), y:Math.round(r.top+Math.min(60,r.height/2)), id:c.dataset.placeId};})()`);
    if (!p2) continue;
    splits++;
    await evaljs(`window.__cl45ClickTarget=null;window.__cl45PressTarget=null`);
    await send('Input.dispatchMouseEvent', {type: 'mousePressed', x: p2.x, y: p2.y, button: 'left', clickCount: 1});
    await send('Runtime.evaluate', {expression: `switchDay('day4')`});
    await send('Input.dispatchMouseEvent', {type: 'mouseReleased', x: p2.x, y: p2.y, button: 'left', clickCount: 1});
    await sleep(450);
    const g2 = await evaljs(`(()=>{const ov=document.getElementById('modal-overlay');
      const open=ov&&ov.style.display==='flex'; const id=ov?ov.dataset.placeId:'';
      const pressed=window.__cl45PressTarget;
      const note=document.getElementById('clui45-transition-note');
      const noteShown=!!(note&&note.classList.contains('show'));
      if(open)closeModal(); return {open, id, pressed, noteShown};})()`);
    if (g2.open) splitOpened++;
    if (g2.open && g2.id !== p2.id) splitWrong++;
    if (!g2.open && !g2.noteShown) splitSilent++;
  }
  assert.ok(splits > 0, 'the split press/release probe must run');
  assert.equal(splitWrong, 0, 'a press/release split across the repaint never opened an unrelated spot');
  assert.equal(splitSilent, 0, 'a press the repaint dropped is announced, not swallowed');
  assert.ok(splitOpened > 0, `a press whose place survived the repaint opens that place (opened ${splitOpened}/${splits})`);

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

browserTest('CL-UI-45 (5b): a region switch clears the list, shows the skeleton and repaints the counts', async () => {
  const base = await boot();
  await send('Page.navigate', {url: base + '?region=tw&date=today&tier=all'});
  await evaljs(`new Promise((res,rej)=>{const t0=Date.now();const iv=setInterval(()=>{
    if(document.querySelectorAll('#spots-container .card:not(.card-skeleton)').length>10){clearInterval(iv);res(1);}
    else if(Date.now()-t0>60000){clearInterval(iv);rej(new Error('cards never rendered'));}},100);})`);
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
    else if(Date.now()-t0>60000){clearInterval(iv);rej(new Error('jp cards never rendered'));}},100);})`);
  await sleep(400);
  const after = await evaljs(`(()=>{const st=window.CLListStats||{};
    const cards=[...document.querySelectorAll('#spots-container .card:not(.card-skeleton)')];
    return {cards:cards.length, todayCards:cards.filter(x=>!x.querySelector('.tomorrow-badge')).length,
      skeletons:document.querySelectorAll('#spots-container .card-skeleton').length,
      stats:st, tierText:document.getElementById('tier-tabs').textContent.replace(/\\s+/g,' ').trim(),
      resultLine:(document.getElementById('filter-result-summary')||{}).textContent};})()`);
  assert.equal(after.skeletons, 0, 'the skeleton is replaced by the real list');
  assert.equal(after.stats.region, 'jp');
  assert.equal(after.stats.listed, after.todayCards, 'the published count IS the rendered list length (the late-night 「明天」 rescue cards are not today\'s list)');
  assert.match(String(after.tierText), new RegExp(String(after.todayCards)), 'tier tabs agree with the list');
  assert.match(String(after.resultLine), new RegExp(String(after.todayCards)), 'the result line agrees with the list');

  // CL-UI-45 (defect 4 follow-up): the day pill must quote the SAME number the
  // ✓推薦 tab shows — it used to run its own dayPickerViableCount walk, so
  // 「今天 · 8 個景點符合」 sat beside 「✓推薦 11」. Check all three regions.
  for (const region of ['tw', 'jp', 'us']) {
    await evaljs(`(()=>{const sel=document.getElementById('country-select');sel.value='${region}';switchRegion('${region}');return 1;})()`);
    await evaljs(`new Promise((res,rej)=>{const t0=Date.now();const iv=setInterval(()=>{
      if(document.querySelectorAll('#spots-container .card:not(.card-skeleton)').length>5){clearInterval(iv);res(1);}
      else if(Date.now()-t0>60000){clearInterval(iv);rej(new Error('${region} cards never rendered'));}},100);})`);
    await sleep(500);
    const c = await evaljs(`(()=>{
      const st=window.CLListStats||{};
      const cards=[...document.querySelectorAll('#spots-container .card:not(.card-skeleton)')];
      const tabs=[...document.querySelectorAll('#tier-tabs .tier-tab')].map(b=>b.textContent.replace(/\\s+/g,' ').trim());
      // CL-UI-46 (2b): the pill's own count moved OFF the visible face (it was
      // printed three times on the first screen) and into the trigger's tooltip
      // and screen-reader label. The CL-UI-45 (counts) invariant is unchanged —
      // the pill, the ✓推薦 tab and the CLListStats publish still quote ONE
      // number; it is now read from the accessible text, not the painted text.
      const trig=document.getElementById('day-picker-trigger');
      const pillFace=trig.textContent.replace(/\\s+/g,' ').trim();
      const pill=(pillFace+' · '+(trig.getAttribute('title')||'')).replace(/\\s+/g,' ').trim();
      return {region:st.region, loading:!!st.loading, listed:st.listed, recommendAll:st.recommendAll,
        todayCards:cards.filter(x=>!x.querySelector('.tomorrow-badge')).length,
        recTab:tabs.find(t=>/推薦/.test(t))||'', pill, pillFace};})()`);
    assert.equal(c.region, region);
    assert.equal(c.loading, false);
    const pillN = (c.pill.match(/·\s*(\d+)\s*個景點符合/) || [])[1];
    const recN = (c.recTab.match(/(\d+)/) || [])[1];
    assert.ok(pillN !== undefined, `${region}: the pill states its count (${c.pill})`);
    assert.equal(pillN, recN, `${region}: pill 「${c.pill}」 must equal the ✓推薦 tab 「${c.recTab}」`);
    assert.equal(Number(pillN), c.recommendAll, `${region}: the pill reads the CLListStats publish`);
    assert.doesNotMatch(c.pillFace, /個景點|spots/, `${region}: the pill FACE prints no place count (CL-UI-46 2b)`);
    assert.equal(c.listed, c.todayCards, `${region}: published list length = rendered cards`);
  }
});

browserTest('CL-UI-45 teardown', async () => {
  try { ws?.close(); } catch {}
  try { chrome?.kill(); } catch {}
  if (server) await new Promise(r => server.close(r));
});
