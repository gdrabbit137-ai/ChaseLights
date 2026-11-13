// CL-UI-69: per-subject card rows (owner mockup). The card's summary area is
// a per-subject row list: each suitable subject of the selected date renders
// ONE line 「短名: HH:MM–HH:MM 🔔」 with the reminder bell at the line end
// (owner ruling: 🔔 only — ★ stays favorites-only; filled = set, hollow =
// not set). At most 3 rows + 「+N 題材」 fold; the honest tier line (○可拍 /
// ✗不宜·short word) covers the no-suitable days; the summary pills row adds
// elevation + current temp + sun azimuth/elevation; the bottom tool row keeps
// the 天氣預報/地圖/天氣圖 buttons. Source assertions + extracted pure
// helpers, per the established V1-shell test pattern.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const appCss = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');
const remHtml = readFileSync(join(ROOT, 'reminders.html'), 'utf8');
const remClient = readFileSync(join(ROOT, 'assets', 'reminders-client.js'), 'utf8');
const remPage = readFileSync(join(ROOT, 'assets', 'reminders-page.js'), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};
const createSpotCardBlock = grab('function createSpotCard', 'function distanceToSpotKm');
const i18nDict = grab('const i18nDict = {', 'const categoryKeys = {');

// ---- extracted pure helpers (real source, stubbed surroundings) ----
function makeRowHelpers() {
  let entries = grab('const scEntries=', 'const clSubjBell=');
  // The card source runs the builder as an IIFE over the in-scope scRow; the
  // extracted test wrapper takes the row as a parameter instead.
  entries = entries.replace('const scEntries=(()=>{', 'const scEntries=(scRow)=>(()=>{');
  assert.ok(entries.startsWith('const scEntries=(scRow)'), 'extraction rewrap applied');
  const rowHtml = grab('const clSubjectRowHtml=', 'const clSubjectExtra=');
  const fmt = grab('function formatHourSegments', 'function v2ContractThreshold');
  const prelude = `
    let currentLang='zh-TW';
    const i18nDict={'zh-TW':{clui69_more_subjects:'+{n} 題材',clui69_less:'收起'}};
    const d=()=>i18nDict[currentLang];
    const esc=s=>String(s);
    const colonSep=()=>currentLang==='en'?': ':'：';
    const listSep=()=>'、';
    const clSubjBell='<button type="button" class="cl-rem-btn cl-rem-compact" data-rem-place="tw-001"></button>';
    ${fmt}
  `;
  return new Function(
    prelude + entries + rowHtml +
    'return {scEntries,clSubjectRowHtml,formatHourSegments};')();
}

