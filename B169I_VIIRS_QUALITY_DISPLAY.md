# B169i VIIRS quality-aware display semantics

Date: 2026-10-01

B169i keeps VNP46A4 radiance and quality semantics visible at the point-inspector level.

For a selected photography point:
- radiance remains the continuous annual nighttime-light field;
- the VNP46A4 quality flag is sampled by nearest browser grid cell, never interpolated;
- QA 0 is shown as good, QA 1 as poor/lower quality, QA 2 as gap-filled;
- missing/unknown quality is stated rather than inferred.

The radiance legend uses explicit piecewise ticks (0, 1, 5, 10, 50+) so low-light differences are not visually collapsed by bright urban outliers.

This batch does not turn radiance into a Bortle class, sky brightness, or a photography score. It also does not mix daily/NRT Black Marble products into the annual baseline.
