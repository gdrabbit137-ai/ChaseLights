// CL-UX-02: 我的頁 UI 精修（mobile）
//
// Source-contract test for the owner's real-device review:
//   · 星期選擇器 = 單行 7 顆等寬膠囊（無勾勾方框、無 5+2 折行），
//     亮綠填滿＝選中／暗框＝未選。
//   · 目標出景日預設「不限星期」，星期列只在「只篩選」時展開。
//   · 預報展望天數 = 1/3/5/7 四顆膠囊，不再叫系統下拉選單。
//   · 「我的提醒」移到「預設提醒規則」上方；預設規則預設收合為
//     摘要列＋「修改預設」，點擊才展開完整面板。
//   · 規則卡片移除舊版「提前 N 小時」截斷字樣，只留排程觸發摘要。
//   · 手機頂部安全區域：env(safe-area-inset-top) 內距＋遮罩。
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(import.meta.url);
const fs = require('node:fs');

const ROOT = path.join(path.dirname(require.resolve('../../../assets/reminders-page.js')), '..');
const HTML = fs.readFileSync(path.join(ROOT, 'reminders.html'), 'utf8');
const PAGE_JS = fs.readFileSync(path.join(ROOT, 'assets/reminders-page.js'), 'utf8');

// ---------------------------------------------------------------------------
// 1. Page order: tracked list first, defaults underneath
// ---------------------------------------------------------------------------
test('CL-UX-02 (1): 我的提醒 renders above 預設提醒規則', () => {
  const listAt = HTML.indexOf('id="rem-list-panel"');
  const defAt = HTML.indexOf('id="rem-def-panel"');
  assert.ok(listAt > 0 && defAt > 0, 'both panels exist');
  assert.ok(listAt < defAt, 'the tracked list comes first');
});

