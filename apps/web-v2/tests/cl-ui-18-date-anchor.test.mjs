// CL-UI-18: date-anchor re-anchoring + card/modal minor fixes.
//
// Major: at 03:21 spot-local time the bundle's day rows are still anchored to
// the bundle generation date, so the homepage "今天" tab and the modal summary
// described 11/04 ("今天 11/04 17:00 起還有 1 小時" — 10 hours in the past)
// while the card's next-window had already re-anchored to 11/05 05:00. All V2
// consumers now resolve the day row BY DATE (spot wall clock), past days carry
// zero actionable hours, and the modal labels a stale row as 昨天.
//
// The V1 shell has no DOM harness, so this suite combines extracted-function
// tests (run for real), a fixed-clock 03:21 simulation (FakeDate shadowing the
// Date global inside the evaluated source), and source assertions.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));

// ---------------------------------------------------------------------------
// Part A: pure helpers under the REAL clock (scenario dates derived from it).
// ---------------------------------------------------------------------------
const factoryA=new Function([
  grab('function localDateString','function selectedDateForSpot'),
  grab('function localNowMinutes','function v2IsToday'),
  grab('function v2IsToday','function v2RemainingHoursList'),
  grab('function v2RemainingHoursList','function v2NextWindowLocal'),
  grab('function v2NextWindowLocal','function v2BestForSpot'),
  grab('function v2DayLabel','function shortDateStamp'),
  grab('function shortDateStamp','function v2OpportunityById'),
  'const d=()=>({eval2_d0:\'今天\',eval2_d1:\'明天\',eval2_d2:\'後天\',eval2_d_past:\'昨天\'});',
  'return {localDateString,v2DayRel,v2DayForOffset,v2EffectiveHours,v2DayLabel,shortDateStamp};'
].join('\n'));
const {localDateString,v2DayRel,v2DayForOffset,v2EffectiveHours,v2DayLabel,shortDateStamp}=factoryA();

const tz='Asia/Taipei';
const D=(off)=>localDateString(tz,off);
const day=(date,hours)=>({local_date:date,good_hours:hours});

test('CL-UI-18 A1: day rows resolve by spot-local wall clock, not bundle index',()=>{
  const rows=[day(D(-1),['17:00']),day(D(0),['05:00']),day(D(1),['16:00'])];
  // The reported bug: days[0] is yesterday after midnight in the spot's zone.
  assert.equal(v2DayForOffset({days:rows},0,tz).local_date,D(0));
  assert.equal(v2DayForOffset({days:rows},1,tz).local_date,D(1));
  assert.equal(v2DayRel(D(-1),tz),'past');
  assert.equal(v2DayRel(D(0),tz),'today');
  assert.equal(v2DayRel(D(1),tz),'future');
});

test('CL-UI-18 A2: a past day row has zero actionable hours (never "還有")',()=>{
  const rows=[day(D(-1),['17:00','18:00']),day(D(0),['05:00'])];
  assert.deepEqual(v2EffectiveHours(rows[0],tz),[],'yesterday must not be described as remaining hours');
  // A fully stale bundle (no row matches any target) fails closed: the
  // index-fallback row is past, so its hours are history too.
  const stale=[day(D(-2),['09:00']),day(D(-1),['17:00'])];
  const picked=v2DayForOffset({days:stale},0,tz);
  assert.ok(picked);
  assert.deepEqual(v2EffectiveHours(picked,tz),[]);
  // A future day keeps its full list.
  assert.deepEqual(v2EffectiveHours(day(D(2),['16:00']),tz),['16:00']);
});

test('CL-UI-18 A3: modal day labels follow the wall clock (stale row = 昨天)',()=>{
  const rows=[day(D(-1),['17:00']),day(D(0),['05:00']),day(D(1),['16:00'])];
  assert.equal(v2DayLabel(rows[0].local_date,tz,0),'昨天');
  assert.equal(v2DayLabel(rows[1].local_date,tz,1),'今天');
  assert.equal(v2DayLabel(rows[2].local_date,tz,2),'明天');
  // No parseable date → positional fallback, never a bare dash.
  assert.equal(v2DayLabel('',tz,1),'明天');
});

test('CL-UI-18 A4: user-facing stamps use the 11/05 page-header convention',()=>{
  assert.equal(shortDateStamp('2026-11-05 05:00'),'11/05 05:00');
  assert.equal(shortDateStamp('2026-11-05'),'11/05');
  assert.equal(shortDateStamp('05:00'),'05:00');
});

