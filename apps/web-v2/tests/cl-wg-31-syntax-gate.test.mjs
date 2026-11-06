// CL-WG-31 regression gate: assets/weather-map.js must always be syntactically
// valid and must never again contain orphan-comma slots in the WM_I18N
// dictionaries. CL-CI-20's merge deleted VNP46A4-era entries but left empty
// `,\n\n,` slots behind, producing a top-level SyntaxError that killed the
// entire WeatherGrid page (white screen) in production.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const ROOT = path.resolve(import.meta.dirname, '../../..');
const JS_PATH = path.join(ROOT, 'assets/weather-map.js');
const source = fs.readFileSync(JS_PATH, 'utf8');

test('CL-WG-31: assets/weather-map.js parses with node --check', () => {
  const res = spawnSync(process.execPath, ['--check', JS_PATH], {
    encoding: 'utf8',
  });
  const detail = (res.stderr || '') + (res.stdout || '');
  assert.strictEqual(
    res.status,
    0,
    `node --check failed on assets/weather-map.js:\n${detail}`
  );
});

test('CL-WG-31: no orphan comma lines (empty dictionary entries)', () => {
  const lines = source.split(/\r?\n/);
  const offenders = [];
  for (let i = 0; i < lines.length; i++) {
    if (!/^\s*,\s*$/.test(lines[i])) continue;
    const prev = i > 0 ? lines[i - 1] : '';
    const next = i + 1 < lines.length ? lines[i + 1] : '';
    // A bare comma separator line is only valid when squeezed between two
    // complete entries (key line on BOTH sides). Adjacent blank line or
    // another bare comma means an empty/corrupted entry slot.
    if (!/\S/.test(prev) || !/\S/.test(next) || /^\s*,\s*$/.test(next)) {
      offenders.push(i + 1);
    }
  }
  assert.deepStrictEqual(
    offenders,
    [],
    `orphan comma lines (empty entry slots) at: ${offenders.join(', ')}`
  );
});

test('CL-WG-31: weather-map.html pins bumped stamp matches gate', () => {
  const html = fs.readFileSync(
    path.join(ROOT, 'weather-map.html'),
    'utf8'
  );
  const m = html.match(/assets\/weather-map\.js\?v=(bclwg\d+)/);
  assert.ok(m, 'weather-map.html must pin assets/weather-map.js with ?v=bclwgNN');
  assert.notStrictEqual(
    m[1],
    'bclwg32',
    'weather-map.js content changed in CL-WG-31; stamp must be bumped past bclwg32'
  );
});
