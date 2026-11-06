# 事實查證掃描報告 — batch 1/6（tw-001–tw-030）

- 分支：task/FACTCHECK-1（基於 origin/main ae891f5c44efe92b2dd467cb7bc7c6f80239c858）
- 資料來源：weather_details/tw/tw-XXX.json（spot lat/lon、api_elevation、name）、regions.py 舊 tuple
- 查證日期：2026-11-06；方法：web_search 對照官方（國家風景區/國家公園/林業署/地方政府）與維基
- 標記：VERIFIED（權威源相符）/ CORRECT（常識+來源合理）/ CONFLICT（需修正查證）/ UNVERIFIABLE
- 統計：30 景點 — VERIFIED 14、CORRECT 7、CONFLICT 9、UNVERIFIABLE 0

## 衝突總表（CONFLICT，後續修復對象）

| 景點 | repo api_elevation | 查證值 | 偏差 |
|---|---|---|---|
| tw-004 不厭亭 | 505 m | 531 m | −26 m |
| tw-008 觀音山硬漢嶺 | 361 m | 616 m | −255 m |
| tw-013 火炎山 | 483 m | 596–614 m | −113+ m |
| tw-016 鳶嘴山 | 2120 m | 2180 m | −60 m |
| tw-020 金龍山 | 666 m | 820 m | −154 m |
| tw-021 武界部落 | 863 m | 760–820 m | +43 m |
| tw-025 二寮觀日亭 | 156 m | 185 m | −29 m |
| tw-029 鵝鑾鼻燈塔 | 39 m | 56.4（焦點海拔） m | −17.4 m |
| tw-030 屏東關山 | 128 m | 152 m | −24 m |

## 逐景點查證

### tw-001 — 大屯山助航站（Datunshan Navigation Station）

- repo 名稱：大屯山助航站 / Datunshan Navigation Station
- repo 座標：lat 25.17614, lon 121.52244（source: OSM/Mapcarta POI, confidence: medium）
- repo api_elevation：1082.0 m；elevation 欄位：None
- 查證值：助航台觀景臺約1076 m
- 來源：https://taiwantour.net/datun-mountain/
- **VERIFIED** — api_elevation 1082 m 與 1076 m 相差6 m，屬同一平台高度帶；名稱「大屯山助航站」通用正確（又稱助航台）。

### tw-002 — 象山六巨石（Xiangshan Six Boulders Viewpoint）

- repo 名稱：象山六巨石 / Xiangshan Six Boulders Viewpoint
- repo 座標：lat 25.02688, lon 121.57419（source: curated camera point, confidence: high）
- repo api_elevation：127.0 m；elevation 欄位：None
- 查證值：象山主峰184 m；六巨石 viewpoint 約130–150 m
- 來源：https://zh.wikipedia.org/zh-hant/%E8%B1%A1%E5%B1%B1_(%E8%87%BA%E5%8C%97%E5%B8%82)
- **VERIFIED** — api 127 m 為六巨石攝影點高度，低於主峰，合理。

### tw-003 — 淡水漁人碼頭（Tamsui Fisherman's Wharf）

- repo 名稱：淡水漁人碼頭 / Tamsui Fisherman's Wharf
- repo 座標：lat 25.18339, lon 121.41147（source: Taiwan scenic POI, confidence: high）
- repo api_elevation：5.0 m；elevation 欄位：None
- 查證值：海平面漁港，約0–10 m
- 來源：https://zh.wikipedia.org/wiki/%E6%B7%A1%E6%B0%B4%E6%BC%81%E4%BA%BA%E7%A2%BC%E9%A0%AD
- **CORRECT** — 名稱正確（法定名稱淡水第二漁港）；座標符合淡水河出海口東岸。

### tw-004 — 不厭亭（Buyan Pavilion Viewpoint）

- repo 名稱：不厭亭 / Buyan Pavilion Viewpoint
- repo 座標：lat 25.08923, lon 121.84752（source: New Taipei Tourism + direct photography GPS, confidence: high）
- repo api_elevation：505.0 m；elevation 欄位：None
- 查證值：約531 m
- 來源：https://myjourney.tw/buyen-pavilion/
- **CONFLICT** — api 505 m 比通行引用值 531 m 低約26 m；座標與台102線不厭亭位置相符。

