-- CL-API-02C: OAuth auth state moves off KV (KV put() daily free-tier cap was
-- exhausted by manual re-seeds, 500ing /auth/*/start). auth_states holds the
-- single-use CSRF state; rows are self-cleaning (opportunistic DELETE of rows
-- older than 15 minutes on every read).
CREATE TABLE IF NOT EXISTS auth_states (
  state      TEXT PRIMARY KEY,
  payload    TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
