# B172 Photographer-first WeatherGrid AUTO selection

B172 changes WeatherGrid navigation so photographers choose the useful environmental layer first and only override the data provider when needed.

## AUTO provider contract

AUTO selects a provider per layer and valid forecast time.

- Cloud layers prefer CWA, then JMA, then ICON, then GFS when the provider actually exposes that field and time.
- Other forecast layers prefer CWA, then JMA, then GFS, then ICON.
- Manual provider selection remains available under the advanced data-source control.
- QC follows the selected provider.
- Himawari observations, CAMS haze layers, and VIIRS annual night-light context keep their distinct time/source semantics and are not silently mixed into forecast AUTO.

## UI contract

The photography layer selector is the primary control. The provider selector is an advanced control. Layer labels use photographer-facing descriptions such as low cloud / mountain fog, visibility, wind field, haze, and night lights.

## Deliberate B172 boundary

The previous experimental branch synthesized 0–100 photography composite maps on the GFS 0.25-degree display grid. That implementation is not promoted in this batch because resampling higher-resolution regional inputs to the GFS grid discards useful spatial detail and the composite score provenance was not explicit enough.

B172 therefore does not publish a new photography score and does not change Opportunity scoring.

A follow-up composite implementation must define:
- the target grid independently of GFS;
- provider and resampling provenance per input;
- missing-data behavior;
- temporal alignment tolerance;
- separation between an environment visualization and the canonical Opportunity score.


## B173 follow-up contract: photography composite research

B173 may reintroduce photography environment composites only after the display-grid and provenance problems above are resolved. The first implementation target is deliberately a **contract and research boundary**, not a published 0–100 score.

Requirements:

- **Target grid is independent of GFS.** Choose a grid from the requested photography/coverage viewport and an explicit output resolution; do not inherit the GFS 0.25-degree grid merely because GFS owns the timeline.
- **Per-input provenance is mandatory.** Record the selected provider, source field, source grid spacing, source valid time, target valid time, interpolation method, and temporal offset for every component.
- **Temporal alignment is bounded.** Exact valid-time matches are preferred. A nearest frame may only participate when its absolute offset is within an explicit per-source tolerance; otherwise that component is missing.
- **Spatial resampling fails closed.** Do not extrapolate outside a source bbox. Missing interpolation neighbours remain missing rather than being synthesized.
- **Missing-data behavior is visible.** Renormalizing available weights must also expose which inputs were absent and the effective weight coverage; low-coverage cells must not look equally authoritative.
- **Environment visualization remains separate from Opportunity scoring.** Composite output is diagnostic evidence and must not silently overwrite the canonical Opportunity score.
- **VIIRS remains evidence-only.** Annual VNP46A4 radiance is not Bortle class, SQM, or a calibrated sky-brightness score and must not directly change a photography weather score without a validated model.

The previous prototype on branch `b172-photographer-first-weathergrid` is retained as implementation research for subject-specific weighting and geometry-aware diagnostics. B173 should selectively port those ideas onto this contract rather than copying its GFS-grid composite implementation.
