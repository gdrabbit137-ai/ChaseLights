// CL-UI-65: dominant-reason gap fix + general-v0.1 baseline full catalog +
// three-tier display semantics (owner ruling).
//  (1) derived artifact rows carry tier + general_baseline (and the tw-005
//      regression: a failed day never renders a bare ✗ 未符 without a reason)
//  (2) card second line is three-tier: ✓推薦 chips / ○可拍 / ✗不宜 · short reason
//  (3) the modal quick view shares the semantics (modalDayRow carries the row)
//  (4) chips never include the general subject (separate field only)
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

const helperCode = grab('const V2_SUBJECT_CARDS_FILE', '// CL-UI-26: every 不符 verdict');
const tierDict = {
  'v2_general_shooting': '一般拍攝',
  'v2_tier_shootable': '○ 可拍',
  'v2_tier_not_recommended': '✗ 不宜',
};
const makeHelpers = (tree) => new Function(
  `const i18nStub=${JSON.stringify(tierDict)};\nconst d=()=>i18nStub;\n` +
  `${helperCode}\nv2SubjectCards=${JSON.stringify(tree)};\n` +
  'return {v2SubjectCardRow,v2GeneralBaseline,v2GeneralLineText,v2SubjectCardShorts,v2SubjectCardShortReason};')();

test('CL-UI-65 (1): every derived row carries tier + general_baseline (460 places)', () => {
  const counts = {recommend: 0, shootable: 0, not_recommended: 0, null_tier: 0};
  let rows = 0;
  for (const days of Object.values(artifact.places)) {
    for (const row of Object.values(days)) {
      rows++;
      const gb = row.general_baseline;
      assert.ok(gb && typeof gb.ok === 'boolean', 'general_baseline present');
      if (gb.ok) assert.equal(gb.reason_short, null);
      if (row.suitable.length) assert.equal(row.tier, 'recommend');
      else if (gb.ok) assert.equal(row.tier, 'shootable');
      counts[row.tier ?? 'null_tier']++;
    }
  }
  assert.ok(rows > 3000, `real corpus: ${rows}`);
  assert.ok(counts.recommend > 0 && counts.shootable > 0 && counts.not_recommended > 0,
    `all three tiers occur: ${JSON.stringify(counts)}`);
  // tw-005 (大稻埕碼頭) regression: its formerly bare failed days carry a reason
  const tw = artifact.places['tw-005'];
  const bare = Object.values(tw).filter(r => r.status === 'failed' && !r.dominant_reason);
  assert.equal(bare.length, 0, 'tw-005 failed days all carry a short reason');
});

test('CL-UI-65 (2): three-tier second line renders per tier', () => {
  const h = makeHelpers(artifact);
  // shootable tier line: ○可拍 · 一般拍攝
  const shootable = grab('const scSecondLine=', 'const opportunityName=');
  assert.ok(shootable.includes('v2-verdict-mid'), 'shootable tier uses the mid verdict style');
  assert.ok(shootable.includes('v2_tier_shootable') && shootable.includes('v2_general_shooting'));
  // not_recommended line: ✗不宜 · short reason (general reason backs up curated)
  assert.ok(shootable.includes('v2_tier_not_recommended') && shootable.includes('scTierReason'));
  // recommend line keeps chips + window, labeled ✓推薦 when the row is recommend
  assert.match(createSpotCardBlock,
    /scTier==='recommend'\?d\(\)\.v2_tier_recommend:d\(\)\.card_line_ok/);
  // helper semantics
  const row = {general_baseline: {ok: false, reason_short: {'zh-TW': '雨', en: 'rain', ja: '雨'}}};
  assert.equal(h.v2GeneralLineText(row, 'zh-TW'), '一般拍攝 · ✗ 不宜 · 雨');
  assert.equal(h.v2GeneralLineText(row, 'en'), '一般拍攝 · ✗ 不宜 · rain');
  assert.equal(h.v2GeneralLineText({general_baseline: {ok: true, reason_short: null}}, 'zh-TW'),
    '一般拍攝 · ○ 可拍');
  assert.equal(h.v2GeneralLineText(null, 'zh-TW'), '');
  assert.equal(h.v2GeneralLineText({}, 'zh-TW'), '');
});

test('CL-UI-65 (3): the modal quick view shares the three-tier semantics', () => {
  const modalRow = grab('function modalDayRow', '// CL-UI-29');
  assert.match(modalRow, /function modalDayRow\(label,info,scRow\)/);
  assert.ok(modalRow.includes('v2GeneralLineText(scRow,currentLang)'),
    'none-branch appends the general tier line');
  // the overview rows feed the subject-card row for that place+date
  assert.match(appSource,
    /modalDayRow\(dayLabels\[i\],info,v2SubjectCardRow\(summaryData\.place\.place_id,info&&info\.date\)\)/);
});

test('CL-UI-65 (4): chips never include the general subject', () => {
  // suitable carries curated genres only; the general line renders from
  // general_baseline, a separate field
  for (const days of Object.values(artifact.places)) {
    for (const row of Object.values(days)) {
      for (const s of row.suitable) {
        assert.ok(!['一般拍攝', '一般'].includes(s.subject_short['zh-TW']),
          `general subject leaked into chips: ${s.subject_short['zh-TW']}`);
      }
    }
  }
  // the chip list is built from suitable only — never from general_baseline
  const shortsFn = grab('function v2SubjectCardShorts', '// CL-UI-65');
  assert.ok(!shortsFn.includes('general_baseline'));
});

test('CL-UI-65 (5): mid-verdict style exists and stamps advanced to clui73', () => {
  const css = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');
  assert.match(css, /\.v2-verdict-mid\s*{\s*color:/);
  assert.match(indexSource, /assets\/app\.js\?v=clui73/);
  assert.match(indexSource, /assets\/app\.css\?v=clui73/);
});
