// CL-UI-115 §2 (fog signal) — pins the DOCUMENTED fog behaviour and proves the
// old verdict-list branch was unreachable, so deleting it lost nothing.
//
// Background (reviewer condition 2): the shard's hourly rows carry raw values
// only. Over the committed weather_details shards 0 of 42,048 rows carried a
// `conditions[]` list, so a `fog_visibility` / `in_cloud_fog` FAIL branch could
// never fire. It was removed; the operative signals are visibility < 1 km and
// the fog WMO codes 45 / 48. This file pins that contract:
//   1. the source has no conditions[] branch (no dead verdict path),
//   2. the two documented signals are the only ones,
//   3. a foggy hourly row in the REAL shard SHAPE makes the branch fire and the
//      chip render its fog state — proven from a committed fixture, so the
//      contract is verifiable in CI (weather_details/ is gitignored and absent
//      on a runner),
//   4. the live-shard census (0 of 42,048 rows carry `conditions[]`) still runs
//      where the shards exist and skips honestly where they do not.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync, existsSync} from 'node:fs';
import {join} from 'node:path';

const ROOT = new URL('../../..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const APP = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');
// CI-provable evidence: one hourly row, visibility 0.1 km, WMO 45, in the
// minimal shard shape the loader reads (schema_version + updated_at + region +
// spot.hourly_forecast). Committed, so a fresh checkout and CI both have it.
const FIXTURE = JSON.parse(readFileSync(new URL('./fixtures/cl-ui-115-fog-hour.json', import.meta.url), 'utf8'));


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

// The shipped now-chip renderer, sliced the same way the CL-UI-115 §2 harness
// does it, with only its immediate dependencies supplied.
const chipFn = (() => {
  const prelude = `
    const DICT={clui115_fog_now:'目前起霧，能見度低',vis_cap:'≥ 24 km（資料上限）'};
    const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const d=()=>DICT;
    const currentTempUnit='C';
    const formatTemp=c=>{ if(c==null||c===''||Number.isNaN(Number(c)))return '—'; return (Math.round(Number(c)*10)/10)+'°C'; };
    const visibilityText=km=>{ if(km==null||km==='')return null; const n=Number(km); if(!Number.isFinite(n))return null; if(n>=24.1)return DICT.vis_cap; return n+' km'; };
    const clIconSvg=k=>'<svg data-cl-icon="'+k+'" aria-hidden="true"></svg>';
    const wmoWord=()=>'霧';
    const wmoIcon=()=>'<svg data-cl-icon="45" aria-hidden="true"></svg>';
  `;
  const body = slice('function clui115LocalParts', 'function trMessage');
  return new Function(`${prelude}\n${body}\nreturn clui115NowChipHtml;`)();
})();


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

test('CL-UI-115 §2 (fog): the committed fixture is a valid shard and its foggy hour fires the branch', () => {
  // The fixture must be loadable by the SAME loader the page uses: the schema
  // range app.js accepts, a version stamp, and spot.hourly_forecast rows.
  const minSchema = Number((APP.match(/MIN_SCHEMA_VERSION=(\d+)/) || [])[1]);
  const maxSchema = Number((APP.match(/MAX_SCHEMA_VERSION=(\d+)/) || [])[1]);
  assert.ok(Number.isFinite(minSchema) && Number.isFinite(maxSchema), 'app.js declares its schema range');
  assert.ok(FIXTURE.schema_version >= minSchema && FIXTURE.schema_version <= maxSchema,
    `fixture schema_version ${FIXTURE.schema_version} is inside ${minSchema}-${maxSchema} (the loader rejects anything else)`);
  assert.ok(typeof FIXTURE.updated_at === 'string' && FIXTURE.updated_at, 'fixture carries updated_at (loadDetails version match)');
  assert.equal(FIXTURE.region, 'tw', 'fixture names its region (weather_details/<region>/<spot>.json)');
  const rows = FIXTURE.spot && FIXTURE.spot.hourly_forecast;
  assert.ok(Array.isArray(rows) && rows.length === 1, 'the fixture holds ONE hourly row');
  const row = rows[0];
  // Raw values only — the field the deleted branch needed is NOT there.
  assert.equal(Object.prototype.hasOwnProperty.call(row, 'conditions'), false, 'the row carries no conditions[] list');
  assert.equal(Number(row.visibility), 0.1, 'visibility 0.1 km');
  assert.equal(Number(row.weather_code), 45, 'WMO 45 (fog)');
  assert.ok(row.time && row.local_date, 'row carries the timestamps the loader/hour-picker read');
  // The branch fires on each documented signal of this one row.
  assert.equal(fogFn(row), true, 'the fixture row fires the fog branch');
  assert.equal(fogFn({visibility: row.visibility, weather_code: 3}), true, 'visibility alone is enough');
  assert.equal(fogFn({visibility: 20, weather_code: row.weather_code}), true, 'WMO 45 alone is enough');
  // …and the shipped chip renders the fog state from that row (class + reason),
  // at the instant that makes the row the place-local "now" (2026-11-15 02:20).
  const html = chipFn(rows, FIXTURE.spot.timezone, Date.UTC(2026, 10, 14, 18, 20));
  assert.match(html, /data-now-hour="02:00"/, 'the chip labels the foggy hour');
  assert.match(html, /cl-now-fog/, 'the fog state is a CLASS (CSS owns the amber tint)');
  assert.match(html, /data-now-fog="1"/, 'the chip is addressable as fog');
  assert.match(html, /目前起霧/, 'the reason text rides the chip');
  assert.match(html, /0\.1 km/, 'the chip shows the visibility that caused it');
});

const DETAILS = join(ROOT, 'weather_details');
const hasShards = existsSync(join(DETAILS, 'tw'));

test('CL-UI-115 §2 (fog): the committed shards carry raw values only — no conditions[]', {skip: hasShards ? false : 'weather_details/ is not present in this checkout (gitignored; the fixture above proves the contract in CI)'}, () => {
  const dir = join(DETAILS, 'tw');
  const files = readdirSync(dir).filter(f => f.endsWith('.json'));
  assert.ok(files.length >= 50, `the tw shard set is complete (got ${files.length})`);
  let rows = 0, withConditions = 0, foggyRows = 0;
  for (const f of files) {
    const payload = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    for (const r of (payload.spot && payload.spot.hourly_forecast) || []) {
      rows++;
      if (r && Object.prototype.hasOwnProperty.call(r, 'conditions')) withConditions++;
      if (fogFn(r)) foggyRows++;
    }
  }
  assert.ok(rows > 10000, `sampled a real row population (got ${rows})`);
  assert.equal(withConditions, 0, `no hourly row carries conditions[] (checked ${rows} rows)`);
  // The same shape as the fixture occurs in the live data (a foggy hour exists
  // in every season), so the fixture is not a synthetic outlier.
  assert.ok(foggyRows > 0, `the live shards contain foggy hours (${foggyRows} of ${rows} rows)`);
});

