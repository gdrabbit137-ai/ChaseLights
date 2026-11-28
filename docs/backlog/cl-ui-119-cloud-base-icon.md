# CL-UI-119 — a distinct icon for the cloud-base chip (owner spec, 2026-11-28)

Owner-reported while reviewing the CL-UI-118 card: the now row's cloud-base chip
and the terrain row's elevation both draw the same "mountain" glyph, so

```
▲ 1743 m        ← cloud base (L2, now row)
▲  256 m        ← spot elevation (L4, terrain row)
```

read as the same quantity twice, with two different values. For a photographer
the first is "is the summit in cloud", the second is "how high is this place" —
they must not look alike.

## Required change

1. Add ONE new glyph to `assets/icons.js`: `cloud_base` — a cloud outline with a
   short upward arrow beneath it (currentColor strokes, no inline size, no
   hard-coded fill, same conventions as the rest of the set). It must be visually
   distinct from `cloud`, `fog`, `elevation` and `weather_overview` at 12 px and
   56 px.
2. The cloud-base chip in the now row (the first metric chip rendered by the card
   / the quick view) uses `cloud_base`. The elevation chip in the terrain line
   keeps `elevation` (the mountain glyph).
3. Any other surface that prints cloud base (the modal hourly metric rows, the
   quick view, the mobile timeline) uses the same key, so one quantity always
   carries one glyph.
4. Keep the text (`715 m`) and the existing tooltip (`tip_cloud_base`). No copy,
   verdict or i18n change.

## Acceptance

- `grep` shows the now-row cloud chip and the terrain elevation chip resolve to
  DIFFERENT icon keys.
- A DOM assertion on a real card: the two chips' `svg[data-cl-icon]` values differ,
  and the cloud chip's is `cloud_base`.
- The glyph-body hash test (CL-UI-118's set) still reports all keys distinct —
  `cloud_base` must not be a copy of `cloud` with a transform.
- Screenshot at 1440×900 and 393×852, zh-TW: one card showing `雲底 1743 m`
  above and `海拔 256 m` below, glyphs visibly different.

## Constraints

Whitelist: `assets/icons.js`, `assets/app.js`, `assets/app.css`, HTML stamp lines,
`apps/web-v2/tests/`. No `data/**`, no `packages/**`. Bump the shared cache
generation on all five root pages and update every test pin in one pass.
