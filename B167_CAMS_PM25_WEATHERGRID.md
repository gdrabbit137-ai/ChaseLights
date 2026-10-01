# B167 CAMS PM2.5 WeatherGrid

Date: 2026-10-01

## Goal

Add near-surface PM2.5 as a photography environment field beside CAMS AOD 550 nm.

## Contract

- Source: CAMS Global via Open-Meteo Air Quality API.
- Field: `pm2_5_ug_m3`, unit `µg/m³`.
- Encoding: integer scaled by 0.1 µg/m³.
- Timeline and request/presentation lattice are shared with the B166 CAMS bundle.
- Missing PM2.5 stays null and is QC flagged; it is never coerced to zero.
- PM2.5 is near-surface particulate mass concentration. It is not AOD and is not by itself a fog classifier.
- The 0.4° browser lattice remains a presentation/request lattice; CAMS native resolution remains about 45 km.

## UI

CAMS now exposes both AOD 550 nm and PM2.5. PM2.5 has its own legend/palette and inspector identity. B168 will combine these environmental fields with meteorological saturation/visibility evidence; B167 does not change photography scoring.
