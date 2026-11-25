// CL-UI-126 (owner report): reminders#subjects → 「＋ 新增題材」 → 「選擇景點」
// always opened on Hokkaido, because the catalog's first entry is Japanese and
// the picker listed every region at once. It must open on the region of the
// current page context / the last used region (fallback 'tw') and carry a
// visible region switcher (台灣/日本/美國/阿拉斯加/夏威夷).
//
// Run: node --test apps/web-v2/tests/cl-ui-126-subject-picker-region.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const LIB = readFileSync(join(WEB, 'assets', 'subject-sets-library.js'), 'utf8');
const HTML = readFileSync(join(WEB, 'reminders.html'), 'utf8');
const CATALOG = JSON.parse(readFileSync(join(WEB, 'apps', 'web-v2', 'evaluations-latest.json'), 'utf8'));

const grab = (start, end) => {
  const a = LIB.indexOf(start);
  assert.ok(a !== -1, `slice start not found: ${start}`);
  const b = LIB.indexOf(end, a);
  assert.ok(b !== -1, `slice end not found: ${end}`);
  return LIB.slice(a, b);
};

// ── the pure part, evaluated for real ──────────────────────────────────────
const factory = new Function([
  grab("var PICK_REGIONS = ['tw', 'jp', 'us', 'ak', 'hi'];", 'function pickerRegionDefault()'),
  grab('function pickerEntries', 'function quotaLine'),
  "const placeName=(id,catalog)=>((catalog||[]).find(p=>p.place_id===id)||{}).name_i18n?.['zh-TW']||id;",
  'return {pickerEntries,regionOfPlaceId,PICK_REGIONS};'
].join('\n'));
const { pickerEntries, regionOfPlaceId, PICK_REGIONS } = factory();

const catalog = [
  { place_id: 'jp-001', name_i18n: { 'zh-TW': '美瑛青池' } },
  { place_id: 'tw-001', name_i18n: { 'zh-TW': '象山' } },
  { place_id: 'us-001', name_i18n: { 'zh-TW': '優勝美地' } },
  { place_id: 'ak-004', name_i18n: { 'zh-TW': '迪納利' } },
  { place_id: 'hi-002', name_i18n: { 'zh-TW': '歐胡島' } }
];

test('CL-UI-126 (1): entries are filtered to ONE region — tw never lists Hokkaido', () => {
  const tw = pickerEntries(catalog, [], '', 'zh-TW', 'tw');
  assert.deepEqual(tw.official.map((e) => e.placeId), ['tw-001'],
    'the tw list contains tw places only');
  assert.deepEqual(pickerEntries(catalog, [], '', 'zh-TW', 'jp').official.map((e) => e.placeId), ['jp-001']);
  assert.deepEqual(pickerEntries(catalog, [], '', 'zh-TW', 'ak').official.map((e) => e.placeId), ['ak-004']);
  assert.deepEqual(pickerEntries(catalog, [], '', 'zh-TW', 'hi').official.map((e) => e.placeId), ['hi-002']);
});

test('CL-UI-126 (2): keyword search stays inside the selected region; private places are never region-gated', () => {
  const hits = pickerEntries(catalog, [{ id: 'cp-9', name: '我的秘密點' }], '', 'zh-TW', 'us');
  assert.deepEqual(hits.official.map((e) => e.placeId), ['us-001']);
  assert.deepEqual(hits.private.map((e) => e.placeId), ['cp-9'], 'the member’s own places stay visible');
  const none = pickerEntries(catalog, [], '青池', 'zh-TW', 'tw');
  assert.equal(none.official.length, 0, 'a jp match does not leak into the tw tab');
  const jp = pickerEntries(catalog, [], '青池', 'zh-TW', 'jp');
  assert.deepEqual(jp.official.map((e) => e.placeId), ['jp-001']);
});

