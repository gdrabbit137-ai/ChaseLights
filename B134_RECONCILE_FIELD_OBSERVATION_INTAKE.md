# B134 — Reconcile Field Observation Intake on Current Main

Date: 2026-09-30 (Asia/Taipei)

> **Status: historical implementation/reconciliation record — not the current policy source-of-truth.**
> Current production Field Intake observation-association and photographer-facing UX policy is owned by `RESEARCH_EVIDENCE_SPEC_R4_2.md` §14. Navigation semantics remain owned by `NAVIGATION_SPEC_R4_2.md`. If this record conflicts with the latest effective specification on `main`, the formal specification wins. B134 MUST NOT be used to reintroduce superseded behavior such as silently confirming a nearest Place.

## Goal

Rebase the previously completed B120 local-first field-observation intake onto the current ChaseLights main without regressing the newer mobile/desktop UI, WeatherGrid, region filters, or scoring work.

## Preserved B120 contract

- original photo bytes remain in the browser;
- EXIF is parsed client-side;
- no observation API or object-storage upload is introduced;
- precise GPS is omitted from exported JSON by default;
- every export remains `status=unreviewed`;
- an observation draft is not an admitted `FV-...` case and cannot change scoring automatically.

## B134 reconciliation changes

1. The main header exposes the field-intake page beside WeatherGrid using the current responsive header style.
2. The header label participates in the existing Traditional Chinese / English / Japanese UI translation system.
3. Weak GPS matches are fail-closed: if the nearest researched Place is more than 5 km away, it is shown as a candidate but is not preselected. The user must choose a Place manually.
4. The B120 smoke workflow watches the main-page integration files as well as the intake assets.
5. The implementation is rebuilt directly on the current main rather than merging the stale B120 branch history.

## Still intentionally out of scope

- authentication;
- server-side persistence;
- image/thumbnail upload;
- public galleries;
- AI image analysis;
- automatic field-validation admission;
- scoring changes.

Those require a separate reviewed upload/storage/privacy contract.
