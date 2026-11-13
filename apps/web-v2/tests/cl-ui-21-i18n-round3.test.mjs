// CL-UI-21: round-3 i18n residual fixes. The headline verification below is
// DOM-level in the sense that it renders the exact string the modal injects
// into .modal-headline (esc(modalHeadline(summaryData))) — the actual rendered
// text, not a source-string pin. Live headless evidence is captured separately
// in the ticket report.
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
  'const colonSep=()=>currentLang==="en"?": ":"：";',
  'const slashSep=()=>currentLang==="en"?" / ":"／";',
  grab('function esc','const OPPORTUNITY_NEGATIVE_STATUS_KEYS'),
  grab('function localDateString','function selectedDateForSpot'),
  grab('function localNowMinutes','function v2IsToday'),
  grab('function v2IsToday','function v2RemainingHoursList'),
  grab('function v2RemainingHoursList','function v2ParseLocalStamp'),
  grab('function formatHourSegments','function v2ContractThreshold'),
  grab('// CL-UI-14/F1: the modal','function navigationTargetNote'),
  'return {esc,modalDayInfo,modalWindowSegment,modalDayRow,v2DayLabel,shortDateStamp};'
].join('\n'));
const {esc,modalDayInfo,modalWindowSegment,modalDayRow,v2DayLabel,shortDateStamp}=factory();

const setLang=(lang)=>{ /* dict is closed over; factory rebuild instead */ };
const buildFor=(lang)=>{
  const f=new Function([
    block('const i18nDict','const categoryKeys'),
    `let currentLang='${lang}',currentTempUnit='C',currentRegion='tw',currentDayFilter='today';`,
    'const d=()=>i18nDict[currentLang]||i18nDict["zh-TW"];',
    'const listSep=()=>currentLang==="en"?", ":"、";',
    'const colonSep=()=>currentLang==="en"?": ":"：";',
    'const slashSep=()=>currentLang==="en"?" / ":"／";',
    grab('function esc','const OPPORTUNITY_NEGATIVE_STATUS_KEYS'),
    grab('function localDateString','function selectedDateForSpot'),
    grab('function localNowMinutes','function v2IsToday'),
    grab('function v2IsToday','function v2RemainingHoursList'),
    grab('function v2RemainingHoursList','function v2ParseLocalStamp'),
    grab('function formatHourSegments','function v2ContractThreshold'),
    grab('// CL-UI-14/F1: the modal','function navigationTargetNote'),
    'return {esc,modalDayInfo,modalWindowSegment,modalDayRow,v2DayLabel,shortDateStamp};'
  ].join('\n'));
  return f();
};

