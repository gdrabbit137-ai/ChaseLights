import maplibregl from 'https://unpkg.com/maplibre-gl@6.11.2/dist/maplibre-gl.mjs';
const SOURCES={
 gfs:'./weathergrid/gfs_tw_weather_browser.json',
 jma:'./weathergrid/jma_msm_tw_cloud_browser.json',
 cwa:'./weathergrid/cwa_wrf3_tw_weather_browser.json',
 icon:'./weathergrid/icon_tw_cloud_browser.json'
};
const $=id=>document.getElementById(id), canvas=$('overlay'),ctx=canvas.getContext('2d');
const state={data:null,cache:new Map(),timer:null,prefetch:null};
const map=new maplibregl.Map({container:'map',style:'https://tiles.openfreemap.org/styles/liberty',center:[121,23.7],zoom:6});
map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');
function bboxOfData(d){const b=d?.bbox||{};return {w:+(b.leftlon??b.west),s:+(b.bottomlat??b.south),e:+(b.rightlon??b.east),n:+(b.toplat??b.north)}}
function fmt(b){return b?[b.w,b.s,b.e,b.n].map(v=>Number(v).toFixed(3)).join(', '):'—'}
function view(){const b=map.getBounds();return {w:b.getWest(),s:b.getSouth(),e:b.getEast(),n:b.getNorth()}}
function expand(b,f=.6){const dx=(b.e-b.w)*f,dy=(b.n-b.s)*f;return {w:b.w-dx,s:b.s-dy,e:b.e+dx,n:b.n+dy}}
function contains(a,b){return a&&b&&a.w<=b.w&&a.e>=b.e&&a.s<=b.s&&a.n>=b.n}
function key(b){return [b.w,b.s,b.e,b.n].map(v=>v.toFixed(2)).join(':')}
function resize(){const r=canvas.getBoundingClientRect(),d=devicePixelRatio||1;canvas.width=r.width*d;canvas.height=r.height*d;ctx.setTransform(d,0,0,d,0,0);draw()}
function draw(){const r=canvas.getBoundingClientRect();ctx.clearRect(0,0,r.width,r.height);if(!state.data)return;const cov=bboxOfData(state.data),v=view();if(!contains(cov,v)){ctx.fillStyle='rgba(10,18,30,.16)';ctx.fillRect(0,0,r.width,r.height);ctx.fillStyle='rgba(255,190,70,.95)';ctx.font='600 13px system-ui';ctx.fillText('部分 viewport 超出目前靜態資料範圍 · V2 將要求補抓',16,28)}}
function schedule(){clearTimeout(state.timer);state.timer=setTimeout(()=>{const v=view(),p=expand(v,.65),k=key(p);state.prefetch=p;state.cache.set(k,{requestedAt:Date.now(),bbox:p,status:contains(bboxOfData(state.data),p)?'cache-hit/static':'needs-provider-fetch'});$('viewport').textContent='viewport: '+fmt(v);$('coverage').textContent='loaded coverage: '+fmt(bboxOfData(state.data));$('prefetch').textContent='prefetch ring: '+fmt(p);$('cache').textContent='request cache: '+state.cache.size+' · '+state.cache.get(k).status;$('status').textContent=contains(bboxOfData(state.data),v)?'目前 viewport 已有資料':'偵測到缺資料範圍：等待動態 provider';draw()},180)}
async function load(){const id=$('provider').value,url=SOURCES[id];$('status').textContent='載入 '+id.toUpperCase()+'…';let d=state.cache.get(url);if(!d){d=await fetch(url,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(r.status);return r.json()});state.cache.set(url,d)}state.data=d;const fields=Object.keys(d.fields||{});$('layer').innerHTML=fields.map(x=>'<option>'+x+'</option>').join('');const b=bboxOfData(d);map.fitBounds([[b.w,b.s],[b.e,b.n]],{padding:35,duration:0});schedule()}
map.on('load',()=>{resize();load().catch(e=>$('status').textContent='載入失敗 '+e.message)});
map.on('move',schedule);map.on('zoom',schedule);map.on('resize',resize);
$('provider').addEventListener('change',()=>load().catch(e=>$('status').textContent='載入失敗 '+e.message));
$('home').addEventListener('click',()=>{const b=bboxOfData(state.data);map.fitBounds([[b.w,b.s],[b.e,b.n]],{padding:35})});
window.addEventListener('resize',resize);