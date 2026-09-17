# 📷 ChaseLights — 專案交接文件

> 撰寫日期：2026/9/14
> 當前版本：v0.1（git tag: v0.1）
> 開發者交接給 Claude-3-Haiku
> 專案路徑：`D:\Dick\Project\ChaseLights`

---

## 1. 專案概覽

ChaseLights 是一個攝影天氣助手網站，為攝影愛好者提供：
- **今日/明日/後日最佳景點排名**（0-100 評分）
- **天氣感知的拍攝建議**（依實際天氣動態調整 tip）
- **季節限定過濾**（非當季題材自動標示）
- **中英文雙語切換**
- **4 個國家、174個景點**的完整資料庫

### 核心技術

```text
Flask (Python) + Leaflet.js + Open-Meteo API
├─ 後端：app.py (905 行) — Flask 主程式
├─ 前端：home.html / summary.html / weather_guide.html
├─ 資料：regions.py (4 國定義) + build_cache.py (天氣快取)
└─ 排程：scheduler.py (每日 00/06/12/18 自動更新)
```

---

## 2. 專案目錄結構

```
D:\Dick\Project\ChaseLights\
├── weather_web\                   ← Web 主目錄
│   ├── app.py                     ← Flask 主程式（905行）
│   ├── regions.py                 ← 4 國區域/景點定義（227行）
│   ├── build_cache.py             ← 快取產生器（146行）
│   ├── scheduler.py               ← 自動排程（155行）
│   ├── fetch_data.py              ← Open-Meteo API 客戶端
│   ├── chaselights_UX_flow.md    ← UX 流程文件（463行）
│   ├── DEPLOY.md                  ← 部署指南
│   ├── static/
│   │   └── style.css              ← 共用樣式表
│   ├── templates/
│   │   ├── home.html              ← 首頁（地區選單）
│   │   ├── summary.html           ← 景點摘要頁
│   │   ├── weather_guide.html     ← 天氣對策指南
│   │   └── index.html             ← 能見度地圖（已停用）
│   └── .cache/                    ← 天氣資料快取
│       ├── forecast_tw.json       ─ 台灣
│       ├── forecast_jp.json       ─ 日本
│       ├── forecast_us.json       ─ 美國
│       ├── forecast_ak.json       ─ 阿拉斯加
│       └── update_status.json     ─ 各區更新時間記錄
├── Knowledge Base\                ← 知識庫
│   ├── 共用型_攝影知識庫.md       ─ 通用攝影知識
│   ├── 台灣攝影景點指南.md        ─ 台灣 69 景點
│   ├── 日本攝影景點指南.md        ─ 日本 35 景點
│   ├── 美國攝影景點指南.md        ─ 美國本土 40 + 阿拉斯加 10
│   └── 國家區域分類列表.md        ─ 子區域分類主檔
└── .git\                          ← git 版本控制（v0.1 tag）
```

---

## 3. 核心架構 — app.py 關鍵元件

### 3.1 路由一覽

| 路由 | 頁面 | 功能 |
|:----|:----|------|
| `/` | home.html | 首頁：各國地區選單 |
| `/summary?region=tw` | summary.html | 景點排名（支援 ?region= / ?sub= 參數） |
| `/weather-guide` | weather_guide.html | 天氣對策指南 |
| `/api/best-spots?region=tw` | JSON | 景點排名 API |
| `/api/forecast?region=tw` | JSON | 網格天氣資料 |
| `/api/update-status` | JSON | 各區更新時間 |
| `/api/refresh?region=tw` | - | 觸發重新抓取快取 |
| ~~`/map`~~ | ~~index.html~~ | ~~能見度地圖（已移除路由）~~ |

### 3.2 攝影評分公式（0-100）

```
能見度 30分  — vis > 30km → 30分, >20km → 25分, >15km → 20分 …
雲量   20分  — 依題材類型不同標準（mountain/coastal/waterfall/forest/general）
降雨   20分  — pop < 10% → 20分, < 30% → 15分 …
時段   30分  — 黃金時段(日出±1hr/日落±1hr) → 20分 + 白天 → 10分
加上風速<5 + 毛毛雨/高濕度 → +5分（鏡像倒影）
```

大雨（WMO code 61,63,65,82,95,96,99 + pop>70%）排除。
深夜（t_h<5 或 t_h>=19）自然景觀型排除。

### 3.3 天氣感知 Tip 系統

```python
def weather_tip(info, name, month=None):
    # 1. 若 best_genre 是特定天氣（非通用）→ 直接用天氣感知標題作為 tip
    #    例如：「🔥 火燒雲夕陽」「☁️ 雲海大景」「🏔️ 金色山脈」
    # 2. 若天氣通用 → 用時段感知靜態 tip（TIME_AWARE_TIPS → PHOTO_TIPS）
    # 3. 最後 SEASON_RULES 過濾季節性內容
```

