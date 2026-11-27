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
const remHtml = read('reminders.html');
const sourcesHtml = read('sources.html');
const appJs = read('assets/app.js');
const wgJs = read('assets/weather-map.js');
const navCss = read('assets/site-nav.css');

function navBlock(html) {
  const m = html.match(/<nav class="site-nav"[\s\S]*?<\/nav>/);
  assert.ok(m, 'site-nav <nav> block present');
  return m[0];
}
// Normalize the shared DOM: strip the page-specific active marks, and the
// CL-UI-126 language slot (only the 我的 page carries it — asserted separately
// below so every other nav node stays byte-identical).
function normalized(html) {
  return navBlock(html)
    .replace(/ data-active="page"/g, '')
    .replace(/\s*<span class="site-nav-lang">[\s\S]*?<\/span>\s*/g, '\n        ');
}

test('CL-UI-28 (1): all six pages share ONE identical site-nav DOM', () => {
  const pages = [indexHtml, wgHtml, genreHtml, fieldHtml, remHtml, sourcesHtml];
  const norm = pages.map(normalized);
  assert.equal(norm[1], norm[0], 'weather-map.html nav DOM matches index');
  assert.equal(norm[2], norm[0], 'genre-eval.html nav DOM matches index');
  assert.equal(norm[3], norm[0], 'field-intake.html nav DOM matches index');
  assert.equal(norm[4], norm[0], 'reminders.html nav DOM matches index');
  assert.equal(norm[5], norm[0], 'sources.html nav DOM matches index');
  for (const html of pages) {
    const nav = navBlock(html);
    assert.match(nav, /data-nav-target="cards"/);
    assert.match(nav, /data-nav-target="weather"/);
    assert.match(nav, /data-nav-target="reminders"/);
    assert.match(nav, /reminders\.html/);
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
  // CL-UI-126 (owner ruling): the 我的 page's language switcher lives in the
  // navbar. It is the ONLY page-specific nav node; every other nav byte stays
  // identical (the comparison above ignores just this slot).
  assert.match(navBlock(remHtml), /<span class="site-nav-lang">[\s\S]*?<select id="lang-select"/,
    'reminders.html carries the language slot');
  for (const [name, html] of [['index', indexHtml], ['weather-map', wgHtml], ['genre-eval', genreHtml], ['field-intake', fieldHtml], ['sources', sourcesHtml]]) {
    assert.doesNotMatch(navBlock(html), /site-nav-lang|id="lang-select"/,
      `${name}: no duplicate nav language slot`);
  }
});

test('CL-UI-28 (2): active mark marks the CURRENT page (cards / weather / reminders)', () => {
  assert.match(navBlock(indexHtml), /data-nav-target="cards" data-active="page"/);
  assert.match(navBlock(wgHtml), /data-nav-target="weather" data-active="page"/);
  assert.match(navBlock(remHtml), /data-nav-target="reminders" data-active="page"/);
  assert.doesNotMatch(navBlock(indexHtml), /data-nav-target="weather" data-active="page"/);
  assert.doesNotMatch(navBlock(indexHtml), /data-nav-target="reminders" data-active="page"/);
  assert.doesNotMatch(navBlock(wgHtml), /data-nav-target="cards" data-active="page"/);
  assert.doesNotMatch(navBlock(remHtml), /data-nav-target="cards" data-active="page"/);
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
  // CL-APP-09: the reminders nav item was renamed 「我的」 (nav_my) — the
  // reminders page mirrors the nav keys it renders.
  const navSources = [appJs, read('assets/genre-eval.js'), read('assets/field-intake.js'), read('assets/reminders-page.js')];
  for (const src of navSources) {
    for (const key of ['nav_cards', 'nav_weathermap', 'nav_my']) {
      assert.match(src, new RegExp(`${key}:`), `${key} present`);
    }
  }
  for (const src of [appJs, read('assets/genre-eval.js'), read('assets/field-intake.js')]) {
    for (const key of ['nav_more_tools', 'nav_genre_eval', 'nav_field_intake']) {
      assert.match(src, new RegExp(`${key}:`), `${key} present`);
    }
  }
  // No internal/provisional wording leaks into the nav labels.
  for (const s of ['nav_cards', 'nav_weathermap', 'nav_more_tools']) {
    assert.ok(!appJs.match(new RegExp(`${s}:'[^']*'`))?.[0]?.match(/provisional|draft|internal/));
  }
});

test('CL-UI-28 (9): index.html stamps tracked (CL-UI-73: app.js/app.css at clui102)', () => {
  // CL-UI-116: site-nav.css advanced to clui117 (brand-logo swap).
  assert.match(indexHtml, /assets\/site-nav\.css\?v=clui117/);
  assert.doesNotMatch(indexHtml, /site-nav\.css\?v=clui62/);
  assert.match(indexHtml, /assets\/site-nav\.js\?v=clui41/);
  assert.match(indexHtml, /assets\/app\.js\?v=clui143/);
  assert.match(indexHtml, /assets\/app\.css\?v=clui143/);
  assert.doesNotMatch(indexHtml, /clui29/);
});

test('CL-UI-116: every shell-page header carries the CL-APP-05 brand SVG (emoji retired)', () => {
  const pages = { 'index.html': indexHtml, 'weather-map.html': wgHtml, 'genre-eval.html': genreHtml,
    'field-intake.html': fieldHtml, 'reminders.html': remHtml, 'sources.html': sourcesHtml };
  for (const [page, html] of Object.entries(pages)) {
    const nav = navBlock(html);
    assert.match(nav, /<a class="site-nav-brand" href="\.\/index\.html"><img class="site-nav-logo" src="\.\/assets\/brand\/brand-512\.svg" alt="" width="24" height="24"> ChaseLights<\/a>/,
      `${page} brand link uses the brand SVG next to the wordmark`);
    assert.doesNotMatch(nav, /📸/, `${page} nav no longer carries the camera emoji`);
    // Cache-bust: the masthead assets ride the same generation on every page.
    assert.match(html, /site-nav\.css\?v=clui117/, `${page} site-nav.css stamp bumped`);
    assert.match(html, /member-auth\.js\?v=clui117/, `${page} member-auth.js stamp bumped`);
  }
  assert.ok(navCss.includes('.site-nav-logo {'), 'site-nav.css ships the logo sizing rule');
  assert.match(navCss, /\.site-nav-logo \{\s*\n\s*width: 24px;\s*\n\s*height: 24px;/,
    'logo renders ~24px tall, vertically centered by the inline-flex brand link');
  // APP shell (the Capacitor WebView loads apps/web-v2): the masthead brand
  // mark drops the ◉ placeholder and shows the same 案5 artwork, embedded as
  // a styles.css data-URI so the offline www fallback still renders it.
  const shellHtml = read('apps/web-v2/index.html');
  const shellCss = read('apps/web-v2/styles.css');
  assert.doesNotMatch(shellHtml, /brand-mark[^>]*>◉/, 'APP shell top drops the ◉ placeholder');
  assert.match(shellHtml, /<span class="brand-mark" aria-hidden="true"><\/span>/);
  assert.match(shellHtml, /styles\.css\?v=clui117/, 'APP shell styles.css cache-busted');
  assert.match(shellCss, /\.brand-mark\{width:34px;height:34px;display:block;border-radius:8px;background:url\("data:image\/svg\+xml,/,
    'APP shell brand mark paints the brand SVG at 34px');
  assert.match(shellCss, /\.brand-mark\{width:24px;height:24px\}/, 'mobile brand mark scales to 24px');
  assert.ok(shellCss.includes('%3Csvg'), 'styles.css embeds the brand SVG data URI');
});

test('CL-UI-28 (10): weather-map.js stamp bumped in weather-map.html (same commit)', () => {
  assert.match(wgHtml, /assets\/weather-map\.js\?v=bclwg53/);
  assert.doesNotMatch(wgHtml, /bclwg23|bclwg24/);
});