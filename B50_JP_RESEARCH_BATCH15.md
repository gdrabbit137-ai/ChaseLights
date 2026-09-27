# ChaseLights R4.2 B50 — Japan Research Batch 15 (jp-027 through jp-031)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five Japan production Places into the canonical Opportunity catalog:

- jp-027 神戶六甲山
- jp-028 高野山
- jp-029 伊賀上野城
- jp-030 鳴門海峽漩渦
- jp-031 倉敷美觀地區

The canonical production source is `runtime_catalog_v004_r4_2.json`. This document records research evidence and modeling decisions; it is not a second runtime catalog.

## Evidence boundary

The batch follows `RESEARCH_EVIDENCE_SPEC_R4_2.md`:

- official/place-specific evidence proves the subject exists,
- runtime weather/access data estimates when an admitted subject may work,
- seasonal foregrounds are not treated as present from calendar month alone,
- recurring annual lighting/events are not copied into a new year without a current official notice,
- Naruto whirlpool strength is not approximated with the existing relative sea-level tide module.

## jp-027 神戶六甲山 — 天覽台

Official source:
- KOBE Mt. Rokko official Tenrandai: https://www.rokkosan.com/tenrandai/

Verified facts:
- Tenrandai is an official observation deck at about 737 m.
- The official page directly supports a daytime panorama over Kobe, Osaka Plain and toward Wakayama.
- It directly supports the evening transition and Osaka Bay / urban night view.
- Current published opening hours are 07:10–21:00, daily.

Admitted Opportunities:
- P01 — daytime broad panorama.
- P02 — twilight / Osaka Bay urban night view.

Runtime decision:
- Both use the curated minimum-sufficient visibility contract.
- Long-range visibility is photographically material.
- Spot access is constrained to the official 07:10–21:00 window.
- The existing observation-deck coordinate remains a Camera Zone / precise map pin, not automatically a separately verified road-arrival target.

## jp-028 高野山 — 壇上伽藍 / 蛇腹路

Official sources:
- Kongobu-ji official Danjo Garan guide: https://www.koyasan.or.jp/meguru/
- 2025 official special night lighting notice: https://www.koyasan.or.jp/news/2025/10/08/11214/
- Current 2026 official news index: https://www.koyasan.or.jp/news/2026/

Verified facts:
- Danjo Garan is the central sacred precinct with Konpon Daito, Kondo and historic halls.
- Official notices prove Jabaramichi autumn foliage and special night lighting as real place-specific subjects.
- 2026 official notices also demonstrate temporary viewing restrictions can occur.
- No 2026 Jabaramichi autumn night-lighting date was found at this checkpoint.

Admitted Opportunities:
- P01 — Danjo Garan / Konpon Daito architecture.
- P02 — Jabaramichi autumn foliage.
- P03 — annual special night lighting.

Runtime decision:
- P01 uses minimum-sufficient local-scene scoring: close-range architecture does not require distant visibility.
- P02 stays `module_pending` until a seasonal-foreground state can establish actual foliage state.
- P03 stays `module_pending` until a current-year official event/lighting state exists.
- Prior-year dates must not be copied into 2026.

## jp-029 伊賀上野城

Official sources:
- Iga Ueno Tourism Association — castle: https://www.igaueno.net/?p=89
- Mie Prefecture official tourism — Ueno Park cherry blossoms: https://www.kankomie.or.jp/event/5750

Verified facts:
- The castle has a reconstructed wooden three-story keep.
- The high stone wall is approximately 30 m and is a defining visual feature.
- Mie official tourism explicitly promotes the castle + cherry blossom composition and states about 200 cherry trees in Ueno Park.
- Typical cherry period is described as late March through mid-April, but actual flowering must not be guaranteed from dates alone.

Admitted Opportunities:
- P01 — keep + high stone wall exterior composition.
- P02 — spring cherry blossoms + castle.

Runtime decision:
- P01 uses minimum-sufficient local-scene scoring.
- P02 remains `module_pending` pending actual seasonal-foreground state.
- Castle interior hours (09:00–17:00) are not incorrectly applied to every exterior park composition.

## jp-030 鳴門海峽漩渦

Official sources:
- Uzu-no-Michi official tide/current calendar: https://www.uzunomichi.jp/tide-calendar/
- Naruto City Uzushio Tourism Association: https://www.naruto-kankou.jp/uzu/

Verified facts:
- Whirlpool visibility is not continuous.
- The official table labels the listed “high/low” times as the fastest northbound/southbound current times.
- Official optimum windows are:
  - spring current: ±2 hours,
  - intermediate current: ±1.5 hours,
  - neap current: ±1 hour.
- Official guidance notes stronger whirlpools are more likely around spring tides and highlights spring/autumn periods.

Admitted Opportunity:
- P01 — Uzu-no-Michi bridge-walkway view of Naruto whirlpools.

Runtime decision:
- New safe status: `data_insufficient_tidal_current_extremum`.
- The current `tide_state` module models relative sea-level percentile/trend; that is not equivalent to fastest current.
- Do not map “low tide” exposure scoring onto Naruto whirlpool strength.
- A future tidal-current/extremum provider must ingest or reproduce the official current-timing semantics before high-confidence runtime scoring is enabled.

## jp-031 倉敷美觀地區

Official sources:
- Kurashiki official standard guide: https://www.kurashiki-tabi.jp/standard/kurashiki-bikan-historical-quarter/
- Kurashiki official night landscape lighting: https://www.kurashiki-tabi.jp/see/see-201/

Verified facts:
- The official guide directly supports the Kurashiki River, white-walled storehouses, willow trees and historic streetscape as the representative daytime subject.
- The official night page states the white buildings are illuminated and reflected on the river.
- Published daily lighting windows:
  - Apr–Sep: sunset–22:00,
  - Oct–Mar: sunset–21:00.

Admitted Opportunities:
- P01 — daytime white walls / willow / river historic streetscape.
- P02 — official night lighting + river reflection.

Runtime decision:
- P01 uses minimum-sufficient local-scene scoring.
- P02 remains `module_pending` under `needs_lighting_state_module` rather than assuming lighting is active solely from generic city-night scoring.
- Reflection existence is evidence-verified; actual water-surface calmness remains a runtime quality variable.

## Catalog delta

Expected canonical delta for this batch:
- +5 curated Japan Places
- +10 Opportunities
- +10 Condition Variants
- +10 viewpoint relations

Expected canonical totals after the batch:
- 114 curated Places
- 261 Opportunities
- 271 Condition Variants
- 266 viewpoint relations

Japan migrated range becomes jp-001 through jp-031:
- 31 curated Japan Places
- 44 Japan Opportunities
- 44 Japan Condition Variants
- 44 Japan viewpoint relations

Remaining Japan research queue after this batch:
- jp-032 福岡城跡
- jp-033 唐津城
- jp-034 長崎哥拉巴園
- jp-035 福岡塔

## QA changes in this batch

`.github/workflows/b32_jp_candidate_weather.yml` is modernized because B45 retired regional detail files but the old B32 workflow still attempted to read `jp_weather_details.json`.

The Japan QA now:
- triggers on pull requests to main for current canonical/runtime inputs,
- validates `jp_weather.json`,
- validates all 35 per-Place Japan detail shards,
- asserts the retired regional detail file does not reappear,
- verifies researched IDs jp-001 through jp-031,
- keeps jp-032 through jp-035 explicitly research-pending.
