# ChaseLights R4.2 B32 — Japan Research Migration Batch 10

Date: 2026-09-25 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

## Scope

This batch migrates:

- `jp-021 新穗高高空纜車` → **新穗高・西穗高口展望台 / Shinhotaka · Nishi-Hotakaguchi Observatory**

The legacy broad coordinate is retired as the photography/navigation anchor. Research is centered on the real summit visitor photography area at Nishi-Hotakaguchi Station.

## Time-zone contract

- Shooting windows, hourly forecast rows, access windows and event times use the Place local timezone: `Asia/Tokyo` (JST).
- Website `Last Updated` continues to use the user's browser/device timezone.
- Never convert a Shinhotaka shooting window into the user's timezone for display.

## Camera Zone

Primary researched Camera Zone:

- Name: 西穗高口站屋頂展望台／頂之森 Camera Zone
- Anchor: `36.268335, 137.601580`
- Elevation: `2156 m`
- Geometry: small-area visitor observation zone, approximately 120 m extent
- Confidence: high

Cross-check:
- official Shinhotaka Ropeway material identifies Nishi-Hotakaguchi Station rooftop and Itadaki no Mori as summit scenic areas;
- MapFan station coordinate: approximately `36.2678409, 137.6017974`;
- multiple geotagged camera locations cluster within the same summit station area.

This is not a mandatory tripod point. It represents the legal summit visitor photography zone.

## Official research evidence

### Summit panorama

Shinhotaka Ropeway official material states:
- Nishi-Hotakaguchi Station is approximately 2,156 m above sea level;
- the rooftop observation deck offers a 360-degree Northern Alps panorama;
- identifiable landscape subjects include Mt. Nishihotaka, Mt. Yari, Mt. Kasagatake and the deep alpine valley;
- Itadaki no Mori provides additional outdoor viewpoints.

Sources:
- https://shinhotaka-ropeway.jp/en/info01/
- https://shinhotaka-ropeway.jp/en/about/

### Seasonal photography value

Official seasonal material supports:
- spring: remaining snow + new green contrast;
- summer: alpine greenery;
- autumn: foliage, typically with a strong period around mid-October; snow-capped peaks may coexist with autumn color;
- winter: snow-covered Northern Alps.

Source:
- https://shinhotaka-ropeway.jp/en/season/

These are photographic boosters, not guaranteed daily Outcomes. The scorer must not claim autumn foliage or snow is present unless a corresponding seasonal/ground-state signal is available.

### Ropeway access

Official business information states the ropeway is generally operated year-round but may suspend because of:
- adverse weather;
- scheduled maintenance;
- operational notices.

Therefore weather quality alone is not sufficient to recommend the summit.

Source:
- https://shinhotaka-ropeway.jp/en/price/

### Night stargazing access

Night access is **not normal year-round access**.

The official Stargazing Service publishes date-specific night operations. For 2026 autumn the official schedule includes:
- Oct 2–4
- Oct 9–12
- Oct 30–Nov 3
- Nov 6–8

Published special-service timing includes:
- first ascent from Shirakabadaira around 18:00;
- last ascent around 20:20;
- descent service from Nishi-Hotakaguchi until around 21:00.

Only the No. 2 Ropeway operates for the special night service.

Source:
- https://shinhotaka-ropeway.jp/en/2025%E5%B9%B4%E5%BA%A6%E3%81%AE%E6%98%9F%E7%A9%BA%E8%A6%B3%E8%B3%9E%E4%BE%BF%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6/

Do not infer future-year dates from the 2026 schedule.

## Opportunity contracts

### jp-021-P01 — 西穗高口展望台・北阿爾卑斯360°高山景觀

- Theme baseline: `mountain_view`
- Mode: `area_opportunity`
- Runtime status: `dynamic_access_visibility_runtime_ready`
- Best time: ropeway-accessible daylight, Place-local JST
- Required:
  - Northern Alps mountain/valley landscape readable;
  - sufficient visibility;
  - low cloud/fog not materially obscuring the major mountain mass.
- Hard access gate:
  - required ropeway route actually operating;
  - no official suspension/maintenance closure.
- Boosters:
  - clean air;
  - seasonal snow/foliage contrast when actually present.
- Current runtime policy:
  - `preview_module_available`
  - dynamic access + visibility are both runtime-ready.
  - 80+ is allowed only when the dedicated contract is actually satisfied; stale, ambiguous, suspended or schedule-closed access remains fail-closed.

### jp-021-P02 — 西穗高口限定星空觀賞便・北阿爾卑斯星空

- Theme baseline: `milky_way`
- Mode: `area_opportunity`
- Runtime status: `astronomy_ephemeris_dynamic_access_runtime_ready`
- Astronomy module: registered and ready
- Dynamic access: registered and ready for the verified 2026 Stargazing Service contract
- Best time: only official Stargazing Service nights, Place-local JST
- Required:
  - official event date/time is active;
  - special night ropeway actually operating;
  - visitor can still descend on the official last service;
  - astronomy/darkness conditions valid;
  - cloud conditions usable.
- Important:
  - a clear ordinary night is **not** enough;
  - do not claim exact Milky Way foreground alignment without verified geometry.
- Current runtime policy:
  - `preview_module_available`
  - 80+ is allowed only on a verified official Stargazing Service date/time when the same event-window live No.2 Ropeway status confirms operation and the astronomy/cloud contract also matches.

## Runtime / QA invariants

- `jp-021` is researched and must no longer be `research_pending`.
- Expected Opportunity IDs:
  - `jp-021-P01`
  - `jp-021-P02`
