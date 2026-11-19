# CL-DATA-77 — 低天氣光影依賴 13 筆處置審計 ＋ 方位幾何補齊

日期：2026-11-20 ｜ 角色：reviewer（審計段）＋RD（修正段）｜ 分支：`task/CL-DATA-77`

## 背景與範圍

來源：弱點清單 `low_weather_light`（catalog-scoring.json，13 筆，機械評分
weather_light_dependency 低＋建議「改題材」）。其中 tw-059-P01／tw-060-P01／
tw-078-P01（潮汐決定型，CL-DATA-76 範圍）與 us-111-P01（已裁撤）四筆已另票，
本票處置其餘 **9 筆**，另含 Gemini 稽核的 **方位幾何缺失 8 筆**。

共同根因（reviewer 查證結論）：這批題材的主判據是「無模型源的狀態指標」——
`river_flow_state`／`legacy_long_exposure`／`legacy_drift_ice` 等在評估層落
`METRIC_NOT_MAPPED → REQUIRED UNKNOWN`，整題材**永久 NOT_EVALUABLE**（
`apps/web-v2/evaluations-latest.json` 實測：jp-070/jp-081/jp-083/jp-091/tw-151/
tw-224/jp-041/jp-030 全數 NOT_EVALUABLE、day_verdict UNKNOWN）。
另 tw-082-P01 為**過期誤報**（CL-DATA-72 batch A 已接派生指標，現已可評估）。

## 逐筆裁定（9 筆）

| # | 題材 | 現況 | 裁定 | 理由與來源 |
|---|------|------|------|-----------|
| 1 | jp-030-P01 鳴門渦之道・漩渦 | `legacy_long_exposure` 佔位 | **收緊** | 漩渦由潮汐驅動：官方口徑大潮（新月/滿月隔日及周邊日）最盛、春（3月下旬–4月下旬）秋（9月下旬–10月下旬）規模最大、潮流最速＝滿/乾潮前後。落實為新派生指標 `spring_tide_state`（朔望 ±~2.7 天 ≒ 月照亮率 ≤8% 或 ≥92%，純天文、不需潮汐源）＋`light_window`（戶外步道夜間不可看）。精確時段誠實留給官方潮見表（不捏造逐時潮位）。來源：uzunomichi.jp/tide-calendar（大潮＝赤字、観潮±2h）、naruto-kankou.jp/uzu、pref.tokushima.lg.jp/uzushio、tabi.jtb.or.jp/res/360024-（大潮＝新月と満月の1日あたり） |
| 2 | jp-041-P01 知床流氷接岸 | `legacy_drift_ice` 佔位 | **收緊** | 流冰季窗＝發生學硬約束：知床（斜里町）1992–2002 平均初日 1/20、接岸初日 1/22、海明け 4/1（bonshome.sakura.ne.jp/ice.html，斜里無氣象站）；近年接岸最安定 2 月中旬–3 月上旬（nap-camp.com/mag/103789）。落實為 `seasonal_state=window_open`（季節曆新增 drift_ice 01-20～03-15，seasonal-calendar 橋判定）＋`light_window`＋`precipitation ≤0.3`。**誠實缺口**：接岸實況無即時觀測源——rationale 明示出發前查 JMA 流冰速報 |
| 3–8 | jp-070-P01 奧入瀬／jp-081-P01 鍋ヶ滝／jp-083-P01 吹割の滝／jp-091-P01 白谷雲水峡／tw-151-P01 內洞／tw-224-P01 銀河洞（瀑布 ×6） | `river_flow_state` 無派生 | **收緊（實作模板已聲明的派生）** | 瀑布模板（waterfall.json T1，2026-10-26 起草）本就宣告「水量＝過去 72h 累積雨量映射三級（provisional：<5 low、5–40 mid、>40 high；mid/high 可拍、過量僅提示）」，但評估層從未接線。六筆契約已符合模板（T1 水量＋T2 降水 ≤0.3＋T3 黃金時刻加分），缺的是評估層派生——本次接上：adapter 增 trailing-72h 逐時雨量（一次輕量呼叫、fail-closed），評估層逐時算精確滾動窗（不外推），`low` 否決。無契約改動 |
| 9 | tw-082-P01 鯉魚潭湖光倒影 | `water_reflection_state` | **結案不實作** | CL-DATA-72 batch A（CL-COND-A7）已派生水面狀態（鏡面/可拍/不宜）；現行 evaluations-latest 該題材已有 day_verdict PASS/PARTIAL。弱點清單條目為過期誤報，不動契約 |

（四筆已另票：tw-059-P01/tw-060-P01/tw-078-P01＝CL-DATA-76 乾潮窗施工中；us-111-P01＝裁撤。本票僅依指示補齊 tw-059/tw-060/tw-078 的方位幾何。）

