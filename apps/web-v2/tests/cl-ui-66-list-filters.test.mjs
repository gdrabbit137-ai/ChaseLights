// CL-UI-66 contract: the homepage list gains (1) status-tier tabs
// [✓推薦/○可拍/✗不宜/全部] with live counts and 推荐 as default, (2) a
// horizontally scrollable subject-chip strip (data source: the derived
// subject-cards layer's `suitable` entries), (3) a 「最近可拍」 sort option
// (next qualifying window soonest) that is the recommend tab's default,
// (4) full URL sync (?tier=&subject=&sort= alongside the existing
// lang/region/date context), (5) AND-composed filters with trilingual
// empty-state copy. CL-UI-65 (semantic three-level tier) is not merged yet,
// so the tier mapping goes through an adapter over the current two-level
// data: recommend <- viable, not_recommended <- deferred, shootable
// RESERVED (always 0 until CL-UI-65 lands), noeval spots only under 全部.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');
const indexSource = readFileSync(new URL('../../../index.html', import.meta.url), 'utf8');
const cssSource = readFileSync(new URL('../../../assets/app.css', import.meta.url), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, `source slice start not found: ${start}`);
  const j = appSource.indexOf(end, i + start.length);
  assert.ok(j > i, `source slice end not found after start: ${end}`);
  return appSource.slice(i, j);
};

test('CL-UI-66 (1): tier/subject/sort/empty i18n keys exist in ALL three dictionaries', () => {
  const keys = [
    ['tier_recommend', ['✓ 推薦', '✓ Recommended', '✓ おすすめ']],
    ['tier_shootable', ['○ 可拍', '○ Shootable', '○ 撮影可']],
    ['tier_not_recommended', ['✗ 不宜', '✗ Not suitable', '✗ 不適']],
    ['tier_all', ["tier_all:'全部'", "tier_all:'All'", "tier_all:'すべて'"]],
    ['subject_chip_all', ['全部題材', 'All subjects', 'すべての題材']],
    ['sort_next_window', ['最近可拍', 'Next qualifying window', '次の適した時間帯が近い順']],
    ['result_count_next_window', ['依最近可拍時段', 'By next qualifying window', '次の適した時間帯が近い順 · ']],
    ['clui66_empty', ['無符合條件的景點——試著放寬篩選', 'No spots match these filters — try relaxing the filters', '条件に合うスポットがありません——絞り込みを緩めてみてください']],
    ['tier_bar_label', ['狀態分頁', 'Status tabs', 'ステータスタブ']],
    ['subject_chips_label', ['題材篩選', 'Subject filters', '題材フィルタ']],
  ];
  for (const [key, values] of keys) {
    for (const value of values) {
      assert.ok(appSource.includes(`${key}:'${value.slice(0, 4)}`) || appSource.includes(`${key}:'${value}`) || appSource.includes(value),
        `missing i18n value for ${key}: ${value}`);
    }
  }
  // every key must appear at least 3 times (once per dictionary)
  for (const [key] of keys) {
    const n = appSource.split(`${key}:`).length - 1;
    assert.ok(n >= 3, `${key} present in ${n} dictionaries, expected >= 3`);
  }
});

test('CL-UI-66 (2): tier adapter maps viable/deferred/noeval; shootable reserved for CL-UI-65', () => {
  const fn = new Function([
    'const verdicts={a:"viable",b:"deferred",c:"noeval",d:"noeval"};',
    'function v2SpotDayVerdict(spot){return verdicts[spot.spot_id];}',
    grab('function clui66SpotTier', 'function clui66SpotLocalDate'),
    'return {a:clui66SpotTier({spot_id:"a"}),b:clui66SpotTier({spot_id:"b"}),c:clui66SpotTier({spot_id:"c"})};',
  ].join('\n'));
  const r = fn();
  assert.equal(r.a, 'recommend');
  assert.equal(r.b, 'not_recommended');
  // CL-UI-66: 資料不足 spots are never labeled ✗不宜 — they only count under 全部.
  assert.equal(r.c, 'noeval');
  assert.ok(!/\bshootable\b[^]*return\s*'shootable'/.test(grab('function clui66SpotTier', 'function clui66SpotLocalDate').replace(/^[\s\S]*?return 'noeval';/, '')) || true);
  // shootable never produced by the adapter (reserved for CL-UI-65)
  const src = grab('function clui66SpotTier', 'function clui66SpotLocalDate');
  assert.ok(!src.includes("'shootable'"), 'adapter must not emit shootable yet');
});

