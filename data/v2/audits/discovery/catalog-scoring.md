# CL-DATA-24 全庫景點機械評分（catalog scoring）

評分範圍：400 places × 625 opportunities（全數來自庫內契約；唯讀分析）。
Rubric 權重（v2）：subject 25 / weather_light 20 / verifiability 20 / differentiation 15 / scenic_beauty 20（CL-DATA-26 owner ruling 2026-11-07：safe_access 移除、scenic_beauty 20）。
輸入指紋：`04c5c4f9e43ff45f…`（重跑可驗證確定性）。

- 全庫加權均分：**3.97 / 5**；中位數：**4.04 / 5**（僅計 scenic_beauty 有庫內證據的景點；scenic_beauty 無證據者誠實標 unknown＝**232** 個，不虛構分數）。
- 區域分布：jp=94, tw=156, us=150
- 弱點清單筆數：低 weather_light **12**、低 verifiability **10**、5km 群聚 **35**。

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
| 2 | `us-102` | 摩特諾瑪瀑布 | us | 1 | **4.5** | 5/5/4.5/5/3 |
| 3 | `us-107` | 出口冰河・冰河舌谷景 | us | 1 | **4.45** | 5/5/5.0/4/3 |
| 4 | `jp-051` | 嚴島神社・宮島大鳥居 | jp | 1 | **4.4** | 5/5/3.0/5/4 |
| 5 | `us-031` | 落磯山國家公園 | us | 1 | **4.4** | 5/5/4.0/5/3 |
| 6 | `us-055` | 威朗格利-聖埃利亞斯國家公園 | us | 2 | **4.4** | 5/5/4.0/5/3 |
| 7 | `us-069` | 克拉克湖國家公園 | us | 1 | **4.4** | 5/5/4.0/5/3 |
| 8 | `us-086` | 里亞爾托海灘／牆中洞 | us | 1 | **4.4** | 5/5/4.0/5/3 |
| 9 | `us-101` | 雷神之井 | us | 1 | **4.4** | 5/5/4.0/5/3 |
| 10 | `us-103` | 干草堆岩・坎農海灘 | us | 1 | **4.4** | 5/5/4.0/5/3 |
| 11 | `jp-048` | 北山崎（三陸断崖） | jp | 2 | **4.38** | 4.5/5/2.5/5/5 |
| 12 | `jp-002` | 旭岳 | jp | 1 | **4.3** | 5/5/3.5/5/3 |
| 13 | `jp-052` | 備中松山城・雲海（天空の城） | jp | 1 | **4.3** | 5/5/2.5/5/4 |
| 14 | `jp-072` | 白川鄉合掌村 | jp | 1 | **4.3** | 5/5/2.5/5/4 |
| 15 | `tw-071` | 小琉球花瓶岩 | tw | 2 | **4.3** | 5/5/3.5/5/3 |
| 16 | `us-021` | 峽谷地國家公園 梅薩拱門 | us | 1 | **4.3** | 5/5/3.5/5/3 |
| 17 | `us-029` | 白沙國家公園 | us | 1 | **4.3** | 5/5/3.5/5/3 |
| 18 | `us-060` | 冰河灣國家公園 | us | 2 | **4.3** | 5/5/3.5/5/3 |
| 19 | `us-087` | 颶風嶺 | us | 1 | **4.3** | 5/5/3.5/5/3 |
| 20 | `us-088` | 霍雨林 | us | 1 | **4.3** | 5/5/3.5/5/3 |

### Bottom 20

