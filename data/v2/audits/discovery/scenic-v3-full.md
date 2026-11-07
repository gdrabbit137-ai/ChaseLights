# CL-DATA-30 景色優美評分 v3 全庫報告（218 景點）

Owner 裁決「直接跑全庫」。方法沿用 CL-DATA-27/28/29：
- 多源抓照（Wikimedia Commons 搜尋＋Wikipedia 語言連結＋Openverse，每點目標 3–6 張）
- 代表性篩選（標題黑名單前置＋視覺複核 INVALID 標註，n≥2 取中位數、n=1 取均值）
- 視覺評分四子項 1–10：地貌獨特性／構圖層次／光影天氣戲劇性／色彩，÷2 換算 0–5
- 社群信號（修正版）：標章僅採計通過代表性篩選照片（+0.5）；檔案頁 12 個月瀏覽 ≥5000（+0.25）；負向 −0.25 僅在逐景點完成完整標章盤點（Quality/Featured/Popular/PotD 類別正式交集）且瀏覽 payload 完整時才可扣；缺 payload 一律 unknown 不計 0
- 認證階梯 ±1（5=UNESCO/國際、4=國家級官方、3=多攻略共識、2=一般）
- 合成分 = 視覺0–5 ＋ clamp(認證−視覺, ±1) ＋ 社群，clip 0–5；無有效照片 → 誠實 unknown

統計：211/218 已評分，均分 3.48，中位數 3.88，unknown 7。

## Top 10

| 名次 | id | 景點 | v3 | v2 | 視覺 | 認證 | 社群 |
|---|---|---|---|---|---|---|---|
| 1 | us-055 | 威朗格利-聖埃利亞斯國家公園 | **5** | 4.0 | 4.0 | 5 | 0 |
| 2 | us-010 | 黃石國家公園 大稜鏡溫泉 | **5** | 3.65 | 4.12 | 5 | 0 |
| 3 | jp-023 | 京都清水寺 | **5** | — | 4.06 | 5 | 0 |
| 4 | us-003 | 羚羊峽谷 | **5** | — | 4.5 | 5 | 0 |
| 5 | us-008 | 優勝美地半圓頂 | **5** | — | 4.12 | 5 | 0 |
| 6 | us-009 | 優勝美地隧道觀景臺 | **5** | — | 4.5 | 5 | 0 |
| 7 | jp-044 | 十二湖・青池 | **4.62** | 4.6 | 3.62 | 5 | 0 |
| 8 | us-019 | 奧林匹克國家公園 | **4.62** | 3.35 | 3.62 | 5 | 0 |
| 9 | us-060 | 冰河灣國家公園 | **4.56** | 3.9 | 3.56 | 5 | 0 |
| 10 | jp-048 | 北山崎（三陸断崖） | **4.0** | 4.38 | 3.88 | 4 | 0 |

## Bottom 10

| 名次 | id | 景點 | v3 | v2 | 視覺 | 認證 | 社群 |
|---|---|---|---|---|---|---|---|
| 1 | tw-084 | 大農大富平地森林園區 | **2.0** | 4.23 | 2.38 | 2 | 0 |
| 2 | jp-016 | 橫濱山下公園 | **2.0** | — | 2.62 | 2 | 0 |
| 3 | jp-035 | 福岡塔 | **2.0** | — | 2.38 | 2 | 0 |
| 4 | tw-006 | 關渡大橋 | **2.0** | — | 2.69 | 2 | 0 |
| 5 | tw-011 | 永安漁港 | **2.0** | — | 2.69 | 2 | 0 |
| 6 | tw-028 | 駁二藝術特區 | **2.0** | — | 2.38 | 2 | 0 |
| 7 | tw-052 | 小崗山雲臺 | **2.0** | — | 3.0 | 2 | 0 |
| 8 | tw-093 | 福壽山農場觀景點 | **2.0** | — | 2.38 | 2 | 0 |
| 9 | us-016 | 拉斯維加斯大道 | **2.0** | — | 2.94 | 2 | 0 |
| 10 | us-024 | 西雅圖太空針塔 | **2.0** | — | 2.62 | 2 | 0 |

## Unknown（7 點，誠實標註）

| id | 景點 | 抓到照片 | 有效照片 | 認證 |
|---|---|---|---|---|
| tw-023 | 頂石棹 | 8 | 0 | 4 |
| tw-071 | 小琉球花瓶岩 | 12 | 0 | 4 |
| tw-080 | 帆船鼻大草原／海岬 | 7 | 0 | 4 |
| tw-085 | 南子吝步道 | 6 | 0 | 3 |
| us-063 | 塔爾基特納 | 7 | 0 | 3 |
| us-088 | 霍雨林 | 8 | 0 | 4 |
| tw-091 | 司馬庫斯部落觀景點 | 12 | 0 | 3 |

## 逐景點明細

### jp-044 十二湖・青池 — v3 **4.62**（v2: 4.6，視覺 3.62，認證 5，社群 +0）
- 認證依據：白神山地世界遺產緩衝地域（林野廳保護概要）
- 合成：視覺3.62＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 3 張，有效 2 張
- A：子項 [8, 6, 6, 9] 均分 None — File:十二湖の青池.jpg（None）
- B：子項 [8, 6, 6, 9] 均分 None — File:十二湖の青池２.jpg（None）
- C：INVALID（非風景代表照）— File:十二湖 青池 THETA SC 20180527 R0012691.JPG

### jp-048 北山崎（三陸断崖） — v3 **4.0**（v2: 4.38，視覺 3.88，認證 4，社群 +0）
- 認證依據：三陸復興國立公園（北山崎屬園區）
- 合成：視覺3.88＋認證校正0.12＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 3 張，有效 3 張
- A：子項 [8, 8, 7, 8] 均分 None — File:北山崎第一展望台からの北山崎.jpg（None）
- B：子項 [8, 8, 7, 8] 均分 None — File:北山崎 - panoramio.jpg（None）
- C：子項 [7, 6, 7, 6] 均分 None — File:北山崎～朝焼け - panoramio.jpg（None）

### tw-026 井仔腳瓦盤鹽田 — v3 **4.0**（v2: 4.33，視覺 3.0，認證 4，社群 +0）
- 認證依據：雲嘉南濱海國家風景區＋台南市定文化景觀（井仔腳鹽田）
- 合成：視覺3.0＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 3 張，有效 3 張
- A：子項 [8, 7, 4, 5] 均分 None — File:井仔腳瓦盤鹽田.JPG（None）
- B：子項 [8, 7, 4, 5] 均分 None — File:井仔腳瓦盤鹽田 Jingzaijiao Tile-paved Salt Fields - panoramio.jpg（None）
- C：子項 [8, 8, 4, 6] 均分 None — File:Jingzaijiao Tile-paved Salt Fields 井仔腳瓦盤鹽田 - panoramio.jpg（None）

### tw-084 大農大富平地森林園區 — v3 **2.0**（v2: 4.23，視覺 2.38，認證 2，社群 +0）
- 認證依據：林業署平地森林園區（官方但非景觀級認證）
- 合成：視覺2.38＋認證校正-0.38＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 3 張，有效 1 張
- A：INVALID（非風景代表照）— File:台灣農業部林業及自然保育署大農大富平地森林園區服務台 20250510.jpg
- B：INVALID（非風景代表照）— File:Exterior view of the entrance to Danong Dafu Plains Forest Park.jpg
- C：子項 [4, 5, 5, 5] 均分 None — File:Road through Danongdafu Forest Park.jpg（None）

### jp-046 タウシュベツ川橋梁（幻の橋） — v3 **4.0**（v2: 4.2，視覺 4.0，認證 4，社群 +0）
- 認證依據：北海道遺產（舊國鐵士幌線混凝土拱橋群）官方選定
- 合成：視覺4.0＋認證校正0.0＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 3 張，有效 3 張
- A：子項 [9, 9, 8, 8] 均分 None — File:Taushubetsu-Bridge.jpg（None）
- B：子項 [9, 9, 7, 7] 均分 None — File:Taushubetsu-River-Bridge.jpg（None）
- C：子項 [9, 7, 6, 7] 均分 None — File:タウシュベツ川橋梁 - panoramio.jpg（None）

### jp-045 地球岬展望台 — v3 **3.75**（v2: 4.17，視覺 2.75，認證 4，社群 +0）
- 認證依據：室蘭八景＋日本の灯台50選（官方選定）
- 合成：視覺2.75＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 3 張，有效 2 張
- A：子項 [5, 5, 5, 6] 均分 None — File:CAPE CHIKYU LIGHTHOUSE.JPG（None）
- B：子項 [6, 6, 5, 6] 均分 None — File:CAPE CHIKYU.JPG（None）
- C：INVALID（非風景代表照）— File:ChikyuMisakiDanchi DonanBus 20090505.jpg

### us-011 大提頓國家公園 — v3 **4.0**（v2: 4.17，視覺 3.94，認證 4，社群 +0）
- 認證依據：美國國家公園署（Grand Teton NP）官方
- 合成：視覺3.94＋認證校正0.06＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 3 張，有效 2 張
- A：子項 [9, 9, 7, 8] 均分 None — File:Oxbow Bend outlook in the Grand Teton National Park.jpg（None）
- B：子項 [9, 8, 6, 7] 均分 None — File:Willow Flats area and Teton Range in Grand Teton National Park.jpg（None）
- C：INVALID（非風景代表照）— File:Moose in Grand Teton National Park 3 (8007698498).jpg

### us-001 大峽谷國家公園 — v3 **4.0**（v2: 4.13，視覺 4.25，認證 4，社群 +0）
- 認證依據：美國國家公園署（Grand Canyon NP）官方
- 合成：視覺4.25＋認證校正-0.25＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 3 張，有效 3 張
- A：子項 [10, 8, 7, 8] 均分 None — File:Grand canyon march 2013.jpg（None）
- B：子項 [10, 8, 9, 8] 均分 None — File:Grand Canyon Powell Point Evening Light 02 2013.jpg（None）
- C：子項 [10, 8, 8, 8] 均分 None — File:Grand Canyon Hopi Point with rainbow 2013.jpg（None）

### jp-037 雲海テラス（トマム） — v3 **3.0**（v2: 4.1，視覺 3.88，認證 3，社群 +0）
- 認證依據：TOMAMU雲海テラス——多方攝影攻略一致推薦，無官方認證
- 合成：視覺3.88＋認證校正-0.88＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 2 張，有效 1 張
- A：INVALID（非風景代表照）— File:雲海テラス TOMAMU - panoramio (1).jpg
- B：子項 [7, 7, 9, 8] 均分 None — File:UNKAI TERRACE.jpg（None）

### us-031 落磯山國家公園 — v3 **4.0**（v2: 4.0，視覺 3.25，認證 4，社群 +0）
- 認證依據：美國國家公園署（Rocky Mountain NP）官方
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：openverse, wiki-zh；抓到 6 張，有效 4 張
- A：子項 [7, 7, 6, 8] 均分 7.0 — File:OuzelLake Colorado.jpg（wiki-zh）〈高山湖畔秋色〉
- B：子項 [5, 6, 6, 7] 均分 6.0 — Rocky Mountain National Park（openverse）〈苔石溪流森林〉
- C：INVALID（地點不符（馬蹄灣））— File:Glen Canyon Dam MC.jpg
- D：子項 [6, 6, 5, 6] 均分 5.75 — Roaring River, Rocky Mountain National Park（openverse）〈瀑布巨石〉
- E：INVALID（地點不符（平原河畔棕櫚））— File:Colorado River Avi.JPG
- F：子項 [7, 6, 8, 7] 均分 7.0 — Rocky Mountain National Park - moonscape（openverse）〈月昇山岳燒霞〉

### us-055 威朗格利-聖埃利亞斯國家公園 — v3 **5**（v2: 4.0，視覺 4.0，認證 5，社群 +0）
- 認證依據：威朗格利—聖埃利亞斯＝UNESCO 世界遺產（Kluane/Wrangell/St Elias/Glacier Bay）
- 合成：視覺4.0＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：openverse；抓到 4 張，有效 1 張
- A：INVALID（縮圖下載失敗）— University Range, Wrangell-St Elias NP, Alaska
- B：子項 [9, 8, 7, 8] 均分 8.0 — Copper River below Wrangell-St. Elias NP（openverse）〈辮狀冰川河鳥瞰〉
- C：INVALID（繪畫非照片）— Dead Dog Hill in Wrangell-St. Elias NP
- D：INVALID（人文展示物）— Fish trap at Wrangell-St Elias NP visitor center in AK 7-19-24

### us-069 克拉克湖國家公園 — v3 **4.0**（v2: 4.0，視覺 3.12，認證 4，社群 +0）
- 認證依據：美國國家公園署（Lake Clark NP）官方
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search, openverse；抓到 6 張，有效 4 張
- A：子項 [8, 7, 9, 8] 均分 8.0 — File:Lake Clark National Park and Preserve LACL8452.jpg（commons-search）〈金色河谷日出〉
- B：INVALID（野生動物主體）— Lake Clark National Park and Preserve
- C：INVALID（野生動物主體）— File:By ovedc - Lake Clark National Park - 09.jpg
- D：子項 [4, 4, 4, 5] 均分 4.25 — Old Village Fire, Lake Clark National Park, 2015（openverse）〈灰霧海面平淡〉
- E：子項 [7, 6, 5, 6] 均分 6.0 — File:Lake Clark National Park, USA.jpg（commons-search）〈山脊紋理鳥瞰〉
- F：子項 [7, 6, 6, 7] 均分 6.5 — Lake Clark National Park（openverse）〈雪山下溪谷森林〉

### tw-036 七星潭 — v3 **3.0**（v2: 3.99，視覺 3.19，認證 3，社群 +0）
- 認證依據：七星潭——攝影攻略一致推薦（月牙灣），無官方景觀認證
- 合成：視覺3.19＋認證校正-0.19＋社群0；社群：無社群信號資料
- 照片來源：openverse；抓到 6 張，有效 2 張
- A：子項 [6, 5, 7, 6] 均分 6.0 — 晴天彩虹@七星潭(Solar Halo @ Qixingtan, Taiwan)（openverse）〈日暈天象〉
- B：INVALID（動物主體）— Full resolution version of that picture of Juno at Qixingtan.
- C：INVALID（海堤石刻招牌）— Qixingtan (七星潭)
- D：INVALID（縮圖下載失敗）— 七星潭海岸风景特定区 - Qixingtan Coast Scenic Area - panoramio
- E：子項 [6, 7, 7, 7] 均分 6.75 — 2017-6-28 花蓮新城七星潭 (Hualien Xincheng Qixingtan Scenic Area)（openverse）〈礫灘疊石晚霞〉
- F：INVALID（縮圖下載失敗）— Qixingtan Beach, Taiwan

### us-005 拱門國家公園 — v3 **4.0**（v2: 3.98，視覺 3.62，認證 4，社群 +0）
- 認證依據：美國國家公園署（Arches NP）官方
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：openverse；抓到 5 張，有效 5 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — Arches National Park（openverse）〈平衡岩紅岩〉
- B：子項 [9, 8, 7, 9] 均分 8.25 — Delicate Arch, Arches National Park（openverse）〈精緻拱門經典〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — Garden of Eden, Arches National Park [Explore 12/06/13]（openverse）〈公園大道紅岩〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — Arches National Park - Utah - United States - South West（openverse）〈南北窗拱門〉
- E：子項 [7, 7, 8, 6] 均分 7.0 — Night Sky and Clouds, Arches National Park（openverse）〈星空帳篷剪影〉

### jp-039 津別峠展望台（屈斜路湖雲海） — v3 **4.0**（v2: 3.95，視覺 3.0，認證 4，社群 +0）
- 認證依據：阿寒摩周國立公園域內（津別峠屈斜路湖雲海）
- 合成：視覺3.0＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 4 張，有效 3 張
- A：INVALID（展望台建築非風景）— File:Tsubetsu Tōge01.JPG
- B：子項 [6, 6, 6, 6] 均分 6.0 — File:Lake Kussharo01.JPG（commons-search）〈雲海漫湖〉
- C：子項 [7, 7, 7, 7] 均分 7.0 — File:Lake Kussharo from Tsubetsu pass deck 2009.jpg（commons-search）〈屈斜路湖全景〉
- D：子項 [6, 6, 6, 6] 均分 6.0 — File:屈斜路湖～津別峠 - Lake Kussharo-ko from Tsubetsu-toge - panoramio.jpg（commons-search）〈枝間框景〉

### tw-087 大雪山森林遊樂區43K觀景台 — v3 **2.62**（v2: 3.95，視覺 1.62，認證 4，社群 +0）
- 認證依據：雪霸國家公園域內大雪山國家森林遊樂區（林業署官方園區）
- 合成：視覺1.62＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：pilot-cl27；抓到 3 張，有效 2 張
- A：子項 [3, 3, 3, 4] 均分 None — File:Entrance stations in Dasyueshan National Forest Recreation Area 20241012.jpg（None）
- B：子項 [3, 3, 3, 4] 均分 None — File:Looking back at the entrance to Dasyueshan National Forest Recreation Area.jpg（None）
- C：INVALID（非風景代表照）— File:20190408大雪山遊樂區界碑.jpg

### us-059 卡特邁國家公園 — v3 **4.0**（v2: 3.95，視覺 3.25，認證 4，社群 +0）
- 認證依據：美國國家公園署（Katmai NP）官方
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search, openverse；抓到 6 張，有效 4 張
- A：子項 [6, 6, 7, 6] 均分 6.25 — File:Katmai National Park and Preserve KATM4108.jpg（commons-search）〈陰鬱火山湖〉
- B：INVALID（地圖）— Katmai National Park and Preserve
- C：子項 [7, 6, 7, 7] 均分 6.75 — File:Packrafting Soluka Creek. Katmai National Park, Alaska - panoramio.jpg（commons-search）〈萬煙谷漂流〉
- D：INVALID（地圖）— The Genesis of Katmai National Park and Preserve
- E：子項 [7, 6, 7, 7] 均分 6.75 — File:Katmai National Park, Alaska - panoramio.jpg（commons-search）〈山脊眺望〉
- F：子項 [6, 5, 6, 6] 均分 5.75 — Crossing one of the Knife Creeks. Valley of Ten Thousand Smokes, Katmai National Park, Alaska（openverse）〈火山灰谷健行〉

### tw-044 南湖大山 — v3 **4.0**（v2: 3.9，視覺 3.19，認證 4，社群 +0）
- 認證依據：太魯閣國家公園域內（南湖大山）
- 合成：視覺3.19＋認證校正0.81＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：openverse, wiki-en；抓到 6 張，有效 2 張
- A：子項 [7, 7, 6, 7] 均分 6.75 — File:NanhuMountain 02.jpg（wiki-en）〈南湖岩峰雲林〉
- B：INVALID（縮圖下載失敗）— Nanhu Mountain(Yi sun)02
- C：INVALID（地點不符（喜馬拉雅雪峰））— File:Everest, Nuptse, Khumbu Glacier, Nepal, Himalayas.jpg
- D：INVALID（縮圖下載失敗）— Nanhu Mountain ＆Scabiosa lacerifolia Hayata(Yi Sun)01
- E：子項 [6, 5, 7, 6] 均分 6.0 — sunrise @ Nanhu Mountain, Taiwan（openverse）〈日出燒雲〉
- F：INVALID（縮圖下載失敗）— Struggle to survive (Gentiana sp. at Nanhu Mountain area) Gen-Chang HSU 016

### us-021 峽谷地國家公園 梅薩拱門 — v3 **4.0**（v2: 3.9，視覺 3.62，認證 4，社群 +0）
- 認證依據：美國國家公園署（Canyonlands NP 梅薩拱門）官方
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：openverse；抓到 4 張，有效 3 張
- A：子項 [9, 8, 9, 9] 均分 8.75 — Canyonlands - Mesa Arch Sunrise Flare by Michael Matti（openverse）〈梅薩拱門日出經典〉
- B：INVALID（縮圖下載失敗）— Canyonlands - Mesa Arch
- C：子項 [8, 7, 6, 8] 均分 7.25 — canyonlands mesa arch（openverse）〈拱門白晝視野〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — Canyonlands, Mesa Arch（openverse）〈拱門藍天〉

### us-029 白沙國家公園 — v3 **4.0**（v2: 3.9，視覺 3.19，認證 4，社群 +0）
- 認證依據：美國國家公園署（White Sands NP，2024 升格國家公園）官方
- 合成：視覺3.19＋認證校正0.81＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search, openverse；抓到 6 張，有效 6 張
- A：子項 [7, 7, 5, 7] 均分 6.5 — File:Aerial view of dunefield, White Sands National Park, New Mexico, United States.png（commons-search）〈白沙遠山〉
- B：子項 [8, 7, 9, 8] 均分 8.0 — White Sands National Park（openverse）〈沙丘雷雨〉
- C：子項 [6, 6, 6, 6] 均分 6.0 — File:White Sands National Park - 51875868804.jpg（commons-search）〈沙丘草原〉
- D：子項 [6, 6, 6, 7] 均分 6.25 — 2022-10-25 White Sands National Park 9（openverse）〈獨行沙丘〉
- E：子項 [5, 5, 3, 6] 均分 4.75 — File:White Sands National Park - 53196074884.jpg（commons-search）〈沙紋特寫〉
- F：子項 [7, 6, 8, 7] 均分 7.0 — Sunset at White Sands National Park, New Mexico（openverse）〈夕照沙谷〉

### us-060 冰河灣國家公園 — v3 **4.56**（v2: 3.9，視覺 3.56，認證 5，社群 +0）
- 認證依據：冰河灣＝UNESCO 世界遺產（Kluane/Wrangell/St Elias/Glacier Bay）
- 合成：視覺3.56＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search, openverse, wiki-en；抓到 6 張，有效 6 張
- A：子項 [8, 7, 6, 7] 均分 7.0 — File:Johns Hopkins Glacier Bay Mount Orville Mount Wilbur Alaska 2014.jpg（commons-search）〈冰河灣山勢〉
- B：子項 [9, 8, 7, 8] 均分 8.0 — File:A042, Glacier Bay National Park, Alaska, USA, Margerie Glacier, 2002.jpg（wiki-en）〈潮冰河正面〉
- C：子項 [8, 7, 6, 7] 均分 7.0 — Marjorie Glacier, Glacier Bay National Park & Preserve（openverse）〈冰谷鳥瞰〉
- D：子項 [8, 7, 7, 7] 均分 7.25 — File:Glacier Bay National Park Inner Passage-0219.jpg（commons-search）〈霧峽灣綠水〉
- E：子項 [7, 6, 5, 6] 均分 6.0 — File:A043, Glacier Bay National Park, Alaska, USA, Brady Icefield, 2002.jpg（wiki-en）〈雪峰紋理〉
- F：子項 [8, 7, 7, 7] 均分 7.25 — Glacier Bay National Park: La Perouse Glacier（openverse）〈冰河瀑布〉

### jp-042 森吉山樹氷平（阿仁スキー場） — v3 **3.0**（v2: 4.05，視覺 3.5，認證 3，社群 +0）
- 認證依據：森吉山樹氷平——攝影攻略一致推薦（秋田三大樹氷），無官方景觀認證
- 合成：視覺3.5＋認證校正-0.5＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [7, 6, 6, 7] 均分 6.5 — File:Snow monsters in Mount Moriyoshi 20250215b.jpg（commons-search）〈樹氷平原〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — File:Snow monsters in Mount Moriyoshi 20250215c.jpg（commons-search）〈雪原樹氷列〉
- C：子項 [8, 7, 6, 7] 均分 7.0 — File:Snow monsters in Mount Moriyoshi 20250215a.jpg（commons-search）〈樹氷特寫〉
- D：子項 [8, 7, 6, 7] 均分 7.0 — File:Snow monsters in Mount Moriyoshi 20250215d.jpg（commons-search）〈藍天樹氷〉
- E：子項 [8, 7, 6, 7] 均分 7.0 — File:Snow monsters in Mount Moriyoshi 20250215e.jpg（commons-search）〈樹氷群〉
- F：子項 [8, 7, 6, 7] 均分 7.0 — File:Snow monsters in Mount Moriyoshi 20250215f.jpg（commons-search）〈夕照樹氷〉

### jp-047 八甲田山樹氷（八甲田ロープウェー） — v3 **3.38**（v2: 4.05，視覺 2.38，認證 4，社群 +0）
- 認證依據：十和田八幡平國立公園域內（八甲田樹氷＝日本三大樹氷）
- 合成：視覺2.38＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：子項 [5, 4, 4, 6] 均分 4.75 — File:Hakkoda Ropeway near the summit station.jpg（commons-search）〈遊客為前景，樹氷在後〉
- B：INVALID（非風景代表照）— File:Juhyo of Hakkoda 02.jpg
- C：INVALID（非風景代表照）— File:Hakkoda snow monsters (51885476927).jpg
- D：INVALID（非風景代表照）— File:Hakkoda snow monsters (51885477032).jpg
- E：INVALID（非風景代表照）— File:Hakkoda snow monsters (51886442471).jpg
- F：INVALID（非風景代表照）— File:Hakkoda snow monsters (51886768259).jpg

### tw-088 翠峰湖環山步道觀景點 — v3 **3.62**（v2: 4.0，視覺 2.62，認證 4，社群 +0）
- 認證依據：太平山國家森林遊樂區（翠峰湖環山步道）
- 合成：視覺2.62＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [5, 5, 5, 6] 均分 5.25 — File:2019 Cueifong Lake Circle Trail b.jpg（commons-search）〈苔林古木〉
- B：子項 [4, 4, 3, 5] 均分 4.0 — File:2019 Cueifong Lake Circle Trail c.jpg（commons-search）〈林下暗部〉
- C：子項 [5, 5, 4, 6] 均分 5.0 — File:2019 Cueifong Lake Circle Trail f.jpg（commons-search）〈苔木棧道〉
- D：子項 [5, 5, 5, 6] 均分 5.25 — File:2019 Cueifong Lake Circle Trail e.jpg（commons-search）〈苔根森林〉
- E：子項 [5, 5, 5, 6] 均分 5.25 — File:2019 Cueifong Lake Circle Trail Qingfeng Explanation Station b.jpg（commons-search）〈落葉鐵軌〉
- F：INVALID（里程標柱）— File:2019 Cueifong Lake Circle Trail i.jpg

### us-014 死亡谷國家公園 — v3 **4.0**（v2: 3.88，視覺 3.12，認證 4，社群 +0）
- 認證依據：美國國家公園署（Death Valley NP）官方
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [7, 6, 7, 8] 均分 7.0 — File:USA 10789 Death Valley Luca Galuzzi 2007.jpg（commons-search）〈彩繪惡地〉
- B：子項 [6, 6, 6, 6] 均分 6.0 — File:Death Valley Mesquite Flats Sand Dunes 2013.jpg（commons-search）〈土黃沙丘〉
- C：子項 [7, 7, 6, 7] 均分 6.75 — File:Death Valley exit SR190 view Panamint Butt flash flood 2013.jpg（commons-search）〈鹽原鏡面〉
- D：子項 [7, 6, 6, 7] 均分 6.5 — File:Death Valley view from Zabriskie Point with people 2013.jpg（commons-search）〈金色峽谷〉
- E：子項 [4, 4, 3, 5] 均分 4.0 — File:SR 190 Panamint Springs Resort End Death Valley 2013.jpg（commons-search）〈沙漠公路〉
- F：子項 [4, 4, 4, 5] 均分 4.25 — File:Death Valley National Park December 2013 002.jpg（commons-search）〈礫漠灌木〉

