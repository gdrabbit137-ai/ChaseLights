// Six real browser cases against the newly built eight-file candidate package.
// This is loopback artifact verification, distinct from existing public smoke.
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createServer} from 'node:http';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {resolve,extname,sep} from 'node:path';
import {verifyResearchPage,locales} from '../browser_contract.mjs';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/codex/cua_node/lib/node_modules/playwright');
let browser,server,base,opportunity,manifest;
const requested=new Set();
before(async()=>{
  assert.ok(process.env.V2_BUILD_DIR,'Actual static build output is required');
  const build=resolve(process.env.V2_BUILD_DIR);const root=resolve(build,'public');
  manifest=JSON.parse(await readFile(resolve(build,'build-manifest.json'),'utf8'));
  assert.equal(manifest.status,'PASS');assert.equal(manifest.deployment_allowed,false);
  assert.equal(Object.keys(manifest.files).length,8);
  for(const [file,sha] of Object.entries(manifest.files)){
    const bytes=await readFile(resolve(root,file));
    assert.equal(createHash('sha256').update(bytes).digest('hex'),sha,file+' manifest bytes differ');
  }
  const catalog=JSON.parse(await readFile(resolve(root,'apps/web-v2/catalog.v2.json'),'utf8'));
  assert.equal(catalog.research_only,true);assert.equal(catalog.forecast_available,false);
  assert.equal(catalog.selected_date_recommendation_eligible,false);assert.deepEqual(catalog.evaluations,[]);
  opportunity=catalog.opportunities[0];assert.equal(opportunity.opportunity_id,'tw-026-P01');
  server=createServer(async(request,response)=>{
    try{
      const path=new URL(request.url,'http://localhost').pathname;
      const file=resolve(root,'.'+(path.endsWith('/')?path+'index.html':path));
      if(!file.startsWith(root+sep)){response.writeHead(403).end();return;}
      requested.add(path);
      const body=await readFile(file);
      response.writeHead(200,{'Content-Type':{'.mjs':'text/javascript','.css':'text/css','.html':'text/html','.json':'application/json'}[extname(file)]||'application/octet-stream'}).end(body);
    }catch{response.writeHead(404).end();}
  });
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
  base=`http://127.0.0.1:${server.address().port}/apps/web-v2/`;
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',args:['--no-sandbox']});
});
after(async()=>{await browser?.close();if(server?.listening)await new Promise(resolve=>server.close(resolve));});
for(const [device,viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]])for(const locale of locales){
  test(`candidate static package ${device} ${locale}: real catalog-state dependency, exact source and research entry`,async()=>{
    const context=await browser.newContext({viewport,isMobile:device==='mobile',hasTouch:device==='mobile'});
    const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
    try{
      const response=await page.goto(base);assert.equal(response.status(),200);
      await verifyResearchPage(page,opportunity,locale,'forecast-home');
      assert.ok(requested.has('/apps/web-v2/catalog-state.mjs'));
      assert.ok(requested.has('/apps/web-v2/catalog.v2.json'));
      assert.deepEqual(errors,[]);
      const directory=process.env.W5_SCREENSHOT_DIR;
      if(directory){await mkdir(directory,{recursive:true});await page.screenshot({path:resolve(directory,`${device}-${locale}-built-home.png`),fullPage:true});}
    }finally{await context.close();}
  });
}
