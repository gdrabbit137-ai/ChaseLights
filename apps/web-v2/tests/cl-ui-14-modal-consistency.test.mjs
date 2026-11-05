// CL-UI-14: weather-modal consistency fixes + user-view UI optimization.
// The V1 shell (repo-root assets/app.js) has no DOM harness, so this suite
// combines extracted-function tests with source assertions (same approach as
// CL-UI-12 / CL-UI-13).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
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
  // CL-UI-20: the shared helpers now delegate separators to these two fns.
  'const listSep=()=>currentLang==="en"?", ":"、";',
  'const colonSep=()=>currentLang==="en"?": ":"：";',
  grab('const tempUnitLabel','function trMessage'),
  grab('function esc','const OPPORTUNITY_NEGATIVE_STATUS_KEYS'),
  grab('function localDateString','function selectedDateForSpot'),
  grab('function localNowMinutes','function v2IsToday'),
  grab('function v2IsToday','function v2RemainingHoursList'),
  grab('function v2RemainingHoursList','function v2ParseLocalStamp'),
  grab('function formatHourSegments','function v2ContractThreshold'),
  grab('const VIS_CAP_KM','function astroMissingHtml'),
  grab('// CL-UI-14/F1: the modal','function navigationTargetNote'),
  'return {formatTemp,esc,tzAbbrLabel,visibilityText,tempChipHtml,modalWindowKey,modalDayInfo,modalWindowSegment,modalHeadline,modalDayRow};'
].join('\n'));
const {formatTemp,esc,tzAbbrLabel,visibilityText,tempChipHtml,modalWindowKey,modalDayInfo,modalWindowSegment,modalHeadline,modalDayRow}=factory();

