import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {validateArtifact, render, COPY, LOCALES} from '../solar-pilot.mjs';

const artifact = JSON.parse(readFileSync(
  fileURLToPath(new URL('../solar-window-tw036.json', import.meta.url)), 'utf8'));

test('real solar pilot artifact validates', () => {
  assert.equal(validateArtifact(artifact).place_id, 'tw-036');
  assert.equal(artifact.results.length, 14);
});

test('identity and research-state mismatches fail closed', () => {
  for (const key of ['pilot_id', 'place_id', 'schema_version', 'time_zone']) {
    const copy = structuredClone(artifact);
    copy[key] = 'x';
    assert.throws(() => validateArtifact(copy), /ARTIFACT_IDENTITY_MISMATCH|STATE_NOT_RESEARCH/);
  }
  const score = structuredClone(artifact);
  score.recommendation_eligible = true;
  assert.throws(() => validateArtifact(score), /STATE_NOT_RESEARCH/);
  const verdict = structuredClone(artifact);
  verdict.results[0].capability = 'FAVORABLE';
  assert.throws(() => validateArtifact(verdict), /RESULT_STATE_NOT_WINDOW/);
});

test('window length and date ordering are enforced', () => {
  const short = structuredClone(artifact);
  short.results = short.results.slice(0, 13);
  assert.throws(() => validateArtifact(short), /WINDOW_NOT_14_DAYS/);
  const unordered = structuredClone(artifact);
  [unordered.results[3].local_date, unordered.results[4].local_date] =
    [unordered.results[4].local_date, unordered.results[3].local_date];
  assert.throws(() => validateArtifact(unordered), /NOT_ASCENDING/);
});

test('event state consistency is enforced (no fabricated times)', () => {
  const fabricated = structuredClone(artifact);
  fabricated.results[2].sunrise.status = 'NO_EVENT';
  assert.throws(() => validateArtifact(fabricated), /EVENT_STATE_INCONSISTENT/);
  const orphan = structuredClone(artifact);
  orphan.results[2].sunset.time_local = null;
  assert.throws(() => validateArtifact(orphan), /EVENT_STATE_INCONSISTENT/);
});

test('observer provenance must stay a representative sample', () => {
  const camera = structuredClone(artifact);
  camera.results[0].observer.coordinate_role = 'verified_camera_reference';
  assert.throws(() => validateArtifact(camera), /OBSERVER_PROVENANCE_INVALID/);
});

test('trilingual copy sets are equivalent', () => {
  assert.deepEqual(LOCALES.sort(), ['en', 'ja', 'zh-TW']);
  const keys = Object.keys(COPY['zh-TW']).sort();
  for (const locale of ['en', 'ja']) assert.deepEqual(Object.keys(COPY[locale]).sort(), keys);
});

test('render marks past dates and localizes', () => {
  const farFuture = Date.parse('2027-06-01T00:00:00Z');
  for (const locale of ['zh-TW', 'en', 'ja']) {
    const html = render({title: ''}, artifact, locale, farFuture);
    assert.ok(html.includes(COPY[locale].limitationsHeading));
    assert.ok(html.includes(COPY[locale].pastNotice));
  }
});

test('render escapes cell text', () => {
  const hostile = structuredClone(artifact);
  hostile.generation.source = '<script>';
  const rendered = render({title: ''}, hostile, 'en', Date.now());
  assert.ok(!rendered.includes('<script>'));
  assert.ok(rendered.includes('&lt;script&gt;'));
});
