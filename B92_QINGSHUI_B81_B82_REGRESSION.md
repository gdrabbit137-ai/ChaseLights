# B92 — Qingshui Cliff B81/B82 Mainline Verification and Regression Contract

Date: 2026-09-28 (Asia/Taipei)

## Scope

This note verifies the effective mainline behavior for:

- `tw-034-P03 — 清水斷崖晨霧、雲霧山海`
- `tw-034-P02 — 清水斷崖山海遠眺`

It specifically re-checks the B81/B82 intent after the later B87/B88 hardening.

Relevant merged commits:

- B81: `ba283b5e94720bf8f7a6af51deb21d05c609b8ae`
- B82: `e8211e4f0b3f69b4d995c87d29cbdcfabbb1d061`
- B87 readability guard: `49b007e509b4d0b943dba2a5b7aa1453987ba93c`
- B88 hard score cap: `bffe5d7728bf07bd5e5696a9ba3ae2827bef551e`

The effective contract on current main is therefore **B81 + B82 + B87 + B88**, not the original B81/B82 scoring in isolation.

## Verified effective behavior

### 1. Low visibility without whiteout remains only a low-confidence candidate

For a morning row such as:

- visibility: about 0.8 km
- RH: 77%
- low cloud: 27%
- weather code: clear/partly-cloudy, not fog
- no heavy precipitation

`tw-034-P03` remains eligible only as:

- reason: `coastal_cliff_visibility_only_candidate`
- score: 68
- confidence: low
- uncertain: true
- subject readability uncertain: true

This preserves the B81 planning signal without claiming that photogenic mist is actually on the cliff.

### 2. B82 north-sector proxies may raise confidence only when there is directional contrast

The optional proxy sector is exactly:

- bearings: 330° / 0° / 30°
- distances: 2.5 km / 5.0 km
- total directional proxy points: 6
- plus 1 camera point

If the camera remains readable and at least one north-sector proxy has materially stronger mist evidence than the camera, the directional context may promote P03 to the directional-mist candidate state.

If the north-sector proxy points are no mistier than the camera:

- the spatial module must return `directional_mist_not_distinguished_from_camera`;
- an existing 0.8 km visibility-only candidate must remain the B81 low-confidence 68-point fallback;
- a clear 20–30 km camera row must remain a P03 miss rather than being promoted by the mere presence of proxy samples.

The proxy grid is environmental context only. It does not prove exact fog location, cliff intersection, or observed on-site conditions.

### 3. Camera readability overrides directional mist support below 2.5 km

B87/B88 changed the original B82 behavior where a ~0.6–0.9 km camera row plus north-sector mist support could reach 88.

Current effective behavior:

- if camera visibility < 2.5 km,
- and the row is not a whiteout,
- even strong local or directional mist support remains capped at 68,
- confidence remains low,
- `subject_readability_uncertain = true`.

The 2.5 km value is a conservative planning guard derived from the nearest B82 proxy range. It is **not** a measured camera-to-cliff distance.

### 4. Afternoon P03 is excluded

P03 is a verified morning subject.

Current hard gate:

- local time < 11:00: morning gate may pass
- local time >= 11:00: `outside_morning_mist_window`

Therefore fog-like weather in the afternoon must not resurrect the morning-mist Opportunity.

### 5. P02 can win again after visibility recovers

The regression contract now explicitly covers the winner transition:

- low-visibility morning calibration row: P03 may be the best remaining researched Opportunity, but only at 68 / low confidence;
- later in the same morning, once visibility returns to roughly 30 km and the north-sector proxies no longer show a mist contrast, P03 becomes a miss and P02 can become the winner again.

This is the intended B81 handoff between a mist-oriented Opportunity and the original clear-cliff Opportunity.

## 2026-09-28 data boundary

The B81 PR description referred to a “2026-09-28 Qingshui example” with roughly 0.7–0.8 km visibility.

However, the retained GitHub production weather snapshots inspected for 2026-09-28 do **not** preserve that low-visibility morning row:

- post-B81 weather refresh `b463d64a2a2a1fb1dd46dee55ef0e596029110d7`:
  - 06:00 visibility about 33.4 km
  - 07:00 about 30.0 km
  - 09:00 about 29.9 km
  - P02 is the clear-view winner
- post-B82 weather refresh `ddbcf584de7a17be376c2be0b37ab2a8256408cb` preserves the same broad clear-morning behavior.

Therefore the 0.7–0.8 km row must be treated as a **calibration/regression scenario derived from the 2026-09-28 review**, not as a retained historical production forecast snapshot.

Separately, B87 documents a reproducible production issue on 2026-10-01 where camera visibility around 0.6–0.9 km plus directional mist support could still score P03 at 88 before the readability guard was added.

Do not merge these two provenance statements.

## Remaining evidence / data gaps

1. There is currently no `tw-034` field-validation registry case and no Qingshui replay fixture.
   - The 2026-09-28 Qingshui calibration scenario is therefore regression input, not registered field ground truth.
2. The 330° / 0° / 30° samples are broad environmental proxies.
   - Exact cliff geometry and exact fog/cliff overlap remain unverified.
3. The 2.5 km readability threshold is not field-calibrated.
   - It is a conservative planning guard and should be revisited only after multiple positive and negative field cases.
4. P02 can be the weather winner when visibility recovers, but its current runtime does not provide a provider-backed dynamic-access guarantee.
   - “P02 wins” means the photographic/weather Opportunity wins under the supplied access-open state; it is not a guarantee that the site is physically accessible.
5. Retained weather snapshots are refresh snapshots, not a full immutable archive of every forecast revision seen during the day.
   - A value mentioned during live review may be unrecoverable later unless it is captured in a replay fixture.

## Regression coverage added in B92

`test_opportunity_adapter.py` now additionally asserts:

- the B82 proxy layout is exactly 330° / 0° / 30° × 2.5 / 5.0 km;
- no directional contrast does not promote a weak B81 visibility-only candidate;
- clear camera + clear/equivalent proxies deny P03;
- a same-day 2026-09-28-derived transition goes from low-confidence P03 at 0.8 km to P02 winning after visibility recovery.

Existing regressions continue to cover:

- whiteout veto;
- strong mist support with readable camera;
- directional mist promotion with a clear camera;
- sub-2.5 km hard cap even with directional support;
- afternoon rejection.

## Release interpretation

A passing B92 regression means the mainline decision logic preserves the intended state transitions. It does **not** prove that Open-Meteo correctly located the real mist on 2026-09-28, nor that the 2.5 km guard is optimally calibrated.
