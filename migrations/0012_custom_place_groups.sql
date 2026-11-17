-- CL-APP-08 (owner-approved conservative version): private-place grid
-- deduplication. Two ACTIVE private points of the SAME member share ONE
-- Open-Meteo grid fetch when: distance < 1 km AND DEM elevation diff < 30 m
-- AND 500 m-neighborhood terrain relief ≤ 100 m AND the straight line
-- between them crosses no ridge line / gully mouth. A group counts as ONE
-- quota point (one forecast fetch, one user-budget unit); the judgment side
-- changes ZERO — every member keeps its own DEM elevation/timezone in its
-- own eval record, only the raw grid (cloud/precip/visibility/wind) is
-- shared. Escape hatch: a point can detach (share_mode='independent') and
-- refetch solo, costing 1 quota.
--
-- group_id    — NULL = independent; 'g:<rep place id>' = group key.
-- share_mode  — 'auto' (dedup eligible) | 'independent' (escape hatch:
--               permanently excluded from grouping, always fetches solo).
-- The background migration stamps these columns for already-existing
-- places ONCE (cron-guarded via KV v1:cp:regroup:done) and never queues a
-- fetch nor bumps any counter for the migration itself.

ALTER TABLE custom_places ADD COLUMN group_id TEXT;
ALTER TABLE custom_places ADD COLUMN share_mode TEXT NOT NULL DEFAULT 'auto';

CREATE INDEX IF NOT EXISTS idx_custom_places_group
  ON custom_places(group_id, status);
