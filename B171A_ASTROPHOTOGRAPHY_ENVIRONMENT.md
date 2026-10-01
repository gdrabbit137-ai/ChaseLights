# B171a Astrophotography environment diagnostic

B171a synthesizes existing ChaseLights environment evidence for night-sky photography without changing Opportunity scoring.

Inputs may include:
- B169j annual VIIRS artificial-light radiance + QA;
- B170 atmospheric transparency inputs;
- total / low / mid / high cloud cover;
- moon altitude, illumination fraction, and target separation when a future lunar-geometry provider supplies them.

The contract is fail-incomplete: favorable darkness, transparency and clouds are not enough to call a night favorable when moon geometry is absent. Likewise, it never claims Milky Way or astronomical-target visibility.

Current states are `incomplete_evidence`, `challenging_environment`, and `environment_evidence_favorable`. They are diagnostic labels only. `score_effect` remains `none`.

Moon geometry is intentionally not fabricated in B171a. A later batch must add a deterministic astronomical ephemeris/source before replay or scoring can treat lunar conditions as complete.
