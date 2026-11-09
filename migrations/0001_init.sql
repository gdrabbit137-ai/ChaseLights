-- CL-API-01: ChaseLights backend base schema (D1)
-- NOTE: auth is device_id-first; OAuth identity columns land with the member ticket.
-- Threshold/condition formula values are NEVER stored here — API returns results only.

CREATE TABLE IF NOT EXISTS users (
  id            TEXT PRIMARY KEY,
  device_id     TEXT UNIQUE NOT NULL,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS favorites (
  user_id     TEXT NOT NULL,
  place_id    TEXT NOT NULL,
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (user_id, place_id)
);

CREATE TABLE IF NOT EXISTS notify_rules (
  id            TEXT PRIMARY KEY,
  user_id       TEXT NOT NULL,
  place_id      TEXT NOT NULL,
  opportunity_id TEXT,
  channel       TEXT NOT NULL DEFAULT 'push',
  enabled       INTEGER NOT NULL DEFAULT 1,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_favorites_user   ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_notify_user      ON notify_rules(user_id);
CREATE INDEX IF NOT EXISTS idx_notify_place     ON notify_rules(place_id);
