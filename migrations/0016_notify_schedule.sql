-- CL-UX-01 Part B: user-controlled reminder schedules.
-- Every column is NULLable: NULL = "inherit the caller's notify_defaults row"
-- (single-place override = the column is non-NULL on the rule). When BOTH the
-- rule and the defaults are NULL for every schedule field the engine keeps the
-- pre-CL-UX-01 behaviour exactly (fire on the first qualifying window inside
-- the 24h match window, dedupe by (rule_id, window_start), one message/rule).
--
-- schedule_mode      'every_n_days' | 'weekdays' | NULL (legacy/inherit)
-- schedule_every_n   1..7  cadence for every_n_days (days between sends)
-- schedule_weekdays  CSV of 0..6 (0=Sunday), e.g. '4,5'
-- send_time          'HH:MM' wall clock in the USER's tz (may be non-round,
--                    e.g. 20:15 — the 30-min cron matches on the local-date
--                    bucket, never on exact string equality)
-- lead_days          1..7 forecast look-ahead days (place-local dates)
-- target_weekdays    CSV 0..6, NULL = any day
-- min_tier           'recommend' | 'shootable' (shootable = recommend OR shootable)
-- tz                 IANA user timezone (send_time is interpreted there)
-- last_sent_at       ISO instant of the last SUCCESSFUL scheduled send; the
--                    start point of the every_n_days cadence
ALTER TABLE notify_rules ADD COLUMN schedule_mode TEXT;
ALTER TABLE notify_rules ADD COLUMN schedule_every_n INTEGER;
ALTER TABLE notify_rules ADD COLUMN schedule_weekdays TEXT;
ALTER TABLE notify_rules ADD COLUMN send_time TEXT;
ALTER TABLE notify_rules ADD COLUMN lead_days INTEGER;
ALTER TABLE notify_rules ADD COLUMN target_weekdays TEXT;
ALTER TABLE notify_rules ADD COLUMN min_tier TEXT;
ALTER TABLE notify_rules ADD COLUMN tz TEXT;
ALTER TABLE notify_rules ADD COLUMN last_sent_at TEXT;

-- One consolidated message per (user, channel, tick): every per-rule ledger row
-- that fed the same message carries the same batch_id.
ALTER TABLE notify_log ADD COLUMN batch_id TEXT;
CREATE INDEX IF NOT EXISTS idx_notify_log_batch ON notify_log(batch_id);

-- Per-member schedule defaults. A rule column that is NULL inherits from here.
CREATE TABLE IF NOT EXISTS notify_defaults (
  user_id           TEXT PRIMARY KEY,
  schedule_mode     TEXT,
  schedule_every_n  INTEGER,
  schedule_weekdays TEXT,
  send_time         TEXT,
  lead_days         INTEGER,
  target_weekdays   TEXT,
  min_tier          TEXT,
  channel           TEXT,
  tz                TEXT,
  updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
