# B50 Japan Research Batch 15 — jp-027 through jp-031

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates five production Japan Places into the canonical R4.2 Opportunity catalog:

- jp-027 神戶六甲山・天覽台
- jp-028 高野山・壇上伽藍
- jp-029 伊賀上野城
- jp-030 鳴門海峽・渦之道
- jp-031 倉敷美觀地區・倉敷川

The batch adds 9 researched Opportunities. jp-032 through jp-035 remain research-pending.

## jp-027 — Rokko Tenrandai

Official Mt. Rokko guidance establishes Tenrandai as a 737 m observation deck with:
- daytime panorama from Kobe across Osaka Plain toward Wakayama,
- evening transition,
- Osaka Bay urban night view,
- current published opening 07:10–21:00.

Runtime:
- daytime panorama: researched minimum-sufficient visibility contract,
- city night: researched minimum-sufficient visibility contract,
- the facility window remains an independent access gate.

Source:
- https://www.rokkosan.com/tenrandai/

## jp-028 — Koyasan Danjo Garan

Official Wakayama / Kongobuji sources establish:
- Danjo Garan and Konpon Daito as the architectural subject,
- autumn foliage with the sacred precinct,
- Jabaramichi in Danjo Garan as a popular foliage scene.

Runtime:
- architecture: close-range minimum-sufficient local scene,
- foliage: seasonal_foreground pending.

A month is not proof of foliage condition. Historic or prior-year night-lighting notices are not promoted to a permanent annual rule.

Sources:
- https://www.wakayama-kanko.or.jp/spots/detail_481.html
- https://www.koyasan.or.jp/meguru/
- https://www.wakayama-kanko.or.jp/events/detail_3936.html

## jp-029 — Iga Ueno Castle

Mie official tourism establishes:
- the white three-storey castle,
- approximately 30 m inner-moat stone walls,
- castle + cherry blossom seasonal composition,
- official tower hours 09:00–17:00, last entry 16:45.

Runtime:
- castle / high-stone-wall exterior: minimum-sufficient local scene,
- cherry blossom: seasonal_foreground pending.

Actual blossom state is required; late-March / April timing is only a research clue.

Sources:
- https://www.kankomie.or.jp/spot/3156
- https://www.kankomie.or.jp/event/5750

## jp-030 — Naruto whirlpool / Uzu-no-Michi

Official Naruto guidance explicitly states that whirlpools are not visible 24/7.
The official viewing contract is tied to local tide extrema:
- spring tide: roughly ±2 h around high / low tide,
- middle tide: roughly ±1.5 h,
- neap tide: roughly ±1 h,
- Naruto side particularly recommends the low-tide period.

Existing ChaseLights tide_state is a relative sea-level percentile/trend model for shoreline exposure, tidal access and reflection subjects. It does not estimate Naruto tidal-current velocity or whirlpool strength.

Therefore this batch adds a new explicit but unimplemented dependency:
- tidal_current_extremum,
- plus authoritative Uzu-no-Michi access state.

jp-030-P01 remains module_pending until those sources are implemented. Generic tide percentile must never be substituted.

Sources:
- https://www.naruto-kankou.jp/uzu/
- https://www.uzunomichi.jp/tide-calendar/

## jp-031 — Kurashiki Bikan Historical Quarter

Official Kurashiki tourism establishes:
- preserved white-wall / namako-wall townscape along Kurashiki River,
- night landscape lighting,
- illuminated white-wall buildings reflected on Kurashiki River,
- standard lighting hours:
  - Apr–Sep: sunset–22:00,
  - Oct–Mar: sunset–21:00.

Runtime:
- daytime historic streetscape: minimum-sufficient local scene,
- night illumination + reflection: managed_lighting_state + water_surface_state.

water_surface_state is implemented, but managed_lighting_state is not, so the night reflection Opportunity remains module_pending.

Sources:
- https://www.kurashiki-tabi.jp/rm_see/rm-see98/
- https://www.kurashiki-tabi.jp/see/see-201/

## Evidence admission

Explicit evidence-registry entries are added for:
- jp-028-P02 — autumn foliage,
- jp-029-P02 — cherry blossom,
- jp-031-P02 — managed night reflection.

No fog / mist or sunbeam Opportunity is admitted for Koyasan from legacy hints. Those legacy theme hints are removed from the Place override because the batch research does not prove those photographic subjects.

## Canonical counts

After this batch:
- total curated Places: 114
- total Opportunities: 260
- Condition Variants: 270
- viewpoint relations: 265

Japan:
- curated Places: 31
- Opportunities: 43
- Condition Variants: 43
- viewpoint relations: 43
- pending Places: jp-032 through jp-035

## CI / migration note

B32 Japan Candidate Weather QA is updated in the same batch to:
- run on pull requests to main,
- validate the current canonical catalog rather than historical batch fragments,
- use the B45 shard-only detail architecture,
- assert the regional jp_weather_details.json file remains retired,
- validate all 35 per-Place detail shards.
