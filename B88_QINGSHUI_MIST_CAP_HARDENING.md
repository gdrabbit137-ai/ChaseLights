# B88 — 清水斷崖晨霧 68 分硬上限 Hardening

## 背景

B87 已修正 `tw-034-P03 — 清水斷崖晨霧、雲霧山海`：

- 拍攝點 visibility < 2.5 km 且有霧訊號時，不再給 80+；
- 改為低信心候選；
- 增加 Opportunity-specific status copy。

B88 是後續 hardening，不改 2.5 km policy 本身。

## 為什麼還需要 B88

minimum-sufficient scoring 的一般邏輯會：

`score = max(theme_base_score, minimum_sufficient_score_hint)`

因此只把 `score_hint` 改成 68 並不等於真正的上限。若未來 generic fog/mist Theme baseline 因其他因子升到 80+，仍可能把「斷崖構圖可讀性不足」的候選重新拉高。

B88 將 B87 policy 改成真正的 hard ceiling：

- `subject_readability_uncertain == true`
- final Opportunity score **<= 68**

generic Theme baseline 不得覆蓋這個構圖 guard。

## 其他 hardening

1. visibility-only candidate（沒有其他霧訊號）若 visibility < 2.5 km：
   - 保留原本 visibility-only reason；
   - 同時標記 `subject_readability_uncertain = true`；
   - UI 可顯示斷崖／山壁／海岸輪廓不足的原因。
2. Opportunity runtime module version 升為 B88 checkpoint。
3. Canonical catalog formula version / Condition Variant 文案同步寫明「最終 Opportunity 分數封頂 68」。
4. Evidence registry 明確記錄：
   - 68 是 score cap，不只是 score hint；
   - cap 可覆蓋 generic Theme baseline。

## 不變的邊界

- 2.5 km 仍只是 conservative planning guard，不是實際 camera-to-cliff distance。
- 晨霧題材存在性仍由 Grade-A Place-specific evidence 支持。
- directional proxy 不是精確霧／斷崖交會。
- camera whiteout 仍 fail closed。
- B88 不提高任何晨霧分數，只防止低可讀性案例被其他基礎分數重新抬高。
