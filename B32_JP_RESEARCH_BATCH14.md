# ChaseLights R4.2 B32 — Japan Research Migration Batch 14

Date: 2026-09-25 (Asia/Taipei)
Development base: `r4.2-b32-jp025-hagi` at `5598b22280f4d616dd73e0278437af20bfa97ea4`

## Scope and evidence

This batch researches `jp-026 出雲大社` as a public-approach architectural photography Place. The shrine's official precinct guide distinguishes the public pine avenue and Haiden from the restricted main-sanctuary gate. The outcome is the visible exterior of the approach and worship hall, not access to the Honden or an inferred special ceremony.

Sources checked on 2026-09-25:

- Shrine precinct route and access boundary: https://izumooyashiro.or.jp/en/precincts
- Official precinct map: https://izumooyashiro.or.jp/en/precinctmap
- Current visiting-hours notice, dated 2026-05-03: https://izumooyashiro.or.jp/archives/news/12552
- Shrine guidance for photography beyond private appreciation: https://izumooyashiro.or.jp/inquiry/contactpress
- Local tourism association's entrance and parking options: https://www.izumo-kankou.gr.jp/13218
- Geotagged area reference near the public approach: https://commons.wikimedia.org/wiki/File:Izumo_grand_shrine_-_2022_oct_2_various.jpeg

## Camera Zone versus Navigation Target

`jp-026-P01` is the public walking area between the pine approach and Haiden exterior. A geotagged reference near `35.401383, 132.686264` locates the general area, with **medium** coordinate confidence. It is not a surveyed camera station or a route endpoint. The existing `35.402083, 132.685556` Place coordinate remains a weather sampling anchor near the shrine, not a road destination; it must never produce Directions.

The official tourist parking guide identifies at least the shrine-managed large parking area and the Seidamari formal entrance as distinct arrival choices. A single mode-independent Directions target would mislead some visitors. `navigation_target.status = multiple_access_routes` therefore suppresses navigation links until the product supports route selection and exact arrival coordinates are separately verified. No Camera Zone point is promoted to a verified Navigation Target.

## Opportunity contract

`jp-026-P01` — 松之參道與拝殿社殿:

- Public, visible daylight during the official 06:00–19:00 JST precinct visiting window.
- Area photography along permitted pedestrian paths; no claim of a required tripod point or access beyond the Yatsuashi Gate.
- `minimum_sufficient_local_scene` is manually assigned: benign low cloud or modest long-distance visibility does not hide a nearby building. Material rain and known access closure block the local-scene result.
- Ceremonies, crowding and restrictions can change conditions on site; the weather feed does not monitor them. No automatically generated ceremony, night illumination or congestion recommendation is added.
- The official press/filming guidance requires advance permission for work beyond private appreciation; the Place Guide must not imply that publication or commercial shooting is pre-approved.

`mountain_view` is used solely as the existing daylight compatibility baseline; it does not describe a mountain subject. No `blue_hour` Opportunity is enabled, because permitted hours alone do not establish a useful illuminated exterior after dusk.

## Result and next checkpoint

Japan researched coverage becomes 26/35, with nine Places remaining. The additive catalog has 26 Places, 34 Opportunities, 34 Condition Variants and 34 profile-viewpoint relations. The next research target is `jp-027 神戶六甲山`.

Before release, run adapter tests, Japan candidate weather QA and browser smoke for the new coverage; assess the original jp-025 Navigation Target checkpoint for production separately. Review the approximate Camera Zone coordinate on site or against stronger mapped evidence before upgrading its confidence or offering navigation to it.
