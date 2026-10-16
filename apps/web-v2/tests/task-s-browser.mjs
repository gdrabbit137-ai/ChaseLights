// node --test apps/web-v2/tests/task-s-browser.mjs
// Requires actual Chromium. A missing executable is a test failure, not SKIP.
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {resolve,extname,sep} from 'node:path';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=resolve(fileURLToPath(new URL('../',import.meta.url)));
let server,browser,url;
before(async()=>{
  server=createServer(async(req,res)=>{try{
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const path=resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
    if(!path.startsWith(root+sep))return res.writeHead(403).end();
    const bytes=await readFile(path);
    res.writeHead(200,{'Content-Type':{'.html':'text/html','.mjs':'text/javascript','.css':'text/css','.json':'application/json'}[extname(path)]||'application/octet-stream'}).end(bytes);
  }catch{res.writeHead(404).end();}});
  await new Promise(done=>server.listen(0,'127.0.0.1',done));
  url=`http://127.0.0.1:${server.address().port}`;
  browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||chromium.executablePath(),headless:true,args:['--no-sandbox']});
});
after(async()=>{await browser?.close();if(server)await new Promise(done=>server.close(done));});

for(const [device,width] of [['desktop',1440],['mobile',390]])for(const locale of ['zh-TW','en','ja']){
  test(`${device} ${locale}: verified seven-place search, OR topics and locale persistence`,async()=>{
    const context=await browser.newContext({viewport:{width,height:900},isMobile:device==='mobile',hasTouch:device==='mobile'});
    await context.addInitScript(value=>localStorage.setItem('chaselights-v2-locale',value),locale);
    const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
    try{
      await page.goto(url);await page.waitForFunction(()=>document.querySelectorAll('.place-button').length===7);
      assert.equal(await page.locator('#research-browser').isVisible(),false);
      await page.locator('#browse-research').click();
      assert.equal(await page.locator('#place-count').textContent(),{
        'zh-TW':'符合景點: 7',en:'Matching places: 7',ja:'一致する撮影地: 7'}[locale]);
      assert.equal(await page.locator('#topic-options input').count(),8);
      assert.equal(await page.locator('.nav-action,.score').count(),0);
      if(device==='mobile'){
        assert.equal(await page.locator('#filter-panel').isVisible(),false);
        await page.locator('#open-filters').click();
        assert.equal(await page.locator('#filter-panel').isVisible(),true);
      }
      await page.locator('#search').fill('井仔脚');
      assert.equal(await page.locator('.place-button').count(),1);
      await page.locator('#search').fill('Jingzaijiao');
      assert.equal(await page.locator('.place-button').count(),1);
      await page.locator('#topic-options input[value="topic:sunset"]').check();
      await page.locator('#topic-options input[value="topic:colorful-clouds"]').check();
      await page.locator('.place-button[data-place-id="tw-026"]').click();
      assert.equal(await page.locator('.opportunity').count(),2);
      await page.locator('#topic-options input[value="topic:sunset"]').uncheck();
      assert.equal(await page.locator('.opportunity').count(),1);
      assert.ok((await page.locator('.opportunity h3').textContent()).length>0);
      await page.locator('#language').selectOption(locale==='en'?'ja':'en');
      assert.equal(await page.locator('#topic-options input[value="topic:colorful-clouds"]').isChecked(),true);
      assert.equal(await page.locator('.opportunity').count(),1);
      await page.locator('#search').fill('[.*]');assert.equal(await page.locator('.place-button').count(),0);
      await page.locator('#clear-filters').click();assert.equal(await page.locator('.place-button').count(),7);
      assert.equal(await page.locator('.opportunity .pill').first().count(),1);
      assert.ok(!(await page.locator('#detail').innerText()).includes('FAVORABLE'));
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      if(device==='mobile'){
        await page.locator('#close-filters').click();
        assert.equal(await page.locator('#filter-panel').isVisible(),false);
        assert.equal(await page.evaluate(()=>document.activeElement.id),'open-filters');
      }
      assert.deepEqual(errors,[]);
    }finally{await context.close();}
  });
}
test('tampered index fails closed without research cards or forecast',async()=>{
  const context=await browser.newContext();const page=await context.newPage();
  try{
    await page.route('**/browse-index.v2.json',async route=>route.fulfill({status:200,contentType:'application/json',body:'{"forged":true}'}));
    await page.goto(url);await page.waitForFunction(()=>document.querySelector('#data-state').dataset.status==='ready');
    await page.waitForFunction(()=>document.querySelector('#places-list').textContent.includes('索引'));
    await page.locator('#browse-research').click();
    assert.equal(await page.locator('.place-button,.opportunity,.nav-action').count(),0);
  }finally{await context.close();}
});