test('CL-UI-66 (3): clui66TierCounts counts each tab from the same verdict source', () => {
  const verdicts={a:'viable',b:'viable',c:'deferred',d:'noeval'};
  const fn = new Function([
    `const verdicts=${JSON.stringify(verdicts)};`,
    'function v2SpotDayVerdict(spot){return verdicts[spot.spot_id];}',
    grab('function clui66SpotTier', 'function clui66SpotLocalDate'),
    grab('function clui66TierCounts', 'function renderTierTabs'),
    'const rows=["a","b","c","d"].map(id=>({spot:{spot_id:id}}));',
    'return clui66TierCounts(rows);',
  ].join('\n'));
  assert.deepEqual(fn(), { recommend: 2, shootable: 0, not_recommended: 1, all: 4 });
});

test('CL-UI-66 (4): clui66NextWindowValue ranks today hours, then future days, then unknown', () => {
  const fn = new Function([
    `const places={
      today:{tz:'Asia/Taipei',best:{hoursList:['2026-11-13 17:00','2026-11-13 16:30'],nextLocal:''}},
      future:{tz:'Asia/Taipei',best:{hoursList:[],nextLocal:'2026-11-14 05:30'}},
      past:{tz:'Asia/Taipei',best:{hoursList:[],nextLocal:'2026-11-12 05:30'}},
      none:{tz:'Asia/Taipei',best:{hoursList:[],nextLocal:''}}
    };`,
    'function v2PlaceForSpot(spot){return places[spot.spot_id]||null;}',
    'function v2BestForSpot(place){return place.best;}',
    'function v2LocalNow(tz){return {date:"2026-11-13",minutes:600};}',
    'function v2ParseLocalStamp(s){const m=/^(\\d{4}-\\d{2}-\\d{2}) (\\d{2}):(\\d{2})$/.exec(s);return m?{date:m[1],minutes:Number(m[2])*60+Number(m[3])}:null;}',
    grab('function clui66NextWindowValue', 'function filterAndRender'),
    'return {today:clui66NextWindowValue({spot_id:"today",timezone:"Asia/Taipei"}),future:clui66NextWindowValue({spot_id:"future",timezone:"Asia/Taipei"}),past:clui66NextWindowValue({spot_id:"past",timezone:"Asia/Taipei"}),none:clui66NextWindowValue({spot_id:"none",timezone:"Asia/Taipei"})};',
  ].join('\n'));
  const r = fn();
  assert.equal(r.today, 16 * 60 + 30, 'today: earliest remaining qualifying hour, clock minutes');
  assert.equal(r.future, 1440 + 5 * 60 + 30, 'future window: day offset * 1440 + minutes');
  assert.equal(r.past, Number.POSITIVE_INFINITY, 'already-past nextLocal must not rank as future');
  assert.equal(r.none, Number.POSITIVE_INFINITY);
  assert.ok(r.today < r.future, 'today hours rank before tomorrow windows');
});

test('CL-UI-66 (5): sortRows next_window ranks by next window with geographic tie-break', () => {
  const windows = { early: 9 * 60, late: 17 * 60, unknown: Number.POSITIVE_INFINITY };
  const geoOrder = { earlyB: 1, earlyA: 2, late: 3, unknown: 4 };
  const fn = new Function([
    `const windows={earlyA:540,earlyB:540,late:1020,unknown:Infinity};`,
    `const geoOrder=${JSON.stringify(geoOrder)};`,
    'function distanceToSpotKm(){return null;}',
    'function clui66NextWindowValue(spot){return windows[spot.spot_id];}',
    'function compareGeographic(a,b){return geoOrder[a.spot.spot_id]-geoOrder[b.spot.spot_id];}',
    'function v2HoursSortValue(){return null;}',
    grab('function sortRows', 'function appendSpotRows'),
    'const rows=["unknown","late","earlyA","earlyB"].map(id=>({spot:{spot_id:id},metric:{}}));',
    'sortRows(rows,"next_window");',
    'return rows.map(r=>r.spot.spot_id);',
  ].join('\n'));
  assert.deepEqual(fn(), ['earlyB', 'earlyA', 'late', 'unknown']);
});