### jp-043 富田農場ラベンダーイースト — v3 **3.0**（v2: 3.85，視覺 3.5，認證 3，社群 +0）
- 認證依據：富田農場——攝影攻略一致推薦（薰衣草花海），民營農場無官方認證
- 合成：視覺3.5＋認證校正-0.5＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：INVALID（雕像非花海）— File:ファーム富田ラベンダーEAST - panoramio.jpg
- B：INVALID（農機具）— File:トラクターバス - panoramio.jpg
- C：INVALID（入口設施）— File:Farm Tomita Lavender East 20260704a.jpg
- D：子項 [7, 7, 6, 8] 均分 7.0 — File:Farm Tomita Lavender East 20260704c.jpg（commons-search）〈薰衣草田列〉
- E：子項 [7, 7, 6, 8] 均分 7.0 — File:Farm Tomita Lavender East 20260704b.jpg（commons-search）〈花海遠山〉
- F：子項 [7, 7, 6, 8] 均分 7.0 — File:Farm Tomita Lavender East 20260704e.jpg（commons-search）〈紫田層次〉

### tw-094 東莒燈塔（東犬燈塔） — v3 **3.75**（v2: 3.85，視覺 2.75，認證 4，社群 +0）
- 認證依據：東莒燈塔＝國定古蹟＋馬祖國家風景區
- 合成：視覺2.75＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Dongquan Lighthouse, Dongju, Matsu, Taiwan.JPG（commons-search）〈燈塔白舍〉
- B：子項 [5, 5, 5, 6] 均分 5.25 — File:東莒島燈塔及其景觀.jpg（commons-search）〈聚落坡地〉
- C：子項 [6, 5, 6, 6] 均分 5.75 — File:東犬燈塔及福正聚落.jpg（commons-search）〈海岬燈塔遠眺〉
- D：子項 [5, 4, 4, 5] 均分 4.5 — File:東犬燈塔及戰地遺跡.jpg（commons-search）〈舊牆石階〉
- E：子項 [5, 4, 4, 5] 均分 4.5 — File:東犬燈塔、戰地遺跡與海岸線.jpg（commons-search）〈步道燈桿〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Dongquan Lighthouse Dongju Juguang Lienchiang-2.jpg（commons-search）〈丘頂燈塔〉

### us-013 火山口湖國家公園 — v3 **3.56**（v2: 3.85，視覺 2.56，認證 4，社群 +0）
- 認證依據：美國國家公園署（Crater Lake NP）官方
- 合成：視覺2.56＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 7, 9] 均分 8.25 — File:Crater Lake winter pano2.jpg（commons-search）〈雪冬火山湖全景〉
- B：子項 [5, 5, 4, 6] 均分 5.0 — File:Trees, Crater Lake National Park, Crater Lake, OR.jpg（commons-search）〈松林浮石坡〉
- C：子項 [4, 4, 3, 5] 均分 4.0 — File:Stone Wall, Crater Lake National Park, Crater Lake, OR.jpg（commons-search）〈林間石牆〉
- D：子項 [5, 5, 5, 6] 均分 5.25 — File:Trees, Crater Lake National Park, Crater Lake, OR - 53848146397.jpg（commons-search）〈松間遠湖〉
- E：子項 [5, 5, 4, 6] 均分 5.0 — File:Trees, Crater Lake National Park, Crater Lake, OR - 53849395944.jpg（commons-search）〈雪坡森林〉
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:Crater Lake, Crater Lake National Park, Crater Lake, OR - 53848151122.jpg（commons-search）〈岩縫框湖〉

### us-007 錫安國家公園 — v3 **4.0**（v2: 3.83，視覺 3.25，認證 4，社群 +0）
- 認證依據：美國國家公園署（Zion NP）官方
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 7, 8] 均分 7.5 — File:Zion angels landing view.jpg（commons-search）〈峽谷日落紅岩〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — File:Zion Narrows.jpg（commons-search）〈溪流峽縫〉
- C：子項 [7, 6, 6, 7] 均分 6.5 — File:Mountains in Zion National Park, Utah.jpg（commons-search）〈崖徑望谷〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:Angels Landing.jpg（commons-search）〈樹框紅岩〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Kolob Canyons part of Zion National Park.JPG（commons-search）〈紅崖灌木〉
- F：子項 [4, 4, 4, 5] 均分 4.25 — File:Zion National Park, the Narrows.jpg（commons-search）〈溪石特寫〉

### tw-034 崇德 — v3 **3.0**（v2: 3.8，視覺 3.38，認證 3，社群 +0）
- 認證依據：崇德（立霧溪口/清水斷崖北端眺望）——攝影攻略一致推薦
- 合成：視覺3.38＋認證校正-0.38＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：INVALID（建築非本景點風景）— File:TRA Chongde Station 20070816.jpg
- B：INVALID（車站設施）— File:TRA Chongde Station platforms 20090119.jpg
- C：INVALID（地圖）— File:City wall of Chongde in 1879.jpg
- D：INVALID（寺廟非本景點）— File:Chongde Confucian Temple 16 2014-06.jpg
- E：子項 [7, 7, 6, 7] 均分 6.75 — File:Driftwood at Chongde Beach.jpg（commons-search）〈清水斷崖海岸〉
- F：INVALID（室內車站）— File:Taichung Metro Wenxin Chongde Station Exit 2020.jpg

### us-018 冰川國家公園 — v3 **4.0**（v2: 3.77，視覺 3.38，認證 4，社群 +0）
- 認證依據：美國國家公園署（Glacier NP）官方
- 合成：視覺3.38＋認證校正0.62＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [7, 6, 6, 7] 均分 6.5 — File:Girl Posing at Glacier Point Yosemite 2013.jpg（commons-search）〈岩峰眺望〉
- B：INVALID（野生動物主體）— File:Hoary Marmot in Glacier National Park.jpg
- C：INVALID（野生動物主體）— File:Mountain Goat at Hidden Lake.jpg
- D：子項 [8, 7, 6, 7] 均分 7.0 — File:Grinnell Glacier Overlook at Glacier National Park, MT (DSC 0597).jpg（commons-search）〈高山湖群〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Glacier National Park (Canada).jpg（commons-search）〈雪峰林海〉
- F：子項 [8, 7, 6, 7] 均分 7.0 — File:Glacier valley in Khan Tengri Nature Park, Tien Shan.jpg（commons-search）〈冰蝕尖峰〉

### tw-025 二寮觀日亭 — v3 **3.62**（v2: 3.75，視覺 2.62，認證 4，社群 +0）
- 認證依據：西拉雅國家風景區域內（二寮觀日亭）
- 合成：視覺2.62＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：子項 [5, 5, 5, 6] 均分 5.25 — File:台南左鎮區二寮觀日亭.jpg（commons-search）〈鳥瞰草山觀景區〉
- B：INVALID（碑文石碑）— File:節序日考(二).djvu
- C：INVALID（碑文石碑）— File:竹葉亭雜記(二).djvu
- D：INVALID（碑文石碑）— File:思益堂日札(二).djvu
- E：INVALID（碑文石碑）— File:棕亭古文鈔(二).djvu
- F：INVALID（碑文石碑）— File:松夢寮詩稿(二).djvu

### tw-043 奇萊主峰 — v3 **4.0**（v2: 3.75，視覺 3.38，認證 4，社群 +0）
- 認證依據：太魯閣國家公園域內（奇萊主峰）
- 合成：視覺3.38＋認證校正0.62＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [7, 7, 6, 7] 均分 6.75 — File:MountainChiLai.jpg（commons-search）〈金色箭竹草坡〉
- B：INVALID（繪畫非照片）— File:Spring Morning On Mt. Chi Lai,by Li Mei-shu Memorial Gallery.jpg
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:紅毛杜鵑遠眺奇萊北峰.jpg（commons-search）〈杜鵑繞黑峰〉
- D：子項 [7, 6, 6, 7] 均分 6.5 — File:Chilai Main Peak - Chien Tzu Hao - 01.jpg（commons-search）〈鞍部眺望〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:View south towards Qilaichi Mountain and Qilai Main Peak in the morning on 8 July 2013.jpg（commons-search）〈稜線草原〉
- F：子項 [8, 7, 6, 7] 均分 7.0 — File:Snowy Mount Qilai North Peak, Taroko National Park by David Sung.jpg（commons-search）〈積雪山巔〉

### tw-019 合歡山主峰 — v3 **3.94**（v2: 3.71，視覺 2.94，認證 4，社群 +0）
- 認證依據：太魯閣國家公園域內（合歡山；另合歡山國際暗空公園）
- 合成：視覺2.94＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [7, 6, 5, 6] 均分 None — File:Hehuan West Peak and Baigu Massif.jpg（None）
- B：子項 [7, 6, 5, 5] 均分 None — File:Hehuan Mountain Main Peak Trails-qwop11714-001.jpg（None）
- C：INVALID（非風景代表照）— File:An adult Taiwan vole (Microtus kikuchii) at Hehuan Mountain of Taiwan on September 25th, 2015.jpg

### tw-001 大屯山助航站 — v3 **3.38**（v2: 3.67，視覺 2.38，認證 4，社群 +0）
- 認證依據：陽明山國家公園域內（大屯山助航站）
- 合成：視覺2.38＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 3 張，有效 1 張
- A：INVALID（入口設施）— File:Datunshan Navigation Station gate closed.jpg
- B：子項 [5, 4, 4, 6] 均分 4.75 — File:Datunshan Navigation Station under white clouds and blue sky on 13th February 2016.jpg（commons-search）〈草坡雷達站藍天〉
- C：INVALID（通訊設施特寫）— File:No entry to Datunshan Navigation Station.jpg

### tw-038 三仙台 — v3 **4.0**（v2: 3.67，視覺 3.38，認證 4，社群 +0）
- 認證依據：東部海岸國家風景區域內（三仙台）
- 合成：視覺3.38＋認證校正0.62＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [7, 7, 6, 8] 均分 7.0 — File:Sansiantai Bridge 02.jpg（commons-search）〈八拱橋跨礁〉
- B：子項 [8, 7, 7, 8] 均分 7.5 — File:Taitung-County Taiwan Sansiantai-Bridge-01.jpg（commons-search）〈燈塔島浪湧〉
- C：子項 [7, 6, 6, 7] 均分 6.5 — File:Taitung-County Taiwan Sansiantai-Bridge-02.jpg（commons-search）〈拱橋特寫〉
- D：子項 [7, 6, 6, 7] 均分 6.5 — File:Tourists walk on the eight arch bridge at Sansiantai Scenic Area.jpg（commons-search）〈沙灘望橋〉
- E：子項 [8, 7, 7, 8] 均分 7.5 — File:Sanxiantai Eight-arch Bridge under blue sky with clouds on 14 May 2016.jpg（commons-search）〈藍水列礁〉
- F：子項 [7, 6, 6, 7] 均分 6.5 — File:Sanxiantai Eight-arch Bridge on 7 October 2011.jpg（commons-search）〈岩林框橋〉

### tw-040 玉山主峰 — v3 **4.0**（v2: 3.67，視覺 3.38，認證 4，社群 +0）
- 認證依據：玉山國家公園＋台灣最高峰
- 合成：視覺3.38＋認證校正0.62＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [8, 7, 6, 6] 均分 None — File:玉山主峰 08.jpg（None）
- B：子項 [6, 6, 7, 5] 均分 None — File:雪山主峰南側山坡的玉山圓柏白木林.jpg（None）
- C：子項 [8, 7, 7, 6] 均分 None — File:玉山主峰.jpg（None）

### tw-095 塔塔加夫妻樹／鹿林山觀景點 — v3 **4.0**（v2: 3.67，視覺 3.25，認證 4，社群 +0）
- 認證依據：玉山國家公園塔塔加遊憩區（夫妻樹/鹿林山）
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [7, 6, 6, 7] 均分 6.5 — File:Couple Tree in Yushan National Park.jpg（commons-search）〈夫妻樹雙枯木〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — File:Couple Tree near Tataka.jpg（commons-search）〈枯木草原〉
- C：子項 [7, 6, 6, 7] 均分 6.5 — File:塔塔加夫妻神木 - Tataka Couple Trees - 2012.02 - panoramio.jpg（commons-search）〈夫妻樹步道〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:夫妻樹 Couple Trees - panoramio.jpg（commons-search）〈樹影公路〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:The Husband of Couple Trees 老公樹 - panoramio.jpg（commons-search）〈巨幹神木〉
- F：INVALID（廟宇圍欄）— File:鹤岡鰜鲽老樹 Hegang Old Couple Trees - panoramio.jpg

### jp-038 蔵王樹氷（蔵王ロープウェイ・山形側） — v3 **4.0**（v2: 3.65，視覺 3.25，認證 4，社群 +0）
- 認證依據：藏王樹氷＝日本三大樹氷；藏王國定公園域內
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [7, 6, 6, 7] 均分 6.5 — File:Zao snow monsters.jpg（commons-search）〈樹氷全景〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — File:Mt.Zao(Mt.Jizo) Juhyo.JPG（commons-search）〈樹氷林遠眺〉
- C：子項 [8, 6, 6, 7] 均分 6.75 — File:Snow Monsters, Zao Onsen Ski Resort.jpg（commons-search）〈藍調樹氷〉
- D：子項 [6, 5, 6, 6] 均分 5.75 — File:Zao 20201226-2.jpg（commons-search）〈過飽和濾鏡〉
- E：子項 [7, 6, 6, 7] 均分 6.5 — File:Mt. Zao snow monsters (51843220026).jpg（commons-search）〈圍籬樹氷〉
- F：子項 [8, 7, 7, 7] 均分 7.25 — File:Mt. Zao snow monsters (51843581919).jpg（commons-search）〈夕光樹氷〉

### tw-035 六十石山 — v3 **3.0**（v2: 3.65，視覺 2.88，認證 3，社群 +0）
- 認證依據：六十石山金針花海——攝影攻略一致推薦，無官方認證
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [8, 7, 8, 7] 均分 7.5 — File:花蓮 六十石山 Liushidan Mountain,Hualien county,Taiwan - Flickr - JerryLai0208.jpg（commons-search）〈縱谷光柱〉
- B：子項 [5, 5, 5, 6] 均分 5.25 — File:六十石山金針花 - panoramio.jpg（commons-search）〈青草草原〉
- C：子項 [6, 5, 5, 6] 均分 5.5 — File:六十石山 panoramic, August 2017.jpg（commons-search）〈丘陵聚落〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:六十石山 pavilion view, August 2017 – Taiwan.jpg（commons-search）〈霧中梯田〉
- E：INVALID（花卉特寫）— File:Hemerocallis fulva flower at 六十石山.jpg
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:六十石山 view, August 2017.jpg（commons-search）〈金針花海丘陵〉

### tw-082 鯉魚潭 — v3 **3.62**（v2: 3.65，視覺 2.62，認證 4，社群 +0）
- 認證依據：花東縱谷國家風景區域內（鯉魚潭）
- 合成：視覺2.62＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Taiwan 2009 HuaLien Carp Lake FRD 5321.jpg（commons-search）〈霧山棧橋〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:花蓮鯉魚潭 Carp Lake, Hualian - panoramio.jpg（commons-search）〈綠湖倒影〉
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:花蓮鯉魚潭 HuaIian Liyu Lake - panoramio.jpg（commons-search）〈山色湖面〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:花蓮鯉魚潭 Carp Lake Hualian - panoramio.jpg（commons-search）〈礫岸步道〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:Carp Lake Hualian 花蓮鯉魚潭 - panoramio.jpg（commons-search）〈遊艇湖面〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Liyu Lake Hualien (37723288612).jpg（commons-search）〈湖畔涼亭〉

### us-006 布萊斯峽谷國家公園 — v3 **4.0**（v2: 3.65，視覺 3.62，認證 4，社群 +0）
- 認證依據：美國國家公園署（Bryce Canyon NP）官方
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Bryce Canyon Hoodoos.jpg（commons-search）〈岩柱深空〉
- B：子項 [8, 7, 6, 8] 均分 7.25 — File:Bryce Canyon Amphitheater Hoodoos Panorama.jpg（commons-search）〈露天劇場岩柱〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:USA 10638 Bryce Canyon Luca Galuzzi 2007.jpg（commons-search）〈林中岩柱〉
- D：子項 [9, 8, 7, 8] 均分 8.0 — File:USA 10654 Bryce Canyon Luca Galuzzi 2007.jpg（commons-search）〈雷神之錘〉
- E：子項 [9, 8, 8, 8] 均分 8.25 — File:Hoodoos in the Bryce Canyon National Park.jpg（commons-search）〈暮色岩柱泛光〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Bryce Amphitheater from Sunrise Point Highres 2013.jpg（commons-search）〈峽谷全景〉

### us-010 黃石國家公園 大稜鏡溫泉 — v3 **5**（v2: 3.65，視覺 4.12，認證 5，社群 +0）
- 認證依據：黃石＝UNESCO 世界遺產（大稜鏡溫泉）
- 合成：視覺4.12＋認證校正0.88＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [10, 9, 8, 10] 均分 9.25 — File:Grand prismatic spring.jpg（commons-search）〈大稜鏡空拍經典〉
- B：子項 [9, 8, 7, 9] 均分 8.25 — File:Grand Prismatic Spring and Midway Geyser Basin from above.jpg（commons-search）〈藍泉彩緣〉
- C：子項 [9, 8, 7, 9] 均分 8.25 — File:Grand prismatic no noise reduction.jpg（commons-search）〈松林彩泉〉
- D：子項 [9, 8, 7, 9] 均分 8.25 — File:Grand Prismatic Spring 2013.jpg（commons-search）〈蒸汽彩泉〉
- E：子項 [8, 7, 6, 8] 均分 7.25 — File:Yellowstone National Park (WY, USA), Grand Prismatic Spring -- 2022 -- 2514.jpg（commons-search）〈橙色菌流〉
- F：子項 [10, 9, 8, 10] 均分 9.25 — File:Yellowstone National Park (WY, USA), Grand Prismatic Spring -- 2022 -- 2519.jpg（commons-search）〈彩虹稜鏡全景〉

### us-020 紅木國家公園 — v3 **4.0**（v2: 3.65，視覺 3.0，認證 5，社群 +0）
- 認證依據：紅木國家公園＝UNESCO 世界遺產
- 合成：視覺3.0＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（縮圖下載失敗）— File:Costal Redwood.jpg
- B：子項 [9, 7, 7, 8] 均分 7.75 — File:Redwood National Park, fog in the forest.jpg（commons-search）〈霧光紅木巨杉〉
- C：子項 [7, 6, 4, 6] 均分 5.75 — File:Redwood National Park REDW9356.jpg（commons-search）〈暗林巨木〉
- D：子項 [6, 5, 4, 6] 均分 5.25 — File:Redwood National Park REDW9370.jpg（commons-search）〈霧蕨幽暗〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Hidden Beach, a beach in Redwood National Park.jpg（commons-search）〈海岸巨石灘〉
- F：INVALID（縮圖下載失敗）— File:Walk through Coast Redwood in Redwood National Park.jpg

### us-023 巨人柱國家公園 — v3 **4.0**（v2: 3.65，視覺 3.12，認證 4，社群 +0）
- 認證依據：美國國家公園署（Saguaro NP）官方
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（園區招牌）— File:Saguaro National Park East Entry.jpg
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Saguaronationalparl17102008.jpg（commons-search）〈巨柱仙人掌〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Saguaro National Park - Flickr - Joe Parks.jpg（commons-search）〈沙漠柱群〉
- D：INVALID（花卉特寫）— File:Saguaro National Monument West.jpg
- E：子項 [8, 7, 5, 7] 均分 6.75 — File:Saguaro National Park near Tucson Arizona (7334031850).jpg（commons-search）〈仙人掌森林〉
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:Carnegiea gigantea in Saguaro National Park near Tucson, Arizona during November (58).jpg（commons-search）〈孤柱草原〉

### us-038 大霧山國家公園 — v3 **4.0**（v2: 3.65，視覺 3.0，認證 5，社群 +0）
- 認證依據：大霧山＝UNESCO 世界遺產＋國際生物圈保留區
- 合成：視覺3.0＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Great Smoky Mountains NP.jpg（commons-search）〈幽暗溪潭〉
- B：INVALID（穀倉建築為主體）— File:Great Smoky Mountain NP - Barn.jpg
- C：INVALID（木屋建築）— File:Great Smoky Mountain NP - Mingus Mill.jpg
- D：子項 [7, 6, 6, 7] 均分 6.5 — File:Great Smoky Mountain NP - The Sinks.jpg（commons-search）〈階疊溪瀑〉
- E：子項 [7, 6, 5, 6] 均分 6.0 — File:Great Smoky Mountains NP - Valley.jpg（commons-search）〈草甸青山〉
- F：INVALID（人群主體）— File:A crowd gathers in a "bear jam" (Great Smoky Mountains NP) (3cd1df30-1dd8-b71b-0b2a-e54bb036b6c6).JPG

### us-041 迪納利國家公園 — v3 **4.0**（v2: 3.65，視覺 3.12，認證 4，社群 +0）
- 認證依據：美國國家公園署（Denali NP）官方
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [9, 8, 7, 9] 均分 8.25 — File:Wonder Lake, Denali2.jpg（commons-search）〈迪納利鏡湖〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Parque nacional y reserva Denali, Alaska, Estados Unidos, 2017-08-30, DD 72.jpg（commons-search）〈苔原遠峰〉
- C：INVALID（繪畫非照片）— File:Heinrich Berann NPS Panorama of Denali without labels.jpg
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Denali National Park, Alaska (16).jpg（commons-search）〈山脊殘雪〉
- E：INVALID（圈養馴鹿）— File:Animals of Denali National Park. Alaska, 2016 (177).jpg
- F：INVALID（水上飛機）— File:Denali National Park. Alaska 2016 (199).jpg

### tw-020 金龍山 — v3 **3.0**（v2: 3.54，視覺 2.38，認證 3，社群 +0）
- 認證依據：金龍山——攝影攻略一致推薦（曙光雲海），無官方認證
- 合成：視覺2.38＋認證校正0.62＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:南投魚池金龍山 Jinlongshan, Yuchi, Nantou 20220216204515 01.jpg（commons-search）〈層嵐山影〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:南投魚池金龍山 Jinlongshan, Yuchi, Nantou 20220216204515 03.jpg（commons-search）〈山城霧靄〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:南投魚池金龍山 Jinlongshan, Yuchi, Nantou 20220216204515 02.jpg（commons-search）〈樹框山巒〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:南投魚池金龍山 Jinlongshan, Yuchi, Nantou 20220216204649.jpg（commons-search）〈嵐氣層嶺〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:南投魚池金龍山 Jinlongshan, Yuchi, Nantou 20220218090140.jpg（commons-search）〈遠山如黛〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:南投魚池金龍山 Jinlongshan, Yuchi, Nantou 20220216204725.jpg（commons-search）〈枝影山城〉

### tw-083 雲山水夢幻湖 — v3 **3.0**（v2: 3.82，視覺 2.88，認證 3，社群 +0）
- 認證依據：雲山水夢幻湖——攝影攻略一致推薦，私人莊園無官方認證
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:34-花蓮雲山水 (28896718933).jpg（commons-search）〈湖畔別墅〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:雲山水夢幻湖 Yunshanshui Dream Lake - panoramio.jpg（commons-search）〈棕櫚綠湖〉
- C：子項 [6, 6, 4, 6] 均分 5.5 — File:雲山水夢幻湖 Yunshanshui Dream Lake - panoramio (1).jpg（commons-search）〈鏡面水色〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:View across Yunshanshui Dream Lake towards white bridge.jpg（commons-search）〈椰影倒映〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Reflection view of Yunshanshui Dream Lake at four o'clock in the afternoon.jpg（commons-search）〈薄霧湖畔〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Late afternoon view of Yunshanshui Dream Lake with Castle Villa l9 behind trees in the background.jpg（commons-search）〈草坪水岸〉

### jp-049 蔵王御釜（五色湖） — v3 **4.0**（v2: 3.5，視覺 3.88，認證 4，社群 +0）
- 認證依據：藏王御釜——藏王山域國定公園、五色湖名勝級攝影名點
- 合成：視覺3.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [9, 8, 6, 8] 均分 None — File:Zao L.Okama.JPG（None）
- B：子項 [9, 8, 5, 7] 均分 None — File:Lake Okama (Zao), Miyagi 02.jpg（None）
- C：子項 [9, 9, 6, 8] 均分 None — File:Lake Okama (Zao), Miyagi 06.jpg（None）

### tw-089 觀霧榛山步道觀景點 — v3 **3.0**（v2: 4.1，視覺 2.0，認證 4，社群 +0）
- 認證依據：雪霸國家公園觀霧遊憩區（榛山步道）
- 合成：視覺2.0＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（碑文石碑）— File:變雅堂遺集(七).djvu
- B：INVALID（園區石牌）— File:觀霧 Guanwu - panoramio.jpg
- C：子項 [4, 4, 3, 5] 均分 4.0 — File:Guanwu 觀霧 - panoramio.jpg（commons-search）〈暗部棧道〉
- D：子項 [5, 5, 5, 6] 均分 5.25 — File:Guanwu 觀霧 - panoramio (1).jpg（commons-search）〈霧林生態〉
- E：子項 [4, 4, 3, 5] 均分 4.0 — File:觀霧 Guanwu - panoramio (1).jpg（commons-search）〈霧鎖芒草步道〉
- F：子項 [4, 4, 3, 5] 均分 4.0 — File:Guanwu 觀霧 - panoramio (3).jpg（commons-search）〈霧林幽徑〉

### jp-040 美幌峠展望台 — v3 **4.0**（v2: 3.95，視覺 3.31，認證 4，社群 +0）
- 認證依據：阿寒摩周國立公園域內（美幌峠）
- 合成：視覺3.31＋認證校正0.69＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：INVALID（車內路牌）— File:R243bihoro.JPG
- B：INVALID（餐廳建築）— File:Michinoeki Gurutto Panorama Bihorotouge.jpg
- C：子項 [6, 6, 5, 7] 均分 6.0 — File:Bihoro Pass.JPG（commons-search）〈碑前屈斜路湖〉
- D：INVALID（餐廳建築）— File:Michinoeki Gurutto Panorama Bihorotouge 2019.jpg
- E：INVALID（標柱為主體）— File:Bihoro Pass 201909.jpg
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Lake Kussharoko Bihoro pass.jpg（commons-search）〈中島湖景〉

