# CHALLENGER-15 — 全題材條件正確性總審計（data/v2/templates/ + 契約抽樣）

日期：2026-11-15。基準：origin/main 7627967bc。審計對象：`data/v2/templates/` 16 檔（14 題材模板 + general + metric-vocabulary），對照 `data/v2/opportunities/` 705 契約（22 個 genre_template，690 機會）與 `data/v2/evaluations/bundle-20261115T051058Z.json`（460 景點/690 機會/168h）實證。接續 CL-DATA-71「琉璃光缺雲高條件」同類問題全面清查。

評估層語義（packages/core-v2/tools/evaluate_batch.py，實測確認）：role=REQUIRED FAIL→該小時 UNFAVORABLE；REQUIRED/QUALITY 之 UNKNOWN→NOT_EVALUABLE（fail-closed）；QUALITY 永不否決；condition_tier 不參與否決（role 才是閘）。日判 = 該條件自身逐小時判定聚合（CL-DATA-56 語義）。

問題分級：**A=致命缺決勝條件/條件反向**、**B=閾值可疑**、**C=小疵（文案/簿記/漂移）**。

總計：問題 43 項 — A 級（致命缺決勝條件/條件反向/無源決勝）14、B 級（閾值可疑）8、C 級（小疵）21（詳見各節與末段票單）。

---

## 1. cloud_sea 雲海（模板 1 檔；契約 50 處）

**現狀**：模板條件最完整的一族——light_window（民用光線，owner CL-DATA-11 裁定）+ RH925≥85 + RH850≥55 + lcl_height<viewpoint−200 + 低雲≥60 + AOD≤0.4 + 視點能見度≥1km，QUALITY 逆溫蓋 ΔT≥0、850風<12。
**實證**：74 天 GUIDANCE_SATISFIED / 326 UNFAVORABLE；抽 tw-165/tw-022/tw-023/tw-134 滿意日逐條檢查，判定與物理一致；ΔT FAIL（318/328）未否決滿意日（52 天帶 ΔT FAIL 仍滿意）——MODIFIER 語義正確。
**問題**：
- **A1**｜同類 CL-DATA-71 缺雲高共 6 處：tw-035-P06（六十石山）、tw-047-P01（喜多麗）、tw-049-P03（桃山）、tw-082-P09（鯉魚潭）、tw-086-P01（淡江大橋霧景）、us-020-P02（紅木林霧）缺 lcl_height_m_agl；其中 tw-019-P04、tw-040-P04 另缺 RH925/RH850、tw-024-P02（祝山）缺 AOD+visibility、tw-082/tw-086/us-020 連 cloud_cover_low 或 RH850 也缺。**根因**：這 6 處 camera_contexts.altitude_m=null——海拔未錄，lcl 閾值無從計算。沒有雲高門檻的雲海/霧海題材會把「濕但雲在頭上」誤判為可拍。
- **B1**｜tw-023-P03（頂石棹）lcl 閾值 1170 已寫死但 altitude_m=null——閾值與情境欄不同步（換算根據不可稽）。
- **C1**｜tw-086-P01（霧中橋）、us-020-P02（林中霧）實為「霧景」非雲海俯視，硬套 cloud_sea 低雲≥60 語義待第二輪細化（desc 自承 V1 骨架）。
**修正建議**：補 6 處 altitude_m（zh.wikipedia/官方：六十石山約 900m、桃山步道口—以實測 GPS 為準、鯉魚潭 750、淡江觀景點 60、Lady Bird Johnson Grove 300m 級），恢復 lcl=viewpoint−200 運算式；tw-019/tw-040 補齊 RH 對；tw-024 補 AOD/visibility；tw-023 同步 altitude_m=1370（與閾值 1170+200 一致）。

## 2. city_night 城市夜景（51 處）＋夜間琉璃光子題材

