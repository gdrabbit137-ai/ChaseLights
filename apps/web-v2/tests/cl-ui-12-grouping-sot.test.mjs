// CL-UI-12: the homepage main-grid / deferred-group split must use the SAME
// source as the card verdict — the V2 evaluation day-state — not the legacy
// metric.no_viable_opportunity flag. Also: unified no-V2 card copy and day0
// qualifying-hours counted from the remaining part of the day only.
// The V1 shell (repo-root assets/app.js) is a browser script with no DOM test
// harness, so this suite combines source assertions with extracted-function
// tests (the pure day0 helpers are extracted from the shipped source and
// executed for real).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const block=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,appSource.indexOf(start))
);
const filterAndRenderBlock=block('function filterAndRender','function opportunityScoreClass');
const createSpotCardBlock=block('function createSpotCard','function distanceToSpotKm');
const v2VerdictBlock=block('function localNowMinutes','function v2HoursSortValue');
const i18nBlock=block("const i18nDict = {","const categoryKeys = {");

test('CL-UI-12 (a): grouping key shares the card verdict source (V2 day-state)',()=>{
  // The legacy flag must not be the grouping key anymore (comment prose that
  // documents the rule is fine; no code reference in the grouping block).
  assert.equal(/rows\.filter\(\(\{metric\}\)=>!?metric\.no_viable_opportunity\)/.test(filterAndRenderBlock),false,
    'filterAndRender must not group by the legacy no_viable_opportunity flag');
  assert.match(filterAndRenderBlock,/v2SpotDayVerdict\(row\.spot\)/);
  // Same verdict helpers the card consumes: v2PlaceForSpot + v2BestForSpot.
  assert.match(v2VerdictBlock,/function v2SpotDayVerdict\(spot\)\{\s*const place=v2PlaceForSpot\(spot\);\s*if\(!place\)return 'noeval';\s*const best=v2BestForSpot\(place,spot\.timezone\);\s*if\(!best\)return 'noeval';\s*return best\.hours>0\?'viable':'deferred';\s*\}/);
  assert.match(v2VerdictBlock,/function v2PlaceForSpot\(spot\)\{\s*return \(v2EvalBundle&&\(v2EvalBundle\.places\|\|\[\]\)\.find\(p=>p\.place_id===spot\.spot_id\)\)\|\|null;\s*\}/);
  // Three explicit buckets; the deferred group keeps its own sorting via
  // appendSpotRows and never receives a viable card.
  assert.match(filterAndRenderBlock,/const viableRows=\[\],deferredRows=\[\],noEvalRows=\[\];/);
  assert.match(filterAndRenderBlock,/verdict==='viable'\?viableRows:verdict==='deferred'\?deferredRows:noEvalRows/);
  assert.match(filterAndRenderBlock,/appendSpotRows\(container,viableRows\);/);
  assert.match(filterAndRenderBlock,/d\(\)\.no_viable_group\.replace\('\{n\}',deferredRows\.length\)/);
  // The supplementary legacy signal lives only inside the card's code (the
  // single `const noViable=...` read; comment prose elsewhere documents the
  // rule but never executes it).
  assert.match(createSpotCardBlock,/const noViable=!!metric\.no_viable_opportunity;/);
  assert.equal([...appSource.matchAll(/!!metric\.no_viable_opportunity/g)].length,1,
    'the legacy flag must be read exactly once, inside createSpotCard');
});