### tw-018 日月潭・水社壩湖景步道 — v3 **4.0**（v2: 3.52，視覺 3.06，認證 4，社群 +0）
- 認證依據：日月潭國家風景區域內（水社壩）
- 合成：視覺3.06＋認證校正0.94＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [7, 6, 6, 7] 均分 6.5 — File:Kandance2005 sun moon lake.jpg（commons-search）〈水社壩晚霞〉
- B：INVALID（地點待疑（異地塔樓夜景））— File:Sun and Moon Pagodas Guilin November 2017 HDR panorama.jpg
- C：INVALID（地點待疑（異地塔樓夜景））— File:Sun and Moon Pagodas Guilin November 2017 HDR.jpg
- D：INVALID（建築主體）— File:Sun Moon University.jpg
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Sun Moon Lake 20150202.jpg（commons-search）〈拉魯島霧景〉
- F：INVALID（書封非照片）— File:CADAL09012851 日月譚.djvu

### jp-041 知床ウトロ流氷（プユニ岬） — v3 **4.0**（v2: 3.5，視覺 3.0，認證 5，社群 +0）
- 認證依據：知床半島＝UNESCO 世界遺產（流冰海域為核心景觀）
- 合成：視覺3.0＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：INVALID（非風景代表照）— File:Ice in the Sea of Okhotsk (MODIS 2024-04-10).jpg
- B：子項 [7, 5, 5, 4] 均分 None — File:Drift ice in the Sea of Okhotsk.jpg（None）
- C：子項 [7, 7, 7, 6] 均分 None — File:JRH Senmo-main-line Kiha40 Drift-ice.jpg（None）

### tw-024 阿里山祝山觀日平台 — v3 **4.0**（v2: 3.5，視覺 3.25，認證 4，社群 +0）
- 認證依據：阿里山國家森林遊樂區（祝山觀日）
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [8, 7, 8, 7] 均分 7.5 — File:Alishan predawn.JPG（commons-search）〈祝山雲海日出〉
- B：子項 [8, 7, 8, 7] 均分 7.5 — File:阿里山祝山觀日出平台上的黎明景色.jpg（commons-search）〈金光雲海〉
- C：INVALID（車站月台）— File:祝山站 Zhushan Station - panoramio.jpg
- D：子項 [6, 4, 6, 6] 均分 5.5 — File:Sunrise at Zhushan, Alishan National Scenic Area 2020-01-03.jpg（commons-search）〈日出人群森林〉
- E：子項 [5, 5, 5, 6] 均分 5.25 — File:Zhushan Station 2012-12-10.jpg（commons-search）〈霧林觀日設施〉
- F：INVALID（車站屋頂）— File:Zhushan Station c. 2024.jpg

### tw-098 渭水之丘／櫻花陵園 — v3 **3.0**（v2: 3.5，視覺 2.69，認證 3，社群 +0）
- 認證依據：渭水之丘——攝影攻略一致推薦（俯瞰蘭陽平原），無官方認證
- 合成：視覺2.69＋認證校正0.31＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（陵園模型）— File:櫻花陵園（渭水之丘）.jpg
- B：INVALID（地圖）— File:Weishui.png
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Wei River,Ning Xiang county 02.JPG（commons-search）〈蘭陽溪口視野〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:7001在过渭河 10.jpg（commons-search）〈都市河景〉
- E：子項 [5, 5, 4, 6] 均分 5.0 — File:Wei River, 4 April 2021D.jpg（commons-search）〈溪綠濕地〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Wei River, 4 April 2021G.jpg（commons-search）〈蜿蜒濕原〉

### tw-060 七美雙心石滬 — v3 **3.0**（v2: 3.35，視覺 3.12，認證 3，社群 +0）
- 認證依據：澎湖國家風景區（官方）；雙心石滬無文化資產認定，攝影攻略高度推薦
- 合成：視覺3.12＋認證校正-0.12＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [8, 7, 5, 8] 均分 None — File:Double-Heart of Stacked Stones 20150721.jpg（None）
- B：子項 [8, 7, 4, 6] 均分 None — File:七美雙心石滬.jpg（None）
- C：子項 [8, 6, 4, 5] 均分 None — File:七美島雙心石滬.jpg（None）

### us-019 奧林匹克國家公園 — v3 **4.62**（v2: 3.35，視覺 3.62，認證 5，社群 +0）
- 認證依據：Olympic NP＝UNESCO 世界遺產＋國家公園署官方
- 合成：視覺3.62＋認證校正1＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：子項 [8, 8, 6, 7] 均分 None — File:Rock face, Ruby Beach, Olympic National Park, Washington State, 1992.JPG（None）
- B：INVALID（非風景代表照）— File:Olympic National Park ranger ca. 1960.png
- C：INVALID（非風景代表照）— File:Olympic national park 1949.jpg

### tw-041 雪山主峰 — v3 **4.0**（v2: 3.3，視覺 3.25，認證 4，社群 +0）
- 認證依據：雪霸國家公園域內（雪山主峰）
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [7, 6, 7, 6] 均分 None — File:雪山主峰南側山坡的玉山圓柏白木林.jpg（None）
- B：子項 [7, 7, 6, 6] 均分 None — File:HsuehMountain.jpg（None）
- C：子項 [6, 6, 5, 5] 均分 None — File:由雪山主峰看雪山圈谷.jpg（None）

### us-012 雷尼爾山國家公園 — v3 **4.0**（v2: 3.1，視覺 3.75，認證 4，社群 +0）
- 認證依據：美國國家公園署（Mount Rainier NP）官方
- 合成：視覺3.75＋認證校正0.25＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：INVALID（非風景代表照）— File:Golden-Mantled Ground Squirrel, Mount Rainier, July 2006.jpg
- B：子項 [7, 7, 6, 6] 均分 None — File:Tatoosh Range WA MRNP1.jpg（None）
- C：子項 [9, 8, 9, 8] 均分 None — File:Rainier Aerial West Close Washington Mar23 R16 07149.jpg（None）

### tw-076 龍磐公園／草原海岸 — v3 **3.12**（v2: 3.05，視覺 2.12，認證 4，社群 +0）
- 認證依據：墾丁國家公園域內
- 合成：視覺2.12＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 5 張，有效 3 張
- A：子項 [6, 5, 3, 3] 均分 None — File:Lungpan Park More 04.jpg（None）
- B：子項 [6, 5, 3, 3] 均分 None — File:Lungpan Park More 03.jpg（None）
- C：子項 [6, 5, 3, 3] 均分 None — File:Lungpan Park More 05.jpg（None）

### jp-002 旭岳 — v3 **4.0**（v2: new，視覺 3.25，認證 4，社群 +0）
- 認證依據：大雪山國立公園域內（旭岳，北海道最高峰）
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 4 張
- A：INVALID（車站建築）— File:MT-Asahi-mae Station-Building 3.jpg
- B：INVALID（黑白地圖）— File:MT-Asahi-mae Station-AP1946.jpg
- C：子項 [8, 7, 5, 7] 均分 6.75 — File:Mount Asahi (Daisetsuzan) under snow, April 2023 02.jpg（commons-search-topup）〈山頂雪原標柱〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Mount Asahi (Daisetsuzan) under snow, April 2023 03.jpg（commons-search-topup）〈山頂小祠雪景〉
- E：子項 [8, 7, 5, 7] 均分 6.75 — File:Mount Asahi (Daisetsuzan) under snow, April 2023 04.jpg（commons-search-topup）〈雪原錐峰〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Mount Asahi (Daisetsuzan) under snow, April 2023 07.jpg（commons-search-topup）〈雪徑滑降〉
- G：INVALID（非風景代表照）— File:Asahidake Ishimuro, Hokkaido, April 2023 01.jpg
- H：INVALID（非風景代表照）— File:Asahidake Ishimuro, Hokkaido, April 2023 02.jpg
- I：INVALID（非風景代表照）— File:MT-Mikawa Asahi Station.jpg
- J：INVALID（非風景代表照）— File:MT-Asahi-mae Station-Platform.JPG
- K：INVALID（非風景代表照）— File:Asahiyama uji01.jpg
- L：INVALID（非風景代表照）— File:MT-Asahi-mae Station-NorthGate.jpg

### jp-003 釧路濕原 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：釧路濕原國立公園＋Ramsar 濕地（日本最大濕原）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Kushiro Marsh.jpg（commons-search）〈展望台濕原〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Kushirositsugen Hosooka Tenboudai01.jpg（commons-search）〈綠原無垠〉
- C：子項 [7, 6, 6, 7] 均分 6.5 — File:釧路濕原國立公園 Kushiro Shitsugen National Park - panoramio.jpg（commons-search）〈濕原航拍紋理〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Kushiro Shitsugen.jpg（commons-search）〈藍天濕原〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Kushiro Marsh Wetland Hokkaido Panorama 2014.png（commons-search）〈林澤步道〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Kushiro Marsh, Shibecha.jpg（commons-search）〈葦原棧道〉

### jp-004 函館山夜景 — v3 **4.0**（v2: new，視覺 3.75，認證 4，社群 +0）
- 認證依據：函館山＝日本三大夜景（官方常引）
- 合成：視覺3.75＋認證校正0.25＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [8, 7, 7, 8] 均分 7.5 — File:Night view of Hakodate.jpg（commons-search）〈函館灣夜景〉
- B：INVALID（拼貼合成）— File:Hakodate montage.jpg
- C：INVALID（巴士車輛）— File:Hakodate Bus 0384.jpg
- D：子項 [8, 7, 7, 8] 均分 7.5 — File:函館山 夜景 The Night View From Mt Hakodate (139442723).jpeg（commons-search）〈灣口燈火〉
- E：子項 [8, 7, 7, 8] 均分 7.5 — File:2018-01-07 The million dollar night view.jpg（commons-search）〈夜光海灣〉
- F：子項 [8, 7, 7, 8] 均分 7.5 — File:Mount-Hakodate Night-view.jpg（commons-search）〈橘色燈海〉

### jp-005 小樽運河 — v3 **4.0**（v2: new，視覺 3.25，認證 4，社群 +0）
- 認證依據：小樽運河＝北海道遺產／日本の道100選官方選定
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無社群信號資料
- 照片來源：openverse, wiki-zh；抓到 6 張，有效 6 張
- A：子項 [8, 7, 7, 8] 均分 7.5 — File:Otaru Canal HDR2.jpg（wiki-zh）〈運河煤油燈〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — Otaru Canal（openverse）〈綠苔倉庫倒影〉
- C：子項 [7, 6, 6, 7] 均分 6.5 — File:Otaru Canal on July 19th, 2018.jpg（wiki-zh）〈紅磚倉庫〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — OTARU CANAL IN WINTER（openverse）〈雪後運河〉
- E：子項 [6, 5, 5, 6] 均分 5.5 — File:小樽運河-雪景.jpg（wiki-zh）〈冬日人影〉
- F：子項 [8, 7, 7, 8] 均分 7.5 — OTARU CANAL NIGHT VIEW（openverse）〈夜色倉庫群〉

### jp-006 摩周湖 — v3 **4.0**（v2: new，視覺 3.44，認證 4，社群 +0）
- 認證依據：阿寒摩周國立公園（特別保護區）、國指定名勝
- 合成：視覺3.44＋認證校正0.56＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [9, 7, 5, 7] 均分 None — File:Hokkaido, Japan, Lake Mashū, 2008.jpg（None）
- B：INVALID（非風景代表照）— File:Lake Mashu, Japan (ASTER).jpg
- C：子項 [9, 7, 5, 6] 均分 None — File:Lake Mashū 20200222-3.jpg（None）

### jp-007 十和田湖 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：十和田八幡平國立公園域內（十和田湖）
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：INVALID（衛星影像）— File:Lake towada landsat.jpg
- B：子項 [8, 7, 6, 8] 均分 7.25 — File:Lake Towada from Ohanabe 2008.jpg（commons-search）〈中山島鏡湖〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Lake Towada IMG 20161010 111654.jpg（commons-search）〈湖畔林壁〉
- D：INVALID（停車場巴士）— File:Hinomaru-Towada Kanko Dentetsu OP-21 Sky Bus at Lake Towada.jpg
- E：INVALID（解說標牌）— File:Lake towada 20220813121522 (52652330999).jpg
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Towada lake in Winter (51901382099).jpg（commons-search）〈雪嶺映湖〉

### jp-008 松島 — v3 **4.0**（v2: new，視覺 3.06，認證 4，社群 +0）
- 認證依據：松島＝日本三景
- 合成：視覺3.06＋認證校正0.94＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [7, 6, 6, 7] 均分 6.5 — File:Matsushima miyagi z.JPG（commons-search）〈松島群島遊船〉
- B：子項 [8, 7, 6, 7] 均分 7.0 — File:夏の松島 (The view of Matsushima) 08 Aug, 2010 - panoramio.jpg（commons-search）〈五大堂岩島〉
- C：INVALID（浮世繪版畫）— File:Utagawa-Hiroshige-III-Progression-During-the-Imperial-Inspection-at-Ou-Matsushima-1876.png
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Matsu Island-01.jpg（commons-search）〈孤島海景〉
- E：INVALID（街口車流）— File:Matsushima 3-chōme INT NNE from Matsushima-fureai Pedestrian Bridge Matsushima Harada Higashi-ku Fukuoka 20231012.jpg
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Matsushima along Umi River NNE from the W end of Matsushima-ōhashi Higashi-ku Fukuoka 20231016.jpg（commons-search）〈養殖筏灣〉

### jp-009 磐梯山 — v3 **4.0**（v2: new，視覺 3.12，認證 4，社群 +0）
- 認證依據：磐梯朝日國立公園＋日本百名山
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:Mt. Bandaisan 0811.JPG（commons-search）〈殘雪磐梯田疊〉
- B：INVALID（橋樑道路主體）— File:Lake Hibara-ko & Mt. Bandai-san.jpg
- C：INVALID（凍湖設施）— File:Mt. Bandai from Lake Hibara winter.JPG
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Mt.Bandai 10.jpg（commons-search）〈山容端正〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:磐梯山 - Mt. Bandai-san - panoramio.jpg（commons-search）〈芒草山麓〉
- F：INVALID（建築主體）— File:Mt. Bandai eruption memorial museum.jpg

### jp-010 大石公園 — v3 **3.0**（v2: new，視覺 3.19，認證 3，社群 +0）
- 認證依據：河口湖大石公園——多方攝影攻略一致推薦，無官方景觀認證
- 合成：視覺3.19＋認證校正-0.19＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：INVALID（地點不符（熱帶海岬））— File:Oishinohana.jpg
- B：子項 [9, 8, 7, 8] 均分 8.0 — File:Mount Fuji from Oishi Park.jpg（commons-search）〈湖上富士經典〉
- C：INVALID（設施與人群）— File:Oishi in Fujikawaguchiko 01.jpg
- D：INVALID（人群主體）— File:Oishi in Fujikawaguchiko 03.jpg
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:Oishi in Fujikawaguchiko 02.jpg（commons-search）〈庭園石徑〉
- F：INVALID（雕像施工）— File:Oishi in Fujikawaguchiko 05.jpg

### jp-011 東京鐵塔 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：東京鐵塔＝國家代表地標（國の重要文化財）
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 2 張
- A：INVALID（庭園非塔景）— File:Wooden footbridge in Shinjuku Gyoen National Garden, Tokyo, Japan, a sunny day with blue sky.jpg
- B：INVALID（異地建築）— File:Exterior view of the illuminated facade of Maison Hermès, Ginza, Tokyo, Japan.jpg
- C：INVALID（黑白街拍）— File:Soba-Noodles-Deliveryman-Tokyo-1935.png
- D：INVALID（異地建築）— File:Exterior view of the illuminated facade of Maison Hermès made of glass blocks, Ginza, Tokyo, Japan.jpg
- E：子項 [8, 7, 6, 8] 均分 7.25 — File:Japan-Tokyo-tower-1024.jpg（commons-search-topup）〈東京鐵塔紅架〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Tokyo Tower 2023.jpg（commons-search-topup）〈鐵塔天際線〉
- G：INVALID（非風景代表照）— File:Minato City, Tokyo, Japan (Night).jpg
- H：INVALID（非風景代表照）— File:Tokyo Tower, Minato City.jpg
- I：INVALID（非風景代表照）— File:Tokyo Tower-20091017-RM-102813.jpg
- J：INVALID（非風景代表照）— File:Tokyo Tower-20091017-RM-103413.jpg
- K：INVALID（非風景代表照）— File:Tokyo Shibuya Scramble Crossing 2018-10-09.jpg
- L：INVALID（非風景代表照）— File:Facade of the polyhedral glass building The Iceberg, Shibuya, Tokyo, Japan.jpg

### jp-013 諏訪湖 — v3 **3.0**（v2: new，視覺 2.88，認證 3，社群 +0）
- 認證依據：諏訪湖——攝影攻略一致推薦（花火/霧氷），無官方景觀認證
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [7, 6, 7, 7] 均分 6.75 — File:Lake Suwa, Nagano Prefecture; May 2019 (03).jpg（commons-search）〈湖上夕陽〉
- B：子項 [7, 6, 7, 7] 均分 6.75 — File:Lake Suwa, Nagano Prefecture; May 2019 (02).jpg（commons-search）〈棧橋燒霞〉
- C：子項 [6, 6, 6, 7] 均分 6.25 — File:Lake Suwa, Nagano Prefecture; May 2019 (04).jpg（commons-search）〈暮藍燈火〉
- D：子項 [5, 5, 5, 6] 均分 5.25 — File:Lake Suwa, Nagano Prefecture; May 2019 (05).jpg（commons-search）〈暗暮湖光〉
- E：子項 [5, 5, 5, 6] 均分 5.25 — File:Lake Suwa, Nagano Prefecture; May 2019 (06).jpg（commons-search）〈遠燈湖灣〉
- F：子項 [5, 5, 5, 6] 均分 5.25 — File:Lake Suwa, Nagano Prefecture; May 2019 (08).jpg（commons-search）〈夜霧湖岸〉

### jp-016 橫濱山下公園 — v3 **2.0**（v2: new，視覺 2.62，認證 2，社群 +0）
- 認證依據：橫濱市立海濱公園——無景觀認證
- 合成：視覺2.62＋認證校正-0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：INVALID（黑白歷史照）— File:Yamashita Park 1930s.jpg
- B：INVALID（明信片版畫）— File:The Grand Yokohama Exhibition.png
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Sea bus pier in Yamashita Park 2.jpg（commons-search）〈塔影船隊〉
- D：INVALID（人群主體）— File:Yamashita Park @ Yokohama (9054589120).jpg
- E：INVALID（人群主體）— File:Yamashita Park @ Yokohama (9054591494).jpg
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Yamashita Park @ Yokohama (9054590638).jpg（commons-search）〈草坪綠地〉

### jp-019 濱名湖 — v3 **3.0**（v2: new，視覺 2.06，認證 3，社群 +0）
- 認證依據：濱名湖——攝影攻略常見，無具體官方景觀認證
- 合成：視覺2.06＋認證校正0.94＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（衛星影像）— File:Lake hamana landsat.jpg
- B：INVALID（人物主體）— File:Lake Hamana 01.jpg
- C：子項 [5, 5, 5, 6] 均分 5.25 — File:Lake Hamana 03.jpg（commons-search）〈松影暗岸〉
- D：子項 [4, 4, 4, 5] 均分 4.25 — File:Lake Hamana Shizuoka, Japan.jpg（commons-search）〈舟影灰堤〉
- E：子項 [4, 4, 3, 5] 均分 4.0 — File:Lake Hamana Shizuoka, Japan 2.jpg（commons-search）〈灰海棕櫚〉
- F：子項 [4, 4, 3, 5] 均分 4.0 — File:Lake Hamana 浜名湖 - panoramio.jpg（commons-search）〈灰灣孤島〉

### jp-020 橫濱港未來21 — v3 **2.5**（v2: new，視覺 3.5，認證 2，社群 +0）
- 認證依據：橫濱港未來21＝都市開發區，無景觀認證
- 合成：視覺3.5＋認證校正-1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [8, 7, 7, 8] 均分 7.5 — File:070203 MM21&FUJI.jpg（commons-search）〈地標塔燒霞〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — File:Minato Mirai 21 views from Osanbashi Pier.jpg（commons-search）〈港灣郵輪〉
- C：子項 [8, 7, 7, 8] 均分 7.5 — File:Minato Mirai 21 at dusk IMG 4649.jpg（commons-search）〈夜摩天輪〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Yokohama Landmark Tower and Minato-Mirai waterfront seen from the boat.jpg（commons-search）〈灰雲港景〉
- E：INVALID（通道設施）— File:Minato Mirai 21 @ Yokohama (9054466278).jpg
- F：INVALID（建築特寫）— File:Minato Mirai 21 @ Yokohama (9052267333).jpg

### jp-021 新穗高・西穗高口展望台 — v3 **4.0**（v2: new，視覺 3.25，認證 4，社群 +0）
- 認證依據：中部山岳國立公園域內（新穗高纜車西穗高口）
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：INVALID（文件書頁）— File:CADAL09012027 展望.djvu
- B：INVALID（書頁）— File:CADAL09002318 世界新形勢.djvu
- C：INVALID（書頁）— File:CADAL11100765 東方文藝復興的展望·上冊.djvu
- D：INVALID（書頁）— File:CADAL11109814 中國行政新論.djvu
- E：INVALID（書頁）— File:CADAL11105490 新狂飈時代.djvu
- F：子項 [7, 6, 6, 7] 均分 6.5 — File:Shinhotaka ropeway01s3200.jpg（commons-search）〈雪嶺纜車〉

### jp-022 彌彥山頂公園・Panorama Tower — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：佐渡彌彥米山國定公園域內（彌彥山）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 5 張，有效 1 張
- A：INVALID（紅葉特寫）— File:Red Maple Leaves in Yahiko.JPG
- B：INVALID（行政區地圖）— File:Yahiko in Niigata Prefecture.png
- C：INVALID（道路設施）— File:Niigata r2 Yahiko Fumoto April2020.jpg
- D：INVALID（林道非風景）— File:Niigata r2 Yahiko Kamiizumi April2020.jpg
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Momiji-dani, Yahiko Park, Yahiko, Niigata, Japan, November 2022.png（commons-search）〈彌彥紅葉步道〉

### jp-023 京都清水寺 — v3 **5**（v2: new，視覺 4.06，認證 5，社群 +0）
- 認證依據：清水寺＝UNESCO 世界文化遺產（古都京都文化財）
- 合成：視覺4.06＋認證校正0.94＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 7, 9] 均分 8.25 — File:Kiyomizu-dera, Kyoto, November 2016 -01.jpg（commons-search）〈清水舞台紅葉〉
- B：子項 [9, 8, 7, 9] 均分 8.25 — File:Kiyomizu-dera, Kyoto, November 2016 -02.jpg（commons-search）〈三重塔舞台〉
- C：子項 [9, 8, 6, 9] 均分 8.0 — File:Kiyomizu-dera, Kyoto, November 2016 -03.jpg（commons-search）〈楓塔同框〉
- D：子項 [8, 7, 7, 8] 均分 7.5 — File:Kiyomizu-dera, Kyoto, November 2016 -05.jpg（commons-search）〈夜楓點燈〉
- E：子項 [9, 8, 8, 8] 均分 8.25 — File:Kiyomizu-dera, Kyoto, November 2016 -06.jpg（commons-search）〈夜間舞台全景〉
- F：子項 [8, 7, 7, 8] 均分 7.5 — File:Kiyomizu-dera, Kyoto, November 2016 -07.jpg（commons-search）〈夜塔紅葉〉

### jp-025 萩城下町・菊屋橫町 — v3 **3.88**（v2: new，視覺 2.88，認證 5，社群 +0）
- 認證依據：萩城下町＝UNESCO 明治日本產業革命遺產構成資產
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Kikuya Lane in Hagi Castle Town 3.jpg（commons-search）〈白壁土塀巷〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Kikuya Lane in Hagi Castle Town 1.jpg（commons-search）〈格窗土牆〉
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Kikuya Lane in Hagi Castle Town 2.jpg（commons-search）〈城下町街屋〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Kikuya Lane in Hagi Castle Town 4.jpg（commons-search）〈菊屋橫町〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Kikuya Lane in Hagi Castle Town 7.jpg（commons-search）〈町家延伸〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Kikuya Lane in Hagi Castle Town 5.jpg（commons-search）〈土牀巷景〉

### jp-026 出雲大社 — v3 **4.0**（v2: new，視覺 3.0，認證 4，社群 +0）
- 認證依據：出雲大社＝國寶建築、國家級神社
- 合成：視覺3.0＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：wiki-en, wiki-zh；抓到 6 張，有效 5 張
- A：INVALID（器物特寫）— File:Izumo-shrine Shin-no-mihashira.jpg
- B：子項 [8, 7, 5, 7] 均分 6.75 — File:Izumo-shrine Haiden01.jpg（wiki-en）〈神樂殿大屋頂〉
- C：子項 [7, 6, 5, 6] 均分 6.0 — File:Izumo-taisha 121538651 f69f257ed0 o.jpg（wiki-zh）〈古社松影〉
- D：子項 [7, 6, 5, 6] 均分 6.0 — File:Izumo-shrine Haiden Honden.jpg（wiki-en）〈社殿境內〉
- E：子項 [7, 6, 5, 6] 均分 6.0 — File:IzumoTaisha-honden.JPG（wiki-zh）〈屋脊連綿〉
- F：子項 [6, 5, 4, 6] 均分 5.25 — File:Izumo-taisha10n4592.jpg（wiki-en）〈講社木造〉

### jp-027 神戶六甲山 — v3 **2.88**（v2: new，視覺 1.88，認證 4，社群 +0）
- 認證依據：六甲山（摩耶夜景＝日本新三大夜景區域；六甲山為國立公園）
- 合成：視覺1.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：子項 [3, 4, 3, 5] 均分 None — File:Rokkosan pasture08s1920.jpg（None）
- B：INVALID（非風景代表照）— File:Cow at Rokkosan Pasture, Kobe, Japan.jpg
- C：INVALID（非風景代表照）— File:Kid at Rokkosan Pasture, Kobe, Japan.jpg

### jp-028 高野山 — v3 **3.88**（v2: new，視覺 2.88，認證 5，社群 +0）
- 認證依據：高野山＝UNESCO 紀伊山地靈場與參詣道
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [7, 6, 4, 6] 均分 5.75 — File:高野山 一乗院1 Koyasan (Mount Koya) - panoramio.jpg（commons-search）〈總門伽藍〉
- B：INVALID（石佛特寫）— File:Japanese maple and cement lantern at Mount Kōya 500px photo (188687305).jpg
- C：子項 [6, 5, 4, 6] 均分 5.25 — File:Mount Kōya unidentified buildings with Japanese maple in the background 500px photo (188687307).jpg（commons-search）〈大門簷影〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Japanese maple at Mount Kōya 500px photo (188687301).jpg（commons-search）〈青楓塔頭〉
- E：子項 [6, 6, 6, 6] 均分 6.0 — File:Mount Koya - Flickr - Marco Togni fotografo.jpg（commons-search）〈參道煙香〉
- F：INVALID（電車車輛）— File:Mount Kōya (Kōya-san), Wakayama Prefecture; April 2012 (04).jpg

