# -*- coding: utf-8 -*-
# CL-DATA-36 batch2 access-verification content (verified 2026-11-09 against official sources)
D = '2026-11-09'
# per-place shared access facts: place -> (zh, en, ja) access note body
PLACE_NOTES = {
 'tw-019': (
  "位於太魯閣國家公園合歡山遊憩區。合歡主峰步道曾因鋪面改善工程封閉，2025年10月起隨園區部分開放公告恢復通行，惟觀景平台整建中暫不開放；實際開放期程依太管處官網公告。車行台14甲線至登山口（無大眾運輸直達），高海拔夜間易結霜，請備保暖衣物與照明。",
  "In the Hehuan Mountain recreation area of Taroko National Park. The Hehuan Main Peak trail was closed for pavement improvement and reopened from October 2025 under the park's partial-reopening notice; the viewing platform remains closed during reconstruction. Check the Taroko HQ site for the current status. Access is by car along Provincial Highway 14A to the trailhead (no direct public transport). Frost forms at night at this altitude — bring warm layers and lights.",
  "太魯閣国家公園合歓山遊憩区域内。合歓主峰歩道は舗装改善工事のため閉鎖されていたが、2025年10月の園区部分開放公告により通行再開。ただし展望台は改築中のため引き続き閉鎖。実際の開放状況は太魯閣管理処の公式サイトで確認すること。登山口へは台14甲線を車で向かう（公共交通の直達なし）。この標高では夜間に霜が降りるため、防寒具とライトを携行すること。"),
 'tw-020': (
  "位於南投縣魚池鄉大雁村。依日月潭國家風景區管理處官網，金龍山24小時全年開放，僅於颱風等天然災害或整修工程時暫時封閉；步道全長約1.5公里，一、二、三亭各自設有停車場，可依體力選擇落點。夜間為無照明山道，請攜燈並注意濕滑。",
  "In Dayan Village, Yuchi Township, Nantou. Per the Sun Moon Lake National Scenic Area HQ site, Jinlongshan is open 24 hours year-round and closes only during typhoons, other natural disasters or maintenance works. The trail is about 1.5 km with parking lots by each of the three pavilions (Yi/Ert/San Ting) so you can pick your start. The trail is unlit at night — bring lights and watch for wet surfaces.",
  "南投県魚池郷大雁村内。日月潭国家風景区管理処の公式サイトによると、金龍山は24時間・通年開放で、台風などの自然災害や改修工事のときのみ一時閉鎖。全長約1.5kmの歩道には一・二・三の展望亭それぞれに駐車場があり、体力に応じて出発点を選べる。夜間は照明のない山道のため、ライト携行と足元の湿りに注意。"),
 'tw-021': (
  "位於南投縣仁愛鄉武界部落（南投縣政府官方旅遊網收錄，全天開放）。自部落步行約一小時可達摩摩納爾瀑布與武界壩，一線天位於濁水溪河道沿線，須自武界吊橋旁小路下切河床，地形與溪水狀態變動大，請結伴並依現場指示。部落道路無照明，夜間移動請自備燈。",
  "In Wujie Village, Ren'ai Township, Nantou (listed on the official Nantou tourism site; open around the clock). Momonael Falls and the Wujie Dam are about a one-hour walk from the village; the Yixiantian (One-Line-Sky) gorge is along the Zhuoshui riverbed and reached via the small path beside the Wujie suspension bridge — conditions change with the river, so go in company and follow on-site signs. Village roads are unlit; carry your own lights at night.",
  "南投県仁愛郷の武界部落（南投県公式観光サイト掲載、終日開放）。部落から徒歩約1時間で摩摩納爾瀑布と武界壩に到達。一線天は濁水渓の河川敷沿いにあり、武界吊り橋の脇の小道から川原へ降りる必要がある。川の状態で状況が変わるため、必ず複数人で移動し現地案内に従うこと。部落内の道路は無照明のため、夜間は自前のライトが必要。"),
 'tw-022': (
  "入口位於嘉義縣台18線（阿里山公路）52.8K處，依阿里山國家風景區管理處官網全天開放。單程約2.1公里、原路往返且有階梯。汽車可停鞍頂或隙頂停車場；大眾運輸可搭嘉義縣公車（達邦/奮起湖/阿里山線）或台灣好行阿里山線於鞍頂站下車，步行約30公尺至登山口。",
  "Trailhead on Provincial Highway 18 (Ali Mountain Highway) at 52.8K, Chiayi County; per the Ali Mountain National Scenic Area HQ site it is open around the clock. One way is about 2.1 km, out-and-back with stairs. Cars can park at Anding or Xiding lots; by bus take the Chiayi County bus (Dabang / Fenqihu / Alishan lines) or the Taiwan Trip Ali Mountain line to Anding stop, about 30 m from the trailhead.",
  "嘉義県の台18線（阿里山公路）52.8Kに入口があり、阿里山国家風景区管理処の公式サイトによると終日開放。片道約2.1km、往復で階段を含む。車は鞍頂または隙頂の駐車場を利用。公共交通は嘉義県バス（達邦/奮起湖/阿里山線）か「台湾好行」阿里山線で鞍頂駅下車、徒歩約30mで登山口。"),
 'tw-023': (
  "位於嘉義縣石棹附近（阿里山國家風景區管理處官網收錄），步道群由霧、茶、雲、霞、櫻、愛之道六條步道組成，全天開放。霧之道入口自台18線63.4K轉產業道路進入；客運可搭嘉義聯營客運或台灣好行阿里山線至石棹站，步行約1公里。茶園間路徑晨間易滑，夜間無照明請攜燈。",
  "Near Shizhuo, Chiayi County (listed on the Ali Mountain National Scenic Area HQ site). The trail group comprises six paths — Wu (mist), Cha (tea), Yun (cloud), Xia (glow), Ying (cherry) and Ai (love) — open around the clock. The Wu-trail entrance leaves Highway 18 at 63.4K onto a farm road. By bus, take the Chiayi joint-service bus or the Taiwan Trip Ali Mountain line to Shizhuo stop, then about 1 km on foot. Paths between tea fields are slippery in the morning dew and unlit at night — bring lights.",
  "嘉義県石棹付近（阿里山国家風景区管理処公式サイト掲載）。霧・茶・雲・霞・桜・愛の六つの歩道群で、終日開放。霧の道の入口は台18線63.4Kから産業道路へ入る。バスは嘉義共同運行バスか「台湾好行」阿里山線で石棹駅下車、徒歩約1km。茶畑間の径は朝露で滑りやすく、夜間は照明がないためライト携行が必要。"),
 'tw-024': (
  "位於阿里山國家森林遊樂區內。依林業及自然保育署阿里山林業鐵路及文化資產管理處官網，祝山車站自2023年11月21日重新啟用，觀日列車開車時間於乘車前1日下午4時30分在林鐵官網首頁、阿里山車站2樓、遊樂區大門口及旅客中心公告；建議預先在林鐵網路訂票系統或各站購票。祝山線僅由阿里山站發車，請依公告時刻前往。",
  "Inside the Ali Mountain National Forest Recreation Area. Per the Forestry and Nature Conservation Agency's Ali Mountain Forest Railway & Cultural Heritage Management Office site, Zhushan Station reopened on 2023-11-21; the sunrise-train departure time is announced at 16:30 on the day before travel on the railway's website home page, at Ali Station 2F, at the recreation-area main gate and at the visitor center. Advance tickets via the railway's online booking system or station counters are recommended. The Zhushan line departs only from Ali Station — follow the announced times.",
  "阿里山国家森林遊楽区内。林業及び自然保育署阿里山林業鉄路・文化資産管理処の公式サイトによると、祝山駅は2023年11月21日に再開業。観日列車の発車時刻は乗車前日の午後4時30分に、林鉄公式サイトのトップページ・阿里山駅2階・遊楽区ゲート・ビジターセンターで発表される。林鉄のネット予約システムか各駅の窓口での事前購入を推奨。祝山線は阿里山駅のみの発車で、発表の時刻に従うこと。"),
 'tw-025': (
  "位於台南市左鎮區二寮里，依西拉雅國家風景區管理處官網全天開放、免門票。新建觀景平台旁設有停車場與公廁；管理處並提供二寮觀日平台即時影像。日出以6至9月為佳，雨後隔日最易出現雲海大景；清晨路面與觀景台易結露濕滑，請注意腳下。",
  "In Erliao Village, Zuozhen District, Tainan; per the Siraya National Scenic Area HQ site it is open around the clock with no admission fee. The new viewing platform has a parking lot and public toilets beside it, and the HQ runs a live camera of the platform. June–September is the best season for sunrise, with big cloud-sea scenes most likely the morning after rain. The pre-dawn pavement and platform are dew-slick — mind your footing.",
  "台南市左鎮区二寮里。西拉雅国家風景区管理処の公式サイトによると終日開放・入場無料。新設の展望台の脇に駐車場とトイレがあり、管理処は展望台のライブカメラも提供している。日の出は6〜9月が狙い目で、雨上がりの翌朝に雲海が最も出やすい。早朝の路面と展望台は露で滑りやすいので足元に注意。"),
 'tw-026': (
  "位於台南市北門區復育鹽田西南郊，依雲嘉南濱海國家風景區管理處官網每日09:00–18:00開放、全區免門票。鹽田步道與興安宮周邊為主要拍攝範圍，夕照時段光線最著名；區內請勿踏越鹽田結晶層，依現場指示行走。",
  "Southwest of the restored salt fields in Beimen District, Tainan; per the Yunlin-Chiayi-Tainan Coastal National Scenic Area HQ site it is open 09:00–18:00 daily with free admission. The salt-field boardwalk and the area around Xing'an Temple are the main shooting range, and the sunset light is the site's signature. Do not step on the salt crust beyond the walkways; follow on-site signs.",
  "台南市北門区の塩田復育地の南西郊。雲嘉南浜海国家風景区管理処の公式サイトによると毎日09:00–18:00の開放で、区域全体入場無料。塩田の遊歩道と興安宮周辺が主な撮影範囲で、夕景が名物。遊歩道以外の塩の結晶面には踏み込まず、現地案内に従うこと。"),
 'tw-027': (
  "位於高雄市田寮區月世界地景公園（高雄市政府官方刊物《高雄畫刊》收錄之國家級泥岩惡地景觀）。公園內步道與觀景設施依現場公告開放；主要道路為月球路（崇德與古亭里之間），車行可达，夜間有景觀照明時段與設施管制依市府公告。土質鬆軟易滑，請勿離開步道。",
  "In the Moon World landform park, Tianliao District, Kaohsiung (the national-class mudstone badland landscape covered by the city government's official TAKAO magazine). The park's trails and viewing facilities open per on-site notices; the main road is Yueqiu (Moon) Road between Chongde and Guting villages and is reachable by car. Landscape-lighting hours and facility controls follow city government notices. The mud surface is soft and slippery — stay on the trails.",
  "高雄市田寮区の月世界地景公園（高雄市政府公式誌『TAKAO楽高雄』が掲載する国際級の泥岩悪地景観）。園内の歩道と展望施設は現地公告に従い開放。主要道路は崇德里と古亭里の間の「月球路（月の道）」で、車でアクセス可。ライトアップの時間帯と施設の規制は市の公告に従う。泥質の地面は柔らかく滑りやすいため、歩道から外れないこと。"),
 'tw-028': (
  "位於高雄市鹽埕區大勇路1號（高雄市政府文化局駁二藝術特區官方網站）。戶外園區開放空間自由進出，展館開放時間為週一至週四10:00–18:00、週五至週日及國定假日10:00–20:00，除夕休館。夜間拍攝以園區外圍與倉庫外牆光影為主，公共空間依規定使用，請勿影響活動進行。",
  "At No.1 Dayong Road, Yancheng District, Kaohsiung (Pier-2 Art Center official site, run by the Kaohsiung City Bureau of Cultural Affairs). The outdoor grounds are freely accessible; exhibition halls open Mon–Thu 10:00–18:00 and Fri–Sun plus national holidays 10:00–20:00, closed on Lunar New Year's Eve. Night photography is mainly around the perimeter and warehouse facades — use public spaces per the rules and do not obstruct events.",
  "高雄市塩埕区大勇路1号（高雄市政府文化局が運営する駁二芸術特区の公式サイト）。屋外エリアは自由に出入り可。展示館は月〜木10:00–18:00、金〜日と祝日10:00–20:00、旧暦大晦日は休館。夜間の撮影は周辺部と倉庫外壁の光と影が中心。公共空間は規則に従って利用し、催事の進行を妨げないこと。"),
 'tw-030': (
  "位於屏東縣恆春鎮關山（又名高山巖），依墾丁國家公園官方主題網，海拔約152公尺，是園區內極佳的眺望與賞夕陽地點；山頂有以珊瑚礁岩建造的福德宮與飛來石。車行至關山高山巖福德宮旁即可步上觀景處，台灣西南海岸線與貓鼻頭方向夕照著名；廟宇與平台設施依現場公告使用。",
  "Guanshan (also called Gaoshanyan) in Hengchun Township, Pingtung County. Per the official Taiwan National Parks portal it rises about 152 m and is the park's premier lookout for the west-coast sunset; on the summit are the coral-rock Fude Temple and the Feilaishi rock. Drive up to the Gaoshanyan Fude Temple at Guanshan and the viewpoint is right there — the sunset over the southwestern coast toward Maobitou is the famous shot. Temple and platform use follows on-site notices.",
  "屏東県恒春鎮の関山（別名・高山巖）。公式の台湾国家公園ポータルによると標高約152mで、園内でも夕日を望む最高の展望地。山頂にはサンゴ礁岩で建てられた福德宮と「飛来石」がある。車で関山の高山巖福德宮まで上がれば展望処に直結。台湾南西部の海岸線・猫鼻頭方面に沈む夕景が有名。宮と展望施設の利用は現地公告に従うこと。"),
 'tw-031': (
  "位於宜蘭縣礁溪鄉五峰旗瀑布風景區上方。依林業及自然保育署宜蘭分署官網，聖母登山步道全長約1.6公里（海拔400–950公尺），無入山管制，步道入口為聖母山莊（海拔900公尺）與通天橋產業道路（海拔410公尺）兩處，小型車可達；前往山莊須自五峰旗風景區沿溪上溯。稜線風大、箭竹草原泥滑，請結伴並備防滑與保暖。",
  "Above the Wufengqi waterfall scenic area, Jiaoxi Township, Yilan. Per the Yilan Branch of the Forestry and Nature Conservation Agency, the Shengmu (Sacred Mother) trail is about 1.6 km long (400–950 m elevation) with no entry permit required; its two entrances are Shengmu Villa (900 m) and the Tongtianqiao farm road (410 m), both reachable by small vehicles. Reaching the villa from Wufengqi involves a riverside climb. The ridge is windy and the bamboo-grass slope slippery — go with company and bring grip and warm layers.",
  "宜蘭県礁溪郷の五峰旗瀑布風景区の上方。林業及び自然保育署宜蘭分署の公式サイトによると、聖母登山歩道は全長約1.6km（標高400–950m）で入山管制はない。入口は聖母山荘（標高900m）と通天橋産業道路（410m）の2か所で小型車が到達可。山荘へは五峰旗風景区から渓沿いに登る。稜線は風が強く、笹原はぬかるむため、複数人での入山に滑り止めと防寒を携行すること。"),
 'tw-032': (
  "位於宜蘭縣大同鄉太平山國家森林遊樂區內。依林業及自然保育署宜蘭分署官網，見晴懷古步道無入山管制；太平山園區須購票入園（門票與開放依林業及自然保育署公告），自羅東沿台7線經宜專1公路上山，園區內設有停車場。步道沿舊鐵道林間，晨間常有雲霧，木棧道濕滑請注意。",
  "Inside Taiping Mountain National Forest Recreation Area, Datong Township, Yilan. Per the Yilan Branch of the Forestry and Nature Conservation Agency, the Jianqing Old Trail needs no entry permit; the recreation area itself requires an admission ticket (fees and hours per the agency's notices) and is reached from Luodong via Highway 7 onto the Yi-zhuan-1 road, with parking inside the area. The trail follows an old forest railway through mossy woods — the boardwalk is slick with morning fog and dew.",
  "宜蘭県大同郷の太平山国家森林遊楽区内。林業及び自然保育署宜蘭分署の公式サイトによると、見晴懐古歩道に入山管制はないが、遊楽区自体は入園券が必要（料金・開放状況は同署の公告による）。羅東から台7線・宜専1公路で上山し、園区内に駐車場がある。歩道は旧森林鉄道沿いの苔むした林道で、朝霧と露で木道が滑りやすい。"),
 'tw-033': (
  "位於宜蘭縣南澳鄉東澳灣最南端（宜蘭縣政府官方旅遊網收錄，全天開放）。主要拍攝點集中在粉鳥林漁港堤防與海岸步道；縣府旅遊網提醒礫灘地滑、不宜靠近崩塌岩壁。車行沿台9線轉東澳路抵漁港停車場，港區作業與海況變動請依現場指示，夜間無照明請攜燈。",
  "At the southern end of Dong'ao Bay, Nan'ao Township, Yilan (listed on the official Yilan tourism site; open around the clock). The main shooting points are the Fendiaolin fishing-harbor breakwater and the coastal path; the county tourism site warns that the pebble beach is slippery and collapsed rock faces must be avoided. Drive Highway 9 onto Dong'ao Road to the harbor parking. Harbor operations and sea conditions vary — follow on-site signs, and bring lights since the area is unlit at night.",
  "宜蘭県南澳郷の東澳湾最南端（宜蘭県公式観光サイト掲載、終日開放）。主な撮影点は粉鳥林漁港の防波堤と海岸の遊歩道。県観光サイトは礫浜が滑りやすく、崩壊した岩壁には近づかないよう注意を呼びかけている。台9線から東澳路へ入り漁港の駐車場へ。港湾作業と海況で状況が変わるため現地案内に従い、夜間は無照明のためライトを携行すること。"),
 'tw-034': (
  "位於花蓮縣秀林鄉台9線旁崇德地區（太魯閣國家公園崇德遊憩區）。太管處2025年10月公告崇德遊憩區隨園區部分開放範圍恢復開放；太魯閣國家公園官方網站提供崇德休憩區即時影像。台9線海側即崇德礫石灘與清水斷崖景觀，海濱礫石與長浪請依現場公告注意安全。",
  "Chongde, Xiulin Township, Hualien County, beside Provincial Highway 9 (Chongde recreation area of Taroko National Park). Per the Taroko HQ notice of October 2025, the Chongde recreation area is within the park's partially reopened range; the park's official site also streams a live camera of the Chongde rest area. Seaward of Highway 9 are the Chongde pebble beach and the Qingshui Cliff view — watch the surf and pebble beach per on-site notices.",
  "花蓮県秀林郷の台9線沿いの崇德地区（太魯閣国家公園崇德遊憩区）。太魯閣管理処は2025年10月の公告で崇德遊憩区を園区の部分開放範囲に含めた。公園公式サイトは崇德休憩区のライブカメラも配信している。台9線の海側は崇德の礫浜と清水断崖の景観。浜辺と長浪の安全は現地公告に従うこと。"),
 'tw-035': (
  "位於花蓮縣富里鄉，海拔約800公尺。依花蓮縣政府官方旅遊網，山區產業道路狹窄陡峭、午後常有濃霧或雷陣雨，花季（8–9月）期間縣府辦理道路交通管制並禁行甲、乙類大客車，非花季通行仍請小心會車。園區涼亭（忘憂亭等）24小時開放；夜間無照明、早晚溫差大，請攜燈與保暖。",
  "In Fuli Township, Hualien County, at about 800 m elevation. Per the official Hualien tourism site, the mountain farm road is narrow and steep with frequent afternoon fog or thunderstorms; during the daylily season (Aug–Sep) the county runs road traffic controls and bans large tour buses, and oncoming traffic needs care off-season too. The pavilions (including Wangyou Pavilion) are open 24 hours. Unlit at night with a big day-night temperature swing — bring lights and warm clothing.",
  "花蓮県富里郷、標高約800m。花蓮県公式観光サイトによると山間の産業道路は狭く急で、午後は濃霧や雷雨が多い。花の季節（8–9月）には県が道路の交通規制を実施し大型観光バスが通行禁止となるが、通常期もすれ違いに注意。忘憂亭などの亭は24時間開放。夜間は無照明で寒暖差が大きいため、ライトと防寒を携行すること。"),
 'tw-036': (
  "位於花蓮縣新城鄉（花蓮縣政府官方旅遊網收錄，全天開放、免費入園）。景區南北側與遊客中心旁設有免費停車場；大眾運輸可自花蓮火車站轉台灣好行310太魯閣線或308市區公車至七星潭站。縣府旅遊網明示嚴禁下水（離岸急深、瘋狗浪）、礫石請勿撿拾，夜間適合賞日出與觀星請自備照明。",
  "In Xincheng Township, Hualien County (official Hualien tourism site; open around the clock, free entry). Free parking sits at the north and south ends of the scenic area and beside the visitor center; by public transport, transfer at Hualien Station to the Taiwan Trip 310 Taroko line or the 308 city bus to Qixingtan stop. The county site bans swimming (steep offshore drop, rogue waves), asks visitors not to take pebbles, and recommends lights for the stargazing/sunrise hours.",
  "花蓮県新城郷（花蓮県公式観光サイト掲載、終日開放・入園無料）。景勝区の南北両端とビジターセンター脇に無料駐車場あり。公共交通は花蓮駅から「台湾好行」310太魯閣線か308市街バスで七星潭下車。海への飛び込みは厳禁（沖は急に深く、荒波）。礫の持ち出しは禁止。日の出・星空観賞には自前のライトが必要。"),
 'tw-037': (
  "位於台東縣太麻里鄉多良村（南迴鐵路旁，台9線可達）。觀景園區由太麻里鄉公所管理，2023年曾因收費亭及周邊設施修繕休園；開放狀況與入園規定依太麻里鄉公所官網與臉書公告（台東縣政府觀光網亦會轉知）。鐵道為營運中路線，站區拍照嚴禁進入軌道，列車通過時請站上觀景平台。",
  "In Duoliang Village, Taimali Township, Taitung County, beside the South-Link Railway (reachable from Highway 9). The viewing area is run by the Taimali Township Office, which closed it temporarily in 2023 for ticket-booth and facilities repairs; the current opening status and entry rules follow the township office's website and Facebook notices (also relayed on the Taitung tourism site). The railway is in service — never step onto the track; use the viewing platform when trains pass.",
  "台東県太麻里郷多良村（南迴線鉄道沿い、台9線からアクセス可）。展望園区は太麻里郷公所（郷役場）が管理し、2023年に券売亭と周辺施設の修繕で一時休園した。現在の開放状況と入園規則は郷公所の公式サイト・Facebookの公告に従う（台東県観光サイトでも案内される）。鉄道は営業中で、線路への立入は厳禁。列車通過時は展望台から撮影すること。"),
 'tw-038': (
  "位於台東縣成功鎮台11線約110.5K處，依東部海岸國家風景區管理處官網全天候開放；停車清潔費大客車假日200/非假日170元、小客車60/50元、機車20/15元，收費時段一般為08:00–17:00（旺季與連假為08:00–18:00）。重要：跨海八拱橋正進行整修工程，施工期間八拱橋暫時封閉（管理處公告預計116年/2027年底完工），登島須依公告安排，海象與燈杆區地形險峻請注意安全。",
  "On Highway 11 at about 110.5K, Chenggong Township, Taitung County; per the East Coast National Scenic Area HQ site it is open around the clock. Parking/cleaning fees: large vehicles 200 (weekend)/170 (weekday) NTD, cars 60/50, scooters 20/15, charged 08:00–17:00 (08:00–18:00 in peak season and holidays). IMPORTANT: the eight-arch sea bridge is under repair and temporarily CLOSED during the works (the HQ notice expects completion around late 2027 / year 116); island access depends on the official notice. Mind sea conditions and the steep lighthouse path.",
  "台東県成功鎮の台11線約110.5K。東部海岸国家風景区管理処の公式サイトによると終日開放。駐車清掃料は大型車200元（休日）/170元（平日）、自家用車60/50元、バイク20/15元で、課金時間は通常08:00–17:00（繁忙期・連休は08:00–18:00）。重要：八連拱橋は改修工事中で施工期間中は一時閉鎖（管理処の公告では116年＝2027年末の完成を予定）。島への立ち入りは公告に従い、海況と灯台への急な道に注意すること。"),
 'tw-040': (
  "位於南投縣及高雄市境（玉山國家公園），依玉山國家公園管理處官網登山路線現況為開放，惟入園與入山均須提前申請（臺灣國家公園入園入山線上申請服務網），主峰線沿塔塔加—排雲路線往返，住宿為排雲山莊（需依管理處規定登記）。高山天候變化劇烈、冬季積雪結霜，夜間山徑依規定使用頭燈與留守制度。",
  "Straddling Nantou and Kaohsiung within Yushan National Park. Per the Yushan HQ site the climbing routes are open, but BOTH park-entry and mountain-entry permits must be applied for in advance (Taiwan National Parks online permit service); the main-peak route goes from Tataka via Paiyun, with lodging at Paiyun Mountain Hut (booked per HQ rules). Weather swings hard at altitude with winter snow and frost — headlamps and a buddy/watch system are required on night sections.",
  "南投県と高雄市にまたがる玉山国家公園内。玉山管理処の公式サイトでは登山路線は開放状態だが、入園・入山とも事前申請が必須（台湾国家公園入園入山オンライン申請サービス網）。主峰ルートは塔塔加から排雲経由の往復で、宿泊は排雲山荘（管理処の規定による登録が必要）。高所の天候は激変し冬季は積雪・霜。夜間区間ではヘッドライトと留守番制度が必須。"),
}
PLACE_EVID = 'e-d36-access'
PLACE_SLUG = {
 'tw-019':'hehuanshan-main-peak','tw-020':'jinlongshan-yuchi','tw-021':'wujie-nantou',
 'tw-022':'eryanping-trail','tw-023':'shizhuo-trails','tw-024':'zhushan-sunrise',
 'tw-025':'erliao-sunrise','tw-026':'jingziao-saltfields','tw-027':'tianliao-moonworld',
 'tw-028':'pier2-kaohsiung','tw-030':'guanshan-kenting','tw-031':'shengmu-trail',
 'tw-032':'jianqing-trail','tw-033':'fendiaolin-nanao','tw-034':'chongde-taroko',
 'tw-035':'liushishishan-fuli','tw-036':'qixingtan-hualien','tw-037':'duoliang-station',
 'tw-038':'sanxiantai','tw-040':'yushan-main-peak',
}
PLACE_SOURCES = {
 'tw-019':["https://hike.taiwan.gov.tw/news_0_1.aspx?id=4682","https://www.taiwan.nps.gov.tw/home/zh-tw/news/30100.html"],
 'tw-020':["https://www.sunmoonlake.gov.tw/Attractions/Attractions?a=20&id=94"],
 'tw-021':["https://travel.nantou.gov.tw/attractions/bukai/"],
 'tw-022':["https://www.ali-nsa.net/zh-tw/attractions/detail/141"],
 'tw-023':["https://www.ali-nsa.net/zh-tw/attractions/detail/252"],
 'tw-024':["https://afrch.forest.gov.tw/0000300"],
 'tw-025':["https://www.siraya-nsa.gov.tw/zh-tw/attractions/detail/30"],
 'tw-026':["https://www.swcoast-nsa.gov.tw/zh-tw/attraction/details/369"],
 'tw-027':["https://takao.kcg.gov.tw/article/1888"],
 'tw-028':["https://www.pier2.org/about/"],
 'tw-030':["https://www.taiwan.nps.gov.tw/home/zh-tw/attractions/21054.html"],
 'tw-031':["https://yilan.forest.gov.tw/0000137"],
 'tw-032':["https://yilan.forest.gov.tw/0000106","https://yilan.forest.gov.tw/0000137"],
 'tw-033':["https://travel.yilan.gov.tw/zh-tw/attraction/11/"],
 'tw-034':["https://hike.taiwan.gov.tw/news_0_1.aspx?id=4682","https://www.taroko.gov.tw/ch/sglarticle/chongde-rest-area"],
 'tw-035':["https://hualien.travel/zh-tw/attraction/395/"],
 'tw-036':["https://hualien.travel/zh-tw/attraction/68/"],
 'tw-037':["https://tour.taitung.gov.tw/zh-tw/news/details/5267","https://www.taimali.gov.tw/home/"],
 'tw-038':["https://www.eastcoast-nsa.gov.tw/zh-tw/attractions/detail/41/"],
 'tw-040':["https://www.ysnp.gov.tw/Trail/7fa5c242-df1a-4a8e-bcab-32dc55b1f7b6","https://hike.taiwan.gov.tw/news_0_1.aspx?id=4682"],
}