// ---------------------------------------------------------------------------
// Part B: fixed-clock 03:21 simulation (FakeDate shadows the Date global).
// ---------------------------------------------------------------------------
// FIXED = 2026-11-04 19:21 UTC = Taipei 2026-11-05 03:21 (the reported moment).
const FIXED=Date.UTC(2026,10,4,19,21,0);
class FakeDate extends Date{
  constructor(...args){args.length?super(...args):super(FIXED);}
  static now(){return FIXED;}
}
const BUNDLE_DAY_PAST='2026-11-04';
const SPOT_TODAY='2026-11-05';
const dayRow=(date,good)=>({local_date:date,state:good.length?'GUIDANCE_SATISFIED':'UNFAVORABLE',good_hours:good,hours:good.map(h=>({local:h,status:'GUIDANCE_SATISFIED',conditions:[]})),hour_counts:{GUIDANCE_SATISFIED:good.length}});

test('CL-UI-18 B1: 03:21 modal summary — headline never cites the past window',()=>{
  const grabModal=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));
  const factoryB=new Function('Date',[
    "const DAY_KEYS=['today','tomorrow','after_tomorrow','day3','day4','day5','day6'];",
    grabModal('function localDateString','function selectedDateForSpot'),
    grabModal('function localNowMinutes','function v2IsToday'),
    grabModal('function v2IsToday','function v2RemainingHoursList'),
    grabModal('function v2RemainingHoursList','function v2NextWindowLocal'),
    grabModal('function v2NextWindowLocal','function v2BestForSpot'),
    grabModal('function modalDayInfo','function modalDayRow'),
    grabModal('function v2PlaceForSpot','function v2SpotDayVerdict'),
    'const formatHourSegments=(l)=>(l||[]).join(\'、\');',
    'const d=()=>({eval2_d0:\'今天\',eval2_d1:\'明天\',eval2_d2:\'後天\',eval2_d_past:\'昨天\',modal_headline_now:\'{day} {window} 起還有 {n} 小時適合拍攝\',modal_headline_none_today:\'{day}已無建議拍攝時段\',modal_headline_better:\'；{day} {window} 條件更好（{n} 小時）\',modal_headline_unknown:\'目前無法提供拍攝建議摘要\'});',
    'let v2EvalBundle={places:[]};',
    'return {modalSummaryData,modalHeadline,v2NextWindowLocal,v2LocalNow,shortDateStamp,setBundle:(v)=>{v2EvalBundle=v;}};'
  ].join('\n'));
  const {modalSummaryData,modalHeadline,v2NextWindowLocal,v2LocalNow,shortDateStamp,setBundle}=factoryB(FakeDate);
  // Sanity: the fake clock really reads 03:21 on 11/05 in Taipei.
  const now=v2LocalNow(tz);
  assert.deepEqual(now,{date:SPOT_TODAY,minutes:3*60+21},'simulation clock is 03:21 on 11/05');
  const summarySpot={spot_id:'tw-1',timezone:tz};
  const opp={opportunity_id:'sunset_cloud',live:{},days:[
    dayRow(BUNDLE_DAY_PAST,['17:00']),   // bundle was generated on 11/04
    dayRow(SPOT_TODAY,['05:00'])
  ]};
  setBundle({places:[{place_id:'tw-1',opportunities:[opp]}]});
  const data=modalSummaryData(summarySpot,'sunset_cloud');
  // Day 0 is re-anchored to the wall-clock day, not bundle index 0.
  assert.equal(data.dayInfos[0].date,SPOT_TODAY);
  assert.equal(data.dayInfos[0].hours,1,'05:00 today is still ahead at 03:21');
  assert.equal(data.dayInfos[0].list[0],'05:00');
  const headline=modalHeadline(data);
  assert.ok(headline.includes('05:00'),'headline cites the real remaining window');
  assert.ok(headline.includes('還有 1 小時'),'the remaining-hours phrasing attaches to the real remaining list');
  assert.ok(!headline.includes('17:00'),'the past 11/04 17:00 window is never quoted');
  assert.ok(!headline.includes('11/04'),'no yesterday date leaks into the summary');
  // Next window keeps the page-header 11/05 convention.
  const nextLocal=v2NextWindowLocal(opp.days,now,'2026-11-04 17:00');
  assert.equal(shortDateStamp(nextLocal),'11/05 05:00');
});