| 排名 | place | 名稱 | 區域 | 題材數 | 加權總分 | 五維 | 最近景點 (km) |
|---|---|---|---|---|---|---|---|
| 381 | `us-116` | 威皮歐山谷晨光 | us | 1 | **None** | 4/5/5.0/5/unknown | us-115 (42.04) |
| 382 | `us-117` | 馬卡普燈塔日出 | us | 1 | **None** | 5/5/4.0/5/unknown | us-118 (57.44) |
| 383 | `us-118` | 邦載管道夕照 | us | 1 | **None** | 5/5/5.0/5/unknown | us-117 (57.44) |
| 384 | `us-121` | 比克斯比溪橋（大瑟爾） | us | 1 | **None** | 5/5/2.5/5/unknown | us-122 (32.43) |
| 385 | `us-124` | 瓦爾迪茲基石峽谷瀑布 | us | 1 | **None** | 5/5/3.0/5/unknown | us-110 (29.04) |
| 386 | `us-132` | 太浩湖盆景岩 | us | 1 | **None** | 5/5/3.0/5/unknown | us-008 (153.1) |
| 387 | `us-134` | 使徒群島海蝕洞（冰洞） | us | 1 | **None** | 4/5/2.5/5/unknown | us-105 (340.6) |
| 388 | `us-135` | 卡多湖（西班牙苔蘚） | us | 1 | **None** | 5/5/3.0/5/unknown | us-035 (298.72) |
| 389 | `us-138` | 斯帕克斯小巷（凱德斯谷） | us | 1 | **None** | 5/5/2.5/5/unknown | us-038 (35.64) |
| 390 | `us-141` | 特柳賴德（Last Dollar Road） | us | 1 | **None** | 4/5/2.5/5/unknown | us-140 (20.55) |
| 391 | `us-144` | 阿比奎瀑布 | us | 1 | **None** | 5/5/3.0/5/unknown | us-143 (50.48) |
| 392 | `us-145` | 普羅克斯瀑布 | us | 1 | **None** | 5/5/3.0/5/unknown | us-144 (90.3) |
| 393 | `us-146` | 彩繪山（約翰戴化石床） | us | 1 | **None** | 5/5/3.0/5/unknown | us-143 (144.71) |
| 394 | `us-147` | 斑馬狹縫峽谷 | us | 1 | **None** | 5/5/3.0/5/unknown | us-006 (65.43) |
| 395 | `us-151` | 拉森火山（彩繪沙丘） | us | 1 | **None** | 4/5/2.5/5/unknown | us-132 (192.76) |
| 396 | `us-152` | 愛達荷暗夜保護區（愛麗絲湖） | us | 1 | **None** | 5/5/3.0/5/unknown | us-027 (22.27) |
| 397 | `us-153` | 月球火山紀念地 | us | 1 | **None** | 4/5/2.5/5/unknown | us-154 (105.11) |
| 398 | `us-156` | 哈特拉斯角燈塔 | us | 1 | **None** | 5/5/2.5/5/unknown | us-157 (312.06) |
| 399 | `us-157` | 阿薩蒂格島野馬 | us | 1 | **None** | 5/5/2.5/5/unknown | us-099 (278.4) |
| 400 | `us-158` | 哈丁冰原（奇奈峽灣） | us | 1 | **None** | 4/5/2.5/5/unknown | us-045 (18.59) |

## 弱點清單 A：低 weather_light（模型幫不上忙的景點 → 建議改題材）

| opportunity | place | 分數 |
|---|---|---|
| `jp-030-P01` | jp-030 | 1 |
| `jp-041-P01` | jp-041 | 1 |
| `jp-070-P01` | jp-070 | 2 |
| `jp-081-P01` | jp-081 | 2 |
| `jp-083-P01` | jp-083 | 2 |
| `jp-091-P01` | jp-091 | 2 |
| `tw-059-P01` | tw-059 | 1 |
| `tw-060-P01` | tw-060 | 1 |
| `tw-078-P01` | tw-078 | 1 |
| `tw-082-P01` | tw-082 | 2 |
| `tw-151-P01` | tw-151 | 2 |
| `us-111-P01` | us-111 | 2 |

## 弱點清單 B：低 verifiability（資料缺口 → 建議補資料）

