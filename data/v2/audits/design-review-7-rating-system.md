# ChaseLights 設計審計 design-review-7 — 景點評分＋回報/留言 UGC 通道（專家評估＋完整設計）

- 評估者：chaselights_designer（DESIGN-7）
- 分支：task/DESIGN-4（from origin/main `6a4818c3c`）
- **v2（owner 裁示改版）**：①只評「景點分數」——不評題材×窗、不評「系統準不準」；L/P 兩軸對象是景點本身。②新增「回報機制」（回報站上錯誤內容或留言），與評分合成**一條 UGC 通道**。③舊留言系統（guest-comment.js／chaselights-comment Apps Script bridge）拆掉，功能併入新通道（§6 退役計畫）。
- 依據：owner 裁示（2026-11-11 原裁示＋本次改版）——會員評分取代 AI 自評；L（景色）＋P（出片滿意度）；UGC 五級信任階梯加權；事實欄（海拔/地質/季節）與評價分欄分離；冷啟動顯示「尚無足夠評價」；評分暫停中待 APP 穩定後接手。
- 本文件為**設計規格草案**：RD 落地前仍需 owner 對 §7 裁決點拍板；schema 為草案（review 通過才開票）。
- 配套 mockup：`data/v2/audits/design-mockups/mockup-rating.html`（卡片／景點彈窗／評分送出／回報表單、L/P 兩軸＋錯誤類型分類、三語、1280/390）。

---

## 1. 評什麼：景點分數（owner 裁示 v2）

### 1.1 對象裁定

> **評分主體 = (place_id)。** 不評題材×窗（v1 草案已撤）、不評「系統準不準」。

- 攝影師決策的第一問是「**這個景點值不值得去**」：專程程度、到達成本、機位品質——這些是跨題材的景點屬性。題材差異（雲海 vs 日出能不能拍）由 tier 層（✓○✗）承載，不需要第二套題材分。
- 「系統準不準」是 owner/data 層的內部品質指標，不該變成攝影師要回答的問題；預報誤差由 field validation 流程（B86 系列）處理。
- 評分鍵：`(user_id, place_id)` 一人一票；選填「拍攝日」（時間衰減用）——**不再鎖題材/窗**。

### 1.2 L／P 兩軸（對象＝景點本身）

| 軸 | 名稱 | 評什麼 | 五級文案 |
|---|---|---|---|
| **L（Landscape）** | 景色 | 這個景點本身值不值得：景色、氛圍、專程程度 | 1 不佳 · 2 普通 · 3 尚可 · 4 好 · 5 極佳 |
| **P（Photo yield）** | 出片滿意度 | 實際拍攝的收穫：成功率、片子滿意度 | 同上五級文案 |

- L 任何有效會員都能評；P 允許所有人評，但**無出片佐證鏈路**的會員 P 權重 ×0.5（§3.3）——「沒去也給 P 低分」是景點級分數最大的污染源（裁決點 §7-1）。
- 事實欄（海拔/地質/季節）是 data 層資產，**永不進評分聚合**；顯示上兩者分欄（mockup 分隔線）。
- 題材細節去哪：寫進**文字留言**（「雲海值得但機位只有一個」）——文字承載題材粒度，分數只給景點。

### 1.3 與三級語義／時間感知 tier 的關係：評分是 tier 的「人類校正層」

**裁定：評分永不參與 tier 計算**（理由不變：tier 是 fail-closed 物理預測，混入人為票即污染單一真相源；DESIGN-2 後 tier 才剛單一真相化）。

| | tier（✓○✗） | 評分（L/P） |
|---|---|---|
| 本質 | 物理預測層：氣象條件 fail-closed | 人類校正層：事後驗證 |
| 問答 | 「**今天**去能拍嗎？」 | 「**上次**去了值不值？」 |
| 資料源 | weather_details＋subject-cards 規則 | 會員 UGC（§2 一條通道） |
| 失效模式 | 預報誤差（觀測修正） | 串證/洗分（防護 §2.4） |

顯示層並列即校正：tier 說 ✓、評價區說「P≥4 出片率 62%、『機位只有一個』」——攝影師自己合成判斷。統計回流（預報 vs 出片校準）走 data 層重訓，不在 v1。

---

## 2. 回報機制：一條 UGC 通道（owner 裁示 v2 核心）

### 2.1 通道統一模型

三種提交共用一張表、同一個送出彈窗骨架、同一套信任/防護：

