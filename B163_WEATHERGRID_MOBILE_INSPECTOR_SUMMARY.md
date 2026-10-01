# B163 — WeatherGrid mobile inspector summary

Date: 2026-10-01

## Goal

Keep the phone layout map-first after B160–B162 by reducing the height of the
"目前圖層" inspector card without removing technical information.

## Mobile default summary

On screens at or below 720 px, the layer card now shows only the information
needed for a quick decision:

- current layer name;
- current displayed value range;
- a compact data-quality state.

The data-quality summary can show states such as:

- 資料正常
- 觀測正常
- 需注意
- QC 未提供
- DEMO
- 載入失敗

## Expandable technical details

A mobile-only "詳細" button expands the existing secondary information:

- model / unit information;
- vertical cloud-layer definition;
- wind-vector toggle and explanation;
- full QC explanation and internal diagnostics.

The button changes to "收合" while expanded and exposes `aria-expanded` plus
`aria-controls` for accessibility.

## Desktop behavior

Desktop retains the complete inspector content by default. The mobile detail
button is hidden on desktop, so existing desktop information density does not
change.

## Guardrails

- no weather values change;
- no QC logic changes, only an additional summarized presentation state;
- no model selection, timeline, coverage geometry or scoring changes;
- B161 cloud-readability behavior remains intact;
- B162 mobile clustering and map controls remain intact.

## Regression requirements

The WeatherGrid UI polish contract verifies:

- collapsed mobile detail section by default;
- full desktop details remain visible;
- accessible expand/collapse controls;
- QC summary state updates for forecast, observation, warning and failure cases.
