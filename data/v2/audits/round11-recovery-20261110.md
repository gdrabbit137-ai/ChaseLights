# Round 11 挑戰者質疑清單重建（2026-11-10）

round11 原報告遺失，僅存摘要「季節語意不對稱＋事實修正批」。本檔以紅隊模式重建：對 6 個 US 題材各提出 ≥3 個候選質疑，逐一以外部權威來源驗證。查證日期一律 **2026-11-10**。讀取基準：origin/main d14be82c9（唯讀，未修任何契約/資料檔）。

---

## us-125-P01 坎坎瑪格斯楓紅公路（White Mountain NF, NH）

契約現況：seasonal_plant 模板；seasonal_state window_open；季節曆窗 **09-29→10-27**；altitude_m **926**（3,037 ft）；座標 -71.365, 44.0234（Kancamagus Pass 對位，medium）；precip rationale 引「花田步道…小雨水珠加分」。

| # | 候選質疑 | 驗證 | 判定 |
|---|---|---|---|
| 1 | 季節窗尾 10-27 偏晚：當地 peak 集中在 9 月底–10 月中 | kancamagushighway.com：peak=十月頭兩週、「October 19th 應已 past peak」；AAA Northeast 2025/Old Farmer's Almanac：White Mountains peak early Oct；Bretton Woods 2026 導覽：late Sep–mid Oct、early Oct 最常見。窗尾較多方來源晚約一週以上，且描述「9月末至10月下旬典型峰值」的「下旬」過頭 | **成立** |
| 2 | 海拔 3,037 ft / 926 m 疑似錯誤 | Wikipedia《New Hampshire Route 112》：NH 112 越 Kancamagus Pass **2,855 ft (870 m)**；NewEngland.com、OnlyInYourState 同 2,855 ft；dangerousroads.org 給 874 m。契約多寫 ~56 m，無任何來源支持 3,037 ft | **成立（CONFLICT）** |
| 3 | precip 條件 rationale 是花田模板文案（「花田步道」「微雨水珠加分」），與楓紅題材語意錯置 | 契約自身文案（seasonal_plant-v0.1 模板未重寫）；對照同專業語意：楓紅拍攝的降雨門檻理由應為「濕葉/霧氣」而非水珠加分 | **成立（模板錯置類）** |
| 4 | 座標對位 Pass 而非「走廊」（公路 34.5 mi 長） | camera_context kind=area、medium 已標註；Pass 是公路最高點與定番瞭望位，對位合理 | 不成立（座標合理，維持 medium 標註） |

證據 URL（2026-11-10 查證）：
- https://kancamagushighway.com/fall-foliage-on-kancamagus-highway-nh-fall-foliage/
- https://magazine.northeast.aaa.com/daily/travel/road-trips/northeast-fall-foliage-trips/
- https://www.brettonwoodsvacations.com/blog/white-mountains-fall-foliage-2026-peak-color-forecast-best-scenic-drives-where-to-stay/
- https://en.wikipedia.org/wiki/Kancamagus_Highway
- https://www.dangerousroads.org/north-america/usa/4029-kancamagus-highway.html/

---

## us-139-P01 水晶磨坊秋色（Crystal Mill, Gunnison County, CO）

契約現況：overlook 模板；**無 SEASON_TIME/seasonal_state 條件**；季節曆 entries 無本點；altitude_m 2710；座標 -107.10389, 39.05889（NRHP 對位）。

| # | 候選質疑 | 驗證 | 判定 |
|---|---|---|---|
| 1 | 名稱含「秋色」卻無季節窗——冬季/夏季照樣可被判符合，與 us-125（有窗）、us-141 Last Dollar（09-20→10-10）不對稱 | 季節曆 us 條目僅 us-125/us-126/us-134/us-141/us-149；Colorado State Forest Service + USFS：高海拔 aspen 於 9 月–10 月初轉色（2,700 m 帶 peak 約 9 月下旬–10 月上旬），且秋季後雪封路使磨坊拍攝季實質上在暖季 | **成立（季節語意不對稱）**；建議補窗約 09-15→10-10 級距（本檔僅建議，不改檔） |
| 2 | 座標偏移 | NRHP/Wikidata：**39°03′32″N 107°06′14″W = 39.05889, -107.10389** 與契約逐位一致 | 不成立 |
| 3 | 海拔 2710 m 無單點來源 | Wikipedia 給的是 Crystal 鎮中心 8,951 ft (2,728 m)；磨坊在鎮下方 Crystal River 出露岩上，無權威單點海拔公開；2,710 m 落在鎮區高程帶（2,590–2,728 m）內、低於鎮中心合理 | 不成立（合理但建議 provenance 註明為鎮區高程帶推定） |
| 4 | 「私人路需高底盤車」開放資訊 | NRHP 登錄表：County Road 3、Marble 東南 7 mi；多方來源同述 4WD/高底盤私道，與契約一致 | 不成立 |

