// CL-UI-28 — site-wide persistent navigation (blueprint §7 IA rework).
// Covers: 1) identical nav DOM on all four pages with correct active marks;
// 2) CL-UI-54: the 更多工具 dropdown is GONE (owner ruling: genre-eval /
//    field-intake didn't help users); the page FILES stay (direct URLs work);
// 3) cross-page region carry (cards → WeatherGrid and back, URL ?region=);
// 4) 390px collapse (bottom bar, ≥44px touch targets);
// 5) page toolbars kept below the nav (nav owns page switching only);
// 6) i18n keys in all three dictionaries; 7) cache-bust stamp bumps.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const read = (p) => readFileSync(join(root, p), 'utf8');

const indexHtml = read('index.html');
const wgHtml = read('weather-map.html');
const genreHtml = read('genre-eval.html');
const fieldHtml = read('field-intake.html');
const appJs = read('assets/app.js');
const wgJs = read('assets/weather-map.js');
const navCss = read('assets/site-nav.css');

function navBlock(html) {
  const m = html.match(/<nav class="site-nav"[\s\S]*?<\/nav>/);
  assert.ok(m, 'site-nav <nav> block present');
  return m[0];
}
// Normalize the shared DOM: strip the page-specific active marks.
function normalized(html) {
  return navBlock(html).replace(/ data-active="page"/g, '');
}

test('CL-UI-28 (1): all four pages share ONE identical site-nav DOM', () => {
  const pages = [indexHtml, wgHtml, genreHtml, fieldHtml];
  const norm = pages.map(normalized);
  assert.equal(norm[1], norm[0], 'weather-map.html nav DOM matches index');
  assert.equal(norm[2], norm[0], 'genre-eval.html nav DOM matches index');
  assert.equal(norm[3], norm[0], 'field-intake.html nav DOM matches index');
  for (const html of pages) {
    const nav = navBlock(html);
    assert.match(nav, /data-nav-target="cards"/);
    assert.match(nav, /data-nav-target="weather"/);
    assert.match(nav, /aria-expanded="false"/);
    // CL-UI-54: no 更多工具 dropdown in the nav anymore.
    assert.doesNotMatch(nav, /data-nav-more/);
    assert.doesNotMatch(nav, /nav_more_tools/);
    assert.doesNotMatch(nav, /genre-eval\.html/);
    assert.doesNotMatch(nav, /field-intake\.html/);
  }
  // The nav is included on every page.
  for (const html of pages) assert.match(html, /assets\/site-nav\.css/);
  for (const html of pages) assert.match(html, /assets\/site-nav\.js/);
});

test('CL-UI-28 (2): active mark marks the CURRENT page (cards / weather only)', () => {
  assert.match(navBlock(indexHtml), /data-nav-target="cards" data-active="page"/);
  assert.match(navBlock(wgHtml), /data-nav-target="weather" data-active="page"/);
  assert.doesNotMatch(navBlock(indexHtml), /data-nav-target="weather" data-active="page"/);
  assert.doesNotMatch(navBlock(wgHtml), /data-nav-target="cards" data-active="page"/);
});

test('CL-UI-54: genre-eval / field-intake pages still exist outside the nav', () => {
  // Nav demotion was replaced by full removal (CL-UI-54); direct URLs work.
  const genre = read('genre-eval.html');
  const field = read('field-intake.html');
  assert.match(genre, /<nav class="site-nav"/);
  assert.match(field, /<nav class="site-nav"/);
  assert.doesNotMatch(genre, /data-nav-more/);
  assert.doesNotMatch(field, /data-nav-more/);
});

