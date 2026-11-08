# -*- coding: utf-8 -*-
# CL-DATA-35 batch1 access-verification content (verified 2026-11-08 against official sources)
D = '2026-11-08'
# per-place shared access facts: place -> (zh, en, ja) access note body
PLACE_NOTES = {
 'tw-001': (
  "位於陽明山國家公園（全年開放）。依陽明山管理處公告，大屯山車道自2020-08-10起全日禁止汽機車進入（公務及緊急車輛除外），須將車輛停放鄰近停車場後步行上主峰；建議搭乘捷運劍潭站轉紅5、台北站轉260/1717或北投站轉230/小9至陽明山，再轉108公車至二子坪站。山頂助航站及三角點位置非開放區域（軍事管制），觀景以助航站前平台為主。夜間拍攝請攜照明並依園區安全指示。",
  "In Yangmingshan National Park (open year-round). Per park HQ notice, the Datun Mountain roadway has been closed to private motor vehicles 24h since 2020-08-10 (official/emergency vehicles excepted); park nearby and walk up. Bus routes: MRT Jiantan + Red5, Taipei Station + 260/1717, or Beitou + 230/Xiao9 to Yangmingshan, then bus 108 to Erziping stop. The summit navigation-aid station and triangulation point are a restricted military area; shooting is done from the platform in front. Bring lights for night sessions and follow park safety guidance.",
  "陽明山国家公園内（通年開放）。同公園の告知により、大屯山車道は2020-08-10から終日自家用車・二輪の進入禁止（公務・緊急車両を除く）。近隣駐車場に停車し徒歩で登る。捷運剣潭駅からバス紅5、台北駅から260/1717、北投駅から230/小9で陽明山へ、108番バスで二子坪下車。山頂の助航站（航空支援施設）と三角点は軍事管理のため立入不可で、手前の展望プラットフォームから撮影。夜間は照明を携行し園区の安全指示に従う。"),
 'tw-002': (
  "位於象山自然步道（台北信義區，捷運象山站步行約10–15分入線）。依台北市府公告，象山步道及攝手（攝影）平台正進行環境整修施工，跨年前完工前請依施工圍籬與現場指示改道；園區無入場時限。跨年煙火場景之機位須提前占位，現場人潮管制依警方與市府公告。",
  "On Xiangshan (Elephant Mountain) nature trail in Xinyi, Taipei (10-15 min walk from MRT Xiangshan Station). Per Taipei City Government notice, the trail and the photographer platform are undergoing renovation; follow construction fencing and on-site detour instructions until completion (scheduled before the New Year fireworks). Open access, no gate hours. For the New Year fireworks shots arrive early; crowd-control measures per city/police notices.",
  "台北市信義区の象山自然歩道（捷運象山駅から徒歩10〜15分）。台北市の告知により、歩道と撮影用平台（攝手平台）は環境整備工事中で、完成（年越し花火前予定）までは仮囲いと現地案内に従い迂回する。開放式で入場制限なし。年越し花火撮影は早めの占位が必要で、人出規制は警察・市の公告に従う。"),
 'tw-003': (
  "位於新北市淡水漁人碼頭（24小時開放）。情人橋已由新北市政府正式開放通行（官方公告），木棧道全線自由進出；碼頭附設停車場與公車（捷運淡水站轉乘接駁公車）為主要交通方式。颱風或風浪大時安全管制依現場公告。",
  "At Tamsui Fisherman's Wharf, New Taipei (open 24 hours). The Lover's Bridge has been officially opened to pedestrians by the New Taipei City Government (official notice); the boardwalk is freely accessible. Parking at the wharf and buses connecting from MRT Tamsui Station are the main access. Safety closures during typhoons or heavy seas follow on-site notices.",
  "新北市淡水漁人碼頭（24時間開放）。恋人橋は新北市政府の公式告知により通行開放済みで、木製遊歩道は自由に通行可。港内駐車場と捷運淡水駅からの連絡バスが主なアクセス。台風・高波時の安全規制は現地案内に従う。"),
 'tw-004': (
  "位於新北市102號縣道（瑞雙公路）上、雙溪與九份交界山脊（新北市官方觀光網收錄景點）。車輛沿台102線自撰天?上山或自九份方向抵達，涼亭旁路肩可短暫停車，無專用大型停車場，連假易壅塞；夜間無照明，往返請備燈並注意公路車流。",
  "On Provincial Highway 102 (Rui-Shuang Road) on the ridge between Shuangxi and Jiufen, New Taipei (listed on the official New Taipei tourism site). Approach by road either from Ruifang side or Jiufen side; the paved shoulder by the pavilion allows short stops — there is no dedicated large parking lot and holiday congestion is common. The site is unlit at night; bring lights and watch traffic.",
  "新北市道102号（瑞双公路）上、双渓と九份の境界尾根にある（新北市公式観光サイト掲載）。瑞芳側または九份側から車で到達。あずまや脇の路肩に短時間駐車可だが専用大型駐車場はなく、連休は混雑しやすい。夜間は照明がなく、ライト携行と交通への注意が必要。"),
 'tw-005': (
  "位於台北市大同區大稻埕碼頭（淡水河岸，24小時開放；交通部觀光署官方即時影像頁收錄）。機車/汽車可停碼頭停車場，捷運大橋頭站或雙連站步行約15分。河濱園區無門禁，夜間照明僅步道基本燈光，器材照明自備。",
  "At Dadaocheng Wharf on the Tamsui riverfront, Datong District, Taipei (open 24 hours; listed on the Tourism Administration's official live-camera page). Wharf parking available; MRT Daqiaotou or Shuanglian then ~15 min walk. The riverside park has no gate; lighting at night is limited to basic path lamps — bring your own gear light.",
  "台北市大同区の大稲埕埠頭（淡水河岸、24時間開放、交通部観光署のライブカメラ公式ページ掲載）。埠頭駐車場利用可、捷運大橋頭駅または双連駅から徒歩約15分。河浜園区はゲートなし、夜間は歩道の基本照明のみで機材用照明は自前。"),
 'tw-008': (
  "位於北海岸及觀音山國家風景區（交通部觀光署）。依北觀處官方步道資料：硬漢嶺步道全長約1,563公尺，由北53-1線凌雲禪寺下方約100公尺處登山口起登（一般熱門路線），或由楓櫃斗湖步道終點銜接940公尺處；另有山區公車可達。步道無時限、無門票；觀音山冬季清晨易起霧，夜拍往返請結伴並備燈。",
  "Within North Coast and Guanyinshan National Scenic Area (Tourism Administration). Per the official trail page, the Yinghanyan (Hardman) Trail is about 1,563 m long, starting near Lingyun Temple on Route 53-1 (the popular route), or via the Fengguidouhu Trail junction at the 940 m mark; local buses reach the mountain area. No gate hours or ticket; fog is common on winter mornings — pair up and bring lights for night photography.",
  "北海岸及観音山国家風景区内（交通部観光署）。公式歩道ページによると、硬漢嶺歩道は全長約1,563 m、北53-1線の凌雲禅寺下方約100 mの登山口から（メインルート）、または楓櫃斗湖歩道の終点から940 m地点で合流。山間部へは路線バスもあり。開放制限・入場料なし。冬の早朝は霧が多く、夜撮影は複数人数とライト携行を推奨。"),
 'tw-009': (
  "位於基隆市八斗子（基隆市政府官方景點頁，24小時開放）。交通依官方指南：台鐵東部幹線至瑞芳站轉平溪深澳線至八斗子站（或西部幹線直達八斗子站）步行前往；公車103路至八斗子站沿八斗街、環山路步行抵達。步道臨崖，夜間無照明，請勿越出步道範圍。",
  "In Badouzi, Keelung (official city attractions page; open 24 hours). Official access: TRA East main line to Ruifang, transfer to the Pingxi–Shen'ao line to Badouzi Station (or direct from the West main line), then walk; city bus 103 to Badouzi and follow Badou St / Huanshan Rd. The trail runs along cliffs and is unlit at night — stay on the path.",
  "基隆市八斗子（基隆市政府公式景点ページ、24時間開放）。公式アクセス：台鉄東部幹線で瑞芳駅から平渓・深澳線に乗換、八斗子駅下車（西部幹線からは直行）後徒歩。バス103路で八斗子駅から八斗街・環山路を歩く。崖沿いの歩道で夜間照明はなく、道外に出ないこと。"),
 'tw-010': (
  "和平島公園為收費園區。依官方FAQ：5/1–10/31 開放 08:00–19:00（18:00停止兌票）、11/1–4/30 開放 08:00–18:00（17:00停止兌票）；自駕國道1號基隆端下接中正高架道路→正濱路→和一路→平一路，園區小客車停車134席（收費，平日50元/次、假日30元/時）。阿拉寶灣（岩石管制區）不含於門票，須另行預約園區導覽且依當日海象氣候開放——無導覽或海象不佳時不得進入，日出題材請先向園區確認導覽時段。",
  "Heping Island Park is a ticketed park. Official FAQ: 5/1-10/31 open 08:00-19:00 (ticket sales stop 18:00); 11/1-4/30 open 08:00-18:00 (17:00). Drive: Freeway 1 Keelung exit -> Zhongzheng elevated road -> Zhengbin Rd -> Heyi Rd -> Pingyi Rd; on-site parking 134 car spaces (fees: weekdays NT$50/entry, weekends NT$30/hr). Alabowan (the rock-restricted zone) is NOT included in the ticket: access only on official guided tours subject to daily sea/weather conditions — without a tour or in rough seas entry is prohibited. Sunrise subjects must first confirm the guided-tour slot with the park.",
  "和平島公園は有料園区。公式FAQ：5/1〜10/31 08:00〜19:00（18:00チケット発行終了）、11/1〜4/30 08:00〜18:00（17:00）。車は国道1号基隆端→中正高架道路→正浜路→和平一路→平一路。園内駐車134台分（平日50元/回、休日30元/時）。阿拉宝湾（岩石管制区域）は入園券に含まれず、公式ガイドツアーのみ・当日の海象により開放。ガイドなしや海象不良時は立入不可のため、日の出題材は事前にツアー枠を確認。"),
 'tw-011': (
  "位於桃園市觀音區永安漁港（桃園市政府觀光官網收錄）。港區24小時開放、免門票；港區有免費停車場，交通以自駕或客運為主。觀海橋依媒體報導曾進行除鏽整修並平日分時管制通行——實際可通行時段以現場公告與港方指示為準。",
  "At Yong'an Fishing Harbor, Guanyin District, Taoyuan (listed on the city tourism site). Harbor area open 24h, free entry, with free parking; access is mainly by car or intercity bus. The Guanhai (Sea-viewing) Bridge underwent rust-removal renovation with weekday time-limited access per news reports — actual passable windows follow on-site notices and port authority instructions.",
  "桃園市観音区の永安漁港（市公式観光サイト掲載）。港区域は24時間開放・無料で無料駐車場あり。主に自家用車または路線バス。観海橋は報道によると錆落とし補修と平日の時間帯別通行規制が実施されたことがあり、実際の通行可能時間は現地案内・港側指示に従う。"),
 'tw-012': (
  "賞蟹步道由新竹市政府管理。依市府香山濕地生態網官方公告：步道每月開放時間依潮汐表公告（一般約09:00起至18:00為止、滿潮前後與公休日封閉），且「陣風達6級以上步道封閉」（參考香山濕地測站資料）；實際開放以現場公告為主。步道僅在開放時段內進入，泥灘地拍照不可離開步道範圍（國家級重要濕地，濕地保育法管制）。",
  "The Crab-viewing boardwalk is managed by Hsinchu City Government. Per the official Xiangshan Wetland Eco-site notices: the monthly opening windows follow the tide table (roughly 09:00 to 18:00, closed around high tide and on scheduled closing days), and the boardwalk closes when gusts reach Beaufort 6 or above (per the Xiangshan wetland station data); on-site notices prevail. Entry only during open windows; leaving the boardwalk onto the mudflats is prohibited (a nationally protected wetland under the Wetland Conservation Act).",
  "香山湿蟹歩道は新竹市政府管理。市公式の香山湿地生態網告知によると、開放時間は毎月の潮汐表に従い（概ね09:00〜18:00、満潮前後と指定休館日は閉鎖）、陣風6級以上で閉鎖（香山湿地観測站データ参照）。実開放は現地公告が優先。開放時間内のみ入場可で、干潟への歩道外立入は禁止（国家級重要湿地・湿地保育法の管制）。"),
 'tw-013': (
  "火炎山位於苗栗三義（海拔602公尺），南北坡面主體屬「三義火炎山自然保留區」（林業及自然保育署劃設，礫岩惡地地形保護對象）。北側遠眺點（台13線／中安段）可自公路遠觀山壁，夕照題材成立；進入保留區步道須依主管機關當期規定申請或依公告辦理，切勿自行離開既設步道攀爬惡地坡面（坍方風險與法規管制）。本票以外部遠眺為主，不涉及保留區內拍攝。",
  "Houyan Mountain, Sanyi, Miaoli (602 m). The main slopes lie inside the Sanyi Houyan Mountain Nature Reserve (designated by the Forestry and Nature Conservation Agency for its gravel badlands). External viewpoints along the Tai-13 line allow the red-wall sunset view from public roadside; entering the reserve's trail is subject to the current application/notice rules of the managing agency — never leave the established trail to climb the badlands (rockfall/legal restrictions). This subject is the external view only and does not require reserve entry.",
  "苗栗三義の火炎山（標高602 m）。主な斜面は「三義火炎山自然保留区」（林業及び自然保育署指定、礫岩の悪地地形保護）内。台13線沿いの外部展望から赤い山肌の夕景を撮る本題材には保留区の立入は不要。保留区歩道への入場は主管機関の当該時期規定・公告に従い、既設歩道を外れて悪地斜面を登ることはしないこと（崩落リスクと法規制）。"),
 'tw-014': (
  "雲洞山莊為私有景觀民宿（苗栗縣政府客家景點資料收錄）：其觀景台屬民宿營業設施，非公共開放空間——白天及夜間使用宜事先聯繫或住宿確認開放與收費方式，勿在未獲同意下進入。通聯道路沿山區產業道路，夜間無照明、會車困難。",
  "Yundong Shanzhuang is a private scenic guesthouse (listed in Miaoli County's Hakka attraction records). Its viewing deck is part of the guesthouse operation, not public space — arrange access (day or night) in advance by contacting/staying; do not enter without consent. Access roads are narrow mountain farm roads, unlit at night with limited passing space.",
  "雲洞山荘は私有の景観民宿（苗栗県政府の客家景点資料に収録）。展望台は営業設備で公共空間ではないため、昼・夜とも事前に連絡または宿泊して利用可否・料金を確認し、同意なく入ることはしない。アクセスは山間の農道で夜間照明はなく、すれ違いも困難。"),
 'tw-015': (
  "高美濕地位於台中市清水區（台中市府列管自然保護區，遊憩票志工管理依市府公告）。堤岸周邊環境24小時可達；木棧道依市府公告實施維護封閉制度與潮汐管制（滿潮時封閉不得進入），2026年木棧道檢修已於10月完工全線開放（官方市政新聞）；清水高美大道旁設有大型停車場。進入濕地僅限木棧道，勿踏出棧道範圍（保育管制）。",
  "Gaomei Wetland, Qingshui, Taichung (managed by the city as a protected nature area). The embankment surroundings are reachable 24h; the boardwalk is subject to city-announced maintenance closures and tidal controls (closed at high tide). Official city news confirms the 2026 boardwalk maintenance finished in October with the full line reopened. A large public parking lot sits along Gaomei Road. Stay on the boardwalk — leaving it onto the wetland is prohibited (conservation rules).",
  "台中市清水区の高美湿地（市が自然保護区域として管理）。堤防周辺は24時間アクセス可。木製遊歩道は市公告による保守閉鎖と潮汐規制（満潮時は立入不可）あり。市公式報道により2026年の点検補修は10月に完了し全線開放済み。高美大道沿いに大型公共駐車場あり。遊歩道外の湿地へ踏み出すことは禁止（保育規制）。"),
 'tw-017': (
  "位於彰化縣芳苑鄉王功漁港（彰化縣政府旅遊網官方景點）。港區與漁港路沿線24小時可達、免費停車；芳苑燈塔為交通部航港局管轄之國際燈塔（1978年建，黑白直條紋，燈高35.7公尺，每10秒明暗），塔區並未對外開放登塔，從堤岸外側與生態景觀橋拍攝。潮汐潮差大，夕照潮溝構圖隨潮汐變化。",
  "At Wanggong Fishing Harbor, Fangyuan, Changhua (official county tourism page). Harbor and Yugang Rd are reachable 24h with free parking; Fangyuan Lighthouse is an international light under the Maritime and Port Bureau (built 1978, black-white stripes, light height 35.7 m, 10-second cycle) — the tower itself is not open for climbing; shoot from the embankment and the eco-bridge. Large tidal range changes the tidal-channel compositions through the day.",
  "彰化県芳苑郷の王功漁港（県公式観光ページ）。港区と漁港路は24時間アクセス可、無料駐車あり。芳苑灯台は交通部航港局管轄の国際灯台（1978年建、白黒縞模様、灯高35.7 m、10秒周期）で塔内への登塔は不可、堤防外側と生態景観橋から撮影。潮差が大きく、干潟構図は潮位で変化する。"),
 'tw-018': (
  "位於日月潭國家風景區（交通部觀光署）。水社壩一帶（含湖景步道）24小時自由進出、免門票；水社壩旁及水社遊客中心沿線有付費停車場與公車停靠（台灣好行日月潭線水社站）。拍攝「看見拉魯平台」等步道設施時請依風景區告示，環湖公路夜間車流注意。",
  "Within Sun Moon Lake National Scenic Area (Tourism Administration). The Shuishe Dam lakeside trail is open 24h free of charge; paid parking at Shuishe Dam and along the visitor center, with Sun Moon Lake Taiwan Tourist Shuttle stopping at Shuishe. Follow scenic-area signs on the lakeside platforms (incl. the Lalu-viewing platform) and watch traffic on the lake loop road at night.",
  "日月潭国家風景区内（交通部観光署）。水社壩の湖畔歩道は24時間自由進出・入場無料。水社壩付近と遊客中心沿線に有料駐車場があり、台湾好行日月潭線が水社駅に停車。ラルー島展望台などの湖畔設備は風景区の案内表示に従い、環湖道路の夜間走行に注意。"),
 'tw-019': (
  "位於太魯閣國家公園合歡山區（台14甲線）。依內政部國家公園署及太魯閣管理處公告：合歡主峰步道為自由進入的高山步道（免入園申請之遊憩區型步道），由主峰登山口步行約1.5–2公里登頂；日出前後及夜間拍攝常見，山區路肩停車位有限、假期實施交通管制（依國家公園署假日疏運公告），冬季道路可能封閉結冰管制，出發前查詢公路與園區即時公告。高山夜間氣溫低，注意保暖與高山症風險。",
  "In Taroko National Park's Hehuanshan area (Tai-14A road). Per the National Parks HQ and Taroko HQ notices, the Hehuan Main Peak trail is a freely accessible high-mountain trail (no park-entry permit needed for this recreation-type trail), about 1.5-2 km from the trailhead to the summit; night and pre-sunrise shooting are common. Roadside parking is limited and holiday traffic controls apply (per NPS holiday-management notices); winter road closures for ice are possible — check live road/park notices before setting out. Cold mountain nights; mind warmth and altitude effects.",
  "太魯閣国家公園の合歓山区（台14甲線）。国家公園署および太魯閣管理处の告知により、合歓主峰歩道は自由入場の高山歩道（遊憩区型で入山許可不要）、登山口から山頂まで約1.5〜2 km。日の出前や夜間撮影も一般的。路肩駐車は限られ、連休は交通規制（国家公園署の休日整理告知）。冬は凍結による通行止めがあり得るため、出発前に道路・園区の最新公告を確認。夜間の低温と高山反応に注意。"),
 'jp-002': (
  "位於大雪山國家公園旭岳（北海道東川町）。官方營運資訊：大雪山旭岳ロープウェイ（asahidake.hokkaido.jp）營運目前班次約 09:00 上行 – 16:00 下行（季節與天候會調整，山頂姿見站海拔約1600公尺），姿見池展望路線自山頂站起步行抵達；冬季大雪頻繁、地面易結冰，拍攝前請查閱當日纜車營運與入山安全公告（官方頁面同時發布山岳事故警示與即時氣象）。",
  "On Mt Asahidake, Daisetsuzan National Park (Higashikawa, Hokkaido). Official operator info: Asahidake Ropeway runs currently from about 09:00 up to 16:00 last down (season/weather dependent; Sugatami top station at ~1,600 m). The Sugatami-ike pond loop starts from the top station; heavy snow and ice are frequent in winter — check same-day ropeway operation and the safety/mountaineering alerts on the official page (which also posts live weather and mountain-accident warnings).",
  "大雪山国立公園・旭岳（北海道東川町）。運営公式情報：旭岳ロープウェイは現行 09:00 運行開始〜16:00 最終（季節・天候で変動；山頂姿見駅は標高約1,600 m）。姿見池の展望ルートは山頂駅から徒歩。冬は大雪と凍結が頻繁で、撮影前に当日のロープウェイ運行状況と入山安全の告知（山岳事故注意・実況気象）を公式サイトで確認すること。"),
 'jp-003': (
  "位於釧路濕原國立公園（國土交通省多言語解說資料庫收錄官方位置：北海道釧路郡釧路町達古武22-9）。展望台免費、全天可達，設有木棧展望平台與階梯；自釧路市方向經國道274/北海道立釧路線前往，設有免費停車場。冬季路面易凍，春季融雪前展望台部分封閉情況依管理公告。",
  "Within Kushiro Shitsugen National Park (official location in the MLIT multilingual database: Hokkaido, Kushiro-gun, Kushiro-cho, Takkobu 22-9). The observatory is free and reachable at all hours, with a wooden deck platform and stairs; access from Kushiro city via Route 274/local roads, with a free parking lot. Winter roads are icy, and part of the deck may close before the spring thaw per management notices.",
  "釧路湿原国立公園内（国土交通省多言語解説DBの公式位置：北海道釧路郡釧路町達古武22-9）。展望台は無料で終日アクセス可、木製デッキと階段あり。釧路市側から国道274号・道道でアクセスし無料駐車場あり。冬季は路面凍結しやすく、春の融雪前は一部閉鎖の場合あり（管理公告に従う）。"),
 'jp-004': (
  "函館山夜景：依函館山官方（函obura）公告，2026-10-20～11-08 為纜車法定整備運休期，期間山頂展望台開館 10:00–21:00，函館站始發登山巴士 13:30–19:30（山頂回程至20:10）；私家用車通行受限（9/30前 17:00–22:00、10/1起 16:00–21:00 禁行），11/9 起進入冬季通行管制。一般期山頂展望台由函館山ロープウェイ營運，夜間開放至約21:00，營業時間與運休資訊以官方公告為準。",
  "Mt Hakodate night view: per the official Mt Hakodate site (hakobura), 2026-10-20 to 11-08 is the annual statutory ropeway maintenance closure; during that period the summit observatory is open 10:00-21:00, the shuttle bus leaves Hakodate Station 13:30-19:30 (return to 20:10). Private cars are restricted (no-entry 17:00-22:00 until 9/30, 16:00-21:00 from 10/1), and winter closure begins 11/9. In normal periods the summit observatory is run by the Hakodateyama Ropeway with night operation to about 21:00; hours/closures follow the official notices.",
  "函館山夜景：公式サイト（hakobura）告知により、2026-10-20〜11-08はロープウェイ法定点検運休。期間中は山頂展望台 10:00〜21:00、函館駅発登山バス 13:30〜19:30（山頂発20:10まで）。自家用車は通行制限（9/30まで17:00〜22:00、10/1から16:00〜21:00の通行止め）、11/9から冬季通行止め。通常期は函館山ロープウェイが山頂展望台を運営し夜間は21時頃まで、時間・運休は公式告知による。"),
 'jp-005': (
  "位於小樽市中心（小樽市官方資料）：小樽運河全長1,140公尺，散步路沿線設置63基瓦斯燈，傍晚點燈與石造倉庫群一同燈光演出（市政府官方燈光資訊頁收錄燈光設施與LED更新公告）；小樽運河淺草橋前設有觀光案內所。運河自由步行參觀（24小時戶外開放），交通以 JR 小樽站步行可達。",
  "Central Otaru (official city info): Otaru Canal is 1,140 m long with 63 gas lamps along the promenade; the stone warehouses are lit up at dusk (the city's official lighting pages list the illumination facilities and LED-upgrade notices). A tourist information office sits at Asakusa-bashi on the canal. The canal promenade is free to walk (outdoor, 24h), reachable on foot from JR Otaru Station.",
  "小樽市中心（小樽市公式資料）：小樽運河は全長1,140 m、遊歩道沿いに63基のガス灯が設置され、夕暮れ時に石造倉庫群とともにライトアップされる（市公式の灯り資料ページに施設・LED更新告知あり）。浅草橋には観光案内所あり。運河遊歩道は自由散策（屋外・24時間）、JR小樽駅から徒歩。"),
 'jp-006': (
  "位於北海道弟子屈町（北海道官方旅遊HOKKAIDO LOVE! 收錄）。摩周湖第一展望台：設施「摩周湖 Kamuy Terrace」室內 8:30–17:00（年末年始休）；屋頂露台與展望平台可夜間/星空拍攝（官方明示屋頂露台夜晚依然開放）；停車場125輛（11月–4月免費），JR川湯溫泉站自駕約20分、女滿別機場約80分。冬季路面結冰與湖面霧氣頻繁，前往前查閱官方最新營運資訊。",
  "Teshikaga, Hokkaido (official HOKKAIDO LOVE! page). Mashu First Observatory: the indoor Kamuy Terrace runs 8:30-17:00 (closed New Year period); the rooftop terrace and deck are open at night for star/moonlight shooting (official text states the rooftop stays open after dark). Parking for 125 cars (free Nov-Apr), ~20 min by car from JR Kawayu-Onsen, ~80 min from Memanbetsu Airport. Icy roads and lake fog are frequent in winter — check the official page before visiting.",
  "北海道弟子屈町（北海道公式観音 HOKKAIDO LOVE! 掲載）。摩周湖第一展望台：屋内「摩周湖カムイテラス」は8:30〜17:00（年末年始休）、屋上テラスと展望デッキは夜間も開放で星空撮影可（公式文に夜間開放を明記）。駐車125台分（11〜4月は無料）、JR川湯温泉駅から車約20分、女満別空港から約80分。冬季は凍結と湖霧が多く、来訪前は公式最新情報を確認。"),
 'jp-007': (
  "位於青森縣十和田湖畔休屋地區。交通依青森縣官方觀音：JR八戶站轉乘十和田湖方向的巴士至休屋；休屋停靠的十和田湖遊覽船由十和田觀光電鐵營運（2026年時刻表已公開，休屋售票處遷至「十和田湖観光交流センター ぷらと」內，9:00起營業）。湖畔步道自由散步，冬季大雪與結冰期部分道路封閉，出發前查詢官方即時資訊。",
  "On the Yasumiya shore of Lake Towada, Aomori. Official Aomori tourism info: buses from JR Hachinohe Station head to Yasumiya; the Lake Towada sightseeing boat is operated by Towada Kanko Dentetsu (2026 timetable published; the Yasumiya ticket office has moved into the Towada-ko Kanko Koryu Center 'Puratto', opening at 9:00). The lakeshore trail is free to walk; heavy snow and ice close parts of the road in winter — check official live info before setting out.",
  "青森県十和田湖畔・休屋地区。青森県公式観光情報：JR八戸駅から十和田湖方面のバスで休屋へ。休屋発着の十和田湖遊覧船は十和田観光電鉄が運営（2026年時刻表公開；休屋発売所は「十和田湖観光交流センターぷらっと」内に移転、9時開始）。湖畔の遊歩道は自由散策可。冬期は大雪・凍結で一部道路が閉鎖となるため、出発前に公式の最新情報を確認。"),
 'jp-008': (
  "位於宮城縣松島町（松島町官方網站收錄）。依官方資料：双観山自松島海岸站步行約15分，位於國道45號沿線的「町道松島パノラマ線」入口附近；山頂展望台為公園整備、免費、全天可達；官方並明示「島々の間から昇る朝日」為著名拍攝題材。",
  "In Matsushima Town, Miyagi (listed on the town's official site). Official info: Sakan-yama (Sokanzan) is ~15 min walk from Matsushima-Kaigan Station, near the entrance of the Matsushima Panorama Line off Route 45; the hilltop viewing platform is a maintained park, free and accessible at all hours. The town's official page explicitly notes the sunrise between the islands as a famous subject.",
  "宮城県松島町（松島町公式サイト掲載）。公式資料：双観山は松島海岸駅から徒歩約15分、国道45号沿いの「町道松島パノラマ線」入口付近。山頂展望台は公園として整備され、無料・終日アクセス可。公式ページでは「島々の間から昇る朝日」が名物と明記されている。"),
 'jp-009': (
  "位於磐梯朝日國立公園內、福島縣猪苗代町（福島縣官方復興構想頁面收錄中瀬沼展望台景觀）。自磐梯山西側的「中瀬沼探勝路」前往，展望台免費、無時限；冬季大雪封路與雪崩資訊依磐梯山地區公告（猪苗代觀光協會官方交通頁）。泥沼地形泥濘，請依既設棧道行走。",
  "Inside Bandai-Asahi National Park, Inawashiro, Fukushima (the official Fukushima Green Recovery page covers the Nakanozawa observatory view). Reached via the Nakanozawa walking trail on the west side of Mt Bandai; the observatory is free and unlimited-hours. Winter heavy snow can close roads and avalanche notices follow the Bandai-area official pages (Inawashiro Tourism Association). The marsh terrain is muddy — stay on the established boardwalk.",
  "磐梯朝日国立公園内・福島県猪苗代町（福島県公式グリーン復興構想ページに中瀬沼展望台の景観を掲載）。磐梯山西側の「中瀬沼探勝路」から access、展望台は無料・時間制限なし。冬期の豪雪による道路閉鎖や雪崩情報は磐梯山地區の公式告知（猪苗代観光協会）に従う。泥沼地形のため既設の木道を外れて歩かないこと。"),
 'jp-010': (
  "位於山梨縣富士河口湖町（河口湖大石公園，町政府官方都市公園頁收錄）。官方資料：地址富士河口湖町大石2525-11先，設大型巴士可停的免費駐車場、展望あずまや與「河口湖自然生活館」（冬季12月中旬–3月末供水停用）；公園為24小時開放免費，逆さ富士以清晨靜水為佳，拍攝時留意湖畔道路停車規定與花季人潮。",
  "Fujikawaguchiko, Yamanashi (Oishi Park on Lake Kawaguchiko; listed on the town's official urban-park page). Official info: address Oishi 2525-11-先, free parking including large buses, a viewing pavilion and the Kawaguchiko Natural Living Center (water off mid-Dec to end-Mar). The park is free and open 24h; the reverse-Fuji reflection is best in calm early mornings — mind roadside parking rules and flower-season crowds.",
  "山梨県富士河口湖町（河口湖・大石公園、町公式都市公園ページ掲載）。公式情報：所在地 大石2525-11の先、大型バスも停められる無料駐車場、展望あずまやと「河口湖自然生活館」（12月中旬〜3月末は給水停止）。公園は24時間開放・無料。逆さ富士は早朝の静けい水面が好機で、湖畔道路の駐車規則と花季の混雑に注意。"),
 'jp-013': (
  "位於長野縣諏訪市（諏訪市官方公園頁）。依官方交通資訊：JR上諏訪站步行約30分或計程車約15分（另有 AI 交通「チョイソコ」立石町站步行10分）；公園駐車場僅23台（含2台無障礙）、摩托8台，大型巴士不可停，路邊停車嚴禁；假期或平日16時後常壅塞（官方建議先看官方 Live camera 確認停車情況）；公園免費、無時限（戶外）。",
  "In Suwa, Nagano (official city park page). Official access: ~30 min walk or ~15 min taxi from JR Kamisuwa Station (also the AI on-demand 'Choisoko' stop Tateishi-cho, 10 min walk). Parking only 23 cars (2 accessible) plus 8 bikes; no large-bus parking, roadside stopping strictly prohibited; congestion typical on holidays and after 16:00 even on weekdays (official advice: check the official live camera before coming). Park is free, outdoor, unlimited hours.",
  "長野県諏訪市（諏訪市公式公園ページ）。公式アクセス：JR上諏訪駅から徒歩約30分またはタクシー約15分（AI交通「チョイソコ」立石町停留所から徒歩約10分）。駐車場は23台分（内2台は障害者用）とバイク8台のみで大型バスは不可、路上駐車は厳禁。祝日や平日でも16時以降は渋滞しやすく、公式ライブカメラで駐車状況を確認してから訪問推奨。公園は無料・屋外・時間制限なし。"),
 'jp-016': (
  "位於橫濱市中區港邊（橫濱市官方公園資料與官方觀光頁收錄）。山下公園為24小時開放的濱水公園、免費；鄰近 JR 關內站／港未來站步行可達，周邊多處收費停車場（自駕不提供免費停車）。夜間步道有基本照明，拍水面倒影時留意風向與船舶作業影響。",
  "In Naka-ku, Yokohama waterfront (official city park page and official visitor guide). Yamashita Park is a free, 24h-open waterfront park; walkable from JR Kannai or Minato Mirai stations, with paid parking nearby (no free on-site parking). Basic path lighting at night; watch wind direction and ship-operations effects when shooting reflections.",
  "横浜市中区の水辺（横浜市公式公園資料・公式観光ガイド掲載）。山下公園は24時間開放・無料の臨海公園。JR関内駅またはみなとみらい駅から徒歩、近隣に有料駐車場多数（無料駐車なし）。夜間は歩道の基本照明のみで、水面反射の撮影では風向きと船舶作業の影響に注意。"),
 'jp-019': (
  "位於靜岡縣濱松市濱名湖畔（濱松市官方「弁天島海浜公園再整備事業」頁收錄）。公園為免費、戶外、24小時可達（濱名湖湖岸）；交通以 JR 弁天島站步行或自駕為主，園區周邊有市營收費停車場；湖岸淺灘拍攝留意潮位與風（漲潮時部分步道濕滑），再整備工程期間部分區域依施工告示管制。",
  "On the Hamanako lakeshore in Hamamatsu, Shizuoka (listed on the city's official Bentenjima Kaihin Park redevelopment page). Free outdoor lakeside park, reachable 24h; access mainly on foot from JR Bentenjima Station or by car, with city paid parking nearby. Mind tide levels and wind on the shallow lakeshore (some paths are slippery at high tide); during redevelopment works some areas follow construction notices.",
  "静岡県浜松市の浜名湖畔（浜松市公式「弁天島海浜公園再整備事業」ページ掲載）。無料・屋外・24時間アクセス可の湖岸公園。JR弁天島駅から徒歩または自家用車が主で、近隣に市営有料駐車場あり。湖岸の浅場では潮位と風に注意（満潮時は一部歩道が滑る）。再整備工事中は工事告示に従い一部区域が規制される。"),
 'jp-020': (
  "位於橫濱港大棧橋國際客船碼頭（官方樓層指南頁）。官方明示：「屋上廣場（鯨之背）」為24小時開放、任何人可自由使用的公園型空間，從屋上可 360 度眺望港未來大樓群與 Bay Bridge；碼頭內停車為收費（依官方 FAQ），夜間拍攝時配合客船入港作業避免進入作業區。",
  "Yokohama Osanbashi International Passenger Terminal (official floor guide). Officially: the rooftop plaza ('Whale's Back') is a 24-hour, free, anyone-can-use park-like space with a 360-degree view over Minato Mirai and Bay Bridge; terminal parking is paid (official FAQ). At night, stay clear of ship-berthing operation areas while shooting.",
  "横浜港大さん橋国際客船ターミナル（公式フロアガイド）。公式：屋上広場「くじらのせなか」は24時間・無料で誰でも自由に使える公園的空間で、みなとみらいのビル群とベイブリッジを360度望める。ターミナル駐車場は有料（公式FAQ）。夜間は客船の入出港作業エリアに入らないよう注意。"),
 'jp-025': (
  "限定活動題材：依山口縣官方旅遊網（おいでませ山口へ）2026 年公告，「萩・竹灯路物語」於 2026-10-09～10-11 每晚 18:00–21:00 於萩城下町周邊舉行（免費，雨天中止）；期間約 2,000 支竹灯籠照亮菊屋橫町等歷史街區，交通：JR 新山口站巴士約60分或小郡萩道路絵堂 IC 自駕約20分；一般車輛可停萩博物館前駐車場（一般93台、一次310日元、大型8台1,050日元）。活動期外的菊屋橫町僅有街燈，不成立本題材。",
  "Event-only subject: per the official Yamaguchi tourism site (2026), 'Hagi Chiku-toro Monogatari' runs 2026-10-09 to 10-11, 18:00-21:00 nightly around the Hagi castle town (free; cancelled in rain); about 2,000 bamboo lanterns light Kikuya Yokomachi and the historic streets. Access: ~60 min bus from JR Shin-Yamaguchi or ~20 min drive from Oido IC on the Shimonoseki–Hagi road; general parking at the Hagi Museum lot (93 cars, 310 yen per entry; 8 buses 1,050 yen). Outside the event dates the lane has only ordinary street lights — the subject does not hold.",
  "期間限定題材：山口県公式観光サイト（おいでませ山口へ）2026年告知によると、「萩・竹灯路物語」は2026-10-09〜10-11、毎晩18:00〜21:00に萩城下町周辺で開催（無料、雨天中止）。約2,000本の竹灯籠が菊屋横丁など歴史街並みを照らす。アクセス：JR新山口駅からバス約60分、または小郡萩道路絵堂ICから車約20分。萩博物館前駐車場（一般93台・1回310円、大型8台1,050円）を利用。期間外の菊屋横丁は普通の街灯のみで本題材は不成立。"),
 'jp-028': (
  "位於和歌山縣高野山（世界遺產）。壇上伽藍院區為自由參拜（免費、戶外），依高野山真言宗總本山金剛峯寺官方公告：金堂等個別內陣參拜另有制度與臨時拝観休止公告（例2026-09-14金堂終日拝観休止），夜間伽藍院區照明有限，蛇腹路／根本大塔周邊為最受歡迎的紅葉機位；拍攝請保持參拜禮節、不使用閃光燈於參拜者通道。",
  "Mt Koya (Koyasan), Wakayama (World Heritage). The Danjo Garan grounds are freely viewable (free, outdoors). Per the official Kongobuji (Koyasan Shingon Shu) notices: individual inner-sanctum worship (Kondo etc.) has its own system and temporary closure notices (e.g. Kondo closed all day 2026-09-14). Grounds lighting is limited at night; the Serpent-path area near the Konpon Daito is the most popular autumn-leaf spot. Keep worship etiquette — no flash toward visitors.",
  "和歌山県・高野山（世界遺産）。壇上伽藍の院区は自由参拝（無料・屋外）。高野山真言宗総本山金剛峯寺の公式告知によると、金堂など個別の内陣参拝は別制度と臨時の拝観休止公告（例：2026-09-14は金堂終日拝観休止）がある。夜間の伽藍内は照明が限られ、蛇腹路・根本大塔周辺が紅葉の定番ポイント。参拝者の通路ではフラッシュを使用せず礼節を守る。"),
 'jp-029': (
  "位於三重縣伊賀市上野（伊賀上野城，官方管理單位伊賀文化產業協會）。官方「ご利用案内」頁公布參觀制度與票價；石牆與外觀公園為常時可拍（戶外），天守閣入館（收費）依官方時間制度；拍攝櫻花題材時上野公園為市立公園（24小時可達），觀音門周邊留意參觀人潮與禁入區。",
  "Ueno, Iga, Mie (Iga-Ueno Castle; managed by the Iga Cultural Property Association). The official usage-guide page lists visiting rules and fees; the stone walls and outer castle grounds are viewable at all times (outdoor) and the donjon interior is ticketed with official hours. For the cherry-blossom subject, Ueno Park is a public city park (open 24h); mind crowds and restricted areas around the castle.",
  "三重県伊賀市上野（伊賀上野城、管理は伊賀文化産業協会）。公式ご利用案内ページに見学制度・料金を掲載。石垣と外郭の公園は常時見学可（屋外）、天守閣内部は有料で公式時間制度に従う。桜題材は上野公園が市立公園（24時間アクセス可）で、城周辺の混雑と立入禁止区域に注意。"),
 'jp-030': (
  "位於德島縣鳴門市（德島縣立「渦の道」官方頁）。官方資訊：營業時間 夏季（3–9月）09:00–18:00（最終入場17:30）、冬季（10–2月）09:00–17:00（16:30）、GW/暑假期間 08:00–19:00；休館日為 6、9、12、3月第2個星期一（7/20–8/31無休）；票價大人510日元、中小生410/250日元；自駕由鳴門北 IC 5分，停車場小客車200台（1日420日元）、巴士20台；JR鳴門站轉市營巴士約20分。漩渦屬潮汐現象，最盛期依潮汐表為主（官方頁同時提供大鳴門橋展望台與觀潮船資訊）。",
  "Naruto, Tokushima (official Tokushima Prefecture Uzunomichi page). Official info: summer (Mar-Sep) 09:00-18:00 (entry till 17:30), winter (Oct-Feb) 09:00-17:00 (16:30), GW/summer holidays 08:00-19:00; closed the 2nd Monday of Jun/Sep/Dec/Mar (no closure 7/20-8/31). Fees: adults 510 yen, junior/senior-high 410, elementary 250. Access: 5 min from Naruto-Kita IC, parking 200 cars (420 yen/day) and 20 buses; ~20 min city bus from JR Naruto Station. The whirlpools are tidal phenomena — best timing follows the tide table (official page also lists Onaruto Bridge observatory and cruise-boat info).",
  "徳島県鳴門市（徳島県立「渦の道」公式ページ）。公式情報：夏季（3〜9月）09:00〜18:00（入場17:30まで）、冬季（10〜2月）09:00〜17:00（16:30）、GWと夏休みは08:00〜19:00。休館日は6・9・12・3月の第2月曜（7/20〜8/31は無休）。料金：大人510円、中高生410円、小学生250円。アクセスは鳴門北ICから5分、駐車場は乗用車200台（1日420円）・バス20台。JR鳴門駅から市営バス約20分。渦潮は潮汐現象のためベストタイミングは潮見表による（公式ページに展望台・観潮船情報もあり）。"),
 'jp-031': (
  "位於岡山縣倉敷市美觀地區（倉敷市官方觀光網收錄）。依官方頁：夜間景觀照明由 2005 年起實施（石井幹子設計），時間 4–9月 日沒–22:00、10–3月 日沒–21:00，範圍以倉敷川沿岸為核心；街區為自由步行（24小時戶外），倉敷川船遊為營運時間內收費項目；夜拍水面倒影留意遊客與船班。",
  "Bikan (Beauty-view) district, Kurashiki, Okayama (official city tourism site). Official info: the night landscape lighting has run since 2005 (designed by Motoko Ishii) from dusk to 22:00 in Apr-Sep and 21:00 in Oct-Mar, centered on the Kurashiki-gawa riverfront; the streets are free to walk (outdoor, 24h), and the canal boat ride is a paid scheduled service. Mind pedestrians and boat traffic when shooting river reflections.",
  "岡山県倉敷市の美観地区（倉敷市公式観光サイト掲載）。公式情報：夜間景観照明は2005年から実施（石井幹子氏デザイン）、4〜9月は日没〜22:00、10〜3月は日没〜21:00で、倉敷川沿いを中心に点灯。街並みは自由散策（屋外・24時間）で、倉敷川の舟遊は営業時間内の有料。水面反射の撮影では通行者と運航に注意。"),
 'jp-032': (
  "位於福岡市中央區（福岡市文化財官方頁）。依官方「福岡城天守台入場制限のお知らせ」（2026年）：天守台石垣目前實施入場限制（具體開放與否依官方最新公告），城跡公園整體（戶外）仍自由參觀；櫻花與季節花木題材以城跡公園與天守台石垣遠景為主，開放限制期間請勿靠近管制區。",
  "Chuo-ku, Fukuoka (official Fukuoka City Cultural Properties page). Per the official 'Fukuoka Castle Tenshudai Entry Restriction Notice' (2026): entry to the tenshudai stone-base is currently restricted (openings follow the latest official notices), while the castle-park grounds (outdoor) remain freely walkable. The four-seasons/flower subjects use the park and the stone-base view from outside — do not approach the restricted area while limits are in effect.",
  "福岡市中央区（福岡市文化財公式ページ）。公式「福岡城天守台入場制限のお知らせ」（2026年）により、天守台石垣への入場は現在制限中（開放の有無は最新の公式告知による）だが、城跡公園全体（屋外）は自由に見学可。四季の花木題材は公園と石垣を外側から撮るもので、規制中は立入禁止区域に近づかないこと。"),
 'jp-036': (
  "位於宮崎縣高千穗町（高千穗町觀光協會官方）。官方資訊：峽谷有真名井瀑布、柱狀節理與划船等多重機位；高千穗峽遊覽船（官方 boat 頁）為營運時間內收費租船（一般遊船50分/分鐘制），划船視角自真名井瀑布下方水域拍攝；周邊有第一、第二等多處免費停車場（連假易滿），峽谷步道免費、無時限，但部分路段因石落與保育管理會臨時封閉（依現場告示）。自駕沿國道218轉縣道，宮崎或熊本方向約1.5–2小時。",
  "Takachiho, Miyazaki (official Takachiho Tourism Association). Official info: the gorge offers Manai Falls, columnar basalt and boat viewpoints; the Takachiho Gorge rental boats (official boat page) run within operating hours for a fee, with the rowing view from the water below Manai Falls; several free parking lots (first/second etc.) fill up on holidays; the gorge walking path is free and unlimited-hours, but some sections close temporarily for rockfall/conservation management (on-site signs). Drive via Route 218 to the prefectural road, ~1.5-2 h from Miyazaki or Kumamoto directions.",
  "宮崎県高千穂町（高千穂町観光協会公式）。公式情報：峡谷には真名井の滝・柱状節理・貸しボートなど複数の撮影拠点がある。高千穂峡遊覧船（公式boatページ）は営業時間内の有料貸船で、真名井の滝下部の水上からの視点が得られる。第1・第2など複数の無料駐車場があり連休は満車になりやすい。峡谷遊歩道は無料・時間制限なしだが、落石や保護管理で一部区間が臨時閉鎖の場合あり（現地案内に従う）。国道218号から県道へ、宮崎または熊本側から約1.5〜2時間。"),
 'jp-041': (
  "已於 2026-11-08（CL-DATA-32 入案驗證）完成存取與座標查證：プユニ岬展望台位於北海道斜里町、國道93（知床橫斷道路）沿線的自駕展望台（mapion 座標 44.0958,145.0093），免費、24小時可停車短留；流冰接岸期（1月下旬–3月）往烏道方向往返常見塞車與結冰路面。",
  "Already access- and coordinate-verified 2026-11-08 (CL-DATA-32 admission verification): Puyuni Cape Observatory sits on Route 93 (the Shiretoko crossing road) in Shari, Hokkaido, as a drive-up viewpoint (Mapion coordinates 44.0958,145.0093), free with short-stop parking 24h. During the drift-ice onshore season (late Jan-Mar) traffic jams and icy surfaces are common on the pass.",
  "2026-11-08（CL-DATA-32入案検証）でアクセスと座標の照合済み：プユニ岬展望台は北海道斜里町の国道93号（知床横断道路）沿いの車で行ける展望台（マピオン座標 44.0958,145.0093）。無料で24時間、短時間の停車可。流氷接岸期（1月下旬〜3月）は峠道で渋滞と凍結路面が頻繁。"),
}
PLACE_EVID = 'e-d35-access'
PLACE_SLUG = {
 'tw-001':'datunshan-ymsnp','tw-002':'xiangshan-taipei','tw-003':'tamsui-fishermans-wharf','tw-004':'buyanting-newtaipei',
 'tw-005':'dadaocheng-wharf','tw-008':'yinghanyan-northguan','tw-009':'wangyougu-keelung','tw-010':'heping-island-park',
 'tw-011':'yongan-fishing-harbor','tw-012':'xiangshan-wetland-hccg','tw-013':'huoyanshan-reserve','tw-014':'yundong-guesthouse',
 'tw-015':'gaomei-wetland-taichung','tw-017':'wanggong-fangyuan','tw-018':'shuishe-dam-sml','tw-019':'hehuan-taroko',
 'jp-002':'asahidake-ropeway','jp-003':'hosooka-observatory','jp-004':'hakodateyama-hakobura','jp-005':'otaru-canal-city',
 'jp-006':'mashu-first-observatory','jp-007':'towada-yasumiya','jp-008':'sokanzan-matsushima','jp-009':'nakanozawa-bandai',
 'jp-010':'oishi-park-fujikawaguchiko','jp-013':'tateishi-park-suwa','jp-016':'yamashita-park-yokohama','jp-019':'bentenjima-hamamatsu',
 'jp-020':'osanbashi-rooftop','jp-025':'hagi-chikutoro','jp-028':'danjo-garan-koyasan','jp-029':'iga-ueno-castle',
 'jp-030':'uzunomichi-tokushima','jp-031':'bikan-kurashiki','jp-032':'fukuoka-castle-tenshudai','jp-036':'takachiho-gorge',
 'jp-041':'puyuni-cl-d32',
}
PLACE_SOURCES = {
 'tw-001':["https://www.ymsnp.gov.tw/ch/sglarticle/datun-mountain-roadway-motor-vehicles-prohibited","https://www.taiwan.nps.gov.tw/home/zh-tw/attractions/21183.html"],
 'tw-002':["https://www-ws.gov.taipei/Download.ashx?u=LzAwMS9VcGxvYWQvMzU2L3JlbGZpbGUvNjg1MTUvOTcxMDMyNS9jZjM3M2I3NC0wZjEyLTQwOTktOTFlYy1mYzRmNGRmYmE3N2EucGRm&n=MTE15q2l5bCILeaWveW3peWFrOWRijA3MTYucGRm&icon=.pdf","https://news.ltn.com.tw/news/life/breakingnews/5612320"],
 'tw-003':["https://www.ntpc.gov.tw/ch/home.jsp?id=e8ca970cde5c00e1&dataserno=b1604f8839124c4d7d61c21854617856","https://www.taiwan.net.tw/m1.aspx?sNo=0042331&uid=25004"],
 'tw-004':["https://newtaipei.travel/zh-tw/attractions/detail/110088"],
 'tw-005':["https://www.taiwan.net.tw/m1.aspx?sNo=0042331&uid=25000"],
 'tw-008':["https://www.northguan-nsa.gov.tw/user/article.aspx?Lang=1&SNo=04006757"],
 'tw-009':["https://www.klcg.gov.tw/tw/klcg1/973-95928.html"],
 'tw-010':["https://hpipark.fonticket.com/web/faq","https://www.taiwan.net.tw/m1.aspx?sNo=0001016&id=635"],
 'tw-011':["https://www.taiwan.net.tw/m1.aspx?sNo=0042331&uid=25048","https://www.cna.com.tw/news/aloc/202606070106.aspx"],
 'tw-012':["https://ssw.hccg.gov.tw/posts/152","https://ssw.hccg.gov.tw/"],
 'tw-013':["https://www.forest.gov.tw/0007960"],
 'tw-014':["https://romantichakka.hakka.gov.tw/zh-tw/attraction/spot?a=928&id=676"],
 'tw-015':["https://www.taichung.gov.tw/8868/8872/9962/1396251","https://www.taichung.gov.tw/8868/8872/9962/3377284"],
 'tw-017':["https://tourism.chcg.gov.tw/AttractionsContent.aspx?id=80&chk=7ca73fbb-c3e0-4c87-ba52-e2b0b3b04065&l=TW"],
 'tw-018':["https://www.sunmoonlake.gov.tw/zh-TW/Attractions/Attractions?a=20&id=100"],
 'tw-019':["https://www.taroko.gov.tw/ch/listicle/faq/341","https://www.nps.gov.tw/ch/titlelist/parknews/2589","https://www.nps.gov.tw/ch/titlelist/parknews/5197"],
 'jp-002':["https://asahidake.hokkaido.jp/ja/"],
 'jp-003':["https://www.mlit.go.jp/tagengo-db/R1-01971.html","https://www.env.go.jp/nature/nationalparks/list/kushiro-shitsugen/spot/"],
 'jp-004':["https://www.hakobura.jp/news/437"],
 'jp-005':["https://www.city.otaru.lg.jp/docs/2020100900367/","https://www.city.otaru.lg.jp/docs/2020100900633/"],
 'jp-006':["https://www.visit-hokkaido.jp/tw/spot/detail_10484.html"],
 'jp-007':["https://aomori-tourism.com/access/detail_8962.html","https://www.toutetsu.co.jp/ship.html"],
 'jp-008':["https://www.town.miyagi-matsushima.lg.jp/page/1267.html"],
 'jp-009':["https://www.pref.fukushima.lg.jp/w4/fgr/perfectview/p04/","https://www.bandaisan.or.jp/access-3/"],
 'jp-010':["https://www.town.fujikawaguchiko.lg.jp/ka/info.php?if_id=2346"],
 'jp-013':["https://www.city.suwa.lg.jp/site/tateishipark/74822.html","https://www.city.suwa.lg.jp/site/tateishipark/"],
 'jp-016':["https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/midori-koen/koen/koen/daihyoteki/kouen008.html","https://www.welcome.city.yokohama.jp/spot/details.php?+bbid=190"],
 'jp-019':["https://www.city.hamamatsu.shizuoka.jp/kanko/bentenjima-kaihinkouen/saiseibi.html"],
 'jp-020':["https://osanbashi.jp/floorguide/rooftop","https://osanbashi.jp/faq"],
 'jp-025':["https://yamaguchi-tourism.jp/event/detail_17542.html"],
 'jp-028':["https://www.koyasan.or.jp/sp/news/2026/08/28/7539/","https://www.koyasan.or.jp/news/2026/08/31/12150/"],
 'jp-029':["http://igaueno-castle.jp/?page_id=8"],
 'jp-030':["https://www.pref.tokushima.lg.jp/japanese/tourism/spot/uzunomichi"],
 'jp-031':["https://www.kurashiki-tabi.jp/rm_see/rm-see227/"],
 'jp-032':["https://bunkazai.city.fukuoka.lg.jp/news/detail/462"],
 'jp-036':["https://takachiho-kanko.info/faq/","https://takachiho-kanko.info/boat/"],
 'jp-041':["https://www.mapion.co.jp/m2/44.09579822,145.00933597,16/poi=L0634319","https://hokkaidodo.jp/capes/shari-5/"],
}