證據 URL（2026-11-10 查證）：
- https://commons.wikimedia.org/wiki/Category:Crystal_Mill （39°03′32″N 107°06′14″W, NRHP 85001493）
- https://npgallery.nps.gov/AssetDetail/15311a1e-deda-4eea-ad81-bcec145281da
- https://en.wikipedia.org/wiki/Crystal,_Gunnison_County,_Colorado
- https://csfs.colostate.edu/forests-trees/aspen-fall-colors/
- https://www.fs.usda.gov/wildflowers/beauty/fallcolors/rockymountains.shtml

---

## us-143-P01 特里利姆湖胡德山倒影（Trillium Lake, Mt. Hood NF, OR）

契約現況：reflection 模板；water_surface_state（不結冰/未乾涸）僅 advisory 不否決；altitude_m **1160**（derivation 引 3,812 ft/1,162 m）；座標 -121.7417, 45.2617；描述行銷「冬季冰湖雪景」。

| # | 候選質疑 | 驗證 | 判定 |
|---|---|---|---|
| 1 | 海拔 1,162 m 疑似錯誤 | USFS Mt. Hood NF 官方 Trillium Lake Day Use：**Elevation 3,600 feet**；Wikipedia：surface elevation **3,601 ft (1,098 m)**。1,162 m 較兩個權威高 ~62 m，「3,812 ft」查無來源 | **成立（CONFLICT）** |
| 2 | 描述行銷「冬季冰湖雪景」但題材是 reflection——湖面結冰時倒影物理上不成立，而 water_surface_state 是純提示不否決，冬季日期仍可能被判「符合」 | 契約自身語意（water_surface_state「純提示、不否決、缺公告 propagate unknown」）＋描述三語同寫冬季冰湖；USFS 將 Trillium Sno-Park 列為冬季使用區（冬季湖面結冰是常態而非例外） | **成立（季節語意不對稱：描述與判據矛盾）** |
| 3 | 座標 45.2617,-121.7417 偏離湖面 | Wikipedia 湖心 45.2673,-121.7423（契約點在南約 0.6 km 南岸）。經典倒影構圖即自南岸向北望胡德山（湖在胡德山 SSW 7.5 mi），南岸為正確拍攝側 | 不成立（合理拍攝點；建議以 photo point 語意註明） |
| 4 | 歸屬/管理機關 | USFS Mt. Hood NF 官方 recreation 頁（Day Use/Campground/Sno-Park）確認 USFS 屬性與「對胡德山倒影定番」描述 | 不成立 |

證據 URL（2026-11-10 查證）：
- https://www.fs.usda.gov/r06/mthood/recreation/trillium-lake-day-use （Elevation 3,600 feet）
- https://en.wikipedia.org/wiki/Trillium_Lake （3,601 ft / 1,098 m；45.2673406, -121.7422998）
- https://www.fs.usda.gov/r06/mthood/recreation/trillium-sno-park-trailhead

---

## us-136-P01 帕洛杜羅燈塔岩（Palo Duro Canyon SP, TX）

契約現況：overlook 模板；altitude_m 900；座標 -101.68, 34.97（derivation 引「Lighthouse 岩區約 34°58′N 101°41′W」）；描述「約20公里長峽谷 / ~20-mile canyon」「全美第二大峽谷」。

| # | 候選質疑 | 驗證 | 判定 |
|---|---|---|---|
| 1 | 座標對位錯誤：34.97,-101.68 不在 Lighthouse 岩體 | TPWD 官方步道圖/POI（主管機關一級來源）：**Lighthouse = 34.9364, -101.6967**。契約點在其東北 ~4 km（鄰近 wildlife viewing blind 34.9737,-101.6764 / 步道口一帶）；TPWD 地質誌另註 Lighthouse 在 Little Sunday Canyon、園界外 ~3 mi。拍攝位若取步道口，從該點根本看不到岩體；uncertainty_m=null 與「medium」主張亦不符 | **成立（CONFLICT，以主管機關座標為準）** |
| 2 | 「約20公里長 / ~20-mile canyon」長度錯誤 | TPWD 官方 Nature 頁：canyon **about 120 miles long、20 miles wide、up to 800 ft deep**。「20」是寬度（英里）非長度；zh 版再誤把單位縮成公里 | **成立（事實錯誤）** |
| 3 | 「全美第二大峽谷」 | TPWD 官方兩頁同述 "The second largest canyon in the country" | 不成立 |
| 4 | 海拔 900 m | 峽谷緣高程帶約 3,000+ ft（公園 HQ 34.9847 高程帶相近）；Lighthouse 峽谷底較低；900 m 落於邊坡合理帶，無官方單點海拔可證偽 | 不成立（無法證偽，合理） |

證據 URL（2026-11-10 查證）：
- https://tpwd.texas.gov/state-parks/palo-duro-canyon/trails-info （POI Lighthouse 34.9364, -101.6967）
- https://tpwd.texas.gov/publications/pwdpubs/media/park_maps/pwd_mp_p4506_0007p.pdf （官方步道圖同座標）
- https://tpwd.texas.gov/state-parks/palo-duro-canyon/nature （120 mi long / 20 mi wide / 800 ft deep）
- https://www.gutenberg.org/files/52179/52179-h/52179-h.htm （Lighthouse 位於 Little Sunday Canyon、園界外）