// ---------------------------------------------------------------------------
// 2. Weekday selector: one row of seven equal capsules
// ---------------------------------------------------------------------------
test('CL-UX-02 (2): weekday selector is a 7-column capsule row, not a boxed checkbox', () => {
  assert.match(HTML, /\.rem-def-wds\{display:grid;grid-template-columns:repeat\(7,minmax\(0,1fr\)\)/,
    'seven equal columns in one row');
  assert.match(HTML, /\.rem-def-wd\{[^}]*border-radius:999px/,
    'capsule shape');
  assert.match(HTML, /\.rem-def-wd input\{[^}]*opacity:0/, 'checkbox glyph is visually hidden');
  assert.match(HTML, /\.rem-def-wd:has\(input:checked\)\{background:var\(--cl-green\)/,
    'selected = bright green fill');
  assert.match(HTML, /\.rem-def-wd\{[^}]*border:1px solid var\(--cl-border-strong\)/,
    'unselected = dark outline');
  // no tick glyph inside the weekday capsules
  const wdBlock = HTML.slice(HTML.indexOf('id="rem-def-wd-group"'), HTML.indexOf('id="rem-def-twd-group"'));
  assert.ok(!/✓|✔|&#10003;/.test(wdBlock), 'no checkmark glyph in the weekday row');
  assert.equal((wdBlock.match(/class="rem-wd-t"/g) || []).length, 7, 'seven weekday labels');
});

// ---------------------------------------------------------------------------
// 3. Target day: default any, row only expands for 只篩選
// ---------------------------------------------------------------------------
test('CL-UX-02 (3): 目標出景日 defaults to 不限星期 and the row is collapsed until 只篩選', () => {
  assert.match(HTML, /data-f="target_mode" data-v="any" value="any" checked/,
    '不限星期 is the default');
  assert.match(HTML, /id="rem-def-twd-group" data-wd-group="twd" hidden/,
    'target weekday row starts collapsed');
  assert.match(PAGE_JS, /var twdGroup = root\.querySelector\('\[data-wd-group="twd"\]'\)/,
    'syncModes owns the target row');
  assert.match(PAGE_JS, /twdGroup\.hidden = !only/,
    'row visibility follows the mode');
});

// ---------------------------------------------------------------------------
// 4. Look-ahead: quick capsules 1 / 3 / 5 / 7
// ---------------------------------------------------------------------------
test('CL-UX-02 (4): 預報展望天數 is four quick capsules, no system dropdown', () => {
  const leads = HTML.match(/type="radio"[^>]*data-f="lead" value="[0-9]+"/g) || [];
  assert.deepEqual(leads.map((s) => s.match(/value="(\d+)"/)[1]), ['1', '3', '5', '7'],
    '1 / 3 / 5 / 7 capsules');
  assert.ok(!/<select[^>]*data-f="lead"/.test(HTML), 'no <select> for the look-ahead');
  assert.match(HTML, /\.rem-def-leads\{display:grid;grid-template-columns:repeat\(4,minmax\(0,1fr\)\)/,
    'one row of four equal capsules');
  // the hidden input keeps non-preset values round-trippable
  assert.match(HTML, /type="hidden"[^>]*id="rem-def-lead"[^>]*data-f="lead"/,
    'hidden value store');
  assert.match(PAGE_JS, /function readLead\(root\)/, 'readLead helper');
  assert.match(PAGE_JS, /lead_days: clampInt\(readLead\(root\), 1, 7, 3\)/,
    'readSchedule reads the capsule group');
});

// ---------------------------------------------------------------------------
// 5. Defaults panel collapses to summary + 修改預設
// ---------------------------------------------------------------------------
test('CL-UX-02 (5): 預設提醒規則 collapses to a summary row + 修改預設', () => {
  assert.match(HTML, /id="rem-def-body" hidden/, 'full panel starts collapsed');
  assert.match(HTML, /id="rem-def-toggle"[^>]*aria-expanded="false"/, 'toggle starts collapsed');
  const summaryAt = HTML.indexOf('id="rem-def-summary"');
  const bodyAt = HTML.indexOf('id="rem-def-body"');
  assert.ok(summaryAt > 0 && summaryAt < bodyAt, 'summary row stays visible above the hidden body');
  assert.match(PAGE_JS, /body\.hidden = !opening/, 'toggle flips the panel');
  assert.match(PAGE_JS, /setText\('rem-def-toggle', 'rem_def_modify'\)/, 'toggle label is localised');
});

// ---------------------------------------------------------------------------
// 6. Rule cards: no legacy truncated 「提前 …」 text
// ---------------------------------------------------------------------------
test('CL-UX-02 (6): rule cards drop the legacy 提前 fragment and keep the schedule summary', () => {
  const renderList = PAGE_JS.slice(PAGE_JS.indexOf('function renderList()'), PAGE_JS.indexOf('function renderLogin'));
  assert.ok(!renderList.includes('rem_col_advance'), 'no 提前 N 小時 on the card');
  assert.ok(renderList.includes('data-rem-sched-summary'), 'schedule trigger summary stays');
  assert.ok(renderList.includes('rem-sched-summary'), 'summary class present');
});

// ---------------------------------------------------------------------------
// 7. Top safe area
// ---------------------------------------------------------------------------
test('CL-UX-02 (7): top safe area padding + mask for iOS status bar', () => {
  assert.match(HTML, /\.rem-header\{padding-top:calc\([^}]*env\(safe-area-inset-top/,
    'header pads by the safe area');
  assert.match(HTML, /\.cl-safe-top-mask\{[^}]*height:env\(safe-area-inset-top/,
    'mask covers the status bar band');
  assert.match(HTML, /class="cl-safe-top-mask"/, 'mask element rendered');
});

// ---------------------------------------------------------------------------
// 8. i18n keys in all three dictionaries
// ---------------------------------------------------------------------------
function dictOf(src, lang) {
  const start = src.indexOf(`'${lang}': {`);
  assert.ok(start >= 0, `dictionary ${lang}`);
  const end = src.indexOf('\n    }', start);
  return src.slice(start, end);
}

test('CL-UX-02 (8): new keys exist in zh-TW / en / ja', () => {
  for (const lang of ['zh-TW', 'en', 'ja']) {
    const dict = dictOf(PAGE_JS, lang);
    for (const key of ['rem_def_modify', 'rem_def_lead_opt']) {
      assert.ok(new RegExp(`\\b${key}:`).test(dict), `${lang} missing ${key}`);
    }
  }
  assert.ok(dictOf(PAGE_JS, 'zh-TW').includes('修改預設'), 'zh-TW wording');
});
