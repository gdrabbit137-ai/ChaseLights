# W3 M6a: First deterministic solar WINDOW model

Scope: `packages/models-v2/` only. Research/technical diagnostic, **NOT an approved photography recommendation**. Built against W1 contract [#473](https://github.com/gdrabbit137-ai/ChaseLights/pull/473) and #467. This model introduces the first independent `packages/models-v2/solar_window.py` routine.

## Contract and usage

`compute_solar_window(request, computed_at=None)` accepts only `solar-window-request-v0.1.schema.json` and returns a response validating against `solar-window-result-v0.1.schema.json`. It requires `model.model_id="chase-v2-noaa-meeus"`, `algorithm_version="0.1.0"`, `horizon_assumption="ideal_unobstructed"`, and `sun_altitude_crossing_deg=-0.833`. It validates IANA timezone names with Python `zoneinfo`. Invalid dates, sources, coordinates, model identifiers, and unrecognized fields are rejected.

Computations sample the **actual local civil date** (23/24/25 hours across DST) converted into UTC, solve solar altitude crossings by bracketed bisection, then verify that returned instants belong to the requested IANA-local date. At high latitude, midnight-sun/polar-night produces `NO_EVENT` rather than invented times. Ambiguous multiple crossings produce `UNKNOWN`. A completely unknown observer produces `UNKNOWN_LOCATION`, never a fabricated Place-center Camera GPS.

The approximate geometric solar-center altitude is based on NOAA equation-of-time/declination relationships and Meeus-style mean solar longitude, anomaly and obliquity. The common apparent-horizon proxy **−0.833°** approximates Sun semidiameter and atmospheric refraction; it **does not account for** altitude corrections, actual observed refraction, weather, skyline/mountains, terrain horizon, water horizon, exact camera alignment, licensing, legal access or image-making suitability.

The result is **always** `capability="WINDOW"`, `recommendation_eligible=false` and `photography_verdict="NOT_EVALUABLE"`, with complete localized zh-TW/en/ja caveats. Coordinates must have an independent provenance; general Place coordinates are regional **examples only**, not Directions.

## Independent numerical acceptance references

External almanac snapshot queried on **2026-10-13**. References are rounded to minutes, and a generous **±5 min** tolerance is a reproducibility/checking threshold, **not a claim of measured geometric accuracy**. Exact observer coordinate/environment differences can shift published local sunrise/sunset.

| Place / local date | Approximate benchmark sunrise / sunset | Source |
| --- | --- | --- |
| Taipei 2026-10-13 | 05:50 / 17:28 | [Timeanddate Taipei](https://www.timeanddate.com/sun/taiwan/taipei?month=10&year=2026) |
| Seattle 2026-10-13 | 07:25 / 18:24 | [Timeanddate Seattle](https://www.timeanddate.com/sun/usa/seattle?month=10&year=2026) |
| Fairbanks 2026-10-13 | 08:38 / 18:34 | [Timeanddate Fairbanks](https://www.timeanddate.com/sun/usa/fairbanks?month=10&year=2026) |
| Tokyo 2026-06-21 | 04:25 / 19:00 | [Timeanddate Tokyo](https://www.timeanddate.com/sun/japan/tokyo?month=6&year=2026) |
| Seattle 2026-03-08 (spring DST) | 07:35 / 19:04 | [Timeanddate Seattle March](https://www.timeanddate.com/sun/usa/seattle?month=3&year=2026) |

Numerical regressions also cover Seattle **fall DST** `2026-11-01`, `Arctic/Longyearbyen` midnight Sun, Utqiaġvik polar night, `Pacific/Kiritimati` date-line +14h UTC conversion, unknown Location, rejected fake ephemeris/provider metadata and unexpected access-status fields, and time-capture determinism.

Relevant methods: NOAA [Solar Calculation Details](https://gml.noaa.gov/grad/solcalc/calcdetails.html) and Jean Meeus, *Astronomical Algorithms* (2nd ed., Willmann-Bell, 1998). Numerical outputs must be independently checked before higher-accuracy or photo-alignment claims.

## Tests and release boundary

Run from repository root (requires `jsonschema` and W1 branch schemas):

```bash
python -m unittest discover -s packages/models-v2/tests -p 'test_*.py' -v
```

**10** regression cases; these complement the four W1 schema tests. The legacy `123` acceptance gate was raised to `128` by W2 Batch04, so W5 must intentionally rotate exact W1/W3 source pins and raise the global CI count to **142 = 128 + 4 + 10**, not weaken/skip the existing checks. Preserve W2 8 research opportunities, human signoff pending, W4 single default Research-only preview and original W3 evaluator security rules. Do not add sunset photo scores, moon/aurora probability, unreviewed horizon sectors or fabricated verified navigation.

No V1, W2, W4, WeatherGrid or deployment changes are made here.
