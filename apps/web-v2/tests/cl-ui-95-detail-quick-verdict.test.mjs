// CL-UI-95: 詳情彈窗速覽單一真相改版 (DESIGN-5, owner-approved mockup
// 0565654aa — origin/task/DESIGN-3 data/v2/audits/design-mockups/mockup-detail.html,
// implemented verbatim; tokens = the live --cl-* layer).
// Contract:
//  (1) 速覽 = 「現在去會怎樣」: the tier chip reads the SAME subject-cards row
//      the card's tier line consumes (row.tier + tier_reason / dominant_reason)
//      — the old status:'failed'→✗短因 read could contradict the card (the
//      汐止翠湖 tw-176 case: status failed·tier shootable → old ✗低雲, card ○可拍).
//  (2) 今日 24h 迷你色帶: built by the SAME v2BandHtml the forecast page's
//      #timeline-band renders (one implementation, same v2HourSubjectCell
//      kind buckets) — never a re-implementation.
//  (3) 題材層判定 demoted: the subject verdict row (今天題材判定) renders
//      UNDER the 8-day strip via v2DaySubHtml; a selected day other than
//      today shows the honest no-verdict hint; the quick panel carries no
//      subject-level chips any more.
//  (4) CL-UI-94 (預報表刪狀態欄) is NOT merged into main (verified) — the
//      band/colloquial components stay single-implementation by construction.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const appCss = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');
const cardsFile = (appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/) || [])[1];
assert.ok(cardsFile, 'subject-cards filename pinned in app.js');
const artifact = JSON.parse(readFileSync(
  join(ROOT, 'data', 'v2', 'evaluations', cardsFile), 'utf8'));

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};

// ---- (A) same-source tier: quick chip == the card's badge tier -------------
// The card badge maps scRow.tier → rec/shoot/no (createSpotCard clBadgeTier).
const CARD_TIER_MAP = {recommend: 'ok', shootable: 'mid', not_recommended: 'bad'};

test('CL-UI-95 (1): quick tier chip is the CARD tier (same subject-cards row, same mapping)', () => {
  // The quick chip reads the SAME row lookup the card tier line uses —
  // v2SubjectCardRow(spotId, localDateString(tz, selectedDayOffset())) —
  // and maps row.tier through the card's three-tier verdict only.
  const quickBlock = grab('function v2QuickViewHtml', '// CL-UI-95 (DESIGN-5): subject-level verdict demoted');
  assert.ok(quickBlock.includes('v2SubjectCardRow(spot&&spot.spot_id,selDate)'),
    'chip source = the card subject-cards row');
  assert.ok(quickBlock.includes("row.tier==='recommend'") && quickBlock.includes("row.tier==='shootable'")
    && quickBlock.includes("row.tier==='not_recommended'"),
    'chip branches read row.tier (single truth), never row.status');
  assert.ok(!quickBlock.includes("row.status==='clear'") && !quickBlock.includes("row.status==='failed'"),
    'the retired status-level read is gone (the tw-176 ✗低雲-vs-○可拍 contradiction class)');
  // tier_reason / dominant_reason feed the chip note exactly like the card's
  // tier row (clNoWinName / scTierReason).
  assert.ok(quickBlock.includes('row.tier_reason'), 'chip note = row.tier_reason');
  assert.ok(quickBlock.includes('v2SubjectCardShortReason(row,currentLang)'),
    'not_recommended note falls back through the card reason chain');
});

