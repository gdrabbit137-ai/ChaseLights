# B157 WeatherGrid Progressive Inspector

Date: 2026-10-01

## Goal

Remove empty or engineering-only inspector cards from the normal WeatherGrid
view while keeping useful context available when the user actually needs it.

This is a presentation-only change. Weather values, provider selection,
coverage geometry, and Photography Opportunity scoring are unchanged.

## Progressive inspector behavior

The default WeatherGrid view now keeps the right inspector focused on the
active weather layer.

Before a Place is selected:

- the Place result card is hidden;
- the subject-aware coverage card is hidden;
- data quality is shown compactly inside the active-layer card;
- technical provider notes do not occupy a permanent card.

After a Place is selected:

- the Place result card appears;
- the coverage card appears and can show the aggregate coverage state;
- selecting an Opportunity continues to replace that aggregate state with its
  Camera / Subject / Environment details.

Clearing the Place selection hides those dependent cards again.

## Data quality

QC is no longer a separate full-height panel.

Normal state is shortened to:

`✓ 資料正常`

Warnings remain visible in the active-layer card and still include the small
internal QC code for diagnosis.

Missing QC is shown as a compact caution instead of implying that the weather
field itself is invalid.

## Data/model documentation

The former always-visible `POC 限制` card is moved to an on-demand
`ⓘ 資料說明` dialog in the header.

The dialog retains the existing notes about:

- supported WeatherGrid providers;
- current auto-provider policy;
- CWA native cloud-field limitations;
- JMA MSM browser-domain limitations;
- display interpolation versus true model resolution;
- MapLibre/OpenFreeMap fallback behavior.

The content is therefore still accessible without consuming the main
photography workflow.

## Guardrails

- keep the map and provider no-data boundary visible;
- do not crop the basemap to the weather raster;
- do not remove the Place or Opportunity selectors;
- do not hide QC warnings;
- do not change model field availability;
- do not change fetch, scoring, or coverage logic.

## Regression

`test_weathergrid_progressive_inspector.py` verifies:

1. Place and coverage cards start hidden;
2. JS reveals them only when a Place is selected;
3. QC lives inside the current-layer panel;
4. the normal QC state is compact;
5. technical notes live in the data-info dialog;
6. hidden panels remain hidden inside responsive grid layouts;
7. the browser debug surface reports inspector visibility.
