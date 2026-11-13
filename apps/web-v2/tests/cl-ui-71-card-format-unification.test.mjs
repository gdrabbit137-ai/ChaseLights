// CL-UI-71: card format unification (owner实测 CL-UI-63/69 split). Root cause:
// a place whose subject-cards row is missing or has NO suitable entries (e.g.
// tw-002 象山六巨石 / tw-134 1314觀景台 on a status:'failed'·tier:'shootable'
// day) fell through to the old CL-UI-63 「本日最佳題材＋✓符合」 line while
// neighbouring places rendered the CL-UI-69 per-subject rows — one list, two
// card formats. Fix: the fallback renders the SAME row anatomy via a
// synthetic entry (「○ 可拍: HH:MM–HH:MM 🔔」, or the ✗不宜·短因 row when the
// tier is not_recommended), and the retired 「本日最佳題材」 render path is
// removed from the card entirely. Source assertions + extracted fallback
// exercised against the REAL committed subject-cards artifact, per the
// established V1-shell test pattern.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};
const createSpotCardBlock = grab('function createSpotCard', 'function distanceToSpotKm');
const cardsFile = (appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/) || [])[1];
assert.ok(cardsFile, 'subject-cards file name pinned in app.js');
const artifact = JSON.parse(readFileSync(join(ROOT, 'data', 'v2', 'evaluations', cardsFile), 'utf8'));

// ---- extracted fallback builder (real source, stubbed surroundings) ----
function makeFallback() {
  const rowHtml = grab('const clSubjectRowHtml=', 'const clSubjectExtra=');
  // The card runs the builder as an IIFE over the in-scope card vars; the
  // extracted test wrapper takes them as parameters instead (cl-ui-69 style).
  let fallback = grab('const clFallbackRows=', 'const v2Summary=');
  fallback = fallback.replace('const clFallbackRows=(()=>{',
    'const evaluated=(v2Evaluated,v2Best,clSubjectRows,scTierReason,scRow)=>{');
  fallback = fallback.replace(/\}\)\(\);\s*$/, '};');
  assert.ok(fallback.startsWith('const evaluated='), 'extraction rewrap applied');
  const fmt = grab('function formatHourSegments', 'function v2ContractThreshold');
  const prelude = `
    let currentLang='zh-TW';
    const i18nDict={'zh-TW':{v2_tier_shootable:'○ 可拍',v2_tier_not_recommended:'✗ 不宜'}};
    const d=()=>i18nDict[currentLang];
    const esc=s=>String(s);
    const colonSep=()=>'：';
    const listSep=()=>'、';
    const clSubjBell='<button type="button" class="cl-rem-btn cl-rem-compact" data-rem-place="tw-002" data-rem-compact="1"></button>';
    ${fmt}
  `;
  return new Function(prelude + rowHtml + fallback +
    'return {evaluated,formatHourSegments};')();
}

test('CL-UI-71 (1): 象山六巨石/1314 fallback renders the SAME row format — real artifact rows', () => {
  const h = makeFallback();
  // Real committed rows for suitable-empty + shootable days (the shape the
  // fallback exists for). CHALLENGER-14/A: re-anchored to the current
  // same-run artifact — tw-002/tw-134 gained curated suitable rows in the
  // newer run; jp-001/jp-002 carry the same fallback shape on 2026-11-13.
  for (const [spotId, date] of [['jp-001', '2026-11-13'], ['jp-002', '2026-11-13']]) {
    const row = artifact.places[spotId][date];
    assert.ok(row, `${spotId} has a subject-cards row`);
    assert.equal(row.suitable.length, 0, `${spotId} suitable empty on ${date}`);
    assert.equal(row.tier, 'shootable', `${spotId} tier on ${date}`);
    const html = h.evaluated(true, {hours: 1, hoursList: ['18:00']}, '', '', row);
    assert.ok(html.includes('cl-subject-rows') && html.includes('cl-subject-row'), html);
    assert.ok(html.includes('○ 可拍') && html.includes('18:00'), html);
    assert.ok(html.includes('cl-rem-compact') && html.includes('data-rem-place'), 'bell on the fallback row');
    // same anatomy as a curated row (cl-subject-name/colon/window + bell)
    assert.ok(/class="cl-subject-name">○ 可拍<\/span><span class="cl-subject-colon">：<\/span><span class="cl-subject-window">18:00<\/span>/.test(html), html);
  }
});

