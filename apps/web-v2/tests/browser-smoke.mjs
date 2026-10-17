// Run explicitly: node --test apps/web-v2/tests/browser-smoke.mjs
// Missing browser tooling is an environment error, never a silently passing test.
import test, {before, after} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {resolve, extname, sep} from 'node:path';
import {readOriginals, fixtureDirectory, readPinned, W2_SHA} from './pinned-worker2.mjs';

const require = createRequire(import.meta.url);
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/opt/codex/cua_node/lib/node_modules/playwright');
const root = resolve(fileURLToPath(new URL('../', import.meta.url)));
const preview = readPinned('tw-026-P01.research-only.v21.json');
const originals = readOriginals();
const current = originals.find(row => row.opportunity_id === 'tw-026-P01');
const INDEX_SHA='cf29288ce47e2cccb2fb2e1453ad193200996a95';
const expected = {
  'zh-TW': {lang:'zh-Hant',title:'ChaseLights V2 — 攝影預報',skip:'跳至主要內容',
    aria:['語言選擇','資料來源與進階資訊','景點清單','攝影題材與研究資料'],
    headline:'攝影預報',summary:'資料來源與進階資訊',
    notice:'目前沒有可驗證的 V2 即時評估，不提供拍攝適合度或分數。',
    invalid:'資料結構或語系不完整'},
  en: {lang:'en',title:'ChaseLights V2 — Photography forecast',skip:'Skip to main content',
    aria:['Language selection','Data sources and advanced information','Places list','Photography opportunities and research'],
    headline:'Photography forecast',summary:'Data sources and advanced information',
    notice:'No verifiable V2 runtime evaluation; no shooting verdict or score is displayed.',
    invalid:'Invalid structure or incomplete localization'},
  ja: {lang:'ja',title:'ChaseLights V2 — 撮影予報',skip:'メインコンテンツへ移動',
    aria:['言語の選択','データの出典と詳細情報','撮影地一覧','撮影機会と調査資料'],
    headline:'撮影予報',summary:'データの出典と詳細情報',
    notice:'検証可能な V2 実行結果はありません。撮影可否や点数は表示しません。',
    invalid:'構造または翻訳が不完全'}
};
let server, browser, baseURL;
before(async () => {
  server = createServer(async (request, response) => {
    try {
      const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
      const path = resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
      if (!path.startsWith(root + sep)) {response.writeHead(403).end();return;}
      const body = await readFile(path);
      const type = {'.html':'text/html','.mjs':'text/javascript','.css':'text/css','.json':'application/json'}[extname(path)] || 'application/octet-stream';
      response.writeHead(200, {'Content-Type':type});response.end(body);
    } catch {response.writeHead(404).end();}
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  baseURL = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE || '/usr/bin/chromium',
    headless:true,args:['--no-sandbox']});
});
after(async () => {
  await browser?.close();
  if (server) await new Promise(resolve => server.close(resolve));
});

