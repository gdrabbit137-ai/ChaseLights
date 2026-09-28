# B83 — 七星潭北望清水山／清水斷崖貼山雲帶

## 目的

修正七星潭在白天只剩「日出」與「星空／銀河」可評分的 Coverage gap。

2026-09-28 13:00 的現場驗證案例顯示：七星潭海岸本身晴朗、海面與天空通透，但北方山區有明顯貼山低雲／山腰雲帶，山峰仍部分可辨。當時 ChaseLights 的點位預報本身其實合理（高能見度、海岸低雲少、低雲底），但因 tw-036 只有日出與星空兩個 Opportunity，13:00 仍以「日出時段不成立」得到低分。

B83 不調高「日出」分數，而是新增一個被地點證據支持的獨立 Photography Opportunity。

## Place-specific evidence

依 RESEARCH_EVIDENCE_SPEC_R4_2：

- 交通部觀光署七星潭官方頁明確記錄「可遠眺清水斷崖」。
- 臺灣國家公園官方文章直接描述從七星潭海岸隔海灣向北，可同時看見太平洋、清水斷崖與向上延伸的清水山；同文亦記錄清水山山頂常聚積雲霧。
- 花蓮縣官方攝影專欄把七星潭的海、雲與中央山脈列為可拍景觀。

因此「七星潭北望山海＋山區雲帶」是 Place-specific 已查證題材，不是由地形或天氣反推生成。

來源：

1. https://www.taiwan.net.tw/m1.aspx?id=9488&sno=0001124
2. https://www.taiwan.nps.gov.tw/home/zh-tw/quarterly/7933/6910
3. https://tour-hualien.hl.gov.tw/jp/News_Content.aspx?n=288&s=8856

## 新增 Opportunity

- ID: `tw-036-P03`
- 名稱：七星潭北望清水山／清水斷崖＋貼山雲帶
- Theme compatibility: `mountain_view`
- Formula: `needs_spatial_weather_module`
- Geometry: broad northward directional sector, not exact alignment
- Evidence grade: A

## Runtime contract

單一七星潭格點不能判斷「北方山區有雲、拍攝點本身清楚」這種空間反差，所以 B83 使用 required directional spatial weather。

Camera Zone：

- 代表座標：24.031426, 121.627170
- 僅作七星潭月牙灣代表 Camera Zone，不主張精確腳架點

Target proxy：

- 方位：350° / 5° / 20°
- 距離：8 / 15 / 22 km
- 必須是相對拍攝點至少高 250 m 的 Open-Meteo DEM 格點
- 這些都是 broad environmental proxies，不是精確清水山山峰或斷崖交會點

成立條件：

1. 拍攝點能見度至少 8 km，且不在明顯白牆／大雨。
2. 至少兩個高地 proxy 有低雲／高濕／相對能見度下降的雲帶訊號。
3. 至少兩個高地 proxy 的訊號必須明顯強於拍攝點。
4. 至少一個帶雲高地 proxy 仍保持 planning-grade 可讀狀態，避免把整片山區白牆當作優質山腰雲帶。
5. 正面判定只表示「方向性貼山雲候選」，不保證實際雲形、山峰露出比例或精確雲帶位置。

## 2026-09-28 field-validation case

非識別化現場案例：

- 地點：七星潭海岸
- 時間：2026-09-28 13:00 CST
- 相機方向：北
- 現場：海岸與海面清楚；北方山區形成低雲帶，部分山峰仍露出
- ChaseLights 拍攝前對 13:00 的點位預報：約 27 km visibility、9% low cloud、23% mid cloud、0% high cloud、約 687 m AGL cloud base、無降雨

這個案例用來驗證「單點天氣數值可以合理，但 Opportunity coverage 仍可能錯」；它不是未來預報的直接真值來源，也不取代 Place-specific 官方證據。

## 安全邊界

- 不把「高能見度 + 低雲底」單點組合直接解讀成山腰雲帶。
- 不把任一山區格點低雲直接宣稱為清水山實景。
- 不保證 exact cloud/ridge overlap。
- 不把全白山區當成理想貼山雲。
- 海岸浪況與現場安全仍需獨立確認。
