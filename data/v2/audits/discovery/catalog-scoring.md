# CL-DATA-24 全庫景點機械評分（catalog scoring）

評分範圍：197 places × 374 opportunities（全數來自庫內契約；唯讀分析）。
Rubric 權重：subject 25 / weather_light 20 / verifiability 20 / differentiation 15 / safe_access 20（沿用 CL-DATA-23）。
輸入指紋：`1401e35027ba985a…`（重跑可驗證確定性）。

- 全庫加權均分：**3.37 / 5**；中位數：**3.42 / 5**（健康度基準）。
- 區域分布：jp=29, tw=85, us=83
- 弱點清單筆數：低 weather_light **5**、低 verifiability **307**、5km 群聚 **15**。

## 五維判定規則（機械、可重跑）

| 維度 | 判定 |
|---|---|
| subject_strength | 契約條件豐富度：≥2 指標 +1、≥4 +1、有 QUALITY/BONUS/MODIFIER +1、天文/題材狀態 family +1 |
| weather_light | 光線/時間窗（light/sunset/sunrise/golden/blue/夜間窗）＝5；深夜天文組＝5；季節窗＝5；雲海 LCL 組 REQUIRED＝4；雲量主導＝3；僅靜態地景條件＝1–2 |
| verifiability | provenance 完整度：geometry verified/derived、targets evidence_refs、claim_refs+threshold_source、access/safety 非佔位、navigation confidence |
| differentiation | 機械 5km 最近鄰（>15→5、>8→4、>5→3、≤5→1） |
| safe_access | 季節窗(+2)、access/safety 具體(+1/+1)、geometry verified(+1)、altitude(+0.5)、nav high(+0.5) |

## 排名（前 20 / 後 20）

### Top 20

| 排名 | place | 名稱 | 區域 | 題材數 | 加權總分 | 五維 |
|---|---|---|---|---|---|---|
| 1 | `tw-084` | 大農大富平地森林園區 | tw | 3 | **4.6** | 4.33/5/4.0/5/4.83 |
| 2 | `tw-016` | 鳶嘴山 | tw | 1 | **4.5** | 5/3/5.0/5/4.5 |
| 3 | `tw-039` | 池上伯朗大道 | tw | 3 | **4.22** | 4.67/5/2.5/5/4.0 |
| 4 | `tw-026` | 井仔腳瓦盤鹽田 | tw | 3 | **4.2** | 5/5/3.67/5/2.33 |
| 5 | `us-008` | 優勝美地半圓頂 | us | 1 | **4.15** | 5/5/3.5/4/3.0 |
| 6 | `us-001` | 大峽谷國家公園 | us | 3 | **4.13** | 4.33/5/3.5/5/3.0 |
| 7 | `tw-083` | 雲山水夢幻湖 | tw | 3 | **4.12** | 4.33/5/2.67/4/4.5 |
| 8 | `tw-029` | 鵝鑾鼻燈塔 | tw | 2 | **4.1** | 5/5/4.0/1/4.5 |
| 9 | `jp-010` | 大石公園 | jp | 2 | **4.08** | 3.5/5/3.25/5/4.0 |
| 10 | `us-011` | 大提頓國家公園 | us | 2 | **4.08** | 4.5/5/3.5/5/2.5 |
| 11 | `jp-023` | 京都清水寺 | jp | 1 | **4.05** | 4/5/2.5/5/4.0 |
| 12 | `jp-033` | 唐津城 | jp | 2 | **4.05** | 4/5/2.5/5/4.0 |
| 13 | `jp-026` | 出雲大社 | jp | 1 | **4.0** | 5/5/3.0/5/2.0 |
| 14 | `tw-006` | 關渡大橋 | tw | 3 | **4.0** | 5/5/4.0/1/4.0 |
| 15 | `us-065` | 楚加奇州立公園 | us | 1 | **4.0** | 5/5/3.0/5/2.0 |
| 16 | `tw-007` | 碧潭 | tw | 2 | **3.98** | 4.5/5/2.75/4/3.5 |
| 17 | `tw-058` | 澎湖跨海大橋 | tw | 2 | **3.92** | 4.5/5/2.5/4/3.5 |
| 18 | `jp-034` | 長崎哥拉巴園 | jp | 2 | **3.9** | 4/5/2.75/5/3.0 |
| 19 | `us-004` | 紀念碑谷 | us | 1 | **3.9** | 5/5/2.5/5/2.0 |
| 20 | `us-035` | 沃斯堡牲畜市場 | us | 1 | **3.9** | 5/5/1.5/5/3.0 |

### Bottom 20