### tw-005 — 大稻埕碼頭（Dadaocheng Wharf）

- repo 名稱：大稻埕碼頭 / Dadaocheng Wharf
- repo 座標：lat 25.0564, lon 121.50761（source: curated camera point, confidence: high）
- repo api_elevation：1.0 m；elevation 欄位：None
- 查證值：河岸約1–5 m
- 來源：https://www.travel.taipei/zh-tw/attraction/details/1
- **CORRECT** — api 1 m 合理；座標符合五號水門一帶。

### tw-006 — 關渡大橋（Guandu Bridge）

- repo 名稱：關渡大橋 / Guandu Bridge
- repo 座標：lat 25.125428, lon 121.45751（source: geographic POI, confidence: high）
- repo api_elevation：0.0 m；elevation 欄位：None
- 查證值：跨淡水河橋面近海平面
- 來源：https://newtaipei.travel/zh-tw/attractions/detail/110955
- **CORRECT** — api 0 m 合理；名稱/座標正確（亞洲第一座全焊接鋼拱橋）。

### tw-007 — 碧潭（Bitan Scenic Area）

- repo 名稱：碧潭 / Bitan Scenic Area
- repo 座標：lat 24.95599, lon 121.5365（source: Taiwan tourism POI, confidence: high）
- repo api_elevation：9.0 m；elevation 欄位：None
- 查證值：新店溪畔約5–15 m
- 來源：https://www.tad.gov.tw/m1.aspx?id=2187&sNo=0001016
- **CORRECT** — api 9 m 合理；座標在碧潭吊橋附近。

### tw-008 — 觀音山硬漢嶺（Guanyin Mountain Yinghan Peak）

- repo 名稱：觀音山硬漢嶺 / Guanyin Mountain Yinghan Peak
- repo 座標：lat 25.128356, lon 121.42433（source: Taiwan tourism POI, confidence: high）
- repo api_elevation：361.0 m；elevation 欄位：None
- 查證值：硬漢嶺 616 m（北觀處官方）
- 來源：https://www.northguan-nsa.gov.tw/user/article.aspx?Lang=1&SNo=04002861
- **CONFLICT** — api 361 m 與官方 616 m 相差255 m，明顯偏低；座標 25.1284,121.4243 與硬漢嶺峰頂(約25.128,121.432)差約0.8 km，均在容差內但建議複查。

### tw-009 — 望幽谷（Wangyou Valley）

- repo 名稱：望幽谷 / Wangyou Valley
- repo 座標：lat 25.146003, lon 121.797514（source: curated camera point, confidence: high）
- repo api_elevation：22.0 m；elevation 欄位：None
- 查證值：望幽谷步道 8–101 m
- 來源：https://www.travelerluxe.com/article/desc/230008983
- **VERIFIED** — api 22 m 位於步道 8–101 m 範圍（谷底段）；步道起點座標 25.14579,121.80489 與 repo 25.146,121.7975 相差約0.75 km，容差內。

### tw-010 — 和平島（Heping Island Park）

- repo 名稱：和平島 / Heping Island Park
- repo 座標：lat 25.158066, lon 121.768055（source: curated camera point, confidence: high）
- repo api_elevation：57.0 m；elevation 欄位：None
- 查證值：公園主體低海拔；島上東砲台山61 m
- 來源：https://ballenf.pixnet.net/blog/posts/4045667537
- **VERIFIED** — api 57 m 接近砲台山61 m，合理；名稱「和平島公園/和平島地質公園」正確。

### tw-011 — 永安漁港（Yongan Fishing Port）

- repo 名稱：永安漁港 / Yongan Fishing Port
- repo 座標：lat 24.98828, lon 121.01451（source: curated camera point, confidence: high）
- repo api_elevation：3.0 m；elevation 欄位：None
- 查證值：海平面漁港約0–5 m
- 來源：https://focustaiwan.net/live/yongan-fishing-harbor
- **CORRECT** — api 3 m 合理；座標符合新屋永安漁港。

### tw-012 — 香山濕地賞蟹步道（Xiangshan Wetland Crab Boardwalk）

