-- CL-API-02: member system (OAuth login -> D1 users).
-- Worker keeps device_id as the universal user key: OAuth identities get a
-- synthetic device_id "p:{provider}:{provider_user_id}" so favorites/notify_rules
-- (keyed by device_id since CL-API-01) keep working unchanged. Anonymous device
-- rows are merged into the OAuth identity's key at login time.
-- No thresholds/condition formulas are stored here (results only).

ALTER TABLE users ADD COLUMN provider          TEXT;
ALTER TABLE users ADD COLUMN provider_user_id  TEXT;
ALTER TABLE users ADD COLUMN display_name      TEXT;
ALTER TABLE users ADD COLUMN level             TEXT NOT NULL DEFAULT 'free';

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_provider_uid
  ON users(provider, provider_user_id) WHERE provider IS NOT NULL;
