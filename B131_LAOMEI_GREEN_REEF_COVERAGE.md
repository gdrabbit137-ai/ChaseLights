# B131 Laomei Green Reef Subject-aware WeatherGrid Coverage

Date: 2026-09-29

## Goal

Make `tw-073` 老梅綠石槽 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring.

The weather-relevant photographed scene is not the Place center. It is:

- the researched public-coast Camera Zone;
- the seasonal green algae-covered erosion-groove foreground;
- the spring dawn / sunrise atmosphere used by the canonical Opportunity.

## Existing catalog contract

`tw-073-P01` already defines:

```text
Camera Zone: 老梅綠石槽公共海岸 Camera Zone
foreground:  spring green algae-covered erosion grooves
season:      March to mid-May
tide:        low / dry tide window
sun:         eastern dawn / sunrise
```

The canonical Camera Zone `tw-073-VP01` is a high-confidence `small_area` with:

```text
anchor:             25.29242, 121.54446
geometry_extent_m:  250
```

The catalog explicitly says this is a movable coastal composition area rather than a unique tripod point.

## Official evidence

Taiwan Tourism Administration publishes Laomei Green Reef at approximately:

```text
25.292439, 121.54471
```

and describes the April-May green algae-covered erosion grooves while warning visitors not to step on the slippery reef.

The North Coast and Guanyinshan National Scenic Area Headquarters' 2026 peak-season notice states that:

- the green-reef season runs approximately March through May;
- guided viewing is provided during daily low-tide periods from March through mid-May;
- early-morning slant sunlight across the green reef and sea is a recognized photography period;
- visitors must not step on the reef.

Sources:

- https://www.taiwan.net.tw/m1.aspx?id=a12-00270&sno=0001016
- https://www.northguan-nsa.gov.tw/USER/article.aspx?Lang=2&SNo=04008948

## Foreground subject geometry

B131 does not invent an exact reef polygon.

The photographed green-reed foreground is represented conservatively by reusing the catalog's existing 250 m Camera Zone extent:

```text
origin:  tw-073-VP01
azimuth: 0°-360°
range:   0-0.25 km
```

This is intentionally an over-covering local subject envelope for the algae-covered erosion grooves.

## Spring dawn environment geometry

At latitude ~25.29°N, geometric sunrise azimuth from March 1 through May 15 is approximately 99° to 69° from north.

B131 pads that seasonal range to:

```text
origin:  tw-073-VP01
azimuth: 65°-105°
range:   0-15 km
```

The padding is deliberate. This sector is used only to ensure WeatherGrid contains the atmosphere relevant to the spring dawn composition.

It does not claim:

- an exact visible local horizon;
- an exact daily solar alignment;
- a terrestrial coordinate for the Sun.

Status remains `provisional`.

## Registry result

```text
registry_version: B121.8 -> B121.9
entries:          34 -> 35
complete:         34 -> 35
needs_research:   0
```

`tw-073` has one active Opportunity, so it becomes an all-topic-complete Place.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-073
```

The derived provider bbox must contain:

- the conservatively expanded 250 m Camera Zone;
- the local green-reef subject envelope;
- the padded 65°-105° spring dawn sector;
- display padding;
- the GFS interpolation halo.

It must remain smaller than the Taiwan regional request.

## Regression requirements

CI must prove:

1. registry count is 35;
2. `tw-073-P01` is provisional-complete;
3. the official attraction coordinate is inside the coverage bbox;
4. all conservative Camera Zone extent points are inside the coverage bbox;
5. browser payload marks `tw-073` all-topic-complete;
6. subject and environment are exported as sectors;
7. B123 Place-scoped fetch is safe and smaller than Taiwan-wide;
8. existing all-topic-complete Places remain complete;
9. scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact reef polygon claim;
- no fake terrestrial Sun coordinate;
- no exact local-horizon claim;
- no inference that favorable weather overrides tide, marine safety, access, or no-stepping rules;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-073` scoped GFS validation;
- continue with other single-Opportunity Places whose photographed subject geometry is already strongly constrained;
- keep seasonal/tide/marine eligibility logic separate from WeatherGrid coverage geometry.
