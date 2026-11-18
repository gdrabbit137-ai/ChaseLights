// CL-UI-87: forecast-page layout redo (mockup-first construction, Stage 2b).
// Spec source: origin/task/DESIGN-3 head 3d455f121 —
// data/v2/audits/design-mockups/mockup-forecast.html, implemented verbatim
// (RD does not redesign). Tokens: the live --cl-* layer (CL-UI-85).
// Contract under test:
//  (1) 8-day date-groups: one <details class="day-group"> per local_date on
//      BOTH the desktop shell (#timeline-groups) and the mobile shell
//      (#timeline-mobile); the selected day opens by default, user-opened
//      groups persist across re-renders (clui87LastSelDate revert rule).
//  (2) 24h mini color band (mockup n3b / DR1 P3-2) over the selected day,
//      best hours carrying the white inset frame via --cl-white.
//  (3) Desktop per-group table = mockup 5 columns 時刻|狀態|適合題材|口語化氣象|⋯
//      with 40px rows and the mono 時刻 anchor column (n1b, DR1 P2-9); raw
//      values live ONLY in the expandable kv row (n2c), toggled by the ⋯
//      button with the open state captured across re-renders.
//  (4) na hours (subject-cards 'outside' bucket) collapse into ONE
//      「時段外」 line per group (n1c) — they never emit a desktop row; the
//      mobile shell keeps the mockup's minimal na card.
//  (5) Painter compatibility: the status cell keeps index 1 and the honest
//      資料不足 placeholder (CL-UI-43), painted by decorateWeatherTimeline
//      against the new #timeline-groups host (legacy #timeline-body fallback).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const cssSource = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');

const grab = (start, end) => {
  const a = appSource.indexOf(start);
  assert.ok(a >= 0, 'missing source slice: ' + start);
  return appSource.slice(a, appSource.indexOf(end, a));
};
const block = (start, end) => {
  const a = appSource.indexOf(start);
  assert.ok(a >= 0, 'missing source block: ' + start);
  return appSource.slice(a, appSource.indexOf(end, appSource.indexOf(start) + 1));
};

const hourLoop = grab('for(const item of wmList){', 'const naHtml=');
const groupLoop = grab('for(const [wmDate,wmList] of dayMap){', 'clui87LastSelDate=selectedDate;');
const captures = grab('const dgDesktopOpen=', 'let mobile=mobileRoot;');

// ---- (1) 8-day date-groups on both shells ----
test('CL-UI-87 (1): one day-group <details> per local_date, selected day opens by default', () => {
  // desktop shell + mobile shell both render the same group anatomy
  assert.ok(appSource.includes("mobileDet.className='day-group';mobileDet.dataset.date=wmDate"), 'mobile group keyed by date');
  assert.ok(appSource.includes("det.className='day-group';det.dataset.date=wmDate"), 'desktop group keyed by date');
  assert.ok(appSource.includes("groupsEl.appendChild(det)"), 'desktop groups appended to #timeline-groups');
  assert.ok(appSource.includes("mobileRoot.appendChild(mobileDet)"), 'mobile groups appended to #timeline-mobile');
  // open rule: selected date always open + user-opened groups persist
  const openRule = groupLoop.slice(groupLoop.indexOf('const open='), groupLoop.indexOf('// mockup n1a'));
  assert.match(openRule, /wmDate===selectedDate/, 'selected day opens by default');
  assert.match(openRule, /dgUserOpen\.has\(wmDate\)/, 'user-opened groups persist');
  // revert rule: the previously default-open day is excluded from the
  // persistence set so only the CURRENT selected day opens by default
  assert.match(captures, /filter\(dt=>dt!==clui87LastSelDate\)/, 'previous default-open day reverts');
  assert.ok(appSource.includes('let clui87LastSelDate=null;'), 'module-level last-selected tracking');
  assert.ok(appSource.includes('clui87LastSelDate=selectedDate;'), 'last-selected updated after each render');
  // index.html carries the new shells
  assert.ok(indexSource.includes('<div class="timeline-band" id="timeline-band">'), 'band shell');
  assert.ok(indexSource.includes('<div id="timeline-groups">'), 'desktop groups shell');
  assert.ok(indexSource.includes('<div class="timeline-mobile" id="timeline-mobile">'), 'mobile shell (kept)');
});

