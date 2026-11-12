// CL-APP-03: push base unit tests — token registration, graceful degradation
// when the plugin (google-services.json) is absent. node:test, no deps.
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  PUSH_CHANNEL_ID, PUSH_API_PATH, deviceUniqueId,
  registerPushToken, createPushRegistrar, defaultPushPlugin
} from '../src/push.mjs';

function fakeStorage() {
  const m = new Map();
  return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, v), _m: m };
}

test('push: deviceUniqueId is stable and persisted per install', () => {
  const s = fakeStorage();
  const a = deviceUniqueId(s);
  const b = deviceUniqueId(s);
  assert.equal(a, b);
  assert.ok(a.startsWith('app-'));
  assert.equal(deviceUniqueId(fakeStorage()) !== a, true, 'fresh storage -> fresh id');
});

test('push: registerPushToken POSTs token to /api/v1/push_tokens with device id', async () => {
  const calls = [];
  const fetchImpl = async (url, opts) => {
    calls.push({ url: String(url), opts });
    return { ok: true, status: 200, json: async () => ({ ok: true }) };
  };
  const r = await registerPushToken({
    apiBase: 'https://chaselights.app', fetchImpl,
    token: 'fcm-token-1', deviceId: 'app-xyz', accessToken: 'jwt-abc',
  });
  assert.equal(r.ok, true);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, `https://chaselights.app${PUSH_API_PATH}`);
  assert.equal(calls[0].opts.method, 'POST');
  const body = JSON.parse(calls[0].opts.body);
  assert.deepEqual(body, { platform: 'android/fcm', token: 'fcm-token-1', deviceId: 'app-xyz' });
  assert.equal(calls[0].opts.headers.Authorization, 'Bearer jwt-abc');
});

test('push: registerPushToken never throws (network error -> ok:false)', async () => {
  const r = await registerPushToken({
    apiBase: 'https://chaselights.app',
    fetchImpl: async () => { throw new Error('offline'); },
    token: 'fcm-token-2', deviceId: 'app-xyz',
  });
  assert.equal(r.ok, false);
  const bad = await registerPushToken({
    apiBase: 'https://chaselights.app',
    fetchImpl: async () => ({ ok: false, status: 400 }),
    token: 'fcm-token-2', deviceId: 'app-xyz',
  });
  assert.equal(bad.ok, false);
  assert.equal(bad.status, 400);
});

test('push: no plugin (google-services.json missing) -> graceful disable, no API call', async () => {
  const logs = [];
  const log = { info: (m) => logs.push(m), warn: (m) => logs.push(m) };
  const reg = createPushRegistrar({ plugin: null, log });
  const r = await reg.start();
  assert.deepEqual(r, { enabled: false, reason: 'plugin-unavailable' });
  assert.ok(logs[0].includes('[push] disabled'));
  assert.ok(logs[0].includes('google-services.json'));
});

test('push: permission denied -> graceful disable, no register() call', async () => {
  let registered = false;
  const plugin = {
    checkPermissions: async () => ({ display: 'prompt' }),
    requestPermissions: async () => ({ display: 'denied' }),
    register: async () => { registered = true; },
    addListener: () => {},
    createChannel: async () => {},
  };
  const logs = [];
  const r = await createPushRegistrar({ plugin, storage: fakeStorage(), log: { info: (m) => logs.push(m), warn: () => {} } }).start();
  assert.equal(r.enabled, false);
  assert.equal(r.reason, 'permission-denied');
  assert.equal(registered, false);
});

test('push: granted permission -> channel created, register() called, token POSTed', async () => {
  const s = fakeStorage();
  const calls = [];
  const fetchImpl = async (url, opts) => { calls.push({ url: String(url), body: JSON.parse(opts.body) }); return { ok: true, status: 200 }; };
  const listeners = {};
  const channelCalls = [];
  const plugin = {
    checkPermissions: async () => ({ display: 'granted' }),
    requestPermissions: async () => ({ display: 'granted' }),
    createChannel: async (c) => channelCalls.push(c),
    addListener: (ev, cb) => { listeners[ev] = cb; return { remove: () => {} }; },
    register: async () => { listeners.registration({ value: 'fcm-token-9' }); },
  };
  const r = await createPushRegistrar({
    plugin, fetchImpl, storage: s,
    accessTokenProvider: () => 'jwt-1',
    log: { info: () => {}, warn: () => {} },
  }).start();
  assert.equal(r.enabled, true);
  assert.equal(channelCalls.length, 1);
  assert.equal(channelCalls[0].id, PUSH_CHANNEL_ID);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].body.token, 'fcm-token-9');
  assert.equal(calls[0].body.deviceId, s.getItem('chaselights:device-id'));
  assert.equal(calls[0].body.platform, 'android/fcm');
});

test('push: register() throwing (FCM absent at runtime) -> graceful disable', async () => {
  const logs = [];
  const plugin = {
    checkPermissions: async () => ({ display: 'granted' }),
    createChannel: async () => {},
    addListener: () => {},
    register: async () => { throw new Error('No FirebaseApp initialized'); },
  };
  const r = await createPushRegistrar({ plugin, storage: fakeStorage(), log: { info: (m) => logs.push(m), warn: () => {} } }).start();
  assert.equal(r.enabled, false);
  assert.equal(r.reason, 'register-failed');
});

test('push: defaultPushPlugin resolves null outside the Capacitor shell', () => {
  assert.equal(defaultPushPlugin(), null);
});
