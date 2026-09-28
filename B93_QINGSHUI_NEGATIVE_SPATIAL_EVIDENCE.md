# B93 — Qingshui Cliff Negative Spatial Evidence Veto

Date: 2026-09-28 (Asia/Taipei)

## Purpose

B92 verified the B81/B82/B87/B88 behavior and added the missing same-day winner-transition regression. This follow-up fixes one remaining ambiguity in the B82 fallback contract for:

- `tw-034-P03 — 清水斷崖晨霧、雲霧山海`

B82 said the B81 single-point fallback should be preserved when multi-point data are unavailable. Before B93, the runtime also fell back when multi-point data were fully available but broadly contradicted target-sector mist.

B93 separates those states.

## Effective decision order

For `tw-034-P03`:

1. outside the verified morning window → reject;
2. access closed / material precipitation → reject;
3. camera whiteout → reject;
4. optional 330° / 0° / 30° directional context:
   - directional mist support → may promote the candidate;
   - spatial data missing / insufficient / inconclusive → allow B81 fallback;
   - broad clear target sector with zero mist targets → reject;
5. if no conclusive spatial veto:
   - camera visibility < 2.5 km → candidate only, score capped at 68;
   - supported readable mist → 82/88 path;
   - visibility-only <= 3 km → 68 low-confidence fallback;
   - visibility > 8 km → mist Opportunity miss.

## Broad-clear target-sector rule

The negative-evidence veto requires:

- at least 2 valid target samples;
- zero target samples meeting the directional mist definition;
- at least two thirds of valid target samples passing all conservative clear checks:
  - visibility >= 8 km;
  - low cloud <= 35%;
  - RH <= 88%;
  - no fog weather code.

This threshold is intentionally stricter than merely “no directional contrast.”

Examples:

- camera 0.8 km + targets unavailable → keep B81 68-point low-confidence candidate;
- camera 0.8 km + six clear northward proxies → P03 ineligible;
- camera 20 km + one materially mistier target → B82 directional candidate may be promoted;
- camera and targets both broadly misty without directional contrast → do not apply the broad-clear veto; remain conservative/inconclusive.

## 2026-09-28 interpretation

The retained production snapshots around the B81/B82 merges show a broadly clear Qingshui morning, with roughly 28.7–33.4 km camera-grid visibility during 06:00–10:00 and P02 winning.

The B81 PR's 0.7–0.8 km example is therefore retained as a calibration/regression scenario, not as repository-backed field ground truth for that morning.

B93 does not change that provenance boundary.

## Regression changes

B93 preserves the B92 winner-transition test but changes the low-visibility setup:

- the 0.8 km B81 fallback test now omits spatial data, matching the stated fallback contract;
- a separate production-consistent spatial case uses a 0.8 km camera row plus six clear north-sector proxy rows and asserts:
  - spatial data available;
  - zero mist targets;
  - six clear targets;
  - broad clear target sector = true;
  - P03 ineligible;
  - reason = `directional_target_sector_lacks_mist_support`.

Existing tests continue to cover:

- 330° / 0° / 30° × 2.5 / 5 km geometry;
- directional promotion;
- camera whiteout;
- sub-2.5 km 68-point hard cap;
- afternoon rejection;
- P02 winner restoration after visibility recovery.

## Remaining limitations

- The proxy grid is coarse environmental context, not exact cliff geometry.
- A broad-clear veto can still miss narrow fog attached to the real cliff.
- The clear-sector thresholds are model-policy thresholds, not field-calibrated physical constants.
- No Qingshui field-validation replay currently exists for the 0.7–0.8 km scenario.
