// CL-UI-23 headless verification: Xiangshan (tw-002) card best-window vs modal
// evaluation day rows must agree, and the night subject must not advertise
// daytime hours. Modeled on tests/local-smoke.mjs CDP harness.
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFileSync, mkdtempSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {tmpdir} from 'node:os';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const BROWSER = process.env.CHROMIUM_EXECUTABLE
  || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
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
  '--user-data-dir='+mkdtempSync(join(tmpdir(),'clui23-')),'about:blank'],
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
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function evaljs(expr){ const r=await send('Runtime.evaluate',
  {expression:expr,returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||'page error');
  return r.result?.result?.value ?? r.result?.value;}
await send('Page.enable'); await send('Runtime.enable');
await send('Page.navigate',{url:base+'index.html'});
await evaljs(`new Promise(r=>{const t=setInterval(()=>{if(document.readyState==='complete'){clearInterval(t);r(1)}},50);})`);
await evaljs(`new Promise(r=>{let n=0;const t=setInterval(()=>{
  if(document.querySelector('.card .theme-winner')){clearInterval(t);r(true);return}
  if(++n>300){clearInterval(t);r(false)}},100)})`);
const hasXiang = await evaljs(`!![...document.querySelectorAll('.card')].find(c=>c.textContent.includes('象山六巨石'))`);
console.log('xiangshan card found:', hasXiang);
const card = await evaljs(`(() => {
  const c=[...document.querySelectorAll('.card')].find(c=>c.textContent.includes('象山六巨石'));
  if(!c)return null;
  return {winner:[...c.querySelectorAll('.theme-winner')].map(n=>n.textContent.trim()),
          windows:[...c.querySelectorAll('.best-window-row')].map(n=>n.textContent.trim())};
})()`);
console.log('CARD:', JSON.stringify(card));
const nightCard = await evaljs(`(() => {
  const c=[...document.querySelectorAll('.card')].find(c=>c.textContent.includes('象山六巨石'));
  if(!c)return null;
  const el=[...c.querySelectorAll('.theme-winner')].find(n=>n.textContent.includes('夜景'));
  if(!el)return null;
  let s=el.textContent.trim();
  let n=el.nextElementSibling;
  while(n){ if(n.classList.contains('best-window-row')){s+=' || '+n.textContent.trim();break;} n=n.nextElementSibling; }
  return s;
})()`);
console.log('NIGHT CARD TEXT:', nightCard);
// Open the detail modal (card click → openPlaceModal).
await evaljs(`[...document.querySelectorAll('.card')].find(c=>c.textContent.includes('象山六巨石')).click()`);
await sleep(800);
const modal = await evaljs(`(() => {
  const body=document.querySelector('#place-modal-body');
  if(!body)return null;
  return {winner:[...body.querySelectorAll('.theme-winner')].map(n=>n.textContent.trim()),
          dayRows:[...body.querySelectorAll('.v2-day')].map(n=>n.textContent.trim()),
          modalDayRows:[...body.querySelectorAll('.modal-day-row')].map(n=>n.textContent.trim())};
})()`);
console.log('MODAL:', JSON.stringify(modal));
await new Promise(r=>{server.close(r);});
chrome.kill();
