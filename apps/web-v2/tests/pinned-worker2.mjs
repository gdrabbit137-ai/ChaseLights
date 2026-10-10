import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

export const W2_SHA = '7f10e9bd2757449d72546155c66714880c6d3ab1';
export const fixtureDirectory = fileURLToPath(new URL('./fixtures/worker2/', import.meta.url));
export const manifest = JSON.parse(readFileSync(resolve(fixtureDirectory, 'manifest.json'), 'utf8'));
export function gitBlob(buffer) {
  return createHash('sha1').update(`blob ${buffer.length}\0`).update(buffer).digest('hex');
}
export function readPinned(name, directory=fixtureDirectory) {
  assert.equal(manifest.commit_sha, W2_SHA);
  const entry = manifest.files.find(file => file.fixture === name);
  assert.ok(entry, `Unregistered W2 source: ${name}`);
  const bytes = readFileSync(resolve(directory, name));
  assert.equal(gitBlob(bytes), entry.blob_sha, `${name}: not the pinned Git blob`);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), entry.sha256, `${name}: SHA-256 mismatch`);
  return JSON.parse(bytes.toString('utf8'));
}
export function readOriginals(directory=fixtureDirectory) {
  return ['tw-016-P01','tw-026-P01','tw-026-P02'].map(id => readPinned(`${id}.json`, directory));
}
