# B91 — Qingshui B81/B82 Mainline Regression and Directional-Mist Contrast Hardening

Date: 2026-09-28 (Asia/Taipei)

## Scope

This checkpoint verifies the effective mainline behavior for:

- `tw-034-P03 — 清水斷崖晨霧、雲霧山海`
- `tw-034-P02 — 清水斷崖山海遠眺`

The effective behavior is not B81/B82 alone. Current main also includes the B87 camera-readability guard and the B88 hard 68-point ceiling for low-readability mist candidates.

## Evidence boundary for the 2026-09-28 case

The repository does **not** contain a structured Qingshui Cliff field-observation case for 2026-09-28.

The 0.7–0.8 km values used by B81/B88 tests are therefore treated as an investigated regression scenario, not as proof that a Qingshui field observation on that morning measured 0.7–0.8 km visibility or confirmed mist at the cliff.

The structured field-validation registry for 2026-09-28 covers the separate Qixingtan 13:00 case. Do not conflate that ground truth with Qingshui.

## Archived production-weather comparison

The generated Qingshui detail shard immediately after B82 was merged and regenerated at commit:

- B82 merge: `e8211e4f0b3f69b4d995c87d29cbdcfabbb1d061`
- post-B82 weather generation: `ddbcf584de7a17be376c2be0b37ab2a8256408cb`

That archived 2026-09-28 morning forecast was broadly clear at the camera grid:

- 06:00: visibility 33.4 km; P02 score 93; P03 rejected because visibility was too high for the mist subject.
- 07:00: visibility 30.0 km; P02 score 93; P03 rejected.
- 08:00: visibility 29.9 km; P02 score 89; P03 rejected.
- 09:00: visibility 29.9 km; P02 score 88; P03 rejected.
- 10:00: visibility 28.7 km; P02 score 87; P03 rejected.
- 11:00 and later: P03 is additionally outside the verified morning-mist window.

Therefore the archived production snapshot itself demonstrates the clear-cliff side of the transition, but it does **not** contain the synthetic 0.7–0.8 km morning case.

## Required regression behavior

### 1. Low visibility, not local whiteout

At about 0.7–0.8 km camera visibility, with no corroborating fog / near-saturation / low-cloud signal:

- P03 may remain eligible only as a low-confidence planning candidate.
- score hint: 68.
- final Opportunity score: <= 68.
- status: uncertain mist candidate.
- this must not be described as confirmed cliff mist.

### 2. B82 north-sector proxies

The optional directional samples are:

- bearings: 330°, 0°, 30°
- ranges: 2.5 km and 5.0 km
- six target samples total plus the camera sample.

Each of the three verified broad bearings must be able to supply directional context when its target sample is materially mistier than the camera.

The proxy is an environmental planning proxy only. It does not prove the exact fog location or exact fog/cliff overlap.

### 3. Directional promotion requires camera-vs-target contrast

A target fog weather code (45/48) is not, by itself, directional evidence when the camera grid reports the same fog state.

If camera and target both carry fog code and there is no material contrast in:

- visibility,
- low-cloud cover, or
- relative humidity,

then the directional module must return:

- `eligible = false`
- `reason = directional_mist_not_distinguished_from_camera`

Local non-directional mist evidence may still keep P03 viable according to the B81/B87/B88 contract; it simply must not receive a directional promotion.

### 4. Low camera readability overrides directional support

If directional proxies support mist but camera visibility is below the conservative 2.5 km composition-readability guard:

- preserve the mist candidate,
- confidence stays low,
- `subject_readability_uncertain = true`,
- final score remains capped at 68.

The 2.5 km threshold is a planning guard derived from the nearest B82 proxy range, not an asserted physical camera-to-cliff distance.

### 5. Afternoon exclusion

P03 is a verified morning subject. Local time >= 11:00 must fail the P03 runtime gate even if visibility, RH, low cloud, or fog code would otherwise support mist.

This prevents afternoon low visibility from being mislabeled as the verified morning-mist Opportunity.

### 6. Clear-cliff recovery

When visibility recovers later in the morning:

- P03 must become ineligible once visibility is too high for the mist subject.
- P02 must be allowed to regain the higher score when its clear-cliff visibility conditions are satisfied.
- winner selection must not remain sticky on P03.

## B91 implementation

B91 adds/changes:

1. `spatial_weather.py`
   - hardens B82 directional contrast semantics.
   - target fog code only supplies contrast by itself when the camera is not also reporting fog.
   - bumps spatial runtime version.

2. `test_opportunity_adapter.py`
   - verifies all 330° / 0° / 30° bearings can independently supply directional context.
   - adds equal-camera-and-target fog regression; this must not count as directional contrast.
   - adds a low-visibility P03 -> recovered-visibility P02 winner-transition regression.
   - retains the B81 low-confidence candidate, whiteout veto, B87/B88 score cap, and afternoon-gate tests.

3. canonical catalog / evidence registry
   - explicitly state that north-sector confidence promotion requires a real camera-vs-target contrast.
   - preserve the existing evidence boundary and 68-point readability cap.

## Remaining data gaps

The following are still not established by current repository evidence:

- a Qingshui-specific 2026-09-28 field photograph / observation paired with the P03 runtime diagnostics,
- measured cliff-outline readability as a function of camera-grid visibility,
- enough positive and negative field labels to calibrate whether 2.5 km should move,
- enough spatial ground truth to decide whether one mistier proxy point is sufficient or whether future policy should require multi-bearing coherence.

Until those data exist, do not raise the low-confidence cap or claim exact fog/cliff overlap.
