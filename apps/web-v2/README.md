# ChaseLights V2 — independent static research explorer

**Scope:** Worker 4 owns only this directory. No legacy index.html, production UI, or weather runtime was modified.

## Entry and deployment

GitHub Pages currently builds from repository root. Once this directory is merged to the deployed root branch, the candidate path is:

https://gdrabbit137-ai.github.io/ChaseLights/apps/web-v2/

This URL is **not** proof of deployment until the Pages run succeeds and an HTTP/browser check confirms the page. It is deliberately not linked from the legacy site; Worker 5 owns that link.

## Current data state

There is **no committed V2 dataset or forecast fixture** in this directory. On first load, the UI attempts a same-directory \`catalog.v2.json\` (optional future Worker 2 publication); if missing, it displays a transparent no-data state. Users may import a V2 JSON file locally using the file picker. Imported data stays in the browser and is not uploaded.

The interface consumes V2 collections named \`places\`, \`opportunities\`, \`camera_zones\`, \`subject_geometries\`, \`view_relations\`, \`condition_contracts\`, \`conditions\`, \`evidence\`, \`research_status\`, \`unknowns\`, and optional \`evaluations\`. This is a **temporary read-only adapter**, not a second canonical schema. When Worker 1 publishes \`specs/v2\`, adapt this reader to the authoritative schema and add a contract test. Worker 2 must publish real researched data, with provenance and localized semantic content, before any cards can be considered validated V2 content.

## Runtime boundary (Worker 3)

An evaluation is shown only if it explicitly declares \`kind: "runtime"\`, \`contract_status: "ready"\`, \`source\`, and \`generated_at\`. Otherwise, no score, verdict, date-specific recommendation, or synthetic weather is displayed. Runtime integration and freshness contracts require Worker 3 confirmation; do not promote research status to a forecast.

## R4.2 / navigation / localization constraints

- Place-specific evidence proves **what** can be photographed; runtime evaluates **when**.
- Camera Zone, Photo Target / Subject, and Navigation Target are separate. Missing relation geometry remains unknown; never derive GPS, azimuth or distance from a name or photo.
- Verified Navigation Targets may produce exact-coordinate Directions. Provisional camera anchors may produce coordinate-only map pins. Unverified/multiple routes have no navigation link. No \`map_query\` fallback.
- zh-TW / en / ja interface copy is complete. Imported semantic fields missing an equivalent locale remain explicitly untranslated, rather than silently falling back to Chinese or inventing translated claims. Proper names can retain original-language names.
- Source generation time and local loading time are separate. No sample data is presented as live data.
- Evidence/unknown/condition details are available in an expandable technical section, not automatically pushed into the main photographer decision surface.

## Verification

\`node --test apps/web-v2/tests/model.test.mjs\`

Manual browser checks: phone/desktop layout; keyboard selection; language switching; no-data state; local JSON import; a known V2 research record with no evaluation; missing translations; unsafe evidence URL; verified vs provisional vs pending navigation; generated-vs-loaded timestamps.

## Open integration gates

1. Worker 1: authoritative V2 schema and strict schema-version validation.
2. Worker 2: verified localized V2 research catalog, evidence, geometry, source timestamps.
3. Worker 3: runtime evaluation payload and calibration/freshness status.
4. Worker 5: optional link from legacy production site.
5. Deployment: verify the actual Pages build and live URL before announcing availability.
