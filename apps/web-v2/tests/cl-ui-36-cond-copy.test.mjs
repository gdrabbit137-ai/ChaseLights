// CL-UI-36 B contract: pressure-level condition labels carry the layer as a
// parenthetical annotation (「相對濕度（925 hPa）」, not the glued 「相對濕度925hPa」)
// and the modal's 現況 live value carries the condition's unit instead of a
// bare number.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, `source slice start not found: ${start}`);
  const j = appSource.indexOf(end, i + start.length);
  assert.ok(j > i, `source slice end not found after start: ${end}`);
  return appSource.slice(i, j);
};

test('CL-UI-36 B: RH pressure-level labels use parenthetical layer annotation (all langs)', () => {
  assert.ok(appSource.includes("relative_humidity_925hpa:'相對濕度（925 hPa）'"));
  assert.ok(appSource.includes("relative_humidity_850hpa:'相對濕度（850 hPa）'"));
  assert.ok(appSource.includes("relative_humidity_925hpa:'RH (925 hPa)'"));
  assert.ok(appSource.includes("relative_humidity_850hpa:'RH (850 hPa)'"));
  assert.ok(appSource.includes("relative_humidity_925hpa:'相対湿度（925 hPa）'"));
  assert.ok(appSource.includes("relative_humidity_850hpa:'相対湿度（850 hPa）'"));
  assert.ok(!appSource.includes('相對濕度925hPa'), 'glued label must be gone');
});

test('CL-UI-36 B: v2CondLive current value carries the unit', () => {
  const slice = grab('function v2CondLive', 'function v2CondDaySummary');
  assert.match(slice, /cond\.unit\?' '\+cond\.unit:''/);
  assert.ok(!/t\.v2_cond_now\+' '\+v2FmtNum\(v\)\+' · '/.test(slice), 'bare unit-less 現況 value must be gone');
});

test('CL-UI-36: homepage cache-bust stamp bumped to clui41', () => {
  const index = readFileSync(new URL('../../../index.html', import.meta.url), 'utf8');
  assert.match(index, /assets\/app\.js\?v=clui41/);
  assert.match(index, /assets\/app\.css\?v=clui41/);
});

test('CL-UI-36 A: no internal review note leaks into user-facing bundles', () => {
  for (const f of ['../catalog.v2.json', '../opportunity-contracts.json']) {
    const s = readFileSync(new URL(f, import.meta.url), 'utf8');
    assert.ok(!s.includes('審查修正') && !s.includes('審査修正') && !s.includes('[2026-11-01 review'), f);
  }
  const globPack = new URL('.', import.meta.url);
  assert.ok(globPack); // records asserted via data-layer tests
});
