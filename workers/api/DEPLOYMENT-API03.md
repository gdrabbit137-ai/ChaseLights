# CL-API-03 deployment evidence (2026-11-10 UTC)

Notification engine: cron (every 30 min) matching notify_rules against the next-24h
distilled evaluation windows, dedupe via notify_log PK, Telegram delivery; rules +
Telegram-binding + web-push-skeleton endpoints (JWT-only); free 3 / paid 30 limits.

## Branch / commits (worktree `D:/tmp/clapi03-wt`, branch `task/CL-API-03`, base origin/main 2a2929ad0)
- `cf293ae57` migration 0004 (min_advance_hours + telegram_bindings + notify_log + web_push_subscriptions)
- `8f16621fe` engine + endpoints + scheduled() + wrangler.toml crons
- `8d7ab0860` tests (16/16: matcher, cron dedupe, TG mock, limits, binding poll)
- `d6b8d2e22` fix two pre-existing KV defects that starved the engine (see below)
- (evidence commit follows this file)

## Pre-existing defects found & fixed (in-scope: the engine consumed neither)
1. **KV hours were all empty**: `scripts/kv_distill.py` kept only `isinstance(h, int)`
   good_hours, but the bundle carries `"HH:MM"` strings → every distilled day had
   `hours: []`. Fixed to normalize ints and "HH:MM" strings.
2. **KV values double-wrapped**: `b169_kv_sync.yml` uploaded `{"value": <json>}` as the
   request body; the KV values REST endpoint stores the body RAW, so every record was
   served as `{"value":"{...}"}` and `GET /evaluations` returned junk. Fixed to raw-body
   text/plain upload.
3. KV re-seeded NOW from the live bundle (index + tw-001/tw-029/tw-030/tw-037/tw-069/
   tw-070/tw-071/tw-107/us-117) via `wrangler kv key put --remote`; remaining 340 places
   self-heal at the next scheduled b169_kv_sync run (fix requires this branch on main).

## D1 (remote, chaselights-db)
- 0004 applied via `wrangler d1 execute --remote --file`; `sqlite_master` shows
  telegram_bindings / notify_log / web_push_subscriptions; `PRAGMA table_info(notify_rules)`
  confirms `min_advance_hours INTEGER` (default 24).

## Secrets / deploy
- `TG_BOT_TOKEN` set via `wrangler secret put` (value [REDACTED], shared existing bot @chaselights_cm_bot).
- `wrangler deploy` → Version `b0b86384-5b12-446a-b01e-75d033df24db`, route
  `chaselights.app/api/v1/*`, schedule `*/30 * * * *` registered.

## Live endpoint checks (browser UA; edge 403s default curl UA)
- `GET /health` → 200 v2-auth
- `POST /notify/rules` anonymous → **401** `JWT session required`
- `POST /notify/rules` Bearer (self-minted JWT, sub `p:line:clapi03-livecheck`) →
  3 rules created (`{"ok":true,...,"count":n,"limit":3}`), 4th → **402**
  `{"error":"notify rule limit reached — upgrade to paid for more","level":"free","limit":3,"count":3}`
- `GET /notify/rules` → list w/ level + rules; validation: bad channel / bad
  minAdvanceHours / missing placeId → 400
- `POST /notify/telegram/start` → deep-link `https://t.me/chaselights_cm_bot?start=<token>` + pending
- `GET /notify/telegram/status` → `{"status":"pending","chatId":null}`
- `POST /notify/web_push/subscribe` → `{"ok":true,"delivery":"skeleton — VAPID delivery ships in a follow-up ticket"}`

## Local scheduled pipeline (`wrangler dev --test-scheduled`, local D1/KV, fake TG token)
- `/__scheduled` → `[notify-cron] rules_scanned:1, matches:1` → notify_log row
  `clapi03-live-rule | 2026-11-10T17:00 | delivered=0` (404 expected — fake token),
  repeat triggers → `skipped_dupe:1, undelivered:0` (dedupe proven in worker runtime).

## Remote end-to-end
- Live rule `clapi03-live-rule` (tw-030 / tw-030-P01, advance 0) + active binding to the
  owner chat inserted remotely; natural 17:00 cron executed — evidence in the report
  commit + tail log (notify_log delivered flag + Telegram push).

## Local test summary (node --test, 16/16 pass incl. CL-API-01/02 suites)

## Owner TODO
- Open the deep-link once (real /start) to bind the owner's own app user — current
  binding is the manager's live-check row for the probe user.
- Optional: after merge, verify the next scheduled b169_kv_sync reseeds all 349 places
  with real hours (spot-check `GET /api/v1/evaluations?place_id=<id>` hours non-empty).
