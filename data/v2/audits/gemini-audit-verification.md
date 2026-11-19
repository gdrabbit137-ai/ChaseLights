# Gemini 異常稽核清單事實查證（tw-/us- 景點題材條件）

- 查證日期：2026-11-20。基準：`origin/main` 現行契約（`git show origin/main:data/v2/opportunities/<id>.json`）、`data/v2/seasonal-calendar.json`、`data/v2/audits/discovery/catalog-scoring.json`（弱點清單）、evaluations 免責聲明；必要事實另以官方管理單位網頁查證。
- 方法教訓落實：每筆先確認 Gemini 比對的是同一景點、同一欄位。兩筆（[1] 的引擎行為、[6] 的 AOD 單位）屬 Gemini 誤讀既有設計，已個別註記。
- 本檔為純報告，未改動任何契約。

## 逐筆判定

### [1] tw-073-P01（老梅春季綠石槽晨光）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | ① `季節窗(必須)=window_open` 但季節窗欄為空，引擎會永遠 False 或拋錯；② 綠石槽需乾潮前後 ±2 小時，現行條件無潮汐門檻；建議補 03-15~05-05。 |
| 現行契約實況 | `condition_contract`（rev 3）確有 `seasonal_state eq "window_open"`（REQUIRED/MAIN）。但季節窗語義依 CL-DATA-25 建置規則讀 `seasonal-calendar.json`，**兩者皆缺時誠實 `not_evaluatable`，不會 False 也不會拋錯**——Gemini 對引擎行為的描述是誤報。實質問題屬實：`seasonal-calendar.json` 62 個 entries 中**查無老梅綠石槽（tw-073）條目**，季節門檻永遠無法解析。潮汐部分：v2 契約無任何 `tide*` metric，且評估免責聲明明載「潮位決定的海岸被寫體誠實降級 not_evaluatable，請自行查干潮表」——屬既有設計決策，非本筆異常。 |
| 判定 | **真缺口（季節窗未登錄）**；潮汐與引擎行為部分＝誤報／既有設計 |
| 建議 | 於 seasonal-calendar.json 新增老梅綠石槽條目（owner 管理）。官方窗口：北觀處「每年2月到5月，最佳4、5月（清明後至端午前）」，巡守期 3/1–5/31；Gemini 建議的 03-15~05-05 較官方窗口偏窄。潮汐資訊維持現行「提醒查 CWA 石門潮汐表」設計，是否新增潮汐 metric 請 owner 另行裁定。來源：https://www.northguan-nsa.gov.tw/user/article.aspx?Lang=1&SNo=04008584 、https://www.northguan-nsa.gov.tw/user/article.aspx?Lang=1&SNo=04007088 |

### [2] tw-076-P01（龍磐草原海岸日出）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | 題材標籤「山景展望」誤植，套用 `cloud_cover_mid(必須)[30,60]` 會誤殺晴朗日出；缺 `cloud_cover_low(必須)`。 |
| 現行契約實況 | 屬實：`genre_template: mountain_view`（rev 3），條件含 `cloud_cover_mid between [30,60]%（REQUIRED）`，且確無任何低雲條件。龍磐為臨海草原向東看海平線日出，非山嶺雲海/山景語義；晴朗日出日會被中雲必須條件擋下。 |
| 判定 | **需要 owner 裁決**（題材重定義屬語義類） |
| 建議 | 事實無爭議，但改判 genre（mountain_view → sunrise 模板，如 tw-073-P01 的 sunrise 條件組）屬題材語義重定義，須 owner 確認龍磐的定位（日出 vs 山海草原遠眺）後改契約。 |

