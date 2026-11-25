// CL-UI-124 (owner bug 2026-11-24): the modal's 8-day strip mislabelled every
// cell. The evaluation bundle keeps PAST days inside opp.days, so the strip's
// `opp.days.slice(0, 7)` paired a five-day-old row with the label 「今天」 —
// every past day has zero remaining hours, so the owner saw 「✓0」 on 今天,
// 明天, 後天, 11/27 and 11/28, while 11/29 showed tomorrow's six hours.
// The strip must align by DATE (v2DayForOffset) and drop days it cannot cover.
// Run: node --test apps/web-v2/tests/cl-ui-124-strip-day-alignment.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const bundle = JSON.parse(readFileSync(join(WEB, 'apps', 'web-v2', 'evaluations-latest.json'), 'utf8'));

test('CL-UI-124 (1): the modal strip aligns days by DATE, never by array index', () => {
  assert.ok(!/opp\.days\.slice\(0,\s*DAY_KEYS\.length\)/.test(appSource),
    'the index slice that shifted every label is gone');
  // CL-UI-126: both day-list surfaces now go through ONE normaliser
  // (modalDays: local today..today+6, past rows dropped, duplicate
  // local_date collapsed) instead of each resolving offsets inline.
  assert.match(appSource, /function modalDays\(days,todayKey\)\{[\s\S]{0,900}DAY_KEYS\.forEach/,
    'the normaliser builds one slot per tab key');
  const strip = appSource.slice(appSource.indexOf('const aligned=modalDays(opp.days,localDateString(tzStrip,0));'));
  assert.match(strip, /aligned\.forEach\(\(_d,_i\)=>\{\s*\n\s*if\(!_d\)return;/,
    'a day the bundle cannot cover is skipped instead of being borrowed from the tail');
  assert.match(strip, /days\.push\(_d\);labels\.push\(labelsAll\[_i\]\);/, 
    'the day and its label are pushed together (they cannot drift apart)');
});

test('CL-UI-124 (2): v2DayForOffset resolves by local_date first, and only then falls back', () => {
  assert.match(appSource, /function v2DayForOffset\(opp,offsetDays,tz\)\{[\s\S]{0,220}const byDate=days\.find\(day=>day&&day\.local_date===target\);/,
    'the date lookup wins over any positional guess');
});

test('CL-UI-124 (3): bundle days are date-ascending and unique per opportunity', () => {
  let checked = 0;
  for (const place of bundle.places || []) {
    for (const opp of place.opportunities || []) {
      const days = (opp.days || []).map((d) => d && d.local_date).filter(Boolean);
      if (!days.length) continue;
      assert.deepEqual(days.slice().sort(), days, `${place.place_id}/${opp.opportunity_id}: days are date-ascending`);
      assert.equal(new Set(days).size, days.length, `${place.place_id}/${opp.opportunity_id}: no duplicate local_date`);
      checked += 1;
    }
  }
  assert.ok(checked > 0, 'the bundle actually carries day rows');
});

test('CL-UI-124 (4): a satisfied day with zero effective hours is only possible TODAY', () => {
  // A future day keeps its full hour list (v2EffectiveHours only trims TODAY),
  // so the old 「✓0」 on 明天..11/28 could only come from showing a PAST row.
  // Guard the premise of that reasoning.
  assert.match(appSource, /if\(!v2IsToday\(day,tz\)\)return \(day\.good_hours\|\|\[\]\)\.filter\(t=>\/\^\(\[01\]\\d\|2\[0-3\]\):\[0-5\]\\d\$\/\.test\(String\(t\|\|''\)\)\);/,
    'non-today days are not trimmed by the current clock');
});
