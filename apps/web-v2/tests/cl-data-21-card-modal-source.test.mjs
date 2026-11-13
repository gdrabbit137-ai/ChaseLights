// CL-DATA-21: homepage card / modal single-source enforcement + pinned places.
//
// Evidence (Yehliu 2026-11-06): the V2 evaluation bundle (evaluations-latest.json
// generated BEFORE CL-DATA-19 landed) let tw-074-P02 (野柳蕈狀岩與燭台石群紋理,
// golden_hour_window BONUS, no light window) qualify at 22:00–23:00, so the
// homepage card — which is V2-driven (v2BestForSpot) — showed a night "符合".
// The contract now carries a REQUIRED civil light_window (CL-DATA-19); this
// ticket pins the verdict sources and re-anchors the remaining legacy-JUDGMENT
// fields:
//  - the weather-modal hourly table's 「最佳」 row tag now comes from the same
//    V2 good_hours as the card (legacy summaryMetric window never paints it);
//  - the place-guide modal resolves V2 day rows BY LOCAL DATE (v2DayForOffset),
//    not by bundle index (a stale bundle's day[0] is yesterday);
//  - pinned places: 野柳 (tw-074-P01/P02), 得月樓 (tw-062-P01), 和平島
//    (tw-010-P02 REQUIRED light_window / tw-010-P03 REQUIRED sunset_window)
//    — night hours can never qualify on any of them.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(here,'..','..','..');
const appSource=readFileSync(path.join(repo,'assets','app.js'),'utf8');

test('CL-DATA-21 (a): weather-modal 「最佳」 tag is painted only from V2 good_hours',()=>{
  const block=appSource.slice(appSource.indexOf('let nowAnchorAssigned=false'),appSource.indexOf('(spot.hourly_forecast||[]).forEach'));
  assert.match(block,/v2WmPlace=v2PlaceForSpot\(summarySpot\)/);
  assert.match(block,/v2WmDay=v2WmOpp\?v2DayForOffset\(v2WmOpp,selectedDayOffset\(\),summarySpot\?\.timezone\):null/);
  assert.match(block,/v2WmHours=new Set\(v2EffectiveHours\(v2WmDay,summarySpot\?\.timezone\)\)/);
  // the isBest predicate on the timeline loop reads the same V2 hour set
  assert.match(appSource,/const isBest=!!\(selectedDate&&item\.local_date===selectedDate&&v2WmHours\.size&&v2WmHours\.has\(item\.time\.slice\(-5\)\)\)/);
  // the legacy window must no longer select the tag anywhere in the timeline
  assert.ok(!appSource.includes('summaryMetric?.window_start&&item.time>='),'legacy window_start best-tag must be gone');
});

test('CL-DATA-21 (b): place-guide modal resolves V2 day rows by local date, not index',()=>{
  assert.ok(!appSource.includes('(o.days||[])[selectedDayOffset()]'),'v2Hours ranking must not index day rows');
  assert.ok(!appSource.includes('(v2op.days||[])[selectedDayOffset()]'),'opportunity current-day must not index day rows');
  assert.match(appSource,/const dy=v2DayForOffset\(o,selectedDayOffset\(\),spot\.timezone\);v2Hours\[o\.opportunity_id\]=dy\?/);
  // CL-UI-67: the modal's per-subject current-day verdict line was removed
  // (the 8-day strip expresses it), so the index-based v2day lookup is gone
  // too — the modal must never resolve a day row by index.
  assert.ok(!appSource.includes('(v2op.days||[])[selectedDayOffset()]'),'v2day day-row lookups must stay local-date anchored or be absent');
});

test('CL-DATA-21 (c): pinned places carry a gating light/sunset window',()=>{
  const load=oid=>JSON.parse(readFileSync(path.join(repo,'data','v2','opportunities',`${oid}.json`),'utf8'));
  const windowConds=oid=>{
    const d=load(oid);
    return (d.condition_contract?.conditions||[]).filter(c=>c.metric==='light_window'||c.metric==='sunset_window'||c.metric==='sunrise_time_window');
  };
  for(const oid of ['tw-074-P01','tw-074-P02','tw-062-P01','tw-010-P02']){
    const w=windowConds(oid).find(c=>c.metric==='light_window');
    assert.ok(w,`${oid} carries a civil light_window`);
    assert.equal(w.role,'REQUIRED',`${oid} light_window is REQUIRED`);
    assert.equal(w.condition_tier,'MAIN',`${oid} light_window is MAIN`);
  }
  // 和平島奇岩海岸夕照 gates on its own REQUIRED sunset window (subject semantics)
  const sw=windowConds('tw-010-P03').find(c=>c.metric==='sunset_window');
  assert.ok(sw,'tw-010-P03 carries sunset_window');
  assert.equal(sw.role,'REQUIRED');
  assert.equal(sw.condition_tier,'MAIN');
});

test('CL-DATA-21 (d): cache-bust stamp bumped for the edited app.js',()=>{
  const index=readFileSync(path.join(repo,'index.html'),'utf8');
  assert.match(index,/assets\/app\.js\?v=clui79/);
  assert.match(index,/assets\/app\.css\?v=clui79/);
});
