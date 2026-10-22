// node --test apps/web-v2/tests/photography-topics-browser.mjs
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {resolve,sep,extname} from 'node:path';

const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/codex/cua_node/lib/node_modules/playwright');
const root=resolve(fileURLToPath(new URL('../',import.meta.url)));
const source=JSON.parse(await readFile(resolve(root,'catalog.v2.json'),'utf8'));
const places=[...new Set(source.opportunities.map(row=>row.place_id))];
const expected={
  'zh-TW':{list:'這裡可以拍什麼',scope:'這些題材仍為待審核的研究資料，並非已核准的正式拍攝指南。',
    GUIDANCE:'拍攝參考',VERIFY:'需另行確認',AUTO:'自動判斷尚未接線',required:'拍攝所需的條件',quality:'可能提升拍攝效果的條件',
    automatic:'此題材尚未支援可信的自動條件判斷。',description:'這個題材的簡介尚未提供。',conditions:'尚未提供特殊拍攝條件；不代表沒有條件限制。'},
  en:{list:'What can you photograph here?',scope:'These subjects are research awaiting review, not an approved photography guide.',
    GUIDANCE:'Shooting reference',VERIFY:'Needs verification',AUTO:'Automatic evaluation not connected',required:'Conditions needed for the subject',quality:'Conditions that may improve the photograph',
    automatic:'Trusted automatic condition assessment is not supported for this subject yet.',description:'A description of this subject has not been provided.',conditions:'Special shooting conditions have not been provided. This does not mean there are no constraints.'},
  ja:{list:'ここでは何を撮れる？',scope:'これらの題材は審査待ちの調査情報であり、承認済みの撮影ガイドではありません。',
    GUIDANCE:'撮影の参考',VERIFY:'別途確認が必要',AUTO:'自動判定は未接続',required:'撮影に必要な条件',quality:'写真の仕上がりを高める条件',
    automatic:'この題材の信頼できる自動条件判定はまだ利用できません。',description:'この題材の説明はまだ提供されていません。',conditions:'特別な撮影条件は未提供です。制約がないことを意味しません。'}
};
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