test('CL-UI-14 F1: modal window label is keyed to the same V2 day state as the rows',()=>{
  // Only a fully met day may be called "best".
  assert.equal(modalWindowKey('GUIDANCE_SATISFIED'),'best_window');
  // A day whose hours are mostly "not met" must NOT carry the best wording.
  assert.equal(modalWindowKey('UNFAVORABLE'),'modal_window_relative');
  assert.equal(modalWindowKey('NOT_EVALUABLE'),'modal_window_relative');
  // The wording exists in all three languages.
  for(const lang of ['zh-TW','en','ja']){
    assert.ok(new RegExp(`(\\n|\\s)${lang === 'zh-TW' ? "'zh-TW'" : lang === 'en' ? "'en'" : "'ja'"}:\\s*\\{`).test(appSource));
    assert.ok([...appSource.matchAll(/modal_window_relative:'/g)].length >= 3);
  }
});

// helper to build day info with a deterministic "now"
test('CL-UI-14 F1/F2: modal day hours use the card\u2019s remaining-hours source (CL-UI-12)',()=>{
  const today={local_date:'2026-11-02',good_hours:['00:00','05:56','17:00'],state:'GUIDANCE_SATISFIED'};
  const info=modalDayInfo(today,'Asia/Taipei',6*60); // now 06:00 spot-local
  assert.equal(info.hours,1);
  assert.equal(JSON.stringify(info.list),JSON.stringify(['17:00']));
  assert.equal(modalWindowSegment(info),'11/02 17:00');
  // Hours already past are never advertised (same rule as the card).
  const gone=modalDayInfo({local_date:'2026-11-02',good_hours:['05:56'],state:'GUIDANCE_SATISFIED'},'Asia/Taipei',6*60);
  assert.equal(gone.hours,0);
  // A future day keeps its full-day list.
  const future=modalDayInfo({local_date:'2030-01-01',good_hours:['00:00','01:00','02:00'],state:'GUIDANCE_SATISFIED'},'Asia/Taipei');
  assert.equal(future.hours,3);
  assert.equal(modalWindowSegment(future),'01/01 00:00\u201302:00');
  // Same-source wiring: the card (createSpotCard) and the modal day info both
  // consume v2EffectiveHours (the card through v2BestForSpot).
  const cardBlock=block('function createSpotCard','function distanceToSpotKm');
  assert.match(cardBlock,/v2BestForSpot\(v2PlaceData,spot\.timezone\)/);
  const bestBlock=grab('function v2BestForSpot','function v2PlaceForSpot');
  assert.match(bestBlock,/v2EffectiveHours\(day,tz\)/);
  const modalBlock=grab('function modalDayInfo','function modalWindowSegment');
  assert.match(modalBlock,/v2EffectiveHours\(day,tz\)/);
});

test('CL-UI-14 F2: modal summary is a 3-day overview with an honest none-fallback',()=>{
  const noHours={hours:0,list:[],state:'UNFAVORABLE',date:'2026-11-04'};
  const row=modalDayRow('後天',noHours);
  assert.match(row,/modal-day-none/);
  // CL-UI-21: the none wording carries the row's own day label.
  assert.match(row,/後天無建議時段/);
  assert.doesNotMatch(row,/最佳拍攝時段/);
  const met={hours:2,list:['17:00','18:00'],state:'GUIDANCE_SATISFIED',date:'2026-11-02'};
  const okRow=modalDayRow('今天',met);
  assert.match(okRow,/最佳拍攝時段/);
  assert.match(okRow,/符合時數 2/);
});

test('CL-UI-14 F1: a partially-met day is labelled "relatively better, still not met", never "best"',()=>{
  const partial={hours:2,list:['14:00','15:00'],state:'UNFAVORABLE',date:'2026-11-02'};
  const row=modalDayRow('今天',partial);
  assert.match(row,/相對較佳但仍未符/);
  assert.doesNotMatch(row,/最佳拍攝時段/);
});

test('CL-UI-14 F1/U1: headline answers "should I go today, and when"',()=>{
  const data={dayInfos:[
    {hours:1,list:['17:00'],state:'GUIDANCE_SATISFIED',date:'2026-11-02'},
    {hours:3,list:['00:00','01:00','02:00'],state:'GUIDANCE_SATISFIED',date:'2026-11-03'},
    {hours:0,list:[],state:'UNFAVORABLE',date:'2026-11-04'}
  ]};
  const headline=modalHeadline(data);
  assert.match(headline,/今天 11\/02 17:00 起還有 1 小時適合拍攝/);
  assert.match(headline,/明天 11\/03 00:00–02:00 條件更好（3 小時）/);
  // No suggestion at all → honest wording, never a bare dash.
  const none=modalHeadline({dayInfos:[
    {hours:0,list:[],state:'UNFAVORABLE',date:'2026-11-02'},
    {hours:0,list:[],state:'UNFAVORABLE',date:'2026-11-03'},
    {hours:0,list:[],state:'UNFAVORABLE',date:'2026-11-04'}
  ]});
  assert.match(none,/今天已無建議拍攝時段/);
  assert.doesNotMatch(none,/—/);
  // No bundle data → unknown wording, never a bare dash.
  assert.match(modalHeadline(null),/目前無法提供拍攝建議摘要/);
});

test('CL-UI-14 F3: missing astronomy gets an honest per-hour reason, never a bare dash',()=>{
  assert.equal(esc('x<'),'x&lt;');
  const rowBlock=grab('(spot.hourly_forecast||[])','decorateWeatherTimeline(spot');
  assert.match(rowBlock,/\$\{astro\|\|astroMissingHtml\(\)\}/);
  assert.match(rowBlock,/timeline-mobile-astro astro-missing/);
  for(const lang of ['zh-TW','en','ja']){
    assert.ok(new RegExp(`astro_missing:'`).test(appSource));
    assert.ok(appSource.includes(lang));
  }
  assert.ok(appSource.includes("astro_missing:'該時段無天文資料'"));
  assert.ok(appSource.includes("astro_missing:'No astronomy data for this hour'"));
  assert.ok(appSource.includes("astro_missing:'この時間帯の天文データなし'"));
});

test('CL-UI-14 F4: no bare-dash output — temp chip gets a tooltip, summary gets a sentence',()=>{
  assert.equal(formatTemp(null),'—');
  const emptyChip=tempChipHtml(null);
  assert.match(emptyChip,/title="氣溫資料暫缺"/);
  const okChip=tempChipHtml(21.4);
  assert.doesNotMatch(okChip,/title=/);
  assert.match(okChip,/21\.4°C/);
  // The old bare summary dash is gone: modal summary no longer renders
  // best_window with a legacy '—' value; it uses the sentence fallback.
  const modalBlock=block('function renderWeatherModal','function closeModal');
  assert.doesNotMatch(modalBlock,/modal-summary-window/);
  assert.match(modalBlock,/modal_window_none/);
});

test('CL-UI-14 F6: visibility at the data cap is labelled, not shown as a bare number',()=>{
  assert.match(visibilityText(24.1),/≥ 24 km（資料上限）/);
  assert.equal(visibilityText(12.5),'12.5 km');
  assert.equal(visibilityText(null),null);
  assert.equal(visibilityText('junk'),null);
  assert.ok(appSource.includes("vis_cap:'≥ 24 km（資料上限）'"));
  assert.ok(appSource.includes("vis_cap:'≥ 24 km (data cap)'"));
  assert.ok(appSource.includes("vis_cap:'≥ 24 km（データ上限）'"));
  const rowBlock=grab('(spot.hourly_forecast||[])','decorateWeatherTimeline(spot');
  assert.match(rowBlock,/\$\{visibilityText\(item\.visibility\)\?\?'—'\}/);
});

test('CL-UI-14 F7: a single timezone convention (GMT+8) across card and modal',()=>{
  assert.equal(tzAbbrLabel('CST'),'GMT+8');
  assert.equal(tzAbbrLabel('JST'),'GMT+9');
  assert.equal(tzAbbrLabel('GMT+8'),'GMT+8');
  // No other convention is ever rendered.
  assert.doesNotMatch(appSource,/'UTC\+8'/);
  assert.doesNotMatch(appSource,/title="[^"]*CST/);
  // CL-UI-15: the card list no longer renders a per-card timezone row (the
  // page header carries the unified GMT clock); tzAbbrLabel stays for the
  // header clock and the modal windows.
  assert.match(appSource,/function tzAbbrLabel\(/);
  const fmt=grab('function fmtWindow','function confidenceLabel');
  assert.match(fmt,/tzAbbrLabel\(tz\)/);
  assert.match(appSource,/clock card-timezone|'GMT\+8'/);
});

test('CL-UI-14 U2: status legend + plain-language tooltips above the table',()=>{
  const modalBlock=block('function renderWeatherModal','function closeModal');
  assert.match(modalBlock,/timeline-legend/);
  assert.match(modalBlock,/legend-ok/);
  assert.match(modalBlock,/legend-chance/);
  assert.match(modalBlock,/legend-bad/);
  // Professional values stay; tooltips add the plain-language meaning.
  for(const key of ['tip_cloud_base','tip_low_cloud','tip_wind','tip_vis']){
    for(const marker of [`'zh-TW'`,`'en'`,`'ja'`]){
      const section=appSource.indexOf(marker);
      const next=appSource.indexOf(marker,section+10);
      const span=appSource.slice(section,next>0?next:undefined);
      assert.ok(new RegExp(key+':').test(span),`${key} missing for ${marker}`);
    }
  }
});

test('CL-UI-14 U4: modal date switch re-evaluates the same source the cards use',()=>{
  const modalBlock=block('function renderWeatherModal','function closeModal');
  assert.match(modalBlock,/data-modal-day/);
  assert.match(modalBlock,/switchDay\(btn\.dataset\.modalDay\)/);
  assert.match(modalBlock,/renderWeatherModal\(spot,latest\?getMetric\(latest\):summaryMetric\)/);
  // Mobile close button exists and is pinned/styled.
  const initBlock=appSource.slice(appSource.lastIndexOf('function initializeApp'));
  assert.match(initBlock,/modal-close-mobile/);
  assert.match(initBlock,/closeModal\(\)/);
  assert.match(cssSource,/modal-close-mobile-btn/);
  assert.match(cssSource,/max-width:640px[\s\S]*#modal-close-mobile\{display:block/);
});

test('CL-UI-14 U3: mobile usability — sticky time column, larger targets, summary first',()=>{
  assert.match(cssSource,/\.terminal-table th:first-child,\.terminal-table td:first-child\{position:sticky;left:0/);
  assert.match(cssSource,/max-width:640px[\s\S]*?\.modal-day-btn\{min-height:40px/);
  assert.match(cssSource,/max-width:640px[\s\S]*?\.timeline-mobile-time\{font-size:\.92rem\}/);
  // The summary (headline + 3-day overview) renders before the hourly table.
  const modalBlock=block('function renderWeatherModal','function closeModal');
  assert.ok(modalBlock.indexOf('modal-headline')>-1);
  assert.ok(modalBlock.indexOf('modal-overview')>-1);
  assert.ok(modalBlock.indexOf('modal-headline')<modalBlock.indexOf('timeline-head'));
});

test('CL-UI-14 U5: all new copy exists in all three languages and carries no internal labels',()=>{
  const keys=['modal_window_none','modal_window_relative','astro_missing','temp_unavailable','vis_cap','legend_title','modal_headline_now','modal_headline_none_today','modal_headline_better','modal_headline_unknown'];
  for(const key of keys){
    const count=[...appSource.matchAll(new RegExp(`(?:^|[^\\w-])${key}:`).source,'g')].length;
    // one occurrence per language dictionary (zh-TW, en, ja)
    const occurrences=(appSource.match(new RegExp(`${key}:'`,'g'))||[]).length;
    assert.ok(occurrences>=3,`${key} not present in all three languages (${occurrences})`);
  }
  const newCopy=grab("modal_window_none:'{day}無建議時段'","modal_headline_unknown:'現在、撮影サマリーを表示できません'");
  assert.doesNotMatch(newCopy,/internal|provisional|待證據|研究中/i);
});