### [3] tw-076-P02（龍磐草原銀河／星空）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | ① `moon_altitude<0` 與另外三個月照條件互斥／冗餘且封殺微月光地景；② `galactic_core_altitude ≥10°`（必須）封殺 11–1 月冬季星空；③ 未設風速上限（落山風）。 |
| 現行契約實況 | 條件清單屬實（rev 2：moon_altitude<0、moon_illumination_fraction ≤0.5、moon_target_separation ≥40°、moon_illuminance_proxy ≤0.15、galactic_core_altitude ≥10° 全為 REQUIRED；無風速條件）。但邏輯解讀有誤：月仰角<0 成立時後三者**自動通過（冗餘非互斥、非誤殺）**；「封殺微月光地景」實為模板設計意圖（銀河題材要求月在地平下）。銀核心 ≥10° 在天文昏影終後確實約 3–10 月才成立，11–1 月不觸發——是「核心導向」與「全年星空」的路線取捨。風速：35 個 night_sky 契約中僅 2 個（tw-035-P05、tw-045-P03）有風速門檻，缺風速屬模板常態非本筆個別異常；落山風屬實（墾丁冬季）。 |
| 判定 | **需要 owner 裁決**（三項皆為語義/設計取捨） |
| 建議 | 若 owner 決定支持冬季銀河與微月光地景，可改 any_of 雙軌（月仰角<0 OR 月相≤0.25 且夾角≥45°）並將 galactic_core 降 QUALITY；風速上限建議在 night_sky 模板層統一加，而非單筆。 |

### [4] tw-078-P01（建功嶼退潮石板道景觀）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | tidal 題材卻掛已廢棄的 `legacy_mountain_view(必須)`，無潮汐窗也無光影門檻。 |
| 現行契約實況 | 完全屬實：rev 2 條件僅一筆 `legacy_mountain_view（REQUIRED）`。該佔位條件全庫僅 6 筆（jp-030-P01、jp-041-P01、jp-078-P01、tw-059-P01、tw-060-P01、tw-078-P01），皆為 R0「V1 遷移骨架、待第二輪研究」，並已在 weakness list 以 `low_verifiability 1.0 / 條件缺 claim 或 threshold_source` 追蹤。 |
| 判定 | **真缺口（已知、已在庫內追蹤）** |
| 建議 | 改為潮汐通行窗＋夕照光影條件組。官方依據：金門縣政府依潮汐公布建議登島時段（乾潮前後短暫時間，約滿潮後3小時至乾潮後2小時），日落後禁止登島；來源：金門縣觀光旅遊網（建功嶼潮汐公告）。潮汐 metric 為 v2 尚未建置的資料能力，能力建置請 owner 裁定。 |

### [5] tw-074-P01（野柳女王頭地景光影）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | 標籤「日出（通用）」但 `sunrise_time_window` 降級 QUALITY、必須改用全天光線窗，語意矛盾。 |
| 現行契約實況 | 屬實：rev 2 `genre_template: sunrise`，`sunrise_time_window` 為 QUALITY/MODIFIER，`light_window`（civil，太陽仰角 >−6°）為 REQUIRED——但該 light_window 是 CL-DATA-19/23 全面稽查時**有意**加上語意修正（非夜景全日題材統一補 civil 光線窗，理由記於 rationale_i18n）。契約自洽（全天地質光影＋日出加分），只是 genre 標籤未同步。 |
| 判定 | **需要 owner 裁決**（語義類） |
| 建議 | 兩條路皆可：(a) 維持全天地質光影語義、genre 改 `golden_hour`；(b) 保留日出語義、`sunrise_time_window` 升回 REQUIRED。選擇權在 owner，現行條件本身無引擎層錯誤。 |

### [6] tw-072-P02（南雅奇岩夕照雲霞）、tw-074-P02（野柳蕈狀岩與燭台石群紋理）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | ① `landform_present(必須)` 無觀測來源屬佔位符；② `aod_550nm ≤0.4` 帶 "AOD" 單位後綴與其他列不一致、易解析失敗；③ tw-072-P02 缺 `cloud_cover_low(必須) ≤40%`。 |
| 現行契約實況 | ①誤報：`landform_present` 為全庫 geological_landform 模板的既有條件，rationale 明載「靜態主體存在性由機會定義聲明（owner 於景點建立時確認），非即時評估，propagate_unknown 保底」——設計如此，非佔位符。②誤報：`unit:"AOD"` 為全庫通行寫法（68 個 opportunity 契約同格式），非解析異常。③屬實：tw-072-P02（golden_hour/夕照雲霞）條件僅 landform_present、precipitation ≤0.3、golden_hour_window、aod_550nm ≤0.4、light_window，**無任何雲量門檻**；對照姊妹模板（us-075-P02 sunset 有 `cloud_cover_low ≤55%`（必須）＋中高雲 [20,70] QUALITY），夕照雲霞題材缺雲量判據確實影響鑑別度。 |
| 判定 | **混合：③真缺口；①②誤報** |
| 建議 | tw-072-P02 補 `cloud_cover_low(必須)`（建議沿用 sunset 模板既有已審門檻 55%，而非 Gemini 憑空的 40%）與中高雲 QUALITY；①②不需修改。 |

