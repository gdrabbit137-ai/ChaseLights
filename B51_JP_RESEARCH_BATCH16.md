# ChaseLights R4.2 B51 — Japan Research Batch 16 (jp-032 through jp-035)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch completes the Japan production Place migration into the canonical Opportunity catalog:

- jp-032 福岡城跡
- jp-033 唐津城
- jp-034 長崎哥拉巴園
- jp-035 福岡塔

After this batch all 35 Japan production Place cards have individually researched Opportunities. “Research complete” does not mean every Opportunity is runtime-ready: seasonal foregrounds, managed lighting, annual night events and facility access remain explicit dependencies where applicable.

## Evidence boundary

The batch follows the existing R4.2 contract:

- official/place-specific sources prove the photographic subject exists,
- runtime data determines whether the admitted subject is currently viable,
- calendar month alone never proves blossoms or foliage state,
- facility opening and public exterior access are separate contracts,
- current-year event/night-opening notices are not generalized into permanent annual access,
- a currently closed Camera Zone is not offered as navigation or a valid viewpoint.

## jp-032 福岡城跡

Official sources:

- Fukuoka Castle / Korokan official walking guide:
  https://fukuokajyo.com/walking/
- Official Tenshudai access-restriction notice:
  https://fukuokajyo.com/24704/

Verified facts:

- Shimonohashi Gate, Tamon Yagura and castle stonework are official castle-ruin subjects.
- The official seasonal guide directly documents plum, cherry blossoms, wisteria and autumn foliage.
- Tenshudai is closed for excavation from 2026-05-26 through the end of December 2026 (planned).

Admitted Opportunities:

- P01 — Tamon Yagura / Shimonohashi Gate / stone-wall castle composition.
- P02 — seasonal plum, cherry, wisteria and autumn foliage in the castle grounds.

Runtime / navigation decision:

- P01 uses minimum-sufficient local-scene scoring.
- P02 remains seasonal-foreground module pending.
- The legacy Tenshudai coordinate is not used as the B51 Camera Zone or exact Directions target while closure is active.
- Navigation remains needs-review until a practical public arrival / parking anchor is separately verified.

## jp-033 唐津城

Official sources:

- Karatsu Tourism Association — Karatsu Castle:
  https://www.karatsu-kankou.jp/spots/detail/181/
- Karatsu Tourism Association — history guide:
  https://www.karatsu-kankou.jp/guide/history/
- Official flower route:
  https://www.karatsu-kankou.jp/sp/feature/hanameguri/course02

Verified facts:

- Maizuru Park / castle exterior is separately accessible from the keep interior.
- Official material lists Maizuru Park roughly 05:00–22:00.
- Castle keep is currently 09:00–17:00, last entry 16:40, with possible seasonal changes.
- The keep panorama directly includes Karatsu Bay and Niji-no-Matsubara.
- Official tourism identifies cherry blossoms and old wisteria as major seasonal subjects.

Admitted Opportunities:

- P01 — castle exterior / Maizuru Park.
- P02 — fifth-floor panorama over Karatsu Bay and Niji-no-Matsubara.
- P03 — cherry blossom and wisteria compositions.

Runtime decision:

- P01 uses minimum-sufficient local-scene scoring.
- P02 requires facility access + visibility and remains module pending until authoritative facility state is connected.
- P03 remains seasonal-foreground pending.
- Park opening is never treated as proof that the paid keep interior is open.

## jp-034 長崎哥拉巴園

Official sources:

- Glover Garden 2026 opening schedule:
  https://glover-garden.jp/event-and-news/26532/
- Former Glover House:
  https://glover-garden.jp/about/glover-house/
- 2026 Lantern Night:
  https://glover-garden.jp/event-and-news/26562/
- Official night-view gallery:
  https://glover-garden.jp/gallery/category/night-view/

Verified facts:

- Former Glover House and the Western-style historic buildings are explicit heritage subjects.
- 2026 opening hours vary by date range; multiple periods have extended night opening.
- Lantern Night 2026 officially includes about 300 lanterns, illuminated Western houses and Nagasaki night scenery.
- The official gallery directly documents night views from the garden / Former Mitsubishi No.2 Dock House.

Admitted Opportunities:

- P01 — Former Glover House / historic Western architecture.
- P02 — 2026 Lantern Night / illuminated Western houses / Nagasaki night view.

Runtime decision:

- P01 uses minimum-sufficient local-scene scoring.
- P02 requires event state + dynamic access and remains module pending.
- The Place-level access baseline uses conservative 08:00–18:00; extended night access is not generalized to every date.
- Private events, weather and current official notices can change opening times.

## jp-035 福岡塔

Official sources:

- Fukuoka Tower observation rooms:
  https://www.fukuokatower.co.jp/viewroom/
- Current hours / fees:
  https://www.fukuokatower.co.jp/charge/
- Official night-view / illumination page:
  https://www.fukuokatower.co.jp/viewroom/night.php

Verified facts:

- The top observation floor is about 123 m and provides a 360-degree view over Fukuoka city and Hakata Bay.
- Current official hours are 09:30–22:00 with last admission at 21:30.
- The official night page promotes the sunset-to-night transition.
- Exterior tower illumination operates from sunset to 23:00 and changes seasonally.

Admitted Opportunities:

- P01 — 123 m observation-room city / Hakata Bay panorama.
- P02 — sunset transition to city / bay night view.
- P03 — exterior seasonal tower illumination.

Runtime decision:

- P01/P02 use minimum-sufficient visibility.
- P03 remains managed-lighting-state pending.
- 21:30 is used as the conservative entry cutoff for tower-interior Opportunities.

## Catalog delta

B51 adds:

- +4 curated Japan Places
- +10 Opportunities
- +15 Condition Variants
- +11 viewpoint relations

Expected canonical totals:

- 118 curated Places
- 270 Opportunities
- 285 Condition Variants
- 276 viewpoint relations

Japan totals:

- 35 curated Places
- 53 Opportunities
- 58 Condition Variants
- 54 viewpoint relations
- 0 research-pending production Places

## QA contract

B51 updates:

- Adapter regression coverage for all new Opportunity IDs and runtime policies.
- Dynamic-access profile count from 50 to 52.
- Japan Candidate Weather researched range from jp-001..031 to jp-001..035.
- Japan pending count from 4 to 0.
- Browser Smoke researched-card count from 31 to 35 and pending Japan cards from 4 to 0.

A Place can be fully researched while some of its Opportunities remain module pending. That distinction must remain visible and must not be replaced by legacy Theme scoring.
