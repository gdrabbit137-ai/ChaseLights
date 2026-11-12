-- CL-APP-03: FCM device push tokens (APP push is the default reminder channel).
-- PK is the raw FCM token (a re-issued token updates the row in place via
-- ON CONFLICT ... DO UPDATE in POST /api/v1/push_tokens).
CREATE TABLE IF NOT EXISTS push_tokens (
  user_device_id TEXT NOT NULL,
  platform       TEXT NOT NULL DEFAULT 'android/fcm',
  token          TEXT NOT NULL,
  updated_at     TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (token)
);
CREATE INDEX IF NOT EXISTS idx_push_tokens_user ON push_tokens(user_device_id);
