// Run explicitly: node --test apps/web-v2/tests/browser-smoke.mjs
// Missing browser tooling is an environment error, never a silently passing test.
import test, {before, after} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {resolve, extname, sep} from 'node:path';
import {readOriginals, fixtureDirectory, readPinned} from './pinned-worker2.mjs';

const require = createRequire(import.meta.url);
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/opt/codex/cua_node/lib/node_modules/playwright');
const root = resolve(fileURLToPath(new URL('../', import.meta.url)));
const preview = readPinned('tw-026-P01.research-only.v21.json');
const originals = readOriginals();
const current = originals.find(row => row.opportunity_id === 'tw-026-P01');
const expected = {
  'zh-TW': {lang:'zh-Hant',title:'ChaseLights V2 — 攝影機會研究',skip:'跳至主要內容',
    aria:['語言選擇','資料來源與時效','景點清單','攝影題材與研究資料'],
    headline:'從拍攝位置，看見真正的拍攝主體',summary:'研究條件、未知項與證據',
    notice:'目前沒有可驗證的 V2 即時評估，不提供拍攝適合度或分數。',
    invalid:'資料結構或語系不完整'},
  en: {lang:'en',title:'ChaseLights V2 — Photography research',skip:'Skip to main content',
    aria:['Language selection','Data provenance and freshness','Places list','Photography opportunities and research'],
    headline:'From camera location to photographic subject',summary:'Research conditions, unknowns and evidence',
    notice:'No verifiable V2 runtime evaluation; no shooting verdict or score is displayed.',
    invalid:'Invalid structure or incomplete localization'},
  ja: {lang:'ja',title:'ChaseLights V2 — 撮影機会の調査',skip:'メインコンテンツへ移動',
    aria:['言語の選択','資料の出典と更新時刻','撮影地一覧','撮影機会と調査資料'],
    headline:'撮影地点から被写体まで、関係を明確に',summary:'調査条件・不明点・根拠',
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
  assert.equal(await page.title(), e.title);
  assert.equal(await page.locator('#skip-link').textContent(), e.skip);
  assert.equal(await page.locator('#headline').textContent(), e.headline);
  for (const [i,id] of ['language','source-strip','sidebar','detail'].entries())
    assert.equal(await page.locator('#'+id).getAttribute('aria-label'), e.aria[i]);
  assert.equal(await page.locator('.opportunity h3').textContent(), current.name_i18n[locale]);
  assert.equal(await page.locator('.technical summary').textContent(), e.summary);
  assert.equal(await page.locator('.notice').textContent(), e.notice);
  assert.equal(await page.locator('.nav-action').count(), 0);
  assert.equal(await page.locator('a[href*="/maps/"]').count(), 0);
  await page.locator('.technical summary').focus();
  await page.keyboard.press('Enter');
  assert.equal(await page.locator('.technical').getAttribute('open'), '');
  const visible = await page.locator('.technical').innerText();
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
        await page.waitForSelector('.opportunity');
        assert.equal(await page.locator('.opportunity').count(), 1);
        assert.equal(await page.locator('#source-value').textContent(), 'catalog.v2.json');
        // Reach the skip link via a real Tab, then move keyboard focus to main.
        await page.keyboard.press('Tab');
        assert.equal(await page.evaluate(() => document.activeElement.id), 'skip-link');
        await page.keyboard.press('Enter');
        assert.equal(await page.evaluate(() => document.activeElement.id), 'content');
        await switchWithKeyboard(page, locale);
        await assertLocale(page, locale);
        // Switch away and back to detect stale localized text and accessible names.
        await switchWithKeyboard(page, locale === 'en' ? 'ja' : 'en');
        await switchWithKeyboard(page, locale);
        await assertLocale(page, locale);
        assert.equal(await page.evaluate(() => localStorage.getItem('chaselights-v2-locale')), locale);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, 'horizontal overflow');
        await page.reload();await page.waitForSelector('.opportunity');
        await assertLocale(page, locale);
        // Native file input loads exact pinned W2 preview bytes, without upload.
        const posts=[];page.on('request',request => {if(request.method() !== 'GET') posts.push(request.url())});
        await page.locator('#file').setInputFiles(resolve(fixtureDirectory,'tw-026-P01.research-only.v21.json'));
        await page.waitForFunction(() => document.querySelector('#source-value').textContent.endsWith('.research-only.v21.json'));
        await assertLocale(page, locale);
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
        await page.locator('#search').press('Tab');
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
        // Reject incomplete localization instead of falling back or keeping old cards.
        const invalid = structuredClone(preview);delete invalid.opportunities[0].name_i18n.en;
        await page.locator('#file').setInputFiles({name:'test-only-invalid-localization.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(invalid))});
        await page.waitForFunction(() => document.querySelectorAll('.opportunity').length === 0);
        assert.ok((await page.locator('#data-status').textContent()).includes(expected[locale].invalid));
        assert.equal(await page.locator('.nav-action').count(), 0);
        assert.deepEqual(posts, [], 'local import must not upload data');
        assert.deepEqual(errors, [], 'browser runtime errors');
      } finally {await context.close();}
    });
  }
}
