// CL-UI-09: English subject-count pluralization in the V1 shell (repo-root assets/genre-eval.js).
// Loads the browser IIFE in Node via its module.exports test hook (DOM-free).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { subjectCountLabel } = require('../../../assets/genre-eval.js');

test('CL-UI-09: en — 1 subject (singular)', () => {
  assert.equal(subjectCountLabel(1, 'en'), 'subject');
});

test('CL-UI-09: en — 2 subjects (plural)', () => {
  assert.equal(subjectCountLabel(2, 'en'), 'subjects');
});

test('CL-UI-09: en — 0 subjects (plural)', () => {
  assert.equal(subjectCountLabel(0, 'en'), 'subjects');
});

test('CL-UI-09: en — large count stays plural', () => {
  assert.equal(subjectCountLabel(12, 'en'), 'subjects');
});

test('CL-UI-09: zh-TW count string is count-invariant', () => {
  assert.equal(subjectCountLabel(1, 'zh-TW'), '個題材');
  assert.equal(subjectCountLabel(2, 'zh-TW'), '個題材');
  assert.equal(subjectCountLabel(0, 'zh-TW'), '個題材');
});

test('CL-UI-09: ja count string is count-invariant', () => {
  assert.equal(subjectCountLabel(1, 'ja'), '题材');
  assert.equal(subjectCountLabel(2, 'ja'), '题材');
  assert.equal(subjectCountLabel(0, 'ja'), '题材');
});
