# B136 — Country-aware first-level administrative-area filters

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
7. Areas with zero current ChaseLights Places stay visible but disabled, so the administrative model is stable as catalog coverage grows.
8. Multi-jurisdiction Places match when any selected administrative area intersects their `admin_areas` list.
9. Place cards show the first-level administrative area when available instead of the legacy macro-region label.

## Data model

`regions.get_spots(region)` emits `admin_areas` for TW, JP, and US.

The value is always an array to support boundary/spanning Places. Examples:

```json
{"spot_id":"jp-010","admin_areas":["山梨県"]}
{"spot_id":"us-001","admin_areas":["Arizona"]}
{"spot_id":"us-038","admin_areas":["Tennessee","North Carolina"]}
```

The browser contains a compatibility fallback for cached pre-B136 JP/US weather snapshots that do not yet contain `admin_areas`. Fresh snapshots should use the metadata emitted by `regions.py`.

## Compatibility

- Existing `category` values are not removed in B136 because scoring/data paths may still reference them.
- Existing saved category selections are collapsed to the all-Places state; Favorites remains preserved.
- Existing per-country selected admin areas remain stored under `chaselights_admin_areas_<region>`.

## Regression expectations

- Every active TW/JP/US Place must have at least one `admin_areas` value.
- Border/spanning examples remain multi-valued.
- Filtering uses `admin_areas`, not legacy `category`.
- Search also matches localized prefecture/state names.
