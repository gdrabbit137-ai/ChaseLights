-- CL-APP-06 (DESIGN-8, owner rulings 2026-11-15): custom places (private
-- points). A member may pin ANY latitude/longitude worldwide (ocean/polar
-- included) as a private point: name + lat/lng + auto DEM elevation + auto
-- timezone, then attach CL-UI-99 custom conditions (five parameter groups —
-- the SAME schema notify_rules.custom_conditions uses; subject mode and
-- custom mode stay mutually exclusive there, and here the optional blob only
-- adds constraints on top of the lenient general baseline).
--
-- Caps (owner ruling): free members get a 3-point trial for 90 days measured
-- from users.created_at; after the trial the cap is 0 — every active point
-- flips to status='trial_expired' (data KEPT, evaluation STOPPED, hidden from
-- the default list, gray-shown under the private filter with an honest
-- 「試用期滿」 label). paid = 50. owner = unlimited. When a free member hits
-- the trial cap the points are NEVER deleted (grandfather rule) — only new
-- adds are blocked.
--
-- Delete semantics (owner anti-abuse ruling): delete is SOFT — status goes
-- 'archived' + deleted_at is stamped. Re-adding the same (user, lat/lng
-- rounded to 0.001°) within 30 days REVIVES the row (existing data reused,
-- no new fetch queued).
--
-- Anti-abuse layers (owner ruling, close-out update: the rolling 30-day
-- distinct budget cap×1.5 was REMOVED as a gate — daily cost is already
-- capped by the per-user daily fetch budget 60 and the extra layer only
-- confused users; the distinct-key count is kept as internal telemetry):
--   1. daily add cooldown: at most 60 creates per user per day (403 + honest
--      trilingual message; a friendly reminder rides the 50th add);
--   2. per-user daily fetch budget: at most 60 actual weather fetches per
--      user per day — excess queue entries defer to the NEXT day, the point
--      stays created and its card honestly reports the delayed update;
--   3. first-fetch downgrade: a newly created point's first fetch is queued
--      LOW priority (custom_fetch_queue) — bulk adds never burst the API.

CREATE TABLE IF NOT EXISTS custom_places (
  id          TEXT PRIMARY KEY NOT NULL DEFAULT (lower(hex(randomblob(16)))),
  user_id     TEXT NOT NULL,              -- users.device_id (member identity)
  name        TEXT NOT NULL,
  lat         REAL NOT NULL,
  lng         REAL NOT NULL,
  elevation   REAL,                       -- DEM auto (Elevation API); never user-edited
  timezone    TEXT,                       -- IANA name, auto-resolved at create
  custom_conditions TEXT,                 -- CL-UI-99 five-parameter JSON blob (nullable)
  status      TEXT NOT NULL DEFAULT 'active'
              CHECK (status IN ('active','trial_expired','archived')),
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
  deleted_at  TEXT                        -- set when archived (soft delete)
);

-- List rendering + per-user counting.
CREATE INDEX IF NOT EXISTS idx_custom_places_user
  ON custom_places(user_id, status);

-- Dedupe/revive lookups: same (user, rounded coords) within 30 days.
CREATE INDEX IF NOT EXISTS idx_custom_places_dedupe
  ON custom_places(user_id, lat, lng);

-- Cron: next due low-priority fetches.
CREATE TABLE IF NOT EXISTS custom_fetch_queue (
  place_id    TEXT PRIMARY KEY,
  user_id     TEXT NOT NULL,
  reason      TEXT NOT NULL DEFAULT 'new'
              CHECK (reason IN ('new','refresh','revive')),
  priority    INTEGER NOT NULL DEFAULT 20, -- 20 = low (first fetch); 30 = bulk-refresh
  due_at      TEXT NOT NULL DEFAULT (datetime('now')),
  status      TEXT NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending','done')),
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_custom_fetch_queue_due
  ON custom_fetch_queue(status, priority, due_at);
