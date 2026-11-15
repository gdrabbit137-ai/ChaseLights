-- CL-DATA-70 (DESIGN-7 v2): unified UGC feedback channel — one table carries
-- ratings (place L/P two-axis votes), reports (error reports → owner ticket
-- queue) and comments (first-review moderated). Per ticket schema: identifiers
-- in real columns, per-kind fields in a payload JSON blob.
-- Status semantics (fail-closed): ratings land 'ok' (they ARE the aggregate);
-- reports/comments land 'pending' and only become 'ok' after admin review.
-- flagged/rejected rows stay in the table for the audit trail — they never
-- enter the aggregate.

CREATE TABLE IF NOT EXISTS feedback (
  id          TEXT PRIMARY KEY NOT NULL DEFAULT (lower(hex(randomblob(16)))),
  user_id     TEXT NOT NULL,              -- users.device_id (member identity)
  place_id    TEXT,                       -- rating/report required; comment NULL = site-wide
  type        TEXT NOT NULL CHECK (type IN ('rating','report','comment')),
  status      TEXT NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending','ok','flagged','rejected','need_info')),
  payload     TEXT NOT NULL DEFAULT '{}', -- JSON: l, p, shot_date, report_category,
                                          -- comment_text, fix_suggest, photo_url,
                                          -- source, trust_level, weight,
                                          -- ip_cluster, device_hash, flag_reason,
                                          -- reviewed_by, reviewed_at
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One member, one vote per place (edit overwrites the same row, never a second vote).
CREATE UNIQUE INDEX IF NOT EXISTS idx_feedback_vote
  ON feedback(user_id, place_id) WHERE type = 'rating';

-- Aggregate reads + per-place comment listing.
CREATE INDEX IF NOT EXISTS idx_feedback_agg
  ON feedback(place_id, type, status, created_at);

-- Admin review queue (pending/flagged listings).
CREATE INDEX IF NOT EXISTS idx_feedback_queue
  ON feedback(status, type, created_at);

-- Throttle (90s rule) + trust-ladder recomputation.
CREATE INDEX IF NOT EXISTS idx_feedback_user_time
  ON feedback(user_id, created_at);

-- Owner ruling (Stage 1 addition): display_name change audit. The member can
-- rename themselves at most once per 7 days (enforced in /auth/profile when
-- the feedback channel is live); every accepted rename lands here so admins
-- can trace masked-name abuse. Trust/rating weights stay keyed to user_id —
-- renames never touch them.
ALTER TABLE users ADD COLUMN name_history TEXT NOT NULL DEFAULT '[]';

-- Owner ruling (Stage 1 addition): member grading uses the EXISTING
-- users.level column — value domain extended to three values
-- 'free' / 'paid' / 'owner' (no new column; current rows all 'free').
-- Reminder caps: free 3 / paid 20 / owner unlimited. The owner account
-- (level='owner') is flagged by the manager directly in D1; until billing
-- goes live a KV flag (v1:flags:member {freeAsPaid:true}) treats everyone
-- as paid for testing.