### jp-029 伊賀上野城 — v3 **3.75**（v2: new，視覺 2.75，認證 4，社群 +0）
- 認證依據：伊賀上野城＝國家重要文化財（日本百名城）
- 合成：視覺2.75＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（石碑）— File:伊賀上野城3 Iga Ueno Castle - panoramio.jpg
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:伊賀上野城2 Iga Ueno Castle - panoramio.jpg（commons-search）〈白牆櫻花〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Iga Ueno Castle, 伊賀上野城 - panoramio (8).jpg（commons-search）〈城門老木〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Iga Ueno Castle, 伊賀上野城 - panoramio (15).jpg（commons-search）〈石垣眺城下〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:Iga Ueno Castle, 伊賀上野城 - panoramio (18).jpg（commons-search）〈石階林道〉
- F：INVALID（岩石特寫）— File:Iga Ueno Castle, 伊賀上野城 - panoramio (20).jpg

### jp-030 鳴門海峽漩渦 — v3 **4.0**（v2: new，視覺 3.12，認證 4，社群 +0）
- 認證依據：瀬戶內海國立公園域內（鳴門）
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [7, 7, 7, 7] 均分 None — File:Naruto Whirlpools taken 4-21-2008.jpg（None）
- B：INVALID（非風景代表照）— File:Awa, Naruto Whirlpools, ca 1855.jpg
- C：子項 [6, 5, 5, 6] 均分 None — File:Naruto whirlpools 20170609-1.jpg（None）

### jp-031 倉敷美觀地區 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：倉敷美觀地區＝重要傳統的建造物群保存地區（國家選定）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:倉敷美觀地區 Kurashiki Bikan Historical Quarter - panoramio.jpg（commons-search）〈町家格子窗〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Kurashiki Bikan historical quarter 1.jpg（commons-search）〈倉敷川柳橋〉
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Kurashiki Bikan historical quarter 2.jpg（commons-search）〈白壁小巷〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Kurashiki Bikan historical quarter 3.jpg（commons-search）〈川舟景〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Kurashiki Bikan historical quarter 20190324.jpg（commons-search）〈洋館運河〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Kurashiki Bikan historical quarter 20190324-2.jpg（commons-search）〈本町通り〉

### jp-032 福岡城跡 — v3 **3.38**（v2: new，視覺 2.38，認證 4，社群 +0）
- 認證依據：福岡城跡＝國指定史跡
- 合成：視覺2.38＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Hyakken-Ishigaki stone wall (one of the Onojo-Castle ruins).jpg（commons-search）〈亂石垣〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:Kita-ishigaki Stonewall(one of the Onojo-Castle-Ruins).jpg（commons-search）〈殘雪石垣〉
- C：子項 [4, 4, 3, 4] 均分 3.75 — File:Ko-ishigaki Stonewall(one of the Onojo-Castle-Ruins).jpg（commons-search）〈土坡雜木〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Sakura at Fukuoka Castle March2013 08.jpg（commons-search）〈櫻下城跡〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:大野城（筑前国）太宰府口.jpg（commons-search）〈苔石垣〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:大野城（筑前国）百間石垣.jpg（commons-search）〈綠苔牆根〉

### jp-033 唐津城 — v3 **3.0**（v2: new，視覺 2.75，認證 3，社群 +0）
- 認證依據：唐津城＝舞鶴城，櫻/藤名所、觀光排名常客；無官方百選佐證
- 合成：視覺2.75＋認證校正0.25＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [5, 6, 5, 6] 均分 None — File:Karatsujo.jpg（None）
- B：子項 [5, 6, 4, 5] 均分 None — File:Karatsu Castle.jpg（None）
- C：子項 [5, 7, 5, 7] 均分 None — File:桜と唐津城 (Karatsu Castle with Cherry blossoms) 30 Mar, 2014 - panoramio.jpg（None）

### jp-034 長崎哥拉巴園 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：哥拉巴園＝長崎南山手重要傳統的建造物群保存地區
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Nagasaki-Glover-Garden-5415.jpg（commons-search）〈南山手庭園〉
- B：INVALID（室內）— File:Glover Garden Nagasaki-150821367.jpg
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:View of ships from Glover Garden-12.jpg（commons-search）〈港灣眺望〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:View of ships from Glover Garden-06.jpg（commons-search）〈坡地港景〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:View of ships from Glover Garden-03.jpg（commons-search）〈庭園步道〉
- F：INVALID（電扶梯設施）— File:Glover Garden Nagasaki-150821401.jpg

### jp-035 福岡塔 — v3 **2.0**（v2: new，視覺 2.38，認證 2，社群 +0）
- 認證依據：福岡塔＝現代都市塔，無景觀認證
- 合成：視覺2.38＋認證校正-0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Fukuoka Tower October 2011 01.jpg（commons-search）〈塔身街景〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:Fukuoka Tower Before Sunset.jpg（commons-search）〈路口塔影〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:View of Fukuoka Tower from Seaside Momochi Seaside Park area around 902-1 Momochihama-2-chōme Sawara-ku Fukuoka City 20221213.jpg（commons-search）〈塔區廣場〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:Seaside Momochi Seaside Park the view of Fukuoka Tower Momochi-hama 2-chōme Sawara-ku Fukuoka 20231121.jpg（commons-search）〈塔體側看〉
- E：子項 [6, 5, 5, 6] 均分 5.5 — File:Fukuoka Tower the view from Marizon Momochi-hama 2-chōme Sawara-ku Fukuoka 20231103.jpg（commons-search）〈夜光塔身〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Fukuoka Tower the W side 3-26 Momochi-hama 2-chōme Sawara-ku Fukuoka 20240611.jpg（commons-search）〈塔鄰高樓〉

### jp-036 高千穗峽 — v3 **4.0**（v2: new，視覺 3.88，認證 4，社群 +0）
- 認證依據：國指定名勝（高千穗峽）＋名水百選
- 合成：視覺3.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [9, 8, 7, 7] 均分 None — File:秋色の高千穂峡 (Autumn Colored Takachiho Gorge) 24 Nov, 2012 - panoramio.jpg（None）
- B：子項 [8, 7, 5, 6] 均分 None — File:Takachihokyo (18297992885).jpg（None）
- C：子項 [10, 8, 6, 7] 均分 None — File:Takachihokyo 20170219-2.jpg（None）

### tw-003 淡水漁人碼頭 — v3 **3.0**（v2: new，視覺 3.31，認證 3，社群 +0）
- 認證依據：淡水漁人碼頭夕照——攝影攻略一致推薦，無官方景觀認證
- 合成：視覺3.31＋認證校正-0.31＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Tamsui Fisherman's Wharf 2012.jpg（commons-search）〈漁港城堡旅館〉
- B：子項 [8, 7, 8, 7] 均分 7.5 — File:2020 Sunset of Tamsui Fisherman's Wharf.jpg（commons-search）〈情人橋夕照〉
- C：INVALID（輕軌車站）— File:2020-11-15 Tamsui Fisherman's Wharf Station.jpg
- D：INVALID（輕軌車站）— File:2022 Tamsui Fisherman's Wharf Station Ni.jpg
- E：INVALID（車站月台）— File:2022 Tamsui Fisherman's Wharf Station N.jpg
- F：INVALID（站體特寫）— File:Danhai LRT Tamsui Fisherman's Wharf Station.jpeg

### tw-004 不厭亭 — v3 **3.0**（v2: new，視覺 3.38，認證 3，社群 +0）
- 認證依據：不厭亭——攝影攻略一致推薦（寂寞公路），無官方認證
- 合成：視覺3.38＋認證校正-0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [7, 7, 6, 7] 均分 6.75 — File:Looking down from Buyan Pavilion.jpg（commons-search）〈不厭亭經典彎道〉
- B：子項 [7, 7, 6, 7] 均分 6.75 — File:City Highway 102 with blossom miscanthus on both side.jpg（commons-search）〈芒草S彎〉
- C：子項 [7, 7, 6, 7] 均分 6.75 — File:View along City Highway 102 towards Buyan Pavilion.jpg（commons-search）〈稜線公路〉
- D：子項 [7, 7, 6, 7] 均分 6.75 — File:Looking down road from Buyan Pavilion.jpg（commons-search）〈寂寞公路〉
- E：INVALID（碑文石碑）— File:考亭淵源錄(四).djvu
- F：INVALID（碑文石碑）— File:棕亭古文鈔(二).djvu

### tw-005 大稻埕碼頭 — v3 **3.0**（v2: new，視覺 3.0，認證 3，社群 +0）
- 認證依據：大稻埕碼頭夕照——攝影攻略一致推薦
- 合成：視覺3.0＋認證校正0.0＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Dadaocheng Wharf main gate 20101004.jpg（commons-search）〈碼頭門樓〉
- B：INVALID（街景雜訊）— File:Taipei Taiwan Flood-Gate-01.jpg
- C：INVALID（夜市攤位）— File:2018 Dadaocheng Wharf 街頭藝人展演區 Août.jpg
- D：子項 [7, 6, 6, 7] 均分 6.5 — File:Dadaocheng Wharf.jpg（commons-search）〈淡水河夜景〉
- E：子項 [6, 6, 6, 6] 均分 6.0 — File:Sanchong skyline from Dadaocheng Wharf 2013.jpg（commons-search）〈河畔夜騎〉
- F：INVALID（車輛主體）— File:TCFD BFY-6930 left side at Dadaocheng Wharf 20230422 (cropped).jpg

### tw-006 關渡大橋 — v3 **2.0**（v2: new，視覺 2.69，認證 2，社群 +0）
- 認證依據：關渡大橋＝橋樑設施，無景觀認證
- 合成：視覺2.69＋認證校正-0.69＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [6, 6, 5, 7] 均分 6.0 — File:Guandu Bridge.jpg（commons-search）〈紅橋倒影〉
- B：INVALID（塔樓建築）— File:202601 Guandu Bridge observation tower (Bali Left Bank) 01.jpg
- C：INVALID（設施夜景）— File:202602 Guandu Bridge observation tower (Tamsui Right Bank) 02 (135mm 焦距).jpg
- D：INVALID（塔樓建築）— File:202602 Guandu Bridge observation tower (Tamsui Right Bank) 01.jpg
- E：INVALID（夜光塔樓）— File:202602 Guandu Bridge observation tower (Tamsui Right Bank) 02.jpg
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Guandu Bridge from Tamsui March 2026.jpg（commons-search）〈河口遠望〉

### tw-007 碧潭 — v3 **3.38**（v2: new，視覺 2.38，認證 4，社群 +0）
- 認證依據：碧潭＝日治台灣八景選定（新店溪畔官方歷史選景）
- 合成：視覺2.38＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:碧潭.jpg（commons-search）〈吊橋遠景綠地〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:Bitan Xindian.jpg（commons-search）〈河畔樓影〉
- C：INVALID（地點待疑岩壁）— File:Bitan 碧潭 - panoramio.jpg
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Bitan Scenic Area 碧潭風景區 - panoramio.jpg（commons-search）〈碧潭吊橋〉
- E：INVALID（地點待疑石潭）— File:碧潭 Bitan - panoramio (1).jpg
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:碧潭 Bitan - panoramio (3).jpg（commons-search）〈碧潭泛舟〉

### tw-008 觀音山硬漢嶺 — v3 **3.38**（v2: new，視覺 2.38，認證 4，社群 +0）
- 認證依據：北海岸及觀音山國家風景區域內（硬漢嶺）
- 合成：視覺2.38＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：INVALID（繪畫非照片）— File:Guanyin mountain.jpg
- B：INVALID（民宅非風景）— File:Villas around Guangdong Guanyin Mountain Forest Park 01.jpg
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Across the power grid of Guanyin Mountain.jpg（commons-search）〈步道欄杆眺望〉
- D：INVALID（民宅非風景）— File:Villas around Guangdong Guanyin Mountain Forest Park 04.jpg
- E：INVALID（民宅非風景）— File:Villas around Guangdong Guanyin Mountain Forest Park 02.jpg
- F：INVALID（雕飾特寫）— File:2020 Lianzuo Mountain Guanyin Temple.jpg

### tw-009 望幽谷 — v3 **3.0**（v2: new，視覺 3.25，認證 3，社群 +0）
- 認證依據：望幽谷——攝影攻略一致推薦，無官方景觀認證
- 合成：視覺3.25＋認證校正-0.25＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 2 張
- A：INVALID（書頁文獻）— File:望溪先生文集(九).djvu
- B：INVALID（書頁文獻）— File:CADAL09009320 方望溪先生全集·（一）.djvu
- C：INVALID（書頁文獻）— File:CADAL09009325 方望溪先生全集·（六）.djvu
- D：INVALID（書頁文獻）— File:CADAL09009326 方望溪先生全集·（七）.djvu
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:望幽谷 Wangyou Valley - panoramio.jpg（commons-search-topup）〈綠谷步道〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Wangyou Valley 望幽谷 - panoramio.jpg（commons-search-topup）〈望基隆嶼海崖〉
- G：INVALID（非風景代表照）— File:望幽谷 Wangyou Valley - panoramio (2).jpg
- H：INVALID（非風景代表照）— File:望幽谷 Wangyou Valley - panoramio (3).jpg
- I：INVALID（非風景代表照）— File:望幽谷 Wangyou Valley - panoramio (4).jpg
- J：INVALID（非風景代表照）— File:2022 Wangyou Valley at Zhongzheng District Keelung.jpg
- K：INVALID（非風景代表照）— File:Sibu Congkan Xubian362-李復言-續幽怪錄-1-1.djvu
- L：INVALID（非風景代表照）— File:望溪先生文集(八).djvu

### tw-010 和平島 — v3 **4.0**（v2: new，視覺 3.12，認證 4，社群 +0）
- 認證依據：北海岸及觀音山國家風景區域內（和平島公園）
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:Peace Island Coast Park 和平島公園 - panoramio.jpg（commons-search）〈綠藻礁石〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — File:Peace Island Park 和平島公園 - panoramio.jpg（commons-search）〈萬人堆疊石台〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:和平島海岸 coast of heping island - panoramio.jpg（commons-search）〈蕈狀風化岩〉
- D：子項 [7, 6, 6, 7] 均分 6.5 — File:Heping Island Park 07.23.jpg（commons-search）〈基隆嶼框景〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Heping Island 20240116 01.jpg（commons-search）〈礁岩海岸〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Heping Island 20240116 03.jpg（commons-search）〈岩區營地〉

### tw-011 永安漁港 — v3 **2.0**（v2: new，視覺 2.69，認證 2，社群 +0）
- 認證依據：永安漁港＝地方漁港設施，無景觀認證
- 合成：視覺2.69＋認證校正-0.69＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [5, 5, 5, 5] 均分 5.0 — File:永安漁港 Yongan Fishing Harbor - panoramio (1).jpg（commons-search）〈防波堤燈塔〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Yong'an fishing port 201805.jpg（commons-search）〈觀海橋白拱〉
- C：INVALID（工程施工）— File:2021 Yong-An Fishing Port ii.jpg
- D：子項 [6, 6, 6, 6] 均分 6.0 — File:2021 Yong-An Fishing Port i.jpg（commons-search）〈沙灘日出燈杆〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:2021 Yong-An Fishing Port oii.jpg（commons-search）〈港區全景〉
- F：INVALID（建築特寫）— File:2021 Yong-An Fishing Port oi.jpg

### tw-013 火炎山 — v3 **4.0**（v2: new，視覺 3.38，認證 4，社群 +0）
- 認證依據：火炎山自然保留區（國家級保留區）
- 合成：視覺3.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（建築主體）— File:Miaoli County Huoyan Mountain Ecology Museum.JPG
- B：子項 [8, 7, 6, 8] 均分 7.25 — File:Huoyan Mountain+MingHsiung Yang+02.jpg（commons-search）〈惡地稜脊〉
- C：INVALID（車窗模糊）— File:View of Mount Houyan on Freeway 1.jpg
- D：子項 [8, 7, 6, 7] 均分 7.0 — File:17750 kkshe. 02.jpg（commons-search）〈火炎山岩峰〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:17750 kkshe 01.jpg（commons-search）〈惡地平原〉
- F：子項 [7, 6, 6, 7] 均分 6.5 — File:Huoyan Mountain weisheng lu 3.jpg（commons-search）〈卵石河床夕照〉

### tw-015 高美濕地 — v3 **4.0**（v2: new，視覺 3.0，認證 4，社群 +0）
- 認證依據：高美濕地野生動物保護區＋國家級重要濕地（官方）
- 合成：視覺3.0＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 8, 8] 均分 8.25 — File:Gaomei Wetland kuocw 416 555594017.jpg（commons-search）〈高美夕照鏡面〉
- B：子項 [8, 7, 7, 8] 均分 7.5 — File:Gaomei Wetland Huang Chung Yu 02.jpg（commons-search）〈藍調濕地〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Gaomei Wetland chung photography.jpg（commons-search）〈風車濕原〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Taichung Gaomei Wetland Preservation Area-Huang pin yi-555594035(1).jpg（commons-search）〈木棧草海〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Taichung Gaomei Wetland Preservation Area-Huang pin yi-555594035(2).jpg（commons-search）〈石滬步道〉
- F：子項 [6, 5, 5, 6] 均分 5.5 — File:Gaomei wetland scenic trail.jpg（commons-search）〈棧道遊客〉

### tw-016 鳶嘴山 — v3 **3.38**（v2: new，視覺 2.38，認證 4，社群 +0）
- 認證依據：雪霸國家公園域內（鳶嘴—稍來山步道）
- 合成：視覺2.38＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:Yuanzui Mountain.jpg（commons-search）〈鳶嘴峭壁〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:2019 Yuanzui Mountain 鳶嘴山.jpg（commons-search）〈岩稜松林〉
- C：INVALID（碑石）— File:2019 Top of Yuanzui Mountain (2180m).jpg
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:浪漫台三線-台灣台中東勢-鳥瞰鳶嘴山-02.jpg（commons-search）〈遠山嵐氣〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:浪漫台三線-台灣台中東勢-鳥瞰鳶嘴山-06.jpg（commons-search）〈山城遠望〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:浪漫台三線-台灣台中東勢-鳥瞰鳶嘴山-10.jpg（commons-search）〈雲影山巒〉

### tw-017 王功漁港 — v3 **3.0**（v2: new，視覺 2.0，認證 3，社群 +0）
- 認證依據：王功漁港夕照——攝影攻略一致推薦（芳苑濕地）
- 合成：視覺2.0＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：INVALID（街景）— File:彰化縣芳苑鄉 王功 - panoramio.jpg
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:彰化縣芳苑鄉 王功 - panoramio (1).jpg（commons-search）〈蚵架殘構〉
- C：子項 [4, 4, 4, 5] 均分 4.25 — File:彰化縣芳苑鄉 王功 未完成的西濱快速公路 - panoramio.jpg（commons-search）〈橋墩灰調〉
- D：子項 [4, 4, 4, 4] 均分 4.0 — File:彰化縣芳苑鄉 王功漁港 - panoramio (7).jpg（commons-search）〈頹橋木棧〉
- E：子項 [4, 4, 3, 5] 均分 4.0 — File:彰化縣芳苑鄉 王功漁港 - panoramio (8).jpg（commons-search）〈林間步道〉
- F：子項 [4, 4, 3, 5] 均分 4.0 — File:彰化縣芳苑鄉 王功漁港 - panoramio (9).jpg（commons-search）〈紅橋綠蔭〉

### tw-021 武界部落 — v3 **3.0**（v2: new，視覺 2.38，認證 3，社群 +0）
- 認證依據：武界部落——攝影攻略一致推薦（滿江紅/雲海）
- 合成：視覺2.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Wujie Overlook.jpg（commons-search）〈曲流村谷〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:Wujie in the far distance.jpg（commons-search）〈竹園部落〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Overlooking the Zhuoshui River towards Wujie in the distance.jpg（commons-search）〈溪床土石〉
- D：INVALID（建築主體）— File:Wujie Police Station, as taken on 11th October 2020.jpg
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:Overlooking Wujie from Nantou Township Road 71, as taken on 11th October 2020.jpg（commons-search）〈谷地村落〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:View of the Zhuoshui River as it flows through Wujie, as taken on 11th October 2020.jpg（commons-search）〈河階田園〉

### tw-023 頂石棹 — v3 **unknown**（v2: new，視覺 None，認證 4，社群 +0）
- 認證依據：阿里山國家風景區域內（頂石棹）
- 合成：unknown：無有效代表照片（有認證但無視覺信號，不虛構分數）；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 8 張，有效 0 張
- A：INVALID（涼亭解說牌）— File:頂石棹步道櫻之道.2023-11-10.jpg
- B：INVALID（地點不符（海灣暮色））— File:Sonnenuntergang (202659845).jpeg
- C：INVALID（花卉特寫）— File:嘉義縣竹崎鄉 頂石棹櫻花 - panoramio (1).jpg
- D：INVALID（花卉特寫）— File:嘉義縣竹崎鄉 頂石棹櫻花 - panoramio (2).jpg
- E：INVALID（花卉特寫）— File:嘉義縣竹崎鄉 頂石棹櫻花 - panoramio (3).jpg
- F：INVALID（花卉特寫）— File:嘉義縣竹崎鄉 頂石棹櫻花 - panoramio (4).jpg
- G：INVALID（非風景代表照）— File:嘉義縣竹崎鄉 頂石棹櫻花 - panoramio (7).jpg
- H：INVALID（非風景代表照）— File:嘉義縣竹崎鄉 頂石棹櫻花 - panoramio (8).jpg

### tw-027 田寮月世界 — v3 **3.0**（v2: new，視覺 3.12，認證 3，社群 +0）
- 認證依據：田寮月世界——攝影攻略一致推薦（惡地），地方政府風景區非國家級
- 合成：視覺3.12＋認證校正-0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（車內視角）— File:Tianliao Moon World.JPG
- B：子項 [8, 7, 5, 7] 均分 6.75 — File:Tianliao Moon World 2.jpg（commons-search）〈月世界惡地〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Tianliao Moon World 1.jpg（commons-search）〈白堊河谷〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Tianliao Moon World 2018.jpg（commons-search）〈灰岩嶙峋〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Tianliao Moon World 3.jpg（commons-search）〈惡地全景〉
- F：INVALID（展示館建築）— File:Tianliao-Moon-World-Tourist-Information-Center-20230527-2.jpg

### tw-028 駁二藝術特區 — v3 **2.0**（v2: new，視覺 2.38，認證 2，社群 +0）
- 認證依據：駁二藝術特區＝文創園區，無景觀認證
- 合成：視覺2.38＋認證校正-0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Pier-2 Art Center.jpg（commons-search）〈倉庫彩繪區〉
- B：INVALID（路口街景）— File:Dayong Road in front of Pier-2 Art Center 2013-06.15.jpg
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:高雄市鹽埕區 駁二藝術特區自行車道 Pier-2 Art Center,Bicycle path(Yancheng,Kaohsiung City) - panoramio (1).jpg（commons-search）〈自行車道廠房〉
- D：INVALID（過飽和天際線）— File:Kaohsiung skyline from Pier 2 Art District.jpg
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:The Pier-2 Art Center 2020070901.jpg（commons-search）〈舊倉庫群〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:The Pier-2 Art Center 2020070902.jpg（commons-search）〈倉庫巷景〉

### tw-029 鵝鑾鼻燈塔 — v3 **4.0**（v2: new，視覺 3.12，認證 4，社群 +0）
- 認證依據：墾丁國家公園域內＋國定古蹟（鵝鑾鼻燈塔）
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Eluanbi Lighthouse 02.jpg（commons-search）〈燈塔草坪〉
- B：子項 [8, 7, 6, 8] 均分 7.25 — File:Hengchun-Township Taiwan Eluanbi-Lighthouse-01.jpg（commons-search）〈燈塔全貌〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Hengchun-Township Taiwan Eluanbi-Lighthouse-02.jpg（commons-search）〈塔身特寫〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Hengchun-Township Taiwan Eluanbi-Lighthouse-03.jpg（commons-search）〈塔影側身〉
- E：INVALID（銅器器物）— File:Hengchun-Township Taiwan CHERUB-Ship-Log-01.jpg
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:Hengchun-Township Taiwan Eluanbi-Lighthouse-04.jpg（commons-search）〈白舍拱窗〉

### tw-030 屏東關山 — v3 **4.0**（v2: new，視覺 3.25，認證 4，社群 +0）
- 認證依據：墾丁國家公園域內（關山夕照）
- 合成：視覺3.25＋認證校正0.75＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [6, 6, 7, 6] 均分 6.25 — File:墾丁國家公園關山夕照.jpg（commons-search）〈紫調夜眺（重濾鏡）〉
- B：INVALID（過曝雕像）— File:GuanshanRock.JPG
- C：子項 [7, 7, 6, 7] 均分 6.75 — File:View northwest to the Hengchun Western Plateau from Guanshan Lookout.jpg（commons-search）〈半島海岸鳥瞰〉
- D：INVALID（街景）— File:Taiwan Main Road 3 Tail.jpg
- E：INVALID（建築主體）— File:屏東縣屏東市公所大樓 2011-03-20.jpg
- F：INVALID（街景）— File:Pingtung city.jpg

### tw-031 抹茶山 — v3 **3.0**（v2: new，視覺 3.12，認證 3，社群 +0）
- 認證依據：抹茶山（聖母山莊）——攝影攻略一致推薦，無官方認證
- 合成：視覺3.12＋認證校正-0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [6, 5, 5, 6] 均分 5.5 — File:三角崙山 Sanjiaolun Mountain - panoramio.jpg（commons-search）〈樹拱步道口〉
- B：子項 [8, 7, 6, 7] 均分 7.0 — File:Yangmingshan National Park Rogner 1.jpg（commons-search）〈抹茶山草原〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Yangmingshan National Park Rogner 2.png（commons-search）〈稜線草原〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Big white cloud over Mt. Sanjiaolun in the morning on 4 June 2020.jpg（commons-search）〈草嶺步道〉
- E：子項 [7, 6, 5, 6] 均分 6.0 — File:Match Mountain.jpg（commons-search）〈山巒層雲〉
- F：INVALID（攤車非風景）— File:SZ 深圳 Shenzhen 龍華 Longhua 紅山6979 Hongshan zone mall 夜市 night market shop 抹茶實驗室 October 2024 R12S.jpg

### tw-032 見晴懷古步道 — v3 **4.0**（v2: new，視覺 3.5，認證 4，社群 +0）
- 認證依據：太平山國家森林遊樂區（見晴懷古步道）
- 合成：視覺3.5＋認證校正0.5＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：子項 [7, 7, 7, 7] 均分 7.0 — File:Classicu 2023-10-01 153028.481.jpg（commons-search）〈霧中苔鐵道〉
- B：INVALID（非本景涼亭）— File:Gazebo in Central Botanical Garden of the National Academy of Sciences of Belarus.jpg
- C：INVALID（涼亭設施）— File:Wooden Gazebo, Holy Wells Park, Ipswich.jpg
- D：INVALID（異地建築）— File:Tallinn asv2022-04 img24 Kadriorg Park.jpg
- E：INVALID（異地建築）— File:Scuol Vulpera, Unterengadin, Graubünden. 21-09-2023. (actm.) 51.jpg
- F：INVALID（解說牌）— File:Gazebo plaque 2096.jpg

