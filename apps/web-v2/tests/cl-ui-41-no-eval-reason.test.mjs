// CL-UI-41: the 「尚無本日評估」 card group names WHAT is missing instead of
// the generic 「所選日期目前無法提供可靠的拍攝建議」 line. The card copy is a
// mechanical mapping from the evaluation bundle's machine-derived skip
// reasons (evaluate_batch.py skipped[].reason -> i18n key); unknown reasons
// keep the conservative generic copy. Data-missing wording stays on the
// 「無法評估」 route and never mixes with a conditions-not-met verdict.
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

const REASONS = ['NO_OPPORTUNITY_CONTRACT', 'NO_VERIFIED_GEOMETRY', 'NO_GENRE_TEMPLATE'];

test('CL-UI-41: skip-reason -> i18n key mapping is mechanical and total', () => {
  const slice = grab('function v2NoEvalReasonKey', 'function v2NoEvalReasonText');
  assert.ok(slice.includes("reason==='NO_OPPORTUNITY_CONTRACT'"));
  assert.ok(slice.includes("reason==='NO_VERIFIED_GEOMETRY'"));
  assert.ok(slice.includes("reason==='NO_GENRE_TEMPLATE'"));
  assert.ok(slice.includes("return null;"), 'unmapped reason must fall back');
});

test('CL-UI-41: lookup reads bundle skipped[] by place_id, generic fallback when unknown', () => {
  const slice = grab('function v2NoEvalReasonText', 'function createSpotCard');
  assert.match(slice, /v2EvalBundle&&v2EvalBundle\.skipped/);
  assert.match(slice, /s\.place_id===spot\.spot_id/);
  assert.match(slice, /d\(\)\.research_pending_card/, 'unknown reason keeps generic copy');
});

test('CL-UI-41: no-eval card uses the named-reason lookup, not the bare generic copy', () => {
  assert.ok(appSource.includes('v2Evaluated?opportunityDisplayName(spot,metric.opportunity_id,theme,metric.opportunity_name):v2NoEvalReasonText(spot)'));
  assert.ok(!appSource.includes('metric.opportunity_name):d().research_pending_card'), 'generic string must no longer be the direct fallback');
});

test('CL-UI-41: named reasons exist in all three dictionaries', () => {
  for (const [k, v] of [
    ['eval2_no_contract', '此景點的攝影題材條件尚未完成查證，無法提供評估'],
    ['eval2_no_geometry', '拍攝座標尚未完成查證，無法評估此題材'],
    ['eval2_no_template', '此題材的成立條件尚未定義，無法提供評估'],
  ]) assert.ok(appSource.includes(`${k}:'${v}'`), k);
  for (const [k, v] of [
    ['eval2_no_contract', 'Subject conditions for this spot are not yet verified, so no evaluation is available'],
    ['eval2_no_geometry', 'Shooting coordinates are not yet verified, so this subject cannot be evaluated'],
    ['eval2_no_template', 'Qualifying conditions for this subject are not yet defined, so no evaluation is available'],
  ]) assert.ok(appSource.includes(`${k}:'${v}'`), k);
  for (const [k, v] of [
    ['eval2_no_contract', 'このスポットの撮影題材の条件はまだ検証されておらず、評価を提供できません'],
    ['eval2_no_geometry', '撮影座標の検証が未了のため、この題材は評価できません'],
    ['eval2_no_template', 'この題材の成立条件がまだ定義されておらず、評価を提供できません'],
  ]) assert.ok(appSource.includes(`${k}:'${v}'`), k);
});

test('CL-UI-41: mapping helper executes with the bundle shape (extracted function)', () => {
  const slice = grab('function v2NoEvalReasonKey', 'function v2NoEvalReasonText');
  const fn = new Function(`return ${slice.replace(/function v2NoEvalReasonKey/, 'function')}`);
  const f = fn();
  assert.equal(f('NO_OPPORTUNITY_CONTRACT'), 'eval2_no_contract');
  assert.equal(f('NO_VERIFIED_GEOMETRY'), 'eval2_no_geometry');
  assert.equal(f('NO_GENRE_TEMPLATE'), 'eval2_no_template');
  assert.equal(f('SOMETHING_ELSE'), null);
  assert.equal(f(undefined), null);
});

test('CL-UI-41: homepage cache-bust stamp bumped to clui41', () => {
  const index = readFileSync(new URL('../../../index.html', import.meta.url), 'utf8');
  assert.match(index, /assets\/app\.js\?v=clui56/);
  assert.match(index, /assets\/app\.css\?v=clui53/);
});

test('CL-UI-41: evaluator emits machine-derived skip reasons for unevaluated places', () => {
  const eb = readFileSync(new URL('../../../packages/core-v2/tools/evaluate_batch.py', import.meta.url), 'utf8');
  for (const r of REASONS) assert.ok(eb.includes(`"${r}"`), `evaluator must emit ${r}`);
  assert.ok(eb.includes('load_opportunity_docs'), 'evaluator must classify non-contracted docs too');
  assert.ok(eb.includes('v1_ids - evaluated_place_ids - skipped_place_ids'), 'legacy-catalog places must reach the skip list');
});