test('CL-UI-28 (3): cards → WeatherGrid carries the current region', () => {
  // app.js keeps the region links pointed at ?region=<current region>.
  assert.match(appJs, /function updateNavRegionLinks\(\)/);
  assert.match(appJs, /\.\/weather-map\.html\?region='\+encodeURIComponent\(currentRegion\)/);
  assert.match(appJs, /'\.site-nav a\[data-nav-target="weather"\]'/);
  assert.match(appJs, /loadData\(k\);updateNavRegionLinks\(\)/);
  assert.match(appJs, /syncDayButtons\(\);updateNavRegionLinks\(\)/);
});

test('CL-UI-28 (4): WeatherGrid → cards carries the region back', () => {
  assert.match(wgJs, /\.\/index\.html\?region='\+encodeURIComponent\(regionId\)/);
  assert.match(wgJs, /'\.site-nav a\[data-nav-target="cards"\]'/);
});

test('CL-UI-28 (5): cards page honors the ?region= URL param (fail-closed)', () => {
  assert.match(appJs, /new URLSearchParams\(location\.search\)\.get\('region'\)/);
  assert.match(appJs, /VALID_REGIONS\.includes\(urlRegion\)&&urlRegion!==currentRegion/);
  assert.match(appJs, /switchRegion\(urlRegion\)/);
});

test('CL-UI-28 (6): 390px collapse — bottom bar, ≥44px touch targets', () => {
  assert.match(navCss, /@media \(max-width: 640px\)/);
  assert.match(navCss, /position: fixed;\s*\n\s*left: 0;\s*\n\s*right: 0;\s*\n\s*bottom: 0;/);
  assert.match(navCss, /padding-bottom: 64px;/);
  assert.match(navCss, /min-height: 44px/);
  assert.match(navCss, /min-height: 48px/); // mobile bump for touch
  assert.match(navCss, /env\(safe-area-inset-bottom/);
  // 更多工具 menu opens upward on mobile
  assert.match(navCss, /\.site-nav-menu \{[\s\S]*?bottom: calc\(100% - 64px \+ 4px\);/);
});

test('CL-UI-28 (7): page toolbars stay below the nav (nav = switching only)', () => {
  // Cards page keeps region/day/sort toolbar; WeatherGrid keeps layer/region
  // controls; both come AFTER the nav block in document order.
  const idxPos = indexHtml.indexOf('</nav>');
  assert.ok(indexHtml.indexOf('id="sub-nav"', idxPos) > idxPos);
  assert.ok(indexHtml.indexOf('id="spot-sort"', idxPos) > idxPos);
  const wgPos = wgHtml.indexOf('</nav>');
  assert.ok(wgHtml.indexOf('id="region-switch"', wgPos) > wgPos);
  assert.ok(wgHtml.indexOf('id="layer-select"', wgPos) > wgPos);
});

test('CL-UI-28 (8): nav i18n keys exist in all three dictionaries', () => {
  for (const src of [appJs, read('assets/genre-eval.js'), read('assets/field-intake.js')]) {
    for (const key of ['nav_cards', 'nav_weathermap', 'nav_more_tools', 'nav_genre_eval', 'nav_field_intake']) {
      assert.match(src, new RegExp(`${key}:`), `${key} present`);
    }
  }
  // No internal/provisional wording leaks into the nav labels.
  for (const s of ['nav_cards', 'nav_weathermap', 'nav_more_tools']) {
    assert.ok(!appJs.match(new RegExp(`${s}:'[^']*'`))?.[0]?.match(/provisional|draft|internal/));
  }
});

test('CL-UI-28 (9): index.html stamp bumped clui33 → clui41', () => {
  // CL-UI-53B: site-nav.css advanced to clui62 (site-nav.js stays clui41).
  assert.match(indexHtml, /assets\/site-nav\.css\?v=clui62/);
  assert.match(indexHtml, /assets\/site-nav\.js\?v=clui41/);
  assert.match(indexHtml, /assets\/app\.js\?v=clui61/);
  assert.match(indexHtml, /assets\/app\.css\?v=clui54/);
  assert.doesNotMatch(indexHtml, /clui29/);
});

test('CL-UI-28 (10): weather-map.js stamp bumped in weather-map.html (same commit)', () => {
  assert.match(wgHtml, /assets\/weather-map\.js\?v=bclwg34/);
  assert.doesNotMatch(wgHtml, /bclwg23|bclwg24/);
});