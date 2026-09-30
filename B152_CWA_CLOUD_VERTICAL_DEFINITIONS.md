# B152 — CWA cloud-field verification and model-specific vertical definitions

Date: 2026-09-30

## Goal

Verify whether the CWA WRF 3 km public feed used by ChaseLights can publish
native low/middle/high cloud-cover layers.  At the same time, preserve and show
the vertical definition of cloud layers for providers that do publish them.

## CWA result

The current ChaseLights CWA provider reads the public M-A0064 WRF 3 km GRIB2
series.

A live PR smoke test downloaded the current f000, f006 and f012 files and
inventoried every GRIB variable whose name/metadata referred to cloud or
humidity.

Observed cloud/humidity-related fields in all three files:

- 2 m specific humidity
- 2 m relative humidity
- pressure-level relative humidity

No native GRIB cloud-cover field was present:

- no LCDC
- no MCDC
- no HCDC
- no TCDC
- no equivalent cloud-fraction field

This agrees with the official M-A0064/M-A0061 WRF product table: the upper-air
package publishes relative humidity on standard pressure levels
1000/925/850/700/500/400/300/250/200/150/100 hPa, while the surface package
does not list low/mid/high cloud cover.

CWA's public visualization products are broader than this raw feed.  The WIFI
site documents a WRF low-level cloud-cover display, and the NPD product catalog
lists WRF "cloud cover + relative humidity" charts.  Those are evidence that
CWA has cloud diagnostics internally/for visualization, but they do not provide
a validated raw low/middle/high cloud field contract for the M-A0064 files
currently integrated by ChaseLights.

### Decision

Do **not** derive or label low/middle/high cloud cover from relative humidity in
B152.

Relative humidity is useful evidence for cloud potential, but it is not the
same quantity as model cloud fraction.  A future RH-derived cloud proxy may be
added as a separately named experimental product, but it must not masquerade as
native CWA cloud cover or be mixed directly with ICON/GFS cloud percentages.

If CWA later exposes a stable raw cloud-cover endpoint/field, it can be added to
the existing provider without changing the browser model selector architecture.

## ICON Global vertical definition

DWD's GRIB parameter definition is retained verbatim in the browser metadata:

- Low cloud / CLCL: surface–800 hPa — approximately ground to 2 km
- Mid cloud / CLCM: 800–400 hPa — approximately 2 to 7 km
- High cloud / CLCH: below 400 hPa pressure — approximately above 7 km

The kilometre ranges are explanatory standard-atmosphere approximations.  The
pressure bounds are the authoritative model definition.

## GFS vertical definition

NCEP UPP defines the low/middle/high cloud layers as:

- Low: pressure >= 642 hPa — approximately ground to 3.7 km
- Mid: 642–350 hPa — approximately 3.7 to 8.1 km
- High: pressure < 350 hPa — approximately above 8.1 km

Again, the pressure bounds are authoritative; the kilometre values are only a
human-readable approximation.

## Browser metadata contract

Cloud fields may contain:

```json
{
  "vertical_definition": {
    "coordinate": "pressure",
    "native_definition": "surface–800 hPa",
    "approx_height": "約地面～2 km",
    "pressure_bounds_hpa": {
      "bottom": "surface",
      "top": 800
    },
    "definition_source": "DWD CLCL"
  }
}
```

The WeatherGrid inspector renders the selected model and layer together with
this native definition and approximate altitude.

Examples:

- ICON Global — 低雲 / surface–800 hPa / 約地面～2 km
- GFS 0.25° — 低雲 / surface–642 hPa / 約地面～3.7 km

The UI intentionally does not normalize the providers into one common cloud
height definition.

## Guardrails

1. Provider-native cloud percentages keep their provider-native vertical
   definitions.
2. Approximate height text never replaces the pressure definition.
3. CWA M-A0064 pressure-level RH is not published as cloud cover.
4. Cross-model comparisons must account for different vertical layer bounds.
5. Auto provider selection must never blend cloud percentages from two models.
