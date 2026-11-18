-- CL-APP-09 (owner ruling): user-defined subject sets (自訂題材) on OFFICIAL
-- spots. Each row is one personal condition group owned by one member:
--   - place_id     — the OFFICIAL spot the set rides (e.g. tw-014)
--   - name         — free-form; duplicates ARE allowed (owner ruling:
--                    題材可重複、命名不阻擋重名), so no UNIQUE(name)
--   - template_id  — the official opportunity forked from (nullable)
--   - base_rev     — the official contract revision at fork time; when the
--                    live contract's revision moves past this, the fork is
--                    marked 「官方已更新可同步」
--   - base_conditions — the mappable weather subset of the official contract
--                    snapshotted at fork time (diff + ±30% tolerance base)
--   - conditions   — CL-UI-99 five-parameter-group JSON (same schema as
--                    notify_rules.custom_conditions / custom_places
--                    custom_conditions; the worker re-validates)
--   - months       — JSON array of ints 1..12 (適用月份 multi-select;
--                    empty = all year)
-- Caps (owner ruling, 追加2 steer 2026-11-18: the 20-total rule is CANCELLED —
-- only the per-point rule remains): 5 sets per user per official place (paid)
-- / 1 set PER PLACE as the free trial / unlimited (owner). There is NO
-- system-wide total cap anymore; counts.total is informational only. Free
-- over-cap is fail-closed 403 with concrete numbers; rows are NEVER
-- mass-deleted.
-- Indexes cover the two reads: per-place listing/eval and the total count.
CREATE TABLE IF NOT EXISTS custom_subject_sets (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  place_id TEXT NOT NULL,
  name TEXT NOT NULL,
  template_id TEXT,
  base_rev INTEGER,
  base_conditions TEXT,
  conditions TEXT,
  months TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_custom_subject_sets_user_place
  ON custom_subject_sets (user_id, place_id);
CREATE INDEX IF NOT EXISTS idx_custom_subject_sets_user
  ON custom_subject_sets (user_id);