test('CL-UI-126 (3): the region of a place id is its prefix; unknown ids fall through', () => {
  assert.equal(regionOfPlaceId('tw-036'), 'tw');
  assert.equal(regionOfPlaceId('ak-004'), 'ak');
  assert.equal(regionOfPlaceId('cp-123'), '', 'private places carry no region prefix');
  assert.equal(regionOfPlaceId(''), '');
  // unknown region → fail-open (the whole catalog, as before the fix)
  assert.equal(pickerEntries(catalog, [], '', 'zh-TW', '').official.length, 5);
  assert.equal(pickerEntries(catalog, [], '', 'zh-TW', 'zz').official.length, 5);
});

test('CL-UI-126 (4): the real catalog resolves every region the switcher offers', () => {
  const present = new Set((CATALOG.places || []).map((p) => regionOfPlaceId(p.place_id)));
  for (const region of PICK_REGIONS) {
    const list = pickerEntries(CATALOG.places || [], [], '', 'zh-TW', region).official;
    const wrong = list.filter((e) => regionOfPlaceId(e.placeId) !== region);
    assert.equal(wrong.length, 0, `${region}: no foreign place in the list`);
    if (present.has(region)) assert.ok(list.length > 0, `${region}: the catalog's places are listed`);
    else assert.equal(list.length, 0, `${region}: an uncovered region is honestly empty (never foreign places)`);
  }
});

test('CL-UI-126 (5): default region = URL → last used → page selector → tw', () => {
  const fn = grab('function pickerRegionDefault()', 'function openPicker()');
  const urlRegion = fn.indexOf("new URLSearchParams(location.search).get('region')");
  const stored = fn.indexOf("localStorage.getItem('chaselights_region')");
  const remRegion = fn.indexOf("document.getElementById('rem-region')");
  const fallback = fn.lastIndexOf("return 'tw';");
  assert.ok(urlRegion > 0 && stored > urlRegion && remRegion > stored && fallback > remRegion,
    'resolution order is URL → last used → page selector → tw');
  assert.ok(!/Hokkaido|北海道|jp-001/.test(fn), 'no hardcoded Japanese default');
});

test('CL-UI-126 (6): the picker renders a five-region switcher and repaints on switch', () => {
  const picker = grab('function openPicker()', '// ───────────────────────── condition form');
  for (const r of ['tw', 'jp', 'us', 'ak', 'hi']) {
    assert.ok(picker.includes(`region_' + r`), 'labels come from the i18n dictionary');
  }
  assert.match(picker, /class="sslib-region" role="group" aria-label="/, 'visible region switcher group');
  assert.match(picker, /data-sslib-region="' \+ r/, 'each region is a real button');
  assert.match(picker, /state\.pickRegion = b\.getAttribute\('data-sslib-region'\)/, 'click switches the region');
  assert.match(picker, /localStorage\.setItem\('chaselights_region', state\.pickRegion\)/, 'the choice is remembered');
  assert.match(picker, /paint\(pickerEntries\(state\.catalog, state\.customPlaces, '', currentLang\(\), state\.pickRegion\)\)/,
    'the initial list already honours the region');
});

test('CL-UI-126 (7): region labels exist in all three locales (mentions all five regions)', () => {
  for (const key of ['region_tw', 'region_jp', 'region_us', 'region_ak', 'region_hi', 'pick_region']) {
    assert.equal((LIB.match(new RegExp(`${key}:`, 'g')) || []).length, 3,
      `${key} exists in all three dictionaries`);
  }
  assert.ok(LIB.includes("region_tw: '台灣', region_jp: '日本', region_us: '美國', region_ak: '阿拉斯加', region_hi: '夏威夷'"),
    'zh-TW names the five regions exactly as the owner asked');
});

test('CL-UI-126 (8): the picker stays on ONE page/one control and the styles exist', () => {
  assert.equal((HTML.match(/data-sslib-region/g) || []).length, 0, 'buttons are built by the asset, not duplicated in HTML');
  assert.match(HTML, /\.sslib-region\{display:flex/, 'switcher row styling');
  assert.match(HTML, /\.sslib-region-btn\.on\{/, 'active region styling');
});
