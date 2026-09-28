# B87 — 清水斷崖晨霧構圖可讀性 Guard + 狀態文案

Date: 2026-09-28 (Asia/Taipei)

## 問題

B81/B82 已建立 `tw-034-P03 — 清水斷崖晨霧、雲霧山海` 與北向多點霧訊號。

Production re-check 發現一個過度推薦案例：

- 拍攝點能見度約 0.6–0.9 km，
- 北向 proxy 同時顯示霧訊號，
- 舊模型仍可給 88 分，
- UI 甚至只顯示「此景點的基本好拍條件已成立」。

對「清水斷崖晨霧」這個已驗證題材而言，霧本身不是唯一條件；斷崖／山壁／海岸仍需要保留足夠輪廓，否則容易變成只看到白牆或霧幕。

## B87 規則

對 `tw-034-P03` 加入保守的拍攝點構圖可讀門檻：

- `min_camera_readability_km = 2.5`
- 2.5 km 取自 B82 最近的 directional environmental proxy range，僅作 planning guard。
- 這 **不是** 宣稱觀景平台到斷崖的實際距離。

若：

- 晨霧條件有至少一項佐證，
- 但拍攝點能見度 < 2.5 km，

則：

- 仍保留為攝影候選，
- `score_hint = 68`,
- `confidence = low`,
- `subject_readability_uncertain = true`,
- 不得進入 80+ 高推薦。

原有 local whiteout veto 仍保留。

## 狀態文案

B87 同時移除過於泛化的「基本好拍條件」文案：

### 北向多點霧訊號 + 拍攝點仍可讀
`OPPORTUNITY_DIRECTIONAL_MIST_CANDIDATE`

> 多點預報支持斷崖方向晨霧候選，拍攝點視野仍可用

### 非 spatial、但有多項氣象佐證 + 拍攝點仍可讀
`OPPORTUNITY_MIST_SUPPORTED`

> 晨霧候選有多項氣象訊號佐證，拍攝點視野仍可用

### 霧區位置不確定或斷崖構圖可讀性不足
`OPPORTUNITY_MIST_CANDIDATE`

> 晨霧候選條件出現，但斷崖可見度或霧區位置仍有不確定性

所有文案都保持「候選／支持」語意，不宣稱現場已經觀測到霧。

## Production issue reproduced before B87

2026-10-01 forecast rows in production had examples:

- 05:00：visibility 約 0.6 km、low cloud 100%，P03 仍為 88
- 06:00：visibility 約 0.9 km、low cloud 88%，P03 仍為 88

兩者都有 directional mist support，但拍攝點本身太不透明，不應以 88 分呈現為高可信度斷崖晨霧構圖。

B87 將這類案例保留為低信心候選，而不是把霧訊號直接等同於可拍的斷崖晨霧。

## 邊界

- 此 guard 不證明現場斷崖一定看得見。
- 此 guard 不證明霧的位置。
- 2.5 km 不是實際 cliff distance。
- 多點 proxy 仍是環境 proxy，不是精確霧／斷崖交會。
- 若日後有實拍 ground truth，可再校準門檻；不得只因單一案例提高分數。
