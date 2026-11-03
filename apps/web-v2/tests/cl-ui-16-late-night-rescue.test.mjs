// CL-UI-16: late-night rescue (today main grid = 0 viable → tomorrow's
// suggestions with an honest tomorrow badge + banner) and the sparse featured
// mode (1..SPARSE_MAIN_THRESHOLD viable cards → flat hours-desc list instead of
// sparse region grouping). Owner rulings 2026-11-03. All paths reuse the
// existing v2SpotDayVerdict evaluation source — no new evaluation path; the
// CL-UI-14 fail-closed semantics are untouched.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const block=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,appSource.indexOf(start))
);
const filterAndRenderBlock=block('function filterAndRender','function opportunityScoreClass');
const compareBlock=block('function lateNightHoursCompare','function buildLateNightBanner');
const bannerBlock=block('function buildLateNightBanner','function userFacingResearchValue');
const i18nBlock=block('const i18nDict = {','const categoryKeys = {');
const switchDayBlock=block('function switchDay','function switchLanguage');
const CL16_KEYS=['late_night_banner_sparse','late_night_banner','late_night_banner_both','back_today','tomorrow_badge'];

test('CL-UI-16 (a): sparse featured mode — flat hours-desc list under the threshold',()=>{
  assert.match(appSource,/const SPARSE_MAIN_THRESHOLD=4;/,'threshold constant exists (adjustable value, owner-suggested 4)');
  assert.match(filterAndRenderBlock,
    /const sparseFeatured=lateNightToday&&viableRows\.length>0&&viableRows\.length<=SPARSE_MAIN_THRESHOLD;/);
  // Featured branch: banner + flat card list (no appendSpotRows / region grouping).
  assert.match(filterAndRenderBlock,
    /if\(sparseFeatured\)\{[^}]*buildLateNightBanner\(d\(\)\.late_night_banner_sparse\)[\s\S]*?\}\s*else if\(lateNightTomorrowRows\)\{/);
  assert.match(filterAndRenderBlock,
    /\[\.\.\.viableRows\]\.sort\(lateNightHoursCompare\)\.forEach\(\(\{spot,metric\}\)=>container\.appendChild\(createSpotCard\(spot,metric\)\)\);/);
  // The comparator is hours desc (qualifying hours high→low) with a
  // geographic tiebreak — a pure, test-executable function.
  assert.match(compareBlock,/const av=v2HoursSortValue\(a\.spot\),bv=v2HoursSortValue\(b\.spot\);/);
  assert.match(compareBlock,/return bv-av;/);
  assert.match(compareBlock,/return compareGeographic\(a,b\);/);
  // The banner copy answers the photographer first (plain language, honest).
  const sparseKeys=[...i18nBlock.matchAll(/late_night_banner_sparse:'([^']*)'/g)].map(m=>m[1]);
  assert.equal(sparseKeys.length,3);
  sparseKeys.forEach(v=>assert.ok(v.length>8));
});

test('CL-UI-16 (b): normal mode (>threshold) keeps the region grouping path',()=>{
  // The default branch still routes through the shared grouping renderer.
  assert.match(filterAndRenderBlock,/appendSpotRows\(container,viableRows\);/);
  // The sparse branch never calls appendSpotRows.
  const sparseBranch=filterAndRenderBlock.slice(filterAndRenderBlock.indexOf('if(sparseFeatured)'));
  const branchBody=sparseBranch.slice(0,sparseBranch.indexOf('}else if(lateNightTomorrowRows)'));
  assert.equal(/appendSpotRows/.test(branchBody),false,'featured mode must render a flat list, not region groups');
});

