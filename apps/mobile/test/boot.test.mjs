import test from 'node:test';
import assert from 'node:assert/strict';
import {boot} from '../src/boot.mjs';
import {createVersionChecker} from '../src/version-check.mjs';
import {createI18n} from '../src/i18n/index.mjs';
import {memoryCache} from '../src/cache-store.mjs';

const BUNDLE = JSON.stringify({schema_version: '2.1.0', opportunities: []});
const DIGEST = await (await import('../src/version-check.mjs')).sha256Hex(BUNDLE);

test('boot: offline with cache reports localized degrade message', async () => {
  const cache = memoryCache({bundle: BUNDLE, digest: DIGEST});
  const checker = createVersionChecker({
    fetchImpl: async () => { throw new Error('network down'); }, cache});
  const events = [];
  const result = await boot({checker, i18n: createI18n({locale: 'zh-TW'}),
    onStatus: (e) => events.push(e)});
  assert.equal(result.status, 'offline');
  assert.equal(events[0].message, '目前離線；使用本機快取的資料。');
});

test('boot: new version triggers background download and reports localized result', async () => {
  const cache = memoryCache({bundle: '{"old":true}', digest: 'old-digest'});
  const checker = createVersionChecker({
    fetchImpl: async (url) => url.includes('digests')
      ? {ok: true, status: 200, json: async () => ({digest: DIGEST})}
      : {ok: true, status: 200, text: async () => BUNDLE},
    cache});
  const events = [];
  await boot({checker, i18n: createI18n({locale: 'en'}), onStatus: (e) => events.push(e)});
  await new Promise((r) => setTimeout(r, 10)); // let the fire-and-forget download settle
  const phases = events.map((e) => e.phase);
  assert.deepEqual(phases, ['checked', 'downloaded']);
  assert.equal(events[1].message, 'New data cached; it will be used on next launch.');
  assert.equal(await cache.read('bundle'), BUNDLE);
});
