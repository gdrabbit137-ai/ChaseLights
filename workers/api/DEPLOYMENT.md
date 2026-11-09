# CL-API-01 deployment evidence (2026-11-09 UTC)

## Cloudflare resources created
- D1: `chaselights-db` (id `05ef33f5-b833-4418-9b0d-ceca81db4f86`), migrations `0001_init.sql` + `0002_users_id_notnull.sql` applied remotely (3 tables, 20 rows written on 0002).
- KV: namespace `EVALS` id `330ba59f50bc47e7b5aef11d7da059c6` (preview `590d7aae…`).
- Worker: `chaselights-api` bound to the chaselights.app zone route `chaselights.app/api/v1/*`.

## Deploy versions
- `13da75e3-86bc-4d89-8c75-cee1e8e4a1b8` (initial)
- `8e67c504-7715-42fb-9739-490d2ba4c423` (getUser → device_id key fix after live NOT NULL error)

## Live checks (all with browser UA — Cloudflare bot protection 403s curl default)
- `GET /api/v1/health` → `{"ok":true,"service":"chaselights-api","version":"v1","time":"2026-11-09T18:14:52Z"}`
- `GET /api/v1/evaluations` → index JSON (generated_at 2026-11-09T16:46:44Z, 168h, 349 distilled places; KV seeded index + 50 place keys via wrangler, CI syncs the rest)
- `GET /api/v1/evaluations?place_id=jp-001` → per-place results: subjects → days {local_date, verdict, hours}, next_window; NO threshold/condition fields (distill script fail-closed greps for leaked keys)
- `GET /api/v1/evaluations?place_id=nope` → 404 `{"error":"place not evaluated"}`
- `POST /api/v1/favorites` `{userId, placeId}` → `{"ok":true,"action":"add"}`; GET then shows the row; `action:"remove"` deletes — verified round-trip on live D1.
- CORS: `Origin: https://chaselights.app` echoes allowed; other origins get `Access-Control-Allow-Origin: null`.

## Known limitations (v1)
- KV currently holds 50/349 places (local seed cap); CI workflow `b169_kv_sync.yml` uploads all on next scheduled run — requires owner to create GitHub secret `CHASELIGHTS_CF_API_TOKEN` (TODO), workflow fail-closed skips without it.
- Rate limiter is per-isolate in-memory (60 req/min/IP).
