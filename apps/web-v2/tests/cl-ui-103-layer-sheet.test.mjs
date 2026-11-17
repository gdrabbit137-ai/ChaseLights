// CL-UI-103: 手機天氣圖「圖層選單」開啟態修復 — owner 實測漏網開啟態
// （挑戰者 16 未涵蓋）：390px 下圖層 chips（低雲/能見度/10m風場/降雨率）＋
// 圖例（Camera/Subject/Environment）展開時一大塊深色面板蓋住台灣左半。
// Fix (比照已上線 DESIGN-10 bottom sheet 慣例):
//   · 收合態＝地圖左上僅一顆圖層 pill（標籤跟隨目前圖層）
//   · 展開態＝bottom sheet（與列表 sheet 同構：chips 網格＋圖例三行＋詳細入口），
//     地圖壓暗收成上緣預覽條（同款 wm-map-dim）
//   · 時間軸細帶（DESIGN-9）／列表 sheet（DESIGN-10）／圖層 sheet 三者互斥開啟
//   · 桌面 1280 零改動（地圖左上 chips overlay 列保留）；鏡頭行為不動（CL-UI-59）
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(path.dirname(require.resolve('../../../assets/weather-map-regions.js')), '..');
const MAP_JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const MAP_CSS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.css'), 'utf8');
const WG_HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

function grab(src, start, end) {
  const a = src.indexOf(start);
  assert.ok(a !== -1, `source slice start not found: ${start}`);
  const b = src.indexOf(end, a);
  assert.ok(b !== -1, `source slice end not found: ${end}`);
  return src.slice(a, b);
}

// ---------------------------------------------------------------------------
// 1. Markup: layer pill + layer sheet (chips grid + 3-row legend + 詳細 entry)
// ---------------------------------------------------------------------------
test('CL-UI-103: weather-map.html carries the layer pill and the layer bottom sheet', () => {
  assert.ok(WG_HTML.includes('id="layer-sheet-btn"'), 'collapsed state = single layer pill');
  assert.match(WG_HTML, /id="layer-sheet-btn"[^>]*aria-expanded="false"/, 'pill starts collapsed');
  assert.match(WG_HTML, /id="layer-sheet-btn"[^>]*aria-controls="wm-layer-sheet"/, 'pill controls the sheet');
  assert.ok(WG_HTML.includes('id="wm-layer-sheet"'), 'layer bottom sheet section');
  assert.match(WG_HTML, /<section id="wm-layer-sheet" class="wm-sheet"/, 'sheet reuses the DESIGN-10 .wm-sheet anatomy');
  assert.ok(WG_HTML.includes('id="wm-layer-sheet-grab"'), 'grab bar (下拉收起), same as the list sheet');
  assert.ok(WG_HTML.includes('id="wm-layer-sheet-head"'), 'sheet head with ✕');
  assert.ok(WG_HTML.includes('id="wm-ls-chips"'), 'chips grid host inside the sheet');
  assert.match(WG_HTML, /data-wm-act="layer-sheet-close"/, 'visible close affordance');
  assert.match(WG_HTML, /data-wm-act="layer-details"[\s\S]*?data-i18n="wm_details"[\s\S]*?>詳細</, '「詳細」 entry is i18n-wired');
  // 圖例三行（Camera/Subject/Environment）— same swatch anatomy as the map legend
  const legendRows = grab(WG_HTML, 'wm-ls-legend', 'wm-ls-foot');
  assert.ok(legendRows.includes('coverage-swatch camera'), 'Camera legend row');
  assert.ok(legendRows.includes('coverage-swatch subject'), 'Subject legend row');
  assert.ok(legendRows.includes('coverage-swatch environment'), 'Environment legend row');
});

test('CL-UI-103: cache-bust stamps bumped to bclwg49 in weather-map.html', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg49/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg49/);
});

// ---------------------------------------------------------------------------
// 2. i18n: the new key exists in ALL three dictionaries
// ---------------------------------------------------------------------------
test('CL-UI-103: wm_layer_sheet_close_aria exists in zh-TW, en and ja', () => {
  const count = (MAP_JS.match(/wm_layer_sheet_close_aria:/g) || []).length;
  assert.ok(count >= 3, `must exist in all three dictionaries (found ${count})`);
});

