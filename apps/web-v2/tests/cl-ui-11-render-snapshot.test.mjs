// CL-UI-11: F5 no longer flashes the loading splash — the last gated render is
// persisted in sessionStorage and restored synchronously on boot. The V1 shell
// (repo-root assets/app.js) is a browser script with no DOM test harness, so
// these are source-assertion tests over the shipped file, following the
// CL-UI-10 test conventions.
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
const saveBlock = block('function saveRenderSnapshot', 'function loadRenderSnapshot');
const loadBlock = block('function loadRenderSnapshot', 'const d=()=>i18nDict');
const loadDataBlock = block('async function loadData', 'function selectedDayOffset');
const applyDataBlock = block('function applyData(', 'function migrateFavorites');

test('CL-UI-11 (a): a valid snapshot is restored without the loading splash', () => {
  // The restore branch must paint the snapshot HTML, hide #loading, and never
  // touch the splash copy in that path.
  const restoreBranch = loadDataBlock.slice(loadDataBlock.indexOf('const snapshot='), loadDataBlock.indexOf('else{container.innerHTML=\'\''));
  assert.ok(restoreBranch.length > 0, 'snapshot restore branch not found in loadData');
  assert.match(restoreBranch, /container\.innerHTML=snapshot\.html;/);
  assert.match(restoreBranch, /loading\.style\.display='none';/);
  assert.equal(/innerText=d\(\)\.loading/.test(restoreBranch), false,
    'the restore branch must not show the loading splash copy');
  assert.match(restoreBranch, /showUpdateIndicator\(\);/,
    'a stale-while-revalidate banner accompanies the restored (possibly stale) view');
  // The header states the snapshot's real data time — never presented as live.
  assert.match(restoreBranch, /formatUpdated\(snapshot\.updated_at\)/);
  // Restoring happens only when there is no already-rendered content.
  assert.match(loadDataBlock, /const snapshot=hasRendered\?null:loadRenderSnapshot\(region\);/);
});

test('CL-UI-11 (b): expired, missing, or corrupt snapshots fall back to the loading path', () => {
  // Age check against a bounded threshold (10 minutes, inside one refresh
  // cycle), plus full key/state validation.
  assert.match(appSource, /RENDER_SNAPSHOT_MAX_AGE_MS=10\*60\*1000;/);
  assert.match(loadBlock, /Date\.now\(\)-snap\.saved_at>RENDER_SNAPSHOT_MAX_AGE_MS/);
  assert.match(loadBlock, /snap\.region!==region\|\|snap\.lang!==currentLang\|\|snap\.day!==currentDayFilter/);
  assert.match(loadBlock, /typeof snap\.html!=='string'\|\|!snap\.html/);
  assert.match(loadBlock, /return null;/);
  // Parsing/reading errors must land in try/catch and behave like no snapshot.
  assert.match(loadBlock, /catch\{return null;\}/);
  // The splash path is intact for the no-snapshot case.
  assert.match(loadDataBlock, /loading\.innerText=d\(\)\.loading;loading\.style\.display='block';/);
});

test('CL-UI-11 (c): after restore, data still updates through the single gated render', () => {
  // The snapshot restore path never renders by itself — the fetch continues
  // and applyData keeps CL-UI-10's exactly-once gated render.
  const calls = (applyDataBlock.match(/filterAndRender\(\)/g) || []).length;
  assert.equal(calls, 1, 'applyData must still call filterAndRender exactly once');
  assert.match(applyDataBlock,
    /ensureV2EvalBundle\(\)\.then\(bundle=>\{if\(seq===activeLoadSequence&&region===currentRegion\)\{filterAndRender\(\);/);
  // The snapshot is written only after the settled gated render: inside
  // filterAndRender, after cards (or the empty state) are on screen.
  const filterBlock = block('function filterAndRender', 'function opportunityScoreClass');
  assert.match(filterBlock, /saveRenderSnapshot\(\);/);
  assert.ok(filterBlock.lastIndexOf('saveRenderSnapshot()') > filterBlock.indexOf('appendSpotRows(container'),
    'the snapshot must be saved after the gated render completes');
  // Snapshot content is the already-gated container HTML, not raw data or
  // unevaluated verdicts.
  assert.match(saveBlock, /html:container\.innerHTML/);
  assert.equal(/opportunityVerdict/.test(saveBlock), false,
    'the snapshot must store rendered HTML, not re-run legacy verdicts');
});

test('CL-UI-11 (d): sessionStorage writes and reads are try/catch protected', () => {
  assert.match(saveBlock, /try\{[\s\S]*sessionStorage\.setItem\(/);
  assert.match(saveBlock, /catch\{\}/);
  // Quota guard: skip oversized payloads whole instead of truncating markup.
  assert.match(saveBlock, /json\.length>2000000\)return;/);
  assert.match(loadBlock, /try\{[\s\S]*sessionStorage\.getItem\(/);
});

test('CL-UI-11: snapshot keys are scoped per region/lang/day and carry the data timestamp', () => {
  assert.match(appSource, /chaselights_last_render_/);
  assert.match(saveBlock, /updated_at:currentData\.updated_at\|\|null/);
});
