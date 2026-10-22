// W5 acceptance contract. Source text comes from the real Catalog, never a
// summary invented by the test or an alternative language fallback.
import assert from 'node:assert/strict';
export const locales=['zh-TW','en','ja'];
// No-review-gate breadth admission (2026-10-22): the catalog is 216 Places /
// 428 Opportunities. Deep browser checks SAMPLE a small place set; breadth is
// asserted by exact counts (full 216-place deep coverage is cost-prohibitive).
export async function verifyPhotographyTopics(page,catalog,locale,sample=3){
  await page.locator('#browse-research').click();
  await page.waitForFunction(()=>document.querySelector('#data-state').dataset.status==='ready');
  assert.equal(await page.locator('.place-button').count(),catalog.places.length,
    'The admitted index must expose every canonical Place');
  const seen=new Set();
  const sampled=catalog.places.slice(0,sample);
  for(const place of sampled){
    await page.locator(`.place-button[data-place-id="${place.place_id}"]`).click();
    const subjects=catalog.opportunities.filter(x=>x.place_id===place.place_id);
    assert.equal(await page.locator('.opportunity').count(),subjects.length);
    assert.equal(await page.locator('.topic-jump-list a').count(),subjects.length);
    for(const subject of subjects){
      seen.add(subject.opportunity_id);
      const card=page.locator(`article[data-opportunity-id="${subject.opportunity_id}"]`);
      assert.equal(await card.locator('.opportunity-description').textContent(),subject.description_i18n[locale]);
      assert.deepEqual(await card.locator('.topic-targets li').allTextContents(),subject.targets.map(x=>x.name_i18n[locale]));
      const conditions=subject.condition_contract.conditions.filter(x=>x.domain!=='ACCESS_SAFETY');
      assert.deepEqual(await card.locator('.condition-description').allTextContents(),conditions.map(x=>x.notes_i18n[locale]));
      assert.equal(await card.locator('.condition-mode').count(),conditions.length);
      assert.equal(await card.locator('.topic-assessment .automation-status').count(),1);
      assert.equal(await card.locator('.decision-core .access-advisories,.condition-result,.score,.nav-action').count(),0);
      assert.equal(await card.locator('.access-advisories').count(),1);
    }
  }
  assert.equal(seen.size,
    sampled.reduce((n,p)=>n+catalog.opportunities.filter(x=>x.place_id===p.place_id).length,0));
  await page.locator('#close-research').click();
}
const copy={
  'zh-TW':{forecast:'目前尚無可用的攝影預報',scope:'研究資料，非指定日期預報。',title:'ChaseLights V2 — 攝影預報',headline:'攝影預報',oldTitle:'ChaseLights V2 — 攝影機會研究',oldHeadline:'從景點與題材，規劃你的拍攝'},
  en:{forecast:'No photography forecast is available yet.',scope:'Research information, not a date-specific forecast.',title:'ChaseLights V2 — Photography forecast',headline:'Photography forecast',oldTitle:'ChaseLights V2 — Photography research',oldHeadline:'Explore places and what to photograph'},
  ja:{forecast:'撮影条件の予報はまだ利用できません。',scope:'調査情報であり、指定日の予報ではありません。',title:'ChaseLights V2 — 撮影予報',headline:'撮影予報',oldTitle:'ChaseLights V2 — 撮影機会の調査',oldHeadline:'撮影地と題材から、撮影を考える'}
};
export async function verifyResearchPage(page,opportunity,locale,ui,placeCount){
  assert.ok(['existing-preview','forecast-home'].includes(ui),'Explicit UI generation required');
  await page.locator('#language').selectOption(locale);
  assert.equal(await page.locator('#language').inputValue(),locale);
  assert.equal(await page.locator('html').getAttribute('lang'),locale==='zh-TW'?'zh-Hant':locale);
  const expected=copy[locale];
  assert.equal(await page.title(),ui==='forecast-home'?expected.title:expected.oldTitle);
  assert.equal(await page.locator('#headline').textContent(),ui==='forecast-home'?expected.headline:expected.oldHeadline);
  if(ui==='forecast-home'){
    assert.equal(await page.locator('#research-browser').isVisible(),false,'Research must be user initiated');
    assert.equal(await page.locator('#forecast-status').textContent(),expected.forecast);
    assert.equal(await page.locator('#research-scope').textContent(),expected.scope);
    assert.equal(await page.locator('.forecast-empty .opportunity,.forecast-empty .score').count(),0);
    await page.locator('#browse-research').click();
    await page.waitForFunction(()=>document.querySelector('#data-state').dataset.status==='ready');
    assert.equal(await page.locator('#browse-research').getAttribute('aria-expanded'),'true');
    if(await page.locator('.place-button').count()>1){
      assert.equal(await page.locator('.place-button').count(),placeCount,
        'The admitted index must expose every canonical Place');
      await page.locator('.place-button[data-place-id="tw-026"]').click();
    }
  }
  await page.locator('.opportunity').first().waitFor({state:'visible',timeout:30000});
  assert.equal(await page.locator('.opportunity').count(),ui==='forecast-home' && await page.locator('.place-button').count()>1?2:1);
  const card=page.locator('.opportunity').first();
  assert.equal(await card.locator('h3').textContent(),opportunity.name_i18n[locale]);
  assert.equal(await card.locator('.opportunity-description').textContent(),opportunity.description_i18n[locale]);
  const warning=card.locator('.access-advisories');
  assert.equal(await warning.isVisible(),true);assert.equal(await warning.getAttribute('role'),'note');
  const camera=opportunity.camera_contexts[0];
  const text=await warning.textContent();
  for(const value of [camera.access_notes_i18n[locale],camera.safety_notes_i18n[locale]])assert.ok(text.includes(value),'Exact source access/safety warning lost');
  const conditions=await card.locator('.decision-core').textContent();
  assert.ok(!conditions.includes(camera.access_notes_i18n[locale]),'Access leaked into photograph requirements');
  for(const condition of opportunity.condition_contract.conditions.filter(x=>x.domain!=='ACCESS_SAFETY' && ['REQUIRED','QUALITY'].includes(x.role)))assert.ok(conditions.includes(condition.notes_i18n[locale]),'Exact condition copy lost');
  assert.equal(await page.locator('.decision-risks,.nav-action,a[href*="/maps/"]').count(),0);
  assert.equal(await card.locator('.decision-unknowns li').count(),opportunity.readiness.gaps.length);
  assert.equal(await card.locator('.technical').getAttribute('open'),null);
  await card.locator('.technical summary').click();
  const advanced=await card.locator('.technical').innerText();
  for(const condition of opportunity.condition_contract.conditions)assert.ok(advanced.includes(condition.notes_i18n[locale]));
  for(const target of opportunity.targets)assert.ok(advanced.includes(target.name_i18n[locale]));
  assert.ok(advanced.includes(camera.access_notes_i18n[locale]));
  assert.ok(advanced.includes(camera.safety_notes_i18n[locale]));
  await card.locator('.technical summary').click();
  const notices=await page.locator('.notice').allTextContents();
  assert.ok(notices.some(s=>/No verifiable|沒有可驗證|検証可能/.test(s)),'Research-only status missing');
  assert.ok(!(await page.locator('body').innerText()).includes('FAVORABLE'));
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth<=1),'Horizontal overflow');
  if(ui==='forecast-home'){
    await page.locator('#close-research').click();
    assert.equal(await page.evaluate(()=>document.activeElement.id),'browse-research');
    assert.equal(await page.locator('#research-browser').isVisible(),false);
  }
}
