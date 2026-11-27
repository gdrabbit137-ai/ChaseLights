// CL-UI-101 — site-wide 「資料來源與授權」 page (sources.html) + shared
// site-footer (commercial-compliance attribution: CC BY 4.0 / ODbL /
// 政府資料開放授權 1.0 …) + shooting-safety disclaimer.
// Covers: 1) sources.html shell (shared site-nav DOM, no active mark);
// 2) ALL required sources + original-language license names + canonical
//    attribution quotes + official-site links; 3) disclaimer section;
// 4) trilingual pack (nav + page keys, en/ja non-empty, zh-TW static markup);
// 5) site-wide footer: identical block on all six pages + cache-busted
//    widget script; 6) 390px rhythm; 7) cache-bust stamps coherent.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const read = (p) => readFileSync(join(root, p), 'utf8');

const indexHtml = read('index.html');
const wgHtml = read('weather-map.html');
const genreHtml = read('genre-eval.html');
const fieldHtml = read('field-intake.html');
const remHtml = read('reminders.html');
const srcHtml = read('sources.html');
const footerJs = read('assets/site-footer.js');

function navBlock(html) {
  const m = html.match(/<nav class="site-nav"[\s\S]*?<\/nav>/);
  assert.ok(m, 'site-nav <nav> block present');
  return m[0];
}
function normalized(html) {
  return navBlock(html).replace(/ data-active="page"/g, '');
}
function footerBlock(html) {
  const m = html.match(/<footer class="site-footer">[\s\S]*?<\/footer>/);
  assert.ok(m, 'site-footer <footer> block present');
  return m[0];
}

test('CL-UI-101 (1): sources.html shares the ONE site-nav DOM (no active mark)', () => {
  // The nav on sources.html must equal the shared nav (index's, active mark
  // stripped) so future strict-equal nav pins can include this page.
  assert.equal(normalized(srcHtml), normalized(indexHtml), 'sources nav DOM matches index');
  assert.doesNotMatch(navBlock(srcHtml), /data-active="page"/);
  // Sources page is reached from the footer, not the masthead.
  assert.doesNotMatch(navBlock(srcHtml), /sources\.html/);
});

const SOURCES = [
  { name: 'Open-Meteo', license: 'CC BY 4.0', links: ['https://open-meteo.com/'] },
  { name: 'CAMS', license: 'CAMS Data Licence (Copernicus)', links: ['https://atmosphere.copernicus.eu/'] },
  { name: '中央氣象署', license: '政府資料開放授權條款—1.0版', links: ['https://www.cwa.gov.tw/', 'https://data.gov.tw/license'] },
  { name: '気象庁', license: '気象庁ホームページ利用条件（出典表示）', links: ['https://www.jma.go.jp/jma/index.html'] },
  { name: 'Himawari-9', license: 'JAXA／JMA 利用条件（出典表示）', links: ['https://www.eorc.jaxa.jp/ptree/', 'https://www.data.jma.go.jp/mscweb/'] },
  { name: 'NOAA', license: 'Public Domain', links: ['https://www.noaa.gov/', 'https://www.usgs.gov/'] },
  { name: 'Wikipedia', license: 'CC BY-SA 4.0', links: ['https://www.wikipedia.org/', 'https://creativecommons.org/licenses/by-sa/4.0/'] },
  { name: 'OpenStreetMap', license: 'ODbL 1.0', links: ['https://www.openstreetmap.org/copyright'] }
];

test('CL-UI-101 (2): all required sources, original license names, official links', () => {
  for (const s of SOURCES) {
    assert.ok(srcHtml.includes(s.name), `source present: ${s.name}`);
    assert.ok(srcHtml.includes(s.license), `license name (original) present: ${s.license}`);
    for (const link of s.links) {
      assert.ok(srcHtml.includes(`href="${link}"`), `official link present: ${link}`);
    }
  }
  // Canonical attribution lines are language-invariant quotes.
  for (const quote of [
    'Weather data by Open-Meteo.com (CC BY 4.0)',
    'Contains modified Copernicus Atmosphere Monitoring Service information',
    'Himawari-9 imagery courtesy of JAXA and JMA',
    '© OpenStreetMap contributors'
  ]) {
    assert.ok(srcHtml.includes(quote), `canonical attribution present: ${quote}`);
  }
  // ODbL naming per the ticket.
  assert.ok(srcHtml.includes('開放資料庫授權（ODbL）'));
});

test('CL-UI-101 (3): disclaimer section — reference-only weather + self-responsibility', () => {
  assert.match(srcHtml, /src-disclaimer-title[^>]*>[\s\S]*?免責聲明/);
  assert.ok(srcHtml.includes('src_disclaimer_1'), 'disclaimer li 1');
  assert.ok(srcHtml.includes('src_disclaimer_2'), 'disclaimer li 2');
  assert.ok(srcHtml.includes('src_disclaimer_3'), 'disclaimer li 3');
  // The zh-TW static markup carries the two mandatory sentences.
  assert.ok(srcHtml.includes('僅供參考'), 'weather data reference-only wording');
  assert.ok(srcHtml.includes('拍攝安全自負'), 'shooting safety self-responsibility wording');
});

