# ChaseLights R4.2 B32 — Japan Research Migration Batch 03

Date: 2026-09-25 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

Research-only start. Do not enable scores from legacy Scene/Theme tags.

## Time-zone contract

- Opportunity shooting times use the Place local timezone.
- Japan Places use `Asia/Tokyo` (JST).
- Website Last Updated uses the user's browser/device timezone.

---

## jp-011 — 東京鐵塔 / Tokyo Tower

Current coordinate:
- `35.658656, 139.745364`
- this is the Tower POI / subject coordinate, not a verified external Camera Zone.

### Official evidence

GO TOKYO identifies Tokyo Tower as a major photo subject and explicitly states that:
- Minato Ward Shiba Park is a strong location for photographing Tokyo Tower in the background;
- nearby Zojoji Temple can produce an iconic composition with Tokyo Tower behind it;
- Tokyo Tower illumination and surrounding parks are core visual strengths.

Sources:
- https://www.gotokyo.org/en/destinations/southern-tokyo/tokyo-tower-and-around/index.html
- https://www.gotokyo.org/en/spot/423/index.html

### Candidate Opportunities

**jp-011-P01 — 芝公園・東京鐵塔城市地標**
- likely legacy theme: `city_night` or `blue_hour`.
- subject: Tokyo Tower.
- Camera Zone: Minato Ward Shiba Park / lawn-area family.
- best time: blue hour into night (JST).
- required:
  - tower visually unobstructed from selected Camera Zone;
  - usable visibility;
  - illumination/time state appropriate to intended Outcome.
- status:
  - research-ready concept;
  - **do not enable** until exact public Camera Zone is pinned.

**jp-011-P02 — 增上寺＋東京鐵塔**
- separate composition-specific Opportunity.
- requires a verified temple/public approach Camera Zone and exact subject geometry.
- do not auto-merge with P01.

### Migration decision

Keep the Tokyo Tower POI for navigation/subject identity only. Do not use the tower's own coordinate as the photography Camera Zone.

---

## jp-012 — 鎌倉大佛 / Great Buddha of Kamakura, Kotoku-in

Current coordinate:
- `35.316719, 139.535631`
- corresponds to Kotoku-in / Great Buddha POI.

### Official evidence

Kotoku-in official visitor information:
- April–September: 08:00–17:30;
- October–March: 08:00–17:00;
- last entry 15 minutes before closing;
- personal photography on the grounds is allowed;
- commercial photography requires permission;
- drone use is prohibited;
- photography inside the Buddha statue is prohibited.

Sources:
- https://kotoku-in.jp/en/
- https://kotoku-in.jp/en-site/faq

### Candidate Opportunity

**jp-012-P01 — 高德院境內鎌倉大佛**
- theme should not be forced into `blue_hour` / `city_night` just because those tags exist in legacy data.
- best time: official opening hours, daylight (JST).
- hard gates:
  - temple open;
  - visitor photography permitted;
  - public visitor area only.
- required:
  - precipitation/light state usable enough for outdoor architecture/sculpture photography.
- access:
  - seasonal opening-hour contract can be machine-readable.
- runtime limitation:
  - current ChaseLights modules do not yet model architecture/sculpture light quality well enough to justify a high-confidence photography score.

### Migration decision

Research can be migrated before scoring, but keep module-pending until an appropriate simple architecture/outdoor-light contract exists. Do not use generic city-night scoring.

---

## jp-013 — 諏訪湖 / Lake Suwa from Tateishi Park

Current coordinate:
- `36.053326, 138.122711`
- current map query: 立石公園 諏訪
- already represents the intended elevated viewpoint rather than the lake center.

### Official evidence

Suwa City official Tateishi Park page:
- Tateishi Park overlooks Lake Suwa and the surrounding city;
- on clear days the Northern Alps may be visible;
- sunset and night views are specifically highlighted;
- the park is recognized as a major sunset/night-view viewpoint;
- current city notices warn of routine congestion, especially after 16:00, and publish temporary parking restrictions for specific dates.

Suwa Tourism Association further describes:
- full Lake Suwa + city + surrounding mountain panorama;
- twilight/sunset and night city lights as core visual Outcomes;
- seasonal variation through the year.

Sources:
- https://www.city.suwa.lg.jp/site/tateishipark/
- https://www.suwakanko.jp/tateishipark/
- https://www.suwakanko.jp/en/suwa-area-guide/

### Candidate Opportunities

**jp-013-P01 — 立石公園・諏訪湖夕景**
- legacy theme: `sunset`.
- Camera Zone: Tateishi Park observation terrace/viewpoint.
- best time: sunset / twilight (JST).
- required:
  - western/sunset light window valid;
  - lake/city panorama visible;
  - low cloud/fog not fully obscuring the basin.
- boosters:
  - usable mid/high cloud;
  - clean visibility.
- runtime direction:
  - directional horizon + visibility.
- coordinate:
  - current Tateishi Park coordinate is suitable as initial anchor, but exact observation-terrace pin should be confirmed before runtime enablement.

**jp-013-P02 — 立石公園・諏訪湖城市夜景**
- legacy theme: `city_night`.
- best time: blue hour into night (JST).
- required:
  - legal park access;
  - lake/city basin visibility;
  - low cloud/fog not fully obscuring the view.
- congestion:
  - do not convert ordinary crowding/parking difficulty into a weather score.
  - temporary parking restrictions are access/transport information, not a photography-condition penalty.

### Migration decision

Among jp-011–013, jp-013 is the strongest next runtime candidate because:
1. the Place already points to the actual elevated photography area;
2. official sources explicitly identify sunset and night-view Outcomes;
3. weather dependencies map cleanly to existing modules.

---

## Batch03 implementation priority

1. jp-013 Tateishi Park / Lake Suwa — verify exact observation terrace coordinate, then implement sunset first.
2. jp-012 Kotoku-in — encode seasonal access hours; keep score module-pending until architecture-light semantics exist.
3. jp-011 Tokyo Tower — pin a real external Camera Zone before any score is enabled.

---

## Implementation status — 2026-09-25

### Runtime migrated

**jp-013-P01 — 立石公園・諏訪湖夕景**
- Camera Zone: Tateishi Park observation area
- anchor: 36.053326, 138.122711
- elevation: 934 m
- runtime: directional horizon + visibility
- sunset sector: west-facing
- all shooting times: JST
- release gates: Adapter PASS, Japan Candidate PASS, Taiwan Candidate PASS, Browser Smoke PASS

### Research complete, scoring not enabled

**jp-011 東京鐵塔**
- Tokyo Tower POI is a subject coordinate, not a camera position.
- External Shiba Park / Zojoji Camera Zone must be pinned before scoring.

**jp-012 鎌倉大佛**
- official seasonal visitor hours and personal-photography rules are researched;
- current ChaseLights architecture/sculpture light semantics are not strong enough for a trustworthy score;
- do not convert this into a generic 0–64 module-pending photography score merely because research text exists.

