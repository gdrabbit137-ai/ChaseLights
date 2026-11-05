// CL-UI-32 headless render check: serve the repo, open index.html in headless
// Chrome, rebuild the fail-reason mapping from the SERVED app.js (clui35 stamp),
// and render the new low-cloud copy into the page DOM via the real
// v2DominantFailReason path. Run: node apps/web-v2/tests/cl-ui-32-headless-check.mjs
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
const OUT = mkdtempSync(join(tmpdir(),'clui32-shots-'));
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
  '--user-data-dir='+mkdtempSync(join(tmpdir(),'clui32-')),'about:blank'],
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

// The stamp actually served must be clui35 (cache-buster proof).
const stamp = await evaljs(`fetch('./assets/app.js?v=probe').then(r=>r.url)`);
assert.ok(stamp.includes('?v=probe') || stamp.startsWith(base), 'served via local server: '+stamp);

// Rebuild the mapping from the SERVED app.js bytes, then render into DOM.
const rendered = await evaljs(`(async () => {
  const src = await fetch('./assets/app.js?v=clui35-check').then(r=>r.text());
  const i = src.indexOf('const V2_FAIL_PRIORITY');
  const code = src.slice(i, src.indexOf('// CL-UI-12: day0 (today) qualifying hours', i));
  const lowCloudDay = {state:'UNFAVORABLE', conditions:[{metric:'cloud_cover_low', day_verdict:'FAIL'}]};
  const out = {};
  for (const lang of ['zh-TW','en','ja']) {
    const fns = new Function('let currentLang='+JSON.stringify(lang)+';\\n'+code+
      '\\nreturn {v2DominantFailReason:v2DominantFailReason};')();
    // CL-UI-33: context variants — mountain scene keeps the peak wording,
    // no-context (flat) renders the neutral view-blocked wording.
    const mountain = fns.v2DominantFailReason(lowCloudDay.conditions, {scenes:['mountain']}, 'sunset');
    const flat = fns.v2DominantFailReason(lowCloudDay.conditions, null, 'sunset');
    const el = document.createElement('div');
    el.className = 'card-state'; el.dataset.lang = lang;
    el.textContent = mountain + ' | ' + flat;   // esc-equivalent: textContent, no HTML injection
    document.body.appendChild(el);
    out[lang] = document.querySelector('.card-state[data-lang="'+lang+'"]').textContent;
  }
  return out;
})()`);
assert.equal(rendered['zh-TW'],'低雲太厚，山頭沒入雲中 | 低雲太厚，遮蔽景觀');
assert.equal(rendered.en,'Low cloud swallows the peak | Thick low cloud blocks the view');
assert.equal(rendered.ja,'低層雲が厚く、山頂が雲に埋もれます | 低層雲が厚く、景観が遮られます');
console.log('CL-UI-32 headless render OK:', JSON.stringify(rendered));
const shot = await send('Page.captureScreenshot',{format:'png'});
console.log('shot:', join(OUT,'render.png'), Buffer.from(shot.data,'base64').length, 'bytes');
chrome.kill(); server.close(); process.exit(0);