### 3.4 季節過濾規則（SEASON_RULES）

14 條規則，每條格式：
```python
(["關鍵詞"], 起始月, 結束月, "過期替代文字")
```

| 關鍵詞 | 有效月 | 替代文字 |
|:------|:-----:|:---------|
| 金針花、六十石山 | 8-9月 | 🍂 縱谷風光 |
| 藍眼淚 | 4-9月 | 🌌 藍眼淚季為4-9月 |
| 極光、Aurora | 8-4月（跨年） | 🌌 極光季為8月～4月 |
| 鮭魚、Katmai | 7-9月 | 🐻 棕熊捕鮭季為7-9月 |
| 雪景、冠雪 | 12-3月 | ❄️ 冬季雪景 |
| 紅葉、楓葉 | 9-11月 | 🍁 紅葉季 |
| 銀河 | 4-9月 | 🌌 銀河季為4-9月 |

### 3.5 題材分類（classify_scene）

景點分類流程：
1. **multi_scene 精準匹配** — 已知景點直接指定題材（如「七星潭」→ coastal）
2. **關鍵詞自動分類** — 中/英/日關鍵詞匹配（mountain/coastal/waterfall/forest）
3. **fallback** → `["general"]`（城市/通用）

---

## 4. 地區與子區域系統

### 4.1 4 個國家

| Code | 名稱 | 景點數 | 子區域數 |
|:----:|:----|:-----:|:--------:|
| `tw` | 🇹🇼 台灣 | 69 | 8（本島+6外島+小琉球） |
| `jp` | 🇯🇵 日本 | 35 | 7 |
| `us` | 🇺🇸 美國 | 40 | 3（美西/美中/美東） |
| `ak` | 🏔️ 阿拉斯加 | 30 | 1 |

### 4.2 子區域列表

**台灣**：台灣本島 / 澎湖 / 金門 / 馬祖 / 蘭嶼 / 綠島 / 小琉球

**日本**：北海道 / 東北 / 關東 / 中部北陸 / 關西 / 中國四國 / 九州

**美國**：美西 / 美中 / 美東 / 阿拉斯加

### 4.3 子區域過濾機制

首頁點選子區域連結 → 跳轉到 `/summary?region=tw&sub=outlier`
摘要頁 `switchRegion()` 從 URL 讀取 `?sub=` → 在渲染前設定 `currentSubRegion`
`renderToday()` 等函數過濾：`items.filter(s => SUB_REGION_MAP[s.name] === currentSubRegion)`

⚠️ **重要**：子區域連結直接使用 `href="/summary?region=tw&sub=outlier"`，**不用 onclick**。之前用 onclick 造成 href/onclick 競態條件（race condition），sub 參數遺失。

---

## 5. 快取與資料更新

### 5.1 快取策略

`build_cache.py` 從 Open-Meteo API 抓取未來 3 天氣象，寫入 `.cache/forecast_{region}.json`

每筆資料包含：
- **hourly**: visibility, cloud_cover_low/mid/high, wind_speed_10m, weather_code, precipitation_probability, temperature_2m, dew_point_2m, relative_humidity_2m
- **daily**: sunrise, sunset, weather_code, precipitation_sum

### 5.2 更新排程

`scheduler.py` 每日 **00:00 / 06:00 / 12:00 / 18:00** 自動重建快取。

啟動方式：
```bash
cd weather_web
python scheduler.py    # 背景執行，自動每6小時更新
```

### 5.3 重要提醒：清除舊 Flask 程序

每次重啟 Flask 前，必須先**殺掉所有佔用 port 5000 的舊程序**，否則新舊混淆：

```bash
# Windows
for /f "tokens=5" %a in ('netstat -ano ^| find ":5000" ^| find "LISTENING"') do taskkill -f -pid %a
```

歷史上多次發生舊程序殘留導致新版程式碼未生效的狀況。

---

## 6. 頁面細節

### 6.1 首頁（home.html）

- 三個國家卡片（台灣/日本/美國），JS renderPage() 渲染
- 每個卡片內有子區域連結
- 天氣對策指南連結在國家卡片下方
- 右上角中英文切換
- **無**更新時間顯示（只在景點頁顯示）

### 6.2 景點摘要頁（summary.html）

- 上方：三個分頁按鈕（今日/明日/後天）
- 分頁下方：子區域切換按鈕（如 [🗺️ 全部] [台灣本島] [澎湖]...）
- 時間顯示在「今日最佳攝影點」標題下方
- 每個景點卡片含：名稱、評分、題材 badge、最佳時間、拍攝 tip
- 更新時間在頁面最底部（只顯示當前地區）
- 右上角：首頁按鈕 + 中英文切換

### 6.3 天氣對策指南（weather_guide.html）

- 獨立頁面，有首頁連結
- 4 張卡片：晴天大景 / 陰天漫射光 / 雨天雨後 / 閃電攝影
- 中英文雙語切換

