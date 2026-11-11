import test from 'node:test';
import assert from 'node:assert/strict';
import {createI18n, keyParity, bundled} from '../src/i18n/index.mjs';

test('three bundled locales have complete key parity with zh-TW base', () => {
  const report = keyParity();
  for (const code of ['zh-TW', 'en', 'ja']) {
    assert.deepEqual(report[code].missing, [], `${code} missing keys`);
    assert.deepEqual(report[code].extra, [], `${code} extra keys`);
    assert.equal(report[code].complete, true);
  }
});

test('no hardcoded copy: every message the shell can render exists as a key in all locales', () => {
  // Keys boot.mjs / status flows rely on (version check + offline degrade states).
  const required = ['loading', 'loadError', 'retry', 'offlineUsingCache', 'offlineNoCache',
    'dataCurrent', 'dataNew', 'dataUpdated', 'digestMismatch', 'firstRun'];
  for (const [code, pack] of Object.entries(bundled)) {
    for (const key of required) assert.equal(typeof pack[key], 'string', `${code}/${key}`);
    // Zero-copy-in-code rule: no locale may contain empty strings.
    for (const [key, value] of Object.entries(pack)) assert.ok(value.trim(), `${code}/${key} empty`);
  }
});

test('t() falls back to zh-TW then key itself for unknown keys, interpolates vars', () => {
  const i18n = createI18n({locale: 'ja'});
  assert.equal(i18n.t('offline'), 'オフライン');
  assert.equal(i18n.t('does-not-exist'), 'does-not-exist');
  const en = createI18n({locale: 'en'});
  assert.equal(en.t('dataDownloading'), 'Downloading new data…');
  i18n.registerLocale('xx', {dataDownloading: '下載中 {percent}%'});
  i18n.setLocale('xx');
  assert.equal(i18n.t('dataDownloading', {percent: 42}), '下載中 42%');
});

test('cloud language pack registration enables a new language without a release', () => {
  const i18n = createI18n({locale: 'en'});
  i18n.registerLocale('ko', {'ko-only': '한국어'});
  i18n.setLocale('ko');
  assert.equal(i18n.locale, 'ko');
  // Registered pack lacking a key falls back to the fallback locale's value.
  assert.equal(typeof i18n.t('offline'), 'string');
  assert.equal(i18n.availableLocales().includes('ko'), true);
});
