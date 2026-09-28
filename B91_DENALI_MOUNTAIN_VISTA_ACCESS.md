# B91 — Denali Mountain Vista Dynamic Access Provider

## Goal

Connect the researched `us-041` Mountain Vista Opportunities to an authoritative, fail-closed current access provider instead of leaving them blocked on `dynamic_access`.

Affected Opportunities:

- `us-041-P01` — Mountain Vista・Denali／Alaska Range遠景
- `us-041-P02` — Mountain Vista・Denali極光／夜空

## Authoritative source

U.S. National Park Service — Denali Current Conditions:

https://www.nps.gov/dena/planyourvisit/conditions.htm

NPS states on this page that its current-condition details supersede other trip-planning information. The page also documents how far the Denali Park Road is currently open and warns that road access can change rapidly with snow/ice/weather.

Mountain Vista is near Mile 13. A closure farther west, such as the Pretty Rocks / Mile 43 closure, does **not** by itself make Mountain Vista inaccessible.

## Runtime contract

Provider file:

- `denali_access.py`

Provider version:

- `denali-mountain-vista-access-r1-preview`

The parser only returns OPEN when the official Current Conditions page has explicit present-tense language that the road is open far enough to reach or pass Mountain Vista, for example Mountain Vista, Savage River / Mile 15, or Teklanika / Mile 30.

The parser returns CLOSED only when the current page explicitly closes normal vehicle access at/before Park Headquarters / Mile 3.

Ambiguous, contradictory, unavailable, or unparsable pages return UNKNOWN.

## Freshness

Both OPEN and CLOSED results use `freshness_mode = live`.

The generic access-state contract therefore accepts the snapshot only within the existing six-hour freshness window for `road_viewpoint_status`.

This is intentional:

- a current road condition is useful for the near-term weather / aurora decision,
- it must not be extrapolated across the entire multi-day forecast,
- future weather rows beyond the live freshness window fail closed until a new provider fetch occurs.

## Opportunity behavior

After B91:

### us-041-P01
Required components:

- `dynamic_access`
- `visibility`

Both components are now runtime-supported, so the Opportunity moves from `module_pending` to `preview_module_available`.

### us-041-P02
Required components:

- `aurora_state`
- `dynamic_access`

B79 already supplies the location-aware NOAA OVATION aurora runtime. B91 supplies the missing access provider, so the Opportunity also moves to `preview_module_available`.

A closed/unknown/stale road state must still veto an otherwise-positive aurora signal.

## Safety / interpretation boundaries

- Favorable weather does not prove Mountain Vista access.
- Favorable aurora does not prove Mountain Vista access.
- A western Park Road closure beyond Mile 13 does not automatically block Mountain Vista.
- A generic seasonal statement is insufficient unless it appears in the official current-conditions context as a present road-open state.
- UNKNOWN never becomes OPEN.
- A live snapshot older than the access freshness window fails closed.
- This provider only models the researched Mountain Vista public Camera Zone; it does not prove parking availability, road surface safety, or entitlement for unrelated Denali destinations.

## CI / release coverage

B91 adds:

- open / closed / ambiguous NPS parser fixtures,
- provider parser tests,
- stale-snapshot regression,
- P01 access + visibility runtime test,
- P02 access veto against an otherwise-positive aurora state,
- US-region CI impact routing for `johnston_ridge_access.py` and `denali_access.py`,
- Candidate Weather / Browser Smoke / production weather trigger coverage.

## Expected manifest delta

No Place / Opportunity / Variant / Viewpoint count changes.

Runtime-policy delta:

- `module_pending`: -2
- `preview_module_available`: +2
