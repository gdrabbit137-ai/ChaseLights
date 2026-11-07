# CL-DATA-24 全庫景點機械評分（catalog scoring）

評分範圍：218 places × 406 opportunities（全數來自庫內契約；唯讀分析）。
Rubric 權重（v2）：subject 25 / weather_light 20 / verifiability 20 / differentiation 15 / scenic_beauty 20（CL-DATA-26 owner ruling 2026-11-07：safe_access 移除、scenic_beauty 20）。
輸入指紋：`451c8ad74bffde2b…`（重跑可驗證確定性）。

- 全庫加權均分：**3.81 / 5**；中位數：**3.83 / 5**（僅計 scenic_beauty 有庫內證據的景點；scenic_beauty 無證據者誠實標 unknown＝**155** 個，不虛構分數）。
- 區域分布：jp=42, tw=93, us=83
- 弱點清單筆數：低 weather_light **6**、低 verifiability **308**、5km 群聚 **16**。

## 五維判定規則（機械、可重跑）

| 維度 | 判定 |
|---|---|
| subject_strength | 契約條件豐富度：≥2 指標 +1、≥4 +1、有 QUALITY/BONUS/MODIFIER +1、天文/題材狀態 family +1 |
| weather_light | 光線/時間窗（light/sunset/sunrise/golden/blue/夜間窗）＝5；深夜天文組＝5；季節窗＝5；雲海 LCL 組 REQUIRED＝4；雲量主導＝3；僅靜態地景條件＝1–2 |
| verifiability | provenance 完整度：geometry verified/derived、targets evidence_refs、claim_refs+threshold_source、access/safety 非佔位、navigation confidence |
| differentiation | 機械 5km 最近鄰（>15→5、>8→4、>5→3、≤5→1） |
| scenic_beauty (v2) | 庫內分類/評分證據機械判定：base 2 + s1 攝影社群(+1) + s2 官方A級/UNESCO/三大類分類(+1，頂級＋1) + s3 攻略清單頻率≥2獨立來源(+1)，上限 5；無證據＝unknown（不虛構） |

## 排名（前 20 / 後 20）

### Top 20

| 排名 | place | 名稱 | 區域 | 題材數 | 加權總分 | 五維 |
|---|---|---|---|---|---|---|
| 1 | `jp-044` | 十二湖・青池 | jp | 1 | **4.6** | 5/5/3.0/5/5 |
| 2 | `jp-048` | 北山崎（三陸断崖） | jp | 2 | **4.38** | 4.5/5/2.5/5/5 |
| 3 | `tw-026` | 井仔腳瓦盤鹽田 | tw | 3 | **4.33** | 5/5/3.67/5/3 |
| 4 | `tw-084` | 大農大富平地森林園區 | tw | 3 | **4.23** | 4.33/5/4.0/5/3 |
| 5 | `jp-046` | タウシュベツ川橋梁（幻の橋） | jp | 1 | **4.2** | 5/5/3.0/5/3 |
| 6 | `jp-045` | 地球岬展望台 | jp | 2 | **4.17** | 4.5/5/2.5/5/4 |
| 7 | `us-011` | 大提頓國家公園 | us | 2 | **4.17** | 4.5/5/3.5/5/3 |
| 8 | `us-001` | 大峽谷國家公園 | us | 3 | **4.13** | 4.33/5/3.5/5/3 |
| 9 | `jp-037` | 雲海テラス（トマム） | jp | 2 | **4.1** | 5/5/2.5/5/3 |
| 10 | `tw-089` | 觀霧榛山步道觀景點 | tw | 1 | **4.1** | 5/5/2.5/5/3 |
| 11 | `jp-042` | 森吉山樹氷平（阿仁スキー場） | jp | 2 | **4.05** | 4/5/2.5/5/4 |
| 12 | `jp-047` | 八甲田山樹氷（八甲田ロープウェー） | jp | 1 | **4.05** | 4/5/2.5/5/4 |
| 13 | `tw-088` | 翠峰湖環山步道觀景點 | tw | 2 | **4.0** | 5/5/2.75/4/3 |
| 14 | `us-031` | 落磯山國家公園 | us | 1 | **4.0** | 5/5/2.0/5/3 |
| 15 | `us-055` | 威朗格利-聖埃利亞斯國家公園 | us | 2 | **4.0** | 5/5/2.0/5/3 |
| 16 | `us-069` | 克拉克湖國家公園 | us | 1 | **4.0** | 5/5/2.0/5/3 |
| 17 | `tw-036` | 七星潭 | tw | 4 | **3.99** | 4.75/5/2.25/5/3 |
| 18 | `tw-091` | 司馬庫斯部落觀景點 | tw | 2 | **3.98** | 4.5/5/2.5/5/3 |
| 19 | `us-005` | 拱門國家公園 | us | 2 | **3.98** | 4.5/5/2.5/5/3 |
| 20 | `jp-039` | 津別峠展望台（屈斜路湖雲海） | jp | 1 | **3.95** | 5/5/2.5/4/3 |