### tw-033 粉鳥林 — v3 **3.0**（v2: new，視覺 2.88，認證 3，社群 +0）
- 認證依據：粉鳥林——攝影攻略一致推薦（秘境海灣），無官方認證
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:粉鳥林漁港 Fenniaolin Fishing Harbor - panoramio.jpg（commons-search）〈藍舟漁港〉
- B：INVALID（漁具器物特寫）— File:粉鳥林漁港 Fenniaolin Fishing Harbour - panoramio.jpg
- C：INVALID（廢棄車輛）— File:Fenniaolin 粉鳥林 - panoramio.jpg
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:Fenniaolin Fishing Harbor 粉鳥林漁港 - panoramio.jpg（commons-search）〈老漁船景〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:2021 Fenniaolin Fishing Port ii.jpg（commons-search）〈港堤遠望〉
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:2021 Fenniaolin Fishing Port.jpg（commons-search）〈峽灣港灣〉

### tw-037 多良火車站觀景台 — v3 **3.0**（v2: new，視覺 3.38，認證 3，社群 +0）
- 認證依據：多良車站——攝影攻略一致推薦（最美車站），無官方認證
- 合成：視覺3.38＋認證校正-0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:TRA Duoliang Station 02.jpg（commons-search）〈鐵道海崖經典〉
- B：子項 [8, 7, 6, 8] 均分 7.25 — File:Duoliang Railway Station 多良車站 - panoramio (1).jpg（commons-search）〈紅色列車過彎〉
- C：INVALID（廢棄房舍）— File:Abandoned Duoliang Station 多良廢棄車站 - panoramio.jpg
- D：INVALID（廢棄房舍）— File:Abandoned Duoliang Station 多良車站廢棄房舍 - panoramio.jpg
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Duoliang Station approach.jpg（commons-search）〈隧道口鐵道〉
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:Overlooking the ocean at Duoliang Train Station.jpg（commons-search）〈海線鐵道藍天〉

### tw-039 池上伯朗大道 — v3 **3.0**（v2: new，視覺 3.0，認證 3，社群 +0）
- 認證依據：伯朗大道——攝影攻略一致推薦，無官方認證
- 合成：視覺3.0＋認證校正0.0＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [7, 7, 6, 7] 均分 6.75 — File:The Brown Boulevard Chishang Taitung.jpg（commons-search）〈稻路雲海〉
- B：子項 [7, 6, 7, 7] 均分 6.75 — File:Country Road To Mountain (241078067).jpeg（commons-search）〈田埂落日〉
- C：子項 [7, 6, 5, 6] 均分 6.0 — File:Mr. Brown Avenue, Chishang.jpg（commons-search）〈金城武樹〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:金城武樹 (14545001530).jpg（commons-search）〈稻浪單車〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:29-伯朗大道 (28896712393).jpg（commons-search）〈天堂路樹影〉
- F：INVALID（石碑主體）— File:2023-09-13 Mr. Brown Avenue.jpg

### tw-042 雪山北峰 — v3 **4.0**（v2: new，視覺 3.12，認證 4，社群 +0）
- 認證依據：雪霸國家公園域內（雪山北峰）
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:HsuehMountainNorthenPeak.jpg（commons-search）〈綠稜岩峰〉
- B：INVALID（拓印碑帖）— File:CADAL09011313 揅經室詩錄.djvu
- C：子項 [8, 7, 6, 7] 均分 7.0 — File:Mount Shaolai viewed from Mount Yuanzui.jpg（commons-search）〈碎石坡雲〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:17817 登山者的水管路.jpg（commons-search）〈稜線雲霧〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:HsuehMountain.jpg（commons-search）〈山屋稜線〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:雪山主峰南側山坡的玉山圓柏白木林.jpg（commons-search）〈白木芒草〉

### tw-045 嘉明湖 — v3 **4.0**（v2: new，視覺 3.88，認證 4，社群 +0）
- 認證依據：玉山國家公園域內南二段（嘉明湖）
- 合成：視覺3.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [9, 8, 7, 8] 均分 8.0 — File:Jiaming lake.jpg（commons-search）〈嘉明湖金秋〉
- B：INVALID（山屋建築）— File:Jiaming Lake Shelter from above.jpg
- C：子項 [8, 7, 8, 7] 均分 7.5 — File:Sunrise in Jiaming Lake, Yushan National Park.jpg（commons-search）〈日落雲海層山〉
- D：子項 [9, 8, 6, 8] 均分 7.75 — File:Jiaming Lake (229618779).jpeg（commons-search）〈天使淚湖〉
- E：子項 [9, 8, 6, 8] 均分 7.75 — File:JiamingLake jdtien 03.jpg（commons-search）〈橢圓藍湖〉
- F：子項 [9, 8, 6, 8] 均分 7.75 — File:Chiaming Lake 20180718 01 (cropped).jpg（commons-search）〈藍湖草坡〉

### tw-046 大霸尖山 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：雪霸國家公園域內（大霸尖山）
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 6, 8] 均分 7.75 — File:DabajianMountain.jpg（commons-search）〈大霸經典〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:DabajianANDXiaobajianMountains.jpg（commons-search）〈稜線岩峰〉
- C：子項 [9, 8, 7, 8] 均分 8.0 — File:Mt Dabajian-winter view.jpg（commons-search）〈積雪霸群〉
- D：子項 [8, 7, 5, 7] 均分 6.75 — File:Dabajian Mountain AFA 8102.jpg（commons-search）〈霸基巨岩〉
- E：子項 [9, 8, 7, 8] 均分 8.0 — File:大小霸.jpg（commons-search）〈大霸雲海〉
- F：子項 [8, 7, 5, 7] 均分 6.75 — File:Shei-Pa National Park+cwtu+003.jpg（commons-search）〈松岩對望〉

### tw-047 北大武山 — v3 **4.0**（v2: new，視覺 3.06，認證 4，社群 +0）
- 認證依據：北大武山＝台灣五岳（南台首嶽）岳界選定＋百岳
- 合成：視覺3.06＋認證校正0.94＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [7, 6, 6, 7] 均分 6.5 — File:台灣北大武山之一.jpg（commons-search）〈雲海枯枝〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:鳥瞰神秘谷陰陽瀑布 - panoramio.jpg（commons-search）〈深谷綠林〉
- C：子項 [6, 5, 6, 6] 均分 5.75 — File:中央山脈陷落區以南的群峰.jpg（commons-search）〈晨昏山巒〉
- D：子項 [8, 7, 6, 7] 均分 7.0 — File:Dawu Mt+Hunag Chung Yu黃中佑+17755.jpg（commons-search）〈雲瀑山脊〉
- E：INVALID（地點不符（城市））— File:Far view of North Dawu Mountain from Kaohsiung.jpg
- F：INVALID（人物主體）— File:2007-05-12 collecting trash in North Dawu Mountain.jpg

### tw-048 池有山 — v3 **4.0**（v2: new，視覺 3.06，認證 4，社群 +0）
- 認證依據：雪霸國家公園域內（池有山）
- 合成：視覺3.06＋認證校正0.94＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:ChiYouMountain.jpg（commons-search）〈綠峰紮營〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — File:新達山屋早晨 - panoramio.jpg（commons-search）〈燒霞尖峰〉
- C：INVALID（書頁文獻）— File:雙池文集(一).djvu
- D：INVALID（書頁文獻）— File:雙池文集(四).djvu
- E：INVALID（書頁文獻）— File:雙池文集(八).djvu
- F：INVALID（書頁文獻）— File:CADAL06200567 古本小說集成：鳳凰池.djvu

### tw-049 桃山 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：雪霸國家公園域內（桃山）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:River Cijiawan.jpg（commons-search）〈碧綠溪澗〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:TaoMountain.jpg（commons-search）〈桃山紅屋〉
- C：INVALID（繪畫非照片）— File:Cordelia Wilson - Taos Mountain Trail Home.jpg
- D：INVALID（廟簷建築）— File:Tao-shan-kuan.jpg
- E：INVALID（白牆非風景）— File:Foochow wall in tao-shan-kuan.jpg
- F：INVALID（地點不符（油井））— File:Vung Tao Oil Field.jpg

### tw-050 品田山 — v3 **4.0**（v2: new，視覺 3.44，認證 4，社群 +0）
- 認證依據：雪霸國家公園域內（品田山）
- 合成：視覺3.44＋認證校正0.56＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 5, 8] 均分 7.5 — File:PintienMountain.jpg（commons-search）〈品田褶皺斷崖〉
- B：子項 [8, 7, 5, 7] 均分 6.75 — File:PintienMountain2.jpg（commons-search）〈品田尖峰〉
- C：子項 [8, 7, 5, 7] 均分 6.75 — File:Pintianshan trail.jpg（commons-search）〈松岩對峙〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:424, Taiwan, 台中市和平區平等里 - panoramio.jpg（commons-search）〈褐峰草坡〉
- E：子項 [8, 7, 6, 7] 均分 7.0 — File:品田山 - panoramio.jpg（commons-search）〈積雪峰雲霧〉
- F：子項 [8, 7, 6, 7] 均分 7.0 — File:遠望品田山 - panoramio.jpg（commons-search）〈雪峰霧湧〉

### tw-051 大古山 — v3 **3.0**（v2: new，視覺 2.38，認證 3，社群 +0）
- 認證依據：大古山眺望平台——攝影攻略常見（機場夜景），無官方認證
- 合成：視覺2.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:蘆竹區大古山步道遠眺桃園機場2017.jpg（commons-search）〈機場平原遠眺〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:蘆竹區大古山步道福山宮前遠眺2017.jpg（commons-search）〈觀景台視野〉
- C：子項 [4, 4, 3, 4] 均分 3.75 — File:蘆竹區大古山步道遠眺桃園機場2017B.jpg（commons-search）〈港區鳥瞰〉
- D：子項 [6, 5, 7, 6] 均分 6.0 — File:Grand-Coulee-PB110070.JPG（commons-search）〈夕日光軌〉
- E：INVALID（地點不符（河谷））— File:Grand coulee below dry falls.JPG
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Grand Coulee aerial 01.jpg（commons-search）〈山巒層疊〉

### tw-052 小崗山雲臺 — v3 **2.0**（v2: new，視覺 3.0，認證 2，社群 +0）
- 認證依據：小崗山雲臺＝地方觀景平台，無景觀認證
- 合成：視覺3.0＋認證校正-1＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 11 張，有效 1 張
- A：子項 [6, 6, 6, 6] 均分 6.0 — File:Siaogangshan Skywalk Park 岡山之眼全景.jpg（commons-search-topup）〈港區夕照遠眺〉
- B：INVALID（書冊文獻）— File:CADAL06200655 古本小說集成：瓦崗寨演義.djvu
- C：INVALID（書冊文獻）— File:CADAL07003840 小先生制.djvu
- D：INVALID（地點待疑（一線天））— File:田寮月世界 小滾水泥火山 月世界泥火山 大崗山 朝元寺 石母乳 碧水洞 一線天 情人洞 瘦身洞 (24908834006).jpg
- E：INVALID（器物特寫）— File:Siaogangshan Skywalk Park 20251001.jpg
- F：INVALID（書冊文獻）— File:寶雲詩集(二).djvu
- G：INVALID（非風景代表照）— File:亜東印画輯 01 065 "大連小崗子（大連）".jpg
- H：INVALID（非風景代表照）— File:SZ 深圳 Shenzhen 龍崗 Longgang 禾坪崗村 Hepinggang Cun shop 江小長沙碗仔餸飯食店 Jiangxiao Changsha Steamed Rice Restaurant October 2023 R12S 03 fired yellow bean.jpg
- I：INVALID（非風景代表照）— File:SZ 深圳 Shenzhen 龍崗 Longgang 禾坪崗村 Hepinggang Cun shop 江小長沙碗仔餸飯食店 Jiangxiao Changsha Steamed Rice Restaurant October 2023 R12S food green tray.jpg
- J：INVALID（非風景代表照）— File:SZ 深圳 Shenzhen 龍崗 Longgang 禾坪崗村 Hepinggang Cun shop 江小長沙碗仔餸飯食店 Jiangxiao Changsha Steamed Rice Restaurant October 2023 R12S food counter.jpg
- K：INVALID（非風景代表照）— File:SZ 深圳 Shenzhen 龍崗 Longgang 禾坪崗村 Hepinggang Cun shop 江小長沙碗仔餸飯食店 Jiangxiao Changsha Steamed Rice Restaurant October 2023 R12S 08 egg minced pork.jpg

### tw-053 杉林溪 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：杉林溪森林生態渡假園區（官方劃設森林遊樂區）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [6, 5, 6, 6] 均分 5.75 — File:Haltern am See, Stausee, Anleger -- 2016 -- 2859.jpg（commons-search）〈鎖鏈逆光〉
- B：INVALID（園區大門）— File:杉林溪 Sun-Link-Sea Forest and Nature Resort - panoramio.jpg
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:SunLinkSea 杉林溪 - panoramio.jpg（commons-search）〈杉林花旗〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:杉林溪 SunLinkSea - panoramio.jpg（commons-search）〈紅橋杉影〉
- E：子項 [7, 6, 5, 6] 均分 6.0 — File:Shanlinxi Forest Road 杉林溪林道 - panoramio.jpg（commons-search）〈杉林步道〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Shanlinxi Forest Road 杉林溪林道 - panoramio (1).jpg（commons-search）〈杉林車道〉

### tw-054 正濱漁港 — v3 **3.0**（v2: new，視覺 3.62，認證 3，社群 +0）
- 認證依據：正濱漁港彩色屋——攝影攻略一致推薦，無官方景觀認證
- 合成：視覺3.62＋認證校正-0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [6, 6, 6, 6] 均分 6.0 — File:2020 Zhengbin Fishing Port b.jpg（commons-search）〈碼頭暮色剪影〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:2020 Zhengbin Fishing Port a.jpg（commons-search）〈漁船鏽殼〉
- C：子項 [9, 8, 7, 8] 均分 8.0 — File:Zhengbin Fishing Port 正濱漁港.jpg（commons-search）〈彩色屋經典〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:Zhengbin Fishing Port (20250302174308).jpg（commons-search）〈彩屋跨橋〉
- E：子項 [8, 7, 6, 8] 均分 7.25 — File:Zhengbin Fishing Port (20250302144830).jpg（commons-search）〈彩屋港灣〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Zhengbin Fishing Harbor 正濱漁港 - panoramio.jpg（commons-search）〈彩屋綠堤〉

### tw-055 五峰旗瀑布 — v3 **3.0**（v2: new，視覺 2.88，認證 3，社群 +0）
- 認證依據：五峰旗瀑布＝宜蘭縣級風景特定區（非國家級）
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Wufengchi.JPG（commons-search）〈五峰旗瀑〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Wufongci falls middle.JPG（commons-search）〈瀑畔涼亭〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Wufengqi Falls Taiwan.jpeg（commons-search）〈長曝水簾〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Yilan Wufengqi Waterfall-宜蘭-五峰旗瀑布.jpg（commons-search）〈三層疊瀑〉
- E：子項 [6, 5, 5, 6] 均分 5.5 — File:Wufengqi Second Fall-yilan-20260926.jpg（commons-search）〈瀑下戲水〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Wufengqi First Fall-yilan-20260926.jpg（commons-search）〈溪畔綠蔭〉

### tw-056 松蘿湖 — v3 **3.0**（v2: new，視覺 3.0，認證 3，社群 +0）
- 認證依據：松蘿湖——攝影攻略一致推薦（秘境湖泊），無官方認證
- 合成：視覺3.0＋認證校正0.0＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [7, 7, 6, 7] 均分 6.75 — File:Songluo Lake 20170611.jpg（commons-search）〈松蘿湖鏡面〉
- B：子項 [6, 6, 6, 6] 均分 6.0 — File:Camping on the bank of Songluo Lake in early morning.jpg（commons-search）〈林隙天光〉
- C：子項 [7, 6, 6, 7] 均分 6.5 — File:SongLuo Lake, Ivan Tsung-Yi Lin, 005.jpg（commons-search）〈山區眺湖〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:SongLuo Lake, Ivan Tsung-Yi Lin, 004.jpg（commons-search）〈層疊雲山〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:SongLuo Lake, Ivan Tsung-Yi Lin, 006.jpg（commons-search）〈幽暗湖影〉
- F：INVALID（器物待疑）— File:Hapen WSY 02.jpg

### tw-057 加羅湖 — v3 **3.0**（v2: new，視覺 2.88，認證 3，社群 +0）
- 認證依據：加羅湖——攝影攻略一致推薦（秘境湖泊），無官方認證
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Collapse on the road to Jialuo Lake.jpg（commons-search）〈山徑崩壁〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:喔走48小時 第五季成員登加羅湖.jpg（commons-search）〈湖畔營帳〉
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Lago Rogaguado.jpg（commons-search）〈水杉列〉
- D：子項 [7, 6, 6, 7] 均分 6.5 — File:Palmar de Coquinal.jpg（commons-search）〈棕櫚夕照〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Palmares.jpg（commons-search）〈林間湖畔〉
- F：INVALID（文獻碑帖）— File:CADAL09007295 羅湖野錄.djvu

### tw-058 澎湖跨海大橋 — v3 **3.0**（v2: new，視覺 2.88，認證 3，社群 +0）
- 認證依據：澎湖跨海大橋——地標設施；澎湖國家風景區域內但橋體本身無景觀認證
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Penghu CrossSeeBridge.jpg（commons-search）〈白拱跨海〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Penghu Great Bridge 20150619.jpg（commons-search）〈橋拱牌樓〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Penghu Great Bridge over the Houmen Channel.jpg（commons-search）〈港灣海堤〉
- D：INVALID（建築非橋景）— File:Penghu Great Bridge 2021 02.jpg
- E：INVALID（碑文）— File:Penghu Great Bridge 石碑 02.jpg
- F：INVALID（碑文）— File:Penghu Great Bridge 石碑 03.jpg

### tw-059 奎壁山 — v3 **3.0**（v2: new，視覺 2.44，認證 3，社群 +0）
- 認證依據：澎湖國家風景區（官方）但無特級認證；摩西分海為攝影攻略常客
- 合成：視覺2.44＋認證校正0.56＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：INVALID（非風景代表照）— File:奎壁山 20260925.jpg
- B：子項 [7, 6, 5, 6] 均分 None — File:奎壁山摩西分海 20260925.jpg（None）
- C：子項 [5, 4, 3, 3] 均分 None — File:奎壁山踏浪 03.jpg（None）

### tw-061 澎湖觀音亭 — v3 **3.0**（v2: new，視覺 2.38，認證 3，社群 +0）
- 認證依據：觀音亭夕照——攝影攻略一致推薦，無官方認證
- 合成：視覺2.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：INVALID（拼貼合成）— File:Penghu County Montage.png
- B：子項 [8, 7, 8, 7] 均分 7.5 — File:澎湖馬公海邊夕陽-3.jpg（commons-search）〈觀音亭夕照〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:澎湖馬公咕咾石牆.jpg（commons-search）〈咾咕石牆〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:澎湖七美嶼大獅龍程風景區道路.jpg（commons-search）〈鄉道海景〉
- E：INVALID（牆面特寫）— File:澎湖馬公碼頭民宅-2.jpg
- F：INVALID（器物特寫）— File:澎湖馬公碼頭民宅-1.jpg

### tw-062 金門得月樓 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：金門國家公園域內＋國定古蹟（得月樓）
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:金門水頭得月樓.jpg（commons-search）〈得月樓經典〉
- B：INVALID（解說牌）— File:得月樓 Deyue House - panoramio.jpg
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:Deyue Tower 得月樓 - panoramio.jpg（commons-search）〈樓院草坪〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:水头得月楼 - Deyue Tower in Shuitou Settlement - 2014.05 - panoramio.jpg（commons-search）〈槍樓洋樓〉
- E：INVALID（牆面特寫）— File:Kinmen National Park Yenping Lee 010.jpg
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:金門金沙洋摟.jpg（commons-search）〈樓鄰閩宅〉

### tw-064 金門慈湖 — v3 **3.38**（v2: new，視覺 2.38，認證 4，社群 +0）
- 認證依據：金門國家公園域內（慈湖）
- 合成：視覺2.38＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Road northbound carriageway looking towards the dike of Cihu Lake.jpg（commons-search）〈慈湖堤道〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:Road southbound carriageway looking towards the dike of Cihu Lake.jpg（commons-search）〈長堤延伸〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:金門慈湖.jpg（commons-search）〈湖灣水色〉
- D：子項 [7, 6, 7, 6] 均分 6.5 — File:慈湖.jpg（commons-search）〈沙灘燒霞〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:慈湖观海平台 - Cihu Sea View Terrace - 2014.05 - panoramio.jpg（commons-search）〈觀景平台〉
- F：子項 [6, 6, 6, 6] 均分 6.0 — File:慈湖落日 - Sunset on Cihu Coast - 2015.01 - panoramio.jpg（commons-search）〈暮紅潮灘〉

### tw-065 馬祖南竿 — v3 **3.0**（v2: new，視覺 2.88，認證 3，社群 +0）
- 認證依據：馬祖國家風景區（官方）南竿綜合景點，無特級認證
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 3 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:南竿牛角村 Nangan Niujiao Village - panoramio.jpg（commons-search-topup）〈山城聚落俯瞰〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Nangan Furen Cafe 南竿夫人咖啡 - panoramio.jpg（commons-search-topup）〈綠灣水道〉
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Nangan Tieban Village 南竿鐵板村 - panoramio.jpg（commons-search-topup）〈岩岸海灣〉
- D：INVALID（碑塔主體）— File:南竿馬祖劍碑.jpg
- E：INVALID（紅色歷史照）— File:Zhongzheng Rd., Nangan Township, Matsu.jpg
- F：INVALID（機場設施）— File:Matsu Nangan Airport 20250912.jpg
- G：INVALID（非風景代表照）— File:Matsu Distillery, Nangan, Matsu, Taiwan.JPG
- H：INVALID（非風景代表照）— File:Nangan Airport, Nangan, Matsu, Taiwan.JPG
- I：INVALID（非風景代表照）— File:Matsu Nangan Airport 馬祖南竿機場 - panoramio.jpg
- J：INVALID（非風景代表照）— File:Matsu Nangan Airport 馬祖南竿機場.jpg
- K：INVALID（非風景代表照）— File:Matsu Nangan Airport 2024-09-10.jpg
- L：INVALID（非風景代表照）— File:Mandarin Airlines B-16863 at Matsu Nangan Airport.jpg

### tw-066 東引燈塔 — v3 **4.0**（v2: new，視覺 3.0，認證 4，社群 +0）
- 認證依據：東引燈塔＝國定古蹟＋馬祖國家風景區
- 合成：視覺3.0＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Tungyin Tao Lighthouse.jpg（commons-search）〈東引白牆燈塔〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:东引灯塔公路 - Road towards Dongyin Lighthouse - 2016.04 - panoramio.jpg（commons-search）〈海岬步道〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:东引灯塔步道 - Dongyin Lighthouse Trail - 2016.04 - panoramio.jpg（commons-search）〈石階山徑〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:东引灯塔 - Dongyin Lighthouse - 2016.04 - panoramio.jpg（commons-search）〈塔影草坡〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:东引灯塔步道 - Dongyin Lighthouse Trail - 2016.04 - panoramio (1).jpg（commons-search）〈岩岬小徑〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:东引灯塔 - Dongyin Lighthouse - 2016.04 - panoramio (1).jpg（commons-search）〈燈塔全貌〉

### tw-067 北竿芹壁 — v3 **4.0**（v2: new，視覺 3.0，認證 4，社群 +0）
- 認證依據：馬祖國家風景區旗艦聚落（芹壁保存區）
- 合成：視覺3.0＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Qinbi Village 001, Beigan, Matsu, Taiwan.JPG（commons-search）〈芹壁石屋群〉
- B：子項 [7, 6, 5, 6] 均分 6.0 — File:北竿芹壁村 Beigan Qinbi Village - panoramio.jpg（commons-search）〈石屋菜園〉
- C：子項 [7, 6, 5, 6] 均分 6.0 — File:Beigan Qinbi Village 北竿芹壁村 - panoramio.jpg（commons-search）〈海灣花叢〉
- D：子項 [7, 6, 5, 6] 均分 6.0 — File:芹壁社區發展協會 Qinbi Community Development Association - panoramio.jpg（commons-search）〈石階巷弄〉
- E：INVALID（門窗特寫）— File:芹壁石屋 Qinbi Stone House - panoramio.jpg
- F：INVALID（屋頂特寫）— File:Qinbi 14 芹壁14號 - panoramio.jpg

### tw-068 綠島朝日溫泉 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：東部海岸國家風景區官方；「世界級海底溫泉」為官方用語（非三大佐證）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [8, 7, 8, 6] 均分 None — File:朝日溫泉.jpg（None）
- B：子項 [6, 5, 3, 4] 均分 None — File:Zhaori Hot Springs.jpg（None）
- C：子項 [6, 7, 4, 6] 均分 None — File:Zhaori Hot Springs 20150128.jpg（None）

### tw-069 蘭嶼東清灣 — v3 **4.0**（v2: new，視覺 3.19，認證 4，社群 +0）
- 認證依據：東部海岸國家風景區域內（蘭嶼東清灣）
- 合成：視覺3.19＋認證校正0.81＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:View at Dongqing Bay, Orchid Island 20100911.jpg（commons-search）〈礫灘礁群〉
- B：子項 [8, 7, 6, 8] 均分 7.25 — File:View at Dongqing Bay, Orchid Island 20100911 01.jpg（commons-search）〈礁岩海灣〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:View at Dongqing Bay, Orchid Island 20100911 04.jpg（commons-search）〈群礁湛藍〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:View at Dongqing Bay, Orchid Island 20100911 02.jpg（commons-search）〈潮池反光〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:View at Dongqing Bay, Orchid Island 20100911 03.jpg（commons-search）〈礁原浪湧〉
- F：子項 [7, 6, 7, 6] 均分 6.5 — File:Dongqing Bay at night 20100912.jpg（commons-search）〈夜光礁池〉

### tw-070 蘭嶼青青草原 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：東部海岸國家風景區域內（蘭嶼青青草原）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：INVALID（山羊群主體）— File:Goats at Orchid Island 20100915.jpg
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Langdao.JPG（commons-search）〈礫灘弧灣〉
- C：INVALID（地點不符（枯樹潭））— File:蘭嶼 天池 - panoramio.jpg
- D：INVALID（閘門設施）— File:蘭嶼電廠.jpg
- E：INVALID（渡輪主體）— File:蘭嶼機場.jpg
- F：INVALID（地圖）— File:Txu-pclmaps-oclc-6550512-koto-sho-2413-iii.jpg

