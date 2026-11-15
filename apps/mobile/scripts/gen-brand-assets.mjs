#!/usr/bin/env node
// CL-APP-05: rasterize the approved 案5「主峰金頂」brand SVGs into every PNG the
// repo serves or ships: Android mipmap adaptive-icon layers + legacy launchers,
// web favicons (16/32/48 + apple-touch 180) and the Play Store 512 icon.
// Sources of truth live in <repo>/assets/brand/*.svg — rerun this script after
// any SVG edit; never hand-edit the PNGs.
import { Resvg } from '@resvg/resvg-js';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const mobileDir = dirname(dirname(fileURLToPath(import.meta.url)));
const repo = resolve(mobileDir, '..', '..');
const brand = join(repo, 'assets', 'brand');
const res = join(repo, 'apps', 'mobile', 'android', 'app', 'src', 'main', 'res');
const assets = join(repo, 'assets');

const svg = (name) => readFileSync(join(brand, name), 'utf8');
const brandFull = svg('brand-512.svg');
const bg = svg('icon-background.svg');
const fg = svg('icon-foreground.svg');
const mono = svg('icon-monochrome.svg');

// Circular-cropped full brand for mipmap-*/ic_launcher_round.png: wrap the
// brand art in a clipPath circle instead of its rounded-rect background.
const roundSvg = (size) => `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="${size}" height="${size}">
<clipPath id="round-clip"><circle cx="256" cy="256" r="256"/></clipPath>
<g clip-path="url(#round-clip)">${brandFull.replace(/^<\?xml[^>]*\?>\s*/, '').replace(/<svg[^>]*>|<\/svg>/g, '')}</g>
</svg>`;

const renderPng = (source, size) => {
  const resvg = new Resvg(source, {
    fitTo: { mode: 'width', value: size },
    background: 'rgba(0,0,0,0)',
  });
  return resvg.render().asPng();
};

const writePng = (source, size, path) => {
  const png = renderPng(source, size);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, png);
  console.log(`wrote ${path.replace(repo + '\\', '').replace(/\\/g, '/')} (${size}px, ${png.length} bytes)`);
};

// Android adaptive layers: 108dp total → mdpi 108 / hdpi 162 / xhdpi 216 /
// xxhdpi 324 / xxxhdpi 432. Foreground art is centered in the 66dp safe zone
// by the SVG itself.
const ADAPTIVE_DENSITIES = [
  ['mipmap-mdpi', 108],
  ['mipmap-hdpi', 162],
  ['mipmap-xhdpi', 216],
  ['mipmap-xxhdpi', 324],
  ['mipmap-xxxhdpi', 432],
];
// Legacy launchers (pre-8.0) keep 48dp launch icons: 48/72/96/144/192.
const LEGACY_DENSITIES = [
  ['mipmap-mdpi', 48],
  ['mipmap-hdpi', 72],
  ['mipmap-xhdpi', 96],
  ['mipmap-xxhdpi', 144],
  ['mipmap-xxxhdpi', 192],
];

for (const [dir, size] of ADAPTIVE_DENSITIES) {
  writePng(bg, size, join(res, dir, 'ic_launcher_background.png'));
  writePng(fg, size, join(res, dir, 'ic_launcher_foreground.png'));
  writePng(mono, size, join(res, dir, 'ic_launcher_monochrome.png'));
}
for (const [dir, size] of LEGACY_DENSITIES) {
  writePng(brandFull, size, join(res, dir, 'ic_launcher.png'));
  writePng(roundSvg(size), size, join(res, dir, 'ic_launcher_round.png'));
}

// Web favicons (favicon.svg stays the vector source; PNG for ico-less engines)
writePng(brandFull, 16, join(assets, 'favicon-16.png'));
writePng(brandFull, 32, join(assets, 'favicon-32.png'));
writePng(brandFull, 48, join(assets, 'favicon-48.png'));
writePng(brandFull, 180, join(assets, 'apple-touch-icon-180.png'));

// Play Store listing icon: full-bleed 512x512 (no alpha allowed in listing).
const playstore512 = renderPng(
  brandFull.replace('<rect width="512" height="512" rx="96"', '<rect width="512" height="512"'),
  512,
);
writeFileSync(join(brand, 'playstore-512.png'), playstore512);
console.log(`wrote assets/brand/playstore-512.png (512px, ${playstore512.length} bytes)`);
console.log('done: android mipmaps + web favicons + playstore 512 generated from assets/brand/*.svg');
