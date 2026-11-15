// CL-UI-85: design-system token landing (mockup-first construction, Stage 1).
// Spec source: origin/task/DESIGN-3 head 3d455f121 —
// data/v2/audits/design-mockups/design-system.html, implemented verbatim
// (RD does not redesign). Stage 1 = --cl-* token layer + hardcoded-color
// zeroing + shared component base + the five empty-state components.
// Pure visual layer: no behavior/data logic changes; the three approved
// mockup faces (list / forecast / detail) keep their layout until Stage 2.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const cssSource = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');

const rootStart = cssSource.indexOf(':root {');
const rootEnd = cssSource.indexOf('\n    }', rootStart);
const rootBlock = cssSource.slice(rootStart, rootEnd);

// ---- (1) token layer: every spec token verbatim from design-system.html
const SPEC_TOKENS = {
  '--cl-bg-0': '#0B0F1A', '--cl-bg-1': '#111827', '--cl-bg-2': '#1A2332', '--cl-bg-3': '#232D3F',
  '--cl-border': '#2A3441', '--cl-border-strong': '#3B4757',
  '--cl-text-1': '#E6EBF2', '--cl-text-2': '#A8B3C2', '--cl-text-3': '#8B98A9',
  '--cl-green': '#22C55E', '--cl-green-text': '#4ADE80', '--cl-green-bg': 'rgba(34,197,94,.10)', '--cl-green-border': '#166534',
  '--cl-amber': '#F59E0B', '--cl-amber-text': '#FBBF24', '--cl-amber-bg': 'rgba(245,158,11,.10)', '--cl-amber-border': '#92600A',
  '--cl-red': '#EF4444', '--cl-red-text': '#F87171', '--cl-red-bg': 'rgba(239,68,68,.09)', '--cl-red-border': '#7F1D1D',
  '--cl-grey': '#6B7686', '--cl-grey-text': '#98A4B3', '--cl-grey-bg': 'rgba(107,118,134,.14)',
  '--cl-blue': '#3B82F6',
  '--cl-r-xs': '6px', '--cl-r-sm': '8px', '--cl-r-md': '12px', '--cl-r-lg': '16px',
  '--cl-sp-1': '4px', '--cl-sp-2': '8px', '--cl-sp-3': '12px', '--cl-sp-4': '16px', '--cl-sp-5': '24px', '--cl-sp-6': '32px',
  '--cl-fs-12': '12px', '--cl-fs-13': '13px', '--cl-fs-14': '14px', '--cl-fs-15': '15px', '--cl-fs-16': '16px', '--cl-fs-20': '20px',
  '--cl-control-h': '36px', '--cl-pill-h': '32px', '--cl-chip-h': '24px', '--cl-btn-h': '40px',
  '--cl-shadow-1': '0 1px 2px rgba(0,0,0,.4)',
  '--cl-shadow-2': '0 8px 24px rgba(0,0,0,.5)',
  '--cl-shadow-3': '0 16px 48px rgba(0,0,0,.65)',
  '--cl-font': '"Inter","Segoe UI","Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif',
  '--cl-mono': '"SF Mono",ui-monospace,"Cascadia Mono","Consolas",monospace',
};
test('CL-UI-85 (1) token layer matches design-system.html (DESIGN-4) verbatim', () => {
  for (const [k, v] of Object.entries(SPEC_TOKENS)) {
    assert.ok(rootBlock.includes(`${k}:${v}`), `token missing or off-value: ${k}:${v}`);
  }
});