for(const [device,width] of [['desktop',1440],['mobile',360]])for(const locale of ['zh-TW','en','ja']){
  test(`${device} ${locale}: deep sample Places plus breadth across all 216, role/mode, missing information and no invented results`,async()=>{
    const context=await browser.newContext({viewport:{width,height:960},isMobile:device==='mobile',hasTouch:device==='mobile'});
    await context.addInitScript(value=>localStorage.setItem('chaselights-v2-locale',value),locale);
    const page=await context.newPage(),errors=[];page.on('pageerror',error=>errors.push(error.message));
    try{
      await page.goto(url);await page.waitForFunction(()=>document.querySelectorAll('.place-button').length===216);
      assert.equal(await page.locator('#research-browser').isVisible(),false,'keep the existing Beta home');
      await page.locator('#browse-research').click();
      // Depth sample: the seven historically reviewed Places plus three admitted
      // breadth-migration Places. Full 216-place depth runs are cost-prohibitive
      // in the browser harness; breadth (structure/count) is asserted below.
      const DEPTH=new Set(['tw-016','tw-026','tw-034','tw-036','tw-082','jp-010','us-071','tw-001','tw-002','jp-001']);
      const seen=new Set();
      for(const place of places.filter(p=>DEPTH.has(p))){
        await page.locator(`.place-button[data-place-id="${place}"]`).click();
        const opportunities=source.opportunities.filter(row=>row.place_id===place);
        assert.equal(await page.locator('.opportunity').count(),opportunities.length);
        assert.equal(await page.locator('.topic-list-heading').textContent(),expected[locale].list);
        assert.equal(await page.locator('.topic-scope').textContent(),expected[locale].scope);
        assert.equal(await page.locator('.topic-jump-list').getAttribute('aria-label'),expected[locale].list);
        assert.equal(await page.locator('.topic-jump-list a').count(),opportunities.length);
        for(const original of opportunities){
          seen.add(original.opportunity_id);
          const card=page.locator(`article[data-opportunity-id="${original.opportunity_id}"]`);
          assert.equal(await card.locator('h3').textContent(),original.name_i18n[locale]);
          assert.equal(await card.locator('.opportunity-description').textContent(),original.description_i18n[locale]);
          assert.deepEqual(await card.locator('.topic-targets li').allTextContents(),original.targets.map(row=>row.name_i18n[locale]));
          assert.ok((await card.locator('.decision-core').innerText()).includes(expected[locale].required));
          assert.ok((await card.locator('.decision-core').innerText()).includes(expected[locale].quality));
          const conditions=original.condition_contract.conditions.filter(row=>row.domain!=='ACCESS_SAFETY');
          assert.equal(await card.locator('.topic-condition').count(),conditions.length);
          for(const condition of conditions){
            const row=card.locator(`.topic-condition[data-condition-id="${original.opportunity_id}/${condition.id}"]`);
            assert.equal(await row.locator('.condition-description').textContent(),condition.notes_i18n[locale]);
            assert.equal(await row.locator('.condition-mode').textContent(),expected[locale][condition.evaluation_mode]);
            assert.ok((await row.locator('.condition-domain').textContent()).length>0);
          }
          assert.equal(await card.locator('.automation-status').textContent(),expected[locale].automatic);
          assert.equal(await card.locator('.access-advisories').count(),1);
          assert.equal(await card.locator('.decision-core .access-advisories').count(),0);
          for(const camera of original.camera_contexts)
            assert.ok((await card.locator('.access-advisories').innerText()).includes(camera.safety_notes_i18n[locale]));
          assert.equal(await card.locator('.technical').getAttribute('open'),null);
          assert.equal(await card.locator('.nav-action,.condition-result,.score,[data-condition-result]').count(),0);
          assert.doesNotMatch(await card.locator('.topic-assessment').innerText(),/\b(PASS|FAIL|UNKNOWN|FAVORABLE)\b/);
        }
        const jump=page.locator('.topic-jump-list a').first();
        await jump.focus();await page.keyboard.press('Enter');
        assert.equal(await page.evaluate(()=>document.activeElement.id),'topic-'+opportunities[0].opportunity_id);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${device} ${place}: horizontal overflow`);
      }
      // Breadth: every admitted Place renders in the research browser; deep
      // per-subject assertions ran on the depth sample above.
      assert.deepEqual([...seen].sort(),
        source.opportunities.filter(row=>DEPTH.has(row.place_id)).map(row=>row.opportunity_id).sort());
      // Existing OR-topic/search behavior must still omit nonmatching subjects.
      if(device==='mobile')await page.locator('#open-filters').click();
      await page.locator('#topic-options input[value="topic:colorful-clouds"]').check();
      await page.locator('.place-button[data-place-id="tw-026"]').click();
      assert.equal(await page.locator('.opportunity,.topic-jump-list a').count(),2,'one matching card and one jump link');
      await page.locator('#language').selectOption(locale==='en'?'ja':'en');
      await page.locator('#language').selectOption(locale);
      assert.equal(await page.locator('.topic-list-heading').textContent(),expected[locale].list);
      assert.equal(await page.locator('.opportunity').count(),1);
      await page.locator('#clear-filters').click();
      await page.locator('.place-button[data-place-id="tw-026"]').click();
      if(device==='mobile')await page.locator('#close-filters').click();
      if(process.env.W4_TOPICS_SCREENSHOT_DIR){
        await mkdir(process.env.W4_TOPICS_SCREENSHOT_DIR,{recursive:true});
        await page.screenshot({path:resolve(process.env.W4_TOPICS_SCREENSHOT_DIR,`${device}-${locale}.png`),fullPage:true});
      }
      // Missing optional research on one subject leaves the other seven usable.
      const changed=structuredClone(source.opportunities);delete changed[0].description_i18n;changed[0].condition_contract.conditions=[];
      changed[1].condition_contract.conditions[0].evaluation_mode='AUTO'; // adversarial metadata only
      const imported={schema_version:'2.1.0',places:source.places,opportunities:changed,
        evaluations:[{opportunity_id:changed[1].opportunity_id,verdict:'PASS',score:100}]};
      await page.locator('#tools-heading').click();
      await page.locator('#file').setInputFiles({name:'test-only-incomplete-research.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(imported))});
      await page.waitForFunction(()=>document.querySelector('#source-value').textContent==='test-only-incomplete-research.json');
      assert.equal(await page.locator('.place-button').count(),216);
      await page.locator(`.place-button[data-place-id="${changed[0].place_id}"]`).click();
      assert.equal(await page.locator('.opportunity-description').textContent(),expected[locale].description);
      assert.ok((await page.locator('.decision-core').innerText()).includes(expected[locale].conditions));
      await page.locator(`.place-button[data-place-id="${changed[1].place_id}"]`).click();
      assert.equal(await page.locator('.opportunity-description').textContent(),changed[1].description_i18n[locale]);
      assert.ok((await page.locator('.decision-core').innerText()).includes(expected[locale].AUTO));
      assert.equal(await page.locator('.condition-result,.score,.nav-action,[data-condition-result]').count(),0);
      assert.doesNotMatch(await page.locator('.topic-assessment').innerText(),/\b(PASS|FAIL|UNKNOWN|FAVORABLE)\b/);
      await page.locator('#close-research').click();
      assert.equal(await page.evaluate(()=>document.activeElement.id),'browse-research');
      assert.deepEqual(errors,[]);
    }finally{await context.close();}
  });
}
