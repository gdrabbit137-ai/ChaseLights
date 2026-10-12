#!/usr/bin/env node
/** End-to-end smoke for the actual public V2 Research-only URL, never localhost. */
import assert from "node:assert/strict";
import {createRequire} from "node:module";
import {setTimeout as delay} from "node:timers/promises";

const BASE = "https://chaselights.app/apps/web-v2/";
const LOCALES = ["zh-TW", "en", "ja"];
const require = createRequire(import.meta.url);
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || "playwright");

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

const html = await fetchPublic("");
assert.match(html.response.headers.get("content-type") || "", /text\/html/i);
assert.match(html.body, /ChaseLights V2/);
const assets = ["styles.css", "app.mjs", "model.mjs", "catalog-loader.mjs",
                "v21-adapter.mjs", "catalog.v2.json"];
for (const path of assets) {
  const found = await fetchPublic(path);
  assert.ok(!/text\/html/i.test(found.response.headers.get("content-type") || ""),
            path + " served as HTML, likely fallback/404");
  console.log("ASSET PASS", path, found.response.status,
              found.response.headers.get("content-type"), found.body.length);
}
const catalog = JSON.parse((await fetchPublic("catalog.v2.json")).body);
assert.equal(catalog.research_only, true);
assert.equal(catalog.selected_date_recommendation_eligible, false);
assert.equal(catalog.forecast_available, false);
assert.deepEqual(catalog.evaluations, []);
assert.equal(catalog.opportunities.length, 1,
             "Only the audited R1 P01 is eligible for this preview");
assert.equal(catalog.source_commit_sha, "2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd");
const opportunity = catalog.opportunities[0];
assert.equal(opportunity.opportunity_id, "tw-026-P01");
assert.equal(opportunity.readiness.research_level, "R1");
assert.ok(opportunity.navigation_targets.every(x => x.status !== "verified"));
for (const locale of LOCALES) {
  assert.ok(opportunity.name_i18n[locale]?.trim(), "Missing localized name");
  assert.ok(opportunity.camera_contexts[0].access_notes_i18n[locale]?.trim(),
            "Missing access warning");
}
console.log("RESEARCH SAFETY FLAGS PASS", "No live score or fabricated Directions");

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
    await page.locator(".opportunity").first().waitFor({state: "visible", timeout: 30000});
    assert.equal(await page.locator(".opportunity").count(), 1);
    for (const locale of LOCALES) {
      await page.locator("#language").selectOption(locale);
      assert.equal(await page.locator("#language").inputValue(), locale);
      const warning = page.locator(".access-advisories");
      await warning.waitFor({state: "visible"});
      assert.equal(await warning.getAttribute("role"), "note");
      const note = opportunity.camera_contexts[0].access_notes_i18n[locale];
      const safety = opportunity.camera_contexts[0].safety_notes_i18n[locale];
      const text = await warning.textContent();
      assert.ok(text.includes(note), locale + " missing exact source-backed access warning");
      assert.ok(text.includes(safety), locale + " missing safety warning");
      const conditions = await page.locator(".decision-core").textContent();
      assert.ok(!conditions.includes(note), locale + " access restriction leaked into photo rules");
      assert.equal(await page.locator(".decision-risks").count(), 0,
                   "Access warning must not be a photographic blocker");
      assert.equal(await page.locator(".nav-action").count(), 0,
                   "Unverified navigation directions must remain unavailable");
      const notices = await page.locator(".notice").allTextContents();
      assert.ok(notices.some(s => /not a live|No verifiable|沒有可驗證|検証可能/.test(s)),
                "Research-only, non-live status message is missing: " + locale);
      const overflow = await page.evaluate(() =>
        document.documentElement.scrollWidth - document.documentElement.clientWidth);
      assert.ok(overflow <= 1, "Horizontal overflow " + device.name + " " + locale + " " + overflow);
      assert.deepEqual(errors, [], "Browser errors on " + device.name + " " + locale);
      console.log("PUBLIC BROWSER PASS", device.name, locale,
                  "research-only", "access-warning-separated", "no-directions");
      total++;
    }
    await context.close();
  }
} finally { await browser.close(); }
assert.equal(total, 6);
console.log("PUBLIC V2 PREVIEW PASS: 6/6 locale-device combinations, 0 errors");
