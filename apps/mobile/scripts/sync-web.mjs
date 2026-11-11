#!/usr/bin/env node
// Copies the static apps/web-v2 bundle (html/mjs/json/css) into apps/mobile/www
// so `npx cap add android` / `cap sync` can package it as the offline fallback shell.
// Cloud data (catalog / topics / language packs) is fetched at runtime; www is only
// the boot shell + last-known-good fallback assets.
import {cpSync, mkdirSync, existsSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const src = join(root, '..', 'web-v2');
const out = join(root, 'www');

if (!existsSync(src)) throw new Error(`web-v2 source not found: ${src}`);
mkdirSync(out, {recursive: true});
cpSync(src, out, {
  recursive: true,
  filter: (p) => {
    const base = p.replace(/\\/g, '/').split('/').pop();
    return !base.startsWith('tests') && base !== 'README.md' && base !== 'logs';
  }
});
console.log(`synced ${src} -> ${out}`);
