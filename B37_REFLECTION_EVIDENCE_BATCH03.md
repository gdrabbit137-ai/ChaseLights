# B37 Reflection Evidence Review — Batch 03 / Completion

本批次完成 reflection 類別剩餘項目，並修正 audit 對「核心題材」與「次要畫面元素」的誤判。

## Verified — Grade B

### tw-056-P02 松蘿湖平靜湖面倒影
多筆獨立健行／攝影實拍記錄直接展示松蘿湖清晨、平靜湖面時的天空、山景、帳篷倒影，並描述湖水平滑如鏡。以多次 Place-specific observation 驗證。

### tw-057-P02 加羅湖平靜湖面倒影
旅遊媒體地點明確影片直接描述加羅湖湖面如鏡、倒映百年山林，另有具地點標記的攝影作品佐證。

## Verified — Grade A

### tw-083-P01 雲山水夢幻湖與落羽松倒影
花東縱谷官方相簿及遊程直接描述翠綠落羽松林倒映水中。

### jp-010-P02 大石公園・逆さ富士
富士河口湖町官方觀光網站直接說明無風時大石公園湖面可映出富士山形成「逆さ富士」。

### tw-082-P06 鯉魚潭水岸光影節夜景與裝置藝術
活動本身以 2026 官方公告驗證。reflection 不是 admission 的核心 claim，因此 audit risk override 只保留 event。

## Narrow scope

### tw-082-P01 鯉魚潭湖光山景與平靜倒影
花東縱谷官方明確證明鯉魚潭有山水倒影，且潭南碼頭官方圖片說明直接稱可捕捉山水倒影；但目前 P01 Camera Zone 是潭北公共湖岸，證據與 Camera Zone 尚未完全對齊，所以先標 narrow_scope。

## Audit false-positive corrections

### tw-060-P01 七美雙心石滬完整形態
核心題材是潮位下雙心石滬的完整形態，不是 reflection。移除 reflection risk classification。

### tw-082-P10 鯉魚潭人工濕地與水岸近景細節
核心題材是人工濕地、植被與水岸近景；倒影只是 optional detail / booster。移除 reflection risk classification。若未來要讓倒影成為獨立高分題材，必須建立獨立有證據的 Opportunity。

## Reflection category completion

完成本批次後，Evidence Audit 中已沒有任何 `review_required` reflection Opportunity。

Reflection 類別正式遵循以下規則：

1. 有水面不是倒影證據。
2. 低風不是倒影存在證據。
3. 潮位／水位只是 runtime condition。
4. 反射構圖必須有 Place-specific evidence。
5. 證據必須符合 Camera Zone / composition scope。
6. 次要 booster 不應讓整個 Opportunity 被誤分類成 reflection subject。
