import test from 'node:test';
import assert from 'node:assert/strict';
import {projectV21} from '../v21-adapter.mjs';
test('empty documents are not projected', () => assert.equal(projectV21({places:[]}), null));
