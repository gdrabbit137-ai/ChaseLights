# B136 — Reconcile Subject-aware Verdicts on Current Main

Date: 2026-09-30 (Asia/Taipei)

## Goal

Carry the previously reviewed B107 photographer-facing verdict layer onto the current ChaseLights main without reverting newer WeatherGrid, field-intake, regional UI, desktop-polish, or scoring work.

## Preserved B107 behavior

- normal high/medium-confidence `OPPORTUNITY_SIMPLE_MATCH` → `適合拍攝 {Opportunity}`
- low-confidence or candidate phenomena → `有機會拍到 {Opportunity}`
- `OPPORTUNITY_SIMPLE_MISS` → `目前不利於拍攝 {Opportunity}`
- `OPPORTUNITY_OUTSIDE_TIME_WINDOW` → `目前不是拍攝 {Opportunity} 的建議時段`
- candidate detail remains visible in the explainability section
- no score, threshold, eligibility, weather-provider, or Opportunity contract changes

## B136 reconciliation

The verdict helper is applied consistently to:

1. desktop/mobile Place cards;
2. Place-guide current score and explanation;
3. desktop hourly forecast table;
4. mobile hourly forecast cards.

`fetch_data.py` also replaces the old generic Place-level fallback text so stale/backend-rendered status copy does not reintroduce “基本好拍條件已成立”.

## Regression

B30 Browser Smoke synthesizes all four primary verdict paths and rejects the legacy generic phrase from rendered page source.

## Boundary

A verdict describes whether forecast prerequisites support a researched Photography Opportunity. It does not claim that uncertain phenomena such as mist, cloud sea, flowers, wildlife, or celestial alignment have actually been observed in the field.