// ---- (2) 24h mini color band ----
test('CL-UI-87 (2): 24h mini band over the selected day — semantic cells + best white frame', () => {
  const bandCode = grab('const bandRows=', 'const dayLabelOf=');
  assert.match(bandCode, /dayMap\.get\(selectedDate\)\|\|\[\]/, 'band reads the selected day only');
  // CL-UI-95: the cells/best-frame/band-label anatomy moved into the SHARED
  // v2BandHtml (the place-modal quick view renders the same builder), the
  // call site only feeds rows + the CL-UI-81 v2-effective best set.
  assert.match(bandCode, /bandEl\.innerHTML=bandRows\.length\?v2BandHtml\(bandRows,spot,v2WmHours\):''/, 'band built by the shared v2BandHtml');
  const bandFn = grab('function v2BandHtml', 'function v2QuickViewHtml');
  assert.match(bandFn, /class="\$\{cls\}\$\{best\}"/, 'per-hour semantic cell');
  assert.match(bandFn, /b\.kind==='fit'\?'rec':b\.kind==='general'\?'shoot':b\.kind==='fail'\?'no':'na'/, 'fit→green / general→amber / fail→grey / outside→dark');
  assert.match(bandFn, /bestSet&&bestSet\.size&&bestSet\.has\(item\.time\.slice\(-5\)\)\?' best':''/, 'best hours = the CL-UI-81 v2-effective set');
  assert.match(bandFn, /<span>00:00<\/span><span>06:00<\/span><span>12:00<\/span><span>18:00<\/span><span>23:00<\/span>/, 'mockup band-label stamps');
  const best = cssSource.match(/\.timeline-band \.band i\.best \{[^}]*\}/);
  assert.match(best[0], /inset 0 0 0 1\.5px var\(--cl-white\)/, 'white inset frame via token');
  const band = cssSource.match(/\.timeline-band \.band \{[^}]*\}/);
  assert.match(band[0], /height: 16px;/, '16px band (mockup n3b)');
});

