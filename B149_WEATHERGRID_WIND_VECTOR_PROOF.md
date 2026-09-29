# B149 WeatherGrid Wind Vector Render Proof

Date: 2026-09-30

## Goal

Strengthen B148 so production validation proves that wind arrows were actually
drawn, not only that the wind-vector toggle was enabled.

## Problem found from the first B148 production screenshot

The first deployed B148 screenshot showed:

- the 10 m wind-speed layer;
- the wind-vector toggle checked;
- the wind-vector legend entry;

but the selected local viewport did not make individual arrows visually obvious.

The previous smoke contract only asserted the vector state flag. That was not
strong enough to distinguish "enabled" from "rendered at least once".

## Render counter

The browser now records a diagnostic-only counter:

```text
window.__weatherGridCoverageDebug.windVectorCount
```

The counter is reset on every vector render pass and increments only after an
arrow is actually stroked on the Canvas.

It is not used by production scoring or user-facing weather logic.

## Production smoke

The deployed-page smoke now:

1. switches to the 10 m wind-speed layer;
2. waits for automatic vector enablement;
3. requires `windVectorCount > 0` in the all-Taiwan view;
4. captures a dedicated wind-overview screenshot;
5. continues with the existing `tw-073` subject-aware coverage selection and
   captures the detailed screenshot.

This gives two short-lived diagnostic images:

- all-Taiwan wind field with vectors;
- selected Place/Opportunity coverage view.

## Guardrails

- no GFS field changes;
- no scoring changes;
- no coverage changes;
- render counter is diagnostic-only;
- calm-cell omission and adaptive density from B148 remain unchanged.