**現狀**：模板 T1 總雲≤30、T2 能見度≥10km、T3 雨量<0.2、T4 AOD≤0.5(MODIFIER)；50/51 契約自帶 city_night_window（評估層另有 EVALGATE 自動補窗）。
**問題**：
- **A2（本票核心同類問題的最大一簇）**｜夜間琉璃光 5 處——tw-128（墨硯山）、tw-145（東華聖宮）、tw-148（中寮山）、tw-163（半天岩）、tw-179（碧山巖）——直接套 city_night 模板：**cloud_cover_total≤30% 是反條件**。琉璃光的成景前提是視點「下方」有低雲/輻射霧覆蓋城市光域（低雲量應該要高），總雲≤30% + 能見度≥10km（日間語義）把雲海／霧層本身否決——條件互斥：low≥60 之時 total 必≥low，兩者不可同時成立 → 琉璃光永遠不成立，只剩天際線夜景。對照日間藍調琉璃光 tw-020-P03/tw-023-P03（blue_hour_city 題材）已正確使用 RH 對+lcl+低雲≥60——證明正確語義在 repo 已存在，夜間 5 處是複製殘留。**修正**：改掛「夜間琉璃光」變體＝city_night_window + lcl_height<viewpoint−200 + cloud_cover_low≥60 + RH925≥85 + RH850≥55 + 視點能見度≥1km（日間同構、窗換夜窗）；並補 4 處 altitude_m（tw-145/148/163/179 均 null，同 A1 根因）。
- **B2**｜AOD 夜間判據矛盾仍在：42 處 role=REQUIRED（夜間 CAMS 常缺值→UNKNOWN→NOT_EVALUABLE，aod 全 bundle UNKNOWN 率 34%）vs 6 處 QUALITY——同題材相反語義（challenger round15 jp-018/jp-020 已指）。建議全族收斂為 MODIFIER（模板 T4 即如此設計）。
- **C2**｜city_night_window 用了 54 處但不在 metric-vocabulary（36 條）；temperature_2m（6）、daylight_window（1）同缺。
**實證**：156 天滿意/251 否決；滿意日均為「夜窗+晴+能見度佳」——天際線語義本身無荒謬案例；問題集中在琉璃光子題材。

## 3. night_sky 星空/銀河（35 處）

**現狀**：天文黑暗≤−18°、月照≤50%、總雲≤20%、AOD≤0.3、銀河核心≥20°、月高<0、月核距≥40°、月照度代理≤0.15。
**問題**：
- **A3（條件重疊→物理荒謬實錘）**｜月照≤50%（B2）對「月亮在地平線下」的小時照樣否決。實證：jp-021-P02（西穗高口）2026-11-19 02:00–05:00，月高 −18°~−50°、月照度代理=0.0、天文黑暗 PASS，小時仍 UNFAVORABLE——月照 0.52–0.63>0.5 觸發 B2。**月亮在地平線下不會照亮天空**，B2 須加「僅月出時啟用」閘（與 M3 同語義）。
- **A4**｜M2/M3/M5 的「交替」語義（rationale 明言 M2 未成立時改由 M3）在評估層**未實作**——三條 REQUIRED 平鋪 AND：月出 5°+月核距 86.7° 時 M2 照樣 FAIL（fallback M3 PASS 亦不被採計）。建議在 evaluator 落實 activate-when 交替，或改單一 moon_illuminance_proxy≤0.15 一條（月亮在地平線下時代理=0 自動 PASS，涵蓋全部語義）。
- **C3**｜moon_target_separation_deg 以 999° 哨兵代表月落→恆 PASS（264/304 PASS）：永真條件，建議月落時直接跳過而非發 PASS。
- **C4**｜blue_tears 4 處整組複製本模板：rationale 殘留「星空是長曝主體」「離銀河核心 ≥40°」——藍眼淚無銀河目標，月核距條件對淚題物理無關，應刪或改目標。
**閾值**：雲≤20、AOD≤0.3、核心≥20° 合理；B4 AOD 夜間 22:00–01:00 常見 UNKNOWN（CAMS 覆蓋縫）→ 晴夜小時被 NOT_EVALUABLE 阻斷，建議夜間降 MODIFIER 或以日間最後值標 STALE。
**無降水條件**（C5，小疵）：長曝對落雨/雪敏感，建議補 precipitation<0.2。

## 4. sunset 日落（98 處）

