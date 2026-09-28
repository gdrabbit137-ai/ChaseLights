# B87 — 清水斷崖晨霧構圖可讀性 Guard

## 目的

B81 / B82 已把 `tw-034-P03 — 清水斷崖晨霧、雲霧山海` 建成 Place-specific 已查證題材，並加入北向多點霧訊號。

Production 仍有一個過度推薦風險：拍攝點能見度只有約 0.6–0.9 km 時，只要北向 proxy 更霧，P03 仍可能得到 88 分。這與題材規格「斷崖、山壁或海岸至少部分可辨」不一致。

B87 不否定霧訊號，而是把「有霧」與「這個構圖仍可拍」分開。

## 規則

對 `tw-034-P03`：

1. 拍攝點白牆仍是 hard blocker。
2. 北向多點霧訊號仍可提高晨霧候選信心。
3. 拍攝點能見度低於 **2.5 km** 時：
   - 仍可保留晨霧候選；
   - score hint 封頂在 **68**；
   - confidence = **low**；
   - UI 明確指出斷崖／山壁／海岸輪廓可能不足。
4. 拍攝點能見度至少 2.5 km，且有多項單點霧訊號：
   - 可使用 `OPPORTUNITY_MIST_SUPPORTED`。
5. 拍攝點能見度至少 2.5 km，且北向多點霧訊號成立：
   - 可使用 `OPPORTUNITY_DIRECTIONAL_MIST_CANDIDATE`。

## 2.5 km 的意義

2.5 km 是目前 B82 最接近的 directional environmental proxy range，因此只作為**保守規劃門檻**。

它不是：
- 宣稱崇德平台到清水斷崖的精確距離；
- 保證 2.5 km 以上一定看得到斷崖；
- 把 visibility 當成實景觀測。

若未來取得更精確的 subject geometry / field validation，可再替換這個 guard。

## UI 語意

- `OPPORTUNITY_MIST_CANDIDATE`
  - 低信心
  - 可見度或霧區位置仍不確定
- `OPPORTUNITY_MIST_SUPPORTED`
  - 多項氣象訊號佐證
  - 拍攝點視野仍在保守可用範圍
- `OPPORTUNITY_DIRECTIONAL_MIST_CANDIDATE`
  - 北向多點預報支持
  - 仍不宣稱霧已實際落在斷崖

## 與舊 PR 的關係

B87 重新在 current `main` 上實作並整合舊 PR #140 / #141 的有效意圖：

- #140 的 Opportunity-specific status copy
- #141 的 cliff-readability guard

不直接 merge 舊 branch，避免把 B83–B86 之後的 runtime / UI 變更倒退。

## Release gate

- Adapter PASS
- Evidence Audit PASS
- Taiwan Candidate Weather PASS
- Browser Smoke PASS
- production weather refresh PASS
- production output 中 0.6–0.9 km 類案例不得維持 88 分
