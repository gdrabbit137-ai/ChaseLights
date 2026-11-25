// CL-APP-09 patch-4: the private-point forecast popup rides the OFFICIAL
// forecast-popup renderers (app.js bridge window.CLForecastRenderers).
// (1) The client solar mirror is byte-for-byte BEHAVIOR-identical to
//     workers/api/src/solar.js (anchor windows must expand the same on both
//     sides — a divergent mirror would give the popup a second truth).
// (2) The notify cron reaches the PRIVATE eval KV (v1:evals:custom:<id>) so
//     a private-point subject-row bell creates a rule the cron can fire —
//     never a dead control.
// Run: node --test apps/web-v2/tests/cl-app-09-popup-renderer-parity.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const cpSrc = readFileSync(join(WEB, 'assets', 'custom-places.js'), 'utf8');

// ------------------------------------------------------- (1) solar mirror
test('CL-APP-09-p4 (1): the client solar mirror matches workers/api/src/solar.js exactly', async () => {
  const begin = cpSrc.indexOf('/* BEGIN SOLAR MIRROR');
  const end = cpSrc.indexOf('/* END SOLAR MIRROR');
  assert.ok(begin >= 0 && end > begin, 'the mirror block markers are present');
  const block = cpSrc.slice(begin, end);
  // Evaluate the mirror in isolation (self-contained: only Math + String padStart)
  const factory = new Function(block + '\nreturn { sunTimesForDate: cpSunTimesForDate };');
  const mirror = factory();
  const worker = await import('file:///' + join(WEB, 'workers', 'api', 'src', 'solar.js').replace(/\\/g, '/'));
  const cases = [
    ['2026-11-16', 23.9412, 121.1523, 8],
    ['2026-12-21', 25.033, 121.5654, 8],
    ['2026-06-21', 25.033, 121.5654, 8],
    ['2026-01-01', 42.6389, 141.3556, 9],
    ['2026-03-11', -33.8688, 151.2093, 10],
    ['2026-12-03', 25.033, 121.5654, 5.5],
  ];
  for (const [date, lat, lng, off] of cases) {
    const a = worker.sunTimesForDate(date, lat, lng, off);
    const b = mirror.sunTimesForDate(date, lat, lng, off);
    assert.deepEqual(b, a, `solar mirror diverges for ${date} (${lat},${lng},${off})`);
  }
  // polar day/night: BOTH sides honestly return null (fail-closed parity)
  const aNull = worker.sunTimesForDate('2026-06-21', 78.22, 15.65, 1); // Svalbard midsummer
  const bNull = mirror.sunTimesForDate('2026-06-21', 78.22, 15.65, 1);
  assert.equal(bNull, aNull);
  assert.equal(bNull, null);
  // segment expansion parity: an anchored segment resolves to the SAME
  // bounds on both sides (the popup never disagrees with the worker)
  const seg = { type: 'after_sunset', offset_minutes: -30 };
  const ctx = { lat: 23.9412, lng: 121.1523, utcOffsetHours: 8 };
  const wa = await import('file:///' + join(WEB, 'workers', 'api', 'src', 'notify.js').replace(/\\/g, '/'));
  const wb = new Function(
    cpSrc.slice(begin, end) +
    '\nvar CP_RESOLVE_SEGMENT_TEST=' + cpSrc.slice(cpSrc.indexOf('function cpResolveSegment'), cpSrc.indexOf('  // mirror of notify.js segmentsOf')) +
    '\nreturn function(seg,date,ctx){return CP_RESOLVE_SEGMENT_TEST.apply(null,arguments);};'
  )();
  for (const date of ['2026-11-16', '2026-06-21', '2026-01-01']) {
    const a = wa.resolveSegmentBounds(seg, date, ctx);
    const b = wb(seg, date, ctx);
    assert.deepEqual(b, a, `segment expansion diverges for ${date}`);
  }
});

