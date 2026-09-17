# 📷 ChaseLights 專案開發文件 — UX 流程與天氣應用

> 開發者視角：設計目的、使用者流程、核心 API、天氣參數
> 更新日期：2026/9/13

---

## 1. 專案定位：為什麼設計 ChaseLights？

### 1.1 解決的問題

台灣／日本／阿拉斯加／美國的攝影愛好者有一個共同痛點：

> 「我知道某某景點很出名，但**今天去到底能不能拍？**」

傳統解法是：
1️⃣ 上氣象局網站看天氣 → 看不懂雲層圖
2️⃣ 上景點 IG 看照片 → 昨天拍的，不代表今天
3️⃣ 問社團前輩 → 很多人答非所問

**ChaseLights 的解法：**
直接用 `Open-Meteo API` 抓未來 3 天的氣象預報，套進「攝影評分公式」：
- 能見度、雲量、降雨、黃金時段 **→ 量化成 0-100 分**
- 依景點屬性（山區/海岸/瀑布/森林）**用不同標準**
- 前端輸出「景點排名 + 拍攝提示」

### 1.2 目標使用者

- **認真風景攝影師**：中強度，每日用，要準確天氣數據
- **假日攝影玩家**：輕度，週末用，想知道去哪裡
- **出國攝影者**：掃國際區域（日本/阿拉斯加/美國），快速知道當地天氣

---

## 2. 使用者流程（User Flow）

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  開啟網頁     │───▶│  選擇地區     │───▶│  瀏覽景點排名  │
│  /summary    │    │  TW/JP/AK/US │    │  今日/明日/後天 │
└──────────────┘    └──────────────┘    └──────────────┘
                          │                      │
                          ▼                      ▼
                   ┌──────────────┐    ┌──────────────┐
                   │  切換到地圖   │    │  點擊景點卡片  │
                   │  /?region=jp │    │  查看詳細資訊  │
                   └──────────────┘    └──────────────┘
```

### 2.1 三個主要頁面

| 頁面 | 路由 | 功能 |
|:----|:----|------|
| **景點摘要** | `/summary` | 各區今日/明日/後天最佳 30 個景點排名，含評分、題材、tip |
| **能見度地圖** | `/` | Leaflet 地圖 + Canvas 能見度熱力圖 overlay，24hr 動畫播放 |
| **API 資料端** | `/api/best-spots?region=tw&day=0` | 前端 AJAX 拉取的 JSON 資料 |

### 2.2 地區切換流程

```
使用者點擊「🇯🇵 日本」按鈕
  → 呼叫 Frontend switchRegion('jp')
  → 更新地圖中心 + zoom
  → fetch /api/forecast?region=jp（地圖用網格資料）
  → fetch /api/best-spots?region=jp（摘要頁用景點排名）
  → 渲染對應 UI
```

支援地區（`regions.py` 定義）：

| Code | 名稱 | 網格範圍 | 景點數 | 地圖中心 |
|:----:|:----|:--------:|:-----:|:--------:|
| `tw` | 🇹🇼 台灣 | 21.5-26.5N, 117.5-122.5E | 69 | 23.8, 120.9 |
| `jp` | 🇯🇵 日本 | 30-46N, 129-146E | 35 | 36.0, 138.0 |
| `ak` | 🏔️ 阿拉斯加 | 54-71N, 180-130W | 30 | 63.0, -150.0 |
| `us` | 🇺🇸 美國 | 24-50N, 125-66W | 40 | 39.8, -98.0 |

### 2.3 資料更新流程（後端）

```
build_cache.py <region>
  │
  ├─ 從 REGIONS[region]["spots"] 取得所有景點座標
  ├─ 從 REGIONS[region]["grid_bounds"] 取得網格範圍
  │
  ├─ 並行呼叫 Open-Meteo API（ThreadPoolExecutor）
  │   └─ GET https://api.open-meteo.com/v1/forecast
  │      params: latitude, longitude
  │               &hourly=relative_humidity_2m,cloud_cover_low,...
  │               &daily=sunrise,sunset,weather_code,...
  │               &timezone=auto
  │               &forecast_days=3
  │
  └─ 寫入 .cache/forecast_{region}.json