test('CL-UI-18 B2: 03:21 homepage "today" tab — card evaluates 11/05, not the bundle\'s 11/04',()=>{
  const byId={};const store={};
  class FakeEl{
    constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.style={};this.className='';this._html='';this._text='';this._attrs={};this.parentNode=null;}
    get innerHTML(){return this._html;}
    set innerHTML(v){this._html=String(v);this.children=[];}
    get textContent(){return this._text;}
    set textContent(v){this._text=String(v);}
    setAttribute(k,v){this._attrs[k]=v;}
    getAttribute(k){return this._attrs[k];}
    appendChild(c){c.parentNode=this;this.children.push(c);return c;}
    append(...cs){cs.forEach(c=>{c.parentNode=this;this.children.push(c);});}
    querySelector(sel){return this._q(sel,true);}
    _q(sel,allowFallback){
      const raw=String(sel);sel=raw.replace(/^:scope\s*>\s*/,'').trim();
      for(const c of this.children){const hit=matchSel(c,sel);if(hit)return hit;const f=c._q(sel,false);if(f)return f;}
      if(allowFallback&&(this._html||this._autoQuery)){
        const tag=(/[\w-]+$/.exec(sel)||['div'])[0];
        this._fallback=this._fallback||{};
        if(!this._fallback[sel]){const e=new FakeEl(tag);e._autoQuery=true;this._fallback[sel]=e;}
        return this._fallback[sel];
      }
      return null;
    }
    querySelectorAll(sel){const out=[];const walk=n=>{n.children.forEach(c=>{if(matchSel(c,sel))out.push(c);walk(c);});};walk(this);return out;}
    closest(){return null;}
    insertAdjacentHTML(pos,html){this._html=(pos==='afterbegin'?html+this._html:this._html+html);this.children.push(new FakeEl('#frag'));}
    addEventListener(){}
    focus(){}
    classList={add:()=>{},remove:()=>{},toggle:()=>{},contains:()=>false};
  }
  function matchSel(el,sel){
    if(sel.startsWith('#'))return el.id===sel.slice(1);
    if(sel.startsWith('.'))return (el.className||'').split(/\s+/).includes(sel.slice(1));
    if(sel.startsWith('[')){const m=/\[data-([\w-]+)(?:="([^"]*)")?\]/.exec(sel);return m?el.dataset[m[1]]===undefined?false:(m[2]===undefined?el.dataset[m[1]]!==undefined:el.dataset[m[1]]===m[2]):false;}
    return el.tag===sel;
  }
  const documentFake={
    getElementById:(id)=>{if(!byId[id])byId[id]=new FakeEl('#'+id);return byId[id];},
    createElement:(t)=>new FakeEl(t),
    createTextNode:(t)=>{const e=new FakeEl('#text');e.textContent=t;return e;},
    querySelector:()=>null,querySelectorAll:()=>[],
    addEventListener:()=>{},
    body:new FakeEl('body'),documentElement:new FakeEl('html'),head:new FakeEl('head'),
    activeElement:null,title:'',visibilityState:'visible',
  };
  const winFake={addEventListener:()=>{},matchMedia:()=>({matches:false,addListener:()=>{},addEventListener:()=>{}}),location:{href:'https://chaselights.app/',pathname:'/',search:''},scrollTo:()=>{},innerWidth:1280,navigator,open:()=>null};
  const storageFake=()=>({getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=String(v);},removeItem:()=>{},clear:()=>{},key:()=>null,get length(){return 0;}});
  const spot={
    spot_id:'tw-1',lat:24,lon:121,n:0,category:'mountain',timezone:tz,admin_areas:['花蓮縣'],
    name_i18n:{'zh-TW':'測試點'},name_local:'Test',
    daily:[
      {date:BUNDLE_DAY_PAST,all:{score:40,cloud_base_agl:1000,temp:15,no_viable_opportunity:true}},
      {date:SPOT_TODAY,all:{score:60,cloud_base_agl:1000,temp:14,opportunity_id:'sunset_cloud',opportunity_name:'雲海',theme:'sunset_cloud',indicator_key:'',factors:[]}}
    ],
    opportunities:[{opportunity_id:'sunset_cloud',name_zh:'雲海'}],
  };
  const bundle={places:[{place_id:'tw-1',opportunities:[{opportunity_id:'sunset_cloud',name_i18n:{'zh-TW':'雲海'},days:[dayRow(BUNDLE_DAY_PAST,['17:00']),dayRow(SPOT_TODAY,['05:00'])]}]}]};
  const hook=';return {filterAndRender,setDay:(k)=>{currentDayFilter=k;},setSpots:(v)=>{currentSpots=v;},setData:(v)=>{currentData=v;},setBundle:(v)=>{v2EvalBundle=v;},container:()=>document.getElementById(\'spots-container\'),spotName};';
  const fn=new Function('document','window','localStorage','sessionStorage','navigator','location','fetch','alert','confirm','requestAnimationFrame','IntersectionObserver','MutationObserver','ResizeObserver','getComputedStyle','matchMedia','Date',`${appSource}\n${hook}`);
  const api=fn(documentFake,winFake,storageFake(),{getItem:()=>null,setItem:()=>{},removeItem:()=>{},clear:()=>{}},{getItem:()=>null,setItem:()=>{},removeItem:()=>{},clear:()=>{}},navigator,{href:'https://chaselights.app/',pathname:'/',search:''},()=>Promise.reject(new Error('sim')),()=>{},()=>()=>{},class{},class{},class{},()=>({getPropertyValue:()=>''}),()=>({matches:false}),FakeDate);
  api.setData({spots:[spot],updated_at:'sim',region:'tw'});
  api.setSpots([spot]);
  api.setBundle(bundle);
  api.setDay('today');
  api.filterAndRender();
  const c=api.container();
  const cards=c.children.filter(x=>x.className==='card');
  assert.equal(cards.length,1,'the 11/05 05:00 hour makes the spot viable on the today tab at 03:21');
  const html=cards[0]._html;
  assert.ok(html.includes('符合時數 1'),'card counts the re-anchored today hours');
  assert.ok(html.includes('05:00'),'card window is the 11/05 05:00 block');
  assert.ok(!html.includes('17:00'),'the stale 11/04 17:00 window never renders');
  assert.ok(!html.includes('2026-11-05'),'no raw ISO date — page-header 11/05 convention only');
  // A viable card renders its remaining-hours window ('05:00'); the dated
  // "下一個符合時段" row only appears on the no-remaining-hours branch (B1
  // covers its short-date form there).
  assert.ok(!html.includes('建議改期'),'misleading "改期" copy removed');
});

