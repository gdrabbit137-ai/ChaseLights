# mountain_view 批次 111 筆 — 照片證據裁定總表（2026-10-26）

## 產出檔案
- `FINAL_111_verdicts.csv` — 逐筆裁定（原判 vs 照片後判）
- `vision_findings.json` — 每筆照片分析內容
- `round2_list.json` — 補查清單（26 筆）
- `_manifest.csv` + `harvest_state.json` — 377 張照片與 Commons 來源對照
- `sheets/` — 每景點 2×2 拼圖

## 流程統計
- 採集：111/111 筆搜尋，377 張照片下載（Commons 1600px 縮圖）
- 視覺分析：98/111 筆有照片證據（含 pilot 10 筆），13 筆 0 命中待 round-2
- **照片改變原判：24 筆**（見下）

## 最終分布（111 筆）
- D（人文/無對應題材）：44
- B:mountain_view：28 ＋ 雙掛（+reflection 6、+seasonal_plant 3、其他 2）
- B:overlook：14 ＋ 雙掛 2
- B:seasonal_plant：5
- B:sunrise/cloud_sea：2（阿里山）
- KEEP（冰河題材候選）：5

## 照片改變原判的 24 筆（需 owner 複審）

### 升級（原 D 或低判 → 有題材）
1. **jp-023-P01 清水寺** D→B:seasonal_plant（舞台被紅葉主導）
2. **jp-033-P02 唐津城** B:overlook→B:seasonal_plant（桜と唐津城強證據）
3. **tw-024-P03 小笠原山** B:mountain_view→B:sunrise+cloud_sea（破曉雲海雙證據）
4. **us-050-P01 Juneau** D→B:overlook（Mt Roberts 俯瞰港灣）
5. **us-052-P02 Homer Spit** D→B:mountain_view（高點沙嘴+雪峰海灣）
6. **us-072-P01 Golden Gardens** D→B:sunset（海灘日落火燒雲為絕對主體）
7. **us-083-P02 Bryce** B:mountain_view→B:overlook（日出金光照 hoodoos）
8. **us-038-P01 Smokies** B:mountain_view→B:overlook（Newfound Gap 眺望台）
9. **us-046-P01 Hatcher Pass** →B:overlook（雲海繞山全景）
10. **us-060-P02 Glacier Bay** KEEP→B:mountain_view（水面峽灣冰川全景）

### 降級（原掛題材被證據削弱）
11. **jp-009-P01 中瀬沼** reflection 移除（沼面倒影未取證）
12. **tw-084-P09 大農大富** →D（道路+遠山背景，非山景主體）
13. **tw-007-P03 碧潭** →D（遊憩河畔）
14. **tw-018-P01 日月潭向山** →D（纜車站建築主體）
15. **tw-039-P01 伯朗大道** →D（稻田+道路主體，稻浪屬農田語意）
16. **us-049/068/070/066/078-P02** →D（街景/河谷/礦場/苔原/濱海公園，非山景主體）

### 題材綁定調整
17. **us-027/us-031/us-081** 倒影/季節元素降為次要或保持（湖小風大、花田主導等）
18. **us-048 Portage** B:mountain_view→KEEP（冰河題材候選第 4 例）

## 門檻校訂證據（供模板修訂）
1. **倒影 wind 門檻**：us-027 風面湖無倒影 vs us-062/us-069/us-031/us-013 鏡面 → wind<3 [provisional] 證據一致
2. **大煙山悖論**：us-038 谷中霧是主題不是障礙 → overlook「低雲≤30%」會反向錯殺，建議 per-opportunity 覆寫
3. **能見度分級**：摩周湖/金龍山（能見度主判據）vs Grand Prismatic（近景主體）→ overlook 模板允許 visibility 權重差異
4. **地圖/古籍/衛星照過濾**：Def/地圖/djvu/Landsat 標題黑名單已證必要

## Round-2 補查清單（26 筆）
撞名/0 命中/主體未取證，已帶修正查詢詞（見 round2_list.json）。重點：jp-002 姿見池、jp-021 西穗高口、tw-052 崗山之眼、tw-057 加羅湖、us-063 Talkeetna+Denali、us-064 Alyeska 纜車眺望點、us-075 Discovery Park（撞英國 Liverpool）。