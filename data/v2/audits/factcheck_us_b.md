# Fact-check scan — batch 5/6: us 區後半（us-049–us-096）

- 掃描範圍：data/v2/opportunities/us-049*–us-096*（實存 58 份契約；us-049/053/054/058/066–068/070 無檔）
- 掃描基準：contract-semantic-audit 已知 mismatch classes（name↔window 語義、threshold=null、
  template misplacement、window tier、高緯 light_window），並對照 CL-DATA-11/12 已落地修正
  （batch f 高緯全日題材 light_window、batch g 低雲 null 修復）作為 known-fixed 排除清單。
- 方法：機讀契約逐筆規則掃描 + 被標記筆的 rationale 人工複核。日期：2026-11-06。
- 掃描者：chaselights_fact_checker（read-only audit；本檔為唯一產出）

## 統計

- OK：44 / 58
- MISMATCH（真語義矛盾，建議開票）：8 筆 id / 8 項
- OBSERVATION（範圍/分類決策待裁定，非單筆矛盾）：4 筆 id
- MINOR（模板錯置但無功能矛盾）：3 筆 id

## OK ids

us-050-P01 us-050-P02 us-051-P01 us-052-P01 us-055-P02 us-056-P01 us-059-P01 us-059-P02
us-060-P01 us-060-P02 us-061-P01 us-063-P01 us-064-P01 us-065-P01 us-071-P01 us-071-P02
us-072-P01 us-072-P02 us-073-P01 us-073-P02 us-074-P01 us-075-P01 us-075-P02 us-076-P01
us-077-P01 us-079-P01 us-080-P01 us-080-P02 us-081-P01 us-081-P02 us-082-P01 us-083-P01
us-083-P02 us-084-P01 us-085-P01 us-086-P01 us-088-P01 us-089-P01 us-090-P01 us-091-P01
us-092-P01 us-093-P01 us-094-P01 us-095-P01 us-096-P01

（44 筆，含 us-051-P01/us-059-P02/us-082/us-090/us-093 等有 wind gate 與 seasonal_state 的邊界筆，
複核後判定語義成立；us-059-P02 棕熊捕鮭已具 REQUIRED seasonal_state=window_open，非「無季節閘」類。）

## MISMATCH（id＋name | 矛盾處（引用現值） | 建議修正）

1. us-071-P03 Kerry Park・藍調／夜景＋Space Needle 城市燈火 | NAME 帶「夜景」但契約僅
   blue_hour_window（−4°～−8°）；無 city_night_window（−6° 民用黑暗）。深夜城市燈火最強時段
   不在判據內，白天規則不會被時間窗擋（blue hour 窗外全滅屬巧合而非語義保證）。
   → 依 city_night 既有慣例補 city_night_window（REQUIRED/MAIN、threshold_source=computed）。
2. us-076-P02 Hamilton Viewpoint・Seattle 藍調／夜景＋Elliott Bay | 同上，僅 blue_hour_window。
   → 補 city_night_window。
3. us-077-P02 Dr. Jose Rizal Park・Downtown Seattle 藍調／夜景 | 同上，僅 blue_hour_window。
   → 補 city_night_window。
4. us-074-P02 Gas Works Park・Lake Union 日落／藍調＋Seattle Skyline | NAME 承諾「日落」但
   genre=blue_hour_city 且唯一時間窗為 blue_hour_window；日落/黃金段語義無契約承載
   （blue hour 定義於日落後）。→ 補 sunset/golden 窗或改名去「日落」。
5. us-078-P03 Myrtle Edwards・Puget Sound 日落／藍調海灣景 | 同上：NAME「日落／藍調」vs 僅
   blue_hour_window。→ 補 sunset 窗或改語義拆分。
6. us-087-P01 Hurricane Ridge・Olympic Mountains 山岳層次／雲海 | NAME 帶「雲海」但契約是
   層次山景門檻（cloud_cover_mid between 30–60 是山腰雲帶判據）；無 LCL/雲底條件
   （雲海語義 = 雲底低於視點，LCL ≤ DEM−200 class）。雲海項永遠不會被正確判別。
   → 移除名稱「雲海」或另立真雲海條件。
7. us-057-P01 Arctic Circle Wayside・北極圈標誌地標照（lat 66.6°N） | 高緯 >55°N 全日題材
   缺 light_window——同模板姊妹筆 us-055-P01/P02、us-061-P01/P02 均已由 CL-DATA-12 batch f
   補上，唯本筆遺漏（家族不一致）。→ 補 light_window（civil，sun elevation > −6°）。
8. us-051-P02 Nugget Falls・瀑布＋冰河湖谷景觀（lat 58.4°N） | 高緯 overcast_soft 全日題材
   缺 light_window；batch f 修正明言適用「高緯度全日題材」，本筆屬同語義類但未涵蓋。
   → 補 light_window（或記錄 batch f 範圍裁決為僅限 landscape 類）。

## OBSERVATION（分類級決策，建議 owner/manager 裁定一次後整批套用）

- 高緯（>55°N）reflection 類無 light_window：us-051-P01（58.4N）、us-062-P01（61.4N）、
  us-069-P01（60.2N）。batch f 只補了全日 landscape 類；reflection 是否視為全日題材需統一裁定。
- us-052-P02 Homer Spit・港灣船隻／海濱店舖街景 | genre=mountain_view，條件 rationale 全文
  以「層次山景」撰寫（AOD 0.6/中雲帶判據），與街景/船隻主體不匹配。天氣門檻無害但語義錯置；
  極座標點無山景視角宣稱，屬模板錯置而非功能矛盾。→ 換模板或改名。

## MINOR（語義空轉，建議併入鄰近票）

- us-055-P01（礦場建築）、us-057-P01（北極圈標誌）、us-061-P02（WWII 碉堡）帶
  landform_present（人工主體）。其 rationale 明載「主體存在性由機會定義聲明、非即時評估、
  propagate_unknown 保底」，故無錯誤否決風險，僅屬 taxonomy 的語義空欄。已知類別，
  不影響 verdict，併入下次觸碰這些契約的票一併清理即可。

## 明確排除（已修/誤判防線）

- batch g 已修的低雲 threshold=null 類：本批次 0 筆 REQUIRED 數值條件 threshold=null。
- 反射/湖面類（us-051-P01、062、069、082、090、093）均有 REQUIRED wind_speed_10m ≤2 +
  water_surface_state，非「reflection 無風閘」類。
- us-083-P01「Sunrise・日出光照」已具 REQUIRED MAIN sunrise_time_window（地名雙關，
  語義正確）；us-084-P01 Tipsoo Lake 掛 sunrise 模板但景點即 Sunrise 區、名稱無時間承諾，
  屬模板選擇而非矛盾（註：長期可考慮重命名以避免與題材混淆）。