test('CL-UI-95 (1b): extracted quick chip agrees with the card badge for EVERY artifact row sampled', () => {
  const helperCode = grab('function v2DominantFailMetric', 'function ensureV2Detail');
  const makePrelude = (dayDate, cards) => `
    const V2_EVAL_METRICS={'zh-TW':{precipitation:'降水'},en:{},ja:{}};
    const V2_FAIL_PRIORITY=['precipitation'];
    let currentLang='zh-TW';
    let v2SubjectCards=${JSON.stringify(cards)};
    const v2SubjectCardRow=(id,date)=>(v2SubjectCards[id]&&v2SubjectCards[id][date])||null;
    const v2SubjectCardShortReason=(row,lang)=>row&&row.dominant_reason?(row.dominant_reason[lang]||row.dominant_reason['zh-TW']||''):'';
    const v2GeneralBaseline=row=>{const gb=row&&row.general_baseline;return (gb&&typeof gb.ok==='boolean')?gb:null;};
    const localDateString=(tz,off)=>dayDate;
    let dayDate=${JSON.stringify(dayDate)};
    const selectedDayOffset=()=>0;
    const localNowMinutes=()=>0;
    const v2RemainingHoursList=(times)=>(times||[]).filter(t=>/^([01]\\d|2[0-3]):[0-5]\\d$/.test(String(t||'')));
    const v2NextWindowLocal=()=>'';
    const v2LocalNow=()=>null;
    const nextWindowStamp=s=>s;
    const clui82PlainWeather=()=>'';
    const v2BestForSpot=null;
    const v2HourSubjectCell=()=>({kind:'na'});
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({'v2_quick_title':'現在去會怎樣','v2_quick_none':'尚無速覽資料','v2_quick_next':'下一個符合時刻：',
      'v2_tier_recommend':'✓ 推薦','v2_tier_shootable':'○ 可拍','v2_tier_not_recommended':'✗ 不宜',
      'eval2_hours':'符合時數','eval2_ok':'符合','eval2_bad':'未符','eval2_unk':'資料不足'});
    const listSep=()=>'、';
    const formatHourSegments=list=>(list||[]).join('、');
    const compactHourSegmentsText=text=>text;
    const v2EffectiveHours=(day)=>((day&&day.good_hours)||[]);
  `;
  const quickOf = (dayDate, cards, spot, place) => new Function(
    makePrelude(dayDate, cards) + helperCode + ';return {v2QuickViewHtml};')().v2QuickViewHtml(spot, place);
  // Sample rows across the artifact (bounded): every sampled row with a
  // known tier must produce the SAME data-tier the card badge maps to.
  let checked = 0;
  outer:
  for (const [pid, days] of Object.entries(artifact.places)) {
    for (const [dt, row] of Object.entries(days)) {
      if (!row || !CARD_TIER_MAP[row.tier]) continue;
      const html = quickOf(dt, artifact.places, {spot_id: pid, timezone: 'Asia/Taipei'}, null);
      const m = /data-tier="(ok|mid|bad)"/.exec(html);
      assert.ok(m, 'chip carries a data-tier marker for ' + pid + ' ' + dt + ': ' + html);
      assert.equal(m[1], CARD_TIER_MAP[row.tier],
        `quick chip tier must equal the card badge tier for ${pid} ${dt} (row.tier=${row.tier})`);
      if (++checked >= 60) break outer;
    }
  }
  assert.ok(checked >= 20, 'sampled enough artifact rows: ' + checked);
});

