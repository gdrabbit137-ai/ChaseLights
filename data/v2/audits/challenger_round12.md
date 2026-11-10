# Challenger Round12 — us-147..158（CL-DATA-53 剩餘批次，知識隔離）

日期：2026-11-10。資料來源：線上 `https://chaselights.app/apps/web-v2/opportunity-contracts.json` 與 `evaluations-latest.json`（13 個機會契約 / 12 景點）。方法：對每個機會提出 ≥3 個候選質疑，逐一以物理約束（太陽仰角/方位、暮光、季節封閉、潮汐、季節語意、緯度天象、時段合理性）與權威來源（NPS/BLM/州/NOAA/time.is）驗證。僅真缺陷判「成立」。

**成立質疑：4 項**（us-147-P01 ×1、us-152-P01 ×1、us-154-P01 ×2）。其餘 41 個候選驗證為不成立或已被警語/UNKNOWN 機制覆蓋。

---

## us-147 斑馬狹縫峽谷（Zebra Slot, Grand Staircase–Escalante, 37.661/-111.421, America/Denver）

**卡片摘錄**：P01 geological_landform「斑馬狹縫波紋牆」——「寬僅一臂的狹縫內橙白條紋如斑馬紋（Escalante；狹縫內常年積水段需涉水——access 資訊性）」。判據：landform_present / precip ≤0.3 / golden_hour_window BONUS / AOD ≤0.4 BONUS / light_window（civil，> −6°）。評估 11-10、11-11 均 GUIDANCE_SATISFIED，good_hours 07:00–16:45。

1. **候選**：golden_hour_window BONUS 對狹縫題材物理空窗——縫寬僅一臂，太陽仰角 <15°（golden hour 定義域）時直射光根本進不了縫內；斑馬紋需斜上/頂光束，實拍社群公認最佳在上午至中午（8:00–14:00），golden hour 反而是縫內最暗時段。**驗證**：explorumentary 實拍記錄「early morning light (8:00 a.m.) was perfect… mid-morning good」；bearfoottheory/vanlifebydesign 皆指 late morning–early afternoon 為條紋最佳光。與模板理由「低角度直射光強化岩層紋理」直接矛盾——此理由對開放地景成立、對狹縫不成立。**判定：成立（小缺陷：模板理由錯配，加分項在該點為無效訊號）**。證據：https://www.explorumentary.com/adventure-blog/zebra-slot-and-devils-garden-a-weekend-in-grand-staircase-escalante ；https://bearfoottheory.com/escalante-hiking/
2. **候選**：Hole-in-the-Rock Road 冬季/雨後沖毀，11 月是否可達。**驗證**：BLM/多源確認土路乾季 2WD 可達、雨後泥濘難行，無固定季節封閉；卡片 desc 已標「積水段需涉水——access 資訊性」，且 SHOOT 條件 precip ≤0.3 mm/h 排除降雨時拍攝。**判定：不成立（已被警語覆蓋）**。證據：https://vanlifebydesign.com/zebra-slot-canyon-utah/
3. **候選**：11 月 good_hours 07:00–16:45 是否落在夜間/暮光外。**驗證**：37.66°N 11 月 10 日日出約 06:57、日落約 17:09（民用暮光 06:25–17:40 量級），07:00–16:45 全程太陽在地平線上；light_window PARTIAL 10 小時與 civil 光窗量級一致。**判定：不成立（物理一致）**。
4. **候選**：無上游集水區閃洪判據（狹縫致命風險）。**驗證**： shooting 時降雨 ≤0.3 mm/h 已排除現場降水；上游遠端降雨為安全警示層級，desc 已資訊性提示涉水。**判定：不成立（guidance 範疇；安全警語建議未來加註）**。

## us-148 膨潤土彩帶丘陵（Bentonite Hills, Capitol Reef Cathedral Valley, 38.3611/-111.1278, America/Denver）

**卡片摘錄**：「火山灰黏土層帶狀棕紅紫灰綠圓丘（NPS；雨天黏土路不通且丘面禁踩踏痕跡保育——access 不計分）」。判據同通用 geological_landform 模板。

