# B85 — 七星潭地形雲低信心 Proxy

## 背景

B83 已新增 `tw-036-P03`「七星潭北望清水山／清水斷崖＋貼山雲帶」。
B84 再把一般「北望山海遠眺」拆成獨立 `tw-036-P04`，避免把「山看得見」和「山腰有雲帶」混成同一個 pass/fail。

2026-09-28 13:00 的實拍仍揭露一個解析度問題：

- 海岸與海面通透；
- 北方山體有明顯貼山雲；
- production 多點格點能正確判斷 P04 山海遠眺良好；
- 但 P03 的直接低雲／高濕門檻仍未抓到現場雲帶。

這不是把地形本身當成題材證據。P03 的題材存在性已由 Grade-A Place-specific 官方資料建立；B85 只處理「已查證題材何時較可能成立」的 runtime 解析度缺口。

## B85 原則

直接格點雲訊號仍是主要判定。

只有在直接訊號未成立時，才允許一個 **低信心 orographic-cloud proxy**，而且必須同時具備：

1. 七星潭 Camera Zone 本身保持清楚，不能白牆或大雨；
2. 規劃級 LCL proxy 與至少 2 個北向高地樣本相交；
3. 相交樣本跨至少 2 個方位；
4. 至少一個高地樣本能見度 <= 8 km；
5. 該最低高地能見度 <= 海岸能見度的 30%；
6. 高地低雲量至少有 15% 支持；
7. 北方仍至少有 2 個可讀高地樣本，跨至少 2 個方位，避免把整片白牆當作好題材。

## 輸出邊界

此 fallback：

- reason = `orographic_cloud_proxy_candidate`
- confidence = `low`
- score cap = **78**
- UI 明確寫「格點未直接解析雲帶，需現場確認」
- 不宣稱雲帶已被觀測
- 不宣稱雲帶精確貼住清水山／清水斷崖
- 不取代 P04 的一般山海遠眺判定

## 2026-09-28 13:00 校準理由

B84 production diagnostics 在 13:00 顯示：

- Camera visibility 約 27 km
- Camera low cloud 約 2%
- LCL proxy 約 699 m AGL / 713 m ASL
- 北向高地最高約 1670 m
- 3 個高地樣本高於 LCL proxy，跨 2 個方位
- 高地最低 visibility 約 5.6 km
- 高地最高 low cloud 約 24%
- P04 山海遠眺可讀

這組條件與實拍「海岸清楚、北方山腰雲帶」一致，但不足以當成高信心直接雲帶偵測，因此 B85 只建立低信心候選。

## 風險控制

目前只有一筆明確 ground-truth 正例，因此門檻採保守設計，且不讓 proxy 進入 80+ 推薦帶。

後續若累積更多實拍：

- 有雲帶但 proxy miss → 檢查敏感度
- 無雲帶但 proxy hit → 優先收緊 visibility ratio / low-cloud / LCL intersection 條件
- 不應單靠一兩筆案例把分數直接拉高
