# CL-DATA-26 — rubric v2 候選重評報告（2026-11-07）

owner 裁決：移除 safe_access，其 20 分權重改給 scenic_beauty。rubric v2（權重和=100）：
subject_strength 25 / weather_light_dependency 20 / verifiability 20 / differentiation 15 / scenic_beauty 20。
scenic_beauty 機械化分級（dossier 證據，逐筆存 candidates JSON `scenic_beauty_evidence`）：
s1 攝影社群熱度（攝影社群/攝影平台專題收錄）0/1；s2 官方分類（官方 A 級・全国観光資源評価特A級・世界遺産・日本三大〜・八景/百選類）0/1；s3 攻略清單文出現頻率（≥2 獨立清單文）0/1；
分數 = 2 + s1 + s2 + s3；世界遺産／特A級／三大之首／観光資源台帳 A 級加 +1（上限 5）。
safe_access 移出評分；其「季節窗/封閉期」資訊（seasonal_window、access_note、safety_note）仍完整保留於 dossier 與契約要求——只是不再影響評分。
v1 分數欄位（weighted_total_v1 / rubric_v1）保留供對照（jp-north 以其原 1/2/1/1/1 相對權重原值重現）。

## v2 納入清單（≥3.8）

### jp-north（14 個）

| # | id | 名稱 | v2 分數 | v1 對照 |
|---|---|---|---|---|
| 1 | jp-north-zao-juhyo | 蔵王樹氷（蔵王ロープウェイ・山形側） | 5.00 | 4.83 |
| 2 | jp-north-unkai-terrace-tomamu | 雲海テラス（トマム） | 4.80 | 5.00 |
| 3 | jp-north-shiretoko-utoro-ryuhyo | 知床ウトロ流氷（プユニ岬） | 4.80 | 4.67 |
| 4 | jp-north-biei-blue-pond | 青い池（美瑛・白金） | 4.60 | 4.67 |
| 5 | jp-north-hakkoda-juhyo | 八甲田山樹氷（八甲田ロープウェー） | 4.60 | 4.33 |
| 6 | jp-north-moriyoshi-juhyo | 森吉山樹氷平（阿仁スキー場） | 4.55 | 4.67 |
| 7 | jp-north-aoike-junikako | 十二湖・青池 | 4.55 | 4.50 |
| 8 | jp-north-kitayamazaki | 北山崎（三陸断崖） | 4.55 | 4.33 |
| 9 | jp-north-tsubetsu-toge | 津別峠展望台（屈斜路湖雲海） | 4.35 | 4.67 |
| 10 | jp-north-bihoro-toge | 美幌峠展望台 | 4.35 | 4.67 |
| 11 | jp-north-chikyu-misaki | 地球岬展望台 | 4.35 | 4.33 |
| 12 | jp-north-farm-tomita-lavender | 富田農場ラベンダーイースト | 4.15 | 4.50 |
| 13 | jp-north-taushubetsu-bridge | タウシュベツ川橋梁（幻の橋） | 4.15 | 4.33 |
| 14 | jp-north-zao-okama | 蔵王御釜（五色湖） | 4.15 | 4.17 |
| 15 | jp-north-monaiyama-unkai | 毛無山展望所（小樽雲海） | 3.55 | 4.17 |
| 16 | jp-north-appi-unkai | 安比高原雲海ゴンドラ | 3.30 | 4.00 |

### tw（8 個）

| # | id | 名稱 | v2 分數 | v1 對照 |
|---|---|---|---|---|
| 1 | tw-smangus | 司馬庫斯部落觀景點 | 4.40 | 4.00 |
| 2 | tw-dashan-43k-cloudsea | 大雪山森林遊樂區43K觀景台 | 4.25 | 4.65 |
| 3 | tw-cuifeng-lake | 翠峰湖環山步道觀景點 | 4.25 | 4.45 |
| 4 | tw-guanwu-zhenshan | 觀霧榛山步道觀景點 | 4.20 | 4.40 |
| 5 | tw-dongju-lighthouse | 東莒燈塔（東犬燈塔） | 4.15 | 3.95 |
| 6 | tw-fushoushan-farm | 福壽山農場觀景點 | 4.00 | 4.00 |
| 7 | tw-tatajia-couple-trees | 塔塔加夫妻樹／鹿林山觀景點 | 3.90 | 3.90 |
| 8 | tw-weishui-hill | 渭水之丘／櫻花陵園 | 3.80 | 4.00 |
| 9 | tw-jialulan-coast | 加路蘭海岸遊憩區 | 3.70 | 4.30 |
| 10 | tw-haowanjiao | 半天寮好望角 | 3.70 | 3.90 |
| 11 | tw-beiguan-tide-park | 北關海潮公園 | 3.60 | 4.00 |
| 12 | tw-qingjing-farm | 清境農場霧上觀景帶 | 3.45 | 3.65 |
| 13 | tw-qingtiangang | 擎天崗草原 | 3.20 | 3.80 |

## 異動清單（因換尺跨 3.8 線）

### 移出（v1 ≥3.8 → v2 <3.8）5 個

| id | 名稱 | v1 → v2 | 主因 |
|---|---|---|---|
| jp-north-monaiyama-unkai | 毛無山展望所（小樽雲海） | 4.17 → 3.55 | scenic_beauty=2（單一攻略專欄源，清單頻率不足） |
| jp-north-appi-unkai | 安比高原雲海ゴンドラ | 4.00 → 3.30 | scenic_beauty=2＋verifiability=2（僅官方新聞稿片段） |
| tw-jialulan-coast | 加路蘭海岸遊憩區 | 4.30 → 3.70 | scenic_beauty=2（僅東管處單一體系提及） |
| tw-haowanjiao | 半天寮好望角 | 3.90 → 3.70 | 跌破線（scenic_beauty=4 仍不敵低 subject/weather 權重結構） |
| tw-beiguan-tide-park | 北關海潮公園 | 4.00 → 3.60 | scenic_beauty=3，移除 safe_access=5 後失分 |
| tw-qingtiangang | 擎天崗草原 | 3.80 → 3.20 | scenic_beauty=2（弱源：threads AI 帖＋單篇部落格） |

（備註：tw-qingjing-farm v1=3.65 本已在 3.8 線下，v2=3.45 續留線下，不屬跨線異動。）

### 移入（v1 <3.8 → v2 ≥3.8）0 個

無。

## 維持線上者（v1 ≥3.8 且 v2 ≥3.8）
jp-north 14 個、tw 8 個（見上表）。

## 誠實聲明
- jp-north-shortlist.md 上方 12 候選表為 CL-DATA-23 首輪試跑歷史紀錄（另一 12-候選清單），未重評；本報告涵蓋兩張機器可讀短名單 JSON 的全部 16+14 個候選（含 tw 已剔除的 wangyou-forest 亦補評分欄位）。
- scenic_beauty 為 dossier 證據之機械化分級，非裸品味判斷；分數、訊號與證據字串全部可由短名單 JSON 逐筆回查。
- 本票不改動 catalog：僅 shortlist/rubric 工具與報告。