test('CL-UI-69 (1): per-subject rows replace the second-line chips when the layer is loaded', () => {
  // Rows come from the SAME subject-cards row the verdict consumes.
  assert.match(createSpotCardBlock, /const scRow=\(v2Evaluated&&v2Best\.day\)\?v2SubjectCardRow\(spot\.spot_id,v2Best\.day\.local_date\):null;/);
  // Row anatomy: 短名: HH:MM–HH:MM + line-end bell.
  assert.match(createSpotCardBlock, /class="cl-subject-rows"/);
  assert.match(createSpotCardBlock, /cl-subject-row\$\{hidden\?' cl-subject-extra':''\}/);
  assert.match(createSpotCardBlock, /<span class="cl-subject-name">\$\{esc\(entry\.name\)\}<\/span><span class="cl-subject-colon">\$\{colonSep\(\)\}<\/span><span class="cl-subject-window">\$\{esc\(formatHourSegments\(entry\.window\)\)\}<\/span>\$\{clSubjBell\}<\/div>/);
  // Compact bell mount point: the client (notify_rules contract) owns state.
  assert.match(createSpotCardBlock, /class="cl-rem-btn cl-rem-compact" data-rem-place="\$\{esc\(spot\.spot_id\)\}" data-rem-compact="1"/);
  // At most 3 visible rows + +N fold; extras start hidden.
  assert.match(createSpotCardBlock, /clSubjectExtra=scEntries\.slice\(3\)/);
  assert.match(createSpotCardBlock, /scEntries\.slice\(0,3\)\.map/);
  assert.match(createSpotCardBlock, /data-sc-more aria-expanded="false"/);
  assert.match(createSpotCardBlock, /clui69_more_subjects\.replace\('\{n\}',clSubjectExtra\.length\)/);
  // The fold toggle never opens the place modal.
  assert.match(createSpotCardBlock, /scMoreBtn\.onclick=e=>\{e\.stopPropagation\(\);/);
  assert.match(createSpotCardBlock, /card\.onclick=e=>\{if\(e\.target\.closest&&e\.target\.closest\('a,button,input,select,summary'\)\)return;openPlaceModal\(spot,metric\);\};/);
  // The row summary wins over the fallback lines when the layer is loaded.
  // CL-UI-71: the fallback is the SAME row format (clFallbackRows), never the
  // retired CL-UI-63 second line.
  assert.match(createSpotCardBlock, /class="shooting-summary">\$\{clSummaryHtml\|\|clFallbackRows\|\|v2Summary\|\|/);
  assert.match(createSpotCardBlock, /const clFallbackRows=/);
  // Degraded path (subject-cards file unavailable) keeps a tier line.
  assert.match(createSpotCardBlock, /card-second-line/);
});

test('CL-UI-69 (2): dedupe by trilingual name, union windows, fold past 3', () => {
  const h = makeRowHelpers();
  const dupRow = {suitable: [
    {subject_short: {'zh-TW': '山景', en: 'Mountain view', ja: '山景'}, window: ['05:35', '06:00']},
    {subject_short: {'zh-TW': '山景', en: 'Mountain view', ja: '山景'}, window: ['07:00']},
    {subject_short: {'zh-TW': '日落', en: 'Sunset', ja: '夕景'}, window: ['17:00']},
  ]};
  const entries = h.scEntries(dupRow);
  assert.equal(entries.length, 2, 'same-genre duplicates collapse to one line');
  assert.deepEqual(entries[0].window, ['05:35', '06:00', '07:00'], 'windows union, insertion order kept');
  assert.equal(entries[0].name, '山景');
  // Row HTML: name, colon, compressed window, one compact bell per line.
  const row = h.clSubjectRowHtml(entries[0], false);
  assert.ok(row.includes('山景') && row.includes('：') && row.includes('05:35–07:00'), row);
  assert.ok(row.includes('cl-rem-compact') && row.includes('data-rem-place'), row);
  // Fold: entries pass through untouched; the render slices are asserted on
  // the source — exercise the fold decision here.
  const all = Array.from({length: 6}, (_, i) =>
    h.scEntries({suitable: [{subject_short: {'zh-TW': '題材' + i}, window: ['06:00']}]})[0]);
  assert.equal(all.length, 6);
  assert.equal(all.slice(3).length, 3, 'three rows fold behind +N');
});

test('CL-UI-69 (3): no-suitable days stay honest — tier lines, never sentences', () => {
  // The fallback second line keeps the three-tier glyphs (○可拍 / ✗不宜).
  assert.match(createSpotCardBlock, /v2_tier_shootable/);
  assert.match(createSpotCardBlock, /v2_tier_not_recommended/);
  assert.match(createSpotCardBlock, /card_line_bad/);
  // i18n copy is short and sentence-free.
  for (const m of i18nDict.matchAll(/clui69_more_subjects:'([^']*)',clui69_less:'([^']*)'/g)) {
    for (const w of [m[1], m[2]]) assert.ok(!/[，。！？、]/.test(w), w);
  }
  assert.deepEqual([...i18nDict.matchAll(/clui69_more_subjects:'([^']*)'/g)].map(m => m[1]),
    ['+{n} 題材', '+{n} more', '+{n} 題材']);
  assert.deepEqual([...i18nDict.matchAll(/clui69_less:'([^']*)'/g)].map(m => m[1]),
    ['收起', 'Less', '折りたたむ']);
});

test('CL-UI-69 (4): summary pills — elevation + current temp + sun azimuth/elevation', () => {
  assert.match(createSpotCardBlock, /const clElevPill=clElev!=null\?`<span class="metric-chip">⛰ \$\{clElev\} m<\/span>`:''/);
  assert.match(createSpotCardBlock, /clElev=\(spot\.elevation!=null\)\?spot\.elevation:\(spot\.api_elevation!=null\?spot\.api_elevation:null\)/);
  assert.match(createSpotCardBlock, /<span class="metric-chip">⛰ \$\{clElev\} m<\/span>/);
  // Sun pill is field-driven: rendered only when BOTH angles exist, omitted
  // honestly otherwise (the daily snapshot carries the per-hour fields).
  assert.match(createSpotCardBlock, /clSunPill=\(metric&&metric\.sun_azimuth!=null&&metric\.sun_elevation!=null\)\?`<span class="metric-chip">☀ \$\{Math\.round\(metric\.sun_azimuth\)\}°\/\$\{Math\.round\(metric\.sun_elevation\)\}°<\/span>`:''/);
  // Pills lead the chip row, before the existing cloud/temp chips.
  assert.match(createSpotCardBlock, /card-metric-chips">\$\{clElevPill\}\$\{clSunPill\}\$\{compactMetrics\}\$\{distanceChip\}/);
});

test('CL-UI-69 (5): the reminder icon is 🔔 only (owner ruling) — compact toggle in the client', () => {
  // Compact buttons render the bell glyph only; ★ never appears in reminder
  // copy (it is reserved for favorites).
  assert.match(remClient, /var compact = btn\.getAttribute\('data-rem-compact'\) === '1';/);
  assert.match(remClient, /btn\.textContent = compact \? '🔔' : \(added \? t\('rem_added'\) : t\('rem_add'\)\);/);
  assert.ok(!remClient.match(/textContent = compact.*$/m)[0].includes('★'), 'compact glyph is the bell, never the favorites star');
  assert.match(remClient, /btn\.classList\.toggle\('cl-rem-on', added\);/);
  // CSS: hollow (desaturated) when off, filled + highlight when on.
  assert.match(appCss, /\.cl-rem-btn\.cl-rem-compact\{margin-left:auto;gap:0;padding:3px 7px;min-height:26px/);
  assert.match(appCss, /\.cl-rem-btn\.cl-rem-compact:not\(\.cl-rem-on\)\{filter:grayscale\(1\);opacity:\.5\}/);
  assert.match(appCss, /\.cl-rem-btn\.cl-rem-compact\.cl-rem-on\{background:rgba\(63,185,80,\.16\)\}/);
  // Reminders list name (owner ruling): 提醒清單 / Reminders / リマインダー.
  assert.deepEqual([...remPage.matchAll(/page_title: '([^']*)'/g)].map(m => m[1]),
    ['提醒清單', 'Reminders', 'リマインダー']);
  assert.match(remHtml, /<title>ChaseLights — 提醒清單<\/title>/);
});

test('CL-UI-69 (6): 390px row rules ship and the page serves the bumped stamps', () => {
  assert.match(appCss, /@media \(max-width:390px\)\{\n  \.cl-subject-row\{font-size:\.74rem\}/);
  assert.match(indexSource, /assets\/app\.js\?v=clui84/);
  assert.match(indexSource, /assets\/app\.css\?v=clui84/);
  assert.match(indexSource, /assets\/reminders-client\.js\?v=clui83/);
  assert.match(remHtml, /assets\/reminders-page\.js\?v=clui75/);
});