// CL-UI-34: bundle day rows must follow the real wall clock — the app's
// v2DayLabel/v2IsToday vocabulary anchors to the spot's local now (CL-UI-18),
// so hardcoded 2026-11-0X fixtures go stale the moment the clock crosses
// midnight. Derive today/today+1/today+2 with the same en-CA formatToParts
// Asia/Taipei local-date logic as assets/app.js localDateString(). The
// nowOverride=10*60 (10:00 spot-local) in each call keeps the hour list
// deterministic; only the date labels follow the clock.
const FIXTZ='Asia/Taipei';
const fixLocalDate=(offsetDays=0)=>{
  const parts=new Intl.DateTimeFormat('en-CA',{timeZone:FIXTZ,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
  const values=Object.fromEntries(parts.map(p=>[p.type,p.value]));
  const base=new Date(Date.UTC(Number(values.year),Number(values.month)-1,Number(values.day)+offsetDays));
  return `${base.getUTCFullYear()}-${String(base.getUTCMonth()+1).padStart(2,'0')}-${String(base.getUTCDate()).padStart(2,'0')}`;
};
const D0=fixLocalDate(0),D1=fixLocalDate(1),D2=fixLocalDate(2);
// Deterministic bundle day rows for D0 (Today) with one remaining hour.
const days=[D0,D1,D2].map((d)=>({local_date:d,good_hours:[],state:'UNFAVORABLE'}));
days[0]={local_date:D0,good_hours:['17:00'],state:'GUIDANCE_SATISFIED'};
const summary=(f,tz,now)=>{
  const infos=[0,1,2].map(i=>f.modalDayInfo(days[i],tz,now));
  const labels=infos.map((info,i)=>f.v2DayLabel(info&&info.date,tz,i));
  return {dayInfos:infos,labels};
};

test('CL-UI-72: the modal headline is retired — day rows still render the trilingual day vocabulary',()=>{
  // The old A1 pin verified the headline sentence; CL-UI-72 removed it.
  // The per-day row wording (the surviving surface) must still localize.
  const en=buildFor('en');
  const info=en.modalDayInfo(days[0],'Asia/Taipei',10*60); // 10:00 spot-local
  const rowHtml=en.modalDayRow(en.v2DayLabel(info.date,'Asia/Taipei',0),info);
  assert.ok(rowHtml.includes('qualifying hours'),'en row carries the hours vocabulary');
  const zh=buildFor('zh-TW');
  const zhRow=zh.modalDayRow(zh.v2DayLabel(zh.modalDayInfo(days[0],'Asia/Taipei',10*60).date,'Asia/Taipei',0),zh.modalDayInfo(days[0],'Asia/Taipei',10*60));
  assert.ok(zhRow.includes('符合時數'),'zh-TW row carries the hours vocabulary');
});

test('CL-UI-21 B2: day-tab none rows carry the selected date\u2019s day vocabulary (en not "today")',()=>{
  const en=buildFor('en');
  const tomorrow={local_date:D1,good_hours:[],state:'UNFAVORABLE'};
  const info=en.modalDayInfo(tomorrow,'Asia/Taipei',10*60);
  const label=en.v2DayLabel(info.date,'Asia/Taipei',1);
  assert.equal(label,'Tomorrow');
  const rowHtml=en.modalDayRow(label,info);
  assert.ok(rowHtml.includes('no suggested time'));
  assert.ok(!rowHtml.includes('No suggested time today'));
});

test('CL-UI-21 B2: v2 none-copy follows the day filter in all three languages',()=>{
  for(const [lang,today,tmrw,after] of [
    ['en','No qualifying subject today','No qualifying subject tomorrow','No qualifying subject day after'],
    ['zh-TW','本日無符合題材','明日無符合題材','後日無符合題材'],
    ['ja','本日に適したテーマなし','明日に適したテーマなし','明後日に適したテーマなし'],
  ]){
    assert.ok(appSource.includes(`v2_none_today:'${today}`),lang+' today key');
    assert.ok(appSource.includes(`v2_none_tomorrow:'${tmrw}`),lang+' tomorrow key');
    assert.ok(appSource.includes(`v2_none_after:'${after}`),lang+' day-after key');
  }
  assert.ok(appSource.includes("const v2NoneSubjectKey=()=>currentDayFilter==='tomorrow'?'v2_none_tomorrow':currentDayFilter==='after_tomorrow'?'v2_none_after':isFarDay(currentDayFilter)?'v2_none_far':'v2_none_today';"));
  assert.ok(appSource.includes("${esc(v2Best.state==='NOT_EVALUABLE'?d().eval2_unk:d()[v2NoneSubjectKey()])}"));
});

test('CL-UI-21 C3: no full-width separators remain in en rendering paths',()=>{
  // guide-label colon sites use the language-aware separator
  for(const key of ['guide_required','guide_boosters','guide_penalties','guide_confidence','guide_viewpoint','guide_time','guide_season']){
    const re=new RegExp(`\\$\\{esc\\(d\\(\\)\\.${key}\\)\\}：`);
    assert.ok(!re.test(appSource),key+' still hardcodes ：');
  }
  assert.ok(appSource.includes('${esc(d().guide_required)}${colonSep()}'));
  // v2-group labels too (3 sites)
  assert.ok(appSource.split('${esc(d().guide_required)}${colonSep()}').length>=3);
  assert.ok(!appSource.includes("${esc(viewpoints.join('／'))}"));
  assert.ok(appSource.includes("${esc(viewpoints.join(slashSep()))}"));
  // live reference-hour stamp uses parens() (en half-width) + short stamp
  assert.ok(appSource.includes('div.textContent=line+parens(shortDateStamp(refH.local));'));
});

test('CL-UI-21 D4: place-modal now/next lines re-anchor to spot-local day vocabulary + 11/04 15:00 stamp',()=>{
  // CL-UI-67 (owner ruling): the standalone now/next rows are gone — the
  // strip is self-explaining and the next window rides on the first
  // qualifying cell's hover title. The 15:00 stamp format contract survives:
  // the next window is still re-anchored via v2NextWindowLocal and stamped
  // from the validated nextLocal instead of the raw bundle value.
  assert.ok(!appSource.includes('const nowLabel=v2DayLabel(nowLocal.slice(0,10)'),
    'the standalone now row must stay removed');
  assert.match(appSource,/\$\{d\(\)\.v2_next_window\}\$\{nextWindowStamp\(nextLocal,spot\.timezone\)\}/);
});

test('CL-UI-21 F6: provisional map link title is localized and short',()=>{
  assert.ok(appSource.includes("map_link_approx:'📍 Map (approximate pin)'"));
  assert.ok(appSource.includes("map_link_approx:'📍 地圖（概略座標）'"));
  assert.ok(appSource.includes("map_link_approx:'📍 地図（概略座標）'"));
  assert.ok(appSource.includes('${toolButtonAttrs(d().map_link_approx)}'));
  assert.ok(!appSource.includes('provisional-map-pin"${toolButtonAttrs(d().map_link,note)}'));
  assert.ok(!appSource.includes('toolButtonAttrs(d().map_link,note)'));
});

test('CL-UI-21 G1: app.js is cache-busted from index.html (CL-UI-20 root cause)',()=>{
  const index=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
  assert.ok(/<script src="\.\/assets\/app\.js\?v=[^"]+"><\/script>/.test(index));
  assert.ok(/<link rel="stylesheet" href="\.\/assets\/app\.css\?v=[^"]+"/.test(index));
});