---

## 7. 知識庫體系

### 7.1 檔案清單

| 檔案 | 用途 | 網站載入 |
|:----|:----|:--------:|
| `共用型_攝影知識庫.md` | 通用攝影技巧/天氣條件 | ✅ 是 |
| `台灣攝影景點指南.md` | 台灣 69 景點（統一表格） | ✅ 是 |
| `日本攝影景點指南.md` | 日本 35 景點 | ✅ 是 |
| `美國攝影景點指南.md` | 美國 40+阿拉斯加 10 景點 | ✅ 是 |
| `國家區域分類列表.md` | 子區域分類主檔（參考用） | ❌ 否 |

### 7.2 載入方式（app.py）

```python
KNOWLEDGE_SPOTS = {}
_kb_dir = os.path.join(專案根目錄, "Knowledge Base")
for fname in ["共用型_攝影知識庫.md", "台灣攝影景點指南.md",
              "日本攝影景點指南.md", "美國攝影景點指南.md"]:
    # 讀入 KNOWLEDGE_SPOTS[key] 供 display/reference
```

---

## 8. 語言切換

所有三個頁面（home/summary/weather-guide）都支援中英文切換。

### 實現方式

```javascript
const LANG = {
  zh: { /* 中文 */ },
  en: { /* 英文 */ }
};
function setLang(lang) { /* 切換 active 按鈕 + 重新渲染 */ }
function t(key) { return LANG[currentLang][key] || key; }
```

- home.html：`LANG` 物件含 `regions` 陣列（3國資料）及 foot/guide 文字
- summary.html：`LANG` 物件含 UI 文字（empty/error/scoreLabels 等）+ `REGION_LABELS` 地圖標籤
- weather_guide.html：使用 `data-zh`/`data-en` 屬性切換

---

## 9. 已知問題與注意事項

### 9.1 Port 5000 多程序殘留（⚠️ 最常見問題）

舊的 Flask 程序不會自動退出，堆積在 port 5000。重啟前務必全殺：
```bash
netstat -ano | grep ":5000" | grep LISTENING | awk '{print $5}' | sort -u
# 逐一 taskkill -f -pid <PID>
```

### 9.2 瀏覽器快取

前端 JS 渲染的內容（國家卡片、景點列表）如果沒出現，通常不是程式問題而是瀏覽器快取。強制重新整理 Ctrl+Shift+R。

### 9.3 git 版本回退

```bash
cd D:\Dick\Project\ChaseLights
git checkout v0.1     # 退回當前穩定版
git tag -l            # 列出所有 tag
```

### 9.4 Cloudflare Tunnel

開發階段使用 cloudflared 臨時 tunnel：
```bash
cloudflared tunnel --url http://localhost:5000
# 每次重啟產生新網址，如 https://xxx.trycloudflare.com
```

### 9.5 海拔校正（TRUE_ELEVATIONS）

Open-Meteo 的 7km 網格在山區誤差可達 900m，`app.py` 中有 `TRUE_ELEVATIONS` 字典覆蓋 30+ 個山區景點。

---

## 10. 開發指令速查

```bash
# 啟動伺服器
cd D:\Dick\Project\ChaseLights\weather_web
python app.py                     # → http://localhost:5000

# 更新天氣快取（先 kill 所有舊 Flask）
python build_cache.py tw          # 僅台灣
python build_cache.py tw jp us ak  # 全部 4 區

# 自動排程
python scheduler.py               # 背景，每日 00/06/12/18 更新

# 知識庫位置
cd D:\Dick\Project\ChaseLights\Knowledge Base

# git 版本管理
git tag -a v0.2 -m "version 0.2"
git checkout v0.1                 # 退回 v0.1
```

---

## 11. 開發者須知（給 Claude-3-Haiku）

1. **永遠先 kill 所有 port 5000 程序再重啟 Flask** — 這個問題出現最多次
2. **子區域過濾用 `?sub=` URL 參數**，不用 sessionStorage 或 onclick
3. **Tip 系統有三層**：天氣感知 genre → TIME_AWARE_TIPS → PHOTO_TIPS
4. **季節過濾 14 條規則**在 `app.py` 的 `SEASON_RULES` 列表
5. **景點分類三層**：multi_scene 精準 → 關鍵詞自動 → general 通用
6. **國家區域分類列表.md** 是子區域分組的權威來源，改分類前先更新它
7. **v0.1 是當前穩定版**，重大改動前先 `git tag` 再做
8. **專案路徑**：`D:\Dick\Project\ChaseLights\`

---

> 交接完成。ChaseLights v0.1 已在 Production 運行。
> 天氣每 6 小時更新一次，支援 4 國 174 景點，中英文雙語，天氣感知 Tip 系統。
> 緊急問題：kill port 5000 → rebuild cache → restart Flask。