// ------------------------------------------------------- (2) cron KV fallback
test('CL-APP-09-p4 (2): the notify cron reaches the PRIVATE eval KV (v1:evals:custom:<id>)', async () => {
  const { runNotifyCron } = await import('file:///' + join(WEB, 'workers', 'api', 'src', 'notify.js').replace(/\\/g, '/'));
  // One instant for date AND hour. Deriving them separately made the fixture
  // point at "today 00:00" between 23:00 and 00:00 Taipei — a slot in the past —
  // so the cron correctly declined and this test red-lit CI only at night.
  const next = new Date(Date.now() + 8 * 3600e3 + 3600e3);
  const d0 = next.toISOString().slice(0, 10);
  const hh = String(next.getUTCHours()).padStart(2, '0') + ':00';
  const customRec = {
    place_id: 'cp-parity-1', private: true, name: '霧社水庫西岸岔路', lat: 23.9412, lng: 121.1523,
    elevation: 1150, timezone: 'Asia/Taipei',
    hourly: [{ local_date: d0, hour: hh, values: { cloud_low: 10, cloud_mid: 20, cloud_high: 30, precipitation: 0, visibility: 20000, wind: 2 } }],
  };
  const kv = new Map([
    // the private eval lives ONLY under the custom prefix
    ['v1:evals:custom:cp-parity-1', JSON.stringify(customRec)],
  ]);
  const execLog = [];
  const db = {
    prepare(sql) {
      return {
        all: async () => ({ results: rulesRows }),
        first: async () => null,
        bind(...args) {
          execLog.push({ sql, args });
          return { run: async () => ({ meta: { changes: 1 } }), all: async () => ({ results: [] }), first: async () => null };
        },
        bind0: null,
      };
    },
  };
  // prepare() must return bind-able statements for INSERT/UPDATE too — shape
  // the stub so every call site gets the same builder.
  const rulesRows = [{
    id: 'r1', user_id: 'u1', place_id: 'cp-parity-1', opportunity_id: null,
    channel: 'push', min_advance_hours: 0,
    custom_conditions: JSON.stringify({ cloud_low_max: 15 }),
  }];
  const db2 = {
    prepare(sql) {
      const base = {
        all: async () => ({ results: sql.includes('notify_rules') ? rulesRows : [] }),
        first: async () => null,
      };
      return Object.assign(base, {
        bind(...args) {
          execLog.push({ sql, args });
          return {
            run: async () => ({ meta: { changes: 1 } }),
            all: async () => ({ results: [] }),
            first: async () => null,
          };
        },
      });
    },
  };
  const summary = await runNotifyCron({ DB: db2, EVALS: { get: async (k) => kv.has(k) ? JSON.parse(kv.get(k)) : null, put: async () => {} } }, Date.now());
  assert.equal(summary.matches, 1, 'the custom-mode rule MATCHED through the private eval KV (without the fallback this is 0)');
  assert.ok(summary.undelivered >= 1, 'delivery fails closed without an FCM secret — but the MATCH is proven');
  const insert = execLog.find((e) => /INSERT INTO notify_log/.test(e.sql));
  assert.ok(insert, 'the dedupe log row was written for the private place');
  assert.equal(insert.args[3], 'cp-parity-1', 'the notify_log row carries the private place id');
  // a rule pointing at a place with NO eval anywhere is skipped honestly
  const rulesRows2 = [Object.assign({}, rulesRows[0], { place_id: 'cp-gone' })];
  const db3 = {
    prepare(sql) {
      return {
        all: async () => ({ results: rulesRows2 }),
        first: async () => null,
        bind() { return { run: async () => ({ meta: { changes: 1 } }), all: async () => ({ results: [] }), first: async () => null }; },
      };
    },
  };
  const summary2 = await runNotifyCron({ DB: db3, EVALS: { get: async () => null, put: async () => {} } }, Date.now());
  assert.equal(summary2.matches, 0, 'no eval record anywhere → the rule is skipped (never fabricated)');
});

// ------------------------------------------------------- (3) bridge contract
test('CL-APP-09-p4 (3): the official renderer bridge exposes ONE implementation per block', () => {
  const appSrc = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
  // the bridge methods delegate to the SAME functions the official surfaces use
  for (const fn of ['mountQuickView', 'v2DayStripHtml', 'v2DaySubHtml', 'v2CondFoldHtml',
    'clSubjectRowLine', 'clTierRowLine', 'evalDayLabels', 'nextWindowStamp',
    'initDragScroll', 'centerSel', 'localDateString', 'localNowMinutes', 'ensureSubjectCards']) {
    const bridgeIdx = appSrc.indexOf('window.CLForecastRenderers=');
    assert.ok(bridgeIdx > 0, 'the bridge exists');
    const after = appSrc.slice(bridgeIdx, bridgeIdx + 2200);
    assert.match(after, new RegExp(fn.replace(/\$/g, '\\$')), `the bridge exposes ${fn} (no re-implementation)`);
  }
  // the official place panel still renders the fold through the shared builder
  assert.match(appSrc, /const v2CondHtml=v2CondFoldHtml\(v2c\?v2c\.conditions:null\);/,
    'openPlaceModal uses the same v2CondFoldHtml (one fold implementation, two hosts)');
});
