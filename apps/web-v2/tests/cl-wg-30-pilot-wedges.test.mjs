// CL-WG-30: pilot wedge presentation semantics (CL-WG-29 design doc).
// 1. The selected-spot label appends the sampled layer value WITH the layer
//    short name (「景點名 · 圖層名 值」), never a bare percentage that could be
//    misread as a coverage score.
// 2. The coverage status badge is honest: full migration reads
//    「遷移完成 N/N（資料仍為 provisional）」, not "all topics covered".
// 3. Opportunities without azimuth data get an explicit "camera only" line
//    instead of a fabricated full-ring Subject sector.
// 4. sectors_monthly geometries are resolved to the current Asia/Taipei
//    month at draw time (CL-DATA-13 mechanism, sectors[month-1] semantics).
// 5. Cache-bust stamp moved to bclwg31 in the same ticket.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

test('CL-WG-30: spot label carries layer short name with the sampled value', () => {
  assert.match(
    JS,
    /selected\.name\} · \$\{selectedCfg\.label\} \$\{formatValue\(value,state\.layer\)\}/,
    'label format: 「name · layerLabel value」',
  );
  assert.doesNotMatch(
    JS,
    /selected\.name\} · \$\{formatValue\(value,state\.layer\)\}/,
    'bare value without layer name must not remain',
  );
});

test('CL-WG-30: full-migration badge is honest (provisional data stated)', () => {
  assert.match(JS, /遷移完成 \$\{migrated\}\/\$\{total\}（資料仍為 provisional）/);
  assert.doesNotMatch(JS, /all topics covered/);
});

test('CL-WG-30: no-azimuth topics state camera-only honestly', () => {
  assert.match(JS, /未建立方位資料，僅顯示機位/);
  assert.match(JS, /不以全向環冒充主體扇/);
});

test('CL-WG-30: sectors_monthly wedges resolve the current month', () => {
  assert.match(JS, /function resolvedSectorArc\(g\)\{[\s\S]*sectors_monthly/);
  assert.match(
    JS,
    /sectors_monthly\.length===12/,
    'the mechanism is the 12-entry CL-DATA-13 sectors array',
  );
  assert.match(
    JS,
    /timeZone:'Asia\/Taipei',month:'numeric'/,
    'month resolution is Asia/Taipei wall clock',
  );
  // Both sector draw paths use the resolved arc.
  const uses = JS.match(/const arc=resolvedSectorArc\(g\);/g) || [];
  assert.equal(uses.length, 2, 'drawGeometry and the envelope sampler both resolve monthly arcs');
});

test('CL-WG-30: cache-bust stamp bumped to bclwg31 in the same ticket', () => {
  assert.match(HTML, /assets\/weather-map\.js\?v=bclwg31/);
  assert.match(HTML, /assets\/weather-map\.css\?v=bclwg31/);
});
