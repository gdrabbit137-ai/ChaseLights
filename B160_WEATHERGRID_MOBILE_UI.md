# B160 — WeatherGrid mobile UI optimization

Date: 2026-10-01

## Goal

Reduce vertical chrome on phones so the weather map appears much earlier, while
keeping all existing WeatherGrid capabilities and desktop behavior.

The reference issue was a phone layout where controls consumed most of the
initial viewport and the map did not become visible until far down the page.

## Mobile changes

### Safe-area aware page chrome

The viewport opts into `viewport-fit=cover` and mobile body padding includes
the iOS safe-area insets. Controls and labels therefore do not sit underneath
the status bar or Dynamic Island area.

### Two-column primary controls

Phones keep a two-column control grid instead of collapsing every field into one
full-width row.

- data source + layer share the first row;
- display opacity remains full width because it is a continuous slider;
- Place + photography topic share a row once a Place is selected.

When no Place is selected, the disabled topic selector is hidden and the Place
selector expands across both columns.

### Reset view becomes a map action

The large full-width `模型範圍` control is removed from the filter stack.
It becomes a compact overlay button inside the map, next to the map navigation
controls.

This preserves the action while removing one entire control row.

### Larger mobile map

The mobile map uses a taller aspect ratio so the useful weather visualization
gets more screen area after the filter stack is compacted.

### Smaller map overlays

On phones:

- the basemap provider badge is constrained so it cannot dominate the map;
- the legend is smaller;
- the provider-boundary explanatory line is hidden because the boundary itself
  remains visible and the full explanation is still available in data info.

### Compact forecast-time navigation

Previous / slider / next / play stay on one row.

The play button becomes an icon-only control on phones. Five timeline captions
are reduced visually to three (start / middle / end) to prevent clipped,
low-value labels.

### Compact inspector

Inspector cards use smaller padding and typography on mobile while retaining the
same data and progressive disclosure behavior.

## Guardrails

- no weather values change;
- no model-selection behavior changes;
- no timeline semantics change;
- no coverage geometry changes;
- no Photography Opportunity scoring changes;
- desktop layout keeps its existing three-column control grid.

## Regression requirements

The existing WeatherGrid UI contract asserts:

- safe-area handling;
- two-column mobile controls;
- progressive topic visibility;
- map-overlay reset action;
- single-row mobile time controls;
- taller mobile map;
- compact legend behavior.