### [7] tw-059-P01、tw-060-P01、tw-082-P01、tw-151-P01、tw-224-P01（低光影依賴群組）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | 全組低天氣光影依賴（1.0~2.0）、條件幾乎只要不下雨就觸發；tw-059/060 另有 geometry_not_verified/targets_missing。 |
| 現行契約實況 | 分四種實況：(a) tw-059-P01（`legacy_long_exposure`）、tw-060-P01（`legacy_reflection`，且無 genre 模板）確為單一佔位條件、幾何 provisional——屬實且已在 weakness list（low_weather_light 1.0＋low_verifiability 1.0 多重 gap）追蹤；(b) tw-078 同類（見 [4]）；(c) tw-082-P01（reflection：wind_speed_10m ≤2 m/s＋water_reflection_state＋precipitation＋雲量 [20,60] QUALITY）**條件非「只要不下雨」**——Gemini 以訛傳訛；但其 target geometry 為 unknown（無座標）屬實；(d) tw-151-P01、tw-224-P01 為標準 waterfall 模板（river_flow_state 必須＋降水＋golden hour 加分），score 2.0 為 rubric 計分結果。 |
| 判定 | **混合：(a) 真缺口（已知追蹤）；(c)(d) 誤報** |
| 建議 | (a) 佔位條件待第二輪研究替換（補潮汐/光影條件＋幾何，owner 資源排程）；(c)(d) 條件已具鑑別度，ruble 低分與「scoreless intake（owner 裁定 admission=查證＋5km 去重，score 留空）」皆為既有裁定，不因 Gemini 一句「改題材」而動。 |

### [8] us-075-P01/P02、us-076-P01/P02、us-077-P01/P02（幾何查證缺口群組）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | 6 筆 geometry_not_verified＋targets_missing（score 1.5），致星空 `moon_target_separation_deg(必須) ≥40°` 與日出日落方位遮擋運算無法求解。 |
| 現行契約實況 | 幾何 provisional（imported_from_v1_viewpoint_reference、evidence_refs 空）屬實且已在 weakness list（low_verifiability 1.5、geometry_not_verified＋targets_missing_evidence_refs）。但「方向性角度規則失效」的論據是誤報：這 6 筆契約的 genre 為 overlook/sunset/blue_hour_city，**契約內根本沒有任何 moon_target_separation 或方位遮擋條件**，無規則可失效。 |
| 判定 | **誤報（引用的規則不存在）；幾何缺口為已知追蹤項** |
| 建議 | 無需「先補幾何再啟用方向規則」——這些題材本來就不用方向角規則。幾何/證據補齊照既有 low_verifiability 追蹤排程即可。 |

### [9] us-111-P01（布魯克斯瀑布階梯水景）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | 低天氣光影依賴（score 2.0，建議改題材），條件過寬；建議 golden_hour(必須) 或 visibility ≥25 km＋AOD ≤0.25。 |
| 現行契約實況 | score 2.0／rec「改題材」確在 weakness list（catalog-scoring.json low_weather_light）——主張與既有清單一致。但 Gemini 的替代條件不適配題材：契約為標準 waterfall 模板（river_flow_state 必須＋降水＋golden hour QUALITY），Brooks Falls 是白天賞瀑與棕熊捕鮭場景（target/camera geometry 已 verified，來源 Wikipedia CL-DATA-43），golden_hour 硬門檻與 25 km 眺望通透是山景/遠眺題材的規則，套在瀑布上反而錯殺。 |
| 判定 | **需要 owner 裁決**（是否改題材；Gemini 建議的具體門檻不建議採用） |
| 建議 | 若 owner 認定「瀑布水流狀態」判據不足以稱攝影題材，依 weakness list 原建議走「改題材/移候選池」流程；不要用眺望型門檻硬改瀑布題材。 |