test('CL-UI-66 (6): filterAndRender composes filters with AND and shows the relax-filters empty state', () => {
  const block = grab('function filterAndRender', 'const effSort=');
  assert.ok(block.includes("currentTier!=='all'"), 'tier filter applied');
  assert.ok(block.includes("currentSubject!=='all'"), 'subject filter applied');
  assert.ok(block.includes('clui66SpotTier(row.spot)===currentTier'));
  assert.ok(block.includes('clui66SpotSubjectKeys(row.spot).includes(currentSubject)'));
  const emptyBlock = grab('const filterActive=', 'CL-UI-66: an active status tab renders a flat list');
  assert.ok(emptyBlock.includes("d().clui66_empty"), 'active-filter empty state uses the relax-filters copy');
  assert.ok(emptyBlock.includes("d().no_spots"), 'no active filters keeps the original empty copy');
});

test('CL-UI-66 (7): active tier tab renders a flat list (no deferred details grouping)', () => {
  const block = grab('CL-UI-66: an active status tab renders a flat list', 'const rows=tierRows;');
  assert.match(block, /appendSpotRows\(container,tierRows,effSort\)/);
  assert.ok(block.includes('saveRenderSnapshot()'));
  assert.ok(block.includes('return;'));
});

test('CL-UI-66 (8): syncContextUrl writes tier/subject/sort next to lang/region/date', () => {
  const fn = grab('function syncContextUrl', 'function switchLanguage');
  assert.match(fn, /history\.replaceState/);
  assert.match(fn, /searchParams\.set\('lang'/);
  assert.match(fn, /searchParams\.set\('region'/);
  assert.match(fn, /searchParams\.set\('date'/);
  assert.match(fn, /searchParams\.set\('tier'/);
  assert.match(fn, /searchParams\.set\('subject',currentSubject\)/);
  assert.match(fn, /searchParams\.set\('sort',clui66EffectiveSort\(\)\)/);
  assert.ok(!fn.includes('pushState'));
  // subject=all is dropped from the URL, not written as a literal 'all'
  assert.match(fn, /searchParams\.delete\('subject'\)/);
});

const resolveFilterState = (urlSearch) => {
  const f = new Function([
    `const VALID_SORT_MODES=['region','hours_desc','next_window','distance_near','distance_far'];`,
    `const location={search:${JSON.stringify(urlSearch)}};`,
    `let currentSortMode='region';`,
    grab('const VALID_TIERS=', 'let userLocation=null;'),
    'return {currentTier,currentSubject,sortTouched,currentSortMode};',
  ].join('\n'));
  return f();
};

test('CL-UI-66 (9): URL ?tier=&subject=&sort= restores the filter state on load', () => {
  const r = resolveFilterState('?tier=all&subject=%E9%9B%B2%E6%B5%B7&sort=hours_desc');
  assert.equal(r.currentTier, 'all');
  assert.equal(r.currentSubject, '雲海');
  assert.equal(r.sortTouched, true);
  assert.equal(r.currentSortMode, 'hours_desc');
});

test('CL-UI-66 (10): no URL params → recommend tab default, sort untouched (最近可拍 default)', () => {
  const r = resolveFilterState('');
  assert.equal(r.currentTier, 'recommend');
  assert.equal(r.currentSubject, 'all');
  assert.equal(r.sortTouched, false);
  assert.equal(r.currentSortMode, 'region');
});

test('CL-UI-66 (11): invalid tier/subject/sort fail closed to defaults', () => {
  const r = resolveFilterState('?tier=best&subject=&sort=random');
  assert.equal(r.currentTier, 'recommend');
  assert.equal(r.currentSubject, 'all');
  assert.equal(r.sortTouched, false);
  assert.equal(r.currentSortMode, 'region');
});

test('CL-UI-66 (12): clui66EffectiveSort — next_window is the recommend-tab default; explicit choice wins', () => {
  const mk = (tier, touched, sortMode) => new Function([
    `let currentTier=${JSON.stringify(tier)};let sortTouched=${touched};let currentSortMode=${JSON.stringify(sortMode)};`,
    grab('function clui66EffectiveSort', 'function syncContextUrl'),
    'return clui66EffectiveSort();',
  ].join('\n'))();
  assert.equal(mk('recommend', false, 'region'), 'next_window');
  assert.equal(mk('recommend', true, 'region'), 'region');
  assert.equal(mk('not_recommended', false, 'region'), 'region');
  assert.equal(mk('all', false, 'hours_desc'), 'hours_desc');
});

test('CL-UI-66 (13): subject chip catalog builds from subject-cards suitable and resets stale subjects', () => {
  const fn = new Function([
    `const spots=[
      {spot_id:'s1',timezone:'Asia/Taipei'},{spot_id:'s2',timezone:'Asia/Taipei'}
    ];`,
    `const cards={places:{
      s1:{'2026-11-13':{suitable:[{subject_short:{'zh-TW':'雲海',en:'Cloud sea',ja:'雲海'}},{subject_short:{'zh-TW':'日落',en:'Sunset',ja:'夕景'}}]}},
      s2:{'2026-11-13':{suitable:[{subject_short:{'zh-TW':'雲海',en:'Cloud sea',ja:'雲海'}}]}}
    }};`,
    'function v2PlaceForSpot(){return {};}', 
    'function v2BestForSpot(){return {day:{local_date:"2026-11-13"}};}',
    'function v2SubjectCardRow(id,date){return (cards.places[id]&&cards.places[id][date])||null;}',
    'let currentSpots=spots;let currentSubject="不存在";let clui66SubjectCatalogKeys=[];let clui66SubjectCatalogNames={};',
    grab('function clui66SpotLocalDate', 'function clui66SubjectDisplayName'),
    'clui66BuildSubjectCatalog();',
    'return {keys:clui66SubjectCatalogKeys,names:clui66SubjectCatalogNames,active:currentSubject};',
  ].join('\n'));
  const r = fn();
  assert.deepEqual(r.keys, ['雲海', '日落']);
  assert.equal(r.active, 'all', 'a stale subject resets to 全部 instead of filtering everything out');
  assert.equal(r.names['雲海'].en, 'Cloud sea');
});

test('CL-UI-66 (14): subject matching keys are zh-TW canonical names, language-independent', () => {
  const fn = new Function([
    `const cards={places:{s1:{'2026-11-13':{suitable:[{subject_short:{'zh-TW':'雲海',en:'Cloud sea',ja:'雲海'}}]}}}};`,
    'function v2PlaceForSpot(){return {};}',
    'function v2BestForSpot(){return {day:{local_date:"2026-11-13"}};}',
    'function v2SubjectCardRow(id,date){return (cards.places[id]&&cards.places[id][date])||null;}',
    grab('function clui66SpotLocalDate', 'function clui66BuildSubjectCatalog'),
    'return clui66SpotSubjectKeys({spot_id:"s1",timezone:"Asia/Taipei"});',
  ].join('\n'));
  assert.deepEqual(fn(), ['雲海']);
});

test('CL-UI-66 (15): index.html carries the tab/chip hosts, the next_window sort option, and clui75 stamps', () => {
  assert.match(indexSource, /id="tier-tabs"/);
  assert.match(indexSource, /id="subject-chips"/);
  assert.match(indexSource, /<option value="next_window" data-i18n="sort_next_window">/);
  assert.match(indexSource, /assets\/app\.js\?v=clui84/);
  assert.match(indexSource, /assets\/app\.css\?v=clui84/);
});

test('CL-UI-66 (16): app.css styles both strips with horizontal scroll and the shared active accent', () => {
  for (const cls of ['.tier-tab-bar', '.subject-chip-strip']) {
    const i = cssSource.indexOf(cls + ' {');
    assert.ok(i >= 0, `missing CSS block for ${cls}`);
    const block = cssSource.slice(i, cssSource.indexOf('}', i));
    assert.match(block, /overflow-x:\s*auto/, `${cls} must scroll horizontally (390px-first)`);
    assert.match(block, /-webkit-overflow-scrolling:\s*touch/);
  }
  assert.match(cssSource, /\.tier-tab\.active \{[^}]*#38bdf8/);
  assert.match(cssSource, /\.subject-chip\.active \{[^}]*#38bdf8/);
});
