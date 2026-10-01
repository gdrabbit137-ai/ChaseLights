# B171e VIIRS spatial evidence sampling

B171e closes the explicit B171d gap between the published annual NASA Black Marble VNP46A4 WeatherGrid artifact and timestamp-level astrophotography diagnostics.

## Contract

For each forecast spot, ChaseLights loads the published browser artifact and its QC artifact once, then samples the nearest published grid cell at the camera coordinates. The sampled radiance and VNP46A4 quality flag are copied into the existing item-data keys consumed by B169j.

The join fails closed when:
- either artifact is absent or invalid;
- QC identifies flags;
- the requested coordinate is outside the artifact bbox;
- the sampled radiance or quality value is missing.

## Resolution semantics

This is intentionally a sample of the **published browser grid**, not a claim of native 15 arc-second sampling. The diagnostic preserves:
- sampled latitude/longitude;
- sampling distance;
- annual composite year;
- browser sampling stride;
- native source resolution provenance;
- explicit `nearest published browser-grid cell; not native-resolution sampling` semantics.

This matters because B169g may deterministically stride the native VNP46A4 grid to stay within the browser payload budget.

## Scoring boundary

A successful QA-preserving sample can satisfy B171's `quality_checked_nighttime_light_radiance` evidence requirement. It remains artificial-light radiance context only.

B171e does not:
- convert VIIRS radiance to Bortle class or SQM;
- claim zenith sky brightness or Milky Way visibility;
- alter Opportunity scoring.

A future native-resolution/server-side sampler can replace the browser-grid join without changing the B169j/B171 diagnostic semantics.
