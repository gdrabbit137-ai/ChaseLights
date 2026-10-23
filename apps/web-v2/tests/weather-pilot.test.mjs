import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {validateArtifact, retrievalAgeSeconds, staleness, formatHourAsiaTaipei,
  render, COPY, FIELD_LABELS, LOCALES} from '../weather-pilot.mjs';

const artifact = JSON.parse(readFileSync(
  fileURLToPath(new URL('../weather-pilot-tw036.json', import.meta.url)), 'utf8'));

test('real pilot artifact validates', () => {
  assert.equal(validateArtifact(artifact).place_id, 'tw-036');
});

test('identity mismatches fail closed', () => {
  for (const key of ['pilot_id', 'place_id', 'pilot_binding_sha256']) {
    const copy = structuredClone(artifact);
    copy[key] = 'x';
    assert.throws(() => validateArtifact(copy), /IDENTITY_MISMATCH|STATE_NOT_RESEARCH_RAW/);
  }
});

test('non-research state is rejected', () => {
  const copy = structuredClone(artifact);
  copy.recommendation_eligible = true;
  assert.throws(() => validateArtifact(copy), /STATE_NOT_RESEARCH_RAW/);
  const copy2 = structuredClone(artifact);
  copy2.availability = 'PARTIAL';
  assert.throws(() => validateArtifact(copy2), /STATE_NOT_RESEARCH_RAW/);
});

test('horizon shorter than 72 rows is rejected', () => {
  const copy = structuredClone(artifact);
  copy.hours = copy.hours.slice(0, 71);
  assert.throws(() => validateArtifact(copy), /HORIZON_NOT_72/);
});

test('gapped or non-hourly time axis is rejected', () => {
  const gapped = structuredClone(artifact);
  gapped.hours.splice(5, 1);
  assert.throws(() => validateArtifact(gapped), /NOT_CONTIGUOUS|HORIZON_NOT_72/);
  const shifted = structuredClone(artifact);
  shifted.hours[3].valid_at_utc = shifted.hours[3].valid_at_utc.replace('T0', 'T0').replace(':00:00Z', ':00:30Z');
  assert.throws(() => validateArtifact(shifted), /TIME_AXIS_INVALID/);
});

test('invalid cell values are rejected', () => {
  const copy = structuredClone(artifact);
  copy.hours[10].values.temperature_2m.value = '26.7';
  assert.throws(() => validateArtifact(copy), /CELL_INVALID/);
  const nan = structuredClone(artifact);
  nan.hours[10].values.visibility.value = NaN;
  assert.throws(() => validateArtifact(nan), /CELL_INVALID/);
});

test('missing or extra fields are rejected', () => {
  const missing = structuredClone(artifact);
  delete missing.hours[2].values.visibility;
  assert.throws(() => validateArtifact(missing), /CELL_INVALID|FIELD_COUNT/);
  const extra = structuredClone(artifact);
  extra.hours[2].values.wind_gust = {value: 1, state: 'AVAILABLE', reason_code: null, unit: 'm/s', source_unit: 'm/s'};
  assert.throws(() => validateArtifact(extra), /FIELD_COUNT_MISMATCH/);
});

test('staleness boundary is 21600 seconds from retrieval', () => {
  assert.equal(staleness(21600), 'CURRENT');
  assert.equal(staleness(21601), 'STALE');
  assert.equal(staleness(0), 'CURRENT');
  const now = Date.parse(artifact.source.retrieved_at_utc) + 21600000;
  assert.equal(staleness(retrievalAgeSeconds(now, artifact)), 'CURRENT');
  const later = now + 1000;
  assert.equal(staleness(retrievalAgeSeconds(later, artifact)), 'STALE');
});

test('UTC to Asia/Taipei formatting matches the contract example', () => {
  assert.equal(formatHourAsiaTaipei('2026-10-19T16:00:00Z'), '2026-10-20 00:00');
  assert.equal(formatHourAsiaTaipei('2026-10-23T14:00:00Z'), '2026-10-23 22:00');
});

test('all three locales carry an equivalent copy set', () => {
  assert.deepEqual(LOCALES.sort(), ['en', 'ja', 'zh-TW']);
  const keys = Object.keys(COPY['zh-TW']).sort();
  for (const locale of ['en', 'ja']) assert.deepEqual(Object.keys(COPY[locale]).sort(), keys);
  for (const locale of ['zh-TW', 'en', 'ja'])
    assert.deepEqual(Object.keys(FIELD_LABELS[locale]).sort(), Object.keys(FIELD_LABELS['zh-TW']).sort());
});

test('render recomputes staleness and labels it visibly', () => {
  const fresh = render({title: ''}, artifact, 'zh-TW', Date.parse(artifact.source.retrieved_at_utc) + 60000);
  assert.match(fresh, /仍在研究時效內/);
  const stale = render({title: ''}, artifact, 'zh-TW', Date.parse(artifact.source.retrieved_at_utc) + 25 * 3600000);
  assert.match(stale, /已超過研究時效上限/);
});

test('render is localized and escapes cell text', () => {
  for (const locale of ['zh-TW', 'en', 'ja']) {
    const html = render({title: ''}, artifact, locale, Date.now());
    assert.ok(html.includes(COPY[locale].limitationsHeading));
  }
  const hostile = structuredClone(artifact);
  hostile.hours[0].values.temperature_2m.unit = '<x>';
  const rendered = render({title: ''}, hostile, 'en', Date.now());
  assert.ok(!rendered.includes('<x>'));
  assert.ok(rendered.includes('&lt;x&gt;'));
});
