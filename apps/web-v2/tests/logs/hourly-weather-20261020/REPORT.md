# W4 Issue #526: offline hourly view

- Owner/scope: W4, `apps/web-v2/` only. Base `main`:
  `6c3f0e46728b9b774a1d6edf657c979f2823827e` (verified again during work).
- Source: W5 `ops/v2/evidence/open-meteo-one-shot-20261019/replay.json.gz`;
  `operation=OFFLINE_REPLAY`, `network_attempts=0`, `new_live_capture=false`.
  Original response SHA-256 `e441ea1bad2d42cfd89169bb030d7aec518d798c56aafe61e037f8a0e9406b1f`.
  W4's exact JSON copy SHA-256 `e1ed353e7fcbe5a542d54da1c50e8f2b990fdade834b6fa54be0a53e1191b9ab`.
- `node --test --test-isolation=none --test-reporter=tap apps/web-v2/tests/*.test.mjs`:
  **60 PASS, 0 FAIL/ERROR/SKIP**, actual output in `node.log`.
- `CHROMIUM_EXECUTABLE=/usr/bin/chromium node --test --test-isolation=none --test-timeout=120000 --test-reporter=tap apps/web-v2/tests/browser-smoke.mjs apps/web-v2/tests/task-s-browser.mjs apps/web-v2/tests/photography-topics-browser.mjs apps/web-v2/tests/hourly-weather-browser.mjs`:
  **96 PASS, 0 FAIL/ERROR/SKIP**, actual output in `browser.log`. Includes
  desktop 1440px and mobile 360px in all three locales, keyboard, original
  search/topics, 72 hours, missing/zero, no external requests and failed
  archive/digest states. Chromium's loopback server required execution with
  the environment's network permission.
- `git diff --check`: PASS. Final changed paths are all under W4 ownership.

An initial Node run failed one existing VM harness because its mocked module
bindings did not include the new W4 panel initializer; the harness is updated.
An initial browser run could not find Playwright's default cached Chromium;
the final command names the installed `/usr/bin/chromium`. Neither initial
attempt is counted as a passing run.

The archived response was captured once on 2026-10-19 16:43 UTC. It is not
ongoing live provider data or validated coastal weather. The static view always
remains historical/stale and `NOT_EVALUABLE`; source issue/model update time is
unknown. Browser automation does not establish physical-phone or human
translation approval. W5 must independently review this tree, add the fixture
and modules to the static build, update exact source pin/test discovery and run
full integration before a separately approved merge. No W5 file is modified.
