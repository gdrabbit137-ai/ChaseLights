-- CL-UI-99: notify_rules gains an optional custom-conditions payload.
-- NULL/absent = legacy subject mode (opportunity_id rules) — untouched.
-- A rule with a custom_conditions JSON blob runs in CUSTOM mode: the cron
-- engine judges per-hour weather values (cloud low/mid/high %, precipitation
-- mm/h, visibility km, wind m/s, HH:MM window, lead minutes) against the
-- blob. Subject mode and custom mode are mutually exclusive by contract.
-- NOTE: 0008 is intentionally skipped — reserved by the in-flight
-- CL-DATA-70 feedback migration on its own branch.
ALTER TABLE notify_rules ADD COLUMN custom_conditions TEXT;