### [10] tw-071 ~ tw-080（多語系 en/ja 欄）
| 欄位 | 內容 |
|---|---|
| Gemini 主張 | en/ja 欄直接複製繁中，未本地化。 |
| 現行契約實況 | 完全屬實：tw-071~tw-080 全部 15 筆契約 `name_i18n.en` 與 `ja` 均等於 `zh-TW`（逐一程式檢核）。對照已本地化者（tw-082-P01、tw-151-P01、tw-224-P01、us-111-P01 等）可見差距。 |
| 判定 | **真缺口** |
| 建議 | 批次翻譯補齊（入庫前 i18n 檢核）；屬資料補件，不改條件契約。 |

## 計數

10 筆稽核項：**誤報 1（[8]，另有 [1][6][7] 部分誤報）／真缺口 3（[1][4][10]）／混合（真缺口＋誤報併陳）2（[6][7]）／需要 owner 裁決 4（[2][3][5][9]）**。

其中真缺口與混合的「真缺口」半邊（[1][4][10]、[6]③、[7]a）皆為已知/可定位的資料補件；無任何一筆顯示現行契約會在引擎層拋錯或誤判 False。

## Owner 裁決落地（CL-DATA-76，2026-11-20）

本稽核「需要 owner 裁決」四項與真缺口半邊，由 owner 兩份裁決（主稽核＋第二份稽核新增項）落地：

- [1] 老梅：seasonal-calendar 登錄官方 2–5 月（最佳 4–5 月，來源北觀處 URL）；並補乾潮前後 ±2 小時潮汐決定門檻（water_surface_state，CL-COND-A7 誠實模式；legacy tide_state 已接）。
- [2] tw-076-P01：模板 mountain_view→sunrise（與 tw-080-P01 同族對齊）；低雲必須 35%；能見度 ≥15 km 必須；cloud_cover_mid [30,60] 降為加分；rationale 三語改寫為太平洋海崖草原語義（75 已先行降格中雲＋補 30/15，76 依 owner 裁決調 35 並完成對齊）。
- [3] tw-076-P02 銀河：owner 未裁定（維持現狀，不在 76 範圍）。
- [4] 建功嶼 tw-078：legacy_mountain_view 佔位改為官方乾潮登島窗（金門縣政府公告，乾潮前後約 ±30 分）＋黃金時段錨點（日落後禁止登島）＋降水；潮汐決定語義走 water_surface_state（V2 誠實 not_evaluatable，legacy tide_state 供卡片判讀）。
- [5] tw-074-P01：契約條件不動；genre/家族標籤 sunrise→geological_landform（與 tw-074-P02 同家族）。
- [7]a tw-059/tw-060：佔位改為潮汐決定型真實契約（CL-DATA-20「待潮汐模組」語義由本票取代——legacy tide_state 已接，V2 誠實降級）。
- [9] us-111：裁撤。product_status=retired（lifecycle_status retired；regions.py tuple 與契約檔保留，id 保留於 manifest retired_spot_ids）；狀態：低天氣光影依賴（弱點清單 score 2）＋題材無適配模板→裁撤入候選池（owner 裁決 2026-11-20）；弱點清單該列處置改「已裁撤」。
- [10] tw-071~080 15 筆 en/ja 名稱補齊（自然日文、零簡體字）。
- 第二份稽核：tw-072-P02/tw-074-P02 移除 landform_present（無觀測源指標；REQUIRED 集非空，未另補代理）；tw-072-P02 雲量門檻由 CL-DATA-75 先行補上（≤40%，未再動）；單位正規化（降水 mm→mm/h 14 筆、aod「AOD」後綴移除 68 筆，僅動單位欄、門檻不變）；jp-021-P02 綁西穗高口官方星空観賞便營運季（seasonal_state＋seasonal-calendar 登錄，來源 URL 記 provenance；精確營運日由 legacy shinhotaka access provider 把關）。
