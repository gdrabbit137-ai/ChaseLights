// CL-UI-41 headless render check: serve the repo, open index.html in headless
// Chrome, switch to the 明天 tab, and verify the 「尚無本日評估」 group cards
// carry the NAMED missing-data copy (mechanical skip-reason mapping) instead
// of the generic 「所選日期目前無法提供可靠的拍攝建議」 line, in all three
// languages, rendered through the real createSpotCard path against the real
// regenerated bundle. Run: node apps/web-v2/tests/cl-ui-41-headless-check.mjs
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync, mkdtempSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';
import assert from 'node:assert/strict';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const OUT = mkdtempSync(join(tmpdir(),'clui41-shots-'));
const MIME = {'.html':'text/html','.mjs':'text/javascript','.css':'text/css',
  '.json':'application/json','.png':'image/png','.svg':'image/svg+xml'};
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
  '--user-data-dir='+mkdtempSync(join(tmpdir(),'clui41-')),'about:blank'],
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
await send('Page.enable'); await send('Runtime.enable');

await send('Page.navigate',{url:base});
await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50);})`);
await new Promise(r=>setTimeout(r,1500));

// The card group must exist and every card in it must carry a NAMED reason
// for its spot — keyed by spot id so the assertion is per-spot exact.
const EXPECT = {
  'tw-006':'此景點的攝影題材條件尚未完成查證，無法提供評估',
  'tw-007':'此景點的攝影題材條件尚未完成查證，無法提供評估',
  'tw-016':'拍攝座標尚未完成查證，無法評估此題材',
  'tw-029':'此景點的攝影題材條件尚未完成查證，無法提供評估',
  'tw-039':'此景點的攝影題材條件尚未完成查證，無法提供評估',
  'tw-058':'此景點的攝影題材條件尚未完成查證，無法提供評估',
  'tw-059':'此題材的成立條件尚未定義，無法提供評估',
  'tw-078':'此題材的成立條件尚未定義，無法提供評估',
  'tw-083':'此景點的攝影題材條件尚未完成查證，無法提供評估',
  'tw-084':'此景點的攝影題材條件尚未完成查證，無法提供評估',
};
const EN = {
  'tw-016':'Shooting coordinates are not yet verified, so this subject cannot be evaluated',
  'tw-059':'Qualifying conditions for this subject are not yet defined, so no evaluation is available',
};
const JA = {
  'tw-078':'この題材の成立条件がまだ定義されておらず、評価を提供できません',
};
async function collectGroup(){
  return evaljs(`(() => {
    const g=document.querySelector('.no-eval-group');
    if(!g) return {found:false};
    const spotIds=[...g.querySelectorAll('.card')].map(c=>{
      const m=[...c.querySelectorAll('a[data-weather], .tool-link')];
      return null;});
    // spot ids are not exposed on cards; match by spot name via the spot list:
    return {found:true, summary:g.querySelector('summary').textContent,
      cards:[...g.querySelectorAll('.card')].map(c=>({
        name:c.querySelector('.spot-name').textContent,
        copy:[...c.querySelectorAll('.theme-winner')].map(x=>x.textContent.trim()).join(' ')}))};
  })()`);
}
// zh-TW is the default language.
await new Promise(r=>setTimeout(r,8000));
const diag = await evaljs(`(() => ({
  loading: document.getElementById('loading')?document.getElementById('loading').style.display:'missing',
  groups: [...document.querySelectorAll('.deferred-group')].map(d=>d.className+' | '+d.querySelector('summary').textContent),
  bundlePlaces: (window.v2EvalBundle&&window.v2EvalBundle.places)?window.v2EvalBundle.places.length:('no-var:'+typeof v2EvalBundle),
  skipped: (window.v2EvalBundle&&window.v2EvalBundle.skipped)?window.v2EvalBundle.skipped.length:0,
  dayBtns: [...document.querySelectorAll('.day-btn')].map(b=>b.dataset.day),
}))()`);
console.log('diag:', JSON.stringify(diag));
const zh = await (async()=>{ const b=[...await evaljs(`[...document.querySelectorAll(".day-btn")]`)] ; return null;})();
await evaljs(`(()=>{const b=[...document.querySelectorAll('.day-btn')].find(x=>x.dataset.day==='tomorrow');if(b)b.click();})()`);
await new Promise(r=>setTimeout(r,6000));
const diag2 = await evaljs(`(() => ({
  active: (document.querySelector('.day-btn.active')||{}).dataset ? document.querySelector('.day-btn.active').dataset.day : null,
  groups: [...document.querySelectorAll('.deferred-group')].map(d=>d.className+' | '+(d.querySelector('summary')?d.querySelector('summary').textContent:'?')),
}))()`);
console.log('diag2:', JSON.stringify(diag2));
const zhGroup = await collectGroup();
console.log('zhGroup names:', JSON.stringify(zhGroup.cards.map(c=>c.name)));
console.log('zhGroup:', JSON.stringify(zhGroup).slice(0,400));
assert.ok(zhGroup && zhGroup.found === true, 'no-eval group must render');
assert.match(zhGroup.summary, /尚無本日評估的景點（\d+）/);
const nameToCopy = Object.fromEntries(zhGroup.cards.map(c=>[c.name, c.copy]));
for (const [spot, copy] of Object.entries(EXPECT)) {
  const name = await evaljs(`fetch('./tw_weather.json').then(r=>r.json()).then(d=>{const s=(d.spots||[]).find(x=>x.spot_id==='${spot}');return s?(s.name_i18n['zh-TW']||s.name||s.name_local):null;})`);;
  const hit = nameToCopy[name];
  assert.ok(hit !== undefined, `${spot} (${name}) must be in the no-eval group`);
  assert.ok(hit.includes(copy), `${spot}: expected named copy, got: ${hit}`);
  assert.ok(!hit.includes('所選日期目前無法提供可靠的拍攝建議'), `${spot}: generic copy must be gone`);
}
console.log('CL-UI-41 zh-TW no-eval group OK:', JSON.stringify(zhGroup.summary), zhGroup.cards.length, 'cards');

// en + ja: switch language, an already-rendered page re-renders in the new language.
for (const [lang, subset] of [['en', EN], ['ja', JA]]) {
  await evaljs(`(()=>{const s=document.getElementById('lang-select');s.value='${lang}';s.dispatchEvent(new Event('change'));})()`);
  await new Promise(r=>setTimeout(r,2500));
  const grp = await collectGroup();
  assert.ok(grp.found, `${lang}: no-eval group must render`);
  for (const [spot, copy] of Object.entries(subset)) {
    const name = await evaljs(`fetch('./tw_weather.json').then(r=>r.json()).then(d=>{const s=(d.spots||[]).find(x=>x.spot_id==='${spot}');return s?((s.name_i18n&&s.name_i18n['${lang}'])||(s.name_i18n&&s.name_i18n['zh-TW'])||s.name||s.name_local):null;})`);
    const hit = Object.fromEntries(grp.cards.map(c=>[c.name, c.copy]))[name];
    assert.ok(hit !== undefined, `${lang}: ${spot} (${name}) must be in the no-eval group`);
    assert.ok(hit.includes(copy), `${lang} ${spot}: expected ${copy}, got: ${hit}`);
  }
  console.log('CL-UI-41', lang, 'no-eval group OK:', grp.cards.length, 'cards');
}
const shot = await send('Page.captureScreenshot',{format:'png'});
console.log('shot:', join(OUT,'render.png'), Buffer.from(shot.data,'base64').length, 'bytes');
chrome.kill(); server.close();
console.log('CL-UI-41 headless render OK');
