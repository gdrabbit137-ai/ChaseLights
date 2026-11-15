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
  grab('function clui82CloudFullReason','function tempChipHtml'),
  grab('function decorateWeatherTimeline','function decorateV2Eval'),
  'return {esc,v2EffectiveHours,v2DayHtml,v2HourLabel,decorateWeatherTimeline,v2RemainingHoursList};'
].join('\n'));
const {esc,v2EffectiveHours,v2DayHtml,v2HourLabel,decorateWeatherTimeline,v2RemainingHoursList}=factory();

// ---- CL-UI-43 i) single evaluation source for the hourly table ----

test('CL-UI-94/43 i: the 適合題材 cell IS the hourly verdict — the status column is retired',()=>{
  const rowBlock=grab('(spot.hourly_forecast||[])','decorateWeatherTimeline(spot');
  // CL-UI-94: no status cell at all — the placeholder td and the mobile
  // status span are gone; the subject cell (subject-cards hours) is the
  // single truth (✓chip / ○ 可拍 / ✗短原因).
  assert.ok(!rowBlock.includes('<td>${esc(d().eval2_unk)}</td>'),'no placeholder status cell');
  assert.ok(!rowBlock.includes('timeline-mobile-status'),'no mobile status span');
  assert.ok(!appSource.includes('th_status:</th>')&&!rowBlock.includes('d().th_status'),'no 狀態 header in the hourly table');
  // The legacy shortOpportunityState verdict is gone from the hourly render.
  assert.ok(!rowBlock.includes('shortOpportunityState(metrics)'));
  // The legacy scores remain only as a row-presence/sorting reference.
  assert.match(rowBlock,/const metrics=\(activeOpportunityId&&item\.opportunity_scores\?\.\[activeOpportunityId\]\)\|\|item\.theme_scores\?\.\[activeTheme\]/);
  // The subject cell is the verdict source for every row.
  assert.match(rowBlock,/const subjCell=v2HourSubjectCell\(spot,item\)/);
  // Past hours are told by the past-row tint alone (CL-UI-96) — never a
  // 歷史 status tag, and no （已過） small text in the time cell.
  assert.match(rowBlock,/isPast\?'past-row'/);
  assert.ok(!rowBlock.includes('d().tag_past'),'歷史 tag retired from the hourly table');
  // The V2 painter that filled cells[1] from evaluations-details is retired
  // (it was the contradiction source: it could paint ⚠未符 next to a ✓chip).
  const decoBlock=grab('function decorateWeatherTimeline','function decorateV2Eval');
  assert.match(decoBlock,/CL-UI-94/);
  assert.match(decoBlock,/return;\s*\n\s*\}/);
  assert.ok(!decoBlock.includes('cells[1]'),'painter no longer writes cells[1]');
});

test('CL-UI-94 fixture replay (碧潭/望幽谷 shape + 大屯山 contradiction): eval-detail verdicts never reach the hourly table',async()=>{
  // Fixture: the card says 「本日無符合」 (V2 zero qualifying hours) while the
  // legacy hourly payload scores every hour as recommended.
  const v2Day={local_date:'2030-01-01',state:'UNFAVORABLE',good_hours:[],hour_counts:{GUIDANCE_SATISFIED:0,UNFAVORABLE:24,NOT_EVALUABLE:0}};
  assert.deepEqual(v2EffectiveHours(v2Day,'Asia/Taipei'),[]);
  // The eval2 day row built from that fixture shows zero qualifying hours and
  // never lists a qualifying hour window.
  const html=v2DayHtml(v2Day,'今天','Asia/Taipei',{spot_id:'tw-007'},'mountain_view','tw-007-P01');
  assert.match(html,/符合時數 0/);
  assert.ok(!/✅/.test(html));
  // CL-UI-94: with the status column retired, evaluations-details verdicts
  // have NO render path into the hourly table at all — the retired painter
  // must leave every cell untouched, even when the details bundle carries a
  // GUIDANCE_SATISFIED/UNFAVORABLE verdict for the same hour (the 大屯山
  // contradiction class: chip said ✓ while the painter painted ⚠未符).
  const detail={opportunities:[{opportunity_id:'tw-007-P01',days:[
    {local_date:'2020-01-01',hours:[{local:'06:00',status:'GUIDANCE_SATISFIED'},{local:'07:00',status:'GUIDANCE_SATISFIED'}]},
    {local_date:'2030-01-01',hours:[{local:'06:00',status:'GUIDANCE_SATISFIED'},{local:'12:00',status:'UNFAVORABLE'}]}
  ]}]};
  const rows=[
    {v2t:'2020-01-01|06:00'}, // past hour — time column marks it, painter stays silent
    {v2t:'2020-01-01|07:00'},
    {v2t:'2030-01-01|06:00'}, // future GUIDANCE_SATISFIED — chip-side source only
    {v2t:'2030-01-01|12:00'}  // future UNFAVORABLE — never ⚠️ 未符 in a cell
  ];
  const painted=await runDecorate(detail,'tw-007',rows);
  for(const r of rows)assert.equal(painted.get(r.v2t),'','retired painter writes nothing — no ⚠️ 未符/✅/歷史 text in any cell');
});

