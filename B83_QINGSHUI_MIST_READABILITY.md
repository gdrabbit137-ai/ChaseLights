# B83 Qingshui Cliff Morning-Mist Readability Guard

Date: 2026-09-28 (Asia/Taipei)

## Purpose

B81 admitted `tw-034-P03 — 清水斷崖晨霧、雲霧山海` from Grade-A place-specific evidence.
B82 added optional north-facing multi-point environmental proxy sampling.

Production output after B82 exposed an over-promotion case: a camera-grid visibility near 0.7 km could still receive an 88 score when north-sector proxy cells were mistier than the camera. That violates the researched composition contract because the Opportunity requires some cliff / mountain / coast outline to remain readable.

## B83 rule

For `tw-034-P03`:

- local whiteout remains a hard blocker;
- directional mist evidence remains useful;
- low visibility alone remains only a candidate signal;
- a high-score mist recommendation additionally requires camera-grid visibility to remain above a conservative composition-readability guard;
- the current guard is 2.5 km, matching the nearest B82 directional environmental proxy range;
- 2.5 km is a planning threshold, not a claimed physical distance from the Camera Zone to the cliff.

If camera-grid visibility is below 2.5 km but mist evidence exists, keep the Opportunity as a low-confidence candidate and cap its minimum-sufficient hint at 68 instead of promoting it into the 80+ band.

## UI semantics

Confirmed directional mist + readable camera view:
- `OPPORTUNITY_MIST_MATCH`
- medium confidence
- may enter the 80+ band.

Mist evidence but cliff readability uncertain:
- `OPPORTUNITY_MIST_CANDIDATE`
- low confidence
- explicit negative factor explaining that the camera-point visibility is below the conservative readability threshold.

## Evidence boundary

This guard does not prove actual on-site visibility, exact fog position, or exact cliff distance. It only prevents the forecast model from treating a mist signal as automatically sufficient for the verified composition when the camera-grid visibility is itself too short.
