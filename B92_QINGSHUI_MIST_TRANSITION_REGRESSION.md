# B92 — 清水斷崖晨霧 Spatial Negative Evidence + Winner Transition Regression

Date: 2026-09-28 (Asia/Taipei)

## Scope

This hardens the effective B81/B82 Qingshui Cliff morning-mist runtime on current `main`.

Affected Opportunity:

- `tw-034-P03 — 清水斷崖晨霧、雲霧山海`

Sibling clear-view Opportunity used for winner handoff:

- `tw-034-P02 — 清水斷崖山海遠眺`

## Why B92 is needed

B82 intentionally added optional 330° / 0° / 30° north-sector proxy samples at 2.5 km and 5 km.

The B82 PR contract said:

- directional proxy support may promote the mist candidate;
- camera whiteout remains a veto;
- the B81 single-point fallback is preserved when multi-point data are unavailable.

The implementation did not fully preserve that distinction. Before B92, when multi-point data were available and the entire northward proxy sector contained no mist signal, `tw-034-P03` could still fall through to the B81 visibility-only candidate path. That made these two states equivalent:

1. spatial data missing / insufficient;
2. spatial data present and broadly contradicting cliff-sector mist.

They are not equivalent.

## B92 spatial semantics

### Positive directional evidence

If the camera remains usable and one or more north-sector proxies show a material mist signal relative to the camera:

- keep the B82 directional candidate path;
- directional support may raise the candidate to the dedicated directional score/state;
- exact fog/cliff overlap is still not claimed.

### Missing or inconclusive spatial evidence

If the optional spatial fetch is unavailable, insufficient, or not conclusive:

- preserve the B81 single-point fallback;
- low visibility may still create only a low-confidence candidate;
- B87/B88 readability guard and 68-point hard cap remain in force below 2.5 km.

### Negative directional evidence

If spatial data are available and:

- at least two valid target samples exist;
- at least two thirds of valid target samples are conservatively clear:
  - visibility >= 8 km,
  - low cloud <= 35%,
  - RH <= 88%,
  - no fog weather code;
- zero target samples meet the mist-signal definition;

then the broad northward target sector is treated as **negative spatial evidence**.

Result:

- `tw-034-P03` is ineligible;
- reason: `directional_target_sector_lacks_mist_support`;
- camera-local low visibility must not be reinterpreted as Qingshui-Cliff mist.

This is a conservative forecast veto, not an observation that the real cliff is definitely clear.

## Existing guards preserved

- camera whiteout still fails closed;
- camera visibility below the 2.5 km planning/readability guard cannot enter the 80+ band;
- 2.5 km is not asserted as the physical camera-to-cliff distance;
- `tw-034-P03` remains morning-only (`local_time < 11:00`);
- afternoon mist-like weather does not reactivate this Opportunity;
- directional proxies remain environmental proxies, not exact subject points.

## 2026-09-28 evidence boundary

The B81 PR described an expected 2026-09-28 planning case with approximately 0.7–0.8 km visibility and weak RH/low-cloud support. That input is useful as a regression case, but the repository does not preserve it as a verified on-site morning observation.

The generated weather snapshots currently preserved around the B81/B82 merges show the 2026-09-28 morning at the Qingshui camera grid as broadly clear:

- 06:00: about 33.4 km visibility;
- 07:00: about 30.0 km;
- 08:00: about 29.9 km;
- 09:00: about 29.9 km;
- 10:00: about 28.7 km.

Those snapshots therefore support the separate requirement that the normal clear-cliff Opportunity `tw-034-P02` can win when visibility is restored. They do **not** prove that a 0.7–0.8 km morning occurred on site.

Ground truth, historical forecast snapshots, and synthetic regression inputs must remain separately labeled.

## Regression coverage

B92 adds regressions for all four state transitions requested for Qingshui mist:

1. **Low visibility, no spatial data**
   - 0.8 km visibility with weak support remains a low-confidence P03 candidate;
   - B88 hard cap keeps it at 68.

2. **Positive north-sector spatial evidence**
   - 330° / 0° / 30° proxy support can promote the candidate;
   - exact target-zone verification remains false.

3. **Negative north-sector spatial evidence**
   - broad clear target-sector evidence with zero mist targets vetoes P03;
   - missing spatial data is still allowed to use the B81 fallback.

4. **Time / winner transition**
   - afternoon P03 remains excluded;
   - once visibility returns, P03 becomes ineligible for mist and P02 can become the best Opportunity again.

## Remaining data limitations

- No repository-backed field-validation case currently proves the 0.7–0.8 km Qingshui morning as observed ground truth.
- The 330° / 0° / 30° samples are coarse model-grid proxies; they can miss narrow cliff-attached fog.
- The 8 km / 35% low-cloud / 88% RH clear-sector thresholds are conservative negative-evidence thresholds and should be recalibrated only after multiple positive and negative field cases.
- There is still no exact surveyed camera-to-subject geometry for the cliff composition.