### tw-071 小琉球花瓶岩 — v3 **unknown**（v2: new，視覺 None，認證 4，社群 +0）
- 認證依據：大鵬灣國家風景區域內（小琉球花瓶岩）
- 合成：unknown：無有效代表照片（有認證但無視覺信號，不虛構分數）；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 0 張
- A：INVALID（書頁文獻）— File:CADAL09010580 小滄浪筆談·二.djvu
- B：INVALID（書頁文獻）— File:CADAL09011767 夏小正箋.djvu
- C：INVALID（書頁文獻）— File:CADAL09013558 小市民.djvu
- D：INVALID（書頁文獻）— File:CADAL11103827 袁小修詩集.djvu
- E：INVALID（書頁文獻）— File:CADAL11106212 苗荒小紀.djvu
- F：INVALID（衛星影像）— File:EO1 ALI Lamay Island.jpg
- G：INVALID（非風景代表照）— File:小琉球遊客中心.jpg
- H：INVALID（非風景代表照）— File:小琉球瓦厝內正門.jpg
- I：INVALID（非風景代表照）— File:小琉球五連宮.jpg
- J：INVALID（非風景代表照）— File:小琉球碧雲寺.jpg
- K：INVALID（非風景代表照）— File:小琉球碧雲寺正立面.jpg
- L：INVALID（非風景代表照）— File:CADAL11200469 功甫小集.djvu

### tw-072 南雅奇岩 — v3 **4.0**（v2: new，視覺 3.5，認證 4，社群 +0）
- 認證依據：東北角暨宜蘭國家風景區域內（南雅奇岩）
- 合成：視覺3.5＋認證校正0.5＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:224, Taiwan, 新北市瑞芳區南雅里 - panoramio (9).jpg（commons-search）〈南雅奇岩浪〉
- B：INVALID（歷史肖像畫）— File:The Imperial Durbar Album of the Indian princes, chiefs and zamindars.djvu
- C：INVALID（車內後視鏡）— File:新北-南雅奇岩 (30754132415).jpg
- D：子項 [8, 7, 5, 8] 均分 7.0 — File:新北-南雅奇岩 (30118507293).jpg（commons-search）〈風化紋岩〉
- E：INVALID（解說牌主體）— File:新北-南雅奇岩 (30754128715).jpg
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:新北-南雅奇岩 (30118506293).jpg（commons-search）〈步道望奇岩〉

### tw-073 老梅綠石槽 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：北海岸及觀音山國家風景區域內（老梅綠石槽）
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Wongwt 老梅石槽 (17203248716).jpg（commons-search）〈綠石槽溝紋〉
- B：子項 [8, 7, 6, 8] 均分 7.25 — File:老梅綠石槽 Laomei Algal Reef - panoramio.jpg（commons-search）〈石槽苔綠〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:Laomei Algal Reef 老梅綠石槽 - panoramio.jpg（commons-search）〈綠潮石槽〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Laomei Algal Reef 老梅石槽 - panoramio.jpg（commons-search）〈暗槽溝列〉
- E：子項 [8, 7, 6, 8] 均分 7.25 — File:Stone trench of Laomei, Taiwan; April 2016 (01).jpg（commons-search）〈浪拍石槽〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:202605 A large tire on Laomei Green Reef 01.jpg（commons-search）〈稀疏綠槽〉

### tw-074 野柳地質公園 — v3 **4.0**（v2: new，視覺 3.38，認證 4，社群 +0）
- 認證依據：北海岸及觀音山國家風景區（野柳地質公園旗艦景點）
- 合成：視覺3.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：wiki-en, wiki-zh；抓到 6 張，有效 6 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:Fairy Sandal.JPG（wiki-zh）〈海龜岩〉
- B：子項 [9, 8, 6, 9] 均分 8.0 — File:Taiwan wanli queenshead altonthompson.jpg（wiki-en）〈女王頭經典〉
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Keelung Island 001.JPG（wiki-zh）〈基隆嶼遠望〉
- D：子項 [8, 7, 5, 7] 均分 6.75 — File:20190415 Yehliu geopark rock formations-1.jpg（wiki-en）〈蕈狀岩群〉
- E：子項 [9, 8, 7, 8] 均分 8.0 — File:Yehliu Cape 20041113.jpg（wiki-zh）〈女王頭夕照〉
- F：子項 [8, 7, 5, 7] 均分 6.75 — File:Yehliu - Mushroom Rock 02.jpg（wiki-zh）〈蕈狀岩陣〉

### tw-075 外澳沙灘／龜山朝日 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：東北角暨宜蘭國家風景區域內（外澳）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Wai-ao.JPG（commons-search）〈衝浪人潮〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:外澳海水浴場 Waiao Beach - panoramio.jpg（commons-search）〈沙灘浪線〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Distant View of Lailai Cape 萊萊鼻遠眺 - panoramio.jpg（commons-search）〈藍海衝浪〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:外澳海水浴場 Waiao Beach - panoramio (1).jpg（commons-search）〈浪花人群〉
- E：子項 [7, 6, 6, 7] 均分 6.5 — File:Waiao Beach 外澳海灘 - panoramio.jpg（commons-search）〈龜山黑沙灘〉
- F：INVALID（過曝夕照）— File:Double lions gold.jpg

### tw-077 石梯坪海蝕平台／壺穴群 — v3 **3.69**（v2: new，視覺 2.69，認證 4，社群 +0）
- 認證依據：東部海岸國家風景區域內（石梯坪）
- 合成：視覺2.69＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（停車場山景）— File:石梯坪 Shitiping - panoramio.jpg
- B：子項 [6, 6, 6, 6] 均分 6.0 — File:石梯坪海景.jpg（commons-search）〈日落海岸〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:石梯嶺步道.jpg（commons-search）〈草坡小徑〉
- D：INVALID（室內展示）— File:卑南文化岩雕石梯.jpg
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:石梯坪的慈中學生.jpg（commons-search）〈礫灘遊客〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:石梯坪蕈狀壺穴.jpg（commons-search）〈潮池壺穴〉

### tw-078 建功嶼／退潮石板道 — v3 **3.62**（v2: new，視覺 2.62，認證 4，社群 +0）
- 認證依據：金門國家公園域內
- 合成：視覺2.62＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [6, 6, 5, 6] 均分 None — File:建功屿步道 - Footpath to Jiangong Islet - 2014.09 - panoramio.jpg（None）
- B：子項 [6, 6, 4, 3] 均分 None — File:Jiangong Yu YuTK 01.jpg（None）
- C：INVALID（非風景代表照）— File:Jiangong Islet notice board.jpg

### tw-079 池西柱狀玄武岩／池西岩瀑九孔池 — v3 **4.0**（v2: new，視覺 3.5，認證 4，社群 +0）
- 認證依據：澎湖國家風景區域內（池西岩瀑柱狀玄武岩）
- 合成：視覺3.5＋認證校正0.5＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 4 張，有效 4 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:0429 池西岩瀑 (4).jpg（commons-search）〈玄武岩石滬〉
- B：子項 [8, 7, 5, 7] 均分 6.75 — File:0429 池西岩瀑 (3).jpg（commons-search）〈柱狀岩列〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:0429 池西岩瀑 (8).jpg（commons-search）〈岩瀑潮池〉
- D：子項 [8, 7, 5, 7] 均分 6.75 — File:0429 池西岩瀑 (11).jpg（commons-search）〈岩柱近觀〉

### tw-080 帆船鼻大草原／海岬 — v3 **unknown**（v2: new，視覺 None，認證 4，社群 +0）
- 認證依據：墾丁國家公園域內（帆船鼻大草原）
- 合成：unknown：無有效代表照片（有認證但無視覺信號，不虛構分數）；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 7 張，有效 0 張
- A：INVALID（地點待疑（孤岩灘））— File:Syu-Hai(WDPA-555594034)-PeterWen-17.jpg
- B：INVALID（船隻）— File:Sailing ship Zuiderzee in Bremerhaven.jpg
- C：INVALID（船隻）— File:Shtandart (ship, 1999), Sète cf02.jpg
- D：INVALID（明信片船隻）— File:Corinth canal tugged sailing ship.jpg
- E：INVALID（異地冰海船）— File:Sailing vessel Rembrandt van Rijn.jpg
- F：INVALID（器物特寫）— File:Scratched drawing of a sailing ship 3000 BC.jpg
- G：INVALID（非風景代表照）— File:Beacon Stawa Młyny, Świnoujście.jpg

### tw-085 南子吝步道 — v3 **unknown**（v2: new，視覺 None，認證 3，社群 +0）
- 認證依據：南子吝步道——攝影攻略一致推薦，官方風景區認定佐證不足
- 合成：unknown：無有效代表照片（有認證但無視覺信號，不虛構分數）；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 6 張，有效 0 張
- A：INVALID（書頁文獻）— File:周禮正義(二十九).djvu
- B：INVALID（書頁文獻）— File:唐書合鈔(一百十二).djvu
- C：INVALID（書頁文獻）— File:CADAL06210418 學津討原：第七集凡八冊：七.djvu
- D：INVALID（書頁文獻）— File:CADAL06211444 景文集：四.djvu
- E：INVALID（書頁文獻）— File:CADAL09010693 陶靖節集·（二）.djvu
- F：INVALID（書頁文獻）— File:CADAL09008453 佛國記.djvu

### tw-093 福壽山農場觀景點 — v3 **2.0**（v2: new，視覺 2.38，認證 2，社群 +0）
- 認證依據：福壽山農場＝官方農場（非景觀級認證，大農大富同例）
- 合成：視覺2.38＋認證校正-0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Fushoushan Farm 福壽山農場 - panoramio.jpg（commons-search）〈農舍藍天〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Remote view of the Fushoushan Farm with Xueshan Range in the background.jpg（commons-search）〈層巒千田〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:福壽山農場露營區 Fushoushan Farm campground (01).jpg（commons-search）〈露營草坡〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:福壽山農場露營區 Fushoushan Farm campground (02).jpg（commons-search）〈松林小屋〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:福壽山農場露營區 Fushoushan Farm campground (03).jpg（commons-search）〈農莊小路〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:福壽山農場露營區 Fushoushan Farm campground (04).jpg（commons-search）〈松林野花〉

### us-002 馬蹄灣 — v3 **3.0**（v2: new，視覺 4.0，認證 3，社群 +0）
- 認證依據：馬蹄灣——多方攝影攻略一致推薦，觀景台無官方景觀認證
- 合成：視覺4.0＋認證校正-1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：INVALID（地圖）— File:Horseshoe Bay, British Columbia Location.png
- B：子項 [9, 8, 7, 8] 均分 8.0 — File:Horseshoe Bay Stevage.jpg（commons-search）〈馬蹄灣空拍經典〉
- C：INVALID（地點不符（湖泊宅邸））— File:Horseshoe Bay, 23 mars 2009, 3.jpg
- D：INVALID（異地海蝕洞）— File:Horseshoe Bay IOW.jpg
- E：INVALID（建築主體）— File:Horseshoe Bay Texas City Hall.jpg
- F：INVALID（異地海岸）— File:Horseshoe Bay (Culver Cliff), Isle of Wight, UK.jpg

### us-003 羚羊峽谷 — v3 **5**（v2: new，視覺 4.5，認證 5，社群 +0）
- 認證依據：羚羊峽谷——國際級攝影朝聖地（Navajo 部落公園管轄）
- 合成：視覺4.5＋認證校正0.5＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [10, 9, 10, 9] 均分 None — File:USA Antelope-Canyon.jpg（None）
- B：子項 [10, 9, 9, 8] 均分 None — File:Lower Antelope Canyon 478.jpg（None）
- C：子項 [10, 9, 8, 7] 均分 None — File:Lower Antelope Canyon November 2018 008.jpg（None）

### us-004 紀念碑谷 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：紀念碑谷＝Navajo 部落公園（官方劃設）
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Monument Valley 2.jpg（commons-search）〈梅里克岩枯木〉
- B：子項 [8, 7, 6, 7] 均分 7.0 — File:John Ford's Point Monument Valley Luca Galuzzi 2007.jpg（commons-search）〈騎士剪影〉
- C：子項 [9, 8, 7, 9] 均分 8.25 — File:Oljato-Monument Valley, United States (Unsplash R9S19dOFlcs).jpg（commons-search）〈手套岩暮色〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:00 5891 Monument Valley. - Navajo Indian Reservation.jpg（commons-search）〈馬群岩影〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Forrest Gump Point Monument Valley November 2018 001.jpg（commons-search）〈紀念碑谷公路〉
- F：INVALID（地點待疑（黃土線紋））— File:Monument Valley (ASTER).jpg

### us-008 優勝美地半圓頂 — v3 **5**（v2: new，視覺 4.12，認證 5，社群 +0）
- 認證依據：優勝美地＝UNESCO 世界遺產（Half Dome 為核心景觀）
- 合成：視覺4.12＋認證校正0.88＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 7, 9] 均分 8.25 — File:Glacier Point at Sunset, Yosemite NP, CA, US - Diliff.jpg（commons-search）〈半圓頂冰川點〉
- B：子項 [9, 8, 7, 9] 均分 8.25 — File:Half Dome from Glacier Point, Yosemite NP - Diliff.jpg（commons-search）〈雲漫半圓頂〉
- C：子項 [9, 8, 7, 9] 均分 8.25 — File:Yosemite Half Dome from Valley 2013.jpg（commons-search）〈花崗岩穹〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Girl Posing at Glacier Point Yosemite 2013.jpg（commons-search）〈穹頂攀者〉
- E：子項 [9, 8, 7, 9] 均分 8.25 — File:Half Dome with Eastern Yosemite Valley.jpg（commons-search）〈峰頂望谷〉
- F：子項 [9, 8, 7, 9] 均分 8.25 — File:Half Dome from near Glacier Point.jpg（commons-search）〈松間半圓頂〉

### us-009 優勝美地隧道觀景臺 — v3 **5**（v2: new，視覺 4.5，認證 5，社群 +0）
- 認證依據：優勝美地＝UNESCO 世界遺產（Tunnel View 官方觀景台）
- 合成：視覺4.5＋認證校正0.5＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [10, 9, 8, 10] 均分 9.25 — File:Yosemite Valley from Wawona Tunnel view, vista point.jpg（commons-search）〈隧道觀景經典〉
- B：子項 [10, 9, 8, 9] 均分 9.0 — File:Tunnel View, Yosemite Valley, Yosemite NP - Diliff.jpg（commons-search）〈雲霧優勝美地〉
- C：INVALID（人群主體）— File:YosemiteTunnelView.jpg
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:Tunnel view at Yosemite dllu.jpg（commons-search）〈嵐氣山谷〉
- E：子項 [10, 9, 8, 10] 均分 9.25 — File:“Tunnel View” overlook showing famous rock formations in Yosemite Valley 01.jpg（commons-search）〈全景經典〉
- F：子項 [9, 8, 7, 9] 均分 8.25 — File:“Tunnel View” overlook showing famous rock formations in Yosemite Valley 03.jpg（commons-search）〈谷地層綠〉

### us-015 舊金山金門大橋 — v3 **4.0**（v2: new，視覺 4.0，認證 4，社群 +0）
- 認證依據：金門大橋＝ASCE 現代世界奇觀、國際級工程地標
- 合成：視覺4.0＋認證校正0.0＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 8, 9] 均分 8.5 — File:Golden Gate Bridge by night.jpg（commons-search）〈金門大橋夜色〉
- B：子項 [9, 8, 8, 9] 均分 8.5 — File:Golden Gate Bridge Yang Ming Line.jpg（commons-search）〈霧湧紅橋〉
- C：子項 [8, 7, 8, 8] 均分 7.75 — File:SF Golden Gate Bridge splash CA.jpg（commons-search）〈霧柱浪擊〉
- D：子項 [9, 8, 7, 8] 均分 8.0 — File:Golden Gate Bridge at sunset 1.jpg（commons-search）〈雲上橋影〉
- E：子項 [9, 8, 7, 8] 均分 8.0 — File:The Bridge (August 2013).jpg（commons-search）〈雲海橋塔〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Golden Gate Bridge as seen from Marshall’s Beach, March 2018.jpg（commons-search）〈灘畔紅橋〉

### us-016 拉斯維加斯大道 — v3 **2.0**（v2: new，視覺 2.94，認證 2，社群 +0）
- 認證依據：拉斯維加斯大道＝商業娛樂街區，無景觀認證
- 合成：視覺2.94＋認證校正-0.94＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [6, 6, 6, 6] 均分 6.0 — File:Bellagio Las Vegas December 2013 panorama.jpg（commons-search）〈夜光大道〉
- B：子項 [5, 5, 5, 5] 均分 5.0 — File:Las Vegas (Nevada, USA), The Strip -- 2012 -- 6215.jpg（commons-search）〈金殿棕櫚〉
- C：子項 [6, 6, 6, 6] 均分 6.0 — File:Las Vegas (Nevada, USA), The Strip -- 2012 -- 6232.jpg（commons-search）〈霓虹街景〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Mirage Las Vegas December 2013.jpg（commons-search）〈水舞賭城〉
- E：子項 [6, 6, 6, 6] 均分 6.0 — File:Las Vegas Strip from Resorts World February 2023 HDR 1.jpg（commons-search）〈大道夜流〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:The Strip (2026)-L1000592.jpg（commons-search）〈街區白天〉

### us-017 聖海倫斯火山 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：聖海倫斯國家火山紀念地（USDA 官方 Monument）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [10, 9, 8, 9] 均分 9.0 — File:MSH82 st helens plume from harrys ridge 05-19-82.jpg（commons-search）〈爆發經典〉
- B：子項 [6, 6, 4, 6] 均分 5.5 — File:Mount St. Helens 1985a.jpg（commons-search）〈倒木毀滅帶〉
- C：子項 [5, 5, 3, 5] 均分 4.5 — File:Mount St Helens 1985c.jpg（commons-search）〈灰燼枯林〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Mt St Helens via Worm Flows (18154).jpg（commons-search）〈雪坡殘跡〉
- E：子項 [7, 6, 5, 6] 均分 6.0 — File:Mt St Helens via Worm Flows (32628).jpg（commons-search）〈雪嶺雲道〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Mt St Helens via Worm Flows (99374).jpg（commons-search）〈火山口雪原〉

### us-024 西雅圖太空針塔 — v3 **2.0**（v2: new，視覺 2.62，認證 2，社群 +0）
- 認證依據：太空針塔＝商業地標，無景觀認證
- 合成：視覺2.62＋認證校正-0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:SpaceNeedleTopClose.jpg（commons-search）〈太空針塔〉
- B：INVALID（城市鳥瞰非塔景）— File:Seattle from Space Needle June 2018 003.jpg
- C：INVALID（城市鳥瞰）— File:Seattle from Space Needle June 2018 010.jpg
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Seattle (WA, USA), Space Needle -- 2022 -- 1498.jpg（commons-search）〈針塔街景〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:Seattle (WA, USA), Space Needle -- 2022 -- 1523.jpg（commons-search）〈塔基仰視〉
- F：子項 [5, 5, 4, 5] 均分 4.75 — File:Seattle (WA, USA), Space Needle -- 2022 -- 1524.jpg（commons-search）〈塔身結構〉

### us-025 聖莫尼卡碼頭 — v3 **2.0**（v2: new，視覺 2.88，認證 2，社群 +0）
- 認證依據：聖莫尼卡碼頭＝商業碼頭，無景觀認證
- 合成：視覺2.88＋認證校正-0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：INVALID（黑白歷史照）— File:USA Santa Monica Beach and pier CA.jpg
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Aerial Photo of Santa Monica Pier.jpg（commons-search）〈碼頭空拍〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Los Angeles (California, USA), Santa Monica Beach -- 2012 -- 5301.jpg（commons-search）〈海灘碼頭〉
- D：子項 [6, 6, 6, 6] 均分 6.0 — File:Santa Monica Pier Sunset.jpg（commons-search）〈棕櫚日落〉
- E：INVALID（人群主體）— File:The Lobster restaurant on the Santa Monica Pier.jpg
- F：INVALID（拱門人群）— File:Front of The Lobster Restaurant and the Santa Monica Pier.jpg

### us-026 西雅圖派克市場 — v3 **2.0**（v2: new，視覺 2.38，認證 2，社群 +0）
- 認證依據：派克市場＝商業市集，無景觀認證
- 合成：視覺2.38＋認證校正-0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Pike-place-market.jpg（commons-search）〈市場招牌街景〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:Pike Place Market Seattle.jpg（commons-search）〈農夫市場〉
- C：INVALID（黑白歷史照）— File:Pike Place Market, Economy Market arcade, 1968.jpg
- D：INVALID（室內）— File:Blown Glass for sale in Pike Place Market, Seattle, Washington, 2025.jpg
- E：INVALID（室內）— File:Goods from India for Sale in Pike Place Market, Seattle, Washington.jpg
- F：INVALID（室內）— File:Seattle pigs 03A.jpg

### us-027 鋸齒山脈 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：Sawtooth 國家遊憩區（SNRA，USDA 官方）
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：INVALID（地點待疑（靜水灣））— File:SawtoothMtnsMN2.JPG
- B：子項 [9, 8, 6, 8] 均分 7.75 — File:Sawtooth Mountains and Salmon River.JPG（commons-search）〈鋸齒群峰曲流〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Sawtooth Valley ID1.jpg（commons-search）〈金楊遠峰〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:Sawtooth from Stanley Lake Creek.JPG（commons-search）〈草甸鋸齒山〉
- E：子項 [9, 8, 6, 8] 均分 7.75 — File:Sawtooth mtns.JPG（commons-search）〈尖峰犬牙〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Sawtooth Range MN.jpg（commons-search）〈秋色山丘〉

### us-028 洛杉磯格里斐斯天文台 — v3 **3.0**（v2: new，視覺 2.88，認證 3，社群 +0）
- 認證依據：格里斐斯天文台——攝影攻略一致推薦（LA 夜景），市立無國家認證
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:Griffith Observatory on the south-facing slope of Mount Hollywood in L.A.'s Griffith Park (LC-DIG-highsm- 22255).tif（commons-search）〈天文台空拍〉
- B：INVALID（室內雷射秀）— File:Tesla coil at Griffith Observatory LA.jpg
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Los Angeles Skyline, Griffith Park Observatory (3124933827).jpg（commons-search）〈LA 天際線〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:Griffith Park With Observatory (210512049).jpeg（commons-search）〈公園丘地〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Griffith Observatory front.jpg（commons-search）〈草坪人群〉
- F：子項 [7, 6, 6, 7] 均分 6.5 — File:Griffith Observatory (133860519).jpeg（commons-search）〈天文台夜色〉

### us-030 芝加哥天際線 — v3 **3.0**（v2: new，視覺 3.12，認證 3，社群 +0）
- 認證依據：芝加哥天際線——攝影攻略一致推薦，無官方景觀認證
- 合成：視覺3.12＋認證校正-0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Chicago sunrise 1.jpg（commons-search）〈湖鏡天際線〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Skyline de Chicago desde el centro, Illinois, Estados Unidos, 2012-10-20, DD 06.jpg（commons-search）〈暮色高樓〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:Chicago Skyline Sunrise March 15 2026 - 01.jpg（commons-search）〈夜明天際〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Chicago Skyline Sunrise March 15 2026 - 02.jpg（commons-search）〈白天全景〉
- E：子項 [7, 6, 5, 6] 均分 6.0 — File:R0015679 7-ELEVEN-芝加灣門市.jpg（commons-search）〈豆子鏡面〉
- F：INVALID（失焦空白）— File:CADAL11100444 加力比斯之月.djvu

### us-033 丹佛天際線 — v3 **2.0**（v2: new，視覺 2.38，認證 2，社群 +0）
- 認證依據：丹佛天際線＝一般都市天際線，無景觀認證
- 合成：視覺2.38＋認證校正-0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Mount Evans and Denver skyline from City Park Golf Course.jpg（commons-search）〈草坪望城〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:Denver Skyline (147779451).jpeg（commons-search）〈城景施工〉
- C：子項 [4, 4, 3, 4] 均分 3.75 — File:Denver skyline from Speer Blvd near I-25, April 2019.jpg（commons-search）〈公路望城〉
- D：INVALID（插畫非照片）— File:Denver Skyline - Illustration.jpg
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:Nighttime Denver Skyline.jpg（commons-search）〈夜間公園〉
- F：子項 [4, 4, 3, 4] 均分 3.75 — File:Denver skyline (55347682989).jpg（commons-search）〈街區樓群〉

### us-035 沃斯堡牲畜市場 — v3 **3.0**（v2: new，視覺 2.38，認證 3，社群 +0）
- 認證依據：沃斯堡牲畜市場＝國家史蹟區（NRHP），歷史街區景觀
- 合成：視覺2.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Fort Worth June 2016 68 (skyline).jpg（commons-search）〈會展中心天際〉
- B：INVALID（明信片建築）— File:Fort Worth High School (20102134).jpg
- C：INVALID（明信片建築）— File:Fort Worth Medical College (20102122).jpg
- D：INVALID（明信片建築）— File:Fort Worth High School (20102184).jpg
- E：INVALID（明信片建築）— File:Fort Worth University (20106750).jpg
- F：INVALID（明信片拼貼）— File:Fort Worth, Texas (20106806).jpg

### us-036 紐約曼哈頓天際線 — v3 **3.0**（v2: new，視覺 3.5，認證 3，社群 +0）
- 認證依據：曼哈頓天際線——國際攝影攻略一致推薦，無官方景觀認證
- 合成：視覺3.5＋認證校正-0.5＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [7, 7, 6, 7] 均分 6.75 — File:NYC Manhattan Skyline 1.JPG（commons-search）〈曼哈頓海線〉
- B：子項 [8, 7, 6, 8] 均分 7.25 — File:NYC Manhattan Skyline 2.JPG（commons-search）〈下城日落〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:NYC Manhattan Skyline 4.JPG（commons-search）〈新世貿城景〉
- D：子項 [7, 7, 5, 7] 均分 6.5 — File:NYC Manhattan Skyline 5.JPG（commons-search）〈晨光樓群〉
- E：子項 [8, 7, 6, 8] 均分 7.25 — File:NYC Manhattan Skyline 3.JPG（commons-search）〈晚霞天際線〉
- F：子項 [7, 6, 5, 6] 均分 6.0 — File:NYC Lower Manhattan skyline 2015 - panoramio.jpg（commons-search）〈灰色樓牆〉

### us-037 尼加拉瀑布 — v3 **4.0**（v2: new，視覺 4.0，認證 4，社群 +0）
- 認證依據：尼加拉瀑布州立公園（紐約州最老州立公園，官方）
- 合成：視覺4.0＋認證校正0.0＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 7, 8] 均分 8.0 — File:Niagara watervallen canada.jpg（commons-search）〈霧瀑斷崖〉
- B：子項 [9, 8, 7, 9] 均分 8.25 — File:Niagara-Falls-Horseshoe-Falls-view.jpg（commons-search）〈馬蹄瀑全景〉
- C：子項 [7, 6, 5, 6] 均分 6.0 — File:SkylineNiagaraFalls.jpg（commons-search）〈瀑布遠城〉
- D：子項 [9, 8, 7, 8] 均分 8.0 — File:Maid of the Mist - pot-o-gold.jpg（commons-search）〈虹霧遊船〉
- E：子項 [8, 7, 6, 8] 均分 7.25 — File:3Falls Niagara.jpg（commons-search）〈急流群瀑〉
- F：子項 [9, 8, 7, 8] 均分 8.0 — File:Niagara Falls 001.JPG（commons-search）〈雙瀑空拍〉