| 類型 | 針對 | place_id | 內容 | 公開？ |
|---|---|---|---|---|
| `rating` | 評景點 | 必填 | L/P ＋選填留言文字 | 分數公開；留言經審公開 |
| `report` | 回報站上內容錯誤 | 必填 | 錯誤類型＋說明（≤500 字）＋選填更正建議 | **不公開**（站長工單） |
| `comment` | 一般留言 | 選填（NULL＝站務留言，原 CL-UI-52 功能） | 文字（≤500 字） | 經審公開（景點留言）／站務留言僅站長 |

### 2.2 錯誤類型分類（回報表單必選單選）

| 代碼 | zh-TW | en | 覆蓋情境 |
|---|---|---|---|
| `data_wrong` | 資料錯誤 | Wrong data | 預報值/氣象數字與現場明顯不符 |
| `location_wrong` | 位置錯誤 | Wrong location | 座標偏移、地點名錯、到達方式/停車點錯 |
| `condition_wrong` | 條件錯誤 | Wrong conditions | 必須/加分/扣分門檻與實際出片經驗不符 |
| `seasonal_wrong` | 季節/時窗錯誤 | Wrong season/window | 季節植物/流冰等季節窗、日出日落時段錯 |
| `place_gone` | 封閉/消失 | Closed or gone | 封路、整建、撤除——影響可達性 |
| `other` | 其他 | Other | 兜底（必填說明） |

- 類型代碼＝triage 派工 routing key：`data_wrong/condition_wrong/seasonal_wrong` → data 層 ticket；`location_wrong/place_gone` → content ticket；`other` → 站長。
- 表單欄位（mockup 已呈）：類型單選（icon＋文案雙編碼）→ 景點（自動帶入當前景點；站務留言免）→ 說明 → 選填「更正建議」→ 匿名聲明 → 送出。

### 2.3 審閱流程（fail-closed）

```
送出 → 自動篩（節流＋禁詞＋同簇去重；honeypot 精神由登入門檻取代）→
  ok      → status='open' 進審閱佇列
  flagged → status='flagged'（標記原因，人工裁決，不自動刪）
→ 處置：
  accepted  → 建對應 ticket（data/content/站務）；對回報者 trust 記一次「有貢獻」（§3.1）
  need_info → status='need_info'（v1 不回推訊息；重報即新工單）
  rejected  → status='rejected'（留審計軌跡）
```

- **留言公開規則（首審制）**：景點留言由 admin 核可後公開；v2 演進＝trust≥T1 且無違規者免審直發（裁決點 §7-2）。
- **管理端最小方案**：不建新系統——D1 表＋現有 admin 頁體系（B137 admin filters 骨架）加一個「回報審閱」清單頁：篩選（status/類型/place）＋逐筆展開＋三鍵處置（接受/需更多資訊/拒絕）＋CSV 匯出兜底。

### 2.4 防 spam／防洗分（評分與回報共用）

| 攻擊 | 防護 |
|---|---|
| 未登入灌水 | **全通道要求登入**（OAuth 會員）；guest 直送端點拆除（§6.3） |
| 新帳號爆量 | T0 權重 0.5；24h 內**計入聚合的評分上限 3 票**、全通道提交上限 10 筆 |
| 同 IP/裝置簇互刷 | `ip_cluster`（/24 hash）＋`device_hash`；同景點同簇等效票上限 2（第 3 票 ×0.25）；同簇同日回報 >3 筆併一張工單 |
| 秒評/沒去也評 | 與上次提交 <90 秒 → flagged；P 軸無鏈路 ×0.5；`shot_date` 不得晚於今天 |
| 統計異常 | 單筆與該景點現況差 >2.5σ 且無鏈路 → flagged 人工審 |
| 重複 | 評分 PK `(user_id, place_id)` 編輯覆蓋；同 (user,place,report_type) 7 天內重複併入原工單 |
| 評分與回報互打 | 惡意簇的票被 ×0.25 壓制；owner 可手動 `rejected` |

flagged/rejected 不進聚合但保留（審計軌跡）；判定不了就 flagged（fail-closed）。

---

## 3. 誰的評分算數：信任階梯＋冷啟動＋聚合

### 3.1 五級信任階梯（owner 裁示落地）