test('CL-UI-16 (c): today 0 viable → tomorrow cards with an honest badge + banner',()=>{
  // Detection reuses the existing verdict (no new evaluation path): the
  // tomorrow pass re-runs v2SpotDayVerdict under a scoped dayOffsetOverride=1.
  assert.match(filterAndRenderBlock,/if\(lateNightToday&&viableRows\.length===0&&deferredRows\.length>0\)\{/);
  assert.match(filterAndRenderBlock,/dayOffsetOverride=1;\s*try\{rows\.forEach\(row=>\{if\(v2SpotDayVerdict\(row\.spot\)==='viable'\)tRows\.push\(row\);\}\);\}\s*finally\{dayOffsetOverride=null;\}/);
  // Honest labeling: a visible tomorrow badge on every rescue card, plus the
  // banner with a "back to today" switch. Cards are never presented as today.
  assert.match(filterAndRenderBlock,/buildLateNightBanner\(d\(\)\.late_night_banner,true\)/);
  assert.match(filterAndRenderBlock,/card\.querySelector\('\.spot-title-group'\)\.insertAdjacentHTML\('afterbegin',`<span class="tomorrow-badge">\$\{esc\(d\(\)\.tomorrow_badge\)\}<\/span>`\);/);
  assert.match(bannerBlock,/data-late-night-back/);
  assert.match(bannerBlock,/lateNightRescueDismissed=true;filterAndRender\(\);/);
  // The rescue card render itself is scoped to tomorrow semantics.
  assert.match(filterAndRenderBlock,/dayOffsetOverride=1;\s*try\{\s*lateNightTomorrowRows\.forEach\(row=>\{row\.metric=getMetric\(row\.spot\);\}\);/);
  // Switching to another date tab re-arms the rescue.
  assert.match(switchDayBlock,/if\(k!=='today'\)lateNightRescueDismissed=false;/);
  const badgeKeys=[...i18nBlock.matchAll(/tomorrow_badge:'([^']*)'/g)].map(m=>m[1]);
  assert.equal(badgeKeys.length,3);
  badgeKeys.forEach(v=>assert.ok(v.length>0));
});

test('CL-UI-16 (d): today and tomorrow both 0 → honest both-none banner, collapsed groups kept',()=>{
  assert.match(filterAndRenderBlock,
    /else if\(lateNightToday&&viableRows\.length===0&&deferredRows\.length>0&&!lateNightRescueDismissed\)\{\s*container\.appendChild\(buildLateNightBanner\(d\(\)\.late_night_banner_both\)\);\s*\}/);
  const bothKeys=[...i18nBlock.matchAll(/late_night_banner_both:'([^']*)'/g)].map(m=>m[1]);
  assert.equal(bothKeys.length,3);
  bothKeys.forEach(v=>assert.ok(v.length>8));
  // The collapsed groups still render in every mode (deferred/no-eval cards
  // stay reachable below the banner).
  assert.match(filterAndRenderBlock,/d\(\)\.no_viable_group\.replace\('\{n\}',deferredRows\.length\)/);
  assert.match(filterAndRenderBlock,/d\(\)\.no_eval_group\.replace\('\{n\}',noEvalRows\.length\)/);
});

test('CL-UI-16 (e): banner + back-to-today copy exist in all three dictionaries',()=>{
  CL16_KEYS.forEach(key=>{
    const values=[...i18nBlock.matchAll(new RegExp(key+':','g'))].map(m=>m[0]);
    assert.equal(values.length,3,`${key} must exist in zh-TW/en/ja`);
    values.forEach(v=>assert.ok(v.trim().length>0,`${key} must be non-empty`));
  });
  // The en banner uses an apostrophe-bearing string via double quotes — make
  // sure the key is still greppable in its quoted form.
  assert.match(appSource,/late_night_banner:"Today's shooting hours have ended — showing tomorrow's suggestions"/);
});

test('CL-UI-16 (f): executing the selectedDayOffset override + hours sort for real',()=>{
  const extract=(start,end,fn,prelude='')=>{
    const src=appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));
    return new Function(`${prelude}\n${src}\nreturn ${fn};`)();
  };
  // dayOffsetOverride scoping: null → filter value, 1 → tomorrow even on today.
  const selectedDayOffset=extract(
    'function selectedDayOffset','function localDateString','selectedDayOffset',
    "let dayOffsetOverride=null;let currentDayFilter='today';"
  );
  assert.equal(selectedDayOffset(),0);
  const selectedDayOffsetTomorrow=extract(
    'function selectedDayOffset','function localDateString','selectedDayOffset',
    "let dayOffsetOverride=1;let currentDayFilter='today';"
  );
  assert.equal(selectedDayOffsetTomorrow(),1,'the rescue render must evaluate offset 1 while scoped');
  const selectedDayOffsetAfter=extract(
    'function selectedDayOffset','function localDateString','selectedDayOffset',
    "let dayOffsetOverride=null;let currentDayFilter='tomorrow';"
  );
  assert.equal(selectedDayOffsetAfter(),1,'without the override the tab value drives the offset');
  // The featured-list comparator orders by qualifying hours high→low.
  const compare=extract(
    'function lateNightHoursCompare','function buildLateNightBanner','lateNightHoursCompare',
    'function v2HoursSortValue(s){return s.hours;}const compareGeographic=()=>0;'
  );
  const rows=[{spot:{hours:3}},{spot:{hours:9}},{spot:{hours:5}}];
  const sorted=[...rows].sort(compare);
  assert.deepEqual(sorted.map(r=>r.spot.hours),[9,5,3],'featured list must be qualifying hours high→low');
  // v2HoursSortValue fails closed (null) for a place without opportunities.
  const v2HoursSortValue=extract(
    'function v2HoursSortValue','function v2DayHtml','v2HoursSortValue',
    `let dayOffsetOverride=null;let currentDayFilter='today';
     const v2EvalBundle={places:[{place_id:'c',opportunities:[]}]};
     function localeText(x){return null;}
     function selectedDayOffset(){return dayOffsetOverride!==null?dayOffsetOverride:0;}`
  );
  assert.equal(v2HoursSortValue({spot_id:'c'}),null);
});

test('CL-UI-16 (g): CSS ships the banner, back button and tomorrow badge',()=>{
  assert.match(cssSource,/\.late-night-banner\{/);
  assert.match(cssSource,/\.late-night-back\{/);
  assert.match(cssSource,/\.tomorrow-badge\{/);
  // Mobile (390px): the banner wraps instead of overflowing.
  assert.match(cssSource,/\.late-night-banner\{[\s\S]*?flex-wrap:\s*wrap/);
});