### us-039 邁阿密海灘 — v3 **2.0**（v2: new，視覺 2.94，認證 2，社群 +0）
- 認證依據：邁阿密海灘＝都市海灘，無景觀認證
- 合成：視覺2.94＋認證校正-0.94＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:MiamiSouthBeachPanoramaEdit.jpg（commons-search）〈沙灘樓影〉
- B：INVALID（建築特寫）— File:A1A & Espanada Way, Miami Beach, FL.jpg
- C：INVALID（雕像主體）— File:Living statue, Miami Beach, FL.jpg
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:Miami Beach R02.jpg（commons-search）〈灰灘塔群〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Lifeguard stand, Miami Beach.jpg（commons-search）〈救生塔經典〉
- F：子項 [7, 6, 5, 6] 均分 6.0 — File:Miamimetroarea.jpg（commons-search）〈海灘空拍〉

### us-040 波士頓天際線 — v3 **2.0**（v2: new，視覺 2.88，認證 2，社群 +0）
- 認證依據：波士頓天際線＝一般都市天際線，無景觀認證
- 合成：視覺2.88＋認證校正-0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search, openverse；抓到 5 張，有效 5 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Boston skyline from Longfellow Bridge September 2017 panorama 2.jpg（commons-search）〈河鏡樓群〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — Boston Skyline Panorama（openverse）〈夜光樓影〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Boston skyline from Grand View Ave Winthrop July 2025.jpg（commons-search）〈暗暮城市〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — POTD 2014-06-15 - Boston Skyline from Malone Park - HDR（openverse）〈紫夜紅磚〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — Boston skyline from the Prudential Skywalk - HDR - 2014-05-10 - [Explored]（openverse）〈港灣空拍〉

### us-044 安克拉治 — v3 **2.0**（v2: new，視覺 2.88，認證 2，社群 +0）
- 認證依據：安克拉治＝都市，無景觀認證
- 合成：視覺2.88＋認證校正-0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Anchorage on an April evening.jpg（commons-search）〈安城雪山倒影〉
- B：INVALID（地點待疑（峽瀑））— File:Mouth of Campbell Creek, in Anchorage, Alaska.jpg
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Beluga Point, Anchorage, Alaska, Estados Unidos, 2017-08-22, DD 02.jpg（commons-search）〈鐵路迪納利〉
- D：INVALID（圖騰柱器物）— File:Poste de Tótem, Anchorage, Alaska, Estados Unidos, 2017-09-01, DD 46.jpg
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Parque Eagle River, Anchorage, Alaska, Estados Unidos, 2017-09-01, DD 02.jpg（commons-search）〈谷地湖泊秋色〉
- F：INVALID（停車場）— File:Anchorage, Alaska 2016 314.jpg

### us-045 蘇華德 — v3 **3.0**（v2: new，視覺 2.88，認證 3，社群 +0）
- 認證依據：蘇華德——攝影攻略一致推薦（Exit Glacier/海港），無官方認證
- 合成：視覺2.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 4 張
- A：INVALID（狐狸動物主體）— File:Alaska Red Fox (Vulpes vulpes).jpg
- B：INVALID（異地洞穴壁畫）— File:Leones marinos de Steller (Eumetopias jubatus), Bahía de Aialik, Seward, Alaska, Estados Unidos, 2017-08-21, DD 80.jpg
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Seward, Alaska, Estados Unidos, 2017-08-21, DD 07.jpg（commons-search-topup）〈蘇華德山城〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Seward, Alaska, Estados Unidos, 2017-08-21, DD 09.jpg（commons-search-topup）〈海港小鎮〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:Seward, Alaska, Estados Unidos, 2017-08-21, DD 86.jpg（commons-search-topup）〈山湖霧靄〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Seward, Alaska, Estados Unidos, 2017-08-21, DD 87.jpg（commons-search-topup）〈水岸街區〉
- G：INVALID（非風景代表照）— File:Zimmerer Hs Seward NE.JPG
- H：INVALID（非風景代表照）— File:Jones House Seward NE.JPG
- I：INVALID（非風景代表照）— File:Seward Pennsylvania 2012.jpg
- J：INVALID（非風景代表照）— File:Seward County, Nebraska courthouse from S 1.JPG
- K：INVALID（非風景代表照）— File:Seward, Nebraska 5th and Seward NE corner.JPG
- L：INVALID（非風景代表照）— File:Seward, Nebraska (14187552466).jpg

### us-046 哈徹山口 — v3 **3.0**（v2: new，視覺 2.75，認證 3，社群 +0）
- 認證依據：哈徹山口——攝影攻略一致推薦，無官方認證
- 合成：視覺2.75＋認證校正0.25＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [8, 7, 5, 7] 均分 6.75 — File:Hatcher Pass Talkeetna Mountains Alaska.jpg（commons-search）〈雪嶺採礦界樁〉
- B：子項 [6, 6, 4, 6] 均分 5.5 — File:Hatcher Pass (1).jpg（commons-search）〈苔原谷地〉
- C：子項 [6, 6, 4, 5] 均分 5.25 — File:Hatcher Pass in winter 2.jpg（commons-search）〈雪埋礦舍〉
- D：INVALID（解說牌）— File:Hatcher Pass gold.jpg
- E：子項 [6, 6, 4, 6] 均分 5.5 — File:West down Hatcher Pass in Alaska, Jul 07.jpg（commons-search）〈綠谷殘雪〉
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:Hatcher S Pass (254438763).jpeg（commons-search）〈高山湖雪緣〉

### us-047 馬塔努斯卡冰河 — v3 **3.0**（v2: new，視覺 3.0，認證 3，社群 +0）
- 認證依據：馬塔努斯卡冰河——攝影攻略一致推薦，無官方認證
- 合成：視覺3.0＋認證校正0.0＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 6, 8] 均分 7.75 — File:Matanuska Glacier From The Air.JPG（commons-search）〈冰川空拍經典〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Matanuska River 8727.JPG（commons-search）〈谷壁岩塔〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:Matanuska Glacier mouth.jpg（commons-search）〈冰舌特寫〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Glaciar Matanuska, Alaska, Estados Unidos, 2017-08-22, DD 61.jpg（commons-search）〈冰河群山〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Glaciar Matanuska, Alaska, Estados Unidos, 2017-08-22, DD 68.jpg（commons-search）〈辮狀河公路〉
- F：子項 [6, 6, 5, 6] 均分 5.75 — File:Glaciar Matanuska, Alaska, Estados Unidos, 2017-08-22, DD 69.jpg（commons-search）〈切坡望峰〉

### us-048 波蒂奇冰河 — v3 **4.0**（v2: new，視覺 3.88，認證 4，社群 +0）
- 認證依據：Chugach 國家森林波蒂奇冰河遊憩區（USDA 官方）
- 合成：視覺3.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 10 張，有效 3 張
- A：子項 [9, 8, 6, 8] 均分 7.75 — File:Portage Glacier Alaska.jpg（commons-search-topup）〈波蒂奇冰河全景〉
- B：子項 [9, 8, 6, 8] 均分 7.75 — File:Portage Glacier Alaska (3).jpg（commons-search-topup）〈藍冰冰川〉
- C：子項 [9, 8, 6, 8] 均分 7.75 — File:Portage Glacier Alaska (5).jpg（commons-search-topup）〈雪峰冰川〉
- D：INVALID（黑白照片）— File:Portage Glacier, Alaska (5426404508).jpg
- E：INVALID（街景）— File:Poti market.jpg
- F：INVALID（紋章）— File:Poti COA.jpg
- G：INVALID（非風景代表照）— File:Poti – Aerial.jpg
- H：INVALID（非風景代表照）— File:1702 naar noorden.BP olierafinaderij, Kulevi boven Poti Zwarte Zee, Georgia.jpg
- I：INVALID（非風景代表照）— File:1692 naar oosten toe.BP olierafinaderij, Kulevi boven Poti Zwarte Zee, Georgia.jpg
- J：INVALID（非風景代表照）— File:Poti tower2.jpg

### us-050 朱諾 — v3 **3.0**（v2: new，視覺 3.0，認證 3，社群 +0）
- 認證依據：朱諾——攝影攻略一致推薦（州府/冰河門戶），無官方認證
- 合成：視覺3.0＋認證校正0.0＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Downtown Juneau and Douglas Island.jpg（commons-search）〈朱諾港空拍〉
- B：子項 [7, 6, 6, 7] 均分 6.5 — File:Juneau Waterfront 08.jpg（commons-search）〈霧中峽灣小鎮〉
- C：INVALID（街景）— File:Calle Front, Juneau, Alaska, Estados Unidos, 2017-08-17, DD 24.jpg
- D：INVALID（衛星影像）— File:Juneau, AK (ASTER).jpg
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:2018-09-20 01 Wide view of Juneau, Alaska USA.jpg（commons-search）〈郵輪碼頭〉
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:Queen Elizabeth (ship, 2010) in Juneau, Alaska 2024-08-15.jpg（commons-search）〈峽灣鎮全景〉

### us-051 門登霍爾冰河 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：Tongass 國家森林門登霍爾冰河遊憩區（USDA 官方）
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [9, 8, 6, 8] 均分 7.75 — File:Mendenhall Glacier (Winter).jpg（commons-search）〈門登霍爾冰河〉
- B：INVALID（黑白照片）— File:Mountain Peak, Alaska (1999).jpg
- C：子項 [9, 8, 6, 8] 均分 7.75 — File:Mendenhall Glacier 2004 08 15.jpg（commons-search）〈冰川鏡湖〉
- D：子項 [8, 7, 6, 7] 均分 7.0 — File:Glaciar Mendenhall, Juneau, Alaska, Estados Unidos, 2017-08-17, DD 09.jpg（commons-search）〈霧繞冰河林〉
- E：子項 [8, 7, 6, 8] 均分 7.25 — File:Glacier Collapse.jpg（commons-search）〈藍冰特寫〉
- F：子項 [8, 7, 5, 7] 均分 6.75 — File:Mendenhall Glacier - 2021-01-19.jpg（commons-search）〈冰湖倒映〉

### us-052 荷馬沙嘴 — v3 **3.0**（v2: new，視覺 3.25，認證 3，社群 +0）
- 認證依據：荷馬沙嘴——攝影攻略一致推薦，無官方認證
- 合成：視覺3.25＋認證校正-0.25＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 5, 7] 均分 6.75 — File:USACE Homer Spit Alaska.jpg（commons-search）〈荷馬沙嘴空拍〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Aerial View of Homer Spit.jpg（commons-search）〈卡徹馬克灣〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Homer spit from the hillside.jpg（commons-search）〈坡地民居〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Homer Spit AK - beach scene.jpg（commons-search）〈沙嘴餐廳〉
- E：子項 [8, 7, 5, 7] 均分 6.75 — File:Homer Spit aerial.jpg（commons-search）〈沙嘴月牙〉
- F：子項 [8, 7, 5, 7] 均分 6.75 — File:Homer Spit 2.jpg（commons-search）〈港灣沙嘴〉

### us-056 布魯克斯山脈 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：Gates of the Arctic 國家公園（布魯克斯山脈域內，官方）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [8, 7, 5, 7] 均分 6.75 — File:Brooks Range Mountains ANWR.jpg（commons-search）〈苔原湖群〉
- B：子項 [7, 6, 4, 6] 均分 5.75 — File:Brooks Range Mountains.jpg（commons-search）〈灰岩山脊〉
- C：子項 [7, 6, 4, 6] 均分 5.75 — File:Brooks Range (22).jpg（commons-search）〈冰蝕綠嶺〉
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Brooks Range (28).jpg（commons-search）〈霧峰雲杉〉
- E：INVALID（岩石化石特寫）— File:Coral fossils high in the Brooks Range, Alaska.jpg
- F：子項 [7, 6, 4, 6] 均分 5.75 — File:Rock Formations in Gates of the Arctic National Park. Brooks Range, Alaska.jpg（commons-search）〈灰岩石塔〉

### us-057 北極圈地標 — v3 **2.0**（v2: new，視覺 2.5，認證 2，社群 +0）
- 認證依據：北極圈公路地標——無官方景觀認證，僅攝影朝聖點
- 合成：視覺2.5＋認證校正-0.5＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：子項 [6, 5, 4, 5] 均分 None — File:Arctic circle Dalton Highway.jpg（None）
- B：子項 [6, 5, 4, 5] 均分 None — File:Arctic Circle sign (29650507696).jpg（None）
- C：INVALID（非風景代表照）— File:Arctic Circle sign.jpg

### us-061 柯迪亞克島 — v3 **3.0**（v2: new，視覺 3.31，認證 3，社群 +0）
- 認證依據：柯迪亞克島——攝影攻略一致推薦，無官方認證
- 合成：視覺3.31＋認證校正-0.31＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（火箭發射）— File:Athena 1 rocket launching from Kodiak Island.jpg
- B：子項 [8, 7, 6, 7] 均分 7.0 — File:Kodiak Island (8240252194).jpg（commons-search）〈霞光雪峰〉
- C：子項 [7, 6, 5, 6] 均分 6.0 — File:Pyramid Peak in Kodiak Island, Alaska (26415117178).jpg（commons-search）〈圓頂雪峰〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:Coastal delta on Kodiak Island.jpg（commons-search）〈辮狀三角洲〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Alaska (6750194629) (cropped to Kodiak Island).jpg（commons-search）〈群島空拍〉
- F：INVALID（航海圖）— File:Kodiak Island 1947.jpg

### us-062 埃克盧特納湖 — v3 **4.0**（v2: new，視覺 3.12，認證 4，社群 +0）
- 認證依據：Chugach 州立公園域內（Eklutna Lake，官方）
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Eklutna Lake from Twin Peaks trail.jpg（commons-search）〈湖光雪峰〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Eklutna Lake ENBLA03.jpg（commons-search）〈湖畔沙洲〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Eklutna Lake ENBLA02.jpg（commons-search）〈群峰鏡湖〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Eklutna Lake ENBLA07.jpg（commons-search）〈碧綠碎石灘〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Eklutna Lake ENBLA08.jpg（commons-search）〈林間碧湖〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Eklutna Lake, Chugach State Park, Eagle River, Alaska 2.jpg（commons-search）〈雪峰湖灣〉

### us-063 塔爾基特納 — v3 **unknown**（v2: new，視覺 None，認證 3，社群 +0）
- 認證依據：塔爾基特納——攝影攻略常見（迪納利門戶），無官方認證
- 合成：unknown：無有效代表照片（有認證但無視覺信號，不虛構分數）；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 7 張，有效 0 張
- A：INVALID（雕花招牌壁畫）— File:Talkeetna Library, Talkeetna, Alaska.jpg
- B：INVALID（歡迎招牌）— File:Welcome to beautiful downtown Talkeetna.jpg
- C：INVALID（主街街景）— File:Talkeetna June 2015.JPG
- D：INVALID（披薩招牌）— File:Talkeetna, Alaska (2574262734).jpg
- E：INVALID（天線設施）— File:Talkeetna Depot (46811402165).jpg
- F：INVALID（雪中木屋）— File:Talkeetna Visitors Center, Alaska, Winter.jpg
- G：INVALID（非風景代表照）— File:The Roadhouse, Talkeetna, Alaska 3.jpg

### us-064 艾利耶斯卡 — v3 **3.0**（v2: new，視覺 3.12，認證 3，社群 +0）
- 認證依據：艾利耶斯卡——攝影攻略常見（度假村），無官方認證
- 合成：視覺3.12＋認證校正-0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:Anchorage - View of inlet from Alyeska Ski Resort at Girdwood.jpg（commons-search）〈霧中冰川〉
- B：INVALID（度假村建築）— File:Alyeska Resort.JPG
- C：INVALID（木屋建築）— File:Building at Alyeska Resort.jpg
- D：INVALID（度假村招牌）— File:Alyeska Resort (2010) (15443770710).jpg
- E：INVALID（人物主體）— File:Lisa Murkowski at 2019 Alyeska Climbathon.jpg
- F：INVALID（雪村建築）— File:Alyeska Trip.jpg

### us-065 楚加奇州立公園 — v3 **4.0**（v2: new，視覺 3.88，認證 4，社群 +0）
- 認證依據：Chugach 州立公園（官方，美國最大州立公園之一）
- 合成：視覺3.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 6, 8] 均分 7.75 — File:Parque estatal Chugach, Alaska, Estados Unidos, 2017-08-22, DD 52.jpg（commons-search）〈山脊冰川群〉
- B：子項 [9, 8, 6, 8] 均分 7.75 — File:Parque estatal Chugach, Alaska, Estados Unidos, 2017-08-22, DD 63.jpg（commons-search）〈冰河特寫〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:Parque estatal Chugach, Alaska, Estados Unidos, 2017-08-22, DD 66.jpg（commons-search）〈沖積扇雪峰〉
- D：子項 [7, 6, 5, 6] 均分 6.0 — File:Parque estatal Chugach, Alaska, Estados Unidos, 2017-08-22, DD 68.jpg（commons-search）〈苔原沼澤〉
- E：子項 [9, 8, 6, 8] 均分 7.75 — File:Parque estatal Chugach, Alaska, Estados Unidos, 2017-08-22, DD 77.jpg（commons-search）〈冰河正面〉
- F：子項 [9, 8, 6, 8] 均分 7.75 — File:Parque estatal Chugach, Alaska, Estados Unidos, 2017-08-22, DD 94.jpg（commons-search）〈裂隙藍冰〉

### us-071 Kerry Park — v3 **2.0**（v2: new，視覺 2.75，認證 2，社群 +0）
- 認證依據：Kerry Park＝西雅圖市立公園——無任何景觀認證
- 合成：視覺2.75＋認證校正-0.75＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [8, 7, 5, 7] 均分 6.75 — File:Seattle 4.jpg（commons-search）〈天際線望雷尼爾〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:Kerry Park on a nice evening, 2014-10-19.jpg（commons-search）〈觀景台人群〉
- C：INVALID（設施特寫）— File:Tourists at Kerry Park (48572237686).jpg
- D：INVALID（地點不符（丘陵））— File:Ladies View in summer, Ring of Kerry, Killarney National Park (panoramic).jpg
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:Kerry Park 01.jpg（commons-search）〈座椅步道〉
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:Kerry Park & Seattle skyline 01.jpg（commons-search）〈秋葉天際線〉

### us-072 金色花園公園 — v3 **2.5**（v2: new，視覺 3.5，認證 2，社群 +0）
- 認證依據：金色花園公園＝市立公園，無景觀認證
- 合成：視覺3.5＋認證校正-1＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 6 張
- A：子項 [6, 6, 5, 6] 均分 5.75 — File:Golden Gardens 06.jpg（commons-search-topup）〈水岸戲水灘〉
- B：子項 [8, 7, 7, 7] 均分 7.25 — File:Atardecer Golden Gardens Park 06.jpg（commons-search-topup）〈普吉特灣燒霞〉
- C：子項 [8, 7, 7, 7] 均分 7.25 — File:Atardecer Golden Gardens Park 13.JPG（commons-search-topup）〈暮雲海灣〉
- D：子項 [7, 6, 7, 7] 均分 6.75 — File:Atardecer Golden Gardens Park 14.JPG（commons-search-topup）〈粉霞雲海〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Atardecer Golden Gardens Park 15.JPG（commons-search-topup）〈月暈暮雲〉
- F：子項 [8, 7, 7, 7] 均分 7.25 — File:Atardecer Golden Gardens Park 17.JPG（commons-search-topup）〈橘霞雲層〉
- G：INVALID（非風景代表照）— File:Rosa Gold Glow 2.jpg
- H：INVALID（非風景代表照）— File:Gold-crystals.jpg
- I：INVALID（非風景代表照）— File:Fountain pen writing (literacy).jpg
- J：INVALID（非風景代表照）— File:Multiple rows of golden statues of the Buddha seated with flowers, at Wat Phou Salao, Pakse, Laos.jpg
- K：INVALID（非風景代表照）— File:Skogskyrk Grav 2006.jpg
- L：INVALID（非風景代表照）— File:Skogskyrkogarden-night-2007-11-03.JPG

### us-073 阿爾基海灘公園 — v3 **2.0**（v2: new，視覺 2.38，認證 2，社群 +0）
- 認證依據：阿爾基海灘公園＝市立公園，無景觀認證
- 合成：視覺2.38＋認證校正-0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 10 張，有效 3 張
- A：INVALID（沙灘排球人群）— File:Alki Beach 7A.jpg
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Alki Beach, West Seattle aerial.jpg（commons-search-topup）〈阿爾基海灘空拍〉
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Beach Access 0784.jpg（commons-search-topup）〈墩柱涼亭眺望〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:Beach Access 0840.jpg（commons-search-topup）〈海灘遠望〉
- E：INVALID（黑白歷史照）— File:Alki Beach Puget Sound-552279.jpg
- F：INVALID（黑白歷史照）— File:ALKI BEACH ON PUGET SOUND, A FAVORITE RESORT FOR RESIDENTS OF SEATTLE. YOUNGSTER PLAYS AT THE WATER'S EDGE WHILE HIS... - NARA - 552279.jpg
- G：INVALID（非風景代表照）— File:Swimmers at the bathhouse and beach, Alki Point, West Seattle, 1918 (SEATTLE 1995).jpg
- H：INVALID（非風景代表照）— File:Alki Beach Park, Seattle, circa 1908 (MOHAI 9291).jpg
- I：INVALID（非風景代表照）— File:Beach view to the east from Alki Natatorium, ca 1905 (MOHAI 5979).jpg
- J：INVALID（非風景代表照）— File:Alki Beach, 1911 (3662558337).gif

### us-074 煤氣廠公園 — v3 **3.0**（v2: new，視覺 2.81，認證 3，社群 +0）
- 認證依據：煤氣廠公園＝國家史蹟名錄（NRHP）內，後工業景觀攝影名點
- 合成：視覺2.81＋認證校正0.19＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [5, 5, 3, 5] 均分 4.5 — File:Gas Works Park in Seattle.jpg（commons-search）〈地磚廣場〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Seattle from Gas Works Park2013.jpg（commons-search）〈煤氣塔湖景〉
- C：子項 [6, 6, 4, 5] 均分 5.25 — File:Gas Works Park, Seattle 3.jpg（commons-search）〈遊戲塔架〉
- D：子項 [7, 6, 5, 6] 均分 6.0 — File:Gas Works Park, Seattle.jpg（commons-search）〈鏽塔藍天〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Gas Works Park, Seattle 2.jpg（commons-search）〈塔影草坪〉
- F：子項 [6, 6, 4, 5] 均分 5.25 — File:Gas Works Park, Seattle 4.jpg（commons-search）〈塔群結構〉

### us-075 探索公園 — v3 **2.0**（v2: new，視覺 1.88，認證 2，社群 +0）
- 認證依據：探索公園＝市立公園，無景觀認證
- 合成：視覺1.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Seattle - Discovery Park 04.jpg（commons-search）〈草原望海〉
- B：子項 [4, 4, 3, 4] 均分 3.75 — File:Discovery Park, Liverpool 05.jpg（commons-search）〈公園草坪〉
- C：INVALID（樹木特寫）— File:Discovery Park, Liverpool 04.jpg
- D：INVALID（樹木建築）— File:Discovery Park, Liverpool 18.jpg
- E：子項 [4, 4, 3, 4] 均分 3.75 — File:Discovery Park, Liverpool 17.jpg（commons-search）〈草坪城市〉
- F：子項 [4, 4, 3, 4] 均分 3.75 — File:Discovery Park, Liverpool 26.jpg（commons-search）〈行道樹群〉

### us-076 漢密爾頓觀景公園 — v3 **2.12**（v2: new，視覺 3.12，認證 2，社群 +0）
- 認證依據：漢密爾頓觀景公園＝市立公園，無景觀認證
- 合成：視覺3.12＋認證校正-1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:Hamilton Viewpoint, Seattle, March 2013.jpg（commons-search）〈望城針塔〉
- B：INVALID（樹木特寫）— File:Seattle, August 2026 - 144.jpg
- C：INVALID（櫻花特寫）— File:Seattle, August 2026 - 145.jpg
- D：INVALID（關閉告示牌）— File:Seattle, August 2026 - 145 (cropped).jpg
- E：INVALID（廣告海報）— File:Pullman compartment cars through trains - interior of dining cars on the Cincinnati, Hamilton & Dayton R.R LCCN2003663800.jpg
- F：INVALID（廣告海報）— File:Pullman compartment cars through trains - interior of dining cars on the Cincinnati, Hamilton & Dayton R.R. LCCN2003663800.jpg

### us-077 何塞・黎剎博士公園 — v3 **2.0**（v2: new，視覺 1.88，認證 2，社群 +0）
- 認證依據：黎剎公園＝市立公園，無景觀認證
- 合成：視覺1.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：INVALID（關閉告示牌）— File:2023-06-23, Dr. Jose Rizal Park, Seattle, Washington, 001.jpg
- B：INVALID（銅牌特寫）— File:2023-06-23, Dr. Jose Rizal Park, Seattle, Washington, 009.jpg
- C：子項 [4, 4, 3, 4] 均分 3.75 — File:2023-06-23, Dr. Jose Rizal Park, Seattle, Washington, 010.jpg（commons-search）〈涼亭步道〉
- D：INVALID（銅牌特寫）— File:2023-06-23, Dr. Jose Rizal Park, Seattle, Washington, 011.jpg
- E：INVALID（銅牌特寫）— File:2023-06-23, Dr. Jose Rizal Park, Seattle, Washington, 012.jpg
- F：INVALID（銅牌特寫）— File:2023-06-23, Dr. Jose Rizal Park, Seattle, Washington, 013.jpg

### us-078 默特爾・愛德華茲公園 — v3 **2.0**（v2: new，視覺 2.12，認證 2，社群 +0）
- 認證依據：西雅圖市立公園——無任何景觀認證
- 合成：視覺2.12＋認證校正-0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [2, 3, 3, 4] 均分 None — File:Seattle (WA, USA), Pocket Beach -- 2022 -- 1707.jpg（None）
- B：子項 [3, 5, 4, 5] 均分 None — File:Seattle (WA, USA), Pocket Beach, Blick auf Elliott Bay -- 2022 -- 1701.jpg（None）
- C：子項 [3, 5, 4, 5] 均分 None — File:Seattle (WA, USA), Pocket Beach, Blick auf Elliott Bay -- 2022 -- 1709.jpg（None）

### us-079 斯諾夸爾米瀑布 — v3 **3.0**（v2: new，視覺 3.62，認證 3，社群 +0）
- 認證依據：斯諾夸爾米瀑布——攝影攻略一致推薦，部落土地無國家公園認證
- 合成：視覺3.62＋認證校正-0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 7, 8] 均分 7.5 — File:Snoqualmie Falls, Snoqualmie, WA.jpeg（commons-search）〈瀑布晚霞〉
- B：子項 [8, 7, 6, 7] 均分 7.0 — File:Snoqualmie Falls 3.jpg（commons-search）〈夜瀑燈光〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:Snoqualmie Falls 2.jpg（commons-search）〈瀑落松林〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:Snoqualmie Falls 7.jpg（commons-search）〈瀑頂水簾〉
- E：子項 [8, 7, 6, 8] 均分 7.25 — File:Snoqualmie Falls 4.jpg（commons-search）〈長曝白瀑〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Snoqualmie Falls 8.jpg（commons-search）〈瀑身特寫〉

