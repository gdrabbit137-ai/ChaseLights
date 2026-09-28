# B94 — Qingshui Negative Spatial Evidence

Date: 2026-09-28 (Asia/Taipei)

B94 refines the effective B81/B82/B87/B88/B92/B93 contract for `tw-034-P03`.

## Rule

Optional north-sector samples remain 330° / 0° / 30° at 2.5 km and 5 km.

- Positive directional contrast may strengthen the mist candidate.
- Missing, insufficient, or inconclusive spatial data may use the B81 low-confidence fallback.
- Broad regional fog without directional contrast is not a directional promotion and is not a clear-sector veto.
- Fully sampled, broadly clear north-sector evidence with zero mist targets vetoes P03 within the <= 8 km mist-candidate range.

A target is conservatively clear when:
- visibility >= 8 km;
- low cloud <= 35%;
- RH <= 88%;
- weather code is not fog.

Broad-clear requires at least 2 valid targets and at least two thirds of valid targets meeting those clear checks, with zero mist targets.

The veto reason is `directional_target_sector_lacks_mist_support`.

## 2026-09-28 boundary

Retained weather snapshots around the B81/B82 merges show the Qingshui camera grid broadly clear during the morning (roughly 28.7–33.4 km from 06:00–10:00), supporting the P02 clear-view handoff.

The 0.7–0.8 km case in the B81 review is retained as a calibration/regression scenario, not registered Qingshui field ground truth.

## Regression coverage

B94 keeps:
- B81 0.8 km fallback when spatial data are absent;
- B82 positive directional promotion;
- B93 same-fog no-false-directional-promotion;
- B87/B88 sub-2.5 km 68-point cap;
- afternoon exclusion;
- P02 winner restoration after visibility recovery.

B94 adds:
- 0.8 km camera visibility plus six broadly clear north-sector proxies => P03 ineligible.

## Limitations

The proxy grid is coarse environmental context, not exact fog/cliff geometry. The clear-sector thresholds and 2.5 km readability guard are planning policy thresholds and still need calibration against multiple positive and negative field cases.
