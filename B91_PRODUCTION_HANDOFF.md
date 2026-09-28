# ChaseLights R4.2 B91 Production / Maintenance Handoff

Date: 2026-09-28 (Asia/Taipei)

## Start here

This file supersedes `B89_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before changing production:

1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md`,
4. read B83–B85 before changing Qixingtan P03/P04,
5. read B87–B88 before changing Qingshui mist,
6. read B89 before changing field-validation replay semantics,
7. read `B91_DENALI_MOUNTAIN_VISTA_ACCESS.md` before changing Denali / Mountain Vista access,
8. keep weather quality, subject existence, access, entitlement, transport, and safety as separate contracts.

## Verified production checkpoint

Repository: `gdrabbit137-ai/ChaseLights`

Public site: <https://chaselights.app/>

Recent provider releases:

- B90 Johnston Ridge / SR 504 merge: `ad9ef7e8319344121160536ee40eaa42f520394f`
- B91 Denali Mountain Vista merge: `a84a45e9cd8ab853199e6ab4075462cf7a19ba85`
- B91 generated weather: `23d7d13422b323586886c1a354483557a6503fb1`

B91 PR #157 validation:

- Opportunity Adapter — PASS
- Evidence Audit — PASS
- Taiwan Candidate Weather — PASS
- Japan Candidate Weather — PASS
- US Candidate Weather — PASS
- Browser Smoke — PASS

Post-B91 main validation:

- Opportunity Adapter — PASS
- Evidence Audit — PASS
- code-merge Pages deployment — PASS
- production weather refresh — PASS
- generated-weather Pages deployment — pending only if this handoff is read before that deployment finishes; verify the latest Pages run on `23d7d13422b3...`

## Canonical catalog checkpoint

No Place / Opportunity / Variant / Viewpoint count changed in B90 or B91.

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 220 | 230 | 225 |
| Japan | 35 | 53 | 58 | 54 |
| United States | 70 | 111 | 111 | 111 |
| **Total** | **188** | **384** | **399** | **390** |

Runtime-policy totals after B91:

- `module_pending`: **119**
- `preview_module_available`: **125**
- `minimum_sufficient_available`: **134**
- `prototype_pending_certification`: **2**
- `hold`: **2**
- `data_insufficient`: **2**

B90 moved one Opportunity from pending to preview.
B91 moved two more.

## B90 — Johnston Ridge / SR 504 access

B90 connects `us-017-P01` to the official WSDOT SR 504 / Johnston Ridge project status.

Key behavior:

- explicit long-running closure can prove CLOSED across the forecast horizon using schedule freshness,
- OPEN requires explicit present-tense reopening language,
- ambiguous provider content fails closed,
- favorable weather never proves Johnston Ridge access.

B91 also fixes CI impact routing so future edits to `johnston_ridge_access.py` are explicitly classified as US weather changes.

## B91 — Denali Mountain Vista current road access

Affected Opportunities:

- `us-041-P01` — Mountain Vista・Denali／Alaska Range遠景
- `us-041-P02` — Mountain Vista・Denali極光／夜空

Authoritative provider:

- U.S. National Park Service
- Denali Current Conditions
- https://www.nps.gov/dena/planyourvisit/conditions.htm

NPS states that the Current Conditions page supersedes other trip-planning information.

### Parsing rule

Mountain Vista is near Mile 13.

The provider returns OPEN only from explicit current road-open language that reaches or passes Mountain Vista, such as:

- Mountain Vista / Mile 13,
- Savage River / Mile 15,
- Teklanika / Mile 30.

The provider returns CLOSED when normal vehicle access is explicitly closed at/before Park Headquarters / Mile 3.

A closure farther west, such as Pretty Rocks / Mile 43, does not by itself close Mountain Vista.

Contradictory, missing, unavailable, or unparsable state => UNKNOWN.

### Freshness

Both OPEN and CLOSED use `freshness_mode = live`.

The existing `road_viewpoint_status` six-hour freshness window applies.

This means:

- current access can unlock near-term weather rows,
- current access is not extrapolated across the multi-day forecast,
- stale future rows fail closed until the next production/provider refresh.

### Dependency effect

`us-041-P01`:

- dynamic_access — ready
- visibility — ready
- runtime policy => `preview_module_available`

`us-041-P02`:

- aurora_state — already ready from B79
- dynamic_access — ready from B91
- runtime policy => `preview_module_available`

A closed/unknown/stale road state still vetoes an otherwise-positive aurora signal.

## Verified live B91 production behavior

The B91 production weather refresh fetched the NPS Current Conditions source successfully and generated:

### 2026-09-28 / Mountain Vista P01

- `access_open = true`
- runtime eligible = true
- score around high-60s at the selected daylight window
- visibility around 84 km in that generated forecast
- current winner: Mountain Vista・Denali／Alaska Range遠景

