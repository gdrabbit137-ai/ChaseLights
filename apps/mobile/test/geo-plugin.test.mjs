// CL-APP-06: @capacitor/geolocation is registered in the mobile shell so the
// private-place 「📍 使用我的目前位置」 button also works inside the native
// WebView (WKWebView / Android WebView can block the raw web Geolocation API
// in a Capacitor shell). The web-v2 implementation stays the SINGLE copy —
// it prefers the plugin only when window.Capacitor reports a native platform,
// and falls back to navigator.geolocation on the plain web.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const MOBILE = join(HERE, '..');
const pkg = JSON.parse(readFileSync(join(MOBILE, 'package.json'), 'utf8'));
const lock = JSON.parse(readFileSync(join(MOBILE, 'package-lock.json'), 'utf8'));

function readSrcMjs(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...readSrcMjs(p));
    else if (name.endsWith('.mjs')) out.push(readFileSync(p, 'utf8'));
  }
  return out;
}

test('geo-plugin: @capacitor/geolocation is a shell dependency pinned to the shell major (6)', () => {
  const dep = pkg.dependencies['@capacitor/geolocation'];
  assert.ok(dep, 'dependency present in apps/mobile/package.json');
  assert.equal(dep.startsWith('^6.'), true, `pinned to Capacitor 6 shell, got ${dep}`);
  // same-major pin rule that saved push-notifications from the v8 ERESOLVE trap
  const coreMajor = pkg.dependencies['@capacitor/core'].match(/\^(\d+)\./)[1];
  assert.equal(dep.match(/\^(\d+)\./)[1], coreMajor, 'plugin major == @capacitor/core major');
});

test('geo-plugin: package-lock resolves the plugin against the Capacitor 6 core peer', () => {
  const entry = lock.packages['node_modules/@capacitor/geolocation'];
  assert.ok(entry, 'lockfile entry exists');
  assert.equal(entry.version.startsWith('6.'), true);
  assert.match(entry.peerDependencies['@capacitor/core'], /\^6\./);
});

test('geo-plugin: the android CI build runs cap:sync so the plugin registers natively', () => {
  const wf = readFileSync(join(MOBILE, '..', '..', '.github', 'workflows', 'android-build.yml'), 'utf8');
  assert.match(wf, /npm run cap:sync/, 'cap:sync regenerates the native plugin registration');
});

test('geo-plugin: web-v2 keeps the single geolocation implementation', () => {
  const web = readFileSync(join(MOBILE, '..', '..', 'assets', 'custom-places.js'), 'utf8');
  assert.match(web, /geoGetPosition/);
  assert.match(web, /navigator\.geolocation\.getCurrentPosition/);
  assert.match(web, /cap\.Plugins\.Geolocation/);
  // the mobile shell source must NOT carry its own geolocation call —
  // one implementation, in web-v2
  const src = readSrcMjs(join(MOBILE, 'src')).join('');
  assert.doesNotMatch(src, /getCurrentPosition/);
});

