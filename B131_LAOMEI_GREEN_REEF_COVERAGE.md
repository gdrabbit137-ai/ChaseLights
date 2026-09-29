# B131 Laomei Green Reef Subject-aware WeatherGrid Coverage

Date: 2026-09-30

## Goal

Make `tw-073` 老梅綠石槽 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring.

The weather-relevant scene is not the Place center. It is:

- the researched public-coast Camera Zone;
- the local spring green algae-covered erosion grooves as foreground;
- the eastern spring dawn atmosphere used by the canonical sunrise Opportunity.

## Existing catalog contract

`tw-073-P01` already defines:

```text
Camera Zone: 老梅綠石槽公共海岸 Camera Zone
foreground:  spring green algae-covered erosion grooves
tide:        dry / low-tide window
sun:         eastern dawn / sunrise
season:      March to mid-May
```

The catalog Camera Zone is:

```text
anchor:             25.29242, 121.54446
geometry_type:      small_area
geometry_extent_m:  250
coordinate confidence: high
geometry confidence:   high
```

The catalog explicitly treats the coast as a movable Camera Zone rather than one exact tripod point.

## Official evidence

Taiwan Tourism Administration lists Laomei Green Reef at approximately:

```text
25.292439, 121.54471
```

and describes the spring green algae-covered erosion grooves along the Laomei coast.

The North Coast and Guanyinshan National Scenic Area Administration states in its 2026 guidance that:

- the green season is approximately March to mid-May;
- dry-tide periods are preferred;
- visitors should arrive around one to two hours before/after dry tide;
- early-morning oblique sunlight gives strong color layering for photography;
- visitors must not step on the green grooves and should avoid full-tide / unsafe coastal conditions.

Sources:

- https://www.tad.gov.tw/m1.aspx?id=A12-00270&sNo=0001016
- https://www.northguan-nsa.gov.tw/user/Article.aspx?Lang=1&SNo=04008948
- https://www.northguan-nsa.gov.tw/user/article.aspx?Lang=1&SNo=04002497

## Foreground subject geometry

The photographed green-groove foreground is local to the researched coastal Camera Zone.

B131 represents it as a conservative full-circle local subject envelope:

```text
origin:  tw-073-VP01
azimuth: 0°–360°
range:   0–0.25 km
```

This intentionally reuses the catalog's curated 250 m Camera Zone extent.

It does **not** claim:

- an exact algae-coverage polygon;
- an exact exposed-tide polygon;
- a legal walking polygon;
- that every point inside the envelope is safe to stand on.

The existing no-stepping / safe-access rules remain separate hard gates.

## Spring dawn environment geometry

At latitude ~25.29°N, geometric sunrise direction from early March through mid-May is approximately 69°–99° azimuth.

B131 pads that range conservatively to:

```text
origin:  tw-073-VP01
azimuth: 65°–105°
range:   0–15 km
```

The sector is used only as a WeatherGrid atmospheric envelope around the spring dawn direction.

It does **not** claim:

- an exact Sun coordinate;
- exact Sun / groove alignment;
- exact local horizon obstruction;
- guaranteed sunrise visibility.

Actual Opportunity eligibility still depends on the separate seasonal, tide, marine, visibility and safety modules defined by the canonical catalog.

## Coverage result

```text
registry_version: B121.8 -> B121.9
entries:          34 -> 35
complete:         34 -> 35
needs_research:   0
```

`tw-073` has one active Opportunity, so it becomes all-topic-complete.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-073
```

The provider request must contain:

- the conservatively expanded 250 m Camera Zone;
- the local green-groove subject envelope;
- the 65°–105° spring dawn environment sector;
- display padding;
- the GFS interpolation halo.

The snapped provider rectangle must remain smaller than the Taiwan regional bbox.

## Regression requirements

CI must prove:

1. registry count is 35;
2. `tw-073-P01` is provisional-complete;
3. its coverage contains the official Tourism Administration attraction coordinate;
4. its coverage contains every conservative Camera Zone extent point from the 250 m catalog extent;
5. its coverage extends far enough east to contain the dawn sector;
6. browser payload marks `tw-073` all-topic-complete;
7. foreground and dawn geometry are exported as explicit sectors;
8. B123 Place-scoped fetch is safe and smaller than Taiwan-wide;
9. existing complete Places remain complete;
10. Photography Opportunity scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact algae polygon claim;
- no exact tide-line claim;
- no fake terrestrial coordinate for the Sun;
- no guarantee that weather alone makes the scene safe or seasonally valid;
- no stepping-access inference from the WeatherGrid geometry;
- no scoring changes.

## Previous live validation

Before starting B131, B130 `tw-075` was validated against a real NOAA/NOMADS request after merge.

The live check confirmed:

- current main returned `coverage_complete=true`;
- Place-scoped fetch remained enabled;
- provider bbox was `121.5–122.5E, 24.5–25.25N`;
- the response was a valid GRIB payload;
- the request succeeded on GFS `20260929T12Z_f000`;
- no regional fallback occurred.

The temporary validation PR was closed without merge after the result was captured.
