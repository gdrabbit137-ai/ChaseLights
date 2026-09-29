# B127 Qixingtan All-topic WeatherGrid Coverage

Date: 2026-09-29

## Goal

Make 七星潭 (`tw-036`) the third Place whose entire active Photography Opportunity set has subject-aware WeatherGrid coverage.

This completes the two remaining celestial / horizon Opportunities:

1. `tw-036-P01` — 七星潭礫石海岸日出
2. `tw-036-P02` — 七星潭海岸星空／銀河帶

The existing B121/B122 coverage for:

- `tw-036-P03` — 北望清水山／清水斷崖＋貼山雲帶
- `tw-036-P04` — 北望清水斷崖／清水山山海遠眺

is preserved.

No Photography Opportunity score changes are made.

## Evidence

### Sunrise

Official Taiwan tourism material identifies Qixingtan as a sunrise / dawn photography destination.

Sources:

- https://spotlightaward.taiwan.net.tw/tourpage.php?id=128d4234-7181-4ffd-aab7-56b9d4e95ae6&tag=4
- https://www.taiwan.net.tw/m1.aspx?id=9488&sno=0001016

The first source explicitly describes Qixingtan's dawn sunrise as a photography highlight. The second establishes the official Qixingtan Camera Zone location and open Pacific-coast setting.

### Stargazing / Milky Way

Official Hualien County tourism material identifies Qixingtan and Star Plaza as a stargazing location, and separately describes enjoying the starry sky / Milky Way at Qixingtan.

Sources:

- https://tour-hualien.hl.gov.tw/TourContent.aspx?n=109&s=1190
- https://tour-hualien.hl.gov.tw/News_Content.aspx?n=26&s=8386

Therefore the celestial Opportunities are Place-specific researched subjects. They are not inferred merely because Qixingtan is a dark coastal place.

## P01 sunrise geometry

The Sun is a celestial subject, so B120 forbids assigning it a fake terrestrial coordinate.

At the Qixingtan Camera Zone latitude (~24.03°N), the geometric horizon sunrise azimuth for solar declination ±23.44° is approximately:

```text
summer-solstice extreme  ~64.2°
equinox                  90.0°
winter-solstice extreme ~115.8°
```

B127 therefore uses a padded annual horizon envelope:

```text
azimuth: 60°–120°
range:   0–20 km
origin:  tw-036-VP01
```

The 20 km range is an **over-covering marine-horizon weather envelope**. It is not the distance to the Sun and is not an exact cloud-position claim.

The provider Fetch BBox adds its own GFS interpolation halo beyond this viewport geometry.

## P02 stargazing / Milky-Way geometry

The Milky Way is also celestial and its apparent azimuth changes with date and time.

The current runtime does not yet have a curated ephemeris-facing sector for this Opportunity. B127 therefore does not invent one.

Instead it uses:

```text
origin:  tw-036-VP02
azimuth: 0°–360°
range:   0–20 km
role:    celestial_cloud_environment_zone
```

This is a conservative local atmospheric / horizon envelope that prevents the WeatherGrid from cropping weather in a possible viewing direction before the astronomy module determines the actual sky orientation.

Status remains `provisional`.

## Place-level result

After B127:

```text
tw-036 catalog Opportunities = 4
coverage entries             = 4
all_topics_complete          = true
```

The all-topic-complete Places are now:

```text
tw-014  雲洞山莊觀景平台
tw-036  七星潭
tw-082  鯉魚潭
```

B123 can therefore safely use:

```text
coverage_scope = place
coverage_id    = tw-036
```

and derive a scoped GFS/NOMADS request from the union of all four Camera / Subject / Environment coverage plans.

## Registry state

B127 advances the sidecar to:

```text
registry_version = B121.5
entries          = 29
provisional      = 29
complete         = 29
needs_research   = 0
```

These counts describe migrated coverage entries only, not all Opportunities in the canonical catalog.

## Regression requirements

CI must prove:

1. all four `tw-036` Opportunities are provisional-complete;
2. the browser payload reports `tw-036 all_topics_complete=true`;
3. the P01 sunrise coverage materially extends east of the Camera Zone;
4. the P02 celestial environment surrounds the Camera Zone in all directions;
5. Place-scoped B123 fetch for `tw-036` remains scoped and smaller than the Taiwan regional request;
6. an actually unmigrated Place such as `tw-034` still falls back to the Taiwan-wide provider bbox;
7. `tw-014` and `tw-082` remain all-topic complete;
8. no scoring behavior changes.

## Guardrails

- no fake Sun / Milky-Way ground coordinate;
- no claim that 20 km is a physical subject distance;
- no claim that P02's full-circle envelope is the actual Milky-Way direction;
- exact ephemeris-facing sectors may replace the provisional envelope later;
- Camera Zones remain browser-generalized;
- coverage geometry remains separate from scoring sample topology.

## Next work

1. live-run `place / tw-036` with B123 and compare overlapping grid cells with a regional run;
2. complete `tw-034` P01/P02 so 清水斷崖 becomes Place-scope safe;
3. extend the same all-topic completion pattern to other Places that are close to full migration;
4. later let the astronomy module replace broad celestial envelopes with time-specific viewing sectors.
