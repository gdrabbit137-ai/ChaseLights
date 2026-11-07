// CL-UI-43: single evaluation source for the weather-modal hourly
// table (fail-closed to the V2 evaluations-details verdict) + field-driven
// astronomy cell. The V1 shell (repo-root assets/app.js) has no DOM harness,
// so this suite combines extracted-function tests (with a small fake-DOM
// harness for the decorate pass) with source assertions — same approach as
// CL-UI-12/13/14. The fixture replays the reported 碧潭/望幽谷 failure shape:
// legacy scores exist for every hour while the V2 evaluation has zero
// qualifying hours for the whole day.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const block=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,appSource.indexOf(start))
);
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));

// Extract the shipped pure helpers and run them for real.
const factory=new Function([
  block('const i18nDict','const categoryKeys'),
  "let currentLang='zh-TW',currentTempUnit='C',currentRegion='tw',currentDayFilter='today';",
  'const d=()=>i18nDict[currentLang]||i18nDict["zh-TW"];',
  'const listSep=()=>currentLang==="en"?", ":"、";',
  'const v2DominantFailReason=()=>"條件未達";',
  grab('function esc','const OPPORTUNITY_NEGATIVE_STATUS_KEYS'),
  grab('function localDateString','function currentDayForSpot'),
  grab('function localNowMinutes','function v2ParseLocalStamp'),
  grab('function v2DayForOffset','function v2BestForSpot'),
      grab('function formatHourSegments','function v2ContractThreshold'),
  grab('function v2HourLabel','function v2PickRefHour'),
  grab('function v2DayHtml','let v2Details={}'),
  grab('function decorateWeatherTimeline','function decorateV2Eval'),
  'return {esc,v2EffectiveHours,v2DayHtml,v2HourLabel,decorateWeatherTimeline,v2RemainingHoursList};'
].join('\n'));
const {esc,v2EffectiveHours,v2DayHtml,v2HourLabel,decorateWeatherTimeline,v2RemainingHoursList}=factory();

// ---- CL-UI-43 i) single evaluation source for the hourly table ----

