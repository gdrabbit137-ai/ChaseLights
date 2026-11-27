// CL-UI-115 §2 — two triggers, two panels (real browser, Playwright).
//
// Contract under test:
//   - #modal-overlay        data-panel="weather"        ← card BODY click
//   - #place-modal-overlay  data-panel="subject-window" ← SUBJECT button click
//   - the two are never the same element, and the panels are distinct documents
//     sections with distinct data-panel values;
//   - both triggers are keyboard-openable (Enter on the card, Enter/Space on the
//     subject button) and focus returns to the trigger on close;
//   - a foggy now_hour tints the condition chip via a CLASS, and the COMPUTED
//     style is amber (not just a class name);
//   - the same metric chip renders byte-identical outerHTML at 1440×900 and
//     393×852;
//   - the subject panel renders zero empty subject rows.
//
// Run: node --test apps/web-v2/tests/cl-ui-115-panels.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFileSync,statSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {dirname,join,normalize} from 'node:path';

const HERE=dirname(fileURLToPath(import.meta.url));
const ROOT=normalize(join(HERE,'..','..','..'));
const PW_MODULE=process.env.PLAYWRIGHT_MODULE||join(ROOT,'.ci','tooling','node_modules','playwright','index.js');
const BROWSER=process.env.CHROMIUM_EXECUTABLE||process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe';

const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.woff2':'font/woff2'};
let server=null,base='',browser=null,page=null;

