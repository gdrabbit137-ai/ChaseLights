-- CL-API-03: notification engine (cron matching + Telegram binding + dedup log).
-- notify_rules gains a lead-time control; notify_log is the dedupe ledger
-- (same rule + same window is pushed once, ever — PK enforces it atomically).
-- web_push_subscriptions is the CL-API-03 skeleton: rows are accepted now,
-- delivery (VAPID) ships in a follow-up ticket.

ALTER TABLE notify_rules ADD COLUMN min_advance_hours INTEGER NOT NULL DEFAULT 24;

CREATE TABLE IF NOT EXISTS telegram_bindings (
  user_id    TEXT PRIMARY KEY,
  chat_id    TEXT,
  status     TEXT NOT NULL DEFAULT 'none',  -- none | pending | active
  token      TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  bound_at   TEXT
);
CREATE INDEX IF NOT EXISTS idx_tg_token ON telegram_bindings(token);

CREATE TABLE IF NOT EXISTS notify_log (
  rule_id        TEXT NOT NULL,
  window_start   TEXT NOT NULL,
  user_id        TEXT,
  place_id       TEXT,
  opportunity_id TEXT,
  channel        TEXT,
  delivered      INTEGER NOT NULL DEFAULT 0,
  detail         TEXT,
  sent_at        TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (rule_id, window_start)
);

CREATE TABLE IF NOT EXISTS web_push_subscriptions (
  user_id    TEXT NOT NULL,
  endpoint   TEXT PRIMARY KEY,
  p256dh     TEXT,
  auth       TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_wps_user ON web_push_subscriptions(user_id);
