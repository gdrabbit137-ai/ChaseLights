#!/usr/bin/env node
/** End-to-end smoke for the actual public V2 Research-only URL, never localhost. */
import assert from "node:assert/strict";
import {createRequire} from "node:module";
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {verifyResearchPage,verifyPhotographyTopics} from './browser_contract.mjs';
import {validateManifest,verifyPublicAsset,verifyPublicIndex,runtimeFiles} from './public_source_contract.mjs';
import {setTimeout as delay} from "node:timers/promises";

const UI=process.env.V2_PUBLIC_UI || 'existing-preview';
assert.ok(['existing-preview','existing-beta','forecast-home'].includes(UI),'Explicit public UI generation required');
const HOME=UI==='existing-beta'||UI==='forecast-home';
let expectedManifest=null;
if(UI==='forecast-home'){
  assert.ok(process.env.V2_EXPECTED_BUILD_MANIFEST,'Candidate public smoke requires an exact build manifest');
  expectedManifest=JSON.parse(await readFile(process.env.V2_EXPECTED_BUILD_MANIFEST,'utf8'));

}
if(UI==='existing-beta')expectedManifest=JSON.parse(await readFile(new URL('./public-beta-r3-manifest.json',import.meta.url),'utf8'));
if(expectedManifest)validateManifest(expectedManifest);
console.log('PUBLIC SMOKE SCOPE',UI==='forecast-home'?'PUBLISHED_CANDIDATE_EXACT_MANIFEST':'EXISTING_PUBLIC_PREVIEW_NOT_CANDIDATE');
const BASE = "https://chaselights.app/apps/web-v2/";
const LOCALES = ["zh-TW", "en", "ja"];
const require = createRequire(import.meta.url);
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || "playwright");

// CL-INT-76: provenance expectations are read from the repo's own build/pin
// artifacts, never hardcoded sha literals — when the catalog is regenerated
// (new canonical commit) the artifacts move and this smoke follows instead of
// silently going red. The block below is slice-tested in
// tests/cl-int-76-provenance.test.mjs with simulated regeneration fixtures.
// BEGIN provenance-artifact block
const repoCatalog=JSON.parse(await readFile(new URL('../../apps/web-v2/catalog.v2.json',import.meta.url),'utf8'));
const legacySourceCommitSha=JSON.parse(await readFile(new URL('./integration-sources.json',import.meta.url),'utf8')).sources.w2.canonical_content_sha;
// END provenance-artifact block

async function fetchPublic(path, maxAttempts = 3) {
  const address = new URL(path, BASE);
  assert.equal(address.origin, "https://chaselights.app");
  assert.ok(address.pathname.startsWith("/apps/web-v2/"));
  let last;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await fetch(address, {
        headers: {"cache-control": "no-cache", "user-agent": "ChaseLights-V2-PublicSmoke/1"},
        signal: AbortSignal.timeout(20000),
      });
      const body = await response.text();
      if (response.status === 200 && body.length > 0) {
        if (response.url && new URL(response.url).hostname !== "chaselights.app")
          throw new Error("Unexpected public host redirect " + response.url);
        return {response, body, address: address.href};
      }
      last = new Error(address + " HTTP " + response.status + " body " + body.slice(0, 140));
    } catch (error) { last = error; }
    if (attempt < maxAttempts) await delay(5000);
  }
  throw last;
}

let html = await fetchPublic("");
if(UI==='forecast-home'){
  for(let attempt=0;attempt<24 && createHash('sha256').update(html.body).digest('hex')!==expectedManifest.files['apps/web-v2/index.html'];attempt++){
    await delay(15000);
    html=await fetchPublic('');
  }
}
assert.match(html.response.headers.get("content-type") || "", /text\/html/i);
assert.match(html.body, /ChaseLights V2/);
if(expectedManifest)assert.equal(createHash('sha256').update(html.body).digest('hex'),expectedManifest.files['apps/web-v2/index.html']);
const legacyAssets = ["styles.css", "app.mjs", "model.mjs", "catalog-loader.mjs",
                "v21-adapter.mjs", "catalog.v2.json"];