1. **候選**：Cathedral Valley 道路冬季不剷雪、雨後不可通行，11 月 access 是否實質關閉而卡片未反映。**驗證**：NPS「Roads in this area are maintained infrequently and are not plowed in winter… bentonite clay becomes impassable when wet」——與卡片 desc「雨天黏土路不通」完全對應。**判定：不成立（警語已覆蓋；access 不計分為系統設計）**。證據：https://www.nps.gov/thingstodo/hike-cathedral-valley.htm
2. **候選**：golden_hour_window BONUS 對圓潤黏土丘是否物理成立。**驗證**：開放坡面低角度光確實強化彩帶色差（與狹縫不同情境），物理無矛盾。**判定：不成立**。
3. **候選**：座標 38.3611/-111.1278 是否落在 Bentonite Hills 實際位置。**驗證**：Bentonite Hills 位 Cathedral Valley 西南緣（~38.36/-111.13），座標吻合。**判定：不成立**。
4. **候選**：11 月 good_hours 07:00–16:40 光窗合理性。**驗證**：同 us-147 緯度帶 civil 光窗量級一致。**判定：不成立**。

## us-149 約書亞樹國家公園（Keys View, 33.8928/-116.1888, America/Los_Angeles）

### P01 night_sky「約書亞樹銀河夜」

1. **候選**：11 月銀河核心已入晝側，≥10° 核心判據是否會產生假陽性。**驗證**：11 月核心夜間僅短暫低懸 SW 後即落（50°N 已不可見；34°N 僅黃昏極短窗），評估實輸出 11-09/11-10 全 UNFAVORABLE、核心判據 FAIL/PARTIAL——判據與天文一致、無假陽性。**判定：不成立**。證據：https://www.photographytalk.com/big-bend-stargazing/
2. **候選**：Keys View 夜間是否封閉（園區夜間 access）。**驗證**：NPS FAQ「The park is open 24 hours a day… gates are left open at night」，Keys View 為官方列名觀星/日落點。**判定：不成立**。證據：https://home.nps.gov/jotr/faqs.htm
3. **候選**：tz America/Los_Angeles（11 月 UTC-8）是否正確。**驗證**：Joshua Tree 屬加州，太平洋時區正確。**判定：不成立**。
4. **候選**：月判據三件套（illum ≤0.5 / separation ≥40° / proxy ≤0.15）自承 provisional 卻 REQUIRED。**驗證**：round8 已對同構判據提過系統性疑慮（us-018-P02）；本輪以知識隔離立場確認行為一致且評估誠實輸出 UNFAVORABLE，非本批新缺陷。**判定：不成立（既有議題，非本點缺陷）**。

### P02 seasonal_plant「約書亞樹花枝」

1. **候選**：desc「罕見晚春花序」「2–4月花期」與 NPS 官方 Yucca brevifolia 花期 4–5 月是否矛盾。**驗證**：NPS 物種頁列 Joshua Tree 開花 April–May；FAQ 載低海拔 2 月起、高海拔可到 6 月，年度浮動大——「2–4月」早端可成立但 4–5 月為主窗；P02 由 seasonal_state（例年窗×實況窗）動態判定，非寫死月份。**判定：不成立（desc 月份措辭略早端，機制已動態處理；建議文案對齊 4–5 月）**。證據：https://www.nps.gov/jotr/learn/nature/keys-view.htm
2. **候選**：11 月評估 seasonal_state=UNKNOWN 是否為硬湊。**驗證**：非花期 UNKNOWN 誠實回報、全日 UNFAVORABLE，符合 limitations 聲明。**判定：不成立**。
3. **候選**：light_window 夜間 FAIL 是否正確。**驗證**：11-09 01 時樣本 FAIL、白天 PARTIAL——可見光題材不落夜間，正確。**判定：不成立**。

## us-150 特羅納石灰華石塔（Trona Pinnacles, 35.6611/-117.3453, America/Los_Angeles）

