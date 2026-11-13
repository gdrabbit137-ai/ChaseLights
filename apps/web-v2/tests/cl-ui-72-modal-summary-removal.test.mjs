// CL-UI-72 (owner ruling): the weather-forecast modal's summary sentence
// (「今天 11/13 19:00 起還有 1 小時適合拍攝；後天…條件更好（6 小時）」)
// and the blue 「🎯 下一個符合時段」 banner were hard to read and duplicate
// the date tabs + per-day rows — the whole block is removed. These pins keep
// it removed (source-level: markup, helper, i18n keys, CSS) while asserting
// the surviving surface (date switch + per-day rows) is untouched.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const root=new URL('../../..',import.meta.url);
const appSource=readFileSync(new URL('assets/app.js',root),'utf8');
const cssSource=readFileSync(new URL('assets/app.css',root),'utf8');
const htmlSource=readFileSync(new URL('index.html',root),'utf8');

const block=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,appSource.indexOf(start))
);
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));

test('CL-UI-72 (1): modal renders day switch first — no headline div, no next-window banner',()=>{
  const renderBlock=block('function renderWeatherModal','function closeModal');
  assert.ok(!renderBlock.includes('modal-headline'),'summary sentence removed');
  assert.ok(!renderBlock.includes('modal-next-window'),'blue banner removed');
  // The day switch is now the first element in #modal-summary.
  assert.match(renderBlock,/modal-summary'\)\.innerHTML=`<div class="modal-day-switch"/);
  // Per-day rows and the modal-subtitle hourly table survive.
  assert.ok(renderBlock.includes('modal-overview'));
  assert.ok(appSource.includes('modal_subtitle'));
});

test('CL-UI-72 (2): modalHeadline helper + modal_headline_* i18n keys retired',()=>{
  assert.ok(!appSource.includes('modalHeadline'));
  for(const key of ['modal_headline_now','modal_headline_none_today','modal_headline_better','modal_headline_unknown']){
    assert.ok(!appSource.includes(`${key}:`),`${key} removed from all three dictionaries`);
  }
});

test('CL-UI-72 (3): CSS rules for the removed block are gone',()=>{
  assert.ok(!cssSource.includes('.modal-headline'));
  assert.ok(!cssSource.includes('.modal-next-window'));
});

test('CL-UI-72 (4): the daily strip keeps its concise two-line format',()=>{
  // Owner convention: short words, no long sentence stacking. CL-UI-75
  // (owner ruling) retired the 🎯 next-window in-cell badge at every
  // breakpoint — the compact cell copy (✓n hours badge, ✗short-reason,
  // abbreviated 06–14 window) is the only in-cell info now.
  const strip=grab('function v2DayStripHtml','// CL-UI-64: top');
  assert.ok(strip.includes('eval2_hours'));
  assert.ok(strip.includes('v2ShortReasonWord'));
  assert.ok(!strip.includes('v2-strip-next') && !strip.includes('🎯'),
    'CL-UI-75: the 🎯 next-window badge is retired from the strip');
  assert.ok(!/modal_headline/.test(strip));
});

test('CL-UI-72 (5): cache-bust bumped in the same commit',()=>{
  assert.match(htmlSource,/assets\/app\.js\?v=clui86/);
  assert.match(htmlSource,/assets\/app\.css\?v=clui86/);
});