| 級 | 名稱 | 資格 | 權重 w | 徽章 |
|---|---|---|---|---|
| T0 | 新會員 | 帳齡 <30 天 或 有效提交 <3 | 0.5 | 無 |
| T1 | 活躍 | 帳齡 ≥30 天 且 近 30 天 ≥3 筆有效提交 | 1.0 | 無 |
| T2 | 有出片紀錄 | T1 ＋ 出片鏈路：`push_invite`（拍完推播邀評）或 accepted 回報/field intake，近 90 天 ≥1 | 1.5 | 🎞 |
| T3 | 資深 | T2 ＋ 帳齡 ≥90 天 且 有效提交 ≥20 且 跨 ≥3 地區 | 2.0 | 🏔 |
| Tx | 策展 | owner/admin 認證 | 3.0 | ✔ |

- 每日 batch 重算 `user_trust` snapshot；提交時快照等級入列（事後降權不追溯歷史列，重算聚合用最新 snapshot）。
- **回報也算貢獻**：accepted report 近似一次有效提交（糾錯貢獻計入信任階梯）。

### 3.2 冷啟動（owner 裁示落地）

- 顯示門檻：`n_eff < 2.0` 或 `n_raw < 3` → **不出示任何分數**，顯示「尚無足夠評價」＋邀評 CTA（三語）。
- 收斂：首票起算；n≥3 顯示＋樣本少註記；n≥10 撤註記；貝氏 k=5 下 n≥15 先驗影響 <25%、n≥30 <10%——3–5 個活躍會員票後可顯示。
- 460 景點起步期必然大量冷啟動：**卡片不出空 chip**（列表掃描層維持乾淨），冷啟動狀態只在彈窗評價區顯示。

### 3.3 聚合演算法（精確定義）

```
per rating r (kind='rating', status='ok'):
  age_days = (evaluated_at − r.created_at)
  decay    = 0.5 ^ (age_days / 365)              # 景點層半衰期 365 天（比題材級慢；裁決點 §7-3）
  cluster  = 同簇等效票>2 ? 0.25 : 1.0
  chain    = (source != 'app') ? 1.0 : (trust='t0' ? 0.5 : 1.0)   # 無鏈路新會員 P 降權
  w'_L = w × decay × cluster            ;  w'_P = w × decay × cluster × chain
  s̄_L = Σw'_L·L/Σw'_L ; s̄_P = Σw'_P·P/Σw'_P ; n_eff = Σw'_L
貝氏收縮（k=5；m = 全站先驗均值，每日 batch 重算）：
  L_final = (s̄_L·n_eff + m_L·k)/(n_eff+k) ; P_final 同式
顯示：n_eff≥2.0 且 n_raw≥3
```

---

## 4. 資料模型（schema 草案，D1/SQLite）

### 4.1 統一 UGC 表 `feedback`

```sql
-- CL-DESIGN-7 v2 草案：評分＋回報＋留言，一表一通道
CREATE TABLE IF NOT EXISTS feedback (
  id            TEXT PRIMARY KEY NOT NULL DEFAULT (lower(hex(randomblob(16)))),
  kind          TEXT NOT NULL CHECK (kind IN ('rating','report','comment')),
  user_id       TEXT NOT NULL,              -- users.id（device_id 體系）
  place_id      TEXT,                       -- rating/report 必填；comment 選填（NULL=站務）
  -- kind='rating' 用
  l_score       INTEGER CHECK (l_score BETWEEN 1 AND 5),   -- L 景色
  p_score       INTEGER CHECK (p_score BETWEEN 1 AND 5),   -- P 出片滿意度
  shot_date     TEXT,                       -- 選填拍攝日 'YYYY-MM-DD'（≤今天）
  -- kind='report' 用
  report_type   TEXT CHECK (report_type IN
                ('data_wrong','location_wrong','condition_wrong','seasonal_wrong','place_gone','other')),
  fix_suggest   TEXT,                       -- 選填更正建議 ≤300 字
  -- 共用
  message       TEXT,                       -- 留言文字 ≤500 字（rating 附言 / comment）
  source        TEXT NOT NULL DEFAULT 'app'
                CHECK (source IN ('app','push_invite','legacy_import')),
  trust_level   TEXT NOT NULL,              -- 提交時 snapshot（t0..tx）
  weight        REAL NOT NULL,              -- 提交時基礎權重（0.5–3.0）
  ip_cluster    TEXT NOT NULL,              -- IP /24 hash（不留原 IP）
  device_hash   TEXT NOT NULL,              -- device_id hash
  status        TEXT NOT NULL DEFAULT 'ok'
                CHECK (status IN ('ok','open','flagged','rejected','need_info')),
  flag_reason   TEXT,                       -- burst/cluster/time/sigma/words
  reviewed_by   TEXT,  reviewed_at TEXT,    -- admin 處置軌跡
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_feedback_vote
  ON feedback(user_id, place_id) WHERE kind='rating';       -- 一人一票，編輯覆蓋
CREATE INDEX IF NOT EXISTS idx_feedback_agg
  ON feedback(place_id, kind, status, created_at);          -- 聚合＋景點留言讀取
CREATE INDEX IF NOT EXISTS idx_feedback_queue
  ON feedback(status, kind, created_at);                    -- 管理端審閱佇列
CREATE INDEX IF NOT EXISTS idx_feedback_user_time
  ON feedback(user_id, created_at);                         -- 節流＋trust 重算
```

