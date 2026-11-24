// Local pre-flight for the V2 public preview smoke: verifies the release
// manifest against the bytes this tree would publish (same helpers CI uses).
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { validateManifest, verifyPublicAsset, verifyPublicIndex } from './public_source_contract.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..');
const manifest = JSON.parse(await readFile(join(HERE, 'public-beta-r3-manifest.json'), 'utf8'));
validateManifest(manifest);
let checked = 0;
for (const key of Object.keys(manifest.files)) {
  const body = await readFile(join(ROOT, key));
  verifyPublicAsset(manifest, key.replace(/^apps\/web-v2\//, ''), body);
  checked += 1;
}
const catalog = JSON.parse(await readFile(join(ROOT, 'apps/web-v2/catalog.v2.json'), 'utf8'));
const bundle = JSON.parse(await readFile(join(ROOT, 'apps/web-v2/browse-index.v2.json'), 'utf8'));
verifyPublicIndex(manifest, catalog, bundle);
console.log(JSON.stringify({ ok: true, checked, source_commit_sha: manifest.source_commit_sha }));
