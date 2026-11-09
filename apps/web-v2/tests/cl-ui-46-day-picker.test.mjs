// CL-UI-46: the homepage date switch becomes a picker (owner ruling on
// CL-UI-45 — the horizontal day strip does not fit the form-control cluster
// next to 「全部地區」/「排序」).
// Contract:
//  (1) The strip and its ‹ › arrows are GONE: no day-nav / day-nav-strip /
//      day-nav-arrow markup, no scrollDayNav/syncDayNavArrows wiring, and no
//      strip CSS. The trigger keeps the strip's full-width row slot.
//  (2) The trigger is in the .sort-select form-control family (same radius,
//      surface, text color, hover/focus border) and carries the selected day
//      label + that day's honest viable-count summary.
//  (3) Mobile (≤640px): the panel is a bottom sheet — position:fixed,
//      bottom:0, slide-up transition — over a semi-transparent overlay that
//      closes on tap. Desktop: an absolutely positioned dropdown panel.
//      One data model, two presentations, never both visible at once.
//  (4) a11y: trigger has aria-haspopup=listbox + aria-expanded; options are
//      role=option with aria-selected; keyboard Esc closes and arrows walk.
//  (5) URL ?date= semantics preserved through switchDay → syncContextUrl.
//  (6) Cache-bust stamps bumped to clui49 in the same commit.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const htmlSource=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
const block=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,appSource.indexOf(start))
);
const i18nBlock=block("const i18nDict = {","const categoryKeys = {");

test('CL-UI-46 (1): the CL-UI-45 day strip + arrows are removed everywhere',()=>{
  assert.doesNotMatch(htmlSource,/day-nav|day-btn[^-]/,'strip markup must be gone');
  assert.doesNotMatch(appSource,/scrollDayNav|syncDayNavArrows|dayStrip/,'strip JS wiring must be gone');
  assert.doesNotMatch(cssSource,/\.day-nav|\.day-btn/,'strip CSS must be gone');
  for(const key of ['day_nav_prev','day_nav_next']){
    assert.equal([...i18nBlock.matchAll(new RegExp(`${key}:`,'g'))].length,0,`${key} retired with the arrows`);
  }
  // Trigger keeps the strip's full-width row slot on mobile.
  const media=cssSource.slice(cssSource.indexOf('@media (max-width: 640px)'),cssSource.indexOf('.sub-btn.active'));
  assert.match(media,/\.day-picker-trigger\s*\{[^}]*width:\s*100%;/);
  assert.match(media,/\.day-picker-trigger\s*\{[^}]*min-height:\s*44px;/,'≥44px tap target');
});

