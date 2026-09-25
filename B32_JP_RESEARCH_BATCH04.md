# ChaseLights R4.2 B32 — Japan Research Migration Batch 04

Date: 2026-09-25 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

## Time-zone contract

- Shooting time, best window, access window and hourly forecast use the Place local timezone.
- Japan uses `Asia/Tokyo` (JST).
- Website Last Updated uses the user's device/browser timezone.

---

## jp-014 — 等等力溪谷 / Todoroki Valley

### Current official state

Setagaya City states:
- the valley park and riverside path reopened on 2026-03-24 after the 2023 fallen-tree closure;
- some paths have no nighttime lighting and visitors should not enter after dark;
- river level can rise rapidly during heavy rain;
- because of congestion/safety, the city currently says photography/shooting applications are not being accepted;
- the valley remains an important natural scenic area with forest, geological layers, spring water and Fudo-no-taki waterfall.

Sources:
- https://www.city.setagaya.lg.jp/02075/9082.html
- https://www.city.setagaya.lg.jp/02059/3482.html

### Migration decision

**KEEP research-pending. Do not enable a photography score yet.**

Reasons:
1. The park has reopened, but current official photography wording needs a more precise distinction between casual visitor snapshots and organized/commercial shooting.
2. Night access should be treated as invalid because the city explicitly warns visitors not to enter after dark.
3. Heavy rain is an access/safety concern, not just a photographic penalty.
4. The current ChaseLights point at Fudo-no-taki should be rechecked against the reopened public route before it is promoted to a Camera Zone.

No legacy fog/sunbeam/long-exposure tag may generate a score automatically.

---

## jp-019 — 濱名湖 / Bentenjima Seaside Park

### Official evidence

Hamamatsu City identifies Bentenjima Seaside Park as a representative Hamanako tourism destination and specifically highlights sunset viewing as a core attraction throughout the year.

Shizuoka Prefecture official tourism further identifies the red Bentenjima symbol tower sunset alignment as a **season-limited composition around one month either side of the winter solstice**.

Sources:
- https://www.city.hamamatsu.shizuoka.jp/kanko/bentenjima-kaihinkouen/saiseibi.html
- https://hellonavi.jp/article/bentenjima-akadorii

### Runtime-migrated Opportunity

**jp-019-P01 — 弁天島海浜公園・濱名湖夕景**
- legacy theme: `sunset`
- Camera Zone: public Bentenjima Seaside Park lakeside area
- anchor: 34.688461, 137.603753
- best time: sunset / twilight, JST
- runtime: directional horizon + visibility
- directional sector: broad west-to-southwest sunset sector
- required:
  - sunset direction usable;
  - water horizon readable;
  - sufficient visibility;
  - low cloud does not fully block the sunset direction.

This Opportunity intentionally does **not** claim that the sun will align with the center of the red tower.

### Pending precise composition

**jp-019-P02 — 紅色鳥居正中夕陽**
- composition-specific;
- official seasonal evidence: approximately one month either side of winter solstice;
- requires exact Camera Zone + subject geometry + date-aware solar alignment;
- must remain pending until exact geometry and seasonal ephemeris contract are implemented.

### Guardrail

A high score for P01 means “good conditions for the Bentenjima/Hamanako sunset landscape,” not “the sun will be centered in the red torii.”

---

## Next candidates

- jp-016 橫濱山下公園: official sources support harbor/Hikawa Maru views and night scenery; exact Opportunity split still required.
- jp-017 金澤兼六園: research seasonal opening/access and garden-specific Outcomes before scoring.
- jp-018 名古屋城: avoid generic architecture scoring until access/light semantics are researched.
- jp-020 橫濱港未來21 / Osanbashi: strong official 24-hour rooftop-deck night-view evidence and likely a high-value next candidate.
