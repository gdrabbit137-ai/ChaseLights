# B164 — WeatherGrid mobile source header

Date: 2026-10-01

## Goal

Reduce the remaining technical text above the WeatherGrid controls on phones so
the map reaches the first viewport sooner, while preserving complete provenance
and model metadata on desktop and in the existing data-information dialog.

## Mobile header structure

At widths up to 720 px:

- the ChaseLights back link and WeatherGrid title share one compact row;
- the long descriptive subtitle remains hidden;
- source status, concise run metadata and the data-info button share one row;
- full cycle / grid / interpolation text is hidden from the phone header;
- source attribution is hidden from the phone header but remains available in
  the data-information dialog.

Desktop keeps the existing detailed metadata.

## Concise source summary

The phone-only summary intentionally contains only decision-useful metadata.

Examples:

- JMA MSM: `起報 09/30 17:00 · 5 km · 1h`
- CWA WRF: `起報 09/30 18:00 · 3 km · 6h`
- ICON: `起報 09/30 18:00 · 約 13 km`
- GFS: `起報 09/30 18:00 · 0.25°`
- Himawari: `觀測 10/01 12:00 · 2 km · 8 分前`

The source pill still identifies LIVE / AUTO / OBS and the active provider.

## Data information access

The existing data-information dialog remains the single place for detailed
provenance and source caveats. On phones its button uses the shorter label
`ⓘ 資料`; desktop retains `ⓘ 資料說明`.

## Guardrails

- no weather values change;
- no model selection or source priority changes;
- no source provenance is removed from the application;
- no timeline, coverage, QC or scoring logic changes;
- B160–B163 mobile behavior remains intact.

## Regression requirements

The WeatherGrid UI contract verifies:

- phone header has a compact source-summary element;
- detailed source metadata and attribution are hidden only in the mobile layout;
- source summary is rendered for forecast and observation data;
- the data-information entry point remains present;
- desktop title/header structure remains available.