```

---

## 3. 核心架構（Architecture Overview）

```
┌─────────────────────────────────────────────────────────┐
│                   前端 (Browser)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐   │
│  │ index.html  │  │ summary.html │  │ static/       │   │
│  │ Leaflet 地圖│  │ 景點卡片列表 │  │ style.css     │   │
│  │ Canvas 熱力 │  │ 分頁切換    │  │               │   │
│  └──────┬──────┘  └──────┬───────┘  └───────────────┘   │
│         │                │                               │
│         ▼                ▼                               │
│    fetch JSON       fetch JSON                            │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP
┌─────────────────▼───────────────────────────────────────┐
│          後端 Flask (Python)                              │
│                                                          │
│  app.py (795行)                                          │
│  ├─ /              → index.html (能見度地圖)              │
│  ├─ /summary       → summary.html (最佳景點)             │
│  ├─ /api/forecast  → 網格資料 JSON（給地圖用）            │
│  ├─ /api/best-spots→ 景點排名 JSON（給摘要用）            │
│  └─ /api/refresh   → 觸發 build_cache.py                 │
│                                                          │
│  輔助模組：                                              │
│  ├─ regions.py     → 4 地區定義（座標/網格/景點）        │
│  ├─ build_cache.py → 呼叫 Open-Meteo API 產生快取        │
│  ├─ fetch_data.py  → Open-Meteo HTTP 客戶端              │
│  └─ scheduler.py   → 定時自動更新快取（每小時）           │
│                                                          │
│  快取資料夾                                              │
│  └─ .cache/                                             │
│     ├─ forecast_tw.json  → 台灣快取                      │
│     ├─ forecast_jp.json  → 日本快取                      │
│     ├─ forecast_ak.json  → 阿拉斯加快取                   │
│     └─ forecast_us.json  → 美國快取                      │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Open-Meteo API 叫用細節

### 4.1 請求網址

```
GET https://api.open-meteo.com/v1/forecast
    ?latitude={lat}&longitude={lon}
    &hourly=relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,
            wind_speed_10m,visibility,weather_code,precipitation_probability,
            temperature_2m,dew_point_2m
    &daily=sunrise,sunset,weather_code,precipitation_sum
    &timezone=auto
    &forecast_days=3
```

### 4.2 使用到的 hourly 欄位

| 欄位 | 單位 | 在評分中的用途 |
|:----|:----:|-------------|
| `visibility` | m | 能見度評分（30分權重） |
| `cloud_cover_low` | % | 低雲量 — 雲海判定（<2km） |
| `cloud_cover_mid` | % | 中雲量 — 閃電/雨層 |
| `cloud_cover_high` | % | 高雲量 — 火燒雲判定（5-10km） |
| `relative_humidity_2m` | % | 濕度 — 雲海/晨霧判定 |
| `wind_speed_10m` | km/h | 風速 — 雲海穩定度 |
| `weather_code` | WMO code | 降雨排除 |
| `precipitation_probability` | % | 降雨機率評分（20分權重） |
| `temperature_2m` | °C | 僅顯示，不列入評分 |
| `dew_point_2m` | °C | 用於計算雲底高度（(T-Td)×125） |

### 4.3 使用到的 daily 欄位

| 欄位 | 用途 |
|:----|------|
| `sunrise` | 日出時間 → 黃金時段判定 |
| `sunset` | 日落時間 → 黃金時段判定 |
| `weather_code` | 跨日天氣參考 |
| `precipitation_sum` | 日總降雨量參考 |

---

## 5. 攝影評分公式（完整拆解）

### 5.1 總分結構（0-100）

```
能見度 30分 ─ 空氣通透度
雲量   20分 ─ 依題材類型不同標準
降雨   20分 ─ 降雨機率
時段   30分 ─ 黃金時段 + 白天優先
────────────────────────
總分  100分
```

### 5.2 詳細評分規則

#### ① 能見度（30分）

```
vis > 30km → 30分
vis > 20km → 25分
vis > 15km → 20分
vis > 10km → 15分
vis >  5km →  8分
vis >  2km →  4分
其他       →  1分
```

