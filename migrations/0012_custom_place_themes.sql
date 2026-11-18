-- CL-APP-06 patch-8: ONE private point may carry MULTIPLE condition groups
-- (custom themes). Each group = name (i18n object; legacy single `name` kept)
-- + a CL-UI-99 five-parameter conditions blob (months live INSIDE the blob —
-- the same schema the notify engine already validates) + its own timestamps.
--
-- Limits (owner ruling): at most 5 groups per place (a cost brake against
-- abuse; the quota dedup does NOT apply here — weather is fetched ONCE per
-- place and every group judges the SAME stored hourly rows, so theme CRUD
-- never enqueues a fetch and never consumes the daily fetch budget).
-- Duplicate names are deliberately NOT blocked (owner ruling).
--
-- Migration of the existing single set: every custom_places row with a
-- non-null custom_conditions blob becomes ONE group (name 「題材 1」). The
-- worker ALSO backfills lazily per place (loadThemeGroups) so the migration
-- takes effect even before the remote D1 apply — data can never be lost.

CREATE TABLE IF NOT EXISTS custom_place_themes (
  id          TEXT PRIMARY KEY NOT NULL DEFAULT (lower(hex(randomblob(16)))),
  place_id    TEXT NOT NULL,              -- custom_places.id
  user_id     TEXT NOT NULL,              -- users.device_id (ownership mirror)
  name        TEXT NOT NULL,              -- display name (zh-TW working language)
  name_i18n   TEXT,                       -- optional {"zh-TW":..,"en":..,"ja":..} JSON; NULL = name fallback
  conditions  TEXT,                       -- CL-UI-99 five-parameter JSON blob (months inside; NULL never allowed on writes)
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_custom_place_themes_place
  ON custom_place_themes(place_id, created_at);

-- Existing single custom_conditions blob → one group per place (idempotent:
-- re-running inserts nothing because the backfill filters on a NOT EXISTS).
INSERT INTO custom_place_themes (place_id, user_id, name, conditions)
SELECT p.id, p.user_id, '題材 1', p.custom_conditions
FROM custom_places p
WHERE p.custom_conditions IS NOT NULL
  AND p.status != 'archived'
  AND NOT EXISTS (
    SELECT 1 FROM custom_place_themes t WHERE t.place_id = p.id
  );