test('CL-UI-71 (2): 中寮山蓮花亭 keeps the curated rows path — one format per list', () => {
  const row = artifact.places['tw-148']['2026-11-13'];
  assert.ok(row.suitable.length > 0, '中寮山蓮花亭 has suitable entries');
  const h = makeFallback();
  // suitable present → clFallbackRows stays empty; the curated rows render
  const html = h.evaluated(true, {hours: 1, hoursList: ['18:00']}, '<div class="cl-subject-rows"></div>', '', row);
  assert.equal(html, '', 'curated rows win, no fallback duplication');
});

test('CL-UI-71 (3): not_recommended tier keeps the ✗ line — no invented ✓ from hours', () => {
  const h = makeFallback();
  const html = h.evaluated(true, {hours: 1, hoursList: ['18:00']}, '', '霾', {tier: 'not_recommended'});
  assert.ok(html.includes('✗ 不宜') && html.includes('霾'), html);
  assert.ok(!html.includes('○ 可拍'), html);
});

test('CL-UI-71 (4): artifact audit — every suitable-empty day is shootable or not_recommended', () => {
  // The fallback only needs the two tier shapes; a suitable-empty 'recommend'
  // row would need a third branch. Assert the artifact never produces one —
  // except the honest null tier on days the committed weather_details do not
  // cover yet (CHALLENGER-14/A: same-run regeneration reaches the furthest
  // forecast dates; a weather-less row renders no invented verdict).
  let checked = 0, nullTiers = 0;
  for (const [placeId, days] of Object.entries(artifact.places)) {
    for (const [date, row] of Object.entries(days)) {
      if ((row.suitable || []).length) continue;
      if (row.tier === 'shootable' || row.tier === 'not_recommended') { checked++; continue; }
      const h = row.hours || {};
      const weatherless = !(h.ok || []).length && !Object.keys(h.no || {}).length
        && !(h.na || []).length && !(h.unk || []).length;
      assert.equal(row.tier, null, `${placeId} ${date} unexpected tier for a suitable-empty row`);
      assert.ok(weatherless, `${placeId} ${date} null tier must be a weather-less row`);
      nullTiers++;
    }
  }
  assert.ok(checked > 1000, `expected a real corpus, got ${checked}`);
});

test('CL-UI-71 (5): the old 「本日最佳題材」 render path is retired from the card', () => {
  assert.ok(!createSpotCardBlock.includes('v2BestSubjectKey()'), 'best-subject line retired');
  assert.ok(!createSpotCardBlock.includes('v2-chip-ok'), 'hours chip retired');
  assert.ok(!createSpotCardBlock.includes('scShortsHtml'), 'chip second line retired');
  // uniform chain: curated rows → same-format fallback → honest none line
  assert.match(createSpotCardBlock, /class="shooting-summary">\$\{clSummaryHtml\|\|clFallbackRows\|\|v2Summary\|\|/);
  // the fallback uses the SAME row builder (one anatomy everywhere)
  assert.match(createSpotCardBlock, /clSubjectRowHtml\(\{name:d\(\)\.v2_tier_shootable,window:v2Best\.hoursList\},false\)/);
  // the reminder mount (data-rem-opp) survives on the honest none line
  assert.match(createSpotCardBlock, /data-rem-opp="\$\{esc\(v2Best\.oppId\|\|''\)\}"/);
  // the CL-UI-69 row anatomy is untouched
  assert.match(createSpotCardBlock, /class="cl-subject-rows"/);
});

test('CL-UI-71 (6): cache-bust stamp — app.js advanced to clui77 (app.css follows at clui77 per CL-UI-72)', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui77/);
  assert.match(indexSource, /assets\/app\.css\?v=clui77/);
  assert.ok(!indexSource.includes('app.js?v=clui75'), 'stale app.js stamp retired');
});
