// CL-WG-28: redesigned WeatherGrid legend + cursor value readout.
//
// Owner ruling (reversal of the remove-legend ticket): Windy has no legend and
// that is a long-running community complaint, so OUR legend is a
// differentiator — but it must be restrained. Compact state = one slim
// gradient bar + ONLY the first/last value labels; click/tap (or a 500ms
// long-press on touch) expands the full tick detail. The cursor readout is
// the PRIMARY value-query channel; the legend is an aid. The legend only
// renders while the active layer has decodable data.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.js'), 'utf8');
const CSS = fs.readFileSync(path.join(ROOT, 'assets/weather-map.css'), 'utf8');
const HTML = fs.readFileSync(path.join(ROOT, 'weather-map.html'), 'utf8');

test('CL-WG-28 legend compact state: slim bar + first/last labels only, expandable', () => {
  // The gradient bar row is a real toggle button carrying aria-expanded.
  assert.match(JS, /class="legend-toggle" aria-expanded=/);
  // Compact labels row renders exactly two spans (first/last of the label list).
  assert.match(JS, /legend-compact-labels"><span>\$\{escapeHtml\(labels\[0\]\)\}<\/span><span>\$\{escapeHtml\(labels\[labels\.length-1\]\)\}<\/span><\/span>/);
  // Full tick detail lives in a hidden-by-default expanded panel.
  assert.match(JS, /class="legend-expanded"\$\{state\.legendExpanded\?'':' hidden'\}/);
  assert.match(CSS, /\.legend-expanded\[hidden]\{display:none\}/);
  // Click toggles; touch gets a 500ms long-press that suppresses the click.
  assert.match(JS, /function toggleLegendExpanded\(/);
  assert.match(JS, /function attachLegendLongPress\(/);
  assert.match(JS, /if\(longPressed\)\{ longPressed=false; return; \}/);
  assert.match(CSS, /\.legend-compact-labels\{display:flex;justify-content:space-between/);
});

test('CL-WG-28 legend content derives from the palette module, never hand-copied', () => {
  // Cloud ramps come straight from the palette band tables.
  assert.match(JS, /cloudLegendGradient\(bands\)/);
  assert.match(JS, /cfg\.palette==='cloudLow'\?LOW_CLOUD_PERCENT_BANDS:CLOUD_PERCENT_BANDS/);
  // Non-cloud gradients sample the palette's colorFor at the config ticks.
  assert.match(JS, /stopValues\.map\(v=>colorFor\(v,cfg\)\)/);
  // All-weather-layer inventory: one updateLegend renders every layer's
  // legend from LAYER_RENDER_CONFIG-derived cfg (no per-layer hand copies).
  assert.match(JS, /const hasData=decodedArray\(state\.layer\)\.some\(Number\.isFinite\)/);
  assert.match(JS, /\$\('legend'\)\.hidden=!hasData/);
});

test('CL-WG-28 cloud 50% hinge keeps its one-line key + midline marker', () => {
  assert.match(JS, /50% 雲量分界/);
  assert.match(JS, /<span class="cloud-midline" aria-hidden="true"><\/span>/);
  assert.match(CSS, /\.cloud-midline\{position:absolute;left:50%/);
});

test('CL-WG-28 cursor value readout exists and is the primary value channel', () => {
  assert.match(HTML, /id="cursor-readout"/);
  assert.match(JS, /function wireCursorReadout\(/);
  assert.match(JS, /host\.addEventListener\('pointermove',updateCursorReadout\)/);
  assert.match(JS, /host\.addEventListener\('pointerleave',hideCursorReadout\)/);
  // Reuses the SAME sampler the spot inspector uses — no second value path.
  assert.match(JS, /const value=samplePointValue\(\{lon:p\.lon,lat:p\.lat\},state\.layer\)/);
  // Honest degradation: outside bbox or missing cell hides the readout.
  assert.match(JS, /if\(!Number\.isFinite\(value\)\)\{\s*el\.hidden=true;\s*return;\s*\}/);
  assert.match(CSS, /\.cursor-readout\{position:absolute;z-index:7;[^}]*pointer-events:none/);
});
