// CL-UI-63: card second line (card redesign step 2). The homepage card's
// second line carries the verdict + short subject chips from the derived
// subject-cards layer (CL-UI-62 artifact): suitable -> ✓ Met · window · up to
// 4 short names + "+N" fold; not-met -> ✗ Not met · one short weather word.
// The long-sentence fail reason leaves the card and stays in the place modal
// day rows (題材展開區). Source assertions + extracted pure helpers, per the
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
const artifact = JSON.parse(readFileSync(
  join(ROOT, 'data', 'v2', 'evaluations', 'subject-cards-20261112T202312Z.json'), 'utf8'));

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};
const createSpotCardBlock = grab('function createSpotCard', 'function distanceToSpotKm');

// Pure subject-card helpers over an injectable tree (the fetch layer is not
// exercised here; the pipeline wiring is asserted on the source).
const helperCode = grab('const V2_SUBJECT_CARDS_FILE', '// CL-UI-26: every 不符 verdict');
const makeHelpers = (tree) => new Function(
  `${helperCode}\nv2SubjectCards=${JSON.stringify(tree)};\n` +
  'return {V2_SUBJECT_CARDS_FILE,v2SubjectCardRow,v2SubjectCardShorts,v2SubjectCardShortReason};')();

const ARTIFACT_FILE = 'subject-cards-20261112T202312Z.json';

test('CL-UI-63 (1): subject-cards layer loads inside the existing evaluations fetch flow', () => {
  // Bound into ensureV2EvalBundle — the same gated fetch that already feeds
  // the card verdict; a load failure degrades to chip-less lines, never a
  // blocked render.
  assert.match(appSource,
    /\.then\(j=>\{v2EvalBundle=j;return Promise\.all\(\[ensureFailOverrides\(\),ensureSubjectCards\(\)\]\)\.then\(\(\)=>j\);\}\)/);
  assert.match(appSource, /fetch\('\.\/data\/v2\/evaluations\/'\+V2_SUBJECT_CARDS_FILE,\{cache:'no-cache'\}\)/);
  assert.ok(helperCode.includes(`'${ARTIFACT_FILE}'`), 'artifact filename pinned');
  // fetch failure resets the promise and yields null — same fail-open-to-null
  // contract as the other card feeds.
  assert.match(appSource, /catch\(\(\)=>\{v2SubjectCardsPromise=null;return null;\}\)/);
});

test('CL-UI-63 (2): row lookup keys on the selected date (date switching updates)', () => {
  const h = makeHelpers(artifact);
  assert.equal(h.V2_SUBJECT_CARDS_FILE, ARTIFACT_FILE);
  // A real place with two different days: 2026-11-13 clear (has suitable),
  // 2026-11-15 failed — switching the date must switch the row.
  // (CHALLENGER-14/A: re-anchored to the current same-run artifact — jp-003's
  // 11-13 row became failed in the newer run, jp-005 carries the pair.)
  const clearRow = h.v2SubjectCardRow('jp-005', '2026-11-13');
  const failedRow = h.v2SubjectCardRow('jp-005', '2026-11-15');
  assert.ok(clearRow, 'clear day row exists');
  assert.ok(failedRow, 'failed day row exists');
  assert.equal(clearRow.status, 'clear');
  assert.equal(failedRow.status, 'failed');
  assert.ok(clearRow.suitable.length > 0 && failedRow.suitable.length === 0,
    'the two dates really differ');
  assert.equal(h.v2SubjectCardRow('jp-003', '1999-01-01'), null);
  assert.equal(h.v2SubjectCardRow('no-such-place', '2026-11-13'), null);
  // The card render keys the lookup on the selected day's own local_date (the
  // same anchor as the verdict), so a date switch re-resolves the row.
  assert.match(createSpotCardBlock,
    /v2SubjectCardRow\(spot\.spot_id,v2Best\.day\.local_date\)/);
});

