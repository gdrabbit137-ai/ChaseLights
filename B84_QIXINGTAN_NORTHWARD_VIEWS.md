# B84 — 七星潭北望山海與貼山雲分流

## 問題

B83 已新增 `tw-036-P03`「七星潭北望清水山／清水斷崖＋貼山雲帶」，但 2026-09-28 13:00 的現場案例仍揭露兩個不同層次：

1. 「北方山海本身值得拍」是較穩定的 Place-specific 題材。
2. 「北方山區剛好形成貼山雲帶」是更細、較難由粗網格預報的可變條件。

如果只保留 P03，粗網格沒有抓到局部雲帶時，系統會把整個北望山海場景一起判成不成立。這與現場照片不符。

## 官方地點證據

- 交通部觀光署七星潭頁面明確記錄：在七星潭「可以遠眺清水斷崖」。
  - https://www.taiwan.net.tw/m1.aspx?id=9488&sno=0001124
- 臺灣國家公園文章直接描述：從七星潭海岸隔海灣向北眺望，太平洋、清水斷崖與向上延伸的清水山完整出現在眼前；同文亦記錄清水山山頂常聚積雲霧。
  - https://www.taiwan.nps.gov.tw/home/zh-tw/quarterly/7933/6910

因此「北望清水斷崖／清水山山海遠眺」與「貼山雲帶」都具有 Place-specific 依據，但 runtime 不應把兩者視為同一條件。

## Opportunity 分流

### tw-036-P03 — 貼山雲帶

目標：海岸本身清楚、北方山區出現比拍攝點更強的低雲／高濕／能見度下降訊號，且至少部分山體仍可能可讀。

判定仍採較嚴格的 directional mountain-cloud contract。若北方 proxy 沒有直接雲訊號，不高分宣稱貼山雲已成立。

### tw-036-P04 — 北望清水斷崖／清水山山海遠眺

目標：即使沒有明確貼山雲訊號，只要海岸與北向多個高地 proxy 保持可讀，仍可把這個已查證的山海題材列為有效拍攝機會。

Runtime：

- Camera Zone visibility 必須至少 12 km。
- Camera Zone 不可是高低雲＋高濕的白牆狀態，也不可有明顯降雨。
- 採 350° / 5° / 20°、8 / 15 / 22 km 的北向多點 proxy。
- 只納入比相機格點至少高 250 m 的高地樣本。
- 至少 2 個高地樣本、跨至少 2 個方位必須保持：
  - visibility >= 8 km
  - low cloud <= 80%
  - 非霧 weather code
  - 無明顯降雨
- 格點只代表廣角環境 proxy，不保證每一段山稜完全無雲。

## B84 calibration diagnostics

P03 額外輸出 compact diagnostics：

- elevated target 最大低雲量
- elevated target 最大 RH
- elevated target 最低 visibility
- elevated target 最大高程
- Camera Zone 溫度／露點推算的 LCL proxy
- 有多少北向高地樣本高於 LCL proxy，以及跨多少方位

注意：目前 `cloud_base_agl` 是依溫度／露點估算的 planning-grade LCL proxy，不是雲底實測值。B84 只把它用於後續校正觀察，不直接把「地形高於 LCL」升格成貼山雲已成立。

## 2026-09-28 13:00 field case

現場非識別化驗證：

- 七星潭往北
- 海岸與海面非常通透
- 北方山體仍可辨
- 山腰／山區有局部低雲帶
- 拍攝前後 ChaseLights 點位資料約為 27 km visibility、低雲約個位數%、LCL proxy 約 0.7 km AGL

預期新行為：

- P03 若粗網格沒有抓到方向性雲訊號，可以維持「貼山雲未直接支持」。
- P04 應在北方高地多點仍可讀時成立，避免把整個白天山海場景錯判為「只能看日出題材」。

這樣把「題材存在」與「局部雲形是否被模型解析」分開處理。
