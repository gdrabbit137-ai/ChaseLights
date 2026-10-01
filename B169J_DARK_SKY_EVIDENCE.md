# B169j Dark-sky environment evidence contract

Date: 2026-10-01

B169j adds a diagnostic contract that turns the annual VNP46A4 radiance value and its QA flag into conservative artificial-light evidence.

States:
- low_artificial_light_radiance: radiance < 1 nW/(cm²·sr)
- moderate_artificial_light_radiance: 1–<5
- elevated_artificial_light_radiance: 5–<10
- high_artificial_light_radiance: >=10
- night_lights_unavailable: no radiance

These thresholds are ChaseLights planning/display heuristics, not NASA classes.

Quality semantics are carried separately. QA=0 may reach medium diagnostic confidence. Poor, gap-filled, missing, or unknown QA remains low confidence. A radiance value with unknown QA is not marked usable for downstream context.

Hard semantic boundary:
- no Bortle conversion;
- no SQM / mag arcsec^-2 claim;
- no direct sky-brightness claim;
- no limiting-magnitude or Milky-Way-visibility claim;
- no Opportunity score effect.

A future astrophotography model must combine this artificial-light context with atmosphere/transparency, clouds, moon geometry/illumination, target geometry, elevation/terrain, and a validated skyglow model before making stronger claims.
