# B157 — Himawari-9 scheduled WeatherGrid publish

## Goal

Promote the proven B156 Himawari Taiwan browser bundle from CI artifact to a
current snapshot under `weathergrid/`.

This batch still makes **no public WeatherGrid UI change**. It only establishes
the provider-owned refresh/publish path first.

## Schedule

Himawari Full Disk observations repeat every 10 minutes. NOAA Level-2 cloud
products arrive after processing/distribution latency, so the workflow polls
every 10 minutes and selects the newest complete same-slot CMSK + CHGT pair.

```text
cron: */10 * * * *
```

GitHub Actions scheduling is best-effort; the observation timestamp in the
bundle, not the workflow start time, remains the authoritative data time.

## Freshness gate

Before publishing, B157 requires:

- `source_kind = observation`
- Himawari-9 / AHI source identity
- 276 × 301 regular Taiwan grid
- both observation fields present
- no API key requirement
- observation end time no more than 90 minutes old
- p99 nearest-neighbour distance <= 5 km
- zero target cells beyond the declared 5 km maximum distance

If the current refresh or freshness validation fails, the workflow removes
the public Himawari files instead of silently leaving an old observation
selectable.

## Published files

- `weathergrid/himawari9_tw_cloud_browser.json`
- `weathergrid/himawari9_tw_cloud_qc.json`

## Cost / credentials

The workflow uses anonymous NOAA NODD / AWS Open Data reads. It does not use:

- `OPEN_METEO_API_KEY`
- AWS access-key secrets
- a paid JMBSC feed

## Next step

After one successful main-branch publish and Pages deployment, add a separate
WeatherGrid **Observed / Himawari-9** mode with:

- observed cloud mask
- cloud-top height
- observation timestamp and age

The UI must not label these as forecast low/mid/high cloud percentages.
