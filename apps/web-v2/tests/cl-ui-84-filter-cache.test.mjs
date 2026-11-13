// CL-UI-84: cache-first filter bar. Owner实测: on reload the day-picker
// counts / tier tabs / subject chips appeared only after the ~1MB evaluations
// bundle + subject-cards artifact finished downloading (applyData gates the
// single render on ensureV2EvalBundle). Fix: the last settled filter-bar
// STATE (tier counts, per-day viable counts, subject catalog) is persisted in
// localStorage with a timestamp + bundle digest and painted synchronously on
// boot; the fresh bundles then replace it seamlessly. Offline/429 over an
// expired cache keeps the cached bar behind the honest 「顯示上次資料」 label.
// Source assertions + extracted cache helpers, per the established V1-shell
// test pattern.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};

// ---- 1. wiring: save on settled render, restore on boot before any fetch ----
test('CL-UI-84 (1): filter-bar state is persisted on every settled render and restored synchronously on boot', () => {
  assert.ok(appSource.includes("FILTER_CACHE_KEY_PREFIX='chaselights_filter_cache_'"), 'localStorage key prefix present');
  const save = grab('function saveFilterCache', 'function loadFilterCache');
  assert.ok(save.includes('if(!v2EvalBundle)return;'), 'saveFilterCache never persists a bundle-less (fail-closed) state');
  assert.ok(save.includes('localStorage.setItem(filterCacheKey(currentRegion)'), 'persists under the region key');
  assert.ok(save.includes('digest:clui84Digest()'), 'payload carries the bundle digest');
  assert.ok(save.includes('saved_at:Date.now()'), 'payload carries a timestamp for expiry');
  assert.ok(save.includes('tier_counts:clui66TierCounts(rowsAll)'), 'tier tab counts saved');
  assert.ok(save.includes('day_counts:dayCounts'), 'per-day picker counts saved');
  assert.ok(save.includes('subject_keys:clui66SubjectCatalogKeys.slice()'), 'subject chip catalog saved');
  // filterAndRender persists after the real render (not in the cached-fallback branch)
  const fr = grab('function filterAndRender', 'function opportunityScoreClass');
  assert.ok(fr.includes('saveFilterCache(rowsAll);'), 'filterAndRender persists the settled state');
  const saveIdx = fr.indexOf('saveFilterCache(rowsAll);');
  const fallbackBranch = fr.indexOf('if(!v2EvalBundle&&clui84FilterCache){');
  assert.ok(fallbackBranch >= 0 && fallbackBranch < saveIdx, 'bundle-failure branch never overwrites the cache');
  // loadData paints the cached bar BEFORE any fetch work
  const ld = grab('async function loadData', 'function selectedDayOffset');
  const restoreIdx = ld.indexOf('restoreFilterBarFromCache(region);');
  const fetchIdx = ld.indexOf('await cacheMatch(');
  assert.ok(restoreIdx > 0 && fetchIdx > restoreIdx, 'cache-first paint precedes the first network wait');
  // applyData still gates the card render on the bundle (gate semantics unchanged)
  assert.ok(appSource.includes('ensureV2EvalBundle().then(bundle=>{if(seq===activeLoadSequence&&region===currentRegion){filterAndRender();'), 'single gated render preserved');
});

// ---- 2. extracted helpers: digest + cache validation ----
function makeCacheHelpers() {
  const digest = grab('function clui84Hash', 'function saveFilterCache');
  const loader = grab('function loadFilterCache', 'function clui84RenderTabsFromCounts');
  const prelude = `
    const FILTER_CACHE_KEY_PREFIX='chaselights_filter_cache_';
    const FILTER_CACHE_MAX_AGE_MS=24*60*60*1000;
    const filterCacheKey=region=>\`\${FILTER_CACHE_KEY_PREFIX}\${region}\`;
    let clui84FilterCache=null, clui84CacheStale=false;
    let currentLang='zh-TW';
    const store={};
    const localStorage={getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=String(v);},removeItem:k=>{delete store[k];}};
  `;
  return new Function(prelude + digest + loader + 'return {clui84Hash,clui84Digest,loadFilterCache,store,get state(){return {clui84FilterCache,clui84CacheStale};}};')();
}

test('CL-UI-84 (2): digest changes with the bundle generation stamp', () => {
  const h = makeCacheHelpers();
  const src = grab('function clui84Digest', 'function saveFilterCache');
  const fn = new Function('v2EvalBundle', 'v2SubjectCards', 'clui84Hash', src + '; return clui84Digest();');
  const digest = fn({generated_at: '2026-11-13T07:12:12Z'}, {schema_version: '1.3'}, h.clui84Hash);
  const digest2 = fn({generated_at: '2026-11-14T07:12:12Z'}, {schema_version: '1.3'}, h.clui84Hash);
  const none = fn(null, null, h.clui84Hash);
  assert.equal(none, '', 'no bundle → empty digest (never persisted)');
  assert.notEqual(digest, digest2, 'a new bundle generation produces a different digest');
  assert.equal(digest, fn({generated_at: '2026-11-13T07:12:12Z'}, {schema_version: '1.3'}, h.clui84Hash), 'same bundle → stable digest');
});

