# B171b Lunar ephemeris contract

B171b exposes the dependency-free astronomy approximation already used in ChaseLights as a deterministic, replayable lunar contract.

Outputs include Moon altitude/azimuth, illumination fraction, and optional angular separation from an RA/Dec target. A helper uses the same Galactic Core coordinates already present in fetch_data.py.

The contract requires timezone-aware datetimes and fails closed for partial target coordinates. Accuracy is explicitly labelled approximate and is intended for photography planning, not navigation or scientific astrometry.

This batch does not yet change Opportunity scoring. B171c can inject these fields into the B171a astrophotography diagnostic so moon evidence becomes complete for a known camera position/time and target.