test('CL-UI-63 (3): short subject names dedupe, resolve per language, fold past 4', () => {
  const h = makeHelpers({});
  // duplicates (two same-genre opportunities on one date) collapse to one
  const dupRow = {suitable: [
    {subject_short: {'zh-TW': '夜景', en: 'Night view', ja: '夜景'}},
    {subject_short: {'zh-TW': '夜景', en: 'Night view', ja: '夜景'}},
    {subject_short: {'zh-TW': '銀河', en: 'Galaxy', ja: '銀河'}}]};
  assert.deepEqual(h.v2SubjectCardShorts(dupRow, 'zh-TW'), ['夜景', '銀河']);
  assert.deepEqual(h.v2SubjectCardShorts(dupRow, 'en'), ['Night view', 'Galaxy']);
  // zh-TW fallback keeps a partial entry usable
  assert.deepEqual(
    h.v2SubjectCardShorts({suitable: [{subject_short: {'zh-TW': '山景'}}]}, 'en'), ['山景']);
  assert.deepEqual(h.v2SubjectCardShorts({suitable: []}, 'zh-TW'), []);
  assert.deepEqual(h.v2SubjectCardShorts(null, 'zh-TW'), []);
  // CL-UI-71: the CL-UI-63 chip fold left the card with the old format —
  // the card folds per-subject ROWS instead (cl-ui-69, at most 3 + +N) and
  // the suitable-empty fallback renders the tier row (see CL-UI-63 (5)).
  assert.ok(!createSpotCardBlock.includes('scShortsHtml'), 'chip second line retired');
  assert.ok(createSpotCardBlock.includes('clSubjectRows'), 'per-subject rows are the card surface');
});

