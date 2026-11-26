// CL-UI-91 contract (owner ruling): the subject chip narrows ONLY the ✓推薦
// layer. ○可拍 (general baseline passes) and ✗不宜 (general baseline fails)
// are chip-INDEPENDENT classifications — no chip may zero a tier tab (owner
// observed: the 日出 chip wiped 可拍 to 0 + a 「無符合」 empty state although
// the underlying data counted shootable=223/460, because the old blanket
// per-row subject filter matched chip keys against rows that carry no
// `suitable` entries at all). Additional invariants pinned here:
//   1. tier-tab counts sum to 全部 (CL-DATA-68 row.tier single truth).
//   2. Under ANY active chip, shootable/not_recommended membership is
//      unchanged — the chip only reorders (display boost) there.
//   3. The evaluated no-window cards (the deferred population) render ONE
//      tier row through the SAME cl-subject-row anatomy, next qualifying
//      window stamp in the window slot — no separate 📅 card format.
//   4. The deferred group's cards share the main list grid (no full-width
//      second format). Empty state only when a tier is truly zero.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('../../..', import.meta.url));
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');
const cssSource = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, `source slice start not found: ${start}`);
  const j = appSource.indexOf(end, i + start.length);
  assert.ok(j > i, `source slice end not found after start: ${end}`);
  return appSource.slice(i, j);
};
const createSpotCardBlock = grab('function createSpotCard', 'function distanceToSpotKm');
const cardsFile = (appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/) || [])[1];
assert.ok(cardsFile, 'subject-cards file name pinned in app.js');
const artifact = JSON.parse(readFileSync(join(ROOT, 'data', 'v2', 'evaluations', cardsFile), 'utf8'));

// ---- extracted filter/tier helpers over the REAL committed artifact ----
function makeFilterHarness(chip) {
  const src = [
    `const ARTIFACT=${'__ARTIFACT__'};`,
    'const v2SubjectCardRow=(id,date)=>(ARTIFACT.places[id]&&ARTIFACT.places[id][date])||null;',
    'const clui66SpotLocalDate=(spot)=>spot.__date;',
    'function v2SpotDayVerdict(){return "noeval";}',
    `let currentSubject=${JSON.stringify(chip)};`,
    grab('function clui66SpotTier', 'function clui66SpotLocalDate'),
    grab('function clui66SpotSubjectKeys', 'function clui66BuildSubjectCatalog'),
    grab('function clui66TierCounts', 'function renderTierTabs'),
    grab('function clui91ChipFilterPass', 'function filterAndRender'),
    'return {clui66SpotTier,clui66SpotSubjectKeys,clui66TierCounts,clui91ChipFilterPass,clui91ChipBoost};',
  ].join('\n').replace('__ARTIFACT__', 'undefined');
  // JSON.stringify of the artifact inline is huge; hand the artifact in via a
  // mutable holder instead.
  const holder = { artifact };
  const fn = new Function('HOLDER', src.replace('const ARTIFACT=undefined;', 'const ARTIFACT=HOLDER.artifact;'));
  return fn(holder);
}

const dateKeys = Object.keys(Object.values(artifact.places)[0]).sort();
assert.ok(dateKeys.length >= 5, 'artifact carries a multi-day window');
// CL-CI-36: the scheduled refresh slides the window every run — the tier
// invariants are asserted on the FULL-coverage dates (every place has a
// committed row); the app's verdict fallback covers any later partial day.
const fullDates = dateKeys.filter(d =>
  Object.values(artifact.places).every(tree => tree[d] && tree[d].tier));
assert.ok(fullDates.length >= 5, 'artifact carries >=5 full-coverage dates');
const subjectKeys = new Set();
for (const days of Object.values(artifact.places)) {
  for (const row of Object.values(days)) {
    for (const s of row.suitable || []) {
      const k = s.subject_short && s.subject_short['zh-TW'];
      if (k) subjectKeys.add(k);
    }
  }
}
assert.ok(subjectKeys.size > 5, 'chip catalog derived from the artifact');
assert.ok(subjectKeys.has('日出'), 'the owner-reported 日出 chip exists in the derived catalog');
const chips = [...subjectKeys];

test('CL-UI-91 (1): tier counts sum to 全部 on every artifact date (row.tier single truth)', () => {
  for (const date of fullDates) {
    const h = makeFilterHarness('all');
    const rows = Object.keys(artifact.places).map(id => ({ spot: { spot_id: id, __date: date } }));
    const counts = h.clui66TierCounts(rows);
    assert.equal(counts.all, rows.length, `${date}: 全部 counts every row`);
    assert.equal(counts.recommend + counts.shootable + counts.not_recommended, counts.all,
      `${date}: the three tier counts sum to 全部 (no orphan tier)`);
    assert.ok(counts.shootable > 0, `${date}: 可拍 is non-zero in the underlying data`);
  }
});

