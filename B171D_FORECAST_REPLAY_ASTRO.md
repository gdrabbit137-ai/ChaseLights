# B171d Forecast/replay astrophotography diagnostic wiring

B171d persists the B171 astrophotography environment diagnostic inside the existing timestamp-level `photography_environment` object used by both generated hourly forecasts and replay snapshots.

The diagnostic receives the forecast UTC timestamp and the same camera latitude/longitude already used by ChaseLights astronomy. The current target is explicitly `galactic_core`, so B171b can provide Moon altitude, illumination, and Moon-to-Galactic-Core separation deterministically.

This batch intentionally does **not** fake VIIRS availability. The annual VNP46A4 artifact is a static spatial grid and is not yet sampled into `item_data`; until that spatial join exists, the diagnostic keeps `quality_checked_nighttime_light_radiance` in `missing_evidence`.

No Opportunity score consumes this diagnostic.