async function switchWithKeyboard(page, locale) {
  await page.locator('#language').focus();
  await page.keyboard.press('Home');
  for (let i=0;i<['zh-TW','en','ja'].indexOf(locale);i++) await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  await page.waitForFunction(value => document.querySelector('#language').value === value &&
    document.documentElement.lang === (value === 'zh-TW' ? 'zh-Hant' : value), locale);
}
async function assertLocale(page, locale) {
  const e = expected[locale];
  await page.locator('.place-button[data-place-id="tw-026"]').click();
  const card=page.locator('.opportunity').filter({has:page.locator('h3',{hasText:current.name_i18n[locale]})});
  assert.equal(await page.title(), e.title);
  assert.equal(await page.locator('#skip-link').textContent(), e.skip);
  assert.equal(await page.locator('#headline').textContent(), e.headline);
  for (const [i,id] of ['language','source-strip','sidebar','detail'].entries())
    assert.equal(await page.locator('#'+id).getAttribute('aria-label'), e.aria[i]);
  assert.equal(await card.locator('h3').textContent(), current.name_i18n[locale]);
  // Photographer decision information precedes optional camera/subject geometry.
  assert.equal(await card.locator('.decision-core').count(), 1);
  assert.equal(await card.locator('.access-advisories').count(), 1);
  assert.equal(await card.locator('.access-advisories').getAttribute('role'),'note');
  assert.equal(await card.locator('.decision-risks').count(), 0,
    'access closures must not appear as photographic blockers');
  assert.equal(await card.locator('.technical .context-grid').count(), 1);
  assert.equal(await card.locator('.context-grid').count(), 1);
  const primaryConditions = await card.locator('.decision-core').innerText();
  for (const condition of current.condition_contract.conditions.filter(x=>x.role==='REQUIRED'||x.role==='QUALITY'))
    assert.ok(primaryConditions.includes(condition.notes_i18n[locale]), locale+': missing decision condition');
  const primary = await card.locator('.decision-core').innerText();
  assert.ok(!primary.includes(current.camera_contexts[0].access_notes_i18n[locale]),
    locale+': closure warning leaked into photo-condition requirements');
  const riskText = await card.locator('.access-advisories').innerText();
  assert.ok(riskText.includes(current.camera_contexts[0].safety_notes_i18n[locale]), locale+': missing access risk');
  assert.ok(riskText.includes(current.camera_contexts[0].access_notes_i18n[locale]), locale+': hidden access restriction');
  assert.equal(await card.locator('.technical').getAttribute('open'), null, 'geometry must be opt-in');
  assert.equal(await card.locator('.technical .context-grid').isVisible(), false);
  assert.ok(await card.evaluate(card => {
    const details=card.querySelector('.technical');
    return ['.decision-core','.access-advisories','.decision-unknowns','.notice'].every(selector =>
      Boolean(card.querySelector(selector)?.compareDocumentPosition(details) & Node.DOCUMENT_POSITION_FOLLOWING));
  }), 'conditions, limitations, unknowns and research warning must precede technical geometry');
  const framing = await card.locator('.framing-note').innerText();
  assert.ok(framing.length > 20 && !framing.includes('FAVORABLE'), locale+': invalid composition guidance');

  assert.equal(await card.locator('.technical summary').textContent(), e.summary);
  assert.equal(await card.locator('.notice').textContent(), e.notice);
  assert.equal(await card.locator('.nav-action').count(), 0);
  assert.equal(await page.locator('a[href*="/maps/"]').count(), 0);
  await card.locator('.technical summary').focus();
  await page.keyboard.press('Enter');
  assert.equal(await card.locator('.technical').getAttribute('open'), '');
  const visible = await card.locator('.technical').innerText();
  const camera = current.camera_contexts[0];
  for (const text of [camera.access_notes_i18n[locale],camera.safety_notes_i18n[locale],
    ...current.condition_contract.conditions.map(condition => condition.notes_i18n[locale])])
    assert.ok(visible.includes(text), `${locale}: missing semantic text ${text}`);
  for (const other of ['zh-TW','en','ja'].filter(value => value !== locale))
    for (const condition of current.condition_contract.conditions)
      assert.ok(!visible.includes(condition.notes_i18n[other]), `${locale}: stale ${other} condition copy`);
  await page.keyboard.press('Enter');
}

