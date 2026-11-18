// CL-UI-114 追加: 方案 C — Windy 風格（owner 貼圖指定: 深藍海＋深綠陸地（植被色）
// ＋地形光影＋衛星實況雲白灰，台灣立體清晰、雲最突出）。
// Contract:
//  (1) CL-UI-117: 方案 C 設為預設（windy 預設 true）；?wgBasemapLight=1 為
//      逃生口回亮色 liberty（無 hillshade、無 tint、無濾鏡）。
//  (2) 底圖切 OpenFreeMap fiord（與方案 A 同一深色樣式）＋ 共用 Terrarium
//      raster-dem hillshade（illumination 315°、exaggeration 0.55）。
//  (3) Windy land tint：OpenMapTiles landcover/landuse 層（landcover_wood / park /
//      landuse_residential）＋ background 陸地基底調深綠、water 調深藍。
//  (4) 方案 C 不套 CSS 濾鏡 —— 雲層 canvas 在地圖容器內，濾鏡會連雲一起暗化；
//      C 必須讓雲保持白灰最突出（clui114ApplyLandTint 內不得出現 filter）。
//  (5) 應用時機：load + styledata 均呼叫（冪等；styledata 重入時 tint 已套用即跳過）。
//  (6) cache-bust stamp 進到 bclwg49。
// Run: node --test apps/web-v2/tests/cl-ui-114-basemap-c-windy.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
const ROOT = path.join(path.dirname(require.resolve('../../../assets/weather-map-regions.js')), '..');
const MAP_JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const WG_HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

test('CL-UI-114 C: 方案 C 為預設 — windy 預設 true、?wgBasemapLight=1 逃生口', () => {
  assert.ok(MAP_JS.includes("windy: q.get('wgBasemapLight') !== '1'"));
  assert.ok(MAP_JS.includes("light: q.get('wgBasemapLight') === '1',"));
  // 逃生口：light flag 直接 return，完全回亮色預設
  assert.ok(MAP_JS.includes('if (CLUI114_FLAGS.light) return;'));
  // catch fallback（無 window.search 可用）也必須保持方案 C 預設
  assert.ok(MAP_JS.includes('return { light: false, dark: false, dim: false, windy: true };'));
});

test('CL-UI-114 C: fiord 深色樣式共用（dark 或 windy 都切深色）＋ 共用 hillshade', () => {
  assert.ok(MAP_JS.includes('style:CLUI114_FLAGS.light ? BASEMAP_STYLE : CLUI114_DARK_STYLE,'));
  assert.ok(MAP_JS.includes('if (CLUI114_FLAGS.dark||CLUI114_FLAGS.windy) clui114ApplyHillshade(map);'));
  // Windy 風格的地形光影 = 同方案 A 的 Terrarium hillshade（315°、exaggeration 0.55）
  assert.ok(MAP_JS.includes("'hillshade-illumination-direction': 315"));
  assert.ok(MAP_JS.includes("'hillshade-exaggeration': 0.55"));
});

test('CL-UI-114 C: Windy land tint — landcover/landuse 深綠 + water 深藍', () => {
  assert.ok(MAP_JS.includes('function clui114ApplyLandTint(map){'));
  assert.ok(MAP_JS.includes('const CLUI114_WINDY_TINT = {'));
  for (const [layer, color] of [
    ['background', '#1C3B2A'],   // 陸地基底深綠
    ['water', '#152A45'],        // 海深藍
    ['landcover_wood', '#205232'], // 植被（森林）深綠
    ['park', '#1E4A2F'],
    ['landuse_residential', '#25382C'],
  ]) {
    assert.ok(MAP_JS.includes(color), `missing windy tint color ${color} for ${layer}`);
  }
  assert.ok(MAP_JS.includes("if (id === 'background') map.setPaintProperty(id, 'background-color', color);"));
  assert.ok(MAP_JS.includes("else map.setPaintProperty(id, 'fill-color', color);"));
  // 冪等：background 已是目標色即跳過（styledata 重入不重複套）
  assert.ok(MAP_JS.includes("if (map.getPaintProperty('background', 'background-color') === CLUI114_WINDY_TINT.background) return;"));
});

test('CL-UI-114 C: 套用時機 — tint 在共用入口內、load/styledata 都呼叫、不套 CSS 濾鏡', () => {
  assert.ok(MAP_JS.includes('if (CLUI114_FLAGS.windy) clui114ApplyLandTint(map);'));
  assert.ok(MAP_JS.includes('clui114ApplyBasemapAB(map);   // CL-UI-117: 方案 C 預設（?wgBasemapLight=1 逃生口）'));
  // 方案 C 不得暗化雲層：tint 函式內不可出現 filter（濾鏡只屬於方案 B 的 dim 分支）
  const a = MAP_JS.indexOf('function clui114ApplyLandTint(map){');
  const b = MAP_JS.indexOf('function clui114ApplyBasemapAB(map){', a);
  const tintFn = MAP_JS.slice(a, b);
  assert.ok(tintFn.includes('setPaintProperty') && !/\.style\.filter/.test(tintFn),
    'clui114ApplyLandTint must not apply a CSS filter');
});

test('CL-UI-114 C: cache-bust stamp bclwg49（css+vendor；js 已進 bclwg50）', () => {
  const stamps = WG_HTML.match(/\?v=bclwg49/g) || [];
  assert.ok(stamps.length >= 2, `expected >=2 bclwg49 stamps in weather-map.html, got ${stamps.length}`);
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg50/, 'js stamp must be bclwg50 after CL-APP-09 nav rename');
  assert.ok(!WG_HTML.includes('bclwg47'), 'stale bclwg47 stamp left in weather-map.html');
});
