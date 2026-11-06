// CL-CI-13: weather-modal hourly-data load hardening.
//
// 1. openWeatherModal auto-retries the hourly (detail shard) load exactly once
//    after a short backoff before surfacing an error.
// 2. The failure state carries a manual retry button (detail_retry), not just
//    a dead-end 「暫時無法載入」 message; a stale modal (closed/superseded load)
//    never renders or re-triggers.
// 3. The modal subtitle describes the ACTUAL hourly data window ({p}/{f}
//    measured from the loaded spot payload; legacy source = past 24h + 168h
//    forecast), replacing the stale hardcoded 「過去 24 小時 + 未來 72 小時」.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const indexSource=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
const grab=(start,end)=>{
  const a=appSource.indexOf(start);
  const b=appSource.indexOf(end,a+1);
  assert.ok(a>=0&&b>a,`grab failed: ${start} .. ${end}`);
  return appSource.slice(a,b);
};

// ---------------------------------------------------------------------------
// Part A: static contract — new strings and the stale-window copy removal.
// ---------------------------------------------------------------------------
test('CL-CI-13 A1: detail_retry exists in all three LANG dicts',()=>{
  assert.ok(appSource.includes("detail_retry:'重試'"));
  assert.ok(appSource.includes("detail_retry:'Retry'"));
  assert.ok(appSource.includes("detail_retry:'再試行'"));
});

test('CL-CI-13 A2: modal_subtitle is a {p}/{f} template — the stale 72h copy is gone',()=>{
  const zh=grab("modal_subtitle:'⏱️ 逐時拍攝條件","tag_best:'最佳'");
  const en=grab("modal_subtitle:'⏱️ Hourly","tag_best:'BEST'");
  const ja=grab("modal_subtitle:'⏱️ 時間別","tag_best:'最適'");
  for(const [seg] of [[zh],[en],[ja]]){
    assert.ok(seg.includes('{p}')&&seg.includes('{f}'),seg);
    assert.ok(!/72/.test(seg),`stale 72h window still hardcoded: ${seg}`);
  }
});

test('CL-CI-13 A3: index.html bumps the app.js cache-bust stamp to clui40',()=>{
  assert.match(indexSource,/assets\/app\.js\?v=clui40/);
  assert.ok(!indexSource.includes('assets/app.js?v=clui33'));
});

// ---------------------------------------------------------------------------
// Part B: live retry logic (openWeatherModal / loadWeatherModal harness).
// ---------------------------------------------------------------------------
const retryBlock=grab('let modalLoadSeq=0','function scrollWeatherModalToCurrent');
const subtitleBlock=grab('const HOURLY_WINDOW_DEFAULT','function applyStaticI18n');

function makeHarness(stubs){
  const timeouts=stubs.timeouts||[];
  const elements={};
  const makeEl=()=>({innerText:'',innerHTML:'',style:{display:stubs.overlayOpen===false?'none':'flex'},
    handlers:{},addEventListener(t,f){this.handlers[t]=f;},trigger(){this.handlers.click&&this.handlers.click();}});
  const getElementById=id=>elements[id]||(elements[id]=makeEl());
  const document={
    getElementById,
    querySelector:sel=>sel==='[data-i18n="modal_subtitle"]'?getElementById('subtitle'):null,
  };
  const factory=new Function('document','esc','d','currentRegion','currentSpots','getMetric',
    'renderWeatherModal','loadDetails','spotName','syncModalScrollLock','setTimeout',`
    ${retryBlock}
    return {openWeatherModal,loadWeatherModal,showModalLoadError,getSeq:()=>modalLoadSeq};
  `);
  const api=factory(document,
    stubs.esc||(s=>String(s)),
    ()=>stubs.d,
    stubs.currentRegion||'tw',
    stubs.currentSpots||[],
    stubs.getMetric||(()=>null),
    stubs.renderWeatherModal,
    stubs.loadDetails,
    stubs.spotName||(s=>s.spot_id),
    ()=>{},
    (f,ms)=>timeouts.push({f,ms}));
  return {...api,elements,timeouts};
}

const D={detail_error:'暫時無法載入天氣預報。',detail_retry:'重試',detail_loading:'正在載入天氣預報…',
  weather_link:'🌦️ 天氣預報',modal_subtitle:'⏱️ 逐時拍攝條件：過去 {p} 小時 + 未來 {f} 小時'};