1. **候選**：座標偏移——BLM/Wikipedia 主區座標 35.617/-117.370，卡片 35.6611/-117.3453 偏北東約 4.9 km。**驗證**：BLM「dirt road RM143…5.0-mile from SR 178」與 Wikipedia 座標一致；卡片偏移約一個格點尺度，對天氣網格與方位計算影響輕微（coordinate_source=camera_context_provisional 已自標 provisional）。**判定：不成立（座標有 ~5km 偏移，建議校正但不構成行為缺陷）**。證據：https://www.blm.gov/visit/trona-pinnacles ；https://en.wikipedia.org/wiki/Trona_Pinnacles
2. **候選**：冬季大雨後土路封閉未反映。**驗證**：BLM「road may be closed during the winter months after a heavy rain」；卡片 desc 標「土路最後 3.5 英里——access 資訊性」（實為 5.0 mi，路長敘述略短，屬文案誤差非判據缺陷）。**判定：不成立（已覆蓋）**。
3. **候選**：light_window/golden hour 對開放地景的物理適配。**驗證**：開放石塔群低角度光成立。**判定：不成立**。
4. **候選**：11 月光窗（good_hours 自 06:00 起）。**驗證**：35.66°N 11 月 civil twilight 起於約 05:55，06:00 合理。**判定：不成立**。

## us-151 拉森火山（彩繪沙丘火山口, Lassen Painted Dunes, 40.5264/-121.2722, America/Los_Angeles）

**卡片摘錄**：「氧化火山灰彩層鋪展在 Cinder Cone 火山口旁（NPS；Butte Lake 區夏季開放——access 資訊性）」。評估 11-10/11-11 GUIDANCE_SATISFIED。

1. **候選**：11 月 Butte Lake 區實際季節封閉——NPS 明載 Butte Lake Road（FR-32N21）冬季不維護、「vehicle travel is not advised when snow covers the road (approx. November–April)」、可閘門關閉；公園主幹線 11 月中下旬封閉（曾早至 10-18）。卡片僅「夏季開放」一筆警語，11 月 SATISFIED 天數對使用者有誤導風險。**驗證**：NPS Getting Around/Winter 頁確認。**判定：不成立（警語已覆蓋；但警語強度弱於實際：11 月起道路常態閘門關閉，建議加註「November–April 不維護/可能閘門關閉」）**。證據：https://www.nps.gov/lavo/planyourvisit/gettingaround.htm ；https://www.nps.gov/lavo/planyourvisit/fall.htm
2. **候選**：visibility 判據 24 km 上限自承鈍化。**驗證**：理由欄自我揭露並由 AOD 承接，非隱藏缺陷。**判定：不成立**。
3. **候選**：cloud_cover_low ≤30% 取代總雲量（owner 2026-10-26 修正）對俯瞰題材是否物理合理。**驗證**：低雲/霧層擋視線、高雲為構圖元素的物理區分成立。**判定：不成立**。
4. **候選**：light_window 對 40.5°N 11 月（good_hours 07:00–16:00）。**驗證**：日出約 06:45、日落約 17:00，civil 光窗覆蓋 07:00–16:00，合理。**判定：不成立**。

## us-152 愛達荷暗夜保護區（愛麗絲湖, Alice Lake Sawtooth, 43.9391/-114.9437, America/Los_Angeles）

**卡片摘錄**：「鋸齒山…冰斗湖映 El Capitan 峰（2,622 m；湖水初夏可能結冰——資訊性；IdDA 全州暗夜保護區…）」。判據：wind ≤2 / water_surface_state / precip / 雲 20–60% BONUS / light_window。