// ---- (3) desktop table anatomy ----
test('CL-UI-87/94 (3): 4-column group table, 40px rows, mono 時間 anchor, plain-weather cell', () => {
  // per-group table header: 時間|適合題材|口語化氣象|⋯ (CL-UI-94: 狀態 retired)
  const headIdx = appSource.indexOf('<thead><tr><th>${esc(d().th_time)}</th>');
  const head = appSource.slice(headIdx, appSource.indexOf('</thead>', headIdx));
  const order = ['th_time', 'th_subjects', 'th_plain'];
  let pos = -1;
  for (const key of order) {
    const at = head.indexOf(key, pos + 1);
    assert.ok(at > pos, `${key} column in order`);
    pos = at;
  }
  assert.ok(!head.includes('th_status'), 'CL-UI-94: no 狀態 column');
  assert.ok(appSource.includes("th_plain:'口語化氣象'") && appSource.includes("th_plain:'Weather (plain)'") && appSource.includes("th_plain:'口語天気'"), 'th_plain trilingual');
  // row: mono 64px time cell + plain weather + ⋯ toggle button
  assert.match(hourLoop, /<td class="hr">\$\{esc\(hh\)\}/, 'hour-only mono time cell');
  assert.match(hourLoop, /<td class="wx">\$\{esc\(clui82PlainWeather\(item\)\)\|\|'—'\}<\/td>/, 'plain-language weather cell (live mapping)');
  assert.match(hourLoop, /class="clui87-more"/, '⋯ toggle button');
  // CSS: 40px rows, 64px mono anchor, anchor bolding reads the same bucket
  const td = cssSource.match(/#timeline-groups table\.hrs td \{[^}]*\}/);
  assert.match(td[0], /height: 40px;/, '40px row rhythm (mockup n1b)');
  const hr = cssSource.match(/#timeline-groups td\.hr \{[^}]*\}/);
  assert.match(hr[0], /font-family: var\(--cl-mono\);/);
  assert.match(hr[0], /width: 64px; min-width: 64px;/, 'mockup time-w');
  assert.match(cssSource, /#timeline-groups tr:has\(td\.td-subjects\.subj-has\) td\.hr,\n[^{]*#timeline-groups tr:has\(td\.td-subjects\.subj-ok-row\) td\.hr \{ color: var\(--cl-text-1\); font-weight: 600; \}/,
    'DR1 P2-9: the qualifying hour bolds its 時刻 anchor (same bucket as the chips)');
  const summary = cssSource.match(/details\.day-group > summary \{[^}]*\}/);
  assert.match(summary[0], /min-height: 44px;/, '44px group summary bar (mockup)');
});

// ---- (4) kv detail row (n2c) + open preservation ----
test('CL-UI-87 (4): raw values only in the expandable kv row; open state survives re-renders', () => {
  const kv = grab('const kvHtml=', 'let nowAnchorAssigned');
  for (const key of ['th_temp', 'th_wind', 'th_rh', 'th_clow', 'th_cmid', 'th_chigh', 'th_cloud_base', 'th_vis', 'th_astro']) {
    assert.ok(kv.includes('${esc(d().' + key + ')}'), `kv item ${key}`);
  }
  assert.match(kv, /\$\{astro\|\|astroMissingHtml\(item,true\)\}/, 'astro keeps the honest per-hour missing reason (CL-UI-14)');
  // the row is emitted hidden unless it was open pre-wipe; the ⋯ handler flips
  // the hidden attribute (guarded by an explicit display rule, CL-UI-47-safe)
  assert.match(hourLoop, /class="detail" data-h="\$\{esc\(detKey\)\}"\$\{detOpen\?'':' hidden'\}/, 'kv row hidden until opened');
  assert.match(cssSource, /#timeline-groups tr\.detail\[hidden\] \{ display: none; \}/, 'explicit hidden guard rule');
  assert.match(captures, /tr\.detail\[data-h\]:not\(\[hidden\]\)/, 'open kv rows captured before the wipe');
  const handler = grab('groupsEl.onclick=', 'clui87LastSelDate=selectedDate;');
  assert.match(handler, /det\.classList\.contains\('detail'\)/, 'toggle targets the detail row');
  assert.match(handler, /btn\.textContent=on\?'▴':'⋯'/, 'mockup glyph toggle');
  assert.match(handler, /btn\.setAttribute\('aria-expanded'/, 'aria-expanded synced');
});

// ---- (5) na collapse (n1c) ----
test('CL-UI-87 (5): 時段外 hours collapse into one line — never a per-hour row', () => {
  assert.match(hourLoop, /const isNa=subjCell\.kind==='outside';/, 'collapse source = the subject-cards na bucket');
  assert.match(hourLoop, /na\.push\(hh\)/, 'collapsed hours collected, no row emitted');
  const naCode = grab('const naHtml=', 'const det=document.createElement');
  assert.match(naCode, /na\.length\?`<tr class="na-row"><td colspan="4"><span>\$\{esc\(d\(\)\.state_outside\)\}<\/span> · <span class="mono">\$\{esc\(formatHourSegments\(na\)\)\}<\/span><\/td><\/tr>`:''/, 'one collapsed line with the compressed hour segments');
  assert.match(cssSource, /#timeline-groups tr\.na-row > td \{ height: 32px; color: var\(--cl-text-3\); font-size: var\(--cl-fs-12\); \}/, '32px honest grey line');
  // CL-UI-94: the mobile na card shows the neutral 🕒 word itself — no
  // 資料不足 status placeholder anywhere
  assert.match(hourLoop, /isNa\?`<span class="tm-subj-na">\$\{esc\(d\(\)\.state_outside\)\}<\/span>`:`<div class="tm-maincol">/, 'minimal na card on mobile');
  assert.match(hourLoop, /\$\{isNa\?'':`<details class="tm-details"/, 'na card carries no 詳細氣象');
});

// ---- (6) group summary: day label, tier chip, counts ----
test('CL-UI-87 (6): summary = day label · date + tier chip + ✓/○ counts + subject shorts', () => {
  const sum = grab('const dayLabelOf=', '// mockup n2c');
  assert.match(sum, /v2DayRel\(date,tz\)==='today'\)return d\(\)\.eval2_d0/, 'relative day word for day 0');
  assert.match(sum, /return wmDayBanner\(date\);/, 'page-header banner stamp beyond day 2');
  assert.match(sum, /esc\(shortDateStamp\(date\)\)/, 'MM/DD stamp (never raw ISO)');
  assert.match(sum, /recommend:`<span class="dg-chip dg-chip-rec">\$\{esc\(d\(\)\.v2_tier_recommend\)\}<\/span>`/, '✓ 推薦 chip');
  assert.match(sum, /shootable:`<span class="dg-chip dg-chip-shoot">\$\{esc\(d\(\)\.v2_tier_shootable\)\}<\/span>`/, '○ 可拍 chip');
  assert.match(sum, /not_recommended:`<span class="dg-chip dg-chip-no">\$\{esc\(d\(\)\.v2_tier_not_recommended\)\}<\/span>`/, '✗ 不宜 chip');
  assert.match(sum, /if\(!row\)return ''/, 'honest: no artifact row → no chip');
  assert.match(sum, /b\.kind==='fit'\)ok\+\+/, '✓ count from the same hourly buckets as the chips');
  assert.match(sum, /v2SubjectCardShorts\(/, 'subject shorts on the summary (mockup mini)');
  for (const cls of ['.dg-chip-rec', '.dg-chip-shoot', '.dg-chip-no']) {
    assert.ok(cssSource.includes(cls), `css has ${cls}`);
  }
});

// ---- (7) painter compatibility ----
test('CL-UI-94 (7): status column retired — no painter write path into the hourly table', () => {
  assert.ok(!hourLoop.includes('<td>${esc(d().eval2_unk)}</td>'), 'no status placeholder cell at index 1');
  const deco = grab('function decorateWeatherTimeline', 'function decorateV2Eval');
  assert.match(deco, /CL-UI-94/, 'retirement comment anchors the contract change');
  assert.match(deco, /return;\s*\n\s*\}/, 'the evaluations-details painter is a no-op');
  assert.ok(!deco.includes('cells[1]') && !deco.includes("querySelectorAll('#timeline-mobile [data-v2t]')"), 'no paint path on desktop or mobile');
});

// ---- (8) tokens + stamps ----
test('CL-UI-87 (8): --cl-* tokens only + clui102 stamps + scroll/probe compat', () => {
  const clui87css = cssSource.slice(cssSource.indexOf('===== CL-UI-87'), cssSource.indexOf('#timeline-mobile .tbl-390'));
  assert.doesNotMatch(clui87css.replace(/\/\*[^*]*\*\//g, ''), /#[0-9A-Fa-f]{3,8}\b/, 'no hardcoded hex in the new CSS (token layer only)');
  assert.equal((indexSource.match(/\?v=clui102/g) || []).length,3, 'app.css + feedback-ui stay at clui102; app.js advanced to clui112 (CL-UI-110)');
  // the now-anchor scroll keeps working against the new container
  const scroll = grab('function scrollWeatherModalToCurrent', '// ---- CL-UI-34');
  assert.match(scroll, /getElementById\('timeline-groups'\)/, 'desktop anchor lookup on the groups container');
  assert.match(scroll, /#timeline-groups thead/, 'sticky offset reads the group table header');
});
