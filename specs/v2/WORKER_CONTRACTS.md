# ChaseLights V2 Worker Ownership

**Owner:** Worker 1. Each worker must check latest main, current R4.2 research/navigation specs, V2 contracts and overlapping PRs before a branch update or merge.

| Worker | Owned paths | Required handoff |
| --- | --- | --- |
| 1 — Architecture | `specs/v2/` | JSON Schema, model contracts, migration rules |
| 2 — Data | `data/v2/` | reviewed records, evidence, crosswalk and migration tests |
| 3 — Models | `packages/core-v2/`, `packages/models-v2/` | deterministic evaluations, provenance, unknown propagation |
| 4 — Web | `apps/web-v2/` | isolated multilingual preview with explicit readiness |
| 5 — Integration | V2 CI/deployment and later minimal Legacy link | validated public URL and regression evidence |

No worker may independently invent a conflicting schema or silently alter another worker's contract. Worker 1 owns schema changes. No Legacy runtime, data or scoring changes are allowed. Worker 5 adds the Legacy-to-V2 link only after a verified V2 URL exists.

Sequence: schema → reviewed sample data and evaluation fixtures → standalone V2 preview → CI/deployment smoke → Legacy entry link. No automatic Legacy/V2 comparison is required.
