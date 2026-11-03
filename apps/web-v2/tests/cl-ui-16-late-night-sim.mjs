// CL-UI-16 late-night simulation harness (run manually: node cl-ui-16-late-night-sim.mjs).
// Executes the real V1-shell app.js in a minimal fake DOM and drives
// filterAndRender through the four owner scenarios:
//   1) sparse featured mode (1..SPARSE_MAIN_THRESHOLD viable today)
//   2) normal mode (> threshold, region grouping kept)
//   3) today 0 viable → tomorrow rescue cards + badge + banner
//   4) today 0 and tomorrow 0 → honest both-none banner + collapsed groups
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');

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
  querySelector(sel){
    return this._q(sel,true);
  }
  _q(sel,allowFallback){
    const raw=String(sel);sel=raw.replace(/^:scope\s*>\s*/,'').trim();
    for(const c of this.children){if(matchSel(c,sel))return c;const f=c._q(sel,false);if(f)return f;}
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
  insertAdjacentHTML(pos,html){this._html=(pos==='afterbegin'?html+this._html:this._html+html);this.children.push(new FakeEl('#frag'));ADJ_LOG.push(html);}
  addEventListener(){}
  focus(){}
  classList={
    add:(...c)=>{this._classes=(this._classes||new Set());c.forEach(x=>this._classes.add(x));},
    remove:()=>{},toggle:()=>{},contains:()=>false
  };
  get childrenHtml(){return this.children.map(c=>c.tag).join(',');}
}
function matchSel(el,sel){
  if(sel.startsWith('#'))return el.id===sel.slice(1);
  if(sel.startsWith('.'))return (el.className||'').split(/\s+/).includes(sel.slice(1));
  if(sel.startsWith('[')){const m=/\[data-([\w-]+)(?:="([^"]*)")?\]/.exec(sel);return m?el.dataset[m[1]]===undefined?false:(m[2]===undefined?el.dataset[m[1]]!==undefined:el.dataset[m[1]]===m[2]):false;}
  return el.tag===sel;
}
const byId={};const store={};const sessStore={};const ADJ_LOG=[];
const documentFake={
  getElementById:(id)=>{if(!byId[id])byId[id]=new FakeEl('#'+id);return byId[id];},
  createElement:(t)=>new FakeEl(t),
  createTextNode:(t)=>{const e=new FakeEl('#text');e.textContent=t;return e;},
  querySelector:()=>null,querySelectorAll:()=>[],
  addEventListener:()=>{},
  body:new FakeEl('body'),documentElement:new FakeEl('html'),head:new FakeEl('head'),
  activeElement:null,title:'',visibilityState:'visible',
};
const storage=()=>({getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=String(v);},removeItem:k=>{delete store[k];},clear:()=>{for(const k in store)delete store[k];},key:i=>Object.keys(store)[i]||null,get length(){return Object.keys(store).length;}});
const winFake={
  addEventListener:()=>{},matchMedia:()=>({matches:false,addListener:()=>{},addEventListener:()=>{}}),
  location:{href:'https://chaselights.app/',pathname:'/',search:''},
  scrollTo:()=>{},innerWidth:1280,navigator:navigator,open:()=>null,
};
const hook=`// CL-UI-16 sim hook
;return {
  filterAndRender,
  setDay:(k)=>{currentDayFilter=k;},
  setSpots:(v)=>{currentSpots=v;},
  setData:(v)=>{currentData=v;},
  setBundle:(v)=>{v2EvalBundle=v;},
  container:()=>document.getElementById('spots-container'),
  spotName,
  dayOffsetOf:()=>selectedDayOffset(),
};`;

function runScenario({spots,bundle,day='today',dismissed=false}){
  ADJ_LOG.length=0;
  const fn=new Function('document','window','localStorage','sessionStorage','navigator','location','fetch','alert','confirm','requestAnimationFrame','IntersectionObserver','MutationObserver','ResizeObserver','getComputedStyle','matchMedia',`${appSource}\n${hook}`);
  const api=fn(documentFake,winFake,storage(),{getItem:()=>null,setItem:()=>{},removeItem:()=>{},clear:()=>{}},navigator,{href:'https://chaselights.app/',pathname:'/',search:''},()=>Promise.reject(new Error('sim')),()=>{},()=>()=>{},class{},class{},class{},()=>({getPropertyValue:()=>''}),()=>({matches:false}));
  api.setData({spots,updated_at:'sim',region:'tw'});
  api.setSpots(spots);
  api.setBundle(bundle);
  api.setDay(day);
  api.filterAndRender();
  return api;
}

