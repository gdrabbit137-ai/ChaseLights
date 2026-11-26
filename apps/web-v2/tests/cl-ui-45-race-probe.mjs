// CL-UI-45 driver (not a test): measures the local build's date-switch cost,
// the date-switch + card-click race (wrong-spot modal), and profiles where the
// main thread spends its time. Run:
//   node apps/web-v2/tests/cl-ui-45-race-probe.mjs
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync, mkdtempSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const BROWSER = process.env.CHROMIUM_EXECUTABLE || process.env.CHROME_PATH
  || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const FLAGS = (process.env.CL_CHROME_FLAGS || '--enable-unsafe-swiftshader --use-angle=swiftshader').split(' ').filter(Boolean);
const MIME = {'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml'};
const REGION = process.env.CL_REGION || 'tw';

const server = createServer((req, res) => {
  const p = req.url.split('?')[0].replace(/\/+$/, '') || '/';
  const file = join(WEB, p === '/' ? 'index.html' : p.slice(1));
  try { const body = readFileSync(file);
    res.writeHead(200, {'content-type': MIME[file.slice(file.lastIndexOf('.'))] || 'application/octet-stream'});
    res.end(body);
  } catch { res.writeHead(404); res.end('not found'); }
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const baseURL = `http://127.0.0.1:${server.address().port}/`;

const chrome = spawn(BROWSER, ['--headless=new','--disable-gpu','--no-sandbox','--disable-dev-shm-usage',
  '--no-first-run','--remote-debugging-port=0','--window-size=1280,1000',
  ...FLAGS, '--user-data-dir=' + mkdtempSync(join(tmpdir(), 'clui45-')), 'about:blank'],
  {stdio:['ignore','ignore','pipe']});
const wsUrl = await new Promise((resolve, reject) => {
  let buf=''; const t=setTimeout(()=>reject(new Error('no devtools endpoint')), 60000);
  chrome.stderr.on('data', d => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
    if (m) { clearTimeout(t); resolve(m[1]); } });
  chrome.on('error', reject);
});
const dbgHost = wsUrl.match(/ws:\/\/([^/]+)/)[1];
let targets = [];
for (let i=0;i<40;++i){ targets = await (await fetch(`http://${dbgHost}/json/list`)).json();
  if (targets.some(t=>t.type==='page')) break; await new Promise(r=>setTimeout(r,250)); }
const ws = new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
let id=0; const pending=new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params={}) => new Promise((resolve,reject)=>{ const i=++id;
  pending.set(i, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
  ws.send(JSON.stringify({id:i, method, params})); });
const evaljs = async (expr) => { const r = await send('Runtime.evaluate', {expression:expr, returnByValue:true, awaitPromise:true});
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error');
  return r.result?.value; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function realClickAt(x, y) {
  await send('Input.dispatchMouseEvent', {type:'mousePressed', x, y, button:'left', clickCount:1});
  await send('Input.dispatchMouseEvent', {type:'mouseReleased', x, y, button:'left', clickCount:1});
}

await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', {width:1280, height:1000, deviceScaleFactor:1, mobile:false});
await send('Page.navigate', {url: baseURL + '?region=' + REGION + '&date=today&tier=all'});
await evaljs(`new Promise((res,rej)=>{const t0=Date.now();const iv=setInterval(()=>{
  if(document.querySelectorAll('#spots-container .card').length>10){clearInterval(iv);res(1);}
  else if(Date.now()-t0>25000){clearInterval(iv);rej(new Error('cards never rendered'));}},100);})`);
await sleep(1500);

const out = {cards: await evaljs(`document.querySelectorAll('#spots-container .card').length`)};

// ---- (A) date-switch cost: 11 switches, measured in-page ---------------------
out.switch = await evaljs(`(async () => {
  const seq=['tomorrow','after_tomorrow','day3','day4','day5','day6','today','tomorrow','day3','today','tomorrow'];
  const per=[]; const wall0=performance.now();
  for (const k of seq) {
    const t0=performance.now(); switchDay(k); per.push([k, Math.round(performance.now()-t0)]);
    await new Promise(r=>setTimeout(r,20));
  }
  return {per, wall: Math.round(performance.now()-wall0), total: per.reduce((a,b)=>a+b[1],0)};
})()`);

// ---- (B) race: date switch then a real click lands on the new DOM -------------
// The page records the card that the click ACTUALLY landed on, so the oracle
// separates "different card than the one pressed before the switch" (the old
// bug) from "the card the user is now looking at" (correct behaviour).
async function installClickProbe() {
  await evaljs(`(()=>{ if(!window.__cl45ClickTarget){ window.__cl45ClickTarget=null;
    document.getElementById('spots-container').addEventListener('click',function(e){
      const c=e.target.closest&&e.target.closest('.card');
      window.__cl45ClickTarget=c?(c.dataset.placeId||''):null; },true); } return 1; })()`);
}
async function raceOnce() {
  // reset to today with the full list
  await evaljs(`(()=>{if(document.getElementById('spot-sort'))document.getElementById('spot-sort').value='region';setSortMode('region');switchDay('today');return 1;})()`);
  await sleep(600);
  const probe = await evaljs(`(()=>{const c=[...document.querySelectorAll('#spots-container .card')].find(x=>x.getBoundingClientRect().top>150);
    if(!c)return null;const r=c.getBoundingClientRect();
    return {x:Math.round(r.left+r.width/2), y:Math.round(r.top+Math.min(60,r.height/2)), id:c.dataset.placeId, name:(c.querySelector('.spot-name')||{}).textContent};})()`);
  if (!probe) return null;
  // swipe date -> the render blocks; the click is queued and delivered after it
  await evaljs(`window.__cl45ClickTarget=null`);
  await send('Runtime.evaluate', {expression:`switchDay('day3')`});
  await realClickAt(probe.x, probe.y);
  await sleep(450);
  const opened = await evaljs(`(()=>{const ov=document.getElementById('modal-overlay');
    const open=ov&&ov.style.display==='flex';
    const name=(document.getElementById('modal-spot-name')||{}).textContent||'';
    const id=ov?ov.dataset.placeId:'';
    const clicked=window.__cl45ClickTarget;
    if(open)closeModal();
    return {open,name,id,clicked};})()`);
  // restore
  await evaljs(`(()=>{switchDay('today');return 1;})()`);
  await sleep(500);
  return {pressed: probe, opened,
    wrong_than_pressed: !!(opened.open && opened.id !== probe.id),
    wrong_than_clicked: !!(opened.open && opened.id !== opened.clicked)};
}
await installClickProbe();
out.race = [];
for (let i=0;i<10;++i) { const r = await raceOnce(); if (r) out.race.push(r); }
out.wrong_than_pressed = out.race.filter(r=>r.wrong_than_pressed).length;
out.wrong_than_clicked = out.race.filter(r=>r.wrong_than_clicked).length;
out.opened = out.race.filter(r=>r.opened.open).length;
out.attempts = out.race.length;

// ---- (C) profile: where does one switchDay spend its time? -------------------
await send('Profiler.enable'); await send('Profiler.setSamplingInterval', {interval: 200});
await send('Profiler.start');
await evaljs(`switchDay('tomorrow')`);
await send('Profiler.stop').then(async p => {
  const prof = p.profile; const byId = new Map(prof.nodes.map(n=>[n.id,n]));
  const self = new Map(); const dt = prof.timeDeltas; const samples = prof.samples;
  for (let i=0;i<samples.length;++i){ const n = byId.get(samples[i]); if(!n) continue;
    const f = n.callFrame; const key = (f.functionName||'(anon)') + ' @' + (f.url||'').split('/').pop() + ':' + (f.lineNumber+1);
    self.set(key, (self.get(key)||0) + (dt[i]||0)); }
  out.profile = [...self.entries()].sort((a,b)=>b[1]-a[1]).slice(0,15)
    .map(([k,v])=>[k, Math.round(v/1000)+'ms']);
});
await evaljs(`switchDay('today')`);

console.log(JSON.stringify(out, null, 1));
try { ws.close(); } catch {}
chrome.kill(); server.close();
process.exit(0);