#### ② 雲量（20分）— 依題材類型切換

**山區（mountain）：**
```
低雲>60% + 濕度>85% + 風<15km/h → 20分（🔥雲海絕佳）
總雲量<30%  → 18分（晴空萬里）
總雲量<50%  → 12分
低雲>70%   → 10分
其他        →  5分
```

**海岸（coastal）：**
```
高雲30-70% + 低雲<20% → 20分（🔥火燒雲）
總雲量<30% → 18分
總雲量<60% → 12分
其他       →  5分
```

**瀑布（waterfall）：**
```
總雲>70% + 低雲>50% → 20分（漫射光完美）
總雲>50% → 15分
總雲<20% →  8分
其他     → 12分
```

**森林（forest）：**
```
濕度>85% + 總雲>50% → 20分（晨霧夢幻）
總雲>40% → 15分
總雲<20% →  5分
其他     → 12分
```

**通用（general）：**
```
總雲<30% → 20分
總雲<60% → 15分
總雲<85% →  8分
其他     →  3分
```

#### ③ 降雨機率（20分）

```
預報降雨機率 < 10% → 20分
             < 30% → 15分
             < 50% → 10分
             < 70% →  5分
             其他   →  2分
```

大雨/雷雨時段直接排除（WMO code 61,63,65,82,95,96,99 + pop>70%）

#### ④ 時段（30分）

```
黃金時段（日出±1hr 或 日落±1hr） → 20分
白天（非深夜）                   → 10分
夜晚（自然景觀型）               →  2分
```

**深夜排除規則：**
- 自然景觀型（mountain/coastal/waterfall/forest）：`t_h < 5 或 t_h >= 19` 直接過濾
- 通用型（general）：夜間可拍城市夜景→不排除

**加分項：**
```
風速<5km/h +（毛毛雨或濕度>85%）→ +5分（鏡像倒影條件）
```

### 5.3 題材分類中文標籤

由 `get_genre_label()` 函數根據條件輸出：

```python
# 山區雲海 → 低雲>60%+濕度>85%+風<15
# 火燒雲日出/夕陽 → 高雲30-70%+低雲<20%+黃金時段
# 金色山脈 → 山區+黃金時段+中高雲量
# 夢幻晨霧 → 森林+高濕度
# 溪瀑慢速 → 瀑布+漫射光
# 一般攝影 → 其他情況
```

---

## 6. 前端元件（UI Components）

### 6.1 摘要頁（summary.html）

```
Header: 地區按鈕 (TW/JP/AK/US) + 語言切換 (中文/English)
                │
Paginator: 今日分頁 | 明日分頁 | 後天分頁
                │
Spots List (最多 30 張卡片)
  ├─ 景點名稱 + 評分 + 題材 badge
  ├─ 資訊格：海拔 | 能見度 | 氣溫 | 降雨%
  ├─ 最佳時間：時段 + 日出/日落
  └─ 拍攝提示：時段感知 tip（自動切日出/日落版）
```

### 6.2 地圖頁（index.html）

```
Header: 同上 + 地圖/景點切換按鈕
                │
Leaflet 地圖
  ├─ 圖層：OpenStreetMap 底圖
  ├─ 覆蓋：Canvas 能見度熱力圖（colormap: 紅→黃→綠→藍→紫）
  ├─ 控制：播放/暫停按鈕 + 時間滑桿 + 時間標籤
  ├─ 圖例：能見度色階條
  └─ 圖示：標記各景點位置
```

---

## 7. 知識庫體系（Knowledge Base）