test('CL-UI-63 (4): not-met line renders ONE short word, no sentence', () => {
  const h = makeHelpers({});
  assert.equal(h.v2SubjectCardShortReason(
    {dominant_reason: {'zh-TW': '霾', en: 'haze', ja: '霞'}}, 'zh-TW'), '霾');
  assert.equal(h.v2SubjectCardShortReason(
    {dominant_reason: {'zh-TW': '霾', en: 'haze', ja: '霞'}}, 'en'), 'haze');
  assert.equal(h.v2SubjectCardShortReason({dominant_reason: null}, 'zh-TW'), '');
  assert.equal(h.v2SubjectCardShortReason(null, 'zh-TW'), '');
  // no sentence ever reaches the line: zh-TW words are ≤6 chars and no
  // language copy carries sentence punctuation
  for (const days of Object.values(artifact.places)) {
    for (const row of Object.values(days)) {
      if (!row.dominant_reason) continue;
      assert.ok(row.dominant_reason['zh-TW'].length <= 6,
        `short word too long: ${row.dominant_reason['zh-TW']}`);
      for (const lang of ['zh-TW', 'en', 'ja']) {
        assert.ok(!/[，。！？、]/.test(row.dominant_reason[lang]),
          `sentence punctuation in short word: ${row.dominant_reason[lang]}`);
      }
    }
  }
  // CL-UI-65: the fallback (no curated reason) UNFAVORABLE line still starts
  // with the bare ✗ 未符 verdict glyph
  assert.match(createSpotCardBlock,
    /\(v2Best\.state==='UNFAVORABLE'\?`<div class="best-window-row card-second-line"><span class="v2-line-verdict v2-verdict-bad">\$\{esc\(d\(\)\.card_line_bad\)\}<\/span>/);
  // CL-UI-65 owner ruling: the second line is three-tier and covers
  // UNFAVORABLE and NOT_EVALUABLE days (tier is derived from real weather,
  // not an invented verdict)
  const scSecondLineDecl = grab('const scSecondLine=', 'const opportunityName=');
  assert.ok(scSecondLineDecl.includes("v2_tier_shootable") &&
    scSecondLineDecl.includes("v2_tier_not_recommended"),
    'second line carries the shootable / not-recommended tiers');
  assert.ok(scSecondLineDecl.includes("v2Best.state==='UNFAVORABLE'||v2Best.state==='NOT_EVALUABLE'"),
    'second line covers UNFAVORABLE and NOT_EVALUABLE days');
});

test('CL-UI-63 (5): suitable-empty fallback renders the SAME row format (CL-UI-71)', () => {
  // tw-002/tw-134 style day: subject-cards row present but suitable [] while
  // the eval bundle still has qualifying hours — the card must NOT fall back
  // to the retired 本日最佳題材 line; it renders one synthetic row
  // 「○ 可拍: HH:MM–HH:MM 🔔」 through the same clSubjectRowHtml.
  assert.match(createSpotCardBlock, /const clFallbackRows=/);
  assert.match(createSpotCardBlock, /clSubjectRowHtml\(\{name:d\(\)\.v2_tier_shootable,window:v2Best\.hoursList\},false\)/);
  assert.match(createSpotCardBlock, /v2_tier_not_recommended\+\(scTierReason\?' · '\+scTierReason:''/);
  // the window anchor stays the card's existing v2EffectiveHours list — the
  // card can never advertise hours the modal contradicts (CL-UI-12/43).
  assert.match(createSpotCardBlock, /window:v2Best\.hoursList/);
  // the retired old-format line is gone from the card block entirely
  assert.ok(!createSpotCardBlock.includes("d()[v2BestSubjectKey()]"), '本日最佳題材 line retired');
  assert.ok(!createSpotCardBlock.includes('v2-chip-ok'), 'hours chip retired');
});

test('CL-UI-63 (6): the long-sentence reason left the card and lives in the modal', () => {
  assert.equal(createSpotCardBlock.includes('v2FailReasonSuffix'), false,
    'card must not render the long-sentence fail reason');
  assert.equal(createSpotCardBlock.includes('forecast-status-row'), false,
    'status row retired from the card');
  // the modal day rows keep the full plain-language reason (題材展開區)
  assert.match(appSource,
    /const failReason=\(day\.state!=='GUIDANCE_SATISFIED'\)\?v2DominantFailReason\(day\.conditions,spot,genre,opportunityId\):null;/);
  assert.match(appSource, /\$\{esc\(d\(\)\.v2_fail_reason\)\}\$\{esc\(failReason\)\}/);
});

test('CL-UI-63 (7): verdict glyphs exist in all three dictionaries', () => {
  const i18n = grab('const i18nDict = {', 'const categoryKeys = {');
  assert.deepEqual([...i18n.matchAll(/card_line_ok:'([^']*)'/g)].map(m => m[1]),
    ['✓ 符合', '✓ Met', '✓ 達成']);
  assert.deepEqual([...i18n.matchAll(/card_line_bad:'([^']*)'/g)].map(m => m[1]),
    ['✗ 未符', '✗ Not met', '✗ 未達成']);
  // CL-UI-65 three-tier copy exists in all three dictionaries
  assert.deepEqual([...i18n.matchAll(/v2_tier_recommend:'([^']*)'/g)].map(m => m[1]),
    ['✓ 推薦', '✓ Recommended', '✓ 推薦']);
  assert.deepEqual([...i18n.matchAll(/v2_tier_shootable:'([^']*)'/g)].map(m => m[1]),
    ['○ 可拍', '○ Shootable', '○ 撮影可']);
  assert.deepEqual([...i18n.matchAll(/v2_tier_not_recommended:'([^']*)'/g)].map(m => m[1]),
    ['✗ 不宜', '✗ Not recommended', '✗ 非推奨']);
  assert.deepEqual([...i18n.matchAll(/v2_general_shooting:'([^']*)'/g)].map(m => m[1]),
    ['一般拍攝', 'General shooting', '一般撮影']);
});

test('CL-UI-63 (8): artifact rows join back to the artifact dictionary (zh/en/ja chips)', () => {
  const dict = artifact.dictionaries.genre_short_names;
  const canon = (o) => JSON.stringify([o.en, o.ja, o['zh-TW']]);
  const allowed = new Set(Object.values(dict).map(canon));
  const langs = new Set(['zh-TW', 'en', 'ja']);
  let checked = 0;
  for (const days of Object.values(artifact.places)) {
    for (const row of Object.values(days)) {
      for (const s of row.suitable) {
        assert.ok(allowed.has(canon(s.subject_short)), 'suitable short name is a dictionary entry');
        for (const lang of langs) assert.ok(typeof s.subject_short[lang] === 'string' && s.subject_short[lang]);
        checked++;
      }
    }
  }
  assert.ok(checked > 500, `expected a real suitable corpus, got ${checked}`);
});

test('CL-UI-63 (9): cache-bust stamps advanced to clui75', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui78/);
  assert.match(indexSource, /assets\/app\.css\?v=clui78/);
  assert.ok(!indexSource.includes('clui69'), 'stale stamps fully retired');
});
