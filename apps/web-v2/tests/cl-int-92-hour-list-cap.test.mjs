// CL-INT-92: the modal day row's qualifying-hour stamp list must cover the
// SAME hour set as its count. The served 象山 (tw-002) evidence —
// 「符合時數 6 · 18:00、19:00、20:00、21:00」 — came from v2DayHtml's
// hoursList.slice(0,4) cap: the count was computed from the full
// v2EffectiveHours list while the stamps were truncated. The data contract
// (evaluations-latest good_hours vs evaluations-details rows, CL-INT-91)
// already held; the defect was display-only. The fix renders the FULL list
// via formatHourSegments (consecutive hours compress to a segment).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const block=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,appSource.indexOf(start))
);
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));

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
  grab('function v2DayHtml','let v2Details={}'),
  'return {v2DayHtml,formatHourSegments,v2EffectiveHours};'
].join('\n'));
const {v2DayHtml,formatHourSegments,v2EffectiveHours}=factory();

// 象山 replay: a future day whose good_hours carry 6 consecutive qualifying
// hours (18:00–23:00). The count and the stamp list must describe the same
// set — no 4-stamp cap.
test('CL-INT-92: day-row stamp list covers every qualifying hour the count reports',()=>{
  const day={local_date:'2030-01-01',state:'GUIDANCE_SATISFIED',
    good_hours:['18:00','19:00','20:00','21:00','22:00','23:00'],
    hour_counts:{GUIDANCE_SATISFIED:6,UNFAVORABLE:18,NOT_EVALUABLE:0}};
  assert.deepEqual(v2EffectiveHours(day,'Asia/Taipei'),day.good_hours);
  const html=v2DayHtml(day,'11/01','Asia/Taipei',{spot_id:'tw-002'},'city_night','tw-002-P02');
  assert.match(html,/符合時數 6/);
  // Compressed segment covers all six hours — 22:00/23:00 are never dropped.
  assert.match(html,/18:00–23:00/);
  assert.ok(!html.includes('18:00、19:00、20:00、21:00'),'4-stamp cap must be gone');
});

// Disjoint hours stay fully enumerated (one stamp per isolated hour).
test('CL-INT-92: disjoint qualifying hours are enumerated completely',()=>{
  const day={local_date:'2030-01-01',state:'GUIDANCE_SATISFIED',
    good_hours:['05:00','12:00','22:00'],
    hour_counts:{GUIDANCE_SATISFIED:3,UNFAVORABLE:21,NOT_EVALUABLE:0}};
  const html=v2DayHtml(day,'11/01','Asia/Taipei',{spot_id:'tw-002'},'city_night','tw-002-P02');
  assert.match(html,/符合時數 3/);
  assert.match(html,/05:00、12:00、22:00/);
});

// The shipped source no longer contains the cap, and stamps always go through
// formatHourSegments (the single segment-compression helper).
test('CL-INT-92: v2DayHtml no longer slices the stamp list',()=>{
  const fn=grab('function v2DayHtml','let v2Details={}');
  assert.ok(!fn.includes('slice(0,4)'), 'slice(0,4) cap must be removed');
  assert.match(fn,/formatHourSegments\(hoursList\)/);
});