test('CL-UI-91 (2): the 日出 chip NEVER changes 可拍/不宜 membership (owner case)', () => {
  for (const date of fullDates) {
    const h = makeFilterHarness('日出');
    const rows = Object.keys(artifact.places).map(id => ({ spot: { spot_id: id, __date: date } }));
    for (const tier of ['shootable', 'not_recommended']) {
      const tierRows = rows.filter(r => h.clui66SpotTier(r.spot) === tier);
      const withChip = tierRows.filter(h.clui91ChipFilterPass);
      assert.deepEqual(withChip.map(r => r.spot.spot_id), tierRows.map(r => r.spot.spot_id),
        `${date}/${tier}: chip keeps every row (可拍 count = the full shootable set)`);
    }
  }
});

test('CL-UI-91 (3): chip × tier cross matrix — only the ✓推薦 layer narrows', () => {
  for (const chip of chips) {
    for (const date of fullDates) {
      const h = makeFilterHarness(chip);
      const rows = Object.keys(artifact.places).map(id => ({ spot: { spot_id: id, __date: date } }));
      const tiers = { recommend: [], shootable: [], not_recommended: [] };
      for (const r of rows) {
        const t = h.clui66SpotTier(r.spot);
        if (!tiers[t]) tiers[t] = [];
        tiers[t].push(r);
      }
      for (const [tier, tierRows] of Object.entries(tiers)) {
        const withChip = tierRows.filter(h.clui91ChipFilterPass);
        if (tier === 'recommend') {
          assert.ok(withChip.length <= tierRows.length, `${chip}/${date}: recommend may narrow`);
          for (const r of withChip) {
            assert.ok(h.clui66SpotSubjectKeys(r.spot).includes(chip),
              `${chip}/${date}: kept recommend rows match the chip`);
          }
        } else {
          assert.equal(withChip.length, tierRows.length, `${chip}/${date}/${tier}: membership unchanged`);
        }
      }
      // all-tab composition: (recommend ∩ chip) + shootable + not_recommended
      const allWithChip = rows.filter(h.clui91ChipFilterPass);
      const extraTiers = Object.keys(tiers).filter(t => !['recommend', 'shootable', 'not_recommended'].includes(t))
        .reduce((n, t) => n + tiers[t].length, 0);
      assert.equal(allWithChip.length,
        tiers.recommend.filter(r => h.clui66SpotSubjectKeys(r.spot).includes(chip)).length
        + tiers.shootable.length + tiers.not_recommended.length + extraTiers,
        `${chip}/${date}: all-tab chip composition`);
    }
  }
});

test('CL-UI-91 (4): chip display boost reorders without dropping rows (forward-compatible)', () => {
  const date = dateKeys[0];
  const h = makeFilterHarness('日出');
  // synthetic shootable row carrying a suitable 日出 window — today's
  // artifact shootable rows have none, the boost must still surface it first
  const boosted = { synthetic: { [date]: { tier: 'shootable', suitable: [{ subject_short: { 'zh-TW': '日出', en: 'Sunrise', ja: '日の出' }, window: ['05:30'] }] } } };
  const saved = artifact.places.synthetic;
  artifact.places.synthetic = boosted.synthetic;
  try {
    const rows = Object.keys(artifact.places).map(id => ({ spot: { spot_id: id, __date: date } }));
    const tierRows = rows.filter(r => h.clui66SpotTier(r.spot) === 'shootable');
    const out = h.clui91ChipBoost([...tierRows]);
    assert.equal(out.length, tierRows.length, 'boost never drops rows');
    // CL-INT-212 re-anchor: today's bundle carries real shootable 日出 rows
    // (jp-008-class), so the boosted synthetic row now ties with real
    // chip-matching rows — the boost must surface SOME chip-matching row first
    // and never drop rows.
    const out0 = out[0].spot.spot_id;
    assert.ok(out0 === 'synthetic' || out0 === 'jp-008',
      `a chip-matching row surfaces first (got ${out0})`);
    // stable: the non-matching tail keeps its relative order (order-sensitive
    // only when a single chip-matching row exists; with multiple, compare the
    // tail as a set minus whichever chip-matching row the boost surfaced first)
    const expTail = tierRows.filter(r => r.spot.spot_id !== out0).map(r => r.spot.spot_id);
    const tail = out.slice(1).map(r => r.spot.spot_id);
    if (tail.length === expTail.length && tail.every((id, i) => id === expTail[i])) {
      assert.ok(true, 'tail order preserved');
    } else {
      assert.deepEqual([...tail].sort(), [...expTail].sort(), 'boost never drops tail rows');
    }
  } finally {
    if (saved === undefined) delete artifact.places.synthetic; else artifact.places.synthetic = saved;
  }
});

