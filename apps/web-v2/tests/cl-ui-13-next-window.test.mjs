// CL-UI-13: the card's "下一個符合時段" (next qualifying window) must never
// show a past time. The bundle's live.next_good is relative to the bundle
// generation time — at night, after the spot-local day's remaining qualifying
// hours are gone, it can point into the past (e.g. "2026-11-01 17:00" shown at
// 23:02). The V1 shell (repo-root assets/app.js) has no DOM harness, so this
// suite combines extracted-function tests with source assertions, mirroring
// the CL-UI-12 approach.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const block=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,appSource.indexOf(start))
);

// Extract the shipped pure helpers and run them for real.
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));
const factory=new Function([
  grab('function localDateString','function selectedDateForSpot'),
  grab('function localNowMinutes','function v2IsToday'),
  grab('function v2RemainingHoursList','function v2EffectiveHours'),
  grab('function v2ParseLocalStamp','function v2LocalNow'),
  grab('function v2LocalNow','function v2NextWindowLocal'),
  grab('function v2NextWindowLocal','function v2BestForSpot'),
  'return {localDateString,localNowMinutes,v2RemainingHoursList,v2ParseLocalStamp,v2LocalNow,v2NextWindowLocal};'
].join('\n'));
const {localDateString,localNowMinutes,v2RemainingHoursList,v2ParseLocalStamp,v2LocalNow,v2NextWindowLocal}=factory();

const day=(date,hours)=>({local_date:date,good_hours:hours});
const now=d=>({date:d[0],minutes:d[1]});

test('CL-UI-13 (a): a still-future bundle value passes through unchanged',()=>{
  const rows=[day('2026-11-01',['17:00']),day('2026-11-02',['16:00'])];
  // now 15:00 on 11-01 → 17:00 today is still ahead.
  assert.equal(v2NextWindowLocal(rows,now(['2026-11-01',15*60]),'2026-11-01 17:00'),'2026-11-01 17:00');
  // A next window on a later date passes through too.
  assert.equal(v2NextWindowLocal(rows,now(['2026-11-01',18*60]),'2026-11-02 16:00'),'2026-11-02 16:00');
});

test('CL-UI-13 (b): a past bundle value is filtered and replaced by the first still-future day-row hour',()=>{
  const rows=[day('2026-11-01',['17:00']),day('2026-11-02',['16:00']),day('2026-11-03',['05:00'])];
  // The reported symptom: at 23:02 the bundle still advertises 17:00 today.
  assert.equal(v2NextWindowLocal(rows,now(['2026-11-01',23*60+2]),'2026-11-01 17:00'),'2026-11-02 16:00');
  // Remaining hours of TODAY count first (only the part still ahead).
  const rows2=[day('2026-11-01',['17:00','20:00']),day('2026-11-02',['00:00'])];
  assert.equal(v2NextWindowLocal(rows2,now(['2026-11-01',19*60]),'2026-11-01 17:00'),'2026-11-01 20:00');
  // Past day rows are never candidates.
  const rows3=[day('2026-10-31',['09:00']),day('2026-11-02',['16:00'])];
  assert.equal(v2NextWindowLocal(rows3,now(['2026-11-01',10*60]),'2026-10-31 09:00'),'2026-11-02 16:00');
});

test('CL-UI-13 (c): no future qualifying hour anywhere → the row is omitted (empty string)',()=>{
  const rows=[day('2026-11-01',['17:00']),day('2026-11-02',[]),day('2026-11-03',[])];
  assert.equal(v2NextWindowLocal(rows,now(['2026-11-01',23*60]),'2026-11-01 17:00'),'');
  // Missing fallback and no day rows → omitted as well.
  assert.equal(v2NextWindowLocal([],now(['2026-11-01',10*60]),''),'');
  assert.equal(v2NextWindowLocal(undefined,now(['2026-11-01',10*60]),null),'');
});

