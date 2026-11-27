# CL-UI-115 — Experience and visual unification (owner spec, 2026-11-27)

Owner-reported. Three separate defects, one ticket because they all change the same
card surface (`assets/app.js` + `assets/app.css`). Ship as three sub-commits on one
branch so each can be reviewed and reverted independently.

Read this whole document before editing. The constraints in §4 are the ones that
have already burned us.

---

## 1. Metric icons: one SVG library for every device

### What the owner sees

The eye glyph used for visibility looks sharper on the desktop web page than on the
phone. The same is true for the other metric symbols — the phone falls back to the
system emoji font, the desktop draws a different-looking glyph.

### What is actually in the code (measured, not assumed)

- `assets/app.js` contains **0** `<svg>` elements. Every metric and weather symbol is
  an emoji literal baked into a string table:
  - `WMO_ICONS` (line 634) — 29 weather codes, e.g. `45:'🌫️'`, `63:'🌧️'`.
  - The subject label table (lines 97–99) — 23 subjects × 3 languages, e.g.
    `cloud_sea:'☁️ 雲海'`.
  - `☁️` cloud-base chip at line 2343.
- There is no icon font and no sprite. `assets/` contains only `favicon.svg`.

So the inconsistency is **not** two different code paths — it is one code path whose
glyph is rendered by the platform emoji font. Chrome on Windows/macOS, Android, and
iOS all draw different artwork for the same codepoint, and the mobile emoji font is
the softer one the owner dislikes.

### Required change

Introduce a small inline SVG icon set and use it everywhere a metric/weather symbol
is currently an emoji:

1. New file `assets/icons.js` exporting a frozen map `CL_ICONS = { key: '<svg …>' }`
   with `currentColor` strokes only (no hard-coded fills) so CSS can tint them.
   Required keys at minimum: the 29 WMO codes in `WMO_ICONS`, the 23 subject keys in
   the label table, plus `visibility`, `cloud`, `fog`, `wind`, `humidity`,
   `temperature`, `elevation`, `azimuth`, `sunrise`, `sunset`, `moon`, `star`.
2. Replace every emoji occurrence in `WMO_ICONS`, the subject table and the cloud-base
   chip with a lookup into `CL_ICONS`. Keep the emoji as a **fallback only** if the
   key is missing, so an unknown code still renders something.
3. Size and colour from CSS: `.cl-icon { width:1em; height:1em; vertical-align:-0.125em;
   stroke:currentColor; fill:none }`. No inline width/height in the SVG strings.
4. Accessibility: decorative icons get `aria-hidden="true"`; an icon that is the only
   carrier of a metric name must keep a text label next to it (the existing labels
   already do — do not remove them).
5. Verify on real Chrome at 1440×900 and 393×852 in zh-TW/en/ja: no emoji glyph may
   remain in a metric or weather position. Screenshot both widths into the report.

### Acceptance

- `grep -c '🌫️\|🌧️\|☁️\|👁' assets/app.js` drops to 0 outside the fallback branch.
- The same metric renders byte-identical markup at 1440px and 393px (assert the
  rendered `outerHTML` of one metric chip in both viewports).
- No layout shift: the icon box is `1em` and the baseline offset is fixed.

---

## 2. Information architecture: card shows *now*, taps split into two panels

### What the owner asked for

- **Card surface**: keep one line of "today's headline subject + window"
  (e.g. `夕陽 17:20 · 夜景 02:00`). The weather row must show the **current hour**
  (`now_hour`) live weather — temperature, condition, visibility — and turn the
  condition orange when it is foggy right now. Remove the duplicated yellow
  azimuth-dot row at the card bottom (already owned by CL-UI-46, do not duplicate).
- **Tap the card body** → open the "historical weather + next 7 days forecast" panel.
- **Tap the subject button** → open the "subject windows" panel: which subjects this
  place supports, and for each subject the qualifying window today and on the
  following days.

### Why this is not a CSS change

Today the card body and the subject button both open the same weather modal; the
subject button is a shortcut into the same dialog. Splitting them means two distinct
panels with two distinct data sources:

| Panel | Source | Existing artefact |
|---|---|---|
| Weather (history + 7-day) | evaluation bundle day rows + hourly details | `evaluations-latest.json`, `weather_details/` |
| Subject windows | subject-cards rows (`suitable[].window`) | `subject-cards-<stamp>.json` |

Both already exist and are already fetched. The work is to route two different
renderers to two different triggers, not to invent a data source.

### Required change