// ---------------------------------------------------------------------------
// 3. JS behavior: open/close + the same dimmed preview strip as DESIGN-10
// ---------------------------------------------------------------------------
test('CL-UI-103: layer sheet open/close mirrors the list sheet (sheet-open shell + dim + pill aria)', () => {
  const open = grab(MAP_JS, 'function wmOpenLayerSheet()', 'function wmCloseLayerSheet()');
  assert.ok(open.includes("panel.classList.add('sheet-open')"), 'reuses the shared sheet-open shell');
  assert.ok(open.includes("sheet.classList.add('open')"), 'the sheet itself carries .open');
  assert.ok(open.includes("dim.hidden=false"), 'map dims into the preview strip (same as DESIGN-10)');
  assert.ok(open.includes('wmRelocateDockForSheet(true)'), 'dock moves into the flow below the sheet');
  assert.ok(open.includes('wmFitSheetPanel()'), 'panel height fits the first screen');
  assert.ok(open.includes('renderWmLayerChips()'), 'sheet chips are rendered on open');
  assert.ok(open.includes('wmCloseMini()'), 'mini card yields while a sheet is open');
  const close = grab(MAP_JS, 'function wmCloseLayerSheet()', 'function renderWmSheet()');
  assert.ok(close.includes("panel.classList.remove('sheet-open')"), 'close restores the map shell');
  assert.ok(close.includes("sheet.classList.remove('open')"), 'close clears .open');
  assert.ok(close.includes("dim.hidden=true"), 'close removes the dim');
  assert.ok(close.includes('wmRelocateDockForSheet(false)'), 'close moves the dock back into the map');
});

// ---------------------------------------------------------------------------
// 4. Mutual exclusion: band / list sheet / layer sheet — open one closes others
// ---------------------------------------------------------------------------
test('CL-UI-103: the three mobile overlays are mutually exclusive (open one closes the others)', () => {
  const openLayer = grab(MAP_JS, 'function wmOpenLayerSheet()', 'function wmCloseLayerSheet()');
  assert.ok(openLayer.includes('if(wmSheetOpen) wmCloseSheet()'), 'opening the layer sheet closes the list sheet');
  assert.ok(openLayer.includes('wmCollapseTimelineBand()'), 'opening the layer sheet collapses the timeline band');
  const collapse = grab(MAP_JS, 'function wmCollapseTimelineBand()', 'function wmOpenLayerSheet()');
  assert.ok(collapse.includes('wmDockExpanded=false'), 'band collapse flips the shared state');
  assert.ok(collapse.includes("dock.classList.remove('expanded')"), 'band collapse clears the expanded class');
  assert.ok(collapse.includes("tlBar.setAttribute('aria-expanded','false')"), 'band collapse syncs aria');
  const openList = grab(MAP_JS, 'function wmOpenSheet()', 'function wmCloseSheet()');
  assert.ok(openList.includes('if(wmLayerSheetOpen) wmCloseLayerSheet()'), 'opening the list sheet closes the layer sheet');
  const wiring = grab(MAP_JS, 'function wmInitOverlays()', '// ── renderAll 掛鉤');
  const tlBarSlice = wiring.slice(wiring.indexOf('const tlBar'), wiring.indexOf('const sheetHost'));
  assert.ok(tlBarSlice.includes('if(wmSheetOpen) wmCloseSheet()'), 'expanding the band closes the list sheet');
  assert.ok(tlBarSlice.includes('if(wmLayerSheetOpen) wmCloseLayerSheet()'), 'expanding the band closes the layer sheet');
  const dimSlice = wiring.slice(wiring.indexOf('const sheetHost'), wiring.indexOf('const sheetSearch'));
  assert.ok(dimSlice.includes('wmCloseLayerSheet()'), 'dim hint / ✕ close the layer sheet too');
  assert.ok(wiring.includes('if(wmLayerSheetOpen) wmCloseLayerSheet()'), 'Escape closes the layer sheet');
});

