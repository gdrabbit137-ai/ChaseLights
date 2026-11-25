// CL-UI-114 / CL-UI-117: 深色底圖地形改善。方案 C（Windy 風格）已自 CL-UI-117
// 起設為預設（windy 預設 true）。
// Contract:
//  (1) 預設（無 URL flag）＝方案 C：OpenFreeMap fiord 深色樣式；
//      ?wgBasemapLight=1 逃生口回 liberty 亮色（無 hillshade、無 tint、無濾鏡）。
//  (2) 方案 A（?wgBasemapDark=1）：樣式切換為 OpenFreeMap fiord（深色），
//      疊 AWS Terrarium raster-dem source（encoding:terrarium）＋ hillshade
//      圖層（illumination 315°、exaggeration 0.55、半透明 highlight，深色下
//      山脊可辨）；hillshade 層插入第一個 symbol 圖層之前，地名標籤保持最上。
//  (3) 方案 B（?wgBasemapDim=1）：現行亮色底圖 + 容器 CSS 暗化濾鏡
//      brightness(0.55) saturate(0.75)，只作用於底圖容器（雲層 canvas 在
//      容器之外，不受濾鏡影響——雲層可讀性由視覺 A/B 截圖評註）。
//  (4) 應用時機：'load' 與 'styledata' 都呼叫（冪等；與 CL-UI-107 同點）。
//  (5) cache-bust stamp 進到 bclwg49（本票改了 weather-map.js）。
// Run: node --test apps/web-v2/tests/cl-ui-114-basemap-ab-flag.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
const ROOT = path.join(path.dirname(require.resolve('../../../assets/weather-map-regions.js')), '..');
const MAP_JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const WG_HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

test('CL-UI-117: 預設樣式為 fiord 深色；liberty 僅 ?wgBasemapLight=1 逃生口', () => {
  const a = MAP_JS.indexOf("const BASEMAP_STYLE =");
  assert.ok(a !== -1, 'BASEMAP_STYLE declaration missing');
  assert.ok(MAP_JS.includes("const BASEMAP_STYLE = 'https://tiles.openfreemap.org/styles/liberty';"));
  // 樣式選擇：預設 → fiord；light 逃生口 → liberty
  assert.ok(MAP_JS.includes('style:CLUI114_FLAGS.light ? BASEMAP_STYLE : CLUI114_DARK_STYLE,'));
});

test('CL-UI-114: 方案 A — fiord 深色樣式 + Terrarium raster-dem hillshade 參數', () => {
  assert.ok(MAP_JS.includes("const CLUI114_DARK_STYLE = 'https://tiles.openfreemap.org/styles/fiord';"));
  assert.ok(MAP_JS.includes('https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'));
  assert.ok(MAP_JS.includes("encoding: 'terrarium'"));
  assert.ok(MAP_JS.includes("type: 'raster-dem'"));
  assert.ok(MAP_JS.includes("type: 'hillshade'"));
  assert.ok(MAP_JS.includes("'hillshade-illumination-direction': 315"));
  assert.ok(MAP_JS.includes("'hillshade-exaggeration': 0.55"));
  assert.ok(MAP_JS.includes("'hillshade-highlight-color': 'rgba(255,255,255,0.42)'"));
  // hillshade 插在第一個 symbol 之前，地名標籤不會被 DEM 層蓋住
  assert.ok(MAP_JS.includes("layers.find((l) => l && l.type === 'symbol')"));
  assert.ok(MAP_JS.includes("map.addLayer(layer, firstSymbol.id)"));
});

test('CL-UI-114: 方案 B — 底圖容器 CSS 暗化濾鏡 brightness(0.55) saturate(0.75)', () => {
  assert.ok(MAP_JS.includes("c.style.filter = 'brightness(0.55) saturate(0.75)'"));
  // 濾鏡只作用於 map 容器（getContainer），不是全頁 body
  const a = MAP_JS.indexOf('CLUI114_FLAGS.dim');
  const slice = MAP_JS.slice(a, MAP_JS.indexOf('}', a) + 400);
  assert.ok(slice.includes('map.getContainer()'));
});

test('CL-UI-114: 應用時機 load + styledata，且 flag 關閉時 no-op 冪等', () => {
  assert.ok(MAP_JS.includes('clui114ApplyBasemapAB(map);   // CL-UI-117'));
  assert.ok(MAP_JS.includes("map.on('styledata',()=>{ hideBoundaryLineLayers(map); clui114ApplyBasemapAB(map); });"));
  // 冪等：source 已存在即跳過
  assert.ok(MAP_JS.includes("if (map.getSource('clui114-terrarium')) return;"));
  // 逃生口：light flag 直接 return，回亮色預設
  assert.ok(MAP_JS.includes('if (CLUI114_FLAGS.light) return;'));
});

test('CL-UI-114: cache-bust stamp bclwg49（css+vendor；js 已進 bclwg51）', () => {
  const stamps = WG_HTML.match(/\?v=bclwg49/g) || [];
  assert.ok(stamps.length >= 2, `expected >=2 bclwg49 stamps in weather-map.html, got ${stamps.length}`);
  assert.match(WG_HTML, /assets\/weather-map\.js\?v=bclwg51/, 'js stamp must be bclwg51 after CL-APP-09 nav rename');
  assert.ok(!WG_HTML.includes('bclwg46'), 'stale bclwg46 stamp left in weather-map.html');
});
