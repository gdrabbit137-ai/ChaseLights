// CL-UI-10: stale-while-revalidate + single render on the V1 homepage shell.
// The V1 shell (repo-root assets/app.js) is a browser script with no DOM test
// harness, so these are source-assertion tests over the shipped file, per the
// ticket's acceptance plan (source-assertion or extracted-testable-function).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');

const block = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, `anchor not found: ${start}`);
  const j = appSource.indexOf(end, i);
  assert.ok(j > i, `end anchor not found: ${end}`);
  return appSource.slice(i, j);
};
const loadDataBlock = block('async function loadData', 'function selectedDayOffset');
const applyDataBlock = block('function applyData(', 'function migrateFavorites');
const showUpdateBlock = block('function showUpdateIndicator', 'function hideUpdateIndicator');

test('CL-UI-10 (a): reload/region-switch with existing content does not wipe the container', () => {
  // The container must only be cleared inside the no-existing-content branch.
  assert.match(loadDataBlock, /const hasRendered=container\.children\.length>0&&currentData!==null;/);
  const branch = loadDataBlock.slice(loadDataBlock.indexOf('if(hasRendered)'), loadDataBlock.indexOf('const url='));
  assert.ok(branch.length > 0, 'hasRendered branch not found in loadData');
  // The wipe + loading splash only happens when there is no existing content.
  assert.match(branch, /if\(hasRendered\)\{showUpdateIndicator\(\);loading\.style\.display='none';\}/);
  assert.match(branch, /else\{container\.innerHTML='';currentSpots=\[\];currentData=null;renderSubNav\(\);loading\.innerText=d\(\)\.loading;loading\.style\.display='block';updateHeader\(\);\}/);
  // No unconditional wipe remains anywhere in loadData.
  const wipeCount = (loadDataBlock.match(/container\.innerHTML=''/g) || []).length;
  assert.equal(wipeCount, 1, 'container.innerHTML=\'\' must appear exactly once (the no-content branch only)');
});

test('CL-UI-10 (a): no existing content keeps the loading splash', () => {
  assert.match(loadDataBlock, /loading\.innerText=d\(\)\.loading;loading\.style\.display='block';/);
});

test('CL-UI-10 (b): applyData renders exactly once, after the V2 bundle settles', () => {
  // The only filterAndRender call in applyData lives inside the
  // ensureV2EvalBundle().then(...) — no synchronous first paint plus a second
  // repaint when the bundle arrives.
  const calls = (applyDataBlock.match(/filterAndRender\(\)/g) || []).length;
  assert.equal(calls, 1, 'applyData must call filterAndRender exactly once');
  assert.match(applyDataBlock,
    /ensureV2EvalBundle\(\)\.then\(\(\)=>\{if\(seq===activeLoadSequence&&region===currentRegion\)filterAndRender\(\);\}\);return true;\}/);
  assert.equal(/filterAndRender\(\);return true;\}/.test(applyDataBlock), false,
    'the synchronous double render must be gone');
});

test('CL-UI-10 (b): gate semantics unchanged — fail-closed conservative copy without the bundle', () => {
  // The card gate (CL-UI-05) must be intact: no V2 evaluation → research
  // pending copy, no legacy verdict, no best window.
  const createSpotCardBlock = block('function createSpotCard', 'function distanceToSpotKm');
  assert.match(createSpotCardBlock, /const v2Evaluated=!!v2Best;/);
  assert.match(createSpotCardBlock,
    /v2Evaluated\?opportunityDisplayName\(spot,metric\.opportunity_id,theme,metric\.opportunity_name\):v2NoEvalReasonText\(spot\)/);
  // applyData must not render before the bundle promise settles.
  assert.ok(applyDataBlock.indexOf('filterAndRender') > applyDataBlock.indexOf('ensureV2EvalBundle'),
    'render is scheduled only via the bundle promise');
  // The bundle promise resolves null on failure (fail-closed stays reachable).
  const ensureBundleBlock = block('function ensureV2EvalBundle', 'function v2MetricName');
  assert.match(ensureBundleBlock, /catch\(\(\)=>\{v2EvalBundlePromise=null;return null;\}\)/);
});

test('CL-UI-10 (b): fetch timeout guarantees the bundle promise always settles', () => {
  // Regression: an unresolved fetch left the promise pending forever, so the
  // single gated render never ran and first load stayed blank. The fetch must
  // carry an abort timeout (10–15s chosen to tolerate slow mobile networks)
  // so a hang rejects → .catch resets the promise → resolves null → the same
  // single filterAndRender runs once and the card shows research_pending copy.
  const ensureBundleBlock = block('function ensureV2EvalBundle', 'function v2MetricName');
  assert.match(ensureBundleBlock, /signal:AbortSignal\.timeout\(\d+\)/,
    'the bundle fetch must carry an AbortSignal.timeout');
  const ms = Number(ensureBundleBlock.match(/AbortSignal\.timeout\((\d+)\)/)[1]);
  assert.ok(ms >= 10000 && ms <= 15000, `timeout must be 10-15s, got ${ms}ms`);
  // Timeout rejection reaches the existing catch: nothing added between the
  // fetch chain and the null-reset catch, so fail-closed stays the only path.
  const chain = ensureBundleBlock.slice(ensureBundleBlock.indexOf('fetch('));
  const catchIdx = chain.indexOf('.catch(()=>{v2EvalBundlePromise=null;return null;})');
  assert.ok(catchIdx >= 0, 'the null-reset catch must still terminate the fetch chain');
  assert.equal(chain.indexOf('.then(', catchIdx), -1,
    'no handler may be chained after the null-reset catch');
  // No second render path: applyData still renders exactly once, via the gate.
  const calls = (applyDataBlock.match(/filterAndRender\(\)/g) || []).length;
  assert.equal(calls, 1);
});

test('CL-UI-10 (c): the update indicator uses the shared i18n "updating" copy, no internal labels', () => {
  assert.match(showUpdateBlock, /updateBanner\.textContent=d\(\)\.updating;/);
  const bannerText = showUpdateBlock.slice(showUpdateBlock.indexOf('cssText'));
  assert.equal(/provisional|pending|internal|待證據|研究中/i.test(bannerText), false);
  // zh-TW / en / ja dictionaries all carry the updating string.
  assert.equal((appSource.match(/updating:'/g) || []).length, 3,
    'updating must exist once per language (zh-TW, en, ja)');
});

test('CL-UI-10 (c): the banner is hidden on success and on refresh failure', () => {
  assert.match(applyDataBlock, /hideUpdateIndicator\(\);/);
  const refreshBlock = block('async function refreshSummary', 'let updateBanner=null;');
  assert.match(refreshBlock, /return;hideUpdateIndicator\(\);/);
});