### us-080 欺騙海峽州立公園 — v3 **4.0**（v2: new，視覺 3.12，認證 4，社群 +0）
- 認證依據：Deception Pass 州立公園（華盛頓州官方）
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Deception Pass 2.JPG（commons-search）〈欺騙峽空拍〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Deception Pass State Park, Washington (23024650420).jpg（commons-search）〈灣澳沙洲〉
- C：子項 [8, 7, 6, 8] 均分 7.25 — File:Deception Pass State Park, Washington (23320435315).jpg（commons-search）〈拱橋越峽〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Deception Pass State Park, Washington (23212151002).jpg（commons-search）〈橋跨水道〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Deception Pass State Park (9289864267).jpg（commons-search）〈灣口孤嶼〉
- F：子項 [6, 6, 4, 6] 均分 5.5 — File:Deception Pass June 2018 001.jpg（commons-search）〈漂流木灘〉

### us-081 雷尼爾山・天堂區 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：美國國家公園署（Mount Rainier NP 天堂區）官方
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Paradise Glacier 8346.JPG（commons-search）〈天堂冰川雪槽〉
- B：子項 [8, 7, 6, 8] 均分 7.25 — File:Paradise Glacier 8348.JPG（commons-search）〈雪階山徑〉
- C：子項 [9, 8, 6, 8] 均分 7.75 — File:Mount Rainier behind the flowering meadows of Paradise Park (18 August 2012).jpg（commons-search）〈雪峰野花坡〉
- D：INVALID（黑白歷史照）— File:Skier on Paradise Glacier, Mount Rainier (502361966).jpg
- E：INVALID（黑白雪洞照）— File:Exploring ice cave Paradise Glacier, Mt. Rainier, October 13, 1923.jpg
- F：INVALID（建築圖紙）— File:Roy H. Dobell Caddy House at Paradise Inn Mount Rainier National Park 1931.jpg

### us-082 雷尼爾山・倒影湖 — v3 **4.0**（v2: new，視覺 3.88，認證 4，社群 +0）
- 認證依據：美國國家公園署（Mount Rainier NP 倒影湖）官方
- 合成：視覺3.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 6, 8] 均分 7.75 — File:Mt Rainier-Reflection Lake.jpg（commons-search）〈羽扇豆白雪峰〉
- B：子項 [9, 8, 7, 9] 均分 8.25 — File:Mount Rainier and lake reflection.jpg（commons-search）〈燒霞鏡湖〉
- C：子項 [9, 8, 6, 8] 均分 7.75 — File:Reflection Lake at Mount Rainier National Park.jpg（commons-search）〈倒影湖鏡面〉
- D：子項 [9, 8, 6, 8] 均分 7.75 — File:Reflection Lakes Mount Rainier Seattle (127328459).jpeg（commons-search）〈秋色鏡湖〉
- E：子項 [9, 8, 7, 8] 均分 8.0 — File:Reflection Lakes, Mt Rainier (48656886908).jpg（commons-search）〈粉霞湖光〉
- F：子項 [8, 7, 5, 7] 均分 6.75 — File:Mt Rainier & Reflection Lakes (8082913563).jpg（commons-search）〈林湖雪頂〉

### us-083 雷尼爾山・日出區 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：美國國家公園署（Mount Rainier NP 日出區）官方
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 1 張
- A：INVALID（停車場主體）— File:Sunset from Sunrise Point (7 October 2024) 6.jpg
- B：INVALID（書頁文獻）— File:出使美日秘國日記(三).djvu
- C：INVALID（解說牌主體）— File:Historic Sunrise Road Wayside (2b370597-dc23-4300-bb2d-1ef052518734).JPG
- D：子項 [6, 6, 5, 6] 均分 5.75 — File:Mount Rainier from Sunrise WA1.jpg（commons-search-topup）〈枯木望主峰〉
- E：INVALID（遊客中心建築）— File:Sunrise Visitor Center (Yakima Park Stockade Group), Mount Rainier National Park, Ashford, WA.jpg
- F：INVALID（停車場設施）— File:Sunrise Visitor Center (Yakima Park Stockade Group), Mount Rainier National Park, Ashford, WA - 53798832093.jpg
- G：INVALID（非風景代表照）— File:Sunrise Visitor Center (Yakima Park Stockade Group), Mount Rainier National Park, Ashford, WA - 53798613506.jpg
- H：INVALID（非風景代表照）— File:Sunrise Visitor Center (Yakima Park Stockade Group), Mount Rainier National Park, Ashford, WA - 53799031680.jpg
- I：INVALID（非風景代表照）— File:Bryce Amphitheater from Sunrise Point Highres 2013.jpg
- J：INVALID（非風景代表照）— File:Sunrise Point Bryce Canyon November 2018 002.jpg
- K：INVALID（非風景代表照）— File:Sunrise Point Bryce Canyon November 2018 HDR.jpg
- L：INVALID（非風景代表照）— File:Sunset from Sunrise Point (7 October 2024) 5.jpg

### us-084 雷尼爾山・蒂普蘇湖 — v3 **4.0**（v2: new，視覺 3.88，認證 4，社群 +0）
- 認證依據：美國國家公園署（Mount Rainier NP Tipsoo Lake）官方
- 合成：視覺3.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：INVALID（野生動物主體）— File:Golden-Mantled Ground Squirrel, Mount Rainier, July 2006.jpg
- B：INVALID（滑翔傘活動主體）— File:Flickr - The U.S. Army - Jump over Mt. Rainier.jpg
- C：子項 [9, 8, 6, 8] 均分 7.75 — File:Mount Rainier behind the flowering meadows of Paradise Park (18 August 2012).jpg（commons-search）〈野花白雪峰〉
- D：子項 [8, 7, 5, 7] 均分 6.75 — File:Mount Rainier from the Silver Queen Peak.jpg（commons-search）〈主峰橫嶺〉
- E：INVALID（野生動物主體）— File:Golden-Mantled Ground Squirrel, Mount Rainier, June 2015.jpg
- F：子項 [9, 8, 7, 8] 均分 8.0 — File:Rainier20200906.jpg（commons-search）〈燒霞主峰〉

### us-085 紅寶石海灘 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：Olympic 國家公園海岸段（Ruby Beach）官方
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無標章、瀏覽量普通或資料不完整（不負向校正）
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Rock face, Ruby Beach, Olympic National Park, Washington State, 1992.JPG（commons-search）〈海崖漂流木〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Ruby Beach WA low tide.jpg（commons-search）〈闊灘漂流木〉
- C：子項 [7, 6, 6, 7] 均分 6.5 — File:Sunset at Ruby Beach (Olympic Peninsula, Washinton, USA).jpg（commons-search）〈夕光林岸〉
- D：子項 [9, 8, 6, 8] 均分 7.75 — File:Doorway to Ruby Beach in Washington.jpg（commons-search）〈海蝕拱門〉
- E：子項 [8, 7, 6, 8] 均分 7.25 — File:Breaker 3508.jpg（commons-search）〈海蝕柱浪湧〉
- F：子項 [8, 7, 6, 8] 均分 7.25 — File:Breaker 3507.jpg（commons-search）〈石柱群海〉

### us-086 里亞爾托海灘／牆中洞 — v3 **4.0**（v2: new，視覺 3.38，認證 4，社群 +0）
- 認證依據：Olympic 國家公園海岸段（Rialto Beach 牆中洞）官方
- 合成：視覺3.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [9, 8, 6, 8] 均分 7.75 — File:Rialto beach hole in the wall 39 (23104362626).jpg（commons-search）〈牆中洞經典〉
- B：子項 [8, 7, 5, 7] 均分 6.75 — File:Rialto Beach - 54019638408.jpg（commons-search）〈拱門遊客〉
- C：子項 [8, 7, 5, 7] 均分 6.75 — File:Rialto Beach - 54019410031.jpg（commons-search）〈拱門框海〉
- D：子項 [8, 7, 5, 7] 均分 6.75 — File:Rialto Beach - 54018509412.jpg（commons-search）〈洞口望海〉
- E：子項 [7, 6, 5, 6] 均分 6.0 — File:Rialto Beach - 54018508812.jpg（commons-search）〈潮池岩灘〉
- F：子項 [9, 8, 6, 8] 均分 7.75 — File:Rialto Beach - 54019847965.jpg（commons-search）〈石拱藍天〉

### us-087 颶風嶺 — v3 **4.0**（v2: new，視覺 3.12，認證 4，社群 +0）
- 認證依據：Olympic 國家公園（Hurricane Ridge）官方
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [8, 7, 5, 7] 均分 6.75 — File:Hurricane Ridge - Olympic National Park - Washington State (9779945775) (3).jpg（commons-search）〈高山草原眺望〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Hurricane Ridge panorama 2.jpg（commons-search）〈稜線步道〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Hurricane Ridge panorama.jpg（commons-search）〈山徑草嶺〉
- D：INVALID（花卉特寫）— File:Lupin on Hurricane Ridge, August 2012.JPG
- E：子項 [8, 7, 5, 7] 均分 6.75 — File:Hurricane Ridge panorama, August 2012.jpg（commons-search）〈颶風嶺雲湧〉
- F：子項 [7, 6, 5, 7] 均分 6.25 — File:View from Hurricane Ridge.jpg（commons-search）〈暗嶺層疊〉

### us-088 霍雨林 — v3 **unknown**（v2: new，視覺 None，認證 4，社群 +0）
- 認證依據：Olympic 國家公園（Hoh 雨林）官方
- 合成：unknown：無有效代表照片（有認證但無視覺信號，不虛構分數）；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 8 張，有效 0 張
- A：INVALID（解說牌）— File:Hoh Rain Forest - 54018550762.jpg
- B：INVALID（步道標牌）— File:Hoh Rain Forest - 54018538822.jpg
- C：INVALID（廁所告示）— File:Hoh Rain Forest - 54019463021.jpg
- D：INVALID（室內展示）— File:Hoh Rain Forest - 54019690468.jpg
- E：INVALID（室內展示）— File:Hoh Rain Forest - 54019462731.jpg
- F：INVALID（步道標牌）— File:Hoh Rain Forest - 54019461571.jpg
- G：INVALID（非風景代表照）— File:Hoh Rain Forest - 54019454206.jpg
- H：INVALID（非風景代表照）— File:Hoh Rain Forest - 54018551112.jpg

### us-089 帕盧斯瀑布 — v3 **4.0**（v2: new，視覺 4.0，認證 4，社群 +0）
- 認證依據：Palouse Falls 州立公園（華盛頓州官方）
- 合成：視覺4.0＋認證校正0.0＋社群0；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 4 張
- A：子項 [9, 8, 7, 9] 均分 8.25 — File:Palouse Falls.jpg（commons-search-topup）〈彩虹瀑布〉
- B：子項 [9, 8, 6, 8] 均分 7.75 — File:Palouse Falls in Eastern Washington.jpg（commons-search-topup）〈峽谷雙瀑〉
- C：子項 [9, 8, 7, 9] 均分 8.25 — File:Водопад Палаус.jpg（commons-search-topup）〈暮色瀑布〉
- D：INVALID（黑白歷史照）— File:Palouse Falls, Washington, 1952 (4276462668).jpg
- E：INVALID（黑白明信片）— File:Big Falls, Palouse River, April 24, 1911 - Palouse Falls, Washington (4276431750).jpg
- F：子項 [9, 8, 6, 8] 均分 7.75 — File:Palouse Falls in the Fall.png（commons-search-topup）〈高原望瀑〉
- G：INVALID（非風景代表照）— File:Teluk Palu, Sulawesi Tengah.jpg
- H：INVALID（非風景代表照）— File:Eski Palu Überblick.jpg
- I：INVALID（非風景代表照）— File:Palu III Bridge.jpg
- J：INVALID（非風景代表照）— File:Kota Palu.jpg
- K：INVALID（非風景代表照）— File:Muhammad J Wartabone Rizal Mayoral Candidate and Vice Mayoral Candidate of Palu.jpg
- L：INVALID（非風景代表照）— File:Hidayat Andi Nur Lamakarate Mayoral Candidate and Vice Mayor Candidate of Palu.jpg

### us-090 迪亞布羅湖 — v3 **4.0**（v2: new，視覺 3.62，認證 4，社群 +0）
- 認證依據：北喀斯開國家公園複合區（Diablo Lake，NPS 官方）
- 合成：視覺3.62＋認證校正0.38＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 6, 8] 均分 7.25 — File:Diablo Lake.JPG（commons-search）〈迪亞布羅全景〉
- B：子項 [9, 8, 6, 8] 均分 7.75 — File:Diablo Lake (Washington State).jpg（commons-search）〈冰川綠湖〉
- C：子項 [9, 8, 6, 8] 均分 7.75 — File:Diablo Lake looking toward Diablo Dam.jpg（commons-search）〈藍綠湖水〉
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:Diablo Lake 05.jpg（commons-search）〈雲影湖色〉
- E：子項 [8, 7, 5, 7] 均分 6.75 — File:Diablo Lake 06.jpg（commons-search）〈峭壁環湖〉
- F：子項 [8, 7, 5, 7] 均分 6.75 — File:Diablo Lake 07.jpg（commons-search）〈林間湖灣〉

### us-091 華盛頓山口觀景點 — v3 **3.88**（v2: new，視覺 2.88，認證 4，社群 +0）
- 認證依據：北喀斯開國家公園複合區（Washington Pass 觀景點，NPS 官方）
- 合成：視覺2.88＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 5, 7] 均分 6.75 — File:Washington Pass Observation Site 03.jpg（commons-search）〈雪峰河谷〉
- B：子項 [7, 6, 4, 6] 均分 5.75 — File:Washington Pass Observation Site 05.jpg（commons-search）〈花崗岩簷〉
- C：子項 [7, 6, 4, 6] 均分 5.75 — File:Washington Pass Observation Site 06.jpg（commons-search）〈松林尖峰〉
- D：子項 [6, 6, 4, 6] 均分 5.5 — File:Washington Pass Observation Site 07.jpg（commons-search）〈岩稜苔原〉
- E：子項 [7, 6, 4, 6] 均分 5.75 — File:Washington Pass Observation Site 08.jpg（commons-search）〈金字塔峰〉
- F：子項 [8, 7, 4, 7] 均分 6.5 — File:Washington Pass Observation Site pano 01.jpg（commons-search）〈犬牙雪巖〉

### us-092 藝術家角 — v3 **4.0**（v2: new，視覺 3.38，認證 4，社群 +0）
- 認證依據：Mount Baker 國家森林 Heather Meadows 遊憩區（Artist Point，USDA 官方）
- 合成：視覺3.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：INVALID（人群主體）— File:Visitors at Artist Point (11983069053).jpg
- B：INVALID（人群主體）— File:Visitors at Artist Point (8381919008).jpg
- C：子項 [8, 7, 5, 7] 均分 6.75 — File:Artist Point view of Yellowstone Canyon 03.jpg（commons-search）〈峽谷下瀑〉
- D：子項 [8, 7, 5, 7] 均分 6.75 — File:Artist Point view of Yellowstone Canyon 02.jpg（commons-search）〈瀑落黃石峽〉
- E：子項 [8, 7, 5, 7] 均分 6.75 — File:Artist Point view of Yellowstone Canyon 04.jpg（commons-search）〈下瀑縱谷〉
- F：子項 [8, 7, 5, 7] 均分 6.75 — File:Artist Point view of Yellowstone Canyon 08.jpg（commons-search）〈黃石大峽谷〉

### us-093 畫湖 — v3 **4.0**（v2: new，視覺 3.88，認證 4，社群 +0）
- 認證依據：Mount Baker 國家森林 Heather Meadows 遊憩區（Picture Lake，USDA 官方）
- 合成：視覺3.88＋認證校正0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 1 張
- A：INVALID（地點不符（夢蓮湖））— File:Moraine Lake 17092005.jpg
- B：INVALID（異地瀑布洞）— File:Kaindy lake south-east Kazakhstan.jpg
- C：INVALID（地點待疑）— File:Lake Vuoksa 1.jpg
- D：INVALID（異地火山湖）— File:Crater Lake winter pano2.jpg
- E：子項 [9, 8, 6, 8] 均分 7.75 — File:Mount Shuksan, Picture Lake (2362739742).jpg（commons-search）〈畫湖舒克桑山〉
- F：INVALID（異地彩泉空拍）— File:Lake MacKay Australia.jpg

### us-094 斯特普托山丘 — v3 **2.06**（v2: new，視覺 3.06，認證 2，社群 +0）
- 認證依據：斯特普托山丘＝市立觀景丘，無景觀認證
- 合成：視覺3.06＋認證校正-1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 6 張
- A：子項 [8, 7, 6, 7] 均分 7.0 — File:Palouse - American Tuscany.jpg（commons-search）〈麥田丘陵曲路〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:03-49-10 fields - panoramio.jpg（commons-search）〈帕盧斯丘陵〉
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:02-31-00, fields - panoramio.jpg（commons-search）〈濕地空拍〉
- D：子項 [8, 7, 5, 7] 均分 6.75 — File:03-12-15, palouse fields - panoramio.jpg（commons-search）〈拼布田園〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:01-07-12, picnic area - panoramio.jpg（commons-search）〈樹洞小徑〉
- F：子項 [7, 6, 5, 6] 均分 6.0 — File:Steptoe Butte day use state park (1456835577).jpg（commons-search）〈斯特普托丘〉

### us-095 失望角州立公園 — v3 **4.0**（v2: new，視覺 3.0，認證 4，社群 +0）
- 認證依據：Cape Disappointment 州立公園（華盛頓州官方）
- 合成：視覺3.0＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 4 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:Cape Disappointment and Cape Disappointment Light.jpg（commons-search）〈海崖浪蝕〉
- B：子項 [6, 6, 5, 6] 均分 5.75 — File:Cape Disappointment State Park.jpg（commons-search）〈斷崖海岸〉
- C：INVALID（巨樹特寫）— File:Cape Disappointment State Park - Ilwaco, Washington - 51739178132.jpg
- D：INVALID（公園招牌）— File:Cape Disappointment State Park - Ilwaco, Washington - 51740638784.jpg
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Cape Disappointment State Park - Ilwaco, Washington - 51740642754.jpg（commons-search）〈崖下石柱〉
- F：子項 [6, 6, 4, 6] 均分 5.5 — File:Cape Disappointment State Park - Ilwaco, Washington - 51739184177.jpg（commons-search）〈草岬遠海〉

### us-096 乾瀑布 — v3 **4.0**（v2: new，視覺 3.38，認證 4，社群 +0）
- 認證依據：Sun Lakes—Dry Falls 州立公園（華盛頓州官方，冰河洪水遺跡）
- 合成：視覺3.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：子項 [8, 7, 5, 8] 均分 7.0 — File:Sun Lakes coulee.jpg（commons-search）〈乾瀑布崖壁〉
- B：子項 [8, 7, 5, 7] 均分 6.75 — File:Dry Falls 2017-09-22 627.jpg（commons-search）〈冰期峽谷沼〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Dry Falls 2017-09-22 621.jpg（commons-search）〈黑岩峽壁〉
- D：INVALID（公路主體）— File:Sun Lake Dry Falls SP 5090.jpg
- E：INVALID（路牌設施）— File:Sun Lake Dry Falls SP 5091.jpg
- F：INVALID（歡迎招牌）— File:Sun Lake Dry Falls SP 5092.jpg

### tw-091 司馬庫斯部落觀景點 — v3 **unknown**（v2: 3.98，視覺 None，認證 3，社群 +0）
- 認證依據：司馬庫斯部落——攝影攻略一致推薦，無官方景觀認證
- 合成：unknown：無有效代表照片（有認證但無視覺信號，不虛構分數）；社群：無社群信號資料
- 照片來源：commons-search, commons-search-topup；抓到 12 張，有效 0 張
- A：INVALID（地點待疑（紅萍池））— File:Smangus 司馬庫斯 - panoramio (8).jpg
- B：INVALID（停車場部落）— File:司馬庫斯 Smangus - panoramio (8).jpg
- C：INVALID（木雕器物）— File:司馬庫斯 Smangus - panoramio (10).jpg
- D：INVALID（教堂建築）— File:Smangus 司馬庫斯 - panoramio (14).jpg
- E：INVALID（木雕像主體）— File:司馬庫斯 Smangus - panoramio (12).jpg
- F：INVALID（房舍建築）— File:司馬庫斯 Smangus - panoramio (15).jpg
- G：INVALID（非風景代表照）— File:Sima Qian 2.jpg
- H：INVALID（非風景代表照）— File:Sima Guang.jpg
- I：INVALID（非風景代表照）— File:Sima-Violet, Zweitakt-Boxermotor um 1923-24.jpg
- J：INVALID（非風景代表照）— File:Sima-Violet (Radaufhängung), Baujahr um 1924 (2008-06-28).JPG
- K：INVALID（非風景代表照）— File:Sima Guang 1.jpg
- L：INVALID（非風景代表照）— File:Lizarraga - Hayas y sima 01.jpg

### tw-022 二延平步道鋼構觀景平台 — v3 **3.38**（v2: 3.54，視覺 2.38，認證 4，社群 +0）
- 認證依據：阿里山國家風景區域內（二延平步道）
- 合成：視覺2.38＋認證校正1＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 3 張
- A：INVALID（道路主體）— File:Eryanping Trail 01 20251210.jpg
- B：INVALID（遊客中心停車場）— File:Eryanping Trail 02 20251210.jpg
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Eryanping Trail 03 20251210.jpg（commons-search）〈石階茶園步道〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:Pavilion of Eryanping Trail 01 20251210.jpg（commons-search）〈觀景平台亭〉
- E：子項 [6, 6, 5, 6] 均分 5.75 — File:Eryanping Trail 07 20251210.jpg（commons-search）〈棧道遠眺〉
- F：INVALID（解說牌）— File:Eryanping Trail 09 20251210.jpg

### tw-002 象山六巨石攝影平台 — v3 **3.0**（v2: new，視覺 2.38，認證 3，社群 +0）
- 認證依據：象山六巨石——攝影攻略一致推薦（101 夜景），非國家公園域
- 合成：視覺2.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search-topup；抓到 4 張，有效 3 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:Xiangshan trail.jpg（commons-search）〈象山石階步道〉
- B：子項 [5, 5, 4, 5] 均分 4.75 — File:Xiangshan trail 2.jpg（commons-search）〈步道石階〉
- C：INVALID（刻字岩壁特寫）— File:Xiangshan trail markers.jpg
- D：子項 [8, 7, 6, 8] 均分 7.25 — File:Taipei night skyline and Elephant Mountain May 2025.jpg（commons-search）〈六巨石望101夜景〉

### tw-012 香山濕地賞蟹步道 — v3 **3.0**（v2: new，視覺 2.38，認證 3，社群 +0）
- 認證依據：香山濕地＝國家級重要濕地（保育地位，非景觀認證）
- 合成：視覺2.38＋認證校正0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [5, 5, 4, 5] 均分 4.75 — File:香山濕地賞蟹步道.jpg（commons-search）〈蚵架海堤〉
- B：INVALID（水鳥主體）— File:五百分之一的琵嘴鷸.jpg
- C：子項 [5, 5, 4, 5] 均分 4.75 — File:Xiangshan Wetland-Hu Sung Chu-01.jpg（commons-search）〈賞蟹步道堤〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:Xiangshan Wetland-Hu Sung Chu-02.jpg（commons-search）〈涼亭步道〉
- E：子項 [5, 5, 4, 5] 均分 4.75 — File:Xiangshan Wetland-Hu Sung Chu-03.jpg（commons-search）〈泥灘濕地〉
- F：子項 [6, 6, 7, 6] 均分 6.25 — File:Xiangshan Wetland+minghsiung.yang+01((WDPA555594007)).jpg（commons-search）〈香山夕照剪影〉

### tw-014 雲洞山莊 — v3 **3.0**（v2: new，視覺 3.12，認證 3，社群 +0）
- 認證依據：雲洞山莊——攝影攻略一致推薦（雲海曙光），無官方認證
- 合成：視覺3.12＋認證校正-0.12＋社群0；社群：無社群信號資料
- 照片來源：commons-search, openverse；抓到 4 張，有效 1 張
- A：INVALID（地點不符（農舍））— File:Tuscan Landscape 7.JPG
- B：子項 [6, 6, 7, 6] 均分 6.25 — Yundong Villa, Miaoli, Taiwan.（openverse）〈雲海夜村〉
- C：INVALID（地點不符（高山草原））— File:Icelandic Landscape near Neskaupstaður July 2014.JPG
- D：INVALID（異地韓屋）— File:House of Hong Geonik in Pirun-dong.jpg

### tw-081 南竿鐵堡／海防礁岩 — v3 **4.0**（v2: new，視覺 3.12，認證 4，社群 +0）
- 認證依據：馬祖國家風景區域內（南竿鐵堡）
- 合成：視覺3.12＋認證校正0.88＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 5 張
- A：子項 [7, 6, 5, 7] 均分 6.25 — File:Iron Fort, Nangan, Matsu, Taiwan.JPG（commons-search）〈鐵堡礁岩棧道〉
- B：子項 [7, 6, 5, 7] 均分 6.25 — File:Iron Fort 鐵堡 - panoramio.jpg（commons-search）〈海防棧道〉
- C：子項 [7, 6, 5, 7] 均分 6.25 — File:Iron Fort 鐵堡 - panoramio (1).jpg（commons-search）〈迷彩岩壁〉
- D：子項 [7, 6, 5, 7] 均分 6.25 — File:Iron Fort 鐵堡 - panoramio (2).jpg（commons-search）〈礁島哨亭〉
- E：子項 [7, 6, 5, 7] 均分 6.25 — File:Iron Fort 鐵堡 - panoramio (3).jpg（commons-search）〈堡壘全景〉
- F：INVALID（設施前景）— File:Iron Fort 鐵堡 - panoramio (4).jpg

### tw-086 八里崁頭里・淡江大橋觀景點 — v3 **2.0**（v2: new，視覺 2.62，認證 2，社群 +0）
- 認證依據：八里崁頭里觀景點＝地方視點，無景觀認證
- 合成：視覺2.62＋認證校正-0.62＋社群0；社群：無社群信號資料
- 照片來源：commons-search；抓到 6 張，有效 2 張
- A：INVALID（建築主體）— File:行政院衛生署八里療養院 20121227.jpg
- B：INVALID（廟宇建築）— File:八里安福宮.jpg
- C：子項 [6, 6, 5, 6] 均分 5.75 — File:Cityscape Bali (New Taipei City, Taiwan) 20160207.jpg（commons-search）〈河景觀音山〉
- D：子項 [5, 5, 4, 5] 均分 4.75 — File:八里渡船碼頭.jpg（commons-search）〈河面漁船天際〉
- E：INVALID（街景彩繪牆）— File:八里國小125324.jpg
- F：INVALID（匾額特寫）— File:八里國小 124633.jpg