1. Card weather row switches from "the day's representative hour" to `now_hour`
   (the current hour in the place's timezone, clamped to the forecast range). If the
   current hour is outside the forecast range, fall back to the first forecast hour
   and label it with the hour, never silently show another day's weather.
2. Fog right now (`fog_visibility` FAIL or `in_cloud_fog` FAIL at `now_hour`, or
   `visibility < 1 km`) tints the condition chip orange and adds the reason text.
3. Card body click → weather panel. Subject button click → subject-window panel.
   Keep the existing keyboard reachability: both must be focusable and openable with
   Enter/Space, and the panel must return focus to its trigger on close.
4. The subject-window panel lists, per supported subject: today's window, and the
   next days' windows as a compact per-day list. A subject with no qualifying window
   today must say so explicitly (資料不足 / 今日無符合時段), never render an empty row.
5. Both panels must read from the **same** single-source helpers the card already
   uses (`v2DayQualifiedSet()` family). Do not re-derive verdicts in the panel.

### Acceptance

- Card weather row equals the bundle's `now_hour` row for the same place (assert the
  temperature and WMO code match, not just the presence of text).
- A foggy now_hour renders the orange state (assert computed style, not a class name).
- Card body opens the weather panel; subject button opens the subject panel; the two
  panels are never the same element (assert distinct `data-panel` values).
- Every subject row in the subject panel carries a window or an explicit
  "no window today" string — assert zero empty rows across all 459 places.
- Focus returns to the trigger on close.

---

## 3. Desktop first-screen control bar slimming

Owned by **CL-UI-46** (already in flight). Do not re-implement here. Requirements, for
the record:

- When the member has no private places (`私人 0`), hide the whole
  `不限來源 / 官方 / 私人` filter row; show it only when at least one private place exists.
- Condense the place-count hint that currently appears three times on the first screen
  into one.

CL-UI-115 tracks only §1 and §2. If CL-UI-46 lands first, §3 is closed there.

---

## 4. Constraints (these have already caused CI failures)

1. **Whitelist**: `assets/icons.js` (new), `assets/app.js`, `assets/app.css`,
   `assets/app.css` consumers, and the tests under `apps/web-v2/tests/` that pin these
   behaviours. Nothing else. No `data/**`, no `packages/**`, no HTML pages.
2. **Never weaken an assertion.** Existing card/modal tests must keep passing as-is.
   If a test pins the old "card body opens the weather modal" behaviour, extend it to
   the new contract rather than deleting the assertion.
3. **Cache stamps**: `assets/app.js` and `assets/app.css` are referenced with `?v=`
   stamps from seven root pages **and** from `apps/web-v2/`. Bump the generation in
   every reference and update the pins in the tests that assert the stamp. Missing the
   `apps/web-v2/` copies is the exact mistake that reddened CI before.
4. **Single source of truth**: the card, the weather panel and the subject panel must
   read verdicts from the same helper. The audit that created this backlog found 1,211
   place-days where the card and the modal disagreed because two renderers re-derived
   the same judgement. Do not add a third.
5. **Independent review**: this ticket changes a front-end state machine (two triggers,
   two panels). Per the standing rule, a separate reviewer must read the diff before
   merge, with no access to the author's reasoning.

---

## 5. Evidence from the audits that produced this ticket

- Visual/RWD audit (45 screenshots, 1440×900 and 393×852, zh-TW/en/ja, °C/°F):
  - "我的" page was not translated in en/ja (fixed in CL-I18N-12A).
  - Weather map was half Chinese in en/ja (fixed in CL-I18N-12B).
  - Mobile map controls were pushed off-screen (fixed in CL-I18N-12B).
  - English mobile forecast text was truncated (fixed in CL-I18N-12C).
  - Legend overlapped the bottom bar on mobile (fixed in CL-I18N-12C).
- Photographer-persona audit: recommendation badges were meaningless — "recommended"
  included fog and no-data cases; night golden hours were classified as "not
  recommended" (fixed in CL-PHYS-03); three key inputs were missing (moon phase,
  subject azimuth, travel time) — see `photographer-decision-inputs.md`.
- Physics audit: white-wall recommendations at 25 places / 155 hours (fixed in
  CL-PHYS-03); card↔modal hour disagreement at 1,211 place-days (fixed in CL-UI-45).

## 6. Sequencing

`CL-UI-46` (control bar + duplicate azimuth row) is in flight and touches the same two
files. **Do not start §1 or §2 until CL-UI-46 is merged**, then branch from the merged
main. Two branches editing `assets/app.js` in parallel is the file-collision the
standing rules forbid.
