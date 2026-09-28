# B101 — Field Snapshot Core

Date: 2026-09-29 (Asia/Taipei)

## Goal

Freeze the exact forecast inputs and model outputs used by one ChaseLights
execution so the same scene can be replayed after scoring logic changes.

B101 is an engineering/reproducibility tool. A Field Snapshot is **not** a
Field Validation Case and is not field ground truth.

## Core contract

Snapshot flow:

```
provider response
  -> ChaseLights normalization
  -> runtime diagnostics
  -> Opportunity scoring
  -> immutable FVS snapshot
```

Replay flow:

```
immutable normalized input
  -> selected ChaseLights Git version
  -> runtime/scoring
  -> structured diff against recorded output
```

Replay must never fetch current weather.

## Snapshot identity

IDs use capture time, not forecast-valid hour:

```
FVS-TW-034-YYYYMMDD-HHMMSS
```

`captured_at` and `forecast_valid_at` are separate fields. This permits
multiple snapshots of the same forecast hour and makes provider forecast
revisions visible.

## Schema

Current schema:

`field-snapshot-r4.2-1`

A snapshot contains:

- Place identity,
- capture time,
- forecast-valid time / epoch,
- timezone and language,
- full Git commit SHA,
- adapter/catalog/runtime/spatial version provenance,
- raw camera Open-Meteo response,
- raw spatial Open-Meteo response,
- exact spatial request plan,
- normalized one-hour model input,
- recorded runtime diagnostics,
- recorded Theme metrics,
- recorded Opportunity scores,
- an observation block fixed to `unreviewed`,
- SHA256 payload integrity.

The raw snapshot is immutable. Future schema migration must happen in memory
during replay and must never rewrite an old snapshot in place.

## Same-run capture requirement

B101 adds an optional `snapshot_sink` to `fetch_weather_for_spot()`.

When unused, production follows the normal forecast path.

When used by `field_snapshot.py capture`, the sink receives the data from the
same execution that produced the Opportunity scores:

- provider camera payload,
- provider spatial payload,
- request geometry,
- normalized `item_data`,
- runtime diagnostics,
- Theme scores,
- Opportunity scores.

The capture tool must not perform a second weather request after scoring merely
to reconstruct the snapshot.

## Local storage

Default storage:

`.snapshots/`

The directory is gitignored.

Snapshots are created with write-once filesystem semantics. Existing snapshot
files are never overwritten.

Reviewed field-validation fixtures remain a separate repository artifact under
`test_fixtures/field_validation/`.

## CLI

Capture nearest forecast row to current time:

```bash
python field_snapshot.py capture --place tw-034
```

Capture nearest forecast row to an explicit offset-aware time:

```bash
python field_snapshot.py capture \
  --place tw-034 \
  --valid-at 2026-09-29T06:00:00+08:00
```

Validate integrity/schema:

```bash
python field_snapshot.py validate .snapshots/FVS-....json
```

Human-readable recorded result:

```bash
python field_snapshot.py show .snapshots/FVS-....json
```

Replay with current checkout:

```bash
python field_snapshot.py replay .snapshots/FVS-....json
```

Replay using the snapshot's original commit:

```bash
python field_snapshot.py replay .snapshots/FVS-....json --original
```

Replay a specific B101-or-later commit:

```bash
python field_snapshot.py replay .snapshots/FVS-....json --commit <sha>
```

Matrix replay:

```bash
python field_snapshot.py matrix .snapshots/FVS-....json \
  --commits original <sha1> <sha2> current
```

## Version replay boundary

Cross-version replay is implemented with a detached Git worktree.

The target checkout executes its own `field_snapshot.py`, therefore the target
model's runtime/catalog code evaluates the same immutable normalized input.

This replay contract begins at B101. A commit older than B101 does not contain
the contract and must return an explicit unsupported error rather than silently
using current code.

Every future B101-or-later change to snapshot schema must retain a compatibility
reader for older admitted snapshot schema versions if cross-version replay is
expected.

## Replay diff

The stable comparison currently covers each Opportunity's:

- score,
- condition state,
- score confidence,
- runtime eligibility,
- temporal eligibility,
- runtime reason,
- directional mist negative-evidence flag,
- directional mist availability/eligibility/reason,
- target/mist/clear counts,
- broad-clear-target-sector flag.

User-facing localized prose is intentionally not the primary regression key.

## Qingshui B101 regressions

### Broad-clear negative evidence

Synthetic normalized input:

- camera visibility: 0.8 km,
- six directional proxy targets,
- 330° / 0° / 30° at 2.5 / 5.0 km,
- all six targets clear,
- three clear bearings,
- no mist targets.

Required runtime behavior:

- `tw-034-P03` ineligible,
- reason `directional_target_sector_lacks_mist_support`,
- `directional_mist_negative_evidence = true`,
- broad-clear target sector true.

Exact replay must match the recorded stable outcome.

### Missing spatial context

Same low camera visibility with no spatial observation:

- P03 remains eligible as the conservative visibility-only candidate,
- minimum-sufficient score hint remains 68,
- confidence remains low,
- negative-spatial evidence remains false.

Exact replay must match the recorded stable outcome.

## Ground-truth boundary

Every B101 snapshot starts with:

```json
{
  "observation": {
    "status": "unreviewed"
  }
}
```

A snapshot may be associated with an actual photograph later, but it does not
become an `FV-...` registry case automatically.

Promotion to field validation remains governed by B86/B99:

- observed scene,
- exact capture time/direction,
- structured profile fields,
- provenance,
- limitations,
- review/admission.

## Raw versus normalized replay

B101 guarantees **normalized exact replay** and preserves the camera/spatial raw
weather payload needed for future parser/rebuild work.

Full provider-to-normalization rebuild replay for every external provider
(marine, tide, aurora, dynamic access) is intentionally not claimed by B101.
Those providers remain frozen at their normalized one-hour samples in
`normalized_input` for exact scoring replay.

A later batch may extend raw-provider coverage without changing the immutable
B101 records.

## CI / Definition of Done

B101 is complete when:

1. `field_snapshot.py` compiles.
2. Same-run capture hook does not affect ordinary production calls.
3. Snapshot writes are immutable/write-once.
4. SHA256 detects tampering.
5. Validation is offline.
6. Current replay is offline.
7. Original/specific-commit replay is target-version aware.
8. Future B101+ commits can participate in matrix replay.
9. Snapshot remains explicitly non-ground-truth.
10. Qingshui broad-clear veto regression passes.
11. Qingshui missing-spatial fallback regression passes.
12. Existing Opportunity adapter regression remains green.