| 排名 | place | 名稱 | 區域 | 題材數 | 加權總分 | 五維 | 最近景點 (km) |
|---|---|---|---|---|---|---|---|
| 178 | `tw-065` | 馬祖南竿 | tw | 1 | **2.9** | 5/5/1.5/1/1.0 | tw-081 (3.37) |
| 179 | `us-012` | 雷尼爾山國家公園 | us | 2 | **2.9** | 4/5/1.75/1/2.0 | us-082 (0.08) |
| 180 | `us-072` | 金色花園公園 | us | 2 | **2.9** | 5/5/1.5/1/1.0 | us-075 (4.06) |
| 181 | `us-085` | 紅寶石海灘 | us | 1 | **2.9** | 5/5/1.5/1/1.0 | us-019 (0.05) |
| 182 | `us-092` | 藝術家角 | us | 1 | **2.9** | 5/5/1.5/1/1.0 | us-093 (2.65) |
| 183 | `tw-054` | 正濱漁港 | tw | 2 | **2.83** | 4.5/5/1.75/1/1.0 | tw-010 (0.63) |
| 184 | `tw-003` | 淡水漁人碼頭 | tw | 3 | **2.82** | 4.67/5/1.5/1/1.0 | tw-086 (4.84) |
| 185 | `tw-049` | 桃山 | tw | 3 | **2.82** | 4.67/5/1.5/1/1.0 | tw-048 (1.71) |
| 186 | `tw-064` | 金門慈湖 | tw | 2 | **2.77** | 4.5/5/1.5/1/1.0 | tw-078 (4.74) |
| 187 | `tw-080` | 帆船鼻大草原／海岬 | tw | 2 | **2.77** | 4.5/5/1.5/1/1.0 | tw-068 (0.47) |
| 188 | `us-073` | 阿爾基海灘公園 | us | 2 | **2.77** | 4.5/5/1.5/1/1.0 | us-076 (2.04) |
| 189 | `us-075` | 探索公園 | us | 2 | **2.77** | 4.5/5/1.5/1/1.0 | us-072 (4.06) |
| 190 | `tw-076` | 龍磐公園／草原海岸 | tw | 2 | **2.65** | 4/5/1.5/1/1.0 | tw-029 (3.02) |
| 191 | `us-074` | 煤氣廠公園 | us | 2 | **2.65** | 4/5/1.5/1/1.0 | us-071 (2.6) |
| 192 | `us-076` | 漢密爾頓觀景公園 | us | 2 | **2.65** | 4/5/1.5/1/1.0 | us-073 (2.04) |
| 193 | `us-077` | 何塞・黎剎博士公園 | us | 2 | **2.65** | 4/5/1.5/1/1.0 | us-026 (2.61) |
| 194 | `us-078` | 默特爾・愛德華茲公園 | us | 1 | **2.65** | 4/5/1.5/1/1.0 | us-024 (0.88) |
| 195 | `jp-030` | 鳴門海峽漩渦 | jp | 1 | **1.85** | 2/1/1.0/5/1.0 | jp-027 (78.29) |
| 196 | `tw-059` | 奎壁山 | tw | 1 | **1.7** | 2/1/1.0/4/1.0 | tw-061 (11.63) |
| 197 | `tw-078` | 建功嶼／退潮石板道 | tw | 1 | **1.25** | 2/1/1.0/1/1.0 | tw-062 (2.32) |

## 弱點清單 A：低 weather_light（模型幫不上忙的景點 → 建議改題材）

| opportunity | place | 分數 |
|---|---|---|
| `jp-030-P01` | jp-030 | 1 |
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
- 淡水漁人碼頭（tw-003，最近 4.84 km）、關渡大橋（tw-006，最近 3.36 km）、觀音山硬漢嶺（tw-008，最近 1.42 km）、八里崁頭里・淡江大橋觀景點（tw-086，最近 1.42 km）
- 望幽谷（tw-009，最近 2.96 km）、和平島（tw-010，最近 0.63 km）、正濱漁港（tw-054，最近 0.63 km）
- 鵝鑾鼻燈塔（tw-029，最近 3.02 km）、龍磐公園／草原海岸（tw-076，最近 3.02 km）
- 抹茶山（tw-031，最近 1.61 km）、五峰旗瀑布（tw-055，最近 1.61 km）
- 雪山主峰（tw-041，最近 3.61 km）、雪山北峰（tw-042，最近 3.08 km）、大霸尖山（tw-046，最近 3.45 km）、池有山（tw-048，最近 1.71 km）、桃山（tw-049，最近 1.71 km）、品田山（tw-050，最近 2.19 km）
- 金門得月樓（tw-062，最近 2.32 km）、金門慈湖（tw-064，最近 4.74 km）、建功嶼／退潮石板道（tw-078，最近 2.32 km）
- 馬祖南竿（tw-065，最近 3.37 km）、南竿鐵堡／海防礁岩（tw-081，最近 3.37 km）
- 綠島朝日溫泉（tw-068，最近 0.47 km）、帆船鼻大草原／海岬（tw-080，最近 0.47 km）
- 南雅奇岩（tw-072，最近 0.57 km）、南子吝步道（tw-085，最近 0.57 km）
- 雷尼爾山國家公園（us-012，最近 0.08 km）、雷尼爾山・天堂區（us-081，最近 2.02 km）、雷尼爾山・倒影湖（us-082，最近 0.08 km）
- 奧林匹克國家公園（us-019，最近 0.05 km）、紅寶石海灘（us-085，最近 0.05 km）
- 西雅圖太空針塔（us-024，最近 0.88 km）、西雅圖派克市場（us-026，最近 1.33 km）、Kerry Park（us-071，最近 1.1 km）、金色花園公園（us-072，最近 4.06 km）、阿爾基海灘公園（us-073，最近 2.04 km）、煤氣廠公園（us-074，最近 2.6 km）、探索公園（us-075，最近 4.06 km）、漢密爾頓觀景公園（us-076，最近 2.04 km）、何塞・黎剎博士公園（us-077，最近 2.61 km）、默特爾・愛德華茲公園（us-078，最近 0.88 km）
- 藝術家角（us-092，最近 2.65 km）、畫湖（us-093，最近 2.65 km）

> 本報告為唯讀分析：不改任何 catalog/契約資料；弱點處置（改題材/補資料/裁撤）為建議，決策權在 PM/owner。機器可讀版本：catalog-scoring.json。