### Bottom 20

| 排名 | place | 名稱 | 區域 | 題材數 | 加權總分 | 五維 | 最近景點 (km) |
|---|---|---|---|---|---|---|---|
| 199 | `us-077` | 何塞・黎剎博士公園 | us | 2 | **None** | 4/5/1.5/1/unknown | us-026 (2.61) |
| 200 | `us-078` | 默特爾・愛德華茲公園 | us | 1 | **None** | 4/5/1.5/1/unknown | us-024 (0.88) |
| 201 | `us-079` | 斯諾夸爾米瀑布 | us | 1 | **None** | 5/5/1.5/5/unknown | us-077 (36.48) |
| 202 | `us-080` | 欺騙海峽州立公園 | us | 2 | **None** | 4.5/5/1.5/5/unknown | us-087 (79.74) |
| 203 | `us-081` | 雷尼爾山・天堂區 | us | 2 | **None** | 5/5/1.5/1/unknown | us-082 (2.02) |
| 204 | `us-082` | 雷尼爾山・倒影湖 | us | 1 | **None** | 5/5/2.0/1/unknown | us-012 (0.08) |
| 205 | `us-083` | 雷尼爾山・日出區 | us | 2 | **None** | 4.5/5/1.5/4/unknown | us-084 (10.7) |
| 206 | `us-084` | 雷尼爾山・蒂普蘇湖 | us | 1 | **None** | 5/5/1.5/4/unknown | us-083 (10.7) |
| 207 | `us-085` | 紅寶石海灘 | us | 1 | **None** | 5/5/1.5/1/unknown | us-019 (0.05) |
| 208 | `us-086` | 里亞爾托海灘／牆中洞 | us | 1 | **None** | 5/5/2.0/5/unknown | us-019 (28.31) |
| 209 | `us-087` | 颶風嶺 | us | 1 | **None** | 5/5/1.5/5/unknown | us-088 (34.65) |
| 210 | `us-088` | 霍雨林 | us | 1 | **None** | 5/5/1.5/5/unknown | us-087 (34.65) |
| 211 | `us-089` | 帕盧斯瀑布 | us | 1 | **None** | 5/5/2.0/5/unknown | us-094 (81.67) |
| 212 | `us-090` | 迪亞布羅湖 | us | 1 | **None** | 5/5/2.0/5/unknown | us-091 (39.5) |
| 213 | `us-091` | 華盛頓山口觀景點 | us | 1 | **None** | 4/5/2.0/5/unknown | us-090 (39.5) |
| 214 | `us-092` | 藝術家角 | us | 1 | **None** | 5/5/1.5/1/unknown | us-093 (2.65) |
| 215 | `us-093` | 畫湖 | us | 1 | **None** | 5/5/2.0/1/unknown | us-092 (2.65) |
| 216 | `us-094` | 斯特普托山丘 | us | 1 | **None** | 4/5/1.5/5/unknown | us-089 (81.67) |
| 217 | `us-095` | 失望角州立公園 | us | 1 | **None** | 5/5/1.5/5/unknown | us-017 (141.15) |
| 218 | `us-096` | 乾瀑布 | us | 1 | **None** | 5/5/2.0/5/unknown | us-089 (135.64) |

## 弱點清單 A：低 weather_light（模型幫不上忙的景點 → 建議改題材）

| opportunity | place | 分數 |
|---|---|---|
| `jp-030-P01` | jp-030 | 1 |
| `jp-041-P01` | jp-041 | 1 |
| `tw-059-P01` | tw-059 | 1 |
| `tw-060-P01` | tw-060 | 1 |
| `tw-078-P01` | tw-078 | 1 |
| `tw-082-P01` | tw-082 | 2 |

## 弱點清單 B：低 verifiability（資料缺口 → 建議補資料）