**問題**：
- **A5**｜T3 cloud_cover_mid_and_high 20–70% role=**REQUIRED**（模板＋98 契約全數）——rationale 自己寫「20–70% 區間加分」，卻用 REQUIRED 否決。實證：**167 天僅因此條件被否決**（低雲/雨/AOD/日落窗全過、全晴日）；sunset 族 685 UNFAVORABLE vs 89 滿意，全題材最悽慘比例。日出同構條件（T3）是 QUALITY——兩模板不一致，sunset 是錯的那個。修正：role→QUALITY（tier MODIFIER 已正確）。
- **B3**｜光向（light_direction，CL-DATA-13 月弧機制）只有 2 處使用——對位型日落（兩塔對位、橋洞對位）缺光向弧等於沒有季節語義；建議對位主體普遍補 sectors。
- **C6**｜sunset_window=日落±40min：海平線合理；山嶺受地形遮擋（模板自承待地形遮擋角參數）——掛追蹤即可。
**實證**：無其他荒謬案例；AOD≤0.6 白晝值充足。

## 5. sunrise 日出（59 處）

**現狀**：日出±40min、低雲≤55（上色主角=塊狀雲）、中高雲 20–70（QUALITY）、雨<0.3。**實證**：275 滿意/185 否決——健康族。
**問題**：
- **C7**｜tw-024-P02 等少數契約把 sunrise_time_window+RH 對+lcl 混掛（雲海疊加判據）——模板自述「疊加判據不在此模板內（activate_when/merge 各自掛）」，但 activate_when 機制未實作，實際是平鋪 AND（祝山日出雲海＝兩族全 AND，窗重疊極窄）。建議落實 activate_when。
- **C8**｜地形遮擋角（山嶺實際見日）缺參數——與 C6 同源。

## 6. mountain_view 山景層次（76 處）

**問題**：
- **B4**｜T2 中雲 30–60% role=REQUIRED：「完全無雲＝沒有層次」把大晴日 360° 山景硬否決（challenger round15 jp-021-c3 已判成立；實證 cloud_cover_mid FAIL 336/696，mountain_view 528 UNFAV/72 滿意）。層次是品質非存亡：建議降 QUALITY 或改「≤60 且 ≥30 加分」。
- **C9**｜tw-016-P01 等 1 處缺 AOD（模板 T1）；sunset_window 74 處 vs 模板 QUALITY——一致。

## 7. overlook 俯瞰（97 處）

**現狀**：能見度≥min(視距,24km)（GFS 飽和誠實標註）、AOD≤0.4、低雲≤30（owner 10-26 修正：主體在地面，擋視線的是低雲）、雨<0.2、light_window 92/97。
**問題**：
- **A6（機械缺值）**｜14 處 cloud_cover_low threshold=null（us-001/002/006/007/009/010/011-P02/013-P01/013-P02/026-P02/038/041/114/116）：owner 修正只改了 rationale 沒落 threshold→compare() INVALID_THRESHOLD→UNKNOWN→REQUIRED→條件全過也只到 NOT_EVALUABLE。修正：14 處補 30。
- **C10**｜模板 V3 threshold=null 未與 owner 修正同步（83 處契約已帶 30）——模板該更新為 ≤30。
- **C11**｜5 處缺 light_window（sunset_window/seasonal 代替）——審計基準「自然光題材一律光線窗」漏網。

## 8. reflection 倒影（50 處）

**問題**：
- **A7（資料可得性→題材死亡）**｜water_surface_state：47/50 契約 role=REQUIRED（模板亦 REQUIRED），無觀測源→每小時 UNKNOWN→全日 NOT_EVALUABLE。全 bundle reflection 僅 5 天滿意——恰為 CL-DATA-58 降級為 QUALITY 的 3 處（us-132/us-143 等）。同一 CL-DATA-58 修了 3 處沒修 47 處；模板 rationale 自己說「屬純提示、不否決」與 role=REQUIRED 自相矛盾。修正：47 處+模板全面降 QUALITY（結冰風險另以警語層處理）。
- **C12**｜模板 T4（雲量 20–60 加分）role=REQUIRED+tier=MODIFIER 標籤矛盾（契約僅 2 處沿襲）——模板改 QUALITY。
- **閾值**：風≤2（鏡面/微漣分界）合理；降水<0.2 合理。

## 9. seasonal_plant 花季（38 處）

