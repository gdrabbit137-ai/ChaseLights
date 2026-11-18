-- CL-APP-09 追加2 (steer ④): KV cache-write budget metering table.
--
-- Read-time custom-subject verdicts are cached in worker KV under
--   v1:ssc:<place_id>:<generated_at>:<hash(conditions)>
-- so members with IDENTICAL condition sets share cache entries. Worker KV
-- allows 1000 writes/day TOTAL (shared with catalog digests, custom places,
-- flags, ...), so cache writes are metered PER USER per UTC day.
--
-- The meter lives in D1 on purpose: accounting in KV would burn one KV write
-- per cache write and double the cost. One atomic upsert charges n writes and
-- refuses (no row) once the day's budget is exhausted:
--   INSERT INTO ss_kv_budget ... ON CONFLICT(user_id, day)
--     DO UPDATE SET writes = writes + n WHERE writes + n <= cap
--     RETURNING writes
-- Over-budget requests still evaluate and answer NORMALLY (transparent) —
-- only the KV write is skipped; the budget resets next UTC day.
-- Default cap 40 writes/user/day (≈25 users saturate the 1000/day KV plan;
-- owner-tunable via the SS_KV_WRITES_USER_DAY worker var).
CREATE TABLE IF NOT EXISTS ss_kv_budget (
  user_id TEXT NOT NULL,
  day TEXT NOT NULL,           -- UTC yyyymmdd
  writes INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, day)
);