- Both Opportunities are now runtime-ready for their researched dependency contracts.
- P01 dependency state:
  - ready: dynamic_access, visibility
  - missing: none
- P02 dependency state:
  - ready: astronomy_ephemeris, dynamic_access
  - missing: none
- P01 access classification: `transport_facility_status`
- P02 access classification: `event_access_control`
- `ACCESS_RUNTIME_READY_PROFILES` contains exactly `jp-021-P01` and `jp-021-P02`; the other access-dependent Opportunities remain fail-closed pending their own providers.
- `jp-021` is permitted in the 80+ whitelist only when the winner is `dedicated_conditions_match`; a partial runtime contract is no longer accepted.
- No legacy `cloud_sea`, sunrise, sunset or snow-scene score may leak into the Place merely because those tags existed in the old catalog.

## Provider implementation and feasibility verified

The official Shinhotaka Ropeway homepage exposes a machine-readable-enough live status block in the public HTML, including:
- a visible update time (for example `08:00 update`);
- current No. 1 Ropeway status;
- current No. 2 Ropeway status.

Official FAQ also explicitly directs visitors to the website for current operating status when strong wind may suspend service.

Official 2026 maintenance notice additionally publishes fixed full-line closure periods:
- 2026-06-15 through 2026-06-26;
- 2026-11-24 through 2026-11-27.

The official English timetable/pamphlet provides summit-access operating windows:
- Green season (Apr 1–Nov 30): Shirakabadaira first ascent 08:45; Nishi-Hotakaguchi last descent 16:45.
- August: first ascent 08:15; last descent 16:45.
- October Saturdays/Sundays/holidays: first ascent 08:15; last descent 16:45.
- Winter (Dec 1–Mar 31): first ascent 09:15; last descent 16:15.
- Separately published 2026 early-morning special-service dates can begin before the regular timetable and must be treated as date-specific exceptions rather than a permanent opening-time change.
- The Stargazing Service has its own night timetable and must remain a separate P02 access contract.

Source:
- https://shinhotaka-ropeway.jp/pdf/pamphlet/en.pdf

Implemented provider contract (`shinhotaka_access.py`, `shinhotaka-access-r1-preview`):
1. Source the official public Shinhotaka Ropeway homepage for live No.1 / No.2 status.
2. Parse both No.1 and No.2 status; P01 summit access is open only when the required route is operational.
3. Preserve source fetch/check timestamp and the visible official update time.
4. If parsing is ambiguous, source layout changes, or either required status is missing, return `unknown` — never infer open.
5. Apply official maintenance closure dates as authoritative scheduled closed windows.
6. A static timetable may prove `closed`, but a static timetable may never prove a live-notice facility `open`.
7. Live-open snapshots expire after the registered six-hour freshness window; future forecast timestamps may not reuse a stale current-open snapshot.
8. P02 separately enforces the exact verified 2026 Stargazing Service calendar and 18:00–21:00 event window. A daytime live status cannot prove night-event operation; the live No.2 status must be stamped within the same event window.
9. Dates beyond the verified 2026 annual event schedule return `unknown`; future-year Stargazing dates are never inferred.

Sources:
- https://shinhotaka-ropeway.jp/en/
- https://shinhotaka-ropeway.jp/en/faq/
- https://shinhotaka-ropeway.jp/%E3%80%902026%E5%B9%B4%E5%BA%A6%E3%80%91%E6%96%B0%E7%A9%82%E9%AB%98%E3%83%AD%E3%83%BC%E3%83%97%E3%82%A6%E3%82%A7%E3%82%A4%E3%81%AE%E9%81%8B%E8%A1%8C%E8%A8%88%E7%94%BB%E3%81%AB%E3%81%A4%E3%81%84/

## Runtime activation checkpoint — 2026-09-25

Provider and scoring activation is complete on candidate branch `r4.2-b32-jp-research-batch01`.

Regression coverage now includes:
- official homepage open state;
- No.2 Ropeway suspended;
- ambiguous / incomplete status HTML;
- official maintenance closure;
- ordinary non-event night;
- valid 2026 Stargazing Service night;
- event-date daytime status rejected as proof of night operation;
- future-year event schedule rejected as unverified;
- October weekday/weekend timetable distinction;
- stale live snapshot rejection;
- static schedule-open snapshot rejected as proof of live operation.

Live-source QA on GitHub Actions successfully parsed the current official homepage with:
- `parse_ok = true`;
- No.1 status recognized;
- No.2 status recognized;
- visible official update timestamp recognized.

Activation QA results:
- Opportunity Adapter: success;
- Taiwan Candidate Weather QA: success;
- Japan Candidate Weather QA: success;
- Browser Smoke: success.

Observed candidate artifact after activation:
- `jp-021-P01` reached 86 with `dedicated_conditions_match` while the official live access snapshot remained fresh.
- The same current-open snapshot stopped unlocking P01 after the six-hour freshness window and fell back to runtime-data-missing behavior.
- Outside the official regular ropeway timetable, access became authoritative `closed`.
- `jp-021-P02` remained access-ineligible on a non-Stargazing date even when astronomy conditions could otherwise be evaluated.

## Remaining maintenance work

1. Monitor the official homepage markup; parser ambiguity must continue to fail closed.
2. Refresh and re-verify the annual Stargazing Service calendar before using dates beyond 2026.
3. Add date-specific early-morning special-service exceptions only from official annual notices; never generalize them into permanent opening hours.
4. Re-run the provider fixture, live parser, candidate-weather and browser gates whenever the provider or access contract changes.
