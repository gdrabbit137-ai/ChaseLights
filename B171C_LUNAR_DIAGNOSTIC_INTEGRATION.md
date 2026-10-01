# B171c Lunar evidence integration

B171c wires the B171b replayable lunar ephemeris into the B171a astrophotography diagnostic.

When timezone-aware time plus camera latitude/longitude are supplied, Moon altitude and illumination are calculated instead of remaining missing. Target separation is calculated only when a target is explicit. The built-in `galactic_core` target uses the same coordinates as the existing ChaseLights astronomy helper.

A camera position without a target is intentionally insufficient for `moon_target_separation`; the system does not invent a target. Existing item-level lunar fields remain supported for replay/backward compatibility.

This remains diagnostic only and does not alter Opportunity scoring.
