// Local browser smoke for apps/web-v2 — playwright-free replacement.
//
// Drives the system Chrome via the raw DevTools protocol (Node >= 22 global
// WebSocket), so the same suite runs on this Windows host without the Codex
// cloud playwright environment. Checks are a port of the browser suites'
// owner-relevant assertions: rendering, honest-research guardrails, i18n and
// responsive layout over the admitted 216-place catalog.
//
// Usage: node tests/local-smoke.mjs [--browser <path-to-chrome/edge>]
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..');
const flagIx = process.argv.indexOf('--browser');
const BROWSER = flagIx > 0 ? process.argv[flagIx+1]
  : (process.env.CHROMIUM_EXECUTABLE
     || 'C:/Program Files/Google/Chrome/Application/chrome.exe');

const MIME = {'.html':'text/html','.mjs':'text/javascript','.css':'text/css',
  '.json':'application/json','.png':'image/png','.svg':'image/svg+xml'};
const server = createServer((req,res)=>{
  let path = req.url.split('?')[0].replace(/\/+$/,'') || '/';
  const file = join(WEB, path === '/' ? 'index.html' : path.slice(1));
  try{ const body = readFileSync(file);
       res.writeHead(200,{'content-type':MIME[file.slice(file.lastIndexOf('.'))]||'application/octet-stream'});
       res.end(body); }
  catch{ res.writeHead(404); res.end('not found'); }
}).listen(0,'127.0.0.1');
await new Promise(r=>server.on('listening',r));
const base = `http://127.0.0.1:${server.address().port}/`;

const chrome = spawn(BROWSER,[
  '--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port=0',
  '--user-data-dir='+process.env.TEMP+'/local-smoke-profile-'+Date.now(),'about:blank'],
  {stdio:['ignore','ignore','pipe']});
const wsUrl = await new Promise((resolve,reject)=>{
  let buf='';const t=setTimeout(()=>reject(new Error('no devtools endpoint')),15000);
  chrome.stderr.on('data',d=>{buf+=d;
    const m=buf.match(/DevTools listening on (ws:\/\/\S+)/);
    if(m){clearTimeout(t);resolve(m[1]);}});
  chrome.on('exit',()=>{clearTimeout(t);reject(new Error('chrome exited: '+buf.slice(-400)));});
});

let id=0; const pending=new Map();
// Attach to the page target: browser-level sockets reject Page.* commands.
const targets = await (await fetch(`http://${wsUrl.match(/ws:\/\/([^/]+)/)[1]}/json/list`)).json();
const pageWs = targets.find(t=>t.type==='page').webSocketDebuggerUrl;
const ws = new WebSocket(pageWs);
await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
ws.onmessage = e => { const m=JSON.parse(e.data);
  if(m.id && pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id);}
  if(m.method==='Runtime.exceptionThrown')
    console.log('# page error:',m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text); };
const send=(method,params={})=>new Promise((resolve,reject)=>{
  const i=++id; pending.set(i,m=>m.error?reject(new Error(method+': '+m.error.message)):resolve(m.result));
  ws.send(JSON.stringify({id:i,method,params}));});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function evaljs(expr){ const r=await send('Runtime.evaluate',
  {expression:expr,returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||'page error');
  return r.result?.result?.value ?? r.result?.value;}
async function goto(path,locale,viewport){
  await send('Emulation.setDeviceMetricsOverride',
    viewport==='mobile'?{width:390,height:844,deviceScaleFactor:1,mobile:true,hasTouch:true}
                       :{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await send('Runtime.evaluate',{expression:locale?
    `localStorage.setItem('chaselights-v2-locale',${JSON.stringify(locale)})`:
    `localStorage.clear()`});
  await send('Page.navigate',{url:base+path});
  await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.querySelector('#browse-research')){clearInterval(t);r(true)}},50);setTimeout(()=>{clearInterval(t);r(false)},15000)})`);
}
async function openResearch(){
  await evaljs(`document.readyState==='complete'?1:new Promise(r=>addEventListener('load',()=>r(1)))`);
  const shown = await evaljs(`new Promise(r=>{let n=0;const t=setInterval(()=>{
    if(document.querySelectorAll('.place-button').length===216){clearInterval(t);r(true);return}
    if(++n%10===0)document.querySelector('#browse-research')?.click()},100);setTimeout(()=>{clearInterval(t);r(false)},20000)})`);
  if(!shown) console.log('# body:',String(await evaljs(`document.body.innerText.slice(0,400)`)).replace(/\n/g,' | '));
}
const results=[];
const check=(name,ok,detail='')=>{results.push({name,ok});console.log(`${ok?'ok':'not ok'} - ${name}${detail?' :: '+detail:''}`);};
async function expect(name,expr,detail){ check(name,await evaljs(expr),detail); }

try{
  await send('Page.enable'); await send('Runtime.enable');
  for(const locale of ['zh-TW','en','ja']){
    await goto('/',locale,'desktop');
    await openResearch();
    check(`${locale}: 216 place buttons`,await evaljs(`document.querySelectorAll('.place-button').length===216`));
    check(`${locale}: honest place count`,await evaljs(
      `document.querySelector('#place-count').textContent===${JSON.stringify({'zh-TW':'符合景點: 216',en:'Matching places: 216',ja:'一致する撮影地: 216'}[locale])}`));
    await expect(`${locale}: no scores on research view`,'!document.querySelector(".score")');
    await expect(`${locale}: no navigation buttons`,'!document.querySelector(".nav-action")');
    // Deep sample: one reviewed + one admitted place.
    for(const place of ['jp-010','tw-001']){
      await evaljs(`document.querySelector('.place-button[data-place-id="${place}"]').click()`);
      await sleep(200);
      await expect(`${locale} ${place}: subject cards rendered`,
        `document.querySelectorAll('.opportunity').length>0`);
      await expect(`${locale} ${place}: no FAVORABLE verdicts`,
        `!document.body.innerText.includes('FAVORABLE')`);
      await expect(`${locale} ${place}: no horizontal overflow`,
        `document.documentElement.scrollWidth<=window.innerWidth`);
      await goto('/',locale,'desktop');
      await openResearch();
    }
    // Locale persistence across reload.
    await send('Page.reload',{});
    await sleep(500);
    check(`${locale}: locale persists after reload`,await evaljs(
      `localStorage.getItem('chaselights-v2-locale')==='${locale}'`));
  }
  // Topic filter honesty: colorful-clouds only binds evidenced opportunities.
  await goto('/','en','desktop');
  await openResearch();
  await evaljs(`const cb=document.querySelector('#topic-options input[value="topic:colorful-clouds"]');cb.checked=true;cb.dispatchEvent(new Event('change',{bubbles:true}))`);
  await sleep(300);
  const filtered=await evaljs(`document.querySelectorAll('.place-button').length`);
  check('topic filter narrows places',filtered>0&&filtered<216,`visible=${filtered}`);
  // Mobile smoke.
  await goto('/','zh-TW','mobile');
  await openResearch();
  await expect('mobile: no horizontal overflow','document.documentElement.scrollWidth<=window.innerWidth');
}catch(e){
  check('harness error',false,e.message);
}finally{
  chrome.kill(); server.close();
  const pass=results.filter(r=>r.ok).length;
  console.log(`# local smoke: ${pass}/${results.length} passed`);
  // TAP summary for the CI group runner (parse_node requires exactly one of each).
  console.log(`# tests ${results.length}`);
  console.log(`# pass ${pass}`);
  console.log(`# fail ${results.length-pass}`);
  console.log('# skipped 0');
  process.exitCode = pass===results.length && results.length>0 ? 0 : 1;
}
