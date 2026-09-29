# B146 WeatherGrid Overlay Readability

Date: 2026-09-30

## Goal

Make the B144 cartographic basemap genuinely useful underneath the GFS WeatherGrid instead of tinting every grid cell with the same fixed opacity.

The B145 production screenshot proved that MapLibre/OpenFreeMap is loading correctly. It also exposed a readability problem: a low-cloud value of 0% still painted a dark-blue cell at the global 62% layer opacity, so clear areas obscured the basemap even though the weather signal was effectively absent.

## Rendering change

B146 keeps the user-level WeatherGrid opacity control, but adds a second value-aware cell opacity.

Effective alpha is:

```text
user opacity × value-aware cell opacity
```

Default user opacity remains 62%.

## Per-layer behavior

### Low / mid / high cloud

Clear cells become nearly transparent. Cloudier cells progressively become more visible.

This makes coastline, roads and labels readable in clear areas while preserving dense-cloud structure.

### Precipitation

Near-zero precipitation is fully transparent.

Rain cells become progressively stronger with rate.

### Visibility

Poor visibility is emphasized. High/clear visibility recedes so a mostly clear map does not become a solid color wash.

### Wind speed

Low wind recedes; stronger wind becomes more visible.

### Wind direction

Direction is categorical/circular rather than magnitude-like, so it retains a moderate constant cell opacity.

## Basemap-only inspection

The WeatherGrid opacity slider now supports:

```text
0% .. 100%
```

instead of starting at 20%.

At 0%, the user can inspect the cartographic basemap and Camera / Subject / Environment overlays without any weather fill.

## Scope guardrails

- no GFS values are changed;
- no provider/fetch changes;
- no Photography Opportunity scoring changes;
- no subject-aware coverage geometry changes;
- this is presentation-only alpha compositing;
- the existing 62% default remains unchanged.

## Regression requirements

CI verifies:

1. the opacity slider allows 0%;
2. fixed global-alpha-only rendering is removed;
3. cloud opacity increases with cloud fraction;
4. dry precipitation becomes transparent;
5. clear visibility and low wind recede;
6. B117 WeatherGrid CI runs the readability contract.