test('CL-UI-12 (b): one data state, one card copy (research_pending_card)',()=>{
  // The dual copy is gone: no_viable_card is no longer defined or selected.
  assert.equal(/no_viable_card:'/.test(appSource),false,'no_viable_card key must be removed');
  assert.equal(/noViable\?d\(\)\.no_viable_card/.test(appSource),false,'no_viable_card branch must be removed');
  assert.match(createSpotCardBlock,
    /const opportunityName=v2Evaluated\?opportunityDisplayName\(spot,metric\.opportunity_id,theme,metric\.opportunity_name\):d\(\)\.research_pending_card;/);
  // The unified fallback copy is present in all three locales.
  const pending=[...i18nBlock.matchAll(/research_pending_card:'([^']*)'/g)].map(m=>m[1]);
  assert.equal(pending.length,3);
  // The new group labels are locale-paritous ({n} in each).
  const groupKeys=[...i18nBlock.matchAll(/no_eval_group:'([^']*)'/g)].map(m=>m[1]);
  assert.equal(groupKeys.length,3);
  groupKeys.forEach(v=>assert.ok(v.includes('{n}')));
  const pastKeys=[...i18nBlock.matchAll(/eval2_past_hours:'([^']*)'/g)].map(m=>m[1]);
  assert.equal(pastKeys.length,3);
});

test('CL-UI-12 (c): day0 qualifying hours count only the remaining part of the day',()=>{
  // Extract and execute the shipped pure helpers.
  const extract=(start,end,fn)=>{
    const src=appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));
    return new Function(`${src}\nreturn ${fn};`)();
  };
  const v2RemainingHoursList=extract('function v2RemainingHoursList','function v2EffectiveHours','v2RemainingHoursList');
  const localNowMinutes=extract('function localNowMinutes','function v2IsToday','localNowMinutes');
  // now 17:30 → 16:00 and 17:00 are past, 18:00 remains.
  assert.deepEqual(v2RemainingHoursList(['16:00','17:00','18:00'],17*60+30),['18:00']);
  // Near midnight: 23:50 → nothing after except the next day's hours, which
  // belong to another date entry.
  assert.deepEqual(v2RemainingHoursList(['23:00','00:00'],23*60+50),[]);
  // Just after midnight: the 00:00 block already started.
  assert.deepEqual(v2RemainingHoursList(['00:00','01:00','02:00'],5),['01:00','02:00']);
  // Unresolvable local now fails closed (never recommend past hours).
  assert.deepEqual(v2RemainingHoursList(['09:00','23:00'],null),[]);
  assert.deepEqual(v2RemainingHoursList(['09:00'],undefined),[]);
  // Malformed entries are dropped.
  assert.deepEqual(v2RemainingHoursList(['17:00','junk',null,'24:00'],0),['17:00']);
  // Boundary semantics: the current hour block still counts (>= now).
  assert.deepEqual(v2RemainingHoursList(['17:00'],17*60),['17:00']);
  // Cross-timezone sanity: localNowMinutes resolves per-zone integers and
  // fails closed on an unknown zone.
  const tw=localNowMinutes('Asia/Taipei');
  assert.ok(Number.isInteger(tw)&&tw>=0&&tw<=1439);
  const utc=localNowMinutes('UTC');
  assert.ok(Number.isInteger(utc)&&utc>=0&&utc<=1439);
  assert.equal(localNowMinutes('Not/AZone'),null);
  assert.equal(localNowMinutes(null),localNowMinutes('UTC'));
  // Wire-up: today is detected by the spot-local date, the effective list
  // filters remaining hours only when the day IS today, and the card +
  // grouping verdict consume it through v2BestForSpot.
  assert.match(v2VerdictBlock,/function v2IsToday\(day,tz\)\{\s*return !!\(day&&day\.local_date===localDateString\(tz\|\|'UTC',0\)\);\s*\}/);
  assert.match(v2VerdictBlock,/if\(!v2IsToday\(day,tz\)\)return \(day\.good_hours\|\|\[\]\)\.filter\(t=>\/\^\(\[01\]\\d\|2\[0-3\]\):\[0-5\]\\d\$\/\.test\(String\(t\|\|''\)\)\);\s*return v2RemainingHoursList\(day\.good_hours\|\|\[\],localNowMinutes\(tz\)\);/);
  assert.match(v2VerdictBlock,/const hoursList=v2EffectiveHours\(day,tz\);\s*const hours=hoursList\.length;/);
  // The modal day row also counts remaining hours for today and annotates
  // excluded past hours; the full-day detail is preserved.
  const v2DayHtmlBlock=block('function v2DayHtml','let v2Details={}');
  assert.match(v2DayHtmlBlock,/const hoursList=v2IsToday\(day,tz\)\?v2RemainingHoursList\(allHours,localNowMinutes\(tz\)\):allHours;/);
  assert.match(v2DayHtmlBlock,/v2-past-note/);
  assert.match(appSource,/v2DayHtml\(day,labels\[i\]\|\|day\.local_date,spot\.timezone\)/);
  // The modal's "current-conditions" reference hour never resolves to a
  // today-hour that already passed.
  const v2PickRefHourBlock=block('function v2PickRefHour','function v2FmtNum');
  assert.match(v2PickRefHourBlock,/v2PickRefHour\(opp,tz\)/);
  assert.match(v2PickRefHourBlock,/v2IsToday\(day,tz\)\?all\.filter\(h=>v2RemainingHoursList\(\[h\.local\],localNowMinutes\(tz\)\)\.length===1\):all/);
  assert.match(appSource,/v2PickRefHour\(dop,spot\.timezone\)/);
  // A today card whose remaining hours hit 0 lands in the deferred group,
  // which surfaces the next qualifying window (v2Best.nextLocal path).
  assert.match(v2VerdictBlock,/return best\.hours>0\?'viable':'deferred';/);
  assert.match(v2VerdictBlock,/best\.nextLocal=ng\?ng\.local:'';/);
  // The css knows the past-hours note.
  assert.match(cssSource,/\.v2-past-note\{/);
});

test('CL-UI-12 (d): spots without V2 evaluation get one explicit, consistent group',()=>{
  // Missing place / no bundle → 'noeval', grouped separately from both the
  // main grid and the V2-unmet deferred group, with its own label.
  assert.match(filterAndRenderBlock,/d\(\)\.no_eval_group\.replace\('\{n\}',noEvalRows\.length\)/);
  assert.match(filterAndRenderBlock,/deferred-group no-eval-group/);
  // Same data state, same treatment: a noeval spot's card fails closed to the
  // unified research_pending copy (v2Best null ⇒ v2Evaluated false).
  assert.match(createSpotCardBlock,/const v2PlaceData=v2PlaceForSpot\(spot\);\s*const v2Best=v2PlaceData\?v2BestForSpot\(v2PlaceData,spot\.timezone\):null;/);
});
