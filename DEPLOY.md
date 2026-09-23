# ChaseLights R4 Place-first Beta deployment

The public R4 beta keeps the legacy weather score/ranking as the primary production score while exposing the new Place → Photography Opportunity model as preview metadata.

Deployment flow:
1. Merge/fast-forward the tested release branch into `main`.
2. A main-branch push touching R4 core files automatically triggers **Update ChaseLights Weather Data**.
3. Confirm the six weather JSON files are regenerated with schema 9 and contain `opportunities`; hourly detail rows may include `opportunity_runtime`.
4. The browser cache namespace is `chaselights-v10-r4-preview`, so old schema-9 JSON without Opportunity metadata is not reused.
5. R4 preview statuses are diagnostic only. Unsupported/pending Opportunities do not receive a new production score.
6. `tw-063` is retired and must not appear in the active catalog.

# ChaseLights V5.4 deployment

1. Replace `index.html`, `regions.py`, `fetch_data.py`, `analyze_weather.py`, and keep/update `update_weather.yml`.
2. Run **Update ChaseLights Weather Data** manually once. New JSON uses `schema_version: 9`.
3. Confirm the six files exist: `tw_weather.json`, `tw_weather_details.json`, `jp_weather.json`, `jp_weather_details.json`, `us_weather.json`, `us_weather_details.json`.
4. Hard refresh once (`Ctrl+Shift+R`). The front-end accepts schema 7–9 during deployment, so the site should not go blank while JSON rolls over.
5. Bortle classes are static planning estimates; no extra API or secret is required.

# ChaseLights V5.2 deployment

1. Replace these core files in the repository:
   - `index.html`
   - `regions.py`
   - `fetch_data.py`
   - `analyze_weather.py`
   - `get_weather.py`

2. Keep the V5 workflow (`update_weather.yml`). No output filenames changed.

3. Manually run **Actions → Update ChaseLights Weather Data → Run workflow** once after deploying V5.2.
   This is required because coordinates/themes changed and `schema_version` is now **7**.

4. Confirm these six files are regenerated:
   - `tw_weather.json`
   - `tw_weather_details.json`
   - `jp_weather.json`
   - `jp_weather_details.json`
   - `us_weather.json`
   - `us_weather_details.json`

5. After the workflow succeeds, do one hard refresh (`Ctrl + Shift + R`). The V5.2 cache is `chaselights-v7-weather`.


## V5.3 deployment
This release uses `schema_version: 8`. Upload the updated `index.html`, `fetch_data.py`, `analyze_weather.py`, and `regions.py`, then run the weather workflow once so all six JSON files are regenerated as schema 8. A hard refresh is recommended after deployment because the browser cache namespace changed to `chaselights-v8-weather`.