1. **候選**：**timezone_display 掛 America/Los_Angeles（UTC-8），但愛麗絲湖所在的 Sawtooth/Blaine–Custer County 屬 Mountain Time（America/Boise，11 月 MST UTC-7）**——display 時段整體偏移 1 小時，使用者在錯的鐘點赴拍。**驗證**：time.is「IANA time zone identifier for Twin Falls is America/Boise」、timeanddate Stanley/Sawtooth NRA 均 MST；49 CFR §71.9 邊界在 Salmon River 以北才轉 Pacific。**判定：成立**。證據：https://www.timeanddate.com/time/zone/@5608726 ；https://calendarhours.com/idaho-time-zone-map/
2. **候選**：11 月湖面已結冰、倒影季節性死亡而判據僅 propagate UNKNOWN。**驗證**：Alice Lake 標高 2,622 m，湖凍至初夏（Wikipedia/gpsnauticalcharts）；卡片 desc「湖水初夏可能結冰——資訊性」+ water_surface_state 誠實 UNKNOWN。**判定：不成立（已被警語覆蓋）**。證據：https://en.wikipedia.org/wiki/Alice_Lake_(Sawtooth_Wilderness)
3. **候選**：11 月步道積雪、11.6 mi 往返晨間進入不可行。**驗證**：10–4 月步道積雪（discoversawtooth/多源）；access 資訊性設計。**判定：不成立（已覆蓋；同上建議加註）**。
4. **候選**：desc 拼字「IdDA」錯誤（Idaho Dark…）。**驗證**：文字誤植，無行為影響。**判定：不成立（文案瑕疵，隨修復批次一併更正）**。

## us-153 月球火山紀念地（Craters of the Moon, 43.4169/-113.4977, America/Denver）

**卡片摘錄**：P01 night_sky「熔岩地景上的國際暗夜公園銀河（NPS；熔岩地形同時為白天題材——資訊性）」。

1. **候選**：Loop Road 11 月中旬起封閉機動車輛（mid-Nov–mid-Apr），夜間攝點是否實質不可達。**驗證**：NPS Winter 頁確認「Loop Road is typically closed for motorized travel between mid-November and mid-April」；步行/雪鞋仍可進入（遊客中心區步行可及熔岩地形），且 11-10 尚在封閉前。**判定：不成立（季節封閉屬 access 層；建議卡片加註冬季道路封閉）**。證據：https://www.nps.gov/thingstodo/craters-in-winter.htm
2. **候選**：熔岩洞管冬季關閉（11–5 月洞口積雪冰）影響白天同框題材。**驗證**：NPS 確認 caves 通常 5 月底–10 月開放；卡片把熔岩地形列為白天資訊性題材、判據僅針對夜空，不衝突。**判定：不成立**。證據：https://www.nps.gov/thingstodo/craters-caves.htm
3. **候選**：11 月核心判據假陽性。**驗證**：評估 11-10/11-11 全 UNFAVORABLE、core PARTIAL（黃昏低窗）——與 43°N 11 月天文一致。**判定：不成立**。
4. **候選**：tz America/Denver 是否正確（Idaho 多數縣 Mountain）。**驗證**：Butte County 屬 Mountain Time，正確。**判定：不成立**。證據：https://calendarhours.com/idaho-time-zone-map/

## us-154 肖肖尼瀑布（Shoshone Falls, Twin Falls, 42.7547/-114.4214, America/Los_Angeles）

**卡片摘錄**：P01 waterfall「比尼加拉更高（212 呎）的蛇河斷層瀑布，春季灌溉取水前水量最大（Twin Falls 市；夏季分流水量銳減——資訊性）」。判據：river_flow_state＝「過去 72h 累積雨量映射（<5mm low、5–40mm mid、>40mm high）」REQUIRED/MAIN。