| opportunity | place | 分數 | 缺口 |
|---|---|---|---|
| `jp-002-P01` | jp-002 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-003-P01` | jp-003 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-004-P01` | jp-004 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-005-P02` | jp-005 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-006-P01` | jp-006 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-007-P01` | jp-007 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-008-P01` | jp-008 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-009-P01` | jp-009 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-010-P02` | jp-010 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-013-P01` | jp-013 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-016-P02` | jp-016 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-019-P01` | jp-019 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-020-P01` | jp-020 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-025-P02` | jp-025 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-028-P02` | jp-028 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-029-P02` | jp-029 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-030-P01` | jp-030 | 1.0 | geometry_not_verified, targets_missing_evidence_refs, conditions_missing_claim_or_threshold_source, access_note_placeholder |
| `jp-031-P02` | jp-031 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-032-P02` | jp-032 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-036-P01` | jp-036 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-036-P03` | jp-036 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `jp-041-P01` | jp-041 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, conditions_missing_claim_or_threshold_source |
| `tw-001-P01` | tw-001 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-001-P02` | tw-001 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-001-P03` | tw-001 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-002-P01` | tw-002 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-002-P02` | tw-002 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-002-P03` | tw-002 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-003-P01` | tw-003 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-003-P02` | tw-003 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-003-P03` | tw-003 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-004-P01` | tw-004 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-004-P03` | tw-004 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-004-P04` | tw-004 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-005-P01` | tw-005 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-005-P02` | tw-005 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-008-P01` | tw-008 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-008-P02` | tw-008 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-008-P03` | tw-008 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-009-P02` | tw-009 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-010-P01` | tw-010 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-010-P02` | tw-010 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-010-P03` | tw-010 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-011-P01` | tw-011 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-011-P02` | tw-011 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-012-P01` | tw-012 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-012-P02` | tw-012 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-013-P01` | tw-013 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-013-P02` | tw-013 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-014-P01` | tw-014 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-014-P02` | tw-014 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-015-P01` | tw-015 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-015-P02` | tw-015 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-017-P01` | tw-017 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-017-P02` | tw-017 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-017-P03` | tw-017 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-018-P02` | tw-018 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-018-P03` | tw-018 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-019-P01` | tw-019 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-019-P02` | tw-019 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-019-P03` | tw-019 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-019-P04` | tw-019 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-019-P05` | tw-019 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-019-P06` | tw-019 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-020-P01` | tw-020 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-020-P02` | tw-020 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-020-P03` | tw-020 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-020-P04` | tw-020 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-021-P01` | tw-021 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-021-P02` | tw-021 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-022-P01` | tw-022 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-022-P02` | tw-022 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-022-P03` | tw-022 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-022-P04` | tw-022 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-023-P01` | tw-023 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-023-P02` | tw-023 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-023-P03` | tw-023 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-024-P01` | tw-024 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-024-P02` | tw-024 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-024-P03` | tw-024 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-024-P04` | tw-024 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-024-P05` | tw-024 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-025-P01` | tw-025 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-025-P02` | tw-025 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-026-P03` | tw-026 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-027-P01` | tw-027 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-027-P02` | tw-027 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-027-P03` | tw-027 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-028-P01` | tw-028 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-028-P02` | tw-028 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-028-P03` | tw-028 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-028-P04` | tw-028 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-030-P01` | tw-030 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-030-P02` | tw-030 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-031-P01` | tw-031 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-031-P02` | tw-031 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-032-P01` | tw-032 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-032-P02` | tw-032 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-032-P03` | tw-032 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-033-P01` | tw-033 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-033-P02` | tw-033 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-034-P01` | tw-034 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-034-P03` | tw-034 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P01` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P02` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P03` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P04` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P05` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P06` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P07` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P08` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P09` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-035-P10` | tw-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-036-P02` | tw-036 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-036-P03` | tw-036 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-036-P04` | tw-036 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-037-P01` | tw-037 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-038-P01` | tw-038 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-038-P02` | tw-038 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-040-P01` | tw-040 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-040-P02` | tw-040 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-040-P03` | tw-040 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-040-P04` | tw-040 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-040-P05` | tw-040 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-040-P06` | tw-040 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-041-P01` | tw-041 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-041-P02` | tw-041 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-041-P03` | tw-041 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-041-P04` | tw-041 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-041-P05` | tw-041 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-042-P01` | tw-042 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-043-P01` | tw-043 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-043-P02` | tw-043 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-043-P03` | tw-043 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-043-P04` | tw-043 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-044-P01` | tw-044 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-044-P02` | tw-044 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-044-P03` | tw-044 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-045-P01` | tw-045 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-045-P02` | tw-045 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-045-P03` | tw-045 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-045-P04` | tw-045 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-045-P05` | tw-045 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-046-P01` | tw-046 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-046-P02` | tw-046 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-047-P01` | tw-047 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-047-P02` | tw-047 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-047-P03` | tw-047 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-048-P01` | tw-048 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-049-P01` | tw-049 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-049-P02` | tw-049 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-049-P03` | tw-049 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-050-P01` | tw-050 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-051-P01` | tw-051 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-051-P02` | tw-051 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-053-P01` | tw-053 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-053-P02` | tw-053 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-054-P01` | tw-054 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-054-P02` | tw-054 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-055-P01` | tw-055 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-056-P01` | tw-056 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-056-P02` | tw-056 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-057-P01` | tw-057 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-057-P02` | tw-057 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-059-P01` | tw-059 | 1.0 | geometry_not_verified, targets_missing_evidence_refs, conditions_missing_claim_or_threshold_source, access_note_placeholder |
| `tw-060-P01` | tw-060 | 1.0 | geometry_not_verified, targets_missing_evidence_refs, conditions_missing_claim_or_threshold_source, access_note_placeholder |
| `tw-060-P02` | tw-060 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-060-P03` | tw-060 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-061-P01` | tw-061 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-061-P02` | tw-061 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-064-P01` | tw-064 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-064-P02` | tw-064 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-065-P01` | tw-065 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-066-P01` | tw-066 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-067-P01` | tw-067 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-069-P01` | tw-069 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-070-P01` | tw-070 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-070-P02` | tw-070 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-071-P01` | tw-071 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-071-P02` | tw-071 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-072-P01` | tw-072 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-072-P02` | tw-072 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-073-P01` | tw-073 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-075-P01` | tw-075 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-076-P01` | tw-076 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-076-P02` | tw-076 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-077-P01` | tw-077 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-078-P01` | tw-078 | 1.0 | geometry_not_verified, targets_missing_evidence_refs, conditions_missing_claim_or_threshold_source, access_note_placeholder |
| `tw-079-P01` | tw-079 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-080-P01` | tw-080 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-080-P02` | tw-080 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-082-P02` | tw-082 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-082-P03` | tw-082 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-082-P04` | tw-082 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-082-P05` | tw-082 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-082-P07` | tw-082 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-082-P08` | tw-082 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-082-P09` | tw-082 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-085-P01` | tw-085 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-085-P02` | tw-085 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-085-P03` | tw-085 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-086-P01` | tw-086 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-086-P02` | tw-086 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-086-P03` | tw-086 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-005-P01` | us-005 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-006-P01` | us-006 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-006-P02` | us-006 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-007-P01` | us-007 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-007-P02` | us-007 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-009-P01` | us-009 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-010-P01` | us-010 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-012-P01` | us-012 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-012-P02` | us-012 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-013-P01` | us-013 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-014-P01` | us-014 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-014-P02` | us-014 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-014-P03` | us-014 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-015-P01` | us-015 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-015-P02` | us-015 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-016-P01` | us-016 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-016-P02` | us-016 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-017-P01` | us-017 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-018-P01` | us-018 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-018-P02` | us-018 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-019-P01` | us-019 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-019-P02` | us-019 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-020-P01` | us-020 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-020-P02` | us-020 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-021-P01` | us-021 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-023-P01` | us-023 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-025-P01` | us-025 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-025-P02` | us-025 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-027-P01` | us-027 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-028-P01` | us-028 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-029-P01` | us-029 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-030-P01` | us-030 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-031-P01` | us-031 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-033-P01` | us-033 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-035-P02` | us-035 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-036-P01` | us-036 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-037-P02` | us-037 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-038-P01` | us-038 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-039-P01` | us-039 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-039-P02` | us-039 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-040-P01` | us-040 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-041-P01` | us-041 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-044-P01` | us-044 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-045-P01` | us-045 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-046-P01` | us-046 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-047-P01` | us-047 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-048-P01` | us-048 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-048-P02` | us-048 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-050-P01` | us-050 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-050-P02` | us-050 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-051-P01` | us-051 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-051-P02` | us-051 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-052-P01` | us-052 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-052-P02` | us-052 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-055-P01` | us-055 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-055-P02` | us-055 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-056-P01` | us-056 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-057-P01` | us-057 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-059-P01` | us-059 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-059-P02` | us-059 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-060-P01` | us-060 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-060-P02` | us-060 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-061-P01` | us-061 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-061-P02` | us-061 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-062-P01` | us-062 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-063-P01` | us-063 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-064-P01` | us-064 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-069-P01` | us-069 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-071-P02` | us-071 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-071-P03` | us-071 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-072-P01` | us-072 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-072-P02` | us-072 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-073-P01` | us-073 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-073-P02` | us-073 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-074-P01` | us-074 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-074-P02` | us-074 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-075-P01` | us-075 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-075-P02` | us-075 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-076-P01` | us-076 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-076-P02` | us-076 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-077-P01` | us-077 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-077-P02` | us-077 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-078-P03` | us-078 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-079-P01` | us-079 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-080-P01` | us-080 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-080-P02` | us-080 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-081-P01` | us-081 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-081-P02` | us-081 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-082-P01` | us-082 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-083-P01` | us-083 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-083-P02` | us-083 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-084-P01` | us-084 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-085-P01` | us-085 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-086-P01` | us-086 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-087-P01` | us-087 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-088-P01` | us-088 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-089-P01` | us-089 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-090-P01` | us-090 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-091-P01` | us-091 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-092-P01` | us-092 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-093-P01` | us-093 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-094-P01` | us-094 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-095-P01` | us-095 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-096-P01` | us-096 | 2.0 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |

## 弱點清單 C：高重叠區（5km 群聚 → 檢討差異化/候選裁撤，僅建議）

- 橫濱山下公園（jp-016，最近 0.36 km）、橫濱港未來21（jp-020，最近 0.36 km）
- 福岡城跡（jp-032，最近 3.09 km）、福岡塔（jp-035，最近 3.09 km）
- 蔵王樹氷（蔵王ロープウェイ・山形側）（jp-038，最近 2.6 km）、蔵王御釜（五色湖）（jp-049，最近 2.6 km）
- 淡水漁人碼頭（tw-003，最近 4.84 km）、關渡大橋（tw-006，最近 3.36 km）、觀音山硬漢嶺（tw-008，最近 1.42 km）、八里崁頭里・淡江大橋觀景點（tw-086，最近 1.42 km）
- 望幽谷（tw-009，最近 2.96 km）、和平島（tw-010，最近 0.63 km）、正濱漁港（tw-054，最近 0.63 km）
- 鵝鑾鼻燈塔（tw-029，最近 3.02 km）、龍磐公園／草原海岸（tw-076，最近 3.02 km）
- 抹茶山（tw-031，最近 1.61 km）、五峰旗瀑布（tw-055，最近 1.61 km）、渭水之丘／櫻花陵園（tw-098，最近 3.28 km）
- 雪山主峰（tw-041，最近 3.61 km）、雪山北峰（tw-042，最近 3.08 km）、大霸尖山（tw-046，最近 3.45 km）、池有山（tw-048，最近 1.71 km）、桃山（tw-049，最近 1.71 km）、品田山（tw-050，最近 2.19 km）
- 金門得月樓（tw-062，最近 2.32 km）、金門慈湖（tw-064，最近 4.74 km）、建功嶼／退潮石板道（tw-078，最近 2.32 km）
- 馬祖南竿（tw-065，最近 3.37 km）、南竿鐵堡／海防礁岩（tw-081，最近 3.37 km）
- 綠島朝日溫泉（tw-068，最近 0.47 km）、帆船鼻大草原／海岬（tw-080，最近 0.47 km）
- 南雅奇岩（tw-072，最近 0.57 km）、南子吝步道（tw-085，最近 0.57 km）
- 雷尼爾山國家公園（us-012，最近 0.08 km）、雷尼爾山・天堂區（us-081，最近 2.02 km）、雷尼爾山・倒影湖（us-082，最近 0.08 km）
- 奧林匹克國家公園（us-019，最近 0.05 km）、紅寶石海灘（us-085，最近 0.05 km）
- 西雅圖太空針塔（us-024，最近 0.88 km）、西雅圖派克市場（us-026，最近 1.33 km）、Kerry Park（us-071，最近 1.1 km）、金色花園公園（us-072，最近 4.06 km）、阿爾基海灘公園（us-073，最近 2.04 km）、煤氣廠公園（us-074，最近 2.6 km）、探索公園（us-075，最近 4.06 km）、漢密爾頓觀景公園（us-076，最近 2.04 km）、何塞・黎剎博士公園（us-077，最近 2.61 km）、默特爾・愛德華茲公園（us-078，最近 0.88 km）
- 藝術家角（us-092，最近 2.65 km）、畫湖（us-093，最近 2.65 km）

> Rubric v2（CL-DATA-25R 重跑）：safe_access 權重移除、scenic_beauty 權重 20，由庫內證據機械判定；scenic_beauty 無證據的景點誠實標 unknown，其加權總分留空（不虛構）。季節窗/封閉期資訊仍保留於 dossier 與契約。
> 本報告為唯讀分析：不改任何 catalog/契約資料；弱點處置（改題材/補資料/裁撤）為建議，決策權在 PM/owner。機器可讀版本：catalog-scoring.json。
