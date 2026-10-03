# ChaseLights — Place Discovery Sorting & Area Filtering R1

Date: 2026-10-03

## Goal

Make the main Place list useful before the user chooses a state, prefecture, or county/city.

Filtering and ordering are separate concepts:

- first-level administrative areas are multi-select filters;
- sorting controls how the already-filtered Places are ordered;
- the default ordering is stable geographic browsing rather than a weather score that changes every refresh.

## Default geographic browsing

The default sort is `region`.

Places are grouped for browsing by stable macro geography while retaining first-level administrative areas as the actual filter identity:

- Taiwan: North, Central, South, East, Offshore Islands;
- Japan: Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu/Okinawa;
- United States: Northeast, Midwest, South, West.

Within a macro group, first-level administrative order is deterministic. A Place spanning multiple first-level areas appears only once, at the first matching area in the defined browse order.

Macro groups are presentation only. They must not replace or rewrite `admin_areas`.

## Sort modes

The main list supports:

1. Geographic order — default; grouped by macro geography.
2. Score high to low — one global ranking with no macro group headings.
3. Score low to high — one global ranking with no macro group headings.
4. Distance near to far — one global ranking.
5. Distance far to near — one global ranking.

Missing scores or coordinates sort after comparable Places. Geographic order is the deterministic tie-breaker.

The weather score remains date-dependent; choosing a score sort therefore orders by the metric for the currently selected date.

## Distance privacy and permission

Distance sorting must not request location permission on page load.

The browser asks for geolocation only after the user explicitly chooses a distance sort. The returned coordinates are held in memory only:

- do not write exact location to localStorage;
- do not include it in URLs;
- do not send it to the ChaseLights data pipeline;
- a reload falls back to the default geographic sort if the previous choice was distance-based.

If geolocation is unavailable or denied, revert to geographic order and show a short status message.

When distance sorting is active, a Place card may show the calculated straight-line distance in kilometres so the ordering is explainable.

## Administrative-area filter

First-level administrative areas remain multi-select and country-specific:

- Taiwan: county/city;
- Japan: prefecture;
- United States: state / District of Columbia.

Only administrative areas containing at least one active Place are shown by default. This removes large disabled grey blocks from sparse countries while preserving the complete administrative model.

A dedicated control reveals areas not yet covered. Revealed zero-Place areas stay disabled. Search operates over the currently displayed area set.

Selections continue to be persisted per country under `chaselights_admin_areas_<region>`.

## Interaction with other filters

Favorites, Place search, selected date, and administrative-area filters run before sorting.

Changing sort order must not change:

- which Places match a filter;
- Place scoring;
- opportunity selection;
- navigation target semantics;
- favorite state.

The existing collapsed “no viable opportunity” section remains separate. Its members use the selected ordering inside that section.

## Responsive behavior

The same sort choices are available on desktop and mobile.

The existing mobile administrative-area bottom sheet remains the mobile selection surface. The zero-area disclosure control is available inside that sheet without expanding the page behind it.

## Regression requirements

Automated checks should cover at least:

- geographic sort is the default;
- score and distance modes exist;
- geolocation is called only from the distance-sort path;
- exact coordinates are not persisted;
- zero-count administrative areas are hidden by default and explicitly revealable;
- multi-select area filtering remains unchanged;
- geographic group rendering does not duplicate cross-boundary Places;
- score/distance modes render as global lists without geographic group headings.