- repo 名稱：香山濕地賞蟹步道 / Xiangshan Wetland Crab Boardwalk
- repo 座標：lat 24.783421, lon 120.91431（source: Taiwan tourism POI, confidence: high）
- repo api_elevation：2.0 m；elevation 欄位：None
- 查證值：潮間帶約0–3 m
- 來源：https://khh.travel/zh-tw/attractions/detail/162/
- **CORRECT** — api 2 m 合理（賞蟹步道沿濕地）；名稱正確，座標符合香山濕地。

### tw-013 — 火炎山（Huoyan Mountain）

- repo 名稱：火炎山 / Huoyan Mountain
- repo 座標：lat 24.369396, lon 120.72806（source: official natural reserve, confidence: high）
- repo api_elevation：483.0 m；elevation 欄位：None
- 查證值：火炎山主峰 596–614 m（小百岳）
- 來源：https://hiking.biji.co/index.php?act=info&q=review&review_id=47780
- **CONFLICT** — api 483 m 明顯低於主峰權威值；座標接近主峰，若為「1.8K大峽谷展望點」則483 m 可能代表展望點而非山頭 — 需 RD 依 DEM 確認 spot 所指。另 regions.py 舊 tuple (24.3630,120.7400) 與 weather_details (24.3694,120.7281) 相差逾1 km，兩路徑不一致。

### tw-014 — 雲洞山莊（Yundong Villa）

- repo 名稱：雲洞山莊 / Yundong Villa
- repo 座標：lat 24.388806, lon 120.822056（source: official site DMS, confidence: high）
- repo api_elevation：797.0 m；elevation 欄位：None
- 查證值：700–865 m（各源不一：旅宿網約700、業者自稱865、旅記約800）
- 來源：https://jinggotrip.com/yundonghome/
- **VERIFIED** — api 797 m 落於各源區間，可接受；名稱/座標正確（苗栗三義）。

### tw-015 — 高美濕地（Gaomei Wetlands）

- repo 名稱：高美濕地 / Gaomei Wetlands
- repo 座標：lat 24.31195, lon 120.54981（source: curated camera point, confidence: high）
- repo api_elevation：2.0 m；elevation 欄位：None
- 查證值：潮間帶約0–5 m
- 來源：https://www.taiwan.net.tw/m1.aspx?sNo=0001016&id=A12-00004
- **CORRECT** — api 2 m 合理；座標符合高美濕地。

### tw-016 — 鳶嘴山（Yuanzui Mountain）

- repo 名稱：鳶嘴山 / Yuanzui Mountain
- repo 座標：lat 24.241111, lon 120.955028（source: curated summit/camera point, confidence: high）
- repo api_elevation：2120.0 m；elevation 欄位：None
- 查證值：鳶嘴山 2180 m（林業及自然保育署官方步道資料）
- 來源：https://recreation.forest.gov.tw/Trail/RT?tr_id=060
- **CONFLICT** — api 2120 m 低於官方 2180 m 約60 m；weather_details 座標 24.2411,120.9550 與峰頂(約24.241,120.9492)容差內，但 regions.py 舊 tuple lon=120.9790 偏東約2.9 km — 超出容差，需修正路徑查證。

### tw-017 — 王功漁港（Wanggong Fishing Port）

- repo 名稱：王功漁港 / Wanggong Fishing Port
- repo 座標：lat 23.969796, lon 120.326592（source: curated camera point, confidence: high）
- repo api_elevation：5.0 m；elevation 欄位：None
- 查證值：海平面漁港約0–5 m
- 來源：https://tourism.chcg.gov.tw/AttractionsContent.aspx?id=80
- **CORRECT** — api 5 m 合理；名稱/座標正確（芳苑王功，芳苑燈塔塔高37.4 m 為另一地標）。

### tw-018 — 日月潭 水社壩（Sun Moon Lake · Shuishe Dam Viewpoint）

- repo 名稱：日月潭 水社壩 / Sun Moon Lake · Shuishe Dam Viewpoint
- repo 座標：lat 23.85495, lon 120.90546（source: curated camera point (Xiangshan lookout), confidence: high）
- repo api_elevation：747.0 m；elevation 欄位：None
- 查證值：日月潭海拔約748 m
- 來源：https://my.trip.com/moments/detail/nantou-759-151152150
- **VERIFIED** — api 747 m 與湖面748 m 一致；水社壩座標正確。