> 狀態語義：`ok`＝免審直入（rating；accepted 後的 comment）；`open/need_info`＝report/comment 審閱流；rating 只會是 `ok/flagged/rejected`。

### 4.2 聚合表＋SQL 草案

聚合數學在 worker JS（冪函數衰減/簇統計），SQL 管抓取與落表——精確到可開票：

```sql
CREATE TABLE IF NOT EXISTS rating_agg (
  place_id    TEXT PRIMARY KEY,
  l_final     REAL, p_final REAL,           -- 貝氏校正（未達門檻=NULL）
  l_raw       REAL, p_raw REAL,             -- 未收縮（除錯用，不顯示）
  n_raw       INTEGER NOT NULL DEFAULT 0,
  n_eff       REAL NOT NULL DEFAULT 0,      -- 顯示門檻
  n_last30    INTEGER NOT NULL DEFAULT 0,   -- 近 30 天票數（近況）
  pct_p4plus  REAL,                         -- P≥4 出片率（顯示）
  n_comments  INTEGER NOT NULL DEFAULT 0,   -- 已公開留言數
  last_rated_at TEXT,
  computed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS user_trust (
  user_id     TEXT PRIMARY KEY,
  level       TEXT NOT NULL,                -- t0..tx
  weight      REAL NOT NULL,
  chain_rate  REAL NOT NULL DEFAULT 0,      -- 近 90 天鏈路比例
  computed_at TEXT NOT NULL
);
-- 全站先驗（每日 batch）
CREATE TABLE IF NOT EXISTS rating_prior (
  scope       TEXT PRIMARY KEY DEFAULT 'global',
  m_l REAL NOT NULL, m_p REAL NOT NULL,
  computed_at TEXT NOT NULL
);

-- ① 抓取（worker 算 w'）：
SELECT l_score, p_score, weight, source, trust_level, created_at
  FROM feedback
 WHERE kind='rating' AND place_id=?1 AND status='ok'
 ORDER BY created_at DESC LIMIT 500;         -- 衰減後等效 <0.03 權重的舊票拋棄

-- ② worker 算完 UPSERT（冪等）：
INSERT INTO rating_agg (place_id, l_final, p_final, l_raw, p_raw, n_raw, n_eff,
                        n_last30, pct_p4plus, n_comments, last_rated_at, computed_at)
VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,datetime('now'))
ON CONFLICT(place_id) DO UPDATE SET
  l_final=excluded.l_final, p_final=excluded.p_final, l_raw=excluded.l_raw,
  p_raw=excluded.p_raw, n_raw=excluded.n_raw, n_eff=excluded.n_eff,
  n_last30=excluded.n_last30, pct_p4plus=excluded.pct_p4plus,
  n_comments=excluded.n_comments, last_rated_at=excluded.last_rated_at,
  computed_at=excluded.computed_at;

-- ③ 讀取（彈窗一次拿分＋我的評分）：
SELECT a.l_final, a.p_final, a.n_raw, a.n_eff, a.pct_p4plus, a.n_last30, a.n_comments,
       (SELECT 1 FROM feedback mf WHERE mf.user_id=?2 AND mf.kind='rating'
          AND mf.place_id=a.place_id AND mf.status='ok') AS mine
  FROM rating_agg a WHERE a.place_id=?1;

-- ④ 景點留言（公開，首審通過）：
SELECT message, trust_level, created_at FROM feedback
 WHERE kind='comment' AND place_id=?1 AND status='ok'
 ORDER BY created_at DESC LIMIT 20;
```

- 資料量：聚合表 ≤460 列；明細表十萬列內，D1 勝任。聚合寫入與明細寫入同一請求順序完成；失敗靠每日 batch 全量重算兜底（冪等）。