地點：`D:\Dick\Project\ChaseLights\Knowledge Base\`

```
共用型_攝影知識庫.md         7.5 KB   攝影常識・技巧・天氣條件
台灣攝影景點指南.md          25 KB    台灣  69 景點（統一格式）
日本攝影景點指南.md          11 KB    日本  35 景點
阿拉斯加攝影景點指南.md      8.0 KB   阿拉斯加 30 景點
美國攝影景點指南.md          11 KB    美國  40 景點
```

### 7.1 地區型統一格式

```markdown
### 景點名稱
| 項目 | 內容 |
|------|------|
| **座標** | XX.XXX°N, YY.YYY°E |
| **海拔** | X,XXXm |
| **區域** | 縣市／國家公園 |
| **題材** | 🥇 日出、雲海、火燒雲 |
| **最佳天氣** | 雨後放晴、能見度>15km |
| **黃金時刻** | 日出前30min、日落前40min |
| **建議焦段** | 16-35mm、70-200mm |
| **拍攝建議** | 題材・器材・條件（時段感知用） |
| **備註** | 交通、難度、申請等 |
```

### 7.2 時段感知 Tip 系統

`app.py` 中的 `tip_for_day()` 函數流程：

```
使用者選「今日」分頁
  → API 回傳 each spot 的 best_time, sunrise, sunset
  → tip_for_day() 讀取 best_time 的小時
  → 判斷是否接近日出（±2hr）或日落（±2hr）
  → 從 TIME_AWARE_TIPS 取出對應版本（日出版/日落版）
  → 若不在 TIME_AWARE_TIPS，fallback 到 PHOTO_TIPS
  → 前端 render tip_today 欄位
```

---

## 8. 評分降效機制

### 8.1 大雨排除

```python
heavy_rain_codes = (61, 63, 65, 82, 95, 96, 99)  # WMO code
if wcode in heavy_rain_codes and pop > 70:
    continue  # 跳過此時段不評分
```

### 8.2 深夜排除（自然景觀型）

```python
is_night = t_h < 5 or t_h >= 19
night_exempt = {"general"}  # 城市夜景例外
if is_night and scene_type not in night_exempt:
    continue
```

### 8.3 總分上限

```python
score = min(best_score, 100)  # 最高 100 分
```

---

## 9. 海拔校正

`Open-Meteo` 的解析度約 **7km 網格**，在山區誤差可達 **900m**。對照表 `TRUE_ELEVATIONS` 負責校正：

```python
TRUE_ELEVATIONS = {
    "池有山": 3303,    # API 可能給 2400（溪谷）
    "南湖大山": 3742,  # API 可能給 3200
    "玉山主峰": 3952,  # API 可能給 3200
    # ... 共 30+ 筆
}
```

---

## 10. 部署與維運

### 10.1 本地開發

```bash
cd weather_web
python build_cache.py tw      # 先抓快取（台灣）
python build_cache.py jp      # 日本
python build_cache.py ak      # 阿拉斯加
python build_cache.py us      # 美國
python app.py                 # 啟動 Flask → localhost:5000
```

### 10.2 生產部署（參考 DEPLOY.md）

```
Cloudflare CDN → Cloudflare Workers → VPS (DigitalOcean $6/月)
                                         └─ Waitress + Flask
```

### 10.3 自動更新機制

`scheduler.py` 使用 `subprocess` 每小時執行一次 `build_cache.py`，確保：
- 快取不超過 1 小時
- 每日 sunrise/sunset 隨日期更新
- 多區域輪流更新

### 10.4 Cloudflare Tunnel（開發用）

```bash
cloudflared tunnel --url http://localhost:5000
```
每次啟動產生臨時 URL，如 `https://xxx.trycloudflare.com`

---

## 11. 重要設計決策

| 決策 | 選擇 | 理由 |
|:----|:----|------|
| **題材分類** | 公式（非 AI） | 0 成本、可預測、易除錯 |
| **評分方式** | 四項加權（30+20+20+30） | 直觀、易調整 |
| **時段感知** | ±2hr 判斷 | 誤差容忍，覆蓋黃金時段前後 |
| **快取策略** | 預先計算 + JSON 檔 | 避免每次請求都 call API |
| **地區切換** | 前端 fetch 不同 JSON | 後端 RESTful，前端純渲染 |
| **地圖熱力** | Canvas 覆蓋 + Leaflet | 自訂 colormap，不依賴 plugins |

---

> 📌 本文件由開發者視角撰寫，適合新成員快速掌握專案架構。
> 對應知識庫檔案位於 `Knowledge Base/` 目錄下。