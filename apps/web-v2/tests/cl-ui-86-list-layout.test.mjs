// CL-UI-86: card list page layout redo (mockup-first construction, Stage 2a).
// Spec source: origin/task/DESIGN-3 head 3d455f121 —
// data/v2/audits/design-mockups/mockup-cards.html, implemented verbatim
// (RD does not redesign). Tokens are the Stage 1 --cl-* layer (CL-UI-85).
// Scope: the homepage LIST only — date pill (two-segment, CL-UI-81 anatomy),
// tier segmented control dual encoding, subject chips (single-line scroll +
// fade mask), card anatomy (head = name 14/600 + tier badge + ★; region gray
// line; per-subject rows with a leading green dot and mono window; env pills;
// three equal bottom buttons), 460-card content-visibility virtualization,
// and the 3-column / ≤768px single-column list grid. Cache-first filter bar
// (CL-UI-84) behavior is untouched.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const cssSource = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');

const cssBlock = (sel) => {
  const i = cssSource.indexOf(sel);
  assert.ok(i >= 0, 'missing css selector ' + sel);
  return cssSource.slice(i, cssSource.indexOf('}', i));
};
const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'missing source slice start ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};
const createSpotCardBlock = grab('function createSpotCard', 'function distanceToSpotKm');

// ---- (1) 460-card performance: content-visibility virtualization verbatim ----
test('CL-UI-86 (1): cards carry content-visibility:auto + contain-intrinsic-size (mockup 460-card scheme)', () => {
  const card = cssBlock('.card {');
  assert.match(card, /content-visibility:\s*auto/);
  assert.match(card, /contain-intrinsic-size:\s*auto\s*190px/);
  // Grid: 3 columns at the mockup's 1280 shell; ≤768px collapses to one
  // column with the compact 8px gutter.
  const container = cssBlock('.container {');
  assert.match(container, /grid-template-columns:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\)/);
  assert.match(container, /max-width:\s*1280px/);
  assert.match(container, /gap:\s*var\(--cl-sp-5\)/);
  assert.match(cssSource, /@media \(max-width: 768px\) \{[^{]*\.container,[^{]*\.deferred-grid \{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/s);
});

// ---- (2) card head: 名稱 14/600 + tier badge + ★ ----
test('CL-UI-86 (2): card head renders name 14/600 ellipsis + tier badge + bare star', () => {
  assert.match(createSpotCardBlock, /<span class="tier tier-\$\{clBadgeTier\}">\$\{esc\(clBadgeLabel\)\}<\/span><button class="fav-btn/);
  // The badge shares the tier adapter's three-level state + the honest 資料不足.
  assert.match(createSpotCardBlock, /clBadgeTier=\(\(\)=>\{if\(!v2Evaluated\)return 'defer';if\(scTier\)return\(\{recommend:'rec',shootable:'shoot',not_recommended:'no'\}\)\[scTier\];if\(v2Best\.state==='GUIDANCE_SATISFIED'\)return 'rec';return v2Best\.state==='NOT_EVALUABLE'\?'defer':'no';\}\)\(\);/);
  assert.match(createSpotCardBlock, /clBadgeLabel=\{rec:d\(\)\.tier_recommend,shoot:d\(\)\.tier_shootable,no:d\(\)\.tier_not_recommended,defer:d\(\)\.eval2_unk\}\[clBadgeTier\];/);
  // Badge classes map to the CL-UI-85 shared tier components (all three + grey).
  assert.match(cssSource, /\.tier-rec\{[^}]*var\(--cl-green-text\)/);
  assert.match(cssSource, /\.tier-shoot\{[^}]*var\(--cl-amber-text\)/);
  assert.match(cssSource, /\.tier-no\{[^}]*var\(--cl-red-text\)/);
  assert.match(cssSource, /\.tier-defer\{[^}]*var\(--cl-grey-text\)/);
  // Name: 14px / 600 / single-line ellipsis scan; star = bare glyph, amber fav.
  const name = cssBlock('.spot-name {');
  assert.match(name, /font-size:\s*var\(--cl-fs-14\)/);
  assert.match(name, /font-weight:\s*600/);
  assert.match(name, /text-overflow:\s*ellipsis/);
  const fav = cssBlock('.fav-btn {');
  assert.match(fav, /border:\s*none/);
  assert.match(cssSource, /\.fav-btn\.active \{ color:var\(--cl-amber\); \}/);
});

// ---- (3) region gray line + 屬性灰字 (env-type) ----
test('CL-UI-86 (3): region line is plain gray text; env-type stays plain text under it', () => {
  const tag = cssBlock('.category-tag {');
  assert.match(tag, /color:\s*var\(--cl-text-3\)/);
  assert.match(tag, /background:\s*transparent/);
  assert.doesNotMatch(tag, /border:\s*1px/);
  // CL-UI-77 guard intact: env-type stays frameless plain gray text.
  const env = cssSource.match(/\.env-type-text \{[^}]*\}/)[0];
  assert.match(env, /color:var\(--cl-text-3\)/);
});

// ---- (4) per-subject rows: dot + 600 short name + mono window + bell ----
test('CL-UI-86 (4): subject rows get the mockup scan-line anatomy (green dot, mono window, no box)', () => {
  const rows = cssBlock('.cl-subject-rows{');
  assert.doesNotMatch(rows, /border/);
  assert.doesNotMatch(rows, /background/);
  const row = cssBlock('.cl-subject-row{');
  assert.match(row, /height:\s*26px/);
  assert.match(row, /font-size:\s*var\(--cl-fs-13\)/);
  // Leading green dot carries the semantics (mockup .subj-row .dot).
  const dot = cssBlock('.cl-subject-row::before{');
  assert.match(dot, /background:\s*var\(--cl-green\)/);
  assert.match(cssSource, /\.cl-subject-name\{color:var\(--cl-text-1\);font-weight:600/);
  const win = cssBlock('.cl-subject-window{');
  assert.match(win, /font-family:\s*var\(--cl-mono\)/);
  assert.match(win, /color:\s*var\(--cl-text-2\)/);
  assert.doesNotMatch(win, /var\(--cl-blue\)/);
  // The pinned render expression (CL-UI-69 anatomy) is untouched.
  assert.match(createSpotCardBlock, /<span class="cl-subject-name">\$\{esc\(entry\.name\)\}<\/span><span class="cl-subject-colon">\$\{colonSep\(\)\}<\/span><span class="cl-subject-window">/);
});

// ---- (5) env pills + three equal bottom buttons ----
test('CL-UI-86 (5): pills are 22px bg-2 surfaces; the three tool buttons stretch 30px above a solid rule', () => {
  const pill = cssBlock('.metric-chip {');
  assert.match(pill, /height:\s*22px/);
  assert.match(pill, /background:\s*var\(--cl-bg-2\)/);
  assert.match(pill, /border-radius:\s*var\(--cl-r-xs\)/);
  assert.match(pill, /font-size:\s*var\(--cl-fs-12\)/);
  const toolsBlock = (() => {
    // Several .card-footer-tools blocks exist (mobile/base/density); assert on
    // the base block that carries the CL-UI-86 rule.
    const i = cssSource.indexOf('CL-UI-86 (mockup-cards .acts)');
    assert.ok(i >= 0, 'missing CL-UI-86 tools rule');
    return cssSource.slice(i, cssSource.indexOf('}', i));
  })();
  assert.match(toolsBlock, /border-top:\s*1px solid var\(--cl-border\)/);
  assert.match(toolsBlock, /margin-top:\s*auto/);
  const btn = cssBlock('.tool-link {');
  assert.match(btn, /height:\s*30px/);
  assert.match(btn, /flex:\s*1 1 0/);
  assert.match(btn, /background:\s*var\(--cl-bg-2\)/);
  assert.match(btn, /color:\s*var\(--cl-text-2\)/);
  // Hover follows the mockup .btn contract — never the link blue.
  assert.match(cssSource, /\.tool-link:hover \{ background:var\(--cl-bg-3\); border-color:var\(--cl-border-strong\); color:var\(--cl-text-1\); \}/);
});

// ---- (6) tier segmented control + subject chips ----
test('CL-UI-86 (6): tier tabs dual-encoded per tier; chips 24px single-line scroll with fade mask', () => {
  const tab = cssBlock('.tier-tab {');
  assert.match(tab, /background:\s*var\(--cl-bg-2\)/);
  assert.match(cssSource, /\.tier-tab\.active \{ background: var\(--cl-bg-3\); color: var\(--cl-text-1\); border: 1\.5px solid var\(--cl-border-strong\); font-weight: 600; \}/);
  for (const [tier, color] of [['recommend', '--cl-green-text'], ['shootable', '--cl-amber-text'], ['not_recommended', '--cl-red-text']]) {
    assert.match(cssSource, new RegExp(`\\.tier-tab\\[data-tier="${tier}"\\]\\.active \\{ border-color: var\\(${color === '--cl-green-text' ? '--cl-green-border' : color === '--cl-amber-text' ? '--cl-amber-border' : '--cl-red-border'}\\); color: var\\(${color}\\); \\}`));
  }
  // Count = mono second gray layer; selected count takes the tier color.
  const count = cssBlock('.tier-tab-count {');
  assert.match(count, /font-family:\s*var\(--cl-mono\)/);
  assert.match(count, /color:\s*var\(--cl-text-3\)/);
  // The 🌐 mark renders on the 全部 tab in BOTH paint paths (live + cached).
  const live = grab('function renderTierTabs', 'function renderSubjectChips');
  const cached = grab('function clui84RenderTabsFromCounts', 'function restoreFilterBarFromCache');
  for (const fn of [live, cached]) {
    assert.match(fn, /labelKey==='tier_all'\?'🌐 ':''/);
  }
  const chip = cssBlock('.subject-chip {');
  assert.match(chip, /height:\s*var\(--cl-chip-h\)/);
  assert.match(chip, /scroll-snap-align:\s*start/);
  // Two .subject-chip-strip blocks exist (base geometry + the CL-UI-86 snap/
  // mask composition) — assert the composition block.
  const stripFirst = cssSource.indexOf('.subject-chip-strip {');
  const strip = cssSource.slice(cssSource.indexOf('.subject-chip-strip {', stripFirst + 1),
    cssSource.indexOf('}', cssSource.indexOf('.subject-chip-strip {', stripFirst + 1)));
  assert.match(strip, /scroll-snap-type:\s*x proximity/);
  assert.match(strip, /mask-image:\s*linear-gradient\(90deg,\s*var\(--cl-ink\) calc\(100% - 24px\), transparent\)/);
});

// ---- (7) title row baseline (P3-1) + date pill family ----
test('CL-UI-86 (7): title 16/600 with the count on the same baseline; date pill keeps the 176/48 two-segment anatomy', () => {
  const title = cssBlock('.discovery-title {');
  assert.match(title, /font-size:\s*var\(--cl-fs-16\)/);
  assert.match(title, /font-weight:\s*600/);
  const count = cssBlock('.rank-summary {');
  assert.match(count, /font-size:\s*var\(--cl-fs-13\)/);
  assert.match(count, /color:\s*var\(--cl-text-3\)/);
  const pill = cssBlock('.day-picker-trigger {');
  assert.match(pill, /min-width:\s*176px;/);
  assert.match(pill, /min-height:\s*48px;/);
  assert.match(pill, /border-radius:\s*var\(--cl-r-sm\);/);
  const main = cssBlock('.day-picker-main {');
  assert.match(main, /white-space:\s*nowrap/);
});

// ---- (8) body scan list: the blue callout box is retired ----
test('CL-UI-86 (8): shooting-summary drops the blue left-border box', () => {
  const sum = cssBlock('.shooting-summary {');
  assert.doesNotMatch(sum, /var\(--cl-blue\)/);
  assert.match(sum, /background:\s*transparent/);
});

// ---- (9) cache-first render path untouched; stamp bumped ----
test('CL-UI-86 (9): CL-UI-84 cache-first wiring intact and cache-bust at clui95', () => {
  assert.ok(appSource.includes("if(!v2EvalBundle&&clui84FilterCache){"), 'failure branch keeps the cached bar');
  assert.ok(appSource.includes('clui84RenderTabsFromCounts(clui84FilterCache.tier_counts)'), 'cached counts repaint the tabs');
  assert.ok(appSource.includes('saveFilterCache(rowsAll);'), 'settled render persists the bar state');
  assert.equal((indexSource.match(/\?v=clui95/g) || []).length, 2, 'app.js + app.css both at clui95');
  assert.doesNotMatch(indexSource, /\?v=clui90\b/, 'old generation retired');
});
