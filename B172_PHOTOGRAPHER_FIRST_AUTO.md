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