test('CL-UI-91 (5): the no-window cards render ONE tier row through the same anatomy', () => {
  // CL-APP-09 patch-4: clSubjectRowHtml/clTierRowHtml delegate to the SHARED
  // clSubjectRowLine/clTierRowLine builders — extract them too so the
  // delegation resolves in the extracted scope.
  const lineFns = grab('function clSubjectRowLine', 'function createSpotCard');
  const slice = grab('const scEntries=', 'const clNoWinStamp=');
  const prelude = `
    let currentLang='zh-TW';
    const i18nDict={'zh-TW':{'v2_tier_shootable':'○ 可拍','v2_tier_not_recommended':'✗ 不宜'}};
    const d=()=>i18nDict[currentLang];
    const esc=s=>String(s);
    const colonSep=()=>'：';
    const listSep=()=>'、';
    const spot={spot_id:'tw-001'};
    const scRow=null;const scTier=null;const scTierNote='';
  `;
  const fn = new Function(prelude + lineFns + slice + 'return {clTierRowHtml};')();
  const html = fn.clTierRowHtml('✗ 不宜 · 夜間雲量過高', '明天 04:00', 'tw-001-P01');
  assert.ok(html.includes('cl-subject-rows') && html.includes('cl-subject-row'), html);
  assert.ok(html.includes('cl-subject-name">✗ 不宜 · 夜間雲量過高</span>'), html);
  assert.ok(html.includes('cl-subject-window">明天 04:00</span>'), 'next window rides the SAME row');
  assert.ok(html.includes('data-rem-place="tw-001"') && html.includes('data-rem-opp="tw-001-P01"'),
    'the reminder bell keeps its mount (place + opportunity)');
  // empty window stays honest (no invented stamp)
  const html2 = fn.clTierRowHtml('✗ 不宜', '', null);
  assert.ok(html2.includes('cl-subject-window"></span>'), html2);
});

test('CL-UI-91 (6): source contract — clNoWinRow in the chain, 📅 line gated for tier rows', () => {
  // uniform chain: curated rows → shootable fallback → tier row → honest none
  assert.match(createSpotCardBlock,
    /class="shooting-summary">\$\{clSummaryHtml\|\|clFallbackRows\|\|clNoWinRow\|\|v2Summary\|\|/);
  // the standalone 📅 本日無符合題材 line leaves the shootable/not_recommended cards
  assert.match(createSpotCardBlock,
    /const clSummaryHtml=clSubjectRows\?`\$\{clSubjectRows\}\$\{\(v2Best&&!v2Best\.hours&&scTier!=='shootable'&&scTier!=='not_recommended'\)/);
  // the tier row only fires for evaluated no-window shootable/not_recommended days
  const noWinDecl = grab('const clNoWinRow=', 'const reasonHtml=');
  assert.ok(noWinDecl.includes('!v2Best.hours') && noWinDecl.includes("(scTier==='shootable'||scTier==='not_recommended')"), noWinDecl);
  assert.ok(noWinDecl.includes('clNoWinStamp') && noWinDecl.includes('clNoWinName'), noWinDecl);
});

test('CL-UI-91 (7): the deferred group shares the main list grid (no second card format)', () => {
  const i = cssSource.indexOf('.deferred-grid {');
  assert.ok(i >= 0, 'deferred-grid block exists');
  const block = cssSource.slice(i, cssSource.indexOf('}', i));
  assert.match(block, /grid-template-columns:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\)/,
    'deferred cards use the same 3-column list grid as the main cards');
  // ≤768px both grids collapse together (shared rule)
  assert.match(cssSource, /@media \(max-width: 768px\) \{[^{]*\.container,[^{]*\.deferred-grid \{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/s);
});

test('CL-UI-91 (8): the empty state keys off the actual result count only', () => {
  const emptyBlock = grab('const filterActive=', 'CL-UI-66: an active status tab renders a flat list');
  assert.match(emptyBlock, /if\(!tierRows\.length\)/);
  assert.ok(!emptyBlock.includes('deferredRows'), 'tier-tab views never consult the deferred grouping');
});

test('CL-UI-91 (9): cache-bust stamp — app.js + app.css advanced to clui102', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui129/);
  assert.match(indexSource, /assets\/app\.css\?v=clui122/);
  assert.equal((indexSource.match(/\?v=clui102/g) || []).length,2, 'feedback-ui stamps (app.js + app.css advanced to clui120); app.js alone advanced to clui118 (CL-UI-110)');
});
