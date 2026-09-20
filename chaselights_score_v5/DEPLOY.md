# ChaseLights Score V5 部署

1. 用 V5 的 5 個核心檔案覆蓋專案：
   - `index.html`
   - `regions.py`
   - `fetch_data.py`
   - `analyze_weather.py`
   - `get_weather.py`

2. Workflow 對每個地區執行：
   ```bash
   python analyze_weather.py tw
   python analyze_weather.py jp
   python analyze_weather.py us
   ```

3. 確認部署產物包含以下 6 個 JSON：
   - `tw_weather.json`
   - `tw_weather_details.json`
   - `jp_weather.json`
   - `jp_weather_details.json`
   - `us_weather.json`
   - `us_weather_details.json`

4. V5 前端不再需要 `*_weather_zh-TW.json / *_en.json / *_ja.json`。若 GitHub Workflow 有明確列出舊檔名，請把 commit / upload 規則改成上述 6 個新檔。

5. 第一次開啟某地區會下載 summary；之後重新整理會先顯示 Cache Storage 中的資料，再背景 revalidate。第一次點「96H 明細」才會下載該地區 details。

6. 升級後若瀏覽器仍使用舊 Service Worker / CDN 快取，做一次 hard refresh。V5 Cache Storage 名稱為 `chaselights-v5-weather`，schema 不符的 V4 資料會被忽略。
