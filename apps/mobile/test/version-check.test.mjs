import test from 'node:test';
import assert from 'node:assert/strict';
import {createVersionChecker, sha256Hex} from '../src/version-check.mjs';
import {memoryCache} from '../src/cache-store.mjs';

const BUNDLE = JSON.stringify({schema_version: '2.1.0', opportunities: []});
const DIGEST = await sha256Hex(BUNDLE);

function make({digestStatus = 200, digestBody = {digest: DIGEST}, bundleStatus = 200, bundleBody = BUNDLE} = {}) {
  const cache = memoryCache();
  const fetchImpl = async (url) => {
    if (url.includes('digests')) {
      if (digestStatus >= 500) throw new Error(`HTTP ${digestStatus}`);
      return {ok: digestStatus < 400, status: digestStatus, json: async () => digestBody};
    }
    return {ok: bundleStatus < 400, status: bundleStatus, text: async () => bundleBody};
  };
  return {checker: createVersionChecker({fetchImpl, cache}), cache};
}

test('first run: no cache + reachable digest -> status first, download caches after digest match', async () => {
  const {checker, cache} = make();
  const r = await checker.check();
  assert.equal(r.status, 'first');
  const d = await checker.download(r.remoteDigest);
  assert.equal(d.status, 'cached');
  assert.equal(await cache.read('bundle'), BUNDLE);
  const again = await checker.check();
  assert.equal(again.status, 'current');
});

test('current: cached digest equals remote digest keeps cached bundle', async () => {
  const {checker} = make();
  await checker.check();
  const r = await checker.download(DIGEST);
  assert.equal(r.status, 'cached');
  assert.equal((await checker.check()).status, 'current');
});

test('offline: fetch throws + cache exists -> offline degrade with cached bundle', async () => {
  const {checker, cache} = make();
  await cache.write('bundle', BUNDLE);
  await cache.write('digest', DIGEST);
  const r = await checker.check({}); // digest endpoint unreachable
  const offline = await createVersionChecker({
    fetchImpl: async () => { throw new Error('network down'); },
    cache
  }).check();
  assert.equal(offline.status, 'offline');
  assert.equal(offline.bundle, BUNDLE);
  assert.equal(offline.cachedDigest, DIGEST);
  void r;
});

test('offline with no cache -> offline-no-cache', async () => {
  const {checker} = make({digestStatus: 503});
  const r = await checker.check();
  assert.equal(r.status, 'offline-no-cache');
  assert.equal(r.bundle, null);
});

test('fail-closed: downloaded bytes whose sha256 != declared digest are rejected, cache untouched', async () => {
  const {checker, cache} = make({bundleBody: '{"tampered":true}'});
  const r = await checker.check();
  const d = await checker.download(r.remoteDigest);
  assert.equal(d.status, 'digest-mismatch');
  assert.notEqual(d.actual, DIGEST);
  assert.equal(await cache.read('bundle'), null);
});

test('digest-mismatch reported for corrupted remote digest vs good bundle', async () => {
  const {checker} = make({digestBody: {digest: 'deadbeef'}});
  const r = await checker.check();
  assert.equal(r.status, 'first');
  assert.equal((await checker.download(r.remoteDigest)).status, 'digest-mismatch');
});
