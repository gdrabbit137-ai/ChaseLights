# B134 Kuibishan Moses-Sea Subject-aware WeatherGrid Coverage

Date: 2026-09-30

## Goal

Make `tw-059` 奎壁山 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring or pretending that weather can determine whether the tidal causeway is safely walkable.

The photographed subject is the local low-tide "Moses sea-parting" scene between Kuibishan's east shore and Chiyu.

## Existing catalog contract

`tw-059-P01` is the canonical Opportunity:

```text
name:          奎壁山摩西分海
Camera Zone:   北寮奎壁山岸側觀景區
formula:       needs_tide_access_module
best time:     low_tide_window
```

The catalog Camera Zone `tw-059-VP01` is a site-verified small-area anchor at:

```text
23.59968, 119.67137
```

Its exact public standing-area extent is not reconstructed in the catalog, so WeatherGrid must preserve an anchor-only Camera Zone warning rather than invent a shoreline polygon.

## Official evidence

Penghu National Scenic Area official material states that:

- the east shore below Kuibishan and Chiyu are connected at low tide by an S-shaped gravel causeway;
- the exposed causeway is about 300 m long;
- the route widens as the tide recedes;
- returning water can rise quickly, so tide timing and safe access are dynamic concerns.

Sources:

- https://www.penghu-nsa.gov.tw/TravelInformationSceneryDetailC001200.aspx?Cond=0947d150-504e-425c-9920-cd5fa2652527&Language=1028&SearchAdvanced=True&SortType=1
- https://www.penghu-nsa.gov.tw/ChiHoOneLer/tour/ThematicTours/Recommend/Package04.htm

## Subject geometry

B134 does not invent an exact causeway polyline, tide boundary, shoreline polygon or Chiyu outline.

Instead, it conservatively over-covers the official ~300 m local subject with:

```text
origin:  tw-059-VP01
azimuth: 0°–360°
range:   0–0.4 km
```

This local subject envelope covers the shore-side Camera Zone, the exposed gravel path and the immediate intertidal scene while remaining far smaller than a regional request.

## Dynamic conditions remain separate

WeatherGrid coverage does not decide:

- whether the causeway is exposed;
- whether it is safe to enter;
- how quickly water is returning;
- whether tide timing is inside the permitted/safe window.

Those remain fail-closed tide/access/safety concerns in the Photography Opportunity model.

## Registry result

```text
registry_version: B121.11 -> B121.12
entries:          37 -> 38
complete:         37 -> 38
needs_research:   0
```

`tw-059` has one active Opportunity, so it becomes all-topic-complete.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-059
```

The derived provider bbox must contain the curated Camera Zone plus the local 0.4 km subject envelope, display padding and GFS interpolation halo, while remaining smaller than the Taiwan regional bbox.

## Regression requirements

CI must prove:

1. registry count is 38;
2. `tw-059-P01` is provisional-complete;
3. the Camera Zone coordinate is contained in coverage;
4. the 0.4 km local subject envelope materially extends beyond the anchor;
5. browser payload marks `tw-059` all-topic-complete;
6. the subject is exported as an explicit sector;
7. Camera Zone exposure remains generalized;
8. B123 Place-scoped fetch is safe and smaller than Taiwan-wide;
9. existing all-topic-complete Places remain complete;
10. Photography Opportunity scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact causeway/polyline claim;
- no inferred tide state from WeatherGrid;
- no assumption that favorable weather means safe access;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-059` scoped NOAA/NOMADS validation;
- continue migrating single-Opportunity Places only when the subject can be conservatively bounded from official evidence;
- keep tide/access eligibility separate from WeatherGrid geometry.
