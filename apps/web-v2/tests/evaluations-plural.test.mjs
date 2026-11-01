// node --test apps/web-v2/tests/evaluations-plural.test.mjs
// CL-UI-04: English count nouns must be singular for count===1 and plural otherwise.
// zh-TW and ja have no morphological pluralization; their dict values stay strings.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {resolve, dirname} from 'node:path';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const source = await readFile(resolve(here, '../evaluations.html'), 'utf8');

// I18N is a multi-line object literal terminating with its own "}; " line.
const extractBlock = name => {
  const begin = source.indexOf(`const ${name}=`);
  assert.notEqual(begin, -1, `const ${name}= must exist in evaluations.html`);
  const end = source.indexOf('\n};', begin);
  assert.notEqual(end, -1, `block ${name} must terminate with };`);
  return source.slice(begin, end + 3);
};

// pickCount is a single-line arrow function ending in ";".
const extractLine = name => {
  const begin = source.indexOf(`const ${name}=`);
  assert.notEqual(begin, -1, `const ${name}= must exist in evaluations.html`);
  const end = source.indexOf('\n', begin);
  assert.notEqual(end, -1, `line ${name} must be terminated`);
  return source.slice(begin, end);
};

const vmSource = extractBlock('I18N') + '\n' + extractLine('pickCount') + '\n({I18N, pickCount})';
const sandbox = vm.runInNewContext(vmSource, {});

test('CL-UI-04 en: opportunity count uses singular "opportunity" for 1 and plural otherwise', () => {
  assert.equal(sandbox.pickCount(sandbox.I18N.en.opps, 1), 'opportunity');
  assert.equal(sandbox.pickCount(sandbox.I18N.en.opps, 2), 'opportunities');
  assert.equal(sandbox.pickCount(sandbox.I18N.en.opps, 0), 'opportunities');
  assert.equal(sandbox.pickCount(sandbox.I18N.en.opps, 353), 'opportunities');
});

test('CL-UI-04 en: place-group count uses singular "place group" for 1 and plural otherwise', () => {
  assert.equal(sandbox.pickCount(sandbox.I18N.en.places, 1), 'place group');
  assert.equal(sandbox.pickCount(sandbox.I18N.en.places, 2), 'place groups');
  assert.equal(sandbox.pickCount(sandbox.I18N.en.places, 0), 'place groups');
});

test('CL-UI-04 zh-TW and ja keep plain strings (no morphological plural)', () => {
  assert.equal(sandbox.I18N['zh-TW'].places, '景點組');
  assert.equal(sandbox.I18N['zh-TW'].opps, '機會');
  assert.equal(sandbox.I18N.ja.places, '地点グループ');
  assert.equal(sandbox.I18N.ja.opps, '機会');
});