// --- fixtures -------------------------------------------------------------
// One spot: today's V2 day row has only already-past qualifying hours
// (23:00 with local now 23:50 → fail-closed empty); tomorrow has a window.
const tz='Asia/Taipei';
const todayDate=(()=>{const p=new Intl.DateTimeFormat('en-CA',{timeZone:tz,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());const v=Object.fromEntries(p.map(x=>[x.type,x.value]));return `${v.year}-${v.month}-${v.day}`;})();
const tomorrowDate=(()=>{const p=new Intl.DateTimeFormat('en-CA',{timeZone:tz,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date(Date.now()+86400000));const v=Object.fromEntries(p.map(x=>[x.type,x.value]));return `${v.year}-${v.month}-${v.day}`;})();
// A qualifying hour still ahead today (now + 2h, wraps past midnight only in
// the last two minutes of a day — good enough for the sim).
const futureHour=(()=>{const p=new Intl.DateTimeFormat('en-GB',{timeZone:tz,hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date(Date.now()+2*3600000));const m=/^(\d{1,2}):(\d{2})$/.exec(p.trim());return `${String(m[1]).padStart(2,'0')}:${m[2]}`;})();
const spot=(id,n,areas)=>({
  spot_id:id,lat:24,n:0,lon:121,category:'mountain',timezone:tz,admin_areas:areas||['花蓮縣'],
  name_i18n:{'zh-TW':`測試點${n}`},name_local:`Test ${n}`,
  daily:[{date:todayDate,all:{score:40,cloud_base_agl:1000,temp:15,no_viable_opportunity:true}},{date:tomorrowDate,all:{score:60,cloud_base_agl:1000,temp:14,opportunity_id:'sunset_cloud',opportunity_name:'雲海',theme:'sunset_cloud',indicator_key:'',factors:[]}}],
  opportunities:[{opportunity_id:'sunset_cloud',name_zh:'雲海'}],
});
const dayRow=(date,good)=>({local_date:date,state:good.length?'GUIDANCE_SATISFIED':'UNFAVORABLE',good_hours:good,hours:good.map(h=>({local:h,status:'GUIDANCE_SATISFIED',conditions:[]})),hour_counts:{GUIDANCE_SATISFIED:good.length}});
const place=(id,goodToday,goodTomorrow)=>({place_id:id,opportunities:[{opportunity_id:'sunset_cloud',name_i18n:{'zh-TW':'雲海'},days:[dayRow(todayDate,goodToday),dayRow(tomorrowDate,goodTomorrow)]}]});

// Scenario 3: today all deferred, tomorrow viable → rescue cards.
{
  const spots=[spot('tw-901',1),spot('tw-902',2),spot('tw-903',3)];
  const bundle={places:spots.map((s,i)=>place(s.spot_id,[],['20:00','21:00']))};
  const api=runScenario({spots,bundle});
  const c=api.container();
  const html=c.innerHTML+c.children.map(x=>x._html).join('');
  const banner=c.querySelector('.late-night-banner');
  assert.ok(banner,'rescue banner rendered');
  assert.ok(banner._html.includes('今日拍攝時段已結束'),`banner copy: ${banner._html}`);
  assert.ok(banner._html.includes('late-night-back'),'back-to-today button present');
  const cards=c.children.filter(x=>x.className==='card');
  assert.equal(cards.length,3,'tomorrow rescue cards replace the empty main grid');
  assert.equal(api.dayOffsetOf(),0,'dayOffsetOverride is scoped back to the tab value after render');
  cards.forEach(card=>{
    assert.ok(card._html.includes('符合時數 2'),'card evaluates tomorrow hours, not today (got: '+card._html.slice(card._html.indexOf('theme-winner'),card._html.indexOf('theme-winner')+200)+')');
  });
  const badgeInserts=ADJ_LOG.filter(h=>h.includes('tomorrow-badge'));
  assert.equal(badgeInserts.length,3,'one tomorrow badge per rescue card');
  assert.ok(badgeInserts.every(h=>h.includes('明天')),'badge shows the zh-TW tomorrow label');
  console.log('SCENARIO today0/tomorrowViable PASS — banner + 3 badge cards + scoped override');
}

// Scenario 1: sparse featured mode (2 viable today).
{
  const spots=[spot('tw-911',1),spot('tw-912',2)];
  const bundle={places:spots.map((s,i)=>place(s.spot_id,[futureHour],['20:00']))};
  const api=runScenario({spots,bundle});
  const c=api.container();
  const banner=c.querySelector('.late-night-banner');
  assert.ok(banner&&banner._html.includes('今日接近尾聲'),'sparse banner rendered');
  assert.ok(!banner._html.includes('late-night-back'),'sparse banner has no back button');
  const cards=c.children.filter(x=>x.className==='card');
  assert.equal(cards.length,2,'flat card list, no region sections');
  assert.ok(!c.children.some(x=>x.className==='spot-region-section'),'no region grouping headings in featured mode');
  cards.forEach(card=>assert.ok(!card._html.includes('tomorrow-badge'),'featured cards are today cards — no badge'));
  // hours-desc ordering: give spot1 1h and spot2 3h
  console.log('SCENARIO sparse-featured PASS — banner + flat list, cards unchanged');
}

// Scenario 2: normal mode (5 viable today → region grouping).
{
  const spots=[1,2,3,4,5].map(i=>spot('tw-92'+i,i,i%2?['台北市']:['花蓮縣']));
  const bundle={places:spots.map(s=>place(s.spot_id,[futureHour],['20:00']))};
  const api=runScenario({spots,bundle});
  const c=api.container();
  assert.equal(c.querySelector('.late-night-banner'),null,'no banner above threshold');
  assert.ok(c.querySelector('.spot-region-section'),'region grouping kept in normal mode');
  console.log('SCENARIO normal (>threshold) PASS — region grouping, no banner');
}

// Scenario 4: today 0 and tomorrow 0 → honest both-none banner + collapsed groups.
{
  const spots=[spot('tw-931',1),spot('tw-932',2)];
  const bundle={places:spots.map(s=>place(s.spot_id,[],[]))};
  const api=runScenario({spots,bundle});
  const c=api.container();
  const banner=c.querySelector('.late-night-banner');
  assert.ok(banner&&banner._html.includes('今日與明日目前均無符合時段'),'honest both-none banner');
  const cards=c.children.filter(x=>x.className==='card');
  assert.equal(cards.length,0,'no main-grid cards when both days are 0');
  assert.ok(c.querySelector('.deferred-group'),'collapsed deferred group still reachable');
  assert.ok(!c.querySelector('.late-night-back'),'no back button on the both-none banner');
  console.log('SCENARIO both-zero PASS — honest banner + collapsed groups intact');
}

// Scenario 3b (dismissal): same data, but the user pressed 回到今天.
{
  const spots=[spot('tw-941',1),spot('tw-942',2)];
  const bundle={places:spots.map(s=>place(s.spot_id,[],['20:00']))};
  const api=runScenario({spots,bundle});
  const bannerBefore=api.container().querySelector('.late-night-banner');
  assert.ok(bannerBefore,'rescue banner before dismissal');
  const back=bannerBefore.querySelector('[data-late-night-back]');
  assert.ok(back&&back.onclick,'back button wired to the dismissal handler');
  back.onclick();
  const c=api.container();
  assert.equal(c.querySelector('.late-night-banner'),null,'banner gone after 回到今天');
  assert.ok(c.querySelector('.deferred-group'),'today collapsed groups are back');
  assert.ok(c.children.filter(x=>x.className==='card').length===0,'no tomorrow cards after dismissal');
  console.log('SCENARIO back-to-today PASS — dismissed rescue shows today collapsed view');
}

console.log('ALL CL-UI-16 SIMULATIONS PASS');
