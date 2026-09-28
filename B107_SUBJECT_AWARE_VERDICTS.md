# B107 — Subject-aware conversational shooting verdicts

## Goal

Replace engineering-style status copy such as:

> 此景點的基本好拍條件已成立

with a photographer-facing verdict that says **what the current forecast is suitable for**.

Primary UI wording:

- sufficiently supported / normal match → `適合拍攝 {Photography Opportunity}`
- candidate or low-confidence state → `有機會拍到 {Photography Opportunity}`
- generic weather miss → `目前不利於拍攝 {Photography Opportunity}`
- outside the researched time window → `目前不是拍攝 {Photography Opportunity} 的建議時段`

The Opportunity name is inserted from the researched Place-specific Opportunity. The UI does not invent a subject from weather alone.

## Confidence and uncertainty rule

A weather match MUST NOT upgrade uncertain subject presence into a factual claim.

Candidate-style runtime states (mist, directional/orographic cloud and spatial cloud-sea candidates) use **有機會拍到** and retain their detailed runtime explanation below the primary verdict.

A low-confidence `OPPORTUNITY_SIMPLE_MATCH` also uses **有機會拍到** instead of **適合拍攝**.

## Where the underlying photographic conditions are actually stored

The short examples used in UI discussion — e.g. "visibility good + little low cloud", "weak wind for reflections", or "Moon interference low for Milky Way" — are explanatory summaries. They are **not one canonical hard-coded condition table**.

Source ownership follows `RESEARCH_EVIDENCE_SPEC_R4_2.md §12`:

1. **Canonical researched Opportunity definitions**
   - `runtime_catalog_v004_r4_2.json`
   - Owns Opportunity names, best time/season, condition variants, required conditions, boosters, penalties and Camera Zones.

2. **Evidence / provenance**
   - `runtime_evidence_registry_r4_2.json`
   - Related evidence-review documents such as `B37_REFLECTION_EVIDENCE_*.md`, `B38_ASTRO_EVIDENCE_REVIEW.md`, and Place-specific research batches.
   - These establish that the photographic subject is actually supported at the Place; favorable weather alone cannot create a subject.

3. **Executable current-condition evaluation**
   - `opportunity_runtime.py` — shared Opportunity runtime contracts including minimum-sufficient visibility/local-scene logic, directional light, reflection/calm-water, mist, astronomy and other composable modules.
   - `spatial_weather.py` — multi-point / vertical cloud diagnostics used by cloud-sea and directional mist/cloud cases.
   - `marine_state.py` — wave/swell state.
   - `tide_state.py` — relative tide state.
   - `fetch_data.py` — integrates runtime diagnostics with forecast scoring and publishes status/factor translations.

4. **UI wording**
   - `assets/app.js`
   - Converts runtime status + Opportunity name + confidence into the conversational verdict shown to the user.
   - This layer changes wording only; it does not change the score or decide whether a weather condition is true.

## Mapping for the discussed subject families

| Subject family | Main condition/evidence locations |
| --- | --- |
| Mountain / long-range view | `runtime_catalog_v004_r4_2.json`; `opportunity_runtime.py` minimum-sufficient visibility contracts; base weather scoring integrated by `fetch_data.py` |
| Coast / seascape | Place-specific catalog contracts; visibility/runtime policy in `opportunity_runtime.py`; marine-specific Opportunities may additionally use `marine_state.py` |
| Reflection | Catalog + `runtime_evidence_registry_r4_2.json`; `opportunity_runtime.py` water-surface-state evaluator; evidence history in `B37_REFLECTION_EVIDENCE_*.md` |
| Morning mist / fog | Catalog + evidence registry; `opportunity_runtime.py` local/mist contracts; `spatial_weather.py` where directional/multi-point support is configured; Qingshui behavior documented by B81/B82/B87/B88/B92/B93 series |
| Cloud sea | Catalog + evidence registry; `opportunity_runtime.py`; `spatial_weather.py` for camera-vs-lower-terrain evidence; Hehuan interpretation documented in `B94_HEHUAN_CLOUD_SEA_COMMENTARY.md` |
| Forest light / sunbeams | Catalog condition variants; `opportunity_runtime.py` direct-radiation / cloud-light evaluators. A forest Scene alone is not enough to create a sunbeam Opportunity |
| Sunrise / sunset | Catalog composition/time contract; `opportunity_runtime.py` directional-horizon and cloud/sky-glow modules where enabled |
| Milky Way / stars | Catalog + evidence registry; `opportunity_runtime.py` astronomy-ephemeris evaluator; evidence rules in `B38_ASTRO_EVIDENCE_REVIEW.md` |
| Long-exposure coast | Catalog contract plus the enabled runtime dependencies; may combine visibility/cloud logic with `marine_state.py` and `tide_state.py` depending on the specific Opportunity |

## Important semantic boundary

The UI verdict means **the forecast is suitable for the researched Opportunity**, not that the subject has been observed in the field.

Examples:

- Allowed: `適合拍攝六十石山黃花季金針花田與山景` when the researched seasonal Opportunity and runtime gates are satisfied.
- Allowed for uncertain phenomena: `有機會拍到清水斷崖晨霧、雲霧山海`.
- Not allowed: claiming that mist, cloud sea, flowers, wildlife, Milky Way alignment, or another non-observed subject is definitely present merely because prerequisites are favorable.

## Regression contract

Browser Smoke verifies the four primary wording paths and rejects the old phrase `基本好拍條件已成立` from rendered UI.
