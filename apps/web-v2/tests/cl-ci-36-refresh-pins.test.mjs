// CL-CI-36: root-cure for the "scheduled refresh breaks test pins" loop.
// The cron (update_evaluations.yml) rebuilds the evaluations bundle and the
// derived subject-cards artifact in place every 6h under app.js's stable
// pointer (V2_SUBJECT_CARDS_FILE). Tests that hardcode a place/date/count
// from that artifact go stale on the next refresh and must be re-anchored by
// hand. The cure is dynamic anchoring: tests derive their exemplars FROM the
// current artifact and read the filename through app.js's pointer. This
// guard keeps the suite honest — it fails whenever a test reintroduces a
// hardcoded data pin against the refreshable artifacts:
//   (1) a copied subject-cards filename literal (the pointer lives in app.js);
//   (2) a chained place+date row read off the real artifact (exemplars must
//       be derived at runtime);
//   (3) the pointer itself must resolve to a real artifact file.
// Behavioral contracts (contradiction-free tiers, fail-closed cells,
// dictionary joins, honest degradation) stay hard-asserted — this guard
// only bans DATA anchors, never behavior assertions.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync, existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const SELF = 'cl-ci-36-refresh-pins.test.mjs';

const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const pointer = (appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/) || [])[1];
const testDir = join(here);
const testFiles = readdirSync(testDir).filter(f => f.endsWith('.test.mjs') && f !== SELF);

test('CL-CI-36 (1): no test copies the subject-cards filename — the pointer lives in app.js', () => {
  assert.ok(pointer, 'app.js pins V2_SUBJECT_CARDS_FILE');
  for (const f of testFiles) {
    const src = readFileSync(join(testDir, f), 'utf8');
    const hits = src.match(/subject-cards-\d{8}T\d{6}Z\.json/g) || [];
    assert.equal(hits.length, 0,
      `${f} hardcodes the refreshable artifact filename ${hits[0] || ''} — read V2_SUBJECT_CARDS_FILE from assets/app.js instead`);
  }
});

test('CL-CI-36 (2): no test chains a literal place+date read off the real artifact', () => {
  for (const f of testFiles) {
    const src = readFileSync(join(testDir, f), 'utf8');
    const hits = src.match(/places\['[^']+'\]\['\d{4}-\d{2}-\d{2}'\]/g) || [];
    assert.equal(hits.length, 0,
      `${f} pins an artifact row (${hits[0] || ''}) — derive the exemplar from the current artifact instead`);
  }
});

test('CL-CI-36 (3): the app.js pointer resolves to the committed artifact', () => {
  assert.ok(pointer, 'app.js pins V2_SUBJECT_CARDS_FILE');
  const path = join(ROOT, 'data', 'v2', 'evaluations', pointer);
  assert.ok(existsSync(path), `artifact missing: ${pointer}`);
  const artifact = JSON.parse(readFileSync(path, 'utf8'));
  assert.equal(artifact.layer, 'subject_cards');
  assert.ok(existsSync(join(ROOT, 'data', 'v2', 'evaluations', artifact.derived_from.source_bundle)),
    'the derived artifact declares a real source bundle');
});
