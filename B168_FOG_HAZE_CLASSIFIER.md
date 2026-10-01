# B168 Fog vs Haze Diagnostic Classifier

Date: 2026-10-01

B168 introduces a conservative diagnostic classifier that separates meteorological fog support from aerosol haze support.

The classifier combines visibility with RH/dew-point saturation, fog weather code and low cloud for fog evidence, while CAMS PM2.5/AOD provide aerosol evidence. It deliberately returns mixed or unresolved states when evidence overlaps or the cause of low visibility is not supported.

Important boundaries:

- AOD is column aerosol loading, not fog and not surface PM2.5.
- PM2.5 is near-surface particulate mass concentration; elevated PM2.5 alone does not prove degraded photographic visibility.
- Fog requires low visibility plus meteorological support.
- If fog and aerosol evidence coexist, B168 reports `mixed_fog_haze` rather than forcing one cause.
- This module is diagnostic only. It has no Opportunity score effect in B168.
- Thresholds are initial planning heuristics and require replay/field calibration before scoring integration.

Next: B169 can feed the diagnostic state into WeatherGrid inspector and replay it against Qingshui / Qixingtan field cases before any score policy changes.