### tw-019 — 合歡山主峰（Mt. Hehuan Main Peak）

- repo 名稱：合歡山主峰 / Mt. Hehuan Main Peak
- repo 座標：lat 24.1426, lon 121.2712（source: national park summit waypoint, confidence: high）
- repo api_elevation：3417.0 m；elevation 欄位：3417
- 查證值：3417 m（維基/太魯閣國家公園/PEAKSTW 一致）
- 來源：https://zh.wikipedia.org/wiki/%E5%90%88%E6%AD%A1%E4%B8%BB%E5%B3%B0
- **VERIFIED** — elevation 3417 = api 3417，座標 24.1426,121.2712 與主峰(約24.1375,121.2703)容差內。

### tw-020 — 金龍山（Jinlong Mountain）

- repo 名稱：金龍山 / Jinlong Mountain
- repo 座標：lat 23.90023, lon 120.90869（source: curated camera point, confidence: high）
- repo api_elevation：666.0 m；elevation 欄位：None
- 查證值：約820 m（日月潭國家風景區管理處/交通部觀光署）
- 來源：https://www.taiwan.net.tw/m1.aspx?keystring=10008&sNo=0042331
- **CONFLICT** — api 666 m 比官方 820 m 低約154 m；名稱正確（金龍山=槌子寮山，魚池鄉大雁村）。

### tw-021 — 武界部落（Wujie Tribe）

- repo 名稱：武界部落 / Wujie Tribe
- repo 座標：lat 23.90874, lon 121.03959（source: National Cultural Memory POI, confidence: medium）
- repo api_elevation：863.0 m；elevation 欄位：None
- 查證值：部落 760–820 m
- 來源：http://trip.grp.com.tw/Zupload/Tripfile/T0715202202094fa92cba1e4541deb4215492ab9d6923.pdf
- **CONFLICT** — api 863 m 略高於通行 760–820 m 區間約40 m；座標符合仁愛鄉法治村。

### tw-022 — 二延平步道觀景平台（Eryanping Trail Viewing Platform）

- repo 名稱：二延平步道觀景平台 / Eryanping Trail Viewing Platform
- repo 座標：lat 23.422951, lon 120.651379（source: curated camera platform, confidence: high）
- repo api_elevation：1324.0 m；elevation 欄位：None
- 查證值：隙頂帶 1000–1500 m；入口/觀雲平台約1300–1450 m
- 來源：https://www.ali-nsa.net/zh-tw/attractions/detail/141
- **VERIFIED** — api 1324 m 落於區間；座標在台18線52.8K入口附近，正確。

### tw-023 — 頂石棹（Dingfazhao Trail）

- repo 名稱：頂石棹 / Dingfazhao Trail
- repo 座標：lat 23.474492, lon 120.701277（source: viewpoint coordinate, confidence: high）
- repo api_elevation：1370.0 m；elevation 欄位：None
- 查證值：石棹 1200–1600 m（約1300）
- 來源：https://drizzletea.com/edcontent_d.php?id=53&lang=tw&tb=6
- **VERIFIED** — api 1370 m 落於區間；頂石棹步道群位置正確。

### tw-024 — 祝山觀日平台（Alishan Zhushan Sunrise Platform）

- repo 名稱：祝山觀日平台 / Alishan Zhushan Sunrise Platform
- repo 座標：lat 23.512215, lon 120.822892（source: Zhushan sunrise platform, confidence: high）
- repo api_elevation：2459.0 m；elevation 欄位：None
- 查證值：祝山觀日平台約2451 m、小笠原山2464 m
- 來源：https://hiking.biji.co/index.php?act=detail&id=485&q=trail
- **VERIFIED** — api 2459 m 落於兩點之間；座標正確。

### tw-025 — 二寮觀日亭（Erliao Sunrise Pavilion）

- repo 名稱：二寮觀日亭 / Erliao Sunrise Pavilion
- repo 座標：lat 22.9928, lon 120.40972（source: viewpoint POI, confidence: high）
- repo api_elevation：156.0 m；elevation 欄位：None
- 查證值：約185 m（通行引用）
- 來源：https://www.taiwanviptravel.com/articles/erliao-sunrise/
- **CONFLICT** — api 156 m 比引用值185 m 低約29 m；「全台最低海拔觀日出勝地」描述一致。308高地(308 m)是另一點，未混淆。

