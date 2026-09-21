# ChaseLights V5.4 audit

## Implemented in this release

- Estimated Bortle class and dark-sky score for every current Milky Way / Aurora-capable spot.
- Strong light-pollution penalty and score cap for Milky Way; lighter penalty for Aurora.
- Light-pollution factors shown in score explanations.
- Astronomy cards and 96H modal show approximate Bortle class.
- Timezone display no longer treats every `CST` abbreviation as Taiwan UTC+8.
- Summary/detail cache consistency: details are invalidated when a newer summary arrives.
- Old ChaseLights browser caches are cleaned up automatically.
- Taiwan Traditional Chinese modal no longer duplicates local aliases.
- Schema bumped to 9; UI accepts schemas 7–9 during deployment transition.

## Validation performed

- Python compile: PASS.
- JavaScript syntax: PASS.
- Unique spot IDs: PASS.
- Duplicate exact coordinates: none in current TW/JP/US datasets.
- Scene/theme enum validation: PASS.
- Aurora only appears in Alaska: PASS.
- All current Milky Way/Aurora spots receive a Bortle class: PASS.
- Controlled Milky Way score decreases from ~94 at Bortle 1 to ~30 at Bortle 9: PASS.
- Controlled Aurora score uses a lighter light-pollution penalty: PASS.

## Remaining model limitations (not software bugs)

1. Bortle values are curated planning estimates, not live SQM measurements. They are exported with `light_pollution_source` and `light_pollution_confidence` and displayed as `≈Bortle`.
2. Bortle is a site-level approximation; it does not yet model directional light domes on the horizon.
3. Cloud-sea forecasting remains a heuristic using cloud base, humidity, wind and related weather fields; valley/top dual-point modeling would be the next major accuracy upgrade.
4. Fire-cloud / vivid-twilight predictions are probabilistic; cloud optical depth and exact horizon obstruction are not available from the current Open-Meteo inputs.
5. Access-hours rules are only present for locations explicitly configured; the system does not yet maintain live opening/permit status for every park or attraction.