---

## 5. 與現有管的整合

### 5.1 tier 計算：**不受評分影響**

- 門檻/權重/✓○✗ 語義零改動；`build_subject_cards.py`、time-aware tier 管線不讀 `feedback`/`rating_agg`。
- 評分僅顯示層附掛；tier 斷言與 UGC 斷言測試隔離。

### 5.2 顯示位置（mockup 對應）

| 面 | 放什麼 | 門檻 |
|---|---|---|
| **卡片** | 標題行 tier 徽章旁一枚景點評分 chip「★4.3 ·27」（mono 第二灰層，琥珀數字）；未達門檻不出 chip | n_eff≥2 |
| **景點彈窗**（點卡片本體） | quick-look＋24h 色帶下加「評價」區：L/P 雙軸列（五級刻度＋分數）＋P≥4 出片率＋n＋近 30 天＋匿名留言 ≤3 則＋「我的評分」列＋入口鈕 ✎評分／🚩回報錯誤；冷啟動＝虛線框「尚無足夠評價」＋邀評 CTA | 全狀態 |
| **評分彈窗** | L/P 兩軸五級＋選填留言＋匿名聲明；流程 B＝拍完推播邀評（「📸 今日拍攝」鏈路徽章，計入 T2） | — |
| **回報彈窗** | §2.2 錯誤類型單選＋說明＋更正建議＋匿名聲明 →「已收到·審閱中」完成態 | — |
| **頁尾** | 原「💬 留言」入口（CL-UI-52）換成「💬 留言/回報」，開**同一通道**（站務留言＝不帶景點的 comment） | — |
| genre-eval 頁 | v1 不放評分（評分是景點級） | — |

- 匿名顯示：遮罩暱稱「晨曦\*\*」；未填暱稱顯示「攝影者·地區」；永不顯示帳號/device/Email。回報內容**不公開**。
- 「我的評分」：已評顯示 L/P＋✎編輯（UPDATE 覆蓋同 PK）；編輯重新觸發聚合。
- 事實欄分離：彈窗內 data 層事實（海拔/條件）與 UGC 評價區視覺分組＋分隔線。

### 5.3 提醒／推播聯動（出片鏈路引擎）

- **拍完邀評 push**：`notify_rules` 該窗觸發後 +3 小時（日出窗 06:00 → 09:00 邀評），點開直進**景點評分彈窗**（帶今日拍攝徽章）；`source='push_invite'`＝T2 自動來源。頻率：每日 ≤1、每週 ≤3（沿用 notify 引擎節流位）；當日已評不推。
- 無推播訂閱者：卡片顯示「去過？評個分」邀評 pill（`source='app'`，不享 T2 加成——推播訂閱的實際誘因）。

---

## 6. 留言系統退役計畫（owner 裁示 ③）

### 6.1 現狀盤點（拆什麼）

| 件 | 位置 | 角色 |
|---|---|---|
| 前端 widget | `assets/guest-comment.js`（193 行）、`assets/guest-comment.css`（164 行） | 頁尾💬入口→彈窗→POST（暱稱≤20/留言≤500/honeypot，no-cors） |
| 頁面掛載 | `index.html` L146–170（footer entry＋modal DOM） | |
| 後端 | `templates/gas_sheet_bridge.js` `doPost` 的 `action==='comment'` 分支 → Google Sheet「訪客留言」分頁（時間戳/暱稱/留言/來源語言/user_agent） | **公開無鑑權**（honeypot 防spam） |
| 代理 | `chaselights.app/api/comment` → Apps Script | |
| 測試 | `apps/web-v2/tests/cl-ui-52-guest-comment.test.mjs` | 斷言頁尾入口存在 |

### 6.2 資料遷移（一次性）

1. 匯出「訪客留言」分頁全量 → 映射寫入 `feedback`：`kind='comment'`、`place_id=NULL`（舊留言無景點上下文）、`message=留言`、`user_id='legacy:'+rowhash`（合成佔位 user，永不登入）、`trust_level='t0'/weight=0`（歷史留言只留檔，不參與任何權重）、`status='ok'`、`source='legacy_import'`、`created_at=時間戳`、`ip_cluster='legacy'`。
2. 遷移腳本 `scripts/migrate_legacy_comments.py`：先 dry-run 報數、後對帳（Sheet 列數＝匯入數）；Sheet 原狀保留（只讀封存，不刪）。
3. 舊留言**不公開顯示**（無景點歸屬＋無會員身份），僅管理端審閱佇列可見；站長要回應的手動轉新工單。