1. **候選**：**river_flow_state 代理與實際水量脫鉤——Shoshone Falls 的水量由上游落磯山融雪 + Milner Dam（上游 24 mi）灌溉分流與 Shoshone Falls 水電取水決定，夏季近乎蒸發、秋季近乾；拍攝點當地 72h 雨量與瀑布流量幾乎無因果關係（流域為大壩調節、當地屬乾旱區，春汛時當地常無雨）。判據測不到它要判定的物理量，mid/high 窗永遠不會由真實春汛觸發。**驗證**：Twin Falls 官方「In the summer months, a portion of the river is diverted for irrigation… In the Fall… nearly dry」；Wikipedia「natural water from snowmelt in the Rockies… Milner Dam 24 miles upstream… frequently zero」——直接證實水量驅動源不在拍攝點降雨。**判定：成立（判據定義缺陷，provisional 但物理錯向）**。證據：https://www.tfid.org/309/Shoshone-Falls ；https://en.wikipedia.org/wiki/Shoshone_Falls
2. **候選**：**timezone_display 掛 America/Los_Angeles（UTC-8），Twin Falls 實為 America/Boise Mountain Time（MST UTC-7）**——顯示時段偏移 1 小時。**驗證**：time.is/timeanddate/savvytime 一致。**判定：成立**。證據：https://time.is/Twin_Falls
3. **候選**：11 月水量近枯仍列「春汛」題材是否季節錯置。**驗證**：desc 已言明春季最大/夏秋銳減；評估 river_flow_state UNKNOWN（不假陽性）、全日 UNFAVORABLE——行為誠實。**判定：不成立**。
4. **候選**：座標 42.7547/-114.4214 較瀑布實址（42.755/-114.391）偏西約 2.5 km。**驗證**：格點尺度內，影響輕微。**判定：不成立（建議校正）**。
5. **候選**：園區開放時間（Shoshone Falls Park 有收費營業時段）與光窗重疊。**驗證**：good_hours 均在日間營業時段內量級。**判定：不成立**。

## us-155 乾龜國家公園（傑佛遜堡日落, Dry Tortugas, 24.628/-82.8735, America/New_York）

1. **候選**：一日遊 15:00 離島、日落（約 17:40）不可達——sunset_window REQUIRED 與大眾交通根本衝突。**驗證**：Yankee Freedom「DEPARTURE: 3PM」；NPS camping 頁確認渡輪為日遊唯一班次、水上飛機不載宿營客；卡片判據理由自承「渡輪約 15:00 離島…日落時刻僅島上宿營者可達（honest 標註）」。**判定：不成立（已被警語誠實覆蓋）**。證據：https://www.drytortugas.com/key-west-ferry/ ；https://www.nps.gov/drto/planyourvisit/camping.htm
2. **候選**：good_hours 17:05 是否落在真實日落窗。**驗證**：24.63°N 11 月日落約 17:35–17:40 EST，±40 分窗＝約 16:55–18:20，17:05 在窗內。**判定：不成立（物理一致）**。
3. **候選**：堡區開放「sunrise to sunset」是否排除日落拍攝。**驗證**：NPS 營區規則指堡體開放至日落；宿營者於營地/海堤看日落不違規。**判定：不成立**。
4. **候選**：tz America/New_York（11 月 EST UTC-5）正確。**驗證**：Dry Tortugas 屬佛州東時區。**判定：不成立**。

## us-156 哈特拉斯角燈塔（Cape Hatteras, 35.2113/-75.5213, America/New_York）

1. **候選**：外灘島海灘朝東，「日落」是否物理存在於此題材。**驗證**：11 月日落方位約 245–250°（西南西）落於 Pamlico Sound 側陸/潟湖方向；實拍社群證實自海灘向西取燈塔剪影為成熟日落構圖（photographylife 提供日落 200mm 實拍）。sunset_window 本身（日落時刻 ±40 分）天文正確。**判定：不成立**。證據：https://photographylife.com/photo-spots/cape-hatteras-lighthouse ；https://tile.loc.gov/storage-services/master/pnp/habshaer/nc/nc0400/nc0432/data/nc0432data.pdf
2. **候選**：good_hours 17:00（11-11）是否在窗內。**驗證**：Buxton 11-11 日落約 16:55，窗約 16:15–17:35，17:00 在窗內。**判定：不成立**。
3. **候選**：「198 呎美國最高磚砌燈塔」事實核。**驗證**：Cape Hatteras Light 198 ft、全美最高磚造燈塔，正確。**判定：不成立**。證據：https://home.nps.gov/caha/planyourvisit/chls.htm
4. **候選**：tz EST 正確性。**驗證**：北卡東部時區，正確。**判定：不成立**。

