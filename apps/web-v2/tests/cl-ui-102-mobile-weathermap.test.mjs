// CL-UI-102: 手機天氣圖總修復 — DESIGN-9/10 mockup + CHALLENGER-16 audit (20 items).
// Spec sources:
//   · origin/task/DESIGN-3 head fdae38022 mockup-weathermap.html
//     (DESIGN-9 32px collapsible timeline band; DESIGN-10 full-width bottom sheet)
//   · origin/task/CHALLENGER-16 head 5acec1a57 data/v2/audits/challenger-16-mobile-weathermap.md
//     (F1 chip overlap / F2 dead zone + scrollIntoView / F3 sheet / F5 locate hack /
//      F6 one-name-per-column / F7 label clipping / F8-F9 layering / F11-F20 polish)
// All fixes are scoped to the mobile shell (<=768px); desktop (>=769px) keeps the
// right side panel and the always-open timeline dock (1280 zero-change), and the
// camera behavior stays CL-UI-59.
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
// 1. Markup: collapsible band (DESIGN-9) + bottom sheet (DESIGN-10) + stamps
// ---------------------------------------------------------------------------
test('CL-UI-102: weather-map.html carries the tl-bar, bottom sheet and map-dim markup', () => {
  assert.ok(WG_HTML.includes('id="wm-tl-bar"'), 'DESIGN-9 collapsed band button');
  assert.ok(WG_HTML.includes('id="wm-tl-sel"'), 'band selection summary');
  assert.match(WG_HTML, /class="wm-tl-bar"[^>]*aria-expanded="false"/, 'band starts collapsed');
  assert.ok(WG_HTML.includes('id="wm-sheet"'), 'DESIGN-10 bottom sheet section');
  assert.ok(WG_HTML.includes('id="wm-sheet-search"'), 'sheet search input');
  assert.ok(WG_HTML.includes('id="wm-sheet-sort"'), 'sheet sort label');
  assert.ok(WG_HTML.includes('id="wm-sheet-list"'), 'sheet list host');
  assert.ok(WG_HTML.includes('id="wm-sheet-grab"'), 'grab bar (下拉收起)');
  assert.ok(WG_HTML.includes('id="wm-sheet-close"') || WG_HTML.includes('data-wm-act="sheet-close"'),
    'visible close affordance (✕ / dim-hint), audit F3');
  assert.ok(WG_HTML.includes('id="wm-map-dim"'), 'map dim overlay (map shrinks to preview strip)');
  assert.ok(WG_HTML.includes('wm_dim_hint'), '點此返回 pill is i18n-wired');
});

test('CL-UI-102: cache-bust stamps bumped to bclwg46 in weather-map.html', () => {
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg46/);
  assert.match(WG_HTML, /assets\/weather-map\.css\?v=bclwg46/);
  assert.ok(!/weather-map\.js\?v=bclwg38/.test(WG_HTML), 'old js stamp must not linger');
});

// ---------------------------------------------------------------------------
// 2. New WM_STATIC i18n keys exist in ALL three dictionaries
// ---------------------------------------------------------------------------
test('CL-UI-102: wm_tl_now / wm_sheet_* / wm_dim_hint exist in zh-TW, en and ja', () => {
  for (const key of ['wm_tl_now', 'wm_sheet_search', 'wm_sheet_close_aria', 'wm_dim_hint', 'wm_sheet_sort', 'wm_sheet_n']) {
    const count = (MAP_JS.match(new RegExp(`${key}:`, 'g')) || []).length;
    assert.ok(count >= 3, `${key} must exist in all three dictionaries (found ${count})`);
  }
});

