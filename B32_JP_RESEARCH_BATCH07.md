# ChaseLights R4.2 B32 — Japan Research Migration Batch 07

Date: 2026-09-25 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

Scope:
- jp-014 等等力溪谷 / Todoroki Valley — **do not enable yet**
- jp-015 東京皇居 legacy Place — **redefine as 皇居外苑二重橋 / Nijubashi, Kokyo Gaien**

## jp-014 — 等等力溪谷 / Todoroki Valley

### Current official status

Setagaya City states:
- the riverside path reopened on 2026-03-24 after the long closure caused by hazardous trees;
- visitors should not enter after dark because sections lack night lighting;
- the path is narrow and may be crowded;
- the city currently states that photography/shooting is not being accepted in Todoroki Valley Park in order to protect visitor safety;
- heavy rain can rapidly raise the river level.

Source:
- https://www.city.setagaya.lg.jp/02075/9082.html

### Migration decision

**Remain research_pending / no photography score.**

Reason:
- reopening alone does not justify an active photography recommendation while the current official page explicitly restricts/does not accept shooting;
- do not infer that casual landscape photography is allowed from older pre-closure photo evidence;
- a future migration requires a clearer current policy that supports the intended personal-photography use case.

Do not retire the Place yet because the valley itself remains a meaningful scenic location and the restriction may change.

---

## jp-015 — 皇居外苑二重橋 / Nijubashi, Kokyo Gaien

### Product correction

The legacy name `東京皇居` is too broad and can incorrectly imply photography inside controlled Imperial Palace visit areas.

Keep the stable ID `jp-015`, but product display should become:
- zh-TW: 皇居外苑二重橋
- en: Nijubashi, Kokyo Gaien
- ja: 皇居外苑 二重橋
- local: 二重橋

This Opportunity applies only to the public Kokyo Gaien / Imperial Palace Outer Garden viewpoint, not palace interiors or guided-tour areas.

### Official evidence

National Gardens Association / Kokyo Gaien official material:
- describes Nijubashi as the most popular spot in the Imperial Palace Front Plaza;
- official photography article explicitly recommends photographing Nijubashi and Fushimi-yagura from the Uchibori-dori sidewalk through the black pines;
- official walking guidance identifies the Imperial Palace Front Plaza as a view spot and explicitly tells visitors to take commemorative photos at Nijubashi;
- the outer garden is a public Kokyo Gaien visitor area and is distinct from the controlled palace-tour photography rules.

Sources:
- https://fng.or.jp/koukyo/2017/08/22/post_279/
- https://fng.or.jp/koukyo/place/historical/ruins-gaien/
- https://fng.or.jp/koukyo/2016/07/28/post_197/
- https://fng.or.jp/koukyo/access/

Coordinate cross-check:
- existing camera point `35.678475, 139.754897` corresponds to an actual photographed Nijubashi-moat viewpoint and is suitable as the Camera Zone anchor.

### Candidate Opportunity

**jp-015-P01 — 皇居外苑・二重橋與伏見櫓景觀**
- mode: area_opportunity
- baseline: visible-light landscape / architecture
- Camera Zone: Uchibori-dori sidewalk / Imperial Palace Front Plaza side that frames Nijubashi and Fushimi-yagura
- best_time: daylight (JST)
- required conditions:
  - Nijubashi / Fushimi-yagura readable;
  - adequate visibility;
  - no severe fog or precipitation obscuring the architecture.
- boosters:
  - clean air;
  - seasonal black-pine / foreground context.
- penalties:
  - heavy rain;
  - dense fog / low visibility.
- do not inherit the guided Palace-tour `No Photography / No Tripods` rule, because this Opportunity is outside in Kokyo Gaien and backed by official photography guidance.
- do not claim access to bridge interiors, palace grounds, or restricted gates.

### Runtime decision

Eligible for minimum-sufficient visibility scoring after the display-name and Camera Zone correction.


## Implementation status

### jp-014 等等力溪谷
- **Not migrated.**
- Remains `research_pending` with no photography score.
- Re-review only if current official shooting restrictions change.

### jp-015 皇居外苑二重橋
- **Runtime-migrated on the B32 candidate branch.**
- Stable ID retained as `jp-015`.
- Product name corrected from the overly broad legacy `東京皇居` to `皇居外苑二重橋`.
- Curated Opportunity: `jp-015-P01 皇居外苑・二重橋與伏見櫓景觀`.
- Camera Zone: public Kokyo Gaien / Imperial Palace Front Plaza side at approximately `35.678475, 139.754897`.
- Runtime policy: minimum-sufficient visibility.
- Japan Candidate QA: PASS after migration.
- Adapter CI: PASS after migration.
- Browser Smoke / Taiwan regression: pending at the time of this update.

Japan researched migration count after jp-015: **17 / 35 Places**.
Remaining research-pending Places: **18**.
