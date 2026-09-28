# B103 — First Permanent Qingshui Live Snapshot Baseline

Date: 2026-09-29 (Asia/Taipei)

## Purpose

B103 exercises the B101 Field Snapshot Core against a real live ChaseLights
forecast execution and retains the result as a permanent replay fixture.

This batch does not change Qingshui scoring thresholds and does not create field
ground truth.

## Production source

The capture workflow intentionally checked out production commit:

`fadfc65aeb8e9219cec2b60fc0ed91bf9fc98e21`

That commit is the post-B101 production weather refresh following:

- B101 merge `fb92a51e4316e70c1352812d4b8f15ba7c7b1581`,
- successful main Adapter,
- successful all-region Weather Update,
- successful Pages deployment.

The workflow ran `field_snapshot.py capture --place tw-034` with
`GITHUB_SHA` removed from the capture process so provenance resolves from the
checked-out production commit rather than the temporary capture-workflow branch.

## Permanent baseline

Snapshot:

`FVS-TW-034-20260928-163925`

Permanent archive:

`test_fixtures/field_snapshot/FVS-TW-034-20260928-163925.json.gz.b64`

Metadata:

`test_fixtures/field_snapshot/FVS-TW-034-20260928-163925.metadata.json`

Registry:

`field_snapshot_baselines_r4_2.json`

The JSON snapshot is gzip-compressed and base64-wrapped for repository storage.
The archive contains the complete B101 snapshot, including provider camera and
spatial payloads, normalized input, request geometry, runtime diagnostics,
Opportunity outputs, provenance and integrity hash.

Snapshot integrity:

- captured at: `2026-09-28T16:39:25.329314+00:00`
- forecast valid at: `2026-09-28T17:00:00+00:00`
- forecast local time: `2026-09-29 01:00 +08:00`
- production commit: `fadfc65aeb8e9219cec2b60fc0ed91bf9fc98e21`
- payload SHA256: `0736bab3200a9d229a696d2ac896b737dba5e2484459c88a864c42496e341e6f`
- observation status: `unreviewed`

## Recorded Qingshui conditions

The captured 01:00 forecast row contained:

- camera visibility: 0.5 km,
- camera RH: 82%,
- camera low cloud: 41%,
- precipitation: 0 mm,
- wind: about 0.78 m/s,
- six north-sector directional targets,
- five mist targets,
- two directional-mist targets,
- zero clear targets,
- zero clear bearings,
- `broad_clear_target_sector = false`.

P03 runtime therefore reported:

- runtime eligible: true,
- reason: `camera_visibility_too_low_for_cliff_readability`,
- minimum-sufficient score hint: 68,
- low runtime-confidence hint,
- `directional_mist_negative_evidence = false`.

Because 01:00 is outside the visible-light Theme window, the final recorded P03
Opportunity was:

- score 38,
- medium score confidence,
- state `minimum_sufficient_weather_match_outside_time_window`.

This distinction is intentional: the subject-specific runtime can detect a
mist candidate while the final photographic Opportunity remains outside a
usable light window.

## Original replay

The capture workflow immediately ran the archived normalized input against its
production commit. Result:

- `match = true`,
- `different_opportunity_ids = []`.

This proves the first live B101 snapshot was reproducible before it was admitted
as a permanent baseline.

## Archive support

B103 extends `field_snapshot.py` so these commands accept either ordinary
`.json` snapshots or permanent `.json.gz.b64` fixtures:

```bash
python field_snapshot.py validate test_fixtures/field_snapshot/FVS-TW-034-20260928-163925.json.gz.b64

python field_snapshot.py show test_fixtures/field_snapshot/FVS-TW-034-20260928-163925.json.gz.b64

python field_snapshot.py replay test_fixtures/field_snapshot/FVS-TW-034-20260928-163925.json.gz.b64 --original

python field_snapshot.py matrix test_fixtures/field_snapshot/FVS-TW-034-20260928-163925.json.gz.b64 \
  --commits original current
```

When the target commit predates B103 archive support but still contains the
B101 replay contract, the current runner materializes a temporary JSON copy and
passes that immutable payload to the target checkout.

## Regression policy

The permanent baseline locks:

- snapshot provenance,
- raw/normalized input,
- recorded B101-era Opportunity output,
- archive integrity,
- ground-truth boundary.

Future scoring versions are **allowed** to produce a different replay result.
The purpose of matrix replay is to expose that difference, not force all future
models to reproduce B101 forever.

Therefore CI validates that:

- the archive decodes,
- B101 snapshot integrity still passes,
- recorded Qingshui values remain unchanged,
- current code can execute the baseline,
- Opportunity IDs remain replayable.

CI does not assert that every future current-model score must equal the recorded
B101 score.

## Ground-truth boundary

This remains a forecast-only baseline.

No photo was captured or attached.
No structured observed-scene judgment was admitted.
It must not be added to `field_validation_registry_r4_2.json`.

The next meaningful field-validation promotion still requires an actual
observed Qingshui scene with exact capture time/direction and the B99
`qingshui_cliff_mist` observation contract.