### 6.3 移除範圍與切換順序（嚴禁 big-bang）

```
W1 上線新通道（feedback 表＋評分/回報/留言彈窗＋管理端審閱頁）；頁尾入口換新版（同位置、沿用 i18n key 風格）
W2 並行 2 週：舊入口收起（guest-comment.js 保留但 GC_ENDPOINT 指向停用 stub）；新提交全走新通道
W3 退役 PR（單票、可 revert）：
   - 刪 assets/guest-comment.js / guest-comment.css、index.html 頁尾留言區塊
   - 刪 gas_sheet_bridge.js 的 action==='comment' 分支＋COMMENT_TAB 常數
     （legacy 四分頁 sync 分支【保留】——資料管線仍依賴）
   - 刪 /api/comment 代理路由
   - 刪 cl-ui-52 測試，新增新通道對等測試（三語/登入門檻/節流/失效態；honeypot 由登入門檻取代）
   - AGENTS/README 內 CL-UI-52 標記 retired → DESIGN-7
```

- 測試負債點：cl-ui-52 斷言頁尾入口存在——退役 PR 必須同步換測（新入口同位），否則 CI 變紅。
- GAS 專案本身保留（legacy 資料 sync 用），只是不再收留言。

---

## 7. 裁決點（owner 必須拍板，5 項）

| # | 問題 | 選項 | 建議 |
|---|---|---|---|
| **1** | **L/P 兩軸保留還是併單分**（對象已是景點） | A. 單一分數（最簡、表單少一軸）／B. 保留 L/P（「值不值」與「拍到了」兩種訊息） | **B**——「值不值得去（L）」與「實際收穫（P）」對攝影師是兩個問題；卡片 chip 顯示 P（出片是硬訊息）、彈窗並列雙軸。P 軸無鏈路 ×0.5 防沒去也評 |
| **2** | **留言公開策略** | A. 全首審（品質穩、慢）／B. T1＋無違規免審直發（快、需風控）／C. 不公開（僅站長收件） | **A 起，B 為既定 roadmap**——UGC 開閘初期顯示品質就是信任度本身；免審直發等 trust 資料累積後再開 |
| **3** | **時間衰減** | A. 無衰減（分數穩定）／B. 365 天半衰期／C. 180 天 | **B**——景點會變（封路/整建）但比預報體驗慢；365 天一年約衰一半，既反映近況又不會一夜清空。C 對景點級偏快 |
| **4** | **匿名顯示** | A. 完全匿名（無署名）／B. 遮罩暱稱「晨曦\*\*」／C. 實名 | **B**——有署名才有社群感與責任感，遮罩擋起底騷擾；C 對台日美三語用戶隱私預期過重 |
| **5** | **開閘時機** | A. APP 穩定即全量／B. 先對「有推播訂閱＋有最愛」會員灰度 2 週再全量 | **B**——灰度期天然產生有鏈路（push_invite）的 T2 種子評分，全量開閘當天已有可顯示分數對沖 T0 灌票。**回報通道可與評分同步灰度**（回報無冷啟動問題，早開早收錯誤） |

---

## 8. 驗收斷言建議（RD 開票時掛上）

- tier 斷言零變動：掛 UGC 後 subject-cards 全量測試 tier 值不變。
- 聚合冪等：同明細重算 `rating_agg` 兩次逐位相等。
- 門檻行為：n_eff<2 → API `score=null, insufficient=true`，UI「尚無足夠評價」三語；卡片不出空 chip。
- 一票一列：同 (user,place) 第二次 POST=UPDATE，`n_raw` 不增。
- 簽簇上限：同 `ip_cluster` 5 票同景點 → n_eff 等效 ≤2+0.25×3。
- 回報路由：report 必選 `report_type`；`place_id` 缺失且 kind≠'comment' → 400。
- 管理端：三鍵處置後 status 落表＋`reviewed_by/at` 有值；CSV 匯出含全部 status。
- 退役回歸：W3 PR 後 `grep guest_comment/guest-comment` 零殘留（i18n pack、tests、README）；頁尾入口存在且開新通道；legacy 四分頁 sync 測試不受影響。
- 顯示全寬：★chip/軸列任何字串不省略號（`scrollWidth==clientWidth` 三語斷言，站規）。
