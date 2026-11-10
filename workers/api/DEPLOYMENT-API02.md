# CL-API-02 deployment evidence (2026-11-10 UTC)

Member system: OAuth login (LINE primary + Google fallback skeleton) → D1 users,
signed-JWT sessions, anonymous-data merge.

## Branch / commits (worktree `D:/tmp/clapi02-wt`, not merged/pushed)
- `cd8fa6bcb` migration 0003 users OAuth columns (provider / provider_user_id / display_name / level + unique identity index)
- `5cddd1820` worker OAuth skeleton + /auth/me|logout|refresh, Bearer-aware favorites
- `df20b588a` auth tests (14 total incl. CL-API-01's 6, all green)
- `b61d3f9ae` multi Set-Cookie via Headers.append
- `80ad4fca6` /auth/me self-heal for valid sessions with missing users row (live-check finding)

## D1 (remote, chaselights-db)
- `0003_users_oauth.sql` applied via `wrangler d1 execute --remote --file`.
- `PRAGMA table_info(users)` confirms columns: id, device_id, created_at, provider, provider_user_id, display_name, level.
- Live-check row verified: `p:line:clapi02-livecheck` (provider=line, level=free).

## Secrets
- `wrangler secret put AUTH_SECRET` → uploaded ([REDACTED]); token values [REDACTED] throughout.

## Worker versions
- `1b5165f8-09d3-4fe5-80a9-f91771a9e77f` (CL-API-02 first deploy)
- `393bd8d9-52bd-4dc2-99b7-70927df95448` (self-heal fix)
- Route unchanged: `chaselights.app/api/v1/*`.

## Live endpoint checks (browser UA; curl default UA 403s at the edge)
- `GET /api/v1/health` → `{"ok":true,"service":"chaselights-api","version":"v2-auth",...}`
- `GET /api/v1/auth/me` anonymous → **401** `{"error":"unauthorized"}`
- `GET /api/v1/auth/line/start` (no owner creds yet) → **503** `{"error":"line OAuth credentials not configured (owner application pending)"}`
- `GET /api/v1/auth/mock/start` in prod (AUTH_MOCK unset) → **404** (mock can never serve in production)
- `POST /api/v1/favorites` with `Authorization: Bearer <HS256 JWT>` (self-minted with AUTH_SECRET) → `{"ok":true}`; GET with Bearer → favorites scoped to `p:line:clapi02-livecheck` on live D1
- `GET /api/v1/auth/me` with Bearer → `{"user":{"id":"p:line:clapi02-livecheck","provider":"line","providerUserId":"clapi02-livecheck","displayName":"CL-API-02 Live Check","level":"free"}}`
- `POST /api/v1/auth/logout` → `{"ok":true}` + `Max-Age=0` cookie clears
- `POST /api/v1/auth/refresh` with garbage token → 401
- Legacy anonymous favorites (userId param) still work unchanged.

## Local mock-provider OAuth flow (wrangler dev --local, AUTH_MOCK=1, migrations applied locally)
- `GET /auth/mock/start?provider=google&user=dev42&name=Dev42` → 200, user `p:google:dev42`, `cl_session` + `cl_refresh` HttpOnly cookies set; `GET /auth/me` with the session cookie → 200 user JSON.
- Anonymous merge: anonymous `dev-anon` favorite `tw-009` → login `?merge=dev-anon` → `mergedRows:1`, row re-keyed to `p:line:merger42`.
- `GET /auth/line/start` without creds → 503 (skeleton behaviour confirmed locally too).

## Test summary (node --test, 14/14 pass)
- JWT sign/verify; tamper + wrong-secret + expiry rejected
- /auth/me 401 anon / 200 Bearer / 200 self-heal
- OAuth start→callback with mocked LINE token+userinfo endpoints; state single-use (replay + forged state → 400)
- Mock provider disabled when AUTH_MOCK unset
- Refresh (real refresh token rotates; garbage → 401), logout clears cookies
- Anonymous merge case (2 favorites + 1 notify_rule → 3 rows re-keyed)
- Bearer precedence over legacy userId; anonymous legacy still works

## Owner application steps pending (credentials via wrangler secret put)
- LINE Login: channel at https://developers.line.biz/ — callback `https://chaselights.app/api/v1/auth/line/callback`, scope openid+profile
- Google OAuth: Cloud Console OAuth client (Web) — callback `https://chaselights.app/api/v1/auth/google/callback`
- After receiving: `wrangler secret put LINE_LOGIN_CLIENT_ID`, `LINE_LOGIN_CLIENT_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
