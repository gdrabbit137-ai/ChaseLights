// The browser pins bundle bytes at load time. These checks keep the pins
// generated (bundle-digests.mjs from build_web_catalog.py) and consumed
// (app.mjs imports them) so a manual edit can never drift from the data.
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';

const here=new URL('.',import.meta.url);
const read=u=>readFileSync(new URL(u,here));
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');

test('bundle-digests.mjs matches the shipped catalog and browse index bytes',()=>{
  const generated=read('../bundle-digests.mjs').toString();
  const catalog=sha(read('../catalog.v2.json'));
  const index=sha(read('../browse-index.v2.json'));
  assert.ok(generated.includes(`CATALOG_SHA256 = '${catalog}'`),'catalog pin drift');
  assert.ok(generated.includes(`BROWSE_INDEX_SHA256 = '${index}'`),'browse index pin drift');
});

test('app.mjs consumes the generated pins instead of hard-coded literals',()=>{
  const app=read('../app.mjs').toString();
  assert.ok(app.includes('from "./bundle-digests.mjs"'),'app must import bundle-digests');
  assert.ok(!/['"][0-9a-f]{64}['"]/.test(app.replace(/source_blob_sha|source_commit_sha/g,'')),
    'app must not embed raw 64-hex digests');
});