The score is not an access score; it remains the photographic weather score after the separate access gate has passed.

### 2026-09-28 / Mountain Vista P02

- runtime policy = preview
- current access gate passed
- aurora Opportunity can now be evaluated by the B79 local OVATION + darkness + cloud contract instead of being permanently blocked by missing access.

Future forecast dates outside the live access freshness horizon may correctly show no viable Opportunity until a fresher access snapshot exists.

## Current NPS source interpretation at B91 release

At release time the NPS Current Conditions page stated that, weather permitting, personal vehicles could drive to Teklanika / Mile 30.

That is sufficient to reach Mountain Vista / Mile 13.

The same source warns that the road may close back to Mountain Vista or Park Headquarters because conditions can change quickly. B91 therefore deliberately keeps the result short-lived rather than treating the seasonal statement as a multi-day access schedule.

## Runtime/access rules reinforced by B90–B91

- Favorable photography weather never proves access.
- Favorable aurora never proves access.
- A provider must be profile-specific or explicitly scoped; do not build one generic OPEN switch for unrelated Places.
- UNKNOWN is never OPEN.
- Static annual schedules do not prove a live road/facility state when rapid closures are possible.
- A closure beyond the Camera Zone is not automatically a closure of the Camera Zone.
- Access freshness must match how quickly the source state can change.
- Entitlement / booking remains separate from public open/closed state.
- A weather coordinate remains different from a navigation or arrival point.

## CI / provider plumbing checkpoint

Runtime provider files now include:

- `shinhotaka_access.py`
- `yahiko_access.py`
- `johnston_ridge_access.py`
- `denali_access.py`

`ci_weather_impact.py` explicitly maps:

- Shinhotaka / Yahiko => Japan
- Johnston Ridge / Denali => United States

B91 adds Denali provider paths to:

- Adapter CI
- US Candidate Weather
- Browser Smoke
- production weather refresh

Provider changes must continue to fail safe when fetch or parsing fails.

## Field-validation checkpoint

B86/B89 remain unchanged:

- canonical Qixingtan case: `FV-TW-036-20260928-1300-01`
- real user photograph is not stored in the repository,
- structured field observation is separated from Place-specific admission evidence,
- replay fixture is explicitly synthetic minimum reproduction,
- P04 remains the strong mountain-seascape outcome,
- P03 remains a lower-confidence cloud-band outcome when the grid does not directly resolve the cloud.

Do not retune B85 again from the same single positive case.

## Qingshui checkpoint

B87/B88 remain the production protection for `tw-034-P03`:

- poor cliff readability can cap a mist candidate,
- generic theme scoring cannot restore an 80+ recommendation,
- current 2.5 km planning guard is not a claimed exact cliff distance.

## Next-work queue

### 1. Continue authoritative public-road access providers

Recommended next candidates:

1. `us-038-P01` — Newfound Gap / US 441 current NPS road closure state
2. `us-046-P01/P02` — Hatcher Pass current road / parking access, including the aurora Opportunity
3. `us-056-P01/P02` and `us-057-P01/P02` — Dalton Highway / Alaska 511 or other authoritative current-road contract if a reliable machine-readable source can be built

Prefer providers where otherwise-good weather can materially mislead a user about reachability.

### 2. Managed transport / facilities

High-value blocked cases include:

- Alyeska Aerial Tram,
- Glacier Bay tour boat,
- Portage Glacier cruise,
- Goldbelt Tram.

Keep public operating status separate from ticket/seat entitlement.

### 3. Taiwan dynamic access

Continue only where official current status can be checked reliably:

- mountain road/trail status,
- permit + closure state,
- tide-path access windows,
- weather-control attractions.

### 4. Event-state and managed-lighting providers

Continue the B80 backlog:

- current event/cancellation state,
- managed lighting operation,
- attraction-specific current state.

Static recurring schedules can be context but must not prove today's operation if cancellation is possible.

### 5. Payload / compatibility cleanup

Continue conservatively:

- detail-shard payload audit,
- staged `tag_scores` producer cleanup only after downstream compatibility check,
- favorites legacy retirement only after its observation window.

## Release gates

For dynamic-access provider changes:

- authoritative Place/profile-specific source,
- missing/stale/ambiguous/unparsable => fail closed,
- access does not override weather/safety,
- relevant runtime dependency inventory stays exact,
- Adapter PASS,
- Evidence Audit when catalog/evidence semantics change,
- relevant Candidate Weather PASS,
- Browser Smoke PASS,
- production weather refresh PASS,
- final generated-weather Pages deployment PASS.

For field-validation and Qixingtan/Qingshui changes, retain all B89/B88 release gates.
