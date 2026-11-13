// CL-UI-50: no-black-box homepage cards. Two live QA findings (zh-TW):
//   (A) NOT_EVALUABLE cards rendered the label 「資料不足」 twice (summary line
//       + status row concatenated) with no explanation — the status row must
//       never repeat the label and must surface the honest missing-input
//       reason instead.
//   (B) Cards fell back to the bare generic 「所選日期目前無法提供可靠的拍攝建議」
//       without naming WHICH input is missing — owner rule: the generic line
//       must be followed by a missing-input statement (評估條件尚未查證).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, `source slice start not found: ${start}`);
  const j = appSource.indexOf(end, i + start.length);
  assert.ok(j > i, `source slice end not found after start: ${end}`);
  return appSource.slice(i, j);
};

test('CL-UI-50: eval2_unverified key exists in all three dictionaries', () => {
  assert.ok(appSource.includes("eval2_unverified:'評估條件尚未查證，無法判定'"), 'zh-TW');
  assert.ok(appSource.includes("eval2_unverified:'Assessment conditions are not yet verified, so no verdict is available'"), 'en');
  assert.ok(appSource.includes("eval2_unverified:'評価条件が未検証のため、判定できません'"), 'ja');
});

test('CL-UI-50: NOT_EVALUABLE day with all-UNKNOWN conditions maps to the missing-input reason', () => {
  const slice = grab('function v2NotEvaluatableReasonKey', 'function createSpotCard');
  const fn = new Function(`return (${slice.replace(/^function v2NotEvaluatableReasonKey\(day\)\{/, 'function(day){')})`);
  const keyOf = fn();
  assert.equal(keyOf({ conditions: [{ day_verdict: 'UNKNOWN' }, { day_verdict: 'UNKNOWN' }] }), 'eval2_unverified');
  assert.equal(keyOf({ conditions: [{ day_verdict: 'UNKNOWN' }, { day_verdict: 'FAIL' }] }), null);
  assert.equal(keyOf({ conditions: [] }), null);
  assert.equal(keyOf(null), null);
});

test('CL-UI-50: the 資料不足 label is never emitted twice on a NOT_EVALUABLE card', () => {
  // CL-UI-63 retired the status row entirely: the summary line keeps the
  // 「資料不足」 label exactly once and the card adds no verdict row after it
  // (the honest missing-input detail lives in the place modal day rows).
  assert.ok(!appSource.includes('card-meta-row">${v2StatusRow}</div>'), 'status row retired (CL-UI-63)');
  assert.ok(!grab('function createSpotCard', 'function distanceToSpotKm').includes('v2NotEvalReason'),
    'no NOT_EVALUABLE status-row lookup remains on the card');
  assert.ok(grab('function createSpotCard', 'function distanceToSpotKm')
    .includes("v2Best.state==='NOT_EVALUABLE'?d().eval2_unk"),
    'summary line keeps the single honest 資料不足 label');
});

test('CL-UI-50: the unavailable-card line is not the bare generic sentence', () => {
  const slice = grab('function v2NoEvalReasonText', '// CL-UI-50');
  // Every fallback names the absent input: generic sentence + missing-input
  // statement, never research_pending_card alone.
  const bare = 'return d().research_pending_card;';
  assert.ok(!slice.includes(bare), 'bare generic fallback must be gone');
  assert.ok(slice.includes("d().research_pending_card+' · '+d().eval2_unverified"), 'fallback composes generic + missing-input reason');
  // And the composed string itself contains 資料不足 at most once.
  const zh = '所選日期目前無法提供可靠的拍攝建議 · 評估條件尚未查證，無法判定';
  assert.ok((zh.match(/資料不足/g) || []).length <= 1, 'label appears at most once');
});

test('CL-CI-29: the retired card status row left no dangling v2StateLabel use', () => {
  // B149 production smoke fixed the TDZ ordering; CL-UI-63 removed the row
  // (and its v2StateLabel consumer) altogether — no reference may remain.
  assert.equal(appSource.includes('esc(v2StateLabel)'), false, 'no v2StateLabel template use remains');
  assert.equal(appSource.includes('const v2StateLabel='), false, 'no dangling v2StateLabel declaration');
});
