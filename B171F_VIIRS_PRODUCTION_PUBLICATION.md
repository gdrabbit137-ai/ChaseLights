# B171f — VIIRS production publication

## Problem

B171e samples `weathergrid/viirs_nightlights_tw_browser.json` and its QC sidecar at forecast runtime, but the B169 live ingest workflow previously uploaded those files only as a short-lived GitHub Actions artifact. They were therefore not guaranteed to exist in the repository/runtime filesystem.

## Contract

- VNP46A4 ingestion remains manual/annual rather than coupled to the GFS refresh cadence.
- The workflow validates product identity, DOI, semantics and requires an empty artifact-wide QC flag list before publication.
- Only the compact browser JSON and QC JSON are committed to `weathergrid/`.
- Source HDF5 tiles and cache files are never committed.
- Publication rebases/retries against `main`.
- If ingest or validation fails, no new VIIRS snapshot is published. Existing B169f/B171e consumers continue to fail closed when a valid local artifact is absent.
- This does not convert radiance to Bortle/SQM and does not change Opportunity scores.

## Scope

Taiwan only. Region-aware VIIRS routing for Japan, the United States and later regions remains future work.