// ---- (2) hardcoded colors: zero outside the token layer (comment-aware)
test('CL-UI-85 (2) zero hardcoded colors outside the :root token layer', () => {
  const noComments = cssSource.replace(/\/\*[\s\S]*?\*\//g, '');
  const bodyStart = noComments.indexOf('\n    }', noComments.indexOf(':root {'));
  const body = noComments.slice(bodyStart);
  assert.equal((body.match(/#[0-9A-Fa-f]{3,8}\b/g) || []).length, 0, 'hex colors outside :root');
  assert.equal((body.match(/rgba?\(\s*[-0-9.,%\s]+\)/g) || []).length, 0, 'rgba() outside :root');
  assert.equal((body.match(/(?:color|background|border-color|fill|stroke)\s*:\s*(?:white|black|gray|grey|red|green|blue|orange|yellow|purple|pink|cyan|magenta)\b/g) || []).length, 0, 'named colors outside :root');
});

// ---- (3) shared component base (§7 元件庫): pill / chip / tier / tab /
//         buttons 30·36·40 / accordion / select+input / switch — token-driven
test('CL-UI-85 (3) shared component base present, composed from tokens', () => {
  for (const sel of ['.pill{', '.pill b{', '.chip{', '.chip.on{', '.tier{', '.tier-rec{', '.tier-shoot{',
                     '.tier-no{', '.tier-defer{', '.tab{', '.tab.sel{', 'select.sel{', 'input.sel{',
                     '.btn{', '.btn:hover{', '.btn-ctl{', '.btn-lg{', '.btn-primary{', '.btn-danger{', '.btn-ghost{',
                     '.date-pill{', '.box{', 'details.acc{', 'details.acc summary::before{', '.switch{', '.switch.on{']) {
    assert.ok(cssSource.includes(sel), 'missing component rule ' + sel);
  }
  // size system: chip 24 / pill·tier 22 / controls 36 / secondary btn 30 / primary 40
  assert.match(cssSource, /\.chip\{[^}]*height:var\(--cl-chip-h\)/);
  assert.match(cssSource, /\.pill\{[^}]*height:22px/);
  assert.match(cssSource, /\.tier\{[^}]*height:22px/);
  assert.match(cssSource, /\.btn\{[^}]*height:30px/);
  assert.match(cssSource, /\.btn-ctl\{[^}]*height:var\(--cl-control-h\)/);
  assert.match(cssSource, /\.btn-lg\{[^}]*height:var\(--cl-btn-h\)/);
  assert.match(cssSource, /select\.sel\{[^}]*height:var\(--cl-control-h\)/);
  // semantic tiers carry the contract colors, never hue-only (icon+text in markup)
  assert.match(cssSource, /\.tier-rec\{[^}]*var\(--cl-green-text\)[^}]*var\(--cl-green-border\)/);
  assert.match(cssSource, /\.tier-shoot\{[^}]*var\(--cl-amber-text\)[^}]*var\(--cl-amber-border\)/);
  assert.match(cssSource, /\.tier-no\{[^}]*var\(--cl-red-text\)[^}]*var\(--cl-red-border\)/);
});

// ---- (4) empty-state components ×5 (§9) styled purely by tokens
test('CL-UI-85 (4) empty-state components styled by tokens', () => {
  for (const sel of ['.empty{', '.empty .ic{', '.empty .t{', '.empty .d{', '.empty .btn{',
                     '.empty .skel-lines{', '.skel{', '.skel-line{', '.offline-badge{', '@keyframes cl-sk{']) {
    assert.ok(cssSource.includes(sel), 'missing empty-state rule ' + sel);
  }
  assert.match(cssSource, /\.empty\{[^}]*border:1px dashed var\(--cl-border-strong\)/);
  assert.match(cssSource, /\.skel\{[^}]*var\(--cl-bg-2\)[^}]*var\(--cl-bg-3\)/);
  assert.match(cssSource, /\.offline-badge\{[^}]*var\(--cl-grey-bg\)[^}]*var\(--cl-grey-text\)/);
});

// ---- (5) render functions: clEmptyStateHtml covers the five states with
//         trilingual copy wired to the existing i18nDict
function extractFn(name) {
  const i = appSource.indexOf('function ' + name);
  assert.ok(i >= 0, 'missing function ' + name);
  let depth = 0;
  for (let k = i; k < appSource.length; k++) {
    if (appSource[k] === '{') depth++;
    else if (appSource[k] === '}') { depth--; if (depth === 0) return appSource.slice(i, k + 1); }
  }
  throw new Error('unbalanced function ' + name);
}
const clEmptyStateHtml = extractFn('clEmptyStateHtml');

const E_KEYS = ['e_fav_t', 'e_fav_d', 'e_fav_a', 'e_rem_t', 'e_rem_d', 'e_rem_a',
                'e_load_t', 'e_load_d', 'e_err_t', 'e_err_d', 'e_err_a',
                'e_off_t', 'e_off_badge', 'e_off_d', 'e_off_a'];
test('CL-UI-85 (5a) empty-state copy exists in all three dictionaries', () => {
  for (const key of E_KEYS) {
    const n = (appSource.match(new RegExp(key + ':', 'g')) || []).length;
    assert.equal(n, 3, `${key} must be defined in zh-TW/en/ja (found ${n})`);
  }
});