**問題**：
- **A8（決勝條件無資料源→永遠未知）**｜seasonal_state REQUIRED（全 repo 95 處）在評估層被硬編碼為 NO_SOURCE_METRICS→UNKNOWN 764/764 次——**seasonal-calendar.json 明明存在**（typical_window+current_season，含金針花 08-25~09-30 等）卻沒被讀。花季題材全 bundle 0 滿意日：好天氣日全數 NOT_EVALUABLE（實證 tw-116 等 247 天「季節 UNKNOWN+其餘全過」）。這是确定性日期-區間判斷，根本不需 live 資料源。修正：evaluator 讀 seasonal-calendar（current_season 優先、typical 墊底），window_open/window_closed 可計算即計算。
- **閾值**：雨<0.2、風<5 合理。

## 10. blue_hour_city 藍調城市（32 處）

**現狀**：藍調窗（−4°~−8°）、總雲≤70、AOD≤0.5、雨<0.2。金龍山/頂石棹兩契約正確改掛 RH 對+lcl+低雲≥60（見 A2）。
**問題**：
- **B5**｜模板 T2 總雲≤70 與低雲形成中的琉璃光子題材近衝突（low≥60+中高>10 即破 70）——子題材契約已棄用 T2 是對的，模板應拆分或把 T2 降級註明「僅天際線藍調」。
- **C13**｜2 處缺 cloud_cover_total（tw-020-P03/tw-023-P03 屬子題材正當省略；其餘對齊）。
**實證**：74 滿意/146 否決——無荒謬案例。

## 11. overcast_soft 柔光（18 處）

**現狀**：總雲≥70、雨<0.5（柔光刻意放寬）、風<5（MODIFIER）、light_window 18 處。**實證**：84 滿意/60 否決——健康族。**無 A 級問題**；小疵：O3 標 REQUIRED+MODIFIER 同 C12 式矛盾（role REQUIRED 才是閘，文字說不否決——現況確實不否決，僅標籤易誤讀）。

## 12. golden_hour 金黃時刻（6 處）

**問題**：
- **B6**｜T2 總雲≤50 REQUIRED：金黃時刻的彩霞主角恰是雲，≤50 會否掉「分散雲+火燒雲」的最佳日；全陰否決才必要。建議改「≤80 或以中高雲 20–70 加分」同構。
- **C14**｜jp-012/jp-018/tw-072-P02 缺 cloud_cover_total；jp-018-tw 等 2 處缺 light_window（有 golden_hour_window 覆窗，尚可）。

## 13. waterfall 瀑布（13 處）

**問題**：
- **A9（決勝條件無實作→題材死亡）**｜river_flow_state REQUIRED（13/13）：vocabulary 有條目（72h 雨量映射 low/mid/high），但 METRIC_FIELDS 無此 metric、open-meteo 批次未取 72h 欄→UNKNOWN 103/103→全 bundle waterfall 0 滿意（29 NOT_EVALUABLE/74 UNFAVORABLE）。修正：橋接 72h 累積雨量→三級映射（<5/5–40/>40mm）。
- **C15**｜golden_hour_window 12/13（1 處缺）。

## 14. geological_landform 地景（64 處）

**現狀**：landform_present（owner 宣告恆 PASS）、雨≤0.3、golden_hour(BONUS)、AOD(BONUS)、light_window 62/64。
**問題**：
- **A10**｜場域依存型地景缺決勝條件：Upper Antelope（砂岩光柱=正午現象，golden_hour BONUS 方向還相反）、Rialto Beach Hole-in-the-Wall（**潮汐門檻缺**——低潮才可進）、及多處需導覽/入場時段——venue_open_window 全族僅 1 處。地景「永遠在」不等於「今天能拍」。修正：依點補 venue_open_window／潮汐窗（ tidal 機制見 19 節）。
- **B7**｜無任何能見度/雲量條件→512 天中 468 滿意（91%）：霧天伸手不見五指也滿意。遠景型地景建議掛 general 的 visibility≥view_scale；近景型至少補降水外的視障判據。
- **C16**｜us-086 降水閾 0.3 vs 模板 lte vs 他族 0.2——有 rationale 出處，列小疵觀察。

## 15. blue_tears 藍眼淚（4 處）

