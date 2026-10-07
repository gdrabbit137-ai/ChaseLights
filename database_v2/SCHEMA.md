# Database V2 Migration Schema R1

Database V2 is an additive migration scaffold. It does not replace the production catalog until separately validated.

## Tables

- places
- opportunities
- camera_zones
- subject_geometries
- view_relations
- condition_contracts
- conditions
- runtime_bindings
- evidence
- migration_progress

## Condition domains

WEATHER, ASTRONOMY, ACCESS_SAFETY, SUBJECT_STATE, SEASON_TIME, GEOMETRY_COMPOSITION.

## Migration rules

1. Place-specific evidence proves what can be photographed; runtime estimates when an already researched Opportunity may work.
2. Camera evidence does not prove Subject geometry. Subject identity can be retained while spatial geometry stays null.
3. Camera-to-Subject distance, azimuth, elevation angle, angular size, horizon and corridor are derived values. They remain null until source geometry supports calculation.
4. Conditions carry role, domain, metric, target, operator, threshold, unit, unknown_policy, confidence and human descriptions.
5. Unknown geometry, operators and numeric thresholds remain null. Do not infer them from Theme labels or generic photography knowledge.
6. Runtime/formula readiness belongs in runtime_bindings and is separate from researched condition truth.
7. Recommendation policy remains Opportunity-contract owned. This schema does not create a repository-global score threshold.