## us-157 阿薩蒂格島野馬（Assateague, 38.0111/-75.2814, America/New_York）

1. **候選**：晨間 06:05 園區是否開放。**驗證**：NPS「Maryland District Open year round, 24 hours a day」——日出拍攝可達。**判定：不成立**。證據：https://home.nps.gov/asis/planyourvisit/hours.htm
2. **候選**：sunrise_window good_hours 06:05/07:00 是否涵蓋實際日出。**驗證**：38°N 11-10 日出約 06:34，±40 分＝05:54–07:14，06:05/07:00 皆在窗內；海平線無遮擋假設成立（東側大西洋）。**判定：不成立**。
3. **候選**：11 月是否仍蟲季/野馬離灘。**驗證**：蚊蟲季 5–9 月資訊性；野馬全年活動於灘與鹽沼。**判定：不成立**。
4. **候選**：座標屬馬里蘭區南端（近 OC 入口），野馬於全島分布。**驗證**：38.011 在 MD 區內，成立點位有效。**判定：不成立**。

## us-158 哈丁冰原展望（Harding Icefield, Kenai Fjords, 59.995/-149.69, America/Anchorage）

**卡片摘錄**：「8.2 英里步道頂端俯瞰 700 平方哩冰原與冰河溢口（NPS；步道夏季開放——access 不計分）」。

1. **候選**：11 月 Exit Glacier Road（Herman Leirer Rd）封閉汽車（約 11 月–5 月），trailhead 不可開車抵達——desc「步道夏季開放」警語是否足夠。**驗證**：NPS「in late-October to mid-May, the road to Exit Glacier is inaccessible to cars」；步道本身 10–5 月為 mountaineering route。卡片已標夏季開放+access 不計分；評估 11 月全 UNFAVORABLE 無誤導輸出。**判定：不成立（已覆蓋；同 us-151 建議強化警語具體月份）**。證據：https://www.nps.gov/kefj/planyourvisit/exit-glacier-area.htm ；https://www.nps.gov/kefj/planyourvisit/harding_icefield_trail.htm
2. **候選**：desc「8.2 英里」與「7.8-mile」版本差異。**驗證**：NPS 兩頁並存 7.8/8.2 mi 表述（thingstodo 頁用 8.2），非錯誤。**判定：不成立**。
3. **候選**：59.995°N 11 月 light_window PARTIAL 9 小時是否物理可能。**驗證**：11-10 日出約 09:20、日落約 16:50，civil 光窗約 08:35–17:35 ≈ 9.0 h——與 9 一致；無 22:00–06:00 光窗洩漏。**判定：不成立**。
4. **候選**：tz America/Anchorage（UTC-9）正確。**驗證**：Kenai 半島屬 Alaska Time。**判定：不成立**。

---

## 結論

**成立（4）**
- us-147-P01｜golden_hour_window BONUS 理由對「一臂寬狹縫」物理空窗（縫內需中上午光束；低角度光進不了縫），模板理由錯配為無效加分訊號。
- us-152-P01｜timezone_display America/Los_Angeles 誤置：Sawtooth/愛麗絲湖屬 America/Boise（Mountain, UTC-7），顯示時段偏移 1 小時。
- us-154-P01｜timezone_display 同誤：Twin Falls 屬 America/Boise（Mountain, UTC-7）。
- us-154-P01｜river_flow_state 以拍攝點 72h 當地雨量映射水量，但瀑布流量由上游融雪 + Milner Dam 灌溉分流/水電取水決定，當地降雨與水量脫鉤——判據物理上測不到目標量。

**次要文案建議（不計成立）**：us-149-P02 花期文案 2–4月→4–5月對齊；us-150 desc 土路 3.5→5.0 mi、座標 ~5km 校正；us-154 座標 ~2.5km 校正；us-152「IdDA」拼字；us-151/us-153/us-158 冬季道路封閉警語加註具體月份。
