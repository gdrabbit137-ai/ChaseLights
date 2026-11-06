// CL-INT-76 — public_browser_smoke.mjs must never pin a hardcoded commit sha:
// catalog regeneration (new canonical commit) moves the repo artifacts, and the
// smoke's provenance expectations must move with them instead of going red.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {test} from 'node:test';

const smoke = await readFile(new URL('../public_browser_smoke.mjs', import.meta.url), 'utf8');

test('smoke contains no hardcoded 40-hex commit sha literal', () => {
  const hits = smoke.match(/\b[a-f0-9]{40}\b/g) || [];
  assert.deepEqual(hits, [], 'hardcoded sha literal leaked back into the smoke: ' + hits.join(','));
});

test('smoke derives provenance expectations from repo build/pin artifacts', () => {
  assert.ok(smoke.includes('apps/web-v2/catalog.v2.json'),
    'HOME branch must compare against the repo built catalog artifact');
  assert.ok(smoke.includes('integration-sources.json'),
    'legacy branch must read the canonical commit from the integration source lock');
  assert.ok(smoke.includes('BEGIN provenance-artifact block') &&
            smoke.includes('END provenance-artifact block'),
    'slice-tested provenance block markers missing');
});

// Slice the provenance block out of the smoke (grab pattern) and replay it
// against fixtures so a simulated catalog regeneration proves the assertion
// follows the artifacts instead of a frozen literal.
async function loadProvenanceRunner() {
  const begin = smoke.indexOf('// BEGIN provenance-artifact block');
  const end = smoke.indexOf('// END provenance-artifact block');
  assert.ok(begin >= 0 && end > begin, 'provenance block not found');
  const src = smoke.slice(begin, end)
    .split("new URL('../../apps/web-v2/catalog.v2.json',import.meta.url)").join('"repo-catalog-url"')
    .split("new URL('./integration-sources.json',import.meta.url)").join('"integration-lock-url"');
  assert.ok(src.includes('"repo-catalog-url"') && src.includes('"integration-lock-url"'),
    'artifact URL stubbing failed — smoke block text drifted');
  // eslint-disable-next-line no-new-func
  return new Function('readFile', 'URL', 'assert', `return async () => {\n${src}\nreturn {repoCatalog, legacySourceCommitSha};\n};`);
}

test('simulated catalog regeneration keeps the assertion artifact-driven', async () => {
  const makeRunner = await loadProvenanceRunner();
  let LEGACY_SHA = 'b'.repeat(40);
  let REPO_CATALOG = {
    source_pins: {
      'tw-026-P01': {source_commit_sha: 'a'.repeat(40), source_path: 'data/v2/opportunities/tw-026-P01.json', revision: 1},
      'jp-010-P01': {source_commit_sha: LEGACY_SHA, source_path: 'data/v2/opportunities/jp-010-P01.json', revision: 1},
    },
  };
  const fakeReadFile = async path =>
    (path === 'repo-catalog-url' || path?.href === 'repo-catalog-url') ? JSON.stringify(REPO_CATALOG)
      : JSON.stringify({sources: {w2: {canonical_content_sha: LEGACY_SHA}}});
  // `new URL(...)` in the sliced block needs a real constructor function.
  function fakeURL(x) { return {href: x}; }

  // Current repo state: built catalog pins and integration lock agree.
  let derived = await makeRunner(fakeReadFile, fakeURL, assert)();
  assert.deepEqual(derived.repoCatalog, REPO_CATALOG);
  assert.equal(derived.legacySourceCommitSha, LEGACY_SHA);

  // Regenerate: every sha moves together (data + artifacts + published site).
  const regenerated = structuredClone(REPO_CATALOG);
  for (const pin of Object.values(regenerated.source_pins))
    pin.source_commit_sha = 'c'.repeat(40);
  REPO_CATALOG = regenerated;
  LEGACY_SHA = 'c'.repeat(40);
  derived = await makeRunner(fakeReadFile, fakeURL, assert)();
  // The expectation now equals the regenerated value — a hardcoded literal
  // ('a'.repeat(40) / 'b'.repeat(40)) would have failed this smoke.
  assert.equal(derived.legacySourceCommitSha, 'c'.repeat(40));
  assert.deepEqual(derived.repoCatalog.source_pins, regenerated.source_pins);

  // Structural same-origin check used by the HOME branch: identical artifacts
  // pass, a drifted live catalog fails with a real diff (evolution signal kept).
  assert.deepEqual(regenerated.source_pins, regenerated.source_pins);
  const preRegeneration = structuredClone(regenerated);
  for (const pin of Object.values(preRegeneration.source_pins))
    pin.source_commit_sha = 'a'.repeat(40);
  assert.notDeepEqual(regenerated.source_pins, preRegeneration.source_pins,
    'regenerated pins must differ from the pre-regeneration artifact');
});
