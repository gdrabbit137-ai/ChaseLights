// CL-UI-45: mobile (390px) day-strip fix on the card page.
// Owner symptom: at 390px the date tabs showed only 「今天 …」 — the media
// block's later `.day-nav-strip { overflow: hidden }` re-applied clipping on
// the shared .day-nav-bar element, so the 7 chips overflowed past one row
// with no scrollbar and no reachable tabs.
// Fix contract:
//  (1) ≤640px the strip is a horizontal scroll strip (overflow-x:auto) with
//      an edge fade-out mask hint — never overflow:hidden on the strip.
//  (2) ‹ › arrow buttons flank the strip inside .day-nav-wrap, with
//      data-i18n-aria-label keys present in ALL three dictionaries.
//  (3) app.js wires scrollDayNav(dir), syncDayNavArrows() (disabled at the
//      strip's start/end), and scroll-syncs the active chip into view from
//      syncDayButtons (URL ?date= / restored preference stays reachable).
// (4) Cache-bust stamps bumped to clui48 in the same commit.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const htmlSource=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
const block=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,appSource.indexOf(start))
);
const i18nBlock=block('const i18nDict = {','const categoryKeys = {');

test('CL-UI-45 (1): mobile media block renders a scroll strip, never a clipped one',()=>{
  const media=cssSource.slice(cssSource.indexOf('@media (max-width: 640px)'),cssSource.indexOf('.sub-btn.active'));
  assert.match(media,/\.day-nav-strip\s*\{[^}]*overflow-x:\s*auto;/,'strip scrolls horizontally at 390px');
  assert.doesNotMatch(media,/\.day-nav-strip\s*\{[^}]*overflow:\s*hidden;/,'root cause regression guard: strip must not be overflow:hidden');
  // Edge fade-out hint: a mask that fades the strip's right edge.
  assert.match(media,/\.day-nav-strip\s*\{[^}]*mask-image:\s*linear-gradient\(to right/,'edge fade-out hint present');
  assert.match(media,/\.day-nav-wrap\s*\{\s*display:\s*flex;/,'wrap row hosts strip + arrows');
});

test('CL-UI-45 (2): ‹ › arrow buttons flank the strip with trilingual labels',()=>{
  const nav=htmlSource.slice(htmlSource.indexOf('id="day-nav"'),htmlSource.indexOf('admin-filter'));
  assert.match(htmlSource,/id="day-nav-prev"[^>]*data-i18n-aria-label="day_nav_prev"[^>]*onclick="scrollDayNav\(-1\)"/);
  assert.match(htmlSource,/id="day-nav-next"[^>]*data-i18n-aria-label="day_nav_next"[^>]*onclick="scrollDayNav\(1\)"/);
  assert.match(nav,/day-btn-far[\s\S]*<\/div>\s*<button[^>]*id="day-nav-next"/,'next arrow sits after the strip');
  assert.match(cssSource,/\.day-nav-arrow\s*\{[^}]*cursor:\s*pointer;/);
  assert.match(cssSource,/\.day-nav-arrow:disabled\s*\{\s*opacity:\s*0\.3;/,'arrows gray out at strip ends');
  for(const key of ['day_nav_prev','day_nav_next']){
    const vals=[...i18nBlock.matchAll(new RegExp(`${key}:'([^']*)'`,'g'))].map(m=>m[1]);
    assert.equal(vals.length,3,`${key} must exist in all three dictionaries`);
    vals.forEach(v=>assert.ok(v.length>=6,`${key} carries a meaningful spoken label`));
  }
});

test('CL-UI-45 (3): app.js wires arrow scroll + honest end states + active-chip reachability',()=>{
  const syncArrows=block('function syncDayNavArrows','function scrollDayNav');
  const syncBtns=block('function syncDayButtons','function switchDay');
  assert.match(block('function scrollDayNav','function syncDayButtons'),/scrollBy\(\{left:dir\*Math\.max\(120,Math\.round\(s\.clientWidth\*0\.7\)\),behavior:'smooth'\}\)/);
  assert.match(syncArrows,/p\.disabled=s\.scrollLeft<=2;/);
  assert.match(syncArrows,/n\.disabled=s\.scrollLeft\+s\.clientWidth>=s\.scrollWidth-2;/);
  // Active chip is nudged into view when scrolled out of sight (URL ?date=
  // deep links and restored preferences must stay operable on the strip).
  assert.match(syncBtns,/if\(br\.left<sr\.left\|\|br\.right>sr\.right\)strip\.scrollLeft\+=/);
  assert.match(syncBtns,/syncDayNavArrows\(\);/);
  // Arrows re-sync while the user swipes the strip.
  assert.match(block('function initializeApp','// CL-UI-28: region carry BACK'),/dayStrip\.addEventListener\('scroll',\(\)=>syncDayNavArrows\(\),\{passive:true\}\)/);
  // A runnable re-check of the end-state math against a stub strip.
  const fn=new Function(`
    let disabled={};
    const strip={scrollLeft:0,clientWidth:300,scrollWidth:900};
    const prev={set disabled(v){disabled.prev=v;},get disabled(){return disabled.prev;}};
    const next={set disabled(v){disabled.next=v;},get disabled(){return disabled.next;}};
    const document={getElementById:id=>id==='day-nav'?strip:id==='day-nav-prev'?prev:next};
    ${syncArrows}
    syncDayNavArrows();
    const atStart={prev:disabled.prev,next:disabled.next};
    strip.scrollLeft=650;
    syncDayNavArrows();
    const atEnd={prev:disabled.prev,next:disabled.next};
    return {atStart,atEnd};
  `);
  const r=fn();
  assert.deepEqual(r.atStart,{prev:true,next:false},'at strip start: prev disabled, next enabled');
  assert.deepEqual(r.atEnd,{prev:false,next:true},'at strip end: next disabled, prev enabled');
});

test('CL-UI-45 (4): index.html cache-bust stamps bumped to clui48 in the same commit',()=>{
  assert.match(htmlSource,/assets\/app\.js\?v=clui48/);
  assert.match(htmlSource,/assets\/app\.css\?v=clui48/);
});