**現狀**：季節窗 04-01–09-30、天文黑暗、月判據組（複製 night_sky）、雲≤20、AOD≤0.3、noctiluca_concentration（REQUIRED 無源→誠實 fail-closed）、nearshore_surf_state（BONUS 無源）。
**問題**：
- **A11**｜決勝的夜光蟲濃度無資料源（馬管處官方口徑：或然率現象）→ 題材永遠 NOT_EVALUABLE——**誠實但無偵測力**。owner 已知情（CL-DATA-25/20 口徑），列為「已知 fail-closed」；建議可保留但 UI 應以「或然率+天氣條件」雙軌呈現，否則該 4 點形同永久失效。
- **B8**｜月判據整組複製（見 C4/A3/A4）：夜光蟲發光最怕月光直射，關鍵是月高×月照度（M5），月照≤50%（B2）對「月落但滿月夜」同樣誤否決（同 A3 物理）。
- **C17**｜rain/降水缺：小雨不影響淚反而增加擾動；可不補，列觀察。

## 16. snow_ice / snow_ice_night（7 處）

**問題**：
- **A12**｜缺積雪/冰存續決勝條件：無溫度、無近期降雪——jp-017（兼六園雪吊）靠季節窗勉強覆蓋，jp-047 等冰瀑/樹冰類「零下才有」的物理完全沒判據。建議補 temperature_2m≤X（依題材 0~−5°C provisional）或前 72h 降雪量。
- **C18**｜wind≤15 極鬆（seasonal_plant 是 5）——雪景風影響較小可接受，但需 rationale 出處。
- **實證**：47 UNFAV/0 滿意（11 月非窗＋seasonal UNKNOWN）——季節窗接上後（A8）才會有訊號。

## 17. volcanic_glow（1 處 us-161）

**問題**：volcanic_activity REQUIRED 無源（USGS HVO 未連線）→誠實 fail-closed（rationale 明載「系統尚未連線」）——已知狀態，同 A11 類；建議接 HVO feed（https://www.usgs.gov/volcanoes/kilauea）或降 BONUS。C19：rationale 是 city_night「城市燈火」複製殘留。雲≤30/能見度≥10/夜窗語義正確。

## 18. drift_ice（1）/ tidal（2）— legacy 骨架

- **A13**｜jp-041 知床流氷：legacy_drift_ice 單條 UNKNOWN 8/8→全 NOT_EVALUABLE。決勝＝海冰邊緣接岸（海溫≤−1.5°C＋向岸風＋季節 1–3 月）——全部缺。
- **A14**｜tw-059 摩西分海/tw-078 建功嶼：**決勝=潮汐**（退潮窗才露步道），legacy 條件無源無窗→全 NOT_EVALUABLE。潮汐是可計算的（天文潮，世界各國 NOAA/BSH 模式表公開）；短期 fallback：掛 venue/tidal 常數窗（官方公告的乾潮±時窗）。
- 這 3 處是「佔位不能拍」的示範點——建議移出推薦池或限期補條件。

## 19. general（1 處 jp-030-P99）

G1 能見度≥view_scale（3/5/8 分級語義自洽：近景只排觀點起霧、遠景保主體可辨識；誠實標 GFS 24km 上限鈍化）、G2 雨<0.5（一般題材刻意寬）、G3 RH925≤95（霧代理，誠實標非地面觀測）、G4 light_window。**無 A 級**；B 級僅 G3 的代理性偏粗（2m RH 更直接）——可接受。

## 20. metric-vocabulary 簿記（跨題材）

- **C20**｜缺條目：city_night_window（54 用）、temperature_2m（6）、noctiluca_concentration（4）、nearshore_surf_state（4）、volcanic_activity（1）、daylight_window（1）、light_direction（2）、legacy_*（4）。
- **C21**｜現行 22 genre 中 8 個無模板檔（snow_ice、snow_ice_night、blue_tears、volcanic_glow、drift_ice、tidal、NONE×2）——條件語義散在契約、無 layering parity 可比對。建議至少為 blue_tears/snow_ice/volcanic_glow 補模板。

---

## 抽樣實證清單（實資料逐日驗證）