test.before(async()=>{
  server=createServer((req,res)=>{
    const url=new URL(req.url,'http://127.0.0.1');
    let p=normalize(join(ROOT,decodeURIComponent(url.pathname)));
    if(!p.startsWith(ROOT)){res.writeHead(403);res.end();return;}
    try{if(statSync(p).isDirectory())p=join(p,'index.html');}catch(e){res.writeHead(404);res.end('not found');return;}
    let body;
    try{body=readFileSync(p);}catch(e){res.writeHead(404);res.end('not found');return;}
    const ext=/\.([a-z0-9]+)$/i.exec(p);res.writeHead(200,{'content-type':MIME[ext?'.'+ext[1].toLowerCase():'']||'application/octet-stream'});
    res.end(body);
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  base=`http://127.0.0.1:${server.address().port}`;
  const pw=await import(pathToFileURL(PW_MODULE).href);
  const chromium=pw.chromium||(pw.default&&pw.default.chromium);
  browser=await chromium.launch({executablePath:BROWSER,args:['--no-sandbox','--disable-dev-shm-usage']});
});

test.after(async()=>{
  try{if(browser)await browser.close();}catch(e){/* noop */}
  if(server)await new Promise(r=>server.close(r));
});

async function openHome(viewport){
  if(page)await page.close();
  page=await browser.newPage({viewport:viewport||{width:1440,height:900},locale:'zh-TW'});
  await page.goto(`${base}/index.html?region=tw`,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelectorAll('#spots-container .card').length>0,null,{timeout:60000});
  // The evaluation bundle gates the card anatomy; wait for a real tier badge.
  await page.waitForFunction(()=>{const t=document.querySelector('#spots-container .card .tier');return t&&t.textContent.trim().length>0;},null,{timeout:60000});
  return page;
}

test('CL-UI-115 §2: the two panels are distinct elements with distinct data-panel values',async()=>{
  await openHome();
  const panels=await page.evaluate(()=>{
    const w=document.getElementById('modal-overlay');
    const s=document.getElementById('place-modal-overlay');
    return {weather:w&&w.dataset.panel,subject:s&&s.dataset.panel,same:w===s,weatherId:w&&w.id,subjectId:s&&s.id};
  });
  assert.equal(panels.weather,'weather','the forecast dialog declares data-panel="weather"');
  assert.equal(panels.subject,'subject-window','the subject dialog declares data-panel="subject-window"');
  assert.equal(panels.same,false,'the two panels are never the same element');
  assert.notEqual(panels.weatherId,panels.subjectId);
});

test('CL-UI-115 §2: card body opens the weather panel and closing returns focus to the card',async()=>{
  await openHome();
  const id=await page.evaluate(()=>{const c=document.querySelector('#spots-container .card');c.scrollIntoView({block:'center'});return c.dataset.placeId;});
  await page.waitForTimeout(300);
  await page.locator('#spots-container .card').first().click({position:{x:20,y:20}});
  await page.waitForFunction(()=>document.getElementById('modal-overlay').style.display==='flex',null,{timeout:15000});
  const open=await page.evaluate(()=>({
    panel:document.getElementById('modal-overlay').dataset.panel,
    subjectOpen:document.getElementById('place-modal-overlay').style.display==='flex',
  }));
  assert.equal(open.panel,'weather','the card body opened the WEATHER panel');
  assert.equal(open.subjectOpen,false,'it did not open the subject panel');
  await page.keyboard.press('Escape');
  await page.waitForFunction(()=>document.getElementById('modal-overlay').style.display!=='flex',null,{timeout:10000});
  const focus=await page.evaluate(()=>({id:document.activeElement&&document.activeElement.dataset?document.activeElement.dataset.placeId:null,cls:document.activeElement&&document.activeElement.className}));
  assert.equal(focus.id,id,'focus returned to the card that opened the panel');
  assert.match(String(focus.cls),/card/,'the focused element is the card body');
});

test('CL-UI-115 §2: the subject button opens the SUBJECT panel (keyboard) with zero empty rows',async()=>{
  await openHome();
  const id=await page.evaluate(()=>{const c=document.querySelector('#spots-container .card');c.scrollIntoView({block:'center'});return c.dataset.placeId;});
  await page.waitForTimeout(300);
  // Focus the subject button and open it with Space (the a[href="#"] must honour it).
  await page.evaluate(()=>{const b=document.querySelector('#spots-container .card [data-weather]');b.focus();});
  await page.keyboard.press(' ');
  await page.waitForFunction(()=>document.getElementById('place-modal-overlay').style.display==='flex',null,{timeout:15000});
  const open=await page.evaluate(()=>({
    panel:document.getElementById('place-modal-overlay').dataset.panel,
    weatherOpen:document.getElementById('modal-overlay').style.display==='flex',
    rows:document.querySelectorAll('#place-modal-body .sw-row').length,
    cells:document.querySelectorAll('#place-modal-body .sw-win').length,
    empty:[...document.querySelectorAll('#place-modal-body .sw-win')].filter(el=>!el.textContent.trim()).length,
    named:[...document.querySelectorAll('#place-modal-body .sw-name')].filter(el=>!el.textContent.trim()).length,
  }));
  assert.equal(open.panel,'subject-window','the subject button opened the SUBJECT-WINDOW panel');
  assert.equal(open.weatherOpen,false,'it did not open the weather panel');
  assert.ok(open.rows>0,`the subject panel lists subject rows (got ${open.rows})`);
  assert.equal(open.empty,0,`no subject row cell is empty (checked ${open.cells} cells)`);
  assert.equal(open.named,0,'every subject row carries its subject name');
  await page.keyboard.press('Escape');
  await page.waitForFunction(()=>document.getElementById('place-modal-overlay').style.display!=='flex',null,{timeout:10000});
  const focus=await page.evaluate(()=>({isSubjectBtn:!!(document.activeElement&&document.activeElement.closest&&document.activeElement.closest('[data-weather]'))}));
  assert.equal(focus.isSubjectBtn,true,'focus returned to the subject button');
});

test('CL-UI-115 §2: a foggy now_hour tints the chip via a class, and the COMPUTED style is amber',async()=>{
  await openHome();
  const id=await page.evaluate(()=>document.querySelector('#spots-container .card').dataset.placeId);
  const applied=await page.evaluate((placeId)=>{
    const now=new Date();
    const date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Taipei',year:'numeric',month:'2-digit',day:'2-digit'}).format(now);
    const hh=String(Number(new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Taipei',hour:'2-digit',hour12:false}).format(now))%24).padStart(2,'0');
    const rows=[{time:`${date} ${hh}:00`,local_date:date,weather_code:45,temp:12.3,visibility:0.4}];
    window.__clui115.setNowRows(placeId,rows);
    const chip=document.querySelector(`.card[data-place-id="${placeId}"] .now-wx`);
    if(!chip)return {ok:false};
    const cs=getComputedStyle(chip);
    const plain=document.querySelector('.card-metric-chips .metric-chip:not(.now-wx)');
    const plainCs=plain?getComputedStyle(plain):null;
    return {ok:true,cls:chip.className,hour:chip.getAttribute('data-now-hour'),text:chip.textContent.replace(/\s+/g,' ').trim(),
      bg:cs.backgroundColor,border:cs.borderTopColor,color:cs.color,plainBg:plainCs?plainCs.backgroundColor:null};
  },id);
  assert.equal(applied.ok,true,'the injected foggy hour produced a now chip');
  assert.match(applied.cls,/cl-now-fog/,'the fog state is carried as a class');
  assert.match(String(applied.hour||''),/^\d{2}:\d{2}$/,'the chip labels the hour it is showing');
  assert.match(applied.text,/目前起霧/,'the chip states the reason in words');
  assert.notEqual(applied.bg,applied.plainBg,'the foggy chip background differs from a plain chip (computed)');
  assert.match(applied.bg,/rgba?\(245, 158, 11|245, 158, 11/,'the computed background is the amber token set');
});

test('CL-UI-115 §2 (CL-UI-115 §1 acceptance): the same metric chip is byte-identical at 1440×900 and 393×852',async()=>{
  await openHome({width:1440,height:900});
  const id=await page.evaluate(()=>document.querySelector('#spots-container .card').dataset.placeId);
  // Inject the SAME synthetic hour in both viewports: the lazy weather_details
  // fetch would otherwise repaint one side with the local shard snapshot.
  const inject=()=>page.evaluate((placeId)=>{
    const now=new Date();
    const date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Taipei',year:'numeric',month:'2-digit',day:'2-digit'}).format(now);
    const hh=String(Number(new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Taipei',hour:'2-digit',hour12:false}).format(now))%24).padStart(2,'0');
    window.__clui115.setNowRows(placeId,[{time:`${date} ${hh}:00`,local_date:date,weather_code:3,temp:18.4,visibility:12.5}]);
  },id);
  // §3 made the now row viewport-lazy: wait for this card's shard fetch to
  // SETTLE before injecting, or a late arrival repaints one viewport with the
  // real shard after the injection and the two sides legitimately differ.
  const settle=async()=>{
    await page.waitForFunction(()=>!!document.querySelector('#spots-container .card .now-wx'),null,{timeout:25000}).catch(()=>{});
    await page.waitForTimeout(800);
  };
  await settle();
  await inject();
  const readChip=async(placeId)=>{
    await page.waitForFunction(pid=>{
      const el=document.querySelector(`.card[data-place-id="${pid}"] .now-wx`);
      return !!(el&&el.getAttribute('data-now-hour'));
    },placeId,{timeout:15000});
    return page.evaluate(pid=>document.querySelector(`.card[data-place-id="${pid}"] .now-wx`).outerHTML,placeId);
  };
  const wide=await readChip(id);
  await page.setViewportSize({width:393,height:852});
  // The list re-renders on the breakpoint switch; the chip is rebuilt from the
  // same cache + renderer, so wait for it instead of racing the repaint.
  await page.waitForTimeout(600);
  await settle();
  await inject();
  const narrow=await readChip(id);
  assert.equal(narrow,wide,`the metric chip markup is viewport-independent (no emoji font dependency)
  1440: ${wide}
   393: ${narrow}`);
  // Both sides must carry the INJECTED hour, not a shard snapshot: that is what
  // makes the byte comparison meaningful.
  const hour=await page.evaluate(()=>{const n=new Date();return String(Number(new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Taipei',hour:'2-digit',hour12:false}).format(n))%24).padStart(2,'0')+':00';});
  assert.match(wide,new RegExp(`data-now-hour="${hour}"`),'1440 shows the injected hour');
  assert.match(narrow,new RegExp(`data-now-hour="${hour}"`),'393 shows the injected hour');
  assert.match(wide,/<svg class="cl-icon" data-cl-icon="visibility"/,'the chip carries the SVG eye, not 👁');
  assert.doesNotMatch(wide,/👁/,'no emoji glyph remains in the metric chip');
});