## 方位幾何缺失 8 筆（Gemini 稽核 §一）

方法：OSM Nominatim 節點＋權威頁（Wikipedia/Seattle Parks/官網）交叉對位機位與
目標座標 → 大地測量初始方位角（WGS84 球面，北=0 順時針）寫入
`observation_relations`（`geometry_mode=static_verified`、derivation_method、
uncertainty_note、新增 `target_geometry`/`camera_location` evidence claim）。

| 題材 | 機位（驗證結果） | 目標座標 | 方位角 |
|------|----------------|---------|--------|
| us-075-P01 Discovery Park 山海景 | 保留（園區代表點；Wikipedia 47.65833,-122.41889 無衝突） | Mt Olympus 47.80122,-123.71091（OSM） | 280° |
| us-075-P02 West Point Lighthouse | 保留（園區代表點） | 燈塔 47.66198,-122.43573（OSM/Wikipedia/lighthousefriends 三源一致） | 283° |
| us-076-P01/P02 Hamilton Viewpoint | 保留（園區內；Wikipedia/西雅圖公園局無衝突） | Columbia Center 47.60454,-122.33072（OSM） | 70° |
| us-077-P01/P02 Jose Rizal Park | 保留，verification=verified（Wikipedia 47.59308,-122.31858／Seattle open-data 47.59386,-122.31809／NRHP 47.5924,-122.3175 收斂） | Columbia Center | 325° |
| jp-030-P99 渦之道漩渦（可拍） | 保留（渦之道廊道甲板帶代表點；ja.wikipedia 入口 34.237833,134.647889＋橋樑幾何一致） | 裸島東側渦帶 34.23703,134.64573（OSM 裸島；JTB「一番大きな渦は裸島の東側」） | 236°（PARTIAL：甲板俯視多向，僅錨定主渦帶） |
| tw-059-P01 奎壁山摩西分海 | 保留（OSM 奎壁山 23.60021,119.67116 無衝突） | 赤嶼 23.59925,119.67552（OSM） | 96° |
| tw-060-P01 雙心石滬 | **修正**：原點＝石滬本體（水中）→ 移至 OSM「雙心石滬觀景台」23.21943,119.44655（verified）；評估座標隨之南移 ~90m | 石滬 23.22021,119.44698（OSM） | 27° |
| tw-078-P01 建功嶼 | 保留（堤道東端代表點；OSM 建功嶼島 24.42736,118.30 ——0.46km 西，一致） | 建功嶼島 24.42736,118.29998（OSM） | 284°（取代 legacy 270，容差帶一致） |

全數落在契約 `view_azimuth`（observation_relations.azimuth_deg）＋座標＋
provenance（來源 URL＋2026-11-20 查證日）；jp-030-P99 標 PARTIAL 誠實容差。

## 未處置誠實未知項

- jp-030-P01／P99 的逐時「潮流最速時刻」：無免費可靠潮汐模型源，誠實不建模，
  卡片導引依官方潮見表（uzunomichi.jp）。
- jp-041-P01 的「接岸實況」：無即時源，rationale 明示查 JMA 流冰速報。
- us-075-P01 的東向 Cascade 分量、us-076 的海港全幅：多分量構圖，僅錨定主方向。

## RD 實施清單

1. 契約：jp-030-P01（rev 3：spring_tide_state＋light_window，claim-02/03）、
   jp-041-P01（seasonal_state＋light_window＋precipitation，claim-02/03）、
   10 筆方位幾何編輯（上表）；seasonal-calendar.json 新增 drift_ice 條目。
2. 評估層：`river_flow_levels()`（trailing 72h 精確滾動窗、fail-closed）、
   `spring_tide_state` 判定（朔望月照代理）、adapter
   `fetch_trailing_precipitation()`（Open-Meteo past_hours=72，一次/座標群、
   fail-closed）、bundle limitations 三語更新。
3. 詞彙/文案：metric-vocabulary.json 0.12（spring_tide_state）、
   fail_reason_short.json、assets/app.js（V2_EVAL_METRICS×3＋V2_FAIL_PRIORITY＋
   V2_FAIL_PHRASES×3）＋app.mjs（EVAL_METRICS）——`非大潮帶/outside the
   spring-tide band/大潮帯の外`；app.js stamp clui113→clui117＋index.html bump
   ＋54 個 stamp pin 測試重錨。
4. 限範圍重生成：evaluate_batch --only-place-id（jp-030/jp-041/jp-070/jp-081/
   jp-083/jp-091/tw-151/tw-224/tw-060）→ 併回 published bundle＋details。
5. re-pin（repin 邏輯內聯、commit 後對準）→ research_index build →
   build_web_catalog → research_index → sync_integration_sources。