// ---------------------------------------------------------------------------
// 5. Sheet contents: chips grid drives the SAME layer path; 選定即收; pill label
// ---------------------------------------------------------------------------
test('CL-UI-103: sheet chips share the overlay path (layer-select → renderAll) and close the sheet on pick', () => {
  const chips = grab(MAP_JS, 'function renderWmLayerChips()', '// ── 景點側欄');
  assert.ok(chips.includes("[$('layer-chips'),$('wm-ls-chips')]"), 'one chips source feeds the desktop overlay AND the sheet grid');
  assert.ok(chips.includes("pillLabel.textContent="), 'collapsed pill label follows the current layer');
  const wiring = grab(MAP_JS, 'function wmInitOverlays()', '// ── renderAll 掛鉤');
  const chipSlice = wiring.slice(wiring.indexOf("layerSheetHost.contains(chip)"));
  assert.ok(chipSlice.includes('state.layer=chip.dataset.wmLayer'), 'sheet chip sets the same state.layer');
  assert.ok(chipSlice.includes("layerSelect.value=state.layer"), 'sheet chip drives the existing layer-select path');
  assert.ok(chipSlice.includes('wmCloseLayerSheet()'), '選定即收 — picking a layer closes the sheet');
  assert.ok(chipSlice.includes('renderAll()'), 'sheet chip re-renders through the existing path');
  const detailsSlice = wiring.slice(wiring.indexOf("data-wm-act=\"layer-details\""));
  assert.ok(detailsSlice.includes('wmCloseLayerSheet()'), '詳細 closes the layer sheet first');
  assert.ok(detailsSlice.includes("detailsToggle.click()"), '詳細 expands the inspector layer details via the real toggle');
  assert.ok(detailsSlice.includes('scrollIntoView'), '詳細 scrolls the layer panel into view');
  assert.ok(wiring.includes("layerBtn.addEventListener('click',()=>wmOpenLayerSheet())"), 'the pill opens the layer sheet');
});

// ---------------------------------------------------------------------------
// 6. CSS: collapsed pill / expanded sheet / sheet contents — mobile only
// ---------------------------------------------------------------------------
test('CL-UI-103 CSS: mobile collapses the overlay chips into the pill; the sheet carries grid + legend + 詳細', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /\.wm-ctl\{display:none\}/, 'no chips block painted over the map on mobile');
  assert.match(mobileBlock, /#layer-sheet-btn\{left:var\(--cl-sp-3\);right:auto\}/, 'single pill at top-left');
  assert.match(mobileBlock, /\.map-panel\.sheet-open #wm-layer-sheet\.open\{display:flex;flex:0 0 auto/, 'layer sheet opens inside the shared sheet-open shell');
  assert.match(mobileBlock, /\.wm-ls-chips\{[^}]*grid-template-columns:repeat\(2,minmax\(0,1fr\)\)/, 'chips render as a 2-column grid');
  assert.match(mobileBlock, /\.wm-ls-chips \.wm-chip\{width:100%;justify-content:center\}/, 'grid chips fill their cell');
  assert.match(mobileBlock, /\.wm-ls-legend\{[^}]*border-top:1px solid var\(--cl-border\)\}/, 'legend rows sit in the sheet, not on the map');
  assert.match(mobileBlock, /\.wm-ls-foot \.wm-btn\{width:100%;height:44px\}/, '詳細 entry is a 44px touch target');
  // 圖例不再被 top:52px+bottom:56px 拉伸成蓋住台灣左半的深色大面板
  assert.match(mobileBlock, /\.map-wrap \.legend\{display:block;top:auto;bottom:56px\}/, 'compact legend stays a small box above the band (no vertical stretch)');
  // the sheet chrome must not leak outside the mobile block (1280 zero-change)
  const beforeMobile = MAP_CSS.slice(0, MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.ok(!/\.wm-ls-/.test(beforeMobile), 'no layer-sheet chrome leaks outside the mobile block');
  assert.ok(!/#layer-sheet-btn\{left/.test(beforeMobile), 'no pill position leak outside the mobile block');
});

// ---------------------------------------------------------------------------
// 7. Desktop 1280 zero-change + camera untouched
// ---------------------------------------------------------------------------
test('CL-UI-103: desktop (>=769px) keeps the overlay chips row and hides pill/sheet (zero change)', () => {
  const desktopBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'));
  assert.match(desktopBlock, /\.wm-sheet-btn\{display:none\}/, 'no pill on desktop (covers #layer-sheet-btn via its class)');
  assert.match(desktopBlock, /\.wm-sheet\{display:none\}/, 'both sheets hidden on desktop');
  assert.match(desktopBlock, /\.wm-map-dim\{display:none\}/, 'no dim on desktop');
  const select = grab(MAP_JS, 'function selectSpot(spotId)', 'function locateSpot(');
  assert.ok(!select.includes('setViewBbox'), 'CL-UI-59: selecting a spot never re-fits the view');
  assert.ok(!select.includes('fitCoverageBbox'), 'CL-UI-59: selecting a spot never zooms');
});
