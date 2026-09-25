Continue ChaseLights R4.2 B32 from branch `r4.2-b32-jp025-hagi`.

Read first:
1. `handoff/B32_20260925/00_START_HERE/HANDOFF_README.md`
2. `NAVIGATION_SPEC_R4_2.md`
3. `B32_JP_RESEARCH_BATCH13.md`
4. `B32_JP_RESEARCH_BATCH12.md`
5. `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md`
6. `LOCATION_AUDIT.md`
7. `regions.py`
8. `analyze_weather.py`
9. `index.html`
10. `test_opportunity_adapter.py`

Important current change:
- Camera Zone and Navigation Target are separate.
- Never use `map_query` to construct production Google Maps navigation.
- `verified` targets use exact-coordinate Directions.
- `provisional_camera_anchor` is an exact map pin only.
- `needs_review` / `multiple_access_routes` must not keyword-search a destination.
- 加羅湖 is intentionally `needs_review`.
- New weather schema is v10.

QA already green:
- Adapter 36100446591
- Japan Candidate QA 36100403517
- Browser Smoke 36100369665

Taiwan Candidate QA:
- PASS 36100640799

Current Japan research is 25/35. The next Place after navigation work is `jp-026 出雲大社`.

For every new Place, research both:
1. photographable Camera Zone / composition;
2. practical Navigation Target / arrival point.

Do not infer one from the other.
