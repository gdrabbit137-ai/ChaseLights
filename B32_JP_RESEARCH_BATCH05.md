# ChaseLights R4.2 B32 — Japan Research Migration Batch 05

Date: 2026-09-25 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

Research-only start. Runtime enablement waits until the prior jp-019 gates are green.

## jp-020 — 橫濱港未來21 / Minato Mirai from Osanbashi

### Place / Camera Zone correction

The current ChaseLights Place represents Minato Mirai, but its intended photography position is Osanbashi.

Official Yokohama City:
- Osanbashi rooftop plaza ("Whale's Back") is open 24 hours;
- public entry is free;
- the rooftop provides 360-degree harbor panoramas including Minato Mirai and Yokohama Bay Bridge.

Official Yokohama tourism:
- the rooftop is explicitly promoted as a panoramic viewpoint;
- the Minato Mirai cityscape and harbor night lights are a core night-view Outcome.

Precise scenic-viewpoint evidence:
- OSM scenic viewpoint node `OSANBASHI VIEWPOINT`: 35.45099, 139.64670.
- This is preferable to treating the broad terminal POI or the Minato Mirai district center as the camera position.

Sources:
- https://www.city.yokohama.lg.jp/kanko-bunka/minato/yokohamako/gaiyo/terminalhome.html
- https://www.city.yokohama.lg.jp/kanko-bunka/minato/kyakusen/terminal.html
- https://www.welcome.city.yokohama.jp/spot/details.php?bbid=179
- OSM scenic viewpoint evidence surfaced via https://mapcarta.com/N4895092862

### Candidate Opportunity

**jp-020-P01 — 大棧橋屋頂・港未來城市夜景**
- legacy theme: `city_night`
- Camera Zone: west-side Osanbashi rooftop / OSANBASHI VIEWPOINT
- anchor: 35.45099, 139.64670
- best time: blue hour through night, JST
- access:
  - rooftop itself is officially open 24 hours;
  - do not bind the Opportunity to the indoor terminal 09:00–21:30 hours.
- required conditions:
  - Minato Mirai skyline and harbor readable;
  - usable visibility;
  - low cloud/fog not materially obscuring skyline/harbor.
- stable semantic support:
  - official tourism explicitly supports night-view use; this is not an inferred "city lights" claim.
- runtime direction:
  - minimum-sufficient visibility paired with `city_night` temporal baseline is likely sufficient for the base night-view Outcome.
- no managed-event-lighting assumption is needed for the ordinary city-night panorama.

### Optional separate Opportunity

**jp-020-P02 — 大棧橋・Bay Bridge 港景**
- use the east-side rooftop viewpoint if migrated;
- keep separate from Minato Mirai because the subject direction and composition differ.

### Guardrail

A score for P01 means the ordinary Minato Mirai city/harbor night panorama is photographically usable. It does not guarantee special illuminations, fireworks, cruise-ship presence or event lighting.