test('CL-UI-13 (d): near-midnight and cross-timezone safety',()=>{
  // 23:50 today: the 23:00 block is gone; tomorrow's 00:00 row is the window.
  const rows=[day('2026-11-01',['23:00']),day('2026-11-02',['00:00'])];
  assert.equal(v2NextWindowLocal(rows,now(['2026-11-01',23*60+50]),'2026-11-01 23:00'),'2026-11-02 00:00');
  // Just after midnight (00:05): today's 00:00 block already started, 01:00 remains.
  const rows2=[day('2026-11-02',['00:00','01:00'])];
  assert.equal(v2NextWindowLocal(rows2,now(['2026-11-02',5]),'2026-11-02 00:00'),'2026-11-02 01:00');
  // v2LocalNow resolves per-zone and fails closed on an unknown zone.
  const tw=v2LocalNow('Asia/Taipei');
  assert.ok(tw&&/^\d{4}-\d{2}-\d{2}$/.test(tw.date)&&Number.isInteger(tw.minutes)&&tw.minutes>=0&&tw.minutes<=1439);
  assert.equal(v2LocalNow('Not/AZone'),null);
  assert.equal(JSON.stringify(v2LocalNow(null)),JSON.stringify(v2LocalNow('UTC')));
});

test('CL-UI-13 (e): unresolvable local now fails closed — the row is omitted',()=>{
  const rows=[day('2026-11-01',['17:00']),day('2026-11-02',['16:00'])];
  // Even a future-looking fallback must not be shown when it cannot be
  // verified against the spot-local now.
  assert.equal(v2NextWindowLocal(rows,null,'2026-11-01 17:00'),'');
  assert.equal(v2NextWindowLocal(rows,undefined,'2026-11-02 16:00'),'');
});

test('CL-UI-13 (f): malformed bundle values and malformed day rows are never displayed',()=>{
  const rows=[day('2026-11-02',['junk','24:00',null,'16:00'])];
  // Unparseable fallback → scan the day rows instead.
  assert.equal(v2NextWindowLocal(rows,now(['2026-11-01',18*60]),'not-a-stamp'),'2026-11-02 16:00');
  assert.equal(JSON.stringify(v2ParseLocalStamp('2026-11-01 17:00')),JSON.stringify({date:'2026-11-01',minutes:1020}));
  assert.equal(v2ParseLocalStamp('2026-11-01 25:00'),null);
  assert.equal(v2ParseLocalStamp('2026-11-01 17:5x'),null);
  assert.equal(v2ParseLocalStamp(''),null);
  assert.equal(v2ParseLocalStamp(null),null);
  // Day rows with a malformed local_date are skipped, not rendered.
  const rows2=[day('bad-date',['09:00']),day('2026-11-03',['08:00'])];
  assert.equal(v2NextWindowLocal(rows2,now(['2026-11-01',18*60]),''),'2026-11-03 08:00');
});

test('CL-UI-13 (g): wiring — v2BestForSpot validates nextLocal via the spot timezone',()=>{
  const v2VerdictBlock=grab('function localNowMinutes','function v2HoursSortValue');
  // The helper is now-injected (pure) and fed from the spot's own timezone.
  assert.match(v2VerdictBlock,/best\.nextLocal=v2NextWindowLocal\(best\.oppDays,v2LocalNow\(tz\),ng\?ng\.local:''\);/);
  // The best candidate carries its own day rows for the fallback scan.
  assert.match(v2VerdictBlock,/oppDays:o\.days\|\|\[\]/);
  // The card renders the row only when a validated future value exists.
  const createSpotCardBlock=block('function createSpotCard','function distanceToSpotKm');
  assert.match(createSpotCardBlock,/v2Best\.nextLocal\?`<div class="best-window-row">\$\{esc\(d\(\)\.v2_next_window\)\}<b>\$\{esc\(v2Best\.nextLocal\)\}<\/b><\/div>`:''/);
  // Fail-closed doc: the row renders only through the guarded ternary above;
  // there is no unconditional v2_next_window rendering outside it.
  const summaryMatches=[...createSpotCardBlock.matchAll(/best-window-row">\$\{esc\(d\(\)\.v2_next_window\)\}/g)].length;
  assert.equal(summaryMatches,1);
});
