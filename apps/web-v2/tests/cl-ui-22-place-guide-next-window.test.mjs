// CL-UI-22: the place-guide modal (place-modal-overlay, v2PlaceForSpot) renders
// the same "next qualifying window" row as the weather modal, but Round 4
// review found it displayed a past time: it printed the raw bundle
// live.next_good.local (e.g. "11/04 17:00" while the spot-local now is
// 11/05) while the weather modal correctly re-anchored to
// "Next qualifying window: 11/05 17:00". The fix routes the place-guide
// modal's v2-next row through the same v2NextWindowLocal(v2LocalNow(tz))
// re-anchor as the weather modal and uses the shared v2_next_window label.
// The V1 shell (repo-root assets/app.js) has no DOM harness, so this suite
// asserts the wiring in source, mirroring the CL-UI-13 approach.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const grab=(start,end)=>{
  const a=appSource.indexOf(start);
  const b=appSource.indexOf(end,a+1);
  assert.ok(a>=0&&b>a,`source block ${start}…${end} not found`);
  return appSource.slice(a,b);
};

test('CL-UI-22 (a): place-guide modal v2-next uses v2NextWindowLocal with the spot timezone',()=>{
  const v2PlaceBlock=grab('function v2PlaceForSpot','async function cleanupOldCaches');
  // The row value comes from the same re-anchor helper as the weather modal,
  // fed with the spot's own timezone (never a hardcoded zone).
  assert.match(v2PlaceBlock,/v2NextWindowLocal\(opp\.days\|\|\[\],v2LocalNow\(spot\.timezone\),live\.next_good\?live\.next_good\.local:''\)/);
  // CL-UI-67 (owner ruling): the standalone v2-next row is gone — the
  // re-anchored window rides on the FIRST qualifying strip cell's hover
  // title instead, still labelled with the shared v2_next_window wording
  // and only when a validated future value exists (fail-closed preserved).
  assert.doesNotMatch(v2PlaceBlock,/v2-next/);
  assert.match(v2PlaceBlock,/const nextNote=nextLocal\?`\$\{d\(\)\.v2_next_window\}\$\{nextWindowStamp\(nextLocal,spot\.timezone\)\}`:''/);
  assert.match(v2PlaceBlock,/v2DayStripHtml\(days,labels,spot\.timezone,spot,opp\.genre_template\|\|'',opp\.opportunity_id,nextNote\)/);
});

test('CL-UI-22 (b): place-guide modal no longer shows the raw bundle next_good stamp',()=>{
  const v2PlaceBlock=grab('function v2PlaceForSpot','async function cleanupOldCaches');
  assert.doesNotMatch(v2PlaceBlock,/shortDateStamp\(live\.next_good\.local\)/);
});

test('CL-UI-22 (c): no other live.next_good rendering path skips the re-anchor',()=>{
  // Every remaining direct read of live.next_good in app.js is the pattern
  // `next_good` → capture the local stamp → v2NextWindowLocal fallback
  // (createSpotCard, v2PlaceForSpot). None render next_good.local without
  // going through v2NextWindowLocal first. CL-UI-72 retired the third read
  // (modalSummaryData) with the banner it fed.
  const reads=[...appSource.matchAll(/(opp\.live&&opp\.live\.next_good)|(best\.live&&best\.live\.next_good)|(live\.next_good\?live\.next_good\.local)/g)].map(m=>m.index);
  assert.equal(reads.length,2,'unexpected number of live.next_good reads');
  for(const idx of reads){
    const windowText=appSource.slice(idx-200,idx+800);
    assert.match(windowText,/v2NextWindowLocal/,`next_good read at ${idx} must feed v2NextWindowLocal`);
  }
});

test('CL-UI-22 (d): cache-bust stamp bumped for the edited app.js',()=>{
  const index=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
  assert.match(index,/assets\/app\.js\?v=clui76/);
  assert.match(index,/assets\/app\.css\?v=clui76/);
});
