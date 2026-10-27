# Phase-2 全量題材裁定 — 297 筆（2026-10-26）

## 產出檔案（photo_refs2/）
- `FINAL_P2_297_verdicts.csv` — 逐筆裁定（verdict / confidence / evidence / notes）
- `vision_findings_p2.json` — 每筆照片分析
- `round2_p2.json` — 補查/複審清單（180 筆：含 23 筆完全無效 + 157 筆「主體或時段未取證」）
- `sheets/` — 2×2 拼圖、`harvest_state.json` — 377+ 張照片來源對照

## 流程
- Wikimedia Commons 採集 297/297、視覺分析 274 筆有效照片、19 筆 0 命中、4 筆全 djvu 撞古籍
- 命名規則：12 模板固定詞彙；confidence 標記 [uncertain]＝機會主體（如日出、星空、鏡面）未在照片中直接取證

## 最終分布（297 筆）
| 題材 | 數 |
|---|---|
| D（人文/不在 12 模板） | 77 |
| sunset | 42 |
| mountain_view | 29 |
| sunrise | 26 |
| blue_hour_city | 21 |
| city_night | 17 |
| night_sky | 14 |
| cloud_sea | 12 |
| seasonal_plant | 11 |
| overlook | 9 |
| reflection | 7 |
| KEEP（冰河題材候選） | 4 |
| overcast_soft | 3 |
| golden_hour | 2 |
| 無效待 round-2 | 23 |

## 給 owner 的 5 個歸類議題（跨批次一致出現）
1. **瀑布/峽谷地質**（高千穂、尼加拉、Snoqualmie、羚羊谷、Mesa Arch、拱門群）：地質語意不在 12 模板 → 全判 D；若 owner 想收，「岩質地景」可能需要新語意或歸 mountain_view（Mesa Arch 日出光束證據極強）
2. **火山地貌**（St Helens、Katmai、紀念碑谷、火炎山、月世界）：目前歸 mountain_view，一致性待 owner 確認
3. **城市天際線**：blue_hour_city 與 city_night 邊界需定義（芝加哥/西雅圖 Kerry Park 均有黃昏與夜景雙機會）
4. **農業地景**（Palouse 色塊田、伯朗大道）：稻田/麥浪語意與 seasonal_plant 的植物季節語意不同
5. **雪季語意**（Crater Lake 冬、Tipsoo）：季節地貌（雪）不屬 seasonal_plant，建議未來 seasonal_state 覆寫機制

## 門檻證據累積（延續批次 1）
- **reflection wind<3**：松蘿湖鏡面（極強）、高美天空之鏡（極強）、Crater Lake/Tipsoo/雲山水（強）vs 嘉明湖風面無倒影（fail）→ 門檻成立
- **時段型機會（sunset/sunrise）**：42+26 筆中約 6 成照片未取到該時段 → 顯示此類機會的「時段正確性驗證」比「主體存在驗證」更重要，建議模型輸出需分離「主體確認」與「時段確認」兩個 confidence

## round-2 建議
180 筆清單已附修正查詢詞（zh+en），重點：
- 23 筆完全無效：djvu 撞名（南子吝、西穗高口、二寮、關山、外澳、見晴…）、撞外國同名（Liverpool、Arctic Henge、Sikkim/Kazakhstan 湖）
- 157 筆未取證：多為日落/日出/星空時段照、或眺望點本體（Alyeska、六甲山天覽台、Space Needle 台）