// Small fake-DOM harness around the shipped decorateWeatherTimeline.
function runDecorate(detail,spotId,rows){
  const els=rows.map(r=>({dataset:{v2t:r.v2t},cells:[null,{textContent:''}]}));
  // The mobile paint branch (CL-UI-82) touches classList and the general
  // chips on every card — stub them or the branch throws async after the
  // test ends (unhandledRejection fails the run even when all tests pass).
  const mobileEls=rows.map(r=>({dataset:{v2t:r.v2t},querySelector:()=>({textContent:''}),classList:{add(){},remove(){}},querySelectorAll:()=>[]}));
  const run=new Function('els','mobileEls','detailJson',[
    block('const i18nDict','const categoryKeys'),
    "let currentLang='zh-TW';const d=()=>i18nDict[currentLang]||i18nDict['zh-TW'];",
    grab('function localDateString','function currentDayForSpot'),
    grab('function localNowMinutes','function v2BestForSpot'),
    grab('function v2HourLabel','function v2PickRefHour'),
    grab('function clui82CloudFullReason','function tempChipHtml'),
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

// ---- CL-UI-43 x) CHALLENGER-14/C: the hourly status word is three-way ----

test('CL-UI-43 x: v2HourLabel splits window-geometry misses from weather failures',()=>{
  const outside={status:'UNFAVORABLE',conditions:[
    {role:'REQUIRED',metric:'city_night_window',verdict:'FAIL'},
    {role:'REQUIRED',metric:'visibility',verdict:'PASS'}]};
  assert.equal(v2HourLabel(outside),'🕒 非建議時段','window-geometry-only FAIL → neutral 🕒');
  const weather={status:'UNFAVORABLE',conditions:[
    {role:'REQUIRED',metric:'city_night_window',verdict:'FAIL'},
    {role:'REQUIRED',metric:'cloud_cover_total',verdict:'FAIL'}]};
  assert.equal(v2HourLabel(weather),'⚠️ 未符','any weather FAIL stays ⚠️ 未符');
  const mixed={status:'UNFAVORABLE',conditions:[
    {role:'REQUIRED',metric:'sunset_window',verdict:'FAIL'},
    {role:'REQUIRED',metric:'wind_speed_10m',verdict:'FAIL'}]};
  assert.equal(v2HourLabel(mixed),'⚠️ 未符','mixed window+weather → 未符');
  assert.equal(v2HourLabel({status:'GUIDANCE_SATISFIED',conditions:[]}),'✅ 符合');
  // bare-string input stays supported (CL-UI-43 callers pass a status)
  assert.equal(v2HourLabel('UNFAVORABLE'),'⚠️ 未符');
  assert.equal(v2HourLabel('GUIDANCE_SATISFIED'),'✅ 符合');
  assert.equal(v2HourLabel(null),'資料不足');
  // the window metric set mirrors evaluate_batch.py TIME_WINDOW_METRICS
  assert.match(appSource,/V2_HOUR_WINDOW_METRICS=new Set\(\['light_window','sunrise_time_window','sunset_window','golden_hour_window','blue_hour_window','city_night_window','astronomical_darkness','daylight_window'\]\)/);
});

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