// ---------------------------------------------------------------------------
// 3. DESIGN-9 behavior in the JS overlay section
// ---------------------------------------------------------------------------
test('CL-UI-102 DESIGN-9: band expands in place, collapses on selection, scrolls the selection into view', () => {
  const init = grab(MAP_JS, 'function wmInitOverlays()', '// ── renderAll 掛鉤');
  assert.ok(init.includes("wmDockExpanded=!wmDockExpanded"), 'tl-bar click toggles the band');
  assert.ok(init.includes("selPill.scrollIntoView"), 'expand scrolls the selected day pill into view (audit F2/F7)');
  assert.ok(init.includes("selCell.scrollIntoView"), 'expand scrolls the selected hour cell into view');
  const dayClick = grab(MAP_JS, "const dayRow=$('wm-day-row');\n    if(dayRow){", "const hourRow=$('wm-hour-row')");
  assert.ok(dayClick.includes('wmDockExpanded=false'), '選定即收合 — picking a day collapses the band');
  const hourClick = grab(MAP_JS, "const hourRow=$('wm-hour-row');\n    if(hourRow){", 'const mini=$(\'wm-mini\')');
  assert.ok(hourClick.includes('wmDockExpanded=false'), '選定即收合 — picking an hour collapses the band');
  const dockUpdate = grab(MAP_JS, 'function wmUpdateTimeDock()', '// ── 事件接線');
  assert.ok(dockUpdate.includes("dock.classList.toggle('expanded'"), 'expanded state survives re-renders');
  assert.ok(dockUpdate.includes("tlSel.textContent="), 'band summary tracks the current selection');
});

test('CL-UI-102 DESIGN-9: band is mobile-only — desktop keeps the always-open dock', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /\.wm-tl-bar\{display:flex/, 'mobile shows the band');
  assert.match(mobileBlock, /\.wm-timeline-dock \.wm-day-row,\.wm-timeline-dock \.wm-hour-row\{display:none\}/,
    'collapsed band hides the rows by default');
  assert.match(mobileBlock, /\.wm-timeline-dock\.expanded \.wm-day-row/, 'expanding shows the rows');
  const desktopBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'));
  assert.match(desktopBlock, /\.wm-tl-bar\{display:none\}/, 'desktop hides the band (1280 zero-change)');
});

// ---------------------------------------------------------------------------
// 4. DESIGN-10 behavior in the JS overlay section
// ---------------------------------------------------------------------------
test('CL-UI-102 DESIGN-10: sheet open/close, row select closes and reopens the map, grab drag >80px closes', () => {
  const section = grab(MAP_JS, '===== CL-UI-102: DESIGN-9 collapsible timeline', 'window.addEventListener(\'pagehide\'');
  assert.ok(section.includes('function wmOpenSheet()'), 'open');
  assert.ok(section.includes('function wmCloseSheet()'), 'close');
  assert.ok(section.includes('panel.classList.add(\'sheet-open\')'), 'open toggles the panel shell');
  assert.ok(section.includes('wmCloseMini()'), 'open closes the mini card (three-layer stack, audit F8/F9)');
  assert.ok(section.includes('wmRelocateDockForSheet(true)'), 'dock moves into the flow below the sheet');
  const wiring2 = grab(MAP_JS, 'function wmInitOverlays()', '// ── renderAll 掛鉤');
  assert.ok(wiring2.includes('wmSheetDragDy>80'), 'grab drag down >80px closes');
  assert.ok(wiring2.includes('data-wm-sheet-spot'), 'sheet rows carry spot ids');
  const wiring = grab(MAP_JS, 'function wmInitOverlays()', '// ── renderAll 掛鉤');
  const rowClick = wiring.slice(wiring.indexOf('data-wm-sheet-spot'));
  assert.ok(rowClick.includes('wmCloseSheet()'), 'row select closes the sheet');
  assert.ok(rowClick.includes('selectSpot(spotId)'), 'row select drives the existing select path');
  assert.ok(rowClick.includes('wmOpenMini(spotId)'), 'row select opens the mini card (選定即回圖)');
});

