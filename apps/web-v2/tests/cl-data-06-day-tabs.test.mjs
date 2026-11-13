// CL-DATA-06: forecast-days maximization — homepage day tabs extend from the
// three-day filter (today/tomorrow/after_tomorrow) to seven days with a
// scrollable strip, render-time date labels beyond day 2, and an honest
// forecast-confidence note on the far tabs (no precision claims).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const htmlSource=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));

// --------------------------------------------------------------------------
// Part A: i18n keys for the far-day labels, discovery header and confidence
// note exist in all three locales.
// --------------------------------------------------------------------------
test('CL-DATA-06 A1: far-day keys exist in zh-TW / en / ja',()=>{
  assert.ok(appSource.includes("v2_best_subject_far:'當日最佳題材：'"));
  assert.ok(appSource.includes("v2_none_far:'當日無符合題材'"));
  assert.ok(appSource.includes("where_far:'📍 當天去哪裡拍？'"));
  assert.ok(appSource.includes("day_conf_note:'第4天起預報可信度逐日遞減'"));
  assert.ok(appSource.includes("v2_best_subject_far:'Best subject that day: '"));
  assert.ok(appSource.includes("v2_none_far:'No qualifying subject that day'"));
  assert.ok(appSource.includes("day_conf_note:'Forecast confidence decreases day by day from day 4'"));
  assert.ok(appSource.includes("v2_best_subject_far:'当日の最適な題材：'"));
  assert.ok(appSource.includes("day_conf_note:'4日目以降は予報の信頼度が日ごとに低下します'"));
});

// --------------------------------------------------------------------------
// Part B: the day-key/offset model — seven valid days, far-day helpers.
// --------------------------------------------------------------------------
test('CL-DATA-06 B1: VALID_DAYS spans seven days and the offset map is exact',()=>{
  assert.ok(appSource.includes("VALID_DAYS=['today','tomorrow','after_tomorrow','day3','day4','day5','day6']"));
  assert.ok(appSource.includes("DAY_KEYS=['today','tomorrow','after_tomorrow','day3','day4','day5','day6']"));
  assert.ok(appSource.includes("DAY_OFFSETS={today:0,tomorrow:1,after_tomorrow:2,day3:3,day4:4,day5:5,day6:6}"));
});

test('CL-DATA-06 B2: selectedDayOffset reads the map for every key',()=>{
  const sel=grab('function selectedDayOffset','function localDateString');
  assert.ok(sel.includes('DAY_OFFSETS[currentDayFilter]??0'));
});

test('CL-DATA-06 B3: far-day subject/header keys are wired',()=>{
  const best=grab('const v2BestSubjectKey=()=>','const v2NoneSubjectKey=()=>');
  const none=grab('const v2NoneSubjectKey=()=>','// Place names are the one intentional locale exception');
  assert.ok(best.includes("isFarDay(currentDayFilter)?'v2_best_subject_far'"));
  assert.ok(none.includes("isFarDay(currentDayFilter)?'v2_none_far'"));
  const disc=grab('function updateDiscoveryText','function applyStaticI18n');
  assert.ok(disc.includes("isFarDay(currentDayFilter)?d().where_far"));
});

// --------------------------------------------------------------------------
// Part C: syncDayButtons — seven tabs, data-day matching, far-tab date labels
// plus the confidence note in title/aria (day 4 onward).
// --------------------------------------------------------------------------
test('CL-DATA-06 C1: the picker labels far days with MM/DD and a confidence note',()=>{
  const sync=grab('function dayPickerOption','function renderDayPicker');
  assert.ok(sync.includes("shortDateStamp(localDateString(null,i))"));
  assert.ok(sync.includes("i>=4?d().day_conf_note:''"));
});

// --------------------------------------------------------------------------
// Part D: homepage markup — seven buttons with data-day keys in a
// scrollable strip container.
// --------------------------------------------------------------------------
test('CL-DATA-06 D1: the picker offers all seven day keys (CL-UI-46 rendering)',()=>{
  const render=grab('function renderDayPicker','function syncDayButtons');
  for(const k of ['today','tomorrow','after_tomorrow','day3','day4','day5','day6']){
    assert.ok(render.includes(`data-day="${k}"`)||appSource.includes(`'${k}'`),k);
  }
  assert.ok(render.includes('DAY_KEYS.map'));
  assert.ok(htmlSource.includes('id="day-picker-trigger"'));
  assert.ok(htmlSource.includes('id="day-picker-panel"'));
});

test('CL-DATA-06 D2: the strip is replaced by the picker (CL-UI-46)',()=>{
  assert.ok(cssSource.includes('.day-picker-trigger'));
  assert.ok(!cssSource.includes('.day-nav-strip'));
});

// --------------------------------------------------------------------------
// Part E: the V2 evaluation surfaces span the full seven-day window.
// --------------------------------------------------------------------------
test('CL-DATA-06 E1: evalDayLabels covers day 0-6 (relative words, then MM/DD)',()=>{
  const helper=grab('function evalDayLabels','function v2OpportunityById');
  assert.ok(helper.includes("d().eval2_d0")&&helper.includes("d().eval2_d1")&&helper.includes("d().eval2_d2"));
  assert.ok(helper.includes("shortDateStamp(localDateString(tz||'UTC',i))"));
});

test('CL-DATA-06 E2: modal summary and place-guide eval render all seven days',()=>{
  const modal=grab('function modalSummaryData','function modalDayRow');
  assert.ok(modal.includes('DAY_KEYS.map'));
  const guide=grab('CL-DATA-06: show the full 7-day evaluation window','const labels=evalDayLabels');
  assert.ok(guide.includes('opp.days.slice(0,DAY_KEYS.length)'));
});

test('CL-DATA-06 E3: the weather modal day switch offers all seven tabs',()=>{
  const block=grab('const daySwitch=DAY_KEYS.map',").join('')");
  assert.ok(block.includes('DAY_KEYS.map'));
  assert.ok(block.includes('data-modal-day'));
});

// --------------------------------------------------------------------------
// Part F: v2DayLabel fallback for unmatched dates beyond day 2 falls back to
// the spot-local MM/DD stamp for that offset, never to a day-2 label.
// --------------------------------------------------------------------------
test('CL-DATA-06 F1: v2DayLabel date fallback extends past day 2',()=>{
  const fn=grab('function v2DayLabel','// CL-UI-18: user-facing stamps follow the page-header convention');
  assert.ok(fn.includes('fallbackIdx>=3'));
  assert.ok(fn.includes("shortDateStamp(localDateString(tz||'UTC',fallbackIdx))"));
});

