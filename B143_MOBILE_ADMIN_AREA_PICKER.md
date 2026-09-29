# B143 — Mobile Administrative Area Picker

## Goal

On phones, the administrative-area picker must not expand inline into a page-height panel. It becomes a bottom-sheet dialog while desktop/tablet keeps the existing floating dropdown.

This applies to every supported country and reuses the B137 first-level administrative-area model.

## Responsive behavior

- `<= 640px`: bottom sheet.
- `>= 641px`: existing floating dropdown.
- The underlying filter state, `currentAdminAreas`, persistence keys, area counts, and multi-jurisdiction matching are shared by both layouts.

## Mobile bottom sheet

Opening the area control must:

1. show a dimmed backdrop;
2. lock background-page scrolling while preserving the original scroll position;
3. open a sheet from the bottom;
4. keep the sheet height bounded with `height: min(72dvh, 680px)` and `max-height: 82dvh`;
5. expose an explicit close button with at least a 44x44 px target;
6. expose a persistent footer with Clear and Done actions;
7. preserve iPhone safe-area padding;
8. move keyboard focus into the sheet.

Closing is supported by:

- the top-right close button;
- Done;
- tapping the backdrop;
- Escape;
- browser / Android Back via a temporary history entry;
- tapping the trigger again.

Done closes the sheet only. It does not introduce a second "apply" state.

## Selection behavior

- Area changes apply immediately.
- The sheet stays open after an area is toggled so multi-select remains efficient.
- Reload persistence continues to use `chaselights_admin_areas_<region>`.
- Active areas include a visible checkmark in addition to color.
- Zero-place areas remain visible but disabled.

## Search

The mobile sheet always shows search.

Localized placeholders:

- Taiwan: county / city search;
- Japan: prefecture search;
- United States: state search.

Search matches both canonical area identifiers and localized labels.

When a query is active, matching groups auto-expand and nonmatching groups hide.

## Group behavior

Japan and the United States use collapsible visual groups on mobile.

- A group containing an active selection opens automatically.
- If no area is selected, the first group opens initially.
- Other groups are collapsed.
- Desktop groups remain fully expanded and are not interactively collapsible.
- Grouping is presentation-only; the selected identity remains the first-level administrative unit.

Taiwan remains a single flat first-level area list.

## Scroll model

The sheet consists of:

- fixed header;
- fixed search field;
- independently scrollable area list;
- fixed footer.

The page behind the sheet must not scroll.

## Accessibility

The mobile sheet uses dialog semantics with `aria-modal=true`.

- Trigger exposes expanded state.
- Area buttons expose `aria-pressed`.
- Disabled zero-count areas use native disabled state plus `aria-disabled`.
- Close has a localized aria-label.
- Focus returns to the area trigger after closing.
- Reduced-motion preference disables sheet and chevron animation.

## Regression requirements

- Desktop area dropdown positioning and behavior remain intact.
- Choosing an area updates results immediately without closing the mobile sheet.
- Search text and currently expanded group state survive a filter re-render.
- Cross-boundary Places still appear once when one or several matching areas are selected.
- Switching countries keeps each country's stored area selection independent.
- Opening or closing the picker must not change the page's previous scroll position.
- On mobile, the trigger owns the open/close transition explicitly; the sheet must not depend solely on the asynchronous native `<details>` `toggle` event to acquire the scroll lock.