test('CL-UI-102 DESIGN-10: shootable % is a deterministic recompute; row color shares the dot tier source', () => {
  const slice = grab(MAP_JS, 'function wmShootPct(', '// DESIGN-10: when the sheet opens');
  const factory = new Function('samplePointValue', 'state', 'wmSpotCoverage',
    `${slice}\nreturn wmShootPct;`);
  const wmShootPct = factory(
    (point, key) => ({ low_cloud_percent: 40, visibility_km: 12, wind_speed_10m_m_s: 5, precip_rate_mm_h: 1 }[key]),
    { layer: 'low_cloud_percent' },
    () => ({ dot: 'ok', badge: 'ok', group: {} }));
  assert.equal(wmShootPct({ lat: 25, lon: 121 }), 60, 'low cloud 40% → 60%');
  const vis = factory((p, k) => 12, { layer: 'visibility_km' }, (() => ({ dot: 'ok', badge: 'ok', group: {} })));
  assert.equal(vis({ lat: 25, lon: 121 }), 50, 'visibility 12km / 24.1 → 50%');
  const wind = factory((p, k) => 5, { layer: 'wind_speed_10m_m_s' }, (() => ({ dot: 'ok', badge: 'ok', group: {} })));
  assert.equal(wind({ lat: 25, lon: 121 }), 80, 'wind 5 m/s → 80%');
  const none = factory((p, k) => NaN, { layer: 'low_cloud_percent' }, (() => ({ dot: 'ok', badge: 'ok', group: {} })));
  assert.equal(none({ lat: 25, lon: 121 }), null, 'no sample → honest null, never a fake %');
  const noCov = factory((p, k) => 10, { layer: 'low_cloud_percent' }, () => ({ dot: 'off', badge: 'off', group: null }));
  assert.equal(noCov({ lat: 25, lon: 121 }), null, 'no-coverage spot → no fabricated % (single-truth ruling)');
  const renderer = grab(MAP_JS, 'function renderWmSheet()', '// ── F18：跨頁往返');
  assert.ok(renderer.includes("cov.dot==='ok'?'wm-p-hi'"), '% color derives from the SAME tier source as the dot');
  assert.ok(renderer.includes("rows.sort"), 'rows are sorted');
  assert.ok(renderer.includes('.includes(query)'), 'search filters rows (name / id / region)');
  assert.ok(!renderer.includes('${escapeHtml(spot.spot_id)}') || renderer.includes('data-wm-sheet-spot'),
    'raw ids stay as data attributes, never row copy (audit F12)');
  assert.ok(renderer.includes("r-meta\">${escapeHtml(regionName)}"), 'row meta is the region name (no tw-002 leak)');
});

// ---------------------------------------------------------------------------
// 5. Fatal F1: quick chips must never sit under the list button
// ---------------------------------------------------------------------------
test('CL-UI-102 F1 (re-anchored by CL-UI-103): quick chips live in the layer sheet on mobile — the overlay row collapses to the single pill and can never sit under the list button', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /\.wm-ctl\{display:none\}/, 'CL-UI-103: overlay chips row is collapsed into the layer pill on mobile');
  assert.match(mobileBlock, /#layer-sheet-btn\{left:var\(--cl-sp-3\);right:auto\}/, 'collapsed state = one layer pill at top-left (list button stays top-right)');
  assert.match(mobileBlock, /\.map-panel\.sheet-open #wm-layer-sheet\.open\{display:flex/, 'expanded state = layer bottom sheet, same shell as the list sheet');
  const desktopBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'));
  assert.match(desktopBlock, /\.wm-sheet-btn\{display:none\}/, 'desktop keeps the overlay chips row (no pill) — 1280 zero-change');
});

