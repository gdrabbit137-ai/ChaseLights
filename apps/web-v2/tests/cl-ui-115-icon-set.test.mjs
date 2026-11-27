// CL-UI-115 §1 — one inline SVG icon set for every metric/weather glyph.
//
// Why: every metric/weather symbol used to be an emoji literal baked into
// assets/app.js, so the same codepoint was drawn by a different font on Windows,
// macOS, Android and iOS (the owner saw a sharp eye on desktop, a soft one on
// the phone). There was no second code path — only the platform emoji font.
//
// This file pins the CONTRACT of assets/icons.js and the fact that app.js routes
// its metric/weather positions through it:
//   - frozen CL_ICONS map, currentColor strokes, no hard-coded fill, no width/height
//   - a key for every WMO code in app.js, every subject in the label table, plus
//     the twelve metric keys
//   - clIcon(key) falls back to the historical emoji for an unknown key
//   - .cl-icon is a 1em box with a fixed baseline offset (no layout shift)
//   - no emoji left in a metric/weather render position in app.js
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const iconSource=readFileSync(new URL('../../../assets/icons.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const indexSource=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');

// Load the shipped icon set the way the browser does (a plain script that
// assigns onto its global), then inspect the REAL map, not a copy of it.
const sandbox={window:{},Object,Number,String,isFinite,RegExp};
vm.createContext(sandbox);
vm.runInContext(iconSource.replace(/^\(function \(root\)/,'(function (root)'), sandbox);
const G=sandbox.window;
assert.ok(G.CL_ICONS&&G.clIcon,'assets/icons.js publishes CL_ICONS + clIcon onto the global');

const WMO_CODES=(()=>{
  const table=appSource.slice(appSource.indexOf('const WMO_ICON_FALLBACK='),appSource.indexOf('function clIconSvg'));
  return [...table.matchAll(/(\d+):'/g)].map(m=>m[1]);
})();
const SUBJECT_KEYS=(()=>{
  const start=appSource.indexOf('const themeLabels = {');
  const block=appSource.slice(start,appSource.indexOf('\n    };',start));
  const zh=block.slice(block.indexOf("'zh-TW':{")+9,block.indexOf('},',block.indexOf("'zh-TW':{")));
  return [...zh.matchAll(/(?:^|,)([a-z_]+):'/g)].map(m=>m[1]);
})();
const METRIC_KEYS=['visibility','cloud','fog','wind','humidity','temperature','elevation','azimuth','sunrise','sunset','moon','star'];

test('CL-UI-115 §1: CL_ICONS is a frozen map of currentColor-stroke SVGs',()=>{
  assert.ok(Object.isFrozen(G.CL_ICONS),'CL_ICONS is frozen');
  const keys=Object.keys(G.CL_ICONS);
  assert.ok(keys.length>=60,`the set carries the whole table (got ${keys.length} keys)`);
  for(const key of keys){
    const svg=G.CL_ICONS[key];
    assert.match(svg,/^<svg /,`${key}: is an inline <svg>`);
    assert.match(svg,/data-cl-icon="/,`${key}: is addressable by data-cl-icon`);
    assert.match(svg,/stroke="currentColor"/,`${key}: strokes currentColor so CSS can tint it`);
    assert.doesNotMatch(svg,/\swidth="|\sheight="/,`${key}: no inline width/height — the CSS box owns the size`);
    assert.doesNotMatch(svg,/fill="(?!none")/,`${key}: no hard-coded fill colour`);
    assert.match(svg,/aria-hidden="true"/,`${key}: decorative glyph is hidden from AT (the text label carries the name)`);
  }
});

test('CL-UI-115 §1: every WMO code, subject and metric key has a glyph',()=>{
  assert.ok(WMO_CODES.length>=28,`app.js carries the full WMO table (got ${WMO_CODES.length} codes)`);
  for(const code of WMO_CODES){
    assert.ok(G.CL_ICONS[code],`WMO ${code} has an icon`);
    assert.equal(G.clIconKeyForWmo(code)!==null,true,`WMO ${code} maps to a shape`);
  }
  assert.equal(SUBJECT_KEYS.length,23,`the subject label table has 23 subjects (got ${SUBJECT_KEYS.length})`);
  for(const key of SUBJECT_KEYS) assert.ok(G.CL_ICONS[key],`subject ${key} has an icon`);
  for(const key of METRIC_KEYS) assert.ok(G.CL_ICONS[key],`metric ${key} has an icon`);
});

test('CL-UI-115 §1: an unknown key still renders something (emoji fallback data)',()=>{
  // A WMO code the forecast adds tomorrow, an unmapped named metric, a null.
  assert.equal(G.clIcon('12'),'☁️','an unknown numeric code falls back to the range emoji, never blank');
  assert.equal(G.clIcon('999'),'⛈️','unknown severe codes keep the storm emoji');
  assert.equal(G.clIcon('not_a_key'),'','a fully unknown named key degrades to empty, never to "[object Object]"');
  assert.equal(G.clIcon(null),'','null is handled without throwing');
  // …and a KNOWN key never returns the emoji any more.
  assert.match(G.clIcon('visibility'),/^<svg /,'visibility resolves to the SVG, not 👁');
  for(const code of WMO_CODES) assert.match(G.clIcon(code),/^<svg /,`WMO ${code} resolves to the SVG`);
});

test('CL-UI-115 §1: app.js routes every metric/weather position through the icon set',()=>{
  // The lookup helper is typeof-guarded so extracted test slices stay self-contained.
  assert.match(appSource,/function clIconSvg\(key\)\{[\s\S]*?typeof clIcon==='function'/, 'the helper guards the global lookup');
  assert.match(appSource,/function wmoIcon\(code\)\{[\s\S]*?clIconSvg\(String\(c\)\)/, 'wmoIcon reads the icon set');
  assert.match(appSource,/const cloudChip=clBaseTxt\?`<span class="metric-chip">\$\{clIconSvg\('cloud'\)\}/, 'the cloud-base chip uses the cloud icon');
  assert.match(appSource,/const clElevPill=clElev!=null\?`<span class="metric-chip">\$\{clIconSvg\('elevation'\)\}/, 'the elevation pill uses the elevation icon');
  assert.match(appSource,/\$\{clIconSvg\('visibility'\)\} \$\{esc\(vt\)\}/, 'the visibility value carries the eye icon');
  assert.match(appSource,/function tempChipHtml\(temp\)[\s\S]*?clIconSvg\('temperature'\)/, 'the temperature chip uses the temperature icon');
  // Emoji survive ONLY as fallback data: the render positions may not carry one.
  for(const literal of ['`👁 ','>☁️ ${esc(clBaseTxt)', '>⛰ ${clElev}', '>🌡 ${esc(t)}', "'☀ ${Math.round(metric.sun_azimuth)}"]){
    assert.ok(!appSource.includes(literal),`no emoji metric glyph "${literal}" remains in a render position`);
  }
});

test('CL-UI-115 §1: .cl-icon is a 1em box with a fixed baseline offset',()=>{
  const rule=cssSource.match(/\.cl-icon \{[^}]*\}/);
  assert.ok(rule,'app.css defines .cl-icon');
  assert.match(rule[0],/width:\s*1em/);
  assert.match(rule[0],/height:\s*1em/);
  assert.match(rule[0],/vertical-align:\s*-0\.125em/);
  assert.match(rule[0],/stroke:\s*currentColor/);
  assert.match(rule[0],/fill:\s*none/);
});

test('CL-UI-115 §1: icons.js loads before app.js with a cache stamp',()=>{
  assert.match(indexSource,/assets\/icons\.js\?v=clui\d+/,'index.html stamps the icon set');
  assert.ok(indexSource.indexOf('assets/icons.js')<indexSource.indexOf('assets/app.js'),'icons.js loads first');
});