const DICT = {
  'zh-TW': {e_fav_t: '還沒有收藏', e_fav_d: '在卡片右上按 ★ 加入最愛，這裡會列出你追蹤的景點。', e_fav_a: '去逛卡片列表',
            e_rem_t: '還沒有提醒', e_rem_d: '選地區 → 景點 → 題材建立第一個拍攝提醒，符合時段前會通知你。', e_rem_a: '建立提醒',
            e_load_t: '載入中', e_load_d: 'skeleton 佔位（shimmer 是唯一裝飾動畫）',
            e_err_t: '暫時無法載入', e_err_d: '網路逾時（30s）。已自動重試 2 次 — 可再手動重試。', e_err_a: '↻ 重試',
            e_off_t: '離線中 — 顯示上次資料', e_off_badge: '離線 · 上次更新', e_off_d: '以下為最後一次成功載入的快照。', e_off_a: '重新連線'},
  'en': {e_fav_t: 'No favorites yet', e_fav_d: 'Tap ★ on a card to track it; tracked places list here.', e_fav_a: 'Browse cards',
         e_rem_t: 'No reminders yet', e_rem_d: 'Pick region → place → subject to create your first reminder.', e_rem_a: 'Create reminder',
         e_load_t: 'Loading', e_load_d: 'Skeleton placeholder (shimmer is the only decorative animation)',
         e_err_t: 'Could not load', e_err_d: 'Network timed out (30s). Auto-retried twice — retry manually if you like.', e_err_a: '↻ Retry',
         e_off_t: 'Offline — showing last data', e_off_badge: 'Offline · last update', e_off_d: 'Snapshot of the last successful load.', e_off_a: 'Reconnect'},
  'ja': {e_fav_t: 'お気に入りはまだありません', e_fav_d: 'カード右上の ★ で追跡するとここに並びます。', e_fav_a: 'カード一覧へ',
         e_rem_t: 'リマインドはまだありません', e_rem_d: '地域 → スポット → 題材を選んで最初のリマインドを作成。', e_rem_a: 'リマインド作成',
         e_load_t: '読み込み中', e_load_d: 'skeleton プレースホルダー（唯一の装飾アニメ）',
         e_err_t: '読み込めませんでした', e_err_d: 'ネットワークタイムアウト（30s）。自動再試行 2 回済み — 手動でも再試行できます。', e_err_a: '↻ 再試行',
         e_off_t: 'オフライン — 前回データを表示', e_off_badge: 'オフライン・最終更新', e_off_d: '最後に成功した読み込みのスナップショット。', e_off_a: '再接続'},
};
function render(kind, opts, lang) {
  const esc = (v) => String(v == null ? '' : v).replace(/[&<>"']/g, (ch) => (
    {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[ch]));
  const fn = new Function('d', 'esc', clEmptyStateHtml + '\nreturn clEmptyStateHtml;')(
    () => DICT[lang], esc);
  return fn(kind, opts);
}
test('CL-UI-85 (5b) clEmptyStateHtml renders the five standard states', () => {
  for (const lang of ['zh-TW', 'en', 'ja']) {
    const fav = render('favorites', {}, lang);
    assert.ok(fav.includes('class="empty"') && fav.includes('★'), lang);
    assert.ok(fav.includes(DICT[lang].e_fav_t) && fav.includes(DICT[lang].e_fav_d), lang);
    assert.ok(fav.includes('btn-ctl btn-primary'), lang + ' favorites action is primary');
    const rem = render('reminders', {}, lang);
    assert.ok(rem.includes('🔔') && rem.includes('btn-ctl btn-primary'), lang);
    const load = render('loading', {}, lang);
    assert.equal((load.match(/skel skel-line/g) || []).length, 3, lang + ' skeleton = 3 shimmer lines');
    assert.ok(load.includes('class="empty"') && !load.includes('btn'), lang + ' loading has no action button');
    const err = render('error', {}, lang);
    assert.ok(err.includes('⚠️') && err.includes('btn-ctl"'), lang + ' error offers a plain retry button');
    const off = render('offline', {updated: '11/16 05:40'}, lang);
    assert.ok(off.includes('offline-badge'), lang);
    assert.ok(off.includes('<span class="mono">11/16 05:40</span>'), lang + ' snapshot time shown');
    assert.ok(off.includes('btn-ctl"'), lang + ' reconnect action');
  }
  assert.equal(render('nope', {}, 'zh-TW'), '', 'unknown kind renders nothing');
});
test('CL-UI-85 (5c) empty-state classes match the design-system names', () => {
  assert.ok(clEmptyStateHtml.includes('class="empty"'), 'spec .empty component');
  assert.ok(clEmptyStateHtml.includes('skel skel-line'), 'spec .skel/.skel-line');
  assert.ok(clEmptyStateHtml.includes('offline-badge'), 'spec .offline-badge');
});

// ---- (6) cache-bust: app.js + app.css bumped together in index.html
test('CL-UI-85 (6) cache-bust stamp: index.html serves app.js + app.css at ?v=clui99', () => {
  assert.equal((indexSource.match(/\?v=clui99/g) || []).length, 2, 'app.js + app.css both at clui99');
  assert.doesNotMatch(indexSource, /\?v=clui89\b/, 'old generation retired');
});
