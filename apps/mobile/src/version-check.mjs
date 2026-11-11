// Data-version check for the ChaseLights APP shell.
//
// Contract: the cloud publishes a bundle digest (catalog.v2.json SHA-256, matching
// apps/web-v2/bundle-digests.mjs pins) at a well-known endpoint. On startup the shell
// compares it against the locally cached digest; on a new version it downloads the
// bundle in the background and swaps the cache only after the digest verifies
// (fail-closed, same policy as web-v2). Offline -> serve cached data and report status.
import {createHash} from 'node:crypto';

// In the browser this maps to window.crypto.subtle; Node's webcrypto keeps the
// same async interface so the module runs unchanged in `node --test`.
const subtle = globalThis.crypto?.subtle;

export async function sha256Hex(text) {
  if (subtle) {
    const buf = new TextEncoder().encode(text);
    const digest = await subtle.digest('SHA-256', buf);
    return Buffer.from(digest).toString('hex');
  }
  return createHash('sha256').update(text, 'utf8').digest('hex');
}

export function createVersionChecker({
  fetchImpl = (...args) => fetch(...args),
  digestUrl = '/api/v1/catalog/digests',
  bundleUrl = '/catalog.v2.json',
  cache, // {read(key), write(key, text)} — inject Capacitor Preferences / localStorage
  now = () => new Date().toISOString()
} = {}) {
  if (!cache) throw new Error('createVersionChecker: cache adapter is required');
  const cached = (key) => cache.read(key);

  async function check() {
    const cachedDigest = await cached('digest');
    const cachedBundle = await cached('bundle');
    let remote;
    try {
      const res = await fetchImpl(digestUrl, {headers: {accept: 'application/json'}});
      if (!res.ok) throw new Error(`digest HTTP ${res.status}`);
      const doc = await res.json();
      remote = typeof doc.digest === 'string' ? doc.digest
        : typeof doc?.catalog?.sha256 === 'string' ? doc.catalog.sha256 : null;
      if (!remote) throw new Error('digest field missing');
    } catch (error) {
      // Offline / endpoint unreachable: degrade to cache.
      if (cachedBundle) {
        return {status: 'offline', remoteDigest: null, cachedDigest, bundle: cachedBundle,
          message: 'offline-cache', error: String(error?.message ?? error), checkedAt: now()};
      }
      return {status: 'offline-no-cache', remoteDigest: null, cachedDigest: null, bundle: null,
        message: 'offline-no-cache', error: String(error?.message ?? error), checkedAt: now()};
    }
    if (cachedDigest === remote && cachedBundle) {
      return {status: 'current', remoteDigest: remote, cachedDigest, bundle: cachedBundle, checkedAt: now()};
    }
    return {status: cachedDigest ? 'new' : 'first', remoteDigest: remote, cachedDigest,
      bundle: cachedBundle, checkedAt: now()};
  }

  // Background download: only replaces the cache after digest verification.
  async function download(remoteDigest) {
    const res = await fetchImpl(bundleUrl, {headers: {accept: 'application/json'}});
    if (!res.ok) throw new Error(`bundle HTTP ${res.status}`);
    const text = await res.text();
    const actual = await sha256Hex(text);
    if (actual !== remoteDigest) {
      return {status: 'digest-mismatch', expected: remoteDigest, actual, cached: false};
    }
    await cache.write('bundle', text);
    await cache.write('digest', remoteDigest);
    await cache.write('updatedAt', now());
    return {status: 'cached', digest: remoteDigest, bytes: text.length};
  }

  return {check, download, sha256Hex};
}