// ---------------------------------------------------------------------------
// 6. Locate button hack removed (audit F5); 44px touch targets (audit F4)
// ---------------------------------------------------------------------------
test('CL-UI-102: locate pill becomes a normal in-flow 44px button on mobile', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /#locate-spot\{position:static/, 'no absolute page-top hack on mobile');
  assert.match(mobileBlock, /#locate-spot\{position:static;width:100%;height:44px/, '44px pill');
  assert.match(mobileBlock, /\.wm-chip\{height:44px\}/, 'chips 44px');
  assert.match(mobileBlock, /\.maplibregl-ctrl-group button\{width:44px;height:44px\}/, 'zoom controls 44px');
  assert.match(mobileBlock, /\.wm-mini-x\{width:44px;height:44px/, 'mini-card ✕ 44px');
  assert.match(mobileBlock, /\.layer-details-toggle\{min-height:44px\}/, '詳細 toggle 44px');
});

// ---------------------------------------------------------------------------
// 7. Dead zone + range honesty
// ---------------------------------------------------------------------------
test('CL-UI-102: scrollport keeps a clickable right padding (dead-zone fix)', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /scroll-padding-right:8px/, 'scroll-padding so the last pill can fully center');
  assert.match(mobileBlock, /padding-right:8px/, 'visible padding, not painted-over dead area');
});

// ---------------------------------------------------------------------------
// 8. Copy/leak fixes (F11/F12/F13-scope/F14/F15/F16/F18)
// ---------------------------------------------------------------------------
test('CL-UI-102 F11: no internal-state leakage in the coverage panel', () => {
  assert.ok(!MAP_JS.includes('partial migration'), 'English pipeline badge never leaves the page');
  assert.ok(!MAP_JS.includes("coverage-badge provisional\">partial"), 'no provisional badge for incomplete migrations');
  assert.ok(MAP_JS.includes("wmT('題材涵蓋 {a} / {b} 個；其中 {c} 個仍在補齊。'"), 'localized coverage wording');
  assert.ok(MAP_JS.includes("wmT('機位 {a} · 主體 {b} · 環境 {c}'"), 'Camera/Subject/Environment counts localized');
  assert.ok(MAP_JS.includes("wmT('選擇單一題材可檢查 機位／主體／環境。'"), 'coverage hint localized');
});

test('CL-UI-102 F12: raw coordinates and engineering copy stay out of display surfaces', () => {
  const mini = grab(MAP_JS, 'function renderWmMini()', 'function wmOpenMini(');
  assert.ok(!mini.includes('spot.lat.toFixed'), 'mini card region line has no coordinates');
  const modal = grab(MAP_JS, 'function wmOpenDetail(', 'function wmCloseDetail(');
  assert.ok(!modal.includes("regionHost.textContent=`${wmRegionName()} · ${spot.lat"), 'modal headline has no coordinates');
  assert.ok(modal.includes('wm-modal-region'), 'modal region line still names the region');
  const spotPanel = grab(MAP_JS, 'const wmMobileShell=window.matchMedia', 'updateLegend(cfg)');
  assert.ok(spotPanel.includes('wm-panel-acc'), 'mobile collapses coords/取樣/診斷 into a 詳細 accordion');
  assert.ok(spotPanel.includes('wmMobileShell'), 'the collapse is mobile-only (desktop 1280 unchanged)');
  assert.ok(MAP_JS.includes("'☁️ 低雲'"), 'dropdown and chips share the single 低雲 name (audit F6)');
  assert.ok(!/low_cloud_percent:'🌫️ 山霧'/.test(MAP_JS), 'no second name for the same data column');
});

test('CL-UI-102 F14/F20: compact legend shows on mobile; panel range and legend scale are one sentence', () => {
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /\.map-wrap \.legend\{display:block/, 'mobile shows the palette-derived compact legend');
  assert.match(mobileBlock, /bottom:56px/, 'legend sits above the collapsed band');
  assert.match(mobileBlock, /\.map-panel\.sheet-open \.map-wrap \.legend\{display:none\}/, 'legend yields when the sheet opens');
  assert.ok(MAP_JS.includes("圖例色階上限 {a}"), 'panel range names the legend scale when they differ');
});

test('CL-UI-102 F15: QC badge never contradicts rendered wind arrows', () => {
  const qc = grab(MAP_JS, 'if(!state.lastDataRendered && !state.lastCanvasPainted){', 'if(isObservationMode()){');
  assert.ok(qc.includes('lastWindVectorCount'), 'checks whether arrows actually rendered');
  assert.ok(qc.includes('風向箭頭已顯示'), 'two-part wording instead of a blanket 資料層未顯示');
});

