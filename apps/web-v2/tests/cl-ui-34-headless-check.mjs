// CL-UI-34 headless check: serve the repo, open the weather modal for a TW
// spot, verify the collapsed provenance panel is present but collapsed by
// default, expand it, verify source rows + WeatherGrid cycle stamps render
// from SERVED data, and capture 390px + desktop screenshots.
// Run: node apps/web-v2/tests/cl-ui-34-headless-check.mjs
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync, mkdtempSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';
import assert from 'node:assert/strict';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const OUT = mkdtempSync(join(tmpdir(), 'clui34-shots-'));
const MIME = {'.html':'text/html','.mjs':'text/javascript','.css':'text/css',
  '.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.ico':'image/x-icon'};
const server = createServer((req,res)=>{
  let p = req.url.split('?')[0].replace(/\/+$/,'') || '/';
  const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
  try{ const body=readFileSync(file);
       res.writeHead(200,{'content-type':MIME[file.slice(file.lastIndexOf('.'))]||'application/octet-stream'});
       res.end(body);}
  catch{ res.writeHead(404); res.end('not found'); }
}).listen(0,'127.0.0.1');
await new Promise(r=>server.on('listening',r));
const base = `http://127.0.0.1:${server.address().port}/`;
let chrome = spawn(BROWSER,[
  '--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
  '--no-first-run','--remote-debugging-port=0',
  '--user-data-dir='+mkdtempSync(join(tmpdir(),'clui34-')),'about:blank'],
  {stdio:['ignore','ignore','pipe']});
const wsUrl = await new Promise((resolve,reject)=>{
  let buf='';const t=setTimeout(()=>reject(new Error('no devtools endpoint')),15000);
  chrome.stderr.on('data',d=>{buf+=d;const m=buf.match(/DevTools listening on (ws:\/\/\S+)/);
    if(m){clearTimeout(t);resolve(m[1]);}});
  chrome.on('error',e=>reject(new Error('spawn: '+e.message)));
});
const targets = await (await fetch(`http://${wsUrl.match(/ws:\/\/([^/]+)/)[1]}/json/list`)).json();
const pageWs = targets.find(t=>t.type==='page').webSocketDebuggerUrl;
const ws = new WebSocket(pageWs);
await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
let id=0; const pending=new Map();
ws.onmessage = e => { const m=JSON.parse(e.data);
  if(m.id && pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id);} };
const send=(method,params={})=>new Promise((resolve,reject)=>{
  const i=++id; pending.set(i,m=>m.error?reject(new Error(m.error.message)):resolve(m.result));
  ws.send(JSON.stringify({id:i,method,params}));});
async function evaljs(expr){ const r=await send('Runtime.evaluate',
  {expression:expr,returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||'page error');
  return r.result?.result?.value ?? r.result?.value;}
async function shot(name){
  const {data}=await send('Page.captureScreenshot',{format:'png'});
  writeFileSync(join(OUT,name),Buffer.from(data,'base64'));}

await send('Page.enable'); await send('Runtime.enable');
await send('Page.addScriptToEvaluateOnNewDocument',{source:`window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message||e)));`});
// 390px mobile viewport first.
await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:2,mobile:true});
await send('Page.navigate',{url:base});
await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50);})`);
await new Promise(r=>setTimeout(r,2500));

// The SERVED html must carry the new stamp (cache-buster proof).
const stamp = await evaljs(`document.querySelector('script[src*="app.js"]').src`);
assert.ok(stamp.includes('?v=clui40'),'served app.js stamp: '+stamp);

const opened = await evaljs(`(async () => {
  await new Promise(r=>{const t=setInterval(()=>{try{if(typeof currentSpots!=='undefined'&&currentSpots.length){clearInterval(t);r(1)}}catch(e){}},100);setTimeout(r,20000);});
  if(typeof currentSpots==='undefined'||!currentSpots.length) return 'no spots:'+JSON.stringify({cs:typeof currentSpots,err:window.__errs||null,loading:document.getElementById('loading')?.hidden});
  const spot=currentSpots.find(s=>s.spot_id&&/^tw-/.test(s.spot_id));
  const metric=getMetric(spot);
  await openWeatherModal(spot,metric);
  return document.getElementById('modal-overlay').style.display;
})()`);
assert.equal(opened,'flex','weather modal opened');

// Panel exists, collapsed by default, below the hourly timeline (deep layer).
const initial = await evaljs(`(() => {
  const det=document.getElementById('modal-provenance');
  const tableWrap=document.querySelector('#modal-overlay .timeline-table-wrap');
  return {open:det.open, rows:det.querySelectorAll('.prov-row').length,
          afterTimeline:!!tableWrap&&det.offsetTop>tableWrap.offsetTop,
          summary:det.querySelector('summary').textContent.trim()};
})()`);
assert.equal(initial.open,false,'panel collapsed by default');
assert.ok(initial.rows>0,'static rows pre-rendered: '+initial.rows);
assert.equal(initial.summary,'資料來源');
assert.ok(initial.afterTimeline,'panel sits below the hourly table');
await shot('clui34-390-collapsed.png');

// Expand → layer rows fetch cycle times from SERVED WeatherGrid QC data.
await new Promise(r=>setTimeout(r,600));
const expanded = await evaljs(`(async () => {
  const det=document.getElementById('modal-provenance');
  det.open=true;
  det.dispatchEvent(new Event('toggle'));
  await new Promise(r=>setTimeout(r,3000));
  const rows=[...det.querySelectorAll('.prov-row')].map(r=>r.textContent.replace(/\\s+/g,' ').trim());
  return {open:det.open, rows};
})()`);
assert.equal(expanded.open,true);
console.log('CL-UI-34 provenance rows (390px):');
for(const r of expanded.rows)console.log('  -',r);
assert.ok(expanded.rows.some(r=>r.includes('GFS Seamless')),'hourly model row');
assert.ok(expanded.rows.some(r=>r.includes('起報')),'at least one cycle stamp resolved');
assert.ok(expanded.rows.some(r=>r.includes('觀測')),'Himawari observation stamp resolved');
assert.ok(expanded.rows.some(r=>r.includes('門檻為暫定值')||r.includes('尚未以實拍校準')),'threshold honesty row');
assert.ok(expanded.rows.some(r=>r.includes('GMT+8')),'timezone row');
// Bring the panel into view for the screenshot (it sits below the timeline).
await evaljs(`document.getElementById('modal-provenance').scrollIntoView({block:'start'});window.scrollTo(0,0);`);
await new Promise(r=>setTimeout(r,400));
await shot('clui34-390-open.png');

// Desktop viewport, panel closed again after re-render via language switch.
await send('Emulation.clearDeviceMetricsOverride');
await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
const desktop = await evaljs(`(async () => {
  if(window.activeModalSpot){renderWeatherModal(activeModalSpot,activeModalSummary);}
  const det=document.getElementById('modal-provenance');
  det.open=true;
  await new Promise(r=>setTimeout(r,800));
  return {w:innerWidth, open:det.open, rows:det.querySelectorAll('.prov-row').length,
          noHScroll:document.documentElement.scrollWidth<=innerWidth+1};
})()`);
assert.equal(desktop.open,true);
assert.ok(desktop.noHScroll,'no horizontal scroll');
await evaljs(`document.getElementById('modal-provenance').scrollIntoView({block:'start'});window.scrollTo(0,0);`);
await new Promise(r=>setTimeout(r,400));
await shot('clui34-desktop-open.png');
console.log('CL-UI-34 headless OK; screenshots in', OUT);
chrome.kill(); server.close();
