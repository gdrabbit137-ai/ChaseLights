# CL-UI-118 — Homepage card hierarchy and alignment (owner spec, 2026-11-27)

Owner-reported after reviewing the live homepage with the CL-UI-115/117 now-row
shipped. All four layers below change the same card surface
(`assets/app.js` + `assets/app.css`), so they ship as ONE ticket with two
reviewable sub-commits: (A) layer re-ordering + the bell consolidation,
(B) the alignment/typography pass.

## What the owner sees today

The card mixes four different concerns on loosely separated lines:

- the identification row (name, city/landform sub-label, ✓ badge, star)
- the now row (`陰 · 12.7°C · ≥ 24 km（資料上限）01:00`)
- the subject row (`夜景：22:00–23:00`) with its own per-subject bell
- the terrain parameters (`1082 m`) and the azimuth/elevation numbers wrapping
  onto a line of their own, so two cards side by side do not line up

Photographers read top-down: *where is this* → *what is it like right now* →
*what can I shoot and when* → *the terrain numbers*. The current order buries
the answer to the second question under the subject row.

## Required structure (four layers, fixed order)

### Layer 1 — identification
Left: spot name, then the city/landform sub-label with a higher-contrast tone
than today.
Right: `✓ 推薦` badge, the favourite star, and **one spot-level reminder bell**.
Remove the per-subject bell that currently repeats on every subject row — one
bell per spot is enough, and its menu must still offer the same per-subject
choices it offers today.

### Layer 2 — now (its own full-width line, moved ABOVE the subject block)
- Temperature, condition word, visibility, hour label.
- Fog/rain right now: the chip turns amber/orange (red when visibility < 1 km),
  keeping the existing `.now-wx` / `.now-stale` semantics from CL-UI-117.
- `≥ 24 km（資料上限）` becomes **`≥ 24 km`**; the words 「資料上限」 move into a
  `title`/`aria-label` tooltip so the number stays honest but the line is short.

### Layer 3 — headline subject and window (the visual protagonist)
Directly under the now row and directly above the action row:
- larger type than today (the answer to 「拍什麼、幾點拍」 must win the card)
- a faint state background tint plus a left colour bar, using the existing
  green = recommend / amber = chance / grey = not-recommended tokens
- keeps the existing text shape (`夜景：22:00–23:00`) and i18n keys

### Layer 4 — terrain parameters + action row
- elevation (`▲ 86 m`) and the astronomical numbers become their OWN fixed
  single line — never mixed into the now row and never wrapping
- the action row (`題材` / `地圖` / `天氣圖` / `LIVE`) sits at the bottom
- **acceptance**: for cards in the same grid row, every layer's top edge and the
  action row's top edge are horizontally aligned (measure with
  `getBoundingClientRect()` across a row of cards, tolerance ≤ 1 px).

## Constraints

1. Whitelist: `assets/app.js`, `assets/app.css`, the HTML stamp lines and the
   tests under `apps/web-v2/tests/`. No `data/**`, no `packages/**`.
2. **Never weaken an assertion.** Tests that pin the current order (the now row
   before/after the subject row, the per-subject bell) must be *extended* to the
   new contract, not deleted.
3. The single-source rule from CL-CI-44 still holds: the card, the weather panel
   and the subject panel read verdicts from the same helpers. Re-ordering the
   DOM must not introduce a second judgement path.
4. The now-row data source must stay the CL-UI-117 sidecar with its existing
   fallback — do not touch `clui117*` beyond moving the rendered row.
5. Cache stamps: bump `app.js`, `app.css`, `icons.js` to the same new generation
   on all five root pages and update every test pin in one pass.
6. Independent review before merge (front-end state machine + layout).

## Acceptance (machine-checkable)

- Card DOM order is: identification → now → subject → terrain → actions
  (assert the `data-layer` markers or the element order directly).
- Exactly ONE bell per card; opening it still lists every subject's reminder
  options.
- `≥ 24 km` renders without 「資料上限」 in the visible text; the tooltip carries it.
- The headline subject line's computed `font-size` is strictly larger than the
  now row's, and it carries the state tint + left bar.
- Elevation and the astronomical values never share a line with the now row
  (assert their common ancestor differs, or that their `offsetTop` differ).
- Cross-card alignment: within one rendered row of cards, the four layers and
  the action row align within 1 px (real Chrome, 1440×900 and 393×852).
- Screenshots at 1440×900 and 393×852 in zh-TW/en for each of: normal card,
  foggy card, card with no subject (資料不足), and a two-card row showing the
  alignment.
