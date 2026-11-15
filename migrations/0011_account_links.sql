-- CL-APP-07: account linking (multi-provider identity, Sign in with Apple prep).
-- The universal user key stays users.device_id ("p:{provider}:{provider_user_id}"
-- since CL-API-02); favorites/notify_rules/feedback all key on it. account_links
-- records ALIAS identities that resolve to one PRIMARY user row: the second
-- OAuth login (same verified email, or an explicit 連結 flow from the member
-- center) is re-keyed onto the primary — data (favorites/notify_rules/feedback/
-- custom_places/push_tokens) moves with it (conflict policy: favorites union,
-- reminders all kept, one-rating-per-place keeps the primary's vote).
-- NOTE: numbering jumps to 0011 to leave 0010 free for CL-APP-06 (custom_places,
-- in flight on a parallel branch); migration files apply independently.
-- The users.verified_email column is the linking key: Google/Apple report a
-- verified email at login (stored here); LINE has no email scope, so its
-- members link via the member-center email-verification flow instead.

ALTER TABLE users ADD COLUMN verified_email TEXT;

CREATE TABLE IF NOT EXISTS account_links (
  alias_device_id        TEXT PRIMARY KEY,  -- users.device_id of the linked identity
  primary_user_id        TEXT NOT NULL,     -- users.device_id of the primary account
  alias_provider         TEXT NOT NULL,
  alias_provider_user_id TEXT NOT NULL,
  verified_email         TEXT,              -- email used to establish the link (if any)
  created_at             TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_account_links_primary
  ON account_links(primary_user_id);

-- Email-verification queue for the member-center link flow (no-email providers
-- like LINE): a token is issued by POST /auth/link/start, delivered by email,
-- and consumed by the /auth/link/verify callback. Tokens live 30 minutes and
-- are single-use; expired rows are deleted opportunistically on every read.
CREATE TABLE IF NOT EXISTS link_email_verifications (
  token      TEXT PRIMARY KEY,
  user_id    TEXT NOT NULL,   -- alias (session) user at request time
  email      TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  consumed   INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_link_email_verifications_user
  ON link_email_verifications(user_id);

-- One verified_email per account: the auto-link lookup runs BEFORE the write,
-- so this unique index can only trip on a race — which fail-closed is correct
-- for (the login errors, the member retries).
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_verified_email
  ON users(verified_email) WHERE verified_email IS NOT NULL;