// ---------------------------------------------------------------------------
// Part C: source-level assertions for the minor batch.
// ---------------------------------------------------------------------------
test('CL-UI-18 C1: i18n — yesterday label in all three dictionaries; 改期 copy removed',()=>{
  for(const lang of ['zh-TW','en','ja'])assert.ok(appSource.includes(lang));
  assert.ok(appSource.includes("eval2_d_past:'昨天'"));
  assert.ok(appSource.includes("eval2_d_past:'Yesterday'"));
  assert.ok(appSource.includes("eval2_d_past:'昨日'"));
  assert.ok(!appSource.includes('建議改期'),'the misleading postponement copy is gone');
});

test('CL-UI-18 C2: modal summary consumes date-anchored day rows and labels',()=>{
  const modalBlock=grab('function modalSummaryData','function modalDayRow');
  assert.match(modalBlock,/v2DayForOffset\(opp,i,tz\)/);
  assert.match(modalBlock,/v2DayLabel\(info&&info\.date,tz,i\)/);
  assert.match(appSource,/const labels=data\.labels\|\|\[d\(\)\.eval2_d0/);
});

test('CL-UI-18 C3: cards and sort consume date-anchored day rows',()=>{
  const bestBlock=grab('function v2BestForSpot','function v2PlaceForSpot');
  assert.match(bestBlock,/v2DayForOffset\(o,dayIndex,tz\)/);
  const sortBlock=grab('function v2HoursSortValue','function v2DayHtml');
  assert.match(sortBlock,/v2DayForOffset\(o,dayIndex,spot\.timezone\)/);
  assert.match(sortBlock,/v2DayRel\(day\.local_date,spot\.timezone\)==='past'/);
});

test('CL-UI-18 C4: temp chip omitted when there is no value',()=>{
  const cardBlock=grab('function createSpotCard','function distanceToSpotKm');
  assert.match(cardBlock,/formatTemp\(metric\.temp\)==='—'\?''/);
});

test('CL-UI-18 C5: navigation tool unified; bare-coords destination carries the spot name',()=>{
  const navBlock=grab('function navigationToolHtml','function createSpotCard');
  assert.match(navBlock,/data-navigation-mode="verified"/);
  assert.match(navBlock,/labelNote=`\$\{note\?note\+' · ':''\}\$\{spotName\(spot\)\}/);
  assert.match(navBlock,/toolButtonInner\(d\(\)\.map_link\)/);
});

test('CL-UI-18 C6: astro missing is a compact marker + one legend note; badge column widened',()=>{
  const rowBlock=grab('(spot.hourly_forecast||[])','decorateWeatherTimeline(spot');
  assert.match(rowBlock,/\$\{astro\|\|astroMissingHtml\(\)\}/);
  assert.match(rowBlock,/astroMissingRows\+\+/);
  assert.match(rowBlock,/timeline-legend/);
  assert.match(cssSource,/terminal-table td:first-child \{ min-width: 96px; \}/);
  assert.match(cssSource,/\.v2-chip-ok\{color:#3fb950;font-weight:600;white-space:nowrap\}/);
});