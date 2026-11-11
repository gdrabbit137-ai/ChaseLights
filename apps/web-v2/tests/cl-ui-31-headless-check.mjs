import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync, mkdtempSync, mkdirSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const OUT = mkdtempSync(join(tmpdir(),'clui31-shots-'));
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
  '--user-data-dir='+mkdtempSync(join(tmpdir(),'clui31-')),'about:blank'],
  {stdio:['ignore','ignore','pipe']});
const wsUrl = await new Promise((resolve,reject)=>{
  let buf='';const t=setTimeout(()=>reject(new Error('no devtools endpoint')),15000);
  chrome.stderr.on('data',d=>{buf+=d;const m=buf.match(/DevTools listening on (ws:\/\/\S+)/);
    if(m){clearTimeout(t);resolve(m[1]);}});
  chrome.on('error',e=>reject(new Error('spawn: '+e.message)));
});
let targets = [];
for (let i2 = 0; i2 < 40; ++i2) {
  targets = await (await fetch(`http://${wsUrl.match(/ws:\/\/([^/]+)/)[1]}/json/list`)).json();
  if (targets.some(t => t.type === 'page')) break;
  await new Promise(r => setTimeout(r, 250));
}
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

for (const [page, name] of [['genre-eval.html','genre-eval'],['field-intake.html','field-intake']]) {
  for (const w of [1280, 390]) {
    await send('Emulation.setDeviceMetricsOverride',{width:w,height:900,deviceScaleFactor:1,mobile:w<700});
    await send('Page.navigate',{url:base+page});
    await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50);})`);
    await new Promise(r=>setTimeout(r,1500));
    const audit = await evaljs(`(() => ({
      brands: document.querySelectorAll('.site-nav-brand').length,
      siteHeaders: document.querySelectorAll('.site-header').length,
      backLinks: document.querySelectorAll('.back-link').length,
      navItems: document.querySelectorAll('.site-nav-item').length,
      controlStrip: document.querySelectorAll('.control-strip').length,
      regionSelect: !!document.getElementById('region-select'),
      langSelect: !!document.getElementById('lang-select'),
      updateTime: !!document.getElementById('update-time'),
      langSelectField: !!document.getElementById('language-select'),
      pageTitle: !!document.getElementById('page-title'),
      h1s: [...document.querySelectorAll('h1')].map(h=>h.textContent.trim().slice(0,30))
    }))()`);
    console.log(name, w+'px', JSON.stringify(audit));
    const shot = await send('Page.captureScreenshot',{format:'png'});
    writeFileSync(join(OUT, `${name}-${w}.png`), Buffer.from(shot.data,'base64'));
  }
}
console.log('shots at', OUT);
chrome.kill(); server.close();
process.exit(0);