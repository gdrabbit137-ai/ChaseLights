# B137 — Country-aware first-level administrative-area filters

## Goal

Use one geographic filtering interaction across ChaseLights while respecting each country's own first-level administrative divisions.

- Taiwan: county / city
- Japan: prefecture (都道府県)
- United States: state (plus Washington, D.C. in the complete picker)

The old Japan macro regions (for example 関東/中部) and U.S. macro regions (for example 美西) remain legacy catalog metadata only. They are no longer primary UI filters.

## UI behavior

1. Favorites is a standalone toggle in Taiwan, Japan, and the United States.
2. The geographic picker appears in the same position for all three countries.
3. Japan is grouped for browsing by Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, and Kyushu/Okinawa.
4. The United States is grouped by Northeast, Midwest, South, and West.
5. The actual selected values are prefectures/states, not the visual macro groups.
6. Japan and U.S. pickers include search because 47/51 first-level areas are too many for a flat picker.
7. The complete first-level administrative model remains stable as catalog coverage grows, but the picker hides zero-Place areas by default. An explicit “show uncovered areas” control reveals them as disabled entries.
8. Multi-jurisdiction Places match when any selected administrative area intersects their `admin_areas` list.
9. Place cards show the first-level administrative area when available instead of the legacy macro-region label.

## Data model

`regions.get_spots(region)` emits `admin_areas` for every supported country. TW, JP, and US are the first implementations of this country-neutral contract.

The value is always an array to support boundary/spanning Places. The rule is geographic, not country-specific:

- If a Place is wholly inside one first-level administrative unit, store one value.
- If the Place itself spans a boundary, store every first-level administrative unit it intersects.
- A large named area such as a national park may therefore have multiple values.
- A precise viewpoint inside that park should only carry the unit(s) that the viewpoint itself occupies.
- Do not add neighboring areas merely because they are commonly associated with the destination.
- Visual macro-regions (for example "West", "Kanto", or "Northern Taiwan") are browsing groups only and must not replace the authoritative first-level units.

For future countries, use the country's normal first-level administrative division as the filter identity (for example province, state, prefecture, region, canton, etc.). The UI may localize the label, but the same array/intersection behavior applies everywhere.

Examples:

```json
{"spot_id":"jp-010","admin_areas":["山梨県"]}
{"spot_id":"us-001","admin_areas":["Arizona"]}
{"spot_id":"us-014","admin_areas":["California","Nevada"]}
{"spot_id":"us-038","admin_areas":["Tennessee","North Carolina"]}
```

The browser contains a compatibility fallback for cached pre-B137 JP/US weather snapshots that do not yet contain `admin_areas`. Fresh snapshots should use the metadata emitted by `regions.py`.

## Compatibility

- Existing `category` values are not removed in B137 because scoring/data paths may still reference them.
- Existing saved category selections are collapsed to the all-Places state; Favorites remains preserved.
- Existing per-country selected admin areas remain stored under `chaselights_admin_areas_<region>`.

## Regression expectations

- Every active Place in every supported country must have at least one `admin_areas` value.
- Border/spanning examples remain multi-valued, including Taiwan county/city boundaries, Japan prefecture boundaries, U.S. state boundaries, and equivalent future-country boundaries.
- Filtering uses `admin_areas`, not legacy `category`.
- Search also matches localized prefecture/state names.
