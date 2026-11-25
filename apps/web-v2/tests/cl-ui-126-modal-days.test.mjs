// CL-UI-126 (owner phone report): the forecast modal's daily list showed 「昨天」
// and repeated dates. The evaluation bundle keeps PAST day rows and can repeat a
// local_date between refreshes, so any positional read pairs today's tab with a
// yesterday row. The fix is ONE pure normaliser — modalDays(days, todayKey) —
// that every surface (modal summary rows, eval day strip, private popup) uses.
//
// Contract: build from the spot's local today; drop every day whose local_date
// is before today; de-duplicate by local_date (first row wins); return exactly
// DAY_KEYS.length slots for today..today+6, ascending, with null for a slot the
// bundle cannot cover. Index i therefore always means "today + i" — the same key
// the date tabs above the list are built from.
//
// Run: node --test apps/web-v2/tests/cl-ui-126-modal-days.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');

const grab = (start, end) => {
  const a = appSource.indexOf(start);
  assert.ok(a !== -1, `slice start not found: ${start}`);
  const b = appSource.indexOf(end, a);
  assert.ok(b !== -1, `slice end not found: ${end}`);
  return appSource.slice(a, b);
};

const factory = new Function([
  "const DAY_KEYS=['today','tomorrow','after_tomorrow','day3','day4','day5','day6'];",
  grab('function modalDays', 'function modalSummaryData'),
  'return {modalDays};'
].join('\n'));
const { modalDays } = factory();

const day = (date, extra = {}) => ({ local_date: date, state: 'UNFAVORABLE', good_hours: [], ...extra });
const dates = (out) => out.map((d) => (d ? d.local_date : null));

test('CL-UI-126 (1): a yesterday row is dropped — today is always slot 0', () => {
  const out = modalDays([
    day('2026-11-25', { tag: 'yesterday' }),
    day('2026-11-26', { tag: 'today' }),
    day('2026-11-27', { tag: 'tomorrow' })
  ], '2026-11-26');
  assert.equal(out.length, 7, 'always seven slots');
  assert.equal(out[0].tag, 'today', 'slot 0 is today, never the stale first row');
  assert.equal(out[1].tag, 'tomorrow');
  assert.equal(dates(out).includes('2026-11-25'), false, 'the past row is gone');
});

test('CL-UI-126 (2): a duplicated local_date collapses to ONE entry (first row wins)', () => {
  const out = modalDays([
    day('2026-11-27', { tag: 'dup-first' }),
    day('2026-11-27', { tag: 'dup-second' }),
    day('2026-11-26', { tag: 'today' })
  ], '2026-11-26');
  assert.equal(out.filter((d) => d && d.local_date === '2026-11-27').length, 1,
    'one entry per local_date');
  assert.equal(out[1].tag, 'dup-first', 'the first row for that date wins');
  assert.equal(new Set(dates(out).filter(Boolean)).size, 2, 'no repeated date in the list');
});

test('CL-UI-126 (3): an out-of-order bundle is re-sorted into today..today+6', () => {
  const out = modalDays([
    day('2026-11-29', { tag: 'd3' }),
    day('2026-11-27', { tag: 'd1' }),
    day('2026-11-26', { tag: 'd0' }),
    day('2026-11-28', { tag: 'd2' })
  ], '2026-11-26');
  assert.deepEqual(dates(out), [
    '2026-11-26', '2026-11-27', '2026-11-28', '2026-11-29', null, null, null
  ], 'ascending slots keyed to today+offset');
  assert.deepEqual(out.filter(Boolean).map((d) => d.tag), ['d0', 'd1', 'd2', 'd3'],
    'row content follows its own date, not the array index');
});

test('CL-UI-126 (4): exactly seven slots, with null for a day the bundle cannot cover', () => {
  const out = modalDays([
    day('2026-11-26'),
    day('2026-11-28'),
    day('2026-12-20') // beyond today+6 → not part of the list
  ], '2026-11-26');
  assert.equal(out.length, 7);
  assert.equal(out[5], null, 'a missing future day stays empty — never borrowed from the tail');
  assert.equal(out[6], null);
  assert.ok(!dates(out).includes('2026-12-20'), 'days past today+6 are outside the tab window');
});

test('CL-UI-126 (5): the slot keys roll over month/year boundaries', () => {
  const out = modalDays([day('2026-12-06', { tag: 'last' })], '2026-11-30');
  assert.equal(out[6].tag, 'last', 'today+6 = 12/06 across the month boundary');
  const year = modalDays([day('2027-01-02', { tag: 'ny' })], '2026-12-27');
  assert.equal(year[6].tag, 'ny', 'today+6 = 2027-01-02 across the year boundary');
});

test('CL-UI-126 (6): malformed rows and an unresolvable today fail closed to null slots', () => {
  const out = modalDays([day(''), { local_date: null }, null, { local_date: '2026-11-26' }, day('2026-11-27')], '2026-11-26');
  assert.equal(out[0].local_date, '2026-11-26');
  assert.equal(out[1].local_date, '2026-11-27');
  assert.deepEqual(modalDays([day('2026-11-26')], ''), Array(7).fill(null),
    'no local today → no list');
  assert.deepEqual(modalDays(null, '2026-11-26'), Array(7).fill(null),
    'no days → seven empty slots');
});

test('CL-UI-126 (7): both list surfaces consume the same normaliser', () => {
  const modal = grab('function modalSummaryData', 'function modalDayRow');
  assert.match(modal, /modalDays\(opp\.days,localDateString\(tz\|\|'UTC',0\)\)/,
    'modal summary rows go through modalDays');
  const strip = appSource.slice(appSource.indexOf('const aligned=modalDays(opp.days,localDateString(tzStrip,0));'));
  assert.ok(strip.length > 0, 'the eval day strip goes through modalDays too');
  assert.ok(!/v2DayForOffset\(opp,_i,tzStrip\)/.test(appSource),
    'no surface re-resolves the day by array offset anymore');
  assert.match(appSource, /modalDays:function\(days,todayKey\)\{return modalDays\(days,todayKey\);\}/,
    'the private-place popup reaches the same normaliser through the renderer bridge');
});
