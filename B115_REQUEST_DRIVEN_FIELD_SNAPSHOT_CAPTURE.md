# B115 — Request-Driven Field Snapshot Capture

Date: 2026-09-29 (Asia/Taipei)

## Purpose

B115 removes the need to create and delete a one-off GitHub Actions workflow for
every Field Snapshot capture.

After B115, a capture is requested by creating a short-lived branch named:

`snapshot-capture/<request-name>`

and adding one file:

`.field_snapshot_capture_request.json`

The fixed workflow:

`.github/workflows/field_snapshot_capture_request.yml`

then performs the capture.

This makes scheduled or assistant-driven capture much simpler and keeps capture
logic in one reviewed workflow.

## Request schema

Schema:

`field-snapshot-capture-request-r4.2-1`

Example:

```json
{
  "schema_version": "field-snapshot-capture-request-r4.2-1",
  "request_id": "FSCR-TW034-20260930-0400",
  "place_id": "tw-034",
  "valid_at": "2026-09-30T06:00:00+08:00",
  "capture_ref": "<40-character production Git SHA>",
  "scene_family": "qingshui_cliff_mist",
  "revision_group": "tw-034@2026-09-29T22:00:00+00:00",
  "persist": true
}
```

The request must use a full 40-character Git SHA for `capture_ref`.
Branch names such as `main` are intentionally rejected.

That makes the exact code version immutable even if production `main` advances
while the workflow is running.

## Capture flow

```
create snapshot-capture/* branch
  -> add .field_snapshot_capture_request.json
  -> fixed workflow validates request
  -> verify capture_ref
  -> detached production worktree
  -> field_snapshot.py capture
  -> validate
  -> replay --original
  -> metadata
  -> artifact upload
  -> optional permanent archive + registry entry
  -> remove request file
  -> commit result to request branch
```

The workflow does not capture from the request branch.

The request branch contains orchestration code and reviewable request metadata.
The actual forecast capture executes from the exact commit named in
`capture_ref`.

## Persist modes

### `persist: false`

The workflow:

- captures,
- validates,
- runs original replay,
- uploads an Actions artifact.

It does not change the baseline registry.

This mode is intended for smoke tests and temporary diagnostics.

### `persist: true`

The workflow additionally:

- gzip-compresses and base64-wraps the immutable snapshot,
- stores it under `test_fixtures/field_snapshot/`,
- creates capture metadata,
- appends a standardized baseline entry to
  `field_snapshot_baselines_r4_2.json`,
- removes the request file,
- commits the result back to the request branch.

The result branch is then ready for ordinary PR review and the existing Adapter,
Matrix Replay, and Forecast Revision Comparison checks.

## Registry entry

`field_snapshot_capture_request.py` creates a standardized registry entry from
the immutable snapshot.

It records:

- snapshot ID,
- Place,
- scene family,
- revision group,
- archive and metadata paths,
- capture and forecast-valid times,
- production commit,
- snapshot SHA256,
- observation status,
- request/workflow provenance,
- stable Opportunity summary,
- explicit limitations.

The standard Opportunity summary includes, when available:

- score,
- score confidence,
- condition state,
- runtime reason,
- minimum-sufficient score hint,
- runtime confidence hint,
- directional-mist negative evidence,
- target / mist / directional-mist / clear counts,
- broad-clear target-sector state.

## Ground-truth boundary

The capture-request path never promotes a forecast snapshot to field ground
truth.

All request-driven captures retain:

`observation.status = unreviewed`

and the registry entry explicitly states that the snapshot is not an observed
scene.

Promotion to an `FV-...` case still requires the separate B86/B99 field
validation process.

## Duplicate protection

The baseline registrar rejects a duplicate `snapshot_id`.

Existing permanent snapshot records are not overwritten.

## Capture-request CLI

Validate a request:

```bash
python field_snapshot_capture_request.py validate-request \
  .field_snapshot_capture_request.json
```

Create a request locally:

```bash
python field_snapshot_capture_request.py make-request \
  --request-id FSCR-TW034-20260930-0400 \
  --place tw-034 \
  --valid-at 2026-09-30T06:00:00+08:00 \
  --capture-ref <40-char-sha> \
  --scene-family qingshui_cliff_mist
```

Use `--artifact-only` to generate a `persist: false` request.

## Scheduled-task usage

The preferred scheduled flow after B115 is:

1. read latest production `main` SHA,
2. create a `snapshot-capture/*` branch from current main,
3. write one request JSON containing that full SHA,
4. allow the fixed workflow to perform the capture,
5. inspect the result commit and CI,
6. open/merge the result PR when validation passes.

A scheduled task no longer needs to author temporary GitHub Actions YAML.

## CI

B115 adds tests for:

- request schema validation,
- full-SHA requirement,
- offset-aware valid time,
- request metadata,
- standardized registry entry,
- duplicate registration rejection,
- ground-truth boundary.

The existing Adapter workflow compiles and runs these tests.

An artifact-only live smoke capture is also used during B115 development to
exercise the complete request-driven workflow without adding a permanent
baseline.

## Live integration verification

B115 was exercised through two real request branches before merge.

### Artifact-only smoke

Request:

`FSCR-B115-SMOKE`

Workflow run:

`36504287559`

Capture ref:

`f8a5615a6ba99733d0f040885bdfbf202d4ecd16`

Result:

- request validation passed,
- immutable production ref verification passed,
- detached production worktree capture passed,
- snapshot validation passed,
- original replay returned `match = true`,
- artifact upload passed,
- persistence step was correctly skipped.

Captured snapshot:

`FVS-TW-034-20260929-004146`

The smoke branch did not add a permanent baseline.

### Persist-path smoke

Request:

`FSCR-B115-PERSIST-SMOKE`

Workflow run:

`36504428603`

Capture ref:

`f8a5615a6ba99733d0f040885bdfbf202d4ecd16`

Captured snapshot:

`FVS-TW-034-20260929-004332`

Result:

- capture / validate / original replay passed,
- artifact upload passed,
- compressed fixture was written,
- standardized registry entry was appended,
- request file was removed,
- result commit was created automatically.

Result commit on the isolated smoke branch:

`ae52cdf3b80e1295c39caa0d20aad14c0bcd004c`

The generated registry entry preserved:

- request ID,
- workflow run ID,
- source branch,
- production commit,
- payload SHA256,
- `observation_status = unreviewed`,
- stable Opportunity summaries.

This smoke branch is intentionally not merged into production; it verifies the
persistence path without polluting the permanent baseline registry.

## Runtime impact

None on normal forecast generation or public UI.

B115 changes only Field Snapshot capture orchestration and baseline registration.