test('CL-UI-46 (2): trigger sits in the form-control family (.sort-select tokens)',()=>{
  const trigger=cssSource.slice(cssSource.indexOf('.day-picker-trigger {'),cssSource.indexOf('.day-picker-trigger:hover'));
  assert.match(trigger,/border-radius:\s*6px;/);
  assert.match(trigger,/background:\s*#1e293b;/);
  assert.match(trigger,/color:\s*#cbd5e1;/);
  assert.match(cssSource,/\.day-picker-trigger:hover,\s*\n\s*\.day-picker-trigger:focus-visible\s*\{\s*border-color:\s*#38bdf8;/);
  assert.match(block('function syncDayButtons','function openDayPicker'),/day_summary_(viable|none)/,'trigger carries the day summary count');
});

test('CL-UI-46 (3): mobile bottom sheet + desktop dropdown, one data model',()=>{
  const sheet=cssSource.slice(cssSource.indexOf('@media (max-width: 640px)'),cssSource.indexOf('.sub-btn.active'));
  assert.match(sheet,/\.day-picker-panel\s*\{[^}]*position:\s*fixed;/,'panel is a bottom sheet on mobile');
  assert.match(sheet,/\.day-picker-panel\s*\{[^}]*bottom:\s*0;/);
  assert.match(sheet,/\.day-picker-panel\s*\{[^}]*transform:\s*translateY\(100%\);/,'slides up from the bottom edge');
  assert.match(sheet,/\.day-picker-overlay:not\(\[hidden\]\)\s*\{\s*display:\s*block;/,'semi-transparent overlay is mobile-only (and hidden state still wins — CL-UI-47)');
  assert.match(sheet,/\.day-picker-overlay\[hidden\]\s*\{\s*display:\s*none;/,'CL-UI-47: closed-state overlay can never defeat the [hidden] rule');
  assert.match(cssSource,/rgba\(2,\s*6,\s*23,\s*0\.55\)/,'overlay is semi-transparent');
  // Desktop: the base panel is a dropdown anchored under the trigger.
  const base=cssSource.slice(cssSource.indexOf('.day-picker-panel {'),cssSource.indexOf('.day-option {'));
  assert.match(base,/position:\s*absolute;/);
  assert.match(base,/top:\s*calc\(100\%\s*\+\s*4px\);/);
  // Mobile hides the desktop anchor geometry instead of adding a second control.
  assert.match(sheet,/\.day-picker-panel\s*\{[^}]*top:\s*auto;/);
  assert.match(block('function renderDayPicker','function syncDayButtons'),/role="option"/);
  assert.match(block('function renderDayPicker','function syncDayButtons'),/aria-selected/);
});

test('CL-UI-46 (4): a11y wiring — listbox semantics, Esc close, outside-click close',()=>{
  const trigger=htmlSource.slice(htmlSource.indexOf('id="day-picker-trigger"'),htmlSource.indexOf('id="day-picker-overlay"'));
  assert.match(htmlSource,/aria-haspopup="listbox"/);
  assert.match(trigger,/aria-expanded="false"/);
  assert.match(trigger,/aria-controls="day-picker-panel"/);
  const wiring=block('// CL-UI-46: picker wiring','// CL-UI-28: region carry BACK');
  assert.match(wiring,/dayTrigger\.addEventListener\('click',toggleDayPicker\)/);
  assert.match(wiring,/dayOverlay\.addEventListener\('click',closeDayPicker\)/);
  assert.match(wiring,/if\(e\.key==='Escape'\)\{e\.stopPropagation\(\);closeDayPicker\(\);return;\}/);
  assert.match(wiring,/e\.key==='ArrowDown'\?Math\.min\(opts\.length-1,idx\+1\):Math\.max\(0,idx-1\)/);
  assert.match(wiring,/!trigger\.contains\(e\.target\)\)closeDayPicker\(\);/);
  assert.match(block('function switchDay','// CL-UI-38'),/function switchDay\(k\)\{closeDayPicker\(\);currentDayFilter=k;/,'switching a day closes the picker first');
});

test('CL-UI-46 (5): day option labels — relative words for day 0-2, MM/DD beyond, honest summary',()=>{
  const opt=block('function dayPickerOption','function renderDayPicker');
  assert.match(opt,/d\(\)\.eval2_d0/);
  assert.match(opt,/shortDateStamp\(localDateString\(null,i\)\)/);
  assert.match(opt,/i>=4\?d\(\)\.day_conf_note:''/,'confidence note survives on day 4+');
  assert.match(opt,/d\(\)\.eval2_load_fail/,'no-bundle state is named, never faked');
  const count=block('function dayPickerViableCount','function dayPickerOption');
  // Runnable: two spots, one qualifies on day 1 only.
  const fn=new Function(`
    const currentSpots=[
      {spot_id:'a',timezone:'UTC'},
      {spot_id:'b',timezone:'UTC'}
    ];
    const v2EvalBundle={places:[
      {place_id:'a',opportunities:[{opportunity_id:'o1',days:[{local_date:'2030-01-01',good_hours:['06:00']},{local_date:'2030-01-02',good_hours:[]}]}]},
      {place_id:'b',opportunities:[{opportunity_id:'o2',days:[{local_date:'2030-01-01',good_hours:[]},{local_date:'2030-01-02',good_hours:['07:00']}]}]}
    ]};
    const v2PlaceForSpot=spot=>v2EvalBundle.places.find(p=>p.place_id===spot.spot_id);
    const v2DayForOffset=(o,off,tz)=>o.days[off]||null;
    const v2EffectiveHours=(day,tz)=>day.local_date==='2030-01-01'&&day.good_hours.length?[day.good_hours[0]]:day.good_hours;
    const DAY_OFFSETS={today:0,tomorrow:1,after_tomorrow:2,day3:3,day4:4,day5:5,day6:6};
    ${count}
    return {today:dayPickerViableCount('today'),tomorrow:dayPickerViableCount('tomorrow')};
  `);
  assert.deepEqual(fn(),{today:1,tomorrow:1});
});

test('CL-UI-46 (6): URL ?date= semantics preserved via switchDay → syncContextUrl',()=>{
  const ctx=block('function syncContextUrl','function switchLanguage');
  assert.match(ctx,/u\.searchParams\.set\('date',currentDayFilter\)/);
});

test('CL-UI-46 (7): new i18n keys exist in all three dictionaries',()=>{
  for(const key of ['day_picker_label','day_summary_viable','day_summary_none']){
    const vals=[...i18nBlock.matchAll(new RegExp(`${key}:'([^']*)'`,'g'))].map(m=>m[1]);
    assert.equal(vals.length,3,`${key} must exist in all three dictionaries`);
    vals.forEach(v=>assert.ok(v.length>=2,`${key} carries a meaningful label`));
  }
  assert.match([...i18nBlock.matchAll(/day_summary_viable:'([^']*)'/g)].map(m=>m[1]).join(' '),/\{n\}/,'summary template carries {n}');
});

test('CL-UI-46 (8): index.html cache-bust stamps tracked (app.css bumped to clui53 by CL-UI-49)',()=>{
  assert.match(htmlSource,/assets\/app\.js\?v=clui59/);
  assert.match(htmlSource,/assets\/app\.css\?v=clui53/);
});