test('CL-CI-13 B1: first load failure auto-retries once after backoff, then succeeds',async()=>{
  let calls=0;const renders=[];
  const h=makeHarness({
    d:D,timeouts:[],
    loadDetails:async()=>{calls++;if(calls===1)throw new Error('HTTP 503');
      return {spot:{spot_id:'tw-001',hourly_forecast:[]}};},
    renderWeatherModal:(spot)=>renders.push(spot.spot_id),
  });
  await h.openWeatherModal({spot_id:'tw-001'},null);
  assert.equal(renders.length,0,'must not render on first failure');
  assert.equal(h.timeouts.length,1,'exactly one automatic retry');
  assert.equal(h.timeouts[0].ms,2000);
  h.timeouts[0].f();
  await new Promise(r=>setImmediate(r));
  assert.deepEqual(renders,['tw-001']);
  assert.ok(!h.elements['modal-summary'].innerHTML.includes('modal-retry-btn'));
});

test('CL-CI-13 B2: second failure renders the error + manual retry button',async()=>{
  let calls=0;
  const h=makeHarness({d:D,timeouts:[],loadDetails:async()=>{calls++;throw new Error('HTTP 503');},
    renderWeatherModal:()=>{}});
  await h.openWeatherModal({spot_id:'tw-001'},null);
  assert.equal(calls,1);
  h.timeouts[0].f();
  await new Promise(r=>setImmediate(r));
  assert.equal(calls,2,'auto-retry fired exactly once');
  const box=h.elements['modal-summary'];
  assert.ok(box.innerHTML.includes('modal-retry-btn'),'retry button present');
  assert.ok(box.innerHTML.includes('重試'));
  assert.ok(box.innerHTML.includes(D.detail_error));
});

test('CL-CI-13 B3: clicking retry re-runs the load and can recover',async()=>{
  let calls=0;const renders=[];
  const h=makeHarness({d:D,timeouts:[],
    loadDetails:async()=>{calls++;if(calls<3)throw new Error('HTTP 503');
      return {spot:{spot_id:'tw-001'}};},
    renderWeatherModal:(spot)=>renders.push(spot.spot_id)});
  await h.openWeatherModal({spot_id:'tw-001'},null);
  h.timeouts[0].f(); // auto-retry -> still fails -> button
  await new Promise(r=>setImmediate(r));
  const btn=h.elements['modal-retry-btn'];
  assert.ok(btn,'button exists');
  btn.trigger();
  assert.equal(h.elements['modal-summary'].innerText,D.detail_loading,'click resets to loading copy');
  await new Promise(r=>setImmediate(r));
  h.timeouts[1]&&h.timeouts[1].f(); // manual attempt also gets one auto-retry
  await new Promise(r=>setImmediate(r));
  assert.deepEqual(renders,['tw-001'],'manual retry path recovers');
});

test('CL-CI-13 B4: a superseded modal load never retries or renders',async()=>{
  const renders=[];
  const h=makeHarness({d:D,timeouts:[],
    loadDetails:async()=>{throw new Error('HTTP 503');},
    renderWeatherModal:(spot)=>renders.push(spot.spot_id)});
  const first=h.openWeatherModal({spot_id:'tw-001'},null);
  await h.openWeatherModal({spot_id:'tw-002'},null); // supersedes the first load
  await first;
  // The superseded load's catch saw a stale seq and scheduled NO retry; only
  // the active modal's auto-retry exists.
  assert.equal(h.timeouts.length,1,'stale load must not schedule a retry');
  h.timeouts[0].f();
  await new Promise(r=>setImmediate(r));
  assert.deepEqual(renders,[],'nothing renders while every attempt fails');
});

test('CL-CI-13 B5: subtitle window is measured from the loaded payload',()=>{
  const H=36e5;
  const rows=[{time_utc:new Date(Date.now()-24*H).toISOString()},
              {time_utc:new Date(Date.now()+168*H).toISOString()}];
  const elements={};
  const subtitleEl={innerText:''};
  const factory=new Function('d',`
    ${subtitleBlock}
    return {updateModalHourlyWindow,modalSubtitleText,modalHourlyWindowRef:()=>modalHourlyWindow};
  `);
  const api=factory(()=>D);
  assert.deepEqual(api.modalHourlyWindowRef(),{past:24,future:168},'default = legacy source window');
  api.updateModalHourlyWindow({hourly_forecast:rows});
  assert.equal(api.modalHourlyWindowRef().past,24);
  assert.equal(api.modalHourlyWindowRef().future,168);
  const text=api.modalSubtitleText();
  assert.ok(text.includes('過去 24 小時 + 未來 168 小時'),text);
  assert.ok(!text.includes('{p}')&&!text.includes('{f}'),'placeholders substituted');
  // A wider source window flows through dynamically instead of being hardcoded.
  api.updateModalHourlyWindow({hourly_forecast:[
    {time_utc:new Date(Date.now()-30*H).toISOString()},
    {time_utc:new Date(Date.now()+180*H).toISOString()}]});
  assert.ok(api.modalSubtitleText().includes('過去 30 小時 + 未來 180 小時'));
});