test('CL-UI-43 i: the hourly status cell is V2-owned — legacy verdicts are never painted',()=>{
  const rowBlock=grab('(spot.hourly_forecast||[])','decorateWeatherTimeline(spot');
  // The initial cell is the honest placeholder; decorateWeatherTimeline fills
  // the V2 verdict per hour.
  assert.match(rowBlock,/<td>\$\{esc\(d\(\)\.eval2_unk\)\}<\/td>/);
  assert.match(rowBlock,/timeline-mobile-status">\$\{esc\(d\(\)\.eval2_unk\)\}/);
  // The legacy shortOpportunityState verdict is gone from the hourly render.
  assert.ok(!rowBlock.includes('shortOpportunityState(metrics)'));
  // The legacy scores remain only as a row-presence/sorting reference.
  assert.match(rowBlock,/const metrics=\(activeOpportunityId&&item\.opportunity_scores\?\.\[activeOpportunityId\]\)\|\|item\.theme_scores\?\.\[activeTheme\]/);
  // The V2 fill pass is the only place the per-hour verdict is decided.
  const decoBlock=grab('function decorateWeatherTimeline','function decorateV2Eval');
  assert.match(decoBlock,/v2HourLabel\(st\)/);
  assert.match(decoBlock,/ensureV2Detail\(spot\.spot_id\)/);
});

test('CL-UI-43 i fixture replay (碧潭/望幽谷 shape): V2 0 qualifying hours + legacy scores → no ✅ in the hourly table',async()=>{
  // Fixture: the card says 「本日無符合」 (V2 zero qualifying hours) while the
  // legacy hourly payload scores every hour as recommended.
  const v2Day={local_date:'2030-01-01',state:'UNFAVORABLE',good_hours:[],hour_counts:{GUIDANCE_SATISFIED:0,UNFAVORABLE:24,NOT_EVALUABLE:0}};
  assert.deepEqual(v2EffectiveHours(v2Day,'Asia/Taipei'),[]);
  // The eval2 day row built from that fixture shows zero qualifying hours and
  // never lists a qualifying hour window.
  const html=v2DayHtml(v2Day,'今天','Asia/Taipei',{spot_id:'tw-007'},'mountain_view','tw-007-P01');
  assert.match(html,/符合時數 0/);
  assert.ok(!/✅/.test(html));
  // And the hourly status source can only come from the V2 fill pass — with a
  // V2 day of zero GUIDANCE_SATISFIED hours the map carries no ✅ status at
  // all, so no row can ever show one (asserted structurally in the test above
  // and behaviorally via the paint harness below).
  const detail={opportunities:[{opportunity_id:'tw-007-P01',days:[
    {local_date:'2020-01-01',hours:[{local:'06:00',status:'GUIDANCE_SATISFIED'},{local:'07:00',status:'GUIDANCE_SATISFIED'}]},
    {local_date:'2030-01-01',hours:[{local:'06:00',status:'UNFAVORABLE'}]}
  ]}]};
  const rows=[
    {v2t:'2020-01-01|06:00'}, // past hour — must degrade, never ✅
    {v2t:'2020-01-01|07:00'},
    {v2t:'2030-01-01|06:00'}  // future hour with V2 UNFAVORABLE
  ];
  const painted=await runDecorate(detail,'tw-007',rows);
  assert.equal(painted.get('2020-01-01|06:00'),'歷史');
  assert.equal(painted.get('2020-01-01|07:00'),'歷史');
  assert.equal(painted.get('2030-01-01|06:00'),'⚠️ 未符');
  // A V2 GUIDANCE_SATISFIED hour in the future still earns ✅ (no regression).
  const detail2={opportunities:[{opportunity_id:'tw-007-P01',days:[
    {local_date:'2030-01-01',hours:[{local:'17:00',status:'GUIDANCE_SATISFIED'}]}
  ]}]};
  const painted2=await runDecorate(detail2,'tw-007',[{v2t:'2030-01-01|17:00'}]);
  assert.equal(painted2.get('2030-01-01|17:00'),'✅ 符合');
});

// Small fake-DOM harness around the shipped decorateWeatherTimeline.
function runDecorate(detail,spotId,rows){
  const els=rows.map(r=>({dataset:{v2t:r.v2t},cells:[null,{textContent:''}]}));
  const mobileEls=rows.map(r=>({dataset:{v2t:r.v2t},querySelector:()=>({textContent:''})}));
  const run=new Function('els','mobileEls','detailJson',[
    block('const i18nDict','const categoryKeys'),
    "let currentLang='zh-TW';const d=()=>i18nDict[currentLang]||i18nDict['zh-TW'];",
    grab('function localDateString','function currentDayForSpot'),
    grab('function localNowMinutes','function v2BestForSpot'),
    grab('function v2HourLabel','function v2PickRefHour'),
    grab('function decorateWeatherTimeline','function decorateV2Eval'),
    'const document={getElementById:id=>id==="timeline-body"?{querySelectorAll:()=>els}:null,querySelectorAll:()=>mobileEls};',
    'const ensureV2Detail=()=>Promise.resolve(JSON.parse(detailJson));',
    'decorateWeatherTimeline({spot_id:'+JSON.stringify(spotId)+',timezone:"Asia/Taipei"},"'+spotId+'-P01");',
    'return ensureV2Detail().then(()=>{});'
  ].join('\n'));
  // The paint pass runs inside a .then(); await it, then read the cells.
  return run(els,mobileEls,JSON.stringify(detail)).then(()=>{
    const cells=new Map();
    els.forEach((el,i)=>cells.set(rows[i].v2t,el.cells[1].textContent));
    return cells;
  });
}

// ---- CL-UI-43 ii) past hours never count as qualifying ----

test('CL-UI-43 ii: eval2 day rows share the card v2EffectiveHours anchor — past days degrade',()=>{
  // A past day (stale-bundle scenario): the card shows 0 hours via
  // v2EffectiveHours; the eval2 row must agree.
  const pastDay={local_date:'2020-01-01',state:'GUIDANCE_SATISFIED',good_hours:['06:00','07:00','18:00']};
  assert.deepEqual(v2EffectiveHours(pastDay,'Asia/Taipei'),[]);
  const html=v2DayHtml(pastDay,'昨天','Asia/Taipei',{spot_id:'tw-007'},'mountain_view','tw-007-P01');
  assert.match(html,/此日已過/);
  assert.match(html,/符合時數 0/);
  assert.ok(!/06:00/.test(html), 'a past day must not re-exhibit its full-day list as qualifying');
  // A future day keeps its full-day list (unchanged behaviour).
  const future={local_date:'2030-01-01',state:'GUIDANCE_SATISFIED',good_hours:['06:00','07:00']};
  const fHtml=v2DayHtml(future,'2030/01/01','Asia/Taipei',{spot_id:'tw-007'},'mountain_view','tw-007-P01');
  assert.match(fHtml,/符合時數 2/);
  // The wording exists in all three dictionaries.
  for(const lang of ['zh-TW','en','ja']){
    assert.ok(appSource.includes(lang));
    assert.match(appSource,/eval2_day_past:'/);
  }
  assert.ok(appSource.includes("eval2_day_past:'此日已過，時段不計入符合'"));
  assert.ok(appSource.includes("eval2_day_past:'This day has passed — its hours no longer count as qualifying'"));
  assert.ok(appSource.includes("eval2_day_past:'この日は終了済みのため、適した時間数には含めません'"));
});