for (const [device, viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]]) {
  for (const locale of ['zh-TW','en','ja']) {
    test(`${device} ${locale}: real W2 automatic/imported data, ARIA, keyboard and fail-closed behavior`, async () => {
      const context = await browser.newContext({viewport,isMobile:device === 'mobile',hasTouch:device === 'mobile'});
      const page = await context.newPage();
      const errors = [];page.on('pageerror',error => errors.push(error.message));
      try {
        const response = await page.goto(baseURL);
        assert.equal(response.status(), 200);
        await page.waitForFunction(()=>document.querySelectorAll('.place-button').length===7);
        assert.equal(await page.locator('#research-browser').isVisible(),false);
        assert.equal(await page.locator('.forecast-empty .opportunity').count(),0);
        assert.equal(await page.locator('.opportunity').count(), 1);
        assert.equal(await page.locator('#source-value').textContent(), 'catalog.v2.json');
        assert.equal(await page.locator('#source-commit-value').textContent(), INDEX_SHA);
        // Reach the skip link via a real Tab, then move keyboard focus to main.
        await page.keyboard.press('Tab');
        assert.equal(await page.evaluate(() => document.activeElement.id), 'skip-link');
        await page.keyboard.press('Enter');
        assert.equal(await page.evaluate(() => document.activeElement.id), 'content');
        await switchWithKeyboard(page, locale);
        await page.locator('#browse-research').focus();await page.keyboard.press('Enter');
        assert.equal(await page.evaluate(()=>document.activeElement.id),'research-heading');
        await assertLocale(page, locale);
        // Switch away and back to detect stale localized text and accessible names.
        await switchWithKeyboard(page, locale === 'en' ? 'ja' : 'en');
        await switchWithKeyboard(page, locale);
        await assertLocale(page, locale);
        assert.equal(await page.evaluate(() => localStorage.getItem('chaselights-v2-locale')), locale);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'horizontal overflow');
        await page.reload();await page.locator('#browse-research').click();await page.waitForFunction(()=>document.querySelectorAll('.place-button').length===7);
        if(device==='mobile')await page.locator('#open-filters').click();
        await assertLocale(page, locale);
        // Native file input loads exact pinned W2 preview bytes, without upload.
        await page.locator('#tools-heading').click();
        const posts=[];page.on('request',request => {if(request.method() !== 'GET') posts.push(request.url())});
        await page.locator('#file').setInputFiles(resolve(fixtureDirectory,'tw-026-P01.research-only.v21.json'));
        await page.waitForFunction(() => document.querySelector('#source-value').textContent.endsWith('.research-only.v21.json'));
        await assertLocale(page, locale);
        assert.ok(!(await page.locator('#source-commit-value').textContent()).includes(W2_SHA),
          'original preview has no commit declaration; do not retain the previous source SHA');
        // Adversarial runtime metadata is test-only and must not change the research UI.
        const forged = {...preview,forecast_available:true,evaluations:[{
          opportunity_id:'tw-026-P01',kind:'runtime',contract_status:'ready',source:'test-only-forgery',
          generated_at:preview.generated_at,verdict:'FAVORABLE',score:100
        }]};
        await page.locator('#file').setInputFiles({name:'test-only-forged-runtime.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(forged))});
        await page.waitForFunction(() => document.querySelector('#source-value').textContent === 'test-only-forged-runtime.json');
        await assertLocale(page, locale);
        assert.ok(!(await page.locator('#detail').innerText()).includes('FAVORABLE'));
        // All three original records; no invented research fixture or geometry.
        await page.locator('#file').setInputFiles({name:'pinned-worker2-records.json',mimeType:'application/json',
          buffer:Buffer.from(JSON.stringify({schema_version:'2.1.0',opportunities:originals}))});
        await page.waitForFunction(() => document.querySelectorAll('.place-button').length === 2);
        await page.locator('#search').fill('tw-026');
        assert.equal(await page.locator('.place-button').count(), 1);
        await page.locator('.place-button').focus();
        assert.equal(await page.evaluate(() => document.activeElement.className), 'place-button');
        await page.keyboard.press('Enter');
        await page.waitForFunction(() => document.querySelectorAll('.opportunity').length === 2);
        assert.equal(await page.locator('.place-button').getAttribute('aria-current'), 'true');
        assert.equal(await page.evaluate(() => document.activeElement.className), 'place-button', 'selected place loses keyboard focus');
        assert.equal(await page.locator('.nav-action').count(), 0);
        assert.equal(await page.locator('.notice').count(), 2);
        await page.locator('#search').fill('not-a-real-place');
        assert.equal(await page.locator('.place-button').count(), 0);
        await page.locator('#search').fill('');
        assert.equal(await page.locator('.place-button').count(), 2);
        // Exercise native pointer/touch controls in addition to desktop keyboard flow.
        const selectPlace=page.locator('.place-button[data-place-id="tw-016"]');
        if (device==='mobile') await selectPlace.tap(); else await selectPlace.click();
        await page.waitForFunction(() => document.querySelectorAll('.opportunity').length===1);
        assert.equal(await selectPlace.getAttribute('aria-current'), 'true');
        const summary=page.locator('.technical summary');
        if (device==='mobile') await summary.tap(); else await summary.click();
        assert.equal(await page.locator('.technical .context-grid').isVisible(), true);
        // Reject incomplete localization instead of falling back or keeping old cards.
        const invalid = structuredClone(preview);delete invalid.opportunities[0].name_i18n.en;
        await page.locator('#file').setInputFiles({name:'test-only-invalid-localization.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(invalid))});
        await page.waitForFunction(() => document.querySelector('#data-state').dataset.status === 'invalid');
        assert.equal(await page.locator('.opportunity').count(), 0);
        assert.ok((await page.locator('#data-status').textContent()).includes(expected[locale].invalid));
        assert.equal(await page.locator('.nav-action').count(), 0);
        await page.locator('#close-research').click();
        assert.equal(await page.evaluate(()=>document.activeElement.id),'browse-research');
        assert.equal(await page.locator('#research-browser').isVisible(),false);
        assert.deepEqual(posts, [], 'local import must not upload data');
        assert.deepEqual(errors, [], 'browser runtime errors');
      } finally {await context.close();}
    });
  }
}

// Network scenarios are test-only transports of the byte-pinned research data.
// Every scenario exercises all three locales on both existing device sizes.
const homeExpected = {
  'zh-TW':{forecast:'目前尚無可用的攝影預報',scope:'研究資料，非指定日期預報。',loading:'正在載入景點資料…',unavailable:'景點資料尚未提供，請稍後重試。',error:'暫時無法載入資料，請重試。',invalid:'資料結構或語系不完整，無法使用這份資料。請重試或選取其他檔案。',empty:'目前尚無可瀏覽的景點資料。',missing:'景點名稱尚未提供'},
  en:{forecast:'No photography forecast is available yet.',scope:'Research information, not a date-specific forecast.',loading:'Loading place information…',unavailable:'Place information is not available yet. Please retry later.',error:'Information could not be loaded. Please try again.',invalid:'Invalid structure or incomplete localization. This information cannot be used. Retry or choose another file.',empty:'There is no place information to browse yet.',missing:'Place name not provided'},
  ja:{forecast:'撮影条件の予報はまだ利用できません。',scope:'調査情報であり、指定日の予報ではありません。',loading:'撮影地の情報を読み込んでいます…',unavailable:'撮影地の情報はまだ提供されていません。後でもう一度お試しください。',error:'情報を読み込めませんでした。もう一度お試しください。',invalid:'構造または翻訳が不完全なため、この情報は使用できません。再試行するか、別のファイルを選択してください。',empty:'閲覧できる撮影地の情報はまだありません。',missing:'撮影地の名称は未提供です'}
};
const wait = ms => new Promise(resolve=>setTimeout(resolve,ms));
const scenarios = [
  ['delayed','ready'],['404','unavailable'],['500','error'],['network','error'],
  ['invalidJSON','invalid'],['schemaMismatch','invalid'],['missingLocale','invalid'],['empty','invalid']
];
const catalogBytes = await readFile(resolve(root,'catalog.v2.json'),'utf8');
async function waitStatus(page,status){await page.waitForFunction(s=>document.querySelector('#data-state').dataset.status===s,status);}
async function assertNoForecast(page,locale){
  assert.equal(await page.locator('#forecast-status').textContent(),homeExpected[locale].forecast);
  assert.equal(await page.locator('#research-scope').textContent(),homeExpected[locale].scope);
  assert.equal(await page.locator('.forecast-empty .opportunity, .forecast-empty .score, .nav-action, a[href*="/maps/"]').count(),0);
  assert.ok(!(await page.locator('body').innerText()).includes('FAVORABLE'));
}
for(const [device,viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]]){
  for(const locale of ['zh-TW','en','ja']){
    for(const [scenario,status] of scenarios){
      test(`${device} ${locale}: ${scenario} transport, one-request retry and truthful home`,async()=>{
        const context=await browser.newContext({viewport,isMobile:device==='mobile',hasTouch:device==='mobile'});
        await context.addInitScript(l=>localStorage.setItem('chaselights-v2-locale',l),locale);
        const page=await context.newPage();let requests=0;const errors=[];
        page.on('pageerror',e=>errors.push(e.message));
        await page.route('**/catalog.v2.json',async route=>{
          requests++;
          if(requests>1){await wait(300);await route.fulfill({status:200,contentType:'application/json',body:catalogBytes});return;}
          if(scenario==='delayed')await wait(2000);
          if(scenario==='network'){await route.abort('failed');return;}
          let body=catalogBytes;
          if(scenario==='invalidJSON')body='{broken';
          if(scenario==='empty')body=JSON.stringify({schema_version:'2.1.0',opportunities:[]});
          if(scenario==='schemaMismatch')body=JSON.stringify({...JSON.parse(catalogBytes),schema_version:'9'});
          if(scenario==='missingLocale'){
            const doc=JSON.parse(catalogBytes);delete doc.opportunities[0].camera_contexts[0].safety_notes_i18n.ja;body=JSON.stringify(doc);
          }
          await route.fulfill({status:scenario==='404'?404:scenario==='500'?500:200,contentType:'application/json',body});
        });
        try{
          const started=Date.now();await page.goto(baseURL);
          assert.equal(await page.locator('#research-browser').isVisible(),false);
          assert.equal(await page.locator('#data-tools').getAttribute('open'),null);
          await page.locator('#browse-research').click();
          assert.equal(await page.evaluate(()=>document.activeElement.id),'research-heading');
          if(scenario==='delayed'){
            await waitStatus(page,'loading');
            assert.equal(await page.locator('#data-status').textContent(),homeExpected[locale].loading);
            assert.equal(await page.locator('.opportunity,.place-button').count(),0);
            assert.equal(await page.locator('#retry').isDisabled(),true);
            // Navigation and locale remain usable while the real request is pending.
            await switchWithKeyboard(page,locale==='en'?'ja':'en');
            await switchWithKeyboard(page,locale);
          }
          await waitStatus(page,status);
          if(scenario==='delayed')assert.ok(Date.now()-started>=2000,'must wait for actual two-second response');
          else{
            assert.equal(await page.locator('#data-status').textContent(),homeExpected[locale][status]);
            assert.equal(await page.locator('.opportunity,.place-button').count(),0);
            await page.locator('#tools-heading').click();await page.locator('#source-heading').click();
            assert.ok(!(await page.locator('#source-commit-value').textContent()).includes(W2_SHA));
            await page.locator('#retry').focus();await page.keyboard.press('Enter');
            await waitStatus(page,'loading');
            assert.equal(await page.locator('#data-status').textContent(),homeExpected[locale].loading);
            assert.equal(await page.locator('#retry').isDisabled(),true);
            // Disabled native button rejects repeated pointer/keyboard activation.
            await page.locator('#retry').evaluate(button=>{button.click();button.click();});
            await page.keyboard.press('Enter');
            await switchWithKeyboard(page,locale==='ja'?'en':'ja');
            await switchWithKeyboard(page,locale);
            await waitStatus(page,'ready');
          }
          assert.equal(requests,scenario==='delayed'?1:2);
          await page.waitForFunction(()=>document.querySelectorAll('.place-button').length===7);
          assert.equal(await page.locator('.opportunity').count(),1);
          assert.ok((await page.locator('.place-button strong').allTextContents()).every(Boolean));
          assert.equal(await page.locator('#source-commit-value').textContent(),INDEX_SHA);
          await assertNoForecast(page,locale);
          assert.equal(await page.locator('.access-advisories').isVisible(),true);
          assert.equal(await page.locator('.decision-risks').count(),0);
          if(device==='mobile')await page.locator('#open-filters').click();
          await page.locator('#search').fill('not-a-real-place');
          assert.equal(await page.locator('#data-state').getAttribute('data-status'),'ready');
          assert.equal(await page.locator('.place-button').count(),0);
          await page.locator('#clear-search').click();
          assert.equal(await page.evaluate(()=>document.activeElement.id),'search');
          assert.equal(await page.locator('.place-button').count(),7);
          await page.locator('#close-research').click();
          assert.equal(await page.evaluate(()=>document.activeElement.id),'browse-research');
          assert.deepEqual(errors,[]);
        } finally {await context.close();}
      });
    }
    test(`${device} ${locale}: a failed refresh removes old cards and source rather than retaining stale data`,async()=>{
      const context=await browser.newContext({viewport});const page=await context.newPage();let requests=0;
      await context.addInitScript(l=>localStorage.setItem('chaselights-v2-locale',l),locale);
      await page.route('**/catalog.v2.json',async route=>{
        requests++;await route.fulfill({status:requests===1?200:500,contentType:'application/json',body:catalogBytes});
      });
      try{
        await page.goto(baseURL);await page.locator('#browse-research').click();await waitStatus(page,'ready');
        await page.locator('#retry').click();await waitStatus(page,'error');
        assert.equal(requests,2);assert.equal(await page.locator('.opportunity,.place-button,.nav-action').count(),0);
        assert.ok(!(await page.locator('#source-commit-value').textContent()).includes(W2_SHA));
        assert.equal(await page.locator('#search').isDisabled(),true);
        await assertNoForecast(page,locale);
      }finally{await context.close();}
    });
  }
}

// Full Task 06 sizing remains separate. These are the changed Task 01 screens.
for(const width of [360,390,1440])for(const locale of ['zh-TW','en','ja']){
  test(`${width}px ${locale}: screenshot, overflow and native keyboard controls`,async()=>{
    const context=await browser.newContext({viewport:{width,height:900}});
    await context.addInitScript(l=>localStorage.setItem('chaselights-v2-locale',l),locale);
    const page=await context.newPage();
    try{
      await page.goto(baseURL);await waitStatus(page,'ready');
      await page.waitForFunction(()=>document.querySelectorAll('.place-button').length===7);
      await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'skip-link');
      await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'content');
      await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'browse-research');
      const {mkdir}=await import('node:fs/promises');
      const screenshotDir=resolve(process.env.W4_SCREENSHOT_DIR||'/tmp/chaselights-task-s-browser');
      await mkdir(screenshotDir,{recursive:true});
      await page.screenshot({path:resolve(screenshotDir,`${width}-${locale}-home.png`),fullPage:true});
      await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'research-heading');
      await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'close-research');
      await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'retry');
      await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),width<700?'open-filters':'search');
      if(width<700){await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'search');}
      await page.locator('.place-button').first().focus();assert.equal(await page.evaluate(()=>document.activeElement.className),'place-button');
      await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.className),'place-button');
      await page.locator('.technical summary').focus();assert.equal(await page.evaluate(()=>document.activeElement.tagName),'SUMMARY');
      await page.keyboard.press('Enter');assert.equal(await page.locator('.technical').getAttribute('open'),'');
      // Changing presentation retains selection and the open advanced panel.
      await switchWithKeyboard(page,locale==='en'?'ja':'en');await switchWithKeyboard(page,locale);
      assert.equal(await page.locator('.technical').getAttribute('open'),'');
      assert.equal(await page.locator('.place-button[aria-current="true"]').count(),1);
      await page.screenshot({path:resolve(screenshotDir,`${width}-${locale}-research.png`),fullPage:true});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      for(const id of ['browse-research','close-research','retry','language']){
        const size=await page.locator('#'+id).boundingBox();assert.ok(size.height>=44,id+' requires a 44px control');
      }
      await page.locator('#tools-heading').focus();await page.keyboard.press('Enter');
      await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'file');
      await page.locator('#close-research').focus();await page.keyboard.press('Enter');
      assert.equal(await page.evaluate(()=>document.activeElement.id),'browse-research');
      await assertNoForecast(page,locale);
    }finally{await context.close();}
  });
}

