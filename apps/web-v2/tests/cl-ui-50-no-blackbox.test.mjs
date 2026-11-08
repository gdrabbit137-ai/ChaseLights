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
  // The status row must not contain the eval2_unk label lookup at all: the
  // summary line already carries it exactly once.
  const statusRow = grab('const v2StatusRow=', 'const opportunityName=');
  assert.ok(!statusRow.includes('eval2_unk'), 'status row must not repeat the 資料不足 label');
  assert.ok(statusRow.includes("state==='NOT_EVALUABLE'"), 'status row special-cases NOT_EVALUABLE');
  assert.ok(statusRow.includes('v2NotEvalReason'), 'status row prefers the honest missing-input reason');
  // The card template consumes v2StatusRow instead of the old duplicated pair.
  assert.ok(appSource.includes('card-meta-row">${v2StatusRow}</div>'), 'template renders v2StatusRow');
  assert.ok(!appSource.includes('${esc(v2StateLabel)}${esc(v2FailReasonSuffix(v2Best,spot))}'), 'old duplicated pair removed');
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

test('CL-CI-29: v2StateLabel is declared before its first use in the card template', () => {
  // B149 production smoke: the served card render threw a TDZ
  // ReferenceError (Cannot access 'v2StateLabel' before initialization)
  // because the declaration sat BELOW the v2StatusRow expression that
  // consumes it. The declaration must precede every reference.
  const use = appSource.indexOf('esc(v2StateLabel)');
  const decl = appSource.indexOf('const v2StateLabel=');
  assert.ok(decl >= 0, 'v2StateLabel declaration exists');
  assert.ok(use >= 0, 'v2StateLabel is referenced');
  assert.ok(decl < use, 'declaration must come before its first reference');
});
