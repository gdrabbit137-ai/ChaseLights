-- CL-API-01 follow-up: SQLite TEXT PRIMARY KEY alone permits NULL ids (observed
-- live: users.id was null after device INSERT). Future installs get a NOT NULL
-- random default; the live DB already carries rows with null ids — favorites
-- reference device_id instead (worker uses device_id as the user key), so no
-- backfill is required for v1. Member-OAuth ticket will migrate keys.
ALTER TABLE users RENAME TO users_old;
CREATE TABLE users (
  id            TEXT PRIMARY KEY NOT NULL DEFAULT (lower(hex(randomblob(16)))),
  device_id     TEXT UNIQUE NOT NULL,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO users (id, device_id, created_at)
  SELECT COALESCE(id, lower(hex(randomblob(16)))), device_id, created_at FROM users_old;
DROP TABLE users_old;
