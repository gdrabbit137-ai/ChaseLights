// Run explicitly with Chromium: node --test apps/web-v2/tests/hourly-weather-browser.mjs
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {resolve,sep,extname} from 'node:path';

const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/codex/cua_node/lib/node_modules/playwright');
const root=resolve(fileURLToPath(new URL('../',import.meta.url)));
let server,browser,url;
before(async()=>{
  server=createServer(async(req,res)=>{try{
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const file=resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
    if(!file.startsWith(root+sep)){res.writeHead(403).end();return;}
    const bytes=await readFile(file);
    res.writeHead(200,{'Content-Type':{'.html':'text/html','.mjs':'text/javascript','.json':'application/json','.css':'text/css'}[extname(file)]||'application/octet-stream'}).end(bytes);
  }catch{res.writeHead(404).end();}});
  await new Promise(done=>server.listen(0,'127.0.0.1',done));url=`http://127.0.0.1:${server.address().port}`;
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',args:['--no-sandbox']});
});
after(async()=>{await browser?.close();if(server?.listening)await new Promise(done=>server.close(done));});

const expected={
  'zh-TW':{title:'七星潭 · 72 小時逐時天氣歷史樣本',stale:'歷史／已過期',missing:'缺值',field:'前一小時降雨機率'},
  en:{title:'Qixingtan · 72-hour historical hourly weather sample',stale:'Historical / expired',missing:'Unavailable',field:'Preceding-hour precipitation probability'},
  ja:{title:'七星潭 · 過去の72時間分の毎時気象サンプル',stale:'過去のデータ／期限切れ',missing:'欠損',field:'直前1時間の降水確率'}
};
for(const [device,width] of [['desktop',1440],['mobile',360]])for(const locale of ['zh-TW','en','ja']){
  test(`${device} ${locale}: archived hourly view, keyboard, source and research regression`,async()=>{
    const context=await browser.newContext({viewport:{width,height:900},isMobile:device==='mobile',hasTouch:device==='mobile'});
    await context.addInitScript(value=>localStorage.setItem('chaselights-v2-locale',value),locale);
    const page=await context.newPage(),errors=[],outside=[];
    page.on('pageerror',error=>errors.push(error.message));
    page.on('request',request=>{if(!request.url().startsWith(url))outside.push(request.url());});
    try{
      await page.goto(url);
      await page.waitForFunction(()=>document.querySelector('.hourly-state')?.dataset.state==='STALE');
      await page.waitForFunction(()=>document.querySelectorAll('.place-button').length===7);
      const panel=page.locator('#hourly-weather');
      assert.equal(await panel.locator('h2').textContent(),expected[locale].title);
      assert.equal(await panel.locator('.hourly-state').textContent(),expected[locale].stale);
      assert.equal(await panel.locator('.hourly-day').count(),3);
      assert.equal(await panel.locator('.hourly-hour').count(),72);
      assert.equal(await panel.locator('.hourly-evaluation').count(),1);
      assert.match(await panel.innerText(),/Open-Meteo/);
      assert.match(await panel.innerText(),/CC BY 4.0/);
      assert.equal(await panel.locator('a[href="https://open-meteo.com/"]').count(),1);
      assert.equal(await panel.locator('a[href="https://creativecommons.org/licenses/by/4.0/"]').count(),1);
      const first=panel.locator('.hourly-hour').first();
      await first.locator('summary').focus();await page.keyboard.press('Enter');
      assert.equal(await first.getAttribute('open'),'');
      assert.equal(await first.locator('dt').count(),10);
      assert.ok((await first.innerText()).includes(expected[locale].field));
      assert.ok((await first.innerText()).includes('0 %'),'actual zero cloud value');
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'no horizontal overflow');
      await page.locator('#browse-research').click();
      if(device==='mobile')await page.locator('#open-filters').click();
      await page.locator('#search').fill('七星潭');
      assert.equal(await page.locator('.place-button').count(),1);
      await page.locator('.place-button[data-place-id="tw-036"]').click();
      assert.equal(await page.locator('.opportunity').count(),1);
      assert.equal(await page.locator('.score,.nav-action').count(),0);
      assert.deepEqual(errors,[]);assert.deepEqual(outside,[],'no live provider or other network requests');
    }finally{await context.close();}
  });
}

test('missing archive and corrupted archive fail closed with localized status',async()=>{
  const context=await browser.newContext({viewport:{width:360,height:900},isMobile:true,hasTouch:true});
  const page=await context.newPage();
  try{
    await page.route('**/qixingtan-one-shot-20261019.json',route=>route.fulfill({status:404,body:''}));
    await page.goto(url);await page.waitForFunction(()=>document.querySelector('.hourly-state')?.dataset.state==='UNAVAILABLE');
    assert.equal(await page.locator('.hourly-hour').count(),0);
    assert.equal(await page.locator('.hourly-retry').count(),1);
    await page.unrouteAll();
    await page.route('**/qixingtan-one-shot-20261019.json',route=>route.fulfill({status:200,contentType:'application/json',body:'{"forged":true}'}));
    await page.locator('.hourly-retry').click();
    await page.waitForFunction(()=>document.querySelector('.hourly-state')?.dataset.state==='ERROR');
    assert.equal(await page.locator('.hourly-hour').count(),0);
    assert.equal(await page.locator('.score,.nav-action').count(),0);
  }finally{await context.close();}
});

test('test-only pinned partial archive shows missing cell, never a zero',async()=>{
  const changed=JSON.parse(await readFile(resolve(root,'fixtures/hourly/qixingtan-one-shot-20261019.json'),'utf8'));
  changed.availability='PARTIAL';
  changed.hours[0].values.cloud_cover_high={value:null,unit:'%',source_unit:'%',state:'UNAVAILABLE',reason_code:'NULL_VALUE'};
  const body=JSON.stringify(changed),digest=createHash('sha256').update(body).digest('hex');
  const moduleSource=await readFile(resolve(root,'hourly-weather.mjs'),'utf8');
  const moduleBody=moduleSource.replace(/export const ARCHIVE_SHA256 = '[a-f0-9]{64}'/,`export const ARCHIVE_SHA256 = '${digest}'`);
  const context=await browser.newContext({viewport:{width:360,height:900},isMobile:true,hasTouch:true});
  await context.addInitScript(()=>localStorage.setItem('chaselights-v2-locale','en'));
  const page=await context.newPage();
  try{
    await page.route('**/hourly-weather.mjs',route=>route.fulfill({status:200,contentType:'text/javascript',body:moduleBody}));
    await page.route('**/qixingtan-one-shot-20261019.json',route=>route.fulfill({status:200,contentType:'application/json',body}));
    await page.goto(url);await page.waitForFunction(()=>document.querySelector('.hourly-state')?.dataset.state==='STALE');
    assert.equal(await page.locator('.hourly-partial').textContent(),'Incomplete data');
    await page.locator('.hourly-hour').first().locator('summary').click();
    const cell=page.locator('.hourly-hour').first().locator('dd').nth(5);
    assert.equal(await cell.textContent(),'Unavailable');
    assert.equal(await cell.getAttribute('class'),'hourly-missing');
    assert.ok((await page.locator('.hourly-hour').first().innerText()).includes('0 mm'),'independent genuine zero retained');
  }finally{await context.close();}
});