// ---- (B) band 同源: one builder, two surfaces ------------------------------
test('CL-UI-95 (2): the 24h mini band is the forecast page band (shared v2BandHtml)', () => {
  assert.equal((appSource.match(/function v2BandHtml\(/g) || []).length, 1,
    'exactly one band implementation');
  // Forecast modal call site rewired onto the shared builder.
  assert.match(appSource, /bandEl\.innerHTML=bandRows\.length\?v2BandHtml\(bandRows,spot,v2WmHours\):'';/,
    'forecast #timeline-band renders v2BandHtml');
  // Quick view rides the same builder (place-level rows, no best-frame set).
  assert.match(appSource, /v2BandHtml\(\(spot\.hourly_forecast\|\|\[\]\)\.filter\(it=>it&&it\.local_date===selDate\),spot,null\)/,
    'quick band renders v2BandHtml over the same hourly rows');
  // The builder keeps the forecast band anatomy verbatim (n3b classes).
  const bandBlock = grab('function v2BandHtml', 'function v2QuickViewHtml');
  for (const piece of ['class="band"', "kind==='fit'?'rec'", "kind==='general'?'shoot'",
    "kind==='fail'?'no'", 'band-label', "bestSet&&bestSet.size"]) {
    assert.ok(bandBlock.includes(piece), 'band anatomy piece: ' + piece);
  }
  // CL-UI-94 is NOT merged into main — no second band/colloquial component to
  // dedupe with; the shared functions are the single source by construction.
  assert.ok(!appSource.includes('cl-ui-94'), 'CL-UI-94 absent from main (no dedupe target)');
});

test('CL-UI-95 (2b): extracted v2BandHtml paints the same cells as the forecast band', () => {
  const helperCode = grab('function v2BandHtml', 'function v2QuickViewHtml');
  const prelude = `
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const v2HourSubjectCell=(spot,item)=>({kind:item.__kind});
  `;
  const fns = new Function(prelude + helperCode + ';return {v2BandHtml};')();
  const rows = [
    {__kind: 'fit', time: '2026-11-15 06:00'},
    {__kind: 'general', time: '2026-11-15 09:00'},
    {__kind: 'fail', time: '2026-11-15 14:00'},
    {__kind: 'outside', time: '2026-11-15 23:00'},
  ];
  const html = fns.v2BandHtml(rows, {spot_id: 'tw-176'}, null);
  assert.ok(html.includes('class="band"'), 'band shell');
  assert.ok(html.includes('<i class="rec" title="06:00">'), 'fit → rec cell');
  assert.ok(html.includes('<i class="shoot" title="09:00">'), 'general → shoot cell');
  assert.ok(html.includes('<i class="no" title="14:00">'), 'fail → no cell');
  assert.ok(html.includes('<i class="na" title="23:00">'), 'outside → na cell');
  assert.ok(html.includes('band-label'), 'hour scale label present');
  assert.equal(fns.v2BandHtml([], {}, null), '', 'no rows → no band (honest omit)');
  // bestSet (forecast only) adds the white inset frame.
  const best = fns.v2BandHtml([{__kind: 'fit', time: '2026-11-15 06:00'}], {}, new Set(['06:00']));
  assert.ok(best.includes('class="rec best"'), 'bestSet keeps the white inset frame');
});

// ---- (C) 題材判定 demoted below the 8-day strip ----------------------------
test('CL-UI-95 (3): the subject verdict row renders UNDER the 8-day strip, other days get the hint', () => {
  // Wiring: v2-eval block = strip + day-sub row (in that order).
  assert.match(appSource, /el\.innerHTML=`<div class="v2-eval-block">\$\{dayHtml\}\$\{v2DaySubHtml\(spot,opp\)\}<\/div>`;/,
    'day-sub row rides directly below the strip');
  // The quick panel no longer carries subject-level chips/verdicts.
  const quickBlock = grab('function v2QuickViewHtml', '// CL-UI-95 (DESIGN-5): subject-level verdict demoted');
  assert.ok(!quickBlock.includes('quick-chip'), 'no subject chips in the quick panel');
  // Day-sub semantics: today → 今天題材判定 + verdict; other day → hint.
  const subBlock = grab('function v2DaySubHtml', 'function ensureV2Detail');
  assert.ok(subBlock.includes("selectedDayOffset()!==0") && subBlock.includes('v2_ds_none'),
    'a non-today selected day shows the honest no-verdict hint');
  assert.ok(subBlock.includes('v2_ds_label'), 'today shows the 今天題材判定 label');
  assert.ok(subBlock.includes("row.tier==='shootable'") && subBlock.includes('nextWindowStamp'),
    'verdict = card tier truth + the validated next window');
});

test('CL-UI-95 (3b): extracted v2DaySubHtml — verdict / hint / degrade contracts', () => {
  const helperCode = grab('function v2DominantFailMetric', 'function ensureV2Detail');
  const makePrelude = (offset, cards) => `
    const V2_EVAL_METRICS={'zh-TW':{precipitation:'降水'},en:{},ja:{}};
    const V2_FAIL_PRIORITY=['precipitation'];
    let currentLang='zh-TW';
    let v2SubjectCards=${JSON.stringify(cards)};
    const v2SubjectCardRow=(id,date)=>(v2SubjectCards[id]&&v2SubjectCards[id][date])||null;
    const v2SubjectCardShortReason=(row,lang)=>row&&row.dominant_reason?(row.dominant_reason[lang]||row.dominant_reason['zh-TW']||''):'';
    const v2GeneralBaseline=row=>{const gb=row&&row.general_baseline;return (gb&&typeof gb.ok==='boolean')?gb:null;};
    const TODAY='2026-11-15';
    const localDateString=(tz,off)=>TODAY;
    const selectedDayOffset=()=>${offset};
    const localNowMinutes=()=>600;
    const v2RemainingHoursList=(times,now)=>(times||[]).filter(t=>/^([01]\\d|2[0-3]):[0-5]\\d$/.test(String(t||''))&&Number(t.slice(0,2))*60>=now);
    const v2LocalNow=()=>({date:TODAY,minutes:600});
    const v2NextWindowLocal=(days,now)=>'2026-11-17 07:00';
    const nextWindowStamp=s=>s;
    const v2EffectiveHours=(day)=>(day&&day.state==='GUIDANCE_SATISFIED')?(day.good_hours||[]):[];
    const v2DayForOffset=(opp,off,tz)=>((opp&&opp.days)||[]).find(d=>d.local_date===TODAY)||null;
    const v2Contract=()=>null;
    const reviewedLocaleName=()=>'';
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({'v2_ds_label':'今天題材判定','v2_ds_none':'題材判定僅提供今天','v2_ds_next':'下一窗',
      'v2_ds_nonext':'今日無下一窗','v2_ds_ok_today':'今天 {t} 符合',
      'v2_tier_shootable':'○ 可拍','eval2_ok':'符合','eval2_unk':'資料不足'});
  `;
  const subOf = (offset, cards, spot, opp) => new Function(
    makePrelude(offset, cards) + helperCode + ';return {v2DaySubHtml};')().v2DaySubHtml(spot, opp);
  const spot = {spot_id: 'tw-176', timezone: 'Asia/Taipei'};
  const opp = {opportunity_id: 'tw-176-P01', genre_template: 'overlook',
    days: [{local_date: '2026-11-15', state: 'UNFAVORABLE', good_hours: []}]};

  // Other selected day → the honest no-verdict hint, never a fabricated verdict.
  const far = subOf(2, artifact.places, spot, opp);
  assert.ok(far.includes('v2-day-sub') && far.includes('題材判定僅提供今天'),
    'non-today selection → no-verdict hint: ' + far);
  assert.ok(!far.includes('v2-ds-v'), 'no verdict chip on a non-today day');

  // Today + shootable row → ○可拍·窗已過·…·下一窗 (the card truth).
  const cards = {'tw-176': {'2026-11-15': {status: 'failed', tier: 'shootable',
    tier_reason: {'zh-TW': '窗已過·今日仍可拍', en: 'windows passed · still shootable today', ja: '撮影窓は終了・本日は撮影可'},
    dominant_reason: {'zh-TW': '低雲'}, suitable: []}}};
  const today = subOf(0, cards, spot, opp);
  assert.ok(today.includes('今天題材判定'), 'label rendered on today');
  assert.ok(today.includes('v2-ds-mid'), 'shootable → mid chip');
  assert.ok(today.includes('窗已過·今日仍可拍'), 'tier_reason rides the chip');
  assert.ok(today.includes('下一窗 2026-11-17 07:00'), 'next window stamp in the chip');

  // Today + not_recommended → ✗reason·下一窗 (「翠湖景 ✗低雲·下一窗 …」式).
  const cardsBad = {'tw-176': {'2026-11-15': {status: 'failed', tier: 'not_recommended',
    dominant_reason: {'zh-TW': '低雲'}, suitable: []}}};
  const badHtml = subOf(0, cardsBad, spot, opp);
  assert.ok(badHtml.includes('v2-ds-bad') && badHtml.includes('✗ 低雲'), '✗ short reason chip');
  assert.ok(badHtml.includes('下一窗 2026-11-17 07:00'), 'next window after the reason');

  // Rowless GUIDANCE_SATISFIED day → 今天 {t} 符合 from the remaining hours.
  const oppOk = {opportunity_id: 'tw-176-P01', genre_template: 'overlook',
    days: [{local_date: '2026-11-15', state: 'GUIDANCE_SATISFIED', good_hours: ['06:00', '07:00', '16:25']}]};
  const okHtml = subOf(0, {}, spot, oppOk);
  assert.ok(okHtml.includes('v2-ds-ok') && okHtml.includes('今天 06:00 符合'),
    'ok verdict from the remaining-hours anchor: ' + okHtml);

  // NOT_EVALUABLE → honest 資料不足.
  const oppUnk = {opportunity_id: 'tw-176-P01',
    days: [{local_date: '2026-11-15', state: 'NOT_EVALUABLE', good_hours: []}]};
  const unkHtml = subOf(0, {}, spot, oppUnk);
  assert.ok(unkHtml.includes('v2-ds-unk') && unkHtml.includes('資料不足'), 'honest unknown chip');
});

// ---- (D) styles + stamps + trilingual keys ---------------------------------
test('CL-UI-95 (4): styles, trilingual keys, cache-bust stamp', () => {
  for (const cls of ['.q-chip', '.q-next', '.q-wx', '.quick-band', '.v2-day-sub',
    '.place-quick-view.quick-mid', '.place-quick-view.quick-bad']) {
    assert.ok(appCss.includes(cls), 'css missing ' + cls);
  }
  // No hex outside :root (CL-UI-85 scan contract) in the added block.
  const added = appCss.slice(appCss.indexOf('CL-UI-95 (DESIGN-5): 「現在去會怎樣」'),
    appCss.indexOf('.v2-day-sub{'));
  assert.ok(!/#[0-9a-fA-F]{3,8}\b/.test(added), 'no raw hex in the CL-UI-95 CSS');
  for (const key of ['v2_quick_title', 'v2_quick_next', 'v2_ds_label', 'v2_ds_none',
    'v2_ds_next', 'v2_ds_nonext', 'v2_ds_ok_today']) {
    assert.equal(appSource.split(key + ':').length - 1, 3, key + ' in all three dictionaries');
  }
  assert.equal((indexSource.match(/\?v=clui97/g) || []).length, 2,
    'app.js + app.css both at clui97');
});