---

## us-121-P01 比克斯比橋夕照（Big Sur, CA）

契約現況：sunset 模板；sunset_window ±40 min；altitude_m 80；座標 -121.9046, 36.0727；描述「橋面約85m」「us-122 麥克威瀑布 14km 南」。

| # | 候選質疑 | 驗證 | 判定 |
|---|---|---|---|
| 1 | 橋高「約85m」 | Wikipedia Bixby Bridge infobox：Height **280 feet (85 m)** ✓ | 不成立 |
| 2 | 座標 | Wikipedia 36°04′22″N 121°54′17″W = 36.0728, -121.9047 ✓（1932 年開放拱橋同頁確認） | 不成立 |
| 3 | 「us-122 麥克威瀑布 14km 南」錯誤 | Wikipedia：McWay Falls = 36.1586, -121.6661。與本點實測距 **~23.5 km**（南偏東），非 14 km。另：**us-122 契約自身座標存 -121.9762, 36.3586**——該點在 Bixby 北方 ~32.5 km 且遠離 McWay 真址 ~25 km，疑似嚴重錯位（超出本 6 點範圍，列為 us-122 的獨立 lead） | **成立（鄰點關係事實錯誤＋us-122 座標 lead）** |
| 4 | 夕照語意 | sunset_window（日落 ±40 min）在契約內；Big Sur 西臨太平洋，西沉方向正確 | 不成立 |

證據 URL（2026-11-10 查證）：
- https://en.wikipedia.org/wiki/Bixby_Bridge （280 ft/85 m；36°04′22″N 121°54′17″W）
- https://en.wikipedia.org/wiki/McWay_Falls （36°09′31″N 121°39′58″W）
- repo 內 us-122-P01.json 座標（-121.9762, 36.3586）— 獨立 lead

---

## us-128-P01 反射峽谷 S 形灣（Glen Canyon NRA, UT）

契約現況：overlook 模板；altitude_m 1330；座標 -110.9038, 37.1746（展望台推定，誠實標註）；「無步道、約16–18 英里越野徒步」。

| # | 候選質疑 | 驗證 | 判定 |
|---|---|---|---|
| 1 | 徒步距離 16–18 mi 誇大 | whatdoyousea：16 mi（往返實測 8.18+7.69）；organizedadventurer：16–18 mi RT；lakepowellnavigator：15–18 mi off-trail RT。一致 | 不成立 |
| 2 | 海拔 1330 m 與自身引文 4,466 ft (1,361 m) 差 31 m | whatdoyousea/organizedadventurer：Peak elevation **4,466 ft**。契約 derivation 自己引了 1,361 m 卻存 1330 m（展望台略低於 peak 可辯，但與自引值不一致） | **部分成立（建議對齐引文或註明展望台略低於 peak）** |
| 3 | 座標不可靠 | 無官方座標；aroundus 給 37.17555,-110.91098（西偏 ~0.7 km）；契約已誠實標「展望台推定/medium、access 不計分」 | 不成立（推定性質已誠實標註） |
| 4 | 季節：無任何季節提示（冬季雪、夏季 >100°F 高溫） | overlook 全日模板慣例＋access 誠實標註已列；屬可用性資訊非語意錯誤 | 不成立（建議性，非質疑成立） |

證據 URL（2026-11-10 查證）：
- https://www.whatdoyousea.com/reflection-canyon/
- https://organizedadventurer.com/reflection-canyon/
- https://lakepowellnavigator.com/blog/reflection-canyon-by-boat/
- https://aroundus.com/p/173011416-reflection-canyon

---

## 總結（成立質疑數）

| id | 成立 | 主旨 |
|---|---|---|
| us-125-P01 | 3 | 楓紅窗尾 10-27 偏晚（peak 集中 9 月底–10 月中）＋Pass 海拔 3,037ft 應為 2,855ft＋花田模板文案錯置 |
| us-139-P01 | 1 | 名稱「秋色」無季節窗，與 us-125/us-141 不對稱（建議補 09-15→10-10 級距窗） |
| us-143-P01 | 2 | 海拔 1,162m 與 USFS/Wikipedia 3,600/3,601ft 衝突＋描述行銷冬季冰湖但判據允許結冰期「符合」 |
| us-136-P01 | 2 | 座標應以 TPWD 官方 Lighthouse POI 34.9364,-101.6967 為準（差 ~4km）＋峽谷長度誤植（TPWD：120 mi 長，20 mi 是寬；zh 又縮成公里） |
| us-121-P01 | 1 | 「us-122 麥克威瀑布 14km 南」實為 ~23.5km；且 us-122 自身座標（36.3586,-121.9762）疑似嚴重錯位，列獨立 lead |
| us-128-P01 | 1 | 海拔 1330m 與自引 4,466ft/1,361m 不一致（其餘誠實標註合格） |