| 題材 | 樣本 | 結果 |
|---|---|---|
| night_sky | jp-021-P02 11/18–21 逐小時 | **荒謬實錘**：月下 −18°~−50°、月照度代理 0、仍因月照 0.52–0.81 否決（A3） |
| sunset | tw-188/tw-030/us-118 等 | **167 天僅因中高雲非 20–70 被否決**（全晴日）（A5） |
| cloud_sea | tw-165/tw-022/tw-023/tw-134 滿意日 | 判定合理；ΔT MODIFIER 不否決（語義正確） |
| seasonal_plant | tw-116 等 247 天 | 季節 UNKNOWN＋天氣全過→NOT_EVALUABLE，0 滿意（A8） |
| reflection | us-132/us-143 vs 其餘 47 處 | 3 處 QUALITY 後有 5 滿意日；47 處 REQUIRED 全死（A7） |
| waterfall | 全族 | 0 滿意；flow UNKNOWN 103/103（A9） |
| blue_tears | tw-121~124 | 全 UNFAVORABLE；決勝濃度 fail-closed（A11，已知） |
| geological | 全族 | 91% 滿意；霧/場域/潮汐無判據（B7/A10） |
| drift_ice/tidal | 3 處 | 全 NOT_EVALUABLE legacy（A13/A14） |
| city_night | 全族 | 天際線語義正常；琉璃光 5 處條件反向（A2） |
| overlook | 全族 | 14 處 threshold=null 機械性 NOT_EVALUABLE（A6） |
| mountain_view | 全族 | 中雲 30–60 REQUIRED 否決近半（B4） |

南北半球/緯度語義：日出日落/晨昏/月/銀河窗皆由座標計算，US（含夏威夷/阿拉斯加）與 JP/TW 無誤；季節窗為 owner 逐點維護（皆北半球點位），無反向案例。海邊/高山/城市語義：visibility 分級 1/3/5/8/10km 與題材尺度對位（general G1 rationale 明載），無張冠李戴案例。

## 修正工作清單（票單）

1. **CL-COND-A2（最高優先）**：夜間琉璃光 5 契約（tw-128/145/148/163/179）改「夜間琉璃光」變體條件組（夜窗+lcl+低雲≥60+RH 對+視點 vis≥1km）＋補 4 處 altitude_m。
2. **CL-COND-A8**：evaluator 接 seasonal-calendar.json（current_season>typical），seasonal_state 可計算即計算（95 契約受益）。
3. **CL-COND-A5**：sunset T3（98 契約+模板）role→QUALITY；比照 sunrise T3。
4. **CL-COND-A3+A4**：night_sky 月判據——B2 加「月出才啟用」或刪除；實作 M2/M3 交替或統一改 moon_illuminance_proxy≤0.15；M3 月落哨兵 999 不發 PASS。
5. **CL-COND-A7**：reflection water_surface_state 47 契約+模板 REQUIRED→QUALITY（CL-DATA-58 收尾）。
6. **CL-COND-A1**：cloud_sea 6 處補 altitude_m+缺漏 MAIN 條件（含 tw-024 祝山 AOD/vis、tw-019/tw-040 RH 對）；tw-023 同步 altitude_m。
7. **CL-COND-A6**：overlook 14 處 cloud_cover_low 補 30；模板 V3 同步 ≤30。
8. **CL-COND-A9**：waterfall river_flow_state 橋接 72h 雨量映射（METRIC_FIELDS+批次欄位）。
9. **CL-COND-A10+B7**：geological 依點補 venue_open_window/潮汐/visibility（Antelope 光柱改午窗 BONUS；Rialto 潮汐）。
10. **CL-COND-A12**：snow_ice 補溫度/降雪判據。
11. **CL-COND-A13/A14**：drift_ice/tidal 補真實條件或移出推薦池。
12. **CL-COND-A11**：blue_tears 決勝濃度維持 fail-closed 但 UI 雙軌呈現；月判據去銀河目標殘留。
13. **CL-COND-B2**：city_night AOD 42 處 REQUIRED→MODIFIER 收斂。
14. **CL-COND-B4**：mountain_view 中雲 30–60 降 QUALITY（76 契約+模板）。
15. **CL-COND-B6**：golden_hour 雲量≤50 放寬/改加分。
16. **CL-COND-B5**：blue_hour_city 模板拆分子題材語義。
17. **CL-COND-B1**：tw-023 閾值-altitude 同步；tw-086/us-020 霧景語義重分類。
18. **CL-COND-C2/C20/C21**：vocabulary 補 8 metric；補 3 題材模板；C 級文案殘留（C4/C19 等）隨票清。

---
審計執行：CHALLENGER-15（分支 task/CHALLENGER-15）。實證資料：bundle-20261115T051058Z（place_count=460/opportunity_count=690/fetch_failures=0）。
