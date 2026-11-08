# CL-DATA-32 景點發現報告 — 日本南部（關西以西／九州／四國／中國地方）

日期 2026-11-08 ｜ admission = PM 判斷（owner 裁決 2026-11-08「你找到覺得好的就直接加入」；評分暫停）
座標驗證 2026-11-08：Wikimedia 逐筆核（ja.wikipedia REST summary / ja.wikipedia prop=coordinates / Wikidata P625），
來源網址記於各建置 record 的 camera derivation_method 與 data/v2/audits/cl-data-32_web_evidence.json；
原始核取快照 data/v2/tools/discovery/cl_data_32_coord_verify.json（含一次 429 冷卻重試記錄）。

## 已納入 14 個（雙軌建置：regions.py jp-051..064 + V2 contracts jp-051-P01..jp-064-P01）

| id | 名稱 | 題材(template) | 座標來源 | 四項判準重點 |
|---|---|---|---|---|
| jp-051 | 嚴島神社・宮島大鳥居 | reflection | ja.wikipedia 厴島神社 34.29602,132.31989 | 潮汐/海面倒影可判；世界遺產主體；與現有近海景點遠；可查證高 |
| jp-052 | 備中松山城雲海（天空の城） | cloud_sea（季節窗 09-25–04-10，高梁市官方） | ja.wikipedia 34.80909,133.62233；elev 430 m | 雲海 LCL 依賴＋早晚窗；與 jp-031 值 ~39 km |
| jp-053 | 天橋立 | overlook | ja.wikipedia 35.56936,135.19153 | 日本三景；能見度依度依賴；遠離清水寺 ~90 km |
| jp-054 | 伊根的舟屋 | reflection | ja.wikipedia 35.67572,135.28744 | 晨靜倒影；距 jp-053 ~12 km 題材異 |
| jp-055 | 鳥取砂丘 | sunset（風紋夕景） | ja.wikipedia 35.5425,134.23028 | 光影依賴強（低角夕照）；地質主體獨有 |
| jp-056 | 大山剣ヶ峰 | mountain_view | ja.wikipedia 35.3711,133.5464；elev 1729 m | 中國最高峰；冬季雪期封閉 |
| jp-057 | 稻佐山夜景 | city_night | ja.wikipedia 32.75336,129.84933；elev 333 m | 日本三大夜景；★與 jp-034 哥拉巴園 2.2 km 為互補對（夜景 vs 日間建築），沿用蔵王/御釜 2.6 km 互補先例 |
| jp-058 | 櫻島・湯之平展望所 | mountain_view（活火山） | Wikidata Q110582222 31.5915,130.6299 | 噴煙主體；警戒等級依氣象廳公告 |
| jp-059 | 阿蘇草千里ヶ浜 | mountain_view（雙火山口草原） | ja.wikipedia 32.88417,131.10389 | 火口噴煙＋草原；荒天封閉 fail-closed |
| jp-060 | 角島大橋 | overlook | ja.wikipedia 34.35277,130.88616 | 強風禁行；翡翠海弧線；距萩 ~90 km |
| jp-061 | 錦帯橋 | reflection | Wikidata Q1196460 34.16760,132.17837 | 錦川倒影＋木拱；距嚴島 ~28 km |
| jp-062 | 祖谷藤橋 | overlook（深谷） | ja.wikipedia かずら橋 33.87528,133.83528 | 冬雪臨時封閉；夜燈 19:00–21:30（不渡橋）；距鳴門遠 |
| jp-063 | 松山城（伊予） | overlook | Wikidata Q981357 33.84554,132.76572 | 瀬戶內展望；纜車營運以公告為準 |
| jp-064 | 元乃隅稻成神社 | overlook | ja.wikipedia 元乃隅神社 34.41972,131.06278 | 朱紅鳥居×海崖；距角島 ~19 km |

dedupe：14/14 與 232 既有景點 5km 最近鄰檢查通過（最近者為 jp-057↔jp-034 2.2 km 互補對，依先例保留並註記）。

## Shortlist（未建置，供下輪/cherry-pick）
- 軍艦島（端島）32.6278,129.7383（ja.wikipedia 端島）：登島由營運船隻許可硬性門檻，天氣模型無法判定
- 由布院温泉・金鱗湖 33.2660,131.3686（ja.wikipedia 由布院温泉）：晨霧佳但主體小品、與溫泉街視角重疊
- 四万十川・佐田沈下橋（Wikidata Q124878 河域 32.9333,132.9963）：沈下橋多點分布，待精查拍攝點

## 源頭挖掘記錄
命中：ja/zh Wikipedia + Wikidata API（1 rps 節流，遇 429 冷卻 240s 後重試）、各県観光/高梁市官方（備中松山城雲海 9月下旬–4月上旬早朝、最盛 10月下旬–12月上旬）、徳島県観光（藤橋渡橋 8:00–18:00／燈火 19:00–21:30）。
本輪不可達（誠實列出）：YAMATWO、なっぷ、500px/Flickr geotag API（付費鍵）、みんなのカメラ登入區。

## 建置與驗證摘要
- 雙軌：V2 contracts 14 筆（schema PASS，validate_task_w_contracts 14/14；模板克隆自已審查同類型並依 PM 判斷調整；季节窗 seasonal-calendar +unkai_bitchu）；legacy regions.py jp-051..064 + runtime catalog 252 spots/477 opps + manifest jp counts + runtime_dependencies gap ids
- 5km dedupe（機械重跑）＋座標 web 驗證（2 位未核實海拔誠實留空）
- 再生鏈：source-lock canonical/supporting repin → research_index build PASS（6 W1 schemas + provenance）→ build_web_catalog（232 places/420 opps, 6.32MB）→ task-x fixture re-anchor → sync_integration_sources SYNCED（w2 1899, w4 tree）
- 測試：node --test --test-isolation=none（node 26）518/518 PASS；python data/v2/tests 109/109 OK（CHASELIGHTS_W1_SPEC_ROOT=specs/v2）；specs/v2/tests 79/79 OK