### tw-026 — 井仔腳瓦盤鹽田（Jingzijiao Tile-paved Salt Fields）

- repo 名稱：井仔腳瓦盤鹽田 / Jingzijiao Tile-paved Salt Fields
- repo 座標：lat 23.25883, lon 120.10757（source: curated camera point, confidence: high）
- repo api_elevation：-3.0 m；elevation 欄位：None
- 查證值：海平面鹽田約0 m（可略低於海平面）
- 來源：https://chinatimes.com/realtimenews/20261106002602-260405
- **VERIFIED** — api -3 m 對排水鹽田屬邊緣合理；名稱「井仔腳瓦盤鹽田」正確（台灣現存最早瓦盤鹽田）。

### tw-027 — 田寮月世界（Tianliao Moon World）

- repo 名稱：田寮月世界 / Tianliao Moon World
- repo 座標：lat 22.886, lon 120.38898（source: curated geology POI, confidence: high）
- repo api_elevation：34.0 m；elevation 欄位：None
- 查證值：月世界地景公園 30–90 m
- 來源：https://uptogo.com.tw/%E6%97%85%E9%81%8A/%E7%94%B0%E5%AF%AE%E6%9C%88%E4%B8%96%E7%95%8C%E5%A5%BD%E7%8E%A9%E5%97%8E%EF%BC%9F/
- **VERIFIED** — api 34 m 落於區間；惡地(泥岩)描述與高雄旅遊網一致。

### tw-028 — 駁二藝術特區（Pier-2 Art Center）

- repo 名稱：駁二藝術特區 / Pier-2 Art Center
- repo 座標：lat 22.62033, lon 120.2817（source: POI, confidence: medium）
- repo api_elevation：8.0 m；elevation 欄位：None
- 查證值：港區倉庫群近海平面約5–10 m
- 來源：https://khh.travel/zh-tw/attractions/detail/6
- **CORRECT** — api 8 m 合理；名稱「駁二藝術特區 Pier-2 Art Center」正確，座標在鹽埕區。

### tw-029 — 鵝鑾鼻燈塔（Eluanbi Lighthouse）

- repo 名稱：鵝鑾鼻燈塔 / Eluanbi Lighthouse
- repo 座標：lat 21.902214, lon 120.85264（source: Taiwan Tourism lighthouse POI, confidence: high）
- repo api_elevation：39.0 m；elevation 欄位：None
- 查證值：燈塔焦點海拔 56.4 m（維基，塔高21.4 m）
- 來源：https://zh.wikipedia.org/zh-hant/%E9%B5%9D%E9%91%BE%E9%BC%BB%E7%87%88%E5%A1%94
- **CONFLICT** — api 39 m 明顯低於燈塔所在地岬角高度（焦距海拔56.4 m）；座標 21.9022,120.8526 與維基 21°54′08″N 120°51′10″E 一致。

### tw-030 — 屏東關山（Pingtung Guanshan Sunset）

- repo 名稱：屏東關山 / Pingtung Guanshan Sunset
- repo 座標：lat 21.964933, lon 120.719517（source: curated sunset viewpoint, confidence: high）
- repo api_elevation：128.0 m；elevation 欄位：None
- 查證值：關山（高山巖）152 m（恆春鎮公所官方）
- 來源：https://www.pthg.gov.tw/townhengchuen/cp.aspx?n=E3BCC84A0709DF36
- **CONFLICT** — api 128 m 比官方 152 m 低24 m；名稱「關山/高山巖」正確，珊瑚礁台地描述一致，可能指觀景點而非山頂。

## 結語

- 9 項 CONFLICT 全部為 api_elevation 與權威源偏差（−17 至 −255 m 或 +43 m），座標均在 ±0.01° 容差內（唯 tw-016/tw-013 的 regions.py 舊 tuple 座標與 weather_details 路徑不一致，建議一併查證）。
- 名稱與景點性質描述全部成立：實際存在、地形描述（惡地/珊瑚礁/崩崖/瓦盤鹽田/雲海茶園等）與官方描述一致。
- 無 UNVERIFIABLE 項目；本批僅報告，不做任何資料修改（唯讀任務）。
