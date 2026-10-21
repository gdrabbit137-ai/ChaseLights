# ChaseLights V2 — Access Advisory Priority Decision

Status: Product decision (D-2026-01), supplementing `ACCESS_ADVISORY_SPEC.md`.
Date: 2026-10-22. Scope: V2 product behavior and build priority. Does not edit Legacy rules or the navigation safety gate.

## Decision

1. **Advisory remains non-scoring (confirmed).** Access closures, unreachable routes, construction, and unsafe-entry hazards stay out of `ConditionContract` scoring, exactly as `ACCESS_ADVISORY_SPEC.md` requires. No new scoring blockers are introduced for access state.
2. **Advisory is presentation-only, marked low priority.** When a site is *researched as known unreachable or dangerous*, the V2 UI shows a clearly labeled reminder/warning (via `access_notes_i18n` / `safety_notes_i18n`) alongside an otherwise unchanged suitability result. This warning layer is a **low-priority feature (P3)**: it must not block or delay any higher-priority V2 work.
3. **Data sourcing is deferred.** The mechanism for *periodically searching* closure/hazard information (official announcements, news, community reports), the advisory data structure (spot ID → warning text + period + source), and any update/alerting workflow are **deliberately deferred until the V2 website is complete**. Until then:
   - No scheduled search jobs, scrapers, or notification pipelines for access data shall be built.
   - Advisory content may exist only as manually maintained static notes if needed for testing; none may be fabricated as if sourced.
4. **Invariants that do NOT change:**
   - The navigation safety gate in `ACCESS_ADVISORY_SPEC.md` (no verified Directions from unknown/closed routes, no encouraging entry) remains fully in force at all times, regardless of priority.
   - No weather provider, numeric threshold, or factual legal status may be fabricated to populate or demo an advisory.
   - All advisory text, when present, must be semantically equivalent in zh-TW / en / ja per the i18n policy.

## Execution policy for the agent

- Build V2 core (data feeds, formula scoring, explorer UI, W2–W5 migration) as specified elsewhere. Do not spend task time on advisory search/sourcing until the user reopens this decision after website completion.
- If any planned work item conflicts with this document — e.g. a spec clause effectively forces building access-data collection now — the agent MUST stop and notify the user with: the conflicting clause, why it is hard to execute, and options (change the document / change the implementation). The user decides whether the document changes.
- When the user reopens this decision, the deferred design items are: (a) source list and refresh cadence, (b) advisory data schema, (c) manual maintenance workflow (user-maintained).

## zh-TW 摘要

1. 存取/危險資訊維持「不計分、僅提示」原則（與 ACCESS_ADVISORY_SPEC 一致）。
2. 已知無法到達或有危險的地點：僅顯示醒目警語/提醒，不改變評分結果；此功能優先度為低（P3）。
3. 定時搜尋封閉/危險資訊、警語資料結構與維護流程，全部延後到 V2 網站完成後再設計；在此之前不建置任何排程搜尋或通知管線。
4. 導航安全閘門（不對未知/封閉路線提供驗證導航、不鼓勵進入）不受優先度影響，永遠生效；不得偽造任何氣象或法律狀態資料。
5. 若文件內容難以執行，Agent 必須回報衝突條款與選項，由使用者決定是否修改文件。
