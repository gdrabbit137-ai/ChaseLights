// CL-UI-05: selected-date verdict single source of truth on the V1 homepage card.
// The V1 shell (repo-root assets/app.js) is a browser script with no DOM test
// harness, so these are source-assertion tests over the shipped file, per the
// ticket's acceptance plan (source-assertion or extracted-testable-function).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cardBlock=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,start)
);
const createSpotCardBlock=cardBlock('function createSpotCard','function distanceToSpotKm');
const v2BestForSpotBlock=cardBlock('function v2BestForSpot','function v2HoursSortValue');

test('CL-UI-05 (a): card never renders the legacy opportunityVerdict verdict',()=>{
  // The legacy recommendation verdict template must no longer be called from
  // the homepage card path; it stays only for the place-modal score verdict.
  assert.equal(/opportunityVerdict\(/.test(createSpotCardBlock),false,
    'createSpotCard must not call opportunityVerdict (legacy path suppressed)');
  // Exactly two occurrences survive: the function definition (:331) and the
  // single place-modal call (:1032). Any call inside createSpotCard would
  // push this above 2.
  const cardCalls=[...appSource.matchAll(/opportunityVerdict\(/g)].length;
  assert.equal(cardCalls,2,'opportunityVerdict should only remain as definition + place-modal call');
  // Legacy best-window row (fmtWindow(metric) driven by recommendationState)
  // must not be rendered on the card when the summary falls back.
  assert.equal(/recommendationStateValue/.test(createSpotCardBlock),false);
  assert.equal(/fmtWindow\(metric\)/.test(createSpotCardBlock),false,
    'card must not derive a best window from the legacy metric');
});

test('CL-UI-05 (a): no V2 evaluation fails closed to the conservative copy',()=>{
  // Gate: when the V2 bundle has no evaluated day for the place on the
  // selected date (v2Best null), the card shows research_pending_card and no
  // best-window row.
  assert.match(createSpotCardBlock,/const v2Evaluated=!!v2Best;/);
  // CL-UI-41: the fail-closed copy is the named-reason lookup — it maps the
  // bundle's machine-derived skip reason to a specific missing-data line and
  // keeps research_pending_card only as the unknown-reason fallback.
  assert.match(createSpotCardBlock,
    /v2Evaluated\?opportunityDisplayName\(spot,metric\.opportunity_id,theme,metric\.opportunity_name\):v2NoEvalReasonText\(spot\)/);
  // The fallback summary is the conservative pending copy only — no best window.
  assert.match(createSpotCardBlock,
    /\$\{v2Summary\|\|`<div class="theme-winner">📷 \$\{esc\(opportunityName\)\}<\/div>`\}/);
  // The no-evaluation branch of the summary shows no legacy best-window row.
  const v2SummaryBlock=cardBlock('const v2Summary=v2Best&&v2Best.hours?','const reasonHtml=');
  const noneBranch=v2SummaryBlock.slice(v2SummaryBlock.indexOf('(v2Best?'));
  assert.equal(/d\(\)\.best_window/.test(noneBranch),false,'no-evaluation path must not show a best-window row');
  // Forecast status row renders only for non-satisfied V2 evaluations:
  // CL-UI-15 omits it on GUIDANCE_SATISFIED cards (the summary line and the
  // card colour already express the state).
  assert.match(createSpotCardBlock,
    /\$\{v2Best&&v2Best\.state!=='GUIDANCE_SATISFIED'\?`<div class="info-row forecast-status-row card-meta-row">\$\{v2StatusRow\}<\/div>`:''\}/);
});

test('CL-UI-05 (b): evaluated card uses V2-derived day-state labels shared with the modal',()=>{
  // Card label mapping must be a single helper keyed on the same V2 day-state
  // values the modal consumes (GUIDANCE_SATISFIED / UNFAVORABLE / fallback unk).
  assert.match(appSource,/function v2CardStateLabel\(state\)\{\s*return state==='GUIDANCE_SATISFIED'\?d\(\)\.state_ok:state==='UNFAVORABLE'\?d\(\)\.eval2_bad:d\(\)\.eval2_unk;\s*\}/);
  // The card consumes the helper, not an inline copy.
  assert.match(v2BestForSpotBlock,/best\.stateLabel=v2CardStateLabel\(best\.state\);/);
  assert.equal(/best\.state==='NOT_EVALUABLE'\?d\(\)\.eval2_unk/.test(v2BestForSpotBlock),false,
    'card state label must come from v2CardStateLabel, not an inline map');
  // Modal current-day row maps the same day states (consistency contract).
  assert.match(appSource,
    /v2day\.state==='GUIDANCE_SATISFIED'\?d\(\)\.state_ok:v2day\.state==='UNFAVORABLE'\?d\(\)\.state_bad:d\(\)\.eval2_unk/);
});

test('CL-UI-05 (c): eval2_none (not generated) and eval2_unk (NOT_EVALUABLE) stay distinct',()=>{
  // Modal fail-closed path keeps the data-not-generated branch.
  assert.match(appSource,
    /if\(!opp\|\|\!\(opp\.days\|\|\[\]\)\.length\)\{el\.innerHTML=`<div class="v2-eval-block"><div class="v2-note">\$\{esc\(d\(\)\.eval2_none\)\}<\/div><\/div>`;return;\}/);
  // NOT_EVALUABLE keeps its own day label.
  assert.match(appSource,
    /day\.state==='GUIDANCE_SATISFIED'\?'v2-ok':day\.state==='NOT_EVALUABLE'\?'v2-unk':'v2-bad'/);
  assert.match(appSource,
    /day\.state==='GUIDANCE_SATISFIED'\?d\(\)\.eval2_ok:day\.state==='NOT_EVALUABLE'\?d\(\)\.eval2_unk:d\(\)\.eval2_bad/);
  // Card honours the same split: NOT_EVALUABLE shows eval2_unk, an evaluated
  // day without qualifying hours shows the day-aware v2_none copy (v2NoneSubjectKey).
  const summary=cardBlock('const v2Summary=v2Best&&v2Best.hours?','const reasonHtml=');
  assert.match(summary,/v2Best\.state==='NOT_EVALUABLE'\?d\(\)\.eval2_unk:d\(\)\[v2NoneSubjectKey\(\)\]/);
  // i18n: the not-generated copy is date-scoped and distinct from the
  // NOT_EVALUABLE label in every supported locale.
  const i18n=cardBlock("const i18nDict = {","const categoryKeys = {");
  const vals=[...i18n.matchAll(/eval2_none:'([^']*)'/g)].map(m=>m[1]);
  assert.deepEqual(vals,[
    '此日期的評估尚未生成',
    'Evaluation for this date has not been generated yet',
    'この日付の評価はまだ生成されていません'
  ]);
});

test('CL-UI-05 (d): next qualifying window shows when live.next_good exists',()=>{
  // v2BestForSpot wires nextLocal through the CL-UI-13 validation (the raw
  // bundle value is shown only when still in the spot-local future).
  assert.match(v2BestForSpotBlock,
    /best\.nextLocal=v2NextWindowLocal\(best\.oppDays,v2LocalNow\(tz\),ng\?ng\.local:''\);/);
  // The card's no-qualifying-hours summary renders the wired next window and
  // falls back to pure copy when there is none.
  const summary=cardBlock('const v2Summary=v2Best&&v2Best.hours?','const reasonHtml=');
  assert.match(summary,
    /v2Best\.nextLocal\?` · \$\{esc\(d\(\)\.v2_next_window\)\}<b>\$\{esc\(nextWindowStamp\(v2Best\.nextLocal,spot\.timezone\)\)\}<\/b>`:''/);
  // CL-UI-22: the place-guide modal's v2-next row went through the same
  // v2NextWindowLocal re-anchor as the weather modal, with the shared
  // v2_next_window label and fail-closed rendering.
  assert.match(appSource,
    /const nextLocal=v2NextWindowLocal\(opp\.days\|\|\[\],v2LocalNow\(spot\.timezone\),live\.next_good\?live\.next_good\.local:''\);/);
  assert.match(appSource,
    /const nextLine=nextLocal\?`<div class="v2-next">🎯 \$\{esc\(d\(\)\.v2_next_window\)\}\$\{esc\(nextWindowStamp\(nextLocal,spot\.timezone\)\)\}<\/div>`:'';/);
});
