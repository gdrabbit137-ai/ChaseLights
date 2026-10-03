# B120 — Field Observation Intake MVP

Date: 2026-09-29 (Asia/Taipei)

> **Status: historical implementation handoff / MVP record — not the current policy source-of-truth.**
> Current Field Intake observation-association and photographer-facing UX requirements are owned by `RESEARCH_EVIDENCE_SPEC_R4_2.md` §14. Navigation semantics remain owned by `NAVIGATION_SPEC_R4_2.md`. If this B120 record conflicts with the latest effective specification on `main`, the formal specification wins. Statements below describe the B120 implementation at the time it was delivered and MUST NOT be used to reintroduce superseded behavior such as silent Place confirmation.

## Goal

Add the first user-facing field-observation intake surface to the ChaseLights website without turning ChaseLights into a photo-hosting service.

B120 is deliberately local-first:

- the selected image stays in the browser,
- EXIF metadata is parsed client-side,
- no image bytes are uploaded,
- precise GPS is not included in an exported draft unless the user explicitly enables it,
- the result is an `unreviewed` observation draft, never automatic field ground truth.

## Product flow

```
select JPEG / HEIC / HEIF
  -> browser-local EXIF parse
  -> capture time / GPS / camera metadata
  -> nearest researched Place match from runtime catalog viewpoints
  -> user confirms or overrides Place
  -> optional consent flags
  -> download structured observation draft JSON
```

The initial page is `field-intake.html`.

## Metadata parser

The browser page uses the pinned `exifr` 7.1.3 lite browser bundle from jsDelivr.

The parser supports JPEG and HEIC/HEIF EXIF/GPS in the browser. The library is loaded from a third-party CDN, but selected photo bytes are passed directly to the in-browser parser and are not sent to ChaseLights.

If the parser cannot load, the page must fail closed and clearly state that metadata parsing is unavailable. It must never fall back to uploading the file elsewhere.

## Place matching

B120 does not introduce another Place database.

The page loads `runtime_catalog_v004_r4_2.json` and builds a lightweight in-memory Place index from researched Opportunity viewpoints.

When EXIF GPS is available:

1. collect unique viewpoint coordinates for each catalog Place,
2. compute great-circle distance from the photo GPS to every viewpoint,
3. choose the nearest Place/viewpoint,
4. matches over 5 km are treated as weak: the page shows the nearest candidate but does not preselect it, so the user must choose a Place manually.

The user may always override the automatic match.

If GPS is absent or stripped by a sharing workflow, the user selects a Place manually.

## Draft schema

Current browser draft schema:

`field-observation-draft-r4.2-1`

Important fields:

- `status = unreviewed`
- non-image file metadata
- EXIF capture time and camera metadata when available
- Place match and distance
- exact GPS only when the user explicitly opts in
- model-validation consent flag
- public-photo flag fixed to false in B120
- explicit ground-truth boundary

The draft is intentionally separate from:

- `field-validation-registry-r4.2-2`
- `field-snapshot-r4.2-1`

A future server-side admission flow may associate a reviewed draft with a Field Snapshot and later promote it into an `FV-...` case, but B120 never performs that promotion.

## Privacy and storage boundary

B120 performs no photo upload and creates no server-side record.

Default behavior:

- image bytes: local browser only
- exact GPS: local browser only
- exported draft: exact GPS omitted unless explicitly enabled
- public photo permission: false
- model-validation permission: false until checked

This preserves the B86/B99 rule that user-supplied images are not committed or published by default.

## Scaling path

Later batches may add:

1. authenticated users,
2. direct-to-object-storage thumbnail upload,
3. signed upload URLs,
4. observation API/database,
5. quota/rate limiting,
6. moderation,
7. async image analysis queue,
8. snapshot lookup by capture time,
9. reviewed promotion into field-validation cases.

Those features must not require changing the B120 local-first draft contract.

## Definition of done

1. `field-intake.html` is usable on desktop/mobile.
2. JPEG/HEIC/HEIF can be selected.
3. EXIF is parsed locally.
4. GPS auto-matches the nearest catalog Place when available.
5. Missing GPS supports manual Place selection.
6. Original image bytes are never uploaded.
7. Exact GPS is withheld from exported JSON by default.
8. Every exported record is `unreviewed`.
9. Static CI checks the privacy/storage boundary and JavaScript syntax.
10. Main site exposes an entry point to the intake page.