test('CL-UI-101 (4): sources page trilingual — nav + page keys in en/ja, zh-TW static', () => {
  const navM = srcHtml.match(/var NAV_I18N = \{[\s\S]*?\n      \};/);
  assert.ok(navM, 'NAV_I18N block present');
  const srcM = srcHtml.match(/var SRC_I18N = \{[\s\S]*?\n      \};/);
  assert.ok(srcM, 'SRC_I18N block present');
  for (const key of ['nav_cards', 'nav_weathermap', 'nav_my']) {
    assert.match(navM[0], new RegExp(`${key}: \\{ en: '[^']+', ja: '[^']+' \\}`), `${key} en+ja`);
  }
  const keyRe = /(\w+): \{ en: '((?:[^'\\]|\\.)*)', ja: '((?:[^'\\]|\\.)*)' \}/g;
  let m, count = 0;
  const seen = new Set();
  const flat = srcM[0].replace(/\s*\n\s*/g, ' ');
  while ((m = keyRe.exec(flat)) !== null) {
    count++;
    seen.add(m[1]);
    assert.ok(m[2].length > 0, `${m[1]} en non-empty`);
    assert.ok(m[3].length > 0, `${m[1]} ja non-empty`);
    assert.ok(!/provisional|draft|internal/i.test(m[2] + m[3]), `${m[1]} no internal wording`);
  }
  assert.ok(count >= 20, `expected >=20 trilingual keys, got ${count}`);
  for (const k of ['src_page_title', 'src_intro', 'src_disclaimer_1', 'src_disclaimer_2',
    'src_disclaimer_3', 'src_om_desc', 'src_cwa_attr', 'src_jma_attr']) {
    assert.ok(seen.has(k), `key present in SRC_I18N: ${k}`);
  }
  // Three languages switchable; ?lang= precedence handled in the inline script.
  for (const v of ['"zh-TW"', '"en"', '"ja"']) {
    assert.ok(srcHtml.includes(`value=${v}`), `lang option ${v}`);
  }
  assert.match(srcHtml, /chaselights_lang/);
  assert.match(srcHtml, /URLSearchParams\(location\.search\)\.get\('lang'\)/);
  // Per-language document titles.
  for (const t of ['ChaseLights — 資料來源與授權', 'ChaseLights — Data Sources & Licenses', 'ChaseLights — データソースとライセンス']) {
    assert.ok(srcHtml.includes(t), `title variant: ${t}`);
  }
});

const PAGES = {
  'index.html': indexHtml,
  'weather-map.html': wgHtml,
  'genre-eval.html': genreHtml,
  'field-intake.html': fieldHtml,
  'reminders.html': remHtml,
  'sources.html': srcHtml
};
const PAGE_NAMES = ['index.html', 'weather-map.html', 'genre-eval.html', 'field-intake.html', 'reminders.html', 'sources.html'];

test('CL-UI-101 (5): site-wide footer — identical block + cache-busted script on ALL pages', () => {
  const first = footerBlock(indexHtml);
  for (const name of PAGE_NAMES) {
    const html = PAGES[name];
    assert.equal(footerBlock(html), first, `${name} footer DOM matches index`);
    assert.match(html, /<a class="site-footer-link" href="\.\/sources\.html" data-sf-i18n="sf_sources">/);
    assert.match(html, /<script src="\.\/assets\/site-footer\.js\?v=sf01"><\/script>/, `${name} widget script (cache-bust stamp)`);
    assert.match(html, /data-sf-i18n="sf_note"/);
  }
  // Footer carries the compact safety disclaimer site-wide too.
  assert.ok(first.includes('氣象資料僅供參考'));
});

test('CL-UI-101 (6): site-footer.js — self-contained trilingual pack, no app.js edit', () => {
  for (const key of ['sf_sources', 'sf_note']) {
    assert.match(footerJs, new RegExp(`${key}: \\{ 'zh-TW': '[^']+', en: '[^']+', ja: '[^']+' \\}`), `${key} trilingual`);
  }
  assert.match(footerJs, /chaselights_lang/);
  assert.match(footerJs, /'@media \(max-width:390px\)/, '390px rhythm in the injected style');
  // Never edits app.js — no stamp bump needed for app assets this ticket.
  assert.match(indexHtml, /assets\/app\.js\?v=clui139/);
  assert.match(indexHtml, /assets\/app\.css\?v=clui139/);
});

test('CL-UI-101 (7): sources page shell — tokens via app.css, 390 media query', () => {
  assert.match(srcHtml, /assets\/app\.css\?v=/, 'app.css token layer loaded');
  assert.match(srcHtml, /assets\/site-nav\.css\?v=/, 'site-nav.css loaded');
  assert.match(srcHtml, /assets\/site-nav\.js/);
  assert.match(srcHtml, /assets\/member-auth\.js\?v=/);
  assert.match(srcHtml, /@media \(max-width: 390px\)/, '390 rhythm');
  assert.match(srcHtml, /var\(--cl-/g, 'uses live --cl-* tokens');
  // No color redefinition outside the token layer (CL-UI-85 spirit).
  assert.doesNotMatch(srcHtml.replace(/rgba\(255,\s*255,\s*255[^)]*\)/g, ''), /#[0-9a-fA-F]{3,8}\b/);
});