for(const [device,viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]])for(const locale of ['zh-TW','en','ja']){
  test(`${device} ${locale}: local import supersedes delayed fetch without duplicate or stale cards`,async()=>{
    const context=await browser.newContext({viewport});
    await context.addInitScript(l=>localStorage.setItem('chaselights-v2-locale',l),locale);
    const page=await context.newPage();let requests=0,release;
    const pending=new Promise(resolve=>release=resolve);
    await page.route('**/catalog.v2.json',async route=>{
      requests++;await pending;
      // Browser abort may already have canceled this route; generation guards
      // are separately exercised with an abort-ignoring transport in Node.
      await route.fulfill({status:200,contentType:'application/json',body:catalogBytes}).catch(()=>{});
    });
    try{
      await page.goto(baseURL);await page.locator('#tools-heading').click();
      await page.locator('#file').setInputFiles({name:'local-pinned-records.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({schema_version:'2.1.0',opportunities:originals}))});
      await waitStatus(page,'ready');
      assert.equal(await page.locator('.place-button').count(),2);
      assert.equal(await page.locator('#source-value').textContent(),'local-pinned-records.json');
      release();await wait(200);
      assert.equal(requests,1);assert.equal(await page.locator('.place-button').count(),2);
      assert.equal(await page.locator('#source-value').textContent(),'local-pinned-records.json');
      await page.locator('.place-button[data-place-id="tw-026"]').click();
      assert.equal(await page.locator('.opportunity').count(),2);
      await switchWithKeyboard(page,locale==='en'?'ja':'en');await switchWithKeyboard(page,locale);
      assert.equal(await page.locator('.place-button[data-place-id="tw-026"]').getAttribute('aria-current'),'true');
      assert.equal(await page.locator('.opportunity').count(),2);
      await assertNoForecast(page,locale);
    }finally{release();await context.close();}
  });
}