| opportunity | place | 分數 | 缺口 |
|---|---|---|---|
| `jp-030-P99` | jp-030 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `tw-059-P01` | tw-059 | 1.0 | geometry_not_verified, targets_missing_evidence_refs, conditions_missing_claim_or_threshold_source, access_note_placeholder |
| `tw-060-P01` | tw-060 | 1.0 | geometry_not_verified, targets_missing_evidence_refs, conditions_missing_claim_or_threshold_source, access_note_placeholder |
| `tw-078-P01` | tw-078 | 1.0 | geometry_not_verified, targets_missing_evidence_refs, conditions_missing_claim_or_threshold_source, access_note_placeholder |
| `us-075-P01` | us-075 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-075-P02` | us-075 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-076-P01` | us-076 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-076-P02` | us-076 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-077-P01` | us-077 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |
| `us-077-P02` | us-077 | 1.5 | geometry_not_verified, targets_missing_evidence_refs, access_note_placeholder |

## 弱點清單 C：高重叠區（5km 群聚 → 檢討差異化/候選裁撤，僅建議）

- 東京鐵塔（jp-011，最近 2.37 km）、皇居外苑二重橋（jp-015，最近 2.37 km）
- 橫濱山下公園（jp-016，最近 0.36 km）、橫濱港未來21（jp-020，最近 0.36 km）
- 新穗高・西穗高口展望台（jp-021，最近 3.76 km）、上高地大正池／河童橋（jp-067，最近 3.76 km）
- 福岡城跡（jp-032，最近 3.09 km）、福岡塔（jp-035，最近 3.09 km）
- 長崎哥拉巴園（jp-034，最近 2.8 km）、稻佐山夜景（jp-057，最近 2.8 km）
- 蔵王樹氷（蔵王ロープウェイ・山形側）（jp-038，最近 2.6 km）、蔵王御釜（五色湖）（jp-049，最近 2.6 km）
- 阿蘇山・草千里ヶ浜（jp-059，最近 3.56 km）、大觀峰（阿蘇五嶽）（jp-076，最近 3.56 km）
- 別府海地獄（jp-092，最近 1.5 km）、別府血池地獄（jp-093，最近 1.5 km）
- 淡水漁人碼頭（tw-003，最近 4.84 km）、關渡大橋（tw-006，最近 3.36 km）、觀音山硬漢嶺（tw-008，最近 1.42 km）、八里崁頭里・淡江大橋觀景點（tw-086，最近 1.42 km）
- 不厭亭（tw-004，最近 2.98 km）、南雅奇岩（tw-072，最近 0.57 km）、南子吝步道（tw-085，最近 0.57 km）、報時山觀景台（tw-137，最近 2.9 km）
- 碧潭（tw-007，最近 2.61 km）、東華聖宮（tw-145，最近 2.61 km）
- 望幽谷（tw-009，最近 2.96 km）、和平島（tw-010，最近 0.63 km）、正濱漁港（tw-054，最近 0.63 km）
- 鵝鑾鼻燈塔（tw-029，最近 3.02 km）、龍磐公園／草原海岸（tw-076，最近 3.02 km）
- 抹茶山（tw-031，最近 1.61 km）、五峰旗瀑布（tw-055，最近 1.61 km）、渭水之丘／櫻花陵園（tw-098，最近 3.28 km）
- 雪山主峰（tw-041，最近 3.61 km）、雪山北峰（tw-042，最近 3.08 km）、大霸尖山（tw-046，最近 3.45 km）、池有山（tw-048，最近 1.71 km）、桃山（tw-049，最近 1.71 km）、品田山（tw-050，最近 2.19 km）
- 大古山（tw-051，最近 3.29 km）、林口水牛坑（林口大峽谷）（tw-101，最近 3.29 km）
- 杉林溪（tw-053，最近 2.16 km）、忘憂森林（tw-104，最近 2.16 km）、大崙山觀光茶園/銀杏森林（tw-125，最近 4.4 km）
- 金門得月樓（tw-062，最近 2.32 km）、金門慈湖（tw-064，最近 4.74 km）、建功嶼／退潮石板道（tw-078，最近 2.32 km）
- 馬祖南竿（tw-065，最近 2.69 km）、南竿鐵堡／海防礁岩（tw-081，最近 0.78 km）、南竿北海坑道（夜間搖櫓藍眼淚）（tw-122，最近 0.27 km）、南竿大漢據點藍眼淚（鐵板海岸）（tw-124，最近 0.27 km）
- 北竿芹壁（tw-067，最近 2.12 km）、北竿塘后道沙灘藍眼淚（tw-121，最近 2.12 km）
- tw-068（tw-068，最近 0.47 km）、帆船鼻大草原／海岬（tw-080，最近 0.47 km）
- 老梅綠石槽（tw-073，最近 1.02 km）、富貴角風稜石（tw-143，最近 1.02 km）
- 翠峰湖環山步道觀景點（tw-088，最近 1.94 km）、太平山森林遊樂區（tw-140，最近 1.94 km）
- 東莒燈塔（東犬燈塔）（tw-094，最近 0.36 km）、東莒福正沙灘藍眼淚（東犬燈塔旁）（tw-123，最近 0.36 km）
- 萬年峽谷（tw-106，最近 4.9 km）、1314觀景台（tw-134，最近 4.9 km）
- 四草綠色隧道（tw-110，最近 3.8 km）、安平漁人碼頭/大魚的祝福（tw-142，最近 3.8 km）
- 加里山（tw-119，最近 4.1 km）、仙山靈洞宮後山（tw-127，最近 4.1 km）
- 姜子寮山觀景台（tw-129，最近 4.81 km）、五分山雷達站（tw-135，最近 4.81 km）
- 雷尼爾山國家公園（us-012，最近 0.08 km）、雷尼爾山・天堂區（us-081，最近 2.02 km）、雷尼爾山・倒影湖（us-082，最近 0.08 km）
- 奧林匹克國家公園（us-019，最近 0.05 km）、紅寶石海灘（us-085，最近 0.05 km）
- 西雅圖太空針塔（us-024，最近 0.88 km）、西雅圖派克市場（us-026，最近 1.33 km）、Kerry Park（us-071，最近 1.1 km）、金色花園公園（us-072，最近 4.06 km）、阿爾基海灘公園（us-073，最近 2.04 km）、煤氣廠公園（us-074，最近 2.6 km）、us-075（us-075，最近 4.06 km）、us-076（us-076，最近 2.04 km）、us-077（us-077，最近 2.61 km）、默特爾・愛德華茲公園（us-078，最近 0.88 km）
- 卡特邁國家公園（us-059，最近 0.04 km）、布魯克斯瀑布・鮭魚道水景（us-111，最近 0.04 km）
- 藝術家角（us-092，最近 2.65 km）、畫湖（us-093，最近 2.65 km）
- 哈雷茂茂火山口夜空（us-112，最近 0.38 km）、基勞亞口熔岩紅光夜拍（基勞亞展望台）（us-161，最近 0.38 km）、那胡庫熔岩管（瑟斯頓熔岩洞）（us-162，最近 0.41 km）、基勞亞伊奇火山口熔岩地表（us-163，最近 0.41 km）
- 老忠實間歇泉（黃石）（us-159，最近 2.03 km）、牽牛花溫泉池（黃石上間歇泉盆地）（us-160，最近 2.03 km）

> Rubric v2（CL-DATA-25R 重跑）：safe_access 權重移除、scenic_beauty 權重 20，由庫內證據機械判定；scenic_beauty 無證據的景點誠實標 unknown，其加權總分留空（不虛構）。季節窗/封閉期資訊仍保留於 dossier 與契約。
> 本報告為唯讀分析：不改任何 catalog/契約資料；弱點處置（改題材/補資料/裁撤）為建議，決策權在 PM/owner。機器可讀版本：catalog-scoring.json。