test('CL-UI-102 F16: mobile basemap noise muted; desktop untouched', () => {
  assert.ok(MAP_JS.includes('function hideBasemapLabelNoise('), 'sea/water label mute exists');
  assert.ok(MAP_JS.includes("hideBasemapLabelNoise(map);"), 'wired next to the boundary mute');
  const mute = grab(MAP_JS, 'function hideBasemapLabelNoise(', 'function hideBoundaryLineLayers(');
  assert.ok(mute.includes("matchMedia('(max-width:768px),(max-height:768px)')"), 'mute is mobile-only (CL-UI-109: min(w,h)<=768)');
  const mobileBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.match(mobileBlock, /\.maplibregl-ctrl-group\{background:rgba\(15,23,42,\.92\)/, 'dark zoom control on mobile');
  assert.ok(!/@media \(min-width:769px\)[\s\S]*maplibregl-ctrl-group\{background:rgba\(15,23,42/.test(
    MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'))), 'desktop zoom control keeps the stock theme');
});

test('CL-UI-102 F18: cross-page roundtrip restores spot + model; deep link still wins', () => {
  assert.ok(MAP_JS.includes("chaselights_wm_session_v1"), 'session memory key');
  assert.ok(MAP_JS.includes('function wmPersistSession()'), 'persist');
  assert.ok(MAP_JS.includes('function wmRestoreSession()'), 'restore');
  assert.ok(MAP_JS.includes("wmPersistSession();\n    renderAll();"), 'selectSpot persists the session');
  const restore = grab(MAP_JS, 'function wmRestoreSession()', 'window.addEventListener(\'pagehide\'');
  assert.ok(restore.includes('!dl.spot'), 'explicit ?spot= deep link still wins over memory');
  assert.ok(restore.includes('switchModel(saved.model)'), 'model choice is carried back');
});

// ---------------------------------------------------------------------------
// 9. Desktop 1280 zero-change guard
// ---------------------------------------------------------------------------
test('CL-UI-102: desktop (>=769px) gets no sheet / band / dim / dark-zoom changes', () => {
  const desktopBlock = MAP_CSS.slice(MAP_CSS.indexOf('@media (min-width:769px) and (min-height:769px){'));
  assert.match(desktopBlock, /\.wm-sheet\{display:none\}/);
  assert.match(desktopBlock, /\.wm-map-dim\{display:none\}/);
  assert.match(desktopBlock, /\.wm-tl-bar\{display:none\}/);
  // The sheet/band CSS lives ONLY inside the mobile media query.
  const beforeMobile = MAP_CSS.slice(0, MAP_CSS.indexOf('@media (max-width:768px),(max-height:768px){'));
  assert.ok(!/\.wm-sheet-grab/.test(beforeMobile), 'no sheet chrome leaks outside the mobile block');
  assert.ok(!/\.wm-tl-bar/.test(beforeMobile), 'no band chrome leaks outside the mobile block');
});

// ---------------------------------------------------------------------------
// 10. Camera contract untouched (CL-UI-59) and side list preserved for desktop
// ---------------------------------------------------------------------------
test('CL-UI-102: selectSpot still never moves the camera; sheet select drives the same path', () => {
  const select = grab(MAP_JS, 'function selectSpot(spotId)', 'function locateSpot(');
  assert.ok(!select.includes('setViewBbox'), 'selecting a spot never re-fits the view');
  assert.ok(!select.includes('fitCoverageBbox'), 'selecting a spot never zooms');
  const wiring = grab(MAP_JS, 'function wmInitOverlays()', '// ── renderAll 掛鉤');
  assert.ok(wiring.includes("sideToggle.addEventListener('click',()=>wmOpenSheet())"), 'list button opens the sheet');
});
