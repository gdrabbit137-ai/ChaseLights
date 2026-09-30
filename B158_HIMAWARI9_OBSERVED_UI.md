# B158 — Himawari-9 observed mode in WeatherGrid

## Goal

Expose the already-published Himawari-9 Taiwan snapshot in the public
WeatherGrid UI while preserving a strict semantic boundary between
**observation** and **forecast** data.

B158 does not change Photography Opportunity scoring and does not add
Himawari to the automatic forecast-model selection policy.

## Selector

The existing "氣象模型" selector becomes **資料來源**.

- 自動預報
- 觀測 · Himawari-9 2 km
- JMA MSM 5 km
- CWA WRF 3 km
- ICON Global
- GFS 0.25°

"自動預報" continues to use the existing forecast policy only. It never
silently swaps to a satellite observation.

## Observation layers

### 衛星雲遮罩

- source field: `observed_cloud_mask`
- 0 = clear
- 1 = cloudy
- categorical nearest-neighbour rendering
- no bilinear blending between category values

### 雲頂高度

- source field: `cloud_top_height_m`
- stored in metres, displayed in kilometres
- sourced from NOAA L2 `CldTopHghtAWIPS`
- location uses the B156 parallax-corrected geolocation path
- presentation and point sampling use nearest-neighbour values; forecast-style
  bilinear interpolation is not applied to satellite retrievals

Cloud-top height describes the retrieved top of an observed cloud pixel. It
does not prove that lower decks are absent and is not labelled as low/mid/high
cloud percentage.

## Time semantics

Himawari is exposed as one current observation frame.

- source badge: `OBS · Himawari-9 2 km`
- time label: **觀測時間**
- metadata: **衛星觀測** + Taiwan-local observation time + data age
- previous/next/play controls are disabled for the single observation
- no forecast lead (for example `+6h`) is shown

## QC

The inspector shows observation-specific QC:

- data age
- nearest-neighbour p99 / maximum distance
- valid-cell count
- cloud-top missing values are explicitly allowed for clear sky / failed
  retrievals and are not automatically treated as a data error

## Production validation

B158 extends the existing B145 public-site smoke:

- the Himawari selector option must exist
- when a current snapshot is available, it must select successfully
- the only layers must be `observed_cloud_mask` and
  `cloud_top_height_m`
- debug state must report `sourceKind = observation`
- timeline model must be `HIMAWARI9_AHI_OBS`
- the slider has exactly one position
- the UI says observation, not forecast

The option remains gracefully disabled if the scheduled provider has removed
a stale snapshot after an upstream refresh failure.