const assets=HOME?runtimeFiles.filter(x=>x!=='index.html'):legacyAssets;
for (const path of assets) {
  const found = await fetchPublic(path);
  // The not-HTML guard detects JSON-fallback 404 pages; additional packaged
  // research pages (weather-pilot.html) are legitimately served as HTML and
  // are byte-verified against the manifest below instead.
  if(!path.endsWith('.html'))assert.ok(!/text\/html/i.test(found.response.headers.get("content-type") || ""),
            path + " served as HTML, likely fallback/404");
  if(expectedManifest)verifyPublicAsset(expectedManifest,path,found.body);
  console.log("ASSET PASS", path, found.response.status,
              found.response.headers.get("content-type"), found.body.length);
}
const catalog = JSON.parse((await fetchPublic("catalog.v2.json")).body);
assert.equal(catalog.research_only, true);
assert.equal(catalog.selected_date_recommendation_eligible, false);
assert.equal(catalog.forecast_available, false);
assert.deepEqual(catalog.evaluations, []);
// Full breadth migration is published (PR #533): the live pilot grew from the
// 7-place preview to the admitted 189-place / 353-opportunity catalog. The
// byte-exactness guarantee is the per-file digest verification against the
// pinned manifest; these counts are the breadth sanity assertions.
assert.equal(catalog.opportunities.length, HOME?356:1);
if(HOME){
  assert.equal(catalog.places.length,190);
  verifyPublicIndex(expectedManifest,catalog,JSON.parse((await fetchPublic('browse-index.v2.json')).body));
  // Same-origin pin check: the live candidate catalog must declare exactly the
  // source pins the repo's own build artifact declares (structural comparison;
  // survives catalog regeneration because both sides move together).
  assert.deepEqual(catalog.source_pins,repoCatalog.source_pins);
}else assert.equal(catalog.source_commit_sha, legacySourceCommitSha);
const opportunity = HOME ? catalog.opportunities.find(x=>x.opportunity_id==='tw-026-P01') : catalog.opportunities[0];
assert.equal(opportunity.opportunity_id, "tw-026-P01");
assert.equal(opportunity.readiness.research_level, "R1");
assert.ok(opportunity.navigation_targets.every(x => x.status !== "verified"));
for (const locale of LOCALES) {
  assert.ok(opportunity.name_i18n[locale]?.trim(), "Missing localized name");
  assert.ok(opportunity.camera_contexts[0].access_notes_i18n[locale]?.trim(),
            "Missing access warning");
}
console.log("RESEARCH SAFETY FLAGS PASS", "No live score or fabricated Directions");

// After the actual GitHub Pages deployment, require the legacy V1 page to be
// publicly reachable.  The dedicated "🧭 V2 研究預覽" header entry was
// deliberately removed from the V1 shell (V2 subjects are now the main UI;
// apps/web-v2/ data endpoints remain) — the removed link must NOT be required
// here, only same-origin reachability of the legacy page and its script.
if (process.env.REQUIRE_PUBLIC_V1_LINK === "true") {
  const rootResponse = await fetch("https://chaselights.app/", {
    headers: {"cache-control": "no-cache", "user-agent": "ChaseLights-V2-LinkSmoke/1"},
    signal: AbortSignal.timeout(20000),
  });
  assert.equal(rootResponse.status, 200, "Legacy root is not publicly reachable");
  const legacyHtml = await rootResponse.text();
  assert.doesNotMatch(legacyHtml, /href="\.\/apps\/web-v2\/"[^>]*data-i18n="v2_link"/,
               "Removed V2 header entry must stay removed from the V1 shell");
  const legacyScriptResponse = await fetch("https://chaselights.app/assets/app.js", {
    headers: {"cache-control": "no-cache"},
    signal: AbortSignal.timeout(20000),
  });
  assert.equal(legacyScriptResponse.status, 200);
  console.log("PUBLIC V1 REACHABLE PASS: legacy page published, removed V2 entry stays removed");
}

const browser = await chromium.launch({
  headless: true,
  ...(process.env.CHROMIUM_EXECUTABLE
    ? {executablePath: process.env.CHROMIUM_EXECUTABLE} : {}),
  args: ["--no-sandbox"],
});
const devices = [
  {name: "desktop", viewport: {width: 1440, height: 1000}, isMobile: false},
  {name: "mobile", viewport: {width: 390, height: 844}, isMobile: true},
];
let total = 0;
try {
  for (const device of devices) {
    const context = await browser.newContext({
      viewport: device.viewport,
      isMobile: device.isMobile,
      hasTouch: device.isMobile,
    });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    await page.goto(BASE, {waitUntil: "domcontentloaded", timeout: 45000});
    assert.equal(new URL(page.url()).hostname, "chaselights.app");
    for (const locale of LOCALES) {
      // placeCount / expectedOpportunities come from the LIVE catalog: the
      // public page is a 7-place research pilot, so the count assertions must
      // compare against what the live catalog itself declares.
      await verifyResearchPage(page,opportunity,locale,HOME?'forecast-home':UI,catalog.places.length,
        catalog.opportunities.filter(x=>x.place_id===opportunity.place_id).length);
      if(UI==='forecast-home')await verifyPhotographyTopics(page,catalog,locale);
      assert.deepEqual(errors,[],"Browser errors on "+device.name+" "+locale);
      console.log("PUBLIC BROWSER PASS",device.name,locale,UI,"source-exact","access-warning-separated","no-directions");
      total++;
    }
    await context.close();
  }
} finally { await browser.close(); }
assert.equal(total, 6);
console.log("PUBLIC V2 PREVIEW PASS: 6/6 locale-device combinations, 0 errors", "scope="+UI);