test('CL-UI-84 (3): loadFilterCache validates region/lang/version and tolerates corruption', () => {
  const h = makeCacheHelpers();
  const good = {v: 1, region: 'tw', lang: 'zh-TW', saved_at: Date.now(), digest: 'abc',
    tier_counts: {recommend: 3, shootable: 5, not_recommended: 9, all: 17},
    day_counts: {today: 3, tomorrow: 4}, subject_keys: ['雲海'], subject_names: {'雲海': {'zh-TW': '雲海'}}};
  h.store['chaselights_filter_cache_tw'] = JSON.stringify(good);
  assert.deepEqual(h.loadFilterCache('tw').tier_counts, good.tier_counts, 'fresh valid cache loads');
  assert.equal(h.loadFilterCache('jp'), null, 'other region → miss');
  h.store['chaselights_filter_cache_tw'] = '{"v":1,broken';
  assert.equal(h.loadFilterCache('tw'), null, 'corrupt JSON → miss, never throws');
  h.store['chaselights_filter_cache_tw'] = JSON.stringify({...good, lang: 'en'});
  assert.equal(h.loadFilterCache('tw'), null, 'language mismatch → miss');
  h.store['chaselights_filter_cache_tw'] = JSON.stringify({...good, v: 0});
  assert.equal(h.loadFilterCache('tw'), null, 'unknown payload version → miss');
  h.store['chaselights_filter_cache_tw'] = JSON.stringify({...good, subject_keys: 'nope'});
  assert.equal(h.loadFilterCache('tw'), null, 'malformed catalog → miss');
});

// ---- 4. dayPickerViableCount cache-first fallback ----
test('CL-UI-84 (4): day-picker counts answer from the cache while the bundle is absent', () => {
  const src = grab('function dayPickerViableCount', 'function dayPickerOption');
  const fn = new Function('v2EvalBundle', 'clui84FilterCache', 'DAY_OFFSETS', 'currentSpots', 'v2PlaceForSpot', 'v2DayForOffset', 'v2EffectiveHours',
    src + '; return dayPickerViableCount;')(
    null,
    {day_counts: {today: 7, tomorrow: null}},
    {today: 0, tomorrow: 1},
    [], () => null, () => null, () => []);
  assert.equal(fn('today'), 7, 'cache-backed count painted before the bundle arrives');
  assert.equal(fn('tomorrow'), null, 'a cached null (資料不足) stays honest');
  assert.equal(fn('after_tomorrow'), null, 'day missing from cache → honest null, not 0');
  // with a real bundle the cache is bypassed (live computation path unchanged)
  const fnLive = new Function('v2EvalBundle', 'clui84FilterCache', 'DAY_OFFSETS', 'currentSpots', 'v2PlaceForSpot', 'v2DayForOffset', 'v2EffectiveHours',
    src + '; return dayPickerViableCount;')(
    {places: []}, {day_counts: {today: 7}}, {today: 0}, [], () => null, () => null, () => []);
  assert.equal(fnLive('today'), null, 'live path: no matching place → null (unchanged)');
});

// ---- 5. offline degradation: cached bar survives a failed fetch, honestly labeled ----
test('CL-UI-84 (5): bundle fetch failure keeps the cached bar and shows the honest last-data label', () => {
  const fr = grab('function filterAndRender', 'let tierRows=rowsAll');
  assert.ok(fr.includes('if(!v2EvalBundle&&clui84FilterCache){'), 'failure branch keeps the cached bar');
  assert.ok(fr.includes('showUpdateIndicator(d().cache_last_data)'), 'failure branch labels the stale bar 「顯示上次資料」');
  assert.ok(fr.includes('clui84RenderTabsFromCounts(clui84FilterCache.tier_counts)'), 'cached counts repaint the tabs');
  const thenBlock = grab('ensureV2EvalBundle().then(bundle=>{', 'return true;}');
  assert.ok(thenBlock.includes('if(bundle){clui84BundleSettled=true;clui84CacheStale=false;hideUpdateIndicator();}else{clui84BundleSettled=true;if(clui84FilterCache)showUpdateIndicator(d().cache_last_data);'), 'settle: success clears the hint + stale flag, failure relabels it honestly');
  assert.ok(appSource.includes('function showUpdateIndicator(text){'), 'banner accepts the honest-label override');
  assert.ok(appSource.includes('showUpdateIndicator(clui84BundleSettled?d().cache_last_data:d().updating)'), 'applyData cannot overwrite the honest label after a settled bundle failure');
});

// ---- 6. first-time visitors unchanged: no cache → no cache paint, old loading path ----
test('CL-UI-84 (6): first-time visitors keep the old behavior', () => {
  const r = grab('function restoreFilterBarFromCache', 'const d=()=>i18nDict');
  assert.ok(r.includes('const c=loadFilterCache(region);'), 'restore reads the cache first');
  assert.ok(r.includes('if(!c){'), 'a cache miss leaves the bar untouched (loading path unchanged)');
  assert.ok(r.includes('if(clui84CacheStale)showUpdateIndicator();'), 'an expired cache still paints first, behind the updating banner');
  assert.ok(r.includes('Number.isFinite(c.saved_at)&&Date.now()-c.saved_at<=FILTER_CACHE_MAX_AGE_MS'), 'staleness decided by the saved timestamp');
});

// ---- 7. i18n: the honest label exists in all three dictionaries ----
test('CL-UI-84 (7): cache_last_data exists in zh-TW / en / ja', () => {
  assert.ok(appSource.includes("cache_last_data:'顯示上次資料'"), 'zh-TW');
  assert.ok(appSource.includes("cache_last_data:'Showing last saved data'"), 'en');
  assert.ok(appSource.includes("cache_last_data:'前回のデータを表示中'"), 'ja');
});

// ---- 8. cache-bust stamp bumped and pinned ----
test('CL-UI-84 (8): index.html serves app.js + app.css at clui89', () => {
  assert.equal((indexSource.match(/\?v=clui89/g) || []).length, 2, 'app.js + app.css both at clui89');
  assert.ok(!indexSource.includes('clui87'), 'no stale clui87 stamp left on the homepage');
});
