// CL-UI-115 §2 (fog signal) — pins the DOCUMENTED fog behaviour and proves the
// old verdict-list branch was unreachable, so deleting it lost nothing.
//
// Background (reviewer condition 2): the shard's hourly rows carry raw values
// only. Over the committed weather_details shards 0 of 42,048 rows carried a
// `conditions[]` list, so a `fog_visibility` / `in_cloud_fog` FAIL branch could
// never fire. It was removed; the operative signals are visibility < 1 km and
// the fog WMO codes 45 / 48. This file pins that contract:
//   1. the source has no conditions[] branch (no dead verdict path),
//   2. the real shards carry no conditions[] key (evidence for the deletion),
//   3. a REAL foggy hourly row from a real shard makes the branch fire.
// Point 2/3 need weather_details/ (gitignored, absent in a fresh worktree), so
// they skip honestly instead of failing the suite for an environmental reason.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync, existsSync} from 'node:fs';
import {join} from 'node:path';

const ROOT = new URL('../../..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const APP = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');

const slice = (start, end) => {
  const i = APP.indexOf(start);
  const j = APP.indexOf(end, i);
  assert.ok(i > 0 && j > i, `slice ${start} → ${end}`);
  return APP.slice(i, j);
};

// The shipped helper, re-run exactly as the page runs it (no re-derived logic).
const fogFn = new Function(
  `${slice('function clui115NowFog', 'function clui115NowHourLabel')}
   return clui115NowFog;`)();

test('CL-UI-115 §2 (fog): the source has no conditions[] verdict branch', () => {
  const body = slice('function clui115NowFog', 'function clui115NowHourLabel');
  assert.doesNotMatch(body, /conditions/, 'no dead conditions[] branch survives');
  assert.doesNotMatch(body, /fog_visibility|in_cloud_fog/, 'no unreachable metric-verdict path survives');
  assert.match(body, /vis<1/, 'visibility < 1 km is an operative signal');
  assert.match(body, /code===45\|\|code===48/, 'the fog WMO codes are operative signals');
});

test('CL-UI-115 §2 (fog): visibility and WMO are the only two documented signals', () => {
  assert.equal(fogFn({visibility: 0.3, weather_code: 55}), true, '0.3 km fog');
  assert.equal(fogFn({visibility: 1.4, weather_code: 3}), false, 'clear hour is not fog');
  assert.equal(fogFn({visibility: 1, weather_code: 3}), false, 'exactly 1.0 km is the boundary');
  assert.equal(fogFn({visibility: 12, weather_code: 45}), true, 'WMO 45');
  assert.equal(fogFn({visibility: 12, weather_code: 48}), true, 'WMO 48');
  assert.equal(fogFn(null), false, 'no row → no fog');
  // A conditions[] list that no shard can carry must not change the verdict.
  assert.equal(fogFn({visibility: 20, weather_code: 0, conditions: [{metric: 'fog_visibility', verdict: 'FAIL'}]}), false,
    'a conditions[] list is ignored — it is not a data-layer field');
});

const DETAILS = join(ROOT, 'weather_details');
const hasShards = existsSync(join(DETAILS, 'tw'));

test('CL-UI-115 §2 (fog): the committed shards carry raw values only — no conditions[]', {skip: hasShards ? false : 'weather_details/ is not present in this checkout'}, () => {
  const dir = join(DETAILS, 'tw');
  const files = readdirSync(dir).filter(f => f.endsWith('.json'));
  assert.ok(files.length >= 50, `the tw shard set is complete (got ${files.length})`);
  let rows = 0, withConditions = 0;
  for (const f of files) {
    const payload = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    for (const r of (payload.spot && payload.spot.hourly_forecast) || []) {
      rows++;
      if (r && Object.prototype.hasOwnProperty.call(r, 'conditions')) withConditions++;
    }
  }
  assert.ok(rows > 10000, `sampled a real row population (got ${rows})`);
  assert.equal(withConditions, 0, `no hourly row carries conditions[] (checked ${rows} rows)`);
});

test('CL-UI-115 §2 (fog): a REAL shard row fires the fog branch', {skip: hasShards ? false : 'weather_details/ is not present in this checkout'}, () => {
  const dir = join(DETAILS, 'tw');
  const files = readdirSync(dir).filter(f => f.endsWith('.json')).sort();
  let hit = null;
  for (const f of files) {
    const payload = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    for (const r of (payload.spot && payload.spot.hourly_forecast) || []) {
      if (fogFn(r)) { hit = {file: f, row: r}; break; }
    }
    if (hit) break;
  }
  assert.ok(hit, 'the committed forecast contains at least one foggy hour (it does every season)');
  const vis = Number(hit.row.visibility);
  const code = Number(hit.row.weather_code);
  assert.ok((Number.isFinite(vis) && vis < 1) || code === 45 || code === 48,
    `the real foggy row qualifies on a documented signal (${hit.file} ${hit.row.time} vis=${vis} code=${code})`);
});
